#!/bin/bash
# Batch 0 (gate G3): anchor certification + seed noise floor.
# Array over (family x panel-dataset x seed): 2 x 6 x 3 = 36 tasks @ smoke tier.
# Submit: sbatch mffp_autoresearch/round1/eval/run_batch0.sbatch
#SBATCH --job-name=r1-batch0
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --gres=gpu:p100:1
#SBATCH --mem=32G
#SBATCH --time=06:00:00
#SBATCH --array=0-35
#SBATCH --output=/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch_outputs/round1/batch0/slurm/%x_%A_%a.out
#SBATCH --error=/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch_outputs/round1/batch0/slurm/%x_%A_%a.err

set -euo pipefail
PROJECT_ROOT=/resnick/groups/Hippo/ezeng/mf_field
ROUND_ROOT="$PROJECT_ROOT/mffp_autoresearch/round1"
OUT_DIR="$PROJECT_ROOT/mffp_autoresearch_outputs/round1/batch0"

FAMILIES=(mf_fno_transfer_film mf_fno_pinn_transfer)
DATASETS=(ext__helmholtz_2d sharp__phase_field_crystal_2d sharp__allen_cahn_2d sharp__fisher_kpp_2d sharp__cahn_hilliard ifc_poisson)
SEEDS=(0 1 2)

i=$SLURM_ARRAY_TASK_ID
f=$((i / 18)); rem=$((i % 18)); d=$((rem / 3)); s=$((rem % 3))
FAMILY="${FAMILIES[$f]}"; DATASET="${DATASETS[$d]}"; SEED="${SEEDS[$s]}"

source "$PROJECT_ROOT/.venv/bin/activate"
mkdir -p "$OUT_DIR/eval" "$OUT_DIR/slurm"

echo "[$(date)] task=$i family=$FAMILY dataset=$DATASET seed=$SEED gpu=$(nvidia-smi -L | head -1 || echo none)"

python "$ROUND_ROOT/eval/score_panel.py" \
    --family_dir "$PROJECT_ROOT/mf_field/factory_mffp/models/$FAMILY" \
    --datasets "$DATASET" \
    --epochs 200 \
    --seed "$SEED" \
    --out "$OUT_DIR/eval/${FAMILY}__${DATASET}_s${SEED}.json"

echo "[$(date)] done"
