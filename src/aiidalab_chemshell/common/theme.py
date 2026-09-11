"""Central visual theme for the AiiDAlab ChemShell application.

This module provides a single stylesheet, injected once at the application root,
that gives the app a consistent modern look. It is built on CSS custom
properties (design tokens) so the whole app can be retuned from one place, and
so that dark mode is a matter of overriding a handful of variables.

Usage
-----
Add :data:`APP_ROOT_CLASS` to the top-level application container and include the
widget returned by :func:`chemshell_theme` once among its children::

    view = ipw.VBox(children=[chemshell_theme(), header, body, footer])
    view.add_class(APP_ROOT_CLASS)

All rules are scoped under ``.{APP_ROOT_CLASS}`` so the theme does not leak into
other AiiDAlab apps sharing the same page. The design tokens live on ``:root``
(they are inert until referenced by a scoped rule).
"""

import ipywidgets as ipw

from aiidalab_chemshell.common.utils import CHEMSHELL_BUTTON_CLASS

#: CSS class applied to the top-level application container. All theme rules are
#: scoped under this class.
APP_ROOT_CLASS = "chemshell-app"

#: CSS class applied to the header "app bar" (logo, subtitle and quick-access
#: buttons). See :func:`chemshell_appbar`.
APPBAR_CLASS = "chemshell-appbar"

#: Design tokens. Tweak these to retune the whole app.
#:
#: Dark mode is handled in two layers (see :data:`_DARK`):
#:
#: 1. *Primary* — the neutral palette tokens inherit JupyterLab/Voila's own
#:    ``--jp-*`` theme variables. Jupyter swaps those values when the user
#:    changes theme, so the app automatically tracks the active Jupyter theme
#:    (light, dark, or custom) with no extra work.
#: 2. *Fallback* — each neutral references a ``*-fallback`` variable as the
#:    second ``var()`` argument, used only when Jupyter's tokens are absent.
#:    Those fallbacks are light by default and switched to dark by the OS
#:    ``prefers-color-scheme`` block in :data:`_DARK`.
#:
#: The ChemShell green accent is kept as a brand colour (not inherited from
#: Jupyter's brand blue); it and the shadows get dark-mode variants in both the
#: Jupyter-dark and OS-dark blocks.
_TOKENS = """
:root {
    /* Radii */
    --cs-radius: 10px;
    --cs-radius-lg: 16px;

    /* Elevation */
    --cs-shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.15);
    --cs-shadow-md: 0 3px 8px rgba(0, 0, 0, 0.22);

    /* Spacing rhythm */
    --cs-gap: 12px;
    --cs-pad: 20px;
    /* Vertical gap between wizard step cards. */
    --cs-step-gap: 4px;

    /* Typography. A native system-font stack: always available offline (no
       web font to download), using whatever high-quality UI font the user's
       OS already ships. */
    --cs-font: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen,
        Ubuntu, Cantarell, "Helvetica Neue", Arial, sans-serif;

    /* Brand accent (kept, not inherited from Jupyter). */
    --cs-accent: #2e7d32;
    --cs-accent-contrast: var(--jp-ui-inverse-font-color1, #ffffff);

    /* Neutral palette: inherit Jupyter's theme tokens, falling back to our own
       light values (which the OS-dark block flips to dark) when absent. */
    --cs-surface: var(--jp-layout-color1, var(--cs-surface-fallback));
    --cs-surface-muted: var(--jp-layout-color2, var(--cs-surface-muted-fallback));
    --cs-border: var(--jp-border-color1, var(--cs-border-fallback));
    --cs-text: var(--jp-ui-font-color1, var(--cs-text-fallback));
    --cs-text-muted: var(--jp-ui-font-color2, var(--cs-text-muted-fallback));

    /* Light fallbacks (used only when the --jp-* tokens above are undefined). */
    --cs-surface-fallback: #ffffff;
    --cs-surface-muted-fallback: #f5f6f8;
    --cs-border-fallback: #e2e5ea;
    --cs-text-fallback: #1f2933;
    --cs-text-muted-fallback: #6b7280;
}
"""

#: Sleek button styling, driven by the shared design tokens. ``!important`` is
#: required to win over the default ipywidgets/Jupyter button rules.
_BUTTONS = f"""
.{APP_ROOT_CLASS} .{CHEMSHELL_BUTTON_CLASS} {{
    box-sizing: border-box !important;
    border-radius: var(--cs-radius) !important;
    border: none !important;
    font-weight: 600 !important;
    box-shadow: var(--cs-shadow-sm);
    transition: transform 0.08s ease, box-shadow 0.15s ease;
}}
.{APP_ROOT_CLASS} .{CHEMSHELL_BUTTON_CLASS}:hover {{
    transform: translateY(-1px);
    box-shadow: var(--cs-shadow-md);
}}
.{APP_ROOT_CLASS} .{CHEMSHELL_BUTTON_CLASS}:active {{
    transform: translateY(0);
    box-shadow: var(--cs-shadow-sm);
}}
"""

#: Card treatment for the wizard steps. ``WizardAppWidget`` renders as an
#: accordion, so each step panel is styled as an elevated surface. Selectors
#: cover both the classic-notebook/Voila (``.widget-accordion``) and JupyterLab
#: (``.jupyter-widget-Accordion``) class names.
_CARDS = f"""
.{APP_ROOT_CLASS} .widget-accordion .p-Accordion-child,
.{APP_ROOT_CLASS} .widget-accordion .lm-Accordion-child,
.{APP_ROOT_CLASS} .jupyter-widget-Accordion .lm-Accordion-child {{
    background: var(--cs-surface);
    border: 1px solid var(--cs-border);
    border-radius: var(--cs-radius-lg);
    box-shadow: var(--cs-shadow-sm);
    margin-bottom: var(--cs-step-gap);
    overflow: hidden;
}}
.{APP_ROOT_CLASS} .widget-accordion .p-Accordion-child .p-Collapse-contents,
.{APP_ROOT_CLASS} .widget-accordion .lm-Accordion-child .lm-Collapse-contents,
.{APP_ROOT_CLASS} .jupyter-widget-Accordion .lm-Accordion-child .lm-Collapse-contents {{
    padding: var(--cs-pad);
}}
"""

#: Header "app bar": logo, subtitle and quick-access buttons on a muted surface
#: band, matching the wizard-step card treatment so the page top reads as a
#: distinct region.
_APPBAR = f"""
.{APP_ROOT_CLASS} .{APPBAR_CLASS} {{
    background: var(--cs-surface-muted);
    border: 1px solid var(--cs-border);
    border-radius: var(--cs-radius-lg);
    box-shadow: var(--cs-shadow-sm);
    padding: var(--cs-pad);
    margin-bottom: var(--cs-gap);
    align-items: center;
}}
"""

#: Consistent form-control styling with a visible focus ring for accessibility.
_INPUTS = f"""
.{APP_ROOT_CLASS} .widget-dropdown select,
.{APP_ROOT_CLASS} .widget-text input,
.{APP_ROOT_CLASS} .widget-text input[type="number"],
.{APP_ROOT_CLASS} .widget-int-text input,
.{APP_ROOT_CLASS} .widget-float-text input {{
    /* border-box keeps the added border/padding inside the fixed height and
       width ipywidgets assigns, so controls neither clip their text nor
       overflow fixed-size parents. */
    box-sizing: border-box !important;
    /* Pin every single-line control to the framework's standard inline height
       so text inputs match the dropdowns rather than collapsing to the
       browser's (thinner) default input height. */
    min-height: var(--jp-widgets-inline-height, 28px) !important;
    height: var(--jp-widgets-inline-height, 28px) !important;
    border-radius: var(--cs-radius) !important;
    border: 1px solid var(--cs-border) !important;
    padding: 0 8px !important;
    transition: border-color 0.12s ease, box-shadow 0.12s ease;
}}
.{APP_ROOT_CLASS} .widget-textarea textarea {{
    /* Multi-line control: fill the height set via the widget's Layout (falling
       back to the inline height) and stay user-resizable, rather than being
       pinned to a single line like the inputs above. */
    box-sizing: border-box !important;
    height: 100% !important;
    min-height: var(--jp-widgets-inline-height, 28px) !important;
    border-radius: var(--cs-radius) !important;
    border: 1px solid var(--cs-border) !important;
    padding: 6px 8px !important;
    resize: vertical;
    transition: border-color 0.12s ease, box-shadow 0.12s ease;
}}
.{APP_ROOT_CLASS} .widget-dropdown select:focus,
.{APP_ROOT_CLASS} .widget-text input:focus,
.{APP_ROOT_CLASS} .widget-textarea textarea:focus,
.{APP_ROOT_CLASS} .widget-int-text input:focus,
.{APP_ROOT_CLASS} .widget-float-text input:focus {{
    border-color: var(--cs-accent) !important;
    box-shadow: 0 0 0 2px rgba(46, 125, 50, 0.25) !important;
    outline: none !important;
}}
"""

#: Typography, header and footer polish.
_CHROME = f"""
.{APP_ROOT_CLASS} {{
    font-family: var(--cs-font);
    color: var(--cs-text);
}}
.{APP_ROOT_CLASS} .logo img {{
    max-width: 100%;
    height: auto;
}}
.{APP_ROOT_CLASS} #subtitle {{
    font-weight: 600;
    letter-spacing: 0.2px;
    margin: 8px 0 4px;
}}
.{APP_ROOT_CLASS} footer {{
    margin-top: var(--cs-pad);
    padding-top: var(--cs-gap);
    border-top: 1px solid var(--cs-border);
    color: var(--cs-text-muted);
    font-size: 0.85em;
    text-align: center;
}}
"""

#: Dark-mode overrides, layered.
#:
#: The neutral palette needs no override here: it inherits Jupyter's ``--jp-*``
#: tokens, which Jupyter itself flips to dark. These blocks only adjust the
#: things Jupyter does not provide — the brand accent (to a lighter, more
#: legible green on dark) and the shadows (deepened).
#:
#: * ``body[data-jp-theme-light="false"]`` fires when a Jupyter dark theme is
#:   active (primary trigger).
#: * ``@media (prefers-color-scheme: dark)`` additionally switches the neutral
#:   *fallbacks* to dark so the app still looks right when Jupyter's tokens are
#:   absent and the OS prefers dark (fallback trigger).
_DARK = """
body[data-jp-theme-light="false"] {
    --cs-accent: #66bb6a;
    --cs-shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.5);
    --cs-shadow-md: 0 3px 8px rgba(0, 0, 0, 0.6);
}
@media (prefers-color-scheme: dark) {
    :root {
        --cs-accent: #66bb6a;
        --cs-shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.5);
        --cs-shadow-md: 0 3px 8px rgba(0, 0, 0, 0.6);

        --cs-surface-fallback: #1e2228;
        --cs-surface-muted-fallback: #171a1f;
        --cs-border-fallback: #333a44;
        --cs-text-fallback: #e6e8eb;
        --cs-text-muted-fallback: #9aa3af;
    }
}
"""

_THEME = f"""
<style>
{_TOKENS}
{_BUTTONS}
{_CARDS}
{_APPBAR}
{_INPUTS}
{_CHROME}
{_DARK}
</style>
"""


def chemshell_appbar(children):
    """Return a header "app bar" ``VBox`` wrapping the given children.

    The returned box carries :data:`APPBAR_CLASS` and is styled as a muted
    surface band. Intended to hold the logo, subtitle and quick-access buttons
    at the top of a page.

    Parameters
    ----------
    children : list of ipywidgets.Widget
        Widgets to place inside the app bar (e.g. logo, subtitle, nav buttons).

    Returns
    -------
    ipywidgets.VBox
        The styled app-bar container.
    """
    bar = ipw.VBox(children=children, layout=ipw.Layout(margin="auto"))
    bar.add_class(APPBAR_CLASS)
    return bar


def chemshell_theme():
    """Return an ``HTML`` widget carrying the application theme stylesheet.

    Include the returned widget once among the children of the top-level
    application container, and apply :data:`APP_ROOT_CLASS` to that container.
    The ``<style>`` block is global to the page, so a single instance suffices.

    Returns
    -------
    ipywidgets.HTML
        A hidden widget holding the stylesheet.
    """
    return ipw.HTML(value=_THEME, layout=ipw.Layout(display="none"))
