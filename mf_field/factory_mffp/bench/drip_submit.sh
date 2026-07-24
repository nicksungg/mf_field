#!/bin/bash
# Throttled drip-submitter for the fair benchmark (9 families × 15 datasets).
# Keeps the pi_faez queue near the QOS submit cap and tops up as jobs finish.
# Each cell gets a unique job-name "b_<family>__<dataset>" so we can tell which
# cells are already queued (skip), which finished (have result JSON), and which
# failed/preempted (no result, not queued -> resubmit). Resume-friendly.
# Usage: bash bench/drip_submit.sh [EPOCHS] [SEED]
set -uo pipefail
ROOT=/orcd/data/faez/001/nick/mf_field/factory_mffp
cd "$ROOT"
EPOCHS="${1:-2500}"; SEED="${2:-42}"
CAP=63           # under the 64/user QOS cap (1 slot for the stacking job)
MAX_ITERS=720    # ~24h safety horizon at 120s/iter

FAMILIES=(fno_mf_stack fno_coregionalization fno_coreg_residual
          transolver_residual transolver_attention_fusion v9_baseline
          mfrnp mf_deeponet d_mfd mf_fno_transfer)
DATASETS=(ifc_heat ifc_poisson poisson_local heat_local fluid era5 pm_test
          advection_diffusion_generated allen_cahn_generated burgers_generated
          burgers_param_generated darcy_generated heat_generated
          lid_driven_cavity_generated poisson_generated)

for ((it=0; it<MAX_ITERS; it++)); do
    mapfile -t QUEUED < <(squeue -u "$USER" -h -o "%j" 2>/dev/null | grep '^b_' || true)
    qn="${#QUEUED[@]}"
    done=0; submitted=0
    for fam in "${FAMILIES[@]}"; do
      for ds in "${DATASETS[@]}"; do
        out="results/raw_bench/${fam}__${ds}__e${EPOCHS}__s${SEED}.json"
        if [ -f "$out" ]; then done=$((done+1)); continue; fi
        name="b_${fam}__${ds}"
        # already queued?
        already=0; for q in "${QUEUED[@]:-}"; do [ "$q" = "$name" ] && { already=1; break; }; done
        [ "$already" -eq 1 ] && continue
        # room left?
        if [ "$qn" -ge "$CAP" ]; then continue; fi
        if sbatch --job-name="$name" bench/bench_one.sbatch "$fam" "$ds" "$EPOCHS" "$SEED" >/dev/null 2>&1; then
            qn=$((qn+1)); submitted=$((submitted+1)); QUEUED+=("$name")
        fi
      done
    done
    total=$(( ${#FAMILIES[@]} * ${#DATASETS[@]} ))
    echo "[drip it=$it] done=$done/$total queued=$qn submitted_this_iter=$submitted"
    if [ "$done" -ge "$total" ]; then echo "[drip] complete."; break; fi
    sleep 120
done
echo "[drip] final result files: $(ls results/raw_bench/*.json 2>/dev/null | wc -l)/135"
