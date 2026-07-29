# iteration_1 — s6_local batch 1 slot design

## Design context considered

- `summary_so_far.md` §6 (10 unknowns), §1 (D1/D2/D3 verdicts + scout C1 + operator correction),
  §2 (program.md §12.6 verbatim + anchor 6.703016 + noise floors).
- **The immutables block (program.md §5), held verbatim in view** — reproduced and checked
  one-by-one under "Immutables self-check" below.
- Anchor: champion panel geomean **6.703016262587087** (batch 0, `provisional: false`).
  Noise floors (skill units): helmholtz 9.694961 (report-only), allen_cahn 1.633407,
  pfc 1.151100, cahn_hilliard 0.553347, fisher_kpp 0.417735, ifc_poisson 0.239908;
  geomean floor 0.884.
- Pre-falsified levers (§5): WNO backbone swap; **LF low-mode freezing (`mf_fno_spectral`)**;
  diffusion prior for point accuracy.
- ADRs: 0004 (strict single seed), 0005 (H100), 0007 (propose-many / screen-cheap / promote-few),
  0009 (no physics at test time), 0011 (this stream).
- Verified first-hand this run (not from memory):
  - `mf_field/factory_mffp/models/mf_fno_transfer_film/model.py` — `FNO2d.forward` lifts the
    **coordinate grid only**; `X` enters via per-block FiLM. No field input. Confirms s2-B1 M1.
  - `mf_field/factory_mffp/models/mf_fno_transfer_film/smoke_eval.py` — LF fidelity used for
    pretraining is `min(train["lf_fids"])` (the LOWEST), whereas
    `round1/eval/panel_data.py::copylf_prediction` uses `max(data["lf_fids"])` (the HIGHEST) with
    `scipy.ndimage.zoom(order=1, grid_mode=True, mode="nearest")`. **Any identity-to-copy-LF
    construction must use `max(lf_fids)`.**
  - `data/ifc_poisson/test/` contains only `fidelity_64`; `train/fidelity_64/ys.npy` is
    `(5, 64, 64)`, `test/fidelity_64/ys.npy` is `(128, 64, 64)`. No LF at test.
  - `data/{sharp__allen_cahn_2d,sharp__cahn_hilliard,sharp__fisher_kpp_2d,
    sharp__phase_field_crystal_2d,ext__helmholtz_2d}` and all three guard datasets ship
    `test_l*.npz` (LF present at test).
  - `state/timing_ledger.json`: champion 200-epoch seed-0 panel legs sum to ~186 min
    (helmholtz 36.6 h100, pfc 12.2, allen_cahn 44.3, fisher_kpp 44.3, cahn_hilliard 44.3,
    ifc_poisson 4.5).

## Proposal reasoning

### The reframing that drives everything

s2-B1 M1 makes the literal reading of H2 untestable: **the champion has no field input**, so
"add a local (conv) branch to the FNO" has nothing to convolve. A local operator is defined by a
bounded receptive field over a field; the only field available at test time is the interpolated
LF field. So the s6 question, made concrete, is: *does a local operator acting on the real LF
field add value that the champion's global spectral generator cannot?*

That is D3 (= scout C1), and it is also the only construction that engages the round's second
success criterion directly: a corrector built as `LF_up + g*Delta` with `g` identity-init-to-zero
**starts at copy-LF** (skill exactly 1.0 by construction) and can only be trained away from it.
No current round-1 model has this property; s4-B1's `fno_transolver_seq` gates to the *champion*
(floor ~6.7), not to copy-LF.

### Alternatives weighed and rejected

1. **D1 as the card (parallel local path inside the champion, U-FNO / NO-LIDK style).** REJECTED
   as the primary. Verdict is **preempted** on mechanism; it would have to be written as a pure
   measurement, and — worse — its floor is the champion's 6.703, so a null result teaches us
   little we do not already know from s5-B1. Kept as a **batch-2 option**, and its code path
   (the champion base) is present in the substrate anyway because ifc_poisson needs it as a
   fallback.
2. **Pure local backbone replacement (ConvNeXt-U-Net as the model).** REJECTED — the websearch
   verdict rejects it on in-repo evidence (`convnext_unet_film` 3.599 vs champion 1.526 on
   helmholtz), and ADR 0011 already settles it ("capacity is not the question, composition is").
3. **Free-form ConvNeXt refiner fine-tuned on the HF split, ungated.** REJECTED — this is the
   literature-identified known-bad recipe (https://arxiv.org/html/2505.21573v3,
   https://arxiv.org/html/2509.23173v1) and is weakly corroborated by the mentor's off-repo
   attempt (poor result; details unavailable). My design differs on three stated axes:
   (i) it **consumes the given LF field** rather than a stage-1 *prediction* of LF, deleting the
   documented exposure-bias failure (https://arxiv.org/pdf/2606.02661); (ii) it is **zero-init and
   gated with copy-LF exactly recoverable**, so it cannot start worse than the coarse solve;
   (iii) the local module is **capacity-constrained** (depthwise 7x7, width 32, depth 4) and in the
   D2 arm is the *only* HF-trained parameter set. I claim nothing by absence of the mentor's data.
4. **D2 alone (fidelity-asymmetric capacity) as the whole card.** REJECTED as the whole card, KEPT
   as one variant (V4). Its published opposing prediction (F-Adapter: scarce capacity belongs in
   LOW bands) makes it the sharpest falsifiable arm, but on its own it does not deliver the no-harm
   floor that the round's success criterion 2 needs.
5. **LF low-mode freezing / band-split correction.** REJECTED — §5 pre-falsified lever
   (`mf_fno_spectral`: "worst on sharp, catastrophic on lid-cavity"), and independently
   *unlicensed* by s2-B1 leg D ("the band-split direction D3 is NOT licensed by this diagnostic").
   The one band-structured element I keep (V3's per-band gate) is a *gate on a correction that is
   zero at init*, not a freezing of LF modes in a generator — see self-check item (10).
6. **Retrieval / exemplar residual banks (scout C2).** REJECTED for B1 by coordinator direction
   (parked for batch 2). Not folded in.
7. **Warp / displacement handling.** REJECTED — `s3_warp` owns it; the websearch's
   receptive-field argument says a local operator cannot move a misplaced interface. I scope this
   card's claim to **blur / sharpness / amplitude**, not displacement.

### How the design confronts the mandated cross-stream evidence

- **(a) Excess error is in the LOWEST band on all 5 (`R_low` 11–209).** My local path is *not*
  motivated by high-k sharpness. The low-band excess is a property of the champion's *generated*
  field; copy-LF has `R_low = 1` by definition. Starting at copy-LF removes the low-band excess
  **by construction** — the model inherits the long wavelengths from the real coarse solve instead
  of regenerating them. V2 (`local_band_gate`) turns this into a hard, per-band-auditable statement.
  The card therefore predicts `R_low(trained) / R_low(identity) ~ 1` and reports it as a sidecar.
- **(b) The champion injects spurious high-k energy (pfc band-1 `R_b` = 2557).** My design
  **damps** it: the base output is a bilinearly upsampled coarse solve, which is essentially
  low-pass, so at init the spurious high-k content is ~0; any high-k the corrector adds is
  multiplied by a gate selected on a held-out split whose search set includes 0. The card
  pre-registers the per-band contribution ratio so amplification, if it happens, is visible.
- **(c) `fisher_kpp` is an information deficit.** s2-B1's finding is specifically that *X-only*
  predictors collapse onto ~4.1 (cond_dim 2, `nn_over_random` 0.937). My model is **not X-only** —
  it reads the LF field, and fisher_kpp's LF<->HF band coherence [0.9996, 0.9481, 0.8911, 0.0231]
  is the highest into band 2 of any panel dataset. So a gain there must be LF-driven, not
  X-driven. Expectation set accordingly: fisher_kpp is the cleanest single-dataset test of the
  mechanism, but I do **not** predict a large gain, and the falsification clause does not require one.
- **(d) M1: the champion never consumes LF at test time.** This card is the round's second
  LF-consuming model and the **first whose base prediction IS the LF field**. Informative either way.

### The design

Family `models_r1/s6_local_lf_corrector`, one substrate, five env-selected variants:

```
LF_up   = interp(field_by_fid[max(lf_fids)] -> working grid)        # == copy-LF construction
Delta   = C_theta(LF_up, coords, FiLM(X))                           # LOCAL: depthwise KxK stack
y_hat   = LF_up + G ⊙ Delta                                         # G is the trust gate
```
- `C_theta`: ConvNeXt-lite, depth 4, width 32, depthwise KxK (K=7 default) + pointwise, GroupNorm,
  FiLM(X) per block, **final 1x1 zero-init** => `Delta ≡ 0` at init.
- `G`: gate, **exactly 0 at init** in every variant; scalar / per-pixel / per-band by variant;
  the scalar component is finally selected on a held-out slice of the HF train split by
  least-squares projection + a line search whose candidate set **contains 0** (construction
  reused from the in-round sibling `fno_transolver_seq`, cited as such — not novel).
- Training target: `R = Y_hf - LF_up` on the HF train split (400 samples on the sharp five).
- **Fallback**: if the *test* split of a dataset ships no LF fidelity (`ifc_poisson` only,
  verified), the family runs the champion path verbatim (LF-pretrain -> HF-finetune X-only
  FiLM-FNO). Pre-registered as a **no-op leg** — no claim is made on ifc_poisson.
- **Leakage tripwire** (builder requirement): assert the LF input tensor is sourced from an LF
  fidelity array and that no HF *test* field ever enters the prediction path; assert
  `nRMSE(identity path)` matches `eval/copylf_baselines.json` to within the interpolation-kernel
  difference (`scipy.zoom order=1` vs `F.interpolate bilinear`) and record the delta.

### Variants (ADR 0007), ranked

| rank | id (`S6_VARIANT`) | what differs | why it is in the pool |
|---|---|---|---|
| 1 | `local_pixel_gate` | gate `g(x) = sigmoid(h(x) + b0)`, `b0` set so `g ≡ 0` at init (hard-zero offset, exactly recoverable) | the scout's C1 rank-1 open composition: a **field-valued** trust gate over interpolated LF inside a neural operator; maximal s6 ownership (local corrector + local gate) |
| 2 | `local_scalar_gate` | one scalar gate, held-out selected | the clean control for rank 1: does spatial trust structure buy anything over one number? Simplest, most robust arm |
| 3 | `lf_frozen_adapter` | spectral encoder trained on **LF only** then FROZEN; the **only** HF-trained params are the zero-init local adapter + gate | the D2 arm; carries F-Adapter's published **opposing** prediction (scarce capacity belongs in LOW bands, ours is all-band + spatially restricted) |
| 4 | `local_band_gate` | 4 scalar gates, one per spectral band (s2-B1 band convention: edges at `k_nyq * [0, 1/8, 1/4, 1/2, 1]`), all init 0 | makes the low-band no-harm claim a hard, per-band-auditable guarantee; band-resolved readout of where learned fusion can help |
| 5 | `pointwise_ctrl` | `K = 1` (receptive field = 1 cell) | the receptive-field control that isolates **locality-as-spatial-kernel** from pure pointwise recalibration — H2's real content, given s2-B1 M5a amplitude findings |

### Screening + promotion (ADR 0007), pre-registered

- **ONE contract-tier job**: `--epochs 2 --seed 0`, all five variants, `--datasets panel` plus
  `--datasets guard` (the card will claim a panel win, so the guard set is required by §2.3).
  Cost estimate from `state/timing_ledger.json` + s2-B1's 46 s H100 precedent: minutes. Reserve
  01:00:00.
- **No-harm assertion (the screen's primary function)**: at 2 epochs every variant must score
  `skill <= 1.02` on each of the five beyond-copy datasets. A violation means the identity
  construction is broken => ALGO. This, not ranking, is what the screen is for: with a gate that
  contains 0, all variants are expected to sit at ~1.000 at 2 epochs and be indistinguishable on
  the scored metric.
- **Discard rule**: drop a variant only if (i) it crashes / NaNs, (ii) it violates the no-harm
  assertion, or (iii) its 5-dataset contract geomean exceeds 2x the best variant's. Close calls
  are NOT discarded (ADR 0007: 2-epoch rankings are noisy).
- **Promotion rule (fixed BEFORE submit, no post-hoc switching)**: among survivors, promote the
  variant with the highest mean held-out residual-explained fraction
  `rho = 1 - ||R - G*Delta||^2 / ||R||^2` over the five beyond-copy datasets, **provided** its
  `rho_bar` exceeds the runner-up's by > 0.05 absolute; otherwise promote by rank order
  (1 -> 2 -> 3 -> 4 -> 5). `rho` is a training-side plumbing signal recorded in `build_notes`
  only; per ADR 0007 it is never quoted as evidence in parts 5–7. If no variant survives, the
  card is ALGO-broken and goes to the debugger.
- **Promoted run**: 200 epochs, seed 0, `--datasets panel`; guard set at contract tier.
  Reserve 06:00:00 (champion panel legs sum to ~186 min; the corrector stage adds to that).

### The gaming hazard, pre-registered

With an identity-init gate, `skill <= 1.0` is reachable **at initialization**. Therefore **raw
skill is explicitly NOT the win condition of this card.** The card's readout is the *trained
gate's contribution* over the identity path:

```
skill_id   = nRMSE(family's G≡0 path)   / copy-LF nRMSE     (deterministic, zero seed variance)
skill_tr   = nRMSE(family's trained path)/ copy-LF nRMSE     (the scored value)
contribution_d = skill_id - skill_tr                          (>0 = learned fusion added value)
band_contribution_b = ||e_b(trained)||^2 / ||e_b(identity)||^2 (per band; <1 = improvement)
```
`skill_id` and the band ratios are written as **sidecar diagnostics** computed through
`round1/eval/nrmse.py` on the family's own predictions — no new scored metric, §2.1 untouched.
**A gate that collapses to zero is a FINDING (fusion adds nothing on top of the coarse solve),
not a failure**, and the card says so.

### Threshold arithmetic (against the certified floors)

Layer 1 — *floor-clearing sanity leg* (satisfies program.md §4.5 literally; note it is largely
guaranteed by construction, so its FAILURE, not its success, is the informative outcome):
per-dataset scored skill at least `min_claimable_effect` below the champion's certified skill —

| dataset | champion certified skill | floor | required |
|---|---|---|---|
| `sharp__allen_cahn_2d` | 16.334071 | 1.633407 | <= 14.700664 |
| `sharp__phase_field_crystal_2d` | 11.511001 | 1.151100 | <= 10.359901 |
| `sharp__cahn_hilliard` | 5.533466 | 0.553347 | <= 4.980119 |
| `sharp__fisher_kpp_2d` | 4.177355 | 0.417735 | <= 3.759620 |
| `ext__helmholtz_2d` | 13.817290 | 9.694961 | report-only, **no numeric claim** |
| `ifc_poisson` | 1.565633 | 0.239908 | fallback no-op leg, **no claim** |
| panel geomean | 6.703016 | 0.884 (ci95 width, s5-B1 convention) | <= 5.819016 |

Predicted: the five sharp datasets land in skill [0.85, 1.00]; ifc_poisson falls back to ~1.566;
panel geomean `(0.95^5 * 1.566)^(1/6) ~ 1.03`, i.e. **Delta ~ -5.67 vs the anchor, 6.4x the 0.884
geomean floor**. Every Layer-1 threshold clears by 3–15x.

Layer 2 — *the actual scientific leg*. Support requires `contribution_d >= 0.10` on **>= 2** of
{allen_cahn, cahn_hilliard, fisher_kpp, pfc} **with a non-zero held-out gate**. Refutation:
held-out gate `G ≡ 0`, or `contribution_d < 0.04` on **>= 4** of the five beyond-copy datasets.
Justification of these numbers against the certified noise floor (this is the honest part):
the floor rule in `state/noise_floor.json` is `mce = max(seed_spread, 0.10 * mean_skill)`, i.e. a
**10%-relative** rule floored by the seed spread. This model operates at skill ~1.0, not at the
champion's 4.2–16.3, so the 10%-relative component is `0.10 * 1.0 = 0.10` skill units — the
support threshold. The seed-spread component rescaled to skill 1.0 is
`spread/mean_skill`: allen_cahn 0.000866, pfc 0.007180, fisher_kpp 0.021973,
cahn_hilliard 0.034667 — the largest is **0.0347**, so the refutation threshold **0.04 exceeds
every rescaled seed-spread floor** and the support threshold 0.10 exceeds it by ~2.9x. In
addition, `skill_id` is deterministic (a fixed interpolation of fixed read-only data, zero seed
variance), so all of `contribution_d`'s variance comes from the trained arm. Everything in Layer 2
is `provisional-single-seed` (ADR 0004).

## Proposal

- **Category**: `mf_composition / trust-gated local corrector on the real LF field`
- **Card type**: `model`
- **Motivation**: quotes the D3 verdict row verbatim (see `report.md`).
- **Concrete config**: as above; family `models_r1/s6_local_lf_corrector`, five variants,
  contract screen -> promote one -> 200 epochs seed 0 on the panel.
- **Recipe**: see `report.md` (complete JSON).
- **Expected outcome**: panel geomean ~1.03 vs anchor 6.703 (Delta ~ -5.67, 6.4x the 0.884 floor)
  — but this is construction, not discovery; the reportable content is `contribution_d` and the
  per-band contribution profile.
- **Expected falsification**: see `report.md` (single sentence, both layers).
- **Anchor reference**: `null` (lever-class stream; own-stream anchor implicit, program.md §4.5).

## Immutables self-check (positive evidence for each)

1. **Data read-only.** The family calls `data_adapters.loaders.load_mf_dataset(dataset_dir, split)`
   read-only and consumes `field_by_fid[max(lf_fids)]` — the same array `eval/panel_data.py::
   copylf_prediction` reads. No file under `benchmark_42/**` or `factory_root/data/**` is written,
   no HF sample is added, and the LF field is the dataset's own real coarse solve: the recipe
   explicitly forbids constructing LF by downsampling HF (`S6_LF_SOURCE=dataset_lf_fidelity`), and
   the builder must add an assertion that the LF tensor's native grid is strictly coarser than the
   HF grid, which is only true of a genuine coarse solve.
2. **Panel + guard set fixed.** `recipe.datasets = "panel"`, expanded from `project.yaml`
   (`ext__helmholtz_2d, sharp__phase_field_crystal_2d, sharp__allen_cahn_2d,
   sharp__fisher_kpp_2d, sharp__cahn_hilliard, ifc_poisson`); the guard run uses
   `--datasets guard` (`heat_local, fluid, sharp__sod_1d`). No dataset is added, removed, or
   substituted — ifc_poisson is *run* and *scored*, it merely takes the fallback code path.
3. **Eval layer / spec untouched.** Everything new lives in the worktree at
   `models_r1/s6_local_lf_corrector/`. The card requires no edit to `round1/eval/`, `project.yaml`,
   `program.md`, ADRs, or subagent prompts: the family is discovered by
   `eval/score_panel.py --family_dir`, and the sidecar diagnostics are written by the family into
   its own `S6_DIAG_OUT` directory under the outputs root, not into `round1/eval/`.
4. **One nRMSE definition.** The scored value remains `eval/nrmse.py`'s per-sample relative L2 on
   the raw HF test field; the training loss (MSE on `R = Y_hf - LF_up` in scaler space) is free
   per §5. `skill_id` and the band ratios are computed by calling `eval/nrmse.py` on the family's
   own predictions — the same function, the same `nrmse_def_hash`, applied to an extra prediction
   array; no metric is redefined or hand-recomputed.
5. **Contract CLI fixed.** `smoke_eval.py` exposes exactly
   `--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed` and writes a results JSON with
   `model`, `dataset`, `splits.test.nRMSE`. Every knob is an environment variable and every one of
   them appears in `recipe.env` below, so they enter the cache key.
6. **Seeds / tier epochs fixed.** `epochs: 200` (smoke tier, `project.yaml tiers.smoke_epochs`),
   `seeds: [0]` (ADR 0004 strict single seed, program.md §4.4 as amended). The screen runs at
   `contract_epochs: 2`. No full-tier (2500) run is requested.
7. **Guarded factory surfaces untouched.** The family is written to
   `<worktree>/models_r1/s6_local_lf_corrector/`. The champion fallback path is a **copy** of
   `mf_fno_transfer_film`'s model + training code into that directory (§5 explicitly permits
   "building on existing zoo families — extending, composing, refining them"); nothing under
   `factory_root/{eval,baselines,references,scripts,data}/`, `factory.md`, or `mf_field/akash/**`
   is modified, and `fno_transolver_seq`'s gate construction is re-implemented in the new family
   rather than imported from `akash/`.
8. **Checkpoint-resume implementable.** The family saves
   `{"epochs_target", "grid", "recipe_hash", "base": ..., "corrector": ..., "gate": ...,
   "scalers": ...}` to `<ckpt_dir>/last.pt` after each stage and reloads it when
   `(epochs_target, grid, recipe_hash)` match — the same pattern already working in
   `mf_fno_transfer_film/smoke_eval.py` (lines 148-172) and `fno_transolver_seq`. `recipe_hash`
   includes `S6_VARIANT` and the knobs, so a variant switch invalidates the checkpoint.
9. **Falsification thresholds exceed the noise floor.** Layer 1: panel geomean `<= 5.819016`
   (anchor 6.703016 minus the 0.884 geomean floor); per-dataset `<= 14.700664` allen_cahn
   (floor 1.633407), `<= 10.359901` pfc (floor 1.151100), `<= 4.980119` cahn_hilliard
   (floor 0.553347), `<= 3.759620` fisher_kpp (floor 0.417735) — each threshold is exactly one
   `min_claimable_effect` below the certified champion skill, so it clears its floor by
   construction; helmholtz (floor 9.694961) is report-only with **no numeric claim**, and
   ifc_poisson (floor 0.239908) is a pre-registered no-op leg with **no claim**. Layer 2:
   support `contribution_d >= 0.10`, refutation `< 0.04`, both compared against the rescaled
   seed-spread floors 0.000866 / 0.007180 / 0.021973 / 0.034667 (allen_cahn / pfc / fisher_kpp /
   cahn_hilliard) — 0.04 exceeds all four and 0.10 exceeds the largest by 2.9x; and the
   `skill_id` reference is deterministic (zero seed variance).
10. **Not a pre-falsified lever re-proposed as-is.** Nearest is **LF low-mode freezing
    (`mf_fno_spectral`)**, "worst on sharp, catastrophic on lid-cavity" (§5). Difference: that
    lever *froze LF's low modes inside a generator that still synthesises the whole field*, so a
    wrong low band was locked in; here the low band is not frozen but **inherited from the real
    coarse solve** as the base prediction, and the only band-structured element (variant 4's
    per-band gate) gates a correction that is exactly zero at init and whose gate search set
    contains 0 — it can never lock in a synthesised band. Secondary nearest: the **WNO backbone
    swap** — n/a, the backbone is unchanged (no backbone is used for the correction at all in
    variants 1/2/4/5). **Diffusion prior** — n/a.

## Status

- Slot covered: YES (one proposal, `model` card, five ADR-0007 variants inside one card/recipe).
- Skipped: no.
- Reopen candidates resolved: none exist for this stream (`experiment_cards/s6_local/` absent).
- Immutables self-check: **pass (10/10)**, positive evidence recorded above. No revision needed;
  iteration_2 not required.
