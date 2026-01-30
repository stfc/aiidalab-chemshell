# AiiDAlab ChemShell Plugin

[![Release](https://img.shields.io/github/v/release/stfc/aiidalab-chemshell)](https://github.com/stfc/aiidalab-chemshell/releases)
[![PyPI](https://img.shields.io/pypi/v/aiidalab-chemshell)](https://pypi.org/project/aiidalab-chemshell/)

[![Pipeline Status](https://github.com/stfc/aiidalab-chemshell/actions/workflows/ci-testing.yml/badge.svg?branch=main)](https://github.com/stfc/aiidalab-chemshell/actions)
[![Docs status](https://github.com/stfc/aiidalab-chemshell/actions/workflows/ci-docs.yml/badge.svg?branch=main)](https://stfc.github.io/aiidalab-chemshell/)
<!-- [![Coverage Status]( https://coveralls.io/repos/github/stfc/aiidalab-chemshell/badge.svg?branch=main)](https://coveralls.io/github/stfc/aiidalab-chemshell?branch=main) -->

[![DOI](badge)](https://zenodo.org/)

This is an AiiDAlab application plugin for ChemShell based scientific workflows, maintained by the [Ada Lovelace Center](https://adalovelacecentre.ac.uk/) (ALC).
The app is still in early development stage and any input/contributions are welcome.
Full documentation can be found here: [https://stfc.github.io/aiidalab-chemshell/](https://stfc.github.io/aiidalab-chemshell/).

## Usage

This plugin is hosted on the AiiDAlab plugin registry and therefore can be installed via the AiiDAlab plugin
management UI page from within the AiiDAlab application interface. Instructions for how to run AiiDAlab
itself can be found in its [documentation](https://aiidalab.readthedocs.io/en/latest/usage/access/index.html)
and are also included in the documentation associated with this project
[https://stfc.github.io/aiidalab-chemshell/](https://stfc.github.io/aiidalab-chemshell/).
It is generally recommended to run AiiDAlab through a container engine such as Docker or Apptainer, both of
which are discussed in more detail in the documentation provided. In general the core docker image applicable
to most use cases is [aiidalab/full-stack:latest](https://hub.docker.com/r/aiidalab/full-stack) however, many
other options exist for more tailored startup environments.

## ChemShell Containers

Multiple docker images are provided with this repository which build on the core foundation of the images
provided by AiiDAlab bundling various components of the ChemShell workflows on-top of the core AiiDAlab
application. At present two images are available; [base](https://github.com/stfc/aiidalab-chemshell/pkgs/container/aiidalab-chemshell%2Fbase) includes the AiiDAlab ChemShell plugin pre-installed including all
required dependencies,
[full](https://github.com/stfc/aiidalab-chemshell/pkgs/container/aiidalab-chemshell%2Ffull) builds upon
the base package including a working installation of ChemShell (version 25) configured with DL_POLY, NWChem
and PySCF as available backends.

To run one of the provided containers, first install and setup your desired container engine, then run the
image as follows,

``` sh
docker run -it --rm -p 8888:8888 -v $HOME:/home/jovyan ghcr.io/stfc/aiidalab-chemshell/base:latest
```

The additional run parameters will run the container interactively (``-it``), delete it when it is finished
(``--rm``), expose the required port for the jupyter notebook instance (``-p 8888:8888``) and the final flag
(``-v``) binds the home directory into the containers home directory so data can be made available and will
persist beyond the container instance. For more information on how to configure containers for AiiDAlab
see [https://stfc.github.io/alc-ux](https://stfc.github.io/alc-ux).

## For Developers

### Style Checking

This package uses pre-commit hooks to check for style consistency, to use these the ``pre-commit`` tool is required.
This can be installed alongside the base package by running,

``` sh
pip install .[dev]
```

or separately via,

``` sh
pip install pre-commit 
```

Once installed run,

``` sh
pre-commit install 
```

in the base repository to enable the pre-commit hooks.
This will now run style and formatting checks on every commit.

### Testing

This package uses [pytest](https://docs.pytest.org/en/stable/)
to run all unit tests which is included in the ```[dev]``` optional
package dependencies. Once installed it can be run from the project root directory.
The CI workflows are configured to ensure all tests pass
before a pull request can be accepted into the main repository.
It is important that any new additions to the code base are accompanied
by appropriate testing, maintaining a high code coverage. The coverage
can be checked via,

``` sh
pytest --cov=aiidalab_alc 
```

### Documentation

The documentation, including a User Guide, Developer Guide and an API reference,
is built using [sphinx](https://www.sphinx-doc.org/). The source
for which is contained in the ```docs/``` directory. At present
only the html generator has been fully tested. All required packages can
be installed alongside the core package via,

``` sh
pip install .[docs]
```

and then the documentation can be built using sphinx-build,

``` sh
sphinx-build -b html docs/source/ docs/build/html 
```

from the root directory.

## License

[BSD 3-Clause License](LICENSE)

## Funding

Contributors to this project were funded by

<div align="center">
    <a href="https://adalovelacecentre.ac.uk/">
        <img src="images/alc.svg" alt="ALC Logo" style="width: 30%">
    </a>
</div>
