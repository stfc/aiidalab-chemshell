#!/bin/bash 

# Install the AiiDAlab application 
echo "INSTALLING AiiDAlab ChemShell Application"
cd "${HOME}"/apps
if [[ -d "aiidalab-chemshell" ]]; then 
    echo "AiiDAlab ChemShell app already installed..." 
else 
    wget https://github.com/stfc/aiidalab-chemshell/archive/refs/heads/main.zip 
    unzip main.zip 
    rm -f main.zip 
    mv "${HOME}"/apps/aiidalab-chemshell-main "${HOME}"/apps/aiidalab-chemshell
fi 

# Install the associated python package 
cd "${HOME}"/apps/aiidalab-chemshell 
pip install --no-user --no-cache-dir -q . 

# Return to the $HOME directory 
cd "${HOME}" 