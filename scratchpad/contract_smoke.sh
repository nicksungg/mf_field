#!/bin/bash
# BUILDER SMOKE (contract tier, 2 epochs). Not part of the card's grid.
#
# It reuses the PRODUCTION `COMMON_ENV` array by extracting it verbatim out of
# `scripts/01_train_eval.sh`, so the smoke cannot drift from what the SLURM job
# will actually pass. `$1` selects the dataset, `$2` the arm, `$3` the cond_set,
# `$4` the cap ("r1" resolves from the seal), `$5` the split seed, and any
# further arguments are appended to --env as OVERRIDES (used only to record the
# data-binding failure documented in state/blocked.md).
set -euo pipefail
cd "$(dirname "$0")/.."
WORKTREE="$(pwd)"
PROJECT_ROOT="/resnick/groups/Hippo/ezeng/mf_field"
ROUND_ROOT="$PROJECT_ROOT/mffp_autoresearch/round3"
EVAL_DIR="$PROJECT_ROOT/mffp_autoresearch/round2/eval"
PREREG_JSON="$ROUND_ROOT/state/r3s3_lf_value/prereg_knees_B3.json"
PREREG_SHA256="$("$PROJECT_ROOT/.venv/bin/python" -c "import json,sys;print(json.load(open(sys.argv[1]))['_payload_sha256'])" "$PREREG_JSON")"

DS="${1:?dataset}" ARM="${2:?arm}" CSET="${3:?cond_set}" CAP="${4:?cap}" SPLIT="${5:?split_seed}"
shift 5
if [[ "$CAP" == r[123] ]]; then
  CAP="$("$PROJECT_ROOT/.venv/bin/python" -c "import json,sys;print(json.load(open(sys.argv[1]))['payload']['cells'][sys.argv[2]]['ladder'][sys.argv[3]])" "$PREREG_JSON" "$DS" "$CAP")"
fi

# the PRODUCTION env block, verbatim
eval "$(sed -n '/^COMMON_ENV=(/,/^)/p' "$WORKTREE/scripts/01_train_eval.sh")"

TAG="${ARM}__${DS}__c${CAP}__d${SPLIT}"
OUT="$WORKTREE/scratchpad/smoke/$TAG"
mkdir -p "$OUT"
source "$PROJECT_ROOT/.venv/bin/activate"
export ROUND2_EVAL_RESULTS="$OUT/training"
export ROUND2_EVAL_CACHE="$OUT/cache"
mkdir -p "$ROUND2_EVAL_RESULTS" "$ROUND2_EVAL_CACHE"

echo "[smoke] $TAG cap=$CAP overrides=$*"
python "$EVAL_DIR/score_panel.py" \
    --family_dir "$WORKTREE/models_r3/r3s3_knee_prereg" \
    --datasets "$DS" --epochs 2 --seed 0 --no_cache \
    --out "$WORKTREE/scratchpad/contract_smoke_${TAG}.json" \
    --env "${COMMON_ENV[@]}" \
          "R3S3B3_ARM=$ARM" \
          "R3S3B3_LF_COND_SET=$CSET" \
          "R3S3B3_LF_COND_CAP=$CAP" \
          "R3S3B3_SPLIT_SEED=$SPLIT" \
          "$@"
