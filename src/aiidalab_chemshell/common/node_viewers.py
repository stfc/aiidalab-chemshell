"""Defines a custom AiiDA node visualiser."""

from pathlib import Path
from tempfile import NamedTemporaryFile

import ase
from aiida.orm import ArrayData, Node, ProcessNode, SinglefileData, StructureData
from aiidalab_widgets_base.loaders import LoadingWidget
from aiidalab_widgets_base.viewers import AIIDA_VIEWER_MAPPING
from IPython.display import clear_output, display
from ipywidgets import HTML, DOMWidget, Dropdown, Output, VBox
from traitlets import Instance, observe


class CustomAiidaNodeViewWidget(VBox):
    """
    Custom viewer based on a specific AiiDA node type.

    An extension of the aiida_widgets_base.viewers.AiidaNodeViewWidget
    enabling more customisability when registering viewers with nodes
    returned from ChemShell jobs. The main outline is taken from the base
    aiidalab_widgets_base viewer with an extended viewer() method which
    allows handling of node types which the base viewer has no registered
    visualisation widgets.
    """

    node = Instance(Node, allow_none=True)

    def __init__(self, **kwargs):
        """CustomAiidaNodeViewWidget Constructor."""
        self._output = Output()
        self.node_views = {}
        self.node_view_loading_message = LoadingWidget("Loading Node View")
        super().__init__(**kwargs)
        self.add_class("aiida-node-view-widget")

    @observe("node")
    def _observe_node(self, change):
        if not ((node := change["new"]) and node != change["old"]):
            return
        if node.uuid in self.node_views:
            self.children = [self.node_views[node.uuid]]
            return
        self.children = [self.node_view_loading_message]
        node_view = self._viewer(node)
        if isinstance(node_view, DOMWidget):
            self.node_views[node.uuid] = node_view
            self.children = [node_view]
        else:
            with self._output:
                clear_output()
                if change["new"]:
                    display(node_view)
            self.children = [self._output]

    def _viewer(self, node: Node, **kwargs):
        """Create a viewer based on the type of Node being visualised."""
        _viewer = AIIDA_VIEWER_MAPPING.get(node.node_type)
        if isinstance(node, ProcessNode):
            # Allow to register specific viewers based on node.process_type
            _viewer = AIIDA_VIEWER_MAPPING.get(node.process_type, _viewer)

        if _viewer:
            return _viewer(node, **kwargs)

        # Handle custom ChemShell specific visualisation
        if isinstance(node, SinglefileData):
            # Singlefile data output generally refers to a structure file
            # output from ChemShell jobs
            structure = self._get_structure_data_object_from_file(
                node.filename, node.content
            )
            if structure:
                _viewer = AIIDA_VIEWER_MAPPING.get(structure.node_type)
                if _viewer:
                    return _viewer(structure, **kwargs)

        if isinstance(node, ArrayData):
            return AiidaArrayDataViewWidget(node, **kwargs)
        # No viewer registered for this type, return node itself
        return node

    def _get_structure_data_object_from_file(
        self, fname: str, content: bytes
    ) -> StructureData | None:
        """
        Create an ase strucure object from a structure file.

        Parameters
        ----------
        fname   : str
            The file name the structure is being read from.
        content : bytes
            The content of the structure file byte encoded.

        Return
        ------
        structure : ase.Atoms | None
            The ASE atomic structure object or None if the file could not be read.
        """
        suffix = "".join(Path(fname).suffixes)
        with NamedTemporaryFile(suffix=suffix) as tmpf:
            tmpf.write(content)
            tmpf.flush()
            try:
                structure = ase.io.read(tmpf.name, index=":")[0]
            except (KeyError, ase.io.formats.UnknownFileTypeError):
                node = None
            else:
                # ASE doesn't correctly interpret atomic units so convert all units to
                # angstrom
                for i in range(len(structure)):
                    structure.positions[i] = structure.positions[i] * 0.529177
                node = StructureData()
                node.set_ase(structure)
        return node


class AiidaArrayDataViewWidget(VBox):
    """Custom widget to display array data produced from ChemShell jobs."""

    def __init__(self, array: ArrayData, **kwargs):
        """AiidaArrayDataViewWidget Constructor.

        Parameters
        ----------
        array : ArrayData
            The AiiDA ArrayData object to display.
        """
        super().__init__(**kwargs)
        self.array = array
        self.array_names = array.get_arraynames()

        self.array_selector = Dropdown(
            options=self.array_names,
            description="Array Label:",
            disabled=False,
            layout={"width": "30%"},
        )
        self._render_array({"new": self.array_selector.index, "old": -1})
        self.array_selector.observe(self._render_array, "index")

        return

    def _render_array(self, change) -> None:
        """Create a HTML table based on the currently selected array."""
        index = change["new"]
        if index == change["old"]:
            return
        values = self.array.get_array(self.array_names[index])
        # Construct HTML Table
        html = "<table style='width:100%; border: 1px solid #ddd; text-align: left; "
        html += "border-collapse: collapse;'>"
        html += "<tr style='background-color: #2196F3; color: white;'>"
        html += "<th>Atom Index</th><th>X</th><th>Y</th><th>Z</th></tr>"

        for idx, row in enumerate(values):
            bg_color = "#f9f9f9" if idx % 2 == 0 else "#ffffff"
            html += f"<tr style='background-color: {bg_color};'>"
            html += f"<td><b>{idx}</b></td><td>{row[0]:.6f}</td><td>{row[1]:.6f}</td>"
            html += f"<td>{row[2]:.6f}</td>"
            html += "</tr>"
        html += "</table>"

        self.children = [self.array_selector, HTML(html)]
        return
