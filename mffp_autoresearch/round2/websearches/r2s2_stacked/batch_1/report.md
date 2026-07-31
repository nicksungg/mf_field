# Websearch Report — Stream `r2s2_stacked`, Batch 1

**Stream**: `r2s2_stacked` (lever) — condition → pseudo-LF → frozen round-1 corrector
**Batch**: 1
**Total iterations**: 4 (cap 5)
**WebSearch calls**: 12 (3 per iteration, cap respected)
**WebFetch calls**: 16 raw calls over 12 distinct sources (≤2 distinct sources fetched per
search term, as required; the extra calls are retries of the SAME source after a failed fetch
— oversize PDF, HTTP 403, or unparsable binary — on a different URL for that source)
**Cap hit**: NO — `ENOUGH` declared after iteration 3 (field context converged; iteration 4
spent entirely on §3.3 refutation searches)

## Search trace

### Turn 1 — does "emulate the coarse solve, then correct" exist in PDE-surrogate work?
Terms: (1) neural emulator of coarse solver + learned correction network; (2) parameters →
LF → HF two-stage neural operator; (3) generated-input distribution shift / exposure bias in
cascades. Chosen because the stream's B1 topology has two independently checkable halves
(the composition, and the shift), and the PDE vocabulary is where a drop-in precedent would
live.
- Key: every hit keeps a **real** coarse solve online — Learned Correction framing
  [cite: https://www.emergentmind.com/topics/neural-surrogate-modeling], NN multigrid
  corrector [cite: https://arxiv.org/pdf/2008.11520].
- Key: bifidelity nonintrusive ROM (Lu & Zhu 2019) uses **LF data as input features** and
  decouples only the **HF** simulation from the online stage
  [cite: https://arxiv.org/abs/1902.00148] — round-1 regime, not round-2.
- Key: PF-NO [cite: https://www.sciencedirect.com/science/article/abs/pii/S0141029625016098]
  and two-stage PI-FNO [cite: https://iopscience.iop.org/article/10.1088/1873-7005/ae79a2]
  are LF-pretrain / LF-input designs, not test-time stacks.
- Key: exposure-bias vocabulary is owned by diffusion/sequence models
  [cite: https://arxiv.org/html/2305.15583v5]. → `iteration_1.md`

### Turn 2 — can the coarse solver be *replaced* by an emulator, and is frozen-vs-end-to-end settled?
Terms: surrogate replaces coarse solver in hybrid pipelines; end-to-end vs frozen two-stage
PDE surrogate; coarse solution as intermediate bottleneck.
- Key: hybrids keep the solver in the loop (ANCHOR
  [cite: https://arxiv.org/pdf/2512.19643], surrogate/solver alternation
  [cite: https://arxiv.org/pdf/2604.20061], INC
  [cite: https://openreview.net/forum?id=s3Uk3lrfjy]).
- Key (verified): CALM-PDE §4.3 — end-to-end "more stable compared to a two-stage training
  procedure that first trains the encoder-decoder … then trains the processor"
  [cite: https://arxiv.org/abs/2505.12944].
- Key: PANIS uses an explicit coarse discretization as an information bottleneck
  [cite: https://arxiv.org/abs/2405.19019, verified via
  http://export.arxiv.org/api/query?search_query=ti:%22Physics-Aware%20Neural%20Implicit%20Solvers%22] — physics-explicit, which
  round 2 forbids at test. → `iteration_2.md`

### Turn 3 — refutation in the MF-statistics / operator-learning vocabulary
Terms: composite MF neural network (Meng & Karniadakis); NARGP prediction-time LF emulator;
MF-DeepONet with predicted LF fed to a residual subnet.
- **Kill shot**: MF-DeepONet with a **frozen LF subnet whose predicted output feeds a residual
  subnet** [cite: https://arxiv.org/abs/2310.00057].
- **Corroboration**: a 2025 MF-DeepONet paper differentiates itself from "residual-learning
  frameworks that sequentially combine low and high-fidelity predictions" and reports a
  frozen/full-tune/linear-probe ablation [cite: https://arxiv.org/html/2503.17941v1].
- Nearest MF-NN neighbour: composite LF-NN → two HF-NNs
  [cite: https://arxiv.org/abs/1903.00104]. → `iteration_3.md`

### Turn 4 — final refutation pass + verdicts
Terms: corrector fed surrogate-generated LF inputs (degradation quantified?); Howard et al.
MF-DeepONet composition; composed-vs-direct benchmark evidence.
- Key (verified): progressive MF learning freezes lower fidelity levels
  ("weights … for j<l remain fixed") but **still requires LF inputs at test**
  [cite: https://arxiv.org/html/2510.13762v1].
- Key: canonical composite MF-DeepONet incl. "the same physical model at two different
  resolutions" (our nested ladder) [cite: https://arxiv.org/abs/2204.09157].
- Key: MF-vs-single-fidelity benchmark verdict is problem-dependent — "no particular surrogate
  performs better on every test case"
  [cite: https://www.sciencedirect.com/science/article/abs/pii/S0045782524008314].
- **No source found** quantifying a real-LF-trained corrector's degradation on emulated LF
  inputs. → `iteration_4.md`

## Prior-art verdict

| Candidate direction | Verdict | Citations (fetched) | What remains open |
|---|---|---|---|
| **D1** condition → pseudo-LF emulator → **frozen** round-1 DC corrector, vs direct condition→HF | `preempted (cite)` | Xu et al. 2023 https://arxiv.org/abs/2310.00057 (frozen LF subnet, predicted LF → residual subnet); Yang et al. 2025 https://arxiv.org/html/2503.17941v1 (names the sequential residual class); Meng & Karniadakis 2020 https://arxiv.org/abs/1903.00104 (nearest MF-NN) | Reuse of a corrector **trained on real coarse solves** behind an emulator (deliberate train/test input mismatch); evaluation against **copy-LF skill** in a no-solver-at-test regime; N_hf ∈ {5, 400} sharp-field regime |
| **D2** frozen / fine-tuned / end-to-end arms decomposing **emulator error vs pseudo-LF distribution shift** | `preempted-but-MF-composition-open (cite)` | Yang et al. 2025 https://arxiv.org/html/2503.17941v1 (fine-tune vs full-tune vs linear probe); CALM-PDE https://arxiv.org/abs/2505.12944 (end-to-end > two-stage, §4.3 verbatim); Conti et al. 2025 https://arxiv.org/html/2510.13762v1 (frozen lower levels) | The **attribution**: no fetched source decomposes stacked error into emulator error + downstream distribution shift, nor uses the frozen−finetuned delta as the shift estimator, on field-valued PDEs |
| **D3** LF as an intermediate **supervised bottleneck** inside one condition→HF net | `preempted (cite)` | Meng & Karniadakis https://arxiv.org/abs/1903.00104; Howard et al. https://arxiv.org/abs/2204.09157; PANIS arXiv:2405.19019 (physics-explicit variant) | Only the empirical question: does the LF bottleneck help or hurt vs direct condition→HF on sharp few-HF fields under corrected denominators. Arm, not mechanism |

## Citations summary

- [Lu & Zhu 2019] "Bifidelity data-assisted neural networks in nonintrusive reduced-order modeling" — https://arxiv.org/abs/1902.00148 — used in: iteration_1 (term 2, abs fetched; PDF-fetch summary discarded as unsupported)
- [Margenberg et al.] "A neural network multigrid solver for the Navier-Stokes equations" — https://arxiv.org/pdf/2008.11520 — used in: iteration_1 (term 1, snippet-level; PDF unparsable)
- [PF-NO 2025] "Pretrain-finetune neural operator for multi-fidelity surrogate modeling of structural dynamic systems" — https://www.sciencedirect.com/science/article/abs/pii/S0141029625016098 — used in: iteration_1 (term 2, snippet-level)
- [Two-stage PI-FNO] super-resolution reconstruction of flow fields — https://iopscience.iop.org/article/10.1088/1873-7005/ae79a2 — used in: iteration_1 (term 2, snippet-level)
- [Ning et al. 2023] "Alleviating Exposure Bias in Diffusion Models…" — https://arxiv.org/html/2305.15583v5 — used in: iteration_1 (term 3)
- [INC] "An Indirect Neural Corrector for Auto-Regressive Hybrid PDE Solvers" — https://openreview.net/forum?id=s3Uk3lrfjy — used in: iteration_2 (term 1, snippet-level)
- [ANCHOR] "Error-Controlled Adaptive Numerical Correction for Neural Operator Time Marching" — https://arxiv.org/pdf/2512.19643 — used in: iteration_2 (term 1, snippet-level)
- [Hagnberger, Musekamp, Niepert 2025] "CALM-PDE" (NeurIPS 2025) — https://arxiv.org/abs/2505.12944 (§4.3 via https://arxiv.org/html/2505.12944v2) — used in: iteration_2 (term 2, VERIFIED)
- [Chatzopoulos & Koutsourelakis 2024] "Physics-Aware Neural Implicit Solvers for multiscale, parametric PDEs" arXiv:2405.19019 — http://export.arxiv.org/api/query?search_query=ti:%22Physics-Aware%20Neural%20Implicit%20Solvers%22 — used in: iteration_2 (term 3, VERIFIED via API)
- [Meng & Karniadakis 2020] "A composite neural network that learns from multi-fidelity data" JCP 401:109020 — https://arxiv.org/abs/1903.00104 — used in: iteration_3 (term 1, abs verified; inference dataflow unverified)
- [Perdikaris et al.] NARGP reference implementation — https://github.com/paraklas/NARGP — used in: iteration_3 (term 2, README fetched; prediction detail NOT confirmed)
- [Xu, Cao, Yuan, Meschke 2023] "A multi-fidelity deep operator network (DeepONet) for fusing simulation and monitoring data" — https://arxiv.org/abs/2310.00057 — used in: iteration_3 (term 3, VERIFIED abs)
- [Yang, Lee, Kang 2025] "Physics-Guided Multi-Fidelity DeepONet for Data-Efficient Flow Field Prediction" — https://arxiv.org/html/2503.17941v1 — used in: iteration_3 (term 3, VERIFIED HTML)
- [Howard, Perego, Karniadakis, Stinis 2023] "Multifidelity Deep Operator Networks" JCP — https://arxiv.org/abs/2204.09157 — used in: iteration_4 (term 2, abs verified; composition detail unverified)
- [Conti, Guo, Frangi, Manzoni 2025] "Progressive multi-fidelity learning for physical system predictions" — https://arxiv.org/html/2510.13762v1 — used in: iteration_4 (term 1, VERIFIED HTML)
- [MF functional-output survey 2024] "A survey on multi-fidelity surrogates for simulators with functional outputs" — https://www.sciencedirect.com/science/article/abs/pii/S0045782524008314 (arXiv PDF https://arxiv.org/pdf/2408.17075) — used in: iteration_4 (term 3, snippet-level; PDF unparsable, ScienceDirect 403)
- In-repo prior websearch (not re-derived): `docs/reports/MF_Leaderboard_Beaters_2026_Report.md` [LF-13] correlation-based MF neural emulators https://arxiv.org/abs/2512.02868; `docs/reports/MF_Sharp_HighFreq_Report.md` line 101 (zoo families already run on "model-generated LF only")

## Dead ends

- `distribution shift cascaded surrogate … exposure bias` → returns diffusion-model exposure
  bias and unrelated cascades (classifier→regressor); the PDE-surrogate community does not use
  this vocabulary for stacked-input shift.
- ScienceDirect URLs → HTTP 403 under WebFetch; use arXiv mirrors or treat as snippet-level.
- Large arXiv **PDF** fetches (1903.00104, 2008.11520, 2408.17075) → binary/unparsable; always
  prefer `/abs/` or `/html/`.
- One PDF fetch (1902.00148) produced a **fabricated-sounding summary contradicted by the
  paper's own abstract** — discarded; lesson recorded in iteration_1.

## For the brainstormer

1. **You may not claim a new mechanism for the stack.** Quote verbatim: *"D1 —
   `preempted (cite)`: Xu, Cao, Yuan, Meschke (2023), https://arxiv.org/abs/2310.00057 —
   frozen LF DeepONet subnet whose predicted LF output feeds a residual subnet; Yang et al.
   (2025), https://arxiv.org/html/2503.17941v1 — names 'residual-learning frameworks that
   sequentially combine low and high-fidelity predictions' as an existing class."* Frame B1 as
   **measuring a known composition in an unmeasured regime**.
2. **Put the stream's claim on D2, not D1.** The open contribution is the *attribution*:
   decompose stacked error into (emulator error) + (distribution shift on a corrector trained
   on real LF), using the **frozen − fine-tuned** delta as the shift estimator. Quote
   *"D2 — `preempted-but-MF-composition-open`"* and state that no fetched source performs this
   decomposition. Design the arms so the decomposition is identifiable (an oracle arm that
   feeds the frozen corrector the **real train-side LF** is the natural upper bound; it is
   train-side only, so it does not violate §5.9's stripped-test rule — confirm with the
   builder/reviewer before relying on it).
3. **Expect end-to-end ≥ frozen, and pre-register that expectation.** CALM-PDE
   (https://arxiv.org/abs/2505.12944, §4.3) found end-to-end more stable than two-stage;
   Yang et al. found partial fine-tuning beat both full-tuning and linear probing. If the
   frozen arm wins here, that is itself a reportable inversion — say so in the falsification
   clause.
4. **Restate `dc_cleaned`'s 0.1233 under the corrected denominators before using it**
   (program.md §3, §12.2), and carry the **wrap-seam caveat** (deep-bulk ratio 0.908 on pfc)
   plus the **BC-match rule** (training-free audit:
   `tools/spectral_prestage_bc_audit.py`) — the cleaning stage's eligibility per dataset must
   be decided before training, not after.
5. **Beat the floors first.** Anchor = best-floor panel geomean **23.06**
   (`state/anchors/r2s2_stacked.json`); per-dataset floors helmholtz 3.344 (zero) / pfc 59.81
   (mean) / allen_cahn 269.20 (NN) / fisher_kpp 11.99 (mean) / cahn_hilliard 23.18 (NN) /
   ifc_poisson 10.05 (NN). Floor arms are mandatory on the card (§2.2); the helmholtz
   zero-floor column and the pfc denominator caveat must appear on any claim.
6. **Watch the nested-ladder degeneracy** (r1 report §6): the pseudo-LF target is a
   band-limited version of the HF target on the same conditions, so the emulator and a direct
   condition→HF model may be learning nearly the same function — state explicitly what the LF
   bottleneck is supposed to add (spectral truncation structure / easier target), because if
   it adds nothing the stack cannot beat r2s1 by construction (§12.2's falsification framing).
