# Brainstormer Report — Stream `s6_local`, Batch 1

**Stream**: `s6_local` (lever, ADR 0011) / **Batch**: 1 / **Total iterations**: 1 /
**Slot filled**: 1 (model card, 5 ADR-0007 variants in one card+recipe) /
**Reopen candidates resolved**: 0 (none exist — `experiment_cards/s6_local/` absent)

## Slot

- **Category**: `mf_composition / trust-gated LOCAL corrector on the real LF field`
- **Card type**: `model`

- **Motivation**:
  s2_beyond_copy-B1's M1 measured that the champion `mf_fno_transfer_film` is **LF-blind at
  inference** — `lf_at_inference = FALSE` on 5/5 datasets x 3/3 seeds,
  `n_field_shaped_inputs_at_eval = 0`, "the only tensor entering the network at eval is the
  `[16, cond_dim]` condition vector" (verified independently in
  `factory_mffp/models/mf_fno_transfer_film/model.py::FNO2d.forward`, which lifts the coordinate
  grid only). That makes the literal form of H2 untestable: a local operator needs a field, and
  the champion has none. The only field available at test time is the interpolated LF field, so
  the concrete s6 question is whether a **local operator acting on the real LF field** adds value
  that the champion's global spectral generator cannot. The websearcher's verdict licenses exactly
  this and only this: **D3 — "local corrector consuming the real interpolated LF field at test
  time, with an identity-to-copy-LF construction (zero-init gate => at init the model IS copy-LF)"
  — `preempted-but-MF-composition-open`**, open because "A no-harm floor **defined by a real
  coarse PDE solve** (= round success criterion 2, skill < 1), plus the champion's blind spot that
  it never sees LF at inference"; stream boundary respected — "`s2_beyond_copy`-B1 D2 already owns
  'identity-to-LF'; **s6 owns only 'the corrector is LOCAL'**". The scouting websearch reached the
  same class independently (C1, its rank-1 open composition) and sharpens the open surface to "a
  **field-valued per-pixel/per-band trust gate** over the interpolated LF field inside a neural
  operator, parameterized so the scored copy-LF reference is exactly recoverable and is the
  initialization". One variant additionally carries D2 — "**preempted-but-MF-composition-open** ...
  It also carries a *published opposing prediction* (F-Adapter says capacity belongs in LOW bands)
  — a genuine pre-registered falsification risk". **No mechanism novelty is claimed**: parallel
  local kernels in an FNO are peer-reviewed prior art (NO-LIDK ICML 2024; U-FNO; LOGLO-FNO), and
  learned coarse-grid correction is standard (Kochkov 2021). The mentor's FNO->CNN two-stage
  hybrid and iFNO **were trained off-repo with poor results reported ("not going well"); the code
  and numbers are unavailable**, so no claim here rests on their absence — instead this design
  differs from the plausible naive recipe on three stated axes: it **consumes the given LF field**
  instead of predicting it (deleting the documented exposure-bias failure,
  https://arxiv.org/pdf/2606.02661), it is **zero-init and gated so copy-LF is exactly
  recoverable**, and the local module is **capacity-constrained** (and, in variant 3, the *only*
  HF-trained parameter set). Fact correction carried into the card: `n_train_hf = 400` on all five
  beyond-copy datasets (s2-B1 part 5); **N_hf = 5 applies to `ifc_poisson` only**, so the
  literature's "free-form refiner overfits at N=5" argument binds with full force only on the
  ifc_poisson leg — which this card makes a no-op fallback.

- **Concrete config**:
  New family `models_r1/s6_local_lf_corrector`, one substrate, five env-selected variants.
  Prediction on any dataset whose **test** split ships an LF fidelity (all five beyond-copy
  datasets and all three guard datasets — verified on disk):
  ```
  LF_up = interp(field_by_fid[max(lf_fids)] -> 256-capped working grid)   # == copy-LF construction
  Delta = C_theta(LF_up, coords, FiLM(X))          # LOCAL: depthwise KxK ConvNeXt-lite stack
  y_hat = LF_up + G (*) Delta                      # G = trust gate, EXACTLY 0 at init
  ```
  - `C_theta`: depth 4, width 32, depthwise K=7 + pointwise, GroupNorm, per-block FiLM(X),
    **final 1x1 zero-init** => `Delta ≡ 0` at init. Receptive field ~25 cells.
  - `G`: zero at init in every variant; its scalar component is finally selected on a held-out
    slice of the HF train split by least-squares projection + line search **whose candidate set
    contains 0** (construction reused from the in-round sibling `fno_transolver_seq`; cited, not
    claimed as novel).
  - Target: `R = Y_hf - LF_up` on the HF train split.
  - `max(lf_fids)` is mandatory: `eval/panel_data.py::copylf_prediction` uses the HIGHEST LF
    fidelity, while the champion's `smoke_eval.py` pretrains on `min(lf_fids)`.
  - **Fallback**: `ifc_poisson`'s test split ships only `fidelity_64` (verified on disk), so there
    the family runs the champion path verbatim (LF-pretrain -> HF-finetune, X-only FiLM-FNO).
    Pre-registered **no-op leg**; no claim is made on ifc_poisson.
  - **Builder tripwires**: (i) LF tensor must come from an LF fidelity array whose native grid is
    strictly coarser than HF (never a downsampled HF field); (ii) no HF *test* field may enter the
    prediction path; (iii) the identity path's nRMSE must match `eval/copylf_baselines.json` up to
    the interpolation-kernel difference (`scipy.zoom order=1` vs `F.interpolate bilinear`), delta
    recorded in `build_notes`; (iv) attempt a re-fetch of the unresolved prior-art threat
    **AGMF-Net** (https://www.sciencedirect.com/science/article/abs/pii/S002980182502997X, HTTP 403
    for both websearchers) and record the outcome.

  **Ranked variants (ADR 0007)** — one card, one worktree, one SLURM chain:

  | rank | `S6_VARIANT` | recipe delta | rationale |
  |---|---|---|---|
  | 1 | `local_pixel_gate` | `g(x) = sigmoid(h(x) + b0)` with hard-zero offset so `g ≡ 0` at init | the scout's rank-1 open composition (field-valued trust gate); local corrector + local gate = maximal s6 ownership |
  | 2 | `local_scalar_gate` | one scalar gate, held-out selected | clean control for rank 1: does spatial trust structure beat one number? simplest, most robust |
  | 3 | `lf_frozen_adapter` | spectral encoder trained on **LF only**, then FROZEN; the **only** HF-trained params are the zero-init local adapter + gate | the D2 arm; tests F-Adapter's published opposing prediction (scarce capacity belongs in LOW bands) |
  | 4 | `local_band_gate` | 4 per-band scalar gates, edges `k_nyq * [0, 1/8, 1/4, 1/2, 1]` (s2-B1 convention), all init 0 | makes the low-band no-harm claim hard and per-band auditable |
  | 5 | `pointwise_ctrl` | `S6_KERNEL=1` (receptive field = 1 cell) | isolates locality-as-spatial-kernel from pure pointwise recalibration — H2's real content given s2-B1 M5a amplitude findings |

  **Screening plan**: ONE contract-tier job (`--epochs 2 --seed 0`), all five variants, on
  `--datasets panel` **and** `--datasets guard` (the card will claim a panel win, so §2.3 requires
  the guard set). Reserve 01:00:00 (s2-B1 precedent: 5 datasets, 46 s on H100).
  *Primary function of the screen is the **no-harm assertion**, not ranking*: every variant must
  score `skill <= 1.02` on each of the five beyond-copy datasets at 2 epochs; a violation means the
  identity construction is broken (ALGO). With a gate whose search set contains 0, all variants are
  expected to sit at ~1.000 and be indistinguishable on the scored metric at 2 epochs.
  **Discard rule**: drop only on (i) crash/NaN, (ii) no-harm violation, (iii) 5-dataset contract
  geomean > 2x the best variant's. Close calls are NOT discarded (ADR 0007).
  **Promotion rule (fixed before submit, no post-hoc switching)**: among survivors promote the
  highest mean held-out residual-explained fraction `rho = 1 - ||R - G*Delta||^2/||R||^2` over the
  five beyond-copy datasets, *provided* it beats the runner-up by > 0.05 absolute; otherwise
  promote by rank order 1->2->3->4->5. `rho` is a plumbing/gross-ordering signal recorded in
  `build_notes` only and is never quoted as evidence in parts 5-7 (ADR 0007 guardrail). If no
  variant survives, the card is ALGO-broken -> debugger.
  **Promoted run**: 200 epochs, seed 0, `--datasets panel`; reserve 06:00:00
  (`state/timing_ledger.json`: champion 200-epoch panel legs sum to ~186 min; the corrector stage
  adds to that).

  **Pre-registered gaming hazard (coordinator direction)**: with an identity-init gate,
  `skill <= 1.0` is reachable **at initialization**, so **raw skill is explicitly NOT this card's
  win condition**. The readout is the *trained gate's contribution*, written as sidecar
  diagnostics computed through `eval/nrmse.py` on the family's own predictions (no new scored
  metric; §2.1 untouched): `skill_id` (the `G ≡ 0` path — deterministic, zero seed variance),
  `contribution_d = skill_id - skill_trained`, the per-band contribution profile
  `||e_b(trained)||^2 / ||e_b(identity)||^2` on the s2-B1 band grid, and the gate statistics
  (selected scalar / mean and percentiles of `g(x)` / fraction of pixels with `g > 0.01`).
  **A gate that collapses to zero is a FINDING (learned fusion adds nothing on top of the real
  coarse solve), not a failure.**

- **Recipe**:
```json
{
  "base_family": "mf_fno_transfer_film",
  "base_commit": "967562e2a4e3493515edab36b0fcb23655fce71f",
  "family_dir": "models_r1/s6_local_lf_corrector",
  "datasets": "panel",
  "epochs": 200,
  "seeds": [0],
  "env": {
    "S6_VARIANT": "local_pixel_gate",
    "S6_SCREEN_VARIANTS": "local_pixel_gate,local_scalar_gate,lf_frozen_adapter,local_band_gate,pointwise_ctrl",
    "S6_SCREEN_EPOCHS": "2",
    "S6_SCREEN_DATASETS": "panel,guard",
    "S6_SCREEN_NOHARM_MAX_SKILL": "1.02",
    "S6_PROMOTION_RULE": "max_holdout_rho_margin_0.05_else_rank_order",
    "S6_KERNEL": "7",
    "S6_DEPTH": "4",
    "S6_WIDTH": "32",
    "S6_GATE_INIT": "zero",
    "S6_GATE_HOLDOUT_FRAC": "0.2",
    "S6_GATE_LINESEARCH_INCLUDES_ZERO": "1",
    "S6_BAND_EDGES_FRAC": "0,0.125,0.25,0.5,1.0",
    "S6_LF_SOURCE": "dataset_lf_fidelity",
    "S6_LF_FID": "max",
    "S6_FALLBACK_NO_TEST_LF": "champion",
    "S6_LEAKAGE_TRIPWIRE": "1",
    "S6_DIAG_OUT": "mffp_autoresearch_outputs/round1/s6_local/B1/eval"
  }
}
```

- **Expected outcome**:
  Panel geomean skill **~1.03** vs the certified anchor **6.703016** — `Delta ~ -5.67`, **6.4x the
  0.884 geomean floor** (the s5-B1 convention, = the anchor ci95 width). Composition: the five
  beyond-copy datasets land in skill **[0.85, 1.00]** (they start at exactly 1.000 by construction
  and can only be trained away from it), and `ifc_poisson` falls back to the champion path at
  **~1.566**; `(0.95^5 * 1.566)^(1/6) = 1.03`. Per-dataset Layer-1 thresholds and their floors:
  allen_cahn `<= 14.700664` (certified 16.334071, floor 1.633407), pfc `<= 10.359901`
  (11.511001 / 1.151100), cahn_hilliard `<= 4.980119` (5.533466 / 0.553347), fisher_kpp
  `<= 3.759620` (4.177355 / 0.417735) — each clears its floor by construction and the prediction
  clears each threshold by 3-15x. `ext__helmholtz_2d` (floor **9.694961**) is **report-only, no
  numeric claim**; `ifc_poisson` (floor 0.239908) is a no-op fallback leg with **no claim**.
  **This geomean move is construction, not discovery, and the card says so.** The reportable
  content is `contribution_d` (predicted 0.05-0.20 on `sharp__cahn_hilliard` and
  `sharp__fisher_kpp_2d`, where LF<->HF band coherence stays highest — fisher_kpp
  [0.9996, 0.9481, 0.8911, 0.0231]; predicted near 0 on `sharp__phase_field_crystal_2d`, whose
  band-2 coherence is 0.0005) and the per-band contribution profile.
  Cross-stream evidence confronted: **(a)** the low-band excess (`R_low` 11-209) is a property of
  the champion's *generated* field — this design inherits the low band from the real coarse solve
  and so predicts `R_low(trained)/R_low(identity) ~ 1`, i.e. it fixes low-band error by not
  generating it; the claim is *not* motivated by high-k sharpness. **(b)** it **damps** spurious
  high-k: the base output is a bilinearly upsampled coarse solve (essentially low-pass), and any
  high-k the corrector adds is multiplied by a held-out-selected gate whose search set contains 0
  — versus the champion's pfc band-1 `R_b = 2557`. **(c)** `fisher_kpp`'s information deficit is
  an *X-only* result (cond_dim 2, `nn_over_random` 0.937); this model is not X-only, so a gain
  there must be LF-driven — expectations are set low and no falsification leg requires a
  fisher_kpp win. **(d)** this is the round's second LF-consuming model and the **first whose base
  prediction IS the LF field** (s4's `fno_transolver_seq` gates to the champion, floor ~6.7).

- **Expected falsification**:
  H2-local is falsified if, at 200 epochs seed 0, EITHER the promoted variant's panel geomean skill
  is not at least 0.884 skill units below the certified anchor 6.703016 (i.e. not `<= 5.819016`)
  or any of `sharp__allen_cahn_2d`, `sharp__phase_field_crystal_2d`, `sharp__cahn_hilliard`,
  `sharp__fisher_kpp_2d` fails its Layer-1 threshold `14.700664 / 10.359901 / 4.980119 / 3.759620`
  (each exactly one `min_claimable_effect` — 1.633407 / 1.151100 / 0.553347 / 0.417735 — below the
  certified champion skill), which would mean the identity-to-copy-LF construction itself is broken;
  OR — the informative leg — the held-out-selected trust gate is identically zero, or the trained
  contribution `contribution_d = skill_id - skill_trained` is below 0.04 on at least 4 of the 5
  beyond-copy datasets (0.04 exceeds every champion seed-spread floor rescaled to skill 1.0:
  allen_cahn 0.000866, pfc 0.007180, fisher_kpp 0.021973, cahn_hilliard 0.034667), in which case a
  LOCAL corrector adds nothing on top of the real coarse solve and H2 is refuted for this
  composition; and the strong form of H2 is supported only if `contribution_d >= 0.10` (the same
  10%-relative rule that generates every `min_claimable_effect`, applied at this model's skill
  level of ~1.0) on at least 2 of {allen_cahn, cahn_hilliard, fisher_kpp, pfc} with a non-zero
  gate — with `ext__helmholtz_2d` report-only (floor 9.694961, no numeric claim), `ifc_poisson` a
  pre-registered no-op fallback leg (no LF at test), displacement error explicitly out of scope
  (`s3_warp` owns it), and every Layer-2 number labelled `provisional-single-seed` (ADR 0004).

- **Prior-art verdict quoted**: verbatim from
  `websearches/s6_local/batch_1/report.md`, `## Prior-art verdict`, row **D3** —
  > **D3** — local corrector consuming the **real interpolated LF field at test time**, with an
  > identity-to-copy-LF construction (zero-init gate ⇒ at init the model IS copy-LF) |
  > **preempted-but-MF-composition-open** | https://arxiv.org/pdf/2102.01010 and
  > https://www.sciencedirect.com/science/article/abs/pii/S0045793023001962 (learned coarse-grid
  > correction); https://arxiv.org/abs/2605.12965 (U-HNO per-pixel spectral/local routing,
  > shock-aware, **no** no-harm guarantee); https://arxiv.org/pdf/1901.09321 (Fixup
  > identity-at-init; fetched by s2-B1) | A no-harm floor **defined by a real coarse PDE solve**
  > (= round success criterion 2, skill < 1), plus the champion's blind spot that it never sees LF
  > at inference. **Stream-boundary flag: `s2_beyond_copy`-B1 D2 already owns "identity-to-LF";
  > s6 owns only "the corrector is LOCAL".**

  and row **D2** (variant 3 only) —
  > **D2** — fidelity-asymmetric capacity: LF trains the spectral backbone; the ONLY HF-trained
  > module is a small, capacity-constrained, zero-init **local** adapter |
  > **preempted-but-MF-composition-open** | https://arxiv.org/html/2509.23173v1 (F-Adapter: PEFT on
  > FNO, per-band widths, N=24, single fidelity); https://arxiv.org/abs/2204.09157 (MF DeepONet: LF
  > subnet + HF correction subnet, no locality); https://arxiv.org/html/2505.21573v3 (5-trajectory
  > spectral model beats data-driven at 200) | **Aligning the spectral/local inductive-bias split
  > with the LF/HF data split** appears in no fetched source. It also carries a *published opposing
  > prediction* (F-Adapter says capacity belongs in LOW bands) — a genuine pre-registered
  > falsification risk, which is what makes it a real experiment.

  and, from `websearches/_scouting/2026-07-29_stream_gap_mining/report.md` row **C1** —
  > **C1 Guaranteed-fallback, trust-gated MF fusion** — `y = LF_up + g ⊙ Δ(LF,X)`, `g∈[0,1]`
  > per-pixel/per-band, `g≡0` at init reproduces copy-LF exactly |
  > **preempted-but-MF-composition-open** | MAST https://arxiv.org/html/2602.20974 (GP, **scalar
  > QoI**, no guarantee, ~2.04x worst case); physics-guided correction
  > https://arxiv.org/html/2606.03469 (additive, **explicitly ungated**, **"no formal guarantee
  > exists"**, physics prior); CV gating
  > https://www.emergentmind.com/topics/learnable-skip-and-gate-fusion (hit); safe policy
  > improvement (hit) | OPEN: a **field-valued per-pixel/per-band trust gate over the interpolated
  > LF field inside a neural operator, parameterized so the scored copy-LF reference is exactly
  > recoverable and is the initialization**. -> **NEW STREAM (rank 1)**. Unresolved threat to
  > re-check: AGMF-Net (403)

  Suggested `prior_art` for the card: `verdict: "preempted-but-MF-composition-open"`; citations
  https://arxiv.org/pdf/2102.01010 , https://www.sciencedirect.com/science/article/abs/pii/S0045793023001962 ,
  https://arxiv.org/abs/2605.12965 , https://arxiv.org/pdf/1901.09321 ,
  https://arxiv.org/html/2509.23173v1 , https://arxiv.org/abs/2204.09157 ,
  https://arxiv.org/html/2505.21573v3 , https://arxiv.org/abs/2402.16845 ,
  https://arxiv.org/abs/2109.03697 , https://arxiv.org/pdf/2504.04260 ,
  https://arxiv.org/pdf/2606.02661 , https://arxiv.org/html/2602.20974 ,
  https://arxiv.org/html/2606.03469 ; unresolved threat: AGMF-Net
  https://www.sciencedirect.com/science/article/abs/pii/S002980182502997X (HTTP 403, both loops).

- **Immutables self-check**: **pass (10/10)** — positive evidence for each of the 8 immutables
  plus the two round-1 extras is recorded in
  [iteration_1.md](iteration_1.md) § "Immutables self-check". Nothing was flagged; no revision
  was needed. Highlights: (1) LF comes from the dataset's own LF fidelity array with a
  coarser-than-HF grid assertion, never a downsampled HF field; (3) all new code lives in the
  worktree `models_r1/`, no `round1/eval/` edit; (4) the scored metric stays `eval/nrmse.py`, the
  sidecars call the same function; (9) thresholds quoted above clear every cited floor;
  (10) nearest pre-falsified lever is **LF low-mode freezing (`mf_fno_spectral`)** — the difference
  is that nothing is frozen here: the low band is *inherited from the real coarse solve* rather
  than locked inside a generator, and the only band-structured element (variant 4) gates a
  correction that is exactly zero at init with 0 in its search set.

- **Anchor reference**: `null` (lever-class stream; own-stream anchor implicit — program.md §4.5).

- **Source iteration**: [iteration_1.md](iteration_1.md)

## Reopen candidates

| Candidate | Verdict (retry/drop) | Eased conditions | Source iteration |
|---|---|---|---|
| _none — `experiment_cards/s6_local/` does not exist; this is the stream's first card_ | n/a | n/a | [iteration_1.md](iteration_1.md) |

## Skipped slot

Not applicable — the slot is filled.

## Summary table

| Slot | Category | One-liner | Status |
|---|---|---|---|
| `s6_local-B1` | `mf_composition / trust-gated LOCAL corrector on the real LF field` | `y = LF_up + G(*)Delta_local(LF_up, X)` with the gate exactly 0 at init, so the model IS copy-LF at initialization and can only be trained away from it; 5 ADR-0007 variants (per-pixel / scalar / LF-frozen-adapter / per-band / receptive-field-1 control), contract-tier no-harm screen, promote one to 200 epochs seed 0 | filled |
