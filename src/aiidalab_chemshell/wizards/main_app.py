"""Defines the wizard widget for the main AiiDAlab ChemShell application."""

import aiidalab_widgets_base as awb
import ipywidgets as ipw

from aiidalab_chemshell.process import MainAppModel
from aiidalab_chemshell.wizards.resources import (
    ComputationalResourcesWizardStep,
)
from aiidalab_chemshell.wizards.results import ResultsWizardStep
from aiidalab_chemshell.wizards.structure import StructureWizardStep
from aiidalab_chemshell.wizards.workflows import WorkflowWizardStep


class MainAppWizardWidget(ipw.VBox):
    """An ipywidgets based widget to hold the main application construct wizard."""

    def __init__(self, model: MainAppModel, **kwargs):
        """
        WizardWidget constructor.

        Parameters
        ----------
        **kwargs :
            Keyword arguments passed to the `ipywidgets.VBox.__init__()`.
        """
        self.structureStep = StructureWizardStep(model.structure_model)
        self.workflowStep = WorkflowWizardStep(model.workflow_model)
        self.compResourceStep = ComputationalResourcesWizardStep(model.resource_model)
        self.results_step = ResultsWizardStep(model.results_model)

        self._wizard_app_widget = awb.WizardAppWidget(
            steps=[
                ("Select Structure", self.structureStep),
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
