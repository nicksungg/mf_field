#!/usr/bin/env python
"""Does this LF pool actually ADD DESIGN ROWS, or only replicate the HF conditions?

Provenance: promoted from `r2s3_lf_train_signal-B2` mechanism turn 3
(`worktrees/r2s3_lf_train_signal/B2/scratchpad/reanalysis_turn_3b.py` block (1) +
block (4), and `.../reanalysis_turn_3.py`'s covered-condition discrepancy block).

WHY THIS EXISTS
---------------
Before you spend an LF budget, decide WHERE to spend it. With N_hf HF training
rows and a d-dimensional condition vector, the augmented design `[X, 1]` has
rank r and null dimension m = d + 1 - r; every affine functional in that null
space is invisible to the training rows no matter how the model is built. LF
rows can only reduce m by adding NEW CONDITIONS: LF rows at conditions that
already carry an HF row leave the design's rank, null dimension and singular
values BIT-IDENTICAL (r2s3-B2 turn 3 T3.7 verified exactly this), so a paired
LF pool has zero access to the deficient subspace.

Worse, it can hurt. Where the coarse solve is a genuinely DIFFERENT field rather
than a blurred one, LF rows at the covered conditions are a contradictory target
on precisely the rows the HF loss supervises: on `sharp__cahn_hilliard` rung 1
the lifted LF is rel-L2 0.398 from HF at the 5 covered conditions (one condition
at 1.398 — a different phase-separation morphology), and the paired-LF arm
scored 0.83 skill units WORSE than training with no LF at all.

This tool reports, per LF rung, training-free and in seconds:
  - rank / m / singular values of `[X, 1]` for the HF training rows,
    for the PAIRED pool (LF rows at exactly those conditions), for the FULL LF
    pool, and for the UNION (HF rows + full LF pool);
  - covered vs uncovered condition counts (the disjoint SUPPLY);
  - `m_reduction_paired` and `m_reduction_full` — the identifiability the pool
    actually buys;
  - with `--fields`: the lifted-LF-vs-HF rel-L2 and cosine at the covered
    conditions, i.e. how contradictory a paired target would be.

Verdict per rung: `FULL_POOL_COMPLETES` (full pool removes deficiency the paired
pool cannot) / `PAIRED_POOL_ADDS_NO_RANK` / `NO_DEFICIT_TO_FIX` /
`POOL_LEAVES_DEFICIT`, plus `CONTRADICTORY_PAIRED_TARGET` when `--fields` shows
the covered-condition discrepancy above `--contradiction_tol` (default 0.2).

RELATION TO THE NEIGHBOURING TOOLS (run them together, they are four axes)
--------------------------------------------------------------------------
`ladder_pair_alignment_audit.py` (r2s4-B2) asks whether the rungs are paired by
CONDITION or only by ROW INDEX, and counts the disjoint supply a `lf[:n_hf]`
truncation discards. This tool takes the pairing as given and asks the next
question — whether the pool changes the AFFINE IDENTIFIABILITY of the design at
all. `affine_ladder_voi.py` (r2s3-B1) prices the SAME deficiency in skill units
with the fields (how much law energy lives in the null space, what the LF rungs
recover, the HF-only information limit); this one is the cheap condition-only
pre-flight that says whether that analysis can help before any field is loaded.
`condition_identifiable_rank.py` (r2s1-B1) is the field-basis axis (which POD
modes the condition can predict at all) and `reachable_set_rank_audit.py`
(r2s2-B1) the model-output axis (what a trained net's output family spans).

USAGE
-----
  source "$PROJECT_ROOT/.venv/bin/activate"
  # HF design = the 5 rows an arm actually trained on, read from its preds dump
  python tools/design_coverage_audit.py --dataset sharp__cahn_hilliard \
      --hf_rows_from <outputs>/results_ch_A3_s0/<family>/<ds>_e200_s0_preds.npz \
      --fields --out coverage_ch.json
  # or an explicit subset, or the whole HF train split (default)
  python tools/design_coverage_audit.py --dataset ifc_poisson --hf_rows 0,7,12,31,44

Pure numpy (torch only inside the shared rung loader, and only with `--fields`).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROUND_ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROUND_ROOT / "eval"))
from affine_ladder_voi import load_rungs, _factory_import, CFG, ROOT  # noqa: E402


def load_conditions_only(dataset, root_key):
    """Condition vectors + grids per rung — the cheap path when --fields is off."""
    load_mf_dataset, resolve_grid = _factory_import()
    ddir = ROOT / CFG["paths"][root_key] / dataset
    if not ddir.exists():
        raise SystemExit(f"dataset dir not found: {ddir}")
    train = load_mf_dataset(ddir, "train")
    hf = int(train["hf_fid"])
    rung = {}
    for f in sorted(int(x) for x in train["fids"]):
        g = resolve_grid(dataset, int(train["n_cells_by_fid"][f]))
        rung[f] = {"X": np.asarray(train["cond_by_fid"][f], dtype=np.float64),
                   "grid": [int(g[0]), int(g[1])]}
    return {"rung": rung, "hf": hf}


def aug(X):
    X = np.asarray(X, dtype=np.float64)
    return np.concatenate([X, np.ones((X.shape[0], 1))], axis=1)


def rank_report(X, label, tol):
    A = aug(X)
    s = np.linalg.svd(A, compute_uv=False) if A.shape[0] else np.zeros(0)
    r = int((s > tol * max(float(s[0]) if s.size else 0.0, 1e-300)).sum())
    return {"label": label, "n_rows": int(A.shape[0]), "n_cols": int(A.shape[1]),
            "numerical_rank": r, "m_null_dim": int(A.shape[1] - r),
            "singular_values_head": [float(x) for x in s[:8]]}


def rel(a, b):
    return float(np.linalg.norm(a - b) / max(np.linalg.norm(b), 1e-300))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--hf_rows", default=None,
                    help="comma-separated row indices into the HF train rung "
                         "(default: all HF train rows)")
    ap.add_argument("--hf_rows_from", default=None,
                    help="path[:key] of an int array of HF train row indices "
                         "(default key selected_train_rows; e.g. an arm's preds npz)")
    ap.add_argument("--fields", action="store_true",
                    help="also load the fields and measure the lifted-LF-vs-HF "
                         "discrepancy at the covered conditions")
    ap.add_argument("--max_covered_scored", type=int, default=25,
                    help="cap on covered conditions scored under --fields")
    ap.add_argument("--contradiction_tol", type=float, default=0.2,
                    help="mean rel-L2 above which a paired LF target is flagged")
    ap.add_argument("--match_decimals", type=int, default=12,
                    help="rounding used to decide two condition rows are the same")
    ap.add_argument("--rank_tol", type=float, default=1e-10)
    ap.add_argument("--data_root", default="stripped", choices=["stripped", "orig"])
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    t0 = time.time()
    root_key = "stripped_data_root" if args.data_root == "stripped" else "data_root"
    data = (load_rungs(args.dataset, root_key, max_test=1) if args.fields
            else load_conditions_only(args.dataset, root_key))
    hf = data["hf"]
    X_hf_all = data["rung"][hf]["X"]

    if args.hf_rows_from:
        spec, key = args.hf_rows_from, "selected_train_rows"
        if not Path(spec).exists() and ":" in spec:
            spec, key = spec.rsplit(":", 1)
        z = np.load(spec)
        rows = np.asarray(z[key] if hasattr(z, "files") else z, dtype=int)
        src = f"{spec}:{key}"
    elif args.hf_rows:
        rows = np.array([int(v) for v in args.hf_rows.split(",")], dtype=int)
        src = f"--hf_rows {args.hf_rows}"
    else:
        rows = np.arange(X_hf_all.shape[0], dtype=int)
        src = "all HF train rows"
    X_hf = X_hf_all[rows]

    out = {"_tool": "design_coverage_audit.py", "dataset": args.dataset,
           "_data_root": args.data_root, "hf_rows_source": src,
           "n_hf_train_rows_used": int(rows.size),
           "n_hf_train_rows_available": int(X_hf_all.shape[0]),
           "cond_dim": int(X_hf_all.shape[1]), "hf_fid": int(hf),
           "hf_design": rank_report(X_hf, f"HF train rows (N_hf={rows.size})",
                                    args.rank_tol)}
    m_hf = out["hf_design"]["m_null_dim"]

    def keyset(X):
        return {tuple(np.round(r, args.match_decimals)) for r in X}

    hf_keys = keyset(X_hf)
    rungs = {}
    for f in sorted(int(x) for x in data["rung"] if int(x) != hf):
        Xf = data["rung"][f]["X"]
        j_of_key = {tuple(np.round(r, args.match_decimals)): i for i, r in enumerate(Xf)}
        paired_idx = np.array([j_of_key[k] for k in hf_keys if k in j_of_key], dtype=int)
        cov = {
            "grid": data["rung"][f]["grid"], "n_lf_rows": int(Xf.shape[0]),
            "n_lf_rows_at_hf_covered_conditions": int(paired_idx.size),
            "n_lf_rows_at_conditions_without_an_hf_row": int(
                sum(1 for r in Xf
                    if tuple(np.round(r, args.match_decimals)) not in hf_keys)),
            "n_hf_conditions_covered_by_this_rung": int(
                sum(1 for k in hf_keys if k in j_of_key)),
            "paired_pool": rank_report(Xf[paired_idx] if paired_idx.size else Xf[:0],
                                       f"paired pool, rung {f}", args.rank_tol),
            "full_pool": rank_report(Xf, f"full pool, rung {f}", args.rank_tol),
            "union_hf_plus_full_pool": rank_report(
                np.concatenate([X_hf, Xf], axis=0), f"HF + full pool, rung {f}",
                args.rank_tol),
        }
        cov["m_reduction_paired"] = m_hf - rank_report(
            np.concatenate([X_hf, Xf[paired_idx]], axis=0) if paired_idx.size else X_hf,
            "u", args.rank_tol)["m_null_dim"]
        cov["m_reduction_full"] = m_hf - cov["union_hf_plus_full_pool"]["m_null_dim"]
        cov["paired_pool_singular_values_identical_to_hf"] = bool(
            paired_idx.size == rows.size
            and np.allclose(cov["paired_pool"]["singular_values_head"],
                            out["hf_design"]["singular_values_head"],
                            rtol=0, atol=1e-12))

        if args.fields and paired_idx.size:
            n = min(int(paired_idx.size), args.max_covered_scored)
            hf_idx = np.array([rows[i] for i, r in enumerate(X_hf)
                               if tuple(np.round(r, args.match_decimals)) in j_of_key],
                              dtype=int)[:n]
            lf_idx = np.array([j_of_key[tuple(np.round(X_hf_all[i], args.match_decimals))]
                               for i in hf_idx], dtype=int)
            Yup = data["rung"][f]["Y_up"][lf_idx]
            Yhf = data["rung"][hf]["Y_native"][hf_idx]
            per = [rel(Yup[i], Yhf[i]) for i in range(hf_idx.size)]
            cos = [float(Yup[i] @ Yhf[i]
                         / max(np.linalg.norm(Yup[i]) * np.linalg.norm(Yhf[i]), 1e-300))
                   for i in range(hf_idx.size)]
            cov["covered_condition_discrepancy"] = {
                "n_scored": int(hf_idx.size),
                "rel_l2_lifted_lf_vs_hf": per, "mean_rel_l2": float(np.mean(per)),
                "max_rel_l2": float(np.max(per)), "mean_cos": float(np.mean(cos))}

        if m_hf == 0:
            v = "NO_DEFICIT_TO_FIX"
        elif cov["m_reduction_full"] > cov["m_reduction_paired"]:
            v = ("FULL_POOL_COMPLETES" if cov["union_hf_plus_full_pool"]["m_null_dim"] == 0
                 else "FULL_POOL_REDUCES_DEFICIT")
        elif cov["m_reduction_paired"] == 0:
            v = "PAIRED_POOL_ADDS_NO_RANK"
        else:
            v = "POOL_LEAVES_DEFICIT"
        flags = [v]
        if (cov.get("covered_condition_discrepancy", {}).get("mean_rel_l2", 0.0)
                > args.contradiction_tol):
            flags.append("CONTRADICTORY_PAIRED_TARGET")
        if cov["n_lf_rows_at_hf_covered_conditions"] == 0:
            flags.append("DISJOINT_DESIGN_NO_COVERED_CONDITIONS")
        cov["verdict"] = flags
        rungs[str(f)] = cov

    out["rungs"] = rungs
    out["_wall_seconds"] = round(time.time() - t0, 1)
    txt = json.dumps(out, indent=1)
    if args.out:
        Path(args.out).write_text(txt)
        print(f"wrote {args.out}", flush=True)
    print(f"[{args.dataset}] HF design rank {out['hf_design']['numerical_rank']}"
          f"/{out['hf_design']['n_cols']} m={m_hf} (N_hf={rows.size})", flush=True)
    for f, c in rungs.items():
        d = c.get("covered_condition_discrepancy", {}).get("mean_rel_l2")
        print(f"  rung {f}: covered {c['n_hf_conditions_covered_by_this_rung']}"
              f"/{rows.size}, uncovered LF rows "
              f"{c['n_lf_rows_at_conditions_without_an_hf_row']}, "
              f"m_reduction paired {c['m_reduction_paired']} vs full "
              f"{c['m_reduction_full']}"
              + (f", covered rel-L2 {d:.4f}" if d is not None else "")
              + f"  {'+'.join(c['verdict'])}", flush=True)
    if not args.out:
        print(txt)


if __name__ == "__main__":
    main()
