"""Sequential (residual) FNO -> Transolver hybrid.

    y_hat(x) = FNO_FiLM(X)(x)  +  alpha * Transolver_correction(X, ctx, x)

Motivation
----------
On the 40-dataset MF-field benchmark, `mf_fno_transfer_film` (geomean rel-L2
0.01577) and `transolver_residual` (0.02998) have strongly COMPLEMENTARY error
profiles: the Transolver wins 16/38 datasets despite being ~2x worse on average,
and a per-dataset oracle over the pair scores 0.01095 (-30.6% vs the FNO alone),
by far the largest oracle gap of any pairing in the benchmark. This family tries
to capture part of that gap inside ONE model instead of a dataset-level switch.

Why sequential and not a mixture
--------------------------------
The two backbones fail differently *in space*: the spectral FNO is a global,
band-limited operator (it smears shocks/contact discontinuities and struggles
where the solution is locally non-smooth), while Transolver is point-based with
physics-slice attention (it resolves local structure but has no global spectral
prior, so it is worse on smooth global fields). Composing them as
`base + correction` lets each do what it is good at: the FNO fixes the smooth
global field, the Transolver only has to model the FNO's *error*, which is
concentrated exactly on the sharp/local features the FNO cannot represent.

Two properties make the coupling safe:
  * `alpha` is a scalar gate initialised at 0, so at initialisation the hybrid is
    EXACTLY the FNO base. It is then set by a least-squares fit on a held-out HF
    split, which is the projection of the true residual onto the predicted
    correction: the fitted value can only reduce (never increase) the val MSE,
    and collapses to ~0 when the correction is uninformative.
  * the correction head is zero-initialised and predicts a *pure delta* (no
    LF-interpolation base is added to the output, unlike `transolver_residual`),
    so the correction branch starts at exactly 0 too.

Differences vs `factory_mffp/models/transolver_residual/model.py`
----------------------------------------------------------------
1. `pred = delta` instead of `pred = lf_interp + delta`. Here the interpolated
   context is a *feature*, not an output base: the output base is the FNO.
2. The query tokens carry one extra channel, the FNO base prediction at that
   query point. The corrector therefore knows what it is correcting.
3. The soft-nearest-neighbour interpolation bandwidth `gamma` is learnable and
   initialised from the actual context-point spacing. The hard-coded
   `interp_gamma=4.0` of the original is a *very* wide kernel on [-1,1]^d
   (bandwidth ~0.5), i.e. a global blur rather than an interpolation; with 1024
   context points the useful bandwidth is ~1e2-1e4.

References: li2020fno (FNO), wu2024transolver (physics-slice attention),
perez2018film (FiLM conditioning), lyu2023mffno (LF->HF transfer schedule).
"""
from __future__ import annotations

import math
from typing import List, Sequence

import torch
import torch.nn as nn
import torch.nn.functional as F


# ─────────────────────────────────────────────────────────────────────────────
# helpers (kept byte-compatible with transolver_residual where it matters)
# ─────────────────────────────────────────────────────────────────────────────
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


def soft_interp(ctx_tokens: torch.Tensor, q_coords: torch.Tensor,
                gamma: torch.Tensor) -> torch.Tensor:
    """Soft-nearest-neighbour interpolation of the context field at query coords.

    ctx_tokens: (B, M, 3 + cond_dim + 1) — last channel is the context value.
    q_coords  : (B, N, 3)
    returns   : (B, N, 1)
    """
    c_coords = ctx_tokens[..., :3]
    c_vals = ctx_tokens[..., -1:]
    dist2 = torch.cdist(q_coords, c_coords, p=2.0).pow(2)
    w = F.softmax(-gamma * dist2, dim=-1)
    return torch.einsum("bnm,bmd->bnd", w, c_vals)


# ─────────────────────────────────────────────────────────────────────────────
# the correction network
# ─────────────────────────────────────────────────────────────────────────────
class TransolverCorrector(nn.Module):
    """Point-based Transolver head predicting the FNO's residual field.

    forward(ctx_tokens, q_tokens) -> (B, N, 1) correction in residual-scaler units.

    q_tokens : (B, N, 3 + cond_dim + 1)  = [coords, cond, base_pred]
    ctx_tokens: (B, M, 3 + cond_dim + 1) = [coords, cond, ctx_value]
      (a list of streams is accepted for signature-compatibility with
       `TransolverResidual`; the last/finest stream is used.)
    """

    def __init__(self, cond_dim: int, hidden_dim: int = 192, n_slices: int = 32,
                 num_heads: int = 6, encoder_layers: int = 2, residual_layers: int = 3,
                 pos_enc_freqs: int = 6, interp_gamma: float = 64.0):
        super().__init__()
        assert hidden_dim % num_heads == 0
        self.hidden_dim = hidden_dim
        self.num_heads = num_heads
        self.head_dim = hidden_dim // num_heads
        self.n_slices = n_slices
        # learnable, positive bandwidth (log-parameterised); init from point spacing
        self.log_gamma = nn.Parameter(torch.tensor(float(math.log(max(interp_gamma, 1e-3)))))

        self.pos_enc = SinusoidalPE(coord_dim=3, num_freqs=pos_enc_freqs)
        pe_dim = self.pos_enc.out_dim

        # query features = [coords, cond, base_pred] + interp(ctx) + pos-enc
        q_in = 3 + cond_dim + 1 + 1 + pe_dim
        c_in = 3 + cond_dim + 1 + pe_dim
        self.hf_encoder = _mlp(q_in, hidden_dim, hidden_dim, num_hidden=encoder_layers)
        self.lf_encoder = _mlp(c_in, hidden_dim, hidden_dim, num_hidden=encoder_layers)
        self.hf_ln = nn.LayerNorm(hidden_dim)
        self.lf_ln = nn.LayerNorm(hidden_dim)

        # self physics-slice attention over the query set (wu2024transolver)
        self.self_slice_proj = nn.Linear(hidden_dim, n_slices)
        self.self_v_proj = nn.Linear(hidden_dim, hidden_dim)
        self.self_q = nn.Linear(hidden_dim, hidden_dim, bias=False)
        self.self_k = nn.Linear(hidden_dim, hidden_dim, bias=False)
        self.self_v = nn.Linear(hidden_dim, hidden_dim, bias=False)
        self.self_o = nn.Linear(hidden_dim, hidden_dim)
        self.self_ln = nn.LayerNorm(hidden_dim)

        # cross slice attention: queries -> context slices
        self.cross_slice_proj = nn.Linear(hidden_dim, n_slices)
        self.cross_v_proj = nn.Linear(hidden_dim, hidden_dim)
        self.cross_q = nn.Linear(hidden_dim, hidden_dim, bias=False)
        self.cross_k = nn.Linear(hidden_dim, hidden_dim, bias=False)
        self.cross_v = nn.Linear(hidden_dim, hidden_dim, bias=False)
        self.cross_o = nn.Linear(hidden_dim, hidden_dim)
        self.cross_ln = nn.LayerNorm(hidden_dim)

        # residual head — zero-init so the correction is identically 0 at start
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

    def _split_heads(self, x):
        B, L, _ = x.shape
        return x.reshape(B, L, self.num_heads, self.head_dim).transpose(1, 2)

    def _mha(self, Q, K, V):
        scale = math.sqrt(self.head_dim)
        logits = torch.einsum("bhnd,bhkd->bhnk", Q, K) / scale
        attn = F.softmax(logits, dim=-1)
        return torch.einsum("bhnk,bhkd->bhnd", attn, V)

    def forward(self, ctx_tokens, q_tokens: torch.Tensor,
                return_components: bool = False):
        if isinstance(ctx_tokens, (list, tuple)):
            if len(ctx_tokens) == 0:
                raise ValueError("need at least one context stream")
            ctx_tokens = ctx_tokens[-1]

        B, N, _ = q_tokens.shape
        q_coords = q_tokens[..., :3]

        gamma = self.log_gamma.exp()
        ctx_interp = soft_interp(ctx_tokens, q_coords, gamma)     # (B, N, 1)

        q_pe = self.pos_enc(q_coords)
        q_feat = self.hf_ln(self.hf_encoder(torch.cat([q_tokens, ctx_interp, q_pe], dim=-1)))

        c_coords = ctx_tokens[..., :3]
        c_pe = self.pos_enc(c_coords)
        c_feat = self.lf_ln(self.lf_encoder(torch.cat([ctx_tokens, c_pe], dim=-1)))

        # self slice-attention over the query cloud
        sw = F.softmax(self.self_slice_proj(q_feat), dim=1)
        keys = torch.einsum("bnk,bnd->bkd", sw, q_feat)
        vals = torch.einsum("bnk,bnd->bkd", sw, self.self_v_proj(q_feat))
        Q = self._split_heads(self.self_q(q_feat))
        K = self._split_heads(self.self_k(keys))
        V = self._split_heads(self.self_v(vals))
        ctx_self = self._mha(Q, K, V).transpose(1, 2).reshape(B, N, self.hidden_dim)
        ctx_self = self.self_ln(self.self_o(ctx_self))

        # cross slice-attention onto the context cloud
        cw = F.softmax(self.cross_slice_proj(c_feat), dim=1)
        ckeys = torch.einsum("bmk,bmd->bkd", cw, c_feat)
        cvals = torch.einsum("bmk,bmd->bkd", cw, self.cross_v_proj(c_feat))
        Q = self._split_heads(self.cross_q(q_feat))
        K = self._split_heads(self.cross_k(ckeys))
        V = self._split_heads(self.cross_v(cvals))
        ctx_cross = self._mha(Q, K, V).transpose(1, 2).reshape(B, N, self.hidden_dim)
        ctx_cross = self.cross_ln(self.cross_o(ctx_cross))

        delta = self.delta_mlp(torch.cat([ctx_self, ctx_cross], dim=-1))
        if return_components:
            return {"delta": delta, "ctx_interp": ctx_interp, "gamma": gamma}
        return delta


class SeqHybrid(nn.Module):
    """Container: FNO base + Transolver corrector + scalar gate alpha (init 0).

    Keeping alpha inside an nn.Module means it is checkpointed and can be
    optimised jointly in the optional stage-3 fine-tune.
    """

    def __init__(self, fno: nn.Module, corrector: nn.Module):
        super().__init__()
        self.fno = fno
        self.corrector = corrector
        self.alpha = nn.Parameter(torch.zeros(1))

    @property
    def alpha_value(self) -> float:
        return float(self.alpha.detach().reshape(-1)[0])


def param_count(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters())


def grid_coords(H: int, W: int) -> torch.Tensor:
    """(H*W, 3) coords matching v9's `field_to_points` for a single-channel field.

    x = linspace(-1,1,W) along the fast axis, z = linspace(-1,1,H) along the slow
    axis, y-level = 0 for a 1-channel field. Row-major so point index i*W+j lines
    up with `field.reshape(-1)` — the same flattening the FNO working grid uses.
    """
    xs = torch.linspace(-1.0, 1.0, W)
    zs = torch.linspace(-1.0, 1.0, H)
    zz, xx = torch.meshgrid(zs, xs, indexing="ij")
    yy = torch.zeros_like(xx)
    return torch.stack([xx, yy, zz], dim=-1).reshape(-1, 3)


def gamma_init_for(H: int, W: int, n_pts: int) -> float:
    """Bandwidth init: ~3 / h^2 where h is the typical spacing of `n_pts` samples.

    A d-dimensional [-1,1]^d cloud of M points has nearest-neighbour spacing
    h ~ 2 / M^(1/d); softmax(-gamma*dist^2) then behaves as a local interpolant
    rather than a global average (the 4.0 of transolver_residual is a ~0.5-wide
    blur, which discards all local information at these point counts).
    """
    d = 2 if (H > 1 and W > 1) else 1
    m = max(min(int(n_pts), int(H) * int(W)), 2)
    h = 2.0 / (m ** (1.0 / d))
    return float(min(max(3.0 / (h * h), 4.0), 1e5))


__all__ = ["TransolverCorrector", "SeqHybrid", "SinusoidalPE", "soft_interp",
           "param_count", "grid_coords", "gamma_init_for"]
