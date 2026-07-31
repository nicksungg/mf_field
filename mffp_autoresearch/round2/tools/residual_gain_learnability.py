#!/usr/bin/env python
"""Is a predictor's residual per-sample GAIN error learnable from the condition vector?

Provenance: promoted from `s1_poisson-B2` mechanism analysis turn 2
(`worktrees/s1_poisson/B2/scratchpad/reanalysis_turn_2.py`). There the winning
arm scored nRMSE 0.034250 (skill 0.9514) with 57.1 % of its remaining squared
error still per-sample amplitude; a leave-one-out LINEAR model of that gain on
the 5-D condition vector reached R^2 = 0.919 and would take the arm to 0.02431
(skill 0.675) — which is what turned "amplitude dominates the residual" into an
actionable batch-3 lever (a condition-conditioned calibration head) instead of
a restatement of the error decomposition.

`tools/field_error_decomposition.py` answers *how much* of the error is a
per-sample gain. This tool answers the follow-up: *is that gain a function of
something the model already has at inference?* If yes, a calibration head is a
cheap real lever. If no (R^2 <= 0), the amplitude error is sample-specific
noise and no head keyed on X can remove it — look at the field instead.

WHAT IT REPORTS
  frac_sq_error_from_gain        share of squared error explained by a per-sample
                                 scalar gain (same definition as
                                 field_error_decomposition.py)
  nRMSE / nRMSE_oracle_gain      the metric now, and with every sample rescaled
                                 by its own ORACLE gain (the floor a perfect
                                 calibration head would reach)
  gain_{mean,std,min,max}        the residual gain distribution
  loo.<model>.r2                 leave-one-out R^2 of the gain predicted from the
                                 condition vector (`ridge_linear`, `knn{1,3,5,10}`)
  loo.<model>.nRMSE_after_gain   nRMSE if the LOO-predicted gain were applied
  best_learnable_nRMSE / _skill  the best LOO row — the ATTAINABILITY ESTIMATE

HONESTY LABEL (must travel with any number this prints): the LOO fit uses the
TEST targets to build the gain, so `nRMSE_after_gain` is an UPPER BOUND on a
calibration head, not an achieved score. It is a headroom probe. It also says
nothing about whether the gain law can be *fitted from the training split* —
check `n_hf_train` in the output: with 5 HF training samples a 6-parameter
linear gain model is already saturated, and the honest design is to estimate the
law on the lower-fidelity levels and transfer it.

USAGE
  python tools/residual_gain_learnability.py \
      --pred_npz <preds_test.npz> [<b.npz> ...] [--labels a b] \
      --dataset ifc_poisson [--paper_bar 0.036] \
      [--pred_key pred --target_key target] [--out results.json]

The npz layout is the one `smoke_eval.py` writes beside its checkpoint
(`pred`, `target`, optional `work_grid`). Conditions come from
`round1/eval/panel_data.py` (test split, HF fidelity) and must have the same
sample count as the prediction file.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np


def _repo_root() -> Path:
    out = subprocess.run(["git", "rev-parse", "--show-toplevel"], check=True,
                         capture_output=True, text=True,
                         cwd=Path(__file__).resolve().parent)
    return Path(out.stdout.strip())


_EVAL = _repo_root() / "mffp_autoresearch" / "round1" / "eval"
sys.path.insert(0, str(_EVAL))
import nrmse as nrmse_mod   # noqa: E402
import panel_data           # noqa: E402


def loo_gain_models(Xs: np.ndarray, b: np.ndarray, p: np.ndarray,
                    y: np.ndarray, ridge: float) -> dict:
    n = len(b)
    out = {}
    denom = max(((b - b.mean()) ** 2).sum(), 1e-300)

    D = np.sqrt(((Xs[:, None, :] - Xs[None, :, :]) ** 2).sum(-1))
    np.fill_diagonal(D, np.inf)
    order = np.argsort(D, axis=1)
    for k in (1, 3, 5, 10):
        if k >= n:
            continue
        bh = b[order[:, :k]].mean(1)
        out[f"knn{k}"] = dict(
            r2=float(1 - ((b - bh) ** 2).sum() / denom),
            nRMSE_after_gain=float(nrmse_mod.nrmse(bh[:, None] * p, y)))

    A = np.concatenate([np.ones((n, 1)), Xs], 1)
    bh = np.empty(n)
    for i in range(n):
        m = np.ones(n, bool); m[i] = False
        w = np.linalg.solve(A[m].T @ A[m] + ridge * np.eye(A.shape[1]),
                            A[m].T @ b[m])
        bh[i] = A[i] @ w
    out["ridge_linear"] = dict(
        n_parameters=int(A.shape[1]),
        r2=float(1 - ((b - bh) ** 2).sum() / denom),
        nRMSE_after_gain=float(nrmse_mod.nrmse(bh[:, None] * p, y)))
    return out


def analyse(pred, target, Xte, paper_bar, ridge, n_hf_train):
    p = np.asarray(pred, np.float64)
    y = np.asarray(target, np.float64)
    if p.shape != y.shape or p.ndim != 2:
        raise ValueError(f"need matching 2-D arrays, got {p.shape} vs {y.shape}")
    b = (p * y).sum(1) / np.maximum((p * p).sum(1), 1e-300)     # oracle rescale
    a = (p * y).sum(1) / np.maximum((y * y).sum(1), 1e-300)     # y-projection
    err2 = ((p - y) ** 2).sum(1)
    gain2 = (a - 1.0) ** 2 * (y * y).sum(1)
    lo, hi = Xte.min(0), Xte.max(0)
    Xs = (Xte - lo) / np.maximum(hi - lo, 1e-12)
    loo = loo_gain_models(Xs, b, p, y, ridge)
    best = min(loo, key=lambda k: loo[k]["nRMSE_after_gain"])
    rec = dict(
        n_samples=int(len(y)), n_hf_train=int(n_hf_train),
        cond_dim=int(Xte.shape[1]),
        nRMSE=float(nrmse_mod.nrmse(p, y)),
        frac_sq_error_from_gain=float(gain2.sum() / max(err2.sum(), 1e-300)),
        nRMSE_oracle_gain=float(nrmse_mod.nrmse(b[:, None] * p, y)),
        gain_mean=float(b.mean()), gain_std=float(b.std()),
        gain_min=float(b.min()), gain_max=float(b.max()),
        loo=loo, best_loo_model=best,
        best_learnable_nRMSE=float(loo[best]["nRMSE_after_gain"]),
        honesty_label=("LOO gain models are fitted with the TEST targets; every "
                       "nRMSE_after_gain is an UPPER BOUND on a calibration "
                       "head, not an achieved score. With n_hf_train <= cond_dim+1 "
                       "a linear gain model cannot be fitted from the HF split "
                       "alone — estimate it on the lower-fidelity levels and "
                       "transfer."),
    )
    if paper_bar:
        rec["skill"] = rec["nRMSE"] / paper_bar
        rec["skill_oracle_gain"] = rec["nRMSE_oracle_gain"] / paper_bar
        rec["best_learnable_skill"] = rec["best_learnable_nRMSE"] / paper_bar
    return rec


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--pred_npz", nargs="+", required=True)
    ap.add_argument("--labels", nargs="*", default=None)
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--pred_key", default="pred")
    ap.add_argument("--target_key", default="target")
    ap.add_argument("--paper_bar", type=float, default=None)
    ap.add_argument("--ridge", type=float, default=1e-3)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    te = panel_data.load_split(args.dataset, "test")
    tr = panel_data.load_split(args.dataset, "train")
    hf = te["hf_fid"]
    Xte = np.asarray(te["cond_by_fid"][hf], np.float64)
    n_hf_train = len(tr["cond_by_fid"][tr["hf_fid"]])

    labels = args.labels or [Path(f).parent.name or Path(f).stem
                             for f in args.pred_npz]
    if len(labels) != len(args.pred_npz):
        raise SystemExit("--labels must match --pred_npz in length")

    res = {"dataset": args.dataset, "nrmse_def_hash": nrmse_mod.NRMSE_DEF_HASH,
           "per_file": {}}
    for lab, f in zip(labels, args.pred_npz):
        z = np.load(f)
        p, y = z[args.pred_key], z[args.target_key]
        if len(p) != len(Xte):
            raise SystemExit(f"{lab}: {len(p)} predictions vs {len(Xte)} test "
                             f"conditions for {args.dataset}")
        rec = analyse(p, y, Xte, args.paper_bar, args.ridge, n_hf_train)
        rec["path"] = str(f)
        res["per_file"][lab] = rec

    txt = json.dumps(res, indent=1)
    print(txt)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(txt + "\n")
        print(f"[wrote] {args.out}")


if __name__ == "__main__":
    main()
