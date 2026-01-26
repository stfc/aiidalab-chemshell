#!/bin/bash 

# Install the AiiDAlab application 
echo "INSTALLING AiiDAlab ChemShell Application"
cd "${HOME}"/apps
if [[ -d "aiidalab-chemshell" ]]; then 
    echo "AiiDAlab ChemShell app already installed..." 
else 
    pip install -e git+https://github.com/stfc/aiidalab-chemshell.git#egg=aiidalab-chemshell --src ${HOME}/apps
fi 

# Install the associated python package 
cd "${HOME}"/apps/aiidalab-chemshell 
pip install --no-user --no-cache-dir -q -e . 

# Return to the $HOME directory 
cd "${HOME}" 