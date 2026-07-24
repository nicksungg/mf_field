#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# External-SOTA benchmark array job: one task per (family × dataset) pair, where
# families live under references/external_sota/<name>/ (wrapped upstream code).
# Mirrors eval/run_full.sbatch — parallel sweep, does not contend with it for
# anything except the user's GPU QOS cap.
#
# Usage:
#   FAMILIES="mfrnp,mf_deeponet,d_mfd"          # or "all"
#   CONFIG=eval/full_config_ifc_raw.json
#   python references/external_sota/launch_external_sota.py --plan --families $FAMILIES --config $CONFIG
#   # then submit with --array=0-(N-1)%8
# ─────────────────────────────────────────────────────────────────────────────
#SBATCH --job-name=mffp-extsota
#SBATCH --partition=mit_preemptable
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:1
#SBATCH --mem=96G
#SBATCH --time=24:00:00
#SBATCH --requeue
#SBATCH --signal=B:USR1@120
#SBATCH --output=logs/extsota_%A_%a.out
#SBATCH --error=logs/extsota_%A_%a.err

set -euo pipefail
cd /orcd/data/faez/001/nick/mf_field/factory_mffp

mkdir -p logs results checkpoints
source scripts/env.sh
PY="$MFFP_PY"

FAMILIES_CSV="${1:-all}"
TASK_ID="${SLURM_ARRAY_TASK_ID:-0}"
CONFIG="${MFFP_EXTSOTA_CONFIG:-eval/full_config_ifc_raw.json}"

trap 'echo "[$(date)] USR1 — saving and exiting"; sleep 30; exit 0' USR1

echo "[$(date)] extsota task=$TASK_ID families=$FAMILIES_CSV config=$CONFIG"
"$PY" references/external_sota/launch_external_sota.py \
    --array_index "$TASK_ID" \
    --families "$FAMILIES_CSV" \
    --config "$CONFIG"
