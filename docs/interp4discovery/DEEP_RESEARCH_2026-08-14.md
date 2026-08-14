# Interp4Discovery paper — consolidated deep research (2026-08-14)

One document holding everything relevant to the planned submission to the NeurIPS 2026 workshop "Interpretability for Discovery".
Paper focus: interpreting **why `mf_fno_transfer_film` is the winning baseline** of the MFFP benchmark.
Autoresearch (round 1-4) results are reserved for a different paper and appear here only where they supply benchmark context.

Detail lives in three companion appendices in this directory, compiled the same day:

- `appendix_A_internal_evidence.md` — every internal report, number, and figure, with file paths.
- `appendix_B_interpretability_literature.md` — external interpretability literature, all citations abstract-verified unless tagged otherwise.
- `appendix_C_baseline_landscape.md` — the multi-fidelity baseline landscape and benchmark-coverage analysis.

---

## 1. Workshop and CFP facts (verified from the live site 2026-08-14)

- NeurIPS 2026 workshop, Atlanta, Dec 12 or 13; **submission deadline 2026-08-29 11:59 PM AoE**; notification on/before 2026-09-29.
- Up to **5 pages main text** (+1 at camera-ready), references and appendices free but main text must be self-contained; NeurIPS 2026 workshop LaTeX template; single PDF via OpenReview.
- Double-blind: strip names, affiliations, acknowledgments, GitHub/HF usernames; cite own prior work in third person.
- Non-archival; concurrent submission elsewhere is fine; already-archival work excluded (NeurIPS 2026 fast track excepted).
- **A responsible-use statement is mandatory; a missing one is grounds for desk rejection.**
- Reviewers are explicitly told to weigh reproducibility; anonymized code via anonymous.4open.science and anonymized data/weights via an anonymous HF account are the recommended channels.
- OpenReview accounts without an institutional email can take up to two weeks to approve — register early (Caltech email avoids this).
- CFP is marked "tentative"; re-check the page before submission.

### Fit

The workshop's four topic buckets include (01) interpretability methods for unfamiliar architectures/modalities beyond language and vision, and (02) "empirical case studies where examining model internals surfaces non-obvious, verifiable knowledge".
A neural-operator case study explaining a benchmark-scale win is a clean 01+02 fit.
The organizers' stated bar: "discovery requires more than a compelling visualization — it requires methods, translation, and validation" — the paper should end in a **testable, validated prediction** (see §6, angle 4).
Failure cases and negative results are explicitly welcome, which de-risks analyses that come back null.

---

## 2. The model the paper interprets

`mf_field/factory_mffp/models/mf_fno_transfer_film/` (full details: appendix A §A).

- 4-block FNO, width 64, modes 12, ~4.7M parameters; network input is only the 2 coordinate channels.
- The condition vector $X$ enters solely via per-block FiLM: affine-free GroupNorm then $\gamma(X)\cdot\hat z + \beta(X)$, with a zero-initialized cond→64→2C MLP and $\gamma = 1 + \gamma_{raw}$, so training starts from an unconditioned FNO.
- Multi-fidelity lives entirely in the schedule: pretrain on abundant LF fields (lr 1e-3), fine-tune the same weights on scarce HF fields (lr 3e-4), same epoch count each stage.
- Two structural facts to lead with: (i) the model **never sees the LF field at inference** — it is a pure $X \to$ field regression, and LF data acts only through weight initialization; (ii) all sample-to-sample variation flows through $4 \text{ blocks} \times 2 \times 64$ modulation parameters generated from $X$ — a narrow, readable conditioning bottleneck.
- Housekeeping before submission: the family dir has no `INSPIRATION.md`, and `beggs2025pdecond` in `manifest.json` is a wrong citation key (actual: Shokar, Kerswell & Haynes, arXiv:2509.09599).

---

## 3. The benchmark evidence base — and which artifact to pin

Three benchmark eras exist with **three different film Elo numbers on record (1936, 1820, 1692)**; the paper must pin one artifact per claim (appendix A §B).

| Artifact | Scale | Protocol | What it establishes |
|---|---|---|---|
| Paper-era leaderboard (`factory_mffp/paper/leaderboard_table.csv`) | 17 models × 15 datasets | 2500 ep, **single seed** (s42), pre-repair pipeline | film geomean rel-L2 0.00815 vs concat 0.01231; wins 14/15; param-matched 2M control 0.01246 |
| 30-family zoo Elo (`docs/reports/` reports) | 30 families × 15 datasets | 2500 ep, single seed | film #1 Elo 1820 but **median tied with concat** (0.0154 vs 0.0151) — robustness, not typical error |
| Pre-round-1 Elo (`PRE_ROUND1_BENCHMARK_REVIEW_2026-08-05.md`) | 12 models × 42 datasets | 2500 ep, pre-repair, known defects | film #1 overall but `convnext_unet_film` overtakes it on non-sharp-20 and core-15 scopes |
| **benchmark_30 head-to-head** (`mffp_autoresearch/benchmark30/worktree/mffp_autoresearch/benchmark30/docs/report.md`, branch `bench30-campaign`) | 2 models × 30 datasets | **3 seeds**, 200 ep, post-repair, byte-verified release | film-relative skill geomean 0.6004 [0.5934, 0.6047]; film wins 24/29 vs the round-3 certified challenger |

Recommendation: pin **benchmark_30** as the primary generalist-win evidence (only artifact with seeds, repaired pipeline, and published byte-verified data), and use the paper-era 15-dataset leaderboard **only** for the conditioning ablation triplet (film / concat / param-matched 2M), disclosed as single-seed.
The mentor's 30-family zoo and the 42-dataset Elo become one-sentence context with their caveats.

Numbers the paper will use (appendix A §B for full tables):

- FiLM vs concat, identical backbone: 0.00815 vs 0.01231 geomean rel-L2 over 15 datasets; the concat baseline's capacity-scaled 2M variant (`mf_fno_transfer_2m`, 0.01246) fails to close the gap, supporting mechanism over capacity.
  Caution (fact-check finding): the 2M variant is param-matched to the *concat* family, not to film (~4.7M per draft §5.5), so capacity is not fully controlled against film itself; audit exact param counts before the paper repeats "param-matched".
- Regime split: film is #1 on both the smooth-10 (0.00176) and hard-5 (0.17545) subsets.
- benchmark_30: per-group film-relative skill geomeans core 0.398 / ext 0.785 / sharp 0.729 (film strongest on core).
- Film's 5 losses cluster: sharp__fisher_kpp_2d 6.42×, ext__helmholtz_2d 5.16× (film catastrophically unstable there, rel-L2 4.43 — worse than predicting zero), sharp__allen_cahn_2d 2.63×, sharp__cahn_hilliard 1.35×, sharp__phase_field_crystal_2d 1.22× — four phase-field/reaction-diffusion problems plus one Helmholtz variant.
- Condition-vector structure of the losses (from `mffp_autoresearch/CONDITION_COMPLETENESS_BRIEFING_2026-08-03.md`): three of the five (pfc, fisher_kpp, allen_cahn) originally had *incomplete* condition vectors (unexported random initial conditions) and were regenerated COMPLETE on 2026-08-03, before benchmark_30 — fisher_kpp_2d now carries a **50-D condition vector** encoding the IC, and cahn_hilliard's 16 IC coefficients were always exported.
  Hypothesis to test (not established, and note ext__helmholtz_2d — the fifth loss — is not a pattern-former): four of film's five losses are pattern-forming datasets, and the three IC-encoding ones ask a small FiLM MLP to decode a high-dimensional IC into spatial pattern structure; both models see the same stripped test views (no LF at test), so any r3s2 advantage there must come from how its architecture processes the condition/IC information, not from reading a test-time LF field — worth dissecting as §6 angles 3-4.
- The two Helmholtz datasets split in opposite directions (ext favors the challenger 5×, sharp favors film 6×), so the win/loss discriminator is dataset-level, not equation-level — a gift for the "predict the regime" analysis.
- Tension to reconcile in the paper: "film buys robustness, medians tie" (zoo view) vs "film is 1.5× better in geomean" (15-dataset view); both are true under their aggregates and the paper should say so.
- In flight: the pilot2500 epoch ladder (jobs 753056-753061, pending as of 2026-08-14) tests whether the 200-epoch verdict is scaling-confounded; only the reused e200 rung exists so far.

### Discrepancy to resolve with Eloise

The requested framing "we benchmarked 8 models across 30 datasets" matches no artifact on disk: the options are 17×15 (paper era), 30×15 (mentor's zoo), 12×42 (pre-round-1), and 2×30 (benchmark_30).
If an 8-model × 30-dataset table is wanted for the paper, the closest honest move is to run a selected ~8-family subset on the benchmark_30 release under the campaign protocol — a real but schedulable compute cost (film's 30×3×200 cost was modest; ~8 families ≈ 4× the campaign's GPU budget) — and it would supersede the era mismatch by putting the conditioning ablation and the generalist claim on one artifact.

---

## 4. What is already established vs still hypothesis

(Full labeled list: appendix A §C.)

Established or strongly supported:

- Mechanism-over-capacity, strongly supported but not fully controlled: identical backbone and the capacity-scaled concat-2M control fails to close the gap, yet the control is matched to concat rather than to film (~4.7M) — keep it qualified until the §3 param audit is done.
- Film wins both smooth and hard regimes.
- The winner never consumes the LF field at inference (code-audited).
- Film's ext__helmholtz_2d instability is measured (mechanism unexplained).
- benchmark_30 integrity: 177/177 runs, byte-verified data, anchor reproduced to 0.03%.

Hypotheses the paper must either measure or drop — this is the paper's core opportunity:

- The central causal story — "a constant concat channel is pure $k=0$, so spectral layers barely transform it and it enters once at the bottom; FiLM re-injects $X$ at every block" — has **no measurement behind it anywhere**.
- Nothing anywhere inspects the learned $\gamma(X)/\beta(X)$: the core interpretability object is completely unmeasured.
- "Film wins where LF is informative / where $X$ pins the solution" — stated as labeled hypotheses in the benchmark_30 report, diagnostics never run.
- The 12-mode spectral wall / misalignment-dipole / MSE-prefers-blur stories are analytic prototypes, never measured on real datasets.
- Few-shot HF sweep (the sharpest testable prediction of the transfer story) was never run.

---

## 5. Related work and novelty (merged internal + fresh external pass)

Novelty claim, refined by both passes (appendix A §D, appendix B §5):

- FiLM+FNO exists (Zhu, Raccuglia & Brenner, arXiv:2511.09729 — autoregressive, equation-aware, **no multi-fidelity, no transfer**; verified).
- The winning recipe itself — LF-pretrain FNO → HF fine-tune — is published as a method paper with no why-analysis (Lyu et al., arXiv:2304.06972).
- **Our search found no prior work that mechanistically interprets what a multi-fidelity surrogate learned — its transferred representation and conditioning pathway — at any scale, let alone benchmark scale** (a due-diligence-qualified absence claim, not an exhaustive one). Nearest neighbors: Villatoro arXiv:2512.02868 (performance-level LF-quality assessment), Meng arXiv:1903.00104 (interpretation by architectural construction), Wang arXiv:2605.14546 (weight-space physics directions, single-fidelity).
- That gap — stated with this citation set as due diligence — is the paper's novelty statement, and it is stronger than the July draft's "FiLM beats concat" framing.

Framing precedents (appendix B §4): the paper's archetype is Grinsztajn et al. arXiv:2207.08815 ("Why do tree-based models still outperform deep learning on tabular data?") — benchmark → simple method wins → one controlled analysis per named hypothesis → distilled lessons.
Kin papers: DLinear arXiv:2205.13504, DomainBed arXiv:2007.01434, label-prop-beats-GNNs arXiv:2010.13993, neural-recommender deflation arXiv:1907.06902.
McGreivy & Hakim arXiv:2407.07218 (weak baselines in ML-for-PDE, Nat. Mach. Intell.) motivates in-domain: a strong-simple-baseline finding plus its explanation is a community service.

Interpretability method sources the paper will cite (appendix B §2-3): FNO spectral analyses (Qin arXiv:2404.07200; Rahaman arXiv:1806.08734; George arXiv:2211.15188; LOGLO-FNO arXiv:2504.04260), FiLM analysis vocabulary (Perez arXiv:1709.07871; Dumoulin et al., Distill 2018; CoDA arXiv:2202.01889), transfer-analysis toolkit (Neyshabur arXiv:2008.11687; Frankle LMC arXiv:1912.05671; CKA arXiv:1905.00414; surgical fine-tuning arXiv:2210.11466), discovery precedents (Boullé Green's-function readout arXiv:2105.00266; Cranmer symbolic distillation arXiv:2006.11287; PINN failure modes arXiv:2109.01050), and function-space SAEs for neural operators (arXiv:2509.03738) as the on-theme bridge to this workshop's mechanistic-interpretability audience.

---

## 6. Candidate interpretability analyses, ranked (the paper's menu)

Each angle is grounded in a cited method (appendix B) and closes a named internal gap (appendix A §G).
Realistic scope for 5 pages: the benchmark figure plus **2-3 of these**, each ending in a claim validated on held-out datasets.

1. **Spectral division-of-labor of the warm start** — per-band error before/after fine-tuning plus per-mode delta-norms of the spectral weights $R(k)$; tests "LF pretraining hands over the low-frequency map; fine-tuning edits the high-$k$ tail". Round-3 per-band probes in the repo already implement much of the measurement. (Qin 2404.07200, Rahaman 1806.08734, George 2211.15188.)
2. **Feature reuse vs rediscovery à la Neyshabur** — CKA between LF-pretrained and HF-finetuned checkpoints, weight distance, linear-interpolation loss barriers vs cold starts; correlate basin membership with per-dataset win margin. (Neyshabur 2008.11687, Frankle 1912.05671, CKA 1905.00414 — mind CKA's small-sample bias, HF sets are small.)
3. **FiLM $\gamma/\beta$ atlas over physical parameters** — the never-inspected core object: per-block/per-channel modulation vs $X$, channel switch-off statistics, embedding of FiLM vectors by physical regime, $\gamma$-sensitivity vs true-field parameter sensitivity. (Perez 1709.07871's own analyses, Distill 2018, CoDA 2202.01889.)
4. **LF-informativeness map predicting per-dataset wins** — regress film's margin across ~30 datasets on pre-computable dataset statistics (linear vs nonlinear LF↔HF correlation, spectral coherence, bilinear-prolongation error); validate the fitted predictor on held-out datasets. This is the analysis only a benchmark this size can do, and it directly meets the workshop's "testable knowledge" bar. (Meng 1903.00104, Villatoro 2512.02868.)
5. **Causal ablations of the two pathways** — FiLM→identity, condition-shuffle, LF-pretrain vs random-init per dataset; Grinsztajn-style "break one advantage at a time". (Meyes 1901.08644, Perez 1709.07871, Grinsztajn 2207.08815.)
6. **Surgical re-freezing to localize the correction** — fine-tune one component at a time (spectral weights above/below a mode cutoff, FiLM generator, lift/proj); report where 90% of the warm-start gain lives. (Lee 2210.11466, Wang 2605.14546.)
7. **Green's-function readout on the (near-)linear datasets** — compare the trained map with analytic kernels on Poisson/heat families; note the winner takes only a finite-dimensional $X$, not a field input, so this needs a dataset-specific construction from $X$ to whatever it parameterizes (forcing for Poisson-type sources, initial state for heat-type problems, or boundary data), or application to the LF-consuming families instead. (Boullé 2105.00266.)
8. **Function-space SAE probe** (stretch/appendix) — SAE-NO on the winner's latents. (Tolooshams 2509.03738.)

Natural 3-analysis bundle: **1 + 3 + 4** (spectral story, FiLM atlas, win predictor) — one per named hypothesis, Grinsztajn shape, with 5 as the causal glue if space allows.
A bonus dissection target: the measured-but-unexplained ext__helmholtz_2d blowup (rel-L2 4.43, seed spread [3.13, 5.75]) as the paper's failure-case exhibit.

---

## 7. Should we benchmark other models? (recommendation)

Short answer: **no new heavyweight models; add 2-3 cheap controls** (full analysis: appendix C).

- The literature splits into two disjoint baseline lineages: GP/neural-process (AR(1), NARGP, IFC, GAR, ContinuAR, MFRNP, FIRE) and neural-operator field-to-field (FNO/DeepONet variants, U-Net correctors, interpolation controls); no paper runs both.
  The current design touches both — lineage B by in-house implementation, lineage A via the published IFC (arXiv:2207.00678) and MFRNP (arXiv:2402.18846) numbers used as anchors — with the honest caveat that the anchors are indicative published-number comparisons, not controlled reruns (appendix A §B6); the symmetry defense (those papers never run FNO-class baselines either) should still be stated.
- Same-task-shape published precedent to mirror and cite: **Multi-Fidelity Flow Matching, arXiv:2605.16118 (May 2026)** — same benchmark contract (LF field + params → HF field; note our winner's *inference* contract is pure $X \to$ field, which the paper should distinguish) — its verified baseline table is bilinear upsampling + FNO-direct/FNO-residual/DeepONet-residual + F-FNO/CNO/PDE-Refiner, and it makes the bilinear no-learning error the structural "task-difficulty zero line".
- Every major benchmark's floor set is {FNO, U-Net} + one trivial control (PDEBench, PDEArena, The Well, CFDBench — all verified); none require GP methods or foundation models.
- The real exposure of the current set is not count but (i) **no no-learning control** and (ii) **no explicit single-fidelity/linear floor**; a reviewer cannot see whether the datasets are hard or whether LF matters.

Protocol constraint the plan must respect (fact-check finding, confirmed against the campaign report): the benchmark_30 headline ran under the round-3 **stripped-view protocol, whose test views have LF physically absent** — so LF-at-inference controls (prolongation, AR(1)) *cannot* be leaderboard rows comparable to the 0.6004 headline.
The paper therefore declares an explicit protocol split: interpolation/linear controls are reported on the LF-available view (or as dataset statistics), and only pure $X \to$ field or LF-at-train-only models sit in the stripped-view table.

Add before submission (about a week of low-risk work, in priority order):

1. **Bilinear/bicubic LF→HF prolongation error, computed as a per-dataset statistic** — hours; needs no protocol at all (it is a property of the data), serves as the MFFM-style task-difficulty zero line, and is the covariate analysis 4 (§6) regresses against; optionally also a table row on the LF-available view, labeled as such.
2. **Linear AR(1)-style map** ($\rho \cdot LF + \delta(X)$, ridge) — ~1 day; brackets the task as no-learning / linear / deep on the LF-available view and pre-empts the classical-MF objection.
3. **Cold-start FNO floor** (skip the LF pretrain stage; the winner has no LF input, so this ablates the warm start, not an input channel) — establishes that LF *pretraining* does the work; MFRNP's SF-NP precedent; runs cleanly under the stripped view.

Do **not** add Poseidon/DPOT/AROMA/UPT/UPS-class models: all are rollout-oriented (task-shape mismatch), 15 days is not enough to tune them fairly on 30 datasets, and an under-tuned foundation baseline is a bigger review liability than its absence.
Transolver++ has no official public repo (verified 404) and targets million-scale meshes; the in-house Transolver hybrids already pre-empt the Transolver objection.
Correct treatment for all of these: one related-work sentence on task-shape mismatch.

---

## 8. Caveats and disclosures the paper must carry

(Complete list with sources: appendix A §E; most are scoped to specific artifacts.)

- era5 ≡ pm_test byte-identical duplicate — the 15-dataset leaderboard double-counts era5; disclose or drop one.
- The two Helmholtz datasets are closed-form recoverable from $X$ (2.2e-13 via two FFTs) — cannot support a multi-fidelity claim; keep them out of headline aggregates or disclose.
- rel-L2 is level-dominated on near-uniform fields (fisher_kpp copy-LF raw 0.00062 vs mean-removed 0.02161, 35×) — pair headline rel-L2 with mean-removed companions before citing the 6.4× film loss there.
- Condition-completeness history: sharp__pfc/fisher_kpp/allen_cahn originally omitted their random ICs from $X$ (an impossible deterministic mapping) and were regenerated COMPLETE on 2026-08-03 pre-benchmark_30 (`CONDITION_COMPLETENESS_BRIEFING_2026-08-03.md`); the repair left fisher_kpp_2d with a 50-D IC-encoding condition vector (the repo's "$X$ small, ≤~10" norm is intentionally waived there), which any FiLM-atlas or win-predictor analysis must model explicitly.
- `ext__pressure_poisson_poiseuille` LF is block-mean(HF)+noise (violates the real-coarse-solve rule, inherited from its source paper); `heat_generated` has a fidelity time-window inconsistency.
- The paper-era 15-dataset numbers are single-seed and pre-repair (the 2026-08-01 registration fix); benchmark_30 is the post-repair, 3-seed artifact.
- Pre-round-1 42-dataset Elo defects (7 wrong-target datasets, defective LF training signal, champion flips to `convnext_unet_film` on clean scopes) — disclose if that artifact is cited at all; better to not cite it.
- In the pre-repair 42-dataset review artifact (2026-08-05), every model lost to a corrected copy-LF resample on the 2-D sharp panel by 4-147× — that benchmark ranked degrees of failure there; the sharp datasets' contracts and copy-LF denominators changed with the 2026-08-03 repair, so recompute this comparison on the current release before reusing the framing.
- 200-epoch protocol: the epoch-ladder pilot (in flight) will say whether rankings move with training budget; hold a caveat sentence for it.

Also required by the venue: the responsible-use statement, and an anonymized code/data release (the benchmark_30 release is already on HF as `eloisezeng/mf_field` — it would need an **anonymous** mirror for review).

---

## 9. Reusable figures and tables

(Full inventory: appendix A §F.)

- `mf_field/factory_mffp/paper/make_figures.py` regenerates 5 paper-era figures (leaderboard bar, per-dataset error bars, regime split, film/concat ratio, Elo) from `mf_field/factory_mffp/results/raw_bench/`; all PNGs are git-ignored, so every figure is regenerate-on-demand.
- benchmark_30: the professor-update Figs 1-2 (per-dataset skill bars; the 5 wins in absolute error) regenerate via `mffp_autoresearch/tools/render_b30_update_figure.py` (PNGs git-ignored, not checked in); per-dataset 3-seed table and machine-readable `state/leaderboard.json` under `mffp_autoresearch/benchmark30/worktree/mffp_autoresearch/benchmark30/` (branch `bench30-campaign`).
- Sharp-report analytic-prototype figures (spectral wall, misalignment dipole, MSE-prefers-blur) — reusable as motivation only, clearly labeled analytic.
- `mf_field/datasets_summary.csv` — canonical dataset panel table.
- All new interpretability figures follow the `scientific-figures` skill conventions.

---

## 10. Fifteen-day plan sketch (to 2026-08-29)

1. Days 1-2: decisions (§11), add the three cheap controls (§7), start the $\gamma/\beta$ atlas extraction (checkpoints for benchmark_30 film runs already exist under `mffp_autoresearch_outputs/benchmark30/rev-eac7b48e/results/mf_fno_transfer_film/ckpt_*`).
2. Days 3-7: run the chosen 2-3 analyses (§6) on existing checkpoints + the new controls; seed the LF-informativeness regressors with the bilinear-prolongation errors.
3. Days 8-11: draft (reuse `paper/paper_draft.md` §2-3 problem setup and taxonomy; new results sections); figures.
4. Days 12-13: internal fact-check convergence loop; anonymized repo + data mirror; responsible-use statement.
5. Day 14: buffer; submit before the AoE deadline.
6. Parallel: OpenReview account check now; watch the pilot2500 ladder for the epoch-budget caveat.

---

## 11. Decisions needed from Eloise

1. Resolve the "8 models × 30 datasets" reference (§3): cite existing artifacts as-is, or run an ~8-family subset on benchmark_30 under the campaign protocol to unify the evidence base?
2. Pick the 2-3 analyses from §6 (recommended bundle: 1 + 3 + 4).
3. Approve adding the three cheap baselines (§7) — new compute, though small.
4. Confirm benchmark_30 as the pinned primary artifact (§3).
