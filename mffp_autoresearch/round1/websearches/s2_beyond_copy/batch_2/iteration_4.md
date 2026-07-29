# Iteration 4 — §3.3 refutation pass, part 1: kill direction (i) if it can be killed

**WebSearch calls**: 2 | **WebFetch calls**: 2 (both usable)
**ENOUGH declared on field context** after iteration 3: iterations 1-3 gave the
three literatures the task asked for (coarse-in/residual-out operators;
retrieval/analog residual transfer; hybrid parametric+nonparametric) plus the
baseline-discipline question. Iterations 4-5 are spent entirely on §3.3
refutation.

## Search rationale

Direction (i) is "LF field as an input channel to a FiLM-FNO, residual target,
few/moderate-shot MF". Iteration 1 already found LRC-FNO doing exactly the
composition, but LRC-FNO's "coarse solution" is its own network's output, not
a real coarse solve. The honest refutation must therefore attack the
**multi-fidelity** version specifically: (a) the MF-DeepONet line, where the
LF network's output is fed to the HF/residual network, and (b) MFFM, the
in-repo report's own headline MF residual method — with the specific question
of whether it baselines against the interpolated LF field (which batch 1
claimed nobody does).

## Search terms used

1. `multifidelity DeepONet low-fidelity network output as input to high-fidelity network residual composite Howard Karniadakis`
2. `multi-fidelity deep learning coarse grid solution correction phase field Allen-Cahn Cahn-Hilliard sharp interface surrogate`

## Findings

### Term 1 — the MF-DeepONet line (LF output appended, residual learned)

Results list: multifidelity DeepONet (https://arxiv.org/abs/2204.06684),
MF-DeepONet fusing simulation + monitoring data
(https://arxiv.org/pdf/2310.00057), DeepONet MF residual learning in ROM
(https://arxiv.org/pdf/2302.12682 / journal version
https://amses-journal.springeropen.com/articles/10.1186/s40323-023-00249-9),
data-efficient MF DeepONet with physics-guided subsampling
(https://arxiv.org/pdf/2503.17941), MF-DeepONet closure for multiscale systems
(https://www.sciencedirect.com/science/article/abs/pii/S0045782523002852).

**FETCHED — Multifidelity DeepONet (Lu/Howard/Karniadakis line)**
[cite: https://arxiv.org/abs/2204.06684]. Abstract-level quotes obtained:
"A multifidelity DeepONet includes two standard DeepONets coupled by
**residual learning and input augmentation**" and "Multifidelity DeepONet
significantly reduces the required amount of high-fidelity data and achieves
one order of magnitude smaller error when using the same amount of
high-fidelity data." (The abstract does not spell out the residual definition;
the search-synthesis text — NOT a fetch — adds: "LF DeepONet is trained ... to
produce baseline predictions, while a second separate network, residual
DeepONet, is trained to model the discrepancy between the low-fidelity and
high-fidelity outputs" and "**the low-fidelity prediction is appended to the
trunk net inputs to make the residual operator easier to learn**". Treated as
corroborating context, not as a fetched quote.)

### Term 1b (fetch) — MFFM, the strongest single refutation

**FETCHED — MFFM, "Multi-Fidelity Flow Matching: Cascaded Refinement of PDE
Solutions"** [cite: https://arxiv.org/html/2605.16118]:
- "We pose the refinement as conditional residual flow matching, learning a
  velocity model on the residual delta = u_HF - u_LF **conditioned on u_LF**."
- "Conditioning makes the residual refinement problem substantially easier
  than unconditional field generation."
- **Baseline table (9 methods)** includes **Bilinear (no-learning baseline)**,
  **FNO-direct**, **DeepONet-direct**, **FNO-residual**, **DeepONet-residual**,
  F-FNO, CNO, PDE-Refiner, FM (single-level), MFFM (cascade).
- The fetch confirms the bilinear-upsampling error IS reported, and equals
  "the relative L2 norm of the residual ||delta||/||u_HF||" — i.e. **our
  copy-LF baseline, under another name, already appears in a published MF
  operator paper's baseline table**.
- HF train sizes are per-benchmark, 175-2048 samples (their Table 4).

This is decisive on two counts. First, **`FNO-residual`** — an FNO conditioned
on u_LF predicting u_HF - u_LF — is a *named baseline* in a 2026 MF paper, not
even the paper's contribution. Direction (i) is the baseline of the current
literature. Second, batch 1's claimed gap ("no MF paper baselines against the
interpolated LF") is **too strong**: MFFM does exactly that. What survives of
the gap is narrower (see iteration 5).

### Term 2 — has anyone done this on sharp-interface phase-field data?

Results list: NPF-Net end-to-end DL for nonlocal Allen-Cahn / Cahn-Hilliard
(https://arxiv.org/abs/2410.08914 / https://arxiv.org/pdf/2410.08914),
fully-discrete-operator DL for Allen-Cahn
(https://www.sciencedirect.com/science/article/abs/pii/S0021999123006848).
The retrieved phase-field DL work is **single-fidelity, residual-of-the-PDE
(physics-loss) based** — NPF-Net's losses "are defined using the residual of
the fully discrete approximations", i.e. equation residuals, which ADR 0009
excludes at test time anyway. The search synthesis states plainly: "specific
results addressing **multi-fidelity or coarse grid solution correction**
strategies are not prominently featured in these particular results."
**No usable multi-fidelity phase-field result.**

## Interpretation

Direction (i) is preempted at the mechanism level three times over (LRC-FNO,
MF-DeepONet residual+input-augmentation, MFFM's `FNO-residual` baseline), and
MFFM further preempts the *comparison* against the interpolated LF field. The
only thing iteration 4 leaves standing for our setting is the **dataset
class**: no retrieved MF/coarse-correction work operates on sharp-interface
2-D phase-field data (Allen-Cahn / Cahn-Hilliard / PFC), where batch 1
measured that the fidelity residual is unlearnable on 2 of 5 datasets.
