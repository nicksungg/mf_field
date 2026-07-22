# Meta-Autoresearch — Can We Autoresearch the Autoresearch?

**Status:** analysis, for a go/no-go decision.
Not a spec.
**Date:** 2026-07-22
**Companion to:** `AUTORESEARCH_PLAN.md` (the inner loop this document proposes to optimize).
**Assumed engine:** Claude Fable 5 drives the process.

---

## 1. Three things "meta" could mean

The question collapses three different proposals that have wildly different costs and payoffs.
Separating them is most of the work.

| Level | What it searches over | What one evaluation costs |
|---|---|---|
| **L0 — offline strategy evaluation** | Proposal prompts, prior-art gates, dedup rules, scored against *artifacts that already exist* | Text-only. Minutes, no GPU. |
| **L1 — replay / surrogate benchmark** | Proposal *ranking* policies, replayed against the 30-family × 15-dataset result archive | Text-only. Hours, no GPU. |
| **L2 — live nested loop** | Full research strategies, each scored by running the inner loop end to end | ~100+ H100-hours **per meta-candidate** |

Almost everything interesting people mean by "autoresearch the autoresearch" is L2.
Almost all of the achievable value is in L0 and L1.
That gap is the finding of this document.

There is no L3.
A meta-meta loop searching over meta-loop configurations inherits every cost problem below, multiplied, and is not discussed further.

---

## 2. What the outer loop would actually search over

The inner loop in `AUTORESEARCH_PLAN.md` has roughly seven free parameters.
These are the meta search space.

1. **Proposal policy** — how the strategist generates candidate families.
   One-at-a-time CEO improvisation, batched fan-out of N, mutation of the current leader, or crossover between two archive entries.
2. **Prior-art gate** — retrieval depth, how many independent checks, what counts as "pre-empted," and the accept/reject threshold.
3. **Objective definition** — Elo, median relative-L2, sharpness-weighted composite, or a lexicographic combination.
4. **Acceptance rule** — how much CI overlap disqualifies an apparent win, and how many seeds buy that certainty.
5. **Exploration/exploitation split** — what fraction of each batch must be structurally unlike anything in the archive.
6. **Budget allocation** — cheap wide screening at low epochs versus few candidates at full protocol.
7. **Diagnostic scheduling** — when to stop proposing models and instead spend a cycle measuring something (e.g. the Phase 1 spectral diagnostic).

Item 7 is worth flagging early.
The single highest-value action in the current plan is a *measurement*, not a model, and it was identified by a human reading an audit.
Any meta-loop worth building needs to be able to propose "run a diagnostic instead of training something," and most meta-loop formulations structurally cannot — they only know how to propose candidates for the objective they were handed.

---

## 3. Why L2 does not survive contact with arithmetic

To compare research strategies you must score them, and the only honest score for a research strategy is "how good is the best model it found after K cycles."

Take the inner loop's own numbers.
Smoke eval is `ifc_heat` + `ifc_poisson` at 200 epochs, budgeted at ≤ ~30 min on one H100.
`AUTORESEARCH_PLAN.md` §2 requires CI-gated acceptance, which means multiple seeds per proposal — call it 3.
A batched cycle proposing N=5 families therefore costs roughly 15 H100-hours of compute, plus SLURM queue time and agent overhead.

One meta-evaluation is K cycles of that.
At K=8, one meta-candidate costs ~120 H100-hours.

Now the statistics.
The meta-outcome is a **maximum** over a handful of proposals — a max-statistic on a heavy-tailed distribution, dominated by whether one lucky candidate landed.
Distinguishing two strategies whose true difference is modest needs many repeats, not three.
At M=6 strategies × R=10 repeats you are looking at **~7,000 H100-hours**, roughly 10 months of one H100, before accounting for preemption on `mit_preemptable`.

The structural problem, stated plainly:

> The meta-objective has **worse** signal-to-noise than the inner objective and costs **100× more** per sample.

Nested optimization pays off when the outer signal is cheap or the inner loop is fast.
Neither holds here.

### 3.1 The comparison people reach for, and why it does not transfer

Automated-discovery systems that genuinely worked — FunSearch, AlphaEvolve, and the NAS-Bench line of surrogate benchmarks — share one property this project does not have: **verification is nearly free**.
FunSearch can score a candidate program in milliseconds, so it can afford millions of samples and a brutally noisy generator.
Here, verification costs an H100-hour and the answer still comes back inside a confidence interval.

That single difference is why the analogy fails, and it is also the constructive hint: the way to get a working search loop is not a better search algorithm, it is **a cheaper verifier**.
See §5.

*(These systems are cited from memory as leads, not verified claims — see §8.)*

### 3.2 The harness is not ready to be meta-optimized

`AUTORESEARCH_PLAN.md` §Phase 0 lists four defects in the current measurement: no variance estimate (F05), 11 families training on a loss that is not the scored metric (F19), the backbone not actually held constant despite the protocol claiming it is (F23), and three coexisting definitions of nRMSE (F01).

A meta-optimizer on top of that does not merely inherit the noise.
It is *better than a human-guided loop at finding metric exploits*, because that is precisely what optimizers do.
A broken harness is **more** dangerous at the meta level, not less.
Phase 0 is a hard prerequisite for L2 in a way it is not even for L1.

---

## 4. What is actually cheap — and worth doing

Three offline evaluations extract most of the meta-loop's value without a single GPU-hour.

### L0a — read the literature on automated research loops

The cheapest possible version of "autoresearch the autoresearch" is not optimization at all.
It is a Fable-driven literature scan of automated scientific discovery: The AI Scientist, ADAS / Meta Agent Search, FunSearch, AlphaEvolve, OpenEvolve, the NAS-Bench surrogate benchmarks, and the prompt-optimization line (DSPy, GEPA).

The question to put to that literature is narrow and answerable: *in which regimes did these loops beat a competent human-guided baseline, and what was the verification cost per candidate in each?*
If the honest answer is "only where verification was cheap," that settles L2 from evidence rather than from the arithmetic in §3.

Cost: hours of Fable time.
This should happen before anything else in this document.

### L0b — evaluate the prior-art gate directly

This is the highest expected value per unit cost of anything in either document.

`AUTORESEARCH_PLAN.md` §5 already identifies the prior-art gate as the loop's single most valuable component, and the track record is **0 for 4**: Candidate A (diffusion refiner) pre-empted by Bhola 2512.12749 / MFFM / CorrDiff, Candidate B (FNO↔WNO) by WLNO, Candidate C (cycle-consistency fusion) by Kim 2021, and the FNO→CNN hybrid by Park 2507.06133 / SINO.
Every one of those was discovered *after* write-up.

The gate is a text-in/text-out component, so it can be evaluated like any classifier.

- **Labeled set:** the 4 known-pre-empted candidates as positives, plus the ~30 zoo families whose source papers are recorded in their `INSPIRATION.md`, plus a handful of proposals believed novel at the time they were made.
- **Variants:** retrieval depth, single-check versus N independent checks, verdict threshold, and whether the checker sees the proposal's framing or only its mechanism.
- **Metric:** precision and recall against the labels, with the operating point chosen deliberately — a false negative wastes a full build-and-eval cycle, a false positive discards a real idea, and those costs are not symmetric.

Cost: roughly 40 labeled items × 10 gate variants × 3 repeats ≈ 1,200 Fable calls.
Hours, not weeks, and no GPU.

### L1 — replay proposal ranking against the existing archive

The repo already contains a small tabular benchmark: 30 families × 15 datasets of computed results, in `results/bench_elo.csv` and `results/bench_metrics.csv` on the cluster.
That is the NAS-Bench trick available for free.

Protocol: hide the top-K families, hand the strategist the remaining archive plus the repo's documentation, ask it to propose and rank what to try next, and score by how much of the held-out high-rank set it recovers and how early.

What this measures honestly: **prioritization**, not invention.
It can only reward proposals that already exist in the archive, so a strategy that invents something genuinely new scores zero.
That is a real ceiling and it should be stated whenever the numbers are quoted.

It still answers a question that matters: given everything already known, does the strategist rank sensibly, or does it need to be told?

Cost: text-only, but it depends on cluster artifacts (`results/bench_*.csv`, `results/history.jsonl`) that are gitignored and absent from this checkout.
Confirm they exist before scheduling this.

---

## 5. Where Fable fits, and the trap

Fable's advantage is throughput per dollar, which maps cleanly onto the parts of this problem that are text-shaped and high-volume.

**Good fits:** generating hundreds of candidate proposals so diversity can be measured before anything is built; first-pass prior-art triage; deduplication against the 30-family archive; running the L1 replay harness; and the L0a literature scan.

**Poor fit:** the final novelty verdict and the adversarial verification of an apparent win.
That is exactly where the loop has failed 4 times out of 4, and it is the step where being wrong costs a full cycle plus a written-up paper claim.

**The trap:** if Fable both generates proposals and judges their novelty, the gate is graded by the same model whose blind spots produced the proposal.
It will systematically pass its own failure modes.
The judge must be a *different* model, or — better — grounded in actual retrieval against the literature rather than model recall.
Note that the 4 known misses were all cases where the mechanism was published and the generating model did not surface it, which is precisely a recall failure, not a reasoning failure.

**The real leverage:** §3.1 concluded that the binding constraint is verification cost.
Fable does not lower the cost of a smoke eval.
It lowers the cost of everything *around* it — which is why the recommendation below is to point Fable at the offline tiers and leave the GPU budget under human control.

---

## 6. The strongest argument against, stated fairly

Suppose L2 were affordable.
It would still probably make this project worse, for a reason that has nothing to do with cost.

Look at the leaderboard.
Thirty families, 22 of them FNO-backboned, and the entire top 10 is FNO+transfer or FNO+FIRE variants of each other.
The #1 model differs from #8 by a single change: concatenation → FiLM conditioning.

That is not a project suffering from insufficient optimization pressure.
It is a project suffering from **insufficient diversity**, and a meta-optimizer scored on "best model found" will make that worse, not better.
Optimizers amplify exploitation.
Pointed at this archive, a meta-loop's honest conclusion is "propose more FiLM variants" — which is the direction the search is already stuck in.

The two open scientific questions in `NEW_MODELS_2.md` — is the bottleneck spectral truncation, or missing local representation? — are exactly the kind of question a hill-climbing meta-loop will never ask, because asking them costs a cycle and returns no leaderboard improvement.
`AUTORESEARCH_PLAN.md` §Phase 1 makes the same point from the other direction: a training-free spectral diagnostic could invalidate the entire hybrid-backbone premise for near-zero cost.

Cheap diagnostics beat expensive search.
A meta-loop that cannot propose "measure something instead" is optimizing the wrong layer.

---

## 7. Verdict

**L2 — live nested loop: no.**
Three independent reasons, any one of which is sufficient: the arithmetic in §3 puts it at months of H100 time for statistically weak conclusions; the harness defects in §3.2 mean it would hill-climb artifacts; and §6 argues it would push the search deeper into the region that is already mined out.

**L0a — literature scan on automated discovery loops: yes, first.**
Hours of Fable time, and it either confirms or overturns §3 from published evidence.

**L0b — prior-art gate evaluation: yes, highest priority of the concrete work.**
It targets the component already identified as most valuable, with a documented 0-for-4 failure record, and it is measurable offline with a labeled set that mostly already exists in the repo.
This is worth doing even if no autonomous loop is ever run, because the gate is equally necessary for human-generated candidates — and every candidate so far has been human-generated.

**L1 — replay harness: yes, but second, and quote it honestly.**
Cheap and informative about prioritization.
Blind to invention, which is the thing that actually matters here.
Contingent on the cluster artifacts existing.

**Overall:** the meta-question is worth asking and the answer is mostly "no, but the cheap version of it is the most valuable thing on the table."
The recursion terminates one level up from where the question implies, and that is a real result rather than a dodge.

---

## 8. Sequencing

1. **L0a literature scan** (Fable, hours) — does published evidence support automated research loops in expensive-verification regimes?
2. **L0b prior-art gate benchmark** (Fable, ~1,200 calls) — build the labeled set, measure precision/recall, pick the operating point.
3. **Confirm cluster artifacts** for L1 — `results/bench_elo.csv`, `results/bench_metrics.csv`, `results/history.jsonl`.
4. **L1 replay harness** if step 3 confirms.
5. **Revisit L2 only if** Phase 0 lands, Phase 1 reports headroom, and step 1 turns up a comparable success in a comparable cost regime.
   All three, not any one.

Steps 1 and 2 are independent of `AUTORESEARCH_PLAN.md` Phases 0 and 1 and can run in parallel with them.

---

## 9. Known unknowns

- The automated-discovery systems named in §4 (L0a) are cited from model recall, not verified against primary sources.
  Verifying them *is* step 1 — do not quote them as established until that runs.
- `results/bench_*.csv` and `results/history.jsonl` are gitignored and absent from this checkout; L1's feasibility depends on them existing in the cluster working tree.
- Only 21 of 30 families are present locally (inherits U03 from `AUTORESEARCH_PLAN.md`), so the L0b labeled set cannot be fully assembled from this checkout either.
- Whether `INSPIRATION.md` files record source papers consistently enough across all families to serve as prior-art labels is unverified.
- The dataset-count inconsistency (15 vs 17) noted as U02 propagates into any replay harness built on the archive.
- The per-cycle cost estimates in §3 are derived from the ≤30-min smoke budget in `CLAUDE.md` and the wall-time note in `HOWTO.md`, not from measured cycle timings in `results/history.jsonl`.
