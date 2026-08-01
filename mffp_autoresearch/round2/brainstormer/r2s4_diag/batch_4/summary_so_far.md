# Summary so far — Stream `r2s4_diag`, Batch 4

Every claim below traces to a file read during this invocation; paths are relative to
`mffp_autoresearch/round2/` unless absolute.

## 1. Websearch findings + prior-art verdict

Source: `websearches/r2s4_diag/batch_4/report.md` (5 iterations, cap respected; 15
WebSearch calls, 12 `urllib` page fetches + 2 NCBI eutils records; `WebFetch` disabled
in this environment).

Three candidate directions were assessed.

**Row A — ifc_poisson overfitting anatomy at N_hf in {5, 20, 50}** ->
`preempted-but-MF-composition-open`. Open column, verbatim:
> **No fetched source performs a train-vs-test error decomposition for a field-valued
> condition→HF surrogate at single-digit HF sample counts.** Also uncited: doing it in
> copy-LF-skill units against a *pre-certified* per-dataset min-claimable-effect, and on
> an explicitly non-nested ladder whose rungs are therefore independent designs.
> **NOT open**: the n_eff/effective-sample-size *diagnostic* (no usable results across
> two batches; demote to a descriptive statistic) and anything resembling a scaling law
> / sample-complexity extrapolation from 3 points.

**Row B — close the stream now (no B4)** -> `preempted (cite)`, "the weaker of two
published options": every fetched retirement source treats *saturation*, **none retires
a criterion for infeasibility**; futility stopping's published price is a quantified
type-II inflation that must be stated (Lachin 2005, PubMed 16134130).

**Row B-prime — close but ship the futility statement** -> `novel` in composition,
`preempted` in every component; explicitly "*a report artifact, not an experiment card*".

Binding instructions to me (report section "For the brainstormer"): (1) neither option is
decided by the verdict, but both *lazy* versions are killed; (2) if proposing A, the
sentence that survives refutation is the "no fetched source decomposes train vs test
error for a field-valued condition→HF surrogate at single-digit N" sentence; (3)
**pre-register an EQUIVALENCE test, not a significance test** — Harms & Lakens 2018
(PubMed 30873486), using the certified ifc MCE 0.9377041289531141 as the equivalence
bound, so an "unclaimable" outcome is itself a claim; (4) call the ladder NON-NESTED,
cite it (https://arxiv.org/abs/2407.17087, https://arxiv.org/html/2408.17075v2), treat
rungs as independent designs, do not present non-nestedness as a discovery; (5) forbid
three claims outright — scaling law / extrapolation from few points
(https://arxiv.org/abs/2103.10948), ceiling or information-gap claims at N_hf = 5
(https://arxiv.org/abs/2410.23440), and any `n_eff` *diagnostic*; (6) a non-monotone
ladder is a published phenomenon (https://arxiv.org/abs/2211.14061), pre-register that
reading; (7) if closing, close the B-prime way.

## 2. Section 12 conventions verbatim

Governing section for this stream, `program.md` 12.4, verbatim:

> ### 12.4 `r2s4_diag` (diagnostics)
>
> - **B1 is pre-directed**: floor + spread certification. (a) Verify the frozen
>   floors reproduce (standing zero-predictor column included); (b) train ONE
>   minimal condition→HF baseline (smallest reasonable FiLM-FNO decoder or
>   MLP→field) at smoke tier, seeds {0,1,2}, on the panel — its per-dataset
>   seed spread replaces the provisional `state/noise_floor.json` (§4.3).
>   Diagnostic card, but WITH training (3 seeds) — the exception is the point;
>   cheap by design (small model).
> - Later batches: **value-of-LF accounting** — matched architecture ± LF
>   training signal (coordinates with r2s3: r2s4 measures, r2s3 optimizes);
>   **overfitting anatomy** at N_hf ∈ {5, 20, 50} (ifc ladder) and N=400
>   (sharp): train/test gap decomposition, effective sample counts (the
>   **drift-class rule**: when n_eff/N < 1%, only in-job paired controls are
>   controls).
> - The round-1 probe library is seeded in `tools/` (37 files; index header
>   notes they were written against round-1 eval paths — adapt on use, promote
>   adapted versions via the register turn).

The dispatch message asked for a verbatim `12.2` quote; 12.2 governs `r2s2_stacked`, not
this stream. I read it as a typo for 12.4 (quoted above) and reproduce 12.2 verbatim as
well so the instruction is literally discharged:

> ### 12.2 `r2s2_stacked` (lever)
>
> - **B1 is pre-directed by the spec** (Eloise's stacking proposal): train a
>   FiLM-FNO **pseudo-LF emulator** (condition → LF field) on the TRAIN LF
>   data, feed the best round-1 corrector — the s6 DC lineage / s4-B3
>   `dc_cleaned` stage (r1 geomean 0.1233–0.19 under OLD denominators; restate
>   under corrected before claiming). Arms: **frozen corrector / fine-tuned
>   corrector / end-to-end**, to separate emulator error from distribution
>   shift (the corrector was trained on real LF; pseudo-LF is
>   off-distribution for it).
> - Declared-reuse rule (§5.10a): the corrector is a frozen test-time
>   sub-component — the reuse IS the experiment. Its code lives in the round-1
>   worktrees (`round1/worktrees/s6_local/B2`, `round1/worktrees/
>   s4_hybrid_routing/B3/models_r1/s4_router/`); vendor the needed pieces into
>   the round-2 family dir with provenance comments (round-1 branches are
>   immutable).
> - Round-1 mechanism rules apply to the cleaning stage: **BC-match rule**
>   (eligibility decidable training-free; audit tool
>   `tools/spectral_prestage_bc_audit.py`), the **wrap-seam caveat** (part of
>   dc_cleaned's pfc credit was a boundary-rim artifact of the DEFECTIVE
>   reference — under the corrected reference that credit may vanish; the
>   s4-B3 H4 finding says deep-bulk ratio was 0.908 on pfc), and the
>   **lineage-bound caveat** for any routing/eligibility rule.
> - Failure is informative: if pseudo-LF → corrector loses to r2s1's direct
>   models, the LF representation is not a useful bottleneck — that is the
>   stream's falsification framing.

Also binding from the section-12 preamble (ADR r2-0004): the
**registration-of-model-side-lifts** rule (any family or instrument code that resamples
a field between grids MUST use the ADR r2-0001 per-dataset conventions — vendor from
`eval/panel_data.py` or use `factory_mffp/models/_common/lf_registration.py`; a bare
`F.interpolate`/`zoom` is a reviewer FAIL) and the **target-scaler pre-flight** rule
(applies to `ext__helmholtz_2d` / `sharp__phase_field_crystal_2d` only — N/A for an
ifc-only card, stated explicitly on the card).

## 3. Within-stream prior cards

`experiment_cards/r2s4_diag/batch_{1,2,3}/B{1,2,3}.json`, all `status: complete`, all
`card_type: diagnostic`, all `anchor_reference: null`, all `reopen_candidate: false`
(verified by reading each JSON).

- **B1** — floor + seed-spread certification. Family `r2s4_cert_min` (condition-only
  FiLM-FNO decoder, width 32 / 2 blocks / 16 modes / FiLM-MLP 64, ~1.06M params, AdamW
  1e-3, wd 1e-5, batch 16, cosine, clip 1.0, MSE in `train_zscore_global`, 200 epochs,
  seeds {0,1,2}). Produced `state/noise_floor.json` (certified, `_provisional: false`)
  and the stream anchor `certified_3seed_panel_geomean = 19.817844731907492`. Its ifc
  per-seed skills were 7.941161869912803 / 8.878865998865917 / 7.963632734399563, mean
  **8.261220201059428**, `min_claimable_effect` **0.9377041289531141**. Part 7 names the
  two blind spots: **B1's training-free ceiling estimator had NO SUPPORT on
  `sharp__cahn_hilliard` (19 condition dims) or `ifc_poisson` (5 train rows)**.
- **B2** — value-of-LF accounting (DOPD advantage-gap ported to fields) + HF-sample-count
  scaling. Closed the target-side channel (|T1−T0| inside its operative threshold in
  15/15 dataset x N cells). Found (T2-F6) that on ifc_poisson **0 % of rows pair to their
  nearest condition under the `lf[:n_hf]` rule** — the ladder is unpairable, so B2 scoped
  ifc out of every LF-paired arm. Runtime 17.2 min/seed on h200.
- **B3** — teacher-projection channel ledger. Closed the input-side channel: the LF
  teacher's advantage is realisation information, ~100 % unreachable from the condition
  (reachable component +0.0020 to +0.0038 skill units against thresholds 50–90x larger).
  `ifc_poisson` carried **NO LF-paired arm** (`R2S4B3_IFC_MODE=primary_t0_only_anecdote`),
  only the primary T0 leg, labelled anecdote-grade. Promoted
  `tools/ledger_contamination_audit.py` and `tools/band_retention_probe.py`, plus the
  mis-specification rule (control column / matched n_fit / ceiling-before-threshold).
  Runtime 92 min (dispatch note) — the envelope for this batch.

**B3 part 7 (the B4-or-close input), key clauses verbatim**: "no fourth diagnostic is
warranted ON THE SHARP PANEL, and one is defensible on ifc_poisson only"; "B3's spectral
result … bounds what any stream can produce at test on the sharp panel"; "WHAT WOULD
change an action is the stream's one un-executed mandate: program.md 12.4 assigns r2s4
the 'overfitting anatomy at N_hf in {5, 20, 50} (ifc ladder) and N=400 (sharp)' and no
batch has run it"; and the counter-argument — "at N_hf = 5 the drift-class rule (12.4)
means only in-job paired controls are controls, the certified min_claimable_effect is
0.9377041289531141 against a per-dataset skill of 7.94, and B2 already showed the ladder
is unpairable there — so a B4 on ifc_poisson has a real risk of returning 'unclaimable'
rather than an answer". Recommendation: "close the stream unless the maintainer judges
criterion 1 (ifc_poisson at the paper bar) still reachable by another stream, in which
case run ONE ifc-ladder card scoped to N_hf in {5, 20, 50} with the in-job paired
protocol and a pre-registered 'unclaimable' outcome."

## 4. Cross-stream cards

- **`r2s3_lf_train_signal-B3`** (`status: complete`; part 5 read in full for ifc):
  matched budget-equal +/-LF contrast at N_hf = 5, 33 legs, job 66196690, 54.95 min. On
  `ifc_poisson`: arm `A0_nolf` skill **8.13438381993564** (nRMSE 0.29283781751768306) vs
  arm `A1_lf_cov` skill **2.150091575784423** (nRMSE 0.07740329672823923); effect
  5.984292244151218 skill units against `operative_threshold_max_mce_spread`
  0.9377041289531141, `F1_pass_operative_threshold: true`,
  `relative_effect_1_minus_skillA1_over_skillA0` 0.7356786176581677. One training seed;
  the "draws" are HF-subset draws, ifc is `native` (single draw, `ci95: null`). Both arms
  beat the best in-regime n=5 floor. **This is the round's live criterion-1 leg and its
  most striking number: LF-as-training-signal moves ifc from 8.13 to 2.15 skill, i.e. to
  2.15x the published paper bar 0.036.**
- **`r2s2_stacked-B3`** (`status: drafted`, in build): zero-gradient stage attribution,
  `datasets: panel` so it carries an ifc leg; B3 part 7 note (a) targets it with the
  mis-specification rule (control column, matched `n_fit`, triangle-inequality headroom).
- **B3 part 7 note (c)**: `r2s1_direct-B3`'s helmholtz dump is identically zero — not
  this stream's call, recorded only.

## 5. Reopen candidates

**None.** All three r2s4_diag cards carry `reopen_candidate: false` and
`skipped_reason: null` (read back from the JSONs). Nothing to resolve.

## 6. What is UNKNOWN

**(a) Is ifc_poisson at N_hf = 5 sample-limited or architecture-limited?** The single
largest measured hole in the round. B1's training-free ceiling estimator had no support
there; B2 scoped it out of every LF-paired arm (0 % pairable); B3 carried it as
`primary_t0_only_anecdote`. **Nobody has measured the TRAIN error at all** — every ifc
number in the round is a test number. The train/test gap at N = 5 is one cheap training
run away and it separates "the model memorises 5 fields and cannot generalise"
(variance/sample-limited) from "the model cannot even fit 5 fields"
(bias/architecture-limited). Those imply opposite next actions for r2s1, r2s2 and r2s3.

**(b) What does the ifc ladder actually look like on disk, and what does {5, 20, 50}
mean?** Verified directly against `stripped_data/ifc_poisson`:
`train/fidelity_64` = (5, 64, 64), `train/fidelity_32` = (20, 32, 32),
`train/fidelity_16` = (50, 16, 16), `train/fidelity_8` = (100, 8, 8);
`test/fidelity_64` = (128, 64, 64) and **no test LF at any rung**. So 12.4's
"N_hf ∈ {5, 20, 50}" is *not* three HF sample counts on one grid — it is three rungs at
three resolutions with independently drawn conditions (B2 T2-F6: 0 % pairable). There is
no 20-sample or 50-sample 64x64 training set, and creating one is forbidden (immutables
1 and 11). **A literal N_hf sweep on the scored grid is impossible; the mandate must be
re-expressed.** I found no prior card that states this, and it is the fact that most
constrains the design.

**(c) Can the marginal value of an HF sample be measured at all here?** Yes, and nobody
has tried: with 5 rows there are exactly 31 non-empty subsets, so an *exhaustive*
n in {1..5} curve is computable with zero sampling error in the subset dimension, and the
120 nested chains S1 c S2 c ... c S5 give a genuinely paired in-job delta distribution at
zero extra training cost — precisely the "in-job paired controls are controls" the
drift-class rule demands, on a card that stays strict-1-seed. Whether the resulting CI is
narrower than the certified MCE 0.9377041289531141 is unknown and is the card's real risk
— which is exactly what the equivalence framing converts from a dead end into a claim.

**(d) How much of r2s3-B3's 5.98-skill-unit LF effect is "more effective samples"?**
Unknown, and it decides whether the round's headline ifc claim is an LF claim or a
sample-count claim in disguise. It is boundable without any extrapolation: if the whole
n = 1..5 condition-only envelope sits above `A1_lf_cov`'s 2.150091575784423 by more than
the MCE, then no HF sample count in the accessible range reproduces what LF bought.

**(e) Does the condition→field map on this PDE become learnable at larger N at all?**
Unknown. The lower rungs carry 20 / 50 / 100 samples of the *same* 5-dim condition family
at coarser resolutions. A within-rung generalisation-gap measurement (never mixing rungs
— mixing is r2s3's lever, already run) answers "does a 20x larger design close the gap on
this PDE?" without a single cross-grid interpolation and without any nestedness
assumption. This is the decisive, non-extrapolating re-expression of the 12.4 mandate.

**(f) Known-and-NOT-open, recorded so the design cannot drift into them**: `n_eff` as a
diagnostic (two batches of dead ends; demote to descriptive coverage statistics); any
ceiling / information-gap claim at N_hf = 5 (batch-1/2 binding,
https://arxiv.org/abs/2410.23440); any scaling law fitted to a few-point curve
(https://arxiv.org/abs/2103.10948); non-nestedness as a discovery (published:
https://arxiv.org/abs/2407.17087, https://arxiv.org/html/2408.17075v2); and any claim
resting on cross-rung interpolation without the ADR r2-0001 convention.
