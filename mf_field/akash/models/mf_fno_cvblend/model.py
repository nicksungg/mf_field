"""mf_fno_cvblend (B7) — re-exports the frozen FiLM backbone unchanged.

The B7 mechanism is an INFERENCE-time control-variate blend of two independently
trained FiLM FNOs (an LF model and an HF model), not an architecture change, so
the model is byte-for-byte the benchmark winner's FiLM-on-X FNO.

References: li2020fno (FNO backbone); perez2018film (FiLM); control variates
(classic Monte-Carlo variance reduction).
"""
from __future__ import annotations

import sys
from pathlib import Path

_AKASH = Path(__file__).resolve().parents[2]
if str(_AKASH) not in sys.path:
    sys.path.insert(0, str(_AKASH))

from common.backbone import (  # noqa: E402,F401
    SpectralConv2d, FiLMNorm, FNOBlock, FNO2d, param_count,
)
