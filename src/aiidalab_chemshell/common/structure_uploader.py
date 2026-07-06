"""Widget for selecting an input structure from various sources."""

from aiida.orm import SinglefileData, StructureData, TrajectoryData
from aiidalab_widgets_base import SmilesWidget
from alc_aiidalab_widgets.widgets import StructureViewWidget
from ase import Atoms
from ipywidgets import HTML, Tab, VBox, dlink
from traitlets import HasTraits, Instance

from aiidalab_chemshell.common.database import AiiDADatabaseWidget
from aiidalab_chemshell.common.file_handling import FileUploadWidget


class StructureSelectionWidget(VBox, HasTraits):
    """Widget for selecting an input structre from various sources."""

    structure_data = Instance(StructureData, allow_none=True)
    structure_file = Instance(SinglefileData, allow_none=True)
    trajectory_data = Instance(TrajectoryData, allow_none=True)

    def __init__(self, **kwargs):
        """StructureSelectionWidget constructor."""
        super().__init__(**kwargs)
        # upload file
        self.file_input_widget = VBox()
        self.file_uploader = FileUploadWidget(description="Structure file: ")
        self.file_input_widget.children = [
            self.file_uploader,
        ]

        # AiiDA database
        self.database_widget = AiiDADatabaseWidget(
            title="AiiDA Database",
            query=[SinglefileData, StructureData],
        )

        self.smiles_widget = SmilesWidget(title="SMILES")

        self.tabs = Tab()
        self.tabs.children = [
            self.file_input_widget,
            self.database_widget,
            self.smiles_widget,
        ]
        for i, title in enumerate(["Upload File", "AiiDA Database", "SMILES String"]):
            self.tabs.set_title(i, title)

        self.viewer = HTML("<p>No structure found...</p>")

        self.children = [self.tabs, HTML("<h2>Viewer:</h2>"), self.viewer]

        self.file_uploader.observe(self._on_file_upload, "file")
        self.database_widget.observe(self._on_database_search, "data_object")
        self.smiles_widget.observe(self._on_smiles_generation, "structure")

        dlink((self.file_uploader, "file"), (self, "structure_file"))

        return

    def _on_file_upload(self, change: dict) -> None:
        """When file upload button is pressed."""
        if change["new"] != change["old"]:
            self.viewer = StructureViewWidget()
            self.viewer.assign_structure_from_file(
                self.file_uploader.file.filename,
                self.file_uploader.file.content,
            )
            self._update_children()
        return

    def _on_smiles_generation(self, change: dict) -> None:
        """When SMILES string is inputted."""
        if change["new"] != change["old"]:
            self._create_viewer(change["new"])
            self.structure = StructureData(ase=change["new"])
            if self.structure_file:
                self.structure_file = None
        return

    def _on_database_search(self, change: dict) -> None:
        """When data is loaded from AiiDA database."""
        if change["new"] == change["old"]:
            return
        if isinstance(change["new"], SinglefileData):
            if self.structure_data:
                self.structure_data = None
            self.structure_file = change["new"]
            self._on_file_upload(change)
        elif isinstance(change["new"], StructureData):
            if self.structure_file:
                self.structure_file = None
            self.structure = change["new"]
            self._create_viewer(change["new"]._get_object_ase())
        else:
            self._create_viewer(None)
        return

    def _create_viewer(self, structure: Atoms | None) -> None:
        """Create a viewer widget with the loaded ase.Atoms structure object."""
        if structure:
            self.viewer = StructureViewWidget()
            self.viewer.assign_structure_from_ase(structure)
        else:
            self.viewer = HTML("<p>Could not visualise structure ...</p>")
        self._update_children()
        return

    def _update_children(self) -> None:
        self.children = [
            self.tabs,
            self.viewer,
        ]
        return

    def disable(self, val: bool = True) -> None:
        """Disable the widget and all children."""
        for child in self.tabs.children:
            try:
                child.disable(True)
            except AttributeError:
                pass  # TODO: SmilesWidget cannot be easily disabled at present.
