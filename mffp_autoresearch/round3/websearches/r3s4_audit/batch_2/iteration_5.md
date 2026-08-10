# Iteration 5 — last refutation turn + verdict assembly (CAP: this is iteration 5 of 5)

## Search rationale

One refutation angle remained for C1: our predicate is, stripped of ML vocabulary, **cache invalidation by input content hash** — build-system (Bazel/Nix) and dataflow-recomputation semantics.
If someone has already applied that to model artifacts, C1 collapses from "gap between two published halves" to `preempted`.
Terms 1 and 3 were two framings of that question; term 2 attacked the scientific-workflow/dataflow side.
The `train_seconds` rule-pricing methodology (0 unique TPs / 62 FPs) was already priced against TRAINCHECK §5.3 in iteration 1 and needed no further search.

## Search terms used

1. `content-addressed build system cache invalidation input hash applied to machine learning experiment artifacts reproducibility` — **tool returned "Web search error: unavailable"; no results**
2. `provenance-based staleness detection scientific workflow which results are out of date when input data changed recomputation`
3. `Bazel Nix content addressed cache invalidation input hash machine learning experiment artifact reproducibility` (re-framing of term 1) — **tool returned "Web search error: unavailable" again; no results**

## Findings

### Terms 1 and 3 — build-system content-addressing applied to ML artifacts

**No usable results.** Both issues of this question returned a hard search-tool error, twice, in separate turns.
Nothing is citable here and nothing may be asserted from model recall about Bazel/Nix/DVC semantics.
Record as an unresolved search gap, not as a negative result: the direction was NOT refuted and was NOT confirmed.
(The DVC-style "checksum of file content triggers pipeline re-execution" statement from iteration 2's term 2 remains the only retrieved data point, and it is search-snippet level only.)

### Term 2 — dataflow/provenance staleness detection

Results: **"An Alternative to Cells for Selective Execution of Data Science Pipelines"** https://arxiv.org/pdf/2302.14556 ; HyProv https://arxiv.org/html/2511.07574 ; "Towards Observability for Production Machine Learning Pipelines" https://arxiv.org/pdf/2108.13557 ; "Detecting common scientific workflow fragments using templates and execution provenance" https://dl.acm.org/doi/10.1145/2479832.2479848 ; workflow-provenance-for-SciML (ResearchGate) ; several data-lineage vendor pages and impact-analysis patents.

**FETCHED — "An Alternative to Cells for Selective Execution of Data Science Pipelines"** (arXiv:2302.14556), 32,812 chars.
It formalises exactly our failure mode at the *pipeline* level, verbatim: *"Even without code changes, notebook state can become stale: For example, the dataset we read from disk in Cell 1 might change ... the notebook needs to be partially re-executed to account for such an event."*
It defines a correct re-execution plan as one where *"each operation is executed only when all its input values are up-to-date, including external values"*, and states the rule *"we must always rerun edited operations, impure operations, and pure operations with at least one potentially stale argument"* — with `read_csv` treated as impure, so **"we must always assume that something might have changed"**.
Grep for `hash` in the fetched body: **nothing**. Staleness is propagated structurally (dataflow + impurity), never witnessed by a content hash of the external input.
That is the same shape as our situation and the same limitation: without a content hash you can only *assume* the external read changed (our global `--data-changed-after` cutoff, which flags 186–189 innocent legs) or ignore it (the shipped default, which missed 36 legs).

## Prior-art verdicts (§3.3 — mandatory)

Candidate directions this stream-batch is expected to propose, each with a refutation-oriented verdict.
**Every citation below appears in one of `iteration_1..5.md` with a URL and was retrieved in this loop.**

### B2-D1 — checkpoint↔training-data content binding as the staleness witness
*(ship `ckpt.data_binding[ds].{train,test}_sha256` as the sixth-class contract check; audit predicate `executed_steps == 0 AND train_sha256 != current`; retire `train_seconds_collapsed`; measure coverage from today's 0/18)*

**Verdict: `preempted-but-MF-composition-open (cite)`.**
Published halves, all fetched: **Atlas** (https://systex-workshop.github.io/2025/papers/systex25-final68.pdf) cryptographically binds dataset and checkpoint artifacts in one attested lineage — but under an *adversarial* threat model (tampering, poisoning, EU AI Act evidence), answering "was this artifact modified", not "were these weights fitted to a superseded revision".
**Check-N-Run** (https://www.usenix.org/system/files/nsdi22-paper-eisenman.pdf) binds checkpoint↔dataset by **reader/position state** so the resumed run "should still train the same training dataset", motivated by duplicate consumption; it contains no content hash.
**TRAINCHECK** (https://www.usenix.org/system/files/osdi25-jiang.pdf) supplies the *methodology* we already used — proactive inferred invariants with preconditions to suppress false positives, and an explicit false-positive section run over 63 known-good programs — but its invariant space is in-process training correctness, not data identity.
**arXiv:2302.14556** shows the dataflow community handling "the dataset on disk might change" by *assumption* (impure operations always rerun), explicitly without hashes.
**What remains open**: (i) the exact scoring-correctness predicate `executed_steps == 0 ∧ train_sha256 mismatch`; (ii) **hashing train and test arrays separately**, which is what discriminates our two live populations (18 pfc legs invalidated by a *train-array* box swap vs 18 allen_cahn legs left valid by a *test-split* trim) — no retrieved source makes that distinction; (iii) the empirical **rule-pricing** result on a scored MF benchmark corpus (859 legs, 20 ground-truth stale). Claim (ii)+(iii), cite (i)'s neighbours.
**Caveat**: terms 1/3 of this iteration (build-system content-addressing applied to ML artifacts) failed twice with a tool error, so this verdict is not backed by a completed search on that angle — batch 3 should retry before any novelty language is used in a write-up.

### B2-D2 — certify the pair `(mdd_scored = 0, mdd_reference_unobservable = est)` and license claims on the max
*(the ifc paper-bar cells; `tau_abs` understated ~2.15–2.17×)*

**Verdict: `preempted (cite)`.**
**Batson et al., PLOS ONE** (https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0164827) is a systematic review of *exactly* this problem — comparing against published results whose variance was never reported — cataloguing algebraic calculation, trial-level imputation and no imputation, endorsing conservative approximations, and concluding that authors are **"discouraged from using a no-imputation approach"** and should instead **"explore different approaches using sensitivity analysis"**.
`mdd_scored = 0` *is* the discouraged no-imputation approach; "certify the pair and use the max" *is* conservative imputation plus sensitivity analysis.
Supporting neighbours, all fetched: **arXiv:2605.28873** (pre-registered paired-MDE budget with a per-cell **binomial reference SD** substituted where replication cannot observe the noise, plus a pre-registration template and the warning that "cross-split SD is a misleading noise proxy"); **arXiv:2511.19794** (paired multi-seed + BCa bootstrap + sign-flip decision rule for small improvements); and, snippet-level, **Bradley et al. 2008** on the Brier *skill* score being a biased estimator when the reference is estimated (https://journals.ametsoc.org/view/journals/wefo/23/5/2007waf2007049_1.xml).
**What remains open**: nothing methodological. Only the project-local instantiation — that a *published paper bar computed on somebody else's finite test set* is the missing-variance case, and the concrete licensing bands (ifc_heat |skill−1| ∈ (0.164, 0.356); ifc_poisson ∈ (0.691, 1.483)). Frame as **adoption with citation**; a novelty claim here would be the 0-for-4 record repeating.

### B2-D3 — precision-aware tolerance setting: per-dataset ULP bands + the `sharp__sod_1d` unstable-test defect

**Verdict: `preempted-but-MF-composition-open (cite)`.**
Tolerance selection by relative-vs-ULP error with a separate absolute check near zero is documented verification engineering (MathWorks HDL Coder, https://www.mathworks.com/help/hdlcoder/ref/floatingpointtolerancecheckbasedon.html and https://www.mathworks.com/help/hdlcoder/ug/ulp-considerations-of-native-floating-point-operators.html — search-snippet level) — i.e. `max(1e-9, ULP band)` is standard practice, not a contribution.
The interesting half is named and formally studied: **Titolo, Muñoz, Feliú & Moscato, "Eliminating Unstable Tests in Floating-Point Programs"** (https://arxiv.org/pdf/1808.04289) — round-off makes the *control flow* of conditional FP statements diverge from real arithmetic; they prove a transformation that warns when the flows may diverge and note unstable tests cannot be fully avoided.
The guard itself is the standard library idiom: **scikit-learn `StandardScaler`** (https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html) documents verbatim "If a variance is zero, we can't achieve unit variance, and the data is left as-is, giving a scaling factor of 1."
**What remains open**: the composition — that a **frozen benchmark reference floor** can be the output of an unstable test, measured here at a 3.08e-1 relative move and 53% nearest-neighbour re-selection under a ±1 ULP dither, with the failure invisible to every hash and seam check. No retrieved source measures an unstable test's blast radius on a benchmark's certified constants. Report as a project-local instrument finding; adopt Titolo et al.'s remedy shape (drop/flag the degenerate dimension, warn on divergence) rather than tuning a tolerance.

### B2-D4 (secondary, routed) — the fair-comparison fit-set-size seam (reference arms fit on 400 rows vs the scored arm's 320)

**Verdict: `preempted-but-MF-composition-open (cite)`.**
The matched-procedure principle is published and blunt: **Brigato et al., "Tune It or Don't Use It"** (https://arxiv.org/pdf/2108.13122) — "most existing works compare their proposed method against insufficiently tuned baselines ... which makes it easy to outperform them"; "Comparing against an untuned baseline with default hyper-parameters is as good as no comparison at all"; "To perform a fair comparison, we use the same backbone CNN architecture for all methods."
That covers architecture and tuning-effort matching; **fit-set size** matching between a reference arm and the scored arm is not addressed in any retrieved source.
**Anti-citation (important)**: the search engine's synthesis for this term described a "matched sample size protocol ... draw subsamples of the same size ... bracket the comparison with a confidence interval", attributing it to nothing; the one candidate body fetched (https://arxiv.org/pdf/2606.02959) contains no `matched-n`, `subsample` or `same size` text. **That phrasing must not be cited by the brainstormer.**
