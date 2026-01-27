"""Defines the main AiiDAlab application page."""

from datetime import datetime

import ipywidgets as ipw
from IPython.display import display

from aiidalab_chemshell.common.navigation import QuickAccessButtons
from aiidalab_chemshell.process import MainAppModel
from aiidalab_chemshell.wizards.main_app import MainAppWizardWidget


class MainApp:
    """The main AiiDAlab application class."""

    def __init__(self):
        """MainApp constructor."""
        self.model = MainAppModel()
        self.view = MainAppView(self.model)
        display(self.view)

    # def load(self) -> None:
    #     return


class MainAppView(ipw.VBox):
    """The main app view."""

    def __init__(self, model: MainAppModel, **kwargs):
        """MainAppView constructor."""
        logo = ipw.HTML(
            """
            <div class="app-container logo" style="width: 300px;">
                <img src="../images/alc.svg" alt="ALC AiiDAlab App Logo" />
            </div>
            """,
            layout={"margin": "auto"},
        )

        subtitle = ipw.HTML(
            """
            <h2 id='subtitle'>Welcome to the ALC's AiiDAlab ChemShell App</h2>
            """
        )

        nav_btns = QuickAccessButtons()

        header = ipw.VBox(
            children=[
                logo,
                subtitle,
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

        self.main = MainAppWizardWidget(model)

        super().__init__(
            layout={}, children=[header, nav_btns, self.main, footer], **kwargs
        )
