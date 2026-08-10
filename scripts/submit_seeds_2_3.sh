#!/bin/bash
# r3s2_field_reach-B2 — submit seeds 1 and 2 in parallel, AFTER the seed-0 gate.
# ORCHESTRATOR-invoked (in-round seed confirm, PROGRAM_NOTE MUST 4: only for a
# CLAIMABLE card, as a close precondition). The card recipe declares seeds
# [0, 1, 2]; this script submits the two confirm seeds.
# The guard-set invocation inside 01_train_eval.sh runs on seed 0 only.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUT_DIR="/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch_outputs/round3/r3s2_field_reach/B2"
mkdir -p "$OUT_DIR/eval" "$OUT_DIR/slurm" "$OUT_DIR/training" "$OUT_DIR/cache"

for s in 1 2; do
  jid=$(sbatch --parsable \
          --job-name="r3-r3s2_field_reach-B2-s${s}" \
          "$SCRIPT_DIR/01_train_eval.sh" "$s")
  echo "submitted seed $s: job $jid"
done
