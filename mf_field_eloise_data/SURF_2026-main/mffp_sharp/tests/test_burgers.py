import numpy as np
import pytest

from mffp_sharp.pdes import burgers


def test_module_imports_without_clawpack():
    # Lazy clawpack import: the module + sample_configs work with no clawpack installed.
    assert burgers.NDIMS_SUPPORTED == (1, 2)


def test_sample_configs_1d():
    cfg = {"ic_amplitude_range": [0.5, 1.0], "ic_freq_range": [1, 3]}
    specs = burgers.sample_configs(4, cfg, ndim=1, seed=0)
    assert len(specs) == 4 and all(s["ndim"] == 1 for s in specs)
    assert all("ic_amplitude" in s and "ic_freq" in s for s in specs)


def test_sample_configs_rejects_bad_ndim():
    with pytest.raises(AssertionError):
        burgers.sample_configs(2, {"ic_amplitude_range": [0.5, 1.0],
                                   "ic_freq_range": [1, 3]}, ndim=3, seed=0)


@pytest.mark.parametrize("ndim,res", [(1, 64), (2, 32)])
def test_solve_shapes_box(ndim, res):
    pytest.importorskip("clawpack")            # box-only
    spec = {"ic_amplitude": 0.8, "ic_freq": 2, "ndim": ndim, "seed": 0}
    fields, cond, names = burgers.generate_sample(
        spec, [res, 2 * res], 2 * res, output_time=0.2)
    shape1 = (res,) * ndim
    assert fields[res].shape == shape1
    for f in fields.values():
        assert np.isfinite(f).all()
    assert names == ["ic_amplitude", "ic_freq"]
