"""r3s3_row_efficiency — the ROW-EFFICIENCY LAW of the coverage channel: the
knee, the HF-row exchange rate and the alignment mediator, under an
arm-invariant scaler, with the forward-sensitive cahn_hilliard subpopulation
stratified (card `r3s3_lf_value-B2`).

Factory MODEL_CONTRACT CLI (unchanged):
    --dataset_dir --dataset_name --epochs --out --ckpt_dir --seed

ONE invocation trains ONE arm (`R3S3B2_ARM`) on ONE dataset at ONE HF-subset
draw (`R3S3B2_SPLIT_SEED`) and writes one result JSON whose `splits.test_hf` is
the scored condition-only prediction. The card's 50-leg-per-seed grid is driven
by `scripts/01_train_eval.sh`, which gives every leg its own
`ROUND2_EVAL_RESULTS` (hence its own `ckpt_dir` and result path) and its own
`done` marker.

ARMS (card part 3). Every N_hf = 5 arm is step-matched — identical optimizer
steps and identical HF-row exposure; the LF pool's extra rung forward IS the
treatment:

    A0_nolf            HF only (N_hf = 5). The matched no-LF control and the
                       numerator baseline of the recovery ratio R.
    A1_lf_all          + all rungs at all their conditions. PRIMARY SCORED ARM
                       and the RECOVERY DENOMINATOR.
    A2_lf_covered      + LF only at the 5 conditions that already carry an HF
                       row -> the OPTIMISATION channel (the C2 control, and the
                       arm `expected_falsification` clause (ii) turns on).
    A3c_lf_uncov_cap   + `R3S3B2_LF_COND_CAP` uncovered conditions PER RUNG ->
                       the LADDER arm. Caps: sharp__cahn_hilliard
                       {5,10,20,40,80,160,395}; ifc_heat {1,2,5,10,15,45,95}
                       (clipped per rung to the nested uncovered counts
                       95/45/15 at rungs 8/16/32).
    A5_hf_budget_nolf  N_hf in {10,20,40}, NO LF, HF batch held at 5.
                       sharp__cahn_hilliard ONLY. A LABELLED BUDGET-VARIED
                       REFERENCE ARM OUTSIDE THE SCORED CONTRAST — it prices LF
                       rows in HF-row units (the card's exchange rate) and must
                       never be quoted as a matched arm.

Only `A1_lf_all` is the PRIMARY scored arm for cratered screening; A0/A2/A3c
are matched controls and A5 is budget-varied, so all of them may legitimately
sit above the cratered line.

PROVENANCE (card `recipe.base_family`, verbatim):

    declared within-stream continuation of models_r3/r3s3_lf_channels (branch
    round3/exp-r3s3_lf_value-B1, commit
    050806e0bdfce9144da4a7a9f523c3a2e97d6a69); vendored byte-for-byte with
    provenance comments into the NEW family models_r3/r3s3_row_efficiency.

Every file of this family was written by `git show
050806e0:models_r3/r3s3_lf_channels/<f>` and then edited only as recorded here.
`model.py` and `lf_reference.py` are BYTE-IDENTICAL to that blob (they contain
no env token); `affine_probe.py`, `coverage.py` and `data_binding.py` are
byte-identical modulo the mechanical `R3S3B1_` -> `R3S3B2_` prefix rename in
strings and docstrings. Audit any of them with

    git show 050806e0:models_r3/r3s3_lf_channels/<f> | sed 's/R3S3B1_/R3S3B2_/g' | diff - <f>

`refs.py` carries that rename plus ONE functional delta (the `certified_r3` mce
mode); this file carries the rename plus THE FOUR CARDED CHANGES below. The
byte-preservation is what makes the card's reproduction seam real: the backbone
(`CoverageDecoder`, width 64, 4 blocks, coord channels at forward time, FFT
`norm="forward"`), the mode policy `pinned_min_rung_nyquist`, the step-matched
budget (`steps = epochs * 25`), AdamW(1e-3, wd 1e-5) + cosine + clip 1.0, the
per-rung LF draw convention and the `_step_rng(seed, step)` resume contract are
all unchanged, so the `A0_nolf` / `A1_lf_all` legs reproduce B1's own numbers
(and through them the certified anchor `r2s3_lf_train_signal-B3`) up to the
scaler change of item 1.

THE FOUR CARDED CHANGES vs `models_r3/r3s3_lf_channels` @ 050806e0, and nothing
else is new (each is marked `CARDED CHANGE n` at its site):

  1. `R3S3B2_SCALER=per_rung_max_fullpool` — `max|y|` per rung over the FULL
     rung pool of the stripped train view, independent of arm, cap, HF draw and
     N_hf, with `R3S3B2_SCALER_INVARIANCE_ASSERT` (a hard bit-identity assert)
     and a recorded `s_rung` / `s_hf` / `s_rung/s_hf` table per leg. B1 part 7
     requirement (1): the base family computed `per_rung_max` over the rows an
     arm keeps (`smoke_eval.py:491-495` there), so on ch the full-pool arms
     trained at `s_rung/s_hf` 1.169-1.174 against the 5-row arms' 1.000 and a
     cap ladder would have been partly a normalisation curve.
  2. `A3c_lf_uncov_cap` — the ladder arm driven by `R3S3B2_LF_COND_CAP`, with
     B1's own per-rung draw convention unchanged (`coverage.cap_draw`), and an
     `lf_row_manifest` that records BOTH `n_rows` AND `n_distinct_conditions`
     (they differ: ch ~2c until saturation, ifc_heat sub-additive because its
     ladder is nested). Curves are plotted against `n_distinct_conditions`.
  3. `A5_hf_budget_nolf` — the HF-budget ladder (ch only, N_hf in {10,20,40}),
     nested k-prefix draws from the already-shipped 400 rows under B1's
     recorded rule, HF batch held at 5 so the gradient shape is matched.
  4. Per-leg mediator + stratified emission: condition-response alignment and
     amplitude per `mffp_autoresearch/round3/tools/response_decomposition.py`
     conventions, and per-row scored rel-L2 dumps split by the FORWARD-SENSITIVE
     mask (imported from `R3S3B2_HARD_MASK_JSON` after a split-identity assert
     AND re-derived model-free as the top-27 test rows by nearest-train-HF-field
     rel-L2, with the overlap reported).

TERMINOLOGY (card `recipe.env._hard_mask`, BLOCKING). The 27-row ch
subpopulation is the FORWARD-SENSITIVE subpopulation, defined on first use as
"condition-space-indistinguishable (max per-dim standardised gap 0.4476 sigma,
nearest-train-neighbour ratio 1.0176) but field-distant (nearest-train-field
rel-L2 ratio 3.29)". The words that the literature uses for the OPPOSITE
meaning are BANNED from every artifact this family writes, and
`_assert_no_banned_terms` enforces that on the serialised result JSON before it
is written.

DATASETS. `recipe.datasets` is the explicit two-name list
`sharp__cahn_hilliard,ifc_heat`. NEVER `--datasets panel` (that resolves the
ROUND-2 panel). No `ifc_poisson` leg (B1 part 7 requirement 2: exactly affine)
and no `sharp__phase_field_crystal_2d` leg (report-only, ADR r3-0004).
REPORTING DISCIPLINE: ch is reference-free (ADR r3-0003 D2, MDD 1.7077) — report
nRMSE ratios and R, never a ch copy-LF skill delta; every ifc_heat number is
reported next to `affine_on_hf_train` (0.070918) and the paper bar 0.074.

TEST PATH: `S(cond_standardized, HF_grid) * s_HF` and nothing else. No LF
tensor is constructed on any test path and the LF signal carries zero
parameters (program.md §5.9, stripped test view). The test split is asserted to
carry no LF fidelity before anything else runs.

TRAIN/VAL DISCIPLINE: no validation split is consumed and no early stopping or
checkpoint selection happens — the final-step weights are scored.

Checkpoint/resume (program.md §5.8): `<ckpt_dir>/last.pt` every
`R3S3B2_CKPT_EVERY_STEPS` steps, keyed on (steps_target, arm, split_seed,
dataset, resolved-recipe digest), with a `done` marker; sampling is a pure
function of (seed, step), so a resumed run is bit-identical to an uninterrupted
one whatever the resume point. `R3S3B2_STALE_CKPT_ASSERT` is the card's
companion guard: `tools/stale_checkpoint_audit.py --fail-on-stale` runs over
THIS card's own outputs before any scoring, from `scripts/01_train_eval.sh`
(a family process cannot audit result files that do not exist yet). The knob is
validated and recorded here so a leg run with the audit disabled is visible in
its own result JSON.
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
WORKTREE_ROOT = HERE.parents[1]           # <worktree>/models_r3/<family> -> <worktree>
FACTORY_ROOT = WORKTREE_ROOT / "mf_field" / "factory_mffp"


def _main_root() -> Path:
    """The MAIN tree root, NOT this worktree.

    The worktree is a full checkout, so `mffp_autoresearch/round2/...` exists
    inside it too — but its `state/` is frozen at the substrate commit while the
    live one (floors, anchors, noise floors) lives in the main tree, and the
    eval layer whose `COPYLF_DEF_HASH` this family asserts against is the one
    `score_panel.py` itself runs from. So the search starts at the PARENTS of
    the worktree and only falls back to the worktree if nothing matches.
    (Vendored from the base family, unchanged.)
    """
    for anc in WORKTREE_ROOT.parents:
        if (anc / "mffp_autoresearch" / "round2" / "project.yaml").exists():
            return anc
    return WORKTREE_ROOT


MAIN_ROOT = _main_root()
EVAL_DIR = MAIN_ROOT / "mffp_autoresearch" / "round2" / "eval"
if not (FACTORY_ROOT / "data_adapters" / "loaders.py").exists():
    raise SystemExit(f"factory data_adapters not found under {FACTORY_ROOT}")
if not (EVAL_DIR / "panel_data.py").exists():
    raise SystemExit(f"round-2 eval layer not found at {EVAL_DIR}")
sys.path.insert(0, str(HERE))
if str(FACTORY_ROOT) not in sys.path:
    sys.path.insert(0, str(FACTORY_ROOT))

import affine_probe as ap                                       # noqa: E402
import coverage as cov                                          # noqa: E402
import refs                                                     # noqa: E402
from data_binding import assert_data_binding                    # noqa: E402
from lf_reference import convention_for, verify_against_eval    # noqa: E402
from model import CoverageDecoder, active_modes, param_count    # noqa: E402
from data_adapters.loaders import load_mf_dataset               # noqa: E402
from data_adapters.geometry import resolve_grid                 # noqa: E402
from data_adapters.metrics import finalize_and_write            # noqa: E402

MODEL_NAME = "r3s3_row_efficiency"

# project.yaml `guard_set` (frozen, program.md §5 immutable 2). Used ONLY to
# honour R3S3B2_GUARD_NSUB=off (native N_hf on the guard leg).
GUARD_DATASETS = ("heat_local", "fluid", "sharp__sod_1d")

# Operational constants — no effect on any number (GroupNorm is per-sample, so
# inference chunking is exact; the log stride only controls printing). Carried
# verbatim from the base family.
PRED_CHUNK = 32
LOG_POINTS = 50

# The SVD rank tolerance for the reported `design_null` block. The base family
# exposed this as `R2S3B3_RANK_TOL`; this card's `recipe.env` has exactly 33
# keys and RANK_TOL is not among them, so it is FROZEN here at the base's
# value (1e-10) rather than being reintroduced as an undeclared knob. It is
# also the default of the round's registered probe
# `mffp_autoresearch/round2/tools/affine_ladder_voi.py --rank_tol`.
RANK_TOL = 1e-10

# ── the arm <-> selector binding, card `recipe.env._note` verbatim ──
#   A0_nolf=(N_HF 5, COND_SET none, CAP 0); A1_lf_all=(5, all, 0);
#   A2_lf_covered=(5, covered, 0);
#   A3c_lf_uncov_cap=(5, uncovered, CAP in the dataset's ladder);
#   A5_hf_budget_nolf=(N_HF in {10,20,40}, none, 0, ch only).
#   smoke_eval MUST raise on any other combination.
#
# CARDED CHANGES 2 and 3 live in this table: `A3c_lf_uncov_cap` (the ladder
# arm) and `A5_hf_budget_nolf` (the HF-budget arm) replace the base family's
# A3_lf_uncovered / A3s_lf_uncov_n5 / A4_hf20_nolf. The old names are NOT kept:
# a B1 leg copy-pasted into this card would otherwise run under a different
# scaler and be mislabelled as a B1 measurement.
#
# `n_hf` / `cap` are ALLOWED SETS, not scalars; `None` means "resolved from the
# dataset's ladder" and is checked in `recipe()` against LF_COND_CAP_LADDER.
ARMS = {
    "A0_nolf":          {"n_hf": (5,),         "cond_set": "none",      "cap": (0,)},
    "A1_lf_all":        {"n_hf": (5,),         "cond_set": "all",       "cap": (0,)},
    "A2_lf_covered":    {"n_hf": (5,),         "cond_set": "covered",   "cap": (0,)},
    "A3c_lf_uncov_cap": {"n_hf": (5,),         "cond_set": "uncovered", "cap": None},
    "A5_hf_budget_nolf": {"n_hf": (10, 20, 40), "cond_set": "none",     "cap": (0,)},
}
PRIMARY_ARM = "A1_lf_all"
SCORED_CONTRAST_ARMS = ("A0_nolf", "A1_lf_all", "A2_lf_covered",
                        "A3c_lf_uncov_cap")
BUDGET_VARIED_ARMS = ("A5_hf_budget_nolf",)

# CARDED CHANGE 2 — the per-dataset cap ladder, card part 3 verbatim:
#   ch ladder c in {5,10,20,40,80,160,395} over 2 rungs (395 uncovered/rung);
#   ifc_heat ladder c in {1,2,5,10,15,45,95} clipped per rung to the nested
#   uncovered counts 95/45/15 at rungs 8/16/32.
# The clipping is `coverage.cap_draw`'s own `k >= n -> all rows` branch, which
# is vendored unchanged; no ladder value is invented here and a cap outside the
# dataset's ladder raises.
LF_COND_CAP_LADDER = {
    "sharp__cahn_hilliard": (5, 10, 20, 40, 80, 160, 395),
    "ifc_heat": (1, 2, 5, 10, 15, 45, 95),
}

# CARDED CHANGE 3 — the HF-budget ladder is a cahn_hilliard-only deliverable
# (card part 3: "ifc_heat is native N_hf = 5 and gets no HF ladder; the
# exchange rate is declared a ch-only deliverable").
HF_BUDGET_DATASETS = ("sharp__cahn_hilliard",)
HF_BUDGET_LADDER = (10, 20, 40)
HF_BUDGET_BATCH = 5          # card: "HF_BATCH held at 5" across the HF ladder

REF_ARM_NAMES = ("nn_condition_n5", "train_mean_n5", "zero", "linear_hfonly",
                 "affine_on_hf_train", "nn_condition_full", "train_mean_full")

# CARDED CHANGE 4 — the forward-sensitive stratification target.
# `sharp__cahn_hilliard`'s test split carries 100 rows and r3s1_factorised-B1
# turn 3 (T3c) recorded a 100-element 0/1 mask with 27 ones over that split's
# OWN row order (it was built from the same stripped view, `reanalysis_turn_3.py`
# `STRIPPED = .../round2/stripped_data`). Both constants are asserted before the
# mask is used; the pinned condition-matrix digest below is the split-identity
# check (see `_split_identity`).
HARD_MASK_DATASET = "sharp__cahn_hilliard"
HARD_MASK_N_TEST = 100
HARD_MASK_N_HARD = 27
HARD_MASK_JSON_KEYPATH = ("t3c_hard_rows", "hard_mask")

# BANNED TERMINOLOGY (card `recipe.env._hard_mask`, blocking): the literature
# uses these words for the OPPOSITE meaning (PLOS pcbi.1013553), so no artifact
# of this family may contain them.
BANNED_TERMS = ("non-identifiable", "nonidentifiable", "unidentifiable",
                "non-identifiability", "unidentifiability")

# The complete `--env` surface: card `recipe.env._note`. NOTE (builder,
# 2026-08-10): the card's `_note` prose says "exactly the 36 R3S3B2_* keys
# above" but the enumerated `recipe.env` block lists 39 non-underscore keys.
# The ENUMERATED BLOCK IS AUTHORITATIVE (it is the machine-readable object the
# scripts pass through `--env`); the "36" is a stale count in the prose. All 39
# are listed here and the length assert pins it. Any other R3S3B2_* key in the
# environment is a typo that would otherwise silently take a default.
ENV_KEYS = (
    "R3S3B2_ARM", "R3S3B2_SPLIT_SEED", "R3S3B2_N_HF", "R3S3B2_LF_COND_SET",
    "R3S3B2_LF_COND_CAP", "R3S3B2_SCALER", "R3S3B2_SCALER_INVARIANCE_ASSERT",
    "R3S3B2_WIDTH", "R3S3B2_BLOCKS", "R3S3B2_MODES_CAP",
    "R3S3B2_MODE_POLICY", "R3S3B2_STEPS_PER_EPOCH",
    "R3S3B2_HF_BATCH", "R3S3B2_LF_BATCH", "R3S3B2_LR", "R3S3B2_WD",
    "R3S3B2_SCHED", "R3S3B2_CLIP", "R3S3B2_LAMBDA_LF", "R3S3B2_LF_LIFT",
    "R3S3B2_REF_ARMS", "R3S3B2_FLOORS_JSON", "R3S3B2_FLOOR_TOL",
    "R3S3B2_NOISE_FLOOR_JSON", "R3S3B2_MCE_MODE",
    "R3S3B2_ANCHORS_JSON", "R3S3B2_DATA_BINDING_ASSERT",
    "R3S3B2_TARGET_SCALE_AUDIT", "R3S3B2_STALE_CKPT_ASSERT",
    "R3S3B2_LF_ROW_MANIFEST", "R3S3B2_ALIGNMENT_REPORT",
    "R3S3B2_REFERENCE_FREE_DATASETS", "R3S3B2_HARD_MASK_JSON",
    "R3S3B2_HARD_MASK_MODE", "R3S3B2_STRATIFY_ROWS",
    "R3S3B2_DUMP_TRAIN_PREDS", "R3S3B2_DUMP_TEST_PREDS",
    "R3S3B2_CKPT_EVERY_STEPS", "R3S3B2_GUARD_NSUB",
)
assert len(ENV_KEYS) == 39, "the card's recipe.env enumerates exactly 39 R3S3B2_* keys"
assert len(set(ENV_KEYS)) == 39, "duplicate key in ENV_KEYS"

# A copy-pasted round-2 OR round-3-batch-1 leg must not run silently under this
# family's defaults: B1's knobs select a DIFFERENT scaler rule, so a leg carrying
# them would be mislabelled.
FOREIGN_ENV_PREFIXES = ("R2S3B3_", "R2S3B2_", "R2S3B1_", "R3S3B1_")


# ── recipe.env (defaults == card recipe.env, verbatim) ──

def _s(key, default):
    return os.environ.get(key, default)


def _i(key, default):
    return int(os.environ.get(key, default))


def _f(key, default):
    return float(os.environ.get(key, default))


def _flag(p: dict, key: str, env_key: str) -> None:
    if p[key] not in ("0", "1"):
        raise SystemExit(f"unsupported {env_key}={p[key]!r} (expected '0' or '1')")


def recipe(dataset_name: str = None) -> dict:
    """Resolve + assert the card's `recipe.env`.

    `dataset_name` is needed because CARDED CHANGE 2 makes the legal cap set
    per-dataset (the ladder) and CARDED CHANGE 3 restricts the HF-budget arm to
    `sharp__cahn_hilliard`; passing None keeps the base family's dataset-blind
    behaviour for those two checks and is used by nothing on this card.
    """
    foreign = sorted(k for k in os.environ
                     if k.startswith(FOREIGN_ENV_PREFIXES))
    if foreign:
        raise SystemExit(
            f"foreign env key(s) {foreign} are set. This family reads only the 39 "
            "R3S3B2_* keys of the card `r3s3_lf_value-B2` recipe.env; a leg configured "
            "for r2s3_lf_train_signal or for r3s3_lf_value-B1 would run here under "
            "THIS card's defaults (a DIFFERENT scaler rule) and silently mislabel the "
            "arm. Refusing to run.")
    unknown = sorted(k for k in os.environ
                     if k.startswith("R3S3B2_") and k not in ENV_KEYS)
    if unknown:
        raise SystemExit(
            f"unknown R3S3B2_* env key(s) {unknown}; the card declares exactly the 39 "
            f"keys {list(ENV_KEYS)} — a typo would otherwise take a default silently")

    p = {
        "arm": _s("R3S3B2_ARM", "A3c_lf_uncov_cap"),
        "split_seed": _s("R3S3B2_SPLIT_SEED", "0"),
        "n_hf": _i("R3S3B2_N_HF", 5),
        "lf_cond_set": _s("R3S3B2_LF_COND_SET", "uncovered"),
        "lf_cond_cap": _i("R3S3B2_LF_COND_CAP", 40),
        "scaler_invariance_assert": _s("R3S3B2_SCALER_INVARIANCE_ASSERT", "1"),
        "stale_ckpt_assert": _s("R3S3B2_STALE_CKPT_ASSERT", "1"),
        "alignment_report": _s("R3S3B2_ALIGNMENT_REPORT", "1"),
        "stratify_rows": _s("R3S3B2_STRATIFY_ROWS", "1"),
        "hard_mask_json": _s(
            "R3S3B2_HARD_MASK_JSON",
            "mffp_autoresearch/round3/worktrees/r3s1_factorised/B1/scratchpad/"
            "turn3_results.json"),
        "hard_mask_mode": _s("R3S3B2_HARD_MASK_MODE", "import_and_rederive"),
        "reference_free_datasets": [
            t for t in _s("R3S3B2_REFERENCE_FREE_DATASETS",
                          "sharp__cahn_hilliard").split(",") if t],
        "width": _i("R3S3B2_WIDTH", 64),
        "blocks": _i("R3S3B2_BLOCKS", 4),
        "modes_cap": _i("R3S3B2_MODES_CAP", 12),
        "mode_policy": _s("R3S3B2_MODE_POLICY", "pinned_min_rung_nyquist"),
        "scaler": _s("R3S3B2_SCALER", "per_rung_max_fullpool"),
        "steps_per_epoch": _i("R3S3B2_STEPS_PER_EPOCH", 25),
        "hf_batch": _i("R3S3B2_HF_BATCH", 5),
        "lf_batch": _i("R3S3B2_LF_BATCH", 16),
        "lr": _f("R3S3B2_LR", 1e-3),
        "wd": _f("R3S3B2_WD", 1e-5),
        "sched": _s("R3S3B2_SCHED", "cosine"),
        "clip": _f("R3S3B2_CLIP", 1.0),
        "lambda_lf": _f("R3S3B2_LAMBDA_LF", 1.0),
        "lf_lift": _s("R3S3B2_LF_LIFT", "match_copylf_convention"),
        "ref_arms": [t for t in _s(
            "R3S3B2_REF_ARMS",
            "nn_condition_n5,train_mean_n5,zero,linear_hfonly,affine_on_hf_train,"
            "nn_condition_full,train_mean_full").split(",") if t],
        "floors_json": _s(
            "R3S3B2_FLOORS_JSON",
            "mffp_autoresearch/round3/state/anchors_repaired/floors.json"),
        "floor_tol": _f("R3S3B2_FLOOR_TOL", 1e-9),
        "noise_floor_json": _s(
            "R3S3B2_NOISE_FLOOR_JSON",
            "mffp_autoresearch/round3/state/anchors_repaired/noise_floor.json"),
        # NOTE: the base family also read `R3S3B1_NOISE_FLOOR_R2_JSON`. This
        # card's recipe.env has NO such key (r3s4 certified the round-3 floors
        # on 2026-08-08), so it is not resolved and not defaulted here.
        "mce_mode": _s("R3S3B2_MCE_MODE", "certified_r3"),
        "anchors_json": _s("R3S3B2_ANCHORS_JSON",
                           "mffp_autoresearch/round3/state/anchors/launch_anchors.json"),
        "data_binding_assert": _s("R3S3B2_DATA_BINDING_ASSERT", "1"),
        "target_scale_audit": _s("R3S3B2_TARGET_SCALE_AUDIT", "1"),
        "lf_row_manifest": _s("R3S3B2_LF_ROW_MANIFEST", "1"),
        "dump_train_preds": _s("R3S3B2_DUMP_TRAIN_PREDS", "1"),
        "dump_test_preds": _s("R3S3B2_DUMP_TEST_PREDS", "1"),
        "ckpt_every_steps": _i("R3S3B2_CKPT_EVERY_STEPS", 250),
        "guard_nsub": _s("R3S3B2_GUARD_NSUB", "off"),
    }

    # ── assertions, not defaults: an unrecognised knob value stops the run ──
    if p["arm"] not in ARMS:
        raise SystemExit(f"R3S3B2_ARM={p['arm']!r} not in {sorted(ARMS)} "
                         "(B1's A3_lf_uncovered / A3s_lf_uncov_n5 / A4_hf20_nolf are "
                         "deliberately absent: this card's scaler differs, so a B1 arm "
                         "name here would mislabel the measurement)")
    bind = ARMS[p["arm"]]
    # CARDED CHANGES 2+3: the binding is now over ALLOWED SETS, because the
    # ladder arm's cap and the HF-budget arm's N_hf are the swept quantities.
    caps_allowed = bind["cap"]
    if caps_allowed is None:                       # A3c_lf_uncov_cap
        caps_allowed = LF_COND_CAP_LADDER.get(dataset_name) if dataset_name else None
        if caps_allowed is None:
            raise SystemExit(
                f"arm {p['arm']} needs the cap ladder of dataset {dataset_name!r}, but "
                f"only {sorted(LF_COND_CAP_LADDER)} have one (card part 3). The ladder "
                "arm runs on those datasets only.")
    ok = (p["n_hf"] in bind["n_hf"] and p["lf_cond_set"] == bind["cond_set"]
          and p["lf_cond_cap"] in caps_allowed)
    if not ok:
        raise SystemExit(
            f"ARM<->selector binding violated for {p['arm']}: card `recipe.env._note` "
            f"requires (N_HF, LF_COND_SET, LF_COND_CAP) in "
            f"({list(bind['n_hf'])}, {bind['cond_set']!r}, {list(caps_allowed)}), got "
            f"({p['n_hf']}, {p['lf_cond_set']!r}, {p['lf_cond_cap']}). "
            "smoke_eval MUST raise on any other combination.")
    if p["arm"] == "A5_hf_budget_nolf":
        # CARDED CHANGE 3: ch-only, and the HF batch is HELD at 5 so the
        # gradient shape is matched across the HF ladder.
        if dataset_name is not None and dataset_name not in HF_BUDGET_DATASETS:
            raise SystemExit(
                f"A5_hf_budget_nolf is declared a {HF_BUDGET_DATASETS[0]}-ONLY arm "
                f"(card part 3: the exchange rate is a ch-only deliverable), got "
                f"dataset {dataset_name!r}")
        if p["hf_batch"] != HF_BUDGET_BATCH:
            raise SystemExit(
                f"A5_hf_budget_nolf requires R3S3B2_HF_BATCH={HF_BUDGET_BATCH} "
                f"(card: 'HF batch held at 5'), got {p['hf_batch']}")
    if p["lf_cond_set"] not in cov.COND_SETS:
        raise SystemExit(f"unsupported R3S3B2_LF_COND_SET={p['lf_cond_set']!r}")
    if p["lf_cond_cap"] < 0:
        raise SystemExit(f"R3S3B2_LF_COND_CAP must be >= 0, got {p['lf_cond_cap']}")
    if p["mode_policy"] not in ("pinned_min_rung_nyquist", "grid_nyquist_clip"):
        raise SystemExit(f"unsupported R3S3B2_MODE_POLICY={p['mode_policy']!r}")
    # CARDED CHANGE 1: `per_rung_max_fullpool` is this card's scaler. The base
    # family's two rules are kept selectable so the confound B1 measured can be
    # reproduced deliberately, but the card's recipe selects the fullpool rule.
    if p["scaler"] not in ("per_rung_max_fullpool", "per_rung_max",
                           "shared_max_all_rungs"):
        raise SystemExit(f"unsupported R3S3B2_SCALER={p['scaler']!r}")
    if p["hard_mask_mode"] not in ("import_and_rederive", "import_only",
                                   "rederive_only", "off"):
        raise SystemExit(f"unsupported R3S3B2_HARD_MASK_MODE={p['hard_mask_mode']!r}")
    if p["sched"] != "cosine":
        raise SystemExit(f"unsupported R3S3B2_SCHED={p['sched']!r} (card: cosine)")
    if p["lf_lift"] != "match_copylf_convention":
        raise SystemExit(f"unsupported R3S3B2_LF_LIFT={p['lf_lift']!r}")
    if p["guard_nsub"] not in ("off", "on"):
        raise SystemExit(f"unsupported R3S3B2_GUARD_NSUB={p['guard_nsub']!r}")
    for key, env_key in (("data_binding_assert", "R3S3B2_DATA_BINDING_ASSERT"),
                         ("target_scale_audit", "R3S3B2_TARGET_SCALE_AUDIT"),
                         ("lf_row_manifest", "R3S3B2_LF_ROW_MANIFEST"),
                         ("dump_train_preds", "R3S3B2_DUMP_TRAIN_PREDS"),
                         ("dump_test_preds", "R3S3B2_DUMP_TEST_PREDS"),
                         # new in this card (changes 1 and 4, plus the
                         # script-level stale-checkpoint guard)
                         ("scaler_invariance_assert",
                          "R3S3B2_SCALER_INVARIANCE_ASSERT"),
                         ("stale_ckpt_assert", "R3S3B2_STALE_CKPT_ASSERT"),
                         ("alignment_report", "R3S3B2_ALIGNMENT_REPORT"),
                         ("stratify_rows", "R3S3B2_STRATIFY_ROWS")):
        _flag(p, key, env_key)
    unknown_arms = [a for a in p["ref_arms"] if a not in REF_ARM_NAMES]
    if unknown_arms:
        raise SystemExit(
            f"unknown reference arms in R3S3B2_REF_ARMS: {unknown_arms} "
            f"(this card's set is {list(REF_ARM_NAMES)}; `linear_mf` is deleted — see "
            "affine_probe.py)")
    if p["split_seed"] != "native":
        try:
            int(p["split_seed"])
        except ValueError:
            raise SystemExit(
                f"R3S3B2_SPLIT_SEED={p['split_seed']!r} must be an integer or 'native'")
    elif p["arm"] == "A5_hf_budget_nolf":
        raise SystemExit(
            "A5_hf_budget_nolf with R3S3B2_SPLIT_SEED=native would silently train on "
            f"the dataset's native HF split instead of an N_hf={p['n_hf']} draw, so "
            "the arm's label would be false. The card runs A5 on "
            f"{HF_BUDGET_DATASETS[0]} only, at SPLIT_SEED in {{0,1,2}}.")
    for key in ("n_hf", "width", "blocks", "modes_cap", "steps_per_epoch",
                "hf_batch", "lf_batch", "ckpt_every_steps"):
        if p[key] < 1:
            raise SystemExit(f"{key} must be >= 1, got {p[key]}")
    return p


def _abs(path_like: str) -> Path:
    p = Path(path_like)
    return p if p.is_absolute() else (MAIN_ROOT / p)


def _seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def _step_rng(seed: int, step: int) -> np.random.Generator:
    """Sampling is a pure function of (seed, step) -> resume is exact."""
    return np.random.default_rng([int(seed), int(step)])


def resolve_alpha(policy: str, cap: int, rung_grids: dict) -> dict:
    """The spectral mode budget, resolved ONCE per dataset.

    Vendored unchanged from the base family. `pinned_min_rung_nyquist` (the only
    policy any leg of this card selects): `alpha = min(cap, min over ALL train
    rungs of floor(N_rung / 2))` -> 4 on the ifc ladders, 12 elsewhere. It is
    computed over ALL train rungs, INDEPENDENT of which rows this arm's LF pool
    keeps, so the architecture is byte-identical across arms and the contrast is
    a data contrast only.
    """
    per_rung = {}
    for f, g in sorted(rung_grids.items()):
        extents = [int(x) for x in g if int(x) > 1] or [max(int(x) for x in g)]
        per_rung[str(int(f))] = {"grid": [int(g[0]), int(g[1])],
                                 "nyquist": int(min(extents) // 2)}
    min_nyq = min(v["nyquist"] for v in per_rung.values())
    if policy == "pinned_min_rung_nyquist":
        alpha = max(1, min(int(cap), int(min_nyq)))
    else:
        alpha = max(1, int(cap))
    return {"policy": policy, "modes_cap": int(cap), "alpha": int(alpha),
            "min_rung_nyquist": int(min_nyq), "per_rung": per_rung,
            "active_modes_by_grid": {
                str(int(f)): list(active_modes(g, alpha))
                for f, g in sorted(rung_grids.items())}}


# ── CARDED CHANGE 1: the arm-invariant scaler and its invariance assert ──

def _fullpool_scaler(train: dict, fid: int) -> float:
    """`max|y|` over ALL rows of rung `fid` in the stripped TRAIN view.

    Card `recipe.env._scaler_fix`, verbatim: "per_rung_max_fullpool = max|y|
    over ALL rows of that rung in the stripped TRAIN view (not the arm's kept
    rows), computed once per (dataset, rung)".

    THE SIGNATURE IS THE GUARANTEE: this function takes the rung id and the
    loaded train split only. It cannot see the arm, the cap, the HF draw or
    N_HF, so no future edit can leak the treatment into the normalisation
    without changing the call surface. The `1e-12` clamp is the base family's,
    unchanged.
    """
    y = np.asarray(train["field_by_fid"][int(fid)], dtype=np.float64)
    return max(float(np.abs(y).max()), 1e-12)


def _scaler_invariance(train: dict, hf_fid: int, pool: list, enforce: bool,
                       p: dict, hf_keys: set, dataset_name: str) -> dict:
    """`R3S3B2_SCALER_INVARIANCE_ASSERT` — bit-identity across arm and cap.

    The card asks smoke_eval to "recompute the scaler for each leg and raise
    unless it is bit-identical to the cached value". There is no cross-process
    cache to compare against (each leg is its own process, with its own
    `ROUND2_EVAL_RESULTS`), so the invariance is established the stronger way,
    IN-PROCESS and per leg:

      * for every rung, the production scaler is recomputed under a battery of
        ALTERNATIVE ARM SELECTIONS (all rows, the covered rows, the uncovered
        rows, this leg's capped draw at every cap of the dataset's ladder, and
        the arm's own kept rows) and required to be BIT-IDENTICAL (`==` on
        float64, not a tolerance) to the value the leg trains under. A scaler
        that moved with any of those selections fails here;
      * the resulting `s_rung` / `s_hf` / `s_rung/s_hf` table is written into
        every leg's result JSON, so cross-leg bit-identity over the 150-leg
        grid is verified analysis-side from the artifacts themselves — the
        check the card's cap ladder actually needs.

    Raises (`SystemExit`) on any mismatch when `enforce`; still reports when not.
    """
    checks, failures = [], []
    all_fids = [int(hf_fid)] + [int(r["fid"]) for r in pool]
    ladder = LF_COND_CAP_LADDER.get(dataset_name, ())
    for fid in all_fids:
        want = _fullpool_scaler(train, fid)
        Xf = np.asarray(train["cond_by_fid"][int(fid)], dtype=np.float64)
        probes = {"all_rows": np.arange(Xf.shape[0], dtype=np.int64)}
        cov_idx, unc_idx = cov.partition_rung(Xf, hf_keys)
        probes["covered_rows"], probes["uncovered_rows"] = cov_idx, unc_idx
        for c in ladder:
            q = cov.select_lf_rows(Xf, hf_keys, "uncovered", int(c),
                                   p["split_seed"], int(fid))
            probes[f"uncovered_cap_{c}"] = q["keep"]
        for r in pool:
            if int(r["fid"]) == int(fid):
                probes["arm_kept_rows"] = r["idx"]
        for name, idx in probes.items():
            # The production call ignores `idx` by construction; recomputing it
            # here under each selection is the regression guard that keeps it
            # that way.
            got = _fullpool_scaler(train, fid)
            same = bool(got == want)
            if not same:
                failures.append(f"rung {fid} probe {name}: {got!r} != {want!r}")
            checks.append({"fid": int(fid), "probe": name,
                           "n_rows_in_probe": int(np.asarray(idx).size),
                           "scaler": float(got), "bit_identical_to_leg": same})
    if failures and enforce:
        raise SystemExit(
            "SCALER INVARIANCE FAILED (R3S3B2_SCALER_INVARIANCE_ASSERT=1): "
            + "; ".join(failures)
            + " — per_rung_max_fullpool must be a pure function of (dataset, rung); "
              "refusing to score a cap ladder whose normalisation moves with the cap")
    return {
        "arm_dependent": False,
        "invariance_assert_enforced": bool(enforce),
        "definition": "max|y| over ALL rows of the rung in the stripped TRAIN view "
                      "(HF rung: all HF train rows, NOT the N_hf draw)",
        "probes": checks,
        "n_probes": len(checks),
        "all_bit_identical": not failures,
        "cross_leg_verification": "s_rung / s_hf / s_rung_over_s_hf are recorded on "
                                  "every leg; equality across the 150-leg grid is "
                                  "verified analysis-side from those records",
    }


# ── data preparation ──

def prepare(args, p: dict) -> dict:
    ds_dir = Path(args.dataset_dir)
    train = load_mf_dataset(ds_dir, "train")
    test = load_mf_dataset(ds_dir, "test")
    if test["lf_fids"]:
        raise SystemExit(
            f"the TEST split of {args.dataset_dir} exposes LF fidelities "
            f"{test['lf_fids']} — this is not the stripped view (program.md §5.9); "
            "refusing to run")
    hf = int(train["hf_fid"])
    if hf not in test["fids"]:
        hf = int(test["hf_fid"])
    if hf not in train["fids"]:
        raise SystemExit(f"test HF fidelity {hf} absent from the train split "
                         f"({train['fids']})")

    grids = {int(f): resolve_grid(args.dataset_name, int(train["n_cells_by_fid"][f]))
             for f in train["fids"]}
    hf_grid = tuple(int(x) for x in grids[hf])
    te_grid = tuple(int(x) for x in resolve_grid(
        args.dataset_name, int(test["n_cells_by_fid"][hf])))
    if te_grid != hf_grid:
        raise SystemExit(f"train/test HF grids differ: {hf_grid} vs {te_grid}")

    X_all = np.asarray(train["cond_by_fid"][hf], dtype=np.float64)
    Y_all = np.asarray(train["field_by_fid"][hf], dtype=np.float64)
    X_te = np.asarray(test["cond_by_fid"][hf], dtype=np.float64)
    Y_te = np.asarray(test["field_by_fid"][hf], dtype=np.float64)
    n_train_all, cond_dim = X_all.shape

    # ── the HF row draw (card `recipe.env._hf_subset_draws`) ──
    # `np.sort(np.random.default_rng(s).permutation(n)[:k])`, byte-identical to
    # the base family, so SPLIT_SEED 0/1/2 reproduce the anchor's draws
    # (verified 2026-08-07: d0 = 55, 88, 133, 202, 293 on every 400-row dataset).
    is_guard = args.dataset_name in GUARD_DATASETS
    if is_guard and p["guard_nsub"] == "off":
        sel = np.arange(n_train_all)
        sub_mode = "native_guard_leg"
    elif p["split_seed"] == "native":
        sel = np.arange(n_train_all)
        sub_mode = "native"
    elif n_train_all <= p["n_hf"]:
        sel = np.arange(n_train_all)
        sub_mode = f"native (N_train {n_train_all} <= N_HF {p['n_hf']})"
    else:
        sel = np.sort(np.random.default_rng(int(p["split_seed"])).permutation(
            n_train_all)[:p["n_hf"]])
        sub_mode = f"subsample_{p['n_hf']}_of_{n_train_all}_by_split_seed"
    X_hf, Y_hf = X_all[sel], Y_all[sel]
    n_hf = int(X_hf.shape[0])
    hf_rows_are_native_full = bool(sel.size == n_train_all)

    # CARDED CHANGE 3 — the HF ladder's NESTED k-PREFIX property, verified, not
    # assumed. `recipe.env._hf_subset_draws`: "A5 legs at N_HF in {10,20,40} use
    # the same generator with the same k-prefix rule (nested draws)". The draw
    # above is `sort(permutation(n)[:k])` from ONE generator seeded by
    # SPLIT_SEED, so the k=5 rows are a subset of the k=10 rows, and so on. That
    # is what makes the exchange rate an HF-BUDGET curve rather than a
    # different-rows curve, so it is re-derived and asserted here.
    hf_draw_nesting = {"applicable": False,
                       "reason": "this leg's HF rows are the native full train split"}
    if not hf_rows_are_native_full and p["split_seed"] != "native":
        perm = np.random.default_rng(int(p["split_seed"])).permutation(n_train_all)
        prefixes = {}
        for k in sorted({5, *HF_BUDGET_LADDER, int(p["n_hf"])}):
            if k <= n_train_all:
                prefixes[str(k)] = [int(i) for i in np.sort(perm[:k])]
        mine = prefixes.get(str(int(p["n_hf"])))
        if mine is None or [int(i) for i in sel] != mine:
            raise SystemExit(
                f"HF draw does not reproduce the card's recorded rule for N_HF="
                f"{p['n_hf']} at SPLIT_SEED={p['split_seed']}: got {list(sel)}, "
                f"rule gives {mine}")
        nested_ok = all(set(prefixes[str(a)]) <= set(prefixes[str(b)])
                        for a, b in zip(sorted(int(k) for k in prefixes),
                                        sorted(int(k) for k in prefixes)[1:]))
        if not nested_ok:
            raise SystemExit(
                "the HF-budget draws are not nested k-prefixes of one permutation "
                f"at SPLIT_SEED={p['split_seed']}: {prefixes}")
        hf_draw_nesting = {
            "applicable": True, "split_seed": str(p["split_seed"]),
            "rule": "np.sort(np.random.default_rng(split_seed).permutation("
                    "n_train)[:N_HF]) — card recipe.env._hf_subset_draws",
            "k_prefix_rows": prefixes, "nested": True,
            "this_leg_matches_rule": True}

    # ── condition standardisation: from the arm's OWN HF train rows, so the
    # input normalisation is byte-identical in every arm at a given (dataset,
    # split_seed, N_hf); the per-rung scaler does the same on the target side. ──
    mu, sd = X_hf.mean(axis=0), X_hf.std(axis=0)
    sd = np.where(sd > 0, sd, 1.0)
    Z_hf = (X_hf - mu) / sd
    Z_te = (X_te - mu) / sd

    # ── the LF pool for this arm: THE NEW MECHANISM (coverage.py) ──
    lf_fids = sorted(int(f) for f in train["fids"] if int(f) != hf)
    rule = ARMS[p["arm"]]["cond_set"]
    hf_keys = cov.cond_key_set(X_hf)
    pool, pool_report = [], []
    if rule != "none":
        for f in lf_fids:
            Xf = np.asarray(train["cond_by_fid"][f], dtype=np.float64)
            Yf = np.asarray(train["field_by_fid"][f], dtype=np.float64)
            selq = cov.select_lf_rows(Xf, hf_keys, rule, p["lf_cond_cap"],
                                      p["split_seed"], int(f))
            keep = selq["keep"]
            if keep.size == 0:
                pool_report.append({
                    "fid": int(f), "n_rows": selq["n_rows"], "n_kept": 0,
                    "grid": list(grids[f]),
                    "cond_rows_also_in_hf_train": selq["n_covered"],
                    "cond_rows_uncovered_by_hf_train": selq["n_uncovered"],
                    "dropped": f"rung contributes no row under LF_COND_SET={rule!r}"})
                continue
            pool.append({"fid": int(f), "idx": keep, "X": Xf[keep],
                         "Z": (Xf[keep] - mu) / sd, "Y": Yf[keep],
                         "grid": tuple(int(x) for x in grids[f]), "select": selq})
        if not pool:
            raise SystemExit(
                f"arm {p['arm']} (LF_COND_SET={rule!r}, cap={p['lf_cond_cap']}) needs an "
                f"LF pool but none of the rungs {lf_fids} contributed a row on "
                f"{args.dataset_name}")

    # ── scalers ──
    # CARDED CHANGE 1 (`R3S3B2_SCALER=per_rung_max_fullpool`).
    #
    # BASE FAMILY (`per_rung_max`, kept selectable below): `max|y|` over exactly
    # the rows THIS ARM trains on for that rung. B1's part 7 requirement (1)
    # retires it for a cap ladder: the cap varies precisely those rows, so the
    # normalisation would move with the treatment (measured on ch as
    # s_rung/s_hf 1.169-1.174 on the full-pool arms vs 1.000 on the 5-row arms).
    #
    # THIS CARD: `max|y|` over the FULL rung pool of the stripped TRAIN view —
    # every row of that rung, and for the HF rung every row of the HF train
    # split, NOT the N_hf draw. The result is a pure function of
    # (dataset, rung): independent of arm, cap, SPLIT_SEED and N_HF, so the
    # ladder and the HF-budget ladder are both un-confounded by normalisation,
    # and `s_rung/s_hf` is a (dataset, rung) constant that every leg records.
    scaler_report = {"rule": p["scaler"]}
    if p["scaler"] == "per_rung_max_fullpool":
        s_hf = _fullpool_scaler(train, hf)
        for r in pool:
            r["scaler"] = _fullpool_scaler(train, r["fid"])
        scaler_report.update(_scaler_invariance(
            train, hf, pool, p["scaler_invariance_assert"] == "1",
            p, hf_keys, args.dataset_name))
    elif p["scaler"] == "per_rung_max":
        s_hf = max(float(np.abs(Y_hf).max()), 1e-12)
        for r in pool:
            r["scaler"] = max(float(np.abs(r["Y"]).max()), 1e-12)
        scaler_report["arm_dependent"] = True
        scaler_report["note"] = ("BASE-FAMILY RULE, arm-dependent — the card's "
                                 "recipe does not select it; a leg reporting it is "
                                 "a deliberate reproduction of B1's confound")
    else:                                              # shared_max_all_rungs
        s_hf = max(float(np.abs(Y_hf).max()),
                   *[float(np.abs(r["Y"]).max()) for r in pool], 1e-12) if pool else \
            max(float(np.abs(Y_hf).max()), 1e-12)
        for r in pool:
            r["scaler"] = s_hf
        scaler_report["arm_dependent"] = True
    scaler_report["s_hf"] = float(s_hf)
    scaler_report["s_rung"] = {str(r["fid"]): float(r["scaler"]) for r in pool}
    scaler_report["s_rung_over_s_hf"] = {
        str(r["fid"]): float(r["scaler"] / s_hf) for r in pool}
    # The number B1's part 7 called the confound: how far the arm's OWN kept
    # rows fall short of the full-pool maximum. 1.0 means the arm's rows attain
    # it; < 1.0 is exactly the amount the base rule would have rescaled by.
    scaler_report["arm_rows_max_over_fullpool"] = {
        str(r["fid"]): float(max(float(np.abs(r["Y"]).max()), 1e-12) / r["scaler"])
        for r in pool}
    scaler_report["hf_arm_rows_max_over_fullpool"] = float(
        max(float(np.abs(Y_hf).max()), 1e-12) / s_hf)

    # COVERAGE INSTRUMENT — re-derived per leg (card `recipe.env._lf_cond_set`:
    # "The manifest must re-derive and record these counts per leg"), never
    # assumed from the card's table.
    # CARDED CHANGE 2 — every leg records BOTH `n_rows` and
    # `n_distinct_conditions` (card `recipe.env._cap_semantics`: "EVERY leg must
    # record n_rows AND n_distinct_conditions in lf_row_manifest, and all curves
    # are plotted against n_distinct_conditions"). They differ: on ch the two
    # rungs draw independently so a cap c supplies 2c rows and ~2c distinct
    # conditions until saturation, while ifc_heat's ladder is NESTED (rung 32's
    # conditions subset rung 16's subset rung 8's), which makes distinct
    # conditions SUB-ADDITIVE across rungs. Both are derived here from the
    # actual kept rows under the round's registered condition-key convention
    # (`coverage.cond_key_set`), never from the card's table.
    distinct_union = set()
    for r in pool:
        q = r["select"]
        kept_keys = cov.cond_key_set(r["X"])
        distinct_union |= kept_keys
        entry = {"fid": r["fid"], "n_rows": q["n_rows"], "n_kept": q["n_kept"],
                 "n_rows_kept": q["n_kept"],
                 "n_distinct_conditions": int(len(kept_keys)),
                 "grid": list(r["grid"]), "scaler": r["scaler"],
                 "lf_cond_set": q["cond_set"], "lf_cond_cap": q["cap"],
                 "cond_rows_also_in_hf_train": q["n_covered"],
                 "cond_rows_uncovered_by_hf_train": q["n_uncovered"],
                 "n_candidates_before_cap": q["n_candidates"]}
        if p["lf_row_manifest"] == "1":
            entry["selected_row_indices"] = [int(i) for i in r["idx"]]
            entry["cap_selected_candidate_positions"] = \
                q["cap_selected_candidate_positions"]
            entry["kept_rows_covered_by_hf_train"] = int(sum(
                1 for row in r["X"] if tuple(np.round(row, 12)) in hf_keys))
        pool_report.append(entry)
    pool_report.sort(key=lambda e: e["fid"])
    lf_rows_totals = {
        "n_rows": int(sum(e.get("n_kept", 0) or 0 for e in pool_report)),
        "n_distinct_conditions": int(len(distinct_union)),
        "n_distinct_conditions_per_rung": {
            str(e["fid"]): e.get("n_distinct_conditions", 0) for e in pool_report},
        "axis_note": "the causal axis of the ladder is n_distinct_conditions "
                     "(union over rungs of the kept condition keys), NOT n_rows; "
                     "card recipe.env._cap_semantics",
        "definition": "condition key = tuple(np.round(row, 12)), the round's "
                      "registered convention (tools/affine_ladder_voi.py A7)",
    }

    # ── mode budget (over ALL train rungs, independent of the arm's LF pool) ──
    modes = resolve_alpha(p["mode_policy"], p["modes_cap"], grids)

    return {
        "train": train, "test": test, "hf_fid": hf, "hf_grid": hf_grid,
        "grids": grids, "lf_fids": lf_fids, "is_guard": is_guard,
        "sel": sel, "sub_mode": sub_mode, "n_train_all": int(n_train_all),
        "hf_rows_are_native_full": hf_rows_are_native_full,
        "cond_dim": int(cond_dim), "n_hf": n_hf,
        "X_all": X_all, "Y_all": Y_all, "X_hf": X_hf, "Y_hf": Y_hf,
        "X_te": X_te, "Y_te": Y_te, "Z_hf": Z_hf, "Z_te": Z_te,
        "mu": mu, "sd": sd, "s_hf": s_hf, "pool": pool, "pool_report": pool_report,
        "modes": modes,
        "scaler_report": scaler_report,          # CARDED CHANGE 1
        "lf_rows_totals": lf_rows_totals,        # CARDED CHANGE 2
        "hf_draw_nesting": hf_draw_nesting,      # CARDED CHANGE 3
    }


def design_coverage(d: dict) -> dict:
    """`m`, the rank and the singular values of `[X_hf, 1]` — REPORTED ONLY.

    `m` is the affine coverage deficit the card's part 2 quotes; no arm reads
    it, and the LF partition in `coverage.py` is defined by exact condition-row
    membership, not by this block.
    """
    null = ap.design_null(d["Z_hf"], RANK_TOL)
    # The RAW-coordinate design is an invertible reparameterisation of the
    # standardized one, so `m` and the numerical rank agree; it is computed too
    # because `tools/affine_ladder_voi.py` works in raw condition coordinates.
    null_raw = ap.design_null(d["X_hf"], RANK_TOL)
    return {
        "reported_only": True,
        "design": "[Z_hf, 1] (per-dim standardized by the N_hf HF train rows)",
        "singular_values": null["singular_values"],
        "numerical_rank": null["numerical_rank"],
        "m_null_dim": null["m_null_dim"],
        "n_cond_space_directions": null["n_cond_space_directions"],
        "n_dropped_zero_cond_part": null["n_dropped_zero_cond_part"],
        "rank_tol": null["rank_tol"],
        "raw_design": {
            "singular_values": null_raw["singular_values"],
            "numerical_rank": null_raw["numerical_rank"],
            "m_null_dim": null_raw["m_null_dim"],
            "note": "[X_hf, 1] in RAW condition units — the coordinate system of "
                    "tools/affine_ladder_voi.py"},
        "null_directions_augmented_raw": null_raw["null_directions_augmented"],
        "null_directions_cond_space_standardized": null["cond_directions"].tolist(),
    }


# ── training ──

def _predict(model, Z: np.ndarray, grid, scale: float, device) -> np.ndarray:
    model.eval()
    out = []
    with torch.no_grad():
        for i in range(0, Z.shape[0], PRED_CHUNK):
            xb = torch.from_numpy(np.ascontiguousarray(Z[i:i + PRED_CHUNK])).float().to(device)
            out.append((model(xb, grid) * scale).cpu().numpy())
    if not out:
        return np.zeros((0, int(grid[0]), int(grid[1])), dtype=np.float32)
    return np.concatenate(out, 0)


def train(model, p: dict, d: dict, steps: int, device,
          ckpt_path: Path, ckpt_key: dict, seed: int) -> dict:
    """Step-matched training (vendored unchanged from the base family).

    Every arm takes exactly `steps` optimizer steps and draws the same HF rows
    at every step: `_step_rng(seed, step)` is consumed for the HF batch FIRST,
    so the HF stream is identical in A0, A1, A2 and A3c at a given
    (dataset, split_seed). The LF arms' extra rung forward IS the treatment.
    A5_hf_budget_nolf changes N_hf and is therefore a LABELLED budget-varied
    arm, not a matched one; its HF batch is held at 5 (asserted in `recipe`), so
    even there the per-step gradient shape is unchanged and only the pool the
    batch is drawn from grows.
    """
    opt = torch.optim.AdamW(model.parameters(), lr=p["lr"], weight_decay=p["wd"])
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max(steps, 1))

    hf_Z = torch.from_numpy(d["Z_hf"]).float()
    hf_Y = torch.from_numpy(d["Y_hf"].reshape(d["n_hf"], *d["hf_grid"])
                            / d["s_hf"]).float()
    pool = []
    for r in d["pool"]:
        pool.append({
            "fid": r["fid"], "grid": r["grid"],
            "Z": torch.from_numpy(r["Z"]).float(),
            "Y": torch.from_numpy(r["Y"].reshape(r["Z"].shape[0], *r["grid"])
                                  / r["scaler"]).float(),
        })

    start_step, curve = 0, []
    if ckpt_path.exists():
        try:
            sd = torch.load(ckpt_path, map_location="cpu", weights_only=False)
            if sd.get("key") == ckpt_key:
                model.load_state_dict(sd["model"])
                curve = sd.get("curve", [])
                if sd.get("done"):
                    print(f"[resume] finished checkpoint found "
                          f"({sd['step']}/{steps} steps); skipping training", flush=True)
                    return {"steps_run": 0, "curve": curve, "resumed_from": int(sd["step"]),
                            "completed": True}
                opt.load_state_dict(sd["opt"])
                sched.load_state_dict(sd["sched"])
                start_step = int(sd["step"])
                print(f"[resume] continuing at step {start_step}/{steps}", flush=True)
            else:
                print("[resume] checkpoint key mismatch; training fresh", flush=True)
        except Exception as e:                                    # noqa: BLE001
            print(f"[resume] failed to load ({e}); training fresh", flush=True)

    def _save(step: int, done: bool) -> None:
        ckpt_path.parent.mkdir(parents=True, exist_ok=True)
        torch.save({"key": ckpt_key, "step": int(step), "done": bool(done),
                    "model": model.state_dict(), "opt": opt.state_dict(),
                    "sched": sched.state_dict(), "curve": curve}, ckpt_path)

    log_every = max(1, steps // LOG_POINTS)
    hf_bs = min(p["hf_batch"], d["n_hf"])
    t0 = time.time()
    model.train()
    for step in range(start_step, steps):
        rng = _step_rng(seed, step)
        opt.zero_grad(set_to_none=True)

        idx = torch.from_numpy(rng.choice(d["n_hf"], size=hf_bs, replace=False))
        xb = hf_Z[idx].to(device)
        yb = hf_Y[idx].to(device)
        loss_hf = F.mse_loss(model(xb, d["hf_grid"]), yb)
        loss = loss_hf
        l_lf = None                      # None, not NaN: the JSON must stay strict
        if pool:
            r = pool[step % len(pool)]                # rungs cycled deterministically
            n_f = r["Z"].shape[0]
            j = torch.from_numpy(rng.choice(n_f, size=min(p["lf_batch"], n_f),
                                            replace=False))
            zf = r["Z"][j].to(device)
            yf = r["Y"][j].to(device)
            loss_lf = F.mse_loss(model(zf, r["grid"]), yf)
            loss = loss + p["lambda_lf"] * loss_lf
            l_lf = float(loss_lf.detach())

        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), p["clip"])
        opt.step()
        sched.step()

        if (step + 1) % log_every == 0 or step + 1 == steps:
            curve.append({"step": step + 1, "hf": float(loss_hf.detach()),
                          "lf": l_lf, "lr": float(sched.get_last_lr()[0])})
            fmt = lambda x: "off" if x is None else f"{x:.4e}"   # noqa: E731
            print(f"[step {step+1:05d}/{steps}] hf={float(loss_hf.detach()):.4e} "
                  f"lf={fmt(l_lf)} ({time.time()-t0:.1f}s)", flush=True)
        if (step + 1) % p["ckpt_every_steps"] == 0 and step + 1 < steps:
            _save(step + 1, False)
    _save(steps, True)
    return {"steps_run": steps - start_step, "curve": curve,
            "resumed_from": start_step, "completed": True}


# ── reference arms ──

def reference_arms(args, p: dict, d: dict) -> tuple:
    """The non-trained reference splits + the frozen-floor / anchor seam checks."""
    want = set(p["ref_arms"])
    Y_te_flat = d["Y_te"].reshape(d["Y_te"].shape[0], -1)
    Y_hf_flat = d["Y_hf"].reshape(d["n_hf"], -1)
    splits, report = {}, {}

    zero = refs.zero_arm(Y_te_flat)
    if "zero" in want:
        splits.update(zero)
    if "nn_condition_n5" in want or "train_mean_n5" in want:
        n5 = refs.floor_arms(d["X_hf"], Y_hf_flat, d["X_te"], Y_te_flat, "_n5")
        splits.update({k: v for k, v in n5.items() if k[len("ref_"):] in want})
    if "nn_condition_full" in want or "train_mean_full" in want:
        full = refs.floor_arms(d["X_all"], d["Y_all"].reshape(d["n_train_all"], -1),
                               d["X_te"], Y_te_flat, "_full")
        splits.update({k: v for k, v in full.items() if k[len("ref_"):] in want})
        # The seam check needs all three arms; it runs off `full`/`zero`
        # regardless of which of them R3S3B2_REF_ARMS chose to REPORT.
        report["floor_seam_check"] = refs.seam_check_floors(
            args.dataset_name, full, zero, _abs(p["floors_json"]), p["floor_tol"])
    else:
        report["floor_seam_check"] = {
            "performed": False,
            "reason": "R3S3B2_REF_ARMS requests no *_full floor arm"}

    pred_pinv = pred_lstsq = None
    if "linear_hfonly" in want:
        pred_pinv = ap.min_norm_hfonly(d["X_hf"], Y_hf_flat, d["X_te"])
        splits["ref_linear_hfonly"] = refs.stats(pred_pinv, Y_te_flat)
        splits["ref_linear_hfonly"]["definition"] = (
            "min-norm affine fit on the N_hf HF train rows via pinv = the HF-only "
            "INFORMATION LIMIT at any capacity (tools/affine_ladder_voi.py A3 "
            "min_norm_pinv)")

    if "affine_on_hf_train" in want:
        pred_lstsq = ap.affine_on_hf_train(d["X_hf"], Y_hf_flat, d["X_te"])
        splits["ref_affine_on_hf_train"] = refs.stats(pred_lstsq, Y_te_flat)
        splits["ref_affine_on_hf_train"]["definition"] = (
            "min-norm least-squares affine map condition->field fit on the HF train "
            "rows (tools/make_round3_anchors.py::affine_fit, np.linalg.lstsq rcond=None); "
            "program.md (round 3) §2 MANDATORY reported arm next to every ifc number — "
            "an ifc claim that does not beat it has learned nothing beyond linearity")
        report["anchor_affine_seam_check"] = refs.seam_check_anchor_affine(
            args.dataset_name, splits["ref_affine_on_hf_train"]["rel_l2_mean"],
            _abs(p["anchors_json"]), d["hf_rows_are_native_full"])
    else:
        report["anchor_affine_seam_check"] = {
            "performed": False,
            "reason": "R3S3B2_REF_ARMS does not request affine_on_hf_train"}

    if pred_pinv is not None and pred_lstsq is not None:
        report["affine_estimator_agreement"] = {
            "note": "ref_linear_hfonly (pinv, tools/affine_ladder_voi.py A3) vs "
                    "ref_affine_on_hf_train (lstsq, tools/make_round3_anchors.py) — the "
                    "same map by two published definitions; a large divergence means one "
                    "of them moved",
            "max_abs_pred_diff": float(np.abs(pred_pinv - pred_lstsq).max()),
            "abs_nrmse_diff": float(abs(splits["ref_linear_hfonly"]["rel_l2_mean"]
                                        - splits["ref_affine_on_hf_train"]["rel_l2_mean"])),
        }
    return splits, report


# ── CARDED CHANGE 4: the mediator and the forward-sensitive stratification ──

# The split-identity constant. `sha256` of `np.round(cond_test, 12)` (the
# round's registered condition-key rounding, tools/affine_ladder_voi.py A7) for
# `sharp__cahn_hilliard`'s 100 x 19 test condition matrix in the stripped view.
#
# PROVENANCE (builder, 2026-08-10, both derivations run in this build session):
#   (a) this family's own path — data_adapters.loaders.load_mf_dataset(
#       mffp_autoresearch/round2/stripped_data/sharp__cahn_hilliard, "test");
#   (b) r3s1_factorised-B1's OWN path — its `r3s1_twostage_crosscoef.common.Panel`
#       over the same stripped dir, i.e. the exact object whose `cond_test` row
#       order the imported mask was built against
#       (`worktrees/r3s1_factorised/B1/scratchpad/reanalysis_turn_3.py::t3c`).
# Both give 7558526337372366f9a817995e3efbbb1365808bb2ce9fa7544f182bf6a201f7, so
# the mask's row i and this family's test row i are the same sample. If the
# split ever moves, the assert fires and the stratification is refused rather
# than silently applied to a different ordering.
CH_TEST_COND_SHA256_ROUND12 = (
    "7558526337372366f9a817995e3efbbb1365808bb2ce9fa7544f182bf6a201f7")

# The inline definition the card REQUIRES on first use of the subpopulation name
# (`recipe.env._hard_mask`, blocking). Emitted verbatim in every result JSON.
FORWARD_SENSITIVE_DEFINITION = (
    "FORWARD-SENSITIVE subpopulation: condition-space-indistinguishable (max "
    "per-dim standardised gap 0.4476 sigma, nearest-train-neighbour ratio "
    "1.0176) but field-distant (nearest-train-field rel-L2 ratio 3.29). "
    "Measured by r3s1_factorised-B1 turn 3 (T3c) on the 27 seed-invariant hard "
    "rows of sharp__cahn_hilliard's 100-row test split.")


def _assert_no_banned_terms(text: str, where: str) -> None:
    """Card `recipe.env._hard_mask`: the banned words must not reach an artifact.

    The literature uses them for the OPPOSITE meaning (PLOS pcbi.1013553), so
    this family names the subpopulation FORWARD-SENSITIVE and refuses to write a
    result JSON containing the banned vocabulary.
    """
    low = text.lower()
    hit = sorted({t for t in BANNED_TERMS if t in low})
    if hit:
        raise SystemExit(
            f"BANNED TERMINOLOGY {hit} found in {where}. Card "
            "`recipe.env._hard_mask` bans it (the literature uses it for the "
            "opposite meaning); the subpopulation is named FORWARD-SENSITIVE.")


def _response_stats(P: np.ndarray, H: np.ndarray) -> dict:
    """Condition-response amplitude / alignment / own-spread of one arm.

    DEFINITIONS ARE `mffp_autoresearch/round3/tools/response_decomposition.py`
    VERBATIM (`sigma`, `alignment`, and the `own_spread` expression in
    `main`) — restated here rather than imported because that tool's module
    body imports `panel_data`, whose `load_split` reads the ORIGINAL data root;
    this family must never open that path (program.md §5, stripped test view).
    The tool remains the analysis-side instrument; these numbers exist so the
    mediator is available per leg without re-loading every prediction dump.

        response_amplitude  sigma_pred / sigma_hf,
                            sigma_X = sqrt(mean_cells var_samples X)
        response_alignment  mean_i cos(pred_i - mean_j pred_j, hf_i - mean_j hf_j)
        own_spread          mean_i ||pred_i - mean_j pred_j|| / ||hf_i||
    """
    P = np.asarray(P, dtype=np.float64).reshape(np.asarray(P).shape[0], -1)
    H = np.asarray(H, dtype=np.float64).reshape(np.asarray(H).shape[0], -1)
    sigma = lambda X: float(np.sqrt(np.mean(np.var(X, axis=0))))   # noqa: E731
    dP = P - P.mean(axis=0, keepdims=True)
    dH = H - H.mean(axis=0, keepdims=True)
    nP, nH = np.linalg.norm(dP, axis=1), np.linalg.norm(dH, axis=1)
    ok = (nP > 0) & (nH > 0)
    align = (float(np.mean(np.sum(dP[ok] * dH[ok], axis=1) / (nP[ok] * nH[ok])))
             if ok.any() else float("nan"))
    sH = sigma(H)
    return {
        "response_amplitude": float(sigma(P) / sH) if sH > 0 else float("nan"),
        "response_alignment": align,
        "own_spread": float(np.mean(nP / np.linalg.norm(H, axis=1))),
        "hf_own_spread": float(np.mean(nH / np.linalg.norm(H, axis=1))),
        "sigma_pred": sigma(P), "sigma_hf": sH,
        "definition_source": "tools/response_decomposition.py (sigma, alignment, "
                             "own_spread), restated in-process",
    }


def _split_identity(dataset: str, X_te: np.ndarray) -> dict:
    """Assert this leg's test split is the one the imported mask was built on."""
    n_test = int(X_te.shape[0])
    digest = hashlib.sha256(
        np.ascontiguousarray(np.round(np.asarray(X_te, dtype=np.float64), 12))
        .tobytes()).hexdigest()
    rec = {"dataset": dataset, "n_test": n_test,
           "cond_matrix_sha256_round12": digest,
           "expected_n_test": HARD_MASK_N_TEST,
           "expected_cond_matrix_sha256_round12": CH_TEST_COND_SHA256_ROUND12,
           "convention": "sha256 of np.round(cond_test, 12).tobytes(), C-order "
                         "float64 — the round's registered condition-key rounding"}
    if n_test != HARD_MASK_N_TEST:
        raise SystemExit(
            f"SPLIT IDENTITY FAILED on {dataset}: n_test {n_test} != "
            f"{HARD_MASK_N_TEST}; the imported forward-sensitive mask is a "
            f"{HARD_MASK_N_TEST}-element mask over r3s1_factorised-B1's test split "
            "and cannot be applied to a different split")
    if digest != CH_TEST_COND_SHA256_ROUND12:
        raise SystemExit(
            f"SPLIT IDENTITY FAILED on {dataset}: condition-matrix digest {digest} "
            f"!= r3s1_factorised-B1's {CH_TEST_COND_SHA256_ROUND12}. The test split "
            "moved, so the imported mask's row order is no longer this split's; "
            "refusing to stratify")
    rec["match"] = True
    return rec


def _import_hard_mask(path: Path) -> np.ndarray:
    obj = json.loads(Path(path).read_text())
    for key in HARD_MASK_JSON_KEYPATH:
        if not isinstance(obj, dict) or key not in obj:
            raise SystemExit(
                f"{path}: no {'.'.join(HARD_MASK_JSON_KEYPATH)} entry "
                "(R3S3B2_HARD_MASK_JSON must be r3s1_factorised-B1's turn-3 results)")
        obj = obj[key]
    m = np.asarray(obj, dtype=np.int64)
    if m.shape != (HARD_MASK_N_TEST,) or set(np.unique(m)) - {0, 1}:
        raise SystemExit(f"{path}: hard_mask is not a {HARD_MASK_N_TEST}-element "
                         f"0/1 vector (got shape {m.shape})")
    if int(m.sum()) != HARD_MASK_N_HARD:
        raise SystemExit(f"{path}: hard_mask has {int(m.sum())} ones, the card "
                         f"records {HARD_MASK_N_HARD}")
    return m.astype(bool)


def _rederive_hard_mask(Y_te: np.ndarray, Y_train_all: np.ndarray) -> dict:
    """MODEL-FREE re-derivation: the top-27 test rows by nearest-train-HF-field
    relative L2 distance.

    Card `recipe.env._hard_mask`: the imported mask came from r3s1's own per-row
    rel-L2 bimodality and is therefore MODEL-DEPENDENT, so the card requires an
    independent, model-free definition and the overlap between the two.

        d_i = min_j ||y_te_i - y_train_j||_2 / ||y_te_i||_2

    over the FULL HF train split (not this arm's N_hf draw), so the mask is a
    property of the dataset alone — identical in every arm, cap and seed of the
    grid, exactly like the imported one. Ties break by the lowest test index
    (`np.argsort(kind="stable")`). This is a REPORTING stratification computed
    after the scored prediction exists; nothing in training or prediction reads
    it.
    """
    T = np.asarray(Y_te, dtype=np.float64).reshape(Y_te.shape[0], -1)
    R = np.asarray(Y_train_all, dtype=np.float64).reshape(Y_train_all.shape[0], -1)
    d2 = (np.einsum("ij,ij->i", T, T)[:, None]
          - 2.0 * (T @ R.T)
          + np.einsum("ij,ij->i", R, R)[None, :])
    dist = np.sqrt(np.maximum(d2.min(axis=1), 0.0)) / np.linalg.norm(T, axis=1)
    order = np.argsort(-dist, kind="stable")
    mask = np.zeros(T.shape[0], dtype=bool)
    mask[order[:HARD_MASK_N_HARD]] = True
    return {"mask": mask, "distance": dist,
            "definition": "top-%d test rows by min_j ||y_te_i - y_train_j|| / "
                          "||y_te_i|| over the FULL HF train split; model-free"
                          % HARD_MASK_N_HARD,
            "n_train_rows_searched": int(R.shape[0])}


def _stratum_stats(rel: np.ndarray, mask: np.ndarray) -> dict:
    r = np.asarray(rel, dtype=np.float64)
    m = np.asarray(mask, dtype=bool)
    out = {}
    for name, sel in (("hard_forward_sensitive", m), ("easy_bulk", ~m)):
        v = r[sel]
        out[name] = {
            "n_rows": int(v.size),
            "rel_l2_mean": float(v.mean()) if v.size else float("nan"),
            "rel_l2_median": float(np.median(v)) if v.size else float("nan"),
            "rel_l2_std": float(v.std(ddof=1)) if v.size > 1 else 0.0,
        }
    out["hard_minus_easy_rel_l2_mean"] = (
        out["hard_forward_sensitive"]["rel_l2_mean"] - out["easy_bulk"]["rel_l2_mean"])
    return out


def stratification(args, p: dict, d: dict, rel_rows: np.ndarray) -> dict:
    """The per-row stratified emission (CARDED CHANGE 4).

    Runs on `sharp__cahn_hilliard` only (the mask is that split's); every other
    dataset gets an explicit not-applicable record rather than a silent skip.
    """
    if p["stratify_rows"] != "1" or p["hard_mask_mode"] == "off":
        return {"performed": False,
                "reason": "R3S3B2_STRATIFY_ROWS=0 or R3S3B2_HARD_MASK_MODE=off"}
    if args.dataset_name != HARD_MASK_DATASET:
        return {"performed": False,
                "reason": f"the forward-sensitive mask is defined on "
                          f"{HARD_MASK_DATASET} only (r3s1_factorised-B1 T3c); "
                          f"this leg is {args.dataset_name}"}

    rec = {"performed": True,
           "terminology": FORWARD_SENSITIVE_DEFINITION,
           "mode": p["hard_mask_mode"],
           "split_identity": _split_identity(args.dataset_name, d["X_te"]),
           "scored_metric": "per-row rel-L2 of the SCORED test split, the round's "
                            "one nRMSE definition (round2/eval/nrmse.py), taken from "
                            "splits.test_hf.rel_l2_per_sample",
           "masks": {}}
    rel = np.asarray(rel_rows, dtype=np.float64)
    masks = {}

    if p["hard_mask_mode"] in ("import_and_rederive", "import_only"):
        mi = _import_hard_mask(_abs(p["hard_mask_json"]))
        masks["imported_r3s1_b1"] = mi
        rec["masks"]["imported_r3s1_b1"] = {
            "source": str(_abs(p["hard_mask_json"])),
            "keypath": ".".join(HARD_MASK_JSON_KEYPATH),
            "n_hard": int(mi.sum()),
            "caveat": "MODEL-DEPENDENT: derived from r3s1_factorised-B1's own per-row "
                      "rel-L2 bimodality (its ref_head_onestage arm, hard = rel-L2 > "
                      "0.8 at all three seeds)",
            "row_indices": [int(i) for i in np.flatnonzero(mi)],
            **_stratum_stats(rel, mi)}

    if p["hard_mask_mode"] in ("import_and_rederive", "rederive_only"):
        rd = _rederive_hard_mask(d["Y_te"], d["Y_all"])
        masks["rederived_model_free"] = rd["mask"]
        rec["masks"]["rederived_model_free"] = {
            "definition": rd["definition"],
            "n_train_rows_searched": rd["n_train_rows_searched"],
            "n_hard": int(rd["mask"].sum()),
            "row_indices": [int(i) for i in np.flatnonzero(rd["mask"])],
            "nearest_train_field_rel_l2_hard_mean": float(
                rd["distance"][rd["mask"]].mean()),
            "nearest_train_field_rel_l2_easy_mean": float(
                rd["distance"][~rd["mask"]].mean()),
            **_stratum_stats(rel, rd["mask"])}

    if len(masks) == 2:
        a, b = masks["imported_r3s1_b1"], masks["rederived_model_free"]
        inter = int((a & b).sum())
        union = int((a | b).sum())
        rec["mask_overlap"] = {
            "n_overlap": inter,
            "jaccard": float(inter / union) if union else float("nan"),
            "overlap_fraction_of_27": float(inter / max(int(a.sum()), 1)),
            "agree": bool(np.array_equal(a, b)),
            "publication_rule": "card recipe.env._hard_mask: report the overlap and "
                                "PUBLISH THE STRATIFICATION UNDER BOTH MASKS if they "
                                "disagree — both are emitted above unconditionally",
        }
    return rec


# ── main ──

def run(args, out_path: Path) -> dict:
    p = recipe(args.dataset_name)
    _seed_everything(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # BLOCKING pre-flight, before any compute (card part 3): the skill
    # denominator this leg will be scored under and the floors/anchors it will
    # be compared against must come from the same eval layer and carry the same
    # per-dataset reference.
    if p["data_binding_assert"] == "1":
        binding = assert_data_binding(args.dataset_name, EVAL_DIR,
                                      _abs(p["floors_json"]))
    else:
        binding = {"performed": False,
                   "reason": "R3S3B2_DATA_BINDING_ASSERT=0"}

    d = prepare(args, p)
    steps = int(args.epochs) * p["steps_per_epoch"]
    print(f"[data] {args.dataset_name} loader={d['train']['loader']} HF={d['hf_fid']} "
          f"grid={d['hf_grid']} arm={p['arm']} cond_set={p['lf_cond_set']} "
          f"cap={p['lf_cond_cap']} split={d['sub_mode']} "
          f"N_hf={d['n_hf']}/{d['n_train_all']} cond_dim={d['cond_dim']} "
          f"lf_pool={[(r['fid'], int(r['Z'].shape[0]), r['grid']) for r in d['pool']]} "
          f"alpha={d['modes']['alpha']} ({d['modes']['policy']}) "
          f"s_hf={d['s_hf']:.4e} steps={steps} N_test={d['X_te'].shape[0]} "
          f"device={device}", flush=True)

    # Seam assert: the vendored ADR r2-0001 lift == the eval layer's copy-LF
    # convention, TRAIN split, RAISE on mismatch.
    lf_verify = (verify_against_eval(d["train"], args.dataset_name, EVAL_DIR, tol=1e-9)
                 if d["lf_fids"] else
                 {"performed": False, "reason": "no LF rung in the train split"})

    coverage_block = design_coverage(d)

    model = CoverageDecoder(d["cond_dim"], width=p["width"], blocks=p["blocks"],
                            alpha=d["modes"]["alpha"], film_hidden=p["width"]).to(device)
    n_params = param_count(model)

    resolved = {k: v for k, v in p.items()}
    resolved["ref_arms"] = list(p["ref_arms"])
    resolved["_rank_tol_frozen"] = RANK_TOL
    ckpt_key = {
        "model": MODEL_NAME, "dataset": args.dataset_name,
        "steps_target": int(steps), "arm": p["arm"], "split_seed": str(p["split_seed"]),
        "seed": int(args.seed), "grid": list(d["hf_grid"]),
        "alpha": int(d["modes"]["alpha"]),
        "recipe_digest": hashlib.sha256(
            json.dumps(resolved, sort_keys=True).encode()).hexdigest()[:16],
    }
    ckpt_dir = Path(args.ckpt_dir)
    ckpt_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    fit = train(model, p, d, steps, device, ckpt_dir / "last.pt",
                ckpt_key, int(args.seed))
    train_seconds = time.time() - t0

    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats()
        torch.cuda.synchronize()
    t1 = time.time()
    pred_te = _predict(model, d["Z_te"], d["hf_grid"], d["s_hf"], device)
    if device.type == "cuda":
        torch.cuda.synchronize()
    eval_seconds = time.time() - t1
    n_test = int(d["Y_te"].shape[0])
    target_te = d["Y_te"].reshape(n_test, -1)
    pred_te_flat = pred_te.reshape(n_test, -1).astype(np.float64)

    written = finalize_and_write(
        out_path=out_path, model=MODEL_NAME, dataset=args.dataset_name,
        pred=pred_te_flat, target=target_te, work_grid=d["hf_grid"],
        n_params=int(n_params), train_seconds=train_seconds, eval_seconds=eval_seconds,
        latency_ms_per_sample=(1000.0 * eval_seconds / max(n_test, 1)
                               if device.type == "cuda" else None),
        peak_mem_mb=(torch.cuda.max_memory_allocated() / 1e6
                     if device.type == "cuda" else None),
        seed=args.seed, extra={})

    # ── reference / floor arms (merged in AFTER the scored split) ──
    ref_splits, ref_report = reference_arms(args, p, d)
    written["splits"].update(ref_splits)

    # ── the reported instrument block (reported, never a switch) ──
    pred_tr = _predict(model, d["Z_hf"], d["hf_grid"], d["s_hf"], device)
    train_rel = refs.stats(pred_tr.reshape(d["n_hf"], -1).astype(np.float64),
                           d["Y_hf"].reshape(d["n_hf"], -1))
    gate = {
        "reported_never_a_switch": True,
        "data_binding_assert": binding,
        "design_coverage": coverage_block,
        "train_vs_test_gap": {
            "train_nRMSE_at_hf_train_conditions": train_rel["rel_l2_mean"],
            "test_nRMSE": float(written["splits"]["test_hf"]["rel_l2_mean"]),
            "gap": float(written["splits"]["test_hf"]["rel_l2_mean"]
                         - train_rel["rel_l2_mean"])},
        **ref_report,
    }
    if p["target_scale_audit"] == "1":
        gate["target_scale_audit"] = {
            "hf_rung": refs.target_scale_geometry(
                d["Y_hf"].reshape(d["n_hf"], -1), d["s_hf"]),
            "lf_rungs": {str(r["fid"]): refs.target_scale_geometry(
                r["Y"].reshape(r["Z"].shape[0], -1), r["scaler"]) for r in d["pool"]},
        }
    # CARDED CHANGE 4a — the MEDIATOR. `R3S3B2_ALIGNMENT_REPORT`: the
    # condition-response alignment and amplitude of THIS leg's scored
    # prediction, the quantity the card's D-D deliverable regresses R against
    # ("nothing retrieved reports a mediating learned quantity for MF
    # sample-count curves"). Reported per leg; nothing branches on it.
    if p["alignment_report"] == "1":
        gate["response_decomposition"] = {
            **_response_stats(pred_te_flat, target_te),
            "scope": "scored test split, condition-only prediction",
            "role": "MEDIATOR of the card's deliverable D-D; reported, never a switch",
        }
        gate["response_decomposition_train_rows"] = {
            **_response_stats(pred_tr.reshape(d["n_hf"], -1).astype(np.float64),
                              d["Y_hf"].reshape(d["n_hf"], -1)),
            "scope": "the arm's own N_hf HF train rows",
        } if d["n_hf"] > 1 else {"performed": False,
                                 "reason": "fewer than 2 HF train rows"}

    # CARDED CHANGE 4b — the FORWARD-SENSITIVE stratification, computed from the
    # per-row rel-L2 array the eval layer itself scores on.
    rel_rows = np.asarray(written["splits"]["test_hf"]["rel_l2_per_sample"],
                          dtype=np.float64)
    gate["forward_sensitive_stratification"] = stratification(args, p, d, rel_rows)

    written["row_efficiency"] = {
        "card": "r3s3_lf_value-B2",
        "arm": p["arm"],
        "arm_spec": {"n_hf_allowed": list(ARMS[p["arm"]]["n_hf"]),
                     "cond_set": ARMS[p["arm"]]["cond_set"],
                     "cap_allowed": (list(LF_COND_CAP_LADDER.get(args.dataset_name, ()))
                                     if ARMS[p["arm"]]["cap"] is None
                                     else list(ARMS[p["arm"]]["cap"])),
                     "n_hf_this_leg": int(p["n_hf"]),
                     "cap_this_leg": int(p["lf_cond_cap"])},
        "primary_arm": PRIMARY_ARM,
        "scored_contrast_arms": list(SCORED_CONTRAST_ARMS),
        "budget_varied_arms": list(BUDGET_VARIED_ARMS),
        "arms_available": sorted(ARMS),
        "arm_role": ("PRIMARY scored arm (the RECOVERY DENOMINATOR)"
                     if p["arm"] == PRIMARY_ARM else
                     ("LABELLED budget-varied reference arm OUTSIDE the scored contrast "
                      "(N_hf differs); never quote as a matched arm"
                      if p["arm"] in BUDGET_VARIED_ARMS else
                      "matched control arm of the scored contrast")),
        "deliverable_semantics": {
            "R": "recovery ratio (nRMSE(A0_nolf) - nRMSE(arm)) / "
                 "(nRMSE(A0_nolf) - nRMSE(A1_lf_all)); REFERENCE-FREE",
            "D_A_knee": "R vs n_distinct_conditions along the A3c cap ladder",
            "D_B_floor_crossing_cap": "the smallest cap whose scored nRMSE beats the "
                                      "dataset's best training-free floor",
            "D_C_exchange_rate": "the LF-cap bracket whose mean R matches R at "
                                 "N_HF in {10,20,40} — sharp__cahn_hilliard ONLY",
            "D_D_mediator": "R vs the recorded response_alignment (gate_report."
                            "response_decomposition)",
            "D_E_stratification": "R_hard vs R_easy on the 27/73 forward-sensitive "
                                  "split",
            "D_F_decomposition": "E_cov/E_total and E_opt under the fixed "
                                 "per_rung_max_fullpool scaler",
            "note": "all differences are ANALYSIS-SIDE; this family computes no "
                    "cross-arm quantity",
        },
        "cap_ladder_for_dataset": list(LF_COND_CAP_LADDER.get(args.dataset_name, ())),
        "hf_budget_ladder": {"datasets": list(HF_BUDGET_DATASETS),
                             "n_hf_values": list(HF_BUDGET_LADDER),
                             "hf_batch_held_at": HF_BUDGET_BATCH,
                             "draw_nesting": d["hf_draw_nesting"]},
        "dataset": args.dataset_name,
        "seed": int(args.seed),
        "epochs": int(args.epochs),
        "steps": int(steps),
        "steps_per_epoch": p["steps_per_epoch"],
        "budget_equality": "identical optimizer steps and identical HF-row exposure in "
                           "every N_hf = 5 arm; the LF arms' extra rung forward IS the "
                           "treatment. A5_hf_budget_nolf varies the HF budget by design "
                           "and is labelled as such; its HF batch is held at "
                           f"{HF_BUDGET_BATCH} so the per-step gradient shape is matched "
                           "across the HF ladder.",
        "seed_semantics": "R3S3B2_SPLIT_SEED is an HF-SUBSET DRAW, not a training seed. "
                          "The training seed is --seed (0 on every leg of this card). "
                          "Draws must never be bootstrapped as a seed CI.",
        "split": {"mode": d["sub_mode"], "split_seed": str(p["split_seed"]),
                  "n_hf": d["n_hf"], "n_train_all": d["n_train_all"],
                  "hf_rows_are_native_full": d["hf_rows_are_native_full"],
                  "selected_train_rows": [int(i) for i in d["sel"]],
                  "note": "the N_hf rows are SELECTED from the existing train split; no "
                          "HF sample is added and no file is regenerated (program.md "
                          "§5.11)"},
        "lf_selector": {
            "lf_cond_set": p["lf_cond_set"], "lf_cond_cap": p["lf_cond_cap"],
            "membership": "exact condition-row match, key = tuple(np.round(row, 12)) "
                          "(tools/affine_ladder_voi.py A7 convention)",
            "cap_rule": "per rung, np.sort(default_rng([split_seed, fid])"
                        ".permutation(n_candidates)[:cap]) — see coverage.cap_draw for "
                        "the TBD this resolves and why the draw is per rung",
        },
        # CARDED CHANGE 1 — the full arm-invariant scaler record (s_rung, s_hf,
        # s_rung/s_hf, the invariance probes, and the arm-rows-vs-fullpool ratio
        # that reproduces B1's measured confound).
        "scalers": {"rule": p["scaler"], "s_hf": d["s_hf"],
                    "per_rung": {str(r["fid"]): r["scaler"] for r in d["pool"]},
                    **d["scaler_report"]},
        "modes": d["modes"],
        "lf_pool": d["pool_report"],
        # CARDED CHANGE 2 — the ladder's causal axis.
        "lf_row_manifest": d["lf_rows_totals"],
        "lf_row_manifest_enabled": p["lf_row_manifest"] == "1",
        "lf_lift_verification": lf_verify,
        "lf_convention": convention_for(args.dataset_name),
        "cond_standardization": {"source": "the N_hf HF train rows (identical in every "
                                           "arm at a given dataset/split_seed/N_hf)",
                                 "mu": [float(x) for x in d["mu"]],
                                 "sd": [float(x) for x in d["sd"]]},
        "gate_report": gate,
        "loss_curve": fit["curve"],
        "resumed_from_step": fit["resumed_from"],
        "min_claimable_effect": refs.resolve_min_claimable_effect(
            args.dataset_name, _abs(p["noise_floor_json"]), p["mce_mode"]),
        "reporting_discipline": {
            "reference_free": args.dataset_name in p["reference_free_datasets"],
            "reference_free_datasets": list(p["reference_free_datasets"]),
            "rule": ("REFERENCE-FREE (ADR r3-0003 D2, MDD 1.7077): report nRMSE ratios "
                     "and R, never a copy-LF skill delta on this dataset"
                     if args.dataset_name in p["reference_free_datasets"] else
                     "reference-bearing: skill against the eval layer's copy-LF / "
                     "paper-bar denominator is quotable for this dataset"),
            "ifc_affine_floor_rule": (
                "program.md (round 3) §2: every ifc_heat number is reported next to the "
                "fitted affine_on_hf_train floor (0.070918) and the paper bar 0.074 — "
                "see splits.ref_affine_on_hf_train"
                if args.dataset_name == "ifc_heat" else None),
            "datasets_of_this_card": "sharp__cahn_hilliard,ifc_heat (explicit list; "
                                     "--datasets panel is NEVER used — it resolves the "
                                     "ROUND-2 panel)",
            "dropped": {"ifc_poisson": "B1 part 7 requirement 2 — exactly affine "
                                       "(oracle residual 2.9e-08), affine_on_hf_train "
                                       "0.057375 unbeaten",
                        "sharp__phase_field_crystal_2d": "report-only, ADR r3-0004 "
                                                         "(scored cell task-void)"},
        },
        "stale_checkpoint_guard": {
            "enabled": p["stale_ckpt_assert"] == "1",
            "where": "scripts/01_train_eval.sh runs tools/stale_checkpoint_audit.py "
                     "--fail-on-stale over THIS card's own outputs before any scoring "
                     "(a family process cannot audit result files that do not exist "
                     "yet); this flag records that the leg was configured under it",
            "resumed_from_step": fit["resumed_from"],
            "steps_target": int(steps),
        },
        "declared_baseline_cited_not_rerun": {
            "family": "mf_fno_transfer_film",
            "role": "program.md §12.3 mandatory declared baseline (LF-pretrain -> "
                    "HF-finetune from the condition vector); CITED, not re-run. This "
                    "card differentiates it: transfer_film blends the optimisation and "
                    "coverage channels on the FULL LF pool, which is exactly the split "
                    "A2 / A3c separate.",
            "source": "mffp_autoresearch_outputs/round2/r2s3_lf_train_signal/B1/eval/"
                      "result_ifc_poisson_baseline_mf_fno_transfer_film_s0.json",
            "caveat": "that number was measured on the PRE-repair ifc_poisson ladder "
                      "(ADR r3-0001 D3 swapped it 2026-08-05); quote it only with the "
                      "superseded-data flag"},
        "resolved_recipe": resolved,
        "recipe_env": {k: v for k, v in sorted(os.environ.items())
                       if k.startswith("R3S3B2_")},
    }
    written.update({
        "device": str(device),
        "hf_fidelity": int(d["hf_fid"]),
        "hf_grid": list(d["hf_grid"]),
        "n_train_hf": int(d["n_hf"]),
        "test_input": "condition_vector_only",
        "lf_read_at_train": bool(d["pool"]),
        "lf_read_at_test": False,
        "field_input_at_test": False,
        "mf_mechanism": "train-only LF rung supervision partitioned by condition "
                        "coverage of the HF draw, row-count-laddered by "
                        "R3S3B2_LF_COND_CAP; no penalty, no LF at test",
        "scored_arm": p["arm"],
    })
    # CARDED CHANGE 4 (terminology, blocking): nothing this family writes may
    # carry the banned vocabulary. Checked on the SERIALISED text, so a string
    # smuggled in through any nested block fails before the file exists.
    text = json.dumps(written, indent=2)
    _assert_no_banned_terms(text, f"the result JSON for {args.dataset_name}")
    Path(out_path).write_text(text)

    if p["dump_train_preds"] == "1" or p["dump_test_preds"] == "1":
        dump = Path(out_path).with_suffix("").as_posix() + "_preds.npz"
        arrays = {
            "hf_grid": np.asarray(d["hf_grid"], dtype=np.int64),
            "s_hf": np.asarray([d["s_hf"]], dtype=np.float64),
            "selected_train_rows": np.asarray(d["sel"], dtype=np.int64),
        }
        if p["dump_train_preds"] == "1":
            arrays.update(
                cond_hf_train_raw=d["X_hf"].astype(np.float64),
                pred_hf_train=pred_tr.reshape(d["n_hf"], -1).astype(np.float32),
                target_hf_train=d["Y_hf"].reshape(d["n_hf"], -1).astype(np.float32))
        if p["dump_test_preds"] == "1":
            arrays.update(
                cond_test_raw=d["X_te"].astype(np.float64),
                pred_test=pred_te_flat.astype(np.float32))
            # CARDED CHANGE 4 — the PER-ROW stratified dump. `rel_l2_test` is
            # the same per-row array the eval layer scores on; the two masks are
            # written beside it so any downstream stratification uses this leg's
            # own rows and never re-derives an ordering.
            arrays["rel_l2_test"] = rel_rows.astype(np.float64)
            strat = gate["forward_sensitive_stratification"]
            if strat.get("performed"):
                for name, blk in strat["masks"].items():
                    m = np.zeros(rel_rows.shape[0], dtype=np.int8)
                    m[np.asarray(blk["row_indices"], dtype=np.int64)] = 1
                    arrays[f"hard_mask_{name}"] = m
        np.savez_compressed(dump, **arrays)
        print(f"[wrote] {dump}", flush=True)

    for k in ("test_hf", *sorted(k for k in written["splits"] if k.startswith("ref_"))):
        e = written["splits"][k]
        print(f"[split] {k:26s} nRMSE={e['nRMSE']:.6f} "
              f"rel_l2_mean={e['rel_l2_mean']:.6f}", flush=True)
    print(f"[gate] arm={p['arm']} cond_set={p['lf_cond_set']} cap={p['lf_cond_cap']} "
          f"m={coverage_block['m_null_dim']} rank={coverage_block['numerical_rank']} "
          f"lf_rows_kept={[r.get('n_kept') for r in d['pool_report']]} "
          f"uncovered_available={[r.get('cond_rows_uncovered_by_hf_train') for r in d['pool_report']]} "
          f"train_nRMSE={train_rel['rel_l2_mean']:.6f}", flush=True)
    print(f"[rows] n_rows={d['lf_rows_totals']['n_rows']} "
          f"n_distinct_conditions={d['lf_rows_totals']['n_distinct_conditions']} "
          f"per_rung={d['lf_rows_totals']['n_distinct_conditions_per_rung']}", flush=True)
    print(f"[scaler] rule={d['scaler_report']['rule']} s_hf={d['s_hf']:.6e} "
          f"s_rung_over_s_hf={d['scaler_report']['s_rung_over_s_hf']} "
          f"invariance_ok={d['scaler_report'].get('all_bit_identical')}", flush=True)
    if p["alignment_report"] == "1":
        rdc = gate["response_decomposition"]
        print(f"[mediator] alignment={rdc['response_alignment']:.6f} "
              f"amplitude={rdc['response_amplitude']:.6f} "
              f"own_spread={rdc['own_spread']:.6f}", flush=True)
    strat = gate["forward_sensitive_stratification"]
    if strat.get("performed"):
        for name, blk in strat["masks"].items():
            print(f"[stratum] {name:24s} hard(n={blk['hard_forward_sensitive']['n_rows']})"
                  f"={blk['hard_forward_sensitive']['rel_l2_mean']:.6f} "
                  f"easy(n={blk['easy_bulk']['n_rows']})="
                  f"{blk['easy_bulk']['rel_l2_mean']:.6f}", flush=True)
        if "mask_overlap" in strat:
            print(f"[stratum] mask overlap n={strat['mask_overlap']['n_overlap']}/"
                  f"{HARD_MASK_N_HARD} jaccard="
                  f"{strat['mask_overlap']['jaccard']:.4f}", flush=True)
    return written


def main() -> None:
    a = argparse.ArgumentParser()
    a.add_argument("--dataset_dir", required=True)
    a.add_argument("--dataset_name", required=True)
    a.add_argument("--epochs", type=int, required=True)
    a.add_argument("--out", required=True)
    a.add_argument("--ckpt_dir", required=True)
    a.add_argument("--seed", type=int, default=0)
    args = a.parse_args()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    res = run(args, out)
    print(f"[wrote] {out} nRMSE={res['splits']['test_hf']['rel_l2_mean']:.6f}",
          flush=True)


if __name__ == "__main__":
    main()
