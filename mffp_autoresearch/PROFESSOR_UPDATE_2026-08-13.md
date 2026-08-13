# MFFP Autoresearch — Update for Mentor (Round 3 Closed + Benchmark_30 Head-to-Head vs the Film Baseline)

Date: 2026-08-13. Author: Eloise (with the autoresearch orchestrator).
Canonical adjudicated records: `round3/docs/round3_report.md` (source of every §9–§12 number) and `mffp_autoresearch/benchmark30/docs/report.md` on branch `bench30-campaign` (source of every §13 number); both fact-check-converged.
Narrative through batch 2: `mffp_autoresearch/PROFESSOR_UPDATE_2026-08-10.md`.
Companion to the 2026-08-02 update.

Rendered versions of this update:
[Claude artifact](https://claude.ai/code/artifact/a03c7fd2-cf39-42d6-8ec5-cf5ee44449cc)
(private until shared from its share menu) ·
[`PROFESSOR_UPDATE_2026-08-13.html`](PROFESSOR_UPDATE_2026-08-13.html) (same page, in-repo).
Figures: `round3/docs/figures/r3_{performance_vs_baselines,architectures_overview,model_detail_ic_stack,model_detail_lf_channels}.png` (regenerated 2026-08-12 by `round3/tools/render_round3_update_figures.py`) and `figures/b30_skill_per_dataset.png` (rendered 2026-08-13 from the benchmark_30 leaderboard by `tools/render_b30_update_figure.py`), embedded in the rendered page.

## TL;DR

- **NEW · BENCHMARK_30 HEAD-TO-HEAD (2026-08-13) — the round-3 winner was trained head-to-head against the film-transfer baseline across the published `benchmark_30` release (film on all 30 datasets, the certified model on the 29 it structurally supports): it is a specialist, not a generalist (§13, Fig. 5).**
  Across the 29-dataset common set (3 seeds × 200 epochs, the round-3 stripped-view protocol), the certified model's panel-geomean error is ~1.67× film's (film-relative skill geomean 0.6004, seed range [0.5934, 0.6047]).
  It wins 5 of 29 datasets — by up to 6.4× — but loses the other 24, including two members of its own certification panel.
  All numbers fact-check-converged; the benchmark data was verified byte-identical to the published hub release, so the published benchmark needs no correction.
  Round 4 (approved 2026-08-13) starts lean: diagnostics + a training-budget check on the baseline itself, before any new model is built.
- **NEW · POST-CLOSE RULINGS LANDED — Eloise ratified both open governance decisions on 2026-08-12, and both are executed (§12).**
  The panel-composition ADR (r3-0008) was ratified as Option C: report-only datasets leave every claim-bearing average, each average's noise bar is now calibrated on the same set of datasets it is read against, and panel headlines must disclose how concentrated they are in single datasets.
  Under the corrected bars the batch-3 route headline *survives at reduced magnitude* (scored-5 subset 2.75× its own bar, registered-4 subset 2.54×; direction unchanged), while the six-cell aggregate becomes an era-stamped historical value.
  The ifc affine-floor rule (ADR r3-0009) was ratified as Option B: the rule text now pins both floor numbers (single-fit and leave-one-out mean) that this page already discloses — nothing shipped changes.
- **NEW · ROUND CLOSED — Round 3 closed on 2026-08-12 with all 10 experiment cards complete, each adjudicated at 3 random seeds against the certified noise floor.**
  Batch 3's two cards resolved the round's last open questions: the synthetic-coarse-field detour is capped by a *scalar identity* (r3s2-B3, confirmed — §9), and the training-free knee predictor does *not* transfer (r3s3-B3, falsified — §9) even though its trained arm posted the round's best score against the learned baseline (0.5780 in film units).
  The final era-scoped leaderboard is in §10; the rulings and their execution are in §12 — the only remaining hold is the round-1 2500-epoch queue.
- **DONE — Round 3 launched on 2026-08-05 on the repaired benchmark; batch 1 closed with four experiments, each run at 3 random seeds.**
  All four models beat the no-training reference error of 34.4198.
  Their geometric-mean normalized errors across the evaluated datasets range 11.08–24.96; lower is better.
- **DONE — The system detected and stopped work for two benchmark-integrity failures.**
  First, the evaluated phase-field-crystal (`pfc`) task contained essentially no fidelity gap: the coarse solution was already spectrally converged to the fine one, so the reported reference error was ~100% interpolation error introduced by our own evaluation.
  We made `pfc` report-only and reduced the evaluated set to 5 datasets (ADR r3-0004).
  Second, an audit found that several baseline models had been evaluated on repaired data without being retrained — mandatory checkpoint resumption had silently skipped training.
  We quarantined and retrained 32 runs, rebuilt the baselines, and added a permanent check to every baseline build.
- **The apparent 10.1% benefit from low-fidelity training data was entirely caused by the stale baselines.**
  The original result also claimed a 39% improvement on `ifc_poisson`.
  After the baseline repair, no dataset in that experiment shows a resolvable change: the panel change is −0.81%, only 0.08× the certified minimum detectable effect.
  The experiment still provides a valid decomposition of the mechanism.
- **The mechanism tests replaced two preregistered explanations with better-supported ones.**
  The factorised output head succeeds when the first-stage residual saturates, not when the condition vector has a particular dimension.
  The benefit of initial-condition information arises entirely in stage 1; the corrective second stage again has no detectable effect.
- **The audit experiment established the round's minimum detectable effects and measured the reliability of the audit tools.**
  One checkpoint-staleness heuristic found 0 unique true positives but raised 62 false alarms across 859 individual runs.
  It was replaced with content hashes stored in checkpoints.
- **DONE — Batch 2 closed on 2026-08-10: all 8 round-3 experiment cards from batches 1–2, across all four streams, are complete (§6).**
  The headline is the audit stream's checkpoint↔data binding instrument, CONFIRMED at 108/108 on a labelled-defect exam and now a hard gate in every anchor build.
  The repaired initial-condition stack is the round's best model at 10.09 (0.72× the film-transfer baseline).
- **DONE — ADR r3-0005 (ratified 2026-08-10, option A) is fully executed.**
  The evaluated `pfc` task now uses the coarsest available input resolution (32²→128²) and an exact spectral reference; `pfc` rejoined the scored panel after batch-2 computation closed, so no active experiment ever used mixed reference hashes.
- **DONE — Panel decision (ADR r3-0007; operator option C, 2026-08-10): `ifc_poisson` is demoted to report-only (§7).**
  Its condition→answer map is exactly linear (oracle affine residual 5.4e-16); no learned model ever beat the copy-the-coarse-solve reference there.
  `ifc_heat` stays scored: a dedicated check proved the film baseline's win there is real field structure, not offset calibration.
  The scored panel is 5 datasets; the best training-free floor becomes 53.2146.
- **DONE — Scoring change (ADR r3-0006, operator decision) executed: the headline denominator moved from copy-the-coarse-solve to the best learned baseline** (`mf_fno_transfer_film`), certified at 3 fresh seeds.
  An operator-requested ConvNeXt U-Net twin lands in a statistical dead heat with it (error ratio 0.9805, cross-seed range 0.94–1.04), so film stands (§7.2).
- **DONE — Batch 3 — the round's final batch — launched 2026-08-11 with 2 cards and closed 2026-08-12 (§8–§9).**
  The emulator-ceiling card CONFIRMED its pre-registered prediction and retired the synthetic-coarse-field detour with a mechanism; the sealed knee-prediction card was FALSIFIED with a mechanism that explains exactly when such predictions can and cannot work.
- **Four figures summarize the round**: the final combined leaderboard (Fig. 1, §10), the four experiment lines (Fig. 2, §2), and the two architectures that beat the learned baseline in detail (Figs. 3–4, §2.1).
  All are regenerated from the experiment records by `round3/tools/render_round3_update_figures.py` and embedded in the rendered page.

## 1. What round 3 asked, and how it ran

**The learning regime is unchanged from round 2.**
Models receive low-fidelity (LF) fields — cheap, coarse-grid solver runs — during training, but only the *condition vector* (the handful of numbers that define the physics setup) at test time.
The test interface physically excludes LF fields.

**The repaired benchmark now provides complete condition vectors and corrected fidelity hierarchies.**
Initial-condition coefficients are included in the condition vector, which retires the stochastic-map caveat from ADR r2-0003.
The nested `ifc` fidelity hierarchies are repaired, and `ifc_heat` is now evaluated in the scored panel.

**The scored set contains 5 datasets.**
Its membership changed twice during the round, each time through a recorded architecture decision record (ADR), never silently.
At batch-1/2 registration it was `allen_cahn_2d`, `fisher_kpp_2d`, `cahn_hilliard`, `ifc_poisson`, and `ifc_heat` (ADR r3-0004).
After batch 2 closed, ADR r3-0005 phase 2 restored `pfc` on its repaired 32²→128² task, and ADR r3-0007 demoted `ifc_poisson` to report-only (§7).
The current scored panel is therefore `allen_cahn_2d`, `fisher_kpp_2d`, `cahn_hilliard`, `pfc`, and `ifc_heat`.
Batch-1/2 numbers below are quoted in the units and on the panel they were registered with — this matters for the final leaderboard (§10).

**Batch 1 covered four experiment lines**: factorised heads, initial-condition reach, the value of LF training data, and benchmark auditing.
All 4 closed at 3 seeds.
Every experiment followed the full sequence of literature search, preregistration, implementation, adversarial review, GPU execution, and two-stage analysis.

**The round has certified minimum detectable effects.**
The batch-1 audit experiment (r3s4-B1) established per-dataset `seed_mce`, `tau_rel`, and `tau_abs` — the seed-based minimum claimable effect, its relative threshold, and its absolute threshold.
The geometric-mean `seed_mce` across the panel is 0.5083.
These thresholds were installed on 2026-08-10 and govern every claim below.

## 2. Batch-1 results (condition vector → HF field; no solver at test)

**How to read the verdicts.**
CONFIRMED means the experiment's pre-registered prediction passed its threshold at 3 seeds.
FALSIFIED means the pre-registered prediction failed its threshold; because every prediction is registered before the run, a falsification is a finding, not a process failure.
CERTIFIED is the strongest label: measured at 3 seeds and priced against the audited minimum-detectable-effect table.
"Not resolvable" means the measured difference is smaller than the certified minimum detectable effect, so no claim is made either way.

Batch-1 leaderboard (3-seed geometric mean of normalized error across the batch-1 registration panel, lower is better; no-training reference 34.4198 on that panel — the current 5-dataset panel's floor is 53.2146, §7).
The round-final leaderboard including batches 2–3 is in §10 (Fig. 1).

| Rank | Card | Panel geomean [3-seed] | Verdict | What it is |
|---|---|---|---|---|
| 1 | LF-channels contrast (r3s3-B1) | 11.0789 [10.84, 11.25] | confirmed (mechanism card) | Compute-matched comparison with and without LF training data; **no resolvable change from the repaired baseline** — the decomposition is the result |
| 2 | IC-stack (r3s2-B1) | 12.9556 [10.32, 17.83] | F1 confirmed / **F2 falsified** | Initial-condition information helps in stage 1; the corrective stage is unresolvable, replicating round 2's null result |
| 3 | Certifier (r3s4-B1) | 19.6438 [19.42, 19.93] | F2–F4 confirm; F1 at metrology margin | Source of the round's certified minimum detectable effects |
| 4 | Two-stage factorised head (r3s1-B1) | 24.9573 [24.87, 25.07] | confirmed | Closed-form condition-to-coefficient cascade; the improvement occurs only on `cahn_hilliard` |

Fig. 2 (`round3/docs/figures/r3_architectures_overview.png`) — **the four experiment lines, what each model actually is, and what the round established about each.**
Every model maps condition → fine-grid field with no solver and no coarse field at test.
The number in each title is the 3-seed batch-1 panel error [95% CI], lower is better.
Each panel's footnote now carries the stream's full arc through batch 2 and (for r3s2 and r3s3) the batch-3 closure verdict.
The verdict vocabulary is keyed at the bottom of the figure.

### Headline mechanism results (each from a causal probe, not a hunch)

**The factorised head is distinguished by first-stage residual saturation, not condition dimension.**
`allen_cahn` and `cahn_hilliard` both have condition dimension 19, but their stage-2 margins differ 47×; `fisher_kpp` has the largest condition dimension, 50, and the smallest margin.
The decisive quantity is the predictable energy left after stage 1.
On `fisher_kpp`, a hyperparameter limit (`SELECT_MAX = 32`) excludes 0.0713 of the condition-reachable energy; within the selected subspace the head beats the affine reference, and its loss outside that subspace is 17× larger.
The `cahn_hilliard` improvement is broad rather than outlier-driven: 78–82 of 100 rows improve, and it remains 2.9–3.2× above the certified minimum detectable effect after adversarially removing 10 rows.

**Initial-condition information helps entirely through stage 1, and the remaining error is limited by approximation.**
The fractions of emulator error removed are 63.7% (`allen_cahn`), 22.3% (`cahn_hilliard`), and 85.4% (`fisher_kpp`).
A control given a fake, information-free initial condition performs *worse* than one given no initial condition at all, on every dataset — the benefit comes from the information, not the extra input channel.
The remaining `cahn_hilliard` gap is an approximation problem: even its nearest training neighbor in condition space is 98% as different as a randomly chosen sample.

**The corrective second stage is decisively ineffective for the second consecutive round.**
The best two-stage variant improves over its own front-end-matched emulator-only control by 9–163× *less* than one minimum detectable effect.
Round 2's null of 0.0061 replicates at 0.0056 [0.0053, 0.0061].
The one dramatic failure (`ifc_poisson` seed 2, nRMSE 2.04 vs 0.15) was a deterministic measurement defect: an unregularised spectral Wiener transfer fitted from **3** samples amplified the signal 66× in a frequency band where the LF input has no power — the same failure mode as round 2's baseline instability.

**LF training data helps by supplying identifiable condition–response pairs.**
A control receiving extra LF data only at conditions already covered by HF data learns the same function as the no-LF variant (function-distance ratios 0.098–0.307).
New, distinct condition rows explain $E_{\text{cov}}/E_{\text{total}} \in [0.972, 1.024]$ in 30/30 evaluated cases, and recovery is nearly deterministic given the measurable condition–response alignment (Pearson $r = 0.985$).
Batch 2 then asked whether this mediator yields a stable exchange rate between LF and HF rows; it does not (§6).

**A seed-invariant hard subpopulation exists in `cahn_hilliard`**: 27 of 100 test rows whose conditions are nearly indistinguishable from training conditions (maximum gap $0.45\sigma$) yet whose fields are 3.29× farther away.
LF training data specifically repairs this group: 92 of the no-LF variant's worse-than-zero rows, 97% of that comparison's gain.

### 2.1 The models that beat the baseline, in detail

Three certified batch-1/2 models beat the learned baseline: the repaired batch-2 initial-condition stack (r3s2-B2, 0.72× film), the LF-trained multi-resolution FNO (r3s3-B1, 0.79×), and the original batch-1 initial-condition stack (r3s2-B1, 0.92×).
Batch 3 extended this set with r3s3-B3's arm at 0.5780 film units (§9).
All share the deployment premise (condition in, fine field out, no solver at test), and all owe their standing to mechanism work rather than architecture novelty.
The two IC-stack entries are one architecture — batch 2 changes only the corrector's spectral filter — so the diagrams show two architectures, with the batch-2 repair delta called out on the shared IC-stack diagram.

Fig. 3 (`round3/docs/figures/r3_model_detail_ic_stack.png`) — **the initial-condition stack (r3s2), in detail.**
Left: the test-time path — a FiLM-conditioned Fourier neural operator (4 spectral blocks, width 64, 12 Fourier modes) synthesizes the coarse field the solver would have produced, directly from the condition vector; the certified per-dataset interpolation convention lifts it to the fine grid; a frozen corrector (spectral LSI filter + local CNN) upgrades it.
Right: the batch-2 repair delta (band-limit + ridged inversion) and how the stack is trained.
B1 = 0.92× film, B2 = 0.72× film — the round's best model.
The findings strip records the batch-3 closure: the corrector passes stage-1's own error through at unity gain, so the detour route is retired (§9).

Fig. 4 (`round3/docs/figures/r3_model_detail_lf_channels.png`) — **the LF-trained multi-resolution FNO (r3s3's A1 arm), in detail.**
Left: at test it is just a conditioned FNO reading out its fine head; the coarse heads exist purely to absorb training signal.
Right: the joint multi-resolution loss (~400 coarse rows vs as few as 5 fine rows) and the controlled data-diet arms that isolate *why* it works.
0.79× film at batch 1; best model on `ifc_heat` and `fisher_kpp`.
The findings strip records the batch-3 closure: the knee surrogate's sealed predictions were falsified, while this same card's trained arm scored the round's best film-unit result (§9).

**The initial-condition stack (r3s2).**
Stage 1 is a FiLM-conditioned Fourier neural operator that synthesizes the coarse field the solver would have produced, directly from the condition vector; the condition enters every block as a learned affine modulation, so one network serves all conditions.
Stage 2 is a frozen local CNN corrector trained on real coarse→fine pairs in an earlier round; batch 2 added a cross-validated ridge plus a hard band-limit at the coarse grid's Nyquist frequency, repairing the one failure mode (the 66× spectral amplification fitted from 3 samples).
Established: the initial-condition information is the entire measurable effect and acts in stage 1; the corrector adds nothing resolvable (round 2's null replicates); the repair's attribution was proven by a replication arm that reproduced the old defect digit-for-digit; both `ifc` cells still lose to a 6-parameter affine fit (§7.1 explains how those affine floors are quoted).

**The LF-trained multi-resolution FNO (r3s3's A1 arm).**
One conditioned FNO with its Fourier modes pinned to the coarsest rung's Nyquist so every resolution shares one spectral basis, and per-rung output heads sharing the backbone.
Training minimizes a joint loss — predict the coarse solve at every rung AND the fine field, equally weighted — with ~400 coarse rows against as few as 5 fine rows.
At test only the fine head is read out.
The controlled arms (no coarse data / coarse data only at already-covered conditions / full pool) are what let the round attribute the effect: the value is supply of new condition points, not regularization.
Established: recovery tracks condition–response alignment at $r = 0.985$; the pre-repair −10.1% headline was retracted as a stale-baseline artifact; batch 2 confirmed the cost curve's knee at $c^* = 80$ distinct coarse conditions on `cahn_hilliard` plus a training-free surrogate for it — the object batch 3 then put on trial (§8–§9).

## 3. Benchmark-integrity findings (the part most relevant to the benchmark paper)

- **The evaluated `pfc` task contained essentially no fidelity gap.**
  On 2026-08-07 this triggered the first stop-the-line event.
  The evaluation convention selected the highest available LF resolution, producing the 64²→128² task, where the crystalline fields are band-limited below the coarse-grid Nyquist frequency: the exact per-row copy error is ≤ 1.66e-6 on all 100 test rows, so the certified reference error of 0.018257 was ~100% linear-interpolation error introduced by the fixed lifting operation.
  The real fidelity gap occurs at 32²→128², which the convention did not evaluate.
  We made `pfc` report-only (ADR r3-0004); ADR r3-0005 provided the durable repair (§5).
- **Checkpoint resumption silently invalidated a baseline re-evaluation campaign.**
  On 2026-08-08 this triggered the second stop-the-line event.
  Models being re-evaluated on repaired data resumed already-completed checkpoints (records showed `resumed_from_step = 5000`, training times 1.3–2.9 s), so pre-repair weights were evaluated on post-repair arrays.
  Existing hash checks passed because references were recomputed live while the weights stayed stale.
  We quarantined and retrained 32 runs, rebuilt the baselines (changes confined to the contaminated columns), and installed a permanent stale-checkpoint check in every baseline build.
  Fresh training *improved* every contaminated baseline — the contamination had been flattering experimental comparisons.
  All of round 3's own experiment runs were clean (0/225).
- **The audit experiment measured the audit tools' own accuracy.**
  The `train_seconds` staleness heuristic found 0 unique true positives and 62 false alarms across 859 runs and was deleted.
  File modification times cannot establish data identity (the repair copy preserved them); only a content hash stored in the checkpoint distinguishes a training-invalidating data change from a harmless test-split trim.
  Building that mechanism was the batch-2 audit experiment — built and CONFIRMED at 108/108, now a hard gate in every anchor build (§6).
- **Tolerance setting now rests on a measured numerical-precision limit.**
  The audit F1 condition fired at 1.106e-9 against a fixed 1e-9 tolerance — ~70× below the float64→float32 loading seam.
  Per-dataset analysis in units of floating-point spacing shows suitable tolerances range from 2e-9 to 0.31 (the upper value on a guard dataset with an exact-equality check that amplifies one unit in the last place by 8.4e6×).
  F1-class tolerances are now max(1e-9, measured per-dataset band), installed in `state/floor_tolerances.json`.
- **A reported minimum detectable difference of 0 means unobservable, not zero.**
  For both `ifc` datasets, this round cannot observe uncertainty in the reference itself.
  Batch 2 re-priced the resulting understatement and partially retracted it: the conservative bound on `ifc_poisson` is 1.0136× certified, not the ~2.15× batch 1 warned (the proxy was off 84× because the cell's affine map makes its per-row gaps condition-independent).

## 4. How the harness itself is performing

- **Batch 1 completed all four experiment lines at 3 seeds in ~5 days** (stop-the-line repair consumed ~2 of those); batch 2 went from literature search to first SLURM jobs in under a day; batch 3 launched 2026-08-11 and closed 2026-08-12.
- **Preregistration and minimum-effect thresholds prevented two false headlines** (the −10.1% LF-training panel improvement; the condition-dimension explanation of the factorised head).
  Adversarial reviews caught substantive defects before submission on all four batch-1 builds.
- **Certified and retracted results remain explicitly traceable.**
  Only results backed by the audit certification are called certified; every retraction is annotated in its experiment record with the historical numbers preserved.
  Searches across 7 batch-2 directions found 0-for-7 cases of outright novelty, so each experiment claims only its measured composition.
- **The state-file design allowed the round to survive an orchestrator failure.**
  The launch orchestrator session died on 2026-08-08; a fresh session resumed losslessly from the state files, executed the repair under the standing delegation while holding the stop-the-line decision for operator adjudication, and has run the round since.
  The cluster's SLURM job-ID space also reset mid-round; accounting was re-established and old IDs still resolve.

## 5. Decisions and next steps (statuses final, 2026-08-12)

1. DONE — **ADR r3-0005, the `pfc` spectral-resolution repair, is fully executed** (ratified 2026-08-10, option A; Eloise made the decision for the mentor).
   Serving `pfc` levels {1, 3} changes the evaluated task to 32²→128², where the measured per-row LF→HF gap is real (mean 0.0124, 0/100 task-void rows), and the copy reference uses a `pfc`-specific spectral lift (exact reference 0.012358; a linear lift has ~0.07 error and would again overwhelm the true gap).
   Phase 2 completed after batch-2 computation closed, so no active experiment ever used mixed reference hashes.
   The repaired task remains outlier-dominated (top-5 rows carry 38.8% of the denominator; minimum detectable change **65.8%**) — honest but low-resolution, and every claim about it must exceed that bar.
2. DONE — **Batch 2 completed all four experiments and closed on 2026-08-10** — results in §6.
3. DONE — **ADR r3-0006 executed**: the film-transfer denominator is certified at 3 fresh seeds, converted reporting is live, and batch-3 experiments registered their predictions in the new units (§7.2).
4. DONE — **Batch 3 closed 2026-08-12** (§9); the round is closed, and the final era-scoped leaderboard is §10.
5. HOLD — **The round-1 full runs of 2500 epochs remain on hold** (unchanged since 2026-08-01; §12).

## 6. Batch-2 close (2026-08-10)

All 8 round-3 experiment cards from batches 1–2, across all four streams, completed at 3 seeds through the full pipeline.
In the new film units, the round's standing after batch 2: r3s2-B2 at 0.72, r3s3-B1 at 0.79, r3s2-B1 at 0.92, r3s4-B1 at 1.40, r3s1-B1 at 1.77, and r3s1-B2 at 1.78.

- **Factorised head (r3s1-B2) — complete; falsified its novelty claim; the stream recommended its own consolidation.**
  The pre-registered, statistically calibrated shape-selection rule was compared head-to-head with the plain bug fix — simply raising the cap on how many principal shapes the first stage may keep — and the plain fix wins.
  What survives is a confirmed `fisher_kpp` improvement of 13.35 (1.30× that dataset's minimum claimable effect), attributable entirely to the cap fix.
  The stream-closing measurement: on `fisher_kpp`, even a perfect predictor restricted to the model's 50 principal shapes (the oracle ceiling, 298.83) still loses to the 6-parameter affine reference (270.54).
  The basis, not the selection rule, is the binding constraint there; `cahn_hilliard` retains 26.8× of real headroom.
- **IC-stack (r3s2-B2) — complete at 3 seeds; falsified on exactly one clause (an instrument-acceptance leg), while the route comparison itself came out affirmative.**
  The pre-registered stack-vs-direct contrast holds at panel level: the stack beats the matched direct route by 1.62 (3.2× the minimum claimable effect, sign-stable at every seed) — though no single-dataset win is claimable, because both `ifc` datasets still lose to the mandatory affine reference.
  The clause that fired is honest instrument accounting: with only 3 fitting samples, cross-validation chose zero regularisation in the frequency band that matters on `ifc_poisson`, so the repair was inert exactly where batch 1 blew up.
  The replication arm is the round's cleanest attribution: it reproduced batch 1's numbers within noise on every seed *including* the seed-2 blow-up, down to the identical amplification factor (66.219…), proving the repaired arms removed it via the band-limit and not via re-implementation drift.
  The stream's reference-to-beat improved from 12.96 to 10.09, recorded with the caveat that the card setting it is falsified on its own pre-registration.
- **Value-of-coarse-data (r3s3-B2) — complete at 3 seeds; CONFIRMED.**
  The cost-curve experiment (150 training runs across a ladder of coarse-data budgets) found the pre-registered knee: on `cahn_hilliard`, adding distinct coarse conditions stops paying beyond $c^* = 80$, and the step into the knee is 7.0× the clause floor.
  It also delivered a training-free surrogate that locates the knee without any training runs — the object batch 3 then tested as a pre-registered predictor.
  Two cautions were on the card: the mediator correlation is high ($r = 0.9642$) but the HF points do not collapse onto the LF curve, and the measured LF→HF exchange rate came out an order of magnitude below the registered prediction (0.67–2.18 LF rows per HF row) — so the surrogate had earned "locates the knee", not "prices the exchange".
  By design the card scores only 2 of the 5 panel datasets, so it claims no panel geomean.
- **Audit (r3s4-B2) — complete; the six-role checkpoint↔data binding instrument is CONFIRMED at 108/108.**
  On a labelled fixture of deliberately mutated checkpoints and data it scored perfect recall (27/27, 18/18, 18/18) with 0/27 false "retrain" verdicts (Wilson 95% upper bound 0.125).
  Both pre-registered "a simpler tool buys the same" branches failed: a whole-dataset hash certificate demands 36/36 unnecessary retrains on test-only changes, and a roles-blind variant misses 9/27 detections.
  Together with batch 1's finding that wall-clock heuristics have zero unique true positives, checkpoint↔data binding strictly dominates the alternatives, and it is now installed as a hard gate in every anchor build.
  The card's compound hypothesis was falsified in exactly one conjunct: G5, its fairness probe, found a fit-set seam — reference floors fitted on 400 rows while scored models fit on 320 — firing at 1.93× the minimum claimable effect on `cahn_hilliard`.
- **The G5 fit-set seam was re-analyzed, re-priced in closed form, and ADOPTED by the operator — no re-runs, no verdict flips.**
  The matched-fit-set correction is below the claim threshold on all 5 affected cells and always *widens* the models' margins, so the original escalation priced the seam correctly and conservatively.
  The seam is generic to the nearest-neighbor-in-condition floor arm (it breaches on 61.3% of `cahn_hilliard`, 56.0% of `fisher_kpp`, and 23.0% of `allen_cahn` fit sets), so every future claim priced against that floor now carries the arm's fit-set noise band beside the threshold.
  One live comparand was re-priced (r3s2-B1's `cahn_hilliard` skill 10.0023 → 10.3064; verdict unchanged).

## 7. Panel decision and certified baselines

### 7.1 ADR r3-0007: `ifc_poisson` becomes report-only (operator option C)

- **The trigger was an operator question, not a failure.**
  With batch 2 closed, Eloise asked whether the two `ifc` datasets belong in the scored panel at all.
  The on-file evidence was assembled into ADR r3-0007 with three options; she chose option C: demote `ifc_poisson` only.
- **`ifc_poisson` is demoted because it is a closed-form task.**
  Its condition→answer map is exactly linear: an affine fit on the training conditions reproduces the fields to an oracle residual of 5.4e-16 — machine precision.
  No learned model in three rounds ever beat the copy-the-coarse-solve reference there.
  A scored cell that rewards memorizing a linear map tests nothing this benchmark is about.
  It stays report-only: every model still runs and reports it; it just no longer moves the headline score.
- **`ifc_heat` is retained because the baseline's win there is real structure.**
  The concern was that its fields are 88.5% level-dominated, so plain rel-L2 mostly measures a constant offset.
  A dedicated mean-removed check settled it: the film baseline's advantage over the best training-free floor *grows* from 2.60× to 2.79× after removing each field's mean — the opposite of an offset signature — and film's error sits below even the oracle affine residual (0.0272 vs 0.0377).
  That is structure no affine model can express.
- **Affine floors are always quoted with their leave-one-out fold range.**
  With only 5 HF training rows, a floor fitted once on all 5 rows is fragile.
  On `ifc_heat` the single-fit affine floor is 0.96 (better than the published paper bar at 1.0), but the leave-one-out mean is 1.85 (worse): under refit, the yardstick itself crosses 1.0.
  Disclosing the fold range is mandatory wherever an affine floor appears (`program.md` §2, amended under this ADR); the full disclosure is repeated beside the final leaderboard (§10).
- **Panel arithmetic.**
  The scored panel is `allen_cahn_2d`, `fisher_kpp_2d`, `cahn_hilliard`, `pfc`, and `ifc_heat` (4 sharp + 1 ifc).
  The best training-free floor becomes 53.2146, extending the audited lineage 75.0673 → 38.6300 → 36.3912 → 34.4198 → 38.8368 → 53.2146 (every step an ADR).
  All four round-2 anchor cards were re-certified on the new panel through the binding and stale-checkpoint gates.

### 7.2 ADR r3-0006 executed: the learned-baseline denominator is certified — and has a twin

- **`mf_fno_transfer_film` is certified as the denominator**: three fresh seeds on the repaired data, stale-audit clean; its 5-dataset panel value is 32.2165 in copy-LF units (on the batch-1/2 registration panel: 14.0770).
- **The operator-requested ConvNeXt U-Net twin is a statistical dead heat with it.**
  Its panel error is 0.9805× film's, with cross-seed ratios spanning 0.94–1.04 — neither model separates from the other at seed noise.
  The certified film denominator therefore stands (the operator holds the override), and batch-3 clauses registered in film units as planned.
  The two baselines have complementary per-dataset strengths, which is why the round-close leaderboard figure shows both (Fig. 1).

## 8. Batch 3 — the final batch (launched 2026-08-11; both cards closed 2026-08-12)

Batch-3 scope followed the streams' own recommendations: r3s1 and r3s4 consolidated (no new cards), and the two remaining streams each fielded one card.
Both cards registered their success clauses against the certified film baseline, per the operator's direction that round 3's target is the best learned baseline, and both passed independent code review before submission.

- CLOSED · FALSIFIED — **r3s3-B3 — can the sample-efficiency knee be predicted before paying for the curve?**
  Batch 2's training-free surrogate claims to locate each dataset's knee — the coarse-data budget beyond which more coarse solves stop helping — from structure alone.
  Batch 3 made that falsifiable the hard way: the surrogate's predicted knee for every cell was sealed (sha256 content hash + timestamp) *before any training job ran*, and a 4-rung ladder of coarse-data budgets measured where the real knee is.
  The literature search had found that published knee and break-detection methods find the knee only on a curve that has already been paid for; pre-declaring it from a structural descriptor appears untested.
  Verdict and mechanism: §9.
- CLOSED · CONFIRMED — **r3s2-B3 — how much could the coarse-field detour ever buy?**
  The IC-stack routes through a synthetic ("hallucinated") coarse field; this card separates "the corrector is bad" from "the corrector was fed a hallucinated field" with a 5-rung ladder from fully-deployed to oracle.
  The oracle rung feeds the corrector the *real* coarse field — which can never be deployed, because at test time that field physically does not exist — so the ladder measures a ceiling on what the route could ever buy, not an alternative model.
  Its seed-0 launch demonstrated the guardrails working as designed: a disclosure module refused to report a floor whose fit set did not match its declaration (a guard-dataset mapping defect), the debugger isolated the fix at attempt 1, and the relaunch was clean; the scored panel cells were unaffected.
  Verdict and mechanism: §9.

## 9. Batch-3 close (added 2026-08-12) — the round's last two answers

Both cards completed 3 seeds through the full pipeline; every claim below is a 3-seed mean adjudicated against the certified noise floor, quoted from the adjudicated experiment records (`round3_report.md` §2–§3 and the cards' part 5).

### 9.1 r3s2-B3: the emulator ceiling is CONFIRMED — and it retires the coarse-field detour

**The result in one sentence: routing through a synthetic coarse field can never beat the network that synthesizes it, because the corrector passes the synthesizer's error straight through.**

**The numbers.**
On its registered 6-cell panel the arm scores 14.1909 [14.0046, 14.5243] — since the 2026-08-12 ruling an era-stamped historical value (the launch-era composition includes report-only `ifc_poisson`, so this number is descriptive, not claim-bearing; §12).
On the 5-cell subset the stream anchor is defined on, it scores 10.4763 [10.3176, 10.7785] against the certified anchor's 10.0853 [9.7249, 10.3528] — a difference of +0.3910, which is 0.77× the certified panel seed-mce and therefore *not resolvable*: exactly the pre-registered replication outcome (the card was not expected to beat the anchor, and did not).
The primary falsification clause fired on 0 of 4 registered cells, with the ceiling share $\phi_{\text{ceil}} \ge 0.9648$ and the error hallucination-dominated on 4 cells.

**The mechanism, in plain terms: a unity-gain scalar identity.**
The stack has two stages: a *stage-1 emulator* that synthesizes the coarse field from the condition, and a *corrector* that upgrades coarse to fine.
The card measured how much of stage 1's error the corrector transmits downstream, and the answer is essentially all of it: a gain of 0.80–1.02 on 6 of 6 dataset cells — "unity gain", like a photocopier set to 100%: whatever error goes in comes out the same size.
The consequence is that three quantities that could in principle differ collapse into one number: the deployed route's error ≈ the emulator-only error ≈ the stage-1 emulator's own held-out error on the coarse field (log-log slopes 1.035 / 1.004, correlations $r = 0.998$ / $0.988$).
So the earlier finding that the corrector "adds nothing" ($\rho \approx 0$, twice replicated) is not a subtle statistical null — it is a *scalar identity*: the route's score is pinned to stage 1's own accuracy, full stop.

**Where the error actually lives: at LOW spatial frequency.**
Decomposing the error by wavenumber (spatial frequency — low wavenumbers are the broad strokes of the field, high wavenumbers the fine texture) shows 86–99.8% of the error concentrated in the lowest wavenumber-eighth.
The stack is not failing to reproduce sharp small-scale detail; it is getting the broad strokes wrong.
This retires the "sharp small-scale detail" narrative for this route.

**What the ceiling would cost.**
The ceiling is real — a corrector fed the *true* coarse field does much better — but reaching it through this route costs 8.7–116.6× more LF accuracy than stage 1 delivers.
The round-4 contract therefore pre-registers a hard rule: any future condition→pseudo-LF→HF card must state *in advance* which term of the unity-gain identity it intends to break; otherwise it is pre-falsified by this card's mechanism.

**Honest accounting beside the result.**
One licence check (C3) failed on the `ifc` cells for a real reason: at $N_{\text{hf}} = 5$ training rows, a cancellation-breaking bias appears (mean signed gap +0.3639 on `ifc_poisson`, larger than the 0.25 tolerance, vs |mean| ≤ 0.0369 on the 400-row cells).
Per the mandatory rule, every `ifc` number here carries the fitted affine-floor disclosure quoted in full at §10.
Second, the card's confidence intervals are *seed+run* intervals — upper bounds on the seed effect — because a same-seed cross-node rerun moved the 5-cell subset by 0.62× seed-mce (68% of the across-seed spread); this measured drift was also part of the evidence in the panel-composition question, since ruled (ADR r3-0008 Option C, §12).

The stream is closed: its question — can the complete condition vector be converted into field-level structure through a coarse-field route? — is answered in graded form.
Stage 1 provably benefits from exact IC information (up to 8×); nothing downstream can convert that into more, at unity gain.

### 9.2 r3s3-B3: knee predictability is FALSIFIED — the surrogate is the wrong learner's learning curve

**The result in one sentence: the sealed knee predictions missed decisively on both cells that could adjudicate them, the control confirmed the instrument was fine, and the mechanism explains exactly why — while the same card's trained model quietly posted the round's best score against the learned baseline.**

**The numbers.**
Both adjudicable predictive cells missed the sealed knee on every seed: by 6.03–6.79× the certified threshold ($\tau_{\text{rel}}^{\text{film}}$) on `allen_cahn` and 18.60–19.34× on `fisher_kpp`.
Meanwhile the `cahn_hilliard` reproduction control — the cell where batch 2 had already measured the knee — HIT its pre-declared cap of 80 on all three seeds, closing the "maybe the instrument is unstable" branch.
The falsification is clean: the predictions were sealed (sha256 + timestamp) before any training job ran, so there is no room for hindsight adjustment.

**The mechanism, in plain terms: the wrong learner's learning curve.**
The surrogate predicts the knee by drawing a learning curve — but it draws the learning curve of a *different student*: a closed-form kernel-ridge method, not the Fourier neural operator that actually trains.
Predicting where the FNO's curve bends from the kernel method's curve is like predicting when a marathon runner will hit the wall by watching a cyclist ride the same course: it works only where the two tire at the same rate.
That is measurable: on the two batch-2 validation cells the row-efficiency ratio ($c_{50}$, the budget each learner needs to reach half its final quality) was 1.05 / 0.59 — matched — while on the two missed cells it is 1.79 / 6.28: the kernel method learns up to 6× faster per row, so its curve bends far earlier than the FNO's.
The standing rule extracted from this: a training-free surrogate is licensed by *row-efficiency match*, not by correlation — Pearson 0.98 on validation cells did not survive transfer, and any future surrogate claim must publish the $c_{50}$ ratio beside the correlation.

**The alternative explanations were tested and rejected.**
The coverage-radius reading fails outright (the fill distance decays only 15–29% over an 80× row increase); the level hypothesis is rejected (mean-removed knees also land at 395 on both misses — the required pairing on these level-dominated cells); two design amplifiers were identified and recorded (the confirming ladder was built *from* the prediction, and the step statistic was not normalised by log-spacing — under the corrected statistic the robust effect is `fisher_kpp` alone); and a 10-probe audit found foreseeability was NOT established (3/10 seal-time separators vs 2.0 expected by chance) — the miss was a genuine empirical surprise, not a foreseeable design error.

**The arm itself is the round's best result against the learned baseline.**
The trained A1 arm scores 18.6212 [18.0610, 18.9994] in copy-LF units on the ADR r3-0007 scored panel, which in its registered film units is 0.5780 [0.5606, 0.5897] — about 42% less error than the certified learned baseline, the round's best learned-vs-learned number — even though the card's registered knee claim was falsified.
Both facts are reported side by side, per the round's discipline that a falsification is a finding about the claim, not about the model.

**Disclosure.**
This card's 3-seed part-5 write initially never landed (the analyzer's completion report overstated; the numbers survived in its handoff) and rode two pipeline stages undetected before the 2026-08-12 maintainer walk flagged it.
The repair extended part 5 to the 3-seed record with parts 6/7 verified byte-identical, clause text byte-equal to the locked pre-registration, and every seed-0 digit reproduced before extending — the repaired part 5 is the adjudicated record, not a caveat on these numbers.
Dispatcher-verified card writes are round-4 contract item #1.

Harness note for the batch: one SLURM failure occurred (r3s2-B3 seed 0) and was fixed at debug attempt 1; the r3s2-B3 hold-and-release sequence under a moving clause input was run entirely on written grounds, with the job held at 0 s executed until release.

## 10. The final leaderboard (era-scoped)

**Why two tables.**
Mid-round, three ADRs changed the measurement system itself: the panel composition (r3-0005 restored `pfc`; r3-0007 demoted `ifc_poisson`) and the reporting denominator (r3-0006: film units).
Batch-1/2 cards registered on the old panel in copy-LF units; batch-3 cards registered on the new definitions.
Comparing across that boundary would assert exactly the comparison the ADRs disclaim, so **ranks are assigned within an era only** and the two tables below share no ordinal scale.
Film-unit cells are quoted only where they exist on a primary record; no conversion was computed for this page.

Fig. 1 (`round3/docs/figures/r3_performance_vs_baselines.png`) — **the round-3 final leaderboard (round closed 2026-08-12).**
Every certified card in one combined chart, ranked by 3-seed panel geomean skill in copy-LF units (error ÷ copy-LF; lower is better; whiskers = 95% CI).
Purple bars beat the certified learned baseline `mf_fno_transfer_film` (solid blue line at its own copy-LF panel value 14.0770; its 3-seed spread shaded); each bar is annotated with its film-unit reading.
The U-Net twin (dotted) sits at a statistical dead heat with film (cross-seed ratios 0.94–1.04).
The dashed line is the best training-free floor (53.2146 in copy-LF units on the ADR r3-0007 scored panel, §7.1).
† r3s3-B3 is scored on the ADR r3-0007 panel (`pfc` in place of `ifc_poisson`); all other bars share the ADR r3-0004 5-dataset panel. r3s2-B3 shown as its 5-cell anchor-comparand (same datasets as the batch-1/2 panel).
The ifc affine-floor disclosure below applies to every ifc-containing value in this figure.

**Batch-1/2 era** (ADR r3-0004 5-dataset panel: `allen_cahn`, `fisher_kpp`, `cahn_hilliard`, `ifc_poisson`, `ifc_heat`; copy-LF units; ranks within this era only):

| Era rank | Card / arm | Panel geomean skill | Film units | Verdict | Notes |
|---|---|---|---|---|---|
| 1 | **r3s2-B2 repaired-corrector stack (CERTIFIED stream anchor)** | **10.0853** [9.7249, 10.3528] | — | falsified-via-G2(iii) | Affirmative route; new stream anchor, beats B1 by 2.8704 with the whole interval below it |
| 2 | r3s3-B1 coverage-decomposition arm | 11.0789 [10.8445, 11.2471] | 0.79 | confirmed | vs repaired anchor −0.81% = 0.079× noise floor, not resolvable |
| 3 | r3s2-B1 IC-synthesis stack | 12.9556 [10.3180, 17.8277] | 0.92 | falsified (F2) | F1 reach effect confirmed; wide CI is the deterministic `ifc_poisson` seed-2 blow-up (2.04 vs 0.15) |
| 4 | **r3s4-B1 certifier (3 seeds, CERTIFIED noise floor)** | 19.6438 [19.4235, 19.9318] | 1.40 | falsified (metrology-limited F1) | The round's measurement stick; F2/F3/F4 confirm |
| 5 | r3s1-B1 two-stage factorised head | 24.9573 [24.8726, 25.0662] | 1.77 | confirmed | One-cell effect (`cahn_hilliard`); L3 adjudicated VOID (enumerates pfc) |
| 6 | r3s1-B2 cap-lift + predictive criterion | 25.1243 [24.9477, 25.2757] | — | falsified (L2 panel + L3 novelty; L1 cell confirmed) | Reported per its own clause as the SELECT_MAX bug-fix, no novelty claim |
| — | r3s3-B2 coverage-knee ladder | no panel claim (2-ds diagnostic) | — | confirmed | Knee $c^* = 80$; training-free surrogate; pre-registered as diagnostic-only |
| — | r3s4-B2 checkpoint-binding pricing | no panel cells by design (0/0) | — | falsified (3rd conjunct G5 only) | G1 confirmed 108/108; G5 seam adopted by operator 2026-08-10 |

**Batch-3 era** (post ADR r3-0005/0006/0007; clauses registered in film units) — **UNRANKED**: the two rows quote different 5-dataset compositions (the anchor-comparand subset includes `ifc_poisson`; the ADR r3-0007 scored panel includes `pfc` instead) and cannot be ranked against each other:

| Card / arm | Panel geomean skill | Film units | Verdict | Notes |
|---|---|---|---|---|
| r3s2-B3 emulator-ceiling arm, 5-cell anchor-comparand | 10.4763 [10.3176, 10.7785] (anchor subset) | — | confirmed | Does NOT beat the 10.0853 anchor ($\Delta$ +0.3910 = 0.77× seed-mce, pre-registered replication); 6-cell panel 14.1909 [14.0046, 14.5243] (era-stamped historical, ADR r3-0008-C; §12); subset audit below |
| r3s3-B3 knee-prereg arm | 18.6212 [18.0610, 18.9994] (r3-0007 scored 5-ds) | **0.5780** [0.5606, 0.5897] | falsified | Round-best vs the learned baseline (film units, its card's own record); the registered knee claim still failed (§9.2) |

**Anchors and baselines on file.**
Launch best-floor geomean 53.2146 on the ADR r3-0007 5-dataset scored panel (audited lineage 75.0673 → 38.6300 → 36.3912 → 34.4198 → 38.8368 → 53.2146); film-transfer denominator 14.0770 copy-LF units on the batch-1/2 panel (6-ds era 18.6894; ADR r3-0007 5-ds 32.2165); U-Net/film panel ratio 0.9805 — a statistical dead heat, so the film denominator stands.
Every trained round-3 card beat the launch best-floor anchor of its era; the cards that also beat the learned film-transfer baseline (era-matched comparison) are **r3s2-B1, r3s2-B2, r3s3-B1, and r3s3-B3**, while r3s4-B1 (1.40) and r3s1-B1/B2 (1.77) lose to it.

**Subset-geomean audit citations** (pre-report gate; restated 2026-08-12 under ratified ADR r3-0008-C): the original audit pass read every subset against one bar that had been calibrated on a stale five-dataset roster, and the tool's OK/mismatch labels compared the declared panel to itself — both defects are now fixed, and the re-run (archived beside the card's other audit passes) reproduces every original magnitude exactly with the labels the right way around.
Read against bars recertified on their own compositions, the licensed subsets still clear: scored-5 −2.8943 = **2.75×** its own bar (seed-mce 1.0536) and registered-4 −2.7870 = **2.54×** its own bar (seed-mce 1.0961); the panel6 aggregate retires as claim-bearing.
Magnitudes remain subset- and unit-dependent, so subset sentences are quoted with their subset named and no magnitude is carried across subsets.
r3s2-B2's "survives restriction to claimable cells" reads 2.42× the bar in copy-LF units and 0.35× in film units per its own audit pass — the registered 5-cell verdict is exactly unit-invariant; the subset magnitude is not.

> **Mandatory ifc affine-floor disclosure (applies to every ifc number on this page, including both tables above and §9.1's ifc readings; program §2, numbers completed by ADR r3-0009 Option B, ratified 2026-08-12 — adjudication set unchanged, §12).**
> The quoted affine-floor values are single-draw values of an exactly-determined 6-degree-of-freedom fit on 5 rows, and both cells are fold-catastrophic under leave-one-out:
> `ifc_poisson` 1.5938 single-fit → LOO mean 4.2335 (systematic +3.820 ± 0.719 $\tau_{\text{rel}}$, 5/5 folds breach $\tau$);
> `ifc_heat` 0.9584 single-fit → LOO mean 1.8469 (systematic +5.417 ± 4.890 $\tau_{\text{rel}}$, fold sd 10.935 $\tau_{\text{rel}}$, p95 20.534 $\tau_{\text{rel}}$, 3/5 folds breach — the floor crosses skill 1.0 under leave-one-out).
> Per the completed rule, an ifc claim that does not beat BOTH numbers of the pair has learned nothing beyond linearity; skill < 1 on `ifc_heat` is not by itself a strong claim.
> (The LOO mean is the looser of the pair on both cells, so completing the numbers changed no adjudication.)

One recorded bookkeeping split is honoured throughout: `film_denominator.json` ifc rows are aggregate nRMSE while the ifc floor records are per-sample-mean rel-L2 (~1.27× cross-file bias on `ifc_heat`); the tables above quote card-adjudicated skills throughout and never mix the two file conventions (reconciliation is queued, §12).

## 11. Round close

**Round 3 closed on 2026-08-12 with all 10 experiment cards complete and the operator's round-close go.**
Two streams ran to batch 3; two consolidated at batch 2 by their own part-7 recommendations — the first round in which streams closed themselves by recommendation rather than budget exhaustion.
Every claim was confirmed at 3 seeds in-round, so no post-round confirmation queue exists.
Both round questions are answered:

- **Criterion 1 (field reachability) closed in graded form.**
  The complete condition vector demonstrably pays, but at stage 1 only: exact IC information improves the condition→LF emulator by 3.1× / 1.3× / 8.0× (`allen_cahn` / `cahn_hilliard` / `fisher_kpp`), and the factorised head beats the matched one-stage law by +0.5546 skill units, attributable entirely to `cahn_hilliard` — but nothing downstream converts that into field-level structure, and the emulator-ceiling identity (§9.1) says no unity-gain route can.
- **Criterion 2 (value of LF-at-train) is answered with a mechanism.**
  LF's value on the honest panel is entirely the supply of distinct condition rows; the coverage channel has a knee, which is the sample-complexity elbow of the condition→field regression itself — but the knee is *not* predictable by the batch-2 surrogate on new cells (§9.2), because the surrogate is a different learner's learning curve.
- **The best learned results all live in the LF-at-train streams**: the certified 10.0853 (r3s2-B2) and the film-beating set (r3s3-B1, r3s2-B1, r3s3-B3) all exploit LF coverage at train time; the condition-only factorised stream never approached the learned baseline.
  The learned baseline itself is architecture-insensitive at this budget (the U-Net twin is a dead heat), so the denominator choice is robust.
- **The round's integrity record**: two stop-the-line events fired and were repaired without contaminating any frozen number; 20 reusable probe instruments were promoted to `tools/`; and a set of standing methodological rules was extracted (energy-weighted band statistics; subset-unit calibration; per-dataset metrology tolerances; checkpoint↔data binding in every anchor build; spacing-invariance checks for self-referential ladders; surrogate licensing by row-efficiency match).

A round-4 contract is on file (11 items), collected from the flow log and the terminal cards: dispatcher-verified card writes, commit-pinned job dispatch, the unity-gain pre-statement rule for any future pseudo-LF route card, decoupled knee-confirmation ladders, and the queued `nn_condition` floor-definition question, among others.

## 12. Decisions (both governance rulings landed 2026-08-12)

The two decisions that were open at round close were ratified by Eloise on 2026-08-12, via a plain-language decision brief built from ADRs r3-0008 and r3-0009 (each drafted with every cited number re-verified against its primary artifact), and executed the same session with no new training.

1. **The ifc affine-floor rule — RULED: ADR r3-0009 Option B (keep the rule, complete its numbers).**
   `program.md` §2 now pins both floor numbers per cell — the single fit and the leave-one-out mean this page discloses in §10 — and an ifc claim must beat both.
   Because the LOO mean is the looser of the pair on both cells, no shipped number or verdict changed; the rule text now says what the record already said.
   Original status: the explainer was delivered to the operator 2026-08-10; the rule text stood unchanged until she ruled, and the mandatory disclosure (§10) was honoured throughout this page and the round report.
2. **The panel-composition ADR — RULED: ADR r3-0008 Option C (aggregation hygiene + a concentration rule).**
   What changed: report-only datasets leave every claim-bearing average; noise bars are recertified per composition (scored-5 seed-mce 1.0536, registered-4 1.0961 — re-aggregated from the existing certification legs with a control that first reproduced the old certified constant exactly); the audit tool now verifies a bar against the panel it was *actually* calibrated on (its old check compared the claim to itself and could not fail); and any future panel headline must disclose per-dataset shares, the leave-one-out result, and whether its largest contributor is claim-eligible on its own.
   What it means for the batch-3 headline: it restates as a two-cell claim — the LF route beats the matched-budget no-LF denominator on `allen_cahn` ($\Delta\log$ −0.145) and `fisher_kpp` (−0.170), not on `cahn_hilliard` (+0.023); on `ifc_heat` it does (−0.420), but that cell loses to its own nn-condition floor, so it does not carry the panel claim.
   The subset readings survive correct calibration at reduced magnitude (§10: 2.75× and 2.54× their own bars), the six-cell 14.1909 is era-stamped historical, and the direction of every result is unchanged.
   The evidence that drove the ruling, as presented at close:
   The registered-4 batch-3 headline ("the LF route beats the matched-budget no-LF denominator") is 59.1% carried by `ifc_heat` alone — the one cell that fails the split-transfer licence at every seed for a real reason and loses to its own nn-condition floor by 2.30 G5 band-sd.
   `ifc_poisson` is 55.8% of the same headline on the 6-cell panel AND 98.2% of the cross-node drift while REPORT-ONLY — the cell not allowed to carry a claim carries both the effect and the noise.
   Same-seed cross-node drift is 0.62× seed-mce (68% of across-seed spread), so current CIs are seed+run intervals.
   Against demotion of `ifc_heat`: film's win there is structural, not an offset (mean-removed 0.0547 vs floor 0.1526, below the oracle affine residual), per the ADR r3-0007 option-C check.
   (Subset statements cite r3s2-B3's `subset_geomean_unit_audit` 3-seed pass, §10; the ifc disclosure in §10 applies.)
3. **Round-1 2500-epoch full runs** — still on hold per operator (unchanged since 2026-08-01; the round-1 s4 gate-relaxation decision remains a prerequisite for s4's slot).
4. **Reporting-convention reconciliation** — the `ifc_heat` per-sample-mean rel-L2 (floor records) vs aggregate nRMSE (`film_denominator.json`) split (~1.27× cross-file bias) is flagged on the anchor file; a single convention should be fixed the next time either file is regenerated.
   This page never mixes them.

## 13. Benchmark_30 head-to-head (added 2026-08-13): the round-3 winner at full breadth

### 13.1 What we asked

Round 3 certified the initial-condition-stack route model (`r3s2_route`, arm `A1_stack_ic_reg`) as the round's best on its 5-dataset panel (§10).
The natural next question: does that advantage generalize beyond the panel it was developed on?
We trained it and the film-transfer baseline from scratch across the newly published `benchmark_30` release — film on all 30 datasets, the certified model on the 29 its frozen implementation supports (`era5` exceeds its grid cap; predeclared, §13.4) — at 3 seeds × 200 epochs per (model, dataset), under the same stripped-view evaluation protocol as round 3, and compared per-dataset relative-L2 error.

### 13.2 Headline: the certified model is a specialist, not a generalist

Film wins at full breadth.
Over the 29-dataset common set, the film-relative skill geomean (error ratio film/certified; >1 means the certified model is better) is **0.6004**, per-seed 0.5934 / 0.6047 / 0.6032 — the certified model's panel error is ~1.67× film's.
By group: core 0.398, ext 0.785, sharp 0.729 — so even on the sharp-field group, where the certified model's wins concentrate, film is ahead on the group geomean.
Seed scatter is ~2%, so this is not seed luck.

![Fig. 5 — benchmark_30 per-dataset film-relative skill](figures/b30_skill_per_dataset.png)

*Fig. 5 — per-dataset film-relative skill of the certified model (log scale; bars right of 1.0 are its wins), colored by benchmark group, with the panel geomean marked.*

### 13.3 Where it still wins — and what the win set actually is

The certified model wins 5 of 29: `sharp__fisher_kpp_2d` (6.4×), `ext__helmholtz_2d` (5.2×), `sharp__allen_cahn_2d` (2.6×), `sharp__cahn_hilliard` (1.35×), `sharp__phase_field_crystal_2d` (1.22×) — four phase-field / reaction-diffusion problems plus one Helmholtz variant.
Only three of the five sit in its round-3 certification panel; the other two are out-of-panel.
The panel's remaining two members — `ifc_heat` and `ifc_poisson` — flip to film (film ~4.3× and ~2.7× lower error respectively).
This does not contradict round 3, which certified a panel-level advantage; benchmark_30 makes the per-dataset composition of that advantage explicit, and it comes entirely from the sharp-interface cells.
On `ext__helmholtz_2d` the win deserves an asterisk: film is unstable there (rel-L2 4.43 — worse than predicting zero), the certified model sits at 0.86, and neither model can be said to solve the dataset.

### 13.4 Integrity and provenance

- 177 of 177 eligible (model, seed, dataset) runs completed and scored; zero failures.
- `era5` was excluded for the certified model only, predeclared before any full run: the frozen family caps its working grid at 256 and 721×1440 exceeds it; modifying the family would void the certification. Film's era5 error (0.0451) is reported as informational.
- The 30 published `benchmark_30` datasets were verified **byte-identical** (per-array sha256) to the local arrays and to the corrected hub release — the published benchmark needs no correction.
- Reproducibility cross-check: film's `ifc_heat` seed-0 error re-trained here is 0.0268262 vs the round-3 record 0.0268172 under the same metric convention — agreement to 0.03%.
- The report went through the same adversarial fact-check loop as the round-3 record (three rounds, 8 → 1 → 0 findings); the loop's main catch was exactly the §13.3 nuance (the win set is *not* simply "its certified panel"), which was corrected before publication.

### 13.5 Caveats attached to these numbers

1. `ext__pressure_poisson_poiseuille`'s low-fidelity input is block-mean-downsampled fine solution plus noise (the source paper prescribes subsampling); either way it violates our "LF must be a real coarse solve" rule, so its near-tie (0.84) is read with caution.
2. `heat_generated`'s fidelity levels sample inconsistent time windows.
3. Relative-L2 is level-dominated on near-uniform fields: on `sharp__fisher_kpp_2d`, the benchmark manifest's own copy-LF numbers are 0.00062 raw vs 0.02161 mean-removed (35×), so the 6.4× win is protocol-true but metric-sensitive; a mean-removed companion panel is first on the round-4 diagnostics list.
4. *Why* each side wins where it does is deliberately left as labeled hypotheses — the round-3 diagnostic probes (LF-informativeness, per-band spectral error) have not yet been run on these residuals.

### 13.6 What happens next (round 4, approved 2026-08-13)

The goal is now to develop a model that beats film on benchmark_30.
Approved lean start, in order: **Phase 0** — a headroom map of film's error against the campaign's per-dataset floors, the mean-removed metric panel, and spectral/interface residual diagnostics; and **S1** — a training-budget check on film itself (is 200 epochs undertrained? if longer training moves film, the bar moves before any challenger is scored).
Development will iterate on a pre-registered ~12–15-dataset dev subset, touching the full 30 only at certification points, to avoid overfitting the benchmark.
One question Eloise raised is whether the new model must build on film at all: a preliminary screening pass over the pre-existing 2026-07-28 family sweep (30 families × 15 datasets, single seed, non-campaign protocol; 11 datasets overlap benchmark_30) shows film is not uniformly dominant even on core datasets — e.g. one coregionalization family posts 8× lower error on `lid_driven_cavity` — so re-screening the existing family registry under the campaign protocol is proposed for Phase 0, and the backbone choice stays open until that evidence lands.

---

Canonical adjudicated records: `round3/docs/round3_report.md` (source of every §9–§12 number) · `mffp_autoresearch/benchmark30/docs/report.md` + `state/leaderboard.json`, branch `bench30-campaign` (source of every §13 number) · narrative through batch 2: `mffp_autoresearch/PROFESSOR_UPDATE_2026-08-10.md` · figures: `round3/docs/figures/r3_{performance_vs_baselines,architectures_overview,model_detail_ic_stack,model_detail_lf_channels}.png` (regenerated 2026-08-12) and `figures/b30_skill_per_dataset.png` (2026-08-13) · the rendered page is private until shared from its share menu.
