"""Shared evaluation metrics for the fair MFFP benchmark.

Every model family writes, in addition to its scalar `nRMSE`, the array of
**per-test-sample relative-L2 errors** so the plotting layer can draw real
bootstrap confidence intervals (rather than fabricated error bars).

Definitions (all on the HF test field, flattened per sample):

    rel_l2_i = ||pred_i - y_i||_2 / max(||y_i||_2, eps)

Reported per (model, dataset):
    nRMSE_persample_mean = mean_i rel_l2_i
    bootstrap 95% CI of that mean over the test samples.

Note: this per-sample mean differs slightly from the aggregate
sqrt(sum_i ||Δ_i||² / sum_i ||y_i||²) some wrappers print; we keep BOTH —
the aggregate stays as `nRMSE` for backward-compat, and the per-sample array
is the basis for error bars. Bootstrapping resamples the *samples*, so it is
valid for either statistic; we expose a helper for the mean.
"""
from __future__ import annotations

from typing import Sequence

import numpy as np


def per_sample_rel_l2(pred: np.ndarray, target: np.ndarray, eps: float = 1e-8) -> np.ndarray:
    """Per-sample relative L2 error.

    pred, target: (N, D) flat fields (any matching shape; flattened past axis 0).
    Returns (N,) float64 array of ||pred_i - tgt_i|| / max(||tgt_i||, eps).
    """
    p = np.asarray(pred, dtype=np.float64).reshape(pred.shape[0], -1)
    t = np.asarray(target, dtype=np.float64).reshape(target.shape[0], -1)
    num = np.sqrt(((p - t) ** 2).sum(axis=1))
    den = np.sqrt((t ** 2).sum(axis=1))
    den = np.maximum(den, eps)
    return num / den


def bootstrap_ci(values: Sequence[float], n_boot: int = 10000,
                 alpha: float = 0.05, seed: int = 0) -> dict:
    """Nonparametric bootstrap CI of the mean of `values`.

    Returns {mean, lo, hi, std, sem, n} where [lo, hi] is the (1-alpha) CI of
    the mean (percentile method). For n<=1 the CI collapses to the point value.
    """
    v = np.asarray(values, dtype=np.float64)
    v = v[np.isfinite(v)]
    n = int(v.size)
    if n == 0:
        return {"mean": float("nan"), "lo": float("nan"), "hi": float("nan"),
                "std": float("nan"), "sem": float("nan"), "n": 0}
    mean = float(v.mean())
    if n == 1:
        return {"mean": mean, "lo": mean, "hi": mean, "std": 0.0, "sem": 0.0, "n": 1}
    rng = np.random.default_rng(seed)
    # vectorised: (n_boot, n) index draw → resampled means
    idx = rng.integers(0, n, size=(n_boot, n))
    boot_means = v[idx].mean(axis=1)
    lo = float(np.percentile(boot_means, 100 * (alpha / 2)))
    hi = float(np.percentile(boot_means, 100 * (1 - alpha / 2)))
    return {"mean": mean, "lo": lo, "hi": hi,
            "std": float(v.std(ddof=1)), "sem": float(v.std(ddof=1) / np.sqrt(n)),
            "n": n}


def summarize_per_sample(rel_l2: np.ndarray, seed: int = 0) -> dict:
    """Convenience: aggregate nRMSE-style stats + bootstrap CI from per-sample errors."""
    r = np.asarray(rel_l2, dtype=np.float64)
    ci = bootstrap_ci(r, seed=seed)
    return {
        "rel_l2_mean": ci["mean"],
        "rel_l2_ci95_lo": ci["lo"],
        "rel_l2_ci95_hi": ci["hi"],
        "rel_l2_std": ci["std"],
        "n_samples": ci["n"],
    }


def finalize_and_write(out_path, *, model: str, dataset: str,
                       pred, target, work_grid, n_params: int,
                       train_seconds: float, eval_seconds: float,
                       latency_ms_per_sample=None, peak_mem_mb=None,
                       seed: int = 0, extra: dict | None = None) -> dict:
    """Compute the standardized fair-benchmark result and write it to out_path.

    pred, target: (N, prod(work_grid)) full-field predictions/targets on the
        common working grid (every model evaluates here for fairness).
    Writes BOTH the backward-compatible aggregate `nRMSE` (so eval/score.py keeps
    working) and the per-sample rel-L2 array + 95% bootstrap CI used for plots,
    plus compute/size/latency metadata.
    """
    import json
    from pathlib import Path

    p = np.asarray(pred, dtype=np.float64).reshape(np.asarray(pred).shape[0], -1)
    t = np.asarray(target, dtype=np.float64).reshape(np.asarray(target).shape[0], -1)
    rel = per_sample_rel_l2(p, t)
    ci = bootstrap_ci(rel, seed=seed)
    # aggregate nRMSE (ratio of sums) for backward-compat with score.py
    agg = float(np.sqrt((((p - t) ** 2).sum()) / max((t ** 2).sum(), 1e-12)))

    res = {
        "model": model,
        "dataset": dataset,
        "splits": {
            "test_hf": {
                "nRMSE": agg,
                "rel_l2_mean": ci["mean"],
                "rel_l2_ci95_lo": ci["lo"],
                "rel_l2_ci95_hi": ci["hi"],
                "rel_l2_std": ci["std"],
                "rel_l2_per_sample": [float(x) for x in rel],
                "n_samples": ci["n"],
            }
        },
        "n_params": int(n_params),
        "train_seconds": float(train_seconds),
        "eval_seconds": float(eval_seconds),
        "latency_ms_per_sample": (None if latency_ms_per_sample is None
                                  else float(latency_ms_per_sample)),
        "peak_mem_mb": (None if peak_mem_mb is None else float(peak_mem_mb)),
        "work_grid": [int(work_grid[0]), int(work_grid[1])],
        "eval_protocol": "full_field_on_working_grid",
    }
    if extra:
        res.update(extra)
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2))
    return res


__all__ = ["per_sample_rel_l2", "bootstrap_ci", "summarize_per_sample",
           "finalize_and_write"]
