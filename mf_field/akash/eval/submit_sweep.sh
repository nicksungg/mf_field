#!/bin/bash
# Generic throttled submitter for one benchmark phase (one epochs+seed).
# Usage: submit_sweep.sh EPOCHS SEED [MY_MAX] [FAMILIES_FILE]
#   Reads families from FAMILIES_FILE (default bench_families.txt) and datasets
#   from bench_datasets.txt. Submits every (family x dataset) cell lacking an
#   output JSON, keeping <= MY_MAX of our jobs queued (pi_faez per-user cap 64),
#   retrying when the scheduler is full. Marker files prevent double-submit.
#   Polls until all outputs exist or the queue drains. No aggregation here.
set -uo pipefail
MF=/orcd/data/faez/001/nick/mf_field
EPOCHS="${1:?epochs required}"; SEED="${2:?seed required}"
MY_MAX="${3:-40}"
FAMFILE="${4:-$MF/akash/eval/bench_families.txt}"
DSFILE="${5:-$MF/akash/eval/bench_datasets.txt}"
mapfile -t MODELS < "$FAMFILE"
mapfile -t DATASETS < "$DSFILE"
SUBM="$MF/akash/results/submitted_e${EPOCHS}_s${SEED}"; mkdir -p "$SUBM" "$MF/akash/results/raw_full" "$MF/akash/logs"
LOG="$MF/akash/logs/sweep_e${EPOCHS}_s${SEED}.log"
EXPECT=$(( ${#MODELS[@]} * ${#DATASETS[@]} ))
DEADLINE=$(( $(date +%s) + 46*3600 ))
echo "==== sweep e$EPOCHS s$SEED : ${#MODELS[@]} fam x ${#DATASETS[@]} ds = $EXPECT cells $(date) ====" | tee -a "$LOG"

out_of(){ echo "$MF/akash/results/raw_full/${1}__${2}__e${EPOCHS}__s${SEED}.json"; }
myq(){ squeue -u nicksung -h -n akash-bench 2>/dev/null | wc -l; }

fail_cycles=0
while :; do
  remaining=0; needsub=0; q=$(myq); slots=$(( MY_MAX - q ))
  for m in "${MODELS[@]}"; do for d in "${DATASETS[@]}"; do
    out=$(out_of "$m" "$d"); mark="$SUBM/${m}__${d}"
    [ -f "$out" ] && { rm -f "$mark"; continue; }
    remaining=$((remaining+1))
    [ -f "$mark" ] && continue
    needsub=$((needsub+1))
    if [ "$slots" -gt 0 ]; then
      if sbatch "$MF/akash/eval/run_one.sbatch" "$m" "$d" "$EPOCHS" "$SEED" >>"$LOG" 2>&1; then
        touch "$mark"; slots=$((slots-1)); needsub=$((needsub-1))
      fi
    fi
  done; done
  done_n=0; for mm in "${MODELS[@]}"; do for dd in "${DATASETS[@]}"; do [ -f "$(out_of "$mm" "$dd")" ] && done_n=$((done_n+1)); done; done
  qn=$(myq)
  echo "[$(date)] $done_n/$EXPECT done | $qn queued | $remaining left ($needsub need-submit)" | tee -a "$LOG"
  [ "$done_n" -ge "$EXPECT" ] && { echo "[$(date)] complete" | tee -a "$LOG"; break; }
  [ "$(date +%s)" -ge "$DEADLINE" ] && { echo "[$(date)] TIMEOUT" | tee -a "$LOG"; break; }
  if [ "$remaining" -gt 0 ] && [ "$needsub" -eq 0 ] && [ "$qn" -eq 0 ]; then
    fail_cycles=$((fail_cycles+1)); [ "$fail_cycles" -ge 2 ] && { echo "[$(date)] $remaining failed (no output) — stop" | tee -a "$LOG"; break; }
  else fail_cycles=0; fi
  sleep 180
done
echo "==== sweep e$EPOCHS s$SEED done $(date) ====" | tee -a "$LOG"
