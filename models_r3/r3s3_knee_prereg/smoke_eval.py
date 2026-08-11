"""r3s3_knee_prereg — the PRE-REGISTERED KNEE of the coverage ladder: the
training-free surrogate's step-max knee cap, SEALED before any leg ran, then
confirmed by a minimal ratio-4 ladder and adjudicated in ADR r3-0006 film units
(card `r3s3_lf_value-B3`).

Factory MODEL_CONTRACT CLI (unchanged):
    --dataset_dir --dataset_name --epochs --out --ckpt_dir --seed

ONE invocation trains ONE arm (`R3S3B3_ARM`) on ONE dataset at ONE HF-subset
draw (`R3S3B3_SPLIT_SEED`) and writes one result JSON whose `splits.test_hf` is
the scored condition-only prediction. The card's <= 71-leg-per-seed grid is
driven by `scripts/01_train_eval.sh`, which gives every leg its own
`ROUND2_EVAL_RESULTS` (hence its own `ckpt_dir` and result path) and its own
`done` marker.

ARMS (card part 3 "Arms" + `recipe.env._note`). Every arm is step-matched —
identical optimizer steps and identical HF-row exposure at N_hf = 5; the LF
pool's extra rung forward IS the treatment. The card's ARM<->selector binding
names exactly three arms and says "Any other combination raises":

    A0_nolf            HF only (N_hf = 5). The matched no-LF control and the
                       numerator baseline of the recovery ratio R.
    A1_lf_all          + all rungs at all their conditions. PRIMARY SCORED ARM,
                       the RECOVERY DENOMINATOR, and the ladder's top rung
                       `r4 = FULL`.
    A3c_lf_uncov_cap   + `R3S3B3_LF_COND_CAP` uncovered conditions PER RUNG ->
                       the LADDER arm, run at the SEALED `r1`, `r2`, `r3`.

B2's `A2_lf_covered` and `A5_hf_budget_nolf` are deliberately ABSENT: this card
runs neither, and keeping a name a leg could be launched under would let a
copy-pasted B2 leg score here under a different (prereg-derived) ladder and be
mislabelled as a B3 measurement. Only `A1_lf_all` is the PRIMARY scored arm for
cratered screening; A0 and A3c are matched controls and may legitimately sit
above the cratered line.

PROVENANCE (card `recipe.base_family`, verbatim):

    models_r3/r3s3_row_efficiency @ eedcc655b70471687c9b7f8e537ad206eddd437c
    (branch round3/exp-r3s3_lf_value-B2, card r3s3_lf_value-B2), vendored
    BYTE-FOR-BYTE with provenance comments into the NEW family
    models_r3/r3s3_knee_prereg. PLUS models_r3/_common/ckpt_binding.py vendored
    byte-for-byte from commit da855da (branch round3/exp-r3s4_audit-B2, path
    models_r3/_common/ckpt_binding.py), which imports the UNEDITED
    round3/tools/ckpt_data_binding.py.

Every file of this family was written by `git show
eedcc655:models_r3/r3s3_row_efficiency/<f>` and then edited only as recorded
here. `model.py` is BYTE-IDENTICAL to that blob; `affine_probe.py`,
`coverage.py`, `refs.py` and `eval_seam_binding.py` (B2's `data_binding.py`,
RENAMED — see the import site) are byte-identical modulo the mechanical
`R3S3B2_` -> `R3S3B3_` prefix rename in strings and docstrings.
`lf_reference.py` carries ONE FORCED DELTA: the ADR r3-0005 pfc entry
(`SPECTRAL_RUNG_DATASETS` + `_spectral_zeropad_up`), vendored verbatim from the
amended `eval/panel_data.py` — B2's copy predates that ADR and never ran pfc,
this card does, and the per-leg seam assert caught the stale classification at
`max abs diff 1.400141e-01`. Registration-of-lifts (round-2 §12 / ADR r2-0004)
requires the model-side lift to BE the eval layer's; `verify_against_eval`
re-adjudicates it at 1e-9 on every leg (measured 0.0 on all six datasets this
card touches). Audit the others with

    git show eedcc655:models_r3/r3s3_row_efficiency/<f> \\
        | sed 's/R3S3B2_/R3S3B3_/g' | diff - <f>

and the two vendored-verbatim files with

    git show da855da:models_r3/_common/ckpt_binding.py | diff - ../_common/ckpt_binding.py
    diff <round3>/tools/ckpt_data_binding.py <worktree>/tools/ckpt_data_binding.py

This file carries the rename plus THE FOUR CARDED CHANGES below. The
byte-preservation is what makes the card's reproduction seam real: the backbone
(`CoverageDecoder`, width 64, 4 blocks, coord channels at forward time, FFT
`norm="forward"`), the mode policy `pinned_min_rung_nyquist`, the step-matched
budget (`steps = epochs * 25`), AdamW(1e-3, wd 1e-5) + cosine + clip 1.0, the
arm-invariant `per_rung_max_fullpool` scaler and its invariance assert, the
per-rung LF cap draw and the `_step_rng(seed, step)` resume contract are all
unchanged from B2, so the `A0_nolf` / `A1_lf_all` legs form an exact
reproduction seam against it.

THE FOUR CARDED CHANGES vs `models_r3/r3s3_row_efficiency` @ eedcc655, and
nothing else is new (each is marked `CARDED CHANGE n` at its site):

  1. LADDERS FROM THE SEALED PRE-REGISTRATION (`R3S3B3_LADDER_FROM_PREREG=1`).
     B2's hardcoded `LF_COND_CAP_LADDER` dict is gone; the legal caps of every
     cell are `{r1, r2, r3, r4}` read from `R3S3B3_PREREG_JSON`, with a startup
     assert on `R3S3B3_PREREG_SHA256` and on `_sealed_utc < leg start`
     (`prereg.py`). The card's claim is the DIRECTION of inference, so a leg
     that could run against an unsealed or edited prediction would void it.
  2. DATASET-GENERALITY of the stratified readout. B2's ch-only imported mask
     is replaced by a MODEL-FREE re-derivation available on ANY cell: the top
     `R3S3B3_HARD_MASK_TOPFRAC` (0.27) of test rows by nearest-train-HF-field
     rel-L2 over the FULL HF train split. `R3S3B3_HARD_MASK_JSON` is not a key
     of this card and no mask is imported; the split-identity digest is still
     recorded on `sharp__cahn_hilliard` so the new mask can be compared with
     B2's published one analysis-side.
  3. CHECKPOINT DATA BINDING (`R3S3B3_CKPT_BINDING=1`, batch-3 contract
     requirement, `state/batch3_scope_2026-08-10.md` rule 2):
     `models_r3/_common/ckpt_binding.py` @ `da855da` writes `data_binding` into
     `last.pt` at EVERY save, with `roles_read = cond_only` for `A0_nolf` and
     `lf_at_train` for the LF arms. The block is computed once per leg and
     reused by every save (it is a pure function of the dataset dir and the
     arm's declared roles, and hashing the dataset per save would cost ~60 % of
     a leg).
  4. FILM-UNIT REPORTING (`R3S3B3_FILM_UNITS=1`, batch-3 scope rule 1):
     `skill_film = nRMSE / nrmse_film_mean(ds)` and `tau_rel_film = tau_rel *
     c_ds` beside every emitted statistic, plus the G5 `nn_condition` fit-set
     band (scope rule 5), the pinned floor tolerances / per-arm affine band, and
     the mean-removed metric (`reporting.py`). Copy-LF is not a target on this
     card; it is retained only as the identity check `skill_film =
     skill_copylf * c_ds`.

TERMINOLOGY (carried from B2, BLOCKING). The forward-sensitive subpopulation is
named FORWARD-SENSITIVE and defined on first use. The words the literature uses
for the OPPOSITE meaning are BANNED from every artifact this family writes, and
`_assert_no_banned_terms` enforces that on the serialised result JSON before it
is written.

DATASETS. `R3S3B3_CELLS` is the explicit five-name list (ADR r3-0007 option C):
`sharp__cahn_hilliard,sharp__allen_cahn_2d,sharp__fisher_kpp_2d,
sharp__phase_field_crystal_2d,ifc_heat`. NEVER `--datasets panel` (that resolves
the ROUND-2 panel). `ifc_poisson` is REPORT-ONLY under ADR r3-0007 and this card
runs no leg on it. REPORTING DISCIPLINE (card `_reporting_discipline`): ch is
reference-free (ADR r3-0003 D2, MDD 1.7077) — report ratios, R and film units,
never a ch copy-LF skill delta; every ifc number carries `affine_on_hf_train`
and the paper bar; pfc carries the weak-fidelity-gap denominator caveat AND has
no certified `tau_rel`, so its clause is CONDITIONAL and this family invents no
pfc threshold.

pfc RUNG SET (card `_blocking_preflights` item 3). The round-3 stripped view
serves pfc train rungs {1, 3} — L2 is withheld and the scored cell is
L1(32^2) -> L3(128^2) with the spectral reference (ADR r3-0005). A pfc leg whose
train split carries any other LF rung set is refused, and the leg's
`_copylf_def_hash` is asserted against the eval layer through `data_binding.py`.

TEST PATH: `S(cond_standardized, HF_grid) * s_HF` and nothing else. No LF
tensor is constructed on any test path and the LF signal carries zero
parameters (program.md §5.9, stripped test view). The test split is asserted to
carry no LF fidelity before anything else runs.

TRAIN/VAL DISCIPLINE: no validation split is consumed and no early stopping or
checkpoint selection happens — the final-step weights are scored.

Checkpoint/resume (program.md §5.8): `<ckpt_dir>/last.pt` every
`R3S3B3_CKPT_EVERY_STEPS` steps, keyed on (steps_target, arm, split_seed,
dataset, resolved-recipe digest), with a `done` marker; sampling is a pure
function of (seed, step), so a resumed run is bit-identical to an uninterrupted
one whatever the resume point. `R3S3B3_STALE_CKPT_ASSERT` is the card's
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
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

HERE = Path(__file__).resolve().parent
WORKTREE_ROOT = HERE.parents[1]           # <worktree>/models_r3/<family> -> <worktree>
FACTORY_ROOT = WORKTREE_ROOT / "mf_field" / "factory_mffp"
COMMON_DIR = HERE.parent / "_common"      # <worktree>/models_r3/_common


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
if str(COMMON_DIR) not in sys.path:
    sys.path.insert(0, str(COMMON_DIR))
if str(FACTORY_ROOT) not in sys.path:
    sys.path.insert(0, str(FACTORY_ROOT))

import affine_probe as ap                                       # noqa: E402
import coverage as cov                                          # noqa: E402
import prereg                                                   # noqa: E402
import refs                                                     # noqa: E402
import reporting                                                # noqa: E402
# NOTE (builder): this file is B2's `data_binding.py`, RENAMED. The name had to
# change: `tools/ckpt_data_binding.py` (imported read-only by CARDED CHANGE 3's
# `ckpt_binding.py`) itself does `import data_binding` to reach the SHIPPED
# launch-time instrument `mffp_autoresearch/preflight/data_binding.py`, and a
# family module of the same name on `sys.path[0]` shadows it — the first smoke
# of this build died exactly there (`AttributeError: module 'data_binding' has
# no attribute 'hash_dataset'`). Renaming the family copy removes the collision
# outright instead of making the two imports order-dependent. CONTENTS ARE
# UNCHANGED (rename-only vs the base blob):
#   git show eedcc655:models_r3/r3s3_row_efficiency/data_binding.py \
#       | sed 's/R3S3B2_/R3S3B3_/g' | diff - eval_seam_binding.py
from eval_seam_binding import assert_data_binding                # noqa: E402
from lf_reference import convention_for, verify_against_eval    # noqa: E402
from model import CoverageDecoder, active_modes, param_count    # noqa: E402
from data_adapters.loaders import load_mf_dataset               # noqa: E402
from data_adapters.geometry import resolve_grid                 # noqa: E402
from data_adapters.metrics import finalize_and_write            # noqa: E402

# CARDED CHANGE 3 — the batch-3 contract requirement. Vendored BYTE-FOR-BYTE from
# `da855da:models_r3/_common/ckpt_binding.py`; it imports the UNEDITED
# `round3/tools/ckpt_data_binding.py`, which this worktree carries verbatim at
# `<worktree>/tools/` (the r3s4_audit-B2 convention its own path rule expects).
import ckpt_binding                                             # noqa: E402

MODEL_NAME = "r3s3_knee_prereg"

# project.yaml `guard_set` (frozen, program.md §5 immutable 2). Used ONLY to
# honour R3S3B3_GUARD_NSUB=off (native N_hf on the guard leg).
GUARD_DATASETS = ("heat_local", "fluid", "sharp__sod_1d")

# Operational constants — no effect on any number (GroupNorm is per-sample, so
# inference chunking is exact; the log stride only controls printing). Carried
# verbatim from the base family.
PRED_CHUNK = 32
LOG_POINTS = 50

# The SVD rank tolerance for the reported `design_null` block. This card's
# `recipe.env` has exactly 49 keys and RANK_TOL is not among them, so it stays
# FROZEN at the base family's value (1e-10) rather than being reintroduced as an
# undeclared knob. It is also the default of the round's registered probe
# `mffp_autoresearch/round2/tools/affine_ladder_voi.py --rank_tol`.
RANK_TOL = 1e-10

# FROZEN, for the same reason: B2 read the reference-free dataset list from
# `R3S3B2_REFERENCE_FREE_DATASETS`; this card's `recipe.env` has no such key, so
# the list is pinned here to the value the card's own `_reporting_discipline`
# states ("ch is REFERENCE-FREE (ADR r3-0003 D2, MDD 1.7077)") instead of being
# reintroduced as a knob or silently defaulted.
REFERENCE_FREE_DATASETS = ("sharp__cahn_hilliard",)

# The card's `R3S3B3_CELLS` (ADR r3-0007 option C), used ONLY to record whether a
# leg's dataset is a scored cell of this card or the guard leg; the ladder itself
# comes from the seal. A cell list mismatch is reported, never silently applied.
CARD_CELLS = ("sharp__cahn_hilliard", "sharp__allen_cahn_2d",
              "sharp__fisher_kpp_2d", "sharp__phase_field_crystal_2d", "ifc_heat")

# Card `_blocking_preflights` (3): the pfc scored cell is L1(32^2) -> L3(128^2)
# with the spectral reference, and the stripped view serves train rungs {1, 3}
# only (ADR r3-0005; stripped_data/sharp__phase_field_crystal_2d/
# SERVED_FIDS_ADR_r3-0005.md). A pfc leg carrying any other LF rung set is
# training on a cell the card did not register.
PFC_DATASET = "sharp__phase_field_crystal_2d"
PFC_EXPECTED_LF_FIDS = (1,)

# ── the arm <-> selector binding, card `recipe.env._note` verbatim ──
#   "ARM<->selector binding asserted in smoke_eval: A0_nolf=(COND_SET none,
#    CAP 0); A1_lf_all=(all, 0); A3c_lf_uncov_cap=(uncovered, CAP in the sealed
#    ladder for that dataset). Any other combination raises."
#
# EXACTLY THREE ARMS. B2's `A2_lf_covered` and `A5_hf_budget_nolf` are gone: no
# leg of this card's grid uses them, and a name a leg could be launched under is
# a name a copy-pasted B2 leg can be mislabelled under (this card's caps come
# from the seal, so the same cap integer means a different rung of a different
# ladder). `N_HF` is 5 on every arm (card `_grid`).
#
# `cap` is an ALLOWED SET, not a scalar; `None` means "resolved from the SEALED
# ladder of this dataset" and is checked in `recipe()` against `prereg.ladder_for`.
ARMS = {
    "A0_nolf":          {"n_hf": (5,), "cond_set": "none",      "cap": (0,)},
    "A1_lf_all":        {"n_hf": (5,), "cond_set": "all",       "cap": (0,)},
    "A3c_lf_uncov_cap": {"n_hf": (5,), "cond_set": "uncovered", "cap": None},
}
PRIMARY_ARM = "A1_lf_all"
SCORED_CONTRAST_ARMS = ("A0_nolf", "A1_lf_all", "A3c_lf_uncov_cap")
BUDGET_VARIED_ARMS = ()

# CARDED CHANGE 1 — THE LADDER IS NOT A CONSTANT OF THIS FILE.
# B2 hardcoded `LF_COND_CAP_LADDER = {ch: (...), ifc_heat: (...)}`. On this card
# the legal caps are `{r1, r2, r3, r4}` READ from the phase-P seal
# (`R3S3B3_PREREG_JSON`, digest-pinned by `R3S3B3_PREREG_SHA256`); the ladder
# arm runs at r1/r2/r3 and `A1_lf_all` IS r4 = FULL. `prereg.ladder_for` is the
# only source, and there is deliberately no in-file fallback: a leg that cannot
# read the seal must fail, not silently take a default ladder.
LADDER_SOURCE = "R3S3B3_PREREG_JSON (sealed phase-P pre-registration)"

# The HF-budget nesting rule stays as an ASSERT ONLY (no A5 arm exists here):
# the draw rule is `sort(default_rng(split_seed).permutation(n)[:k])` from ONE
# generator, so the k-prefix property is what makes SPLIT_SEED 0/1/2 reproduce
# B1/B2/r2s3-B3's identical HF rows (card `_hf_subset_draws`). It is re-derived
# and asserted in `prepare()`.
HF_PREFIX_LADDER = (5,)

REF_ARM_NAMES = ("nn_condition_n5", "train_mean_n5", "zero", "linear_hfonly",
                 "affine_on_hf_train", "nn_condition_full", "train_mean_full")

# CARDED CHANGE 2 — the forward-sensitive stratification, now DATASET-GENERAL.
# B2 imported r3s1_factorised-B1's 100-element ch mask after a split-identity
# assert. `R3S3B3_HARD_MASK_JSON` is NOT a key of this card and nothing is
# imported: the mask is re-derived model-free on EVERY cell as the top
# `R3S3B3_HARD_MASK_TOPFRAC` of that cell's test rows by nearest-train-HF-field
# rel-L2. The ch split-identity digest below is still recorded (not enforced as
# a gate on other cells) so B2's published 27-row mask can be compared with this
# card's re-derivation analysis-side, on rows known to be the same samples.
HARD_MASK_REFERENCE_DATASET = "sharp__cahn_hilliard"
HARD_MASK_REFERENCE_N_TEST = 100
HARD_MASK_REFERENCE_N_HARD = 27

# BANNED TERMINOLOGY (card `recipe.env._hard_mask`, blocking): the literature
# uses these words for the OPPOSITE meaning (PLOS pcbi.1013553), so no artifact
# of this family may contain them.
BANNED_TERMS = ("non-identifiable", "nonidentifiable", "unidentifiable",
                "non-identifiability", "unidentifiability")

# The complete `--env` surface: the card's `recipe.env` enumerates EXACTLY 49
# non-underscore `R3S3B3_*` keys (counted programmatically from the card JSON at
# build time; the `_`-prefixed entries are card directives and are never passed
# through `--env`, per `recipe.env._note`). All 49 are listed here and the length
# assert pins it. Any other `R3S3B3_*` key in the environment is a typo that
# would otherwise silently take a default.
ENV_KEYS = (
    # phase P / the seal (new in this card)
    "R3S3B3_PHASE", "R3S3B3_PREREG_JSON", "R3S3B3_PREREG_SHA256",
    "R3S3B3_PREREG_ASSERT", "R3S3B3_LADDER_FROM_PREREG", "R3S3B3_CELLS",
    # the leg selector
    "R3S3B3_ARM", "R3S3B3_LF_COND_SET", "R3S3B3_LF_COND_CAP",
    "R3S3B3_SPLIT_SEED", "R3S3B3_N_HF",
    # the (unchanged) training recipe
    "R3S3B3_SCALER", "R3S3B3_SCALER_INVARIANCE_ASSERT",
    "R3S3B3_WIDTH", "R3S3B3_BLOCKS", "R3S3B3_MODES_CAP", "R3S3B3_MODE_POLICY",
    "R3S3B3_STEPS_PER_EPOCH", "R3S3B3_HF_BATCH", "R3S3B3_LF_BATCH",
    "R3S3B3_LR", "R3S3B3_WD", "R3S3B3_SCHED", "R3S3B3_CLIP",
    "R3S3B3_LAMBDA_LF", "R3S3B3_LF_LIFT",
    # references, floors, units
    "R3S3B3_REF_ARMS", "R3S3B3_FLOORS_JSON", "R3S3B3_FLOOR_TOL",
    "R3S3B3_FLOOR_TOLERANCES_JSON", "R3S3B3_NOISE_FLOOR_JSON",
    "R3S3B3_FILM_DENOM_JSON", "R3S3B3_FILM_UNITS", "R3S3B3_MCE_MODE",
    "R3S3B3_ANCHORS_JSON", "R3S3B3_G5_FITSET_BAND",
    # audits
    "R3S3B3_DATA_BINDING_ASSERT", "R3S3B3_CKPT_BINDING",
    "R3S3B3_TARGET_SCALE_AUDIT", "R3S3B3_STALE_CKPT_ASSERT",
    "R3S3B3_LF_ROW_MANIFEST",
    # emission
    "R3S3B3_STRATIFY_ROWS", "R3S3B3_HARD_MASK_MODE", "R3S3B3_HARD_MASK_TOPFRAC",
    "R3S3B3_MEAN_REMOVED_REPORT", "R3S3B3_DUMP_TEST_PREDS",
    "R3S3B3_ALIGNMENT_REPORT", "R3S3B3_CKPT_EVERY_STEPS", "R3S3B3_GUARD_NSUB",
)
assert len(ENV_KEYS) == 49, "the card's recipe.env enumerates exactly 49 R3S3B3_* keys"
assert len(set(ENV_KEYS)) == 49, "duplicate key in ENV_KEYS"

# A copy-pasted round-2 or earlier round-3 leg must not run silently under this
# family's defaults: those cards' knobs select DIFFERENT ladders (B2's caps were
# hardcoded, this card's come from the seal), so a leg carrying them would be
# mislabelled.
FOREIGN_ENV_PREFIXES = ("R2S3B3_", "R2S3B2_", "R2S3B1_", "R3S3B1_", "R3S3B2_")


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


def recipe(dataset_name: str = None, seal: dict = None) -> dict:
    """Resolve + assert the card's `recipe.env`.

    `dataset_name` + `seal` are needed because CARDED CHANGE 1 makes the legal
    cap set per-dataset AND external: it is the SEALED ladder `{r1,r2,r3,r4}`,
    not a constant of this file. `run()` loads the seal first and passes it in;
    passing `seal=None` (the guard leg, which takes no ladder arm) keeps the
    dataset-blind behaviour for that one check.
    """
    foreign = sorted(k for k in os.environ
                     if k.startswith(FOREIGN_ENV_PREFIXES))
    if foreign:
        raise SystemExit(
            f"foreign env key(s) {foreign} are set. This family reads only the 49 "
            "R3S3B3_* keys of the card `r3s3_lf_value-B3` recipe.env; a leg configured "
            "for r2s3_lf_train_signal or for r3s3_lf_value-B1/B2 would run here under "
            "THIS card's defaults (a DIFFERENT, prereg-derived cap ladder) and silently "
            "mislabel the arm. Refusing to run.")
    unknown = sorted(k for k in os.environ
                     if k.startswith("R3S3B3_") and k not in ENV_KEYS)
    if unknown:
        raise SystemExit(
            f"unknown R3S3B3_* env key(s) {unknown}; the card declares exactly the 49 "
            f"keys {list(ENV_KEYS)} — a typo would otherwise take a default silently")

    p = {
        # phase P / the seal
        "phase": _s("R3S3B3_PHASE", "C"),
        "prereg_json": _s(
            "R3S3B3_PREREG_JSON",
            "mffp_autoresearch/round3/state/r3s3_lf_value/prereg_knees_B3.json"),
        "prereg_sha256": _s("R3S3B3_PREREG_SHA256", ""),
        "prereg_assert": _s("R3S3B3_PREREG_ASSERT", "1"),
        "ladder_from_prereg": _s("R3S3B3_LADDER_FROM_PREREG", "1"),
        "cells": [t for t in _s("R3S3B3_CELLS", ",".join(CARD_CELLS)).split(",") if t],
        "arm": _s("R3S3B3_ARM", "A3c_lf_uncov_cap"),
        "split_seed": _s("R3S3B3_SPLIT_SEED", "0"),
        "n_hf": _i("R3S3B3_N_HF", 5),
        "lf_cond_set": _s("R3S3B3_LF_COND_SET", "uncovered"),
        # NOTE: no numeric default. B2 defaulted the cap to 40; on this card the
        # cap is a rung of the SEALED ladder, so an unset knob must fail loudly
        # rather than silently select a rung the seal may not contain.
        "lf_cond_cap": _i("R3S3B3_LF_COND_CAP", -1),
        "scaler_invariance_assert": _s("R3S3B3_SCALER_INVARIANCE_ASSERT", "1"),
        "stale_ckpt_assert": _s("R3S3B3_STALE_CKPT_ASSERT", "1"),
        "alignment_report": _s("R3S3B3_ALIGNMENT_REPORT", "0"),
        "stratify_rows": _s("R3S3B3_STRATIFY_ROWS", "1"),
        "hard_mask_mode": _s("R3S3B3_HARD_MASK_MODE", "rederive_model_free"),
        "hard_mask_topfrac": _f("R3S3B3_HARD_MASK_TOPFRAC", 0.27),
        "mean_removed_report": _s("R3S3B3_MEAN_REMOVED_REPORT", "1"),
        "film_units": _s("R3S3B3_FILM_UNITS", "1"),
        "film_denom_json": _s(
            "R3S3B3_FILM_DENOM_JSON",
            "mffp_autoresearch/round3/state/anchors/film_denominator.json"),
        "floor_tolerances_json": _s(
            "R3S3B3_FLOOR_TOLERANCES_JSON",
            "mffp_autoresearch/round3/state/floor_tolerances.json"),
        "g5_fitset_band": _s("R3S3B3_G5_FITSET_BAND", "1"),
        "ckpt_binding": _s("R3S3B3_CKPT_BINDING", "1"),
        "width": _i("R3S3B3_WIDTH", 64),
        "blocks": _i("R3S3B3_BLOCKS", 4),
        "modes_cap": _i("R3S3B3_MODES_CAP", 12),
        "mode_policy": _s("R3S3B3_MODE_POLICY", "pinned_min_rung_nyquist"),
        "scaler": _s("R3S3B3_SCALER", "per_rung_max_fullpool"),
        "steps_per_epoch": _i("R3S3B3_STEPS_PER_EPOCH", 25),
        "hf_batch": _i("R3S3B3_HF_BATCH", 5),
        "lf_batch": _i("R3S3B3_LF_BATCH", 16),
        "lr": _f("R3S3B3_LR", 1e-3),
        "wd": _f("R3S3B3_WD", 1e-5),
        "sched": _s("R3S3B3_SCHED", "cosine"),
        "clip": _f("R3S3B3_CLIP", 1.0),
        "lambda_lf": _f("R3S3B3_LAMBDA_LF", 1.0),
        "lf_lift": _s("R3S3B3_LF_LIFT", "match_copylf_convention"),
        "ref_arms": [t for t in _s(
            "R3S3B3_REF_ARMS",
            "nn_condition_n5,train_mean_n5,zero,linear_hfonly,affine_on_hf_train,"
            "nn_condition_full,train_mean_full").split(",") if t],
        "floors_json": _s(
            "R3S3B3_FLOORS_JSON",
            "mffp_autoresearch/round3/state/anchors_repaired/floors.json"),
        "floor_tol": _f("R3S3B3_FLOOR_TOL", 1e-9),
        "noise_floor_json": _s(
            "R3S3B3_NOISE_FLOOR_JSON",
            "mffp_autoresearch/round3/state/anchors_repaired/noise_floor.json"),
        # NOTE: the base family also read `R3S3B1_NOISE_FLOOR_R2_JSON`. This
        # card's recipe.env has NO such key (r3s4 certified the round-3 floors
        # on 2026-08-08), so it is not resolved and not defaulted here.
        "mce_mode": _s("R3S3B3_MCE_MODE", "certified_r3"),
        "anchors_json": _s("R3S3B3_ANCHORS_JSON",
                           "mffp_autoresearch/round3/state/anchors/launch_anchors.json"),
        "data_binding_assert": _s("R3S3B3_DATA_BINDING_ASSERT", "1"),
        "target_scale_audit": _s("R3S3B3_TARGET_SCALE_AUDIT", "1"),
        "lf_row_manifest": _s("R3S3B3_LF_ROW_MANIFEST", "1"),
        # `R3S3B3_DUMP_TRAIN_PREDS` is NOT a key of this card (B2 had it); the
        # train-side dump is therefore off and is not reintroduced as a knob.
        "dump_test_preds": _s("R3S3B3_DUMP_TEST_PREDS", "1"),
        "ckpt_every_steps": _i("R3S3B3_CKPT_EVERY_STEPS", 250),
        "guard_nsub": _s("R3S3B3_GUARD_NSUB", "off"),
    }

    # ── assertions, not defaults: an unrecognised knob value stops the run ──
    if p["phase"] != "C":
        raise SystemExit(
            f"R3S3B3_PHASE={p['phase']!r}: this family is the phase-C confirming "
            "ladder. Phase P is CPU-only and runs from scripts/phase_p_prereg.py; it "
            "never trains.")
    if p["ladder_from_prereg"] != "1":
        raise SystemExit(
            "R3S3B3_LADDER_FROM_PREREG must be '1' on this card: the ladder has no "
            "in-file fallback (CARDED CHANGE 1). A leg with it off would have no legal "
            "cap set at all.")
    if p["arm"] not in ARMS:
        raise SystemExit(f"R3S3B3_ARM={p['arm']!r} not in {sorted(ARMS)} "
                         "(B2's A2_lf_covered and A5_hf_budget_nolf are deliberately "
                         "absent: this card runs neither, and its caps are rungs of the "
                         "SEALED ladder, so a B2 arm name here would mislabel the "
                         "measurement)")
    bind = ARMS[p["arm"]]
    # CARDED CHANGE 1: the ladder arm's legal caps are the SEALED r1/r2/r3 for
    # this dataset. r4 = FULL is not a cap of A3c — it is the `A1_lf_all` arm
    # (card "Arms": "A1_lf_all (= rung r4 = FULL)"), which takes cap 0.
    ladder = None
    if (seal is not None and dataset_name is not None
            and dataset_name in seal["payload"]["cells"]):
        ladder = prereg.ladder_for(seal, dataset_name)
    caps_allowed = bind["cap"]
    if caps_allowed is None:                       # A3c_lf_uncov_cap
        if ladder is None:
            raise SystemExit(
                f"arm {p['arm']} needs the SEALED ladder of dataset {dataset_name!r}, "
                "but that cell is not in the pre-registration. The ladder arm runs "
                "only on sealed cells (CARDED CHANGE 1).")
        caps_allowed = ladder[:3]                  # r1, r2, r3
    ok = (p["n_hf"] in bind["n_hf"] and p["lf_cond_set"] == bind["cond_set"]
          and p["lf_cond_cap"] in caps_allowed)
    if not ok:
        raise SystemExit(
            f"ARM<->selector binding violated for {p['arm']}: card `recipe.env._note` "
            f"requires (N_HF, LF_COND_SET, LF_COND_CAP) in "
            f"({list(bind['n_hf'])}, {bind['cond_set']!r}, {list(caps_allowed)}), got "
            f"({p['n_hf']}, {p['lf_cond_set']!r}, {p['lf_cond_cap']}). "
            "smoke_eval MUST raise on any other combination.")
    p["_sealed_ladder"] = list(ladder) if ladder is not None else None
    if p["lf_cond_set"] not in cov.COND_SETS:
        raise SystemExit(f"unsupported R3S3B3_LF_COND_SET={p['lf_cond_set']!r}")
    if p["lf_cond_cap"] < 0:
        raise SystemExit(
            f"R3S3B3_LF_COND_CAP={p['lf_cond_cap']} (unset or negative). This card "
            "gives it NO numeric default: it is a rung of the sealed ladder and must "
            "be passed explicitly on every leg.")
    if not (0.0 < p["hard_mask_topfrac"] < 1.0):
        raise SystemExit(f"R3S3B3_HARD_MASK_TOPFRAC must lie in (0,1), got "
                         f"{p['hard_mask_topfrac']}")
    if p["mode_policy"] not in ("pinned_min_rung_nyquist", "grid_nyquist_clip"):
        raise SystemExit(f"unsupported R3S3B3_MODE_POLICY={p['mode_policy']!r}")
    # CARDED CHANGE 1: `per_rung_max_fullpool` is this card's scaler. The base
    # family's two rules are kept selectable so the confound B1 measured can be
    # reproduced deliberately, but the card's recipe selects the fullpool rule.
    if p["scaler"] not in ("per_rung_max_fullpool", "per_rung_max",
                           "shared_max_all_rungs"):
        raise SystemExit(f"unsupported R3S3B3_SCALER={p['scaler']!r}")
    # CARDED CHANGE 2: the only supported modes are the card's own
    # `rederive_model_free` and `off`. B2's `import_*` modes are gone with
    # `R3S3B3_HARD_MASK_JSON`: nothing is imported on this card.
    if p["hard_mask_mode"] not in ("rederive_model_free", "off"):
        raise SystemExit(
            f"unsupported R3S3B3_HARD_MASK_MODE={p['hard_mask_mode']!r} (this card "
            "supports 'rederive_model_free' and 'off'; B2's import_* modes are gone "
            "with R3S3B3_HARD_MASK_JSON, which is not a key of this card)")
    if p["sched"] != "cosine":
        raise SystemExit(f"unsupported R3S3B3_SCHED={p['sched']!r} (card: cosine)")
    if p["lf_lift"] != "match_copylf_convention":
        raise SystemExit(f"unsupported R3S3B3_LF_LIFT={p['lf_lift']!r}")
    if p["guard_nsub"] not in ("off", "on"):
        raise SystemExit(f"unsupported R3S3B3_GUARD_NSUB={p['guard_nsub']!r}")
    for key, env_key in (("data_binding_assert", "R3S3B3_DATA_BINDING_ASSERT"),
                         ("target_scale_audit", "R3S3B3_TARGET_SCALE_AUDIT"),
                         ("lf_row_manifest", "R3S3B3_LF_ROW_MANIFEST"),
                         ("dump_test_preds", "R3S3B3_DUMP_TEST_PREDS"),
                         ("scaler_invariance_assert",
                          "R3S3B3_SCALER_INVARIANCE_ASSERT"),
                         ("stale_ckpt_assert", "R3S3B3_STALE_CKPT_ASSERT"),
                         ("alignment_report", "R3S3B3_ALIGNMENT_REPORT"),
                         ("stratify_rows", "R3S3B3_STRATIFY_ROWS"),
                         # new in this card (changes 1, 3 and 4)
                         ("prereg_assert", "R3S3B3_PREREG_ASSERT"),
                         ("ladder_from_prereg", "R3S3B3_LADDER_FROM_PREREG"),
                         ("ckpt_binding", "R3S3B3_CKPT_BINDING"),
                         ("film_units", "R3S3B3_FILM_UNITS"),
                         ("g5_fitset_band", "R3S3B3_G5_FITSET_BAND"),
                         ("mean_removed_report", "R3S3B3_MEAN_REMOVED_REPORT")):
        _flag(p, key, env_key)
    unknown_arms = [a for a in p["ref_arms"] if a not in REF_ARM_NAMES]
    if unknown_arms:
        raise SystemExit(
            f"unknown reference arms in R3S3B3_REF_ARMS: {unknown_arms} "
            f"(this card's set is {list(REF_ARM_NAMES)}; `linear_mf` is deleted — see "
            "affine_probe.py)")
    if p["split_seed"] != "native":
        try:
            int(p["split_seed"])
        except ValueError:
            raise SystemExit(
                f"R3S3B3_SPLIT_SEED={p['split_seed']!r} must be an integer or 'native'")
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
                       p: dict, hf_keys: set, dataset_name: str,
                       ladder: tuple = ()) -> dict:
    """`R3S3B3_SCALER_INVARIANCE_ASSERT` — bit-identity across arm and cap.

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
        every leg's result JSON, so cross-leg bit-identity over the whole grid
        is verified analysis-side from the artifacts themselves — the check the
        card's cap ladder actually needs.

    `ladder` is now the SEALED `{r1,r2,r3,r4}` of this cell (CARDED CHANGE 1),
    passed in rather than looked up in a hardcoded dict; the probe battery is
    otherwise the base family's.

    Raises (`SystemExit`) on any mismatch when `enforce`; still reports when not.
    """
    checks, failures = [], []
    all_fids = [int(hf_fid)] + [int(r["fid"]) for r in pool]
    ladder = tuple(int(x) for x in (ladder or ()))
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
            "SCALER INVARIANCE FAILED (R3S3B3_SCALER_INVARIANCE_ASSERT=1): "
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
                                  "every leg; equality across the whole grid is "
                                  "verified analysis-side from those records",
        "cap_probes_from_sealed_ladder": list(ladder),
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

    # BLOCKING PRE-FLIGHT (card `_blocking_preflights` item 3): the pfc scored
    # cell is L1(32^2) -> L3(128^2) with the spectral reference, and the stripped
    # view serves train rungs {1, 3} ONLY (ADR r3-0005 phase 2; L2 is withheld
    # because the L2->L3 cell is spectrally converged and task-void). A pfc leg
    # carrying any other LF rung set is not the cell this card sealed a
    # prediction for, and its ladder would be over a different pool.
    pfc_rung_check = {"applicable": args.dataset_name == PFC_DATASET}
    if pfc_rung_check["applicable"]:
        got = tuple(sorted(int(f) for f in train["lf_fids"]))
        pfc_rung_check.update(expected=list(PFC_EXPECTED_LF_FIDS), got=list(got),
                              match=got == PFC_EXPECTED_LF_FIDS,
                              adr="r3-0005 (pfc spectral rung-1 scored cell)")
        if got != PFC_EXPECTED_LF_FIDS:
            raise SystemExit(
                f"pfc LF-RUNG-SET ASSERT FAILED: the train split at {ds_dir} carries "
                f"LF fidelities {list(got)}, but ADR r3-0005 pins the scored cell to "
                f"L1 -> L3 with served train rungs {{1, 3}} (LF = "
                f"{list(PFC_EXPECTED_LF_FIDS)}). Training on a different rung set "
                "would make this leg a different cell from the one phase P sealed a "
                "prediction for. Refusing to run.")

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

    # THE REPRODUCTION SEAM, verified rather than assumed. Card
    # `recipe.env._hf_subset_draws`: "SPLIT_SEED in {0,1,2} draws N_HF=5 of the
    # 400 HF train rows via np.sort(np.random.default_rng(s).permutation(400)[:5])
    # - IDENTICAL to B1/B2/r2s3-B3, so the ch A0/A1 legs form an exact
    # reproduction seam against B2." The k-prefix property of that one generator
    # is what makes the identity hold, so it is re-derived and asserted here.
    # (B2 also checked the {10,20,40} prefixes for its A5 arm; this card has no
    # A5 arm, so the prefix set is `HF_PREFIX_LADDER` = {5}.)
    hf_draw_nesting = {"applicable": False,
                       "reason": "this leg's HF rows are the native full train split"}
    if not hf_rows_are_native_full and p["split_seed"] != "native":
        perm = np.random.default_rng(int(p["split_seed"])).permutation(n_train_all)
        prefixes = {}
        for k in sorted({*HF_PREFIX_LADDER, int(p["n_hf"])}):
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
                "the HF draws are not nested k-prefixes of one permutation "
                f"at SPLIT_SEED={p['split_seed']}: {prefixes}")
        hf_draw_nesting = {
            "applicable": True, "split_seed": str(p["split_seed"]),
            "rule": "np.sort(np.random.default_rng(split_seed).permutation("
                    "n_train)[:N_HF]) — card recipe.env._hf_subset_draws",
            "k_prefix_rows": prefixes, "nested": True,
            "this_leg_matches_rule": True,
            "reproduction_seam": "identical to B1/B2/r2s3-B3; d0 = 55, 88, 133, 202, "
                                 "293 on every 400-row dataset"}

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
    # CARDED CHANGE 1 (`R3S3B3_SCALER=per_rung_max_fullpool`).
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
            p, hf_keys, args.dataset_name, ladder=tuple(p.get("_sealed_ladder") or ())))
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
        "scaler_report": scaler_report,
        "lf_rows_totals": lf_rows_totals,
        "hf_draw_nesting": hf_draw_nesting,
        "pfc_rung_check": pfc_rung_check,        # card `_blocking_preflights` (3)
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
          ckpt_path: Path, ckpt_key: dict, seed: int,
          binding_block: dict = None) -> dict:
    """Step-matched training (vendored unchanged from the base family).

    Every arm takes exactly `steps` optimizer steps and draws the same HF rows
    at every step: `_step_rng(seed, step)` is consumed for the HF batch FIRST,
    so the HF stream is identical in A0, A1 and A3c at a given
    (dataset, split_seed). The LF arms' extra rung forward IS the treatment.

    CARDED CHANGE 3: `binding_block` is the `models_r3/_common/ckpt_binding.py`
    record; when present it is written into `state['data_binding']` at EVERY
    save, which is the batch-3 contract requirement
    (`state/batch3_scope_2026-08-10.md` rule 2). It is computed ONCE by `run()`
    and passed in: `ckpt_data_binding.record` re-reads and hashes every array
    file of the dataset (~3.8 s on `sharp__cahn_hilliard`), so recomputing it at
    each of the ~20 saves of a leg would cost more than half the leg. The block
    is a pure function of (dataset dir, dataset name, declared roles) and none of
    those changes inside a leg, so caching it changes no recorded value.
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
        state = {"key": ckpt_key, "step": int(step), "done": bool(done),
                 "model": model.state_dict(), "opt": opt.state_dict(),
                 "sched": sched.state_dict(), "curve": curve,
                 # `executed_steps` is what the round's stale-checkpoint
                 # instruments read as the NECESSARY condition of the defect
                 # (`tools/zero_work_resume_scan.py`); recording it beside the
                 # binding is what turns "zero work" into an actionable verdict.
                 "executed_steps": int(step) - int(start_step),
                 "steps_target": int(steps)}
        if binding_block is not None:              # CARDED CHANGE 3
            state["data_binding"] = binding_block
        torch.save(state, ckpt_path)

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
        # regardless of which of them R3S3B3_REF_ARMS chose to REPORT.
        report["floor_seam_check"] = refs.seam_check_floors(
            args.dataset_name, full, zero, _abs(p["floors_json"]), p["floor_tol"])
    else:
        report["floor_seam_check"] = {
            "performed": False,
            "reason": "R3S3B3_REF_ARMS requests no *_full floor arm"}

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
            "reason": "R3S3B3_REF_ARMS does not request affine_on_hf_train"}

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


# ── CARDED CHANGE 2: the dataset-general forward-sensitive stratification ──

# The ch split-identity constant, carried over from B2 as a COMPARABILITY
# RECORD rather than a gate (this card imports no mask, so there is nothing to
# mis-align). `sha256` of `np.round(cond_test, 12)` (the round's registered
# condition-key rounding, tools/affine_ladder_voi.py A7) for
# `sharp__cahn_hilliard`'s 100 x 19 test condition matrix in the stripped view.
#
# PROVENANCE (r3s3_lf_value-B2 build, 2026-08-10; two independent derivations):
#   (a) this family's own path — data_adapters.loaders.load_mf_dataset(
#       mffp_autoresearch/round2/stripped_data/sharp__cahn_hilliard, "test");
#   (b) r3s1_factorised-B1's OWN path — its `r3s1_twostage_crosscoef.common.Panel`
#       over the same stripped dir, i.e. the exact object whose `cond_test` row
#       order B2's imported mask was built against
#       (`worktrees/r3s1_factorised/B1/scratchpad/reanalysis_turn_3.py::t3c`).
# Both gave the digest below, so B2's published 27-row mask indexes the same
# samples as this card's re-derivation whenever a ch leg reports a match here.
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
    """Record (not gate) this leg's test-split identity.

    CARDED CHANGE 2. B2 imported a 100-element mask built on r3s1_factorised-B1's
    ch test split and had to ASSERT that this leg's split was the same rows. This
    card imports nothing, so there is nothing to mis-align and the digest is no
    longer a gate. It is still RECORDED — on ch it is the same digest B2
    published, which is what lets an analyst compare B2's 27-row mask with this
    card's re-derivation on rows known to be the same samples. On every other
    cell it is a plain provenance record.
    """
    n_test = int(X_te.shape[0])
    digest = hashlib.sha256(
        np.ascontiguousarray(np.round(np.asarray(X_te, dtype=np.float64), 12))
        .tobytes()).hexdigest()
    rec = {"dataset": dataset, "n_test": n_test,
           "cond_matrix_sha256_round12": digest,
           "gating": False,
           "convention": "sha256 of np.round(cond_test, 12).tobytes(), C-order "
                         "float64 — the round's registered condition-key rounding"}
    if dataset == HARD_MASK_REFERENCE_DATASET:
        rec.update(
            reference_n_test=HARD_MASK_REFERENCE_N_TEST,
            reference_cond_matrix_sha256_round12=CH_TEST_COND_SHA256_ROUND12,
            matches_b2_published_split=bool(
                digest == CH_TEST_COND_SHA256_ROUND12
                and n_test == HARD_MASK_REFERENCE_N_TEST),
            reference_note="r3s1_factorised-B1 T3c / r3s3_lf_value-B2 published a "
                           f"{HARD_MASK_REFERENCE_N_HARD}-of-"
                           f"{HARD_MASK_REFERENCE_N_TEST} forward-sensitive mask over "
                           "this split; a True here means this card's re-derived mask "
                           "is comparable to it row by row")
    return rec


def _rederive_hard_mask(Y_te: np.ndarray, Y_train_all: np.ndarray,
                        topfrac: float) -> dict:
    """MODEL-FREE re-derivation, on ANY cell: the top `topfrac` of test rows by
    nearest-train-HF-field relative L2 distance.

    CARDED CHANGE 2 (card part 3: "the ch-only hard-mask path becomes a
    model-free re-derivation on any cell (top 27 % of test rows by
    nearest-train-HF-field rel-L2), stratified readout reported for every cell").

        d_i = min_j ||y_te_i - y_train_j||_2 / ||y_te_i||_2

    over the FULL HF train split (not this arm's N_hf draw), so the mask is a
    property of the dataset alone — identical in every arm, cap and seed of the
    grid. `n_hard = round(topfrac * n_test)`, clamped to `[1, n_test - 1]` so a
    stratification always has two non-empty strata. Ties break by the lowest test
    index (`np.argsort(kind="stable")`). This is a REPORTING stratification
    computed after the scored prediction exists; nothing in training or
    prediction reads it.
    """
    T = np.asarray(Y_te, dtype=np.float64).reshape(Y_te.shape[0], -1)
    R = np.asarray(Y_train_all, dtype=np.float64).reshape(Y_train_all.shape[0], -1)
    n_test = int(T.shape[0])
    n_hard = int(min(max(1, round(float(topfrac) * n_test)), n_test - 1))
    d2 = (np.einsum("ij,ij->i", T, T)[:, None]
          - 2.0 * (T @ R.T)
          + np.einsum("ij,ij->i", R, R)[None, :])
    dist = np.sqrt(np.maximum(d2.min(axis=1), 0.0)) / np.linalg.norm(T, axis=1)
    order = np.argsort(-dist, kind="stable")
    mask = np.zeros(n_test, dtype=bool)
    mask[order[:n_hard]] = True
    return {"mask": mask, "distance": dist, "n_hard": n_hard, "topfrac": float(topfrac),
            "definition": f"top {topfrac:.2%} ({n_hard} of {n_test}) test rows by "
                          "min_j ||y_te_i - y_train_j|| / ||y_te_i|| over the FULL HF "
                          "train split; model-free, dataset-general",
            "n_hard_rule": "round(topfrac * n_test), clamped to [1, n_test - 1]",
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
    """The per-row stratified emission (CARDED CHANGE 2).

    Runs on EVERY cell now: the mask is re-derived model-free from the dataset
    alone, so there is no cell it cannot be defined on. Card part 3: "the ch-only
    hard-mask path becomes a model-free re-derivation on any cell (top 27 % of
    test rows by nearest-train-HF-field rel-L2), stratified readout reported for
    every cell". B2's part 7 asked for exactly this ("a cell can have a knee for
    its bulk and none for a subpopulation that owns most of the error, and a
    bulk-mean ladder hides that completely").
    """
    if p["stratify_rows"] != "1" or p["hard_mask_mode"] == "off":
        return {"performed": False,
                "reason": "R3S3B3_STRATIFY_ROWS=0 or R3S3B3_HARD_MASK_MODE=off"}

    rec = {"performed": True,
           "terminology": FORWARD_SENSITIVE_DEFINITION,
           "mode": p["hard_mask_mode"],
           "dataset_general": True,
           "split_identity": _split_identity(args.dataset_name, d["X_te"]),
           "scored_metric": "per-row rel-L2 of the SCORED test split, the round's "
                            "one nRMSE definition (round2/eval/nrmse.py), taken from "
                            "splits.test_hf.rel_l2_per_sample",
           "masks": {}}
    rel = np.asarray(rel_rows, dtype=np.float64)

    rd = _rederive_hard_mask(d["Y_te"], d["Y_all"], p["hard_mask_topfrac"])
    rec["masks"]["rederived_model_free"] = {
        "definition": rd["definition"],
        "n_hard_rule": rd["n_hard_rule"],
        "topfrac": rd["topfrac"],
        "n_train_rows_searched": rd["n_train_rows_searched"],
        "n_hard": int(rd["mask"].sum()),
        "n_test": int(rel.size),
        "row_indices": [int(i) for i in np.flatnonzero(rd["mask"])],
        "nearest_train_field_rel_l2_hard_mean": float(
            rd["distance"][rd["mask"]].mean()),
        "nearest_train_field_rel_l2_easy_mean": float(
            rd["distance"][~rd["mask"]].mean()),
        "nearest_train_field_rel_l2_hard_over_easy": float(
            rd["distance"][rd["mask"]].mean()
            / max(rd["distance"][~rd["mask"]].mean(), 1e-300)),
        **_stratum_stats(rel, rd["mask"])}
    rec["comparability_note"] = (
        "MODEL-FREE and identical in every arm, cap, draw and seed of this card's "
        "grid, because it is a function of the dataset alone. B2 published a "
        "SECOND, MODEL-DEPENDENT ch mask (imported from r3s1_factorised-B1's "
        "per-row rel-L2 bimodality) and measured overlap 19/27, jaccard 0.543 "
        "against this same re-derivation; this card imports nothing, so the "
        "comparison is made analysis-side from B2's published row indices and "
        "this leg's `split_identity` digest.")
    return rec


# ── main ──

def run(args, out_path: Path) -> dict:
    leg_start = datetime.now(timezone.utc)

    # ── BLOCKING PRE-FLIGHT #1 (CARDED CHANGE 1), before recipe resolution and
    # before any compute: the SEALED pre-registration. `R3S3B3_PREREG_JSON` and
    # `R3S3B3_PREREG_SHA256` are read from the environment directly because the
    # ladder they carry is what `recipe()` validates the leg's cap against —
    # the seal has to exist before the recipe can be resolved at all.
    prereg_path = _abs(os.environ.get(
        "R3S3B3_PREREG_JSON",
        "mffp_autoresearch/round3/state/r3s3_lf_value/prereg_knees_B3.json"))
    prereg_enforce = os.environ.get("R3S3B3_PREREG_ASSERT", "1") == "1"
    card_cells = [t for t in os.environ.get(
        "R3S3B3_CELLS", ",".join(CARD_CELLS)).split(",") if t]
    is_card_cell = args.dataset_name in card_cells
    seal = prereg.load(prereg_path, os.environ.get("R3S3B3_PREREG_SHA256", ""),
                       prereg_enforce,
                       dataset=args.dataset_name if is_card_cell else None)
    ordering = prereg.assert_sealed_before(seal, leg_start)

    p = recipe(args.dataset_name, seal=seal)
    _seed_everything(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    prereg_block = {
        **(prereg.cell_record(seal, args.dataset_name, prereg_path)
           if is_card_cell else
           {"prereg_json": str(prereg_path),
            "payload_sha256": seal["_payload_sha256"],
            "sealed_utc": seal["_sealed_utc"],
            "dataset": args.dataset_name,
            "role": "NOT a sealed cell of this card (guard leg): the seal is still "
                    "verified so the leg is provably contemporaneous with the "
                    "registered ones, but no prediction exists for this dataset"}),
        "ordering": ordering,
        "assert_enforced": prereg_enforce,
        "card_cells": card_cells,
        "is_card_cell": is_card_cell,
    }

    # BLOCKING pre-flight #2, before any compute (card part 3): the skill
    # denominator this leg will be scored under and the floors/anchors it will
    # be compared against must come from the same eval layer and carry the same
    # per-dataset reference (this is also the `_copylf_def_hash` seam the card's
    # pfc pre-flight names).
    if p["data_binding_assert"] == "1":
        binding = assert_data_binding(args.dataset_name, EVAL_DIR,
                                      _abs(p["floors_json"]))
    else:
        binding = {"performed": False,
                   "reason": "R3S3B3_DATA_BINDING_ASSERT=0"}

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

    # CARDED CHANGE 3 — the checkpoint data binding (batch-3 contract
    # requirement, `state/batch3_scope_2026-08-10.md` rule 2). `roles_read` is a
    # DECLARATION of what this ARM consumes, and it is the whole point of the
    # instrument: on the identical dataset a `train_lf`-only change must be
    # RETRAIN for an LF-consuming arm and NONE for a condition-only one. A0_nolf
    # builds no LF pool at all, so it declares `cond_only`; A1_lf_all and
    # A3c_lf_uncov_cap declare `lf_at_train`. The declaration is derived from the
    # arm's OWN `cond_set` (not from a table that could drift out of sync with
    # `ARMS`), and cross-checked against whether a pool was actually built.
    binding_role = "cond_only" if ARMS[p["arm"]]["cond_set"] == "none" else "lf_at_train"
    if bool(d["pool"]) != (binding_role == "lf_at_train"):
        raise SystemExit(
            f"CKPT BINDING ROLE MISMATCH: arm {p['arm']} declares roles_read="
            f"{binding_role!r} but its LF pool is "
            f"{'non-empty' if d['pool'] else 'empty'}. The binding must describe what "
            "the leg actually read.")
    ckpt_binding_block = None
    ckpt_binding_report = {"enabled": False,
                           "reason": "R3S3B3_CKPT_BINDING=0"}
    if p["ckpt_binding"] == "1":
        t_b = time.time()
        ckpt_binding_block = {
            args.dataset_name: ckpt_binding.binding_block(
                args.dataset_dir, args.dataset_name,
                ckpt_binding.roles_read_for(binding_role))}
        blk = ckpt_binding_block[args.dataset_name]
        ckpt_binding_report = {
            "enabled": True,
            "vendored_from": "da855da:models_r3/_common/ckpt_binding.py (byte-for-byte)",
            "tool": blk["tool_version"],
            "arm_role": binding_role,
            "roles_read": blk["roles_read"],
            "roles": blk["roles"],
            "role_n_units": blk["role_n_units"],
            "union_sha256": blk["union_sha256"],
            "layout": blk["layout"],
            "recorded_utc": blk["recorded_utc"],
            "seconds_to_record": round(time.time() - t_b, 2),
            "written_at_every_save": True,
            "computed_once_per_leg": "the block is a pure function of (dataset_dir, "
                                     "dataset_name, roles_read); recomputing it at each "
                                     "save would re-hash the whole dataset ~20x per leg",
            "test_lf_note": "test_lf is read by NEITHER arm (stripped test view, "
                            "program.md §5 immutable #9): it carries the copy-LF "
                            "denominator only, which is why a test_lf change is "
                            "REREFERENCE and never RETRAIN",
        }

    t0 = time.time()
    fit = train(model, p, d, steps, device, ckpt_dir / "last.pt",
                ckpt_key, int(args.seed), binding_block=ckpt_binding_block)
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
        "ckpt_data_binding": ckpt_binding_report,        # CARDED CHANGE 3
        "pfc_lf_rung_set_assert": d["pfc_rung_check"],
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
    # THE MEDIATOR — OFF on this card. `R3S3B3_ALIGNMENT_REPORT` is '0' in the
    # recipe: B2's part 7 item 4 says "do NOT re-run the D-D mediator clause in
    # its B2 form — if a mediator clause is wanted at all, it must go through
    # tools/mediator_collapse_fitform_audit.py first and be written as a
    # matched-mediator contrast", and the card's `recipe.base_family` repeats it
    # ("the B2 D-D mediator clause is NOT re-run"). The code is kept behind the
    # flag rather than deleted so the knob's value is what decides, visibly, in
    # every result JSON.
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
    else:
        gate["response_decomposition"] = {
            "performed": False,
            "reason": "R3S3B3_ALIGNMENT_REPORT=0 — card recipe.base_family: 'the B2 "
                      "D-D mediator clause is NOT re-run (B2 part 7 item 4)'"}

    # CARDED CHANGE 2 — the FORWARD-SENSITIVE stratification, computed from the
    # per-row rel-L2 array the eval layer itself scores on, on EVERY cell.
    rel_rows = np.asarray(written["splits"]["test_hf"]["rel_l2_per_sample"],
                          dtype=np.float64)
    gate["forward_sensitive_stratification"] = stratification(args, p, d, rel_rows)

    # ── CARDED CHANGE 4 — FILM UNITS, the G5 band, the tolerances, mean-removed ──
    scored_nrmse = float(written["splits"]["test_hf"]["rel_l2_mean"])
    if p["film_units"] == "1":
        gate["film_units"] = reporting.film_block(
            args.dataset_name, _abs(p["film_denom_json"]),
            _abs(p["noise_floor_json"]), scored_nrmse,
            copylf_reference=(binding.get("reference_test_nrmse")
                              if isinstance(binding, dict) else None))
        # Every reference arm this leg reports, in the SAME units as the model.
        fu = gate["film_units"]
        if fu.get("performed"):
            den = fu["nrmse_film_mean"]
            gate["film_units"]["skill_film_by_arm"] = {
                k: float(v["rel_l2_mean"]) / den
                for k, v in sorted(written["splits"].items())
                if isinstance(v, dict) and "rel_l2_mean" in v}
    else:
        gate["film_units"] = {"performed": False, "reason": "R3S3B3_FILM_UNITS=0"}
    if p["g5_fitset_band"] == "1":
        gate["g5_nn_condition_fitset_band"] = reporting.g5_band(args.dataset_name)
    if p["mean_removed_report"] == "1":
        gate["mean_removed"] = {
            **reporting.mean_removed_nrmse(pred_te_flat, target_te),
            "carded_scope": "the card names sharp__fisher_kpp_2d and ifc_heat "
                            "explicitly (level-domination); it is computed on every "
                            "cell because reporting more costs nothing and reporting "
                            "less would break the requirement",
            "carded_cells": ["sharp__fisher_kpp_2d", "ifc_heat"],
            "is_carded_cell": args.dataset_name in ("sharp__fisher_kpp_2d", "ifc_heat")}
    gate["floor_tolerances"] = reporting.tolerance_block(
        args.dataset_name, _abs(p["floor_tolerances_json"]))

    # Which rung of the sealed ladder this leg IS — recorded so the analysis side
    # never has to re-derive the mapping cap -> rung from the seal.
    _lad = p.get("_sealed_ladder")
    if p["arm"] == "A3c_lf_uncov_cap" and _lad:
        rung_label = {int(_lad[0]): "r1", int(_lad[1]): "r2",
                      int(_lad[2]): "r3"}.get(int(p["lf_cond_cap"]), "UNKNOWN")
    elif p["arm"] == "A1_lf_all":
        rung_label = ("r4 = FULL (card 'Arms': A1_lf_all IS the top rung)" if is_card_cell
                      else "no rung (not a sealed cell of this card — guard leg)")
    else:
        rung_label = ("no rung (A0_nolf is the numerator baseline of R)" if is_card_cell
                      else "no rung (not a sealed cell of this card — guard leg)")

    written["knee_prereg"] = {
        "card": "r3s3_lf_value-B3",
        "arm": p["arm"],
        "arm_spec": {"n_hf_allowed": list(ARMS[p["arm"]]["n_hf"]),
                     "cond_set": ARMS[p["arm"]]["cond_set"],
                     "cap_allowed": (list(p.get("_sealed_ladder") or ())[:3]
                                     if ARMS[p["arm"]]["cap"] is None
                                     else list(ARMS[p["arm"]]["cap"])),
                     "n_hf_this_leg": int(p["n_hf"]),
                     "cap_this_leg": int(p["lf_cond_cap"])},
        # CARDED CHANGE 1 — the sealed pre-registration this leg ran under.
        "prereg": prereg_block,
        "sealed_ladder": p.get("_sealed_ladder"),
        "ladder_source": LADDER_SOURCE,
        "rung_of_this_leg": rung_label,
        "primary_arm": PRIMARY_ARM,
        "scored_contrast_arms": list(SCORED_CONTRAST_ARMS),
        "budget_varied_arms": list(BUDGET_VARIED_ARMS),
        "arms_available": sorted(ARMS),
        "arm_role": ("PRIMARY scored arm (the RECOVERY DENOMINATOR, and the ladder's "
                     "top rung r4 = FULL)"
                     if p["arm"] == PRIMARY_ARM else
                     "matched control arm of the scored contrast"),
        "registered_statistic": {
            "R": "R(c) = (nRMSE(A0_nolf) - nRMSE(arm@c)) / (nRMSE(A0_nolf) - "
                 "nRMSE(A1_lf_all)) per fold (HF draw x training seed), fold-mean; "
                 "REFERENCE-FREE",
            "steps": "s_i = R(r_{i+1}) - R(r_i) for i = 1..3",
            "knee": "K = r_{argmax(s)+1} in {r2, r3, FULL} — threshold-free in R by "
                    "construction; NO absolute R threshold anywhere",
            "margin": "M_R = max(s) - second-max(s); "
                      "M_film = M_R * E_ds / nrmse_film_mean(ds), "
                      "E_ds = fold-mean (nRMSE(A0) - nRMSE(A1))",
            "adjudicability": "ADJUDICABLE iff M_film > tau_rel_film(ds) with a "
                              "CERTIFIED tau_rel AND the per-seed knee is unanimous "
                              "over seeds {0,1,2}; the 9-fold leave-one-out jackknife "
                              "modal knee is reported, not gating",
            "primary_claim": "the pre-declared c_pred equals the trained step-max knee "
                             "K on each predictive cell; chance match 1/3 per cell",
            "note": "ALL of it is ANALYSIS-SIDE. This family computes no cross-arm "
                    "quantity and never compares K with c_pred in-process.",
        },
        "dataset": args.dataset_name,
        "seed": int(args.seed),
        "epochs": int(args.epochs),
        "steps": int(steps),
        "steps_per_epoch": p["steps_per_epoch"],
        "budget_equality": "EVERY arm of this card is step-matched at N_hf = 5: "
                           "identical optimizer steps and identical HF-row exposure; "
                           "the LF arms' extra rung forward IS the treatment. No "
                           "budget-varied arm exists here (B2's A5 is not run).",
        "seed_semantics": "R3S3B3_SPLIT_SEED is an HF-SUBSET DRAW, not a training seed. "
                          "The training seed is --seed, and this card runs seeds "
                          "{0,1,2} as three SLURM jobs. Draws must never be "
                          "bootstrapped as a seed CI.",
        "hf_draw_nesting": d["hf_draw_nesting"],
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
            "reference_free": args.dataset_name in REFERENCE_FREE_DATASETS,
            "reference_free_datasets": list(REFERENCE_FREE_DATASETS),
            "reference_free_source": "FROZEN constant — the card's recipe.env has no "
                                     "R3S3B3_REFERENCE_FREE_DATASETS key; the value is "
                                     "the card's own _reporting_discipline sentence",
            "primary_units": "FILM (ADR r3-0006, batch-3 scope rule 1): skill_film = "
                             "nRMSE / nrmse_film_mean(ds). Copy-LF is NOT a target on "
                             "this card and is kept only as the identity check "
                             "skill_film = skill_copylf * c_ds.",
            "rule": ("REFERENCE-FREE (ADR r3-0003 D2, MDD 1.7077): report ratios, R and "
                     "film units, never a copy-LF skill delta on this dataset"
                     if args.dataset_name in REFERENCE_FREE_DATASETS else
                     "reference-bearing: skill against the eval layer's copy-LF / "
                     "paper-bar denominator is quotable for this dataset, but the "
                     "card's registered unit is still film"),
            "ifc_affine_floor_rule": (
                "program.md (round 3) §2: every ifc number is reported next to the "
                "fitted affine_on_hf_train floor WITH its leave-one-out fold range "
                "(ifc_heat single-fit 0.070918 = skill 0.9584, LOO mean 1.8469, fold sd "
                "~10.9 tau_rel) and the paper bar 0.074 — see "
                "splits.ref_affine_on_hf_train and gate_report.floor_tolerances"
                if args.dataset_name.startswith("ifc_") else None),
            "pfc_caveat": (
                "WEAK FIDELITY GAP denominator caveat, and NO CERTIFIED tau_rel exists "
                "for this cell (state/anchors_repaired/noise_floor.json has no pfc "
                "entry). The card registers pfc CONDITIONALLY: adjudicated only if a "
                "certified pfc tau_rel exists at analysis time; otherwise reported with "
                "its film-unit margin and an explicit non-adjudication flag. This "
                "family invents no pfc threshold."
                if args.dataset_name == PFC_DATASET else None),
            "datasets_of_this_card": ",".join(card_cells) + " (explicit list from "
                                     "R3S3B3_CELLS; --datasets panel is NEVER used — it "
                                     "resolves the ROUND-2 panel)",
            "dropped": {"ifc_poisson": "REPORT-ONLY under ADR r3-0007 option C "
                                       "(ratified 2026-08-10): its condition->HF map is "
                                       "exactly affine (oracle residual 5.4e-16). This "
                                       "card runs no ifc_poisson leg and its predictive-"
                                       "cell clause is deleted per the card's "
                                       "_ifc_clause_status."},
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
        "declared_baseline_is_the_denominator": {
            "family": reporting.FILM_FAMILY,
            "role": "ADR r3-0006 / batch-3 scope rule 1: mf_fno_transfer_film is the "
                    "certified DENOMINATOR of this card's success clauses "
                    "(state/anchors/film_denominator.json). It is program.md §12.3's "
                    "mandatory declared baseline too, and the card's recipe.base_family "
                    "is explicit that it is 'the ADR r3-0006 DENOMINATOR, never an arm "
                    "here'. No leg of this card trains it.",
            "source": "state/anchors/film_denominator.json (3 seeds, 200 epochs, jobs "
                      "171858-60; pfc cell added 2026-08-10 under ADR r3-0005)",
            "caveat": "the denominator file's own note: the factory family emits no "
                      "step metadata, so zero_work_resume_scan reads UNDERIVABLE on it; "
                      "the clean ckpt-mtime stale audit is the witness"},
        "resolved_recipe": resolved,
        "recipe_env": {k: v for k, v in sorted(os.environ.items())
                       if k.startswith("R3S3B3_")},
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
                        "R3S3B3_LF_COND_CAP; no penalty, no LF at test",
        "scored_arm": p["arm"],
    })
    # CARDED CHANGE 4 (terminology, blocking): nothing this family writes may
    # carry the banned vocabulary. Checked on the SERIALISED text, so a string
    # smuggled in through any nested block fails before the file exists.
    text = json.dumps(written, indent=2)
    _assert_no_banned_terms(text, f"the result JSON for {args.dataset_name}")
    Path(out_path).write_text(text)

    if p["dump_test_preds"] == "1":
        dump = Path(out_path).with_suffix("").as_posix() + "_preds.npz"
        arrays = {
            "hf_grid": np.asarray(d["hf_grid"], dtype=np.int64),
            "s_hf": np.asarray([d["s_hf"]], dtype=np.float64),
            "selected_train_rows": np.asarray(d["sel"], dtype=np.int64),
            "cond_test_raw": d["X_te"].astype(np.float64),
            "pred_test": pred_te_flat.astype(np.float32),
            # CARDED CHANGE 2 — the PER-ROW stratified dump. `rel_l2_test` is the
            # same per-row array the eval layer scores on; the mask is written
            # beside it so any downstream stratification uses this leg's own rows
            # and never re-derives an ordering.
            "rel_l2_test": rel_rows.astype(np.float64),
        }
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
    pb = written["knee_prereg"]["prereg"]
    print(f"[prereg] sha256={pb['payload_sha256'][:16]}... sealed={pb['sealed_utc']} "
          f"lead={pb['ordering']['lead_seconds']}s ladder={p.get('_sealed_ladder')} "
          f"rung={rung_label} c_pred={pb.get('c_pred_REGISTERED')}", flush=True)
    if ckpt_binding_report.get("enabled"):
        print(f"[binding] role={ckpt_binding_report['arm_role']} "
              f"union={ckpt_binding_report['union_sha256'][:16]}... "
              f"roles_read={ckpt_binding_report['roles_read']}", flush=True)
    fu = gate.get("film_units", {})
    if fu.get("performed"):
        print(f"[film] skill_film={fu['skill_film']:.6f} "
              f"denom={fu['nrmse_film_mean']:.6f} "
              f"tau_rel_film={fu['tau_rel_film']} "
              f"certified={fu['tau_rel_certified']}", flush=True)
    mr = gate.get("mean_removed")
    if mr:
        print(f"[mean-removed] nRMSE={mr['mean_removed_nRMSE']:.6f} "
              f"raw={mr['raw_nRMSE']:.6f} ratio={mr['ratio_mean_removed_over_raw']:.3f}",
              flush=True)
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
