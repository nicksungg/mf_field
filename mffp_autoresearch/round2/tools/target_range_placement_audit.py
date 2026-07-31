#!/usr/bin/env python
"""target_range_placement_audit.py -- is the OUTPUT-TARGET SCALER a lever on this dataset?

Promoted from `worktrees/s5_tuning/B2/scratchpad/reanalysis_turn_1.py` (block A) +
`reanalysis_turn_2.py` (block A) + `reanalysis_turn_3.py` (block A2); provenance card
`experiment_cards/s5_tuning/batch_2/B2.json` part 6, findings F1, F2, F5, F6, F7, F12.

WHY THIS EXISTS
---------------
s5_tuning-B2 switched one knob -- the per-stage output-target scaler, `max|Y_train|`
(`maxabs`) vs `mean/std` (`zscore`) -- on the champion substrate and pre-registered
`|mu|/sd` as the covariate that would say WHERE it mattered. It got the ordering exactly
backwards: the panel's largest `|mu|/sd` (3.749) was the panel's smallest movement, and
the smallest (0.0415) was the largest.

The reason is structural, and this tool encodes it.

* Under `maxabs` the supervised target `Y/max|Y|` has PEDESTAL `mu/max` and FLUCTUATION
  RMS `sd/max`; under `zscore` those become 0 and 1.
* The pedestal is absorbed for free by the output layer's bias -- removing it changes
  nothing. So `|mu|/sd` predicts NOTHING.
* The fluctuation magnification `G = max|Y| / sd(Y) = (max/rms) x (rms/sd)` is what
  optimization cannot absorb: with a large `G` the entire learnable population is
  supervised in the bottom few percent of the network's output range, and whatever
  residual output error remains is re-amplified by `max|Y|` at denormalization.
  On `ext__helmholtz_2d` (`G` = 39.5) the champion emitted 2.04x too much energy with an
  optimal per-sample rescale of -0.02; switching to `zscore` cut nRMSE 3.4x, 92 % of it
  pure amplitude calibration.
* And a global scalar CANNOT de-concentrate an outlier-dominated loss -- it divides every
  sample's energy by the same constant. Measured: effective N 1.0145/400 (`maxabs`) vs
  1.0179/400 (`zscore`). This tool prints both so nobody re-derives the wrong story;
  fixing outlier domination is an OBJECTIVE-side change
  (`tools/target_scale_spread_audit.py`, `tools/relative_loss_geometry.py`).

WHAT IT REPORTS (per dataset, per stage, TRAIN split only -- no model, no GPU)
-----------------------------------------------------------------------------
| key | meaning |
|---|---|
| `G_max_over_sd` | the fluctuation magnification a `zscore` (or any unit-variance) scaler buys |
| `G_tail_max_over_rms` / `G_pedestal_rms_over_sd` | `G`'s two factors; a `G` that is mostly PEDESTAL will do nothing |
| `maxabs_pedestal` / `maxabs_fluct_rms` | where the target actually sits in output range under `maxabs` |
| `eff_n_maxabs` / `eff_n_zscore` / `eff_n_fraction` | participation ratio of the per-sample MSE energy under each normalization (they will be nearly equal -- that is the point) |
| `top1_energy_share_*` | share of the MSE owned by the single worst train sample |
| `per_sample_rms_max_over_median` | how extreme the sample that sets `max|Y|` is |
| `stage_fluct_mismatch` / `stage_pedestal_gap` | LF vs HF placement seam a two-stage (pretrain/finetune) family inherits |
| `verdict` | `SCALER_IS_A_LEVER` / `PEDESTAL_ONLY` / `SCALER_INERT` (+ `STAGE_SEAM` suffix) |

HOW TO READ IT
--------------
* `SCALER_IS_A_LEVER` (`G` >= `--g_lever`, default 8) -> a unit-variance target scaler is
  worth an arm on this dataset. **Gate it**: run `tools/dc_pattern_split.py` first; if the
  dataset is LEVEL_ONLY the model has no pattern channel to magnify and the scaler will be
  inert anyway (measured: `sharp__fisher_kpp_2d`, `G` = 6.0, moved +0.04 skill / 10x inside
  its floor). Observed break on the round's panel: `G` 6.0 = nothing, `G` 9.9 = effect.
* `PEDESTAL_ONLY` -> `G` comes mostly from a DC offset (`rms/sd` term). The output bias
  handles it; expect a null. This is the exact trap s5-B2 fell into.
* `SCALER_INERT` -> `G` < `--g_lever` and mostly tail-free: stop tuning normalization here
  and look for a mechanism that produces PATTERN.
* `STAGE_SEAM` -> LF and HF stages are placed very differently under `maxabs`; a
  pretrain-on-LF/finetune-on-HF family transfers weights across a scale jump. (No panel
  dataset triggered it: the worst observed mismatch is 1.357.)
* If `eff_n_fraction` is tiny (helmholtz: 0.0025) the loss is one sample. A scaler will NOT
  fix that -- see the `objective_side_note` this tool emits.

INVOKE
------
  source "$PROJECT_ROOT/.venv/bin/activate"
  python tools/target_range_placement_audit.py --datasets PANEL --out placement.json
  python tools/target_range_placement_audit.py --datasets ext__helmholtz_2d,ifc_poisson \
      --out placement.json [--split train] [--n_max 400] [--g_lever 8.0] \
      [--pedestal_ratio 2.0] [--stage_seam 3.0]

`--datasets` accepts `PANEL` / `GUARD` (from `project.yaml`) or a comma list. Pure numpy
on the login node, ~2-10 s per dataset. Nothing it prints is a score.
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
from panel_data import load_config, load_split  # noqa: E402


def _resolve(names: str):
    if names in ("PANEL", "GUARD"):
        cfg = load_config()
        return list(cfg["panel"] if names == "PANEL" else cfg["guard_set"])
    return [d for d in names.split(",") if d]


def _eff_n(energy):
    e = np.asarray(energy, dtype=np.float64)
    return float(e.sum() ** 2 / max((e ** 2).sum(), 1e-300))


def _stage(Y):
    """Placement statistics for one stage's train target block (N, n_cells)."""
    Y = np.asarray(Y, dtype=np.float64).reshape(len(Y), -1)
    n = len(Y)
    mx = float(max(np.abs(Y).max(), 1e-300))
    mu, sd = float(Y.mean()), float(max(Y.std(), 1e-300))
    rms = float(np.sqrt((Y ** 2).mean()))
    e_max = (Y ** 2).sum(axis=1)                 # per-sample MSE energy, maxabs arm
    e_zs = ((Y - mu) ** 2).sum(axis=1)           # ... and zscore arm
    per_rms = np.sqrt((Y ** 2).mean(axis=1))
    out = {
        "n_train": int(n), "n_cells": int(Y.shape[1]),
        "max_abs": mx, "mean": mu, "std": sd, "rms": rms,
        "abs_mu_over_sd_DO_NOT_USE": abs(mu) / sd,
        "G_max_over_sd": mx / sd,
        "G_tail_max_over_rms": mx / max(rms, 1e-300),
        "G_pedestal_rms_over_sd": rms / sd,
        "maxabs_pedestal": mu / mx,
        "maxabs_fluct_rms": sd / mx,
        "typical_norm_target_rms_maxabs": rms / mx,
        "per_sample_rms_max_over_median": float(per_rms.max() / max(np.median(per_rms), 1e-300)),
        "eff_n_maxabs": _eff_n(e_max), "eff_n_zscore": _eff_n(e_zs),
        "top1_energy_share_maxabs": float(e_max.max() / max(e_max.sum(), 1e-300)),
        "top1_energy_share_zscore": float(e_zs.max() / max(e_zs.sum(), 1e-300)),
    }
    out["eff_n_fraction"] = out["eff_n_maxabs"] / n
    out["eff_n_change_from_zscore"] = out["eff_n_zscore"] - out["eff_n_maxabs"]
    return out


def one(ds, split, n_max, g_lever, pedestal_ratio, stage_seam):
    d = load_split(ds, split)
    hf_fid = d["hf_fid"]
    res = {"split": split,
           "hf_stage": _stage(np.asarray(d["field_by_fid"][hf_fid])[:n_max])}
    if d["lf_fids"]:
        lf_fid = max(d["lf_fids"])
        res["lf_stage"] = _stage(np.asarray(d["field_by_fid"][lf_fid])[:n_max])
        res["stage_fluct_mismatch"] = (res["lf_stage"]["maxabs_fluct_rms"]
                                       / max(res["hf_stage"]["maxabs_fluct_rms"], 1e-300))
        res["stage_pedestal_gap"] = abs(res["lf_stage"]["maxabs_pedestal"]
                                        - res["hf_stage"]["maxabs_pedestal"])
    else:
        res["lf_stage"] = None
        res["stage_fluct_mismatch"] = None
        res["stage_pedestal_gap"] = None

    hf = res["hf_stage"]
    lever = hf["G_max_over_sd"] >= g_lever
    pedestal_driven = hf["G_pedestal_rms_over_sd"] >= pedestal_ratio
    v = ("PEDESTAL_ONLY" if pedestal_driven and not lever else
         "SCALER_IS_A_LEVER" if lever else "SCALER_INERT")
    if res["stage_fluct_mismatch"] is not None and (
            res["stage_fluct_mismatch"] > stage_seam
            or res["stage_fluct_mismatch"] < 1.0 / stage_seam):
        v += "+STAGE_SEAM"
    res["verdict"] = v
    res["gate_note"] = ("G only cashes in where the pattern channel is alive -- run "
                        "tools/dc_pattern_split.py; LEVEL_ONLY datasets are inert "
                        "under ANY affine target scaler (the output bias reproduces "
                        "the DC term for free).")
    if hf["eff_n_fraction"] < 0.05:
        res["objective_side_note"] = (
            f"effective N is {hf['eff_n_maxabs']:.3f}/{hf['n_train']} "
            f"({hf['eff_n_fraction']:.4f} of N): the loss is ~one sample. A GLOBAL "
            "scaler cannot change this (see eff_n_change_from_zscore) -- fix it in the "
            "objective (per-sample normalization / robust loss / sample weights); see "
            "tools/target_scale_spread_audit.py and tools/relative_loss_geometry.py.")
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--datasets", required=True, help="PANEL | GUARD | comma list")
    ap.add_argument("--out", required=True)
    ap.add_argument("--split", default="train")
    ap.add_argument("--n_max", type=int, default=10 ** 9)
    ap.add_argument("--g_lever", type=float, default=8.0,
                    help="G = max|Y|/sd at or above which a unit-variance scaler is a lever "
                         "(round-1 panel break: 6.0 = nothing, 9.9 = effect)")
    ap.add_argument("--pedestal_ratio", type=float, default=2.0,
                    help="rms/sd at or above which G is judged pedestal-driven")
    ap.add_argument("--stage_seam", type=float, default=3.0,
                    help="LF/HF maxabs fluctuation mismatch that flags a transfer seam")
    a = ap.parse_args()

    out = {"tool": "target_range_placement_audit.py", "split": a.split,
           "thresholds": {"g_lever": a.g_lever, "pedestal_ratio": a.pedestal_ratio,
                          "stage_seam": a.stage_seam},
           "datasets": {}}
    for ds in _resolve(a.datasets):
        try:
            out["datasets"][ds] = one(ds, a.split, a.n_max, a.g_lever,
                                      a.pedestal_ratio, a.stage_seam)
        except Exception as exc:                     # noqa: BLE001 - report, never crash the sweep
            out["datasets"][ds] = {"error": f"{type(exc).__name__}: {exc}"}
    pathlib.Path(a.out).write_text(json.dumps(out, indent=1))
    for ds, r in out["datasets"].items():
        if "error" in r:
            print(f"{ds:34s} ERROR {r['error']}")
            continue
        hf = r["hf_stage"]
        print(f"{ds:34s} G={hf['G_max_over_sd']:9.3f} "
              f"(tail {hf['G_tail_max_over_rms']:8.3f} x pedestal {hf['G_pedestal_rms_over_sd']:6.3f})  "
              f"effN {hf['eff_n_maxabs']:8.2f}/{hf['n_train']}  {r['verdict']}")
    print("WROTE", a.out)


if __name__ == "__main__":
    main()
