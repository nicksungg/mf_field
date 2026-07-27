"""Discrepancy-gated transfer FNO (dg_transfer).

The benchmark verdict on `dg_fno` was clear: the discrepancy gates (spatial FiLM
+ spectral mode-gate) DO improve over plain FIRE, and the learned gain field
provably locates the LF->HF error — but they were grafted onto the FIRE *residual*
decomposition (HF = mu_LF + rho*delta), which is itself ~1.4x behind the
transfer-learning branch and catastrophically worse on the Poisson scale-collapse
datasets. So the gates were on the wrong backbone.

This family puts the SAME gates on the WINNING backbone: `mf_fno_transfer_film`
(the #1 model). That backbone predicts the HF field directly via a single FNO that
is pretrained on LF then fine-tuned on HF with PER-STAGE output scalers (the
re-scaling that sidesteps the Poisson collapse). We keep all of that untouched and
only add uncertainty modulation:

  Gate A — spatial FiLM: the per-block GroupNorm affine gets a per-pixel term from
           the encoded LF-uncertainty field G, ALONGSIDE the proven global X-FiLM.
  Gate B — spectral mode-gate: each retained Fourier mode is scaled by a learned
           gain from the uncertainty's own spectrum (open the bands where LF error
           is high-frequency).

Gate C (the residual gain rho) is intentionally dropped: this network predicts HF
directly, there is no mu_LF residual to gate. Both gates are zero-init, so at
initialization dg_transfer is byte-for-byte `mf_fno_transfer_film` and can only grow
the uncertainty conditioning from there — it cannot regress below #1.

The uncertainty fields [mu, sigma, q10, q50, q90] come from a SMALL LF ensemble
(smoke_eval.py), kept deliberately lean so the param budget stays near the 4.77M
transfer backbone rather than ballooning to the 28M FIRE ensemble.

References: li2020fno (FNO); perez2018film (FiLM); lyu2023mffno (LF->HF transfer
schedule); FIRE (Yu, Sung & Ahmed 2026, arXiv:2601.22371; the uncertainty signal).
"""
from __future__ import annotations

from typing import FrozenSet, Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

Grid = Tuple[int, int]
ALL_GATES: FrozenSet[str] = frozenset({"A", "B"})  # no residual gate on this backbone


class GatedSpectralConv2d(nn.Module):
    """2D spectral conv (li2020fno §3) with an optional per-mode uncertainty gain.

    Identical to the shared SpectralConv2d, except the retained modes are scaled
    by g = 1 + tanh(mode_proj(U_modes)) when an uncertainty mode-spectrum is passed.
    `mode_proj` is zero-init so g == 1 at start (Gate B is a no-op until trained).
    """

    def __init__(self, in_ch: int, out_ch: int, modes_h: int, modes_w: int, gate_ch: int):
        super().__init__()
        self.in_ch, self.out_ch = in_ch, out_ch
        self.modes_h = max(1, modes_h)
        self.modes_w = max(1, modes_w)
        scale = 1.0 / (in_ch * out_ch)
        self.w1 = nn.Parameter(scale * torch.randn(in_ch, out_ch, self.modes_h, self.modes_w, dtype=torch.cfloat))
        self.w2 = nn.Parameter(scale * torch.randn(in_ch, out_ch, self.modes_h, self.modes_w, dtype=torch.cfloat))
        self.mode_proj = nn.Conv2d(gate_ch, out_ch, 1)
        nn.init.zeros_(self.mode_proj.weight)
        nn.init.zeros_(self.mode_proj.bias)

    def forward(self, x: torch.Tensor, u_modes: Optional[torch.Tensor]) -> torch.Tensor:
        B, _, H, W = x.shape
        x_ft = torch.fft.rfft2(x, norm="ortho")
        mh = min(self.modes_h, max(H // 2, 1))
        mw = min(self.modes_w, W // 2 + 1)
        out_ft = torch.zeros(B, self.out_ch, H, W // 2 + 1, dtype=torch.cfloat, device=x.device)
        low = torch.einsum("bchw,cohw->bohw", x_ft[:, :, :mh, :mw], self.w1[:, :, :mh, :mw])
        high = None
        if H >= 2 * mh:
            high = torch.einsum("bchw,cohw->bohw", x_ft[:, :, -mh:, :mw], self.w2[:, :, :mh, :mw])
        if u_modes is not None:
            g = 1.0 + torch.tanh(self.mode_proj(u_modes[:, :, :mh, :mw]))
            low = low * g
            if high is not None:
                high = high * g
        out_ft[:, :, :mh, :mw] = low
        if high is not None:
            out_ft[:, :, -mh:, :mw] = high
        return torch.fft.irfft2(out_ft, s=(H, W), norm="ortho")


class SpatialFiLMNorm(nn.Module):
    """GroupNorm + global X-FiLM (always on) + optional spatial uncertainty FiLM.

    gamma = 1 + gamma_X(X) + gamma_U(G),  beta = beta_X(X) + beta_U(G)

    gamma_X/beta_X are the proven global per-channel modulation from the condition
    vector X (exactly mf_fno_transfer_film's FiLMNorm). gamma_U/beta_U add a NEW
    per-pixel term from the encoded uncertainty field G (Gate A). Both zero-init, so
    the block starts as the #1 model's FiLM block and grows the spatial gate.
    """

    def __init__(self, channels: int, cond_dim: int, gate_ch: int, cond_feat_dim: int = 64):
        super().__init__()
        self.channels = channels
        self.norm = nn.GroupNorm(min(8, channels), channels, affine=False)
        self.film_x = nn.Sequential(
            nn.Linear(cond_dim, cond_feat_dim), nn.GELU(),
            nn.Linear(cond_feat_dim, 2 * channels),
        )
        nn.init.zeros_(self.film_x[-1].weight)
        nn.init.zeros_(self.film_x[-1].bias)
        self.film_u = nn.Conv2d(gate_ch, 2 * channels, 1)
        nn.init.zeros_(self.film_u.weight)
        nn.init.zeros_(self.film_u.bias)

    def forward(self, z: torch.Tensor, cond: torch.Tensor, g: Optional[torch.Tensor]) -> torch.Tensor:
        B = z.shape[0]
        C = self.channels
        gx, bx = self.film_x(cond).chunk(2, dim=-1)
        gamma = 1.0 + gx.view(B, C, 1, 1)
        beta = bx.view(B, C, 1, 1)
        if g is not None:
            gu, bu = self.film_u(g).chunk(2, dim=1)
            gamma = gamma + gu
            beta = beta + bu
        return gamma * self.norm(z) + beta


class DGBlock(nn.Module):
    """GatedSpectralConv2d + 1x1 residual, then GELU(SpatialFiLMNorm(.))."""

    def __init__(self, channels: int, modes_h: int, modes_w: int, cond_dim: int,
                 gate_ch: int, cond_feat_dim: int = 64):
        super().__init__()
        self.spectral = GatedSpectralConv2d(channels, channels, modes_h, modes_w, gate_ch)
        self.w = nn.Conv2d(channels, channels, 1)
        self.norm = SpatialFiLMNorm(channels, cond_dim, gate_ch, cond_feat_dim=cond_feat_dim)

    def forward(self, x: torch.Tensor, cond: torch.Tensor, g: Optional[torch.Tensor],
                u_modes: Optional[torch.Tensor]) -> torch.Tensor:
        return F.gelu(self.norm(self.spectral(x, u_modes) + self.w(x), cond, g))


class DGTransferFNO(nn.Module):
    """(cond vector X, LF-uncertainty fields aug) -> HF field (B, H, W).

    The transfer backbone (mf_fno_transfer_film): input is the coordinate grid, X
    enters via the global FiLM term, and the network predicts the HF field directly
    (trained by LF-pretrain -> HF-finetune in smoke_eval.py). The uncertainty fields
    enter only through the zero-init Gates A/B, so at init this equals the #1 model.
    """

    def __init__(self, cond_dim: int, aug_ch: int = 5, gate_ch: int = 16,
                 hidden_channels: int = 64, n_blocks: int = 4, modes_h: int = 12,
                 modes_w: int = 12, grid: Grid = (64, 64), cond_feat_dim: int = 64,
                 gates: FrozenSet[str] = ALL_GATES):
        super().__init__()
        self.cond_dim = cond_dim
        self.aug_ch = aug_ch
        self.modes_h = max(1, modes_h)
        self.modes_w = max(1, modes_w)
        self.grid = (int(grid[0]), int(grid[1]))
        self.gates = frozenset(gates) & ALL_GATES

        self.u_encode = nn.Conv2d(aug_ch, gate_ch, 1)
        self.lift = nn.Conv2d(2, hidden_channels, 1)
        self.blocks = nn.ModuleList(
            DGBlock(hidden_channels, modes_h, modes_w, cond_dim, gate_ch, cond_feat_dim=cond_feat_dim)
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

    def forward(self, x: torch.Tensor, aug: torch.Tensor) -> torch.Tensor:
        B = x.shape[0]
        H, W = self.grid
        g_feat = self.u_encode(aug)
        g_spatial = g_feat if "A" in self.gates else None
        u_modes = None
        if "B" in self.gates:
            mh = min(self.modes_h, max(H // 2, 1))
            mw = min(self.modes_w, W // 2 + 1)
            u_modes = torch.fft.rfft2(g_feat, norm="ortho")[:, :, :mh, :mw].abs()
        z = self.lift(self.coord_grid.expand(B, 2, H, W))
        for blk in self.blocks:
            z = blk(z, x, g_spatial, u_modes)
        return self.proj(z).squeeze(1)


def param_count(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters())
