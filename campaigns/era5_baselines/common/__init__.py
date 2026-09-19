"""Shared scaffold for the operator_library MF-FNO model catalog.

Every new family under operator_library/models/<family>/ forks from here:
  - `backbone`  : the FiLM-FNO primitives (SpectralConv2d, FiLMNorm, FNOBlock,
                  FNO2d, param_count) byte-compatible with the benchmark winner
                  `factory_mffp/models/mf_fno_transfer_film`, so each new model
                  isolates its NEW mechanism against the identical spectral
                  backbone.
  - `mffp`      : a sys.path shim onto factory_mffp + re-exports of the fair-eval
                  plumbing (load_mf_dataset, resolve_grid, finalize_and_write)
                  and the shared train/grid helpers (WORK_CAP, SMOKE, _cap_grid,
                  _modes, _to_grid, train_loop) so every family reports identical
                  metrics on the identical 256-cap working grid.
"""
