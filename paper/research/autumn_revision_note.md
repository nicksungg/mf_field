# Workflow framing check, 14 September 2026

The requested “autumn paper” could not be identified confidently. No AUTUMN citation was found in the local bibliography or research notes. Targeted searches did not identify a relevant primary AutoML publication with that name. Do not introduce an AUTUMN citation or silently equate it with AutoGluon. The following are verified references already present in the bibliography.

Nick Erickson, Jonas Mueller, Alexander Shirkov, Hang Zhang, Pedro Larroy, Mu Li, and Alexander Smola. *AutoGluon Tabular: Robust and Accurate AutoML for Structured Data*. arXiv:2003.06505, 2020. Primary source: https://arxiv.org/abs/2003.06505 and PDF https://arxiv.org/pdf/2003.06505. Existing key: `erickson2020`.

Its abstract leads with the system and a concrete user action. The introduction connects practical modeling expertise to a repeatable workflow. The pipeline preprocesses supplied tables, partitions data, trains a defined portfolio, and combines predictions through stacking and bagging. Claimed contributions include codifying established practices, specific stacking extensions, and a substantial comparative evaluation. Transferable framing is the visible interface and explicit sequence from supplied data to a predictor. AutoMF should not inherit its claims about raw data handling, time budgets, multilayer stacking, or comprehensive automatic selection.

Matthias Feurer, Katharina Eggensperger, Stefan Falkner, Marius Lindauer, and Frank Hutter. *Auto Sklearn 2.0: Hands free AutoML via Meta Learning*. JMLR 23(261):1–61, 2022. Primary source: https://jmlr.org/papers/v23/21-0992.html. Existing key: `feurer2022`.

This paper motivates automation through the burden of configuring learning pipelines. It separately evaluates automation of the model search policy itself. This separation supports distinguishing AutoMF's automated weight fitting from the still incomplete evaluation of automatic choice among weighting rules.

Suggested original opening, with no hyphens or semicolons:

“We present AutoMF, a workflow for constructing field surrogates from simulation parameters and outputs at multiple fidelities. It trains a diverse library of models and uses reserved fine solutions to determine how their field predictions should be combined.”

The next sentence should state the evidence scope precisely, for example: “Across 20 datasets with a common comparison, we evaluate individual models, published method adaptations, and fixed ensemble rules, with automatic rule selection assessed separately.” The same fixed weights apply to all new inputs within a dataset. The main aggregate evidence does not demonstrate that the complete automatic selector beats competing systems on every dataset.
