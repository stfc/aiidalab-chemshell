"""Defines the process history applicaion page."""

from datetime import datetime

from aiida.orm import CalcJobNode, WorkChainNode
from aiidalab_widgets_base import AiidaNodeViewWidget, ProcessNodesTreeWidget
from IPython.display import display
from ipywidgets import HTML, VBox, dlink

from aiidalab_chemshell.common.database import AiiDADatabaseWidget
from aiidalab_chemshell.common.navigation import QuickAccessButtons
from aiidalab_chemshell.results import ProcessModel


class HistoryApp:
    """The process history page's main app."""

    def __init__(self):
        """HistoryApp constructor."""
        self.model = HistoryModel()
        self.view = HistoryAppView(self.model)
        display(self.view)


class HistoryModel(ProcessModel):
    """MVC Model for process history app data management."""

    pass


class HistoryAppView(VBox):
    """Main view for the process history page."""

    def __init__(self, model: HistoryModel, **kwargs):
        """
        HistoryAppView Constructor.

        Parameters
        ----------
        model : HistoryModel
            The MVC model component to associate with this view app.
        """
        self.model = model
        logo = HTML(
            """
            <div class="app-container logo" style="width: 300px;">
                <img src="../images/alc.svg" alt="ALC AiiDAlab App Logo" />
            </div>
            """,
            layout={"margin": "auto"},
        )

        subtitle = HTML(
            """
            <h2 id='subtitle'>AiiDAlab ChemShell</h2>
            """
        )

        nav_btns = QuickAccessButtons()

        header = VBox(
            children=[
                logo,
                subtitle,
            ],
            layout={"margin": "auto"},
        )

        footer = HTML(
            f"""
            <footer>
                Copyright (c) {datetime.now().year} Ada Lovelace Centre
                (STFC) <br>
            </footer>
            """,
            layout={"align-content": "right"},
        )

        self.guide = HTML(
            """
            <h3>ChemShell Process History</h3>
            <p>
            Search through past ChemShell processes and visualise inputs, outputs and
            provenance relationships.
            </p>
            """
        )
        self.lookup_widget = AiiDADatabaseWidget(
            "Process Lookup", [CalcJobNode, WorkChainNode]
        )
        self.lookup_widget.observe(self._update_node_view, "data_object")

        self.node_tree = ProcessNodesTreeWidget()
        dlink((self.model, "process_uuid"), (self.node_tree, "value"))
        self.node_view = AiidaNodeViewWidget()
        dlink(
            (self.node_tree, "selected_nodes"),
            (self.node_view, "node"),
            transform=lambda nodes: nodes[0] if nodes else None,
        )

        super().__init__(
            layout={},
            children=[
                header,
                nav_btns,
                self.guide,
                self.lookup_widget,
                self.node_tree,
                self.node_view,
                footer,
            ],
            **kwargs,
        )
        return

    def _update_node_view(self, _) -> None:
        """Update the node view to the currently selected process node."""
        if self.lookup_widget.data_object is not None:
            self.model.process_uuid = self.lookup_widget.data_object.uuid
        return
