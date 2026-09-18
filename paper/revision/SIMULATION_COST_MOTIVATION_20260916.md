# Motivation for ensemble computation

Source inspected: the author's local `niu24d.pdf`, Niu et al. (2024), *Multi-Fidelity Residual Neural Processes for Scalable Surrogate Modeling*. The existing bibliography entry is `niu2024`.

The source's introduction, PDF page 1, motivates multifidelity modeling through the cost of high fidelity simulation. Its climate task, Section 5.1 on PDF page 6, combines outputs from 13 climate models with ERA5 reanalysis and maps climate drivers to temperature fields. Section 6 on PDF page 9 states that ancestral sampling doubles MFRNP inference time, while describing that overhead as small relative to the underlying simulators. This is an argument about MFRNP's own overhead, not a timing result for AutoMF.

The revised introduction paraphrases and cites that argument, then makes the AutoMF connection: multiple surrogate candidates can reuse simulation data, and selection and combination share the same reserved fine fitting examples. When generating physical fields dominates the resource budget, additional computation on surrogates can be a reasonable tradeoff. ERA5 is described as reanalysis, not a simulator the authors ran to obtain each target. No climate simulation wall time, AutoMF speedup, or measured cost dominance is invented.

The discussion retains accounting for all candidates, shared coarse ensembles, and fine fitting labels, and makes the dependence on query count and accuracy explicit. The conclusion connects the empirical case for ensemble fitting to applications where more field data are expensive and extra surrogate computation is acceptable. The abstract, scientific results, numerical tables, and original manuscript are unchanged.
