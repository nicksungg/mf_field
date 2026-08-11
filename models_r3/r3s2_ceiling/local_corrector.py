# == RE-VENDORED (round-3 card r3s2_field_reach-B2) ==========================
# SOURCE : round3/worktrees/r3s2_field_reach/B1/models_r3/r3s2_stack_ic/local_corrector.py
# COMMIT : d5069a74bb63da837b89b16508ae25a2164780cc  (tip of branch
#          round3/exp-r3s2_field_reach-B1; recipe.env._vendor_source. The
#          recipe's `base_commit` 76d15c2d is a TRUNK commit that carries NO
#          models_r3/ tree at all -- see notes/handoff_experiment_builder.md.)
# SHA256 : 005d1e75b84f048892be6680ec476d96de5ae09653cabb21ecff85bb0ec5f8b5
# STATUS : byte-identical below this header.
#          Copied, never imported: score_panel.py::code_hash hashes only
#          family_dir/**/*.py, so logic outside the family dir is invisible to
#          the eval cache key.
# ROLE   : declared reuse role (a), round-2 program 5.10a -- the DC-lineage
#          corrector stays a FROZEN test-time sub-component behind a
#          condition->pseudo-LF front end. The B2 contribution is the ROUTE
#          SWITCH + budget accountant, not this code.
# ============================================================================
# == RE-VENDORED (round-3 card r3s2_field_reach-B1) ============================
# SOURCE : round2/worktrees/r2s2_stacked/B1/models_r2/r2s2_stack/local_corrector.py
# COMMIT : 6b4e1d4825666e037a43675c83d9bda6289ec9d0  (recipe.env._vendor_source)
# SHA256 : c1b90028e48994bcb8562c7ee73067024def219c8483235b51c6bff067d6fb1a
# STATUS : byte-identical below this header (the round-2 header block and the
#          body are unchanged). Copied, never imported: score_panel.py::code_hash
#          hashes only family_dir/**/*.py.
# ROLE   : declared reuse role (a), round-2 program 5.10a -- the DC-lineage
#          corrector is a frozen test-time sub-component behind a NEW
#          condition->pseudo-LF front end. The reuse IS the experiment.
# ==============================================================================
# ══ VENDORED (round-2 card r2s2_stacked-B1) ═════════════════════════════
# SOURCE : round1/worktrees/s4_hybrid_routing/B3/models_r1/s4_router/local_corrector.py
# COMMIT : b90d4662cd12820b6926730d39bdb5af70bba276  (recipe.base_commit)
# SHA256 : cdb1c65900648d7786aa665898d8e0b2ecd7eee0525e46d32172137ca7a09202
# STATUS : byte-identical below this header. Round-1 branches are immutable
#          (program.md §5.13); the file is COPIED, never imported, because
#          `score_panel.py::code_hash` hashes only `family_dir/**/*.py` and
#          logic living outside the family dir is invisible to the cache key.
# ROLE   : declared frozen test-time sub-component (program.md §5.10a) behind a
#          new condition->pseudo-LF front end. The reuse IS the experiment.
# ══════════════════════════════════════════════════════════════════════════
"""LOCAL corrector + trust gates for card `s6_local-B2`.

VENDORED from `s6_local-B1 models_r1/s6_local_lf_corrector/local_corrector.py`
@ 3abc0e30d56446148f5322787fbfd1d5f384cc82 (sha256-16 `dcf531f8207b93a3`,
verified before edit). The ONLY B2 edit is the `padding_mode` keyword plumbed
through `ConvNeXtLiteBlock` -> `LocalCorrector` / `PixelGate` (card part 3 edit
(1), the row-(ii) "known bug, quantified cost" repair). `padding_mode="zeros"`
is the torch default, so it is **bit-preserving**: `nn.Conv2d` draws exactly the
same parameter tensors for every `padding_mode` (verified at build time --
kaiming_uniform_ on the weight + uniform on the bias, both independent of the
padding mode), and no parameter shape or construction order changes. The
`b1_replica` arm is therefore numerically identical to B1.

    y_hat = LF_up + G (*) Delta,      Delta = C_theta(LF_up, coords, FiLM(X))

`C_theta` is a depthwise-KxK ConvNeXt-lite stack with per-block FiLM on the
condition vector `X` and a **zero-init final 1x1**, so `Delta == 0` exactly at
initialization and therefore `y_hat == LF_up` exactly at initialization — the
card's identity-to-copy-LF construction (part 3).

Everything a variant changes is the gate `G`:

| `S6_VARIANT`        | gate                                        | kernel      |
|---------------------|---------------------------------------------|-------------|
| `local_pixel_gate`  | `alpha * g(x)`, `g` a LOCAL field-valued head| `S6_KERNEL` |
| `local_scalar_gate` | one scalar `alpha`                           | `S6_KERNEL` |
| `lf_frozen_adapter` | `alpha * g(x)` (== rank 1) + FROZEN LF encoder| `S6_KERNEL` |
| `local_band_gate`   | 4 per-band scalars `c_b`, then `alpha`       | `S6_KERNEL` |
| `pointwise_ctrl`    | `alpha * g(x)` (== rank 1)                   | **1**       |

`alpha` is in every variant selected on a held-out slice of the HF train split
by least-squares projection + line search **whose candidate set contains 0**
(`fit_alpha` below, adapted with citation from the in-round sibling
`s4_hybrid_routing-B1 models_r1/fno_transolver_seq/smoke_eval.py::_fit_alpha`).

References (see INSPIRATION.md): Liu et al. 2022 ConvNeXt (dw-KxK -> pw-4x ->
GELU -> pw block); Perez et al. 2018 FiLM (the FiLMNorm reused from the base
family `mf_fno_transfer_film/model.py`); Zhang et al. 2019 Fixup /
Bachlechner et al. 2020 ReZero (zero-init branch => exact identity at init);
Kochkov et al. 2021 (learned coarse-grid correction).
"""
from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from model import FiLMNorm  # base family mf_fno_transfer_film @967562e (byte-identical copy)

CONVNEXT_EXPANSION = 4  # ConvNeXt canonical inverted-bottleneck ratio (Liu 2022 §2.3)


def odd_kernel(k: int, extent: int) -> int:
    """Largest odd kernel <= min(k, extent). 1-D grids (H == 1) collapse to 1."""
    k = int(min(int(k), int(extent)))
    if k % 2 == 0:
        k -= 1
    return max(1, k)


def coord_grid(grid) -> torch.Tensor:
    """(1, 2, H, W) normalized coordinates — same construction as FNO2d."""
    H, W = int(grid[0]), int(grid[1])
    ys = torch.linspace(-1.0, 1.0, H)
    xs = torch.linspace(-1.0, 1.0, W)
    gy, gx = torch.meshgrid(ys, xs, indexing="ij")
    return torch.stack([gy, gx], dim=0).unsqueeze(0)


def fno_features(fno, cond: torch.Tensor) -> torch.Tensor:
    """Hidden features of a base-family `FNO2d` (its forward minus `proj`).

    Used ONLY by `lf_frozen_adapter`, where the FNO is pretrained on LF data and
    then frozen. Mirrors `FNO2d.forward` exactly so `model.py` stays a
    byte-identical copy of the base family's file.
    """
    B = cond.shape[0]
    H, W = fno.grid
    coords = fno.coord_grid.expand(B, 2, H, W)
    z = fno.lift(coords)
    for blk in fno.blocks:
        z = blk(z, cond)
    return z


class ConvNeXtLiteBlock(nn.Module):
    """depthwise KxK -> FiLMNorm(X) -> pw(4C) -> GELU -> pw(C), residual.

    LOCAL by construction: the only spatial mixing is the depthwise KxK conv, so
    a depth-D stack has receptive field 1 + D*(K-1) cells (D=4, K=7 -> 25, the
    card's stated ~25).

    `padding_mode` (B2): `"zeros"` reproduces B1 exactly; `"circular"` lets the
    depthwise stencil see across the wrap seam that
    `eval/panel_data.py::copylf_prediction`'s `zoom(..., mode="nearest")` leaves
    in the base prediction. Only the four sharp datasets + helmholtz earn
    `"circular"`, and only from the DATA-DRIVEN wrap-continuity criterion in
    `periodicity.py` (no physics assumed -- ADR 0009). Prior art for the repair:
    SineNet (ICLR 2024) Table 3, zero 1.50%/4.19% vs circular 1.02%/1.78%,
    "a simple yet crucial component" -- https://ar5iv.labs.arxiv.org/html/2403.19507.
    """

    def __init__(self, width: int, kernel, cond_dim: int, cond_feat_dim: int = 64,
                 expansion: int = CONVNEXT_EXPANSION, padding_mode: str = "zeros"):
        super().__init__()
        kh, kw = int(kernel[0]), int(kernel[1])
        self.padding_mode = str(padding_mode)
        self.dw = nn.Conv2d(width, width, (kh, kw), padding=(kh // 2, kw // 2), groups=width,
                            padding_mode=self.padding_mode)
        self.norm = FiLMNorm(width, cond_dim, cond_feat_dim=cond_feat_dim)
        self.pw1 = nn.Conv2d(width, expansion * width, 1)
        self.pw2 = nn.Conv2d(expansion * width, width, 1)

    def forward(self, z: torch.Tensor, cond: torch.Tensor) -> torch.Tensor:
        h = self.norm(self.dw(z), cond)
        h = self.pw2(F.gelu(self.pw1(h)))
        return z + h


class LocalCorrector(nn.Module):
    """(LF_up, coords[, frozen LF-encoder features], X) -> Delta on the working grid.

    The final 1x1 is ZERO-INIT (weight and bias), so `Delta == 0` exactly at
    initialization for any input.
    """

    def __init__(self, cond_dim: int, grid, width: int = 32, depth: int = 4,
                 kernel: int = 7, extra_ch: int = 0, cond_feat_dim: int = 64,
                 padding_mode: str = "zeros"):
        super().__init__()
        self.grid = (int(grid[0]), int(grid[1]))
        kh = odd_kernel(kernel, self.grid[0])
        kw = odd_kernel(kernel, self.grid[1])
        self.kernel = (kh, kw)
        self.extra_ch = int(extra_ch)
        self.padding_mode = str(padding_mode)
        in_ch = 1 + 2 + self.extra_ch
        self.lift = nn.Conv2d(in_ch, width, 1)
        self.blocks = nn.ModuleList(
            ConvNeXtLiteBlock(width, (kh, kw), cond_dim, cond_feat_dim=cond_feat_dim,
                              padding_mode=self.padding_mode)
            for _ in range(depth)
        )
        self.head = nn.Conv2d(width, 1, 1)
        nn.init.zeros_(self.head.weight)
        nn.init.zeros_(self.head.bias)
        self.register_buffer("coords", coord_grid(self.grid))

    @property
    def receptive_field(self) -> int:
        return 1 + len(self.blocks) * (max(self.kernel) - 1)

    def forward(self, lf: torch.Tensor, cond: torch.Tensor,
                extra: torch.Tensor = None) -> torch.Tensor:
        B = lf.shape[0]
        H, W = self.grid
        parts = [lf.view(B, 1, H, W), self.coords.expand(B, 2, H, W)]
        if extra is not None:
            parts.append(extra)
        z = self.lift(torch.cat(parts, dim=1))
        for blk in self.blocks:
            z = blk(z, cond)
        return self.head(z).view(B, H, W)


class PixelGate(nn.Module):
    """Field-valued trust gate `g(x) in [0, 1]`, EXACTLY 0 at initialization.

        g(x) = clamp( (sigmoid(h(x) + b0) - sigmoid(b0)) / (1 - sigmoid(b0)), 0, 1 )

    with `b0 = 0` and the final 1x1 of `h` zero-init, i.e. the card's
    "`g(x) = sigmoid(h(x) + b0)` with hard-zero offset so `g == 0` at init":
    the offset `sigmoid(b0)` is subtracted and the result renormalized so the
    gate is exactly 0 at init, monotone in `h`, and still spans the full [0, 1]
    trust range. The subgradient at `h = 0` is `(1 - s0)^-1 * s0 * (1 - s0) = 0.5`,
    so the gate is trainable away from zero (it is not a dead init).

    `h` is itself LOCAL (one ConvNeXt-lite block at the corrector's kernel), so
    the gate's receptive field matches the corrector's per-block extent.
    """

    def __init__(self, cond_dim: int, grid, width: int = 32, kernel: int = 7,
                 extra_ch: int = 0, b0: float = 0.0, cond_feat_dim: int = 64,
                 padding_mode: str = "zeros"):
        super().__init__()
        self.grid = (int(grid[0]), int(grid[1]))
        kh = odd_kernel(kernel, self.grid[0])
        kw = odd_kernel(kernel, self.grid[1])
        self.kernel = (kh, kw)
        self.padding_mode = str(padding_mode)
        in_ch = 1 + 2 + int(extra_ch)
        self.lift = nn.Conv2d(in_ch, width, 1)
        self.block = ConvNeXtLiteBlock(width, (kh, kw), cond_dim, cond_feat_dim=cond_feat_dim,
                                       padding_mode=self.padding_mode)
        self.head = nn.Conv2d(width, 1, 1)
        nn.init.zeros_(self.head.weight)
        nn.init.zeros_(self.head.bias)
        self.register_buffer("coords", coord_grid(self.grid))
        self.register_buffer("b0", torch.tensor(float(b0)))

    def forward(self, lf: torch.Tensor, cond: torch.Tensor,
                extra: torch.Tensor = None) -> torch.Tensor:
        B = lf.shape[0]
        H, W = self.grid
        parts = [lf.view(B, 1, H, W), self.coords.expand(B, 2, H, W)]
        if extra is not None:
            parts.append(extra)
        z = self.block(self.lift(torch.cat(parts, dim=1)), cond)
        h = self.head(z).view(B, H, W)
        s0 = torch.sigmoid(self.b0)
        return torch.clamp((torch.sigmoid(h + self.b0) - s0) / (1.0 - s0), 0.0, 1.0)


# ── held-out gate selection ─────────────────────────────────────────────
#
# `fit_alpha` is adapted, with citation and no claim of novelty, from
# `s4_hybrid_routing-B1 models_r1/fno_transolver_seq/smoke_eval.py::_fit_alpha`
# (card part 3: "least-squares projection + line search whose candidate set
# contains 0 (construction reused from the in-round sibling
# `fno_transolver_seq`; cited, not claimed as novel)"). The single adaptation:
# the base prediction here is `LF_up` (the real coarse solve) rather than the
# champion's generated field, so `base_val` is the copy-LF field.

MIN_GAIN = 1e-3  # s4 sibling's value: a non-zero gate must buy a MEANINGFUL held-out gain


def rel_l2(pred, target) -> float:
    p = np.asarray(pred, dtype=np.float64).reshape(pred.shape[0], -1)
    t = np.asarray(target, dtype=np.float64).reshape(target.shape[0], -1)
    den = np.maximum(np.sqrt((t ** 2).sum(axis=1)), 1e-8)
    return float(np.mean(np.sqrt(((p - t) ** 2).sum(axis=1)) / den))


def fit_alpha(R_val: np.ndarray, C_val: np.ndarray, base_val: np.ndarray,
              Y_val: np.ndarray, include_zero: bool = True):
    """Least-squares gate + line search including 0 (so alpha=0 is always allowed).

    R_val : held-out residual `Y - LF_up` (Nv, HW), raw units
    C_val : the (already band-/pixel-gated) correction (Nv, HW), raw units
    base_val, Y_val : copy-LF prediction and truth on the held-out slice, raw units
    """
    denom = float((C_val * C_val).sum())
    a_ls = float((R_val * C_val).sum() / denom) if denom > 1e-20 else 0.0
    a_ls = float(np.clip(a_ls, 0.0, 1.5))
    cands = {float(np.clip(f * a_ls, 0.0, 1.5)) for f in (0.25, 0.5, 0.75, 1.0, 1.25)}
    cands |= {0.25, 0.5, 1.0}
    if include_zero:
        cands |= {0.0}
    cands = sorted(cands)
    base_r = rel_l2(base_val, Y_val)
    ceiling = base_r * (1.0 - MIN_GAIN)
    best, best_r = (0.0 if include_zero else min(cands)), base_r
    for a in cands:
        r = rel_l2(base_val + a * C_val, Y_val)
        if r < min(best_r, ceiling):
            best, best_r = a, r
    return best, a_ls, base_r, best_r


def fit_band_coeffs(R_val: np.ndarray, D_val: np.ndarray, grid, masks, n_bands: int):
    """Per-band least-squares coefficients `c_b` for `sum_b c_b * P_b Delta ~ R`.

    The band projections are orthogonal (disjoint rFFT masks), so the LS problem
    decouples: `c_b = <P_b R, P_b Delta> / ||P_b Delta||^2`, clipped to [0, 1.5]
    exactly as the scalar gate is. All-zero at init because Delta is all-zero.
    """
    H, W = int(grid[0]), int(grid[1])
    fr = np.fft.rfft2(np.asarray(R_val, dtype=np.float64).reshape(-1, H, W))
    fd = np.fft.rfft2(np.asarray(D_val, dtype=np.float64).reshape(-1, H, W))
    weight = np.full((H, W // 2 + 1), 2.0)
    weight[:, 0] = 1.0
    if W % 2 == 0:
        weight[:, -1] = 1.0
    num = np.real(fr * np.conj(fd)) * weight
    den = (np.abs(fd) ** 2) * weight
    coeffs = []
    for b in range(n_bands):
        m = masks[b]
        d = float(den[:, m].sum())
        n = float(num[:, m].sum())
        coeffs.append(float(np.clip(n / d, 0.0, 1.5)) if d > 1e-20 else 0.0)
    return coeffs


def apply_band_coeffs(delta: np.ndarray, coeffs, grid, masks) -> np.ndarray:
    """`sum_b c_b * P_b Delta` for (N, HW) numpy fields."""
    H, W = int(grid[0]), int(grid[1])
    f = np.fft.rfft2(np.asarray(delta, dtype=np.float64).reshape(-1, H, W))
    acc = np.zeros_like(f)
    for c, m in zip(coeffs, masks):
        acc[:, m] += c * f[:, m]
    return np.fft.irfft2(acc, s=(H, W)).reshape(delta.shape[0], -1)


def param_count(module: nn.Module) -> int:
    return sum(p.numel() for p in module.parameters())
