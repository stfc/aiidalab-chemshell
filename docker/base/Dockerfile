# Use this for the latest official aiidalab image (Python 3.9)
# FROM aiidalab/full-stack:latest 
# Use this for a ported version of the above running on Python 3.10 
FROM ghcr.io/stfc/alc-ux/base:py310  

LABEL maintainer="Dr Benjamin T. Speake <benjamin.speake@stfc.ac.uk>"
LABEL org.opencontainers.image.source="https://github.com/stfc/aiidalab-chemshell"

USER root
 
# Install some extra required dependencies to speed up start up and aiida ChemShell plugin 
RUN pip install aiidalab_widgets_base --no-cache-dir --no-user 

# This will install alc-ux on container start up 
COPY 61_prepare_aiidalab_chemshell.sh /usr/local/bin/before-notebook.d/

USER ${NB_UID}
WORKDIR ${HOME}