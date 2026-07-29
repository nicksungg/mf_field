# MFFP Autoresearch Round 1 — Program

> Universal guideline for every agent in Round 1. This document answers: what
> we are trying to do, how the problem is measured, what is allowed to change,
> and who does what. Ported from the quadruped Round-5b program (see ADR 0001);
> the spec behind it is `docs/superpowers/specs/2026-07-28-mffp-autoresearch-design.md`.

---

## 1. Goal

Find **genuine experiments** that improve understanding of **why multi-fidelity
fusion fails on the critical datasets**, and in doing so produce model families
that close those gaps. A better panel score is the *test* of that
understanding, not the goal.

An experiment is *genuine* if, whether it succeeds or fails, we learn something
about why fusion succeeds or fails on these PDE families. An experiment is
**not** genuine if it is local-optimum tuning that tells us nothing beyond X%
more on one dataset.

Round 1 success criteria (spec §1):

1. `ifc_poisson` at or below the published paper bar (0.036 nRMSE; stretch:
   IFC-GPODE 0.018).
2. At least one model with **skill < 1** (beats copy-LF) on each of the five
   beyond-copy panel datasets — at round start, **zero** models achieve this on
   any of them.

Round 1 establishes its own anchors via batch 0 (noise-floor certification);
no leaderboard numbers from the factory era are reportable claims here, though
they inform priors (§12, §13).

---

## 2. Score system

### 2.1 The one nRMSE definition

Per-sample relative L2 on the raw HF test field, averaged over test samples:

```
nRMSE = mean_i ||pred_i − hf_i||₂ / ||hf_i||₂
```

Implemented ONCE in `mffp_autoresearch/round1/eval/nrmse.py`. Every score in
the round flows through that file; result JSONs carry `nrmse_def_hash` and the
eval layer refuses to compare across different hashes. No agent recomputes
metrics by hand.

### 2.2 Copy-LF skill

Per dataset:

```
skill = nRMSE(model) / nRMSE(reference)
```

where the reference is the **copy-LF baseline** (the highest LF fidelity field
bilinearly interpolated onto the HF grid — the error you get by outputting the
model's own input), precomputed in `eval/copylf_baselines.json`. Skill < 1
means the model added value over the LF field it was handed.

**Exception (ADR 0002):** `ifc_poisson`'s test split ships only the HF
fidelity, so its reference is the published **paper bar 0.036**
(`reference_type: paper_bar`). Skill < 1 there means "beats the paper" —
exactly success criterion 1.

### 2.3 The panel score

**Panel geomean skill** = geometric mean of skill over the 6 panel datasets.
Reported per family/experiment as mean ± stratified percentile-bootstrap 95%
CI over seeds {0, 1, 2} (`eval/nrmse.py::bootstrap_ci`). Per-dataset skill
tables are mandatory in every card part 5 — the geomean never appears without
them.

| panel dataset | reference (test) | ref type | pre-round best zoo nRMSE → skill |
|---|---|---|---|
| `ext__helmholtz_2d` | 0.3295 | copylf | 0.478 → **1.45** |
| `sharp__phase_field_crystal_2d` | 0.0448 | copylf | 0.349 → **7.8** |
| `sharp__allen_cahn_2d` | 0.0162 | copylf | 0.245 → **15.1** |
| `sharp__fisher_kpp_2d` | 0.0626 | copylf | 0.247 → **3.9** |
| `sharp__cahn_hilliard` | 0.0877 | copylf | 0.180 → **2.1** |
| `ifc_poisson` | 0.0360 | paper_bar | 0.042 → **1.17** |

(Pre-round skills are computed from the akash 2500-epoch bench and are
**provisional priors only** — batch 0 certifies real anchors at the round's
own tier and seeds. N_hf = 5 on `ifc_poisson`: every per-dataset claim there
carries that caveat.)

**Guard set** (`heat_local`, `fluid`, `sharp__sod_1d`): not part of the
objective. Run at contract tier for any experiment claiming a panel win; a
guard regression > 2× vs its recorded reference flags the card in part 5 (the
analyzer interprets; no auto-reject).

### 2.4 Tiers

| tier | epochs | when |
|---|---|---|
| contract | 2 | plumbing check before any SLURM submit |
| smoke | 200 | ALL in-round experiments (seed 0 only — ADR 0004) |
| full | 2500 | champions only, post-round, human-approved |

---

## 3. What we're starting from

A 45-family model zoo exists (`factory_root/models/` + `akash/models/`), fully
benchmarked at 2500 epochs. The top of that leaderboard (`mf_fno_transfer_film`
et al.) is strong on smooth datasets and **loses to copy-LF on every panel
dataset** (§2.3). The factory CEO loop that built the zoo is retired for this
round (ADR 0001). Its guarded surfaces are read-only inputs (§5).

---

## 4. Structure

### 4.1 The 5-stream layout (no phases)

Round 1 has **5 streams**, all running **in parallel from t=0**, no phases, no
cross-stream barrier. ~3–4 batches per stream planned (≈ 15–20 experiments).

| Stream | Class | Question it owns |
|---|---|---|
| `s1_poisson` | gap | why is `ifc_poisson` above the paper bar, and what closes it? |
| `s2_beyond_copy` | gap | why does every fusion mechanism lose to copy-LF on the five sharp-2D panel datasets? |
| `s3_testtime` | lever | how far does test-time refinement go when the governing residual is real? |
| `s4_hybrid_routing` | lever | can MF compositions of hybrid operators capture the +30.6% FNO↔Transolver oracle? |
| `s5_tuning` | tuning | how much of the gap is knobs, not architecture? |

Streams own research **questions**, not model families: each batch proposes
whatever model, mechanism, or **diagnostic** serves the question.

### 4.2 Batches

One batch = one experiment = one card = one worktree = one branch = one SLURM
chain. Card id `{stream}-B{N}`. Batch N+1 starts when batch N is terminal
(`complete` or `skipped`); no stream waits on another. **3 consecutive skips
⇒ stream abandoned** (maintainer writes `state/streams/{stream}.json`).

### 4.3 Card types

- `model` — trains something; single-seed in-round protocol (§4.4, ADR 0004).
- `diagnostic` — a **measurement**, no training: single run, no seeds 2–3, its
  `expected_falsification` clause states what the measurement will show and
  what result would falsify the motivating hypothesis. Diagnostics are
  first-class experiments (cheap diagnostics beat expensive search —
  `docs/planning/META_AUTORESEARCH.md`). `s2_beyond_copy` batch 1 is a
  diagnostic by design (§12.2).

### 4.4 Seed protocol (single-seed in-round; top-3 confirmation at end — ADR 0004)

**Amended 2026-07-29 by operator direction (Eloise): strict 1-seed.**
Original 1+2 protocol preserved in ADR 0004 for the record.

1. **Seed 0 (the only in-round seed)**: builder writes parameterized scripts
   (still parameterized by seed — confirmation reuses them); code-reviewer
   gates; orchestrator submits seed 0 only. Seeds 1–2 are NOT launched
   in-round regardless of outcome.
2. Every in-round numeric result is recorded as **provisional
   (single-seed)**: initial-analyzer reports the seed-0 point estimate with
   no CI, and every claim of an effect must carry the label
   `provisional-single-seed` in card part 5. Batch-N+1 designs conditioning
   on such results must treat any effect smaller than the certified
   `min_claimable_effect` (batch-0 3-seed floor, `state/noise_floor.json`)
   as noise-compatible.
3. **End-of-round confirmation**: the top 3 models on the provisional
   leaderboard run seeds 1–2 at smoke tier (reusing `submit_seeds_2_3.sh`);
   only then are mean ± CI claims made. Full-tier (2500-epoch) champion runs
   remain 3-seed and human-approved.
4. The **cratered** definition (crash / geomean worse than 1.5× anchor /
   falsification fired) is retained as a seed-0 verdict category.

Diagnostics are unaffected (they measure, not train; single run as before).

### 4.5 Anchors

- Batch 0 (already run at launch, gate G3) certifies per-stream anchors
  through the round's own eval layer at smoke tier:
  `state/anchors/{stream}.json` — `{stream, anchor_type, datasets, value,
  per_seed, source: "batch0", provisional: false}`.
  - `s1_poisson`: best certified skill on `ifc_poisson`.
  - `s2_beyond_copy`: skill 1.0 (copy-LF itself is the bar).
  - `s3_testtime`, `s4_hybrid_routing`, `s5_tuning`: the certified champion's
    panel geomean skill.
- `state/noise_floor.json` records per-dataset seed spread from batch 0.
  **Every falsification threshold must exceed the noise floor for its
  dataset(s).** A claimed effect smaller than the floor is unfalsifiable and
  the brainstormer's immutables self-check rejects it.
- Anchors live in exactly ONE place (`state/anchors/`); dashboards render from
  it, never recompute. A `provisional: true` anchor is not a numeric
  threshold — judge against the falsification clause instead.

### 4.6 Skip rule

Debugger classifies every failure **ALGO** (the experiment's own code/config)
or **INFRA** (cluster misbehavior). **5 ALGO attempts** on a slot ⇒
`status: skipped`, `reopen_candidate: true`. INFRA attempts don't count.
**3 consecutive code-reviewer FAILs** ⇒ skip (separate counter). A skipped
batch is terminal; the next batch's brainstormer decides retry-under-eased-
conditions vs drop.

---

## 5. Fair-comparison rules (IMMUTABLES)

### What CAN be changed (freely, unless the card narrows it)

- Model architecture, fusion mechanism, training procedure, loss (training
  loss is free; the SCORED metric is not), conditioning representation,
  normalization, test-time refinement, hyperparameters.
- Building **on** existing zoo families — extending, composing, refining them
  — is allowed and encouraged. New mechanisms are implemented from scratch
  from the source paper with citations in the family's `INSPIRATION.md`
  (the bar is against copying `references/v9_baseline/`, not against reuse of
  the zoo).
- New analysis tools (promoted via the mechanism-analyzer's register turn).

### What CANNOT be changed (the 8 immutables)

1. **Data is read-only.** `benchmark_42/**` and `factory_root/data/**`
   untouched; no regeneration, no extra HF samples; N_hf per dataset fixed;
   LF is always the real coarse solve (never downsampled HF — repo law).
2. **The panel and guard set are fixed** for the round (§2.3).
3. **The eval layer is byte-untouched during the round.** No agent edits
   `round1/eval/`, `project.yaml`, `program.md`, ADRs, or subagent prompts.
   Blocked? Write `state/blocked.md` and auto-skip (it is a log, not a queue).
4. **One nRMSE definition** (§2.1).
5. **Contract CLI fixed**: families expose the factory `smoke_eval.py`
   signature; env knobs allowed ONLY if recorded in the card `recipe` (they
   enter the cache key).
6. **Seeds {0,1,2} and per-tier epoch budgets fixed** (§2.4).
7. **Guarded factory surfaces never edited**:
   `factory_root/{eval,baselines,references,scripts,data}/`, `factory.md`,
   `mf_field/akash/**`.
8. **Checkpoint-resume mandatory**: training resumes from `<ckpt_dir>/last.pt`
   (the SLURM partition can preempt).

### Pre-falsified levers (do NOT re-propose as-is)

- **WNO backbone swap** (`wno_transfer_film`): worse on sharp than its FNO
  control; wins 1/40 datasets.
- **LF low-mode freezing** (`mf_fno_spectral`): worst on sharp, catastrophic
  on lid-cavity.
- **Diffusion prior for point accuracy** (`mf_fno_diffprior`): gm ≈ 0.95.

A card may attack the *mechanism behind* a falsified lever with a new
composition, but must cite the falsification and say what is different.

---

## 6. Who is who

| Agent | Role | Card writes |
|---|---|---|
| `orchestrator` | THE session driving the loop; dispatches all agents; submits SLURM; owns `state/` | none |
| `websearcher` | ≤5 iterations of literature search per (stream, batch); final iteration = the **prior-art verdict** | none |
| `brainstormer` | packs context, designs ONE slot proposal (incl. `recipe`, falsification clause, prior-art citation) | none |
| `experiment-starter` | transcribes proposal verbatim into the card; creates worktree/branch | parts 1–4 + `expected_falsification`, `prior_art`, `recipe`, `card_type` (then LOCKED) |
| `experiment-builder` | implements in the worktree; SLURM scripts; contract-tier smoke; one atomic commit | mechanics fields, `build_notes[]` |
| `code-reviewer` | independent gate build → submit: PASS / SUGGEST / FAIL | `review_notes[]` |
| `experiment-debugger` | one fix per invocation; ALGO/INFRA classification; relaunch | `debug_notes[]` |
| `experiment-initial-analyzer` | parses eval JSONs (never recomputes); seed-0 verdict; 3-seed mean ± CI; anchors | part 5 |
| `experiment-mechanism-analyzer` | 3 probe turns + register turn; tool promotion to `tools/` | parts 6–7 |
| `maintainer` | cron-driven, read-only for cards: dashboard `index.md`, `state/maintainer_report.md`, timing ledger, abandonment detection | none |
| `advisor-consult` | ad-hoc grounded opinion (no oracle in round 1) | none |

Agent definitions: `mffp_autoresearch/round1/subagents/` (source of truth),
installed to `~/.claude/agents/` by `install_agents.sh`. Every agent starts
with `_shared/universal_context.md`.

---

## 7. No separate oracle

Round 1 runs without a taste oracle (ADR 0001): direction-setting decisions
are made by the deciding agent itself, grounded in THIS document (§1 goal,
§2 metric, §5 immutables, §12 conventions) per
`_shared/decision_discipline.md`. The four hand-offs where an oracle would sit
(websearch term choice, slot design, probe choice, tool promotion) are marked
in the agent prompts for a future round.

---

## 8. Prerequisites (all green before stream launch)

| Gate | What | Verified |
|---|---|---|
| G1 | eval-layer smoke: real family end-to-end at contract tier + assertion drill | `state/gates.md` |
| G2 | copy-LF baselines computed, divergences investigated & noted | `eval/copylf_baselines.json` |
| G3 | batch 0: anchors certified + per-dataset noise floor, 3 seeds | `state/anchors/`, `state/noise_floor.json` |
| G4 | one hand-driven card end-to-end (s5_tuning-B1) | `state/gates.md` |

---

## 9. Training and evaluation commands (reference)

Everything runs through the round's eval layer — one command per
(family, datasets, epochs, seed):

```bash
source <repo>/.venv/bin/activate
python <repo>/mffp_autoresearch/round1/eval/score_panel.py \
    --family_dir <worktree>/models_r1/<family> \
    --datasets panel            # or guard, or a comma-list \
    --epochs 200 --seed 0 \
    --out <outputs_root>/<stream>/B<N>/eval/result_panel_s0.json \
    [--env KEY=VAL ...]         # every knob here MUST be in the card recipe
```

- `--datasets panel|guard` expand from `project.yaml`.
- Caching is automatic (code + env + dataset + epochs + seed); `--no_cache`
  forces.
- The family dir must satisfy the factory contract:
  `manifest.json`, `smoke_eval.py` (six args above), results JSON with
  `model`, `dataset`, `splits.test.nRMSE`; resume from `<ckpt_dir>/last.pt`.
- SLURM: builders write `scripts/{01_train_eval.sh,submit.sh,submit_seeds_2_3.sh}`
  from `resource/logistics/example_scripts/`; the ORCHESTRATOR submits, never
  the builder. Partition/gres from `project.yaml sbatch:`; `--time` from
  `state/timing_ledger.json` (default 04:00:00 until measured).

---

## 10. Where things live

```
mffp_autoresearch/round1/            # the spec surface (loop may not edit: §5.3)
  project.yaml  program.md  subagents/  eval/  docs/adr/
  experiment_cards/{stream}/batch_{N}/B{N}.json
  websearches/{stream}/batch_{N}/    brainstormer/{stream}/batch_{N}/
  worktrees/{stream}/B{N}/           # git worktree, branch round1/exp-{stream}-B{N}
  tools/                             # promoted diagnostics + index.md
  state/                             # orchestrator + maintainer state
mffp_autoresearch_outputs/round1/{stream}/B{N}/{training,eval,slurm}/  # git-ignored
```

Worktrees fork from branch `round1-substrate`. Model code for an experiment
lives in the worktree at `models_r1/<family>/`; promotion into
`factory_root/models/` is a HUMAN post-round step.

## 11. Logistics hard constraints (summary)

- Caltech HPC; partition `gpu`, typed gres `gpu:p100:1` (project.yaml).
- Job names `r1-{stream}-B{N}-s{seed}`; logs under `<outputs_root>/<stream>/B{N}/slurm/`.
- Agents that run python are dispatched with bypassPermissions;
  `description="{stream}-B{N}"` is the transcript archive key.
- The orchestrator re-reads `state/` on every cron wake; crons pulse, they do
  not drive logic.
- Full rules: `resource/logistics/slurm_rules.md`.

---

## 12. Per-stream conventions

Common to all streams: quote these anchors verbatim when designing; thresholds
must clear `state/noise_floor.json`; cite the websearcher's prior-art verdict;
every proposal carries a complete `recipe` block.

### 12.1 `s1_poisson` (gap)

- **Bar**: paper 0.036 (IFC-ODE2); stretch IFC-GPODE 0.018. Current best zoo:
  0.042 (`mf_fno_pinn_transfer`, factory bench). Anchor: `state/anchors/s1_poisson.json`.
- **N_hf = 5.** Every claim is anecdote-grade by sample count; the CI + noise
  floor conventions are the only defensible reporting. Prefer designs that
  reduce variance (ensembling across seeds, all-pairs training) or add
  information (physics residuals) over designs that add capacity.
- Batch-1 seed direction: **all-pairs fidelity training** applied to the gap —
  `mf_field/akash/models/mf_fno_allpairs` was the mentor's best on the hard
  subset (gm 0.0094 vs FiLM 0.0121, FINDINGS.md); its known failure is
  O(L²) pair cost on many-level datasets (era5 timeout) — irrelevant here
  (ifc ladder L=4).
- Physics fact: Poisson is elliptic with global coupling; the IFC papers'
  ODE/GPODE methods exploit the fidelity-ladder structure directly.

### 12.2 `s2_beyond_copy` (gap)

- **Anchor: skill 1.0 = copy-LF.** The five datasets and their copy-LF test
  nRMSE: helmholtz_2d 0.3295, phase_field_crystal_2d 0.0448, allen_cahn_2d
  0.0162, fisher_kpp_2d 0.0626, cahn_hilliard 0.0877. Best zoo skills range
  1.45–15.1 (§2.3) — every model DESTROYS LF information it was handed.
- **Batch 1 is a diagnostic card** (pre-directed by the spec): localize where
  and how models lose to copy-LF — per-frequency-band error vs copy-LF,
  spatial error maps vs interface distance, error vs LF-HF residual magnitude.
  Falsification framing: "the failure is concentrated in X" is falsified if
  the error excess is spatially/spectrally uniform.
- Candidate mechanisms for later batches (from the two literature reports):
  additive-residual misalignment (the residual `HF−LF` is interface-hugging
  and models blur it), rel-L2 blur preference, normalization destroying
  amplitude structure, `modes_cap = 12` spectral wall on 96²–128² grids.
- **Warning**: if the diagnostic finds LF/HF misalignment that looks like a
  data defect, the honest output is a dataset bug report to the mentor, not a
  model (spec §12).

### 12.3 `s3_testtime` (lever)

- **Anchor**: champion's certified panel geomean (batch 0).
- Quantified priors — **CORRECTED, see ADR 0003** (the earlier −21% claim was
  a FINDINGS.md misread; refuted in-repo by the batch-1 websearch):
  `mf_fno_ptr`'s refinement is a registry NO-OP outside ifc_heat/ifc_poisson;
  where it ran (`ifc_poisson`) it bought −1.5%, inside the CI, at 163×
  inference latency. The lever has never been shown to help — this stream's
  batch 1 is closer to a first real test than a scale-up.
- A true governing residual is computable for only **one** panel dataset:
  `ext__helmholtz_2d` (steady; `x = [k, source_x, source_y]` fully determines
  `f`; `Δu + k²u = f` exact). The phase-field snapshots lack ∂ₜu; ifc_poisson's
  source decode is not shipped. Cards must scope accordingly (Helmholtz-exact
  refinement, or equilibrium/free-energy projection for the phase-field sets).
- Known threat (fetched, arXiv:2606.27354): residual minimization can be an
  unreliable proxy for reconstruction accuracy in ill-conditioned systems —
  Helmholtz is the canonical indefinite case; designs should include a
  residual-vs-error check so a null is informative.
- Second lever: IRNO-style frozen-base iterative refinement
  (`docs/reports/MF_Leaderboard_Beaters_2026_Report.md` proposal N1,
  arXiv:2605.24041, ~50× high-frequency band-error reduction claimed) — unbuilt.
- Test-time changes must still respect the contract CLI (refinement runs
  inside `smoke_eval.py`) and report wall-clock in build notes.

### 12.4 `s4_hybrid_routing` (lever)

- **Anchor**: champion's certified panel geomean (batch 0).
- Quantified prior: the FNO↔Transolver **pairwise oracle is +30.6%** over FNO
  alone (Transolver wins 16/38 despite being 2× worse on average).
  `mf_field/akash/models/fno_transolver_seq` (sequential FNO→Transolver
  residual hybrid) is BUILT but unbenchmarked — batch 1 should start by
  scoring it on the panel (cheap, mostly evaluation).
- The surviving novelty is the **MF composition** (routing, per-band/per-region
  gating, which fidelity feeds which expert) — the base hybrids themselves are
  published (WLNO, Park 2507.06133, SINO; see §5 pre-falsified list and the
  prior-art reports).
- Transolver-side caveat: `transolver_residual` is best-in-zoo on 4 of the 5
  beyond-copy datasets — whatever routing is learned should preserve its
  behavior there.

### 12.5 `s5_tuning` (tuning)

- **Anchor**: champion's certified panel geomean (batch 0); later batches
  re-target the current champion card.
- Audited knob findings to grind (from `docs/proposals/MODEL_TWEAKS*.md`):
  **F22** `modes_cap = 12` never scales with resolution (12 of 128 modes at
  256² — candidate M1 in MODELS_TO_TRY.md proposes 32); **F19** training loss
  ≠ scored metric in 11 families; **F20** model-selection metric mismatch;
  normalization choices.
- Constraint: no new losses-as-mechanisms, no new paradigms, no architectural
  changes — knobs on existing recipes only. Anything else belongs in another
  stream.
- G4's dry-run card (`s5_tuning-B1`, modes_cap 12→32 on the champion) is a
  REAL batch-1 card for this stream.

---

## 13. Project overview

### 13.1 The task

Multi-Fidelity Field Prediction: predict a high-fidelity PDE solution field
from cheap low-fidelity (coarse-grid) fields + a small condition vector, with
few HF samples. LF is always a real coarse solve, interpolated onto the HF
grid so residuals are well-defined. Fields are 2-D `(H, W)` (ifc_raw layout)
or flat `(n_cells,)` (npz_l* layout); `round1/eval/panel_data.py` handles both
(plus 1-D signals).

### 13.2 The landscape

45 model families, all benchmarked: FNO-transfer variants on top
(`mf_fno_transfer_film` Elo 1820), then FIRE-uncertainty families, Transolver
hybrids, U-Nets. 22 of 30 factory families are FNO-backboned; the top-10 are
variants of one idea — the zoo is deep but narrow, which is why streams own
questions, not families.

**Corrections that reframe old intuitions** (from Eloise, 2026-07-28):
`convnext_unet_film` is a ConvNeXt-**U-Net** (rank 2 overall, craters only on
`sod_1d`), NOT a CNN-FNO hybrid; the FNO→CNN two-stage hybrid
(`docs/reports/MF_FNO_CNN_Hybrid_Report.md`) was never built; iFNO was never
built. `sharp__sod_1d` (the shock tube) is already solved by
`fno_fire_distcond` (0.0001) — the open problem is sharp-**2D** fusion, not
shock representability.

### 13.3 Prior-art discipline

The project's novelty track record is **0-for-4** (every architecturally
sound candidate was already published: WLNO, Kim 2021, Bhola/MFFM/CorrDiff,
Park/SINO). Hence the mandatory retrieval-grounded prior-art verdict (§6
websearcher) — recall is not citation; only fetched sources count.

### 13.4 People

Eloise runs this round. The mentor owns `mf_field/akash/` and the guarded
factory surfaces; anything requiring changes there (dataset bug reports,
`score.py` fixes, full-benchmark promotion) is a written recommendation, not
an action.
