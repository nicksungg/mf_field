# Shared environment loader for factory_mffp.
# Source this from any sbatch/shell script in this project.
#
# Two pythons are involved:
#   - The factory's own venv (~/akash/remote-factory-main/.venv) runs the `factory` CLI itself.
#   - This project's venv (factory_mffp/.venv) has torch + numpy + pandas for the model code.
# Both sit on top of the miniforge/25.11.0-0 module (Python 3.12).

unset VIRTUAL_ENV
module load miniforge/25.11.0-0
export PATH="$HOME/.local/bin:$PATH"

PROJECT_ROOT="${MFFP_PROJECT_ROOT:-/orcd/data/faez/001/nick/mf_field/factory_mffp}"
export MFFP_PROJECT_ROOT="$PROJECT_ROOT"
export MFFP_PY="$PROJECT_ROOT/.venv/bin/python"

# Factory CLI (only needed in some scripts)
export FACTORY_VENV=/orcd/data/faez/001/nick/mf_field/akash/remote-factory-main/.venv
export FACTORY_PY="$FACTORY_VENV/bin/python"
export PATH="$FACTORY_VENV/bin:$PATH"
export PATH="/orcd/data/faez/001/nick/mf_field/akash/remote-factory-main/node-env/bin:$PATH"

cd "$PROJECT_ROOT"
