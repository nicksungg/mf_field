# Summary so far — stream `r2s1_direct`, batch 1

## 1. Websearch findings + prior-art verdict

Source: `websearches/r2s1_direct/batch_1/report.md` (4 iterations, 10 WebSearch /
9 WebFetch). Verdict table, verbatim rows:

- **D1** "FiLM/modulation-conditioned spectral (FNO) decoder: condition -> latent ->
  HF field, no field input" -> **`preempted`**; "Nothing mechanism-level.
  Admissible only as a *measurement/baseline arm* on this panel against the
  mandatory floor arms." (cites arXiv 2601.22654v1, 2511.09729v1, ModAFNO in
  PhysicsNeMo.)
- **D2** "Condition -> coefficients of a fixed/learned output basis (POD/RB trunk)"
  -> **`preempted`**; "it is POD-NN/PCA-Net prior art under a new name."
  (PODNO 2504.18513v1, RB-DeepONet 2511.18260, both fetched.)
- **D3** "Per-dataset identifiability certification: estimate the
  conditional-mean/aleatoric floor for condition->HF, and validate it by showing
  the missing driver lives in the withheld LF field" ->
  **`preempted-but-MF-composition-open`**; open: "(i) the barrier diagnostic has
  never been instantiated where the unobserved driver is a *stored coarse solve*,
  making the floor validatable rather than assumed; (ii) NN-in-condition /
  train-mean / zero as a standing certification panel is not done in the fetched
  benchmark literature." (arXiv 2605.28076 fetched; REALM 2512.18595 fetched.)

For-the-brainstormer directives (report.md section "For the brainstormer"): quote
the verdict; D1/D2 only as declared baseline arms; **the only open composition
found is D3**; do not make distributional metrics primary (program 2.1 is frozen);
floor arms are a contribution; scarcity fixes in the literature are *acquisition*
methods, barred by 5.11; Lanthaler (2210.01074, via the in-repo sharp report)
proves linear-reconstruction architectures (DeepONet, PCA-Net, fixed-POD) are
provably inefficient for *discontinuous* operators — 4 of 6 panel datasets.

## 2. Section 12 conventions (program.md 12.1, verbatim)

> - **Bar**: the per-dataset floor table (2.3). Beating NN-in-condition with 400
>   train samples is necessary but nowhere near sufficient; the interesting
>   question is how close a from-scratch condition->HF surrogate gets to skill 1.0
>   on each dataset.
> - Design priors (spec 6): FiLM-conditioned FNO **decoders** (condition ->
>   spectral latent -> field), DeepONet-style branch-trunk (branch on condition,
>   trunk on coordinates), spectral/implicit decoders (SIREN/modulated INR
>   class). Condition vectors are 2-19 dims; ifc_poisson's is 5-dim.
> - **ADR r2-0003 (corrects a spec 4 grounding fact)**: on pfc, fisher_kpp
>   and allen_cahn the condition vector is NOT complete — per-sample random
>   ICs live only in the fields, so condition->HF is a stochastic map and
>   deterministic models are bounded by the conditional-mean floor
>   (train_mean > NN on those floors is the symptom). Skill -> 1 is unreachable
>   there; design and falsify against the conditional-mean floor, and treat
>   bare FiLM-decoders as declared baselines (prior-art verdict: preempted).
> - **Helmholtz lesson** (r1 report 5): the zero field is the floor to beat
>   there — any helmholtz claim must show the zero-floor column.
> - **pfc caveat** (2.3): denominator 0.007381 under variant C; no
>   fidelity gap under band-limited. State it on every pfc claim.
> - N_hf on ifc_poisson is 5 — every claim there is anecdote-grade; prefer
>   variance-reducing designs (r1 s1 lesson: ensembling, physics residuals are
>   out per ADR 0009 — physics-agnostic at test).
> - Overfitting is THE central threat at these sample counts; r2s4's
>   overfitting-anatomy diagnostics feed this stream. Train/val discipline in
>   the recipe is mandatory (no test-split peeking; the round-1 D3 val_idx
>   double-consumption caveat is the cautionary tale).

Anchor (`state/anchors/r2s1_direct.json`): `best_floor_panel_geomean` =
**23.0636**, `provisional: false`. Per-dataset best floors (`floors.json`):
helmholtz 3.3441 (zero), pfc 59.812 (train_mean), allen_cahn 269.196 (NN),
fisher_kpp 11.993 (train_mean), cahn_hilliard 23.180 (NN), ifc_poisson 10.055 (NN).
`state/noise_floor.json` is `_provisional: true` (round-1 batch-0 rescaled, from
LF-**consuming** families) -> judged directly per 4.3 until r2s4-B1 certifies.

## 3. Within-stream prior cards

**None.** `experiment_cards/r2s1_direct/` contains no `B*.json` (verified by
`find ... -name "*.json"`). Batch 1 is the stream's first card.

## 4. Cross-stream cards

**None** (no round-2 card exists in any stream). Light scan of the sibling
batch-1 websearch verdicts for turf collisions:
`websearches/r2s4_diag/batch_1/report.md` D1b owns the **test-split** training-free
floor panel and D1a owns the 3-seed spread certification (r2s4-B1 is pre-directed
to both); `r2s3` D1/D2 own LF-as-training-signal; `r2s2` D1/D2 own the
pseudo-LF -> corrector stack. None of them claims the **train-split
identifiability/aleatoric estimate**, which is r2s1's D3 slot.

Round-1 inputs that bear directly (read, not guessed):
`round1/experiment_cards/s5_tuning/batch_3/B3.json` part 7 — on helmholtz the
LF-proxy per-sample scaler reached 0.367721 while the **true-scale oracle**
reached 0.258380 (skill 0.784 under the OLD denominator; 0.864 under the
corrected 0.299033), and the stream closed on the explicit open question "(i) a
PREDICTED scale head ... but its own turn 3 shows the predictor's error becomes the
accuracy floor". `round1/state/orchestrator_flow.md:2801` — the **two-gate loss
rule** (lambda <= 1 always + low-norm tail gate; remedy = p25-median denominator
floor + inference-time per-sample amplitude calibration; "60% of damage is the
amplitude channel"). `round1/docs/round1_report.md` 5.3 — helmholtz zero-predictor.

## 5. Reopen candidates

**None** (no prior cards in this stream, hence no `reopen_candidate: true`).

## 6. What is UNKNOWN

Read-only measurements I ran on the **train split** of the stripped view (scripts
in scratchpad; numbers reproduced in `iteration_1.md`) to size the unknowns:

1. **Where is the identifiability boundary really?** ADR r2-0003 groups pfc,
   fisher_kpp and allen_cahn as stochastic. Pair statistics (relative field
   difference between train samples vs their standardized condition distance)
   say pfc (flat profile, ~0.44 at every distance decile -> aleatoric ~ 0.30) and
   fisher_kpp (flat, 0.33-0.35 -> aleatoric ~ 0.235) are stochastic, but
   **allen_cahn's profile RISES with condition distance** (0.414 at d <= 0.198 ->
   0.698 at d <= 0.885, slope +1.195, intercept-at-zero 0.062) — the signature of
   a *deterministic but under-sampled* map, not a stochastic one. Unknown: which
   reading is right, and therefore whether allen_cahn's floor (269.2) has 2x or
   8x of headroom. This is decidable by a trained model.
2. **How much headroom exists at all?** Converting the aleatoric estimates to
   skill units: pfc's best possible deterministic skill ~ 0.30/0.007381 ~ 41 vs
   floor 59.8 (1.5x); fisher_kpp ~ 0.235/0.021450 ~ 11.0 vs floor 12.0 (1.1x) —
   i.e. **fisher_kpp is essentially exhausted before training starts**. Unknown
   whether a trained model realizes even that.
3. **Is the per-sample amplitude channel learnable from the condition alone?**
   `ext__helmholtz_2d` has cv(||y||) = **12.27** (1st-99th percentile 0.084 ->
   9.63, >100x) — round-1 families scored nRMSE 3.0-6.2 there under a single
   global `max|Y|` scaler, i.e. worse than the zero field. A LOO 5-NN on log||y||
   gives R2 = 0.140 (median scale error 42%) on helmholtz vs 0.965 / 0.986 / 0.895
   on pfc / fisher_kpp / allen_cahn. Unknown: whether a *learned* amplitude head
   beats 5-NN enough to convert round-1's oracle-scale result (0.2584, skill
   0.864) into a legal condition-only number.
4. **Does the withheld coarse solve carry the omitted driver, provably?** For the
   closest-in-condition train pairs, cos(block-mean HF difference, LF difference)
   = 0.997 / 0.969 / 0.998 / 0.985 (pfc / fisher / allen_cahn / helmholtz,
   fraction > 0.9 = 0.99-1.00). Unknown only in the sense that it has never been
   certified inside the round's harness — this is D3's "validatable rather than
   assumed" leg and it is what justifies r2s2/r2s3 existing.
5. **Does the pair estimator work at high condition dimension?** On
   `sharp__cahn_hilliard` (19 dims) the *minimum* standardized pair distance is
   2.82 — there are no near-neighbours, so the estimator has no support and the
   certificate must return `no_support`. Unknown: whether the 16 IC-Fourier dims
   make the map learnable in practice (the meta claims so: "IC-encoded cond ... so
   field=f(x) is learnable"), given the NN floor there is 0.969 ~ the zero floor.
6. **Overfitting / N_hf = 5.** Nothing is known yet about the train/test gap for a
   condition->HF decoder at 400 samples, and ifc_poisson at N_hf = 5 has no
   in-round precedent. r2s4's anatomy card will answer it; this batch must at
   minimum not peek (two disjoint folds) and must label ifc_poisson anecdote-grade.
