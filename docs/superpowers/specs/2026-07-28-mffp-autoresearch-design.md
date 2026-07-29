# MFFP Autoresearch Round 1 — Design

**Status:** approved design, pre-implementation spec
**Date:** 2026-07-28
**Decided by:** Eloise (architecture, scale, eval-layer placement, stream structure via Q&A); panel derivation delegated to Claude and grounded in `mf_field/akash/results/dataset_characterization.csv` + `bench_full_metrics.csv`.
**Supersedes for this work:** the factory CEO loop (`factory ceo … --mode research`) — retired for this workstream, left untouched for the mentor's use.
**Builds on:** `docs/planning/AUTORESEARCH_PLAN.md`, `docs/planning/META_AUTORESEARCH.md`, `docs/proposals/AI_Scientist.pdf` (the ICML 2026 AI4Science paper), and the `playground_test` round-5b scaffold (`/resnick/groups/Hippo/ezeng/playground_test/autoresearch_round5b/`).

---

## 1. Goal

Find genuine experiments that improve understanding of **why multi-fidelity fusion fails on the critical datasets**, and in doing so produce model families that close those gaps. A better panel score is the *test* of that understanding, not the goal (same stance as the quadruped round's program §1).

Two concrete success criteria for the round:

1. `ifc_poisson` at or below the paper bar (0.036; stretch: IFC-GPODE 0.018).
2. At least one model beating the copy-LF baseline on each of the five beyond-copy datasets (§3) — currently **zero** models do, on any of them.

## 2. Objective and metric

**One nRMSE definition for the whole round** (the audit found three coexisting — F01): per-sample relative L2 on the raw HF field, `||y_pred − y_hf||₂ / ||y_hf||₂`, averaged over test samples. Defined once in the round's eval layer; every score in the round comes from that one code path.

**Per-family panel score:** geomean over panel datasets of the **copy-LF skill ratio**

```
skill(family, dataset) = nRMSE(family, dataset) / nRMSE(copy-LF, dataset)
```

where copy-LF = output the interpolated LF field unchanged (precomputed once per dataset). Lower is better; < 1 means the model added value over its own input. Properties this buys:

- Degenerate datasets structurally cannot reward junk — beating copy-LF *is* the definition of MF working. (Fixes the `score.py` vs `compute_elo_full.py` inconsistency without touching either.)
- It is a per-family score across all panel datasets, not best-model-per-dataset — no reward for winning one dataset and blowing up elsewhere (`AUTORESEARCH_PLAN.md` §2's objection to `composite_nRMSE`).
- Per-dataset skill ratios are reported alongside the geomean in every card; claims about a specific gap cite the specific dataset.

**Uncertainty:** every reported number is mean ± stratified percentile-bootstrap 95% CI over 3 seeds (seeds fixed at {0, 1, 2}), with the 1+2 staging protocol (§8). An improvement claim must clear both its pre-registered falsification threshold **and** the seed noise floor measured in batch 0 (§10). Single-seed pilots are always labelled as such.

## 3. The critical panel

### 3.1 Derivation (recorded so it can be re-run)

For each of the 42 datasets in `benchmark_42/`, compare the best zoo model's rel-L2 (from `mf_field/akash/results/bench_full_metrics.csv`, 12 families × 40 datasets, 2500 epochs) against the copy-LF baseline (`lf_hf_rel_resid` in `mf_field/akash/results/dataset_characterization.csv`). Exclude datasets flagged `mf_useless` or `degenerate` in `benchmark_42/MANIFEST.csv` (11 of 42 — on those, copy-LF is near-optimal or LF↔HF is decorrelated, so no fusion method can be rewarded).

### 3.2 Attack panel (6 datasets — the round's objective)

| dataset | best zoo model | copy-LF | best/copy | note |
|---|---|---|---|---|
| `ext/helmholtz_2d` | 0.478 | 0.205 | 2.3× worse | oscillatory; every model loses to identity |
| `sharp/phase_field_crystal_2d` | 0.349 | 0.147 | 2.4× worse | high-band LF-HF corr ≈ 0 |
| `sharp/allen_cahn_2d` | 0.245 | 0.041 | 5.9× worse | copy-LF already strong; models destroy it |
| `sharp/fisher_kpp_2d` | 0.247 | 0.195 | 1.3× worse | front propagation |
| `sharp/cahn_hilliard` | 0.180 | 0.138 | 1.3× worse | spinodal interfaces |
| `ifc_poisson` | 0.042¹ | 80.3 | ≪ 1 | **the only paper-bar loss** (0.036; GPODE 0.018). N_hf = 5 — every claim carries that caveat |

¹ factory-side best (`mf_fno_pinn_transfer`); the akash bench best is 0.047 (`mfrnp`). Batch 0 recertifies all anchors through the round's own eval layer (§10).

The first five are unflagged in the manifest, N_hf = 400, healthy overall LF-HF correlation — real, learnable, and currently failed by all ~45 families. They are also exactly the sharp-interface fields the mentor's shock work targets.

### 3.3 Guard set (no-regression check, not part of the objective)

`heat_local`, `fluid`, `sharp/sod_1d` — three solved datasets spanning smooth, NS, and shock regimes. Run at smoke tier only for experiments that claim a panel win; a guard regression > 2× vs anchor flags the card (recorded in part 5, does not auto-reject — the analyzer interprets).

### 3.4 Facts that reframe the original prompt (recorded per Eloise's correction)

- `convnext_unet_film` is a **ConvNeXt-U-Net backbone** (with the FiLM + transfer recipe), *not* a CNN-FNO hybrid, and it performs well (rank 2 overall). Its one pathology is `sharp/sod_1d` (0.51 vs zoo best 0.0001).
- The **FNO→CNN two-stage hybrid** (LF field as explicit intermediate tensor) exists only as a design report, `docs/reports/MF_FNO_CNN_Hybrid_Report.md` — no family in this tree implements it.
- **iFNO** was never built (candidate M3 in `docs/proposals/MODELS_TO_TRY.md`).
- `sharp/sod_1d` — the canonical shock tube — is already solved by `fno_fire_distcond` (0.0001). The open shock-adjacent problem is the sharp-**2D** family above, where the failure mode is *fusion destroying LF information*, not inability to represent discontinuities.
- Falsified levers (do not re-propose as-is): WNO backbone swap (`wno_transfer_film`, worse on sharp than its FNO control), LF low-mode freezing (`mf_fno_spectral`), diffusion prior for point accuracy (`mf_fno_diffprior`). Unfalsified levers with quantified headroom: test-time PDE-residual refinement (`mf_fno_ptr`, −21% with a placeholder Laplacian), FNO↔Transolver pairwise oracle (+30.6%, `fno_transolver_seq` built but unbenchmarked), all-pairs fidelity training (`mf_fno_allpairs`, best on the hard subset but times out on era5/pm_test), IRNO-style iterative refinement (report proposal N1, unbuilt).

## 4. Architecture — port of the round-5b scaffold

New top-level directory `mffp_autoresearch/round1/` (sibling of `mf_field/`), structured exactly like `autoresearch_round5b/`:

```
mffp_autoresearch/round1/
  project.yaml          # the whole config surface: paths, streams, immutables,
                        # score, seed_protocol, caps, budgets, crons, sbatch
  program.md            # §1 goal, §2 metric, §4 structure, §5 immutables,
                        # §6 roster, §8 prerequisites, §9 commands,
                        # §12 per-stream conventions, §13 project overview
  subagents/            # 9 prompts + _shared/ partials (source of truth;
                        # installed to ~/.claude/agents/ at launch)
  eval/                 # the round's own eval layer (§7)
  experiment_cards/{stream}/batch_{N}/B{N}.json
  websearches/  brainstormer/  worktrees/  tools/  state/  docs/adr/
```

**Kept from round 5b unmodified:** streams-with-serial-batches (no phases, no cross-stream sync); one experiment = one card = one worktree = one branch = one SLURM chain; the 9-subagent roster (websearcher, brainstormer, experiment-starter, -builder, code-reviewer, -debugger, -initial-analyzer, -mechanism-analyzer with 3 turns + register, maintainer) plus ad-hoc advisor-consult; no oracle — the brainstormer designs, grounded in `program.md` per `_shared/decision_discipline.md`; immutable card parts 1–4 + `expected_falsification` locked before launch; per-agent card write-allowlist; handoff memos in `<worktree>/notes/`; pre-return checklists; return protocol (SUCCESS = invocation completed, orchestrator advances only on SUCCESS, max 2 retries); auto-skip with `reopen_candidate`, `blocked.md` as log not queue; 3 consecutive skips ⇒ stream abandoned; timing ledger feeding `--time`; cron-pulsed single-session orchestrator (10-min pulse + 20-min maintainer) with state in `state/{stream}/…` re-read on every wake.

**Orchestration mechanics:** agent defs installed by copying `mffp_autoresearch/round1/subagents/*.md` → `~/.claude/agents/` (replacing the quadruped set — dispatch resolves from the user-level registry, a documented R4 footgun). Kickoff = one persistent session given the role-assigning launch prompt (adapted from `round5_preparation/HOW_TO_LAUNCH.md`). Subagents that run python get `bypassPermissions`; `description="{stream}-B{N}"` is the maintainer's archive key.

**Worktrees:** forked from a stripped substrate branch (code + configs, no data); training/eval outputs go to a sibling `mffp_autoresearch_outputs/round1/{stream}/B{N}/…`, never into the worktree. Model code for an experiment lives in the worktree under a contract-compliant family dir; promotion into `factory_mffp/models/` is a **human** post-round step, keeping the factory leaderboard stable mid-round.

## 5. Four improvements over round 5b

All four come from this repo's own post-mortems, applied at design time rather than discovered mid-round.

1. **Prior-art gate as a hard pipeline stage.** The track record on novelty is 0-for-4 (`AUTORESEARCH_PLAN.md` §5: candidates A/B/C + the FNO→CNN hybrid all pre-empted, discovered only after write-up). The websearcher's final iteration becomes a **novelty verdict**: retrieval-grounded (must cite fetched sources, not model recall), answering "is this mechanism published; if so, what is the surviving MF-composition novelty?" The brainstormer must quote the verdict in the card's motivation; a proposal ruled pre-empted must pivot to its MF composition or the slot is skipped with reason `preempted`. The card gains a locked `prior_art` field (verdict + citations).
2. **Diagnostic slots.** A card may be a *measurement* instead of a model — `card_type: diagnostic`, no training, single run, falsification clause about what the measurement will show. Rationale: `META_AUTORESEARCH.md` §6 — "cheap diagnostics beat expensive search"; the highest-value known action (the Phase-1 spectral diagnostic) is a measurement. s2's batch 1 is a diagnostic card by design (§6).
3. **Seam assertions from day 1** (the `round5_rerun_fixes` lessons, whose shared root cause was "silent, plausible-but-wrong defaults at the seams, with no assertion to fail loudly"):
   - every card carries a structured `recipe` block (dataset dir, epochs, seed, env knobs, base-family commit); a builder finding it missing returns `BLOCKED: recipe-missing` — no fallback to repo defaults;
   - train↔eval contract assertions in the eval layer: grid shape, normalization stats, and the nRMSE-definition hash are checked at load and raise on mismatch;
   - anchors live in exactly one place (`state/anchors/*.json`); the dashboard renders from it, never recomputes.
4. **Noise-floor batch 0.** Before any research batch: run the anchor family on the panel at 3 seeds through the round's eval layer, recording per-dataset seed-to-seed spread. Every stream's falsification threshold must exceed its dataset's noise floor (the MFFP analogue of round 5's G1 determinism gate; without it, sub-noise "wins" are unfalsifiable). Batch 0 doubles as anchor certification (§3.2 footnote).

## 6. Streams (pilot: 5, mixed lineup)

Streams own research questions, not model families; each batch proposes whatever model, mechanism, or diagnostic serves the question. Two dataset-gap streams, two method-lever streams, one tuning stream.

| stream | class | question it owns | anchor | batch-1 seed direction |
|---|---|---|---|---|
| `s1_poisson` | gap | why is `ifc_poisson` above the paper bar, and what closes it? | best certified zoo score on `ifc_poisson` | all-pairs training (`mf_fno_allpairs`, mentor's best on the hard subset) applied to the gap; N_hf = 5 caveat on every claim |
| `s2_beyond_copy` | gap | why does every fusion mechanism lose to copy-LF on the five sharp-2D datasets? | copy-LF itself (skill = 1.0) | **diagnostic card**: spectral + spatial localization of where models destroy LF information (per-band error vs copy-LF, error maps vs interface distance); later batches attack the diagnosed mechanism |
| `s3_testtime` | lever | how far does test-time refinement go when the governing residual is real? | panel score of the frozen base family it refines | true PDE residuals for `mf_fno_ptr` (placeholder Laplacian already gave −21%); then IRNO-style iterative refinement (proposal N1) |
| `s4_hybrid_routing` | lever | can MF *compositions* of hybrid operators capture the +30.6% FNO↔Transolver oracle? | panel score of `mf_fno_transfer_film` | benchmark the built-but-unmeasured `fno_transolver_seq`; then learned per-band/per-region routing. Backbone swaps are pre-falsified (§3.4) and ruled out by convention |
| `s5_tuning` | tuning | how much of the gap is knobs, not architecture? | current champion's panel score | `modes_cap = 12` wall (F22), loss ≠ scored metric (F19), model-selection metric mismatch (F20), normalization; runs from t = 0, no dependencies |

Pilot budget: ~3–4 batches/stream ≈ 15–20 experiments. Streams may be added (e.g. an anchorless discovery stream) in a later round; the pilot validates the port first.

**Per-stream conventions (program.md §12)** will record for each stream: its anchor definition, its falsification-threshold convention (must exceed batch-0 noise floor), the pre-falsified levers it may not re-propose, and the quantified-headroom facts of §3.4 it should build on.

## 7. The eval layer (new, outside all guarded surfaces)

`mffp_autoresearch/round1/eval/` — the round's single source of scoring truth. The guarded `factory_mffp/eval/`, `baselines/`, `references/`, `scripts/`, `factory.md` are **never edited**.

- `score_panel.py` — runs one family × the panel via the family's contract CLI (`smoke_eval.py --dataset_dir --dataset_name --epochs --out --ckpt_dir --seed`, unchanged from `eval/MODEL_CONTRACT.md`), computes the single-definition nRMSE and skill ratios, writes a per-run JSON consumed by cards.
- `copylf_baselines.json` — copy-LF nRMSE per panel dataset, computed once from `benchmark_42/` data with the same nRMSE code path.
- **Seeding:** full determinism per seed — python/numpy/torch and CUDA (`torch.use_deterministic_algorithms`, seeded generators, `CUBLAS_WORKSPACE_CONFIG`) — fixing F13; the batch-0 noise floor measures what irreducible spread remains.
- **Caching** keyed by `(family, dataset, epochs, seed, hash)` where the hash covers the family dir **and** `models/_common/` **and** the eval layer itself (fixing F06), **and** the recorded env knobs from the card's `recipe` (fixing the invisible-sweep-knob collision from `MODELS_TO_TRY.md` §5).
- **Tiering:** contract smoke (2 epochs, plumbing only) → panel smoke (200 epochs, seed 0 — the 1 of 1+2) → replication (seeds 1, 2 at 200 epochs) → full protocol (2500 epochs, champions only, human-approved). Epoch budgets fixed per tier in `project.yaml`.
- **Assertions, not defaults** at every seam (§5.3).

## 8. Seed and verdict protocol

1+2 staging, universal: seed 0 first; seeds 1–2 launch unless seed 0 *cratered* (crash, or a skill ratio worse than 1.5× the stream anchor's, or the falsification clause already fired decisively). Verdict against the card's pre-registered `expected_falsification`, judged on the 3-seed mean ± CI; a falsified prediction is recorded as falsified — no retcon, no editorial skip of replication (protocol overrides analyzer editorial, a live-log lesson from round 5).

## 9. Immutables (program.md §5 for this round)

1. **Data is read-only.** `benchmark_42/**` untouched; no regeneration, no extra HF samples, N_hf per dataset fixed. LF is always the real coarse solve (repo law — never downsampled HF).
2. **The panel and guard set are fixed for the round** (§3.2, §3.3).
3. **The eval layer is byte-untouched during the round**; the loop may not edit it, `project.yaml`, `program.md`, ADRs, or subagent prompts — write `state/blocked.md` instead.
4. **One nRMSE definition** (§2); training loss is free, the scored metric is not.
5. **Contract CLI fixed**; env knobs allowed only if recorded in the card `recipe` (and therefore hashed).
6. **Seeds {0,1,2} and per-tier epoch budgets fixed.**
7. **Guarded factory surfaces never edited** (`factory_mffp/eval|baselines|references|scripts`, `factory.md`, `data/` wiring).
8. **New model code implements its mechanism from scratch from the source paper** with `INSPIRATION.md` citations (factory convention, kept); building *on* existing zoo families (extending, composing, refining them) is allowed and encouraged — the from-scratch rule bars copying `references/v9_baseline/`, not reuse of the zoo.

## 10. Prerequisites and launch validation (all before crons start)

- **G1** — eval-layer smoke: one existing family end-to-end through `score_panel.py` at contract tier; assertions fire on a deliberately mismatched config.
- **G2** — copy-LF baselines computed and sanity-checked against `dataset_characterization.csv` values.
- **G3** — batch 0: anchor certification + noise floor on the panel, 3 seeds (§5, improvement 4).
- **G4** — one hand-driven dry-run card end-to-end (starter → builder → reviewer → SLURM train/eval → analyzers) on a cheap config before autonomy.
- SLURM: Caltech HPC `gpu` partition, typed gres (P100 confirmed working via `run_contract_smoke.sbatch`; prefer faster gres when available), walltimes from measured timings, checkpoint-resume mandatory (partition can preempt).

## 11. Out of scope

- The kkanbu oracle (paper's own ablation: structure alone prevents drift; no MFFP taste profile exists). The scaffold leaves the four consult points identifiable so an oracle can be added in a later round.
- Meta-optimization of the loop (L2 rejected in `META_AUTORESEARCH.md` §7). The cheap items (L0b prior-art-gate benchmark) may run as diagnostic cards inside s-streams if a batch proposes them.
- Editing the mentor's `akash/` workstream or the factory engine; full-benchmark promotion of winners (human step, post-round).
- Dataset generation or repairs (e.g. the era5/pm_test downsampled-target issue F04 — noted for the mentor, not touched; era5/pm_test are excluded from the panel partly for this reason).

## 12. Risks, stated

- **N_hf = 5 on `ifc_poisson`** makes success criterion 1 statistically fragile; the CI convention and the noise floor are the mitigation, and per-dataset claims there stay labelled anecdote-grade.
- **The beyond-copy failure may be a data property** (e.g. LF/HF misalignment specific to those generators) rather than a modeling failure — that is exactly what s2's opening diagnostic is for; if it finds a data defect, the honest output is a dataset bug report, not a model.
- **P100-class compute** makes 2500-epoch tiers slow; the tiering keeps the loop's inner iterations at 200 epochs, and full protocol is champions-only.
- **Agent-definition collision:** installing the MFFP roster replaces the quadruped set in `~/.claude/agents/`. Acceptable (that round is complete); the round-5b originals remain in `playground_test` under version control.
