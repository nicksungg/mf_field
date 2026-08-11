"""The five-rung emulator-ceiling ladder: statistics, units, and clause logic.

Card `r3s2_field_reach-B3`. Nothing in this module trains anything -- it turns
per-leg rung nRMSEs into the card's registered statistics and evaluates the four
clauses. It is separated from `smoke_eval.py` so the clause arithmetic can be
read (and unit-checked) without reading the training loop.

RUNGS (card part 3, verbatim; `R3S2B3_RUNGS`)

  R0_absent     condition -> HF at the matched 300-epoch budget. THE NO-LF
                DENOMINATOR: without it the ceiling ratio has no denominator to
                be read against (prior-art D3, an established absence).
  R1_predicted  condition -> pseudo-LF emulator -> convention lift -> frozen
                corrector -> HF. The DEPLOYED route.
  R1b_degraded  pseudo-LF lifted, corrector removed (B2's A7 analogue).
  R2_oracle     REAL LF of the held-out rows -> the same frozen corrector -> HF.
                THE CEILING. NOT deployable (`R3S2B3_ORACLE_NONDEPLOYABLE=1`).
  R2b_copylf    real LF of the held-out rows, convention lift only, 0 parameters.

Only `R3S2B3_TEST_SPLIT_ARMS` (R0, R1, R1b) are additionally evaluated on the
stripped test split; the two real-LF rungs exist on held-out TRAIN rows alone.

STATISTICS (`R3S2B3_STATS`), per cell per leg

  phi_ceil = 1 - nRMSE(R2)/nRMSE(R0)     what the route could EVER buy
  phi_real = 1 - nRMSE(R1)/nRMSE(R0)     what it DOES buy
  rho      = phi_real / phi_ceil          realization fraction
  E_est    = nRMSE(R2)                    estimator term
  E_hall   = nRMSE(R1) - nRMSE(R2)        hallucination term

UNITS (`R3S2B3_REPORT_UNITS = film_skill,fractional_error_reduction`)
Batch-3 clause rule 1: success clauses register against the CERTIFIED
FILM-TRANSFER baseline (`state/anchors/film_denominator.json`), in film units.
Copy-LF is not a target (operator directive 2026-08-10).

    skill_film(arm) = nRMSE(arm) / nrmse_film_mean(cell)

THRESHOLDS -- both are DERIVED from the certified floors, never typed in:

    tau_film(cell) = tau_rel(cell) * c_ds(cell)
        tau_rel is a copy-LF-referenced skill threshold and `c_ds` is the
        film_denominator's own exact converter (`skill_film = skill_copylf *
        c_ds`), so this is the certified floor expressed in the clause's units.
        Reproduces the card's quoted 0.076103 / 0.045486 / 0.021736 / 0.562718.

    tau_phi(cell)  = tau_rel(cell) / skill_level_used_for_tau_abs(cell)
        phi is a FRACTIONAL error reduction, so its floor is the certified
        threshold divided by the certifier's own skill level on that cell.
        Reproduces the card's quoted 0.07921 / 0.05128 / 0.02741 / 0.13347.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

RUNGS = ("R0_absent", "R1_predicted", "R1b_degraded", "R2_oracle", "R2b_copylf")
DEPLOYABLE = ("R0_absent", "R1_predicted", "R1b_degraded")
NONDEPLOYABLE = ("R2_oracle", "R2b_copylf")

RUNG_ROLE = {
    "R0_absent": ("condition -> HF at the matched budget; THE NO-LF DENOMINATOR "
                  "(prior-art D3: no retrieved source supplies one)"),
    "R1_predicted": "the deployed pseudo-LF route (frozen corrector)",
    "R1b_degraded": "pseudo-LF lifted, corrector removed (B2 A7 analogue)",
    "R2_oracle": ("REAL LF of the held-out TRAIN rows through the SAME frozen "
                  "corrector -- the ceiling. NON-DEPLOYABLE (immutable #9)"),
    "R2b_copylf": "real LF, convention lift only, zero parameters",
}


class LadderError(RuntimeError):
    """A ladder statistic could not be formed without inventing something."""


def _f(x):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def leg_stats(nr: dict) -> dict:
    """`{rung: nRMSE}` on ONE leg -> the card's five statistics."""
    r0, r1, r2 = _f(nr.get("R0_absent")), _f(nr.get("R1_predicted")), _f(nr.get("R2_oracle"))
    phi_ceil = (1.0 - r2 / r0) if (r0 not in (None, 0.0) and r2 is not None) else None
    phi_real = (1.0 - r1 / r0) if (r0 not in (None, 0.0) and r1 is not None) else None
    rho = (phi_real / phi_ceil) if (phi_ceil not in (None, 0.0)
                                    and phi_real is not None) else None
    e_est = r2
    e_hall = (r1 - r2) if (r1 is not None and r2 is not None) else None
    denom = ((e_hall + e_est) if (e_hall is not None and e_est is not None) else None)
    return {
        "phi_ceil": phi_ceil, "phi_real": phi_real, "rho": rho,
        "E_est": e_est, "E_hall": e_hall,
        "E_hall_fraction": ((e_hall / denom) if denom not in (None, 0.0) else None),
    }


# ── the certified references ─────────────────────────────────────────────


def load_film(path: Path, dataset: str) -> dict:
    """The ADR r3-0006 film-transfer denominator entry for `dataset`, or a
    recorded MISS. Batch-3 clause rule 1 makes this the clause unit."""
    p = Path(path)
    if not p.exists():
        return {"available": False, "reason": f"film denominator json not found: {p}"}
    entry = (json.loads(p.read_text()).get("datasets") or {}).get(dataset)
    if not isinstance(entry, dict):
        return {"available": False, "reason": f"{dataset!r} absent from {p}"}
    return {
        "available": True, "_source": str(p),
        "nrmse_film_mean": _f(entry.get("nrmse_film_mean")),
        "nrmse_film_ci95": entry.get("nrmse_film_ci95"),
        "c_ds": _f(entry.get("c_ds")),
        "ref_copylf": _f(entry.get("ref_copylf")),
        "adr": "r3-0006 (film-transfer denominator; batch-3 clause rule 1)",
    }


def load_floor(path: Path, dataset: str) -> dict:
    """The certified `min_claimable_effect` block, plus the two DERIVED
    thresholds. A cell with no certified mce ships REPORT-ONLY (registration
    predicate leg ii) -- it is never given a provisional one here."""
    p = Path(path)
    if not p.exists():
        return {"certified": False, "reason": f"noise floor json not found: {p}"}
    entry = json.loads(p.read_text()).get(dataset)
    if not isinstance(entry, dict):
        return {"certified": False,
                "reason": (f"{dataset!r} has NO certified min_claimable_effect in {p} "
                           "(the certified set covers 5 cells as of 2026-08-08; "
                           "ADR r3-0005 restored pfc on 2026-08-10 without re-certifying "
                           "its mce)")}
    mce = _f(entry.get("min_claimable_effect"))
    tau_rel = _f(entry.get("tau_rel"))
    skill_level = _f(entry.get("skill_level_used_for_tau_abs"))
    return {
        "certified": mce is not None, "_source": str(p),
        "min_claimable_effect": mce, "tau_rel": tau_rel,
        "tau_abs": _f(entry.get("tau_abs")),
        "seed_mce": _f(entry.get("seed_mce")),
        "skill_level_used_for_tau_abs": skill_level,
        "provisional_min_claimable_effect": _f(entry.get("provisional_min_claimable_effect")),
        "_provisional_note": ("state/anchors_repaired/noise_floor.json is PROVISIONAL "
                              "(program.md §3); r3s4 re-certifies before adjudication"),
    }


def thresholds(film: dict, floor: dict) -> dict:
    """`tau_film` and `tau_phi`, both DERIVED (see the module docstring)."""
    tau_rel = floor.get("tau_rel")
    c_ds = film.get("c_ds")
    lvl = floor.get("skill_level_used_for_tau_abs")
    tau_film = (tau_rel * c_ds) if (tau_rel is not None and c_ds is not None) else None
    tau_phi = (tau_rel / lvl) if (tau_rel is not None and lvl not in (None, 0.0)) else None
    return {
        "tau_film": tau_film, "tau_phi": tau_phi,
        "tau_rel": tau_rel, "c_ds": c_ds, "skill_level": lvl,
        "derivation": {
            "tau_film": "tau_rel * c_ds  (c_ds is film_denominator.json's exact converter)",
            "tau_phi": ("tau_rel / skill_level_used_for_tau_abs  (phi is a fractional "
                        "error reduction, so its floor is the certified threshold "
                        "divided by the certifier's skill level on the cell)"),
        },
    }


def skill_film(nrmse, film: dict):
    d = film.get("nrmse_film_mean")
    v = _f(nrmse)
    return (v / d) if (v is not None and d not in (None, 0.0)) else None


# ── the four registered clauses ──────────────────────────────────────────


def _minmax(vals):
    vals = [v for v in vals if v is not None]
    return (min(vals), max(vals), len(vals)) if vals else (None, None, 0)


def clauses(legs: list, film: dict, tau: dict, floors_beat: dict,
            split_transfer: dict, tol_logratio: float) -> dict:
    """Evaluate C1-C4 over the FULL leg population (`R3S2B3_MIN_OVER_LEGS_CLAUSES`).

    Every bar is a `min` (C1) or a `min`/`max` (C2) over legs, so no threshold
    can sit inside its own statistic's spread -- batch-3 clause-hygiene rule 1,
    discharged by construction rather than by argument.
    """
    tau_film, tau_phi = tau.get("tau_film"), tau.get("tau_phi")

    # C1 -- hallucination term certified, in FILM units
    c1_legs = []
    for lg in legs:
        s1 = skill_film(lg["nrmse"].get("R1_predicted"), film)
        s2 = skill_film(lg["nrmse"].get("R2_oracle"), film)
        c1_legs.append(None if (s1 is None or s2 is None) else (s1 - s2))
    c1_min, c1_max, c1_n = _minmax(c1_legs)
    c1 = {"statistic": "min over legs of skill_film(R1) - skill_film(R2)",
          "min_over_legs": c1_min, "max_over_legs": c1_max, "n_legs_with_value": c1_n,
          "tau_film": tau_film,
          "fires": bool(c1_min is not None and tau_film is not None and c1_min > tau_film),
          "margin_over_tau": (None if (c1_min is None or tau_film is None)
                              else c1_min - tau_film),
          "per_leg": c1_legs}

    # C2 -- ceiling existence, the D3 drop/keep rule
    phi_legs = [lg["stats"].get("phi_ceil") for lg in legs]
    p_min, p_max, p_n = _minmax(phi_legs)
    if tau_phi is None or p_n == 0:
        verdict = "INDETERMINATE"
    elif p_max < tau_phi:
        verdict = "DROP"
    elif p_min > tau_phi:
        verdict = "KEEP-CANDIDATE"
    else:
        verdict = "INDETERMINATE"
    c2 = {"statistic": "max/min over legs of phi_ceil vs tau_phi",
          "min_over_legs": p_min, "max_over_legs": p_max, "n_legs_with_value": p_n,
          "tau_phi": tau_phi, "verdict": verdict, "per_leg": phi_legs,
          "rule": ("DROP if max phi_ceil < tau_phi; KEEP-CANDIDATE if min phi_ceil > "
                   "tau_phi; else INDETERMINATE (card C2 / prior-art D3)")}

    # C3 -- split-transfer LICENCE (a gate on the instrument, not on the result)
    c3 = dict(split_transfer)
    c3["tolerance_logratio"] = tol_logratio
    c3["rule"] = ("the two deployable rungs rank identically on H and on test at every "
                  "seed, and |log(nRMSE_H/nRMSE_test)(R1) - log(...)(R0)| <= "
                  f"{tol_logratio} (~3x the largest registered tau_phi). A cell failing "
                  "C3 ships its ceiling REPORT-ONLY.")

    # C4 -- floor arms, mandatory
    c4 = {"statistic": "R0 and R1 against the mandatory floor arms at matched fit-set size",
          "by_rung": floors_beat,
          "g5_band_disclosure": ("every nn_condition-priced margin carries the arm's "
                                 "fit-set noise band (G5 adoption, batch-3 clause rule 5)"),
          "matched_n_knob": "R3S2B3_FLOOR_MATCHED_N"}

    return {"C1_hallucination_term": c1, "C2_ceiling_existence": c2,
            "C3_split_transfer_licence": c3, "C4_floor_arms": c4}


def registration(dataset: str, scored: bool, floor: dict, clause_block: dict,
                 floors_beat: dict, hot_eligible: bool) -> dict:
    """`R3S2B3_REGISTRATION_PREDICATE = scored_and_certified_mce_and_not_floor_disqualified`.

    A per-cell unit REGISTERS iff (i) the cell is scored under the ADR r3-0007
    composition, (ii) it has a certified `min_claimable_effect` at registration
    time, and (iii) NEITHER deployable rung is floor-disqualified there.
    Otherwise it ships REPORT-ONLY -- the six cells run either way.
    """
    leg_i = bool(scored)
    leg_ii = bool(floor.get("certified"))
    disqualified = {}
    for rung in ("R0_absent", "R1_predicted"):
        tbl = (floors_beat or {}).get(rung) or {}
        beats = [v.get("model_beats_floor") for v in tbl.values() if isinstance(v, dict)]
        # "floor-disqualified" = beats NONE of the reported floor arms.
        disqualified[rung] = bool(beats) and not any(beats)
    leg_iii = not any(disqualified.values())
    registered = bool(leg_i and leg_ii and leg_iii and hot_eligible)
    reasons = []
    if not leg_i:
        reasons.append("cell is not scored under ADR r3-0007 (option C)")
    if not leg_ii:
        reasons.append(f"no certified min_claimable_effect: {floor.get('reason', 'absent')}")
    if not leg_iii:
        reasons.append(f"deployable rung floor-disqualified: {disqualified}")
    if not hot_eligible:
        reasons.append("HOT split used the proportional fallback (not a card protocol)")
    # C3 is a SEPARATE gate, not a leg of the predicate: a cell can REGISTER its
    # deployable-rung units and still owe its CEILING as report-only. Surfaced
    # here so the analyzer cannot miss the consequence the card states.
    c3 = (clause_block or {}).get("C3_split_transfer_licence") or {}
    c3_passes = c3.get("passes")
    return {
        "dataset": dataset, "registered": registered,
        "status": "REGISTERED" if registered else "REPORT-ONLY",
        "ceiling_report_only_due_to_C3": bool(c3_passes is not True),
        "c3_passes": c3_passes,
        "c3_note": ("card C3: a cell failing the split-transfer licence ships its "
                    "CEILING report-only. This voids the INSTRUMENT on that cell, not "
                    "the hypothesis, and does not by itself change the registration "
                    "status of the deployable-rung units."),
        "leg_i_scored": leg_i, "leg_ii_certified_mce": leg_ii,
        "leg_iii_not_floor_disqualified": leg_iii,
        "hot_split_eligible": bool(hot_eligible),
        "floor_disqualified_by_rung": disqualified,
        "reasons_if_report_only": reasons,
        "predicate": "scored_and_certified_mce_and_not_floor_disqualified",
        "adr": ("r3-0007 option C, executed 2026-08-10: scored panel = 4 sharp cells + "
                "ifc_heat; ifc_poisson report-only. All six cells RUN regardless."),
    }


def falsifier(legs: list, tau: dict) -> dict:
    """The card's registered falsification: `min` over legs of `rho` > 0.5 while
    `phi_ceil` > `tau_phi` on a cell means the route is NOT emulator-limited
    there, and the ceiling framing (with the D3 rule derived from it) fails."""
    tau_phi = tau.get("tau_phi")
    rho_min, _, rho_n = _minmax([lg["stats"].get("rho") for lg in legs])
    phi_min, _, _ = _minmax([lg["stats"].get("phi_ceil") for lg in legs])
    fired = bool(rho_min is not None and rho_min > 0.5
                 and phi_min is not None and tau_phi is not None and phi_min > tau_phi)
    return {"rho_min_over_legs": rho_min, "n_legs_with_rho": rho_n,
            "phi_ceil_min_over_legs": phi_min, "tau_phi": tau_phi,
            "cell_falsifies": fired,
            "rule": ("card `expected_falsification`: fires on >= 2 REGISTERED cells "
                     "with min-over-legs rho > 0.5 while phi_ceil > tau_phi. This is "
                     "the PER-CELL leg; the >= 2 count is panel-side.")}
