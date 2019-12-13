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

WORKDIR /galaxy-central

RUN add-tool-shed --url 'http://testtoolshed.g2.bx.psu.edu/' --name 'Test Tool Shed'

#ADD tools/rnaseq.yml $GALAXY_ROOT/rnaseq.yaml

#RUN install-tools $GALAXY_ROOT/rnaseq.yaml && \
#    /tool_deps/_conda/bin/conda clean --tarballs --yes > /dev/null && \
#    rm /export/galaxy-central/ -rf

ADD ./workflows/* $GALAXY_HOME/workflows/

# Install Visualisation
#RUN install-biojs msa

# Adding the tool definitions to the container
#ADD my_tool_list.yml $GALAXY_ROOT/my_tool_list.yml

# Install deepTools
#RUN install-tools $GALAXY_ROOT/my_tool_list.yml

# Mark folders as imported from the host.
VOLUME ["/export/", "/data/", "/var/lib/docker"]

ADD assets $GALAXY_CONFIG_DIR/web/
ADD welcome.html $GALAXY_CONFIG_DIR/web/welcome.html

# Expose port 80 (webserver), 21 (FTP server), 8800 (Proxy)
EXPOSE :80
EXPOSE :21
EXPOSE :8800

# Autostart script that is invoked during container start
CMD ["/usr/bin/startup"]
