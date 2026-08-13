# benchmark_30 campaign — implementation plan

Status: DRAFT for Codex convergence (stage 5 of codex-converge).
Spec: `docs/spec.md` (converging; round-1 findings folded at `04debf8`).
Base: `BASE=83a547e`; worktree `mffp_autoresearch/benchmark30/worktree`, branch `bench30-campaign`.
All new code under `mffp_autoresearch/benchmark30/`; nothing outside it is modified except nothing — zero files outside the campaign dir change (spec §3).

Execution discipline (NON-NORMATIVE process, from the governing codex-converge/superpowers workflow, not derived from the spec): each task is one atomic commit; tests are written first where a behavior is being created (TDD red→green, red-phase transcripts recorded in `tests/RED_TRANSCRIPTS.md`); the venv is `mf_field_eloise_data/SURF_2026-main/.venv` (numpy/scipy present) unless a task says otherwise.
Every task lists its spec traceability line; process lines like this one are exempt from traceability.

## Phase A — build (tasks A1–A10)

### A1. Campaign config + skeleton

Create `mffp_autoresearch/benchmark30/{config.yaml,staging/,eval/,family/,slurm/,aggregate/,tests/,state/,docs/adr/}`.
`config.yaml`: the 30 dataset IDs (grouped, with per-dataset `dataset_dir` — era5 → `era5/era5_train_test`), seeds `[0,1,2]`, epochs `{smoke: 2, full: 200}`, families `{r3s2_route_b30: family/r3s2_route_b30, mf_fno_transfer_film: <factory models path>}`, output root `mffp_autoresearch_outputs/benchmark30`, SLURM knobs (partition gpu, gres `gpu:nvidia_h200:1`, mail ezeng@caltech.edu END,FAIL), retry cap 3, and `recipe_env`: the certified B2 env block copied VERBATIM from `round3/experiment_cards/r3s2_field_reach/batch_2/B2.json` (spec D5).
Necessity note (spec §4): round-2 `project.yaml` is frozen round state scoped to its own panel and cannot carry per-dataset `dataset_dir`, campaign roots, or the B2 recipe block — hence a campaign-local config consumed by the vendored scorer's seam (c); no existing config could be reused without editing round state.
Test (first): `tests/test_config.py` — config parses; exactly 30 unique dataset IDs; every `dataset_dir` exists on disk; seeds/epochs match spec D6/D7; `recipe_env` is byte-equal to the B2 card's env block (read from the card file, not restated), including the exact historical `R3S2_TARGET_SCALER_PREFLIGHT` string.
Traceability: spec §6, D6, D7, D10.
Commit: `bench30: A1 campaign config + tree skeleton`.

### A2. Staging manifest builder (G0)

`staging/manifest.py`: for each dataset, sha256 every data file under its `dataset_dir` (sorted walk), record `{dataset, dataset_dir, files: {relpath: sha256}, content_hash (sha256 of sorted file hashes), grid_shape, layout (npz_l|ifc_raw), n_levels, corrected_vs_hf: {status, adr}}`; writes `state/staging_manifest.json` as a PROVISIONAL source lock (`manifest_hash: null`, `sealed: false`).
The final identity is sealed in A6 per the exact D12 formula: `manifest_hash = sha256(registry_revision + sorted per-dataset SOURCE content hashes + sorted per-dataset STRIPPED-VIEW content hashes)` — the hash cannot exist before the stripped views do.
The two known deviations (`sharp__allen_cahn_2d` test, `sharp__phase_field_crystal_2d`) are marked `corrected_local_newer_than_hf` with their ADR ids; all others `identical_to_hf_benchmark30`.
Test (first): fixture mini-dataset in `tests/fixtures/` (tiny npz, FIXTURE-marked) — deterministic hash, deviation marking, provisional manifest carries `sealed: false` and no `manifest_hash`.
Traceability: spec D1, D12, G0.
Commit: `bench30: A2 staging manifest builder (G0)`.

### A3. Vendored scorer (eval/) + seam manifest + byte-identity guard

Copy `round2/eval/score_panel.py` + `round2/eval/panel_data.py` (at BASE) into `benchmark30/eval/`.
Apply EXACTLY the seams of spec D3: (a) baseline path → `benchmark30/state/copylf_baselines.json`; (b) config/data-root resolution → `benchmark30/config.yaml` incl. per-dataset `dataset_dir` and campaign `stripped_data_root`; (c) registry appends land in A5, not here.
`eval/SEAM_MANIFEST.md` lists each changed hunk with before/after.
Test (first): `tests/test_vendor_integrity.py` — diff each vendored file against `git show 83a547e:mffp_autoresearch/round2/eval/<file>`; assert changed lines ⊆ the seam manifest's declared hunks; assert `_extract_test_metric`, nRMSE/skill computation, cache logic, and stripped-view assertions are byte-identical (function-level source compare via ast/inspect).
Traceability: spec D3.
Commit: `bench30: A3 vendored scorer + seam manifest + integrity guard`.

### A4. Vendored family (family/r3s2_route_b30) + byte-identity guard

Copy the family dir from the B2 worktree at `e606a4f` (`git -C <B2> show e606a4f` file-by-file, not the working tree — review-the-commit-that-is-checked-out).
Record `state/family_byte_identity.json`: per-file sha256 at `e606a4f` and in the vendored copy; the ONLY permitted future delta is the `upsample.py` registry append (A5).
Test (first): `tests/test_family_integrity.py` — every file except `upsample.py` byte-identical to `e606a4f`; `upsample.py` differs ONLY inside the three set literals (ast compare: same module minus the set elements).
Traceability: spec D2.
Commit: `bench30: A4 vendored certified family + byte-identity guard`.

### A5. Convention ADR + registry appends + synthetic upsample checks (G2)

Author `docs/adr/0001-benchmark30-convention-registry.md` from the evidence draft (research agent output): 17 2-D classifications with rationale + 3 `1d_path` records + era5.
Append the new names to the three sets in BOTH `eval/panel_data.py` (vendored) and `family/r3s2_route_b30/upsample.py`.
Tests (first): `tests/test_registry.py` — (i) coverage: every 2-D campaign dataset resolves, unknown name still raises; (ii) every NEWLY classified benchmark_30 ID receives the same convention in both vendored copies, with the pre-existing entries (including the intentional pfc divergence, ADR r3-0005) exempted exactly as recorded in the seam manifest — whole-registry equality is deliberately NOT asserted (spec D4); (iii) synthetic checks per convention: periodic_node exactness at shared nodes on nested grids, dirichlet interior-node endpoint mapping, cell-centre alignment for legacy_cell — on synthetic fields, never real test data.
Traceability: spec D4, G2.
Commit: `bench30: A5 convention ADR + registry extension + synthetic checks`.

### A6. Stripped views + LF-free audit (G1)

`staging/preflight.py`: imports `_mirror`/`_verify` from `round2/eval/make_stripped_view.py` (import-only reuse, no edits), builds `stripped_data/` under the campaign output root for all 30, then audits: every test view physically LF-free, loads via `data_adapters.load_mf_dataset`, grid/layout/condition-vector fields present, LF rung present in TRAIN (r3s2 requires a non-empty train LF ladder).
After the audit passes, A6 SEALS the manifest: recomputes the D12 `manifest_hash` over source + stripped-view content hashes + registry revision, sets `sealed: true`, and rewrites `state/staging_manifest.json`; every downstream consumer (A8 rev-roots, A9 validator) refuses an unsealed manifest.
Test (first): fixture dataset → stripped view produced, LF arrays absent, audit catches a deliberately-planted LF leak; sealing test proves BOTH a source-byte change AND a stripped-view-byte change alter `manifest_hash`, and unsealed manifests are refused downstream.
Traceability: spec D3, D6-G1, D12, §6.
Commit: `bench30: A6 stripped views + LF-free audit (G1)`.

### A7. Campaign copy-LF baselines (G2)

`eval/make_copylf_baselines_b30.py`: computes the copy-LF reference per dataset with the VENDORED construction (self-consistent `COPYLF_DEF_HASH`), writes `state/copylf_baselines.json` (committed).
Test (first): on the fixture dataset the copy-LF nRMSE matches a hand-computed value; on a certified-panel dataset (e.g. ifc_heat) the baseline value matches the round-2 committed `copylf_baselines.json` entry (proves construction equivalence end-to-end).
Traceability: spec D3, G2.
Commit: `bench30: A7 campaign copy-LF baselines`.

### A8. SLURM launchers (G3–G5)

`slurm/run_matrix.sbatch` (template) + `slurm/launch.py`: one job per {family, seed, tier} iterating the dataset list sequentially via the vendored `score_panel.py` CLI with `ROUND2_EVAL_RESULTS/CACHE` → `rev-<manifest_hash8>/…` and per-dataset `ckpt_dir` under the same rev root; `--mail-user=ezeng@caltech.edu --mail-type=END,FAIL`; time 8:00:00 full / 1:00:00 smoke; logs immutable per attempt under the D12 revision root (`mffp_autoresearch_outputs/benchmark30/rev-<manifest_hash8>/logs/<jobname>_<jobid>.{out,err}`); the dry-run test asserts that complete path.
`launch.py` enforces an explicit gate→tier matrix on `state/gates.json`: submitting the SMOKE tier requires G0+G1+G2 passed; FULL seed 0 requires G3 recorded (smoke matrix complete, every cell PASS or ledgered); FULL seeds 1–2 require G4 recorded (seed-0 jobs COMPLETED per sacct + results validated by the A9 validator — completion, never metric quality).
Phase B steps write the corresponding immutable gate entries (`{gate, utc, evidence_hash}`) into `state/gates.json` as they validate.
Test (first): launcher dry-run mode renders sbatch scripts; assert exact mail/partition/gres lines, rev-scoped paths; assert each tier's refusal for every insufficient gate combination in the matrix.
Traceability: spec D6, D10, D12.
Commit: `bench30: A8 SLURM launchers with gate enforcement`.

### A9. Aggregator + validator + leaderboard

`aggregate/collect.py`: walks `rev-<hash8>/results/`, validates each result (family, dataset, seed, epochs, `copylf_def_hash` = vendored hash, manifest re-hash per D12 over source AND stripped bytes), assembles `leaderboard.json`: per-dataset per-seed rel-L2, 3-seed mean/min/max, film-relative skill on the common set, geomeans per group and overall, coverage + exclusion ledger, wall-clock/memory table.
Headline aggregation order is EXACTLY spec D9: for each seed s, compute the panel geomean of per-dataset skill over the common eligible set using seed-s numbers; the headline = mean over the three seed-level geomeans, interval = [min, max] of them, labeled a seed+run interval; the aggregator also reports ONLY arm `A1_stack_ic_reg` for r3s2 (the 7-arm sidecar data is carried as diagnostics, never selected over).
`aggregate/report.py`: renders `docs/report.md` tables from `leaderboard.json` only (no hand numbers).
Tests (first): FIXTURE result JSONs → known aggregate numbers, including a deliberately NON-SYMMETRIC fixture where "per-seed panel geomean then mean/min/max" differs numerically from "ratio of seed-averaged means then one geomean" and the test pins the former; validator rejects a wrong manifest hash; geomean excludes datasets missing either family; a fixture with a non-A1 best arm proves the report still quotes A1; ledger classes render.
Traceability: spec D8, D9, D12.
Commit: `bench30: A9 aggregator + validator + report generator`.

### A10. Preflight gate runner + G0–G2 execution

Wire A2/A6/A7 + tests into `staging/run_gates.py` writing `state/gates.json` (G0, G1, G2 entries with timestamps + artifact hashes).
Necessity note (spec §4): the round-3 gate machinery is the orchestrator/card pipeline (state/gates.md + card status driven by the autoresearch agents) — round-scoped state this campaign must not write to, and its gates encode a different protocol (card stages, not G0–G5); hence a minimal campaign-local gate file consumed by `launch.py`, not a parallel orchestrator.
Run it for real on the cluster login node (CPU-only work); commit the state files (manifest, baselines, gates).
Traceability: spec D6.
Commit: `bench30: A10 gates G0-G2 executed + state committed`.

## Phase B — execution (task #5 in the session task list; not code tasks)

1. G3: submit smoke pair (2 epochs, seed 0, both families, all 30); triage every cell PASS/ledger; commit `state/exclusion_ledger.json` (era5×r3s2 expected: WORK_CAP raise).
2. G4: submit full seed 0 (2 jobs); validate completion; no metric-based selection.
3. G5: submit seeds 1–2 (4 jobs).
4. Aggregate (A9), write report, run the Codex↔Claude fact-check loop on it, then deliver D-summary with the D13 payload: leaderboard headline + per-group results, coverage/exclusion ledger, AND the provenance finding (benchmark_30 = sha-identical subset of the corrected release; nicksung repo unfrozen 2026-08-12; the two locally-regenerated datasets are now stale in benchmark_30 too — input to her pending coherent-HF-hub-revision decision).
   Notification triggers (D13): the consolidated summary at the end; immediately on a stop-the-line event or a decision outside the approved envelope; nothing else mid-campaign.

## Who implements (NON-NORMATIVE process — author/reviewer routing per the codex-converge workflow, not a spec decision)

- Codex `--write` candidates (mechanical, well-specified): A3 file copy + seam application, A4 file copy + hash manifest, A8 sbatch template rendering.
  Routed per the round's shape at execute time; whoever writes a range does not review it.
- Claude: A1, A2, A5 (ADR judgment), A6, A7, A9, A10, and all execution-phase work.

## Risks / notes

- The synthetic upsample checks (A5) validate implementation semantics only; classification correctness rests on the ADR evidence — flagged for the plan-convergence round to scrutinize.
- `code_hash` covers the family dir + `models/_common` + the round eval layer; the vendored scorer's `code_hash` function must hash the VENDORED eval dir (seam c) so cache invalidation still works — covered by A3's integrity test scope.
- Film runs use the factory family path directly (not vendored) — it is already frozen upstream (`manifest.json` frozen flag) and D2 only freezes the r3s2 family; the staging manifest records the film family dir's content hash at launch for provenance.
- 6 full jobs × ≤8 h fits partition limits; smoke pair ~1 h.
