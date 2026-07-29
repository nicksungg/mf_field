# Iteration 1 — `s3_testtime`, batch 1

## Design context considered

- `summary_so_far.md` §6 (unknowns) — in particular the four design-time probe results.
- **Prior-art verdict**, D1 row: *"preempted-but-MF-composition-open (cite)"*; D2/D3
  *preempted*; D4 *novel*. Websearcher's instruction 3: *"The strongest batch-1 card is D1,
  narrowly scoped"* with two non-negotiables — mask the source/stencil-singular pixels, and
  state falsification **against copy-LF**, not against the base model.
- **§12.3 verbatim** (quoted in `summary_so_far.md` §2) + **ADR 0003**.
- **Anchor** `state/anchors/s3_testtime.json`: panel geomean 6.703, CI [6.219, 7.102].
- **Noise floor** `state/noise_floor.json` → `ext__helmholtz_2d`: mean_skill 13.817,
  per_seed_skill [18.826, 9.131, 13.495], `min_claimable_effect` / spread **9.695**.
  Panel-geomean seed spread = 7.102 − 6.219 = 0.883.
- **Immutables block (§4.5) verbatim** — reproduced in the self-check below.
- **Pre-falsified levers (§5)**: WNO backbone swap, LF low-mode freezing (`mf_fno_spectral`),
  diffusion prior for point accuracy (`mf_fno_diffprior`).
- Reference points on `ext__helmholtz_2d`: copy-LF test nRMSE **0.3295** (skill 1.000);
  the **zero field** has rel-L2 exactly 1.0 per sample → skill **3.035**. The certified
  champion (13.817) is therefore **4.6× worse than predicting nothing**.

## Proposal reasoning

### Alternatives weighed

**A1 — D1 as the websearcher framed it: model card, anchored field-space descent on the
exact Helmholtz residual, panel × 3 seeds.** Rejected on three independent grounds, each
established by a read-only design-time probe (§6 of the summary):

1. *Vacuity.* `Δ_h + k²I` with Dirichlet-0 on this uniform grid is **exactly diagonalised by
   the 2-D DST-I** (verified 4.3e-14), and `idst(dst(f)/Λ)` reproduces the shipped HF test
   fields to **2.2e-13**. Unbounded residual minimisation is a two-FFT re-solve that needs no
   model at all. A "win" from it would be a linear solver reported as model accuracy, and —
   worse — it would enter `state/anchors/` as the champion panel geomean that **s4 and s5
   both re-target**. Poisoning two other streams' anchor with a solver-in-disguise is the
   single worst outcome available in this batch.
2. *Collapse.* The bounded/1-dof version does not merely fail, it **destroys**: α* =
   ⟨Au,f⟩/‖Au‖² is 0.003 on copy-LF (0.3295 → 0.9964) and 1e-4 on truth+10% noise
   (0.10 → 0.9999), because ‖A·‖² weights modes by λ² across six decades and is therefore a
   roughness meter, not an error meter. Applied to the three certified champion checkpoints
   it sends every seed to rel-L2 1.0000 (skill 3.035). This is the fetched ENS hazard
   (arXiv:2606.27354) instantiated in our own data.
3. *Nothing to refine.* The **oracle** 1-dof rescale — an upper bound on any scalar
   correction — only reaches skill 2.55/2.73/2.81, so the champion's Helmholtz output is
   nearly orthogonal to the truth (cos 0.37–0.54). Refinement cannot rescue a base that
   carries no direction.

   Cost of A1 for that expected null: 3 seeds × 6 panel datasets ≈ 7.7 GPU-hours
   (`state/timing_ledger.json`).

**A2 — D2 (IRNO/MFFM-style frozen-base learned corrector).** Rejected: the verdict is
**preempted (cite)** on three fetched sources, and the websearch report states outright
*"Do not propose D2's plain form … this would be 0-for-5"* (program.md §13.3, 0-for-4 record).

**A3 — D3 (Krylov / warm-start).** Rejected: verdict **preempted (cite)** (NOWS,
super-fidelity, FCG-NO), the report says *"Not recommended for batch 1"*, and on this dataset
the "Krylov solve" is a single DST — i.e. A3 collapses into A1's vacuity case.

**A4 — D4 (free-energy projection on the phase-field panel) as the batch-1 model card.**
Rejected *as the primary card*, kept as a secondary measurement. It is the only `novel`
verdict, but its premise — that a free-energy functional is a usable error proxy on a
mid-trajectory snapshot — is **unverified**, and the same ENS hazard applies more strongly
(the report: *"a free energy is a weaker accuracy proxy than a true residual … amplified"*).
Building a model on an unverified proxy is exactly the mistake A1 would make. Instead the
batch-1 diagnostic **pre-tests the D4 premise** for a few extra CPU-minutes, so batch 2 either
starts on solid ground or is dropped without spending a card.

**A5 — anchor the refinement to the copy-LF input instead of the base prediction** (the
verdict's genuinely open "MF composition" seam). Attractive on paper — copy-LF is 13.8×
better than the champion — but the α* probe shows copy-LF is *rougher* than the model output
in the A-weighted norm and is destroyed even faster (0.3295 → 0.9964). Any *well*-metrized
version of it is again the DST solve. Kept as one measured arm of the diagnostic (the
initialisation sweep) rather than as a model card.

### Why a diagnostic, and why this one

Everything above says the same thing: on the only panel dataset where the s3 lever is
definable, exact-residual test-time refinement is **structurally degenerate** — every road
leads either to a model-independent re-solve or to annihilation of the prediction. That is a
stream-level go/no-go, it is worth establishing rigorously, and it costs ~10 GPU-minutes if
done as a measurement over the **already-certified frozen batch-0 checkpoints** instead of as
a training run. `program.md` §4.3 makes diagnostics first-class ("cheap diagnostics beat
expensive search"); §12.3 asks for a *"residual-vs-error check so a null is informative"*;
`docs/planning/META_AUTORESEARCH.md` is cited for the same principle. This is that card.

Two design choices make it more than a confirmation of my probes:

- The probes covered 3 configurations (α*, oracle α, exact solve) on 100 test samples. The
  card measures the **whole ladder**: K-step masked-residual descent for
  K ∈ {0,10,50,200,1000} from base / copy-LF / zero initialisation, with and without the
  PIC-Flow source-pixel mask, plus the per-|λ|-bucket error anatomy and wall-clock for every
  arm. The **budgeted, initialisation-dependent** regime is genuinely unmeasured and is the
  only place where a non-vacuous positive could hide — which is exactly what the
  falsification clause is pointed at.
- It carries the **D4 feasibility probe** so the stream's next decision is data-driven.

### Honesty disclosure

I ran three read-only design-time probes before choosing (scripts in the session scratchpad;
they touched only `benchmark_42/ext/helmholtz_2d`, `mf_field_extension_data/solvers.py`, and
`eval/results/mf_fno_transfer_film/**/last.pt`, all read-mode). They are the evidence for
rejecting A1 and for the expected outcome below, and the card's motivation must say so. No
data was written, regenerated or modified; no card, worktree or SLURM action was taken.

## Proposal

- **Category**: `residual-lever-feasibility-diagnostic`
- **Card type**: `diagnostic`
- **Motivation**: The prior-art verdict for D1 reads
  *"preempted-but-MF-composition-open (cite)"*, whose open seam is *"**field-space** vs
  weight-space optimization; doing it **from an MF prediction at N_hf = 5**; and scoring
  against **copy-LF** rather than against the base model — nobody in this literature uses that
  bar"*, under the fetched **standing threat** that *"residual minimization 'can be an
  unreliable proxy for reconstruction accuracy in ill-conditioned systems'"* (ENS,
  arXiv:2606.27354). §12.3 (post-ADR-0003) says the lever *"has never been shown to help here —
  this stream's batch 1 is closer to a first real test than a scale-up."* Before spending
  7.7 GPU-hours building the MF composition, measure whether the exact residual can carry any
  non-solver information about an MF prediction at all on `ext__helmholtz_2d` — the one panel
  dataset where a true governing residual exists.
- **Concrete config**: new family `models_r1/hh_residual_anatomy`, `epochs 0`, **no
  training**. It rebuilds the certified champion from the three frozen batch-0 checkpoints
  (`FNO2d(cond_dim=3, hidden=64, n_blocks=4, modes=(12,12), grid=(96,96))`,
  `scaler_hf = max|Y_hf_train|` recomputed exactly as `mf_fno_transfer_film/smoke_eval.py`
  does) and measures, on the 100 HF test samples:
  - **M0 (build gate)** `‖A u_hf − f‖/‖f‖` for all 100 shipped HF fields with
    `A = Δ_h + k²I`, `h = 1/97`, Dirichlet-0, `f = exp(-((x−sx)²+(y−sy)²)/(2·0.04²))`
    (transcribed from `mf_field_extension_data/solvers.py`); assert ≤ 1e-9. Assert the DST-I
    identity `idst(Λ·dst(u)) == A u` to ≤ 1e-10. Assert the reconstructed base rel-L2 matches
    the batch-0 record [6.202266, 3.008260, 4.445797] to 1e-3 relative — else HARD-STOP.
  - **M1 (vacuity)** rel-L2 and per-sample wall-clock of the exact DST solve
    `idst(dst(f)/Λ)`, vs the network forward pass.
  - **M2 (1-dof ladder)** α* = ⟨Au,f⟩/‖Au‖² and α_oracle, their correlation, and the
    resulting rel-L2/skill for base(×3 seeds) / copy-LF / zero / 12-mode-low-passed truth.
  - **M3 (budgeted descent)** K ∈ {0,10,50,200,1000} Adam steps on
    `‖M⊙(Au − f)‖²`, from base / copy-LF / zero init, with `M` = all-ones and with the
    PIC-Flow source/stencil mask (pixels within 3σ = 0.12 of `(sx,sy)` excluded); rel-L2,
    residual, initialisation-divergence `‖u_base-init − u_zero-init‖/‖u_zero-init‖`, wall-clock.
  - **M4 (anatomy)** DST-bucketed error energy (base vs copy-LF) by |λ| decile;
    per-sample cos(pred, truth) vs distance-to-resonance min|λ|; the 408× ‖u‖ spread against
    the champion's single global scaler 7.383.
  - **M5 (seed stability)** every M2/M3 headline recomputed for seeds 0,1,2.
  - **M6 (D4 pre-test, secondary)** on `sharp__allen_cahn_2d`, `sharp__cahn_hilliard`,
    `sharp__phase_field_crystal_2d`: discrete free energy `F[u]` from each set's `meta.json`
    parameters, evaluated on truth / copy-LF / champion prediction / truth+noise; report
    Spearman(|F[pred] − F[truth]|, rel-L2). If non-monotone, D4's premise is dead.

  The contract-scored prediction is the **M2 base 1-dof residual projection** (the primary
  mechanism); every other measurement goes in the result JSON's `extra` block. Wall-clock per
  arm is reported per §12.3.
- **Recipe**:
  ```json
  {
    "base_family": "mf_fno_transfer_film",
    "base_commit": "967562e2a4e3493515edab36b0fcb23655fce71f",
    "family_dir": "models_r1/hh_residual_anatomy",
    "datasets": "ext__helmholtz_2d",
    "epochs": 0,
    "seeds": [0],
    "env": {
      "HHDIAG_BASE_CKPT_DIR": "mffp_autoresearch/round1/eval/results/mf_fno_transfer_film",
      "HHDIAG_BASE_SEEDS": "0,1,2",
      "HHDIAG_GD_STEPS": "0,10,50,200,1000",
      "HHDIAG_GD_LR": "1e-3",
      "HHDIAG_SRC_MASK_SIGMA": "3.0",
      "HHDIAG_ENERGY_PROBE": "sharp__allen_cahn_2d,sharp__cahn_hilliard,sharp__phase_field_crystal_2d"
    }
  }
  ```
- **Expected outcome**: the hypothesis **holds**. `ext__helmholtz_2d` skill moves
  13.817 → **3.035 ± 0.000** under the scored 1-dof residual projection (all three seeds land
  on the zero field; the 9.695 seed spread collapses to ~0 *by annihilation*, not by
  stabilisation) — a 10.78-skill-unit "improvement" that clears the 9.695 floor but is
  **degenerate**, which the zero-predictor bar in the falsification clause is designed to
  expose. The exact DST solve lands at rel-L2 ~1e-13 with **zero** initialisation dependence
  and a per-sample wall-clock below the network's forward pass. The budgeted arms (M3) are the
  genuinely open part: I expect them to interpolate monotonically between "still the base" and
  "collapsing toward zero", with copy-LF-init never beaten by base-init. Panel-geomean framing:
  a *non-degenerate* configuration reaching skill 3.035 would move the anchor
  6.703 → 6.703·(3.035/13.817)^(1/6) = **5.21**, a 1.50 drop against a panel-geomean seed
  spread of 0.883 — so the bar is meaningful at panel level too. M6 is a coin-flip and either
  answer decides batch 2.
- **Expected falsification**: *Falsified if some exact-residual test-time configuration whose
  output is initialisation-dependent (base-init vs zero-init outputs differing by ≥ 10%
  relative L2, i.e. demonstrably not a re-solve) reduces the certified champion's
  `ext__helmholtz_2d` mean skill from 13.817 to below **3.035** — the trivial zero-field
  predictor — an improvement of > 10.78 skill units that exceeds the batch-0 noise floor of
  9.695 (`state/noise_floor.json`).*
- **Anchor reference**: `null` (s3 is a lever stream; §4.5 — own-stream anchor implicit, and
  this is a single-dataset diagnostic, not a panel claim).

## Immutables self-check (§4.5) — positive evidence for each

1. **Data read-only.** The family opens `benchmark_42`/`factory_root/data` only through the
   factory's `load_mf_dataset` adapter in read mode and never writes to a dataset path; the
   residual's `f` is *recomputed analytically from the shipped condition vector* `x`, not
   regenerated data; `N_hf` is untouched (Helmholtz ships 400 train / 100 test at both
   fidelities, unchanged); LF is read as the shipped `train_l1/test_l1` coarse solve and is
   only ever bilinearly *upsampled* for the copy-LF arm — never used as downsampled HF.
2. **Panel + guard set fixed.** `datasets: "ext__helmholtz_2d"` is a member of
   `project.yaml panel`; the M6 probe reads three further *panel* datasets read-only and adds
   nothing to and removes nothing from either list; the guard set is not touched (no panel-win
   claim is made, so §2.3's guard requirement is not triggered).
3. **Eval layer / spec untouched.** The proposal runs through the stock
   `eval/score_panel.py` CLI with `--family_dir/--datasets/--epochs/--seed/--env` only; the
   only contact with `round1/eval/` is `open(..., 'rb')` on three existing `last.pt` files
   under `eval/results/`, and it edits no file in `round1/eval/`, `project.yaml`,
   `program.md`, ADRs or subagent prompts.
4. **One nRMSE definition.** The family writes `splits.test_hf.rel_l2_per_sample` via the
   factory's `finalize_and_write` and lets `score_panel.py::_extract_test_metric` +
   `nrmse.py` compute the scored number; the diagnostic's own α/energy statistics are stored
   under `extra` and are never presented as the scored metric.
5. **Contract CLI fixed.** `smoke_eval.py` keeps exactly
   `--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed`; all six knobs
   (`HHDIAG_*`) are environment variables listed verbatim in the `recipe.env` block above, so
   they enter `code_hash()`'s env digest and the cache key.
6. **Seeds and tier epochs fixed.** `seeds: [0]` with `epochs: 0` is the §4.3 diagnostic
   protocol (SCHEMA.md: *"`recipe.epochs = 0` is legal"*); no training budget is consumed, and
   the three base checkpoints it reads were themselves produced at the fixed smoke tier
   (200 epochs, seeds 0/1/2) by batch 0.
7. **Guarded factory surfaces untouched.** The only factory read is a **verbatim copy** of
   `mf_field/factory_mffp/models/mf_fno_transfer_film/model.py` into the worktree at
   `models_r1/hh_residual_anatomy/base_film/model.py` (with provenance in `INSPIRATION.md`);
   `models/**` is the explicitly modifiable surface and is only *read*, while
   `factory_root/{eval,baselines,references,scripts,data}/`, `factory.md` and `akash/` are
   neither read-for-modification nor written.
8. **Checkpoint-resume implementable.** With no training there is still a resume path:
   `smoke_eval.py` writes `<ckpt_dir>/last.pt` holding
   `{"epochs_target": 0, "grid": [96,96], "measurements": {...}}` after M0–M6 and, on start,
   re-emits the result JSON from that file when it exists and `epochs_target` matches —
   so a preemption mid-M3 costs at most one re-run of a ≤10-minute job.
9. **Falsification threshold vs noise floor.** `state/noise_floor.json ext__helmholtz_2d`:
   `mean_skill 13.817`, `min_claimable_effect`/`spread` **9.695**, per-seed skill
   [18.826, 9.131, 13.495]. The clause demands a drop from 13.817 to **below 3.035**, i.e.
   **> 10.78 skill units > 9.695**. The zero-predictor bar (3.035 = 1.0/0.3295) is used
   instead of a raw delta precisely so the threshold cannot be met degenerately. No other
   dataset carries a numeric claim: M6 reports a rank correlation on three datasets as a
   qualitative go/no-go for batch 2, explicitly not a skill claim.
10. **Not a pre-falsified lever.** Nearest is **LF low-mode freezing** (`mf_fno_spectral`,
    "worst on sharp, catastrophic on lid-cavity") — also a spectral intervention. The
    difference: `mf_fno_spectral` *freezes LF content in low modes during training* as a
    modelling prior; this card *measures, at test time with no training*, how an exactly known
    operator's eigen-decomposition weights an error that already exists, and proposes no
    spectral constraint on any model. WNO backbone swap and diffusion-prior are unrelated
    (no backbone change, no generative prior).

## Status

- Slot **covered** — one proposal, `card_type: diagnostic`.
- Skipped: no.
- Reopen candidates resolved: none existed (no prior cards in any stream).
- Immutables self-check: **pass (10/10)**, first pass, no revision required.
