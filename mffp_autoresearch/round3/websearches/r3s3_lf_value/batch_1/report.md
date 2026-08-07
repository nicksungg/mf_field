# Websearch Report — Stream `r3s3_lf_value`, Batch 1

**Stream**: `r3s3_lf_value` (lever) — "what is LF-at-train worth on the honest panel
(coverage/amplitude, ch identifiability-vs-trainability), matched with/without arms at
matched procedure?" (project.yaml `streams`)
**Batch**: 1
**Total iterations**: 4 (cap 5 — **not** hit; stopped early, both refutation questions
answered decisively from fetched primary sources)
**WebSearch calls**: 12 (3 per turn x 4 turns; term lists are recorded per turn below and in each `iteration_*.md`)
**WebFetch calls**: 0 usable — **the WebFetch tool and `curl`/`wget` are intercepted in
this environment and return a redirect error naming a plugin that is not in this
agent's toolset.** Routed around per the standing directive: **10 page-fetch attempts** were
made with `python3 urllib.request` (8 bodies successfully read, 2 blocked: OpenReview
browser wall and a ScienceDirect 403) (+ tag-strip for HTML, + `zlib` inflation of
PDF `FlateDecode` streams for PDFs). Every "fetched" claim below means the body was
retrieved and read in this loop.
**Cap hit**: no

## Search trace

### Turn 1 — field framing: LUPI, MF-as-auxiliary-signal, and negative transfer
Terms: (1) `learning using privileged information theory why it helps optimization
rather than information deterministic target`; (2) `multi-fidelity training data
optimization benefit versus information gain low-fidelity auxiliary loss neural
operator 2026`; (3) `when does low-fidelity data hurt surrogate negative transfer
multi-fidelity ablation matched budget no-benefit`.
Chosen because round 3's panel is now completeness-certified (ADR r3-0001 D1), which
converts the stream's question into "what is privileged data worth when the input
already determines the target".
Key findings: the canonical LUPI benefit is stated as a convergence-rate/search-space
effect [cite: https://papers.nips.cc/paper/3960-on-the-theory-of-learnining-with-privileged-information — search-return only, PDF-only page];
a 2025 systematic study explicitly "conduct[s] equivalent single-fidelity tests for
each case, quantifying the performance gains achieved through fusing multiple sources"
[cite: https://arxiv.org/abs/2512.02868 — fetched]; negative transfer is the recognised
risk, with LF data able to worsen HF predictions [cite: https://arxiv.org/abs/2410.12690 — fetched].
→ `iteration_1.md`

### Turn 2 — pinning the rate claim; trainability vs information; MF value-of-information
Terms: (1) `unifying distillation and privileged information learning rate O(1/n)
versus O(1/sqrt(n)) teacher student`; (2) `auxiliary data improves optimization not
identifiability distinguishing trainability limit from information limit neural
network`; (3) `multi-fidelity value of information ablation how much does low-fidelity
data help when parameters fully determine solution PDE surrogate`.
Key findings: the rate mechanism is now citable verbatim — "a good teacher can try to
ease the problem at hand by accelerating the learning rate from O(n^-1/2) to O(n^-1)"
[cite: https://leon.bottou.org/publications/pdf/iclr-2016.pdf — fetched; arXiv record
http://arxiv.org/abs/1511.03643v3 — fetched via arXiv API]; "data determines the
fundamental limit of trainability" exists as a general DNN-theory claim
[cite: https://arxiv.org/abs/2602.16177 — fetched]; **no usable result** for a matched
experiment deciding information-vs-optimisation for auxiliary data, and **no usable
result** for MF value-of-information where the parameters provably determine the field.
→ `iteration_2.md` (`ENOUGH` recorded: field context sufficient, remaining turns to §3.3)

### Turn 3 — refutation pass 1 (D3 distillation; D2 warm-start leg)
Terms: (1) `coarse mesh simulation as privileged information distillation
parameter-to-field surrogate low-fidelity teacher not available at inference`;
(2) `low-fidelity pretraining benefit ablation warm start versus additional supervision
optimization curriculum coarse-to-fine PDE surrogate few high-fidelity samples`;
(3) `"low-fidelity" data used only during training surrogate takes only parameters at
inference matched ablation with and without low-fidelity arms`.
Key findings: privileged-features distillation is studied *including when it fails* —
"PFD outperforms several baselines (no-distillation, pretraining-finetuning,
self-distillation, and generalized distillation) ... [but] as the predictive power of a
privileged feature increases, the performance of the resulting student model initially
increases but then decreases" [cite:
https://proceedings.neurips.cc/paper_files/paper/2022/file/aa31dc84098add7dd2ffdd20646f2043-Paper-Conference.pdf — fetched];
LF-in-the-solver warm starts and LF-embedded surrogates exist but keep LF inside the
test path [cite: https://arxiv.org/html/2601.03086, https://arxiv.org/abs/2111.05841 —
search returns]. **No usable result** separating LF-pretraining's warm-start effect
from its supervision effect at matched budget. → `iteration_3.md`

### Turn 4 — refutation pass 2 (D1 completeness regime; D2 diagnostic)
Terms: (1) `privileged information provides no additional information when input is
sufficient statistic distillation acts as variance reduction regularization regression`;
(2) `benchmark where parameter vector exactly determines PDE solution field does
multi-fidelity still help sample efficiency deterministic mapping study`;
(3) `distinguishing whether failure is due to insufficient training data or
optimization difficulty experiment design overparameterized surrogate phase retrieval`.
Key findings: "KD acts as a form of partial variance reduction, which can reduce the
stochastic gradient noise, but may not eliminate it completely" [cite:
https://proceedings.neurips.cc/paper_files/paper/2023/file/ee1f0da706829d7f198eac0edaacc338-Paper-Conference.pdf — fetched];
the information-vs-optimisation dichotomy has canonical vocabulary — phase retrieval is
"possible — in principle — as soon as the number of measurements equals the
dimensionality of the signal" yet has "an algorithmically hard phase where all known
polynomial-time algorithms struggle" [cite: https://arxiv.org/pdf/2502.04282 — fetched].
**No usable result** for MF on a completeness-certified parametric benchmark.
→ `iteration_4.md`

## Prior-art verdict

| Candidate direction | Verdict | Citations (fetched) | What remains open |
|---|---|---|---|
| **D1** — matched, budget-matched **+/-LF-at-train** contrast for a condition-only field surrogate on the **completeness-certified** round-3 panel; the deliverable is the certified per-dataset effect in copy-LF skill units (success criterion 2, >= 3 datasets) | **preempted-but-MF-composition-open** | Ablation genre: https://arxiv.org/abs/2512.02868 (fetched — "equivalent single-fidelity tests for each case, quantifying the performance gains achieved through fusing multiple sources"). Mechanism theory: https://leon.bottou.org/publications/pdf/iclr-2016.pdf (fetched — privileged information accelerates the rate O(n^-1/2) -> O(n^-1)); http://arxiv.org/abs/1511.03643v3 (fetched via arXiv API). Negative side: https://arxiv.org/abs/2410.12690 (fetched — LF data can worsen HF predictions; transfer must be local). | The composition, all four clauses simultaneously: (a) LF **absent from the test path by construction** (stripped view), so the contrast prices LF as *training data*, not as an input; (b) a panel carrying an explicit **completeness certificate** (HF exactly reconstructible from the stored condition) — turn 4 term 2 returned **nothing** in this slot, every retrieved MF-PDE work either keeps LF at inference or never certifies sufficiency; (c) the **copy-LF denominator** ("is the model worth more than running the coarse solve?") plus the ifc `affine_on_hf_train` floor; (d) N_hf = 5 on the ifc ladder with a certified `min_claimable_effect`. **The finding must be the measured number, never the ablation genre.** |
| **D2** — decide **identifiability vs trainability** on `sharp__cahn_hilliard` (19-D complete condition): arms where LF can only act as an optimisation aid (LF-pretrain -> HF-finetune, warm start, curriculum) vs arms where LF supplies supervision at conditions with no HF row | **preempted-but-MF-composition-open** | Dichotomy + vocabulary: https://arxiv.org/pdf/2502.04282 (fetched — information-theoretic recoverability "as soon as the number of measurements equals the dimensionality" vs "an algorithmically hard phase where all known polynomial-time algorithms struggle"). Optimisation channel formalised: https://proceedings.neurips.cc/paper_files/paper/2023/file/ee1f0da706829d7f198eac0edaacc338-Paper-Conference.pdf (fetched — KD = **partial variance reduction** of the stochastic gradient). Trainability-limit language: https://arxiv.org/abs/2602.16177 (fetched — "data determines the fundamental limit of trainability"). | The **discrimination has a name** (statistical-to-computational gap), so the card must not claim the concept. What is open: nobody has run it for *low-fidelity coarse solves as the auxiliary signal on a certified-complete PDE condition vector*, and turn 2 term 2 + turn 3 term 2 both returned **no usable result** for a matched experiment separating warm-start/optimisation help from supervision help. Note the sharpened stake: B4 measured the no-LF ch arm at median per-sample cosine 0.0003-0.0385 vs the LF arm's 0.962-0.964 — that signature is *local-minimum-like*, which is a prediction the trainability arm can falsify. |
| **D3** — distil an **LF-consuming teacher** into a condition-only student (LF as a pure training-time privileged signal, teacher absent at test) | **preempted (cite)** | https://proceedings.neurips.cc/paper_files/paper/2022/file/aa31dc84098add7dd2ffdd20646f2043-Paper-Conference.pdf (fetched — PFD trains a teacher with privileged features, then a student without them; benchmarks it against no-distillation, **pretraining-finetuning**, self-distillation and generalized distillation; and characterises the **non-monotone failure**: a very predictive privileged teacher yields high-variance student estimates and *inferior* test performance). Also https://leon.bottou.org/publications/pdf/iclr-2016.pdf (fetched — generalized distillation unifies distillation and LUPI). Search-returned only (fetch **403**): https://www.sciencedirect.com/science/article/abs/pii/S0952197625034293 (representation-level distillation for train-inference data asymmetry in **surrogate modeling**). | Ship only as a **cited baseline arm**, never as the contribution. If proposed at all, the card must pre-register the PFD non-monotone prediction: on the completeness-certified panel the LF teacher is *very* predictive of the HF field, which is precisely the regime where PFD is documented to **degrade** the student — a cheap, publishable falsification target. Round-2 batch 1 already returned the same verdict class for this mechanism (`round2/websearches/r2s3_lf_train_signal/batch_1/report.md`), so a re-proposal without this framing is a rebadge. |

## Citations summary

- [Lopez-Paz, Bottou, Scholkopf & Vapnik 2016] "Unifying distillation and privileged information", ICLR 2016 — https://leon.bottou.org/publications/pdf/iclr-2016.pdf (PDF body extracted) and http://arxiv.org/abs/1511.03643v3 (arXiv API record) — used in: `iteration_2.md` term 1.
- [Yang, Sanghavi, Rahmanian, Bakus & Vishwanathan 2022] "Toward Understanding Privileged Features Distillation in Learning-to-Rank", NeurIPS 2022 — https://proceedings.neurips.cc/paper_files/paper/2022/file/aa31dc84098add7dd2ffdd20646f2043-Paper-Conference.pdf (PDF body extracted; arXiv mirror https://arxiv.org/pdf/2209.08754 search-returned) — used in: `iteration_3.md` term 1.
- [Safaryan, Peste & Alistarh 2023] "Knowledge Distillation Performs Partial Variance Reduction", NeurIPS 2023 — https://proceedings.neurips.cc/paper_files/paper/2023/file/ee1f0da706829d7f198eac0edaacc338-Paper-Conference.pdf (PDF body extracted) — used in: `iteration_4.md` term 1.
- [arXiv:2502.04282, 2025] "Isolating the hard core of phaseless inference: the Phase selection formulation" — https://arxiv.org/pdf/2502.04282 (PDF body extracted) — used in: `iteration_4.md` term 3.
- [Villatoro, Geraci & Schiavazzi 2025] "Assessing the performance of correlation-based multi-fidelity neural emulators", arXiv:2512.02868 — https://arxiv.org/abs/2512.02868 (fetched) — used in: `iteration_1.md` term 2.
- [Wang, Mak, Miller & Wu 2025] "Local transfer learning Gaussian process modeling" (LOL-GP), arXiv:2410.12690v3 — https://arxiv.org/abs/2410.12690 (fetched) — used in: `iteration_1.md` term 3.
- [Qi 2026] "Conjugate Learning Theory: Uncovering the Mechanisms of Trainability and Generalization in DNNs", arXiv:2602.16177v2 — https://arxiv.org/abs/2602.16177 (fetched) — used in: `iteration_2.md` term 2.
- [Pechyony & Vapnik 2010] "On the Theory of Learning with Privileged Information", NeurIPS 2010 — https://papers.nips.cc/paper/3960-on-the-theory-of-learnining-with-privileged-information — **search-return only, body NOT read**; cite only as "search-returned", or cite Lopez-Paz et al. 2016 instead — used in: `iteration_1.md` term 1.
- [EAAI 2025] "Learning from more to predict with less: Representation-level multimodal distillation ... in surrogate modeling" — https://www.sciencedirect.com/science/article/abs/pii/S0952197625034293 — **search-return only; fetch returned HTTP 403** — used in: `iteration_3.md` term 3.

## Dead ends

- `https://openreview.net/forum?id=yBTDCqNcan` (Transfer Learning in Multi-fidelity Surrogate Modeling: A Wind Farm Case) → OpenReview browser-verification wall; body unreadable.
- ScienceDirect abstracts (`S0952197625034293`, `S1270963824000610`, `S1474034625009693`, `S0141029625016098`) → HTTP 403; carried as search returns only.
- `WebFetch` tool and `curl`/`wget` → intercepted by a plugin shim that names MCP tools not present in this agent's toolset; routed around with `python3 urllib.request` (+ `zlib` PDF stream inflation). Recommend the orchestrator note this for future websearcher runs.
- Query `auxiliary data improves optimization not identifiability ...` → returned auxiliary-task and nonlinear-ICA identifiability literature, not the matched-experiment framing; no usable result.
- Query `benchmark where parameter vector exactly determines PDE solution field ...` → all hits keep LF in the inference path; no usable result for the certified-completeness regime.

## For the brainstormer

1. **Quote the D1 verdict verbatim on any +/-LF measurement card.** The ablation genre is preempted (`https://arxiv.org/abs/2512.02868`, fetched); what is open is the four-clause composition — LF out of the test path, completeness-certified panel, copy-LF denominator, N_hf = 5 with a certified mce. Card the *number*, never the genre.
2. **Do not claim the rate-vs-information framing as an insight.** It is Lopez-Paz et al. 2016 (fetched): privileged information accelerates O(n^-1/2) -> O(n^-1). On a completeness-certified panel that framing *predicts* what the round should find — LF cannot add information about a target its condition already determines, so any surviving effect is sample-efficiency/optimisation. Write that as a **pre-registered expectation**, not a discovery.
3. **The D2 identifiability-vs-trainability discrimination must be phrased with the existing vocabulary** (statistical-to-computational gap; `https://arxiv.org/pdf/2502.04282`, fetched) and the optimisation channel must cite KD-as-partial-variance-reduction (`.../ee1f0da706829d7f198eac0edaacc338-Paper-Conference.pdf`, fetched). The novel part is the *measurement on cahn_hilliard*, where B4 already recorded the local-minimum-like signature (no-LF cosine 0.0003-0.0385 vs LF 0.962-0.964).
4. **If any distillation/teacher arm is proposed, it is D3 = `preempted` — baseline only**, and it must pre-register the documented PFD non-monotone failure (a *very* predictive privileged teacher makes the student *worse*). On the completeness-certified panel the LF teacher is highly predictive, so this is a live falsification risk, not a formality.
5. **Carry the negative-transfer citation** (`https://arxiv.org/abs/2410.12690`, fetched): LF worsening HF predictions is documented, so a certified *null or negative* LF effect on the honest panel is a publishable, literature-anchored result — consistent with program.md §3's "a certified null is a result".
6. **Anchor arithmetic to quote**: launch best-floor geomean **38.63**; the current best card on the round-3 panel is the round-2 **LF-coverage** arm `r2s3_lf_train_signal-B3` at geomean **16.7606** (CI [16.3658, 17.1555]) — so this stream's own predecessor is the bar; per-dataset floors and the mandatory ifc `affine_on_hf_train` arms (ifc_poisson 1.5938, ifc_heat 0.96) go on every card. Provisional mce values (r3s4 re-certifies): pfc 8.86, ac 16.42, fk 158.33, ch 1.16, ifc_poisson 0.24.
