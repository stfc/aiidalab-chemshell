"""Defines the MVC models for ChemShell workflow specification."""

import traitlets as tl
from aiida.orm import SinglefileData


class ChemShellWorkflowModel(tl.HasTraits):
    """The model for setting up a ChemShell workflow."""

    workflow = tl.Integer(0, allow_none=False).tag(sync=True)

    qm_theory = tl.Unicode("NONE", allow_none=False)
    mm_theory = tl.Unicode("NONE", allow_none=True)
    qm_region = tl.List([], allow_none=True)
    basis_quality = tl.Bool(True, allow_none=False)
    force_field = tl.Instance(SinglefileData, allow_none=True)
    submitted = tl.Bool(False).tag(sync=True)
    use_mm = tl.Bool(False).tag(sync=True)

    default_guide = ""
