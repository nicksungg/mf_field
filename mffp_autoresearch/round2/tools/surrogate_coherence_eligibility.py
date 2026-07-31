#!/usr/bin/env python
"""surrogate_coherence_eligibility.py -- IS THIS INTERMEDIATE FIELD WORTH
FEEDING TO A DOWNSTREAM CORRECTOR?  (training-free, decided before you train it)

Any design of the shape `stage-1 produces a surrogate field -> stage-2 corrects
it` rests on an unstated premise: that the surrogate's REALISATION is coherent
with the target, band by band.  This tool measures that premise directly from a
dumped surrogate and its paired target, and returns the ceiling on what ANY
spatially-invariant linear stage could add on top of that particular surrogate.

  gamma_band(k)       energy-weighted coherence of the surrogate with the target
                      inside each dyadic band (s2-B1 band grid, 4 bands)
  oracle_lsi_*        the IN-SAMPLE optimal Wiener transfer T(k) fitted on the
                      very rows being scored -- a strict UPPER BOUND on any LSI
                      / band-gain / spectral-calibration stage on this input
  verdict             CORRECTOR_ELIGIBLE / CORRECTOR_FUTILE / UNDETERMINED

WHY THIS EXISTS
---------------
`r2s2_stacked-B1` turn 3 measured the same FROZEN corrector on inputs
interpolating from the real LF field to an emulated pseudo-LF field.  Its value
is not a property of its weights or its training budget but of its input's
realisation: relative value-add 0.99997 -> -0.000157 (pfc), 0.8186 -> +8e-06
(allen_cahn), 0.3209 -> +0.00082 (cahn_hilliard) as the input goes real ->
pseudo, with the correction vector rotating from cos +0.98 to cos ~0 against the
residual it must remove.  A 10% pseudo admixture already costs 7-48x of the
value.  The discriminator that predicts all of it, and that costs nothing to
compute, is band>=1 coherence: value-add was 63-95% wherever gamma_band1 >= 0.95
and <= 0.08% wherever gamma_band1 <= 0.52.

The decision this supports: on `sharp__cahn_hilliard`, the ORACLE LSI ceiling on
the realised pseudo-LF was +14.07% relative error reduction = ~1.59 skill units,
BELOW that card's own 2.0-skill-unit falsification threshold.  The clause could
not have been beaten by any better-trained corrector of that class.  Running this
tool on the stage-1 output would have said so before stage 2 was built.

RELATION TO NEIGHBOURING TOOLS
------------------------------
* `spectral_prestage_bc_audit.py` (round 1) asks whether a spectral stage is
  APPLICABLE (boundary-condition / wrap-seam match).  This one asks whether the
  input is WORTH filtering at all.  Both are preconditions; this is the tighter.
* `band_gain_counterfactual.py` (r2s1-B1) asks whether an existing arm-vs-arm gap
  is band CALIBRATION, using held-out-fitted gains.  This tool's oracle Wiener is
  the in-sample ceiling of that same family of fixes -- run it first: if the
  ceiling is small, no calibration scheme can pay.
* `posthoc_repair_ladder.py` (r2s3-B1) rung L2 is the ideal-low-pass member of
  the same class with a train-fitted cutoff; this tool gives the unconstrained
  per-wavenumber optimum, i.e. the strictly larger bound.

WHAT IT REPORTS
---------------
  per_band[bandN].coherence_energy_weighted    gamma_band, in [0, 1]
  per_band[bandN].target_energy_share          how much the band is worth
  per_band[bandN].input_over_target_amp        amplitude ratio (blur signature)
  per_band[bandN].oracle_lsi_residual_frac     sqrt(1 - gamma^2) energy-weighted
  identity_nrmse                               nRMSE(surrogate, target)
  oracle_lsi_nrmse_insample                    after the ORACLE Wiener filter
  oracle_lsi_relative_gain                     1 - oracle/identity (negative =
                                               even the oracle filter is harmful
                                               on this input, r2s2-B1 pfc -13.75%)
  implied_skill_after_oracle_lsi               with --arm_nrmse/--reference_nrmse:
                                               the multiplicative transfer of the
                                               gain to a scored arm, in skill units
  verdict.label / .gamma_band1 / .rule

READ IT AS
----------
* `CORRECTOR_FUTILE` (gamma_band1 <= 0.52): do not build stage 2 on this
  surrogate.  Fix stage 1, or change the class (a corrector cannot restore a
  realisation its input does not carry).
* `CORRECTOR_ELIGIBLE` (gamma_band1 >= 0.95): the r2s2-B1 regime where the same
  frozen corrector removed 63-95% of the remaining error.
* `UNDETERMINED` in between: the threshold is only bracketed (0.52, 0.95) by the
  r2s2-B1 panel; treat `oracle_lsi_relative_gain` as the decision number and
  convert it to skill units before committing a batch.
* A high gamma with `input_over_target_amp` far from 1 is the GOOD case: right
  realisation, wrong gain -- exactly what an LSI stage fixes.
* Low gamma in band0 too (r2s2-B1 helmholtz: 0.139) means the surrogate is not
  tracking the target anywhere; nothing downstream is worth building.

LEGALITY
--------
The oracle Wiener filter is fitted IN SAMPLE on the rows handed in, so every
`oracle_*` number is a CEILING and must never be quoted as an arm score.  When
the target is loaded from the dataset the tool reads the TRAIN split only and
asserts the test split exposes no LF fidelity.  nRMSE goes through the round's
own `eval/nrmse.py`.

INVOCATION
----------
    source "$PROJECT_ROOT/.venv/bin/activate"
    # surrogate + target both dumped by the caller (same rows, same grid)
    python tools/surrogate_coherence_eligibility.py \
        --dataset sharp__phase_field_crystal_2d \
        --pred pseudo_lf_up.npy --target hf_train_rows.npy \
        --arm_nrmse 0.47149 --reference_nrmse 0.041803 --out coh.json

    # target taken from the dataset's TRAIN split at the given rows
    python tools/surrogate_coherence_eligibility.py --dataset sharp__cahn_hilliard \
        --pred pseudo_lf_up.npz:val --target_from_train --rows val_idx.npy \
        --out coh.json

`--pred/--target` accept `path.npy` or `path.npz:key`; shapes (N, H, W) or
(N, n_cells).  Both must be on the SAME grid (the corrector's working grid) and
in the same row order.

Provenance: card `experiment_cards/r2s2_stacked/batch_1/B1.json` part 6
(findings 6-8, interpretations I7/I10, falsification postmortem); source probe
`worktrees/r2s2_stacked/B1/scratchpad/reanalysis_turn_3.py` (P6).
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import yaml


def _resolve_roots():
    here = Path(__file__).resolve()
    project_root = Path(subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True,
        check=True, cwd=here.parent).stdout.strip())
    round_root = here.parents[1]
    cfg = yaml.safe_load(open(round_root / "project.yaml"))
    paths = {k: (Path(v) if os.path.isabs(v) else (project_root / v).resolve())
             for k, v in cfg["paths"].items()}
    return project_root, round_root, cfg, paths


PROJECT_ROOT, ROUND_ROOT, CFG, PATHS = _resolve_roots()
sys.path.insert(0, str(PATHS["eval_dir"]))
sys.path.insert(0, str(PATHS["factory_root"]))
from nrmse import NRMSE_DEF_HASH, nrmse                    # noqa: E402
from data_adapters.loaders import load_mf_dataset          # noqa: E402
from data_adapters.geometry import resolve_grid            # noqa: E402

N_BANDS = 4
GAMMA_ELIGIBLE = 0.95      # r2s2-B1: value-add 63-95% at or above this
GAMMA_FUTILE = 0.52        # r2s2-B1: value-add <= 0.08% at or below this


def band_masks(grid, n_bands: int = N_BANDS):
    """s2-B1 dyadic radial bands on the rFFT half-plane (verbatim convention)."""
    h, w_ = int(grid[0]), int(grid[1])
    kx = np.fft.fftfreq(h) * h
    ky = np.arange(w_ // 2 + 1, dtype=np.float64)
    kr = np.sqrt(kx[:, None] ** 2 + ky[None, :] ** 2)
    weight = np.full((h, w_ // 2 + 1), 2.0)
    weight[:, 0] = 1.0
    if w_ % 2 == 0:
        weight[:, -1] = 1.0
    k_ny = min(h, w_) / 2.0
    edges = [0.0] + [k_ny / 2.0 ** (n_bands - 1 - b) for b in range(n_bands)]
    masks = []
    for b in range(n_bands):
        if b == n_bands - 1:
            masks.append(kr >= edges[b])
        else:
            masks.append((kr >= edges[b]) & (kr < edges[b + 1]))
    return masks, weight, edges


def coherence_and_oracle(F, Y, grid, masks, weight):
    """Per-wavenumber coherence of input F with target Y + oracle LSI ceiling.

    All statistics are IN-SAMPLE on the rows handed in, so every oracle number is
    a strict UPPER BOUND on what a spatially-invariant linear filter could have
    achieved on that slice.
    """
    H, W = int(grid[0]), int(grid[1])
    fF = np.fft.rfft2(np.asarray(F, np.float64).reshape(-1, H, W))
    fY = np.fft.rfft2(np.asarray(Y, np.float64).reshape(-1, H, W))
    Sff = (np.abs(fF) ** 2).sum(0)
    Syy = (np.abs(fY) ** 2).sum(0)
    Sfy = (fY * np.conj(fF)).sum(0)
    g2 = np.where(Sff > 1e-30, (np.abs(Sfy) ** 2) / np.maximum(Sff * Syy, 1e-300), 0.0)
    g2 = np.clip(g2, 0.0, 1.0)
    T_or = np.where(Sff > 1e-20, Sfy / np.maximum(Sff, 1e-20), 0.0)
    per_band = {}
    for i, m in enumerate(masks):
        if not m.any():
            continue
        wy = (weight * Syy)[m].sum()
        wf = (weight * Sff)[m].sum()
        per_band[f"band{i}"] = {
            "target_energy_share": float(wy / max((weight * Syy).sum(), 1e-300)),
            "input_over_target_amp": float(np.sqrt(wf / max(wy, 1e-300))),
            "coherence_energy_weighted": float(
                np.sqrt(max((weight * Syy * g2)[m].sum() / max(wy, 1e-300), 0.0))),
            "oracle_lsi_residual_frac": float(
                np.sqrt(max((weight * Syy * (1.0 - g2))[m].sum() / max(wy, 1e-300), 0.0))),
            "mean_abs_T_oracle": float(np.abs(T_or)[m].mean()),
        }
    oracle_pred = np.fft.irfft2(fF * T_or[None, :, :], s=(H, W)).reshape(F.shape[0], -1)
    ident = nrmse(F, Y)
    orc = nrmse(oracle_pred, Y)
    return {
        "per_band": per_band,
        "identity_nrmse": ident,
        "oracle_lsi_nrmse_insample": orc,
        "oracle_lsi_relative_gain": float(1.0 - orc / max(ident, 1e-300)),
        "global_coherence_energy_weighted": float(
            np.sqrt(max((weight * Syy * g2).sum() / max((weight * Syy).sum(), 1e-300), 0.0))),
    }


def load_array(spec, n_cells=None):
    path, _, key = str(spec).partition(":")
    if path.endswith(".npz"):
        with np.load(path) as z:
            arr = z[key] if key else z[list(z.keys())[0]]
    else:
        arr = np.load(path)
    arr = np.asarray(arr, np.float64)
    arr = arr.reshape(arr.shape[0], -1)
    if n_cells is not None and arr.shape[1] != n_cells:
        raise ValueError(f"{spec}: {arr.shape[1]} cells, expected {n_cells}")
    return arr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True, help="for the grid (and the target)")
    ap.add_argument("--pred", required=True, help="surrogate fields, path[:key]")
    ap.add_argument("--out", required=True)
    ap.add_argument("--data_root", default=str(PATHS["stripped_data_root"]))
    ap.add_argument("--target", default=None, help="target fields, path[:key]")
    ap.add_argument("--target_from_train", action="store_true",
                    help="take the target from the dataset's TRAIN split instead")
    ap.add_argument("--target_fid", default="hf",
                    help="'hf' or an explicit fidelity id (with --target_from_train)")
    ap.add_argument("--rows", default=None,
                    help=".npy row indices into the train split (with --target_from_train)")
    ap.add_argument("--arm_nrmse", type=float, default=None,
                    help="a scored arm's nRMSE, to transfer the oracle gain")
    ap.add_argument("--reference_nrmse", type=float, default=None,
                    help="the copy-LF / paper-bar denominator, for skill units")
    ap.add_argument("--label", default=None, help="free-text tag for the record")
    args = ap.parse_args()

    ds_dir = Path(args.data_root) / args.dataset
    train = load_mf_dataset(ds_dir, "train")
    test = load_mf_dataset(ds_dir, "test")
    if test["lf_fids"]:
        raise AssertionError(f"{args.dataset}: test exposes LF {test['lf_fids']}")

    if args.target_from_train:
        fid = test["hf_fid"] if args.target_fid == "hf" else int(args.target_fid)
        Y = np.asarray(train["field_by_fid"][fid], np.float64)
        if args.rows:
            Y = Y[np.load(args.rows)]
    else:
        if not args.target:
            raise SystemExit("need --target or --target_from_train")
        Y = load_array(args.target)
    F = load_array(args.pred, Y.shape[1])
    if F.shape[0] != Y.shape[0]:
        raise ValueError(f"row mismatch: pred {F.shape[0]} vs target {Y.shape[0]}")

    grid = resolve_grid(args.dataset, int(Y.shape[1]))
    masks, weight, edges = band_masks(grid)
    res = coherence_and_oracle(F, Y, grid, masks, weight)
    res["dataset"] = args.dataset
    res["label"] = args.label
    res["n_rows"] = int(Y.shape[0])
    res["grid"] = [int(grid[0]), int(grid[1])]
    res["band_edges_wavenumber"] = [float(e) for e in edges]

    g1 = res["per_band"].get("band1", {}).get("coherence_energy_weighted")
    if g1 is None:
        label = "UNDETERMINED"
    elif g1 >= GAMMA_ELIGIBLE:
        label = "CORRECTOR_ELIGIBLE"
    elif g1 <= GAMMA_FUTILE:
        label = "CORRECTOR_FUTILE"
    else:
        label = "UNDETERMINED"
    res["verdict"] = {
        "label": label, "gamma_band1": g1,
        "gamma_band0": res["per_band"].get("band0", {}).get("coherence_energy_weighted"),
        "rule": (f"gamma_band1 >= {GAMMA_ELIGIBLE} -> ELIGIBLE (r2s2-B1: same frozen "
                 f"corrector removed 63-95% of the error); <= {GAMMA_FUTILE} -> FUTILE "
                 f"(<= 0.08%); in between the threshold is only bracketed"),
    }
    if args.arm_nrmse is not None:
        after = args.arm_nrmse * (1.0 - res["oracle_lsi_relative_gain"])
        res["implied_arm_nrmse_after_oracle_lsi"] = float(after)
        if args.reference_nrmse:
            res["implied_skill_after_oracle_lsi"] = float(after / args.reference_nrmse)
            res["arm_skill"] = float(args.arm_nrmse / args.reference_nrmse)
            res["max_skill_units_available_from_an_lsi_stage"] = float(
                (args.arm_nrmse - after) / args.reference_nrmse)

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    json.dump({"_tool": "surrogate_coherence_eligibility",
               "_nrmse_def_hash": NRMSE_DEF_HASH,
               "_note": "oracle_* is fitted IN SAMPLE on the rows scored; it is a "
                        "ceiling, never an arm score",
               "result": res}, open(args.out, "w"), indent=1)
    pb = res["per_band"]
    print(f"[{args.dataset}] identity={res['identity_nrmse']:.6f} "
          f"oracle_lsi={res['oracle_lsi_nrmse_insample']:.6f} "
          f"gain={100*res['oracle_lsi_relative_gain']:+.2f}% | "
          f"gamma b0={pb.get('band0',{}).get('coherence_energy_weighted'):.3f} "
          f"b1={pb.get('band1',{}).get('coherence_energy_weighted'):.3f} "
          f"-> {label}")
    print("wrote", args.out)


if __name__ == "__main__":
    main()
