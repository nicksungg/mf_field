# Multi-fidelity fusion — what it is, and how the MFFP models group

**Purpose:** define "MF fusion" and sort the benchmark's models into fusion vs other categories.

> **Sourcing caveat.** Categorizations below are marked: **[deck]** = stated in
> `mf_field_prediction.pptx` slide 5 (authoritative); **[name]** = *inferred from the model name*
> because the deck didn't describe it — these should be confirmed against the actual model code in
> the MFFP repo before relying on them.

## The task all of these solve
Predict the **high-fidelity (HF)** 2D solution field from a small **condition vector** + the cheap
**low-fidelity (LF)** field(s), given **few HF training samples** but abundant LF. Input = condition
vector + LF field(s); output = HF field (deck slide 2).

---

## Category A — Multi-fidelity FUSION
**Definition:** explicitly **combine information across fidelity levels** to predict HF — the LF
carries most of the signal and the model learns the (smaller, structured) gap. LF is consumed at
inference (as input and/or as a stacked predictor). Three mechanisms:

### A1. Residual / additive stacking
$\text{HF} \approx \text{LF}_{\uparrow} + \text{learned correction}$. The model learns the
**difference** $\text{HF} - \text{LF}$, which is
small and concentrated at the hard features. *(This residual is exactly the "Error between LF and
HF" panel in our one-pagers.)*
- `fno_mf_stack` — one FNO per fidelity; HF FNO predicts a residual on aggregated upsampled LF (MFRNP-style). **[deck]**
- `fno_additive` — additive correction on LF. **[name]**
- `fno_autoregressive` — predict each fidelity from the one below, in sequence. **[name]**
- `fno_multilevel` — multigrid/multilevel-style correction across levels. **[name]**

### A2. Coregionalization (shared-basis)
Treat fidelity as a (continuous) variable; learn shared latent basis functions $h_k(x)$ combined
with fidelity-dependent weights $B_k(m)$ (head $y = \sum_k B_k(m)\,h_k(x)$). HF "borrows statistical
strength" from abundant LF.
- `fno_coregionalization` — FNO backbone + continuous-fidelity coregionalization head (IFC-style). **[deck]**
- `fno_coreg_conditioned` — coregionalization conditioned on fidelity. **[name]**
- `fno_coreg_residual` — hybrid: residual stack **+** coregionalization basis on the HF latent. **[deck]**

### A3. Attention-based cross-fidelity fusion
Use **cross-fidelity attention** so the HF prediction attends to LF features.
- `transolver_residual` — attention operator, residual form. **[deck]**
- `transolver_attention_fusion` (deck: "attention_fusion") — cross-fidelity attention as the fusion mechanism. **[deck]**

### A4. Published MF baselines (external reference fusion methods)
Established multi-fidelity methods, included for comparison. **[deck]** (named as baselines)
- `mfrnp` — Multi-Fidelity Residual Neural Process.
- `mf_deeponet` — multi-fidelity DeepONet.
- `d_mfd` — (deep multi-fidelity; confirm exact method in code).

---

## Category B — TRANSFER / FINETUNING (not fusion)
**Definition:** transfer knowledge **implicitly through weights** — pretrain on LF (or a related
task), then **finetune on HF**. LF is *not* fused as an input at inference; the model maps condition
vector → HF, having been warm-started from LF. **This is the family that WON the deck** ("FNO HF
finetuning baseline still wins," slide 6).
- `mf_fno_transfer`, `mf_fno_transfer_film`, `mf_fno_transfer_2m` — FNO pretrained on LF then
  transferred/finetuned to HF (FiLM = feature-wise modulation variant). **[name]**, consistent with
  the deck's "finetuning baseline" framing.
- `fno_coreg_lf_hf_transfer` — hybrid: coregionalization **+** LF→HF transfer (spans A2 and B). **[name]**

---

## Category C — Single-fidelity / plain baselines
**Definition:** no multi-fidelity mechanism — trained on HF alone (or a reference config), to show
what the MF/transfer machinery buys.
- `v9_baseline` — reference/baseline config (confirm whether single-fidelity in code). **[name]**

---

## Why the distinction matters for this project
The deck found **B (transfer/finetuning) beats A (fusion)** on a mostly-smooth dataset suite. The
hypothesis we're testing: **A should win back ground in the high-frequency regime**, because when HF
has sharp content that LF locates but can't resolve, the residual $\text{HF} - \text{LF}$ is small
and structured — exactly what A1 (residual fusion) exploits. The CH $\varepsilon$-sweep
([ch-sharpness-transition.md](ch-sharpness-transition.md)) is the controlled way to find where that
crossover happens.

## To make this authoritative
Confirm the **[name]**-tagged rows against the model definitions in the MFFP modeling repo (each
model class's forward pass shows whether it fuses LF at inference, uses a coregionalization head, or
just finetunes). This doc captures the deck-level taxonomy; the code is ground truth.
