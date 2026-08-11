"""`R3S2_TARGET_SCALER_PREFLIGHT = pfc_per_sample_if_outlier_dominated`.

ROUND-2 ADR 0004 §2 (carried into round 3 by program.md §5, "round-2 §12
methodological rules apply verbatim... target-scaler pre-flight"):

    "the pre-flight audit (`tools/target_scale_spread_audit.py`, verified
     2026-07-30 -- its verdicts isolate exactly the two failing datasets) is now
     mandatory on model cards training on helmholtz or pfc, with per-sample
     normalisation required on an OUTLIER_DOMINATED / NEAR_ZERO_TARGETS verdict"

The defect the rule exists to prevent, measured on round-1 `lf_resid_fno`:
pfc's GLOBAL residual scaler was 7.95e4x the median per-sample scale, putting
the emitted-noise floor 8206x above truth. B2 declared the rule
`not_applicable` because pfc was not in its dataset list. B3 SCORES pfc
(ADR r3-0005), so the rule is live and this module implements it.

NO THRESHOLD IS INVENTED HERE. The statistics and the verdict logic below are
VERBATIM from `round2/tools/target_scale_spread_audit.py::one`, and the three
cut-offs are that tool's own argparse defaults:

    outlier_share = 0.5     energy share of the single worst sample
    near_zero     = 1e-3    median normalised target below which targets are 0
    spread        = 100.0   resid_norm max/median that flags WIDE_SPREAD

The one deliberate difference from the tool: the tool audits `HF - copyLF` built
by `panel_data.copylf_prediction`, whereas the corrector here normalises the
residual it is actually fitted on. The audit is therefore run on THIS run's
residual array, which is the quantity the scaler is applied to. Both the
verdict and the raw statistics are recorded either way, applied or not.
"""
from __future__ import annotations

import numpy as np

OUTLIER_SHARE = 0.5        # target_scale_spread_audit.py --outlier_share default
NEAR_ZERO = 1e-3           # target_scale_spread_audit.py --near_zero default
SPREAD = 100.0             # target_scale_spread_audit.py --spread default
# Round-2 ADR 0004 §2 names exactly two datasets; only pfc is in this card's list.
PREFLIGHT_DATASETS = ("sharp__phase_field_crystal_2d", "ext__helmholtz_2d")


def audit(resid: np.ndarray) -> dict:
    """Verbatim statistic set + verdict from `target_scale_spread_audit.py::one`."""
    r = np.asarray(resid, dtype=np.float64).reshape(int(np.asarray(resid).shape[0]), -1)
    n = int(r.shape[0])
    nrm = np.linalg.norm(r, axis=1)
    per_max = np.abs(r).max(axis=1)
    energy = nrm ** 2
    scaler = float(max(np.abs(r).max(), 1e-8))
    k5 = max(1, int(round(0.05 * n)))
    top = np.sort(energy)[::-1]
    e = {
        "n_samples": n,
        "resid_norm_median": float(np.median(nrm)),
        "resid_norm_max_over_median": float(nrm.max() / max(np.median(nrm), 1e-300)),
        "resid_norm_p99_over_median": float(
            np.percentile(nrm, 99) / max(np.median(nrm), 1e-300)),
        "scaler_global_max": scaler,
        "scaler_over_median_per_sample_max": float(scaler / max(np.median(per_max), 1e-300)),
        "median_normalised_target_max": float(np.median(per_max) / scaler),
        "energy_share_top1": float(top[0] / max(energy.sum(), 1e-300)),
        "energy_share_top5pct": float(top[:k5].sum() / max(energy.sum(), 1e-300)),
        "effective_n_samples_of_mse": float(
            energy.sum() ** 2 / max((energy ** 2).sum(), 1e-300)),
    }
    e["effective_n_fraction"] = e["effective_n_samples_of_mse"] / n
    outlier = e["energy_share_top1"] > OUTLIER_SHARE or e["effective_n_fraction"] < 0.05
    nearzero = e["median_normalised_target_max"] < NEAR_ZERO
    wide = e["resid_norm_max_over_median"] > SPREAD
    e["verdict"] = ("BOTH" if outlier and nearzero else
                    "OUTLIER_DOMINATED" if outlier else
                    "NEAR_ZERO_TARGETS" if nearzero else
                    "WIDE_SPREAD" if wide else "OK")
    e["thresholds"] = {"outlier_share": OUTLIER_SHARE, "near_zero": NEAR_ZERO,
                       "spread": SPREAD,
                       "_provenance": "round2/tools/target_scale_spread_audit.py defaults"}
    return e


def decide(dataset_name: str, resid: np.ndarray, knob: str) -> dict:
    """Run the pre-flight and decide the residual scaler.

    Returns `{'per_sample': bool, 'scaler': (n,1) or scalar, 'audit': {...}}`.
    Per-sample normalisation fires ONLY on a dataset the rule names AND on an
    OUTLIER_DOMINATED / NEAR_ZERO_TARGETS / BOTH verdict; every other case keeps
    the base family's global max-abs scaler and says so.
    """
    knob = str(knob).strip()
    if knob != "pfc_per_sample_if_outlier_dominated":
        raise RuntimeError(
            "R3S2_TARGET_SCALER_PREFLIGHT is fixed by the recipe to "
            f"'pfc_per_sample_if_outlier_dominated'; got {knob!r}")
    in_scope = dataset_name in PREFLIGHT_DATASETS
    a = audit(resid)
    fire = bool(in_scope and a["verdict"] in ("OUTLIER_DOMINATED", "NEAR_ZERO_TARGETS",
                                              "BOTH"))
    r = np.asarray(resid, dtype=np.float64)
    r = r.reshape(r.shape[0], -1)
    if fire:
        scaler = np.maximum(np.abs(r).max(axis=1, keepdims=True), 1e-8)
    else:
        scaler = float(max(np.abs(r).max(), 1e-8))
    return {
        "per_sample": fire,
        "scaler": scaler,
        "knob": knob,
        "dataset_in_rule_scope": in_scope,
        "rule_scope": list(PREFLIGHT_DATASETS),
        "audit": a,
        "applied": ("per-sample max-abs normalisation (round-2 ADR 0004 §2: required "
                    "on an OUTLIER_DOMINATED/NEAR_ZERO_TARGETS verdict)" if fire else
                    "global max-abs scaler (base family) -- the rule did not fire"),
        "adr": "round-2 ADR 0004 §2, carried into round 3 by program.md §5",
    }


def scaler_summary(dec: dict) -> dict:
    s = dec["scaler"]
    if isinstance(s, np.ndarray):
        return {"mode": "per_sample", "n": int(s.shape[0]),
                "min": float(s.min()), "median": float(np.median(s)), "max": float(s.max()),
                "max_over_median": float(s.max() / max(float(np.median(s)), 1e-300))}
    return {"mode": "global", "value": float(s)}
