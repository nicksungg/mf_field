#!/usr/bin/env python
"""LSI transfer-function stability audit for the `dc_cleaned` corrector lineage.

WHAT IT MEASURES
----------------
Every card in the round-1 `s4_router` -> round-2 `r2s2_stack` -> round-3
`r3s2_stack_ic` lineage builds its stage-2 corrector on a closed-form
least-squares-in-frequency (Wiener) transfer function ``T(k)``, fit on paired
real-LF/HF residuals and then applied to a *pseudo*-LF that the model produced.
The diag sidecars publish ``T_band_mean_abs`` — |T| averaged over dyadic radial
bands, with the LAST band always the octave above the LF Nyquist (LF is half the
HF grid on every panel cell).

This tool flags the failure class found in `r3s2_field_reach-B1` turn 1:

  * **AMPLIFYING**  — |T| > 1 in any band. A corrector whose transfer function
    amplifies will multiply the emulator's error rather than remove it. Above
    the LF Nyquist the regressor has essentially no power, so an unregularised
    Wiener ratio there is a 0/0 whose magnitude is decided by the fit fold.
  * **SEED-UNSTABLE** — the same band's |T| varies by more than `--seed-ratio-tol`
    across seeds of the same cell. On ifc_poisson this was 6.24 / 6.24 / 66.22,
    a 10.6x swing that produced a 15x swing in the scored nRMSE.
  * **SAMPLE-STARVED** — the operator is fit from fewer than `--min-fit` pairs
    (`split_protocol.n_fit`). ifc_poisson fits a full 64x64 complex operator
    from 3 pairs, with `S6_LSI_RIDGE = 0`.

It also reports each cell's per-band error attribution
(``band_contribution_profile`` = scored-arm / emul-only band error energy) so
you can see whether the flagged band is in fact where the error went.

WHY IT GENERALISES
------------------
It reads only fields that every card in this lineage already writes, takes the
diag directory as a CLI argument, and discovers datasets/seeds from the
filenames. It is the right thing to run after ANY card that uses an LSI /
Wiener / deconvolution pre-stage, and after any change to the fit-fold protocol.

INVOCATION
----------
    python tools/lsi_transfer_stability_audit.py --diag-root <dir> [...]

Exit code 1 with `--fail-on-flag` if any cell is flagged.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys

DIAG_RE = re.compile(r"^diag_(?P<ds>.+)_e(?P<epochs>\d+)_s(?P<seed>\d+)\.json$")


def discover(diag_root: str, pattern: str):
    out = {}
    for p in sorted(glob.glob(os.path.join(diag_root, pattern))):
        m = DIAG_RE.match(os.path.basename(p))
        if not m:
            continue
        out.setdefault(m.group("ds"), {})[int(m.group("seed"))] = p
    return out


def load(p):
    with open(p) as f:
        return json.load(f)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--diag-root", required=True,
                    help="directory containing diag_<dataset>_e<E>_s<S>.json sidecars")
    ap.add_argument("--pattern", default="diag_*.json")
    ap.add_argument("--amplify-tol", type=float, default=1.0,
                    help="flag AMPLIFYING when band |T| exceeds this (default 1.0)")
    ap.add_argument("--seed-ratio-tol", type=float, default=2.0,
                    help="flag SEED_UNSTABLE when max/min band |T| across seeds exceeds this")
    ap.add_argument("--min-fit", type=int, default=32,
                    help="flag SAMPLE_STARVED when split_protocol.n_fit is below this")
    ap.add_argument("--out", default=None, help="write the full report as JSON here")
    ap.add_argument("--fail-on-flag", action="store_true")
    args = ap.parse_args(argv)

    cells = discover(args.diag_root, args.pattern)
    if not cells:
        print(f"no diag sidecars matched {args.pattern} under {args.diag_root}", file=sys.stderr)
        return 2

    report = {"_diag_root": os.path.abspath(args.diag_root),
              "_thresholds": {"amplify_tol": args.amplify_tol,
                              "seed_ratio_tol": args.seed_ratio_tol,
                              "min_fit": args.min_fit},
              "cells": {}}
    n_flagged = 0
    print(f"{'dataset':26s} {'seeds':>7s} {'n_fit':>6s} {'ridge':>7s}  "
          f"{'|T| per band (last = super-LF-Nyquist)':48s} flags")
    for ds in sorted(cells):
        seeds = sorted(cells[ds])
        T = {}
        prof = {}
        n_fit = None
        ridge = None
        edges = None
        grids = None
        for s in seeds:
            d = load(cells[ds][s])
            T[s] = d.get("T_band_mean_abs")
            prof[s] = d.get("band_contribution_profile")
            sp = d.get("split_protocol") or {}
            n_fit = sp.get("n_fit", n_fit)
            edges = (d.get("bands") or {}).get("edges_wavenumber", edges)
            grids = (d.get("hf_grid"), d.get("lf_grid"))
            p1 = (d.get("probes") or {}).get("P1_bc_match_audit") or {}
            if "ridge" in p1:
                ridge = p1["ridge"]
        usable = [s for s in seeds if isinstance(T[s], list) and T[s]]
        if not usable:
            continue
        n_bands = len(T[usable[0]])
        flags = []
        band_flags = []
        for b in range(n_bands):
            vals = [T[s][b] for s in usable
                    if T[s][b] is not None and T[s][b] == T[s][b]]  # drop None/NaN
            if not vals:
                # an empty band (e.g. 1-D cells whose radial band holds no rFFT bins)
                continue
            amp = max(vals) > args.amplify_tol
            ratio = (max(vals) / min(vals)) if min(vals) > 0 else float("inf")
            uns = ratio > args.seed_ratio_tol
            if amp or uns:
                band_flags.append({"band": b + 1, "values": vals, "seed_ratio": ratio,
                                   "amplifying": bool(amp), "seed_unstable": bool(uns),
                                   "is_super_lf_nyquist_band": b == n_bands - 1})
            if amp:
                flags.append(f"AMPLIFYING(b{b + 1}:{max(vals):.3g})")
            if uns:
                flags.append(f"SEED_UNSTABLE(b{b + 1}:{ratio:.1f}x)")
        if n_fit is not None and n_fit < args.min_fit:
            flags.append(f"SAMPLE_STARVED(n_fit={n_fit})")
        if ridge is not None and float(ridge) == 0.0 and any("AMPLIFYING" in f for f in flags):
            flags.append("UNREGULARISED(ridge=0)")
        if flags:
            n_flagged += 1
        tstr = " ".join(f"{max(T[s][b] for s in usable):>8.3g}" for b in range(n_bands))
        print(f"{ds:26s} {len(usable):7d} {str(n_fit):>6s} {str(ridge):>7s}  {tstr:48s} "
              f"{','.join(flags) if flags else 'ok'}")
        if band_flags:
            for bf in band_flags:
                per = ", ".join(f"s{s}={T[s][bf['band'] - 1]:.5g}" for s in usable)
                print(f"{'':26s}   band {bf['band']}"
                      f"{' (SUPER-LF-NYQUIST)' if bf['is_super_lf_nyquist_band'] else ''}: {per}")
                if all(isinstance(prof[s], list) for s in usable):
                    pr = ", ".join(f"s{s}={prof[s][bf['band'] - 1]:.4g}" for s in usable)
                    print(f"{'':26s}   band {bf['band']} error contribution "
                          f"(scored/emul_only): {pr}")
        report["cells"][ds] = {"seeds": usable, "n_fit": n_fit, "ridge": ridge,
                               "band_edges_wavenumber": edges,
                               "hf_grid": grids[0] if grids else None,
                               "lf_grid": grids[1] if grids else None,
                               "T_band_mean_abs": {str(s): T[s] for s in usable},
                               "band_contribution_profile": {str(s): prof[s] for s in usable},
                               "band_flags": band_flags, "flags": flags}

    print(f"\nFLAGGED {n_flagged}/{len(report['cells'])} cells")
    if args.out:
        with open(args.out, "w") as f:
            json.dump(report, f, indent=1)
        print(f"wrote {args.out}")
    if args.fail_on_flag and n_flagged:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
