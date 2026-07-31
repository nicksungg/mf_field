#!/usr/bin/env python
"""How much can ANY per-sample multiplicative calibration head buy on this
prediction -- and how much of that is reachable from the condition vector?

Provenance: promoted from `s1_poisson-B3` mechanism turn 2
(`worktrees/s1_poisson/B3/scratchpad/reanalysis_turn_2.py`, probes Q1/Q3/Q4).

WHY THIS EXISTS
---------------
s1-B2 measured that 57 % of its winner's squared error was a per-sample scalar
gain and spent a whole batch (B3) building a closed-form head to recover it.
The head worked (0.034264 -> 0.024970 on `ifc_poisson`), but turn 2 showed the
honest headroom *left* after it -- intercept and dispersion BOTH re-fitted on
the test targets -- was 0.045x the noise floor, i.e. nothing. This tool front-
loads that arithmetic: before designing a calibration head, it reports the three
ceilings a head can aim at and how they are split.

  1. one global gain (a single scalar for the whole split)   -- usually ~0
  2. an X-linear per-sample law (ridge, LOO-selected lambda) -- what a head can hope for
  3. the per-sample gain oracle (one scalar per sample)      -- the hard ceiling

Ceilings 1-3 are all fitted ON THE TEST TARGETS and are therefore UPPER BOUNDS,
never claims. The tool labels every one of them.

WHAT IT REPORTS
---------------
  nrmse_raw                        the round's metric (eval/nrmse.py)
  amplitude_share_of_sq_error      fraction of squared error removable by a per-sample scalar
  nrmse_one_global_gain            ceiling 1  [TEST-FITTED]
  nrmse_x_linear_law               ceiling 2  [TEST-FITTED], with R^2 and lambda
  nrmse_per_sample_oracle          ceiling 3  [TEST-FITTED]
  log_g_std / dispersion           per-sample log-gain dispersion of the arm
  coordinate_share                 share of the fitted law's variance per condition coordinate
  headroom_in_floors               each ceiling's distance from raw, in noise-floor units

READ IT AS
----------
`amplitude_share_of_sq_error` < ~0.2 -> a calibration head has almost nothing to
work with; look at the pattern channel instead (`dc_pattern_split.py`).
`nrmse_x_linear_law` close to `nrmse_per_sample_oracle` -> the gain is a smooth
function of the conditions, i.e. it is a GENERALIZATION error of the conditional
map, and a head can recover most of it (s1-B3: R^2 0.86-0.92).
`nrmse_x_linear_law` far from the oracle -> the gain is sample noise; a head
will only ever get the smooth part.
`headroom_in_floors` < 1 for every ceiling -> do not spend a batch on a head.

USAGE
-----
  python tools/gain_calibration_ceiling.py \
      --preds /path/to/preds_test.npz \
      [--dataset ifc_poisson] [--data-root ...] [--split test] \
      [--floor 0.008636672175093287] [--clip 0.5 2.0] [--out ceiling.json]

`--dataset` supplies the HF test conditions used for ceiling 2; without it only
ceilings 1 and 3 are reported. Read-only, numpy only, seconds.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np


def _round_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _factory_root() -> Path:
    env = os.environ.get("FACTORY_ROOT")
    if env:
        return Path(env)
    for p in Path(__file__).resolve().parents:
        cand = p / "mf_field/factory_mffp"
        if cand.is_dir():
            return cand
    raise SystemExit("cannot locate factory_mffp; set FACTORY_ROOT")


def _ridge_loo(A, t, lam_grid):
    """Ridge with closed-form LOO (PRESS) lambda selection; intercept unpenalised."""
    best = None
    n, k = A.shape
    for lam in lam_grid:
        P = np.eye(k) * lam
        P[0, 0] = 0.0                      # column 0 is the intercept
        G = A.T @ A + P
        try:
            Gi = np.linalg.inv(G)
        except np.linalg.LinAlgError:
            continue
        w = Gi @ (A.T @ t)
        H = np.einsum("ij,jk,ik->i", A, Gi, A)
        r = t - A @ w
        press = float(np.sum((r / np.maximum(1e-12, 1 - H)) ** 2))
        if best is None or press < best["press"]:
            best = {"lam": float(lam), "w": w, "press": press,
                    "loo_r2": float(1 - press / np.sum((t - t.mean()) ** 2))}
    return best


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--preds", required=True, help="preds_test.npz with pred/target")
    ap.add_argument("--dataset", default=None, help="dataset name, for test conditions")
    ap.add_argument("--data-root", default=None)
    ap.add_argument("--split", default="test")
    ap.add_argument("--floor", type=float, default=None,
                    help="noise floor in nRMSE units, to express headroom in floors")
    ap.add_argument("--clip", nargs=2, type=float, default=[0.5, 2.0])
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    sys.path.insert(0, str(_round_root() / "eval"))
    from nrmse import nrmse, NRMSE_DEF_HASH        # noqa: E402

    d = np.load(a.preds)
    y = d["target"].astype(np.float64)
    p = d["pred"].astype(np.float64)
    g = (p * y).sum(1) / (p * p).sum(1)
    log_g = np.log(g)
    sq_tot = ((p - y) ** 2).sum(1)
    sq_str = ((p * g[:, None] - y) ** 2).sum(1)

    # ceiling 1: one global gain (test-fitted)
    gg = float((p * y).sum() / (p * p).sum())
    R = {
        "preds": str(a.preds), "n_samples": int(y.shape[0]),
        "nrmse_def_hash": NRMSE_DEF_HASH,
        "nrmse_raw": nrmse(p, y),
        "amplitude_share_of_sq_error": float(1 - sq_str.sum() / sq_tot.sum()),
        "log_g_mean": float(log_g.mean()), "log_g_std": float(log_g.std()),
        "g_min": float(g.min()), "g_max": float(g.max()),
        "nrmse_one_global_gain": nrmse(p * gg, y),
        "one_global_gain": gg,
        "nrmse_per_sample_oracle": nrmse(p * g[:, None], y),
        "_label": "every ceiling below is fitted ON TEST TARGETS -> UPPER BOUND, never a claim",
    }

    if a.dataset:
        froot = _factory_root()
        sys.path.insert(0, str(froot))
        from data_adapters import load_mf_dataset       # noqa: E402
        ds = load_mf_dataset(Path(a.data_root or (froot / "data")) / a.dataset, a.split)
        hf = int(ds["hf_fid"])
        X = np.asarray(ds["cond_by_fid"][hf], np.float64)[:y.shape[0]]
        mu, sd = X.mean(0), np.maximum(X.std(0), 1e-12)
        Z = (X - mu) / sd
        A = np.concatenate([np.ones((Z.shape[0], 1)), Z], 1)
        fit = _ridge_loo(A, log_g, [1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1, 10])
        w = fit["w"]
        lg = A @ w
        gc = np.clip(np.exp(lg), a.clip[0], a.clip[1])
        R["x_linear_law"] = {
            "lambda": fit["lam"], "loo_r2": fit["loo_r2"],
            "r2_in_fit": float(1 - np.var(log_g - lg) / np.var(log_g)),
            "intercept": float(w[0]), "slope": w[1:].tolist(),
            "nrmse_x_linear_law": nrmse(p * gc[:, None], y),
            "coordinate_share": {f"coord{i}": float(np.var(Z[:, i] * w[i + 1])
                                                    / max(1e-30, np.var(Z @ w[1:])))
                                 for i in range(Z.shape[1])},
            "clip_fraction": float(np.mean((np.exp(lg) < a.clip[0]) | (np.exp(lg) > a.clip[1]))),
            "_label": "fitted on the TEST oracle gains -> UPPER BOUND for any head",
        }

    if a.floor:
        R["headroom_in_floors"] = {
            "one_global_gain": (R["nrmse_raw"] - R["nrmse_one_global_gain"]) / a.floor,
            "per_sample_oracle": (R["nrmse_raw"] - R["nrmse_per_sample_oracle"]) / a.floor,
        }
        if "x_linear_law" in R:
            R["headroom_in_floors"]["x_linear_law"] = (
                R["nrmse_raw"] - R["x_linear_law"]["nrmse_x_linear_law"]) / a.floor

    print(f"# {Path(a.preds).parent.name}  n={R['n_samples']}  "
          f"amplitude share of sq error = {R['amplitude_share_of_sq_error']:.3f}  "
          f"log-g std = {R['log_g_std']:.5f}")
    print(f"{'ceiling':<34}{'nRMSE':>10}{'floors':>9}")
    rows = [("raw (no calibration)", R["nrmse_raw"]),
            ("1 global gain      [TEST-FITTED]", R["nrmse_one_global_gain"])]
    if "x_linear_law" in R:
        rows.append(("X-linear law       [TEST-FITTED]", R["x_linear_law"]["nrmse_x_linear_law"]))
    rows.append(("per-sample oracle  [TEST-FITTED]", R["nrmse_per_sample_oracle"]))
    for name, v in rows:
        fl = f"{(R['nrmse_raw'] - v) / a.floor:>9.2f}" if a.floor else " " * 9
        print(f"{name:<34}{v:>10.6f}{fl}")
    if "x_linear_law" in R:
        print(f"  law R^2 (in-fit) {R['x_linear_law']['r2_in_fit']:.4f} / LOO "
              f"{R['x_linear_law']['loo_r2']:.4f}, lambda {R['x_linear_law']['lambda']:g}, "
              f"top coord "
              f"{max(R['x_linear_law']['coordinate_share'].items(), key=lambda kv: kv[1])}")

    if a.out:
        Path(a.out).write_text(json.dumps(R, indent=1))
        print(f"[wrote] {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
