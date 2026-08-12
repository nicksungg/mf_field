#!/bin/bash
# Step 7 contract smoke for THIS cluster (Caltech HPC: partition=gpu, nested layout).
# Equivalent to factory_mffp/scripts/contract_smoke_test.sbatch, which is guarded
# and hardcodes mit_preemptable + the flat /orcd path, so it cannot run here.
#SBATCH --job-name=mffp-contract
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --gres=gpu:p100:1
#SBATCH --mem=32G
#SBATCH --time=00:20:00
#SBATCH --output=/resnick/groups/Hippo/ezeng/mf_field/logs_contract/contract_%j.out
#SBATCH --error=/resnick/groups/Hippo/ezeng/mf_field/logs_contract/contract_%j.err

set -euo pipefail
ROOT=/resnick/groups/Hippo/ezeng/mf_field
FACTORY="$ROOT/mf_field/factory_mffp"
source "$ROOT/.venv/bin/activate"
cd "$FACTORY"
mkdir -p results checkpoints

echo "[$(date)] host=$(hostname) part=${SLURM_JOB_PARTITION:-?} gpu=$(nvidia-smi -L | head -1)"
python -c "import torch; print('torch', torch.__version__, 'cuda_avail', torch.cuda.is_available())"

echo "[$(date)] running 2-epoch v9_baseline on ifc_heat..."
python references/v9_baseline/smoke_eval.py \
    --dataset_dir data/ifc_heat --dataset_name ifc_heat \
    --epochs 2 --out results/contract_test.json \
    --ckpt_dir checkpoints/contract_test --seed 0
echo "[$(date)] contract test JSON:"
cat results/contract_test.json
