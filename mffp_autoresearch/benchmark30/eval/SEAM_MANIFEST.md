# Vendored-scorer seam manifest (spec D3)

Origin: `mffp_autoresearch/round2/eval/{nrmse,panel_data,score_panel}.py` at `83a547e`.
The vendored copies differ from the originals in EXACTLY the seams below; `tests/test_vendor_integrity.py` enforces this (whitelist of changed definitions, append-only registry sets, byte-identity for everything else).

## seam (a) — baseline path (`score_panel.py::_load_baselines`)

Original reads `round2/eval/copylf_baselines.json`; vendored copy reads `benchmark30/state/copylf_baselines.json`, built by `eval/make_copylf_baselines_b30.py` with this vendored construction.
The `_copylf_def_hash` consistency check is unchanged and now binds to the VENDORED `panel_data.py` hash.

## seam (b) — registry appends (`panel_data.py` set literals; applied in task A5)

`PERIODIC_NODE_DATASETS` / `DIRICHLET_NODE_DATASETS` / `LEGACY_CELL_DATASETS` may only GROW (append-only), per ADR `docs/adr/0001-benchmark30-convention-registry.md`.
Pre-existing divergence preserved: `sharp__phase_field_crystal_2d` is routed via `SPECTRAL_RUNG_DATASETS` here (ADR r3-0005) while the vendored FAMILY's `upsample.py` lists it PERIODIC_NODE — intentional, exempted from the cross-copy equality guard (spec D4).

## seam (c) — config/data-root resolution (`panel_data.py::load_config`, `panel_data.py::load_split`)

`load_config` adapts `benchmark30/config.yaml` to the schema the eval layer expects (paths + panel + guard_set), with absolute `data_root`/`stripped_data_root`/`venv` and checkout-relative `factory_root`; adds the `dataset_dirs` per-dataset mapping.
`load_split` resolves `dataset_dir` through that mapping (era5 → `era5/era5_train_test`).

## zero-delta dependency

`nrmse.py` is copied byte-identically (import dependency of `score_panel.py`; `NRMSE_DEF_HASH` therefore matches round-2/3 results exactly).
