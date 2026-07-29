#!/bin/bash
# Template: submit seeds 1 and 2 in parallel, AFTER the seed-0 gate passes.
# (Round-1 seeds are {0,1,2}; this file keeps the round-5 name so the
#  orchestrator flow reads the same.)
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
for s in 1 2; do
  jid=$(sbatch --parsable "$SCRIPT_DIR/01_train_eval.sh" "$s")
  echo "submitted seed $s: job $jid"
done
