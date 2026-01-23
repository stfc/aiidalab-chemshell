"""Module containing common settings for configuring ChemShell."""

from enum import Enum, auto


class BasisSet(Enum):
    """Pre-defined basis set levels for simplified ChemShell inputs."""

    FAST = auto()
    BALANCED = auto()
    QUALITY = auto()

    @property
    def label(self) -> str:
        """Convert enum value to a string representation for ChemShell input."""
        match self:
            case BasisSet.FAST:
                return "3-21G"
            case BasisSet.BALANCED:
                return "cc-pvdz"
            case BasisSet.QUALITY:
                return "aug-cc-pvtz"


class Workflows(Enum):
    """Enum defining the available ChemShell based AiiDA workflows."""

    GEOMETRY = auto()
    NEB = auto()
