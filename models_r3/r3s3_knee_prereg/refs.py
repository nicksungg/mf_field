"""Training-free floor arms, the frozen-floor seam check, and the round-3
anchor / min-claimable-effect resolution.

PROVENANCE. `rel_l2_per_sample`, `stats`, `standardize`, `nn_condition_pred`,
`floor_arms`, `zero_arm` and `seam_check_floors` are vendored BYTE-FOR-BYTE
(modulo the `R2S3B3_` -> `R3S3B3_` env prefix in error strings and docstrings)
from this stream's own round-2 family `models_r2/r2s3_coverage_panel/refs.py`
(branch `round2/exp-r2s3_lf_train_signal-B3`, commit
dfcd46c6b51b5fe0bd533b9c670a7cdbf9d13830). Verify with

    git show dfcd46c6:models_r2/r2s3_coverage_panel/refs.py

`rel_l2_mean` here is the round's ONE nRMSE definition
(`mffp_autoresearch/round2/eval/nrmse.py::nrmse` = mean over test samples of
||pred_i - y_i|| / ||y_i||), restated in-process so the floor arms and the
scored split are computed under the identical formula. `nRMSE` is the
backward-compatible aggregate ratio-of-sums that
`data_adapters.metrics.finalize_and_write` also writes.

The NN-in-condition definition is byte-equal to
`eval/make_floor_anchors.py::floors_for`: L2 nearest in per-dim
TRAIN-standardised condition space (sd == 0 -> 1.0), ties broken by the lowest
train index.

NEW IN THE B1 CARD (`r3s3_lf_value-B1`), all three from `recipe.env`:

1. `seam_check_anchor_affine` — the round-3 `affine_on_hf_train` anchor
   (`R3S3B3_ANCHORS_JSON`), program.md §2's mandatory reported arm for every ifc
   number. REPORTED, with a raise only far outside the measured seam; see the
   function docstring for why its tolerance is not `R3S3B3_FLOOR_TOL`.
2. `resolve_min_claimable_effect` — the mce resolution. Reported; nothing
   branches on it.
3. `target_scale_geometry` — the `R3S3B3_TARGET_SCALE_AUDIT` instrument.

VENDORED INTO CARD `r3s3_lf_value-B2` (family `models_r3/r3s3_row_efficiency`)
from `models_r3/r3s3_lf_channels/refs.py` @ commit
050806e0bdfce9144da4a7a9f523c3a2e97d6a69 (blob b95982efef46dec2495baa530f425d3cbd41faaf).
The file is byte-identical to that blob modulo (a) the mechanical
`R3S3B1_` -> `R3S3B3_` env-prefix rename in strings/docstrings and (b) exactly
one functional delta: `resolve_min_claimable_effect` gained the
`certified_r3` mode this card's `recipe.env.R3S3B3_MCE_MODE` selects (see that
function's docstring). Audit with

    git show 050806e0:models_r3/r3s3_lf_channels/refs.py | sed 's/R3S3B1_/R3S3B3_/g' | diff - refs.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

# Tolerance for the `affine_on_hf_train` anchor comparison. This is NOT
# `R3S3B3_FLOOR_TOL` (1e-9) and the difference is measured, not assumed.
#
# `mffp_autoresearch/round3/tools/make_round3_anchors.py::ifc_floors` reads the
# raw `benchmark_42/core/<ds>/{train,test}/fidelity_64/*.npy` arrays, which are
# stored float64. This family reads the same rows through the factory adapter
# `data_adapters/loaders.py`, which returns float32 (verified 2026-08-07). A
# 6-dof least-squares solve is sensitive to that one downcast: measured
# |in_run - anchor| = 2.778e-09 (ifc_poisson) and 2.550e-09 (ifc_heat) — above
# 1e-9, and identical for the `pinv` and `lstsq` estimators, i.e. an input-dtype
# seam and not an estimator difference. The training-free floors (`nn_condition`
# / `train_mean` / `zero`) are far less sensitive and DO reproduce inside 1e-9
# (measured 2.7e-10 worst case over the whole panel), which is why
# `seam_check_floors` keeps the strict card tolerance and RAISES.
#
# 1e-7 leaves ~36x headroom over the measured seam while still catching a moved
# estimator, a moved data root, or a different HF row set (all of which move the
# number by >= 1e-3 here).
ANCHOR_AFFINE_TOL = 1e-7


def rel_l2_per_sample(pred: np.ndarray, target: np.ndarray) -> np.ndarray:
    p = np.asarray(pred, dtype=np.float64).reshape(np.asarray(pred).shape[0], -1)
    t = np.asarray(target, dtype=np.float64).reshape(np.asarray(target).shape[0], -1)
    if p.shape != t.shape:
        raise SystemExit(f"shape mismatch in rel-L2: {p.shape} vs {t.shape}")
    den = np.linalg.norm(t, axis=1)
    if (den == 0).any():
        raise SystemExit("zero-norm target sample (eval/nrmse.py refuses these)")
    return np.linalg.norm(p - t, axis=1) / den


def stats(pred: np.ndarray, target: np.ndarray) -> dict:
    p = np.asarray(pred, dtype=np.float64).reshape(np.asarray(pred).shape[0], -1)
    t = np.asarray(target, dtype=np.float64).reshape(np.asarray(target).shape[0], -1)
    rel = rel_l2_per_sample(p, t)
    sse = float(((p - t) ** 2).sum())
    sty = float((t ** 2).sum())
    return {
        "nRMSE": float(np.sqrt(sse / max(sty, 1e-12))),
        "rel_l2_mean": float(rel.mean()),
        "rel_l2_std": float(rel.std(ddof=1)) if rel.size > 1 else 0.0,
        "n_samples": int(rel.size),
    }


def standardize(c_ref: np.ndarray, c_other: np.ndarray):
    """Per-dim standardisation from `c_ref` (eval/make_floor_anchors.py convention)."""
    c_ref = np.asarray(c_ref, dtype=np.float64)
    mu, sd = c_ref.mean(axis=0), c_ref.std(axis=0)
    sd = np.where(sd > 0, sd, 1.0)
    return ((c_ref - mu) / sd), ((np.asarray(c_other, dtype=np.float64) - mu) / sd), mu, sd


def nn_condition_pred(c_tr: np.ndarray, y_tr: np.ndarray, c_te: np.ndarray):
    """NN-in-condition floor prediction + the index histogram floors.json reports."""
    z_tr, z_te, _, _ = standardize(c_tr, c_te)
    d2 = ((z_te[:, None, :] - z_tr[None, :, :]) ** 2).sum(axis=2)
    nn_idx = d2.argmin(axis=1)                       # ties -> lowest train index
    uniq, counts = np.unique(nn_idx, return_counts=True)
    top = np.argsort(counts)[::-1][:5]
    hist = {str(int(uniq[i])): int(counts[i]) for i in top}
    return np.asarray(y_tr, dtype=np.float64)[nn_idx], hist, nn_idx


def floor_arms(c_tr: np.ndarray, y_tr: np.ndarray, c_te: np.ndarray, y_te: np.ndarray,
               suffix: str) -> dict:
    """`ref_train_mean{suffix}` / `ref_nn_condition{suffix}`."""
    y_tr = np.asarray(y_tr, dtype=np.float64)
    y_te = np.asarray(y_te, dtype=np.float64)
    nn_pred, hist, _ = nn_condition_pred(c_tr, y_tr, c_te)
    out = {
        f"ref_nn_condition{suffix}": stats(nn_pred, y_te),
        f"ref_train_mean{suffix}": stats(
            np.broadcast_to(y_tr.mean(axis=0), y_te.shape), y_te),
    }
    out[f"ref_nn_condition{suffix}"]["nn_index_hist_top5"] = hist
    out[f"ref_nn_condition{suffix}"]["n_train_rows"] = int(y_tr.shape[0])
    out[f"ref_train_mean{suffix}"]["n_train_rows"] = int(y_tr.shape[0])
    return out


def zero_arm(y_te: np.ndarray) -> dict:
    return {"ref_zero": stats(np.zeros_like(np.asarray(y_te, dtype=np.float64)), y_te)}


def seam_check_floors(dataset: str, full_arms: dict, zero: dict, floors_json,
                      tol: float) -> dict:
    """RAISE unless the `_full` floors reproduce `R3S3B3_FLOORS_JSON`.

    The frozen file (round 3: `state/anchors_repaired/floors.json`, recomputed
    after the ADR r3-0002 pfc box swap and the ADR r3-0003 allen_cahn trim) was
    computed by `eval/make_floor_anchors.py`; the train split is byte-identical
    in the stripped view (only TEST LF files are removed), so exact agreement is
    the expectation and disagreement means a loader / metric / convention seam
    has moved. Verified 2026-08-07 by this builder over all 5 scored datasets +
    pfc + the 3 guard datasets: worst |diff| 2.744e-10 < 1e-9.
    """
    path = Path(floors_json)
    if not path.exists():
        raise SystemExit(f"floors.json not found at {path} (R3S3B3_FLOORS_JSON)")
    frozen = json.loads(path.read_text())
    if dataset not in frozen:
        raise SystemExit(f"{dataset!r} has no entry in {path}")
    ref = frozen[dataset]
    checks = {}
    pairs = [
        ("nn_condition", full_arms["ref_nn_condition_full"]["rel_l2_mean"],
         float(ref["nn_condition"]["nrmse"])),
        ("train_mean", full_arms["ref_train_mean_full"]["rel_l2_mean"],
         float(ref["train_mean"]["nrmse"])),
        ("zero", zero["ref_zero"]["rel_l2_mean"], float(ref["zero"]["nrmse"])),
    ]
    for name, got, want in pairs:
        delta = abs(got - want)
        checks[name] = {"in_run": got, "frozen": want, "abs_diff": delta}
        if not (delta <= tol):
            raise SystemExit(
                f"floor seam check FAILED on {dataset} / {name}: in-run {got!r} vs "
                f"frozen {want!r} (|diff| {delta:.3e} > tol {tol:g}) — "
                "the floors, the loader or the metric moved; refusing to score")
    return {"floors_json": str(path), "tol": float(tol), "checks": checks,
            "frozen_certified_utc": frozen.get("_certified_utc"),
            "frozen_nrmse_def_hash": frozen.get("_nrmse_def_hash")}


def seam_check_anchor_affine(dataset: str, in_run_nrmse: float, anchors_json,
                             hf_rows_are_native_full: bool) -> dict:
    """Compare `ref_affine_on_hf_train` against `R3S3B3_ANCHORS_JSON`.

    The anchor file (`state/anchors/launch_anchors.json`) carries
    `ifc_floors_repaired.<ds>.affine_on_hf_train` for the two ifc datasets only,
    fitted on the FULL native HF train split (5 rows). The comparison is
    therefore only meaningful when this leg trained on exactly those rows; on a
    subsampled or `N_hf = 20` leg the check is reported as not-applicable rather
    than silently compared against a different row set.

    RAISES above `ANCHOR_AFFINE_TOL` (see the module-level constant for the
    measured float32-loader seam that makes `R3S3B3_FLOOR_TOL` unusable here).
    """
    path = Path(anchors_json)
    if not path.exists():
        raise SystemExit(f"anchors json not found at {path} (R3S3B3_ANCHORS_JSON)")
    anchors = json.loads(path.read_text())
    entry = (anchors.get("ifc_floors_repaired", {}).get(dataset, {})
             .get("affine_on_hf_train"))
    if entry is None:
        return {"performed": False, "anchors_json": str(path),
                "reason": f"no ifc_floors_repaired.{dataset}.affine_on_hf_train anchor "
                          "(the anchor file carries this arm for the ifc datasets only)"}
    if not hf_rows_are_native_full:
        return {"performed": False, "anchors_json": str(path),
                "anchor_nrmse": float(entry["nrmse"]), "in_run_nrmse": float(in_run_nrmse),
                "reason": "this leg's HF rows are not the anchor's full native train "
                          "split, so the two fits are on different rows"}
    delta = abs(float(in_run_nrmse) - float(entry["nrmse"]))
    if not (delta <= ANCHOR_AFFINE_TOL):
        raise SystemExit(
            f"affine anchor seam FAILED on {dataset}: in-run {in_run_nrmse!r} vs anchor "
            f"{entry['nrmse']!r} (|diff| {delta:.3e} > tol {ANCHOR_AFFINE_TOL:g}) — the "
            "estimator, the data root or the HF row set moved; refusing to score")
    return {
        "performed": True, "anchors_json": str(path), "tol": float(ANCHOR_AFFINE_TOL),
        "in_run_nrmse": float(in_run_nrmse), "anchor_nrmse": float(entry["nrmse"]),
        "abs_diff": float(delta), "anchor_skill": float(entry["skill"]),
        "anchor_oracle_affine_residual_nrmse": entry.get("oracle_affine_residual_nrmse"),
        "anchor_definition": entry.get("definition"),
        "note": "program.md (round 3) §2 affine-floor rule: an ifc claim that does not "
                "beat this fitted floor has learned nothing beyond linearity",
    }


def _mce_entry(dataset: str, path) -> dict:
    p = Path(path)
    if not p.exists():
        return {"available": False, "reason": f"not found: {p}", "path": str(p)}
    nf = json.loads(p.read_text())
    entry = nf.get(dataset)
    if entry is None:
        return {"available": False, "path": str(p),
                "reason": f"no {dataset!r} entry in {p}"}
    return {"available": True, "path": str(p),
            "provisional": bool(nf.get("_provisional", True)),
            "certified_utc": nf.get("_certified_utc"),
            "min_claimable_effect": float(entry["min_claimable_effect"]),
            "definition": entry.get("min_claimable_effect_definition"),
            "source": nf.get("_source")}


def resolve_min_claimable_effect(dataset: str, r3_json, mode: str,
                                 r2_json=None) -> dict:
    """`tau_d` under `R3S3B3_MCE_MODE`. REPORTED — nothing in this family branches.

    CHANGED IN CARD `r3s3_lf_value-B2` (the only functional delta in this file
    against the vendored base `models_r3/r3s3_lf_channels/refs.py` @ 050806e0,
    blob b95982ef; everything else is byte-identical modulo the
    `R3S3B1_` -> `R3S3B3_` prefix rename):

      * `certified_r3` (this card's `recipe.env.R3S3B3_MCE_MODE`) reads the
        round-3 CERTIFIED file alone (`R3S3B3_NOISE_FLOOR_JSON` =
        `state/anchors_repaired/noise_floor.json`, `_certified_utc`
        2026-08-08). B1 ran under `max_r3provisional_r2certified` because the
        round-3 constants were still PROVISIONAL then and had to be maxed
        against round 2's certified ones; r3s4 has since certified them, so
        this card's recipe drops `R3S3B3_NOISE_FLOOR_R2_JSON` entirely (the
        card's `--env` set has no such key) and no round-2 file is consulted.
        The values this resolves to on this card's two datasets are
        `tau_rel` = 0.36124864423263325 (sharp__cahn_hilliard) and
        0.1640195793751628 (ifc_heat) — the constants card part 4 quotes.
      * `max_r3provisional_r2certified` is kept, unchanged, for the base
        family's semantics; it needs `r2_json` and raises without it.

    No threshold is ever manufactured: a dataset with no entry resolves to
    `available: False` with a reason.
    """
    if mode == "certified_r3":
        r3 = _mce_entry(dataset, r3_json)
        out = {"mode": mode, "r3_certified": r3,
               "available": bool(r3.get("available")),
               "source_file_is_provisional": r3.get("provisional"),
               "note": "round-3 CERTIFIED noise floor only; no round-2 file is "
                       "consulted under this mode (card r3s3_lf_value-B2 recipe.env "
                       "has no R3S3B3_NOISE_FLOOR_R2_JSON key)"}
        if r3.get("available"):
            out["min_claimable_effect"] = float(r3["min_claimable_effect"])
            out["selected_source"] = "r3_certified"
        else:
            out["reason"] = (f"{dataset!r} has no min_claimable_effect entry in "
                             f"{r3_json}; no threshold is manufactured here")
        return out
    if mode != "max_r3provisional_r2certified":
        raise SystemExit(f"unsupported R3S3B3_MCE_MODE={mode!r} "
                         "(this card's set: certified_r3, "
                         "max_r3provisional_r2certified)")
    if r2_json is None:
        raise SystemExit(
            "R3S3B3_MCE_MODE=max_r3provisional_r2certified needs a round-2 "
            "noise-floor file, but this card's recipe.env declares no "
            "R3S3B3_NOISE_FLOOR_R2_JSON key")
    r3 = _mce_entry(dataset, r3_json)
    r2 = _mce_entry(dataset, r2_json)
    vals = [e["min_claimable_effect"] for e in (r3, r2) if e.get("available")]
    out = {"mode": mode, "r3_provisional": r3, "r2_certified": r2,
           "available": bool(vals)}
    if vals:
        out["min_claimable_effect"] = float(max(vals))
        out["selected_source"] = ("r3_provisional"
                                  if r3.get("available")
                                  and r3["min_claimable_effect"] == max(vals)
                                  else "r2_certified")
    else:
        out["reason"] = (f"{dataset!r} has no min_claimable_effect entry in either "
                         "noise-floor file; no threshold is manufactured here")
    return out


def target_scale_geometry(y_flat: np.ndarray, scaler: float) -> dict:
    """The `R3S3B3_TARGET_SCALE_AUDIT` instrument. REPORTED, never a switch.

    WHAT THIS IS AND IS NOT. Card part 3 names `tools/target_scale_spread_audit.py`
    (ADR r2-0004) as a blocking pre-flight. That tool audits the geometry of a
    GLOBALLY-NORMALISED ADDITIVE RESIDUAL target `(HF - LF_up) / max|HF - LF_up|`
    and returns verdicts (`OUTLIER_DOMINATED` / `NEAR_ZERO_TARGETS`) about it.
    THIS FAMILY HAS NO RESIDUAL TARGET: it is a direct condition -> field decoder
    trained on `y / max|y|` per rung (`R3S3B3_SCALER=per_rung_max`), and no LF
    field is ever subtracted from anything. The tool's verdict is therefore not
    applicable to this family's objective, and this function does NOT restate it.

    What it does instead is compute the SAME statistics for the target this
    family actually optimises, per rung, so the audit answers the question the
    ADR was written to answer ("will one shared scaler per rung make the MSE
    degenerate here?") for the objective in front of it. The named tool is still
    run verbatim, once, as a pre-flight step of `scripts/01_train_eval.sh`.
    """
    y = np.asarray(y_flat, dtype=np.float64).reshape(np.asarray(y_flat).shape[0], -1)
    n = int(y.shape[0])
    per_sample_max = np.abs(y).max(axis=1)
    e = (y / max(float(scaler), 1e-300)) ** 2
    e_i = e.sum(axis=1)
    tot = float(e_i.sum())
    order = np.argsort(e_i)[::-1]
    k5 = max(1, int(np.ceil(0.05 * n)))
    med = float(np.median(per_sample_max))
    return {
        "n_samples": n,
        "scaler_per_rung_max": float(scaler),
        "median_per_sample_max_abs": med,
        "scaler_over_median_per_sample_max": float(scaler) / max(med, 1e-300),
        "median_normalised_target_max": med / max(float(scaler), 1e-300),
        "per_sample_max_abs_max_over_median": float(per_sample_max.max()) / max(med, 1e-300),
        "per_sample_max_abs_p99_over_median": float(
            np.percentile(per_sample_max, 99)) / max(med, 1e-300),
        "energy_share_top1": float(e_i[order[0]] / max(tot, 1e-300)),
        "energy_share_top5pct": float(e_i[order[:k5]].sum() / max(tot, 1e-300)),
        "effective_n_samples_of_mse": float(tot ** 2 / max(float((e_i ** 2).sum()), 1e-300)),
        "definition": "statistics of tools/target_scale_spread_audit.py applied to THIS "
                      "family's actual normalised target y / max|y| (per rung), not to a "
                      "residual target — this family has none; reported, never a switch",
    }
