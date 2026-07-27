"""Continuous-fidelity MF-FNO with learned Richardson extrapolation
(herde2024poseidon + richardson1911).

Premise: fidelity is a CONTINUOUS coordinate, not a discrete label. Discretization
error decays smoothly as the grid refines, so a single operator conditioned on a
normalized fidelity scalar `f` can interpolate the operator across fidelities —
and, crucially, EXTRAPOLATE toward the true (infinite-fidelity) solution.

Model: the winner's FiLM-on-cond FNO (common.backbone.FNO2d) with the condition
vector AUGMENTED by the fidelity scalar: cond = [X, f], cond_dim = d + 1, where
f = (log(fid) - log(min_fid)) / (log(max_fid) - log(min_fid)) in [0, 1]. f enters
through FiLM at every block exactly like X, so the net learns how the solution
operator *moves* with fidelity.

Training (smoke_eval.py): all fidelities pooled into one set; each sample carries
its own f. HEADLINE eval queries f = hf_norm (= 1.0) -> the comparable HF
prediction. A "super-fidelity" variant queries several f values, fits a per-pixel
Richardson trend in f, and extrapolates past f = 1 toward the limit.

This module provides the thin FNO2d wrapper and the per-pixel Richardson
extrapolation helper. The pooled-training / multi-query logic lives in
smoke_eval.py.

References: herde2024poseidon (operator conditioned on a continuous scale/scalar);
richardson1911 (sequence extrapolation toward the discretization limit);
li2020fno (FNO backbone); perez2018film (FiLM).
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Tuple

import numpy as np
import torch

_AKASH = Path(__file__).resolve().parents[2]
if str(_AKASH) not in sys.path:
    sys.path.insert(0, str(_AKASH))

from common.backbone import FNO2d, param_count  # noqa: E402,F401

Grid = Tuple[int, int]


class FNO2dContinuousFidelity(FNO2d):
    """FNO2d that FiLMs on cond = [X, f].

    Identical to the winner's FNO2d (the backbone is conditioning-source
    agnostic); cond_dim must be d + 1. Constructed as FNO2d(cond_dim=d+1, ...).
    Kept as a named subclass purely for clarity / inspection.
    """
    pass


def richardson_extrapolate(f_query: np.ndarray, preds: np.ndarray, f_target: float) -> np.ndarray:
    """Per-pixel linear (Richardson) extrapolation of the fidelity trend.

    Given predictions at several fidelity coordinates, fit y(f) ≈ a + b·f
    independently per pixel by least squares and evaluate at `f_target`. Linear
    in the normalized fidelity coordinate is the simplest Richardson-style
    error-trend model (error ~ linear in the fidelity coordinate); extrapolating
    to f_target >= max(f_query) projects toward the high-fidelity limit.

    f_query: (K,) fidelity coords.   preds: (K, N, P) predictions per fidelity.
    returns: (N, P) extrapolated field at f_target.
    """
    K = f_query.shape[0]
    fq = np.asarray(f_query, dtype=np.float64)
    # design matrix [1, f]; closed-form LS over the K query points (shared across
    # all pixels), applied to preds reshaped (K, N*P).
    A = np.stack([np.ones(K), fq], axis=1)             # (K, 2)
    P = preds.reshape(K, -1).astype(np.float64)        # (K, N*P)
    coef, *_ = np.linalg.lstsq(A, P, rcond=None)       # (2, N*P): [a; b]
    out = coef[0] + coef[1] * float(f_target)          # (N*P,)
    return out.reshape(preds.shape[1], preds.shape[2])
