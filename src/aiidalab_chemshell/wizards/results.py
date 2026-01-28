"""Module for defining widgets/models for viewing process progress and results."""

import ipywidgets as ipw
from aiidalab_widgets_base import ProcessNodesTreeWidget, WizardAppWidgetStep

from aiidalab_chemshell.common.node_viewers import CustomAiidaNodeViewWidget
from aiidalab_chemshell.models.results import ResultsModel


class ResultsWizardStep(ipw.VBox, WizardAppWidgetStep):
    """Wizard for viewing process progress and results."""

    def __init__(self, model: ResultsModel, **kwargs):
        """
        ResultsWizardStep constructor.

        Parameters
        ----------
        model : ResultsModel
            The model controlling required data.
        **kwargs :
            Keyword arguments passed to the parent class's constructor.
        """
        self.rendered = False
        self.model = model

        self.info = ipw.HTML(
            f"""
            <p>
                View the progress and results of the generated ChemShell
                {self.model.workflow.label} workflow.
            </p>
            """
        )

        self.update_btn = ipw.Button(
            description="Refresh",
            icon="arrows-rotate",
            disabled=False,
            button_style="info",
            tooltip="Refresh process information.",
            layout={"margin": "auto", "width": "70%"},
        )
        self.update_btn.on_click(self._refresh_info)

        super().__init__(**kwargs)
        return

    def render(self) -> None:
        """Render the wizard's uninitialised content."""
        if self.rendered:
            return
        if self.model.blocked:
            msg = ipw.HTML(
                """
                <p>
                    No process has been submitted...
                </p>
                """
            )
            self.children = [msg]
        else:
            self.node_tree = ProcessNodesTreeWidget()
            ipw.dlink((self.model, "process_uuid"), (self.node_tree, "value"))
            self.node_view = CustomAiidaNodeViewWidget()
            ipw.dlink(
                (self.node_tree, "selected_nodes"),
                (self.node_view, "node"),
                transform=lambda nodes: nodes[0] if nodes else None,
            )

            self.children = [
                self.info,
                self.node_tree,
                self.node_view,
                self.update_btn,
            ]
            self.rendered = True
        return

    def _refresh_info(self, _) -> None:
        """Refresh the process information."""
        self.node_tree.update()
        return
