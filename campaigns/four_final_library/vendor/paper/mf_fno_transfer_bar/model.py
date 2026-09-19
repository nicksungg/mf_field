"""Vanilla Fourier Neural Operator (li2020fno), rectangular- and 1-D-safe.

This is a SINGLE-fidelity FNO: cond vector x -> field y on a grid. The
multi-fidelity behaviour lives entirely in the TRAINING SCHEDULE (smoke_eval.py):
pretrain this one network on abundant low-fidelity data, then fine-tune on the
scarce high-fidelity data — the transfer-learning MF-FNO paradigm of
Lyu et al. 2023 (Phys. Fluids, arXiv:2304.06972) and the geological-carbon-storage
MF-FNO (arXiv:2308.09113). No per-fidelity networks, no residual head, no
coregionalization — that is the whole point: it is the published MF-FNO baseline
against which the in-tree fno_* families are compared.

Architecture is a plain lift -> N FNO blocks -> projection, identical in spirit
to the backbone used by the in-tree FNO families so the COMPARISON ISOLATES THE
MF MECHANISM (transfer vs residual-stack vs coregionalization), not the backbone.
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


class FNO2d(nn.Module):
    """cond vector (B, cond_dim) -> field (B, H, W) on a fixed working grid.

    The conditioning vector is broadcast over the grid and concatenated with two
    coordinate channels (li2020fno's standard parametric-PDE input encoding).
    """

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
        H, W = self.grid
        ys = torch.linspace(-1.0, 1.0, H)
        xs = torch.linspace(-1.0, 1.0, W)
        gy, gx = torch.meshgrid(ys, xs, indexing="ij")
        self.register_buffer("coord_grid", torch.stack([gy, gx], dim=0).unsqueeze(0))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B = x.shape[0]
        H, W = self.grid
        xg = x.view(B, self.cond_dim, 1, 1).expand(B, self.cond_dim, H, W)
        coords = self.coord_grid.expand(B, 2, H, W)
        z = self.lift(torch.cat([xg, coords], dim=1))
        for blk in self.blocks:
            z = blk(z)
        return self.proj(z).squeeze(1)  # (B, H, W)


def param_count(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters())
