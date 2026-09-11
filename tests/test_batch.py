"""Tests for the batch processing submission logic."""

from types import SimpleNamespace
from unittest import mock

from aiidalab_chemshell.process import ChemShellProcess


def _fake_model(has_trajectory=False, has_file=False, use_mm=False):
    """Build a lightweight stand-in for BatchAppModel."""
    trajectory = object() if has_trajectory else None
    structure_file = object() if has_file else None
    return SimpleNamespace(
        batch=True,
        workflow_model=SimpleNamespace(
            qm_theory=SimpleNamespace(name="NWCHEM"),
            use_dft=True,
            functional="B3LYP",
            basis_set="cc-pvdz",
            use_mm=use_mm,
            gradients=True,
            hessian=False,
            force_field=None,
            qm_region="",
            combine_batch_results=True,
        ),
        resource_model=SimpleNamespace(
            code_label="chemsh@localhost",
            ncpus=4,
            process_label="batch label",
            process_description="batch description",
        ),
        structure_model=SimpleNamespace(
            has_trajectory=has_trajectory,
            has_file=has_file,
            trajectory=trajectory,
            structure_file=structure_file,
        ),
    )


# --- validate_model -------------------------------------------------------


def test_validate_model_requires_input():
    """Validation fails when neither a trajectory nor a file is provided."""
    assert ChemShellProcess.validate_model(_fake_model()) is False


def test_validate_model_passes_with_trajectory():
    """Validation passes when a trajectory input is provided."""
    assert ChemShellProcess.validate_model(_fake_model(has_trajectory=True)) is True


def test_validate_model_requires_force_field_for_mm():
    """Validation fails for QM/MM without a force field."""
    model = _fake_model(has_trajectory=True, use_mm=True)
    assert ChemShellProcess.validate_model(model) is False


# --- submit_process routing ----------------------------------------------


def _run_submit(model):
    """Run submit_process with AiiDA calls mocked, returning the builder."""
    builder = SimpleNamespace()
    workchain = mock.Mock()
    workchain.get_builder.return_value = builder
    with (
        mock.patch(
            "aiida_chemshell.workflows.batch_calculation.BatchProcessWorkChain",
            workchain,
        ),
        mock.patch("aiidalab_chemshell.process.load_code", return_value="CODE"),
        mock.patch("aiidalab_chemshell.process.Dict", side_effect=lambda d: d),
        mock.patch(
            "aiidalab_chemshell.process.submit", return_value=mock.Mock()
        ) as submit,
    ):
        process = ChemShellProcess(model)
        process.submit_process()
    return builder, submit


def test_submit_routes_trajectory_to_trajectory_port():
    """A TrajectoryData input is routed to builder.trajectory."""
    model = _fake_model(has_trajectory=True)
    builder, submit = _run_submit(model)
    assert builder.trajectory is model.structure_model.trajectory
    assert not hasattr(builder, "structure_files")
    submit.assert_called_once_with(builder)


def test_submit_routes_file_to_structure_files_namespace():
    """A SinglefileData input is routed to the structure_files namespace."""
    model = _fake_model(has_file=True)
    builder, _ = _run_submit(model)
    structure_file = model.structure_model.structure_file
    assert builder.structure_files == {"input_file": structure_file}
    assert not hasattr(builder, "trajectory")


def test_submit_builds_qm_parameters():
    """The shared qm_parameters dict is built from the workflow model."""
    model = _fake_model(has_trajectory=True)
    builder, _ = _run_submit(model)
    assert builder.qm_parameters == {
        "theory": "NWCHEM",
        "method": "dft",
        "functional": "B3LYP",
        "basis": "cc-pvdz",
    }
    assert builder.code == "CODE"
