# Iteration 1 — the linear/affine channel and the null-direction framing

## Search rationale

B1's part 7 names the linear/affine LF channel (E1) and the null-direction
completion framing (E2) as B2's live directions, and B1's own surprise list
says a ~60-line probe beat every network on `ifc_poisson`. Both are *statistics*
claims, not architecture claims, so turn 1 aims squarely at the classical
multi-fidelity-regression and transfer-learning-for-linear-regression
literatures — the places most likely to already contain them — plus the
"simple baselines beat neural operators" thread that decides how the result
must be framed.

## Search terms used

1. `multi-fidelity linear regression low-fidelity samples at different parameter values than high-fidelity samples design of experiments non-nested`
2. `transfer learning linear regression auxiliary source data spans null space of target design matrix rank deficient few samples`
3. `least squares linear baseline outperforms neural operator few high-fidelity samples parametric PDE surrogate`

## Findings

### Term 1 — non-nested multi-fidelity linear regression

Top returns: arXiv:2511.20183 (non-nested MF GP regression); arXiv:1705.02956
(LR-MFS, also AIAA J. 10.2514/1.J057299); S1270963824000610 (non-hierarchical
LF data); arXiv:2006.16728 (overview of GP-based MF with variable
inter-fidelity relationships).

**Fetched — arXiv:1705.02956 "Multi-Fidelity Surrogate Based on Single Linear
Regression" (LR-MFS/LS-MFS)** [cite: https://arxiv.org/abs/1705.02956]:
"the system behavior (high-fidelity behavior) is approximated by a linear
combination of the low-fidelity predictions and a polynomial-based discrepancy
function"; the **scaling coefficient and the discrepancy coefficients are
estimated simultaneously by a single least-squares fit**, with a design matrix
"consist[ing] of both the low-fidelity model and discrepancy function"; sold
explicitly as avoiding kriging hyperparameter optimization. The abstract does
NOT state whether LF/HF samples must be co-located.
→ This is the published form of E1's `c*A(cond) + R(cond)`: LF law as basis,
scalar scaling, additive discrepancy, ordinary least squares.

**Fetched — arXiv:2511.20183 "Efficient multi-fidelity Gaussian process
regression for noisy outputs and non-nested experimental designs"**
[cite: https://arxiv.org/abs/2511.20183]: states that the classical
Kennedy-O'Hagan / recursive Le Gratiet formulation **assumes nested designs
(LF and HF at identical parameter values)** and that non-nested data breaks the
recursion; fixes it with an EM-based decoupled optimization; benefit framed as
training-time reduction "especially when large low-fidelity datasets are
available, while maintaining competitive predictive accuracy". Outputs appear
scalar/noisy-response, not fields.
→ **Non-nested LF/HF designs are an explicitly named, actively-worked setting.**
This materially weakens batch 1's `novel` verdict for D3 ("LF at conditions
disjoint from HF") as a *statistical* setting — see iteration 3's refutation
turn.

### Term 2 — null space of the target design

Top returns: Cai/Li Transfer-Learning-HDLR (JRSS-B 84(1) 149); arXiv:2510.15337;
Trans-Lasso descendants; arXiv:2202.05069 (different input dimensions).

**Fetched — arXiv:2510.15337 "Transfer Learning for Benign Overfitting in
High-Dimensional Linear Regression"** [cite: https://arxiv.org/html/2510.15337]:
two-step Transfer-MNI (pretrain on source, fine-tune on target near the
pre-trained model). Key quoted sentence: *"the fine-tuning step for TM retains
target-learned signal in the span of n_0 target samples ... while transferring
source information only into the null space S_0^perp where the target samples
provide no information"*, called the **retain-plus-transfer** mechanism.
→ E2's mechanism sentence — "the source rows supply exactly the direction the
target design cannot see" — is **published**, in the p > n linear-regression /
minimum-norm-interpolation setting. The composition (source = a *coarser
consistent PDE solve at different parameter values*; target = 5 HF field rows;
response = an (H,W) field) is not what that paper studies, but the mechanism
claim itself cannot be presented as new.

### Term 3 — closed-form/linear baselines vs neural operators

Returns: arXiv:2606.29440 (PCA-RaNN: PCA + fixed random features + closed-form
least-squares readout; "recasts latent operator learning as fixed-feature
linear regression", 1-3 orders of magnitude faster, competitive accuracy —
independently retrieved by `websearches/r2s1_direct/batch_2`);
arXiv:2512.21319 (reduced-basis neural operator with a posteriori error
estimation); arXiv:2512.11168 (optimal weighted least-squares for operator
learning); arXiv:2509.06154 (data-efficient surrogates comparison);
arXiv:2606.17460 (operator boosting). No fetch spent — the search-returned
descriptions already establish the point and PCA-RaNN was fetched in the
sibling stream's loop.
→ "Closed-form least-squares readout competitive with / faster than neural
operators" is an established 2026 position. A linear-probe-beats-FNO result is
therefore **not itself a contribution**; it is a baseline-discipline finding.

## Interpretation

Both of B2's statistical directions have named published ancestors that batch 1
did not retrieve: LR-MFS for the affine LF channel's functional form, and
Transfer-MNI's retain-plus-transfer for the null-space mechanism, plus an
explicit non-nested-design MF-GP literature that undercuts the "disjoint
conditions are unusual" framing. The remaining novelty must therefore be
argued at the level of *composition and measurement* (field-valued response,
LF = coarse consistent solve, N_hf = 5, matched with/without-LF accounting,
training-free per-dataset gating), not mechanism — which is exactly the
failure mode program.md §13.3 warns about (0-for-4).
