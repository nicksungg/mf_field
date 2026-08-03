import numpy as np
import pytest

from mffp_sharp.common import ladder


# ── cell-centred path: behaviour identical to the pre-fix implementation ─────

def test_1d_constant_preserved():
    f = np.full(4, 2.0)
    out = ladder.upsample_to_hf(f, 8, convention="cell_centered")
    assert out.shape == (8,)
    assert np.allclose(out, 2.0)


def test_1d_linear_matches_np_interp():
    f = np.linspace(0.0, 3.0, 4)
    out = ladder.upsample_to_hf(f, 8, convention="cell_centered")
    src = (np.arange(4) + 0.5) / 4
    dst = (np.arange(8) + 0.5) / 8
    assert np.allclose(out, np.interp(dst, src, f))


def test_1d_identity_when_same_res():
    f = np.linspace(0.0, 3.0, 4)
    out = ladder.upsample_to_hf(f, 4, convention="cell_centered")
    assert out.shape == (4,)
    assert np.allclose(out, f)


def test_1d_nearest_order():
    f = np.array([0.0, 1.0, 2.0, 3.0])
    out = ladder.upsample_to_hf(f, 8, order="nearest", convention="cell_centered")
    assert out.shape == (8,)
    assert set(np.unique(out)).issubset(set(f.tolist()))


def test_2d_unchanged_constant():
    f = np.full((4, 4), 2.0)
    out = ladder.upsample_to_hf(f, 8, convention="cell_centered")
    assert out.shape == (8, 8)
    assert np.allclose(out, 2.0)


def test_assemble_sample_1d():
    b = ladder.assemble_sample(
        {4: np.linspace(0, 3, 4), 8: np.linspace(0, 3, 8)}, 8, pde="sod"
    )
    assert b["aligned"][4].shape == (8,)
    assert b["aligned"][8].shape == (8,)
    assert b["raw"][4].shape == (4,)
    assert b["convention"] == "cell_centered"


def test_unsupported_ndim_raises():
    with pytest.raises(ValueError):
        ladder.upsample_to_hf(np.zeros((2, 2, 2)), 4, convention="cell_centered")


# ── registration-defect fix (2026-08-01 note item 2): dispatch policy ────────

def test_convention_is_required():
    with pytest.raises(TypeError):
        ladder.upsample_to_hf(np.zeros(4), 8)  # no convention kwarg


def test_unknown_convention_raises():
    with pytest.raises(ValueError):
        ladder.upsample_to_hf(np.zeros(4), 8, convention="bilinear")


def test_unclassified_pde_raises():
    with pytest.raises(ValueError):
        ladder.assemble_sample({4: np.zeros(4)}, 8, pde="navier_stokes")


def test_every_generator_module_is_classified():
    """Every solver module wired into generate.py has an assigned convention."""
    from mffp_sharp import generate

    for name in generate._MODULES:
        assert ladder.convention_for_pde(name) in ladder.CONVENTIONS


def test_convention_for_pde_examples():
    assert ladder.convention_for_pde("allen_cahn") == "node_periodic"
    assert ladder.convention_for_pde("cahn_hilliard") == "node_periodic"
    assert ladder.convention_for_pde("helmholtz") == "node_dirichlet"
    assert ladder.convention_for_pde("euler") == "cell_centered"


# ── node_periodic: the invariant that would have caught the defect on day 1 ──
# (mirrors models/_common/test_lf_registration.py and panel_data variant C)

def test_node_periodic_exact_nesting_2d():
    rng = np.random.default_rng(0)
    f = rng.standard_normal((4, 4))
    up = ladder.upsample_to_hf(f, 8, convention="node_periodic")
    assert np.array_equal(up[::2, ::2], f)


def test_node_periodic_exact_nesting_1d():
    rng = np.random.default_rng(1)
    f = rng.standard_normal(8)
    up = ladder.upsample_to_hf(f, 32, convention="node_periodic")
    assert np.array_equal(up[::4], f)


def test_node_periodic_index_ramp_probe():
    """Bilinear interp of the index ramp returns the source coordinate each
    output pixel read: up[k] == k*h/H away from the periodic seam."""
    h, H = 4, 8
    f = np.arange(h, dtype=np.float64)
    up = ladder.upsample_to_hf(f, H, convention="node_periodic")
    k = np.arange(H)
    interior = k <= (h - 1) * (H // h)
    assert np.allclose(up[interior], (k * h / H)[interior], atol=1e-12)
    # seam pixel wraps: between f[h-1] and f[0]
    assert np.isclose(up[-1], (f[-1] + f[0]) / 2.0)


def test_node_periodic_periodic_wrap_no_clamp():
    """The seam interpolates across the periodic boundary, not clamp-extends."""
    f = np.zeros((4, 4))
    f[0, 0] = 1.0
    up = ladder.upsample_to_hf(f, 8, convention="node_periodic")
    # pixel (7,0) sits between rows 3 and 0 -> sees half of f[0,0] via wrap
    assert np.isclose(up[7, 0], 0.5)


def test_node_periodic_requires_nested():
    with pytest.raises(ValueError):
        ladder.upsample_to_hf(np.zeros(3), 8, convention="node_periodic")


def test_half_cell_shift_gone_on_node_data():
    """A node-sampled periodic sine keeps its phase under node_periodic but is
    displaced by the old cell-centred map — the defect this fix removes."""
    h, H = 32, 64
    truth = np.sin(2 * np.pi * np.arange(H) / H)
    coarse = np.sin(2 * np.pi * np.arange(h) / h)
    up_new = ladder.upsample_to_hf(coarse, H, convention="node_periodic")
    up_old = ladder.upsample_to_hf(coarse, H, convention="cell_centered")
    shared = np.arange(0, H, H // h)
    err_new = np.max(np.abs(up_new[shared] - truth[shared]))
    err_old = np.max(np.abs(up_old[shared] - truth[shared]))
    assert err_new < 1e-12                 # exact at shared nodes
    assert err_old > 0.04                  # ~half-coarse-cell phase shift


# ── node_dirichlet (variant E; helmholtz) ────────────────────────────────────

def test_node_dirichlet_linear_exact_interior():
    """A linear field on interior nodes x_j=(j+1)/(h+1) is reproduced exactly
    wherever the target coordinate falls inside the source node range."""
    h, H = 4, 8
    f = (np.arange(h) + 1.0) / (h + 1.0)          # f(x) = x on interior nodes
    up = ladder.upsample_to_hf(f, H, convention="node_dirichlet")
    x_dst = (np.arange(H) + 1.0) / (H + 1.0)
    inside = (x_dst >= 1.0 / (h + 1.0)) & (x_dst <= h / (h + 1.0))
    assert np.allclose(up[inside], x_dst[inside], atol=1e-12)
    # outside the source range values are clamped, not extrapolated
    assert np.all(up >= f[0] - 1e-12) and np.all(up <= f[-1] + 1e-12)


def test_node_dirichlet_2d_matches_separable_1d():
    rng = np.random.default_rng(2)
    a = rng.standard_normal(4)
    f2 = np.add.outer(a, a)
    up2 = ladder.upsample_to_hf(f2, 8, convention="node_dirichlet")
    up1 = ladder.upsample_to_hf(a, 8, convention="node_dirichlet")
    assert np.allclose(up2, np.add.outer(up1, up1), atol=1e-12)
