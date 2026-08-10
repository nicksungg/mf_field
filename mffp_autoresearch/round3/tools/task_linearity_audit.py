#!/usr/bin/env python
"""Model-free task-structure audit: is this cell a closed-form task in disguise,
and is its condition->field map even smooth enough to learn?

WHAT IT MEASURES (per dataset, no model, no training, no seed)
--------------------------------------------------------------
1. **oracle_affine_residual** — nRMSE of a min-norm least-squares affine map
   ``condition -> field`` fitted ON THE EVALUATED ROWS THEMSELVES (an oracle, an
   upper bound on any affine method). Same estimator class as the certified
   `affine_on_hf_train` floor in `state/anchors/launch_anchors.json`.
   Near zero => the solution operator IS affine in the condition and a nonlinear
   field model is structurally wasting capacity there.
   Measured on r3s2_field_reach-B1: ifc_poisson 2.9e-08 (certified 5.4e-16),
   ifc_heat 0.0377 (reproduces the certified value exactly), allen_cahn 0.4598,
   cahn_hilliard 0.4997, fisher_kpp 0.0295.

2. **ensemble rank** — PCA rank of the centred field ensemble at 95 %/99 %
   variance, and the variance captured by the first `cond_dim` components.
   ifc_poisson: rank 5 at 99 %, 1.000000 of the variance in 5 PCs.

3. **map smoothness** — median relative field difference between each row and its
   nearest neighbour in standardised condition space, divided by the median
   random-pair difference. -> 1 means "nearest in condition is as different as
   random", i.e. the condition->field map is effectively non-smooth at the
   available sampling density and NO amount of extra conditioning helps.
   Measured: cahn_hilliard 0.980, allen_cahn 0.791, fisher_kpp 0.798.

4. **level domination** — fraction of field energy surviving removal of the
   ensemble mean, and the fraction of pixels saturated at >= 0.9 x max|field|.
   Guards the project's `rel-l2-is-level-dominated` trap: fisher_kpp keeps only
   0.0050 of its variance after mean removal.

WHY IT GENERALISES
------------------
It touches only the dataset (through `round2/eval/panel_data.py`) and the round's
own `nrmse.py`. Run it BEFORE committing GPU time to a cell: it separates cells
where nonlinear multi-fidelity fusion can pay from cells that a 6-parameter
closed form already solves, and it predicts which cells are hard for reasons no
architecture change addresses.

INVOCATION
----------
    python tools/task_linearity_audit.py --datasets a,b,c [--split test] \\
        [--max-samples 128] [--out report.json]

Provenance: r3s2_field_reach-B1 turns 2 and 3.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np


def _bootstrap_paths():
    here = os.path.dirname(os.path.abspath(__file__))
    round_root = os.path.dirname(here)                       # .../round3
    project_root = os.path.dirname(os.path.dirname(round_root))
    eval_dir = os.path.join(project_root, "mffp_autoresearch", "round2", "eval")
    if eval_dir not in sys.path:
        sys.path.insert(0, eval_dir)
    return project_root, eval_dir


PROJECT_ROOT, EVAL_DIR = _bootstrap_paths()
import panel_data          # noqa: E402
import nrmse as nrmse_mod  # noqa: E402


def affine_fit_predict(C: np.ndarray, Y: np.ndarray) -> np.ndarray:
    """Min-norm least-squares affine map condition->field, in-sample (ORACLE).

    Same estimator as the certified `affine_on_hf_train` floor: `[C, 1] B ~ Y`
    via lstsq. In-sample by design; it is a ceiling, not a prediction arm.
    """
    A = np.concatenate([np.asarray(C, dtype=np.float64),
                        np.ones((C.shape[0], 1))], axis=1)
    B, *_ = np.linalg.lstsq(A, np.asarray(Y, dtype=np.float64), rcond=None)
    return A @ B


def audit(ds: str, split: str, max_samples: int, rng_seed: int = 0) -> dict:
    sp = panel_data.load_split(ds, split)
    hf = sp["hf_fid"]
    Y = np.asarray(sp["field_by_fid"][hf], dtype=np.float64)
    C = np.asarray(sp["cond_by_fid"][hf], dtype=np.float64)
    n = int(min(max_samples, Y.shape[0]))
    Y, C = Y[:n], C[:n]

    Yc = Y - Y.mean(axis=0, keepdims=True)
    ev = np.linalg.svd(Yc, compute_uv=False) ** 2
    cum = np.cumsum(ev) / ev.sum()
    rank95 = int(np.searchsorted(cum, 0.95) + 1)
    rank99 = int(np.searchsorted(cum, 0.99) + 1)
    var_at_cond = float(cum[min(C.shape[1], len(cum)) - 1])

    resid = float(nrmse_mod.nrmse(affine_fit_predict(C, Y), Y))

    Cs = (C - C.mean(axis=0)) / (C.std(axis=0) + 1e-12)
    D = ((Cs[:, None, :] - Cs[None, :, :]) ** 2).sum(-1)
    np.fill_diagonal(D, np.inf)
    j = D.argmin(axis=1)
    den = np.linalg.norm(Y, axis=1)
    nn_rel = float(np.median(np.linalg.norm(Y - Y[j], axis=1) / den))
    perm = np.random.default_rng(rng_seed).permutation(n)
    rand_rel = float(np.median(np.linalg.norm(Y - Y[perm], axis=1) / den))

    a = np.abs(Y)
    return {
        "n": n, "cond_dim": int(C.shape[1]), "hf_fid": int(hf), "split": split,
        "grid_shape": list(sp["grid_shape_by_fid"][hf]),
        "rank95": rank95, "rank99": rank99, "var_in_first_cond_dim_pcs": var_at_cond,
        "oracle_affine_residual_nrmse": resid,
        "nn_cond_rel_field_diff_median": nn_rel,
        "random_pair_rel_field_diff_median": rand_rel,
        "map_smoothness_ratio": nn_rel / rand_rel if rand_rel else None,
        "mean_removed_variance_fraction": float((Yc ** 2).sum() / (Y ** 2).sum()),
        "saturated_pixel_fraction": float((a >= 0.9 * a.max()).mean()),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--datasets", required=True,
                    help="comma-separated dataset names as they appear under data_root")
    ap.add_argument("--split", default="test")
    ap.add_argument("--max-samples", type=int, default=128)
    ap.add_argument("--affine-tol", type=float, default=1e-4,
                    help="oracle affine residual below this => CLOSED-FORM TASK")
    ap.add_argument("--smoothness-tol", type=float, default=0.95,
                    help="map_smoothness_ratio above this => NON-SMOOTH MAP")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    print("nrmse_def_hash:", nrmse_mod.NRMSE_DEF_HASH)
    rows = {}
    hdr = (f"{'dataset':26s} {'n':>5s} {'cond':>5s} {'r95':>5s} {'r99':>5s} "
           f"{'var@cond':>9s} {'oracle affine':>14s} {'smoothness':>11s} "
           f"{'meanrm var':>11s} {'sat frac':>9s}  verdict")
    print(hdr)
    for ds in [s.strip() for s in args.datasets.split(",") if s.strip()]:
        try:
            r = audit(ds, args.split, args.max_samples)
        except Exception as exc:                       # noqa: BLE001
            print(f"{ds:26s} ERROR: {exc}")
            rows[ds] = {"error": str(exc)}
            continue
        verdict = []
        if r["oracle_affine_residual_nrmse"] < args.affine_tol:
            verdict.append("CLOSED_FORM_TASK")
        if (r["map_smoothness_ratio"] or 0) > args.smoothness_tol:
            verdict.append("NON_SMOOTH_MAP")
        if r["mean_removed_variance_fraction"] < 0.05:
            verdict.append("LEVEL_DOMINATED")
        rows[ds] = dict(r, verdict=verdict)
        print(f"{ds:26s} {r['n']:5d} {r['cond_dim']:5d} {r['rank95']:5d} {r['rank99']:5d} "
              f"{r['var_in_first_cond_dim_pcs']:9.6f} {r['oracle_affine_residual_nrmse']:14.6g} "
              f"{r['map_smoothness_ratio']:11.4f} {r['mean_removed_variance_fraction']:11.5f} "
              f"{r['saturated_pixel_fraction']:9.4f}  "
              f"{','.join(verdict) if verdict else 'mf-fusion-relevant'}")
    if args.out:
        with open(args.out, "w") as f:
            json.dump({"_nrmse_def_hash": nrmse_mod.NRMSE_DEF_HASH,
                       "_split": args.split, "_max_samples": args.max_samples,
                       "datasets": rows}, f, indent=1)
        print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
