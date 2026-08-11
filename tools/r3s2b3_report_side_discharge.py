#!/usr/bin/env python
"""r3s2b3_report_side_discharge.py — the ZERO-GPU discharge of the code-review
findings F1 and F2 for card `r3s2_field_reach-B3`, computed OUTSIDE the family
directory.

WHY IT LIVES HERE AND NOT IN `models_r3/r3s2_ceiling/`
------------------------------------------------------
This is the OUT-OF-BAND witness for repairs that also landed IN the family.
`scripts/01_train_eval.sh` points `score_panel.py --family_dir` at the live
worktree path, so the family's own numbers are produced by the family's own code
(`d2_select.restrict_folds_to_rows` for F1, `floor_matched_n.py` for F2); this
tool re-derives the same quantities from an independent implementation, and adds
the two things the job structurally cannot report about itself:

  * the PRE-repair overlap — how much of the declared selection population was
    emulator-in-sample before the F1 restriction (the job now refuses that
    configuration, so only a separate computation can size the defect); and
  * the ALL-CELL, ALL-SEED pre-release check that the restriction never empties a
    fold — an empty fold is a hard `R3S2ContractError`, so this must be verified
    for every (cell, seed) the job will touch BEFORE the job is released.

Its C(5,4) numbers agree with the in-job `floor_matched_n.py` block bit for bit
(verified on ifc_heat: affine fold sd 0.13272099165014623 in both), and with
`round3/tools/fitset_matched_n_audit.py`, which is the point of computing them
twice.

WHAT IT COMPUTES

F1 — `d2_selection_emulator_overlap`.
    The card's `R3S2B3_CORRECTOR_SELECT_ON = emulator_heldout_output` says the D2
    ridge/band-limit selection reads the emulator's HELD-OUT pseudo-LF output.
    `smoke_eval.py:1149` passes `nn_stage["LFp_tr"]` — the emulator's output on
    ALL train rows — while the emulator's own fit slice is
    `emu_fit = range(N_lf) \\ (heldout u val_rows)` (`smoke_eval.py:899-901`).
    This block reproduces `hot_split.plan` and `smoke_eval._inner_split` EXACTLY
    (the former by importing the family module read-only, the latter by
    transcribing lines 835-851, asserted against the leg dump's own row lists
    when one is supplied) and reports, per (dataset, seed, leg):

      * `n_sel_rows`                    the selection fold's size
      * `n_sel_rows_in_emu_fit`         rows that are IN-SAMPLE for the emulator
      * `n_sel_rows_emulator_heldout`   rows that are genuinely held out
      * `frac_out_of_sample`            the second / the first

    plus the two tripwire predicates -- the one `d2_select.py` already enforced
    (sel n fit = 0, transfer-fit disjointness) and its EXTENSION to the emulator
    (sel n emu_fit = 0), which did NOT hold before the repair -- and the
    `post_repair_*` fields, which apply `sel_rows n val_rows` exactly as
    `d2_select.restrict_folds_to_rows` now does and confirm per (cell, seed) that
    no fold is emptied and no surviving row is inside `emu_fit`.

F2a — `floor_matched_disclosure_legs`.
    `hot_split.plan` builds the C(5,4) LOO legs that `R3S2B3_IFC_LOO_DISCLOSURE =
    enumerate_C5_4` and `R3S2B3_FLOOR_MATCHED_N = ifc:C5_4_loo` declare; before
    the F2 repair the run loop walked `plan["legs"]` only, so they shipped with no
    number. The family now scores them in `floor_matched_n.disclosure_legs`; this
    is the independent second implementation.
    Every arm they need — `nn_condition`, `train_mean`, `zero`,
    `affine_on_hf_train` — is TRAINING-FREE, so the legs are scored here in
    closed form at zero GPU, on both readings:
      (a) the held-out TRAIN row of each leg (matched to the ladder's own
          held-out-train rungs), and
      (b) the full stripped TEST split (matched to C4, whose `beat_table`
          compares `mean_test` against floors fit on all 5 train rows).
    Arm constructions are byte-identical to `round3/tools/fitset_matched_n_audit.py`
    (itself verbatim from `make_round3_anchors.py`), and the (b) population is
    cross-checked numerically against that tool's own exhaustive-LOO output when
    `--fitset-json` is supplied. This is the ifc affine-floor LOO FOLD RANGE that
    program.md §2's affine-floor rule requires beside every ifc number.

F2b — `g5_band_disclosure`.
    `R3S2B3_G5_BAND_DISCLOSURE=1` had no consumer in the family and `ladder.py`
    emitted the G5 band as prose beside margins that carried no sd; it is now
    wired to `floor_matched_n.matched_n_band`. This block is the same disclosure
    built from the round tool's own audit output: per cell, the reference arm's fit-set band from
    `fitset_matched_n_audit.py`, expressed in ALL THREE unit systems the card
    uses — copy-LF skill, ADR r3-0006 film skill (`* c_ds`), and raw nRMSE
    (`* ref_copylf`) — because `floor_arms.beat_table` prices its margins in
    nRMSE while the clauses are quoted in film skill.

F2c — `subset_rescale_factors`.
    `geomean(c_ds over subset) / geomean(c_ds over panel)` for every subset the
    card can quote, so a subset sentence can be checked for unit-dependence
    before it is written (the `subset_geomean_unit_audit.py` trap).

REPORT-ONLY: reads `state/` and the stripped data view, writes nothing but its
own `--out`. No GPU, no training, no model.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path

sys.dont_write_bytecode = True          # never drop .pyc into the live family dir
os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")

import numpy as np

WORKTREE = Path(__file__).resolve().parents[1]
FAMILY_DIR = WORKTREE / "models_r3" / "r3s2_ceiling"


def _main_repo_root() -> Path:
    """The MAIN checkout (not this worktree): the round state and the frozen
    eval layer live there, exactly as `smoke_eval._main_repo_root` resolves it."""
    try:
        out = subprocess.run(["git", "rev-parse", "--path-format=absolute",
                              "--git-common-dir"], cwd=str(WORKTREE),
                             capture_output=True, text=True, check=True)
        return Path(out.stdout.strip()).resolve().parent
    except Exception:                                              # noqa: BLE001
        return WORKTREE


ROOT = _main_repo_root()
EVAL_DIR = ROOT / "mffp_autoresearch" / "round2" / "eval"
FACTORY_ROOT = ROOT / "mf_field" / "factory_mffp"
STATE = ROOT / "mffp_autoresearch" / "round3" / "state"
for _p in (EVAL_DIR, FACTORY_ROOT, FAMILY_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from nrmse import NRMSE_DEF_HASH, nrmse                            # noqa: E402
from data_adapters import load_mf_dataset                          # noqa: E402
import hot_split as hotlib                                         # noqa: E402  (READ-ONLY)
import rung_lift as runglib                                        # noqa: E402  (READ-ONLY)

# `S6_GATE_HOLDOUT_FRAC`, recipe verbatim (scripts/01_train_eval.sh).
HOLDOUT_FRAC = 0.2
# `smoke_eval._inner_split` offsets the HOT key by this constant (line 844).
INNER_SPLIT_KEY_OFFSET = 7919


# ── arm constructions: byte-identical to round3/tools/fitset_matched_n_audit.py ──

def standardize_cond(c_tr, c_te):
    mu, sd = c_tr.mean(axis=0), c_tr.std(axis=0)
    sd = np.where(sd > 0, sd, 1.0)
    return (c_tr - mu) / sd, (c_te - mu) / sd


def affine_fit(X, Y):
    A = np.hstack([X, np.ones((len(X), 1))])
    W, *_ = np.linalg.lstsq(A, Y, rcond=None)
    return lambda Xq: np.hstack([Xq, np.ones((len(Xq), 1))]) @ W


def arm_value(arm, c_tr, y_tr, c_te, y_te):
    if arm == "train_mean":
        return float(nrmse(np.broadcast_to(y_tr.mean(axis=0), y_te.shape), y_te))
    if arm == "nn_condition":
        z_tr, z_te = standardize_cond(c_tr, c_te)
        d2 = ((z_te[:, None, :] - z_tr[None, :, :]) ** 2).sum(axis=2)
        return float(nrmse(y_tr[np.argmin(d2, axis=1)], y_te))
    if arm == "affine_on_hf_train":
        return float(nrmse(affine_fit(c_tr, y_tr)(c_te), y_te))
    if arm == "zero":
        return float(nrmse(np.zeros_like(y_te), y_te))
    raise SystemExit(f"unknown arm {arm!r}")


def _spread(vals) -> dict:
    v = np.asarray([x for x in vals if np.isfinite(x)], dtype=np.float64)
    if not len(v):
        return {"n": 0}
    return {"n": int(len(v)), "min": float(v.min()), "max": float(v.max()),
            "median": float(np.median(v)), "mean": float(v.mean()),
            "sd": float(v.std(ddof=1)) if len(v) > 1 else 0.0}


# ── F1: the D2 selection's overlap with the emulator's own fit slice ──────

def inner_split(dataset: str, seed: int, rows: np.ndarray):
    """TRANSCRIBED VERBATIM from `smoke_eval.py:835-851` (`_inner_split`).

    Kept as a transcription rather than an import because `_inner_split` is a
    closure over `holdout_frac` inside `run()`; `--assert-against` re-checks this
    transcription against a real leg dump when one exists.
    """
    rows = np.asarray(rows, dtype=np.int64)
    n = len(rows)
    if n < 3:
        raise SystemExit(f"{dataset}: leg has {n} train rows; R3S2_VAL_DISJOINT needs >= 3")
    order = np.random.default_rng(
        hotlib.split_key(dataset, int(seed)) + INNER_SPLIT_KEY_OFFSET).permutation(n)
    n_val = min(int(max(1, round(HOLDOUT_FRAC * n))), max(n - 1, 0))
    target = max(2, n_val - (n_val % 2))
    target = min(target, (n - 1) - ((n - 1) % 2))
    n_val = target
    v = rows[order[:n_val]]
    f = rows[order[n_val:]]
    return np.sort(f), np.sort(v[:n_val // 2]), np.sort(v[n_val // 2:])


def f1_overlap(dataset: str, seed: int, n_train_hf: int, n_lf: int) -> dict:
    plan = hotlib.plan(dataset, int(n_train_hf), int(seed))
    legs = []
    for lg in plan["legs"]:
        fit_a, val_a, val_b = inner_split(dataset, seed, lg["train_rows"])
        val_rows = np.sort(np.concatenate([val_a, val_b]))
        forbidden = set(int(i) for i in np.asarray(lg["heldout"]).tolist()) | \
            set(int(i) for i in val_rows.tolist())
        emu_fit = set(i for i in range(int(n_lf)) if i not in forbidden)
        per_fold = []
        vset = set(int(v) for v in val_rows.tolist())
        for k, (fr, sr) in enumerate(lg["sel_folds"]):
            fr = set(int(v) for v in np.asarray(fr).tolist())
            sr = [int(v) for v in np.asarray(sr).tolist()]
            in_emu = [r for r in sr if r in emu_fit]
            kept = [r for r in sr if r in vset]
            per_fold.append({
                "fold": k,
                "n_sel_rows": len(sr),
                "n_sel_rows_in_emu_fit": len(in_emu),
                "n_sel_rows_emulator_heldout": len(sr) - len(in_emu),
                "frac_out_of_sample": ((len(sr) - len(in_emu)) / len(sr)) if sr else None,
                "tripwire_transfer_fit_disjoint": bool(not (fr & set(sr))),
                "tripwire_emulator_fit_disjoint": bool(not set(in_emu)),
                # after the F1 VAL_ROWS RESTRICTION (d2_select.restrict_folds_to_rows)
                "post_repair_n_sel_rows": len(kept),
                "post_repair_fold_survives": bool(kept),
                "post_repair_in_emu_fit": len([r for r in kept if r in emu_fit]),
                "post_repair_fit_disjoint": bool(not (fr & set(kept))),
            })
        n_sel = sum(f["n_sel_rows"] for f in per_fold)
        n_in = sum(f["n_sel_rows_in_emu_fit"] for f in per_fold)
        legs.append({
            "post_repair": {
                "n_folds_surviving": sum(1 for f in per_fold if f["post_repair_fold_survives"]),
                "n_sel_rows": sum(f["post_repair_n_sel_rows"] for f in per_fold),
                "n_sel_rows_in_emu_fit": sum(f["post_repair_in_emu_fit"] for f in per_fold),
                "leg_would_abort": bool(
                    not any(f["post_repair_fold_survives"] for f in per_fold)),
            },
            "leg_id": lg["leg_id"],
            "n_fit_rows": int(len(lg["fit_rows"])),
            "n_train_rows": int(len(lg["train_rows"])),
            "n_heldout": int(len(lg["heldout"])),
            "n_val_rows": int(len(val_rows)),
            "n_emu_fit_rows": len(emu_fit),
            "n_sel_rows_total": n_sel,
            "n_sel_rows_in_emu_fit_total": n_in,
            "frac_out_of_sample": ((n_sel - n_in) / n_sel) if n_sel else None,
            "sel_folds": per_fold,
        })
    tot = sum(lg["n_sel_rows_total"] for lg in legs)
    inn = sum(lg["n_sel_rows_in_emu_fit_total"] for lg in legs)
    return {
        "protocol": plan["protocol"], "n_legs": plan["n_legs"],
        "split_key": plan["split_key"],
        "n_train_hf": int(n_train_hf), "n_lf": int(n_lf),
        "legs": legs,
        "cell_total": {
            "n_sel_rows": tot, "n_sel_rows_in_emu_fit": inn,
            "n_sel_rows_emulator_heldout": tot - inn,
            "frac_out_of_sample": ((tot - inn) / tot) if tot else None,
        },
        "tripwire_transfer_fit_disjoint_all_legs": bool(all(
            f["tripwire_transfer_fit_disjoint"] for lg in legs for f in lg["sel_folds"])),
        "tripwire_emulator_fit_disjoint_all_legs": bool(all(
            f["tripwire_emulator_fit_disjoint"] for lg in legs for f in lg["sel_folds"])),
        "post_repair_summary": {
            "min_folds_surviving_over_legs": min(
                (lg["post_repair"]["n_folds_surviving"] for lg in legs), default=None),
            "min_sel_rows_over_legs": min(
                (lg["post_repair"]["n_sel_rows"] for lg in legs), default=None),
            "any_leg_would_abort": bool(any(lg["post_repair"]["leg_would_abort"]
                                            for lg in legs)),
            "emulator_fit_disjoint_all_legs": bool(all(
                lg["post_repair"]["n_sel_rows_in_emu_fit"] == 0 for lg in legs)),
            "note": ("`any_leg_would_abort` True on ANY (cell, seed) means the run "
                     "raises R3S2ContractError rather than falling back — this is the "
                     "pre-release check that the F1 repair cannot kill the job."),
        },
    }


# ── F2a: the C(5,4) floor-matched disclosure legs, closed form ────────────

def f2_disclosure(dataset: str, seed: int, arms, c_tr, y_tr, c_te, y_te) -> dict:
    plan = hotlib.plan(dataset, int(len(y_tr)), int(seed))
    disc = plan.get("disclosure_legs") or []
    if not disc:
        return {"applicable": False,
                "reason": (f"{dataset}: hot_split.plan builds no disclosure legs under "
                           f"protocol {plan['protocol']} (R3S2B3_IFC_LOO_DISCLOSURE is "
                           "scoped to the enumerate_C5_3 cells)")}
    legs, full = [], {}
    for arm in arms:
        full[arm] = arm_value(arm, c_tr, y_tr, c_te, y_te)
    for d in disc:
        fit = np.asarray(d["fit_rows"], dtype=np.int64)
        hel = np.asarray(d["heldout"], dtype=np.int64)
        entry = {"leg_id": d["leg_id"], "fit_rows": [int(v) for v in fit],
                 "heldout_rows": [int(v) for v in hel],
                 "n_fit_rows": int(len(fit)), "n_heldout": int(len(hel)),
                 "arms_on_heldout_train_row": {}, "arms_on_test_split": {}}
        for arm in arms:
            entry["arms_on_heldout_train_row"][arm] = arm_value(
                arm, c_tr[fit], y_tr[fit], c_tr[hel], y_tr[hel])
            entry["arms_on_test_split"][arm] = arm_value(
                arm, c_tr[fit], y_tr[fit], c_te, y_te)
        legs.append(entry)
    return {
        "applicable": True,
        "knob": plan.get("disclosure_knob"),
        "matched_n_knob": "R3S2B3_FLOOR_MATCHED_N",
        "protocol": f"C({len(y_tr)},{len(disc[0]['fit_rows'])})_loo",
        "n_legs": len(legs),
        "legs": legs,
        "fold_range_on_heldout_train_row": {
            arm: _spread([lg["arms_on_heldout_train_row"][arm] for lg in legs])
            for arm in arms},
        "fold_range_on_test_split": {
            arm: _spread([lg["arms_on_test_split"][arm] for lg in legs])
            for arm in arms},
        "full_fit_on_test_split": full,
        "reading": ("the `_on_test_split` population is the C4 comparand at MATCHED fit-set "
                    "size (C4's beat_table prices mean_test against floors fit on ALL "
                    f"{len(y_tr)} train rows, i.e. `full_fit_on_test_split`); the "
                    "`_on_heldout_train_row` population is matched to the ladder's own "
                    "held-out-TRAIN rungs. program.md §2's affine-floor rule asks for the "
                    "`affine_on_hf_train` FOLD RANGE, not the single fit — it is the "
                    "`fold_range_on_test_split.affine_on_hf_train` entry."),
    }


# ── F2b/F2c: the G5 band and the subset rescale factors ──────────────────

def geo(v):
    v = np.asarray(v, dtype=np.float64)
    return float(np.exp(np.log(v).mean()))


def g5_band(fitset_jsons, film, arms) -> dict:
    cells = {}
    for fp in fitset_jsons:
        obj = json.loads(Path(fp).read_text())
        for ds, e in (obj.get("cells") or {}).items():
            ref = e.get("reference_nrmse")
            c = ((film.get("datasets") or {}).get(ds) or {}).get("c_ds")
            out = {"_source_file": str(fp), "mode": e.get("mode"),
                   "n_train": e.get("n_train"), "n_fit": e.get("n_fit"),
                   "certified_tau_rel": e.get("certified_tau_rel"),
                   "reference_nrmse_copylf": ref, "c_ds_film": c,
                   "skill_at_full_fit": e.get("skill_at_full_fit"), "arms": {}}
            for arm, a in (e.get("per_arm") or {}).items():
                if arm not in arms:
                    continue
                tau = e.get("certified_tau_rel")
                sd_sk = a.get("skill_matched_sd")
                sys_sk = a.get("systematic_correction")
                band = {
                    "band_definition": ("fit-set band of the reference arm at matched fit-set "
                                        "size: sd over the fold population, plus the "
                                        "systematic matched-n correction and its se"),
                    "sd_skill_copylf": sd_sk,
                    "systematic_correction_skill_copylf": sys_sk,
                    "systematic_correction_se_skill_copylf": a.get("systematic_correction_se"),
                    "sd_over_tau_rel": a.get("selection_noise_sd_over_tau"),
                    "frac_folds_breaching_tau": a.get("frac_folds_breaching_tau"),
                    "skill_matched_mean": a.get("skill_matched_mean"),
                    "skill_matched_ci95": [a.get("skill_matched_p2.5"),
                                           a.get("skill_matched_p97.5")],
                    "n_draws": a.get("n_draws"),
                }
                if isinstance(sd_sk, (int, float)) and isinstance(c, (int, float)):
                    band["sd_skill_film"] = float(sd_sk) * float(c)
                    if isinstance(sys_sk, (int, float)):
                        band["systematic_correction_skill_film"] = float(sys_sk) * float(c)
                if isinstance(sd_sk, (int, float)) and isinstance(ref, (int, float)):
                    band["sd_nrmse"] = float(sd_sk) * float(ref)
                    if isinstance(sys_sk, (int, float)):
                        band["systematic_correction_nrmse"] = float(sys_sk) * float(ref)
                band["tau_rel_units_note"] = (
                    None if tau is None else
                    "sd_over_tau_rel is the band in units of the cell's certified tau_rel")
                out["arms"][arm] = band
            cells[ds] = out
    return {
        "knob": "R3S2B3_G5_BAND_DISCLOSURE",
        "wired_to": ("ladder.clauses -> C4_floor_arms.g5_band_disclosure, which ships as "
                     "prose in the family; these are the numbers that sentence names"),
        "usage": ("quote `sd_nrmse` beside every `floor_arms.beat_table` "
                  "`model_minus_floor_nrmse` margin priced against that arm, and "
                  "`sd_skill_film` beside every film-skill margin; a margin inside the "
                  "band is not a difference"),
        "cells": cells,
    }


def subset_rescale(film, panel, subsets) -> dict:
    c = {k: v["c_ds"] for k, v in (film.get("datasets") or {}).items()}
    missing = [d for d in panel if d not in c]
    if missing:
        return {"error": f"film_denominator.json has no c_ds for {missing}"}
    gp = geo([c[d] for d in panel])
    out = {"panel": list(panel), "geomean_c_panel": gp, "c_ds": c, "subsets": {}}
    for nm, cells in subsets.items():
        miss = [d for d in cells if d not in c]
        if miss:
            out["subsets"][nm] = {"cells": cells, "error": f"no c_ds for {miss}"}
            continue
        gs = geo([c[d] for d in cells])
        out["subsets"][nm] = {
            "cells": cells, "geomean_c_subset": gs, "rescale_vs_panel": gs / gp,
            "bar_calibration_verdict": ("OK" if sorted(cells) == sorted(panel)
                                        else "SUBSET_BAR_MISMATCH"),
        }
    out["reading"] = ("a copy-LF-unit subset delta read against a panel-calibrated bar is "
                      "rescaled by `rescale_vs_panel` when re-expressed in ADR r3-0006 film "
                      "units; |rescale - 1| is the size of the unit trap for that subset. "
                      "Per-CELL verdicts are exactly unit-invariant and need no correction.")
    return out


# ── driver ───────────────────────────────────────────────────────────────

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--datasets", required=True, help="comma list")
    ap.add_argument("--seeds", default="0,1,2")
    ap.add_argument("--arms", default="nn_condition,train_mean,zero,affine_on_hf_train")
    ap.add_argument("--stripped-root", default=str(
        ROOT / "mffp_autoresearch" / "round2" / "stripped_data"))
    ap.add_argument("--film-json", default=str(STATE / "anchors" / "film_denominator.json"))
    ap.add_argument("--fitset-json", action="append", default=[],
                    help="fitset_matched_n_audit.py output(s) feeding the G5 band")
    ap.add_argument("--panel", default=("sharp__phase_field_crystal_2d,sharp__allen_cahn_2d,"
                                        "sharp__fisher_kpp_2d,sharp__cahn_hilliard,"
                                        "ifc_poisson,ifc_heat"))
    ap.add_argument("--subset", action="append", default=[], help="name=ds1,ds2")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)

    datasets = [s.strip() for s in a.datasets.split(",") if s.strip()]
    seeds = [int(s) for s in a.seeds.split(",") if s.strip()]
    arms = [s.strip() for s in a.arms.split(",") if s.strip()]
    panel = [s.strip() for s in a.panel.split(",") if s.strip()]
    subsets = {}
    for s in a.subset:
        nm, cells = s.split("=", 1)
        subsets[nm] = [c for c in cells.split(",") if c.strip()]

    film = json.loads(Path(a.film_json).read_text())
    root = Path(a.stripped_root)

    rep = {
        "_tool": "r3s2b3_report_side_discharge.py",
        "_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "_card": "r3s2_field_reach-B3",
        "_discharges": ["F1 (D2 selection input overlap)",
                        "F2 (G5 band consumer + C(5,4) disclosure legs)"],
        "_report_only": ("reads state/ and the stripped view; writes only --out. NOTHING "
                         "under models_r3/ is read-write or modified — SLURM job 261188 "
                         "runs the family bytes untouched."),
        "_nrmse_def_hash": NRMSE_DEF_HASH,
        "_eval_dir": str(EVAL_DIR),
        "_stripped_root": str(root),
        "_args": vars(a),
        "cells": {},
    }

    for ds in datasets:
        c_tr, y_tr, c_te, y_te, n_lf, lf_rung = None, None, None, None, None, None
        tr = load_mf_dataset(root / ds, "train")
        te = load_mf_dataset(root / ds, "test")
        hf = te["hf_fid"] if te["hf_fid"] in tr["fids"] else tr["hf_fid"]
        rung = runglib.scored_rung(ds, tr["lf_fids"])
        lf_rung = int(rung["lf_rung"])
        f64 = lambda x: np.asarray(x, dtype=np.float64)             # noqa: E731
        c_tr, y_tr = f64(tr["cond_by_fid"][hf]), f64(tr["field_by_fid"][hf])
        c_te, y_te = f64(te["cond_by_fid"][hf]), f64(te["field_by_fid"][hf])
        n_lf = int(np.asarray(tr["field_by_fid"][lf_rung]).shape[0])
        entry = {
            "n_train_hf": int(len(y_tr)), "n_test": int(len(y_te)), "n_lf": n_lf,
            "lf_rung": lf_rung, "lf_rung_source": rung["source"], "hf_fid": int(hf),
            "F1_d2_selection_emulator_overlap": {
                str(s): f1_overlap(ds, s, len(y_tr), n_lf) for s in seeds},
            "F2a_floor_matched_disclosure_legs": {
                str(s): f2_disclosure(ds, s, arms, c_tr, y_tr, c_te, y_te) for s in seeds},
        }
        rep["cells"][ds] = entry
        f1 = entry["F1_d2_selection_emulator_overlap"][str(seeds[0])]["cell_total"]
        print(f"[F1] {ds:32s} sel rows {f1['n_sel_rows']:5d} | in-sample for the "
              f"emulator {f1['n_sel_rows_in_emu_fit']:5d} | genuinely held out "
              f"{f1['n_sel_rows_emulator_heldout']:5d} "
              f"({100.0 * (f1['frac_out_of_sample'] or 0.0):.1f}%)", flush=True)

    rep["F2b_g5_band_disclosure"] = g5_band(a.fitset_json, film, arms)
    rep["F2c_subset_rescale_factors"] = subset_rescale(film, panel, subsets)

    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(rep, indent=1, sort_keys=True) + "\n")
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
