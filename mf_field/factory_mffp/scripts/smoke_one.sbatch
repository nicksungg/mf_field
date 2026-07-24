#!/bin/bash
# Run one (family, dataset) smoke at 200 epochs on a single GPU.
# Args: $1 = family name, $2 = dataset name
#SBATCH --job-name=mffp-smoke1
#SBATCH --partition=mit_preemptable
#SBATCH --nodes=1
#SBATCH --cpus-per-task=4
#SBATCH --gres=gpu:1
#SBATCH --mem=48G
#SBATCH --time=04:00:00
#SBATCH --requeue
#SBATCH --signal=B:USR1@90
#SBATCH --output=/orcd/data/faez/001/nick/mf_field/factory_mffp/logs/smoke1_%j.out
#SBATCH --error=/orcd/data/faez/001/nick/mf_field/factory_mffp/logs/smoke1_%j.err

set -euo pipefail
cd /orcd/data/faez/001/nick/mf_field/factory_mffp
source scripts/env.sh
FAMILY="${1:?family required}"
DATASET="${2:?dataset required}"
EPOCHS="${3:-200}"
SEED="${4:-42}"
mkdir -p results/raw checkpoints

# code hash for cache key
HASH=$("$MFFP_PY" -c "
import hashlib
from pathlib import Path
h = hashlib.sha256()
for p in sorted(Path('models/$FAMILY').rglob('*.py')):
    h.update(p.relative_to('models/$FAMILY').as_posix().encode())
    h.update(p.read_bytes())
print(h.hexdigest()[:12])
")
TAG="${FAMILY}__${DATASET}__e${EPOCHS}__s${SEED}__${HASH}"
OUT="results/raw/${TAG}.json"
CKPT="checkpoints/${FAMILY}/${DATASET}"

echo "[$(date)] family=$FAMILY dataset=$DATASET epochs=$EPOCHS hash=$HASH"
echo "[$(date)] host=$(hostname) gpu=$(nvidia-smi -L | head -1)"

trap 'echo "[$(date)] USR1 — checkpoint saved, exiting for requeue"; sleep 30; exit 0' USR1

"$MFFP_PY" "models/${FAMILY}/smoke_eval.py" \
    --dataset_dir "data/${DATASET}" --dataset_name "${DATASET}" \
    --epochs "$EPOCHS" --out "$OUT" --ckpt_dir "$CKPT" --seed "$SEED"
echo "[$(date)] done. wrote $OUT"
