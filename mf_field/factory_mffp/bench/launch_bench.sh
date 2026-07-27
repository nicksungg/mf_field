#!/bin/bash
# Submit the full fair benchmark: 9 families × 15 datasets on pi_faez.
# Usage: bash bench/launch_bench.sh [EPOCHS] [SEED]
#   EPOCHS default 2500, SEED default 42.
# Skips (family,dataset) pairs whose result JSON already exists (resume-friendly).
set -euo pipefail
ROOT=/orcd/data/faez/001/nick/mf_field/factory_mffp
cd "$ROOT"
EPOCHS="${1:-2500}"
SEED="${2:-42}"

FAMILIES=(
    fno_mf_stack fno_coregionalization fno_coreg_residual
    transolver_residual transolver_attention_fusion
    v9_baseline
    mfrnp mf_deeponet d_mfd mf_fno_transfer
)
DATASETS=(
    ifc_heat ifc_poisson poisson_local heat_local fluid era5 pm_test
    advection_diffusion_generated allen_cahn_generated burgers_generated
    burgers_param_generated darcy_generated heat_generated
    lid_driven_cavity_generated poisson_generated
)

n=0; skipped=0
for fam in "${FAMILIES[@]}"; do
  for ds in "${DATASETS[@]}"; do
    out="results/raw_bench/${fam}__${ds}__e${EPOCHS}__s${SEED}.json"
    if [ -f "$out" ]; then skipped=$((skipped+1)); continue; fi
    sbatch bench/bench_one.sbatch "$fam" "$ds" "$EPOCHS" "$SEED" >/dev/null
    n=$((n+1))
  done
done
echo "submitted $n jobs (skipped $skipped already-done) at epochs=$EPOCHS seed=$SEED on pi_faez"
echo "watch: squeue -u $USER | grep mffp-bench | wc -l ; ls results/raw_bench | wc -l"
