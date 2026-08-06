# Defect-class red-team report (round 3, 2026-08-06)

Adversarial search for the fifth defect class: ways a panel cell can be meaningless, mismeasured, or gameable that the four preflight instruments (completeness, pairing, fidelity_gap, nn_baseline) do not catch.
All numbers below are measured on the live benchmark bytes via the frozen round-2 eval conventions (`panel_data.copylf_prediction`, variant C / legacy, per-sample mean-of-ratios nRMSE).
Measurement code: `measure.py`; artifacts: `c01..c12_*.json`, `f01..f05_*.json` in this directory.
Nothing outside this directory was written; no benchmark data, round state, or guarded surface was touched.

## STOP-THE-LINE — three FIRES on scored panel datasets

1. **ifc_poisson (scored): LF rungs carry a resolution-dependent amplitude defect of ~(64/r)².**
   Coarse-rung fields are shape-correct but 4.2× / 17.9× / 82.9× too large in RMS at fidelity 32 / 16 / 8.
2. **cahn_hilliard (scored): the panel cell is outlier-dominated and cannot resolve model deltas below ~166%.**
   Five of 100 test rows carry 76% of the copy-LF cell; the cell's own bootstrap CI is [0.0123, 0.0818] around 0.0418.
3. **allen_cahn_2d (scored): 18–25% of test rows are task-void (per-row fidelity gap < 1e-6; 9 rows have LF ≡ HF exactly).**
   The aggregate fidelity_gap check passes while a fifth of the cell measures nothing.

These are data/measurement findings, not model findings; per the round's stop-the-line rule they need adjudication before further batch launches lean on the affected cells.

## The fifth class, named

The four known classes were all *generation-side* (registration, condition export, ladder pairing, sampling composition).
The measured fifth class is **per-cell estimator integrity**: the panel cell is a mean of 100 per-sample ratios, and nothing currently checks that this estimator is (a) fed task-valid rows, (b) not dominated by a handful of outliers, (c) fed rungs on a coherent physical scale, and (d) the same statistic across producers.
All three FIRES are instances: degenerate rows deflate the reference cell, heavy-tailed rows inflate its variance, mis-scaled rungs poison the inputs the cell presupposes, and none are visible to any aggregate-level instrument.

## Candidate table

| id | class | question | measurement (datasets) | verdict |
|----|-------|----------|------------------------|---------|
| C01a | test/train contamination (condition space) | are test conditions near-duplicates of train? | min standardized cond distance, 6 panel datasets (`c01`) | DEAD |
| C01b | target-space collapse | do distinct conditions map to near-identical fields across splits? | field-space NN rel-dist, 6 datasets (`c01`) | FIRES (with C-F2) |
| C02 | split condition shift | do train/test condition distributions differ? | per-column KS + range coverage (`c02`) | LATENT |
| C03 | target-norm pathology | near-zero denominators / level domination? | per-sample ‖y‖, structure fraction rho (`c03`) | FIRES (feeds F2) |
| C04 | metric level-domination | does the DC offset own the denominator? | mean-removed vs raw nRMSE (`c03`) | LATENT |
| C05 | reference/data binding | do baselines still match current bytes? are they bound? | recompute copy-LF vs JSON + md5 across 3 roots (`c05`) | LATENT (clean today, unbound) |
| C06 | ladder monotonicity | is each coarser rung actually worse? | per-rung copy-LF nRMSE (`c06`) | DEAD (monotone everywhere; see F3 caveat) |
| C06b | rung-scale coherence | are rungs on one physical amplitude scale? | RMS ratio, cosine, rescaled residual (`f02`, `f05`) | **FIRES — F3** |
| C07 | condition-vector redundancy | dependent / constant columns? | rank, SVs, max corr (`c07`) | DEAD |
| C08 | dtype/precision seam | does a float32 pipeline change cells? | f32 vs f64 copy-LF nRMSE (`c08`) | DEAD |
| C09 | seed noise vs claimed effects | how big is cross-seed spread per dataset? | rel range across s0–s2 in round-2 results (`c09`) | LATENT (ifc_poisson 11.4%) |
| C10 | cell discrimination power | can one cell resolve model deltas? | bootstrap CI + top-k share (`c10`) | **FIRES — F1** |
| C11 | metric-statistic seam | is `nRMSE` one statistic everywhere? | scalar vs mean(per-sample array), 1506 splits (`c11`, `f04`) | LATENT (217 test splits diverge up to 149%) |
| C12 | stripped-view integrity | any test LF below HF leaked? stale copies? | file census + md5 vs scoring root (`c12`, `f03`) | DEAD |
| — | degenerate zero-task rows | how many test rows have no fidelity content? | per-row copy-LF ratio histogram (`f01`) | **FIRES — F2** |

## FIRES findings

### F3 — ifc_poisson cross-rung amplitude incoherence (`f02_ifc_rung_scale.json`, `f05_ifc_shape_vs_scale.json`)

On the repaired nested ladder (train, 5 HF-aligned rows), LF RMS / HF RMS = 82.9 (fid 8), 17.9 (fid 16), 4.16 (fid 32) — consistent with an amplitude factor ≈ (64/r)², the signature of a missing h² in a finite-difference Poisson solve.
Per-rung copy-LF nRMSE is 81.6 / 16.9 / 3.15 — every LF rung is far worse than predicting zero (nRMSE 1.0), so LF-as-prior is worthless at face value.
Yet mean cosine to HF is 0.992 / 0.998 / 0.9997, and a single per-row scalar rescale collapses the rung error to 0.128 / 0.063 / 0.024 — the fields are shape-correct, purely amplitude-wrong.
ifc_heat, generated by the same repair pipeline, is clean (RMS ratios 1.04 / 1.01 / 1.003), isolating the defect to the poisson coarse solves.
Every existing instrument passes: pairing_report says nested=true (cosine-based, scale-blind), completeness looks at condition→HF, fidelity_gap sees "a gap", nn_baseline never touches LF.
Impact: any round-3 model that consumes ifc_poisson LF rungs is being fed mis-scaled physics; the ifc_heat-vs-ifc_poisson skill contrast partly measures this artifact.
Caveat for adjudication: HF-internal consistency (affine oracle residual 5.4e-16) suggests HF is self-consistent; whether HF or LF carries the wrong absolute scale needs one re-solve at a known analytic case.

### F1 — cahn_hilliard cell is outlier-dominated (`c03_denominators.json`, `c10_discrimination.json`)

Top-1 test row carries 31% and top-5 carry 76% of the copy-LF per-sample ratio sum.
Bootstrap 95% CI of the cell (the scored copy-LF denominator 0.0418) is [0.0123, 0.0818]: half-width ±83% of the mean.
Minimum model delta distinguishable by this cell at 95% confidence: ~166% — larger than most plausible architecture effects.
Mean-of-ratios (0.0418) vs ratio-of-sums (0.197) differ 4.7×, confirming a heavy-tailed per-sample distribution (p95/p5 = 56).
The denominator itself is a sampling accident of which coarsening outliers landed in the 100-row test set; skills on this cell inherit ±80%-scale noise before any model is trained.
For contrast, pfc: CI half-width ±27%, top5 16%; fisher_kpp: ±16%; allen_cahn: ±14%.

### F2 — allen_cahn_2d degenerate zero-task rows (`f01_degenerate_rows.json`, `c01`, `c03`)

18/100 test rows have per-row copy-LF rel-L2 < 1e-6; 9 of them are exactly 0 (LF and HF bit-identical after nested-node sampling — the field is a uniform constant on both grids).
21/100 rows have structure fraction rho < 1e-3 (essentially constant fields); median rho on the remaining rows is ~0.5.
These rows contribute 0 to the copy-LF reference but > 0 to any model, so the cell partly scores "reproduce a constant exactly", and the deflated reference inflates every model's skill number on this dataset.
pfc measures 47/100 such rows — the known r3-0002 uniform-phase composition defect at per-row granularity; this check will certify the crystalline-box regeneration when it lands (expected → ~0).
Corroborating target-space collapse (C01b): 59% of pfc and 25% of allen_cahn test rows lie within 2% relative field distance of some train HF row despite standardized condition distances ≥ 0.6 — a field-space-NN oracle would ace them, and the effective test-set size is far below 100.
fisher_kpp shows the soft version: no zero rows, but 23/100 rows have rho < 0.01 and the median level-domination factor is 38.9 (matches the project-memory 35× rel-L2 caveat).
Existing instruments miss all of this because fidelity_gap and nn_baseline operate on aggregates.

## LATENT findings and proposed checks (preflight.py style: inputs → statistic → threshold → runtime)

### L1 — reference/cache-to-data binding (`c05_staleness.json`)

Measured today: recomputed copy-LF equals `copylf_baselines.json` to 0 rel-diff on all four sharp panel cells + helmholtz, and md5 is coherent across benchmark_42 / factory data root / stripped view.
But nothing enforces this: the score_panel cache key is sha256(code_hash | dataset | epochs | seed) and the baselines JSON carries no hash of the data bytes it was computed from.
The pfc r3-0002 swap is imminent; after a swap, cached cells and the baselines file remain silently valid-looking (this exact silent-staleness pattern is how classes 1–4 survived: artifacts outlive the data they described).
Also measured: pfc regeneration has NOT landed yet (observed box r ∈ [−0.400, −0.101], mean_density ∈ [−0.400, −0.200] vs ADR crystalline box r ∈ [−0.4, −0.3], md ∈ [−0.25, −0.2]) while the current baselines match the current (old) bytes — coherent, but only by luck of ordering.
**Check `data_binding`**: inputs = dataset dir + baselines JSON; statistic = md5 manifest of {train,test} × {LF,HF} files vs a `data_manifest_md5` field recorded in the baselines entry (add via the sanctioned mutation path) and asserted before any score; threshold = exact match else HOLD; runtime < 5 s/dataset.

### L2 — mixed-statistic `nRMSE` key (`c11_metric_seam.json`, `f04_metric_seam_followup.json`)

217 of 710 round-2 test splits report a scalar `nRMSE` that differs > 1% from the mean of their own per-sample array (max 149%, ext__helmholtz_2d r2s4 cells) — the scalar is ratio-of-sums, the scored statistic is mean-of-ratios.
score_panel prefers the array, so scored cells are internally consistent, but any human or report quoting the JSON scalar quotes a different number under the same key (one-enum-per-meaning violation).
48 factory-root test splits carry no per-sample array at all; anything scored through the fallback path is scored under a different statistic that differs by 18% (allen_cahn) to 372% (cahn_hilliard) on panel data.
**Check `result_json_lint`**: inputs = result JSON; statistic = presence of per-sample array on every test split + |scalar − mean(array)|/mean; threshold = array required, divergence < 1e-9 else flag MIXED_STATISTIC; runtime trivial, run inside score_panel's extraction seam.

### L3 — seed-noise ledger (`c09_seed_noise.json`)

Cross-seed (s0–s2) relative range of test nRMSE from real round-2 multi-seed results: sharp datasets ≤ 1.4% (fisher_kpp 6e-5, pfc 0.6%, allen_cahn 0.6%, cahn_hilliard 1.4%) but ifc_poisson 11.4%, sod 14%, heat_local 16%, fluid 12%, helmholtz up to 43%.
Single-seed cells on ifc_poisson cannot support deltas below ~11%; the 3-seed confirm rule is necessary there and on all guards, and any single-seed screening claim should carry the dataset's ledger value.
**Check `seed_noise_floor`**: inputs = existing multi-seed result JSONs; statistic = per-dataset max rel range across families; threshold = WARN when a claimed single-seed delta < ledger value; runtime < 1 s (pure JSON scan).

### L4 — split condition shift (`c02_split_shift.json`)

Sharp panel is clean (worst KS 0.16, ≤ 0.8% of test mass outside train ranges).
ifc_poisson col 4 has KS 0.215 (borderline at n = 100 vs 128) with 3.9% of test rows outside the train range; ifc_heat has 5.5% outside on col 1.
**Check `split_shift`**: inputs = train/test condition matrices; statistic = per-column KS + fraction of test outside train min/max; threshold = KS > 0.3 or outside-fraction > 10% → WARN SHIFT; runtime < 1 s.

### Checks derived from the FIRES

**Check `rung_scale_coherence`** (from F3): inputs = train split, all fidelities; statistics = per-rung RMS(LF)/RMS(HF), mean cosine, and raw vs optimally-rescaled per-row rel-L2; thresholds = RMS ratio ∈ [0.5, 2] AND raw/rescaled < 3 AND per-rung copy-LF < 1.0 (zero-floor) else RUNG_SCALE; runtime < 10 s/dataset.
**Check `degenerate_rows`** (from F2): inputs = test (and train) split; statistic = fraction of rows with per-row copy-LF rel-L2 < max(1e-6, 0.01 × median row gap), plus fraction with rho < 1e-3; threshold ≥ 5% → DEGENERATE_ROWS; runtime < 5 s; doubles as the certification instrument for the pfc regeneration.
**Check `cell_stability`** (from F1): inputs = per-sample ratio array (reference or any scored result — arrays already exist in result JSONs); statistics = top-5 share of the ratio sum and bootstrap 95% CI half-width of the cell mean; thresholds = top5 > 0.4 or half-width > 25% of mean → OUTLIER_DOMINATED, and always report min-detectable-delta next to the skill; runtime < 1 s.

## DEAD candidates (measured, cannot bite here)

- **C01a condition-space contamination**: min standardized test→train condition distance ≥ 0.60 on all sharp panel datasets, 0.10 (ifc_poisson), 0.035 (ifc_heat, 2% of rows < 0.05); no exact duplicates anywhere; LHS sampling with disjoint split seeds is doing its job.
- **C06 ladder monotonicity**: every ladder is strictly monotone (coarser rung = larger gap) on both splits of all 6 datasets — but F3 proves monotonicity alone is insufficient (ifc_poisson is monotone *and* broken), so the check only survives inside `rung_scale_coherence`.
- **C07 condition redundancy**: all condition matrices full rank (18/19/50/5/3 cols), no constant columns, max |off-diag corr| 0.21 — no redundancy to exploit.
- **C08 dtype/precision**: float32 scoring pipeline changes copy-LF cells by ≤ 9.1e-7 relative, and all sharp targets are exactly float32-representable (quantization floor 0); the float64 nrmse.py path is safe even for fisher_kpp's 1.65e-4 cell.
- **C12 stripped-view leaks**: zero test files below the HF level in any stripped dataset dir (the earlier `test_l2`/`test_l5` flags were HF files at hf_fid = 2/5, and ood subdirs carry their own HF); stripped test HF md5 matches the scoring root on all 6 panel datasets.
- **C05 staleness today**: recomputed reference equals the JSON on all measurable cells (rel diff 0) — clean now, which is exactly why L1's binding check should land before the pfc swap makes it dirty.

## Ranked implement-next list

1. **`rung_scale_coherence`** — F3 is a live generator-grade defect on a scored dataset; also the cheapest to adjudicate (one analytic re-solve decides HF-vs-LF scale).
2. **`degenerate_rows`** — fixes the allen_cahn blind spot, quantifies fisher_kpp, and is the natural certification gate for the pending pfc regeneration.
3. **`cell_stability`** — cahn_hilliard skill numbers are currently ±80% sampling noise; every claim on that cell needs the min-detectable-delta printed next to it (or a larger/stratified test set).
4. **`data_binding`** — must land before the r3-0002 pfc swap, or classes 1–5 get a sixth sibling: silent artifact staleness.
5. **`result_json_lint`** — one statistic per key; closes the fallback seam in score_panel's extraction.
6. **`seed_noise_floor`** — free (pure JSON scan), gates single-seed claims on ifc_poisson/guards.
7. **`split_shift`** — currently clean; cheap insurance.

All proposed checks are sub-minute, use only numpy/scipy plus the frozen panel_data conventions, and are implementable in preflight.py's per-dataset record style without touching any guarded surface.
