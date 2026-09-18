"""NOMAD — nonlinear-manifold-decoder DeepONet operator (seidman2022nomad).

A DeepONet-style operator map  X (parameter vector)  ->  field on a fixed
working grid.  Built from scratch in PyTorch (no deepxde).

Two decoder modes, selectable via `decoder`:

  * "nonlinear" (NOMAD, the shipped model)
        D(beta, y) = MLP( concat[ beta_broadcast_to_each_coord , coord_feats(y) ] )
        The latent code `beta` (from the branch net) is TILED to every coordinate
        and concatenated with that coordinate's features, then a shared MLP maps
        (latent + 2) -> 1 scalar per point.  This is the NONLINEAR manifold
        decoder of Seidman et al. 2022 (arXiv:2206.03551): the reconstruction is
        a nonlinear function of the latent code, which breaks the linear
        Kolmogorov-n-width bottleneck of the classical DeepONet.

  * "linear" (the built-in DeepONet CONTROL, lu2021deeponet)
        trunk = MLP(coord_feats(y)) -> (P, latent)
        u = einsum("bl,pl->bp", beta, trunk)
        The standard LINEAR DeepONet reconstruction: u is a linear combination of
        the trunk basis with branch coefficients.  Ships one flag away so the
        experiment isolates ONLY the linear-vs-nonlinear decoder (identical
        branch net, coord features, latent width, and MF transfer schedule).

Multi-fidelity behaviour lives entirely in the training schedule (LF-pretrain ->
HF-finetune, see smoke_eval.py), mirroring the benchmark winner
`mf_fno_transfer_film`; the network itself is single-fidelity.

1-D safe: the working grid may be (1, L); coord features and the (H*W)-point
decoder handle a height-1 grid transparently.  Memory: the decoder is evaluated
in CHUNKS along the coordinate axis so era5's ~128x256 = 32768 coords x batch
stays bounded.

References: seidman2022nomad (nonlinear manifold decoder); lu2021deeponet
(DeepONet / linear control); lyu2023mffno (LF->HF transfer schedule).
"""
from __future__ import annotations

from typing import Tuple

import torch
import torch.nn as nn

Grid = Tuple[int, int]


def _mlp(sizes, act=nn.GELU):
    """Plain MLP over the given layer widths (act between hidden layers)."""
    layers = []
    for i in range(len(sizes) - 1):
        layers.append(nn.Linear(sizes[i], sizes[i + 1]))
        if i < len(sizes) - 2:
            layers.append(act())
    return nn.Sequential(*layers)


class NomadMF(nn.Module):
    """cond vector (B, cond_dim) -> field (B, H, W) on a fixed working grid.

    branch : cond_dim -> 256 -> 256 -> latent_dim   (GELU)   => beta
    coords : fixed (H*W, 2) meshgrid in [-1, 1]      (buffer)
    decoder:
      nonlinear -> MLP(latent_dim + 2 -> 256 -> 256 -> 1) applied per coord
      linear    -> trunk MLP(2 -> 256 -> 256 -> latent_dim); u = beta . trunk
    """

    def __init__(self, cond_dim: int, grid: Grid = (64, 64), latent_dim: int = 128,
                 branch_hidden: int = 256, decoder_hidden: int = 256,
                 decoder: str = "nonlinear", coord_chunk: int = 8192):
        super().__init__()
        if decoder not in ("nonlinear", "linear"):
            raise ValueError(f"decoder must be 'nonlinear' or 'linear', got {decoder!r}")
        self.cond_dim = int(cond_dim)
        self.grid = (int(grid[0]), int(grid[1]))
        self.latent_dim = int(latent_dim)
        self.decoder = decoder
        self.coord_chunk = int(coord_chunk)
        self.coord_feat_dim = 2  # raw (y, x) coordinates in [-1, 1]

        # Branch net: parameter vector -> latent code beta.
        self.branch = _mlp([self.cond_dim, branch_hidden, branch_hidden, self.latent_dim])

        if decoder == "nonlinear":
            # Nonlinear manifold decoder: (beta_tiled, coord_feats) -> scalar.
            self.dec = _mlp([self.latent_dim + self.coord_feat_dim,
                             decoder_hidden, decoder_hidden, 1])
        else:
            # Linear DeepONet trunk: coord_feats -> latent basis.
            self.trunk = _mlp([self.coord_feat_dim, decoder_hidden,
                               decoder_hidden, self.latent_dim])

        # Fixed working-grid coordinates as (H*W, 2), row-major (H then W).
        H, W = self.grid
        ys = torch.linspace(-1.0, 1.0, H)
        xs = torch.linspace(-1.0, 1.0, W)
        gy, gx = torch.meshgrid(ys, xs, indexing="ij")
        coords = torch.stack([gy, gx], dim=-1).reshape(H * W, 2)  # (P, 2)
        self.register_buffer("coords", coords)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B = x.shape[0]
        H, W = self.grid
        P = H * W
        beta = self.branch(x)                          # (B, latent)
        coords = self.coords                           # (P, 2)

        out = torch.empty(B, P, device=x.device, dtype=beta.dtype)
        step = max(1, self.coord_chunk)
        for s in range(0, P, step):
            e = min(s + step, P)
            cf = coords[s:e]                           # (Pc, 2)
            Pc = cf.shape[0]
            if self.decoder == "nonlinear":
                # tile beta to each coord, concat coord feats -> shared MLP -> scalar
                beta_t = beta.unsqueeze(1).expand(B, Pc, self.latent_dim)     # (B,Pc,L)
                cf_t = cf.unsqueeze(0).expand(B, Pc, self.coord_feat_dim)     # (B,Pc,2)
                inp = torch.cat([beta_t, cf_t], dim=-1)                       # (B,Pc,L+2)
                out[:, s:e] = self.dec(inp).squeeze(-1)                       # (B,Pc)
            else:
                trunk = self.trunk(cf)                                        # (Pc, L)
                out[:, s:e] = torch.einsum("bl,pl->bp", beta, trunk)          # (B,Pc)
        return out.reshape(B, H, W)


def param_count(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters())
