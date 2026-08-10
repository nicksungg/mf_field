#!/usr/bin/env python
"""Amplitude / level calibration audit for a panel cell.

WHAT IT MEASURES

The round's nRMSE is `mean_i ||pred_i - y_i|| / ||y_i||` -- a MEAN OF PER-ROW
RATIOS. On a cell whose test fields are near-uniform in shape but vary in
AMPLITUDE, that statistic is dominated by how well a model reproduces each
row's field NORM, and the smallest-norm rows carry the most weight (the
denominator is theirs). A model whose output parameterisation cannot express
per-row amplitude -- a factorised/normalised head, a renormalising decoder, a
shape-only basis -- is then capped far above the floor no matter how good its
shape prediction is, and an energy-space or residual-subspace audit will not
see it (it can even report the model as BETTER than the floor).

Two modes, both usable:

  DATASET-SIDE (no model needed, `--dataset` only)
    * CV(||y||) on the split -- how much amplitude there is to get wrong;
    * the CONSTANT-NORM ORACLE: the best any norm-blind predictor can do, i.e.
      `nrmse(a * y_i/||y_i||, y_i)` with the shape EXACT and the amplitude
      replaced by a single constant, reported for both the geometric-mean and
      the nRMSE-optimal constant. This is an upper bound on the achievable
      skill of any model that renormalises its output;
    * the same in copy-LF skill units against the frozen round-2 divisor;
    * verdict AMPLITUDE_CRITICAL when the oracle's skill exceeds `--tau-rel`.

  MODEL-SIDE (`--pred LABEL=/path/preds.npz`, repeatable)
    * CV(||pred||) per arm -- 0.0 means the arm is literally norm-blind;
    * per-row rel-L2 by ||y|| quartile, and, when two arms are given via
      `--arm`/`--ref`, the paired delta's correlation with 1/||y|| and each
      quartile's share of the total gap.

WHEN TO RUN IT

Before committing a batch to a cell, and after any card whose model has an
encode/decode or basis parameterisation. It answers "is this cell's score an
amplitude problem?" and "is my arm norm-blind?" -- two questions that a
residual-energy or per-band decomposition structurally cannot answer.

PROVENANCE: card `r3s1_factorised-B2`, mechanism turns 3B/3C. There, fisher_kpp
scored 361.48 against an affine floor of 270.54 while its TOTAL encoded
residual energy was LOWER than affine's; the reconciliation was CV(||pred||) =
0.0000 exactly vs CV(||y||) = 0.0506 under the head's `fact` centering, with
57% of the gap in the lowest ||y|| quartile and corr(delta, 1/||y||) = +0.612.

All metric definitions are imported read-only from
`mffp_autoresearch/round2/eval/{nrmse.py, panel_data.py}`; nothing is
hand-rolled.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np


def _round2_eval_dir() -> Path:
    here = Path(__file__).resolve()
    for p in here.parents:
        cand = p / "mffp_autoresearch" / "round2" / "eval"
        if cand.exists():
            return cand
    raise SystemExit("could not locate mffp_autoresearch/round2/eval from this file")


EVAL = _round2_eval_dir()
sys.path.insert(0, str(EVAL))
import nrmse as nr          # noqa: E402
import panel_data as pd     # noqa: E402


def rel_l2_per_sample(pred, y):
    pred = np.asarray(pred, dtype=np.float64).reshape(len(pred), -1)
    y = np.asarray(y, dtype=np.float64).reshape(len(y), -1)
    return np.linalg.norm(pred - y, axis=1) / np.linalg.norm(y, axis=1)


def copylf_divisor(dataset: str, path: Path):
    d = json.loads(Path(path).read_text())
    if dataset not in d:
        raise SystemExit(f"{dataset} not in {path}")
    return float(d[dataset]["test_nrmse"])


def load_hf(dataset: str, split: str) -> np.ndarray:
    """HF fields of `split`, flattened. Same accessor as
    `tools/per_row_paired_decomposition.py` (`field_by_fid[hf_fid]`)."""
    if dataset == "sharp__allen_cahn_2d" and split == "test":
        sys.stderr.write(
            "WARNING: ADR r3-0003 trimmed sharp__allen_cahn_2d's scored test split; "
            "panel_data.load_split returns the UNTRIMMED original, so row counts "
            "will disagree with a scored artifact.\n")
    data = pd.load_split(dataset, split)
    y = np.asarray(data["field_by_fid"][data["hf_fid"]], dtype=np.float64)
    return y.reshape(y.shape[0], -1)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--split", default="test")
    ap.add_argument("--pred", action="append", default=[],
                    metavar="LABEL=/path/preds.npz",
                    help="repeatable; npz carrying --pred-key")
    ap.add_argument("--pred-key", default="pred_test")
    ap.add_argument("--arm", default=None, help="label of the arm in a paired read")
    ap.add_argument("--ref", default=None, help="label of the reference in a paired read")
    ap.add_argument("--tau-rel", type=float, default=None,
                    help="the cell's certified tau_rel, for the AMPLITUDE_CRITICAL verdict")
    ap.add_argument("--copylf-json", default=str(EVAL / "copylf_baselines.json"))
    ap.add_argument("--quantiles", type=int, default=4)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    y = load_hf(a.dataset, a.split)
    ny = np.linalg.norm(y, axis=1)
    div = copylf_divisor(a.dataset, Path(a.copylf_json))
    shape = y / ny[:, None]

    amp_geo = float(np.exp(np.mean(np.log(ny))))
    # A norm-blind predictor with EXACT shape has y_i = n_i * s_i and ||s_i|| = 1,
    # so ||a*s_i - y_i|| = |a - n_i| and the objective collapses to
    #     f(a) = mean_i |a - n_i| / n_i,
    # whose minimiser is the WEIGHTED MEDIAN of {n_i} with weights 1/n_i.  Closed
    # form -- no grid search, and asserted against nrmse() below.
    order = np.argsort(ny)
    w = (1.0 / ny)[order]
    amp_opt = float(ny[order][int(np.searchsorted(np.cumsum(w), 0.5 * w.sum()))])
    f = lambda aa: float(np.mean(np.abs(aa - ny) / ny))
    for aa in (amp_geo, amp_opt):
        assert abs(f(aa) - float(nr.nrmse(aa * shape, y))) < 1e-9, \
            "closed-form norm-blind objective disagrees with round2 nrmse()"

    out = {
        "dataset": a.dataset, "split": a.split, "n_rows": int(len(y)),
        "copylf_divisor": div,
        "norm_y": {"mean": float(ny.mean()), "std": float(ny.std()),
                   "cv": float(ny.std() / ny.mean()),
                   "min": float(ny.min()), "max": float(ny.max())},
        "constant_norm_oracle": {
            "_what": ("shape EXACT, amplitude replaced by one constant: the best "
                      "achievable by ANY norm-blind predictor on this cell"),
            "amp_geomean": amp_geo,
            "nrmse_at_geomean": float(nr.nrmse(amp_geo * shape, y)),
            "skill_at_geomean": float(nr.nrmse(amp_geo * shape, y)) / div,
            "amp_nrmse_optimal": amp_opt,
            "nrmse_at_optimal": float(nr.nrmse(amp_opt * shape, y)),
            "skill_at_optimal": float(nr.nrmse(amp_opt * shape, y)) / div,
        },
    }
    sk = out["constant_norm_oracle"]["skill_at_optimal"]
    if a.tau_rel is not None:
        out["tau_rel"] = a.tau_rel
        out["x_tau_rel"] = sk / a.tau_rel
        out["verdict"] = "AMPLITUDE_CRITICAL" if sk > a.tau_rel else "amplitude_not_binding"
    print(f"[{a.dataset} / {a.split}] n = {len(y)} rows; copy-LF divisor {div:.6g}")
    print(f"  CV(||y||) = {out['norm_y']['cv']:.4f}  "
          f"(mean {ny.mean():.6g}, range {ny.min():.6g} .. {ny.max():.6g})")
    print(f"  CONSTANT-NORM ORACLE (shape exact, one amplitude): "
          f"nRMSE {out['constant_norm_oracle']['nrmse_at_optimal']:.6g} = "
          f"{sk:.4f} skill   [at the geomean amplitude: {out['constant_norm_oracle']['skill_at_geomean']:.4f}]")
    if a.tau_rel is not None:
        print(f"  => {out['verdict']}: a norm-blind arm is floored at {sk:.4f} skill "
              f"= {sk/a.tau_rel:.2f}x the certified tau_rel {a.tau_rel:g}")

    preds = {}
    for spec in a.pred:
        if "=" not in spec:
            raise SystemExit(f"--pred needs LABEL=path, got {spec!r}")
        lab, path = spec.split("=", 1)
        z = np.load(path)
        key = a.pred_key if a.pred_key in z else list(z.keys())[0]
        p = np.asarray(z[key], dtype=np.float64).reshape(len(z[key]), -1)
        if p.shape != y.shape:
            raise SystemExit(f"{lab}: prediction shape {p.shape} != target {y.shape}")
        preds[lab] = p

    if preds:
        qs = np.quantile(ny, np.linspace(0, 1, a.quantiles + 1)[1:-1])
        bins = np.digitize(ny, qs)
        out["arms"] = {}
        print(f"\n  per-arm amplitude calibration ({a.quantiles} ||y|| bins):")
        for lab, p in preds.items():
            npd = np.linalg.norm(p, axis=1)
            e = rel_l2_per_sample(p, y)
            rec = {"nrmse": float(nr.nrmse(p, y)), "skill": float(nr.nrmse(p, y)) / div,
                   "cv_norm_pred": float(npd.std() / npd.mean()),
                   "norm_blind": bool(npd.std() / npd.mean() < 1e-9),
                   "corr_err_vs_inv_norm_y": float(np.corrcoef(e, 1.0 / ny)[0, 1]),
                   "per_bin_rel_l2": [float(e[bins == b].mean()) for b in range(a.quantiles)]}
            out["arms"][lab] = rec
            print(f"    {lab:16s} skill {rec['skill']:10.4f}  CV(||pred||) {rec['cv_norm_pred']:.4f}"
                  f"{'  <-- NORM-BLIND' if rec['norm_blind'] else ''}  "
                  f"corr(err, 1/||y||) {rec['corr_err_vs_inv_norm_y']:+.3f}")
            print(f"       rel-L2 by ||y|| bin: "
                  + "  ".join(f"{v:.5f}" for v in rec["per_bin_rel_l2"]))

        if a.arm and a.ref:
            if a.arm not in preds or a.ref not in preds:
                raise SystemExit("--arm/--ref must name labels given with --pred")
            d = rel_l2_per_sample(preds[a.arm], y) - rel_l2_per_sample(preds[a.ref], y)
            share = [float(d[bins == b].sum() / len(d) / div) for b in range(a.quantiles)]
            tot = float(d.mean() / div)
            out["paired"] = {
                "arm": a.arm, "ref": a.ref, "gap_skill": tot,
                "n_rows_arm_worse": int((d > 0).sum()), "n_rows": int(len(d)),
                "median_delta": float(np.median(d)), "mean_delta": float(d.mean()),
                "corr_delta_vs_inv_norm_y": float(np.corrcoef(d, 1.0 / ny)[0, 1]),
                "per_bin_skill_contribution": share,
                "per_bin_share_of_gap": [s / tot if tot else None for s in share]}
            print(f"\n  paired {a.arm} - {a.ref}: gap {tot:+.4f} skill; "
                  f"{out['paired']['n_rows_arm_worse']}/{len(d)} rows worse; "
                  f"corr(delta, 1/||y||) {out['paired']['corr_delta_vs_inv_norm_y']:+.3f}")
            for b in range(a.quantiles):
                print(f"    ||y|| bin {b}: contributes {share[b]:+.4f} skill "
                      f"({100*share[b]/tot if tot else float('nan'):.1f}% of the gap)")

    if a.out:
        Path(a.out).write_text(json.dumps(out, indent=1, default=float))
        print(f"\n  -> {a.out}")


if __name__ == "__main__":
    main()
