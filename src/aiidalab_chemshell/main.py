"""Defines the AiiDAlab application pages (new calculation and batch processing)."""

from datetime import datetime

import ipywidgets as ipw
from IPython.display import display

from aiidalab_chemshell.common.navigation import QuickAccessButtons
from aiidalab_chemshell.common.theme import (
    APP_ROOT_CLASS,
    chemshell_appbar,
    chemshell_theme,
)
from aiidalab_chemshell.process import BatchAppModel, MainAppModel
from aiidalab_chemshell.wizards.main_app import BatchWizardWidget, MainWizardWidget


class App:
    """
    An AiiDAlab ChemShell application page.

    A single application shell shared by the "New Calculation" and
    "Batch Processing" pages. The ``batch`` flag selects the underlying model,
    wizard, and subtitle while keeping the surrounding layout/styling identical.
    """

    def __init__(self, batch: bool = False):
        """
        App constructor.

        Parameters
        ----------
        batch : bool
            If True, build the batch processing page; otherwise build the main
            "New Calculation" page.
        """
        if batch:
            self.model = BatchAppModel()
            wizard = BatchWizardWidget(self.model)
            subtitle = "ChemShell Batch Processing Workflow"
        else:
            self.model = MainAppModel()
            wizard = MainWizardWidget(self.model)
            subtitle = "Welcome to the ALC's AiiDAlab ChemShell App"

        self.view = AppView(wizard, subtitle)
        display(self.view)


class MainApp(App):
    """The main "New Calculation" AiiDAlab application page."""

    def __init__(self):
        """MainApp constructor."""
        super().__init__(batch=False)


class BatchApp(App):
    """The batch processing AiiDAlab application page."""

    def __init__(self):
        """BatchApp constructor."""
        super().__init__(batch=True)


class AppView(ipw.VBox):
    """The shared application view (header, navigation, body wizard, footer)."""

    def __init__(self, wizard: ipw.Widget, subtitle: str, **kwargs):
        """
        AppView constructor.

        Parameters
        ----------
        wizard : ipw.Widget
            The wizard widget rendered as the page body.
        subtitle : str
            The page subtitle displayed beneath the logo.
        **kwargs :
            Keyword arguments passed to the parent class's constructor.
        """
        logo = ipw.HTML(
            """
            <div class="app-container logo" style="width: 500px;">
                <img src="../images/chemshell.png" alt="ChemShell Logo" />
            </div>
            """,
            layout={"margin": "auto"},
        )

        subtitle_widget = ipw.HTML(
            f"""
            <h2 id='subtitle' style="text-align: center;">{subtitle}</h2>
            """
        )

        nav_btns = QuickAccessButtons()

        header = chemshell_appbar([logo, nav_btns])

        footer = ipw.HTML(
            f"""
            <footer>
                Copyright (c) {datetime.now().year} Ada Lovelace Centre
                (STFC) <br>
            </footer>
            """,
            layout={"align-content": "right"},
        )

        self.main = wizard

        super().__init__(
            layout={},
            children=[chemshell_theme(), header, subtitle_widget, self.main, footer],
            **kwargs,
        )
        self.add_class(APP_ROOT_CLASS)
