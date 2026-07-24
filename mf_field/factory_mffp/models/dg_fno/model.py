"""Discrepancy-Gated Fourier Neural Operator (DG-FNO).

Crosses the factory's two best fusion mechanisms. `mf_fno_transfer_film` has the
best *injection* (per-block FiLM modulation) but conditions on the global vector
`X`; `fno_fire_distcond` has the best *signal* (per-pixel LF uncertainty fields
mu/sigma/quantiles) but injects it by concatenation at the lift (FNO2dAug). DG-FNO
takes FIRE's uncertainty FIELD and modulates every spectral block with it, plus two
extensions that only an operator allows:

  Gate A — spatial FiLM: the GroupNorm affine (gamma,beta) gets a per-pixel term
           driven by the encoded uncertainty field G, in addition to the proven
           global X-FiLM term. (concat -> FiLM, but for the uncertainty field.)
  Gate B — spectral mode-gate: each retained Fourier mode of the delta-operator is
           scaled by a learned gain derived from the uncertainty's own spectrum, so
           the correction's spectral BANDWIDTH opens where LF error is high-frequency
           (shocks, boundaries) and stays shut where LF is smooth/trusted.
  Gate C — heteroscedastic gain field: HF = mu_LF + rho(x) * delta, rho(x) a learned
           spatial gain in [0, RHO_MAX] (a spatial generalization of the scalar rho
           in Kennedy & O'Hagan 2000 autoregressive co-kriging).

Every gate is ZERO-INIT (gamma_U=0, mode-gain=1, rho=1), so at initialization DG-FNO
is exactly an X-FiLM residual operator over the FIRE decomposition and can only grow
the gates from there. Gates are selectable (frozenset) so ablations are flag-flips.

The SpectralConv2d / coordinate-grid backbone is byte-for-byte the shared geometry
backbone (rectangular- and 1-D (H==1)-safe) used across the FNO families, so the
comparison isolates the gating MECHANISM, not the backbone.

References: li2020fno (FNO); perez2018film (FiLM); FIRE (Yu, Sung & Ahmed 2026,
arXiv:2601.22371; distribution-conditioned residual); kennedy2000ohagan (rho gain);
beggs2025pdecond (FiLM-via-norm).
"""
from __future__ import annotations

from typing import FrozenSet, Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

Grid = Tuple[int, int]
ALL_GATES: FrozenSet[str] = frozenset({"A", "B", "C"})
RHO_MAX = 2.0  # rho = RHO_MAX * sigmoid(.); zero-init head -> rho == 1.0 at start


def _mode_extent(H: int, W: int, modes_h: int, modes_w: int) -> Tuple[int, int]:
    """The (mh, mw) actually kept by the rfft2 backbone for this grid."""
    mh = min(max(1, modes_h), max(H // 2, 1))
    mw = min(max(1, modes_w), W // 2 + 1)
    return mh, mw


class GatedSpectralConv2d(nn.Module):
    """2D spectral conv (li2020fno §3) with an optional per-mode uncertainty gain.

    Identical to the shared SpectralConv2d, except the retained modes are scaled
    by g = 1 + tanh(mode_proj(U_modes)) when a uncertainty mode-spectrum is passed.
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
        # Gate B: maps the uncertainty mode-magnitudes (gate_ch) -> per-out-channel gain.
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
            # u_modes: (B, gate_ch, mh, mw) real magnitudes -> (B, out_ch, mh, mw) gain.
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

    gamma_X/beta_X are the proven per-channel global modulation from the condition
    vector X (as in mf_fno_transfer_film). gamma_U/beta_U are a NEW per-pixel term
    from the encoded uncertainty field G (Gate A). Both projections are zero-init,
    so the block starts as a plain GroupNorm FNO and grows modulation from there.
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
        # Gate A: per-pixel affine from the encoded uncertainty field.
        self.film_u = nn.Conv2d(gate_ch, 2 * channels, 1)
        nn.init.zeros_(self.film_u.weight)
        nn.init.zeros_(self.film_u.bias)

    def forward(self, z: torch.Tensor, cond: torch.Tensor, g: Optional[torch.Tensor]) -> torch.Tensor:
        B = z.shape[0]
        C = self.channels
        gx, bx = self.film_x(cond).chunk(2, dim=-1)         # each (B, C)
        gamma = 1.0 + gx.view(B, C, 1, 1)
        beta = bx.view(B, C, 1, 1)
        if g is not None:
            gu, bu = self.film_u(g).chunk(2, dim=1)          # each (B, C, H, W)
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


class DGOperator(nn.Module):
    """(cond vector X, uncertainty fields aug) -> (delta field, rho gain field).

    Input to the lift is the coordinate grid only — X enters via Gate A's global
    FiLM, the uncertainty fields via the shared encoder G and the gates. The caller
    forms HF = mu_LF + rho * delta (Gate C); rho == 1 everywhere at init.
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
        self.gates = frozenset(gates)

        # Shared uncertainty encoder -> G (B, gate_ch, H, W), used by all gates.
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
        # Gate C: rho(x) = RHO_MAX * sigmoid(rho_head(G)); zero-init -> rho == 1.0.
        self.rho_head = nn.Conv2d(gate_ch, 1, 1)
        nn.init.zeros_(self.rho_head.weight)
        nn.init.zeros_(self.rho_head.bias)

        H, W = self.grid
        ys = torch.linspace(-1.0, 1.0, H)
        xs = torch.linspace(-1.0, 1.0, W)
        gy, gx = torch.meshgrid(ys, xs, indexing="ij")
        self.register_buffer("coord_grid", torch.stack([gy, gx], dim=0).unsqueeze(0))

    def forward(self, x: torch.Tensor, aug: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        B = x.shape[0]
        H, W = self.grid

        g_feat = self.u_encode(aug)                                   # (B, gate_ch, H, W)
        g_spatial = g_feat if "A" in self.gates else None             # Gate A signal

        u_modes = None
        if "B" in self.gates:                                          # Gate B mode-spectrum
            mh, mw = _mode_extent(H, W, self.modes_h, self.modes_w)
            g_ft = torch.fft.rfft2(g_feat, norm="ortho")
            u_modes = g_ft[:, :, :mh, :mw].abs()                      # (B, gate_ch, mh, mw)

        z = self.lift(self.coord_grid.expand(B, 2, H, W))
        for blk in self.blocks:
            z = blk(z, x, g_spatial, u_modes)
        delta = self.proj(z).squeeze(1)                               # (B, H, W)

        if "C" in self.gates:
            rho = RHO_MAX * torch.sigmoid(self.rho_head(g_feat)).squeeze(1)
        else:
            rho = torch.ones_like(delta)
        return delta, rho


def param_count(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters())
