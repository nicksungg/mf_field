#!/bin/bash
# Run ONE (family, dataset) of the akash subset benchmark on a GPU.
# Args: $1=family  $2=dataset  $3=epochs(default 2500)  $4=seed(default 42)
#
# Isolated from the factory's model discovery: resolves families under
# akash/models/ first, then factory_mffp/models/ (for the calibration anchors),
# and datasets under factory_mffp/data/ then sharp_generated/. Writes results to
# akash/results/raw_bench/ so nothing in factory_mffp is touched.
#SBATCH --job-name=akash-bench
#SBATCH --partition=mit_normal_gpu,mit_preemptable
#SBATCH --exclude=node2901
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:1
#SBATCH --mem=96G
#SBATCH --time=6:00:00
#SBATCH --requeue
#SBATCH --signal=B:USR1@120
#SBATCH --output=/orcd/data/faez/001/nick/mf_field/akash/logs/bench_%j.out
#SBATCH --error=/orcd/data/faez/001/nick/mf_field/akash/logs/bench_%j.err

set -euo pipefail
MF=/orcd/data/faez/001/nick/mf_field
cd "$MF/factory_mffp"
source scripts/env.sh          # sets MFFP_PY
PY="$MFFP_PY"

FAMILY="${1:?family required}"
DATASET="${2:?dataset required}"
EPOCHS="${3:-2500}"
SEED="${4:-42}"

# Resolve family smoke_eval.py: akash contenders, factory models, then external SOTA baselines.
SMOKE=""
for base in "$MF/akash/models" "$MF/factory_mffp/models" \
            "$MF/factory_mffp/references/external_sota" "$MF/factory_mffp/references"; do
    if [ -f "$base/$FAMILY/smoke_eval.py" ]; then SMOKE="$base/$FAMILY/smoke_eval.py"; break; fi
done
[ -z "$SMOKE" ] && { echo "ERROR: smoke_eval.py not found for family=$FAMILY" >&2; exit 2; }

# Dataset dir: all 42 are now collision-safe symlinks under factory_mffp/data/.
DSDIR="$MF/factory_mffp/data/$DATASET"
[ -d "$DSDIR" ] || { echo "ERROR: dataset dir not found for $DATASET" >&2; exit 3; }

OUT="$MF/akash/results/raw_full/${FAMILY}__${DATASET}__e${EPOCHS}__s${SEED}.json"
CKPT="$MF/akash/checkpoints/${FAMILY}/${DATASET}"
mkdir -p "$MF/akash/results/raw_full" "$CKPT" "$MF/akash/logs"

echo "[$(date)] family=$FAMILY dataset=$DATASET epochs=$EPOCHS seed=$SEED"
echo "[$(date)] host=$(hostname) gpu=$(nvidia-smi -L 2>/dev/null | head -1)"
echo "[$(date)] smoke=$SMOKE dsdir=$DSDIR"
trap 'echo "[$(date)] USR1 — checkpoint saved, exiting for requeue"; sleep 30; exit 0' USR1

"$PY" "$SMOKE" \
    --dataset_dir "$DSDIR" --dataset_name "$DATASET" \
    --epochs "$EPOCHS" --out "$OUT" --ckpt_dir "$CKPT" --seed "$SEED"
echo "[$(date)] done -> $OUT"
