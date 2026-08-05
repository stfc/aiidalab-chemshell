"""Logic for installing the ChemShell container and creating an AiiDA code.

This module contains the pure (non-UI) logic used to provision a ChemShell
runtime for AiiDA. The intended flow is:

1. Detect an available container engine (Apptainer first, then Docker).
2. Reuse an existing local image, or acquire one by pulling the project's
   image from the GitHub Container Registry.
3. Create (or reuse) an AiiDA :class:`~aiida.orm.ContainerizedCode` on the
   ``localhost`` computer pointing at that image.

Apptainer is preferred; Docker is used automatically as a fallback when
Apptainer is not available. The two engines differ in how images are stored
(Apptainer keeps a local ``.sif`` file, Docker keeps the image in its daemon's
store) and in the ``engine_command`` used by the created code, but the executable
path, code label and bind convention are identical for both.
"""

import pathlib
import subprocess
from collections.abc import Callable

# --- Engine identifiers ----------------------------------------------------
APPTAINER = "apptainer"
DOCKER = "docker"

# --- Container / image configuration --------------------------------------
CONTAINER_IMAGE = "ghcr.io/stfc/aiidalab-chemshell/chemsh"
CONTAINER_TAG = "latest"
# Apptainer pulls from a ``docker://`` URI; Docker uses the bare image ref.
CONTAINER_IMAGE_URI = f"docker://{CONTAINER_IMAGE}:{CONTAINER_TAG}"
DOCKER_IMAGE = f"{CONTAINER_IMAGE}:{CONTAINER_TAG}"

# The ``.sif`` is stored under the user's home directory
CONTAINER_DIR = pathlib.Path.home() / ".aiidalab-chemshell" / "containers"
SIF_FILENAME = f"chemshell-{CONTAINER_TAG}.sif"

# --- AiiDA code configuration ---------------------------------------------
CODE_LABEL = "chemsh"
COMPUTER_LABEL = "localhost"
APPTAINER_ENGINE_COMMAND = "apptainer exec --bind $PWD:$PWD --cleanenv {image_name}"
DOCKER_ENGINE_COMMAND = (
    "docker run -v $PWD:/workspace -w /workspace --rm --ipc=host "
    "--entrypoint= {image_name}"
)
FILEPATH_EXECUTABLE = "/opt/chemsh-py/bin/intel/chemsh"
DEFAULT_CALC_JOB_PLUGIN = "chemshell"
PREPEND_TEXT = ""
APPEND_TEXT = ""
WITH_MPI = False

# Timeout (seconds) for the quick engine availability checks.
_APPTAINER_CHECK_TIMEOUT = 30
_DOCKER_CHECK_TIMEOUT = 30


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


def check_docker() -> tuple[bool, str]:
    """
    Check that Docker is installed and its daemon is reachable.

    ``docker version --format '{{.Server.Version}}'`` is used because it
    contacts the daemon: a present CLI with a stopped daemon exits non-zero and
    is correctly reported as unavailable.

    Returns
    -------
    tuple[bool, str]
        A tuple ``(ok, message)`` where ``ok`` is True if Docker is available
        and the daemon responded. ``message`` contains the reported server
        version on success or a human-readable error otherwise.
    """
    try:
        result = subprocess.run(
            ["docker", "version", "--format", "{{.Server.Version}}"],
            capture_output=True,
            text=True,
            timeout=_DOCKER_CHECK_TIMEOUT,
            check=False,
        )
    except FileNotFoundError:
        return (
            False,
            "Docker was not found on this system. Please install Docker "
            "and ensure it is available on the PATH.",
        )
    except subprocess.SubprocessError as exc:
        return (False, f"Failed to run Docker: {exc}")

    if result.returncode != 0:
        error = result.stderr.strip() or result.stdout.strip()
        return (
            False,
            "Docker is installed but the daemon is not reachable: "
            f"{error or 'is the Docker daemon running?'}",
        )

    return (True, result.stdout.strip())


def detect_engine() -> tuple[str | None, str]:
    """
    Detect an available container engine, preferring Apptainer over Docker.

    Returns
    -------
    tuple[str | None, str]
        A tuple ``(engine, message)``. ``engine`` is :data:`APPTAINER` or
        :data:`DOCKER` when one is available (Apptainer takes priority), or
        ``None`` when neither is. ``message`` reports the chosen engine's
        version on success, or the combined reason both were rejected.
    """
    apptainer_ok, apptainer_msg = check_apptainer()
    if apptainer_ok:
        return (APPTAINER, apptainer_msg)

    docker_ok, docker_msg = check_docker()
    if docker_ok:
        return (DOCKER, docker_msg)

    return (
        None,
        "No supported container engine is available. "
        f"Apptainer: {apptainer_msg} Docker: {docker_msg}",
    )


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
            ["apptainer", "build", "--fakeroot", str(target), CONTAINER_IMAGE_URI],
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


def docker_image_exists() -> bool:
    """
    Return whether the ChemShell Docker image is present in the local store.

    Returns
    -------
    bool
        True if ``docker image inspect`` reports the image, False otherwise
        (including when Docker is unavailable).
    """
    try:
        result = subprocess.run(
            ["docker", "image", "inspect", DOCKER_IMAGE],
            capture_output=True,
            text=True,
            timeout=_DOCKER_CHECK_TIMEOUT,
            check=False,
        )
    except (FileNotFoundError, subprocess.SubprocessError):
        return False
    return result.returncode == 0


def pull_docker_image(
    on_progress: Callable[[str], None] | None = None,
) -> tuple[bool, str]:
    """
    Pull the ChemShell Docker image into the local daemon's image store.

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

    _report(f"Pulling {DOCKER_IMAGE} ...")
    try:
        result = subprocess.run(
            ["docker", "pull", DOCKER_IMAGE],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return (False, "Docker was not found on this system.")
    except subprocess.SubprocessError as exc:
        return (False, f"Failed to run Docker pull: {exc}")

    if result.returncode != 0:
        error = result.stderr.strip() or result.stdout.strip()
        return (False, f"Failed to pull the container image: {error}")

    return (True, f"Container image {DOCKER_IMAGE} pulled successfully.")


def image_exists(engine: str) -> bool:
    """
    Return whether the ChemShell image for ``engine`` is already available.

    Parameters
    ----------
    engine : str
        Either :data:`APPTAINER` or :data:`DOCKER`.

    Returns
    -------
    bool
        True if the engine's local image is present, False otherwise.
    """
    if engine == DOCKER:
        return docker_image_exists()
    return sif_exists()


def build_image(
    engine: str, on_progress: Callable[[str], None] | None = None
) -> tuple[bool, str]:
    """
    Acquire the ChemShell image for ``engine`` (Apptainer pull or Docker pull).

    Parameters
    ----------
    engine : str
        Either :data:`APPTAINER` or :data:`DOCKER`.
    on_progress : Callable[[str], None], optional
        Optional callback invoked with human-readable progress messages.

    Returns
    -------
    tuple[bool, str]
        A tuple ``(ok, message)`` as returned by :func:`build_sif` or
        :func:`pull_docker_image`.
    """
    if engine == DOCKER:
        return pull_docker_image(on_progress=on_progress)
    return build_sif(on_progress=on_progress)


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
    # Required for containerized codes (see ``ensure_use_double_quotes``).
    computer.set_use_double_quotes(True)
    computer.configure()
    return computer


def ensure_use_double_quotes(computer) -> bool:
    """
    Ensure ``computer`` escapes command-line arguments with double quotes.

    Containerized codes require this: the ``engine_command`` relies on shell
    variable expansion (``$PWD`` in the bind-mount arguments), which only happens
    inside double quotes. With the AiiDA default of single-quote escaping the
    ``$PWD`` token is passed literally and the bind mount is broken.

    The setting is computer-wide but narrow in reach: it governs the escaping of
    the engine command, MPI arguments and the ``stdin``/``stdout``/``stderr``
    file names. Each code's own executable and arguments are escaped by the
    separate per-code ``use_double_quotes`` attribute, so enabling this does not
    change how other codes' arguments are quoted.

    Parameters
    ----------
    computer : aiida.orm.Computer
        The computer to check and, if necessary, update.

    Returns
    -------
    bool
        True if the setting was changed (was disabled, now enabled), False if it
        was already enabled.
    """
    if computer.get_use_double_quotes():
        return False
    computer.set_use_double_quotes(True)
    return True


def _code_params(engine: str) -> tuple[str, str, str]:
    """
    Return the ``(engine_command, image_name, description)`` for ``engine``.

    Parameters
    ----------
    engine : str
        Either :data:`APPTAINER` or :data:`DOCKER`.

    Returns
    -------
    tuple[str, str, str]
        The ``engine_command``, ``image_name`` and code ``description`` for the
        requested engine.
    """
    if engine == DOCKER:
        return (DOCKER_ENGINE_COMMAND, DOCKER_IMAGE, "ChemShell v25 (Docker)")
    return (APPTAINER_ENGINE_COMMAND, str(sif_path()), "ChemShell v25 (Apptainer)")


def create_chemshell_code(engine: str = APPTAINER):
    """
    Create (or reuse) the ChemShell containerized AiiDA code.

    If a code labelled ``chemsh@localhost`` already exists it is loaded and
    returned unchanged. Otherwise a new
    :class:`~aiida.orm.ContainerizedCode` is created for the requested engine
    (pointing at the local ``.sif`` image for Apptainer, or the Docker image
    ref for Docker), stored, and returned.

    Parameters
    ----------
    engine : str, optional
        Either :data:`APPTAINER` (default) or :data:`DOCKER`.

    Returns
    -------
    aiida.orm.ContainerizedCode
        The stored (or pre-existing) ChemShell code.
    """
    from aiida.orm import ContainerizedCode, load_code

    if chemshell_code_exists():
        return load_code(f"{CODE_LABEL}@{COMPUTER_LABEL}")

    engine_command, image_name, description = _code_params(engine)
    computer = get_localhost_computer()
    # Containerized codes need double-quote escaping so the engine command's
    # ``$PWD`` expands; enforce it here so every caller gets a working code.
    ensure_use_double_quotes(computer)
    code = ContainerizedCode(
        computer=computer,
        engine_command=engine_command,
        image_name=image_name,
        filepath_executable=FILEPATH_EXECUTABLE,
        label=CODE_LABEL,
        description=description,
        default_calc_job_plugin=DEFAULT_CALC_JOB_PLUGIN,
        with_mpi=WITH_MPI,
        prepend_text=PREPEND_TEXT,
        append_text=APPEND_TEXT,
    )
    code.store()
    code.is_hidden = False
    return code
