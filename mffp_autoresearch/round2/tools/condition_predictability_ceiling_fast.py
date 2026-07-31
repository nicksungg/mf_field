#!/usr/bin/env python
"""`condition_predictability_ceiling.py` with a float32 / capped-pair estimator
path — same formulas, same output schema, ~50x faster on 256² panel datasets.

WHY THIS EXISTS
---------------
The frozen tool's float64 all-pairs path did not finish a single 256² dataset
inside a 20-minute cap on the round's login node (1 visible CPU, load average
28; killed at >20 min on `sharp__allen_cahn_2d`), which makes it unusable for
the mechanism analyst's turn budget — the place where a training-free ceiling is
most often wanted. This wrapper IMPORTS the frozen tool and swaps in float32
accumulation for the field arithmetic plus a capped random pair sample; it
touches nothing in the original file, so the round's byte-frozen definitions
(`loo_knn_curve`, `pair_extrapolation`, `support_verdict`, the JSON schema and
the printed line) remain the single source of truth.

VALIDATION (do it yourself, it is one command)
----------------------------------------------
    python tools/condition_predictability_ceiling_fast.py --validate \
        --datasets ext__helmholtz_2d --out /tmp/val.json

runs BOTH paths on the same split and prints the absolute difference in the
k-NN bound and the pair intercept. Measured on `ext__helmholtz_2d` at the
register turn: k-NN bound 1.1150040817905758 vs 1.1150040817905758, |Δ| = 0.0,
same k* — and the pair intercept |Δ| = 2.1e-11 when the pair cap is matched
(`--max_pairs 200000`) against 2.1e-2 at the default cap 20000. **Read that
carefully: the float32 swap costs ~1e-11; the pair-intercept difference at the
default cap is PAIR SUBSAMPLING, not precision.** If you quote a pair intercept,
either match `--max_pairs` to the frozen tool or report the cap. r2s4-B2 turn 1
recorded the same k-NN agreement on the LF-upsampled target
(1.4574099779803809 fast vs 1.4574099777246128 exact, |Δ| = 2.6e-10; turn 1's
prose rounds it as 1.8e-10). Runtime: `sharp__allen_cahn_2d` (400 × 256²) is
35 s end-to-end on the fast path, against a >20-min unfinished exact run on the
same login node at turn 1. Re-validate before trusting the fast path on a
dataset whose fields have an unusual dynamic range — float32 accumulation over
n_cells ≈ 65 k is where the difference would show.

Independent seam check: the fast path's `sharp__allen_cahn_2d` k-NN ceiling
176.2813 at k* = 8 reproduces r2s4-B1's float64 value 176.28128331491402 (same
k*), computed by a different script on the same split.

READ IT AS
----------
Identical to `condition_predictability_ceiling.py` — see that file's READ IT AS.
The output JSON gains `_estimator_path` and `_max_pairs` so a downstream reader
can tell which path produced a number.

USAGE
-----
    source "$PROJECT_ROOT/.venv/bin/activate"
    python tools/condition_predictability_ceiling_fast.py \
        --datasets PANEL --out /path/ceiling.json [--max_pairs 20000]
    # every other flag of the frozen tool (--ks, --n_bins, --preds,
    # --data_root) is accepted and forwarded unchanged.

Provenance: promoted from `r2s4_diag-B2` mechanism turn 1
(`worktrees/r2s4_diag/B2/scratchpad/reanalysis_turn_1.py`,
`loo_knn_curve_fast` / `pair_extrapolation_fast`; validation artefact
`scratchpad/t1_fast_helmholtz_validation.json`). The estimators themselves are
r2s4_diag-B1's (card part 6 T2-F1…T2-F6).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import condition_predictability_ceiling as CPC            # noqa: E402

PAIR_CHUNK_FAST = 64
FAST_MAX_PAIRS = 20000


def loo_knn_curve_fast(C, Y, ks):
    """Same recursion as CPC.loo_knn_curve; Y may be float32 (caller's choice)."""
    n = C.shape[0]
    ks = [k for k in ks if k <= n - 1]
    if not ks:
        return {}, None
    kmax = max(ks)
    d2 = ((C[:, None, :] - C[None, :, :]) ** 2).sum(2)
    np.fill_diagonal(d2, np.inf)
    order = np.argsort(d2, axis=1)[:, :kmax]
    ynorm = np.linalg.norm(Y.astype(np.float64), axis=1)
    E = {k: np.zeros(n) for k in ks}
    acc = np.empty(Y.shape[1], dtype=np.float64)
    for i in range(n):
        acc[:] = 0.0
        for pos in range(kmax):
            acc += Y[order[i, pos]]
            k = pos + 1
            if k in E:
                r = Y[i] - acc / k
                E[k][i] = float(r @ r)
    out = {}
    for k in ks:
        e = E[k]
        out[k] = {
            "pooled_resid_energy": float(e.sum()),
            "rel_l2_mean": float(np.mean(np.sqrt(e) / ynorm)),
            "rel_l2_mean_debiased": float(
                np.mean(np.sqrt(e / (1.0 + 1.0 / k)) / ynorm)),
        }
    return out, min(out, key=lambda k: out[k]["rel_l2_mean_debiased"])


def pair_extrapolation_fast(C, Y, n_bins=8, max_pairs=FAST_MAX_PAIRS, rng_seed=0):
    n = C.shape[0]
    iu = np.triu_indices(n, 1)
    rng = np.random.default_rng(rng_seed)
    if iu[0].size > max_pairs:
        sel = rng.choice(iu[0].size, max_pairs, replace=False)
        ii, jj = iu[0][sel], iu[1][sel]
    else:
        ii, jj = iu
    if ii.size == 0:
        return {"bins": [], "d_min": None, "d_median": None,
                "extrap_pair_rel_at_d0": float("nan"), "n_pairs_used": 0}
    d = np.linalg.norm(C[ii] - C[jj], axis=1)
    ynorm = np.linalg.norm(Y.astype(np.float64), axis=1)
    e = np.empty(d.size)
    for s in range(0, d.size, PAIR_CHUNK_FAST):
        D = Y[ii[s:s + PAIR_CHUNK_FAST]] - Y[jj[s:s + PAIR_CHUNK_FAST]]
        e[s:s + PAIR_CHUNK_FAST] = np.einsum("ij,ij->i", D, D, dtype=np.float64)
    rel = np.sqrt(e) / (np.sqrt(2.0) * 0.5 * (ynorm[ii] + ynorm[jj]))
    qs = np.quantile(d, np.linspace(0, 1, n_bins + 1))
    bins = []
    for b in range(n_bins):
        m = (d >= qs[b]) & ((d <= qs[b + 1]) if b == n_bins - 1 else (d < qs[b + 1]))
        if m.sum() < 5:
            continue
        bins.append({"d_mid": float(d[m].mean()), "n": int(m.sum()),
                     "mean_pair_rel": float(rel[m].mean())})
    if len(bins) >= 2:
        x0, x1 = bins[0]["d_mid"], bins[1]["d_mid"]
        y0, y1 = bins[0]["mean_pair_rel"], bins[1]["mean_pair_rel"]
        r0 = float(y0 - (y1 - y0) / (x1 - x0) * x0)
    else:
        r0 = float("nan")
    return {"bins": bins, "d_min": float(d.min()), "d_median": float(np.median(d)),
            "extrap_pair_rel_at_d0": r0, "n_pairs_used": int(d.size)}


def _patch(max_pairs):
    """Swap the two estimators and force float32 fields inside CPC.load_split."""
    orig_load = CPC.load_split

    def load_split_f32(name, data_root):
        C_tr, C_te, Y_tr, Y_te = orig_load(name, data_root)
        return C_tr, C_te, Y_tr.astype(np.float32), Y_te
    CPC.load_split = load_split_f32
    CPC.loo_knn_curve = loo_knn_curve_fast
    CPC.pair_extrapolation = (
        lambda C, Y, n_bins=8, mp=200000, rng_seed=0:
        pair_extrapolation_fast(C, Y, n_bins, max_pairs, rng_seed))
    return orig_load


def validate(names, data_root, ks, n_bins, max_pairs, out_path):
    """Run BOTH paths on the same split and report the absolute difference."""
    rows = []
    for name in names:
        C_tr, _, Y_tr64, _ = CPC.load_split(name, Path(data_root))
        Y_tr32 = Y_tr64.astype(np.float32)
        t0 = time.time()
        c_ex, k_ex = CPC.loo_knn_curve(C_tr, Y_tr64, ks)
        p_ex = CPC.pair_extrapolation(C_tr, Y_tr64, n_bins, 200000)
        t_ex = time.time() - t0
        t0 = time.time()
        c_fa, k_fa = loo_knn_curve_fast(C_tr, Y_tr32, ks)
        p_fa = pair_extrapolation_fast(C_tr, Y_tr32, n_bins, max_pairs)
        t_fa = time.time() - t0
        b_ex = c_ex[k_ex]["rel_l2_mean_debiased"]
        b_fa = c_fa[k_fa]["rel_l2_mean_debiased"]
        row = {"dataset": name, "n_train": int(C_tr.shape[0]),
               "n_cells": int(Y_tr64.shape[1]),
               "knn_bound_exact": b_ex, "knn_bound_fast": b_fa,
               "knn_bound_abs_diff": abs(b_ex - b_fa),
               "k_star_exact": k_ex, "k_star_fast": k_fa,
               "pair_intercept_exact": p_ex["extrap_pair_rel_at_d0"],
               "pair_intercept_fast": p_fa["extrap_pair_rel_at_d0"],
               "pair_intercept_abs_diff": abs(p_ex["extrap_pair_rel_at_d0"]
                                              - p_fa["extrap_pair_rel_at_d0"]),
               "seconds_exact": t_ex, "seconds_fast": t_fa,
               "speedup": t_ex / max(t_fa, 1e-9)}
        rows.append(row)
        print(f"[{name}] knn bound {b_ex:.16f} vs {b_fa:.16f} "
              f"(|d| {row['knn_bound_abs_diff']:.3e}, k* {k_ex} vs {k_fa}) | "
              f"pair intercept |d| {row['pair_intercept_abs_diff']:.3e} | "
              f"{t_ex:.1f}s vs {t_fa:.1f}s ({row['speedup']:.1f}x)", flush=True)
    if out_path:
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        Path(out_path).write_text(json.dumps(
            {"_tool": "condition_predictability_ceiling_fast --validate",
             "rows": rows}, indent=1))
        print("[wrote]", out_path)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=True)
    ap.add_argument("--datasets", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--data_root", default=None)
    ap.add_argument("--ks", default=CPC.KS_DEFAULT)
    ap.add_argument("--n_bins", type=int, default=8)
    ap.add_argument("--max_pairs", type=int, default=FAST_MAX_PAIRS)
    ap.add_argument("--preds", default=None)
    ap.add_argument("--validate", action="store_true",
                    help="run BOTH paths and report the difference (no ceiling JSON)")
    a = ap.parse_args()

    if a.datasets.upper() == "PANEL":
        names = list(CPC.CFG["panel"])
    elif a.datasets.upper() == "GUARD":
        names = list(CPC.CFG["guard_set"])
    else:
        names = [s for s in a.datasets.split(",") if s]
    data_root = a.data_root or str(CPC.PATHS["stripped_data_root"])
    ks = [int(k) for k in a.ks.split(",")]

    if a.validate:
        return validate(names, data_root, ks, a.n_bins, a.max_pairs, a.out)

    _patch(a.max_pairs)
    argv = ["condition_predictability_ceiling_fast",
            "--datasets", a.datasets, "--out", a.out,
            "--data_root", data_root, "--ks", a.ks,
            "--n_bins", str(a.n_bins), "--max_pairs", str(a.max_pairs)]
    if a.preds:
        argv += ["--preds", a.preds]
    old_argv, sys.argv = sys.argv, argv
    try:
        CPC.main()
    finally:
        sys.argv = old_argv
    doc = json.load(open(a.out))
    doc["_tool"] = "condition_predictability_ceiling_fast"
    doc["_estimator_path"] = "fast_float32_capped_pairs"
    doc["_max_pairs"] = int(a.max_pairs)
    doc["_frozen_tool"] = "condition_predictability_ceiling.py (imported, unmodified)"
    Path(a.out).write_text(json.dumps(doc, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
