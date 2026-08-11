#!/usr/bin/env python
"""`r3s2_ceiling` — the EMULATOR-CEILING LADDER of card `r3s2_field_reach-B3`.

Contract: the unchanged six-arg factory CLI (`--dataset_dir --dataset_name
--epochs --out --ckpt_dir --seed`), resume from `<ckpt_dir>/last.pt`, result JSON
via `data_adapters.metrics.finalize_and_write`.

THE CLAIM IS THE REGIME, NOT THE DECOMPOSITION
----------------------------------------------
Prior-art verdict D1 is explicit that the oracle/predicted decomposition is
textbook (`preempted-but-MF-composition-open`) and that "the **instrument may
not be claimed**, only the measurement in this regime". What no fetched source
runs is a ladder whose oracle intermediate is (a) structurally UNAVAILABLE at
inference, (b) measured at N_hf = 5 with an ENUMERATED C(5,3) fold population,
and (c) priced against a certified training-free floor plus a certified baseline
denominator in skill units. That triple is what this family measures.

FIVE RUNGS (`R3S2B3_RUNGS`, all scored on held-out TRAIN rows; the deployable
three additionally on the stripped test split, `R3S2B3_TEST_SPLIT_ARMS`)

  R0_absent     cond -> HF at the matched 300-epoch budget. THE NO-LF DENOMINATOR.
  R1_predicted  cond -> pseudo-LF -> convention lift -> frozen corrector -> HF.
  R1b_degraded  pseudo-LF lifted, corrector removed.
  R2_oracle     REAL LF of the held-out rows -> the SAME frozen corrector -> HF.
  R2b_copylf    real LF, convention lift only, zero parameters.

WHY HELD-OUT TRAIN ROWS
-----------------------
`R2_oracle` needs a real LF field at evaluation time. Immutable #9 makes that
structurally impossible on the test split: the stripped view physically omits
the test LF files and `round2/eval/score_panel.py:99` refuses any view that
exposes them. Gate V2 below asserts the absence before any field array is read,
and `R3S2B3_ORACLE_NONDEPLOYABLE=1` keeps both real-LF rungs out of every test-
split path and out of every panel geomean. The split-transfer LICENCE (clause
C3) is the sanctioned instrument that says whether the held-out-train ceiling
transfers to the test split at all; a cell failing it ships REPORT-ONLY.

WHAT IS NEW HERE vs `r3s2_route` (B2), from which every component is vendored:
  * the 5-rung ladder and its statistics (`ladder.py`);
  * the HOT split protocols and the enumerated fold populations (`hot_split.py`);
  * the D2 selection-input repair — the LSI regularisation is SELECTED on the
    emulator's held-out output instead of on real LF (`d2_select.py`), with the
    real-LF-selected variant as the paired comparand. INSTRUMENT ONLY;
  * the rung/lift tripwire against `panel_data.py`'s scored cell (`rung_lift.py`,
    ADR r3-0005: pfc is rung 1 + spectral zero-pad);
  * the target-scaler pre-flight, now LIVE because B3 scores pfc
    (`target_scale.py`, round-2 ADR 0004 §2);
  * the `models_r3/_common/ckpt_binding.py` save hook (batch-3 contract rule 2).

DECLARED REUSE, role (a) (round-2 program 5.10a): the DC-lineage corrector
remains a declared FROZEN test-time sub-component behind a condition->pseudo-LF
front end. NEW in B3: the SAME frozen corrector is additionally evaluated on
REAL train-side LF (rung `R2_oracle`) as an explicitly NON-DEPLOYABLE reference
arm, in the same role class as the copy-LF reference.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[1]                                   # <worktree>
FACTORY_ROOT = WORKTREE / "mf_field" / "factory_mffp"
COMMON_DIR = HERE.parent / "_common"                          # models_r3/_common


def _main_repo_root() -> Path:
    """The MAIN checkout root, not this worktree's (`--git-common-dir`'s parent)."""
    import subprocess
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
            capture_output=True, text=True, check=True, cwd=str(HERE)).stdout.strip()
        common = Path(out)
        if common.name == ".git" and common.parent.exists():
            return common.parent
    except Exception:  # noqa: BLE001
        pass
    return WORKTREE


# THE EVAL LAYER IS THE MAIN CHECKOUT'S, NOT THIS WORKTREE'S COPY (READ-ONLY).
# `score_panel.py` resolves `repo_root()` from its OWN location and hashes
# `EVAL_DIR/{nrmse,panel_data,score_panel}.py` into the cache key from there. A
# worktree forked before an eval-layer amendment carries a STALE copy: this
# worktree forked at round3-substrate 44f2404 (2026-08-07), which predates the
# ADR r3-0005 amendment to `panel_data.py` (2026-08-10) that this card's
# rung/lift tripwire reads. Importing the worktree copy would silently measure
# against a different scored cell than the scorer scores. `_ASSERT_NRMSE_MATCH`
# below keeps the metric definition itself unambiguous across the two paths.
_MAIN_EVAL = _main_repo_root() / "mffp_autoresearch" / "round2" / "eval"
_WT_EVAL = WORKTREE / "mffp_autoresearch" / "round2" / "eval"
EVAL_DIR = _MAIN_EVAL if (_MAIN_EVAL / "panel_data.py").exists() else _WT_EVAL

sys.path.insert(0, str(HERE))
for _p in (COMMON_DIR, FACTORY_ROOT, EVAL_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from model import param_count                                            # noqa: E402
from front_end import Emulator                                           # noqa: E402
from local_corrector import LocalCorrector, PixelGate, fit_alpha         # noqa: E402
import bands as bandlib                                                  # noqa: E402
import periodicity as periodlib                                          # noqa: E402
import lsi_filter as lsilib                                              # noqa: E402
import upsample as uplib                                                 # noqa: E402
import probes as probelib                                                # noqa: E402
import ic_synth as icsynth                                               # noqa: E402
import floor_arms as floorlib                                            # noqa: E402
import floor_matched_n as fmnlib                                         # noqa: E402
import direct_head as directlib                                          # noqa: E402
import hot_split as hotlib                                               # noqa: E402
import ladder as ladderlib                                               # noqa: E402
import d2_select as d2lib                                                # noqa: E402
import rung_lift as runglib                                              # noqa: E402
import target_scale as tslib                                             # noqa: E402
import ckpt_binding as bindlib                                           # noqa: E402
from data_adapters import load_mf_dataset                                # noqa: E402
from data_adapters.geometry import resolve_grid                          # noqa: E402
from data_adapters.metrics import finalize_and_write                     # noqa: E402
from nrmse import NRMSE_DEF_HASH, nrmse as round_nrmse                   # noqa: E402

MODEL_NAME = "r3s2_ceiling"
WORK_CAP = 256


def _assert_nrmse_unambiguous() -> dict:
    """The ONE nRMSE definition must be the same file on both eval paths.

    The family reads the MAIN checkout's eval layer (see the `EVAL_DIR` note).
    If the worktree also carries a copy, its `nrmse.py` must be byte-identical,
    or "the round's one nRMSE definition" would be two definitions.
    """
    import hashlib as _h
    a = _h.sha256((EVAL_DIR / "nrmse.py").read_bytes()).hexdigest()
    rec = {"eval_dir": str(EVAL_DIR), "nrmse_sha256": a,
           "worktree_copy_present": (_WT_EVAL / "nrmse.py").exists(),
           "main_eval_used": EVAL_DIR == _MAIN_EVAL}
    if (_WT_EVAL / "nrmse.py").exists() and _WT_EVAL != EVAL_DIR:
        b = _h.sha256((_WT_EVAL / "nrmse.py").read_bytes()).hexdigest()
        rec["worktree_nrmse_sha256"] = b
        if a != b:
            raise RuntimeError(
                f"the metric definition differs between {EVAL_DIR}/nrmse.py ({a[:16]}) "
                f"and {_WT_EVAL}/nrmse.py ({b[:16]}); refusing to run against an "
                "ambiguous nRMSE (program.md §5, the eval layer is immutable and single)")
        rec["worktree_copy_byte_identical"] = True
    return rec


EVAL_LAYER = _assert_nrmse_unambiguous()

# Optimisation hyperparameters VERBATIM from the base family (`r3s2_route` @
# e606a4f1, itself `r3s2_stack_ic` @ d5069a74, itself `r2s2_stack` @ 6b4e1d48,
# itself `s4_router` @ b90d4662). No value here is invented by the builder.
SMOKE = dict(hidden_channels=64, n_blocks=4, modes_cap=12, batch_size=16,
             lr_pretrain=1e-3, lr_finetune=3e-4, weight_decay=1e-5, grad_clip=1.0)
LR_EMULATOR = SMOKE["lr_pretrain"]
LR_CORRECTOR = SMOKE["lr_finetune"]
LR_GATE = SMOKE["lr_finetune"]
LR_DIRECT = SMOKE["lr_pretrain"]          # R0 is the same trunk trained from scratch
CKPT_SAVES_PER_STAGE = 5
PAIRED_COND_TOL = 1e-6
DIRECT_VAL_THRESHOLD = 20                 # base family's R3S2B2_DIRECT_VAL rule
FRONT_END = "ic_synth"                    # recipe R3S2_FRONTEND (one front end in B3)


class R3S2ContractError(RuntimeError):
    """A component seam violated its contract (spec §5.3: assert, don't default)."""


# ── knobs ────────────────────────────────────────────────────────────────
# Every value below is the card recipe `env`, VERBATIM. `read_knobs` refuses an
# unknown key and records any deviation, so a silent default is impossible.
# Keys prefixed `_` in the recipe are card directives, not env.
KNOB_RECIPE_VALUES = {
    "R3S2B3_LADDER": "oracle_ceiling_5rung",
    "R3S2B3_RUNGS": "R0_absent,R1_predicted,R1b_degraded,R2_oracle,R2b_copylf",
    "R3S2B3_ORACLE_NONDEPLOYABLE": "1",
    "R3S2B3_TEST_SPLIT_ARMS": "R0_absent,R1_predicted,R1b_degraded",
    "R3S2B3_HOT_SPLIT_SHARP": "seeded_perm_fit320_heldout80",
    "R3S2B3_HOT_SPLIT_IFC": "enumerate_C5_3",
    "R3S2B3_IFC_LOO_DISCLOSURE": "enumerate_C5_4",
    "R3S2B3_SHARP_CLOSEDFORM_FOLDS": "kfold5_within_T",
    "R3S2B3_HOT_SPLIT_KEY": "deterministic_from_dataset_and_seed",
    "R3S2B3_NO_TEST_LF_ASSERT": "1",
    "R3S2B3_STATS": "phi_ceil,phi_real,rho,E_est,E_hall",
    "R3S2B3_REPORT_UNITS": "film_skill,fractional_error_reduction",
    "R3S2B3_BAND_STATS": "energy_weighted_signed_coherence",
    "R3S2B3_MIN_OVER_LEGS_CLAUSES": "1",
    "R3S2B3_LEG_POPULATION_DUMP": "1",
    "R3S2B3_FILM_DENOM_JSON": "mffp_autoresearch/round3/state/anchors/film_denominator.json",
    "R3S2B3_NOISE_FLOOR_JSON": "mffp_autoresearch/round3/state/anchors_repaired/noise_floor.json",
    "R3S2B3_REGISTRATION_PREDICATE": "scored_and_certified_mce_and_not_floor_disqualified",
    "R3S2B3_SPLIT_TRANSFER_GATE": "1",
    "R3S2B3_SPLIT_TRANSFER_TOL_LOGRATIO": "0.25",
    "R3S2B3_CORRECTOR_SELECT_ON": "emulator_heldout_output",
    "R3S2B3_CORRECTOR_SELECT_COMPARAND": "real_lf",
    "S6_LSI_RIDGE": "enumerated_folds_out_of_sample",
    "S6_LSI_RIDGE_GRID": "0,1e-10,3.162e-10,1e-9,1e-8,1e-7,1e-6,1e-4,1e-2,1e-1",
    "S6_LSI_BANDLIMIT": "selected_not_fixed",
    "S6_LSI_BANDLIMIT_GRID": "on,off",
    "S6_LSI_BANDLIMIT_MODE": "zero_above_kcut",
    "S6_LSI_KCUT_SOURCE": "ladder_shape_ratio_adr_r2_0001",
    "S6_LEAKAGE_TRIPWIRE": "1",
    "S6_BAND_EDGES_FRAC": "0,0.125,0.25,0.5,1.0",
    "S6_VARIANT": "local_pixel_gate",
    "S6_SELECTOR": "heldout_scalar",
    "S6_PAD_MODE": "circular_if_periodic",
    "S6_PERIODIC_TEST": "wrap_continuity_ratio_hf_train",
    "S6_PERIODIC_TOL": "1.25",
    "S6_KERNEL": "7",
    "S6_DEPTH": "4",
    "S6_WIDTH": "32",
    "S6_GATE_HOLDOUT_FRAC": "0.2",
    "S6_GATE_INIT": "zero",
    "S6_GATE_LINESEARCH_INCLUDES_ZERO": "1",
    "R3S2_FRONTEND": "ic_synth",
    "R3S2_ARM": "frozen",
    "R3S2_IC_SYNTH": "analytic_modes",
    "R3S2_IC_SYNTH_NORM": "res_min_maxabs",
    "R3S2_IC_SYNTH_SCALE": "1.0",
    "R3S2_IC_NAMES_FROM": "meta_param_names_ic_prefix",
    "R3S2_IC_FALLBACK": "film_only_recorded",
    "R3S2_IC_EQUIV_CHECK": "1",
    "R3S2_IC_SHUFFLE_NULL": "0_established_in_B1",
    "R3S2_EMU_TARGET": "lf_native",
    "R3S2_EMU_RUNG": "scored_cell_lf_from_panel_data",
    "R3S2_EMU_WIDTH": "64",
    "R3S2_EMU_BLOCKS": "4",
    "R3S2_EMU_MODES": "12",
    "R3S2_EMU_LOSS": "rel_l2",
    "R3S2_EMU_SHARED": "1",
    "R3S2_EPOCH_SPLIT": "0.5",
    "R3S2_BUDGET_MATCH": "arm_equal_total",
    "R3S2_UPSAMPLE": "corrected_by_convention",
    "R3S2B3_RUNG_LIFT_TRIPWIRE": "1",
    "R3S2_TARGET_SCALER_PREFLIGHT": "pfc_per_sample_if_outlier_dominated",
    "R3S2_LF_INPUT": "pseudo_and_real_by_rung",
    "R3S2_VAL_DISJOINT": "1",
    "R3S2_REQUIRE_PSEUDO_LF": "1",
    "R3S2_PAIRING_GATE": "1",
    "R3S2_FLOOR_ARMS": "nn_condition,train_mean,zero,affine_on_hf_train",
    "R3S2B3_FLOOR_MATCHED_N": "sharp:320,ifc:C5_4_loo",
    "R3S2B3_G5_BAND_DISCLOSURE": "1",
    "R3S2B3_CKPT_BINDING": "1",
    "R3S2B3_ROLES_READ": ("R0_absent=cond_only,R1_predicted=lf_at_train,"
                          "R1b_degraded=lf_at_train,R2_oracle=lf_at_train,"
                          "R2b_copylf=lf_at_train"),
    "R3S2B3_CKPT_DATA_HASH_BIND": "1",
    "R3S2B3_ANCHOR_REPLICATION_CHECK": "10.0853",
    "R3S2_DIAG_OUT": "mffp_autoresearch_outputs/round3/r3s2_field_reach/B3/eval",
}

# ADR r3-0007 option C (operator, 2026-08-10): the SCORED panel. `ifc_poisson`
# runs and is reported, never aggregated. Registration leg (i) reads this.
SCORED_PANEL_ADR_R3_0007 = (
    "sharp__phase_field_crystal_2d", "sharp__allen_cahn_2d",
    "sharp__fisher_kpp_2d", "sharp__cahn_hilliard", "ifc_heat",
)


def _truthy(v) -> bool:
    return str(v).strip().lower() in ("1", "true", "yes", "on")


def read_knobs() -> dict:
    knobs, deviations = {}, {}
    for k, default in KNOB_RECIPE_VALUES.items():
        v = os.environ.get(k, default)
        knobs[k] = v
        if v != default:
            deviations[k] = {"recipe": default, "env": v}
    knobs["_deviations_from_recipe"] = deviations

    fixed = {
        "R3S2B3_LADDER": "oracle_ceiling_5rung",
        "R3S2B3_RUNGS": ",".join(ladderlib.RUNGS),
        "R3S2B3_TEST_SPLIT_ARMS": ",".join(ladderlib.DEPLOYABLE),
        "R3S2B3_REGISTRATION_PREDICATE":
            "scored_and_certified_mce_and_not_floor_disqualified",
        "R3S2B3_CORRECTOR_SELECT_ON": "emulator_heldout_output",
        "R3S2B3_CORRECTOR_SELECT_COMPARAND": "real_lf",
        "R3S2_EMU_RUNG": "scored_cell_lf_from_panel_data",
        "R3S2_EMU_TARGET": "lf_native",
        "R3S2_UPSAMPLE": "corrected_by_convention",
        "R3S2_IC_SYNTH": "analytic_modes",
        "R3S2_IC_SYNTH_NORM": "res_min_maxabs",
        "R3S2_IC_NAMES_FROM": "meta_param_names_ic_prefix",
        "R3S2_IC_FALLBACK": "film_only_recorded",
        "R3S2_BUDGET_MATCH": "arm_equal_total",
        "R3S2_FRONTEND": "ic_synth",
        "R3S2_ARM": "frozen",
        "S6_VARIANT": "local_pixel_gate",
        "S6_LSI_RIDGE": "enumerated_folds_out_of_sample",
        "S6_LSI_BANDLIMIT": "selected_not_fixed",
        "S6_LSI_BANDLIMIT_MODE": "zero_above_kcut",
        "S6_LSI_KCUT_SOURCE": "ladder_shape_ratio_adr_r2_0001",
        "R3S2_LF_INPUT": "pseudo_and_real_by_rung",
        "R3S2_TARGET_SCALER_PREFLIGHT": "pfc_per_sample_if_outlier_dominated",
    }
    for key, want in fixed.items():
        if knobs[key] != want:
            raise R3S2ContractError(
                f"{key}={knobs[key]!r} contradicts the card recipe ({want!r}). This "
                "family refuses to run under a knob the card did not register.")
    for key in ("R3S2B3_ORACLE_NONDEPLOYABLE", "R3S2B3_NO_TEST_LF_ASSERT",
                "R3S2B3_RUNG_LIFT_TRIPWIRE", "R3S2B3_CKPT_BINDING",
                "R3S2B3_CKPT_DATA_HASH_BIND", "R3S2B3_SPLIT_TRANSFER_GATE",
                "R3S2B3_MIN_OVER_LEGS_CLAUSES", "R3S2_PAIRING_GATE",
                "R3S2_REQUIRE_PSEUDO_LF", "R3S2_VAL_DISJOINT", "S6_LEAKAGE_TRIPWIRE"):
        if not _truthy(knobs[key]):
            raise R3S2ContractError(
                f"{key}={knobs[key]!r}: the card registers this gate as ON; turning it "
                "off would silently change what the run measures")
    if str(knobs["R3S2_IC_SHUFFLE_NULL"]).strip() not in ("0_established_in_B1", "0"):
        raise R3S2ContractError(
            "R3S2_IC_SHUFFLE_NULL must be '0_established_in_B1' — the zero-information "
            "null for the IC channel was established on B1 and is NOT re-spent here; "
            f"got {knobs['R3S2_IC_SHUFFLE_NULL']!r}")
    if knobs["R3S2_EMU_LOSS"] != "rel_l2":
        raise R3S2ContractError(f"R3S2_EMU_LOSS must be 'rel_l2', got "
                                f"{knobs['R3S2_EMU_LOSS']!r}")
    return knobs


def knob_int(k, name) -> int:
    try:
        return int(str(k[name]).strip())
    except Exception as e:  # noqa: BLE001
        raise R3S2ContractError(f"{name}={k[name]!r} is not an int ({e})") from e


def knob_float(k, name) -> float:
    try:
        return float(str(k[name]).strip())
    except Exception as e:  # noqa: BLE001
        raise R3S2ContractError(f"{name}={k[name]!r} is not a float ({e})") from e


# ── small helpers (vendored structure from r3s2_route) ───────────────────


def _cap_grid(grid, cap: int = WORK_CAP):
    H, W = int(grid[0]), int(grid[1])
    m = max(H, W)
    if m <= cap:
        return (H, W)
    f = cap / m
    return (max(1, round(H * f)), max(1, round(W * f)))


def _modes(grid, cap):
    H, W = int(grid[0]), int(grid[1])
    return (min(cap, max(H // 2, 1)), min(cap, W // 2 + 1))


def _sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def state_sha256(sd) -> str:
    if sd is None:
        return None
    h = hashlib.sha256()
    for key in sorted(sd):
        v = sd[key]
        h.update(str(key).encode())
        t = v.detach().cpu().contiguous() if torch.is_tensor(v) else torch.as_tensor(v)
        h.update(str(tuple(t.shape)).encode())
        h.update(str(t.dtype).encode())
        h.update(np.ascontiguousarray(t.numpy()).tobytes())
    return h.hexdigest()


def dataset_content_sha256(parts: dict) -> str:
    """A CONTENT hash over every array this run consumes.

    `R3S2B3_CKPT_DATA_HASH_BIND=1`: bound into `last.pt`, so a resume against
    CHANGED arrays ABORTS instead of zero-stepping (round-3 STOP-THE-LINE #2).
    """
    h = hashlib.sha256()
    for key in sorted(parts):
        v = parts[key]
        h.update(f"|{key}|".encode())
        if isinstance(v, np.ndarray):
            a = np.ascontiguousarray(v)
            h.update(str(a.shape).encode())
            h.update(str(a.dtype.str).encode())
            h.update(a.tobytes())
        else:
            h.update(repr(v).encode())
    return h.hexdigest()


def _jsonable(o):
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, float) and not math.isfinite(o):
        return None
    return o


def _json_safe(o):
    if isinstance(o, dict):
        return {str(k): _json_safe(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_json_safe(v) for v in o]
    return _jsonable(o)


def _save_ckpt(path: Path, payload: dict) -> None:
    """Atomic torch.save (tmp + os.replace): a preemption mid-write cannot leave
    a truncated last.pt that would silently restart at epoch 0."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(str(path) + ".tmp")
    torch.save(payload, tmp)
    os.replace(tmp, path)


def load_ckpt_checked(path: Path, meta: dict, data_sha: str, bind: bool):
    """Return a checkpoint whose meta matches `meta`, else None. ABORT on a
    dataset-content-hash mismatch (`R3S2B3_CKPT_DATA_HASH_BIND=1`)."""
    if path is None or not path.exists():
        return None, {"found": False, "aborted": False}
    try:
        sd = torch.load(path, map_location="cpu", weights_only=False)
    except Exception as e:  # noqa: BLE001
        print(f"[resume] {path} unreadable ({e}); ignoring", flush=True)
        return None, {"found": True, "readable": False, "aborted": False}
    prev = sd.get("data_sha256")
    rec = {"found": True, "readable": True, "bind_enabled": bool(bind),
           "ckpt_data_sha256": prev, "current_data_sha256": data_sha,
           "ckpt_has_data_binding": bool(sd.get("data_binding"))}
    if bind and prev is not None and prev != data_sha:
        raise R3S2ContractError(
            f"CKPT DATA-HASH BIND: {path} was written against dataset content "
            f"{prev[:16]}... but the arrays on disk now hash to {data_sha[:16]}.... "
            "Refusing to resume or to silently restart: this is exactly the stale-"
            "checkpoint contamination of round-3 STOP-THE-LINE #2. Delete the ckpt dir "
            "deliberately if the data change was intended (recipe: ckpt dirs must be "
            "FRESH under .../B3/, never reused).")
    if bind and prev is None:
        print(f"[resume] {path} predates the data-hash bind; ignoring", flush=True)
        rec["aborted"] = False
        return None, rec
    got = {key: sd.get(key) for key in meta}
    if got == meta:
        print(f"[resume] using {path} (stage={sd.get('stage')})", flush=True)
        rec["aborted"] = False
        rec["resumed_stage"] = sd.get("stage")
        return sd, rec
    print(f"[resume] {path} meta mismatch; ignoring", flush=True)
    rec["aborted"] = False
    rec["meta_mismatch"] = True
    return None, rec


def train_stage(params, n: int, epochs: int, lr: float, tag: str, loss_fn,
                ckpt_write=None, resume=None, batch_size: int = None):
    """Shuffle-and-step loop, structure identical to the base family's."""
    params = [p for p in params if p.requires_grad]
    if n == 0 or epochs <= 0 or not params:
        return
    opt = torch.optim.AdamW(params, lr=lr, weight_decay=SMOKE["weight_decay"])
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max(epochs, 1), eta_min=1e-6)
    g = torch.Generator().manual_seed(0)   # base family convention
    bs = min(batch_size or SMOKE["batch_size"], n)
    start_ep = 0
    if resume is not None:
        opt.load_state_dict(resume["opt"])
        sched.load_state_dict(resume["sched"])
        g.set_state(resume["gen"].cpu() if torch.is_tensor(resume["gen"]) else resume["gen"])
        start_ep = int(resume["epoch"])
        print(f"[resume] {tag} continues from epoch {start_ep}/{epochs}", flush=True)
    save_every = max(1, epochs // CKPT_SAVES_PER_STAGE)
    for ep in range(start_ep, epochs):
        perm = torch.randperm(n, generator=g)
        tot, nb = 0.0, 0
        for i in range(0, n, bs):
            idx = perm[i:i + bs]
            opt.zero_grad(set_to_none=True)
            loss = loss_fn(idx)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(params, SMOKE["grad_clip"])
            opt.step()
            tot += float(loss.detach()); nb += 1
        sched.step()
        if (ep + 1) % max(1, epochs // 5) == 0 or ep == epochs - 1:
            print(f"[{tag} {ep+1:04d}/{epochs}] loss={tot/max(nb,1):.4e}", flush=True)
        if ckpt_write is not None and ((ep + 1) % save_every == 0 or ep == epochs - 1):
            ckpt_write(ep + 1, opt, sched, g)


def _resolve_repo_path(rel: str) -> Path:
    """Resolve a ROUND-STATE artifact (certified anchors, floors, noise floor,
    film denominator) against the MAIN checkout FIRST.

    Round state is maintained in the main tree and is re-certified during the
    round; a worktree carries only the frozen snapshot from its fork point. This
    worktree forked at round3-substrate 44f2404 (2026-08-07), which predates the
    2026-08-08 mce certification and the ADR r3-0005/r3-0007 updates — reading
    the worktree copy would silently price every clause against superseded
    thresholds (it makes `ifc_heat` look UNCERTIFIED when it is certified). Same
    hazard, same resolution as the `EVAL_DIR` note above. The worktree copy stays
    as the offline fallback, and the resolved path is recorded in the diag.
    """
    p = Path(rel)
    if p.is_absolute():
        return p
    for root in (_main_repo_root(), WORKTREE):
        cand = root / rel
        if cand.exists():
            return cand
    return _main_repo_root() / rel


def diag_base(knobs: dict) -> Path:
    raw = knobs["R3S2_DIAG_OUT"]
    p = Path(raw)
    return p if p.is_absolute() else _main_repo_root() / raw


def _read_param_names(ds_dir: Path):
    mp = Path(ds_dir) / "meta.json"
    if not mp.exists():
        return None, None
    try:
        meta = json.loads(mp.read_text())
    except Exception as e:  # noqa: BLE001
        raise R3S2ContractError(f"{mp} is unreadable ({e}); refusing to guess the IC columns")
    return meta.get("param_names"), str(mp)


def frac_reduction(a: float, b: float):
    a, b = float(a), float(b)
    if not np.isfinite(a) or a == 0.0:
        return None
    return (a - b) / a


# ── the run ──────────────────────────────────────────────────────────────


def run(args, out_path: Path) -> dict:                      # noqa: C901, PLR0912, PLR0915
    t0 = time.time()
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    knobs = read_knobs()
    name = args.dataset_name

    ds_dir = Path(args.dataset_dir)
    train = load_mf_dataset(ds_dir, "train")
    test = load_mf_dataset(ds_dir, "test")

    # ── V2 / R3S2B3_NO_TEST_LF_ASSERT: no non-HF test path is ever opened ──
    if test["lf_fids"]:
        raise R3S2ContractError(
            f"V2 violated on {name}: the test split exposes LF fidelities "
            f"{test['lf_fids']}. Round 3 evaluates ONLY against the stripped view; "
            "the ceiling rungs are measured on held-out TRAIN rows precisely because "
            "immutable #9 forbids this (card part 3, `Splits`).")
    hf = test["hf_fid"]
    if hf not in train["fids"]:
        raise R3S2ContractError(
            f"{name}: test HF fidelity {hf} absent from the train ladder {train['fids']}")
    if not train["lf_fids"]:
        raise R3S2ContractError(
            f"{name}: the TRAIN split has no LF fidelity; the emulator has no target")

    # ── the scored cell's rung, from panel_data.py (R3S2_EMU_RUNG) ────────
    rung_want = runglib.scored_rung(name, train["lf_fids"])
    lf_rung = int(rung_want["lf_rung"])

    hf_grid = resolve_grid(name, int(test["n_cells_by_fid"][hf]))
    grid = _cap_grid(hf_grid)
    if tuple(grid) != tuple(hf_grid):
        raise R3S2ContractError(
            f"the {WORK_CAP} cap fired on {name} ({hf_grid} -> {grid}); this family "
            "requires working grid == native HF grid so the vendored upsampler's "
            "output is byte-comparable to the eval layer's reference construction.")
    lf_grid = resolve_grid(name, int(train["n_cells_by_fid"][lf_rung]))
    min_fid = min(train["fids"])
    res_min_grid = resolve_grid(name, int(train["n_cells_by_fid"][min_fid]))
    H, W = int(grid[0]), int(grid[1])
    HW = H * W
    h, w = int(lf_grid[0]), int(lf_grid[1])

    if _truthy(knobs["S6_LEAKAGE_TRIPWIRE"]):
        if not ((h * w) < (H * W) and h <= H and w <= W):
            raise R3S2ContractError(
                f"leakage tripwire: LF rung {lf_rung} grid {lf_grid} is not strictly "
                f"coarser than HF {hf_grid} — refusing to run (immutable 1: LF is "
                "always the real coarse solve, never downsampled HF)")

    # ── arrays ───────────────────────────────────────────────────────────
    Y_tr = np.asarray(train["field_by_fid"][hf], dtype=np.float64)
    X_tr = np.asarray(train["cond_by_fid"][hf], dtype=np.float32)
    Y_te = np.asarray(test["field_by_fid"][hf], dtype=np.float64)
    X_te = np.asarray(test["cond_by_fid"][hf], dtype=np.float32)
    LF_nat_all = np.asarray(train["field_by_fid"][lf_rung], dtype=np.float64)
    X_lf_all = np.asarray(train["cond_by_fid"][lf_rung], dtype=np.float32)
    Ntr, Nte, N_lf = Y_tr.shape[0], Y_te.shape[0], LF_nat_all.shape[0]
    cond_dim = int(X_tr.shape[1])
    if int(X_lf_all.shape[1]) != cond_dim:
        raise R3S2ContractError(
            f"{name}: cond_dim differs across rungs ({X_lf_all.shape[1]} at LF rung "
            f"{lf_rung} vs {cond_dim} at HF) — one trunk cannot serve both")
    if Y_te.shape[1] != HW:
        raise R3S2ContractError(f"shape seam: HF test {Y_te.shape} vs grid {grid}")

    # ── R3S2B3_RUNG_LIFT_TRIPWIRE: rung AND lift == the scored cell's ────
    rung_lift_gate = runglib.tripwire(name, lf_rung, LF_nat_all, lf_grid, hf_grid,
                                      train["lf_fids"])
    print(f"[rung/lift] {name}: rung {lf_rung} ({rung_want['source']}), lift "
          f"{rung_lift_gate['family_convention']} == panel_data "
          f"{rung_lift_gate['eval_layer_up_fn']} (max|dev| "
          f"{rung_lift_gate['max_abs_lift_deviation']:.3e})", flush=True)

    data_sha = dataset_content_sha256({
        "Y_tr": Y_tr, "X_tr": X_tr, "Y_te": Y_te, "X_te": X_te,
        "LF_nat_all": LF_nat_all, "X_lf_all": X_lf_all,
        "fids": tuple(int(f) for f in train["fids"]), "hf_fid": int(hf),
        "lf_rung": int(lf_rung), "grid": (H, W), "lf_grid": (h, w),
    })
    print(f"[data-hash] {name} content sha256 = {data_sha}", flush=True)

    # ── the pairing gate (HF - LF_up must be a well-defined residual) ─────
    n_pair = min(N_lf, Ntr)
    pair_dev = (float(np.abs(X_lf_all[:n_pair].astype(np.float64)
                             - X_tr[:n_pair].astype(np.float64)).max())
                if n_pair else float("inf"))
    paired = bool(np.isfinite(pair_dev) and pair_dev <= PAIRED_COND_TOL and N_lf >= Ntr)
    pairing = {"paired_real_lf": paired, "max_abs_cond_deviation_lf_vs_hf": pair_dev,
               "tol": PAIRED_COND_TOL, "n_lf_samples": int(N_lf),
               "n_hf_train_samples": int(Ntr),
               "gate_armed": _truthy(knobs["R3S2_PAIRING_GATE"])}
    if not paired:
        raise R3S2ContractError(
            f"R3S2_PAIRING_GATE: {name} has an UNPAIRED LF ladder (max|dX| = {pair_dev!r} "
            f"> {PAIRED_COND_TOL}, N_lf={N_lf}, Ntr={Ntr}). Every rung of this ladder "
            "is defined on the paired residual; an unpaired cell is void, not defaulted.")
    print(f"[pairing] {name}: paired={paired} max|dX|={pair_dev:.3e} "
          f"(N_lf={N_lf}, Ntr={Ntr})", flush=True)

    # the REAL-LF base, lifted under the scored cell's convention
    up_fn_name = rung_lift_gate["family_convention"]
    LFr_tr = uplib.upsample_fields(LF_nat_all[:Ntr], lf_grid, grid, name)

    # ── the HOT plan (hot_split.py; the ONLY place the partition is decided) ─
    plan = hotlib.plan(name, Ntr, int(args.seed))
    print(f"[hot] {name}: protocol={plan['protocol']} n_fit={plan['n_fit']} "
          f"n_heldout={plan['n_heldout']} legs={plan['n_legs']} "
          f"registered_eligible={plan['registered_unit_eligible']}", flush=True)

    # ── IC synthesis (front end `ic_synth`, both routes) ─────────────────
    param_names, meta_path = _read_param_names(ds_dir)
    ic_layout = icsynth.resolve_ic_indices(param_names, cond_dim)
    ic_scale = knob_float(knobs, "R3S2_IC_SYNTH_SCALE")
    square_lf = (h == w) and (int(res_min_grid[0]) == int(res_min_grid[1])) and h > 1
    square_hf = (H == W) and (int(res_min_grid[0]) == int(res_min_grid[1])) and H > 1
    ic_applicable = bool(ic_layout["applicable"] and square_lf and square_hf)
    ic_record = dict(ic_layout)
    ic_record.update({
        "ic_synth_applicable": ic_applicable, "meta_json": meta_path,
        "res_min": int(res_min_grid[0]), "res_min_grid": list(res_min_grid),
        "stack_synth_res": int(h), "direct_synth_res": int(H), "scale": ic_scale,
        "square_lf": bool(square_lf), "square_hf": bool(square_hf),
        "fallback_note": ("R3S2_IC_FALLBACK=film_only_recorded: where the dataset has no "
                          "ic_c* dims the front end IS film_only, recorded, never a "
                          "second random init"),
        "scale_note": ("the generator's per-dataset IC amplitude and additive mean offset "
                       "are NOT reproduced (recorded, never silently absorbed)"),
    })

    def _coeffs(Xrows):
        return np.asarray(Xrows, dtype=np.float64)[:, ic_layout["ic_indices"]]

    ic_channels, ic_gates = {}, {}
    if ic_applicable:
        if _truthy(knobs["R3S2_IC_EQUIV_CHECK"]):
            ic_gates["equivalence"] = icsynth.equivalence_check(
                _coeffs(X_lf_all), h, int(res_min_grid[0]), ic_scale)
            print(f"[ic] equivalence (analytic vs zero-pad) max|delta|="
                  f"{ic_gates['equivalence']['max_abs_dev']:.3e}", flush=True)
        for split, Xs in (("lf", X_lf_all), ("tr", X_tr), ("te", X_te)):
            ic_channels[("stack", split)] = icsynth.ic_fields(
                _coeffs(Xs), h, int(res_min_grid[0]), ic_scale)
            ic_channels[("direct", split)] = icsynth.ic_fields(
                _coeffs(Xs), H, int(res_min_grid[0]), ic_scale)
    ic_record["gates"] = ic_gates

    def ic_tensor(route: str, split: str):
        if not ic_applicable:
            return None
        return torch.from_numpy(ic_channels[(route, split)].astype(np.float32)).unsqueeze(1)

    film_idx = ic_layout["other_indices"] if ic_applicable else None

    # ── periodicity + bands ──────────────────────────────────────────────
    pad = periodlib.decide_padding(knobs["S6_PAD_MODE"], Y_tr, grid,
                                   knob_float(knobs, "S6_PERIODIC_TOL"))
    padding_mode = pad["padding_decision"]
    band_edges = bandlib.check_edges_env(grid, knobs["S6_BAND_EDGES_FRAC"])
    band_masks_np, _, _ = bandlib.band_masks(grid, bandlib.N_BANDS)

    print(f"[data] {name} loader={train['loader']} LF rung={lf_rung} HF={hf} "
          f"lf_grid={lf_grid} hf_grid={hf_grid} Ntr={Ntr} Nte={Nte} N_lf={N_lf} "
          f"cond_dim={cond_dim} lift={up_fn_name} pad={padding_mode}", flush=True)

    # ── epoch budget (R3S2_EPOCH_SPLIT + R3S2_BUDGET_MATCH) ──────────────
    split_frac = knob_float(knobs, "R3S2_EPOCH_SPLIT")
    if not (0.0 < split_frac < 1.0):
        raise R3S2ContractError(f"R3S2_EPOCH_SPLIT={split_frac!r} must be in (0, 1)")
    E_emu = max(1, int(round(int(args.epochs) * split_frac)))
    E_dc = max(1, int(args.epochs) - E_emu)
    E_corr = max(1, E_dc // 2)
    E_gate = max(1, E_dc - E_dc // 2)
    E_stage2 = E_emu + 2 * E_dc            # the recipe's 300 at tier 200
    E_direct = E_stage2                    # R3S2_BUDGET_MATCH = arm_equal_total
    budget = {"epochs_tier": int(args.epochs), "split": split_frac,
              "emulator": E_emu, "dc_stage_total": E_dc, "corrector": E_corr,
              "gate": E_gate, "stage2_total": E_stage2, "direct_total": E_direct,
              "budget_match": knobs["R3S2_BUDGET_MATCH"],
              "rung_optimizer_epochs": {
                  "R0_absent": E_direct, "R1_predicted": E_stage2,
                  "R1b_degraded": E_emu, "R2_oracle": E_stage2, "R2b_copylf": 0},
              "recipe_declared_stage2_epochs_at_tier_200": 300,
              "note": ("R0 (the no-LF denominator) and R1 (the deployed route) spend the "
                       "SAME optimizer-epoch total, so the ceiling ratio is not a budget "
                       "ratio (round-2 caveat F8). R2_oracle reuses R1's frozen corrector "
                       "and adds ZERO epochs; R2b_copylf has zero parameters.")}
    if budget["rung_optimizer_epochs"]["R0_absent"] != \
            budget["rung_optimizer_epochs"]["R1_predicted"]:
        raise R3S2ContractError(
            "V11: R3S2_BUDGET_MATCH=arm_equal_total but R0 and R1 differ in total epochs")
    print(f"[budget] emulator={E_emu} dc={E_dc} (corr={E_corr} gate={E_gate}) "
          f"R0/R1 spend {E_stage2} each", flush=True)

    # ── checkpointing (+ batch-3 contract: the ckpt_binding save hook) ────
    ckpt_dir = Path(args.ckpt_dir); ckpt_dir.mkdir(parents=True, exist_ok=True)
    ck_last = ckpt_dir / "last.pt"
    bind = _truthy(knobs["R3S2B3_CKPT_DATA_HASH_BIND"])
    meta = {"dataset": name, "seed": int(args.seed), "epochs_target": int(args.epochs),
            "grid": list(grid), "lf_grid": list(lf_grid), "lf_rung": int(lf_rung),
            "padding_mode": padding_mode, "paired_real_lf": paired,
            "ic_applicable": ic_applicable, "hot_protocol": plan["protocol"],
            "n_legs": int(plan["n_legs"]),
            "data_sha256": data_sha, "family": MODEL_NAME}
    # `R3S2B3_CKPT_BINDING=1` / batch-3 scope rule 2: `data_binding` goes into
    # last.pt at EVERY save, so tools/zero_work_resume_scan.py --verify-binding
    # can adjudicate a resume without the family emitting anything else. The arm
    # is the UNION role over the five rungs (R3S2B3_ROLES_READ): the job as a
    # whole reads train LF, so a train_lf change must read RETRAIN.
    roles_by_rung = dict(kv.split("=", 1) for kv in knobs["R3S2B3_ROLES_READ"].split(","))
    binding_block = {}
    binding_error = None
    try:
        binding_block = bindlib.binding_block(
            ds_dir, name, bindlib.roles_read_for("lf_at_train"))
    except Exception as e:  # noqa: BLE001
        binding_error = f"{type(e).__name__}: {e}"
        print(f"[ckpt-binding] WARNING: {binding_error}", flush=True)

    STAGE_ORDER = ["init"]
    for lg in plan["legs"]:
        STAGE_ORDER += [f"leg_{lg['leg_id']}", f"leg_{lg['leg_id']}_done"]
    STAGE_ORDER += ["done"]
    STAGES = {s: i for i, s in enumerate(STAGE_ORDER)}
    ck, resume_record = load_ckpt_checked(ck_last, meta, data_sha, bind)
    ck_stage = (ck or {}).get("stage", "init")
    ck_rank = STAGES.get(ck_stage, 0)
    acc: dict = {}

    def _ckpt_payload(stage: str, extra: dict = None) -> dict:
        # `update`, NOT `dict(meta, **acc, **extra)`: from the second train-rows
        # group onwards (the enumerated ifc folds) `acc` already carries keys the
        # current stage re-emits (`s_emu`, `s_y_direct`), and the kwargs form
        # raises TypeError on the duplicate. Later writers win, which is the
        # intended precedence: the stage being checkpointed is authoritative.
        p = dict(meta)
        p.update(acc)
        p.update(extra or {})
        p["stage"] = stage
        if binding_block:
            p["data_binding"] = {name: binding_block}
            p["data_binding_roles_by_rung"] = roles_by_rung
        return p

    def persist(stage: str, **extra) -> None:
        acc.update(extra)
        _save_ckpt(ck_last, _ckpt_payload(stage))

    persist("init")

    # ── training-free probes (unchanged instruments) ─────────────────────
    probes = {"P2_cond_lf_identifiability": probelib.cond_lf_identifiability(
        X_lf_all.astype(np.float64), LF_nat_all)}

    kcut_rec = lsilib.kcut_from_ladder(lf_grid, grid)
    emu_modes = knob_int(knobs, "R3S2_EMU_MODES")
    mh, mw = _modes(lf_grid, emu_modes)
    mh_hf, mw_hf = _modes(grid, emu_modes)
    emu_width = knob_int(knobs, "R3S2_EMU_WIDTH")
    emu_blocks = knob_int(knobs, "R3S2_EMU_BLOCKS")
    kernel = knob_int(knobs, "S6_KERNEL")
    depth = knob_int(knobs, "S6_DEPTH")
    width = knob_int(knobs, "S6_WIDTH")
    holdout_frac = knob_float(knobs, "S6_GATE_HOLDOUT_FRAC")
    bs = SMOKE["batch_size"]
    Xt_tr = torch.from_numpy(X_tr)
    Xt_te = torch.from_numpy(X_te)
    ic_lf, ic_tr_s, ic_te_s = (ic_tensor("stack", "lf"), ic_tensor("stack", "tr"),
                               ic_tensor("stack", "te"))
    ic_tr_d, ic_te_d = ic_tensor("direct", "tr"), ic_tensor("direct", "te")

    def _inner_split(rows: np.ndarray):
        """val_a / val_b / fit sub-slices INSIDE a leg's train rows (base family
        protocol: S6_GATE_HOLDOUT_FRAC, R3S2_VAL_DISJOINT)."""
        rows = np.asarray(rows, dtype=np.int64)
        n = len(rows)
        if n < 3:
            raise R3S2ContractError(
                f"{name}: a leg has {n} train rows; R3S2_VAL_DISJOINT=1 needs >= 3")
        order = np.random.default_rng(
            hotlib.split_key(name, int(args.seed)) + 7919).permutation(n)
        n_val = min(int(max(1, round(holdout_frac * n))), max(n - 1, 0))
        target = max(2, n_val - (n_val % 2))
        target = min(target, (n - 1) - ((n - 1) % 2))
        n_val = target
        v = rows[order[:n_val]]
        f = rows[order[n_val:]]
        return np.sort(f), np.sort(v[:n_val // 2]), np.sort(v[n_val // 2:])

    # ══ per-leg machinery ════════════════════════════════════════════════
    neural_cache: dict = {}
    train_seconds_acc, t_train0 = 0.0, time.time()

    def _new_modules():
        c = LocalCorrector(cond_dim, grid, width=width, depth=depth, kernel=kernel,
                           padding_mode=padding_mode).to(device)
        g = PixelGate(cond_dim, grid, width=width, kernel=kernel,
                      padding_mode=padding_mode).to(device)
        return c, g

    def _delta(corrector, LFn, Xsrc, n, scaler_r) -> np.ndarray:
        corrector.eval()
        out = np.empty((n, HW), dtype=np.float64)
        with torch.no_grad():
            for i in range(0, n, bs):
                sl = slice(i, min(i + bs, n))
                d = corrector(LFn[sl].to(device), Xsrc[sl].to(device))
                blk = d.reshape(d.shape[0], -1).double().cpu().numpy()
                s = (scaler_r[sl] if isinstance(scaler_r, np.ndarray) else scaler_r)
                out[sl] = blk * s
        return out

    def _gate_out(gate, LFn, Xsrc, n) -> np.ndarray:
        gate.eval()
        out = np.empty((n, HW), dtype=np.float64)
        with torch.no_grad():
            for i in range(0, n, bs):
                sl = slice(i, min(i + bs, n))
                g = gate(LFn[sl].to(device), Xsrc[sl].to(device))
                out[sl] = g.reshape(g.shape[0], -1).double().cpu().numpy()
        return out

    def build_neural(train_rows: np.ndarray, heldout: np.ndarray, T_seed,
                     stage: str, resume_ck):
        """Train the three GPU stages on `train_rows` ONLY.

        `heldout` never enters any of them: it is excluded from the emulator's LF
        fit slice, from the corrector's fit slice, and from the direct head's rows.
        `T_seed` is the leg-0 transfer function used to define the corrector's
        residual target; the per-leg transfer functions are closed form and are
        re-derived outside this function.
        """
        fit_rows, val_a, val_b = _inner_split(train_rows)
        val_rows = np.sort(np.concatenate([val_a, val_b]))

        # --- stage 1: the pseudo-LF emulator (LF rows, H excluded) ---------
        forbidden = set(int(i) for i in heldout.tolist()) | set(int(i) for i in val_rows.tolist())
        emu_fit = np.array([i for i in range(N_lf) if i not in forbidden], dtype=np.int64)
        emu_val = np.array(sorted(int(i) for i in val_rows if int(i) < N_lf), dtype=np.int64)
        if not len(emu_fit):
            raise R3S2ContractError(f"{name}: empty emulator fit slice on stage {stage}")
        s_emu = max(float(np.abs(LF_nat_all[emu_fit]).max()), 1e-8)
        Xl = torch.from_numpy(X_lf_all)
        Yl = torch.from_numpy((LF_nat_all / s_emu).astype(np.float32)).view(N_lf, h, w)
        emu_fit_t = torch.from_numpy(np.ascontiguousarray(emu_fit))
        net = Emulator(FRONT_END if ic_applicable else "film_only", cond_dim, film_idx,
                       lf_grid, emu_width, emu_blocks, mh, mw).to(device)
        if resume_ck is not None and resume_ck.get(stage + "_emu") is not None:
            net.load_state_dict(resume_ck[stage + "_emu"])

        def _emu_loss(idx):
            net.train()
            sel = emu_fit_t[idx]
            extra = None if ic_lf is None else ic_lf[sel].to(device)
            p = net(Xl[sel].to(device), extra)
            t = Yl[sel].to(device)
            num = (p - t).reshape(p.shape[0], -1).norm(dim=1)
            den = t.reshape(t.shape[0], -1).norm(dim=1).clamp_min(1e-8)
            return (num / den).mean()

        def _emu_writer(epoch, opt, sched, g):
            _save_ckpt(ck_last, _ckpt_payload(
                stage, {stage + "_emu": net.state_dict(), "s_emu": s_emu,
                        "substage": "emu", "epoch": int(epoch), "opt": opt.state_dict(),
                        "sched": sched.state_dict(), "gen": g.get_state()}))

        resume = (({k: resume_ck[k] for k in ("opt", "sched", "gen", "epoch")})
                  if (resume_ck is not None and resume_ck.get("substage") == "emu"
                      and "opt" in resume_ck) else None)
        print(f"[{stage}] emulator on {len(emu_fit)} LF rows at rung {lf_rung} "
              f"({h}x{w}), modes {mh}x{mw}", flush=True)
        train_stage(list(net.parameters()), len(emu_fit), E_emu, LR_EMULATOR,
                    f"{stage}/emu", _emu_loss, ckpt_write=_emu_writer, resume=resume)
        net.eval()

        def emu_native(X, ic) -> np.ndarray:
            Xt = torch.from_numpy(np.asarray(X, dtype=np.float32))
            out = np.empty((Xt.shape[0], h * w), dtype=np.float64)
            with torch.no_grad():
                for i in range(0, Xt.shape[0], bs):
                    sl = slice(i, min(i + bs, Xt.shape[0]))
                    extra = None if ic is None else ic[sl].to(device)
                    p = net(Xt[sl].to(device), extra) * s_emu
                    out[sl] = p.reshape(p.shape[0], -1).double().cpu().numpy()
            return out

        LFp_tr = uplib.upsample_fields(emu_native(X_tr, ic_tr_s), lf_grid, grid, name)
        LFp_te = uplib.upsample_fields(emu_native(X_te, ic_te_s), lf_grid, grid, name)

        # V6: the pseudo-LF path must carry sample-specific signal
        if _truthy(knobs["R3S2_REQUIRE_PSEUDO_LF"]):
            if LFp_te.shape != (Nte, HW) or not np.isfinite(LFp_te).all():
                raise R3S2ContractError(
                    f"V6 violated on {name}: pseudo-LF test field is {LFp_te.shape} "
                    "/ non-finite")
            if not (float(LFp_te.std(axis=0).max()) > 0.0):
                raise R3S2ContractError(
                    f"V6 violated on {name}: the pseudo-LF test field has ZERO across-"
                    "sample variance — it collapsed to a constant and the route is a no-op")
        # V1: the pseudo-LF is exactly the lifted emulator output
        v1_dev = float(np.abs(
            LFp_te - uplib.upsample_fields(emu_native(X_te, ic_te_s), lf_grid, grid, name)
        ).max())
        if v1_dev != 0.0:
            raise R3S2ContractError(
                f"V1 violated on {name}: the pseudo-LF test field deviates from an "
                f"independently re-derived upsampled emulator output by {v1_dev!r}")

        # --- stage 2: the frozen defect corrector (fit on REAL LF) --------
        C_seed = lsilib.apply_transfer(LFr_tr, T_seed, grid)
        a_seed, _, _, _ = fit_alpha(Y_tr[val_a] - LFr_tr[val_a], C_seed[val_a],
                                    LFr_tr[val_a], Y_tr[val_a], include_zero=True)
        RES_tr = (Y_tr - LFr_tr) - float(a_seed) * C_seed
        ts_dec = tslib.decide(name, RES_tr[fit_rows], knobs["R3S2_TARGET_SCALER_PREFLIGHT"])
        if ts_dec["per_sample"]:
            scaler_r_fit = np.asarray(ts_dec["scaler"], dtype=np.float64).reshape(-1)
            scaler_full = np.ones((Ntr,), dtype=np.float64) * float(np.median(scaler_r_fit))
            scaler_full[fit_rows] = scaler_r_fit
            scaler_r = scaler_full
            RESn_np = RES_tr / scaler_r[:, None]
        else:
            scaler_r = float(ts_dec["scaler"])
            RESn_np = RES_tr / scaler_r
        scaler_lf = max(float(np.abs(LFr_tr).max()), 1e-8)
        LFn = torch.from_numpy((LFr_tr / scaler_lf).astype(np.float32)).view(Ntr, H, W)
        RESn = torch.from_numpy(RESn_np.astype(np.float32)).view(Ntr, H, W)
        corrector, gate = _new_modules()
        if resume_ck is not None and resume_ck.get(stage + "_corr") is not None:
            corrector.load_state_dict(resume_ck[stage + "_corr"])
            gate.load_state_dict(resume_ck[stage + "_gate"])
        fit_t = torch.from_numpy(np.ascontiguousarray(fit_rows))

        def _dc_writer(sub):
            def _w(epoch, opt, sched, g):
                _save_ckpt(ck_last, _ckpt_payload(
                    stage, {stage + "_emu": net.state_dict(), "s_emu": s_emu,
                            stage + "_corr": corrector.state_dict(),
                            stage + "_gate": gate.state_dict(),
                            "substage": sub, "epoch": int(epoch), "opt": opt.state_dict(),
                            "sched": sched.state_dict(), "gen": g.get_state()}))
            return _w

        def corr_loss(idx):
            corrector.train()
            sel = fit_t[idx]
            d = corrector(LFn[sel].to(device), Xt_tr[sel].to(device))
            return F.mse_loss(d, RESn[sel].to(device))

        print(f"[{stage}] corrector: fit={len(fit_rows)} rf={corrector.receptive_field} "
              f"pad={padding_mode} scaler={tslib.scaler_summary(ts_dec)}", flush=True)
        train_stage(list(corrector.parameters()), len(fit_rows), E_corr, LR_CORRECTOR,
                    f"{stage}/corrector", corr_loss, ckpt_write=_dc_writer("corrector"),
                    resume=(resume_ck if (resume_ck or {}).get("substage") == "corrector"
                            else None))
        for p in corrector.parameters():
            p.requires_grad_(False)
        corrector.eval()

        def gate_loss(idx):
            gate.train()
            sel = fit_t[idx]
            lb, xb = LFn[sel].to(device), Xt_tr[sel].to(device)
            with torch.no_grad():
                d = corrector(lb, xb)
            return F.mse_loss(gate(lb, xb) * d, RESn[sel].to(device))

        train_stage(list(gate.parameters()), len(fit_rows), E_gate, LR_GATE,
                    f"{stage}/gate", gate_loss, ckpt_write=_dc_writer("gate"),
                    resume=(resume_ck if (resume_ck or {}).get("substage") == "gate"
                            else None))
        for p in corrector.parameters():
            p.requires_grad_(True)
        gate.eval()

        # --- stage 3: R0, the no-LF denominator, at the matched budget ----
        rows_rec = directlib.train_rows(len(train_rows), np.arange(len(fit_rows)),
                                        np.arange(len(fit_rows),
                                                  len(fit_rows) + len(val_rows)),
                                        DIRECT_VAL_THRESHOLD)
        d_rows = (fit_rows if rows_rec["val_disjoint"] else np.sort(train_rows))
        s_y_direct = max(float(np.abs(Y_tr[d_rows]).max()), 1e-8)
        Yd = torch.from_numpy((Y_tr / s_y_direct).astype(np.float32)).view(Ntr, H, W)
        d_rows_t = torch.from_numpy(np.ascontiguousarray(d_rows))
        dnet = directlib.build(FRONT_END if ic_applicable else "film_only", cond_dim,
                               film_idx, grid, emu_width, emu_blocks, mh_hf, mw_hf, device)
        if resume_ck is not None and resume_ck.get(stage + "_direct") is not None:
            dnet.load_state_dict(resume_ck[stage + "_direct"])

        def _dloss(idx):
            dnet.train()
            sel = d_rows_t[idx]
            extra = None if ic_tr_d is None else ic_tr_d[sel].to(device)
            p = dnet(Xt_tr[sel].to(device), extra)
            return directlib.rel_l2_loss(p, Yd[sel].to(device))

        def _direct_writer(epoch, opt, sched, g):
            _save_ckpt(ck_last, _ckpt_payload(
                stage, {stage + "_emu": net.state_dict(), "s_emu": s_emu,
                        stage + "_corr": corrector.state_dict(),
                        stage + "_gate": gate.state_dict(),
                        stage + "_direct": dnet.state_dict(), "s_y_direct": s_y_direct,
                        "substage": "direct", "epoch": int(epoch), "opt": opt.state_dict(),
                        "sched": sched.state_dict(), "gen": g.get_state()}))

        print(f"[{stage}] R0 direct cond->HF on {len(d_rows)} HF rows at {H}x{W}, "
              f"{E_direct} epochs ({rows_rec['rule']})", flush=True)
        train_stage(list(dnet.parameters()), len(d_rows), E_direct, LR_DIRECT,
                    f"{stage}/direct", _dloss, ckpt_write=_direct_writer,
                    resume=(resume_ck if (resume_ck or {}).get("substage") == "direct"
                            and "opt" in (resume_ck or {}) else None))
        dnet.eval()
        direct_tr = directlib.predict(dnet, X_tr, ic_tr_d, s_y_direct, grid, device, bs)
        direct_te = directlib.predict(dnet, X_te, ic_te_d, s_y_direct, grid, device, bs)
        v15 = float(np.abs(direct_te - directlib.predict(
            dnet, X_te, ic_te_d, s_y_direct, grid, device, bs)).max())
        if v15 != 0.0:
            raise R3S2ContractError(
                f"V15 violated on {name}: R0 is not reproducible from an independent "
                f"forward pass (max|delta| = {v15!r})")

        return {
            "fit_rows": fit_rows, "val_a": val_a, "val_b": val_b, "val_rows": val_rows,
            "emu_fit": emu_fit, "emu_val": emu_val, "s_emu": s_emu,
            "LFp_tr": LFp_tr, "LFp_te": LFp_te,
            "emu_heldout_nrmse": (round_nrmse(emu_native(X_lf_all[emu_val],
                                                         None if ic_lf is None
                                                         else ic_lf[torch.from_numpy(emu_val)]),
                                              LF_nat_all[emu_val])
                                  if len(emu_val) else None),
            "corrector": corrector, "gate": gate, "scaler_lf": scaler_lf,
            "scaler_r": scaler_r, "target_scale": ts_dec,
            "direct_tr": direct_tr, "direct_te": direct_te,
            "direct_rows": rows_rec, "n_direct_rows": int(len(d_rows)),
            "s_y_direct": s_y_direct,
            "n_params": {"emulator": int(param_count(net)),
                         "corrector": int(param_count(corrector)),
                         "gate": int(param_count(gate)),
                         "direct": int(param_count(dnet))},
            "corrector_state_sha256": state_sha256(corrector.state_dict()),
            "gate_state_sha256": state_sha256(gate.state_dict()),
            "v1_pseudo_lf_reproducible": v1_dev, "v15_direct_reproducible": v15,
            "_states": {stage + "_emu": net.state_dict(),
                        stage + "_corr": corrector.state_dict(),
                        stage + "_gate": gate.state_dict(),
                        stage + "_direct": dnet.state_dict(),
                        "s_emu": s_emu, "s_y_direct": s_y_direct},
        }

    def dc_predict(nn_stage: dict, T, a_lsi: float, a_nn: float,
                   LF_in: np.ndarray, Xsrc: torch.Tensor) -> np.ndarray:
        n = LF_in.shape[0]
        if int(Xsrc.shape[0]) != n:
            raise R3S2ContractError(
                f"dc_predict: {n} LF rows but {int(Xsrc.shape[0])} condition rows — "
                "the FiLM conditioning would be mispaired")
        C = float(a_lsi) * lsilib.apply_transfer(LF_in, T, grid)
        LFn_i = torch.from_numpy(
            (LF_in / nn_stage["scaler_lf"]).astype(np.float32)).view(n, H, W)
        sr = nn_stage["scaler_r"]
        sr_i = (float(np.median(sr)) if isinstance(sr, np.ndarray) else sr)
        D = _delta(nn_stage["corrector"], LFn_i, Xsrc, n, sr_i)
        G = _gate_out(nn_stage["gate"], LFn_i, Xsrc, n)
        return LF_in + C + float(a_nn) * G * D

    # a seed transfer function so the corrector's residual target exists before
    # any per-leg selection: fitted on the FIRST leg's fit rows at ridge 0, which
    # is the literal B1 estimator and is replaced per leg immediately after.
    T_seed = lsilib.fit_transfer(
        LFr_tr[plan["legs"][0]["fit_rows"]],
        (Y_tr - LFr_tr)[plan["legs"][0]["fit_rows"]], grid, ridge=0.0)

    # How many legs share one neural-stage train-row set. The stages are cached
    # by that key, so a leg's stages are shared iff its key is carried by more
    # than one leg -- ALL FIVE sharp legs (they share T = 320) and NO ifc leg
    # (every C(5,3) fold has its own T). The previous expression
    # (`len(neural_cache) > 1 or not retrain_neural_stages`) reported the exact
    # opposite on both cell shapes; code-review downstream note, no consumer.
    leg_key_counts = Counter(tuple(int(v) for v in lg["train_rows"])
                             for lg in plan["legs"])

    legs_out = []
    primary_test_pred = None
    for lg in plan["legs"]:
        stage = f"leg_{lg['leg_id']}"
        key = tuple(int(v) for v in lg["train_rows"])
        if key not in neural_cache:
            resume_ck = ck if (ck is not None and ck.get("stage") == stage) else None
            neural_cache[key] = build_neural(lg["train_rows"], lg["heldout"], T_seed,
                                             stage, resume_ck)
            persist(stage + "_done", **neural_cache[key]["_states"])
        nn_stage = neural_cache[key]
        shared = bool(leg_key_counts[key] > 1)

        # --- the D2 selection: on the EMULATOR's held-out output ----------
        # F1 REPAIR (code review of 89c9fb3d; operator decision 2026-08-11
        # "VAL_ROWS RESTRICTION"). `hot_split`'s folds are out of sample for the
        # TRANSFER fit only; the emulator's fit slice is
        # `range(N_lf) \ (heldout u val_rows)`, so an unrestricted fold hands the
        # criterion IN-SAMPLE pseudo-LF on every row that is neither held out nor
        # a val row (measured before the repair: 256/320 sharp, 10/30 ifc). The
        # selection side is therefore intersected with the leg's OWN `val_rows`,
        # which the emulator is forbidden to fit, and `d2_select.select` then
        # REFUSES if anything is still inside `emu_fit`. The comparand runs on
        # the identical restricted folds so the pair stays attributable.
        sel_folds_used, restrict_rec = d2lib.restrict_folds_to_rows(
            lg["sel_folds"], nn_stage["val_rows"])
        if not sel_folds_used:
            raise R3S2ContractError(
                f"{name} leg {lg['leg_id']}: the F1 val-rows restriction leaves NO "
                f"selection fold ({restrict_rec}). Refusing to fall back to the "
                "unrestricted (emulator-in-sample) folds -- assert, never default.")
        bandlimit_grid = [s.strip() for s in knobs["S6_LSI_BANDLIMIT_GRID"].split(",")]
        sel = d2lib.select(LFr_tr, nn_stage["LFp_tr"], Y_tr, grid, sel_folds_used,
                           knobs["S6_LSI_RIDGE_GRID"], kcut_rec["k_cut"],
                           bandlimit_grid=bandlimit_grid,
                           select_on="emulator_heldout_output",
                           emu_fit_rows=nn_stage["emu_fit"])
        comparand = d2lib.select(LFr_tr, nn_stage["LFp_tr"], Y_tr, grid, sel_folds_used,
                                 knobs["S6_LSI_RIDGE_GRID"], kcut_rec["k_cut"],
                                 bandlimit_grid=bandlimit_grid,
                                 select_on="real_lf")
        sel["fold_restriction"] = restrict_rec
        sel["n_sel_rows_in_emu_fit"] = 0
        sel["n_sel_rows_declared_before_repair"] = restrict_rec["n_sel_rows_before"]
        T_leg = d2lib.final_transfer(LFr_tr, Y_tr, grid, lg["fit_rows"], sel)
        if sel["selected_bandlimit"] == "on":
            lsilib.assert_bandlimited(T_leg, grid, kcut_rec["k_cut"])

        # --- the two closed-form gains, on the leg's own val slices ------
        va, vb = nn_stage["val_a"], nn_stage["val_b"]
        C_raw = lsilib.apply_transfer(LFr_tr, T_leg, grid)
        a_lsi, a_lsi_ls, _, _ = fit_alpha(Y_tr[va] - LFr_tr[va], C_raw[va],
                                          LFr_tr[va], Y_tr[va], include_zero=True)
        base_tr = LFr_tr + float(a_lsi) * C_raw
        sr = nn_stage["scaler_r"]
        sr_i = (float(np.median(sr)) if isinstance(sr, np.ndarray) else sr)
        vb_t = torch.from_numpy(np.ascontiguousarray(vb))
        LFn_vb = torch.from_numpy(
            (LFr_tr[vb] / nn_stage["scaler_lf"]).astype(np.float32)).view(len(vb), H, W)
        NN_val = (_gate_out(nn_stage["gate"], LFn_vb, Xt_tr[vb_t], len(vb))
                  * _delta(nn_stage["corrector"], LFn_vb, Xt_tr[vb_t], len(vb), sr_i))
        a_nn, a_nn_ls, _, _ = fit_alpha(Y_tr[vb] - base_tr[vb], NN_val, base_tr[vb],
                                        Y_tr[vb], include_zero=True)

        # --- the five rungs on the held-out TRAIN rows -------------------
        Hh = np.asarray(lg["heldout"], dtype=np.int64)
        Xh = Xt_tr[torch.from_numpy(np.ascontiguousarray(Hh))]
        pred_H = {
            "R0_absent": nn_stage["direct_tr"][Hh],
            "R1_predicted": dc_predict(nn_stage, T_leg, a_lsi, a_nn,
                                       nn_stage["LFp_tr"][Hh], Xh),
            "R1b_degraded": nn_stage["LFp_tr"][Hh],
            "R2_oracle": dc_predict(nn_stage, T_leg, a_lsi, a_nn, LFr_tr[Hh], Xh),
            "R2b_copylf": LFr_tr[Hh],
        }
        nr_H = {k: round_nrmse(v, Y_tr[Hh]) for k, v in pred_H.items()}
        # --- the three DEPLOYABLE rungs on the stripped test split -------
        pred_te = {
            "R0_absent": nn_stage["direct_te"],
            "R1_predicted": dc_predict(nn_stage, T_leg, a_lsi, a_nn,
                                       nn_stage["LFp_te"], Xt_te),
            "R1b_degraded": nn_stage["LFp_te"],
        }
        nr_te = {k: round_nrmse(v, Y_te) for k, v in pred_te.items()}
        if primary_test_pred is None:
            primary_test_pred = pred_te["R1_predicted"]

        stats = ladderlib.leg_stats(nr_H)
        legs_out.append({
            "leg_id": lg["leg_id"],
            "n_fit_rows": int(len(lg["fit_rows"])), "n_heldout": int(len(Hh)),
            "fit_rows": [int(v) for v in lg["fit_rows"]],
            "heldout_rows": [int(v) for v in Hh],
            "nrmse": nr_H, "nrmse_test": nr_te, "stats": stats,
            "alpha_lsi": float(a_lsi), "alpha_lsi_ls": float(a_lsi_ls),
            "alpha_nn": float(a_nn), "alpha_nn_ls": float(a_nn_ls),
            "d2_selection": {k: v for k, v in sel.items() if k != "table"},
            "d2_selection_table": sel["table"],
            "d2_comparand_real_lf": {k: v for k, v in comparand.items() if k != "table"},
            "d2_repair_moved_selection": bool(
                sel["selected_ridge"] != comparand["selected_ridge"]
                or sel["selected_bandlimit"] != comparand["selected_bandlimit"]),
            "neural_stages_shared_with_other_legs": shared,
            "emulator_heldout_nrmse": nn_stage["emu_heldout_nrmse"],
            "band_err_energy": {k: bandlib.band_error_energy(v - Y_tr[Hh], grid)
                                for k, v in pred_H.items()},
        })
        print(f"[leg {lg['leg_id']}] " + " ".join(
            f"{k}={v:.6f}" for k, v in nr_H.items())
            + f" | phi_ceil={stats['phi_ceil']} rho={stats['rho']}", flush=True)
        persist(stage + "_done")

    train_seconds_acc = time.time() - t_train0

    # ══ statistics, units, clauses ═══════════════════════════════════════
    film = ladderlib.load_film(
        _resolve_repo_path(knobs["R3S2B3_FILM_DENOM_JSON"]), name)
    floor = ladderlib.load_floor(
        _resolve_repo_path(knobs["R3S2B3_NOISE_FLOOR_JSON"]), name)
    tau = ladderlib.thresholds(film, floor)

    for lg in legs_out:
        lg["skill_film"] = {k: ladderlib.skill_film(v, film) for k, v in lg["nrmse"].items()}
        lg["skill_film_test"] = {k: ladderlib.skill_film(v, film)
                                 for k, v in lg["nrmse_test"].items()}

    # C3 -- the split-transfer LICENCE
    tol = knob_float(knobs, "R3S2B3_SPLIT_TRANSFER_TOL_LOGRATIO")
    st_legs = []
    for lg in legs_out:
        h0, h1 = lg["nrmse"]["R0_absent"], lg["nrmse"]["R1_predicted"]
        t0_, t1 = lg["nrmse_test"]["R0_absent"], lg["nrmse_test"]["R1_predicted"]
        ok_rank = None
        gap = None
        if all(isinstance(v, float) and np.isfinite(v) and v > 0
               for v in (h0, h1, t0_, t1)):
            ok_rank = bool((h1 < h0) == (t1 < t0_))
            gap = abs(math.log(h1 / t1) - math.log(h0 / t0_))
        st_legs.append({"leg_id": lg["leg_id"], "rank_agrees": ok_rank,
                        "abs_log_ratio_gap": gap,
                        "within_tolerance": (None if gap is None else bool(gap <= tol))})
    ranks = [s["rank_agrees"] for s in st_legs if s["rank_agrees"] is not None]
    gaps = [s["abs_log_ratio_gap"] for s in st_legs if s["abs_log_ratio_gap"] is not None]
    split_transfer = {
        "per_leg": st_legs,
        "all_ranks_agree": (bool(all(ranks)) if ranks else None),
        "max_abs_log_ratio_gap": (max(gaps) if gaps else None),
        "passes": (bool(ranks and all(ranks) and gaps and max(gaps) <= tol)
                   if (ranks and gaps) else None),
        "knob": knobs["R3S2B3_SPLIT_TRANSFER_GATE"],
        "note": ("a cell failing C3 ships its ceiling REPORT-ONLY: the failure voids the "
                 "INSTRUMENT (does the held-out-train ceiling transfer to test?) and not "
                 "the hypothesis, and is reported as such (card `expected_falsification` "
                 "secondary falsifier)."),
    }

    # C4 -- the mandatory floor arms
    # MAIN checkout first, for the reason in `_resolve_repo_path`: the certified
    # floor table is round state, and this worktree's copy is a fork-time snapshot.
    floors = floorlib.collect(name, [_main_repo_root(), WORKTREE],
                              knobs["R3S2_FLOOR_ARMS"])
    mean_test = {}
    for rung in ladderlib.DEPLOYABLE:
        vals = [lg["nrmse_test"][rung] for lg in legs_out
                if isinstance(lg["nrmse_test"].get(rung), float)]
        mean_test[rung] = (float(np.mean(vals)) if vals else None)
    floors_beat = {rung: (floorlib.beat_table(v, floors) if v is not None else {})
                   for rung, v in mean_test.items()}

    # F2 -- the two declared-but-inert knobs, computed (all closed form, ZERO GPU):
    #   `R3S2B3_IFC_LOO_DISCLOSURE = enumerate_C5_4` -> the disclosure legs the
    #      run loop above does not walk are scored here, giving the ifc
    #      `affine_on_hf_train` LOO FOLD RANGE that program.md §2 makes mandatory;
    #   `R3S2B3_G5_BAND_DISCLOSURE = 1`  -> every floor-arm margin in C4 now
    #      carries that arm's own fit-set band at the `R3S2B3_FLOOR_MATCHED_N`
    #      size, instead of a prose sentence.
    # `model_beats_floor` (and therefore the registration predicate) keeps reading
    # the CERTIFIED full-fit floor: the disclosure informs the margin, it does not
    # redefine the gate.
    # The conditions are re-read at float64 from the loader (NOT `X_tr`, which the
    # trunk keeps at float32): the certified floor table and
    # `tools/fitset_matched_n_audit.py` both build these arms from float64
    # conditions, and a matched-n number is only comparable to the full-fit one it
    # is differenced against if the two share that construction exactly.
    C_tr64 = np.asarray(train["cond_by_fid"][hf], dtype=np.float64)
    C_te64 = np.asarray(test["cond_by_fid"][hf], dtype=np.float64)
    disclosure_block = fmnlib.disclosure_legs(plan, C_tr64, Y_tr, C_te64, Y_te)
    g5_band = fmnlib.matched_n_band(plan, name, knobs["R3S2B3_FLOOR_MATCHED_N"],
                                    C_tr64, Y_tr, C_te64, Y_te,
                                    floors, film, disclosure_block)
    floors_beat = fmnlib.attach_band_to_beat_table(floors_beat, g5_band)
    if disclosure_block.get("applicable"):
        print(f"[disclosure] {name}: {disclosure_block['protocol']} "
              f"{disclosure_block['n_legs']} legs | affine_on_hf_train on test "
              f"{disclosure_block['fold_range_on_test_split']['affine_on_hf_train']}",
              flush=True)

    clause_block = ladderlib.clauses(legs_out, film, tau, floors_beat,
                                     split_transfer, tol, g5_band=g5_band)
    reg = ladderlib.registration(name, name in SCORED_PANEL_ADR_R3_0007, floor,
                                 clause_block, floors_beat,
                                 plan["registered_unit_eligible"])
    fals = ladderlib.falsifier(legs_out, tau)

    # aggregate statistics over the leg population
    def _agg(field):
        vals = [lg["stats"].get(field) for lg in legs_out
                if isinstance(lg["stats"].get(field), float)
                and math.isfinite(lg["stats"][field])]
        if not vals:
            return {"n": 0, "min": None, "max": None, "mean": None}
        return {"n": len(vals), "min": float(min(vals)), "max": float(max(vals)),
                "mean": float(np.mean(vals))}

    stats_agg = {f: _agg(f) for f in ("phi_ceil", "phi_real", "rho", "E_est", "E_hall",
                                      "E_hall_fraction")}
    nrmse_agg = {rung: {"legs": [lg["nrmse"].get(rung) for lg in legs_out],
                        "mean": (float(np.mean([lg["nrmse"][rung] for lg in legs_out]))
                                 if all(isinstance(lg["nrmse"].get(rung), float)
                                        for lg in legs_out) else None)}
                 for rung in ladderlib.RUNGS}

    print(f"[ladder] {name}: phi_ceil {stats_agg['phi_ceil']} | rho "
          f"{stats_agg['rho']} | C2 {clause_block['C2_ceiling_existence']['verdict']} | "
          f"{reg['status']}", flush=True)

    # ── the diag ─────────────────────────────────────────────────────────
    t_eval = time.time()
    gates = {
        "V2_no_test_lf_path": {"test_lf_fids": list(test["lf_fids"]), "pass": True,
                               "knob": knobs["R3S2B3_NO_TEST_LF_ASSERT"],
                               "note": "asserted before any field array was read"},
        "V6b_paired_real_lf": dict(pairing, pass_=paired),
        "V8_ic_equivalence": ic_gates.get("equivalence",
                                          {"skipped": "ic_synth not applicable here"}),
        "V11_arm_equal_total_budget": {
            "R0_absent": budget["rung_optimizer_epochs"]["R0_absent"],
            "R1_predicted": budget["rung_optimizer_epochs"]["R1_predicted"],
            "pass": True},
        "V12_lsi_bandlimit": dict(kcut_rec, mode=knobs["S6_LSI_BANDLIMIT_MODE"],
                                  selected_per_leg=[lg["d2_selection"]["selected_bandlimit"]
                                                    for lg in legs_out]),
        "V13_selection_out_of_sample": {
            "tripwire": knobs["S6_LEAKAGE_TRIPWIRE"],
            "select_on": knobs["R3S2B3_CORRECTOR_SELECT_ON"],
            "comparand": knobs["R3S2B3_CORRECTOR_SELECT_COMPARAND"],
            "n_sel_folds_by_leg": [lg["d2_selection"]["n_sel_folds"] for lg in legs_out],
            "pass": True,
            "note": ("d2_select.select raises if any selection fold overlaps its own fit "
                     "rows, so the criterion cannot silently become in-sample")},
        "V14_ckpt_data_hash_bind": dict(resume_record, data_sha256=data_sha,
                                        knob=knobs["R3S2B3_CKPT_DATA_HASH_BIND"],
                                        pass_=True),
        "V17_rung_lift_tripwire": dict(rung_lift_gate,
                                       knob=knobs["R3S2B3_RUNG_LIFT_TRIPWIRE"]),
        "V18_ckpt_binding": {
            "knob": knobs["R3S2B3_CKPT_BINDING"],
            "attached": bool(binding_block), "error": binding_error,
            "roles_read": list(bindlib.ROLES_READ_BY_ARM["lf_at_train"]),
            "roles_by_rung": roles_by_rung,
            "tool_version": binding_block.get("tool_version") if binding_block else None,
            "note": ("batch-3 scope rule 2: `data_binding` is written into last.pt at "
                     "EVERY save. The arm is the UNION role over the five rungs — the "
                     "job reads train LF, so a train_lf change must read RETRAIN.")},
        "V19_oracle_nondeployable": {
            "knob": knobs["R3S2B3_ORACLE_NONDEPLOYABLE"],
            "rungs_on_test_split": list(ladderlib.DEPLOYABLE),
            "rungs_heldout_train_only": list(ladderlib.NONDEPLOYABLE),
            "pass": True,
            "note": ("R2_oracle and R2b_copylf read REAL LF and are therefore evaluated "
                     "on held-out TRAIN rows only. They never enter a test-split path "
                     "and never enter a panel geomean (immutable #9).")},
        "V20_target_scaler_preflight": {
            f"train_rows_group_{i}": dict(
                neural_cache[k]["target_scale"],
                scaler=tslib.scaler_summary(neural_cache[k]["target_scale"]))
            for i, k in enumerate(neural_cache)},
    }

    sidecars = {
        "S1_emulator_field_error": {
            "by_train_rows_group": [
                {"group": i, "n_train_rows": len(k),
                 "nrmse_lfhat_vs_lf_native_heldout": neural_cache[k]["emu_heldout_nrmse"]}
                for i, k in enumerate(neural_cache)],
            "note": "stage-1 error on the emulator's own held-out LF slice"},
        "S2_ceiling_ladder": {
            "rungs": {r: ladderlib.RUNG_ROLE[r] for r in ladderlib.RUNGS},
            "nrmse_by_rung": nrmse_agg,
            "statistics": stats_agg,
            "note": ("B2's S2 sidecar promoted to the card's PRIMARY measurement, with "
                     "the two rungs it lacked: a matched-budget no-LF denominator (R0) "
                     "and a corrector-free degraded rung (R1b).")},
        "S6_target_scale_preflight": {
            "knob": knobs["R3S2_TARGET_SCALER_PREFLIGHT"],
            "live_on_this_cell": name in tslib.PREFLIGHT_DATASETS,
            "note": ("B2 declared this not_applicable because pfc was not in its dataset "
                     "list. B3 SCORES pfc (ADR r3-0005), so the round-2 ADR 0004 §2 rule "
                     "is live and implemented in target_scale.py with that ADR's own "
                     "audit thresholds.")},
    }

    diag = dict(pad)
    diag.update({
        "model": MODEL_NAME, "dataset": name, "seed": int(args.seed),
        "epochs": int(args.epochs), "nrmse_def_hash": NRMSE_DEF_HASH,
        "knobs": knobs, "budget": budget,
        "hot_split_plan": hotlib.jsonable(plan),
        "legs": legs_out if _truthy(knobs["R3S2B3_LEG_POPULATION_DUMP"]) else [],
        "leg_population_dumped": _truthy(knobs["R3S2B3_LEG_POPULATION_DUMP"]),
        "nrmse_by_rung": nrmse_agg, "statistics": stats_agg,
        "film_denominator": film, "noise_floor": floor, "thresholds": tau,
        "clauses": clause_block, "registration": reg, "falsifier": fals,
        "split_transfer_licence": split_transfer,
        "floor_arms": floors, "floor_comparison_by_rung": floors_beat,
        "floor_matched_disclosure_legs": disclosure_block,
        "floor_matched_n_g5_band": g5_band,
        "mean_test_nrmse_by_deployable_rung": mean_test,
        "anchor_replication_check": {
            "target_stream_anchor_panel_geomean_skill":
                knobs["R3S2B3_ANCHOR_REPLICATION_CHECK"],
            "tolerance_panel_seed_mce": 0.5083,
            "R1_test_nrmse_this_cell": mean_test.get("R1_predicted"),
            "note": ("10.0853 is a PANEL GEOMEAN IN SKILL UNITS; this cell publishes the "
                     "raw R1 test nRMSE the analyzer aggregates. The 320/400 fit-set "
                     "reduction is disclosed in hot_split_plan.")},
        "pairing": pairing, "lift_convention": up_fn_name, "eval_layer": EVAL_LAYER,
        "lf_rung": int(lf_rung), "lf_grid": list(lf_grid), "hf_grid": list(hf_grid),
        "res_min_grid": list(res_min_grid), "dataset_content_sha256": data_sha,
        "ic_synthesis": ic_record, "probes": probes,
        "sidecars": sidecars, "validity_gates": gates,
        "bands": {"edges_wavenumber": [float(e) for e in band_edges],
                  "k_nyquist": float(min(H, W) / 2.0), "n_bands": bandlib.N_BANDS,
                  "stats_knob": knobs["R3S2B3_BAND_STATS"],
                  "note": ("band columns are ENERGY-weighted per rung (batch-3 clause "
                           "rule 4); no unweighted mode mean is published anywhere")},
        "n_params": {k: v for k, v in
                     next(iter(neural_cache.values()))["n_params"].items()},
        "device": str(device),
        "vendor_source": (
            "round3/worktrees/r3s2_field_reach/B2/models_r3/r3s2_route @ "
            "e606a4f14f8e870fccee097ed18b6050344a4ace (model.py, front_end.py, "
            "ic_synth.py, lsi_filter.py, local_corrector.py, direct_head.py, bands.py, "
            "periodicity.py, upsample.py, floor_arms.py, selector.py, probes.py, "
            "sidecars.py — per-file sha256 in _vendor_manifest.json). The recipe's "
            "`base_commit` 23018cc5 is a TRUNK commit carrying NO models_r3/ tree; "
            "`env._substrate_commit` e606a4f1 is the branch tip that carries the family "
            "and governs (see notes/handoff_experiment_builder.md). NO code vendored "
            "from any round-1 family beyond what r3s2_route already carried. "
            "IC-synthesis math remains B1's re-implementation from the READ-ONLY "
            "generator surfaces (never imported, never edited)."),
        "declared_reuse": (
            "role (a), round-2 program 5.10a: the DC-lineage corrector remains a declared "
            "FROZEN test-time sub-component. NEW in B3: the SAME frozen corrector is "
            "additionally evaluated on REAL train-side LF (R2_oracle) as an explicitly "
            "NON-DEPLOYABLE reference arm, in the same role class as the copy-LF "
            "reference; it never touches test LF and never enters a panel geomean."),
        "novelty_declaration": (
            "The contribution is a REGIME and a DECISION RULE, not an architecture and "
            "not the oracle/predicted decomposition (preempted: arXiv:2602.13416, "
            "arXiv:2604.12440, arXiv:1712.05884 §3.3.1). New: a ceiling ladder whose "
            "oracle intermediate is structurally UNAVAILABLE at inference, measured on "
            "held-out TRAIN rows with an enumerated C(5,3) fold population at N_hf = 5, "
            "denominated by a matched-budget no-LF direct arm, priced against certified "
            "training-free floors at matched fit-set size and the certified film "
            "denominator, and converted into a prospective drop/keep rule for the LF "
            "intermediate (D3, an established absence in the retrieved corpus)."),
        "adr_r3_0007": ("option C (operator, 2026-08-10): scored panel = 4 sharp cells + "
                        "ifc_heat; ifc_poisson report-only. All six cells RUN; only the "
                        "REGISTERED-vs-REPORT-ONLY resolution changes."),
    })

    dp = diag_base(knobs)
    dp.mkdir(parents=True, exist_ok=True)
    (dp / f"diag_{name}_e{args.epochs}_s{args.seed}.json").write_text(
        json.dumps(_json_safe(diag), indent=2, sort_keys=True))

    persist("done")
    eval_seconds = time.time() - t_eval

    n_params = int(sum(next(iter(neural_cache.values()))["n_params"].values()))
    latency = (1000.0 * eval_seconds / max(Nte, 1)) if device.type == "cuda" else None
    peak_mem = (torch.cuda.max_memory_allocated() / 1e6) if device.type == "cuda" else None
    print(f"[result] {name} scored_rung=R1_predicted "
          f"nRMSE={round_nrmse(primary_test_pred, Y_te):.6f} | "
          f"wall={time.time()-t0:.1f}s", flush=True)

    return finalize_and_write(
        out_path=out_path, model=MODEL_NAME, dataset=name,
        pred=primary_test_pred, target=Y_te, work_grid=grid, n_params=n_params,
        train_seconds=train_seconds_acc, eval_seconds=eval_seconds,
        latency_ms_per_sample=latency, peak_mem_mb=peak_mem, seed=args.seed,
        extra=_json_safe({
            "scored_rung": "R1_predicted",
            "scored_rung_note": ("the panel number is the DEPLOYED route on the stripped "
                                 "test split, primary leg. The ceiling rungs are held-out-"
                                 "train quantities and never enter it (immutable #9)."),
            "nrmse_by_rung": nrmse_agg,
            "mean_test_nrmse_by_deployable_rung": mean_test,
            "statistics": stats_agg,
            "clauses": clause_block, "registration": reg, "falsifier": fals,
            "split_transfer_licence": split_transfer,
            "thresholds": tau, "film_denominator": film, "noise_floor": floor,
            "hot_split_plan": hotlib.jsonable(plan),
            "legs": legs_out,
            "floor_arms": floors, "floor_comparison_by_rung": floors_beat,
            "floor_matched_disclosure_legs": disclosure_block,
            "floor_matched_n_g5_band": g5_band,
            "validity_gates": gates, "probes": probes,
            "budget": budget, "pairing": pairing,
            "lf_rung": int(lf_rung), "lf_grid": list(lf_grid),
            "hf_grid": list(hf_grid), "work_grid": list(grid),
            "lift_convention": up_fn_name, "padding_mode": padding_mode,
            "dataset_content_sha256": data_sha,
            "ic_synthesis": ic_record,
            "mf_mechanism": ("a FIVE-RUNG emulator-ceiling ladder on one shared FiLM-FNO "
                             "trunk: a matched-budget no-LF direct arm (R0) denominates a "
                             "pseudo-LF route (R1) and its real-LF oracle (R2) through the "
                             "SAME frozen corrector, all on held-out TRAIN rows, with the "
                             "LSI regularisation selected on the emulator's own held-out "
                             "output"),
            "base_family": "r3s2_route@e606a4f1 (itself r3s2_stack_ic@d5069a74)",
            "r3s2_env": knobs, "r3s2_diag": diag,
            "nrmse_def_hash": NRMSE_DEF_HASH,
            "panel_data_note": ("the lift is VENDORED into upsample.py; panel_data.py is "
                                "imported READ-ONLY by rung_lift.py for the tripwire only "
                                "(its bytes are already in score_panel.py's code_hash) "
                                "and is never written to and never edited"),
            "nrmse_module_sha256": _sha256(EVAL_DIR / "nrmse.py"),
        }))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset_dir", required=True)
    ap.add_argument("--dataset_name", required=True)
    ap.add_argument("--epochs", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--ckpt_dir", required=True)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    run(args, out)
    print(f"[wrote] {out}", flush=True)


if __name__ == "__main__":
    main()
