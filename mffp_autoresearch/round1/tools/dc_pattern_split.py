#!/usr/bin/env python
"""Is a field prediction's score real, or is it just the DC (spatial-mean) term?

Provenance: promoted from `s5_tuning-B1` mechanism turn 3
(`worktrees/s5_tuning/B1/scratchpad/reanalysis_turn_3b.py`).

WHY THIS EXISTS
---------------
On `sharp__allen_cahn_2d` the round's certified champion scores nRMSE 0.2648 — and
the per-sample Pearson correlation between its SPATIALLY DEMEANED prediction and the
demeaned HF field is 0.011, with a pattern-only nRMSE of 1.018 (exactly the value of
predicting zero pattern). It scores what it scores because 98% of that field's energy
sits in the DC term and the model guesses one scalar per sample. It is in fact WORSE
than the constant-field oracle (0.2591). Any skill number on such a dataset is a
measurement of mean-level regression, not of field prediction — run this before
interpreting one.

This is complementary to `field_error_decomposition.py` (s1_poisson-B1), which splits
error into per-sample GAIN vs structure and centers by the across-sample MEAN FIELD.
This tool centers each sample by ITS OWN SPATIAL MEAN and adds the constant-field
oracle, which is what separates "predicts a field" from "predicts a level".

WHAT IT REPORTS
---------------
per split (once):
  nrmse_constant_field_oracle   score of predicting each test sample's own spatial
                                mean everywhere -- the level-only ceiling
  hf_dc_energy_share            share of HF energy in the DC term (how much of the
                                metric is winnable without any pattern at all)
  nrmse_zero_predictor          always 1.0 by definition; printed as the other anchor
per arm:
  nrmse_raw                     the round's metric (eval/nrmse.py)
  nrmse_pattern_only            rel-L2 of (pred - mean(pred)) vs (hf - mean(hf));
                                ~1.0 means the pattern is worth nothing
  corr_demeaned_mean/median     per-sample Pearson r of the demeaned fields
  relerr_of_spatial_mean        how well the level itself is predicted
  frac_samples_pattern_useless  share of samples with pattern-only rel-L2 >= 1
  verdict                       LEVEL_ONLY / WEAK_PATTERN / REAL_PATTERN

READ IT AS
----------
`corr_demeaned_mean` < 0.1 and `nrmse_pattern_only` >= 1  ->  LEVEL_ONLY: the model
carries no field information; do not attribute its score to any spatial mechanism,
and do not expect capacity/bandwidth/resolution knobs to help it.
`nrmse_raw > nrmse_constant_field_oracle` -> the model is beaten by a per-sample
scalar; the honest baseline for that dataset is a level regressor.

USAGE
-----
  python tools/dc_pattern_split.py \
      --preds cap32=/path/a/preds_test.npz cap12=/path/b/preds_test.npz \
      [--dataset sharp__allen_cahn_2d --include-copylf] \
      [--n-samples 24] [--out split.json]

The npz files must hold 2-D `(N, n_cells)` `pred` / `target` arrays (the
`preds_test.npz` layout). Arms are compared PAIRED on the first min(N) samples and
the tool refuses to proceed if their targets differ.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np


def _round_root() -> Path:
    here = Path(__file__).resolve().parent
    if (here.parent / "eval" / "nrmse.py").exists():
        return here.parent
    top = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=here,
                         capture_output=True, text=True, check=True).stdout.strip()
    return Path(top) / "mffp_autoresearch" / "round1"


ROUND = _round_root()
sys.path.insert(0, str(ROUND / "eval"))
import nrmse as nrmse_mod  # noqa: E402


def split_arm(pred: np.ndarray, target: np.ndarray) -> dict:
    p = np.asarray(pred, dtype=np.float64)
    y = np.asarray(target, dtype=np.float64)
    pm, ym = p.mean(1, keepdims=True), y.mean(1, keepdims=True)
    pd_, yd = p - pm, y - ym
    ynorm = np.linalg.norm(yd, axis=1)
    pat = np.linalg.norm(pd_ - yd, axis=1) / np.where(ynorm == 0, 1e-30, ynorm)
    num = np.einsum("ij,ij->i", pd_, yd)
    den = np.sqrt(np.einsum("ij,ij->i", pd_, pd_) * np.einsum("ij,ij->i", yd, yd))
    corr = num / np.where(den == 0, 1e-30, den)
    rec = {
        "nrmse_raw": float(nrmse_mod.nrmse(p, y)),
        "nrmse_pattern_only": float(pat.mean()),
        "nrmse_pattern_only_median": float(np.median(pat)),
        "corr_demeaned_mean": float(corr.mean()),
        "corr_demeaned_median": float(np.median(corr)),
        "relerr_of_spatial_mean": float(np.mean(np.abs(pm - ym) / (np.abs(ym) + 1e-30))),
        "frac_samples_pattern_useless": float((pat >= 1.0).mean()),
    }
    if rec["corr_demeaned_mean"] < 0.1 and rec["nrmse_pattern_only_median"] >= 1.0:
        rec["verdict"] = "LEVEL_ONLY"
    elif rec["corr_demeaned_mean"] < 0.5:
        rec["verdict"] = "WEAK_PATTERN"
    else:
        rec["verdict"] = "REAL_PATTERN"
    return rec


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--preds", nargs="+", required=True,
                    help="one or more LABEL=/path/to/preds_test.npz")
    ap.add_argument("--dataset", default=None,
                    help="panel dataset name (only needed for --include-copylf)")
    ap.add_argument("--include-copylf", action="store_true",
                    help="add eval/panel_data.py's copy-LF predictor as a reference arm")
    ap.add_argument("--n-samples", type=int, default=0,
                    help="use only the first N test samples (0 = all)")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    arms, target = {}, None
    for spec in args.preds:
        if "=" not in spec:
            ap.error(f"--preds entries must be LABEL=path, got {spec!r}")
        label, path = spec.split("=", 1)
        z = np.load(path)
        arms[label] = (z["pred"].astype(np.float64), z["target"].astype(np.float64))
    n = min(p.shape[0] for p, _ in arms.values())
    if args.n_samples:
        n = min(n, args.n_samples)
    target = next(iter(arms.values()))[1][:n]
    for label, (p, t) in arms.items():
        if not np.allclose(t[:n], target, rtol=1e-4, atol=1e-8):
            ap.error(f"target mismatch for arm {label!r}: arms are not the same split")
        arms[label] = p[:n]

    if args.include_copylf:
        if not args.dataset:
            ap.error("--include-copylf requires --dataset")
        import panel_data
        lf = panel_data.copylf_prediction(panel_data.load_split(args.dataset, "test"))
        lf = np.asarray(lf, dtype=np.float64)[:n]
        if lf.shape[1] != target.shape[1]:
            print(f"[warn] copy-LF n_cells {lf.shape[1]} != target {target.shape[1]}; skipped",
                  file=sys.stderr)
        else:
            arms["copylf"] = lf

    ym = target.mean(1, keepdims=True)
    res = {
        "dataset": args.dataset, "n_samples": int(n),
        "nrmse_def_hash": nrmse_mod.NRMSE_DEF_HASH,
        "nrmse_constant_field_oracle": float(
            nrmse_mod.nrmse(np.repeat(ym, target.shape[1], 1), target)),
        "hf_dc_energy_share": float((ym ** 2 * target.shape[1]).sum() / (target ** 2).sum()),
        "nrmse_zero_predictor": 1.0,
        "arms": {k: split_arm(v, target) for k, v in arms.items()},
    }
    print(f"# {res['dataset'] or ''} n={n}  constant-field-oracle="
          f"{res['nrmse_constant_field_oracle']:.5f}  "
          f"HF DC energy share={res['hf_dc_energy_share']:.4f}")
    print(f"{'arm':18s}{'nrmse':>10s}{'pattern-only':>14s}{'corr_dm':>9s}"
          f"{'mean relerr':>13s}  verdict")
    for k, a in res["arms"].items():
        print(f"{k:18s}{a['nrmse_raw']:10.5f}{a['nrmse_pattern_only_median']:14.4f}"
              f"{a['corr_demeaned_mean']:9.4f}{a['relerr_of_spatial_mean']:13.5f}"
              f"  {a['verdict']}"
              + ("  [worse than the level oracle]"
                 if a["nrmse_raw"] > res["nrmse_constant_field_oracle"] else ""))
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(res, indent=1))
        print(f"[wrote] {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
