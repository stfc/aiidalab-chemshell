.. _resource_management:

Resource Management
===================

AiiDA relies heavily on *computer* and *code* instances to be able to know where and how
to run the underlying software stacks through any provided plugin. This page allows the
user to configure the available *computer* and *code* instances within the AiiDAlab
interface controlling which core software stacks the plugins have access to. Often the 
provided container images come bundled with the local computer available as *localhost*
and a selection of pre-installed software *code* instances, such as ChemShell if using the
provided AiiDAlab ChemShell docker images. A list of all available codes can be seen at the
bottom of the page including a search bar to search for a specific codes and the ability to
hide certain codes from the AiiDAlab interface. The rest of this page is dedicated to 
configuring new *computer* and *code* instances.

Quick Setup
-----------


Manual Setup
------------

If your required software stack is not available within a quick setup database you will need
to manually configure the different components. First you must check the box labelled *Tick checkbox
to setup resource step by step* to enable to advanced configuration options. This will present
three tabs which allow a user to configure SSH connections, computer and code instances respectively.


SSH Connections
~~~~~~~~~~~~~~~

When setting up a completely fresh connection to a **remote HPC** the first step is to setup
the ability to communicate with the remote server. AiiDA utilises SSH key authorisation by
default to communicate with the remote machine in the background, if you already have 
passwordless SSH authorisation enabled you can skip this step, otherwise you will need to
configure the connection either through this input tab or externally outside AiiDAlab. 

This tab utilises a pre-connection step based on a provided password which will then setup
the SSH key authorisation with the remote machine. First ensure the *Verification mode* option
if set to *Provide password to remote machine*. The user must then provide the hostname/address
of the remote HPC machine alongside their username and password for the remote machine. 

Once all the required fields have been filled click the *Setup ssh* button and AiiDA will run
the required setup process and test the resulting connection in the background and will 
notify the user on a successful setup.

.. note:: 

    Please ensure you remote resources support full passwordless SSH key based authorisation.
    At present AiiDA is incompatible with system that require password authentication and 
    whilst it can work with MFA based login methods these are not guaranteed. 


Computer Instances
~~~~~~~~~~~~~~~~~~

Once a SSH connection has been configured either manually or through the provided UI utility, 
a **computer** instance needs to be created to tell AiiDA how to run jobs on the remote 
machine. A breakdown of the various inputs is given as follows:

- **Computer name:** - the reference name given to the computer in the AiiDA database.
- **Hostname:** - The address of the remote machine.
- **Computer description**: A reference description applied to the computer in the AiiDA database.
- **AiiDA working directory**: The directory on the remote machine where AiiDA jobs will run.
- **Mpirun command:** - How to run mpi based jobs on the remote machine.
- **#CPU(s) per node:** - Maximum number of cpus per node on the remote machine.
- **Memory per node:** - Maximum memory per node on the remote machine.
- **Transport type:** - How to connect to the remote machine, (SSH or local).
- **Min. connection interval:** - The minimum time between connection requests sent to the remote machine.
- **Scheduler:** - The jobs scheduler used on the remote system (use core.direct if no scheduler is implemented).
- **Shebang:** - The top line of any scripts created specifying how they are interpreted.
- **Use login shell** - Runs additional user configurations when connecting to the remote machine.
- **Use double quotes to escape...** - Use double quotes instead of single for bash commands.
- **Prepend text:** - Additional commands to run before the main executable is called.
- **Append text:** - Additional commands to run after the main executable is called.

An example for setting up the ChemShell code on a remote HPC that utilised the SLURM scheduler is given
as follows, with any remaining fields left as their default values,

.. code:: yaml

    label: "remote1"
    hostname: "remote1.ac.uk"
    transport: "core.ssh"
    scheduler: "core.slurm"
    work_dir: "/home/user/.aiida_run"
    mpirun_command: "srun "
    mpiprocs_per_machine: "32"
    prepend_text: "#SBATCH --partition=default"


Clicking the *Setup computer* button will run AiiDA's computer setup and testing routines and will 
provide a message if it is successful.  


Code Instances
~~~~~~~~~~~~~~

Once AiiDA knows how to connect and talk to a computer it then needs to be able to call the
relevant software executable which is where the *code* instance comes in. The Code tab 
allows the setup to new code instances with the following inputs options, 

- **AiiDA code label:** - The reference name for the code instance in the AiiDA database.
- **Select computer:** - The computer instance on which the code is located.
- **Code plugin:** - The AiiDA plugin used to handle the software.
- **Code description:** - The reference description for the code instance in the AiiDA database.
- **Absolute path to executable:** - The executable for the given software.
- **Use double quotes to escape...** - Use double quotes instead of single for bash commands.
- **Prepend text:** - Additional commands to run before the main executable is called.
- **Append text:** - Additional commands to run after the main executable is called.

An example for setting up the ChemShell code on a remote machine is given below,

.. code:: yaml

    label: "ChemShell (SCARF)",
    description: "ChemShell 25.0.1 (parallel) compiled for SCARF",
    filepath_executable: "chemsh.x",
    default_calc_job_plugin: "chemshell",
    prepend_text: "module load contrib/chemshell/25.0.1-intel",
    append_text: "",


Clicking the *Setup code* button will run AiiDA's code setup and testing routines and will 
provide a message if it is successful.  