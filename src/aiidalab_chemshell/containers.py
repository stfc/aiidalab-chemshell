"""Logic for installing the ChemShell container and creating an AiiDA code.

This module contains the pure (non-UI) logic used to provision a ChemShell
runtime for AiiDA. The intended flow is:

1. Check that Apptainer is installed and can be executed.
2. Reuse an existing local ``.sif`` image, or build one by pulling the
   project's image from the GitHub Container Registry.
3. Create (or reuse) an AiiDA :class:`~aiida.orm.ContainerizedCode` on the
   ``localhost`` computer pointing at the ``.sif`` file.

Apptainer is supported first; the function signatures are structured so that a
Docker engine can be added later without changing the public interface.
"""

import pathlib
import subprocess
from collections.abc import Callable

# --- Container / image configuration --------------------------------------
CONTAINER_IMAGE = "ghcr.io/stfc/aiidalab-chemshell/chemsh"
CONTAINER_TAG = "latest"
CONTAINER_IMAGE_URI = f"docker://{CONTAINER_IMAGE}:{CONTAINER_TAG}"

# The ``.sif`` is stored under the user's home directory
CONTAINER_DIR = pathlib.Path.home() / ".aiidalab-chemshell" / "containers"
SIF_FILENAME = f"chemshell-{CONTAINER_TAG}.sif"

# --- AiiDA code configuration ---------------------------------------------
CODE_LABEL = "chemsh"
COMPUTER_LABEL = "localhost"
ENGINE_COMMAND = "apptainer exec --bind $PWD:$PWD --cleanenv {image_name}"
FILEPATH_EXECUTABLE = "/opt/chemsh-py/bin/intel/chemsh"
DEFAULT_CALC_JOB_PLUGIN = "chemshell"
PREPEND_TEXT = ""
APPEND_TEXT = ""
WITH_MPI = False

# Timeout (seconds) for the quick Apptainer availability check.
_APPTAINER_CHECK_TIMEOUT = 30


def sif_path() -> pathlib.Path:
    """
    Return the absolute path to the local ChemShell ``.sif`` image.

    Returns
    -------
    pathlib.Path
        The path where the ``.sif`` image is (or would be) stored.
    """
    return CONTAINER_DIR / SIF_FILENAME


def sif_exists() -> bool:
    """
    Return whether the local ChemShell ``.sif`` image already exists.

    Returns
    -------
    bool
        True if the ``.sif`` file exists, False otherwise.
    """
    return sif_path().is_file()


def check_apptainer() -> tuple[bool, str]:
    """
    Check that Apptainer is installed and can be executed.

    Returns
    -------
    tuple[bool, str]
        A tuple ``(ok, message)`` where ``ok`` is True if Apptainer is
        available and returned successfully. ``message`` contains the reported
        version on success or a human-readable error otherwise.
    """
    try:
        result = subprocess.run(
            ["apptainer", "--version"],
            capture_output=True,
            text=True,
            timeout=_APPTAINER_CHECK_TIMEOUT,
            check=False,
        )
    except FileNotFoundError:
        return (
            False,
            "Apptainer was not found on this system. Please install Apptainer "
            "and ensure it is available on the PATH.",
        )
    except subprocess.SubprocessError as exc:
        return (False, f"Failed to run Apptainer: {exc}")

    if result.returncode != 0:
        error = result.stderr.strip() or result.stdout.strip()
        return (
            False,
            f"Apptainer is installed but returned an error: {error}",
        )

    return (True, result.stdout.strip())


def build_sif(on_progress: Callable[[str], None] | None = None) -> tuple[bool, str]:
    """
    Build the local ChemShell ``.sif`` image by pulling from the registry.

    This pulls :data:`CONTAINER_IMAGE_URI` into :func:`sif_path` using
    ``apptainer pull``.

    Parameters
    ----------
    on_progress : Callable[[str], None], optional
        Optional callback invoked with human-readable progress messages.

    Returns
    -------
    tuple[bool, str]
        A tuple ``(ok, message)`` where ``ok`` is True on success. ``message``
        contains a success note or the captured error output on failure.
    """

    def _report(message: str) -> None:
        if on_progress is not None:
            on_progress(message)

    CONTAINER_DIR.mkdir(parents=True, exist_ok=True)
    target = sif_path()

    _report(f"Pulling {CONTAINER_IMAGE_URI} to {target} ...")
    try:
        result = subprocess.run(
            ["apptainer", "pull", str(target), CONTAINER_IMAGE_URI],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return (False, "Apptainer was not found on this system.")
    except subprocess.SubprocessError as exc:
        return (False, f"Failed to run Apptainer pull: {exc}")

    if result.returncode != 0:
        error = result.stderr.strip() or result.stdout.strip()
        return (False, f"Failed to build the container image: {error}")

    return (True, f"Container image built successfully at {target}.")


def chemshell_code_exists() -> bool:
    """
    Return whether the ChemShell AiiDA code already exists.

    Returns
    -------
    bool
        True if a code labelled ``chemsh@localhost`` exists, False otherwise.
    """
    from aiida.common.exceptions import NotExistent
    from aiida.orm import load_code

    try:
        load_code(f"{CODE_LABEL}@{COMPUTER_LABEL}")
    except NotExistent:
        return False
    return True


def get_localhost_computer():
    """
    Return the ``localhost`` AiiDA computer, creating it if necessary.

    In AiiDAlab deployments the ``localhost`` computer is normally pre-created
    by the base-image startup scripts, so this typically just loads it. If it
    does not exist, a minimal local computer is created and configured as a
    safety fallback.

    Returns
    -------
    aiida.orm.Computer
        The configured ``localhost`` computer.
    """
    from aiida.common.exceptions import NotExistent
    from aiida.orm import Computer, load_computer

    try:
        return load_computer(COMPUTER_LABEL)
    except NotExistent:
        pass

    computer = Computer(
        label=COMPUTER_LABEL,
        hostname=COMPUTER_LABEL,
        workdir=str(pathlib.Path.home() / "aiida_run"),
        transport_type="core.local",
        scheduler_type="core.direct",
    )
    computer.store()
    computer.set_minimum_job_poll_interval(0)
    computer.set_default_mpiprocs_per_machine(1)
    computer.configure()
    return computer


def create_chemshell_code():
    """
    Create (or reuse) the ChemShell containerized AiiDA code.

    If a code labelled ``chemsh@localhost`` already exists it is loaded and
    returned unchanged. Otherwise a new
    :class:`~aiida.orm.ContainerizedCode` is created pointing at the local
    ``.sif`` image, stored, and returned.

    Returns
    -------
    aiida.orm.ContainerizedCode
        The stored (or pre-existing) ChemShell code.
    """
    from aiida.orm import ContainerizedCode, load_code

    if chemshell_code_exists():
        return load_code(f"{CODE_LABEL}@{COMPUTER_LABEL}")

    computer = get_localhost_computer()
    code = ContainerizedCode(
        computer=computer,
        engine_command=ENGINE_COMMAND,
        image_name=str(sif_path()),
        filepath_executable=FILEPATH_EXECUTABLE,
        label=CODE_LABEL,
        default_calc_job_plugin=DEFAULT_CALC_JOB_PLUGIN,
        with_mpi=WITH_MPI,
        prepend_text=PREPEND_TEXT,
        append_text=APPEND_TEXT,
    )
    code.store()
    code.is_hidden = False
    return code
