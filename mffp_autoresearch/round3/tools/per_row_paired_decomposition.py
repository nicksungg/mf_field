#!/usr/bin/env python
"""Per-row decomposition of a paired arm comparison.

WHY THIS EXISTS
---------------
This round's metric is `nRMSE = mean_i ||pred_i - y_i||_2 / ||y_i||_2`
(`round2/eval/nrmse.py`) — a **mean of per-row ratios**. That makes every paired
arm delta decompose exactly, row by row:

    d_i = e_ref_i - e_arm_i     and     mean_i d_i == nRMSE_ref - nRMSE_arm

so a panel delta can be interrogated without re-running anything. The questions
this answers, which a scalar nRMSE cannot:

  * **Is the effect broad or is it a handful of rows?**  sign counts, median vs
    mean, top-k share of the total delta, and TRIMMED re-scores (drop the k
    worst reference rows; adversarially drop the k rows the effect most depends
    on). An outlier-driven effect dies under the adversarial trim; a real one
    does not.
  * **Is there a row-level CI?**  A bootstrap over test rows, complementary to
    the round's bootstrap over seeds — and on the same skill scale, so it can be
    read straight against a certified `tau_rel` / `min_claimable_effect`.
  * **Is the cell one population or several?**  `--bimodal-split T` splits the
    rows at a per-row reference error of T (`ref_zero` is exactly 1.0 by
    construction, so T ~ 0.8 means "as bad as predicting zero") and scores the
    two populations separately, reporting each one's share of the total gain.
    A cell whose skill is a mixture statistic must be read as one.

Provenance: `r3s1_factorised-B1` mechanism turns 2-3, where it showed that the
whole panel win was (a) broad — 78-82/100 rows, top-5 share 12-13 %, surviving
an adversarial 10-row trim at ~3x the certified floor — and (b) confined to a
73-row identifiable subpopulation, with 27 seed-invariant rows scoring worse
than `ref_zero` under every arm.

INPUT MODES
-----------
1. `--result <result.json>` — any family result JSON whose `splits[arm]` carries
   `rel_l2_per_sample` (the Model Family Contract's per-sample record). Arms are
   auto-discovered. No dataset access, no venv beyond numpy.
2. `--pred LABEL=/path/preds.npz --dataset <name>` — per-row errors are computed
   from predictions against the dataset's HF test split via
   `round2/eval/panel_data.py` + `round2/eval/nrmse.py`. Use `--pred-key` for a
   non-default array name.

Skill units come from the frozen `round2/eval/copylf_baselines.json` divisor for
the dataset, so every number is directly comparable to a card's skill column.

EXAMPLES
--------
  python tools/per_row_paired_decomposition.py \
    --result <outputs>/training/<family>/sharp__cahn_hilliard_e0_s0.json \
    --dataset sharp__cahn_hilliard --arm test_hf --ref ref_head_onestage \
    --bimodal-split 0.8

  python tools/per_row_paired_decomposition.py \
    --dataset sharp__cahn_hilliard \
    --pred A1=/path/A1/..._preds.npz --pred A0=/path/A0/..._preds.npz \
    --arm A1 --ref A0
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys

import numpy as np

EVAL_DIR = None


def _find_eval_dir() -> pathlib.Path:
    here = pathlib.Path(__file__).resolve()
    for p in here.parents:
        cand = p / "mffp_autoresearch" / "round2" / "eval"
        if cand.is_dir():
            return cand
    raise RuntimeError("could not locate mffp_autoresearch/round2/eval from "
                       f"{here}; pass --eval-dir")


def _load_eval(eval_dir: pathlib.Path):
    if str(eval_dir) not in sys.path:
        sys.path.insert(0, str(eval_dir))
    import nrmse as nrmse_mod  # noqa: E402
    return nrmse_mod


def copylf_divisor(eval_dir: pathlib.Path, dataset: str):
    path = eval_dir / "copylf_baselines.json"
    if not path.exists() or dataset is None:
        return None
    with open(path) as f:
        base = json.load(f)
    if dataset not in base:
        return None
    return float(base[dataset]["test_nrmse"])


# ── input mode 1: result JSON ────────────────────────────────────────────────
def rows_from_result(path: str, nrmse_mod) -> dict:
    with open(path) as f:
        res = json.load(f)
    splits = res.get("splits", {})
    out = {}
    for arm, blk in splits.items():
        if not isinstance(blk, dict) or "rel_l2_per_sample" not in blk:
            continue
        e = np.asarray(blk["rel_l2_per_sample"], dtype=np.float64)
        # metric seam: the mean of the per-row ratios IS the arm's nRMSE
        if "nRMSE" in blk and abs(float(e.mean()) - float(blk["nRMSE"])) > 1e-12:
            raise RuntimeError(
                f"METRIC SEAM FAILED for arm {arm} in {path}: "
                f"mean(rel_l2_per_sample) = {e.mean()!r} != nRMSE {blk['nRMSE']!r}. "
                "Refusing to decompose a delta whose per-row record does not "
                "reproduce its own score.")
        out[arm] = e
    if not out:
        raise RuntimeError(f"no arm in {path} carries `rel_l2_per_sample`; "
                           "use --pred mode instead")
    return out


# ── input mode 2: prediction npz ─────────────────────────────────────────────
def rows_from_preds(specs, dataset: str, pred_key: str, split: str,
                    eval_dir: pathlib.Path) -> dict:
    if str(eval_dir) not in sys.path:
        sys.path.insert(0, str(eval_dir))
    import panel_data  # noqa: E402
    if dataset == "sharp__allen_cahn_2d":
        sys.stderr.write(
            "[warn] sharp__allen_cahn_2d's scored test split was TRIMMED by "
            "ADR r3-0003 (tools/trim_ac_task_void.py); panel_data.load_split "
            "returns the UNTRIMMED original. Row counts will disagree with a "
            "scored artifact. Prefer --result mode on this cell.\n")
    data = panel_data.load_split(dataset, split)
    target = np.asarray(data["field_by_fid"][data["hf_fid"]], dtype=np.float64)
    target = target.reshape(target.shape[0], -1)
    denom = np.linalg.norm(target, axis=1)
    if (denom == 0).any():
        raise RuntimeError("zero-norm target row")
    out = {}
    for spec in specs:
        if "=" not in spec:
            raise SystemExit(f"--pred must be LABEL=path, got {spec!r}")
        label, path = spec.split("=", 1)
        z = np.load(path)
        if pred_key not in z.files:
            raise SystemExit(f"{path} has no key {pred_key!r}; keys = {list(z.files)}")
        p = np.asarray(z[pred_key], dtype=np.float64)
        p = p.reshape(p.shape[0], -1)
        if p.shape != target.shape:
            raise SystemExit(f"{label}: pred {p.shape} vs target {target.shape}")
        out[label] = np.linalg.norm(p - target, axis=1) / denom
    return out


# ── the decomposition ────────────────────────────────────────────────────────
def decompose(e_arm, e_ref, divisor, trims=(1, 5, 10), n_boot=10000, seed=0):
    d = e_ref - e_arm                       # + = arm better on that row
    scale = divisor if divisor else 1.0
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, d.size, size=(n_boot, d.size))
    boot = d[idx].mean(axis=1)
    order = np.argsort(-np.abs(d))
    tot = d.sum()
    out = {
        "n_rows": int(d.size),
        "nrmse_arm": float(e_arm.mean()), "nrmse_ref": float(e_ref.mean()),
        "delta_nrmse": float(d.mean()),
        "delta_skill": float(d.mean() / scale),
        "row_bootstrap_ci95_skill": [float(np.percentile(boot, 2.5) / scale),
                                     float(np.percentile(boot, 97.5) / scale)],
        "n_rows_arm_better": int((d > 0).sum()),
        "n_rows_arm_worse": int((d < 0).sum()),
        "n_rows_tied": int((d == 0).sum()),
        "median_delta_nrmse": float(np.median(d)),
        "mean_over_median": (float(d.mean() / np.median(d))
                             if np.median(d) != 0 else None),
        "topk_share_of_total_delta": {},
        "trimmed_delta_skill": {},
        "skill_divisor": divisor,
    }
    for k in trims:
        if k >= d.size:
            continue
        out["topk_share_of_total_delta"][f"top{k}"] = (
            float(d[order[:k]].sum() / tot) if tot != 0 else None)
        keep_ref = np.argsort(e_ref)[: e_ref.size - k]
        out["trimmed_delta_skill"][f"drop{k}_worst_ref_rows"] = float(
            (e_ref[keep_ref] - e_arm[keep_ref]).mean() / scale)
        out["trimmed_delta_skill"][f"drop{k}_largest_abs_delta_rows"] = float(
            d[order[k:]].mean() / scale)
    return out


def bimodal(e_arm, e_ref, thresh, divisor):
    scale = divisor if divisor else 1.0
    hard = e_ref > thresh
    d = e_ref - e_arm
    tot = d.sum()
    blk = {"threshold": float(thresh), "n_hard": int(hard.sum()),
           "n_easy": int((~hard).sum()), "frac_hard": float(hard.mean())}
    for tag, m in (("easy", ~hard), ("hard", hard)):
        if not m.any():
            blk[tag] = None
            continue
        blk[tag] = {"nrmse_ref": float(e_ref[m].mean()),
                    "nrmse_arm": float(e_arm[m].mean()),
                    "delta_skill": float(d[m].mean() / scale),
                    "share_of_total_delta": (float(d[m].sum() / tot)
                                             if tot != 0 else None)}
    blk["hard_mask"] = [int(b) for b in hard]
    return blk


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--result", help="family result JSON carrying rel_l2_per_sample")
    ap.add_argument("--pred", action="append", default=[],
                    help="LABEL=/path/preds.npz (repeatable)")
    ap.add_argument("--pred-key", default="pred_test")
    ap.add_argument("--split", default="test")
    ap.add_argument("--dataset", help="dataset name (for the copy-LF skill divisor "
                                      "and, in --pred mode, the target split)")
    ap.add_argument("--arm", required=True, help="the arm under test")
    ap.add_argument("--ref", required=True, help="the paired comparand")
    ap.add_argument("--bimodal-split", type=float, default=None,
                    help="split rows at this per-row REFERENCE error (e.g. 0.8)")
    ap.add_argument("--tau-rel", type=float, default=None,
                    help="certified min_claimable_effect, printed as a ratio")
    ap.add_argument("--boot", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--eval-dir", default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    eval_dir = pathlib.Path(a.eval_dir) if a.eval_dir else _find_eval_dir()
    nrmse_mod = _load_eval(eval_dir)
    if not a.result and not a.pred:
        raise SystemExit("need --result or at least one --pred")

    rows = {}
    if a.result:
        rows.update(rows_from_result(a.result, nrmse_mod))
    if a.pred:
        if not a.dataset:
            raise SystemExit("--pred mode needs --dataset")
        rows.update(rows_from_preds(a.pred, a.dataset, a.pred_key, a.split, eval_dir))
    for name in (a.arm, a.ref):
        if name not in rows:
            raise SystemExit(f"arm {name!r} not found; available: {sorted(rows)}")
    if rows[a.arm].shape != rows[a.ref].shape:
        raise SystemExit("arm and ref have different row counts")

    div = copylf_divisor(eval_dir, a.dataset)
    res = decompose(rows[a.arm], rows[a.ref], div, n_boot=a.boot, seed=a.seed)
    res["_meta"] = {"arm": a.arm, "ref": a.ref, "dataset": a.dataset,
                    "result": a.result, "preds": a.pred,
                    "nrmse_def_hash": nrmse_mod.NRMSE_DEF_HASH,
                    "eval_dir": str(eval_dir)}
    if a.bimodal_split is not None:
        res["bimodal"] = bimodal(rows[a.arm], rows[a.ref], a.bimodal_split, div)

    u = "skill" if div else "nRMSE"
    print(f"{a.arm} vs {a.ref}"
          + (f"  [{a.dataset}]" if a.dataset else "")
          + f"   n_rows = {res['n_rows']}")
    print(f"  nRMSE                    {res['nrmse_arm']:.6f} vs {res['nrmse_ref']:.6f}")
    print(f"  paired delta ({u:<5})      {res['delta_skill']:+.4f}"
          f"   row-bootstrap CI95 [{res['row_bootstrap_ci95_skill'][0]:+.4f}, "
          f"{res['row_bootstrap_ci95_skill'][1]:+.4f}]")
    if a.tau_rel:
        print(f"  vs certified tau_rel     {a.tau_rel:.5f}  ->  "
              f"{res['delta_skill'] / a.tau_rel:.2f}x")
    print(f"  rows better / worse      {res['n_rows_arm_better']} / "
          f"{res['n_rows_arm_worse']}   median delta {res['median_delta_nrmse']:+.6f} "
          f"(mean/median {res['mean_over_median']})")
    print(f"  concentration            " + "  ".join(
        f"{k} {v:.3f}" for k, v in res["topk_share_of_total_delta"].items()
        if v is not None))
    print(f"  trimmed delta ({u}):")
    for k, v in res["trimmed_delta_skill"].items():
        print(f"    {k:<34}{v:+.4f}")
    if "bimodal" in res:
        b = res["bimodal"]
        print(f"  two-population split at ref error > {b['threshold']}: "
              f"{b['n_hard']} hard / {b['n_easy']} easy")
        for tag in ("easy", "hard"):
            if b[tag]:
                print(f"    {tag:<5} ref {b[tag]['nrmse_ref']:.4f} -> arm "
                      f"{b[tag]['nrmse_arm']:.4f}   delta {b[tag]['delta_skill']:+.4f} "
                      f"   share of total {b[tag]['share_of_total_delta']}")
    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)) or ".", exist_ok=True)
        with open(a.out, "w") as f:
            json.dump(res, f, indent=1)
        print(f"  [json] {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
