# Adapted import plumbing only from models/paper/wno_transfer_film/model.py.
# Source SHA256: b0ce207bc6c1d2c32e59b82c5f5e3efb9ece18e7e0a53a88531b527a46c19d08
"""FiLM-conditioned single-level Wavelet Neural Operator (tripura2023wno), 1-D & rect safe.

This is the benchmark-winning FNO+FiLM-transfer backbone
(`factory_mffp/models/mf_fno_transfer_film/model.py` / `akash/common/backbone.py`)
with ONE change: the **Fourier** spectral convolution `SpectralConv2d` is replaced
by a **wavelet** convolution `WaveletConv2d`. Everything else — the FiLM
conditioning (`FiLMNorm`), the block composition `GELU(FiLMNorm(conv(x)+1x1(x), cond))`,
the coordinate-grid lift, the projection head, and the LF->HF transfer schedule
(smoke_eval.py) — is byte-for-byte the winner. This isolates the BACKBONE
(Fourier vs wavelet) while holding conditioning + schedule fixed.

WaveletConv2d (tripura2023wno §3, li2020fno structure)
-----------------------------------------------------
* A native, differentiable **1-level 2-D discrete wavelet transform** implemented
  in pure torch (NO pywt/ptwt/pytorch_wavelets) via periodic circular
  convolution + downsampling. Orthogonal **Daubechies db4** filters (Haar/db1
  fallback available). Analysis = correlation-downsample; synthesis =
  convolution-upsample with the SAME (non-reversed) decomposition filters, which
  gives PERFECT RECONSTRUCTION for the periodic orthonormal DWT (verified to
  ~1e-12 float64 / <1e-4 float32; see `dwt_recon_error`).
* 2-D DWT is SEPARABLE (filter along W then along H) -> 4 subbands LL,LH,HL,HH.
  **1-D-safe:** when H==1 the transform runs along W ONLY -> 2 subbands L,H (the
  exact class of bug that broke a prior model on sod_1d, grid (1,L)).
* ODD sizes: H and/or W are circularly padded up to even before the DWT and the
  reconstruction is cropped back afterwards.
* LEARNABLE MIXING mirrors FNO's per-mode complex weight, but REAL and in the
  wavelet domain: each subband owns a weight tensor `(in_ch, out_ch, m1, m2)`
  applied per coefficient position as `einsum("bixy,ioxy->boxy")` on the
  low-position block up to a mode cap (m1=min(cap,subH), m2=min(cap,subW)).
  Coefficient positions beyond the cap PASS THROUGH unchanged (in_ch==out_ch in
  every block) — pass-through rather than zeroing, because a wavelet coefficient
  index is a SPATIAL position, so zeroing it would spatially crop the subband
  (unlike FNO's frequency-domain truncation). The mixed subbands are inverse-DWT'd
  back to (B, out_ch, H, W).

Single-level WNO: the official tripura2023wno does a multi-level DWT and operates
on the coarsest level (zeroing finer details); we keep a single level for a clean,
provably-invertible native implementation. Documented as such.

References: tripura2023wno (WNO backbone, arXiv:2205.02191); li2020fno (FNO
structure the WNO mirrors); perez2018film (FiLM); lyu2023mffno (LF->HF transfer
schedule, retained in smoke_eval.py).
"""
from __future__ import annotations

from typing import Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

# The architecture below is preserved from the archived model.
from models.paper.mf_fno_transfer_film.model import FiLMNorm, param_count

Grid = Tuple[int, int]

# db4 (Daubechies-4) decomposition low-pass filter (8 taps).
DB4_DEC_LO = [-0.010597401784997278, 0.032883011666982945, 0.030841381835986965, -0.18703481171888114,
              -0.02798376941698385, 0.6308807679295904, 0.7148465705525415, 0.23037781330885523]
# Haar (db1) decomposition low-pass filter — analytic PR fallback.
HAAR_DEC_LO = [0.7071067811865476, 0.7071067811865476]


def wavelet_filters(name: str) -> Tuple[torch.Tensor, torch.Tensor]:
    """Return (dec_lo, dec_hi) as float tensors for the orthogonal filter bank.

    dec_hi[k] = (-1)**k * dec_lo[::-1][k]  (quadrature-mirror high-pass).
    Synthesis reuses these SAME filters (see idwt1d), which yields perfect
    reconstruction for the periodic orthonormal DWT with this analysis/synthesis
    convention.
    """
    taps = {"db4": DB4_DEC_LO, "haar": HAAR_DEC_LO}[name]
    dec_lo = torch.tensor(taps, dtype=torch.float32)
    dec_lo_rev = torch.flip(dec_lo, [0])
    k = torch.arange(dec_lo.numel(), dtype=torch.float32)
    dec_hi = ((-1.0) ** k) * dec_lo_rev
    return dec_lo, dec_hi


#   Periodic separable DWT/IDWT as DEPTHWISE conv2d directional filters.
#   Depthwise (groups=C) applies the SAME 1-D filter to every channel and
#   parallelizes over channels + batch — orders of magnitude faster on CPU than
#   a per-tap roll loop or a channel-collapsed conv1d. `along` selects the axis:
#   "w" -> kernel (1,L) over width, "h" -> kernel (L,1) over height.

def _dw_kernel(filt: torch.Tensor, C: int, along: str) -> torch.Tensor:
    L = filt.numel()
    k = filt.view(1, 1, 1, L) if along == "w" else filt.view(1, 1, L, 1)
    return k.expand(C, 1, *k.shape[2:]).contiguous()


def _down(x: torch.Tensor, filt: torch.Tensor, along: str) -> torch.Tensor:
    """Periodic correlation-downsample by 2 along one axis (analysis).

    a[n] = sum_k filt[k] * x[(2n + k) mod N]: right/bottom circular-pad by L-1,
    then stride-2 depthwise conv2d (cross-correlation).
    """
    C, L = x.shape[1], filt.numel()
    pad = (0, L - 1, 0, 0) if along == "w" else (0, 0, 0, L - 1)
    xp = F.pad(x, pad, mode="circular")
    stride = (1, 2) if along == "w" else (2, 1)
    return F.conv2d(xp, _dw_kernel(filt, C, along), stride=stride, groups=C)


def _up(a: torch.Tensor, filt: torch.Tensor, along: str, N: int) -> torch.Tensor:
    """Periodic upsample-convolution along one axis (synthesis).

    Upsample by 2 (zeros between samples), left/top circular-pad by L-1, then
    stride-1 depthwise conv2d with the REVERSED filter. Exact inverse of `_down`.
    """
    C, L = a.shape[1], filt.numel()
    if along == "w":
        A = torch.zeros(a.shape[0], C, a.shape[2], N, dtype=a.dtype, device=a.device)
        A[..., 0::2] = a
        pad = (L - 1, 0, 0, 0)
    else:
        A = torch.zeros(a.shape[0], C, N, a.shape[3], dtype=a.dtype, device=a.device)
        A[..., 0::2, :] = a
        pad = (0, 0, L - 1, 0)
    Ap = F.pad(A, pad, mode="circular")
    w = _dw_kernel(torch.flip(filt, [0]), C, along)
    return F.conv2d(Ap, w, stride=1, groups=C)


def _pad_even(x: torch.Tensor, dim: int) -> Tuple[torch.Tensor, int]:
    """Circularly pad `dim` up to an even length; return (padded, original_len)."""
    n = x.shape[dim]
    if n % 2 == 0:
        return x, n
    # replicate the last slice (recon is cropped back to n anyway).
    pad = x.index_select(dim, torch.tensor([n - 1], device=x.device))
    return torch.cat([x, pad], dim=dim), n


class WaveletConv2d(nn.Module):
    """1-level wavelet-domain channel/position mixing (WNO), 1-D (H==1) & rect safe.

    Mirrors SpectralConv2d's role (mix channels in a transform domain) but in the
    db4 wavelet domain with a per-coefficient-position weight up to a mode cap.
    """

    def __init__(self, in_ch: int, out_ch: int, modes_cap: int, grid: Grid,
                 wavelet: str = "db4"):
        super().__init__()
        assert in_ch == out_ch, "pass-through mixing requires in_ch == out_ch"
        self.in_ch, self.out_ch = in_ch, out_ch
        H, W = int(grid[0]), int(grid[1])
        self.is_1d = (H == 1)
        # even-padded working sizes and resulting subband sizes
        Hp = H if (H % 2 == 0 or H == 1) else H + 1
        Wp = W if W % 2 == 0 else W + 1
        subH = 1 if self.is_1d else max(Hp // 2, 1)
        subW = max(Wp // 2, 1)
        self.m1 = 1 if self.is_1d else min(int(modes_cap), subH)
        self.m2 = min(int(modes_cap), subW)

        dec_lo, dec_hi = wavelet_filters(wavelet)
        self.register_buffer("dec_lo", dec_lo)
        self.register_buffer("dec_hi", dec_hi)
        self.wavelet = wavelet

        scale = 1.0 / (in_ch * out_ch)
        # 2 subbands for 1-D (L,H), 4 for 2-D (LL,LH,HL,HH); each its own weight.
        n_sub = 2 if self.is_1d else 4
        self.weights = nn.ParameterList([
            nn.Parameter(scale * torch.randn(in_ch, out_ch, self.m1, self.m2))
            for _ in range(n_sub)
        ])

    # ── separable DWT / IDWT ──────────────────────────────────────────────
    def _dwt(self, x: torch.Tensor):
        lo, hi = self.dec_lo, self.dec_hi
        if self.is_1d:                                   # (B,C,1,W) -> L,H
            xp, w0 = _pad_even(x, -1)
            L = _down(xp, lo, "w"); Hh = _down(xp, hi, "w")
            return [L, Hh], (x.shape[-2], w0, xp.shape[-1])
        # 2-D separable: split along W, then split each along H
        xp, w0 = _pad_even(x, -1)
        xp, h0 = _pad_even(xp, -2)
        aL = _down(xp, lo, "w"); aH = _down(xp, hi, "w")        # split W
        LL = _down(aL, lo, "h"); HL = _down(aL, hi, "h")        # split H of L
        LH = _down(aH, lo, "h"); HH = _down(aH, hi, "h")        # split H of H
        return [LL, LH, HL, HH], (h0, w0, xp.shape[-2], xp.shape[-1])

    def _idwt(self, subs, meta):
        lo, hi = self.dec_lo, self.dec_hi
        if self.is_1d:
            _h, w0, Wp = meta
            L, Hh = subs
            x = _up(L, lo, "w", Wp) + _up(Hh, hi, "w", Wp)
            return x[..., :w0]
        h0, w0, Hp, Wp = meta
        LL, LH, HL, HH = subs
        aL = _up(LL, lo, "h", Hp) + _up(HL, hi, "h", Hp)        # merge H of L
        aH = _up(LH, lo, "h", Hp) + _up(HH, hi, "h", Hp)        # merge H of H
        x = _up(aL, lo, "w", Wp) + _up(aH, hi, "w", Wp)         # merge W
        return x[..., :h0, :w0]

    def _mix(self, sub: torch.Tensor, w: torch.Tensor) -> torch.Tensor:
        """Weight the low-position m1xm2 block; pass the rest through unchanged."""
        out = sub.clone()
        m1 = min(self.m1, sub.shape[-2]); m2 = min(self.m2, sub.shape[-1])
        out[..., :m1, :m2] = torch.einsum(
            "bixy,ioxy->boxy", sub[..., :m1, :m2], w[:, :, :m1, :m2])
        return out

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        subs, meta = self._dwt(x)
        mixed = [self._mix(s, w) for s, w in zip(subs, self.weights)]
        return self._idwt(mixed, meta)


class WNOBlock(nn.Module):
    """WNO block: GELU(FiLMNorm(WaveletConv2d(x) + 1x1(x), cond)).

    Mirrors FNOBlock exactly, swapping the spectral conv for the wavelet conv.
    """

    def __init__(self, channels: int, modes_cap: int, grid: Grid, cond_dim: int,
                 cond_feat_dim: int = 64, wavelet: str = "db4"):
        super().__init__()
        self.wavelet_conv = WaveletConv2d(channels, channels, modes_cap, grid, wavelet=wavelet)
        self.w = nn.Conv2d(channels, channels, 1)
        self.norm = FiLMNorm(channels, cond_dim, cond_feat_dim=cond_feat_dim)

    def forward(self, x: torch.Tensor, cond: torch.Tensor) -> torch.Tensor:
        return F.gelu(self.norm(self.wavelet_conv(x) + self.w(x), cond))


class WNO2d(nn.Module):
    """cond vector (B, cond_dim) -> field (B, H, W) on a fixed working grid.

    Identical to the FNO+FiLM winner (FNO2d) except each block uses WaveletConv2d.
    Input is the 2 coordinate channels only; X enters via FiLM at every block.
    """

    def __init__(self, cond_dim: int, hidden_channels: int = 64, n_blocks: int = 4,
                 modes_cap: int = 12, grid: Grid = (64, 64), cond_feat_dim: int = 64,
                 wavelet: str = "db4"):
        super().__init__()
        self.cond_dim = cond_dim
        self.grid = (int(grid[0]), int(grid[1]))
        self.wavelet = wavelet
        self.lift = nn.Conv2d(2, hidden_channels, 1)          # coordinates only
        self.blocks = nn.ModuleList(
            WNOBlock(hidden_channels, modes_cap, self.grid, cond_dim,
                     cond_feat_dim=cond_feat_dim, wavelet=wavelet)
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


def dwt_recon_error(wavelet: str = "db4", device=None) -> float:
    """Max DWT->IDWT reconstruction error over a 2-D and a 1-D probe tensor.

    Exercises BOTH code paths (H>1 rectangular and H==1). Used by smoke_eval to
    verify perfect reconstruction before training and to trigger the Haar fallback.
    """
    dev = device or torch.device("cpu")
    errs = []
    for grid, x in [((32, 48), torch.randn(2, 4, 32, 48, device=dev)),
                    ((1, 64), torch.randn(2, 4, 1, 64, device=dev))]:
        conv = WaveletConv2d(4, 4, 12, grid, wavelet=wavelet).to(dev)
        subs, meta = conv._dwt(x)
        xr = conv._idwt(subs, meta)                # no mixing -> must equal x
        errs.append(float((xr - x).abs().max()))
    return max(errs)
