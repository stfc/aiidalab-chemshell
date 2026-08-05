"""Widget for selecting an input structure from various sources."""

import aiidalab_widgets_base as awb
import ipywidgets as ipw
from aiida.orm import SinglefileData, StructureData, TrajectoryData
from alc_aiidalab_widgets.widgets import (
    AiiDADatabaseQueryWidget,
    FileUploadWidget,
    StructureViewWidget,
)
from traitlets import HasTraits, Instance


class StructureSelectionWidget(ipw.VBox, HasTraits):
    """Widget for selecting an input structre from various sources."""

    structure_data = Instance(StructureData, allow_none=True)
    structure_file = Instance(SinglefileData, allow_none=True)
    trajectory_data = Instance(TrajectoryData, allow_none=True)

    def __init__(self, batch: bool = False, **kwargs):
        """
        StructureSelectionWidget constructor.

        Parameters
        ----------
        batch: bool
            If true assume input will be a batch/trajectory style input
        **kwargs :
            Keyword arguments passed to the parent class's constructor.
        """
        super().__init__(**kwargs)
        self.batch = batch
        # upload file
        self.file_input_widget = ipw.VBox()
        self.file_uploader = FileUploadWidget(description="Structure file: ")
        self.file_input_widget.children = [
            self.file_uploader,
        ]
        self.file_uploader.observe(self._on_file_upload, "file")
        ipw.dlink((self.file_uploader, "file"), (self, "structure_file"))

        # AiiDA database
        self.database_widget = AiiDADatabaseQueryWidget(
            title="AiiDA Database",
            query=[SinglefileData, TrajectoryData]
            if batch
            else [SinglefileData, StructureData],
        )
        self.database_widget.observe(self._on_database_search, "data_object")

        tabs_children = {
            "Upload File": self.file_input_widget,
            "AiiDA Database": self.database_widget,
        }
        if not self.batch:
            self.smiles_widget = awb.SmilesWidget(title="SMILES")
            self.smiles_widget.observe(self._on_smiles_generation, "structure")
            tabs_children["SMILES String"] = self.smiles_widget

        self.tabs = ipw.Tab()
        self.tabs.children = [item for key, item in tabs_children.items()]
        for i, title in enumerate(tabs_children.keys()):
            self.tabs.set_title(i, title)

        self.viewer = ipw.HTML("<p>No structure found...</p>")

        self.children = [self.tabs, self.viewer]

        return

    def _on_file_upload(self, change: dict) -> None:
        """When file upload button is pressed."""
        if change["new"] != change["old"]:
            self.viewer = StructureViewWidget(self.file_uploader.file)  # type: ignore
            # self.viewer.assign_structure_from_file(
            #     self.file_uploader.file.filename,
            #     self.file_uploader.file.content,
            # )
            self._update_children()
        return

    def _on_smiles_generation(self, change: dict) -> None:
        """When SMILES string is inputted."""
        if change["new"] != change["old"]:
            self.structure_data = StructureData(ase=change["new"])
            self.viewer = StructureViewWidget(self.structure_data)
            self._update_children()
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
            if self.trajectory_data:
                self.trajectory_data = None
            self.structure_file = change["new"]
            self._update_children()
        elif isinstance(change["new"], TrajectoryData):
            if self.structure_file:
                self.structure_file = None
            if self.structure_data:
                self.structure_data = None
            self.trajectory_data = change["new"]
        elif isinstance(change["new"], StructureData):
            if self.structure_file:
                self.structure_file = None
            self.structure = change["new"]
        self.viewer = StructureViewWidget(change["new"])
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
