#!/bin/bash
# Run the autonomous factory loop INSIDE a GPU allocation so its agents +
# scripts/cycle_eval.sh have a GPU. On the login node, cycle_eval's step-1 local
# score.py pass imports torch and probes CUDA, which HANGS on the contended
# login node until every agent wrapper times out (the prior run did 0 cycles in
# ~8h for this reason). With a GPU in-job, the local pass runs fast and the loop
# actually progresses.
#
# Bounded to 10 cycles via `factory run --max-cycles`. Partition mit_preemptable
# (2-day walltime fits ~10 cycles @ ~1-2h each); requeues on preemption.
#
# Launch:  sbatch bench/factory_gpu.sbatch
#
#SBATCH --job-name=mffp_factory_4c
#SBATCH --partition=pi_faez
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:1
#SBATCH --mem=96G
#SBATCH --time=12:00:00
#SBATCH --requeue
#SBATCH --output=/orcd/data/faez/001/nick/mf_field/factory_mffp/logs/factory_gpu_%j.out
#SBATCH --error=/orcd/data/faez/001/nick/mf_field/factory_mffp/logs/factory_gpu_%j.err

set -uo pipefail
PROJECT=/orcd/data/faez/001/nick/mf_field/factory_mffp
cd "$PROJECT"
mkdir -p logs

# Activate factory CLI + project venv (adds factory venv to PATH, sets MFFP_PY etc.)
source scripts/env.sh

# Sanitize env so nested `claude` agents use OAuth creds (~/.claude/.credentials.json),
# not this batch job's leaked Vertex/Claude-Code session vars.
for v in $(env | awk -F= '/^(CLAUDE_CODE_|CLAUDECODE|AI_AGENT|CLAUDE_AGENT_SDK|CLAUDE_EFFORT|CLAUDE_CODE_USE_VERTEX|CLOUD_ML_REGION|ANTHROPIC_VERTEX_|GOOGLE_APPLICATION_CREDENTIALS)/ {print $1}'); do
    unset "$v"
done

# Keep the per-cycle smoke eval on mit partitions too (cycle_eval.sh reads these).
# We already hold a GPU, so cycle_eval's local cached/uncached score.py runs here on
# the GPU; if it must submit run_smoke.sbatch it still targets mit.
export MFFP_PARTITION="${MFFP_PARTITION:-mit_preemptable}"
export MFFP_FALLBACK_PARTITION="${MFFP_FALLBACK_PARTITION:-mit_normal_gpu}"

echo "[$(date)] factory_gpu start on $(hostname)"
echo "[$(date)] gpu: $(nvidia-smi -L 2>/dev/null | head -1)"
echo "[$(date)] MFFP_PY=$MFFP_PY  partition=$MFFP_PARTITION fallback=$MFFP_FALLBACK_PARTITION"

# Bounded autonomous research loop: 10 cycles, no GitHub, 60s between cycles.
factory run "$PROJECT" --mode research --loop --max-cycles 4 --interval 60 --no-github

echo "[$(date)] factory run exited (max-cycles reached or error)"
