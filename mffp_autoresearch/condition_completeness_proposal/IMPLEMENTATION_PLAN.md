# IC-Encoded Conditions in `mffp_sharp` — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Land the validated IC-encoding fix inside the `mffp_sharp` package (not beside it), make the condition-completeness certificate a generation gate, and produce the sample-round evidence for Nicholas's sign-off.

**Architecture:** One new `common/ic_encoding.py` module holds the band-limited IC construction (math copied verbatim from the validated `generate_learnable.py`).
Every stochastic-IC PDE module draws its 16 IC coefficients inside `sample_configs`'s Latin-hypercube design and exports them in `cond`/`param_names`, so `generate_sample` becomes a deterministic function of exported values plus per-dataset config constants.
A new `common/completeness.py` runs the nearest-pair witness and a generic reconstruction check at generation time; both generation entry points (`mffp_sharp/generate.py` h5 sample path and `generate_standardized.py` benchmark npz path) record the verdict and fail on INCOMPLETE unless the dataset block explicitly declares `stochastic_map: true`.

**Tech Stack:** numpy, scipy (`qmc`), pytest; repo-root `.venv` (Python 3.9) for local runs.

## Global Constraints

- LF is always a real coarse consistent solve — never downsampled or noised HF (`SURF_2026-main/CLAUDE.md`; nothing in this plan touches solvers or the ladder).
- Generator surface is mentor-owned: everything here lands on branch `mffp-trunk-eloise` as a reviewable package; no full generation runs before Nicholas's sign-off (SURF sample-round gate).
- IC math must be byte-identical to `mf_field_eloise_data/generate_learnable.py` (`K1D=8`, `M2D=3`, max-abs normalization to `scale`) — that construction is already validated on 9 regenerated variants, and the existing `cahn_hilliard` benchmark's reconstruction certificate pins it.
- Per-module IC amplitude keeps the original module's amplitude convention exactly (see table in Task 2) so solver regimes do not shift.
- The ladder-fix patch (`mffp_autoresearch/ladder_fix_proposal/ladder_fix.patch`) touches `common/io.py`, `common/ladder.py`, `generate.py`, and two scripts; edits here must keep `git apply --check` green for that patch (verified in Task 9).
- Condition-vector size: 16 IC coefficients per dataset (the `cahn_hilliard` precedent, 19 total dims, is the accepted envelope; the ≤ ~10 guideline is already superseded there — flagged for Nicholas in the proposal).

## Stochastic-IC audit (grounds the scope)

`rng` used inside `generate_sample` (the defect): allen_cahn, cahn_hilliard, fisher_kpp, gray_scott, kdv, kuramoto_sivashinsky, nls, phase_field_crystal, sine_gordon, swift_hohenberg.
Clean (randomness only in `sample_configs`, fully exported as scalars): burgers, euler, helmholtz, porous_medium, shallow_water, sod.
Regeneration scope stays the three panel datasets (pfc / fisher_kpp / allen_cahn); the other seven module fixes are durability (the package path must stop reproducing the bug for anything generated through it).

---

### Task 1: `common/ic_encoding.py` + tests

**Files:**
- Create: `mf_field_eloise_data/SURF_2026-main/mffp_sharp/src/mffp_sharp/common/ic_encoding.py`
- Test: `mf_field_eloise_data/SURF_2026-main/mffp_sharp/tests/test_ic_encoding.py`

**Interfaces:**
- Produces: `K1D=8`, `M2D=3`, `n_coeffs(ndim)->int` (16 for both), `ic_names(ndim)->list[str]` (`["ic_c0"…"ic_c15"]`), `ic_ranges(ndim)->dict[str,tuple]` (each `(-1.0, 1.0)`), `ic_1d(coeffs, res, scale)`, `ic_2d(coeffs, res, scale)`, `build_ic(coeffs, res, scale, ndim)`, `coeffs_from_spec(spec, ndim)->np.ndarray`.

- [ ] **Step 1: Write failing tests** — determinism; `max|ic| == scale` (normalization); 1D spectral support only in modes `1..K1D`; 2D support only in `|kx|,|ky| < M2D`; `build_ic` dispatch; `ic_ranges` has 16 entries both ndims; `coeffs_from_spec` ordering `ic_c0..ic_c15`.
- [ ] **Step 2: Run tests, verify FAIL (module not found).**
- [ ] **Step 3: Implement.** `ic_1d`/`ic_2d` bodies copied verbatim from `generate_learnable.py:23-40` (the `M2D` module constant replaces the script global).
- [ ] **Step 4: Run tests, verify PASS.**
- [ ] **Step 5: Commit** `mffp_sharp: add common/ic_encoding (validated band-limited IC, single source of truth)`.

### Task 2: Fix the three panel modules (fisher_kpp, allen_cahn, phase_field_crystal)

**Files:**
- Modify: `src/mffp_sharp/pdes/fisher_kpp.py`, `allen_cahn.py`, `phase_field_crystal.py`
- Test: `tests/test_fisher_kpp.py`, `tests/test_allen_cahn.py`, `tests/test_phase_field_crystal.py` (update names assertions; add completeness test per module)

**The uniform edit pattern** (shown for fisher_kpp; the others substitute per the table):

```python
# sample_configs: add the 16 IC coeffs to the LHS design
draws = latin_hypercube(
    {"D": tuple(sampling_cfg["D_range"]),
     "r": tuple(sampling_cfg["r_range"]),
     **ic_encoding.ic_ranges(ndim)}, n, seed)
return [{"D": draws["D"][i], "r": draws["r"][i],
         **{k: draws[k][i] for k in ic_encoding.ic_names(ndim)},
         "domain_size": sampling_cfg["domain_size"], "ndim": ndim,
         "seed": seed + i} for i in range(n)]   # seed kept for provenance; IC no longer reads it

# generate_sample: deterministic IC from exported coefficients (replaces the rng lines)
coeffs = ic_encoding.coeffs_from_spec(spec, ndim)
ic_coarse = 0.5 + ic_encoding.build_ic(coeffs, res_min, 0.5, ndim)

# cond/names: append the coefficients
cond = np.array([spec["D"], spec["r"], *coeffs], dtype=np.float64)
names = ["D", "r"] + ic_encoding.ic_names(ndim)
```

| module | IC line (new) | amplitude rationale |
|---|---|---|
| fisher_kpp | `0.5 + build_ic(coeffs, res_min, 0.5, ndim)` | original was `0.5 + 0.5*U(-1,1)` spanning [0,1]; max-abs normalization keeps [0,1] exactly |
| allen_cahn | `spec["mean_composition"] + build_ic(coeffs, res_min, 0.1, ndim)` | original amplitude 0.1 |
| phase_field_crystal | `spec["mean_density"] + build_ic(coeffs, res_min, spec["ic_amplitude"], 2)` | `ic_amplitude` stays the config constant it already is |

Per-module completeness test (the TDD anchor, e.g. fisher_kpp):

```python
def test_field_is_function_of_exported_cond_only():
    cfg = {"D_range": [1e-4, 1e-3], "r_range": [5.0, 20.0], "domain_size": 1.0}
    spec = fk.sample_configs(1, cfg, ndim=2, seed=7)[0]
    fields, cond, names = fk.generate_sample(spec, [16, 32], 32, output_time=5 * fk._DT)
    # rebuild the spec STRICTLY from exported values + config constants — no seed
    spec2 = dict(zip(names, cond.tolist()))
    spec2.update({"domain_size": 1.0, "ndim": 2})
    fields2, cond2, _ = fk.generate_sample(spec2, [16, 32], 32, output_time=5 * fk._DT)
    assert np.array_equal(fields[32], fields2[32])
    assert np.array_equal(cond, cond2)
    assert [n for n in names if n.startswith("ic_c")] == ic_encoding.ic_names(2)
```

- [ ] Steps per module: update tests (fail) → edit module → tests pass → commit (three commits: `mffp_sharp: IC-encoded conditions for <module>`).

### Task 3: Fix the six script-covered stochastic modules

**Files:**
- Modify: `src/mffp_sharp/pdes/{cahn_hilliard,kuramoto_sivashinsky,sine_gordon,swift_hohenberg,kdv,nls}.py`
- Test: corresponding `tests/test_*.py` (update names/determinism assertions; add the same completeness test shape)

Same pattern as Task 2. IC lines:

| module | IC line (new) |
|---|---|
| cahn_hilliard | `spec["mean_composition"] + build_ic(coeffs, res_min, 0.1, 2)` (matches `generate_learnable` CH `scale=0.1`) |
| kuramoto_sivashinsky | `build_ic(coeffs, res_min, spec["ic_amplitude"], ndim)` |
| sine_gordon | `build_ic(coeffs, res_min, spec["ic_amplitude"], ndim)` |
| swift_hohenberg | `build_ic(coeffs, res_min, spec["ic_amplitude"], ndim)` |
| kdv | `build_ic(coeffs, res_min, spec["ic_amplitude"], 1)` |
| nls | `build_ic(coeffs, res_min, spec["ic_amplitude"], 1)` (then `.astype(complex)` as today) |

Modules where `ic_amplitude` is itself an exported cond param (ks, sg, sh, kdv, nls) keep it exported; the coeffs are appended after it.

- [ ] Update tests → fail → edit → pass → one commit `mffp_sharp: IC-encoded conditions for the six script-covered stochastic modules`.

### Task 4: Fix gray_scott (two-field IC)

**Files:**
- Modify: `src/mffp_sharp/pdes/gray_scott.py`; Test: `tests/test_gray_scott.py`

One coefficient set perturbs both `u0c` and `v0c` at the original 0.01 amplitude (the noise only breaks the square-seed symmetry; one shared band-limited field does that deterministically while keeping the export at 16 coeffs):

```python
pert = ic_encoding.build_ic(coeffs, res_min, 0.01, 2)
u0c += pert
v0c += pert
```

- [ ] Same TDD cycle; commit `mffp_sharp: IC-encoded conditions for gray_scott`.

### Task 5: `common/completeness.py` + tests

**Files:**
- Create: `src/mffp_sharp/common/completeness.py`; Test: `tests/test_completeness.py`

**Interfaces:**
- Produces: `CompletenessError(RuntimeError)`; `nearest_pair_witness(x, y) -> dict` (ported from `certify_condition_completeness.py` — keys `standardized_condition_distance`, `relative_field_difference`, `median_pair_distance`, plus indices); `reconstruction_check(mod, cond, names, const, resolutions, hf_res, output_time, stored_hf) -> dict` (builds `spec = {**const, **dict(zip(names, cond))}`, re-runs `mod.generate_sample`, rel-L2 vs `stored_hf`, verdict COMPLETE iff `< 1e-9`); `certify(mod, x, y_hf, names, const, resolutions, hf_res, output_time, n_reconstruct=2, declared_stochastic=False) -> dict` (witness + per-sample reconstruction; verdict COMPLETE / STOCHASTIC_DECLARED / INCOMPLETE; raises `CompletenessError` on INCOMPLETE unless declared).
- Consumes: any fixed module's `generate_sample` (Task 2-4 signatures).

Tests: witness flags a synthetic incomplete set (two identical conds, O(1)-different fields); `certify` returns COMPLETE for fixed fisher_kpp at tiny res; a stub module reproducing the old unexported-rng behavior raises `CompletenessError`; `declared_stochastic=True` records the verdict without raising.

- [ ] TDD cycle; commit `mffp_sharp: completeness certificate as a library (witness + generic reconstruction)`.

### Task 6: Wire the gate into `mffp_sharp/generate.py`

**Files:**
- Modify: `src/mffp_sharp/generate.py` (collect raw HF fields in the loop; after the loop run `completeness.certify` with `const` built from `block["sampling"]`'s non-`*_range` scalars + `ndim` + `seed 0` placeholder; verdict into `summary["condition_completeness"]`; `SystemExit` on `CompletenessError` unless `block.get("stochastic_map")`).
- Test: `tests/test_generate_gate.py` (drive `generate_dataset` on a 2-sample fisher_kpp block at res [8,16] and assert the summary carries verdict COMPLETE).
- Constraint: hunks must not overlap `ladder_fix.patch`'s `generate.py` hunks (checked in Task 9).

- [ ] TDD cycle; commit `mffp_sharp: completeness gate on the h5 sample-generation path`.

### Task 7: Wire the gate into `generate_standardized.py` + local-run overrides

**Files:**
- Modify: `mf_field_eloise_data/generate_standardized.py`

Changes: `--out_root`, `--cfg`, `--ablation` CLI overrides (default to today's cluster constants, enabling the local sample round); a `_certify_and_record(block, mod, ndim, rungs, X, Y_hf, names)` helper called from both the direct-write path and `merge_shards`; the returned record written into `meta.json` as `condition_completeness`; hard `SystemExit` on `CompletenessError` unless the block carries `stochastic_map: true`; when a dataset is deliberately stochastic, `meta.json` additionally records `stochastic_map_semantics` (declared floor numbers per the proposal §3).

- [ ] Implement + smoke locally (2-sample run) + commit `generate_standardized: completeness gate writes condition_completeness into meta.json; local-run overrides`.

### Task 8: Dedupe `generate_learnable.py`

- Modify: `mf_field_eloise_data/generate_learnable.py` to `from mffp_sharp.common.ic_encoding import ic_1d, ic_2d, K1D, M2D` (bodies deleted, behavior identical — pinned by the CH reconstruction certificate which reproduces the existing benchmark from stored `x`).
- [ ] Commit `generate_learnable: import IC construction from the package (single source of truth)`.

### Task 9: Full verification

- [ ] Full pytest suite in `.venv` — all files, including the untouched-module tests.
- [ ] Grep `scripts/` for hand-built spec dicts passed to `generate_sample`; fix any that now lack `ic_c*` keys.
- [ ] `git apply --check mffp_autoresearch/ladder_fix_proposal/ladder_fix.patch` still green (Task 3 of the handoff).
- [ ] Run `certify_condition_completeness.py` unchanged against the CURRENT benchmark data (~50 s) — confirms the audit numbers are still reproduced and the proposal package's own script is unaffected.

### Task 10: Local sample round (the SURF-gate artifact)

- [ ] Local ablation stub pinning the production ladders from the existing benchmark metas (fk 2d [64,128,256]; ac 2d and pfc from their metas).
- [ ] `python generate_standardized.py <variant> --ntrain 8 --ntest 2 --out_root <local>` for `phase_field_crystal_2d`, `fisher_kpp_2d`, `allen_cahn_2d` through the FIXED package.
- [ ] Verify each output `meta.json` carries `condition_completeness.verdict == COMPLETE` (reconstruction rel-L2 ≤ 1e-9) and `param_names` ends with `ic_c0..ic_c15`.
- [ ] Sample figures via the package `visualize.one_pager` for Nicholas's visual review.
- [ ] Commit sample-round summaries (small JSON/figures only; field data stays git-ignored).

## Follow-ups outside this plan (tracked separately)

Round-3 program note (process fixes); consolidated sign-off package + regeneration/anchor/round-3 launch plan (all operator- and mentor-gated).
