#!/usr/bin/env python
"""Does a multi-fidelity pair/ladder row set add DATA, or only REPLICATE it?

Provenance: promoted from `s1_poisson-B3` mechanism turn 1
(`worktrees/s1_poisson/B3/scratchpad/reanalysis_turn_1.py`, probes P1/P2).

WHY THIS EXISTS
---------------
The s1 ladder families train one shared network on "all ordered fidelity pairs"
(s,t), advertised as data amplification. Once the conditions are indexed on the
TARGET fidelity -- which is the correct construction, because the row is
`(X^(t)_i, f_s, f_t) -> Y^(t)_i` -- a cross row is byte-for-byte a self row at
level t wearing a different `f_src` tag. On `ifc_poisson` the `allpairs` row set
holds 280 rows and exactly **175 distinct (X, Y) pairs**: the whole knob is a
per-level replication schedule with factor (1 + #levels below), i.e. it
downweights the level with 100 distinct conditions to 0.625x and upweights the
5-condition HF level 2.5x. Dropping the cross rows (`self_only`) moved
`ifc_poisson` seed-0 nRMSE 0.034264 -> 0.021913. Run this before attributing
anything to "extra pairs".

It also catches the opposite defect: if a family indexes cross-row conditions on
the SOURCE fidelity and the fidelity sample lists are not index-aligned, the
rows pair the wrong parameters with the wrong field.

WHAT IT REPORTS
---------------
  n_by_level                    train samples at each fidelity
  index_alignment               max|X^(s)[:n] - X^(t)[:n]| per pair; 0 <=> aligned
  rows_total / rows_distinct    distinct (X, Y) content of the row set
  per_level: rows, share, replication_factor, share_ratio_vs_self_only
  steps_per_epoch               rows / batch size (the confound that rides along)
  verdict                       REPLICATION_ONLY | ADDS_ROWS | MISMATCHED_PAIRS

READ IT AS
----------
`REPLICATION_ONLY` -> the pair set is a loss-weighting knob, not augmentation;
compare it against the `self_only` weighting before claiming a pairing result,
and remember the steps/epoch difference is confounded with the weighting.
`MISMATCHED_PAIRS` -> the cross rows train on (parameters, field) from different
samples; fix the indexing before anything else.
`share_ratio_vs_self_only` >> 1 at a level with few samples -> the arm is
upweighting the sparsest condition cloud, which is where generalization to
unseen conditions is worst (see `ladder_level_diagnostic.py`
`matched_level_predictor_on_test`).

USAGE
-----
  python tools/ladder_pair_row_audit.py --dataset ifc_poisson \
      [--modes allpairs adjacent two_level self_only] \
      [--cond-from target|source] [--batch-size 16] [--out audit.json]

Read-only, numpy only, seconds. Fields are compared flat (no interpolation),
which is what "same (X, Y) row" means for this question.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from itertools import combinations
from pathlib import Path

import numpy as np


def _factory_root() -> Path:
    env = os.environ.get("FACTORY_ROOT")
    if env:
        return Path(env)
    here = Path(__file__).resolve()
    for p in here.parents:
        cand = p / "mf_field/factory_mffp"
        if cand.is_dir():
            return cand
    raise SystemExit("cannot locate factory_mffp; set FACTORY_ROOT")


def cross_pairs(levels, mode: str):
    if mode == "self_only":
        return []
    if len(levels) < 2:
        return []
    if mode == "two_level":
        return [(levels[0], levels[-1])]
    if mode == "adjacent":
        return list(zip(levels[:-1], levels[1:]))
    return list(combinations(levels, 2))          # allpairs


def audit_mode(cond, field, levels, mode, cond_from, batch_size):
    # rows are grouped by TARGET level: the field width (n_cells) differs per
    # level, so "distinct (X, Y) row" is only meaningful within a level.
    blocks = {f: [] for f in levels}
    for f in levels:                               # self rows
        n = int(min(cond[f].shape[0], field[f].shape[0]))
        blocks[f].append({"kind": "self", "src": f, "rows": n, "X": cond[f][:n]})
    for s, t in cross_pairs(levels, mode):
        n = int(min(cond[s].shape[0], field[t].shape[0]))
        X = cond[t][:min(n, cond[t].shape[0])] if cond_from == "target" else cond[s][:n]
        n = int(X.shape[0])
        blocks[t].append({"kind": "cross", "src": s, "rows": n, "X": X})
    rows_by_level, distinct, total = {}, 0, 0
    for f in levels:
        Xs = [b["X"] for b in blocks[f]]
        Ys = [field[f][:b["rows"]].reshape(b["rows"], -1) for b in blocks[f]]
        Xl, Yl = np.concatenate(Xs, 0), np.concatenate(Ys, 0)
        rows_by_level[f] = int(Xl.shape[0])
        total += int(Xl.shape[0])
        distinct += int(np.unique(np.concatenate([Xl, Yl], 1), axis=0).shape[0])
    self_total = int(sum(min(cond[f].shape[0], field[f].shape[0]) for f in levels))
    out = {
        "mode": mode, "cond_from": cond_from,
        "cross_pairs": [[int(s), int(t)] for s, t in cross_pairs(levels, mode)],
        "rows_total": total, "rows_distinct_XY": distinct,
        "duplicate_rows": total - distinct,
        "per_level": {
            str(f): {
                "rows": int(rows_by_level.get(f, 0)),
                "share": rows_by_level.get(f, 0) / total,
                "replication_factor": rows_by_level.get(f, 0) / max(
                    1, min(cond[f].shape[0], field[f].shape[0])),
                "share_ratio_vs_self_only": (
                    (rows_by_level.get(f, 0) / total)
                    / (min(cond[f].shape[0], field[f].shape[0]) / self_total)),
            } for f in levels},
        "steps_per_epoch": int(np.ceil(total / batch_size)),
    }
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dataset", required=True, help="dataset name under data/")
    ap.add_argument("--data-root", default=None,
                    help="default: <factory_root>/data")
    ap.add_argument("--split", default="train")
    ap.add_argument("--modes", nargs="+",
                    default=["self_only", "adjacent", "allpairs", "two_level"])
    ap.add_argument("--cond-from", default="target", choices=["target", "source"],
                    help="which fidelity's condition list indexes a cross row")
    ap.add_argument("--batch-size", type=int, default=16)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    froot = _factory_root()
    sys.path.insert(0, str(froot))
    from data_adapters import load_mf_dataset          # noqa: E402

    ddir = Path(a.data_root or (froot / "data")) / a.dataset
    tr = load_mf_dataset(ddir, a.split)
    levels = sorted(int(f) for f in tr["fids"])
    cond = {f: np.asarray(tr["cond_by_fid"][f], np.float64) for f in levels}
    field = {f: np.asarray(tr["field_by_fid"][f], np.float64) for f in levels}

    align = {}
    for s, t in combinations(levels, 2):
        n = min(cond[s].shape[0], cond[t].shape[0])
        align[f"{s}->{t}"] = float(np.abs(cond[s][:n] - cond[t][:n]).max()) if n else float("nan")
    aligned = all(v == 0.0 for v in align.values()) if align else True

    res = {
        "dataset": a.dataset, "split": a.split,
        "n_by_level": {str(f): int(cond[f].shape[0]) for f in levels},
        "index_alignment_max_abs_diff": align,
        "cond_lists_index_aligned": bool(aligned),
        "cond_from": a.cond_from,
        "modes": {},
    }
    for m in a.modes:
        r = audit_mode(cond, field, levels, m, a.cond_from, a.batch_size)
        n_cross_rows = r["rows_total"] - sum(
            int(min(cond[f].shape[0], field[f].shape[0])) for f in levels)
        if not r["cross_pairs"]:
            r["verdict"] = "SELF_ROWS_ONLY"
        elif a.cond_from == "source" and not aligned:
            r["verdict"] = "MISMATCHED_PAIRS"
        elif r["duplicate_rows"] >= n_cross_rows > 0:
            r["verdict"] = "REPLICATION_ONLY"
        else:
            r["verdict"] = "ADDS_ROWS"
        res["modes"][m] = r

    print(f"# {a.dataset} ({a.split})  levels={levels}  "
          f"n={[int(cond[f].shape[0]) for f in levels]}  "
          f"index_aligned={aligned}  cond_from={a.cond_from}")
    print(f"{'mode':<12}{'rows':>7}{'distinct':>10}{'dupes':>7}  "
          f"{'share ratio vs self_only (by level)':<44}{'steps/ep':>9}  verdict")
    for m, r in res["modes"].items():
        sr = " ".join(f"{k}:{v['share_ratio_vs_self_only']:.2f}"
                      for k, v in r["per_level"].items())
        print(f"{m:<12}{r['rows_total']:>7}{r['rows_distinct_XY']:>10}"
              f"{r['duplicate_rows']:>7}  {sr:<44}{r['steps_per_epoch']:>9}  {r['verdict']}")

    if a.out:
        Path(a.out).write_text(json.dumps(res, indent=1))
        print(f"[wrote] {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
