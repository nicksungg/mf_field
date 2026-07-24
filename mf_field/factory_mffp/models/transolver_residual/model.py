"""
Transolver backbone (slice attention) trained as a hard multi-fidelity residual.

HF_pred(x) = LF_interp(x) + transolver_delta(x | LF_context, cond)

Differences from v9_baseline:
  - The LF interpolation is the "prior" — fixed, not learned. v9 learned a soft prior.
  - There is no per-stream gating: only one LF stream is used as the base, and
    the model strictly learns the additive correction the LF doesn't account for.
  - delta_mlp is zero-init so training starts at the pure LF-interp baseline.
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

    def forward(self, coords: torch.Tensor) -> torch.Tensor:
        if self.num_freqs == 0:
            return coords.new_zeros(coords.shape[:-1] + (0,))
        x = coords.unsqueeze(-1) * self.freqs
        pe = torch.cat([x.sin(), x.cos()], dim=-1)
        return pe.flatten(-2)


def _mlp(in_dim, hidden_dim, out_dim, num_hidden=2, act=nn.GELU) -> nn.Sequential:
    layers = [nn.Linear(in_dim, hidden_dim), act()]
    for _ in range(num_hidden - 1):
        layers += [nn.Linear(hidden_dim, hidden_dim), act()]
    layers.append(nn.Linear(hidden_dim, out_dim))
    return nn.Sequential(*layers)


def lf_interp_at_query(lf_tokens: torch.Tensor, hf_coords: torch.Tensor,
                       gamma: float = 4.0) -> torch.Tensor:
    """
    Soft-nearest-neighbor interpolation of the LF field at HF query coords.
    lf_tokens: [B, M, 3 + cond_dim + 1] — last dim contains the LF value.
    hf_coords: [B, N, 3]
    Returns: [B, N, 1] interpolated LF values at the HF query coords.
    """
    lf_coords = lf_tokens[..., :3]
    lf_vals = lf_tokens[..., -1:]
    dist2 = torch.cdist(hf_coords, lf_coords, p=2.0).pow(2)
    w = F.softmax(-gamma * dist2, dim=-1)
    return torch.einsum("bnm,bmd->bnd", w, lf_vals)


class TransolverResidual(nn.Module):
    def __init__(self, cond_dim: int = 23, hidden_dim: int = 192,
                 n_slices: int = 32, num_heads: int = 6,
                 encoder_layers: int = 2, residual_layers: int = 3,
                 pos_enc_freqs: int = 6, interp_gamma: float = 4.0):
        super().__init__()
        assert hidden_dim % num_heads == 0
        self.hidden_dim = hidden_dim
        self.num_heads = num_heads
        self.head_dim = hidden_dim // num_heads
        self.n_slices = n_slices
        self.interp_gamma = interp_gamma

        self.pos_enc = SinusoidalPE(coord_dim=3, num_freqs=pos_enc_freqs)
        pe_dim = self.pos_enc.out_dim

        # HF input = coords + cond + interp(LF) + pos_enc
        hf_in = 3 + cond_dim + 1 + pe_dim
        lf_in = 3 + cond_dim + 1 + pe_dim
        self.hf_encoder = _mlp(hf_in, hidden_dim, hidden_dim, num_hidden=encoder_layers)
        self.lf_encoder = _mlp(lf_in, hidden_dim, hidden_dim, num_hidden=encoder_layers)
        self.hf_ln = nn.LayerNorm(hidden_dim)
        self.lf_ln = nn.LayerNorm(hidden_dim)

        # Self-slice attention on HF (Transolver-style)
        self.self_slice_proj = nn.Linear(hidden_dim, n_slices)
        self.self_v_proj = nn.Linear(hidden_dim, hidden_dim)
        self.self_q = nn.Linear(hidden_dim, hidden_dim, bias=False)
        self.self_k = nn.Linear(hidden_dim, hidden_dim, bias=False)
        self.self_v = nn.Linear(hidden_dim, hidden_dim, bias=False)
        self.self_o = nn.Linear(hidden_dim, hidden_dim)
        self.self_ln = nn.LayerNorm(hidden_dim)

        # Cross-slice attention from HF queries -> LF slices
        self.cross_slice_proj = nn.Linear(hidden_dim, n_slices)
        self.cross_v_proj = nn.Linear(hidden_dim, hidden_dim)
        self.cross_q = nn.Linear(hidden_dim, hidden_dim, bias=False)
        self.cross_k = nn.Linear(hidden_dim, hidden_dim, bias=False)
        self.cross_v = nn.Linear(hidden_dim, hidden_dim, bias=False)
        self.cross_o = nn.Linear(hidden_dim, hidden_dim)
        self.cross_ln = nn.LayerNorm(hidden_dim)

        # Residual head — predicts the additive delta to LF interpolation
        self.delta_mlp = _mlp(2 * hidden_dim, hidden_dim, 1, num_hidden=residual_layers)
        nn.init.zeros_(self.delta_mlp[-1].weight)
        nn.init.zeros_(self.delta_mlp[-1].bias)

        self._init_weights()

    def _init_weights(self):
        for name, m in self.named_modules():
            if isinstance(m, nn.Linear) and "delta_mlp" not in name:
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    nn.init.zeros_(m.bias)

    def _mha(self, Q, K, V):
        scale = math.sqrt(self.head_dim)
        logits = torch.einsum("bhnd,bhkd->bhnk", Q, K) / scale
        attn = F.softmax(logits, dim=-1)
        return torch.einsum("bhnk,bhkd->bhnd", attn, V)

    def _split_heads(self, x):
        B, L, _ = x.shape
        return x.reshape(B, L, self.num_heads, self.head_dim).transpose(1, 2)

    def forward(self, list_of_lf_tokens: List[torch.Tensor], hf_tokens: torch.Tensor,
                return_components: bool = False):
        if isinstance(list_of_lf_tokens, torch.Tensor):
            list_of_lf_tokens = [list_of_lf_tokens]
        if len(list_of_lf_tokens) == 0:
            raise ValueError("Need at least one LF stream")
        # Use only the highest-resolution LF stream (the last one in fid order) as the base.
        lf_tokens = list_of_lf_tokens[-1]

        B, N, _ = hf_tokens.shape
        hf_coords = hf_tokens[..., :3]

        # Hard residual base: interpolate LF values at the HF query coords.
        lf_interp = lf_interp_at_query(lf_tokens, hf_coords, gamma=self.interp_gamma)

        # HF features: coords + cond + lf_interp (so the network knows where LF was uncertain)
        hf_pe = self.pos_enc(hf_coords)
        hf_in = torch.cat([hf_tokens, lf_interp, hf_pe], dim=-1)
        hf_feat = self.hf_ln(self.hf_encoder(hf_in))

        # LF features for cross attention
        lf_coords = lf_tokens[..., :3]
        lf_pe = self.pos_enc(lf_coords)
        lf_in = torch.cat([lf_tokens, lf_pe], dim=-1)
        lf_feat = self.lf_ln(self.lf_encoder(lf_in))

        # Self slice-attention on HF tokens (Transolver pattern)
        self_sw = F.softmax(self.self_slice_proj(hf_feat), dim=1)
        self_keys = torch.einsum("bnk,bnd->bkd", self_sw, hf_feat)
        self_vals = torch.einsum("bnk,bnd->bkd", self_sw, self.self_v_proj(hf_feat))
        Q = self._split_heads(self.self_q(hf_feat))
        K = self._split_heads(self.self_k(self_keys))
        V = self._split_heads(self.self_v(self_vals))
        ctx_self = self._mha(Q, K, V).transpose(1, 2).reshape(B, N, self.hidden_dim)
        ctx_self = self.self_ln(self.self_o(ctx_self))

        # Cross slice-attention HF -> LF slices
        cross_sw = F.softmax(self.cross_slice_proj(lf_feat), dim=1)
        cross_keys = torch.einsum("bmk,bmd->bkd", cross_sw, lf_feat)
        cross_vals = torch.einsum("bmk,bmd->bkd", cross_sw, self.cross_v_proj(lf_feat))
        Q = self._split_heads(self.cross_q(hf_feat))
        K = self._split_heads(self.cross_k(cross_keys))
        V = self._split_heads(self.cross_v(cross_vals))
        ctx_cross = self._mha(Q, K, V).transpose(1, 2).reshape(B, N, self.hidden_dim)
        ctx_cross = self.cross_ln(self.cross_o(ctx_cross))

        # Combine self + cross, predict additive delta to LF interpolation
        delta_in = torch.cat([ctx_self, ctx_cross], dim=-1)
        delta = self.delta_mlp(delta_in)
        pred = lf_interp + delta

        if return_components:
            return {"pred": pred, "lf_interp": lf_interp, "delta": delta}
        return pred


def param_count(model: nn.Module) -> tuple[int, int]:
    total = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    return trainable, total


__all__ = ["TransolverResidual", "SinusoidalPE", "param_count", "lf_interp_at_query"]
