# iteration_2 — heavy-tailed / ESS framing and the MF-residual scaling literature

## Search rationale
Iteration 1 showed instance normalization is preempted-as-technique in time series but not
retrieved for MF residual targets. Two follow-ups: (a) go directly at the MF paper whose
whole framing is residual magnitude (arXiv:2310.03572) — does it scale per-sample?
(b) find the statistical framing of B2's actual diagnostic (one of 400 samples owning
89.2 % of MSE energy = ESS 1.2) — heavy-tailed loss / effective sample size / loss
reweighting; (c) check whether the *standard* operator-learning loss (relative L2, which
is per-sample normalized by definition) already implements the lever, because if it does
the "per-sample normalization" proposal is a bug-fix-to-standard-practice, not a method.

## Search terms used
1. `heavy-tailed loss dominated by few samples effective sample size MSE reweighting scientific machine learning`
2. `Fourier neural operator relative L2 loss normalized per sample training objective instead of MSE`
3. (fetch-only follow-ups, no new term: ar5iv 2310.03572, arXiv 2512.01421, emergentmind FNO topic)

## Findings

### Fetch — Residual Multi-Fidelity Neural Network Computing (arXiv:2310.03572)
**FETCHED** via https://ar5iv.labs.arxiv.org/html/2310.03572 (the direct PDF fetch at
https://arxiv.org/pdf/2310.03572 returned binary — dead). The paper is entirely about the
residual's *magnitude*: "the residual is expected to have a small magnitude (or norm)
relative to that of the high-fidelity quantity Q_HF", with the bound
|F| = |Q_HF - Q_LF| <= c(h_HF^q + h_LF^q) <= (1+s^q) eps_TOL, i.e. "the size of the
residual |F| is proportional to the small quantity eps_TOL". Crucially the scaling is
**characterized globally across the parameter domain** and the paper **introduces no
explicit scaling factor during training** — it relies on the theoretical property that
small-magnitude targets need lower network complexity. So the closest MF-residual-scale
paper retrieved assumes a *uniform* residual scale and does not treat per-sample scale
spread at all. That is exactly the assumption our data violates (spread 8.24e4 on pfc).

### Term 1 — heavy-tailed loss / effective sample size
- Class-Balanced Loss Based on Effective Number of Samples, Cui et al.,
  https://arxiv.org/pdf/1901.05555 (search-listed): "quantifies the effective number of
  samples by taking data overlap into consideration ... reweight the loss by inverse
  effective number of samples" — but for class imbalance in classification.
- Robust X-Learner, https://arxiv.org/html/2601.15360v1 (search-listed): "outcomes ...
  follow a Pareto-like distribution where a minute fraction of observations account for
  the vast majority of cumulative value, and standard machine learning models trained via
  MSE minimization are hypersensitive to these values. The squared error penalty forces
  the model to prioritize fitting the outliers at the expense of the structural majority."
  This is a verbatim description of our helmholtz defect, in causal inference / LTV.
- Rethinking Loss Reweighting for Imbalance Learning, https://arxiv.org/html/2605.10047v1
  (search-listed); Dynamic Loss-Based Sample Reweighting for LLM pretraining,
  https://arxiv.org/html/2502.06733v1 (search-listed). ESS = (sum w)^2 / sum w^2 appears
  as a standard weight-degeneracy diagnostic (importance-sampling framing, quoted in the
  Stable Asynchrony RL paper https://arxiv.org/pdf/2602.17616, search-listed).
No usable result ties heavy-tailed target energy / ESS to **PDE surrogate or MF residual
training**; the framing exists but in classification, causal inference and RL.

### Term 2 — FNO relative-L2 loss as per-sample normalization
Results: Continuum Attention for Neural Operators (https://arxiv.org/pdf/2406.06486),
FNO plasma surrogate (https://iopscience.iop.org/article/10.1088/1741-4326/ad313a),
3D seismic FNO (https://arxiv.org/pdf/2304.10242), Amortized FNO
(https://proceedings.neurips.cc/paper_files/paper/2024/file/d06a797c436cd5136a6f45b063316278-Paper-Conference.pdf),
"Fourier Neural Operators Explained: A Practical Perspective"
(https://arxiv.org/pdf/2512.01421). Search-summary evidence: "Relative L2 loss is used as
a training objective for Fourier neural operators ... normalizing errors relative to the
size of the target vector"; "In training neural operators, losses are typically
relative". Two fetch attempts to nail an exact quote failed:
- https://arxiv.org/pdf/2512.01421 -> binary PDF, unreadable (DEAD).
- https://arxiv.org/abs/2512.01421 -> **FETCHED**, abstract only; Duruisseaux, Kossaifi,
  Anandkumar, a 96-page practical FNO guide "closely integrated with the NeuralOperator
  2.0.0 library" that "address[es] common misunderstandings encountered in the
  literature", but the fetched excerpt contains no loss/normalization section.
- https://www.emergentmind.com/topics/fourier-neural-operators-fnos -> **FETCHED**; it
  discusses frequency-aware losses but explicitly contains nothing on relative-L2 as a
  standard or on input/target normalization (DEAD for this question).

## Interpretation
The MF-residual literature's own assumption (arXiv:2310.03572) is a *uniform small*
residual scale, with no training-time scaling factor — so per-sample target normalization
is not a published MF lever, it is a repair of an assumption the literature makes
implicitly. Meanwhile per-sample-normalized (relative) losses are described as the norm
in operator learning, which makes our family's global-max MSE the deviation. The
heavy-tailed/ESS diagnosis is well published but in other fields. Next: settle whether
relative/per-sample loss in neural operators has an explicit citable source, and open the
trust-gate direction.
