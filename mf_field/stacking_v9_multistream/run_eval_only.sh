#!/bin/bash
# run_eval_only.sh  —  Evaluate all fractions using film_best.pth
set -e
cd "$(dirname "$0")"
mkdir -p logs

PYTHON="$(which python3) -u"
EVAL_LOG="logs/eval_film_best.log"
> "$EVAL_LOG"   # clear / create

ALL_RUNS=(frac0001 frac001 frac005 frac010 frac020)

echo "══════════════════════════════════════════════════════════════" | tee -a "$EVAL_LOG"
echo "  [$(date '+%Y-%m-%d %H:%M:%S')]  Evaluating all fractions — weights=film_best.pth" | tee -a "$EVAL_LOG"
echo "══════════════════════════════════════════════════════════════" | tee -a "$EVAL_LOG"

for RUN in "${ALL_RUNS[@]}"; do
    CKPT="checkpoints/${RUN}"
    if [ ! -f "${CKPT}/film_best.pth" ]; then
        echo "  [SKIP] ${RUN}/film_best.pth not found" | tee -a "$EVAL_LOG"
        continue
    fi
    echo "" | tee -a "$EVAL_LOG"
    echo "  [$(date '+%Y-%m-%d %H:%M:%S')]  Evaluating ${RUN} ..." | tee -a "$EVAL_LOG"
    $PYTHON eval_v9.py \
        --run_name "$RUN" \
        --weights  "film_best.pth" \
        --split    test \
        2>&1 | tee -a "$EVAL_LOG"
    echo "  [$(date '+%Y-%m-%d %H:%M:%S')]  ${RUN} done" | tee -a "$EVAL_LOG"
done

echo "" | tee -a "$EVAL_LOG"
echo "══════════════════════════════════════════════════════════════" | tee -a "$EVAL_LOG"
echo "  [$(date '+%Y-%m-%d %H:%M:%S')]  All evaluations complete" | tee -a "$EVAL_LOG"
echo "══════════════════════════════════════════════════════════════" | tee -a "$EVAL_LOG"
