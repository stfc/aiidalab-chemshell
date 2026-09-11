"""Defines the main AiiDAlab app's start banner."""

import ipywidgets as ipw

from aiidalab_chemshell.common.navigation import QuickAccessButtons


def get_start_widget(appbase, jupbase, notebase):
    """Get the AiiDAlab app's start banner."""
    logo = ipw.HTML(
        f"""
        <div class="app-container" style="margin: auto;width: 600px;">
            <a class="logo" href="{appbase}/notebooks/main.ipynb" target="_blank">
            <img src="{appbase}/images/chemshell.png" alt="ChemShell Logo" />
            </a>
        </div>
        """
    )
    return ipw.VBox(
        children=[
            logo,
            QuickAccessButtons(),
        ]
    )
