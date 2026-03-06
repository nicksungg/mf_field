#!/bin/bash
# Train the stacking MF model for all four data fractions (sequential),
# then evaluate each run with film_best and film_final.
#
# Pause/Resume: just kill the process and re-run the same command.
#   Training auto-resumes from the last saved checkpoint (every 50 epochs).
#
# Logs: logs/train_<run>.log   logs/eval_all.log
#
# Usage:
#   bash run_stacking.sh              # all four fractions
#   bash run_stacking.sh frac020      # single fraction
#   bash run_stacking.sh frac100 frac020   # subset

set -e
cd "$(dirname "$0")"
mkdir -p logs

PYTHON="$(which python3) -u"
COMMON="--epochs 2500 --batch_size 16 --n_points 8192 --lf_weights film_best.pth"
EVAL_LOG="logs/eval_all.log"

# ─── which fractions to run ──────────────────────────────────────────────────
if [ $# -gt 0 ]; then
    RUNS=("$@")
else
    RUNS=(frac100 frac020 frac010 frac005)
fi

declare -A FRAC
FRAC[frac100]="1.00"
FRAC[frac020]="0.20"
FRAC[frac010]="0.10"
FRAC[frac005]="0.05"
FRAC[frac001]="0.01"
FRAC[frac0001]="0.001"

# ─── training ────────────────────────────────────────────────────────────────
for RUN in "${RUNS[@]}"; do
    F="${FRAC[$RUN]}"
    if [ -z "$F" ]; then
        echo "[WARN] Unknown run name '$RUN', skipping."
        continue
    fi
    echo "====== [$(date)] Training ${RUN}  (frac=${F}) ======"
    echo "       Resume-state will be saved every 50 epochs to checkpoints/${RUN}/resume_state.pth"
    $PYTHON train_stacking.py $COMMON \
        --train_frac "$F" --run_name "$RUN" \
        >> "logs/train_${RUN}.log" 2>&1
    echo "====== [$(date)] ${RUN} DONE ======"
done

# ─── evaluation ──────────────────────────────────────────────────────────────
echo "" | tee "$EVAL_LOG"
echo "====== [$(date)] Starting evaluation ======" | tee -a "$EVAL_LOG"

for RUN in frac100 frac020 frac010 frac005; do
    for CKPT in film_best film_final; do
        WEIGHTS_PATH="checkpoints/${RUN}/${CKPT}.pth"
        if [ ! -f "$WEIGHTS_PATH" ]; then
            echo "[SKIP] $WEIGHTS_PATH not found" | tee -a "$EVAL_LOG"
            continue
        fi
        echo "" | tee -a "$EVAL_LOG"
        echo "---------- ${RUN} / ${CKPT} ----------" | tee -a "$EVAL_LOG"
        $PYTHON eval_stacking.py \
            --split test \
            --run_name "$RUN" \
            --weights "${CKPT}.pth" \
            --lf_weights film_best.pth \
            2>&1 | tee -a "$EVAL_LOG"
    done
done

echo "" | tee -a "$EVAL_LOG"
echo "====== [$(date)] ALL EVALUATIONS COMPLETE ======" | tee -a "$EVAL_LOG"

