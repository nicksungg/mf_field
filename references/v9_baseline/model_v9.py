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


def _mlp(in_dim: int, hidden_dim: int, out_dim: int, num_hidden: int = 2, act=nn.GELU) -> nn.Sequential:
	layers = [nn.Linear(in_dim, hidden_dim), act()]
	for _ in range(num_hidden - 1):
		layers += [nn.Linear(hidden_dim, hidden_dim), act()]
	layers.append(nn.Linear(hidden_dim, out_dim))
	return nn.Sequential(*layers)


class MFTransolver_v9(nn.Module):
	def __init__(
		self,
		cond_dim: int = 23,
		hidden_dim: int = 256,
		n_slices: int = 32,
		num_heads: int = 8,
		encoder_layers: int = 3,
		residual_layers: int = 3,
		pos_enc_freqs: int = 6,
		rbf_gamma_init: float = 1.0,
		num_lf_streams: int = 1,
	):
		super().__init__()

		self.hidden_dim = hidden_dim
		self.n_slices = n_slices
		self.num_heads = num_heads
		self.num_lf_streams = num_lf_streams
		assert hidden_dim % num_heads == 0
		self.head_dim = hidden_dim // num_heads

		self.pos_enc = SinusoidalPE(coord_dim=3, num_freqs=pos_enc_freqs)
		pe_dim = self.pos_enc.out_dim

		lf_in = 3 + cond_dim + 1 + pe_dim
		hf_in = 3 + cond_dim + pe_dim

		self.lf_encoder = _mlp(lf_in, hidden_dim, hidden_dim, num_hidden=encoder_layers)
		self.hf_encoder = _mlp(hf_in, hidden_dim, hidden_dim, num_hidden=encoder_layers)
		self.lf_ln = nn.LayerNorm(hidden_dim)
		self.hf_ln = nn.LayerNorm(hidden_dim)

		self.lf_lift = nn.Linear(hidden_dim, hidden_dim)
		self.cross_slice_proj = nn.Linear(hidden_dim, n_slices)
		self.lf_v_proj = nn.Linear(hidden_dim, hidden_dim)

		self.pressure_embed = nn.Sequential(
			nn.Linear(1, hidden_dim),
			nn.GELU(),
			nn.Linear(hidden_dim, hidden_dim),
			nn.Sigmoid(),
		)

		self.cross_q_proj = nn.Linear(hidden_dim, hidden_dim, bias=False)
		self.cross_k_proj = nn.Linear(hidden_dim, hidden_dim, bias=False)
		self.cross_v_proj = nn.Linear(hidden_dim, hidden_dim, bias=False)
		self.cross_o_proj = nn.Linear(hidden_dim, hidden_dim)
		self.cross_attn_ln = nn.LayerNorm(hidden_dim)

		self.log_gamma = nn.Parameter(torch.tensor(math.log(rbf_gamma_init), dtype=torch.float32))

		self.self_slice_proj = nn.Linear(hidden_dim, n_slices)
		self.hf_v_proj = nn.Linear(hidden_dim, hidden_dim)

		self.self_q_proj = nn.Linear(hidden_dim, hidden_dim, bias=False)
		self.self_k_proj = nn.Linear(hidden_dim, hidden_dim, bias=False)
		self.self_v_proj = nn.Linear(hidden_dim, hidden_dim, bias=False)
		self.self_o_proj = nn.Linear(hidden_dim, hidden_dim)
		self.self_attn_ln = nn.LayerNorm(hidden_dim)

		n_ctx = self.num_lf_streams + 1
		self.gate_mlp = nn.Sequential(
			nn.Linear(n_ctx * hidden_dim, hidden_dim),
			nn.GELU(),
			nn.Linear(hidden_dim, n_ctx),
		)

		self.prior_head = nn.Sequential(
			nn.Linear(hidden_dim, hidden_dim),
			nn.GELU(),
			nn.Linear(hidden_dim, 1),
		)

		self.delta_mlp = _mlp(2 * hidden_dim, hidden_dim, 1, num_hidden=residual_layers)
		nn.init.zeros_(self.delta_mlp[-1].weight)
		nn.init.zeros_(self.delta_mlp[-1].bias)

		self._init_weights()
		# Start near-uniform gating to avoid early stream collapse.
		nn.init.zeros_(self.gate_mlp[-1].weight)
		nn.init.zeros_(self.gate_mlp[-1].bias)

	def _init_weights(self):
		for name, m in self.named_modules():
			if isinstance(m, nn.Linear) and "delta_mlp" not in name:
				nn.init.xavier_uniform_(m.weight)
				if m.bias is not None:
					nn.init.zeros_(m.bias)

	def _multihead_attention(self, Q, K, V, bias=None):
		scale = math.sqrt(self.head_dim)
		logits = torch.einsum("bhnd,bhkd->bhnk", Q, K) / scale
		if bias is not None:
			logits = logits + bias
		attn = F.softmax(logits, dim=-1)
		ctx = torch.einsum("bhnk,bhkd->bhnd", attn, V)
		return ctx

	def forward(
		self,
		list_of_lf_tokens: List[torch.Tensor],
		hf_tokens: torch.Tensor,
		gate_temperature: float = 1.0,
		return_components: bool = False,
	):
		if isinstance(list_of_lf_tokens, torch.Tensor):
			list_of_lf_tokens = [list_of_lf_tokens]
		if len(list_of_lf_tokens) == 0:
			raise ValueError("list_of_lf_tokens must contain at least one LF stream.")
		if self.num_lf_streams != len(list_of_lf_tokens):
			raise ValueError(
				f"Model initialized with num_lf_streams={self.num_lf_streams}, "
				f"but got {len(list_of_lf_tokens)} LF streams."
			)

		B, N, _ = hf_tokens.shape
		H, dh = self.num_heads, self.head_dim

		hf_coords = hf_tokens[..., :3]
		hf_pe = self.pos_enc(hf_coords)
		hf_in = torch.cat([hf_tokens, hf_pe], dim=-1) if hf_pe.shape[-1] > 0 else hf_tokens
		hf_feat = self.hf_ln(self.hf_encoder(hf_in))

		def split_heads(x):
			B_, L, _ = x.shape
			return x.reshape(B_, L, H, dh).transpose(1, 2)

		self_sw = F.softmax(self.self_slice_proj(hf_feat), dim=1)
		self_slice_keys = torch.einsum("bnk,bnd->bkd", self_sw, hf_feat)
		hf_vals = self.hf_v_proj(hf_feat)
		self_slice_vals = torch.einsum("bnk,bnd->bkd", self_sw, hf_vals)

		Q_self = split_heads(self.self_q_proj(hf_feat))
		K_self = split_heads(self.self_k_proj(self_slice_keys))
		V_self = split_heads(self.self_v_proj(self_slice_vals))
		ctx_self = self._multihead_attention(Q_self, K_self, V_self)
		ctx_self = ctx_self.transpose(1, 2).reshape(B, N, H * dh)
		ctx_self = self.self_attn_ln(self.self_o_proj(ctx_self))

		cross_contexts = []
		gamma = torch.exp(self.log_gamma)
		Q_cross = split_heads(self.cross_q_proj(hf_feat))

		for lf_tok in list_of_lf_tokens:
			lf_pressure = lf_tok[..., -1:]
			lf_coords = lf_tok[..., :3]

			lf_pe = self.pos_enc(lf_coords)
			lf_in = torch.cat([lf_tok, lf_pe], dim=-1) if lf_pe.shape[-1] > 0 else lf_tok
			lf_feat = self.lf_ln(self.lf_encoder(lf_in))

			lf_lifted = F.gelu(self.lf_lift(lf_feat))
			cross_sw = F.softmax(self.cross_slice_proj(lf_lifted), dim=1)
			cross_slice_keys = torch.einsum("bmk,bmd->bkd", cross_sw, lf_lifted)

			lf_vals = self.lf_v_proj(lf_lifted)
			p_gate = self.pressure_embed(lf_pressure)
			lf_vals = lf_vals * p_gate
			cross_slice_vals = torch.einsum("bmk,bmd->bkd", cross_sw, lf_vals)

			slice_centroids = torch.einsum("bmk,bmc->bkc", cross_sw, lf_coords)
			dist2 = torch.cdist(hf_coords, slice_centroids, p=2.0).pow(2)
			log_rbf_bias = torch.log(torch.exp(-gamma * dist2) + 1e-9).unsqueeze(1)

			K_cross = split_heads(self.cross_k_proj(cross_slice_keys))
			V_cross = split_heads(self.cross_v_proj(cross_slice_vals))
			ctx_cross = self._multihead_attention(Q_cross, K_cross, V_cross, bias=log_rbf_bias)
			ctx_cross = ctx_cross.transpose(1, 2).reshape(B, N, H * dh)
			ctx_cross = self.cross_attn_ln(self.cross_o_proj(ctx_cross))
			cross_contexts.append(ctx_cross)

		gate_in = torch.cat([ctx_self] + cross_contexts, dim=-1)
		alpha_logits = self.gate_mlp(gate_in)
		tau = max(float(gate_temperature), 1e-6)
		alpha = F.softmax(alpha_logits / tau, dim=-1)

		all_contexts = torch.stack([ctx_self] + cross_contexts, dim=-2)
		hybrid_ctx = (alpha.unsqueeze(-1) * all_contexts).sum(dim=-2)

		prior = self.prior_head(hybrid_ctx)
		delta_in = torch.cat([hybrid_ctx, hf_feat], dim=-1)
		delta = self.delta_mlp(delta_in)
		pred = prior + delta

		if return_components:
			return {
				"pred": pred,
				"prior": prior,
				"delta": delta,
				"alpha": alpha,
				"alpha_logits": alpha_logits,
			}
		return pred


def param_count(model: nn.Module) -> tuple[int, int]:
	total = sum(p.numel() for p in model.parameters())
	trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
	return trainable, total


__all__ = ["MFTransolver_v9", "SinusoidalPE", "param_count"]
