#!/bin/bash
# s6_local-B1: 200-epoch guard-set run for the promoted variant (analyzer
# recommendation before panel-win claim language finalizes).
#SBATCH --job-name=r1-s6_local-B1-guard200
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --gres=gpu:h100:1
#SBATCH --mem=32G
#SBATCH --time=01:00:00
#SBATCH --exclude=hpc-93-36
#SBATCH --requeue
#SBATCH --output=/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch_outputs/round1/s6_local/B1/slurm/%x_%j.out
#SBATCH --error=/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch_outputs/round1/s6_local/B1/slurm/%x_%j.err
set -euo pipefail
PROJECT_ROOT=/resnick/groups/Hippo/ezeng/mf_field
ROUND_ROOT="$PROJECT_ROOT/mffp_autoresearch/round1"
OUT="$PROJECT_ROOT/mffp_autoresearch_outputs/round1/s6_local/B1"
source "$PROJECT_ROOT/.venv/bin/activate"
export ROUND1_EVAL_RESULTS="$OUT/training"
ENV_ARGS=$(python3 - <<'PY'
import json
c = json.load(open("/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch/round1/experiment_cards/s6_local/batch_1/B1.json"))
env = dict(c["recipe"]["env"]); env["S6_VARIANT"] = "local_pixel_gate"
print(" ".join(f"{k}={v}" for k, v in env.items()))
PY
)
python "$ROUND_ROOT/eval/score_panel.py" \
  --family_dir "$ROUND_ROOT/worktrees/s6_local/B1/models_r1/s6_local_lf_corrector" \
  --datasets guard --epochs 200 --seed 0 --no_cache \
  --env $ENV_ARGS \
  --out "$OUT/eval/result_guard200_local_pixel_gate_s0.json"
