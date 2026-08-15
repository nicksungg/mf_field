"""
FNO backbone with FiLM-via-LayerNorm conditioning on the fidelity index `m`.

H2 (cycle-008): the IFC outer-product basis `f(x,m) = sum_k B_k(m) * h_k(x)`
from `models/fno_coregionalization/model.py` (li2022ifc) is replaced with FiLM
affine modulation inside the FNO blocks themselves. A single full-resolution
HF FNO produces the prediction directly; the fidelity index `m` modulates the
normalization-layer (γ, β) affines via a small MLP on `[m, m^2]`.

The architectural precedent is `dumoulin2018featurewise` (FiLM-via-norm for
PDE-parameter conditioning, arXiv:2509.09599) and `herde2024poseidon`
(Poseidon scOT time-conditioned LayerNorm at scale, NeurIPS 2024). The FNO
backbone is `li2020fno`; the LF→HF training schedule retained in
`smoke_eval.py` is `lyu2023mffno`. The K-dim coregionalization basis from
`li2022ifc` is removed — m-modulation is now carried by affine LayerNorm
parameters rather than a per-fidelity outer-product basis, which is the
canonical 2024-2025 PDE-conditioning pattern.

Architecture (Mode A):
  1. Lift: broadcast cond vector X over the working grid, concatenate two
     coordinate channels, project to `hidden_channels` via a 1x1 conv.
  2. Backbone: `n_blocks` FNO blocks. Each block = SpectralConv2d + 1x1
     conv residual + GELU + FiLMNorm(channels, m_feat_dim). FiLMNorm is
     GroupNorm followed by per-channel affine (γ, β) computed from m.
  3. Projection head: two 1x1 convs (hidden → hidden → 1), GELU between.
  4. Per-fidelity output scaler: y = y_scaled * scaler[m], identical to
     the fno_coregionalization family.

Constructor mirrors the cycle-007 H1 anisotropic-modes pattern from
`models/mf_fno_transfer_bar/model.py:62-94`: separate `modes_h, modes_w`
kwargs with grid as a 2-tuple. Smoke_eval.py passes per-axis modes derived
from the working grid.
"""
from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


class SpectralConv2d(nn.Module):
    """2D spectral conv (li2020fno §3), rectangular- and 1-D (H==1)-safe.

    Mirrors `models/mf_fno_transfer_bar/model.py:27` so the comparison
    isolates the FiLM-conditioning mechanism, not the spectral backbone.
    """

    def __init__(self, in_ch: int, out_ch: int, modes_h: int, modes_w: int):
        super().__init__()
        self.in_ch, self.out_ch = in_ch, out_ch
        self.modes_h = max(1, modes_h)
        self.modes_w = max(1, modes_w)
        scale = 1.0 / (in_ch * out_ch)
        self.w1 = nn.Parameter(
            scale * torch.randn(in_ch, out_ch, self.modes_h, self.modes_w,
                                dtype=torch.cfloat)
        )
        self.w2 = nn.Parameter(
            scale * torch.randn(in_ch, out_ch, self.modes_h, self.modes_w,
                                dtype=torch.cfloat)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, _, H, W = x.shape
        x_ft = torch.fft.rfft2(x, norm="ortho")
        mh = min(self.modes_h, max(H // 2, 1))
        mw = min(self.modes_w, W // 2 + 1)
        out_ft = torch.zeros(
            B, self.out_ch, H, W // 2 + 1,
            dtype=torch.cfloat, device=x.device,
        )
        out_ft[:, :, :mh, :mw] = torch.einsum(
            "bchw,cohw->bohw",
            x_ft[:, :, :mh, :mw], self.w1[:, :, :mh, :mw],
        )
        if H >= 2 * mh:
            out_ft[:, :, -mh:, :mw] = torch.einsum(
                "bchw,cohw->bohw",
                x_ft[:, :, -mh:, :mw], self.w2[:, :, :mh, :mw],
            )
        return torch.fft.irfft2(out_ft, s=(H, W), norm="ortho")


class FiLMNorm(nn.Module):
    """GroupNorm followed by m-dependent per-channel affine (FiLM).

    γ(m), β(m) are produced by a small MLP on `[m, m^2]` (matching the
    `B(m)` input encoding from li2022ifc so the conditioning signal is
    bit-comparable to the basis family being replaced). The MLP outputs
    `2 * channels` values which are split into γ and β and broadcast
    over the spatial grid.

    Reference: dumoulin2018featurewise (FiLM-via-norm for PDE-parameter
    conditioning, arXiv:2509.09599); herde2024poseidon (time-conditioned
    LayerNorm at scale, NeurIPS 2024).
    """

    def __init__(self, channels: int, m_feat_dim: int = 32):
        super().__init__()
        self.channels = channels
        self.norm = nn.GroupNorm(min(8, channels), channels, affine=False)
        self.film = nn.Sequential(
            nn.Linear(2, m_feat_dim),
            nn.GELU(),
            nn.Linear(m_feat_dim, 2 * channels),
        )
        # Initialise the final projection so γ ≈ 1, β ≈ 0 at start
        # (preserves the un-conditioned forward pass and avoids early
        # divergence under random init — the standard FiLM init trick).
        nn.init.zeros_(self.film[-1].weight)
        nn.init.zeros_(self.film[-1].bias)

    def forward(self, z: torch.Tensor, m: torch.Tensor) -> torch.Tensor:
        B = z.shape[0]
        m_feat = torch.stack([m, m * m], dim=-1)  # (B, 2)
        gb = self.film(m_feat)  # (B, 2*C)
        gamma, beta = gb.chunk(2, dim=-1)  # each (B, C)
        gamma = 1.0 + gamma  # zero-init → identity at start
        z_n = self.norm(z)
        return gamma.view(B, self.channels, 1, 1) * z_n + beta.view(B, self.channels, 1, 1)


class FNOBlock(nn.Module):
    """FNO block with FiLMNorm replacing the plain GroupNorm.

    Composition matches `mf_fno_transfer_bar/model.py:51` exactly except
    the norm is now m-conditioned: spectral conv + 1x1 residual, then
    GELU(FiLMNorm(spectral + residual, m)).
    """

    def __init__(self, channels: int, modes_h: int, modes_w: int,
                 m_feat_dim: int = 32):
        super().__init__()
        self.spectral = SpectralConv2d(channels, channels, modes_h, modes_w)
        self.w = nn.Conv2d(channels, channels, 1)
        self.norm = FiLMNorm(channels, m_feat_dim=m_feat_dim)

    def forward(self, x: torch.Tensor, m: torch.Tensor) -> torch.Tensor:
        return F.gelu(self.norm(self.spectral(x) + self.w(x), m))


class FNOCoregConditioned(nn.Module):
    """Single full-resolution HF FNO with FiLM-via-LayerNorm m-conditioning.

    Output is the HF prediction directly — no K-dim outer-product basis.
    Per-fidelity output scaler is retained from the fno_coregionalization
    family (matches the ~40× value-scale collapse on ifc_poisson).
    """

    def __init__(
        self,
        cond_dim: int,
        hidden_channels: int = 64,
        n_blocks: int = 4,
        modes_h: int = 12,
        modes_w: int = 12,
        grid: tuple = (64, 64),
        m_feat_dim: int = 32,
    ):
        super().__init__()
        self.cond_dim = cond_dim
        self.grid = (int(grid[0]), int(grid[1]))

        self.lift = nn.Conv2d(cond_dim + 2, hidden_channels, 1)
        self.blocks = nn.ModuleList(
            FNOBlock(hidden_channels, modes_h, modes_w, m_feat_dim=m_feat_dim)
            for _ in range(n_blocks)
        )
        self.proj = nn.Sequential(
            nn.Conv2d(hidden_channels, hidden_channels, 1),
            nn.GELU(),
            nn.Conv2d(hidden_channels, 1, 1),
        )

        # Per-fidelity output scalers (populated externally via set_scalers).
        # Mirrors the fno_coregionalization buffer pattern.
        self.register_buffer("m_keys", torch.zeros(0, dtype=torch.float32))
        self.register_buffer("scalers", torch.zeros(0, dtype=torch.float32))

        H, W = self.grid
        ys = torch.linspace(-1.0, 1.0, H)
        xs = torch.linspace(-1.0, 1.0, W)
        gy, gx = torch.meshgrid(ys, xs, indexing="ij")
        self.register_buffer(
            "coord_grid", torch.stack([gy, gx], dim=0).unsqueeze(0)
        )

    def set_scalers(self, m_keys, scalers):
        dev = self.lift.weight.device
        self.m_keys = torch.as_tensor(m_keys, dtype=torch.float32, device=dev)
        self.scalers = torch.as_tensor(scalers, dtype=torch.float32, device=dev)

    def scaler_for(self, m: torch.Tensor) -> torch.Tensor:
        if self.m_keys.numel() == 0:
            return torch.ones_like(m)
        diff = (m.unsqueeze(-1) - self.m_keys.unsqueeze(0)).abs()
        idx = diff.argmin(dim=-1)
        return self.scalers[idx]

    def forward(self, X: torch.Tensor, m: torch.Tensor) -> torch.Tensor:
        B = X.shape[0]
        H, W = self.grid

        X_grid = X.view(B, self.cond_dim, 1, 1).expand(B, self.cond_dim, H, W)
        coords = self.coord_grid.expand(B, 2, H, W)
        z = torch.cat([X_grid, coords], dim=1)

        z = self.lift(z)
        for blk in self.blocks:
            z = blk(z, m)
        y_scaled = self.proj(z).squeeze(1)  # (B, H, W)

        s = self.scaler_for(m).view(B, 1, 1)
        return y_scaled * s


def param_count(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters())
