# Cross-Family Fixes: Decision Brief

**Status:** decision document, nothing implemented.
**Audit date:** 2026-07-19.
**Last revised:** 2026-07-21 — restructured as a decision brief; no finding was added, removed, or changed in substance.
**Evidence register:** [`MODEL_TWEAKS_EVIDENCE.md`](MODEL_TWEAKS_EVIDENCE.md).
**Scope of evidence:** static audit of the 21 model directories present in this checkout, plus `eval/`, `bench/`, and `references/v9_baseline/`.
No code was run and no dataset was read.

---

## 1. Decisions needed now

The reader is being asked for five fixed-surface approvals, four compute-budget approvals, and one policy call.
The mutable `models/**` bugs and model-side improvements do not need approval and should proceed after the scoring and noise decisions are clear.

| Ask | Recommendation | Surface | Cost | Blocks if not decided | Evidence |
|---|---|---|---|---|---|
| A1 | Enforce one nRMSE definition | `eval/`, possibly `data_adapters/` | One metric function, then re-score all 436 cells | Any leaderboard comparison can be won by metric definition rather than model quality | F01 |
| A2 | Make test/OOD splits comparable | `eval/`, possibly `data_adapters/` | Split-selection logic, then re-score all 436 cells | Fifteen test-only families remain advantaged against six test+OOD families | F02 |
| A3 | Make `vs_paper` compare like with like | `eval/score.py` | One aggregation change, no re-scoring | `beats_paper` remains biased by arithmetic-vs-geomean aggregation | F03 |
| A4 | Gate paper comparisons on matching target grids | `eval/score.py` | One gating comparison, affects 2 datasets, no re-scoring | `era5` and `pm_test` can be scored on downsampled targets and still compared to paper numbers | F04 |
| A5 | Hash shared code and configs | `eval/score.py`, shared-code hash policy | One hash function, invalidates the cache once by design | Edits to `_common/`, `data_adapters/`, and configs can silently reuse invalid cached results | F06 |
| A6 | Calibrate the noise floor after the nearly free determinism fix | `models/**`, then cluster compute | Small code fix, then about 36 runs, roughly 8% of one full benchmark | Existing leaderboard deltas have no measured resolution threshold | F05 and F13 |
| A7 | Run the off-Poisson attribution experiment for `mf_fno_pinn_transfer` | Cluster compute | Two families times the off-Poisson datasets, cluster only because key families are absent here | The physics-vs-FiLM explanation for the #2 family remains undecided | P01 and U03 |
| A8 | Run the constraint-detection probe on cluster data | Cluster compute, read-only over `data/` | One probe pass over the 17 datasets, no training | Constraint work risks guessing which datasets satisfy positivity, conservation, vector-field, or boundary assumptions | F18 and U01 |
| A9 | Run a clean `modes_cap` sweep | `models/**`, then cluster compute | Compute only, no new mechanism to implement | The strongest bandwidth hypothesis remains untested | F22 |
| A10 | Decide the backbone consistency policy | Policy call, then `models/**` | The decision is free; conforming the families afterwards is not | Mechanism comparisons remain confounded by capacity, mode schedule, optimizer protocol, and validation fraction | F23 |

**On the re-scoring cost in A1 and A2.**
Both change what the metric measures, so every cached cell becomes stale.
`results/raw/<tag>.json` stores summary numbers rather than predictions, so re-scoring cannot be done from the cached results alone.
Whether that means re-evaluating from retained `checkpoints/` or retraining from scratch was not determined in this checkout — the gap between those two is large, and it is worth establishing before A1 is approved rather than after.

---

## 2. Recommended order

1. Do the F13 determinism fix first inside `models/**`.
This is nearly free and should shrink the run-to-run sigma before any measurement.
It means adding `torch.cuda.manual_seed_all`, stdlib `random.seed`, cuDNN flags, and an explicit TF32 decision.

2. Run the sparse noise-floor calibration.
Do not rerun the whole benchmark three times.
Measure run-to-run sigma on roughly 3 families times roughly 4 datasets times 3 seeds, sampling across precision and dataset-conditioning axes.
The precision axis matters because `transolver_*` and `v9_baseline` train under AMP fp16 (`transolver_residual/smoke_eval.py:52,79,132`) while every FNO family runs fp32.
Once sigma is measured, apply it as a resolution threshold to the 436 existing leaderboard cells.
No re-benchmark of those cells is required.

3. Escalate A1 through A5 as one scoring-validity package.
They share one root cause: cached leaderboard cells are being compared before the harness proves that the cells measure the same thing.

4. Run the two small decision experiments before broader model work.
The first is the off-Poisson `mf_fno_pinn_transfer` attribution experiment.
The second is the dataset constraint-detection probe.

5. Proceed with mutable-surface fixes in `models/**`.
The highest-leverage order is checkpoint resume in `fire_run`, per-sample relative-L2 loss, cross-fitted LF summaries, stale-checkpoint guards, and `fno_mf_stack` repairs.

---

## 3. Bottom line

The narrow physics question is mostly resolved against embedding PDE residuals as the default mechanism.
The better general direction is structural constraints on the function space rather than equation residuals.
That conclusion has one important unresolved attribution experiment: `mf_fno_pinn_transfer` is #2 by Elo and best by median relative-L2, and the current audit cannot prove whether that rank comes from its Poisson-only PDE term or from its transfer machinery.

The larger issue is scoring validity.
Three incompatible nRMSE definitions coexist, split coverage differs across families, paper comparisons mix aggregation rules, some targets are downsampled before scoring, and shared code is not hashed.
Until A1 through A6 are decided, small leaderboard movements are not reliable approval signals.

The noise-floor claim must be read as an absolute relL2-unit estimate, not as a 1% relative-delta claim.
The estimate is that any absolute delta below roughly `0.01` in relL2 units is plausibly indistinguishable from run noise.
Under that reading, the current ranks 1-15 collapse into one indistinguishable band until measured sigma says otherwise.
This `1e-2` figure is argued from TF32 magnitude and known nondeterminism sources, not measured by the current harness.
Nothing in the current harness measures the noise directly.

---

## 4. What does not need approval

The following items are inside `models/**` and are mutable without reader escalation.
They should still wait for the scoring/noise decisions when their success criterion depends on leaderboard movement.

| Priority | Work | Why it matters | Evidence |
|---|---|---|---|
| 1 | Add checkpoint resume in `fire_run` | Nine FIRE families discard preempted runs | F07 |
| 2 | Add a per-sample relative-L2 loss term | Eleven families train against a loss that does not match the scored metric | F19 |
| 3 | Cross-fit LF summaries for residual training | The residual net trains on over-optimistic LF predictions | F10 |
| 4 | Guard stale checkpoints against code and shared-code drift | Shape-preserving edits can skip training and emit old-code results | F09 |
| 5 | Repair `fno_mf_stack` | It lacks GroupNorm, grad clipping, and working validation selection | F11 |
| 6 | Hoist `randperm` to epoch scope | Current loops use with-replacement batches while paying full permutation cost per step | F12 |
| 7 | Add HF-stage regularization and validation | Fifteen families have no validation split and the shared HF residual net exposes no dropout | F25 |

---

## 5. Evidence map

All original S/C/B/decimal findings have been renumbered into one register.
Use this map to trace old IDs to the new evidence file.

| New ID | Old ID | Finding |
|---|---|---|
| F01 | S1 | Three incompatible definitions of nRMSE coexist |
| F02 | S2 | Split asymmetry rewards not reporting OOD |
| F03 | S3 | `vs_paper` mixes aggregation rules |
| F04 | S4 | `era5` and `pm_test` are scored against a downsampled target |
| F05 | S5 | No variance estimate exists, and the current leaderboard has a winner's curse |
| F06 | S6 | `code_hash` does not cover shared code |
| F07 | C1 | `fire_run` has no checkpoint resume |
| F08 | C2 | Two families refuse to load their own mid-training checkpoints |
| F09 | C3 | Stale checkpoints can silently skip training entirely |
| F10 | C4 | The residual net trains on in-sample LF predictions |
| F11 | C5 | `fno_mf_stack` has three independent defects |
| F12 | C6 | `randperm` inside the batch loop is not epoch semantics |
| F13 | C7 | Seeding is incomplete |
| F14 | 5.1 | Positivity should use a multiplicative or log-space head |
| F15 | 5.2 | Global integral conservation can be enforced by projection |
| F16 | 5.3 | Divergence-free velocity can be enforced via a stream function |
| F17 | 5.4 | Hard boundary conditions can replace soft Dirichlet penalties |
| F18 | 5.5 | A detection probe is needed before enabling constraints |
| F19 | 6.1 | The training loss does not match the scored metric |
| F20 | 6.2 | The model-selection metric mismatches too |
| F21 | 6.3 | Two families train in raw physical units |
| F22 | B1 | `modes_cap = 12` never scales with resolution |
| F23 | B2 | The backbone is not held constant, contrary to the stated protocol |
| F24 | B3 | LF-stage ensembling is a capacity confound |
| F25 | section 8 | HF-stage regularization is largely absent |
| F26 | section 8 | The smoke/full gap interacts badly with the cosine schedule |
| P01 | section 2 | The physics question favors structural constraints over PDE residuals, with one attribution experiment unresolved |
| U01-U06 | section 10 | Unverified claims and audit limits |

---

## 6. Audit limits

The full limitations section is preserved in `MODEL_TWEAKS_EVIDENCE.md`.
The load-bearing caveat is simple: no data was read, no code was run, only 21 of 30 families are present, and `data_adapters/` internals are incomplete in this checkout.
Every performance claim is therefore a mechanism argument, not a measurement.
