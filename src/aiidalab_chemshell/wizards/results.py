"""Module for defining widgets/models for viewing process progress and results."""

from pathlib import Path
from tempfile import NamedTemporaryFile

import aiidalab_widgets_base as awb
import ase
import ipywidgets as ipw
from aiida.orm import ProcessNode
from plumpy import ProcessState

from aiidalab_chemshell.common.chemshell import WorkflowOptions
from aiidalab_chemshell.models.results import ResultsModel


class ResultsWizardStep(ipw.VBox, awb.WizardAppWidgetStep):
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
            self.node_tree = awb.ProcessNodesTreeWidget()
            ipw.dlink((self.model, "process_uuid"), (self.node_tree, "value"))
            self.node_view = awb.viewers.AiidaNodeViewWidget()
            ipw.dlink(
                (self.node_tree, "selected_nodes"),
                (self.node_view, "node"),
                transform=lambda nodes: nodes[0] if nodes else None,
            )

            self.workflow_results = WorkflowResultsWidget(
                self.model.workflow, self.model.process
            )

            self.children = [
                self.info,
                self.node_tree,
                self.node_view,
                self.update_btn,
                self.workflow_results,
            ]
            self.rendered = True
        return

    def _refresh_info(self, _) -> None:
        """Refresh the process information."""
        self.node_tree.update()
        self.workflow_results.render()
        return


class WorkflowResultsWidget(ipw.VBox):
    """Widget for visualising workflow specific result."""

    def __init__(self, workflow: WorkflowOptions, process: ProcessNode, **kwargs):
        """
        WorkflowResultsWidget Class Constructor.

        Parameters
        ----------
        workflow  : WorkflowOptions
            An enum specifying which process

        """
        super().__init__(**kwargs)
        self.rendered = False
        self.workflow = workflow
        self.process = process
        self.title = self._get_workflow_title(self.workflow)
        self.render()

        return

    def render(self) -> None:
        """Render the widgets contents."""
        if not self.rendered:
            match self.process.process_state:
                case ProcessState.FINISHED:
                    self._build_widget()
                    self.rendered = True
                case _:
                    msg = ipw.HTML(
                        """
                        <p>
                            Awaiting Process Results ...
                        </p>
                        """
                    )
                    self.children = [self.title, msg]
        return

    def _build_widget(self) -> None:
        """Build a workflow specific results visualiser widget."""
        children = [
            self.title,
        ]

        match self.workflow:
            case WorkflowOptions.GEOMETRY:
                structure_file = self.process.outputs["optimised_structure"]
                structure = self._get_ase_object_from_file(
                    structure_file.filename, structure_file.content
                )
                if structure:
                    viewer = awb.viewers.StructureDataViewer(structure=structure)
                else:
                    viewer = ipw.HTML(
                        "<p>ERROR :: Could not visualise structure from file ...</p>"
                    )
                children.append(viewer)
            case _:
                msg = ipw.HTML(
                    """
                    <p>
                        Process has no visual results ...
                    </p>
                    """
                )
                children.append(msg)

        self.children = children
        return

    def _get_workflow_title(self, workflow: WorkflowOptions) -> ipw.HTML:
        """Return a title for the workflow specific results visualiser widget."""
        match workflow:
            case WorkflowOptions.GEOMETRY:
                return ipw.HTML(
                    """
                    <h3>
                        Optimised Geometry
                    </h3>
                    """
                )
            case _:
                return ipw.HTML("")

    def _get_ase_object_from_file(self, fname: str, content: bytes) -> ase.Atoms | None:
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
                structure = None
        return structure
