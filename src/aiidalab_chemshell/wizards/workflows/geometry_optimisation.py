"""Defines the input widget for the base geometry optimisation workflow."""

from importlib.util import find_spec

import ipywidgets as ipw
from traitlets import link

from aiidalab_chemshell.common.chemshell import BasisSetOptions
from aiidalab_chemshell.common.file_handling import FileUploadWidget
from aiidalab_chemshell.models.workflow import ChemShellWorkflowModel


class ChemShellOptionsWidget(ipw.VBox):
    """Widget for selecting the ChemShell input options."""

    def __init__(self, model: ChemShellWorkflowModel, **kwargs):
        """
        ChemShellOptionsWidget constructor.

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
            <h3> QM/MM Geometry Optimisation </h3>
            """,
            layout={"margin": "auto"},
        )
        self.guide = ipw.HTML(
            """
            <p>
                Perform a geometry optimisation on the given structure via either QM or
                QM/MM. Uses NWChem for the QM region and DL_POLY for the (optional) MM
                region. The quality of the calculation can be controlled via the basis
                set option, higher quality basis set will result in a more accurate QM
                calculation but will increase the time required.
            </p>
            """
        )

        # Force Field File
        self.ff_file = FileUploadWidget(description="Force Field:")
        self.ff_file.disable(True)

        self.h_line = ipw.HTML("<hr>")

        return

    def _get_qm_theory_options(self) -> list[str]:
        """Get the available QM theory options."""
        try:
            from aiida_chemshell.utils import ChemShellQMTheory

            return list(ChemShellQMTheory.__members__.keys())
        except ImportError:
            return []
        except Exception as e:
            raise e

    def _get_mm_theory_options(self) -> list[str]:
        """Get the available MM theory options."""
        try:
            from aiida_chemshell.utils import ChemShellMMTheory

            return list(ChemShellMMTheory.__members__.keys())
        except ImportError:
            return []
        except Exception as e:
            raise e

    def _enable_mm_options(self, _) -> None:
        # self.mm_theory_dropdown.disabled = not self.enable_mm_chk.value
        self.qm_region_text.disabled = not self.enable_mm_chk.value
        self.ff_file.disable(not self.enable_mm_chk.value)
        return

    # def _update_basis_quality(self, _) -> None:
    #     print(self.model.basis_quality)
    #     return

    def render(self):
        """Render the options widget contents if not already rendered."""
        if self.rendered:
            return

        # Basis Quality
        self.qm_basis_dropdown = ipw.Dropdown(
            options={e.name: e for e in BasisSetOptions},
            description="Basis Quality:",
            disabled=False,
            layout={"width": "50%"},
        )
        link((self.model, "basis_quality"), (self.qm_basis_dropdown, "value"))

        # Enable vibrational analysis
        self.enable_vib = ipw.Checkbox(
            value=True, description="Calculate Vibrational Frequencies", index=True
        )
        ipw.dlink((self.enable_vib, "value"), (self.model, "vibrational_analysis"))

        # DFT checkbox
        # self.enable_dft = ipw.Checkbox(value=False, description="Use DFT", index=True)
        # ipw.dlink((self.enable_dft, "value"), (self.model, "use_dft"))

        # QM/MM Checkbox
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
            disabled=True,
            layout={"width": "50%"},
        )

        children = [
            self.header,
            self.guide,
            self.qm_basis_dropdown,
            self.enable_vib,
            self.h_line,
            self.enable_mm_chk,
            self.qm_region_text,
            self.ff_file,
        ]

        if find_spec("aiida_mlip"):
            self.create_mlip_fine_tuning_options(children)

        self.children = children
        self.rendered = True
        return

    def disable(self, val: bool) -> None:
        """Disable the input fields."""
        for child in self.children:
            child.disabled = val
        self.ff_file.disable(val)
        return

    def create_mlip_fine_tuning_options(self, children: list) -> None:
        """Create optional inputs for enabling MLIP fine-tuning."""
        self.use_mlip_ft = ipw.Checkbox(
            value=False, description="Fine-Tune MLIP Model", index=True
        )
        self.mlip_model = FileUploadWidget(description="MLIP Model:")
        children.append(self.h_line)
        children.append(self.use_mlip_ft)
        children.append(self.mlip_model)
        return
