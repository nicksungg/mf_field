#!/usr/bin/env python
"""Condition-response decomposition of a model's test predictions.

Provenance: promoted from r3s3_lf_value-B1 mechanism turn 1
(`worktrees/r3s3_lf_value/B1/scratchpad/reanalysis_turn_1.py`,
`reanalysis_turn_1_results.md`). It is the instrument that separated the
coverage channel from the optimisation channel: two arms can have similar
nRMSE for entirely different reasons, and nRMSE alone cannot tell you whether
a model has learned a condition->field MAP at all.

For each labelled prediction set it reports, across the test split:

  nrmse                round metric (round2/eval/nrmse.py), recomputed
  response_amplitude   sigma_pred / sigma_hf, sigma_X = sqrt(mean_cells var_samples X)
                       -- how much of the true across-condition variability the
                       model reproduces
  response_alignment   mean_i cos(pred_i - mean_j pred_j, hf_i - mean_j hf_j)
                       -- whether that variability points where the truth does.
                       ~0 means "condition-independent noise": the model has no
                       usable condition->field map even if its nRMSE looks fine.
  own_spread           mean_i ||pred_i - mean_j pred_j|| / ||hf_i||
  copylf_*             the same statistics for the round's copy-LF reference
                       (skipped when the test split carries no LF, e.g. ifc_*)

and pairwise `mean_i ||A_i - B_i|| / ||hf_i||` between every labelled pair --
how far apart two arms are AS FUNCTIONS, which distinguishes "arm B is a
weaker A" from "arm B is arm A0 with extra compute".

Prediction files are .npz dumps with a (n_test, n_cells) array; the default key
is `pred_test`. Row order must match the dataset's test split order (assert it
by checking the printed nRMSE against the leg's own result JSON).

Usage
-----
  python tools/response_decomposition.py \
      --dataset sharp__cahn_hilliard \
      --pred A0=/path/A0/.../ch_e200_s0_preds.npz \
      --pred A1=/path/A1/.../ch_e200_s0_preds.npz \
      [--pred-key pred_test] [--split test] [--out /path/out.json]

Exit code 0 always (a measurement tool, never a gate).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np


def _eval_dir() -> Path:
    root = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"],
                               capture_output=True, text=True, check=True,
                               cwd=Path(__file__).resolve().parent).stdout.strip())
    return root / "mffp_autoresearch" / "round2" / "eval"


sys.path.insert(0, str(_eval_dir()))
import nrmse as NR  # noqa: E402
import panel_data as PD  # noqa: E402


def sigma(X: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.var(X, axis=0))))


def alignment(P: np.ndarray, H: np.ndarray) -> float:
    dP = P - P.mean(axis=0, keepdims=True)
    dH = H - H.mean(axis=0, keepdims=True)
    nP, nH = np.linalg.norm(dP, axis=1), np.linalg.norm(dH, axis=1)
    ok = (nP > 0) & (nH > 0)
    if not ok.any():
        return float("nan")
    return float(np.mean(np.sum(dP[ok] * dH[ok], axis=1) / (nP[ok] * nH[ok])))


def rel_dist(A: np.ndarray, B: np.ndarray, H: np.ndarray) -> float:
    return float(np.mean(np.linalg.norm(A - B, axis=1) / np.linalg.norm(H, axis=1)))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dataset", required=True, help="panel dataset name (panel_data convention)")
    ap.add_argument("--pred", action="append", required=True, metavar="LABEL=PATH.npz",
                    help="repeatable; label for the table + path to a preds .npz")
    ap.add_argument("--pred-key", default="pred_test", help="array key inside the npz")
    ap.add_argument("--split", default="test")
    ap.add_argument("--out", default=None, help="write the full record as JSON here")
    args = ap.parse_args(argv)

    data = PD.load_split(args.dataset, args.split)
    H = np.asarray(data["field_by_fid"][data["hf_fid"]], dtype=np.float64)
    sH = sigma(H)

    rec = {"dataset": args.dataset, "split": args.split, "n_test": int(H.shape[0]),
           "nrmse_def_hash": NR.NRMSE_DEF_HASH, "copylf_def_hash": PD.COPYLF_DEF_HASH,
           "hf_own_spread": float(np.mean(
               np.linalg.norm(H - H.mean(axis=0, keepdims=True), axis=1)
               / np.linalg.norm(H, axis=1))),
           "arms": {}}

    if data["lf_fids"]:
        C = PD.copylf_prediction(data, args.dataset)
        rec["copylf"] = {"nrmse": NR.nrmse(C, H), "response_amplitude": sigma(C) / sH,
                         "response_alignment": alignment(C, H)}
    else:
        rec["copylf"] = None
        rec["no_test_lf"] = True

    preds = {}
    for spec in args.pred:
        if "=" not in spec:
            ap.error(f"--pred needs LABEL=PATH, got {spec!r}")
        label, path = spec.split("=", 1)
        z = np.load(path)
        if args.pred_key not in z.files:
            ap.error(f"{path}: no key {args.pred_key!r} (has {z.files})")
        P = np.asarray(z[args.pred_key], dtype=np.float64)
        if P.shape != H.shape:
            ap.error(f"{path}: pred shape {P.shape} != HF target shape {H.shape}")
        preds[label] = P
        rec["arms"][label] = {
            "path": path,
            "nrmse": NR.nrmse(P, H),
            "response_amplitude": sigma(P) / sH,
            "response_alignment": alignment(P, H),
            "own_spread": float(np.mean(
                np.linalg.norm(P - P.mean(axis=0, keepdims=True), axis=1)
                / np.linalg.norm(H, axis=1))),
        }

    labels = list(preds)
    rec["pairwise_prediction_distance"] = {
        f"{a}->{b}": rel_dist(preds[a], preds[b], H)
        for i, a in enumerate(labels) for b in labels[i + 1:]
    }

    print(f"# {args.dataset} / {args.split} / n_test={H.shape[0]}")
    print(f"{'label':22s}{'nRMSE':>12s}{'amplitude':>12s}{'alignment':>12s}{'own_spread':>12s}")
    for lab in labels:
        e = rec["arms"][lab]
        print(f"{lab:22s}{e['nrmse']:12.6f}{e['response_amplitude']:12.4f}"
              f"{e['response_alignment']:12.4f}{e['own_spread']:12.4f}")
    if rec["copylf"]:
        e = rec["copylf"]
        print(f"{'copy-LF (reference)':22s}{e['nrmse']:12.6f}"
              f"{e['response_amplitude']:12.4f}{e['response_alignment']:12.4f}{'':>12s}")
    else:
        print("copy-LF: n/a (test split carries no LF fidelity)")
    print(f"{'HF (truth)':22s}{0.0:12.6f}{1.0:12.4f}{1.0:12.4f}{rec['hf_own_spread']:12.4f}")
    if rec["pairwise_prediction_distance"]:
        print("\n# pairwise prediction distance  mean_i ||A_i-B_i|| / ||hf_i||")
        for k, v in rec["pairwise_prediction_distance"].items():
            print(f"  {k:44s} {v:.5f}")

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        with open(args.out, "w") as f:
            json.dump(rec, f, indent=1)
        print(f"\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
