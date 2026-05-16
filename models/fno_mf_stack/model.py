"""FNO + MFRNP-style residual stacking, implemented from scratch.

Architecture (per spec H2):
  - 4 SmallFNOs, one per fidelity level k ∈ {L1=8, L2=16, L3=32, L4=64 (HF)}.
  - Each FNO operates at its native resolution. The input X (B, cond_dim) is
    broadcast as constant channels onto a (cond_dim, R, R) tensor, concatenated
    with sin/cos positional grid coords.
  - LF FNOs (L1..L3) predict the normalized output y/scaler at native res.
  - The MFRNP aggregator is an MLP that takes [decoded_L1_up, decoded_L2_up,
    decoded_L3_up, m_broadcast] (4 channels at 64×64) and predicts a baseline.
  - The HF (L4) FNO takes [X_grid, sin/cos coords, baseline] (cond_dim + 3
    channels at 64×64) and predicts the *residual* delta. Final HF prediction
    in normalized space = baseline + delta. De-normalize with scaler[L4] at
    inference.

Spectral conv weights are learned from scratch following li2020fno
(two-corner formulation: weights1 for low-kx, weights2 for high-kx, both at
low-ky modes of the rfft output).
"""
from __future__ import annotations

import math
from typing import Dict, List

import torch
import torch.nn as nn
import torch.nn.functional as F


# ---------- spectral conv (li2020fno) ----------

class SpectralConv2d(nn.Module):
    """2D spectral convolution. Multiplies rfft2 output by learned weights
    at the lowest (modes1, modes2) modes in both the +kx and -kx corners.
    """

    def __init__(self, in_ch: int, out_ch: int, modes1: int, modes2: int):
        super().__init__()
        self.in_ch = in_ch
        self.out_ch = out_ch
        self.modes1 = modes1  # along H (kx, two-sided)
        self.modes2 = modes2  # along W (ky, one-sided via rfft)
        scale = 1.0 / (in_ch * out_ch)
        self.w_pos = nn.Parameter(
            scale * torch.randn(in_ch, out_ch, modes1, modes2, dtype=torch.cfloat)
        )
        self.w_neg = nn.Parameter(
            scale * torch.randn(in_ch, out_ch, modes1, modes2, dtype=torch.cfloat)
        )

    @staticmethod
    def _compl_mul2d(x: torch.Tensor, w: torch.Tensor) -> torch.Tensor:
        # x: (B, in_ch, m1, m2) complex; w: (in_ch, out_ch, m1, m2) complex
        return torch.einsum("bixy,ioxy->boxy", x, w)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, in_ch, H, W) real
        B, C, H, W = x.shape
        m1 = min(self.modes1, H // 2 + 1, H - 1) if H > 1 else 0
        m2 = min(self.modes2, W // 2 + 1)
        x_ft = torch.fft.rfft2(x, dim=(-2, -1))  # (B, in_ch, H, W//2+1) cfloat
        out_ft = torch.zeros(
            B, self.out_ch, H, W // 2 + 1,
            dtype=torch.cfloat, device=x.device,
        )
        if m1 > 0 and m2 > 0:
            # +kx corner (low rows)
            mm1 = min(m1, self.modes1)
            mm2 = min(m2, self.modes2)
            out_ft[:, :, :mm1, :mm2] = self._compl_mul2d(
                x_ft[:, :, :mm1, :mm2], self.w_pos[:, :, :mm1, :mm2]
            )
            # -kx corner (high rows; only if H > 2*mm1 — else collides with low rows)
            if H >= 2 * mm1 and mm1 > 0:
                out_ft[:, :, -mm1:, :mm2] = self._compl_mul2d(
                    x_ft[:, :, -mm1:, :mm2], self.w_neg[:, :, :mm1, :mm2]
                )
        return torch.fft.irfft2(out_ft, s=(H, W), dim=(-2, -1))


class FNOBlock(nn.Module):
    def __init__(self, channels: int, modes1: int, modes2: int):
        super().__init__()
        self.spec = SpectralConv2d(channels, channels, modes1, modes2)
        self.w = nn.Conv2d(channels, channels, kernel_size=1)
        self.act = nn.GELU()

    def forward(self, x):
        return self.act(self.spec(x) + self.w(x))


class SmallFNO(nn.Module):
    def __init__(self, in_ch: int, out_ch: int, hidden: int,
                 modes1: int, modes2: int, n_blocks: int = 2):
        super().__init__()
        self.lift = nn.Conv2d(in_ch, hidden, kernel_size=1)
        self.blocks = nn.ModuleList([
            FNOBlock(hidden, modes1, modes2) for _ in range(n_blocks)
        ])
        self.proj1 = nn.Conv2d(hidden, hidden, kernel_size=1)
        self.act = nn.GELU()
        self.proj2 = nn.Conv2d(hidden, out_ch, kernel_size=1)

    def forward(self, x):
        x = self.lift(x)
        for blk in self.blocks:
            x = blk(x)
        x = self.proj2(self.act(self.proj1(x)))
        return x


# ---------- MFRNP-style aggregator (decoder-in-the-aggregation) ----------

class MFRNPAggregator(nn.Module):
    """Pointwise MLP fusing [decoded_LF_preds_up | m_broadcast] -> baseline_hf."""

    def __init__(self, n_lf: int, hidden: int = 16):
        super().__init__()
        self.c1 = nn.Conv2d(n_lf + 1, hidden, kernel_size=1)
        self.c2 = nn.Conv2d(hidden, hidden, kernel_size=1)
        self.c3 = nn.Conv2d(hidden, 1, kernel_size=1)
        self.act = nn.GELU()

    def forward(self, lf_stack: torch.Tensor, m_value: torch.Tensor) -> torch.Tensor:
        # lf_stack: (B, n_lf, H, W); m_value: (B,) float
        B, _, H, W = lf_stack.shape
        m_b = m_value.view(B, 1, 1, 1).expand(-1, 1, H, W)
        x = torch.cat([lf_stack, m_b], dim=1)
        x = self.act(self.c1(x))
        x = self.act(self.c2(x))
        return self.c3(x)  # (B, 1, H, W)


# ---------- the full model ----------

class FNOMFStack(nn.Module):
    """4 small FNOs + MFRNP aggregator + HF residual head.

    native_resolutions: e.g. [8, 16, 32, 64].
    modes_per_level:    e.g. [4, 5, 5, 5] (capped by Nyquist).
    hidden:             channels in each FNO.
    cond_dim:           dim of conditioning vector X (3 for heat, 5 for poisson).
    """

    def __init__(self,
                 cond_dim: int,
                 native_resolutions: List[int] = (8, 16, 32, 64),
                 modes_per_level: List[int] = (4, 5, 5, 5),
                 hidden: int = 16,
                 agg_hidden: int = 16,
                 n_blocks: int = 2,
                 hf_res: int = 64):
        super().__init__()
        self.cond_dim = cond_dim
        self.native_resolutions = list(native_resolutions)
        self.modes_per_level = list(modes_per_level)
        self.hf_res = hf_res
        self.n_levels = len(native_resolutions)
        assert self.n_levels >= 2

        # 4 FNOs. LF FNOs take (cond_dim + 2) channels (X + sin/cos grid).
        # HF FNO takes (cond_dim + 2 + 1) channels (+ baseline channel).
        in_ch_lf = cond_dim + 2
        in_ch_hf = cond_dim + 2 + 1
        self.lf_fnos = nn.ModuleList([
            SmallFNO(in_ch_lf, 1, hidden, modes_per_level[k], modes_per_level[k], n_blocks=n_blocks)
            for k in range(self.n_levels - 1)
        ])
        self.hf_fno = SmallFNO(
            in_ch_hf, 1, hidden, modes_per_level[-1], modes_per_level[-1], n_blocks=n_blocks
        )
        self.aggregator = MFRNPAggregator(n_lf=self.n_levels - 1, hidden=agg_hidden)

        # per-level y-scaler. Registered as buffer so .to(device) moves it.
        self.register_buffer("scaler", torch.ones(self.n_levels), persistent=True)

    def set_scaler(self, scaler_dict: Dict[int, float]):
        s = torch.ones(self.n_levels)
        for k, v in scaler_dict.items():
            s[k] = float(v)
        self.scaler = s.to(self.scaler.device)

    @staticmethod
    def _grid(res: int, device, dtype):
        # sin/cos positional encoding for x and y at one frequency each.
        # Shape (2, R, R), values in [-1, 1].
        ys = torch.linspace(0.0, 1.0, res, device=device, dtype=dtype)
        xs = torch.linspace(0.0, 1.0, res, device=device, dtype=dtype)
        gy, gx = torch.meshgrid(ys, xs, indexing="ij")
        # use (2x-1, 2y-1) so it sits centered on 0
        return torch.stack([2 * gx - 1, 2 * gy - 1], dim=0)  # (2, R, R)

    def _make_input(self, X: torch.Tensor, res: int, extra: torch.Tensor = None) -> torch.Tensor:
        # X: (B, cond_dim). extra: (B, 1, res, res) or None.
        B = X.shape[0]
        grid = self._grid(res, X.device, X.dtype).unsqueeze(0).expand(B, -1, -1, -1)  # (B, 2, R, R)
        X_grid = X.view(B, -1, 1, 1).expand(-1, -1, res, res)  # (B, cond_dim, R, R)
        if extra is None:
            return torch.cat([X_grid, grid], dim=1)
        return torch.cat([X_grid, grid, extra], dim=1)

    # --- LF prediction at a single level (native resolution) ---
    def lf_predict_native(self, X: torch.Tensor, level_idx: int) -> torch.Tensor:
        """Returns (B, R_k, R_k) NORMALIZED prediction at native res of level_idx."""
        assert 0 <= level_idx < self.n_levels - 1
        R = self.native_resolutions[level_idx]
        inp = self._make_input(X, R)
        return self.lf_fnos[level_idx](inp).squeeze(1)

    # --- HF prediction (residual stack) ---
    def hf_predict(self, X: torch.Tensor, m_value: torch.Tensor) -> Dict[str, torch.Tensor]:
        """Run all LF FNOs at their native resolutions, upsample to HF, aggregate,
        and add the HF residual delta. All outputs are in NORMALIZED space.

        Returns dict with:
          'baseline': (B, R_hf, R_hf)
          'delta':    (B, R_hf, R_hf)
          'pred':     (B, R_hf, R_hf) = baseline + delta
          'lf_preds_native': list of (B, R_k, R_k) normalized LF preds
        """
        B = X.shape[0]
        R_hf = self.hf_res
        lf_preds_native = []
        lf_preds_up = []
        for k in range(self.n_levels - 1):
            R_k = self.native_resolutions[k]
            inp_k = self._make_input(X, R_k)
            pk = self.lf_fnos[k](inp_k)  # (B, 1, R_k, R_k) normalized
            lf_preds_native.append(pk.squeeze(1))
            pk_up = F.interpolate(pk, size=(R_hf, R_hf), mode="bilinear", align_corners=False)
            lf_preds_up.append(pk_up)
        lf_stack = torch.cat(lf_preds_up, dim=1)  # (B, n_lf, R_hf, R_hf)
        baseline = self.aggregator(lf_stack, m_value).squeeze(1)  # (B, R_hf, R_hf)

        hf_inp = self._make_input(X, R_hf, extra=baseline.unsqueeze(1))
        delta = self.hf_fno(hf_inp).squeeze(1)  # (B, R_hf, R_hf)
        return {
            "baseline": baseline,
            "delta": delta,
            "pred": baseline + delta,
            "lf_preds_native": lf_preds_native,
        }


def param_count(model: nn.Module):
    total = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    return trainable, total
