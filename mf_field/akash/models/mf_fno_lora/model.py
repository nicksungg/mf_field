"""Fidelity-conditioned LoRA-adapted MF-FNO.

The benchmark winner `mf_fno_transfer_film` does LF-pretrain -> HF-finetune by
fine-tuning the WHOLE backbone on the scarce HF data. This family keeps the same
FiLM-on-X FNO backbone (common.backbone.FNO2d) but replaces full HF fine-tuning
with PARAMETER-EFFICIENT low-rank adapters (LoRA, Hu et al. 2022):

  * Pretrain the FNO on LF with the FULL backbone trainable.
  * FREEZE the backbone. Inject a parallel low-rank path  B @ A  (rank r, e.g. 4)
    into every 1x1 Conv2d — the `w` in each FNO block, the lift, and both proj
    convs. B is ZERO-INIT, so at the start of HF-finetune the adapted model is
    IDENTICAL to the frozen LF-pretrained model (exact reduction).
  * Optionally also LoRA-adapt the FiLM MLP Linears.
  * HF-finetune trains ONLY the adapters (+ optionally the FiLM-MLP adapters).

The complex spectral kernels (SpectralConv2d.w1/w2) are NOT adapted — real-valued
LoRA on complex weights is awkward and the 1x1 convs + FiLM already give the
channel-mixing capacity to retune the LF features for HF. The total adapter L2
norm is a proxy for the LF->HF gap (reported in `extra`).

References: hu2022lora (LoRA), lyu2023mffno (LF->HF transfer schedule),
perez2018film (FiLM), li2020fno (FNO backbone).
"""
from __future__ import annotations

from typing import Tuple

import torch
import torch.nn as nn

from common.backbone import FNO2d, param_count  # noqa: F401

Grid = Tuple[int, int]


class LoRAConv1x1(nn.Module):
    """Wrap a frozen 1x1 nn.Conv2d with a parallel low-rank update B@A.

    out = base(x) + scale * conv1x1(B @ A) applied to x.
    A: (rank, in), B: (out, rank). B zero-init -> update == 0 at start, so the
    wrapped module reduces EXACTLY to `base` until the adapter trains.
    """

    def __init__(self, base: nn.Conv2d, rank: int = 4, alpha: float = 1.0):
        super().__init__()
        assert base.kernel_size == (1, 1), "LoRAConv1x1 expects a 1x1 conv"
        self.base = base
        for q in self.base.parameters():
            q.requires_grad_(False)
        in_ch = base.in_channels
        out_ch = base.out_channels
        self.rank = rank
        self.scale = alpha / rank
        self.A = nn.Parameter(torch.randn(rank, in_ch) * (1.0 / in_ch ** 0.5))
        self.B = nn.Parameter(torch.zeros(out_ch, rank))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out = self.base(x)
        # low-rank 1x1 conv: weight = (B @ A) shaped (out, in, 1, 1)
        w = (self.B @ self.A).unsqueeze(-1).unsqueeze(-1)
        upd = nn.functional.conv2d(x, w * self.scale)
        return out + upd

    def adapter_parameters(self):
        return [self.A, self.B]


class LoRALinear(nn.Module):
    """Wrap a frozen nn.Linear with a parallel low-rank update B@A (B zero-init)."""

    def __init__(self, base: nn.Linear, rank: int = 4, alpha: float = 1.0):
        super().__init__()
        self.base = base
        for q in self.base.parameters():
            q.requires_grad_(False)
        self.rank = rank
        self.scale = alpha / rank
        self.A = nn.Parameter(torch.randn(rank, base.in_features) * (1.0 / base.in_features ** 0.5))
        self.B = nn.Parameter(torch.zeros(base.out_features, rank))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.base(x) + self.scale * (x @ self.A.t()) @ self.B.t()

    def adapter_parameters(self):
        return [self.A, self.B]


def _replace_module(parent: nn.Module, name: str, new: nn.Module):
    setattr(parent, name, new)


def inject_lora(model: FNO2d, rank: int = 4, alpha: float = 1.0,
                adapt_film: bool = True):
    """Freeze `model`, wrap every 1x1 Conv2d (and optionally FiLM Linears) in LoRA.

    Returns the list of adapter parameter tensors (A, B for each wrapped layer).
    After this call, ONLY the returned tensors require grad; the rest of the
    backbone is frozen. With B zero-init, model(x) is unchanged at injection time.
    """
    for q in model.parameters():
        q.requires_grad_(False)

    adapters = []

    def wrap_conv(parent, attr):
        nonlocal adapters
        mod = getattr(parent, attr)
        if isinstance(mod, nn.Conv2d) and mod.kernel_size == (1, 1):
            lo = LoRAConv1x1(mod, rank=rank, alpha=alpha)
            _replace_module(parent, attr, lo)
            adapters.extend(lo.adapter_parameters())

    def wrap_linear(parent, attr):
        nonlocal adapters
        mod = getattr(parent, attr)
        if isinstance(mod, nn.Linear):
            lo = LoRALinear(mod, rank=rank, alpha=alpha)
            _replace_module(parent, attr, lo)
            adapters.extend(lo.adapter_parameters())

    # lift (1x1 conv)
    wrap_conv(model, "lift")
    # proj is a Sequential: Conv2d, GELU, Conv2d
    for i, sub in enumerate(model.proj):
        if isinstance(sub, nn.Conv2d) and sub.kernel_size == (1, 1):
            mod = model.proj[i]
            lo = LoRAConv1x1(mod, rank=rank, alpha=alpha)
            model.proj[i] = lo
            adapters.extend(lo.adapter_parameters())
    # each FNO block: w (1x1 conv) + optionally the FiLM MLP Linears
    for blk in model.blocks:
        wrap_conv(blk, "w")
        if adapt_film:
            # blk.norm.film is Sequential(Linear, GELU, Linear)
            film = blk.norm.film
            for i, sub in enumerate(film):
                if isinstance(sub, nn.Linear):
                    lo = LoRALinear(film[i], rank=rank, alpha=alpha)
                    film[i] = lo
                    adapters.extend(lo.adapter_parameters())

    return adapters


def adapter_l2_norm(adapters) -> float:
    """Total L2 norm over all adapter tensors (proxy for the LF->HF gap)."""
    with torch.no_grad():
        sq = sum(float((a.detach() ** 2).sum()) for a in adapters)
    return float(sq ** 0.5)
