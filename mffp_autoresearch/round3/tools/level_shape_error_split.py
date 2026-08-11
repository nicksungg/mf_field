#!/usr/bin/env python
"""level_shape_error_split.py — split a prediction's nRMSE into level + shape, exactly.

WHAT IT MEASURES
    The project's standing rule is that rel-L2 on a near-uniform field measures
    the constant offset, so every rel-L2 number must be paired with a
    mean-removed one. The usual mean-removed readout divides by ||y_tilde||,
    which changes the DENOMINATOR as well as the numerator and can flip a
    verdict for reasons that are pure normalisation.

    This tool instead performs the ENERGY-ORTHOGONAL split. For each test row,

        ||e_i||^2 = ||e_bar_i||^2 + ||e_tilde_i||^2      (exact, Pythagorean)

    where e_bar_i is the spatial-mean offset of the error and e_tilde_i is the
    mean-removed remainder. Dividing both pieces by ||y_i|| keeps them in the
    round's own nRMSE units and gives, per sample,

        nrmse_i^2 = level_i^2 + shape_i^2.

    Reported per prediction file:
      nrmse_total     the round's nRMSE (computed with round2/eval/nrmse.py)
      nrmse_level     the part of the error carried by the constant offset
      nrmse_shape     the mean-removed part, SAME denominator (comparable)
      nrmse_shape_conventional_mr   the ||y_tilde||-normalised variant, for
                                    comparison with legacy readouts
      level_share_of_error_energy   mean_i ||e_bar_i||^2 / ||e_i||^2
      hf_level_energy_fraction      how level-dominated the TARGET is

    Ground truth is loaded read-only through round2/eval/panel_data.py, and rows
    are matched to the prediction file's own condition block, so trimmed test
    splits (e.g. the ADR r3-0003 allen_cahn trim) align correctly.

PROVENANCE
    r3s3_lf_value-B3 mechanism turn 2. There it rejected the level-domination
    explanation of that card's falsification (fisher_kpp: 99.77 % of HF energy
    is the spatial mean, yet the mean-removed ladder knees at the same rung as
    the total) and showed that a flagged seed-level knee flip on allen_cahn was
    a denominator convention, not a physical effect
    (orthogonal [395,395,395] vs conventional [20,395,20]).

CAVEATS
    * Fields are treated as flat vectors with uniform cell weight; on a
      non-uniform mesh the "spatial mean" is the unweighted mean.
    * The split is of the ERROR, not of the field: a model can have a small
      level error on a level-dominated field and still be useless.

INVOCATION
    python tools/level_shape_error_split.py --dataset sharp__fisher_kpp_2d \
        --pred A0=/path/A0/..._preds.npz --pred A1=/path/A1/..._preds.npz \
        --out /tmp/fk_split.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np


def _panel_dir() -> Path:
    here = Path(__file__).resolve()
    for p in here.parents:
        cand = p / "mffp_autoresearch" / "round2" / "eval"
        if cand.is_dir():
            return cand
    raise SystemExit("could not locate mffp_autoresearch/round2/eval from this file")


sys.path.insert(0, str(_panel_dir()))
import panel_data  # noqa: E402
from nrmse import nrmse  # noqa: E402


def hf_rows(dataset: str, split: str, cond_test: np.ndarray | None):
    data = panel_data.load_split(dataset, split)
    fid = data["hf_fid"]
    fld = np.asarray(data["field_by_fid"][fid], dtype=np.float64)
    fld = fld.reshape(fld.shape[0], -1)
    if cond_test is None:
        return fld
    cond = np.asarray(data["cond_by_fid"][fid], dtype=np.float64)
    idx = []
    for row in cond_test:
        d = np.abs(cond - row[None, :]).max(axis=1)
        j = int(np.argmin(d))
        if d[j] > 1e-9:
            raise SystemExit(f"condition row not found in {dataset}/{split} (residual {d[j]:.3g})")
        idx.append(j)
    if len(set(idx)) != len(idx):
        raise SystemExit("condition rows matched non-uniquely; refusing to guess")
    return fld[np.array(idx)]


def split_error(pred: np.ndarray, hf: np.ndarray) -> dict:
    e = pred - hf
    n = e.shape[1]
    lvl = np.abs(e.mean(axis=1)) * np.sqrt(n)
    tot = np.linalg.norm(e, axis=1)
    shp = np.sqrt(np.maximum(tot ** 2 - lvl ** 2, 0.0))
    den = np.linalg.norm(hf, axis=1)
    hf_mr = hf - hf.mean(axis=1, keepdims=True)
    den_mr = np.linalg.norm(hf_mr, axis=1)
    hf_lvl = np.abs(hf.mean(axis=1)) * np.sqrt(n)
    return {
        "n_rows": int(e.shape[0]),
        "nrmse_total": float(np.mean(tot / den)),
        "nrmse_level": float(np.mean(lvl / den)),
        "nrmse_shape": float(np.mean(shp / den)),
        "nrmse_shape_conventional_mr": float(np.mean(shp / den_mr)),
        "level_share_of_error_energy": float(np.mean(lvl ** 2 / np.maximum(tot ** 2, 1e-300))),
        "hf_level_energy_fraction": float(np.mean(hf_lvl ** 2 / np.maximum(
            np.linalg.norm(hf, axis=1) ** 2, 1e-300))),
        "pythagorean_max_abs_residual": float(np.max(np.abs(tot ** 2 - lvl ** 2 - shp ** 2))),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--split", default="test")
    ap.add_argument("--pred", action="append", required=True, metavar="LABEL=PATH",
                    help="repeatable; npz holding the predictions")
    ap.add_argument("--pred-key", default="pred_test")
    ap.add_argument("--cond-key", default="cond_test_raw",
                    help="condition block used to align rows; '' to assume identity order")
    ap.add_argument("--out", type=Path, default=None)
    a = ap.parse_args()

    res = {"dataset": a.dataset, "split": a.split, "arms": {}}
    for spec in a.pred:
        if "=" not in spec:
            raise SystemExit(f"--pred needs LABEL=PATH, got {spec}")
        label, path = spec.split("=", 1)
        z = np.load(path, allow_pickle=True)
        pred = np.asarray(z[a.pred_key], dtype=np.float64)
        cond = np.asarray(z[a.cond_key], dtype=np.float64) if a.cond_key else None
        hf = hf_rows(a.dataset, a.split, cond)
        if hf.shape != pred.shape:
            raise SystemExit(f"{label}: pred {pred.shape} vs hf {hf.shape}")
        d = split_error(pred, hf)
        d["nrmse_via_round_metric"] = nrmse(pred, hf)
        d["path"] = path
        res["arms"][label] = d

    print(f"dataset {a.dataset} / split {a.split}")
    print(f"{'arm':16s} {'nRMSE':>10s} {'level':>10s} {'shape':>10s} {'shape(mr den)':>14s} "
          f"{'lvl share':>10s}")
    for label, d in res["arms"].items():
        print(f"{label:16s} {d['nrmse_total']:10.6f} {d['nrmse_level']:10.6f} "
              f"{d['nrmse_shape']:10.6f} {d['nrmse_shape_conventional_mr']:14.6f} "
              f"{d['level_share_of_error_energy']:10.4f}")
    any_arm = next(iter(res["arms"].values()))
    print(f"\nHF target level-energy fraction: {any_arm['hf_level_energy_fraction']:.6f}")
    print(f"max |Pythagorean residual| over all arms: "
          f"{max(d['pythagorean_max_abs_residual'] for d in res['arms'].values()):.3e}")

    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(json.dumps(res, indent=1, default=float))
        print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
