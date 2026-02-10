"""The structure input model for ChemShell input configuration."""

from aiida.orm import SinglefileData, StructureData
from traitlets import Bool, HasTraits, Instance, observe


class StructureInputModel(HasTraits):
    """
    Model for structure selection and manipulation.

    A model to define and store required information from the structure
    step in the app's configuration wizard.
    """

    structure = Instance(StructureData, allow_none=True)
    structure_file = Instance(SinglefileData, allow_none=True)
    submitted = Bool(False).tag(sync=True)

    @property
    def has_structure(self) -> bool:
        """True if a StructureData object has been attached to the model."""
        return self.structure is not None

    @property
    def has_file(self) -> bool:
        """True if a raw structure file object has been attached to the model."""
        return self.structure_file is not None

    @property
    def is_periodic(self) -> bool:
        """True if the attached StructureData object is a periodic structure."""
        if self.has_structure:
            return any(self.structure.pbc)
        return False

    @observe("structure")
    def _update_structure(self, _) -> None:
        """Remove any file associated if a StructureData object is provided."""
        self.structure_file = None
        return
