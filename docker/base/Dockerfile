# Use this for the latest official aiidalab image (Python 3.9)
# FROM aiidalab/full-stack:latest 
# Use this for a ported version of the above running on Python 3.10 
FROM ghcr.io/stfc/alc-ux/base:py310  

LABEL maintainer="Dr Benjamin T. Speake <benjamin.speake@stfc.ac.uk>"
LABEL org.opencontainers.image.source="https://github.com/stfc/aiidalab-chemshell"

USER root

# Install the AiiDAlab and AiiDA plugins for ChemShell 
RUN pip install -e git+https://github.com/stfc/aiidalab-chemshell.git#egg=aiidalab-chemshell --src ${HOME}/apps  && \
    pip install aiida-chemshell --no-cache-dir --no-user  


USER ${NB_UID}
WORKDIR ${HOME}