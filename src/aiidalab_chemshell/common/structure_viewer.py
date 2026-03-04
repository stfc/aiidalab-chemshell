"""Defines a widget for visualisation of chemical structures."""

from pathlib import Path
from tempfile import NamedTemporaryFile

from ase import Atoms
from ase import io as ase_io
from ipywidgets import HTML, VBox
from weas_widget import WeasWidget


class StructureViewWidget(VBox):
    """Visualise atom structure using weas_widget."""

    def __init__(self, **kwargs):
        """StructureViewWidget constructor."""
        super().__init__(**kwargs)
        self.message = HTML("<p>No Structure Currently Loaded</p>")
        self.viewer = None
        self.children = [
            self.message,
        ]

    def assign_structure_from_file(self, fname: str, content: bytes) -> None:
        """Visualise the given structure from a file."""
        suffix = "".join(Path(fname).suffixes)
        with NamedTemporaryFile(suffix=suffix) as tmpf:
            tmpf.write(content)
            tmpf.flush()
            try:
                structure = ase_io.read(tmpf.name, index=":")[0]
            except (KeyError, ase_io.formats.UnknownFileTypeError):
                self.message = HTML("<p>Could not visualise structure...</p>")
                self.children = [
                    self.message,
                ]
            except Exception as e:
                raise e
            else:
                if suffix == "cjson":
                    # ASE doesn't correctly interpret atomic units so convert all units
                    # to angstrom
                    for i in range(len(structure)):
                        structure.positions[i] = structure.positions[i] * 0.529177
                self.viewer = WeasWidget()
                self.viewer.from_ase(structure)
                self.children = [
                    self.viewer,
                ]
        return

    def assign_structure_from_ase(self, structure: Atoms) -> None:
        """Visualise the given ASE structure."""
        self.viewer = WeasWidget()
        self.viewer.from_ase(structure)
        self.children = [
            self.viewer,
        ]
        return
