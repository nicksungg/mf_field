#!/usr/bin/env bash
# Install the MFFP round-3 subagent definitions into the user-level registry.
# Dispatch resolves subagent_type from ~/.claude/agents/, NOT from the repo —
# a repo commit alone does not take effect (documented round-4 footgun).
# Idempotent. Backs up the pre-existing (MFFP round-2) set once.
set -euo pipefail

SRC="$(cd "$(dirname "$0")/subagents" && pwd)"
DST="$HOME/.claude/agents"
BAK="$HOME/.claude/agents.mffp-round2.bak"

if [ -d "$DST" ] && [ ! -d "$BAK" ]; then
  cp -r "$DST" "$BAK"
  echo "backed up existing agents -> $BAK"
fi

mkdir -p "$DST/_shared"
changed=0
for f in "$SRC"/*.md "$SRC"/_shared/*.md; do
  rel="${f#"$SRC"/}"
  if ! cmp -s "$f" "$DST/$rel" 2>/dev/null; then
    cp "$f" "$DST/$rel"
    echo "installed: $rel"
    changed=$((changed + 1))
  fi
done
echo "done: $changed file(s) updated; $(ls "$DST"/*.md | wc -l) agents + $(ls "$DST/_shared"/*.md | wc -l) partials in registry"
