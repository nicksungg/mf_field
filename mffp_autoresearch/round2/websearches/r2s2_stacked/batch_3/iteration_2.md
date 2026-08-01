# Iteration 2 — field context: fitted spectral transfers, retrieval baselines, and "simple baseline" benchmarking

## Search rationale

Iteration 1 established that closed-form MF corrections and training-free correctors both exist as classes.
Three gaps remained. (a) Is the specific object — a **Wiener/LSI transfer fitted from coarse-fine training
pairs** and applied to a surrogate field — published in the PDE/turbulence super-resolution literature?
(b) Is the **k-NN-average-of-training-fields** intermediate an established baseline (it is B2's stage 1)?
(c) For direction (iii) — the closed-form filter as a zero-parameter *evaluation bar* — is there a canonical
citation for "publish the simple baseline as the bar"?

## Search terms used

1. `Wiener deconvolution transfer function fitted from coarse-fine simulation pairs spectral correction turbulence super-resolution`
2. `analog ensemble nearest-neighbor retrieval baseline with linear correction outperforms neural network downscaling`
3. `simple linear baseline outperforms deep learning surrogate benchmark reality check scientific machine learning`

## Findings

### Term 1 — fitted Wiener transfer between coarse and fine solves

**No usable results for the exact object.** The returned set is dominated by instrument/optics deconvolution:
eddy-covariance frequency-response correction via Wiener deconvolution
https://link.springer.com/article/10.1007/s10546-023-00799-w; optical-aperture image restoration
https://www.sciencedirect.com/science/article/abs/pii/S0030402617310033 (ScienceDirect, 403 per the standing
dead end); a Fermilab student note on Wiener deconvolution for analog signals
https://lss.fnal.gov/archive/2025/pub/fermilab-pub-25-0551-student.pdf; plus generative turbulence
super-resolution via stochastic interpolants https://arxiv.org/html/2508.13770 (a *generative* SR method, not
a fitted linear transfer). Snippet-level statement of the classical mechanism ("a Wiener filter applies a
smoothly decreasing amplification factor at higher frequencies according to signal-to-noise ratio") confirms
the textbook status of the filter itself but no PDE-surrogate composition.
Reading: the Wiener filter is textbook; **applying one fitted from LF/HF training pairs as the corrector
stage of a multi-fidelity field stack did not surface in this term.**

### Term 2 — retrieval / analogue intermediates

Snippet-level only. Analogue/k-NN resampling is an established statistical-downscaling family: the search
synthesis describes analogue downscaling as *"resamples existing RCM data based on a nearest neighbor search
in GCM data, selecting similar GCM days and using their corresponding RCM days as probabilistic predictions"*,
with the noted strength that *"it yields samples with the correct spatial pattern, as they are all drawn from
the existing RCM data"*; Gangopadhyay et al. 2005, "Statistical downscaling using K-nearest neighbors",
Water Resources Research https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2004WR003444 is the
canonical reference returned (FETCH FAILED, HTTP 403 — Wiley joins the ScienceDirect/ResearchGate 403 list,
so this stays snippet-level). Also returned: EnScale https://arxiv.org/pdf/2509.26258; twin-NN-improved kNN
regression https://arxiv.org/pdf/2310.00664.
Reading: **k-NN-average-of-training-fields is a classical baseline family (analogue downscaling)**, which is
exactly why r2s2's stage 1 is a floor-class object, not a contribution — and it corroborates B2's own
amplitude finding (averaging analogues attenuates; the field's fix is to resample rather than average).

### Term 3 — simple baselines as the bar

**FETCHED (abstract extracted this loop)** — "Optimal Linear Baseline Models for Scientific Machine Learning"
https://arxiv.org/abs/2508.05831: *"We derive closed-form, rank-constrained linear and affine linear optimal
mappings for forward modeling and inverse recovery tasks... We validate our theoretical results by conducting
numerical experiments on datasets from simple biomedical imaging, financial factor analysis, and simulations
involving nonlinear fluid dynamics via the shallow water equations. This work provides a robust baseline for
understanding and benchmarking learned neural network models for scientific machine learning problems."*
Reading: the **"closed-form linear/affine optimal map as the benchmarking bar for learned models in SciML"**
programme is published, with PDE (shallow water) experiments. Direction (iii)'s *framing* is therefore
preempted; what 2508.05831 does not contain is a multi-fidelity composition (no LF stage, no retrieval
intermediate) or a spatially-invariant Fourier-domain transfer.

**FETCHED** — Ahlmann-Eltze, Huber et al., "Deep-learning-based gene perturbation effect prediction does not
yet outperform simple linear baselines", Nature Methods https://www.nature.com/articles/s41592-025-02772-6:
*"Here we compared five foundation models and two other deep learning models against deliberately simple
baselines for predicting transcriptome changes after single or double perturbations. None outperformed the
baselines, which highlights the importance of critical benchmarking in directing and evaluating method
development."* Note the adversarial reply also exists and was returned:
https://www.biorxiv.org/content/10.1101/2025.10.20.683304.full.pdf ("Deep Learning-Based Genetic Perturbation
Models *Do* Outperform Uninformative Baselines on Well-Calibrated Metrics") — i.e. the field's own lesson is
that **which metric you score the baseline in decides the verdict**, which is precisely r2s2-B2's
H-RULE-UNITS finding (relative error reduction vs skill units) arriving from an unrelated domain.
Also returned (snippet-level): linear vs deep scaling on UK Biobank brain images
https://www.nature.com/articles/s41467-020-18037-z.

## Interpretation

The *evaluation-bar* framing of direction (iii) is preempted at the programme level (arXiv:2508.05831 closed-form
optimal linear maps as SciML benchmark; Nature Methods s41592-025-02772-6 for the "compare against deliberately
simple baselines" discipline), and stage 1 (k-NN analogue averaging) is a classical downscaling baseline.
Neither the fitted LSI/Wiener transfer on a multi-fidelity intermediate nor the *attribution* result
(a zero-gradient stage carrying 33-100% of a trained stack's out-of-fold gain) surfaced in any fetched source —
that attribution remains the stream's candidate open content.
