# Iteration 3 — ULP-band tolerance setting (C3) and the fit-set-size fairness seam (C4)

## Search rationale

Two routed contract items remain unpriced against prior art.
**C3**: batch 1 measured a per-dataset ULP round-off band and recommends `F1 tolerance := max(1e-9, band)`, and found that `sharp__sod_1d`'s "band" (3.08e-1) is not a seam at all but an **exact-equality-gated branch** (`sd = where(sd > 0, sd, 1.0)`) that a 1-ULP perturbation flips, amplifying 8.4e6× and re-selecting 53% of nearest neighbours.
The literature question is therefore two-part: is ULP-based tolerance setting for reproduction checks standard (expected: yes, textbook), and is the *branch-flip* failure mode a named, studied class (which would tell us how to phrase the sod_1d finding).
**C4**: r3s1's mechanism turn found paired reference arms fit on 400 rows against a scored arm's 320 — a fit-set-size asymmetry inside a matched comparison.

## Search terms used

1. `setting numerical tolerance regression test floating point ULP round-off scientific software reproducibility bitwise comparison threshold`
2. `float32 float64 precision nondeterminism affects benchmark results scientific machine learning reproducibility tolerance`
3. `baseline fitted on more training samples than the evaluated method unfair comparison matched sample size protocol benchmark`

## Findings

### Term 1 — ULP tolerance setting and unstable tests

Results: MathWorks HDL Coder ULP/tolerance docs (https://www.mathworks.com/help/hdlcoder/ug/ulp-considerations-of-native-floating-point-operators.html , https://www.mathworks.com/help/hdlcoder/ref/floatingpointtolerancecheckbasedon.html , https://www.mathworks.com/help/hdlcoder/ref/tolerancevalue.html) ; **"Eliminating Unstable Tests in Floating-Point Programs"** https://arxiv.org/pdf/1808.04289 ; emmtrix ULP-difference wiki ; a C++ comparison-strategy write-up (sqlpey.com).

Snippet-level from the MathWorks docs: a verification harness lets you specify the tolerance check **"based on relative error or ULP error"**, with defaults `1e-7` (relative) and `0` (ULP); each FP op contributes up to 0.5 ULP; "comparisons near zero often require a separate absolute tolerance check, as relative comparisons break down".
That is exactly our `max(1e-9, band)` construction (an absolute floor under a relative/ULP band) — shipped engineering practice, not a research contribution.

**FETCHED — "Eliminating Unstable Tests in Floating-Point Programs"** (Titolo, Muñoz, Feliú, Moscato; NIA / NASA Langley; arXiv:1808.04289v2), https://arxiv.org/pdf/1808.04289 (40,578 chars).
Abstract, verbatim: *"Round-off errors arising from the difference between real numbers and their floating-point representation cause the control flow of conditional floating-point statements to deviate from the ideal flow of the real-number computation. This problem, which is called **test instability**, may result in a significant difference between the computation of a floating-point program and the expected output in real arithmetic."*
They give a formally proven program transformation that returns either the original result *when both the real and floating-point flows provably agree* or **a warning when the flows may diverge**, and state that "unstable tests are an inherent feature of floating-point programs. In general, it is not possible to completely avoid them", only to mitigate by conservative detection.
This names our sod_1d defect exactly: `sd > 0` and the `argmin` over standardized distances are unstable tests; a 1-ULP dither flips the branch and moves a *frozen reference floor* by 3.1e-1.
It also supplies the right remedy shape — the guard should be conservative/warning-emitting (or the degenerate dimension dropped outright), not tolerance-tuned.

### Term 2 — float32/float64 seams in SciML benchmarks

Results: "Speeding up and reducing memory usage for scientific machine learning via mixed precision" https://arxiv.org/html/2401.16645v1 (+ ScienceDirect version) ; DL schemes for singularly perturbed convection–diffusion https://arxiv.org/pdf/2205.04779 ; several mixed-precision hardware patents ; a vendor FAQ.
Snippet-level: this literature studies precision as a **training/efficiency knob** (fp16 fails in SciML from gradient divergence; fp64 can hinder convergence; fp32 is the stable operating point) and handles run-to-run variability by repeating runs and reporting mean ± sd.
**No usable result** on precision as an *evaluation-metrology* problem — i.e. nobody here sets a reproduction tolerance from the loader/dtype path of the benchmark itself.
Record as a partial dead end: the phrase "float32 vs float64" pulls training-efficiency work, not eval-tolerance work.

### Term 3 — fit-set-size asymmetry between arms

Results: **"Tune It or Don't Use It: Benchmarking Data-Efficient Image Classification"** https://arxiv.org/pdf/2108.13122 ; "Image Classification with Small Datasets: Overview and Benchmark" https://arxiv.org/pdf/2212.12478 ; ABCFair (NeurIPS 2024 D&B) https://proceedings.neurips.cc/paper_files/paper/2024/file/46bae562da84d63269673808e8eff777-Paper-Datasets_and_Benchmarks_Track.pdf ; "Less is more: Not all samples are effective for evaluation" https://arxiv.org/html/2601.03272 ; Gate AI LLM security benchmark https://arxiv.org/pdf/2606.02959 ; "Training variance and performance evaluation of neural networks in speech" https://arxiv.org/pdf/1606.04521 .

**FETCHED — "Tune It or Don't Use It"** (Brigato, Barz, Iocchi, Denzler), https://arxiv.org/pdf/2108.13122 (42,978 chars).
Verbatim: *"most existing works compare their proposed method against insufficiently tuned baselines or baselines trained with default hyper-parameters, which makes it easy to outperform them"*; *"Comparing against an untuned baseline with default hyper-parameters is as good as no comparison at all"*; and *"To perform a fair comparison, we use the same backbone CNN architecture for all methods."*
Their result — a properly tuned plain baseline beats all but one specialized method — is the canonical statement of the *procedure-matching* immutable this project already enforces (program.md §5, matched-procedure arm comparisons).
The **budget** dimension (same *architecture*, same *tuning effort*) is published; the specific asymmetry we found (**reference arm fitted on 400 rows while the scored arm sees 320**) is a *fit-set-size* mismatch, which this paper does not address.

**FETCHED — Gate AI LLM Security Benchmark Evaluation Methodology** https://arxiv.org/pdf/2606.02959 (51,397 chars) — fetched to check the search engine's "matched sample size protocol / draw subsamples of the same size / matched-n interval" summary, which the engine rendered without attribution.
Greps for `matched-n`, `matched n`, `subsample`, `same size` returned **nothing** in the fetched body.
**That summary is therefore NOT attributable to any source retrieved in this loop and must not be cited.** (Recorded as an explicit anti-citation: the phrase was a search-engine synthesis.)

## Interpretation

C3 splits cleanly: ULP/relative tolerance selection with an absolute near-zero floor is standard verification engineering (MathWorks docs; snippet level), while the interesting half — a frozen reference floor whose value is governed by an **unstable test** — is a named and formally studied class (arXiv:1808.04289), which we should cite and adopt rather than claim.
C4's matched-procedure principle is published (arXiv:2108.13122); the fit-set-size seam is a project-local fairness defect, and no retrieved source discusses reference arms fitted on more rows than the scored arm.
Remaining iterations go to the mandatory refutation pass on the three candidate directions.
