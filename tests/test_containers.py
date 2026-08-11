"""Tests for the ChemShell container install / code creation logic."""

import subprocess
from types import SimpleNamespace
from unittest import mock

from aiidalab_chemshell import containers


def _completed(returncode=0, stdout="", stderr=""):
    """Build a fake ``subprocess.CompletedProcess``-like object."""
    return SimpleNamespace(returncode=returncode, stdout=stdout, stderr=stderr)


# --- check_apptainer ------------------------------------------------------


def test_check_apptainer_available():
    """Apptainer present and returning successfully reports ok."""
    with mock.patch.object(
        containers.subprocess,
        "run",
        return_value=_completed(stdout="apptainer version 1.3.0"),
    ):
        ok, message = containers.check_apptainer()
    assert ok is True
    assert "1.3.0" in message


def test_check_apptainer_missing():
    """A missing Apptainer binary is reported as unavailable."""
    with mock.patch.object(containers.subprocess, "run", side_effect=FileNotFoundError):
        ok, message = containers.check_apptainer()
    assert ok is False
    assert "not found" in message.lower()


def test_check_apptainer_broken():
    """Apptainer present but exiting non-zero is reported as an error."""
    with mock.patch.object(
        containers.subprocess,
        "run",
        return_value=_completed(returncode=1, stderr="boom"),
    ):
        ok, message = containers.check_apptainer()
    assert ok is False
    assert "boom" in message


# --- check_docker ---------------------------------------------------------


def test_check_docker_available():
    """Docker present with a reachable daemon reports ok."""
    with mock.patch.object(
        containers.subprocess,
        "run",
        return_value=_completed(stdout="24.0.7"),
    ):
        ok, message = containers.check_docker()
    assert ok is True
    assert "24.0.7" in message


def test_check_docker_missing():
    """A missing Docker binary is reported as unavailable."""
    with mock.patch.object(containers.subprocess, "run", side_effect=FileNotFoundError):
        ok, message = containers.check_docker()
    assert ok is False
    assert "not found" in message.lower()


def test_check_docker_daemon_down():
    """Docker present but the daemon unreachable is reported as an error."""
    with mock.patch.object(
        containers.subprocess,
        "run",
        return_value=_completed(returncode=1, stderr="Cannot connect to the daemon"),
    ):
        ok, message = containers.check_docker()
    assert ok is False
    assert "daemon" in message.lower()


def test_check_docker_uses_server_version_command():
    """The availability check queries the Docker server version."""
    with mock.patch.object(
        containers.subprocess, "run", return_value=_completed(stdout="v")
    ) as run:
        containers.check_docker()
    args = run.call_args.args[0]
    assert args[:2] == ["docker", "version"]
    assert "{{.Server.Version}}" in args
    assert run.call_args.kwargs.get("check") is False


# --- detect_engine --------------------------------------------------------


def test_detect_engine_prefers_apptainer():
    """Apptainer is chosen when available, without checking Docker."""
    with (
        mock.patch.object(
            containers, "check_apptainer", return_value=(True, "apptainer 1.3.0")
        ),
        mock.patch.object(containers, "check_docker") as check_docker,
    ):
        engine, message = containers.detect_engine()
    assert engine == containers.APPTAINER
    assert "1.3.0" in message
    check_docker.assert_not_called()


def test_detect_engine_falls_back_to_docker():
    """Docker is chosen when Apptainer is unavailable."""
    with (
        mock.patch.object(
            containers, "check_apptainer", return_value=(False, "no apptainer")
        ),
        mock.patch.object(containers, "check_docker", return_value=(True, "24.0.7")),
    ):
        engine, message = containers.detect_engine()
    assert engine == containers.DOCKER
    assert "24.0.7" in message


def test_detect_engine_none_available():
    """When neither engine is present, None is returned with both reasons."""
    with (
        mock.patch.object(
            containers, "check_apptainer", return_value=(False, "no apptainer")
        ),
        mock.patch.object(
            containers, "check_docker", return_value=(False, "no docker")
        ),
    ):
        engine, message = containers.detect_engine()
    assert engine is None
    assert "no apptainer" in message
    assert "no docker" in message


# --- build_sif ------------------------------------------------------------


def test_build_sif_success(tmp_path):
    """A successful pull returns ok and reports progress."""
    progress = []
    with (
        mock.patch.object(containers, "CONTAINER_DIR", tmp_path),
        mock.patch.object(
            containers.subprocess, "run", return_value=_completed()
        ) as run,
    ):
        ok, message = containers.build_sif(on_progress=progress.append)
    assert ok is True
    assert progress  # at least one progress message emitted
    # The pull command targets the expected sif path and image uri.
    args = run.call_args.args[0]
    assert args[:2] == ["apptainer", "build"]
    assert args[-1] == containers.CONTAINER_IMAGE_URI


def test_build_sif_failure(tmp_path):
    """A failing pull surfaces the captured error output."""
    with (
        mock.patch.object(containers, "CONTAINER_DIR", tmp_path),
        mock.patch.object(
            containers.subprocess,
            "run",
            return_value=_completed(returncode=255, stderr="registry unreachable"),
        ),
    ):
        ok, message = containers.build_sif()
    assert ok is False
    assert "registry unreachable" in message


# --- docker image helpers -------------------------------------------------


def test_docker_image_exists_true():
    """A zero return code from ``docker image inspect`` means present."""
    with mock.patch.object(
        containers.subprocess, "run", return_value=_completed()
    ) as run:
        assert containers.docker_image_exists() is True
    args = run.call_args.args[0]
    assert args[:3] == ["docker", "image", "inspect"]
    assert args[-1] == containers.DOCKER_IMAGE


def test_docker_image_exists_false_when_absent():
    """A non-zero return code means the image is not present."""
    with mock.patch.object(
        containers.subprocess, "run", return_value=_completed(returncode=1)
    ):
        assert containers.docker_image_exists() is False


def test_docker_image_exists_false_when_missing_binary():
    """A missing Docker binary reports the image as absent."""
    with mock.patch.object(containers.subprocess, "run", side_effect=FileNotFoundError):
        assert containers.docker_image_exists() is False


def test_pull_docker_image_success():
    """A successful pull returns ok and reports progress."""
    progress = []
    with mock.patch.object(
        containers.subprocess, "run", return_value=_completed()
    ) as run:
        ok, message = containers.pull_docker_image(on_progress=progress.append)
    assert ok is True
    assert progress
    args = run.call_args.args[0]
    assert args[:2] == ["docker", "pull"]
    assert args[-1] == containers.DOCKER_IMAGE


def test_pull_docker_image_failure():
    """A failing pull surfaces the captured error output."""
    with mock.patch.object(
        containers.subprocess,
        "run",
        return_value=_completed(returncode=1, stderr="manifest unknown"),
    ):
        ok, message = containers.pull_docker_image()
    assert ok is False
    assert "manifest unknown" in message


# --- engine-agnostic routers ----------------------------------------------


def test_image_exists_routes_by_engine():
    """image_exists dispatches to the sif / docker checks per engine."""
    with (
        mock.patch.object(containers, "sif_exists", return_value=True) as sif,
        mock.patch.object(
            containers, "docker_image_exists", return_value=False
        ) as docker,
    ):
        assert containers.image_exists(containers.APPTAINER) is True
        assert containers.image_exists(containers.DOCKER) is False
    sif.assert_called_once()
    docker.assert_called_once()


def test_build_image_routes_by_engine():
    """build_image dispatches to build_sif / pull_docker_image per engine."""
    with (
        mock.patch.object(
            containers, "build_sif", return_value=(True, "sif")
        ) as build_sif,
        mock.patch.object(
            containers, "pull_docker_image", return_value=(True, "docker")
        ) as pull,
    ):
        assert containers.build_image(containers.APPTAINER) == (True, "sif")
        assert containers.build_image(containers.DOCKER) == (True, "docker")
    build_sif.assert_called_once()
    pull.assert_called_once()


# --- create_chemshell_code ------------------------------------------------


def test_create_chemshell_code_reuses_existing():
    """An existing code is loaded and returned without creating a new one."""
    existing = mock.Mock()
    with (
        mock.patch.object(containers, "chemshell_code_exists", return_value=True),
        mock.patch("aiida.orm.load_code", return_value=existing) as load_code,
        mock.patch("aiida.orm.ContainerizedCode") as containerized,
    ):
        result = containers.create_chemshell_code()
    assert result is existing
    load_code.assert_called_once_with(
        f"{containers.CODE_LABEL}@{containers.COMPUTER_LABEL}"
    )
    containerized.assert_not_called()


def test_create_chemshell_code_creates_new():
    """When no code exists a ContainerizedCode is built, stored and unhidden."""
    computer = mock.Mock()
    code = mock.Mock()
    with (
        mock.patch.object(containers, "chemshell_code_exists", return_value=False),
        mock.patch.object(containers, "get_localhost_computer", return_value=computer),
        mock.patch("aiida.orm.ContainerizedCode", return_value=code) as containerized,
    ):
        result = containers.create_chemshell_code()

    assert result is code
    code.store.assert_called_once()
    assert code.is_hidden is False

    kwargs = containerized.call_args.kwargs
    assert kwargs["computer"] is computer
    assert kwargs["engine_command"] == containers.APPTAINER_ENGINE_COMMAND
    assert "{image_name}" in kwargs["engine_command"]
    assert kwargs["image_name"] == str(containers.sif_path())
    assert kwargs["filepath_executable"] == containers.FILEPATH_EXECUTABLE
    assert kwargs["label"] == containers.CODE_LABEL
    assert kwargs["default_calc_job_plugin"] == containers.DEFAULT_CALC_JOB_PLUGIN


def test_create_chemshell_code_docker_engine():
    """Requesting the Docker engine builds a code with the docker settings."""
    computer = mock.Mock()
    code = mock.Mock()
    with (
        mock.patch.object(containers, "chemshell_code_exists", return_value=False),
        mock.patch.object(containers, "get_localhost_computer", return_value=computer),
        mock.patch("aiida.orm.ContainerizedCode", return_value=code) as containerized,
    ):
        result = containers.create_chemshell_code(engine=containers.DOCKER)

    assert result is code
    kwargs = containerized.call_args.kwargs
    assert kwargs["engine_command"] == containers.DOCKER_ENGINE_COMMAND
    assert "{image_name}" in kwargs["engine_command"]
    assert kwargs["image_name"] == containers.DOCKER_IMAGE
    assert "Docker" in kwargs["description"]


def test_create_chemshell_code_enforces_double_quotes():
    """Creating a code enables double-quote escaping on the computer."""
    computer = mock.Mock()
    computer.get_use_double_quotes.return_value = False
    code = mock.Mock()
    with (
        mock.patch.object(containers, "chemshell_code_exists", return_value=False),
        mock.patch.object(containers, "get_localhost_computer", return_value=computer),
        mock.patch("aiida.orm.ContainerizedCode", return_value=code),
    ):
        containers.create_chemshell_code()
    computer.set_use_double_quotes.assert_called_once_with(True)


# --- ensure_use_double_quotes ---------------------------------------------


def test_ensure_use_double_quotes_sets_when_disabled():
    """A computer with double quotes disabled is updated and reports a change."""
    computer = mock.Mock()
    computer.get_use_double_quotes.return_value = False
    changed = containers.ensure_use_double_quotes(computer)
    assert changed is True
    computer.set_use_double_quotes.assert_called_once_with(True)


def test_ensure_use_double_quotes_noop_when_enabled():
    """A computer that already uses double quotes is left untouched."""
    computer = mock.Mock()
    computer.get_use_double_quotes.return_value = True
    changed = containers.ensure_use_double_quotes(computer)
    assert changed is False
    computer.set_use_double_quotes.assert_not_called()


# --- chemshell_code_exists ------------------------------------------------


def test_chemshell_code_exists_false_when_not_found():
    """A missing code is reported via the NotExistent exception path."""
    from aiida.common.exceptions import NotExistent

    with mock.patch("aiida.orm.load_code", side_effect=NotExistent):
        assert containers.chemshell_code_exists() is False


def test_chemshell_code_exists_true_when_found():
    """An existing code is reported as present."""
    with mock.patch("aiida.orm.load_code", return_value=mock.Mock()):
        assert containers.chemshell_code_exists() is True


# --- sif helpers ----------------------------------------------------------


def test_sif_path_and_exists(tmp_path):
    """sif_path/sif_exists reflect the configured container directory."""
    with mock.patch.object(containers, "CONTAINER_DIR", tmp_path):
        path = containers.sif_path()
        assert path == tmp_path / containers.SIF_FILENAME
        assert containers.sif_exists() is False
        path.write_text("")
        assert containers.sif_exists() is True


def test_check_apptainer_uses_expected_command():
    """The availability check invokes ``apptainer --version``."""
    with mock.patch.object(
        containers.subprocess, "run", return_value=_completed(stdout="v")
    ) as run:
        containers.check_apptainer()
    assert run.call_args.args[0] == ["apptainer", "--version"]
    # Guard against subprocess raising on non-zero exit.
    assert run.call_args.kwargs.get("check") is False


# Ensure the module exposes subprocess for patching stability.
assert hasattr(containers, "subprocess")
assert issubclass(subprocess.SubprocessError, Exception)
