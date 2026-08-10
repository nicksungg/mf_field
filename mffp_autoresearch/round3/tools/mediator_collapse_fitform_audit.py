#!/usr/bin/env python
"""mediator_collapse_fitform_audit.py — is a "does arm X collapse onto arm Y's
mediator curve?" verdict a FINDING or an artefact of the fit's functional form?

WHAT IT MEASURES
    A common clause shape in this round: fit outcome ~ mediator on a REFERENCE set of
    cells, then declare a TEST set of cells "collapsed" if it lies within tol of the
    fit. If the mediator relation is curved and the test cells sit in a band where a
    straight line is biased, the clause reports a systematic deficit that is entirely
    the estimator's. This tool prices that risk with three things:

      1. CURVATURE OF THE REFERENCE RELATION — the reference set's OWN residuals about
         its own linear fit, grouped by whatever label you supply. A monotone-then-
         reversing (U or inverted-U) pattern of group means is the signature.
      2. THE SAME VERDICT UNDER THREE FITS of the SAME reference cells — linear,
         quadratic, and isotonic (PAVA; monotone, shape-free). Reports n_negative,
         mean residual, max |residual|, n over tol, and the per-seed collapse verdict
         for each.
      3. BIAS vs SCATTER — the reference set's own RMS residual about each fit, so you
         can say whether the test cells' miss is a systematic offset (which the fit
         form can create) or genuine per-cell scatter (which it cannot).

    Read the verdict as: if the deficit's MEAN collapses across fit forms but the MAX
    does not, the directional claim is an artefact and the surviving finding is
    scatter -- report it that way.

PROVENANCE
    r3s3_lf_value-B2 mechanism turn 2. On that card's pre-registered D-D clause it
    reproduced part 5 exactly under the linear fit (25/27 negative, per-seed
    max |resid| 0.2594 / 0.2292 / 0.1583, slope 1.6877 / intercept -0.2849 on seed 0)
    and then showed that a quadratic or isotonic fit of the SAME 30 reference cells
    takes the systematic deficit from -0.0834 R to -0.0120 / -0.0156 R (below one
    tau_rel = 0.0246 R) with the sign count falling 25/27 -> 13/27, 14/27, while the
    max |residual| stays 0.154-0.205 against the reference cells' own RMS of
    0.023-0.057. Verdict there: FIT_FORM_ARTEFACT on the mean, genuine scatter on
    the max.

INVOCATION
    # generic: one JSON/CSV-free table of cells passed inline
    python tools/mediator_collapse_fitform_audit.py \
        --cells cells.json --ref-arms A0,A1,A2,A3c --test-arms A5 \
        --x-key alignment --y-key R --group-key arm --seed-key seed --tol 0.05

    # cells.json is a list of records; every key above must be present on each record.

VERDICTS
    FIT_FORM_ARTEFACT   |mean residual| falls below --tol-mean (default = tol/2) under
                        at least one non-linear fit AND the sign count loses its
                        majority (crosses 60/40).
    GENUINE_OFFSET      the mean survives every fit form.
    SCATTER_ONLY        the mean is small under every fit but the max exceeds tol.
"""
import argparse
import json

import numpy as np


def isotonic_predictor(x, y):
    """PAVA isotonic regression of y on x; returns a callable interpolator."""
    o = np.argsort(x)
    xs, ys = np.asarray(x, float)[o], np.asarray(y, float)[o]
    lvl, wt = list(ys), [1.0] * len(ys)
    i = 0
    while i < len(lvl) - 1:
        if lvl[i] > lvl[i + 1]:
            nw = wt[i] + wt[i + 1]
            lvl[i:i + 2] = [(lvl[i] * wt[i] + lvl[i + 1] * wt[i + 1]) / nw]
            wt[i:i + 2] = [nw]
            if i > 0:
                i -= 1
        else:
            i += 1
    fit = np.repeat(lvl, [int(round(w)) for w in wt])[: len(xs)]
    return lambda q: np.interp(q, xs, fit)


def fit_of(tag, x, y):
    if tag == "linear":
        c = np.polyfit(x, y, 1)
        return lambda q: np.polyval(c, q), c
    if tag == "quadratic":
        c = np.polyfit(x, y, 2)
        return lambda q: np.polyval(c, q), c
    return isotonic_predictor(x, y), None


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cells", required=True, help="JSON list of cell records")
    ap.add_argument("--ref-arms", required=True, help="comma-separated arm labels")
    ap.add_argument("--test-arms", required=True)
    ap.add_argument("--x-key", default="alignment")
    ap.add_argument("--y-key", default="R")
    ap.add_argument("--group-key", default="arm")
    ap.add_argument("--seed-key", default="seed")
    ap.add_argument("--arm-key", default="arm")
    ap.add_argument("--tol", type=float, default=0.05, help="collapse tolerance on |resid|")
    ap.add_argument("--tol-mean", type=float, default=None,
                    help="threshold on |mean resid| for FIT_FORM_ARTEFACT (default tol/2)")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    tol_mean = a.tol_mean if a.tol_mean is not None else a.tol / 2.0

    cells = json.load(open(a.cells))
    ref_arms = a.ref_arms.split(",")
    test_arms = a.test_arms.split(",")
    ref = [c for c in cells if c[a.arm_key] in ref_arms]
    tst = [c for c in cells if c[a.arm_key] in test_arms]
    seeds = sorted({c[a.seed_key] for c in cells})
    print(f"reference cells {len(ref)} ({ref_arms})   test cells {len(tst)} ({test_arms})   "
          f"seeds {seeds}   tol {a.tol}")
    if not ref or not tst:
        raise SystemExit("empty reference or test set -- check --ref-arms/--test-arms")

    out = {"n_ref": len(ref), "n_test": len(tst), "seeds": seeds, "tol": a.tol}

    # ---- 1. curvature of the reference relation
    print("\n== 1. reference set's OWN residuals about its OWN linear fit ==")
    groups = sorted({c[a.group_key] for c in ref},
                    key=lambda g: np.mean([c[a.x_key] for c in ref if c[a.group_key] == g]))
    print(f"  {'group':<20}{'x':>8}" + "".join(f"{'s'+str(s):>10}" for s in seeds) + f"{'mean':>10}")
    curv = {}
    for s in seeds:
        L = [c for c in ref if c[a.seed_key] == s]
        f, _ = fit_of("linear", [c[a.x_key] for c in L], [c[a.y_key] for c in L])
        for c in L:
            c["_lin_res"] = c[a.y_key] - float(f(c[a.x_key]))
    for g in groups:
        per = [float(np.mean([c["_lin_res"] for c in ref
                              if c[a.group_key] == g and c[a.seed_key] == s])) for s in seeds]
        xg = float(np.mean([c[a.x_key] for c in ref if c[a.group_key] == g]))
        curv[str(g)] = dict(x=xg, per_seed=per, mean=float(np.mean(per)))
        print(f"  {str(g):<20}{xg:>8.3f}" + "".join(f"{v:>+10.4f}" for v in per) +
              f"{np.mean(per):>+10.4f}")
    signs = [np.sign(curv[str(g)]["mean"]) for g in groups]
    n_flips = int(sum(1 for i in range(len(signs) - 1) if signs[i] != signs[i + 1]))
    out["curvature"] = dict(groups=curv, sign_changes=n_flips,
                            span=float(max(v["mean"] for v in curv.values()) -
                                       min(v["mean"] for v in curv.values())))
    print(f"  sign changes across groups: {n_flips}   residual span "
          f"{out['curvature']['span']:.4f}  (>=2 sign changes = the linear fit is "
          f"structurally biased in some x band)")
    print(f"  test cells sit at x = " +
          ", ".join(f"{g}:{np.mean([c[a.x_key] for c in tst if c[a.group_key]==g]):.3f}"
                    for g in sorted({c[a.group_key] for c in tst})))

    # ---- 2/3. the verdict under three fits
    print(f"\n== 2. the collapse verdict under three fits of the SAME {len(ref)} cells ==")
    print(f"  {'fit':<11}{'n_neg':>8}{'mean':>10}{'max|res|':>10}{'n>tol':>7}"
          f"{'per-seed max':>28}{'ref RMS':>22}{'collapse':>22}")
    res_by_fit = {}
    for tag in ["linear", "quadratic", "isotonic"]:
        allr, permax, permean, refrms = [], [], [], []
        for s in seeds:
            L = [c for c in ref if c[a.seed_key] == s]
            f, _ = fit_of(tag, [c[a.x_key] for c in L], [c[a.y_key] for c in L])
            rr = [c[a.y_key] - float(f(c[a.x_key])) for c in tst if c[a.seed_key] == s]
            lr = [c[a.y_key] - float(f(c[a.x_key])) for c in L]
            allr += rr
            permax.append(float(np.max(np.abs(rr))))
            permean.append(float(np.mean(rr)))
            refrms.append(float(np.sqrt(np.mean(np.square(lr)))))
        v = np.array(allr)
        res_by_fit[tag] = dict(n_negative=int((v < 0).sum()), n=len(v), mean=float(v.mean()),
                               max_abs=float(np.abs(v).max()),
                               n_over_tol=int((np.abs(v) > a.tol).sum()),
                               per_seed_max=permax, per_seed_mean=permean,
                               ref_rms=refrms,
                               collapse=[m <= a.tol for m in permax])
        print(f"  {tag:<11}{res_by_fit[tag]['n_negative']:>4}/{len(v):<3}{v.mean():>+10.4f}"
              f"{np.abs(v).max():>10.4f}{res_by_fit[tag]['n_over_tol']:>7}"
              f"{str([round(m,4) for m in permax]):>28}"
              f"{str([round(m,4) for m in refrms]):>22}"
              f"{str(res_by_fit[tag]['collapse']):>22}")
    out["by_fit"] = res_by_fit

    lin = res_by_fit["linear"]
    maj = max(lin["n_negative"], lin["n"] - lin["n_negative"]) / lin["n"]
    nonlin = [res_by_fit[t] for t in ["quadratic", "isotonic"]]
    mean_collapses = any(abs(r["mean"]) < tol_mean for r in nonlin)
    sign_collapses = any(max(r["n_negative"], r["n"] - r["n_negative"]) / r["n"] < 0.6
                         for r in nonlin)
    if abs(lin["mean"]) < tol_mean:
        verdict = "SCATTER_ONLY" if lin["max_abs"] > a.tol else "COLLAPSED"
    elif mean_collapses and sign_collapses:
        verdict = "FIT_FORM_ARTEFACT"
    elif mean_collapses:
        verdict = "FIT_FORM_ARTEFACT_MEAN_ONLY"
    else:
        verdict = "GENUINE_OFFSET"
    surviving = ("scatter (max |resid| exceeds tol under every fit)"
                 if min(r["max_abs"] for r in res_by_fit.values()) > a.tol
                 else "nothing beyond tol under at least one fit")
    print(f"\n  linear-fit sign majority {maj:.2f}; |mean| under non-linear fits "
          f"{[round(abs(r['mean']),4) for r in nonlin]} vs tol_mean {tol_mean}")
    print(f"  VERDICT: {verdict}    surviving finding: {surviving}")
    out["verdict"] = verdict
    out["surviving"] = surviving

    if a.out:
        json.dump(out, open(a.out, "w"), indent=1, default=float)
        print(f"\n[saved] {a.out}")


if __name__ == "__main__":
    main()
