#!/bin/bash
# Heavy (era5-scale) re-run for the 6 missing climate cells, on mit_preemptable
# (mit_normal_gpu caps at 6h — too short). Runs FAMILY x era5, then copies the
# result to the pm_test cell (pm_test is a byte-identical alias of era5).
# Args: $1=family  $2=epochs(default 2500)  $3=seed(default 42)
#SBATCH --job-name=akash-bench
#SBATCH --partition=pi_faez
#SBATCH --exclude=node2901
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:1
#SBATCH --mem=128G
#SBATCH --time=4-00:00:00
#SBATCH --requeue
#SBATCH --signal=B:USR1@120
#SBATCH --output=/orcd/data/faez/001/nick/mf_field/akash/logs/heavy_%j.out
#SBATCH --error=/orcd/data/faez/001/nick/mf_field/akash/logs/heavy_%j.err

set -uo pipefail
MF=/orcd/data/faez/001/nick/mf_field
cd "$MF/factory_mffp"; source scripts/env.sh; PY="$MFFP_PY"
FAMILY="${1:?family}"; EPOCHS="${2:-2500}"; SEED="${3:-42}"; DATASET="era5"

SMOKE=""
for base in "$MF/akash/models" "$MF/factory_mffp/models" \
            "$MF/factory_mffp/references/external_sota" "$MF/factory_mffp/references"; do
    [ -f "$base/$FAMILY/smoke_eval.py" ] && { SMOKE="$base/$FAMILY/smoke_eval.py"; break; }
done
[ -z "$SMOKE" ] && { echo "no smoke_eval for $FAMILY" >&2; exit 2; }

OUT="$MF/akash/results/raw_full/${FAMILY}__${DATASET}__e${EPOCHS}__s${SEED}.json"
PM="$MF/akash/results/raw_full/${FAMILY}__pm_test__e${EPOCHS}__s${SEED}.json"
CKPT="$MF/akash/checkpoints/${FAMILY}/${DATASET}"
mkdir -p "$MF/akash/results/raw_full" "$CKPT" "$MF/akash/logs"
echo "[$(date)] HEAVY family=$FAMILY era5 epochs=$EPOCHS host=$(hostname) gpu=$(nvidia-smi -L 2>/dev/null|head -1)"
trap 'echo "[$(date)] USR1 preempt/timeout"; sleep 20; exit 0' USR1

"$PY" "$SMOKE" --dataset_dir "$MF/factory_mffp/data/era5" --dataset_name era5 \
    --epochs "$EPOCHS" --out "$OUT" --ckpt_dir "$CKPT" --seed "$SEED"
if [ -f "$OUT" ]; then cp -f "$OUT" "$PM"; echo "[$(date)] done -> $OUT (+ copied to pm_test)"; fi
