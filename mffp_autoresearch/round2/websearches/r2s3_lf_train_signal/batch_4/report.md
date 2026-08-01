# Websearch Report — Stream `r2s3_lf_train_signal`, Batch 4

**Stream**: `r2s3_lf_train_signal` (lever — "how much does LF, available only
during training, help a condition→HF model?")
**Batch**: 4
**Total iterations**: 5 (cap 5 — **CAP HIT**, noted in `iteration_5.md`)
**WebSearch calls**: 15 (3 per turn × 5 turns; one turn-3 term was returned by
the engine as three successive result sets and still counts as one call)
**WebFetch calls**: 0 — **`WebFetch` is disabled in this environment** (it
returns a context-mode redirect instead of a page). All body reads were done
with `curl` from Bash and are labelled **[curl-fetched]** in the iteration
files; engine results are labelled **[search return]**. Same route-around as
the r2s2 batch-3 loop. **curl fetches: 12** (10 usable: arXiv `/abs/`,
`/html/`, ar5iv, and one Crossref API call; 2 unusable: ScienceDirect JS
shells, explicitly flagged and never quoted).
**Cap hit**: yes (5/5)

## Search trace

### Turn 1 — the amplitude channel and the ensemble alternative, in PDE-surrogate vocabulary
Terms: per-sample amplitude head in operator surrogates; output-norm/energy
calibration in PDE surrogates; deep ensembles vs auxiliary LF data at tiny N.
Chosen because B3's part 6 M1 makes the **per-sample gain channel** the
mechanism (96.9% of the no-LF arm's allen_cahn draw-range) and part 7 ranks
(a) gain-head and (b) budget-matched ensemble as the two live directions.
- **ELADO** [curl-fetched]: benchmark isolating "the effect of input signal
  complexity on prediction accuracy under **controlled amplitude
  normalization**", concluding that heavy-tailed targets etc. "cause
  substantial degradation … that standard datasets and metrics (e.g., the
  **mean relative L² error**) may obscure" [cite:
  https://arxiv.org/abs/2606.20771]. Diagnostic, not a learned gain head.
- **ADEPT** [curl-fetched]: deep ensembles as an *acquisition* device,
  "factor of 20 reduction in training dataset size", **no** ensemble-vs-LF
  budget contrast [cite: https://arxiv.org/abs/2310.09024].
- "amplitude surrogate" in the search index is a particle-physics false friend
  [https://arxiv.org/abs/2601.13308]. Engine: "direct empirical comparisons of
  these strategies are not present". → `iteration_1.md`

### Turn 2 — same two questions in conditioning/calibration vocabulary
Terms: hypernetwork/FiLM scale emission; post-hoc multiplicative scale
correction of a shrunk regressor; shape/magnitude factorisation.
- **FiLM is a scale-emitting hypernetwork** — "learned scaling (gamma) and
  shifting (beta) parameters"; "The FiLM generator is a specialized
  HyperNetwork" [https://distill.pub/2018/feature-wise-transformations/].
- **LCC / Tweedie de-shrinkage** [curl-fetched, abstract + body]: post-hoc
  corrections for "**shrinkage toward the mean**" that need no new labels;
  "LCC applies a simple linear transformation estimated on a **held-out
  calibration split**"; "much of the bias arises from a **first-order scaling
  distortion that can be identified on a small held-out calibration set**";
  applied to "a black-box model, requiring no specialized retraining"; claimed
  domain-general [cite: https://arxiv.org/abs/2508.01341].
- Per-sample multiplicative correction is 30-year-old chemometrics practice
  [search returns: US 5568400; ScienceDirect S016974390700216X].
  → `iteration_2.md`

### Turn 3 — claimability protocol (direction c) + head-on refutation of (a)
Terms: heteroscedastic paired comparison protocols; "calibration explains away
the auxiliary-data gain"; which variance axis dominates.
- **Bouthillier et al., "Accounting for Variance in ML Benchmarks"**
  [curl-fetched abstract + ar5iv body]: "**Bootstrapping data stands out as
  the most important source of variance. In contrast, model initialization
  generally is less than 50% of the variance of bootstrap**"; recommendations
  = randomize every source, use "a high-enough **probability that in one run
  an algorithm outperforms another**", prefer out-of-bootstrap to fixed test
  sets; "51 times reduction in compute cost" [cite:
  https://arxiv.org/abs/2103.03098].
- "Has anyone shown a plain output calibration reproduces an auxiliary-data
  gain?" → **No usable results** (three successive result sets, engine
  explicitly could not find it).
- Engine on heteroscedastic/worst-split/minimum-seed protocols: "The search
  results **don't contain specific information** about" them. → `iteration_3.md`

### Turn 4 — refutation pass from the multi-fidelity-methodology side
Terms: MF ablation controlled for output scaling; ensemble-of-single-fidelity
vs MF at equal budget; predict-the-norm-then-the-normalized-field.
- **DiSOL** [curl-fetched abstract + html/ar5iv body] — the decisive hit:
  "We define a **per-sample amplitude** u_lim … and the dimensionless solution
  pattern u_h := U_h/u_lim … All models … trained to predict the **normalized
  pattern** … reconstructed as Û_h = û_lim·û_h using an **optional amplitude
  regressor**" [cite: https://arxiv.org/abs/2601.09143].
- **Ensemble-based MF emulation** [curl-fetched]: ensemble members are
  themselves LF-consuming hierarchical-kriging emulators; body has **0** hits
  for "fixed computational budget"/"equal budget"/"fair" [cite:
  https://arxiv.org/abs/2604.18045].
- "Output scaling multi-fidelity (OS-MF)" exists but scales LF toward HF
  [search return: https://link.springer.com/article/10.1007/s00158-023-03537-5].
- **No retrieved MF ablation scale-corrects its single-fidelity baseline.**
  → `iteration_4.md`

### Turn 5 — control-baseline framing, LUPI vocabulary, verdict (cap hit)
Terms: control baselines that erase reported gains; attributing an
auxiliary-data benefit to a channel; training–inference data asymmetry.
- **Simple Control Baselines for Evaluating Transfer Learning**
  [curl-fetched]: prescribes "**blind-guess** … **scratch-model** …
  **maximal-supervision**" controls because there is "not yet an agreed-upon
  set of control baselines" [cite: https://arxiv.org/abs/2202.03365].
- **The regime is named after all**: LUPI / privileged-information
  distillation, with a 2026 surrogate-modeling instance — Mazloom,
  Shafieezadeh, Hur, Jung, Ha, Hahm, *Eng. Appl. Artif. Intell.*, **DOI
  10.1016/j.engappai.2025.113398** (metadata Crossref-verified in-loop; body
  unobtainable) [cite:
  https://www.sciencedirect.com/science/article/abs/pii/S0952197625034293].
  This **retires batch 3's third "independent miss"**.
- No work decomposes an auxiliary-data benefit into scale vs map channels.
  → `iteration_5.md`

## Prior-art verdict

| Candidate direction | Verdict | Citations (fetched/returned in this loop) | What remains open |
|---|---|---|---|
| **(a)** LF-free **gain/amplitude head** conditioned on the condition vector, fitted on the same 5 HF rows, used as a **substitution test** for LF's train-time value (training-free probe on shipped dumps first, then one confirmatory arm) | **preempted-but-MF-composition-open** | https://arxiv.org/abs/2601.09143 (**curl-fetched**; DiSOL Methods §4.1: per-sample amplitude u_lim, dimensionless pattern, "optional **amplitude regressor**" — the mechanism verbatim, in PDE operator learning); https://arxiv.org/abs/2508.01341 (**curl-fetched**; LCC = affine de-shrinkage on a small held-out calibration split, Tweedie local de-shrinkage, no new labels, domain-general); https://distill.pub/2018/feature-wise-transformations/ (search return; FiLM γ = learned scale, "specialized HyperNetwork"); https://arxiv.org/abs/2606.20771 (**curl-fetched**; controlled amplitude normalization + "mean relative L² … may obscure"); https://arxiv.org/abs/2202.03365 (**curl-fetched**; control-baseline discipline) | Only the **composition**: using the head as a **control that prices auxiliary low-fidelity training data**. No retrieved MF ablation output-scale-corrects its single-fidelity baseline (turn 4 t1), and the direct query "is the auxiliary-data gain just calibration?" returned **no usable results** (turn 3 t2). Plus the round's four standing openers: condition-vector-only test input with genuine coarse consistent solves at train; N_hf = 5; the **copy-LF denominator**; a panel varying condition completeness (ADR r2-0003). **The deliverable is the measured share of the ±LF effect the LF-free head absorbs — never the head itself.** |
| **(b)** Budget-matched pricing of the **no-LF ensemble** alternative (vs B3's M5, which used 15 HF rows and 3× compute) | **preempted-but-MF-composition-open** (weak — carries as a control arm, not a claim) | https://arxiv.org/abs/2604.18045 (**curl-fetched**; ensemble MF emulator "outperforms single-model alternatives", but members are LF-consuming hierarchical kriging; **0** body hits for budget/fairness language); https://arxiv.org/abs/2103.03098 (**curl-fetched**; randomize all variance sources, probability-of-improvement criterion, out-of-bootstrap, bagging-style variance reduction); https://arxiv.org/html/2512.02868v1, https://link.springer.com/article/10.1186/s40323-025-00316-3, https://arxiv.org/abs/2512.12276 (search returns; MF-vs-single-fidelity under budget/cost imbalance is standard framing) | Nothing retrieved prices a **no-auxiliary-data ensemble against an LF-trained arm at matched compute** for a condition→field surrogate. Real gap, but an *evaluation control*: admissible as an arm inside (a)'s card, never as the card's claim. |
| **(c)** Repaired **claimability protocol** for draw-heteroscedastic effects (worst-split gate, axis-appropriate variance constant, ≥5 draws) | **preempted** | https://arxiv.org/abs/2103.03098 (**curl-fetched** abstract + ar5iv body: "Bootstrapping data stands out as the most important source of variance … model initialization generally is less than 50% of the variance of bootstrap"; three recommendations incl. probability-of-improvement and out-of-bootstrap; credits Hothorn et al. 2005); search returns https://machinelearningmastery.com/statistical-significance-tests-for-comparing-machine-learning-algorithms/ (corrected resampled t / 5×2 CV / Friedman–Nemenyi), https://pmc.ncbi.nlm.nih.gov/articles/PMC10435952/, https://arxiv.org/pdf/2304.01910, https://arxiv.org/pdf/2606.20536 | Nothing at contribution level. **Adopt as methodology and cite**; the exact defect B3's T1-3 found (a seed-certified constant used to gate a data-subset-varying effect) is the published diagnosis, not a discovery. |
| **(S)** Stream-level framing: "rich auxiliary/LF data at training, deployment-feasible inputs only at inference" | **preempted (cite)** — genre named; MF composition open per batch 3's P1 | Mazloom, Shafieezadeh, Hur, Jung, Ha, Hahm, *Eng. Appl. Artif. Intell.* 2026, DOI **10.1016/j.engappai.2025.113398** — https://www.sciencedirect.com/science/article/abs/pii/S0952197625034293 (search return; **metadata Crossref-verified in-loop, body unobtainable — content characterization is flagged engine synthesis**); LUPI: Vapnik & Izmailov, https://www.researchgate.net/publication/301362871_Learning_using_privileged_information_Similarity_control_and_knowledge_transfer (search return); https://arxiv.org/abs/2602.04942, https://arxiv.org/pdf/2410.13872, https://arxiv.org/pdf/2603.29167 (search returns) | Batch 3's P1 open items stand (copy-LF denominator; N_hf = 5; genuine coarse consistent solves rather than downsampled HF; condition-completeness-varying panel). **Stop describing the regime as unnamed** — batch 3's third "independent miss" is retired by this loop. |

## Citations summary

- [Zhang et al. 2026 — DiSOL] "Discrete Solution Operator Learning for Geometry-Dependent PDEs" — https://arxiv.org/abs/2601.09143 (body https://arxiv.org/html/2601.09143v1, https://ar5iv.labs.arxiv.org/html/2601.09143) — **curl-fetched** — used in: `iteration_4.md` term 3; verdict (a).
- [2025] "Debiasing Machine Learning Predictions for Causal Inference Without Additional Ground Truth Data: 'One Map, Many Trials' in Satellite-Driven Poverty Analysis" — https://arxiv.org/abs/2508.01341 (body https://arxiv.org/html/2508.01341) — **curl-fetched** — used in: `iteration_2.md` term 2; verdict (a).
- [Bouthillier, Delaunay, Bronzi, Trofimov, Nichyporuk, Szeto, Sepah, Raff, Madan, Voleti, Ebrahimi Kahou, Michalski, Serdyuk, Arbel, Pal, Varoquaux et al.] "Accounting for Variance in Machine Learning Benchmarks" — https://arxiv.org/abs/2103.03098 (body https://ar5iv.labs.arxiv.org/html/2103.03098) — **curl-fetched** — used in: `iteration_3.md` term 3; verdicts (b), (c).
- [—] "ELADO: Elliptic PDE Assessment Datasets for Operator Learning" — https://arxiv.org/abs/2606.20771 — **curl-fetched** — used in: `iteration_1.md` term 2; verdict (a).
- [—] "Simple Control Baselines for Evaluating Transfer Learning" — https://arxiv.org/abs/2202.03365 — **curl-fetched** — used in: `iteration_5.md` term 1; verdict (a).
- [—] "An ensemble-based approach for multi-fidelity emulation and adaptive sampling" — https://arxiv.org/abs/2604.18045 (body https://arxiv.org/html/2604.18045) — **curl-fetched** — used in: `iteration_4.md` term 2; verdict (b).
- [—] "ADEPT: Active Deep Ensembles for Plasma Turbulence" — https://arxiv.org/abs/2310.09024 — **curl-fetched** — used in: `iteration_1.md` term 3.
- [Mazloom, Shafieezadeh, Hur, Jung, Ha, Hahm 2026] "Learning from more to predict with less: Representation-level multimodal distillation to address training–inference data asymmetry in surrogate modeling", *Eng. Appl. Artif. Intell.*, DOI 10.1016/j.engappai.2025.113398 — https://www.sciencedirect.com/science/article/abs/pii/S0952197625034293 — **search return; metadata curl-verified via Crossref API; body NOT obtainable (JS shell) — content characterization is engine synthesis, flagged** — used in: `iteration_5.md` terms 2–3; verdict (S).
- [Distill 2018] "Feature-wise transformations" — https://distill.pub/2018/feature-wise-transformations/ — search return — used in: `iteration_2.md` term 1; verdict (a).
- [Vapnik & Izmailov] "Learning using privileged information: similarity control and knowledge transfer" — https://www.researchgate.net/publication/301362871_Learning_using_privileged_information_Similarity_control_and_knowledge_transfer — search return — used in: `iteration_5.md` term 2; verdict (S).
- [—] "A general multi-fidelity metamodeling framework for models with various output correlation" (OS-MF) — https://link.springer.com/article/10.1007/s00158-023-03537-5 — search return — used in: `iteration_4.md` term 1.
- [—] "Assessing the performance of correlation-based multi-fidelity neural emulators" — https://arxiv.org/html/2512.02868v1 — search return — used in: `iteration_4.md` term 1; verdict (b).
- [—] "Comparison of multi-fidelity surrogate models … under extreme cost imbalance" — https://link.springer.com/article/10.1186/s40323-025-00316-3 — search return — used in: `iteration_4.md` term 2; verdict (b).
- [—] "Balancing Accuracy and Speed: A Multi-Fidelity Ensemble Kalman Filter with a ML Surrogate Model" — https://arxiv.org/abs/2512.12276 — search return (engine's "fixed computational budget to be fair" sentence is **unconfirmed by fetch** and is not used as a citation of record) — `iteration_4.md` term 2.
- [—] "The FID Lottery: Quantifying Hidden Randomness in Generative-Model Evaluation" — https://arxiv.org/pdf/2606.20536 — search return — `iteration_3.md` term 3.
- [—] "On the Variance of Neural Network Training" — https://arxiv.org/pdf/2304.01910; "Variational Resampling Based Assessment of Deep Neural Networks" — https://arxiv.org/pdf/1906.02972 — search returns — `iteration_3.md` term 3.
- [—] Statistical-comparison practice (corrected resampled t / 5×2 CV / Friedman–Nemenyi) — https://machinelearningmastery.com/statistical-significance-tests-for-comparing-machine-learning-algorithms/; paired evaluation under confounders/outliers — https://pmc.ncbi.nlm.nih.gov/articles/PMC10435952/ — search returns — `iteration_3.md` term 1; verdict (c).
- [—] Privileged-information distillation cluster: https://arxiv.org/abs/2602.04942, https://arxiv.org/pdf/2410.13872, https://arxiv.org/pdf/2603.29167, https://arxiv.org/pdf/2605.20643 — search returns — `iteration_5.md` term 3; verdict (S).
- [—] "Stronger Baseline Models — A Key Requirement for Aligning ML Research with Clinical Utility" — https://arxiv.org/html/2409.12116v1; "Source-Optimal Training is Transfer-Suboptimal" — https://arxiv.org/html/2511.08401v1 — search returns — `iteration_5.md` term 1.
- [—] SIB-CL — https://www.nature.com/articles/s41467-022-31915-y — search return — `iteration_5.md` term 2.
- [—] "CHRep: … Post-hoc Calibration for Spatial Gene Expression Prediction" — https://arxiv.org/pdf/2604.21573 — search return — `iteration_2.md` term 2.
- **Carried from prior loops (cited, not re-derived)**: batch 3's fetched https://arxiv.org/html/2511.01830v1, https://arxiv.org/html/2408.17075v1, https://arxiv.org/html/2510.23111v1, https://iopscience.iop.org/article/10.1088/1741-4326/adfdfb, https://arxiv.org/abs/2505.14704; batch 2's https://arxiv.org/html/2510.15337, https://arxiv.org/abs/2511.20183; in-repo `docs/reports/MF_Leaderboard_Beaters_2026_Report.md` (line 46: `mf_fno_transfer_film` = LF-pretrain→HF-finetune, the stream's mandatory declared baseline) and `docs/reports/MF_Sharp_HighFreq_Report.md` (displacement+amplitude decomposition converged on by meteorology/seismics/statistics — Hoffman 1995, Keil & Craig 2009, Francom arXiv:2305.08834; PDE-Refiner per-mode MSE ∝ amplitude², arXiv:2308.05732).

## Dead ends

- `simple output calibration matches gains attributed to auxiliary data …` → three successive result sets of generic calibration literature; engine explicitly could not find the study. **This is the loop's most valuable miss** — it is what keeps direction (a)'s composition open.
- `paired comparison … heteroscedastic … worst-case split minimum number of seeds` → engine: "don't contain specific information about heteroscedastic significance protocols, worst-case split analysis, or minimum number of seeds recommendations". The *general* variance literature (2103.03098) covers the ground anyway, which is why (c) is preempted rather than novel.
- `per-sample amplitude scaling head …` in the operator-surrogate vocabulary → returned particle-physics "amplitude surrogates" (https://arxiv.org/abs/2601.13308). The right vocabulary turned out to be "**normalized pattern + amplitude regressor**" (turn 4), not "amplitude head".
- ScienceDirect bodies (`S2590197426000406`, `S0952197625034293`) → JS shells under curl; only Crossref metadata is verifiable for the latter. No quote was taken from either body.

## For the brainstormer

The brainstormer MUST quote the prior-art verdict above for whatever it proposes.

1. **Direction (a) is the only cardable one, and its mechanism is preempted.**
   Quote **(a) `preempted-but-MF-composition-open`** and name the preemptor
   verbatim: DiSOL already defines "a per-sample amplitude u_lim … the
   dimensionless solution pattern … reconstructed … using an **optional
   amplitude regressor**" (https://arxiv.org/abs/2601.09143), and post-hoc
   affine de-shrinkage on a small held-out split is published and claimed
   domain-general (https://arxiv.org/abs/2508.01341). A card that proposes
   *a gain head* is a rebadge; a card that proposes *the measurement — what
   share of the certified ±LF effect an LF-free gain head absorbs on the same
   5 HF rows* — is the open composition. Frame it as a **control baseline**
   in the sense of https://arxiv.org/abs/2202.03365 (blind-guess /
   scratch-model / maximal-supervision), sitting alongside the round's
   mandatory floor arms (§2.2).
2. **Do the training-free probe first.** B3 part 7 says
   `tools/residual_gain_learnability.py` answers this on the shipped
   prediction dumps with no GPU; `tools/gain_calibration_ceiling.py` already
   holds the oracle ceiling (96.9% of A0's allen_cahn draw-range). Card the
   confirmatory training arm only if the probe says the achievable head
   recovers a material share. This also satisfies decision-discipline: the
   result is informative in **both** directions — if the head recovers the
   channel, the round's affirmative LF evidence reduces to output
   calibration; if it does not, "LF supplies a calibration signal 5 HF rows
   provably cannot" becomes the stronger statement.
3. **Direction (b) may ride along as an arm, never as the claim**
   (`preempted-but-MF-composition-open`, weak). If you price the no-LF
   ensemble, price it at matched compute AND matched HF rows, and judge it
   with Bouthillier's criterion — "a high-enough probability that in one run
   an algorithm outperforms another" (https://arxiv.org/abs/2103.03098).
   Ensembling LF-consuming members is already published
   (https://arxiv.org/abs/2604.18045).
4. **Do NOT card direction (c)** — `preempted`. "Data-sampling variance
   dominates initialization variance" is Bouthillier et al.'s Figure-1 result
   verbatim ("model initialization generally is less than 50% of the variance
   of bootstrap"), and their remedies (randomize every source; out-of-bootstrap
   over fixed splits; probability-of-improvement) are stronger than a
   worst-split gate. **Use it as the card's statistics section and cite it**;
   B3's cross-stream note (2) about the axis-mismatched
   `min_claimable_effect` (0.8797 seed-certified vs a 726.06-unit draw range
   on allen_cahn) is now a *published* diagnosis, so state it as compliance,
   not as a finding.
5. **Stop calling the regime unnamed.** Verdict **(S) `preempted (cite)`**:
   it is **LUPI / privileged-information distillation**, with a 2026
   surrogate-modeling instance (Mazloom et al., DOI
   10.1016/j.engappai.2025.113398 — metadata verified, body unobtainable, so
   cite the title/venue/DOI and do **not** quote its numbers). Batch 3's
   third "independent miss" is retired; batch 3's P1 open items (copy-LF
   denominator, N_hf = 5, genuine coarse consistent solves, condition-
   completeness-varying panel) are what still separate this stream from that
   literature.
6. **Honour B3's explicit do-not**: no further LF-supply engineering on
   `sharp__fisher_kpp_2d` or `sharp__phase_field_crystal_2d` — M5 already has
   a cheaper LF-free alternative that beats the LF arm on both. And carry the
   standing caveats on any new panel row: helmholtz is report-only (ADR
   r2-0004: its HF test fields reproduce from the condition vector to 2.2e-13
   via two FFTs); pfc claims carry the band-limited-denominator caveat;
   ac/fk/pfc have incomplete condition vectors (ADR r2-0003), so the
   conditional-mean bound + the M2 shrinkage reward apply — an intervention
   that *fixes* amplitude should be expected to score worse there, which is
   precisely the sign to pre-register for a gain-head arm on pfc.
7. **Per-dataset clauses against `state/noise_floor.json`** (ifc 0.9377041,
   ch 0.0912454, fk 0.0007137, ac 0.8797047, pfc 0.2130273, hz 2.9529916;
   panel geomean 1.1418668), written as "must beat X on EACH of …", and
   quoted alongside the launch anchor 23.0636 with the per-dataset floor table
   (§12 common convention).
