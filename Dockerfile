# Galaxy - tsd
#
# VERSION       0.1

FROM bgruening/galaxy-stable

MAINTAINER Kim Brugger, kim.brugger@uib.no

ENV GALAXY_CONFIG_BRAND NeLS
# The following two lines are optional and can be given during runtime
# with the -e http_proxy='http://yourproxyIP:8080' parameter
#ENV http_proxy 'http://yourproxyIP:8080'
#ENV https_proxy 'http://yourproxyIP:8080'

ENV GALAXY_DEFAULT_ADMIN_USER galaxy
ENV GALAXY_DEFAULT_ADMIN_PASSWORD galaxy


WORKDIR /galaxy-central

RUN add-tool-shed --url 'http://testtoolshed.g2.bx.psu.edu/' --name 'Test Tool Shed'

#ADD ./tools/rnaseq.yml $GALAXY_ROOT/rnaseq.yaml
ADD ./tools/tools.yml $GALAXY_ROOT/tools.yaml

RUN install-tools $GALAXY_ROOT/tools.yaml && \
    /tool_deps/_conda/bin/conda clean --tarballs --yes > /dev/null && \
    rm /export/galaxy-central/ -rf && \
    mkdir -p workflows

ADD ./nels-workflows/* $GALAXY_HOME/workflows/

ENV GALAXY_CONFIG_TOOL_PATH=/galaxy-central/tools/


#RUN /tool_deps/_conda/bin/workflow-install --workflow_path $GALAXY_HOME/workflows/ -g http://localhost:8080 \
#        -u $GALAXY_DEFAULT_ADMIN_USER -p $GALAXY_DEFAULT_ADMIN_PASSWORD

# Download training data and populate the data library

#RUN startup_lite && \
#    /tool_deps/_conda/bin/workflow-install --workflow_path $GALAXY_HOME/workflows/ -g http://localhost:8080 -u $GALAXY_DEFAULT_ADMIN_USER -p $GALAXY_DEFAULT_ADMIN_PASSWORD

# Install Visualisation
#RUN install-biojs msa

# Adding the tool definitions to the container
#ADD my_tool_list.yml $GALAXY_ROOT/my_tool_list.yml

# Install deepTools
#RUN install-tools $GALAXY_ROOT/my_tool_list.yml

# Mark folders as imported from the host.
VOLUME ["/export/", "/data/", "/var/lib/docker"]

ADD assets $GALAXY_CONFIG_DIR/web/

#RUN mkdir $GALAXY_HOME/workflows/
#ADD ./workflows/* $GALAXY_HOME/workflows/

# Expose port 80 (webserver), 21 (FTP server), 8800 (Proxy)
EXPOSE :80
#EXPOSE :21
#EXPOSE :8800

# Autostart script that is invoked during container start
CMD ["/usr/bin/startup"]
