import numpy as np

from mffp_sharp.common import screen


def _mode_2d(n, kx, ky):
    x = np.arange(n) / n
    return np.sin(2 * np.pi * kx * x)[:, None] * np.sin(2 * np.pi * ky * x)[None, :]


def test_energy_above_cutoff_monotone_decreasing():
    f = _mode_2d(64, 10, 10) + 0.5 * _mode_2d(64, 2, 2)
    vals = [screen.energy_above_cutoff(f, kc) for kc in [0, 4, 8, 16]]
    assert all(vals[i] >= vals[i + 1] - 1e-12 for i in range(len(vals) - 1))


def test_f_at_zero_is_one():
    f = _mode_2d(64, 5, 5)
    assert abs(screen.energy_above_cutoff(f, 0) - 1.0) < 1e-9   # all non-DC energy is >0


def test_high_mode_sharper_than_low_mode():
    lo = _mode_2d(64, 2, 2)
    hi = _mode_2d(64, 20, 20)
    kc = 8
    assert screen.energy_above_cutoff(hi, kc) > screen.energy_above_cutoff(lo, kc)


def test_dc_excluded():
    f = 5.0 + _mode_2d(64, 6, 6)            # large DC offset must not change f(k_c)
    g = _mode_2d(64, 6, 6)
    assert abs(screen.energy_above_cutoff(f, 4) - screen.energy_above_cutoff(g, 4)) < 1e-9


def test_sharpness_coordinate_endpoints():
    assert abs(screen.sharpness_coordinate(0.2, 0.2, 0.8) - 0.0) < 1e-12
    assert abs(screen.sharpness_coordinate(0.8, 0.2, 0.8) - 1.0) < 1e-12
    assert np.isnan(screen.sharpness_coordinate(0.5, 0.3, 0.3))   # coincident anchors


def test_floor_and_1d():
    ks = np.sin(2 * np.pi * 3 * np.arange(128) / 128)            # smooth-ish 1D control
    cand = np.sin(2 * np.pi * 30 * np.arange(128) / 128)         # sharp 1D candidate
    kc = 8
    assert screen.passes_floor(screen.energy_above_cutoff(cand, kc),
                               screen.energy_above_cutoff(ks, kc))
    assert screen.energy_above_cutoff(cand, kc) > screen.energy_above_cutoff(ks, kc)


def test_lf_hf_gap_nonnegative():
    hf = _mode_2d(64, 12, 12)
    lf_up = _mode_2d(64, 3, 3)                                   # blurry LF (low modes only)
    assert screen.lf_hf_gap(lf_up, hf, 8) >= 0.0
