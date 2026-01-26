"""Defines the MVC models for ChemShell workflow specification."""

from aiida.orm import SinglefileData
from traitlets import (
    Bool,
    HasTraits,
    Instance,
    List,
    Unicode,
    UseEnum,
)

from aiidalab_chemshell.common.chemshell import BasisSetOptions, WorkflowOptions


class ChemShellWorkflowModel(HasTraits):
    """The model for setting up a ChemShell workflow."""

    # workflow = Integer(0, allow_none=False).tag(sync=True)
    workflow = UseEnum(WorkflowOptions, WorkflowOptions.GEOMETRY, allow_none=False)

    qm_theory = Unicode("NWChem", allow_none=False)
    mm_theory = Unicode("DL_POLY", allow_none=True)
    qm_region = List([], allow_none=True)
    basis_quality = UseEnum(BasisSetOptions, BasisSetOptions.FAST, allow_none=False)
    force_field = Instance(SinglefileData, allow_none=True)
    submitted = Bool(False).tag(sync=True)
    use_mm = Bool(False).tag(sync=True)

    default_guide = ""
