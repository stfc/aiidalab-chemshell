"""Defines the model and view components for the structure setup stage."""

import ase
import ipywidgets as ipw
from aiida.orm import SinglefileData, StructureData
from aiidalab_widgets_base import SmilesWidget, WizardAppWidgetStep

from aiidalab_chemshell.common.database import AiiDADatabaseWidget
from aiidalab_chemshell.common.file_handling import FileUploadWidget
from aiidalab_chemshell.common.structure_viewer import StructureViewWidget
from aiidalab_chemshell.models.structure import StructureInputModel


class StructureWizardStep(ipw.VBox, WizardAppWidgetStep):
    """
    Wizard for structure selection and manipulation.

    A step in a wizard based process widget which allows a user to
    configure a chemical structure to be used in their workflow.
    """

    def __init__(self, model: StructureInputModel, **kwargs):
        """
        StructureWizardStep constructor.

        Parameters
        ----------
        model : StructureStepModel
            A model controlling the data required for the structure step.
        **kwargs :
            Keyword arguments passed to the parent class's constructor.
        """
        super().__init__(children=[], **kwargs)
        self.rendered = False
        self.model = model

        self.info = ipw.HTML(
            """
                <p>
                    Load in a structure to start the workflow.
                </p>
            """
        )

        self.tabs = ipw.Tab()

        # upload file
        self.file_input_widget = ipw.VBox()
        self.file_uploader = FileUploadWidget(description="Structure file: ")
        self.file_input_widget.children = [
            self.file_uploader,
        ]
        ipw.dlink((self.file_uploader, "file"), (self.model, "structure_file"))

        # AiiDA database
        self.database_widget = AiiDADatabaseWidget(
            title="AiiDA Database",
            query=[SinglefileData, StructureData],
        )

        self.smiles_widget = SmilesWidget(title="SMILES")

        self.tabs.children = [
            self.file_input_widget,
            self.database_widget,
            self.smiles_widget,
        ]
        for i, title in enumerate(["Upload File", "AiiDA Database", "SMILES String"]):
            self.tabs.set_title(i, title)

        self.model.observe(self._on_file_upload, "structure_file")
        self.database_widget.observe(self._on_database_search, "data_object")
        self.smiles_widget.observe(self._on_smiles_generation, "structure")

    def render(self):
        """Render the wizard's contents if not already rendered."""
        if self.rendered:
            return

        self.submit_btn = ipw.Button(
            description="Submit Structure",
            disabled=False,
            button_style="success",
            tooltip="Submit the structure to the workflow",
            icon="check",
            layout={"margin": "auto", "width": "60%"},
        )
        self.submit_btn.on_click(self.submit_structure)
        self.viewer = ipw.HTML("<p>No structure found...</p>")

        self._update_children()
        self.rendered = True
        return

    def _update_children(self) -> None:
        self.children = [
            self.info,
            self.tabs,
            ipw.HTML("<h2>Viewer:</h2>"),
            self.viewer,
            self.submit_btn,
        ]
        return

    def _on_file_upload(self, change: dict) -> None:
        """When file upload button is pressed."""
        if self.model.has_file:
            self.viewer = StructureViewWidget()
            self.viewer.assign_structure_from_file(
                self.model.structure_file.filename, self.model.structure_file.content
            )
            self._update_children()
        return

    def _on_smiles_generation(self, change: dict) -> None:
        """When SMILES string is inputted."""
        if change["new"] != change["old"]:
            self._create_viewer(change["new"])
            self.model.structure = StructureData(ase=change["new"])
        return

    def _on_database_search(self, change: dict) -> None:
        """When data is loaded from AiiDA database."""
        if change["new"] == change["old"]:
            return
        if isinstance(change["new"], SinglefileData):
            self.model.structure_file = change["new"]
            self._on_file_upload(change)
        elif isinstance(change["new"], StructureData):
            self.model.structure = change["new"]
            self._create_viewer(change["new"]._get_object_ase())
        else:
            self._create_viewer(None)
        return

    def _create_viewer(self, structure: ase.Atoms | None) -> None:
        """Create a viewer widget with the loaded ase.Atoms structure object."""
        # if structure:
        #     # self.viewer = awb.viewers.StructureDataViewer(structure=structure)
        #     self.viewer = WeasWidget()
        #     self.viewer.from_ase(structure)
        # else:
        #     self.viewer = ipw.HTML("<p>Could not visualise structure ...</p>")
        self.viewer = StructureViewWidget()
        self.viewer.assign_structure_from_ase(structure)
        self._update_children()
        return

    def submit_structure(self, _):
        """Submit the structure step."""
        if self.model.has_file or self.model.has_structure:
            self.file_uploader.disable(True)
            self.database_widget.disable(True)
            self.submit_btn.disabled = True
            self.submit_btn.description = "Submitted"
            self.model.submitted = True
        else:
            self.model.submitted = False
        return
