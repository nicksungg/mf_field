import numpy as np

from mffp_sharp.common import ic_encoding as ice
from mffp_sharp.pdes import fisher_kpp as fk


def _spec(ndim, seed=0):
    s = {"D": 1e-4, "r": 10.0, "domain_size": 1.0, "ndim": ndim, "seed": seed}
    rng = np.random.default_rng(seed)
    s.update(zip(ice.ic_names(ndim), rng.uniform(-1, 1, ice.n_coeffs(ndim))))
    return s


def test_2d_shapes_finite_and_bounded():
    fields, cond, names = fk.generate_sample(_spec(2), [16, 32], 32, output_time=0.02)
    assert fields[16].shape == (16, 16) and fields[32].shape == (32, 32)
    for f in fields.values():
        assert np.isfinite(f).all()
        assert f.min() >= -1e-6 and f.max() <= 1.0 + 1e-6     # logistic stays in [0,1]
    assert names == ["D", "r"] + ice.ic_names(2) and cond.shape == (18,)


def test_1d_shapes_finite():
    fields = fk.generate_sample(_spec(1), [32, 64], 64, output_time=0.02)[0]
    assert fields[32].shape == (32,) and fields[64].shape == (64,)
    for f in fields.values():
        assert np.isfinite(f).all()


def test_deterministic():
    a = fk.generate_sample(_spec(1, seed=2), [32, 64], 64, 0.02)[0][64]
    b = fk.generate_sample(_spec(1, seed=2), [32, 64], 64, 0.02)[0][64]
    assert np.array_equal(a, b)


def test_sample_configs():
    cfg = {"D_range": [1e-4, 1e-3], "r_range": [5.0, 20.0], "domain_size": 1.0}
    specs = fk.sample_configs(3, cfg, ndim=2, seed=1)
    assert len(specs) == 3 and all(s["ndim"] == 2 for s in specs)
    assert all(set(ice.ic_names(2)) <= set(s) for s in specs)
    assert fk.NDIMS_SUPPORTED == (1, 2)


def test_field_is_function_of_exported_cond_only():
    # The completeness contract: rebuilding the spec STRICTLY from the exported
    # cond/names plus config constants (no seed) reproduces the field exactly.
    cfg = {"D_range": [1e-4, 1e-3], "r_range": [5.0, 20.0], "domain_size": 1.0}
    spec = fk.sample_configs(1, cfg, ndim=2, seed=7)[0]
    fields, cond, names = fk.generate_sample(spec, [16, 32], 32, output_time=5 * fk._DT)
    spec2 = dict(zip(names, cond.tolist()))
    spec2.update({"domain_size": 1.0, "ndim": 2})
    fields2, cond2, _ = fk.generate_sample(spec2, [16, 32], 32, output_time=5 * fk._DT)
    assert np.array_equal(fields[32], fields2[32])
    assert np.array_equal(cond, cond2)
    assert [n for n in names if n.startswith("ic_c")] == ice.ic_names(2)


def test_ladder_outputs_spectrally_consistent():
    # Near-zero T: each level solves from the SAME continuous IC (coarse IC spectrally
    # interpolated up). The band-limited IC spans exactly [0,1], so the [0,1] clip in
    # _solve no longer bites and every level sees the identical continuous IC.
    from mffp_sharp.common.spectral import spectral_interp
    fields = fk.generate_sample(_spec(2, seed=4), [16, 32], 32, output_time=1e-6)[0]
    diff = np.abs(spectral_interp(fields[16], 32) - fields[32])
    assert np.median(diff) < 1e-3
    assert (diff < 1e-2).mean() > 0.9
