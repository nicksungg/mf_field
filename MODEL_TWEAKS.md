# Cross-Family Fixes: Structural Constraints, Objective Alignment, and Scoring Validity

**Status:** findings memo, nothing implemented.
**Date:** 2026-07-19.
**Scope of evidence:** static audit of the 21 model directories present in this checkout, plus `eval/`, `bench/`, and `references/v9_baseline/`.
No code was run and no dataset was read — see §10 for exactly what that leaves unverified.

---

## 1. Bottom line

This memo started as a narrow question: should MFFP models embed PDE physics, and if not, what PDE-agnostic structure could replace it?

The answer to the narrow question is in §2, and it is: **structural constraints, not equation residuals** — with one honest complication that needs a cheap experiment to resolve.

But auditing for that answer turned up something more consequential.
**Several leaderboard comparisons are not currently measuring the same quantity.**
Three mutually incompatible definitions of nRMSE coexist across families; 15 of 21 families are scored on an easier split set than the other 6; and `vs_paper` compares our arithmetic mean against the papers' geometric mean.
Those findings are in §3, and they gate everything else: until they are resolved, a tweak that "improves" a family's number cannot be distinguished from a tweak that changed which quantity is being reported.

The work therefore sorts into four tiers:

| Tier | What | Surface | Acting on it |
|---|---|---|---|
| **0** | Scoring validity (§3) | `eval/`, `data_adapters/` — **FIXED** | Needs your override or escalation to the factory CEO |
| **1** | Correctness bugs (§4) | `models/**` — mutable | Actionable now |
| **2** | Objective, constraints, bandwidth, regularization (§5–§8) | `models/**` — mutable | Actionable now |
| **3** | The physics question (§2) | — | One experiment, then a decision |

§9 ranks every item by expected gain × breadth ÷ effort.

The single highest-leverage edit in the mutable surface is **C1**: `models/_common/fire_core.py` never reads or writes `ckpt_dir`, so 9 families discard their entire run on every SLURM preemption.
The single highest-value unrun *experiment* is **B1**: a `modes_cap` sweep, currently pinned at 12 regardless of grid size, retaining 0.87% of the spectrum on a 256×256 work grid.

---

## 2. The physics question, resolved

### 2.1 The apparent paradox

The objection to embedding physics is that we often do not know the PDE.
The natural counter is that we must know the PDE, because we used it to generate the LF and HF data.

Both are right, about different moments.
Knowing the equation at *data-generation* time is the generator's knowledge.
Embedding it in the model asserts something stronger: that at *deployment* time someone can hand the model the governing equation, its coefficients, its boundary conditions, and its source term, per sample.
That is a much narrower claim, and it fails on most of this benchmark.

### 2.2 The 17 datasets split four ways

**Residual demonstrably writable (2).**
`poisson_generated`, `poisson_local` — these are exactly the two where `mf_fno_pinn_transfer` activates its PDE term (`smoke_eval.py:8-12`).

**Writable in principle (10).**
`heat_generated`, `heat_local`, `ifc_heat`, `ifc_poisson`, `darcy_generated`, `advection_diffusion_generated`, `allen_cahn_generated`, `burgers_generated`, `burgers_param_generated`, `lid_driven_cavity_generated`.
Here LF versus HF is a pure *discretization* gap — the same equation on a coarser mesh — so a residual loss is legitimate, though nobody has implemented one.

**Not writable — LF and HF satisfy different equations (3).**
`fluid`, `chin_chun_isothermal`, `chin_chun_potential`.

`chin_chun_potential` is the cleanest counterexample in the repo.
LF is potential flow (Laplace); HF is full CFD building flow.
Those are two *different* equations.
The LF field is not an approximate solution of the HF equation — it is an exact solution of a different one.
There is no single PDE whose residual you can minimize, because the thing being learned is the discrepancy between a wrong model and a right one.
The same holds for any RANS→LES or simplified-physics→resolved-physics pair.

**No usable PDE (2).**
`era5`, `pm_test`.

So a PDE residual is available on 12 of 17 datasets at absolute best, and is currently exercised on 2.

### 2.3 On weather specifically

The atmosphere does obey PDEs — the primitive equations, essentially rotating Navier–Stokes plus thermodynamics plus moisture.
The precise statement is not "weather isn't a PDE."
It is **"weather is a PDE whose residual cannot be evaluated on this data,"** for three independent reasons:

1. **The equations are not closed at any resolution you have.**
   Convection, cloud microphysics, radiation, and boundary-layer turbulence are all parameterized.
   Those parameterizations are empirical and model-specific, not differentiable equations.
   The part that dominates the LF→HF gap is precisely the part that is not written down.
2. **ERA5 is not a solution field.**
   It is a reanalysis — an assimilation of observations into a model — so it satisfies no PDE exactly, by construction.
3. **You do not have the full state.**
   A residual needs all prognostic variables at all levels; the npz gives a few channels.

### 2.4 The distinction that actually matters: kinematic vs dynamic

The useful line is not "physics vs no physics."
It is:

> **Constraints on the function space are portable. Constraints on the dynamics are not.**

A *dynamic* constraint — a PDE residual — needs the equation, its coefficients, its source term, and its boundary data.
A *kinematic* constraint — positivity, a conserved integral, divergence-freeness, a boundary value — needs only a property of the field, discoverable from the data itself.

Incompressibility is the sharpest illustration.
Enforcing `∇·u = 0` says nothing about the momentum equation, the Reynolds number, the viscosity, the forcing, or the boundary conditions.
It constrains *which functions are representable*, not *how they evolve*.
That is why it transfers to `fluid`, `lid_driven_cavity_generated`, and the `chin_chun` pair alike, while a Navier–Stokes residual does not.

§5 is the catalogue of kinematic constraints.
None of them are implemented anywhere in the repo.

### 2.5 The complication, stated honestly

`mf_fno_pinn_transfer` — the one family that embeds an equation — is **#2 by Elo (1799) and the best in the entire zoo by median relative-L2 (0.0122, versus 0.0154 for the #1 family)**.
`model/README.md` headline takeaway #2 credits the physics term directly.

That is real evidence against the position in §2.1–§2.4, and this memo does not explain it away.

But the attribution is untested.
The PDE and Dirichlet terms are soft penalties with `lam_pde = lam_bc = 1e-3` (`models/mf_fno_pinn_transfer/smoke_eval.py:41`), and per its own docstring (`smoke_eval.py:8-12`) they are active **only on the Poisson datasets**; every other dataset falls back to plain FiLM transfer.
So there are two competing explanations for the rank, and they make different predictions.

### 2.6 The decisive experiment (cheap, run this first)

**Compare `mf_fno_pinn_transfer` against `mf_fno_transfer_film` on the non-Poisson datasets only.**

Those two families share a backbone and a schedule; the PDE term is the only mechanism that differs, and it is inert outside Poisson.

- **If the two are statistically indistinguishable off-Poisson:** the physics contributes on 2 of 15 datasets, the rest of the rank comes from FiLM transfer, and a mechanism that fires on 13% of the benchmark is a special case rather than a family.
  The §2.4 position holds on the evidence, not just on principle.
- **If `pinn_transfer` also wins off-Poisson:** something other than the PDE residual is responsible — a schedule difference, an initialization difference, a normalization difference — and that something should be found and given to every family.
  Either way the result is actionable.

**This experiment is currently not interpretable**, because `mf_fno_transfer_film` is not in this checkout and because of §3.5 (single seed, no variance estimate).
Resolve §3.5 first, or run ≥3 seeds for just these two families.

### 2.7 Prior art check: multiplicative residuals are partly tried

Before proposing a positivity-preserving multiplicative head (§5.1), the record should be straight.

`fno_autoregressive` already implements `HF = ρ·LF_pred + δ` with a **learned scalar** ρ (Kennedy & O'Hagan 2000), and it ranks **#22 of 30** (`model/README.md:106-107`).
So a multiplicative correction is not untried, and the tried version lost.

The proposal in §5.1 is a different object — a **per-pixel, log-space** correction, which is a spatially-varying function rather than one scalar gain — but the honest prior is that the scalar version of this idea already failed on this benchmark.
Treat §5.1 as speculative, and rank it below §6 accordingly.

---

## 3. Tier 0 — scoring validity

> ⚠️ **ESCALATION REQUIRED — DO NOT EDIT.**
> Every fix in this section touches `eval/` or `data_adapters/`, which `factory.md` declares fixed surfaces.
> These are written as findings for your decision, not as work to do.
> They are listed first because they determine what every number in §5–§8 would mean.

### S1 — Three incompatible definitions of nRMSE coexist

The contract metric is per-sample relative-L2, each sample weighted equally:
`rel_l2 = mean_over_samples( sqrt(Σ diff²) / sqrt(Σ true²) )`
(corroborated at `references/v9_baseline/eval_mfrnp_v9.py:85`, and by the keys `bench/summary_report.py:18` and `bench/plot_extra.py:40-41` read).

Three different quantities are actually reported under that name:

| Definition | Families | Where |
|---|---|---|
| Per-sample relative-L2 via `finalize_and_write` | 9 FIRE families + others | `models/_common/fire_core.py:312` |
| **Dataset-aggregate** `sqrt(Σ‖err‖² / Σ‖target‖²)` | `transolver_residual`, `transolver_attention_fusion`, `fno_mf_stack`, `fno_coreg_residual` | `transolver_residual/smoke_eval.py:49-62`, `fno_mf_stack/smoke_eval.py:110-115`, `fno_coreg_residual/smoke_eval.py:106-113` |
| Relative-L2 over a **2048-point subsample**, not the full field | `transolver_residual`, `transolver_attention_fusion` | `transolver_residual/smoke_eval.py:167` with `n_hf=2048` at `:36` |

The aggregate form is dominated by large-magnitude samples and is systematically *lower* than the per-sample form whenever per-sample magnitude varies.
Because `composite_nRMSE` takes the minimum over families per dataset (`eval/score.py:169-170`), **a family can win a dataset on metric definition alone.**

### S2 — Split asymmetry rewards not reporting OOD

`per_dataset_nrmse` is the unweighted arithmetic mean over whatever split keys a family chose to emit (`eval/score.py:116-120`).

- Families emitting `{test, ood}` (6): `fno_coreg_conditioned`, `fno_coreg_residual`, `fno_coregionalization`, `transolver_residual`, `transolver_attention_fusion`, `v9_baseline`.
- Families emitting `{test}` only (15): all 12 FIRE families, both DINO families, `fno_mf_stack` (`smoke_eval.py:296-298`), `mf_fno_transfer_bar`, `mf_fno_pinn_transfer`.

OOD nRMSE is typically several times test nRMSE.
Averaging it in therefore *penalizes* the 6 families that report it, independent of model quality — and the best-per-dataset composite hands the win to the test-only families.

The FIRE path never loads the OOD split at all: `fire_core.py:237` reads only `"train"` and `"test"`.

### S3 — `vs_paper` mixes aggregation rules

Ours is the arithmetic mean over splits (`eval/score.py:116-120`); the paper number is the **geomean** over splits (`:140-141`).
Arithmetic mean ≥ geometric mean, so `ratio_ours_over_paper` (`:184`) is biased against us and `beats_paper` (`:185`) is decided on non-comparable quantities.

Also: the module docstring at `eval/score.py:9-10` says "mean over datasets" while the code computes a geomean (`:188-190`).
Stale, and misleading to anyone reading for the definition.

### S4 — era5 and pm_test are scored against a downsampled target

`fire_core.py:243` sets `grid = cap_grid(hf_native)` with `WORK_CAP = 256` (`:135`), and `:247` bilinearly resamples the HF **test target** onto that grid via `to_grid` (`:152-157`), with `antialias` left at its default `False`.

For era5 the native HF grid is 721×1440 (`fno_coregionalization/smoke_eval.py:15`), so the target becomes 128×256 — a **5.6× decimation with no prefilter**, folding everything above the new Nyquist back as aliasing.

A smoothed target is a strictly easier problem, and `eval/score.py` does not check `work_grid` before declaring `beats_paper`.
`work_grid` *is* recorded in the output JSON (`fire_core.py:301, :314`), so the gate is one comparison away.
Per `fno_coregionalization/smoke_eval.py:64`, only era5 and pm_test exceed the cap; the other 15 datasets are unaffected.

### S5 — No variance estimate anywhere, plus a winner's curse

`eval/smoke_config.json` and `eval/full_config.json` both fix `"seed": 42`, passed through unchanged (`eval/score.py:234`, `:61`, `:90`).
Every reported number is a **single run**.

Determinism is also incomplete — repo-wide, zero hits for `torch.cuda.manual_seed*`, `cudnn.deterministic`, `use_deterministic_algorithms`, `CUBLAS_WORKSPACE_CONFIG`, or any TF32 control.
`SpectralConv2d` is cuFFT plus `einsum` (`fire_core.py:44-52`), and conv/GroupNorm backward on CUDA use atomics, so the same command twice on the same GPU does not give bit-identical results.
TF32 is on by default on H100 — a silent ~1e-3 relative perturbation, unpinned.
`transolver_*` and `v9_baseline` train under AMP fp16 (`transolver_residual/smoke_eval.py:52,79,132`) while every FNO family runs fp32 — different numerical noise floors across families being ranked against each other.
`mit_preemptable` has heterogeneous GPU types (`eval/run_smoke.sbatch:9`), so a requeue can change hardware mid-benchmark.

Compounding this, `min` over ~22 families with one seed each (`eval/score.py:169-170`) selects the luckiest noise draw.
Adding a family can only lower the composite, so it drifts downward as the zoo grows and is not a measure of any single model.

**Consequence: any leaderboard delta below roughly 1e-2 relative is indistinguishable from run noise, and nothing in the harness measures that noise.**
This directly affects the §2.6 experiment (a 0.0122 vs 0.0154 median gap) and every keep/revert decision made to date.

### S6 — `code_hash` does not cover shared code

`eval/score.py:53-58` computes `code_hash` as a sha256 over `sorted(family_dir.rglob("*.py"))`.

`models/_common/{fire_core,fire_methods,recipe_hash}.py` sit **outside** every family directory, yet 12 families' entire training and evaluation logic lives there.
Editing `fire_core.py` — the optimizer, the schedule, the residual runner, all of `fire_run` — invalidates **zero** cached results.
The same hole applies to `data_adapters/*` (all families) and to `references/v9_baseline/{train_v9,eval_v9}.py`, which `transolver_residual/smoke_eval.py:31-32` imports its dataset and collate function from.

Non-`.py` inputs are also unhashed: `manifest.json`, per-family `full_config.json`, and the dataset contents.

This interacts with C3 below to produce silent wrong results.

**Suggested fix if the surface is opened:** hash `models/_common/**`, `data_adapters/**`, and the family's non-`.py` configs alongside the family directory. One function.

---

## 4. Tier 1 — correctness bugs in `models/**`

These are inside the mutable surface and actionable now.

### C1 — `fire_run` has no checkpoint resume: 9 families lose every preempted run

`eval/MODEL_CONTRACT.md` makes resume mandatory because `mit_preemptable` jobs are preempted and requeued.
`models/_common/fire_core.py:226-316` contains **zero** `torch.save` or `torch.load` calls, and never reads `args.ckpt_dir`.

Affected, all of them 33-line wrappers delegating to `fire_run`:
`fno_fire_batchens`, `fno_fire_cqr`, `fno_fire_dkl`, `fno_fire_iqn`, `fno_fire_laplace`, `fno_fire_mdn`, `fno_fire_quantile`, `fno_fire_snapshot`, `fno_fire_swag`.

The regression came from the refactor into `_common` — the copied-out variants that predate it do implement resume (`fno_fire_distcond/smoke_eval.py:193-206, 225-227`).

**Fix:** one save/load of `{lf_state, fno_d_state, opt, sched, epoch, res_scaler, code_hash}` in `fire_core.py`.
**This is the highest-leverage single edit in the repo** — one function, nine families, and it is inside the mutable surface.

Related: `eval/run_smoke.sbatch:44-50` traps `USR1` and comments "letting current iteration save its checkpoint," but **no Python file installs a SIGUSR1 handler** (zero hits for `signal.signal` / `SIGUSR1`).
Python's default action for SIGUSR1 is to terminate, so the graceful-save path does not exist.

### C2 — Two families refuse to load their own mid-training checkpoints

`fno_coreg_conditioned` and `fno_coregionalization` write `last.pt` every `ckpt_every=10` epochs, but the resume guard accepts **only a completed run** (`stage == 2 and epoch == args.epochs`):
`fno_coreg_conditioned/smoke_eval.py:306-321` (guard), `:325-331` (save); `fno_coregionalization/smoke_eval.py:314-330`, `:336-343`.

So a mid-training checkpoint is always discarded and training restarts from epoch 1 — the checkpoint I/O cost is paid and none of the benefit received.
Neither saves optimizer or scheduler state.

Six more families save exactly once, after all training completes (`fno_dino_cond:221-223`, `fno_dino_residual:231-233`, `fno_fire_distcond:222-224`, `fno_fire_mcdropout:198-200`, `mf_fno_pinn_transfer:204`, `mf_fno_transfer_bar:166-167`) — preemption at 99% of training loses 100% of it.

Only 4 of 21 are correct: `fno_coreg_residual`, `fno_mf_stack`, `transolver_residual`, `transolver_attention_fusion`.
Even those never save RNG state, so a preempted run's data ordering diverges from an uninterrupted one — the same config yields two different numbers depending on whether SLURM preempted it.

### C3 — Stale checkpoints can silently skip training entirely

`ckpt_dir = ckpt_root / fam_name / ds_name` (`eval/score.py:72`) — keyed by neither `epochs`, `seed`, nor `code_hash`.
Meanwhile family resume guards check `epochs_target` and `grid`, plus optionally `recipe_hash`, which `models/_common/recipe_hash.py:10-12` computes over **`SMOKE_DEFAULTS` only**, not over any code.

The failure mode: edit `model.py` or a training loop without touching `SMOKE_DEFAULTS` → `code_hash` changes → the results cache misses → the family reruns → it loads the **old** `last.pt`, sets `trained = True`, skips training, and writes a fresh result JSON reflecting the *previous* code.
It looks exactly like a legitimate cache miss.

A shape-changing edit raises inside `load_state_dict` and is caught into a fresh start; a shape-preserving edit — learning rate, loss weights, normalization, schedule — resumes cleanly and does nothing.
Most exposed (no `recipe_hash` guard at all): `fno_coreg_conditioned`, `fno_dino_cond`, `fno_dino_residual`, `fno_fire_distcond`, `fno_fire_mcdropout`, `mf_fno_pinn_transfer`, `mf_fno_transfer_bar`.

Also: `fno_coreg_conditioned/smoke_eval.py:413-414` and `fno_coregionalization/smoke_eval.py:428` load `best.pt` **unguarded** — no `epochs_target`, `grid`, or `recipe_hash` check — so a stale `best.pt` from a prior configuration in the same `ckpt_dir` can be loaded for evaluation if the current run never beats it.

**Fix inside the mutable surface:** have each family's guard store and compare a hash of its own source plus `models/_common/`.
The cleaner fix (keying `ckpt_dir` by `code_hash`) is in `eval/` — see S6.

### C4 — The residual net trains on in-sample LF predictions

`fire_core.py:259` fits the LF model on `X_lf`.
`fire_core.py:260` then computes `mu_hf, aug_hf = lfm.summaries(X_hf, s_lf)` from that same just-fitted model.

In these MF datasets the HF conditions are typically a subset of the LF conditions, so at training time the residual net sees an **optimistically good `mu` and an optimistically small `sigma`**; at test time (`:286`) it sees genuinely out-of-sample LF summaries.
The conditioning distribution shifts between fit and inference.

This is the classic residual-stacking flaw, and it degrades **precisely the uncertainty channels that the entire nine-way FIRE ablation exists to measure**.
The comparison "which uncertainty source helps most" is being run on uncertainty estimates that are systematically too confident at training time.

**Fix:** cross-fit — compute `summaries` on `X_hf` out-of-fold (K-fold over the LF fit), so the residual net trains on the same kind of LF summary it will meet at test.

This is the most scientifically consequential bug in the memo, because it does not just add error — it biases an ablation toward a particular conclusion.

### C5 — `fno_mf_stack` has three independent defects

- **No normalization layer.** `fno_mf_stack/model.py:81-89` is the only FNOBlock in the repo without `nn.GroupNorm(min(8,ch), ch)`; every peer has it (`fire_core.py:60`, `mf_fno_transfer_bar/model.py:56`, `fno_coregionalization/model.py:76`, `fno_coreg_residual/model.py:88`).
  This looks like an omission, and it would depress the family's numbers for a reason unrelated to its MF mechanism.
- **No gradient clipping.** The only family without a `grad_clip` key (`smoke_eval.py:39-55`).
- **Builds a validation split and discards it.** `val_loaders` are constructed at `smoke_eval.py:166` but never evaluated; `best_val` stays `inf` (`:203`) and no `best.pt` is written.
  Likely an unfinished edit.

(It also uses default FFT normalization rather than `norm="ortho"` at `model.py:61,78` — benign, since the transform pair is self-inverse either way.)

### C6 — `randperm` inside the batch loop is not epoch semantics

```python
for _ in range(epochs):
    for i in range(0, n, bs):
        idx = torch.randperm(n, generator=g)[i:i + bs]   # fresh permutation EVERY step
```

A fresh permutation is drawn per step, so an "epoch" is a with-replacement sample across batches — roughly 1/e of the dataset is unseen in any given epoch and others are seen twice.
Still unbiased SGD, but not epoch semantics, and it costs an O(n) permutation per optimizer step.

Sites: `fire_core.py:192, 208`; `fire_methods.py:52, 110, 166, 211, 262, 312`; `fno_dino_cond:82,101`; `fno_dino_residual:84,107`; `fno_fire_distcond:82,107`; `fno_fire_mcdropout:73,96`.

**Fix:** hoist `perm = torch.randperm(n, generator=g)` one loop level up. One line per site.

### C7 — Seeding is incomplete

Every entry point does only `torch.manual_seed(seed)` and `np.random.seed(seed)` (`fire_core.py:234`, `fno_coreg_conditioned:241-242`, `transolver_residual:73`).
Missing: `torch.cuda.manual_seed_all`, stdlib `random.seed`, cuDNN determinism flags, and an explicit TF32 decision.
See S5 for why this matters at the resolution the leaderboard is read at.

---

## 5. Tier 2a — structural constraints

**Confirmed exhaustively: no output constraint of any kind exists in any of the 21 families.**

Every terminal operation is a bare `nn.Conv2d(·, out_ch, 1)` or `nn.Linear(·, 1)` with **no trailing activation** — in every `nn.Sequential` head the pattern is `Conv2d → GELU → Conv2d`, with the GELU between the two 1×1s and never after the last (`fire_core.py:102`, `fire_core.py:123`, `fno_coreg_residual/model.py:124-130`, `fno_mf_stack/model.py:100-102`, `transolver_*/model.py:40-45`).

A repo-wide grep for `Sigmoid|Softplus|Tanh|ReLU|softplus|exp|clamp|abs|mask|positive` returns **zero hits on any output path**.
Every hit is one of: internal attention softmax; a *distribution-parameter* guard rather than a field guard (`fire_methods.py:299-300` clamps MDN `logσ`, `:121` clamps SWAG variance, `:401`/`:415` clamp noise variance); or a metric denominator guard.

`mf_fno_pinn_transfer` is the closest thing to physics-aware and is still a pure soft penalty (`smoke_eval.py:41`), never a projection.
The only structural output *transform* anywhere is a constant per-fidelity de-normalization scalar (`fno_coregionalization/model.py:162-163`) — a rescale, not a constraint.

The three residual families anchor their output to the LF field (`fire_core.py:288`, `transolver_residual/model.py:178`), but that is a prior, not a constraint — nothing prevents the sum from leaving the physical range.

### 5.1 Positivity — multiplicative / log-space head

Applies where the field is nonnegative by nature: absolute temperature, concentration, density, permeability (`darcy_generated`), specific humidity (`era5`).

The naive `HF = mu_LF + softplus(delta)` is wrong — it forces the correction to be one-signed, so the model can only ever increase the LF prediction.
The correct form makes the correction multiplicative:

```
HF = mu_LF * softplus(delta)     # equivalently: log HF = log mu_LF + delta
```

Positivity is automatic whenever `mu_LF > 0`.
The secondary benefit is that MF discrepancies are often *relative* rather than absolute — a coarse solver that is 5% low everywhere is a constant in log space and a spatially varying function in linear space.

**Interaction with the global max-abs scalers (§6.2):** this would also equalize loss weight across the interior and thin boundary layers, which is the specific failure mode expected on `lid_driven_cavity_generated` and `fluid`.

**Traps.**
Positivity in physical units is not positivity in scaled units — the constraint must be applied before normalization, or the shift carried explicitly.
And if the field genuinely reaches zero, `softplus` never gets there and gradients vanish near the floor; only impose this where the data minimum is comfortably above zero.

**Confidence: low-to-moderate.**
See §2.7 — the scalar-ρ version of this idea is already implemented as `fno_autoregressive` and ranks #22 of 30.
The per-pixel log-space version is a materially different function class, but the prior is not encouraging.

### 5.2 Global integral conservation

Assert that a scalar total is preserved, and enforce by projection after the network:

```python
raw = mu_LF + delta
u   = raw + (C - raw.sum()) / N          # additive: preserves fluctuation shape
u   = raw * (C / raw.sum())              # multiplicative: also preserves positivity
```

A rank-1 projection — differentiable, free, exact.

**Where `C` comes from without knowing the PDE:** from the LF field, `C = mu_LF.sum()`.
This is not asserting a conservation law; it asserts *"whatever the LF solver conserves, the HF field conserves too."*
Finite-volume LF solvers are conservative by construction, so this usually holds — and it is empirically checkable (§5.5).

**Why it should help the metric directly:** squared error decomposes into a mean-offset term and a fluctuation term, and this annihilates the mean-offset term exactly.

**Why it should help more than that here:** `model/README.md:18-19` reports that for the FIRE families "the *mean* relL2 is wrecked by a few blow-up datasets."
On a geomean composite a single blow-up dataset is devastating.
A projection is a hard bound on that failure mode — the prediction cannot drift arbitrarily far in the mean, no matter what the residual net does.
This is the strongest argument in the memo for constraints, and it is an argument about *robustness*, not average accuracy.

**Confidence: moderate**, conditional on the §5.5 probe showing a tight LF/HF total ratio.

### 5.3 Divergence-free velocity via a stream function

For incompressible velocity fields — `fluid`, `lid_driven_cavity_generated`, and plausibly the `chin_chun` pair.

Do not predict `(u, v)` and penalize `∇·u`.
Predict a stream function ψ and take `u = ∂ψ/∂y`, `v = -∂ψ/∂x`; then `∇·u = 0` identically, to machine precision.

In an FNO this is unusually clean: the derivative is multiplication by `ik` in Fourier space — exact on periodic domains, no finite-difference truncation error, and the model is already in that basis.
Equivalent alternative if the velocity head must be kept: Helmholtz projection, `û ← û − k(k·û)/|k|²`, one spectral layer.

Per §2.4 this is a kinematic constraint, so it does not import any dynamic assumption.

**Confidence: moderate**, but gated on whether these datasets actually expose multi-channel velocity — unverified, see §10.

### 5.4 Hard boundary conditions

Replace the soft Dirichlet penalty (`mf_fno_pinn_transfer/smoke_eval.py:136`, `lam_bc=1e-3`) with a mask:

```
u = g + φ · NN(x)
```

where φ vanishes on ∂Ω.
The BC then holds exactly regardless of what the network does, with no hyperparameter.
And `g` need not be known analytically — take it from the LF field's boundary values, which makes this PDE-agnostic in exactly the §2.4 sense.

### 5.5 The detection probe — what makes this a family rather than a hack

This is the part that separates the proposal from `mf_fno_pinn_transfer`.
Each constraint requires knowing only:

1. which channels are nonnegative,
2. which channels form a vector field,
3. whether some integral is stable between LF and HF.

All three are **detectable from training data**, so the constraint layer can adapt per dataset instead of being hardcoded to one equation.

**Deliverable: a probe script** that, for each of the 17 datasets, reports:

| Test | Statistic | Enable constraint if |
|---|---|---|
| Positivity | `min(HF_train)`, `min(LF_train)` | both > 0 with margin ≥ 5% of field std |
| Conservation | distribution of `HF.sum() / LF.sum()` per sample | ratio within 1 ± 0.02 for ≥ 95% of samples |
| Vector field | channel count and metadata | ≥ 2 channels identifiable as components |
| Boundary | variance of HF on ∂Ω | near-constant ⇒ Dirichlet-like |

Turn each constraint on **only when its test passes**, log which fired per dataset, and fall back to the unconstrained head otherwise.

The failure mode to guard against: imposing a constraint that is *not* true in the data actively hurts accuracy.
Detection must be empirical and conservative — a false positive here is worse than a missed opportunity.

**This probe cannot be run from this checkout** — all 17 `data/` entries are dangling symlinks to the cluster tree (`scripts/env.sh:13`, `/orcd/data/faez/001/nick/mf_field/factory_mffp`).
The per-dataset applicability table has to be generated there, and is the first concrete task if this direction is pursued.

---

## 6. Tier 2b — objective alignment

### 6.1 The training loss does not match the scored metric

`models/_common/fire_core.py:210`:

```python
loss = F.mse_loss(model(Xt[idx], At[idx]), Yt[idx])
```

with the target built at `fire_core.py:261-262`:

```python
residual   = (Y_hf - mu_hf).astype(np.float32)
res_scaler = max(float(np.abs(residual).max()), 1e-8)
```

`res_scaler` is a **single global scalar** — max-abs over the entire HF training set.
`F.mse_loss` then averages over pixels *and* samples uniformly, so every sample contributes in proportion to its **absolute** squared error in one fixed global unit.

The metric is `mean_i ‖pred_i − true_i‖ / ‖true_i‖`.
A sample whose field energy is 10× below the dataset median contributes about 1/10 of the gradient it deserves, while counting exactly as much at scoring time.

**Breadth:** this one line governs 9 families, and the identical construction is copy-pasted into `fno_fire_distcond/smoke_eval.py:115-116, 216-217` and `fno_fire_mcdropout/smoke_eval.py:104-105, 194-195` — **11 of 21 families** with identical exposure.

**In-repo precedent for the fix.** `transolver_residual/smoke_eval.py:65-69`:

```python
mse = torch.mean(diff ** 2)
rel = torch.sqrt(torch.sum(diff**2, dim=1)) / torch.clamp(torch.sqrt(torch.sum(targets**2, dim=1)), min=1e-4)
return mse + torch.mean(rel), mse
```

The `rel` term is exactly the scored quantity — reduced per-sample, then averaged, so it is scale-invariant and weights every sample equally.
Its provenance is the frozen reference `references/v9_baseline/train_v9.py:157-163`, so this is **already sanctioned repo practice**, not a new idea.

**This is the highest-confidence item in the memo**: a known mismatch, a fix with in-repo precedent, and 11 families of breadth.

### 6.2 The model-selection metric mismatches too

Every family that does validation-based selection selects on a **pooled, energy-weighted** nRMSE, `sqrt(Σ_i Σ_p err² / Σ_i Σ_p true²)`, not the per-sample mean:
`fno_coreg_conditioned/smoke_eval.py:215-220`, `fno_coreg_residual/smoke_eval.py:169-174`, `transolver_residual/smoke_eval.py:57-62`, `transolver_attention_fusion/smoke_eval.py:45-50`.

So low-energy samples are underweighted at selection time as well as at training time.
Cheap fix, and it should be made in the same edit as §6.1.

### 6.3 Two families train in raw physical units

`fno_coregionalization` and `fno_coreg_conditioned` de-normalize inside the model (`model.py:163` / `model.py:213-214`) and take the loss on the de-normalized output (`smoke_eval.py:370` / `:358`).
The effective gradient on each fidelity's head is therefore weighted by that fidelity's scaler — a *per-fidelity* weighting distortion layered on top of the per-sample one in §6.1.

---

## 7. Tier 2c — spectral bandwidth

### B1 — `modes_cap = 12` never scales with resolution

```python
# models/_common/fire_core.py:147-149
def modes(grid, c):
    H, W = grid
    return (min(c, max(H // 2, 1)), min(c, W // 2 + 1))
```

The `min(c, ...)` makes the mode count **constant at 12** for every grid ≥ 24×22.
`SpectralConv2d.forward` (`fire_core.py:47-51`) writes only the `[:mh,:mw]` and `[-mh:,:mw]` corners into a zero-initialized output, so **every unwritten Fourier coefficient is set to exactly zero** — a hard low-pass, not an attenuation.

On a 256×256 work grid the `rfft2` has 256×129 = 33,024 coefficients and 24×12 = 288 survive: **0.87% of the spectrum.**
On 64×64 it is 11%.

`modes_cap=12` is the setting in every FNO-backbone family except `fno_coregionalization`, which raised it to 16 — and did so as part of a coupled width/depth capacity bump, so the effect of the mode count alone was never isolated.
(The two transolver families are attention-based and have no Fourier modes, so they are outside this finding.)

**Why this may explain the leaderboard shape.**
For the non-augmented `FNO2d` families the only spatially varying input is a two-channel linear coordinate ramp (`fire_core.py:67-70`, lifted at `:79,85`) — the conditioning vector is broadcast to a spatial constant (`_broadcast_cond`, `:91-93`).
All HF spatial content must therefore be synthesized from a linear ramp through ≤12 Fourier modes plus GELU harmonics.
Sharp features are structurally unreachable.

The augmented families predict `HF = μ_LF + δ` (`fire_core.py:288`), so the LF field's high frequencies pass through *additively* and the truncation limits only the correction.
**That is a plausible mechanism for why residual/additive families dominate the leaderboard** — they are the only ones not paying the full low-pass penalty.

**Proposed experiment:** a clean `modes_cap` sweep (12 → 24 → 32 → Nyquist) at fixed width and depth.
This is the highest-value single experiment the repo has not run.

Note also that `to_grid` upsamples the LF field to the HF work grid (`fire_core.py:245`), so `mu_LF` is band-limited by construction and cannot contain structure above the LF Nyquist — the residual net must supply *all* fine detail through those 12 modes.

### B2 — The backbone is **not** held constant, contrary to the stated protocol

`model/README.md:10-11` claims the backbone is "held roughly constant so the comparison isolates the MF mechanism."
It is not.

- **Capacity.** `fno_coregionalization/smoke_eval.py:74-78` runs `hidden=128, n_blocks=6, modes_cap=16, K=20, b_hidden=128` against the zoo standard `64 / 4 / 12` — roughly 4× the trunk FLOPs and 33% more Fourier modes.
  The comment at `:70-73` documents this as a deliberate "H1 cycle-008 paper-config capacity bump."
  Its sibling `fno_coreg_conditioned/smoke_eval.py:70-75` explicitly documents *refusing* the same bump.
  So the two coregionalization families — whose entire purpose is an A/B on the fusion mechanism — differ in width, depth, and mode count.
  **That comparison measures capacity, not mechanism.**
- **Mode schedules.** `fno_mf_stack` uses `modes_per_level=(4,8,16,20)`; `fno_coreg_residual` uses `n_blocks=3` with `(4,8,12,12)`.
  Neither uses the shared `modes()` schedule.
- **Optimizer protocol**, splitting cleanly by lineage: `lr=1e-3, bs=16` (all FIRE, DINO, transfer), `lr=3e-4, bs=8` (coreg, mf_stack), `lr=3e-4, bs=4` (transolver).
- **Validation fraction:** 0.1 for the FNO families, 0.2 for transolver and v9 — those groups train on different amounts of data and are ranked against each other.

**Recommendation:** either propagate the capacity bump to all families or revert it.
Leaving it on exactly one family is the worst of the three options.

### B3 — LF-stage ensembling is a capacity confound, not only a UQ ablation

Six families ensemble at the LF stage, and the ensemble mean is the additive base of the final prediction (`fire_core.py:260, 288`): `fno_fire_distcond` (5 full FNOs), `fno_fire_snapshot`/`fno_fire_cqr` (5 snapshots), `fno_fire_swag` (10 samples), `fno_fire_batchens` (5 heads), `fno_fire_mcdropout` (16 passes).

`model/README.md` reports `fno_fire_distcond`/`snapshot`/`cqr` at **28.4M params** versus 9.48M for single-model FIRE variants and 4.77M for the transfer families.
`fno_fire_distcond` ranks #3 partly on 5× the compute.
No family ensembles the HF correction network.

---

## 8. Tier 2d — regularization

The HF stage fits scarce data with essentially no guard against overfitting.

- **Dropout is 0 in every family** except `fno_fire_mcdropout`, and there only on the LF net (`smoke_eval.py:41`).
- **`FNO2dAug` does not expose a dropout argument at all** (`fire_core.py:119-123`) — and that is the residual network *every* FIRE family trains on the scarce HF split.
  The HF-fitting stage is structurally un-regularizable.
- **`weight_decay=1e-5`** (`fire_core.py:179`) is negligible.
- **15 of 21 families have no validation split at all.**
  `fire_run` never builds one, never early-stops, and takes the final-epoch weights unconditionally (`fire_core.py:279`).
  Contrast `references/v9_baseline/smoke_eval.py:138,150`, which tracks `best_val` and reloads the best checkpoint.
- **No LR warmup anywhere.**
  Cosine annealing is present (`fire_core.py:180`, `CosineAnnealingLR(T_max=epochs, eta_min=1e-6)`) and gradient clipping is present everywhere except `fno_mf_stack`, but warmup, EMA, SWA, and early stopping are absent repo-wide (`patience`/`early_stop`: zero hits).

**A fixed epoch budget on a handful of HF samples with no overfitting guard is a plausible mechanism for the "few blow-up datasets" reported at `model/README.md:18-19`** — which in turn is the failure mode §5.2 is designed to bound.
These two items address the same symptom from different directions and should be evaluated together.

### The smoke/full gap interacts badly with the cosine schedule

Smoke is 200 epochs, full is 2500 (`eval/smoke_config.json`, `eval/full_config.json`).
Because `T_max=epochs`, these are **not the same run truncated** — they are two different LR trajectories, each annealed to `eta_min` at its own horizon.
A method that benefits from a long low-LR tail is indistinguishable at 200 epochs from one that does not.

Compounding:
`fno_coreg_*` split epochs by fraction (`pretrain_frac=0.25`), so smoke gives 50 warm-up / 150 fine-tune versus 625 / 1875 — a different recipe, not a shorter one.
`SnapshotLF` uses `epc = epochs // K` with K=5 (`fire_methods.py:41`), so smoke runs 40-epoch snapshot cycles; snapshot diversity is a function of cycle length, so smoke is measuring a different method.
`MDNLF` warms up on MSE for `int(0.4*epochs)` (`fire_methods.py:308`) — 80 versus 1000 epochs before the NLL objective engages.
Capacity-heavy families are the most underfit at 200 epochs, so **smoke systematically favors small models.**

There is no evidence in the harness that smoke ranking transfers to full ranking, and keep/revert decisions are currently made on smoke.

---

## 9. Ranked

Ordered by expected gain × breadth ÷ effort. "Breadth" is families affected of the 21 in this checkout.

| # | Item | § | Breadth | Effort | Confidence | Surface |
|---|---|---|---|---|---|---|
| 1 | Checkpoint resume in `fire_run` | C1 | 9 | 1 function | Certain (contract violation) | `models/**` |
| 2 | Per-sample relative-L2 loss term | 6.1 | 11 | 1 function, precedent exists | High | `models/**` |
| 3 | Unify the nRMSE definition | S1 | 4 deviate, all 21 compared | — | Certain | **eval/ — escalate** |
| 4 | Cross-fit LF summaries | C4 | 11 | moderate | High | `models/**` |
| 5 | `modes_cap` sweep | B1 | 19 (all FNO-backbone) | compute only | High value, unknown sign | `models/**` |
| 6 | Fix split asymmetry (test vs test+ood) | S2 | 21 | — | Certain | **eval/ — escalate** |
| 7 | Multi-seed + determinism | S5, C7 | 21 | 3× compute | Certain | both |
| 8 | Val split + early stopping | §8 | 15 | moderate | Moderate | `models/**` |
| 9 | Conservation projection | 5.2 | probe-dependent | small | Moderate | `models/**` |
| 10 | Guard stale checkpoints | C3 | 7 | small | Certain | `models/**` |
| 11 | `code_hash` over `_common/` | S6 | 12 | 1 function | Certain | **eval/ — escalate** |
| 12 | Resolve backbone inconsistency | B2 | 21 | policy call | Certain | `models/**` |
| 13 | Expose dropout in `FNO2dAug` | §8 | 11 | trivial | Moderate | `models/**` |
| 14 | `fno_mf_stack` GroupNorm + grad_clip + val | C5 | 1 | trivial | High | `models/**` |
| 15 | Hoist `randperm` | C6 | 12 | trivial | Certain (semantics + speed) | `models/**` |
| 16 | Divergence-free head | 5.3 | probe-dependent | moderate | Moderate | `models/**` |
| 17 | Hard BC mask | 5.4 | probe-dependent | small | Moderate | `models/**` |
| 18 | Gate `beats_paper` on `work_grid` | S4 | 2 datasets | 1 comparison | Certain | **eval/ — escalate** |
| 19 | Positivity / log-space head | 5.1 | probe-dependent | small | **Low — see §2.7** | `models/**` |

**Suggested order of work.**
Run the §2.6 attribution experiment and the §5.5 probe first — both are cheap, and both change what the rest of the list is worth.
Then #1, #2, #4 (all mutable-surface, all high confidence).
Escalate #3, #6, #11 in one conversation, since they share a root cause.

---

## 10. What this memo could not verify

Stated explicitly so nothing here is read as stronger than it is.

- **No data was read.**
  All 17 `data/` entries are dangling symlinks into the cluster tree (`scripts/env.sh:13`).
  Every claim about field structure, positivity, conserved integrals, channel layout, or HF/LF sample counts is inference from code and paper provenance, not measurement.
  The §5.5 probe exists precisely to close this gap and must be run before any constraint is implemented.
- **The dataset count is inconsistent in the repo itself.**
  `eval/full_config.json` lists 17 datasets; `model/README.md:3` reports the benchmark as 30 families × **15** datasets (436/450 cells).
  This memo uses 17 when reasoning about the data (§2.2) and 15 when quoting leaderboard coverage (§2.6).
  Which 2 datasets are excluded from the benchmark, and why, was not determined — worth resolving, since §2.6's "2 of 15" ratio depends on whether the Poisson datasets are among them.
- **Only 21 of 30 families are in this checkout.**
  Absent: `mf_fno_transfer_film`, `mf_fno_transfer`, `mf_fno_transfer_2m`, `fno_additive`, `fno_multilevel`, `fno_autoregressive`, `fno_coreg_lf_hf_transfer`, `mfrnp`, `d_mfd`, `mf_deeponet`.
  Notably this includes the #1 family and both families in the §2.6 experiment, so that experiment must be run on the cluster.
- **`data_adapters/` internals are not present** — only `npz_compat.py` is tracked.
  `load_mf_dataset`, `resolve_grid`, and `finalize_and_write` were not read.
  The metric definition in S1 is corroborated from `references/v9_baseline/eval_mfrnp_v9.py:85` and the keys consumed at `bench/summary_report.py:18`, not read from `metrics.py`.
  **If `finalize_and_write` differs from that formula, S1 and §6.1 both need revisiting.**
- **No code was executed**, so every performance claim is a mechanism argument, not a measurement.
  In particular the confidence column in §9 rates *how sure the diagnosis is*, never how much nRMSE the fix will buy.
- **`model/README.md` numbers are taken as given** (30 families × 15 datasets, 436/450 cells, seed 42, 2500 epochs).
  Per S5 they carry no variance estimate, so all rank comparisons quoted in this memo inherit that limitation — including the 0.0122 vs 0.0154 gap that motivates §2.6.
