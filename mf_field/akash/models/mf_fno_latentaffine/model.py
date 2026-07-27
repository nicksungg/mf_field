"""mf_fno_latentaffine (B1) — "HF ~= LF + constant latent direction" test.

Hypothesis
----------
Word2vec-style (mikolov2013word2vec): does moving from low- to high-fidelity
correspond to a SINGLE constant direction `delta` in a learned field-latent
space, the way "king - man + woman = queen" is a constant offset? If so, an HF
field can be synthesized as `decode(encode(LF) + delta)`.

Components
----------
* A small convolutional autoencoder over fields on the working grid. We try to
  REUSE the exported AE from `mf_fno_diffprior/ae.pt` (same ConvAE class,
  importable encode/decode); if it is missing / incompatible we build and train
  our own small AE here.
* A tiny base regressor `X -> z_lf` (an MLP on the condition vector) so that at
  eval, when only HF inputs X are available (the ifc test split is HF-only), we
  can still produce a prediction: z_lf_hat = base(X), then HF = decode(z_lf_hat +
  delta).

The REAL deliverable is the MEASUREMENT of whether the affine hypothesis holds:
`shift_direction_consistency` (mean pairwise cosine of bootstrapped per-fidelity
shift vectors + their relative std). A high cosine / low relative std means the
LF->HF map is well-approximated by one constant latent translation.

Inspired by: mikolov2013word2vec (constant semantic offset vectors),
rombach2022ldm (latent-space field modelling).
"""
from __future__ import annotations

from typing import Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

Grid = Tuple[int, int]


class ConvAE(nn.Module):
    """PDE-native conv AE: field (B,1,H,W) <-> flat latent z (B, zdim).

    Class-compatible with `mf_fno_diffprior.ConvAE` so the exported ae.pt loads
    directly. Encoder downsamples + adaptive-pools to a fixed (lh,lw) latent,
    flattens, linearly projects to zdim; decoder reverses.
    """

    def __init__(self, base_ch: int = 32, latent_ch: int = 16,
                 latent_hw: Tuple[int, int] = (4, 4), zdim: int = 64):
        super().__init__()
        self.latent_ch = latent_ch
        self.latent_hw = latent_hw
        self.zdim = zdim
        flat = latent_ch * latent_hw[0] * latent_hw[1]
        self.enc = nn.Sequential(
            nn.Conv2d(1, base_ch, 3, stride=2, padding=1), nn.GELU(),
            nn.Conv2d(base_ch, base_ch * 2, 3, stride=2, padding=1), nn.GELU(),
            nn.Conv2d(base_ch * 2, latent_ch, 3, stride=1, padding=1),
        )
        self.to_z = nn.Linear(flat, zdim)
        self.from_z = nn.Linear(zdim, flat)
        self.dec = nn.Sequential(
            nn.Conv2d(latent_ch, base_ch * 2, 3, stride=1, padding=1), nn.GELU(),
            nn.Conv2d(base_ch * 2, base_ch, 3, stride=1, padding=1), nn.GELU(),
            nn.Conv2d(base_ch, 1, 3, stride=1, padding=1),
        )

    def encode(self, field: torch.Tensor) -> torch.Tensor:
        if field.dim() == 3:
            field = field.unsqueeze(1)
        h = self.enc(field)
        h = F.adaptive_avg_pool2d(h, self.latent_hw)
        return self.to_z(h.flatten(1))

    def decode(self, z: torch.Tensor, grid: Tuple[int, int]) -> torch.Tensor:
        B = z.shape[0]
        h = self.from_z(z).view(B, self.latent_ch, *self.latent_hw)
        h = F.interpolate(h, size=grid, mode="bilinear", align_corners=False)
        return self.dec(h).squeeze(1)

    def forward(self, field: torch.Tensor, grid: Tuple[int, int]) -> torch.Tensor:
        return self.decode(self.encode(field), grid)


class BaseRegressor(nn.Module):
    """Tiny MLP: condition vector X -> LF latent z_lf (B, zdim).

    Used only on the HF-only test fallback path: predict z_lf from X, then add the
    constant latent shift delta and decode.
    """

    def __init__(self, cond_dim: int, zdim: int, hidden: int = 128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(cond_dim, hidden), nn.GELU(),
            nn.Linear(hidden, hidden), nn.GELU(),
            nn.Linear(hidden, zdim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


def param_count(*modules) -> int:
    return sum(p.numel() for m in modules for p in m.parameters())
