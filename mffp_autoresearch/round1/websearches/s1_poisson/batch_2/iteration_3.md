# iteration_3 — s1_poisson batch 2

## Search rationale

Task item (c): extend s7_loss's *single-fidelity* gain/shape verdict (C-AMP,
Eigen 1406.2283) to the **multi-level** case. If a per-sample/per-level
amplitude factor between fidelities is the dominant error term, the classical
MF literature must already have a name for it — Kennedy–O'Hagan's ρ. Turn 3
therefore asks: (i) how does classical MF represent the amplitude ratio between
levels, (ii) has anyone ported that to a *fidelity-conditioned neural operator*
as an output-scale mechanism / normalization ablation, (iii) is the
multiplicative-vs-additive correction choice studied when levels differ by a
near-constant factor (ifc_poisson: 4.379/4.196/4.120).

## Search terms used

1. `Kennedy O'Hagan autoregressive multi-fidelity scaling factor rho amplitude ratio between fidelity levels neural network learned scale`
2. `fidelity-conditioned neural operator output scale conditioning amplitude differences across fidelity levels normalization ablation`
3. `multiplicative scaling versus additive residual multi-fidelity deep learning which correction form when fidelities differ by constant factor`

## Findings

### Term 1 — ρ as the amplitude ratio (classical MF)

- **SMT Multi-Fidelity Kriging docs**
  [https://smt.readthedocs.io/en/latest/_src_docs/applications/mfk.html]
  (fetched). The AR1 / Kennedy–O'Hagan model is written
  **y_high(x) = ρ(x)·y_low(x) + δ(x)**, with ρ(x) "a scaling/correlation factor
  (constant, linear or quadratic)" and δ the discrepancy; recursive extension to
  many levels follows Le Gratiet. Fetch verdict on the second question: "**The
  documentation contains no mention of normalizing each fidelity level's
  data.**"
- Also returned (not fetched): overview of GP MF techniques with variable
  fidelity relationships [https://arxiv.org/pdf/2006.16728] (**fetch failed —
  unparsable PDF binary, 2.6 MB**); MF-Box multi-scale emulation
  [https://arxiv.org/pdf/2306.03144]; MF surrogates for composites: co-kriging
  → MF neural networks [https://arxiv.org/pdf/2605.02871].

The take: classical MF **models the amplitude ratio explicitly as a free
parameter ρ** rather than normalizing it out of the data. B1's shared scaler
does neither — it leaves the 75.7× ratio in the targets and gives the network
no ρ to fit, only a fidelity embedding.

### Term 2 — fidelity-conditioned operators with output-scale conditioning

**No usable result.** The engine's own closing statement: "I couldn't locate a
single paper specifically addressing all your specified topics together
(fidelity-conditioned neural operators with output scale conditioning,
amplitude differences, and normalization ablations)." Adjacent-only returns:
conditional neural operator architectures
[https://www.emergentmind.com/topics/conditional-neural-operator-architecture],
FiLM-style LayerNorm conditioning
[https://www.emergentmind.com/topics/film-style-layer-norm-conditioning]
(ablations exist, but for conditioning sample-efficiency, not fidelity
amplitude), MF-HNP latent transformation of cross-fidelity correlations
[https://dl.acm.org/doi/10.1145/3534678.3539364], MFRNP
[https://arxiv.org/html/2402.18846v1]. The neural-operator normalization
constraint restated: normalization "must preserve discretization invariance ...
avoiding dependence on spatial variables" — consistent with QuadNorm
(iteration_1).

### Term 3 — multiplicative vs additive correction form

Engine synthesis over
[https://arxiv.org/pdf/2402.18846], [https://arxiv.org/pdf/2104.03743]
(Residual GP), [https://arxiv.org/pdf/2605.16118],
[https://link.springer.com/article/10.1007/s12206-016-0414-0] (**fetch failed —
303 to an auth IdP**), [https://www.researchgate.net/publication/303535115_...]:
MF relations are built by "additive scaling, multiplicative scaling, and hybrid
scaling"; multiplicative is "preferred when the error scales proportionally with
the measurement magnitude ... particularly relevant when fidelities differ by a
constant factor", additive "for fixed offsets". **Snippet-grade only** — the two
sources that would substantiate it both failed to fetch, so this is recorded as
a lead, not a citation.

## Interpretation

The multi-level extension of s7's gain/shape axis has a **classical owner**
(ρ in AR1 co-kriging: an explicit multiplicative amplitude factor per level
pair) and **no neural-operator owner** (term 2 returned an explicit negative).
So the per-level normalization B1 proposes is best understood as *implicitly
supplying the ρ that the pooled-scaler formulation deleted* — a framing that is
publishable-as-analysis but not as a new mechanism.
