import os

import numpy as np
import pytest

from mffp_sharp.common import ic_encoding as ice
from mffp_sharp.common.spectral import spectral_interp
from mffp_sharp.pdes import kuramoto_sivashinsky as ks

_GOLDEN = os.path.join(os.path.dirname(__file__), "fixtures", "ks_2d_golden.npy")


def _spec(ndim, seed=0, L=30.0):
    s = {"L": L, "ic_amplitude": 0.1, "ndim": ndim, "seed": seed}
    rng = np.random.default_rng(seed)
    s.update(zip(ice.ic_names(ndim), rng.uniform(-1, 1, ice.n_coeffs(ndim))))
    return s


@pytest.mark.skipif(not os.path.exists(_GOLDEN),
                    reason="golden fixture (*.npy, gitignored) lives on the box")
def test_2d_output_matches_golden():
    # The N-D generalization must not change the validated 2D solve. The golden was
    # recorded from the pre-IC-encoding white-noise IC, so reproduce that IC here and
    # pin _solve directly (which the IC-encoding change does not touch).
    golden = np.load(_GOLDEN)
    rng = np.random.default_rng(1)
    ic_coarse = 0.1 * (2 * rng.random((16, 16)) - 1)
    fields = {res: ks._solve(spectral_interp(ic_coarse, res), 30.0, 2.0)
              for res in (16, 32)}
    got = np.stack([fields[16].ravel()[:64], fields[32].ravel()[:64]])
    assert np.allclose(got, golden, atol=1e-12, rtol=0)


def test_1d_shapes_and_zero_mean():
    fields, cond, names = ks.generate_sample(_spec(1, seed=2), [64, 128], 128, output_time=2.0)
    assert fields[64].shape == (64,) and fields[128].shape == (128,)
    for f in fields.values():
        assert np.isfinite(f).all()
        assert abs(float(f.mean())) < 1e-8          # stores zero-mean fluctuation
    assert names == ["L", "ic_amplitude"] + ice.ic_names(1) and cond.shape == (18,)


def test_1d_deterministic():
    spec = _spec(1, seed=5, L=28.0)
    a = ks.generate_sample(spec, [64, 128], 128, 2.0)[0][128]
    b = ks.generate_sample(spec, [64, 128], 128, 2.0)[0][128]
    assert np.array_equal(a, b)


def test_field_is_function_of_exported_cond_only():
    cfg = {"L_range": [22.0, 36.0], "ic_amplitude_range": [0.05, 0.2]}
    spec = ks.sample_configs(1, cfg, ndim=1, seed=7)[0]
    fields, cond, names = ks.generate_sample(spec, [64, 128], 128, output_time=1.0)
    spec2 = dict(zip(names, cond.tolist()))
    spec2.update({"ndim": 1})
    fields2, cond2, _ = ks.generate_sample(spec2, [64, 128], 128, output_time=1.0)
    assert np.array_equal(fields[128], fields2[128])
    assert np.array_equal(cond, cond2)


def test_1d_supported():
    assert ks.NDIMS_SUPPORTED == (1, 2)
    cfg = {"L_range": [22.0, 36.0], "ic_amplitude_range": [0.05, 0.2]}
    specs = ks.sample_configs(3, cfg, ndim=1, seed=0)
    assert all(s["ndim"] == 1 for s in specs)
    assert all(set(ice.ic_names(1)) <= set(s) for s in specs)
