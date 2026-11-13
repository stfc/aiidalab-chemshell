"""Defines the model and view for the resource setup stage."""

import aiidalab_widgets_base as awb
import ipywidgets as ipw
import traitlets as tl
from alc_aiidalab_widgets.widgets import CodeSelector

from aiidalab_chemshell.common.utils import (
    add_button_style_class,
    chemshell_button_style,
)
from aiidalab_chemshell.models.resources import ComputationalResourcesModel
from aiidalab_chemshell.utils import test_aiida_chemsh_import


class ComputationalResourcesWizardStep(ipw.VBox, awb.WizardAppWidgetStep):
    """Main view for the resource setup stage."""

    def __init__(self, model: ComputationalResourcesModel, **kwargs):
        """
        ComputationalResourcesWizardStep constructor.

        Parameters
        ----------
        **kwargs :
            Keyword arguments passed to the parent class's constructor.
        """
        super().__init__(children=[], **kwargs)
        self.model = model
        self.rendered = False

        self.header = ipw.HTML(
            """
            <h3> Computational Resources Setup </h3>
            """,
            layout={"margin": "auto"},
        )
        self.chemsh_installed = test_aiida_chemsh_import()
        self.chemsh_warning = ipw.HTML("", layout={"margin": "auto"})

        self.guide = ipw.HTML(
            self.model.default_guide,
        )

        self.submit_btn = ipw.Button(
            description="Submit",
            button_style="success",
            tooltip="Submit the calculation",
            icon="check",
            layout={"width": "60%", "height": "30px", "margin": "20px auto 8px"},
        )
        self.submit_btn.on_click(self._submit)
        add_button_style_class(self.submit_btn)

        self.children = [
            chemshell_button_style(),
            # self.header,
            self.guide,
            self.chemsh_warning if not self.chemsh_installed else ipw.HTML(""),
            ResourceSetupBox(model=self.model),
            self.submit_btn,
        ]
        return

    def render(self):
        """Render the wizard's contents if not already rendered."""
        if self.rendered:
            return
        self._refresh_widget()
        self.rendered = True
        return

    def _submit(self, _=None) -> None:
        """Handle the submission of the AiiDA process."""
        if self.model.validate():
            self.model.submitted = True
            self.submit_btn.disabled = True
            self.submit_btn.description = "Submitted"
            # Mark the (collapsed) step as complete via the AWB wizard icon.
            self.state = self.State.SUCCESS
        else:
            print("ERROR: Input Validation Failed")
        return

    def _refresh_widget(self) -> None:
        """Refresh the widget's contents."""
        self.chemsh_installed = test_aiida_chemsh_import()
        if not self.chemsh_installed:
            self.submit_btn.disabled = True
            self.chemsh_warning.value = (
                "<p style='color:red;'>"
                "The aiida-chemshell plugin is not installed. Please install it "
                "to proceed."
                "</p>"
            )
        else:
            self.chemsh_warning.value = ""
            self.submit_btn.disabled = False


class ResourceSetupBox(ipw.VBox):
    """A box widget for defining computational resources."""

    def __init__(self, model: ComputationalResourcesModel, **kwargs):
        """
        ResourceSetupBox constructor.

        Parameters
        ----------
        **kwargs :
            Keyword arguments passed to the parent class's constructor.
        """
        super().__init__(layout={"margin": "auto", "width": "80%"}, **kwargs)
        self.model = model

        self.code_selector = CodeSelector(
            model=self.model,
            code_name="chemsh",
            description="Code:",
            show_mpi=True,
        )
        # Match the width/description-label styling used by the sibling fields
        # below so the inputs line up (CodeSelector hardcodes its own layout,
        # so these must be overridden after construction).
        self.code_selector.layout.width = "80%"
        self.code_selector.code.style.description_width = "100px"

        self.label = ipw.Text(
            value=self.model.process_label,
            placeholder="Enter process label",
            description="Label:",
            disabled=False,
            style={"description_width": "100px"},
            layout=ipw.Layout(width="80%"),
        )
        tl.link((self.label, "value"), (self.model, "process_label"))

        self.description = ipw.Textarea(
            value=self.model.process_description,
            placeholder="Enter process description",
            description="Description:",
            disabled=False,
            style={"description_width": "100px"},
            layout=ipw.Layout(width="80%", height="120px"),
        )
        tl.link((self.description, "value"), (self.model, "process_description"))

        self.children = [
            chemshell_button_style(),
            self.code_selector,
            self.label,
            self.description,
        ]
