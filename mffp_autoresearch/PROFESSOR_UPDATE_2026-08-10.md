# MFFP Autoresearch — Update for Mentor (Round 3, Batch 1 Close)

Date: 2026-08-10. Author: Eloise (with the autoresearch orchestrator).
Authoritative sources: `round3/state/orchestrator_flow.md` (decision log), `round3/state/gates.md`, per-experiment cards under `round3/experiment_cards/`, `round3/index.md` (dashboard).
Companion to the 2026-08-02 update (round-2 results and the benchmark-repair pipeline are described there and are not repeated).
Updated 2026-08-10 (evening): batch-2 midpoint results and the ADR r3-0006 scoring change are in §6.

Rendered versions of this update:
[Claude artifact](https://claude.ai/code/artifact/a03c7fd2-cf39-42d6-8ec5-cf5ee44449cc)
(private until shared from its share menu) ·
[`PROFESSOR_UPDATE_2026-08-10.html`](PROFESSOR_UPDATE_2026-08-10.html) (same page, in-repo).
Companion decision page for §5.1: [ADR r3-0005 decision memo](https://claude.ai/code/artifact/df42daf9-e82d-4746-93f0-fe06e1b93e08).

## TL;DR

- **Round 3 launched on 2026-08-05 on the repaired benchmark; batch 1 closed with four experiments, each run at 3 random seeds.**
  All four models beat the no-training reference error of 34.4198.
  Their geometric-mean normalized errors across the evaluated datasets range from 11.08–24.96, and lower is better.
- **The system detected and stopped work for two benchmark-integrity failures.**
  First, the evaluated phase-field-crystal (`pfc`) task contained essentially no fidelity gap because the coarse solution was already spectrally converged to the fine solution.
  The reported reference error was therefore ~100% interpolation error introduced by our evaluation.
  We made `pfc` report-only and reduced the evaluated set to 5 datasets (ADR r3-0004).
  Second, an audit found that several baseline models had been evaluated on repaired data without being retrained.
  Mandatory checkpoint resumption had silently skipped training.
  We quarantined and retrained 32 individual runs, rebuilt the baselines, and added a permanent check to every baseline build.
- **The apparent 10.1% benefit from low-fidelity data during training was entirely caused by the stale baselines.**
  The original result also claimed a 39% improvement on `ifc_poisson`.
  After baseline repair, no dataset in that experiment has a resolvable change relative to its baseline.
  The panel change is −0.81%, only 0.08× the certified minimum detectable effect.
  The experiment still provides a valid decomposition of the mechanism.
- **The mechanism tests replaced two preregistered explanations with better-supported ones.**
  The factorised output head succeeds when the first-stage residual saturates, not when the condition vector has a particular dimension.
  The benefit of initial-condition information arises entirely in stage 1.
  The corrective second stage again has no detectable effect.
- **The audit experiment established the round’s minimum detectable effects and measured the reliability of the audit tools.**
  One checkpoint-staleness heuristic found 0 unique true positives but raised 62 false alarms across 859 individual runs.
  We are replacing it with content hashes stored in checkpoints.
- **Batch 2 is designed, reviewed, and now launching.**
  The first two cluster jobs start today.
  Searches in 7 research directions found no basis for outright novelty claims, so each experiment claims only its measured composition.
- **ADR r3-0005 was ratified on 2026-08-10 with option A.**
  The evaluated `pfc` task will use the coarsest available input resolution and a spectral reference.
  This is the round’s only amendment to the frozen round-2 evaluation convention.
  Phase 1, the serving change, is complete.
  Phase 2, the reference amendment and re-evaluation that restore the 6-dataset panel, waits until batch-2 computation closes so no active experiment uses mixed reference hashes.
- **Batch-2 midpoint (§6): the first batch-2 experiment is already complete and falsified its own novelty claim** — the calibrated selection rule loses to the plain cap fix it was registered against, and that stream now recommends its own consolidation.
  The audit stream's new fairness probe fired as pre-registered, exposing a resolvable reference-fitting bias on one dataset; escalated to the operator per its clause.
- **Scoring change (ADR r3-0006, operator decision): the headline denominator moves from copy-the-coarse-solve to the best learned baseline** (`mf_fno_transfer_film`).
  The change is an exact per-dataset conversion — nothing is re-scored, the frozen evaluation layer is untouched, and in-flight verdicts stay in their registered units; the baseline's own 3-seed certification is running.
- **Two new figures summarize performance and architectures.**
  They are `round3/docs/figures/r3_performance_vs_baselines.png` and `r3_architectures_overview.png`.
  Both are regenerated from the experiment records by `round3/tools/render_round3_update_figures.py` and embedded in the rendered page.

## 1. What round 3 asked, and how it ran

**The learning regime is unchanged from round 2.**
Models receive low-fidelity (LF) fields during training but only the condition vector at test time.
The test interface physically excludes LF fields.

**The repaired benchmark now provides complete condition vectors and corrected fidelity hierarchies.**
Initial-condition coefficients are included in the condition vector, which retires the stochastic-map caveat from ADR r2-0003.
The nested `ifc` fidelity hierarchies are repaired.
`ifc_heat` is now evaluated in the scored panel.

**The evaluated set contains 5 datasets after ADR r3-0004.**
They are `allen_cahn_2d`, `fisher_kpp_2d`, `cahn_hilliard`, `ifc_poisson`, and `ifc_heat`.
`helmholtz` and `pfc` are report-only.

**Batch 1 covered four experiment lines: factorised heads, initial-condition reach, the value of LF training data, and benchmark auditing.**
All 4 experiments closed at 3 seeds.
The round also produced 5 architecture decision records and promoted 7 new diagnostic tools.
A stop-the-line repair consumed ~2 days.
Every experiment followed the full sequence of literature search, preregistration, implementation, adversarial review, GPU execution, and two-stage analysis.

**The round now has certified minimum detectable effects.**
The batch-1 audit experiment (`r3s4-B1`) established per-dataset `seed_mce`, `tau_rel`, and `tau_abs`.
These denote the seed-based minimum claimable effect, its relative threshold, and its absolute threshold.
The geometric-mean `seed_mce` across the panel is 0.5083.
These thresholds were installed on 2026-08-10 and govern every claim below.

## 2. Round 3 batch-1 results (condition vector → HF; no solver at test)

**How to read the verdicts.**
CONFIRMED means the experiment's pre-registered prediction passed its threshold at 3 seeds.
FALSIFIED means the pre-registered prediction failed its threshold; because every prediction is registered before the run, a falsification is a finding, not a process failure.
CERTIFIED is the strongest label: measured at 3 seeds and priced against the audited minimum-detectable-effect table.
"Not resolvable" means the measured difference is smaller than the certified minimum detectable effect, so no claim is made either way.

Leaderboard (3-seed geometric mean of normalized error across the panel, lower is better; no-training reference 34.4198):

| Rank | Card | Panel geomean [3-seed range/CI] | Verdict | What it is |
|---|---|---|---|---|
| 1 | r3s3-B1 LF-channels | **11.0789** [10.84, 11.25] | confirmed (mechanism card) | Compute-matched comparison with and without LF training data; **no resolvable change from the repaired baseline**; the decomposition is the result |
| 2 | r3s2-B1 IC-stack | **12.9556** [10.32, 17.83] | F1 confirmed / **F2 falsified** | Initial-condition information helps in stage 1; the corrective stage is unresolvable, replicating round 2’s null result |
| 3 | r3s4-B1 certifier | **19.6438** [19.42, 19.93] | F2–F4 confirm; F1 fired at metrology margin | Source of the round’s certified minimum detectable effects |
| 4 | r3s1-B1 two-stage factorised head | **24.9573** [24.87, 25.07] | confirmed (L1/L2/L4) | Closed-form condition-to-coefficient cascade; the improvement occurs only on `cahn_hilliard` |

**The factorised head is distinguished by first-stage residual saturation, not condition dimension.**
`allen_cahn` and `cahn_hilliard` both have condition dimension 19, but their stage-2 margins differ 47×.
`fisher_kpp` has the largest condition dimension, 50, and the smallest margin.
The decisive quantity is the predictable energy left after stage 1.
On `fisher_kpp`, a hyperparameter limit causes the loss relative to an affine reference.
Specifically, `SELECT_MAX = 32` excludes 0.0713 of the condition-reachable energy.
Within the selected subspace, the head is better than the affine reference.
Its loss outside that subspace is 17× larger.
The `cahn_hilliard` improvement is broad rather than driven by outliers.
It improves 78–82 of 100 rows and remains 2.9–3.2× above the certified minimum detectable effect after adversarially removing 10 rows.

**Initial-condition information helps entirely through stage 1, and the remaining error is limited by approximation.**
The fractions of emulator error removed are 63.7% for `allen_cahn`, 22.3% for `cahn_hilliard`, and 85.4% for `fisher_kpp`.
A control given a fake, information-free initial condition performs worse than a control given no initial condition at all, on every dataset.
The benefit therefore comes from the information in the real initial conditions, not from the extra input channel.
The remaining `cahn_hilliard` gap is an approximation problem.
Even its nearest training neighbor in condition space is 98% as different as a randomly chosen sample.

**The corrective second stage is decisively ineffective for the second consecutive round.**
The best two-stage variant improves over its own front-end-matched emulator-only control by 9–163× less than one minimum detectable effect.
Round 2’s null result of 0.0061 replicates at 0.0056 [0.0053, 0.0061].
The one dramatic failure was `ifc_poisson` seed-2, with nRMSE 2.04 versus 0.15.
A deterministic measurement defect caused it.
An unregularised spectral Wiener transfer was fitted from **3** samples and amplified the signal 66× in a frequency band where the LF input has no power.
This is the same failure mode as round 2’s baseline instability.
The same audit tool flags the `pfc` baseline runs and the `fluid` guard dataset.

**LF training data helps by supplying identifiable condition–response pairs.**
A control receiving extra LF data only at conditions already covered by HF data learns the same function as the no-LF variant.
Their function-distance ratios are 0.098–0.307.
New, distinct condition rows explain E_cov/E_total ∈ [0.972, 1.024] in 30/30 evaluated cases.
Recovery is nearly deterministic given the measurable condition–response alignment, with Pearson r = 0.985.
Batch 2 tests whether this mediator yields a stable exchange rate between LF rows and HF rows.

**A seed-invariant hard subpopulation exists in `cahn_hilliard`.**
It contains 27 of 100 test rows.
Their conditions are nearly indistinguishable from training conditions, with maximum gap 0.45σ and nearest-neighbor ratio 1.02.
Their fields are nevertheless 3.29× farther away.
LF training data specifically repairs this group.
It repairs 92 of the no-LF variant’s worse-than-zero rows and accounts for 97% of that comparison’s gain.

## 3. Benchmark-integrity findings (the part most relevant to the benchmark paper)

- **The evaluated `pfc` task contained essentially no fidelity gap.**
  On 2026-08-07, this triggered the first stop-the-line event.
  The evaluation convention selected the highest available LF resolution, `max(lf_fids)`, producing the 64²→128² task.
  The crystalline fields are band-limited below the coarse-grid Nyquist frequency.
  Consequently, the exact per-row copy error is ≤ 1.66e-6 on all 100 test rows.
  The certified reference error of 0.018257 was ~100% linear-interpolation error introduced by the fixed lifting operation.
  The real fidelity gap occurs at 32²→128², which the convention did not evaluate.
  The box-swap repair exposed this resolution-convention mismatch.
  We made `pfc` report-only and reduced the evaluated set to 5 datasets under ADR r3-0004.
  ADR r3-0005 provides the durable repair described in §5.
- **Checkpoint resumption silently invalidated a baseline re-evaluation campaign.**
  On 2026-08-08, this triggered the second stop-the-line event.
  Models being re-evaluated on repaired data resumed already-completed checkpoints.
  The records showed `resumed_from_step = 5000` and training times of 1.3–2.9 s.
  Pre-repair weights were therefore evaluated on post-repair arrays.
  Existing hash and reference-consistency checks all passed because the references were recomputed live while the weights remained stale.
  The failure affected the launch baselines for the `ifc_poisson` columns.
  Later audit tools found 18 affected individual runs for report-only `pfc`.
  All of round 3’s own experiment runs were clean, with 0/225 affected.
  We quarantined and retrained 32 individual runs.
  We then rebuilt the baselines, with changes confined to the contaminated columns.
  A permanent stale-checkpoint check now runs inside every baseline build.
  Fresh training improved every contaminated baseline, so the contamination had made experimental comparisons look better than they were.
- **The audit experiment measured the audit tools’ own accuracy.**
  The `train_seconds` checkpoint-staleness heuristic found 0 unique true positives and raised 62 false alarms across 859 individual runs.
  Checkpoint modification-time evidence strictly dominated it, so the heuristic is being deleted.
  File modification times cannot establish data identity because the repair copy preserved them.
  Only a content hash stored in the checkpoint can distinguish a training-invalidating data change from a harmless test-split trim.
  Current checkpoint-to-data hash coverage is 0/18.
  Building this mechanism is the batch-2 audit experiment.
- **Tolerance setting now rests on a measured numerical-precision limit.**
  The audit experiment’s F1 condition triggered at 1.106e-9 against a 1e-9 tolerance.
  This is ~70× below the variation introduced by the float64→float32 data-loading boundary.
  Per-dataset analysis in units of floating-point spacing shows that suitable tolerances range from 2e-9 to **0.31**.
  The upper value occurs for `sod_1d`.
  There, an exact-equality `std == 0` check amplifies one unit in the last place by 8.4e6×.
  The issue is confined to a guard dataset, and no released result is wrong.
  Batch 2 changes the contract by setting F1-class tolerances to max(1e-9, measured per-dataset band).
- **A reported minimum detectable difference of `mdd_scored = 0` means unobservable, not zero.**
  For both `ifc` datasets, this round cannot observe uncertainty in the reference itself.
  The resulting absolute threshold, `tau_abs`, is understated by ~2.15×.
  No current claim changes.
  Claims involving absolute error bars in the affected range remain authorized only by the certified constants.

## 4. How the harness itself is performing

- **Batch 1 completed all four experiment lines at 3 seeds in ~5 days.**
  Stop-the-line repair consumed ~2 of those days.
  Batch 2 progressed from literature search through brainstorming, preregistration, implementation, adversarial review, and first SLURM jobs in under a day.
- **Preregistration and minimum-effect thresholds prevented two false headlines.**
  They retracted the apparent −10.1% panel improvement from the LF-training experiment and the condition-dimension explanation from the factorised-head experiment.
  Adversarial reviews also caught substantive defects before submission.
  One falsification condition used the wrong statistic.
  One admission rule differed measurably from its preregistered description and was adjudicated before any result existed.
- **Certified and retracted results remain explicitly traceable.**
  Only results backed by the batch-1 audit certification are called certified.
  Every retraction is annotated in its experiment record with the historical numbers preserved.
  Searches across 7 batch-2 directions found 0-for-7 cases of outright novelty.
  Each experiment therefore claims only its measured composition.
- **The state-file design allowed the round to survive an orchestrator failure.**
  The launch orchestrator session died on 2026-08-08.
  A fresh session resumed losslessly from the state files.
  It executed the repair under the standing delegation while holding the stop-the-line decision for operator adjudication, as required by the global rule.
  It has run the round since.
  The cluster’s SLURM job-ID space also reset mid-round from 8-digit to 5-digit IDs.
  Job accounting was re-established, and old IDs still resolve.

## 5. Gated next steps

1. **ADR r3-0005, the `pfc` spectral-resolution repair, was ratified on 2026-08-10 with option A.**
   Eloise made the decision for the mentor.
   Phase 1 is complete, and phase 2 waits for batch-2 computation to close.
   The repair has two inseparable parts.
   First, serving `pfc` resolutions {1, 3} changes the evaluated task to 32²→128².
   At that resolution, the measured per-row gap is real, with mean 0.0124 and 0/100 task-void rows.
   Second, the reference that copies the LF field must use a `pfc`-specific spectral lift.
   A linear lift has ~0.07 error at 32²→128² and would again overwhelm the ~0.012 true gap.
   The repaired task remains dominated by outliers.
   Its top-5 rows contribute 38.8% of the denominator, and its minimum detectable change is **65.8%**.
   It therefore returns to the evaluated panel as an honest but low-resolution dataset.
   Every claim about it must exceed that minimum detectable change.
   One alternative is to keep `pfc` permanently report-only, which is conservative but removes the panel’s only stiff-map dataset.
   Another is to regenerate a higher-resolution hierarchy, which costs the most computation.
   The sweep suggests that the same convergence would recur one resolution level higher because crystal wavelength, rather than grid spacing, determines it.
2. **Batch 2 will complete 4 experiments through the SLURM and analysis pipeline.**
   The first two seed-0 jobs are running as of this update.
3. **ADR r3-0006 executes in phases**: denominator certification on the cluster now; converted reporting once `film_denominator.json` is built; batch-3 experiments register their predictions in the new units.
4. **The round-1 full runs of 2500 epochs remain on hold.**
## 6. Batch-2 midpoint (added 2026-08-10, evening)

- **Factorised head (r3s1-B2) — complete; falsified its novelty claim; the stream recommends its own consolidation.**
  The statistically calibrated shape-selection rule was pre-registered head-to-head against the plain "raise the cap" bug-fix, and the plain fix wins.
  What survives is a confirmed fisher_kpp improvement of 13.35 (1.30× that dataset's minimum claimable effect), attributable entirely to the cap fix.
  The input-space-expansion repair is now a certified null: worse than inert (3.62× the threshold), because widening the correction gate's input collapses it — 19 columns of pure noise collapse it identically, so input width alone explains the failure.
  The stream-closing measurement: on fisher_kpp, even a perfect predictor restricted to the model's 50 principal shapes (the oracle ceiling, 298.83) still loses to the 6-parameter affine reference (270.54).
  The basis, not the selection rule, is the binding constraint there; cahn_hilliard retains 26.8× of real headroom.
- **IC-stack (r3s2-B2) — complete at 3 seeds; falsified on exactly one clause (an instrument-acceptance leg), while the route comparison itself came out affirmative.**
  The pre-registered stack-vs-direct contrast holds at panel level: the stack beats the matched direct route by 1.62 (3.2× the minimum claimable effect, sign-stable at every seed) — though no single-dataset win is claimable, because both ifc datasets still lose the mandatory affine reference.
  The clause that fired is honest instrument accounting: with only 3 fitting samples, cross-validation chose zero regularisation in the frequency band that matters on ifc_poisson, so the repair was inert exactly where batch 1 blew up.
  The replication arm is the round's cleanest attribution: it reproduced batch 1's numbers within noise on every seed *including* the seed-2 blow-up, down to the identical amplification factor (66.219…), proving the repaired arms removed it via the band-limit and not via re-implementation drift.
  The stream's reference-to-beat improves from 12.96 to 10.09, recorded with the caveat that the card setting it is falsified on its own pre-registration.
- **Value-of-coarse-data (r3s3-B2) — the cost-curve experiment (150 training runs across a ladder of coarse-data budgets) is on the cluster.**
- **Audit (r3s4-B2) — the checkpoint-binding instrument passed its labelled-defect exam exactly** (every pre-registered detection count reproduced; zero false "retrain" verdicts), **and its fairness probe fired as pre-registered**: fitting reference baselines on 400 rows while scored models fit on 320 shifts cahn_hilliard's reference by 1.93× the minimum claimable effect.
  Per the clause this is escalated to the operator rather than silently absorbed; the proposed fix is a closed-form re-pricing of the affected batch-1 comparisons once the pricing stage lands (no re-runs needed).
- **Scoring change (ADR r3-0006, operator decision).**
  The headline score's denominator moves from "copy the coarse solve and enlarge it" to the best learned baseline, `mf_fno_transfer_film`.
  Because both scores are ratios to the same model RMSE, the switch is an exact per-dataset conversion: nothing is re-scored, the frozen evaluation layer is untouched, rankings within the panel are preserved, and in-flight batch-2 verdicts evaluate in the units their predictions were registered in.
  The trade-off is recorded in the ADR: the denominator becomes a trained, seed-dependent object, so its own 3-seed variance is certified and disclosed beside every converted number.
