"""Defines a resource setup widget based on foundations from aiidalab-widgets-base."""

import asyncio
import concurrent.futures
import threading

import aiidalab_widgets_base as awb
import ipywidgets as ipw
from traitlets import HasTraits, Unicode, observe

from aiidalab_chemshell import containers


class CodeSetupWidget(ipw.VBox, HasTraits):
    """Widget to setup a new code instance."""

    _database_source = Unicode(
        "",
        allow_none=False,
    )

    def __init__(self, **kwargs):
        self.source = ipw.Text(
            value=self._database_source, description="Source: ", layout={"width": "80%"}
        )
        ipw.dlink((self.source, "value"), (self, "_database_source"))
        self.resource_widget = awb.computational_resources.ResourceSetupBaseWidget()
        self.setup_message = awb.utils.StatusHTML(clear_after=15)
        ipw.dlink(
            (self.resource_widget, "message"),
            (self.setup_message, "message"),
        )

        self.source.value = "https://raw.githubusercontent.com/stfc/alc-ux/refs/heads/main/resources/remotes.json"

        children = [
            ipw.HTML("<hr>"),
            self.source,
            ipw.HTML("<hr>"),
            self.resource_widget,
            self.setup_message,
        ]
        super().__init__(children=children, **kwargs)
        return

    @observe("_database_source")
    def _update_database_source(self, _):
        self.resource_widget.comp_resources_database.database_source = (
            self._database_source
        )
        return


class ChemShellContainerSetupWidget(VBox):
    """Widget for one-click install of the ChemShell container and AiiDA code."""

    _SPINNER = "<i class='fa fa-spinner fa-spin fa-fw'></i>"

    def __init__(self, **kwargs):
        self.install_btn = ipw.Button(
            description="Install ChemShell Container & Create Code",
            button_style="success",
            tooltip="Check Apptainer, build the image and create the AiiDA code",
            icon="download",
            layout={"width": "auto"},
        )
        self.install_btn.on_click(self._on_install_clicked)
        self.status = ipw.HTML("")

        children = [
            self.install_btn,
            self.status,
        ]
        super().__init__(children=children, **kwargs)
        return

    def _set_status(self, message: str, level: str = "info") -> None:
        """Update the status area with a colour-coded message."""
        colours = {
            "info": "#31708f",
            "success": "#3c763d",
            "error": "#a94442",
            "working": "#8a6d3b",
        }
        colour = colours.get(level, colours["info"])
        self.status.value = f"<p style='color:{colour};'>{message}</p>"
        return

    def _on_install_clicked(self, _=None) -> None:
        """Launch the install sequence on a background thread."""
        self.install_btn.disabled = True
        # Capture the notebook's event loop so AiiDA ORM work can be marshalled
        # back onto the main thread (see ``_call_on_loop``).
        self._loop = asyncio.get_event_loop()
        thread = threading.Thread(target=self._run_install, daemon=True)
        thread.start()
        return

    def _call_on_loop(self, func):
        """Run ``func`` on the notebook's event loop and return its result.

        AiiDA's storage session is bound to the (main) thread that loaded the
        profile. ORM operations must therefore run on that thread.
        """
        future: concurrent.futures.Future = concurrent.futures.Future()

        def _wrapper():
            try:
                future.set_result(func())
            except Exception as exc:  # noqa: BLE001 - propagated to the worker
                future.set_exception(exc)

        self._loop.call_soon_threadsafe(_wrapper)
        return future.result()

    def _create_code(self):
        """Create/reuse the ChemShell code (must run on the main thread)."""
        existed = containers.chemshell_code_exists()
        code = containers.create_chemshell_code()
        return existed, code.full_label

    def _run_install(self) -> None:
        """Run the full check/build/create sequence (background thread)."""
        try:
            self._set_status(f"{self._SPINNER} Checking Apptainer ...", "working")
            ok, message = containers.check_apptainer()
            if not ok:
                self._set_status(message, "error")
                return

            if containers.sif_exists():
                self._set_status(
                    f"Existing container image found at "
                    f"<code>{containers.sif_path()}</code>.",
                    "info",
                )
            else:
                self._set_status(
                    f"{self._SPINNER} Building container image "
                    "(this can take several minutes) ...",
                    "working",
                )
                ok, message = containers.build_sif(
                    on_progress=lambda msg: self._set_status(
                        f"{self._SPINNER} {msg}", "working"
                    )
                )
                if not ok:
                    self._set_status(message, "error")
                    return

            self._set_status(f"{self._SPINNER} Creating AiiDA code ...", "working")
            existed, full_label = self._call_on_loop(self._create_code)
            if existed:
                self._set_status(
                    f"Code <code>{full_label}</code> already exists and is "
                    "ready to use.",
                    "success",
                )
            else:
                self._set_status(
                    f"Code <code>{full_label}</code> created successfully.",
                    "success",
                )
        except Exception as exc:  # noqa: BLE001 - surface any failure in the UI
            self._set_status(f"Unexpected error: {exc}", "error")
        finally:
            self.install_btn.disabled = False
        return
