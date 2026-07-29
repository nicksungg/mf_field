# MFFP Autoresearch Round 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and launch `mffp_autoresearch/round1/` — the round-5b AI-Scientist scaffold ported to MFFP with its own eval layer — per `docs/superpowers/specs/2026-07-28-mffp-autoresearch-design.md`.

**Architecture:** A new top-level round directory holds the whole system: `project.yaml` (config surface), `program.md` (the shared spec), 9 subagent prompts + `_shared/` partials (source of truth, installed to `~/.claude/agents/` at launch), and an eval layer whose single nRMSE definition and copy-LF-skill panel score every card cites. Experiments run in git worktrees; SLURM executes; a cron-pulsed orchestrator session drives.

**Tech Stack:** Python 3 (repo root `.venv`: torch 2.6, numpy, scipy), pytest (user-site install), git worktrees, SLURM (Caltech HPC `gpu` partition), Claude Code agents/crons.

## Global Constraints

- **Never edit** `mf_field/factory_mffp/{eval,baselines,references,scripts,data}/`, `factory.md`, `benchmark_42/**`, or `mf_field/akash/**`. Importing from them read-only is allowed.
- One nRMSE definition for the whole round: per-sample `||pred − hf||₂ / ||hf||₂`, mean over test samples (spec §2). Every score flows through `round1/eval/nrmse.py`.
- Panel (spec §3.2): `ext__helmholtz_2d`, `sharp__phase_field_crystal_2d`, `sharp__allen_cahn_2d`, `sharp__fisher_kpp_2d`, `sharp__cahn_hilliard`, `ifc_poisson`. Guard set: `heat_local`, `fluid`, `sharp__sod_1d`. Dataset dirs: `mf_field/factory_mffp/data/<name>/`.
- Seeds fixed at {0, 1, 2}; tiers: contract = 2 epochs, smoke = 200 epochs, full = 2500 epochs (champions only, human-approved).
- Family CLI is the existing contract (`mf_field/factory_mffp/eval/MODEL_CONTRACT.md`): `smoke_eval.py --dataset_dir --dataset_name --epochs --out --ckpt_dir --seed`, results JSON with `model`, `dataset`, `splits.{train,test,ood}.nRMSE`.
- Assertions, not defaults, at every component seam (spec §5.3). A missing input is a raised error, never a silent fallback.
- Python: `source /resnick/groups/Hippo/ezeng/mf_field/.venv/bin/activate` (torch available). Tests: `python -m pytest` (install once with `pip install --user pytest` if missing).
- Commits: small, per task, on `mffp-trunk-eloise`. Round1 heavy artifacts (results JSONs, checkpoints) are git-ignored; code/config/docs are committed. End commit messages with the Claude co-author line.

---

### Task 1: Round scaffold + `project.yaml` + gitignore

**Files:**
- Create: `mffp_autoresearch/round1/project.yaml`
- Create: `mffp_autoresearch/round1/.gitignore`
- Create: `mffp_autoresearch/round1/docs/adr/0001-round1-port-decisions.md`
- Create (empty `.gitkeep`): `mffp_autoresearch/round1/{experiment_cards,websearches,brainstormer,worktrees,tools,state,eval}/`

**Interfaces:**
- Produces: `project.yaml` keys consumed by every later task: `paths:` (`round_root`, `outputs_root`, `venv`, `factory_root`, `data_root`, `eval_dir`), `panel:` (list of 6), `guard_set:` (list of 3), `streams:` (5 entries `{name, class, question}`), `seed_protocol: {seeds: [0,1,2], cratered_skill_factor: 1.5}`, `tiers: {contract_epochs: 2, smoke_epochs: 200, full_epochs: 2500}`, `caps: {slurm_algo_attempts: 5, review_fail_attempts: 3, consecutive_skips_for_stream_abandonment: 3}`, `crons: {orchestrator_pulse_min: 10, maintainer_min: 20}`, `sbatch: {partition: gpu, gres: "gpu:p100:1"}`.

- [ ] **Step 1: Create directories and `.gitkeep`s**

```bash
cd /resnick/groups/Hippo/ezeng/mf_field
mkdir -p mffp_autoresearch/round1/{experiment_cards,websearches,brainstormer,worktrees,tools,state/anchors,eval/tests,docs/adr,subagents/_shared,resource/logistics}
touch mffp_autoresearch/round1/{experiment_cards,websearches,brainstormer,worktrees,tools,state/anchors}/.gitkeep
```

- [ ] **Step 2: Write `project.yaml`**

All paths relative to the repo root (Layer-A portability, resolved at runtime via `git rev-parse --show-toplevel`):

```yaml
round: round1
paths:
  round_root: mffp_autoresearch/round1
  outputs_root: mffp_autoresearch_outputs/round1     # sibling-of-round outputs, git-ignored
  venv: .venv
  factory_root: mf_field/factory_mffp
  data_root: mf_field/factory_mffp/data
  eval_dir: mffp_autoresearch/round1/eval
panel:
  - ext__helmholtz_2d
  - sharp__phase_field_crystal_2d
  - sharp__allen_cahn_2d
  - sharp__fisher_kpp_2d
  - sharp__cahn_hilliard
  - ifc_poisson
guard_set: [heat_local, fluid, sharp__sod_1d]
streams:
  - {name: s1_poisson,       class: gap,    question: "why is ifc_poisson above the paper bar (0.036), and what closes it?"}
  - {name: s2_beyond_copy,   class: gap,    question: "why does every fusion mechanism lose to copy-LF on the five sharp-2D panel datasets?"}
  - {name: s3_testtime,      class: lever,  question: "how far does test-time refinement go when the governing residual is real?"}
  - {name: s4_hybrid_routing, class: lever, question: "can MF compositions of hybrid operators capture the +30.6% FNO<->Transolver oracle?"}
  - {name: s5_tuning,        class: tuning, question: "how much of the gap is knobs, not architecture?"}
seed_protocol: {seeds: [0, 1, 2], cratered_skill_factor: 1.5}
tiers: {contract_epochs: 2, smoke_epochs: 200, full_epochs: 2500}
caps: {slurm_algo_attempts: 5, review_fail_attempts: 3, consecutive_skips_for_stream_abandonment: 3}
crons: {orchestrator_pulse_min: 10, maintainer_min: 20}
sbatch: {partition: gpu, gres: "gpu:p100:1", account: null}
```

- [ ] **Step 3: Write `round1/.gitignore`** (heavy artifacts out, code/config in)

```gitignore
worktrees/
state/timing_ledger.json
eval/results/
eval/cache/
__pycache__/
```

(Repo-root `.gitignore` already excludes `*.npz *.npy *.pt *.h5`; add `mffp_autoresearch_outputs/` to the **repo-root** `.gitignore` — that file is not guarded.)

- [ ] **Step 4: Write ADR 0001** — one page recording the port decisions already fixed by the spec (round5b base, no oracle, mixed streams, copy-LF-skill objective, eval outside guards) with a pointer to the spec. This is the round's ADR trail seed.

- [ ] **Step 5: Verify and commit**

```bash
python -c "import yaml; yaml.safe_load(open('mffp_autoresearch/round1/project.yaml'))" \
  && git add mffp_autoresearch .gitignore && git commit -m "round1: scaffold + project.yaml"
```

---

### Task 2: `eval/nrmse.py` — the one metric definition

**Files:**
- Create: `mffp_autoresearch/round1/eval/nrmse.py`
- Test: `mffp_autoresearch/round1/eval/tests/test_nrmse.py`

**Interfaces:**
- Produces (consumed by Tasks 3, 4, 5, 14):
  - `nrmse(pred: np.ndarray, target: np.ndarray) -> float` — both `(N, n_cells)`; per-sample relative L2, mean over N. Raises `ValueError` on shape mismatch or non-finite inputs.
  - `skill(model_nrmse: float, copylf_nrmse: float) -> float` — ratio; raises if `copylf_nrmse <= 0`.
  - `panel_geomean(skills: dict[str, float]) -> float` — geomean over values; raises on empty or non-positive.
  - `bootstrap_ci(per_seed_values: list[float], n_boot: int = 10000, seed: int = 0) -> tuple[float, float, float]` — returns `(mean, lo95, hi95)` percentile bootstrap over seeds.
  - `NRMSE_DEF_HASH: str` — sha256 of this file's own source text (seam assertion token, spec §5.3).

- [ ] **Step 1: Write the failing tests**

```python
# mffp_autoresearch/round1/eval/tests/test_nrmse.py
import numpy as np
import pytest
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from nrmse import nrmse, skill, panel_geomean, bootstrap_ci, NRMSE_DEF_HASH

def test_nrmse_zero_for_perfect_prediction():
    y = np.random.default_rng(0).normal(size=(5, 64))
    assert nrmse(y, y) == pytest.approx(0.0)

def test_nrmse_one_for_zero_prediction():
    y = np.random.default_rng(0).normal(size=(5, 64))
    assert nrmse(np.zeros_like(y), y) == pytest.approx(1.0)

def test_nrmse_is_mean_of_per_sample_ratios():
    y = np.ones((2, 4)); p = y.copy(); p[1] *= 3.0   # sample errors: 0 and 2
    assert nrmse(p, y) == pytest.approx(1.0)

def test_nrmse_rejects_shape_mismatch_and_nan():
    y = np.ones((2, 4))
    with pytest.raises(ValueError): nrmse(np.ones((2, 5)), y)
    bad = y.copy(); bad[0, 0] = np.nan
    with pytest.raises(ValueError): nrmse(bad, y)

def test_skill_and_geomean():
    assert skill(0.05, 0.10) == pytest.approx(0.5)
    with pytest.raises(ValueError): skill(0.05, 0.0)
    assert panel_geomean({"a": 0.25, "b": 4.0}) == pytest.approx(1.0)
    with pytest.raises(ValueError): panel_geomean({})

def test_bootstrap_ci_brackets_mean_and_is_deterministic():
    vals = [0.10, 0.12, 0.11]
    m, lo, hi = bootstrap_ci(vals)
    assert lo <= m <= hi and m == pytest.approx(np.mean(vals))
    assert bootstrap_ci(vals) == bootstrap_ci(vals)

def test_def_hash_is_stable_sha256():
    assert len(NRMSE_DEF_HASH) == 64
```

- [ ] **Step 2: Run tests, verify they fail** — `cd mffp_autoresearch/round1/eval && python -m pytest tests/test_nrmse.py -v` → import error (`nrmse` not defined).

- [ ] **Step 3: Implement `nrmse.py`**

```python
"""The round's single nRMSE definition (spec §2). Every score cites this file.

nRMSE(pred, target) = mean_i ||pred_i - target_i||_2 / ||target_i||_2
"""
from __future__ import annotations
import hashlib, pathlib
import numpy as np

def nrmse(pred: np.ndarray, target: np.ndarray) -> float:
    pred, target = np.asarray(pred, dtype=np.float64), np.asarray(target, dtype=np.float64)
    if pred.shape != target.shape or pred.ndim != 2:
        raise ValueError(f"shape mismatch or not 2-D: pred {pred.shape} vs target {target.shape}")
    if not (np.isfinite(pred).all() and np.isfinite(target).all()):
        raise ValueError("non-finite values in pred or target")
    denom = np.linalg.norm(target, axis=1)
    if (denom == 0).any():
        raise ValueError("zero-norm target sample")
    return float(np.mean(np.linalg.norm(pred - target, axis=1) / denom))

def skill(model_nrmse: float, copylf_nrmse: float) -> float:
    if copylf_nrmse <= 0:
        raise ValueError(f"copy-LF nRMSE must be positive, got {copylf_nrmse}")
    return float(model_nrmse) / float(copylf_nrmse)

def panel_geomean(skills: dict[str, float]) -> float:
    vals = np.array(list(skills.values()), dtype=np.float64)
    if vals.size == 0 or (vals <= 0).any():
        raise ValueError(f"skills must be non-empty and positive: {skills}")
    return float(np.exp(np.mean(np.log(vals))))

def bootstrap_ci(per_seed_values, n_boot: int = 10000, seed: int = 0):
    vals = np.asarray(per_seed_values, dtype=np.float64)
    if vals.size == 0:
        raise ValueError("no values")
    rng = np.random.default_rng(seed)
    boots = rng.choice(vals, size=(n_boot, vals.size), replace=True).mean(axis=1)
    return float(vals.mean()), float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))

NRMSE_DEF_HASH = hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
```

- [ ] **Step 4: Run tests, verify all pass.**
- [ ] **Step 5: Commit** — `git add mffp_autoresearch/round1/eval && git commit -m "round1 eval: single nRMSE definition + CI helpers"`

---

### Task 3: `eval/panel_data.py` — panel access + copy-LF prediction

**Files:**
- Create: `mffp_autoresearch/round1/eval/panel_data.py`
- Test: `mffp_autoresearch/round1/eval/tests/test_panel_data.py`

**Interfaces:**
- Consumes: `mf_field/factory_mffp/data_adapters/loaders.py::load_mf_dataset(dataset_dir, split)` (read-only import; returns `fids, hf_fid, lf_fids, cond_by_fid, field_by_fid, grid_shape_by_fid, …`, fields flat `(N, n_cells)`).
- Produces (consumed by Tasks 4, 14):
  - `load_split(dataset_name: str, split: str) -> dict` — resolves `data_root/<name>` from project.yaml, wraps `load_mf_dataset`.
  - `copylf_prediction(data: dict) -> np.ndarray` — `(N_hf, n_cells_hf)`: the **highest LF fidelity** field, reshaped to its grid, bilinearly interpolated to the HF grid (`scipy.ndimage.zoom`, `order=1`), flattened. Raises `ValueError` if either grid shape is `None` (non-square layout) or if per-fid sample counts are misaligned (LF count < HF count).

- [ ] **Step 1: Write the failing tests** (synthetic + one real-data smoke)

```python
# mffp_autoresearch/round1/eval/tests/test_panel_data.py
import numpy as np, pytest, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from panel_data import copylf_prediction, load_split

def _fake(lf_grid, hf_grid, n=3):
    rng = np.random.default_rng(0)
    lf = rng.normal(size=(n, lf_grid[0] * lf_grid[1]))
    hf = rng.normal(size=(n, hf_grid[0] * hf_grid[1]))
    return {"fids": [1, 2], "hf_fid": 2, "lf_fids": [1],
            "field_by_fid": {1: lf, 2: hf},
            "grid_shape_by_fid": {1: lf_grid, 2: hf_grid}}

def test_copylf_shape_and_identity_when_grids_match():
    d = _fake((8, 8), (8, 8))
    np.testing.assert_allclose(copylf_prediction(d), d["field_by_fid"][1])

def test_copylf_upsamples_to_hf_grid():
    d = _fake((8, 8), (16, 16))
    assert copylf_prediction(d).shape == (3, 256)

def test_copylf_constant_field_is_exact_under_interpolation():
    d = _fake((8, 8), (16, 16))
    d["field_by_fid"][1][:] = 7.0
    np.testing.assert_allclose(copylf_prediction(d), 7.0)

def test_copylf_uses_highest_lf_fidelity():
    d = _fake((8, 8), (16, 16))
    d["fids"] = [1, 2, 3]; d["lf_fids"] = [1, 2]; d["hf_fid"] = 3
    d["field_by_fid"][3] = d["field_by_fid"].pop(2)
    d["grid_shape_by_fid"] = {1: (4, 4), 2: (8, 8), 3: (16, 16)}
    d["field_by_fid"][2] = np.full((3, 64), 5.0)
    d["field_by_fid"][1] = np.zeros((3, 16))
    np.testing.assert_allclose(copylf_prediction(d), 5.0)   # l2, not l1

def test_copylf_raises_on_missing_grid_or_misalignment():
    d = _fake((8, 8), (16, 16)); d["grid_shape_by_fid"][1] = None
    with pytest.raises(ValueError): copylf_prediction(d)
    d2 = _fake((8, 8), (16, 16)); d2["field_by_fid"][1] = d2["field_by_fid"][1][:2]
    with pytest.raises(ValueError): copylf_prediction(d2)

def test_real_dataset_loads_and_predicts():   # touches benchmark_42 via factory symlinks
    d = load_split("ext__helmholtz_2d", "test")
    pred = copylf_prediction(d)
    hf = d["field_by_fid"][d["hf_fid"]]
    assert pred.shape == hf.shape == (100, 9216)
```

- [ ] **Step 2: Run tests, verify they fail** (module missing).
- [ ] **Step 3: Implement** — repo root found via `git rev-parse --show-toplevel` (subprocess) or walking parents for `project.yaml`'s round dir; `sys.path` insert of `factory_root` for the `data_adapters` import; `copylf_prediction` takes the max of `lf_fids`, reshapes `(N, H, W)`, `scipy.ndimage.zoom` each sample by `(H_hf/H_lf, W_hf/W_lf)` with `order=1`, asserts output grid matches, flattens. Misalignment check: `lf.shape[0] >= hf.shape[0]`, then truncate to HF count (index-aligned per repo convention).
- [ ] **Step 4: Run tests, verify all pass** (real-data test included — run on a node with `/resnick` mounted, which is everywhere here).
- [ ] **Step 5: Commit** — `"round1 eval: panel data access + copy-LF predictor"`

---

### Task 4: Copy-LF baselines + G2 sanity gate

**Files:**
- Create: `mffp_autoresearch/round1/eval/make_copylf_baselines.py`
- Create (generated, committed): `mffp_autoresearch/round1/eval/copylf_baselines.json`

**Interfaces:**
- Consumes: Task 2 `nrmse`, Task 3 `load_split`/`copylf_prediction`.
- Produces: `copylf_baselines.json` — `{dataset: {"test_nrmse": float, "characterization_ref": float|null, "ratio_to_ref": float|null}}` for panel + guard datasets. Consumed by Task 5's scorer (hard requirement: scoring a dataset absent from this file raises).

- [ ] **Step 1: Write the script.** For each dataset in `panel + guard_set`: load test split, `nrmse(copylf_prediction(d), hf)`; join against `mf_field/akash/results/dataset_characterization.csv` column `lf_hf_rel_resid` (key: `dataset` for core, `{collection}__{dataset}` otherwise); write JSON sorted by name. Print a table.
- [ ] **Step 2: Run it** — `python make_copylf_baselines.py` (venv). **G2 gate:** for every dataset, `0.25 < ratio_to_ref < 4` OR a written note in the JSON explaining the divergence (the characterization may use train split / different interpolation — investigate before accepting; guard `sharp__sod_1d` is 1-D-in-2-D-layout: verify grid handling rather than special-casing silently). `ifc_poisson`'s ref is 80.3 (LF scale mismatch) — expect a large test_nrmse too; if instead it's ~O(1), investigate the scalers dir before proceeding.
- [ ] **Step 3: Commit JSON + script** — `"round1 eval: copy-LF baselines (G2)"`

---

### Task 5: `eval/score_panel.py` — contract runner with caching + seam assertions

**Files:**
- Create: `mffp_autoresearch/round1/eval/score_panel.py`
- Test: `mffp_autoresearch/round1/eval/tests/test_score_panel.py`
- Test fixture: `mffp_autoresearch/round1/eval/tests/fake_family/{manifest.json,smoke_eval.py}`

**Interfaces:**
- Consumes: family contract CLI; Tasks 2–4 modules; card `recipe` dicts.
- Produces (consumed by builder/analyzer agents and Tasks 13–15):
  - CLI: `python score_panel.py --family_dir <path> --datasets <csv|panel|guard> --epochs <n> --seed <n> [--out <json>] [--env KEY=VAL ...] [--no_cache]`
  - Python: `score_family(family_dir, datasets, epochs, seed, env=None, use_cache=True) -> dict` returning `{"family", "nrmse_def_hash", "code_hash", "per_dataset": {ds: {"nRMSE", "skill", "cached"}}, "panel_geomean_skill"}`.
  - Cache key: sha256 over (family dir `*.py` sources ∪ `mf_field/factory_mffp/models/_common/*.py` ∪ `round1/eval/{nrmse,panel_data,score_panel}.py` ∪ sorted env knobs) + `(dataset, epochs, seed)`. Cache at `eval/cache/<key>.json`.
  - Seam assertions (each raises `ScoreContractError` with a specific message): family results JSON missing `splits.test.nRMSE`; reported `dataset` ≠ requested; non-finite nRMSE; dataset absent from `copylf_baselines.json`; `nrmse_def_hash` mismatch when comparing two result files.
- Child env: sets `PYTHONHASHSEED=<seed>`, `CUBLAS_WORKSPACE_CONFIG=:4096:8`, plus caller `--env` knobs; records all of it in the output JSON (the card `recipe` mirror).

- [ ] **Step 1: Write the fake family fixture** — a `smoke_eval.py` that parses the six contract args and writes `{"model": "fake_family", "dataset": <name>, "splits": {"test": {"nRMSE": 0.5}}}`; env knob `FAKE_NRMSE` overrides the value (for cache-key testing); `FAKE_BREAK=missing_key|wrong_dataset|nan` produces each contract violation.
- [ ] **Step 2: Write the failing tests** — happy path (score = 0.5/copylf, geomean over 2 datasets); cache hit on second call (`cached: true`) and miss after touching a fixture `.py` or changing `--env FAKE_NRMSE`; each `FAKE_BREAK` mode raises `ScoreContractError`; unknown dataset raises. Use a tmp cache dir via env `ROUND1_EVAL_CACHE`.
- [ ] **Step 3: Run tests → fail. Implement. Run tests → pass.** Implementation: `subprocess.run([venv_python, smoke_eval, ...], env=child_env, timeout=...)`; per-dataset out JSON under `eval/results/<family>/<dataset>_e<epochs>_s<seed>.json`.
- [ ] **Step 4: Commit** — `"round1 eval: score_panel runner with caching + seam assertions"`

---

### Task 6: `program.md`

**Files:**
- Create: `mffp_autoresearch/round1/program.md`
- Reference (port from, read-only): `/resnick/groups/Hippo/ezeng/playground_test/autoresearch_round5b/program.md`

**Interfaces:**
- Produces: the section numbers every agent prompt cites — keep round5b's numbering: §1 Goal, §2 Score system, §3 (reserved/short), §4 Structure, §5 Fair-comparison immutables, §6 Subagent roster, §7 (short), §8 Prerequisites & gates, §9 Training/eval commands, §10 Termination, §11 Logistics pointers, §12 Per-stream conventions, §13 Project overview.

- [ ] **Step 1: Port the domain-neutral sections** (§1, §4, §6, §8, §10, §11) from round5b's program.md, substituting round1 names/paths. §1 = spec §1 verbatim (goal + two success criteria). §4 = 5 streams, serial batches, 1 card/batch, 1+2 seeds {0,1,2}, cratered rule (crash, skill > 1.5× stream anchor's, or falsification already decisive), diagnostic cards (single run, no seeds 2–3).
- [ ] **Step 2: Write the domain sections fresh from the spec:**
  - §2 Score: the nRMSE definition (formula, file path `round1/eval/nrmse.py`), copy-LF skill, panel geomean, bootstrap CI convention, panel + guard tables with the anchor numbers from spec §3.2/§3.3.
  - §5 Immutables: the 8 items of spec §9 verbatim, plus the pre-falsified-lever list (WNO backbone swap, LF low-mode freeze, diffusion prior for point accuracy) as "do not re-propose as-is".
  - §9 Commands: exact `score_panel.py` invocations per tier; sbatch template path; venv activation; checkpoint-resume requirement (`<ckpt_dir>/last.pt`, preemptable partition).
  - §12 Per-stream conventions: one subsection per stream from spec §6's table — anchor definition, falsification-threshold convention (must exceed the batch-0 noise floor for its dataset, from `state/noise_floor.json`), seed direction, and the §3.4 facts relevant to that stream (quantified headroom + pre-falsified levers).
  - §13 Project overview: 1 page — what MFFP is, the two data layouts, the model zoo landscape (FNO-transfer top, 45 families), the mentor-owned guarded surfaces, and the convnext≠CNN-FNO correction.
- [ ] **Step 3: Cross-check** — every §-reference used by the round5b subagent prompts (§1, §2, §4, §5, §6, §9, §12, §13) resolves to real content. Grep the round5b prompts for `§` to build the checklist.
- [ ] **Step 4: Commit** — `"round1: program.md"`

---

### Task 7: `_shared/` partials + card schema

**Files:**
- Create: `mffp_autoresearch/round1/subagents/_shared/{universal_context.md,decision_discipline.md,card_update.md,handoff_convention.md,pre_return_checklist.md,return_format.md,env_activation.md}`
- Create: `mffp_autoresearch/round1/experiment_cards/SCHEMA.md`
- Reference: `/resnick/groups/Hippo/ezeng/playground_test/autoresearch_round5b/subagents/_shared/` and `~/.claude/agents/_shared/`

**Interfaces:**
- Produces: the shared-partial names each agent prompt references; the card JSON field list all agents obey.

- [ ] **Step 1: Port the partials.** Transformations: `universal_context.md` preamble points at `mffp_autoresearch/round1/project.yaml` (keep the `git rev-parse` + python-yaml absolutify pattern, exporting the `paths:`/`caps:`/`seed_protocol:` keys of Task 1); `env_activation.md` becomes venv activation + `CUBLAS_WORKSPACE_CONFIG` + "no JAX flags — this is a torch project"; the rest are domain-neutral (copy, fix paths only). `decision_discipline.md` (round5b's no-oracle judgment guide) copies with §-references intact.
- [ ] **Step 2: Write `SCHEMA.md`** — the round-5 card fields (spec §4 list: id/stream/batch/category/created_utc/worktree_path/source_iteration/reopened_from; locked parts `1_id_category, 2_motivation, 3_description, 4_expected_result, expected_falsification, anchor_reference`; result parts `5_actual_result, 6_analysis, 7_gap_and_future`; mechanics `status, job_ids[], logs{}, scripts_path{}, output_paths{}, build_commit, build_notes[], review_notes[], debug_notes[]`) **plus the three round-1 additions**: `card_type: model|diagnostic`, `prior_art: {verdict: novel|preempted-pivoted|preempted, citations: [...]}` (locked), `recipe: {family_dir, base_family, dataset(s), epochs, seeds, env: {...}}` (locked; builder HARD-STOPs with `BLOCKED: recipe-missing` if absent/empty).
- [ ] **Step 3: Commit** — `"round1: shared partials + card schema"`

---

### Task 8: Planning agents — websearcher (+ prior-art gate) and brainstormer

**Files:**
- Create: `mffp_autoresearch/round1/subagents/websearcher.md`, `mffp_autoresearch/round1/subagents/brainstormer.md`
- Reference: round5b versions + `~/.claude/agents/{websearcher,brainstormer}.md`

- [ ] **Step 1: Port `websearcher.md`.** Keep: ≤5 iterations, per-iteration files, report format, stop-decision discipline. Replace the per-stream search-topic table with the 5 MFFP streams (from program.md §12). **Add the prior-art gate as the mandatory final iteration:** given the brainstormer-bound candidate directions, produce a `## Prior-art verdict` section — for each direction: `novel | preempted (cite) | preempted-but-MF-composition-open (cite)`, citations only from sources actually fetched this loop (no model recall; every citation must have an iteration file recording the fetch). Failure to include the section is a checklist failure.
- [ ] **Step 2: Port `brainstormer.md`.** Keep the whole round5b structure (context packing → design → immutables self-check → report; recipe HARD-STOP; reopen candidates). Transformations: §12 conventions references stay; the immutables block becomes the 8 MFFP immutables from program.md §5 (self-check requires positive evidence per item, same as round5b); design directives table = the 5 streams; **add**: (a) the proposal must quote the websearcher's prior-art verdict — designing a `preempted` mechanism without an MF-composition pivot is a self-check failure; (b) a `diagnostic` proposal is legal (category `diagnostic`, no training, single run, falsification clause about the measurement); s2 batch 1 is pre-directed to the fusion-destruction diagnostic (spec §6); (c) every proposal includes the structured `recipe` block for its card.
- [ ] **Step 3: Commit** — `"round1: planning agents (websearcher w/ prior-art gate, brainstormer)"`

---

### Task 9: Mechanical agents — starter, builder, code-reviewer, debugger

**Files:**
- Create: `mffp_autoresearch/round1/subagents/{experiment-starter,experiment-builder,code-reviewer,experiment-debugger}.md`
- Reference: round5b versions + `~/.claude/agents/` copies

- [ ] **Step 1: Port `experiment-starter.md`.** Verbatim-transcriber role unchanged. Worktree: branch `round1/exp-{stream}-B{N}` from substrate branch `round1-substrate` (Task 11) at `mffp_autoresearch/round1/worktrees/{stream}/B{N}/`. Card per Task 7 SCHEMA including `card_type`, `prior_art`, `recipe` transcribed from the brainstormer report (TBD-marking rule kept; missing `recipe` in the report → card written, status `blocked`, `BLOCKED: recipe-missing`).
- [ ] **Step 2: Port `experiment-builder.md`.** Transformations: model code lives in the worktree as a contract-compliant family dir `models_r1/<family>/` (manifest.json + smoke_eval.py + INSPIRATION.md with bibtex; checkpoint-resume from `<ckpt_dir>/last.pt` mandatory); SLURM scripts per Task 11 templates (`01_train_eval.sh SEED`, `submit.sh` seed 0, `submit_seeds_2_3.sh`) — for MFFP, train+eval is ONE `score_panel.py` (or direct `smoke_eval.py`) invocation per (dataset, seed), so the R5 train→eval `afterok` chain collapses to one job per dataset×seed with an `sbatch` array; smoke test = contract tier (2 epochs, 1 panel dataset) run in-session before returning; one atomic commit to the experiment branch. Diagnostic cards: build the measurement script instead, same review path, output to `outputs_root`.
- [ ] **Step 3: Port `code-reviewer.md`.** PASS/SUGGEST/FAIL unchanged (3-FAIL cap). Review checklist swaps the quadruped envelope for MFFP: the 8 §5 immutables, recipe present & matched against the diff, contract CLI compliance, checkpoint-resume implemented, prior-art verdict quoted, no writes outside worktree + `outputs_root`, sbatch sanity (partition/gres/time from Task 11 rules).
- [ ] **Step 4: Port `experiment-debugger.md`.** ALGO/INFRA classification, 5-ALGO cap, numbered immutable handoffs, minimal-fix discipline — all unchanged; queue commands (`squeue/sacct`) and log locations updated to round1 paths; the R5 "retry rule discourages skipping" language kept.
- [ ] **Step 5: Commit** — `"round1: mechanical agents"`

---

### Task 10: Analysis agents + maintainer + advisor-consult

**Files:**
- Create: `mffp_autoresearch/round1/subagents/{experiment-initial-analyzer,experiment-mechanism-analyzer,maintainer,advisor-consult}.md`
- Reference: round5b versions

- [ ] **Step 1: Port `experiment-initial-analyzer.md`.** Part-5 writer: parses `score_panel` result JSONs (never recomputes metrics), records per-dataset nRMSE + skill + panel geomean, seed-0 verdict vs cratered rule, then 3-seed mean ± CI on the second invocation; writes/updates `state/anchors/{stream}.json` when the stream's anchor changes; guard-set check for panel-win claims (>2× guard regression → flag in part 5). Diagnostic cards: part 5 = the measurement's findings vs its falsification clause.
- [ ] **Step 2: Port `experiment-mechanism-analyzer.md`.** 3 turns + register, tool promotion into `round1/tools/` with `tools/index.md` registry, prefer-existing-tool rule — structure unchanged; the probe menu swaps to MFFP: per-band spectral error vs copy-LF, error maps vs interface distance, residual histograms, per-dataset skill breakdown, weight/feature probes.
- [ ] **Step 3: Port `maintainer.md`.** Read-only card walk + `squeue/sacct` + `index.md` dashboard + `state/maintainer_report.md` deltas + timing ledger + transcript archiving + abandonment detection; single in-flight rule (R5 live-log lesson); paths to round1.
- [ ] **Step 4: Write `advisor-consult.md`** — the ad-hoc no-oracle variant: reads project.yaml + program.md, gives a task-grounded opinion per `decision_discipline.md` (this mirrors the agent already in the session roster).
- [ ] **Step 5: Commit** — `"round1: analysis agents + maintainer"`

---

### Task 11: SLURM logistics + substrate branch + outputs

**Files:**
- Create: `mffp_autoresearch/round1/resource/logistics/{slurm_rules.md,example_scripts/01_train_eval.sh,example_scripts/submit.sh,example_scripts/submit_seeds_2_3.sh}`
- Create: branch `round1-substrate`; dir `mffp_autoresearch_outputs/round1/`

- [ ] **Step 1: Write `example_scripts/01_train_eval.sh`** — takes `SEED DATASET EPOCHS FAMILY_DIR OUT_DIR`; activates venv; runs `python <round>/eval/score_panel.py --family_dir "$FAMILY_DIR" --datasets "$DATASET" --epochs "$EPOCHS" --seed "$SEED" --out "$OUT_DIR/result_${DATASET}_s${SEED}.json"`; sbatch header `--partition=gpu --gres=gpu:p100:1 --time=<from timing ledger, default 04:00:00> --signal=B:USR1@120` (preemption-aware; families resume from `last.pt`). `submit.sh` = seed-0 array over card datasets; `submit_seeds_2_3.sh` = seeds 1,2.
- [ ] **Step 2: Write `slurm_rules.md`** — Caltech port of R5's: typed gres mandatory; `--time` from `state/timing_ledger.json` (default 4 h until measured); job names `r1-{stream}-B{N}-s{seed}`; logs to `outputs_root/{stream}/B{N}/slurm/`; the orchestrator submits, never the builder.
- [ ] **Step 3: Create the substrate branch** — `git branch round1-substrate HEAD` (full tree is fine — repo is code-only, data is git-ignored; record in ADR 0001 that round1 worktrees fork from it and experiment branches are `round1/exp-*`). Create `mffp_autoresearch_outputs/round1/` and verify it's git-ignored (`git check-ignore`).
- [ ] **Step 4: Commit** — `"round1: SLURM logistics + substrate branch"`

---

### Task 12: `HOW_TO_LAUNCH.md` + agent install script

**Files:**
- Create: `mffp_autoresearch/round1/HOW_TO_LAUNCH.md`
- Create: `mffp_autoresearch/round1/install_agents.sh`

- [ ] **Step 1: Write `install_agents.sh`** — backs up `~/.claude/agents/` to `~/.claude/agents.quadruped-round5.bak/` (once, if not present), then copies `round1/subagents/*.md` → `~/.claude/agents/` and `_shared/` → `~/.claude/agents/_shared/`. Idempotent; prints a diff summary.
- [ ] **Step 2: Write `HOW_TO_LAUNCH.md`** (adapted from `round5_preparation/HOW_TO_LAUNCH.md`): prerequisites table G1–G4 with the verification command for each; install step; the kickoff prompt verbatim (role assignment + "read program.md §6/§4/§8, confirm gates green, start all 5 streams at batch 1 — batch 0 is the noise-floor certification, already run"); the two crons (10-min orchestrator pulse: "for each stream, where are you in the flow?"; 20-min maintainer dispatch) with the note that crons pulse, they don't drive logic; dispatch pattern (`bypassPermissions` for python-running agents, `description="{stream}-B{N}"` as archive key); recovery procedure (state re-read from `state/`).
- [ ] **Step 3: Commit** — `"round1: launch runbook + agent installer"`

---

### Task 13: Gate G1 — eval-layer smoke on a real family

**Files:**
- Create: `mffp_autoresearch/round1/state/gates.md` (gate ledger; appended by Tasks 13–15)

- [ ] **Step 1: Contract-tier run, real family, 2 panel datasets** (login-node or `srun` if GPU needed):

```bash
source .venv/bin/activate
python mffp_autoresearch/round1/eval/score_panel.py \
  --family_dir mf_field/factory_mffp/models/mf_fno_transfer_film \
  --datasets ext__helmholtz_2d,ifc_poisson --epochs 2 --seed 0 \
  --out mffp_autoresearch/round1/eval/results/g1_contract.json
```

Expected: exits 0; JSON has both datasets with finite nRMSE and skill; second invocation reports `cached: true` for both.

- [ ] **Step 2: Assertion drill** — run the same command against the Task 5 fake family with `FAKE_BREAK=wrong_dataset` and confirm the specific `ScoreContractError` fires (screenshot of stderr into `state/gates.md`). If any drill assertion does NOT fire, the gate fails — fix before proceeding.
- [ ] **Step 3: Record G1 PASS in `state/gates.md`** with command lines + result paths. Commit.

---

### Task 14: Gate G3 — batch 0: anchor certification + noise floor

**Files:**
- Create: `mffp_autoresearch/round1/eval/run_batch0.sbatch` (array job)
- Create (generated, committed): `mffp_autoresearch/round1/state/{noise_floor.json,anchors/*.json}`

**Interfaces:**
- Produces: `state/noise_floor.json` — `{dataset: {family, per_seed_nrmse: [s0,s1,s2], spread: max-min, skill_mean}}`; `state/anchors/{stream}.json` — `{stream, anchor_type, dataset(s), value (skill), source: "batch0", certified_utc, provisional: false}`.

- [ ] **Step 1: Write `run_batch0.sbatch`** — array over (family × panel-dataset × seed) at smoke tier (200 epochs): families `mf_fno_transfer_film` (champion) + `mf_fno_pinn_transfer` (ifc_poisson best in factory zoo); 2 × 6 × 3 = 36 tasks, each one `score_panel.py --datasets <ds> --epochs 200 --seed <s>`. `--time` 6:00:00 first pass.
- [ ] **Step 2: Submit, monitor to completion** (debugger discipline applies manually here; record failures + fixes in `state/gates.md`).
- [ ] **Step 3: Aggregate** — small script inline or in `eval/` (committed): read the 36 result JSONs, write `noise_floor.json` (per dataset: best family's per-seed values + spread) and the 5 anchor files per program.md §12 (s1: best skill on `ifc_poisson`; s2: 1.0 = copy-LF; s3/s4: champion's panel geomean; s5: champion's panel geomean). **G3 pass condition:** per-dataset seed spread < half of the smallest effect any stream's falsification convention will claim (sanity: spread/mean < 10%); if a dataset's spread is larger, its noise floor value becomes the minimum claimable effect and program.md §12 is updated (allowed pre-launch — the spec freeze starts at launch).
- [ ] **Step 4: Record G3 in `state/gates.md`; commit JSONs.**

---

### Task 15: Gate G4 — hand-driven dry-run card end-to-end

- [ ] **Step 1: Drive one cheap real card by hand through every stage** — stream `s5_tuning`, batch 1, a genuinely useful first experiment: `modes_cap` 12→32 on `mf_fno_transfer_film` (candidate M1, `MODELS_TO_TRY.md`), smoke tier, panel. Invoke the actual agents one at a time via the Agent tool (websearcher → brainstormer → starter → builder → code-reviewer), then submit seed 0 via `submit.sh`, then initial-analyzer; seeds 1–2 only if not cratered; then mechanism-analyzer turns. This validates: agent defs load post-install, card writes obey the schema, worktree/branch conventions, SLURM scripts, result parsing, anchors.
- [ ] **Step 2: Fix everything that breaks** (expect prompt-path bugs); each fix is a commit to `round1/subagents/` or `eval/`. Re-run the broken stage only.
- [ ] **Step 3: Record G4 PASS + the full card id (`s5_tuning-B1`) in `state/gates.md`; commit.** Note: G4's card is a real card — it counts as `s5_tuning` batch 1, not a throwaway.

---

### Task 16: Launch

- [ ] **Step 1: Install agents** — `bash mffp_autoresearch/round1/install_agents.sh` (after G4 they're already installed; re-run to confirm idempotency).
- [ ] **Step 2: Verify gate ledger** — all of G1–G4 PASS in `state/gates.md`.
- [ ] **Step 3: Start the crons** per `HOW_TO_LAUNCH.md`: orchestrator pulse (10 min), maintainer (20 min). Record cron ids in `state/orchestrator_flow.md`.
- [ ] **Step 4: Begin orchestration in this session** — assume the orchestrator role per the kickoff prompt: start `s1_poisson`, `s2_beyond_copy`, `s3_testtime`, `s4_hybrid_routing` at batch 1 (websearcher first, background, parallel), continue `s5_tuning` at batch 2. Maintain `state/{stream}/current_*` and `state/orchestrator_flow.md` from the first dispatch.
- [ ] **Step 5: Commit any remaining round1 files; push the branch** (existing remote `origin/mffp-trunk-eloise`).

---

## Self-Review

**Spec coverage:** §1–§2 → Tasks 2, 6; §3 panel/guard → Tasks 1, 4; §3.4 facts → Task 6 (§12/§13); §4 scaffold → Tasks 1, 6–12; §5 improvements: prior-art gate → Task 8, diagnostic slots → Tasks 7–10, seam assertions → Tasks 5, 7 (recipe hard-stop), noise floor → Task 14; §6 streams → Tasks 1, 6, 8; §7 eval layer → Tasks 2–5; §8 protocol → Tasks 6, 10; §9 immutables → global constraints + Task 6 §5; §10 gates → Tasks 13–15; §11 out-of-scope respected (no oracle task, no factory edits); §12 risks → Tasks 4 (ifc_poisson baseline oddity), 14 (noise floor). No gaps found.

**Placeholder scan:** prose-porting tasks (6–12) specify source file + exact transformation list rather than embedding round5b's full text — deliberate (the source files are on disk and versioned); every code task has real code or exact commands. No TBDs.

**Type consistency:** `nrmse/skill/panel_geomean/bootstrap_ci/NRMSE_DEF_HASH` (Task 2) match usage in Tasks 4, 5, 14; `load_split/copylf_prediction` (Task 3) match Task 4; `score_family`/CLI flags (Task 5) match Tasks 13–15; card fields (Task 7) match Tasks 8–10, 15.
