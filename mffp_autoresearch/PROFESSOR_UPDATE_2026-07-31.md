# MFFP Autoresearch — Update for Mentor (Rounds 1–2)

Date: 2026-07-31. Author: Eloise (with the autoresearch orchestrator).
Authoritative sources: `round1/docs/round1_report.md`, `round2/program.md`,
per-experiment cards under `round{1,2}/experiment_cards/`.

Rendered versions of this update (figures embedded):
[Claude artifact](https://claude.ai/code/artifact/47cb0e44-05ae-4e0f-a6ec-ded0d4106cc3)
(private until shared from its share menu) ·
[`PROFESSOR_UPDATE_2026-07-31.html`](PROFESSOR_UPDATE_2026-07-31.html) (same page, in-repo).

## TL;DR

- **Round 1 is closed; both success criteria were met.** Best sharp-panel geomean
  skill **0.1233** (8.1× better than copying the LF field; −34.3% vs the prior best),
  best ifc_poisson skill **0.6087** vs the published paper bar. Seeds 1–2 confirmation
  runs for the top-3 slate are submitted and in the queue (jobs 66165252–57).
- **The round's most valuable output is arguably benchmark-integrity findings, not a
  model**: the LF→HF regridding carried a half-cell registration defect that inflates
  copy-LF denominators 2.0–8.6×, so most sharp-panel "wins" (ours and any prior)
  partly re-learn registration. Fixed in the round-2 eval layer.
- **Round 2 launched today** (condition-vector → HF; LF available at training only).
  Floors were re-certified pre-experiment; the first wave of all 4 streams is
  submitted, two experiments already have results, and the first mechanism analysis
  produced a round-defining finding: on these datasets the condition vector
  determines only **1–3 field degrees of freedom**, so direct decoders are
  information-limited, not representation-limited.
- Round-1 figures updated: `round1/docs/figures/error_comparison.png` and
  `top_models_overview.svg` now show the final leaderboard including the champion.

## 1. How the autoresearch system is set up

The system is a no-oracle research harness: a persistent orchestrator session
drives parallel research *streams*, each stream running batches of single-slot
experiments through a fixed pipeline of specialized subagents:

1. **websearcher** — retrieval-grounded prior-art verdict on candidate directions
   (max 5 search iterations, must end with a verdict: novel / preempted / open).
2. **brainstormer** — designs exactly one experiment for the slot, with a complete
   training recipe and a **pre-registered falsification clause** that must clear the
   certified noise floor (no post-hoc goalpost moves).
3. **experiment-starter** — creates a git worktree for the slot and transcribes the
   proposal verbatim into an append-only **experiment card** (hypothesis, design,
   expected result, falsification clause, recipe).
4. **experiment-builder** — implements the model family / measurement script in the
   worktree, smoke-tests it, commits atomically.
5. **code-reviewer** — adversarial pass (PASS / SUGGEST / FAIL) before any GPU time
   is spent; reviewers can never submit jobs themselves.
6. **Orchestrator submits to SLURM** (the only actor allowed to), then
   **experiment-debugger** handles failures (5 algorithmic-failure retries then
   auto-skip; infra failures don't count against the budget).
7. **initial-analyzer** — parses result JSONs only (never recomputes metrics),
   fills in per-dataset skill tables, applies validity gates.
8. **mechanism-analyzer** — 3 iterative probe turns (spectral band errors, residual
   structure, causal ablations…) answering *why*, then promotes generalizable
   probes into a shared `tools/` library for later experiments.

A **maintainer** agent on a cron keeps a dashboard (`index.md`) and timing ledger.
Guard rails baked into the program spec: the eval layer (one nRMSE definition,
hashed — results with mismatched hashes refuse to compare), frozen certified noise
floors and anchors, immutable card fields, report-only guard datasets, and a rule
that screens/reviews are non-reportable. Heavy runs are checkpoint-resumable
because the SLURM partition is preemptable.

**Round-1 scale**: 7 streams, 21 experiment cards (17 model, 4 diagnostic),
~55 SLURM jobs, 12 ADRs, ~20 reusable probe tools promoted — in ~3 days
(spec approved 07-28, round closed 07-31), with mentor gates at round
close (seed confirms and full runs fire only on explicit operator go).

## 2. Round 1 — results (condition + test-time LF → HF)

Final claimable leaderboard (seed 0, 200-epoch tier; 3-seed confirms in queue):

| Rank | Model | Skill (lower = better) | What it is |
|---|---|---|---|
| 1 | `dc_cleaned` (s4-B3) | **0.1233** panel geomean | BC-matched spectral cleaning stage, then a small local CNN corrector on the *cleaned* residual |
| 2 | s6-B2 DC lineage | 0.188–0.193 panel geomean | Richardson-style defect correction + out-of-fold trust gate |
| 3 | `self_only` (s1-B3) | **0.6087** on ifc_poisson | Fidelity-ladder FNO, few-shot (5 HF samples), vs published paper bar |

Headline mechanism results (each backed by a causal probe, not a hunch):

- **The round-best gain is the cleaning stage alone.** The router/trust-head
  machinery on top contributed exactly 0.000000: cleaning *nests* the correction
  library, so routing headroom collapses to zero. Two-sided causal proof that the
  cleaning stage's eligibility decider is **boundary-condition match** — decidable
  before training with a training-free audit tool.
- **Benchmark integrity** (the part most relevant to the benchmark paper):
  (a) the (r−1)/2 half-cell registration defect in LF→HF interpolation — closed
  form derived; ~96–100% of sharp-panel wins were re-learned registration;
  (b) a wrap-seam defect in the periodic reference construction;
  (c) on helmholtz the **zero field beats every trained model** (skill 3.0 vs
  certified floor 9.7) — the dataset is report-only until it gets a zero-floor
  column; (d) with aligned/nested fidelity ladders, all-pairs multi-fidelity
  training degenerates to top-rung replication (we could not find this reported
  anywhere).

Both updated figures live in `round1/docs/figures/` (regenerate the dot plot from
cards with `tools/render_error_comparison.py`).

## 3. Round 2 — launched today (condition vector → HF; no solver at test)

**Regime**: models see LF fields only during training; at test they get the
condition vector alone (the stripped data view physically omits test LF). This is
the deployment case where a company hands over historical simulation data but no
callable solver. Skill < 1 now means: *beats actually running the LF solver and
copying its output*, under **corrected** denominators (registration + wrap-seam
fixes landed in `round2/eval/` before any experiment ran; round-1 and round-2
skills are not comparable).

**Streams** (4): r2s1 direct condition→HF decoding; r2s2 stacked (FiLM-FNO
pseudo-LF feeding the frozen round-1 corrector); r2s3 LF as a training signal
(with the one round-1 family that already runs condition-only at test as the
declared baseline); r2s4 diagnostics — its first job was to replace the
provisional noise floor with a 3-seed certified one *before* any model claims.

**Status after day 1** (all four streams' batch-1 submitted; running on idle H200s
after the H100 queue was estimated at ~1 week):

- **r2s4**: floor certification complete (3 seeds). Certified minimum claimable
  effects are 10–1700× tighter than the provisional ones; the certified
  training-free floor panel geomean is **19.82** (anchor all models must beat).
- **r2s1** (seed 0): panel geomean **19.64** — beats the certified floor
  resolvably on 4 of 6 datasets, but one pre-registered falsification leg fired
  marginally (within seed noise; seeds 1–2 will decide). Mechanism turn 1 found
  the round-defining structure: per dataset only **1–3 orthogonal field modes are
  predictable from the condition vector at all** (out-of-fold R²>0.1), splitting
  the panel into "coefficient-unidentifiable" datasets (the missing information
  is 1–2 decades of error) and "basis-inadequate" ones. On allen_cahn the entire
  learnable map is one scalar — which a 16M-parameter decoder overfits to rediscover.
- **r2s2 / r2s3** (seed 0): in flight. r2s2's build disclosed a data finding worth
  mentor attention: the **ifc_poisson fidelity ladder is unpaired** (no shared
  condition vectors across rungs, min condition distance 0.08–0.30 on every rung;
  independently reproduced by two streams) — this invalidates paired-ladder
  semantics on that dataset and is a generator-side item
  (`mffp_sharp/common/ladder.py`, mentor-owned; we did not touch it).

## 4. How the harness itself is performing

- **Throughput**: an experiment goes idea → prior-art check → build → adversarial
  review → GPU run → analyzed card in roughly a day; round 2's first wave went
  from launch commit to two analyzed experiments in one day. Wall-clock estimates
  are tracked in a timing ledger (e.g., r2s1's run took 7 min vs a 4 h request —
  the ledger feeds better future requests).
- **What the design catches**: pre-registration + certified floors killed several
  would-be "wins" (claims inside noise are recorded as fired-but-unresolvable);
  the reviewer gate caught confounds before GPU time (e.g., r2s3's shared-scaler
  confound is now a card-level interpretation constraint); mechanism turns are
  producing causal, reusable findings rather than leaderboard deltas.
- **Known hazards, managed**: SLURM preemption (mandatory checkpoint-resume),
  session-restart replays (claim protocol: stage-file tags + pre-submit queue
  checks), GPU nondeterminism (~1.9e-4 rel envelope on H100 — bitwise gates are
  CPU-only by rule).

## 5. Gated next steps (in order, each on explicit go)

1. Round-1 top-3 seed confirms — **submitted, in queue** → re-issue leaderboard
   with 3-seed means.
2. Human-approved 2500-epoch full runs for round-1 survivors.
3. ifc_poisson ladder pairing fix (generator-side, mentor-owned).
4. Round-2 batch 2, informed by the batch-1 mechanism findings.
