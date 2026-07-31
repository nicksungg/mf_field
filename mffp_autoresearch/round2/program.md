# MFFP Autoresearch Round 2 — Program

> Universal guideline for every agent in Round 2. This document answers: what
> we are trying to do, how the problem is measured, what is allowed to change,
> and who does what. Round 2 inherits Round 1's pipeline, card format, agents,
> cron orchestration, and tools library unless this document says otherwise.
> Spec: `docs/superpowers/specs/2026-07-30-mffp-autoresearch-round2-design.md`
> (approved by Eloise 2026-07-30; launch authorized by Eloise 2026-07-31).
> Round-1 program: `../round1/program.md`; round-1 results:
> `../round1/docs/round1_report.md` (authoritative).

---

## 1. Goal

Round 1 predicted HF fields from LF (coarse-solve) fields plus a condition
vector. Round 2 removes the solver at test time: **how well can models predict
the HF field from the condition vector alone, and how much does LF data —
available only during training — help?** This matches the deployment reality
where a company hands over historical simulation data but no callable solver,
and (where a solver exists) condition→HF inference skips the solve entirely.

An experiment is *genuine* if, whether it succeeds or fails, we learn
something about why condition→HF prediction succeeds or fails on these PDE
families, or about the value of LF as a training signal. Local-optimum tuning
that tells us nothing beyond X% on one dataset is not genuine.

Round 2 success criteria (operator-amendable):

1. **A certified value-of-LF measurement**: a matched with/without-LF-training
   contrast (same architecture, same budget) with a claimable effect on at
   least 3 panel datasets (r2s4's question — answerable whatever the absolute
   skill level turns out to be).
2. **At least one model with skill < 1** (beats running the LF solver and
   copying its output, under the CORRECTED denominators) on at least one
   panel dataset, while beating the best training-free floor on the panel
   geomean (§2.3 — at round start the best floor geomean is 23.06; every
   trained model must at minimum beat that).

Numbers from round 1 are NOT comparable to round-2 numbers on the corrected
datasets (§2.2). Any side-by-side must state both denominators.

---

## 2. Score system

### 2.1 The one nRMSE definition

Per-sample relative L2 on the raw HF test field, averaged over test samples:

```
nRMSE = mean_i ||pred_i − hf_i||₂ / ||hf_i||₂
```

Implemented ONCE in `mffp_autoresearch/round2/eval/nrmse.py` (byte-identical
to round 1's). Every score flows through that file; result JSONs carry
`nrmse_def_hash` AND `copylf_def_hash` (new in round 2: the reference
construction is hashed separately — a round-1 gap) and the eval layer refuses
to compare across different hashes.

### 2.2 Copy-LF skill under CORRECTED references (ADR r2-0001)

```
skill = nRMSE(model) / nRMSE(copy-LF)
```

The copy-LF denominator is computed **offline** from stored test LF fields
that round-2 models never see, under the per-dataset grid conventions fixed
between rounds (round-1 report §5: the round-1 construction carried a
(r−1)/2 half-cell registration defect plus a wrap-seam defect, inflating
denominators 2.0–9.1×):

- nested periodic pseudo-spectral datasets → node-aligned bilinear with
  periodic wrap (HF pixel k samples LF index k/r);
- `ext__helmholtz_2d` → Dirichlet interior-node map;
- guards / 1-D → round-1 convention (certified consistent by the audit);
- `ifc_poisson` → published paper bar 0.036 (test ships no LF; r1 ADR 0002).

Reading: skill < 1 means the no-solver model beats actually running the LF
solver and copying its output — the headline deployment claim.

**Mandatory floor arms** (frozen in `state/anchors/floors.json`, spec §3):
every model card's part 5 reports, next to the model, the pre-computed
**NN-in-condition** floor (nearest train condition → copy that train HF
field), the **train-mean** floor, and the **zero** floor (nRMSE ≡ 1.0 —
round 1's helmholtz champion lost to it). A model that does not beat the best
floor on a dataset has learned nothing there, whatever its skill.

### 2.3 The panel and its frozen references

Panel geomean skill = geometric mean of skill over the 6 panel datasets;
per-dataset skill tables are mandatory in every part 5.

| panel dataset | corrected ref (test nRMSE) | r1 frozen ref | best floor skill (arm) |
|---|---|---|---|
| `ext__helmholtz_2d` | 0.299033 | 0.329450 | 3.344 (zero) |
| `sharp__phase_field_crystal_2d` | 0.007381 | 0.044780 | 59.81 (mean) |
| `sharp__allen_cahn_2d` | 0.001781 | 0.016152 | 269.20 (NN) |
| `sharp__fisher_kpp_2d` | 0.021450 | 0.062632 | 11.99 (mean) |
| `sharp__cahn_hilliard` | 0.041803 | 0.087660 | 23.18 (NN) |
| `ifc_poisson` | 0.036 (paper bar) | 0.036 | 10.05 (NN) |

Best-floor panel geomean = **23.06** — the all-stream launch anchor
(`state/anchors/{stream}.json`). The table says the regime is HARD: with no
LF at test, even the best training-free predictor is 10–270× worse than
copying a real coarse solve. Standing caveats: helmholtz's best floor is the
zero field (report-only discipline continues); pfc has essentially no
fidelity gap under a band-limited reference (denominator caveat in
`eval/copylf_baselines.json _notes.pfc`) — pfc claims carry it.

**Guard set** (`heat_local`, `fluid`, `sharp__sod_1d`): not part of the
objective; run at contract tier for any experiment claiming a panel win; a
guard regression > 2× vs its recorded reference flags the card. Note: on
`fluid` and `sod_1d` the NN floor already beats copy-LF (0.21 / 0.24) — LF
adds little there; a guard "win" below those floors is floor-level, not
model-level.

### 2.4 Tiers

| tier | epochs | when |
|---|---|---|
| contract | 2 | plumbing check before any SLURM submit |
| smoke | 200 | ALL in-round experiments (seed 0 only; r1 ADR 0004) |
| full | 2500 | champions only, post-round, human-approved |

---

## 3. What we're starting from

Round 1 closed 2026-07-31 with both criteria met (report §1): best claimable
panel geomean skill 0.1233 (`dc_cleaned`, s4-B3 — BC-matched spectral
cleaning + local corrector; the routing machinery contributed exactly zero),
best ifc_poisson skill 0.6087 (s1-B3 `self_only__none`). Those numbers are
under the OLD inflated denominators — they are **priors, not bars**, for
round 2. Field-input round-1 models (correctors, residual/coreg fusers)
cannot run here: the stripped view leaves them nothing to read (gates.md
G1-r2). BUT transfer-style factory families are already condition→field at
test — `mf_fno_transfer_film` (zoo champion) reads only the condition
vector and runs fine; its round-1 panel numbers were condition→HF numbers
all along, and it lost to copy-LF on every panel dataset. It is the
canonical declared baseline for r2s3 (§12.3), and the reviewer's rebadge
check (§5.10) is the novelty enforcement for any runnable family.

Round-1 findings that directly seed round-2 design (see §12): the BC-match
rule, the routing-license rule, the lineage-bound caveat, the unified
normalization eligibility rule, the drift-class rule, the two-gate loss rule,
revin_lf's two-scaler finding, and the **nested-ladder degeneracy** (with
aligned/nested ladders, all-pairs MF training degenerates to top-rung
replication — novel remark, r1 report §6).

---

## 4. Structure

### 4.1 The stream layout (no phases)

4 streams, all running **in parallel from t=0**, no cross-stream barrier;
~3 batches per stream at roughly half of round 1's compute (spec §6).

| Stream | Class | Question it owns |
|---|---|---|
| `r2s1_direct` | gap | how well can condition→HF architectures built from scratch do with no LF at test? |
| `r2s2_stacked` | lever | does condition→pseudo-LF→(frozen round-1 corrector) beat direct condition→HF, and how much is lost to pseudo-LF distribution shift? |
| `r2s3_lf_train_signal` | lever | how much does LF, available only during training, help a condition→HF model? |
| `r2s4_diag` | diag | value-of-LF accounting, overfitting anatomy at N_hf = 5, floor certification |

### 4.2 Batches, card types, seed protocol, skip rule

All inherited from round 1 verbatim (r1 program §4.2–§4.6): one batch = one
card = one worktree = one branch = one SLURM chain; card id `{stream}-B{N}`;
`model` vs `diagnostic` cards; **strict 1-seed in-round** (seed 0 point
estimates labeled `provisional-single-seed`; top-3 get seeds 1–2 at round
end); cratered = crash / geomean worse than 1.5× anchor / falsification
fired; 5 ALGO attempts ⇒ skip; 3 consecutive reviewer FAILs ⇒ skip; 3
consecutive skips ⇒ stream abandoned. Worktrees fork from branch
`round2-substrate`; model code lives at `models_r2/<family>/`; branches are
`round2/exp-{stream}-B{N}`.

### 4.3 Anchors and the noise floor

- `state/anchors/{stream}.json`: the certified launch anchor for every stream
  is the **best-floor panel geomean 23.06** (`anchor_type:
  best_floor_panel_geomean`, source: training-free floors — no batch-0
  training round was needed; the floors are deterministic).
- `state/anchors/floors.json`: the per-dataset floor panel (frozen 2026-07-31,
  before any experiment ran — spec §3).
- `state/noise_floor.json` is **provisional** (`_source:
  round1-batch0-rescaled`): round-1 batch-0 seed spreads under the corrected
  denominators, from LF-consuming families. Per r1 program §4.5, a
  provisional floor is not a numeric threshold — falsification clauses are
  judged directly until **r2s4-B1 certifies a condition→HF 3-seed spread**
  (§12.4, pre-directed), which replaces this file.

---

## 5. Fair-comparison rules (IMMUTABLES)

Round 1's 8 immutables hold verbatim (r1 program §5): data read-only; panel
and guard fixed; eval layer byte-untouched during the round (now
`round2/eval/`); one nRMSE definition; contract CLI fixed (env knobs only via
the card recipe); seeds and tier budgets fixed; guarded factory surfaces
never edited; checkpoint-resume from `<ckpt_dir>/last.pt` mandatory.

Round-2 additions (spec §4–§5):

9.  **Stripped test view.** Models are evaluated ONLY against
    `stripped_data_root` (test LF field files physically absent;
    `score_panel.py` points there and refuses views that leak LF). Family
    code or scripts reading the original `data_root` at test time = reviewer
    FAIL. Train-side LF use is free (that is the round's question).
10. **Novelty guarantee / declared-reuse-only.** Every round-2 family
    implements a new condition→field pathway (new `INSPIRATION.md`, new
    forward signature). A round-1 model may appear ONLY as (a) a **declared
    frozen test-time sub-component** behind a new condition→pseudo-LF front
    end (the r2s2 design, where the reuse IS the experiment), or (b) a
    **training-time-only teacher** (r2s3), never present at test. The
    reviewer answers "is this a rebadge of a round-1 family?" on every card.
11. **No new HF data, no LF-only pools** (Eloise's decision, spec §4): the
    round runs on the existing aligned train samples only (400 per sharp
    dataset; 5/20/50 ladder on ifc_poisson).
12. **Floor arms mandatory** on every model card (§2.2).
13. **Round-1 results, cards, and state are immutable** — read-only inputs.

Pre-falsified levers (r1 §5) still apply where relevant (WNO backbone swap,
LF low-mode freezing, diffusion prior for point accuracy), as does the
prior-art discipline: the project's novelty track record is 0-for-4;
retrieval-grounded prior-art verdicts are mandatory (recall is not citation).

---

## 6. Who is who

Identical to round 1 (r1 program §6): orchestrator (THE session; dispatches
agents, submits SLURM, owns `state/`), websearcher, brainstormer,
experiment-starter, experiment-builder, code-reviewer, experiment-debugger,
experiment-initial-analyzer, experiment-mechanism-analyzer, maintainer,
advisor-consult. Definitions: `mffp_autoresearch/round2/subagents/` (source
of truth), installed to `~/.claude/agents/` by `install_agents.sh` (this
OVERWRITES the round-1 registry set; round 1 is closed and its definitions
live in git). Every agent starts with `_shared/universal_context.md`.

## 7. No separate oracle

As in round 1 (ADR 0001): deciding agents ground direction-setting decisions
in THIS document per `_shared/decision_discipline.md`.

---

## 8. Prerequisites (gates — all green before stream launch)

| Gate | What | Verified |
|---|---|---|
| G1-r2 | eval-layer tests green (35, incl. registration-fix regressions) + stripped-view structural enforcement demonstrated (loader on stripped view exposes no test LF; an LF-consuming family cannot run) | `state/gates.md` |
| G2-r2 | corrected copy-LF baselines: seam checks vs r1 frozen values (unchanged datasets bit-identical; corrected datasets match the s3-B1 audit) | `eval/copylf_baselines.json` |
| G3-r2 | floors + stream anchors frozen BEFORE any experiment; provisional noise floor recorded with provenance | `state/anchors/`, `state/noise_floor.json` |

No G4 hand-driven card this round: the pipeline is inherited from round 1
where it ran 18 cards end-to-end (ADR r2-0002 records the deviation); in
compensation the orchestrator drives every stream's B1 with extra scrutiny
and r2s4-B1 is the certification card.

---

## 9. Training and evaluation commands (reference)

```bash
source <repo>/.venv/bin/activate
python <repo>/mffp_autoresearch/round2/eval/score_panel.py \
    --family_dir <worktree>/models_r2/<family> \
    --datasets panel            # or guard, or a comma-list \
    --epochs 200 --seed 0 \
    --out <outputs_root>/<stream>/B<N>/eval/result_panel_s0.json \
    [--env KEY=VAL ...]         # every knob here MUST be in the card recipe
```

`score_panel.py` hands the family the STRIPPED view automatically; the family
contract (`smoke_eval.py` six-arg CLI, result JSON schema, checkpoint resume)
is unchanged from the factory MODEL_CONTRACT. SLURM: builders write
`scripts/{01_train_eval.sh,submit.sh,submit_seeds_2_3.sh}` from
`resource/logistics/example_scripts/`; the ORCHESTRATOR submits, never the
builder. Partition/gres from `project.yaml sbatch:`; `--time` from
`state/timing_ledger.json` (default 02:00:00 until measured). Job names
`r2-{stream}-B{N}-s{seed}`.

## 10. Where things live

```
mffp_autoresearch/round2/            # the spec surface (loop may not edit: §5.3)
  project.yaml  program.md  subagents/  eval/  docs/adr/
  experiment_cards/{stream}/batch_{N}/B{N}.json
  websearches/{stream}/batch_{N}/    brainstormer/{stream}/batch_{N}/
  worktrees/{stream}/B{N}/           # git worktree, branch round2/exp-{stream}-B{N}
  stripped_data/                     # materialized stripped test views (git-ignored)
  tools/                             # seeded from round 1 (see tools/index.md header note)
  state/                             # orchestrator + maintainer state
mffp_autoresearch_outputs/round2/{stream}/B{N}/{training,eval,slurm}/  # git-ignored
```

## 11. Logistics hard constraints (summary)

As round 1 (r1 program §11): Caltech HPC, partition `gpu`, typed gres
`gpu:h100:1` (project.yaml; ADR 0005 carry-over), job names
`r2-{stream}-B{N}-s{seed}`, logs under `<outputs_root>/<stream>/B{N}/slurm/`,
bypassPermissions for python-running agents, crons pulse but do not drive
logic. Full rules: `resource/logistics/slurm_rules.md`.

---

## 12. Per-stream conventions

Common to all streams: quote the launch anchor (best-floor geomean 23.06) and
the per-dataset floor table verbatim when designing; thresholds must clear
the noise floor for the dataset(s) — while `state/noise_floor.json` is
provisional, judge falsification clauses directly (§4.3); cite the
websearcher's prior-art verdict; every proposal carries a complete `recipe`
block; floor arms mandatory on model cards (§2.2).

### 12.1 `r2s1_direct` (gap)

- **Bar**: the per-dataset floor table (§2.3). Beating NN-in-condition with
  400 train samples is necessary but nowhere near sufficient; the interesting
  question is how close a from-scratch condition→HF surrogate gets to
  skill 1.0 on each dataset.
- Design priors (spec §6): FiLM-conditioned FNO **decoders** (condition →
  spectral latent → field), DeepONet-style branch–trunk (branch on condition,
  trunk on coordinates), spectral/implicit decoders (SIREN/modulated INR
  class). Condition vectors are 2–19 dims (each sharp `meta.json` certifies
  the field is a learnable function of them); ifc_poisson's is 5-dim.
- **Helmholtz lesson** (r1 report §5): the zero field is the floor to beat
  there — any helmholtz claim must show the zero-floor column.
- **pfc caveat** (§2.3): denominator 0.007381 under variant C; no
  fidelity gap under band-limited. State it on every pfc claim.
- N_hf on ifc_poisson is 5 — every claim there is anecdote-grade; prefer
  variance-reducing designs (r1 s1 lesson: ensembling, physics residuals are
  out per ADR 0009 — physics-agnostic at test).
- Overfitting is THE central threat at these sample counts; r2s4's
  overfitting-anatomy diagnostics feed this stream. Train/val discipline in
  the recipe is mandatory (no test-split peeking; the round-1 D3 val_idx
  double-consumption caveat is the cautionary tale).

### 12.2 `r2s2_stacked` (lever)

- **B1 is pre-directed by the spec** (Eloise's stacking proposal): train a
  FiLM-FNO **pseudo-LF emulator** (condition → LF field) on the TRAIN LF
  data, feed the best round-1 corrector — the s6 DC lineage / s4-B3
  `dc_cleaned` stage (r1 geomean 0.1233–0.19 under OLD denominators; restate
  under corrected before claiming). Arms: **frozen corrector / fine-tuned
  corrector / end-to-end**, to separate emulator error from distribution
  shift (the corrector was trained on real LF; pseudo-LF is
  off-distribution for it).
- Declared-reuse rule (§5.10a): the corrector is a frozen test-time
  sub-component — the reuse IS the experiment. Its code lives in the round-1
  worktrees (`round1/worktrees/s6_local/B2`, `round1/worktrees/
  s4_hybrid_routing/B3/models_r1/s4_router/`); vendor the needed pieces into
  the round-2 family dir with provenance comments (round-1 branches are
  immutable).
- Round-1 mechanism rules apply to the cleaning stage: **BC-match rule**
  (eligibility decidable training-free; audit tool
  `tools/spectral_prestage_bc_audit.py`), the **wrap-seam caveat** (part of
  dc_cleaned's pfc credit was a boundary-rim artifact of the DEFECTIVE
  reference — under the corrected reference that credit may vanish; the
  s4-B3 H4 finding says deep-bulk ratio was 0.908 on pfc), and the
  **lineage-bound caveat** for any routing/eligibility rule.
- Failure is informative: if pseudo-LF → corrector loses to r2s1's direct
  models, the LF representation is not a useful bottleneck — that is the
  stream's falsification framing.

### 12.3 `r2s3_lf_train_signal` (lever)

- **Question**: LF as training-only signal. Candidate mechanisms (spec §6):
  distillation from an LF-consuming teacher (round-1 families in role §5.10b
  — teacher at train, absent at test), LF-pretrain → HF-finetune, auxiliary
  multi-fidelity losses (predict LF and HF jointly from condition).
- **The stream has a mandatory declared baseline**: `mf_fno_transfer_film`
  (factory zoo champion) IS LF-pretrain→HF-finetune from the condition
  vector (verified 2026-07-31: its test input is `cond_by_fid` only; it runs
  on the stripped view unmodified). Any r2s3 pretrain/finetune proposal must
  either score it as the baseline arm or cite how it differs — an
  undifferentiated re-proposal is a rebadge (reviewer FAIL, §5.10).
- **revin_lf two-scaler finding** (r1 s5): exact at LF-pretrain, 3.1% proxy
  at HF — normalization transfer across fidelities is a solved sub-problem;
  reuse it, don't rediscover it.
- **Nested-ladder degeneracy** (r1 report §6) directly constrains this
  stream: with aligned/nested ladders, "multi-fidelity" training pairs
  degenerate toward top-rung replication — LF-as-signal designs must state
  what information the LF rungs add that the HF rung does not already
  contain (spectral truncation structure, more samples at low rungs on
  ifc_poisson: 70 lower-fidelity vs 5 HF).
- The **unified normalization eligibility rule** (r1 s2, checks 0–6) governs
  any per-sample normalization proposal; spread is not the decider.
- Uses the existing 400 aligned samples only (§5.11).

### 12.4 `r2s4_diag` (diagnostics)

- **B1 is pre-directed**: floor + spread certification. (a) Verify the frozen
  floors reproduce (standing zero-predictor column included); (b) train ONE
  minimal condition→HF baseline (smallest reasonable FiLM-FNO decoder or
  MLP→field) at smoke tier, seeds {0,1,2}, on the panel — its per-dataset
  seed spread replaces the provisional `state/noise_floor.json` (§4.3).
  Diagnostic card, but WITH training (3 seeds) — the exception is the point;
  cheap by design (small model).
- Later batches: **value-of-LF accounting** — matched architecture ± LF
  training signal (coordinates with r2s3: r2s4 measures, r2s3 optimizes);
  **overfitting anatomy** at N_hf ∈ {5, 20, 50} (ifc ladder) and N=400
  (sharp): train/test gap decomposition, effective sample counts (the
  **drift-class rule**: when n_eff/N < 1%, only in-job paired controls are
  controls).
- The round-1 probe library is seeded in `tools/` (37 files; index header
  notes they were written against round-1 eval paths — adapt on use, promote
  adapted versions via the register turn).

---

## 13. Project overview

### 13.1 The task (round-2 regime)

Multi-Fidelity Field Prediction with **no LF at test**: predict a
high-fidelity PDE solution field from a small condition vector (2–19
scalars; complete by construction — each dataset's `meta.json` certifies the
field is a learnable function of it), with few HF samples and LF coarse-solve
fields available at training time only. Fields are 2-D `(H, W)` (ifc_raw) or
flat `(n_cells,)` (npz); `round2/eval/panel_data.py` handles both (offline
reference computation only — models get the stripped view).

### 13.2 The landscape

45 LF-consuming factory families + round 1's additions exist as PRIORS and
potential teachers/sub-components (§5.10) — none can run in this regime.
Corrections that survive from round 1 (r1 program §13.2): `convnext_unet_film`
is a ConvNeXt-U-Net (not a CNN-FNO hybrid); the mentor's FNO→CNN hybrid and
iFNO were trained off-repo with unknown-but-poor results — never cite in-repo
absence as evidence about them. `sharp__sod_1d` is solved in the LF-consuming
regime (0.0001); in THIS regime its NN floor (0.24 skill) is already below
copy-LF — the guard exists to catch harness breakage, not to be won.

### 13.3 Prior-art discipline

0-for-4 novelty track record; retrieval-grounded prior-art verdicts
mandatory. Round-2-specific: condition→field surrogates are a HEAVILY
published area (DeepONet, parametric FNO, PINO, neural operators for
parametric PDEs, INR-based surrogates like CORAL/DINO) — the novelty
question for r2s1 is never "a conditioned decoder" but the specific MF
training signal and few-HF regime. The websearcher must check the
multi-fidelity-distillation and pretrain-finetune literature for r2s3
(MF-DeepONet variants exist) and the "emulate-then-correct" literature for
r2s2.

### 13.4 People

Eloise runs this round; she approved the design 2026-07-30 and authorized
launch 2026-07-31. The mentor owns `mf_field/akash/` and the guarded factory
surfaces; dataset defects (registration note, pfc redesign, wrap-seam) are
WRITTEN RECOMMENDATIONS to the mentor (`../round1/docs/operator_notes/`), not
actions. The registration/wrap-seam fixes applied here live entirely in
`round2/eval/` — the generator package (`mffp_sharp/common/ladder.py`) still
carries the defect and fixing it is the mentor's call.
