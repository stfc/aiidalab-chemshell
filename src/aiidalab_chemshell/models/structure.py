"""The structure input model for ChemShell input configuration."""

from aiida.orm import SinglefileData, StructureData, TrajectoryData
from traitlets import Bool, HasTraits, Instance, observe


class StructureInputModel(HasTraits):
    """Model for structure selection and manipulation."""

    structure = Instance(StructureData, allow_none=True)
    structure_file = Instance(SinglefileData, allow_none=True)
    trajectory = Instance(TrajectoryData, allow_none=True)
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
    def has_trajectory(self) -> bool:
        """True if a TrajectoryData object has been attached to the model."""
        return self.trajectory is not None

    @property
    def is_periodic(self) -> bool:
        """True if the attached StructureData object is a periodic structure."""
        if self.has_structure:
            return any(self.structure.pbc)
        return False

    @observe("structure")
    def _update_structure(self, _) -> None:
        """Clear other inputs if a StructureData object is provided."""
        if self.structure is not None:
            self.structure_file = None
            self.trajectory = None
        return

    @observe("structure_file")
    def _update_structure_file(self, _) -> None:
        """Clear other inputs if a structure file is provided."""
        if self.structure_file is not None:
            self.structure = None
            self.trajectory = None
        return

    @observe("trajectory")
    def _update_trajectory(self, _) -> None:
        """Clear other inputs if a TrajectoryData object is provided."""
        if self.trajectory is not None:
            self.structure = None
            self.structure_file = None
        return
