"""The D2 instrument repair: select the LSI regularisation on the EMULATOR's
held-out output, not on real LF.

THIS IS AN INSTRUMENT FOOTNOTE, NOT THE IDEA (prior-art verdict D2, quoted on
the card: `preempted (cite)`, "usable ONLY as an instrument repair, exactly like
batch 2's E1. Presenting it as the idea is a rebadge"). What is open is "only
the numbers".

THE COVARIATE SHIFT BEING FIXED
-------------------------------
B2 fitted AND selected the transfer function's ridge on REAL LF, then fed the
frozen operator PSEUDO-LF at deployment. The selection input therefore had a
different spectrum from the deployment input, and the band-deletion that
followed cost the ifc_poisson gap (B2 F9/F10). Here the transfer function is
still FITTED on real LF -- the corrector stays a declared frozen real-LF
sub-component, role (a) -- but its two hyperparameters

    ridge  in  `S6_LSI_RIDGE_GRID`   = {0, 1e-10, 3.162e-10, 1e-9, 1e-8, 1e-7,
                                        1e-6, 1e-4, 1e-2, 1e-1}
    band   in  `S6_LSI_BANDLIMIT_GRID` = {on, off}

are chosen by an EXACTLY out-of-sample criterion evaluated on the emulator's own
held-out pseudo-LF output (`R3S2B3_CORRECTOR_SELECT_ON = emulator_heldout_output`).
The identical selection driven by real LF is computed as the PAIRED comparand
(`R3S2B3_CORRECTOR_SELECT_COMPARAND = real_lf`), so the repair is attributable.

GRID PROVENANCE (card part 3, verbatim -- both ends justified, clause-hygiene
rule 3 "any pre-registered repair grid must justify its FLOOR, not only its
ceiling"):
  FLOOR 1e-10  -- B2 F2 measured the ridge actually needed at 5.264e-10-5.707e-10,
                  so the floor must sit a decade below it.
  CEILING 1e-1 -- B2 F1 measured loo_sse(0.1)/loo_sse(0) = 122-160 on ifc_poisson.

`S6_LSI_KCUT_SOURCE = ladder_shape_ratio_adr_r2_0001`: the band-limit's k_cut is
the LF Nyquist derived from the rung shape ratio, unchanged from B2
(`lsi_filter.kcut_from_ladder`). `S6_LSI_BANDLIMIT_MODE = zero_above_kcut`.
"""
from __future__ import annotations

import numpy as np

import lsi_filter as lsilib


class D2SelectError(RuntimeError):
    """The selection could not be run without inventing something."""


def _fit_T(LF_fit, R_fit, grid, ridge, k_cut_or_none):
    """Fit T on REAL LF at a given (ridge, band-limit). The fit input never
    changes -- only the two hyperparameters do.

    `lsi_filter._solve` is the EXACT arithmetic of `lsi_filter.fit_transfer`
    (that module factored it out precisely so the two paths cannot drift), with
    the band-limit applied as `S6_LSI_BANDLIMIT_MODE = zero_above_kcut`.
    """
    fl, fr = lsilib._accumulators(LF_fit, R_fit, grid)
    num = (fr * np.conj(fl)).sum(axis=0)
    den = (np.abs(fl) ** 2).sum(axis=0)
    mask = (None if k_cut_or_none is None
            else lsilib.bandlimit_mask(grid, float(k_cut_or_none)))
    return lsilib._solve(num, den, float(ridge), mask)


def select(LF_real, LF_pseudo, Y, grid, sel_folds, ridge_grid, k_cut,
           bandlimit_grid=("on", "off"), select_on="emulator_heldout_output"):
    """Joint (ridge x band-limit) selection over `sel_folds`.

    `sel_folds` : [(fit_rows, sel_rows), ...] INSIDE the leg's fit set. The pairs
                  are disjoint by construction (`hot_split.plan`), which is what
                  makes the criterion exactly out of sample.
    `select_on` : 'emulator_heldout_output' -> the criterion reads `LF_pseudo`
                  on `sel_rows`; 'real_lf' -> it reads `LF_real` (the comparand).

    Returns the selection record; the caller fits the FINAL T on the leg's whole
    fit set at the selected pair.
    """
    ridges = lsilib.parse_ridge_grid(ridge_grid)
    bands = [str(b).strip().lower() for b in bandlimit_grid]
    for b in bands:
        if b not in ("on", "off"):
            raise D2SelectError(
                f"S6_LSI_BANDLIMIT_GRID entry {b!r} is not 'on'/'off' (recipe)")
    if not sel_folds:
        raise D2SelectError("no selection folds: the criterion would be in-sample")
    if select_on not in ("emulator_heldout_output", "real_lf"):
        raise D2SelectError(
            f"R3S2B3_CORRECTOR_SELECT_ON={select_on!r} is not one of "
            "{'emulator_heldout_output', 'real_lf'}")

    LF_sel_source = LF_pseudo if select_on == "emulator_heldout_output" else LF_real
    Hh, Ww = int(grid[0]), int(grid[1])
    masks = {"on": lsilib.bandlimit_mask(grid, float(k_cut)), "off": None}

    # Per fold, the fit accumulators and the selection-input spectrum are
    # INDEPENDENT of (ridge, band) -- they are computed once and the 10 x 2 grid
    # is then a closed-form sweep. This is a pure speed factoring: `_solve` is
    # `fit_transfer`'s own arithmetic, so the selected pair is identical to the
    # one a naive refit-per-combination loop would pick.
    prep, n_sel_total = [], 0
    for fit_rows, sel_rows in sel_folds:
        fit_rows = np.asarray(fit_rows, dtype=np.int64)
        sel_rows = np.asarray(sel_rows, dtype=np.int64)
        if len(np.intersect1d(fit_rows, sel_rows)):
            raise D2SelectError(
                "S6_LEAKAGE_TRIPWIRE: a selection fold overlaps its own fit rows "
                f"({sorted(set(fit_rows.tolist()) & set(sel_rows.tolist()))})")
        fl, fr = lsilib._accumulators(LF_real[fit_rows],
                                      Y[fit_rows] - LF_real[fit_rows], grid)
        LF_s = np.asarray(LF_sel_source[sel_rows], dtype=np.float64)
        prep.append({
            "num": (fr * np.conj(fl)).sum(axis=0),
            "den": (np.abs(fl) ** 2).sum(axis=0),
            "f_sel": np.fft.rfft2(LF_s.reshape(-1, Hh, Ww)),
            "LF_sel": LF_s,
            "Y_sel": np.asarray(Y[sel_rows], dtype=np.float64),
        })
        n_sel_total += int(len(sel_rows))

    table, best = [], None
    for b in bands:
        for lam in ridges:
            sse = 0.0
            for pr in prep:
                T = lsilib._solve(pr["num"], pr["den"], float(lam), masks[b])
                corr = np.fft.irfft2(pr["f_sel"] * T[None, :, :], s=(Hh, Ww)).reshape(
                    pr["LF_sel"].shape[0], -1)
                sse += float(((pr["Y_sel"] - (pr["LF_sel"] + corr)) ** 2).sum())
            row = {"ridge": float(lam), "bandlimit": b, "oos_sse": float(sse),
                   "n_sel_rows": n_sel_total}
            table.append(row)
            # Ties -> the earliest grid entry (band-limit 'on' first, then the
            # smallest ridge), which is the grid order the recipe declares.
            if best is None or row["oos_sse"] < best["oos_sse"]:
                best = row
    return {
        "selected_ridge": best["ridge"],
        "selected_bandlimit": best["bandlimit"],
        "selected_k_cut": (float(k_cut) if best["bandlimit"] == "on" else None),
        "selected_oos_sse": best["oos_sse"],
        "select_on": select_on,
        "criterion": ("exactly out-of-sample SSE of LF_sel + T*LF_sel vs HF on the "
                      "selection rows; T is always FITTED on REAL LF (role (a) frozen "
                      "sub-component) -- only the two hyperparameters are selected here"),
        "n_sel_folds": len(sel_folds),
        "ridge_grid": [float(v) for v in ridges],
        "bandlimit_grid": bands,
        "grid_floor_provenance": ("B2 F2: the ridge actually needed is 5.264e-10-5.707e-10, "
                                  "so the grid floor sits a decade below at 1e-10"),
        "grid_ceiling_provenance": ("B2 F1: loo_sse(0.1)/loo_sse(0) = 122-160 on "
                                    "ifc_poisson"),
        "table": table,
        "declared_role": ("INSTRUMENT REPAIR ONLY (prior-art D2 `preempted (cite)`): "
                          "'usable ONLY as an instrument repair... Presenting it as the "
                          "idea is a rebadge'. Nothing is claimed for it; the paired "
                          "real-LF-selected comparand makes it attributable."),
    }


def final_transfer(LF_real, Y, grid, fit_rows, sel: dict):
    """Fit the FINAL T on the leg's whole fit set at the selected pair."""
    fit_rows = np.asarray(fit_rows, dtype=np.int64)
    return _fit_T(LF_real[fit_rows], Y[fit_rows] - LF_real[fit_rows], grid,
                  sel["selected_ridge"], sel["selected_k_cut"])
