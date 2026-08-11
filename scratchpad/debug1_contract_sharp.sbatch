#!/bin/bash
# debug attempt 1 -- contract-tier (2-epoch) smoke of ONE SCORED SHARP CELL after
# the floor_matched_n shape-classifier fix. Debug evidence only; nothing here
# enters a card number (env_activation.md: direct smoke_eval is debug-only, so
# this goes through score_panel.py exactly as the real job does).
#
# On the login node this cell needs > 100 min (nproc = 1); on the H200 it is a
# couple of minutes, so the check runs where the real job runs.
#SBATCH --job-name=r3-B3-debug1-contract-sharp
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:nvidia_h200:1
#SBATCH --mem=64G
#SBATCH --time=00:30:00
#SBATCH --output=/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch/round3/worktrees/r3s2_field_reach/B3/scratchpad/debug1_contract/%x_%j.out
#SBATCH --error=/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch/round3/worktrees/r3s2_field_reach/B3/scratchpad/debug1_contract/%x_%j.err

set -euo pipefail
PROJECT_ROOT="/resnick/groups/Hippo/ezeng/mf_field"
W="$PROJECT_ROOT/mffp_autoresearch/round3/worktrees/r3s2_field_reach/B3"
E="$PROJECT_ROOT/mffp_autoresearch/round2/eval"
SCRATCH="$W/scratchpad/debug1_contract"

# the recipe's 74 env knobs, sourced VERBATIM from the real submit script
source "$SCRATCH/knobs.sh"

# never write into the frozen round-2 eval layer (recipe env._script_env)
export ROUND2_EVAL_RESULTS="$SCRATCH/gpu_results"
export ROUND2_EVAL_CACHE="$SCRATCH/gpu_cache"
mkdir -p "$ROUND2_EVAL_RESULTS" "$ROUND2_EVAL_CACHE" "$SCRATCH/eval"

source "$PROJECT_ROOT/.venv/bin/activate"
echo "[$(date)] host=$(hostname) gpu=$(nvidia-smi -L | head -1)"

python "$E/score_panel.py" \
    --family_dir "$W/models_r3/r3s2_ceiling" \
    --datasets sharp__allen_cahn_2d \
    --epochs 2 --seed 0 --no_cache \
    --out "$SCRATCH/eval/contract_sharp_ac_gpu.json" \
    --env "${ENV_KNOBS[@]}"

echo "[$(date)] contract sharp cell DONE"
cat "$SCRATCH/eval/contract_sharp_ac_gpu.json"
