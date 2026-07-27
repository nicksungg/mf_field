"""Hyper-/meta-conditioned FiLM-FNO: generalize the conditioning SOURCE.

The benchmark winner `mf_fno_transfer_film` FiLMs each block on the raw
per-sample condition vector `X` alone. Here we widen the conditioning vector to

    cond = [X, c, f]

  - X : the per-sample raw condition vector (cond_dim = d), exactly as the winner.
  - c : a permutation-invariant DeepSets task-context descriptor (perez2018film +
        finn2017maml / zintgraf2019cavia style task embedding) computed ONCE from
        a support set of (X_i, field_summary(Y_i)) pairs. The SAME c is reused for
        every query at eval time — it is a task-level descriptor, not per-sample.
        DeepSets: per-element shared MLP -> mean+max pool -> small projection.
  - f : a scalar normalized fidelity index (LF stage = 0.0, HF stage = 1.0),
        letting one network span fidelities (herde2024poseidon-style fidelity
        conditioning) instead of relying purely on the transfer schedule.

`use_context` / `use_fidelity` flags zero out c and/or f so the model reduces to
the FiLM-on-X winner (the --null ablation must match the winner's ballpark).

References: perez2018film (FiLM), finn2017maml + zintgraf2019cavia (task context /
context vectors for fast adaptation), herde2024poseidon (multi-operator / fidelity
conditioning), li2020fno (FNO backbone, imported from common.backbone).
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Tuple

import torch
import torch.nn as nn

AKASH = Path(__file__).resolve().parents[2]
if str(AKASH) not in sys.path:
    sys.path.insert(0, str(AKASH))

from common.backbone import FNOBlock, param_count  # noqa: E402,F401

Grid = Tuple[int, int]


class DeepSetsContext(nn.Module):
    """Permutation-invariant task-context encoder over a support set.

    Each support element is feat_i = concat(X_i, field_summary(Y_i)). A shared
    MLP encodes each element; mean + max pooling over the set gives an
    order-invariant task descriptor, projected to `ctx_dim`. (DeepSets;
    zaheer2017deepsets — used here as the finn2017maml task-context source.)
    """

    def __init__(self, elem_dim: int, hidden: int = 64, ctx_dim: int = 16):
        super().__init__()
        self.ctx_dim = ctx_dim
        self.enc = nn.Sequential(
            nn.Linear(elem_dim, hidden), nn.GELU(),
            nn.Linear(hidden, hidden), nn.GELU(),
        )
        self.proj = nn.Sequential(
            nn.Linear(2 * hidden, hidden), nn.GELU(),
            nn.Linear(hidden, ctx_dim),
        )

    def forward(self, support: torch.Tensor) -> torch.Tensor:
        """support: (S, elem_dim) -> context (ctx_dim,)."""
        h = self.enc(support)              # (S, hidden)
        pooled = torch.cat([h.mean(0), h.amax(0)], dim=-1)  # (2*hidden,)
        return self.proj(pooled)           # (ctx_dim,)


def field_summary(field: torch.Tensor, ds: int = 8) -> torch.Tensor:
    """Small fixed descriptor of a field on the working grid.

    field: (N, H, W) -> (N, ds*ds + 5): an 8x8 adaptive-avgpool downsample
    flattened, concatenated with [mean, std, min, max, L2] global stats.
    Purely a fixed (non-learned) descriptor fed into the DeepSets encoder.
    """
    N = field.shape[0]
    small = nn.functional.adaptive_avg_pool2d(field.unsqueeze(1), (ds, ds))
    small = small.reshape(N, ds * ds)
    flat = field.reshape(N, -1)
    stats = torch.stack([
        flat.mean(1), flat.std(1),
        flat.amin(1), flat.amax(1),
        flat.norm(dim=1),
    ], dim=-1)                              # (N, 5)
    return torch.cat([small, stats], dim=-1)


SUMMARY_DIM = 8 * 8 + 5  # field_summary output width (ds=8)


class HyperFiLM_FNO2d(nn.Module):
    """FiLM-FNO whose blocks condition on [X, c, f].

    Mirrors common.backbone.FNO2d (coords-only input, FiLM at every block) but
    the FiLM cond vector is widened to d + ctx_dim + 1. The context c and
    fidelity f are supplied at forward time (broadcast over the batch) so a
    single instance can be driven with c=0 / f=0 (the --null reduction) or with
    the real task context and fidelity scalar.
    """

    def __init__(self, cond_dim: int, hidden_channels: int = 64, n_blocks: int = 4,
                 modes_h: int = 12, modes_w: int = 12, grid: Grid = (64, 64),
                 cond_feat_dim: int = 64, ctx_dim: int = 16,
                 use_context: bool = True, use_fidelity: bool = True):
        super().__init__()
        self.cond_dim = int(cond_dim)
        self.ctx_dim = int(ctx_dim)
        self.use_context = bool(use_context)
        self.use_fidelity = bool(use_fidelity)
        self.grid = (int(grid[0]), int(grid[1]))
        film_cond_dim = self.cond_dim + self.ctx_dim + 1  # [X, c, f]

        self.lift = nn.Conv2d(2, hidden_channels, 1)
        self.blocks = nn.ModuleList(
            FNOBlock(hidden_channels, modes_h, modes_w, film_cond_dim,
                     cond_feat_dim=cond_feat_dim)
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

    def build_cond(self, x: torch.Tensor, context: torch.Tensor | None,
                   fidelity: float) -> torch.Tensor:
        """Assemble the (B, d+ctx_dim+1) FiLM cond from X, c, f (with flags)."""
        B = x.shape[0]
        dev = x.device
        if self.use_context and context is not None:
            c = context.to(dev).view(1, self.ctx_dim).expand(B, self.ctx_dim)
        else:
            c = torch.zeros(B, self.ctx_dim, device=dev, dtype=x.dtype)
        if self.use_fidelity:
            f = torch.full((B, 1), float(fidelity), device=dev, dtype=x.dtype)
        else:
            f = torch.zeros(B, 1, device=dev, dtype=x.dtype)
        return torch.cat([x, c, f], dim=-1)

    def forward(self, x: torch.Tensor, context: torch.Tensor | None = None,
                fidelity: float = 0.0) -> torch.Tensor:
        B = x.shape[0]
        H, W = self.grid
        cond = self.build_cond(x, context, fidelity)
        coords = self.coord_grid.expand(B, 2, H, W)
        z = self.lift(coords)
        for blk in self.blocks:
            z = blk(z, cond)
        return self.proj(z).squeeze(1)  # (B, H, W)
