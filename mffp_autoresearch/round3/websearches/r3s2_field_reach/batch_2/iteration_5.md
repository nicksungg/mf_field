# Iteration 5 (CAP — 5/5 iterations used) — refutation pass 2 (§3.3) and the prior-art verdict

## Search rationale

Last turn. Two jobs: (a) refute **D3** — that "the residual `cahn_hilliard` gap is approximability-limited, not information-limited" is a claimable attribution; (b) make one final attempt to refute the **regime** that both D1 and D2 depend on (LF exists at train, is unavailable at test, only the condition vector is known at inference). If the regime is preempted, nothing in this stream is claimable and the brainstormer must propose a pure measurement.

## Search terms used

1. `attributing surrogate error to training set size versus approximability sampling density parametric PDE error decomposition study`
2. `neural PDE surrogate benchmark critique trivial linear baseline on parameters beats operator learning weak baselines` — **engine returned `Web search error: unavailable`**; re-issued reworded as `weak baselines critique operator learning benchmarks simple linear regression baseline outperforms neural operator` — **also `Web search error: unavailable`**. Term recorded as **FAILED (engine unavailable, 2 attempts)**; the D3 refutation therefore rests on term 1 plus the fetched Duraisamy article from iteration 2, which already carries the weak-baseline critique verbatim.
3. `low-fidelity data used only during training not available at inference parameter-only neural operator high-fidelity field prediction` — **engine returned `Web search error: unavailable`**; re-issued reworded as `multi-fidelity surrogate where low-fidelity model cannot be evaluated at test time only parameters known inference` (one term slot, two issuances).

## Findings

### Term 1 — D3 refutation: the error decomposition is textbook, the *field-target attribution instrument* is not (FETCHED)

- [Discrete Neural Operator with Adaptive Sampling for Parametric Transient Darcy Flows] — <https://arxiv.org/pdf/2512.03113> — **FETCHED this loop (pypdf)**. Verbatim: *"the total error of NN-based surrogates comprises of two parts, i.e., the **approximation error arising from model capacity limitations, and statistical error originating from limited training data**"*, formalised as `E[J] <= statistic error + approximation error` with *"the approximation error is due to neural network capability, and the statistic error results from finite training samples"*, and the explicit consequence that *"random samples introduce statistical errors, which may become the dominant errors for the approximation of low-regularity and high-dimensional problems"*.
- Snippet-only neighbours: <https://arxiv.org/pdf/2505.18923> (graph operator learning from limited data), <https://arxiv.org/abs/2606.09949> (generative active sampling for online PDE surrogate training), <https://link.springer.com/article/10.1007/s10915-024-02711-1> (deep adaptive sampling), <https://arxiv.org/pdf/2605.15356>.
- **Rejected as a source**: <https://arxiv.org/pdf/2511.04576> ("Physics-Informed Neural Networks and Neural Operators for Parametric PDEs") — **FETCHED and discarded**: its own front matter states *"The core content generation was performed by Claude Sonnet 4.5 ... we present this as an evolving AI-generated survey"*. Not citable as evidence.

So the *decomposition* (approximation/capacity vs statistical/sample-count) is standard, and Duraisamy supplies its diagnostic form in the evaluation register (*"The key diagnostic is whether classical reduced-order methods with comparable offline cost achieve similar accuracy; if so, the benchmark tests interpolation"*, <https://arxiv.org/html/2604.20061>, fetched iteration 2). What remains unretrieved across iterations 3 and 5 is a **model-free, condition-space nearest-neighbour sampling-density probe on a field target** used to decide the attribution before spending compute — B1 already ran one (ac 0.791 / ch 0.980 / fk 0.798).

### Terms 2–3 — the regime, one last time

Term 2 failed twice on engine error (recorded). Term 3's re-issue returned MF-ROM literature only, and the returned corpus contradicts the regime rather than matching it: the multi-fidelity reduced-order line *"infers HF solutions from **LF evaluations** over a wider range of parameter configurations"* and *"the essence of MF regression is inferring HF POD coefficients from their **LF counterpart**"* — i.e. the LF model is called online. Sources **snippet-only**: <https://royalsocietypublishing.org/doi/10.1098/rspa.2023.0655> (**a direct fetch returned HTTP 403**), <https://arxiv.org/pdf/2208.03115>, <https://arxiv.org/pdf/2109.11374>, <https://www.sciencedirect.com/science/article/abs/pii/S0045782522007678>. The engine's own gloss claiming these "work even when low-fidelity models cannot be directly evaluated at test time" is **engine-generated interpolation, not source text, and is not used as evidence**.

This is the fourth independent failure (batch-1 turns 1, 2, 5; batch-2 turn 5) to retrieve a multi-fidelity or parameter-conditioned surrogate that consumes **no field and no LF evaluation at inference**. The regime stands unrepresented.

## PRIOR-ART VERDICT (§3.3) — the three candidate directions r3s2-B2 may propose

### E1 — Regularised / band-limited / shrunk estimation of the LSI transfer function `T(k)` as a stability repair for the stage-2 corrector at `n_fit ~ 3`

**Verdict: `preempted (cite)` — usable ONLY as an instrument repair, never as a contribution.**

Fetched citations: <https://arxiv.org/pdf/1511.07030> (spectral-matrix shrinkage precisely when *"the number of complex degrees of freedom only slightly exceeds the dimension"*); <https://arxiv.org/abs/1810.08360> (LOOCV rules for choosing the shrinkage coefficient under low sample support, *"near-oracle performance"*); <https://arxiv.org/pdf/2606.03936> (FreqNO-DPS: *"a closed-form, spectrally shaped guidance score that weights the surrogate contribution according to its frequency-dependent accuracy"*, applied to a **frozen** neural operator). In-repo prior websearch: `docs/reports/MF_Sharp_HighFreq_Report.md` line 260 (fitted LF↔HF transfer kernel + FNO-as-prox, arXiv:2211.01567) and lines 224–230 / 293–297 (coherence < 0.7 band cutoff).
**What remains open**: only the *measurement* — that a specific published MF stack's panel-level variance was 100 % attributable to an unregularised band above the LF Nyquist, and that a one-line ridge/band-limit removes it with the pre-registered numeric prediction (2.041 -> ~0.171; range [10.32, 17.83] -> ~[10.3, 10.9]). Ship it as a **defect repair + acceptance check** (`tools/lsi_transfer_stability_audit.py`), with the citations above in `prior_art`. Any card wording that presents ridge/band-limiting as the idea will be a rebadge.

### E2 — Route contrast: direct condition->HF head vs condition->pseudo-LF->corrector, matched total budget, **no LF at test**

**Verdict: `preempted-but-MF-composition-open (cite)`.**

Fetched citations for the preempted parts: <https://arxiv.org/abs/2411.07576> (coarse-FE-in continuous super-resolution corrector); <https://arxiv.org/abs/2512.02868> (architecture-matched single- vs multi-fidelity arms — *"The single-fidelity networks use identical architectures to their multi-fidelity counterparts but are trained exclusively on the high-fidelity data without access to low-fidelity information"*, and *"multi-fidelity approaches consistently outperform their single-fidelity counterparts, particularly in data-scarce scenarios"*); <https://arxiv.org/abs/2511.12764> (INC: *"directly applying learned corrections to solver outputs leads to significant autoregressive errors"*); <https://arxiv.org/abs/2510.23111> (emulator superiority — a learned LF stage is **not** bounded by the LF solver); plus batch-1's <https://arxiv.org/abs/2302.12682>, <https://arxiv.org/abs/2310.00057>, <https://arxiv.org/html/2606.17460v2>.
**What remains open, exactly**: no fetched source runs a **direct parameter->HF arm against a coarse-intermediate arm at matched total optimizer budget in a regime where the coarse field cannot be produced at inference**. Every MF comparison retrieved either calls the LF model online (2512.02868 "exact LF"; the MF-ROM line, rspa.2023.0655 and kin) or feeds a real coarse solve to the corrector (2411.07576, INC). The composition — *is the LF intermediate worth its place in the graph when it must itself be hallucinated from the condition?* — is unmeasured. That, and only that, is E2's claim.
**Two-sided prior**: 2512.02868 predicts the stack wins; 2606.17460 and in-repo `MF_Sharp_HighFreq_Report.md` line 101 predict it loses; B1's F2 already measured "no resolvable value". Pre-register both directions.

### E3 — Attributing the residual `cahn_hilliard` gap to approximability (sampling density / slow n-width) rather than missing information

**Verdict: `preempted-but-MF-composition-open (cite)`.**

Fetched citations: <https://arxiv.org/html/2604.20061> (Duraisamy — *"When the parameter-to-solution map is smooth and the solution set has low intrinsic dimension: rapidly decaying Kolmogorov n-width, any competent approximation method will succeed"*; *"The key diagnostic is whether classical reduced-order methods with comparable offline cost achieve similar accuracy; if so, the benchmark tests interpolation, not the capacity to handle multiscale physics"*; *"no architecture or training procedure can recover information the coarse representation discards"*; reporting standard = *"(1) problem characterization (intrinsic dimension / n-width proxy ...); (3) scale-aware metrics (band-limited errors, H1/H2 norms ...)"*); <https://arxiv.org/pdf/2512.03113> (approximation vs statistical error decomposition); batch-1's <https://arxiv.org/abs/2605.28076> (deterministic underfitting vs irreducible conditional variability).
**What remains open**: the *paired* application — a completeness-certified condition vector (so the information channel is provably present: B1's IC-null contrast) **plus** a model-free condition-space nearest-neighbour sampling-density probe on the field target, used **prospectively** to declare a dataset cell approximability-limited and therefore off-limits for capacity spending. The vocabulary, the decomposition and the reporting standard are all published; the instrument-on-a-field-target and the prospective use are not. Note this verdict also **preempts** any claim that the `affine_on_hf_train` / `task_linearity_audit` accounting on the ifc cells is methodologically new — Duraisamy states the identical diagnostic in one sentence.

## Interpretation

No direction is `novel`; the project's 0-for-4 record is now 0-for-7. B2's defensible shape is a **measurement card**: repair the corrector with cited textbook regularisation, add the direct route as the arm that has never been run in this regime, and report both in fractional-error and skill units with a prospective approximability declaration for `cahn_hilliard`.

**Cap note**: this is iteration 5 of 5; the loop stops here. Two term slots this turn (2 and 3) and one in iteration 4 hit `Web search error: unavailable` and were re-issued once each; term 2 failed on both attempts and is recorded as a failed term, not a dead end.
