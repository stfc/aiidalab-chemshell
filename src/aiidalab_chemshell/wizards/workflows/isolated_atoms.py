"""Defines the input widget for the Isolated Atomic Energy workflow."""

from aiida_chemshell.utils import ChemShellQMTheory
from ipywidgets import HTML, Checkbox, Dropdown, Text, VBox
from traitlets import link

from aiidalab_chemshell.common.chemshell import BasisSetOptions
from aiidalab_chemshell.common.utils import LoadingWidget
from aiidalab_chemshell.models.workflow import ChemShellWorkflowModel


class IsolatedAtomEnergyWidget(VBox):
    """Widget for selecting ChemShell input options."""

    def __init__(self, model: ChemShellWorkflowModel, **kwargs):
        """
        IsolatedAtomEnergyWidget constructor.

        Parameters
        ----------
        model : ChemShellWorkflowModel
            The model that defines the data related to this step in the setup wizard.
        **kwargs :
            Keyword arguments passed to the parent class's constructor.
        """
        super().__init__(**kwargs)
        self.model = model
        self.rendered = False
        self.header = HTML(
            """
            <h3> Isolated Atomic Energy Calculation </h3>
            <p>
                Extract all unique atom types from a given input structure and calculate
                their isolated QM energy.
            </p>
            """
        )
        self.children = [self.header, LoadingWidget()]
        return

    def render(self) -> None:
        """Render the widget."""
        if self.rendered:
            return
        self.rendered = True

        self.advanced_options = Checkbox(
            value=False, description="Show Advanced Options", index=True
        )
        self.advanced_options.observe(self._render_input_options, "value")

        self.basis_dropdown = Dropdown(
            options={e.name: e for e in BasisSetOptions},
            description="Basis Quality:",
            disabled=False,
            layout={"width": "50%"},
        )
        self.basis_dropdown.index = 1
        self.basis_dropdown.observe(self._update_basis_set, "value")
        # link((self.model, "basis_quality"), (self.basis_dropdown, "value"))

        self.basis_string = Text(
            value="",
            description="Basis Set:",
            disabled=False,
            layout={"width": "50%"},
        )
        link((self.model, "basis_set"), (self.basis_string, "value"))
        self.backend = Dropdown(
            options=list(ChemShellQMTheory.__members__.keys()),
            description="QM Backend:",
            disbled=False,
            layout={"width": "50%"},
        )
        self.functional = Text(
            value="B3LYP",
            description="Functional:",
            disabled=False,
            layout={"width": "50%"},
        )
        link((self.model, "functional"), (self.functional, "value"))

        self._render_basic_options()
        return

    def _render_basic_options(self) -> None:
        """Render the simplified input options view."""
        self.children = [
            self.header,
            self.advanced_options,
            self.basis_dropdown,
        ]
        return

    def _render_advanced_options(self) -> None:
        """Render the advanced input options view."""
        self.children = [
            self.header,
            self.advanced_options,
            self.backend,
            self.basis_string,
            self.functional,
        ]
        return

    def _render_input_options(self, change: dict) -> None:
        """Switch between basic and advanced views."""
        if change["new"]:
            self._render_advanced_options()
        else:
            self._render_basic_options()
        return

    def _update_basis_set(self, change: dict) -> None:
        """Update the basis set based of the simplified input options."""
        if change["new"] == change["old"]:
            return
        self.model.basis_set = change["new"].label
        return
