# Environment activation

For any python/bash that touches models, data, or the eval layer:

```bash
source "${PROJECT_ROOT}/.venv/bin/activate"     # torch 2.6 + numpy/scipy/yaml (python 3.9)
```

Notes:

- This is a **torch** project. No JAX flags, no MJX — those belong to the
  quadruped round and must not be cargo-culted here.
- Determinism env for anything that scores: the eval layer
  (`score_panel.py`) already sets `PYTHONHASHSEED=<seed>` and
  `CUBLAS_WORKSPACE_CONFIG=:4096:8` for its child processes — do NOT bypass
  it by invoking `smoke_eval.py` directly for scoring. Direct `smoke_eval.py`
  invocation is allowed only for debugging, never for numbers that enter a
  card.
- `pytest` for the eval layer's own tests needs the user-site path:
  `PYTHONPATH=/home/ezeng/.local/lib/python3.9/site-packages python -m pytest`
  (run from `${EVAL_DIR}`).
- Long jobs go through SLURM (`resource/logistics/slurm_rules.md`), never on
  the login node. Contract-tier (2-epoch) checks are login-node OK.
