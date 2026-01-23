"""Defines the MVC model for holding ChemShell results information."""

import traitlets as tl

from aiidalab_chemshell.models.process import ProcessModel


class ResultsModel(ProcessModel):
    """MVC results step model."""

    blocked = tl.Bool(True)
