#!/usr/bin/env bash
# Launch the factory in a tmux session with a sanitized env.
# Strips any leaked CLAUDE_CODE_*/CLAUDECODE/Vertex vars from the parent shell.

set -euo pipefail

PROJECT=/orcd/data/faez/001/nick/mf_field/factory_mffp
SESSION="${1:-mffp}"

# Kill any prior session first
tmux kill-session -t "$SESSION" 2>/dev/null || true

# Sanitize env: strip Claude Code's own session vars and any Vertex AI vars
# so that `claude` subprocesses spawn fresh and use the OAuth credentials at
# ~/.claude/.credentials.json (the default), not Vertex AI.
EXTRA_VARS=$(env | awk -F= '/^(CLAUDE_CODE_|CLAUDECODE|AI_AGENT|CLAUDE_AGENT_SDK|CLAUDE_EFFORT|CLAUDE_CODE_USE_VERTEX|CLOUD_ML_REGION|ANTHROPIC_VERTEX_|GOOGLE_APPLICATION_CREDENTIALS)/ {print $1}')
UNSET_CMD=""
for v in $EXTRA_VARS; do UNSET_CMD+="unset $v; "; done

# Inside the tmux session we need the same activate steps as scripts/env.sh.
# `factory run --loop` is the heartbeat command (factory ceo is single-shot).
# Trailing `; bash` keeps the pane alive after factory exits so we can inspect.
INNER="$UNSET_CMD source $PROJECT/scripts/env.sh && factory run $PROJECT --mode research --loop --interval 60 --no-github; echo '[factory run exited]'; exec bash"

tmux new-session -d -s "$SESSION" "bash -lc \"$INNER\"" \
  || { echo "tmux new-session failed"; exit 1; }

echo "Factory launched in tmux session: $SESSION"
echo "  tmux attach -t $SESSION"
echo "  tmux capture-pane -t $SESSION -p | tail -50"
echo "  tmux kill-session -t $SESSION"
