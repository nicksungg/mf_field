# summary_so_far — stream `s7_loss`, batch 1

Written before searching. Sources are files actually read this run (paths given).

## What the stream owns

`s7_loss` (ADR 0012, `docs/adr/0012-s7-loss-stream.md`) is a **lever** stream:
*does an interface-aware (or otherwise reshaped) training objective, holding the
architecture fixed, fix sharp-2D fusion?* Ground rules from the ADR and
program.md §12.7:

- **The scored metric is immutable** (program.md §2.1): per-sample rel-L2
  `mean_i ||pred_i - hf_i|| / ||hf_i||` through `round1/eval/nrmse.py`. A win =
  better rel-L2 obtained by training against something *else*.
- **Physics-agnostic only** (ADR 0009, `docs/adr/0009-unknown-physics-constraint.md`):
  interface/frequency weights must come from the field's own gradients / level
  sets / spectra, never from governing equations.
- **ADR 0007** (`0007-propose-many-screen-cheap.md`): propose 3-5 ranked loss
  variants, screen at contract tier (2 epochs, H100), promote one to the
  200-epoch seed-0 run.
- **Pre-registered risk (ADR 0012)**: sharp-region upweighting can trade bulk
  accuracy for interface accuracy and *lose* on rel-L2. Cards must state this.

## Anchor and noise floor

No `state/anchors/s7_loss.json` exists yet; the stream's anchor is the batch-0
champion panel geomean, certified in `state/anchors/s5_tuning.json`:
`mf_fno_transfer_film`, geomean skill **6.703** (per-seed 7.102 / 6.219 / 6.788,
CI95 [6.219, 7.102], `provisional: false`).

`state/noise_floor.json` `min_claimable_effect` per dataset (skill units):
helmholtz **9.695** (enormous - helmholtz supports no numeric claims),
ifc_poisson 0.240, allen_cahn 1.633, cahn_hilliard 0.553, fisher_kpp 0.418,
phase_field_crystal 1.151. Any falsification threshold must exceed these.

## In-round evidence that reshapes the loss question (s2_beyond_copy-B1)

From `experiment_cards/s2_beyond_copy/batch_1/B1.json` part 5 and
`state/orchestrator_flow.md` (2026-07-29T17:26Z):

1. **M1 - the champion is LF-BLIND at inference on all 5 datasets / 3 seeds**:
   the only tensor entering the network is `[batch, cond_dim]`; zero
   field-shaped inputs. Decisive for s7: "make the output faithful to the LF
   low band" cannot be enforced *at test time* through the loss on this family
   - but LF **is** available at training time, so an LF-anchoring loss term is
   still a pure objective change.
2. **M3 - excess error concentrates in the LOWEST spectral band, 5/5 datasets**
   (`R_low > 1` for every seed; allen_cahn `R_low ~ 209`), and the champion
   injects spurious high-k energy. The classical sharp-field reflex (upweight
   high-k / interface pixels) is therefore *contraindicated* as a first move.
3. **M4 - error is not interface-concentrated on pfc** (mid-distance peak); on
   helmholtz the outermost (far-from-interface) stratum carries ~3.0-3.6x its
   area share for every predictor including copy-LF.
4. **M5a - helmholtz error is 86.5% amplitude**: one optimal per-sample scalar
   rescale takes champion nRMSE 6.202 -> 0.839. Amplitude/normalization, not
   sharpness, is the helmholtz story.
5. M5b: LF<->HF pairing is sound (the data-defect branch is closed).

## In-repo backlog this stream ingests

`docs/proposals/MODEL_TWEAKS_EVIDENCE.md`:
- **F19** (line 534): 11 of 21 families train `F.mse_loss` on a globally
  max-abs scaled residual - a sample 10x below median energy contributes ~1/10
  of the gradient it deserves while counting fully at scoring time. In-repo
  precedent for the fix exists (`transolver_residual/smoke_eval.py:65-69`,
  provenance `references/v9_baseline/train_v9.py:157-163`): `mse + mean(rel)`.
- **F20** model-selection metric mismatch (pooled energy-weighted nRMSE, not
  per-sample); **F21** two families train in raw physical units.
- **F14-F18** are *structural constraints* (positivity/log-space head, integral
  conservation projection, divergence-free stream function, hard BCs, and the
  F18 detection probe that must run before any constraint is enabled). F14-F17
  are output-parameterization/head changes and MODEL_TWEAKS ranks them
  "probe-dependent"/low-confidence - weaker batch-1 material than F19/F20.

## Prior websearch already in repo (cite, do not re-derive)

`docs/reports/MF_Sharp_HighFreq_Report.md` proposes exactly this stream's P2
(`mf_fno_transfer_sharploss`: Charbonnier + gradient-weighted + focal-frequency
+ frequency-continuation curriculum) and lists band-reweighted losses,
multi-resolution STFT loss, OT/soft-warp auxiliary losses, hard-patch mining.
`docs/reports/MF_Leaderboard_Beaters_2026_Report.md` carries IRNO's progressive
spectral loss, HANO's empirical H1 loss, and the Spectral-Refiner H^-1
estimator. These are *prior websearches by another agent* - their arXiv IDs are
leads to verify, not citations I may re-issue without fetching (program.md
§13.3; novelty record 0-for-4).

## Open questions this batch must answer

- (a) Published losses beyond L2 for neural PDE surrogates (Sobolev/H1,
  frequency-weighted, gradient-domain, SSIM-structural, relative-vs-absolute
  per-sample normalization) and evidence on sharp/discontinuous fields.
- (b) Amplitude/scale-calibration objectives (per-sample normalization,
  scale-equivariant training) for field regression.
- (c) Losses / output parameterizations that anchor the low-k band to the LF
  input - and whether "residual-from-LF" is an objective or architecture change
  for an LF-blind champion.
- (d) Small-N_hf multi-fidelity regime evidence.
- Prior-art verdict: Sobolev training is published. The adversarial question is
  what remains open for the *multi-fidelity, few-HF-sample* composition.
