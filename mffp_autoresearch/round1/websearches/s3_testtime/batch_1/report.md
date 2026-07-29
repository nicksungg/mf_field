# Websearch Report — Stream `s3_testtime`, Batch 1

**Stream**: s3_testtime
**Batch**: 1
**Total iterations**: 5
**Total WebSearch calls**: 15 (3 per iteration, at the cap every time)
**Total WebFetch calls**: 19 — 12 usable, 7 failed (3 x oversize PDF /
corrupted-binary, 1 x `maxContentLength exceeded`, 1 x OpenReview verification
wall, 2 x abstract-only fallbacks that still resolved). Every failure is named
inline in the iteration file where it happened and in Dead ends below.
**Cap hit**: **YES** — 5 of 5 iterations used (noted at the top of
`iteration_5.md`). Field context was declared **ENOUGH** at the end of
`iteration_3.md`; iterations 4-5 were spent entirely on 3.3.

**Precondition note**: `state/anchors/` is empty and `state/noise_floor.json`
does not exist (batch 0 / gate G3 still queued — `state/gates.md`). Recorded in
`summary_so_far.md`; the brainstormer must write an anchor-free falsification
clause and re-check it against the noise floor once G3 lands.

---

## Search trace

### Turn 1 — does test-time residual refinement work at all? -> `iteration_1.md`
**Terms chosen** (and why): `summary_so_far.md` had just shown the stream's own
prior is a mis-attribution and the placeholder mechanism measured null, so go
straight at the mechanism family, verify the second lever first-hand
(program.md 13.3 bans memory-citation), and hunt the failure mode.
- `test-time optimization neural operator output PDE residual refinement inference-time NITO`
  - Key finding: the hazard, stated outright — "numerically minimizing the PDE
    residual can be an **unreliable proxy for reconstruction accuracy in
    ill-conditioned systems**", explaining "why residual minimization fails
    despite achieving low residual values". [cite: https://arxiv.org/abs/2606.27354]
  - Key finding: gradient-based test-time residual optimization is the
    *baseline* newer work tries to replace. [cite: https://arxiv.org/html/2512.01370]
- `Iterative Refinement Neural Operators Learned Fixed-Point Solvers arXiv 2605.24041`
  - Key finding: IRNO verified first-hand — frozen base, `h_{k+1} = h_k +
    alpha*Phi(x,h_k)`, alpha in {0.2,0.25} (0.6 **diverges**); progressive
    spectral loss `rho = 1+(|w|/|w|_nyq)^lambda_k`; HF-band error to
    **1.48-2.04%** of base by iter 12; cross-operator transfer **58.53%**
    without retraining. Decisively: "**no true PDE residuals are computed at
    test time**" and "**no mention of coarse-grid, low-fidelity inputs, or
    multi-fidelity training data**". [cite: https://arxiv.org/html/2605.24041]
- `physics-informed fine-tuning at inference time neural operator overfitting failure worse than base prediction`
  - Key finding: the published safeguard is an **anchor loss** to the
    pretrained model — i.e. `mf_fno_ptr`'s anchor is prior art, and a strong
    anchor + weak residual is a no-op by construction. (search-summary level)

### Turn 2 — Helmholtz ill-conditioning + the phase-field substitute -> `iteration_2.md`
**Terms chosen** (and why): Helmholtz is the ONLY panel dataset with a
computable true residual, so the ill-conditioning threat had to be tested
there; and four panel datasets are time snapshots with no du/dt, so something
must replace the residual.
- `Helmholtz ... indefinite ill-conditioned ... high wavenumber`
  - Key finding: "PINNs frequently encounter severe optimization instabilities
    when modeling **singular sources**" — and `ext__helmholtz_2d`'s condition
    vector IS a point source. Fix is architectural (envelope demodulation),
    10x speedup "where baseline PINNs fail entirely".
    [cite: https://arxiv.org/html/2603.02231]
- `energy functional ... phase field Allen-Cahn Cahn-Hilliard ...`
  - Key finding: free-energy-as-objective is published for phase-field
    operators — the minimizing-movement scheme "optimizes and controls how the
    total free energy of a system evolves, **instead of solving the governing
    equations directly**" — but at **training** time.
    [cite: https://arxiv.org/abs/2302.13368]
- `multi-fidelity test-time refinement low-fidelity coarse solve initialization ...`
  - Key finding (the big one): MFFM claims exactly "the **cascaded composition
    of a frozen base operator plus a learned refinement stage**"; base trained
    on LF, refinement conditioned on its output, "without modifying the frozen
    base weights". But it "does **not** explicitly employ the true governing
    PDE residual". [cite: https://arxiv.org/pdf/2605.16118]

### Turn 3 — the intersection, the guarantee, the solver route -> `iteration_3.md`
**Terms chosen** (and why): one un-refuted intersection was left (real physics
objective x test time x MF); the "skill > 1" pathology demanded a
cannot-be-worse guarantee; and proposal N3 was still untested.
- `physics residual test-time correction of multi-fidelity surrogate ...`
  - **No usable results** for the test-time+MF+physics triple; everything
    returned was train-time MF residual learning.
- `guarantee refinement never worse than baseline safeguard line search trust region ...`
  - Key finding: the learned-refinement family offers **no monotonicity
    guarantee**; only a classical solver is monotone by construction.
- `learned preconditioner Krylov CG correction of neural operator prediction ...`
  - Key finding: NOWS — learned "high-quality initial guesses for Krylov
    methods such as conjugate gradient and GMRES" "while **preserving the
    stability and convergence guarantees of the underlying numerical
    algorithms**", up to 90% runtime cut. [cite: https://arxiv.org/abs/2511.02481]
  - Key finding: FCG-NO — frozen NO as nonlinear preconditioner in flexible
    CG, 2-8x on elliptic/Poisson; "**No multi-fidelity**".
    [cite: https://arxiv.org/pdf/2402.05598]
  - **ENOUGH** declared here (`iteration_3.md` last line): every branch of the
    design space had a fetched source.

### Turn 4 — prior-art refutation, round 1 -> `iteration_4.md`
**Terms chosen** (and why): each phrased to FIND the paper that kills a
candidate direction (D1 Helmholtz true residual, D2 MF-conditioned fixed-point
refinement, D4 phase-field free-energy correction).
- kill-D1 term: no direct kill; one unresolved threat (PIC-Flow, fetch failed).
- kill-D2 term: **SINO** found — a third instance of the same skeleton,
  learnable starter for "dominant low-frequency components" + unrolled learned
  iterator `Delta u = B(f - A u)`; "**purely learned. It does not use true PDE
  residuals**", "**No explicit multi-fidelity structure**", starter **not**
  frozen. [cite: https://arxiv.org/html/2606.18305]
- kill-D4 term: **no usable results** across three result pages — no free-energy
  or equilibrium projection applied post-hoc to a predicted phase-field snapshot.

### Turn 5 — FINAL (cap), threats resolved + verdict -> `iteration_5.md`
- `Quaratiello Rizzo physics-based flow matching ... Helmholtz residual`
  - Key finding: PIC-Flow's Helmholtz residual is a **training** loss, so D1
    survives; and it contributes a mandatory trick — an "**interface-aware
    masking scheme for the Helmholtz residual that excludes ... pixels where
    finite-difference stencil errors dominate**".
    [cite: https://arxiv.org/abs/2605.06929]
- `PINO instance-wise test-time optimization anchor loss ...`
  - Key finding: instance-wise test-time optimization "using **only the PDE
    loss**" plus "an additional **anchor loss** ... to prevent the optimization
    from deviating too much" is repeatedly described as established — but
    **three fetch attempts failed**, and the one page that DID fetch
    (emergentmind) says it lacks those details. Recorded as *presumed
    preempted, unverified*. [cite: https://arxiv.org/pdf/2111.03794 —
    search-summary only]
- `neural operator warm start CG ... multi-fidelity few high-fidelity samples elliptic`
  - Key finding: NOWS covers "the canonical **Poisson** equation, a
    second-order elliptic PDE"; and **super-fidelity** maps "**low-fidelity
    solutions to high-fidelity targets**, then employs this as a **warm-start
    initialization for classical steady-state PDE solvers**", >=2x, "capable of
    learning with just a **few solutions**". D3 is fully preempted, MF form
    included. [cite: https://arxiv.org/abs/2312.11842]

---

## Prior-art verdict

| Candidate direction | Verdict | Citations (fetched) | What remains open |
|---|---|---|---|
| **D1** — exact governing residual (`du + k^2u = f`, source located by `x`) descended on the **output field** with an anchor, from a multi-fidelity prediction; `ext__helmholtz_2d` is the only panel dataset where this is computable | **preempted-but-MF-composition-open (cite)** *(with an honesty caveat: the preempting source could not be fetched)* | ENS https://arxiv.org/abs/2606.27354 (fetched); PIC-Flow https://arxiv.org/abs/2605.06929 (search-returned; does NOT preempt — training-time); PE-PINN https://arxiv.org/html/2603.02231 (fetched); PINO https://arxiv.org/pdf/2111.03794 (**search-summary only, 3 fetch attempts failed**) | Mechanism = PINO instance-wise test-time optimization + anchor loss (presumed prior art). Open: **field-space** vs weight-space optimization; doing it **from an MF prediction at N_hf = 5**; and scoring against **copy-LF** rather than against the base model — nobody in this literature uses that bar. **Standing threat (fetched)**: residual minimization "can be an unreliable proxy for reconstruction accuracy in ill-conditioned systems"; Helmholtz is the canonical indefinite operator with a singular point source. **Mandatory mitigation**: PIC-Flow-style masking of the source/stencil-error pixels. |
| **D2** — IRNO-style frozen-base weight-tied fixed-point refinement conditioned on the LF field, progressive spectral loss | **preempted (cite)** | IRNO https://arxiv.org/html/2605.24041 (fetched); MFFM https://arxiv.org/pdf/2605.16118 (fetched); SINO https://arxiv.org/html/2606.18305 (fetched) | Three independent 2026 papers build "coarse initialization + learned residual refinement"; MFFM claims the LF-conditioned frozen-base cascade as its **primary contribution**. Open only if the corrector is driven by a **real physics objective** instead of data supervision (all three verified purely learned). Second open item, cheap: IRNO's cross-operator transfer (58.53% without retraining) has never been tested **across fidelities**. |
| **D3** — MF prediction as warm start for a fixed Krylov budget (in-repo proposal N3 `mf_fno_solve`) | **preempted (cite)** | NOWS https://arxiv.org/abs/2511.02481 (fetched, incl. elliptic/Poisson); super-fidelity https://arxiv.org/abs/2312.11842 (fetched, **LF->HF warm start**, few solutions); FCG-NO https://arxiv.org/pdf/2402.05598 (fetched) | Mechanism, elliptic application, and MF variant all published. Only reframing left: accuracy-under-HF-scarcity vs speed (all cited works report runtime: 90%, 2x, 2-8x). Also blocked in practice — the discrete operator + source is unavailable for `ifc_poisson` (`refine.py` docstring), leaving Helmholtz alone. **Not recommended for batch 1.** |
| **D4** — free-energy / equilibrium projection as a **test-time** correction on the four time-snapshot phase-field panel datasets | **novel** (by absence of evidence — weak) | Nearest neighbours, all training-time: Phase-Field DeepONet https://arxiv.org/abs/2302.13368 (fetched abstract); PINNs-MPF https://arxiv.org/pdf/2407.02230; Sharp-PINNs https://arxiv.org/html/2502.11942 | Three result pages found nothing applying an energy/equilibrium projection post-hoc to a predicted snapshot. Caveats the card must confront: a free energy is a weaker accuracy proxy than a true residual (ENS hazard, amplified), and its minimizer at fixed mean composition is **not** the t=0.5 snapshot — state explicitly what prevents collapse to bulk equilibrium. |

---

## Citations summary

Fetched (primary, full or abstract-level, quoted in the iteration files):
- [Liu, Shang, Wang, Ren & Yang 2026] "Iterative Refinement Neural Operators are Learned Fixed-Point Solvers" (ICML 2026) — https://arxiv.org/html/2605.24041 (abs https://arxiv.org/abs/2605.24041 ; code https://github.com/xiaotianliu-dartmouth/Iterative_Refinement_Neural_Operator ) — used in: iteration_1 (term 2), iteration_4 (term 2)
- [Error-Conditioned Neural Solvers] — https://arxiv.org/abs/2606.27354 — used in: iteration_1 (term 1) *(PDF fetch failed with maxContentLength; abstract page fetched)*
- [Multi-Fidelity Flow Matching] "Cascaded Refinement of PDE Solutions" — https://arxiv.org/pdf/2605.16118 — used in: iteration_2 (term 3), iteration_4 (term 2)
- [PE-PINN] "PINNs with Architectural Physics Embedding for Large-Scale Wave Field Reconstruction" — https://arxiv.org/html/2603.02231 — used in: iteration_2 (term 1)
- [Li et al.] "Phase-Field DeepONet" — https://arxiv.org/abs/2302.13368 — used in: iteration_2 (term 2) *(abstract only; PDF fetch failed)*
- [NOWS] "Neural Operator Warm Starts for Accelerating Iterative Solvers" — https://arxiv.org/abs/2511.02481 — used in: iteration_3 (term 3), iteration_5 (term 3) *(abstract; PDF fetch failed with maxContentLength)*
- [FCG-NO] "Neural operators meet conjugate gradients" — https://arxiv.org/pdf/2402.05598 — used in: iteration_3 (term 3)
- [SINO] "Starter-Iterator Neural Operator" — https://arxiv.org/html/2606.18305 — used in: iteration_4 (term 2)
- [Super-fidelity] "Neural operator-based super-fidelity: A warm-start approach for accelerating steady-state simulations" — https://arxiv.org/abs/2312.11842 — used in: iteration_5 (term 3)
- [emergentmind PINO topic page] — https://www.emergentmind.com/topics/physics-informed-neural-operator-pino — used in: iteration_5 (term 2) *(fetched; used as NEGATIVE evidence — it does not confirm PINO test-time optimization)*

Search-returned but NOT fetched (explicitly weaker; flagged everywhere they appear):
- [PIC-Flow] Quaratiello & Rizzo, "Physics-Based Flow Matching for Full-Field Prediction of Silicon Photonic Devices" — https://arxiv.org/abs/2605.06929 — used in: iteration_4 (term 1), iteration_5 (term 1) *(2 PDF fetch attempts failed)*
- [PINO] "Physics-Informed Neural Operator for Learning PDEs" — https://arxiv.org/pdf/2111.03794 — used in: iteration_1 (term 1), iteration_5 (term 2) *(3 fetch attempts failed across arXiv PDF and OpenReview)*
- [PRISMA] — https://arxiv.org/html/2512.01370 — used in: iteration_1 (term 1)
- [PINNs-MPF] — https://arxiv.org/pdf/2407.02230 ; [Sharp-PINNs] — https://arxiv.org/html/2502.11942 — used in: iteration_4 (term 3)

---

## Dead ends

- `physics residual test-time correction of multi-fidelity surrogate ... few high-fidelity samples` (iter 3 t1) -> returned only **train-time** MF residual learning (MFRNP, bi-fidelity operator learning). The test-time x MF x physics triple genuinely returns nothing; this is the verdict's main open space, but also means there is no template to copy.
- `free energy projection test-time correction phase field ... tanh equilibrium profile ...` (iter 4 t3) -> three result pages, all training-time PINN phase-field solving. Query was over-compound; a narrower "post-processing/projection of a predicted phase field" phrasing might do better in batch 2.
- `gradient descent on predicted field Helmholtz exact source residual ... anchor loss` (iter 4 t1) -> too compound; half the page was off-domain (video-coding "prediction refinement" patents, object matting).
- **arXiv PDF fetches are unreliable here**: 5 of 8 attempted PDF fetches failed (2 x `maxContentLength size of 10485760 exceeded`, 3 x corrupted/binary passthrough). `arxiv.org/abs/...` and `arxiv.org/html/...` worked far better — future batches should prefer those.
- OpenReview PDFs are behind a browser-verification wall — not fetchable.

---

## For the brainstormer

The brainstormer MUST quote the verdict row for whatever it proposes.

1. **First: program.md 12.3's quantified prior for this stream is false, and I verified it in-repo** (`summary_so_far.md`). `mf_fno_ptr`'s `RESIDUAL_REGISTRY` contains only `ifc_poisson` and `ifc_heat`, so on era5/pm_test the refinement is a **documented NO-OP** — and indeed `mf_fno_ptr` and `mf_fno_transfer_film` are byte-identical to 17 digits there (`bench_metrics_subset.csv`). The "-21%" is `mf_fno_foundation`'s number, mis-read across rows. Where the mechanism actually ran (`ifc_poisson`) it bought **-1.5%, inside the CI, at 163x inference latency**. Do not cite -21% in a card. The honest framing is: *the mechanism has never been shown to help here; batch 1 is the first real test.*
2. **Do not propose D2's plain form.** "Frozen base + LF conditioning + learned residual refinement" is **MFFM's own primary contribution claim** [https://arxiv.org/pdf/2605.16118], and IRNO [https://arxiv.org/html/2605.24041] and SINO [https://arxiv.org/html/2606.18305] are two more instances. Project novelty record is 0-for-4 (program.md 13.3); this would be 0-for-5.
3. **The strongest batch-1 card is D1, narrowly scoped**: exact Helmholtz residual `du + k^2u = f` (f is a point source located by `x = [k, source_x, source_y]` — confirmed from `benchmark_42/ext/helmholtz_2d/{meta,README}`), descended on the **output field** with an anchor, from a frozen MF base. Quote the verdict as `preempted-but-MF-composition-open`. Two non-negotiables: (a) **mask the source / stencil-singular pixels** in the residual [PIC-Flow, https://arxiv.org/abs/2605.06929]; (b) the falsification clause must be stated against **copy-LF skill** (Helmholtz copy-LF 0.3295, best zoo skill **1.45**), not against the base model — beating your own base while still losing to your own input is the round's defining failure mode.
4. **Budget-guard the design against the ENS hazard** [fetched, https://arxiv.org/abs/2606.27354]: "minimizing the PDE residual can be an unreliable proxy for reconstruction accuracy in **ill-conditioned** systems". Helmholtz is exactly that. The cheap protection is a **residual-vs-error sweep** — record nRMSE at several `refine_steps` / `w_res` values and report whether the residual and the error move together at all. That single curve is a genuine result whichever way it goes, and it makes a null outcome informative rather than wasted (program.md 1: an experiment is genuine if we learn why fusion fails either way).
5. **Note what a true residual can and cannot reach on this panel** (`summary_so_far.md` table): **1 of 6** datasets has a computable governing residual (Helmholtz). `ifc_poisson`'s source decode is not shipped; the four phase-field/reaction sets are time snapshots with no du/dt and (except Cahn-Hilliard) no IC in `x`. So a card promising panel-wide test-time physics refinement is not implementable as written — scope it to Helmholtz, or take D4.
6. **D4 is the only `novel` verdict** and is the natural batch-2 card: free-energy / equilibrium projection at test time on the phase-field panel. If proposed now, the card must say what stops the projection collapsing the field toward bulk equilibrium (the free-energy minimizer at fixed mean composition is *not* the t=0.5 snapshot), and must acknowledge that the nearest neighbour, Phase-Field DeepONet [https://arxiv.org/abs/2302.13368], does the same substitution at **training** time.
7. **Cheap freebie worth a line in any card**: IRNO's refinement module transfers **across base operators** without retraining (58.53% improvement, Sec 4.5). Nobody has tested transfer **across fidelities**. That is a one-line hypothesis with a real prior behind it.
