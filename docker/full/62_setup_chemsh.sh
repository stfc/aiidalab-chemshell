#!/bin/bash 

## Setup an AiiDA code instance for locally installed ChemShell

source /opt/intel/oneapi/setvars.sh 

export PATH="/opt/chemsh-py/bin/intel:${PATH}"

if verdi code list | grep -q "chemsh@localhost"; then 
    echo "Found existing AiiDA ChemShell code instance..." 
else 
    echo "Creating AiiDAChemShell code instance..." 
    verdi code create core.code.installed --config /opt/chemsh.yml --non-interactive
fi  
