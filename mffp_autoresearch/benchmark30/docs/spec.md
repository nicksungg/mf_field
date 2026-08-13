# benchmark_30 campaign — specification

Status: DRAFT for Codex convergence (stage 3 of codex-converge).
Base for all reviews: `BASE=83a547e` (mffp-trunk-eloise), worktree `mffp_autoresearch/benchmark30/worktree`, branch `bench30-campaign`.
Author: Claude (Fable 5), 2026-08-12.
Operator request: "train our best model from round 3 on these 30 datasets \[HF nicksung/mf_field benchmark_30\]. then benchmark the model against film transfer fno baseline."

## 1. Goal

Train the round-3 certified best MFFP model and the FiLM-transfer-FNO baseline on all 30 datasets of the newly published `nicksung/mf_field` `benchmark_30`, 3 seeds x 200 epochs each, under the round-3 stripped-view evaluation protocol, and produce a comparative leaderboard report: per-dataset nRMSE for both families, film-relative skill, and panel geomean with a seed-aware interval.

Deliverables:

- `D-report`: `mffp_autoresearch/benchmark30/docs/report.md` — fact-check-converged benchmark report.
- `D-results`: per-run result JSONs + an aggregate `leaderboard.json` under `mffp_autoresearch_outputs/benchmark30/` (gitignored heavy artifacts; JSON summaries committed).
- `D-manifest`: dataset version/staging manifest (§5.1) committed to git.
- `D-adr`: one ADR extending the upsample-convention registry to the 17 unclassified 2-D datasets (§D4; the 4 1-D datasets bypass the registry).
- `D-summary`: one consolidated summary to Eloise at the end (notify-on-response directive), including the benchmark_30 provenance finding that feeds her pending "coherent HF hub revision" decision.

## 2. Verified environment facts (probed 2026-08-12; do not re-derive)

### 2.1 The benchmark

- `benchmark_30` = 30 datasets: 11 `core`, 6 `ext`, 13 `sharp`; listed in `benchmark_30/datasets_final.txt` on HF.
- Every LFS file in `benchmark_30` is sha256-identical to the corrected `eloisezeng/mf_field` `benchmark_42` release (three-way oid comparison, no downloads needed).
  `nicksung/mf_field` is no longer frozen — it was pushed 2026-08-12T18:56Z with this subset.
- SUPERSEDED 2026-08-12 (late): the earlier "two datasets newer locally" finding is FALSE against the current hub — the round-3 regens (`sharp/allen_cahn_2d` test split, `sharp/phase_field_crystal_2d`) were re-pushed as hub commit `36a5f198` on 2026-08-07, and a direct three-way sha256 check this session confirms benchmark_30 == corrected hub == local for every file of both datasets.
  **All 30 datasets are byte-identical local ↔ benchmark_30**; there are no deviations to document.
- All 30 datasets already exist locally under `mf_field/factory_mffp/data/` with the local naming rule: `core` names bare (`era5`, `fluid`, `heat_local`, `ifc_heat`, `ifc_poisson`, `poisson_local`, `poisson_generated`, `heat_generated`, `darcy_generated`, `allen_cahn_generated`, `lid_driven_cavity_generated`), `ext/X` → `ext__X`, `sharp/X` → `sharp__X`.

The full 30, by local name:

| group | datasets |
| --- | --- |
| core (11) | poisson_generated, poisson_local, heat_generated, heat_local, darcy_generated, allen_cahn_generated, lid_driven_cavity_generated, fluid, ifc_heat, ifc_poisson, era5 |
| ext (6) | ext__helmholtz_2d, ext__rayleigh_benard_2d, ext__wave_2d, ext__eikonal_2d, ext__cahn_hilliard_2d, ext__pressure_poisson_poiseuille |
| sharp (13) | sharp__euler, sharp__sod_1d, sharp__burgers_1d, sharp__burgers_2d, sharp__shallow_water_1d, sharp__shallow_water_2d, sharp__cahn_hilliard, sharp__porous_medium_1d, sharp__porous_medium_2d, sharp__helmholtz_2d, sharp__fisher_kpp_2d, sharp__allen_cahn_2d, sharp__phase_field_crystal_2d |

### 2.2 The certified model

- Family `models_r3/r3s2_route`, scored arm `A1_stack_ic_reg`, one job computes 7 arms on identical inputs.
- Certified checkout: worktree `mffp_autoresearch/round3/worktrees/r3s2_field_reach/B2` at `e606a4f` (build `211eb91` + reviewed citation fix; the commit the certified jobs ran at).
- Certified result: panel geomean skill 10.0853, per-seed [10.3528, 9.7249, 10.1781] on the 5-dataset round-3 panel (sharp__allen_cahn_2d, sharp__fisher_kpp_2d, sharp__cahn_hilliard, ifc_poisson, ifc_heat), 200 epochs, seeds {0,1,2}, SLURM jobs 158775/165550/165551, ~44–55 min per seed on one H200.
- The recipe carries ~60 env knobs, including `R3S2B2_ARM=A1_stack_ic_reg` and `R3S2_TARGET_SCALER_PREFLIGHT=not_applicable_no_helmholtz_no_pfc_in_datasets` — the latter's NAME is stale for benchmark_30 (which contains both Helmholtz variants and pfc), but it is a hard-asserted, recorded-only knob with no active code path; see D5.
- Checkpoints bind the dataset content sha256 into the payload; resume against changed arrays aborts.
- The family's vendored `upsample.py` `resolve_convention()` RAISES for any unclassified 2-D dataset (ADR r2-0001: convention assignment is an ADR-level decision).
  Classified today: PERIODIC_NODE {sharp__phase_field_crystal_2d, sharp__allen_cahn_2d, sharp__fisher_kpp_2d, sharp__cahn_hilliard}; DIRICHLET_NODE {ext__helmholtz_2d}; LEGACY_CELL {heat_local, fluid, sharp__sod_1d, ifc_poisson, ifc_heat}.
  That classifies 10 of 30; **20 are unclassified** (7 core, 5 ext, 8 sharp).
- `upsample_fields()` has a separate 1-D interpolation path; whether the four 1-D datasets (sod_1d is classified; burgers_1d, shallow_water_1d, porous_medium_1d are not) reach `resolve_convention()` at all is a build-time verification item (V-1D, §7).

### 2.3 The baseline

- `mf_field/factory_mffp/models/mf_fno_transfer_film` — LF-pretrain → HF-finetune FNO with FiLM conditioning on the condition vector (Lyu 2023), supports `ifc_raw` and `npz_l`.
- Already run under the EXACT round-3 protocol for the 5-dataset panel: `round3_anchors/film_baseline-R3`, jobs 171858–60, 3 seeds x 200 epochs, consumed by `round3/tools/make_film_denominator.py` (ADR r3-0006) with a stale-checkpoint-audit gate.
  This proves protocol reuse: the same runner layout extends to 30 datasets.

### 2.4 The evaluation protocol

- `mffp_autoresearch/round2/eval/score_panel.py` invokes each family's `smoke_eval.py` against a STRIPPED test view (test split physically contains no LF fields; family gate V2 asserts `test['lf_fids']` empty) and extracts the metric itself: prefer `rel_l2_per_sample` mean, then `rel_l2_mean`, then `nRMSE` — one definition for all families, so metric parity is structural.
- Stripped views are built by `round2/eval/make_stripped_view.py` into `round2/stripped_data/<dataset>/`; it currently iterates only the round-2 panel+guard list, so the campaign must extend coverage additively (§5.4).
- Result/cache roots are redirectable via `ROUND2_EVAL_RESULTS` / `ROUND2_EVAL_CACHE` env — but the copy-LF baseline registry is NOT redirectable: `score_panel.py` hard-loads `round2/eval/copylf_baselines.json` and raises for unlisted datasets, and `COPYLF_DEF_HASH` = sha256 of `panel_data.py`, so in-place registry extension would invalidate round-2/3 state.
  This is why D3 vendors the scorer.

## 3. Non-goals / out of scope

- No re-invention or tuning of either model; both run frozen recipes.
- No secondary reproduction against the STALE published HF arrays (deferred; see decision D1 rationale). It can be a follow-up if Eloise wants published-HF reproducibility.
- No change to any guarded surface: `factory_mffp/{data,baselines,eval,references,scripts,factory.md}` stay untouched; round-2/round-3 state stays untouched except the additive stripped-view build.
- No new HF uploads (the hub revision is Eloise's pending decision; this campaign only adds evidence to it).
- No 2500-epoch runs (round-1 holds remain in force).

## 4. Necessity gate (skill step 4, answered early because the spec's shape depends on it)

**What already does this?** The round-2/3 eval stack: `score_panel.py` + `make_stripped_view.py` + the family contract + the film-baseline runner layout under `round3_anchors/film_baseline-R3` + SLURM sbatch patterns from round 3.
**Reuse decision: the campaign REUSES all of it — by VENDORING where in-place use is impossible.** The scorer cannot run unmodified on non-round-2 datasets (hard copy-LF registry dependency, §2.4), and extending it in place would invalidate round-2/3 state (`COPYLF_DEF_HASH`), so D3 vendors `score_panel.py`+`panel_data.py` byte-identically except three named seams, with a guard test proving the metric path is unchanged.
New code is limited to: (a) a campaign staging/preflight script, (b) the convention-registry ADR extension (append-only, in the vendored copies), (c) the campaign copy-LF baseline builder, (d) SLURM launcher scripts, (e) an aggregator/report generator.
No new eval logic, no new metric code; the vendored scorer is a pinned copy, not a parallel implementation.
**Contradiction check:** ADR r2-0001 says convention assignment is ADR-level — we extend it BY an ADR, not by an env override.
The round-3 "certified" label attaches to byte-identical family code — decision D2 keeps it so.
**Mechanical guards:** §5.3 (registry completeness test), §5.2 (byte-identity manifest test).

## 5. Design decisions (locked unless Codex convergence overturns with evidence)

### D1 — Score against the LOCAL arrays, which ARE benchmark_30 exactly

The primary campaign scores against the local arrays; these are verified byte-identical to published benchmark_30 for all 30 datasets (§2.1), so scoring local IS scoring the published benchmark with zero deviations.
The staging manifest still records per-dataset `hub_identity` (verified hash equality) as a TRIPWIRE: any future local regeneration diverging from the published set fails staging loudly instead of silently changing what "benchmark_30" means.
Arrays from the defective frozen `nicksung` benchmark_42 tree are never mixed in (never-mix rule, unchanged).

### D2 — The certified family is FROZEN; the campaign runs a vendored copy with an append-only registry extension

- Vendor `models_r3/r3s2_route` at `e606a4f` into the campaign tree (`mffp_autoresearch/benchmark30/family/r3s2_route_b30/`).
- The ONLY permitted delta: appending dataset names to the three convention sets in `upsample.py` (and, if V-1D requires, registering 1-D datasets in whatever table the 1-D path keys on), exactly as ADR r2-0001 prescribes ("classify it … before using it").
- A file-hash manifest (committed) proves every other file byte-identical to `e606a4f`; a guard test recomputes and asserts this.
- If ANY code change beyond the registry append turns out to be required for some dataset, that dataset is EXCLUDED from the certified-model run (exclusion ledger, D8) — we do not patch, and we do not rename-and-recertify inside this campaign.
  Exception per brainstorm: a correctness bug demonstrably affecting certified behaviour too would be a stop-the-line event for Eloise, not a silent patch.
- Reporting rule: the model is labeled "r3s2-B2 certified stack (registry-extended to benchmark_30)"; the certified 10.0853 anchor is quoted only for the original 5-dataset panel.

### D3 — Evaluation protocol: VENDORED copy of the round-3 stripped-view scorer, with three named seam deltas

Codex round-1 finding (CONFIRMED, score_panel.py:47/198–202): `score_panel.py` hard-loads `round2/eval/copylf_baselines.json` from its own directory (not env-redirectable) and RAISES for any dataset without an entry, so the unmodified scorer cannot score the 20 non-round-2 datasets.
And `COPYLF_DEF_HASH` is the sha256 of `panel_data.py` itself (panel_data.py:219), so extending the registry in `round2/eval/panel_data.py` in place would invalidate ALL existing round-2/3 baselines and score caches — round-2 files must not be touched.

Resolution — vendor, exactly as D2 vendors the family:

- `mffp_autoresearch/benchmark30/eval/` gets byte-copies of `score_panel.py` + `panel_data.py` from `83a547e`, with ONLY these three seam deltas: (a) the baseline path constant points at the campaign's own `copylf_baselines.json`; (b) the convention registry sets are extended append-only per D4; (c) data-root/config resolution points at the campaign config (which carries per-dataset `dataset_dir`, needed for era5's `era5_train_test/` subdir).
- A seam manifest + guard test diff the vendored files against the `83a547e` originals and assert the delta is EXACTLY those named hunks — metric extraction (`_extract_test_metric`), nRMSE/skill definitions, cache logic, and the stripped-view contract assertions stay byte-identical, so metric parity with round 3 is provable, not claimed.
- A campaign script builds `state/copylf_baselines.json` for all 30 datasets using the vendored construction (its self-consistent `COPYLF_DEF_HASH` = vendored panel_data hash); this is a G2 gate output.
- `ROUND2_EVAL_RESULTS`/`ROUND2_EVAL_CACHE` point at `mffp_autoresearch_outputs/benchmark30/rev-<manifest_hash8>/{results,cache}` (content-addressed, D13).
- Metric: per-sample rel-L2 mean, as the (vendored, byte-identical) extractor computes it; identical for both families by construction.
- `eval/score.py` (factory leaderboard) is NOT used — it lacks the stripped-view guarantee.

### D4 — Convention registry extension is one ADR, fail-closed, with per-dataset rationale

- Grid shapes MEASURED 2026-08-12: exactly 4 datasets are 1-D (sharp__{sod,burgers,shallow_water,porous_medium}_1d, 128 cells) and take the family's 1-D path that bypasses `resolve_convention`; sharp__euler is 2-D (128x128) contrary to the brainstorm's guess; era5 is 721x1440; every other 2-D dataset is ≤ 256x256.
- One ADR (`docs/adr/` in the campaign tree) classifies each of the **17 genuinely-2-D unclassified datasets** (6 core: poisson_generated, poisson_local, heat_generated, darcy_generated, allen_cahn_generated, lid_driven_cavity_generated; era5; 5 ext: rayleigh_benard_2d, wave_2d, eikonal_2d, cahn_hilliard_2d, pressure_poisson_poiseuille; 5 sharp: euler, burgers_2d, shallow_water_2d, porous_medium_2d, helmholtz_2d) into `periodic_node` / `dirichlet_node` / `legacy_cell`, each with a one-paragraph rationale grounded in the dataset's generator/grid semantics (solver docs in `mf_field_eloise_data/`, `mf_field_extension_data/solvers.py`, `datasets_summary.csv`); the 3 unclassified 1-D datasets are recorded as `1d_path` for completeness.
- era5 needs its classification even though r3s2 cannot run it (D11): the campaign copy-LF baseline construction upsamples LF→HF for every scored dataset.
- CORRECTION from generator-evidence research: `allen_cahn_generated` is registered 1-D in the shared `data_adapters.geometry.KNOWN_GRIDS` (`(1, L)` entries; its dataset README's "16x16" is wrong), so it joins the 1-D bypass set — **16** 2-D datasets need ADR classification and **5** are 1-D.
- Accepted-approximation policy: minting new upsample variants is out of scope (D2 freezes the family; the vendored scorer's metric path must stay byte-identical).
  Where generator evidence shows semantics no existing variant implements — endpoint-node `linspace` grids (lid_driven_cavity, rayleigh_benard, wave, eikonal, era5-latitude, heat_generated's spatial axis) or periodic-node data on a NON-NESTED ladder that variant C's nesting assert rejects (`ext__cahn_hilliard_2d`, 24→64) — the ADR records `legacy_cell` as an ACCEPTED APPROXIMATION with the mismatch documented per dataset, rather than silently pretending an exact match.
  Both families and the copy-LF baseline share the same approximation per dataset, so comparisons stay internally consistent.
- The extension is applied append-only in BOTH vendored copies (campaign `panel_data.py` and the vendored family's `upsample.py`), and a guard test asserts every NEWLY classified benchmark_30 ID receives the same convention in both copies.
  The guard deliberately does NOT assert whole-registry equality: the frozen sources already differ intentionally on `sharp__phase_field_crystal_2d` (the family's `upsample.py` lists it PERIODIC_NODE; round-2 `panel_data.py` routes it through the `SPECTRAL_RUNG_DATASETS` override per ADR r3-0005) — that pre-existing difference is preserved as-is, and the guard exempts exactly the pre-existing entries recorded in the seam manifest.
- Unknown IDs keep failing closed (`resolve_convention` raise preserved).
- A staging test asserts registry coverage of exactly the 30 campaign IDs before any launch.
- Per brainstorm: for ambiguous datasets, deterministic synthetic-field interpolation unit checks validate the implementation semantics; conventions are NEVER chosen by looking at test metrics.
- The ADR records the registry revision; every run manifest and checkpoint records that revision.

### D5 — Recipe knobs carried verbatim; the preflight knob documented, not changed

- VERIFIED (smoke_eval.py:369–374, 1671–1677): the family HARD-ASSERTS `R3S2_TARGET_SCALER_PREFLIGHT == "not_applicable_no_helmholtz_no_pfc_in_datasets"` (any other value raises `R3S2ContractError`), and the knob is recorded-only — the sidecar writes `"applied": False, "Recorded, never applied"`; no scaler code path exists for any dataset.
- Therefore the knob is passed VERBATIM; running helmholtz/pfc datasets applies no special scaling to any dataset (identical treatment), and the campaign manifest documents that the knob's name and the sidecar's note text are historical strings scoped to the certified 5-dataset panel, superseded by this manifest's dataset list.
- All other knobs are carried verbatim from the certified B2 recipe.
- No per-dataset knob tuning at any point; anything the preflight rejects goes to the exclusion ledger rather than being tuned through (selection-leakage guard, brainstorm risk #6).
- The 7-arm computation is preserved (intrinsic to the certified job); ONLY `A1_stack_ic_reg` is reported; no per-dataset best-arm selection.

### D6 — Staged launch gates (no full fan-out before the gates pass)

1. **G0 hash/version lock** — staging manifest written; 30/30 local dirs hashed; the two deviations documented (the final `manifest_hash` is sealed at G1 once stripped-view hashes exist, per D12).
2. **G1 schema + stripped-view audit** — stripped views built for all 30; audit asserts test split physically LF-free for every dataset; loader smoke (shapes, LF rungs, condition vectors) for both layouts.
3. **G2 registry completeness** — ADR merged; coverage test green; synthetic upsample unit checks green; campaign `copylf_baselines.json` built for all 30 with the vendored construction and committed.
4. **G3 contract smoke** — both families x all 30 datasets x 2 epochs x seed 0 on SLURM; deterministic failures → exclusion ledger; this is the fixed, predeclared compatibility suite.
5. **G4 one full seed** — both families x eligible datasets x 200 epochs x seed 0.
6. **G5 remaining seeds** — seeds 1–2, launched only after G4 results validate (completion, not metric quality — no selection on metrics).

### D7 — Fairness contract (film baseline)

- Same staging manifest and array hashes, same stripped test views, same seeds {0,1,2}, same 200-epoch ceiling, same checkpoint rule (`last.pt`, resume mandatory), same metric extraction.
- FiLM's LF pretraining uses only training-fold LF data (its existing smoke_eval behaviour — verified in round 3; re-asserted in G1 audit); no test-derived statistics for either family.
- Equal-epoch policy WITH reported wall-clock/GPU-time per run (the brainstorm's compute-parity caveat is handled by reporting, not by equalizing FiLM's extra pretrain phase — that phase is intrinsic to the method being benchmarked).
- No per-dataset accommodations for either family (D11); peak memory, wall-clock, and effective batch are recorded per run.

### D8 — Exclusion ledger; coverage separated from score

- Every dataset x family that cannot produce a protocol-compliant result gets a ledger entry: {dataset, family, class: unsupported-by-frozen-family | infra-failure | preflight-reject, evidence}.
- Deterministic compatibility failures stop that dataset/family pair after the G3 smoke; infra failures retry bounded (3 attempts, logs preserved).
- No imputation; the panel geomean runs over the predeclared eligible set = datasets where BOTH families have compliant runs for all 3 seeds; a coverage table reports everything else.
- Film-relative skill is reported only on that common set.

### D9 — Aggregation and report conventions

- Per-dataset: per-sample rel-L2 mean per seed, 3-seed mean, min/max.
- Film-relative skill per dataset: `nrmse_film_mean / nrmse_model_mean` (round-3 convention; >1 means the model beats film).
- Headline: geometric mean of per-dataset skill over the common eligible set, per-seed, reported as 3-seed mean with per-seed [min, max] — labeled as a seed+run interval per the round-3 finding that same-seed cross-node drift is 0.62x seed variance (NOT presented as a proper CI over independent observations; the brainstorm's CI-estimator caveat is resolved by this explicit labeling, predeclared here).
- rel-L2 numbers on near-uniform fields are paired with mean-removed context in the report narrative (rel-l2-is-level-dominated memory).
- Secondary tables: per-group (core/ext/sharp) geomeans; coverage/failure table; wall-clock and peak-memory table; data-version manifest.
- Report goes through the Codex↔Claude fact-check convergence loop before delivery.

### D10 — SLURM execution shape

- One sbatch job per {family, seed} iterating its dataset list sequentially (score_panel caches per dataset; `last.pt` resume makes the unit preemption-safe), partition/gres per round-3 pattern (`gpu`, `gpu:nvidia_h200:1`), time budget sized from certified per-seed timings (~1 h per 5-dataset seed → request 8 h for 30 datasets, era5 padding included).
- `--mail-user=ezeng@caltech.edu --mail-type=END,FAIL` on every job (≥1 h directive).
- Immutable per-attempt logs under the campaign output root; a changed dataset hash invalidates resume by construction (checkpoint binding) and requires a new run id.
- Estimated total: 30 ds x 2 families x 3 seeds x 200 epochs ≈ 15–25 GPU-h — within normal cluster usage, no overage spend.

### D11 — No per-dataset accommodations; era5 is a predeclared r3s2 exclusion

Codex round-1 finding (CONFIRMED): D7/D11 as first drafted contradicted D5's verbatim-knob rule.
Resolved policy — there are NO per-dataset knob accommodations for either family, period:

- r3s2 hard-raises when its built-in `WORK_CAP=256` fires (smoke_eval.py:650–654: working grid must equal native HF grid); era5 is 721x1440, so **era5 is structurally unsupported by the frozen family** and enters the exclusion ledger (class unsupported-by-frozen-family) at G3 with the raise as evidence — predeclared here, not discovered post hoc.
- The film baseline runs era5 as-is with its own internal batch handling; if it OOMs under the standard H200 allocation, that cell is ledgered as infra-failure after the bounded retries. Either way era5 cannot enter the common eligible set (D8 requires both families).
- Peak memory and wall-clock are recorded for every run (D7); no knob of either family is changed for any dataset.

### D12 — Content-addressed run identity (cache/checkpoint invalidation on data change)

Codex round-1 finding (CONFIRMED): the scorer cache key is `sha256(code_hash|dataset|epochs|seed)` with no data-content term (score_panel.py:203), and the film checkpoint accepts `last.pt` on `(epochs_target, grid)` alone (film smoke_eval.py:156) with no dataset hash — so a changed array under the same name could silently reuse a stale score or checkpoint.
Only r3s2 binds data hashes into its checkpoints.
Resolution at the PATH layer, with zero frozen-code edits:

- `manifest_hash = sha256(registry_revision + the 30 sorted per-dataset SOURCE content hashes + the 30 sorted STRIPPED-VIEW content hashes)` is computed after the stripped-view build and frozen in the staging manifest — identity covers the exact bytes the scorer consumes, not just their source arrays.
- The aggregator's collect-time re-hash covers BOTH the source arrays and the stripped views; a mismatch on either rejects the result.
- EVERY mutable root — results, cache, checkpoints, logs — lives under `mffp_autoresearch_outputs/benchmark30/rev-<manifest_hash8>/`; any data change → new manifest hash → empty cache and fresh checkpoint namespace by construction.
- The aggregator re-hashes the staged arrays at collect time and REJECTS any result whose recomputed manifest hash differs from the frozen one (act-on-fresh-state directive).
- Film's resume granularity is whole-run (it writes `last.pt` only after both training stages complete — verified); acceptable because per-dataset runs are minutes-scale, and the bounded-retry policy (D8) covers preemption restarts.

### D13 — Decision records and notification

- This spec + the ADR + the staging manifest ARE the written decision records (operator-delegation directive).
- Eloise is notified once at the end with the consolidated report, plus immediately if a stop-the-line event occurs (pause-rounds-on-bug-discovery) or a decision outside the approved envelope becomes necessary.
- The provenance finding is included in the summary: benchmark_30 (nicksung, unfrozen and pushed 2026-08-12) is a byte-identical subset of the CURRENT corrected hub — fully up to date, no action needed on it; the formerly pending hub staleness was resolved by the 2026-08-07 re-push (hub commit `36a5f198`).
- The summary also carries the generator-evidence data-methodology caveats that Eloise may want to act on as benchmark curator: `ext__pressure_poisson_poiseuille`'s LF is block-mean(HF)+noise (paper-faithful to Partin 2022, but it violates the repo's own "LF is never downsampled HF" rule); `heat_generated`'s LF↔HF time-window inconsistency (`n/(n-1)` factor); era5's per-rung sample counts differ, making index-aligned LF↔HF pairing unverifiable for measurement data.
  These are REPORT CAVEATS for the campaign (both models face identical data, so the comparison stands), not campaign blockers.

## 6. Engineering shape (what gets built; the plan will decompose this)

All new code lives under `mffp_autoresearch/benchmark30/` in the worktree:

- `staging/manifest.py` → writes `state/staging_manifest.json` (G0) — 30 IDs, source paths, split content hashes, corrected-vs-HF status, stripped-view hashes, registry revision.
- `family/r3s2_route_b30/` — vendored family (D2) + `state/family_byte_identity.json` + guard test.
- `eval/` — vendored `score_panel.py` + `panel_data.py` (D3) + seam manifest + byte-identity guard test; `eval/make_copylf_baselines_b30.py` → `state/copylf_baselines.json`.
- `staging/preflight.py` (G1–G2 checks as runnable asserts; includes the stripped-view build calls — importing round-2 `_mirror`/`_verify` — and the LF-free audit for all 30).
- `adr/0001-benchmark30-convention-registry.md` (D4).
- `slurm/` — sbatch templates + launcher for the 6 {family, seed} jobs + the G3 smoke job pair.
- `aggregate/collect.py` → `leaderboard.json`; `aggregate/report.py` → report tables.
- `tests/` — registry coverage, byte-identity, synthetic upsample checks, aggregator unit tests on fixture results (marked FIXTURE).

## 7. Build-time verification items — ALL RESOLVED (probed 2026-08-12, this session)

- **V-1D RESOLVED**: `upsample_fields()` routes any field with grid `H == 1` on both levels through a legacy 1-D `zoom` path BEFORE `resolve_convention` is consulted (upsample.py:147–156).
  So genuinely 1-D datasets need NO 2-D convention entry; the ADR classifies only the genuinely 2-D unclassified datasets, and the staging manifest records every dataset's grid shape so the eligible-for-ADR set is measured, not assumed.
- **V-PREFLIGHT RESOLVED**: see D5 — knob verbatim, hard assert, scaler never applied, historical note documented in the manifest.
- **V-FILM-LAYOUT RESOLVED**: both families load through the SAME shared loader, `data_adapters.load_mf_dataset` (film smoke_eval.py:43; r3s2 smoke_eval.py:100) — layout support is symmetric at the loader level; residual per-dataset incompatibilities are exactly what the G3 smoke matrix is for.
- **V-STRIPPED-EXTEND RESOLVED**: `make_stripped_view.py` exposes importable `_mirror(src, dst)` and `_verify(view)`; only its `main()` is panel+guard-scoped.
  The campaign preflight imports `_mirror`/`_verify` and iterates the 30 campaign IDs — zero edits to round-2 files.
- **V-ERA5-SIZE RESOLVED**: era5 is 1.2 GB, npz_l layout with 9 LF levels, and its npz files live in a SUBDIRECTORY `era5/era5_train_test/` — the staging manifest must therefore carry an explicit `dataset_dir` per dataset (not `data_root/<name>` by convention), and the preflight asserts each recorded dir actually loads.

## 8. Acceptance criteria

1. Staging manifest committed, 30/30 hashed, hub-identity tripwire recorded (G0).
2. All 30 stripped views exist and pass the LF-free audit (G1).
3. Registry ADR merged; coverage + byte-identity + synthetic-upsample tests green (G2).
4. G3 smoke matrix complete with every cell either PASS or ledgered.
5. 6 full jobs (2 families x 3 seeds) complete; every eligible {family, dataset, seed} has a validated result JSON.
6. `leaderboard.json` + report generated by code (no hand-computed numbers), fact-check-converged.
7. Consolidated summary delivered to Eloise; no mid-campaign questions unless stop-the-line.
