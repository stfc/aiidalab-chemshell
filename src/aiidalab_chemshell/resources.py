"""Defines a widget for one-click install of the ChemShell container and AiiDA code."""

import asyncio
import concurrent.futures
import threading

import ipywidgets as ipw

from aiidalab_chemshell import containers
from aiidalab_chemshell.common.utils import (
    add_button_style_class,
    chemshell_button_style,
)


class ChemShellContainerSetupWidget(ipw.VBox):
    """Widget for one-click install of the ChemShell container and AiiDA code."""

    _SPINNER = "<i class='fa fa-spinner fa-spin fa-fw'></i>"

    def __init__(self, **kwargs):
        self.install_btn = ipw.Button(
            description="Install ChemShell Container & Create Code",
            button_style="success",
            tooltip=(
                "Detect Apptainer or Docker, build the image and create the AiiDA code"
            ),
            icon="download",
            layout={"width": "auto"},
        )
        self.install_btn.on_click(self._on_install_clicked)
        add_button_style_class(self.install_btn)
        self.status = ipw.HTML("")

        children = [
            chemshell_button_style(),
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

    def _create_code(self, engine: str):
        """Create/reuse the ChemShell code (must run on the main thread)."""
        existed = containers.chemshell_code_exists()
        # Containerized codes require double-quote escaping on the computer for
        # the engine command's ``$PWD`` to expand. Enable it if needed (also
        # covers the code-reuse path) and report whether we changed it.
        computer = containers.get_localhost_computer()
        dq_changed = containers.ensure_use_double_quotes(computer)
        code = containers.create_chemshell_code(engine)
        return existed, code.full_label, dq_changed

    def _run_install(self) -> None:
        """Run the full detect/build/create sequence (background thread)."""
        try:
            self._set_status(
                f"{self._SPINNER} Checking for a container engine ...", "working"
            )
            engine, message = containers.detect_engine()
            if engine is None:
                self._set_status(message, "error")
                return

            self._set_status(f"Using {engine} ({message}).", "info")

            if containers.image_exists(engine):
                self._set_status(
                    "Existing container image found; reusing it.",
                    "info",
                )
            else:
                self._set_status(
                    f"{self._SPINNER} Building container image "
                    "(this can take several minutes) ...",
                    "working",
                )
                ok, message = containers.build_image(
                    engine,
                    on_progress=lambda msg: self._set_status(
                        f"{self._SPINNER} {msg}", "working"
                    ),
                )
                if not ok:
                    self._set_status(message, "error")
                    return

            self._set_status(f"{self._SPINNER} Creating AiiDA code ...", "working")
            existed, full_label, dq_changed = self._call_on_loop(
                lambda: self._create_code(engine)
            )
            if existed:
                message = (
                    f"Code <code>{full_label}</code> already exists and is "
                    "ready to use."
                )
            else:
                message = f"Code <code>{full_label}</code> created successfully."
            if dq_changed:
                message += (
                    " Note: enabled <code>use_double_quotes</code> on the "
                    f"<code>{containers.COMPUTER_LABEL}</code> computer, which is "
                    "required for containerized codes."
                )
            self._set_status(message, "success")
        except Exception as exc:  # noqa: BLE001 - surface any failure in the UI
            self._set_status(f"Unexpected error: {exc}", "error")
        finally:
            self.install_btn.disabled = False
        return
