# Websearch Report — Stream `s7_loss`, Batch 2

**Stream**: s7_loss (lever, ADR 0012) — B1 FALSIFIED, mechanism fully resolved
**Batch**: 2
**Total iterations**: 5 (**cap hit: YES** — noted at the top of `iteration_5.md`)
**WebSearch calls**: 15 (3 per iteration)
**WebFetch calls**: 11 attempted / 8 usable (3 failures: `arxiv.org/html/2412.10354v2`
carries no loss definition; `arxiv.org/abs/2107.04497` is abstract-only; the
NeurIPS 2023 PDF endpoint returned binary — the failure mode batch 1 documented)

## Search trace

### Turn 1 — floored relative losses, tempered weighting, published pathologies
Terms: `relative L2 loss neural operator training epsilon denominator clamp normalized loss small norm samples instability`;
`per-sample norm weighted regression loss interpolation between MSE and relative error exponent beta imbalanced regression`;
`pitfalls of relative error training loss operator learning degenerate solution collapse zero prediction stationary point`.
Chosen to test whether B1's "add a denominator floor, keep λ ≤ 1" repair is a
publishable mechanism or an idiom, and whether B1's origin-stationary-point
result is already published.
Key findings: normalized losses are adopted for boundedness / scale-invariance /
interpretability, per-sample target-magnitude normalization is documented as
equalizing "heteroscedastic task difficulty", and epsilon appears **only** as a
numerical-stability patch with — quoting the fetch — "no discussion of failure
modes, degenerate optima, or collapse phenomena"
[cite: https://www.emergentmind.com/topics/normalized-loss-function]. No
operator-learning negative result on relative training surfaced. → `iteration_1.md`

### Turn 2 — jointly trained gain heads, two-term objectives, LF-referenced MF losses
Terms: `learned output scaling head amplitude calibration jointly trained neural operator surrogate predict magnitude and normalized shape separately`;
`two-term loss normalized shape term plus magnitude term deep learning regression scale decomposition training objective`;
`multi-fidelity training loss weighted by low-fidelity residual magnitude supervise correction term objective neural network`.
Key findings: "amplitude calibration" for PDE surrogates means **uncertainty**
calibration [cite: https://arxiv.org/html/2602.11090, https://arxiv.org/html/2412.12069];
the field's own loss survey defines no relative/floored loss and no scale-invariant
loss [cite: https://arxiv.org/html/2307.02694v3]; MF work keeps LF on the
architecture side, loss-side MF = per-fidelity scalar weights
[cite: https://arxiv.org/abs/2310.03572]. **In-repo check made this turn**:
`MFFP_S7_LOSS=rel` is already `mean_i rel_i²` with the denominator clamped at
`1e-4` — "add a denominator floor" is already shipped, and did not prevent the
allen_cahn collapse. → `iteration_2.md`

### Turn 3 — the standard operator loss, skill-score losses, per-sample weighting (ENOUGH declared)
Terms: `neuraloperator LpLoss relative L2 loss definition size_average unsquared standard FNO training loss implementation`;
`skill score loss function training neural network normalize loss by baseline persistence climatology error weather forecasting`;
`per-sample loss weighting inverse baseline error difficulty normalization heteroscedastic scientific machine learning surrogate training`.
Key findings: skill is treated as **verification**, not training
[cite: https://glossary.ametsoc.org/wiki/Skill, https://www.cawcr.gov.au/projects/verification/];
per-sample weighting is a populated idiom space (metric-optimized bilevel
weights Zhao 2018; auxiliary weight net Mellatshahi 2023) whose documented
failure mode is that "excessive boosting of rare examples … can destabilize
training … or distort global performance", and whose page states
baseline-error formulations "are not elaborated"
[cite: https://www.emergentmind.com/topics/weighted-loss-function]; inverse-variance
weighting exists but keys off **label noise**, not reference error
[cite: https://arxiv.org/abs/2107.04497]. **ENOUGH** declared (returns repeating).
→ `iteration_3.md`

### Turn 4 — refutation part 1 (D3, D4, D5)
Terms: `"skill score" as training loss deep learning normalize each sample by reference forecast error downscaling super-resolution baseline-relative loss`;
`loss weight target magnitude power exponent tuning between absolute and relative error regression scale sensitivity alpha`;
`network predicts normalized field and separate scalar amplitude head rescale output per-sample gain regression PDE field super-resolution`.
Key findings: the exponent-swept magnitude weight is the standard imbalance
idiom (inverse-frequency / effective-number / class-distance α)
[cite: https://www.emergentmind.com/topics/class-weighted-loss]; SR and
multiscale-correction work normalizes by **dataset constants**, never a
predicted per-sample gain [cite: https://arxiv.org/html/2406.17244v2,
https://arxiv.org/html/2411.07576v2, https://arxiv.org/pdf/2101.09839]; the
survey has no metric-aligned-training discussion
[cite: https://arxiv.org/html/2307.02694v3]. → `iteration_4.md`

### Turn 5 — refutation part 2 + verdicts (CAP)
Terms: `multi-fidelity loss normalized by low-fidelity error per sample train to beat the low fidelity baseline objective operator learning`;
`sample weighting by reference model error external baseline difficulty score training regression not self-paced focal loss`;
`jointly learned scale factor branch output gain neural network regression predicts unit-norm shape and magnitude two outputs`.
**Decisive finding**: the FNO authors' own library trains by default on the
**unsquared per-sample relative norm** `||x−y||_p / (||y||_p + eps)`, `eps =
1e-8`, no clamping
[cite: https://raw.githubusercontent.com/neuraloperator/neuraloperator/main/neuralop/losses/data_losses.py].
Third independent pass confirms MF loss design = per-fidelity scalar weights
[cite: https://arxiv.org/pdf/2402.18846, https://arxiv.org/pdf/2507.07292].
And, verbatim: "there is no documented evidence of networks predicting
per-sample scalar output gains jointly with normalized predictions for fields,
signals, or PDE surrogates"
[cite: https://www.emergentmind.com/topics/learned-scaling-factors].
→ `iteration_5.md`

## Prior-art verdict

| Candidate direction | Verdict | Citations (fetched) | What remains open |
|---|---|---|---|
| **D1** — A0: `MFFP_S7_LOSS=rel` (λ=1, `mean_i rel_i²`, clamp 1e-4) for 200 ep on `sharp__allen_cahn_2d` alone — card part 7's inherited disambiguation | **preempted** (and no novelty needed) | https://raw.githubusercontent.com/neuraloperator/neuraloperator/main/neuralop/losses/data_losses.py ; batch 1's C-REL row | Nothing novel. Value is **disambiguating B1's own λ>1 mechanism** under three pre-registered outcomes — a measurement of an in-house falsified lever, which §13.3 does not require to be novel. Never write up as a method contribution. |
| **D2** — train the **exact scored functional**: unsquared `mean_i ‖p−y‖₂/‖y‖₂` | **preempted** | https://raw.githubusercontent.com/neuraloperator/neuraloperator/main/neuralop/losses/data_losses.py (`LpLoss.rel()` is `__call__`'s default) ; https://arxiv.org/html/2307.02694v3 (survey defines no such loss) | Mechanism fully owned by the reference implementation of our own architecture family. **Reportable as measurement only**: the champion's global-scaler `F.mse_loss` is a *deviation from the community default*; quantify it. Three concrete variants to keep distinct: unsquared+eps(1e-8) [library] / squared+clamp(1e-4) [B1 `rel`] / global-scaler MSE [champion]. |
| **D3** — per-sample loss weight from the copy-LF error, `w_i ∝ 1/‖y_i−LF_i‖²` ("train the skill") | **preempted-but-MF-composition-open** — *but recommend NOT proposing* | https://glossary.ametsoc.org/wiki/Skill ; https://www.cawcr.gov.au/projects/verification/ ; https://www.emergentmind.com/topics/weighted-loss-function ; https://arxiv.org/abs/2107.04497 ; https://arxiv.org/pdf/2402.18846 ; https://arxiv.org/pdf/2507.07292 | Open: weighting a per-sample field-regression loss by an independent lower-fidelity solve's error. **Contraindicated by our own metric**: §2.2 makes copy-LF a per-**dataset** scalar, so the scored per-sample denominator is `‖y‖`; and on pfc, 62/100 test samples have copy-LF rel-L2 `5.8e-08` (B1 part 6) → weights spanning ~14 orders of magnitude, worse conditioning than the 22.7/5017 `hf_norm_spread` that already cratered B1. Any card must show the `‖y−LF‖` spread first (B1 M6 rule). |
| **D4** — tempered norm weight `w_i = ‖y_i‖^{−2β}`, β∈[0,1], with effective-sample-fraction readout | **preempted** | https://www.emergentmind.com/topics/class-weighted-loss (inverse-frequency / effective-number / tunable α) ; https://www.emergentmind.com/topics/normalized-loss-function | Nothing worth claiming: a knob interpolating two endpoints this stream will already have measured (MSE control, D1/D2). Under §1 it is local-optimum tuning, not a genuine experiment. |
| **D5** — jointly trained per-sample **gain head** + normalized-shape training term | **preempted-but-MF-composition-open** | https://www.emergentmind.com/topics/learned-scaling-factors ("no documented evidence of networks predicting per-sample scalar output gains jointly with normalized predictions for fields, signals, or PDE surrogates") ; https://arxiv.org/html/2602.11090 ; https://arxiv.org/html/2412.12069 (joint heads exist, but for **uncertainty**) ; https://arxiv.org/html/2406.17244v2 ; https://arxiv.org/html/2411.07576v2 ; https://arxiv.org/pdf/2101.09839 (SR normalizes by dataset constants) ; https://ar5iv.labs.arxiv.org/html/1406.2283 (Eigen, via batch 1) | Open: a **predicted** per-sample output gain trained jointly with a normalized-shape objective for MF PDE fields. Three caveats: (i) it is an output-**parameterization** change as much as a loss change (ADR 0012 scopes s7 to the objective; the loss-only form is B1's `amp` at λ ≤ 1 — already built); (ii) `experiment_cards/s1_poisson/batch_3/B3.json` is running the **post-hoc** version now — state the contrast, do not duplicate; (iii) F5/F6/F8 forbid aiming it at pfc / cahn_hilliard. |

## Citations summary

- [neuraloperator library] `neuralop/losses/data_losses.py` — `LpLoss.rel()` = `||x−y||_p/(||y||_p+eps)`, unsquared, `eps=1e-8`, default of `__call__` — https://raw.githubusercontent.com/neuraloperator/neuraloperator/main/neuralop/losses/data_losses.py — used in: iteration_5.md; verdicts D1, D2
- [Normalized Loss Functions topic page] `L̂(x)=L(x)/g(x)`; per-sample target-magnitude normalization to equalize heteroscedastic task difficulty; epsilon only as a stability patch; **no** failure-mode discussion; Normalized Hessian Loss (Huynh et al. 2021) — https://www.emergentmind.com/topics/normalized-loss-function — used in: iteration_1.md; verdict D4
- [Weighted Loss Functions topic page] per-sample weighting for "cost-sensitive learning, metric optimization"; Zhao et al. 2018 bilevel meta-weights; Mellatshahi et al. 2023 auxiliary weight net; failure mode "excessive boosting of rare examples … destabilize training … distort global performance"; baseline-error formulations "not elaborated" — https://www.emergentmind.com/topics/weighted-loss-function — used in: iteration_3.md; verdict D3
- [Learned Scaling Factors topic page] "no documented evidence of networks predicting per-sample scalar output gains jointly with normalized predictions"; global/blockwise/latent/per-parameter-block scaling only — https://www.emergentmind.com/topics/learned-scaling-factors — used in: iteration_5.md; verdict D5
- [Class-Weighted Loss topic page] inverse-frequency / effective-number weighting with swept exponents; class-distance weighted CE with tunable α — https://www.emergentmind.com/topics/class-weighted-loss — used in: iteration_4.md; verdict D4
- [Terven et al.] "Loss Functions and Metrics in Deep Learning" — defines no relative/floored loss, no scale-invariant loss, no metric-aligned-training discussion; only "the value of MSE depends on the scale of the target variable" — https://arxiv.org/html/2307.02694v3 — used in: iteration_2.md, iteration_4.md; verdict D2
- [Batch Inverse-Variance Weighting] "inverse-variance weighted mean square error, based on the Gauss–Markov theorem … robust to near-ground truth samples" (abstract only; no formula obtainable) — https://arxiv.org/abs/2107.04497 — used in: iteration_3.md; verdict D3
- [AMS Glossary — Skill] skill = accuracy relative to a reference (chance / climatology / persistence), a verification concept — https://glossary.ametsoc.org/wiki/Skill — used in: iteration_3.md; verdict D3
- [CAWCR Forecast Verification] reference baselines = climatology / persistence, for verification — https://www.cawcr.gov.au/projects/verification/ — used in: iteration_3.md; verdict D3
- [Direct Learning of Calibration-Aware Uncertainty for Neural PDE Surrogates] joint learning of uncertainty controls at the output head / in spectral modes — https://arxiv.org/html/2602.11090 — used in: iteration_2.md; verdict D5
- [Accurate Surrogate Amplitudes with Calibrated Uncertainties] simultaneous mean + uncertainty prediction — https://arxiv.org/html/2412.12069 — used in: iteration_2.md; verdict D5
- [Residual Multi-Fidelity Neural Network Computing] LF as input / residual target (architecture) — https://arxiv.org/abs/2310.03572 — used in: iteration_2.md; verdict D3
- [Multi-Fidelity Residual Neural Processes] — https://arxiv.org/pdf/2402.18846 — used in: iteration_5.md; verdict D3
- [Discretization-independent multifidelity operator learning] — https://arxiv.org/pdf/2507.07292 — used in: iteration_5.md; verdict D3
- [Near-Field Super-Resolution Network] input/output normalized to [0,1] by dataset constants — https://arxiv.org/html/2406.17244v2 — used in: iteration_4.md; verdict D5
- [Multiscale Corrections by Continuous Super-Resolution] — https://arxiv.org/html/2411.07576v2 — used in: iteration_4.md; verdict D5
- [Variational Multi-scale Super-resolution] normalized basis coefficients in/out — https://arxiv.org/pdf/2101.09839 — used in: iteration_4.md; verdict D5
- [Eigen, Puhrsch & Fergus 2014] scale-invariant log loss (carried from batch 1, fetched there) — https://ar5iv.labs.arxiv.org/html/1406.2283 — used in: batch_1/iteration_4.md; verdict D5

**Unverified leads — MUST NOT be cited** (returned in search summaries but never
fetched, or fetched and unparsable): "Learning Sample Difficulty from Pre-trained
Models" (NeurIPS 2023, PDF returned binary); the Fractions-Skill-Score-as-loss
claim; the batch-loss-ratio normalization described in US patent 12205029; the
"relative-L2 training halves test error vs MSE" folk claim (again unattributable,
as in batch 1); "per-curve normalization makes loss insensitive to absolute
amplitude"; the ACE2 caution about skill-based rollout losses;
`arxiv.org/pdf/2401.17739` ("Operator learning without the adjoint") relative-MSE
plateau.

## Dead ends

- `per-sample norm weighted ... exponent beta imbalanced regression` → returns generic
  regression-metric pages; the construction exists only in the class-imbalance
  literature. D4 is a knob, not a finding.
- `pitfalls of relative error training ... stationary point` → returns classifier
  neural collapse and flooding. **No published negative result on per-sample
  relative training for PDE surrogates exists that I could find** — B1's
  origin-stationary-point analysis may be an unoccupied negative result.
- `amplitude calibration ... neural operator` (2nd batch in a row) → uncertainty
  calibration, or particle-physics scattering amplitudes. The word is unusable
  as a search key.
- PDF endpoints again: `proceedings.neurips.cc/*` returned binary (1/1),
  matching batch 1's 4/4 failure rate on PDF endpoints. `raw.githubusercontent.com`
  worked perfectly and is the recommended route for library-definition questions.

## For the brainstormer

The brainstormer MUST quote the verdict row for whatever it proposes.

1. **There is no unoccupied loss *mechanism* left for this stream.** Five turns
   across two batches (10 iterations, 30 searches) produced `preempted` for
   every loss shape except the gain-head composition, which half-belongs to
   architecture. Propose accordingly: a **measurement card**, not an invention
   card. That is fully compatible with program.md §1 ("an experiment is genuine
   if, whether it succeeds or fails, we learn something").

2. **The single most promising card is D1 + D2 as one objective ladder.** New
   this batch: the FNO authors' own library trains by default on the *unsquared*
   per-sample relative norm with `eps=1e-8` and **no clamp**
   [cite: https://raw.githubusercontent.com/neuraloperator/neuraloperator/main/neuralop/losses/data_losses.py],
   while our champion uses global-scaler `F.mse_loss`. So the stream can settle
   card part 7's λ question *and* measure a documented deviation from community
   practice in one cheap run set: control `mse` → `rel` (λ=1, squared, clamp
   1e-4 — already implemented) → an added unsquared `LpLoss`-form arm. The three
   differ only in per-sample gradient weighting, and B1's algebra
   (`rel² = shape + gain`, residual 4.26e-14) makes each contrast attributable.
   Run on `sharp__allen_cahn_2d` alone first, per card part 7 (~10 min GPU).

3. **Pre-register with B1's own instrumentation, not with new tooling.** Card
   part 7 requires `tools/relative_loss_geometry.py` on the champion's
   predictions before any objective arm, refusing any arm whose `frac_perverse`
   is non-zero at its λ; B1's design rule M6 requires reporting
   `hf_norm_spread` per dataset (≥ ~10 → needs a floor that actually binds;
   ≲ 3 → the objective is a no-op). Note the shipped floor is **absolute**
   (`NORM_FLOOR = 1e-4`) and provably did not bind on allen_cahn — say which
   samples any proposed floor binds on.

4. **If the card wants a second, novel-composition arm, it is D5 — with three
   stated caveats.** The one fetched statement supporting openness is verbatim
   in the verdict row [cite: https://www.emergentmind.com/topics/learned-scaling-factors].
   But (i) a predicted gain is an output-parameterization change, arguably
   outside ADR 0012's scope; (ii) `s1_poisson-B3` is running the post-hoc
   closed-form version right now — quote the contrast or drop the arm;
   (iii) the loss-only version of D5 *is* B1's `amp` restricted to λ ≤ 1, i.e.
   already built and already partly measured. Cheapest honest framing: fold it
   into the ladder as `amp λ=0.5` rather than building a head.

5. **Do NOT propose D3 (copy-LF-weighted loss) or D4 (β-tempered weights).**
   D3 is novel but anti-aligned with the frozen metric (§2.2 makes copy-LF a
   per-dataset scalar) and would put ~14 orders of magnitude of weight spread on
   pfc; D4 is a tuning knob whose endpoints the stream already measures. Both
   verdict rows above give the citations to state this in `prior_art`.

6. **Falsification must clear the certified floors** (`state/noise_floor.json`):
   `sharp__allen_cahn_2d` 1.633 skill is the relevant one for a single-dataset
   card; geomean floor 0.884 if the card goes panel-wide;
   `ext__helmholtz_2d` (9.695) is **report-only** — and B1 proved a zero
   predictor beats the champion there (skill 3.035 vs 18.826), so no helmholtz
   movement may be credited to an objective.

7. **Consider that the honest recommendation may be to close the stream after
   this measurement.** Card part 7 says so explicitly, and B1 part 6 M7 bounds
   what any loss-only lever can do on a substrate that cannot see which regime a
   sample is in (collapse label AUC 0.099 from HF sharpness / 0.102 from LF,
   vs best-of-19 condition coords |AUC−0.5| = 0.067). If the brainstormer
   proposes continuation, it must say what M7 leaves available.
