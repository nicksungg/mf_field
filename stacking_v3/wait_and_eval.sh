#!/bin/bash
# Polls until all 5 runs finish training, then runs eval for each
cd "$(dirname "$0")"
PYTHON="$(which python3)"
RUNS=(frac0001 frac001 frac005 frac010 frac020)
LOG="logs/eval_all.log"

echo "[wait_and_eval] Started at $(date)" | tee -a "$LOG"

# Wait for the pipeline to finish (all film_final.pth files exist)
while true; do
  done_count=0
  for r in "${RUNS[@]}"; do
    [ -f "checkpoints/${r}/film_final.pth" ] && done_count=$((done_count + 1))
  done
  echo "  [$(date '+%H:%M:%S')] ${done_count}/5 runs complete" | tee -a "$LOG"
  [ "$done_count" -eq 5 ] && break
  sleep 300
done

echo "[wait_and_eval] All training done at $(date). Running evaluation..." | tee -a "$LOG"

for r in "${RUNS[@]}"; do
  for w in film_best film_final; do
    echo "  Evaluating $r  weights=$w ..." | tee -a "$LOG"
    $PYTHON eval_v3.py --run_name "$r" --weights "${w}.pth" --split test >> "$LOG" 2>&1
  done
done

echo "[wait_and_eval] All evaluations done at $(date)" | tee -a "$LOG"
