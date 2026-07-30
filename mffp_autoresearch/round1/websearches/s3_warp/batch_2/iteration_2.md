# iteration_2 — pinning JUBW; the appearance term; joint vs sequential

## Search rationale

Iteration 1 left one unsourced snippet (JUBW) carrying the whole weight of the
"single-interpolation warp composition" question that B1 F17 forces on the
builder — pin it or drop it. Then the two remaining task questions: (b) what the
metamorphosis appearance channel actually does and whether the decomposition is
attributed per term, and (c) whether the literature's verdict on
alignment-then-correction is joint or sequential training (the s3-vs-s6 boundary).

## Search terms used

1. `"Joint Upsampling and Backward Warping" JUBW sub-pixel distances without interpolation`
2. `metamorphosis image registration appearance intensity term ablation how much error attributed deformation vs appearance topology change`
3. `alignment then refinement two-stage versus jointly trained end-to-end ablation flow warping restoration network`

## Findings

### Term 1 — JUBW PINNED, and it preempts B1 F17's remedy by nine years

The operation is from **Makansi, Ilg & Brox, "End-to-End Learning of Video
Super-Resolution with Motion Compensation" (GCPR 2017)**, arXiv:1707.00471.
Fetched abstract-level confirmation of the core claim: *"common off-the-shelf image
warping does not allow video super-resolution to benefit much from optical
flow"*, and the paper instead proposes *"an operation for motion compensation
that performs warping from low to high resolution directly"*
[cite: https://arxiv.org/abs/1707.00471 — fetched (abs page; the PDF was not
fetched, so the JUBW internals below are SEARCH-SNIPPET level, flagged)].

Snippet-level detail (not citation-grade, flagged): JUBW maps an HF pixel `p` to
LF source coordinates using HF flow at scale alpha=4, takes the **nearest LF
pixel with no interpolation at all**, and additionally emits the **x/y sub-pixel
distances to the source pixel centre as extra channels**, leaving the
interpolation to the network; and the motivating sentence is almost verbatim
B1 F17: *"traditional approaches follow the practice of first upsampling and then
warping the images, and both operations involve interpolation during which image
information is lost"*, with the claim that JUBW *"yields sharper and more
accurate reconstruction"* than alternative warping.

This is the single most important finding of this batch: **"do the warp and the
upsample in one interpolation, because doing them in two destroys information"
is published, named, and ablated in video SR (2017)**, on top of iteration 1's
SRWarp (CVPR 2021) and LTEW (ECCV 2022). Any D1 card must cite it and cannot
claim the composition as its contribution.

### Term 2 — the appearance term: disentanglement is a known open problem, attribution is NOT reported

- **MetaMorph** (arXiv:2303.04849) and **MetaRegNet** (arXiv:2303.09088) are the
  learned metamorphosis pair batch 1 already found; the framing confirmed here
  is that metamorphosis has **two components — a geometric deformation moving
  intensities, and a deformation of the intensity values themselves, which is
  what allows a NEW STRUCTURE to appear** [cite: search-result descriptions over
  https://arxiv.org/pdf/2303.04849 , https://arxiv.org/pdf/2303.09088 ;
  classical source https://arxiv.org/abs/1806.01225 ,
  semi-Lagrangian scheme https://arxiv.org/pdf/2106.08817].
- The known failure mode is exactly the one that would bite us: *"existing
  metamorphic image registration methods struggle with balancing between the
  effects of appearance vs. geometric changes"* — the intensity channel can
  absorb work that should have been done by the diffeomorphism.
- The published fix is **Weighted Metamorphosis** (François et al. 2022), which
  restricts the metamorphic intensity additions with a **time-varying spatial
  weight function** to "improve the disentanglement between anatomical (shape)
  and topological (appearance) changes" [cite:
  https://www.researchgate.net/publication/361870973_Weighted_Metamorphosis_for_Registration_of_Images_with_Different_Topologies ,
  https://openreview.net/forum?id=rAfgDXR35CY — **fetch failed** (OpenReview
  returned a browser-verification page; ResearchGate not fetched). Snippet-level
  only.]
- **No fetched source reports a quantitative per-term attribution** (how much of
  the residual the appearance channel owns vs the diffeomorphism). The search
  engine's own summary says as much. Deep-registration survey
  https://arxiv.org/pdf/2307.15615 is the place to look for evaluation practice
  (iteration 3).

### Term 3 — joint vs sequential: the literature is genuinely split, and it ablates it

- **Against joint**: DrivingScene reports that replacing its two-stage training
  with single-stage end-to-end training *"leads to substantial performance
  degradation"* [cite: https://arxiv.org/pdf/2510.24734 (search result)].
- **For joint**: a ToF RGB-D alignment+refinement pipeline reports end-to-end
  (differentiable-warp) learning beating the non-differentiable two-stage
  variant by 0.12 dB [cite: https://arxiv.org/pdf/1909.07623 (search result)];
  Merging-ISP explicitly studies subtasks-separately vs end-to-end [cite:
  https://arxiv.org/pdf/1911.04762 (search result)].
- **Structure of the compromise**: F2HDR is two-stage with a *flow adapter* that
  turns generic optical flow into a task-adaptive motion field before the
  refinement stage, and its ablation says removing the flow adapter is the worst
  configuration, i.e. *"high quality flow maps serve as a solid foundation for
  the refinement stage"* [cite: https://arxiv.org/html/2603.14920v2 (search
  result)]. EDVR is the canonical alternative that dispenses with explicit flow
  entirely and aligns with deformable convolutions inside a jointly trained net
  [cite: https://arxiv.org/pdf/1905.02716 (search result)].

## Interpretation

The composition that B1 F17 makes mandatory (single interpolation, warp fused
with the upsample) is published prior art with a name (JUBW, 2017) and two later
relatives (SRWarp, LTEW) — it is an implementation obligation for us, not a
claim. The appearance/intensity term is well-founded but its *disentanglement* is
an acknowledged open problem with no published per-term attribution, which both
weakens "add a metamorphosis term" as a design move and makes B1's
scope-instead-of-metamorphosis decision the defensible one. Joint vs sequential
has no field-wide verdict — which means the D1 card must decide it by control
arm, not by citation, and the cheapest published pattern (F2HDR/JUBW) is
*differentiable warp trained jointly with the corrector, with the displacement
head given its own supervision-shaped inductive bias*.
