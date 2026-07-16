# Beating the MFFP Leaderboard: Refiner Mechanism + Hybrid Backbone

**A 2026-07-15 strategy memo · mf_field / MFFP project**

**Revision notes.**

- rev. 9 — Candidate C: from-Kim-to-neural-operator port table (§7.4) + Kim full JFM citation and primary-source-confirmed top-hat term; Candidate B: "why not just raise the FNO mode count" localization-vs-frequency-ceiling contrast (§6.3)
- rev. 8 — Candidate A verdict: engineering-strong but the least-novel of the four; prior-art scan (flow-matching MF residual / CorrDiff / PDE-Refiner) + perception–distortion caveat + required baselines, §5.5
- rev. 7 — Candidate B prior-art on Fourier+wavelet hybrids + tempered novelty claim, §6.5
- rev. 6 — Candidate C prior-art fact-check + required baselines, §7.4
- rev. 5 — Candidate D: warp-then-correct / registration-based fusion, §8, plus the analytic interface / level-set alternative, §6.3
- rev. 4 — Candidate C: cycle-consistent invertible-degradation fusion, §7
- rev. 3 — WNO performance evidence base, §6.4

**Scope.**
Candidate model families that could beat the current MFFP leaderboard.
Four complementary levers headline this memo, each attacking a different bottleneck:

- **Loss** — a deterministic diffusion *refiner* (Candidate A, §5), which fixes the blur.
- **Representation** — an *FNO↔WNO hybrid backbone* (Candidate B, §6), which fixes the spectral-mode truncation.
- **Data** (added rev. 4) — Candidate C (§7) turns the abundant LF surplus into a cycle-consistency constraint on the scarce-HF inverse.
- **Geometry** (added rev. 5) — Candidate D (§8) predicts a smooth displacement field that transports the LF field into HF alignment before any residual is added, so a mispositioned sharp feature is *moved* rather than re-synthesized.

**Companion to** `MF_Leaderboard_Beaters_2026_Report.md` (the 2026-07-13 literature scan, proposals N1–N7).
This memo develops the generative-residual and dual-basis-backbone directions in depth and ties them to the exact repo scaffolding they would reuse.

**Provenance and honesty note.**
Repo facts were verified on 2026-07-15 by reading `factory.md`, `model/README.md`, `models/README.md`, `models/_common/fire_core.py`, and `eval/MODEL_CONTRACT.md`.
The odds, rankings impact, and where-it-wins claims are *calibrated judgment*, not measured results — nothing here has been run yet.
External anchors:

- PDE-Refiner (Lippe et al., NeurIPS 2023)
- FNO (Li et al. 2021)
- WNO (Tripura & Chakraborty 2022, arXiv:2205.02191)
- Multiwavelet operator (Gupta et al., NeurIPS 2021)

**Additional sources.**

- The WNO evidence base (§6.4) further draws on WLNO (arXiv:2605.24658), U-WNO (arXiv:2408.08190), PIWNO (arXiv:2302.05925), FWNO (arXiv:2405.06910), and WDNO (arXiv:2412.04833).
- The iterative-refinement thread also connects to the IRNO anchor from the 2026-07-13 report.
- The Candidate A prior-art scan (§5.5) draws on the flow-matching residual-operator line — Bhola & Duraisamy (arXiv:2512.12749) and MFFM (arXiv:2605.16118) — plus CorrDiff (arXiv:2309.15214), the coarse-to-fine flow-diffusion model (arXiv:2504.04375), PGDM (arXiv:2404.05009), S-DeepONet+video-diffusion residual refinement (arXiv:2507.06133), and SR3 (arXiv:2104.07636).

**Verification status.**

- The WNO performance claims in §6.4 were web-verified on 2026-07-15 against the WLNO arXiv HTML (primary) and the MWT NeurIPS proceedings, plus one secondary aggregate (EmergentMind).
- The canonical WNO paper's own error tables were not line-read, so its per-benchmark margins remain unverified.
- Any other claim drawn from these external papers should be re-verified against the primary source before this memo is promoted to a formal report.

**Per-candidate provenance.**

- **Candidate A** (§5) — prior-art-scanned on 2026-07-15 via web search, primary-source abstracts, and a Codex↔Claude adversarial pass.
  The refiner-on-the-LF→HF-residual mechanism is **prior art, not novel**, and the most crowded of the four candidates — Bhola & Duraisamy (arXiv:2512.12749) is a near-exact FiLM-conditioned-FNO residual-flow relative — so the surviving novelty is the FIRE-conditioned MF application, not the refiner block (see §5.5).
- **Candidate B** (§6) — the FNO↔WNO blend was prior-art-scanned on 2026-07-15 via web search plus primary/secondary sources.
  The gated dual-branch mechanism is **prior art, not novel** — WLNO (arXiv:2605.24658) is the near-exact structural precedent, differing only in using a Laplace rather than a Fourier global branch — so the surviving novelty is the multi-fidelity application, not the block (see §6.5).
- **Candidate C** (§7) — originates from an in-session brainstorm over `IDEA.md`.
  Its prior art was fact-checked against arXiv / journal primary sources in a Codex↔Claude adversarial pass on 2026-07-15, and the mechanism is largely **prior art, not novel** (Kim et al. 2021 is a near-exact relative) — see §7.4.
- **Candidate D** (§8) and the analytic interface / level-set alternative (§6.3) — carried forward from the P-proposals of `MF_Sharp_HighFreq_Report.md` (2026-07-02).
  Their external anchors are cited there and reproduced here unverified — re-verify against the primary sources before promotion.

---

## 1. Bottom line

Two independent bottlenecks cap the leaderboard, and each has its own lever:

- The **loss / inference bottleneck** — MSE regression converges to the conditional mean, which *blurs* sharp fields.
  The lever is a **deterministic diffusion refiner** on the residual.
- The **representation bottleneck** — FNO's spectral-mode truncation cannot represent high-frequency energy in the first place.
  The lever is a **non-truncating or hybrid backbone**, best realized as an **FNO↔WNO dual-basis operator**.

These are orthogonal, so the strongest single bet is to attack **both at once**: a refiner mechanism on a hybrid backbone, aimed at the high-frequency datasets.

Two further orthogonal levers stack onto that core:

- **Candidate C** (§7) attacks the *data* side rather than the loss or the representation: it converts the abundant LF surplus into a cycle-consistency constraint on the scarce-HF inverse, and composes with both levers above.
- **Candidate D** (§8) attacks the *geometry* side: when a sharp feature sits at a slightly different position in LF than in HF, additive correction must erase it in one place and redraw it in another (a blur MSE cannot avoid), so Candidate D predicts a smooth displacement field and *transports* the LF field into HF alignment before any residual is added.
  It too composes with the levers above.

The `composite_nRMSE` scoring (geomean of the *best model per dataset*) rewards regime specialists, so a sharp-datasets specialist does not need to win everywhere — it only needs to win the sharp datasets, and the composite banks it automatically.

---

## 2. Both the fusion mechanism and the backbone are free levers

The project's goal (`factory.md` line 4) is to beat the paper nRMSE numbers on as many of the 17 datasets as possible — the goal is the *numbers*, with no architectural constraint.
New families must only be implemented *from scratch from the source paper(s)* (`factory.md` line 15), and the mutable surface is `models/**`, where each family vendors its own `model.py` backbone.

"Hold the FNO backbone roughly constant" appears only in `model/README.md` as a **methodological convention** for clean mechanism attribution — it is **not** a contract rule.
The leaderboard already contains six non-FNO backbones (Transolver ×2, MFRNP neural process, d_mfd Bayesian, mf_deeponet, v9_baseline Transformer), which proves backbone changes are in-bounds.

The practical consequence: the backbone is a first-class design axis, not a fixed surface.
The only guardrail that comes with that freedom is the from-scratch rule — a new backbone (WNO, multiwavelet, U-Net/UNO, hybrid) needs its own `models/<family>/INSPIRATION.md` citing the source paper(s), not a copy of `references/v9_baseline/`.

---

## 3. The framing correction: fusion and backbone, and the *right* FNO/WNO blend

Backbone choice was earlier treated as "off-axis" only because of the attribution convention above; with the convention relaxed, backbone is a legitimate lever.

This also corrects the original motivating chain (WNO → "blend FNO and WNO" → Transolver):

- **Transolver was never the blend.** It is a transformer operator — neither Fourier nor wavelet — so "blend FNO and WNO, therefore Transolver" is a non-sequitur.
  Its underperformance is principled: attention operators are data-hungry and the high-fidelity regime is data-scarce by construction (`transolver_residual` med relL2 0.116, `transolver_attention_fusion` 0.322 — bottom third).
- **The actual blend is a dual-basis operator.** An FNO↔WNO hybrid *is* the "combine them" idea done correctly, and §6 develops it.

---

## 4. The metric reality that governs where each lever pays off

The leaderboard metric is per-sample relative-L2 (nRMSE); what it rewards is the crux.

- **MSE regression is mathematically a blur.** An L2-trained network's optimal output is the conditional mean `E[HF | inputs]`; when a sharp feature's position is uncertain, the mean of all plausible sharp fields is smeared.
  The blur is in the loss, not the capacity.
- **FNO compounds it, and the residual is high-frequency.** FNOs keep only low Fourier modes, and networks learn low frequencies first (spectral bias).
  Since `HF = mu_LF + delta` with LF smooth/coarse, the residual `delta` is almost pure high-frequency structure — exactly what MSE and mode-truncation lose.
- **The metric under-weights high frequencies on smooth PDEs, and rewards them on sharp ones.** Relative-L2 is dominated by high-energy modes.
  On smooth PDEs (heat, Poisson) energy sits at low modes, so recovering detail barely moves nRMSE.
  On high-frequency PDEs a large share of the energy is *in* the high modes, so recovering them is a first-order nRMSE win.

This one principle explains both the optimism and the skepticism throughout this memo: each lever's value tracks where a dataset's energy sits.

---

## 5. Candidate A — deterministic diffusion refiner (fixes the loss bottleneck)

### 5.1 Why it fits the existing scaffold

`models/_common/fire_core.py:226` (`fire_run`) already fits an LF model → produces summary channels `aug = [mu, sigma, q10, q50, q90] / s_lf` → computes `residual = Y_hf − mu_hf` → trains a **deterministic** `FNO2dAug` with MSE → outputs `HF = mu + delta`.
The refiner replaces only the MSE residual head with a denoising head, conditioned on the same `(X, aug)` channels; the residual is even pre-scaled by `res_scaler` (the bounded target a denoiser wants).
Synergy: the LF `sigma` field is large exactly where the LF→HF gap is sharp, so conditioning the refiner on FIRE's distributional channels tells it *where* to work hardest.

### 5.2 How it works, concretely

At a glance:

- One network `f`, conditioned on `(X_cond, aug)` plus two new inputs — the current noisy residual field and a step/noise-level embedding.
- K ≈ 3–8 noise levels.
- Inference starts from a prediction, not pure noise.

Training (one network, all steps mixed):

```
# HF batch: cond = (X, aug), target delta = (Y_hf - mu) / res_scaler
k ~ Uniform{0..K}
if k == 0:
    loss = MSE( f(x=0, cond, step=0), delta )          # base one-shot prediction
else:
    eps     = randn_like(delta)
    sigma_k = geometric schedule, large -> sigma_min as k grows
    x_k     = delta + sigma_k * eps                     # noise the ground-truth residual
    loss    = MSE( f(x_k, cond, step=k), eps )          # denoising: predict the noise
```

Inference (deterministic, K+1 forward passes):

```
u = f(x=0, cond, step=0)                                # initial residual estimate (~ today's head)
for k in 1..K (sigma_k decreasing to sigma_min):
    x = u + sigma_k * eps                               # ODE/DDIM update -> no fresh randomness
    u = x - sigma_k * f(x, cond, step=k)                # subtract predicted noise -> refined
delta = u * res_scaler
HF    = mu + delta
```

**Why the denoising objective helps (the mechanism).**
The gain is not extra capacity — it is a fix to the *loss weighting*:

- **The failure.** Plain MSE on `delta` decomposes over Fourier modes into a sum of per-mode squared errors dominated by the high-amplitude modes: a mode of true amplitude `a` contributes only ~`a²`, so a low-amplitude high-frequency mode supplies almost no gradient and, under spectral bias, is learned last or never.
  That starvation *is* the blur, and adding capacity does not help — the loss never asks for those modes.
- **The fix.** i.i.d. Gaussian noise has a flat spectrum, so `x_k = delta + sigma_k · eps` injects amplitude `sigma_k` into *every* mode, and a mode is recoverable only when its signal amplitude is `≳ sigma_k` — below that it is buried and the network cannot denoise it without actually modeling it.
- **The sweep.** Taking `sigma_k` from large down to `sigma_min` walks that visibility threshold down the amplitude ladder, handing each band its own turn to dominate the loss — PDE-Refiner's "implicit spectral data augmentation," where one clean sample noised at K levels becomes K training signals that each stress a different band.
- **Why it beats iterating MSE** (the `fno_multilevel` / `fno_autoregressive` cousins of §5.3): iterated MSE keeps the same amplitude²-weighting on every pass, so the small modes stay starved no matter how many passes are spent, whereas the denoising steps re-weight the loss per step via the noise scale — the win is the reweighting, not the extra forward passes.

Two honest bounds on the argument:

- **Scope** (developed in §5.5): this un-starves *deterministic* low-amplitude modes — real signal the MSE head underfit — so it lowers nRMSE only where that detail is predictable and the dataset's energy sits in high modes (§4); where the high-frequency content is genuinely aleatoric there is nothing to recover, and a *sampled* output would instead raise nRMSE.
- **Evidence.** The direct evidence (PDE-Refiner) is for temporal rollout rather than the LF→HF residual, so for Candidate A this is a grounded argument-by-analogy that E1 (§12) is meant to confirm.

The deterministic (probability-flow / DDIM) update gives one sharp point estimate with no sampling variance, which is why it is nRMSE-safe (but see §5.5 on making the inference loop genuinely deterministic).
Cost is K+1 forward passes (~4–9), inside the ≤30-min smoke budget; the only new knobs are `sigma_min` and `K`.

### 5.3 On the roadmap and unbuilt

None of the 30 families use diffusion/denoising/score-matching (verified by grep across `models/`, `references/`, `papers_summary.csv`).
The only occurrence is one roadmap bullet in `models/README.md` ("Latent diffusion / score-matching priors over the residual field").
The closest implemented cousins (`fno_multilevel`, `fno_autoregressive`, `fno_mf_stack`, `transolver_attention_fusion`) all iterate a *deterministic* MSE correction and inherit the same blur.
None use a denoising objective.

### 5.4 The ceiling it cannot fix alone

The refiner fixes the loss and inference procedure, not the representation.
If a dataset's high-frequency energy sits above the FNO's retained modes (`modes_cap`) or above the Nyquist limit of `fire_core`'s capped working grid (256), no objective can recover it.
Removing that ceiling is Candidate B's job.

### 5.5 Is it a good idea? Verdict, prior art, and required baselines

**"Good idea" splits into two questions with different answers.**
As an *engineering bet to move the leaderboard*, Candidate A is the strongest first build target of the four, and this section does not walk that back.
As a *novel mechanism*, it is the **weakest** of the four: the refiner-on-the-LF→HF-residual idea — including the deterministic-inference choice §5.2 sells as its nRMSE-safety insight — is already published, some of it within the last two months.
The honest framing therefore mirrors Candidates B (§6.5) and C (§7.4): **prior art, not invention** — build it for the score, cite the precedents, and do not claim the block.

**Why it is still the right first bet.**
The engineering case in §5.1–5.3 stands: it targets a real, well-understood failure (spectral bias underfitting low-amplitude high modes), it is a minimal residual-head swap on `fire_core` with a bounded downside, it is cheap (K+1 passes), and it composes with B/C/D.
The odds in §11 are unchanged.

**But the mechanism is prior art, and more crowded than B or C.**
Refiner-on-a-residual is one of the most heavily worked directions in 2023–2026 scientific ML.
Candidate A is specifically a *diffusion* (denoising / noise-prediction) refiner (§5.2), but the anchors below span both diffusion and its close cousin flow matching, because for a novelty assessment they are the **same mechanism class**: a diffusion model integrated deterministically is its probability-flow ODE, and that ODE is exactly what a flow-matching model learns directly — so §5.2's own "deterministic, no fresh randomness" variant sits on the diffusion↔flow-matching boundary.
The genuinely-diffusion anchors alone (CorrDiff, PDE-Refiner, PGDM, WDNO, SR3) already establish prior art; the flow-matching anchors (Bhola & Duraisamy, MFFM) are simply the *closest* on backbone and scarce-HF-PDE setting.
Near-exact anchors, ranked by proximity:

- **Bhola & Duraisamy, "Flow Matching Operators for Residual-Augmented Probabilistic Learning of PDEs"** (arXiv:2512.12749, Dec 2025) — *the closest match.*
  A conditional neural operator that learns **flow-matching residual corrections mapping low-fidelity approximations onto the high-fidelity solution manifold**, on a **FiLM-conditioned Fourier neural operator**, explicitly "rather than learning the full solution mapping from scratch," validated "even when trained on limited high-fidelity data" (advection, Burgers, Darcy).
  That is Candidate A's recipe almost line for line — generative residual head, FiLM-conditioned FNO, scarce-HF MF regime — with flow matching in place of denoising (the same generative class; a flow-matching ODE *is* the deterministic sampler §5.2 wants) and plain LF conditioning in place of FIRE's `[mu, sigma, q10, q50, q90]`.
- **Chen, Liu, Tang & Li, "Multi-Fidelity Flow Matching: Cascaded Refinement of PDE Solutions" (MFFM)** (arXiv:2605.16118, May 2026) — *the deterministic-inference precedent.*
  LF-conditioned cascade residual refinement across fidelities, arguing (as §5 does) that "conditioning makes the residual refinement problem substantially easier than unconditional field generation," with inference by a **deterministic one-step rollout** — so the nRMSE-safe determinism §5.2 presents as its own insight is already the published operating point.
  Eight benchmarks (PDEBench, The Well, FNO Navier–Stokes).
- **Li et al., "From Coarse to Fine: A Physics-Informed Self-Guided Flow Diffusion Model"** (arXiv:2504.04375, 2025) — solver-generated LF→HF CFD reconstruction by residual correction; likely closer to the PDE/MF framing than the weather-downscaling anchor below.
- **Mardani et al., NVIDIA CorrDiff — "Residual Corrective Diffusion Modeling for Km-scale Atmospheric Downscaling"** (arXiv:2309.15214; *Comms. Earth & Environment* 6, 2025) — the **regression-mean-UNet + diffusion-residual-corrector** block stated almost verbatim, for coarse→fine (25 km→2 km) downscaling.
  Near-exact on the *block*, but not the *setting*: it is stochastic and distributionally trained (CRPS), not a scarce-HF PDE benchmark with a point-estimate nRMSE target, so it damages the mechanism claim without fully occupying Candidate A's niche.
- **PDE-Refiner** (Lippe et al., NeurIPS 2023) — the anchor already cited; multi-step denoising refinement of PDE fields, but single-fidelity *temporal rollout*, not an LF→HF residual.
- Background and adjacent: **PGDM** (arXiv:2404.05009), **S-DeepONet + video-diffusion residual refinement** (arXiv:2507.06133), **WDNO** (arXiv:2412.04833, §6.4), and generic conditional-diffusion super-resolution **SR3** (Saharia et al., arXiv:2104.07636).

**What survives as novel (thin).**
Strip out what is published and little remains:

- the **FIRE-distribution-channel conditioning** — feeding the refiner `[mu, sigma, q10, q50, q90]` so the LF `sigma` field points it at the sharp gaps (§5.1); and
- the **`composite_nRMSE` specialist framing** (§10).

Both are real but incremental — a conditioning signal and an evaluation framing, not a mechanism.
The deterministic-for-nRMSE idea, which reads as the memo's cleverest move, is *not* in the surviving set — MFFM already runs deterministic inference for the same reason.
Net verdict, the same shape as B and C: **recombination, not invention**; position Candidate A as engineering/consolidation.

**The load-bearing technical caveat §4 currently understates.**
§4 motivates the blur as *aleatoric* — "the mean of all plausible sharp fields is smeared" — but that framing and the nRMSE-safety claim are in tension:

- **If the blur is truly aleatoric,** the distortion–perception tradeoff (Blau & Michaeli 2018; Freirich et al., NeurIPS 2021) says the posterior **mean** — the blurry field — is very nearly the nRMSE-minimizing estimate, so a sharper refiner output would *raise* nRMSE, the opposite of the intent.
  (The "unique minimizer" statement is exactly true only for squared L2; the scored metric is per-sample *relative*-L2, whose Bayes-optimal estimator is not strictly `E[HF | inputs]`, so read this as a strong heuristic, not a clean theorem — the direction survives regardless.)
- **The refiner wins only in the *other* regime:** where the missing detail is **deterministic but underfit** — predictable from the LF and conditioning, yet dropped by a one-shot MSE head because low-amplitude high modes barely move the loss.
  That is PDE-Refiner's actual mechanism, and it improves *accuracy* because the recovered content is the true signal, not a plausible hallucination.

The operative rule and its consequence:

- Candidate A helps only when the baseline is **not already the relative-L2-optimal estimator** (spectral bias, capacity, conditioning), and is a *liability* where the detail is genuinely aleatoric and the baseline already estimates the mean well.
- So the refiner must target the posterior **mean**, not a sample, and **E0 (§12) must be extended to classify each dataset as deterministic-underfit vs. aleatoric in the high modes** (residual-energy spectrum vs. a conditional-variance estimate) before Candidate A is pointed at it.

**A premise worth auditing.**
§4 and §5.4 assume the LF→HF residual `delta` is "near-pure high-frequency."
That is often only partly true: LF→HF residuals also carry phase shifts, amplitude bias, boundary-layer displacement, and coherent *low*-frequency calibration terms.
To the extent they do, the high-frequency-only motivation for the refiner is overstated, and the displacement component is precisely what Candidate D (§8) exists to *move* rather than re-synthesize — another reason A is incomplete alone.

**Mechanism-precision fix (a real inconsistency in §5.2).**
§5.2 claims a "deterministic … update — no fresh randomness — no sampling variance," but the pseudo-code writes `x = u + sigma_k * eps` with fresh `eps = randn_like(...)` at every step — stochastic, contradicting the prose.
The pseudo-code faithfully copies PDE-Refiner, whose refinement *does* inject fresh noise down to a `sigma_min` floor; the prose describes a different, deterministic method.
Pick one explicitly:

1. a **true deterministic ODE / probability-flow integrator** (flow-matching-style, as MFFM does — no injected `eps`) for a single nRMSE-safe point estimate; or
2. **PDE-Refiner-style stochastic sampling**, in which case the nRMSE-optimal output is the **Monte-Carlo sample mean**, not a single sharp draw (and even that is optimal only if the generator is calibrated to the true posterior).

The written loop is neither; fix it to match the choice.

**Required baselines (because the mechanism is prior art).**
A Candidate A build must beat three direct baselines, not just its leaderboard parent:

1. the **plain MSE residual head** (today's `fno_fire_distcond` head) — to prove the generative head earns its keep;
2. a **CorrDiff-style regression-mean + diffusion-residual** refiner with plain LF conditioning — to prove the FIRE-channel conditioning is the delta, not the diffusion head alone; and
3. a **deterministic flow-matching-operator MF residual** (Bhola & Duraisamy / MFFM) — to prove the diffusion-refiner choice beats the published deterministic-flow alternative inside this pipeline.

`INSPIRATION.md` must cite the MF-specific anchors above (Bhola & Duraisamy 2025; Chen et al. 2026; Li et al. 2025; Mardani et al. 2023/2025; Lippe et al. 2023), framing the contribution as the FIRE-conditioned MF application under `composite_nRMSE`, not the refiner block.

---

## 6. Candidate B — FNO↔WNO hybrid backbone (fixes the representation bottleneck)

### 6.1 Why combine, not replace

FNO and WNO sit on opposite ends of the Fourier–wavelet (Heisenberg) tradeoff, and each is strong exactly where the other is weak:

|           | FNO (global Fourier)                                              | WNO (localized wavelet)                                                                                                  |
| --------- | ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Strong at | Smooth, global, periodic/stationary content; low modes, efficient | Sharp,*local*, transient/non-stationary features; multiresolution; no low-pass truncation                              |
| Weak at   | Sharp local detail (mode truncation discards it)                  | Global smooth/periodic structure; boundary artifacts; wavelet-family/level are finicky; weaker discretization-invariance |

A *pure* WNO would likely lose on smooth datasets (heat/Poisson) even while winning on sharp ones, so replacing FNO is the wrong move.
Combining lets one backbone cover both regimes — FNO for the smooth global structure, WNO for the sharp local detail.

### 6.2 How to combine (design space + recommendation)

- **A. Parallel dual-branch block** — each layer runs both an FNO spectral conv and a WNO wavelet conv on the same input, then merges.
  Tightest integration; ~2× operator compute per block.
- **B. Learned per-location gate (Mixture-of-Operators)** — a gate decides per pixel/channel how much to route through FNO vs WNO.
  Adaptive to local field character.
- **C. Explicit frequency split** — FNO on the low-pass component, WNO on the high-pass residual, recombine.
  Interpretable, but the split point is a hardcoded hyperparameter and can sever cross-scale coupling.
- **D. Sequential/interleaved stacking** — simplest, but no per-location basis choice.
  Weakest.

**Recommendation: A + B — a dual-branch operator block with a learned spatial gate.**
The gate learns to lean Fourier in smooth regions and wavelet at sharp features, directly exploiting the complementarity, and it degrades gracefully to FNO-like behavior on smooth datasets so the downside there is bounded.
The gated dual-branch *mechanism* is **not novel** — it is essentially WLNO's published design with a Fourier branch in place of its Laplace branch (see §6.5) — so the contribution to claim is the *multi-fidelity application*, not the block itself.
Implemented from scratch citing FNO (Li et al. 2021) + WNO (Tripura & Chakraborty 2022) in `INSPIRATION.md`.
The Fourier+wavelet prior art (§6.5) should be acknowledged there rather than claimed as new.

### 6.3 Alternatives on the representation axis

**Why not just raise the FNO mode count (the natural first objection)?**
Because more modes raises the frequency *ceiling* but does nothing about spatial *localization* — and sharp features are a localization problem, not only a high-frequency one.
Concretely:

- **Local features are dense in *any* Fourier basis.** A shock, front, or interface is localized in space, and anything spatially localized takes many high-wavenumber global sinusoids that cancel everywhere except at the feature — no mode count avoids this.
- **Gibbs ringing never goes away.** Near a discontinuity those sinusoids leave overshoot that more modes *narrow but never remove*.
  A wavelet basis is localized in space *and* frequency (the Heisenberg trade-off), so it represents the same feature as a few clean fine-scale coefficients near its location.
- **A spectral conv is global and stationary.** It applies the same filter everywhere, so no mode count buys the per-location adaptivity the §6.2 gate has (Fourier where smooth, wavelet where sharp).
- **More modes = more weights to fit from scarce HF.** The wavelet branch reaches the same sharp content with far fewer effective degrees of freedom — decisive when HF is scarce.
- **There is a hard grid wall.** The capped 256 working grid has a Nyquist limit (§5.4), past which "more modes" is meaningless.

**The honest counter-case.**
Where the missing energy is *global and stationary* high-frequency (spread-out, periodic — e.g. high-wavenumber homogeneous turbulence), more modes genuinely is the simpler right tool and wavelets do not help; the cheap middle ground there is F-FNO (below).
This is exactly why §6.2 *gates* the two branches rather than replacing FNO, and why E0 (§12) is the deciding audit: it measures whether a dataset's high-frequency residual energy lives in *localized* features (the wavelet branch wins) or *global* modes (raise modes / F-FNO).

- **Multiwavelet operator (MWT, Gupta et al. 2021)** — a more principled, better-grounded multiscale cousin of WNO.
  A stronger wavelet branch if plain WNO proves finicky.
- **F-FNO / factorized-FNO (Tran et al. 2023)** — stays in the FNO family but affords far more modes cheaply.
  Raises the frequency ceiling without a second basis.
- **U-Net / UNO or FNO↔U-Net hybrid** — no spectral truncation and the default diffusion denoiser backbone; the pragmatic workhorse if the wavelet route stalls.
- **Analytic interface / level-set head (P6 `mf_interface_levelset`)** — instead of widening the basis, sidestep truncation entirely.
  On interface-dominated datasets (e.g. Cahn–Hilliard) the network regresses only *smooth* targets — a signed-distance-like field φ and smooth bulk amplitudes A, B — then composes the sharp solution analytically as `u = A·tanh(φ/ε) + B`, with ε taken from the condition vector.
  The network never regresses a sharp target, so the spectral wall never applies; the sharpness is injected by the analytic form, not learned.
  It is a dataset specialist — it falls back to plain transfer off-interface (the `mf_fno_pinn_transfer` pattern), and the `composite_nRMSE` geomean banks the specialist win (§10).
  Anchors: implicit shock tracking (Zahr et al.), NDNN (arXiv:2405.15559), OT-interpolation MF ROMs for diffuse-interface two-phase flows (arXiv:2603.04232).

### 6.4 What the WNO literature actually shows (evidence base for §6.1)

The strength/weakness split in §6.1 is empirically supported — but with one calibration that *sharpens* the decision to combine rather than replace.
The WNO-over-FNO margin is **modest on smooth standard benchmarks and larger on sharp / discontinuous / irregular-domain problems**, exactly the energy-location principle of §4.

Concrete head-to-heads (web-verified 2026-07-15, provenance noted per line):

- **Darcy (smooth) — Multiwavelet operator vs FNO** — relative-L2 **0.0152 vs 0.0177** (~14% relative) at s=32.
  Real but small; this is the regime where FNO is already strong, so the wavelet edge is thin.
  *(Gupta et al., NeurIPS 2021, from the paper's reported Darcy table.)*
- **WLNO (Wavelet-Laplace NO, 2026)** — **+12.9% on Darcy** and **+20.7% on Navier–Stokes** over its Laplace-NO baseline, with the Burgers gain concentrated **at the shock interface**.
  The baseline smears the sharp gradient; the Haar detail sub-bands recover it.
  The baseline here is Laplace-NO, not FNO, so read these as "wavelet localization helps," not a direct FNO delta.
  *(arXiv:2605.24658; primary source read.)*
- **Canonical WNO (Tripura & Chakraborty 2022)** — benchmarked on Burgers, Darcy (rectangular *and* irregular domains), Allen–Cahn, and Navier–Stokes; the stated advantage is on discontinuities, spikes, and complex/irregular boundaries where FNO's global Fourier basis carries no spatial localization.
  *(arXiv:2205.02191; abstract + secondary aggregate — the paper's own error tables were not line-read, so treat the per-benchmark margins as unverified.)*

**Evidence-quality caveat (load-bearing).**
Most "WNO beats FNO" numbers are **author-reported, on the same smooth Li-et-al. benchmarks**; independent third-party head-to-heads are thin.
The *robust*, theory-backed pattern is the sharp-interface / discontinuity advantage — **not** a uniform win.
This is precisely why §6.1 combines rather than replaces, and why §10's specialist framing is the right one: bank the sharp-dataset wins, do not bet on a global WNO upset.

**Documented WNO limitations that constrain our design:**

- **Vanilla WNO can *underfit* sharp detail** — parameterizing only the top wavelet scale drops high-frequency content, and the literature fix is a U-Net-enhanced WNO (U-WNO, arXiv:2408.08190).
  Implication: the gated wavelet branch of §6.2 must not be a naive single-scale WNO — carry multiple detail scales (or a U-Net skip), or it reintroduces the very blur §5 exists to remove.
- **Architecture sensitivity is real** — results depend materially on wavelet family, decomposition depth, and activation, enough that a NAS paper exists for it (FWNO, arXiv:2405.06910).
  Implication: wavelet family/level is a first-class hyperparameter, not a default (new §13 bullet).
- **Non-uniform / unstructured grids remain open research for WNO** — standard DWT wants dyadic, structured grids.
  This matches the `resolve_grid` geometry-general concern; the hybrid mitigates it structurally by keeping FNO as the general-purpose branch and letting WNO specialize only where a clean grid exists.

**Variant map — where the ecosystem already connects to our other levers:**

- **WDNO — wavelet *diffusion* operator (Hu et al. 2024, arXiv:2412.04833)** — a denoising/diffusion model over a wavelet representation, reporting lowest long-term error on fluid and climate data.
  This is essentially §9's combined bet (refiner-on-wavelet) *already realized in the wild* — a strong external precedent to study before E4, and direct evidence the two levers compose.
- **PIWNO — physics-informed WNO (N et al. 2023, arXiv:2302.05925)** — a PDE-residual loss on a WNO.
  The natural bridge to `mf_fno_pinn_transfer` (#2) if we want to physics-regularize the wavelet branch on the Poisson datasets.
- **MWT (Gupta et al. 2021)** — already flagged in §6.3 as the stronger, better-grounded wavelet branch if plain WNO proves finicky.
  The Darcy number above is the quantitative reason.
- **Multiscale Attention Wavelet NO (AAAI)** — the wavelet×attention hybrid, sitting on the spectral-attention direction rather than the pure dual-basis one.

### 6.5 Prior art on Fourier+wavelet hybrids (the blend is not novel; the MF application is)

Combining a global-spectral basis with a wavelet basis inside a neural operator is an active 2023–2026 line, not a new idea, so the §6.2 recommendation must be framed as an *application*, not a new mechanism (this mirrors the Candidate C correction in §7.4).

**Structural precedent — WLNO already *is* the §6.2 design, with Laplace in place of Fourier.**
WLNO (arXiv:2605.24658) augments a global-spectral (Laplace pole-residue) layer with a *parallel single-level Haar wavelet branch*, fused by a *learnable sigmoid-gated weight* initialized so the global branch dominates early and the wavelet branch activates gradually.
That is precisely the §6.2 "A + B" block — dual-branch operator + learned gate + graceful-to-global fallback — so the *mechanism* is published.
Swapping the Laplace branch for a Fourier (FNO) branch is a small delta, not a novel contribution.

**Explicit Fourier+wavelet combinations already exist.**

- Physics-Informed Fourier-Wavelet Transformer (arXiv:2606.24696, 2026) fuses Fourier and wavelet features for multiscale CFD surrogates.
  An attention/transformer mechanism rather than an FNO/WNO spectral convolution, but direct prior art on using both bases together.
- Physics-informed Multi-resolution Neural Operator (arXiv:2510.23810, 2025) uses a DWT to split content into frequency bands, then integrates them with Galerkin (Fourier-space) attention.
- *(Caveat: both of these PDFs did not text-extract cleanly during the scan; the attention-vs-convolution reading is from title + abstract and should be confirmed by reading the papers before formal citation.)*

**Adjacent "beyond-Fourier localized basis" operators.**
Shearlet Neural Operator (arXiv:2604.25181, 2026) replaces the Fourier basis with a directional multiscale shearlet basis and reports beating FNO on shock-dominated / anisotropic Burgers.
Coupled Multiwavelet NO (arXiv:2303.02304) extends the MWT line.
Same thesis as §6.1 — augment or replace the global Fourier basis with a localized one.

**What the prior-art scan did *not* surface.**
A method that is exactly "parallel FNO spectral-convolution branch + WNO wavelet-convolution branch fused by a per-location learned spatial gate," by that construction, was not found.
The nearest are WLNO (same gating, Laplace global branch) and the Fourier-wavelet transformer (Fourier+wavelet, but attention), so the precise instantiation may be unclaimed.
The mechanism class is well-trodden and a reviewer would place it in this cluster.

**The surviving, defensible novelty is the multi-fidelity application.**
Every hybrid above is *single-fidelity* operator learning.
None uses a gated dual-basis operator as the **HF-residual backbone / denoiser inside an MF fusion pipeline** — conditioned on the FIRE LF distribution channels `[mu, sigma, q10, q50, q90]`, applied to the near-pure-high-frequency LF→HF residual, and scored under the `composite_nRMSE` specialist framing (§10).
That MF framing — not the dual-basis block itself — is the contribution to claim, and the family's `INSPIRATION.md` should cite WLNO and the Fourier-wavelet cluster as prior art, not only FNO + WNO.

---

## 7. Candidate C — cycle-consistent invertible-degradation fusion (exploits the LF surplus)

### 7.1 The idea

The starting observation is the project's defining asymmetry: LF data is abundant, HF data is scarce.
The map we actually want — LF→HF — is *ill-posed*, because it is a sharpening / super-resolution problem in which many distinct HF fields collapse onto the same LF observation.
The map in the other direction — HF→LF — is *well-posed*: it is a smoothing / coarsening (blur, downsample, low-pass), stable and well-conditioned.
The idea is to learn the easy, well-posed forward degradation and use it as a hard constraint on the hard inverse, instead of learning the inverse unconstrained.
This is the same move that underlies learned-degradation super-resolution and cycle-consistent image translation: pin down the operator you *can* estimate cleanly, then invert it under that constraint.
The intuitive form in the source brainstorm is deblurring — to learn to sharpen, first learn to blur, then reverse it — which is exactly right when LF is a warped / low-passed version of HF.

Concretely there are two operators:

- a **forward (degradation) operator** `D: HF → LF` — well-posed, trainable wherever paired HF/LF exists, and on datasets where LF is literally a coarsening of HF, partly known a priori;
- an **inverse (reconstruction) operator** `R: LF → HF` — the quantity of interest, ill-posed on its own.

The lever that makes this pay is **cycle-consistency on the abundant LF data**:
enforce `D(R(LF)) ≈ LF` on *every* LF sample — not only the few paired with HF — and `R(D(HF)) ≈ HF` on the scarce HF.
The first term is semi-supervised: it turns the LF surplus into training signal for `R` without needing HF labels, which is precisely the resource the project has in excess and currently under-uses.

### 7.2 Where it fits, and how the pieces connect to A and B

This is a **fusion-mechanism / data-efficiency** lever, distinct from the two headline levers:
Candidate A fixes the *loss* (blur), Candidate B fixes the *representation* (mode truncation), and Candidate C changes *what the model is trained against* so the abundant LF constrains the scarce-HF inverse.
It is therefore orthogonal to — and composable with — both:
`R` can itself be the deterministic refiner of §5 running on the hybrid backbone of §6, with the cycle-consistency term added to its objective.

Two sub-mechanisms from the source brainstorm need correction before use, and the correction is where this session's "what do people use instead of GANs" thread lands:

- **Self-training feedback loop.**
  The raw idea — run `R` to manufacture extra HF and retrain on it — is pseudo-labeling, and naive pseudo-labeling accumulates its own error because it adds no new ground truth.
  The fix is to **gate** each pseudo-HF sample by its cycle-consistency residual `‖D(R(LF)) − LF‖`, keeping only the self-consistent ones; the forward operator `D` becomes the quality filter the raw loop lacked.
- **Realism prior without a GAN.**
  The brainstorm's alternative — "or run a GAN" on real/fake HF — buys HF-realism at the cost of training instability and, worse, a metric conflict: an adversarial (or any *sampled*) output trades point-wise accuracy for perceptual realism (the perception–distortion tradeoff), which *raises* nRMSE, the scored metric.
  The GAN-free substitutes are the two this session settled on: a **spectral / Sobolev loss** that enforces high-frequency fidelity directly (cheap, deterministic, nRMSE-safe), or the deterministic flow / diffusion refiner of §5 used as `R`'s high-frequency head with the **posterior mean** (DDIM / probability-flow) reported rather than a sample.

### 7.3 Honest caveats

- **The degradation assumption is per-dataset, not universal.**
  `D: HF→LF` is a clean, near-known operator only where LF is genuinely a coarsening / blur of HF (e.g. coarse-grid Poisson).
  Where LF comes from a *different solver or different physics*, `D` is neither known nor necessarily a deterministic function of HF, so it must be learned and may be weak; cycle-consistency still applies but carries less constraint.
  This mirrors §4's energy-location principle: the lever's value is dataset-dependent, and the E0 spectral audit should be extended to flag which datasets have genuine degradation structure.
- **Cycle-consistency alone underdetermines HF.**
  Because many HF fields share an LF, the `D(R(LF)) ≈ LF` term does not by itself pin the correct HF; the scarce HF anchors and a physically-constrained (or partly-known) `D` are what break the tie.
- **Novelty is largely refuted — the mechanism is prior art.**
  An in-repo grep (§7.4) confirms no implemented family enforces inter-fidelity cycle-consistency, so it is new *to this repo*.
  A fact-checked literature scan (§7.4) shows the *mechanism* is published (Kim et al. 2021 is a near-exact relative), so the contribution is consolidation, not invention.

### 7.4 Provenance, prior art, and required baselines

**Origin.**
Candidate C originates from an in-session brainstorm over `IDEA.md` (2026-07-15), refined against this memo's existing levers.

**Fact-check status (2026-07-15).**
The novelty claim was checked in two directions and cross-verified in a Codex↔Claude adversarial pass against the arXiv / journal primary sources.
The result is that the *mechanism is largely prior art*, not a new idea.
In-repo: a grep across all 21 `models/*` families plus `references/v9_baseline` confirms no family enforces inter-fidelity cycle-consistency or learns a forward-degradation operator.
The only `HF→LF` map present is the *fixed, known* `downsample_field_to_fidelity` used to synthesize LF test inputs, never a learned operator inside a cycle-consistency loss, so Candidate C is genuinely new *to this repo*.
In the literature: every one of the five defining ingredients, and the near-complete combination, is already published.
Each citation below was verified against its primary source (titles, authors, and mechanisms confirmed; the two corrections from the adversarial pass are folded in).

**Closest prior art (verified, ranked by proximity).**

- **Kim, Kim, Won & Lee, "Unsupervised deep learning for super-resolution reconstruction of turbulence"** (arXiv:2007.15324; *J. Fluid Mech.* **910**, A29, 2021; DOI 10.1017/jfm.2020.1028) — *the strongest anchor, but not an exact match.*
  A cycle-consistent GAN with two learned generators — `G: LR→HR` (reconstruct) and `F: HR→LR` (degrade) — trained on **unpaired** turbulence with bidirectional cycle losses `F(G(x)) ≈ x`, `G(F(y)) ≈ y`.
  Its LES→DNS example fuses ~10,000 unpaired LES fields with ~100 DNS fields, which is genuinely inter-fidelity (different solvers), not mere downsampling.
  It covers ingredients 1, 2 and 4 and the cycle machinery, but "matches ingredients 1–4 almost exactly" is **overstated on two points** (per the adversarial pass).
  First, its LES degradation is only *partly learned* — it adds a *fixed top-hat-filter* consistency term (`λ = 10`, enforcing `ℐ·G(x) ≈ x` with `ℐ` the top-hat filter; confirmed against the ar5iv primary text on 2026-07-15), so the physical forward operator is partly a known filter, not solely a learned `D`.
  Second, it is **unsupervised unpaired** domain translation, not Candidate C's *semi-supervised* regime of scarce **paired** HF anchors plus an abundant **unpaired** LF surplus.
  It also differs on ingredient 5 — it is adversarial, whereas Candidate C is deliberately GAN-free.
  Net: the closest published relative and a required baseline (below), but not the same method.
- **Guo et al., "Closed-loop Matters: Dual Regression Networks for Single Image Super-Resolution"** (arXiv:2003.07018; CVPR 2020) — *the explicit reconstruct-the-LR-back closed loop.*
  Learns an additional `D: HR→LR` that reconstructs the LR from the predicted SR (`D(R(LR)) ≈ LR`) precisely to constrain the ill-posed inverse when paired data is unavailable and the degradation is unknown.
  Ingredients 1 + 2 + 3 (one direction) + 4, but generic single-image CV (not MF / PDE) and a single closed-loop LR term rather than full bidirectional translation.
- **Kim, Hong & Shin, "Semi-Supervised Neural Super-Resolution for Mesh-Based Simulations" (SuperMeshNet)** (arXiv:2605.09284, 2026) — *the matching data regime.*
  "Complementary learning" leverages a small amount of paired LR–HR data plus **abundant unpaired LR** data via two jointly-trained MPNN models (reported 90% less HR data for equal-or-lower RMSE) — exactly Candidate C's semi-supervised MF-PDE regime (ingredient 3), GAN-free.
  The mechanism is co-training, not an explicit `D(R(LF)) ≈ LF` learned-degradation cycle.
- **Xu, Lu, Shen, Xuan & Barzegari, "Diffusion-based Models for Unpaired Super-resolution in Fluid Dynamics"** (arXiv:2504.05443, 2025) — *the GAN-free unpaired MF-fluid precedent.*
  Two-step, no paired data: unpaired low-fidelity→high-fidelity translation at the LR level via an Enhanced Denoising Diffusion Implicit Bridge, then SR3 super-resolution (with an FNO / neural-operator dynamics step for trajectories).
  Matches ingredient 5 (diffusion, GAN-free) plus unpaired and fluid-MF, but the lever is a diffusion bridge, not cycle-consistency.
- **Bischoff & Deck, "Unpaired Downscaling of Fluid Flows with Diffusion Bridges"** (arXiv:2305.01822; **published in *Artificial Intelligence for the Earth Systems*, vol. 3, e230039, 2024**, DOI 10.1175/AIES-D-23-0039.1 — the arXiv "submitted" metadata is stale) — chains two conditional diffusion models into a diffusion bridge for unpaired LR↔HR geophysical-fluid downscaling and bias correction.
  The same GAN-free diffusion-bridge category as Xu et al.

**What survives as novel.**
No single published method combines *all* of: cycle-consistency **as the multi-fidelity fusion lever**, an **FNO / neural-operator** backbone, evaluation **across the 17 PDE benchmark families**, and a **GAN-free** (spectral / Sobolev or deterministic-diffusion) realism term.
The verdict is therefore *recombination, not invention*: Candidate C should be positioned as **engineering / consolidation, not a novel mechanism**.
Its one defensible novelty angle — endorsed by the adversarial pass — is the **semi-supervised use of the LF surplus as a hard constraint on the scarce-HF inverse** (cycle-consistency-gated pseudo-labeling, anchored by the scarce *paired* HF), inside a GAN-free MF neural-operator validated broadly across PDE families.
That specific setting is what the CycleGAN / dual-regression / diffusion-bridge precedents above do *not* occupy, and it is "more than a trivial reimplementation if validated broadly."

**From Kim's CycleGAN to a neural operator (the concrete port).**
Converting Kim (2021) to an operator is not a separate idea — it *is* Candidate C, and the substitutions that make it a contribution rather than a reimplementation are exactly the surviving-novelty axes above.
The port, substitution by substitution:

| Kim (2021), CNN CycleGAN | Neural-operator port = Candidate C |
| --- | --- |
| CNN generator `G: LR→HR` | FNO / neural-operator reconstruction `R` (resolution-invariant via `resolve_grid`) — the FIRE-conditioned residual refiner of §5 |
| CNN generator `F: HR→LR` | learned **operator** degradation `D` |
| fixed top-hat filter `ℐ·G(x) ≈ x` | the project's *known* `downsample_field_to_fidelity` where LF is a genuine coarsening; a learned `D` where LF is a different solver (§7.3) |
| WGAN-GP adversarial realism | **GAN-free** realism — a spectral / Sobolev loss, or the §5 deterministic refiner reporting the posterior mean (nRMSE-safe, §7.2) |
| fully **unpaired / unsupervised** | **semi-supervised** — scarce *paired* HF anchors + cycle-consistency `D(R(LF)) ≈ LF` on the abundant unpaired LF, pseudo-HF gated by the cycle residual |
| turbulence slices, fixed grid | validated **across the 17 PDE families** |

The port inherits §7.3's two caveats unchanged: `D` is a strong constraint only where a genuine HF→LF degradation exists, and cycle-consistency alone underdetermines HF — the paired anchors break the tie.
Because it is a port of a GAN method, required baseline (1) below — a Kim-style cycle-consistent *GAN* — is what proves the GAN-free substitution earns its place.

**Required baselines.**
Because the mechanism is prior art, a Candidate C build must beat two direct baselines, not just the current leaderboard:

1. a **Kim-style cycle-consistent GAN** (the adversarial version of the same `D` / `R` cycle), to justify the GAN-free claim; and
2. **SuperMeshNet-style semi-supervised co-training** (the same paired-HF + unpaired-LF regime without an explicit degradation cycle), to justify the cycle-consistency lever.

**INSPIRATION.md.**
A from-scratch family must cite these **MF-specific** sources (Kim 2021; SuperMeshNet 2026; Xu 2025; Bischoff & Deck 2024), not the generic CV anchors previously listed (CycleGAN — Zhu et al. 2017; KernelGAN — Bell-Kligler et al. 2019; Noisy Student — Xie et al. 2020).
Those generic CV anchors motivate the mechanism but are the wrong citations for a multi-fidelity operator family.

---

## 8. Candidate D — warp-then-correct / registration-based fusion (fixes the geometric-misalignment bottleneck)

### 8.1 The idea

Candidates A–C all assume the LF and HF fields are *spatially aligned* — that a sharp feature lives at the same location in both, and only its amplitude or high-frequency detail is wrong.
That assumption breaks on advective and interface-dominated problems, where a mispositioned shock, front, or vortex sits at a slightly *different* location in LF than in HF.
When it does, the additive correction `HF = mu_LF + delta` has to do something pathological: erase the feature where LF put it and redraw it where HF wants it.
The residual that accomplishes this is itself sharp and bipolar, so MSE blurs it — and the refiner of §5 is then fixing the wrong quantity, because the error is a *displacement*, not a missing high-frequency amplitude.

The fix is to *move* the feature instead of re-synthesizing it.
What makes this tractable is that the **displacement field is smooth even when the solution is not**.
Two fields related by a shifted shock differ by a smooth transport map, so a network can predict the displacement in exactly the low-frequency regime it is already good at, and the sharp content rides along for free through the warp.

### 8.2 How it works, concretely

Forward pass:

```
HF_pred = warp( up(LF), w_theta ) + delta_theta
```

- `w_theta` is a **smooth 2-channel displacement field** predicted by a small FNO head and applied to `up(LF)` by differentiable `grid_sample`.
  It is **zero-initialized** and **smoothness-penalized** (a gradient penalty on `w_theta`), so at initialization the warp is the identity and the whole family degrades gracefully to the plain additive correction it extends.
- `delta_theta` is the usual FiLM-conditioned residual FNO — the same residual head the rest of the memo uses, but now operating on an *already-aligned* field.
  Its target is the genuinely-missing amplitude rather than a displacement it cannot represent.

Optional warm-start (decouples the ill-posed joint optimization): precompute optical-flow displacement targets between paired `up(LF)`/HF training fields (DIS or Horn–Schunck) and supervise `w_theta` directly for the first epochs.
Then release it to train end-to-end.
The optical flow is a *training-time target generator computed offline*; there is no classical solver in the eval path, so the family is fully neural at inference.

### 8.3 Why it is orthogonal, and where it wins

Candidate D attacks a bottleneck none of the others touch: A fixes the loss, B fixes the representation, C fixes the data budget, and D fixes *geometric alignment*.
It therefore composes with all three — the aligned residual `delta_theta` can itself be the deterministic refiner of §5 running on the hybrid backbone of §6.
Its downside is bounded by construction: zero-init plus the smoothness penalty means it can only *help* relative to plain additive correction.
On the smooth smoke datasets (heat/Poisson), which carry no misalignment, the warp learns to stay near identity and the family reduces to today's recipe.
Where it wins is the advective / interface / shock datasets — exactly the sharp regime the `composite_nRMSE` geomean rewards a specialist for (§10).

### 8.4 On the roadmap and unbuilt

No published multi-fidelity *operator* method predicts an inter-fidelity displacement field and warps before correcting.
The registration-based framing — "align, then correct" — is a documented gap, which makes this both the highest-novelty candidate here and a publishable family in its own right.
The mechanism is the flagship P-proposal (`mf_warp_correct`) of `MF_Sharp_HighFreq_Report.md`.
A from-scratch family still needs `models/mf_warp_correct/INSPIRATION.md` citing its anchors — transport-map regularity for discontinuous solutions (arXiv:1712.09144) and shift / transport mechanisms for operator learning on shocks (arXiv:2210.01074) — re-verified against the primary sources first.

---

## 9. The combined bet: refiner on a hybrid backbone

The two headline levers are orthogonal, so the highest-ceiling family is the **refiner mechanism (§5) with a hybrid or non-truncating backbone as its denoiser (§6)**.
Loss bottleneck and representation bottleneck fixed together, aimed at the sharp datasets.
External precedent that this composition works: WDNO (arXiv:2412.04833) already runs a diffusion model over a wavelet representation and reports lowest long-term error on fluid and climate data (§6.4).
Candidates C (data) and D (geometry) stack onto this same core.
The warp of §8 can wrap the refiner-on-hybrid residual, and the cycle-consistency term of §7 can be added to its objective.
The ceiling family is really "align, then refine on a hybrid backbone, trained under the LF-surplus constraint."
Sequencing matters for attribution: build and validate each lever alone first, then combine, so a final win can be attributed rather than guessed (see §12).

---

## 10. Backbone freedom and the scoring lever

Two facts make backbone diversity strictly good for the score:

1. **The contract permits it** — only `data_adapters`, `eval`, `data`, and `baselines` are fixed.
   The per-family `model.py` backbone is mutable, and non-FNO backbones already ship.
2. **`composite_nRMSE` rewards specialists** — it is the geomean over datasets of the *best model per dataset*, so a sharp-regime backbone needs only to win the sharp datasets while a transfer-FNO keeps the smooth ones.
   The composite takes the best of each.

There is therefore no "must generalize everywhere" penalty against a specialized backbone — the metric is built to bank regime wins.

---

## 11. Honest odds and where each lever wins

| Family                                                                                                                            | Rough odds vs the board                                                                      | Reasoning                                                                                                                                                   |
| --------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Refiner as head-swap of`fno_fire_distcond` (#3): beat parent, crack top ~5                                                      | ~60–70%                                                                                     | Residual headroom (0.0264) and the mechanism targets the blur directly.                                                                                     |
| FNO↔WNO hybrid backbone (MSE/transfer setup): win the sharp datasets                                                             | Good on sharp; neutral-to-slightly-worse on smooth if ungated, bounded if gated              | Fixes representation where FNO truncates; gate limits smooth-dataset downside.                                                                              |
| Candidate C (cycle-consistent invertible-degradation): lift the sharp datasets via LF-surplus semi-supervision, composed with A/B | Promising where a genuine HF→LF degradation exists; weak where fidelities differ physically | Turns abundant LF into a constraint on the scarce-HF inverse; per-dataset applicability (§7.3), so bank it only where E0 flags real degradation structure. |
| Candidate D (warp-then-correct): win the advective / interface / shock datasets                                                   | Good on misaligned-feature datasets; near-neutral where LF/HF are already aligned            | Fixes a*displacement* error additive correction cannot; zero-init + smoothness penalty bounds the downside to "no worse than plain correction."           |
| Either lever: become outright#1 on *smooth* datasets (beat 0.0122–0.0154)                                                      | ~25–35%                                                                                     | Transfer champions are strong and low there, and relative-L2 under-weights high-frequency gains on smooth fields.                                           |
| Combined refiner + hybrid (optionally wrapped by the warp): top the board via**Elo** on the high-frequency datasets         | Highest ceiling of the set                                                                   | Both bottlenecks fixed; Elo is per-dataset pairwise, so sharp-dataset wins lift rank even if smooth-dataset medians do not move.                            |

**The evaluation caveat that stays true throughout:** the smoke datasets are `ifc_heat` + `ifc_poisson`, both smooth, so a wash there is expected and does **not** indicate failure.
Both levers must be judged on the sharp datasets in the full benchmark.

---

## 12. Recommended experiment sequence

1. **E0 — Spectral audit (prerequisite).**
   Measure the high-mode energy of each dataset's HF residual and whether it is representable within the current `modes_cap` / grid Nyquist.
   This ranks the datasets by how much either lever can win, and flags whether `modes_cap` must be raised.
2. **E1 — Refiner on FNO (isolate the mechanism).**
   Deterministic refiner as a controlled head-swap of `fno_fire_distcond`; identical conditioning/LF model/target, only the residual head changes.
3. **E2 — Warp-then-correct on FNO (isolate the alignment mechanism).**
   Add the zero-initialized, smoothness-penalized displacement head of §8 to the same transfer recipe with everything else held fixed, so any gain is attributable to alignment alone.
   Run with and without the optical-flow warm-start to see whether the joint optimization needs decoupling.
4. **E3 — FNO↔WNO hybrid backbone under the standard setup (isolate the backbone).**
   Dual-branch + gated operator, MSE/transfer training, so any gain is attributable to the backbone alone.
5. **E4 — Combine (refiner denoiser on the hybrid backbone, optionally wrapped by the warp).**
   Only after E1–E3 each show a signal, so the combined result is interpretable rather than a multi-variable guess.
6. **E5 (optional) — cycle-consistency objective (Candidate C).**
   Add the inter-fidelity cycle-consistency term (`D(R(LF)) ≈ LF` on the LF surplus, with pseudo-HF gated by the same residual) to the strongest of E1–E4.
   Use the datasets E0 flags as having genuine HF→LF degradation structure.
   Keep it an objective-only change so the LF-surplus gain is attributable.

All of E1–E5 are evaluated on the sharp datasets, not on the heat/Poisson smoke test.

---

## 13. Open questions to resolve before finalizing

- Which of the 15–17 benchmark datasets are genuinely high-frequency, and is their high-mode energy representable within current caps? (E0 answers this.)
- Which combination design (dual-branch, gated, frequency-split) best trades accuracy against compute for the hybrid backbone?
- For the refiner, what `sigma_min` / `K` best trade sharpness against the forward-pass budget, and is `sigma`-guidance from the LF channels the load-bearing conditioning signal?
- Which wavelet family and decomposition depth suit the sharp datasets, and should the WNO branch be single-scale or U-Net-enhanced (U-WNO) to avoid reintroducing high-frequency underfit?
  Grounded in the §6.4 architecture-sensitivity and vanilla-WNO-underfit findings.
- For Candidate C, which datasets have a genuine (near-known) HF→LF degradation operator versus a merely learned, weak one, and does cycle-consistency on the LF surplus measurably tighten the scarce-HF inverse there?
  E0 should be extended to flag this.
- For Candidate D, which datasets actually exhibit inter-fidelity *misalignment* (a displaced shock / front / vortex) versus pure amplitude error, and does the warp need the optical-flow warm-start or can it be learned end-to-end from zero-init?
  An LF/HF cross-correlation displacement estimate, computable inside the E0 pass, flags the misaligned datasets.

---

## 14. Status and next step

This is a strategy memo, not a validated result; the odds are judgment and nothing has been run.
Hardening paths available on request:

- a Codex↔Claude adversarial fact-check pass over the external claims (PDE-Refiner, WNO, FNO, MWT, IRNO, and the warp / transport anchors of §8);
- a matplotlib figure set (leaderboard headroom; MSE-blur vs refiner spectrum; Fourier-vs-wavelet localization; an LF→HF displacement-field illustration for the warp);
- a PDF render to match the existing report deliverables.

The natural next step is to choose the first build target — the refiner (E1), the warp-then-correct mechanism (E2), the hybrid backbone (E3), or straight to the combined family — and turn it into an implementation spec.
