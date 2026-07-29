# Websearch Report — Stream `s4_hybrid_routing`, Batch 1

**Stream**: `s4_hybrid_routing`
**Batch**: 1
**Total iterations**: 4 (of a 5 cap)
**WebSearch calls**: 12 (3 per iteration)
**WebFetch calls**: 11 (8 successful, 3 failed: OpenReview verification page,
ANCHOR PDF over the 10 MB content cap, arXiv:2311.12902 PDF binary — the last
recovered via its abstract page)
**Cap hit**: no — stopped voluntarily at iteration 4; `ENOUGH` on field context
was declared at the top of iteration 4 (same core cluster returned by four
different phrasings) and the turn was spent entirely on §3.3 refutation.

**State caveat**: `state/anchors/` is empty and `state/noise_floor.json` does not
exist (batch 0 queued; `state/gates.md` says *"G3 — batch 0 (anchors + noise
floor): PENDING"*). This batch's card therefore has **no numeric anchor and no
noise floor** to threshold against — see the last bullet in "For the brainstormer".

## Search trace

### Turn 1 — map the three axes the stream can propose on
Terms (why): (1) `mixture of experts neural operator PDE routing gating Fourier
neural operator` — is MoE-over-operators itself already standard? (2) `frequency
band routing spectral operator attention operator hybrid PDE surrogate` — the
§12.4 "per-band gating" phrase; (3) `multi-fidelity mixture of experts operator
learning fidelity-aware routing gating low-fidelity high-fidelity` — the claimed
surviving novelty.
Key findings: MoE routing over operator experts inside Fourier-layer backbones is
mainstream (MoE-POT, 16+2 experts, layer-wise router-gating, NeurIPS 2025)
[cite: https://arxiv.org/abs/2510.25803]; **per-band routing over FNO/MNO/LNO
experts via a spectral-energy attention router with no multi-fidelity component**
[cite: https://arxiv.org/html/2604.07421]; **per-location HARD routing between a
spectral branch and a local/attention branch, zero-init gates, no multi-fidelity
input** [cite: https://arxiv.org/pdf/2605.12965]; nothing routing by fidelity.
→ `iteration_1.md`

### Turn 2 — is the built hybrid preempted, and does MF-MoE exist?
Terms (why): (1) sequential frozen-base + residual corrector — does D1 stand on
prior art? (2) MF neural-operator gating — direct assault on the novelty cell;
(3) band-split against the LF spectrum — the P4 mechanism.
Key findings: **spatially-variant gating over heterogeneous operator experts
weighted by each expert's localized performance is published, beating the best
single expert** [cite: https://arxiv.org/abs/2508.21249]; the OpenReview
"multi-fidelity mixture-of-expert framework" would not fetch (browser
verification) and is recorded as **uncitable**; band-split-against-LF-spectrum
returned no usable results (the search engine said so itself).
→ `iteration_2.md`

### Turn 3 — turn negatives into verdicts; recover the uncitable
Terms (why): (1) LF-conditioned spatially-varying MF gating; (2) an arXiv mirror
of the MF-MoE framework; (3) band cutoff from LF/HF coherence.
Key findings: **LGFNet treats LF CFD as a "low-frequency carrier" and learns the
nonlinear fidelity-gap delta with a local sliding-window + global self-attention
two-branch net — and has NO router** [cite: https://arxiv.org/abs/2603.29303];
the leading MF operator-learning paper **explicitly has no routing/gating/MoE
between operator architectures** [cite: https://arxiv.org/pdf/2507.07292]; no
arXiv mirror of the MF-MoE framework exists, so it stays uncitable. **Honesty
note recorded in-file:** my first (PDF) fetch of LGFNet over-fitted to my leading
prompt and claimed "spectral + attention experts with spatially-varying gating";
the verbatim abstract from the second fetch contradicted it and the first summary
was discarded.
→ `iteration_3.md`

### Turn 4 — §3.3 refutation of the three concrete directions
Terms (why): (1) Transolver+FNO hybrids (refute D1); (2) error-aware routing
between operator branches with identity init (refute D2); (3) copy-LF-band /
predict-HF-band (refute D3).
Key findings: **hierarchical FNO + convolution-residual + attention made
"complementary in the frequency domain", sequential, no gating, no
multi-fidelity** [cite: https://arxiv.org/abs/2311.12902]; third independent
negative on "router conditioned on a low-fidelity field"; third independent
negative on "band cutoff from LF/HF coherence".
→ `iteration_4.md`

## Prior-art verdict

| Candidate direction | Verdict | Citations (fetched) | What remains open |
|---|---|---|---|
| **D1** — panel-benchmark the built `fno_transolver_seq` (FNO-FiLM base + zero-init alpha-gated Transolver corrector on out-of-fold LF->HF residuals) | `preempted-but-MF-composition-open` | https://arxiv.org/html/2602.11197 (FNO smooth background + ViT high-contrast corrector); https://arxiv.org/abs/2311.12902 (hierarchical FNO + conv-residual + attention, frequency-complementary, sequential, no MF) | Neither source is multi-fidelity. Open: out-of-fold LF->HF residual targets under N_hf scarcity; the *real LF field* as corrector context; the least-squares + line-search `alpha` that makes the hybrid collapse **exactly** to the FNO when the correction is useless. **D1 is a measurement card — it should claim no novelty at all**, only that it measures whether the +30.6% oracle survives against copy-LF on sharp 2-D. |
| **D2** — LF-conditioned, spatially-resolved routing between an FNO expert and a Transolver expert, identity-safe init | `preempted-but-MF-composition-open` | https://arxiv.org/abs/2508.21249 (spatially-variant gating over heterogeneous operator experts by localized performance; beats best single expert; no no-harm guarantee); https://arxiv.org/pdf/2605.12965 (U-HNO per-location hard spectral-vs-local routing, zero-init gates, no MF); https://arxiv.org/abs/2510.25803 (MoE-POT, routing by equation family); https://arxiv.org/pdf/2507.07292 (MF operator learning **without** any routing/gating/MoE) | (i) A router whose **input is the LF field or the LF-HF disagreement** — three independent negative queries, and the leading MF operator-learning paper explicitly disclaims routing. (ii) An **identity-safe routing construction** that provably reduces to the per-dataset best expert — required by §12.4's "preserve `transolver_residual` on the 4 beyond-copy datasets it wins"; 2508.21249 offers no guarantee and U-HNO's zero-init only balances branches at init. |
| **D3** — per-band fidelity routing, `k_c` from LF/HF cross-spectral coherence | `preempted-but-MF-composition-open` **+ pre-falsified-lever flag** | https://arxiv.org/html/2604.07421 (SPAMoE: soft concentric frequency bands, learnable per-expert frequency preference, spectral-energy attention router, Top-k=2 over FNO/MNO/LNO; **no MF**); https://arxiv.org/abs/2311.12902; https://arxiv.org/abs/2603.29303 (LGFNet: LF as "low-frequency carrier" + fidelity-gap delta learning, **no router**) | No fetched source derives the cutoff from **LF/HF cross-spectral coherence** on the scarce HF pairs, nor hard-copies a real coarse-solve LF band while predicting only `k > k_c`. **BUT** program.md §5 pre-falsifies *"LF low-mode freezing (`mf_fno_spectral`): worst on sharp, catastrophic on lid-cavity"* — D3's hard-constraint form **is** that lever. A card must cite the falsification and state exactly what differs (data-derived per-dataset `k_c` + a learned low-band correction vs a fixed frozen low-mode block), or the immutables self-check should reject it. |

## Citations summary

All fetched in this loop; each appears in an iteration file with its URL.

- SPAMoE, "Spectrum-Aware Hybrid Operator Framework for Full-Waveform Inversion"
  — https://arxiv.org/html/2604.07421 — used in: iteration_1.md (fetched),
  iteration_4.md (D3 verdict)
- U-HNO, "A U-shaped Hybrid Neural Operator with Sparse-Point Adaptive Routing
  for Non-stationary PDE Dynamics" — https://arxiv.org/pdf/2605.12965 — used in:
  iteration_1.md (fetched), iteration_4.md (D2 verdict)
- MoE-POT, "Mixture-of-Experts Operator Transformer for Large-Scale PDE
  Pre-Training" — https://arxiv.org/abs/2510.25803 — used in: iteration_1.md
  (fetched), iteration_4.md (D2 verdict)
- "Hybrid operator learning of wave scattering maps in high-contrast media" —
  https://arxiv.org/html/2602.11197 — used in: iteration_1.md (search result),
  iteration_2.md, iteration_4.md (D1 verdict)
- "A Mixture of Experts Gating Network for Enhanced Surrogate Modeling in
  External Aerodynamics" — https://arxiv.org/abs/2508.21249 — used in:
  iteration_2.md (fetched), iteration_4.md (D2 verdict, nearest neighbor)
- LGFNet, Zhu/Xiang/Zhang/Wang, "Local-Global Fusion Network with Fidelity Gap
  Delta Learning for Multi-Source Aerodynamics" (31 Mar 2026) —
  https://arxiv.org/abs/2603.29303 — used in: iteration_3.md (abstract fetched
  verbatim; earlier PDF summary discarded), iteration_4.md (D3 verdict)
- "Discretization-independent multifidelity operator learning for PDEs" —
  https://arxiv.org/pdf/2507.07292 — used in: iteration_3.md (fetched),
  iteration_4.md (D2 verdict — the explicit "no routing/gating/MoE" statement)
- "Enhancing Solutions for Complex PDEs: Introducing Complementary Convolution
  and Equivariant Attention in Fourier Neural Operators" —
  https://arxiv.org/abs/2311.12902 — used in: iteration_4.md (abstract fetched),
  D1 and D3 verdicts

## Dead ends

- `band-split neural operator hard constrain low frequency to low-fidelity
  spectrum predict high wavenumber multi-fidelity` → returned speech-enhancement
  band-split RNN and generic MF papers; the search engine explicitly stated the
  mechanism "does not appear in these results".
- `cross-spectral coherence low-fidelity high-fidelity cutoff wavenumber ...` →
  spectral-bias analyses and MF transfer learning, nothing coherence-driven.
- `copy low-fidelity low frequency band predict only high frequency residual ...`
  → image/audio super-resolution frequency-separation work where "LF" is a blur
  of the input, not an independent coarse solve — structurally the wrong prior.
- **Uncitable leads (recorded so nobody cites them from memory):** the OpenReview
  "A MULTI-FIDELITY MIXTURE-OF-EXPERT FRAMEWORK" (browser verification blocked the
  fetch, no arXiv mirror); AGMF-Net adaptive gated multi-fidelity net with a
  deep-MoE gating sub-network (ScienceDirect, paywalled) — **if real, this is the
  closest published thing to "MoE gating inside an MF network", so any novelty
  claim of that exact shape is at risk**; SpecBoost (HF-residual boosting of an
  FNO); ANCHOR arXiv:2512.19643 (fetch exceeded the 10 MB cap); LCWF-MFS
  local-correlation-weighted MF fusion; and the AAAI claim that Transolver's slice
  attention *"may even hurt"* performance (a real risk to D1's premise, but
  synthesis-only and therefore not usable as a citation).

## For the brainstormer

The brainstormer MUST quote the verdict above for whatever it proposes.

1. **Lead with D1 as a pure measurement card, claiming zero novelty.** §12.4
   directs it, it is cheap, and its verdict is `preempted-but-MF-composition-open`
   — the composition is published (https://arxiv.org/html/2602.11197,
   https://arxiv.org/abs/2311.12902). The genuine question it answers is not "is
   this new" but "does the +30.6% FNO<->Transolver oracle survive when the target
   is copy-LF skill on sharp 2-D fields?" — which is exactly a §1-genuine
   experiment: informative whether it wins or loses.
2. **If proposing routing (D2), the ONLY defensible novelty is the router's
   input.** Spatially-variant gating over complementary operator experts by
   localized performance is published (https://arxiv.org/abs/2508.21249) and
   per-location hard spectral-vs-local routing is published
   (https://arxiv.org/pdf/2605.12965). Conditioning the router on the **LF field
   / LF-HF disagreement** is unpreempted by any fetched source, and
   https://arxiv.org/pdf/2507.07292 explicitly disclaims routing in MF operator
   learning. State that boundary in the card's `prior_art` block verbatim.
3. **Any routing proposal must carry an identity-safe construction**, not just
   zero-init. §12.4 requires preserving `transolver_residual` on the 4
   beyond-copy datasets it wins; the in-repo precedent is already built —
   `mf_field/akash/models/fno_transolver_seq/manifest.json` sets the scalar gate
   `alpha` by least-squares + a line search **containing 0**, so a useless
   correction reduces the hybrid *exactly* to the base. Neither published router
   found offers that. Reusing it is both safe and a real differentiator.
4. **Do not propose D3 in hard-constraint form without a §5 citation.**
   Hard-constraining the sub-`k_c` band to the LF spectrum **is** the
   pre-falsified "LF low-mode freezing" lever (`mf_fno_spectral`: worst on sharp,
   catastrophic on lid-cavity). Also note per-band routing over operator experts
   is already published (https://arxiv.org/html/2604.07421). If proposed, it must
   be a *soft, data-derived, learned-correction* variant with the falsification
   cited and the difference stated.
5. **A cross-cutting empirical hook worth using:** the fetched abstract of
   https://arxiv.org/abs/2311.12902 states the FNO *"approximates kernels
   primarily in a relatively low-frequency domain"*, and SPAMoE assigns sharp
   interfaces to a dedicated **local** operator expert. Both independently
   support the stream's premise that on the five sharp-2-D panel datasets the
   spectral expert is the wrong expert near interfaces — which is where routing
   should buy the most, and where the card's per-dataset skill table should be
   read.
6. **No anchor exists yet.** `state/anchors/` is empty and
   `state/noise_floor.json` is absent (batch 0 queued, G3 PENDING). Per
   program.md §4.5 a missing anchor is not a numeric threshold: write the
   falsification clause in terms the card can judge without one (e.g. a skill
   comparison against copy-LF = 1.0, which is fixed and needs no anchor), or
   express the threshold relative to the anchor to be certified. Do **not**
   invent a numeric noise floor.
