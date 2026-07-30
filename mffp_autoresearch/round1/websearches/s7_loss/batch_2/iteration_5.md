# Iteration 5 — `s7_loss` batch 2 (§3.3 refutation pass, part 2 + verdicts)

**ITERATION CAP REACHED (k = 5).** No further search turns are permitted; the
prior-art verdicts below are final for this batch.

## Search rationale

Iteration 4 left two gaps: (a) the definition of the community-standard
neural-operator training loss was never grounded in a fetched source (the
library paper does not state it), which blocks a verdict on **D2 — the
metric-exact unsquared per-sample rel-L2 objective**; and (b) **D3** (copy-LF-
referenced per-sample weight) had been refuted only from the
weather-verification framing, not from the multi-fidelity framing or the
"difficulty from an external model" framing. This turn closes both, and gives
**D5** (jointly trained gain head) its second refutation attempt.

## Search terms used

1. `multi-fidelity loss normalized by low-fidelity error per sample train to beat the low fidelity baseline objective operator learning`
2. `sample weighting by reference model error external baseline difficulty score training regression not self-paced focal loss`
3. `jointly learned scale factor branch output gain neural network regression predicts unit-norm shape and magnitude two outputs`

(Plus a targeted source-code fetch for D2, listed under term 1's block.)

## Findings

### D2 — the standard neural-operator training loss (DECISIVE)

**Fetched**: `https://raw.githubusercontent.com/neuraloperator/neuraloperator/main/neuralop/losses/data_losses.py`
(the canonical `neuraloperator` library, the FNO authors' own code). The fetch
returns `LpLoss.rel()` computing **`||x−y||_p / (||y||_p + eps)`** — the
**per-sample, unsquared** norm ratio — with

```
if take_root and self.p != 1:
    diff = (diff ** (1.0 / self.p)) / (ynorm ** (1.0 / self.p) + self.eps)
else:
    diff = diff / (ynorm + self.eps)
```

`__call__` invokes `self.rel(y_pred, y)`, i.e. **the relative loss is the
default**, aggregated by `reduce_all()`. Denominator protection is an additive
`eps` (default `1e-8`), explicitly "no clamping — only epsilon regularization".

This settles three things at once: (i) training on the **exact scored
functional** (`mean_i ‖p−y‖₂/‖y‖₂`, program.md §2.1) is the field's default
practice, not a contribution; (ii) a denominator epsilon is a library-level
idiom; (iii) our champion's global-scaler `F.mse_loss` is a **deviation from
the community default**, and B1's `MFFP_S7_LOSS=rel` (`mean_i rel_i²`, clamp
`1e-4`) is a *third* variant — squared, and clamped rather than epsilon'd.
Those three are different per-sample gradient weightings and none of them is
novel.

### D3 — copy-LF-referenced per-sample weighting, MF framing

Term 1 top results: `https://arxiv.org/pdf/2402.18846` (Multi-Fidelity Residual
Neural Processes), `https://arxiv.org/pdf/2507.07292` (Discretization-
independent multifidelity operator learning), `https://arxiv.org/pdf/2304.06972`
(MF prediction via transfer learning with FNO),
`https://www.researchgate.net/publication/360079062_Multifidelity_Deep_Operator_Networks`,
`https://arxiv.org/html/2606.09857`.

Third independent pass, same answer as iterations 2 and 4: MF objectives use
**per-fidelity scalar weights** ("loss calculations can be adjusted to focus
more on optimizing toward the highest fidelity") and **L1 or L2 field losses**;
the LF model enters as a trunk input or as a residual target (architecture).
**No hit normalizes or weights the per-sample loss by that sample's
low-fidelity error.**

### D3/D5 — difficulty from an external model

Term 2 top results: `https://proceedings.neurips.cc/paper_files/paper/2023/file/50251f54848a433f3e47ae3b7cbded53-Paper-Conference.pdf`
("Learning Sample Difficulty from Pre-trained Models for Reliable
Prediction", NeurIPS 2023), `https://arxiv.org/pdf/2509.20786` (LiLAW),
`https://arxiv.org/pdf/2110.05481` ("Which Samples Should be Learned First").

This is the closest published family to D3's *shape*: a difficulty score from
an **external pre-trained model** entering the loss as instance-wise adaptive
weighting. **The fetch failed** (the NeurIPS PDF endpoint returned binary — the
same failure batch 1 documented), so per program.md §13.3 I **cannot cite it**;
it is recorded here as an unverified nearest neighbour that a future batch
should chase via an HTML mirror. The returned summaries indicate it is
classification with entropic regularization, not field regression, and the
"difficulty" is model-derived, not a reference *solution* error.

### D5 — jointly learned per-sample output gain

Term 3 top results: `https://www.emergentmind.com/topics/learned-scaling-factors`,
`https://arxiv.org/html/2403.04545`, `https://arxiv.org/pdf/2606.25971`, plus
several quantization patents.

**Fetched**: `https://www.emergentmind.com/topics/learned-scaling-factors`.
Verbatim from the fetch: "**there is no documented evidence of networks
predicting per-sample scalar output gains jointly with normalized predictions**
for fields, signals, or PDE surrogates". The documented learned-scale families
are global/blockwise energy-term scaling (structured prediction), latent-space
spectral scaling (generative), **global** uniform multiplicative scaling in
physical simulation ("applied globally per chemistry model, not per sample"),
and per-parameter-block transfer scaling (aTLAS); the page explicitly separates
these from weight-normalization/quantization scale factors, and states "No
named methods for per-sample gain prediction alongside shape normalization
appear in this content."

## Prior-art verdicts

### D1 — A0 (`MFFP_S7_LOSS=rel`, λ=1, `mean_i rel_i²`) on `sharp__allen_cahn_2d` alone
**`preempted`** (mechanism), and *no novelty claim is required or available*.
Grounding: the relative per-sample loss is the neuraloperator library default
(`https://raw.githubusercontent.com/neuraloperator/neuraloperator/main/neuralop/losses/data_losses.py`),
and batch 1 already returned `preempted` for C-REL. Nearest neighbours: the
library `LpLoss` (unsquared, eps `1e-8`) and this repo's own
`transolver_residual` clamp idiom. **What this arm buys is not novelty but
disambiguation** of B1's own λ>1 mechanism (card part 7's three pre-registered
outcomes); it is a measurement of a falsified in-house lever, which §13.3 does
not require to be novel. Must never be written up as a method contribution.

### D2 — metric-exact **unsquared** per-sample rel-L2 objective (`mean_i ‖p−y‖/‖y‖`)
**`preempted`**. Fully owned by `LpLoss.rel()` + `__call__` in the FNO authors'
own library (URL above); the survey `https://arxiv.org/html/2307.02694v3`
independently shows the loss-function literature treats scale-normalized
objectives as a metrics footnote with no formulations. Nearest neighbour is
literally the reference implementation of the architecture family we use.
**What remains reportable**: the *measurement* that this repo's champion
deviates from the community-default objective (global-scaler `F.mse_loss` at
`mf_fno_transfer_film/smoke_eval.py:96`), and by how much on the panel — a
control, not a contribution. Note the three variants differ concretely:
unsquared+eps(1e-8) [library] vs squared+clamp(1e-4) [B1 `rel`] vs
global-scaler MSE [champion].

### D3 — per-sample loss weight from the **copy-LF error**, `w_i ∝ 1/‖y_i − LF_i‖²`
**`preempted-but-MF-composition-open`** — *and independently contraindicated by
this project's own metric definition; recommend NOT proposing.*
Fetched nearest neighbours: none normalize by a reference model's per-sample
error. Skill is verification-only in the meteorological literature
(`https://glossary.ametsoc.org/wiki/Skill`,
`https://www.cawcr.gov.au/projects/verification/`); MF losses use per-fidelity
scalar weights (`https://arxiv.org/abs/2204.06684` from batch 1, re-confirmed
here by `https://arxiv.org/pdf/2402.18846`, `https://arxiv.org/pdf/2507.07292`);
`https://www.emergentmind.com/topics/weighted-loss-function` states
baseline-error formulations "are not elaborated" and warns that "excessive
boosting of rare examples … can destabilize training … or distort global
performance". **Open**: per-sample weighting by an independent lower-fidelity
solve's error inside an MF field-regression objective.
**Why I still recommend against it**: program.md §2.2 makes the copy-LF
reference a **per-dataset scalar** (`skill = nRMSE(model)/nRMSE(reference)`),
so the scored per-sample denominator is `‖y‖`, not `‖y − LF‖`. Weighting by
`1/‖y−LF‖²` is therefore *anti*-aligned with the frozen metric, and on
`sharp__phase_field_crystal_2d` — where 62/100 test samples have copy-LF
rel-L2 `5.8e-08` (B1 part 6) — the weight would span ~14 orders of magnitude,
a far worse conditioning problem than the `hf_norm_spread` 22.7/5017 that
already cratered B1. Any card proposing it must show the `‖y−LF‖` spread first
under B1's own M6 design rule.

### D4 — tempered per-sample norm weight `w_i = ‖y_i‖^{−2β}`, β ∈ [0,1]
**`preempted`**. The exponent-swept magnitude/frequency weight is the standard
imbalance-weighting idiom — inverse-frequency and effective-number weighting
with swept exponents, and class-distance weighting with a tunable α, both
documented at `https://www.emergentmind.com/topics/class-weighted-loss`;
`https://www.emergentmind.com/topics/normalized-loss-function` documents
per-sample normalization by target magnitude as a means "to equalize
heteroscedastic task difficulty". No fetched source applies the exponent to
per-sample field norms, but the mechanism is a **knob, not a finding**, and
under program.md §1 it is local-optimum tuning: β interpolates between two
objectives whose endpoints this stream will already have measured (MSE control
and D1/D2).

### D5 — jointly trained scalar **gain head** + normalized-shape training term
**`preempted-but-MF-composition-open`**.
Preempted parts: the gain-vs-shape decomposition and its oracle-substitution
evidence (Eigen 2014, `https://ar5iv.labs.arxiv.org/html/1406.2283`, batch 1
C-AMP); joint learning of an auxiliary output-head parameter alongside the mean
prediction for PDE surrogates — but only for **uncertainty**
(`https://arxiv.org/html/2602.11090`, `https://arxiv.org/html/2412.12069`);
per-sample post-hoc MF scale estimators (s1-B3's fetched set: ROMES, LR-MFS,
IFC, APEX).
**Open**, with a fetched negative statement backing it:
`https://www.emergentmind.com/topics/learned-scaling-factors` — "there is no
documented evidence of networks predicting per-sample scalar output gains
jointly with normalized predictions for fields, signals, or PDE surrogates";
SR/field-normalization practice normalizes by **dataset constants**
(`https://arxiv.org/html/2406.17244v2`, `https://arxiv.org/html/2411.07576v2`,
`https://arxiv.org/pdf/2101.09839`).
**Caveats the brainstormer must carry**: (i) a predicted output gain is an
**output-parameterization / architecture** change as much as a loss change —
ADR 0012 scopes s7 to the training objective, so the loss-only form is
"normalized-shape term + explicit gain term at λ ≤ 1", which is B1's `amp`
objective restricted to the regime B1 proved safe, i.e. **already built**;
(ii) `experiment_cards/s1_poisson/batch_3/B3.json` is currently running the
post-hoc closed-form version on a different stream — a jointly-trained s7 arm
must state the contrast and must not duplicate it; (iii) B1's F5/F6/F8 forbid
aiming any per-sample-normalized objective at pfc / cahn_hilliard.

## Interpretation

Nothing in five turns produced an unoccupied *loss mechanism* for this stream;
what the search did produce is a decisive grounding that the champion's
objective is a deviation from the FNO community default, which converts D1+D2
from "another loss idea" into a cheap, pre-registered, decisive measurement.
D5 is the only direction with an open composition, and it half-belongs to
architecture and half-overlaps a running s1 card.
