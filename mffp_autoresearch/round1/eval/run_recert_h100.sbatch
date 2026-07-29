#!/bin/bash
# ADR 0005: anchor carry-over check — champion mf_fno_transfer_film seed-0
# panel at smoke tier on H100, --no_cache. Compare per-dataset nRMSE to the
# batch-0 (p100) seed-0 values; within min_claimable_effect => anchors carry.
#SBATCH --job-name=r1-recert-h100
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --gres=gpu:h100:1
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --exclude=hpc-93-36
#SBATCH --output=/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch_outputs/round1/recert/slurm/%x_%j.out
#SBATCH --error=/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch_outputs/round1/recert/slurm/%x_%j.err

set -euo pipefail
PROJECT_ROOT=/resnick/groups/Hippo/ezeng/mf_field
ROUND_ROOT="$PROJECT_ROOT/mffp_autoresearch/round1"
OUT_ROOT="$PROJECT_ROOT/mffp_autoresearch_outputs/round1/recert"
source "$PROJECT_ROOT/.venv/bin/activate"
# Fresh results root so batch-0 checkpoints are NOT resumed — forces a true
# H100 retrain (the first attempt resumed finished p100 checkpoints and only
# validated the inference path; see orchestrator_flow 2026-07-29).
export ROUND1_EVAL_RESULTS="$OUT_ROOT/training_h100"
mkdir -p "$ROUND1_EVAL_RESULTS"
python "$ROUND_ROOT/eval/score_panel.py" \
  --family_dir "$PROJECT_ROOT/mf_field/factory_mffp/models/mf_fno_transfer_film" \
  --datasets panel --epochs 200 --seed 0 --no_cache \
  --out "$OUT_ROOT/h100_champion_seed0_retrain.json"
