#!/bin/bash
# r3s2_field_reach-B2 — one (dataset-set, seed) scoring job.
#
# Train+eval is ONE `score_panel.py` invocation in this project (no train->eval
# chain). Invoked as: 01_train_eval.sh <SEED>
#
# --time 03:00:00: the card recipe `_note` directs it, and the timing ledger
# (state/timing_ledger.json) supports it — r3s2_field_reach-B1, same datasets,
# same 200 epochs, same nvidia_h200, ran 44.33 / 36.55 / 36.55 min for seeds
# 0/1/2. B1 spent 2400 optimizer epochs per dataset over 10 arms; B2 spends
# fewer (2 emulators x E_emu + 4 corrector stages x E_dc + 2 direct heads x
# 300) but 600 of them are on the HF grid (the two direct condition->HF heads),
# so the recipe estimates 45-70 min/seed. 03:00:00 is ~2.6x the closest analog.
# >= 1 h => --mail-user / --mail-type per project.yaml sbatch.
#
# --datasets takes ONLY 'panel' | 'guard' | a comma-list of NAMES, so the guard
# run is a SEPARATE invocation (recipe `_note`); it runs on seed 0 only.
# NOTE: the literal 'panel' is NOT used — it resolves through round2/project.yaml
# to the ROUND-2 six-dataset panel. ADR r3-0004 fixes the scored set to the 5
# names below (pfc is report-only: its scored cell is task-void).
#
# JOB NAME: an #SBATCH header cannot interpolate $1, so the default below is the
# seed-0 name and `submit.sh` / `submit_seeds_2_3.sh` pass `--job-name` on the
# sbatch command line (which overrides the header) for the seed they submit.
#SBATCH --job-name=r3-r3s2_field_reach-B2-s0
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:nvidia_h200:1
#SBATCH --mem=64G
#SBATCH --time=03:00:00
#SBATCH --mail-user=ezeng@caltech.edu
#SBATCH --mail-type=END,FAIL
#SBATCH --output=/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch_outputs/round3/r3s2_field_reach/B2/slurm/%x_%j.out
#SBATCH --error=/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch_outputs/round3/r3s2_field_reach/B2/slurm/%x_%j.err

set -euo pipefail
SEED="${1:?usage: 01_train_eval.sh <seed>}"

PROJECT_ROOT="/resnick/groups/Hippo/ezeng/mf_field"
ROUND_ROOT="$PROJECT_ROOT/mffp_autoresearch/round3"
EVAL_DIR="$PROJECT_ROOT/mffp_autoresearch/round2/eval"
WORKTREE="$ROUND_ROOT/worktrees/r3s2_field_reach/B2"
FAMILY_DIR="$WORKTREE/models_r3/r3s2_route"
OUT_DIR="$PROJECT_ROOT/mffp_autoresearch_outputs/round3/r3s2_field_reach/B2"

# REDIRECT THE EVAL LAYER'S WRITE ROOTS INTO THE OUTPUTS TREE.
# `score_panel.py::_results_dir()` / `_cache_dir()` default to EVAL_DIR/"results"
# and EVAL_DIR/"cache", and BOTH the per-cell result JSON and the ckpt_dir are
# derived from _results_dir(). Without these exports the job would write per-cell
# JSONs and multi-GB checkpoint trees INTO the frozen round-2 eval layer
# (program.md §5 immutable: the eval layer is byte-untouched during the round).
# Carried verbatim from B1's review-FAIL discharge @ d5069a74 and mandated by the
# card recipe `env._script_env`. Set BEFORE the first score_panel.py call so the
# guard invocation below is covered too; exported so the child process inherits.
export ROUND2_EVAL_RESULTS="$OUT_DIR/training"
export ROUND2_EVAL_CACHE="$OUT_DIR/cache"

# ADR r3-0004: the explicit 5-dataset SCORED panel (recipe.datasets, verbatim).
DATASETS="sharp__allen_cahn_2d,sharp__fisher_kpp_2d,sharp__cahn_hilliard,ifc_poisson,ifc_heat"
EPOCHS=200

source "$PROJECT_ROOT/.venv/bin/activate"
mkdir -p "$OUT_DIR/eval" "$OUT_DIR/slurm" "$OUT_DIR/training" "$OUT_DIR/cache"

echo "[$(date)] host=$(hostname) gpu=$(nvidia-smi -L 2>/dev/null | head -1 || echo none) seed=$SEED"
echo "[$(date)] family=$FAMILY_DIR datasets=$DATASETS epochs=$EPOCHS"
echo "[$(date)] ROUND2_EVAL_RESULTS=$ROUND2_EVAL_RESULTS ROUND2_EVAL_CACHE=$ROUND2_EVAL_CACHE"

# --env values below are the card recipe.env, VERBATIM, in recipe order (the 68
# keys that are NOT `_`-prefixed; `_`-prefixed keys are card directives and are
# NOT passed). Checkpoint dirs are derived by score_panel.py from
# ROUND2_EVAL_RESULTS and are therefore FRESH under .../B2/training/r3s2_route/
# — never reused from B1 (recipe `_note`).
ENV_KNOBS=(
    R3S2B2_ARM=A1_stack_ic_reg
    R3S2B2_ROUTE=stack
    R3S2_FRONTEND=ic_synth
    R3S2_ARM=frozen
    R3S2B2_DIRECT_TARGET=hf
    R3S2B2_DIRECT_TRUNK=shared_film_fno_w64_b4_m12
    R3S2B2_DIRECT_BUDGET=match_stage2_total
    R3S2B2_DIRECT_TRAIN_ROWS=hf_train_all
    R3S2B2_DIRECT_VAL=disjoint_if_n_train_hf_ge_20_else_none_recorded
    R3S2_IC_SYNTH=analytic_modes
    R3S2_IC_SYNTH_NORM=res_min_maxabs
    R3S2_IC_SYNTH_SCALE=1.0
    R3S2_IC_NAMES_FROM=meta_param_names_ic_prefix
    R3S2_IC_FALLBACK=film_only_recorded
    R3S2_IC_EQUIV_CHECK=1
    R3S2_IC_SHUFFLE_NULL=0_established_in_B1
    R3S2_EMU_TARGET=lf_native
    R3S2_EMU_RUNG=max
    R3S2_EMU_WIDTH=64
    R3S2_EMU_BLOCKS=4
    R3S2_EMU_MODES=12
    R3S2_EMU_LOSS=rel_l2
    R3S2_EMU_SHARED=1
    R3S2_EPOCH_SPLIT=0.5
    R3S2_BUDGET_MATCH=arm_equal_total
    R3S2_UPSAMPLE=corrected_by_convention
    R3S2_LF_INPUT=pseudo
    R3S2_CORRECTOR_FIT_ON=real_lf
    R3S2_VAL_DISJOINT=1
    R3S2_REQUIRE_PSEUDO_LF=1
    R3S2_PAIRING_GATE=1
    R3S2_PAIRED_SUBSET_GEOMEAN=1
    R3S2_TARGET_SCALER_PREFLIGHT=not_applicable_no_helmholtz_no_pfc_in_datasets
    "R3S2_FLOOR_ARMS=nn_condition,train_mean,zero,affine_on_hf_train"
    R3S2_DIAG_OUT=mffp_autoresearch_outputs/round3/r3s2_field_reach/B2/eval
    S6_VARIANT=local_pixel_gate
    S6_SELECTOR=heldout_scalar
    S6_PAD_MODE=circular_if_periodic
    S6_PERIODIC_TEST=wrap_continuity_ratio_hf_train
    S6_PERIODIC_TOL=1.25
    S6_LF_SOURCE=dataset_lf_fidelity
    S6_LF_FID=max
    S6_KERNEL=7
    S6_DEPTH=4
    S6_WIDTH=32
    S6_GATE_HOLDOUT_FRAC=0.2
    S6_GATE_INIT=zero
    S6_GATE_LINESEARCH_INCLUDES_ZERO=1
    "S6_BAND_EDGES_FRAC=0,0.125,0.25,0.5,1.0"
    S6_LEAKAGE_TRIPWIRE=1
    S6_LSI_RIDGE=loocv
    "S6_LSI_RIDGE_GRID=0,1e-6,1e-4,1e-3,1e-2,1e-1"
    S6_LSI_RIDGE_SELECT=loocv_on_fit_fold_only
    S6_LSI_BANDLIMIT=lf_nyquist_from_ladder
    S6_LSI_BANDLIMIT_MODE=zero_above_kcut
    S6_LSI_KCUT_SOURCE=ladder_shape_ratio_adr_r2_0001
    "R3S2B2_REPORT_UNITS=skill,fractional_error_reduction"
    R3S2B2_BAND_ERROR_COLUMNS=1
    R3S2B2_MAP_SMOOTHNESS_SIDECAR=1
    R3S2B2_ROUTE_DATA_DISCLOSURE=1
    R3S2B2_T_STABILITY_AUDIT=1
    "R3S2B2_IFC_LOO_SELECTOR=affine_on_hf_train,A1_stack_ic_reg,A3_direct_ic"
    R3S2B2_CKPT_DATA_HASH_BIND=1
    R3S2B2_ANCHOR_REPLICATION_CHECK=12.9556
    R3S2_EMU_ERROR_SIDECAR=1
    R3S2_ORACLE_TRAINHELDOUT_SIDECAR=1
    R3S2_ZERO_GRADIENT_LADDER_SIDECAR=1
    R3S2_BC_AUDIT_SIDECAR=1
)

python "$EVAL_DIR/score_panel.py" \
    --family_dir "$FAMILY_DIR" \
    --datasets "$DATASETS" \
    --epochs "$EPOCHS" \
    --seed "$SEED" \
    --out "$OUT_DIR/eval/result_scored5_s${SEED}.json" \
    --env "${ENV_KNOBS[@]}"

echo "[$(date)] scored panel done; result:"
cat "$OUT_DIR/eval/result_scored5_s${SEED}.json"

# ── the GUARD run: a SEPARATE invocation (recipe `_note`), seed 0 only ────
if [ "$SEED" = "0" ]; then
    echo "[$(date)] guard set (separate --datasets guard invocation, smoke tier 200, seed 0)"
    python "$EVAL_DIR/score_panel.py" \
        --family_dir "$FAMILY_DIR" \
        --datasets guard \
        --epochs "$EPOCHS" \
        --seed 0 \
        --out "$OUT_DIR/eval/result_guard_s0.json" \
        --env "${ENV_KNOBS[@]}"
    echo "[$(date)] guard done; result:"
    cat "$OUT_DIR/eval/result_guard_s0.json"
fi

echo "[$(date)] ALL DONE seed=$SEED"
