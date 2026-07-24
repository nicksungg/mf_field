#!/bin/bash
# Multi-lane topper-upper for the factory_mffp 135-task sweep.
#
# Manages 2 partitions with submit-job caps:
#   - pi_faez:        64-job cap; %3 throttle; H100/H200 (incl. node4002 if free)
#   - mit_normal_gpu: 64-job cap, 2 GPUs concurrent (until reservation activates 2026-05-20)
#
# mit_preemptable is NOT managed — all 135 tasks are already queued there;
# Slurm's QoS cap of ~8 concurrent slots throttles execution natively.
#
# The script wakes every $INTERVAL, counts current per-partition occupancy,
# and submits the next in-tree chunk to whichever lane has headroom.
# State files track per-lane next-index so it resumes cleanly across restarts.
#
# Usage:
#   tmux new -s topup
#   bash data_adapters/topup_multi.sh
#   # Ctrl-b d to detach. Logs: data_adapters/topup_multi.log

set -u
PROJECT=/orcd/data/faez/001/nick/mf_field/factory_mffp
LOG="$PROJECT/data_adapters/topup_multi.log"
USER_ME="${USER:-$(whoami)}"

TOTAL=90                # in-tree task indices 0..89
FAMILIES_CSV="v9_baseline,fno_coregionalization,fno_mf_stack,fno_coreg_residual,transolver_attention_fusion,transolver_residual"
SBATCH_SCRIPT="eval/run_full.sbatch"
CONFIG="data_adapters/full_config_15.json"
INTERVAL=600            # 10 min between cycles
SAFETY_MARGIN=4         # leave this many quota slots free per lane

# Per-lane config (parallel arrays, indexed by lane name)
declare -A LANE_CAP=(
    [pi_faez]=64
    [mit_normal_gpu]=64
)
declare -A LANE_CHUNK=(
    [pi_faez]=15
    [mit_normal_gpu]=10
)
declare -A LANE_THROTTLE=(
    [pi_faez]=3
    [mit_normal_gpu]=2
)
declare -A LANE_SBATCH_EXTRA=(
    [pi_faez]=""
    [mit_normal_gpu]="--time=06:00:00"
)
declare -A LANE_STATE=(
    [pi_faez]="$PROJECT/data_adapters/topup_pi_faez_state.txt"
    [mit_normal_gpu]="$PROJECT/data_adapters/topup_mit_normal_gpu_state.txt"
)

log() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
    echo "$msg"
    echo "$msg" >> "$LOG"
}

count_my_jobs_on() {
    local part="$1"
    local n
    n=$(squeue -u "$USER_ME" -p "$part" -h -t PENDING,RUNNING -r 2>/dev/null | wc -l)
    [ -z "$n" ] && n=0
    echo "$n"
}

submit_chunk_on() {
    local lane="$1"
    local start="$2"
    local end="$3"
    local throttle="${LANE_THROTTLE[$lane]}"
    local extra="${LANE_SBATCH_EXTRA[$lane]}"
    local out
    out=$(MFFP_FULL_CONFIG="$CONFIG" \
          sbatch --partition="$lane" --gres=gpu:1 $extra \
                 --array="${start}-${end}%${throttle}" \
                 "$SBATCH_SCRIPT" "$FAMILIES_CSV" 2>&1)
    if echo "$out" | grep -q "Submitted batch job"; then
        local jid=$(echo "$out" | grep -oE '[0-9]+' | head -1)
        log "OK   ${lane}: submitted job ${jid} array=${start}-${end}%${throttle}"
        return 0
    else
        log "WARN ${lane}: submission failed (${start}-${end}): ${out}"
        return 1
    fi
}

# Initialize per-lane next-index from state file or sensible defaults.
get_next_index() {
    local lane="$1"
    local state="${LANE_STATE[$lane]}"
    local default
    case "$lane" in
        pi_faez)        default=78 ;;   # 0-59 already on pi_faez via various H200 arrays; 60-77 via 14039637
        mit_normal_gpu) default=60 ;;   # 0-59 already via 14040837, 78-79 via 14040822
        *)              default=0 ;;
    esac
    cat "$state" 2>/dev/null || echo "$default"
}

set_next_index() {
    echo "$2" > "${LANE_STATE[$1]}"
}

cd "$PROJECT" || { log "FATAL: cd $PROJECT failed"; exit 1; }

log "----- topup_multi started (PID $$) -----"
log "lanes: pi_faez mit_normal_gpu  | total in-tree=$TOTAL  | interval=${INTERVAL}s"
log "starting indices: pi_faez=$(get_next_index pi_faez) mit_normal_gpu=$(get_next_index mit_normal_gpu)"

trap 'log "Interrupted (SIGINT). State preserved."; exit 0' INT TERM

while true; do
    # If every lane is at or past TOTAL, we're done.
    all_done=true
    for lane in pi_faez mit_normal_gpu; do
        if [ "$(get_next_index "$lane")" -lt "$TOTAL" ]; then
            all_done=false
        fi
    done
    if $all_done; then
        log "DONE all in-tree indices submitted to both lanes. Exiting."
        exit 0
    fi

    for lane in pi_faez mit_normal_gpu; do
        next=$(get_next_index "$lane")
        if [ "$next" -ge "$TOTAL" ]; then continue; fi
        cap="${LANE_CAP[$lane]}"
        chunk="${LANE_CHUNK[$lane]}"
        used=$(count_my_jobs_on "$lane")
        avail=$(( cap - used - SAFETY_MARGIN ))
        if [ "$avail" -ge "$chunk" ]; then
            end=$(( next + chunk - 1 ))
            [ "$end" -ge "$TOTAL" ] && end=$(( TOTAL - 1 ))
            if submit_chunk_on "$lane" "$next" "$end"; then
                set_next_index "$lane" $(( end + 1 ))
            fi
        else
            log "wait ${lane}=${used}/${cap}  avail=${avail}  need=${chunk}  next_index=${next}"
        fi
    done

    sleep "$INTERVAL"
done
