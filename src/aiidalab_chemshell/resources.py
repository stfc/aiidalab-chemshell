"""Defines a resource setup widget based on foundations from aiidalab-widgets-base."""

import aiidalab_widgets_base as awb
import ipywidgets as ipw
from traitlets import HasTraits, Unicode, observe


class CodeSetupWidget(ipw.VBox, HasTraits):
    """Widget to setup a new code instance."""

    _database_source = Unicode(
        "",
        allow_none=False,
    )

    def __init__(self, **kwargs):
        self.source = ipw.Text(
            value=self._database_source, description="Source: ", layout={"width": "80%"}
        )
        ipw.dlink((self.source, "value"), (self, "_database_source"))
        self.resource_widget = awb.computational_resources.ResourceSetupBaseWidget()
        self.setup_message = awb.utils.StatusHTML(clear_after=15)
        ipw.dlink(
            (self.resource_widget, "message"),
            (self.setup_message, "message"),
        )

        self.source.value = "https://raw.githubusercontent.com/stfc/alc-ux/refs/heads/main/resources/remotes.json"

        children = [
            ipw.HTML("<hr>"),
            self.source,
            ipw.HTML("<hr>"),
            self.resource_widget,
            self.setup_message,
        ]
        super().__init__(children=children, **kwargs)
        return

    @observe("_database_source")
    def _update_database_source(self, _):
        self.resource_widget.comp_resources_database.database_source = (
            self._database_source
        )
        return
