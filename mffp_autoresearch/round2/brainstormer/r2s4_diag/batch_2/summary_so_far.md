# Summary so far — Stream `r2s4_diag`, Batch 2

## 1. Websearch findings + prior-art verdict

Source: `websearches/r2s4_diag/batch_2/report.md` (5 iterations, CAP HIT; 15 WebSearch,
13 WebFetch / 9 usable).

Verdict rows (verbatim, `## Prior-art verdict`):

- **D1** — value-of-LF accounting: `preempted-but-MF-composition-open (cite)`.
  "Nothing found pre-registers the null datasets **from a measured training-free ceiling**,
  nor uses LF *fields* as privileged info for a *field-valued* output scored in copy-LF
  skill. Concrete adoptable design: DOPD's advantage-gap split (capability gap vs
  information gap) ported to fields." (Citations quoted in full in `report.md`.)
- **D2** — ceiling estimator at 19 dims / N_hf=5: `preempted (cite)`. "The 19-dim failure
  is a **known theorem-level property**, not a bug... At N_hf = 5, arXiv:2410.23440 says no
  ceiling claim is defensible."
- **D3** — shrinkage / lambda*: `preempted-but-MF-composition-open (cite)`. "**lambda\* as a
  reported diagnostic statistic** ... was not found"; FALCON needs ~1000 calibration points.
- **D4** — overfitting anatomy / n_eff: `preempted-but-MF-composition-open (cite)`,
  upgraded LOW->MEDIUM. "Still no PDE-domain **n_eff estimator** after two batches — if
  B2/B3 uses one it must define it locally and say so."

Binding "For the brainstormer" instructions: (1) D1 is "an adjudication, not a hunt for a
gain" — write the null as the pre-registered expectation; (2) adopt DOPD's advantage-gap
design; (3) **do not propose "build a ceiling estimator"**; (4) sell lambda*, not the
shrinkage, and quantify the small-calibration-fold uncertainty; (5) quote arXiv:2410.23440
for ifc_poisson's N_hf=5 column; (6) define n_eff-like statistics locally as project
conventions; (7) **re-certification is owed** — B1's constants under-state a less-collapsed
successor's noise.

## 2. program.md 12.4 conventions (verbatim)

> ### 12.4 `r2s4_diag` (diagnostics)
>
> - **B1 is pre-directed**: floor + spread certification. (a) Verify the frozen floors
>   reproduce (standing zero-predictor column included); (b) train ONE minimal
>   condition->HF baseline (smallest reasonable FiLM-FNO decoder or MLP->field) at smoke
>   tier, seeds {0,1,2}, on the panel — its per-dataset seed spread replaces the
>   provisional `state/noise_floor.json` (§4.3). Diagnostic card, but WITH training (3
>   seeds) — the exception is the point; cheap by design (small model).
> - Later batches: **value-of-LF accounting** — matched architecture ± LF training signal
>   (coordinates with r2s3: r2s4 measures, r2s3 optimizes); **overfitting anatomy** at
>   N_hf in {5, 20, 50} (ifc ladder) and N=400 (sharp): train/test gap decomposition,
>   effective sample counts (the **drift-class rule**: when n_eff/N < 1%, only in-job
>   paired controls are controls).
> - The round-1 probe library is seeded in `tools/` (37 files; index header notes they
>   were written against round-1 eval paths — adapt on use, promote adapted versions via
>   the register turn).

Also binding: §1 criterion 1 ("a matched with/without-LF-training contrast (same
architecture, same budget) with a claimable effect on at least 3 panel datasets");
§2.2 mandatory floor arms; §5.9 stripped test view; §5.11 no new HF data / no LF-only
pools.

## 3. Within-stream prior cards

`experiment_cards/r2s4_diag/batch_1/B1.json` (`status: complete`,
`falsification_verdict: confirmed`, `reopen_candidate: false`). Anchor upgraded to
`certified_3seed_panel_geomean` **19.817844731907492** (`state/anchors/r2s4_diag.json`),
superseding the training-free floor 23.063616857615774.

Certified per-dataset mean skill / `min_claimable_effect` (`state/noise_floor.json`,
`_provisional: false`): helmholtz 6.9438 / **2.95299**; ifc_poisson 8.2612 / **0.93770**;
allen_cahn 147.3154 / **0.87970**; cahn_hilliard 13.1781 / **0.09125**; fisher_kpp
11.5582 / **0.00071**; pfc 47.8472 / **0.21303**; panel geomean 19.8178 / **1.14187**.

Part 6 mechanism findings that drive B2:

- **T2-F1/T2-F2**: the certifier sits at **1.010x (fisher_kpp)**, **1.139x (pfc)** and
  ~1.11x (allen_cahn) of two independent training-free aleatoric barriers (11.4467/11.4407;
  42.0959/38.6210; 132.6551) -> information-excluded.
- **T2-F3**: **helmholtz is the only certified headroom** — 1.655x the LOO k-NN bound
  (6.1725 vs 3.7287), 2.34x the pair extrapolation (2.6383).
- **T2-F5**: cahn_hilliard (`d_min` 2.8222 in 19 dims) and ifc_poisson (5 train samples)
  admit **no** training-free aleatoric estimate — `no_support`.
- **T3-F1**: test-fitted shrinkage oracle lambda* = 0.0 on helmholtz (6.1725 -> 3.5214),
  1.0 on pfc/allen_cahn/fisher_kpp, 1.1 cahn_hilliard.
- **H5**: "A seed spread measured on a COLLAPSED model is not a general noise floor...
  the constants are usable as a floor for THIS family and are a **LOWER bound** for any
  less-collapsed successor."
- **H8**: "The value-of-LF contrast r2s4-B2 owns should be posed where headroom exists...
  helmholtz — 66% headroom, and a failure of AIMABILITY rather than of information — is
  where a with/without-LF contrast can actually resolve."

Part 7 `next_direction` (four owed items): (1) pose the contrast **on helmholtz first**,
fisher/pfc/allen_cahn as **pre-registered NULL datasets**; (2) a ceiling estimator at 19
dims / N_hf=5 — *the batch-2 websearcher has since ruled this out as a build target*;
(3) make **train-fold-calibrated shrinkage a REQUIRED arm**; (4) **re-certify the seed
spread on whatever arm B2 actually compares**. Promoted tools already on disk:
`tools/condition_predictability_ceiling.py`, `tools/conditional_mean_collapse.py`.

## 4. Cross-stream cards (light scan)

All three sibling B1 cards are `status: analyzing`, `7_gap_and_future: null`,
`reopen_candidate: false`; numbers below are from `5_actual_result` / `6_analysis` and
`state/maintainer_report.md`.

- **r2s1_direct-B1** — `6_analysis` **I1 (high confidence)**: "THE ARCHITECTURE IS NOT THE
  BINDING CONSTRAINT... the condition determines 1-3 out-of-fold degrees of freedom per
  dataset, and a <=156-parameter closed-form head... reproduces the panel geomean to within
  half a min_claimable_effect" (19.0553 vs 19.6444; parameter ratio 1.0e5). **I4**: the
  scored quantity "rewards predicting less, and correctly chosen centering".
- **r2s2_stacked-B1** — the stack adds ~nothing on the 5 paired panel datasets
  (emul_only 19.1863 -> frozen 19.1843, delta 0.002, inside the 1.1419 floor); the
  24.68->14.08 headline is entirely the ifc_poisson column (`attribution.valid=false`).
  Sidecar S2: a **real-LF** corrector reaches nRMSE **1.7e-7 - 5.9e-3** vs pseudo-LF
  0.24-0.46 — with the real LF field present the HF field is essentially determined.
- **r2s3_lf_train_signal-B1** — `cratered`/`falsified`. Panel `rung_native` 25.3919 vs
  `hf_only` 26.8687; on ifc_poisson 16.7963 vs 9.4466 — a **-7.3497 skill-unit sign
  inversion**, 7.8x the certified ifc floor 0.93770, harmful direction. Mechanism leads:
  mesh-scaled ladder / per-rung scaler.

## 5. Reopen candidates

**None.** All four round-2 cards carry `reopen_candidate: false` (verified by reading each
`experiment_cards/{stream}/batch_1/B1.json`); batch 1 was the round's first card wave, so
no candidate has ever been raised in this stream.

## 6. What is UNKNOWN

1. **The round's own criterion-1 quantity has never been measured.** No card has run a
   matched +/- LF-training contrast. r2s3-B1 ran an LF-training arm but not matched: it
   changed the sample set (extra ladder rungs) and the normalization simultaneously, and
   cratered. So "what is LF worth as a training signal" is, at batch 2 of ~3, still
   unmeasured — and r2s4 owns it (program.md §1 criterion 1, §12.4).
2. **Where the LF information goes.** Two facts are now certain and unreconciled: LF
   *contains* almost everything (r2s2 S2: real-LF corrector at 1.7e-7-5.9e-3), and
   condition->HF is stuck at 1.01-1.14x an aleatoric barrier on three datasets. Nobody has
   measured how much of the LF information can cross a condition-only bottleneck. That
   fraction — not a win — is the missing number.
3. **Whether the effect is sample-limited or information-limited.** r2s1-B1 says the
   condition determines only 1-3 identifiable DOF at N=400; r2s4-B1 says the model is at
   the barrier. Both imply zero headroom for LF *at N=400*. Neither says anything about
   N=20 or N=5 — and ifc_poisson (N_hf=5) is exactly where r2s3-B1 saw the only large
   effect. The N-dependence of the value of LF is completely unmeasured.
4. **Whether an LF-ablation instrument can see anything at all here.** A null is
   uninterpretable without a positive control. No card has ever run one.
5. **Whether the certified constants survive a less-collapsed arm** (B1 H5 / part 7 item
   4). fisher_kpp's 0.00071 is certainly too small for an arm carrying an auxiliary head.
6. **Whether train-fold-calibrated shrinkage is certifiable at n<=40** (B1 part 7 item 3
   vs FALCON's ~1000-point requirement). lambda* has only ever been fitted on TEST (an
   oracle), so its deployable value is unknown.
7. **cahn_hilliard and ifc_poisson remain the round's blind spot** — genuine prediction
   (R 0.52 / 0.25) with no estimable ceiling. The batch-2 websearcher closes the door on
   building an estimator; the open route is a *relative* measurement (LF present vs
   ablated) that needs no absolute ceiling.
