"""Spectral fidelity-decomposition MF-FNO (li2020fno + perez2018film).

FNO-native multi-fidelity. The premise: a low-fidelity (coarse-grid) solution
resolves only the LOW Fourier modes of the true field; the high-fidelity
correction lives in the HIGH modes that the coarse grid simply cannot represent.
So we split the spectral weights of every SpectralConv2d into a LOW band (mode
indices the LF grid can resolve) and a HIGH band (everything above), and tie the
training schedule to that split:

  1. PRETRAIN on LF: every spectral weight (w1, w2) is trainable. The net learns
     the coarse, low-mode structure of the operator.
  2. FINE-TUNE on HF: FREEZE the LOW band of every w1, w2 (gradients masked to
     zero) and update ONLY the HIGH-mode band — plus the 1x1 convs, FiLM MLPs,
     lift and proj, which stay fully trainable. The HF stage therefore *adds* the
     high-frequency detail the LF stage could not see, without disturbing the
     low-mode operator it already learned.

The low/high split is per spectral weight, indexed (mode_h, mode_w). A weight
entry is "low" iff (mode_h < cutoff_h) AND (mode_w < cutoff_w); everything else
is "high". `cutoff = min(modes_cap, lf_native_modes)` so the low band is exactly
what the LF grid can resolve (computed in smoke_eval.py and passed to
`freeze_low_band`).

Conditioning is FiLM on X only (identical to the winner mf_fno_transfer_film),
so this isolates the spectral-freezing MECHANISM against the same backbone.

References: li2020fno (FNO backbone); perez2018film (FiLM).
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

_AKASH = Path(__file__).resolve().parents[2]
if str(_AKASH) not in sys.path:
    sys.path.insert(0, str(_AKASH))

from common.backbone import FiLMNorm, param_count  # noqa: E402,F401

Grid = Tuple[int, int]


class SpectralConv2dFreezable(nn.Module):
    """SpectralConv2d (li2020fno §3) with a freezable LOW-mode band.

    Identical math to common.backbone.SpectralConv2d, but each complex weight
    (w1, w2) carries a boolean buffer `low_mask` marking the low band, and a
    backward hook that zeros the gradient on those entries once frozen. The
    low/high split is along the (mode_h, mode_w) axes of the weight tensors.
    """

    def __init__(self, in_ch: int, out_ch: int, modes_h: int, modes_w: int):
        super().__init__()
        self.in_ch, self.out_ch = in_ch, out_ch
        self.modes_h = max(1, modes_h)
        self.modes_w = max(1, modes_w)
        scale = 1.0 / (in_ch * out_ch)
        self.w1 = nn.Parameter(scale * torch.randn(in_ch, out_ch, self.modes_h, self.modes_w, dtype=torch.cfloat))
        self.w2 = nn.Parameter(scale * torch.randn(in_ch, out_ch, self.modes_h, self.modes_w, dtype=torch.cfloat))
        # low_mask[..., h, w] == True where the entry belongs to the LOW band.
        self.register_buffer("low_mask", torch.zeros(self.modes_h, self.modes_w, dtype=torch.bool))
        self._frozen = False
        self._hooks = []

    def freeze_low_band(self, cutoff_h: int, cutoff_w: int) -> int:
        """Mark mode entries with (h < cutoff_h AND w < cutoff_w) as LOW and
        register backward hooks that zero their gradient. Returns the number of
        frozen complex entries per weight tensor (w1 and w2 each)."""
        ch = max(0, min(int(cutoff_h), self.modes_h))
        cw = max(0, min(int(cutoff_w), self.modes_w))
        mask = torch.zeros(self.modes_h, self.modes_w, dtype=torch.bool, device=self.w1.device)
        if ch > 0 and cw > 0:
            mask[:ch, :cw] = True
        self.low_mask = mask
        # broadcast grad mask over (in_ch, out_ch, h, w)
        keep = (~mask).to(self.w1.real.dtype)  # 1.0 on HIGH band (kept), 0.0 on LOW (frozen)

        def _make_hook():
            def hook(grad):
                # grad is complex; multiply real mask broadcasts over both parts.
                return grad * keep.view(1, 1, self.modes_h, self.modes_w)
            return hook

        # remove any prior hooks (idempotent)
        for h in self._hooks:
            h.remove()
        self._hooks = [self.w1.register_hook(_make_hook()), self.w2.register_hook(_make_hook())]
        self._frozen = True
        return int(mask.sum().item()) * self.in_ch * self.out_ch

    def low_band_snapshot(self):
        """Return cloned LOW-band entries of (w1, w2) for an unchanged-after
        -finetune assertion. None if nothing frozen."""
        if not self._frozen or not bool(self.low_mask.any()):
            return None
        m = self.low_mask
        return (self.w1.detach()[:, :, m].clone(), self.w2.detach()[:, :, m].clone())

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, _, H, W = x.shape
        x_ft = torch.fft.rfft2(x, norm="ortho")
        mh = min(self.modes_h, max(H // 2, 1))
        mw = min(self.modes_w, W // 2 + 1)
        out_ft = torch.zeros(B, self.out_ch, H, W // 2 + 1, dtype=torch.cfloat, device=x.device)
        out_ft[:, :, :mh, :mw] = torch.einsum("bchw,cohw->bohw", x_ft[:, :, :mh, :mw], self.w1[:, :, :mh, :mw])
        if H >= 2 * mh:
            out_ft[:, :, -mh:, :mw] = torch.einsum("bchw,cohw->bohw", x_ft[:, :, -mh:, :mw], self.w2[:, :, :mh, :mw])
        return torch.fft.irfft2(out_ft, s=(H, W), norm="ortho")


class FNOBlockFreezable(nn.Module):
    """FNO block using SpectralConv2dFreezable; FiLM(X) norm (matches winner)."""

    def __init__(self, channels: int, modes_h: int, modes_w: int, cond_dim: int,
                 cond_feat_dim: int = 64):
        super().__init__()
        self.spectral = SpectralConv2dFreezable(channels, channels, modes_h, modes_w)
        self.w = nn.Conv2d(channels, channels, 1)
        self.norm = FiLMNorm(channels, cond_dim, cond_feat_dim=cond_feat_dim)

    def forward(self, x: torch.Tensor, cond: torch.Tensor) -> torch.Tensor:
        return F.gelu(self.norm(self.spectral(x) + self.w(x), cond))


class FNO2dSpectralMF(nn.Module):
    """FiLM-on-X FNO whose spectral weights support LOW-band freezing.

    Same lift -> N blocks -> proj structure and same FiLM conditioning as the
    winner; the only difference is the freezable SpectralConv2d. The fidelity
    split is applied externally (smoke_eval.py) via `freeze_low_band` between the
    LF-pretrain and HF-finetune stages.
    """

    def __init__(self, cond_dim: int, hidden_channels: int = 64, n_blocks: int = 4,
                 modes_h: int = 12, modes_w: int = 12, grid: Grid = (64, 64),
                 cond_feat_dim: int = 64):
        super().__init__()
        self.cond_dim = cond_dim
        self.grid = (int(grid[0]), int(grid[1]))
        self.lift = nn.Conv2d(2, hidden_channels, 1)
        self.blocks = nn.ModuleList(
            FNOBlockFreezable(hidden_channels, modes_h, modes_w, cond_dim, cond_feat_dim=cond_feat_dim)
            for _ in range(n_blocks)
        )
        self.proj = nn.Sequential(
            nn.Conv2d(hidden_channels, hidden_channels, 1), nn.GELU(),
            nn.Conv2d(hidden_channels, 1, 1),
        )
        H, W = self.grid
        ys = torch.linspace(-1.0, 1.0, H)
        xs = torch.linspace(-1.0, 1.0, W)
        gy, gx = torch.meshgrid(ys, xs, indexing="ij")
        self.register_buffer("coord_grid", torch.stack([gy, gx], dim=0).unsqueeze(0))

    def freeze_low_band(self, cutoff_h: int, cutoff_w: int) -> int:
        """Freeze the LOW band in every spectral conv. Returns total frozen
        complex entries across all blocks (w1+w2 counted)."""
        tot = 0
        for blk in self.blocks:
            tot += 2 * blk.spectral.freeze_low_band(cutoff_h, cutoff_w)
        return tot

    def low_band_snapshots(self):
        """List of per-block (w1_low, w2_low) snapshots for the frozen assertion."""
        return [blk.spectral.low_band_snapshot() for blk in self.blocks]

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B = x.shape[0]
        H, W = self.grid
        coords = self.coord_grid.expand(B, 2, H, W)
        z = self.lift(coords)
        for blk in self.blocks:
            z = blk(z, x)
        return self.proj(z).squeeze(1)  # (B, H, W)
