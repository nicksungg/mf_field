#!/usr/bin/env python
"""stage_error_transmission_audit — for a MULTI-STAGE route (condition -> some
intermediate -> the scored field), does the pipeline ATTENUATE, transmit or
amplify its first stage's error, and is the end-to-end score anything other than
the first stage's score?

Every "route through a cheap intermediate" card in this program ships three
numbers per cell that answer this without any new compute:

    stage1  the intermediate's own held-out error (e.g. pseudo-LF vs real LF)
    final   the deployed end-to-end arm's error       (intermediate PREDICTED)
    oracle  the same arm fed the REAL intermediate    (the ceiling)
    base    a matched-budget arm that skips the intermediate (the denominator)

From them the tool computes, per cell and pooled:

  * TRANSMISSION GAIN  (final - oracle) / stage1 -- the fraction of the stage-1
    error that survives the downstream stage. ~1 means the downstream stage is
    transparent to stage-1 error (it neither corrects nor amplifies it), which is
    the single most compact way to say "this route is stage-1 limited".
  * THE IDENTITY  final vs stage1 and base vs stage1, as ratios AND as a pooled
    log-log slope with its correlation. A unit slope with r ~ 1 across cells that
    span decades is a law, not a coincidence: the route's accuracy IS its stage-1
    accuracy. If `base` lands on the same line, the intermediate cannot buy
    anything, because predicting it is as hard as predicting the target.
  * REQUIRED-ACCURACY MULTIPLIER  stage1 / oracle -- how many times more accurate
    the intermediate must become before the ceiling is reachable. This is what a
    large `phi_ceil` actually costs, and it is routinely 10x-100x.
  * Optional BAND-RESOLVED anatomy (`--band-key`): the share of each arm's error
    energy per radial band and the final/oracle ratio per band, which localises
    the failure in wavenumber (low-k hallucination vs high-k detail).

Everything is read from shipped per-cell diagnostic JSONs with a per-leg dump.
Nothing is re-scored, no GPU, no checkpoints touched.

Provenance: r3s2_field_reach-B3 turn 2 (worktree
scratchpad/r3s2b3_mech/reanalysis_turn_2.py), where it produced that card's
mechanism: transmission gain 0.80-1.02 on 6/6 cells, final/stage1 in
[0.811, 1.108] with log-log slope 1.035 (r = 0.998) and base/stage1 slope 1.004
(r = 0.988) over 2.2 decades, required-accuracy multiplier 8.7x-116.6x, and an
error that is 86-99.8% low-band while the oracle's residual is high-band.
"""
from __future__ import annotations

import argparse
import glob as globmod
import json
import math
import os

import numpy as np


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--diag", required=True, nargs="+",
                   help="diag JSON paths or globs (one per cell x seed)")
    p.add_argument("--legs-key", default="legs")
    p.add_argument("--stage1-key", default="emulator_heldout_nrmse",
                   help="per-leg scalar: the intermediate's own held-out error")
    p.add_argument("--arm-key", default="nrmse",
                   help="per-leg dict of arm -> error on the scored split")
    p.add_argument("--final-arm", required=True)
    p.add_argument("--oracle-arm", required=True)
    p.add_argument("--baseline-arm", default=None,
                   help="matched-budget arm that skips the intermediate")
    p.add_argument("--extra-arm", action="append", default=[],
                   help="additional arms to report in the band table")
    p.add_argument("--band-key", default=None,
                   help="per-leg dict arm -> list of per-band error energies")
    p.add_argument("--cell-key", default="dataset")
    p.add_argument("--seed-key", default="seed")
    p.add_argument("--out", default=None)
    a = p.parse_args()

    files = []
    for g in a.diag:
        files.extend(sorted(globmod.glob(g)) or ([g] if os.path.exists(g) else []))
    if not files:
        raise SystemExit(f"no diag files matched {a.diag}")

    arms = [a.final_arm, a.oracle_arm] + ([a.baseline_arm] if a.baseline_arm else [])
    arms += [x for x in a.extra_arm if x not in arms]

    cell = {}
    for f in files:
        d = json.load(open(f))
        c = d.get(a.cell_key, os.path.basename(f))
        e = cell.setdefault(c, dict(stage1=[], legs=0, seeds=set(),
                                    arm={k: [] for k in arms}, band={}))
        e["seeds"].add(d.get(a.seed_key))
        for L in d[a.legs_key]:
            s1 = L.get(a.stage1_key)
            if s1 is not None:
                e["stage1"].append(float(s1))
            for k in arms:
                if k in L[a.arm_key]:
                    e["arm"][k].append(float(L[a.arm_key][k]))
            if a.band_key and a.band_key in L:
                for k, v in L[a.band_key].items():
                    e["band"].setdefault(k, []).append(np.asarray(v, dtype=float))
            e["legs"] += 1

    cells = sorted(cell)
    print("=" * 100)
    print(f"stage-1 key `{a.stage1_key}`   final `{a.final_arm}`   "
          f"oracle `{a.oracle_arm}`   baseline `{a.baseline_arm}`")
    print(f"{len(files)} files, {len(cells)} cells")
    print()
    hdr = (f"{'cell':<32}{'legs':>5}{'stage1':>10}{'final':>10}{'oracle':>10}"
           f"{'base':>10}{'gain':>8}{'fin/s1':>8}{'base/s1':>9}{'req x':>9}")
    print(hdr)
    S = {}
    for c in cells:
        e = cell[c]
        s1 = float(np.mean(e["stage1"])) if e["stage1"] else float("nan")
        fin = float(np.mean(e["arm"][a.final_arm]))
        orc = float(np.mean(e["arm"][a.oracle_arm]))
        bas = (float(np.mean(e["arm"][a.baseline_arm]))
               if a.baseline_arm else float("nan"))
        S[c] = dict(n_legs=e["legs"], n_seeds=len(e["seeds"]), stage1=s1,
                    final=fin, oracle=orc, baseline=bas,
                    transmission_gain=(fin - orc) / s1 if s1 else float("nan"),
                    final_over_stage1=fin / s1 if s1 else float("nan"),
                    baseline_over_stage1=bas / s1 if s1 else float("nan"),
                    required_accuracy_multiplier=s1 / orc if orc else float("nan"),
                    oracle_share_of_final=orc / fin if fin else float("nan"))
        v = S[c]
        print(f"{str(c):<32}{e['legs']:>5}{s1:>10.4f}{fin:>10.4f}{orc:>10.4f}"
              f"{bas:>10.4f}{v['transmission_gain']:>8.3f}"
              f"{v['final_over_stage1']:>8.3f}{v['baseline_over_stage1']:>9.3f}"
              f"{v['required_accuracy_multiplier']:>8.1f}x")
    print()
    print("   gain    = (final - oracle) / stage1 : ~1 => the downstream stage is")
    print("             TRANSPARENT to stage-1 error (no correction, no amplification)")
    print("   req x   = stage1 / oracle : how much more accurate the intermediate")
    print("             must become before the ceiling is reachable")

    ok = [c for c in cells if np.isfinite(S[c]["stage1"]) and S[c]["stage1"] > 0]
    if len(ok) >= 3:
        ls = np.log([S[c]["stage1"] for c in ok])
        print()
        print("=" * 100)
        print("pooled across cells (a unit slope with r ~ 1 over decades is a law):")
        for lab, key in (("final", "final"), ("baseline", "baseline")):
            y = np.array([S[c][key] for c in ok])
            if not np.all(np.isfinite(y)) or np.any(y <= 0):
                continue
            sl = float(np.polyfit(ls, np.log(y), 1)[0])
            r = float(np.corrcoef(ls, np.log(y))[0, 1])
            rat = y / np.exp(ls)
            print(f"   log({lab}) vs log(stage1): slope {sl:.3f}  r {r:.4f}   "
                  f"{lab}/stage1 mean {rat.mean():.3f} sd {rat.std(ddof=1):.3f} "
                  f"range [{rat.min():.3f}, {rat.max():.3f}]")
        print(f"   stage-1 error spans {np.exp(ls).min():.4g} to "
              f"{np.exp(ls).max():.4g} "
              f"({(ls.max()-ls.min())/math.log(10):.1f} decades)")
        g = np.array([S[c]["transmission_gain"] for c in ok])
        print(f"   transmission gain over cells: mean {g.mean():.3f} "
              f"range [{g.min():.3f}, {g.max():.3f}]")

    if a.band_key:
        print()
        print("=" * 100)
        print("band-resolved error energy (mean over legs; shares per arm, then ratios)")
        for c in cells:
            e = cell[c]
            if not e["band"]:
                continue
            B = {k: np.mean(np.vstack(v), axis=0) for k, v in e["band"].items()}
            nb = len(next(iter(B.values())))
            print(f"\n   -- {c}")
            print(f"      {'arm':<18}" + "".join(f"{f'b{i}':>11}" for i in range(nb)))
            for k in arms:
                if k not in B:
                    continue
                sh = B[k] / B[k].sum()
                print(f"      {k:<18}" + "".join(f"{x:>11.2%}" for x in sh))
            for num, den in ((a.final_arm, a.oracle_arm),
                             (a.final_arm, a.baseline_arm),
                             (a.oracle_arm, a.baseline_arm)):
                if not den or num not in B or den not in B:
                    continue
                with np.errstate(divide="ignore", invalid="ignore"):
                    rr = np.where(B[den] > 0, B[num] / np.where(B[den] > 0, B[den], 1),
                                  np.nan)
                print(f"      {num[:8]}/{den[:8]:<9}"
                      + "".join(f"{x:>11.3g}" for x in rr)
                      + f"   | total {B[num].sum()/B[den].sum():.3g}")
            S[c]["band_shares"] = {k: list(map(float, B[k] / B[k].sum()))
                                   for k in B}
            S[c]["band_energy"] = {k: list(map(float, B[k])) for k in B}

    if a.out:
        json.dump(dict(cells=S, files=files, stage1_key=a.stage1_key,
                       final_arm=a.final_arm, oracle_arm=a.oracle_arm,
                       baseline_arm=a.baseline_arm),
                  open(a.out, "w"), indent=1, default=float)
        print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
