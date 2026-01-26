"""Module containing common settings for configuring ChemShell."""

from enum import Enum, auto


class BasisSetOptions(Enum):
    """Pre-defined basis set levels for simplified ChemShell inputs."""

    FAST = 0
    BALANCED = auto()
    QUALITY = auto()

    @property
    def label(self) -> str:
        """Convert enum value to a string representation for ChemShell input."""
        match self:
            case BasisSetOptions.FAST:
                return "3-21G"
            case BasisSetOptions.BALANCED:
                return "cc-pvdz"
            case BasisSetOptions.QUALITY:
                return "aug-cc-pvtz"
            case "":
                return ""


class WorkflowOptions(Enum):
    """Enum defining the available ChemShell based AiiDA workflows."""

    GEOMETRY = 0
    NEB = auto()

    @property
    def label(self) -> str:
        """Convert enum value into a more human readable string."""
        match self:
            case WorkflowOptions.GEOMETRY:
                return "Geometry Optimisation"
            case WorkflowOptions.NEB:
                return "Nudged Elastic Band"
            case _:
                return ""

    @property
    def tab_label(self) -> str:
        """Create a tab title for the given enum option."""
        match self:
            case WorkflowOptions.GEOMETRY:
                return "Optimisation"
            case WorkflowOptions.NEB:
                return "NEB"
            case _:
                return "ChemShell"
