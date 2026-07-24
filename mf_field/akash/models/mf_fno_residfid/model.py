"""mf_fno_residfid (B5) — re-exports the frozen FiLM backbone unchanged.

The B5 mechanism is a TRAINING-LOSS change (a PDE-residual self-supervised
auxiliary term), not an architecture change, so the model is byte-for-byte the
benchmark winner's FiLM-on-X FNO. We re-export it here so the family is
self-contained and the smoke script's `from model import ...` resolves locally.

References: li2020fno (FNO backbone); perez2018film (FiLM); raissi2019pinn
(physics-informed residual loss — here a weak Laplacian-smoothness placeholder
for the true PDE operator).
"""
from __future__ import annotations

import sys
from pathlib import Path

# common.backbone is the frozen winner backbone (SpectralConv2d, FiLMNorm,
# FNOBlock, FNO2d, param_count). Import path is set up by smoke_eval.py, but add
# it here too so `from model import FNO2d` works if imported standalone.
_AKASH = Path(__file__).resolve().parents[2]
if str(_AKASH) not in sys.path:
    sys.path.insert(0, str(_AKASH))

from common.backbone import (  # noqa: E402,F401
    SpectralConv2d, FiLMNorm, FNOBlock, FNO2d, param_count,
)
