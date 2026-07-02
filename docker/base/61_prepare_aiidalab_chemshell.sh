#!/bin/bash 

# Install the AiiDAlab application 
echo "INSTALLING AiiDAlab ChemShell Application"
cd "${HOME}"/apps
if [[ -d "chemshell" ]]; then 
    echo "AiiDAlab ChemShell app already installed..." 
else 
    # pip install -e git+https://github.com/stfc/aiidalab-chemshell.git#egg=aiidalab-chemshell --src ${HOME}/apps
    git clone -b v0.2.1 --depth 1  https://github.com/stfc/aiidalab-chemshell.git
    mv aiidalab-chemshell chemshell 
fi 

# Install the associated python package 
cd "${HOME}"/apps/chemshell 
pip install -e . --no-user --no-cache-dir -q  

# Return to the $HOME directory 
cd "${HOME}" 