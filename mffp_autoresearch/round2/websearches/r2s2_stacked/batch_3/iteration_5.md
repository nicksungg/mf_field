# Iteration 5 (FINAL — iteration cap 5 reached) — REFUTATION pass on directions (ii) and (iii), and the verdicts

## Search rationale

Iteration 4 refuted-tested direction (i). This turn does the same for the other two candidate directions the
brainstormer may propose out of `experiment_cards/r2s2_stacked/batch_2/B2.json` part 7:
**(ii)** re-run allen_cahn's gated-CNN increment under the round's 1+2-seed protocol as the decider for whether
the stacked class needs a network at all, and **(iii)** close the stream, exporting the closed-form filter as
the zero-parameter bar every other stream's learned corrector must beat. Both are methodology claims, so the
refutation target is "is this protocol/bar already the field's published practice?".
This is the 5th of the allowed 5 iterations — **cap hit**; no further searching.

## Search terms used

1. `zero-parameter training-free baseline as mandatory benchmark bar neural operator evaluation must beat`
2. `neural network component contributes nothing after proper out-of-fold evaluation multi-fidelity surrogate negative result`
3. `re-running single dataset improvement multiple seeds decide keep or remove learned module protocol machine learning`

## Findings

### Term 1 — zero-parameter baselines as the bar

Snippet-level (no safe fetch: the primary source is a NeurIPS proceedings PDF and PDFs are a standing dead end
in this stream). NAS-Bench-Suite-Zero
https://proceedings.neurips.cc/paper_files/paper/2022/file/b3835dd49b7d5bb062aecccc14d8a675-Supplemental-Datasets_and_Benchmarks.pdf:
*"simple baselines such as 'number of parameters' and 'FLOPS' are competitive with all existing zero-cost
proxies across most settings"*, and *"many zero-cost proxies are unable to demonstrate consistently a higher
correlation with final accuracy than the trivial baseline"*. Also returned: NEAR https://arxiv.org/html/2408.08776v1;
training-free NAS review https://www.sciencedirect.com/science/article/pii/S2405959523001443 (403);
Neural Operators as Efficient Function Interpolators https://arxiv.org/pdf/2605.07792.
Reading: "publish the trivial/zero-cost baseline as the bar new methods must clear" is established practice
in a neighbouring subfield; combined with the **fetched** SciML citation from iteration 2
(https://arxiv.org/abs/2508.05831, closed-form rank-constrained optimal linear maps offered as *"a robust
baseline for understanding and benchmarking learned neural network models for scientific machine learning"*),
direction (iii)'s framing is preempted as a *practice*.

### Term 2 — published "the network added nothing" negatives in MF surrogates

**No usable results.** The search engine reported explicitly that the returned MF-surrogate papers *"don't
specifically contain the negative result you're searching for"*. Everything returned is a positive-result MF
neural method: Bayesian NN MF surrogate https://arxiv.org/pdf/2312.02575; MF residual neural processes
https://arxiv.org/pdf/2402.18846; residual MF neural network computing
https://link.springer.com/article/10.1007/s10543-025-01058-9; co-kriging→MF-NN for composites
https://arxiv.org/html/2605.02871v1; MF LSTM https://www.sciencedirect.com/science/article/abs/pii/S0045782522007678 (403).
Reading: the *negative* — "under out-of-fold selection the learned MF stage is switched off and a closed-form
stage carries the gain" — has no published counterpart found in two loops of searching (this term plus
iteration 3 term 3). That is the surviving open content for BOTH directions (i) and (iii).

### Term 3 — multi-seed protocol as the keep/remove decider

**FETCHED (abstract extracted this loop)** — Du, "…paired multi-seed evaluation protocol" arXiv:2511.19794
https://arxiv.org/abs/2511.19794: *"Recent machine learning papers often report 1-2 percentage point
improvements from a single run… It is therefore unclear when a reported +1-2% reflects a real algorithmic
advance versus noise. We propose a simple, PC-friendly evaluation protocol based on paired multi-seed runs,
bias-corrected and accelerated (BCa) bootstrap confidence intervals, and a sign-flip permutation test on
per-seed deltas… With only three seeds, our paired protocol never declares significance in these settings."*
This is **already the round's own protocol**: `state/noise_floor.json._protocol` cites
`paired_per_seed_deltas: "Du, arXiv:2511.19794"` and reports `sign_flip_p` / `paired_null_95` per dataset.
So direction (ii) is not proposing a new protocol — it is applying the round's certified one, and the fetched
source warns that with 3 seeds a paired test may **never** declare significance, which the brainstormer must
pre-register (the honest decision rule has to be "increment vs the certified per-dataset
`min_claimable_effect` = 0.8797 skill units on allen_cahn", not "paired significance").

**FETCHED** — "On the limitation of evaluating machine unlearning using only a single training seed"
https://arxiv.org/abs/2510.26714: *"this practice can give non-representative results as unlearning performance
can be sensitive to the choice of training seed… We also explain why increasing the number of unlearning seeds
cannot generally compensate for the lack of multiple training seeds."*
Reading: directly transferable to B2's exposure — the allen_cahn 9.443-unit increment is one **fold** seed and
one fit; re-seeding only the corrector fit (analogous to "unlearning seeds") does not substitute for varying
the fold/train seed. Direction (ii)'s design must vary the fold seed, not just the init seed.

## Prior-art verdicts (§3.3)

**Direction (i) — promote `k-NN average of train LF pool at k* -> one closed-form LSI Wiener filter` to a
first-class SCORED panel arm.**
Verdict: **`preempted-but-MF-composition-open (cite)`**.
Preempted parts, all fetched this loop: closed-form least-squares LF→HF correction with the LF model as a
regression basis (LS-MFS, https://arxiv.org/abs/1705.02956); closed-form/POD-projected multifidelity linear
regression on **field outputs with <= 10 HF samples** (https://arxiv.org/abs/2508.08517); band-wise
amplification of attenuated high-frequency content in operator surrogates (HFS,
http://arxiv.org/abs/2503.13695; diagnosis in https://arxiv.org/abs/2602.19265); k-NN/analogue averaging of
training fields as the retrieval intermediate (analogue downscaling family, snippet-level, Gangopadhyay et al.
2005 https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2004WR003444, fetch 403); shrinkage-gated
stagewise residual correction over a cheap base predictor with validation-selected weights
(Operator Boosting, https://arxiv.org/abs/2606.17460).
Open: no fetched source composes *retrieval intermediate → one fitted LSI (Fourier-diagonal) transfer* as a
**multi-fidelity** corrector, scores it against a **copy-LF-skill** denominator with no LF at test, or reports
the attribution that the closed-form stage carries 33-100 % of a trained stack's out-of-fold gain. Claim the
composition + attribution; never the filter.

**Direction (ii) — re-run allen_cahn's gated-CNN increment at the 1+2-seed protocol as the keep/kill decider.**
Verdict: **`preempted (cite)`** as a method — and that is fine, because it is a *measurement*, not a claim.
Citations: Du https://arxiv.org/abs/2511.19794 (paired multi-seed + BCa + sign-flip on per-seed deltas; already
the round's certified protocol in `state/noise_floor.json._protocol`);
https://arxiv.org/abs/2510.26714 (multiple *training* seeds are not substitutable by re-seeding the downstream
step); https://arxiv.org/abs/2406.10229 (seed variance decides whether a difference is meaningful);
https://arxiv.org/abs/2606.17460 (per-cell "does the learned residual stage pay?" decided against confidence
intervals across 30 dataset-architecture pairs — the exact decision this direction re-runs);
Super-Learner/NNLS vocabulary for a zero out-of-fold weight (https://www.biorxiv.org/content/10.1101/172395v1.full,
https://doi.org/10.1177/1536867x231212426, snippet-level).
Open: nothing methodological. What is open is the *answer* on this panel.

**Direction (iii) — close the stream; export the closed-form filter as the zero-parameter bar.**
Verdict: **`preempted (cite)`** as a framing; open only as the artefact + measurement.
Citations: https://arxiv.org/abs/2508.05831 (*"closed-form, rank-constrained linear and affine linear optimal
mappings… a robust baseline for understanding and benchmarking learned neural network models for scientific
machine learning"*, with a shallow-water PDE experiment);
https://www.nature.com/articles/s41592-025-02772-6 (*"None outperformed the baselines, which highlights the
importance of critical benchmarking"*) plus its published rebuttal
https://www.biorxiv.org/content/10.1101/2025.10.20.683304.full.pdf (the metric decides the verdict);
NAS-Bench-Suite-Zero (snippet-level) for "the trivial baseline is the bar".
Open: the specific bar — an LF-derived, retrieval+LSI, **zero-gradient** predictor scored on the round's
copy-LF-skill panel — does not exist in any fetched source, and the Nature-Methods rebuttal pair is the
strongest available warning that the bar must be published **in the round's claim unit (skill units vs the
certified `min_claimable_effect`)**, which is exactly B2's own H-RULE-UNITS finding.
