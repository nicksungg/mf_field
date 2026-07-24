#!/bin/bash
# Fair benchmark as a SLURM job ARRAY (robust: no login-node daemon needed).
# 9 families × 15 datasets = 135 tasks. Throttle concurrency with --array=...%N.
# Submit with:  sbatch --array=0-134%40 bench/bench_array.sbatch [EPOCHS] [SEED]
# Resume-friendly: a task whose result JSON already exists exits immediately;
# otherwise it trains (resuming from checkpoints/bench/<fam>/<ds>/last.pt).
#SBATCH --job-name=mffp-arr
#SBATCH --partition=mit_normal_gpu,mit_preemptable
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:1
#SBATCH --mem=96G
#SBATCH --time=06:00:00
#SBATCH --requeue
#SBATCH --signal=B:USR1@120
#SBATCH --output=/orcd/data/faez/001/nick/mf_field/factory_mffp/logs/arr_%A_%a.out
#SBATCH --error=/orcd/data/faez/001/nick/mf_field/factory_mffp/logs/arr_%A_%a.err

set -euo pipefail
ROOT=/orcd/data/faez/001/nick/mf_field/factory_mffp
cd "$ROOT"
source scripts/env.sh
PY="$MFFP_PY"
EPOCHS="${1:-2500}"; SEED="${2:-42}"

FAMILIES=(fno_mf_stack fno_coregionalization fno_coreg_residual
          transolver_residual transolver_attention_fusion v9_baseline
          mfrnp mf_deeponet d_mfd mf_fno_transfer)
DATASETS=(ifc_heat ifc_poisson poisson_local heat_local fluid era5 pm_test
          advection_diffusion_generated allen_cahn_generated burgers_generated
          burgers_param_generated darcy_generated heat_generated
          lid_driven_cavity_generated poisson_generated)

IDX="${SLURM_ARRAY_TASK_ID:?array task id required}"
NDS=${#DATASETS[@]}
fam="${FAMILIES[$((IDX / NDS))]}"
ds="${DATASETS[$((IDX % NDS))]}"

OUT="$ROOT/results/raw_bench/${fam}__${ds}__e${EPOCHS}__s${SEED}.json"
CKPT="$ROOT/checkpoints/bench/${fam}/${ds}"
if [ -f "$OUT" ]; then echo "[skip] $OUT exists"; exit 0; fi
mkdir -p "$CKPT" "$ROOT/results/raw_bench" "$ROOT/logs"

SMOKE=""
for base in "models" "references" "references/external_sota"; do
    [ -f "$ROOT/$base/$fam/smoke_eval.py" ] && { SMOKE="$ROOT/$base/$fam/smoke_eval.py"; break; }
done
[ -z "$SMOKE" ] && { echo "ERROR: no smoke_eval for $fam" >&2; exit 2; }

echo "[$(date)] task=$IDX family=$fam dataset=$ds epochs=$EPOCHS host=$(hostname)"
trap 'echo "[$(date)] USR1 — ckpt saved, exit for requeue"; sleep 25; exit 0' USR1
"$PY" "$SMOKE" --dataset_dir "$ROOT/data/${ds}" --dataset_name "${ds}" \
    --epochs "$EPOCHS" --out "$OUT" --ckpt_dir "$CKPT" --seed "$SEED"
echo "[$(date)] done -> $OUT"
