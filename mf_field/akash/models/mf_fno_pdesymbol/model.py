"""mf_fno_pdesymbol (B4) — condition on a learned PDE-identity embedding.

Each dataset (a distinct PDE family) gets a learned embedding vector e_pde
indexed by `dataset_name`. The FNO FiLMs on the CONCATENATION [X, e_pde] at every
block, so the same network can specialize per PDE while sharing a backbone. On a
SINGLE-dataset smoke run there is exactly one id, so e_pde is a single learned
bias vector — the value of this family is cross-dataset (a shared multi-PDE
operator), which we document; the single-dataset smoke just verifies the
plumbing and that adding the embedding does not hurt.

Implementation: a tiny `nn.Embedding` over PDE ids feeds the FiLM conditioning
vector; the spectral backbone is the frozen FiLM FNO2d, used with
cond_dim = X_dim + embed_dim and an `id` threaded into forward.

References: li2020fno (FNO backbone); perez2018film (FiLM); learned task/embedding
conditioning for multi-task operator learning.
"""
from __future__ import annotations

from typing import Tuple

import torch
import torch.nn as nn

import sys
from pathlib import Path

_AKASH = Path(__file__).resolve().parents[2]
if str(_AKASH) not in sys.path:
    sys.path.insert(0, str(_AKASH))

from common.backbone import FNO2d, param_count  # noqa: E402,F401

Grid = Tuple[int, int]


class PDESymbolFNO(nn.Module):
    """FNO that FiLMs on [X, pde_embed(id)].

    Wraps the frozen FNO2d: the conditioning vector handed to the backbone is the
    concatenation of the raw condition X and the learned PDE embedding selected by
    the integer dataset id. The backbone is unchanged (it FiLMs on whatever cond
    vector it receives), so this is a pure conditioning-SOURCE change.
    """

    def __init__(self, cond_dim: int, n_pdes: int = 16, embed_dim: int = 8,
                 hidden_channels: int = 64, n_blocks: int = 4,
                 modes_h: int = 12, modes_w: int = 12, grid: Grid = (64, 64),
                 cond_feat_dim: int = 64):
        super().__init__()
        self.cond_dim = cond_dim
        self.embed_dim = embed_dim
        self.pde_embed = nn.Embedding(n_pdes, embed_dim)
        nn.init.normal_(self.pde_embed.weight, std=0.02)
        self.backbone = FNO2d(cond_dim + embed_dim, hidden_channels=hidden_channels,
                              n_blocks=n_blocks, modes_h=modes_h, modes_w=modes_w,
                              grid=grid, cond_feat_dim=cond_feat_dim)

    def forward(self, x: torch.Tensor, pde_id: int = 0) -> torch.Tensor:
        B = x.shape[0]
        idx = torch.full((B,), int(pde_id), dtype=torch.long, device=x.device)
        e = self.pde_embed(idx)                      # (B, embed_dim)
        cond = torch.cat([x, e], dim=-1)             # FiLM on [X, e_pde]
        return self.backbone(cond)
