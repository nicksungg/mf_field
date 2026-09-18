"""Shared fixtures for the common/ refactor tests."""
import numpy as np
import pytest

from mffp_sharp.common import ladder


@pytest.fixture
def ramp_1d():
    """A smooth 1D field on a 4-cell grid (linear ramp -> exact under linear interp)."""
    return np.linspace(0.0, 3.0, 4)


@pytest.fixture
def ramp_2d():
    """A smooth 2D field on a 4x4 grid (separable ramp)."""
    x = np.linspace(0.0, 3.0, 4)
    return np.add.outer(x, x)


@pytest.fixture
def bundle_1d(ramp_1d):
    """A two-level 1D bundle (res 4 -> HF 8) via the real ladder."""
    hf = np.linspace(0.0, 3.0, 8)
    return ladder.assemble_sample({4: ramp_1d, 8: hf}, hf_res=8)


@pytest.fixture
def bundle_2d(ramp_2d):
    """A two-level 2D bundle (res 4 -> HF 8) via the real ladder."""
    x = np.linspace(0.0, 3.0, 8)
    hf = np.add.outer(x, x)
    return ladder.assemble_sample({4: ramp_2d, 8: hf}, hf_res=8)
