#!/usr/bin/env python
"""Are a dataset's fidelity rungs actually PAIRED by condition, or only by ROW
INDEX? — the training-free pre-flight for any design that builds an `LF↑` field
for an HF row (copy-LF reference, auxiliary LF target, LF teacher input,
residual `HF − LF` target, distillation pair).

WHY THIS EXISTS
---------------
`round2/eval/panel_data.py::copylf_prediction` — and every family that vendors
it — pairs the rungs with

    lf = lf[:n_hf]

i.e. it assumes rung `s` row `i` and rung `t` row `i` were solved at the SAME
parameter vector. That assumption is true for the round's five aligned/nested
`npz` datasets and FALSE for the `ifc_raw` ladder, where each rung carries its
own independent condition draw (`ifc_poisson`: 100/50/20/5 rows at rungs
8/16/32/64). r2s4-B2 shipped an ifc arm whose LF target and LF teacher input
were coarse fields belonging to unrelated parameter vectors: max abs condition
mismatch 0.6819, mean paired distance 0.7435 against a mean nearest distance of
0.2703, and 0 % of rows paired to their nearest condition. The card's own seam
check (`max_abs_diff = 0.0` vs the eval layer) PASSED, because the vendored copy
and the eval original share the same wrong assumption — a seam check between two
implementations of one assumption certifies nothing. This tool is the missing
check: it interrogates the DATA, not a second implementation.

It also reports the flip side, which is the same measurement read the other way:
LF rows sitting at conditions the HF rung does not cover are not a defect but a
SUPPLY of extra design rows (`ifc_poisson`: 170 of them; 0 on every aligned
dataset). A truncating pairing rule throws that supply away — on ifc_poisson it
keeps 5 of 170 rows.

Related, deliberately not duplicated:
  * `ladder_pair_row_audit.py` (s1_poisson-B3) — asks whether an all-pairs ROW
    SET replicates data; reports `index_alignment_max_abs_diff` as a side
    quantity and only flags `MISMATCHED_PAIRS` under `--cond-from source`. This
    tool is the standalone pairing pre-flight: nearest-neighbour geometry, the
    per-rung truncation semantics, and the disjoint-condition supply count.
  * r2s2_stacked-B1's in-job `V6b` gate — the same question answered INSIDE a
    training job (it sets `paired_real_lf` / `arm_semantics_degraded` and falls
    back to a pseudo-LF path). Run this BEFORE the build so the card knows which
    datasets can carry a paired-LF arm at all; use V6b-style in-job gating to
    degrade gracefully where this tool says MISPAIRED.

WHAT IT REPORTS  (per dataset, per LF rung, on the chosen split)
---------------------------------------------------------------
  n_hf, n_lf, n_paired               rows the `lf[:n_hf]` rule actually pairs
  max_abs_cond_mismatch_paired       0.0 ⟺ index-aligned
  paired_cond_distance_mean          ‖c_hf,i − c_lf,i‖ under the truncation rule
  nearest_cond_distance_mean         the best any pairing could do
  paired_row_is_nearest_frac         1.0 ⟺ the truncation rule is optimal
  lf_rows_at_conditions_without_hf   disjoint-condition SUPPLY (exact match)
  lf_rows_kept_by_truncation         how many of n_lf survive `lf[:n_hf]`
  verdict  PAIRED_ALIGNED | MISPAIRED | DISJOINT_SUPPLY_TRUNCATED | TOO_FEW_ROWS

READ IT AS
----------
`PAIRED_ALIGNED`  → any LF↑-per-HF-row construction is semantically valid here.
`MISPAIRED`       → every `hf − lf`, LF-target, LF-teacher and copy-LF number on
                    this dataset is computed against the wrong sample. Do not
                    read such an arm as evidence about the value of LF in either
                    direction; either pair by nearest condition, or gate the arm
                    off (V6b style), or drop the dataset from the contrast.
`DISJOINT_SUPPLY_TRUNCATED` → the rungs carry conditions the HF rung does not,
                    and the truncation rule discards them. That supply is the
                    only channel through which LF can add DESIGN ROWS rather
                    than a smoothed copy of the HF target (r2s3-B2 measured
                    A0_nolf 8.1344 → A2_lf_cov_null 3.4550 skill, +4.68, on
                    ifc_poisson at N_hf = 5, single seed); a card that
                    wants it must index rows by rung, not by `[:n_hf]`.

USAGE
-----
    source "$PROJECT_ROOT/.venv/bin/activate"
    python tools/ladder_pair_alignment_audit.py --datasets PANEL \
        --out /path/pair_audit.json
    python tools/ladder_pair_alignment_audit.py --datasets ifc_poisson \
        --split train --fail-on mispaired      # exit 2 ⇒ usable as a build gate

Read-only, numpy only, seconds. Reads condition vectors only — no fields, no
model, no test-side LF.

Provenance: promoted from `r2s4_diag-B2` mechanism turn 2 (block F of
`worktrees/r2s4_diag/B2/scratchpad/reanalysis_turn_2.py`, finding T2-F6) plus
the supply counter from block E (T2-F7).
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
sys.path.insert(0, str(PATHS["factory_root"]))
from data_adapters.loaders import load_mf_dataset          # noqa: E402


def audit_rung(C_hf, C_lf, std, tol):
    """Pairing geometry of the `lf[:n_hf]` truncation rule for one LF rung."""
    n_hf, n_lf = C_hf.shape[0], C_lf.shape[0]
    m = int(min(n_hf, n_lf))
    out = {"n_hf": int(n_hf), "n_lf": int(n_lf), "n_paired": m,
           "lf_rows_kept_by_truncation": m,
           "lf_rows_discarded_by_truncation": int(n_lf - m)}
    if m == 0:
        out["verdict"] = "TOO_FEW_ROWS"
        return out
    A, B = C_hf[:m], C_lf[:m]
    mism = float(np.abs(A - B).max())
    d_pair = np.linalg.norm(A - B, axis=1)
    d_all = np.linalg.norm(A[:, None, :] - C_lf[None, :, :], axis=2)
    nearest = d_all.argmin(1)
    d_pair_s = np.linalg.norm((A - B) / std, axis=1)
    d_all_s = np.linalg.norm((A[:, None, :] - C_lf[None, :, :]) / std, axis=2)
    # disjoint-condition supply: LF rows whose condition matches no HF row
    d_lf_to_hf = np.linalg.norm(
        C_lf[:, None, :] - C_hf[None, :, :], axis=2).min(1)
    out.update({
        "max_abs_cond_mismatch_paired": mism,
        "index_aligned": bool(mism <= tol),
        "paired_cond_distance_mean": float(d_pair.mean()),
        "paired_cond_distance_max": float(d_pair.max()),
        "nearest_cond_distance_mean": float(d_all.min(1).mean()),
        "paired_row_is_nearest_frac": float((nearest == np.arange(m)).mean()),
        "paired_cond_distance_mean_standardised": float(d_pair_s.mean()),
        "nearest_cond_distance_mean_standardised": float(d_all_s.min(1).mean()),
        "lf_rows_at_conditions_without_hf": int((d_lf_to_hf > tol).sum()),
    })
    if out["index_aligned"]:
        out["verdict"] = "PAIRED_ALIGNED"
    elif out["paired_row_is_nearest_frac"] >= 1.0:
        # not index-aligned but the truncation happens to select the nearest row
        out["verdict"] = "PAIRED_ALIGNED"
    elif out["lf_rows_at_conditions_without_hf"] >= max(1, n_lf - m):
        out["verdict"] = "DISJOINT_SUPPLY_TRUNCATED"
    else:
        out["verdict"] = "MISPAIRED"
    if out["verdict"] == "DISJOINT_SUPPLY_TRUNCATED" and \
            out["paired_row_is_nearest_frac"] < 0.5:
        out["also"] = "MISPAIRED"
    return out


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--datasets", required=True,
                    help="comma list, or PANEL / GUARD from project.yaml")
    ap.add_argument("--split", default="train")
    ap.add_argument("--data-root", default=str(PATHS["stripped_data_root"]))
    ap.add_argument("--tol", type=float, default=0.0,
                    help="condition-equality tolerance (default exact)")
    ap.add_argument("--out", default=None)
    ap.add_argument("--fail-on", default=None,
                    choices=["mispaired", "not_aligned"],
                    help="exit 2 if any dataset trips this (build-gate use)")
    a = ap.parse_args()

    if a.datasets.upper() == "PANEL":
        names = list(CFG["panel"])
    elif a.datasets.upper() == "GUARD":
        names = list(CFG["guard_set"])
    else:
        names = [s for s in a.datasets.split(",") if s]
    data_root = Path(a.data_root)

    res = {"_tool": "ladder_pair_alignment_audit", "_split": a.split,
           "_data_root": str(data_root), "_tol": a.tol,
           "_pairing_rule_audited": "lf = lf[:n_hf] (eval/panel_data.py::copylf_prediction)",
           "datasets": {}}
    tripped = []
    print(f"{'dataset':<32}{'rung':>6}{'n_hf':>6}{'n_lf':>6}"
          f"{'max|dc|':>10}{'d_pair':>9}{'d_near':>9}{'near%':>7}"
          f"{'disjoint':>9}  verdict")
    for name in names:
        d = load_mf_dataset(data_root / name, a.split)
        hf_fid = int(d["hf_fid"])
        C_hf = np.asarray(d["cond_by_fid"][hf_fid], dtype=np.float64)
        std = C_hf.std(0)
        std = np.where(std > 0, std, 1.0)
        rungs = {}
        for f in sorted(int(x) for x in d["lf_fids"]):
            C_lf = np.asarray(d["cond_by_fid"][f], dtype=np.float64)
            r = audit_rung(C_hf, C_lf, std, a.tol)
            rungs[str(f)] = r
            print(f"{name:<32}{f:>6}{r['n_hf']:>6}{r['n_lf']:>6}"
                  f"{r.get('max_abs_cond_mismatch_paired', float('nan')):>10.4f}"
                  f"{r.get('paired_cond_distance_mean', float('nan')):>9.4f}"
                  f"{r.get('nearest_cond_distance_mean', float('nan')):>9.4f}"
                  f"{100 * r.get('paired_row_is_nearest_frac', float('nan')):>6.0f}%"
                  f"{r.get('lf_rows_at_conditions_without_hf', -1):>9}"
                  f"  {r['verdict']}"
                  + (f" (+{r['also']})" if "also" in r else ""))
        verdicts = {r["verdict"] for r in rungs.values()} | {
            r["also"] for r in rungs.values() if "also" in r}
        ds_verdict = ("MISPAIRED" if "MISPAIRED" in verdicts else
                      "DISJOINT_SUPPLY_TRUNCATED"
                      if "DISJOINT_SUPPLY_TRUNCATED" in verdicts else
                      "TOO_FEW_ROWS" if "TOO_FEW_ROWS" in verdicts else
                      "PAIRED_ALIGNED")
        res["datasets"][name] = {
            "hf_fid": hf_fid, "cond_dim": int(C_hf.shape[1]),
            "rows_by_fid": {str(int(f)): int(np.asarray(d["cond_by_fid"][f]).shape[0])
                            for f in sorted(int(x) for x in d["cond_by_fid"])},
            "lf_rows_at_conditions_without_hf_total": int(sum(
                r.get("lf_rows_at_conditions_without_hf", 0) for r in rungs.values())),
            "rungs": rungs, "verdict": ds_verdict,
        }
        if a.fail_on == "mispaired" and ds_verdict == "MISPAIRED":
            tripped.append(name)
        if a.fail_on == "not_aligned" and ds_verdict != "PAIRED_ALIGNED":
            tripped.append(name)

    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(json.dumps(res, indent=1))
        print("[wrote]", a.out)
    if tripped:
        print(f"[FAIL] --fail-on {a.fail_on} tripped on: {', '.join(tripped)}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
