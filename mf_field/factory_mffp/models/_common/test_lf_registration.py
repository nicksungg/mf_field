"""Registration-convention tests (the checks from the defect note §07).

Run:  .venv/bin/python -m pytest models/_common/test_lf_registration.py -q
  or: .venv/bin/python models/_common/test_lf_registration.py
"""
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lf_registration import (  # noqa: E402
    _dirichlet_node_up,
    _node_aligned_periodic_up,
    node_periodic_upsample_torch,
    resample_fields,
)

NODE_DS = "sharp__allen_cahn_2d"
LEGACY_DS = "ifc_heat"
UNCLASSIFIED_DS = "era5"


def test_index_ramp_probe():
    """Bilinear interp of a linear ramp returns the source coordinate each
    output pixel read.  Node-aligned must read k/r exactly."""
    h, H, r = 8, 16, 2
    ramp = np.tile(np.arange(h, dtype=np.float64), (h, 1))
    up = _node_aligned_periodic_up(ramp, (H, H))
    expected = np.arange(H, dtype=np.float64) / r
    # periodic wrap folds the last half-step back toward index 0; interior
    # columns (all but the wrap seam) must equal k/r exactly.
    np.testing.assert_allclose(up[0, : H - r], expected[: H - r], atol=1e-12)


def test_nesting_invariant_node_path():
    """The one-line invariant: upsample(coarse)[::r, ::r] == coarse exactly."""
    rng = np.random.default_rng(0)
    lf = rng.standard_normal((5, 16, 16)).astype(np.float32)
    out = resample_fields(lf.reshape(5, -1), (16, 16), (32, 32), NODE_DS)
    np.testing.assert_array_equal(out[:, ::2, ::2].astype(np.float64),
                                  lf.astype(np.float64))


def test_node_path_decimates_exactly_on_downsample():
    rng = np.random.default_rng(1)
    hf = rng.standard_normal((3, 32, 32)).astype(np.float32)
    out = resample_fields(hf.reshape(3, -1), (32, 32), (16, 16), NODE_DS)
    np.testing.assert_array_equal(out, hf[:, ::2, ::2])


def test_legacy_path_bit_identical_to_historic_interpolate():
    """Legacy/unclassified datasets must reproduce the zoo's old behaviour
    bit-for-bit — the fix must not move any un-audited dataset."""
    rng = np.random.default_rng(2)
    lf = rng.standard_normal((4, 12, 12)).astype(np.float32)
    for ds in (LEGACY_DS, UNCLASSIFIED_DS):
        out = resample_fields(lf.reshape(4, -1), (12, 12), (24, 24), ds)
        t = torch.from_numpy(lf).unsqueeze(1)
        ref = F.interpolate(t, size=(24, 24), mode="bilinear",
                            align_corners=False).squeeze(1).numpy()
        np.testing.assert_array_equal(out, ref)


def test_torch_node_path_matches_numpy():
    rng = np.random.default_rng(3)
    lf = rng.standard_normal((2, 3, 16, 16))
    got = node_periodic_upsample_torch(torch.from_numpy(lf), (32, 32)).numpy()
    for b in range(2):
        for c in range(3):
            ref = _node_aligned_periodic_up(lf[b, c], (32, 32))
            np.testing.assert_allclose(got[b, c], ref, atol=1e-12)


def test_torch_node_path_is_differentiable():
    x = torch.randn(1, 1, 8, 8, requires_grad=True)
    y = node_periodic_upsample_torch(x, (16, 16))
    y.sum().backward()
    assert x.grad is not None and torch.isfinite(x.grad).all()


def test_dirichlet_map_hits_shared_interior_nodes():
    """helmholtz interior-node grids: n_lf=24 -> n_hf=96 has no shared nodes
    in general, but the map must be the documented affine coordinate rule."""
    h, H = 24, 96
    ramp = np.tile(np.arange(h, dtype=np.float64), (h, 1))
    up = _dirichlet_node_up(ramp, (H, H))
    jj = (np.arange(H) + 1.0) * (h + 1) / (H + 1) - 1.0
    expected = np.clip(jj, 0, h - 1)
    np.testing.assert_allclose(up[0], expected, atol=1e-12)


def test_identity_when_grids_match():
    rng = np.random.default_rng(4)
    y = rng.standard_normal((3, 8, 8)).astype(np.float32)
    out = resample_fields(y.reshape(3, -1), (8, 8), (8, 8), NODE_DS)
    np.testing.assert_array_equal(out, y)


def test_1d_signals_take_legacy_path():
    rng = np.random.default_rng(5)
    y = rng.standard_normal((2, 1, 64)).astype(np.float32)
    out = resample_fields(y.reshape(2, -1), (1, 64), (1, 128), "sharp__sod_1d")
    t = torch.from_numpy(y).unsqueeze(1)
    ref = F.interpolate(t, size=(1, 128), mode="bilinear",
                        align_corners=False).squeeze(1).numpy()
    np.testing.assert_array_equal(out, ref)


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"[ok] {fn.__name__}")
    print(f"{len(fns)} registration tests passed")
