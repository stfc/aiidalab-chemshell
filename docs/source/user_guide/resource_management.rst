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

Quick Install ChemShell Container
---------------------------------

For users running AiiDAlab on their local machine, the top of the resource setup
page provides a one-click **Install ChemShell Container & Create Code** button. This
downloads the pre-built ChemShell container image and creates a ready-to-use
``chemsh@localhost`` *code* instance, removing the need to manually configure a
*computer* and *code* for local ChemShell runs. It is the quickest way to get up and
running when using one of the base AiiDAlab images that does not already bundle a full
ChemShell installation (see :ref:`getting_started`).

.. note::

    This feature requires either the `Apptainer <https://apptainer.org/>`_ **or**
    `Docker <https://www.docker.com/>`_ container engine to be available on the local
    machine. Apptainer is preferred and Docker is used automatically as a fallback when
    Apptainer is not available.

Clicking the button runs the following steps automatically, reporting progress in the
status area beneath it:

1. **Detect a container engine.** Apptainer is checked first; if it is not present the
   Docker engine is used instead. Docker is only considered available if its daemon is
   actually reachable, so a stopped Docker service is reported as unavailable rather than
   failing later during the build.
2. **Acquire the container image.** If the ChemShell image is already present locally it
   is reused, otherwise it is pulled from the GitHub container registry
   (``ghcr.io/stfc/aiidalab-chemshell/chemsh:latest``). With Apptainer this produces a
   local ``.sif`` file; with Docker the image is stored in the local daemon's image
   store. Building the image can take several minutes on the first run.
3. **Create the AiiDA code.** A containerised ``chemsh@localhost`` *code* is created
   pointing at the ChemShell executable inside the image. If a ChemShell code already
   exists it is reused rather than recreated.

Once the process completes successfully the code becomes available for selection in the
workflow wizard just like any manually configured code.

.. note::

    Containerised codes require the ``use double quotes to escape...`` option to be
    enabled on the host *computer* so that the ``$PWD`` reference in the container engine
    command is expanded correctly. The installer enables this setting automatically on
    the ``localhost`` computer if it is not already set, and reports in the status
    message when it has done so. See :ref:`resource_management` for the equivalent manual
    option.

Quick Setup
-----------

The *Create New Code* section provides a **Quick setup** utility for configuring
*code* instances on remote machines without having to enter every field by hand.
Rather than describing a computer and code from scratch, the quick setup reads a set of
pre-defined *recipes* from a database file and lets you pick a ready-made
combination.

Resource Database Source
~~~~~~~~~~~~~~~~~~~~~~~~~~

The recipes are loaded from the JSON database referenced in the **Source** field at the
top of the section. By default this points at an STFC maintained
database of resources, providing quick access to codes on STFC managed computers such as
SCARF:

.. code:: text

    https://raw.githubusercontent.com/stfc/alc-ux/refs/heads/main/resources/remotes.json

To use a different collection of recipes simply edit the URL in the **Source** field to
point at your chosen JSON database. An example would the the default AiiDA resource 
registry database which can be found at:

.. code:: text 

    https://aiidateam.github.io/aiida-resource-registry/database.json


Configuring a Code
~~~~~~~~~~~~~~~~~~

Once a source is selected, configure a new code using the following steps:

1. **Select the domain** of your remote machine.
2. **Select the computer recipe** for the target machine.
3. **Select the code recipe** for the software you wish to run.
4. **Complete the remaining fields**. The fields presented here depend on the combination
   chosen in steps 1-3 and typically cover account-specific details such as your remote
   username.
5. Click **Quick setup**.

This will automatically run the computer and code setup steps on the background for 
the given pre-configured recipe. The new code will then be available for selection
in the workflow wizard.

.. note::

    If no suitable recipe exists for your computer/code combination in any available
    database, use the :ref:`Manual Setup <_resource_manual_setup>` instead by ticking the
    *Tick checkbox to setup resource step by step* option described below or get in touch
    with your chosen registry maintainers e.g. 
    `Ada Lovelace Centre <https://github.com/stfc/alc-ux>` for STFC managed resources.

.. _resource_manual_setup:

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