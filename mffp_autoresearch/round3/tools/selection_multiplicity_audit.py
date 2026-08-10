#!/usr/bin/env python
"""Audit of a permutation/p-value-calibrated FEATURE-SELECTION rule.

WHAT IT MEASURES

Given any result JSON that emits, per candidate (direction / feature / mode),
(i) a permutation p-value and (ii) an effect size (e.g. an OOF R^2), this tool
reports what the selected set would have been under a family of admission
rules, and it checks two things a card can otherwise ship broken:

  1. RESOLUTION FLOOR.  A conservative permutation p-value
     `p = (1 + #{null >= obs}) / (1 + B)` cannot go below `1/(1+B)`.  If the
     multiplicity-corrected threshold you intend (Bonferroni `alpha/m`, or the
     smallest Holm step) is BELOW that, family-wise control is arithmetically
     UNREACHABLE from your own null and every candidate is rejected -- the rule
     silently degenerates to whatever your SELECT_MIN fallback is.  The tool
     prints the minimum B that makes your threshold reachable
     (`B >= m/alpha - 1`).

  2. SIGNIFICANCE vs EFFECT SIZE.  A permutation null asks "is this candidate
     predictable AT ALL"; a threshold like `R^2 >= tau` asks "is it predictable
     ENOUGH TO BE WORTH A SLOT".  At a few hundred rows those differ by orders
     of magnitude.  The tool reports the selected-set size under the raw
     p-threshold, Benjamini-Hochberg FDR, Holm and Bonferroni FWER, and under
     `p <= alpha AND effect >= t` for a ladder of `t`, plus set-equality
     against any number of REFERENCE sets you name -- so "would a correctly
     sized rule have changed anything?" is answered without retraining.

WHEN TO RUN IT

Before shipping any card whose selection rule is calibrated by a permutation
null or any p-value, and in re-analysis of one that was. It needs no model, no
data and no GPU -- only the emitted per-candidate tables.

PROVENANCE: card `r3s1_factorised-B2`, mechanism turn 1. There, B = 200 put the
Bonferroni threshold (0.05/51 = 9.80e-4) BELOW the estimator's own resolution
(1/201 = 4.975e-3), so FWER control was impossible; and the shipped criterion
turned out to admit a strict SUPERSET of the effect-size rule on all 9
(cell, seed), i.e. it could only ever add sub-threshold candidates.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def dig(obj, dotted: str):
    """`a.b.0.c` -> obj['a']['b'][0]['c']."""
    cur = obj
    for part in dotted.split("."):
        cur = cur[int(part)] if isinstance(cur, list) else cur[part]
    return cur


def bh(p, q):
    p = np.asarray(p, dtype=np.float64)
    m = len(p)
    order = np.argsort(p)
    ok = p[order] <= q * np.arange(1, m + 1) / m
    if not ok.any():
        return set()
    return set(int(i) for i in order[: int(np.max(np.nonzero(ok)[0])) + 1])


def holm(p, alpha):
    p = np.asarray(p, dtype=np.float64)
    m = len(p)
    order = np.argsort(p)
    thr = alpha / (m - np.arange(m))
    sel = set()
    for i in range(m):
        if p[order[i]] <= thr[i]:
            sel.add(int(order[i]))
        else:
            break
    return sel


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--result", action="append", required=True, metavar="LABEL=/path.json",
                    help="repeatable; one artifact per (cell, seed)")
    ap.add_argument("--p-key", required=True,
                    help="dotted path to the per-candidate p-value list")
    ap.add_argument("--effect-key", required=True,
                    help="dotted path to the per-candidate effect-size list")
    ap.add_argument("--b-key", default=None,
                    help="dotted path to the number of permutation draws B "
                         "(else use --b)")
    ap.add_argument("--b", type=int, default=None)
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--fdr-q", type=float, default=[0.05, 0.01], nargs="+")
    ap.add_argument("--effect-ladder", type=float, nargs="+",
                    default=[0.01, 0.05, 0.10])
    ap.add_argument("--select-min", type=int, default=1,
                    help="fallback set size when a rule admits nothing "
                         "(0 disables the fallback)")
    ap.add_argument("--reference-set-key", action="append", default=[],
                    metavar="NAME=dotted.path",
                    help="repeatable; a shipped selected-set to compare against")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    rows, out = [], {"rules": {}, "per_artifact": []}
    for spec in a.result:
        if "=" not in spec:
            raise SystemExit(f"--result needs LABEL=path, got {spec!r}")
        lab, path = spec.split("=", 1)
        j = json.loads(Path(path).read_text())
        p = np.asarray(dig(j, a.p_key), dtype=np.float64)
        eff = np.asarray(dig(j, a.effect_key), dtype=np.float64)
        if len(p) != len(eff):
            raise SystemExit(f"{lab}: {len(p)} p-values vs {len(eff)} effect sizes")
        B = int(dig(j, a.b_key)) if a.b_key else a.b
        if B is None:
            raise SystemExit("give --b-key or --b")
        refs = {}
        for rspec in a.reference_set_key:
            nm, dk = rspec.split("=", 1)
            refs[nm] = set(int(x) for x in dig(j, dk))

        variants = {f"p<={a.alpha}": set(np.nonzero(p <= a.alpha)[0].tolist())}
        for q in a.fdr_q:
            variants[f"BH_FDR_q={q}"] = bh(p, q)
        variants[f"Holm_FWER_{a.alpha}"] = holm(p, a.alpha)
        variants[f"Bonferroni_FWER_{a.alpha}"] = set(
            np.nonzero(p <= a.alpha / len(p))[0].tolist())
        for t in a.effect_ladder:
            variants[f"p<={a.alpha}_AND_effect>={t}"] = {
                int(i) for i in np.nonzero(p <= a.alpha)[0] if eff[i] >= t}
        if a.select_min > 0:
            for k, v in variants.items():
                if not v:
                    variants[k] = set(int(i) for i in np.argsort(-eff)[: a.select_min])

        rec = {"label": lab, "path": path, "m": int(len(p)), "B": B,
               "n": {k: len(v) for k, v in variants.items()},
               "sets": {k: sorted(int(x) for x in v) for k, v in variants.items()},
               "vs_reference": {rn: {k: (v == rs) for k, v in variants.items()}
                                for rn, rs in refs.items()},
               "reference_n": {rn: len(rs) for rn, rs in refs.items()}}
        rows.append(rec)
        out["per_artifact"].append(rec)

    m = rows[0]["m"]
    B = rows[0]["B"]
    p_min = 1.0 / (1.0 + B)
    bonf = a.alpha / m
    out["resolution"] = {"B": B, "m": m, "p_min": p_min, "bonferroni_threshold": bonf,
                         "bonferroni_reachable": bool(bonf >= p_min),
                         "min_B_for_bonferroni": int(np.ceil(m / a.alpha)) - 1}
    print(f"RESOLUTION: B = {B}, m = {m} candidates, alpha = {a.alpha}")
    print(f"  conservative permutation p_min = 1/(1+B) = {p_min:.6f}")
    print(f"  Bonferroni threshold alpha/m  = {bonf:.6f}  -> "
          f"{'REACHABLE' if bonf >= p_min else '*** UNREACHABLE: FWER control is impossible from this null ***'}")
    print(f"  minimum B for a reachable Bonferroni threshold: B >= m/alpha - 1 = "
          f"{out['resolution']['min_B_for_bonferroni']}")

    keys = list(rows[0]["n"].keys())
    print(f"\nSELECTED-SET SIZE by rule ({len(rows)} artifacts):")
    w = max(len(k) for k in keys) + 2
    print("  " + " " * w + "  ".join(f"{r['label'][:10]:>10s}" for r in rows))
    for k in keys:
        print(f"  {k:{w}s}" + "  ".join(f"{r['n'][k]:>10d}" for r in rows))
        out["rules"][k] = {"n": [r["n"][k] for r in rows]}
    for rn in rows[0]["reference_n"]:
        print(f"  {'[ref] ' + rn:{w}s}" + "  ".join(f"{r['reference_n'][rn]:>10d}" for r in rows))
        for k in keys:
            eq = sum(1 for r in rows if r["vs_reference"][rn][k])
            out["rules"][k].setdefault("equals_reference", {})[rn] = eq
        print(f"    set-equality vs {rn}: " + ", ".join(
            f"{k} {sum(1 for r in rows if r['vs_reference'][rn][k])}/{len(rows)}" for k in keys))

    if a.out:
        Path(a.out).write_text(json.dumps(out, indent=1, default=float))
        print(f"\n  -> {a.out}")


if __name__ == "__main__":
    main()
