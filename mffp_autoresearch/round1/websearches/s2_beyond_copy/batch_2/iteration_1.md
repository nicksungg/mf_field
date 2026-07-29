# Iteration 1 — the LF-field-as-input-channel residual operator

**WebSearch calls**: 3 | **WebFetch calls**: 4 (2 usable, 2 dead)

## Search rationale

Batch-2's prescribed candidate (card part 7) is: feed the interpolated
`max(lf_fids)` field as an **input channel** to the FiLM-FNO backbone and
predict `hf - lf`, adding copy-LF back at the output. §13.3 says the project is
0-for-4 on novelty, and the in-repo report
`docs/reports/MF_Leaderboard_Beaters_2026_Report.md` already asserts that
"the residual delta = u_HF - u_LF is becoming the standard learning target".
So iteration 1 goes straight at the refutation: find the closest published
instances of *coarse field in as a channel -> residual out*, and record what
exactly they report (setting, baselines, HF sample count). Third term probes
the neighbouring SR/coarse-grid-correction literature, which is where the
same composition would live under a different vocabulary.

## Search terms used

1. `neural operator takes coarse solution as input channel predicts correction residual multi-fidelity fine grid`
2. `multi-fidelity fusion model concatenate low-fidelity field input channel FNO predict HF-LF residual few high-fidelity samples`
3. `deep learning super-resolution coarse simulation field input predict fine-grid residual compared to bicubic interpolation baseline PDE`

## Findings

### Term 1 — coarse-solution-in / residual-out neural operators

Results list: LRC-FNO (https://arxiv.org/html/2606.17733), Error-Conditioned
Neural Solvers (https://arxiv.org/html/2606.27354), Multifidelity DeepONet
(https://arxiv.org/pdf/2204.06684), Flow-matching operators
(https://arxiv.org/pdf/2512.12749), MFFM (https://arxiv.org/pdf/2605.16118),
IRNO (https://arxiv.org/html/2605.24041).

**FETCHED — LRC-FNO, "Latent Residual-Closure Fourier Neural Operator for
Robust Multi-Field Solving in Particle-in-Cell Simulations"**
[cite: https://arxiv.org/html/2606.17733]. This is a direct structural match
to our candidate. Fetched quotes (Section 3.2):
- "The Coarse-FNO Solver takes the source proxy as input ... and outputs the
  coarse-scale solution field on a downsampled grid".
- "The coarse-scale solution field is upsampled to the original grid to obtain
  the upsampled coarse solution ... The upsampled coarse solution and the
  source proxy are then concatenated as the input of the Residual-Closure
  FNO".
- "The final full-resolution solution field is obtained by adding the coarse
  solution and the residual correction" (their Eq. 34).
Baselines: L-FNO (single-stage, predicts full resolution directly) and
L-FNO-CNN (with a parallel CNN local branch). The fetch explicitly reports:
**they do NOT compare against the coarse solution alone as a standalone
baseline.** HF sample counts are case-specific (e.g. "80 samples for training"
on 2D TSI); no cumulative dataset size given.

**DEAD — Multifidelity DeepONet (https://arxiv.org/pdf/2204.06684)**: PDF
fetch returned undecoded binary streams. No claim made from it in this
iteration.

Search-synthesis text (search result, not a fetch): "Refining an
already-computed approximate solution is easier than solving from scratch; the
residual carries far less variance than the field itself, with a coarse-mesh
solver capturing macroscopic structure while the residual is concentrated
where the cheap solver loses resolution."

### Term 2 — MF-FNO with LF as input / residual

Results list: Practical multi-fidelity ML (https://arxiv.org/abs/2407.15110),
MF-FNO for geological carbon storage
(https://www.sciencedirect.com/science/article/abs/pii/S0022169424000350),
MF-FNO transfer learning (https://arxiv.org/pdf/2304.06972), non-stationary
spatio-temporal MF data fusion (https://arxiv.org/html/2605.03693v1),
single-to-multi-fidelity history-dependent learning
(https://arxiv.org/pdf/2507.13416).

**FETCHED — https://arxiv.org/abs/2304.06972** (abstract page only): the
mechanism is *transfer learning*, "jointing abundant low-fidelity data and
limited high-fidelity data under transfer learning paradigm" — i.e. the SAME
mechanism as our own certified champion `mf_fno_transfer_film`, and the
abstract does not state whether LF enters as an input channel or a residual
target. So this paper is a neighbour of the champion, not of the candidate.

Search-synthesis text worth flagging as a threat to re-verify: "Transfer models
can take as input the decoded stress prediction from the low-fidelity RNN,
concatenated with the high-fidelity strain inputs" (attributed to
https://arxiv.org/pdf/2507.13416); "the low-fidelity model is transfer-learned
to the high-fidelity data and a Bayesian model is trained to learn the
residual between the data and the transfer-learned model"
(https://arxiv.org/abs/2407.15110). Both are LF-output-as-input compositions
outside the field/operator setting (constitutive modelling, scalar/tabular
fusion).

### Term 3 — super-resolution / coarse-grid-correction vocabulary

Results list: data-driven correction of coarse-grid CFD
(https://www.sciencedirect.com/science/article/abs/pii/S0045793023001962),
"Redefining Super-Resolution: Fine-mesh PDE predictions without classical
simulations" (https://arxiv.org/abs/2311.09740), FV features + residual
training (https://arxiv.org/pdf/2311.14464), composable ML for steady-state
high-resolution grids (https://arxiv.org/pdf/2210.05837), SR survey for fluid
flows (https://link.springer.com/article/10.1007/s00162-023-00663-0).

Search-synthesis text: "**Residual training** trains the network to predict the
residual field (F - Upsample(F_LR)), where F_LR is the low-resolution field,
instead of the original field F itself. Since the low-resolution field is an
approximation of the ground truth, much of the residual field will be close to
zero, which eases learning" (attributed to https://arxiv.org/pdf/2311.14464).
**DEAD** — the PDF fetch of 2311.14464 returned undecoded binary; the quote
stands as search-result text only, not a fetched citation.

## Interpretation

The exact composition our card part 7 prescribes — upsample the coarse field,
concatenate it as an input channel, predict a residual, add it back — is
published verbatim in LRC-FNO (fetched). Novelty for direction (i) is
therefore dead as a *mechanism*; what survives is (a) that LRC-FNO's "coarse
solution" is its own network's coarse-FNO output, not a real coarse PDE solve
(our immutable 1), and (b) the fetch confirms LRC-FNO does not baseline
against the coarse field itself — the same gap batch 1 found in 2604.20061.
