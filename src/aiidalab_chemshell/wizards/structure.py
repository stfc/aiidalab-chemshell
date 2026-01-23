"""Defines the model and view components for the structure setup stage."""

from pathlib import Path
from tempfile import NamedTemporaryFile

import aiidalab_widgets_base as awb
import ase
import ipywidgets as ipw
from aiida.orm import SinglefileData

from aiidalab_chemshell.common.database import AiiDADatabaseWidget
from aiidalab_chemshell.common.file_handling import FileUploadWidget
from aiidalab_chemshell.models.structure import StructureInputModel


class StructureWizardStep(ipw.VBox, awb.WizardAppWidgetStep):
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
        self.tabs.set_title(0, "Upload File")
        self.file_input_widget = ipw.VBox()
        self.file_uploader = FileUploadWidget(description="Structure file: ")
        self.file_input_widget.children = [
            self.file_uploader,
        ]
        ipw.dlink((self.file_uploader, "file"), (self.model, "structure_file"))

        # AiiDA database
        self.tabs.set_title(1, "AiiDA Database")
        self.database_widget = AiiDADatabaseWidget(
            title="AiiDA Database",
            query=[
                SinglefileData,
            ],
        )
        ipw.dlink((self.database_widget, "data_object"), (self.model, "structure_file"))

        self.tabs.children = [self.file_input_widget, self.database_widget]

        self.model.observe(self._on_file_upload, "structure_file")

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

    def _on_file_upload(self, change=None):
        """When file upload button is pressed."""
        if self.model.has_file:
            structure = self._get_ase_object_from_file(
                self.model.structure_file.filename, self.model.structure_file.content
            )
            if structure:
                self.viewer = awb.viewers.StructureDataViewer(structure=structure)
            else:
                self.viewer = ipw.HTML(
                    "<p>Could not visualise structure from file...</p>"
                )
            self._update_children()
        return

    def _get_ase_object_from_file(self, fname: str, content: bytes) -> ase.Atoms | None:
        suffix = "".join(Path(fname).suffixes)
        with NamedTemporaryFile(suffix=suffix) as tmpf:
            tmpf.write(content)
            tmpf.flush()
            try:
                structure = ase.io.read(tmpf.name, index=":")[0]
            except (KeyError, ase.io.formats.UnknownFileTypeError):
                structure = None
        return structure

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
