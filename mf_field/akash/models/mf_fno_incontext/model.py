"""mf_fno_incontext (B2) — in-context operator learning (no fine-tune).

A DeepSets encoder summarizes a few support pairs (X_i, Y_i) into a task context
vector c; the FNO then FiLMs on [X_query, c] to predict the query field. There is
NO gradient fine-tuning at the target fidelity: adaptation happens purely
in-context, the way a sequence model conditions on a prompt of examples.

Training is EPISODIC on the abundant LF data: each step samples a random support
subset and a disjoint query subset from LF, builds c from the support, and
supervises the query predictions. At eval the HF TRAIN pairs become the support
(the "prompt") and the HF TEST inputs are the queries — the network transfers to
HF by reading HF examples in-context, never updating its weights on HF.

References: li2020fno (FNO backbone); perez2018film (FiLM); zaheer2017deepsets
(permutation-invariant set encoder); in-context / few-shot operator learning.
"""
from __future__ import annotations

from typing import Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

import sys
from pathlib import Path

_AKASH = Path(__file__).resolve().parents[2]
if str(_AKASH) not in sys.path:
    sys.path.insert(0, str(_AKASH))

from common.backbone import FNO2d, param_count  # noqa: E402,F401

Grid = Tuple[int, int]

SUMMARY_DIM = 4  # cheap permutation-invariant field summary per support field


def field_summary(Y_bhw: torch.Tensor) -> torch.Tensor:
    """(S,H,W) -> (S, SUMMARY_DIM): mean, std, min, max of each support field."""
    f = Y_bhw.flatten(1)
    return torch.stack([f.mean(1), f.std(1), f.amin(1), f.amax(1)], dim=-1)


class DeepSetsContext(nn.Module):
    """Permutation-invariant support encoder -> task context c (ctx_dim)."""

    def __init__(self, elem_dim: int, hidden: int = 64, ctx_dim: int = 16):
        super().__init__()
        self.ctx_dim = ctx_dim
        self.phi = nn.Sequential(
            nn.Linear(elem_dim, hidden), nn.GELU(),
            nn.Linear(hidden, hidden), nn.GELU(),
        )
        self.rho = nn.Sequential(
            nn.Linear(hidden, hidden), nn.GELU(),
            nn.Linear(hidden, ctx_dim),
        )

    def forward(self, support: torch.Tensor) -> torch.Tensor:
        # support: (S, elem_dim) -> mean-pool over S -> (ctx_dim,)
        if support.shape[0] == 0:
            return torch.zeros(self.ctx_dim, device=support.device)
        h = self.phi(support).mean(dim=0)
        return self.rho(h)


class InContextFNO(nn.Module):
    """FNO that FiLMs on [X_query, context]; context comes from support pairs."""

    def __init__(self, cond_dim: int, ctx_dim: int = 16,
                 hidden_channels: int = 64, n_blocks: int = 4,
                 modes_h: int = 12, modes_w: int = 12, grid: Grid = (64, 64),
                 cond_feat_dim: int = 64):
        super().__init__()
        self.cond_dim = cond_dim
        self.ctx_dim = ctx_dim
        self.backbone = FNO2d(cond_dim + ctx_dim, hidden_channels=hidden_channels,
                              n_blocks=n_blocks, modes_h=modes_h, modes_w=modes_w,
                              grid=grid, cond_feat_dim=cond_feat_dim)

    def forward(self, x: torch.Tensor, context: torch.Tensor) -> torch.Tensor:
        B = x.shape[0]
        c = context.view(1, -1).expand(B, self.ctx_dim)
        cond = torch.cat([x, c], dim=-1)
        return self.backbone(cond)
