#!/bin/bash
# Stand-by quota topper-upper for the factory_mffp 135-task sweep on pi_faez.
#
# Why: pi_faez has a 64-jobs-per-user submit cap, so we can't queue all 90
# in-tree tasks at once. This script wakes every $INTERVAL, counts current
# pi_faez occupancy, and submits the next chunk of in-tree tasks if there's
# headroom. It uses --partition=pi_faez and the same launcher/sbatch as the
# initial submissions. Cache dedup in score.py means tasks already finished
# on mit_preemptable will return in <1s — no wasted compute.
#
# Usage:
#   tmux new -s topup
#   bash data_adapters/topup_pi_faez.sh
#   # Ctrl-b d to detach. tmux attach -t topup to come back.
#
# Stop with Ctrl-C (or `tmux kill-session -t topup`).
# Progress lives at data_adapters/topup.log; resume state at data_adapters/topup_state.txt.

set -u
PROJECT=/archive/mf_field/factory_mffp
LOG="$PROJECT/data_adapters/topup.log"
STATE="$PROJECT/data_adapters/topup_state.txt"
USER_ME="${USER:-$(whoami)}"

PARTITION=pi_faez
QOS_CAP=64
SAFETY_MARGIN=4          # always leave this many quota slots free
CHUNK_SIZE=15            # tasks per submitted array (one family worth)
ARRAY_THROTTLE=3         # %N throttle inside each array (concurrent on pi_faez)
INTERVAL=600             # seconds between checks (10 min)
TOTAL_IN_TREE=90         # 6 families × 15 datasets
FIRST_NOT_YET_SUBMITTED=17  # tasks 0-16 already on pi_faez via job 14034327

FAMILIES_CSV="v9_baseline,fno_coregionalization,fno_mf_stack,fno_coreg_residual,transolver_attention_fusion,transolver_residual"
SBATCH_SCRIPT="eval/run_full.sbatch"
CONFIG="data_adapters/full_config_15.json"

log() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
    echo "$msg"
    echo "$msg" >> "$LOG"
}

# Read state file: the next array index we still need to submit to pi_faez.
NEXT_INDEX=$(cat "$STATE" 2>/dev/null || echo "$FIRST_NOT_YET_SUBMITTED")

log "----- topup_pi_faez started (PID $$) -----"
log "next_index=$NEXT_INDEX  total=$TOTAL_IN_TREE  cap=$QOS_CAP  chunk=$CHUNK_SIZE  interval=${INTERVAL}s"

trap 'log "Interrupted (SIGINT); state preserved at $STATE"; exit 0' INT TERM

cd "$PROJECT" || { log "FATAL: cd $PROJECT failed"; exit 1; }

while [ "$NEXT_INDEX" -lt "$TOTAL_IN_TREE" ]; do
    # Count my pi_faez jobs (running + pending). Each array element counts as 1.
    MY_PIFAEZ=$(squeue -u "$USER_ME" -p "$PARTITION" -h -t PENDING,RUNNING -r 2>/dev/null | wc -l)
    if [ -z "$MY_PIFAEZ" ]; then MY_PIFAEZ=0; fi

    AVAILABLE=$(( QOS_CAP - MY_PIFAEZ - SAFETY_MARGIN ))

    if [ "$AVAILABLE" -ge "$CHUNK_SIZE" ]; then
        END_INDEX=$(( NEXT_INDEX + CHUNK_SIZE - 1 ))
        if [ "$END_INDEX" -ge "$TOTAL_IN_TREE" ]; then
            END_INDEX=$(( TOTAL_IN_TREE - 1 ))
        fi
        ARRAY_RANGE="${NEXT_INDEX}-${END_INDEX}"

        OUT=$(MFFP_FULL_CONFIG="$CONFIG" \
              sbatch --partition="$PARTITION" \
                     --array="${ARRAY_RANGE}%${ARRAY_THROTTLE}" \
                     "$SBATCH_SCRIPT" "$FAMILIES_CSV" 2>&1)
        if echo "$OUT" | grep -q "Submitted batch job"; then
            JOB_ID=$(echo "$OUT" | grep -oE '[0-9]+' | head -1)
            log "OK  submitted job ${JOB_ID} array=${ARRAY_RANGE}%${ARRAY_THROTTLE} (pi_faez occupancy ${MY_PIFAEZ}/${QOS_CAP})"
            NEXT_INDEX=$(( END_INDEX + 1 ))
            echo "$NEXT_INDEX" > "$STATE"
        else
            log "WARN submission failed at array=${ARRAY_RANGE}: ${OUT}"
        fi
    else
        log "wait  pi_faez=${MY_PIFAEZ}/${QOS_CAP}  available=${AVAILABLE}  need=${CHUNK_SIZE}"
    fi

    sleep "$INTERVAL"
done

log "DONE all $TOTAL_IN_TREE in-tree tasks submitted to pi_faez. Exiting."
