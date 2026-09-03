# MFFP Autoresearch — Mentor Update (2026-09-03): Round 4

Date: 2026-09-03.
Author: Eloise (with the autoresearch orchestrator).
Scope: round 4 in full, from its start on 2026-08-13 to today.
Previous brief: [`PROFESSOR_UPDATE_2026-08-13.md`](PROFESSOR_UPDATE_2026-08-13.md) (round 3 close + the benchmark_30 head-to-head).
Adjudicated records behind every number here live on branch `round4-program` under `mffp_autoresearch/round4/docs/`; the specific file is named at each claim.
Rendered page: [Claude artifact](https://claude.ai/code/artifact/fecd8b31-934c-4845-8eb9-944025cd189e) (private until shared from its share menu) — same content as this file, with the per-dataset certification chart drawn from `state/bar_reverdict_r4_0013.json`.

## The short version

1. **Round 4's goal is a model that beats your film row in `final_error_matrix.csv` across benchmark_30**, trained at 2500 epochs per stage.
   That row is the bar for the whole round, fixed in writing before any challenger existed, along with the margin rules used to judge one.

2. **We have one challenger that beats it, by a small margin.**
   `C3a` — film with one extra input channel carrying the analytically rendered initial condition — comes in **3.5% better than the bar across all 30 datasets and 7.2% better across the 28 that are cleanly comparable** (3-seed mean against your single seed 42, both sides in your metric).
   Its one large, credible per-dataset win is `sharp__fisher_kpp_2d` at **6.46×**; every other dataset is inside the descriptive band we pre-registered, i.e. real but too small to claim.
   Details in §3.

3. **Four earlier challengers failed their own pre-registered tests, and those failures stand as recorded.**
   We did not move a threshold after seeing a result.
   The sequence and what each one ruled out is in §2.

4. **The most consequential finding of the round was not a model — it was a measurement error on our side, in how we compared against your matrix.**
   For about a week we believed there was a "lineage gap": our film runs looked systematically worse than yours, by up to 2.5× on individual datasets, which would have meant no challenger built on our film could ever match your panel.
   There was no such gap.
   Our harness computes relative L2 two ways, and the pre-registered comparison was reading the wrong one.
   Once matched, our film reproduces your matrix to a panel geometric mean of 0.944, and the "2.5× gap" on `ext__cahn_hilliard_2d` became 1.003.
   Your answers on 2026-09-02 confirmed the metric and the protocol; details and the safeguards we added are in §4.

5. **One discrepancy is still open, and it starts with a mistake of ours.**
   On `lid_driven_cavity_generated` your film gets 0.0203 and our three seeds land between 0.033 and 0.050.
   Your explanation was that you ran a 40/10 snapshot against our documented 400/100 — but that 400/100 figure was an error in our own `datasets_summary.csv`, describing a dataset that exists nowhere, and our cells in fact trained on the same published 40/10 snapshot with matching hashes.
   So the size difference isn't the cause, and a factor of about 2.4 is still unexplained.
   We've narrowed it to three candidates and can close only one ourselves; see §5.
   That dataset is currently excluded from the 28-dataset panel as unexplained rather than silently kept or silently dropped.

6. **In flight right now:** a zero-extra-training ensemble of C3a's three certified checkpoints, which on a device-consistent estimate is **about 27% better than the bar across 30 datasets** and better than the mean of its own seeds on all 30, plus two further challengers (a capacity sweep and a combined-mechanism model).
   The ensemble estimate is an estimate until its GPU evaluation clears the queue; §6.

Nothing here needs an immediate decision from you.
The one request is the `lid_driven` check in §5.

## 1. How round 4 is run

Every challenger goes through the same fixed sequence, and each stage is written down before the next one starts.

- A **design document** stating the mechanism and, critically, its **falsification clauses**: the numeric thresholds that would make us call the model a failure.
  Those clauses ship as executable functions with tests, not as prose, so they cannot be softened later by rewording.
- A **cheap pilot**: 200 epochs, seed 0, on a fixed 14-dataset development subset that was signed off before any challenger was trained.
  A pilot costs under an hour of GPU time and kills most ideas.
- **Certification** only if the pilot passes: all 30 datasets, 2500 epochs per stage, three random seeds — about 65 H100-hours per challenger.
- Two AIs review every artifact (one authors, the other reviews adversarially) until neither finds anything, and the review rounds are run as parallel independent lenses rather than repeated identical passes.

The bar itself is your matrix row.
We deliberately did not re-train our own film at 2500 epochs to serve as the bar, because the point of the round is to beat a number you produced independently of our harness.

## 2. The challengers, and what each one ruled out

| # | Mechanism | Outcome | What it tells us |
|---|---|---|---|
| C1 | Film plus three zero-initialised extra input columns: nearest-neighbour retrieval, retrieval mean, and a rendered initial condition | **Killed at pilot** | Two of three falsification clauses failed. The retrieval columns actively hurt: 19.8% worse than film overall, worst case 8× on `ext__wave_2d`. A derangement control (shuffle the conditions) confirmed the retrieval columns were exploiting almost no information. The initial-condition column, by contrast, gave +82% on `sharp__fisher_kpp_2d` — that signal is what became C3a. |
| C2 | Tail-averaging of film's weights over the last quarter of training, plus spectral weight decay | **No-go at 2500 epochs** | The idea was that film drifts late in training. At 200 epochs the averaging window was inert (0.56% worse). At 2500 epochs the within-run drift is essentially nil on the sharp datasets (max 1.023 on `sharp__allen_cahn_2d`), so the average *is* the last iterate. Useful negative: the "film is worse at 2500 on sharp problems" pattern we saw across separate runs is not within-run drift. |
| C3a | Film plus **one** zero-initialised channel carrying the closed-form initial condition, on the 4 of 30 datasets where one can be rendered | **Certified; beats the bar** | See §3. On the other 26 datasets the channel is exactly zero and the model is film bit-for-bit, which is why the downside is bounded by construction. |
| C3b | Zero-initialised low-rank, condition-driven multiplicative modulation of film's spectral weights | **Passed pilot, failed certification** | At 200 epochs it looked good (5.9% better than film; 1.92× on `lid_driven_cavity_generated`) and the derangement control confirmed the win was real. At 2500 epochs it is 5.8% *worse* than the bar over 30 datasets. The pilot-tier gain did not survive the full budget. |
| C4-ens | Ensemble the predictions of C3a's three certified checkpoints — no new training at all | **Estimate pending GPU evaluation** | Better than the mean of its own three seeds on 30 of 30 datasets. §6. |
| C4b | Capacity sweep on C3a's trunk (wider, more modes, both) | Pilot queued | Tests whether C3a's margin is mechanism or under-parameterisation. |
| C4a | C3a's initial-condition channel combined with C3b's condition modulation | Building | Tests whether C3b's interface win transfers onto a trunk that already works. |

Solver-in-the-loop approaches (re-running a coarse solve at test time) remain banned: inference is condition-only, predicting the high-fidelity field from the small condition vector alone.

## 3. The certified result

**C3a, `mf_fno_film_icrender_r4`.**
Film's trunk and recipe verbatim, plus a single extra input channel holding the initial condition rendered analytically from the `ic_*` entries of the condition vector.
The design identified six candidate datasets, but in the certified runs the channel is actually live on **four**: `sharp__allen_cahn_2d`, `sharp__cahn_hilliard`, `sharp__fisher_kpp_2d` and `sharp__phase_field_crystal_2d` (the burgers and porous-medium datasets do not render an initial condition under the applicability rule).
On the other 26 the channel is identically zero and the network reduces exactly to film, verified as bit-equality rather than asserted.

Certification ran as a 90-cell array (30 datasets × 3 seeds), 90/90 complete, zero failures.

| Panel | Bar ÷ C3a (geometric mean) | Margin | Reading |
|---|---|---|---|
| All 30 datasets | 1.0351 | **+3.5%** | Reportable, but below the 5% line we pre-registered as "credible" |
| Comparable 28 | 1.0722 | **+7.2%** | In the "suggestive" band (5–10%) |

The 28-dataset panel excludes two datasets for stated reasons, not for their values:

- `ifc_heat` — your matrix value comes from the older, disjoint fidelity pairing, which you confirmed on 2026-09-02.
  Our cells train on the repaired nested pairing, so the two numbers describe different data.
- `lid_driven_cavity_generated` — the open discrepancy in §5, flagged in the record as *waived, unexplained* rather than quietly removed.

Per-dataset, only `sharp__fisher_kpp_2d` clears the 1.5× line we pre-registered as the threshold for calling a single-dataset result a win, at **6.46×**.
`sharp__allen_cahn_2d` at 1.44× and `sharp__cahn_hilliard` at 1.20× are recorded as descriptive only.
The worst cases are `ext__helmholtz_2d` at 0.64 (a dataset where film is unstable across seeds — its own runs span 1.31 to 2.66) and `lid_driven_cavity_generated` at 0.52.

**Honest reading:** a 3.5% panel margin is a real but modest result, and it rests substantially on one dataset where the mechanism obviously applies.
The claim we are comfortable making is narrow: *giving the network the initial condition as a field, where one exists, is worth a large amount on the reaction-diffusion problems and costs nothing elsewhere.*
We are not claiming a general improvement over film.

Record: `docs/c3a_cert_results.md`, `docs/c3b_cert_results.md`, `state/bar_reverdict_r4_0013.json`.

## 4. The metric audit — what went wrong and how it was caught

This is the part most relevant to anyone else comparing against your matrix, so it is worth stating carefully.

**The symptom.** After C3a and C3b were certified, both came out well below the bar on the panel (0.80 and 0.74) even though each beat *our own* film in a matched side-by-side.
Decomposing that gap suggested your film was systematically better than ours — 2.51× on `ext__cahn_hilliard_2d`, 2.42× on `lid_driven_cavity_generated`, 3.19× on `sharp__shallow_water_1d`.
The conclusion we drew on 2026-08-24 was that our vendored film was a different, weaker lineage than yours, which would have meant no challenger built on it could ever reach your panel.

**The actual cause.** Our harness reports relative L2 in two aggregations: the mean over test samples of the per-sample relative error, and a ratio of summed norms over the whole split.
On datasets with skewed per-sample errors those two differ by a factor of two or more.
Your matrix is the per-sample mean; the pre-registered comparison clauses were reading the ratio-of-sums field.
The two "lineages" were two columns of one lineage.

**The proof chain**, all in `docs/audit_r4_bar_metric_identity.md`:

- Our round-4 film and the factory's film agree to 1e-6 on a fixed input — same weights, same code.
- The earlier training-ladder film numbers equal the round-4 runs' per-sample-mean values to printed precision on 8 of 8 overlapping datasets.
- Panel geometric mean of your matrix over our film: **0.944** under the per-sample mean, versus 0.729 under the ratio-of-sums.
- The 2.51× `ext__cahn_hilliard_2d` "gap" becomes **1.003**.

**What changed as a result.**
The pre-registered FAIL verdicts still stand — C3b is worse than the bar under the corrected metric too, and the verdicts were recorded before the audit.
C3a moved from "loses to the bar" to "+3.5% / +7.2%".
We added a metric contract file that every comparison must resolve against, plus a gate that refuses to score a panel unless our own film reproduces your matrix within tolerance across the full 30, and explicit *waived-unexplained* semantics so a dataset like `lid_driven` cannot be dropped without a written reason.
The full-30 reproduction gate currently reports FAIL honestly, because 8 optional cells (~6–8 H100-hours) have not been run; it is not marked green on partial evidence.

**Your 2026-09-02 answers, and what we did with each.**

| Your answer | Status |
|---|---|
| Metric is per-sample ‖pred−y‖/max(‖y‖, 1e-8), then mean over test samples | **Confirmed.** Matches our `rel_l2_mean`. We checked that the 1e-8 floor is immaterial: the smallest ‖y‖ across all 30 high-fidelity test splits is 0.0035. |
| 2500 is per stage (2500 LF pretrain + 2500 HF finetune), last checkpoint, seed 42 | **Confirmed identical** to our protocol. The remaining difference is the seed: your 42 against our {0, 1, 2}. |
| `ifc_heat` is the older pairing | **Confirmed**, and that dataset is now excluded from the comparable panel. |
| `lid_driven` was a smaller 40/10 v2 snapshot | **Does not resolve it** — see §5. |
| Other matrix rows: not confirmed for now | Recorded as a caveat everywhere a non-film matrix row is used, including the "perfect per-dataset model selection is worth 1.247×" figure. |

## 5. The one open request

**First, the part that is our fault.**
Your explanation for `lid_driven_cavity_generated` was that you evaluated a smaller dataset than we did — your 40/10 v2 snapshot against our documented 400/100.
The 400/100 figure came from our `datasets_summary.csv`, and it was wrong.
No dataset of that size exists anywhere: not in either hub release, not in our local copy, not in any run we have on record.
So you were reasoning from a document we published, and the document was the error.
That row is now corrected to 40/10, with the hub release treated as canonical.

**Why that doesn't close the gap:** our cells never used a 400/100 snapshot either.

- They train on `train_l4` of shape (40, 65536) and `test_l4` of shape (10, 65536) — the same published 40/10 snapshot you describe.
- Those files' SHA-256 hashes (`b161bc52773c…`, `b42a022c5039…`) are identical on the `nicksung/mf_field` and `eloisezeng/mf_field` releases.
- On that data our three film seeds give 0.0496 / 0.0327 / 0.0345 against your 0.0203.

Both sides are therefore at 40/10, and roughly a factor of 2.4 is still unaccounted for.
Three candidates remain, and we can only close one of them from here:

1. **Your local v2 copy differs in content from the release**, even though it matches in size.
   We can't check this without your hashes.
2. **A different low-fidelity rung.**
   Ours pretrains on `l1` (32×32) against the 256×256 high-fidelity grid; if yours differs, that alone could account for it.
3. **Seed variance on a 10-sample test set.**
   This one is ours to close, and film at seed 42 under exactly the protocol you described is queued on that dataset now.

**So the ask is just the first two:** the SHA-256 of `train_l4.npz` and `test_l4.npz` in your local v2 copy, and which rung you pretrained on.
Either would settle it, and if the hashes differ that is the whole answer.

Lower priority, whenever convenient: a film number on the re-paired `ifc_heat` would let us put that dataset back into the comparison instead of excluding it.

## 6. Diagnostics worth knowing, independent of any model

These came out of the round's Phase 0 and are properties of the benchmark rather than of a challenger.

- **The error is shape, not level.**
  At both training budgets, the share of squared error attributable to a constant offset is small (≤ 0.094 on 9 of 10 datasets probed at 200 epochs; 0.016–0.237 at 2500).
  So a mean/level correction is not a lever.

- **There are at least three distinct spatial failure modes, not one.**
  Interface-dominated (`lid_driven_cavity_generated`: 0.898 of the error mass sits on 5% of pixels, right at interfaces), bimodal (`sharp__fisher_kpp_2d`), and bulk (`sharp__allen_cahn_2d`, `sharp__cahn_hilliard`, peaking well away from any interface).
  `ifc_heat` is the counter-example that kills a single-mode story: 0.086 of its error at the interface and 0.408 in the farthest bin.
  Any mechanism aimed only at sharpening interfaces leaves a large part of the panel untouched.

- **12.5× the training budget does not relocate the failure.**
  On `sharp__allen_cahn_2d` the spatial error profile at 2500 epochs is effectively identical to the one at 200, while the total error is *worse* at the larger budget.

- **On several datasets a trained model is beaten by a zero-cost reference**, but the effect is much smaller than it first appeared.
  Simply resampling the coarse solution beats film at 2500 epochs on seven datasets, by up to 242× on `sharp__allen_cahn_2d`.
  However, that reference uses the test split's low-fidelity field, which no model is allowed to see — the scorer raises an error if it is exposed.
  The *implementable* version of that observation is worth 2 datasets and a 1.054× panel gain, not 2.072×.
  We recorded this correction against our own earlier draft, which had the larger number as its headline.

- **Numbers move across hardware more than expected.**
  Evaluating the same certified checkpoints on CPU versus H100 differs by up to 148% on `lid_driven_cavity_generated` and 41% on `heat_local`, traced to TF32 defaults in cuDNN convolutions with no pin in the model family.
  Practical consequence: any comparison between numbers produced on different machines needs the device stated.
  All certification numbers in this report are H100.

## 7. What is running now, and what comes next

Queued on the GPU partition as of this morning (the partition is congested — 24+ H100 and 45+ H200 jobs pending):

- **C4-ens evaluation** on H100 and H200 — the 3-seed prediction ensemble of C3a's certified checkpoints, no additional training.
  Its CPU run is complete: better than the mean of its own three seeds on **30 of 30** datasets, geometric mean 0.816 (18% lower error), most on the smooth and elliptic problems, least on the sharp ones.
  Combining that ratio with the H100 3-seed means, so that the device offset cancels, gives a device-consistent estimate of **+26.8% over the bar on 30 datasets and +31.2% on 28**, with six per-dataset clears above 1.5× (`sharp__fisher_kpp_2d` 6.75×, `sharp__helmholtz_2d` 1.74×, `sharp__burgers_1d` 1.70×, `poisson_generated` 1.64×, `sharp__allen_cahn_2d` 1.57×, `heat_generated` 1.53×) and 5 of 30 still below the bar.
  This is an **estimate** until the GPU evaluation runs; it is labelled as three times the training compute of a single-seed bar wherever it appears.
- **C4b pilot** — a capacity sweep on C3a's trunk in three configurations, to separate "the mechanism helps" from "the model was too small".
- **Seed-42 film probe** on `lid_driven_cavity_generated` under your stated protocol, on three device classes, for §5.

**C4a** (C3a's initial-condition channel plus C3b's condition modulation) is mid-build; its specification and plan converged and seven of its implementation tasks are committed.

Beyond that, the decision to make is whether the ensemble result, if it survives GPU evaluation, is the round's headline.
A 27% panel improvement at zero extra training cost is a larger effect than any architecture change the round has produced, and it is the kind of result that says something about the benchmark's variance rather than about the model — which we would report as such.

---

*Provenance: all figures traceable to `mffp_autoresearch/round4/` on branch `round4-program`. Certification arrays 1354161 (C3a) and 1354162 (C3b), 180/180 cells complete with zero failures. Re-verdict producer `tools/make_bar_reverdict.py` → `state/bar_reverdict_r4_0013.json`. Metric audit `docs/audit_r4_bar_metric_identity.md`; bar metric contract `vendor/bar_metric_contract.json`, status `confirmed_by_mentor` as of 2026-09-02.*
