"""
model_v3.py  —  Multi-Fidelity Transolver (MFTransolver)

Architecture
------------
Two input encoders:
  LF_Encoder   : processes 2-D "physics-context" tokens
                   input = [x, y=0, z, cond_1..cond_C, C_{p,LF}]
                   dim   = 3 + C + 1 = C + 4
  HF_Encoder   : processes 3-D query tokens
                   input = [x, y, z, cond_1..cond_C]
                   dim   = 3 + C     = C + 3

Cross-Fidelity Slice Attention (Transolver "Slice-and-Basis"):
  1. Assign each LF token a soft weight over K physical slices
       slice_weights  : (B, M, K) = softmax(W_slice(lf_feat), dim=1)
  2. Aggregate the K slice bases from LF features (einsum, memory-efficient)
       slice_keys     : (B, K, D)  = einsum('bmk, bmd -> bkd', w, lf_feat)
       slice_vals     : (B, K, D)  = einsum('bmk, bmd -> bkd', w, v_proj(lf_feat))
  3. HF queries attend to the K LF-derived slice bases
       Q : (B, N, H, dh)   K/V : (B, K, H, dh)   → (B, N, H, dh)
       (multi-head, using einsum throughout)

Residual Head:
  prior    = linear(attended_lf)        → (B, N, 1)   decoded from LF slices
  residual = MLP(attended_lf + hf_feat) → (B, N, 1)   3-D correction
  ŷ        = prior + residual

Sinusoidal Positional Encoding:
  Added to coord-derived features for both LF and HF tokens (placeholder —
  disable by passing pos_enc_freqs=0).

Usage
-----
  from model_v3 import MFTransolver
  model = MFTransolver(cond_dim=23)
  out   = model(lf_tokens, hf_tokens)   # (B, N, 1)
"""

import math
import torch
import torch.nn as nn
import torch.nn.functional as F


# ─────────────────────────────────────────────────────────────────────────────
# Sinusoidal Positional Encoding helper
# ─────────────────────────────────────────────────────────────────────────────

class SinusoidalPE(nn.Module):
    """
    Sinusoidal positional encoding for D-dimensional coordinates.

    For each coordinate channel c and frequency band f:
        pe[..., 2*f]     = sin(2^f * π * coord[..., c])
        pe[..., 2*f + 1] = cos(2^f * π * coord[..., c])

    Parameters
    ----------
    coord_dim   : number of spatial dimensions (3 for 3-D coords)
    num_freqs   : number of frequency bands per dimension (set 0 to disable)

    Output dim  = coord_dim * num_freqs * 2   (appended to raw coords)
    """

    def __init__(self, coord_dim: int = 3, num_freqs: int = 6):
        super().__init__()
        self.coord_dim = coord_dim
        self.num_freqs = num_freqs
        self.out_dim   = coord_dim * num_freqs * 2  # extra dims added

        if num_freqs > 0:
            # precompute 2^f factors; register as buffer (not a parameter)
            freqs = 2.0 ** torch.arange(num_freqs).float() * math.pi
            self.register_buffer("freqs", freqs)           # (num_freqs,)

    def forward(self, coords: torch.Tensor) -> torch.Tensor:
        """
        Parameters
        ----------
        coords : (..., coord_dim)

        Returns
        -------
        pe     : (..., coord_dim * num_freqs * 2)
        """
        if self.num_freqs == 0:
            return coords.new_zeros(coords.shape[:-1] + (0,))

        # coords: (..., C)  →  (..., C, 1) * (num_freqs,)  →  (..., C, F)
        x  = coords.unsqueeze(-1) * self.freqs               # (..., C, F)
        pe = torch.cat([x.sin(), x.cos()], dim=-1)           # (..., C, 2F)
        return pe.flatten(-2)                                  # (..., C*2F)


# ─────────────────────────────────────────────────────────────────────────────
# Building blocks
# ─────────────────────────────────────────────────────────────────────────────

def _mlp(in_dim: int, hidden_dim: int, out_dim: int,
         num_hidden: int = 2, act=nn.GELU) -> nn.Sequential:
    """Simple MLP with GELU activations."""
    layers = [nn.Linear(in_dim, hidden_dim), act()]
    for _ in range(num_hidden - 1):
        layers += [nn.Linear(hidden_dim, hidden_dim), act()]
    layers.append(nn.Linear(hidden_dim, out_dim))
    return nn.Sequential(*layers)


# ─────────────────────────────────────────────────────────────────────────────
# MFTransolver
# ─────────────────────────────────────────────────────────────────────────────

class MFTransolver(nn.Module):
    """
    Multi-Fidelity Transolver:
      predicts 3-D surface pressure C_{p,HF} for each HF query point,
      conditioned on a 2-D LF surface pressure "physics-context" for the
      same car geometry.

    Parameters
    ----------
    cond_dim      : number of geometric condition parameters (23 for this dataset)
    hidden_dim    : internal feature dimension D
    n_slices      : number of physics-inspired slices K  (K << M_lf)
    num_heads     : number of attention heads H
    encoder_layers: hidden layers in LF/HF encoder MLPs
    residual_layers: hidden layers in the residual correction MLP
    pos_enc_freqs : frequency bands for sinusoidal PE (0 = disabled)
    """

    def __init__(self,
                 cond_dim:       int   = 23,
                 hidden_dim:     int   = 256,
                 n_slices:       int   = 32,
                 num_heads:      int   = 8,
                 encoder_layers: int   = 3,
                 residual_layers:int   = 3,
                 pos_enc_freqs:  int   = 6):
        super().__init__()

        self.hidden_dim    = hidden_dim
        self.n_slices      = n_slices
        self.num_heads     = num_heads
        assert hidden_dim % num_heads == 0, \
            f"hidden_dim {hidden_dim} must be divisible by num_heads {num_heads}"
        self.head_dim = hidden_dim // num_heads

        # ── Positional encoding ───────────────────────────────────────────────
        self.pos_enc      = SinusoidalPE(coord_dim=3, num_freqs=pos_enc_freqs)
        pe_dim            = self.pos_enc.out_dim        # 0 if pos_enc_freqs==0

        # ── Input dimensions ──────────────────────────────────────────────────
        # LF token: [x, y=0, z,  cond(C),  p_lf]  + optional PE
        lf_in = 3 + cond_dim + 1 + pe_dim
        # HF token: [x, y,   z,  cond(C)]          + optional PE
        hf_in = 3 + cond_dim     + pe_dim

        # ── Encoders ──────────────────────────────────────────────────────────
        self.lf_encoder = _mlp(lf_in, hidden_dim, hidden_dim,
                                num_hidden=encoder_layers)
        self.hf_encoder = _mlp(hf_in, hidden_dim, hidden_dim,
                                num_hidden=encoder_layers)
        self.lf_ln      = nn.LayerNorm(hidden_dim)
        self.hf_ln      = nn.LayerNorm(hidden_dim)

        # ── Dimensionality-lifting / bridge layer ─────────────────────────────
        # Aligns the y=0 LF subspace with the full 3-D HF query space.
        # A learned linear that can "lift" the LF representation before slicing.
        self.lf_lift = nn.Linear(hidden_dim, hidden_dim)

        # ── Slice-assignment: LF tokens → K slice weights ─────────────────────
        # Physics-based soft partitioning of the LF point cloud.
        self.slice_proj = nn.Linear(hidden_dim, n_slices)    # W_slice

        # ── Value projection for slice aggregation ────────────────────────────
        self.lf_v_proj  = nn.Linear(hidden_dim, hidden_dim)  # V side of LF

        # ── Cross-fidelity multi-head attention projections ───────────────────
        self.q_proj = nn.Linear(hidden_dim, hidden_dim, bias=False)
        self.k_proj = nn.Linear(hidden_dim, hidden_dim, bias=False)
        self.v_proj = nn.Linear(hidden_dim, hidden_dim, bias=False)
        self.o_proj = nn.Linear(hidden_dim, hidden_dim)
        self.attn_ln = nn.LayerNorm(hidden_dim)

        # ── Prior head: decode 2-D pressure prior from attended slice ─────────
        self.prior_head = nn.Linear(hidden_dim, 1)

        # ── Residual head: 3-D correction MLP ────────────────────────────────
        # Input: attended LF context + HF query feature  (2 * hidden_dim)
        self.residual_mlp = _mlp(2 * hidden_dim, hidden_dim, 1,
                                  num_hidden=residual_layers)

        self._init_weights()

    # ── Weight init ───────────────────────────────────────────────────────────
    def _init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    nn.init.zeros_(m.bias)

    # ── Forward ───────────────────────────────────────────────────────────────
    def forward(self,
                lf_tokens: torch.Tensor,
                hf_tokens: torch.Tensor) -> torch.Tensor:
        """
        Parameters
        ----------
        lf_tokens : (B, M, 3 + C + 1)   [x, y=0, z, cond..., p_lf]
        hf_tokens : (B, N, 3 + C)        [x, y, z,  cond...]

        Returns
        -------
        pred_hf   : (B, N, 1)            predicted normalised C_{p,HF}
        """
        B, M, _ = lf_tokens.shape
        _, N, _ = hf_tokens.shape

        # ── Sinusoidal PE on coordinates ──────────────────────────────────────
        lf_coords = lf_tokens[..., :3]                    # (B, M, 3)
        hf_coords = hf_tokens[..., :3]                    # (B, N, 3)

        lf_pe = self.pos_enc(lf_coords)                   # (B, M, pe_dim)
        hf_pe = self.pos_enc(hf_coords)                   # (B, N, pe_dim)

        # Append PE to tokens
        if lf_pe.shape[-1] > 0:
            lf_in = torch.cat([lf_tokens, lf_pe], dim=-1)
            hf_in = torch.cat([hf_tokens, hf_pe], dim=-1)
        else:
            lf_in = lf_tokens
            hf_in = hf_tokens

        # ── Encode ────────────────────────────────────────────────────────────
        lf_feat = self.lf_ln(self.lf_encoder(lf_in))     # (B, M, D)
        hf_feat = self.hf_ln(self.hf_encoder(hf_in))     # (B, N, D)

        # ── Dimensionality-lifting bridge (LF 2-D → 3-D aligned space) ───────
        lf_lifted = F.gelu(self.lf_lift(lf_feat))        # (B, M, D)

        # ── Slice-and-Basis: LF tokens → K physical slices ───────────────────
        # Soft assignment of each LF token to K slices (sum over M tokens)
        slice_logits  = self.slice_proj(lf_lifted)        # (B, M, K)
        slice_weights = F.softmax(slice_logits, dim=1)    # (B, M, K)  sum over M

        # K slice key-bases: weighted average of lifted LF features
        #   slice_keys[b, k, d] = Σ_m  slice_weights[b,m,k] * lf_lifted[b,m,d]
        slice_keys = torch.einsum('bmk,bmd->bkd',
                                  slice_weights, lf_lifted)    # (B, K, D)

        # K slice value-bases: weighted average of projected LF values
        lf_vals    = self.lf_v_proj(lf_lifted)           # (B, M, D)
        slice_vals = torch.einsum('bmk,bmd->bkd',
                                  slice_weights, lf_vals)      # (B, K, D)

        # ── Cross-Fidelity Multi-Head Attention ───────────────────────────────
        # Q from HF queries; K, V from LF slice bases
        H, dh = self.num_heads, self.head_dim

        def split_heads(x):
            # (B, L, D) → (B, L, H, dh) → (B, H, L, dh)
            B_, L, _ = x.shape
            return x.reshape(B_, L, H, dh).transpose(1, 2)

        Q  = split_heads(self.q_proj(hf_feat))              # (B, H, N,  dh)
        K  = split_heads(self.k_proj(slice_keys))           # (B, H, K,  dh)
        V  = split_heads(self.v_proj(slice_vals))           # (B, H, K,  dh)

        # Scaled dot-product via einsum
        scale = math.sqrt(dh)
        attn  = torch.einsum('bhnd,bhkd->bhnk', Q, K) / scale   # (B, H, N, K)
        attn  = F.softmax(attn, dim=-1)

        # Aggregate values
        ctx   = torch.einsum('bhnk,bhkd->bhnd', attn, V)         # (B, H, N, dh)
        ctx   = ctx.transpose(1, 2).reshape(B, N, H * dh)        # (B, N, D)
        ctx   = self.attn_ln(self.o_proj(ctx))                    # (B, N, D)

        # ── Prior: pressure prior decoded from LF slice attention ─────────────
        prior = self.prior_head(ctx)                               # (B, N, 1)

        # ── Residual: 3-D correction from [context ‖ HF features] ───────────
        residual_in  = torch.cat([ctx, hf_feat], dim=-1)          # (B, N, 2D)
        residual     = self.residual_mlp(residual_in)             # (B, N, 1)

        # ── Final prediction: 2-D prior + 3-D learned correction ─────────────
        pred = prior + residual                                    # (B, N, 1)
        return pred


# ─────────────────────────────────────────────────────────────────────────────
# Convenience: parameter count
# ─────────────────────────────────────────────────────────────────────────────

def param_count(model: nn.Module) -> tuple[int, int]:
    """Returns (trainable, total) parameter counts."""
    total     = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    return trainable, total


__all__ = ["MFTransolver", "SinusoidalPE", "param_count"]
