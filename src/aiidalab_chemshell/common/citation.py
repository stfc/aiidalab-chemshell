"""Footer with a "Citation" disclosure for the app's footer.

Clicking the "Citation" word reveals a formatted box listing the citations
for this app, the ``aiida-chemshell`` plugin, and ChemShell itself, each with
a bolded title and its DOI rendered as a clickable link.
"""

from datetime import datetime

import ipywidgets as ipw

#: CSS class applied to the footer container.
FOOTER_CLASS = "chemshell-footer"

#: The Ada Lovelace Centre's website, linked from the footer's copyright line.
ALC_URL = "https://adalovelacecentre.ac.uk/"

#: CSS class applied to the "Citation" disclosure toggle.
CITATION_TOGGLE_CLASS = "chemshell-citation-toggle"

#: CSS class applied to the revealed citation box.
CITATION_BOX_CLASS = "chemshell-citation-box"

#: CSS class applied to the citation box's header line.
CITATION_HEADER_CLASS = "chemshell-citation-header"

#: Header shown at the top of the citation box.
CITATION_HEADER = (
    "If you have used this project in your work, please cite the following components;"
)

#: One entry per citable work: a bolded title, the citation text, and a DOI
#: (rendered as a clickable ``https://doi.org/...`` link).
CITATION_ENTRIES = [
    {
        "title": "AiiDAlab ChemShell App",
        "text": 'Speake, B. T. "AiiDAlab ChemShell App". Zenodo.',
        "doi": "10.5281/zenodo.19188755",
    },
    {
        "title": "AiiDA ChemShell plugin",
        "text": 'Speake, B. T. "AiiDA ChemShell Plugin". Zenodo.',
        "doi": "10.5281/zenodo.17055004",
    },
    {
        "title": "ChemShell",
        "text": (
            "Lu, Y.; Farrow, M. R.; Fayon, P.; Logsdail, A. J.; Sokol, A. A.; "
            "Catlow, C. R. A.; Sherwood, P.; Keal, T. W. "
            '"Open-Source, Python-Based Redevelopment of the ChemShell '
            'Multiscale QM/MM Environment". '
            "J. Chem. Theory Comput. 2019, 15, 1317-1328."
        ),
        "doi": "10.1021/acs.jctc.8b01036",
    },
    {
        "title": "ChemShell — DL-FIND geometry optimiser (if used)",
        "text": (
            "Kästner, J.; Carr, J. M.; Keal, T. W.; Thiel, W.; Wander, A.; "
            'Sherwood, P. "DL-FIND: An Open-Source Geometry Optimizer for '
            'Atomistic Simulations". '
            "J. Phys. Chem. A 2009, 113, 11856-11865."
        ),
        "doi": "10.1021/jp9028968",
    },
    {
        "title": "ChemShell — v21.0+ features (recommended)",
        "text": (
            "Lu, Y.; Sen, K.; Yong, C.; Gunn, D. S. D.; Purton, J. A.; Guan, J.; "
            "Desmoutier, A.; Nasir, J. A.; Zhang, X.; Zhu, L.; Hou, Q.; "
            "Jackson-Masters, J.; Watts, S.; Hanson, R.; Thomas, H. N.; "
            "Jayawardena, O.; Logsdail, A. J.; Woodley, S. M.; Senn, H. M.; "
            "Sherwood, P.; Catlow, C. R. A.; Sokol, A. A.; Keal, T. W. "
            '"Multiscale QM/MM modelling of catalytic systems with ChemShell". '
            "Phys. Chem. Chem. Phys. 2023, 25, 21816-21835."
        ),
        "doi": "10.1039/D3CP00648D",
    },
]


def _citation_entry_html(entry):
    """Render a single :data:`CITATION_ENTRIES` item as an HTML block."""
    doi_url = f"https://doi.org/{entry['doi']}"
    return f"""
    <p>
        <strong>{entry["title"]}</strong><br>
        {entry["text"]}<br>
        <a href="{doi_url}" target="_blank" rel="noopener noreferrer">{doi_url}</a>
    </p>
    """


#: The full citation box content: a header followed by a bolded title,
#: citation text and a clickable DOI link for each entry in
#: :data:`CITATION_ENTRIES`.
CITATION_HTML = f'<p class="{CITATION_HEADER_CLASS}">{CITATION_HEADER}</p>' + "".join(
    _citation_entry_html(entry) for entry in CITATION_ENTRIES
)


def chemshell_footer():
    """Return the app footer: a copyright line plus a "Citation" disclosure.

    Clicking "Citation" reveals a box containing :data:`CITATION_HTML`: one
    entry per citable work, each with a bolded title and a clickable DOI link.

    Returns
    -------
    ipywidgets.VBox
        The footer widget, carrying :data:`FOOTER_CLASS`.
    """
    copyright_line = ipw.HTML(
        f"Copyright (c) {datetime.now().year} "
        f'<a href="{ALC_URL}" target="_blank" rel="noopener noreferrer">'
        "Ada Lovelace Centre</a> (STFC)"
    )

    toggle = ipw.ToggleButton(description="Citation", tooltip="Show citation details")
    toggle.add_class(CITATION_TOGGLE_CLASS)

    citation_box = ipw.HTML(
        value=CITATION_HTML,
        layout=ipw.Layout(width="100%", display="none"),
    )
    citation_box.add_class(CITATION_BOX_CLASS)

    def _on_toggle(change):
        citation_box.layout.display = "" if change["new"] else "none"

    toggle.observe(_on_toggle, "value")

    footer = ipw.VBox(children=[copyright_line, toggle, citation_box])
    footer.add_class(FOOTER_CLASS)
    return footer
