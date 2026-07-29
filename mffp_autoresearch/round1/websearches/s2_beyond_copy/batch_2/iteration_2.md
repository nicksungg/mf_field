# Iteration 2 — retrieval / nonparametric residual transfer keyed on a field

**WebSearch calls**: 3 | **WebFetch calls**: 2 (both usable)

## Search rationale

Batch 1's headline (F6/F7) is a **zero-parameter, LF-field-keyed, k-NN
residual transfer**. The scouting sweep only found an image-domain neighbour
(RASR) and declared "no retrieval-augmented neural operator found in two
framings". §13.3 says distrust a clean-looking gap. Two literatures could
refute it and were NOT searched in batch 1 or the scouting sweep: (1) the
weather **analog method** (retrieval keyed on a coarse forecast field, used
for downscaling and MOS bias correction — a 20-year-old operational
technique), and (2) recent operator-learning work that learns residuals
between a query and a **retrieved similar training sample**.

## Search terms used

1. `analog ensemble method nearest neighbor past forecasts correction bias coarse model output statistics downscaling`
2. `retrieval-augmented neural operator PDE surrogate nearest neighbor retrieval from training set 2026`
3. `learning residual between query solution and retrieved similar training example neural operator data-limited DeltaPhi`

## Findings

### Term 1 — the analog method (weather downscaling / MOS)

Results list: AtmoSwing (https://gmd.copernicus.org/articles/12/2915/2019/),
MOS-Analog RCM bias correction
(https://agupubs.onlinelibrary.wiley.com/doi/10.1002/2016JD025724), analog
downscaling comparisons
(https://www.sciencedirect.com/science/article/abs/pii/S0022169412008839),
statistical downscaling of seasonal precipitation
(https://iopscience.iop.org/article/10.1088/1748-9326/add02c).

**FETCHED — AtmoSwing (GMD 12:2915, 2019)**
[cite: https://gmd.copernicus.org/articles/12/2915/2019/]:
- "AMs use synoptic-scale predictors to search in the past for similar days to
  a target day in order to infer the predictand of interest."
- The similarity key is a **coarse field**: geopotential height at 1000/500
  hPa (circulation analogy), then moisture variables as a secondary level.
- The comparison criterion is **Teweles-Wobus (S1)**, and the fetch quotes:
  "S1 allows for a comparison of the gradients and thus an analogy of the
  atmospheric circulation instead of considering the actual values at the grid
  points"; for other variables "classic criteria representing Euclidean
  distances between grid point values are used: mean absolute error (MAE) and
  root mean square error (RMSE)".
- Output: "the observed values of the predictand of interest ... for the N
  resulting dates provide the empirical conditional distribution considered to
  be the probabilistic forecast for the target day."

Search-synthesis text (search result, not a fetch): "Hamill and Whitaker
(2006) proposed a statistical postprocessing method based on historical
forecast similarity, which is an analog correction method comprised with
corresponding fine-resolution observations. The analog method can work on
precipitation downscaling and bias correction at the same time."

### Term 2 — retrieval-augmented neural operators

Results list: Operator Boosting (https://arxiv.org/abs/2606.17460), Graph
Neural Simulators vs neural operators (https://arxiv.org/html/2509.06154),
"Striding Across Reynolds Numbers" (https://arxiv.org/pdf/2605.30112),
**DeltaPhi** (https://arxiv.org/pdf/2406.09795), multiscale surrogates for
downscaling ocean currents (https://arxiv.org/html/2507.18067v2).
Search-synthesis notes a 2026 "systematic cross-Reynolds number zero-shot
evaluation comparing spectral, **retrieval**, and multi-scale methods"
(https://arxiv.org/pdf/2605.30112) — i.e. retrieval is now a named category in
neural-operator benchmarking. The scouting sweep's "no retrieval-augmented
neural operator" reading is **too strong**.

### Term 3 — DeltaPhi (the direct refutation)

**FETCHED — DeltaPhi, "Physical States Residual Learning for Neural Operators
in Data-Limited PDE Solving"** (NeurIPS 2025 poster; OpenReview
https://openreview.net/forum?id=ppOCvEonKT)
[cite: https://arxiv.org/pdf/2406.09795]. Fetched content:
- Mechanism: "retrieve the most similar training example" as an auxiliary
  reference; the model learns "the residual between the ground truth solution
  and the prediction from the auxiliary example"; at inference "predicted
  solution = retrieved output + learned residual correction".
- **Retrieval key is the input field similarity**: "identifies training
  samples whose input physical fields are closest to the test input, then uses
  their corresponding solutions as reference points".
- Data regimes: limited training samples (the fetch reports 5-50 examples in
  low-data scenarios) up to larger datasets; baselines FNO, DeepONet, standard
  supervised and other data-efficient operator methods.
- Search-result framing: it "transforms the PDE solving task from learning
  direct input-output mappings to learning the residuals between similar
  physical states", giving "implicit data augmentation by exploiting the
  inherent stability of physical systems where closer initial states lead to
  closer evolution trajectories"; "architecture-agnostic".

## Interpretation

Retrieval + residual composition is published on BOTH sides of our claim: in
operator learning as DeltaPhi (retrieve nearest training sample by input-field
similarity, predict a residual on top of its solution, data-limited regime),
and in weather as the analog method (retrieve by coarse-field similarity,
transfer the associated fine-resolution information; MOS-Analog does bias
correction and downscaling simultaneously). Our zero-parameter rule is
structurally an analog-MOS applied to the **fidelity** residual HF-LF and keyed
on the **LF solution** field rather than an input/predictor field — a
recombination, not a new mechanism. Actionable design steal: the analog
literature keys on **gradients** (Teweles-Wobus S1), not raw grid values,
which is directly testable against our 16x16 block-mean signature.
