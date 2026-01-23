"""Defines the MVC model for holding ChemShell results information."""

from traitlets import Bool, UseEnum

from aiidalab_chemshell.common.chemshell import WorkflowOptions
from aiidalab_chemshell.models.process import ProcessModel


class ResultsModel(ProcessModel):
    """MVC results step model."""

    blocked = Bool(True)
    workflow = UseEnum(
        WorkflowOptions,
        WorkflowOptions.GEOMETRY,
        allow_none=False,
        read_only=True,
        help="The workflow that has been carried out.",
    )
