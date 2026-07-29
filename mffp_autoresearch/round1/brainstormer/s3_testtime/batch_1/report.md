# Brainstormer Report — Stream `s3_testtime`, Batch 1

**Stream**: s3_testtime · **Batch**: 1 · **Total iterations**: 1 · **Slot filled**: 1/1 ·
**Reopen candidates resolved**: 0 (none existed)

## Slot

- **Category**: `residual-lever-feasibility-diagnostic`
- **Card type**: `diagnostic`
- **Motivation**: The websearcher's D1 row reads
  **"preempted-but-MF-composition-open (cite)"**, and the open seam it names is
  *"**field-space** vs weight-space optimization; doing it **from an MF prediction at
  N_hf = 5**; and scoring against **copy-LF** rather than against the base model — nobody in
  this literature uses that bar"*, under the fetched **standing threat** that residual
  minimization *"can be an unreliable proxy for reconstruction accuracy in ill-conditioned
  systems"* (ENS, arXiv:2606.27354). program.md §12.3 (post-ADR-0003) adds that the lever
  *"has never been shown to help here — this stream's batch 1 is closer to a first real test
  than a scale-up."* Rather than spend ~7.7 GPU-hours (3 seeds × 6 panel datasets,
  `state/timing_ledger.json`) building the MF composition on an untested premise, this card
  measures — in ~10 GPU-minutes, with **no training** — whether the exact governing residual
  can carry any **non-solver** information about an MF prediction on `ext__helmholtz_2d`, the
  only panel dataset where a true governing residual exists at all (§12.3, 1 of 6).
- **Concrete config**: family `models_r1/hh_residual_anatomy`, `epochs 0`. It rebuilds the
  certified champion from the three frozen batch-0 checkpoints
  (`eval/results/mf_fno_transfer_film/ckpt_ext__helmholtz_2d_e200_s{0,1,2}/last.pt`;
  `FNO2d(cond_dim=3, hidden=64, n_blocks=4, modes=(12,12), grid=(96,96))`, `scaler_hf`
  recomputed exactly as the champion's `smoke_eval.py` does) and measures on the 100 HF test
  samples:
  **M0 build gate** — `‖A u_hf − f‖/‖f‖ ≤ 1e-9` with `A = Δ_h + k²I`, `h = 1/97`,
  Dirichlet-0, `f = exp(-((x−sx)²+(y−sy)²)/(2·0.04²))` transcribed from
  `mf_field_extension_data/solvers.py`; DST-I identity `idst(Λ·dst(u)) == Au` to 1e-10;
  reconstructed base rel-L2 matching the batch-0 record [6.202266, 3.008260, 4.445797] to
  1e-3 relative, else HARD-STOP.
  **M1 vacuity** — rel-L2 + wall-clock of the exact spectral solve `idst(dst(f)/Λ)` vs the
  network forward pass.
  **M2 1-dof ladder** — α* = ⟨Au,f⟩/‖Au‖² and α_oracle, their correlation and resulting
  skill, for base(×3 seeds) / copy-LF / zero / 12-mode-low-passed truth.
  **M3 budgeted descent** — K ∈ {0,10,50,200,1000} Adam steps on `‖M⊙(Au − f)‖²` from
  base / copy-LF / zero init, with `M` = ones and with the PIC-Flow source/stencil mask (3σ
  around `(sx,sy)`); rel-L2, residual, initialisation-divergence, wall-clock.
  **M4 anatomy** — DST-bucketed error energy (base vs copy-LF) by |λ| decile; per-sample
  cos(pred, truth) vs distance-to-resonance; the 408× ‖u‖ spread vs the champion's single
  global scaler 7.383.
  **M5** — M2/M3 headlines across seeds 0,1,2.
  **M6 (secondary, D4 pre-test)** — discrete free energy from `meta.json` parameters on
  `sharp__allen_cahn_2d`, `sharp__cahn_hilliard`, `sharp__phase_field_crystal_2d`, evaluated
  on truth / copy-LF / champion / truth+noise; Spearman(|ΔF|, rel-L2).
  The **contract-scored** prediction is the M2 base 1-dof residual projection; everything else
  lives in the result JSON's `extra` block. Wall-clock per arm is reported (§12.3).
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
- **Expected outcome**: the hypothesis **holds**. Scored metric: `ext__helmholtz_2d` skill
  13.817 → **3.035** (all three seeds land exactly on the zero field; the 9.695 seed spread
  collapses to ~0 **by annihilation**, not by stabilisation). That is a 10.78-skill-unit move,
  which clears the 9.695 noise floor yet is *degenerate* — the zero-predictor bar in the
  falsification clause exists to expose precisely that. The exact DST solve is expected at
  rel-L2 ~1e-13, **zero** initialisation dependence, and per-sample wall-clock below the
  network's forward pass — i.e. unbounded refinement here is a re-solve, not a model. The M3
  budgeted arms are the genuinely open part; expectation is monotone interpolation from
  "still the base" to "collapsed to zero", with copy-LF-init never beaten by base-init.
  Panel framing: a *non-degenerate* configuration reaching skill 3.035 would move the stream
  anchor 6.703 → 6.703·(3.035/13.817)^(1/6) = **5.21**, a 1.50 drop against a panel-geomean
  seed spread of 0.883, so the bar is meaningful at panel level too. M6 is a genuine coin-flip
  and either answer decides batch 2.
- **Expected falsification**: *Falsified if some exact-residual test-time configuration whose
  output is initialisation-dependent (base-init vs zero-init outputs differing by ≥ 10%
  relative L2, i.e. demonstrably not a re-solve) reduces the certified champion's
  `ext__helmholtz_2d` mean skill from 13.817 to below **3.035** — the trivial zero-field
  predictor — an improvement of > 10.78 skill units that exceeds the batch-0 noise floor of
  9.695 (`state/noise_floor.json`).*
- **Prior-art verdict quoted** (verbatim, `websearches/s3_testtime/batch_1/report.md`,
  D1 row):
  > **D1** — exact governing residual (`du + k^2u = f`, source located by `x`) descended on
  > the **output field** with an anchor, from a multi-fidelity prediction; `ext__helmholtz_2d`
  > is the only panel dataset where this is computable | **preempted-but-MF-composition-open
  > (cite)** *(with an honesty caveat: the preempting source could not be fetched)* |
  > ENS https://arxiv.org/abs/2606.27354 (fetched); PIC-Flow https://arxiv.org/abs/2605.06929
  > (search-returned; does NOT preempt — training-time); PE-PINN
  > https://arxiv.org/html/2603.02231 (fetched); PINO https://arxiv.org/pdf/2111.03794
  > (**search-summary only, 3 fetch attempts failed**) | Mechanism = PINO instance-wise
  > test-time optimization + anchor loss (presumed prior art). Open: **field-space** vs
  > weight-space optimization; doing it **from an MF prediction at N_hf = 5**; and scoring
  > against **copy-LF** rather than against the base model — nobody in this literature uses
  > that bar. **Standing threat (fetched)**: residual minimization "can be an unreliable proxy
  > for reconstruction accuracy in ill-conditioned systems"; Helmholtz is the canonical
  > indefinite operator with a singular point source. **Mandatory mitigation**: PIC-Flow-style
  > masking of the source/stencil-error pixels.

  Also quoted, D4 row (drives M6): **"novel"** *(by absence of evidence — weak)*.
- **Immutables self-check**: **pass (10/10)**, first pass, no revision. Full positive
  evidence per item in [iteration_1.md](iteration_1.md) §"Immutables self-check". Headline
  items: (3) the only contact with `round1/eval/` is `open(...,'rb')` on three existing
  `last.pt` files; (5) all six knobs are `HHDIAG_*` env vars listed in `recipe.env`, so they
  enter `code_hash()`; (8) `<ckpt_dir>/last.pt` stores the measurement digest and short-circuits
  a preempted re-run; (9) threshold 10.78 skill units **> 9.695** floor, with the zero-predictor
  bar closing the degenerate loophole; (10) nearest pre-falsified lever is `mf_fno_spectral`
  LF low-mode freezing — a *training-time* spectral prior, whereas this card imposes no
  spectral constraint on any model and only measures an existing error in the operator's own
  eigenbasis at test time.
- **Anchor reference**: `null` (s3 is a lever stream — §4.5: own-stream anchor implicit; this
  is a single-dataset diagnostic, not a panel claim).
- **Source iteration**: [iteration_1.md](iteration_1.md)

## Reopen candidates

| Candidate | Verdict (retry/drop) | Eased conditions | Source iteration |
|---|---|---|---|
| *(none — no prior cards exist in any stream; `experiment_cards/` holds only `SCHEMA.md`)* | n/a | n/a | [iteration_1.md](iteration_1.md) |

## Skipped slot

Not applicable — the slot is filled.

## Summary table

| Slot | Category | One-liner | Status |
|---|---|---|---|
| s3_testtime-B1 | residual-lever-feasibility-diagnostic | Zero-training diagnostic over the three frozen batch-0 champion checkpoints: is the exact Helmholtz residual a non-solver error signal for an MF prediction, or does it either re-solve the PDE or annihilate the field? Carries a free-energy pre-test that decides batch 2. | filled (`diagnostic`) |

## Notes handed forward (not part of the slot)

1. **Cross-stream finding for `s5_tuning` / `s2_beyond_copy`** (from the design-time probes
   recorded in `summary_so_far.md` §6): the champion's `smoke_eval.py` normalises with a
   **single global** `scaler_hf = max|Y_hf_train| = 7.383` while `ext__helmholtz_2d` per-sample
   ‖u‖ spans **408×** (0.070 → 28.46) because of near-resonance samples. The oracle 1-dof
   rescale of the champion's output only reaches skill 2.55–2.81, i.e. the prediction is close
   to orthogonal to the truth. Per-sample amplitude normalisation is a §12.5-legal knob
   ("normalization choices") and is *not* claimed by this card.
2. **Benchmark-integrity flag for the mentor**: `ext__helmholtz_2d`'s HF test fields are
   reproducible to **2.2e-13** from the condition vector alone by two FFTs
   (`idst(dst(f)/Λ)`, DST-I diagonalisation verified to 4.3e-14). Any method permitted to use
   the exact governing operator at test time can therefore score ~0 on this dataset without a
   model. This is a written recommendation only (§13.4), and it is the reason this card is a
   diagnostic rather than a model card — a solver-in-disguise champion would enter
   `state/anchors/` and poison the `s4_hybrid_routing` and `s5_tuning` anchors.
