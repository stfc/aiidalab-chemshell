"""Widget for selecting a force field file from various sources."""

import ipywidgets as ipw
from aiida.orm import SinglefileData
from alc_aiidalab_widgets.widgets import AiiDADatabaseQueryWidget, FileUploadWidget
from traitlets import HasTraits, Instance


class ForceFieldSelectionWidget(ipw.VBox, HasTraits):
    """Widget for selecting a force field file from various sources."""

    force_field = Instance(SinglefileData, allow_none=True)

    def __init__(self, **kwargs):
        """
        ForceFieldSelectionWidget constructor.

        Parameters
        ----------
        **kwargs :
            Keyword arguments passed to the parent class's constructor.
        """
        super().__init__(**kwargs)

        # Upload a new file.
        self.file_uploader = FileUploadWidget(description="Force Field: ")
        ipw.dlink((self.file_uploader, "file"), (self, "force_field"))

        # Pick an existing SinglefileData node from the AiiDA database.
        self.database_widget = AiiDADatabaseQueryWidget(
            title="AiiDA Database",
            query=[SinglefileData],
        )
        self.database_widget.observe(self._on_database_search, "data_object")

        self.tabs = ipw.Tab()
        self.tabs.children = [self.file_uploader, self.database_widget]
        self.tabs.set_title(0, "Upload File")
        self.tabs.set_title(1, "AiiDA Database")

        self.status = ipw.HTML("<p>No force field file selected.</p>")

        self.observe(self._update_status, "force_field")

        self.children = [self.status, self.tabs]
        return

    def _on_database_search(self, change: dict) -> None:
        """
        Handle a force field file being selected from the AiiDA database.

        Parameters
        ----------
        change : dict
            A traitlets change dictionary for the database widget's
            ``data_object`` trait.
        """
        if change["new"] == change["old"]:
            return
        self.force_field = change["new"]
        return

    def _update_status(self, change: dict) -> None:
        """
        Reflect the currently selected force field file in the status area.

        Parameters
        ----------
        change : dict
            A traitlets change dictionary for this widget's ``force_field``
            trait.
        """
        node = change["new"]
        if node is None:
            self.status.value = "<p>No force field file selected.</p>"
        else:
            self.status.value = f"<p>Force field file: <code>{node.filename}</code></p>"
        return

    def disable(self, val: bool = True) -> None:
        """
        Disable the widget and all of its children.

        Parameters
        ----------
        val : bool
            Whether to disable (``True``) or re-enable (``False``) the
            widget's inputs.
        """
        for child in self.tabs.children:
            try:
                child.disable(val)
            except AttributeError:
                pass
        return
