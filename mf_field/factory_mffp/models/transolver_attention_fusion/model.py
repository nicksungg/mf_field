"""
Transolver backbone with iterated cross-fidelity attention as the fusion
mechanism. N stacked blocks of (self-slice attention -> cross-fidelity slice
attention) refine the HF representation against the LF context.

Differences from sibling families:
  - v9_baseline:        soft gated fusion of multiple LF streams (gate MLP)
  - transolver_residual: hard residual on top of LF interpolation
  - this:               pure attention fusion, multiple refinement blocks
"""
from __future__ import annotations

import math
from typing import List

import torch
import torch.nn as nn
import torch.nn.functional as F


class SinusoidalPE(nn.Module):
    def __init__(self, coord_dim: int = 3, num_freqs: int = 6):
        super().__init__()
        self.coord_dim = coord_dim
        self.num_freqs = num_freqs
        self.out_dim = coord_dim * num_freqs * 2
        if num_freqs > 0:
            freqs = 2.0 ** torch.arange(num_freqs).float() * math.pi
            self.register_buffer("freqs", freqs)

    def forward(self, coords):
        if self.num_freqs == 0:
            return coords.new_zeros(coords.shape[:-1] + (0,))
        x = coords.unsqueeze(-1) * self.freqs
        pe = torch.cat([x.sin(), x.cos()], dim=-1)
        return pe.flatten(-2)


def _mlp(in_dim, hidden_dim, out_dim, num_hidden=2, act=nn.GELU):
    layers = [nn.Linear(in_dim, hidden_dim), act()]
    for _ in range(num_hidden - 1):
        layers += [nn.Linear(hidden_dim, hidden_dim), act()]
    layers.append(nn.Linear(hidden_dim, out_dim))
    return nn.Sequential(*layers)


class SliceAttentionBlock(nn.Module):
    """One Transolver-style slice attention block, generic over (query, kv) sources."""

    def __init__(self, hidden_dim, n_slices, num_heads):
        super().__init__()
        assert hidden_dim % num_heads == 0
        self.h = num_heads
        self.dh = hidden_dim // num_heads
        self.slice_proj = nn.Linear(hidden_dim, n_slices)
        self.v_proj = nn.Linear(hidden_dim, hidden_dim)
        self.q = nn.Linear(hidden_dim, hidden_dim, bias=False)
        self.k = nn.Linear(hidden_dim, hidden_dim, bias=False)
        self.v = nn.Linear(hidden_dim, hidden_dim, bias=False)
        self.o = nn.Linear(hidden_dim, hidden_dim)
        self.ln = nn.LayerNorm(hidden_dim)
        self.ffn = _mlp(hidden_dim, 2 * hidden_dim, hidden_dim, num_hidden=1)
        self.ln_ffn = nn.LayerNorm(hidden_dim)

    def _split(self, x):
        B, L, _ = x.shape
        return x.reshape(B, L, self.h, self.dh).transpose(1, 2)

    def forward(self, q_feat, kv_feat):
        # Compute slice weights on the KV source and project to slice keys/values
        sw = F.softmax(self.slice_proj(kv_feat), dim=1)
        keys = torch.einsum("bnk,bnd->bkd", sw, kv_feat)
        vals = torch.einsum("bnk,bnd->bkd", sw, self.v_proj(kv_feat))
        Q = self._split(self.q(q_feat))
        K = self._split(self.k(keys))
        V = self._split(self.v(vals))
        scale = math.sqrt(self.dh)
        logits = torch.einsum("bhnd,bhkd->bhnk", Q, K) / scale
        attn = F.softmax(logits, dim=-1)
        ctx = torch.einsum("bhnk,bhkd->bhnd", attn, V).transpose(1, 2)
        ctx = ctx.reshape(q_feat.size(0), q_feat.size(1), self.h * self.dh)
        x = self.ln(q_feat + self.o(ctx))
        x = self.ln_ffn(x + self.ffn(x))
        return x


class TransolverAttentionFusion(nn.Module):
    def __init__(self, cond_dim: int = 23, hidden_dim: int = 192,
                 n_slices: int = 32, num_heads: int = 6,
                 encoder_layers: int = 2, n_fusion_blocks: int = 3,
                 pos_enc_freqs: int = 6):
        super().__init__()
        self.hidden_dim = hidden_dim

        self.pos_enc = SinusoidalPE(coord_dim=3, num_freqs=pos_enc_freqs)
        pe_dim = self.pos_enc.out_dim

        # HF tokens: coords + cond + PE
        hf_in = 3 + cond_dim + pe_dim
        # LF tokens: coords + cond + value + PE
        lf_in = 3 + cond_dim + 1 + pe_dim
        self.hf_encoder = _mlp(hf_in, hidden_dim, hidden_dim, num_hidden=encoder_layers)
        self.lf_encoder = _mlp(lf_in, hidden_dim, hidden_dim, num_hidden=encoder_layers)
        self.hf_ln = nn.LayerNorm(hidden_dim)
        self.lf_ln = nn.LayerNorm(hidden_dim)

        # n_fusion_blocks × (self-slice-attn on HF, then cross-slice-attn HF->LF)
        self.self_blocks = nn.ModuleList(
            [SliceAttentionBlock(hidden_dim, n_slices, num_heads) for _ in range(n_fusion_blocks)]
        )
        self.cross_blocks = nn.ModuleList(
            [SliceAttentionBlock(hidden_dim, n_slices, num_heads) for _ in range(n_fusion_blocks)]
        )

        self.head = _mlp(hidden_dim, hidden_dim, 1, num_hidden=2)
        nn.init.zeros_(self.head[-1].weight)
        nn.init.zeros_(self.head[-1].bias)
        self._init_weights()

    def _init_weights(self):
        for name, m in self.named_modules():
            if isinstance(m, nn.Linear) and "head" not in name:
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    nn.init.zeros_(m.bias)

    def forward(self, list_of_lf_tokens: List[torch.Tensor], hf_tokens: torch.Tensor,
                return_components: bool = False):
        if isinstance(list_of_lf_tokens, torch.Tensor):
            list_of_lf_tokens = [list_of_lf_tokens]
        if not list_of_lf_tokens:
            raise ValueError("Need at least one LF stream")
        lf_tokens = list_of_lf_tokens[-1]  # use highest LF resolution

        hf_pe = self.pos_enc(hf_tokens[..., :3])
        hf_feat = self.hf_ln(self.hf_encoder(torch.cat([hf_tokens, hf_pe], dim=-1)))

        lf_pe = self.pos_enc(lf_tokens[..., :3])
        lf_feat = self.lf_ln(self.lf_encoder(torch.cat([lf_tokens, lf_pe], dim=-1)))

        # Alternate self-attention on HF and cross-attention HF<-LF
        for self_blk, cross_blk in zip(self.self_blocks, self.cross_blocks):
            hf_feat = self_blk(hf_feat, hf_feat)
            hf_feat = cross_blk(hf_feat, lf_feat)

        pred = self.head(hf_feat)
        if return_components:
            return {"pred": pred, "hf_feat": hf_feat}
        return pred


def param_count(model: nn.Module):
    total = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    return trainable, total


__all__ = ["TransolverAttentionFusion", "SinusoidalPE", "param_count"]
