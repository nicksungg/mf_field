# Iteration 3 — direction 4: is the nested-ladder all-pairs degeneracy reported?

## Search rationale

This is the ONE direction in batch 4 where a real novelty check matters. B3-T1-F1
claims that on an aligned/nested ladder, `allpairs` cross-level rows are *exact*
duplicates of the self rows (cond max|diff| 0.0, target max|diff| 0.0, 6/6
pairs) — so "all-ordered-pairs fidelity augmentation" is pure replication and
carries zero extra supervision. Before the round report states that as an
unreported observation, I must try to refute it.

I first grounded the claim in the family's own provenance:
`mf_field/akash/models/mf_fno_allpairs/manifest.json` (read directly) says
`"inspired_by": ["herde2024poseidon", "perez2018film"]` and describes itself as
"POSEIDON all2all recast onto a fidelity ladder ... All-pairs training amplifies
the data O(L^2)". So the right refutation targets are (a) POSEIDON's own
statement of *why* all2all amplifies data, and (b) any MF paper noting the
aligned/nested-ladder degeneracy directly.

## Search terms used

1. `POSEIDON foundation model PDE all2all training strategy time pairs data amplification trajectory`
2. `multi-fidelity training all pairs of fidelity levels nested aligned samples duplicate targets redundant cross-level supervision`
3. `all-pairs fidelity augmentation degenerate identical inputs low and high fidelity same parameters duplicate training rows operator learning`

## Findings

### Term 1 — POSEIDON's all2all (the source the family cites)

Top-5: emergentmind summary (https://www.emergentmind.com/papers/2405.19101);
OpenReview (https://openreview.net/forum?id=JC1VKK3UXk, dead route);
arXiv abs (https://arxiv.org/abs/2405.19101); ACM DL
(https://dl.acm.org/doi/10.5555/3737916.3740227); NeurIPS poster page.

**FETCHED (attempt 1)** https://arxiv.org/abs/2405.19101 — abstract only: "A
novel training strategy leveraging the semi-group property of time-dependent
PDEs to allow for significant scaling-up of the training data." Insufficient.

**FETCHED (attempt 2, ar5iv)** https://ar5iv.labs.arxiv.org/html/2405.19101 —
the body:

> the solution operator "possesses a *semi-group property*"

> the strategy creates training pairs where an initial condition at intermediate
> time t_k becomes the input and the solution at a later time t_kbar becomes the
> target

> it generates "quadratic O(K^2) samples per trajectory, when compared to the
> linear K samples" of standard training (K-hat = (K+1)(K+2)/2 pairs).

(An `arxiv.org/html/2405.19101v3` attempt returned HTTP 404 — logged as a dead
end; ar5iv is again the working route, as batch 3 found.)

**This is decisive for the mechanism, and it is a refutation of the family's own
description, not of B3.** POSEIDON's O(K^2) amplification is real *because each
(k, kbar) pair has a DIFFERENT INPUT* — the input is the solution field at time
t_k, which varies with k. The semi-group property is what makes the map from
t_k to t_kbar a genuinely different learning target for each k. In the
fidelity-ladder recast, after B2's `cond_from = target` correction, the input is
the condition vector X of the *target* row, so it does **not** vary with f_src;
only a scalar tag does, and the target field is by construction the same row.
The premise POSEIDON's amplification rests on is therefore *absent* in the
recast. B3-T1-F1 is the empirical confirmation of a structural fact that follows
from POSEIDON's own stated mechanism.

### Term 2 — MF literature on nested/aligned designs

Top-5: MF-GP surrogate topic page (emergentmind); SMT MFK docs
(https://smt.readthedocs.io/en/latest/_src_docs/applications/mfk.html);
MF-GP for regression in physics (https://arxiv.org/pdf/2404.11965); Data
Hierarchies in Multifidelity ML (https://arxiv.org/pdf/2410.11392); MF survey
for functional outputs (https://arxiv.org/pdf/2408.17075).

**No usable results** for the degeneracy claim. The nested/non-nested axis IS
discussed throughout the MF literature (search-return: "Not all multi-fidelity
strategies depend on nested data ... recursive AR(1) GPs can accommodate
arbitrary non-nested training locations"), but always as a question of *which
estimator is applicable*, never as "cross-level training pairs on a nested
design are duplicates". No fetch was made: every top hit was `arxiv.org/pdf`
(dead route) or an aggregator page, and none of the returned snippets was
close enough to be worth a fetch budget.

### Term 3 — the degeneracy stated directly, in operator learning

Top-5: Flow-matching operators (https://arxiv.org/pdf/2512.12749);
Discretization-independent multifidelity operator learning
(https://arxiv.org/pdf/2507.07292); MF-DeepONet
(https://arxiv.org/pdf/2503.17941 / html v1); l1-regularized bi-fidelity
(ScienceDirect, dead route); MF deep neural operators (APS).

**FETCHED** https://arxiv.org/html/2503.17941v1 (Physics-Guided Multi-Fidelity
DeepONet). This is the closest the literature gets, and it is **the opposite
concern**. The paper treats LF-HF alignment as a *constraint to be removed*:

> "preservation of DeepONet's inherent query flexibility by removing the
> requirement for low-fidelity and high-fidelity datasets to share identical
> function inputs or spatio-temporal query points"

> "This coupled architecture introduces significant computational limitations,
> ... requires identical query points for both branch inputs ... across
> different fidelity levels."

So the literature's complaint about aligned/nested MF data is **flexibility**
("we should not be forced to have aligned data"), not **degeneracy** ("if the
data IS aligned, all-pairs supervision collapses to replication"). The
search-return for 2507.07292 repeats the same flexibility framing.

Nothing found stating that a nested ladder makes cross-level pairs duplicates.

## Interpretation

Direction 4 survives the refutation attempt: the *mechanism* POSEIDON's O(K^2)
amplification depends on (input varies with the source index) is published and
fetched (https://ar5iv.labs.arxiv.org/html/2405.19101), and the MF literature
discusses nested vs non-nested designs — but **no fetched source states that
all-pairs / cross-level fidelity supervision on an aligned ladder degenerates
into pure replication**. The nearest neighbour treats alignment as an unwanted
requirement, not a source of degeneracy. This is an observation about a
*construction*, not a new method, so the right framing is "not previously
reported (narrow)", never "novel method".
