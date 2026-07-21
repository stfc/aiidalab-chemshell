"""Defines the process history applicaion page."""

from datetime import datetime

import aiidalab_widgets_base as awb
import ipywidgets as ipw
from aiida.orm import CalcJobNode, WorkChainNode
from alc_aiidalab_widgets.widgets import AiiDADatabaseQueryWidget
from IPython.display import display

from aiidalab_chemshell.common.navigation import QuickAccessButtons
from aiidalab_chemshell.common.node_viewers import CustomAiidaNodeViewWidget
from aiidalab_chemshell.models.process import ProcessModel


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


class HistoryAppView(ipw.VBox):
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
        logo = ipw.HTML(
            """
            <div class="app-container logo" style="width: 500px;">
                <img src="../images/chemshell.png" alt="ChemShell Logo" />
            </div>
            """,
            layout={"margin": "auto"},
        )

        # subtitle = ipw.HTML(
        #     """
        #     <h2 id='subtitle' style="text-align: center;">AiiDAlab ChemShell</h2>
        #     """
        # )

        nav_btns = QuickAccessButtons()

        header = ipw.VBox(
            children=[
                logo,
                # subtitle,
            ],
            layout={"margin": "auto"},
        )

        footer = ipw.HTML(
            f"""
            <footer>
                Copyright (c) {datetime.now().year} Ada Lovelace Centre
                (STFC) <br>
            </footer>
            """,
            layout={"align-content": "right"},
        )
        h_line = ipw.HTML("<hr>")

        self.guide = ipw.HTML(
            """
            <h3>ChemShell Process History</h3>
            <p>
            Search through past ChemShell processes and visualise inputs, outputs and
            provenance relationships.
            </p>
            """
        )
        self.lookup_widget = AiiDADatabaseQueryWidget(
            "Process Lookup", [CalcJobNode, WorkChainNode]
        )
        self.lookup_widget.observe(self._update_node_view, "data_object")

        self.node_tree = awb.ProcessNodesTreeWidget()
        ipw.dlink((self.model, "process_uuid"), (self.node_tree, "value"))
        self.node_view = CustomAiidaNodeViewWidget()
        ipw.dlink(
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
                h_line,
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
