#!/usr/bin/env python
"""head_subspace_surgery.py -- IS A SMALL ARM'S WIN (OR LOSS) AGAINST A BIG ARM
A CAPACITY VERDICT OR A COORDINATE VERDICT?

Given two arms' test predictions on the same dataset -- typically a low-rank
closed-form / few-parameter arm ("small") and a high-capacity decoder ("big") --
this recovers the SMALL arm's own fitted subspace `H` from its predictions
alone (no model code, no checkpoint, no training) and prices, in the round's own
metric:

  * a DEPLOYABLE counterfactual: the hybrid `small|H + big|H-perp`, i.e. the
    small arm's coordinates inside its subspace and the big arm's structure
    outside it.  No test label enters its construction, so it is what a free
    combination would actually have scored;
  * the ORACLE ceiling of the small arm's subspace (the truth projected onto
    `H`), which no predictor confined to `H` can beat;
  * ORACLE channel repairs (global gain / per-sample gain / per-sample level /
    per-sample gain&level) on both arms, which say WHICH channel a gap lives in;
  * the OFF-SUBSPACE USEFULNESS test: `cos(small-arm error, big-arm content
    outside H)` and the ORACLE alpha on `small + alpha * big_perp`, which says
    whether the big arm's extra parameters bought any structure the small arm
    is missing.

WHY THIS EXISTS
---------------
`r2s1_direct-B3` scored a 10-parameter closed-form head against a 15 853 057-
parameter FiLM-FNO decoder on `sharp__allen_cahn_2d` and won by 75x the
certified `min_claimable_effect`.  This probe showed the headline was a
COORDINATE verdict, not a capacity one: the dataset is 98.1 % a single constant
direction, the head sits 2.11 mce above the ORACLE ceiling of its own rank-2
subspace, the decoder's deficit is one affine level bias (slope 0.954, corr
0.9925), and a test-label-free replacement of the decoder's coordinates inside
`H` closes 94.4 % of the gap.  On five of six panel cells the decoder's
off-`H` output was orthogonal noise (|cos| <= 0.017); on the sixth
(`sharp__cahn_hilliard`) it was genuinely complementary (cos +0.234, ORACLE
alpha* 0.713) and the free hybrid beat BOTH arms.  Run this before writing
"model A beats model B" in any card that compares arms of very different size.

WHAT IT REPORTS (per dataset)
-----------------------------
  rank / dim_H                 numerical rank of the small arm's predictions
  small_pred_energy_outside_H  self-check that `H` was recovered (should be ~0)
  target_energy_share_in_H     how much of the test truth `H` can hold at all
  skill_{small,big}            the two shipped arms, in the round's skill units
  skill_hybrid_DEPLOYABLE      small|H + big|H-perp  (a real, claimable arm)
  skill_projection_DEPLOYABLE  big projected onto H
  skill_*_ORACLE               ceilings; NEVER quote one as an arm score
  cos_smallerr_vs_bigperp      the off-subspace usefulness separator
  alpha_star_ORACLE / grid     pooled least-squares alpha and the sweep

INTERPRETATION KEYS
-------------------
  |cos| <~ 0.02 and alpha* ~ 0   the big arm contributes NOTHING outside H;
                                 a parameter-count comparison is measuring
                                 coordinates, not capacity.
  cos > 0.1 and alpha* ~ 1       genuinely complementary arms; the free hybrid
                                 is worth scoring as its own arm.
  head within a few mce of the
  truth-in-H ORACLE              the small arm has exhausted its subspace; the
                                 lever is the subspace / the estimator, not the
                                 fit.

USAGE
-----
  source "$PROJECT_ROOT/.venv/bin/activate"
  python tools/head_subspace_surgery.py \
      --dataset sharp__cahn_hilliard \
      --small_arm  <outputs>/preds_test_test_hf_sharp__cahn_hilliard_s0.npz \
      --big_arm    <outputs>/preds_test_ref_decoder_big_sharp__cahn_hilliard_s0.npz \
      --out surgery_ch.json
  # several datasets at once: repeat --dataset/--small_arm/--big_arm triples
  # (order-aligned), or pass --arm_glob patterns; see --help.

Predictions may be `.npz` (key `pred`, the round's `preds_test_*` convention) or
`.npy`.  Targets come from the stripped view by default (`test_l*.npz` key `y`,
or the ifc_raw `test/fidelity_<F>/ys.npy` layout) and can be overridden with
`--targets`.

Provenance: promoted from `r2s1_direct-B3` mechanism turn 2
(`worktrees/r2s1_direct/B3/scratchpad/reanalysis_turn_2.py`, `..._turn_2b.py`).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import subprocess
import sys

import numpy as np


# ── round plumbing ──────────────────────────────────────────────────

def _repo_root() -> pathlib.Path:
    here = pathlib.Path(__file__).resolve()
    try:
        out = subprocess.run(["git", "-C", str(here.parent), "rev-parse",
                              "--show-toplevel"], capture_output=True, text=True,
                             check=True).stdout.strip()
        return pathlib.Path(out)
    except Exception:
        return here.parents[3]


ROUND_ROOT = pathlib.Path(__file__).resolve().parents[1]
EVAL_DIR = ROUND_ROOT / "eval"


def _load_nrmse():
    spec = importlib.util.spec_from_file_location("round_eval_nrmse",
                                                  EVAL_DIR / "nrmse.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


NR = _load_nrmse()


def load_pred(path: str) -> np.ndarray:
    p = pathlib.Path(path)
    if p.suffix == ".npz":
        z = np.load(p)
        key = "pred" if "pred" in z.files else z.files[0]
        a = z[key]
    else:
        a = np.load(p)
    a = np.asarray(a, dtype=np.float64)
    return a.reshape(a.shape[0], -1)


def load_targets(dataset: str, data_root: pathlib.Path,
                 override: str | None) -> np.ndarray:
    if override:
        return load_pred(override)
    dd = data_root / dataset
    tests = sorted(dd.glob("test_l*.npz"))
    if tests:
        z = np.load(tests[-1])
        y = np.asarray(z["y"], dtype=np.float64)
        return y.reshape(y.shape[0], -1)
    fids = sorted((dd / "test").glob("fidelity_*"))
    if not fids:
        raise SystemExit(f"no test split found under {dd}")
    y = np.load(fids[-1] / "ys.npy")
    y = np.asarray(y, dtype=np.float64)
    return y.reshape(y.shape[0], -1)


def skill_ref(dataset: str, copylf: pathlib.Path) -> float | None:
    d = json.loads(pathlib.Path(copylf).read_text())
    if dataset in d and "test_nrmse" in d[dataset]:
        return float(d[dataset]["test_nrmse"])
    return None


# ── the probe ───────────────────────────────────────────────────────

def subspace(pred: np.ndarray, rank: str | int, tol: float) -> tuple[np.ndarray, dict]:
    """Orthonormal rows spanning the row space of `pred` (its reachable set)."""
    U, s, Vt = np.linalg.svd(pred, full_matrices=False)
    if rank == "auto":
        r = int(np.sum(s > tol * s[0])) if s[0] > 0 else 1
    else:
        r = int(rank)
    r = max(1, min(r, Vt.shape[0]))
    B = Vt[:r]
    resid = pred - (pred @ B.T) @ B
    meta = {"rank": r, "singular_values": [float(v) for v in s[: min(len(s), 12)]],
            "pred_energy_outside_H": float((resid ** 2).sum()),
            "pred_energy_outside_H_share":
                float((resid ** 2).sum() / max((pred ** 2).sum(), 1e-300))}
    return B, meta


def or_gain_global(p, y):
    return float((p * y).sum() / (p * p).sum()) * p


def or_gain_persample(p, y):
    a = (p * y).sum(1) / (p * p).sum(1)
    return a[:, None] * p


def or_level_persample(p, y):
    return p + (y - p).mean(1)[:, None]


def or_gain_level_persample(p, y):
    out = np.empty_like(p)
    ones = np.ones(p.shape[1])
    for i in range(p.shape[0]):
        A = np.stack([p[i], ones], 1)
        coef, *_ = np.linalg.lstsq(A, y[i], rcond=None)
        out[i] = A @ coef
    return out


def run(dataset: str, small: np.ndarray, big: np.ndarray, y: np.ndarray,
        rank, tol: float, ref: float | None, alphas) -> dict:
    if not (small.shape == big.shape == y.shape):
        raise SystemExit(f"shape mismatch on {dataset}: small {small.shape} "
                         f"big {big.shape} target {y.shape}")
    B, meta = subspace(small, rank, tol)
    d = {"dataset": dataset, "n_test": int(y.shape[0]), "n_cells": int(y.shape[1]),
         "dim_H": meta["rank"], "subspace": meta,
         "nrmse_def_hash": NR.NRMSE_DEF_HASH}

    def sc(name, arr, oracle=False):
        n = float(NR.nrmse(arr, y))
        key = f"{name}_ORACLE" if oracle else name
        d.setdefault("arms", {})[key] = {
            "nrmse": n, "skill": (NR.skill(n, ref) if ref else None)}
        return n

    small_H = (small @ B.T) @ B
    big_H = (big @ B.T) @ B
    big_perp = big - big_H
    y_H = (y @ B.T) @ B
    d["target_energy_share_in_H"] = float((y_H ** 2).sum() / (y ** 2).sum())

    sc("small", small)
    sc("big", big)
    sc("hybrid_small_in_H_plus_big_perp_DEPLOYABLE", small_H + big_perp)
    sc("big_projected_on_H_DEPLOYABLE", big_H)
    sc("big_perp_only_DEPLOYABLE", big_perp)
    sc("truth_projected_on_H", y_H, oracle=True)
    for tag, arm in (("small", small), ("big", big)):
        sc(f"{tag}_global_gain", or_gain_global(arm, y), oracle=True)
        sc(f"{tag}_persample_gain", or_gain_persample(arm, y), oracle=True)
        sc(f"{tag}_persample_level", or_level_persample(arm, y), oracle=True)
        sc(f"{tag}_persample_gain_and_level", or_gain_level_persample(arm, y),
           oracle=True)

    err = y - small
    na, nb = np.linalg.norm(err), np.linalg.norm(big_perp)
    cos = float((err * big_perp).sum() / (na * nb)) if na > 0 and nb > 0 else float("nan")
    astar = float((err * big_perp).sum() / max((big_perp ** 2).sum(), 1e-300))
    grid = {}
    for a in alphas:
        n = float(NR.nrmse(small + a * big_perp, y))
        grid[str(a)] = {"nrmse": n, "skill": (NR.skill(n, ref) if ref else None)}
    n_star = float(NR.nrmse(small + astar * big_perp, y))
    d["off_subspace"] = {
        "cos_smallerr_vs_bigperp": cos,
        "alpha_star_pooled_LS_ORACLE": astar,
        "skill_at_alpha_star_ORACLE": (NR.skill(n_star, ref) if ref else None),
        "nrmse_at_alpha_star_ORACLE": n_star,
        "bigperp_energy_over_smallerr_energy":
            float((big_perp ** 2).sum() / max((err ** 2).sum(), 1e-300)),
        "frac_samples_hybrid_beats_small": float(np.mean(
            np.linalg.norm(small + big_perp - y, axis=1)
            < np.linalg.norm(small - y, axis=1))),
        "alpha_grid": grid,
    }
    # per-direction coefficient regressions inside H (who owns the coordinates)
    ct, cs, cb = y @ B.T, small @ B.T, big @ B.T
    per = []
    for j in range(B.shape[0]):
        row = {"direction": j}
        for tag, c in (("small", cs), ("big", cb)):
            A = np.stack([ct[:, j], np.ones(ct.shape[0])], 1)
            coef, *_ = np.linalg.lstsq(A, c[:, j], rcond=None)
            row[f"{tag}_slope_on_truth"] = float(coef[0])
            row[f"{tag}_intercept"] = float(coef[1])
            row[f"{tag}_corr"] = float(np.corrcoef(ct[:, j], c[:, j])[0, 1])
            row[f"{tag}_rel_coeff_rmse"] = float(
                np.sqrt(((c[:, j] - ct[:, j]) ** 2).mean())
                / max(np.sqrt((ct[:, j] ** 2).mean()), 1e-300))
        per.append(row)
    d["per_direction_in_H"] = per
    verdict = ("COMPLEMENTARY_OFF_SUBSPACE" if cos > 0.1
               else "COORDINATE_ONLY" if abs(cos) <= 0.05
               else "AMBIGUOUS")
    d["verdict"] = verdict
    return d


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dataset", action="append", required=True,
                    help="dataset name (repeatable; aligned with --small_arm/--big_arm)")
    ap.add_argument("--small_arm", action="append", required=True)
    ap.add_argument("--big_arm", action="append", required=True)
    ap.add_argument("--targets", action="append", default=None,
                    help="optional explicit test-target file per dataset")
    ap.add_argument("--data_root", default=str(ROUND_ROOT / "stripped_data"))
    ap.add_argument("--copylf", default=str(EVAL_DIR / "copylf_baselines.json"))
    ap.add_argument("--rank", default="auto", help="'auto' or an integer")
    ap.add_argument("--rank_tol", type=float, default=1e-8,
                    help="singular-value cutoff (relative to s_max) for 'auto'")
    ap.add_argument("--alphas", default="-0.5,-0.25,0,0.25,0.5,0.75,1.0,1.25,1.5")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    n = len(args.dataset)
    if not (len(args.small_arm) == len(args.big_arm) == n):
        raise SystemExit("--dataset/--small_arm/--big_arm must be given the same "
                         "number of times")
    targets = args.targets or [None] * n
    if len(targets) != n:
        raise SystemExit("--targets, if given, must be repeated once per dataset")
    alphas = [float(a) for a in args.alphas.split(",") if a != ""]

    rep = {"nrmse_def_hash": NR.NRMSE_DEF_HASH, "datasets": {}}
    for i, ds in enumerate(args.dataset):
        y = load_targets(ds, pathlib.Path(args.data_root), targets[i])
        small = load_pred(args.small_arm[i])
        big = load_pred(args.big_arm[i])
        ref = skill_ref(ds, pathlib.Path(args.copylf))
        d = run(ds, small, big, y, args.rank, args.rank_tol, ref, alphas)
        rep["datasets"][ds] = d
        a = d["arms"]
        print(f"[{ds}] dim_H={d['dim_H']} | small {a['small']['nrmse']:.6f} "
              f"| big {a['big']['nrmse']:.6f} | hybrid "
              f"{a['hybrid_small_in_H_plus_big_perp_DEPLOYABLE']['nrmse']:.6f} "
              f"| truth-in-H ORACLE {a['truth_projected_on_H_ORACLE']['nrmse']:.6f} "
              f"| cos {d['off_subspace']['cos_smallerr_vs_bigperp']:+.4f} "
              f"| alpha* {d['off_subspace']['alpha_star_pooled_LS_ORACLE']:+.3f} "
              f"| {d['verdict']}", flush=True)
    pathlib.Path(args.out).write_text(json.dumps(rep, indent=1))
    print("wrote", args.out)


if __name__ == "__main__":
    main()
