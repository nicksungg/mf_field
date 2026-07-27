#!/bin/bash
# Run ONE (family, dataset) of the fair benchmark on a pi_faez GPU.
# Args: $1=family  $2=dataset  $3=epochs(default 2500)  $4=seed(default 42)
#SBATCH --job-name=mffp-bench
#SBATCH --partition=mit_normal_gpu,mit_preemptable
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:1
#SBATCH --mem=96G
#SBATCH --time=06:00:00
#SBATCH --requeue
#SBATCH --signal=B:USR1@120
#SBATCH --output=/orcd/data/faez/001/nick/mf_field/factory_mffp/logs/bench_%j.out
#SBATCH --error=/orcd/data/faez/001/nick/mf_field/factory_mffp/logs/bench_%j.err

set -euo pipefail
ROOT=/orcd/data/faez/001/nick/mf_field/factory_mffp
cd "$ROOT"
source scripts/env.sh   # sets MFFP_PY
PY="$MFFP_PY"

FAMILY="${1:?family required}"
DATASET="${2:?dataset required}"
EPOCHS="${3:-2500}"
SEED="${4:-42}"

# Resolve the family's smoke_eval.py across the three locations.
SMOKE=""
for base in "models" "references" "references/external_sota"; do
    if [ -f "$ROOT/$base/$FAMILY/smoke_eval.py" ]; then
        SMOKE="$ROOT/$base/$FAMILY/smoke_eval.py"; break
    fi
done
if [ -z "$SMOKE" ]; then echo "ERROR: smoke_eval.py not found for family=$FAMILY" >&2; exit 2; fi

OUT="$ROOT/results/raw_bench/${FAMILY}__${DATASET}__e${EPOCHS}__s${SEED}.json"
CKPT="$ROOT/checkpoints/bench/${FAMILY}/${DATASET}"
mkdir -p "$ROOT/results/raw_bench" "$CKPT" "$ROOT/logs"

echo "[$(date)] family=$FAMILY dataset=$DATASET epochs=$EPOCHS seed=$SEED"
echo "[$(date)] host=$(hostname) gpu=$(nvidia-smi -L 2>/dev/null | head -1) smoke=$SMOKE"
trap 'echo "[$(date)] USR1 — checkpoint saved, exiting for requeue"; sleep 30; exit 0' USR1

"$PY" "$SMOKE" \
    --dataset_dir "$ROOT/data/${DATASET}" --dataset_name "${DATASET}" \
    --epochs "$EPOCHS" --out "$OUT" --ckpt_dir "$CKPT" --seed "$SEED"
echo "[$(date)] done -> $OUT"
