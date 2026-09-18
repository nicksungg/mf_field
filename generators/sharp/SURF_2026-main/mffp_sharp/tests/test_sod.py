import numpy as np
import pytest

from mffp_sharp.pdes import sod


def test_module_imports_without_clawpack():
    # Lazy clawpack import: the module + sample_configs work with no clawpack installed.
    assert sod.NDIMS_SUPPORTED == (1,)


def test_sample_configs_1d():
    cfg = {"rho_l_range": [0.8, 1.2], "p_l_range": [0.8, 1.2], "gamma": 1.4}
    specs = sod.sample_configs(4, cfg, ndim=1, seed=0)
    assert len(specs) == 4 and all(s["ndim"] == 1 for s in specs)
    assert all("rho_l" in s and "p_l" in s and "gamma" in s for s in specs)


def test_sample_configs_rejects_bad_ndim():
    with pytest.raises(AssertionError):
        sod.sample_configs(2, {"rho_l_range": [0.8, 1.2], "p_l_range": [0.8, 1.2],
                               "gamma": 1.4}, ndim=2, seed=0)


def test_solve_shapes_box():
    pytest.importorskip("clawpack")            # box-only
    res = 64
    spec = {"rho_l": 1.0, "p_l": 1.0, "gamma": 1.4, "ndim": 1, "seed": 0}
    fields, cond, names = sod.generate_sample(spec, [res, 2 * res], 2 * res,
                                               output_time=0.2)
    assert fields[res].shape == (res,)
    for f in fields.values():
        assert np.isfinite(f).all()
    assert names == ["rho_l", "p_l", "gamma"]
