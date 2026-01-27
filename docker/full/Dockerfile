FROM ghcr.io/stfc/aiidalab-chemshell/base:latest 

LABEL maintainer="Dr Benjamin T. Speake <benjamin.speake@stfc.ac.uk>"
LABEL org.opencontainers.image.source="https://github.com/stfc/aiidalab-chemshell"

USER root 

# Install Intel OneAPI HPC tookit 
RUN apt update --yes && apt upgrade --yes && apt install --yes gpg wget cmake && \ 
    wget -O- https://apt.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS.PUB \
    | gpg --dearmor | tee /usr/share/keyrings/oneapi-archive-keyring.gpg > /dev/null && \ 
    echo "deb [signed-by=/usr/share/keyrings/oneapi-archive-keyring.gpg] https://apt.repos.intel.com/oneapi all main" \
    | tee /etc/apt/sources.list.d/oneAPI.list && \
    apt update --yes && apt install intel-oneapi-hpc-toolkit --yes && \ 
    apt autoremove --yes && apt clean --yes

# Install ChemShell 
COPY ../chemsh-py/. /opt/chemsh-py 
WORKDIR /opt/chemsh-py 
RUN source /opt/intel/oneapi/setvars.sh && \
    pip install pyscf --no-user && \
    ./setup -j 4 -fc mpiifx -cc mpiicx -cpc mpiicpx --mpi --dl_poly --nwchem 

COPY 62_setup_chemsh.sh /usr/local/bin/before-notebook.d/
COPY chemsh.yml /opt/chemsh.yml 

USER ${NB_USER}
WORKDIR ${HOME}
