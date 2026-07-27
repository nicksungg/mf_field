#!/bin/bash
# GPU smoke gate: run all 10 models x 2 probe datasets at epochs=2 to catch
# OOM / shape / adapter bugs on real GPU before the full array. Probes:
#   era5            (per-fid different N, 128x256 working grid, cond_dim 12)
#   burgers_2d      (256x256 working grid — the OOM stress, sharp, 400 samples)
# Writes pass/fail to akash/results/smoke_gpu.csv. Outputs go to /tmp (discarded).
#SBATCH --job-name=akash-smoke
#SBATCH --partition=pi_faez,mit_normal_gpu,mit_preemptable
#SBATCH --exclude=node2901
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:1
#SBATCH --mem=96G
#SBATCH --time=02:00:00
#SBATCH --output=/orcd/data/faez/001/nick/mf_field/akash/logs/smoke_%j.out
#SBATCH --error=/orcd/data/faez/001/nick/mf_field/akash/logs/smoke_%j.err

set -uo pipefail
MF=/orcd/data/faez/001/nick/mf_field
cd "$MF/factory_mffp"; source scripts/env.sh; PY="$MFFP_PY"
mkdir -p "$MF/akash/logs" /tmp/akash_smoke_gpu

MODELS=(mf_fno_hyperfilm mf_fno_allpairs mf_fno_spectral mf_fno_richardson \
        mf_fno_ptr mf_fno_diffprior mf_fno_foundation mf_fno_lora \
        mf_fno_transfer_film mf_fno_transfer_bar)
PROBES=(era5 burgers_2d_generated)

CSV="$MF/akash/results/smoke_gpu.csv"
mkdir -p "$MF/akash/results"
echo "model,dataset,exit,nRMSE,secs" > "$CSV"

resolve_smoke() { for base in "$MF/akash/models" "$MF/factory_mffp/models"; do
    [ -f "$base/$1/smoke_eval.py" ] && { echo "$base/$1/smoke_eval.py"; return; }; done; }
resolve_ds() { for root in "$MF/factory_mffp/data" "$MF/sharp_generated" "$MF"; do
    [ -d "$root/$1" ] && { echo "$root/$1"; return; }; done; }

echo "[$(date)] smoke gate host=$(hostname) gpu=$(nvidia-smi -L 2>/dev/null | head -1)"
for m in "${MODELS[@]}"; do
  smoke=$(resolve_smoke "$m")
  for d in "${PROBES[@]}"; do
    dsdir=$(resolve_ds "$d")
    t0=$SECONDS
    "$PY" "$smoke" --dataset_dir "$dsdir" --dataset_name "$d" --epochs 2 \
        --out "/tmp/akash_smoke_gpu/${m}__${d}.json" \
        --ckpt_dir "/tmp/akash_smoke_gpu/ck_${m}__${d}" --seed 0 \
        > "/tmp/akash_smoke_gpu/${m}__${d}.log" 2>&1
    ec=$?; dt=$((SECONDS-t0))
    nr=$("$PY" -c "import json;d=json.load(open('/tmp/akash_smoke_gpu/${m}__${d}.json'));s=d['splits'];k=next(iter(s));print(round(s[k]['nRMSE'],4))" 2>/dev/null || echo NA)
    echo "${m},${d},${ec},${nr},${dt}" >> "$CSV"
    echo "[$(date)] $m $d exit=$ec nRMSE=$nr ${dt}s"
  done
done
echo "[$(date)] smoke gate complete -> $CSV"
