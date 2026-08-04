# Condition-vector completeness — briefing

**Date:** 2026-08-03.
**Audience:** Eloise (working note; not the mentor-facing ask — that is `condition_completeness_proposal/SIGNOFF.md`).
**Purpose:** one place that holds the whole condition-completeness story — what the defect is, why it bounds round 2, why round 1 could not see it, how the fix works, and what is still open.
**Sources read for this note:** `condition_completeness_proposal/{PROPOSAL.md,certificate_results.json,sample_round/*/meta.json}`, `round2/docs/round2_report.md` §§1–6, `round2/program.md` §§1–2.3, `round1/docs/round1_report.md` §§1–5, `round1/program.md` §2.3, `PROFESSOR_UPDATE_2026-08-02.md`, `mffp_sharp/src/mffp_sharp/{common/ic_encoding.py,common/completeness.py,generate.py,pdes/*.py}`, `mf_field_extension_data/{solvers.py,generate_datasets.py}`.

---

## 0. Decisions waiting on you

Three items surfaced in this session that are **not** in the sign-off package.
Sections 8.1–8.3 carry the detail.

| # | Item | Where | Why it needs a decision |
|---|---|---|---|
| 1 | The completeness gate would certify a seed-padded condition vector as COMPLETE | `mffp_sharp/common/completeness.py` | The gate is part 2 of the package now queued for mentor sign-off; shipping it with this hole admits exactly the shortcut the gate exists to reject |
| 2 | `fisher_kpp.py`'s `ic_modes=3` default is justified in its docstring by numbers `PROPOSAL.md` itself retracts | `mffp_sharp/pdes/fisher_kpp.py` | Same package, same sign-off; the live default rests on a superseded instrument |
| 3 | The identical defect exists in `mf_field_extension_data` (Cahn–Hilliard), a code path the fix package does not touch | `mf_field_extension_data/{solvers.py:169,generate_datasets.py:277}` | Third independent occurrence; suggests a repo-wide sweep rather than another point fix |

Items 1 and 2 are inside a deliverable about to go outward, so they are your call, not mine.
Item 3 is cheap to fix (the IC there is already band-limited — the drawn values just are not exported) and cheap to sweep for.

---

## 1. The finding, and the correction to it

The claim as originally written, and as it still appears in some carried-forward text:

> The condition vector is NOT complete on 4 of 6 panel datasets (pfc, fisher_kpp, allen_cahn by construction — no initial-condition parameters exist in the vector; cahn_hilliard by measurement).

That wording is **superseded**.
`round2/docs/round2_report.md` §5.1 and `PROFESSOR_UPDATE_2026-08-02.md:65` now both read **3 of 6**.

| dataset | IC params exported | closest-pair condition distance | their relative field difference | verdict |
|---|---|---|---|---|
| `sharp__phase_field_crystal_2d` | 0 | 0.0124 | **1.149** | INCOMPLETE |
| `sharp__fisher_kpp_2d` | 0 | 0.0124 | **0.411** | INCOMPLETE |
| `sharp__allen_cahn_2d` | 0 | 0.0511 | **0.118** | INCOMPLETE |
| `sharp__cahn_hilliard` | 16 (`ic_c0…15`) | 2.822 | 0.694 | **COMPLETE** |

For the three INCOMPLETE datasets the generator did this:

```python
rng = np.random.default_rng(spec["seed"])            # seed = base + sample index
ic_coarse = 0.5 + 0.5 * (2 * rng.random(shape) - 1)  # white noise, 64² = 4096 dof
cond = np.array([spec["D"], spec["r"]])              # the IC is not in here
```

Two pfc samples whose conditions agree to 1.2 % of one standard deviation have fields differing by more than their own magnitude.
That is two different labels on the same input, not a hard learning problem.

**Why cahn_hilliard is not in that list.**
Its IC is *built from* `ic_c0…ic_c15`, so the field is a deterministic function of `x` by construction.
`certify_condition_completeness.py` verifies this rather than arguing it: rebuild the IC from the stored `x` alone, re-solve, compare to disk.

```
rel-L2(rebuilt from x alone, vs stored field)   =  1.7e-14, 5.2e-15, 1.7e-14   (3 samples)
control — same physics, another sample's coeffs =  1.346
```

What the r2s2-B3 paired-LF cosine measured on cahn_hilliard is a **support** limit, not an information limit: 400 training rows in 19 condition dimensions, closest pair at standardized distance 2.82 against a median of 6.12.
Nothing has near-neighbour support anywhere.
Extending the incompleteness finding to it was itself a violation of the round's own §6 "unidentifiable" phrasing rule.

This changes how the round's only grade A reads.
On cahn_hilliard, LF supplies a statistically efficient *encoding* of information the condition vector already carries — not information the vector lacks.
Both are real results; they generalise differently.

---

## 2. Why incompleteness caps deterministic models

If the true field is $u = F(c, \xi)$ with $\xi$ the unexported IC seed, then for any deterministic predictor $g(c)$:

$$\mathbb{E}\|u - g(c)\|^2 = \underbrace{\mathbb{E}\|u - \mathbb{E}[u \mid c]\|^2}_{\text{aleatoric, irreducible}} + \underbrace{\mathbb{E}\|\mathbb{E}[u \mid c] - g(c)\|^2}_{\text{what training can reduce}}$$

The first term does not depend on $g$.
The best any condition-only model can do is emit the conditional mean — a blur averaged over every IC consistent with those scalars.

r2s4-B1 measured that floor training-free, in copy-LF skill units: **~11.44 (fisher_kpp), ~38.6–42.1 (pfc), ~132.7 (allen_cahn)**.
The round's certifier already sits within 1.01–1.14× of it.
The models were at the wall, not approaching it.

**Why $\mathrm{skill} \to 1$ is unreachable in principle** is a denominator argument.
$\mathrm{skill} = \mathrm{nRMSE}(\text{model}) / \mathrm{nRMSE}(\text{copy-LF})$, and copy-LF is a real coarse solve *of the same realised IC*.
The denominator holds the missing variable; the numerator is structurally forbidden it.
This is not two models compared fairly — it is a model asked to match something that read the answer key.

Consequence recorded in §5.2 of the round-2 report: the frozen best floors sit **1.3–4.2× above** those aleatoric barriers, so "beats the best training-free floor" is a weak bar on those three datasets.
A model can clear it while learning nothing about the operator.

---

## 3. How round-2 models were actually evaluated

On the full **6-dataset panel** (`round2/program.md` §2.3), scored as a geometric mean of per-dataset skill, with a per-dataset skill table mandatory in every card's part 5 — the geomean never appears alone.

```
ext__helmholtz_2d · ifc_poisson · sharp__cahn_hilliard
sharp__fisher_kpp_2d · sharp__phase_field_crystal_2d · sharp__allen_cahn_2d
```

Guard datasets (`fluid`, `heat_local`, `sharp__sod_1d`) exist to catch harness breakage and are not meant to be won.

Headline numbers: launch anchor 23.0636, panel mce 1.1419, certified 3-seed anchor **19.8178** CI95 [19.385, 20.527] (r2s4-B1 — the round's only certified number).
Best per-dataset skills: helmholtz 2.815, ifc 2.150, ch 11.279, fk 11.574, pfc 47.455, ac 146.86.
None approached 1 anywhere.

But the *interpretable* panel is much narrower than six, and this is worth holding onto:

| cell | status |
|---|---|
| pfc, fisher_kpp, allen_cahn | aleatoric-capped — measurements of conditional-mean estimation, not operator learning |
| `ifc_poisson` | degenerate: HF side affine (LOO residual $3.2\times10^{-8}$ at every rung) **and** ladder mispaired (170 LF rows at conditions with no HF row, 0 conditions covered at every rung — invalidates every $hf-lf$, LF-teacher and copy-LF construction on it) |
| `ext__helmholtz_2d` | its best training-free floor is the zero field; report-only discipline continues |
| `sharp__cahn_hilliard` | the only cell that survives the r2s3-B4 ceiling gate, and the round's only grade A |

The geomean is a real number over six cells.
Only one of them cleanly supports a value-of-LF conclusion, which is exactly why the cahn_hilliard misclassification mattered enough to correct.

---

## 4. Why round 1 did not catch it

**Round 1 handed the model the LF field at test time.**
The condition vector was not load-bearing, so its incompleteness could not show.

| | round 1 | round 2 |
|---|---|---|
| model input at test | LF field **+** condition vector | condition vector **alone** (test LF files physically absent) |
| best panel geomean skill | **0.1233** | **19.82** certified |

Same six datasets, same data.
The unexported seed $\xi$ is exactly what the LF field is a solve *of*, so in round 1 it was fully present in the input — just through the other channel.
A missing variable in a side-channel is not a defect while the main channel already determines the answer.

Round 1's own §5.1 makes this concrete: sharp-panel "wins" were **~96–100 % re-learned registration**, i.e. models largely correcting the $(r-1)/2$ half-cell interpolation shift on the LF field.
That is the signature of a regime where the answer is already in the input and only needs cleanup.
Nothing in that workload asks whether `[D, r]` determines anything.

Three secondary reasons it stayed hidden:

1. **The identical bug was found on 2026-06-28 and triaged by symptom.** The symptom used was *"rel-L2 > 1 for every model."* pfc / fk / ac are level-dominated — `mean_density` / `mean_composition` predicts the bulk — so they score respectably while blind to the pattern driver, and the symptom sweep walked past them.
2. **That fix landed beside the package, not in it.** `mf_field_eloise_data/generate_learnable.py` imports the package's solvers but bypasses `sample_configs` / `generate_sample`. It regenerated 9 variants; the package itself was unchanged, so everything generated afterwards through the documented path reproduced the original convention.
3. **The rule existed but had no executable check.** `SURF_2026-main/CLAUDE.md` has always said the condition vector must be complete. `common/completeness.py` and `tests/test_completeness.py` are dated 2026-08-03. For the package's whole life "complete" was enforced by someone remembering to think about it while adding a PDE.

Round-1 near-miss: its between-rounds fix list did include "pfc redesign", but for the denominator problem (pfc has essentially no fidelity gap), not for IC completeness.
Right dataset, wrong axis.

---

## 5. Why the variables were missing in the first place

Four causes stacked; only the last is a mistake in the ordinary sense.

**5.1 The regime made the omission free.**
The benchmark was defined as predicting HF *from LF fields plus a small condition vector*.
The condition vector was a conditioning hint alongside a field input, never intended as a sufficient statistic.
In that regime the word "complete" was effectively untestable — you cannot notice that a vector fails to determine the field while the model is also being handed a solve of it.

**5.2 The physics convention says the IC noise is not a parameter.**
For pattern-forming PDEs the canonical setup is *mean state + small random perturbation*, where the perturbation exists to break symmetry so the instability can start.
$\varepsilon$, mobility, mean composition genuinely *are* "the parameters of Cahn–Hilliard" in the cited literature; the noise realisation is a nuisance variable you average over.
The category error is subtle: the IC is a parameter of the **problem instance**, not of the **equation**.
Physics conditions on equations.
Supervised learning conditions on instances.

**5.3 The rule was prose, not a test.**
See §4.3.
A rule with no executable form fails predictably the moment a new module is written by copying a neighbouring one, and there are 16 PDE modules.

**5.4 The safe pattern could not propagate by imitation.**
The June fix header names the precedent — *"like the working burgers/darcy datasets do"* — and the unaffected modules do exactly that (`burgers` → `ic_amplitude, ic_freq`; `helmholtz` → `wavenumber, source_width`; `shallow_water` → `inner_height, dam_radius`; `sod` → `rho_l, p_l`).
But that is not attention, it is the physics: those ICs are *shapes with parameters*, and parameterising them is the only way to write them down.
Pattern formers need a *broad-spectrum field*, and getting a finite parameterisation out of that requires a deliberate extra design move that changes the dynamics.

**The compounding step** — the one worth generalising from — is that a defect found by symptom was not closed by construction.
The right query was *"which generators draw a field they do not export?"*, a grep for `default_rng` reached from a per-sample IC builder, which returns all ten.
The query actually run was *"which datasets score above 1?"*, which returned nine.

---

## 6. How the fix works

**Principle:** stop drawing a random field and keeping the seed; draw the field's *parameters* in the design and build the field from them.

The obstacle is that a starting picture on a $64^2$ grid has 4096 independent values.
The way out is that an *arbitrary* picture was never needed — only some bumpy pattern for the physics to grow from.
So restrict to the few smoothest wave patterns and add them with adjustable weights, like naming a chord instead of transcribing a waveform:

$$\mathrm{IC}(x,y) \;=\; \frac{s}{\max|f|}\sum_{(k_x,k_y)\neq(0,0)} \big[a_k\cos(k_x x + k_y y) + b_k\sin(k_x x + k_y y)\big]$$

At the default $m=3$ that is 8 modes × 2 weights = **16 coefficients**, and they do not approximate the IC — they *are* it, exactly.

Three steps in code (`mffp_sharp/pdes/fisher_kpp.py`):

```python
# 1. the recipe is drawn as ordinary parameters, in the same Latin hypercube
draws = latin_hypercube({"D": ..., "r": ..., **ic_encoding.ic_ranges(ndim, m2d)}, n, seed)

# 2. the picture is built from the recipe — generate_sample never opens an RNG
coeffs    = ic_encoding.coeffs_from_spec(spec, ndim, m2d)
ic_coarse = 0.5 + ic_encoding.build_ic(coeffs, res_min, 0.5, ndim)

# 3. the recipe ships with the question
cond  = np.array([spec["D"], spec["r"], *coeffs])
names = ["D", "r"] + ic_encoding.ic_names(ndim, m2d)
```

`spec["seed"]` still exists but nothing reads it for the IC.
The condition vector goes from 2 numbers to 18.

**One structural detail that matters:** the IC is built once on the coarsest grid then spectrally interpolated up, so every rung starts from the *same continuous* initial condition.
Building independently per grid would make the levels solve different problems and quietly destroy the meaning of $\mathrm{HF}-\mathrm{LF}$.

**Coverage — 16 modules:**

| group | count | modules |
|---|---|---|
| IC-encoded (were affected, now fixed) | 10 | fisher_kpp, allen_cahn, phase_field_crystal, cahn_hilliard, nls, gray_scott, kuramoto_sivashinsky, swift_hohenberg, kdv, sine_gordon |
| parametric scalar IC (never affected) | 5 | burgers, helmholtz, porous_medium, shallow_water, sod |
| Riemann-quadrant IC (never affected) | 1 | euler (7-number condition vector) |

**Verification** — the test reproduces rather than argues.
Take the condition vector off disk, rebuild the IC, re-solve, compare:

```
rel-L2(rebuilt from x alone, vs stored field)  =  0.0     ← exact, identical deterministic path
control: same physics, another sample's coeffs =  1.346   ← proves the test can fail
```

Wired as a hard gate in `generate.py` (`SystemExit` on INCOMPLETE unless the block declares `stochastic_map`) and written into `meta.json`.
Sample round: 10 samples × 3 production-ladder rungs per dataset, every `meta.json` reads COMPLETE with reconstruction rel-L2 = 0.0.
Full suite 149 passed, 9 skipped.

---

## 7. What the fix costs — the trilemma

Sharpness is not the variable; **is the IC a shape or a field** is the variable.
And for field-IC PDEs you can have two of these three corners, not all three:

| | complete | small (≤ ~10) | rich dynamics (real LF–HF gap) |
|---|---|---|---|
| pfc / fk / ac as shipped | ✗ | ✓ | ✓ |
| cahn_hilliard as shipped | ✓ | ✗ (19-D) | ✓ (1.5e-2) |
| fk band-limited, `ic_modes=3` | ✓ | ✓-ish (18-D) | ✗ (~4e-5 — copy-LF near-perfect) |
| fk at `ic_modes=5` | ✓ | ✗ (50-D) | ✓ |

Two costs, both real and both open:

- **Dimension.** 18–19 params against a ≤ ~10 methodology cap. Being complete but high-dimensional trades an *information* wall for a *support* wall — cahn_hilliard is complete and still unidentifiable at 400 rows in 19 dimensions.
- **Flattened dynamics.** Restricting to 8 smooth modes gives the coarse grid less fine structure to miss, so LF and HF can agree almost perfectly and the benchmark goes trivial from the other end. On the canonical residual measure the first-pass regenerations give fk ~4e-5 (shipped 7.4e-2) and ac ~1.5e-4 (shipped 5.6e-3); cahn_hilliard keeps a genuine 1.5e-2 at $T=5.0$. **The lever that matters is solve time for nonlinear structure to build, not IC mode count alone.**

Also unrepairable in place: pfc / fk / ac ICs are white-noise fields at 4096 dof, so no small vector describes them after the fact.
They must be regenerated — solver time only, 500 samples × 3 rungs, no algorithmic change.

Part 3 of the proposal (declare `stochastic_map`, ship the aleatoric floor, score distributionally) is therefore a genuine option rather than a consolation prize.
For pattern-forming PDEs it may be the only corner that stays honest at ≤ 10 dimensions.

---

## 8. Open findings from this session (not in the sign-off package)

### 8.1 The completeness gate would pass a seed-padded vector

Exporting the raw RNG seed would be an illegitimate "fix": a seed is a nominal label, the map seed → IC is a PRNG hash with no continuity, and every test seed is a value never seen in training — the achievable error would still equal the aleatoric floor.
It would relabel the impossibility, not remove it.

**But it would certify COMPLETE.**
Rebuild the IC from the seed, re-solve → machine precision.
In `common/completeness.py::certify`, the witness is computed, written to `meta.json`, and then **not consulted** whenever reconstruction is available:

```python
if mod is not None and reconstruction_failure is None:
    complete = record["reconstruction"]["verdict"] == "COMPLETE"
    witness_only = False
else:
    complete = not (w["relative_field_difference"] > WITNESS_REL_MIN
                    and w["standardized_condition_distance"] < WITNESS_DIST_MAX)
    witness_only = True
...
if complete and not witness_only:
    record["verdict"] = "COMPLETE"
```

There is a second layer.
`WITNESS_DIST_MAX = 0.5` is absolute in standardized units, which makes it dimension-blind:

| dataset | condition dim | nearest-pair distance | fires at $< 0.5$? |
|---|---|---|---|
| fisher_kpp, as shipped | 2 | 0.0124 | yes, easily |
| fisher_kpp, sample round | 18 | 4.752 | never |
| allen_cahn, sample round | 19 | 3.987 | never |

The detector works precisely where it is no longer needed and is unreachable precisely where it would be.
The same dimension inflation that "fixes" completeness disarms the instrument that checks it.

**Proposed change:** make the witness a veto rather than a note, and scale its threshold to the dataset's own median pair distance — e.g. fire on `dist < 0.1 × median_pair_distance` and `rel_field_diff > 0.1`.
Checked against the three certified sample-round metas, none would flip: their nearest pairs sit at 0.61–0.75× the median, far above a 0.1× trip point.

### 8.2 `ic_modes=3` is defended by a retracted measurement

`pdes/fisher_kpp.py`'s docstring:

> *"8 low modes leave the LF-vs-HF gap near the NO_GAP floor (measured 0.022 vs 0.041 at ic_modes=5)"*

Those are **block-average** numbers — the instrument `PROPOSAL.md` marks *"SUPERSEDED, instrument error"* for carrying a ~0.02–0.05 operator-mismatch floor that reads as a fake gap.
On the canonical measure the same configuration gives ~4e-5.
The default shipping in the package is justified by a number the proposal itself retracts; the real answer is pending `true_gap_sweep`.

### 8.3 The same defect exists in `mf_field_extension_data`

A third, independent code path the fix package does not touch:

```python
# solvers.py:169  and  generate_datasets.py:277 — Cahn-Hilliard
def ch_ic(n, sd, mean):
    r = np.random.default_rng(5000 + sd)              # sd = sample index
    for _ in range(12):
        kx, ky = r.integers(1, 5), r.integers(1, 5); ph = r.uniform(0, 2*np.pi)
        c += r.uniform(-1, 1) * np.cos(kx*Xg + ky*Yg + ph)
...
c = ch_ic(n, s, mean)                                  # s = sample index
P = np.column_stack([log10 gamma, mean composition])   # 2 params exported
```

Per-sample random IC — 12 modes with random wavenumbers, phases and amplitudes, ~48 hidden dof — against a 2-number condition vector.

One thing in our favour: that IC is **already band-limited** by construction (modes 1–4), which is why the code calls it resolution-independent.
Unlike pfc / fk / ac it is retrofittable — the drawn values could simply be exported without changing the IC family or the physics.
Much cheaper than regeneration.

**Scope caveat.**
`mffp_sharp` has been swept exhaustively (16 modules classified above).
`mf_field_extension_data` has **not** — this instance was found incidentally.
Neither have the `mf_field/` local dataset generators.
Given three independent occurrences, a mechanical repo-wide sweep (`default_rng` reached from a per-sample IC builder) looks warranted.

---

## 9. Conceptual grounding (for reuse in write-ups)

**A PDE is a rule, not a picture.**
Fisher-KPP is $\partial_t u = D\nabla^2 u + r\,u(1-u)$ — genuinely two coefficients.
But that equation has infinitely many solutions.
Pinning one down needs the rule, the coefficients, the domain and boundary conditions, the **initial condition**, and the snapshot time.
The rules of chess fit on a card and do not tell you what the board looks like at move 40; you also need the opening position.

**PDEs differ in whether they forget or amplify the start.**

| family | behaviour | consequence |
|---|---|---|
| heat / diffusion | forgets — every IC converges toward the same flat state | omitting the IC costs almost nothing |
| Poisson (elliptic) | no initial condition at all; the source determines the answer | nothing to omit |
| pattern formers (CH, AC, PFC, Fisher-KPP) | **amplifies** — small differences grow exponentially, then lock in | the IC is the dominant input |

The coefficients set the *style* (interface thickness, front speed).
The IC picks *which pattern you actually get*.

**Why a random start is required, not chosen.**
These equations describe an instability: a uniform state that is unstable and wants to break up.
Perfectly uniform is an exact equilibrium — it sits there forever.
A pencil balanced perfectly on its tip never falls, and which way it falls is decided entirely by the nudge.
The nudge is not noise on top of the answer; the nudge **is** the answer.
Broad-spectrum noise is used so the physics, not the generator, picks the winning pattern — which is why band-limiting has a cost.
A second reason: 500 samples with a fixed IC and only $D, r$ varying would be 500 versions of one pattern at different length scales.

**Sharpness is the wrong axis.**
Inside the sharp portfolio, sharpness and affectedness point opposite ways:

| module | role | affected? | why |
|---|---|---|---|
| `sod.py` | the **shock** — sharpest in the suite | **No** | Riemann step: `cond = [rho_l, p_l, gamma]` |
| `kuramoto_sivashinsky.py` | the **smooth control** | **Yes** | needs a broad-spectrum seed; now IC-encoded |

---

## 10. Status

Implemented and verified locally on branch `mffp-trunk-eloise`; **nothing regenerated at production scale**, awaiting mentor sign-off (`condition_completeness_proposal/SIGNOFF.md`).

1. IC encoding lives in the package — `common/ic_encoding.py` + 10 modules; per-module tests assert field = f(exported cond).
2. The certificate is a generation gate — `common/completeness.py`, wired into `generate.py` and `generate_standardized.py`, written into `meta.json`, hard-fails INCOMPLETE unless `stochastic_map` is declared. **Subject to §8.1.**
3. Sample round generated and certified — `condition_completeness_proposal/sample_round/`, all COMPLETE at reconstruction rel-L2 = 0.0, figures in `sample_round/figures/`.

Round-2 numbers stand as measurements of the panel as it exists.
The correction is to their *interpretation* on cahn_hilliard, and no round-2 model needs re-running.

Open: the fidelity-gap recipe (`true_gap_sweep`), §8.1, §8.2, §8.3, and the §11 IC-field-input option (2026-08-04 addendum).

---

## 11. Addendum (2026-08-04) — the IC field as an input: a way out of the trilemma

*Added after the 2026-08-03 sign-off package was assembled; not yet in `condition_completeness_proposal/`.
Candidate part 4 of the proposal, to be put to the mentor alongside parts 1–3, not landed unilaterally.*

**The trilemma in §7 has a hidden assumption: the condition must be a vector.**
Relax that, and a third repair exists for field-IC PDEs — ship the realised IC *field* as a model input, alongside the small physical-parameter vector.

**This is not the round-1 leak.**
The LF field is a cheap solve *of the answer*; handing it over at test time hides whether the model learned anything (§4).
The IC is part of the *question* — in any real use of a surrogate the starting state is known, because the user supplied it.
Conditioning on the IC field is the standard operator-learning convention: FNO, DeepONet, and PDEBench all pose exactly this task (IC field → solution at time $T$).
It is also the legitimate version of the seed-export shortcut §8.1 rejects: the seed is a discontinuous hash *label* for the IC, while the field **is** the IC — the model receives the actual continuous input instead of a name for it.

**What it buys.**
The map becomes deterministic and complete while the IC stays broad-spectrum, so the LF–HF gap survives untouched.
All three corners of §7 hold at once because the "small" constraint is removed rather than fought: complete (the IC is given), rich dynamics (white noise retained), and the condition *vector* stays at 2–3 physical scalars — the IC's dimensionality moves into an input channel where field-to-field architectures handle it natively.

**What it costs.**
It changes the benchmark question for those datasets: round-2's "predict from the condition vector alone" ceases to exist for them, and the task becomes multi-fidelity *operator learning* — a standard, well-populated regime, but a different one.
Model families need a field-input channel at test time; the round-1 contract already flows the LF field through such a channel, so for most architectures what changes is what flows through it, not the plumbing — but it is a contract change and must be versioned as one.

**Repair cost is low — likely no re-solve.**
§8.1 establishes that the shipped IC is a deterministic function of `spec["seed"]` (rebuild-and-re-solve certifies at machine precision).
So for pfc / fisher_kpp / allen_cahn *as shipped*, the IC input arrays can be reconstructed from the stored seeds and exported without regenerating any solution — unlike the band-limited repair, which must re-solve all 500 samples × 3 rungs.
Before trusting this per dataset, run the existing reconstruction certificate against the rebuilt ICs.

**Which PDEs qualify — the test is two-part.**
(a) The solution depends on a field-valued input with no natural few-number description, and (b) the snapshot time lies inside the predictability horizon, so IC → $u(T)$ is a *learnable* deterministic map.

| group | modules | verdict |
|---|---|---|
| pattern formers | cahn_hilliard, allen_cahn, phase_field_crystal, swift_hohenberg, gray_scott, fisher_kpp | yes — these gain the most; §7's trilemma bites hardest here |
| dispersive / wave | kdv, nls, sine_gordon | yes — information-preserving dynamics; textbook operator-learning targets |
| chaotic | kuramoto_sivashinsky; pattern formers far past the transient | only inside the predictability horizon — see below |
| parametric IC | burgers, porous_medium, shallow_water, sod, euler | no — the field would restate 2–7 scalars at 64² cost |
| elliptic / steady | helmholtz, poisson, eikonal | no IC exists; the analogue is a random coefficient/source *field* (Darcy-style), which is a redesign, not a repair |

**The predictability-horizon caveat.**
For chaotic dynamics the map IC → $u(T)$ is deterministic but its sensitivity to the IC grows exponentially in $T$.
Past the Lyapunov horizon, pointwise prediction is unlearnable *even with the IC in hand* — the field input relabels "unknown randomness" as "known but unusable initial data" without removing it.
There, `stochastic_map` plus distributional scoring remains the honest regime regardless of inputs.
This couples to the open `true_gap_sweep`: the usable snapshot window is long enough for nonlinear structure to build (§7's solve-time lever) yet short enough to stay predictable, and it should be found per-PDE, not assumed.

**Portfolio consequence.**
Adopting this per-dataset splits the panel into a parametric-surrogate group (sod, burgers, shallow_water, …), an operator-learning group (the field-IC PDEs inside their horizons), and a `stochastic_map` group (snapshots past the horizon).
That mirrors how the literature splits, and every cell stays honest under its own scoring rule — but it is a benchmark-identity decision, which is exactly why it belongs in the sign-off package rather than in a generator patch.
`mf_field_extension_data`'s cahn_hilliard (§8.3) falls in the yes group by the same test; any decision here should cover both trees at once.
