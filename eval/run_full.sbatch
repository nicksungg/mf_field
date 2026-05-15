#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# Full benchmark across all 17 datasets. Run as a SLURM array job — one task
# per (model_family × dataset) pair.
#
# Usage:
#   FAMILIES="v9_baseline,my_new_family"
#   sbatch --array=0-$N% eval/run_full.sbatch  $FAMILIES
#
# Use `eval/launch_full.py` to compute the array size and submit for you.
# ─────────────────────────────────────────────────────────────────────────────
#SBATCH --job-name=mffp-full
#SBATCH --partition=mit_preemptable
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:1
#SBATCH --mem=96G
#SBATCH --time=24:00:00
#SBATCH --requeue
#SBATCH --signal=B:USR1@120
#SBATCH --output=logs/full_%A_%a.out
#SBATCH --error=logs/full_%A_%a.err

set -euo pipefail
cd "$(dirname "$(realpath "$0")")/.."

mkdir -p logs results checkpoints
source scripts/env.sh
PY="$MFFP_PY"

FAMILIES_CSV="${1:-v9_baseline}"
TASK_ID="${SLURM_ARRAY_TASK_ID:-0}"

trap 'echo "[$(date)] USR1 — saving and exiting"; sleep 30; exit 0' USR1

echo "[$(date)] full benchmark task=$TASK_ID families=$FAMILIES_CSV"
"$PY" eval/launch_full.py --array_index "$TASK_ID" --families "$FAMILIES_CSV"
