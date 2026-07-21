"""Defines the input widget for the a base single point energy calculation."""

import ipywidgets as ipw
from aiida_chemshell.utils import ChemShellQMTheory
from alc_aiidalab_widgets.widgets import FileUploadWidget
from traitlets import Bool, HasTraits, link

from aiidalab_chemshell.common.chemshell import BasisSetOptions
from aiidalab_chemshell.common.utils import LoadingWidget
from aiidalab_chemshell.models.workflow import ChemShellWorkflowModel


class SinglePointCalcWidget(ipw.VBox):
    """Widget for specifying ChemShell SP calculation inputs."""

    def __init__(self, model: ChemShellWorkflowModel, **kwargs):
        """
        SinglePointCalcWidget constructor.

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
        self.header = ipw.HTML(
            """
            <h3 style="text-align: center;">Single Point Energy Calculation</h3>
            <p>
                Perform a single point calculation on a given input structure.
                Optionally a vibrational frequency calculation can be performed
                instead, again based on the given input structure.
            </p>
            """,
            # layout={"margin": "auto"},
        )
        self.children = [self.header, LoadingWidget()]
        return

    def render(self) -> None:
        """Render the widget."""
        if self.rendered:
            return
        self.rendered = True

        self.advanced_options = ipw.Checkbox(
            value=False, description="Show Advanced Options", index=True
        )
        self.advanced_options.observe(self._render_input_options, "value")

        self.basis_dropdown = ipw.Dropdown(
            options={e.name: e for e in BasisSetOptions},
            description="Basis Quality:",
            disabled=False,
            layout={"width": "50%"},
        )
        self.basis_dropdown.observe(self._update_basis_set, "value")
        self.basis_dropdown.index = 1

        self.basis_string = ipw.Text(
            value="",
            description="Basis Set:",
            disabled=False,
            layout={"width": "50%"},
        )
        link((self.model, "basis_set"), (self.basis_string, "value"))
        self.backend = ipw.Dropdown(
            options={e.name: e for e in ChemShellQMTheory},
            description="QM Backend:",
            disabled=False,
            layout={"width": "50%"},
        )
        link((self.model, "qm_theory"), (self.backend, "value"))
        self.functional = ipw.Text(
            value="B3LYP",
            description="Functional:",
            disabled=False,
            layout={"width": "50%"},
        )
        link((self.model, "functional"), (self.functional, "value"))

        self.derivatives = DerivativeOptions(self.model)

        self.enable_vib = ipw.Checkbox(
            value=False, description="Vibrational Frequencies", index=True
        )
        ipw.dlink((self.enable_vib, "value"), (self.model, "vibrational_analysis"))

        self.enable_mm_chk = ipw.Checkbox(
            value=False, description="Use QM/MM", indent=True
        )
        self.enable_mm_chk.observe(self._enable_mm_options, "value")
        ipw.dlink((self.enable_mm_chk, "value"), (self.model, "use_mm"))

        # MM Backend
        # self.mm_theory_dropdown = ipw.Dropdown(
        #     options=self._get_mm_theory_options(),
        #     description="MM Theory:",
        #     disabled=True,
        #     layout={"width": "50%"},
        # )

        # QM region for QM/MM calculation
        self.qm_region_text = ipw.Text(
            value="",
            description="QM Region:",
            disabled=False,
            layout={"width": "50%"},
        )
        link((self.qm_region_text, "value"), (self.model, "qm_region"))

        # Force Field File
        self.ff_file = FileUploadWidget(description="Force Field:")
        link((self.ff_file, "file"), (self.model, "force_field"))

        self._render_basic_options()

    def _render_basic_options(self) -> None:
        """Render the simplified input options view."""
        children = [
            self.header,
            self.advanced_options,
            self.basis_dropdown,
            self.enable_vib,
            self.derivatives,
            self.enable_mm_chk,
        ]
        if self.enable_mm_chk.value:
            children.append(self.qm_region_text)
            children.append(self.ff_file)
        self.children = children
        return

    def _render_advanced_options(self) -> None:
        """Render the advanced input options view."""
        children = [
            self.header,
            self.advanced_options,
            self.backend,
            self.basis_string,
            self.functional,
            self.enable_vib,
            self.derivatives,
            self.enable_mm_chk,
        ]
        if self.enable_mm_chk.value:
            children.append(self.qm_region_text)
            children.append(self.ff_file)
        self.children = children
        return

    def _render_input_options(self, change: dict) -> None:
        """Switch between basic and advanced views."""
        if change["new"]:
            self._render_advanced_options()
        else:
            self._render_basic_options()
            # Update the linked basis set value
            self._update_basis_set({"new": self.basis_dropdown.value, "old": None})
        return

    def _update_basis_set(self, change: dict) -> None:
        """Update the basis set based of the simplified input options."""
        if change["new"] == change["old"]:
            return
        self.model.basis_set = change["new"].label
        return

    def disable(self, disable: bool = True) -> None:
        """Disable/Enable the wigets input options."""
        for child in self.children:
            child.disabled = disable
        return

    def _enable_mm_options(self, _) -> None:
        self._render_input_options({"new": self.advanced_options.value})
        return


class DerivativeOptions(ipw.HBox, HasTraits):
    """Inline derivative checkboxes."""

    disabled = Bool(False).tag(sync=True)

    def __init__(self, model: ChemShellWorkflowModel, **kwargs):
        """
        DerivativeOptions constructor.

        Parameters
        ----------
        model : ChemShellWorkflowModel
            The model that defines the data related to this step in the setup wizard.
        **kwargs :
            Keyword arguments passed to the parent class's constructor.
        """
        super().__init__(**kwargs)
        self.model = model
        self.label = ipw.HTML(
            "<p>Energy Derivatives: </p>",
        )
        self.first = ipw.Checkbox(value=True, description="First Derivative")
        self.second = ipw.Checkbox(value=False, description="Second Derivative")
        link((self.first, "value"), (self.model, "gradients"))
        link((self.second, "value"), (self.model, "hessian"))

        self.observe(self.disable, "disabled")

        self.children = [self.label, self.first, self.second]

    def disable(self, change: dict) -> None:
        """Disable the contained widgets."""
        for child in self.children:
            child.disabled = change["new"]
        return
