#!/bin/bash
# One few-shot-HF cell.  Args: $1=dataset $2=mechanism $3=n_hf $4=seed $5=epochs
#SBATCH --job-name=fewshot
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --gres=gpu:1
#SBATCH --mem=48G
#SBATCH --time=06:00:00
#SBATCH --requeue
#SBATCH --output=/orcd/data/faez/001/nick/mf_field/factory_mffp/logs/fewshot_%j.out
#SBATCH --error=/orcd/data/faez/001/nick/mf_field/factory_mffp/logs/fewshot_%j.err

set -uo pipefail
ROOT=/orcd/data/faez/001/nick/mf_field/factory_mffp
cd "$ROOT"
source scripts/env.sh
DS="${1:?dataset}"; MECH="${2:?mechanism}"; NHF="${3:?n_hf}"; SEED="${4:-42}"; EP="${5:-2500}"
OUT="$ROOT/results/raw_fewshot/${MECH}__${DS}__nhf${NHF}__s${SEED}__e${EP}.json"
mkdir -p "$ROOT/results/raw_fewshot" "$ROOT/logs"
echo "[$(date)] fewshot ds=$DS mech=$MECH n_hf=$NHF seed=$SEED ep=$EP host=$(hostname)"
"$MFFP_PY" fewshot/run_fewshot.py --dataset_dir "data/$DS" --dataset_name "$DS" \
    --mechanism "$MECH" --n_hf "$NHF" --epochs "$EP" --seed "$SEED" --out "$OUT"
echo "[$(date)] done -> $OUT"
