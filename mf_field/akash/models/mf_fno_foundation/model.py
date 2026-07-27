"""Cross-dataset foundation MF-FNO with a BPOM-style set-encoder.

The benchmark winner `mf_fno_transfer_film` FiLM-conditions an FNO directly on
the raw parameter vector X. That ties one trained network to ONE dataset, because
cond_dim varies across datasets (1..16) — a Linear(cond_dim, ...) cannot be shared.

This family decouples the conditioning from cond_dim with a BPOM-style
permutation-aware SET ENCODER (Branched/Bipartite-pooling-of-mappings, after
NITO/OAT, Nobari et al. 2024/2025): X's scalars are treated as a SET of tokens,
    token_i = MLP([ value_i , positional_embed(i) ]),
and aggregated with a concat(min, max, mean) pool over tokens -> a FIXED-width
embedding (default 64). Because the pooled embedding has the same width for ANY
cond_dim, a SINGLE shared FNO backbone (Poseidon-style cross-dataset pretrain,
Herde et al. 2024) can be FiLM-conditioned uniformly across every dataset.

The FNO backbone is byte-for-byte `common.backbone.FNO2d` EXCEPT its FiLM
conditioning width is the fixed BPOM embedding dim, not cond_dim. So:
  raw X (B, cond_dim)  --BPOM-->  emb (B, EMB)  --FiLM-->  field (B, H, W).

References: nobari2024nito, nobari2025oat (BPOM set encoding for variable-size
geometry/parameter inputs), herde2024poseidon (shared cross-PDE pretraining),
perez2018film (FiLM), li2020fno (FNO backbone).
"""
from __future__ import annotations

from typing import Tuple

import torch
import torch.nn as nn

from common.backbone import SpectralConv2d, FiLMNorm, param_count  # noqa: F401

Grid = Tuple[int, int]

EMB_DIM = 64            # fixed BPOM embedding width (shared across all datasets)
MAX_TOKENS = 32         # positional-embedding table size (>= any dataset cond_dim)
POS_DIM = 16            # positional-embedding width per token


class BPOMSetEncoder(nn.Module):
    """Map a variable-length parameter vector X to a FIXED-width embedding.

    X is treated as a SET of scalar tokens. token_i = MLP([value_i, pos_emb(i)]).
    The token features are aggregated with a permutation-aware concat(min,max,mean)
    pool, then projected to EMB_DIM. This makes the conditioning width independent
    of cond_dim, so one shared backbone serves every dataset.

    Positional embedding (a learned per-index table) keeps the encoder *aware* of
    which slot a value came from — parameter vectors are ordered, not a pure set,
    so this is "BPOM with positions" rather than a fully permutation-invariant
    DeepSet. The min/max/mean pool itself is permutation-invariant; positions
    re-inject slot identity.
    """

    def __init__(self, emb_dim: int = EMB_DIM, token_hidden: int = 64,
                 max_tokens: int = MAX_TOKENS, pos_dim: int = POS_DIM):
        super().__init__()
        self.emb_dim = emb_dim
        self.max_tokens = max_tokens
        self.pos = nn.Embedding(max_tokens, pos_dim)
        self.token_mlp = nn.Sequential(
            nn.Linear(1 + pos_dim, token_hidden),
            nn.GELU(),
            nn.Linear(token_hidden, token_hidden),
            nn.GELU(),
        )
        # concat(min,max,mean) -> 3 * token_hidden
        self.head = nn.Sequential(
            nn.Linear(3 * token_hidden, emb_dim),
            nn.GELU(),
            nn.Linear(emb_dim, emb_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, d) raw parameter vector
        B, d = x.shape
        d = min(d, self.max_tokens)
        x = x[:, :d]
        vals = x.unsqueeze(-1)                                   # (B, d, 1)
        idx = torch.arange(d, device=x.device)
        pos = self.pos(idx).unsqueeze(0).expand(B, d, -1)        # (B, d, pos_dim)
        tok = torch.cat([vals, pos], dim=-1)                     # (B, d, 1+pos_dim)
        feat = self.token_mlp(tok)                               # (B, d, H)
        pooled = torch.cat([feat.amin(1), feat.amax(1), feat.mean(1)], dim=-1)
        return self.head(pooled)                                 # (B, emb_dim)


class FNOBlockEmb(nn.Module):
    """FNO block FiLM-conditioned on the FIXED BPOM embedding (width = emb_dim)."""

    def __init__(self, channels: int, modes_h: int, modes_w: int, emb_dim: int,
                 cond_feat_dim: int = 64):
        super().__init__()
        self.spectral = SpectralConv2d(channels, channels, modes_h, modes_w)
        self.w = nn.Conv2d(channels, channels, 1)
        self.norm = FiLMNorm(channels, emb_dim, cond_feat_dim=cond_feat_dim)

    def forward(self, x: torch.Tensor, emb: torch.Tensor) -> torch.Tensor:
        import torch.nn.functional as F
        return F.gelu(self.norm(self.spectral(x) + self.w(x), emb))


class FoundationFNO2d(nn.Module):
    """BPOM-encoded, FiLM-conditioned, cross-dataset-shareable FNO.

    forward(X) : X (B, cond_dim) -> BPOM emb (B, EMB) -> field (B, H, W).

    The BPOM encoder + lift/blocks/proj are the SHARED, cond_dim-independent
    backbone (loadable from a foundation pretrain). Nothing here references
    cond_dim, so the same state_dict transfers across datasets.
    """

    def __init__(self, hidden_channels: int = 64, n_blocks: int = 4,
                 modes_h: int = 12, modes_w: int = 12, grid: Grid = (64, 64),
                 emb_dim: int = EMB_DIM, cond_feat_dim: int = 64):
        super().__init__()
        self.grid = (int(grid[0]), int(grid[1]))
        self.emb_dim = emb_dim
        self.encoder = BPOMSetEncoder(emb_dim=emb_dim)
        self.lift = nn.Conv2d(2, hidden_channels, 1)
        self.blocks = nn.ModuleList(
            FNOBlockEmb(hidden_channels, modes_h, modes_w, emb_dim, cond_feat_dim=cond_feat_dim)
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
        emb = self.encoder(x)                                    # (B, emb_dim)
        coords = self.coord_grid.expand(B, 2, H, W)
        z = self.lift(coords)
        for blk in self.blocks:
            z = blk(z, emb)
        return self.proj(z).squeeze(1)                           # (B, H, W)

    def shared_state_dict(self) -> dict:
        """state_dict of the cond_dim-independent shared backbone (no buffers).

        Identical key structure across datasets, so it can be saved by
        pretrain_all and reloaded into any dataset's instance.
        """
        return {k: v for k, v in self.state_dict().items() if k != "coord_grid"}
