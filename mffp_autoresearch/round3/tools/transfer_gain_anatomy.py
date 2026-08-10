#!/usr/bin/env python
"""transfer_gain_anatomy.py — is a reported `|T| > 1` a GAIN or a DISPERSION artefact?

Provenance: `r3s2_field_reach-B2` mechanism turns 1-2. Written because that card
was falsified by a clause reading a band-mean `|T| > 1` on `ifc_poisson`, and the
ENERGY-weighted transfer on that cell turned out to be -0.74 in *every* band with
coherence ~1 — i.e. there was no amplification anywhere in the operator. The
statistic that fired is an **unweighted arithmetic mean of |T| over a band's
modes**, which is exactly what `tools/lsi_transfer_stability_audit.py` reads out
of a diag sidecar, so every `AMPLIFYING` verdict in the round deserves this
second column beside it.

WHAT IT MEASURES, per radial band, dataset-side (no model, no GPU, no training):

  * `unweighted_mean_absT`  — THE STATISTIC the audit / a G2-style clause reads.
  * `energy_weighted_absT`  — sum|num| / sum den over the band (Parseval-weighted):
                              the gain that actually moves energy.
  * `signed_aggregate_T`    — Re(sum num)/sum den. Distinguishes `R = +cLF`
                              (the transfer amplifies) from `R = -cLF` (the
                              transfer CANCELS the upsampler's own content, which
                              is what every sharp cell's top octave turns out to be).
  * `coherence` vs its chance level `1/sqrt(n_fit)` — whether the fit is signal.
  * `lf_energy_share` / `residual_energy_share` — how much of the problem the band
                              is. A band holding 0.1% of the LF energy cannot
                              amplify anything, whatever its mode-mean says.
  * verdict per band: `TRUE_AMPLIFICATION` (energy-weighted > tol),
                      `DISPERSION_ARTEFACT` (only the unweighted mean > tol),
                      `CANCELLER` (signed aggregate <= -tol), `OK`.

PLUS two things the falsified card needed and did not have:

  * `--ridge-ladder`: for each candidate the band's unweighted mean |T| AND the
    held-out explained variance of the residual, so "what shrinkage would have
    passed the clause, and what would it have cost?" is answered with a number.
    Reports `min_ridge_passing_tol` per band.
  * `--enumerate-folds`: at small `Ntr` the seeds are a bad sampler of a
    closed-form fit. This enumerates ALL `C(Ntr, n_fit)` fit sets exactly and
    reports the population spread of the statistic, so a clause whose threshold
    sits inside that spread is visible as such.

RUN IT after any card whose stage 2 contains an LSI / Wiener / deconvolution
pre-stage, and before writing any clause whose threshold is a band-mean gain.

The estimator is the round's `fit_transfer` arithmetic verbatim
(`T = sum_n Rhat conj(LFhat) / sum_n |LFhat|^2`, ridge added as
`den + lambda*den.max()`, guard `den > 1e-20`), and the upsampled LF is built by
the FROZEN `round2/eval/panel_data.py::copylf_prediction`, so the residual
`R = HF - LF_up` is the certified construction. `--diag-root` cross-checks the
reproduction against a shipped diag before reporting anything.

Verified against `r3s2_field_reach-B2`: reproduces the shipped
`lsi_repair.T_band_mean_abs_reg` to max abs deviation 0.0 on all 15 legs.
"""
from __future__ import annotations

import argparse
import json
import sys
from itertools import combinations
from pathlib import Path

import numpy as np


# ── frozen eval layer (read-only) ────────────────────────────────────────
def _eval_dir() -> Path:
    here = Path(__file__).resolve()
    for p in here.parents:
        if (p / "mffp_autoresearch" / "round2" / "eval" / "panel_data.py").exists():
            return p / "mffp_autoresearch" / "round2" / "eval"
    raise SystemExit("could not locate mffp_autoresearch/round2/eval from " + str(here))


sys.path.insert(0, str(_eval_dir()))
import panel_data  # noqa: E402


# ── the round's estimator, verbatim arithmetic ───────────────────────────
def solve(num, den_raw, ridge: float, zero_mask=None):
    den = den_raw
    if float(ridge) != 0.0:
        den = den_raw + float(ridge) * float(den_raw.max() if den_raw.size else 0.0)
    T = np.where(den > 1e-20, num / np.maximum(den, 1e-20), 0.0)
    if zero_mask is not None:
        T = np.where(zero_mask, 0.0, T)
    return T


def radial_k(grid):
    H, W = int(grid[0]), int(grid[1])
    kx = np.fft.fftfreq(H) * H
    ky = np.arange(W // 2 + 1, dtype=np.float64)
    return np.sqrt(kx[:, None] ** 2 + ky[None, :] ** 2)


def band_masks(grid, n_bands: int):
    """Dyadic radial bands + the rFFT Parseval weight (the round's convention:
    edges k_nyq / 2^(n_bands-1-b), outermost band open-ended)."""
    H, W = int(grid[0]), int(grid[1])
    kr = radial_k(grid)
    weight = np.full((H, W // 2 + 1), 2.0)
    weight[:, 0] = 1.0
    if W % 2 == 0:
        weight[:, -1] = 1.0
    k_ny = min(H, W) / 2.0
    edges = [0.0] + [k_ny / 2.0 ** (n_bands - 1 - b) for b in range(n_bands)]
    masks = []
    for b in range(n_bands):
        masks.append(kr >= edges[b] if b == n_bands - 1
                     else (kr >= edges[b]) & (kr < edges[b + 1]))
    return masks, weight, edges


def split_fit_fold(Ntr: int, seed: int, holdout_frac: float):
    """The s4_router-lineage split: torch.randperm(Ntr, manual_seed(seed)), the
    first `n_val` (forced even, >= 2) rows held out, the rest the fit fold."""
    import torch
    perm = torch.randperm(Ntr, generator=torch.Generator().manual_seed(seed)).numpy()
    n_val = min(int(max(1, round(holdout_frac * Ntr))), max(Ntr - 1, 0))
    n_val = min(max(2, n_val - (n_val % 2)), (Ntr - 1) - ((Ntr - 1) % 2))
    return perm[:n_val], perm[n_val:]


def load(name: str):
    tr = panel_data.load_split(name, "train")
    te = panel_data.load_split(name, "test")
    hf = te["hf_fid"]
    lf_rung = max(tr["lf_fids"])
    grid = tuple(tr["grid_shape_by_fid"][hf])
    lf_grid = tuple(tr["grid_shape_by_fid"][lf_rung])
    Y = np.asarray(tr["field_by_fid"][hf], dtype=np.float64)
    LF_up = panel_data.copylf_prediction(tr, name)[: Y.shape[0]]
    return grid, lf_grid, Y, LF_up


def anatomy(fl, fr, masks, wcol, n_fit, k_cut, tol):
    num = (fr * np.conj(fl)).sum(axis=0)
    den = (np.abs(fl) ** 2).sum(axis=0)
    numR = (np.abs(fr) ** 2).sum(axis=0)
    zm = None if k_cut is None else (radial_k((fl.shape[1], (fl.shape[2] - 1) * 2)) >= k_cut)
    Tfull = solve(num, den, 0.0, zm)
    out = []
    e_lf, e_r = (den * wcol).sum(), (numR * wcol).sum()
    for b, m in enumerate(masks):
        s_num = (np.abs(num) * wcol)[m].sum()
        s_den = (den * wcol)[m].sum()
        s_R = (numR * wcol)[m].sum()
        ew = float(s_num / max(s_den, 1e-300))
        sg = float((np.real(num) * wcol)[m].sum() / max(s_den, 1e-300))
        uw = float(np.abs(Tfull)[m].mean()) if np.any(m) else float("nan")
        if ew > tol:
            v = "TRUE_AMPLIFICATION"
        elif sg <= -tol:
            v = "CANCELLER"
        elif uw > tol:
            v = "DISPERSION_ARTEFACT"
        else:
            v = "OK"
        out.append({
            "band": b + 1,
            "unweighted_mean_absT": uw,
            "energy_weighted_absT": ew,
            "signed_aggregate_T": sg,
            "coherence": float(s_num / np.sqrt(max(s_den * s_R, 1e-300))),
            "coherence_chance_level": float(1.0 / np.sqrt(max(n_fit, 1))),
            "lf_energy_share": float(s_den / max(e_lf, 1e-300)),
            "residual_energy_share": float(s_R / max(e_r, 1e-300)),
            "n_modes": int(m.sum()),
            "n_modes_zero_lf_power": int((m & (den <= 1e-20)).sum()),
            "verdict": v,
        })
    return out, num, den


def heldout_rho(fr_ho, fl_ho, T, wcol):
    resid = fr_ho - fl_ho * T[None, :, :]
    er = (np.abs(resid) ** 2 * wcol[None]).sum()
    et = (np.abs(fr_ho) ** 2 * wcol[None]).sum()
    return float(1.0 - er / max(et, 1e-300))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--datasets", required=True, help="comma-list of dataset names")
    ap.add_argument("--seeds", default="0", help="comma-list of split seeds")
    ap.add_argument("--holdout-frac", type=float, default=0.2)
    ap.add_argument("--n-bands", type=int, default=4)
    ap.add_argument("--amplify-tol", type=float, default=1.0)
    ap.add_argument("--k-cut", default="ladder",
                    help="'ladder' (k_nyq_hf * N_LF/N_HF), 'none', or a float")
    ap.add_argument("--ridge-ladder", default="0,1e-9,1e-6,1e-4,1e-2",
                    help="comma-list of ridge candidates to price")
    ap.add_argument("--enumerate-folds", action="store_true",
                    help="enumerate ALL C(Ntr, n_fit) fit sets (small Ntr only)")
    ap.add_argument("--max-folds", type=int, default=200)
    ap.add_argument("--diag-root", default=None,
                    help="cross-check against shipped diags in this dir")
    ap.add_argument("--diag-pattern", default="diag_{ds}_e200_s{seed}.json")
    ap.add_argument("--diag-key", default="lsi_repair.T_band_mean_abs_reg")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    seeds = [int(s) for s in a.seeds.split(",") if s.strip() != ""]
    ladder = [float(v) for v in a.ridge_ladder.split(",") if v.strip() != ""]
    report = {"_tool": "transfer_gain_anatomy.py", "_args": vars(a), "datasets": {}}
    worst_seam, n_seam = 0.0, 0

    for name in [s for s in a.datasets.split(",") if s.strip() != ""]:
        grid, lf_grid, Y, LF_up = load(name)
        H, W = int(grid[0]), int(grid[1])
        masks, wcol, edges = band_masks(grid, a.n_bands)
        if a.k_cut == "none":
            k_cut = None
        elif a.k_cut == "ladder":
            k_cut = (min(H, W) / 2.0) * (min(lf_grid) / float(min(H, W)))
        else:
            k_cut = float(a.k_cut)
        zm = None if k_cut is None else (radial_k(grid) >= k_cut)
        R = Y - LF_up
        cell = {"grid": [H, W], "lf_grid": list(lf_grid), "k_cut": k_cut,
                "band_edges": edges, "n_train": int(Y.shape[0]), "seeds": {}}

        for seed in seeds:
            val_idx, fit_idx = split_fit_fold(Y.shape[0], seed, a.holdout_frac)
            fl = np.fft.rfft2(LF_up[fit_idx].reshape(-1, H, W))
            fr = np.fft.rfft2(R[fit_idx].reshape(-1, H, W))
            bands, num, den = anatomy(fl, fr, masks, wcol, len(fit_idx), k_cut,
                                      a.amplify_tol)
            fl_ho = np.fft.rfft2(LF_up[val_idx].reshape(-1, H, W))
            fr_ho = np.fft.rfft2(R[val_idx].reshape(-1, H, W))
            lad = []
            for lam in ladder:
                T = solve(num, den, lam, zm)
                lad.append({
                    "ridge": lam,
                    "band_unweighted_mean_absT": [
                        float(np.abs(T)[m].mean()) if np.any(m) else float("nan")
                        for m in masks],
                    "heldout_rho": heldout_rho(fr_ho, fl_ho, T, wcol),
                })
            min_pass = []
            for b in range(len(masks)):
                ok = [e["ridge"] for e in lad
                      if e["band_unweighted_mean_absT"][b] <= a.amplify_tol]
                min_pass.append(None if not ok else min(ok))
            cell["seeds"][str(seed)] = {
                "fit_idx": [int(v) for v in fit_idx],
                "n_fit": int(len(fit_idx)), "n_heldout": int(len(val_idx)),
                "bands": bands,
                "ridge_ladder": lad,
                "min_ridge_in_ladder_passing_tol_by_band": min_pass,
            }
            if a.diag_root:
                f = Path(a.diag_root) / a.diag_pattern.format(ds=name, seed=seed)
                if f.exists():
                    obj = json.load(open(f))
                    for k in a.diag_key.split("."):
                        obj = obj[k]
                    # the `bands` block is the ridge-0 anatomy; the shipped diag may
                    # have been fitted at a selected ridge, so report the best match
                    # over the ladder AND the ridge-0 deviation. A large ridge-0
                    # deviation with a tiny best-match one is NOT a seam failure —
                    # it identifies the ridge the card actually shipped.
                    cand = {0.0: [e["unweighted_mean_absT"] for e in bands]}
                    for e in lad:
                        cand[e["ridge"]] = e["band_unweighted_mean_absT"]
                    devs = {r: max(abs(x - y) for x, y in zip(obj, v))
                            for r, v in cand.items()}
                    best = min(devs, key=devs.get)
                    worst_seam = max(worst_seam, devs[best])
                    n_seam += 1
                    cell["seeds"][str(seed)]["diag_seam"] = {
                        "best_match_ridge": best,
                        "max_abs_dev_at_best_match": devs[best],
                        "max_abs_dev_at_ridge0": devs[0.0],
                    }

        if a.enumerate_folds:
            n_fit = len(split_fit_fold(Y.shape[0], seeds[0], a.holdout_frac)[1])
            combos = list(combinations(range(Y.shape[0]), n_fit))
            if len(combos) > a.max_folds:
                cell["fold_population"] = {
                    "skipped": f"{len(combos)} folds > --max-folds {a.max_folds}"}
            else:
                seed_sets = {str(s): sorted(int(v) for v in
                                            split_fit_fold(Y.shape[0], s,
                                                           a.holdout_frac)[1])
                             for s in seeds}
                per_band = {b: [] for b in range(len(masks))}
                for combo in combos:
                    idx = np.asarray(combo)
                    fl = np.fft.rfft2(LF_up[idx].reshape(-1, H, W))
                    fr = np.fft.rfft2(R[idx].reshape(-1, H, W))
                    T = solve((fr * np.conj(fl)).sum(axis=0),
                              (np.abs(fl) ** 2).sum(axis=0), 0.0, zm)
                    for b, m in enumerate(masks):
                        per_band[b].append(float(np.abs(T)[m].mean()))
                cell["fold_population"] = {
                    "n_fit": n_fit, "n_folds": len(combos),
                    "n_distinct_folds_drawn_by_the_seeds": len(
                        {tuple(v) for v in seed_sets.values()}),
                    "seed_fit_sets": seed_sets,
                    "unweighted_mean_absT_by_band": {
                        f"band{b+1}": {
                            "min": float(min(v)), "median": float(np.median(v)),
                            "max": float(max(v)),
                            "n_folds_above_tol": int(sum(1 for x in v
                                                         if x > a.amplify_tol)),
                        } for b, v in per_band.items()},
                }
        report["datasets"][name] = cell

    if n_seam:
        report["_diag_seam"] = {"legs_cross_checked": n_seam,
                                "max_abs_dev": worst_seam}

    # ── console ──────────────────────────────────────────────────────────
    for name, cell in report["datasets"].items():
        print(f"\n=== {name}  grid {cell['grid']} lf {cell['lf_grid']} "
              f"k_cut {cell['k_cut']}  Ntr {cell['n_train']}")
        for seed, s in cell["seeds"].items():
            print(f"  seed {seed}  n_fit={s['n_fit']} n_heldout={s['n_heldout']}"
                  + (f"  [diag seam {s['diag_seam']['max_abs_dev_at_best_match']:.3g}"
                     f" at ridge {s['diag_seam']['best_match_ridge']:g}]"
                     if "diag_seam" in s else ""))
            for b in s["bands"]:
                print(f"    b{b['band']}  unweighted |T| {b['unweighted_mean_absT']:9.4f} "
                      f"| ENERGY-wtd {b['energy_weighted_absT']:8.4f} "
                      f"| signed {b['signed_aggregate_T']:+8.4f} "
                      f"| coh {b['coherence']:.4f} (chance {b['coherence_chance_level']:.3f}) "
                      f"| LF energy {b['lf_energy_share']:.3e} -> {b['verdict']}")
            print(f"    ridge ladder (band unweighted |T| ; heldout rho):")
            for e in s["ridge_ladder"]:
                print(f"      lam={e['ridge']:<8g} "
                      f"{[round(v,4) for v in e['band_unweighted_mean_absT']]}  "
                      f"rho={e['heldout_rho']:.6f}")
            print(f"    min ridge in ladder passing tol {a.amplify_tol} by band: "
                  f"{s['min_ridge_in_ladder_passing_tol_by_band']}")
        if "fold_population" in cell:
            fp = cell["fold_population"]
            if "skipped" in fp:
                print(f"  fold population: {fp['skipped']}")
            else:
                print(f"  FOLD POPULATION: {fp['n_folds']} distinct {fp['n_fit']}-of-"
                      f"{cell['n_train']} fit sets; the seeds drew "
                      f"{fp['n_distinct_folds_drawn_by_the_seeds']} distinct")
                for b, v in fp["unweighted_mean_absT_by_band"].items():
                    print(f"    {b} unweighted |T| min/med/max "
                          f"{v['min']:.4f} / {v['median']:.4f} / {v['max']:.4f}"
                          f"  folds above tol: {v['n_folds_above_tol']}/{fp['n_folds']}")
    if n_seam:
        print(f"\nDIAG SEAM: {n_seam} legs cross-checked, max abs dev {worst_seam:.3g}")
    if a.out:
        Path(a.out).write_text(json.dumps(report, indent=1))
        print("wrote", a.out)


if __name__ == "__main__":
    main()
