#!/bin/bash
# One-off contract validation: 2-epoch run on ifc_heat with v9_baseline.
# Confirms: env loads, GPU visible, dataset readable, smoke_eval.py contract holds.
#SBATCH --job-name=mffp-contract
#SBATCH --partition=mit_preemptable
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --gres=gpu:1
#SBATCH --mem=32G
#SBATCH --time=00:20:00
#SBATCH --output=logs/contract_%j.out
#SBATCH --error=logs/contract_%j.err

set -euo pipefail
cd /orcd/data/faez/001/nick/mf_field/factory_mffp
mkdir -p logs results checkpoints
source scripts/env.sh

echo "[$(date)] host=$(hostname) part=$SLURM_JOB_PARTITION gpu=$(nvidia-smi -L | head -1)"
"$MFFP_PY" -c "import torch; print('torch', torch.__version__, 'cuda_avail', torch.cuda.is_available())"

echo "[$(date)] running 2-epoch v9_baseline on ifc_heat..."
"$MFFP_PY" models/v9_baseline/smoke_eval.py \
    --dataset_dir data/ifc_heat --dataset_name ifc_heat \
    --epochs 2 --out results/contract_test.json \
    --ckpt_dir checkpoints/contract_test --seed 0
echo "[$(date)] contract test JSON:"
cat results/contract_test.json
