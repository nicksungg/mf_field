import numpy as np
import pytest

from mffp_sharp.pdes import shallow_water


def test_module_imports_without_clawpack():
    # Lazy clawpack import: the module + sample_configs work with no clawpack installed.
    assert shallow_water.NDIMS_SUPPORTED == (1, 2)


def test_sample_configs_1d():
    cfg = {"inner_height_range": [1.5, 2.5], "dam_radius_range": [0.3, 0.7]}
    specs = shallow_water.sample_configs(4, cfg, ndim=1, seed=0)
    assert len(specs) == 4 and all(s["ndim"] == 1 for s in specs)
    assert all("inner_height" in s and "dam_radius" in s for s in specs)


def test_sample_configs_rejects_bad_ndim():
    with pytest.raises(AssertionError):
        shallow_water.sample_configs(2, {"inner_height_range": [1.5, 2.5],
                                         "dam_radius_range": [0.3, 0.7]}, ndim=3, seed=0)


@pytest.mark.parametrize("ndim,res", [(1, 64), (2, 32)])
def test_solve_shapes_box(ndim, res):
    pytest.importorskip("clawpack")            # box-only
    spec = {"inner_height": 2.0, "dam_radius": 0.5, "ndim": ndim, "seed": 0}
    fields, cond, names = shallow_water.generate_sample(
        spec, [res, 2 * res], 2 * res, output_time=0.2)
    shape1 = (res,) * ndim
    assert fields[res].shape == shape1
    for f in fields.values():
        assert np.isfinite(f).all()
    assert names == ["inner_height", "dam_radius"]
