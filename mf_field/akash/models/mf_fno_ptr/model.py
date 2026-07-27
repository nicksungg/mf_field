"""mf_fno_ptr — the FiLM-transfer winner backbone, UNCHANGED, for PDE-residual
test-time refinement (PTR).

This family is a *wrapper*: training is byte-for-byte the benchmark winner
`mf_fno_transfer_film` (LF-pretrain -> HF-finetune over an FiLM-conditioned FNO,
shared `common.backbone`). The ONLY addition lives at INFERENCE: each predicted
field is refined by a few gradient steps on the FIELD tensor `u` (not the
weights), minimizing

    L(u) = w_res * || R(u, X, grid) ||^2  +  w_anchor * || u - u_pred ||^2

where `R` is a per-dataset PDE residual (see `refine.py` registry) and the
anchor keeps `u` near the network output. If no residual is registered for the
dataset, refinement is a graceful NO-OP and the family reduces exactly to the
winner.

Inspired by: nobari2024nito (inference-time / test-time refinement of an
operator's output by the governing residual), perez2018film (FiLM conditioning),
lyu2023mffno (LF->HF transfer schedule).

This module re-exports the shared backbone so a future family can import the
exact same FNO2d.
"""
from __future__ import annotations

import sys
from pathlib import Path

# allow `from common.backbone import ...` when imported standalone
_AKASH = Path(__file__).resolve().parents[2]
if str(_AKASH) not in sys.path:
    sys.path.insert(0, str(_AKASH))

from common.backbone import (  # noqa: F401,E402
    SpectralConv2d, FiLMNorm, FNOBlock, FNO2d, param_count,
)

__all__ = ["SpectralConv2d", "FiLMNorm", "FNOBlock", "FNO2d", "param_count"]
