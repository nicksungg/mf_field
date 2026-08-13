#!/usr/bin/env python
"""`r3s2_route` — the ROUTE CONTRAST of card `r3s2_field_reach-B2`.

Contract: the unchanged six-arg factory CLI (`--dataset_dir --dataset_name
--epochs --out --ckpt_dir --seed`), resume from `<ckpt_dir>/last.pt`, result JSON
via `data_adapters.metrics.finalize_and_write`.

THE QUESTION
------------
Is the LF intermediate worth its place in the graph when it must itself be
HALLUCINATED from the condition? One shared FiLM-FNO trunk (width 64, 4 blocks,
12 modes) sits behind a ROUTE SWITCH, crossed with a FRONT-END SWITCH:

    stack  : cond --[front end]--> pseudo-LF on the LF rung's NATIVE grid
                  --[corrected upsample, ADR r2-0001]--> LF-hat_up
                  --[frozen REGULARISED LSI T(k), gain alpha_lsi]--> + C_LSI
                  --[LocalCorrector + PixelGate, gain alpha_nn]---> + NN  = HF
    direct : cond --[front end]--> HF                              (direct_head.py)

    front end  `ic_synth`   the exact analytic IC field as an extra input channel
                            (zero parameters), FiLM on the non-`ic_*` dims
               `film_only`  FiLM on the whole condition vector

A BUDGET ACCOUNTANT holds every stage-2 arm and every direct arm at exactly
`E_emu + 2*E_dc` optimizer epochs (300 at tier 200, `R3S2_BUDGET_MATCH=
arm_equal_total`), so the route contrast is not a budget contrast (round-2
caveat F8). Gate V11 asserts the equality at runtime.

SEVEN ARMS (recipe `_arms`, verbatim) — all computed in ONE job on identical
folds, so every contrast is an in-job paired control:

  A1 stack_ic_reg      SCORED PRIMARY. G1 left-hand side, G2 subject.
  A2 stack_film_reg    second, independent replication of the route contrast at
                       the null front end.
  A3 direct_ic         SCORED PRIMARY comparand. G1 right-hand side.
  A4 direct_film       r2s1 CALIBRATION arm (pre-registered near 23.7753).
  A5 stack_ic_unreg    B1 replay at ridge=0, bandlimit=none — repair attribution
                       AND the anchor replication gate (G2 leg iv).
  A6 ifc_loo_selector  closed form, ifc cells only, ZERO GPU (selector.py).
  A7 emul_only_ic      stage-1 reference (the front end alone), E_emu epochs.
  + the mandatory floor arms nn_condition, train_mean, zero, affine_on_hf_train.

THE INSTRUMENT REPAIR IS A GATE, NOT THE CLAIM
----------------------------------------------
The LOOCV ridge + LF-Nyquist band-limit on `T(k)` (`lsi_filter.py`'s APPEND-ONLY
block) is carried as falsification clause **G2, instrument acceptance**. The
prior-art verdict E1 is quoted on the card: the repair is `preempted (cite)`,
"usable ONLY as an instrument repair, never as a contribution", and "Presenting
ridge/band-limiting as the *idea* is a rebadge". This file claims nothing for
it; `A5` is kept as the unrepaired replay so the repair is ATTRIBUTABLE.

DECLARED REUSE, role (a) (round-2 program 5.10a): the DC-lineage corrector
remains a declared FROZEN test-time sub-component behind a condition->pseudo-LF
front end. NO code is vendored from `r2s1_direct`; the direct arms are declared
MATCHED CONTROLS inside the route contrast (recipe `_novelty_declaration`),
carry the analytic IC channel that r2s1's FiLM-only heads do not have, and are
budget-locked to the stack.

NO TEST LF IS EVER READ: the stripped view's test split physically contains only
the HF fidelity, and gate V2 asserts it before any field array is touched.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

HERE = Path(__file__).resolve().parent
# <worktree>/models_r3/<family>/ -> <worktree>/mf_field/factory_mffp
FACTORY_ROOT = HERE.parents[1] / "mf_field" / "factory_mffp"
# <worktree>/models_r3/<family>/ -> <worktree>/mffp_autoresearch/round2/eval (READ-ONLY)
EVAL_DIR = HERE.parents[1] / "mffp_autoresearch" / "round2" / "eval"
sys.path.insert(0, str(HERE))
for _p in (FACTORY_ROOT, EVAL_DIR):
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
import sidecars as sidelib                                               # noqa: E402
import direct_head as directlib                                          # noqa: E402
import selector as sellib                                                # noqa: E402
from data_adapters import load_mf_dataset                                # noqa: E402
from data_adapters.geometry import resolve_grid                          # noqa: E402
from data_adapters.metrics import finalize_and_write                     # noqa: E402
# Read-only import of the round's ONE nRMSE definition, so every diagnostic
# number in this file is on the same footing as the scored metric.
from nrmse import NRMSE_DEF_HASH, nrmse as round_nrmse                   # noqa: E402

MODEL_NAME = "r3s2_route"
WORK_CAP = 256                        # base family's working-grid cap (unchanged)

# Optimisation hyperparameters VERBATIM from the base family (`r3s2_stack_ic` @
# d5069a74, itself `r2s2_stack` @ 6b4e1d48, itself `s4_router` @ b90d4662, itself
# `mf_fno_transfer_film` @ 967562e). No value here is invented by the builder.
SMOKE = dict(hidden_channels=64, n_blocks=4, modes_cap=12, batch_size=16,
             lr_pretrain=1e-3, lr_finetune=3e-4, weight_decay=1e-5, grad_clip=1.0)
LR_EMULATOR = SMOKE["lr_pretrain"]
LR_CORRECTOR = SMOKE["lr_finetune"]
LR_GATE = SMOKE["lr_finetune"]
# The direct head is the SAME trunk trained from scratch on a field target, so it
# takes the same pre-training lr the emulator takes. No new constant.
LR_DIRECT = SMOKE["lr_pretrain"]
CKPT_SAVES_PER_STAGE = 5
PAIRED_COND_TOL = 1e-6
MAP_SMOOTHNESS_ROW_CAP = 128      # the E3 instrument is O(N^2 d + N HW); cap recorded
DIRECT_VAL_THRESHOLD = 20         # recipe R3S2B2_DIRECT_VAL: "..._if_n_train_hf_ge_20_..."

FRONT_ENDS = ("film_only", "ic_synth")
FRONT_TAG = {"film_only": "E0", "ic_synth": "E1"}

# card recipe `_arms`, VERBATIM (tag -> the knobs the arm implies)
ARM_SPEC = {
    "A1_stack_ic_reg": {
        "R3S2B2_ROUTE": "stack", "R3S2_FRONTEND": "ic_synth", "R3S2_ARM": "frozen",
        "S6_LSI_RIDGE": "loocv", "S6_LSI_BANDLIMIT": "lf_nyquist_from_ladder",
        "R3S2_LF_INPUT": "pseudo", "R3S2_CORRECTOR_FIT_ON": "real_lf"},
    "A2_stack_film_reg": {
        "R3S2B2_ROUTE": "stack", "R3S2_FRONTEND": "film_only", "R3S2_ARM": "frozen",
        "S6_LSI_RIDGE": "loocv", "S6_LSI_BANDLIMIT": "lf_nyquist_from_ladder",
        "R3S2_LF_INPUT": "pseudo", "R3S2_CORRECTOR_FIT_ON": "real_lf"},
    "A3_direct_ic": {
        "R3S2B2_ROUTE": "direct", "R3S2_FRONTEND": "ic_synth", "R3S2_ARM": "direct",
        "R3S2_LF_INPUT": "none", "R3S2_CORRECTOR_FIT_ON": "none"},
    "A4_direct_film": {
        "R3S2B2_ROUTE": "direct", "R3S2_FRONTEND": "film_only", "R3S2_ARM": "direct",
        "R3S2_LF_INPUT": "none", "R3S2_CORRECTOR_FIT_ON": "none"},
    "A5_stack_ic_unreg": {
        "R3S2B2_ROUTE": "stack", "R3S2_FRONTEND": "ic_synth", "R3S2_ARM": "frozen",
        "S6_LSI_RIDGE": "0", "S6_LSI_BANDLIMIT": "none",
        "R3S2_LF_INPUT": "pseudo", "R3S2_CORRECTOR_FIT_ON": "real_lf"},
    "A6_ifc_loo_selector": {
        "R3S2B2_ROUTE": "selector", "R3S2_FRONTEND": "none", "R3S2_ARM": "selector",
        "R3S2_LF_INPUT": "none", "R3S2_CORRECTOR_FIT_ON": "none"},
    "A7_emul_only_ic": {
        "R3S2B2_ROUTE": "stack", "R3S2_FRONTEND": "ic_synth", "R3S2_ARM": "emul_only",
        "R3S2_LF_INPUT": "pseudo", "R3S2_CORRECTOR_FIT_ON": "none"},
}
ARMS = tuple(ARM_SPEC)
FIELD_ARMS = ("A1_stack_ic_reg", "A2_stack_film_reg", "A3_direct_ic",
              "A4_direct_film", "A5_stack_ic_unreg", "A7_emul_only_ic")
ARM_ROLE = {
    "A1_stack_ic_reg": ("SCORED PRIMARY - the repaired stack; G1 left-hand side, "
                        "G2 subject"),
    "A2_stack_film_reg": ("second, independent replication of the route contrast at "
                          "the null front end"),
    "A3_direct_ic": ("SCORED PRIMARY comparand - matched-budget direct condition->HF "
                     "control; G1 right-hand side"),
    "A4_direct_film": ("r2s1 CALIBRATION arm - pre-registered to land near "
                       "r2s1_direct-B2's certified 23.7753"),
    "A5_stack_ic_unreg": ("B1 replay - repair attribution AND the anchor replication "
                          "gate (G2 leg iv, target 12.9556 +- 0.5083)"),
    "A6_ifc_loo_selector": ("closed-form, zero-GPU leave-one-out selector over "
                            "{affine_on_hf_train, A1, A3} on the HF train rows; the ifc "
                            "HEADLINE (card part 7 item 4). Selection uses train rows "
                            "ONLY - never the test split"),
    "A7_emul_only_ic": ("stage-1 reference (the front end alone), so the route delta "
                        "can be decomposed into stage-1 and transport terms"),
}
# which LSI chain each stack arm consumes
ARM_CHAIN = {"A1_stack_ic_reg": "reg", "A2_stack_film_reg": "reg",
             "A5_stack_ic_unreg": "unreg"}
ARM_FRONT = {"A1_stack_ic_reg": "ic_synth", "A2_stack_film_reg": "film_only",
             "A3_direct_ic": "ic_synth", "A4_direct_film": "film_only",
             "A5_stack_ic_unreg": "ic_synth", "A7_emul_only_ic": "ic_synth"}


class R3S2ContractError(RuntimeError):
    """A component seam violated its contract (spec §5.3: assert, don't default)."""


# ── knobs ────────────────────────────────────────────────────────────────
# Every value below is the card recipe's `env` value, VERBATIM. `read_knobs`
# refuses an unknown key and records any deviation, so a silent default is
# impossible. Keys prefixed `_` in the recipe are card directives, not env.
KNOB_RECIPE_VALUES = {
    "R3S2B2_ARM": "A1_stack_ic_reg",
    "R3S2B2_ROUTE": "stack",
    "R3S2_FRONTEND": "ic_synth",
    "R3S2_ARM": "frozen",
    "R3S2B2_DIRECT_TARGET": "hf",
    "R3S2B2_DIRECT_TRUNK": "shared_film_fno_w64_b4_m12",
    "R3S2B2_DIRECT_BUDGET": "match_stage2_total",
    "R3S2B2_DIRECT_TRAIN_ROWS": "hf_train_all",
    "R3S2B2_DIRECT_VAL": "disjoint_if_n_train_hf_ge_20_else_none_recorded",
    "R3S2_IC_SYNTH": "analytic_modes",
    "R3S2_IC_SYNTH_NORM": "res_min_maxabs",
    "R3S2_IC_SYNTH_SCALE": "1.0",
    "R3S2_IC_NAMES_FROM": "meta_param_names_ic_prefix",
    "R3S2_IC_FALLBACK": "film_only_recorded",
    "R3S2_IC_EQUIV_CHECK": "1",
    "R3S2_IC_SHUFFLE_NULL": "0_established_in_B1",
    "R3S2_EMU_TARGET": "lf_native",
    "R3S2_EMU_RUNG": "max",
    "R3S2_EMU_WIDTH": "64",
    "R3S2_EMU_BLOCKS": "4",
    "R3S2_EMU_MODES": "12",
    "R3S2_EMU_LOSS": "rel_l2",
    "R3S2_EMU_SHARED": "1",
    "R3S2_EPOCH_SPLIT": "0.5",
    "R3S2_BUDGET_MATCH": "arm_equal_total",
    "R3S2_UPSAMPLE": "corrected_by_convention",
    "R3S2_LF_INPUT": "pseudo",
    "R3S2_CORRECTOR_FIT_ON": "real_lf",
    "R3S2_VAL_DISJOINT": "1",
    "R3S2_REQUIRE_PSEUDO_LF": "1",
    "R3S2_PAIRING_GATE": "1",
    "R3S2_PAIRED_SUBSET_GEOMEAN": "1",
    "R3S2_TARGET_SCALER_PREFLIGHT": "not_applicable_no_helmholtz_no_pfc_in_datasets",
    "R3S2_FLOOR_ARMS": "nn_condition,train_mean,zero,affine_on_hf_train",
    "R3S2_DIAG_OUT": "mffp_autoresearch_outputs/round3/r3s2_field_reach/B2/eval",
    "S6_VARIANT": "local_pixel_gate",
    "S6_SELECTOR": "heldout_scalar",
    "S6_PAD_MODE": "circular_if_periodic",
    "S6_PERIODIC_TEST": "wrap_continuity_ratio_hf_train",
    "S6_PERIODIC_TOL": "1.25",
    "S6_LF_SOURCE": "dataset_lf_fidelity",
    "S6_LF_FID": "max",
    "S6_KERNEL": "7",
    "S6_DEPTH": "4",
    "S6_WIDTH": "32",
    "S6_GATE_HOLDOUT_FRAC": "0.2",
    "S6_GATE_INIT": "zero",
    "S6_GATE_LINESEARCH_INCLUDES_ZERO": "1",
    "S6_BAND_EDGES_FRAC": "0,0.125,0.25,0.5,1.0",
    "S6_LEAKAGE_TRIPWIRE": "1",
    "S6_LSI_RIDGE": "loocv",
    "S6_LSI_RIDGE_GRID": "0,1e-6,1e-4,1e-3,1e-2,1e-1",
    "S6_LSI_RIDGE_SELECT": "loocv_on_fit_fold_only",
    "S6_LSI_BANDLIMIT": "lf_nyquist_from_ladder",
    "S6_LSI_BANDLIMIT_MODE": "zero_above_kcut",
    "S6_LSI_KCUT_SOURCE": "ladder_shape_ratio_adr_r2_0001",
    "R3S2B2_REPORT_UNITS": "skill,fractional_error_reduction",
    "R3S2B2_BAND_ERROR_COLUMNS": "1",
    "R3S2B2_MAP_SMOOTHNESS_SIDECAR": "1",
    "R3S2B2_ROUTE_DATA_DISCLOSURE": "1",
    "R3S2B2_T_STABILITY_AUDIT": "1",
    "R3S2B2_IFC_LOO_SELECTOR": "affine_on_hf_train,A1_stack_ic_reg,A3_direct_ic",
    "R3S2B2_CKPT_DATA_HASH_BIND": "1",
    "R3S2B2_ANCHOR_REPLICATION_CHECK": "12.9556",
    "R3S2_EMU_ERROR_SIDECAR": "1",
    "R3S2_ORACLE_TRAINHELDOUT_SIDECAR": "1",
    "R3S2_ZERO_GRADIENT_LADDER_SIDECAR": "1",
    "R3S2_BC_AUDIT_SIDECAR": "1",
}


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

    scored_tag = knobs["R3S2B2_ARM"]
    if scored_tag not in ARM_SPEC:
        raise R3S2ContractError(
            f"R3S2B2_ARM={scored_tag!r} is not one of the recipe's 7 arms {sorted(ARM_SPEC)}")
    if scored_tag == "A6_ifc_loo_selector":
        raise R3S2ContractError(
            "A6 is a per-cell SELECTOR over the other arms and is defined only where a "
            "certified `affine_on_hf_train` floor exists; it cannot be the panel-wide "
            "scored arm. It is reported per cell in `arms` / `ifc_loo_selector`.")
    knobs["_scored_arm_tag"] = scored_tag
    # The descriptor knobs are DERIVED from the arm (recipe `_arms`); if the caller
    # also set them they must AGREE, otherwise the run would be mislabelled.
    for key, want in ARM_SPEC[scored_tag].items():
        if key in os.environ and os.environ[key] != want:
            raise R3S2ContractError(
                f"{key}={os.environ[key]!r} contradicts arm {scored_tag!r} "
                f"(recipe `_arms` says {want!r})")
        knobs[key] = want

    if knobs["S6_VARIANT"] != "local_pixel_gate":
        raise R3S2ContractError(
            "the router and trust head are REMOVED in this lineage (round 1 measured "
            f"their panel contribution at exactly 0.000000); got {knobs['S6_VARIANT']!r}")
    if knobs["R3S2_EMU_TARGET"] != "lf_native":
        raise R3S2ContractError(
            "R3S2_EMU_TARGET must be 'lf_native' (round-2 Decision B: emulating LF_up "
            "on the HF grid makes the nested-ladder degeneracy total and the stream's "
            f"question unanswerable by construction); got {knobs['R3S2_EMU_TARGET']!r}")
    if knobs["R3S2_UPSAMPLE"] != "corrected_by_convention":
        raise R3S2ContractError(
            f"R3S2_UPSAMPLE must be 'corrected_by_convention', got {knobs['R3S2_UPSAMPLE']!r}")
    if knobs["R3S2_IC_SYNTH"] != "analytic_modes":
        raise R3S2ContractError(
            f"R3S2_IC_SYNTH must be 'analytic_modes' (the card's zero-parameter exact "
            f"reconstruction); got {knobs['R3S2_IC_SYNTH']!r}")
    if knobs["R3S2_IC_SYNTH_NORM"] != "res_min_maxabs":
        raise R3S2ContractError(
            "R3S2_IC_SYNTH_NORM must be 'res_min_maxabs' — the generator normalises the "
            "coarse field BEFORE zero-padding, so any other constant makes the "
            f"reconstruction inexact; got {knobs['R3S2_IC_SYNTH_NORM']!r}")
    if knobs["R3S2_IC_NAMES_FROM"] != "meta_param_names_ic_prefix":
        raise R3S2ContractError(
            "R3S2_IC_NAMES_FROM must be 'meta_param_names_ic_prefix' (the IC columns are "
            f"resolved from the dataset's own param_names, never positionally); got "
            f"{knobs['R3S2_IC_NAMES_FROM']!r}")
    if knobs["R3S2_IC_FALLBACK"] != "film_only_recorded":
        raise R3S2ContractError(
            f"R3S2_IC_FALLBACK must be 'film_only_recorded', got {knobs['R3S2_IC_FALLBACK']!r}")
    if knobs["R3S2_BUDGET_MATCH"] != "arm_equal_total":
        raise R3S2ContractError(
            f"R3S2_BUDGET_MATCH must be 'arm_equal_total' (reviewer caveat F8), got "
            f"{knobs['R3S2_BUDGET_MATCH']!r}")
    if knobs["R3S2B2_DIRECT_TARGET"] != "hf":
        raise R3S2ContractError(
            f"R3S2B2_DIRECT_TARGET must be 'hf' (the direct route predicts the HF field "
            f"from the condition alone); got {knobs['R3S2B2_DIRECT_TARGET']!r}")
    if knobs["R3S2B2_DIRECT_BUDGET"] != "match_stage2_total":
        raise R3S2ContractError(
            f"R3S2B2_DIRECT_BUDGET must be 'match_stage2_total' — an unmatched direct "
            f"budget turns the route contrast into a budget contrast; got "
            f"{knobs['R3S2B2_DIRECT_BUDGET']!r}")
    if knobs["R3S2B2_DIRECT_TRAIN_ROWS"] != "hf_train_all":
        raise R3S2ContractError(
            f"R3S2B2_DIRECT_TRAIN_ROWS must be 'hf_train_all', got "
            f"{knobs['R3S2B2_DIRECT_TRAIN_ROWS']!r}")
    if knobs["R3S2B2_DIRECT_TRUNK"] != "shared_film_fno_w64_b4_m12":
        raise R3S2ContractError(
            "R3S2B2_DIRECT_TRUNK must be 'shared_film_fno_w64_b4_m12' — the route "
            "contrast is only meaningful at a SHARED trunk; got "
            f"{knobs['R3S2B2_DIRECT_TRUNK']!r}")
    if knobs["S6_LSI_RIDGE"] != "loocv":
        raise R3S2ContractError(
            "S6_LSI_RIDGE must be 'loocv' for the SCORED arm (the unregularised replay "
            f"is arm A5, whose ridge=0 is internal); got {knobs['S6_LSI_RIDGE']!r}")
    if knobs["S6_LSI_BANDLIMIT"] != "lf_nyquist_from_ladder":
        raise R3S2ContractError(
            f"S6_LSI_BANDLIMIT must be 'lf_nyquist_from_ladder', got "
            f"{knobs['S6_LSI_BANDLIMIT']!r}")
    if knobs["S6_LSI_BANDLIMIT_MODE"] != "zero_above_kcut":
        raise R3S2ContractError(
            f"S6_LSI_BANDLIMIT_MODE must be 'zero_above_kcut', got "
            f"{knobs['S6_LSI_BANDLIMIT_MODE']!r}")
    if knobs["S6_LSI_RIDGE_SELECT"] != "loocv_on_fit_fold_only":
        raise R3S2ContractError(
            "S6_LSI_RIDGE_SELECT must be 'loocv_on_fit_fold_only' (S6_LEAKAGE_TRIPWIRE); "
            f"got {knobs['S6_LSI_RIDGE_SELECT']!r}")
    if str(knobs["R3S2_IC_SHUFFLE_NULL"]).strip() not in ("0_established_in_B1", "0"):
        raise R3S2ContractError(
            "R3S2_IC_SHUFFLE_NULL must be '0_established_in_B1' — the zero-information "
            "null for the IC channel was established on B1 and is NOT re-spent here; "
            f"got {knobs['R3S2_IC_SHUFFLE_NULL']!r}")
    if knobs["R3S2_TARGET_SCALER_PREFLIGHT"] != \
            "not_applicable_no_helmholtz_no_pfc_in_datasets":
        raise R3S2ContractError(
            "R3S2_TARGET_SCALER_PREFLIGHT is fixed by the recipe to "
            "'not_applicable_no_helmholtz_no_pfc_in_datasets'; got "
            f"{knobs['R3S2_TARGET_SCALER_PREFLIGHT']!r}")
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


# ── small helpers (vendored structure from r3s2_stack_ic) ────────────────


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
    """Deterministic sha256 over a torch state_dict (key order fixed)."""
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

    `R3S2B2_CKPT_DATA_HASH_BIND=1` (recipe): this hash is bound into `last.pt`, so
    a resume against CHANGED arrays ABORTS instead of zero-stepping. It exists
    because r3s4-B1's open question was exactly *"Only a content hash bound into
    the checkpoint can"* distinguish a legitimate resume from a stale-checkpoint
    replay (round-3 STOP-THE-LINE #2, r3s3-B1). Cost: one pass over the arrays.
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
    dataset-content-hash mismatch (`R3S2B2_CKPT_DATA_HASH_BIND=1`).

    The abort is the point: a silent "meta mismatch, start fresh" would burn the
    walltime and produce a number nobody could attribute, and a silent RESUME
    against changed arrays is the stale-checkpoint contamination that halted the
    round (STOP-THE-LINE #2). Neither is acceptable, so a checkpoint that was
    written against different data is a hard error.
    """
    if path is None or not path.exists():
        return None, {"found": False, "aborted": False}
    try:
        sd = torch.load(path, map_location="cpu", weights_only=False)
    except Exception as e:  # noqa: BLE001
        print(f"[resume] {path} unreadable ({e}); ignoring", flush=True)
        return None, {"found": True, "readable": False, "aborted": False}
    prev = sd.get("data_sha256")
    rec = {"found": True, "readable": True, "bind_enabled": bool(bind),
           "ckpt_data_sha256": prev, "current_data_sha256": data_sha}
    if bind and prev is not None and prev != data_sha:
        raise R3S2ContractError(
            f"CKPT DATA-HASH BIND: {path} was written against dataset content "
            f"{prev[:16]}... but the arrays on disk now hash to {data_sha[:16]}.... "
            "Refusing to resume or to silently restart: this is exactly the stale-"
            "checkpoint contamination of round-3 STOP-THE-LINE #2. Delete the ckpt dir "
            "deliberately if the data change was intended (recipe: ckpt dirs must be "
            "FRESH under .../B2/, never reused).")
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
    """Shuffle-and-step loop, structure identical to the base family's `_train`."""
    params = [p for p in params if p.requires_grad]
    if n == 0 or epochs <= 0 or not params:
        return
    opt = torch.optim.AdamW(params, lr=lr, weight_decay=SMOKE["weight_decay"])
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max(epochs, 1), eta_min=1e-6)
    g = torch.Generator().manual_seed(0)   # base family convention (seed-independent shuffle)
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


# ── path resolution ──────────────────────────────────────────────────────


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
    return HERE.parents[1]


def diag_base(knobs: dict) -> Path:
    raw = knobs["R3S2_DIAG_OUT"]
    p = Path(raw)
    if not p.is_absolute():
        p = _main_repo_root() / raw
    return p


def _read_param_names(ds_dir: Path):
    """The dataset's own `meta.json::param_names` (read-only), or None."""
    mp = Path(ds_dir) / "meta.json"
    if not mp.exists():
        return None, None
    try:
        meta = json.loads(mp.read_text())
    except Exception as e:  # noqa: BLE001
        raise R3S2ContractError(f"{mp} is unreadable ({e}); refusing to guess the IC columns")
    return meta.get("param_names"), str(mp)


def frac_reduction(a: float, b: float):
    """`(a - b) / a` — the fractional error reduction of `b` relative to `a`.

    `R3S2B2_REPORT_UNITS=skill,fractional_error_reduction`: B1's M5 measured that a
    59x per-dataset SKILL gap on this panel was 20.3x denominator and only 2.14x
    effect, so every route delta is published in BOTH units. Skill needs the
    cell's copy-LF reference, which lives outside this family; the fraction does
    not, so the fraction is computed HERE and the analyzer converts to skill.
    """
    a, b = float(a), float(b)
    if not np.isfinite(a) or a == 0.0:
        return None
    return (a - b) / a


# ── the run ──────────────────────────────────────────────────────────────


def run(args, out_path: Path) -> dict:
    t0 = time.time()
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    knobs = read_knobs()
    name = args.dataset_name
    scored_tag = knobs["_scored_arm_tag"]
    tripwire = _truthy(knobs["S6_LEAKAGE_TRIPWIRE"])

    ds_dir = Path(args.dataset_dir)
    train = load_mf_dataset(ds_dir, "train")
    test = load_mf_dataset(ds_dir, "test")

    # ── V2: the family never opens a non-HF test path ────────────────────
    if test["lf_fids"]:
        raise R3S2ContractError(
            f"V2 violated on {name}: the test split exposes LF fidelities "
            f"{test['lf_fids']}. Round 3 evaluates ONLY against the stripped view; "
            "this family must never see a test LF field.")
    hf = test["hf_fid"]
    if hf not in train["fids"]:
        raise R3S2ContractError(
            f"{name}: test HF fidelity {hf} absent from the train ladder {train['fids']}")
    if not train["lf_fids"]:
        raise R3S2ContractError(
            f"{name}: the TRAIN split has no LF fidelity; the emulator has no target")
    if knobs["S6_LF_FID"] != "max" or knobs["R3S2_EMU_RUNG"] != "max":
        raise R3S2ContractError("S6_LF_FID and R3S2_EMU_RUNG must both be 'max' (recipe)")
    lf_rung = max(train["lf_fids"])

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

    if tripwire:
        coarser = (h * w) < (H * W) and h <= H and w <= W
        if not coarser:
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

    # ── the dataset CONTENT hash (R3S2B2_CKPT_DATA_HASH_BIND) ────────────
    data_sha = dataset_content_sha256({
        "Y_tr": Y_tr, "X_tr": X_tr, "Y_te": Y_te, "X_te": X_te,
        "LF_nat_all": LF_nat_all, "X_lf_all": X_lf_all,
        "fids": tuple(int(f) for f in train["fids"]), "hf_fid": int(hf),
        "lf_rung": int(lf_rung), "grid": (H, W), "lf_grid": (h, w),
    })
    print(f"[data-hash] {name} content sha256 = {data_sha}", flush=True)

    # ── V6b + the ROUND-3 PAIRING GATE ───────────────────────────────────
    n_pair = min(N_lf, Ntr)
    pair_dev = (float(np.abs(X_lf_all[:n_pair].astype(np.float64)
                             - X_tr[:n_pair].astype(np.float64)).max())
                if n_pair else float("inf"))
    paired = bool(np.isfinite(pair_dev) and pair_dev <= PAIRED_COND_TOL and N_lf >= Ntr)
    pairing = {
        "paired_real_lf": paired,
        "max_abs_cond_deviation_lf_vs_hf": pair_dev,
        "tol": PAIRED_COND_TOL,
        "n_lf_samples": int(N_lf), "n_hf_train_samples": int(Ntr),
        "gate_armed": _truthy(knobs["R3S2_PAIRING_GATE"]),
        "note": ("index-aligned ladder: HF - LF_up is a well-defined per-sample residual"
                 if paired else
                 "UNPAIRED ladder: the LF rung's condition vectors are not the HF rung's, "
                 "so HF - LF_up is undefined and this cell's attribution is VOID"),
    }
    if _truthy(knobs["R3S2_PAIRING_GATE"]) and not paired:
        raise R3S2ContractError(
            f"R3S2_PAIRING_GATE: {name} has an UNPAIRED LF ladder (max|dX| = {pair_dev!r} "
            f"> {PAIRED_COND_TOL}, N_lf={N_lf}, Ntr={Ntr}). The stack arms are undefined "
            "here and the card's route attribution for this cell is void; the round-2 "
            "pseudo-LF re-route is deliberately NOT taken (card part 3, pairing gate).")
    print(f"[pairing] {name}: paired={paired} max|dX|={pair_dev:.3e} "
          f"(N_lf={N_lf}, Ntr={Ntr})", flush=True)

    # ── the CORRECTED real-LF base ───────────────────────────────────────
    up_fn_name = ("legacy_cell_centred_1d" if (h == 1 and H == 1)
                  else uplib.resolve_convention(name)[1])
    LFr_tr = uplib.upsample_fields(LF_nat_all[:Ntr], lf_grid, grid, name)

    # ── IC-SYNTHESIS RESOLUTION (front end `ic_synth`, BOTH routes) ──────
    param_names, meta_path = _read_param_names(ds_dir)
    ic_layout = icsynth.resolve_ic_indices(param_names, cond_dim)
    ic_scale = knob_float(knobs, "R3S2_IC_SYNTH_SCALE")
    square_lf = (h == w) and (int(res_min_grid[0]) == int(res_min_grid[1])) and h > 1
    square_hf = (H == W) and (int(res_min_grid[0]) == int(res_min_grid[1])) and H > 1
    # ONE applicability decision for both routes: the contrast is only meaningful
    # if BOTH routes can carry the channel. Where either cannot, both fall back.
    ic_applicable = bool(ic_layout["applicable"] and square_lf and square_hf)
    ic_record = dict(ic_layout)
    ic_record.update({
        "ic_synth_applicable": ic_applicable,
        "meta_json": meta_path,
        "res_min": int(res_min_grid[0]), "res_min_grid": list(res_min_grid),
        "stack_synth_res": int(h), "stack_grid": list(lf_grid),
        "direct_synth_res": int(H), "direct_grid": list(grid),
        "square_lf": bool(square_lf), "square_hf": bool(square_hf),
        "scale": ic_scale,
        "both_routes_note": ("the SAME analytic coefficients are synthesised at the LF "
                             "rung's native resolution for the stack and at the HF "
                             "working resolution for the direct head; the synthesis is "
                             "closed-form in the mode index, so neither is an "
                             "interpolation of the other"),
        "scale_note": ("the generator's per-dataset IC amplitude and its additive mean "
                       "offset are NOT reproduced: scale is fixed at R3S2_IC_SYNTH_SCALE "
                       "and the offset is dropped. Both are a known global constant / "
                       "affine shift on an INPUT channel and the offset is separately in "
                       "the condition vector; recorded, never silently absorbed."),
    })
    if not ic_applicable and ic_layout["applicable"] and not (square_lf and square_hf):
        ic_record["reason"] = (f"IC columns exist but a rung grid is not square 2-D "
                               f"(lf {lf_grid} / hf {grid} / res_min {res_min_grid}); "
                               "analytic 2-D synthesis does not apply")
    if not ic_applicable:
        print(f"[ic] {name}: ic_synth NOT applicable ({ic_record.get('reason')}) — "
              f"the ic_synth arms fall back to film_only, recorded", flush=True)
    else:
        print(f"[ic] {name}: {ic_layout['n_ic_coeffs']} ic_c* coeffs, mode square "
              f"m={ic_layout['mode_square_m']}, synth at {h}x{w} (stack) and {H}x{W} "
              f"(direct), norm on {res_min_grid[0]}x{res_min_grid[1]}", flush=True)

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

    def ic_tensor(route: str, front: str, split: str):
        """(N, 1, res, res) float32 IC channel, or None."""
        if front == "film_only" or not ic_applicable:
            return None
        arr = ic_channels[(route, split)]
        return torch.from_numpy(arr.astype(np.float32)).unsqueeze(1)

    # ── splits: disjoint, identically-sized val sub-slices ────────────────
    holdout_frac = knob_float(knobs, "S6_GATE_HOLDOUT_FRAC")
    disjoint = _truthy(knobs["R3S2_VAL_DISJOINT"])
    gsplit = torch.Generator().manual_seed(args.seed)
    perm = torch.randperm(Ntr, generator=gsplit).numpy()
    n_val = min(int(max(1, round(holdout_frac * Ntr))), max(Ntr - 1, 0))
    val_forced_even = False
    if disjoint:
        if Ntr < 3:
            raise R3S2ContractError(
                f"{name}: R3S2_VAL_DISJOINT=1 needs Ntr >= 3 to cut two non-empty "
                f"val sub-slices and a non-empty fit slice; Ntr={Ntr}")
        target = max(2, n_val - (n_val % 2))
        target = min(target, (Ntr - 1) - ((Ntr - 1) % 2))
        val_forced_even = (target != n_val)
        n_val = target
    val_idx, fit_idx = perm[:n_val], perm[n_val:]
    val_a, val_b = val_idx[:n_val // 2], val_idx[n_val // 2:]
    if not len(fit_idx) or not len(val_a) or not len(val_b):
        raise R3S2ContractError(
            f"{name}: degenerate split (fit={len(fit_idx)}, val_a={len(val_a)}, "
            f"val_b={len(val_b)}) — refusing to default")
    split_rec = {
        "n_fit": int(len(fit_idx)), "n_val": int(n_val),
        "n_val_a": int(len(val_a)), "n_val_b": int(len(val_b)),
        "holdout_frac": holdout_frac, "disjoint": disjoint,
        "val_a_role": "the LSI gain alpha_lsi (line search including 0)",
        "val_b_role": "the NN gain alpha_nn (line search including 0)",
        "forced_even": val_forced_even,
        "shared_by": ("ALL seven arms and both routes consume the identical folds; the "
                      "direct head's rows are resolved from these by direct_head."
                      "train_rows"),
    }

    # ── periodicity switch (numpy only; consumes no torch RNG) ────────────
    pad = periodlib.decide_padding(knobs["S6_PAD_MODE"], Y_tr, grid,
                                   knob_float(knobs, "S6_PERIODIC_TOL"))
    padding_mode = pad["padding_decision"]
    band_edges = bandlib.check_edges_env(grid, knobs["S6_BAND_EDGES_FRAC"])
    band_masks_np, _, _ = bandlib.band_masks(grid, bandlib.N_BANDS)

    print(f"[data] {name} loader={train['loader']} LF rung={lf_rung} HF={hf} "
          f"lf_grid={lf_grid} hf_grid={hf_grid} Ntr={Ntr} Nte={Nte} N_lf={N_lf} "
          f"cond_dim={cond_dim} upsample={up_fn_name} pad={padding_mode} "
          f"scored_arm={scored_tag}", flush=True)

    # ── epoch budget (R3S2_EPOCH_SPLIT + R3S2_BUDGET_MATCH) ──────────────
    split_frac = knob_float(knobs, "R3S2_EPOCH_SPLIT")
    if not (0.0 < split_frac < 1.0):
        raise R3S2ContractError(f"R3S2_EPOCH_SPLIT={split_frac!r} must be in (0, 1)")
    E_emu = max(1, int(round(int(args.epochs) * split_frac)))
    E_dc = max(1, int(args.epochs) - E_emu)
    E_corr = max(1, E_dc // 2)
    E_gate = max(1, E_dc - E_dc // 2)
    E_stage2 = E_emu + 2 * E_dc            # the recipe's 300 at tier 200
    E_direct = E_stage2                    # R3S2B2_DIRECT_BUDGET=match_stage2_total
    arm_epochs = {
        "A1_stack_ic_reg": E_stage2, "A2_stack_film_reg": E_stage2,
        "A3_direct_ic": E_direct, "A4_direct_film": E_direct,
        "A5_stack_ic_unreg": E_stage2, "A6_ifc_loo_selector": 0,
        "A7_emul_only_ic": E_emu,
    }
    budget = {"epochs_tier": int(args.epochs), "split": split_frac,
              "emulator": E_emu, "dc_stage_total": E_dc,
              "corrector": E_corr, "gate": E_gate,
              "stage2_total": E_stage2, "direct_total": E_direct,
              "budget_match": knobs["R3S2_BUDGET_MATCH"],
              "direct_budget_knob": knobs["R3S2B2_DIRECT_BUDGET"],
              "arm_optimizer_epochs": arm_epochs,
              "recipe_declared_stage2_epochs_at_tier_200": 300,
              "note": ("R3S2_BUDGET_MATCH=arm_equal_total (round-2 caveat F8). Each "
                       "stack arm spends E_emu (its front end) + E_dc (the common "
                       "real-LF ancestor) + E_dc (the frozen extension) = E_emu + 2*E_dc; "
                       "each DIRECT arm spends the SAME total in one stage on the HF "
                       "grid. So the route contrast is not a budget contrast. A6 is "
                       "closed form (0 epochs) and A7 is the front end alone (E_emu).")}
    print(f"[budget] emulator={E_emu} dc={E_dc} (corrector={E_corr} gate={E_gate}) "
          f"stage2/direct arms spend {E_stage2} each", flush=True)

    # ── checkpointing ────────────────────────────────────────────────────
    ckpt_dir = Path(args.ckpt_dir); ckpt_dir.mkdir(parents=True, exist_ok=True)
    ck_last = ckpt_dir / "last.pt"          # the contract-mandated path
    bind = _truthy(knobs["R3S2B2_CKPT_DATA_HASH_BIND"])
    meta = {"dataset": name, "seed": int(args.seed), "epochs_target": int(args.epochs),
            "grid": list(grid), "lf_grid": list(lf_grid), "lf_rung": int(lf_rung),
            "scored_arm": scored_tag, "padding_mode": padding_mode,
            "paired_real_lf": paired, "ic_applicable": ic_applicable,
            "data_sha256": data_sha, "family": MODEL_NAME}
    STAGE_ORDER = ["init"]
    for fe in FRONT_ENDS:
        STAGE_ORDER += [f"emu_{FRONT_TAG[fe]}", f"emu_{FRONT_TAG[fe]}_done"]
    for chain in ("reg", "unreg"):
        STAGE_ORDER += [f"dc_{chain}_real", f"dc_{chain}_real_done",
                        f"dc_{chain}_ext", f"dc_{chain}_ext_done"]
    for fe in FRONT_ENDS:
        STAGE_ORDER += [f"direct_{FRONT_TAG[fe]}", f"direct_{FRONT_TAG[fe]}_done"]
    STAGE_ORDER += ["done"]
    STAGES = {s: i for i, s in enumerate(STAGE_ORDER)}
    ck, resume_record = load_ckpt_checked(ck_last, meta, data_sha, bind)
    ck_stage = (ck or {}).get("stage", "init")
    ck_rank = STAGES.get(ck_stage, 0)
    acc: dict = {}

    def persist(stage: str, **extra) -> None:
        acc.update(extra)
        _save_ckpt(ck_last, dict(meta, **acc, stage=stage))

    # ══ the LSI TRANSFER FUNCTIONS — both chains, fit on REAL LF ══════════
    # Training-free closed forms on the fit fold, so they are built BEFORE any
    # gradient step and held FIXED for the whole run (both `dc_real` and its
    # frozen extension consume the same T, which is what `frozen` means).
    R_real = Y_tr - LFr_tr
    kcut_rec = lsilib.kcut_from_ladder(lf_grid, grid)
    ridge_grid = lsilib.parse_ridge_grid(knobs["S6_LSI_RIDGE_GRID"])
    t_lsi = time.time()
    reg_fit = lsilib.fit_transfer_regularised(
        LFr_tr[fit_idx], R_real[fit_idx], grid, ridge_grid,
        k_cut=kcut_rec["k_cut"], row_ids=fit_idx)
    T_reg = reg_fit["T"]
    ridge_star = float(reg_fit["ridge"])
    T_unreg = lsilib.fit_transfer(LFr_tr[fit_idx], R_real[fit_idx], grid, ridge=0.0)
    print(f"[lsi] k_cut={kcut_rec['k_cut']:.3f} (k_nyq_hf={kcut_rec['k_nyquist_hf']:.3f} "
          f"x {kcut_rec['n_lf_over_n_hf_per_axis']:.4f}) loocv ridge*={ridge_star:g} "
          f"n_fit={len(fit_idx)} max|T_reg|={reg_fit['max_abs_T']:.4g} "
          f"max|T_unreg|={float(np.abs(T_unreg).max()):.4g} "
          f"({time.time()-t_lsi:.1f}s)", flush=True)
    bandlimit_gate = lsilib.assert_bandlimited(T_reg, grid, kcut_rec["k_cut"])
    if tripwire:
        fit_set = set(int(i) for i in fit_idx)
        leaked = [int(i) for i in (reg_fit["loocv_row_ids"] or []) if int(i) not in fit_set]
        if leaked:
            raise R3S2ContractError(
                f"S6_LEAKAGE_TRIPWIRE: the LOOCV ridge selection saw rows {leaked} that "
                "are not in the fit fold")
    T_chain = {"reg": T_reg, "unreg": T_unreg}
    T_band_reg = lsilib.band_mean_abs(T_reg, band_masks_np)
    T_band_unreg = lsilib.band_mean_abs(T_unreg, band_masks_np)
    lsi_repair = {
        "kcut": kcut_rec,
        "bandlimit": reg_fit["bandlimit"],
        "bandlimit_gate": bandlimit_gate,
        "ridge_selection": {k: v for k, v in reg_fit.items() if k != "T"},
        "unregularised_replay": {
            "ridge": 0.0, "bandlimit": None, "max_abs_T": float(np.abs(T_unreg).max()),
            "arm": "A5_stack_ic_unreg",
            "note": "the literal B1 estimator, kept so the repair is ATTRIBUTABLE"},
        "T_band_mean_abs_reg": T_band_reg,
        "T_band_mean_abs_unreg": T_band_unreg,
        "declared_role": ("INSTRUMENT ACCEPTANCE (card clause G2), never a contribution. "
                          "Prior-art verdict E1: ridge/band-limiting is `preempted "
                          "(cite)`; 'Presenting ridge/band-limiting as the *idea* is a "
                          "rebadge'. Cited as preemption: arXiv:1810.08360 (LOOCV ridge "
                          "selection), arXiv:1511.07030 (low-sample-support shrinkage), "
                          "arXiv:2606.03936 (per-band weighting of a frozen operator)."),
    }

    # ══ training-free pre-registered probes ══════════════════════════════
    probes = {}
    if _truthy(knobs["R3S2_BC_AUDIT_SIDECAR"]):
        # ridge = the LOOCV-SELECTED coefficient, so the probe prices the same
        # estimator the scored arm uses (B1 passed the literal S6_LSI_RIDGE float,
        # which is no longer a float under S6_LSI_RIDGE=loocv).
        probes["P1_bc_match_audit"] = dict(probelib.bc_audit_trainonly(
            LFr_tr, Y_tr, grid, fit_idx, val_idx, ridge=ridge_star,
            wrap_ratio_max=pad["wrap_ratio_hf_max"],
            tol=knob_float(knobs, "S6_PERIODIC_TOL")),
            ridge_provenance=f"LOOCV-selected on the fit fold ({ridge_star:g})")
    probes["P2_cond_lf_identifiability"] = probelib.cond_lf_identifiability(
        X_lf_all.astype(np.float64), LF_nat_all)

    # ══ STAGE 1: the TWO front-end emulators (the stack route) ═══════════
    if knobs["R3S2_EMU_LOSS"] != "rel_l2":
        raise R3S2ContractError(f"R3S2_EMU_LOSS must be 'rel_l2' (recipe), got "
                                f"{knobs['R3S2_EMU_LOSS']!r}")
    emu_modes = knob_int(knobs, "R3S2_EMU_MODES")
    mh, mw = _modes(lf_grid, emu_modes)
    mh_hf, mw_hf = _modes(grid, emu_modes)
    emu_width = knob_int(knobs, "R3S2_EMU_WIDTH")
    emu_blocks = knob_int(knobs, "R3S2_EMU_BLOCKS")

    # the emulator hold-out slice: exactly the HF val slice (paired ladder), so the
    # emulator never sees a sample the corrector selects on.
    emu_val = np.array(sorted(set(int(i) for i in val_idx)), dtype=np.int64)
    emu_fit = np.array([i for i in range(N_lf) if i not in set(emu_val.tolist())],
                       dtype=np.int64)
    if not len(emu_fit):
        raise R3S2ContractError(f"{name}: empty emulator fit slice")

    s_emu = max(float(np.abs(LF_nat_all[emu_fit]).max()), 1e-8)
    Xl = torch.from_numpy(X_lf_all)
    Yl = torch.from_numpy((LF_nat_all / s_emu).astype(np.float32)).view(N_lf, h, w)
    emu_fit_t = torch.from_numpy(np.ascontiguousarray(emu_fit))
    bs = SMOKE["batch_size"]

    # `R3S2_IC_FALLBACK=film_only_recorded`: where the dataset has no `ic_c*` dims the
    # ic_synth arms do not merely RESEMBLE the film_only arms — they ARE them. One
    # net is built and the ic_synth record ALIASES it, so every A1-A2 / A3-A4
    # difference is exactly 0 by construction instead of being a second random init
    # that would manufacture a contrast out of seed noise.
    built_fronts = list(FRONT_ENDS) if ic_applicable else ["film_only"]
    fronts = {}
    for fe in built_fronts:
        # film_only is constructed FIRST and from the untouched global RNG, so its
        # init is the B1 emulator's init and the A5 replication check is meaningful.
        film_idx = (ic_layout["other_indices"]
                    if (ic_applicable and fe != "film_only") else None)
        net = Emulator(fe, cond_dim, film_idx, lf_grid, emu_width, emu_blocks,
                       mh, mw).to(device)
        fronts[fe] = {"tag": FRONT_TAG[fe], "net": net,
                      "ic_lf": ic_tensor("stack", fe, "lf"),
                      "ic_tr": ic_tensor("stack", fe, "tr"),
                      "ic_te": ic_tensor("stack", fe, "te"),
                      "film_dim": int(net.film_dim),
                      "n_params": int(param_count(net))}
    alias_of = {}
    for fe in FRONT_ENDS:
        if fe not in fronts:
            fronts[fe] = fronts["film_only"]   # THE SAME object, deliberately
            alias_of[fe] = "film_only"
    ic_record["front_end_alias"] = {
        "built": list(built_fronts),
        "aliased": {FRONT_TAG[k]: FRONT_TAG[v] for k, v in alias_of.items()},
        "note": ("under R3S2_IC_FALLBACK=film_only_recorded a non-applicable dataset "
                 "does not get a SECOND randomly-initialised trunk on either route: the "
                 "ic_synth arms alias the film_only ones, so A1-A2 and A3-A4 are exactly "
                 "0 by construction (gate V10)."),
    }

    def fell_back(fe: str) -> bool:
        return bool(fe != "film_only" and not ic_applicable)

    def _emu_loss_for(fe):
        st = fronts[fe]
        net, ic = st["net"], st["ic_lf"]

        def _loss(idx):
            net.train()
            sel = emu_fit_t[idx]
            extra = None if ic is None else ic[sel].to(device)
            p = net(Xl[sel].to(device), extra)
            t = Yl[sel].to(device)
            num = (p - t).reshape(p.shape[0], -1).norm(dim=1)
            den = t.reshape(t.shape[0], -1).norm(dim=1).clamp_min(1e-8)
            return (num / den).mean()
        return _loss

    t_train = time.time()
    for fe in built_fronts:
        st = fronts[fe]
        tag, net = FRONT_TAG[fe], st["net"]
        key, stage, stage_done = f"emu_{tag}", f"emu_{tag}", f"emu_{tag}_done"
        if ck is not None and ck.get(key) is not None:
            net.load_state_dict(ck[key])
        if ck_rank < STAGES[stage_done]:
            resume = ({k: ck[k] for k in ("opt", "sched", "gen", "epoch")}
                      if ck is not None and ck.get("stage") == stage and "opt" in ck else None)
            print(f"[stage {stage}] front end {fe!r} ({tag}) on {len(emu_fit)} LF samples "
                  f"at rung {lf_rung} ({h}x{w}), modes {mh}x{mw}, FiLM dim "
                  f"{st['film_dim']}{' + IC channel' if net.uses_ic_channel else ''}",
                  flush=True)

            def _writer(_key=key, _stage=stage, _net=net):
                def _w(epoch, opt, sched, g):
                    payload = dict(acc)
                    payload[_key] = _net.state_dict()
                    payload["s_emu"] = s_emu
                    _save_ckpt(ck_last, dict(meta, **payload, stage=_stage,
                                             epoch=int(epoch), opt=opt.state_dict(),
                                             sched=sched.state_dict(), gen=g.get_state()))
                return _w

            train_stage(list(net.parameters()), len(emu_fit), E_emu, LR_EMULATOR,
                        f"emu/{tag}", _emu_loss_for(fe), ckpt_write=_writer(),
                        resume=resume)
        else:
            print(f"[stage {stage}] already trained in checkpoint; skipping", flush=True)
        net.eval()
        persist(stage_done, **{key: net.state_dict()}, s_emu=s_emu)

    def emu_native(fe: str, X: np.ndarray, ic: torch.Tensor, net=None) -> np.ndarray:
        """(N, cond_dim) -> (N, h*w) pseudo-LF on the LF NATIVE grid, raw units."""
        net = net or fronts[fe]["net"]
        net.eval()
        Xt = torch.from_numpy(np.asarray(X, dtype=np.float32))
        out = np.empty((Xt.shape[0], h * w), dtype=np.float64)
        with torch.no_grad():
            for i in range(0, Xt.shape[0], bs):
                sl = slice(i, min(i + bs, Xt.shape[0]))
                extra = None if ic is None else ic[sl].to(device)
                p = net(Xt[sl].to(device), extra) * s_emu
                out[sl] = p.reshape(p.shape[0], -1).double().cpu().numpy()
        return out

    for fe in built_fronts:
        st = fronts[fe]
        st["LFp_tr"] = uplib.upsample_fields(
            emu_native(fe, X_tr, st["ic_tr"]), lf_grid, grid, name)
        st["LFp_te"] = uplib.upsample_fields(
            emu_native(fe, X_te, st["ic_te"]), lf_grid, grid, name)

    # ── V6: the pseudo-LF path must carry sample-specific signal ─────────
    if _truthy(knobs["R3S2_REQUIRE_PSEUDO_LF"]):
        for fe in FRONT_ENDS:
            LFp_te = fronts[fe]["LFp_te"]
            if LFp_te.shape != (Nte, HW) or not np.isfinite(LFp_te).all():
                raise R3S2ContractError(
                    f"V6 violated on {name} ({fe}): pseudo-LF test field is "
                    f"{LFp_te.shape} / non-finite")
            if not (float(LFp_te.std(axis=0).max()) > 0.0):
                raise R3S2ContractError(
                    f"V6 violated on {name} ({fe}): the pseudo-LF test field has ZERO "
                    "across-sample variance — it has collapsed to a constant and the "
                    "stack is a no-op")

    # ── V10: the IC channel is either live or a RECORDED fallback ────────
    d_e1_e0 = float(np.abs(fronts["ic_synth"]["LFp_te"] - fronts["film_only"]["LFp_te"]).max())
    if ic_applicable and not (d_e1_e0 > 0.0):
        raise R3S2ContractError(
            f"V10 violated on {name}: the IC channel is applicable but the ic_synth "
            "pseudo-LF is bit-identical to film_only's — the channel is inert")
    if (not ic_applicable) and d_e1_e0 != 0.0:
        raise R3S2ContractError(
            f"V10 violated on {name}: ic_synth is NOT applicable, so ic_synth must BE "
            f"film_only (R3S2_IC_FALLBACK=film_only_recorded), but they differ by {d_e1_e0!r}")

    # ── S1: emulator field error on the held-out LF slice, per front end ─
    sidecars = {}
    if _truthy(knobs["R3S2_EMU_ERROR_SIDECAR"]):
        s1 = {}
        for fe in FRONT_ENDS:
            st, tag = fronts[fe], FRONT_TAG[fe]
            ic_val = None if st["ic_lf"] is None else st["ic_lf"][torch.from_numpy(emu_val)]
            ic_fitr = None if st["ic_lf"] is None else st["ic_lf"][torch.from_numpy(emu_fit)]
            s1[tag] = {
                "front_end": fe, "n": int(len(emu_val)),
                "nrmse_lfhat_vs_lf_native": round_nrmse(
                    emu_native(fe, X_lf_all[emu_val], ic_val), LF_nat_all[emu_val]),
                "insample_nrmse_native": round_nrmse(
                    emu_native(fe, X_lf_all[emu_fit], ic_fitr), LF_nat_all[emu_fit]),
                "fell_back_to_film_only": fell_back(fe),
            }
            print(f"[S1] {tag} emulator field nRMSE (held out) = "
                  f"{s1[tag]['nrmse_lfhat_vs_lf_native']:.6f}", flush=True)
        sidecars["S1_emulator_field_error"] = s1

    # ══ the defect-correction stage (TWO chains: reg and unreg) ══════════
    kernel = knob_int(knobs, "S6_KERNEL")
    depth = knob_int(knobs, "S6_DEPTH")
    width = knob_int(knobs, "S6_WIDTH")
    Xt_tr = torch.from_numpy(X_tr)
    Xt_te = torch.from_numpy(X_te)

    def _new_modules():
        corrector = LocalCorrector(cond_dim, grid, width=width, depth=depth,
                                   kernel=kernel, padding_mode=padding_mode).to(device)
        gate = PixelGate(cond_dim, grid, width=width, kernel=kernel,
                         padding_mode=padding_mode).to(device)
        return corrector, gate

    def _delta(corrector, LFn, Xsrc, n, scaler_r) -> np.ndarray:
        corrector.eval()
        out = np.empty((n, HW), dtype=np.float64)
        with torch.no_grad():
            for i in range(0, n, bs):
                sl = slice(i, min(i + bs, n))
                d = corrector(LFn[sl].to(device), Xsrc[sl].to(device))
                out[sl] = d.reshape(d.shape[0], -1).double().cpu().numpy() * scaler_r
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

    def fit_dc(LF_base: np.ndarray, tag: str, T_fixed, init=None,
               ckpt_stage: str = None, resume_ck=None, ckpt_prefix: str = "") -> dict:
        """Fit alpha_lsi, LocalCorrector, PixelGate, alpha_nn on `LF_base` at fixed T.

        `T_fixed` is MANDATORY here (B1 allowed an internal fit): both chains build
        their transfer function up front, so there is no code path on which an
        unregularised T could be produced by default.
        """
        if T_fixed is None:
            raise R3S2ContractError("fit_dc requires an explicit T (no silent default)")
        R = Y_tr - LF_base
        T = T_fixed
        C_raw = lsilib.apply_transfer(LF_base, T, grid)
        a_lsi, a_lsi_ls, va_base, va_gated = fit_alpha(
            R[val_a], C_raw[val_a], LF_base[val_a], Y_tr[val_a], include_zero=True)
        C_lsi = float(a_lsi) * C_raw
        base_tr = LF_base + C_lsi
        RES_tr = R - C_lsi
        scaler_lf = max(float(np.abs(LF_base).max()), 1e-8)
        scaler_r = max(float(np.abs(RES_tr[fit_idx]).max()), 1e-8)
        LFn = torch.from_numpy((LF_base / scaler_lf).astype(np.float32)).view(Ntr, H, W)
        RESn = torch.from_numpy((RES_tr / scaler_r).astype(np.float32)).view(Ntr, H, W)

        corrector, gate = _new_modules()
        if init is not None:
            corrector.load_state_dict(init["corrector"])
            gate.load_state_dict(init["gate"])
        resume_sub = (resume_ck or {}).get("substage")
        if resume_ck is not None and resume_ck.get(ckpt_prefix + "corrector") is not None:
            corrector.load_state_dict(resume_ck[ckpt_prefix + "corrector"])
            gate.load_state_dict(resume_ck[ckpt_prefix + "gate"])
        fit_t = torch.from_numpy(np.ascontiguousarray(fit_idx))

        def _wr(sub):
            def _w(epoch, opt, sched, g):
                if ckpt_stage is None:
                    return
                payload = dict(acc)
                payload.update({ckpt_prefix + "corrector": corrector.state_dict(),
                                ckpt_prefix + "gate": gate.state_dict()})
                _save_ckpt(ck_last, dict(meta, **payload, stage=ckpt_stage, substage=sub,
                                         epoch=int(epoch), opt=opt.state_dict(),
                                         sched=sched.state_dict(), gen=g.get_state()))
            return _w

        def corr_loss(idx):
            corrector.train()
            sel = fit_t[idx]
            d = corrector(LFn[sel].to(device), Xt_tr[sel].to(device))
            return F.mse_loss(d, RESn[sel].to(device))

        print(f"[{tag}] stage 1 corrector: fit={len(fit_idx)} alpha_lsi={a_lsi:.6f} "
              f"scaler_r={scaler_r:.4e} rf={corrector.receptive_field} "
              f"pad={padding_mode}", flush=True)
        if resume_sub == "gate":
            print(f"[{tag}] stage 1 already done in checkpoint; skipping", flush=True)
        else:
            train_stage(list(corrector.parameters()), len(fit_idx), E_corr, LR_CORRECTOR,
                        f"{tag}/corrector", corr_loss, ckpt_write=_wr("corrector"),
                        resume=(resume_ck if resume_sub == "corrector" else None))

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

        print(f"[{tag}] stage 2 pixel gate (corrector frozen; g == 0 at init)", flush=True)
        train_stage(list(gate.parameters()), len(fit_idx), E_gate, LR_GATE,
                    f"{tag}/gate", gate_loss, ckpt_write=_wr("gate"),
                    resume=(resume_ck if resume_sub == "gate" else None))
        for p in corrector.parameters():
            p.requires_grad_(True)

        vb_t = torch.from_numpy(val_b)
        NN_val = (_gate_out(gate, LFn[vb_t], Xt_tr[vb_t], len(val_b))
                  * _delta(corrector, LFn[vb_t], Xt_tr[vb_t], len(val_b), scaler_r))
        a_nn, a_nn_ls, vb_base, vb_gated = fit_alpha(
            Y_tr[val_b] - base_tr[val_b], NN_val, base_tr[val_b], Y_tr[val_b],
            include_zero=True)
        print(f"[{tag}] stage 3 alpha_nn={a_nn:.6f} (ls {a_nn_ls:.6f}) "
              f"val_b base={vb_base:.6f} -> gated={vb_gated:.6f}", flush=True)
        return {
            "tag": tag, "T": T, "alpha_lsi": float(a_lsi), "alpha_lsi_ls": float(a_lsi_ls),
            "alpha_nn": float(a_nn), "alpha_nn_ls": float(a_nn_ls),
            "corrector": corrector, "gate": gate,
            "scaler_lf": scaler_lf, "scaler_r": scaler_r,
            "val_a_rel_base": float(va_base), "val_a_rel_gated": float(va_gated),
            "val_b_rel_base": float(vb_base), "val_b_rel_gated": float(vb_gated),
            "corrector_state_sha256": state_sha256(corrector.state_dict()),
            "gate_state_sha256": state_sha256(gate.state_dict()),
            "n_params": int(param_count(corrector) + param_count(gate)),
        }

    def dc_predict(dc: dict, LF_in: np.ndarray, Xsrc: torch.Tensor) -> np.ndarray:
        """`LF_in` (n, HW) on the HF grid + the MATCHING conditions `Xsrc` (n, d)."""
        n = LF_in.shape[0]
        if int(Xsrc.shape[0]) != n:
            raise R3S2ContractError(
                f"dc_predict: {n} LF rows but {int(Xsrc.shape[0])} condition rows — "
                "the FiLM conditioning would be mispaired")
        C = dc["alpha_lsi"] * lsilib.apply_transfer(LF_in, dc["T"], grid)
        LFn = torch.from_numpy((LF_in / dc["scaler_lf"]).astype(np.float32)).view(n, H, W)
        D = _delta(dc["corrector"], LFn, Xsrc, n, dc["scaler_r"])
        G = _gate_out(dc["gate"], LFn, Xsrc, n)
        return LF_in + C + dc["alpha_nn"] * G * D

    def restore_dc(payload: dict, prefix: str, tag: str, T) -> dict:
        """Rebuild a fitted DC stage from a checkpoint (preemption resume)."""
        corrector, gate = _new_modules()
        corrector.load_state_dict(payload[prefix + "corrector"])
        gate.load_state_dict(payload[prefix + "gate"])
        corrector.eval(); gate.eval()
        print(f"[{tag}] restored from checkpoint (no gradient step taken)", flush=True)
        return {
            "tag": tag, "T": T,
            "alpha_lsi": float(payload[prefix + "alpha_lsi"]),
            "alpha_nn": float(payload[prefix + "alpha_nn"]),
            "corrector": corrector, "gate": gate,
            "scaler_lf": float(payload[prefix + "scaler_lf"]),
            "scaler_r": float(payload[prefix + "scaler_r"]),
            "restored_from_checkpoint": True,
            "corrector_state_sha256": state_sha256(corrector.state_dict()),
            "gate_state_sha256": state_sha256(gate.state_dict()),
            "n_params": int(param_count(corrector) + param_count(gate)),
        }

    def dc_payload(dc: dict, prefix: str) -> dict:
        return {prefix + "corrector": dc["corrector"].state_dict(),
                prefix + "gate": dc["gate"].state_dict(),
                prefix + "T": lsilib.pack_transfer(dc["T"]),
                prefix + "alpha_lsi": dc["alpha_lsi"], prefix + "alpha_nn": dc["alpha_nn"],
                prefix + "scaler_lf": dc["scaler_lf"], prefix + "scaler_r": dc["scaler_r"]}

    dc_ext = {}
    dc_real_rec = {}
    for chain in ("reg", "unreg"):
        T_c = T_chain[chain]
        p_real, p_ext = f"{chain}_", f"{chain}ext_"
        s_real, s_ext = f"dc_{chain}_real", f"dc_{chain}_ext"
        # the COMMON ANCESTOR of this chain: E_dc epochs on REAL LF
        if ck_rank >= STAGES[s_real + "_done"] and (ck or {}).get(p_real + "corrector") is not None:
            dc_r = restore_dc(ck, p_real, s_real, T_c)
        else:
            dc_r = fit_dc(LFr_tr, s_real, T_fixed=T_c, ckpt_stage=s_real,
                          ckpt_prefix=p_real,
                          resume_ck=(ck if (ck or {}).get("stage") == s_real else None))
        persist(s_real + "_done", **dc_payload(dc_r, p_real))
        init_common = {"corrector": dc_r["corrector"].state_dict(),
                       "gate": dc_r["gate"].state_dict()}
        # `frozen`: the ancestor + a FURTHER E_dc on REAL LF (budget match)
        if ck_rank >= STAGES[s_ext + "_done"] and (ck or {}).get(p_ext + "corrector") is not None:
            dc_e = restore_dc(ck, p_ext, s_ext, T_c)
        else:
            dc_e = fit_dc(LFr_tr, s_ext, T_fixed=T_c, init=init_common,
                          ckpt_stage=s_ext, ckpt_prefix=p_ext,
                          resume_ck=(ck if (ck or {}).get("stage") == s_ext else None))
        persist(s_ext + "_done", **dc_payload(dc_e, p_ext))
        dc_ext[chain] = dc_e
        dc_real_rec[chain] = {k: v for k, v in dc_r.items()
                              if k not in ("T", "corrector", "gate")}

    # ══ the DIRECT route ═════════════════════════════════════════════════
    rows_rec = directlib.train_rows(Ntr, fit_idx, val_idx, DIRECT_VAL_THRESHOLD)
    d_rows = rows_rec["rows"]
    s_y_direct = max(float(np.abs(Y_tr[d_rows]).max()), 1e-8)
    Yd = torch.from_numpy((Y_tr / s_y_direct).astype(np.float32)).view(Ntr, H, W)
    d_rows_t = torch.from_numpy(np.ascontiguousarray(d_rows))
    directs = {}
    built_direct = list(FRONT_ENDS) if ic_applicable else ["film_only"]
    for fe in built_direct:
        film_idx = (ic_layout["other_indices"]
                    if (ic_applicable and fe != "film_only") else None)
        tag = FRONT_TAG[fe]
        net = directlib.build(fe, cond_dim, film_idx, grid, emu_width, emu_blocks,
                              mh_hf, mw_hf, device)
        ic_tr_d = ic_tensor("direct", fe, "tr")
        ic_te_d = ic_tensor("direct", fe, "te")
        key, stage = f"direct_{tag}", f"direct_{tag}"
        if ck is not None and ck.get(key) is not None:
            net.load_state_dict(ck[key])
        if ck_rank < STAGES[stage + "_done"]:
            resume = ({k: ck[k] for k in ("opt", "sched", "gen", "epoch")}
                      if ck is not None and ck.get("stage") == stage and "opt" in ck else None)
            print(f"[stage {stage}] DIRECT cond->HF head {fe!r} on {len(d_rows)} HF rows "
                  f"at {H}x{W}, modes {mh_hf}x{mw_hf}, {E_direct} epochs "
                  f"({rows_rec['rule']})", flush=True)

            def _dloss(idx, _net=net, _ic=ic_tr_d):
                _net.train()
                sel = d_rows_t[idx]
                extra = None if _ic is None else _ic[sel].to(device)
                p = _net(Xt_tr[sel].to(device), extra)
                return directlib.rel_l2_loss(p, Yd[sel].to(device))

            def _dwriter(_key=key, _stage=stage, _net=net):
                def _w(epoch, opt, sched, g):
                    payload = dict(acc)
                    payload[_key] = _net.state_dict()
                    payload["s_y_direct"] = s_y_direct
                    _save_ckpt(ck_last, dict(meta, **payload, stage=_stage,
                                             epoch=int(epoch), opt=opt.state_dict(),
                                             sched=sched.state_dict(), gen=g.get_state()))
                return _w

            train_stage(list(net.parameters()), len(d_rows), E_direct, LR_DIRECT,
                        f"direct/{tag}", _dloss, ckpt_write=_dwriter(), resume=resume)
        else:
            print(f"[stage {stage}] already trained in checkpoint; skipping", flush=True)
        net.eval()
        persist(stage + "_done", **{key: net.state_dict()}, s_y_direct=s_y_direct)
        directs[fe] = {"net": net, "ic_tr": ic_tr_d, "ic_te": ic_te_d,
                       "n_params": int(param_count(net)), "tag": tag}
    direct_alias = {}
    for fe in FRONT_ENDS:
        if fe not in directs:
            directs[fe] = directs["film_only"]
            direct_alias[fe] = "film_only"

    def direct_predict(fe: str, X: np.ndarray, split: str) -> np.ndarray:
        """`split` selects the IC channel that goes WITH `X`; `X` must therefore be
        the FULL split array in its original row order (the IC tensor is indexed by
        the same row positions). Slice the RESULT, never the input."""
        d = directs[fe]
        ic = d["ic_tr"] if split == "tr" else d["ic_te"]
        n_ic = None if ic is None else int(ic.shape[0])
        if n_ic is not None and n_ic != int(np.asarray(X).shape[0]):
            raise R3S2ContractError(
                f"direct_predict: {X.shape[0]} condition rows but {n_ic} IC-channel rows "
                "— the IC field would be mispaired; pass the full split array")
        return directlib.predict(d["net"], X, ic, s_y_direct, grid, device, bs)

    # ══ predictions ══════════════════════════════════════════════════════
    t_eval = time.time()
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize()
    preds = {
        "A1_stack_ic_reg": dc_predict(dc_ext["reg"], fronts["ic_synth"]["LFp_te"], Xt_te),
        "A2_stack_film_reg": dc_predict(dc_ext["reg"], fronts["film_only"]["LFp_te"], Xt_te),
        "A5_stack_ic_unreg": dc_predict(dc_ext["unreg"], fronts["ic_synth"]["LFp_te"], Xt_te),
        "A7_emul_only_ic": fronts["ic_synth"]["LFp_te"],
        "A3_direct_ic": direct_predict("ic_synth", X_te, "te"),
        "A4_direct_film": direct_predict("film_only", X_te, "te"),
    }
    # the direct heads' TRAIN-row predictions, computed once (the A6 selector and
    # the S2 sidecar both read them; both slice the RESULT, never the input)
    direct_tr_pred = {fe: direct_predict(fe, X_tr, "tr") for fe in FRONT_ENDS}
    if device.type == "cuda":
        torch.cuda.synchronize()
    eval_seconds = time.time() - t_eval
    train_seconds = t_eval - t_train

    # ── the mandatory floor arms (needed before A6: they define its scope) ─
    floors = floorlib.collect(name, [HERE.parents[1], _main_repo_root()],
                              knobs["R3S2_FLOOR_ARMS"])
    aff = floors.get("affine_on_hf_train") or {}
    affine_floor_certified = bool(aff and aff.get("applicable") is not False)

    # ── A6: the closed-form LOO selector (ifc cells only, ZERO GPU) ──────
    # SCOPE IS DATA-DRIVEN, not name-matched: the selector is defined exactly where
    # a certified `affine_on_hf_train` floor exists, which is program.md §2's
    # affine-floor rule and (today) exactly the two ifc cells.
    selector_rec = None
    if affine_floor_certified and Ntr >= 2:
        trained_for_sel = {
            "A1_stack_ic_reg": {
                "train_pred": dc_predict(dc_ext["reg"], fronts["ic_synth"]["LFp_tr"], Xt_tr),
                "test_pred": preds["A1_stack_ic_reg"],
                # the corrector's own fit fold; the front end additionally fitted
                # emu_fit and the two gains were selected on val_a / val_b.
                "fit_rows": np.asarray(fit_idx, dtype=np.int64)},
            "A3_direct_ic": {
                "train_pred": direct_tr_pred["ic_synth"],
                "test_pred": preds["A3_direct_ic"],
                "fit_rows": np.asarray(d_rows, dtype=np.int64)},
        }
        selector_rec, sel_pred = sellib.run(
            Y_tr, X_tr.astype(np.float64), X_te.astype(np.float64), Y_te,
            trained_for_sel, round_nrmse, knobs["R3S2B2_IFC_LOO_SELECTOR"])
        selector_rec["applicable"] = True
        preds["A6_ifc_loo_selector"] = sel_pred
        selector_rec["affine_floor_cross_check"] = {
            "in_job_affine_test_nrmse":
                selector_rec["scores"]["affine_on_hf_train"][
                    "test_nrmse_reported_after_selection"],
            "certified_floor_entry": aff,
            "note": ("the in-job affine estimator is the certified floor's estimator; a "
                     "large deviation between the two would mean the floor and the "
                     "selector disagree about the same closed form"),
        }
        print(f"[A6] selector on {name}: {selector_rec['selected']} "
              f"(test nRMSE {selector_rec['selected_test_nrmse']:.6f})", flush=True)
    else:
        selector_rec = {
            "applicable": False,
            "reason": ("no certified `affine_on_hf_train` floor for this cell "
                       "(program.md §2's affine-floor rule is scoped to the ifc cells), "
                       "so the selector's candidate set is undefined here"),
            "n_train_hf_rows": int(Ntr),
        }

    # ── validity gates ───────────────────────────────────────────────────
    v1 = {}
    for fe in FRONT_ENDS:
        st, tag = fronts[fe], FRONT_TAG[fe]
        ref = uplib.upsample_fields(emu_native(fe, X_te, st["ic_te"]), lf_grid, grid, name)
        dev = float(np.abs(st["LFp_te"] - ref).max())
        if dev != 0.0:
            raise R3S2ContractError(
                f"V1 violated on {name} ({fe}): the pseudo-LF test field deviates from an "
                f"independently re-derived upsampled emulator output by {dev!r}")
        v1[tag] = dev
    v15 = {}
    for fe, armtag in (("ic_synth", "A3_direct_ic"), ("film_only", "A4_direct_film")):
        dev = float(np.abs(preds[armtag] - direct_predict(fe, X_te, "te")).max())
        if dev != 0.0:
            raise R3S2ContractError(
                f"V15 violated on {name} ({armtag}): the direct arm is not reproducible "
                f"from an independent forward pass (max|delta| = {dev!r})")
        v15[armtag] = dev
    v10_direct = float(np.abs(preds["A3_direct_ic"] - preds["A4_direct_film"]).max())
    if (not ic_applicable) and v10_direct != 0.0:
        raise R3S2ContractError(
            f"V10 violated on {name}: ic_synth is not applicable, so A3 must BE A4, "
            f"but they differ by {v10_direct!r}")
    stage2_totals = {k: v for k, v in arm_epochs.items()
                     if k in ("A1_stack_ic_reg", "A2_stack_film_reg", "A3_direct_ic",
                              "A4_direct_film", "A5_stack_ic_unreg")}
    if len(set(stage2_totals.values())) != 1:
        raise R3S2ContractError(
            f"V11 violated: R3S2_BUDGET_MATCH=arm_equal_total but the budget-matched arms "
            f"spend different optimizer-epoch totals {stage2_totals}")
    sha_reg = dc_ext["reg"]["corrector_state_sha256"]
    sha_unreg = dc_ext["unreg"]["corrector_state_sha256"]
    chains_degenerate = bool(sha_reg == sha_unreg)
    if chains_degenerate:
        # Not fatal by itself (the two chains CAN coincide if the LOOCV selects
        # ridge 0 and the band-limit removes nothing), but it means the repair is
        # unattributable on this cell, so it is recorded loudly rather than hidden.
        print("[warn] the reg and unreg correctors share a state hash — the repair "
              "attribution on this cell is degenerate (A5 == A1 by construction)",
              flush=True)

    n_train_route = {
        "A1_stack_ic_reg": {"stage1_lf_rows": int(len(emu_fit)), "n_lf_total": int(N_lf),
                            "corrector_hf_fit_rows": int(len(fit_idx)),
                            "gain_selection_hf_rows": int(len(val_idx))},
        "A2_stack_film_reg": {"stage1_lf_rows": int(len(emu_fit)), "n_lf_total": int(N_lf),
                              "corrector_hf_fit_rows": int(len(fit_idx)),
                              "gain_selection_hf_rows": int(len(val_idx))},
        "A5_stack_ic_unreg": {"stage1_lf_rows": int(len(emu_fit)), "n_lf_total": int(N_lf),
                              "corrector_hf_fit_rows": int(len(fit_idx)),
                              "gain_selection_hf_rows": int(len(val_idx))},
        "A7_emul_only_ic": {"stage1_lf_rows": int(len(emu_fit)), "n_lf_total": int(N_lf)},
        "A3_direct_ic": {"hf_rows": int(rows_rec["n_train_route"]),
                         "n_hf_train_total": int(Ntr),
                         "val_disjoint": bool(rows_rec["val_disjoint"])},
        "A4_direct_film": {"hf_rows": int(rows_rec["n_train_route"]),
                           "n_hf_train_total": int(Ntr),
                           "val_disjoint": bool(rows_rec["val_disjoint"])},
        "_knob": knobs["R3S2B2_ROUTE_DATA_DISCLOSURE"],
        "_why": ("card part 3 / FLAG C: on the ifc cells the stack's stage 1 fits 18 of "
                 "20 LF rows while the direct head sees 5 HF rows. Every ifc route delta "
                 "carries this disclosure, and the ifc HEADLINE is A6, not the raw delta."),
    }

    gates = {
        "V1_pseudo_lf_is_upsampled_emulator": {"max_abs_dev_by_front_end": v1, "pass": True},
        "V2_no_test_lf_path": {"test_lf_fids": list(test["lf_fids"]), "pass": True,
                               "note": "asserted before any array was read"},
        "V3_frozen_corrector_state": {
            "reg_sha256": sha_reg, "unreg_sha256": sha_unreg,
            "chains_degenerate": chains_degenerate,
            "note": ("both `frozen` chains fit their corrector on REAL LF only; the "
                     "pseudo-LF is seen for the first time at prediction time. "
                     "`chains_degenerate` true would mean A5 == A1 and the G2 repair "
                     "attribution is empty on this cell."),
            "pass": True},
        "V6_pseudo_lf_required": {
            "knob": knobs["R3S2_REQUIRE_PSEUDO_LF"],
            "pseudo_lf_test_max_across_sample_std": {
                FRONT_TAG[fe]: float(fronts[fe]["LFp_te"].std(axis=0).max())
                for fe in FRONT_ENDS},
            "fallback_fired": False, "pass": True},
        "V6b_paired_real_lf": dict(pairing, pass_=paired),
        "V8_ic_equivalence": ic_gates.get("equivalence", {
            "skipped": "ic_synth not applicable on this dataset"}),
        "V10_ic_channel_live_or_recorded_fallback": {
            "ic_synth_applicable": ic_applicable,
            "max_abs_dev_stack_ic_vs_film_pseudo_lf": d_e1_e0,
            "max_abs_dev_direct_ic_vs_direct_film": v10_direct,
            "pass": True,
            "note": ("when the IC channel applies, the ic_synth arms must differ from the "
                     "film_only ones on BOTH routes; when it does not, they must BE them "
                     "(R3S2_IC_FALLBACK=film_only_recorded)")},
        "V11_arm_equal_total_budget": {"budget_matched_arms": stage2_totals,
                                       "stage2_total": int(E_stage2),
                                       "direct_total": int(E_direct), "pass": True},
        "V12_lsi_bandlimited_above_lf_nyquist": dict(bandlimit_gate, **kcut_rec),
        "V13_loocv_fit_fold_only": {
            "tripwire": knobs["S6_LEAKAGE_TRIPWIRE"],
            "selected_ridge": ridge_star,
            "n_loocv_rows": int(len(reg_fit["loocv_row_ids"] or [])),
            "all_rows_in_fit_fold": True,
            "selected_by": reg_fit["selected_by"], "pass": True},
        "V14_ckpt_data_hash_bind": dict(resume_record, data_sha256=data_sha,
                                        knob=knobs["R3S2B2_CKPT_DATA_HASH_BIND"],
                                        pass_=True),
        "V15_direct_route_reproducible_and_lf_free": {
            "max_abs_dev_vs_independent_forward_pass": v15,
            "direct_reads_any_lf_array": False,
            "note": ("the direct route's inputs are the condition vector and the analytic "
                     "IC field synthesised FROM it; no LF array enters direct_head.predict "
                     "(see direct_head.py) and the arm reproduces bit-exactly"),
            "pass": True},
        "V16_route_data_disclosure": n_train_route,
    }

    # ── S2: the real-LF oracle ceiling, on the TRAIN hold-out slice ──────
    if _truthy(knobs["R3S2_ORACLE_TRAINHELDOUT_SIDECAR"]):
        Xv = Xt_tr[torch.from_numpy(np.ascontiguousarray(val_idx))]
        s2 = {
            "slice": "train val slice (val_a + val_b); NO test array touched",
            "n": int(len(val_idx)),
            "nrmse_realLF_oracle_reg": round_nrmse(
                dc_predict(dc_ext["reg"], LFr_tr[val_idx], Xv), Y_tr[val_idx]),
            "nrmse_realLF_oracle_unreg": round_nrmse(
                dc_predict(dc_ext["unreg"], LFr_tr[val_idx], Xv), Y_tr[val_idx]),
            "nrmse_copylf_identity_same_slice": round_nrmse(LFr_tr[val_idx], Y_tr[val_idx]),
            "note": ("the 'perfect emulator' ceiling measured in-job: the SAME frozen "
                     "corrector fed REAL LF vs each front end's pseudo-LF on the same "
                     "held-out TRAIN samples. Their ratio is the emulator-error "
                     "contribution, and it is the stack's half of the route delta."),
        }
        for fe in FRONT_ENDS:
            s2[f"nrmse_pseudoLF_{FRONT_TAG[fe]}_reg_same_slice"] = round_nrmse(
                dc_predict(dc_ext["reg"], fronts[fe]["LFp_tr"][val_idx], Xv), Y_tr[val_idx])
        s2["nrmse_direct_ic_same_slice"] = round_nrmse(
            direct_tr_pred["ic_synth"][val_idx], Y_tr[val_idx])
        if rows_rec["val_disjoint"]:
            s2["direct_val_slice_is_heldout"] = True
        else:
            s2["direct_val_slice_is_heldout"] = False
            s2["direct_note"] = ("N_train_HF < 20: the direct head trained on every HF "
                                 "row, so it has no held-out train slice (recorded, "
                                 "R3S2B2_DIRECT_VAL)")
        sidecars["S2_oracle_realLF_trainheldout"] = s2

    # ── S3: the closed form, priced on the SAME intermediate, out of fold ─
    if _truthy(knobs["R3S2_ZERO_GRADIENT_LADDER_SIDECAR"]):
        base_1 = Y_tr[fit_idx].mean(axis=0, keepdims=True)

        def _ladder_fit(LF, R, g, ridge=0.0):
            """The ladder prices the closed form with the SAME estimator the scored
            arm uses (LOOCV ridge + band-limit), not the unregularised one."""
            return lsilib.fit_transfer_regularised(
                LF, R, g, ridge_grid, k_cut=kcut_rec["k_cut"])["T"]

        s3 = {}
        for fe in FRONT_ENDS:
            st, tag = fronts[fe], FRONT_TAG[fe]
            if fe in alias_of:
                s3[tag] = s3[FRONT_TAG[alias_of[fe]]]
                continue
            s3[tag] = sidelib.zero_gradient_ladder(
                st["LFp_tr"], st["LFp_te"], Y_tr, Y_te,
                np.repeat(base_1, Ntr, axis=0), np.repeat(base_1, Nte, axis=0),
                grid, fit_idx, val_a, _ladder_fit, lsilib.apply_transfer,
                fit_alpha, round_nrmse, ridge=ridge_star)
        s3["estimator_note"] = (
            "the ladder's LSI rung uses the REPAIRED estimator (LOOCV ridge + "
            "band-limit above the LF Nyquist), so a trained arm cannot beat the closed "
            "form merely by being better regularised than it")
        s3["real_lf_intermediate_note"] = (
            "the ladder is built on each front end's PSEUDO-LF test intermediate, the "
            "same array the trained stack arms consume, so the comparison is like-for-like")
        sidecars["S3_zero_gradient_stage_ladder"] = s3

    # ── S7: the E3 instrument — model-free map smoothness (all cells) ────
    if _truthy(knobs["R3S2B2_MAP_SMOOTHNESS_SIDECAR"]):
        sidecars["S7_map_smoothness"] = {
            "test": sidelib.map_smoothness(Y_te, X_te.astype(np.float64),
                                           MAP_SMOOTHNESS_ROW_CAP, rng_seed=0),
            "train": sidelib.map_smoothness(Y_tr, X_tr.astype(np.float64),
                                            MAP_SMOOTHNESS_ROW_CAP, rng_seed=0),
            "row_cap": MAP_SMOOTHNESS_ROW_CAP,
            "role": ("the E3 instrument, declared PROSPECTIVELY (clause G3): a cell whose "
                     "map_smoothness_ratio is ~1 is APPROXIMABILITY-limited, so the ROUTE "
                     "is not the binding constraint there. The card's pre-run declaration "
                     "is that sharp__cahn_hilliard (0.980) is such a cell. Measured on "
                     "every cell so the declaration is prospective, not retrofitted."),
            "prospective_declaration": ("|A1 - A3| on sharp__cahn_hilliard is predicted to "
                                        "stay below tau_rel(ch) = 0.3612 skill units"),
        }

    sidecars["S6_target_scale_preflight"] = {
        "knob": knobs["R3S2_TARGET_SCALER_PREFLIGHT"],
        "applied": False,
        "note": ("the recipe fixes this to not_applicable: neither ext__helmholtz_2d nor "
                 "sharp__phase_field_crystal_2d is in the scored dataset list, and no "
                 "dataset gets a different residual estimator. Recorded, never applied."),
    }

    # ── diagnostics ──────────────────────────────────────────────────────
    arm_results = {}
    for tag in FIELD_ARMS:
        p = preds[tag]
        arm_results[tag] = {
            "nrmse": round_nrmse(p, Y_te),
            "role": ARM_ROLE[tag],
            "knobs": ARM_SPEC[tag],
            "optimizer_epochs": int(arm_epochs[tag]),
            "front_end_fell_back_to_film_only": bool(
                (not ic_applicable) and ARM_SPEC[tag]["R3S2_FRONTEND"] == "ic_synth"),
        }
    if selector_rec.get("applicable") is not False:
        arm_results["A6_ifc_loo_selector"] = {
            "nrmse": round_nrmse(preds["A6_ifc_loo_selector"], Y_te),
            "role": ARM_ROLE["A6_ifc_loo_selector"],
            "knobs": ARM_SPEC["A6_ifc_loo_selector"],
            "optimizer_epochs": 0,
            "selected": selector_rec["selected"],
        }
    a = {k: v["nrmse"] for k, v in arm_results.items()}

    band_cols = {}
    if _truthy(knobs["R3S2B2_BAND_ERROR_COLUMNS"]):
        for tag in FIELD_ARMS:
            band_cols[tag] = bandlib.band_error_energy(preds[tag] - Y_te, grid)
        band_cols["_identity_pseudo_lf_film_only"] = bandlib.band_error_energy(
            fronts["film_only"]["LFp_te"] - Y_te, grid)
        band_cols["_edges_wavenumber"] = [float(e) for e in band_edges]
        band_cols["_note"] = ("4-band error columns for every field arm (Duraisamy "
                              "arXiv:2604.20061's reporting standard, card part 3). "
                              "Band 4 is the octave above the LF Nyquist.")

    mce_note = ("skill units require the cell's copy-LF reference and the certified "
                "min_claimable_effect, both of which live OUTSIDE this family; the "
                "analyzer converts. Deltas below are in nRMSE units, with the "
                "reference-free FRACTIONAL form beside each (R3S2B2_REPORT_UNITS).")
    attribution = {
        "G1_route_delta_A1_minus_A3": a["A1_stack_ic_reg"] - a["A3_direct_ic"],
        "G1_route_delta_A1_minus_A3_fractional_vs_A3":
            frac_reduction(a["A3_direct_ic"], a["A1_stack_ic_reg"]),
        "route_delta_A2_minus_A4": a["A2_stack_film_reg"] - a["A4_direct_film"],
        "route_delta_A2_minus_A4_fractional_vs_A4":
            frac_reduction(a["A4_direct_film"], a["A2_stack_film_reg"]),
        "G2_repair_delta_A5_minus_A1": a["A5_stack_ic_unreg"] - a["A1_stack_ic_reg"],
        "G2_repair_delta_fractional_vs_A5":
            frac_reduction(a["A5_stack_ic_unreg"], a["A1_stack_ic_reg"]),
        "front_end_delta_stack_A1_minus_A2": a["A1_stack_ic_reg"] - a["A2_stack_film_reg"],
        "front_end_delta_direct_A3_minus_A4": a["A3_direct_ic"] - a["A4_direct_film"],
        "transport_term_A1_minus_A7": a["A1_stack_ic_reg"] - a["A7_emul_only_ic"],
        "stage1_reference_A7": a["A7_emul_only_ic"],
        "calibration_A4_vs_r2s1_direct_B2_certified_23_7753": {
            "A4_nrmse_this_cell": a["A4_direct_film"],
            "note": ("23.7753 is a PANEL GEOMEAN IN SKILL UNITS, not a per-cell nRMSE; "
                     "the analyzer performs the comparison. If A4 lands far from it, the "
                     "family and not the route is the story (recipe _novelty_declaration).")},
        "anchor_replication_A5": {
            "target_panel_geomean_skill": knobs["R3S2B2_ANCHOR_REPLICATION_CHECK"],
            "tolerance_panel_seed_mce": 0.5083,
            "A5_nrmse_this_cell": a["A5_stack_ic_unreg"],
            "note": ("G2 leg (iv) is a PANEL-level check in skill units; this cell "
                     "publishes the raw A5 nRMSE the analyzer aggregates. A5 is the "
                     "literal B1 estimator (ridge 0, no band-limit) on the same folds.")},
        "valid": bool(paired),
        "ic_synth_applicable": ic_applicable,
        "note": ("G1 is the card's actual result and its SIGN IS NOT ASSUMED — the "
                 "reverse inequality at the same magnitude is recorded as the affirmative "
                 "negative ('the LF intermediate is a strict tax'). G2 is instrument "
                 "acceptance, never a contribution. " + mce_note),
    }

    diag = dict(pad)
    diag.update({
        "model": MODEL_NAME, "dataset": name, "seed": int(args.seed),
        "epochs": int(args.epochs), "scored_arm": scored_tag,
        "nrmse_def_hash": NRMSE_DEF_HASH, "nrmse_sha256": NRMSE_DEF_HASH,
        "knobs": knobs, "budget": budget, "split_protocol": split_rec,
        "pairing": pairing, "upsample_convention": up_fn_name,
        "lf_rung": int(lf_rung), "lf_grid": list(lf_grid), "hf_grid": list(hf_grid),
        "res_min_grid": list(res_min_grid),
        "dataset_content_sha256": data_sha,
        "ic_synthesis": ic_record,
        "front_ends": {FRONT_TAG[fe]: {
            "knob": fe, "film_dim": fronts[fe]["film_dim"],
            "uses_ic_channel": bool(fronts[fe]["net"].uses_ic_channel),
            "fell_back_to_film_only": fell_back(fe),
            "n_params": fronts[fe]["n_params"]} for fe in FRONT_ENDS},
        "emulator": {"width": emu_width, "blocks": emu_blocks,
                     "modes": [int(mh), int(mw)], "loss": "rel_l2",
                     "n_fit": int(len(emu_fit)), "n_heldout": int(len(emu_val)),
                     "scaler": s_emu, "one_emulator_per_front_end": True},
        "direct_head": {
            "trunk": knobs["R3S2B2_DIRECT_TRUNK"], "target": knobs["R3S2B2_DIRECT_TARGET"],
            "grid": list(grid), "modes": [int(mh_hf), int(mw_hf)],
            "width": emu_width, "blocks": emu_blocks, "loss": "rel_l2",
            "lr": LR_DIRECT, "epochs": int(E_direct), "scaler": s_y_direct,
            "rows": {k: v for k, v in rows_rec.items()
                     if k not in ("rows", "val_slice")},
            "n_params": {FRONT_TAG[fe]: directs[fe]["n_params"] for fe in FRONT_ENDS},
            "aliased": {FRONT_TAG[k]: FRONT_TAG[v] for k, v in direct_alias.items()},
            "loss_provenance": ("rel_l2, matching the emulator's R3S2_EMU_LOSS — the "
                                "card's source_iteration (brainstormer iteration_2 item 4) "
                                "states the training objectives are rel_l2 for both the "
                                "emulator and the direct head and are recorded in the diag"),
            "lr_provenance": ("SMOKE.lr_pretrain (1e-3) from the base family — the direct "
                              "head is the same trunk trained from scratch, so it takes "
                              "the emulator's pre-training lr; no new constant"),
        },
        "lsi_repair": lsi_repair,
        "dc_real": dc_real_rec,
        "dc_frozen_ext": {c: {k: v for k, v in dc_ext[c].items()
                              if k not in ("T", "corrector", "gate")}
                          for c in ("reg", "unreg")},
        "dc_fit_source": "real_lf (paired ladder; the pairing gate refuses anything else)",
        "arms": arm_results, "attribution": attribution,
        "ifc_loo_selector": selector_rec,
        "floor_arms": floors,
        "floor_comparison_scored_arm": floorlib.beat_table(a[scored_tag], floors),
        "floor_comparison_by_arm": {t: floorlib.beat_table(a[t], floors)
                                    for t in arm_results},
        "sidecars": sidecars, "probes": probes, "validity_gates": gates,
        "bands": {"edges_wavenumber": [float(e) for e in band_edges],
                  "k_nyquist": float(min(H, W) / 2.0), "n_bands": bandlib.N_BANDS},
        "band_err_energy_by_arm": band_cols,
        # `tools/lsi_transfer_stability_audit.py` reads THESE two keys; they must
        # describe the SCORED arm's transfer function and error attribution (G2 iii).
        "T_band_mean_abs": T_band_reg,
        "T_band_mean_abs_unregularised_A5": T_band_unreg,
        "band_err_energy_E0_emul_only": band_cols.get(
            "_identity_pseudo_lf_film_only", bandlib.band_error_energy(
                fronts["film_only"]["LFp_te"] - Y_te, grid)),
        "band_err_energy_scored_arm": band_cols.get(
            scored_tag, bandlib.band_error_energy(preds[scored_tag] - Y_te, grid)),
        "band_contribution_profile": [
            (float(x / y) if y > 0 else float("nan"))
            for x, y in zip(
                band_cols.get(scored_tag,
                              bandlib.band_error_energy(preds[scored_tag] - Y_te, grid)),
                band_cols.get("_identity_pseudo_lf_film_only",
                              bandlib.band_error_energy(
                                  fronts["film_only"]["LFp_te"] - Y_te, grid)))],
        "device": str(device),
        "vendor_source": ("round3/worktrees/r3s2_field_reach/B1/models_r3/r3s2_stack_ic @ "
                          "d5069a74bb63da837b89b16508ae25a2164780cc (model.py, front_end.py, "
                          "ic_synth.py, lsi_filter.py, local_corrector.py, bands.py, "
                          "periodicity.py, upsample.py, floor_arms.py, probes.py, "
                          "sidecars.py — per-file sha256 in _vendor_manifest.json). That "
                          "family in turn vendors r2s2_stack @ 6b4e1d48 and round-1 "
                          "s4_router @ b90d4662. NO code is vendored from r2s1_direct. "
                          "IC-synthesis math remains B1's re-implementation from the "
                          "READ-ONLY generator surfaces mffp_sharp/common/ic_encoding.py"
                          "::ic_2d and common/spectral.py::spectral_interp (never "
                          "imported, never edited)."),
        "declared_reuse": ("role (a), round-2 program 5.10a: the DC-lineage corrector is a "
                           "declared frozen test-time sub-component behind a "
                           "condition->pseudo-LF front end. A5 (ridge=0) is the literal B1 "
                           "replay and is declared as the pre-registered replication/"
                           "attribution arm, not as a novelty claim."),
        "novelty_declaration": ("the new pathway is a SINGLE shared FiLM-FNO trunk behind a "
                                "ROUTE SWITCH with a budget accountant holding total "
                                "optimizer epochs equal across routes, and a REGULARISED "
                                "LSI transfer stage. The direct_* arms are declared MATCHED "
                                "CONTROLS inside that contrast, not candidate architectures."),
        "paired_subset_geomean_knob": {
            "knob": knobs["R3S2_PAIRED_SUBSET_GEOMEAN"],
            "cell_is_pairing_valid": bool(paired),
            "note": ("panel aggregation is round-3-side; this cell publishes its own "
                     "pairing validity so the analyzer can report the geomean over all "
                     "scored datasets AND over the pairing-valid subset.")},
        "adr_r3_0004": ("sharp__phase_field_crystal_2d is REPORT-ONLY (scored cell "
                        "task-void); its thresholds are void for claim purposes. It is "
                        "not in this card's dataset list."),
    })

    dp = diag_base(knobs)
    dp.mkdir(parents=True, exist_ok=True)
    (dp / f"diag_{name}_e{args.epochs}_s{args.seed}.json").write_text(
        json.dumps(_json_safe(diag), indent=2, sort_keys=True))

    persist("done")

    pred = preds[scored_tag]
    n_params = int(fronts["ic_synth"]["n_params"] + dc_ext["reg"]["n_params"])
    latency = (1000.0 * eval_seconds / max(Nte, 1)) if device.type == "cuda" else None
    peak_mem = (torch.cuda.max_memory_allocated() / 1e6) if device.type == "cuda" else None
    print(f"[result] {name} scored_arm={scored_tag} nRMSE={a[scored_tag]:.6f} | "
          + " ".join(f"{k}={v:.6f}" for k, v in a.items())
          + f" | wall={time.time()-t0:.1f}s", flush=True)
    return finalize_and_write(
        out_path=out_path, model=MODEL_NAME, dataset=name,
        pred=pred, target=Y_te, work_grid=grid, n_params=n_params,
        train_seconds=train_seconds, eval_seconds=eval_seconds,
        latency_ms_per_sample=latency, peak_mem_mb=peak_mem, seed=args.seed,
        extra=_json_safe({
            "scored_arm": scored_tag,
            "arm_nrmse": a,
            "attribution": attribution,
            "ifc_loo_selector": selector_rec,
            "n_train_route": n_train_route,
            "lsi_repair": lsi_repair,
            "band_err_energy_by_arm": band_cols,
            "T_band_mean_abs": T_band_reg,
            "T_band_mean_abs_unregularised_A5": T_band_unreg,
            "map_smoothness": sidecars.get("S7_map_smoothness"),
            "paired_real_lf": paired,
            "ic_synth_applicable": ic_applicable,
            "ic_synthesis": ic_record,
            "floor_arms": floors,
            "floor_comparison_scored_arm": diag["floor_comparison_scored_arm"],
            "floor_comparison_by_arm": diag["floor_comparison_by_arm"],
            "lf_rung": int(lf_rung), "lf_grid": list(lf_grid),
            "hf_grid": list(hf_grid), "work_grid": list(grid),
            "upsample_convention": up_fn_name,
            "padding_mode": padding_mode,
            "padding_decision_reason": pad["padding_decision_reason"],
            "wrap_ratio_hf": pad["wrap_ratio_hf"],
            "alpha_lsi": dc_ext["reg"]["alpha_lsi"], "alpha_nn": dc_ext["reg"]["alpha_nn"],
            "validity_gates": gates,
            "probes": probes,
            "budget": budget, "split_protocol": split_rec,
            "dataset_content_sha256": data_sha,
            "mf_mechanism": ("a ROUTE SWITCH on one shared FiLM-FNO trunk: "
                             "condition -> pseudo-LF -> corrected upsampling -> frozen "
                             "REGULARISED LSI + local defect corrector -> HF, against a "
                             "budget-matched direct condition -> HF head, crossed with an "
                             "analytic-IC vs FiLM-only front end, with a zero-GPU "
                             "closed-form LOO selector as the ifc headline"),
            "base_family": ("r3s2_stack_ic@d5069a74 (itself r2s2_stack@6b4e1d48, itself "
                            "s4_router@b90d4662)"),
            "r3s2_env": knobs, "r3s2_diag": diag,
            "nrmse_def_hash": NRMSE_DEF_HASH,
            "panel_data_note": ("upsamplers VENDORED into upsample.py; eval/panel_data.py "
                                "is never imported and never touched"),
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
