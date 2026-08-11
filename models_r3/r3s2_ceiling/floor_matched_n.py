"""`R3S2B3_FLOOR_MATCHED_N` and `R3S2B3_G5_BAND_DISCLOSURE`, computed.

WHY THIS MODULE EXISTS (code-review finding F2, build 89c9fb3d)
---------------------------------------------------------------
Two of the card's declared knobs shipped as labels rather than computations:

  * `R3S2B3_IFC_LOO_DISCLOSURE = enumerate_C5_4` and the `ifc:C5_4_loo` half of
    `R3S2B3_FLOOR_MATCHED_N` produced `hot_split.plan()["disclosure_legs"]` --
    five leg-ids and row counts -- that the run loop never iterated, so the
    "floor-matched disclosure variant" carried no nRMSE.
  * `R3S2B3_G5_BAND_DISCLOSURE = 1` had NO consumer anywhere in the family;
    `ladder.clauses` emitted the G5 band as a prose sentence beside `beat_table`
    margins that carried no sd.

Both are TRAINING-FREE quantities -- every mandatory floor arm is closed form --
so they are computed here at zero GPU cost inside the same job, and the knobs
name something that exists.

WHAT "MATCHED N" IS, PER CELL SHAPE (`R3S2B3_FLOOR_MATCHED_N`, verbatim)
------------------------------------------------------------------------
  `sharp:320`   the certified floors in `state/anchors_repaired/floors.json` are
                fit on all 400 HF train rows; the ladder's stages see the HOT
                plan's T = 320. The matched-n floor is therefore the SAME arm
                refit on T and scored on the same stripped test split. One
                matched fit set exists per (cell, seed) -- it IS T -- so the
                per-seed value is reported and the band across seeds is the
                analyzer's to assemble.
  `ifc:C5_4_loo` at n_train_hf = 5 a "matched" subset is not a sample question:
                the whole C(5,4) fold population is enumerated (5 folds), giving
                the exact fold RANGE. program.md §2's affine-floor rule makes
                that range mandatory beside every ifc number, and it is the same
                population `hot_split.plan()["disclosure_legs"]` declares.

THE G5 BAND. Batch-3 clause rule 5 / G5 adoption: a margin priced against a
training-free floor arm must carry that arm's own fit-set noise. Here that is the
sd of the matched-n fold population (ifc: exact over 5 folds) together with the
systematic matched-n correction `floor_matched - floor_full_fit`. Both are
reported in nRMSE units -- the units `floor_arms.beat_table` prices margins in --
and, where the film denominator is available, in film-skill units too.

ARM CONSTRUCTIONS are byte-identical to `round3/tools/fitset_matched_n_audit.py`
(itself verbatim from `tools/make_round3_anchors.py` / `r3s4_audit-B2
probes/d4_fitset.py`), so a number computed here is comparable to the certified
table without a convention argument. The nRMSE is the frozen round metric
(`round2/eval/nrmse.py`), imported, never re-implemented.

REPORT-ONLY: nothing here touches the scored prediction, the rung nRMSEs, or the
C1/C2/C3 statistics. It reads train/test arrays and returns a diag block.
"""
from __future__ import annotations

import numpy as np

from nrmse import nrmse as round_nrmse

ARMS_CLOSED_FORM = ("nn_condition", "train_mean", "zero", "affine_on_hf_train")


class FloorMatchedNError(RuntimeError):
    """A matched-n floor could not be computed without inventing something."""


# ── arm constructions (byte-identical to tools/fitset_matched_n_audit.py) ──

def standardize_cond(c_tr, c_te):
    mu, sd = c_tr.mean(axis=0), c_tr.std(axis=0)
    sd = np.where(sd > 0, sd, 1.0)
    return (c_tr - mu) / sd, (c_te - mu) / sd


def affine_fit(X, Y):
    A = np.hstack([X, np.ones((len(X), 1))])
    W, *_ = np.linalg.lstsq(A, Y, rcond=None)
    return lambda Xq: np.hstack([Xq, np.ones((len(Xq), 1))]) @ W


def arm_value(arm, c_tr, y_tr, c_te, y_te) -> float:
    if arm == "train_mean":
        return float(round_nrmse(np.broadcast_to(y_tr.mean(axis=0), y_te.shape), y_te))
    if arm == "nn_condition":
        z_tr, z_te = standardize_cond(c_tr, c_te)
        d2 = ((z_te[:, None, :] - z_tr[None, :, :]) ** 2).sum(axis=2)
        return float(round_nrmse(y_tr[np.argmin(d2, axis=1)], y_te))
    if arm == "affine_on_hf_train":
        return float(round_nrmse(affine_fit(c_tr, y_tr)(c_te), y_te))
    if arm == "zero":
        return float(round_nrmse(np.zeros_like(y_te), y_te))
    raise FloorMatchedNError(f"unknown closed-form floor arm {arm!r}")


def spread(vals) -> dict:
    v = np.asarray([x for x in vals if x is not None and np.isfinite(x)],
                   dtype=np.float64)
    if not len(v):
        return {"n": 0}
    return {"n": int(len(v)), "min": float(v.min()), "max": float(v.max()),
            "median": float(np.median(v)), "mean": float(v.mean()),
            "sd": (float(v.std(ddof=1)) if len(v) > 1 else 0.0)}


def _requested(matched_n_knob: str) -> dict:
    """Parse `R3S2B3_FLOOR_MATCHED_N` (`sharp:320,ifc:C5_4_loo`) verbatim."""
    out = {}
    for part in str(matched_n_knob).split(","):
        part = part.strip()
        if not part:
            continue
        k, _, v = part.partition(":")
        out[k.strip()] = v.strip()
    return out


# ── the C(5,4) disclosure legs (R3S2B3_IFC_LOO_DISCLOSURE) ───────────────

def disclosure_legs(plan: dict, c_tr, y_tr, c_te, y_te,
                    arms=ARMS_CLOSED_FORM) -> dict:
    """Score `plan["disclosure_legs"]` -- the legs the run loop does not walk.

    Both readings are reported, because they answer different questions:
      `arms_on_heldout_train_row`  matched to the ladder's own held-out-TRAIN
                                   rungs (the leg's 1 excluded row);
      `arms_on_test_split`         matched to C4, whose `beat_table` prices
                                   `mean_test` against floors on the test split.
    """
    disc = plan.get("disclosure_legs") or []
    if not disc:
        return {"applicable": False,
                "reason": (f"protocol {plan.get('protocol')} declares no disclosure "
                           "legs (R3S2B3_IFC_LOO_DISCLOSURE is scoped to the "
                           "enumerate_C5_3 cells)")}
    legs = []
    for d in disc:
        fit = np.asarray(d["fit_rows"], dtype=np.int64)
        hel = np.asarray(d["heldout"], dtype=np.int64)
        legs.append({
            "leg_id": d["leg_id"],
            "fit_rows": [int(v) for v in fit], "heldout_rows": [int(v) for v in hel],
            "n_fit_rows": int(len(fit)), "n_heldout": int(len(hel)),
            "arms_on_heldout_train_row": {
                a: arm_value(a, c_tr[fit], y_tr[fit], c_tr[hel], y_tr[hel])
                for a in arms},
            "arms_on_test_split": {
                a: arm_value(a, c_tr[fit], y_tr[fit], c_te, y_te) for a in arms},
        })
    return {
        "applicable": True,
        "knob": plan.get("disclosure_knob", "R3S2B3_IFC_LOO_DISCLOSURE"),
        "protocol": f"C({len(y_tr)},{legs[0]['n_fit_rows']})_loo",
        "n_legs": len(legs), "legs": legs,
        "fold_range_on_heldout_train_row": {
            a: spread([lg["arms_on_heldout_train_row"][a] for lg in legs]) for a in arms},
        "fold_range_on_test_split": {
            a: spread([lg["arms_on_test_split"][a] for lg in legs]) for a in arms},
        "affine_floor_rule": ("program.md §2: every ifc number is reported next to the "
                             "fitted `affine_on_hf_train` floor WITH its leave-one-out "
                             "fold range. That range is "
                             "`fold_range_on_test_split.affine_on_hf_train`; the "
                             "certified single-fit value is the C4 comparand."),
    }


# ── the matched-n floors + the G5 band (R3S2B3_G5_BAND_DISCLOSURE) ───────

def matched_n_band(plan: dict, dataset: str, matched_n_knob: str,
                   c_tr, y_tr, c_te, y_te, floors: dict, film: dict,
                   disclosure: dict, arms=ARMS_CLOSED_FORM) -> dict:
    """Refit the closed-form floor arms at the card's declared matched fit size
    and turn `R3S2B3_G5_BAND_DISCLOSURE` into numbers.

    `floors` is `floor_arms.collect(...)`'s block (the CERTIFIED full-fit table);
    nothing here overwrites it -- the matched value sits beside it with the
    systematic correction spelled out.
    """
    want = _requested(matched_n_knob)
    shape = ("ifc" if str(plan.get("protocol", "")).startswith("enumerate_C")
             else ("sharp" if plan.get("T") is not None else None))
    spec = want.get(shape) if shape else None
    film_c = None
    if isinstance(film, dict):
        film_c = film.get("c_ds")
    out = {
        "knob": "R3S2B3_G5_BAND_DISCLOSURE",
        "matched_n_knob": matched_n_knob,
        "dataset": dataset, "cell_shape": shape, "matched_n_spec": spec,
        "band_definition": (
            "the arm's own fit-set noise at the MATCHED fit-set size: for the ifc "
            "shape the exact sd over the enumerated C(5,4) fold population, for the "
            "sharp shape the single matched fit set T (|T| = 320) whose across-seed "
            "band the analyzer assembles. `systematic_correction_nrmse` = matched "
            "mean - certified full-fit value, i.e. the part of the seam that is a "
            "BIAS rather than noise."),
        "usage": (
            "quote `band.sd_nrmse` beside every `C4.by_rung[*][arm]."
            "model_minus_floor_nrmse` priced against that arm: a margin inside the "
            "band is not a difference. `model_beats_floor` is deliberately left "
            "reading the CERTIFIED full-fit floor -- the registration predicate is "
            "not re-defined by this disclosure."),
        "arms": {},
    }
    if spec is None:
        out["applicable"] = False
        out["reason"] = (f"{dataset}: cell shape {shape!r} is not named in "
                         f"R3S2B3_FLOOR_MATCHED_N={matched_n_knob!r} (the guard/"
                         "fallback cells carry no matched-n obligation)")
        return out
    out["applicable"] = True

    if shape == "ifc":
        if not (disclosure or {}).get("applicable"):
            raise FloorMatchedNError(
                f"{dataset}: R3S2B3_FLOOR_MATCHED_N asks for {spec!r} but no "
                "disclosure-leg population was built")
        out["population"] = disclosure["protocol"]
        out["n_matched_fit_sets"] = disclosure["n_legs"]
        per_arm_vals = {a: [lg["arms_on_test_split"][a] for lg in disclosure["legs"]]
                        for a in arms}
    else:
        T = np.asarray(plan["T"], dtype=np.int64)
        if spec.isdigit() and int(spec) != len(T):
            raise FloorMatchedNError(
                f"{dataset}: R3S2B3_FLOOR_MATCHED_N declares sharp:{spec} but the HOT "
                f"plan's |T| is {len(T)} -- refusing to report a mismatched floor")
        out["population"] = f"the HOT plan's T (|T| = {len(T)}), one matched fit set"
        out["n_matched_fit_sets"] = 1
        out["matched_fit_rows_head"] = [int(v) for v in T[:8]]
        per_arm_vals = {a: [arm_value(a, c_tr[T], y_tr[T], c_te, y_te)] for a in arms}

    for a in arms:
        vals = per_arm_vals[a]
        st = spread(vals)
        cert = (floors or {}).get(a)
        full = (float(cert["nrmse"])
                if isinstance(cert, dict) and isinstance(cert.get("nrmse"), (int, float))
                else None)
        band = {
            "matched_n": st,
            "certified_full_fit_nrmse": full,
            "certified_full_fit_source": (
                None if not isinstance(floors, dict)
                else (floors.get("_source") or {}).get("floors_file")),
            "sd_nrmse": (st.get("sd") if st.get("n", 0) > 1 else None),
            "systematic_correction_nrmse": (None if full is None or not st.get("n")
                                            else st["mean"] - full),
            "matched_beats_full_fit": (None if full is None or not st.get("n")
                                       else bool(st["mean"] < full)),
        }
        if isinstance(film_c, (int, float)):
            ref = (film or {}).get("nrmse_film_mean")
            if isinstance(ref, (int, float)) and ref:
                band["sd_skill_film"] = (None if band["sd_nrmse"] is None
                                         else band["sd_nrmse"] / float(ref))
                band["systematic_correction_skill_film"] = (
                    None if band["systematic_correction_nrmse"] is None
                    else band["systematic_correction_nrmse"] / float(ref))
                band["film_denominator_nrmse"] = float(ref)
        if st.get("n", 0) == 1:
            band["_single_draw_note"] = (
                "one matched fit set exists at this shape (it IS T), so `sd_nrmse` is "
                "undefined within a seed; the band is the across-seed spread of this "
                "value and is assembled by the analyzer from the three seed files.")
        out["arms"][a] = band
    return out


def attach_band_to_beat_table(floors_beat: dict, band: dict) -> dict:
    """Merge the G5 band INTO each arm's existing `beat_table` entry.

    Deliberately in place, inside the per-arm dict: `ladder.registration` reads
    `beat_table.values()[*]["model_beats_floor"]`, so introducing a new top-level
    entry (rather than extra keys on the existing ones) would change what that
    predicate iterates. `model_beats_floor` itself is untouched.
    """
    if not (band or {}).get("applicable"):
        return floors_beat
    for _rung, tbl in (floors_beat or {}).items():
        for arm, entry in (tbl or {}).items():
            b = (band.get("arms") or {}).get(arm)
            if isinstance(entry, dict) and isinstance(b, dict):
                entry["g5_band"] = b
                if isinstance(entry.get("model_minus_floor_nrmse"), float) and \
                        isinstance(b.get("sd_nrmse"), float) and b["sd_nrmse"] > 0:
                    entry["margin_over_g5_band_sd"] = (
                        entry["model_minus_floor_nrmse"] / b["sd_nrmse"])
                    entry["margin_inside_g5_band"] = bool(
                        abs(entry["model_minus_floor_nrmse"]) <= b["sd_nrmse"])
    return floors_beat
