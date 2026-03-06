#!/bin/bash
# Trains 5% run for 2500 epochs, then evaluates all four fractions
# (frac100, frac020, frac010, frac005) with film_best and film_final.
# Log: logs/train_frac005.log   logs/eval_all.log

set -e
cd "$(dirname "$0")"
mkdir -p logs

PYTHON="$(which python3) -u"
EVAL_LOG="logs/eval_all.log"

# ===================== 5% TRAINING =====================
echo "====== [$(date)] Starting 5% run (2500 epochs) ======"
$PYTHON train_car_3d.py \
    --epochs 2500 --batch_size 16 --n_points 8192 \
    --train_frac 0.05 --run_name frac005 \
    > logs/train_frac005.log 2>&1
echo "====== [$(date)] 5% run DONE ======"

# ===================== EVALUATION =====================
echo "====== [$(date)] Starting evaluation of all runs ======" | tee "$EVAL_LOG"

for RUN in frac100 frac020 frac010 frac005; do
    for CKPT in film_best film_final; do
        WEIGHTS="checkpoints_car_3d/${RUN}/${CKPT}.pth"
        if [ ! -f "$WEIGHTS" ]; then
            echo "[SKIP] $WEIGHTS not found" | tee -a "$EVAL_LOG"
            continue
        fi
        echo "" | tee -a "$EVAL_LOG"
        echo "---------- ${RUN} / ${CKPT} ----------" | tee -a "$EVAL_LOG"
        $PYTHON eval_car_3d.py \
            --split test \
            --run_name "$RUN" \
            --weights "$WEIGHTS" \
            2>&1 | tee -a "$EVAL_LOG"
    done
done

echo "" | tee -a "$EVAL_LOG"
echo "====== [$(date)] ALL EVALUATIONS COMPLETE ======" | tee -a "$EVAL_LOG"
