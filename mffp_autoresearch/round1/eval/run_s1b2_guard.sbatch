#!/bin/bash
# s1-B2: guard-set contract run for the winning arm (card's guard trigger
# fired: nRMSE < 0.056363; analyzer flagged the missing guard leg).
#SBATCH --job-name=r1-s1_poisson-B2-guard
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --gres=gpu:h100:1
#SBATCH --mem=32G
#SBATCH --time=00:30:00
#SBATCH --exclude=hpc-93-36
#SBATCH --requeue
#SBATCH --output=/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch_outputs/round1/s1_poisson/B2/slurm/%x_%j.out
#SBATCH --error=/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch_outputs/round1/s1_poisson/B2/slurm/%x_%j.err
set -euo pipefail
PROJECT_ROOT=/resnick/groups/Hippo/ezeng/mf_field
ROUND_ROOT="$PROJECT_ROOT/mffp_autoresearch/round1"
OUT="$PROJECT_ROOT/mffp_autoresearch_outputs/round1/s1_poisson/B2"
source "$PROJECT_ROOT/.venv/bin/activate"
export ROUND1_EVAL_RESULTS="$OUT/eval/results_guard"
python "$ROUND_ROOT/eval/score_panel.py" \
  --family_dir "$ROUND_ROOT/worktrees/s1_poisson/B2/models_r1/mf_fno_ladder_norm" \
  --datasets guard --epochs 2 --seed 0 --no_cache \
  --env MFFP_LADDER_MODE=allpairs MFFP_LADDER_SCALER=per_level \
  --out "$OUT/eval/result_guard_allpairs_per_level_s0.json"
