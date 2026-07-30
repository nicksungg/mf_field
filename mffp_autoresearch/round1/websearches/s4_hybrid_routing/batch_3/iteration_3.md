# iteration_3 — "corrector on an operator-cleaned residual"

## Search rationale

B2's directive is *change the TARGET, not the mixer*: the corrector should be
handed the node-aligned / LSI-cleaned residual, not the raw `hf - copylf`
residual (which s2-B2 showed is ~100 % re-learned registration). The refutation
question is therefore: **is a trained corrector on top of a FITTED linear
pre-stage published?** Three angles: (a) the image-restoration form (fixed
deconvolution / linear prior, then a CNN residual), (b) the PDE form
(machine-learned defect correction on a coarse solve — s6's Richardson DC
lineage), (c) the signal-processing form (fit a linear/polynomial model, learn
only what it misses).

## Search terms used

1. `residual network correcting output of fixed deconvolution filter super-resolution two-stage linear prior then CNN residual`
2. `machine learned defect correction Richardson extrapolation coarse grid neural network correction operator learning`
3. `learn residual of a fitted linear shift-invariant transfer function neural network corrects what the linear filter misses`

## Findings

### Term 1 — two-stage residual SR
Returns: https://openaccess.thecvf.com/content_cvpr_2017_workshops/w12/papers/Fan_Balanced_Two-Stage_Residual_CVPR_2017_paper.pdf
(BTSRN: LR-stage residual blocks → deconvolution+nearest-neighbour upsample →
HR-stage residual blocks), https://arxiv.org/pdf/1907.05282 (attention DenseNet
with residual deconvolution), https://arxiv.org/pdf/2009.12433 (artifact-free
residual SR), https://www.sciencedirect.com/science/article/pii/S2666827021000815 ,
https://openaccess.thecvf.com/content_cvpr_2018/papers/Zhang_Residual_Dense_Network_CVPR_2018_paper.pdf .
Not fetched (budget spent on the two sharper angles). **The SR two-stage form
is unambiguously published**, but in every return the pre-stage is either a
*learned* deconvolution layer or a parameter-free interpolator — none of the
returns fits a **least-squares transfer function to the data** and then
corrects its residual. Recorded as: the *shape* is old, the *fitted-operator
pre-stage* is not evidenced here.

### Term 2 — learned defect correction on a coarse solve — **fetched (ar5iv)**
https://ar5iv.labs.arxiv.org/html/2102.01010 (Kochkov et al., *Machine learning
accelerated CFD*), **fetched via the ar5iv route** after
https://arxiv.org/pdf/2102.01010 returned a 3.1 MB binary. Verbatim:
- *"An alternative approach, closer in spirit to LES modeling, is to simply
  model a residual correction to the discretized Navier-Stokes equations."*
  with `u_t = u_t* + LC(u_t*)`, *"where LC is a neural network and u_t* is the
  uncorrected velocity field."*
- *"Rather than using typical polynomial interpolation ... here we use an
  approach that we call learned interpolation based on data driven
  discretizations."*
- Pre-stage: *"a standard implementation of a finite volume method on a regular
  staggered mesh, with first-order explicit time-stepping"* — i.e. a **fixed
  classical solver**, not a fitted operator.
- *"LI performs best, although learned correction (LC) is not far behind."*
So the coarse-solve-as-base + NN-correction composition is canonical prior art
(and s6-B1's mechanism is its MF instance), but the base is the raw solver.
Other returns: https://www.sciencedirect.com/science/article/abs/pii/S0045793023001962
(data-driven correction of coarse-grid CFD — vertex-wise discretization-error
prediction), https://www.sciencedirect.com/science/article/abs/pii/S0149197019302495
(CG-CFD ML error prediction), https://arxiv.org/abs/2002.02835 (Richardson
extrapolation *in ML* — hyperparameter extrapolation, a different object),
https://link.springer.com/chapter/10.1007/978-3-662-02427-0_14 (classical
extrapolation & defect correction).

### Term 3 — fitted linear model + NN on its residual — **fetched, weak extraction**
https://arxiv.org/pdf/2005.05655 (*Residual Neural Networks for Digital
Predistortion*), **fetched** (269 KB PDF; the fetcher returned only short
fragments — *"Residual learning on the PA"*, *"the inverse structure to identify
DPD coefficients"*, *"residual learning"* — the rest of its answer is the
fetcher's paraphrase and is recorded as such, **not** as quotation). Content
confirmed at paraphrase level: a generalized-memory-polynomial baseline is
identified first and the network then learns only the residual distortion, the
stated benefit being fewer parameters for equal performance. This is the
clearest published instance of "**fit the parametric operator first, learn its
residual**" — outside PDEs, in RF power-amplifier linearization.
Remaining returns were off-target (domain adaptation, patents, generic ResNet).
**No usable result** for a PDE/MF instance where the pre-stage is a *fitted*
LSI transfer function.

## Interpretation

Three separate literatures own pieces of the composition — SR owns
two-stage residual refinement, CFD owns NN-correction-on-a-coarse-solve
(fixed solver base), and RF-DPD owns fit-linear-then-learn-the-residual — but
none of the fetched sources fits a **data-fitted LSI operator** as the pre-stage
of a **multi-fidelity** corrector, which is exactly what B2's "hand the
corrector the OPERATOR" directive builds.
