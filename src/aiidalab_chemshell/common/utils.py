"""Small common widgets used accross the application."""

import ipywidgets as ipw

#: CSS class applied to buttons that should use the sleek/modern styling.
CHEMSHELL_BUTTON_CLASS = "chemshell-sleek-btn"

#: Stylesheet injected once to give ``CHEMSHELL_BUTTON_CLASS`` buttons rounded
#: corners, a subtle shadow and a hover lift. ``!important`` is required to win
#: over the default ipywidgets/Jupyter button rules.
_CHEMSHELL_BUTTON_STYLE = f"""
<style>
.{CHEMSHELL_BUTTON_CLASS} {{
    border-radius: 10px !important;
    border: none !important;
    font-weight: 600 !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.15);
    transition: transform 0.08s ease, box-shadow 0.15s ease;
}}
.{CHEMSHELL_BUTTON_CLASS}:hover {{
    transform: translateY(-1px);
    box-shadow: 0 3px 8px rgba(0, 0, 0, 0.22);
}}
.{CHEMSHELL_BUTTON_CLASS}:active {{
    transform: translateY(0);
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}}
</style>
"""


def chemshell_button_style():
    """Return an ``HTML`` widget carrying the sleek button stylesheet.

    Include the returned widget once in a layout that contains buttons styled
    via :func:`sleek_buttons`. The ``<style>`` block is global to the page, so a
    single instance is enough even if it appears multiple times.

    Returns
    -------
    ipywidgets.HTML
        A zero-height widget holding the stylesheet.
    """
    return ipw.HTML(value=_CHEMSHELL_BUTTON_STYLE, layout=ipw.Layout(display="none"))


def add_button_style_class(*buttons):
    """Apply the sleek styling class to one or more buttons.

    Note that the accompanying stylesheet from :func:`sleek_button_style` must
    also be present in the rendered layout for the styling to take effect.

    Parameters
    ----------
    *buttons : ipywidgets.Button
        Buttons to receive the :data:`CHEMSHELL_BUTTON_CLASS` CSS class.
    """
    for button in buttons:
        button.add_class(CHEMSHELL_BUTTON_CLASS)


class LoadingWidget(ipw.HBox):
    """Widget for displaying a loading spinner."""

    def __init__(self, message="Loading", **kwargs):
        super().__init__(
            children=[
                ipw.Label(message),
                ipw.HTML(
                    value="<i class='fa fa-spinner fa-spin fa-2x fa-fw'/>",
                    layout=ipw.Layout(margin="12px 0 6px"),
                ),
            ],
            layout=ipw.Layout(
                justify_content="center",
                align_items="center",
                **kwargs.pop("layout", {}),
            ),
            **kwargs,
        )
        self.add_class("loading")
