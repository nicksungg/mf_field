import numpy as np

from mffp_sharp.pdes import gray_scott as gs


def _spec(seed=0):
    return {"F": 0.029, "k_rate": 0.057, "Du": 2e-5, "Dv": 1e-5,
            "domain_size": 2.0, "ndim": 2, "seed": seed}


def test_shapes_finite():
    fields, cond, names = gs.generate_sample(_spec(), [32, 64], 64, output_time=10.0)
    assert fields[32].shape == (32, 32) and fields[64].shape == (64, 64)
    for f in fields.values():
        assert np.isfinite(f).all()
    assert names == ["F", "k_rate"] and cond.shape == (2,)


def test_trivial_fixed_point_stays_fixed():
    # u == 1, v == 0 everywhere is an exact steady state: reactions vanish, nothing moves.
    res = 64
    u0 = np.ones((res, res)); v0 = np.zeros((res, res))
    u, v = gs._solve(u0, v0, 2e-5, 1e-5, F=0.029, k_rate=0.057,
                     domain_size=2.0, output_time=50.0)
    assert np.max(np.abs(u - 1.0)) < 1e-8
    assert np.max(np.abs(v)) < 1e-8


def test_deterministic():
    a = gs.generate_sample(_spec(seed=2), [64], 64, 10.0)[0][64]
    b = gs.generate_sample(_spec(seed=2), [64], 64, 10.0)[0][64]
    assert np.array_equal(a, b)


def test_stable_at_config_range():
    # A representative Pearson regime over a longer time must stay finite & bounded in [0,1.5].
    fields = gs.generate_sample(
        {"F": 0.058, "k_rate": 0.065, "Du": 2e-5, "Dv": 1e-5,
         "domain_size": 2.0, "ndim": 2, "seed": 4}, [32, 64], 64, output_time=50.0)[0]
    for f in fields.values():
        # spectral ringing on the sharp GS fronts gives a tiny negative undershoot
        # (~-1.3e-5 at T=50), 4 orders below the field max (~0.34); -2e-5 bounds it while
        # still catching gross instability.
        assert np.isfinite(f).all() and f.min() >= -2e-5 and f.max() < 1.5


def test_only_2d_supported():
    assert gs.NDIMS_SUPPORTED == (2,)
    import pytest
    with pytest.raises(AssertionError):
        gs.sample_configs(2, {"F_range": [0.02, 0.06], "k_rate_range": [0.05, 0.07],
                              "Du": 2e-5, "Dv": 1e-5, "domain_size": 2.0}, ndim=1, seed=0)
