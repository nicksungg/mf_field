import numpy as np

from mffp_sharp.common import ic_encoding as ice
from mffp_sharp.pdes import phase_field_crystal as pfc


def _spec(seed=0):
    s = {"r": -0.25, "mean_density": -0.3, "ic_amplitude": 0.05,
         "domain_size": 32.0, "ndim": 2, "seed": seed}
    rng = np.random.default_rng(seed)
    s.update(zip(ice.ic_names(2), rng.uniform(-1, 1, ice.n_coeffs(2))))
    return s


def test_shapes_finite_bounded():
    fields, cond, names = pfc.generate_sample(_spec(), [32, 64], 64, output_time=5.0)
    assert fields[32].shape == (32, 32) and fields[64].shape == (64, 64)
    for f in fields.values():
        assert np.isfinite(f).all() and np.abs(f).max() < 1e2
    assert names == ["r", "mean_density"] + ice.ic_names(2) and cond.shape == (18,)


def test_mass_conserved():
    # The leading laplacian makes PFC conservative: the spatial mean is preserved.
    res = 64
    rng = np.random.default_rng(1)
    psi0 = -0.3 + 0.05 * (2 * rng.random((res, res)) - 1)
    out = pfc._solve(psi0, r=-0.25, domain_size=32.0, output_time=5.0)
    assert abs(float(out.mean()) - float(psi0.mean())) < 1e-9


def test_deterministic():
    a = pfc.generate_sample(_spec(seed=2), [64], 64, 5.0)[0][64]
    b = pfc.generate_sample(_spec(seed=2), [64], 64, 5.0)[0][64]
    assert np.array_equal(a, b)


def test_ladder_outputs_spectrally_consistent():
    from mffp_sharp.common.spectral import spectral_interp
    fields = pfc.generate_sample(_spec(seed=4), [32, 64], 64, output_time=1e-6)[0]
    assert np.allclose(spectral_interp(fields[32], 64), fields[64], atol=1e-3)


def test_field_is_function_of_exported_cond_only():
    # The completeness contract: rebuilding the spec STRICTLY from the exported
    # cond/names plus config constants (no seed) reproduces the field exactly.
    cfg = {"r_range": [-0.4, -0.1], "mean_density_range": [-0.4, -0.2],
           "ic_amplitude": 0.05, "domain_size": 32.0}
    spec = pfc.sample_configs(1, cfg, ndim=2, seed=7)[0]
    fields, cond, names = pfc.generate_sample(spec, [32, 64], 64, output_time=1.0)
    spec2 = dict(zip(names, cond.tolist()))
    spec2.update({"ic_amplitude": 0.05, "domain_size": 32.0, "ndim": 2})
    fields2, cond2, _ = pfc.generate_sample(spec2, [32, 64], 64, output_time=1.0)
    assert np.array_equal(fields[64], fields2[64])
    assert np.array_equal(cond, cond2)
    assert [n for n in names if n.startswith("ic_c")] == ice.ic_names(2)


def test_only_2d_supported():
    assert pfc.NDIMS_SUPPORTED == (2,)
    import pytest
    with pytest.raises(AssertionError):
        pfc.sample_configs(2, {"r_range": [-0.4, -0.1], "mean_density_range": [-0.4, -0.2],
                               "ic_amplitude": 0.05, "domain_size": 32.0}, ndim=1, seed=0)
