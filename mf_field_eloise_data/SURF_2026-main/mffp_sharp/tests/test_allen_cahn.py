import numpy as np

from mffp_sharp.common import ic_encoding as ice
from mffp_sharp.pdes import allen_cahn as ac


def _spec(ndim, seed=0):
    s = {"eps": 0.05, "mobility": 1.0, "mean_composition": 0.0,
         "domain_size": 1.0, "ndim": ndim, "seed": seed}
    rng = np.random.default_rng(seed)
    s.update(zip(ice.ic_names(ndim), rng.uniform(-1, 1, ice.n_coeffs(ndim))))
    return s


def test_2d_fields_shapes_and_finite():
    fields, cond, names = ac.generate_sample(_spec(2), [16, 32], 32, output_time=0.05)
    assert set(fields) == {16, 32}
    assert fields[16].shape == (16, 16) and fields[32].shape == (32, 32)
    for f in fields.values():
        assert np.isfinite(f).all() and np.abs(f).max() < 5.0
    assert names == ["eps", "mobility", "mean_composition"] + ice.ic_names(2)
    assert cond.shape == (19,)


def test_1d_fields_shapes_and_finite():
    fields, cond, names = ac.generate_sample(_spec(1), [32, 64], 64, output_time=0.05)
    assert fields[32].shape == (32,) and fields[64].shape == (64,)
    for f in fields.values():
        assert np.isfinite(f).all()


def test_ladder_outputs_spectrally_consistent():
    # Near-zero T: each level solves from the SAME continuous IC (coarse IC spectrally
    # interpolated up), so the coarse output interpolated up matches the fine output.
    fields = ac.generate_sample(_spec(2, seed=3), [16, 32], 32, output_time=1e-6)[0]
    from mffp_sharp.common.spectral import spectral_interp
    assert np.allclose(spectral_interp(fields[16], 32), fields[32], atol=1e-3)


def test_deterministic():
    a = ac.generate_sample(_spec(1, seed=5), [32, 64], 64, 0.05)[0][64]
    b = ac.generate_sample(_spec(1, seed=5), [32, 64], 64, 0.05)[0][64]
    assert np.array_equal(a, b)


def test_sample_configs():
    cfg = {"eps_range": [0.02, 0.05], "mobility_range": [1.0, 1.0],
           "mean_composition_range": [-0.1, 0.1], "domain_size": 1.0}
    specs = ac.sample_configs(4, cfg, ndim=1, seed=0)
    assert len(specs) == 4 and all(s["ndim"] == 1 for s in specs)
    assert all(set(ice.ic_names(1)) <= set(s) for s in specs)
    assert ac.NDIMS_SUPPORTED == (1, 2)


def test_field_is_function_of_exported_cond_only():
    # The completeness contract: rebuilding the spec STRICTLY from the exported
    # cond/names plus config constants (no seed) reproduces the field exactly.
    cfg = {"eps_range": [0.02, 0.05], "mobility_range": [0.5, 1.5],
           "mean_composition_range": [-0.1, 0.1], "domain_size": 1.0}
    spec = ac.sample_configs(1, cfg, ndim=2, seed=7)[0]
    fields, cond, names = ac.generate_sample(spec, [16, 32], 32, output_time=5 * ac._DT)
    spec2 = dict(zip(names, cond.tolist()))
    spec2.update({"domain_size": 1.0, "ndim": 2})
    fields2, cond2, _ = ac.generate_sample(spec2, [16, 32], 32, output_time=5 * ac._DT)
    assert np.array_equal(fields[32], fields2[32])
    assert np.array_equal(cond, cond2)
    assert [n for n in names if n.startswith("ic_c")] == ice.ic_names(2)
