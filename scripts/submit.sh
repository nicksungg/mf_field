#!/bin/bash
# r3s3_lf_value-B3 — submit seed 0 (the debug seed) only. Orchestrator-invoked.
#
# HARD ORDERING RULE (card part 3 phase P item 4): the phase-P seal must exist
# and match before ANY sbatch. 01_train_eval.sh re-checks it inside the job, but
# checking here too means a broken seal costs zero queue time and zero GPU
# minutes — and it makes the rule visible at the submission site, which is where
# it can actually be violated.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="/resnick/groups/Hippo/ezeng/mf_field"
PREREG_JSON="$PROJECT_ROOT/mffp_autoresearch/round3/state/r3s3_lf_value/prereg_knees_B3.json"

if [[ ! -f "$PREREG_JSON" ]]; then
  echo "[FATAL] pre-registration missing: $PREREG_JSON — run scripts/phase_p_prereg.py first (CPU only). No sbatch before the seal." >&2
  exit 2
fi
echo "[seal] $PREREG_JSON"
"$PROJECT_ROOT/.venv/bin/python" -c "import json,sys;s=json.load(open(sys.argv[1]));print('[seal] sealed_utc',s['_sealed_utc'],'sha256',s['_payload_sha256'])" "$PREREG_JSON"

jid=$(sbatch --parsable --job-name=r3-r3s3_lf_value-B3-s0 "$SCRIPT_DIR/01_train_eval.sh" 0)
echo "submitted seed 0: job $jid"
