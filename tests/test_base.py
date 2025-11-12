"""Test the base python package (i.e. has it been installed correctly)."""

import aiidalab_chemshell


def test_import():
    """Test whether the python package can be successfully imported."""
    assert aiidalab_chemshell.__version__ is not None
