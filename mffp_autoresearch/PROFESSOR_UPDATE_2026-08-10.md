# MFFP Autoresearch — Update for Mentor (Round 3: Batches 1–2 Closed, Batch 3 Running)

Date: 2026-08-10. Author: Eloise (with the autoresearch orchestrator).
Authoritative sources: `round3/state/orchestrator_flow.md` (decision log), `round3/state/gates.md`, per-experiment cards under `round3/experiment_cards/`, `round3/index.md` (dashboard).
Companion to the 2026-08-02 update (round-2 results and the benchmark-repair pipeline are described there and are not repeated).
Updated 2026-08-11: batch-2 close (§6), the panel decision and certified baselines (§7), and the batch-3 launch (§8).

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
- **Batch 2 closed on 2026-08-10: all 8 round-3 experiment cards from batches 1–2, across all four streams, are complete (§6).**
  The headline is the audit stream's checkpoint↔data binding instrument, which binds a checkpoint to its data in six distinct roles: CONFIRMED at 108/108 on a labelled-defect exam.
  It strictly dominates both whole-dataset hashes and wall-clock heuristics, and is now installed as a hard gate in every anchor build.
  Its one fired falsifier — the G5 fit-set seam — was re-analyzed and correctly re-priced in closed form.
  The operator adopted the correction; no verdict flipped, and every affected margin widened.
  The repaired initial-condition stack is the round's best model at 10.09 (0.72× the film-transfer baseline).
- **ADR r3-0005 (ratified 2026-08-10, option A) is now fully executed.**
  The evaluated `pfc` task now uses the coarsest available input resolution and an exact spectral reference.
  This is the round's only amendment to the frozen round-2 evaluation convention.
  Phase 2 completed after batch-2 computation closed: `pfc` rejoined the scored panel on the honest 32²→128² task, so no active experiment ever used mixed reference hashes.
- **Panel decision (ADR r3-0007; operator option C, 2026-08-10): `ifc_poisson` is demoted to report-only (§7).**
  Its condition→answer map is exactly linear, with an oracle affine residual of 5.4e-16.
  On this closed-form task, no learned model ever beat the copy-the-coarse-solve reference.
  `ifc_heat` stays scored: a follow-up check proved the film baseline's win there is real field structure, not offset calibration.
  The scored panel is now 5 datasets (4 sharp + `ifc_heat`); the best training-free floor becomes 53.2146 (lineage in `state/gates.md`).
- **Scoring change (ADR r3-0006, operator decision) executed: the headline denominator moved from copy-the-coarse-solve to the best learned baseline** (`mf_fno_transfer_film`).
  The change is an exact per-dataset conversion: nothing is re-scored, the frozen evaluation layer is untouched, and in-flight verdicts stay in their registered units.
  The denominator is now certified at 3 fresh seeds.
  An operator-requested ConvNeXt U-Net twin lands in a statistical dead heat with it (error ratio 0.9805, cross-seed range 0.94–1.04), so film stands (§7.2).
- **Batch 3 — the round's final batch — launched 2026-08-11 with 2 cards, both through independent code review (§8).**
  One tests whether a training-free surrogate can *predict* each dataset's sample-efficiency knee — the point beyond which more coarse training data stops helping.
  The surrogate's per-cell predictions were sealed (sha256 content hash + timestamp) before any training job ran, and a 4-rung training ladder now adjudicates them.
  The other bounds what the synthetic-coarse-field detour could ever buy, via a 5-rung ladder.
  Its oracle rung can never be deployed, because the test-time LF field physically does not exist.
  Round close is expected 2026-08-12/13, with a final leaderboard of all round-3 models against both learned baselines.
- **Four figures summarize the round: the leaderboard, the four experiment lines, and the models that beat the baseline.**
  They are `round3/docs/figures/r3_performance_vs_baselines.png` (the round-3 leaderboard — every certified model ranked against the film baseline, plus per-dataset bests on the 5 scored datasets), `r3_architectures_overview.png` (the four experiment lines), and `r3_model_detail_ic_stack.png` + `r3_model_detail_lf_channels.png` (the architectures that beat the learned baseline: the r3s2 initial-condition stack — one shared diagram for B1 and B2 with the batch-2 repair delta called out — and the r3s3 LF-trained multi-resolution FNO).
  All are regenerated from the experiment records by `round3/tools/render_round3_update_figures.py`, reflect the ADR r3-0007 panel, and are embedded in the rendered page.

## 1. What round 3 asked, and how it ran

**The learning regime is unchanged from round 2.**
Models receive low-fidelity (LF) fields during training but only the condition vector at test time.
The test interface physically excludes LF fields.

**The repaired benchmark now provides complete condition vectors and corrected fidelity hierarchies.**
Initial-condition coefficients are included in the condition vector, which retires the stochastic-map caveat from ADR r2-0003.
The nested `ifc` fidelity hierarchies are repaired.
`ifc_heat` is now evaluated in the scored panel.

**The scored set contains 5 datasets.**
Its membership changed twice during the round, each time through a recorded architecture decision record (ADR), never silently.
At batch-1/2 registration it was `allen_cahn_2d`, `fisher_kpp_2d`, `cahn_hilliard`, `ifc_poisson`, and `ifc_heat`, with `helmholtz` and `pfc` report-only (ADR r3-0004).
After batch 2 closed, ADR r3-0005 phase 2 restored `pfc` on its repaired 32²→128² task, and ADR r3-0007 demoted `ifc_poisson` to report-only (§7).
The current scored panel is therefore `allen_cahn_2d`, `fisher_kpp_2d`, `cahn_hilliard`, `pfc`, and `ifc_heat`; `helmholtz` and `ifc_poisson` are report-only.
Batch-1/2 numbers below are quoted in the units and on the panel they were registered with.

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

Leaderboard (3-seed geometric mean of normalized error across the batch-1 registration panel, lower is better; no-training reference 34.4198 on that panel — the current 5-dataset panel's floor is 53.2146, §7):

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
Batch 2 tested whether this mediator yields a stable exchange rate between LF rows and HF rows; it does not — the measured rate came out an order of magnitude below the registered prediction (§6).

**A seed-invariant hard subpopulation exists in `cahn_hilliard`.**
It contains 27 of 100 test rows.
Their conditions are nearly indistinguishable from training conditions, with maximum gap 0.45σ and nearest-neighbor ratio 1.02.
Their fields are nevertheless 3.29× farther away.
LF training data specifically repairs this group.
It repairs 92 of the no-LF variant’s worse-than-zero rows and accounts for 97% of that comparison’s gain.

### 2.1 The models that beat the baseline, in detail

Three certified models beat the learned baseline: the repaired batch-2 initial-condition stack (r3s2-B2, 0.72× film), the LF-trained multi-resolution FNO (r3s3-B1, 0.79×), and the original batch-1 initial-condition stack (r3s2-B1, 0.92×).
All share the deployment premise (condition in, fine field out, no solver at test), and all owe their standing to mechanism work rather than architecture novelty.
The two IC-stack entries are one architecture — batch 2 changes only the corrector's spectral filter — so the diagrams show two architectures, with the batch-2 repair delta called out on the shared IC-stack diagram.
Detailed diagrams: `round3/docs/figures/r3_model_detail_ic_stack.png` and `r3_model_detail_lf_channels.png` (Figs. 3-4 in the rendered page).

**The initial-condition stack (r3s2; B1 at 0.92× the film-transfer baseline, and — after the batch-2 repair — 0.72×, the round's best model).**
Stage 1 is a FiLM-conditioned Fourier neural operator (4 spectral blocks, width 64, 12 Fourier modes) that synthesizes the coarse field the solver would have produced, directly from the condition vector.
The condition enters every block as a learned affine modulation, so one network serves all conditions.
The certified per-dataset interpolation convention lifts the synthetic coarse field to the fine grid.
Stage 2 is a frozen local CNN corrector (7×7 kernels, depth 4, width 32) trained on real coarse→fine pairs in an earlier round; batch 2 added a cross-validated ridge plus a hard band-limit at the coarse grid's Nyquist frequency, repairing the one failure mode (a 66× spectral amplification fitted from 3 samples).
Training uses ~400 (condition → coarse field) pairs per sharp dataset; the fine fields never enter stage 1, and stage 2's weights never change — which is why the mechanism stage located a covariate shift there.
Established: the initial-condition information is the entire measurable effect and acts in stage 1; the corrector adds nothing resolvable (round 2's null replicates); the repair's attribution was proven by a replication arm that reproduced the old defect digit-for-digit; both ifc cells still lose to a 6-parameter affine fit (§7.1 explains how those affine floors are now quoted).

**The LF-trained multi-resolution FNO (r3s3's A1 arm, 0.79× the film-transfer baseline; best model on ifc_heat and fisher_kpp).**
One conditioned FNO (4 spectral blocks, width 64) with its Fourier modes pinned to the coarsest rung's Nyquist so every resolution shares one spectral basis, and per-rung output heads sharing the backbone.
Training minimizes a joint loss: predict the coarse solve at every rung AND the fine field, equally weighted, with ~400 coarse rows against as few as 5 fine rows.
At test only the fine head is read out; the coarse heads exist purely to absorb training signal.
The controlled arms (no coarse data / coarse data only at already-covered conditions / full pool) are what let the round attribute the effect: the value is supply of new condition points, not regularization — the covered-only arm learns the same function as the no-coarse-data arm.
Established: recovery tracks condition-response alignment at r = 0.985; the pre-repair −10.1% headline was retracted as a stale-baseline artifact; batch 2 confirmed the cost curve's knee at c\* = 80 distinct coarse conditions on cahn_hilliard (7.0× the clause floor) plus a training-free surrogate for it — the basis of batch 3's sealed-prediction card (§8).

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
  (Update: built and CONFIRMED at 108/108 in batch 2; it now runs as a hard gate inside every anchor build — §6.)
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

## 5. Decisions and next steps (statuses updated 2026-08-11)

1. **ADR r3-0005, the `pfc` spectral-resolution repair, is fully executed** (ratified 2026-08-10 with option A; Eloise made the decision for the mentor).
   The repair has two inseparable parts.
   First, serving `pfc` resolution levels {1, 3} changes the evaluated task to 32²→128².
   At that resolution, the measured per-row low-fidelity-to-high-fidelity gap is real, with mean 0.0124 and 0/100 task-void rows.
   Second, the reference that copies the LF field must use a `pfc`-specific spectral lift.
   A linear lift has ~0.07 error at 32²→128² and would again overwhelm the ~0.012 true gap.
   Phase 2 completed on 2026-08-10, after batch-2 computation closed, so no active experiment ever used mixed reference hashes: `pfc` is back in the scored panel with the exact spectral reference (0.012358), and all re-scored cells passed the stale-checkpoint gate.
   The repaired task remains dominated by outliers.
   Its top-5 rows contribute 38.8% of the denominator, and its minimum detectable change is **65.8%**.
   It is an honest but low-resolution dataset, and every claim about it must exceed that minimum detectable change.
   The rejected alternatives are recorded in the ADR: permanent report-only status (conservative, but removes the panel's only stiff-map dataset) and regenerating a higher-resolution hierarchy (most computation; the sweep suggests the same convergence would recur one level higher, because crystal wavelength rather than grid spacing determines it).
2. **Batch 2 completed all four experiments and closed on 2026-08-10** — results in §6.
3. **ADR r3-0006 is executed**: the film-transfer denominator is certified at 3 fresh seeds, converted reporting is live, and batch-3 experiments register their predictions in the new units.
   The certification and the operator-requested U-Net comparison are in §7.2.
4. **Batch 3 — the final batch — is running** (§8); round close is expected 2026-08-12/13 with the final leaderboard.
5. **The round-1 full runs of 2500 epochs remain on hold.**
## 6. Batch-2 close (updated 2026-08-11; supersedes the 2026-08-10 midpoint note)

All 8 round-3 experiment cards (batches 1–2, all four streams) are complete; every batch-2 card ran at 3 seeds through the full pipeline.
In the new film units, the round's standing after batch 2: r3s2-B2 at 0.72, r3s3-B1 at 0.79, r3s2-B1 at 0.92, r3s4-B1 at 1.40, r3s1-B1 at 1.77, and r3s1-B2 at 1.78 (the round-3 leaderboard, Fig. 1).

- **Factorised head (r3s1-B2) — complete; falsified its novelty claim; the stream recommends its own consolidation.**
  The pre-registered, statistically calibrated shape-selection rule was compared head-to-head with the plain bug fix — simply raising the cap on how many principal shapes the first stage may keep — and the plain fix wins.
  What survives is a confirmed fisher_kpp improvement of 13.35 (1.30× that dataset's minimum claimable effect), attributable entirely to the cap fix.
  The input-space-expansion repair is now a certified null: worse than inert (3.62× the threshold), because widening the correction gate's input collapses it — 19 columns of pure noise collapse it identically, so input width alone explains the failure.
  The stream-closing measurement: on fisher_kpp, even a perfect predictor restricted to the model's 50 principal shapes (the oracle ceiling, 298.83) still loses to the 6-parameter affine reference (270.54).
  The basis, not the selection rule, is the binding constraint there; cahn_hilliard retains 26.8× of real headroom.
- **IC-stack (r3s2-B2) — complete at 3 seeds; falsified on exactly one clause (an instrument-acceptance leg), while the route comparison itself came out affirmative.**
  The pre-registered stack-vs-direct contrast holds at panel level: the stack beats the matched direct route by 1.62 (3.2× the minimum claimable effect, sign-stable at every seed) — though no single-dataset win is claimable, because both ifc datasets still lose the mandatory affine reference.
  The clause that fired is honest instrument accounting: with only 3 fitting samples, cross-validation chose zero regularisation in the frequency band that matters on ifc_poisson, so the repair was inert exactly where batch 1 blew up.
  The replication arm is the round's cleanest attribution: it reproduced batch 1's numbers within noise on every seed *including* the seed-2 blow-up, down to the identical amplification factor (66.219…), proving the repaired arms removed it via the band-limit and not via re-implementation drift.
  The stream's reference-to-beat improves from 12.96 to 10.09, recorded with the caveat that the card setting it is falsified on its own pre-registration.
- **Value-of-coarse-data (r3s3-B2) — complete at 3 seeds; CONFIRMED.**
  The cost-curve experiment (150 training runs across a ladder of coarse-data budgets) found the pre-registered knee: on cahn_hilliard, adding distinct coarse conditions stops paying beyond c\* = 80, and the step into the knee is 7.0× the clause floor.
  It also delivered a training-free surrogate that locates the knee without any training runs — the object batch 3 now tests as a pre-registered predictor (§8).
  Two cautions are on the card: the mediator correlation is high (r = 0.9642) but the HF points do not collapse onto the LF curve, and the measured LF→HF exchange rate came out an order of magnitude below the registered prediction (0.67–2.18 LF rows per HF row) — so the surrogate has earned "locates the knee", not "prices the exchange".
  By design the card scores only 2 of the 5 panel datasets (cahn_hilliard and ifc_heat), so it claims no panel geomean.
- **Audit (r3s4-B2) — complete; the six-role checkpoint↔data binding instrument is CONFIRMED at 108/108.**
  On a labelled fixture of deliberately mutated checkpoints and data it scored perfect recall (27/27, 18/18, 18/18) with 0/27 false "retrain" verdicts (Wilson 95% upper bound 0.125).
  Both pre-registered "a simpler tool buys the same" branches failed: a whole-dataset hash certificate demands 36/36 unnecessary retrains on test-only changes, and a roles-blind variant misses 9/27 detections — the six-role structure is what makes the instrument both sharp and cheap.
  Together with batch 1's finding that wall-clock heuristics have zero unique true positives, checkpoint↔data binding strictly dominates the alternatives, and it is now installed as a hard gate in every anchor build.
  The card's compound hypothesis was falsified in exactly one conjunct: G5, its fairness probe, found a fit-set seam — reference floors were fitted on 400 rows while scored models fit on 320.
  The seam fired at 1.93× the minimum claimable effect on cahn_hilliard and was escalated per its clause.
- **The G5 fit-set seam was re-analyzed, re-priced in closed form, and ADOPTED by the operator — no re-runs, no verdict flips.**
  The matched-fit-set correction is below the claim threshold on all 5 affected cells and always *widens* the models' margins (5/5 sign-unchanged), so the original escalation priced the seam correctly and conservatively.
  The seam is generic to the nearest-neighbor-in-condition floor arm (it breaches on 56% of fisher_kpp fit sets and 23% of allen_cahn's, not just cahn_hilliard's), so every future claim priced against that floor now carries the arm's fit-set noise band beside the threshold.
  One live comparand was quantitatively re-priced (r3s2-B1's cahn_hilliard skill 10.0023 → 10.3064; verdict unchanged).
- **Scoring change (ADR r3-0006, operator decision).**
  The headline score's denominator moves from "copy the coarse solve and enlarge it" to the best learned baseline, `mf_fno_transfer_film`.
  Because both scores are ratios to the same model RMSE, the switch is an exact per-dataset conversion: nothing is re-scored, the frozen evaluation layer is untouched, rankings within the panel are preserved, and in-flight batch-2 verdicts evaluate in the units their predictions were registered in.
  The trade-off is recorded in the ADR: the denominator becomes a trained, seed-dependent object, so its own 3-seed variance is certified and disclosed beside every converted number.
  The certification, and the U-Net twin the operator asked for, are in §7.2.

## 7. Panel decision and certified baselines (added 2026-08-11)

### 7.1 ADR r3-0007: `ifc_poisson` becomes report-only (operator option C)

- **The trigger was an operator question, not a failure.**
  With batch 2 closed, Eloise asked whether the two `ifc` datasets belong in the scored panel at all.
  The on-file evidence was assembled into ADR r3-0007 with three options (keep both / demote both / demote `ifc_poisson` only); she chose option C, demote `ifc_poisson` only.
- **`ifc_poisson` is demoted because it is a closed-form task.**
  Its condition→answer map is exactly linear: an affine fit on the training conditions reproduces the fields to an oracle residual of 5.4e-16 — machine precision.
  No learned model in three rounds ever beat the copy-the-coarse-solve reference there.
  A scored cell that rewards memorizing a linear map tests nothing this benchmark is about.
  It stays report-only: every model still runs it and reports it; it just no longer moves the headline score.
  Its cells live in the state records and no longer appear in the figures — Fig. 1's per-dataset panel shows the 5 scored datasets only.
- **`ifc_heat` is retained because the baseline's win there is real structure.**
  The concern was that its fields are 88.5% level-dominated, so plain rel-L2 mostly measures a constant offset.
  A dedicated mean-removed check settled it: the film baseline's advantage over the best training-free floor *grows* from 2.60× to 2.79× after removing each field's mean — the opposite of an offset signature — and film's error sits below even the oracle affine residual (0.0272 vs 0.0377).
  That is structure no affine model can express, so the cell stays scored (record: `state/adr0007_meanremoved_check_2026-08-10.json`).
- **Affine floors are now always quoted with their leave-one-out fold range.**
  With only 5 HF training rows, a floor fitted once on all 5 rows is fragile.
  On `ifc_heat` the single-fit affine floor is 0.96 (better than the published paper bar at 1.0), but the leave-one-out mean is 1.85 (worse).
  Under refit, the yardstick itself crosses 1.0.
  Disclosing the fold range is now mandatory wherever an affine floor appears (`program.md` §2, amended under this ADR).
- **Panel arithmetic.**
  The scored panel is `allen_cahn_2d`, `fisher_kpp_2d`, `cahn_hilliard`, `pfc`, and `ifc_heat` (4 sharp + 1 ifc).
  The best training-free floor becomes **53.2146**, extending the audited lineage 75.0673 → 38.6300 → 36.3912 → 34.4198 → 38.8368 → 53.2146 (every step an ADR, recorded in `state/gates.md`).
  All four round-2 anchor cards were re-certified on the new panel through the binding and stale-checkpoint gates.

### 7.2 ADR r3-0006 executed: the learned-baseline denominator is certified — and has a twin

- **`mf_fno_transfer_film` is certified as the denominator.**
  Three fresh seeds on the repaired data, stale-audit clean; its 5-dataset panel value is 32.2165 in copy-LF units (`state/anchors/film_denominator.json`, the `_panel5_adr0007` keys).
- **The operator-requested ConvNeXt U-Net twin is a statistical dead heat with it.**
  Its panel error is 0.9805× film's, with cross-seed ratios spanning 0.94–1.04 (6 of 9 below 1) — neither model separates from the other at seed noise (`state/anchors/unet_baseline.json`).
  The certified film denominator therefore stands (the operator holds the override), and batch-3 clauses register in film units as planned.
  The two baselines have complementary per-dataset strengths (U-Net better on allen_cahn, fisher_kpp, and ifc_heat; film better on cahn_hilliard, pfc, and ifc_poisson), which is why the round-close leaderboard will show both.

## 8. Batch 3 — the final batch (launched 2026-08-11)

Batch-3 scope followed the streams' own recommendations: r3s1 and r3s4 consolidated (no new cards), and the two remaining streams each field one card.
Both cards register their success clauses against the certified film baseline, per the operator's direction that round 3's target is the best learned baseline, and both passed independent code review before submission.

- **r3s3-B3 — can the sample-efficiency knee be predicted before paying for the curve?** (seed 0 complete, under analysis)
  Batch 2's training-free surrogate claims to locate each dataset's knee — the coarse-data budget beyond which more coarse solves stop helping — from structure alone.
  Batch 3 makes that falsifiable the hard way: the surrogate's predicted knee for every cell was sealed (sha256 content hash + timestamp) *before any training job ran*, and a 4-rung ladder of coarse-data budgets now measures where the real knee is.
  The literature search found that published knee and break-detection methods — kneedle, broken-neural-scaling-law fits, projective early stopping — find the knee only on a curve that has already been paid for.
  As far as the search could establish, pre-declaring the knee from a structural descriptor, with zero training runs on the target cell, is untested.
  Seed 0 completed on the cluster (job 261111, 2 h 09 m); a chance match is 1/3 per adjudicable cell, so only the joint pattern across cells carries evidence.
- **r3s2-B3 — how much could the coarse-field detour ever buy?** (seed 0 relaunching after a guardrail stop)
  The IC-stack routes through a synthetic ("hallucinated") coarse field; this card separates "the corrector is bad" from "the corrector was fed a hallucinated field" with a 5-rung ladder from fully-deployed to oracle.
  The oracle rung feeds the corrector the *real* coarse field — which can never be deployed, because at test time that field physically does not exist — so the ladder measures a ceiling on what the route could ever buy, not an alternative model.
  Seed 0 stopped rather than report a wrong number.
  A disclosure module found that a guard dataset (`fluid`, 256 training rows) cannot satisfy the 320-row floor-fitting protocol it had declared, and the run refused to report a floor whose fit set did not match its declaration — the guardrail working as designed on a mapping defect.
  The debugger isolated the fix (the guard cell carries no matched-count obligation) and is relaunching; the scored panel cells were unaffected.

**Round close is expected 2026-08-12/13**: 3 seeds per card, mechanism analysis, then the round report with a final leaderboard of every round-3 model against *both* learned baselines (film and U-Net).
One recorded bookkeeping item must be reconciled in that leaderboard: the ifc rows currently mix two metric conventions across files (aggregate nRMSE vs per-sample rel-L2, a ~1.27× difference on `ifc_heat`), and the final table must use one convention throughout.
