# Iteration 5 — §3.3 refutation, part 2 + the prior-art verdict (CAP REACHED)

**WebSearch calls**: 3 | **WebFetch calls**: 1 (usable)
**Cap note**: this is iteration 5 of 5. No further iterations are permitted;
any unresolved thread is listed as an explicit residual risk below.

## Search rationale

Iteration 4 closed direction (i). This turn attacks the two remaining
candidate directions adversarially: (ii) the **zero-parameter LF-keyed
residual transfer** — is the exact composition `copy-LF + mean of the k
nearest training fidelity-residuals, keyed on the coarse field` published? and
(iii) the **hybrid** — is a trained MF corrector with a nonparametric
retrieval component published? The analog/constructed-analog downscaling
family is the most dangerous ancestor for (ii), so it gets a dedicated term.

## Search terms used

1. `training-free nearest neighbor analog correction from coarse simulation to fine simulation multi-fidelity baseline no training`
2. `combine neural operator prediction with retrieved nearest neighbor residual correction hybrid memory multi-fidelity PDE`
3. `constructed analog downscaling add residual of nearest analogs to coarse field bias correction method definition`

## Findings

### Term 1 — training-free / nonparametric MF correction

Results list: Hybrid Multi-Fidelity Models overview
(https://www.emergentmind.com/topics/hybrid-multi-fidelity-models), data-driven
correction of coarse-grid CFD
(https://www.sciencedirect.com/science/article/abs/pii/S0045793023001962),
local ML correction of CFD (https://arxiv.org/pdf/2305.00114), generative MF
downscaling via transport maps (https://arxiv.org/html/2509.22474v1), MF-Box
GP emulation (https://arxiv.org/pdf/2306.03144).

**FETCHED — Hybrid Multi-Fidelity Models overview**
[cite: https://www.emergentmind.com/topics/hybrid-multi-fidelity-models]:
- the canonical additive form is stated as "**fMF(x) = fLF(x) + Delta(x)**",
  where "the low-fidelity physics-based surrogate is corrected by a learned,
  data-driven model trained on residuals with respect to HF data";
- the correction Delta is "**often from a neural network, RBFN, or GP**", and
  the fetch reports the overview "does **not** discuss
  nonparametric/nearest-neighbor or retrieval-based approaches for the
  additive correction specifically";
- the one nearest-neighbour usage it cites is Bahmani et al. (2020), a
  "k-d tree nearest-neighbor search" used to **switch between constitutive
  models**, "a different paradigm than pure additive correction".

This is the cleanest statement of where the MF field actually is: additive
correction is universal, and the corrector is parametric.

### Term 2 — hybrid learned + retrieval in MF-PDE

Results list: Error-Conditioned Neural Solvers
(https://arxiv.org/pdf/2606.27354, https://neuralsolver.github.io/),
"The Best of Both Worlds: Hybridizing Neural Operators and Solvers"
(https://arxiv.org/abs/2512.19643), flow-matching residual-augmented operators
(https://arxiv.org/pdf/2512.12749), Park et al. residual refinement
(https://arxiv.org/pdf/2507.06133), equation-aware operators
(https://arxiv.org/html/2511.09729v1).

Every retrieved hybrid couples the operator to **the PDE residual or a
numerical solver** ("computing the PDE residual field of the current
prediction and passing it as an explicit input"; "a small number of local
correction iterations"). All are ADR-0009-excluded (they require the governing
equations at test time). **No usable result** for a retrieval/nonparametric
component inside an MF operator. Third independent framing (scouting sweep
iteration 1/4, batch-2 iteration 2 term 2, here) with the same answer.

### Term 3 — constructed analogs (the closest ancestor of the F6 rule)

Results list: LOCA
(https://journals.ametsoc.org/view/journals/hydr/15/6/jhm-d-14-0082_1.xml),
MACA (https://www.climatologylab.org/maca.html), cmip6-downscaling methods
(https://cmip6-downscaling.readthedocs.io/en/latest/downscaling-methods.html),
"Mind the Residual Gap: Probabilistic Downscaling under Real-World Bias"
(https://arxiv.org/pdf/2606.30821).

Search-result text (search-listed, **not fetched** — flagged as such):
constructed-analog downscaling first **coarsens fine-scale observations to the
coarse (GCM) grid**, identifies "the 30 coarsened observed days that best match
the specific GCM day being downscaled", and "calculates the **weighted average
of these analog days** that best reproduces the specific GCM day being
downscaled"; LOCA adds a "multiscale spatial matching scheme", matching over a
correlated region and then picking "the one candidate analog day that best
matches in the local area around the grid cell being downscaled"; MACA "adds an
additional bias correction after the downscaling".

So the *retrieval-keyed-on-the-coarse-field* half of our rule is 10+ years old
and operational in climate downscaling. What the analog family does with the
retrieved neighbours is **substitute their fine-scale fields** (directly or as
a weighted combination), plus separate bias correction — it does not add the
mean of their *fidelity residuals* onto the query's own coarse field. That
distinction is real but small, and it must not be oversold.

## THE PRIOR-ART VERDICT

### (i) LF field as an input channel to a residual FNO, MF few/moderate-shot

**Verdict: `preempted (cite)`.**
- LRC-FNO [https://arxiv.org/html/2606.17733, fetched iteration 1]: "The
  upsampled coarse solution and the source proxy are then concatenated as the
  input of the Residual-Closure FNO"; "The final full-resolution solution field
  is obtained by adding the coarse solution and the residual correction".
- MFFM [https://arxiv.org/html/2605.16118, fetched iteration 4]: residual
  `delta = u_HF - u_LF` "conditioned on u_LF", and **`FNO-residual` is one of
  its nine baselines** — our candidate is the current literature's *baseline*,
  not its frontier.
- Multifidelity DeepONet [https://arxiv.org/abs/2204.06684, fetched iteration
  4]: "two standard DeepONets coupled by **residual learning and input
  augmentation**".

**Nearest neighbours / what remains open**: nothing at the mechanism level.
Three narrow things survive, and only as *setting*, not as novelty:
(a) our LF is a **real coarse consistent solve** (immutable 1), whereas LRC-FNO's
coarse field is its own network's output and the SR/downscaling line coarsens
the HF field; (b) no retrieved MF/coarse-correction work runs on
sharp-interface 2-D phase-field data (iteration 4 term 2 found only
single-fidelity physics-loss phase-field DL); (c) the Class-A/Class-B
partition (the fidelity residual is *unlearnable* on 2 of 5 datasets) is a
finding about the data, not a method claim.
**Consequence for the brainstormer**: propose this as the **missing control /
literature-standard baseline** the zoo does not contain (batch-1 F14: 0 of 27
families read the test LF field at inference), never as a novel model.

### (ii) Zero-parameter LF-keyed residual transfer as a reportable baseline

**Verdict: `preempted-but-MF-composition-open`.**
- Analog method [https://gmd.copernicus.org/articles/12/2915/2019/, fetched
  iteration 2]: retrieval keyed on coarse fields, "search in the past for
  similar days to a target day in order to infer the predictand of interest";
  Teweles-Wobus S1 gradient criterion; retrieved dates give "the empirical
  conditional distribution".
- Constructed analogs / LOCA
  [https://journals.ametsoc.org/view/journals/hydr/15/6/jhm-d-14-0082_1.xml,
  **search-listed only, not fetched**]: coarsen the fine observations, match the
  coarse field, weighted average of the 30 best analog days.
- DeltaPhi [https://arxiv.org/pdf/2406.09795, fetched iteration 2]: retrieve
  the most similar training example by **input field similarity**, learn "the
  residual between the ground truth solution and the prediction from the
  auxiliary example", predict `retrieved output + learned residual`, in the
  data-limited regime.
- Hybrid-MF overview [https://www.emergentmind.com/topics/hybrid-multi-fidelity-models,
  fetched this iteration]: additive correction `fMF = fLF + Delta` with Delta
  "often from a neural network, RBFN, or GP" — **not** retrieval.

**What remains open (state it exactly)**: the composition
`prediction = interpolated LF(query) + mean_k [HF_j - LF_j]`, with `j` retrieved
by similarity **of the LF solution field**, used as a **training-free floor that
a trained multi-fidelity operator must clear** on a field benchmark. Each half
is published (analog retrieval on coarse fields; additive fidelity-residual
correction), and no fetched source combines them: analog methods substitute the
retrieved fine fields rather than transferring the fidelity residual, and the
MF additive-correction literature's corrector is parametric.
**Reportable, with the analog family cited as its ancestor — not a novelty
claim.**

### (iii) Hybrid: trained LF-input residual operator + retrieval residual term

**Verdict: `preempted-but-MF-composition-open`.**
- NNTNNR [https://arxiv.org/abs/2310.00664, fetched iteration 3]: a twin network
  "predict[s] differences between regression targets rather than the targets
  themselves", assembled over "the nearest neighbors of the unknown data point"
  as anchors; "outperform[s] both neural networks and k-nearest neighbor
  regression on **small to medium-sized data sets**" — the exact hybrid shape,
  in scalar regression.
- DeltaPhi [https://arxiv.org/pdf/2406.09795, fetched]: the operator-learning
  instance of the same idea.
- KRF image restoration
  [https://www.sciencedirect.com/science/article/abs/pii/S0952197626000977,
  search-listed] and RASR (scouting sweep) — image-domain instances.

**What remains open**: the *multi-fidelity* binding — an operator whose
correction is the sum of a learned term and a retrieved fidelity-residual term,
with a confidence/blend weight, over a real coarse solve, parameterized so the
copy-LF reference is exactly recoverable (the scouting sweep's C1
guaranteed-fallback question, still unrefuted). This is the only one of the
three directions where a *mechanism* claim is even arguable, and it is thin.

## Residual risks (cap reached, unresolved)

- LOCA/MACA were not fetched; the constructed-analog quotes are search-result
  text. If the brainstormer leans on the analog ancestry in the card, it should
  cite the fetched AtmoSwing paper, not LOCA.
- MF-DeepONet's "LF prediction appended to the trunk net inputs" is
  search-synthesis text, not a fetched quote; the fetched abstract only
  supports "residual learning and input augmentation".
- `arxiv.org/pdf/...` fetches failed 4 times this loop (undecoded binary);
  `/abs/` and `/html/` worked. Later websearchers should prefer those.
