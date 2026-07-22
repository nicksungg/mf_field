# Cross-Family Fixes: Evidence Register

**Status:** evidence companion for [`MODEL_TWEAKS.md`](MODEL_TWEAKS.md), nothing implemented.
**Date:** 2026-07-19.
**Scope of evidence:** static audit of the 21 model directories present in this checkout, plus `eval/`, `bench/`, and `references/v9_baseline/`.
No code was run and no dataset was read.

---

## 1. Unified finding register

The original memo used S1-S6, C1-C7, B1-B3, and bare decimal sections for one list of findings.
This file uses one scheme: F01-F26 for findings, P01 for the physics argument, and U01-U06 for verification limits.

---

## P01. Physics framing and attribution question

The audit started from the question of whether MFFP models should embed PDE physics, and if not, what PDE-agnostic structure could replace it.
The answer is structural constraints, not equation residuals, with one cheap attribution experiment still needed.

The apparent paradox is that we often do not know the PDE, even though the LF and HF data were generated from equations.
Both statements are right about different moments.
Knowing the equation at data-generation time is the generator's knowledge.
Embedding it in the model asserts that at deployment time someone can hand the model the governing equation, coefficients, boundary conditions, and source term for each sample.
That stronger claim fails on most of this benchmark.

The 17 datasets split four ways.
The residual is demonstrably writable for `poisson_generated` and `poisson_local`.
These are exactly the two where `mf_fno_pinn_transfer` activates its PDE term (`smoke_eval.py:8-12`).

The residual is writable in principle for `heat_generated`, `heat_local`, `ifc_heat`, `ifc_poisson`, `darcy_generated`, `advection_diffusion_generated`, `allen_cahn_generated`, `burgers_generated`, `burgers_param_generated`, and `lid_driven_cavity_generated`.
Here LF versus HF is a pure discretization gap, so a residual loss is legitimate, though nobody has implemented one.

The residual is not writable for `fluid`, `chin_chun_isothermal`, and `chin_chun_potential`.
`chin_chun_potential` is the cleanest counterexample in the repo.
LF is potential flow, which is Laplace, while HF is full CFD building flow.
Those are two different equations.
The LF field is not an approximate solution of the HF equation.
It is an exact solution of a different one.
There is no single PDE whose residual can be minimized, because the thing being learned is the discrepancy between a wrong model and a right one.
The same holds for any RANS-to-LES or simplified-physics-to-resolved-physics pair.

There is no usable PDE for `era5` and `pm_test`.
The atmosphere obeys PDEs, namely the primitive equations, essentially rotating Navier-Stokes plus thermodynamics plus moisture.
The precise statement is not that weather is not a PDE.
The precise statement is that weather is a PDE whose residual cannot be evaluated on this data.
The equations are not closed at any resolution here, because convection, cloud microphysics, radiation, and boundary-layer turbulence are parameterized.
Those parameterizations are empirical and model-specific, not differentiable equations.
The part that dominates the LF-to-HF gap is precisely the part that is not written down.
ERA5 is a reanalysis, an assimilation of observations into a model, so it satisfies no PDE exactly by construction.
A residual also needs all prognostic variables at all levels, while the npz gives a few channels.

The useful distinction is kinematic versus dynamic.
Constraints on the function space are portable.
Constraints on the dynamics are not.
A dynamic constraint needs the equation, coefficients, source term, and boundary data.
A kinematic constraint needs only a property of the field, discoverable from the data itself.

Incompressibility is the sharpest illustration.
Enforcing `∇·u = 0` says nothing about the momentum equation, the Reynolds number, the viscosity, the forcing, or the boundary conditions.
It constrains which functions are representable, not how they evolve.
That is why it transfers to `fluid`, `lid_driven_cavity_generated`, and the `chin_chun` pair alike, while a Navier-Stokes residual does not.

`mf_fno_pinn_transfer` is the one family that embeds an equation.
It is #2 by Elo at 1799 and the best in the entire zoo by median relative-L2 at 0.0122, versus 0.0154 for the #1 family.
`model/README.md` headline takeaway #2 credits the physics term directly.
That is real evidence against the structural-constraints position, and this memo does not explain it away.

The attribution is untested.
The PDE and Dirichlet terms are soft penalties with `lam_pde = lam_bc = 1e-3` (`models/mf_fno_pinn_transfer/smoke_eval.py:41`).
Per its own docstring (`smoke_eval.py:8-12`), they are active only on the Poisson datasets.
Every other dataset falls back to plain FiLM transfer.
There are therefore two competing explanations for the rank, and they make different predictions.

The decisive experiment is to compare `mf_fno_pinn_transfer` against `mf_fno_transfer_film` on the non-Poisson datasets only.
Those two families share a backbone and a schedule.
The PDE term is the only mechanism that differs, and it is inert outside Poisson.

If the two are statistically indistinguishable off-Poisson, the physics contributes on 2 of 15 datasets.
The rest of the rank comes from FiLM transfer.
A mechanism that fires on 13% of the benchmark is a special case rather than a family.
The structural-constraints position then holds on the evidence, not just on principle.

If `pinn_transfer` also wins off-Poisson, something other than the PDE residual is responsible.
The candidate causes are schedule difference, initialization difference, or normalization difference.
That something should be found and given to every family.
Either way the result is actionable.

This experiment is currently not interpretable because `mf_fno_transfer_film` is not in this checkout and because F05 shows there is one seed and no variance estimate.
Resolve F05 first, or run at least 3 seeds for just these two families.

Before proposing a positivity-preserving multiplicative head, the record should be straight.
`fno_autoregressive` already implements `HF = ρ·LF_pred + δ` with a learned scalar ρ from Kennedy & O'Hagan 2000, and it ranks #22 of 30 (`model/README.md:106-107`).
So a multiplicative correction is not untried, and the tried version lost.
F14 is a different object, a per-pixel log-space correction rather than one scalar gain.
The honest prior is that the scalar version of this idea already failed on this benchmark.
Treat F14 as speculative, and rank it below F22 accordingly.

---

## F01. Three incompatible definitions of nRMSE coexist

The contract metric is per-sample relative-L2, each sample weighted equally.
The formula is `rel_l2 = mean_over_samples( sqrt(Σ diff²) / sqrt(Σ true²) )`.
This is corroborated at `references/v9_baseline/eval_mfrnp_v9.py:85`, and by the keys `bench/summary_report.py:18` and `bench/plot_extra.py:40-41` read.

Three different quantities are reported under that name.
Nine FIRE families plus others use per-sample relative-L2 via `finalize_and_write` at `models/_common/fire_core.py:312`.
`transolver_residual`, `transolver_attention_fusion`, `fno_mf_stack`, and `fno_coreg_residual` use dataset-aggregate `sqrt(Σ‖err‖² / Σ‖target‖²)` at `transolver_residual/smoke_eval.py:49-62`, `fno_mf_stack/smoke_eval.py:110-115`, and `fno_coreg_residual/smoke_eval.py:106-113`.
`transolver_residual` and `transolver_attention_fusion` compute relative-L2 over a 2048-point subsample, not the full field, at `transolver_residual/smoke_eval.py:167` with `n_hf=2048` at `:36`.

The aggregate form is dominated by large-magnitude samples and is systematically lower than the per-sample form whenever per-sample magnitude varies.
Because `composite_nRMSE` takes the minimum over families per dataset (`eval/score.py:169-170`), a family can win a dataset on metric definition alone.

---

## F02. Split asymmetry rewards not reporting OOD

`per_dataset_nrmse` is the unweighted arithmetic mean over whatever split keys a family chose to emit (`eval/score.py:116-120`).

Six families emit `{test, ood}`.
Those families are `fno_coreg_conditioned`, `fno_coreg_residual`, `fno_coregionalization`, `transolver_residual`, `transolver_attention_fusion`, and `v9_baseline`.

Fifteen families emit `{test}` only.
Those families are all 12 FIRE families, both DINO families, `fno_mf_stack` (`smoke_eval.py:296-298`), `mf_fno_transfer_bar`, and `mf_fno_pinn_transfer`.

OOD nRMSE is typically several times test nRMSE.
Averaging it in penalizes the six families that report it, independent of model quality.
The best-per-dataset composite then hands the win to test-only families.
The FIRE path never loads the OOD split at all.
`fire_core.py:237` reads only `"train"` and `"test"`.

---

## F03. `vs_paper` mixes aggregation rules

Ours is the arithmetic mean over splits (`eval/score.py:116-120`).
The paper number is the geomean over splits (`:140-141`).
Arithmetic mean is greater than or equal to geometric mean.
Therefore `ratio_ours_over_paper` (`:184`) is biased against us.
Therefore `beats_paper` (`:185`) is decided on non-comparable quantities.

The module docstring at `eval/score.py:9-10` says "mean over datasets" while the code computes a geomean (`:188-190`).
That docstring is stale and misleading to anyone reading for the definition.

---

## F04. `era5` and `pm_test` are scored against a downsampled target

`fire_core.py:243` sets `grid = cap_grid(hf_native)` with `WORK_CAP = 256` (`:135`).
Line `:247` bilinearly resamples the HF test target onto that grid via `to_grid` (`:152-157`), with `antialias` left at its default `False`.

For `era5`, the native HF grid is 721×1440 (`fno_coregionalization/smoke_eval.py:15`).
The target therefore becomes 128×256, a 5.6× decimation with no prefilter.
That folds everything above the new Nyquist back as aliasing.

A smoothed target is a strictly easier problem.
`eval/score.py` does not check `work_grid` before declaring `beats_paper`.
`work_grid` is recorded in the output JSON (`fire_core.py:301, :314`), so the gate is one comparison away.
Per `fno_coregionalization/smoke_eval.py:64`, only `era5` and `pm_test` exceed the cap.
The other 15 datasets are unaffected.

---

## F05. No variance estimate exists, and the current leaderboard has a winner's curse

`eval/smoke_config.json` and `eval/full_config.json` both fix `"seed": 42`.
That seed is passed through unchanged (`eval/score.py:234`, `:61`, `:90`).
Every reported number is a single run.

Determinism is incomplete.
Repo-wide, there are zero hits for `torch.cuda.manual_seed*`, `cudnn.deterministic`, `use_deterministic_algorithms`, `CUBLAS_WORKSPACE_CONFIG`, or any TF32 control.
`SpectralConv2d` is cuFFT plus `einsum` (`fire_core.py:44-52`).
Convolution and GroupNorm backward on CUDA use atomics.
The same command twice on the same GPU therefore does not give bit-identical results.
TF32 is on by default on H100.
That creates a silent roughly `1e-3` relative perturbation when unpinned.
`transolver_*` and `v9_baseline` train under AMP fp16 (`transolver_residual/smoke_eval.py:52,79,132`) while every FNO family runs fp32.
Different numerical noise floors are therefore ranked against each other.
`mit_preemptable` has heterogeneous GPU types (`eval/run_smoke.sbatch:9`), so a requeue can change hardware mid-benchmark.

Compounding this, `min` over roughly 22 families with one seed each (`eval/score.py:169-170`) selects the luckiest noise draw.
Adding a family can only lower the composite.
Therefore the composite drifts downward as the zoo grows and is not a measure of any single model.

The practical consequence is an estimated noise floor, not a measured one.
The intended reading is an absolute delta of roughly `0.01` in relL2 units, not a 1% relative delta.
The 0.0122 versus 0.0154 median relative-L2 gap has delta 0.0032, so it falls inside that estimated floor.
Under the absolute-delta reading, essentially all current leaderboard ranks 1-15 collapse into one indistinguishable band until sigma is measured.
The `1e-2` estimate is argued from TF32 magnitude and known nondeterminism sources.
Nothing in the current harness measures the noise directly.

The corrected ask is a sparse noise-floor calibration, not a three-seed rerun of the whole benchmark.
First do F13, because the determinism fix is nearly free and should shrink sigma before measuring it.
Then measure run-to-run sigma on roughly 3 families times roughly 4 datasets times 3 seeds, about 36 runs or about 8% of one full benchmark.
Sample across the two axes sigma plausibly varies along: precision and dataset conditioning.
Once sigma is known, apply it as a resolution threshold to the 436 existing leaderboard cells.
No re-benchmark of those cells is required.

---

## F06. `code_hash` does not cover shared code

`eval/score.py:53-58` computes `code_hash` as a sha256 over `sorted(family_dir.rglob("*.py"))`.

`models/_common/{fire_core,fire_methods,recipe_hash}.py` sit outside every family directory.
Yet 12 families' entire training and evaluation logic lives there.
Editing `fire_core.py`, including the optimizer, schedule, residual runner, and all of `fire_run`, invalidates zero cached results.
The same hole applies to `data_adapters/*`.
It also applies to `references/v9_baseline/{train_v9,eval_v9}.py`, which `transolver_residual/smoke_eval.py:31-32` imports its dataset and collate function from.

Non-`.py` inputs are also unhashed.
Those include `manifest.json`, per-family `full_config.json`, and the dataset contents.
This interacts with F09 to produce silent wrong results.

Suggested fix if the surface is opened: hash `models/_common/**`, `data_adapters/**`, and the family's non-`.py` configs alongside the family directory.
This is one function.

---

## F07. `fire_run` has no checkpoint resume

`eval/MODEL_CONTRACT.md` makes resume mandatory because `mit_preemptable` jobs are preempted and requeued.
`models/_common/fire_core.py:226-316` contains zero `torch.save` or `torch.load` calls.
It never reads `args.ckpt_dir`.

The affected families are all 33-line wrappers delegating to `fire_run`.
They are `fno_fire_batchens`, `fno_fire_cqr`, `fno_fire_dkl`, `fno_fire_iqn`, `fno_fire_laplace`, `fno_fire_mdn`, `fno_fire_quantile`, `fno_fire_snapshot`, and `fno_fire_swag`.

The regression came from the refactor into `_common`.
The copied-out variants that predate it do implement resume (`fno_fire_distcond/smoke_eval.py:193-206, 225-227`).

The fix is one save/load of `{lf_state, fno_d_state, opt, sched, epoch, res_scaler, code_hash}` in `fire_core.py`.
This is the highest-leverage single mutable edit in the repo.
It is one function, nine families, and inside the mutable surface.

Relatedly, `eval/run_smoke.sbatch:44-50` traps `USR1` and comments "letting current iteration save its checkpoint."
No Python file installs a SIGUSR1 handler, with zero hits for `signal.signal` or `SIGUSR1`.
Python's default action for SIGUSR1 is to terminate.
The graceful-save path therefore does not exist.

---

## F08. Two families refuse to load their own mid-training checkpoints

`fno_coreg_conditioned` and `fno_coregionalization` write `last.pt` every `ckpt_every=10` epochs.
Their resume guards accept only a completed run where `stage == 2 and epoch == args.epochs`.
The citations are `fno_coreg_conditioned/smoke_eval.py:306-321` for the guard and `:325-331` for the save.
The parallel citations are `fno_coregionalization/smoke_eval.py:314-330` and `:336-343`.

A mid-training checkpoint is always discarded.
Training restarts from epoch 1.
The checkpoint I/O cost is paid and none of the benefit is received.
Neither family saves optimizer or scheduler state.

Six more families save exactly once, after all training completes.
They are `fno_dino_cond:221-223`, `fno_dino_residual:231-233`, `fno_fire_distcond:222-224`, `fno_fire_mcdropout:198-200`, `mf_fno_pinn_transfer:204`, and `mf_fno_transfer_bar:166-167`.
Preemption at 99% of training loses 100% of it.

Only four of 21 are correct.
They are `fno_coreg_residual`, `fno_mf_stack`, `transolver_residual`, and `transolver_attention_fusion`.
Even those never save RNG state.
A preempted run's data ordering therefore diverges from an uninterrupted one.
The same config yields two different numbers depending on whether SLURM preempted it.

---

## F09. Stale checkpoints can silently skip training entirely

`ckpt_dir = ckpt_root / fam_name / ds_name` (`eval/score.py:72`).
It is keyed by neither `epochs`, `seed`, nor `code_hash`.
Meanwhile family resume guards check `epochs_target` and `grid`, plus optionally `recipe_hash`.
`models/_common/recipe_hash.py:10-12` computes that hash over `SMOKE_DEFAULTS` only, not over any code.

The failure mode is direct.
Edit `model.py` or a training loop without touching `SMOKE_DEFAULTS`.
`code_hash` changes.
The results cache misses.
The family reruns.
It loads the old `last.pt`, sets `trained = True`, skips training, and writes a fresh result JSON reflecting the previous code.
It looks exactly like a legitimate cache miss.

A shape-changing edit raises inside `load_state_dict` and is caught into a fresh start.
A shape-preserving edit resumes cleanly and does nothing.
Examples include learning rate, loss weights, normalization, and schedule.

The most exposed families have no `recipe_hash` guard at all.
They are `fno_coreg_conditioned`, `fno_dino_cond`, `fno_dino_residual`, `fno_fire_distcond`, `fno_fire_mcdropout`, `mf_fno_pinn_transfer`, and `mf_fno_transfer_bar`.

Also, `fno_coreg_conditioned/smoke_eval.py:413-414` and `fno_coregionalization/smoke_eval.py:428` load `best.pt` unguarded.
There is no `epochs_target`, `grid`, or `recipe_hash` check.
A stale `best.pt` from a prior configuration in the same `ckpt_dir` can be loaded for evaluation if the current run never beats it.

The fix inside the mutable surface is to have each family's guard store and compare a hash of its own source plus `models/_common/`.
The cleaner fix is keying `ckpt_dir` by `code_hash`.
That cleaner fix is in `eval/`, so it belongs with F06.

---

## F10. The residual net trains on in-sample LF predictions

`fire_core.py:259` fits the LF model on `X_lf`.
`fire_core.py:260` then computes `mu_hf, aug_hf = lfm.summaries(X_hf, s_lf)` from that same just-fitted model.

In these MF datasets, the HF conditions are typically a subset of the LF conditions.
At training time, the residual net sees an optimistically good `mu` and an optimistically small `sigma`.
At test time (`:286`), it sees genuinely out-of-sample LF summaries.
The conditioning distribution shifts between fit and inference.

This is the classic residual-stacking flaw.
It degrades precisely the uncertainty channels that the entire nine-way FIRE ablation exists to measure.
The comparison of which uncertainty source helps most is being run on uncertainty estimates that are systematically too confident at training time.

The fix is cross-fitting.
Compute `summaries` on `X_hf` out-of-fold with K-fold over the LF fit.
Then the residual net trains on the same kind of LF summary it will meet at test.
This is the most scientifically consequential bug in the memo because it biases an ablation toward a particular conclusion.

---

## F11. `fno_mf_stack` has three independent defects

`fno_mf_stack/model.py:81-89` is the only FNOBlock in the repo without `nn.GroupNorm(min(8,ch), ch)`.
Every peer has it at `fire_core.py:60`, `mf_fno_transfer_bar/model.py:56`, `fno_coregionalization/model.py:76`, and `fno_coreg_residual/model.py:88`.
This looks like an omission.
It would depress the family's numbers for a reason unrelated to its MF mechanism.

`fno_mf_stack` also has no gradient clipping.
It is the only family without a `grad_clip` key (`smoke_eval.py:39-55`).

It also builds a validation split and discards it.
`val_loaders` are constructed at `smoke_eval.py:166` but never evaluated.
`best_val` stays `inf` (`:203`) and no `best.pt` is written.
This is likely an unfinished edit.

It also uses default FFT normalization rather than `norm="ortho"` at `model.py:61,78`.
That is benign because the transform pair is self-inverse either way.

---

## F12. `randperm` inside the batch loop is not epoch semantics

The affected code pattern is:

```python
for _ in range(epochs):
    for i in range(0, n, bs):
        idx = torch.randperm(n, generator=g)[i:i + bs]
```

A fresh permutation is drawn per step.
An "epoch" is therefore a with-replacement sample across batches.
Roughly 1/e of the dataset is unseen in any given epoch and other samples are seen twice.
This is still unbiased SGD.
It is not epoch semantics.
It also costs an O(n) permutation per optimizer step.

Sites are `fire_core.py:192, 208`; `fire_methods.py:52, 110, 166, 211, 262, 312`; `fno_dino_cond:82,101`; `fno_dino_residual:84,107`; `fno_fire_distcond:82,107`; and `fno_fire_mcdropout:73,96`.

The fix is to hoist `perm = torch.randperm(n, generator=g)` one loop level up.
That is one line per site.

---

## F13. Seeding is incomplete

Every entry point does only `torch.manual_seed(seed)` and `np.random.seed(seed)`.
The citations are `fire_core.py:234`, `fno_coreg_conditioned:241-242`, and `transolver_residual:73`.

Missing pieces are `torch.cuda.manual_seed_all`, stdlib `random.seed`, cuDNN determinism flags, and an explicit TF32 decision.
See F05 for why this matters at the resolution the leaderboard is read at.
This should be done before the sparse noise-floor calibration.

---

## F14. Positivity should use a multiplicative or log-space head

The structural-constraint backdrop is that no output constraint of any kind exists in any of the 21 families.
Every terminal operation is a bare `nn.Conv2d(·, out_ch, 1)` or `nn.Linear(·, 1)` with no trailing activation.
In every `nn.Sequential` head, the pattern is `Conv2d → GELU → Conv2d`, with the GELU between the two 1×1s and never after the last (`fire_core.py:102`, `fire_core.py:123`, `fno_coreg_residual/model.py:124-130`, `fno_mf_stack/model.py:100-102`, `transolver_*/model.py:40-45`).

A repo-wide grep for `Sigmoid|Softplus|Tanh|ReLU|softplus|exp|clamp|abs|mask|positive` returns zero hits on any output path.
Every hit is one of three categories.
One category is internal attention softmax.
One category is a distribution-parameter guard rather than a field guard (`fire_methods.py:299-300` clamps MDN `logσ`, `:121` clamps SWAG variance, and `:401`/`:415` clamp noise variance).
The last category is a metric denominator guard.

`mf_fno_pinn_transfer` is the closest thing to physics-aware and is still a pure soft penalty (`smoke_eval.py:41`), never a projection.
The only structural output transform anywhere is a constant per-fidelity de-normalization scalar (`fno_coregionalization/model.py:162-163`).
That is a rescale, not a constraint.

The three residual families anchor their output to the LF field (`fire_core.py:288`, `transolver_residual/model.py:178`).
That is a prior, not a constraint.
Nothing prevents the sum from leaving the physical range.

This applies where the field is nonnegative by nature.
Candidate fields are absolute temperature, concentration, density, permeability (`darcy_generated`), and specific humidity (`era5`).

The naive `HF = mu_LF + softplus(delta)` is wrong.
It forces the correction to be one-signed, so the model can only ever increase the LF prediction.
The correct form makes the correction multiplicative:

```python
HF = mu_LF * softplus(delta)
```

Equivalently, `log HF = log mu_LF + delta`.
Positivity is automatic whenever `mu_LF > 0`.
The secondary benefit is that MF discrepancies are often relative rather than absolute.
A coarse solver that is 5% low everywhere is a constant in log space and a spatially varying function in linear space.

This interacts with the global max-abs scalers in F19.
It would also equalize loss weight across the interior and thin boundary layers.
That is the specific failure mode expected on `lid_driven_cavity_generated` and `fluid`.

The traps matter.
Positivity in physical units is not positivity in scaled units.
The constraint must be applied before normalization, or the shift must be carried explicitly.
If the field genuinely reaches zero, `softplus` never gets there and gradients vanish near the floor.
Only impose this where the data minimum is comfortably above zero.

Confidence is low to moderate.
Per P01, the scalar-ρ version of this idea is already implemented as `fno_autoregressive` and ranks #22 of 30.
The per-pixel log-space version is a materially different function class, but the prior is not encouraging.

---

## F15. Global integral conservation can be enforced by projection

The claim is to assert that a scalar total is preserved, and enforce it by projection after the network.

```python
raw = mu_LF + delta
u   = raw + (C - raw.sum()) / N
u   = raw * (C / raw.sum())
```

The additive form preserves fluctuation shape.
The multiplicative form also preserves positivity.
A rank-1 projection is differentiable, free, and exact.

`C` can come from the LF field without knowing the PDE.
Use `C = mu_LF.sum()`.
This is not asserting a conservation law.
It asserts that whatever the LF solver conserves, the HF field conserves too.
Finite-volume LF solvers are conservative by construction.
This usually holds and is empirically checkable through F18.

It should help the metric directly.
Squared error decomposes into a mean-offset term and a fluctuation term.
This projection annihilates the mean-offset term exactly.

It may help more than that here.
`model/README.md:18-19` reports that for the FIRE families "the *mean* relL2 is wrecked by a few blow-up datasets."
On a geomean composite, a single blow-up dataset is devastating.
A projection is a hard bound on that failure mode.
The prediction cannot drift arbitrarily far in the mean, no matter what the residual net does.
This is the strongest argument in the memo for constraints.
It is an argument about robustness, not average accuracy.

Confidence is moderate, conditional on the F18 probe showing a tight LF/HF total ratio.

---

## F16. Divergence-free velocity can be enforced via a stream function

This applies for incompressible velocity fields.
Candidate datasets are `fluid`, `lid_driven_cavity_generated`, and plausibly the `chin_chun` pair.

Do not predict `(u, v)` and penalize `∇·u`.
Predict a stream function ψ and take `u = ∂ψ/∂y`, `v = -∂ψ/∂x`.
Then `∇·u = 0` identically, to machine precision.

In an FNO this is unusually clean.
The derivative is multiplication by `ik` in Fourier space.
That is exact on periodic domains, has no finite-difference truncation error, and the model is already in that basis.
An equivalent alternative is a Helmholtz projection if the velocity head must be kept.
That projection is `û ← û − k(k·û)/|k|²`, one spectral layer.

Per P01, this is a kinematic constraint.
It does not import any dynamic assumption.
Confidence is moderate, but gated on whether these datasets actually expose multi-channel velocity.
That is unverified in U01.

---

## F17. Hard boundary conditions can replace soft Dirichlet penalties

Replace the soft Dirichlet penalty (`mf_fno_pinn_transfer/smoke_eval.py:136`, `lam_bc=1e-3`) with a mask:

```python
u = g + φ · NN(x)
```

Here φ vanishes on ∂Ω.
The boundary condition then holds exactly regardless of what the network does.
There is no hyperparameter.
`g` need not be known analytically.
It can be taken from the LF field's boundary values.
That makes this PDE-agnostic in the same sense as P01.

---

## F18. A detection probe is needed before enabling constraints

This is the part that separates the proposal from `mf_fno_pinn_transfer`.
Each constraint requires knowing only which channels are nonnegative, which channels form a vector field, and whether some integral is stable between LF and HF.
All three are detectable from training data.
The constraint layer can therefore adapt per dataset instead of being hardcoded to one equation.

The deliverable is a probe script that reports four tests for each of the 17 datasets.
The positivity test reports `min(HF_train)` and `min(LF_train)`, and enables the constraint if both are greater than 0 with margin at least 5% of field standard deviation.
The conservation test reports the distribution of `HF.sum() / LF.sum()` per sample, and enables the constraint if the ratio is within 1 ± 0.02 for at least 95% of samples.
The vector-field test reports channel count and metadata, and enables the constraint if at least two channels are identifiable as components.
The boundary test reports variance of HF on ∂Ω, and enables the constraint if it is near-constant and Dirichlet-like.

Each constraint should turn on only when its test passes.
The script should log which constraints fired per dataset.
It should fall back to the unconstrained head otherwise.

The failure mode to guard against is imposing a constraint that is not true in the data.
That actively hurts accuracy.
Detection must be empirical and conservative.
A false positive here is worse than a missed opportunity.

This probe cannot be run from this checkout.
All 17 `data/` entries are dangling symlinks to the cluster tree (`scripts/env.sh:13`, `/orcd/data/faez/001/nick/mf_field/factory_mffp`).
The per-dataset applicability table has to be generated there.
It is the first concrete task if this direction is pursued.

---

## F19. The training loss does not match the scored metric

`models/_common/fire_core.py:210` contains:

```python
loss = F.mse_loss(model(Xt[idx], At[idx]), Yt[idx])
```

The target is built at `fire_core.py:261-262`:

```python
residual   = (Y_hf - mu_hf).astype(np.float32)
res_scaler = max(float(np.abs(residual).max()), 1e-8)
```

`res_scaler` is a single global scalar.
It is max-abs over the entire HF training set.
`F.mse_loss` averages over pixels and samples uniformly.
Every sample therefore contributes in proportion to its absolute squared error in one fixed global unit.

The metric is `mean_i ‖pred_i − true_i‖ / ‖true_i‖`.
A sample whose field energy is 10× below the dataset median contributes about 1/10 of the gradient it deserves.
It still counts exactly as much at scoring time.

This one line governs nine families.
The identical construction is copy-pasted into `fno_fire_distcond/smoke_eval.py:115-116, 216-217` and `fno_fire_mcdropout/smoke_eval.py:104-105, 194-195`.
That gives 11 of 21 families with identical exposure.

There is in-repo precedent for the fix.
`transolver_residual/smoke_eval.py:65-69` contains:

```python
mse = torch.mean(diff ** 2)
rel = torch.sqrt(torch.sum(diff**2, dim=1)) / torch.clamp(torch.sqrt(torch.sum(targets**2, dim=1)), min=1e-4)
return mse + torch.mean(rel), mse
```

The `rel` term is exactly the scored quantity.
It is reduced per sample, then averaged, so it is scale-invariant and weights every sample equally.
Its provenance is the frozen reference `references/v9_baseline/train_v9.py:157-163`.
This is already sanctioned repo practice, not a new idea.

This is the highest-confidence item in the memo.
It is a known mismatch, a fix with in-repo precedent, and 11 families of breadth.

---

## F20. The model-selection metric mismatches too

Every family that does validation-based selection selects on a pooled, energy-weighted nRMSE.
That metric is `sqrt(Σ_i Σ_p err² / Σ_i Σ_p true²)`, not the per-sample mean.
The citations are `fno_coreg_conditioned/smoke_eval.py:215-220`, `fno_coreg_residual/smoke_eval.py:169-174`, `transolver_residual/smoke_eval.py:57-62`, and `transolver_attention_fusion/smoke_eval.py:45-50`.

Low-energy samples are underweighted at selection time as well as at training time.
The fix is cheap.
It should be made in the same edit as F19.

---

## F21. Two families train in raw physical units

`fno_coregionalization` and `fno_coreg_conditioned` de-normalize inside the model.
The citations are `model.py:163` and `model.py:213-214`.
They take the loss on the de-normalized output.
The citations are `smoke_eval.py:370` and `:358`.

The effective gradient on each fidelity's head is weighted by that fidelity's scaler.
This is a per-fidelity weighting distortion layered on top of the per-sample distortion in F19.

---

## F22. `modes_cap = 12` never scales with resolution

The relevant code is:

```python
# models/_common/fire_core.py:147-149
def modes(grid, c):
    H, W = grid
    return (min(c, max(H // 2, 1)), min(c, W // 2 + 1))
```

The `min(c, ...)` makes the mode count constant at 12 for every grid at least 24×22.
`SpectralConv2d.forward` (`fire_core.py:47-51`) writes only the `[:mh,:mw]` and `[-mh:,:mw]` corners into a zero-initialized output.
Every unwritten Fourier coefficient is set to exactly zero.
This is a hard low-pass, not an attenuation.

On a 256×256 work grid, the `rfft2` has 256×129 = 33,024 coefficients and 24×12 = 288 survive.
That is 0.87% of the spectrum.
On 64×64 it is 11%.

`modes_cap=12` is the setting in every FNO-backbone family except `fno_coregionalization`.
`fno_coregionalization` raised it to 16 as part of a coupled width/depth capacity bump.
The effect of the mode count alone was never isolated.
The two transolver families are attention-based and have no Fourier modes, so they are outside this finding.

This may explain the leaderboard shape.
For the non-augmented `FNO2d` families, the only spatially varying input is a two-channel linear coordinate ramp (`fire_core.py:67-70`, lifted at `:79,85`).
The conditioning vector is broadcast to a spatial constant (`_broadcast_cond`, `:91-93`).
All HF spatial content must therefore be synthesized from a linear ramp through at most 12 Fourier modes plus GELU harmonics.
Sharp features are structurally unreachable.

The augmented families predict `HF = μ_LF + δ` (`fire_core.py:288`).
The LF field's high frequencies pass through additively.
The truncation limits only the correction.
That is a plausible mechanism for why residual/additive families dominate the leaderboard.
They are the only ones not paying the full low-pass penalty.

The proposed experiment is a clean `modes_cap` sweep from 12 to 24 to 32 to Nyquist at fixed width and depth.
This is the highest-value single experiment the repo has not run.

Also, `to_grid` upsamples the LF field to the HF work grid (`fire_core.py:245`).
Therefore `mu_LF` is band-limited by construction and cannot contain structure above the LF Nyquist.
The residual net must supply all fine detail through those 12 modes.

---

## F23. The backbone is not held constant, contrary to the stated protocol

`model/README.md:10-11` claims the backbone is "held roughly constant so the comparison isolates the MF mechanism."
It is not.

Capacity differs.
`fno_coregionalization/smoke_eval.py:74-78` runs `hidden=128, n_blocks=6, modes_cap=16, K=20, b_hidden=128` against the zoo standard `64 / 4 / 12`.
That is roughly 4× the trunk FLOPs and 33% more Fourier modes.
The comment at `:70-73` documents this as a deliberate "H1 cycle-008 paper-config capacity bump."
Its sibling `fno_coreg_conditioned/smoke_eval.py:70-75` explicitly documents refusing the same bump.
The two coregionalization families exist to A/B the fusion mechanism.
They also differ in width, depth, and mode count.
That comparison measures capacity, not mechanism.

Mode schedules differ.
`fno_mf_stack` uses `modes_per_level=(4,8,16,20)`.
`fno_coreg_residual` uses `n_blocks=3` with `(4,8,12,12)`.
Neither uses the shared `modes()` schedule.

Optimizer protocol splits cleanly by lineage.
All FIRE, DINO, and transfer families use `lr=1e-3, bs=16`.
Coreg and `mf_stack` use `lr=3e-4, bs=8`.
Transolver uses `lr=3e-4, bs=4`.

Validation fraction also differs.
It is 0.1 for the FNO families.
It is 0.2 for transolver and v9.
Those groups train on different amounts of data and are ranked against each other.

The recommendation is to either propagate the capacity bump to all families or revert it.
Leaving it on exactly one family is the worst of the three options.

---

## F24. LF-stage ensembling is a capacity confound

Six families ensemble at the LF stage.
The ensemble mean is the additive base of the final prediction (`fire_core.py:260, 288`).
The families are `fno_fire_distcond` with five full FNOs, `fno_fire_snapshot` and `fno_fire_cqr` with five snapshots, `fno_fire_swag` with 10 samples, `fno_fire_batchens` with five heads, and `fno_fire_mcdropout` with 16 passes.

`model/README.md` reports `fno_fire_distcond` and `snapshot` and `cqr` at 28.4M params.
That compares to 9.48M for single-model FIRE variants and 4.77M for the transfer families.
`fno_fire_distcond` ranks #3 partly on 5× the compute.
No family ensembles the HF correction network.

---

## F25. HF-stage regularization is largely absent

The HF stage fits scarce data with essentially no guard against overfitting.
Dropout is 0 in every family except `fno_fire_mcdropout`, and there only on the LF net (`smoke_eval.py:41`).
`FNO2dAug` does not expose a dropout argument at all (`fire_core.py:119-123`).
That is the residual network every FIRE family trains on the scarce HF split.
The HF-fitting stage is structurally un-regularizable.

`weight_decay=1e-5` (`fire_core.py:179`) is negligible.
Fifteen of 21 families have no validation split at all.
`fire_run` never builds one, never early-stops, and takes the final-epoch weights unconditionally (`fire_core.py:279`).
Contrast `references/v9_baseline/smoke_eval.py:138,150`, which tracks `best_val` and reloads the best checkpoint.

There is no LR warmup anywhere.
Cosine annealing is present (`fire_core.py:180`, `CosineAnnealingLR(T_max=epochs, eta_min=1e-6)`).
Gradient clipping is present everywhere except `fno_mf_stack`.
Warmup, EMA, SWA, and early stopping are absent repo-wide.
The repo-wide zero-hit search terms were `patience` and `early_stop`.

A fixed epoch budget on a handful of HF samples with no overfitting guard is a plausible mechanism for the "few blow-up datasets" reported at `model/README.md:18-19`.
That is also the failure mode F15 is designed to bound.
These two items address the same symptom from different directions and should be evaluated together.

---

## F26. The smoke/full gap interacts badly with the cosine schedule

Smoke is 200 epochs, and full is 2500.
The citations are `eval/smoke_config.json` and `eval/full_config.json`.
Because `T_max=epochs`, these are not the same run truncated.
They are two different LR trajectories, each annealed to `eta_min` at its own horizon.
A method that benefits from a long low-LR tail is indistinguishable at 200 epochs from one that does not.

Compounding effects follow.
`fno_coreg_*` split epochs by fraction with `pretrain_frac=0.25`.
Smoke gives 50 warm-up and 150 fine-tune.
Full gives 625 warm-up and 1875 fine-tune.
That is a different recipe, not a shorter one.

`SnapshotLF` uses `epc = epochs // K` with K=5 (`fire_methods.py:41`).
Smoke runs 40-epoch snapshot cycles.
Snapshot diversity is a function of cycle length.
Smoke is therefore measuring a different method.

`MDNLF` warms up on MSE for `int(0.4*epochs)` (`fire_methods.py:308`).
That is 80 epochs for smoke versus 1000 epochs for full before the NLL objective engages.
Capacity-heavy families are the most underfit at 200 epochs.
Smoke systematically favors small models.

There is no evidence in the harness that smoke ranking transfers to full ranking.
Keep/revert decisions are currently made on smoke.

---

## 2. Ranked mutable and decision work

This ranking preserves the original severity information while replacing the mixed ID column with the unified IDs.

| Rank | Item | Evidence | Breadth | Effort | Confidence | Surface |
|---|---|---|---|---|---|---|
| 1 | Checkpoint resume in `fire_run` | F07 | 9 | 1 function | Certain contract violation | `models/**` |
| 2 | Per-sample relative-L2 loss term | F19 | 11 | 1 function, precedent exists | High | `models/**` |
| 3 | Unify the nRMSE definition | F01 | 4 deviate, all 21 compared | Fixed-surface approval | Certain | `eval/`, escalate |
| 4 | Cross-fit LF summaries | F10 | 11 | Moderate | High | `models/**` |
| 5 | `modes_cap` sweep | F22 | 19, all FNO-backbone | Compute only | High value, unknown sign | `models/**` |
| 6 | Fix split asymmetry | F02 | 21 | Fixed-surface approval | Certain | `eval/`, escalate |
| 7 | Determinism fix, then sparse noise-floor calibration | F05 and F13 | 21 | Nearly free code plus about 36 runs | Certain need, measured size unknown | Both |
| 8 | Validation split and early stopping | F25 | 15 | Moderate | Moderate | `models/**` |
| 9 | Conservation projection | F15 | Probe-dependent | Small | Moderate | `models/**` |
| 10 | Guard stale checkpoints | F09 | 7 | Small | Certain | `models/**` |
| 11 | `code_hash` over `_common/` | F06 | 12 | 1 function | Certain | `eval/`, escalate |
| 12 | Resolve backbone inconsistency | F23 | 21 | Policy call | Certain | `models/**` |
| 13 | Expose dropout in `FNO2dAug` | F25 | 11 | Trivial | Moderate | `models/**` |
| 14 | `fno_mf_stack` GroupNorm, grad_clip, and validation | F11 | 1 | Trivial | High | `models/**` |
| 15 | Hoist `randperm` | F12 | 12 | Trivial | Certain semantics and speed | `models/**` |
| 16 | Divergence-free head | F16 | Probe-dependent | Moderate | Moderate | `models/**` |
| 17 | Hard BC mask | F17 | Probe-dependent | Small | Moderate | `models/**` |
| 18 | Gate `beats_paper` on `work_grid` | F04 | 2 datasets | 1 comparison | Certain | `eval/`, escalate |
| 19 | Positivity or log-space head | F14 | Probe-dependent | Small | Low, see P01 | `models/**` |

The suggested order is to run the P01 attribution experiment and the F18 probe first only after the F05/F13 noise decision is settled.
Then do F07, F19, and F10, because all are mutable-surface and high confidence.
Escalate F01, F02, F03, F04, and F06 in one conversation because they share a scoring-validity root cause.

---

## 3. What this memo could not verify

## U01. No data was read

All 17 `data/` entries are dangling symlinks into the cluster tree (`scripts/env.sh:13`).
Every claim about field structure, positivity, conserved integrals, channel layout, or HF/LF sample counts is inference from code and paper provenance, not measurement.
The F18 probe exists precisely to close this gap and must be run before any constraint is implemented.

## U02. The dataset count is inconsistent in the repo itself

`eval/full_config.json` lists 17 datasets.
`model/README.md:3` reports the benchmark as 30 families × 15 datasets, with 436/450 cells.
This memo uses 17 when reasoning about the data in P01.
It uses 15 when quoting leaderboard coverage in P01.
Which two datasets are excluded from the benchmark, and why, was not determined.
That is worth resolving, since P01's "2 of 15" ratio depends on whether the Poisson datasets are among them.

## U03. Only 21 of 30 families are in this checkout

Absent families are `mf_fno_transfer_film`, `mf_fno_transfer`, `mf_fno_transfer_2m`, `fno_additive`, `fno_multilevel`, `fno_autoregressive`, `fno_coreg_lf_hf_transfer`, `mfrnp`, `d_mfd`, and `mf_deeponet`.
Notably, this includes the #1 family and both families in the P01 experiment.
That experiment must be run on the cluster.

## U04. `data_adapters/` internals are not present

Only `npz_compat.py` is tracked.
`load_mf_dataset`, `resolve_grid`, and `finalize_and_write` were not read.
The metric definition in F01 is corroborated from `references/v9_baseline/eval_mfrnp_v9.py:85` and the keys consumed at `bench/summary_report.py:18`.
It was not read from `metrics.py`.
If `finalize_and_write` differs from that formula, F01 and F19 both need revisiting.

## U05. No code was executed

Every performance claim is a mechanism argument, not a measurement.
In particular, the confidence column in the ranking rates how sure the diagnosis is.
It never rates how much nRMSE the fix will buy.

## U06. `model/README.md` numbers are taken as given

The taken-as-given numbers are 30 families × 15 datasets, 436/450 cells, seed 42, and 2500 epochs.
Per F05 they carry no variance estimate.
All rank comparisons quoted in this memo inherit that limitation.
That includes the 0.0122 versus 0.0154 gap that motivates P01.
