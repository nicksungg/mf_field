# Websearch Report — Stream `r2s2_stacked`, Batch 2

**Stream**: `r2s2_stacked` (lever)
**Batch**: 2
**Total iterations**: 4 (cap 5)
**WebSearch calls**: 12 (3 per iteration, cap respected)
**WebFetch calls**: 10 over 9 distinct sources (one source, arXiv:2507.18813, fetched twice —
the PDF fetch produced an unsupported reading that the `/abs/` fetch refuted; both recorded)
**Cap hit**: NO — `ENOUGH` declared at the end of iteration 3; iteration 4 spent entirely on
§3.3 refutation

## Search trace

### Turn 1 — the three things B1's mechanism result makes decidable by literature
Terms: (1) generative emulator *sample* (not conditional mean) fed to a downstream corrector;
(2) conditional-mean collapse as a *diagnosis* of incomplete conditioning; (3) spectral
coherence as an eligibility criterion for correction. Chosen because part 7's two options and
the implicit methodological contribution each hinge on one of them.
- The published composition is **deterministic operator → generative corrector**, not the
  reverse [cite: https://arxiv.org/pdf/2507.02106,
  https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2024MS004395].
- **VERIFIED** "Diagnosing the Conditional-Mean Barrier in Scientific ML Surrogates" gives the
  published vocabulary and a decision rule for exactly the LEARNING-gap vs STRUCTURAL-ceiling
  fork ("deterministic underfitting or conditional variability irreducible relative to the
  chosen input X"), but covers no rank collapse, no coherence, no stacked correctors
  [cite: https://arxiv.org/html/2605.28076].
- **VERIFIED, the key hit**: FreqNO-DPS proposes a cross-spectral coherence diagnostic as *"a
  prerequisite check for applying the method to any new surrogate"*, with the corrector trained
  on real HF solves and applied to a frozen surrogate's predicted field
  [cite: https://arxiv.org/html/2606.03936]. → `iteration_1.md`

### Turn 2 — the two part-7 options in their own literatures
Terms: sample-vs-ensemble-mean under a pointwise metric; factorised amplitude/shape heads for
resonant parametric problems; POD/reduced-basis + parameter regression.
- K-sample posterior mean is the field-standard defence of rel-L2 under a generative stage
  (in-repo `docs/reports/MF_Sharp_HighFreq_Report.md` 203/317; PDE-Refiner arXiv:2308.05732) —
  which returns exactly the conditional mean B1 measured at gamma_b1 <= 0.52.
- **VERIFIED** FaNO factorises transient vs persistent responses, NOT amplitude vs shape, and
  never mentions resonance/Helmholtz [cite: https://arxiv.org/abs/2606.16900].
- **VERIFIED negative** PODNO is a spectral operator method, "not a classical reduced-order
  model mapping parameters to coefficients" [cite: https://arxiv.org/html/2504.18513v1/] — so
  the ifc_poisson prior art is the Hesthaven-Ubbiali line, checked in turn 3. → `iteration_2.md`

### Turn 3 — verify the classical baseline, the I8 principle, generative MF pipelines
Terms: Hesthaven & Ubbiali; data-processing inequality for cascaded surrogates;
conditional generative models of LF fields from parameters.
- [Hesthaven & Ubbiali 2018] POD basis + network approximating reduced coefficients from the
  parameters, offline/online split
  [cite: https://ui.adsabs.harvard.edu/abs/2018JCoPh.363...55H/abstract] (snippet-level; ADS
  body empty, ScienceDirect/ResearchGate 403).
- DPI: "post-processing cannot increase information"
  [cite: https://en.wikipedia.org/wiki/Data_processing_inequality] — I8 is a theorem, not a
  finding.
- **VERIFIED** MFFM requires a real LF solve at inference (*"MFFM operates downstream of
  S_LF"*) and freezes nothing [cite: https://arxiv.org/html/2605.16118]; **VERIFIED** the
  probabilistic MF flow needs only parameters at test but has "no separate downstream model"
  [cite: https://arxiv.org/html/2602.00072]. `ENOUGH` declared. → `iteration_3.md`

### Turn 4 — refutation pass + verdicts
Terms: surrogate-generated inputs into a real-solve-trained corrector; amplitude/shape output
heads; training-free correctability criterion.
- D1 topology: **no usable results** across three independent framings — composition open.
- **VERIFIED, self-correction**: scale-consistent learning's "scale" is DOMAIN SIZE, not
  amplitude [cite: https://arxiv.org/abs/2507.18813]; the earlier PDF-fetch reading claiming an
  amplitude/normalised factorisation was fabricated and is discarded.
- D3 term: **No usable results.** ("go/no-go" collides with neuroscience.) → `iteration_4.md`

## Prior-art verdict

| Candidate direction | Verdict | Citations (fetched / returned this loop) | What remains open |
|---|---|---|---|
| **D1** realisation-aware (stochastic / ensemble) stage-1 pseudo-LF → corrector trained on REAL coarse solves, falsified in coherence units, on cahn_hilliard (part 7 option A) | `preempted-but-MF-composition-open (cite)` | MFFM https://arxiv.org/html/2605.16118 (VERIFIED: LF solve required at inference, no frozen stage); probabilistic MF flow https://arxiv.org/html/2602.00072 (VERIFIED: condition-only at test, no downstream model); Geneva & Zabaras https://arxiv.org/abs/2006.04731; operator→diffusion-corrector ordering https://arxiv.org/pdf/2507.02106; FreqNO-DPS https://arxiv.org/html/2606.03936 (VERIFIED) | The exact topology (parameter → *sampled* LF realisation → corrector trained on real coarse solves) and a coherence-threshold acceptance criterion appear in no fetched source. But the outcome is predicted negative by three lines: K-sample mean = conditional mean; an independent sample has coherence 0 with the test realisation in expectation; DPI |
| **D2a** factorised amplitude x normalised-shape head for `ext__helmholtz_2d`, condition→HF (part 7 option B, first half) | `novel (thin — must not be the claim)` | FaNO https://arxiv.org/abs/2606.16900 (VERIFIED: transient/persistent, not amplitude/shape); scale-consistent learning https://arxiv.org/abs/2507.18813 (VERIFIED: domain rescaling, has a Helmholtz experiment); HNO https://doi.org/10.3390/app16125997 (per-mode multiplicative gating, snippet-level) | No exact match found in 3 targeted terms, but output/target normalisation is generic practice and this loop did not exhaustively cover it. Open content is the DIAGNOSIS (FiLM code eff-rank 1.00 in all 4 blocks while the map is continuous at nn-cosine +0.931), not the head |
| **D2b** closed-form / linear-in-condition (POD + ridge) head on `ifc_poisson` (part 7 option B, second half) | `preempted (cite)` | Hesthaven & Ubbiali 2018 https://ui.adsabs.harvard.edu/abs/2018JCoPh.363...55H/abstract + https://www.sciencedirect.com/science/article/abs/pii/S0021999118301190 (snippet-level); kernel-POD https://www.sciencedirect.com/science/article/abs/pii/S0898122121003928; GPR variant https://arxiv.org/pdf/2103.12472; PODNO is NOT this prior art https://arxiv.org/html/2504.18513v1/ (VERIFIED) | Nothing on the mechanism. Only the MEASUREMENT is open: on this benchmark a 4.78 M-parameter FiLM-FNO sits at 0.0821 where a rank-8 POD+ridge is exact to 6.2e-08 at N_hf = 5. Run as a DECLARED BASELINE |
| **D3** training-free coherence eligibility precondition (gamma_b1 + oracle-Wiener ceiling) as a round-level go/no-go before building any corrector | `preempted-but-MF-composition-open (cite)` | FreqNO-DPS https://arxiv.org/html/2606.03936 (VERIFIED: *"prerequisite check for applying the method to any new surrogate"*, *"off-diagonal cross-spectral coherence diagnostic"*); SCP metric https://arxiv.org/pdf/2509.23074; in-repo coherence<0.7 cutoff `docs/reports/MF_Sharp_HighFreq_Report.md` 226/295/336 | FreqNO-DPS's diagnostic validates an ASSUMPTION OF ITS OWN FILTER (Fourier-diagonal residual covariance). r2s2's rule is a CALIBRATED THRESHOLD ON CORRECTOR VALUE (0.52 < gamma_b1 < 0.95 bracketed by the real→pseudo interpolation) plus an oracle-Wiener upper bound. No fetched source calibrates coherence against realised corrector value-add |
| **D4** closure claim: a deterministic intermediate is a re-parameterisation, so the stacked class is dead on this benchmark (I8) | `preempted (cite)` as a principle; open as a measurement | DPI https://en.wikipedia.org/wiki/Data_processing_inequality, https://people.ece.cornell.edu/zivg/ECE_5630_Lectures7.pdf, https://theses.eurasip.org/document/information-loss-in-deterministic-systems/; end-to-end > staged: CALM-PDE https://arxiv.org/abs/2505.12944 (batch-1), MFFM https://arxiv.org/html/2605.16118 (VERIFIED) | No fetched source states the DPI for stacked PDE surrogates or measures the resulting ceiling on field-valued MF benchmarks. Claim the measurement, cite the theorem for the principle |

## Citations summary

- [Diagnosing the Conditional-Mean Barrier] — https://arxiv.org/html/2605.28076 — iteration_1 (term 2, VERIFIED fetch)
- [FreqNO-DPS] "Correcting Neural Operator Spectral Bias via Diffusion Posterior Sampling with Sparse Observations" — https://arxiv.org/html/2606.03936 — iteration_1 (term 3, VERIFIED fetch)
- [Finn et al. 2024] "Generative Diffusion for Regional Surrogate Models From Sea-Ice Simulations", JAMES — https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2024MS004395 — iteration_1 (term 1, snippet-level)
- [Hybrid Operator-Diffusion MHD] — https://arxiv.org/pdf/2507.02106 — iteration_1 (term 1, snippet-level)
- [ENMA] — https://arxiv.org/html/2506.06158v1 — iteration_1 (term 1, snippet-level)
- [Neural Operator Processes under Partial Observations] — https://arxiv.org/pdf/2606.22946 — iteration_1 (term 2, snippet-level)
- [Diagnosing Failure Modes of Neural Operators] — https://arxiv.org/pdf/2601.11428 — iteration_1 (term 2, snippet-level)
- [Beyond Model Ranking / SCP] — https://arxiv.org/pdf/2509.23074 — iteration_1 (term 3, snippet-level)
- [PODiff] — https://arxiv.org/html/2605.03399 — iteration_2 (term 1, snippet-level)
- [Ensemble sampling for diffusion priors] — https://arxiv.org/html/2506.03979 — iteration_2 (term 1, snippet-level)
- [DPS super-resolution under Gaussian noise] — https://arxiv.org/abs/2512.21797 — iteration_2 (term 1, snippet-level)
- [FaNO] "Factorized Neural Operators Decompose Dynamic and Persistent Responses" — https://arxiv.org/abs/2606.16900 — iteration_2 (term 2, VERIFIED abstract; the PDF fetch at /pdf/2606.16900 was unparsable)
- [HNO] "FFT-Free Neural Operators for Helmholtz Scattering via Adaptive Coefficient Modulation" — https://doi.org/10.3390/app16125997 — iteration_2 (term 2, snippet-level)
- [OOD risk bounds, Helmholtz] — https://arxiv.org/pdf/2301.11509 — iteration_2 (term 2, snippet-level)
- [Learned frequency-domain scattered wavefields] — https://arxiv.org/html/2405.01272 — iteration_2 (term 2, snippet-level)
- [PODNO] — https://arxiv.org/html/2504.18513v1/ — iteration_2 (term 3, VERIFIED fetch, used as a NEGATIVE)
- [Hesthaven & Ubbiali 2018] JCP 363:55-78 — https://ui.adsabs.harvard.edu/abs/2018JCoPh.363...55H/abstract (fetched, empty body) / https://www.sciencedirect.com/science/article/abs/pii/S0021999118301190 (403) / https://scholar.google.com/scholar_lookup?title=Non-Intrusive+Reduced+Order+Modeling+of+Nonlinear+Problems+Using+Neural+Networks — iterations 2 and 3 (snippet-level, three concordant index records)
- [Salvador, Dede', Manzoni] kernel-POD NIROM — https://www.sciencedirect.com/science/article/abs/pii/S0898122121003928 — iteration_2 (term 3, snippet-level)
- [Neural-POD] — https://arxiv.org/html/2602.15632v2 — iteration_2 (term 3, snippet-level)
- [NIROM via Gaussian process regression, EM scattering] — https://arxiv.org/pdf/2103.12472 — iteration_3 (term 1, snippet-level)
- [Data processing inequality] — https://en.wikipedia.org/wiki/Data_processing_inequality ; Cornell ECE 5630 L7 https://people.ece.cornell.edu/zivg/ECE_5630_Lectures7.pdf ; https://theses.eurasip.org/document/information-loss-in-deterministic-systems/ — iteration_3 (term 2, snippet-level)
- [MFFM] "Multi-Fidelity Flow Matching: Cascaded Refinement of PDE Solutions" — https://arxiv.org/html/2605.16118 — iteration_3 (term 3, VERIFIED fetch)
- [Generative-AI-enhanced Probabilistic MF Surrogate via Transfer Learning] — https://arxiv.org/html/2602.00072 — iteration_3 (term 3, VERIFIED fetch)
- [Geneva & Zabaras] "Multi-fidelity Generative Deep Learning Turbulent Flows" — https://arxiv.org/abs/2006.04731 — iteration_3 (term 3, snippet-level)
- [Spatial autoregressive transport maps for MF downscaling] — https://arxiv.org/html/2509.22474v1 — iteration_3 (term 3, snippet-level)
- [Learning Where to Simulate] — https://arxiv.org/pdf/2606.09949 — iteration_4 (term 1, snippet-level)
- [Generative Neural Operators through Diffusion Last Layer] — https://arxiv.org/pdf/2602.04139 — iteration_4 (term 1, snippet-level)
- [NN surrogate performance for uncertainty propagation] — https://arxiv.org/html/2605.16078 — iteration_4 (term 1, snippet-level)
- [Scale-Consistent Learning for PDEs] — https://arxiv.org/abs/2507.18813 — iteration_4 (term 2, VERIFIED abstract; refutes the /pdf/ fetch of the same source)
- [Multiscale Neural PDE Surrogates / downscaling] — https://arxiv.org/html/2507.18067v1 — iteration_4 (term 2, snippet-level)
- [Error modeling for surrogates of dynamical systems] — https://arxiv.org/abs/1701.03240 — iteration_4 (term 3, snippet-level)
- In-repo prior websearches (cited, not re-derived): `docs/reports/MF_Sharp_HighFreq_Report.md`
  lines 203/221/252/295/317/336 (K-sample posterior mean, PDE-Refiner arXiv:2308.05732,
  perception-distortion arXiv:2104.07636, RG stochasticity arXiv:1704.06279, coherence<0.7
  band cutoff); `docs/reports/MF_Leaderboard_Beaters_2026_Report.md` §3.2/§3.3 (FreqNO-DPS as
  [HF-2] line 102, MFFM as [N2])
- Batch-1 carry-over (fetched in batch 1, not re-fetched): CALM-PDE
  https://arxiv.org/abs/2505.12944 §4.3; Xu et al. https://arxiv.org/abs/2310.00057;
  Yang et al. https://arxiv.org/html/2503.17941v1

## Dead ends

- `training-free criterion ... go/no-go correctability test` → neuroscience go/no-go literature;
  the vocabulary does not exist in surrogate modelling. Use "prerequisite check" /
  "diagnostic" instead (that is how FreqNO-DPS names it).
- `stochastic sample surrogate input to correction network ... input distribution mismatch` →
  returns *training-data coverage* work (active sampling), not stacked-input realisation shift.
  Confirms batch-1's dead end: the PDE community has no vocabulary for this.
- Large arXiv **PDF** fetches remain unsafe: `/pdf/2606.16900` unparsable; `/pdf/2507.18813`
  produced a **confidently wrong** summary (claimed amplitude/shape factorisation; the abstract
  says domain rescaling). Always fetch `/abs/` or `/html/`.
- ScienceDirect (403) and ResearchGate (403) remain unfetchable; ADS abstract pages return an
  empty body; Semantic Scholar API returned HTTP 429. Hesthaven & Ubbiali stays snippet-level.

## For the brainstormer

1. **If you propose part 7 option (A), you must quote D1 verbatim**: *"D1 —
   `preempted-but-MF-composition-open (cite)`: the exact topology (parameter → sampled LF
   realisation → corrector trained on real coarse solves) appears in no fetched source; the
   published multi-fidelity generative pipelines either require a real LF solve at inference
   (MFFM, https://arxiv.org/html/2605.16118 — 'MFFM operates downstream of S_LF', all levels
   optimized jointly, nothing frozen) or are single condition→HF models with no downstream
   corrector (https://arxiv.org/html/2602.00072)."* And you must answer the negative prior in
   the design, not around it: the field's standard way to keep a generative stage from hurting
   a pointwise metric is the K-sample posterior mean, which is exactly the conditional mean B1
   measured at gamma_b1 <= 0.52; an independently drawn sample has coherence 0 with the test
   realisation in expectation. Say what your stage 1 conditions on that the conditional mean
   does not have. If the answer is "nothing", the arm is refuted before it runs.
2. **Pre-register in coherence units, and put the go/no-go BEFORE the SLURM submit.** B1's part 7
   already specifies it: the surrogate must lift gamma_b1(surrogate, HF) from 0.516 to >= 0.95 on
   the held-out TRAIN slice, measurable training-free with
   `tools/surrogate_coherence_eligibility.py`. Note that the eligibility-rule framing itself is
   D3 = `preempted-but-MF-composition-open` (FreqNO-DPS https://arxiv.org/html/2606.03936 already
   calls a cross-spectral coherence diagnostic "a prerequisite check for applying the method to
   any new surrogate"); what is open is the *calibration against realised corrector value*, so
   claim the calibration, not the idea.
3. **If you propose part 7 option (B), split the verdicts.** ifc_poisson's closed-form head is
   D2b = `preempted (cite)` — [Hesthaven & Ubbiali 2018] POD basis + parameter→coefficient
   regression, https://ui.adsabs.harvard.edu/abs/2018JCoPh.363...55H/abstract — so it enters as a
   **declared baseline arm**, and the reportable content is the measurement (rank-8 POD+ridge
   exact to 6.2e-08 vs a 4.78 M-parameter FiLM-FNO at 0.0821, N_hf = 5). helmholtz's amplitude x
   shape head is D2a = `novel (thin)`; propose it as the implementation of a measured diagnosis
   (FiLM code eff-rank 1.00 in all four blocks), never as an architectural contribution, and note
   that scale-consistent learning (https://arxiv.org/abs/2507.18813) already runs a Helmholtz
   experiment with a different notion of "scale" (domain size).
4. **If you propose closing the stream (the clean negative), quote D4**: the principle is the
   data-processing inequality (https://en.wikipedia.org/wiki/Data_processing_inequality) — claim
   the *measurement on a field-valued MF benchmark*, not the principle. Note the corroborating
   direction of travel: every fetched stacked design that reports the comparison prefers
   end-to-end to frozen stages (CALM-PDE §4.3 https://arxiv.org/abs/2505.12944; MFFM optimises
   all levels jointly), so a frozen-stack negative is consistent with the field, not surprising
   to it — which lowers its publishable value and raises the bar on the *mechanism* (the
   coherence law) being the contribution.
5. **There is published vocabulary for the fork you are in — use it.**
   https://arxiv.org/html/2605.28076 names the conditional-mean barrier and gives a decision rule
   (residual-feature orthogonality probes, effect size = removable residual variance,
   explained-variance ceiling) for deciding "deterministic underfitting vs irreducible
   conditional variability relative to X" — which is exactly B1's LEARNING-gap vs
   STRUCTURAL-ceiling taxonomy. Adopting its statistics makes the r2s2/r2s4 result legible and
   costs nothing; it does not cover rank collapse, coherence, or stacked correctors, so it does
   not preempt the stream's own measurements.
6. **Budget reality check against program.md §1.** B1 landed panel geomean 14.076 vs anchor
   23.064, with the corrector worth <= 0.08% on five of six columns. Option (A)'s ceiling on
   cahn_hilliard is ~1.6 skill units; option (B) touches the two columns
   (helmholtz 2.815 vs zero-floor 3.344; ifc_poisson 2.993, semantics degraded) closest to
   skill < 1, which is success criterion 2. Whatever you propose, carry the mandatory floor arms
   (§2.2), the helmholtz zero-floor column, the pfc band-limited denominator caveat, and — if you
   touch ifc_poisson — B1's `semantics_degraded`/`attribution.valid=false` flag.
