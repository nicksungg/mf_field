#!/usr/bin/env bash
# Source this file to activate the remote-factory environment on engaging:
#   source /orcd/data/faez/001/nick/mf_field/akash/remote-factory-main/activate-env.sh

# Drop the broken VIRTUAL_ENV pointer so uv stops warning
unset VIRTUAL_ENV

# Python 3.12 via miniforge module
module load miniforge/25.11.0-0

# uv installs to ~/.local/bin
export PATH="$HOME/.local/bin:$PATH"

# Project dir + node env (for claude CLI)
PROJECT_DIR="/orcd/data/faez/001/nick/mf_field/akash/remote-factory-main"
export PATH="$PROJECT_DIR/node-env/bin:$PATH"

# Activate the project venv that `uv sync` created
if [ -f "$PROJECT_DIR/.venv/bin/activate" ]; then
    source "$PROJECT_DIR/.venv/bin/activate"
fi

cd "$PROJECT_DIR"
echo "remote-factory env active"
echo "  python: $(python --version)"
echo "  uv:     $(uv --version)"
echo "  node:   $(node --version)"
echo "  claude: $(claude --version)"
echo "Run: factory --help    (or)    uv run python -m factory --help"
