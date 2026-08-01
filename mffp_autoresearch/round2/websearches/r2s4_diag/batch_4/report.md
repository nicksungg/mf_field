# Websearch Report — Stream `r2s4_diag`, Batch 4

**Stream**: `r2s4_diag` (class: diag)
**Batch**: 4
**Total iterations**: 5 (cap = 5, **respected**; batch 3's 6-turn overrun is not repeated)
**WebSearch calls**: 15 (3 × 5)
**WebFetch calls**: **0 usable — `WebFetch` is DISABLED in this environment.** Every call
returned a context-mode redirect error naming MCP tools that are not in this subagent's
tool list. Per the orchestrator's instruction I routed around with `Bash` + `urllib`
GETs (12 successful page fetches + 2 NCBI **eutils** API records). **Every quotation in
every iteration file is labelled `[bash-fetched]` with its exact URL.**
**Cap hit**: iteration cap reached exactly (5/5); terms/turn ≤ 3 on every turn.
**Fetch failures this loop**: `iopscience.iop.org` → Radware bot-manager **captcha**
(recovered later via the arXiv mirror, see below); `semanticscholar.org` article page →
empty (JS-only); Semantic Scholar Graph **API → HTTP 429**. Not attempted (batch-2/3
blocked list): `sciencedirect.com`, `link.springer.com`, `researchgate.net`,
`pmc.ncbi.nlm.nih.gov` — the last recovered via eutils. **No arXiv `/pdf/` URL was
fetched at any point** (batch-3 process rule observed).

## Search trace

### Turn 1 — is extreme-few-shot (N = 5–50) sample-complexity anatomy published for PDE surrogates?
Terms: (1) neural-operator sample complexity at 5–50 samples; (2) train/test gap
decomposition few-shot PDE surrogate; (3) double descent in SciML small-data.
- Closest theory is asymptotic-in-n for **exactly our PDE class**: "we prove algebraic (in
  the sample size n) convergence rates"; prototypical example "the non-linear solution
  operator to a parametric elliptic partial differential equation"
  [cite: https://arxiv.org/abs/2412.17582]. Silent at n = 5.
- "Few-shot" in operator learning means few shots of a **new PDE family** after multi-family
  pretraining — a transfer setting, not ours [cite: https://arxiv.org/abs/2508.01211].
- Double descent in operator learning / field regression: **No usable results** (all
  tertiary sources).
- Recorded **non-attribution**: the engine's "two regimes of convergence" sentence is NOT in
  the fetched abstract of https://arxiv.org/abs/2512.08444 — do not cite it there.
  → `iteration_1.md`

### Turn 2 — unpaired ladders as "non-nested design"; what a 3-point curve supports
- Non-nestedness is a named, actively-methodologised difficulty: "the challenging setting of
  noisy and **non-nested** high- and low-fidelity data"
  [cite: https://arxiv.org/abs/2511.20183].
- Learning-curve literature's own verdict: "**no universal model can be identified**";
  curves can be "ill-behaved, showing worse learning performance with more training data"
  [cite: https://arxiv.org/abs/2103.10948]; "more data does not necessarily lead to better
  generalization performance" [cite: https://arxiv.org/abs/2211.14061].
- The single most on-point title found was **captcha-blocked** here
  (https://iopscience.iop.org/article/10.1088/2632-2153/ad7f25) — recovered in turn 5.
  → `iteration_2.md`

### Turn 3 — the close-now half: retirement, futility, attainability
- Benchmark-lifecycle argument **against** retiring on the headline number: "When a
  benchmark's accuracy saturates, it is often retired … We show that this approach
  privileges accuracy and misses the opportunity to study six other key dimensions"
  [cite: https://arxiv.org/abs/2606.26158]; saturation prevalence
  [cite: https://arxiv.org/abs/2602.16763].
- Futility stopping, the formal "close unless reachable": "early termination for futility
  when there is little evidence of a beneficial effect", with "the probability of a type II
  error beta increases" and must be "controlled at a desired level"
  [cite: PubMed 16134130, Lachin 2005 Stat Med 24(18):2747–2764, doi 10.1002/sim.2151,
  https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=16134130].
- Pre-training attainability criterion: **No usable results** (third independent failure).
  → `iteration_3.md`

### Turn 4 — ENOUGH on field context; refutation pass 1 on candidate A
- Nearest neighbour to the proposed card is an MF benchmark over **functional outputs** that
  sweeps training-set size and decomposes RMSE by *source*, but whose full text returns
  **NOT FOUND** for "learning curve", "overfit", "training set sizes"
  [cite: https://arxiv.org/abs/2408.17075 , https://arxiv.org/html/2408.17075v2]. Same
  source states the paired/unpaired distinction ("with a set of correspondences … or
  without") and the tiny-HF-budget throttle on usable LF.
- n_eff / effective-sample-size diagnostic: **No usable results** (literature offers
  redundancy pruning instead — batch 3 already ruled that `preempted`).
- Train/test gap decomposition in operator learning at tiny N: **No usable results**.
  → `iteration_4.md`

### Turn 5 — refutation pass 2 + the verdict
- **Recovered the captcha-blocked article via its arXiv mirror**: "the MFML method still
  requires a nested structure of training data across the fidelities. However, the o-MFML
  method shows promising results for non-nested multifidelity training data"
  [cite: https://arxiv.org/abs/2407.17087 = 10.1088/2632-2153/ad7f25].
- Scarce-HF variance domination is published with bias/variance theory: "ML models trained
  on scarce data have high variance, resulting in poor expected generalization performance"
  [cite: https://arxiv.org/abs/2403.08627].
- The remedy for a feared "unclaimable" outcome: "evaluate null-results using **equivalence
  tests**, Bayesian estimation, and Bayes factors"; "no statistical approach can actually
  prove that the null-hypothesis is true"
  [cite: PubMed 30873486, Harms & Lakens 2018, J Clin Transl Res 3(Suppl 2):382–393,
  https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=30873486].
- A decision rule for "MF not worth it at tiny HF budget": **No usable results** (fourth
  independent failure). → `iteration_5.md`

## Prior-art verdict

| Candidate direction | Verdict | Citations (all bash-fetched this loop) | What remains open |
|---|---|---|---|
| **A — ifc_poisson overfitting anatomy at N_hf ∈ {5, 20, 50}** (the un-executed §12.4 mandate: train/test gap decomposition per rung on the non-nested ifc ladder, in copy-LF skill against the certified MCE 0.93770, with `unclaimable` pre-registered) | **`preempted-but-MF-composition-open`** | Non-nested MF assessed method-by-method: https://arxiv.org/abs/2407.17087 · paired/unpaired standard in MF-functional-output surrogates + tiny-HF-budget throttle + source-wise (not train/test) error decomposition: https://arxiv.org/abs/2408.17075 , https://arxiv.org/html/2408.17075v2 · scarce-HF ⇒ high variance, with bias/variance analysis: https://arxiv.org/abs/2403.08627 · non-nested MF-GP methods: https://arxiv.org/abs/2511.20183 · 3-point curves unfittable / ill-behaved curves: https://arxiv.org/abs/2103.10948 , https://arxiv.org/abs/2211.14061 · asymptotic-in-n theory for parametric elliptic PDEs: https://arxiv.org/abs/2412.17582 · "few-shot" ≠ our regime: https://arxiv.org/abs/2508.01211 | **No fetched source performs a train-vs-test error decomposition for a field-valued condition→HF surrogate at single-digit HF sample counts.** Also uncited: doing it in copy-LF-skill units against a *pre-certified* per-dataset min-claimable-effect, and on an explicitly non-nested ladder whose rungs are therefore independent designs. **NOT open**: the n_eff/effective-sample-size *diagnostic* (no usable results across two batches; demote to a descriptive statistic) and anything resembling a scaling law / sample-complexity extrapolation from 3 points. |
| **B — close the stream now (no B4)** | **`preempted (cite)`** — a standard, citable act, but the weaker of two published options | Futility stopping w/ controlled type-II inflation: PubMed 16134130 (Lachin 2005), https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=16134130 · retire-vs-keep-measuring: https://arxiv.org/abs/2606.26158 , https://arxiv.org/abs/2602.16763 · making nulls informative via equivalence testing: PubMed 30873486 (Harms & Lakens 2018) | Closing is not novel and needs no novelty — but a **bare** close is not retrieval-supported: (i) every fetched retirement source treats *saturation* (target met), **none retires a criterion for infeasibility**; (ii) futility stopping's published price is a quantified type-II inflation that must be stated; (iii) the "unclaimable" fear that motivates closing is remediable — the round already owns the one ingredient equivalence testing needs (a certified per-dataset MCE). |
| **B′ — close, but ship the futility statement** (close-now *with* a pre-stated conditional-power/equivalence argument and the instrument suite as the deliverable) | **`novel` in composition, `preempted` in every component** | Same three citations as B; nearest neighbours are Lachin 2005 (futility formalism, clinical trials) and https://arxiv.org/abs/2606.26158 (keep measuring other dimensions after the headline metric stops informing) | Nothing found applies futility stopping / equivalence testing to an **autonomous multi-stream research program's stream-closure decision**; the engine also reported (search-result confidence) that "no power analyses were noted in any of the machine learning papers reviewed". This is a methodology contribution, not a model contribution — appropriate for a diag stream, but it is a *report* artifact, not an experiment card. |

## Citations summary

- [Reinhardt, Wang & Zech 2024] "Statistical Learning Theory for Neural Operators" — https://arxiv.org/abs/2412.17582 — bash-fetched — used in: `iteration_1.md` term 1
- [Hauptmann & Öktem 2025/2026] "Learned iterative networks: An operator learning perspective" — https://arxiv.org/abs/2512.08444 — bash-fetched (**non-attribution test**: the "two regimes" claim is NOT in the abstract) — used in: `iteration_1.md` term 1
- [Li & Zhe 2025] "Multi-Operator Few-Shot Learning for Generalization Across PDE Families" — https://arxiv.org/abs/2508.01211 — bash-fetched — used in: `iteration_1.md` term 2
- [Baillie, Kerleguer, Feau & Garnier 2025/2026] "Multi-fidelity Gaussian process regression for noisy outputs and non-nested experimental designs" — https://arxiv.org/abs/2511.20183 — bash-fetched — used in: `iteration_2.md` term 1
- [Loog & Viering 2022] "A Survey of Learning Curves with Bad Behavior" — https://arxiv.org/abs/2211.14061 — bash-fetched — used in: `iteration_2.md` term 3
- [Viering & Loog 2021] "The Shape of Learning Curves: a Review" — https://arxiv.org/abs/2103.10948 — bash-fetched — used in: `iteration_2.md` term 3
- ["When AI Benchmarks Plateau: A Systematic Study of Benchmark Saturation"] — https://arxiv.org/abs/2602.16763 — bash-fetched — used in: `iteration_3.md` term 1
- ["Life After Benchmark Saturation: A Case Study of CORE-Bench"] — https://arxiv.org/abs/2606.26158 — bash-fetched — used in: `iteration_3.md` term 1
- [Lachin 2005] "A review of methods for futility stopping based on conditional power", Stat Med 24(18):2747–2764, doi 10.1002/sim.2151 — PubMed **16134130** via https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=16134130 — bash-fetched — used in: `iteration_3.md` term 2
- [Brunel, Balesdent, Brevault, Le Riche & Sudret 2024] "A survey on multi-fidelity surrogates for simulators with functional outputs: unified framework and benchmark" (CMAME) — https://arxiv.org/abs/2408.17075 and https://arxiv.org/html/2408.17075v2 — bash-fetched (both; full text keyword-probed) — used in: `iteration_4.md` term 1
- [Vinod, Zaspel et al. 2024] "Assessing Non-Nested Configurations of Multifidelity Machine Learning for Quantum-Chemical Properties" (= 10.1088/2632-2153/ad7f25) — https://arxiv.org/abs/2407.17087 — bash-fetched via **arXiv mirror** after the iopscience page returned a captcha — used in: `iteration_5.md` term 1
- [Harms & Lakens 2018] "Making 'null effects' informative: statistical techniques and inferential frameworks", J Clin Transl Res 3(Suppl 2):382–393 — PubMed **30873486** via https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=30873486 — bash-fetched — used in: `iteration_5.md` term 2
- ["Multifidelity linear regression for scientific machine learning from scarce data"] — https://arxiv.org/abs/2403.08627 — bash-fetched — used in: `iteration_5.md` term 3

**Search-result confidence only (returned, NOT fetched — label as such if used)**:
https://iopscience.iop.org/article/10.1088/2632-2153/ad7f25 (captcha; superseded by the
arXiv mirror above, cite the mirror) · https://arxiv.org/abs/2605.10277 (parabolic-PDE
generalization bounds; different PDE class) · https://arxiv.org/abs/2006.16728 ·
https://link.springer.com/article/10.1007/s00158-020-02583-7 ·
https://www.researchgate.net/publication/341404887 ·
https://arxiv.org/abs/2010.10513 · https://arxiv.org/abs/2607.23404 ·
https://royalsocietypublishing.org/doi/10.1098/rspa.2023.0655 .

**Batch-1/2/3 citations still binding** (do not re-derive): Agarwal et al.
https://ar5iv.labs.arxiv.org/html/2108.13264 ; Du https://arxiv.org/abs/2511.19794 ;
McGreivy & Hakim https://arxiv.org/abs/2407.07218 ; Lipschitz-operator sample complexity
https://arxiv.org/abs/2410.23440 (**at N_hf = 5 no ceiling / information-gap claim is
defensible**) ; MF scaling laws https://arxiv.org/abs/2511.01830 ; TRIE
https://arxiv.org/html/2607.00196 ; AR-OPD https://arxiv.org/html/2606.10385v1 ;
realizability/state-aliasing https://arxiv.org/html/2505.09546 ; FPS/fill-distance
https://arxiv.org/abs/2307.10988 ; PICore https://arxiv.org/abs/2507.17151 .

**Do-not-cite (this loop)**: the "rate of convergence … evolves in two regimes" sentence
attributed by the engine to arXiv:2512.08444 (**not in the fetched abstract**); the
"generalization gap decomposed into intrinsic and external error" sentence
(emergentmind.com aggregator); all generalization-gap/overfitting prose from
bohrium.com, emergentmind.com, mlu-explain, DataCamp, statsig, mbrenndoerfer,
machinelearningmastery (tertiary). Batch 1–3 do-not-cite lists remain in force.

## Dead ends

- `double descent neural operator scientific machine learning small data regime function regression` → only tertiary explainers; the phenomenon has no operator-learning literature handle.
- `effective sample size estimate for deep learning training set redundancy diagnostic n_eff generalization` → returns redundancy *pruning*, not a gap diagnostic. **n_eff is not a citable diagnostic**; second failure for this framing.
- `deciding whether target accuracy is attainable given dataset size irreducible error estimate before further experiments` and `scientific machine learning surrogate fails at very small high fidelity budget when is multi-fidelity not worth it decision rule` → third and fourth independent failures for a **pre-training feasibility/regime criterion** (batches 2–4 now total four framings). Stop searching this.
- `"train-test gap" decomposition … operator learning tiny training set` → two engine passes, both off-domain (diffusion memorization, NLP fine-tuning, grokking).
- New fetch-blocks to record: `iopscience.iop.org` → Radware captcha (**try the arXiv mirror first** — it worked); `semanticscholar.org` article pages → empty/JS-only; S2 Graph API → 429. **`eutils.ncbi.nlm.nih.gov` WORKS** and is the way to reach PubMed/PMC-only items (two successes this loop).
- **`WebFetch` itself is disabled in this environment** — budget for the urllib route-around from turn 1.

## For the brainstormer

The brainstormer MUST quote the applicable verdict row above for whatever it proposes.

1. **Both options are defensible; the verdict does not decide for you — but it kills the
   two *lazy* versions of each.** A bare "run the ladder and look at the train/test gap"
   card is fine but must not claim any of the five preempted components. A bare "close
   because it'll probably be unclaimable" is **not retrieval-supported**: no fetched source
   retires a criterion for infeasibility, and futility stopping's published price is a
   type-II inflation you must state (PubMed 16134130).
2. **If proposing A, the sentence that survives refutation is**: *sweeping HF training-set
   size in multi-fidelity field surrogates is published and even benchmarked
   (https://arxiv.org/abs/2408.17075), and scarce-HF variance domination has bias/variance
   theory (https://arxiv.org/abs/2403.08627) — but **no fetched source decomposes train vs
   test error for a field-valued condition→HF surrogate at single-digit N**, and none scores
   such a decomposition in copy-LF-skill units against a pre-certified per-dataset
   min-claimable-effect.* Quote the A row.
3. **Pre-register an EQUIVALENCE test, not a significance test.** This is the single most
   actionable finding of the loop and it directly answers B3 part 7's counter-argument:
   "unclaimable" is only uninformative when reported as a failed NHST. Harms & Lakens
   (PubMed 30873486) — "evaluate null-results using equivalence tests, Bayesian estimation,
   and Bayes factors"; "no statistical approach can actually prove that the null-hypothesis
   is true". The round already owns what equivalence testing needs: ifc_poisson
   `min_claimable_effect = 0.9377041289531141`. Design the card so that *inside ±MCE* is a
   reported, informative outcome, and state in advance the CI width that would instead make
   it inconclusive.
4. **Call the ladder NON-NESTED, cite it, and treat rungs as independent designs.**
   https://arxiv.org/abs/2407.17087 shows nested-requiring MF methods "break down" on
   non-nested data while one reformulation survives; https://arxiv.org/html/2408.17075v2
   defines the correspondence/no-correspondence split. B2's `lf[:n_hf]` pairing prohibition
   is therefore a *literature-consistent constraint*, not a project quirk — and the card may
   NOT present non-nestedness as a discovery.
5. **Forbid three claims outright.** (a) No scaling law / sample-complexity extrapolation
   from 3 points — https://arxiv.org/abs/2103.10948 ("no universal model can be
   identified"). (b) No ceiling / information-gap claim at N_hf = 5 (batch-1/2 binding,
   https://arxiv.org/abs/2410.23440, reinforced by the asymptotic-only
   https://arxiv.org/abs/2412.17582). (c) No `n_eff` *diagnostic* claim — demote to a
   descriptive statistic (no usable results, two batches).
6. **A non-monotone ladder is a RESULT, not a bug.** If N_hf = 50 is worse than 20, that is
   the published ill-behaved-learning-curve phenomenon (https://arxiv.org/abs/2211.14061 —
   "more data does not necessarily lead to better generalization performance"). Put this in
   `expected_falsification` so the outcome cannot be mistaken for a harness failure.
7. **If closing, close the B′ way.** https://arxiv.org/abs/2606.26158 argues that when the
   headline accuracy number stops informing, the answer is to keep measuring the other
   dimensions rather than retire — which is exactly B3 part 7's "remaining value is the
   instrument suite and the standing sentence". A close-out that ships (i) the futility
   statement in the round's own units and (ii) the promoted-tool suite is the
   retrieval-supported form of closing; a silent close is not.
