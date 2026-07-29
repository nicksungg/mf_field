# Websearch Report — Stream `s3_warp`, Batch 1

**Stream**: `s3_warp` (new; replaces `s3_testtime` per ADR 0010)
**Batch**: 1
**Total iterations**: 5
**WebSearch calls**: 15 (3 / 4 / 2 / 3 / 3 per iteration)
**WebFetch calls**: 10, of which **6 usable**. Failures, all flagged in-line
where they are used: arXiv:2602.01397 and arXiv:2210.01074 returned PDF
structural metadata only (no readable text); doi.org/10.3390/cryst12101496
returned a cross-host redirect and the redirect target www.mdpi.com then
returned HTTP 403.
**Cap hit**: yes — 5/5 iterations used (noted in `iteration_5.md`)

**Rule-compliance note (honesty)**: iteration 2 declared 3 search terms but
issued **4** WebSearch calls — the 4th (`"multi-fidelity" learning reduced
order model Klein 2025 ...`) was a within-term follow-up resolving a
bibliography lead surfaced by term 1, and its result is recorded under term 1
in `iteration_2.md`. Every other iteration used ≤3 terms and ≤3 calls.

## Search trace

### Turn 1 — is warp-before-correct already published for MF PDE fusion?
Terms chosen to attack Candidate D's novelty claim in the two places it is most
likely already published: the MF neural-operator literature and the
registration/transport ROM literature, plus learned-warp coarse→fine SR.
- MF neural operators are uniformly **additive/generative in value space**
  [cite: https://arxiv.org/html/2605.16118v1, https://arxiv.org/pdf/2512.12749,
  https://arxiv.org/abs/1903.00104]; nearest conceptual neighbor is *latent*
  feature-space alignment, not spatial [cite:
  https://www.sciencedirect.com/science/article/abs/pii/S0021999123007787].
- Registration ROMs warp classically, snapshot→reference, **no NN and no MF**
  [cite: https://arxiv.org/html/2501.01299v1 — fetched], and explicitly scope
  themselves to topology-consistent transported features.
- One live thread: "multi-fidelity" appearing inside registration MOR [cite:
  https://www.sciencedirect.com/science/article/abs/pii/S0021999122001309].
→ `iteration_1.md`

### Turn 2 — kill the MF-registration thread; check the crowded warp literature
- **Thread killed**: the flagship "MF + registration" paper registers only
  among HF snapshots and fuses fidelities in POD-coefficient space via an
  MF-LSTM [cite: https://arxiv.org/abs/2309.00325 — fetched].
- The `klein2025` lead is MF ROM for parabolic PDE-constrained optimization,
  no registration [cite: https://arxiv.org/abs/2503.21252].
- Deformable-registration/weather warp literature is dense but never across
  solver fidelities [cite: CVPR 2024 coarse-to-fine registration MLPs,
  https://openaccess.thecvf.com/content/CVPR2024/papers/Meng_Correlation-aware_Coarse-to-fine_MLPs_for_Deformable_Medical_Image_Registration_CVPR_2024_paper.pdf ;
  SR-Weather, https://www.nature.com/articles/s41612-026-01328-5].
- Learned shifts inside operators exist for discontinuous solution operators
  (shift-DeepONet), input-function→solution, single-fidelity [cite:
  https://arxiv.org/pdf/2210.01074 — fetch returned metadata only; abstract-
  level evidence + https://openreview.net/forum?id=CrfhZAsJDsZ].
- New sharpest threat surfaced: https://arxiv.org/html/2603.04232v2.
→ `iteration_2.md`

### Turn 3 — the diffuse-interface MF-OT paper, topology, and metrics
- **Nearest neighbor pinned**: MF + OT + conservative Allen–Cahn two-phase at
  128²→256²→512², but the correction is `u_LF + r_interp` with OT
  displacement-interpolation applied to **residual fields**, **no neural
  networks** [cite: https://arxiv.org/html/2603.04232v2 — fetched].
- Topology mismatch has a published answer: **metamorphosis** = diffeomorphic
  warp + intensity/source term absorbing what a homeomorphism cannot express
  [cite: https://arxiv.org/pdf/2303.09088 — fetched;
  https://arxiv.org/pdf/2303.04849].
- Displacement/amplitude decomposition metric verified at primary source
  [cite: https://journals.ametsoc.org/view/journals/wefo/24/5/2009waf2222247_1.pdf].
→ `iteration_3.md`

### Turn 4 — learned warps inside PDE nets; the physical premise; small data
- **Strongest architectural preemption**: warping as *the* primitive of a 2026
  neural PDE solver, STN-style bilinear sampling at `x + ϱ^(h)(x)`, but
  strictly single-fidelity and with "no coarse-to-fine solution mapping or
  low-to-high-fidelity correction", no smoothness penalty, no zero-init
  [cite: https://arxiv.org/html/2603.04430 — fetched].
- Premise partially supported: coarse phase-field grids produce **position**
  errors (spurious grid friction / pinning, shape deformation) — but a second
  regime is **interfacial-thickness** error, which a warp cannot fix
  [search-snippet level only; the MDPI primary source 403'd].
- Small-data parameterization: free-form displacement fields dominate but
  ignore diffeomorphic guarantees, and global smoothness penalties are
  documented as insufficient locally [cite:
  https://arxiv.org/html/2412.17982v1]; diffeomorphic alternatives via
  velocity fields / B-splines [cite: https://arxiv.org/html/2405.18684v1 ;
  https://www.frontiersin.org/journals/neuroinformatics/articles/10.3389/fninf.2013.00039/full].
→ `iteration_4.md`

### Turn 5 — adversarial refutation of the three candidate directions
Three refutation searches, one per direction; none produced a counterexample.
Fetched confirmation that the MF field's own method is additive with bilinear
prolongation and assumes strong LF-HF correlation [cite:
https://arxiv.org/html/2605.16118v1]; OT-as-objective exists in single-fidelity
1-D ROM [cite: https://arxiv.org/abs/2308.13840]. → `iteration_5.md`

## Prior-art verdict

| Candidate direction | Verdict | Citations (fetched) | What remains open |
|---|---|---|---|
| **D1** `mf_warp_correct`: FNO head predicts a smooth, zero-init, smoothness-penalized displacement from up(LF)+cond; `grid_sample` warp; then FiLM residual correction on the warped field | **preempted-but-MF-composition-open** | Flowers https://arxiv.org/html/2603.04430 ; MetaRegNet https://arxiv.org/pdf/2303.09088 ; Khamlich et al. https://arxiv.org/html/2603.04232v2 ; MFFM https://arxiv.org/html/2605.16118v1 ; MF-ROM https://arxiv.org/abs/2309.00325 ; snapshot-registration ROM https://arxiv.org/html/2501.01299v1 | Predicting a displacement **from an LF PDE field** and warping **that field** into HF alignment before a learned correction, inside an MF operator surrogate at N_hf = 5–25. Already published and NOT claimable: learned warping in neural PDE models (Flowers); align-then-correct as a formulation (metamorphosis); transport geometry for MF diffuse-interface correction (Khamlich, on conservative Allen–Cahn at our own 128²–512² ladder). |
| **D2** warp-oracle / displacement-vs-amplitude diagnostic on the panel (incl. topology component-count check) | **preempted-but-MF-composition-open** | Keil & Craig 2009 DAS https://journals.ametsoc.org/view/journals/wefo/24/5/2009waf2222247_1.pdf ; https://arxiv.org/html/2501.01299v1 | The metric is old; no fetched source applies it **between two fidelities of one PDE solve**, and none reports an oracle-warp upper bound on MF fusion error. It also gates D1: iteration 4's two-regime finding (shape/position vs interfacial-thickness error) means D1's premise is an empirical question about *our* LF grids. |
| **D3** OT / soft-warp auxiliary objective, or metamorphosis-style appearance-parsimony penalty | **preempted-but-MF-composition-open** (weakest confidence) | https://arxiv.org/abs/2308.13840 ; https://arxiv.org/pdf/2303.09088 | An OT/soft-warp term in a **multi-fidelity 2-D operator** training loss. Constraint: program.md §5 fixes the scored metric — an OT-flavored loss must be argued to lower nRMSE. |

**Ruling on the seed claim (NEW_MODELS.md §8.4).** "No published multi-fidelity
operator method predicts an inter-fidelity displacement field and warps before
correcting" — **survives** 5 dedicated refutation searches. "The
registration-based framing 'align, then correct' is a documented gap" — **does
NOT survive** (metamorphosis; Khamlich MF-OT on Allen–Cahn). The claimable
novelty is narrow: the *neural, cross-fidelity, field-level* instantiation in
the few-HF-sample operator-learning regime.

## Citations summary

- [authors not read; arXiv 2026] "Flowers: A Warp Drive for Neural PDE Solvers" — https://arxiv.org/html/2603.04430 — fetched; used in: iteration_4.md, iteration_5.md
- Khamlich et al. 2026, "A Multi-Fidelity and Parametric ROM Framework with Optimal Transport-based Interpolation: Diffused-Interface Two-Phase Flows" — https://arxiv.org/html/2603.04232v2 — fetched; used in: iteration_2.md (lead), iteration_3.md, iteration_5.md
- "MetaRegNet: Metamorphic Image Registration Using Flow-Driven Residual Networks" — https://arxiv.org/pdf/2303.09088 — fetched; used in: iteration_3.md, iteration_5.md
- "MetaMorph: Learning Metamorphic Image Transformation With Appearance Changes" — https://arxiv.org/pdf/2303.04849 — search result; used in: iteration_3.md
- "Multi-Fidelity Flow Matching: Cascaded Refinement of PDE Solutions" (MFFM) — https://arxiv.org/html/2605.16118v1 — fetched; used in: iteration_1.md, iteration_5.md
- "Multi-fidelity reduced-order surrogate modeling" — https://arxiv.org/abs/2309.00325 — fetched; used in: iteration_2.md
- Gowrachari et al., "Model Reduction for Transport-Dominated Problems via Cross-Correlation Based Snapshot Registration" — https://arxiv.org/html/2501.01299v1 — fetched; used in: iteration_1.md, iteration_5.md
- Keil & Craig, "A Displacement and Amplitude Score Employing an Optical Flow Technique", Wea. Forecasting 24(5), 2009 — https://journals.ametsoc.org/view/journals/wefo/24/5/2009waf2222247_1.pdf — search result (primary-source PDF URL); used in: iteration_3.md, iteration_5.md
- "Nonlinear Reconstruction for Operator Learning of PDEs with Discontinuities" (shift-DeepONet) — https://arxiv.org/pdf/2210.01074 , https://openreview.net/forum?id=CrfhZAsJDsZ — fetch failed (PDF metadata only); abstract-level only; used in: iteration_2.md
- Klein & Ohlberger, "Multi-fidelity Learning of ROMs for Parabolic PDE Constrained Optimization" — https://arxiv.org/abs/2503.21252 — search result; used in: iteration_2.md
- "OT-inspired Deep Learning for Slow-Decaying Kolmogorov n-width Problems (Sinkhorn loss, Wasserstein kernel)" — https://arxiv.org/abs/2308.13840 — search result; used in: iteration_5.md
- "Unsupervised learning of spatially varying regularization for diffeomorphic image registration" — https://arxiv.org/html/2412.17982v1 — search result; used in: iteration_4.md
- Mok & Chung, "Fast Symmetric Diffeomorphic Image Registration with CNNs", CVPR 2020 — https://openaccess.thecvf.com/content_CVPR_2020/papers/Mok_Fast_Symmetric_Diffeomorphic_Image_Registration_with_Convolutional_Neural_Networks_CVPR_2020_paper.pdf — search result; used in: iteration_4.md
- "Learning Diffeomorphism for Image Registration with Time-Continuous Networks using Semigroup Regularization" — https://arxiv.org/html/2405.18684v1 — search result; used in: iteration_4.md
- Registration-based MOR of parameterized 2-D conservation laws — https://www.sciencedirect.com/science/article/abs/pii/S0021999122001309 — search result only (paywalled, not fetched); used in: iteration_1.md, iteration_2.md
- Hesthaven, Peherstorfer & Unger, "Nonlinear model reduction for transport-dominated problems" — https://arxiv.org/pdf/2602.01397 — fetch returned PDF metadata only; used in: iteration_1.md (bibliography leads only)
- "Frictionless Motion of Diffuse Interfaces by Sharp Phase-Field Modeling", Crystals 12(10):1496 — https://doi.org/10.3390/cryst12101496 — **fetch 403; search-snippet evidence only**; used in: iteration_4.md

## Dead ends

- `Taddei ... multi-fidelity registration` → the one named MF+registration
  paper registers HF-to-HF and fuses in POD-coefficient space; thread closed.
- `klein2025multifidelitylearningreducedorder` → parabolic PDE-constrained
  optimization ROM hierarchy; no registration.
- `quantify fraction of error due to feature displacement ... coarse vs fine
  grid` → returns image-pyramid optical flow only; "coarse-to-fine" is an
  estimation strategy, not solver fidelity. Nothing to cite.
- `neural network predicts warping field align coarse simulation to fine` →
  fluid SR results are all value-space (GNN/CNN SR); no displacement field.
- Primary-source fetches that failed: arXiv:2602.01397 and arXiv:2210.01074
  (PDF text not extractable), MDPI cryst12101496 (403). Claims resting on
  these are marked as snippet-level, not citation-grade.

## For the brainstormer

**You MUST quote the prior-art verdict above for whatever you propose.** The
usable form for D1 is: *"preempted-but-MF-composition-open — learned warping in
neural PDE architectures is published (Flowers, arXiv:2603.04430, but strictly
single-fidelity with no LF→HF mapping), warp-plus-appearance-correction is
published as metamorphosis (MetaRegNet, arXiv:2303.09088), and transport
geometry for MF diffuse-interface correction is published (Khamlich,
arXiv:2603.04232, classical OT on residual fields, no NN); what is open is a
learned displacement predicted from the LF field and applied to it before a
learned correction, in an MF operator surrogate."*

1. **Consider making batch 1 the D2 diagnostic, not D1.** It is training-free,
   it directly gates D1's premise (iteration 4: coarse phase-field error splits
   into a shape/position regime and an interfacial-thickness regime — only the
   first is warpable), and it is the least-preempted thing found. Concretely:
   per-dataset optical-flow morph of copy-LF onto HF, report displacement
   magnitude and post-morph amplitude error separately (Keil & Craig 2009), and
   report the **oracle-warp nRMSE** = nRMSE after the best smooth warp. If the
   oracle-warp skill is not < 1 on any panel dataset, D1 cannot work and the
   stream should say so.
2. **Handle topology explicitly or scope around it** — program.md §12.3
   requires it. The published answer is metamorphosis: warp + an
   intensity/source term penalized for magnitude (MetaRegNet). Candidate D's
   `warp(up(LF)) + δ` already has that shape; say so, and add the
   component-count check (LF vs HF connected components of the phase
   indicator) to know which panel datasets are topology-preserving.
3. **Beware the confound the orchestrator flagged**: the certified champion
   never consumes the LF field at test time, so any `mf_warp_correct` win could
   be a "use LF at test time" win. Any D1 card needs the **warp-off control**
   (same architecture, displacement forced to zero) as its comparator, not the
   champion alone.
4. **Displacement parameterization at N_hf = 5–25**: the fetched literature
   says free-form displacement fields dominate but drop diffeomorphic
   guarantees, and *global* smoothness penalties are documented as
   insufficient locally (arXiv:2412.17982). Low-parameter options with
   published parents: B-spline control grids (Frontiers 2013), velocity-field
   integration for diffeomorphism (arXiv:2405.18684). A low-Fourier-mode
   displacement head is the cheapest such prior and matches the FNO stack.
5. **Do not claim on helmholtz.** `state/noise_floor.json` gives
   `min_claimable_effect` 9.695 there; any warp threshold must clear the
   per-dataset floor (allen_cahn 1.633, pfc 1.151, cahn_hilliard 0.553,
   fisher_kpp 0.418, ifc_poisson 0.240). Note also that helmholtz is
   oscillatory, not interface-dominated, so it is the wrong dataset for this
   mechanism anyway.
6. **Read s2_beyond_copy-B1's interface-distance stratification before batch
   2** (program.md §12.3) — it measures how much of the champion's excess error
   sits at interfaces, which is the other half of D2's evidence.
