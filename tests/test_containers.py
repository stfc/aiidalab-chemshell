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
    assert args[:2] == ["apptainer", "pull"]
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
    assert kwargs["engine_command"] == containers.ENGINE_COMMAND
    assert "{image_name}" in kwargs["engine_command"]
    assert kwargs["image_name"] == str(containers.sif_path())
    assert kwargs["filepath_executable"] == containers.FILEPATH_EXECUTABLE
    assert kwargs["label"] == containers.CODE_LABEL
    assert kwargs["default_calc_job_plugin"] == containers.DEFAULT_CALC_JOB_PLUGIN


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
