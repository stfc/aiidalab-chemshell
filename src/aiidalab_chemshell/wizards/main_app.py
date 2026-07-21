"""Defines the core wizard widgets for the AiiDAlab ChemShell application pages."""

import aiidalab_widgets_base as awb
import ipywidgets as ipw

from aiidalab_chemshell.process import BaseAppModel
from aiidalab_chemshell.wizards.resources import (
    ComputationalResourcesWizardStep,
)
from aiidalab_chemshell.wizards.results import ResultsWizardStep
from aiidalab_chemshell.wizards.structure import StructureWizardStep
from aiidalab_chemshell.wizards.workflows import (
    BatchWorkflowWizardStep,
    WorkflowWizardStep,
)


class BaseWizardWidget(ipw.VBox):
    """
    The shared application construction wizard.

    A single wizard widget backing both the "New Calculation" and "Batch
    Processing" pages.
    """

    def __init__(self, model: BaseAppModel, batch: bool = False, **kwargs):
        """
        BaseWizardWidget constructor.

        Parameters
        ----------
        model : BaseAppModel
            The application model backing the wizard.
        batch : bool
            If True, build the batch processing wizard; otherwise build the
            main "New Calculation" wizard.
        **kwargs :
            Keyword arguments passed to the `ipywidgets.VBox.__init__()`.
        """
        if batch:
            self.structureStep = StructureWizardStep(model.structure_model, batch=True)
            self.workflowStep = BatchWorkflowWizardStep(model.workflow_model)
            structure_title = "Select Structures Input"
        else:
            self.structureStep = StructureWizardStep(model.structure_model)
            self.workflowStep = WorkflowWizardStep(model.workflow_model)
            structure_title = "Select Structure"

        self.compResourceStep = ComputationalResourcesWizardStep(model.resource_model)
        self.results_step = ResultsWizardStep(model.results_model)

        self._wizard_app_widget = awb.WizardAppWidget(
            steps=[
                (structure_title, self.structureStep),
                ("Configure Workflow", self.workflowStep),
                ("Configure Computational Resources", self.compResourceStep),
                ("Results", self.results_step),
            ]
        )

        self._wizard_app_widget.observe(
            self.on_step_change,
            "selected_index",
        )

        self.results_step.disabled = True
        self._model = model
        # Hide the header
        self._wizard_app_widget.children[0].layout.display = "none"

        super().__init__(
            children=[self._wizard_app_widget],
            **kwargs,
        )

        self._wizard_app_widget.selected_index = None

        return

    @property
    def steps(self):
        """Alias to the wizard's steps list."""
        return self._wizard_app_widget.steps

    def on_step_change(self, change):
        """Switch between wizard steps when selected by the user."""
        if (step_index := change["new"]) is not None:
            step = self.steps[step_index][1]
            step.render()
        return


class MainWizardWidget(BaseWizardWidget):
    """The main "New Calculation" application construction wizard."""

    def __init__(self, model: BaseAppModel, **kwargs):
        """MainWizardWidget constructor."""
        super().__init__(model, batch=False, **kwargs)


class BatchWizardWidget(BaseWizardWidget):
    """The batch processing application construction wizard."""

    def __init__(self, model: BaseAppModel, **kwargs):
        """BatchWizardWidget constructor."""
        super().__init__(model, batch=True, **kwargs)
