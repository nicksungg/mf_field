#!/bin/bash
# Fair benchmark: 9 families x 15 datasets on pi_faez (one array task per pair).
#
# Usage:
#   cd /orcd/data/faez/001/nick/mf_field/factory_mffp
#   N=$(.venv/bin/python fairbench/run_fairbench.py --plan | head -1 | cut -d= -f2)
#   sbatch --array=0-$((N-1))%8 fairbench/run_fairbench.sbatch
#
#SBATCH --job-name=fairbench
#SBATCH --partition=pi_faez
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:1
#SBATCH --mem=96G
#SBATCH --time=24:00:00
#SBATCH --requeue
#SBATCH --signal=B:USR1@120
#SBATCH --output=/orcd/data/faez/001/nick/mf_field/factory_mffp/logs/fairbench_%A_%a.out
#SBATCH --error=/orcd/data/faez/001/nick/mf_field/factory_mffp/logs/fairbench_%A_%a.err

set -euo pipefail
cd /orcd/data/faez/001/nick/mf_field/factory_mffp
mkdir -p logs results/raw_fairbench checkpoints/fairbench
source scripts/env.sh

EPOCHS="${FAIRBENCH_EPOCHS:-2500}"
SEED="${FAIRBENCH_SEED:-42}"
TASK_ID="${SLURM_ARRAY_TASK_ID:-0}"

trap 'echo "[$(date)] USR1 — checkpoint saved, exiting for requeue"; sleep 30; exit 0' USR1

echo "[$(date)] fairbench task=$TASK_ID epochs=$EPOCHS seed=$SEED host=$(hostname)"
echo "[$(date)] gpu=$(nvidia-smi -L | head -1)"

"$MFFP_PY" fairbench/run_fairbench.py \
    --array_index "$TASK_ID" --epochs "$EPOCHS" --seed "$SEED"

echo "[$(date)] done task=$TASK_ID"
