# iteration_4 — `r2s3_lf_train_signal`, batch 1

## Search rationale

Field context is now sufficient (§3.2 rule: `ENOUGH` — three turns have mapped
the distillation, joint/composite-MF, and curriculum branches, and the last
turn's marginal returns were mostly repeats). This turn switches to §3.3:
targeted **refutation** searches, one per candidate direction I expect the
brainstormer to propose for r2s3-B1. The directions are derived from
program.md §12.3's three named mechanisms, filtered by the on-disk ladder
structure recorded in `summary_so_far.md` (sharp = nested, ifc_poisson =
disjoint LF conditions):

- **D1** — LF-consuming teacher → condition-vector-only student distillation
  (teacher absent at test; §5.10b declared reuse).
- **D2** — nested multi-resolution auxiliary targets: shared condition→latent
  trunk with extra heads regressing the l1/l2 coarse *solve* fields, heads
  discarded at test.
- **D3** — LF-as-parameter-coverage: exploit ifc_poisson's 100/50/20 LF samples
  at conditions **disjoint** from the 5 HF ones (multilevel / telescoping-style
  gradient or coverage pretraining).

## Search terms used

1. `distill neural operator teacher that consumes low-fidelity field into student predicting from parameters only`  → refute D1
2. `auxiliary task predict coarse-grid solution same parameters regularize surrogate discard auxiliary head at test time` → refute D2
3. `multilevel Monte Carlo training neural operators telescoping gradient coarse resolution control variate` → refute D3

## Findings per term

### Term 1 (D1 refutation attempt)

- No paper found that distils a **field-consuming MF teacher into a
  condition-vector-only student**. The search engine explicitly said so:
  "If you're looking for a specific paper on distilling operators where the
  teacher consumes low-fidelity field data while the student predicts from
  parameters only, you may want to search for more specific author names."
- Nearest neighbors returned:
  - **Multi-fidelity prediction of fluid flow and temperature field based on
    transfer learning using Fourier Neural Operator** —
    https://arxiv.org/pdf/2304.06972 . Search snippet: "pre-training of the
    low-fidelity model, and fine-tuning of the high-fidelity model, where the
    parameters of the low-fidelity model are migrated as the initial parameters
    of the high-fidelity model… due to the mesh-invariance of FNO the network
    parameters can be directly transferred." (WebFetch failed:
    `maxContentLength size of 10485760 exceeded` — snippet only, not full text.)
    This is *published external prior art for the exact recipe of the mandatory
    declared baseline* `mf_fno_transfer_film` — an undifferentiated
    LF-pretrain→HF-finetune proposal is preempted both in-repo (§12.3) and in
    the literature.
  - Consistency-distilled flow matching for physical fidelity reconstruction —
    https://arxiv.org/pdf/2605.05975 : student distilled from a flow-matching
    *teacher of the same input type*; a compression distillation, not a
    modality/fidelity-asymmetry distillation.
  - The ScienceDirect EAAI paper from iteration 2
    (https://www.sciencedirect.com/science/article/abs/pii/S0952197625034293)
    remains the only work occupying the privileged-modality→primary-input
    surrogate slot, and its privileged modality is "full-field simulation
    outputs" — which is *not* established to be a coarse solve of the same PDE,
    and whose student input/output types are unresolved behind the paywall.

### Term 2 (D2 refutation attempt)

- **No usable results for the PDE-surrogate instance.** The auxiliary-head
  literature returned is generic deep supervision (auxiliary heads at multiple
  feature-pyramid levels, removed at inference — e.g. PP-OCRv6
  https://arxiv.org/pdf/2606.13108 ; FMCE-Net++ https://arxiv.org/pdf/2508.06109 ;
  auxiliary-task reweighting for minimum-data learning
  https://proceedings.neurips.cc/paper/2020/file/4f87658ef0de194413056248a00ce009-Paper.pdf).
  The mechanism "auxiliary head trained then discarded at test acts as a
  regularizer" is thoroughly established **in general ML**.
- The one PDE-adjacent statement in the synthesis — "inspired by the multi-grid
  method, a coarse solution obtained from a PDE solver can be reused as
  auxiliary **pre-training labels**" — could not be attributed to any fetched
  paper in this turn and is therefore **NOT citable**; it is however a warning
  that the idea exists somewhere and a batch-2 search should chase it.
- Also returned: multi-objective/multi-task collocation PINN with
  student/teacher transfer learning — https://arxiv.org/pdf/2107.11496 (PINN
  collocation multi-task, not multi-fidelity target heads).

### Term 3 (D3 refutation attempt)

- **[MAJOR] Rowbottom, Fresca, Liò, Schönlieb & Boullé, "Multi-Level Monte Carlo
  Training of Neural Operators"** — https://arxiv.org/abs/2505.12940 (also
  https://arxiv.org/html/2505.12940 ; CMAME version
  https://www.sciencedirect.com/science/article/pii/S0045782526000745 ; Cambridge
  repository record
  https://www.repository.cam.ac.uk/items/de988071-9631-4e30-9bd5-53353d7c527d ).
  FETCHED (abstract page). Estimates the finest-resolution gradient expectation
  as a **telescopic sum over mesh levels**: a coarse mesh captures most of the
  gradient variance, finer meshes correct the remainder, so fewer fine-resolution
  samples are needed. Fetch findings: the abstract does **not** state whether
  samples must be paired/nested across levels; the demonstrated benefit is
  "improved computational efficiency… while maintaining a high level accuracy" —
  i.e. **cost reduction at comparable accuracy, not accuracy improvement when
  fine data is scarce**; input type (field vs parameter vector) unspecified in
  the abstract. Reported deliverable is "a Pareto curve between accuracy and
  computational time."
  This is the same [LF-10] the in-repo report flagged; I have now retrieved it
  first-hand.
- Multiscale Training of CNNs / Multiscale Gradient Estimation —
  https://arxiv.org/abs/2501.12739 : the same telescoping idea for CNNs, again
  framed as achieving equal variance with fewer fine-mesh convolutions (cost).
- Multilevel Control Functional — https://arxiv.org/html/2305.12996 : MLMC
  variance reduction, not operator training.

## Prior-art verdict (§3.3)

| Direction | Verdict | Basis (fetched/returned THIS loop) |
|---|---|---|
| **D1** — distil an LF-consuming MF teacher into a condition-vector-only student that predicts the HF field | **preempted-but-MF-composition-open** | The general "privileged auxiliary modality (incl. full-field simulation outputs) distilled at the representation level into a deployment-input-only student surrogate" is published: EAAI Dec 2025, https://www.sciencedirect.com/science/article/abs/pii/S0952197625034293 (abstract returned twice by search; WebFetch 403 both URL forms). The LUPI framing itself is classical (Vapnik & Izmailov, https://www.researchgate.net/publication/301362871_Learning_using_privileged_information_Similarity_control_and_knowledge_transfer) and 2026-active (https://arxiv.org/abs/2602.04942, LM domain, which calls the train→test PI transfer gap "a fundamental challenge"). **Still open**: no retrieved work makes the privileged modality a *coarse consistent solve of the same PDE*, with a *condition-vector-only* student emitting a *full field*, at N_hf = 5; and a targeted search for exactly that (term 1 this turn) returned nothing. Any r2s3 D1 card must cite the EAAI paper and claim only the MF composition. |
| **D2** — nested multi-resolution auxiliary target heads (regress l1/l2 coarse solves from the same condition; discard heads at test) | **preempted-but-MF-composition-open** | Deep-supervision auxiliary heads discarded at inference are standard ML (term 2 hits above). Composite MF networks that predict the LF value from the parameter input and compose an HF correction are preempted by Meng & Karniadakis, https://arxiv.org/abs/1903.00104 (iteration 3, fetched) and the MF-DeepONet line (https://dl.acm.org/doi/10.1016/j.jcp.2023.112462, https://arxiv.org/pdf/2310.00057). **Still open**: those compose LF into the HF *prediction path*; the auxiliary-target variant keeps the LF heads strictly out of the test-time path and uses them only as a representation regularizer on a **fully nested** ladder (identical conditions, differing only by grid truncation), for which no work was retrieved. The honest information claim is narrow — https://arxiv.org/html/2604.20061v1 (fetched) warns coarse-graining causes "irreversible information loss", so the only thing the l1/l2 targets can add is a spectral-truncation/curriculum prior, not new content. |
| **D3** — exploit ifc_poisson's LF samples at conditions disjoint from the HF ones (extra parameter-space coverage: 170 LF vs 5 HF) | **novel** (nearest neighbor cited) | Nearest neighbor is MLMC training of neural operators, https://arxiv.org/abs/2505.12940 (fetched) and multiscale gradient estimation, https://arxiv.org/abs/2501.12739 — both telescoping estimators over a mesh hierarchy whose stated payoff is *computational cost at equal accuracy*, on a resolution hierarchy of the same problem. Neither addresses the case where the coarse level covers **different parameter values** than the fine level, which is the only place in this panel where LF adds genuine information (verified on disk: none of the 5 HF condition rows appears in the f8/f32 sets). No retrieved work reports a matched with/without-LF ablation at N_hf ≈ 5 for field prediction (iteration 3 term 3: no usable results). |

Note: iteration cap is 5; this is turn 4 and the verdict work is complete, so the
loop stops here rather than spending turn 5.

## Interpretation

Every mechanism §12.3 names has a published ancestor, but none of the ancestors
is in this regime (condition-vector-only student, full-field output, N_hf = 5,
nested-vs-disjoint ladder asymmetry). The strongest genuinely-open claim is D3's
coverage argument on ifc_poisson plus the value-of-LF ablation itself; D1 and D2
are proposable only with an explicit "preempted-but-MF-composition-open" citation.
