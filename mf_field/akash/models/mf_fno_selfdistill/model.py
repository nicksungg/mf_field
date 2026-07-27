"""mf_fno_selfdistill (B6) — re-exports the frozen FiLM backbone unchanged.

The B6 mechanism is a DATA / training-schedule change (fidelity bootstrapping
via self-generated pseudo-HF labels), not an architecture change, so the model
is byte-for-byte the benchmark winner's FiLM-on-X FNO.

References: li2020fno (FNO backbone); perez2018film (FiLM); lee2013pseudolabel
(pseudo-labelling / self-training); lyu2023mffno (LF->HF transfer schedule).
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
