#!/usr/bin/env python3

import argparse
import sys
import subprocess


def launch_cmd(cmd: str, cwd: str = "") -> None:
    effective_command = cmd
    if cwd == '':
        p = subprocess.Popen(effective_command, stdout=subprocess.PIPE, shell=True, stderr=subprocess.PIPE,
                         bufsize=1)
    else: subprocess.Popen(effective_command, stdout=subprocess.PIPE, shell=True, stderr=subprocess.PIPE, bufsize=1,
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

def container_run():
    cmd = "docker run -dp 8080:80 test"
    launch_cmd( cmd )


def container_logs(container_id):
    cmd = "docker logs -f {}".format( container_id)



def main():

    commands = ['run', 'logs', 'help']


    parser = argparse.ArgumentParser(description='bysykkel_import: importing data')


    parser.add_argument('-c', '--config', default="api.json", help="config file, can be overridden by parameters")
    parser.add_argument('command', nargs='+', help="{}".format(",".join(commands)))

    args = parser.parse_args()

#    config = config_utils.readin_config_file( args.config )


    min_count(1, len(args.command), msg="galaxy_cli takes one of the following commands: {}".format(comma_sep( commands )))

    command = args.command.pop(0)
    if command not in commands:
        parser.print_help()

    if command == 'run':
        container_run()
    elif command == 'logs':
        count(1, len(args.command), msg="logs require a container-d")
        print( container_logs(args.command.pop(0)) )

    else:
        print("The tool support the following commands: {}".format(comma_sep( commands )))
        sys.exit( 1 )


if __name__ == "__main__":
    main()
