#!/usr/bin/env python
"""split_transfer_licence_audit — is a held-out-split LICENCE failure a real
transfer-geometry difference, or an artefact of the licence statistic?

Many round-3 cards measure something on a held-out slice of TRAIN (because
immutable #9 forbids exposing test LF) and then need a licence clause saying
"this held-out measurement transfers to test". The usual clause has two terms:

  (i)  a TOLERANCE term on a difference-in-differences,
           g = log( nRMSE_H(A) / nRMSE_test(A) ) - log( nRMSE_H(B) / nRMSE_test(B) )
             = log( r_H / r_test ),   r = nRMSE(A)/nRMSE(B)
  (ii) a RANK-AGREEMENT term ("A and B rank the same way on both splits").

Both terms fail in ways that are easy to misread, and this tool separates them:

  * TOLERANCE. `g` is small on a passing cell not because H and test agree but
    because the two arms are displaced by the SAME amount and it cancels. The
    tool splits `g` into its two halves a = log(A_H/A_test), b = log(B_H/B_test),
    reports corr(a,b), and separates BIAS (mean g -- a systematic transfer
    difference that more legs will not remove) from SCATTER (sd g -- estimator
    noise). It then prices the sample-size explanation directly: sd(g) should
    scale as 1/sqrt(|H|), so a cell measured at large |H| can be projected down
    to a small-|H| cell's own held-out size and its zero-bias fail rate compared
    with what the small cell actually did.

  * RANK. A rank clause with no dead-band fires on numerical TIES. That is
    self-defeating whenever the card's own thesis is "arm A and its ablation are
    the same", so the tool reports every rank flip's margin and re-runs the
    verdict under a relative dead-band.

Optionally attributes each leg's statistic to the IDENTITY of its held-out rows
(`--row-key`), which is decisive when the held-out population is a handful of
rows (N_hf = 5 cells: one row can move a cell-level mean by more than the seed
does), including leave-one-ROW-out.

Input: any per-cell diagnostic JSON that dumps a leg population with a held-out
and a test nRMSE dict per leg. Nothing is re-scored; the tool only re-reads.

`--tie-arm` is normally the SAME arm as `--den-arm` (that is what r3s2_ceiling's
C3 does: `ok_rank = (R1_H < R0_H) == (R1_test < R0_test)`), in which case a rank
flip is exactly "the paired effect A-vs-B changes sign between the splits".
Passing the ablation arm instead answers a different question; say which you
meant.

Provenance: r3s2_field_reach-B3 turn 1 (worktree
scratchpad/r3s2b3_mech/reanalysis_turn_1.py), where it showed the C3 failure on
the two N_hf=5 cells was a real bias (mean g 0.36 / 0.24 against a 0.25
tolerance, sd ratio 20.5 vs the sampling law's 6.32) while the one sharp-cell
failure was 5/5 rank ties at a 2.1e-3 margin on the cell with the smallest |rho|
in the campaign. Its recomputed predicate reproduced the shipped `rank_agrees`
on 125/125 legs, which is the check that caught a wrong-pair reading in the
first pass.
"""
from __future__ import annotations

import argparse
import glob as globmod
import json
import math
import os
from collections import defaultdict

import numpy as np


def dig(obj, path):
    """dotted lookup, e.g. 'bands.edges_wavenumber'."""
    for part in path.split("."):
        obj = obj[part]
    return obj


def erfc_tail(t, sd):
    """P(|X| > t) for X ~ N(0, sd^2)."""
    if sd <= 0:
        return 0.0
    return math.erfc(t / (sd * math.sqrt(2.0)))


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--diag", required=True, nargs="+",
                   help="diag JSON paths or globs (one file per cell x seed)")
    p.add_argument("--legs-key", default="legs")
    p.add_argument("--num-arm", required=True, help="arm A (numerator of r)")
    p.add_argument("--den-arm", required=True, help="arm B (denominator of r)")
    p.add_argument("--heldout-key", default="nrmse",
                   help="per-leg dict of held-out nRMSE by arm")
    p.add_argument("--test-key", default="nrmse_test",
                   help="per-leg dict of test-split nRMSE by arm")
    p.add_argument("--tol", type=float, default=0.25,
                   help="licence tolerance on |g| (log units)")
    p.add_argument("--tie-arm", default=None,
                   help="arm whose ranking against --num-arm the rank clause "
                        "checks (enables the tie / dead-band analysis)")
    p.add_argument("--tie-deadband", type=float, default=0.01,
                   help="relative margin below which a rank flip is a tie")
    p.add_argument("--heldout-size-key", default="n_heldout")
    p.add_argument("--cell-key", default="dataset")
    p.add_argument("--seed-key", default="seed")
    p.add_argument("--row-key", default=None,
                   help="per-leg list of held-out row ids; enables row-identity "
                        "attribution and leave-one-row-out")
    p.add_argument("--attribute", default=None,
                   help="dotted per-leg scalar to attribute to rows, e.g. "
                        "'stats.rho'")
    p.add_argument("--out", default=None)
    a = p.parse_args()

    files = []
    for g in a.diag:
        files.extend(sorted(globmod.glob(g)) or ([g] if os.path.exists(g) else []))
    if not files:
        raise SystemExit(f"no diag files matched {a.diag}")

    legs = []
    for f in files:
        d = json.load(open(f))
        cell, seed = d.get(a.cell_key, os.path.basename(f)), d.get(a.seed_key)
        for L in d[a.legs_key]:
            H, T = L[a.heldout_key], L[a.test_key]
            if a.num_arm not in T or a.den_arm not in T:
                continue
            aa = math.log(H[a.num_arm] / T[a.num_arm])
            bb = math.log(H[a.den_arm] / T[a.den_arm])
            rec = dict(cell=cell, seed=seed, leg=L.get("leg_id"),
                       g=aa - bb, a=aa, b=bb,
                       nH=L.get(a.heldout_size_key),
                       within_tol=abs(aa - bb) <= a.tol)
            if a.tie_arm and a.tie_arm in H and a.tie_arm in T:
                rec["rank_agrees"] = ((H[a.num_arm] < H[a.tie_arm])
                                      == (T[a.num_arm] < T[a.tie_arm]))
                rec["tie_margin"] = min(
                    abs(H[a.num_arm] - H[a.tie_arm]) / H[a.num_arm],
                    abs(T[a.num_arm] - T[a.tie_arm]) / T[a.num_arm])
            if a.row_key:
                rec["rows"] = list(L[a.row_key])
            if a.attribute:
                rec["attr"] = dig(L, a.attribute)
            legs.append(rec)

    cells = sorted({r["cell"] for r in legs})
    print("=" * 96)
    print(f"licence statistic  g = log(nRMSE_H/nRMSE_test)[{a.num_arm}] "
          f"- log(...)[{a.den_arm}]   tolerance {a.tol}")
    print(f"{len(legs)} legs from {len(files)} files, {len(cells)} cells")
    print()
    print(f"{'cell':<34}{'|H|':>5}{'n':>4}{'mean g':>9}{'sd g':>8}{'|bias|/sd':>10}"
          f"{'mean a':>9}{'mean b':>9}{'corr(a,b)':>10}{'tol fails':>11}")
    S = {}
    for c in cells:
        r = [x for x in legs if x["cell"] == c]
        g = np.array([x["g"] for x in r])
        aa = np.array([x["a"] for x in r])
        bb = np.array([x["b"] for x in r])
        sd = float(g.std(ddof=1)) if len(g) > 1 else 0.0
        corr = float(np.corrcoef(aa, bb)[0, 1]) if len(g) > 1 else float("nan")
        nf = sum(1 for x in r if not x["within_tol"])
        S[c] = dict(nH=r[0]["nH"], n=len(r), mean=float(g.mean()), sd=sd,
                    mean_a=float(aa.mean()), mean_b=float(bb.mean()),
                    corr_ab=corr, tol_fails=nf, fail_rate=nf / len(r))
        print(f"{str(c):<34}{str(r[0]['nH']):>5}{len(r):>4}{g.mean():>9.4f}{sd:>8.4f}"
              f"{(abs(g.mean())/sd if sd else float('nan')):>10.3f}"
              f"{aa.mean():>9.4f}{bb.mean():>9.4f}{corr:>10.3f}{nf:>7d}/{len(r):<3d}")
    print("   legs within a cell are generally NOT independent (overlapping folds,")
    print("   shared seeds): read mean/sd descriptively, not as a p-value.")

    sizes = {S[c]["nH"] for c in cells if S[c]["nH"]}
    if len(sizes) > 1:
        big = max(sizes)
        print()
        print("=" * 96)
        print(f"sample-size explanation: project every cell to |H| = {min(sizes)} "
              f"by the 1/sqrt(|H|) law and compare fail rates")
        small = min(sizes)
        for c in cells:
            s = S[c]
            if not s["nH"]:
                continue
            if s["nH"] == big:
                sd_hat = s["sd"] * math.sqrt(big / small)
                print(f"   {str(c):<34} |H|={s['nH']:<5} sd {s['sd']:.4f} -> "
                      f"sd_hat {sd_hat:.4f} at |H|={small}: zero-bias "
                      f"P(|g|>{a.tol}) = {erfc_tail(a.tol, sd_hat):.2%}")
            else:
                zb = erfc_tail(a.tol, s["sd"])
                wb = 0.5 * (erfc_tail(a.tol - s["mean"], s["sd"])
                            + erfc_tail(a.tol + s["mean"], s["sd"]))
                print(f"   {str(c):<34} |H|={s['nH']:<5} OBSERVED fail rate "
                      f"{s['fail_rate']:.2%}; zero-bias model {zb:.2%}; "
                      f"with its own bias {wb:.2%}")
        obs = np.mean([S[c]["sd"] for c in cells if S[c]["nH"] == small])
        ref = np.mean([S[c]["sd"] for c in cells if S[c]["nH"] == big])
        print(f"   sd ratio small/big = {obs/ref:.2f} vs sampling-law "
              f"sqrt({big}/{small}) = {math.sqrt(big/small):.2f}   "
              f"({'EXCESS -> not pure sampling' if obs/ref > 1.5*math.sqrt(big/small) else 'consistent with sampling'})")

    if a.tie_arm:
        print()
        print("=" * 96)
        print(f"rank sub-clause ({a.num_arm} vs {a.tie_arm}) and the "
              f"{a.tie_deadband:.1%} dead-band counterfactual")
        print(f"{'cell':<34}{'legs':>5}{'rank-only':>11}{'tol-only':>10}"
              f"{'both':>6}{'pass':>6}{'flips that are ties':>21}{'median margin':>15}")
        for c in cells:
            r = [x for x in legs if x["cell"] == c and "rank_agrees" in x]
            if not r:
                continue
            ro = sum(1 for x in r if not x["rank_agrees"] and x["within_tol"])
            to = sum(1 for x in r if x["rank_agrees"] and not x["within_tol"])
            bo = sum(1 for x in r if not x["rank_agrees"] and not x["within_tol"])
            pa = sum(1 for x in r if x["rank_agrees"] and x["within_tol"])
            fl = [x for x in r if not x["rank_agrees"]]
            ties = [x for x in fl if x["tie_margin"] < a.tie_deadband]
            med = np.median([x["tie_margin"] for x in fl]) if fl else float("nan")
            S[c].update(rank_only=ro, tol_only=to, both=bo, passes=pa,
                        n_flips=len(fl), n_ties=len(ties))
            print(f"{str(c):<34}{len(r):>5}{ro:>11}{to:>10}{bo:>6}{pa:>6}"
                  f"{len(ties):>13}/{len(fl):<7}{med:>15.2e}")
        print()
        print("   per (cell, seed) verdict, as-shipped vs with the dead-band:")
        for c in cells:
            for sd_ in sorted({x["seed"] for x in legs if x["cell"] == c},
                              key=lambda v: (v is None, v)):
                r = [x for x in legs if x["cell"] == c and x["seed"] == sd_
                     and "rank_agrees" in x]
                if not r:
                    continue
                fl = [x for x in r if not x["rank_agrees"]]
                ties = [x for x in fl if x["tie_margin"] < a.tie_deadband]
                tol_ok = all(x["within_tol"] for x in r)
                shipped = (not fl) and tol_ok
                after = (len(fl) == len(ties)) and tol_ok
                print(f"     {str(c):<34} seed {str(sd_):<4} flips {len(fl):>2} "
                      f"(ties {len(ties):>2})  tol_ok {str(tol_ok):<5}  "
                      f"as-shipped {'PASS' if shipped else 'FAIL'}  "
                      f"dead-band {'PASS' if after else 'FAIL'}")

    rows_out = {}
    if a.row_key and a.attribute:
        print()
        print("=" * 96)
        print(f"row-identity attribution of `{a.attribute}` (held-out row ids)")
        for c in cells:
            r = [x for x in legs if x["cell"] == c and "rows" in x]
            ids = sorted({i for x in r for i in x["rows"]})
            if not r or len(ids) > 32:
                continue
            print(f"\n   -- {c}  ({len(r)} legs over {len(ids)} distinct rows)")
            print(f"      {'row':>5}{'legs':>7}{'mean':>10}{'min':>10}{'max':>10}"
                  f"{'mean |g|':>10}")
            rows_out[c] = {}
            for i in ids:
                sel = [x for x in r if i in x["rows"]]
                v = np.array([x["attr"] for x in sel], dtype=float)
                gg = np.array([abs(x["g"]) for x in sel])
                rows_out[c][str(i)] = dict(n=len(sel), mean=float(v.mean()),
                                           min=float(v.min()), max=float(v.max()),
                                           mean_absg=float(gg.mean()))
                print(f"      {i:>5}{len(sel):>7}{v.mean():>10.3f}{v.min():>10.3f}"
                      f"{v.max():>10.3f}{gg.mean():>10.3f}")
            print("      leave-one-ROW-out (drop every leg holding row k out):")
            for i in ids:
                sel = [x for x in r if i not in x["rows"]]
                if not sel:
                    continue
                v = np.array([x["attr"] for x in sel], dtype=float)
                nf = sum(1 for x in sel if not x["within_tol"])
                print(f"        drop {i:>3}: n={len(sel):>3}  mean {v.mean():>8.3f}"
                      f"  [{v.min():>7.3f},{v.max():>7.3f}]  tol-fails "
                      f"{nf}/{len(sel)}")

    if a.out:
        json.dump(dict(cells=S, rows=rows_out, tol=a.tol,
                       num_arm=a.num_arm, den_arm=a.den_arm,
                       tie_arm=a.tie_arm, tie_deadband=a.tie_deadband,
                       legs=legs, files=files),
                  open(a.out, "w"), indent=1, default=float)
        print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
