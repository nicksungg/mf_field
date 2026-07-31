#!/usr/bin/env python
"""collapse_set_attribution.py — did MY change break these samples, or were they
already broken? and what identifies them?

Given two or more arms' saved `(pred, target)` on the SAME test split, this
answers the question that decides whether a per-dataset regression (or gain) is
attributable to the change at all:

  1. `pairing` — the arms' `target` arrays must agree; the tool refuses to
     compare otherwise (this is the seam that makes everything below valid).
  2. `attribution` — collapsed fraction per arm (rel-L2 >= `--collapse-threshold`,
     default 0.9 = the trivial-predictor band), the OVERLAP of the collapsed
     sets, and Spearman rho of per-sample rel-L2. High overlap + high rho =>
     the arms fail on the SAME samples and the difference is not a new failure
     mode, it is a shift along a pre-existing hard/easy split.
  3. `separators` — rank-AUC of candidate per-sample features for the reference
     arm's collapse label: `||y||`, DC energy share, a sharpness index
     `mean|grad y| sqrt(n)/||y||`, and (with `--dataset`) the copy-LF per-sample
     rel-L2, the copy-LF-side sharpness (is the hard set visible from the INPUT
     the model may or may not read?), and every condition-vector coordinate.
  4. `subpopulation` — nRMSE of each arm and of copy-LF restricted to the
     collapsed / surviving halves, plus the diagnostic skill on each half.
     A dataset-level skill can be a mixture statistic; this is where you see it.
  5. `trivial_predictor` — the ZERO field has rel-L2 exactly 1 on every sample,
     so its skill is `1/reference_nRMSE` with no training. If an arm's skill is
     near that number, the arm is not predicting, it is abstaining.

Read it as. Overlap ~ 1 and rho > 0.8 => your lever did not create the failure;
do not write a mechanism for it. AUC ~ 1 (or ~ 0) on a FIELD feature but ~ 0.5
on every condition coordinate => the hard set is identifiable from the LF field
and not from the conditioning, so a model that does not read LF at inference
cannot route capacity to it. Arm skill / zero-predictor skill ~ 1 => the arm
is the trivial predictor.

Usage
-----
    source "$PROJECT_ROOT/.venv/bin/activate"
    python tools/collapse_set_attribution.py \
        --preds arm=<a>/preds_test.npz base=<b>/preds_test.npz \
        [--dataset sharp__cahn_hilliard] [--reference-arm arm] \
        [--collapse-threshold 0.9] [--grid 256 256] [--out d.json]

`--dataset` enables the copy-LF / condition-vector separators and the skill
block (loads the test split through `round1/eval/panel_data.py`).

Provenance: worktrees/s7_loss/B1/scratchpad/reanalysis_turn_2{,b,c}.py and
reanalysis_turn_3.py; card experiment_cards/s7_loss/batch_1/B1.json part 6,
findings F6-F9, F11-F12.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROUND = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROUND, "eval"))
import nrmse as nrmse_mod  # noqa: E402  (the round's single metric definition)


def rank_auc(score, label):
    score = np.asarray(score, float)
    label = np.asarray(label, bool)
    if label.all() or not label.any():
        return None
    r = np.empty(len(score))
    r[np.argsort(score)] = np.arange(1, len(score) + 1)
    n1, n0 = label.sum(), (~label).sum()
    return float((r[label].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def spearman(a, b):
    ra = np.argsort(np.argsort(np.asarray(a, float)))
    rb = np.argsort(np.argsort(np.asarray(b, float)))
    return float(np.corrcoef(ra, rb)[0, 1])


def sharpness(flat, grid):
    f = np.asarray(flat, float).reshape(grid)
    gy, gx = np.gradient(f)
    return float(np.mean(np.hypot(gx, gy)) * np.sqrt(f.size) /
                 (np.linalg.norm(f) + 1e-30))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--preds", nargs="+", required=True,
                    help="label=path/preds_test.npz (>= 2)")
    ap.add_argument("--dataset", default=None,
                    help="panel dataset name; enables copy-LF / cond separators")
    ap.add_argument("--reference-arm", default=None,
                    help="arm whose collapse label is attributed (default: first)")
    ap.add_argument("--collapse-threshold", type=float, default=0.9)
    ap.add_argument("--grid", nargs=2, type=int, default=None,
                    help="H W override; default from the npz `work_grid` or square")
    ap.add_argument("--pred_key", default="pred")
    ap.add_argument("--target_key", default="target")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    arms, grid = {}, None
    for item in a.preds:
        if "=" not in item:
            raise SystemExit(f"--preds entries must be label=path, got {item!r}")
        lab, path = item.split("=", 1)
        z = np.load(path)
        arms[lab] = {"pred": z[a.pred_key].astype(np.float64),
                     "target": z[a.target_key].astype(np.float64), "path": path}
        if grid is None and "work_grid" in z.files:
            grid = tuple(int(v) for v in z["work_grid"])
    if len(arms) < 2:
        raise SystemExit("need at least two arms")
    if a.grid:
        grid = tuple(a.grid)

    labels = list(arms)
    ref = a.reference_arm or labels[0]
    if ref not in arms:
        raise SystemExit(f"--reference-arm {ref} not among {labels}")

    # 1. pairing seam ------------------------------------------------------
    n = min(v["target"].shape[0] for v in arms.values())
    t0 = arms[ref]["target"][:n]
    seam = {}
    for lab, v in arms.items():
        d = float(np.max(np.abs(v["target"][:n] - t0)))
        seam[lab] = d
        if d > 1e-5:
            raise SystemExit(f"target mismatch for arm {lab}: max abs {d:.3e} — "
                             "these arms are not on the same test split")
    if grid is None:
        side = int(round(np.sqrt(t0.shape[1])))
        grid = (side, side) if side * side == t0.shape[1] else None

    yn = np.linalg.norm(t0, axis=1)
    rel = {lab: np.linalg.norm(v["pred"][:n] - t0, axis=1) / yn
           for lab, v in arms.items()}
    lab_ref = rel[ref] >= a.collapse_threshold

    rep = {
        "_nrmse_def_hash": nrmse_mod.NRMSE_DEF_HASH,
        "dataset": a.dataset,
        "n_samples": int(n),
        "collapse_threshold": a.collapse_threshold,
        "reference_arm": ref,
        "pairing_target_maxabsdiff_vs_reference": seam,
        "per_arm": {lab: {
            "path": arms[lab]["path"],
            "nrmse_per_sample_mean": float(rel[lab].mean()),
            "frac_collapsed": float((rel[lab] >= a.collapse_threshold).mean()),
            "rel_median": float(np.median(rel[lab])),
        } for lab in labels},
        "attribution_vs_reference": {},
        "separators_AUC_for_reference_collapse": {},
        "subpopulation_nrmse": {},
    }
    for lab in labels:
        if lab == ref:
            continue
        other = rel[lab] >= a.collapse_threshold
        rep["attribution_vs_reference"][lab] = {
            "spearman_rho_per_sample_rel": spearman(rel[ref], rel[lab]),
            "frac_reference_collapsed_also_collapsed_here":
                float(other[lab_ref].mean()) if lab_ref.any() else None,
            "AUC_of_this_arms_rel_for_reference_collapse_label":
                rank_auc(rel[lab], lab_ref),
        }

    feats = {"hf_norm_||y||": yn,
             "dc_energy_share": (t0.mean(1) ** 2 * t0.shape[1]) / (t0 ** 2).sum(1)}
    if grid is not None:
        feats["sharpness_index_hf"] = np.array(
            [sharpness(t0[i], grid) for i in range(n)])
    for lab in labels:
        if lab != ref:
            feats[f"rel_l2_of_arm[{lab}]"] = rel[lab]

    clf_rel = None
    if a.dataset:
        import panel_data
        data = panel_data.load_split(a.dataset, "test")
        hf = np.asarray(data["field_by_fid"][data["hf_fid"]], float)[:n]
        if float(np.max(np.abs(hf - t0))) > 1e-5:
            raise SystemExit("loader HF split does not match the arms' target")
        clf = panel_data.copylf_prediction(data)[:n]
        clf_rel = np.linalg.norm(clf - hf, axis=1) / np.linalg.norm(hf, axis=1)
        feats["copylf_rel_l2"] = clf_rel
        if grid is not None:
            feats["sharpness_index_LF_SIDE"] = np.array(
                [sharpness(clf[i], grid) for i in range(n)])
        cond = np.asarray(data["cond_by_fid"][data["hf_fid"]], float)[:n]
        for j in range(cond.shape[1]):
            if np.ptp(cond[:, j]) > 0:
                feats[f"cond[{j}]"] = cond[:, j]

    rep["separators_AUC_for_reference_collapse"] = {
        k: rank_auc(v, lab_ref) for k, v in feats.items()}
    rep["feature_medians_collapsed_vs_surviving"] = {
        k: {"collapsed": float(np.median(np.asarray(v)[lab_ref])) if lab_ref.any() else None,
            "surviving": float(np.median(np.asarray(v)[~lab_ref])) if (~lab_ref).any() else None}
        for k, v in feats.items()}

    def blk(m):
        return {"all": float(np.mean(m)),
                "collapsed_subpop": float(np.mean(m[lab_ref])) if lab_ref.any() else None,
                "surviving_subpop": float(np.mean(m[~lab_ref])) if (~lab_ref).any() else None}

    rep["subpopulation_nrmse"] = {lab: blk(rel[lab]) for lab in labels}
    if clf_rel is not None:
        rep["subpopulation_nrmse"]["copylf"] = blk(clf_rel)

    if a.dataset:
        ref_json = os.path.join(ROUND, "eval", "copylf_baselines.json")
        base = json.load(open(ref_json))
        if a.dataset in base:
            rn = base[a.dataset]["test_nrmse"]
            rep["trivial_predictor"] = {
                "reference_nrmse": rn,
                "reference_type": base[a.dataset]["reference_type"],
                "copylf_recomputed_vs_frozen_absdiff":
                    float(abs(clf_rel.mean() - rn)) if clf_rel is not None
                    and base[a.dataset]["reference_type"] == "copylf" else None,
                "zero_predictor_skill_1_over_reference": 1.0 / rn,
                "arm_skill": {lab: float(rel[lab].mean() / rn) for lab in labels},
                "arm_skill_over_zero_predictor_skill_1_means_ARM_IS_THE_ZERO_FIELD":
                    {lab: float(rel[lab].mean()) for lab in labels},
            }

    txt = json.dumps(rep, indent=1)
    print(txt)
    if a.out:
        with open(a.out, "w") as f:
            f.write(txt)
        print(f"[wrote] {a.out}")


if __name__ == "__main__":
    main()
