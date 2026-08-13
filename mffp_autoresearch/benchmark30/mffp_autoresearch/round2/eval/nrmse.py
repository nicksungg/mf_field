"""The round's single nRMSE definition (spec §2). Every score cites this file.

nRMSE(pred, target) = mean_i ||pred_i - target_i||_2 / ||target_i||_2

`NRMSE_DEF_HASH` is the sha256 of this file's bytes; result JSONs carry it so
that two scores computed under different metric definitions can never be
silently compared (seam assertion, spec §5.3).
"""
from __future__ import annotations

import hashlib
import pathlib

import numpy as np


def nrmse(pred: np.ndarray, target: np.ndarray) -> float:
    pred = np.asarray(pred, dtype=np.float64)
    target = np.asarray(target, dtype=np.float64)
    if pred.shape != target.shape or pred.ndim != 2:
        raise ValueError(
            f"shape mismatch or not 2-D: pred {pred.shape} vs target {target.shape}"
        )
    if not (np.isfinite(pred).all() and np.isfinite(target).all()):
        raise ValueError("non-finite values in pred or target")
    denom = np.linalg.norm(target, axis=1)
    if (denom == 0).any():
        raise ValueError("zero-norm target sample")
    return float(np.mean(np.linalg.norm(pred - target, axis=1) / denom))


def skill(model_nrmse: float, copylf_nrmse: float) -> float:
    if copylf_nrmse <= 0:
        raise ValueError(f"copy-LF nRMSE must be positive, got {copylf_nrmse}")
    return float(model_nrmse) / float(copylf_nrmse)


def panel_geomean(skills: dict) -> float:
    vals = np.array(list(skills.values()), dtype=np.float64)
    if vals.size == 0 or (vals <= 0).any():
        raise ValueError(f"skills must be non-empty and positive: {skills}")
    return float(np.exp(np.mean(np.log(vals))))


def bootstrap_ci(per_seed_values, n_boot: int = 10000, seed: int = 0):
    """Return (mean, lo95, hi95): percentile bootstrap over per-seed values."""
    vals = np.asarray(per_seed_values, dtype=np.float64)
    if vals.size == 0:
        raise ValueError("no values")
    rng = np.random.default_rng(seed)
    boots = rng.choice(vals, size=(n_boot, vals.size), replace=True).mean(axis=1)
    return float(vals.mean()), float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))


NRMSE_DEF_HASH = hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
