#!/bin/bash
# Throttled re-run of specific (family<TAB>dataset) cells at a higher epoch budget
# (fairness bump for under-trained baselines). Usage: bump_cells.sh EPOCHS SEED [MY_MAX] [PAIRS_FILE]
set -uo pipefail
MF=/orcd/data/faez/001/nick/mf_field
EPOCHS="${1:?epochs}"; SEED="${2:?seed}"; MY_MAX="${3:-40}"
PAIRS="${4:-$MF/akash/eval/bump_cells.txt}"
SUBM="$MF/akash/results/submitted_e${EPOCHS}_s${SEED}"; mkdir -p "$SUBM" "$MF/akash/results/raw_full"
LOG="$MF/akash/logs/bump_e${EPOCHS}_s${SEED}.log"
mapfile -t PAIRLIST < "$PAIRS"
EXPECT=${#PAIRLIST[@]}
DEADLINE=$(( $(date +%s) + 46*3600 ))
echo "==== bump $EXPECT cells e$EPOCHS s$SEED $(date) ====" | tee -a "$LOG"
myq(){ squeue -u nicksung -h -n akash-bench 2>/dev/null | wc -l; }
fail=0
while :; do
  remaining=0; needsub=0; q=$(myq); slots=$(( MY_MAX - q ))
  for line in "${PAIRLIST[@]}"; do
    m="${line%%$'\t'*}"; d="${line##*$'\t'}"
    out="$MF/akash/results/raw_full/${m}__${d}__e${EPOCHS}__s${SEED}.json"; mark="$SUBM/${m}__${d}"
    [ -f "$out" ] && { rm -f "$mark"; continue; }
    remaining=$((remaining+1)); [ -f "$mark" ] && continue; needsub=$((needsub+1))
    if [ "$slots" -gt 0 ] && sbatch "$MF/akash/eval/run_one.sbatch" "$m" "$d" "$EPOCHS" "$SEED" >>"$LOG" 2>&1; then
      touch "$mark"; slots=$((slots-1)); needsub=$((needsub-1)); fi
  done
  done_n=0; for line in "${PAIRLIST[@]}"; do m="${line%%$'\t'*}"; d="${line##*$'\t'}"; [ -f "$MF/akash/results/raw_full/${m}__${d}__e${EPOCHS}__s${SEED}.json" ] && done_n=$((done_n+1)); done
  echo "[$(date)] $done_n/$EXPECT done | $(myq) queued | $remaining left" | tee -a "$LOG"
  [ "$done_n" -ge "$EXPECT" ] && break
  [ "$(date +%s)" -ge "$DEADLINE" ] && { echo "[timeout]" | tee -a "$LOG"; break; }
  if [ "$remaining" -gt 0 ] && [ "$needsub" -eq 0 ] && [ "$(myq)" -eq 0 ]; then
    fail=$((fail+1)); [ "$fail" -ge 2 ] && { echo "[stuck]" | tee -a "$LOG"; break; }; else fail=0; fi
  sleep 180
done
echo "==== bump done $(date) ====" | tee -a "$LOG"
