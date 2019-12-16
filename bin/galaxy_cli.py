#!/usr/bin/env python3

import argparse
import sys
import re
import time
import os
import json
import subprocess


CONTAINER_NAME = "test"


def launch_cmd(cmd: str, cwd: str = "") -> None:
    effective_command = cmd
    if cwd == '':
        p = subprocess.Popen(effective_command, stdout=subprocess.PIPE, shell=True, stderr=subprocess.PIPE,
                         bufsize=1)
    else:
        p = subprocess.Popen(effective_command, stdout=subprocess.PIPE, shell=True, stderr=subprocess.PIPE, bufsize=1,
                                                                       cwd=cwd)
    stdout, stderr = p.communicate()

    return stdout, stderr

def comma_sep(elements:[]) -> str:
    return ", ".join( map(str, elements))

def basic_parser():
    parser = argparse.ArgumentParser(description='cli for user management')
    parser.add_argument('-c', '--config', default="api.json", help="config file, can be overridden by parameters")
    parser.add_argument('-d', '--database', default=None)
    subparsers = parser.add_subparsers(dest='subparser')


    return parser.parse_args()


def count(required:int, count:int, name:str=None, msg:str=None):
    if ( required != count):
        if msg is None:
            msg = "command requires {required} argument(s)".format( required=required)
            if name is not None:
                msg = "{} {}".format( name, msg)

        print(msg)
        sys.exit()

def min_count(required:int, count:int, name:str=None, msg:str=None):
    if ( required > count):
        if msg is None:
            msg = "command requires {required} or more argument(s)".format( required=required )
            if name is not None:
                msg = "{} {}".format( name, msg)

        print(msg)
        sys.exit()

def count_subcommand(required:int, count:int, name:str=None, msg:str=None):

    msg = "command requires a subcommand (run with help)"

    if name is not None:
        msg = "{} {}".format( name, msg)

    return count(required=required, count=count, name=name, msg=msg)

def min_count_subcommand(required:int, count:int, name:str=None, msg:str=None):
    msg = "command requires a subcommand (run with help)"

    if name is not None:
        msg = "{} {}".format( name, msg)

    return min_count(required=required, count=count, name=name, msg=msg)

def valid_command(command:int, commands:int, msg:str=None):
    if command not in commands:
        print("Invalid command name: '{}', allowed commands are {}".format( command, ", ".join(commands)))
        sys.exit()

def container_start(config:{}):

    if 'port' not in config:
        config[ 'port'] = 8080

    extra = ""
    if "storage" in config:
        if not config['storage'].startswith("/"):
            config['storage'] = os.path.abspath(config['storage'])

        extra += " -v {}:/export/".format( config[ 'storage'])

    cmd = "docker run {extra} -d -p{port}:80 {}".format( CONTAINER_NAME )
    cmd = cmd.format( extra=extra, port=config['port'])

#    print( cmd )
    stdout, stderr = launch_cmd( cmd )
    stdout = stdout.decode('utf-8')
    if stderr:
        print( stderr.decode('utf-8'))
        sys.exit()

    wait_for_started( stdout )

def wait_for_started(container_id):
 #   print( "CID", container_id)
    starting = True
    while( starting ):
        log = get_log( container_id )
        print( log )
        if (re.search("Galaxy server instance 'handler0' is running", log)):
            print( "Galaxy container is up and running")
            return

        time.sleep( 10 )

def get_log(container_id:str):
    cmd = "docker logs  {}".format( container_id)
    stdout, stderr = launch_cmd( cmd )
    stdout = stdout.decode("utf-8")
    return stdout


def container_stop(container_id):
    cmd = "docker stop {}".format( container_id )
    launch_cmd( cmd )

def container_logs(container_id):
    print( get_log(container_id))


def container_list(name:str) -> None:
    cmd = "docker ps".format( name)
    stdout, stderr = launch_cmd( cmd )
    lines = stdout.decode("utf-8").split("\n")
    lines = list( filter(lambda x: x.startswith("CONT") or name in x, lines))
    print( "\n".join( lines ))

#    print( stdout.decode("utf-8") )



def get_container_id(name:str) -> str:
    cmd = "docker ps | egrep {}".format( name)
    stdout, stderr = launch_cmd( cmd )
    lines = stdout.decode("utf-8").split("\n")
    lines = list(filter(None, lines))

    if lines == []:
        print("No container named {} is running".format( name))
        sys.exit()

    if len(lines) > 1:
        print( "Multiple containers running, please provide id")
        return None

    fields = lines[0].split(r' ')
    return fields[0]

def container_bootstrap():
    fh = open('galaxy.json', 'w')
    fh.write( '{ "storage":"galaxy_data" }')
    fh.close()
    os.mkdir('galaxy_data')

    sys.exit()

def readin_json_file(filename:str) -> {}:

    if not os.path.isfile( filename ) or os.path.getsize(filename) == 0:
        return {}

    with open( filename ) as json_file:
        data = json.load(json_file)
        json_file.close(  )

    return data


def main():

    commands = ['start', 'stop','logs', 'list', 'bootstrap', 'help']


    parser = argparse.ArgumentParser(description='bysykkel_import: importing data')


    parser.add_argument('-c', '--config', default="galaxy.json", help="config file, can be overridden by parameters")
    parser.add_argument('command', nargs='+', help="{}".format(",".join(commands)))

    args = parser.parse_args()

    config = readin_json_file( args.config )


    min_count(1, len(args.command), msg="galaxy_cli takes one of the following commands: {}".format(comma_sep( commands )))

    command = args.command.pop(0)
    if command not in commands:
        parser.print_help()

    if command == 'start':
        container_start(config)
        sys.exit()
    elif command == 'list':
        container_list(CONTAINER_NAME)
        sys.exit()
    elif command == 'bootstrap':
        container_bootstrap()
        sys.exit()
    elif command == 'help':
        print("The tool support the following commands: {}".format(comma_sep( commands )))
        sys.exit( 1 )


    if len(args.command) == 0:
        container_id = get_container_id(name=CONTAINER_NAME)
        if container_id:
            args.command.append( container_id )


    if command == 'stop':
        count(1, len(args.command), msg="stop require a container-d")
        container_stop(args.command.pop(0))
    elif command == 'logs':
        count(1, len(args.command), msg="logs require a container-d")
        container_logs(args.command.pop(0))


if __name__ == "__main__":
    main()
