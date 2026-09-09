FROM ghcr.io/stfc/alc-ux/base:py310 
# FROM aiidalab/full-stack:edge 

LABEL maintainer="Dr Benjamin T. Speake <benjamin.speake@stfc.ac.uk>"
LABEL org.opencontainers.image.source="https://github.com/stfc/aiidalab-chemshell"

USER root 

ENV AIIDALAB_DEFAULT_APPS="chemshell"

# Install ChemShell 
COPY chemsh-py/. /opt/chemsh-py 
WORKDIR /opt/chemsh-py 
RUN apt update && apt install cmake gfortran libopenmpi-dev openmpi-bin \
    libblas-dev liblapack-dev --yes --no-install-recommends && \
    mamba install --yes pyscf && mamba clean --all -f -y && fix-permissions "${CONDA_DIR}" && \
    ./setup -j 4 -fc mpifort -cc mpicc -cpc mpicxx --mpi --dl_poly --nwchem && \
    # Strip the build-only toolchain. 
    apt-get purge -y cmake gfortran libopenmpi-dev \
        libblas-dev liblapack-dev && \
    apt-get autoremove -y && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY 55_start_aiida_daemon.sh /usr/local/bin/before-notebook.d/
COPY 62_setup_chemsh.sh /usr/local/bin/before-notebook.d/
COPY chemsh.yml /opt/chemsh.yml 

USER ${NB_USER}
WORKDIR ${HOME}
