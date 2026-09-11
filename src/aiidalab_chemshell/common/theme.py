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

#: Design tokens. Tweak these to retune the whole app. Dark-mode overrides live
#: in the ``@media (prefers-color-scheme: dark)`` block below.
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

    /* Typography */
    --cs-font: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
        Helvetica, Arial, sans-serif;

    /* Palette (light) */
    --cs-accent: #2e7d32;
    --cs-accent-contrast: #ffffff;
    --cs-surface: #ffffff;
    --cs-surface-muted: #f5f6f8;
    --cs-border: #e2e5ea;
    --cs-text: #1f2933;
    --cs-text-muted: #6b7280;
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

#: Dark-mode overrides. Only the palette tokens change; every rule above follows
#: automatically. Fill in / adjust as the dark palette is finalised.
_DARK = """
@media (prefers-color-scheme: dark) {
    :root {
        --cs-accent: #66bb6a;
        --cs-accent-contrast: #0b0f0c;
        --cs-surface: #1e2228;
        --cs-surface-muted: #171a1f;
        --cs-border: #333a44;
        --cs-text: #e6e8eb;
        --cs-text-muted: #9aa3af;
        --cs-shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.5);
        --cs-shadow-md: 0 3px 8px rgba(0, 0, 0, 0.6);
    }
}
"""

_THEME = f"""
<style>
{_TOKENS}
{_BUTTONS}
{_CARDS}
{_INPUTS}
{_CHROME}
{_DARK}
</style>
"""


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
