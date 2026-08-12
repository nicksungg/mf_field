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
- `D-adr`: one ADR extending the upsample-convention registry to the 20 unclassified datasets (§5.3).
- `D-summary`: one consolidated summary to Eloise at the end (notify-on-response directive), including the benchmark_30 provenance finding that feeds her pending "coherent HF hub revision" decision.

## 2. Verified environment facts (probed 2026-08-12; do not re-derive)

### 2.1 The benchmark

- `benchmark_30` = 30 datasets: 11 `core`, 6 `ext`, 13 `sharp`; listed in `benchmark_30/datasets_final.txt` on HF.
- Every LFS file in `benchmark_30` is sha256-identical to the corrected `eloisezeng/mf_field` `benchmark_42` release (three-way oid comparison, no downloads needed).
  `nicksung/mf_field` is no longer frozen — it was pushed 2026-08-12T18:56Z with this subset.
- Two datasets are NEWER locally than the HF copies, from post-upload round-3 regenerations: `sharp/allen_cahn_2d` (test split only, ADR r3-0003) and `sharp/phase_field_crystal_2d` (all splits, ADR r3-0002).
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
- The recipe carries ~60 env knobs, including `R3S2B2_ARM=A1_stack_ic_reg` and `R3S2_TARGET_SCALER_PREFLIGHT=not_applicable_no_helmholtz_no_pfc_in_datasets` — the latter is INVALID for benchmark_30 (which contains both Helmholtz variants and pfc) and must be re-derived (§5.5).
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
- Result/cache roots are redirectable via `ROUND2_EVAL_RESULTS` / `ROUND2_EVAL_CACHE` env (used to keep campaign outputs out of round-2/3 state).

## 3. Non-goals / out of scope

- No re-invention or tuning of either model; both run frozen recipes.
- No secondary reproduction against the STALE published HF arrays (deferred; see decision D1 rationale). It can be a follow-up if Eloise wants published-HF reproducibility.
- No change to any guarded surface: `factory_mffp/{data,baselines,eval,references,scripts,factory.md}` stay untouched; round-2/round-3 state stays untouched except the additive stripped-view build.
- No new HF uploads (the hub revision is Eloise's pending decision; this campaign only adds evidence to it).
- No 2500-epoch runs (round-1 holds remain in force).

## 4. Necessity gate (skill step 4, answered early because the spec's shape depends on it)

**What already does this?** The round-2/3 eval stack: `score_panel.py` + `make_stripped_view.py` + the family contract + the film-baseline runner layout under `round3_anchors/film_baseline-R3` + SLURM sbatch patterns from round 3.
**Reuse decision: the campaign REUSES all of it.** New code is limited to: (a) a campaign staging/preflight script, (b) the convention-registry ADR extension (append-only data change inside a vendored family copy), (c) SLURM launcher scripts for 30-dataset sequential runs, (d) an aggregator/report generator.
No new eval logic, no new metric code, no parallel scoring path.
**Contradiction check:** ADR r2-0001 says convention assignment is ADR-level — we extend it BY an ADR, not by an env override.
The round-3 "certified" label attaches to byte-identical family code — decision D2 keeps it so.
**Mechanical guards:** §5.3 (registry completeness test), §5.2 (byte-identity manifest test).

## 5. Design decisions (locked unless Codex convergence overturns with evidence)

### D1 — Score against the LOCAL corrected arrays

The primary campaign scores against the local corrected arrays, not the stale HF copies of `sharp__allen_cahn_2d` (test) and `sharp__phase_field_crystal_2d`.
Why: round 3 certified against corrected data; r3s2_route checkpoints bind content hashes; mixing versions destroys comparability (Codex brainstorm risk #3, concurring verdict).
The staging manifest names the two deviations explicitly as "benchmark_30 IDs, corrected local realization" with all 30 dataset content hashes.
HF-stale runs are never pooled with corrected runs.

### D2 — The certified family is FROZEN; the campaign runs a vendored copy with an append-only registry extension

- Vendor `models_r3/r3s2_route` at `e606a4f` into the campaign tree (`mffp_autoresearch/benchmark30/family/r3s2_route_b30/`).
- The ONLY permitted delta: appending dataset names to the three convention sets in `upsample.py` (and, if V-1D requires, registering 1-D datasets in whatever table the 1-D path keys on), exactly as ADR r2-0001 prescribes ("classify it … before using it").
- A file-hash manifest (committed) proves every other file byte-identical to `e606a4f`; a guard test recomputes and asserts this.
- If ANY code change beyond the registry append turns out to be required for some dataset, that dataset is EXCLUDED from the certified-model run (exclusion ledger, D8) — we do not patch, and we do not rename-and-recertify inside this campaign.
  Exception per brainstorm: a correctness bug demonstrably affecting certified behaviour too would be a stop-the-line event for Eloise, not a silent patch.
- Reporting rule: the model is labeled "r3s2-B2 certified stack (registry-extended to benchmark_30)"; the certified 10.0853 anchor is quoted only for the original 5-dataset panel.

### D3 — Evaluation protocol: round-3 stripped-view score_panel, unmodified

- Both families run through `round2/eval/score_panel.py` with `ROUND2_EVAL_RESULTS`/`ROUND2_EVAL_CACHE` pointed at `mffp_autoresearch_outputs/benchmark30/{results,cache}`.
- Metric: per-sample rel-L2 mean, as score_panel computes it (the round's ONE definition); identical for both families by construction.
- `eval/score.py` (factory leaderboard) is NOT used — it lacks the stripped-view guarantee.

### D4 — Convention registry extension is one ADR, fail-closed, with per-dataset rationale

- One ADR (`docs/adr/` in the campaign tree) classifies each of the 20 unclassified datasets into `periodic_node` / `dirichlet_node` / `legacy_cell` (or `1d_path` where V-1D shows the 2-D registry is not consulted), each with a one-paragraph rationale grounded in the dataset's generator/grid semantics (solver docs in `mf_field_eloise_data/`, `mf_field_extension_data/solvers.py`, `datasets_summary.csv`).
- Unknown IDs keep failing closed (`resolve_convention` raise preserved).
- A staging test asserts registry coverage of exactly the 30 campaign IDs before any launch.
- Per brainstorm: for ambiguous datasets, deterministic synthetic-field interpolation unit checks validate the implementation semantics; conventions are NEVER chosen by looking at test metrics.
- The ADR records the registry revision; every run manifest and checkpoint records that revision.

### D5 — Recipe knob re-derivation, predeclared

- `R3S2_TARGET_SCALER_PREFLIGHT` is re-derived for the 30-dataset panel BEFORE launch by reading what the preflight actually checks in the family code, and the derived value + reasoning goes into the frozen campaign spec file.
- All other knobs are carried verbatim from the certified B2 recipe.
- No per-dataset knob tuning at any point; anything the preflight rejects goes to the exclusion ledger rather than being tuned through (selection-leakage guard, brainstorm risk #6).
- The 7-arm computation is preserved (intrinsic to the certified job); ONLY `A1_stack_ic_reg` is reported; no per-dataset best-arm selection.

### D6 — Staged launch gates (no full fan-out before the gates pass)

1. **G0 hash/version lock** — staging manifest written; 30/30 local dirs hashed; the two deviations documented.
2. **G1 schema + stripped-view audit** — stripped views built for all 30; audit asserts test split physically LF-free for every dataset; loader smoke (shapes, LF rungs, condition vectors) for both layouts.
3. **G2 registry completeness** — ADR merged; coverage test green; synthetic upsample unit checks green; V-1D resolved.
4. **G3 contract smoke** — both families x all 30 datasets x 2 epochs x seed 0 on SLURM; deterministic failures → exclusion ledger; this is the fixed, predeclared compatibility suite.
5. **G4 one full seed** — both families x eligible datasets x 200 epochs x seed 0.
6. **G5 remaining seeds** — seeds 1–2, launched only after G4 results validate (completion, not metric quality — no selection on metrics).

### D7 — Fairness contract (film baseline)

- Same staging manifest and array hashes, same stripped test views, same seeds {0,1,2}, same 200-epoch ceiling, same checkpoint rule (`last.pt`, resume mandatory), same metric extraction.
- FiLM's LF pretraining uses only training-fold LF data (its existing smoke_eval behaviour — verified in round 3; re-asserted in G1 audit); no test-derived statistics for either family.
- Equal-epoch policy WITH reported wall-clock/GPU-time per run (the brainstorm's compute-parity caveat is handled by reporting, not by equalizing FiLM's extra pretrain phase — that phase is intrinsic to the method being benchmarked).
- Peak memory / batch-size accommodations (era5) are declared per-dataset in the frozen spec BEFORE launch, applied to both families identically where applicable (D11).

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

### D11 — era5 memory policy

- A fixed, declared policy written into the frozen spec before launch (e.g. batch-size cap + gradient accumulation to preserve effective batch), applied identically where each family exposes the knob; peak memory and actual optimizer updates recorded per run.
- If era5 cannot run under the declared policy without code changes to the frozen family, it goes to the exclusion ledger (D2 > completeness).

### D12 — Decision records and notification

- This spec + the ADR + the staging manifest ARE the written decision records (operator-delegation directive).
- Eloise is notified once at the end with the consolidated report, plus immediately if a stop-the-line event occurs (pause-rounds-on-bug-discovery) or a decision outside the approved envelope becomes necessary.
- The provenance finding (benchmark_30 = corrected-subset; nicksung repo unfrozen today; 2 stale datasets now ALSO stale in benchmark_30) is included in the summary as input to her pending HF-hub-revision decision.

## 6. Engineering shape (what gets built; the plan will decompose this)

All new code lives under `mffp_autoresearch/benchmark30/` in the worktree:

- `staging/manifest.py` → writes `state/staging_manifest.json` (G0) — 30 IDs, source paths, split content hashes, corrected-vs-HF status, stripped-view hashes, registry revision.
- `family/r3s2_route_b30/` — vendored family (D2) + `state/family_byte_identity.json` + guard test.
- `staging/preflight.py` (G1–G2 checks as runnable asserts; includes the stripped-view build calls and the LF-free audit for all 30).
- `adr/0001-benchmark30-convention-registry.md` (D4).
- `slurm/` — sbatch templates + launcher for the 6 {family, seed} jobs + the G3 smoke job pair.
- `aggregate/collect.py` → `leaderboard.json`; `aggregate/report.py` → report tables.
- `tests/` — registry coverage, byte-identity, synthetic upsample checks, aggregator unit tests on fixture results (marked FIXTURE).

## 7. Build-time verification items (carried into the plan)

- **V-1D**: read the family's 1-D path; establish whether 1-D datasets consult `resolve_convention` and what registration they need; record in the ADR.
- **V-PREFLIGHT**: read the preflight implementation; derive the correct `R3S2_TARGET_SCALER_PREFLIGHT` value for a panel containing helmholtz (x2) and pfc.
- **V-FILM-LAYOUT**: confirm `mf_fno_transfer_film` supports both on-disk layouts across all 30 (it declares `ifc_raw` + `npz_l`; the certified family declares `ifc_raw` + `npz`) — any gap is a G3 exclusion, not a patch.
- **V-STRIPPED-EXTEND**: confirm `make_stripped_view.py` can be driven additively for non-panel datasets without editing round-2 config (e.g. via its CLI or a thin campaign wrapper that calls its functions) — round-2 files are not modified.
- **V-ERA5-SIZE**: measure era5 array sizes before declaring the memory policy.

## 8. Acceptance criteria

1. Staging manifest committed, 30/30 hashed, deviations documented (G0).
2. All 30 stripped views exist and pass the LF-free audit (G1).
3. Registry ADR merged; coverage + byte-identity + synthetic-upsample tests green (G2).
4. G3 smoke matrix complete with every cell either PASS or ledgered.
5. 6 full jobs (2 families x 3 seeds) complete; every eligible {family, dataset, seed} has a validated result JSON.
6. `leaderboard.json` + report generated by code (no hand-computed numbers), fact-check-converged.
7. Consolidated summary delivered to Eloise; no mid-campaign questions unless stop-the-line.
