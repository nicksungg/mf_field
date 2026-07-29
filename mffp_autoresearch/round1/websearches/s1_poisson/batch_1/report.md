# Websearch Report — Stream `s1_poisson`, Batch 1

> Persisted verbatim by the orchestrator from the websearcher's return
> (agent could not Write .md files — harness restriction; content unmodified).

**Stream**: s1_poisson · **Batch**: 1 · **Total iterations**: 5 · **WebSearch calls**: 11 · **WebFetch calls**: 12 (7 usable, 5 failed) · **Cap hit**: **yes** (5 of 5)

## Search trace

### Turn 1 — establish the bar and the benchmark's own method
Terms: IFC/Poisson nRMSE; all-pairs MF operator learning; IFC-GPODE results table. Chosen because the stream is defined by a number I had only read second-hand, and §13.3 forbids recall.
- IFC is a **continuous-fidelity latent neural ODE** with GP/ODE fidelity-varying bases and a tensor-Gaussian variational posterior [cite: https://arxiv.org/abs/2207.00678] → iteration_1.md
- Engine-returned numeric line: "IFC-ODE2 at **m = 1 and m = 2.14** is **0.036 vs. 0.018** ... for Poisson's" — suggests the two numbers may be **one method at two target fidelities**, not two methods [cite: search return on https://openreview.net/pdf?id=dUYLikScE-] → iteration_1.md
- **MFRNP**: aggregate (average) lower-fidelity decoded predictions, learn the residual to HF; **Poisson nRMSE 0.0076 ± 7.49e-4** [cite: https://arxiv.org/html/2402.18846v1] → iteration_1.md
- For >2 nested levels the described convention is a **cascade/stack**, not all-pairs [cite: engine synthesis over https://arxiv.org/abs/2208.05606, https://arxiv.org/pdf/2404.11965] → iteration_1.md

### Turn 2 — the two §12.1-sanctioned routes: variance reduction and added information
Terms: MLMC training of neural operators; N_hf≈5 variance reduction; physics-informed Poisson correction.
- **MLMC-NO**: telescoping ∇L₀^coarse + Σ∇(L_ℓ^fine − L_ℓ^coarse), architecture-agnostic, demonstrated on **FNO + Poisson/Darcy**; framed as compute-at-fixed-accuracy [cite: https://arxiv.org/pdf/2505.12940] → iteration_2.md
- MF-DeepONet (residual learning + input augmentation) reports **an order of magnitude smaller error at equal HF budget** [cite: https://arxiv.org/abs/2204.06684, snippet] → iteration_2.md
- **PINO** "compensates for coarse or limited data" by enforcing PDE constraints at high resolution — the mechanism already in `mf_fno_pinn_transfer` [cite: engine synthesis] → iteration_2.md
- No source at N_hf ≈ 5. → iteration_2.md

### Turn 3 — first D1 refutation attempt
Terms: POSEIDON all2all → fidelity; fidelity-conditioned single-network FNO.
- POSEIDON's all2all is over **time snapshots via the semigroup property**, with time-conditioned layer norms — not fidelity [cite: https://nips.cc/virtual/2024/poster/95731, https://www.emergentmind.com/papers/2405.19101] → iteration_3.md
- Two explicit engine negatives: no source found combining FiLM + all-levels + FNO. → iteration_3.md

### Turn 4 — second D1 refutation attempt, from the classical-MF vocabulary
Term: "all pairs"/"pairwise" fidelity augmentation, cross-fidelity mapping.
- Nearest named classical relative: **input-augmentation GP MF modeling** — surrogates as functions of "both input and fidelity variables" [cite: https://www.emergentmind.com/topics/multi-fidelity-gaussian-process-surrogate-modeling, snippet] → iteration_4.md
- **MFFM**: nested hierarchy G₀⊂…⊂G_L, residual δ=u_HF−u_LF, **adjacent** fidelities only, **one velocity net per level**, end-to-end cascade fine-tune, **512–896 samples**, not the IFC benchmark [cite: https://arxiv.org/html/2605.16118v1] → iteration_4.md

### Turn 5 — the prior-art verdict (mandatory)
Terms: MFRNP full text (D2); deep ensembles at small N (D3); fidelity-as-input joint training (D1).
- Multi-resolution data "**jointly incorporated during training**" is an established neural-operator strategy; deep-GP MF optimizes all levels under a **single joint objective**; MF-HNP infers per-level latents [cite: engine synthesis over https://par.nsf.gov/servlets/purl/10347020 (fetch failed), https://arxiv.org/html/2402.02031v1] → iteration_5.md
- **Progressive MF learning**: sequential ladder training, >2 levels, and it "**specifically addresses very small high-fidelity sample counts**" as a key contribution [cite: https://arxiv.org/pdf/2510.13762] → iteration_5.md
- Ensemble/seed averaging for variance reduction with quantified "**gains in accuracy in small-data regimes and robustness across random seeds**" at the operator level [cite: https://arxiv.org/html/2606.17460, snippet] → iteration_5.md

## Prior-art verdict

| Candidate direction | Verdict | Citations (this loop) | What remains open |
|---|---|---|---|
| **D1.** All-ordered-pairs fidelity training — ONE FiLM-FNO over every (f_src<f_tgt) pair of the nested 100/50/20/5 ladder, queried (LF→HF) at eval (`akash/models/mf_fno_allpairs`) | **preempted-but-MF-composition-open** | fidelity-as-input: https://www.emergentmind.com/topics/multi-fidelity-gaussian-process-surrogate-modeling (snippet); continuous-fidelity conditioning: https://arxiv.org/abs/2207.00678 (fetched); adjacent-pair nested cascade: https://arxiv.org/html/2605.16118v1 (fetched); joint all-levels training: https://arxiv.org/html/2402.02031v1 (snippet); progressive ladder at tiny HF: https://arxiv.org/pdf/2510.13762 (fetched); all2all = **time** pairs only: https://nips.cc/virtual/2024/poster/95731 (snippet) | Conditioning on fidelity, joint multi-level training, and adjacent-level cascades are all published. **Not found published**: (i) **all ordered pairs** (not just adjacent) as a data-amplification augmentation, (ii) with a **single shared** network rather than one net per level, (iii) at **N_hf = 5** on the `li2022ifc` Poisson ladder. Two independent searches (turn 3, turn 4) returned explicit negatives on (i)+(ii). |
| **D2.** Multi-level residual aggregation / control-variate (telescoping) single-loop training over the ladder, replacing pretrain→finetune | **preempted (cite)** | https://arxiv.org/pdf/2505.12940 (fetched — telescoping control-variate gradient on **FNO + Poisson**); https://arxiv.org/html/2402.18846v1 (fetched — aggregate-then-residual, **Poisson 0.0076 ± 7.49e-4**) | The mechanism is published *and* MFRNP's number is literally one of this repo's own paper bars (`poisson_local` test_l2). Open only in narrow senses: MFRNP aggregates by **plain average** — a *learned/optimal* control-variate weighting was not found; and MLMC-NO's **hierarchy construction is ambiguous in my sources** (snippet says downsampled, PDF extraction says separate coarse solves) — which matters because repo law requires real coarse solves. Neither gap is worth a batch-1 card on its own. |
| **D3.** Explicit variance reduction at N_hf = 5 by ensembling (seed / pair ensembles) as the *mechanism* | **preempted (cite, snippet-grade)** | https://arxiv.org/html/2606.17460 (snippet); https://arxiv.org/pdf/2606.29440 (snippet) | Ensembling is textbook and reported at the operator level for small data. Additionally it **collides with the round's own protocol**: seeds {0,1,2} are the CI mechanism (§4.4), so a seed-ensemble inside one model consumes and confounds the CI. Open only as a *within-run* ensemble (e.g. over fidelity-pair queries) that does not touch the seed axis — which is really a variant of D1, not a separate direction. |

## Citations summary

- [Li, Wang, Kirby, Zhe 2022] "Infinite-Fidelity Coregionalization for Physical Simulation" (NeurIPS 35:25965–25978) — https://arxiv.org/abs/2207.00678 (fetched, abs) ; https://openreview.net/pdf?id=dUYLikScE- (**fetch failed**, search-return only) ; https://arxiv.org/pdf/2207.00678v2 (**fetch failed**) — used in: iteration_1
- [Niu et al.] "Multi-Fidelity Residual Neural Processes for Scalable Surrogate Modeling" (MFRNP) — https://arxiv.org/html/2402.18846v1 (**fetched, HTML**) ; https://arxiv.org/pdf/2402.18846 (**fetch failed**) — used in: iteration_1, iteration_5
- [Rowbottom, Fresca, Liò, Schönlieb, Boullé] "Multi-Level Monte Carlo Training of Neural Operators" — https://arxiv.org/pdf/2505.12940 (fetched) ; https://arxiv.org/abs/2505.12940 (fetched, inconclusive) — used in: iteration_2, iteration_3
- [2026] "Multi-Fidelity Flow Matching: Cascaded Refinement of PDE Solutions" — https://arxiv.org/html/2605.16118v1 (fetched) — used in: iteration_1, iteration_4
- [2025] "Progressive multi-fidelity learning with neural networks for physical system predictions" — https://arxiv.org/pdf/2510.13762 (fetched) — used in: iteration_5
- [2025] "Physics-informed low-rank neural operators with application to parametric elliptic PDEs" — https://arxiv.org/pdf/2509.07687 (fetched, thin) — used in: iteration_2
- [Herde et al. 2024] "Poseidon: Efficient Foundation Models for PDEs" — https://nips.cc/virtual/2024/poster/95731 ; https://www.emergentmind.com/papers/2405.19101 (search-returned) — used in: iteration_3
- [Lu et al. 2022] "Multifidelity deep neural operators ..." — https://arxiv.org/abs/2204.06684 (search-returned) — used in: iteration_2
- [MF-GP topic page] "Multi-Fidelity GP Surrogate Modeling" (input-augmentation MF) — https://www.emergentmind.com/topics/multi-fidelity-gaussian-process-surrogate-modeling (search-returned) — used in: iteration_4
- [Wu et al.] "Multi-fidelity Hierarchical Neural Processes" — https://par.nsf.gov/servlets/purl/10347020 (**fetch failed, DNS**) — used in: iteration_5
- [2024] "Multi-fidelity physics constrained neural networks for dynamical systems" (MSPCNN) — https://arxiv.org/html/2402.02031v1 (search-returned) — used in: iteration_5
- [2026] "Operator Boosting Produces Pareto-Efficient PDE Surrogates" — https://arxiv.org/html/2606.17460 (search-returned) — used in: iteration_5
- [2026] "Randomized neural operator for parametric PDEs ..." — https://arxiv.org/pdf/2606.29440 (search-returned) — used in: iteration_5
- [2023] "Multi-fidelity Fourier Neural Operator ... Geological Carbon Storage" — https://arxiv.org/pdf/2308.09113 (**fetch failed**; contents NOT cited) — used in: iteration_3, iteration_4
- [2022] "Multi-fidelity wavelet neural operator" — https://arxiv.org/abs/2208.05606 (search-returned) — used in: iteration_1

## Dead ends

- **OpenReview PDF endpoint** (`openreview.net/pdf?id=…`) — browser-verification wall. Use arXiv or a mirror.
- **arXiv `/pdf/` endpoints** — 3 of 4 failed as unparseable binary; `/html/` worked every time it existed. **Prefer `arxiv.org/html/`.**
- **`par.nsf.gov`** — DNS `ESERVFAIL` from this cluster.
- **UNRESOLVED and material — the 0.036 / 0.018 attribution.** The engine returned "IFC-ODE2 at **m = 1 and m = 2.14** is 0.036 vs. 0.018", i.e. possibly **one method at two target mesh spacings**, whereas `baselines/paper_baselines.json` records `paper_method: IFC-ODE2` = 0.036 and `paper_method_alt: IFC-GPODE` = 0.018. Both PDF fetches failed. **Do not let a card assert which method 0.036 belongs to.**
- **UNRESOLVED — MLMC-NO hierarchy construction** (downsampled vs separate coarse solves). Load-bearing under repo law.
- **Nothing at N_hf ≈ 5** across 11 searches. The regime is genuinely under-studied — a finding: the literature supplies **mechanisms but no effect sizes** for this stream.

## For the brainstormer

1. **Quote this verdict for D1 verbatim: `preempted-but-MF-composition-open`.** Do not claim "all-pairs fidelity training" as novel. What is open, and the only thing a card may claim: **all *ordered* pairs (not just adjacent) through a *single shared* network, at N_hf = 5 on this nested 100/50/20/5 ladder.**
2. **Frame batch 1 honestly as a measurement, not an invention.** `mf_fno_allpairs` is built and never scored on `ifc_poisson` through this round's eval layer at 200 epochs. At L=4 → only **6 ordered pairs**; its known O(L²) failure cannot fire. Cheapest genuine experiment in the stream; directly tests §12.1's "amplify data rather than add capacity" prior.
3. **Design the pair set as the actual variable.** Arms: (a) **adjacent pairs only** (published cascade structure, 3 pairs), (b) **all ordered pairs** (6 pairs, the open composition), (c) **LF→HF only** (plain transfer control). If (b) ≈ (a) the finding is "the ladder's value is in adjacent steps"; if (b) ≫ (a), non-adjacent pairs carry real information and that *is* the result. This turns a preempted direction into a falsifiable one.
4. **Do not propose D2 or D3 as batch-1 mechanisms.** D2 preempted by MLMC-NO (on FNO + Poisson) and MFRNP (whose Poisson number is one of this repo's own bars). D3 collides with §4.4 (seeds are the CI mechanism).
5. **Two facts that must not be asserted in the card**: (i) which method owns 0.036 vs 0.018 (sources conflict; cite "the recorded bar 0.036 (ADR 0002)" without method attribution); (ii) MLMC-NO's hierarchy construction.
6. **Thresholds must be qualitative this batch** — no noise floor or anchor yet at search time (G3 pending); write the falsification clause against the pair-set contrast (internally controlled), not an absolute nRMSE. The only in-zoo number (0.042) is a 2500-epoch result; this round runs 200.
7. **The literature gives mechanisms but no effect sizes for N_hf = 5.** Defensible claims are ordinal (arm A vs arm B), not absolute.
