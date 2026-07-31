#!/usr/bin/env python
"""target_scale_spread_audit.py -- will a GLOBALLY normalised residual target work here?

Promoted from `worktrees/s2_beyond_copy/B2/scratchpad/reanalysis_turn_3.py` block D;
provenance card `experiment_cards/s2_beyond_copy/batch_2/B2.json` part 6, finding F10
(and F6/F8/F9, the two failures it explains).

WHY THIS EXISTS
---------------
Almost every MF family in this round trains an additive corrector

    y_hat = LF_up + scaler * Delta_theta(...) ,   target = (HF - LF_up) / scaler

with ONE global `scaler = max|HF - LF_up|` over the train split, under a plain MSE
loss. That is safe only if every training sample's residual has roughly the same
magnitude. When the per-sample residual scale spans decades the objective degenerates in
two opposite ways, both observed in s2_beyond_copy-B2:

* **outlier-dominated** (`ext__helmholtz_2d`: ONE of 400 train samples carries 89.2 % of
  the MSE target energy) -> the network fits that sample's scale and emits it on every
  query. Result: a ~9.5x-too-large, uncorrelated correction, skill 4.14, worse than
  copy-LF on 96/100 test samples, and worse on its OWN train split (8.36) than on test.
* **numerically-zero targets** (`sharp__phase_field_crystal_2d`: `scaler` is 79460x the
  median per-sample `max|r|`) -> for the majority of samples the normalised target is
  ~1e-5, i.e. no gradient teaches the network to output exactly zero, and a zero-init
  head still emits ~1e-4 relative junk after 200 epochs, damaging 50/100 test samples
  that copy-LF already had exact.

The three B2 datasets whose spread is only 2-4x are exactly the three where the same
substrate behaved sanely. This tool is the pre-flight check: it needs no model, no
training and no GPU, and it should be run BEFORE a card commits to a globally-normalised
additive target.

WHAT IT REPORTS (per dataset, from the TRAIN split only)
--------------------------------------------------------
| key | meaning |
|---|---|
| `resid_norm_max_over_median` / `_p99_over_median` | spread of per-sample `\|\|HF - LF_up\|\|` |
| `scaler_global_max` / `scaler_over_median_per_sample_max` | the shared scaler vs a typical sample's own scale |
| `energy_share_top1` / `_top5pct` | share of the MSE target energy owned by the worst 1 / worst 5 % of samples |
| `effective_n_samples_of_mse` | participation ratio `(sum e_i)^2 / sum e_i^2` -- how many samples the loss actually sees |
| `median_normalised_target_max` | `median_i(max\|r_i\|) / scaler` -- how close a typical target is to numerical zero |
| `verdict` | `OUTLIER_DOMINATED` / `NEAR_ZERO_TARGETS` / `BOTH` / `OK` |

HOW TO READ IT
--------------
* `OUTLIER_DOMINATED` -> use a per-sample normalisation, a relative/robust loss, or
  per-sample loss weights before blaming the architecture. Cross-check with
  `tools/relative_loss_geometry.py` (s7_loss-B1) before switching objectives.
* `NEAR_ZERO_TARGETS` -> the family will not be able to no-op; pair it with a trust gate
  (`tools/trust_gate_headroom.py`) or expect it to damage the already-solved samples.
  A `resid_norm_max_over_median` of 1e4+ usually also means the ladder is partly
  DEGENERATE -- confirm with `tools/registration_audit.py`.
* `OK` (spread <~ 10x, `effective_n_samples_of_mse` a decent fraction of N) -> a global
  scaler is fine and any failure is elsewhere.

INVOKE
------
  source "$PROJECT_ROOT/.venv/bin/activate"
  python tools/target_scale_spread_audit.py --datasets PANEL --out spread.json
  python tools/target_scale_spread_audit.py --datasets ext__helmholtz_2d \
      --out spread.json [--split train] [--n_max 400] [--outlier_share 0.5] [--spread 100]

Pure numpy on the login node, ~2-10 s per dataset. `--datasets` accepts `PANEL` /
`GUARD` (from `project.yaml`) or a comma list. Datasets whose split ships no LF are
skipped with an `error` field. Nothing it prints is a score.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
R1 = HERE.parent
sys.path.insert(0, str(R1 / "eval"))
from panel_data import load_config, load_split, copylf_prediction  # noqa: E402


def _resolve(names: str):
    if names in ("PANEL", "GUARD"):
        cfg = load_config()
        return list(cfg["panel"] if names == "PANEL" else cfg["guard_set"])
    return [d for d in names.split(",") if d]


def one(ds, split, n_max, outlier_share, spread_thresh, near_zero_thresh):
    d = load_split(ds, split)
    if not d["lf_fids"]:
        return {"error": f"{split} split ships no LF fidelity (LF_up undefined)"}
    hf_fid = d["hf_fid"]
    y = np.asarray(d["field_by_fid"][hf_fid], dtype=np.float64)[:n_max]
    lf = copylf_prediction(d)[:len(y)]
    if lf.shape != y.shape:
        return {"error": f"LF_up shape {lf.shape} != HF {y.shape}"}
    r = y - lf
    n = len(r)
    nrm = np.linalg.norm(r, axis=1)
    per_max = np.abs(r).max(axis=1)
    energy = nrm ** 2
    scaler = float(max(np.abs(r).max(), 1e-8))
    k5 = max(1, int(round(0.05 * n)))
    top = np.sort(energy)[::-1]

    e = {
        "split": split, "n_samples": int(n),
        "resid_norm_median": float(np.median(nrm)),
        "resid_norm_max_over_median": float(nrm.max() / max(np.median(nrm), 1e-300)),
        "resid_norm_p99_over_median": float(
            np.percentile(nrm, 99) / max(np.median(nrm), 1e-300)),
        "scaler_global_max": scaler,
        "scaler_over_median_per_sample_max": float(scaler / max(np.median(per_max), 1e-300)),
        "median_normalised_target_max": float(np.median(per_max) / scaler),
        "energy_share_top1": float(top[0] / max(energy.sum(), 1e-300)),
        "energy_share_top5pct": float(top[:k5].sum() / max(energy.sum(), 1e-300)),
        "effective_n_samples_of_mse": float(energy.sum() ** 2 / max((energy ** 2).sum(), 1e-300)),
    }
    e["effective_n_fraction"] = e["effective_n_samples_of_mse"] / n
    outlier = e["energy_share_top1"] > outlier_share or e["effective_n_fraction"] < 0.05
    nearzero = e["median_normalised_target_max"] < near_zero_thresh
    wide = e["resid_norm_max_over_median"] > spread_thresh
    e["verdict"] = ("BOTH" if outlier and nearzero else
                    "OUTLIER_DOMINATED" if outlier else
                    "NEAR_ZERO_TARGETS" if nearzero else
                    "WIDE_SPREAD" if wide else "OK")
    return e


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--datasets", required=True, help="PANEL | GUARD | comma list")
    ap.add_argument("--out", required=True)
    ap.add_argument("--split", default="train")
    ap.add_argument("--n_max", type=int, default=10 ** 9)
    ap.add_argument("--outlier_share", type=float, default=0.5,
                    help="energy share of the single worst sample that flags OUTLIER_DOMINATED")
    ap.add_argument("--spread", type=float, default=100.0,
                    help="resid_norm max/median that flags WIDE_SPREAD")
    ap.add_argument("--near_zero", type=float, default=1e-3,
                    help="median normalised target below which targets are numerically zero")
    a = ap.parse_args()

    out = {"_args": vars(a)}
    for ds in _resolve(a.datasets):
        try:
            e = one(ds, a.split, a.n_max, a.outlier_share, a.spread, a.near_zero)
        except Exception as exc:                                   # noqa: BLE001
            e = {"error": f"{type(exc).__name__}: {exc}"}
        out[ds] = e
        if "error" in e:
            print(f"[{ds}] {e['error']}")
            continue
        print(f"[{ds}] {e['verdict']}: norm max/median {e['resid_norm_max_over_median']:.4g}, "
              f"scaler/median-per-sample-max {e['scaler_over_median_per_sample_max']:.4g}, "
              f"top-1 energy share {e['energy_share_top1']:.3f}, "
              f"effective N {e['effective_n_samples_of_mse']:.1f}/{e['n_samples']}",
              flush=True)
    pathlib.Path(a.out).write_text(json.dumps(out, indent=1))
    print("wrote", a.out)


if __name__ == "__main__":
    main()
