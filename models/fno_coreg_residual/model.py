"""H3: FNO backbone + MFRNP residual stack (decoder-in-the-aggregation) +
continuous-m coregionalization basis-head on the HF prediction.

Clean re-derivation from source papers — NOT copied from existing families:
  - li2020fno         : Fourier Neural Operator spectral convolution.
  - niu2024mfrnp      : Multi-fidelity residual neural processes — each
                        per-fidelity FNO is paired with a small decoder that
                        produces a decoded LF prediction; an aggregator MLP
                        consumes upsampled decoded LFs (decoder-in-the-
                        aggregation) and emits an HF baseline.
  - li2022ifc         : Continuous-fidelity coregionalization. A basis head
                        on the HF latent: y_HF = agg(x) + sum_k B_k(m) h_k(x)
                        with B(m) = MLP_B([m, m^2]).
  - xing2020deepcoreg : Empirical precedent for composing a low-rank basis
                        on top of an MF residual — same conceptual compose,
                        coarser (GP backbone, single-fidelity basis).

Final HF prediction in normalized space:
    y_HF_normalized(x, m) = agg(x, m) + sum_{k=1..K} B_k(m) * h_k(x)
where h(x) is the L4 (HF) FNO latent projected to K channels at 64x64,
and agg is the MFRNP aggregator over upsampled decoded LFs and m.

The basis-head MLP_B's last linear is zero-initialised so B(m) starts at
0 and the architecture begins as pure-H2-style aggregator. Optimisation
then decides how large to make the basis contribution.

Per-fidelity output normalisation: predict y / scaler[m] where
scaler[m] = max(|y|) over training samples at fidelity m. The scaler
buffer is set externally via set_scaler after the train/val split so it
reflects only the training subset.
"""
from __future__ import annotations

from typing import Dict, List

import torch
import torch.nn as nn
import torch.nn.functional as F


# ---------- spectral conv (li2020fno) ----------

class SpectralConv2d(nn.Module):
    """rfft2 -> keep lowest (modes_h, modes_w) modes in the +kx and -kx
    corners (multiplied by independent complex weights) -> irfft2."""

    def __init__(self, in_ch: int, out_ch: int, modes_h: int, modes_w: int):
        super().__init__()
        self.in_ch = in_ch
        self.out_ch = out_ch
        self.modes_h = modes_h
        self.modes_w = modes_w
        scale = 1.0 / (in_ch * out_ch)
        self.w_pos = nn.Parameter(
            scale * torch.randn(in_ch, out_ch, modes_h, modes_w, dtype=torch.cfloat)
        )
        self.w_neg = nn.Parameter(
            scale * torch.randn(in_ch, out_ch, modes_h, modes_w, dtype=torch.cfloat)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, _, H, W = x.shape
        mh = min(self.modes_h, max(H // 2, 1))
        mw = min(self.modes_w, W // 2 + 1)
        x_ft = torch.fft.rfft2(x, dim=(-2, -1), norm="ortho")
        out_ft = torch.zeros(
            B, self.out_ch, H, W // 2 + 1,
            dtype=torch.cfloat, device=x.device,
        )
        if mh > 0 and mw > 0:
            out_ft[:, :, :mh, :mw] = torch.einsum(
                "bchw,cohw->bohw",
                x_ft[:, :, :mh, :mw], self.w_pos[:, :, :mh, :mw],
            )
            if H >= 2 * mh:
                out_ft[:, :, -mh:, :mw] = torch.einsum(
                    "bchw,cohw->bohw",
                    x_ft[:, :, -mh:, :mw], self.w_neg[:, :, :mh, :mw],
                )
        return torch.fft.irfft2(out_ft, s=(H, W), dim=(-2, -1), norm="ortho")


class FNOBlock(nn.Module):
    def __init__(self, channels: int, modes_h: int, modes_w: int):
        super().__init__()
        self.spec = SpectralConv2d(channels, channels, modes_h, modes_w)
        self.w = nn.Conv2d(channels, channels, 1)
        self.norm = nn.GroupNorm(min(8, channels), channels)
        self.act = nn.GELU()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.act(self.norm(self.spec(x) + self.w(x)))


class FNOBackbone(nn.Module):
    """Lift -> n FNO blocks -> returns the channel-rich latent grid (no projection).

    The latent (B, hidden, R, R) is consumed by:
      - a small decoder to produce a 1-channel decoded prediction (for LF
        levels and the aggregator anchor), and
      - the basis-head projection (HF only) to produce h(x) with K channels.
    """

    def __init__(self, in_ch: int, hidden: int, modes_h: int, modes_w: int, n_blocks: int):
        super().__init__()
        self.lift = nn.Conv2d(in_ch, hidden, 1)
        self.blocks = nn.ModuleList(
            FNOBlock(hidden, modes_h, modes_w) for _ in range(n_blocks)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        z = self.lift(x)
        for blk in self.blocks:
            z = blk(z)
        return z


class FieldDecoder(nn.Module):
    """Small 1x1-conv decoder from a (B, hidden, R, R) latent to a 1-channel
    field at the same resolution. niu2024mfrnp's published hidden_dim=32."""

    def __init__(self, hidden_in: int, hidden_dec: int = 32):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(hidden_in, hidden_dec, 1),
            nn.GELU(),
            nn.Conv2d(hidden_dec, hidden_dec, 1),
            nn.GELU(),
            nn.Conv2d(hidden_dec, 1, 1),
        )

    def forward(self, z: torch.Tensor) -> torch.Tensor:
        return self.net(z)


# ---------- MFRNP-style aggregator (decoder-in-the-aggregation) ----------

class MFRNPAggregator(nn.Module):
    """Pointwise MLP fusing [decoded_LFs_upsampled_to_HF, m_broadcast] -> agg(x).

    Threads continuous m as a 4th input channel at every spatial location
    (matches niu2024mfrnp's continuous-m side-input pattern). Output is
    one channel at HF resolution = the LF-aggregate field used both as
    the aggregator anchor target and as the offset that the basis-head's
    residual is added on top of.
    """

    def __init__(self, n_lf: int, hidden: int = 32):
        super().__init__()
        self.c1 = nn.Conv2d(n_lf + 1, hidden, 1)
        self.c2 = nn.Conv2d(hidden, hidden, 1)
        self.c3 = nn.Conv2d(hidden, 1, 1)
        self.act = nn.GELU()

    def forward(self, lf_stack: torch.Tensor, m_value: torch.Tensor) -> torch.Tensor:
        B, _, H, W = lf_stack.shape
        m_b = m_value.view(B, 1, 1, 1).expand(-1, 1, H, W)
        x = torch.cat([lf_stack, m_b], dim=1)
        x = self.act(self.c1(x))
        x = self.act(self.c2(x))
        return self.c3(x)  # (B, 1, H, W)


# ---------- continuous-m basis head (li2022ifc, on top of HF latent) ----------

class BasisHead(nn.Module):
    """B(m) = MLP_B([m, m^2]) -> R^K. Cheap MLP — NOT a neural ODE.

    Last layer is zero-initialised so B(m) starts at the zero vector;
    architecture initially behaves as the pure MFRNP aggregator output.
    """

    def __init__(self, K: int, hidden: int = 64):
        super().__init__()
        self.lin1 = nn.Linear(2, hidden)
        self.lin2 = nn.Linear(hidden, hidden)
        self.lin3 = nn.Linear(hidden, K)
        self.act = nn.GELU()
        nn.init.zeros_(self.lin3.weight)
        nn.init.zeros_(self.lin3.bias)

    def forward(self, m: torch.Tensor) -> torch.Tensor:
        feat = torch.stack([m, m * m], dim=-1)
        h = self.act(self.lin1(feat))
        h = self.act(self.lin2(h))
        return self.lin3(h)  # (B, K)


# ---------- full model ----------

class FNOCoregResidual(nn.Module):
    """4 per-fidelity FNOs with decoders + MFRNP aggregator + HF basis head.

    native_resolutions: e.g. (8, 16, 32, 64).
    modes_per_level:    e.g. (4, 8, 12, 12) at full config (capped by Nyquist).
    hidden:             channels in each per-fidelity FNO (full config = 64).
    decoder_hidden:     channels in each per-fidelity decoder (default 32, MFRNP-published).
    K:                  number of basis-head channels on the HF latent (default 10).
    n_blocks:           spectral conv blocks per FNO (default 3).
    """

    def __init__(
        self,
        cond_dim: int,
        native_resolutions: List[int] = (8, 16, 32, 64),
        modes_per_level: List[int] = (4, 8, 12, 12),
        hidden: int = 64,
        decoder_hidden: int = 32,
        K: int = 10,
        n_blocks: int = 3,
        b_hidden: int = 64,
        hf_res: int = 64,
    ):
        super().__init__()
        self.cond_dim = cond_dim
        self.native_resolutions = list(native_resolutions)
        self.modes_per_level = list(modes_per_level)
        self.n_levels = len(self.native_resolutions)
        assert self.n_levels >= 2
        self.hf_res = hf_res
        self.K = K
        self.hidden = hidden

        in_ch = cond_dim + 2  # X (broadcast) + 2 coordinate channels

        # Per-fidelity FNOs, each at its native resolution.
        self.fnos = nn.ModuleList([
            FNOBackbone(
                in_ch=in_ch, hidden=hidden,
                modes_h=modes_per_level[k], modes_w=modes_per_level[k],
                n_blocks=n_blocks,
            )
            for k in range(self.n_levels)
        ])
        # One decoder per fidelity (decoder-in-the-aggregation, MFRNP).
        self.decoders = nn.ModuleList([
            FieldDecoder(hidden_in=hidden, hidden_dec=decoder_hidden)
            for _ in range(self.n_levels)
        ])
        # MFRNP-style aggregator: n_levels-1 decoded LFs + m -> HF baseline.
        self.aggregator = MFRNPAggregator(n_lf=self.n_levels - 1, hidden=decoder_hidden)
        # HF latent -> K-channel basis grid h(x).
        self.h_proj = nn.Sequential(
            nn.Conv2d(hidden, hidden, 1),
            nn.GELU(),
            nn.Conv2d(hidden, K, 1),
        )
        # B(m): R -> R^K (zero-initialised last layer).
        self.basis = BasisHead(K=K, hidden=b_hidden)

        # Per-level scaler buffer (filled via set_scaler after train/val split).
        self.register_buffer("scaler", torch.ones(self.n_levels), persistent=True)

    # --- scaler bookkeeping ---

    def set_scaler(self, scaler_dict: Dict[int, float]):
        s = torch.ones(self.n_levels)
        for k, v in scaler_dict.items():
            s[k] = float(v)
        self.scaler = s.to(self.scaler.device)

    # --- helpers ---

    @staticmethod
    def _coord_grid(res: int, device, dtype):
        ys = torch.linspace(-1.0, 1.0, res, device=device, dtype=dtype)
        xs = torch.linspace(-1.0, 1.0, res, device=device, dtype=dtype)
        gy, gx = torch.meshgrid(ys, xs, indexing="ij")
        return torch.stack([gy, gx], dim=0)  # (2, res, res)

    def _input_grid(self, X: torch.Tensor, res: int) -> torch.Tensor:
        B = X.shape[0]
        grid = self._coord_grid(res, X.device, X.dtype).unsqueeze(0).expand(B, -1, -1, -1)
        X_grid = X.view(B, -1, 1, 1).expand(-1, -1, res, res)
        return torch.cat([X_grid, grid], dim=1)

    # --- per-level forward (LF supervision path) ---

    def lf_decoded_native(self, X: torch.Tensor, level_idx: int) -> torch.Tensor:
        """(B, R_k, R_k) normalised LF prediction at native resolution."""
        R = self.native_resolutions[level_idx]
        z = self.fnos[level_idx](self._input_grid(X, R))
        return self.decoders[level_idx](z).squeeze(1)

    # --- HF residual + basis head ---

    def hf_predict(self, X: torch.Tensor, m_value: torch.Tensor) -> Dict[str, torch.Tensor]:
        """Returns normalised HF prediction and intermediate fields.

        agg(x, m)      : MFRNP aggregator over decoded LFs (HF resolution).
        basis_residual : sum_k B_k(m) * h_k(x), where h(x) is the L4 latent
                         projected to K channels.
        pred           : agg + basis_residual (still in normalised space).
        lf_decoded_native: list of native-res LF decoded fields (for the
                         per-level direct LF loss).
        """
        B = X.shape[0]
        R_hf = self.hf_res

        # 1) decode LFs at native, upsample to HF
        lf_decoded_native: List[torch.Tensor] = []
        lf_decoded_up: List[torch.Tensor] = []
        for k in range(self.n_levels - 1):
            R_k = self.native_resolutions[k]
            z_k = self.fnos[k](self._input_grid(X, R_k))
            d_k = self.decoders[k](z_k)  # (B, 1, R_k, R_k)
            lf_decoded_native.append(d_k.squeeze(1))
            lf_decoded_up.append(
                F.interpolate(d_k, size=(R_hf, R_hf), mode="bilinear", align_corners=False)
            )
        lf_stack = torch.cat(lf_decoded_up, dim=1)  # (B, n_lf, R_hf, R_hf)
        agg = self.aggregator(lf_stack, m_value).squeeze(1)  # (B, R_hf, R_hf)

        # 2) HF latent -> h(x) (K channels at HF res)
        z_hf = self.fnos[self.n_levels - 1](self._input_grid(X, R_hf))
        h = self.h_proj(z_hf)  # (B, K, R_hf, R_hf)

        # 3) basis-head residual
        Bm = self.basis(m_value)  # (B, K)
        residual = (Bm.view(B, self.K, 1, 1) * h).sum(dim=1)  # (B, R_hf, R_hf)

        return {
            "agg": agg,
            "basis_residual": residual,
            "pred": agg + residual,
            "lf_decoded_native": lf_decoded_native,
            "h": h,
        }


def param_count(model: nn.Module):
    total = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    return trainable, total
