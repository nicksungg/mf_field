import numpy as np
import pytest

from mffp_sharp.pdes import helmholtz as hz


def _spec(seed=0):
    return {"wavenumber": 20.0, "source_width": 0.05, "domain_size": 1.0,
            "ndim": 2, "seed": seed}


def test_shapes_finite():
    fields, cond, names = hz.generate_sample(_spec(), [32, 64], 64, output_time=0.0)
    assert fields[32].shape == (32, 32) and fields[64].shape == (64, 64)
    for f in fields.values():
        assert np.isfinite(f).all()
    assert names == ["wavenumber", "source_width"] and cond.shape == (2,)


def test_linear_solve_residual_near_zero():
    # Direct solve -> A u = f to machine precision: the EXACT correctness gate.
    s = _spec()
    fields = hz.generate_sample(s, [64], 64, output_time=0.0)[0]
    r = hz.residual(fields[64], 64, s["wavenumber"], s["source_width"], s["domain_size"])
    assert r < 1e-8


def test_deterministic():
    a = hz.generate_sample(_spec(seed=1), [64], 64, 0.0)[0][64]
    b = hz.generate_sample(_spec(seed=1), [64], 64, 0.0)[0][64]
    assert np.array_equal(a, b)


def test_only_2d_supported():
    assert hz.NDIMS_SUPPORTED == (2,)
    with pytest.raises(AssertionError):
        hz.sample_configs(2, {"wavenumber_range": [10, 30],
                              "source_width_range": [0.03, 0.08], "domain_size": 1.0},
                          ndim=1, seed=0)
