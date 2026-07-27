"""mf_fno_modeelastic (B3) — nested / ordered Fourier-mode dropout.

Mechanism
---------
A standard FNO learns a FIXED set of spectral weights up to `modes_cap`. Here we
make the network *fidelity-elastic*: during every training step we draw a random
mode cutoff k ~ U[k_min, modes_cap] and, for that forward pass, ZERO OUT every
Fourier mode above k in every SpectralConv2d. Lower frequencies are therefore
trained far more often than high ones, so the network is forced to learn a
NESTED low->high mode hierarchy (Rippel 2014 nested dropout, applied to the
spectral basis instead of latent units). At inference the cutoff can be dialed
down to trade accuracy for a coarser / cheaper spectral representation — the
"elastic" curve — while HF eval simply uses the full cap.

Everything else is byte-for-byte the FiLM winner: FiLM-on-X conditioning, the
same lift -> N FNO blocks -> proj structure, the same transfer schedule (in
smoke_eval.py). The ONLY change is the runtime mode-cutoff threaded through the
forward pass.

References: li2020fno (FNO backbone); rippel2014nesteddropout (ordered/nested
dropout giving a low->high hierarchy); perez2018film (FiLM conditioning).
"""
from __future__ import annotations

from typing import Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

Grid = Tuple[int, int]


class ElasticSpectralConv2d(nn.Module):
    """SpectralConv2d (li2020fno) with a runtime mode cutoff `k`.

    Identical maths to the frozen backbone, except the forward accepts an
    optional `k` that further truncates BOTH the height- and width-mode extents
    for that pass (zeroing every higher mode). k=None uses the full module cap.
    """

    def __init__(self, in_ch: int, out_ch: int, modes_h: int, modes_w: int):
        super().__init__()
        self.in_ch, self.out_ch = in_ch, out_ch
        self.modes_h = max(1, modes_h)
        self.modes_w = max(1, modes_w)
        scale = 1.0 / (in_ch * out_ch)
        self.w1 = nn.Parameter(scale * torch.randn(in_ch, out_ch, self.modes_h, self.modes_w, dtype=torch.cfloat))
        self.w2 = nn.Parameter(scale * torch.randn(in_ch, out_ch, self.modes_h, self.modes_w, dtype=torch.cfloat))

    def forward(self, x: torch.Tensor, k: Optional[int] = None) -> torch.Tensor:
        B, _, H, W = x.shape
        x_ft = torch.fft.rfft2(x, norm="ortho")
        kh = self.modes_h if k is None else min(self.modes_h, max(1, int(k)))
        kw = self.modes_w if k is None else min(self.modes_w, max(1, int(k)))
        mh = min(kh, max(H // 2, 1))
        mw = min(kw, W // 2 + 1)
        out_ft = torch.zeros(B, self.out_ch, H, W // 2 + 1, dtype=torch.cfloat, device=x.device)
        out_ft[:, :, :mh, :mw] = torch.einsum("bchw,cohw->bohw", x_ft[:, :, :mh, :mw], self.w1[:, :, :mh, :mw])
        if H >= 2 * mh:
            out_ft[:, :, -mh:, :mw] = torch.einsum("bchw,cohw->bohw", x_ft[:, :, -mh:, :mw], self.w2[:, :, :mh, :mw])
        return torch.fft.irfft2(out_ft, s=(H, W), norm="ortho")


class FiLMNorm(nn.Module):
    """GroupNorm + X-dependent per-channel affine (FiLM), zero-init -> identity."""

    def __init__(self, channels: int, cond_dim: int, cond_feat_dim: int = 64):
        super().__init__()
        self.channels = channels
        self.norm = nn.GroupNorm(min(8, channels), channels, affine=False)
        self.film = nn.Sequential(
            nn.Linear(cond_dim, cond_feat_dim),
            nn.GELU(),
            nn.Linear(cond_feat_dim, 2 * channels),
        )
        nn.init.zeros_(self.film[-1].weight)
        nn.init.zeros_(self.film[-1].bias)

    def forward(self, z: torch.Tensor, cond: torch.Tensor) -> torch.Tensor:
        B = z.shape[0]
        gb = self.film(cond)
        gamma, beta = gb.chunk(2, dim=-1)
        gamma = 1.0 + gamma
        z_n = self.norm(z)
        return gamma.view(B, self.channels, 1, 1) * z_n + beta.view(B, self.channels, 1, 1)


class ElasticFNOBlock(nn.Module):
    """ElasticSpectralConv2d + 1x1 residual, then GELU(FiLMNorm(., X)); k threaded."""

    def __init__(self, channels: int, modes_h: int, modes_w: int, cond_dim: int,
                 cond_feat_dim: int = 64):
        super().__init__()
        self.spectral = ElasticSpectralConv2d(channels, channels, modes_h, modes_w)
        self.w = nn.Conv2d(channels, channels, 1)
        self.norm = FiLMNorm(channels, cond_dim, cond_feat_dim=cond_feat_dim)

    def forward(self, x: torch.Tensor, cond: torch.Tensor, k: Optional[int] = None) -> torch.Tensor:
        return F.gelu(self.norm(self.spectral(x, k=k) + self.w(x), cond))


class ElasticFNO2d(nn.Module):
    """cond (B, cond_dim) -> field (B, H, W); forward takes an optional cutoff k.

    k applies to EVERY block's spectral conv, so the whole network respects the
    same nested mode budget on a given pass.
    """

    def __init__(self, cond_dim: int, hidden_channels: int = 64, n_blocks: int = 4,
                 modes_h: int = 12, modes_w: int = 12, grid: Grid = (64, 64),
                 cond_feat_dim: int = 64):
        super().__init__()
        self.cond_dim = cond_dim
        self.grid = (int(grid[0]), int(grid[1]))
        self.modes_cap = max(modes_h, modes_w)
        self.lift = nn.Conv2d(2, hidden_channels, 1)
        self.blocks = nn.ModuleList(
            ElasticFNOBlock(hidden_channels, modes_h, modes_w, cond_dim, cond_feat_dim=cond_feat_dim)
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

    def forward(self, x: torch.Tensor, k: Optional[int] = None) -> torch.Tensor:
        B = x.shape[0]
        H, W = self.grid
        coords = self.coord_grid.expand(B, 2, H, W)
        z = self.lift(coords)
        for blk in self.blocks:
            z = blk(z, x, k=k)
        return self.proj(z).squeeze(1)


def param_count(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters())
