# Summary so far — Stream `r2s1_direct`, Batch 2

All paths below are relative to
`/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch/round2/` unless absolute.

## 1. Websearch findings + prior-art verdict

Source: `websearches/r2s1_direct/batch_2/report.md` (5 iterations, cap hit; 13
WebSearch / 12 WebFetch, 8 usable; two fetches explicitly DISCARDED as
prompt-echo / metadata-only and cited for nothing).

Verdict table, verbatim rows:

- **E1** (out-of-fold per-spectral-band gain calibration of a frozen
  condition→field predictor's POINT output) — **`preempted (cite)` at the
  mechanism level**. "B1's band-gain fit is an empirical non-causal Wiener
  filter, `H_nc = S_hy/S_yy`; and 'SW adapts the shrinkage factor to local,
  data-driven SNR estimates ... hard-thresholds frequency components with low
  SNR' — i.e. B1's 'all non-DC gains go to zero' is a named, old phenomenon"
  (https://www.emergentmind.com/topics/non-causal-wiener-filter). Also
  post-hoc affine/amplitude correction of a frozen model on held-out data
  `a*=Cov(Y,Z)/Var(Z)` (https://arxiv.org/html/2505.15354) and in-architecture
  band gating (https://arxiv.org/pdf/2606.21189). Report item 1: "Ship it as
  machinery and *name it as a Wiener gain in the card*".
- **E2** (training-free statistic-selected output parameterization) —
  **`preempted-but-MF-composition-open (cite)`**; open: "Selecting a **field
  predictor's output parameterization** from statistics computable on the train
  split **without training any candidate**, pre-registered per dataset. Not
  found." Caveat: "rank-truncation-by-predictability is **presumed prior
  art**".
- **E3** (mandatory ~10^2-parameter closed-form control arm every capacity
  claim must beat, with the surviving capacity benefit localized to
  `sharp__cahn_hilliard`) — **`preempted-but-MF-composition-open (cite)`**;
  open: "A standing requirement to beat a ~10^2-parameter closed-form arm on a
  **copy-LF-skill** panel, plus per-dataset localization of where capacity is
  worth anything, is unprescribed. **Best-supported contribution shape for
  B2.**" (McGreivy & Hakim https://arxiv.org/abs/2407.07218; PCA-RaNN
  https://arxiv.org/pdf/2606.29440 as the control arm's declared prior art.)
- **E4** (regime/class-conditional prediction + per-class scoring on pfc) —
  **`preempted (cite — SEARCH-RETURN ONLY, NOT FETCHED; PROVISIONAL)`**; "**Do
  not headline E4 without a batch-3 confirming fetch**".

Brainstormer-directed items: quote the right row; E3 is the strongest shape;
E2 claimable only as a *pre-registered rule*; do not claim identifiable-rank
truncation; **design the falsification per-dataset, not on the geomean** (per-
dataset `min_claimable_effect`: cahn_hilliard 0.0912, pfc 0.2130, allen_cahn
0.8797, fisher_kpp 0.00071, ifc_poisson 0.9377, helmholtz 2.9530 →
report-only); honour ADR r2-0003 and the mandatory floor arms **plus the
DC-only ridge**.

## 2. program.md §12.1 conventions (verbatim)

> ### 12.1 `r2s1_direct` (gap)
>
> - **Bar**: the per-dataset floor table (§2.3). Beating NN-in-condition with
>   400 train samples is necessary but nowhere near sufficient; the interesting
>   question is how close a from-scratch condition→HF surrogate gets to
>   skill 1.0 on each dataset.
> - Design priors (spec §6): FiLM-conditioned FNO **decoders** (condition →
>   spectral latent → field), DeepONet-style branch–trunk (branch on condition,
>   trunk on coordinates), spectral/implicit decoders (SIREN/modulated INR
>   class). Condition vectors are 2–19 dims; ifc_poisson's is 5-dim.
> - **ADR r2-0003 (corrects a spec §4 grounding fact)**: on pfc, fisher_kpp
>   and allen_cahn the condition vector is NOT complete — per-sample random
>   ICs live only in the fields, so condition→HF is a stochastic map and
>   deterministic models are bounded by the conditional-mean floor
>   (train_mean > NN on those floors is the symptom). Skill→1 is unreachable
>   there; design and falsify against the conditional-mean floor, and treat
>   bare FiLM-decoders as declared baselines (prior-art verdict: preempted).
> - **Helmholtz lesson** (r1 report §5): the zero field is the floor to beat
>   there — any helmholtz claim must show the zero-floor column.
> - **pfc caveat** (§2.3): denominator 0.007381 under variant C; no
>   fidelity gap under band-limited. State it on every pfc claim.
> - N_hf on ifc_poisson is 5 — every claim there is anecdote-grade; prefer
>   variance-reducing designs (r1 s1 lesson: ensembling, physics residuals are
>   out per ADR 0009 — physics-agnostic at test).
> - Overfitting is THE central threat at these sample counts; r2s4's
>   overfitting-anatomy diagnostics feed this stream. Train/val discipline in
>   the recipe is mandatory (no test-split peeking; the round-1 D3 val_idx
>   double-consumption caveat is the cautionary tale).

Stream anchor (`state/anchors/r2s1_direct.json`): **23.063616857615774**,
`best_floor_panel_geomean`, per-dataset floors helmholtz 3.3441 (zero), pfc
59.8118 (mean), allen_cahn 269.1959 (NN), fisher_kpp 11.9931 (mean),
cahn_hilliard 23.1803 (NN), ifc_poisson 10.0549 (NN).
Noise floor (`state/noise_floor.json`, CERTIFIED, `_provisional: false`,
3-seed family `r2s4_cert_min`): panel `min_claimable_effect` 1.1418668;
per-dataset as quoted in §1.

## 3. Within-stream prior cards

`experiment_cards/r2s1_direct/batch_1/B1.json` — status `complete`,
`reopen_candidate: false`.

- Part 1–4: "identifiability-certified condition→HF decoder with a
  condition-predicted amplitude-direction factorization"; 14–16 M-parameter
  FiLM-spectral decoder, unit-direction × `exp(logamp)`, disjoint 10%/10%
  train-side folds, 21-point out-of-fold blend onto {zero, train_mean,
  nn_condition}, D3 identifiability certificate, floor-arm seam check.
  `prior_art.verdict: preempted-pivoted`. Recipe: `family_dir
  models_r2/r2s1_cond_decoder`, base_commit `9e10d414…`, panel, 200 epochs,
  seeds [0], 37 env knobs, guard leg at contract tier.
- Part 5: panel geomean skill **19.6444** (seed 0, provisional-single-seed);
  per dataset helmholtz 3.1043, pfc 52.0314, allen_cahn 244.4306, fisher_kpp
  11.5839, cahn_hilliard 12.8425, ifc_poisson 9.7846 — beats the best floor on
  all six. `falsification_verdict: falsified`, leg 1 only (19.6444 vs the
  19.60 geomean threshold, a 0.0444 margin = 3.9% of the certified panel
  min_claimable_effect 1.1419, i.e. decided by noise). Wall clock 6.95 min on
  one H200 for the whole panel+guard chain (4 h requested — 35x oversized).
  Anomalies: severe early overfit (best_epoch 2–24 of 200 on 5/6 datasets);
  the declared-to-fail POD+ridge control BEAT the scored arm on allen_cahn;
  blend bimodal (lambda 1.00 fisher → 0.20 ifc); guard `heat_local` flagged
  structurally (6.24x copy-LF, condition-only regime).
- Part 6 findings (mechanism): T1-F2 out-of-fold identifiable rank is 1–3 on
  every panel dataset (helmholtz 5, pfc 2, allen_cahn 1, fisher 1,
  cahn_hilliard 3, ifc 1) while a 50-mode train POD basis represents the TEST
  fields to 0.0033–0.0672 — the basis is not the bottleneck; **T2-F1/T2-F2** a
  <=156-parameter closed-form head scored through the shipped protocol reaches
  panel geomean 19.0553 against the 15,878,402-parameter arm's 19.6444 (0.52x
  the panel mce, indistinguishable); **T2-F5** the ratio `||mean field|| /
  geomean ||y||` (helmholtz 4.210, allen_cahn 0.024, cahn_hilliard 0.052)
  orders a zero-parameter centering choice worth 3.82x on helmholtz; **T3-F8**
  six out-of-fold band gains close the decoder's advantage on 4 of 5 datasets
  (pfc 6.9%→0.06%, helmholtz→parity, allen_cahn/fisher already lost), zeroing
  all non-DC gains on every sharp dataset **except cahn_hilliard**;
  **T3-F5/F6/F7** pfc is two populations (44/100 test patterned, class
  predictable at OOF AUC 0.9998) and a 35-parameter DC-only ridge scores
  0.35020 — 8.8% better than the 14.4 M decoder and at the DC oracle to 6e-6
  on the patterned class.
- Part 7 (binding): `open_question` — is cahn_hilliard's surviving decoder
  advantage real? At the register turn's FULL 31-gain x 2-pass calibration the
  tiny head reached 0.55990 (skill 13.3937) vs the shipped 0.53686 (12.8425):
  **a 4.29% / 0.5511-skill gap = 6.0x cahn_hilliard's certified mce 0.09125**,
  with three named candidate mechanisms — (i) genuine representation value,
  (ii) arm-SET artifact (FACT-2 centering selected where the ratio is 0.052),
  (iii) rank starvation (cahn_hilliard is the one dataset with 3 identifiable
  modes and a 19-dim condition). `next_direction`: "Stop buying decoder
  capacity in this stream; spend B2 on IDENTIFICATION and CALIBRATION" —
  (1) select the scoreable-arm form by training-free statistics (centering by
  `ratio_meanfield_over_geoamp`, rank by identifiable-mode count, per-band
  out-of-fold shrinkage); (2) the DC-only arm is mandatory in the floor set;
  (3) any capacity claim must be made on cahn_hilliard against a
  BAND-CALIBRATED competitor; (4) do not repeat a single-seed panel-geomean
  threshold test — run 3 seeds or state per-dataset per-mechanism predictions;
  (5) reuse `worktrees/r2s1_direct/B1/scratchpad/reanalysis_turn_2.py`, and the
  two promoted tools `tools/band_gain_counterfactual.py`,
  `tools/condition_identifiable_rank.py`.

## 4. Cross-stream cards (light scan)

- `r2s4_diag/batch_1/B1.json` (complete) — certified `state/noise_floor.json`
  (3 seeds, family `r2s4_cert_min`), the per-dataset mce values this card must
  clear, and the aleatoric barriers; its own part 7 names cahn_hilliard +
  ifc_poisson as `no_support` for the barrier estimator. Its 3-seed per-dataset
  skills (147.3 allen_cahn, 47.85 pfc, 13.18 cahn_hilliard, 11.558 fisher,
  8.26 ifc, 6.94 helmholtz) are an unpaired cross-family reference only.
- `r2s4_diag/batch_2/B2.json` (drafted) — value-of-LF accounting (DOPD
  advantage-gap ported to fields) + HF-sample-count scaling; re-certifies the
  seed spread on its own arms and makes train-fold-calibrated shrinkage a
  required column. No overlap with a capacity-localization card; it measures
  LF value, this stream measures where capacity is worth anything.
- `r2s3_lf_train_signal/batch_1/B1.json` (analyzing) — **architecture tax**:
  "All three trained nets are near-affine maps of the condition vector"
  (relative L2 of net − its own affine surrogate: 0.0088 hf_only, 0.1917
  rung_native, 0.5737 rung_upsampled), and on ifc_poisson "27.7% of hf_only's
  own law energy sits in that one unconstrained direction, anti-aligned with
  the truth", against an architecture-free linear channel reaching skill
  0.2427. Directly relevant: any trained arm this stream ships can anti-align
  the directions the data does not constrain — a closed-form (min-norm /
  ridge) arm puts zero there by construction.
- `r2s2_stacked/batch_1/B1.json` (analyzing) — turn-2 F7 (quoted in B1 part 7
  cross-stream notes): the number of LF-field PCs learnable from the condition
  is 1 on pfc/allen_cahn/fisher and 3 on cahn_hilliard, matching the HF-side
  rank ladder measured here.

## 5. Reopen candidates

None. `experiment_cards/r2s1_direct/batch_1/B1.json` carries
`reopen_candidate: false`, and `brainstormer/r2s1_direct/batch_1/report.md`
line 211 records "(none — `experiment_cards/r2s1_direct/` contains no prior
card)". No prior card in this stream or any other stream is flagged for reopen.

## 6. What is UNKNOWN

1. **The one open cell of the panel: is cahn_hilliard's decoder advantage
   real?** B1 measured 0.5511 skill units = 6.0x the certified mce at one seed,
   but could not attribute it. The three named mechanisms are mutually
   exclusive and cheaply separable: (ii) centering — the tiny head's arm set
   selected FACT-2 where the ratio is 0.052, which the B1 part-7 rule itself
   says should be additive; (iii) rank — the closed form was capped at r <= 3
   on the ONE dataset with 3 identifiable modes and a 19-dim condition, so
   r = 3 may simply be the wrong cap; (i) is whatever survives after (ii) and
   (iii) are removed. Nobody has run the rank x centering sweep under band
   calibration.
2. **Is there a capacity ladder at all, or only two points?** Every comparison
   so far is 10^2 vs 10^7 parameters. Where a 10^3-parameter conditionally
   nonlinear head (RFF features on the condition) sits, and where a 10^5.6
   small decoder sits, is unmeasured — and it is exactly the per-dataset
   localization the E3 verdict says is unprescribed.
3. **Does the training-free selection rule actually pick the winner?** The
   centering rule is pre-registered from THREE measured ratios (4.210, 0.052,
   0.024); pfc, fisher_kpp and ifc_poisson ratios are unmeasured, so the rule
   is untested on half the panel. The rank rule's tau = 0.1 has never been
   varied. A rule that loses to its own alternative is not a contribution.
4. **How much of every arm's score is calibration rather than architecture?**
   B1 cross-stream note 2: "any stream comparing two arms without calibrating
   both is measuring shrinkage, not architecture." The uncalibrated-to-
   calibrated delta per arm per dataset has never been reported side by side.
5. **Does adding the DC-only ridge to the blend base set change the pfc
   number?** B1's blend chose lambda = 0.90 onto train_mean on pfc and scored
   0.38403, while a standalone DC-only ridge scored 0.35020. Whether the
   out-of-fold calibration would actually SELECT the DC base (rather than the
   test-side hindsight that it is better) is unknown, and it is the difference
   between a real rule and a post-hoc pick.
6. **Resolution.** B1's part-7 item 4 says a single-seed panel-geomean
   threshold is decided by noise. What is unknown is whether an in-job
   *paired* arm contrast (same folds, same test split, same job) is resolvable
   at one seed where an unpaired cross-family geomean is not — the drift-class
   rule says only in-job paired controls are controls at these sample counts,
   but no paired spread has ever been reported for this stream.
7. **What is NOT unknown and must not be re-asked**: whether a bigger/newer
   decoder architecture helps (T2-F1: 10^5 parameter ratio, 0.52x mce), whether
   phase information is recoverable on pfc (T3-F2: falsified, all arms at
   cos ~ 0), and whether identifiable-rank truncation is novel (presumed prior
   art — instrument only).
