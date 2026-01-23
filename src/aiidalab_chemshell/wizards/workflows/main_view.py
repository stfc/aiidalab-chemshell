"""The main view for the workflow wizard step."""

import aiidalab_widgets_base as awb
import ipywidgets as ipw

from aiidalab_chemshell.models.workflow import ChemShellWorkflowModel
from aiidalab_chemshell.wizards.workflows.geometry_optimisation import (
    ChemShellOptionsWidget,
)


class WorkflowWizardStep(ipw.VBox, awb.WizardAppWidgetStep):
    """Wizard setup for the calculation workflow."""

    def __init__(self, model: ChemShellWorkflowModel, **kwargs):
        """
        MethodWizardStep constructor.

        Parameters
        ----------
        model : ChemShellWorkflowModel
            The model that defines the data related to this step in the setup wizard.
        **kwargs :
            Keyword arguments passed to the parent class's constructor.
        """
        super().__init__(children=[], **kwargs)
        self.model = model
        self.rendered = False

        return

    def render(self):
        """Render the wizard contents if not already rendered."""
        if self.rendered:
            return

        self.header = ipw.HTML(
            """
            <h2> ChemShell Workflow Configuration </h2>
            """,
            layout={"margin": "auto"},
        )
        self.guide = ipw.HTML(
            """
            <p>Configure any one of the available ChemShell workflows</p>
            """
        )

        self.workflow_tabs = ipw.Tab()

        # Core Geometry Optimisation Workflow
        self.workflow_tabs.set_title(0, "Geometry Optimisation")
        self.workflow_tabs.set_title(1, "Gas Phase NEB")

        # Create the options widgets
        self.workflow_tabs.children = [
            ChemShellOptionsWidget(self.model),
            ipw.VBox(),
        ]

        self.workflow_tabs.selected_index = self.model.workflow

        # Link necessary inputs to model
        ipw.dlink((self.workflow_tabs, "selected_index"), (self.model, "workflow"))
        ipw.dlink(
            (self.workflow_tabs.children[0].ff_file, "file"),
            (self.model, "force_field"),
        )

        # Create a submit button for the bottom of the wizard
        self.submit_btn = ipw.Button(
            description="Submit Options",
            disabled=False,
            button_style="success",
            tooltip="Submit the workflow configuration",
            icon="check",
            layout={"margin": "auto", "width": "60%"},
        )
        self.submit_btn.on_click(self._submit)

        # Create the wizard from the component widgets
        self.children = [self.header, self.guide, self.workflow_tabs, self.submit_btn]
        self.rendered = True
        return

    def _submit(self, _):
        """Store the ChemShell parameters in the ChemShell workflow model."""
        if self.workflow_tabs.selected_index == 0:
            self.model.qm_theory = self.workflow_tabs.children[
                0
            ].qm_theory_dropdown.value
            self.model.mm_theory = self.workflow_tabs.children[
                0
            ].mm_theory_dropdown.value
            try:
                self.model.qm_region = [
                    int(x)
                    for x in self.workflow_tabs.children[0].qm_region_text.value.split(
                        ","
                    )
                ]
            except ValueError:
                self.model.qm_region.clear()
                self.workflow_tabs.children[0].qm_region_text.value = ""
            except Exception as e:
                raise e
            if self.model.use_mm:
                if not self.model.force_field:
                    print("ERROR: No force field file found...")
                    return
            self.submit_btn.description = "Submitted"
            self.submit_btn.disabled = True
            self.workflow_tabs.children[0].disable(True)
        return
