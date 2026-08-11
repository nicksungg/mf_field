"""FILM-UNIT reporting, the G5 fit-set band, the pinned tolerances, and the
mean-removed metric. Card `r3s3_lf_value-B3` CARDED CHANGE 4.

Batch-3 scope rule 1 (`state/batch3_scope_2026-08-10.md`, operator directive
2026-08-10): "Register success clauses against the certified film-transfer
baseline (`state/anchors/film_denominator.json`), in film units. Copy-LF is not
a target." The base family reported copy-LF skill; this card reports

    skill_film(ds) = nRMSE / nrmse_film_mean(ds)          (ADR r3-0006)
    tau_rel_film(ds) = tau_rel(ds) * c_ds                 (card `_adjudicability`)

beside every emitted statistic. `c_ds = ref_copylf / nrmse_film_mean` is the
exact converter recorded in the denominator file, so `skill_film =
skill_copylf * c_ds` identically; both are emitted and the identity is asserted.

Three further reporting obligations of this card, all pinned here from files or
from the operator's own recorded words, never from a builder's recollection:

  * `R3S3B3_G5_FITSET_BAND=1` — batch-3 scope rule 5 / the operator's G5
    adoption on `r3s4_audit-B2`: "any claim priced against an `nn_condition`
    best floor carries that band beside `tau_rel`". The band is a per-cell
    SD in `tau_rel` units and it exists for three cells only; the other cells
    get an explicit `null` with the reason, never a borrowed number.
  * `R3S3B3_FLOOR_TOLERANCES_JSON` — the installed F1 tolerance table and, for
    the `affine_on_hf_train` arm, the PINNED PER-ARM band (the install note is
    explicit that the arm "is NOT YET ADJUDICABLE under the installed
    per-dataset table" and must be read against its own band).
  * `R3S3B3_MEAN_REMOVED_REPORT=1` — the project's `rel-l2-is-level-dominated`
    trap: on near-uniform fields rel-L2 measures the constant offset. The
    convention is the benchmark_42 dataset cards' own ("after removing each
    sample's spatial mean"), applied to prediction and target and then scored
    with the round's ONE nRMSE definition, unchanged.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

# The operator's G5 adoption, `experiment_cards/r3s4_audit/batch_2/B2.json`
# key `orchestrator_adjudication_g5_2026_08_10`, quoted verbatim in (a) and (b):
#   (a) "the SYSTEMATIC matched-fit-set correction is +0.842+-0.028 (ch),
#        +0.408+-0.012 (ac), +0.023+-0.009 (fk), +0.349+-0.233 (ifc_poisson LOO),
#        +0.356+-0.265 (ifc_heat LOO) tau_rel"
#   (b) "The residual defect is the nn_condition arm's fit-set NOISE BAND
#        (sd 1.796/0.740/0.276 tau on ch/ac/fk gating arms): from this adoption
#        forward, any claim priced against an nn_condition best floor carries
#        that band beside tau_rel."
# No pfc row exists in either list. It is `null` here, not interpolated.
G5_FITSET_BAND_TAU_REL = {
    "sharp__cahn_hilliard": {"systematic": 0.842, "systematic_se": 0.028, "sd": 1.796},
    "sharp__allen_cahn_2d": {"systematic": 0.408, "systematic_se": 0.012, "sd": 0.740},
    "sharp__fisher_kpp_2d": {"systematic": 0.023, "systematic_se": 0.009, "sd": 0.276},
    "ifc_poisson": {"systematic": 0.349, "systematic_se": 0.233, "sd": None,
                    "estimator": "exhaustive leave-one-out (n_train_hf = 5)"},
    "ifc_heat": {"systematic": 0.356, "systematic_se": 0.265, "sd": None,
                 "estimator": "exhaustive leave-one-out (n_train_hf = 5)"},
}
G5_SOURCE = ("experiment_cards/r3s4_audit/batch_2/B2.json :: "
             "orchestrator_adjudication_g5_2026_08_10 (operator adoption, Eloise, "
             "2026-08-10); underlying artifact reanalysis_turn_2_repricing.json")

# ADR r3-0006 is the DENOMINATOR, never an arm of this card (card
# `recipe.base_family`: "NOT mf_fno_transfer_film (that is the ADR r3-0006
# DENOMINATOR, never an arm here)").
FILM_FAMILY = "mf_fno_transfer_film"


def _load(path, what: str) -> dict:
    p = Path(path)
    if not p.exists():
        raise SystemExit(f"{what} not found at {p}")
    return json.loads(p.read_text())


def mean_removed_nrmse(pred: np.ndarray, target: np.ndarray) -> dict:
    """nRMSE after removing each SAMPLE's spatial mean from pred and target.

    Convention: the benchmark_42 dataset cards' own level-domination diagnostic
    ("after removing each sample's spatial mean the copy error is ...", e.g.
    `benchmark_42/sharp/fisher_kpp_2d/README.md`), composed with the round's one
    nRMSE definition (`round2/eval/nrmse.py`), which is applied unchanged to the
    de-meaned pair. REPORTED ONLY — nothing in this family branches on it, and
    the SCORED number is always the raw one.
    """
    P = np.asarray(pred, dtype=np.float64)
    Y = np.asarray(target, dtype=np.float64)
    P = P.reshape(P.shape[0], -1)
    Y = Y.reshape(Y.shape[0], -1)
    Pc = P - P.mean(axis=1, keepdims=True)
    Yc = Y - Y.mean(axis=1, keepdims=True)
    den = np.linalg.norm(Yc, axis=1)
    ok = den > 0
    rel = np.full(den.shape, np.nan)
    rel[ok] = np.linalg.norm(Pc[ok] - Yc[ok], axis=1) / den[ok]
    raw_den = np.linalg.norm(Y, axis=1)
    raw = np.linalg.norm(P - Y, axis=1) / raw_den
    return {
        "definition": "mean_i ||(p_i - <p_i>) - (y_i - <y_i>)||_2 / ||y_i - <y_i>||_2, "
                      "<.> = the sample's spatial mean (benchmark_42 dataset-card "
                      "convention) composed with round2/eval/nrmse.py",
        "mean_removed_nRMSE": float(np.nanmean(rel)),
        "raw_nRMSE": float(raw.mean()),
        "ratio_mean_removed_over_raw": float(np.nanmean(rel) / raw.mean()),
        "n_zero_variance_targets": int((~ok).sum()),
        "target_level_energy_fraction": float(
            1.0 - (Yc ** 2).sum() / max((Y ** 2).sum(), 1e-300)),
        "reported_only": True,
    }


def film_block(dataset: str, film_json, noise_json, nrmse_value: float,
               copylf_reference: float = None) -> dict:
    """`skill_film`, `tau_rel_film`, and the ADR r3-0006 denominator provenance."""
    film = _load(film_json, "R3S3B3_FILM_DENOM_JSON")
    noise = _load(noise_json, "R3S3B3_NOISE_FLOOR_JSON")
    cell = film.get("datasets", {}).get(dataset)
    if cell is None:
        return {"performed": False,
                "reason": f"{dataset} has no cell in {film_json}; no film denominator "
                          "exists, so no film-unit statement is made for it"}
    den = float(cell["nrmse_film_mean"])
    c_ds = float(cell["c_ds"])
    tau_rel = noise.get(dataset, {}).get("tau_rel")
    out = {
        "performed": True,
        "adr": "r3-0006 (film-transfer denominator); batch-3 scope rule 1",
        "denominator_family": FILM_FAMILY,
        "denominator_role": "DENOMINATOR ONLY — never an arm of this card",
        "nrmse_film_mean": den,
        "nrmse_film_per_seed": cell.get("nrmse_film_per_seed"),
        "nrmse_film_ci95": cell.get("nrmse_film_ci95"),
        "c_ds": c_ds,
        "skill_film": float(nrmse_value) / den,
        "tau_rel": tau_rel,
        "tau_rel_film": (float(tau_rel) * c_ds) if tau_rel is not None else None,
        "tau_rel_certified": tau_rel is not None,
    }
    if tau_rel is None:
        out["conditional_adjudication"] = (
            f"NO certified tau_rel exists for {dataset} in {noise_json}. Card "
            "`_cell_roles`: this cell is registered CONDITIONALLY and is adjudicated "
            "only if a certified tau_rel exists at analysis time; otherwise it is "
            "reported with its film-unit margin and an explicit non-adjudication "
            "flag. No threshold is invented here.")
    if copylf_reference:
        skill_copylf = float(nrmse_value) / float(copylf_reference)
        out["skill_copylf"] = skill_copylf
        out["skill_identity_check"] = {
            "skill_copylf_times_c_ds": skill_copylf * c_ds,
            "skill_film": out["skill_film"],
            "abs_diff": abs(skill_copylf * c_ds - out["skill_film"]),
            "note": "c_ds = ref_copylf / nrmse_film_mean, so the two agree exactly up "
                    "to float rounding; a divergence means the leg's copy-LF reference "
                    "is not the one the denominator file was built against"}
    return out


def g5_band(dataset: str) -> dict:
    """The `nn_condition` fit-set noise band that must accompany any floor-priced
    statement (batch-3 scope rule 5)."""
    e = G5_FITSET_BAND_TAU_REL.get(dataset)
    if e is None:
        return {"performed": True, "band_tau_rel": None,
                "reason": f"the operator's G5 adoption records no fit-set band for "
                          f"{dataset}; it is NOT interpolated from the other cells",
                "source": G5_SOURCE}
    return {"performed": True, "units": "tau_rel",
            "systematic_correction_tau_rel": e["systematic"],
            "systematic_correction_se_tau_rel": e["systematic_se"],
            "band_tau_rel": e["sd"],
            "estimator": e.get("estimator", "subset bootstrap over fit sets"),
            "direction": "the matched-fit-set correction always makes the reference "
                         "arm WORSE, so a model margin priced against it WIDENS",
            "rule": "any claim priced against an nn_condition best floor carries this "
                    "band beside tau_rel (operator adoption, 2026-08-10)",
            "source": G5_SOURCE}


def tolerance_block(dataset: str, tolerances_json) -> dict:
    """The installed F1 tolerance + the pinned per-arm `affine_on_hf_train` band."""
    tol = _load(tolerances_json, "R3S3B3_FLOOR_TOLERANCES_JSON")
    note_path = Path(tolerances_json).with_name("floor_tolerances_install_note.json")
    note = json.loads(note_path.read_text()) if note_path.exists() else {}
    return {
        "floor_tolerances_json": str(tolerances_json),
        "dataset_tolerance": tol.get("tolerances", {}).get(dataset),
        "arms_covered": tol.get("_arms"),
        "affine_arm_pinned_band": note.get("_affine_arm_band_pinned", {}).get(dataset),
        "affine_arm_declaration": note.get("_affine_arm_declaration"),
        "rule": "F1-class floor reproductions adjudicate against dataset_tolerance for "
                "nn_condition / train_mean / zero, and against affine_arm_pinned_band "
                "for affine_on_hf_train (install note: the affine arm is NOT "
                "adjudicable under the dataset-level table)",
    }
