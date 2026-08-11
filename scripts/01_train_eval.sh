#!/bin/bash
# r3s2_field_reach-B3 — one (dataset-set, seed) scoring job.
#
# Train+eval is ONE `score_panel.py` invocation in this project (no train->eval
# chain). Invoked as: 01_train_eval.sh <SEED>
#
# --time 03:00:00: the card recipe `_note` directs it verbatim ("B3 adds pfc and
# two zero-GPU rungs, so request 03:00:00 as B2 did"), and state/timing_ledger.json
# supports it — the closest analog is r3s2_field_reach-B2 (same family lineage,
# same 200 epochs, same nvidia_h200) at 54.7 / 44.07 / 43.87 min for seeds 0/1/2
# on 5 cells, plus the ADR r3-0005 pfc rescore leg at ~2 min/seed. B3 spends LESS
# GPU per sharp cell than B2 (one emulator + one corrector chain + one direct
# head, where B2 ran two of each), and its two real-LF rungs (R2_oracle,
# R2b_copylf) are ZERO-GPU — they reuse R1's frozen corrector. The one addition
# is the ifc cells, where the enumerated C(5,3) fold population retrains the
# neural stages per fold; at n_train_hf = 5 / n_lf = 20 rows that is small.
# 03:00:00 is ~3.3x the closest analog.
# >= 1 h => --mail-user / --mail-type per project.yaml sbatch.
#
# --datasets takes ONLY 'panel' | 'guard' | a comma-list of NAMES, so the guard
# run is a SEPARATE invocation (recipe `_note`); it runs on seed 0 only.
# NOTE: the literal 'panel' is NOT used — it resolves through round2/project.yaml
# to the ROUND-2 six-dataset panel. The list below is recipe.datasets VERBATIM:
# all SIX cells RUN under ADR r3-0007 option C; only which per-cell units are
# REGISTERED vs REPORT-ONLY changes, and the family resolves that in-job via
# R3S2B3_REGISTRATION_PREDICATE.
#
# JOB NAME: an #SBATCH header cannot interpolate $1, so the default below is the
# seed-0 name and `submit.sh` / `submit_seeds_2_3.sh` pass `--job-name` on the
# sbatch command line (which overrides the header) for the seed they submit.
#SBATCH --job-name=r3-r3s2_field_reach-B3-s0
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:nvidia_h200:1
#SBATCH --mem=64G
#SBATCH --time=03:00:00
#SBATCH --mail-user=ezeng@caltech.edu
#SBATCH --mail-type=END,FAIL
#SBATCH --output=/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch_outputs/round3/r3s2_field_reach/B3/slurm/%x_%j.out
#SBATCH --error=/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch_outputs/round3/r3s2_field_reach/B3/slurm/%x_%j.err

set -euo pipefail
SEED="${1:?usage: 01_train_eval.sh <seed>}"

PROJECT_ROOT="/resnick/groups/Hippo/ezeng/mf_field"
ROUND_ROOT="$PROJECT_ROOT/mffp_autoresearch/round3"
EVAL_DIR="$PROJECT_ROOT/mffp_autoresearch/round2/eval"
WORKTREE="$ROUND_ROOT/worktrees/r3s2_field_reach/B3"
FAMILY_DIR="$WORKTREE/models_r3/r3s2_ceiling"
OUT_DIR="$PROJECT_ROOT/mffp_autoresearch_outputs/round3/r3s2_field_reach/B3"

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

# recipe.datasets, VERBATIM (all six cells; ADR r3-0007 option C decides only
# which units REGISTER).
DATASETS="sharp__phase_field_crystal_2d,sharp__allen_cahn_2d,sharp__fisher_kpp_2d,sharp__cahn_hilliard,ifc_poisson,ifc_heat"
EPOCHS=200

source "$PROJECT_ROOT/.venv/bin/activate"
mkdir -p "$OUT_DIR/eval" "$OUT_DIR/slurm" "$OUT_DIR/training" "$OUT_DIR/cache"

echo "[$(date)] host=$(hostname) gpu=$(nvidia-smi -L 2>/dev/null | head -1 || echo none) seed=$SEED"
echo "[$(date)] family=$FAMILY_DIR datasets=$DATASETS epochs=$EPOCHS"
echo "[$(date)] ROUND2_EVAL_RESULTS=$ROUND2_EVAL_RESULTS ROUND2_EVAL_CACHE=$ROUND2_EVAL_CACHE"

# --env values below are the card recipe.env, VERBATIM, in recipe order (the 83
# keys that are NOT `_`-prefixed; `_`-prefixed keys are card directives and are
# NOT passed). Checkpoint dirs are derived by score_panel.py from
# ROUND2_EVAL_RESULTS and are therefore FRESH under
# .../B3/training/r3s2_ceiling/ — never reused from B1/B2 (recipe `_note`).
ENV_KNOBS=(
    R3S2B3_LADDER=oracle_ceiling_5rung
    "R3S2B3_RUNGS=R0_absent,R1_predicted,R1b_degraded,R2_oracle,R2b_copylf"
    R3S2B3_ORACLE_NONDEPLOYABLE=1
    "R3S2B3_TEST_SPLIT_ARMS=R0_absent,R1_predicted,R1b_degraded"
    R3S2B3_HOT_SPLIT_SHARP=seeded_perm_fit320_heldout80
    R3S2B3_HOT_SPLIT_IFC=enumerate_C5_3
    R3S2B3_IFC_LOO_DISCLOSURE=enumerate_C5_4
    R3S2B3_SHARP_CLOSEDFORM_FOLDS=kfold5_within_T
    R3S2B3_HOT_SPLIT_KEY=deterministic_from_dataset_and_seed
    R3S2B3_NO_TEST_LF_ASSERT=1
    "R3S2B3_STATS=phi_ceil,phi_real,rho,E_est,E_hall"
    "R3S2B3_REPORT_UNITS=film_skill,fractional_error_reduction"
    R3S2B3_BAND_STATS=energy_weighted_signed_coherence
    R3S2B3_MIN_OVER_LEGS_CLAUSES=1
    R3S2B3_LEG_POPULATION_DUMP=1
    R3S2B3_FILM_DENOM_JSON=mffp_autoresearch/round3/state/anchors/film_denominator.json
    R3S2B3_NOISE_FLOOR_JSON=mffp_autoresearch/round3/state/anchors_repaired/noise_floor.json
    R3S2B3_REGISTRATION_PREDICATE=scored_and_certified_mce_and_not_floor_disqualified
    R3S2B3_SPLIT_TRANSFER_GATE=1
    R3S2B3_SPLIT_TRANSFER_TOL_LOGRATIO=0.25
    R3S2B3_CORRECTOR_SELECT_ON=emulator_heldout_output
    R3S2B3_CORRECTOR_SELECT_COMPARAND=real_lf
    S6_LSI_RIDGE=enumerated_folds_out_of_sample
    "S6_LSI_RIDGE_GRID=0,1e-10,3.162e-10,1e-9,1e-8,1e-7,1e-6,1e-4,1e-2,1e-1"
    S6_LSI_BANDLIMIT=selected_not_fixed
    "S6_LSI_BANDLIMIT_GRID=on,off"
    S6_LSI_BANDLIMIT_MODE=zero_above_kcut
    S6_LSI_KCUT_SOURCE=ladder_shape_ratio_adr_r2_0001
    S6_LEAKAGE_TRIPWIRE=1
    "S6_BAND_EDGES_FRAC=0,0.125,0.25,0.5,1.0"
    S6_VARIANT=local_pixel_gate
    S6_SELECTOR=heldout_scalar
    S6_PAD_MODE=circular_if_periodic
    S6_PERIODIC_TEST=wrap_continuity_ratio_hf_train
    S6_PERIODIC_TOL=1.25
    S6_KERNEL=7
    S6_DEPTH=4
    S6_WIDTH=32
    S6_GATE_HOLDOUT_FRAC=0.2
    S6_GATE_INIT=zero
    S6_GATE_LINESEARCH_INCLUDES_ZERO=1
    R3S2_FRONTEND=ic_synth
    R3S2_ARM=frozen
    R3S2_IC_SYNTH=analytic_modes
    R3S2_IC_SYNTH_NORM=res_min_maxabs
    R3S2_IC_SYNTH_SCALE=1.0
    R3S2_IC_NAMES_FROM=meta_param_names_ic_prefix
    R3S2_IC_FALLBACK=film_only_recorded
    R3S2_IC_EQUIV_CHECK=1
    R3S2_IC_SHUFFLE_NULL=0_established_in_B1
    R3S2_EMU_TARGET=lf_native
    R3S2_EMU_RUNG=scored_cell_lf_from_panel_data
    R3S2_EMU_WIDTH=64
    R3S2_EMU_BLOCKS=4
    R3S2_EMU_MODES=12
    R3S2_EMU_LOSS=rel_l2
    R3S2_EMU_SHARED=1
    R3S2_EPOCH_SPLIT=0.5
    R3S2_BUDGET_MATCH=arm_equal_total
    R3S2_UPSAMPLE=corrected_by_convention
    R3S2B3_RUNG_LIFT_TRIPWIRE=1
    R3S2_TARGET_SCALER_PREFLIGHT=pfc_per_sample_if_outlier_dominated
    R3S2_LF_INPUT=pseudo_and_real_by_rung
    R3S2_VAL_DISJOINT=1
    R3S2_REQUIRE_PSEUDO_LF=1
    R3S2_PAIRING_GATE=1
    "R3S2_FLOOR_ARMS=nn_condition,train_mean,zero,affine_on_hf_train"
    "R3S2B3_FLOOR_MATCHED_N=sharp:320,ifc:C5_4_loo"
    R3S2B3_G5_BAND_DISCLOSURE=1
    R3S2B3_CKPT_BINDING=1
    "R3S2B3_ROLES_READ=R0_absent=cond_only,R1_predicted=lf_at_train,R1b_degraded=lf_at_train,R2_oracle=lf_at_train,R2b_copylf=lf_at_train"
    R3S2B3_CKPT_DATA_HASH_BIND=1
    R3S2B3_ANCHOR_REPLICATION_CHECK=10.0853
    R3S2_DIAG_OUT=mffp_autoresearch_outputs/round3/r3s2_field_reach/B3/eval
)

python "$EVAL_DIR/score_panel.py" \
    --family_dir "$FAMILY_DIR" \
    --datasets "$DATASETS" \
    --epochs "$EPOCHS" \
    --seed "$SEED" \
    --out "$OUT_DIR/eval/result_all6_s${SEED}.json" \
    --env "${ENV_KNOBS[@]}"

echo "[$(date)] six-cell run done; result:"
cat "$OUT_DIR/eval/result_all6_s${SEED}.json"

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
