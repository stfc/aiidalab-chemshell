"""Defines the model and view components for the structure setup stage."""

import aiidalab_widgets_base as awb
import ipywidgets as ipw

from aiidalab_chemshell.common.structure_uploader import StructureSelectionWidget
from aiidalab_chemshell.models.structure import StructureInputModel


class StructureWizardStep(ipw.VBox, awb.WizardAppWidgetStep):
    """
    Wizard for structure selection and manipulation.

    A step in a wizard based process widget which allows a user to
    configure a chemical structure to be used in their workflow.
    """

    def __init__(self, model: StructureInputModel, batch: bool = False, **kwargs):
        """
        StructureWizardStep constructor.

        Parameters
        ----------
        model : StructureStepModel
            A model controlling the data required for the structure step.
        batch : bool
            If True, configure the step for batch input (a ``TrajectoryData`` or
            a multi-frame structure file) rather than a single structure.
        **kwargs :
            Keyword arguments passed to the parent class's constructor.
        """
        super().__init__(children=[], **kwargs)
        self.rendered = False
        self.model = model
        self.batch = batch

        if self.batch:
            self.info = ipw.HTML(
                """
                    <p>
                        Select the input to process as a batch. This can be either
                        a multi-frame <code>.xyz</code> file or a
                        <code>TrajectoryData</code> object. Each frame is run as an
                        individual single point energy calculation.
                    </p>
                """
            )
        else:
            self.info = ipw.HTML(
                """
                    <p>
                        Load in a structure to start the workflow.
                    </p>
                """
            )

        self.structure_uploader = StructureSelectionWidget(batch=batch)

        ipw.dlink(
            (self.structure_uploader, "structure_file"),
            (self.model, "structure_file"),
        )
        ipw.dlink(
            (self.structure_uploader, "structure_data"), (self.model, "structure")
        )
        ipw.dlink(
            (self.structure_uploader, "trajectory_data"), (self.model, "trajectory")
        )

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
        self.error = ipw.HTML("")

        self._update_children()
        self.rendered = True
        return

    def _update_children(self) -> None:
        self.children = [
            self.info,
            self.structure_uploader,
            self.error,
            self.submit_btn,
        ]
        return

    def submit_structure(self, _):
        """Submit the structure step."""
        self.error.value = ""
        # Batch file input must be a multi-frame .xyz file.
        if self.batch and self.model.has_file:
            filename = self.model.structure_file.filename
            if not filename.lower().endswith(".xyz"):
                self.error.value = (
                    "<p style='color:red;'>Batch file input must be a multi-frame "
                    "<code>.xyz</code> file.</p>"
                )
                self.model.submitted = False
                return

        if self.model.has_file or self.model.has_structure or self.model.has_trajectory:
            self.submit_btn.disabled = True
            self.submit_btn.description = "Submitted"
            self.structure_uploader.disable(True)
            self.model.submitted = True
        else:
            self.model.submitted = False
        return
