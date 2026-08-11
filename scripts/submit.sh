#!/bin/bash
# r3s2_field_reach-B3 — submit seed 0 (the debug seed) only. ORCHESTRATOR-invoked.
# The builder never submits.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUT_DIR="/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch_outputs/round3/r3s2_field_reach/B3"
mkdir -p "$OUT_DIR/eval" "$OUT_DIR/slurm" "$OUT_DIR/training" "$OUT_DIR/cache"

jid=$(sbatch --parsable \
        --job-name="r3-r3s2_field_reach-B3-s0" \
        "$SCRIPT_DIR/01_train_eval.sh" 0)
echo "submitted seed 0: job $jid"
