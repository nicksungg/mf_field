#!/usr/bin/env python
"""Across repeated training splits, does an arm's LEARNED MAP change, or only its SCALE?

Provenance: promoted from `r2s3_lf_train_signal-B3` mechanism turns 2-3
(`worktrees/r2s3_lf_train_signal/B3/scratchpad/reanalysis_turn_3.py`, with the
per-sample gain/cosine decomposition from `.../reanalysis_turn_2_pfc.py`).

WHY THIS EXISTS
---------------
When a treatment (LF-at-train, a regulariser, more data) makes an arm's SCORE
stable across training-set draws, the natural story is "it makes the learned
function draw-independent". On r2s3-B3 that story was wrong in a specific and
reusable way: the LF arm's three allen_cahn models scored within 0.41 skill units
of each other while sitting 100.5 skill units APART in function space. What the
treatment actually pinned was the output AMPLITUDE — 96.9 % of the control arm's
726-unit draw-range was one scalar per sample — and any design that assumes a
canonical treated map (single-teacher distillation, weight averaging) is assuming
something the measurement refutes.

This tool separates the two, training-free, from prediction dumps only.

Per arm, per pair of splits (d, d'), per test sample i:

  cos_i    = cos(p_d(i), p_d'(i))                        agreement in SHAPE
  gain_i   = ||p_d(i)|| / ||p_d'(i)||                    agreement in SCALE
  D_tot    = ||p_d(i) - p_d'(i)|| / ||y(i)||             total dispersion
  D_shape  = min_a ||a p_d(i) - p_d'(i)|| / ||y(i)||     dispersion that survives
           = sqrt(1 - cos_i^2) * ||p_d'(i)|| / ||y(i)||    the best per-sample rescale

`D_shape / D_tot` near 0 -> the splits differ by a scale factor and nothing else;
near 1 -> genuinely different functions. Reported in `||y||` units and in skill
units, so the dispersion is directly comparable with the arm's own error.

It also reports, per arm:
  * the per-split score and the per-split score at the ORACLE per-sample gain
    (`sqrt(1-cos^2)` against the target) — a CEILING, never an arm score, that
    prices how much of a score and of a score's SPLIT-RANGE is the amplitude
    channel alone;
  * the SPLIT-ENSEMBLE arm (mean of the split predictions), which is the
    generous upper bound on any variance-only explanation of a treatment's
    effect. It is NOT budget-matched (it sees every split's training rows and
    n_splits x the compute), so it is only usable in one direction: a treatment
    that still beats it is not doing variance reduction; a treatment that loses
    to it has a cheaper alternative.

USAGE
-----
  source "$PROJECT_ROOT/.venv/bin/activate"
  python tools/map_dispersion_scale_shape.py --dataset sharp__allen_cahn_2d \\
      --arm A0_nolf=<outputs>/results_ac_A0_d0/<fam>/<ds>_e200_s0_preds.npz,\\
<outputs>/results_ac_A0_d1/<fam>/<ds>_e200_s0_preds.npz,\\
<outputs>/results_ac_A0_d2/<fam>/<ds>_e200_s0_preds.npz \\
      --arm A1_lf_cov=<...d0>,<...d1>,<...d2> \\
      --ensemble --out dispersion.json

`--arm NAME=path[,path...]` repeatable, `.npy` or `.npz` (key from `--key`,
default `pred_test`); fields may be `(N,H,W)` or `(N,n_cells)`. Targets come from
`round2/eval/panel_data.py` (the offline reference path, read-only) unless
`--targets path[:key]` is given. Pure numpy; ~20 s for 2 arms x 3 splits at
100 x 256^2 on the login node. NOTE: the login shell is nproc-limited — for more
than ~4 arms x 4 splits at 256^2, run it from a batch step or raise `--max_test`
downward.
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROUND_ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROUND_ROOT / "eval"))
from nrmse import nrmse, NRMSE_DEF_HASH             # noqa: E402
from affine_ladder_voi import skill_denominator     # noqa: E402


def _load(spec, key):
    p = spec
    k = key
    if not Path(p).exists() and ":" in spec:
        p, k = spec.rsplit(":", 1)
    p = Path(p)
    if not p.exists():
        raise SystemExit(f"not found: {spec}")
    if p.suffix == ".npz":
        z = np.load(p)
        if k not in z.files:
            raise SystemExit(f"{p} has keys {list(z.files)}; pass path:key")
        return np.asarray(z[k], dtype=np.float64)
    return np.asarray(np.load(p), dtype=np.float64)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--arm", action="append", required=True,
                    help="NAME=pred.npz[,pred.npz...] (one per training split)")
    ap.add_argument("--key", default="pred_test")
    ap.add_argument("--targets", default=None, help="path[:key] of the test targets")
    ap.add_argument("--skill_denominator", type=float, default=None)
    ap.add_argument("--ensemble", action="store_true")
    ap.add_argument("--max_test", type=int, default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    D, dsrc = skill_denominator(a.dataset, a.skill_denominator)
    if a.targets:
        y = _load(a.targets, "hf")
        ysrc = a.targets
    else:
        import panel_data as PD
        d = PD.load_split(a.dataset, "test")
        y = np.asarray(d["field_by_fid"][d["hf_fid"]], dtype=np.float64)
        ysrc = "round2/eval/panel_data.py::load_split(test) [offline reference path]"
    y = y.reshape(y.shape[0], -1)
    if a.max_test:
        y = y[:a.max_test]
    n_test = y.shape[0]
    ny = np.linalg.norm(y, axis=1)

    out = {"_tool": "map_dispersion_scale_shape.py", "_nrmse_def_hash": NRMSE_DEF_HASH,
           "dataset": a.dataset, "n_test": int(n_test), "targets_source": ysrc,
           "skill_denominator": D, "skill_denominator_source": dsrc,
           "_oracle_key_convention": "*_oracle_gain_* is fitted on the test targets; a CEILING, never an arm score",
           "arms": {}}

    for spec in a.arm:
        name, paths = spec.split("=", 1)
        P = [_load(p, a.key).reshape(-1, y.shape[1])[:n_test] for p in paths.split(",") if p]
        n_split = len(P)
        rec = {"n_splits": n_split, "sources": [p for p in paths.split(",") if p],
               "per_split_skill": [float(nrmse(p, y) / D) for p in P],
               "pairs": {}}
        og = []
        for p in P:
            npn = np.linalg.norm(p, axis=1)
            c = (p * y).sum(1) / (npn * ny + 1e-300)
            og.append(float(np.mean(np.sqrt(np.maximum(1 - c ** 2, 0))) / D))
        rec["per_split_oracle_gain_skill"] = og
        rec["per_split_mean_gain_vs_target"] = [
            float((np.linalg.norm(p, axis=1) / ny).mean()) for p in P]
        s = rec["per_split_skill"]
        rec["skill_range_raw"] = float(max(s) - min(s))
        rec["skill_range_at_oracle_gain"] = float(max(og) - min(og))
        rec["gain_channel_share_of_skill_range"] = (
            float(1 - rec["skill_range_at_oracle_gain"] / rec["skill_range_raw"])
            if rec["skill_range_raw"] > 0 else None)
        # the share is only interpretable when the amplitude channel is a driver:
        # if the raw range is already BELOW the oracle-gain range, this arm's
        # split-to-split score variation is not an amplitude story at all.
        rec["gain_channel_share_valid"] = bool(
            rec["skill_range_raw"] >= rec["skill_range_at_oracle_gain"])

        tot, sh, css, gns = [], [], [], []
        for i, j in itertools.combinations(range(n_split), 2):
            pi, pj = P[i], P[j]
            ni, nj = np.linalg.norm(pi, axis=1), np.linalg.norm(pj, axis=1)
            c = (pi * pj).sum(1) / (ni * nj + 1e-300)
            dtot = np.linalg.norm(pi - pj, axis=1) / ny
            dsh = np.sqrt(np.maximum(1 - c ** 2, 0)) * nj / ny
            rec["pairs"][f"{i}-{j}"] = {
                "cos_mean": float(c.mean()), "gain_ratio_mean": float((ni / nj).mean()),
                "D_tot_mean": float(dtot.mean()), "D_shape_mean": float(dsh.mean()),
                "shape_share_of_dispersion": float(dsh.mean() / max(dtot.mean(), 1e-300))}
            tot.append(dtot.mean()); sh.append(dsh.mean())
            css.append(c.mean()); gns.append((ni / nj).mean())
        if tot:
            rec["pairmean_cos"] = float(np.mean(css))
            rec["pairmean_gain_ratio"] = float(np.mean(gns))
            rec["pairmean_D_tot"] = float(np.mean(tot))
            rec["pairmean_D_shape"] = float(np.mean(sh))
            rec["pairmean_shape_share"] = float(np.mean(sh) / max(np.mean(tot), 1e-300))
            rec["D_tot_skill_units"] = float(np.mean(tot) / D)
            rec["D_shape_skill_units"] = float(np.mean(sh) / D)
        if a.ensemble and n_split > 1:
            ens = np.mean(P, axis=0)
            ne = np.linalg.norm(ens, axis=1)
            ce = (ens * y).sum(1) / (ne * ny + 1e-300)
            rec["split_ensemble"] = {
                "skill": float(nrmse(ens, y) / D),
                "mean_gain_vs_target": float((ne / ny).mean()),
                "oracle_gain_skill": float(np.mean(np.sqrt(np.maximum(1 - ce ** 2, 0))) / D),
                "_caveat": ("NOT budget-matched: sees every split's training rows and "
                            "n_splits x the compute. A generous UPPER BOUND on any "
                            "variance-only explanation; usable in one direction only.")}
        out["arms"][name] = rec

    print(f"== {a.dataset}  ({n_test} test samples, denominator {D:.6g}) ==")
    print(f"{'arm':16s} {'cos(d,d2)':>10s} {'gainratio':>10s} {'D_tot':>9s} {'D_shape':>9s} "
          f"{'shape%':>7s} {'D_tot(skill)':>12s}")
    for nm, r in out["arms"].items():
        if "pairmean_D_tot" not in r:
            continue
        print(f"{nm:16s} {r['pairmean_cos']:10.4f} {r['pairmean_gain_ratio']:10.4f} "
              f"{r['pairmean_D_tot']:9.4f} {r['pairmean_D_shape']:9.4f} "
              f"{100*r['pairmean_shape_share']:6.1f}% {r['D_tot_skill_units']:12.2f}")
    print(f"\n{'arm':16s} {'per-split skill':>34s} {'range':>9s} {'range@oracle-gain':>18s} {'gain share':>11s}")
    for nm, r in out["arms"].items():
        s = "/".join(f"{v:.2f}" for v in r["per_split_skill"])
        gs = r["gain_channel_share_of_skill_range"]
        txt = ("%.1f%%" % (100 * gs)) if (gs is not None and r["gain_channel_share_valid"]) \
            else "n/a"
        print(f"{nm:16s} {s:>34s} {r['skill_range_raw']:9.3f} "
              f"{r['skill_range_at_oracle_gain']:18.3f} {txt:>11s}")
    if a.ensemble:
        print(f"\n{'arm':16s} {'split-ensemble skill':>22s}  (NOT budget-matched — upper bound only)")
        for nm, r in out["arms"].items():
            if "split_ensemble" in r:
                print(f"{nm:16s} {r['split_ensemble']['skill']:22.3f}")
    if a.out:
        Path(a.out).write_text(json.dumps(out, indent=1))
        print("\nwrote", a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
