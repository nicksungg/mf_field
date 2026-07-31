#!/bin/bash
# Template: one (dataset-set, seed) scoring job for MFFP round 2.
# Builders copy to <worktree>/scripts/01_train_eval.sh and substitute the
# ALL-CAPS placeholders. Invoked as: 01_train_eval.sh <SEED>
#SBATCH --job-name=r2-STREAM-BN-sSEED
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --gres=gpu:h100:1
#SBATCH --mem=32G
#SBATCH --time=04:00:00
#SBATCH --output=OUTPUTS_ROOT/STREAM/BN/slurm/%x_%j.out
#SBATCH --error=OUTPUTS_ROOT/STREAM/BN/slurm/%x_%j.err

set -euo pipefail
SEED="${1:?usage: 01_train_eval.sh <seed>}"

PROJECT_ROOT="PROJECT_ROOT_ABS"          # e.g. /resnick/groups/Hippo/ezeng/mf_field
ROUND_ROOT="$PROJECT_ROOT/mffp_autoresearch/round2"
WORKTREE="WORKTREE_ABS"                  # $ROUND_ROOT/worktrees/STREAM/BN
OUT_DIR="OUTPUTS_ROOT/STREAM/BN"         # git-ignored outputs root

source "$PROJECT_ROOT/.venv/bin/activate"
mkdir -p "$OUT_DIR/eval" "$OUT_DIR/slurm"

echo "[$(date)] host=$(hostname) gpu=$(nvidia-smi -L | head -1 || echo none) seed=$SEED"

python "$ROUND_ROOT/eval/score_panel.py" \
    --family_dir "$WORKTREE/models_r2/FAMILY" \
    --datasets DATASETS \
    --epochs EPOCHS \
    --seed "$SEED" \
    --out "$OUT_DIR/eval/result_DATASETS_s${SEED}.json"
    # append: --env KEY=VAL ... (must mirror the card recipe.env exactly)

echo "[$(date)] done; result:"
cat "$OUT_DIR/eval/result_DATASETS_s${SEED}.json"
