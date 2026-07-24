#!/bin/bash
# Launch the full EXP1 few-shot-HF grid:
#   mechanisms x N_HF x datasets x seeds, skipping any cell already done.
# Datasets chosen for enough HF samples to subsample: heat_local(1024),
# fluid(256), darcy_generated(160), poisson_local(64).
set -uo pipefail
ROOT=/orcd/data/faez/001/nick/mf_field/factory_mffp
cd "$ROOT"
EP="${EP:-2500}"
PART="${PART:-mit_normal_gpu}"
MECHS="transfer additive hf_only"
SEEDS="0 1 2"
# dataset:comma-separated N_HF list (<= that dataset's available HF count)
declare -a SPEC=(
  "heat_local:5,10,25,50,100"
  "fluid:5,10,25,50,100"
  "darcy_generated:5,10,25,50,100"
  "poisson_local:5,10,25,50"
)
n=0; skip=0
for entry in "${SPEC[@]}"; do
  ds="${entry%%:*}"; nhfs="${entry#*:}"
  for mech in $MECHS; do
    for nhf in ${nhfs//,/ }; do
      for seed in $SEEDS; do
        out="$ROOT/results/raw_fewshot/${mech}__${ds}__nhf${nhf}__s${seed}__e${EP}.json"
        if [ -f "$out" ]; then skip=$((skip+1)); continue; fi
        sbatch --partition="$PART" fewshot/fewshot_one.sbatch "$ds" "$mech" "$nhf" "$seed" "$EP" >/dev/null 2>&1
        n=$((n+1))
      done
    done
  done
done
echo "submitted $n cells (skipped $skip already-done) on $PART at epochs=$EP"
