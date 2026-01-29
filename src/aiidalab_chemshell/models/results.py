"""Defines the MVC model for holding ChemShell results information."""

from traitlets import Bool

from aiidalab_chemshell.models.process import ProcessModel


class ResultsModel(ProcessModel):
    """MVC results step model."""

    blocked = Bool(True)
