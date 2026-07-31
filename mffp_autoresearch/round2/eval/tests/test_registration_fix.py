"""Regression tests for the ADR r2-0001 reference fixes (r1 report §5.1-5.2).

The round-1 defect: cell-centred `zoom(..., grid_mode=True, mode="nearest")`
on node-sampled fields — a fixed (r-1)/2 HF-cell misregistration plus a
clamp-extended periodic seam. These tests pin the corrected constructions.
"""
import numpy as np
import pytest

from panel_data import (
    _dirichlet_node_up,
    _legacy_cell_centred_up,
    _node_aligned_periodic_up,
    copylf_prediction,
)


def _data(lf2d, hf2d):
    n = lf2d.shape[0]
    return {
        "hf_fid": 9, "lf_fids": [1],
        "field_by_fid": {1: lf2d.reshape(n, -1), 9: hf2d.reshape(n, -1)},
        "grid_shape_by_fid": {1: lf2d.shape[1:], 9: hf2d.shape[1:]},
    }


def test_variant_c_exact_at_shared_nodes():
    """LF node j coincides with HF node r*j: up[::r, ::r] == coarse exactly."""
    rng = np.random.default_rng(0)
    lf = rng.standard_normal((8, 8))
    up = _node_aligned_periodic_up(lf, (16, 16))
    np.testing.assert_array_equal(up[::2, ::2], lf)


def test_variant_c_samples_k_over_r():
    """Ramp probe: HF pixel k samples LF index k/r (NOT (k+0.5)/r - 0.5)."""
    h, H = 8, 16
    ramp = np.repeat(np.arange(h, dtype=np.float64)[:, None], h, axis=1)
    up = _node_aligned_periodic_up(ramp, (H, H))
    k = np.arange(H, dtype=np.float64)
    # periodic wrap: the last row interpolates between index h-1 and 0
    interior = slice(0, H - 2)
    np.testing.assert_allclose(up[interior, 4], (k / 2)[interior], atol=1e-12)


def test_variant_c_wraps_periodically():
    """The seam interpolates toward row 0, not a clamped copy of row h-1."""
    h, H = 4, 8
    lf = np.zeros((h, h))
    lf[0] = 1.0  # row 0 hot; the last HF row sits between LF rows h-1 and 0
    up = _node_aligned_periodic_up(lf, (H, H))
    assert np.allclose(up[-1], 0.5), f"seam row should average rows h-1 and 0, got {up[-1][:3]}"


def test_variant_c_requires_nested():
    with pytest.raises(ValueError, match="nested"):
        _node_aligned_periodic_up(np.zeros((5, 5)), (12, 12))


def test_variant_e_interior_node_map():
    """Dirichlet grids x_j=(j+1)/(n+1): HF node k maps to LF index (k+1)*(h+1)/(H+1)-1."""
    h, H = 24, 96
    ramp = np.repeat(np.arange(h, dtype=np.float64)[:, None], h, axis=1)
    up = _dirichlet_node_up(ramp, (H, H))
    k = np.arange(H, dtype=np.float64)
    expected = np.clip((k + 1.0) * (h + 1) / (H + 1) - 1.0, 0, h - 1)
    np.testing.assert_allclose(up[:, h // 2], expected, atol=1e-12)


def test_variant_e_antisymmetric_offsets_removed():
    """The old cell-centred map had +-2.88-cell edge offsets on helmholtz grids;
    the interior-node map is exact on a linear field (linear interp reproduces it)."""
    h, H = 24, 96
    x_lf = (np.arange(h) + 1.0) / (h + 1.0)
    lf = np.repeat(x_lf[:, None], h, axis=1)
    up = _dirichlet_node_up(lf, (H, H))
    x_hf = (np.arange(H) + 1.0) / (H + 1.0)
    inner = (x_hf >= x_lf[0]) & (x_hf <= x_lf[-1])  # clamped outside LF support
    np.testing.assert_allclose(up[inner, H // 2], x_hf[inner], atol=1e-12)


def test_copylf_dispatches_by_dataset():
    rng = np.random.default_rng(1)
    lf = rng.standard_normal((3, 8, 8))
    hf = rng.standard_normal((3, 16, 16))
    d = _data(lf, hf)
    fixed = copylf_prediction(d, "sharp__allen_cahn_2d")
    legacy = copylf_prediction(d, None)
    assert not np.allclose(fixed, legacy), "corrected convention must differ from legacy"
    np.testing.assert_array_equal(
        fixed.reshape(3, 16, 16)[:, ::2, ::2], lf, err_msg="node identity broken"
    )
    for i in range(3):
        np.testing.assert_allclose(
            legacy[i], _legacy_cell_centred_up(lf[i], (16, 16)).ravel(), atol=0
        )


def test_unclassified_dataset_raises():
    rng = np.random.default_rng(2)
    d = _data(rng.standard_normal((2, 8, 8)), rng.standard_normal((2, 16, 16)))
    with pytest.raises(ValueError, match="no reference convention"):
        copylf_prediction(d, "some_new_dataset")
