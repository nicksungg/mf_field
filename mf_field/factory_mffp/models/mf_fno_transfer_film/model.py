"""FiLM-conditioned Fourier Neural Operator (li2020fno), rectangular- and 1-D-safe.

This is the `mf_fno_transfer_bar` backbone with ONE change: the condition
vector `X` is no longer concatenated as spatially-constant input channels.
Instead it conditions the network via FiLM — per-block, per-channel affine
modulation `(γ(X), β(X))` applied after GroupNorm.

Motivation
----------
In the concat baseline (`mf_fno_transfer_bar/model.py`), `X` is broadcast to a
constant field and concatenated with the coordinate channels before a single
lift conv. A spatially-constant channel carries all its energy in the k=0
Fourier mode, so the spectral convolution barely acts on the conditioning
signal, and the condition is injected only once (at the bottom of the network).

FiLM instead re-injects `X` at every block as a learned per-channel affine.
Because the condition here is a *global* parameter vector, global per-channel
modulation is the natural match — nothing is lost by dropping the spatial
(constant-channel) encoding. This isolates the conditioning MECHANISM
(concat vs FiLM) against the identical spectral backbone and identical
transfer-learning schedule (smoke_eval.py).

FiLM conditions on `X` ONLY (not the fidelity index `m`): the bar is a
single-fidelity network whose multi-fidelity behaviour lives entirely in the
training schedule, so `m` never enters the net — keeping this a pure
concat→FiLM ablation. (Contrast `fno_coreg_conditioned`, which FiLMs on `m`
and still concatenates `X`.)

References: li2020fno (FNO backbone); perez2018film (FiLM);
dumoulin2018featurewise (FiLM-via-norm, Distill 2018) and shokar2025pdecond
(explicit PDE-parameter conditioning, Shokar/Kerswell/Haynes arXiv:2509.09599);
lyu2023mffno (LF→HF transfer schedule, retained in smoke_eval.py).
"""
from __future__ import annotations

from typing import Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

Grid = Tuple[int, int]


class SpectralConv2d(nn.Module):
    """2D spectral conv (li2020fno §3), rectangular- and 1-D (H==1)-safe.

    Byte-for-byte identical to `mf_fno_transfer_bar/model.py` so the comparison
    isolates the conditioning mechanism, not the spectral backbone.
    """

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


class FiLMNorm(nn.Module):
    """GroupNorm followed by X-dependent per-channel affine (FiLM).

    γ(X), β(X) are produced by a small MLP on the raw condition vector `X`
    (cond_dim → cond_feat → 2*channels). The final projection is zero-init so
    γ ≈ 1, β ≈ 0 at start: the network begins as an un-conditioned FNO over the
    coordinate grid and learns to modulate from there (standard FiLM init,
    avoids early divergence). γ and β are broadcast over the spatial grid.
    """

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
        gb = self.film(cond)               # (B, 2*C)
        gamma, beta = gb.chunk(2, dim=-1)  # each (B, C)
        gamma = 1.0 + gamma                # zero-init → identity at start
        z_n = self.norm(z)
        return gamma.view(B, self.channels, 1, 1) * z_n + beta.view(B, self.channels, 1, 1)


class FNOBlock(nn.Module):
    """FNO block with FiLMNorm replacing the plain GroupNorm.

    Composition matches `mf_fno_transfer_bar/model.py` exactly except the norm
    is now X-conditioned: spectral conv + 1x1 residual, then
    GELU(FiLMNorm(spectral + residual, X)).
    """

    def __init__(self, channels: int, modes_h: int, modes_w: int, cond_dim: int,
                 cond_feat_dim: int = 64):
        super().__init__()
        self.spectral = SpectralConv2d(channels, channels, modes_h, modes_w)
        self.w = nn.Conv2d(channels, channels, 1)
        self.norm = FiLMNorm(channels, cond_dim, cond_feat_dim=cond_feat_dim)

    def forward(self, x: torch.Tensor, cond: torch.Tensor) -> torch.Tensor:
        return F.gelu(self.norm(self.spectral(x) + self.w(x), cond))


class FNO2d(nn.Module):
    """cond vector (B, cond_dim) -> field (B, H, W) on a fixed working grid.

    Unlike the concat baseline, the network INPUT is just the 2 coordinate
    channels (sample-independent); all sample-to-sample variation flows through
    FiLM modulation by `X` at every block. Same lift→N blocks→proj structure,
    so param count differs only by the per-block FiLM MLPs.
    """

    def __init__(self, cond_dim: int, hidden_channels: int = 64, n_blocks: int = 4,
                 modes_h: int = 12, modes_w: int = 12, grid: Grid = (64, 64),
                 cond_feat_dim: int = 64):
        super().__init__()
        self.cond_dim = cond_dim
        self.grid = (int(grid[0]), int(grid[1]))
        # Input is coordinates only — X enters via FiLM, not concatenation.
        self.lift = nn.Conv2d(2, hidden_channels, 1)
        self.blocks = nn.ModuleList(
            FNOBlock(hidden_channels, modes_h, modes_w, cond_dim, cond_feat_dim=cond_feat_dim)
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

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B = x.shape[0]
        H, W = self.grid
        coords = self.coord_grid.expand(B, 2, H, W)
        z = self.lift(coords)
        for blk in self.blocks:
            z = blk(z, x)
        return self.proj(z).squeeze(1)  # (B, H, W)


def param_count(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters())
