# Iteration 4 — targeted refutation of the B4 candidate directions

## Search rationale

Prior-art verdict work (§3.3). The three directions the B4 card is likely to
propose, from `experiment_cards/s1_poisson/batch_3/B3.json` part 7
`next_direction` and the orchestrator's B4 brief:

- **D-A** — the disambiguation itself: allpairs-dedup arm (duplicates removed →
  self_only's data at allpairs' step count) + step-matched self_only (epoch
  scaling) + frozen controls, to split effective-N/weighting from optimization
  budget.
- **D-B** — make an explicit per-level row-WEIGHT knob the mechanism under test
  (`allpairs` = 1+#levels-below as the control, `self_only` = natural).
- **D-C** — report the nested-ladder replication finding (B3-T1-F1/T1-F2) as a
  round-level observation about the `allpairs` construction.

Each term below is chosen to REFUTE, not to support: D-B is refuted if per-level
loss weighting in MF training is already a studied knob (I expect yes); D-A is
refuted if the confound-attribution/step-matching genre is published (I expect
yes); D-C is refuted if any source states the degeneracy (iteration 3 found
none; term 3 here is a second, differently-worded attempt).

## Search terms used

1. `multi-fidelity neural network per-level loss weighting weight high fidelity samples more few high-fidelity data upweighting`
2. `reported gain attributed to confound rather than proposed mechanism revisiting ablation deep learning attribution of improvement`
3. `fidelity embedding single network trained on all fidelity levels same design points effective sample size replication nested experimental design`

## Findings

### Term 1 → D-B: per-level loss weighting in MF training

Top-5: MF-BPINN with adaptive residual learning
(https://arxiv.org/html/2602.01176v1); Ensemble adaptive gated MF NN
(ScienceDirect, dead route); Multifidelity DeepONets
(https://arxiv.org/pdf/2204.09157); MF Residual Neural Processes
(https://arxiv.org/pdf/2402.18846); MF data fusion in conv encoder/decoders
(https://arxiv.org/pdf/2205.05187).

**FETCHED** https://arxiv.org/html/2602.01176v1 — per-fidelity loss weighting is
explicit and standard there:

> "L_total = L_LF + λ_HF L_HF + λ_r L_residual + λ_b L_BC + λ_IC L_IC"

> "we monitor the gradient norms of each component and adjust the weights so
> that no single term persistently dominates"

> "This simple normalization is especially important in multi-fidelity
> settings, where the model must reconcile abundant low-fidelity supervision
> with scarce high-fidelity labels."

Search-return (not fetched, recorded as such) adds concrete schedules from the
same result set: "sets the highest fidelity weight to 2 and lower fidelities to
1"; "a lower fidelity weight of 0.25 can further improve performance"; and the
directly relevant negative: upweighting HF samples "showed some improvements in
final high-fidelity accuracy, though results were not consistently better than
with equal penalties across different network weight initializations."

**D-B is preempted as a method.** Per-fidelity loss weights — including
explicitly upweighting the scarce HF level, which is exactly what `allpairs`'s
2.5× share does — are a standard MF-training knob with published weight values.

### Term 2 → D-A: is confound-attribution a published methodology?

Top hits were mostly medical "ablation therapy" noise (a term collision). The
productive return, after the search engine's own re-queries, is **Troubling
Trends in Machine Learning Scholarship** (https://arxiv.org/pdf/1807.03341).

**FETCHED** https://ar5iv.labs.arxiv.org/html/1807.03341 (ar5iv route):

> "Too frequently, authors propose many tweaks absent proper ablation studies,
> obscuring the source of empirical gains."

> "Recently, Melis et al. demonstrated that a series of published improvements,
> originally attributed to complex innovations in network architectures, were
> actually due to better hyper-parameter tuning."

> "In contrast, many papers perform good ablation analyses, and even
> retrospective attempts to isolate the source of gains can lead to new
> discoveries."

Combined with iteration_2's https://arxiv.org/html/2606.10321v1 (the 8×
updates/epoch confound and its two matched controls), **D-A is fully preempted
as methodology** — and named as a *duty*, not an innovation. The literature
also supplies the modern instance genre: "Bilevel Graph Structure Learning,
Revisited: Inner-Channel Origins of the Reported Gain"
(https://arxiv.org/pdf/2605.07577, search-return from iteration_2, not fetched).

### Term 3 → D-C: second refutation attempt on the degeneracy claim

Top-5: MF learning for atomistic models via trainable data embeddings
(https://publica.fraunhofer.de/handle/publica/497533 and
https://iopscience.iop.org/article/10.1088/2632-2153/ae0d41); high-fidelity
graph interatomic potentials (https://arxiv.org/html/2409.00957v1); General
Multi-Fidelity Framework for Training ANNs
(https://www.frontiersin.org/journals/materials/articles/10.3389/fmats.2019.00061/full);
Active Learning for a Recursive Non-Additive Emulator
(https://arxiv.org/pdf/2309.11772).

**No usable results** for the degeneracy claim. Fidelity-embedding /
fidelity-conditioned joint training across levels is well established
(search-return: "An embedding layer maps datasets of different fidelity levels
to respective feature representations"), and it is precisely the architecture
class the `allpairs` family belongs to — but every source frames the benefit as
*more data from cheaper levels*, and none discusses what happens to the row set
when the levels share design points. No fetch spent: none of the returned
snippets came close enough to be worth the budget, and the two most promising
venues (Fraunhofer publica, IOPscience) are outside the batch-3 verified route
list.

## Interpretation

D-A and D-B are **preempted as ML-general / MF-general methods** — which is the
expected and acceptable outcome for a measurement-hygiene batch; the citations
above are what the card should quote to justify the DESIGN, not to claim
novelty. D-C survives a second refutation attempt: two independently worded
searches (iteration_3 term 3, iteration_4 term 3) plus the MF-nested-design
search of iteration_3 term 2 found no source stating the nested-ladder
all-pairs degeneracy. Stopping here (4 of 5 iterations); a fifth turn would be
a third rewording of the same refuted query, and I have retrieval-grounded
verdicts for all four scope directions.
