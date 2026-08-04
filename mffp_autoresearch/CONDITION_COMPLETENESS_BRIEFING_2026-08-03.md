# Condition-vector completeness — briefing

**Date:** 2026-08-03.
**Revised:** 2026-08-04 — restructured for clarity (bug / fix options / status); supersedes the 2026-08-03 text, which git history preserves.
**Audience:** Eloise (working note; the mentor-facing one-pager `condition_completeness_proposal/SIGNOFF.md` is now informational — see Part III).
**Purpose:** state the completeness bug precisely, set out the available benchmark designs, and record what was executed and what remains for the round-3 decision.
**Sources read for this revision:** `condition_completeness_proposal/{PROPOSAL.md,SIGNOFF.md,APPROVAL.md,CLUSTER_RUNBOOK.md,cluster_swap_manifest_2026-08-03.json}`, `round2/docs/round2_report.md` §§5 and 9, `round3/state/hardened_gate_2d_validation.json`, `round3/state/anchor_summary_3seed_2026-08-03.json`, `mffp_sharp/pdes/fisher_kpp.py`, and `mffp_sharp/common/completeness.py`.

---

# Part I — The bug

## What the bug was

Three original round-2 panel datasets generated a fresh random initial condition for every sample but exported only the physical scalar parameters in the condition vector.

Those datasets were `sharp__phase_field_crystal_2d`, `sharp__fisher_kpp_2d`, and `sharp__allen_cahn_2d`.

The omitted initial condition is not incidental for these pattern-forming systems.

It determines which particular pattern the PDE evolves into.

The result was that the same visible condition could correspond to many different valid output fields.

A deterministic condition-to-field model was therefore asked to give one answer where the data supplied several.

This is not merely a difficult learning problem.

It is an impossible deterministic mapping under that input contract.

| Original dataset | IC parameters exported | Closest-pair condition distance | Relative field difference | Original verdict |
|---|---:|---:|---:|---|
| `sharp__phase_field_crystal_2d` | 0 | 0.0124 | 1.149 | INCOMPLETE |
| `sharp__fisher_kpp_2d` | 0 | 0.0124 | 0.411 | INCOMPLETE |
| `sharp__allen_cahn_2d` | 0 | 0.0511 | 0.118 | INCOMPLETE |
| `sharp__cahn_hilliard` | 16 (`ic_c0` … `ic_c15`) | 2.8222 | 0.694 | COMPLETE |

For example, two PFC samples whose visible conditions differ by only 1.2% of one standardized unit have fields differing by more than their own magnitude.

Cahn–Hilliard was initially grouped with the defective datasets, but that was a correction-worthy misclassification.

Its initial condition is built directly from the 16 exported coefficients.

Rebuilding its initial condition from the stored condition vector and re-solving reproduced stored fields at relative $L^2$ errors of $1.7\times10^{-14}$, $5.2\times10^{-15}$, and $1.7\times10^{-14}$.

Using another sample’s coefficients as a control instead gave relative $L^2 = 1.346$.

Cahn–Hilliard is complete but difficult to learn from 400 rows in a 19-dimensional condition space.

Its closest pair lies at standardized distance 2.82, versus median pair distance 6.12.

That is a support problem, not missing information.

The distinction matters because cahn_hilliard is the round's only grade A.

Under the corrected reading, LF's grade-A contribution there is a statistically efficient *encoding* of information the condition vector already carries — not information the vector lacks — and the two claims generalise differently.

## Why deterministic models hit a floor

Let $c$ be the exported condition vector and let $\xi$ be the unexported random initial condition.

For the affected original datasets, the field was really $u = F(c,\xi)$.

Any deterministic predictor $g(c)$ has error

$$\mathbb{E}\lVert u-g(c)\rVert^2 = \underbrace{\mathbb{E}\lVert u-\mathbb{E}[u\mid c]\rVert^2}_{\text{irreducible variation from the hidden IC}} + \underbrace{\mathbb{E}\lVert\mathbb{E}[u\mid c]-g(c)\rVert^2}_{\text{error training can reduce}}.$$

The first term is the aleatoric floor.

No deterministic model using only $c$ can remove it.

The best such model can do is predict an average over the possible initial conditions, which can blur or erase the individual pattern being scored.

The round-2 training-free diagnostic measured these floors in copy-LF skill units.

| Dataset | Aleatoric floor in copy-LF skill units |
|---|---:|
| `fisher_kpp` | approximately 11.44 |
| `phase_field_crystal` | approximately 38.6–42.1 |
| `allen_cahn` | approximately 132.7 |

The certifier was already within $1.01\text{–}1.14\times$ of those barriers.

The frozen best floors were still $1.3\text{–}4.2\times$ above them.

Therefore, on the original defective datasets, “beats the best training-free floor” was a weak test.

A model could clear that bar without learning the missing initial-condition-to-pattern map.

Skill approaching $1$ was structurally unavailable because copy-LF used the realized initial condition while the condition-only model did not.

## Why those three datasets drew a random field, and the safe datasets did not

A "uniform state" means the field has exactly the same value at every point in space — a completely flat, featureless picture.

For Cahn–Hilliard it is a mixture blended perfectly evenly; for Fisher–KPP it is a population at exactly the same density everywhere; for PFC it is matter at exactly the mean density with no crystal structure.

These equations apply the same local update rule at every point in space.

If every point starts with the same value, every point receives the same update at every step, so the field stays perfectly flat forever.

No pattern can ever appear, because nothing in the equation distinguishes one location from another — symmetry cannot break itself.

For the phase-separating equations the flat state is unstable on top of being stuck: the physics *wants* to unmix, and any tiny unevenness grows exponentially — the pencil balanced exactly on its tip.

But "wants to" is not enough; the system still needs some unevenness to tell it *where* the domains, fronts, or crystals go.

So the generator adds a small random bumpy perturbation, and that nudge — not the scalar parameters — decides which pattern appears.

The standard physics recipe is therefore "mean state plus small random noise," with broad-spectrum noise chosen deliberately so the physics, not the generator, selects the winning pattern.

There is a second reason to randomize the start: with one fixed IC and only $D$ and $r$ varying, 500 samples would be 500 versions of a single pattern at different length scales.

In the physics literature that noise realization is a nuisance variable you average over, and $\varepsilon$, mobility, and mean composition genuinely are "the parameters of Cahn–Hilliard."

The category error is subtle: the IC is a parameter of the problem *instance*, not of the *equation* — physics conditions on equations, while supervised learning conditions on instances.

The safe datasets never faced this trap, because their ICs are shapes with a handful of natural parameters: `burgers` has `ic_amplitude` and `ic_freq`, `shallow_water` has `inner_height` and `dam_radius`, `helmholtz` has `wavenumber` and `source_width`, and `sod` has its left/right Riemann states.

For those, exporting the parameters is the only way to write the IC down at all, so completeness came for free.

A pattern former instead needs a broad-spectrum *field* to start from, and turning that into a few exportable numbers requires a deliberate extra design move — option A's band-limiting — which also changes the dynamics.

`sharp__cahn_hilliard` avoided the bug only because it happened to be generated by the 2026-06-28 standalone script that already encoded its IC coefficients; the package path reproduced the old convention until the repair.

## Why this happened, and why round 1 could not reveal it

The generators were written for a regime where a model received an LF field as well as the small condition vector.

In that regime, the LF field already carries the realized initial-condition information.

The condition vector was only a side input, so its incompleteness was not load-bearing.

Round 1 therefore could not expose this defect.

Round 2 removed LF fields at test time and asked for condition-to-HF prediction, which made the omission decisive.

The same defect had been found on 2026-06-28 and repaired in a standalone generation script, but not in the package’s documented generation path.

Later package-path generation therefore reproduced the old convention.

The earlier sweep also searched for a symptom, roughly “all models have relative error above one,” rather than checking every generator for “draws an IC that it does not export.”

PFC, Fisher–KPP, and Allen–Cahn could look passable on bulk-level metrics while still missing the pattern-setting input.

The general lesson is simple.

A defect found by symptom is not closed until the construction itself is checked and guarded.

---

# Part II — The fix options

The choice is not between “fixed” and “unfixed.”

There are three honest benchmark designs, each suited to a different question, plus one tempting shortcut that must stay rejected.

## A. Band-limited parametric initial condition

This is the executed repair.

Instead of drawing a full random grid field, the generator draws a limited set of low-Fourier-mode coefficients and stores those coefficients in the condition vector.

The initial condition is then exactly reconstructible from the stored vector.

Conceptually, this is like naming the notes of a chord rather than transcribing every point of an audio waveform.

A two-dimensional IC carries 16 coefficients at `ic_modes=3` or 48 at `ic_modes=5`, giving 18–50 total condition dimensions once the physical scalars are included.

The field is complete by construction because those coefficients are the initial condition’s recipe.

| What it buys | What it costs | Natural use case |
|---|---|---|
| A deterministic condition-to-field map. | A higher-dimensional condition vector. | Engineering surrogate models: design parameters $\rightarrow$ one predicted field. |
| A reconstruction certificate. | Fewer fine IC features can make LF and HF too similar. | Cases where a vector input is required. |
| A conventional supervised prediction target. | A possible support problem at fixed row count. | Controlled parametric studies. |

The central trade-off is a trilemma.

For a field-valued IC, one can usually keep only two of these three properties: a complete condition, a small vector, and rich LF–HF dynamics.

| Dataset or recipe | Complete condition | Small vector | Rich LF–HF gap |
|---|---|---|---|
| Original PFC / Fisher–KPP / Allen–Cahn | No | Yes | Often yes, subject to PFC’s separate no-gap issue |
| Existing Cahn–Hilliard | Yes | No: 19-D | Yes: approximately $1.5\times10^{-2}$ at $T=5.0$ |
| Fisher–KPP, low-mode first pass | Yes | Approximately 18-D at $m=3$ | No: approximately $4\times10^{-5}$ on the canonical measure |
| Fisher–KPP, final recipe | Yes | No: 50-D at $m=5$ | Weak: approximately $3.2\times10^{-4}$ at $T=0.30$ |

The final Fisher–KPP choice was explicit.

It uses `ic_modes=5`, producing a 50-dimensional condition vector, and thereby gives up the small-vector corner for that dataset.

Per the module docstring, the wider mode square was chosen because it raises front density (more IC level crossings), not because it widens the fidelity gap.

Mode count is not a fidelity-gap lever at all.

On the canonical LF-to-HF residual, Fisher–KPP at $T=0.30$ measured approximately $4.6\times10^{-4}$ at $m=3$ and $3.2\times10^{-4}$ at $m=5$.

The useful lever is allowing enough solve time for nonlinear structure to develop, while remaining inside the predictability horizon.

For context, the original white-noise Fisher–KPP data had canonical gap approximately $7.4\times10^{-2}$, while its first short-time band-limited regeneration measured approximately $4\times10^{-5}$.

The corresponding Allen–Cahn values were approximately $5.6\times10^{-3}$ for the shipped white-noise data and approximately $1.5\times10^{-4}$ for the first short-time band-limited regeneration.

PFC had no meaningful fidelity gap before the repair or after it, with measurements approximately $8.3\times10^{-6}$ and $1.2\times10^{-6}$ — a pre-existing round-2 finding and a panel-composition question, not an IC-fix regression.

## B. Declared stochastic map

This option deliberately keeps random, unexported initial conditions.

The dataset must declare `stochastic_map`.

It must also ship the measured aleatoric floor and use distributional scoring rather than scoring a deterministic point prediction against an unattainable skill target.

| What it buys | What it costs | Natural use case |
|---|---|---|
| Keeps broad-spectrum random ICs and their pattern-forming physics. | It is not a deterministic design-parameter-to-field benchmark. | Scientific or statistical questions about an ensemble of patterns. |
| Retains a small physical-parameter vector. | Models must predict distributions, summaries, or calibrated samples. | Pattern formers where a small condition vector is important. |
| Makes the irreducible uncertainty explicit. | Requires a different score and reporting contract. | Studies of variability rather than a single realized field. |

This is an honest way to preserve rich dynamics at small condition dimension.

No dataset currently declares `stochastic_map`.

It remains a standing option for the round-3 panel-composition ADR.

## C. Supply the realized IC field as a model input

This is the 2026-08-04 addendum and a proposed formal part 4 of the completeness package.

The dataset would ship a small vector of physical parameters together with the realized initial-condition field as an input channel.

This is the standard operator-learning formulation used by FNO, DeepONet, and PDEBench.

It is not the round-1 LF-field leak.

An LF field is a cheap partial solve of the answer.

An initial condition is part of the question the user supplied.

A raw seed is only a discontinuous label for that question.

The IC field itself is the continuous physical input.

| What it buys | What it costs | Natural use case |
|---|---|---|
| A complete deterministic input while preserving broad-spectrum ICs. | Changes the benchmark question from vector-to-field regression to operator learning. | ML operator-learning benchmarks. |
| Preserves the original LF–HF gap. | Models need a field-input channel at test time. | PDE solution operators with field-valued initial states. |
| Keeps the physical scalar vector small. | Requires versioned data and model-interface changes. | Real applications where the starting field is known. |

This option dissolves the trilemma by dropping the assumption that every condition must be a short vector.

It does not make every finite-time map easy.

For chaotic systems, or pattern formers evolved too far past their transient, sensitivity to the IC can make pointwise prediction unusable after a predictability horizon.

In that case, even an IC-field input may need stochastic or distributional scoring.

The qualification is therefore two-part.

The PDE must genuinely depend on a field-valued input without a natural few-number description, and the snapshot time must remain inside its useful predictability horizon.

| PDE group | Modules | Qualification for IC-field input |
|---|---|---|
| Pattern formers | `cahn_hilliard`, `allen_cahn`, `phase_field_crystal`, `swift_hohenberg`, `gray_scott`, `fisher_kpp` | Yes, especially where the trilemma is active. |
| Dispersive or wave systems | `kdv`, `nls`, `sine_gordon` | Yes, as information-preserving operator-learning targets. |
| Chaotic systems | `kuramoto_sivashinsky`, and pattern formers far beyond transient | Only inside a per-PDE predictability horizon. |
| Parametric IC systems | `burgers`, `porous_medium`, `shallow_water`, `sod`, `euler` | No, because a $64^2$ field would merely restate 2–7 scalar inputs. |
| Elliptic or steady systems | `helmholtz`, `poisson`, `eikonal` | No IC exists, although a random coefficient or source field would be a separate redesign. |

For the original PFC, Fisher–KPP, and Allen–Cahn datasets, this option is likely retrofittable without re-solving.

The stored seeds can reconstruct the realized IC arrays, subject to verifying reconstruction with the existing certificate.

The `burgers_param_generated` retrofit in Part III demonstrates the pattern: values re-derived from the generation RNG chain, exported, and certified with no re-solve.

Option C is drafted here but is not yet a formal part 4 in `condition_completeness_proposal/`.

## D. Export the seed

This is a rejected non-fix.

Exporting the seed would let code reconstruct the exact IC and would therefore pass reconstruction alone.

It would not make the learning problem smooth or learnable.

A seed is a discontinuous pseudorandom hash label, not a physical coordinate system for nearby initial conditions.

Nearby numeric seed values do not produce nearby fields.

A model would still face essentially unseen labels at test time.

This is why the hardened gate now requires more than exact reconstruction.

It uses a witness veto and a two-scale continuity probe to distinguish true coefficients from seed or nominal exports.

## Adjudication

Option A is the engineering-surrogate corner.

It best fits a benchmark asking for design parameters to predict one field.

Option B is the science-and-statistics corner.

It best fits a benchmark asking about ensemble behavior of pattern-forming systems at small parameter dimension.

Option C is the ML operator-learning corner.

It best fits a benchmark asking a model to evolve a supplied field-valued state.

The panel may mix these designs per dataset, provided each dataset states its contract and is scored accordingly.

In the repaired round-3 panel, PFC, Fisher–KPP, and Allen–Cahn use option A.

Cahn–Hilliard already uses option A in the broad sense that its IC coefficients are stored in the condition vector, although its 19-dimensional vector exposes the support cost.

No current dataset uses option B.

No current dataset uses option C.

IFC, Helmholtz, and other datasets without this field-IC issue sit outside this specific three-corner decision.

---

# Part III — Status

## Executed and verified

The mentor sign-off gate was waived on 2026-08-03.

`condition_completeness_proposal/APPROVAL.md` records Eloise’s direction that her operator approval was sufficient.

`condition_completeness_proposal/SIGNOFF.md` remains as an informational technical one-pager.

The repair pipeline was executed on the cluster on 2026-08-03.

Commit `192c6ea` records the package-level IC encoding and completeness generation gate, as specified by `condition_completeness_proposal/CLUSTER_RUNBOOK.md`.

Five sharp variants were regenerated through the fixed path and swapped in.

| Regenerated variant | Final recipe detail | Completeness evidence |
|---|---|---|
| `phase_field_crystal_2d` | Fixed-path regeneration. | COMPLETE, reconstruction relative $L^2 = 0.0$. |
| `fisher_kpp_2d` | $T=0.30$, `ic_modes=5`, 50-D condition vector. | COMPLETE, reconstruction relative $L^2 = 0.0$. |
| `allen_cahn_2d` | $\varepsilon\in[0.012,0.02]$ coupled to the ladder, $T=10$. | COMPLETE, reconstruction relative $L^2 = 0.0$. |
| `fisher_kpp_1d` | Fixed-path regeneration. | COMPLETE, reconstruction relative $L^2 = 0.0$. |
| `allen_cahn_1d` | Fixed-path regeneration. | COMPLETE, reconstruction relative $L^2 = 0.0$. |

The swap record is `condition_completeness_proposal/cluster_swap_manifest_2026-08-03.json`.

The previous arrays were archived under `_incomplete_backup_2026-08-03/`.

They were never deleted.

Round-2 and repaired-panel skills are not comparable on regenerated datasets.

The data contract and copy-LF denominators changed, rather than merely the model quality.

The repaired-panel preflight passed.

The archived report is `round3/state/preflight_repaired_panel_2026-08-03.json`.

Its two adjudicated waivers are documented in `round3/state/preflight_waiver_evidence_2026-08-03.md`.

The Helmholtz witness waiver was a resonance-sensitivity false positive, with re-solving from the condition reproducing flagged rows at relative $L^2$ near $10^{-15}$.

The Sod pairing waiver reflected near-duplicate Riemann rows, while cross-level condition arrays were bit-identical.

The three-seed repaired-panel anchor re-score is complete.

The evidence is `round3/state/anchor_summary_3seed_2026-08-03.json`, recorded by commit `4efe5df`.

The repaired-panel best-floor anchor is 46.3911 (lower is better), recorded by commit `91809f2` with the repaired floor artifacts in `round3/state/anchors_repaired/`.

| Card | Repaired-panel three-seed mean [95% CI] | Round-2 single-seed (not comparable — honest-denominator effect) |
|---|---:|---:|
| `r2s2-B1` frozen stack | 24.3725 [22.953, 25.792] | 14.0755 |
| `r2s1-B2` closed-form head | 34.3634 [34.311, 34.416] | 18.3622 |
| `r2s1-B3` out-of-fold head | 39.1843 [39.081, 39.287] | 18.7500 |

The round-2 ranking survives, and every card still beats the repaired best-floor anchor.

## Gate hardening (formerly §8)

The old §8 hardening findings were executed the same day under the same approval.

The generation gate now treats the nearest-pair witness as a veto rather than a note.

Its proximity threshold scales to the dataset’s own median pair distance, so condition-vector dimension inflation cannot disarm it.

The gate also runs a two-scale continuity probe.

A genuine continuous coefficient produces a response that shrinks with the perturbation size.

A seed or nominal label produces a step-like or non-smooth response instead.

The current gate semantics are documented in `mffp_sharp/common/completeness.py`.

Fisher–KPP 2-D and Allen–Cahn 2-D were re-certified under the hardened gate by commit `82c3f23`.

The evidence is `round3/state/hardened_gate_2d_validation.json`.

Fisher–KPP 2-D is COMPLETE and SMOOTH across all 50 condition dimensions.

Allen–Cahn 2-D is COMPLETE and SMOOTH across all 19 condition dimensions.

The extension-tree audit adjudicated `ext/cahn_hilliard_2d`, `ext/gray_scott_2d`, and `ext/kuramoto_sivashinsky_1d` COMPLETE by exact reconstruction from stored conditions.

Each measured relative $L^2 = 0.0$.

The Kuramoto–Sivashinsky witness failure reflects chaotic amplification, not missing information.

The ext-tree Cahn–Hilliard data turned out to share one fixed IC realization across samples, and its underlying batch-position seeding bug (same row, different field depending on call batching) was fixed with an explicit constant seed.

No regeneration was needed for those datasets.

The repo-wide sweep the old §8.3 prescribed also found a fourth occurrence of the defect class: `core/burgers_param_generated` drew per-sample IC phases and never exported them.

It was repaired in place, without re-solving: the phases were re-derived through the generation RNG chain (amps and `log10_nu` reproduce the stored `x` bit-for-bit) and appended as condition columns.

All 500 post-retrofit rows reconstruct at relative $L^2 = 0.0$.

The earlier §8.2 complaint is resolved and obsolete.

The current `fisher_kpp.py` docstring retracts the stale block-average gap figures and states that mode count is not the principal fidelity-gap lever.

It documents the canonical $T=0.30$ measurements of approximately $4.6\times10^{-4}$ at $m=3$ and $3.2\times10^{-4}$ at $m=5$.

The production Fisher–KPP 2-D recipe uses `ic_modes=5`.

## Other verified panel work

The shipped IFC ladders are disjoint at every rung pair.

Nested-condition repaired IFC ladders were regenerated and staged in `mffp_autoresearch/ifc_pairing_repair/`.

They achieve row-match 1.0.

The shipped ladders remain untouched pending the round-3 panel-composition ADR.

## Still open

The remaining fidelity-gap recipe question is `true_gap_sweep`.

Its documented PFC and Fisher–KPP weak-gap physics flags are inputs to the round-3 panel ADR.

The round-3 panel-composition ADR remains open.

It must decide which datasets should use options A, B, or C and whether the staged IFC ladders should replace the shipped ladders.

Option C, IC field as an input, remains drafted in this briefing but has not yet been formalized as part 4 of `condition_completeness_proposal/`.

No dataset currently declares `stochastic_map`.

That choice remains available if the panel decides a small-vector, distributional benchmark is more appropriate than the complete-vector repair for a given pattern former.

---

# Appendix — Conceptual grounding for write-ups

A PDE is a rule, not a picture.

For Fisher–KPP, $u_t=D\nabla^2u+r u(1-u)$ gives the evolution rule and its coefficients.

It does not specify one particular solution.

A complete problem instance also needs the domain, boundary conditions, initial condition, and snapshot time.

The rules of chess fit on a card, but they do not tell you the board position at move 40.

The opening position is also needed.

Pattern-forming PDEs amplify their initial state.

A perfectly uniform unstable state can remain exactly uniform forever, like a pencil balanced exactly on its tip.

The perturbation that breaks symmetry is therefore part of the realized problem instance.

The physical coefficients set the style of the behavior, such as front width or interface thickness.

The initial condition selects which pattern actually appears.

| PDE family | Relation to initial condition | Consequence |
|---|---|---|
| Heat and diffusion | Often forget the start. | Omitting the IC may cost little. |
| Elliptic problems such as Poisson | Have no time-evolving IC. | There is no IC to omit. |
| Pattern formers such as Cahn–Hilliard, Allen–Cahn, PFC, and Fisher–KPP | Amplify small initial differences into distinct patterns. | The IC is a principal input. |

Sharpness is not the deciding axis.

The relevant question is whether the problem instance needs a field-valued starting state or can be described naturally by a few physical numbers.
