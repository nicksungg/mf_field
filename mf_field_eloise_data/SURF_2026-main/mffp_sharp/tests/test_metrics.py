import numpy as np

from mffp_sharp.common import metrics


def test_spectral_band_1d_identical_is_zero():
    ref = np.sin(np.linspace(0, 4 * np.pi, 64))
    assert metrics.spectral_band(ref, ref) == 0.0


def test_spectral_band_1d_nonzero_for_difference():
    ref = np.sin(np.linspace(0, 4 * np.pi, 64))
    pred = np.zeros_like(ref)
    v = metrics.spectral_band(pred, ref)
    assert np.isfinite(v) and v > 0.0


def test_spectral_band_2d_unchanged():
    rng = np.random.default_rng(0)
    ref = rng.standard_normal((16, 16))
    assert metrics.spectral_band(ref, ref) == 0.0


def test_boundary_count_1d():
    mask = np.array([False, False, True, True])
    assert metrics._boundary_count(mask) == 1


def test_boundary_count_2d_unchanged():
    mask = np.zeros((4, 4), dtype=bool)
    mask[2:, :] = True
    assert metrics._boundary_count(mask) == 4


def test_interface_position_1d_zero_when_identical():
    ref = np.array([0.0, 0.0, 1.0, 1.0])
    assert metrics.interface_position(ref, ref) == 0.0


def test_interface_position_1d_positive_when_shifted():
    ref = np.array([0.0, 0.0, 1.0, 1.0])
    pred = np.array([0.0, 1.0, 1.0, 1.0])
    assert metrics.interface_position(pred, ref) > 0.0


def test_ssim_1d_returns_nan():
    ref = np.linspace(0, 1, 32)
    assert np.isnan(metrics.ssim(ref, ref))


def test_evaluate_1d_panel_runs():
    ref = np.sin(np.linspace(0, 4 * np.pi, 64))
    pred = 0.9 * ref
    out = metrics.evaluate(pred, ref, ["rel_l2", "linf", "spectral_band",
                                       "interface_position", "conservation", "ssim"])
    assert set(out) == {"rel_l2", "linf", "spectral_band",
                        "interface_position", "conservation", "ssim"}
    assert np.isnan(out["ssim"])
    assert out["rel_l2"] > 0.0
