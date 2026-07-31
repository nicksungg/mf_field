# Summary so far — stream `r2s2_stacked`, entering batch 2

## Where the stream stands after B1

`experiment_cards/r2s2_stacked/batch_1/B1.json` (status `complete`) ran the spec's
pre-directed stack: FiLM-FNO condition→pseudo-LF emulator on the LF native grid, corrected
upsampler, vendored round-1 `dc_cleaned` stage (closed-form Wiener LSI `T(k)` + alpha line-search,
zero-init-gated `LocalCorrector`), five arms (`emul_only` / `frozen` / `finetuned` /
`end_to_end` / `condmean_lf`).

Headline numbers (part 5, seed 0, `provisional-single-seed`): panel geomean skill **14.076**
vs the launch anchor **23.0636** (`state/anchors/r2s2_stacked.json`, best-floor panel geomean;
`provisional:false`). Per dataset skill: helmholtz 2.815 / pfc 47.455 / allen_cahn 147.763 /
fisher_kpp 11.671 / cahn_hilliard 11.279 / ifc_poisson 2.993 (the last flagged
`semantics_degraded: true` — unpaired ladder, `dc_fit_source='pseudo_lf'`,
`attribution.valid=false`).

Against the certified per-dataset noise floor (`state/noise_floor.json`, r2s4-B1,
family `r2s4_cert_min`, 3 seeds — the closest like-for-like condition→HF comparator at the
same tier), the stack is inside/near the floor on allen_cahn (delta +0.448 vs
min_claimable_effect 0.880 → **not resolvable**), and only marginally better on pfc
(delta -0.392, mce 0.213) and fisher_kpp (delta +0.113 worse, mce 0.0007). The two resolvable
wins are helmholtz (delta -4.129, mce 2.953) and ifc_poisson (delta -5.27, degraded semantics).

## What B1's mechanism analysis established (part 6)

- **~100% of the stack's error is stage-1 error.** Same frozen corrector on a held-out TRAIN
  slice: real LF → 1.7e-07 (pfc) … 5.9e-03 (cahn_hilliard); pseudo-LF → 0.2363–0.4638.
- **Corrector value is a step function of its input's realisation, not of its capacity.**
  Relative value-add along `F_t = (1-t)*LF_real + t*LF_pseudo`: pfc 0.99997 → 0.13 (t=0.1) →
  -0.00016 (t=1). `cos(correction, HF - input)` rotates +0.98 → ~0. Band-1 coherence
  `gamma_b1(pseudo, HF)` 0.128–0.516 vs 0.997–1.000 for real LF. Threshold bracketed at
  0.52 < gamma_b1 < 0.95.
- **I8 (round-level constraint)**: `X → g(X) → f(g(X), X)` is a deterministic function of X, so
  a deterministic pseudo-LF is a *re-parameterisation* of the condition→HF class, never a new
  information channel. The stack sits at or past every training-free condition-only reference
  on 5/6 panel datasets, with the corrector worth <= 0.08% of the margin.
- **Ceiling taxonomy**: (a) STRUCTURAL — pfc / allen_cahn / fisher_kpp: adjacent conditions
  0.13–0.34 sd apart carry *orthogonal* band>=1 content (ADR r2-0003); conditional mean is the
  right answer; emulator collapses to rank 1 (`LF_hat(X) = a(X)*v`, ridge R^2 0.99997 on the
  amplitude). (b) SAMPLING — cahn_hilliard: 19-dim condition IS IC-complete, emulator emits the
  right rank (22) and pattern diversity, but median NN-condition distance is 3.91 sd at N=320,
  so it memorises (in-sample 0.0317 → held-out 0.4649). (c) LEARNING gap — helmholtz (map
  continuous at nn-cosine +0.931 but FiLM code eff-rank collapsed to 1.00 in all 4 blocks;
  resonance-driven amplitude swings, PC1 ridge R^2 -234.7) and ifc_poisson (LF field exactly
  affine in the 5-dim condition: ridge held-out 0.0000, rank-8 PCA+ridge 6.2e-08, trained
  emulator 0.0821).
- Two tools promoted: `tools/reachable_set_rank_audit.py`,
  `tools/surrogate_coherence_eligibility.py`.

## The B2 decision the brainstormer faces (part 7 `next_direction`)

Card offers two mutually exclusive options, both needing a prior-art verdict:

- **(A) Realisation-aware stage 1 on cahn_hilliard only** — replace `E[LF|c]` with something
  that has band>=1 realisation: stochastic/generative head, posterior sample, ensemble whose
  spread the corrector consumes, learned/whitened condition metric (the 3.91-sd Euclidean
  neighbour distance is the binding defect). Falsification pre-registered in **coherence
  units** (gamma_b1 0.516 → >= 0.95) before any corrector is trained. Risk: worth ~1.6 skill
  units against a 14.08 geomean. The open question explicitly notes the mean-vs-sample trade
  under a relative-L2 metric: an *independent* sample has coherence 0 in expectation and scores
  worse than the mean.
- **(B) Pivot to the learning-failure columns** — amplitude-aware / factorised
  direction x amplitude head for helmholtz; linear-in-condition or closed-form warm-start head
  for ifc_poisson. Card notes this is a **condition→HF card**, not a stack.
- Explicitly discouraged: re-running frozen-vs-finetuned as specified (A2-A3 confounded by
  A3's 50% larger optimizer budget; worth <= 0.08% on the five paired columns).

A third, methodological candidate is implicit in the card: **the coherence eligibility
precondition itself** (`gamma_b1` + in-sample oracle Wiener ceiling as a training-free go/no-go
for building any downstream corrector) — cross_stream_notes item 3 proposes it as a round-level
rule extending round 1's BC-match rule.

## Batch-1 prior-art position (do not re-derive)

`websearches/r2s2_stacked/batch_1/report.md`: D1 (pseudo-LF → frozen corrector) =
`preempted` (Xu et al. 2023 arXiv:2310.00057 frozen LF DeepONet subnet feeding a residual
subnet; Yang et al. 2025 arXiv:2503.17941 names the sequential-residual class; Meng &
Karniadakis arXiv:1903.00104). D2 (frozen/finetuned/e2e attribution) =
`preempted-but-MF-composition-open`. D3 (LF as supervised bottleneck) = `preempted`.

In-repo literature reports already cover the generative side and must be cited, not
re-derived: `docs/reports/MF_Sharp_HighFreq_Report.md` — K-sample posterior mean to protect
rel-L2 (lines 203, 317; PDE-Refiner arXiv:2308.05732), cosmology super-resolution's
"small scales are not deterministically recoverable, validate on summary statistics"
(arXiv:2010.06608, arXiv:2105.01016, arXiv:2310.06929), renormalization-group argument that
inverse coarse-graining is *necessarily* stochastic (arXiv:1704.06279), perception–distortion
tradeoff under SR3 (arXiv:2104.07636), and **cross-spectral coherence as the band-cutoff
estimator k_c ~ where coherence < 0.7** (lines 226, 295, 336) — this is the nearest published
neighbour of the card's gamma_b1 eligibility rule and must be checked hard.
`docs/reports/MF_Leaderboard_Beaters_2026_Report.md` — generative-then-distilled residual
transport (section 3.3), per-frequency-band trust weighting (section 3.2 / N7).

## Open questions for this batch's searches

1. Has anyone fed a **generative/stochastic** surrogate's *sample* (not mean) into a
   **deterministic corrector trained on real coarse solves**, and measured whether it helps?
2. Is there published work using **conditional-mean collapse / rank collapse of a conditioned
   surrogate** as a *diagnosis* that the conditioning variable is incomplete (as opposed to
   just reporting blur)?
3. Is **spectral coherence between a learned intermediate and the target** an established
   training-free eligibility criterion for building a downstream corrector?
4. For (B): is a **factorised amplitude x direction (normalised-field) head** established for
   resonance-dominated Helmholtz parametric surrogates? Is **POD/PCA + ridge in the parameter**
   (what ifc_poisson turns out to be) exactly the classical reduced-basis / POD-NN method — i.e.
   is the "closed-form head" direction wholly preempted?
5. Is the **negative-result framing** ("condition→pseudo-LF→corrector is dead as a class when
   the intermediate is a deterministic function of the condition") already published as a
   general statement about deterministic intermediate representations?
