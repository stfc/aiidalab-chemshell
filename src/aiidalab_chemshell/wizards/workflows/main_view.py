"""The main view for the workflow wizard step."""

import aiidalab_widgets_base as awb
import ipywidgets as ipw

from aiidalab_chemshell.common.chemshell import WorkflowOptions
from aiidalab_chemshell.common.utils import (
    add_button_style_class,
    chemshell_button_style,
)
from aiidalab_chemshell.models.workflow import ChemShellWorkflowModel
from aiidalab_chemshell.wizards.workflows.geometry_optimisation import (
    ChemShellOptionsWidget,
)
from aiidalab_chemshell.wizards.workflows.isolated_atoms import IsolatedAtomEnergyWidget
from aiidalab_chemshell.wizards.workflows.neb import NEBOptionsWidget
from aiidalab_chemshell.wizards.workflows.single_point import SinglePointCalcWidget


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

        # Create the options widgets
        self.workflow_tabs.children = [
            self._generate_workflow_widgets(workflow) for workflow in WorkflowOptions
        ]
        # Core Geometry Optimisation Workflow
        for i, workflow in enumerate(WorkflowOptions):
            self.workflow_tabs.set_title(i, workflow.tab_label)

        self.workflow_tabs.selected_index = self.model.workflow.value

        # Link necessary inputs to model
        # ipw.dlink((self.workflow_tabs, "selected_index"), (self.model, "workflow"))
        self.workflow_tabs.observe(self._update_selected_workflow, "selected_index")
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
            layout={"width": "60%", "height": "30px", "margin": "20px auto 8px"},
        )
        self.submit_btn.on_click(self._submit)
        add_button_style_class(self.submit_btn)

        # Create the wizard from the component widgets
        self.children = [
            chemshell_button_style(),
            self.header,
            self.guide,
            self.workflow_tabs,
            self.submit_btn,
        ]
        self.rendered = True
        self.workflow_tabs.children[self.workflow_tabs.selected_index].render()
        return

    def _submit(self, _):
        """Store the ChemShell parameters in the ChemShell workflow model."""
        # Check for force field file if MM has been requested
        if self.model.use_mm and self.model.workflow != WorkflowOptions.ATOMIC_ENERGIES:
            if not self.model.force_field:
                print("ERROR: No force field file found...")
                return
        # Check for second structure file is NEB is requested
        if self.model.workflow == WorkflowOptions.NEB:
            if (
                not self.model.structure_2.has_file
                and not self.model.structure_2.has_structure
            ):
                print("ERROR: NEB calculation requires a second structure input.")
                return
        # Disable the widgets and mark as submitted
        if self.workflow_tabs.selected_index == 0:
            self.workflow_tabs.children[0].disable(True)
        else:
            self.workflow_tabs.children[self.workflow_tabs.selected_index].disable()
        self.submit_btn.description = "Submitted"
        self.submit_btn.disabled = True
        # Mark the (collapsed) step as complete via the AWB wizard icon.
        self.state = self.State.SUCCESS
        return

    def _generate_workflow_widgets(self, workflow: WorkflowOptions) -> ipw.VBox:
        match workflow:
            case WorkflowOptions.GEOMETRY:
                return ChemShellOptionsWidget(self.model)
            case WorkflowOptions.ATOMIC_ENERGIES:
                return IsolatedAtomEnergyWidget(self.model)
            case WorkflowOptions.SINGLE_POINT:
                return SinglePointCalcWidget(self.model)
            case WorkflowOptions.NEB:
                return NEBOptionsWidget(self.model)
            case _:
                return ipw.VBox()

    def _update_selected_workflow(self, _) -> None:
        self.model.workflow = WorkflowOptions(self.workflow_tabs.selected_index)
        self.workflow_tabs.children[self.workflow_tabs.selected_index].render()
        return


class BatchWorkflowWizardStep(ipw.VBox, awb.WizardAppWidgetStep):
    """
    Wizard step for configuring the single point energy options for a batch.

    Reuses the standard :class:`SinglePointCalcWidget` (the same widget used on
    the main calculation page) so that every item in the batch is run with an
    identical single point energy configuration.
    """

    def __init__(self, model: ChemShellWorkflowModel, **kwargs):
        """
        BatchWorkflowWizardStep constructor.

        Parameters
        ----------
        model : ChemShellWorkflowModel
            The model that defines the single point workflow configuration.
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
            <p>
                Define a ChemShell workflow which is then applied to all structures
                within a given batch input.
                The results of which can then be combined into a single
                extended XYZ file.
            </p>
            """
        )

        self.combine_results = ipw.Checkbox(
            value=True, description="Combine Results", index=True
        )
        ipw.dlink(
            (self.combine_results, "value"), (self.model, "combine_batch_results")
        )

        self.options = SinglePointCalcWidget(self.model)

        self.submit_btn = ipw.Button(
            description="Submit Options",
            disabled=False,
            button_style="success",
            tooltip="Submit the workflow configuration",
            icon="check",
            layout={"width": "60%", "height": "30px", "margin": "20px auto 8px"},
        )
        self.submit_btn.on_click(self._submit)
        add_button_style_class(self.submit_btn)

        self.children = [
            self.header,
            self.combine_results,
            self.options,
            self.submit_btn,
        ]
        self.rendered = True
        self.options.render()
        return

    def _submit(self, _):
        """Store and lock in the single point configuration."""
        if self.model.use_mm and not self.model.force_field:
            print("ERROR: No force field file found...")
            return
        self.options.disable(True)
        self.submit_btn.description = "Submitted"
        self.submit_btn.disabled = True
        # Mark the (collapsed) step as complete via the AWB wizard icon.
        self.state = self.State.SUCCESS
        return
