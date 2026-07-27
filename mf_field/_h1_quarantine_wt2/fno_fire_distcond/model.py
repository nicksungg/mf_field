"""FNO backbone for FIRE-style distribution-conditioned residual learning.

Field analog of FIRE (Yu, Sung, Ahmed 2026, arXiv:2601.22371): instead of a
tabular foundation model, a deep ENSEMBLE of FNOs gives the low-fidelity (LF)
posterior-predictive summaries — per-pixel mean μ_LF, std σ_LF and quantile
fields q_τ — and the high-fidelity (HF) correction is conditioned on those
distributional fields, not on the LF mean alone. This captures spatially
heteroscedastic cross-fidelity discrepancy (LF error concentrates at shocks,
boundaries, vortex cores), which a mean-only additive rule (fno_additive) cannot.

Two network types, both on the shared geometry-general (rectangular- & 1-D-safe)
backbone so the comparison isolates the MECHANISM, not the backbone:
  * FNO2d     — cond vector -> field. Ensemble members are independent FNO2d.
  * FNO2dAug  — cond vector + K extra spatial channels (the LF distributional
                summary fields) -> residual field. This is the FIRE δ-model.
"""
from __future__ import annotations

from typing import Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

Grid = Tuple[int, int]


class SpectralConv2d(nn.Module):
    """2D spectral conv (li2020fno §3), rectangular- and 1-D (H==1)-safe."""

    def __init__(self, in_ch: int, out_ch: int, modes_h: int, modes_w: int):
        super().__init__()
        self.in_ch, self.out_ch = in_ch, out_ch
        self.modes_h = max(1, modes_h)
        self.modes_w = max(1, modes_w)
        scale = 1.0 / (in_ch * out_ch)
        self.w1 = nn.Parameter(scale * torch.randn(in_ch, out_ch, self.modes_h, self.modes_w, dtype=torch.cfloat))
        self.w2 = nn.Parameter(scale * torch.randn(in_ch, out_ch, self.modes_h, self.modes_w, dtype=torch.cfloat))

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


class FNOBlock(nn.Module):
    def __init__(self, channels: int, modes_h: int, modes_w: int):
        super().__init__()
        self.spectral = SpectralConv2d(channels, channels, modes_h, modes_w)
        self.w = nn.Conv2d(channels, channels, 1)
        self.norm = nn.GroupNorm(min(8, channels), channels)

    def forward(self, x):
        return F.gelu(self.norm(self.spectral(x) + self.w(x)))


def _coord_grid(H: int, W: int) -> torch.Tensor:
    ys = torch.linspace(-1.0, 1.0, H)
    xs = torch.linspace(-1.0, 1.0, W)
    gy, gx = torch.meshgrid(ys, xs, indexing="ij")
    return torch.stack([gy, gx], dim=0).unsqueeze(0)


class FNO2d(nn.Module):
    """cond vector (B, cond_dim) -> field (B, H, W). Standard parametric FNO."""

    def __init__(self, cond_dim: int, hidden_channels: int = 64, n_blocks: int = 4,
                 modes_h: int = 12, modes_w: int = 12, grid: Grid = (64, 64)):
        super().__init__()
        self.cond_dim = cond_dim
        self.grid = (int(grid[0]), int(grid[1]))
        self.lift = nn.Conv2d(cond_dim + 2, hidden_channels, 1)
        self.blocks = nn.ModuleList(FNOBlock(hidden_channels, modes_h, modes_w) for _ in range(n_blocks))
        self.proj = nn.Sequential(
            nn.Conv2d(hidden_channels, hidden_channels, 1), nn.GELU(),
            nn.Conv2d(hidden_channels, 1, 1),
        )
        self.register_buffer("coord_grid", _coord_grid(*self.grid))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B = x.shape[0]
        H, W = self.grid
        xg = x.view(B, self.cond_dim, 1, 1).expand(B, self.cond_dim, H, W)
        coords = self.coord_grid.expand(B, 2, H, W)
        z = self.lift(torch.cat([xg, coords], dim=1))
        for blk in self.blocks:
            z = blk(z)
        return self.proj(z).squeeze(1)  # (B, H, W)


class FNO2dAug(nn.Module):
    """cond vector + K extra spatial channels -> residual field.

    The K augmentation channels carry the LF distributional summary FIELDS
    (μ_LF, σ_LF, quantiles) at the working grid. This is the FIRE δ-model:
    the HF correction sees *where* and *how uncertain* the LF prior is.
    """

    def __init__(self, cond_dim: int, aug_ch: int, hidden_channels: int = 64,
                 n_blocks: int = 4, modes_h: int = 12, modes_w: int = 12, grid: Grid = (64, 64)):
        super().__init__()
        self.cond_dim = cond_dim
        self.aug_ch = aug_ch
        self.grid = (int(grid[0]), int(grid[1]))
        self.lift = nn.Conv2d(cond_dim + 2 + aug_ch, hidden_channels, 1)
        self.blocks = nn.ModuleList(FNOBlock(hidden_channels, modes_h, modes_w) for _ in range(n_blocks))
        self.proj = nn.Sequential(
            nn.Conv2d(hidden_channels, hidden_channels, 1), nn.GELU(),
            nn.Conv2d(hidden_channels, 1, 1),
        )
        self.register_buffer("coord_grid", _coord_grid(*self.grid))

    def forward(self, x: torch.Tensor, aug: torch.Tensor) -> torch.Tensor:
        B = x.shape[0]
        H, W = self.grid
        xg = x.view(B, self.cond_dim, 1, 1).expand(B, self.cond_dim, H, W)
        coords = self.coord_grid.expand(B, 2, H, W)
        z = self.lift(torch.cat([xg, coords, aug], dim=1))
        for blk in self.blocks:
            z = blk(z)
        return self.proj(z).squeeze(1)  # (B, H, W)


def param_count(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters())
