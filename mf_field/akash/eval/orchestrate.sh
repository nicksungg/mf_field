#!/bin/bash
# Unattended driver (throttled): GPU smoke gate -> fill 120 cells on
# pi_faez/mit_normal_gpu while respecting the per-QOS submit limit -> ELO.
# Keeps <= MY_MAX of OUR jobs queued at once and retries when the scheduler is
# full. Marker files in results/submitted/ prevent double-submitting in-flight
# cells; cells whose output JSON exists are skipped (resume-friendly).
set -uo pipefail
MF=/orcd/data/faez/001/nick/mf_field
PY="$MF/factory_mffp/.venv/bin/python"
LOG="$MF/akash/logs/orchestrate.log"
SUBM="$MF/akash/results/submitted"
mkdir -p "$MF/akash/logs" "$MF/akash/results/raw_bench" "$SUBM"
rm -f "$MF/akash/results/ORCHESTRATE_DONE"
echo "==== orchestrate start $(date) ====" | tee -a "$LOG"

MODELS=(mf_fno_hyperfilm mf_fno_allpairs mf_fno_spectral mf_fno_richardson \
        mf_fno_ptr mf_fno_diffprior mf_fno_foundation mf_fno_lora \
        mf_fno_transfer_film mf_fno_transfer_bar)
DATASETS=(era5 pm_test ifc_poisson darcy_generated lid_driven_cavity_generated \
          poisson_local heat_local euler_generated burgers_2d_generated \
          kuramoto_sivashinsky_generated shallow_water_2d_generated cahn_hilliard_generated)
EPOCHS=2500; SEED=42
EXPECT=$(( ${#MODELS[@]} * ${#DATASETS[@]} ))
MY_MAX=40                                   # max of OUR jobs queued at once (pi_faez per-user submit limit = 64)
DEADLINE=$(( $(date +%s) + 46*3600 ))       # pi_faez is small (~10 H100); allow a long drain

out_of() { echo "$MF/akash/results/raw_bench/${1}__${2}__e${EPOCHS}__s${SEED}.json"; }
myq() { squeue -u nicksung -h -n akash-bench 2>/dev/null | wc -l; }

# ── 1) GPU smoke gate (skip if already clean) ──
SCSV="$MF/akash/results/smoke_gpu.csv"
if [ -f "$SCSV" ] && [ "$(awk -F, 'NR>1 && $3!=0' "$SCSV" | wc -l)" -eq 0 ] && [ "$(awk -F, 'NR>1' "$SCSV" | wc -l)" -gt 0 ]; then
  echo "[$(date)] smoke gate already clean — skipping" | tee -a "$LOG"
else
  echo "[$(date)] submitting smoke gate (sbatch --wait)" | tee -a "$LOG"
  sbatch --wait "$MF/akash/eval/smoke_gpu.sbatch" 2>&1 | tee -a "$LOG" || true
  total=$(awk -F, 'NR>1' "$SCSV" 2>/dev/null | wc -l); fails=$(awk -F, 'NR>1 && $3!=0' "$SCSV" 2>/dev/null | wc -l)
  echo "[$(date)] smoke gate: ${fails:-?}/${total:-?} cells failed" | tee -a "$LOG"
  if [ "${total:-0}" -gt 0 ] && [ "${fails:-0}" -ge "${total:-0}" ]; then
    echo "[$(date)] ABORT — every smoke cell failed" | tee -a "$LOG"; touch "$MF/akash/results/ORCHESTRATE_DONE"; exit 1
  fi
fi

# ── 2+3) throttled submit + wait loop ──
fail_cycles=0
while :; do
  remaining=0; needsub=0
  q=$(myq); slots=$(( MY_MAX - q ))
  for m in "${MODELS[@]}"; do for d in "${DATASETS[@]}"; do
    out=$(out_of "$m" "$d"); mark="$SUBM/${m}__${d}"
    [ -f "$out" ] && { rm -f "$mark"; continue; }     # done -> drop any marker
    remaining=$((remaining+1))
    [ -f "$mark" ] && continue                        # already in flight (submitted)
    needsub=$((needsub+1))
    if [ "$slots" -gt 0 ]; then
      if sbatch "$MF/akash/eval/run_one.sbatch" "$m" "$d" "$EPOCHS" "$SEED" >>"$LOG" 2>&1; then
        touch "$mark"; slots=$((slots-1)); needsub=$((needsub-1))
      fi   # sbatch failed (QOS full) -> retry a later cycle
    fi
  done; done

  done_n=$(ls "$MF"/akash/results/raw_bench/*__e${EPOCHS}__s${SEED}.json 2>/dev/null | wc -l)
  qn=$(myq)
  echo "[$(date)] $done_n/$EXPECT outputs | $qn ours queued | $remaining remaining ($needsub need-submit)" | tee -a "$LOG"

  [ "$done_n" -ge "$EXPECT" ] && { echo "[$(date)] all cells done" | tee -a "$LOG"; break; }
  [ "$(date +%s)" -ge "$DEADLINE" ] && { echo "[$(date)] TIMEOUT" | tee -a "$LOG"; break; }
  # Terminal failure case: cells remain, all were submitted (none need-submit), and
  # none of ours are queued -> they ran and produced no output. Confirm over 2 cycles.
  if [ "$remaining" -gt 0 ] && [ "$needsub" -eq 0 ] && [ "$qn" -eq 0 ]; then
    fail_cycles=$((fail_cycles+1))
    if [ "$fail_cycles" -ge 2 ]; then
      echo "[$(date)] $remaining cells failed (no output, nothing queued) — giving up on them" | tee -a "$LOG"; break
    fi
  else
    fail_cycles=0
  fi
  sleep 180
done

# ── 4) compute ELO ──
echo "[$(date)] computing ELO" | tee -a "$LOG"
"$PY" "$MF/akash/eval/compute_elo.py" --epochs $EPOCHS --seed $SEED 2>&1 | tee -a "$LOG"
touch "$MF/akash/results/ORCHESTRATE_DONE"
echo "==== orchestrate done $(date) ====" | tee -a "$LOG"
