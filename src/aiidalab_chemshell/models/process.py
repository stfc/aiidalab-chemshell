"""Defines the MVC model for a full ChemShell process."""

from typing import cast

import traitlets as tl
from aiida.common.exceptions import NotExistent
from aiida.orm import NodeLinksManager, ProcessNode, load_node


class ProcessModel(tl.HasTraits):
    """Model describing an AiiDA process."""

    process_uuid = tl.Unicode(None, allow_none=True)

    @property
    def process(self) -> ProcessNode | None:
        """Return the process node for the stored uuid."""
        if not self.process_uuid:
            return None
        try:
            return cast(ProcessNode, load_node(self.process_uuid))
        except NotExistent:
            return None

    @property
    def has_process(self) -> bool:
        """Return true if a valid process node is associated with the uuid."""
        return self.process is not None

    @property
    def inputs(self) -> NodeLinksManager | list:
        """Return the inputs for the process."""
        return self.process.inputs if self.has_process else []

    @property
    def outputs(self) -> NodeLinksManager | list:
        """Return the outputs for teh process."""
        return self.process.outputs if self.has_process else []
