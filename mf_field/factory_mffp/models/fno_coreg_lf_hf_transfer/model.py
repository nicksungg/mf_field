"""
FNO backbone + IFC-style continuous-fidelity coregionalization head.

Architecture (implemented from scratch from li2020fno + li2022ifc):

  1. Lift: tile parameter vector X over a 64x64 grid, concatenate with
     two coordinate channels, project to `hidden_channels` via a 1x1 conv.
  2. Backbone: `n_blocks` FNO blocks. Each block = SpectralConv2d + 1x1
     conv residual + GELU + GroupNorm. Spectral conv keeps only the
     first `modes` Fourier modes along each axis.
  3. Project to a low-rank latent grid `h(x) ∈ R^{K × H × W}` via two 1x1
     convs with GELU.
  4. Coregionalization head: `B(m) = MLP([m, m^2])` with output dim K
     (small MLP, not a neural ODE — keeps smoke under budget). Final
     pre-scaler prediction `y_scaled(x) = sum_k B_k(m) * h_k(x)`.
  5. Per-fidelity output scaler: `y = y_scaled * scaler[m]`, where
     `scaler[m] = max(|y|)` over training data at fidelity m. The buffer
     is set externally via `set_scalers` after the train/val split, so
     it reflects only the training subset.
"""
from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


class SpectralConv2d(nn.Module):
    """2D spectral convolution (li2020fno, §3).

    Performs an rfft2 of the input, keeps the lowest `modes_h x modes_w`
    Fourier modes on each side of the height axis (the width axis has only
    non-negative frequencies under rfft2), multiplies by learnable complex
    weights, and inverts back to the spatial domain.
    """

    def __init__(self, in_ch: int, out_ch: int, modes_h: int, modes_w: int):
        super().__init__()
        self.in_ch = in_ch
        self.out_ch = out_ch
        self.modes_h = modes_h
        self.modes_w = modes_w
        scale = 1.0 / (in_ch * out_ch)
        self.w1 = nn.Parameter(
            scale * torch.randn(in_ch, out_ch, modes_h, modes_w, dtype=torch.cfloat)
        )
        self.w2 = nn.Parameter(
            scale * torch.randn(in_ch, out_ch, modes_h, modes_w, dtype=torch.cfloat)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, _, H, W = x.shape
        x_ft = torch.fft.rfft2(x, norm="ortho")  # (B, C_in, H, W//2+1)
        mh = min(self.modes_h, max(H // 2, 1))  # 1-D-safe: H==1 -> mh=1, not 0
        mw = min(self.modes_w, W // 2 + 1)
        out_ft = torch.zeros(
            B, self.out_ch, H, W // 2 + 1,
            dtype=torch.cfloat, device=x.device,
        )
        out_ft[:, :, :mh, :mw] = torch.einsum(
            "bchw,cohw->bohw",
            x_ft[:, :, :mh, :mw], self.w1[:, :, :mh, :mw],
        )
        # Negative-kx corner only when the height axis has room (H >= 2*mh);
        # for H==1 (1-D fields) this is skipped so the slice can't double-count.
        if H >= 2 * mh:
            out_ft[:, :, -mh:, :mw] = torch.einsum(
                "bchw,cohw->bohw",
                x_ft[:, :, -mh:, :mw], self.w2[:, :, :mh, :mw],
            )
        return torch.fft.irfft2(out_ft, s=(H, W), norm="ortho")


class FNOBlock(nn.Module):
    def __init__(self, channels: int, modes_h: int, modes_w: int):
        super().__init__()
        self.spectral = SpectralConv2d(channels, channels, modes_h, modes_w)
        self.w = nn.Conv2d(channels, channels, 1)
        self.norm = nn.GroupNorm(min(8, channels), channels)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return F.gelu(self.norm(self.spectral(x) + self.w(x)))


class FNOCoregionalization(nn.Module):
    def __init__(
        self,
        cond_dim: int,
        hidden_channels: int = 64,
        K: int = 10,
        n_blocks: int = 4,
        modes_h: int = 12,
        modes_w: int = 12,
        grid: tuple = (64, 64),
        b_hidden: int = 64,
    ):
        super().__init__()
        self.cond_dim = cond_dim
        self.K = K
        self.grid = (int(grid[0]), int(grid[1]))

        self.lift = nn.Conv2d(cond_dim + 2, hidden_channels, 1)
        self.blocks = nn.ModuleList(
            FNOBlock(hidden_channels, modes_h, modes_w) for _ in range(n_blocks)
        )
        self.proj = nn.Sequential(
            nn.Conv2d(hidden_channels, hidden_channels, 1),
            nn.GELU(),
            nn.Conv2d(hidden_channels, K, 1),
        )
        # B(m) MLP: input [m, m^2], output K
        self.B = nn.Sequential(
            nn.Linear(2, b_hidden), nn.GELU(),
            nn.Linear(b_hidden, b_hidden), nn.GELU(),
            nn.Linear(b_hidden, K),
        )

        # Per-fidelity output scalers (populated externally via set_scalers).
        # m_keys[i] is the fidelity value (in [0, 1]); scalers[i] = max(|y|)
        # over training samples at that fidelity. We resize the buffers in
        # set_scalers and load_state_dict handles arbitrary sizes via the
        # strict=False path used by smoke_eval.py's resume hook.
        self.register_buffer("m_keys", torch.zeros(0, dtype=torch.float32))
        self.register_buffer("scalers", torch.zeros(0, dtype=torch.float32))

        # Coordinate channels in [-1, 1] x [-1, 1]
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
        # m: (B,) -> (B,) via closest-key lookup against self.m_keys
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
            z = blk(z)
        h = self.proj(z)  # (B, K, H, W)

        m_feat = torch.stack([m, m * m], dim=-1)  # (B, 2)
        Bm = self.B(m_feat)  # (B, K)
        y_scaled = (Bm.view(B, self.K, 1, 1) * h).sum(dim=1)  # (B, H, W)

        s = self.scaler_for(m).view(B, 1, 1)
        return y_scaled * s


def param_count(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters())
