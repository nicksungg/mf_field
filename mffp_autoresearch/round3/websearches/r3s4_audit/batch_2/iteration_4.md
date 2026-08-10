# Iteration 4 — refutation pass ("has this been done?") on C1 / C2 / C3

## Search rationale

Field context is sufficient (`ENOUGH`: iterations 1–3 established neighbours for every candidate; nothing new is needed to *frame* the batch, only to *refute* it).
This turn is entirely §3.3 work: for each candidate direction the goal is to find the paper that makes it non-novel.
C1 = checkpoint↔train-data content binding as the staleness predicate; C2 = certifying an MDE when the reference's uncertainty is unobservable; C3 = ULP-band tolerances + the exact-equality std guard on `sharp__sod_1d`.
Two searches this turn returned a tool error on first attempt and were re-issued (recorded below).

## Search terms used

1. `checkpoint stores hash of training data invalidate resume when dataset changed deep learning framework` (first issue returned "Web search error: unavailable"; re-issued verbatim minus one word, results below)
2. `statistical comparison against a published result reported as a single number no variance estimate meta-analysis of benchmark claims`
3. `zero variance feature standardization divide by zero guard scikit-learn constant column scaling numerical stability` (first framing — `...degenerate dimension nearest neighbor distance numerical instability` — returned "Web search error: unavailable")

## Findings

### Term 1 — refuting C1 (checkpoint carries a training-data hash)

Results: **Check-N-Run (NSDI'22)** https://www.usenix.org/system/files/nsdi22-paper-eisenman.pdf (also https://arxiv.org/pdf/2010.08679) ; Inshrinkerator (checkpoint compression) https://arxiv.org/pdf/2306.11800 ; MindSpore Transformers "Weight Saving and Resumable Training" https://www.mindspore.cn/mindformers/docs/en/r1.3.0/function/resume_training.html ; apxml "Resuming Training from Checkpoints" ; weka.io glossary ; two Meta dataloader patents.
The search engine's own summary states it plainly: *"the search results don't explicitly mention a specific feature where checkpoints store hashes of training data to automatically invalidate resume operations when datasets change."*

**FETCHED — "Check-N-Run: A Checkpointing System for Training Deep Learning Recommendation Models"** (Eisenman et al., NSDI 2022), https://www.usenix.org/system/files/nsdi22-paper-eisenman.pdf (74,971 chars).
The closest statement in the checkpointing literature, verbatim: *"When a training job resumes from a checkpoint, the run should still train the same training dataset as the original run. Hence, the checkpoint must also include the **reader state**. This is important, for example, to avoid training the same sample twice. The reader reads the dataset in the granularity of splits ... Its state includes the set of splits that are pending, and the set of splits that have been partially read."*
So a production checkpointing system does bind checkpoint↔dataset — but by **position/consumption state**, so the *same* dataset is not double-consumed.
Greps for `hash` and `correct` in the fetched body return **nothing**: Check-N-Run has no content-identity check, and its correctness concern is duplicate consumption, not "these weights were fitted to a superseded revision of the array".
Combined with Atlas (iteration 1), which binds dataset and checkpoint cryptographically but for **tamper/attestation** purposes in an adversarial supply-chain threat model, the two halves of C1 exist separately and neither is our predicate.

### Term 2 — refuting C2 (MDE with unobservable reference uncertainty)

Results: **"A Systematic Review of Methods for Handling Missing Variance Data in Meta-Analyses of Interventions in Type 2 Diabetes Mellitus"** (Batson, Burton et al.; PLOS ONE 2016) https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0164827 ; "Quantifying Variance in Evaluation Benchmarks" https://arxiv.org/html/2406.10229 (+ PDF https://arxiv.org/pdf/2406.10229) ; "A Simple and Robust Way of Concluding Meta-Analysis Results Using Reported P values, Standardized Effect Sizes, or Other Statistics" https://pmc.ncbi.nlm.nih.gov/articles/PMC3494546/ ; single-dataset meta-analysis for many-analysts studies https://arxiv.org/pdf/2511.17064 .

**FETCHED — Batson et al., PLOS ONE** (34,875 chars). This is the direct refutation of C2's *mechanism*.
The problem is named and reviewed: primary publications "fail to report any adequate measures of uncertainty", so *"alternative methods for handling missing variance data are required"*; the catalogued approaches are **algebraic calculation, trial-level imputation, and no imputation**; an upper-bound/critical p-value may be used "as an approximation to compute the SD ... a **conservative approach** to quantifying uncertainty"; imputation from a correlation coefficient uses a conservative default (0.5) "imputed from another study".
Conclusion, verbatim: *"While no particular imputation method is favoured, authors are **discouraged from using a no-imputation approach**. Instead, authors are encouraged to explore different approaches using **sensitivity analysis**."*
That is our M11 recommendation, in a mature literature: `mdd_scored = 0` **is** the discouraged no-imputation approach; certifying the pair `(0, estimate)` and licensing on the max is a conservative imputation plus sensitivity analysis.
Snippet-level neighbour: arXiv:2406.10229 argues single-number benchmark comparisons without variance are misleading and introduces variance metrics — the ML-side statement of the same problem, but for the *evaluated* system.

### Term 3 — refuting C3 (the sod_1d exact-equality std guard)

Results: scikit-learn `StandardScaler` https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html ; scikit-learn preprocessing guide https://scikit-learn.org/stable/modules/preprocessing.html ; several textbook/tutorial pages.

**FETCHED — scikit-learn `StandardScaler` reference** (31,306 chars). Verbatim from `scale_`: *"Per feature relative scaling of the data to achieve zero mean and unit variance. Generally this is calculated using `np.sqrt(var_)`. **If a variance is zero, we can't achieve unit variance, and the data is left as-is, giving a scaling factor of 1.**"*
Our `standardize_cond` guard `sd = where(sd > 0, sd, 1.0)` is therefore the *standard library idiom*, implemented identically — the guard itself is not a defect and not a contribution.
The defect is that the idiom's predicate is an **exact-equality (unstable) test** in the sense of Titolo et al. (iteration 3, arXiv:1808.04289): one ULP moves the measured std to 1.192e-7 and the branch flips, amplifying that dimension 8.4e6× and re-selecting 53 % of `sharp__sod_1d`'s nearest-neighbour assignments.
No retrieved source measures that composition (standard guard × unstable test × frozen benchmark reference).

## Interpretation (cap note: this is iteration 4 of 5; iteration 5 is reserved for the last targeted refutation + verdict assembly)

C2's mechanism is **preempted** by a mature missing-variance-imputation literature that even prescribes our exact remedy (impute conservatively + sensitivity analysis, never treat missing as zero) — the honest framing for the card is adoption with citation, not discovery.
C1 survives as an **unfilled gap between two published halves**: position-state binding (Check-N-Run) and cryptographic artifact attestation (Atlas), neither of which yields the `executed_steps == 0 AND train_sha256 mismatch` predicate with train/test hashed separately.
C3's components are all published (ULP tolerances, unstable tests, the sklearn guard); only the measured blast radius on a frozen reference floor is project-local.
