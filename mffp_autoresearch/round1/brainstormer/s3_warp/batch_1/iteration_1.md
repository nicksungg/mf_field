# Iteration 1 — Stream `s3_warp`, Batch 1

## Design context considered

- `summary_so_far.md` §6 (unknowns 1-9), §1 (prior-art verdict), §2 (program.md
  §12.3 verbatim), §4 (the s2_beyond_copy-B1 measurements).
- The immutables block (§4.5 of my spec / program.md §5), quoted in full in the
  self-check below.
- Anchor: no `state/anchors/s3_warp.json`; the batch-0 certification the §12.3
  anchor line points at is `state/anchors/s3_testtime.json` —
  `mf_fno_transfer_film`, panel geomean skill 6.703 (per-seed 7.102/6.219/6.788).
  This card makes **no anchor-referenced claim** (it never runs the champion),
  so the missing file is not blocking; I flag it for the maintainer.
- `state/noise_floor.json`: `min_claimable_effect` helmholtz 9.695, allen_cahn
  1.633, pfc 1.151, cahn_hilliard 0.553, fisher_kpp 0.418, ifc_poisson 0.240;
  `spread` 9.695 / 0.0141 / 0.0826 / 0.192 / 0.0918 / 0.240 respectively.
- Pre-falsified levers (program.md §5): WNO backbone swap; LF low-mode freezing
  (`mf_fno_spectral`); diffusion prior for point accuracy.
- ADRs in force: 0004 (strict single seed), 0005 (H100), 0007 (propose-many —
  **exempt**: "Diagnostics and spec-pre-directed slots are exempt (no candidate
  pool)"), 0009 (no known physics at test time), 0010 (this stream).

## Proposal reasoning

### Step 1 — diagnostic or model?

The websearcher's own conclusion is that D2 gates D1, and I agree, for four
independent reasons that I checked rather than inherited:

1. **The premise is unmeasured and the source that would settle it failed to
   fetch.** Unknown 1. A warp corrects *position*; the competing regime
   (interfacial thickness) is untouchable by any diffeomorphism. The
   websearch's only evidence for the two-regime split is a 403'd MDPI page
   (snippet-level, explicitly declared non-citation-grade). Building a
   200-epoch model on an unverified premise, when the premise is measurable
   training-free in minutes, inverts the round's own cheap-diagnostics-first
   principle (program.md §4.3).
2. **The s2 forensics do not settle it and can be misread as settling it
   against us.** M4 shows the *champion's* excess error is mid-distance on pfc
   and far-field on cahn_hilliard — the naive "error lives at interfaces"
   premise is false for the champion. But the champion is **LF-blind** (M1):
   its error is an X-only regression error and has nothing to do with the
   LF->HF discrepancy a warp acts on. The correct rows are copy-LF's:
   allen_cahn `[2.049, 0.814, 0.560, 0.552]` is strongly interface-tilted, pfc
   `[1.276, 1.811, 0.840, 0.105]` near+mid, while cahn_hilliard and helmholtz
   are far-field. So the premise is *dataset-dependent and partially
   supported* — exactly the state in which a measurement, not a model, is the
   right next move. A model card would have to pick datasets to bet on with no
   basis for the pick.
3. **A model card cannot be sized without a ceiling.** Unknown 3/4. If the
   oracle ceiling is 6%, a D1 model failing to beat the anchor teaches nothing
   (it was never possible); if the ceiling is 60%, the same failure indicts the
   displacement head. One number changes the interpretation of every future
   card in this stream.
4. **Novelty is best served here.** The D2 verdict says: *"no fetched source
   applies it between two fidelities of one PDE solve, and none reports an
   oracle-warp upper bound on MF fusion error"* — whereas D1's claimable
   novelty was explicitly narrowed to a "*neural, cross-fidelity, field-level*
   instantiation". The cheapest defensible claim in this stream is the
   measurement.

Counter-argument I weighed and rejected: *round 1 needs models, not
measurements; s2 already spent a batch on a diagnostic.* Rejected because (a)
the two diagnostics measure disjoint objects (s2 measured the champion's error;
this measures the LF->HF discrepancy), (b) the s2 diagnostic cost 0.77 min of
H100 and produced the single most decision-relevant fact in the round so far
(M1 LF-blindness), and (c) this card's cost is comparable, so the batch budget
lost is minutes, not a slot's worth of compute.

### Step 2 — what makes an oracle measurement non-trivial?

A naive "fit the best warp" measurement is worthless: a free-form per-pixel
displacement can transport values essentially arbitrarily and would report a
near-100% ceiling on every dataset. The measurement is only informative as a
**ladder in warp degrees of freedom**, with the rung a learned low-mode head
could plausibly reach called out in advance. So the primary quantity is
`skill_oracle(rung)` = nRMSE(warped LF) / nRMSE(copy-LF) as a function of
control-grid resolution, with rung 0 (displacement identically zero) equal to
copy-LF *by construction*.

That has a second payoff: **rung 0 is the warp-off control**, structurally,
and it doubles as the seam check against `eval/copylf_baselines.json`. The
websearcher's mandatory warp-off-control point (its note 3, the orchestrator's
point (c)) is thus satisfied inside the diagnostic, and the card can
pre-register the architecture-level version (displacement forced to zero) as a
requirement on any future D1 model card.

Alternatives weighed for the fitter:

- **skimage `optical_flow_tvl1` / `optical_flow_ilk`** (available: skimage
  0.26.0, verified importable in `.venv`). Rejected as the primary fitter: it
  has no explicit DOF axis (the pyramid is an estimation strategy, not a
  parameterisation — the websearch's own dead-end note makes this point), and
  its brightness-constancy objective is not the L2 objective the round scores.
- **Direct per-sample optimisation of a control-grid displacement with
  `torch.nn.functional.grid_sample`** (torch 2.6.0+cu124 verified). Chosen:
  exact DOF control, GPU-batched over all samples at once, and — decisively —
  it is the *same warp primitive* D1 would use (STN-style bilinear sampling at
  `x + phi(x)`, as in Flowers arXiv:2603.04430), so the ceiling it reports is a
  true ceiling for the D1 architecture class rather than for a different
  operator.
- Optical flow is retained as a **cross-check** on one rung (it costs
  seconds and guards against the Adam fit being the bottleneck).

Optimiser-validity risk (the fit could underestimate the ceiling and we would
mistake optimiser failure for absence of a warp regime). Mitigations, all
pre-registered as hard-stops: coarse-to-fine initialisation (each rung
initialised from the upsampled previous rung), monotone loss assertion across
rungs, and a **synthetic self-test** — take HF, apply a known smooth random
displacement to make a pseudo-LF, and require the fitter to recover it to
< 0.25 cells endpoint error and drive nRMSE below 5% of unwarped. Failure
aborts the run rather than reporting a small ceiling.

### Step 3 — which datasets

The five beyond-copy panel datasets. `ifc_poisson` is excluded: its test split
ships only the HF fidelity, so copy-LF is undefined there and there is no LF
field to warp (ADR 0002; `eval/copylf_baselines.json` `_notes.ifc_poisson`
states exactly this and sets `reference_type: paper_bar`). `ext__helmholtz_2d`
is included **as the built-in negative control** and is report-only: its
copy-LF error is far-field (`[0.070, 0.248, 0.717, 3.011]`) and 69% amplitude
(`amplitude_share_of_error` 0.691), it is oscillatory rather than
interface-dominated, and its noise floor (9.695) is 70% of its own anchor. A
mechanism claim there is unavailable and unwanted; a *near-zero* warp benefit
there is a positive validity signal for the measurement.

### Step 4 — the floor problem, resolved explicitly

`min_claimable_effect = max(seed_spread, 0.1 x anchor mean skill)` (verified
against all six entries). It is an **anchor-referenced** convention: it asks
whether a trained model differs from a champion at skill 4-16. This card's
effects are **copy-LF-referenced** and therefore live in [0, 1] skill units by
construction. Consequences I state rather than hide:

- On `sharp__cahn_hilliard` (0.553) and `sharp__fisher_kpp_2d` (0.418) a
  copy-LF-referenced effect *can* clear `min_claimable_effect`, and my
  threshold is chosen so that it does.
- On `sharp__allen_cahn_2d` (1.633) and `sharp__phase_field_crystal_2d`
  (1.151) **no** copy-LF-referenced effect of any size can clear it, because
  the entire available range is 1.0. This is a structural property of the
  convention, not of my design (round-1 success criterion 2, "skill < 1", has
  the same property). For those two datasets the applicable noise term is the
  certified `spread` (0.0141 and 0.0826), which my threshold clears by 40x and
  6.8x, plus the card's own measured optimiser-restart spread.
- Relative reading: the 10%-of-anchor construction behind
  `min_claimable_effect` corresponds to a 10% relative effect; my threshold is
  a 56% relative error reduction, 5.6x that, on every dataset.

Threshold chosen: `skill_oracle <= 0.44` at the learnable rung (i.e. >= 56% of
copy-LF's error removed). Effect = 0.56 skill units > 0.553 (cahn_hilliard)
and > 0.418 (fisher_kpp); vs `spread`: 40x (allen_cahn), 6.8x (pfc), 2.9x
(cahn_hilliard), 6.1x (fisher_kpp).

### Step 5 — what else must be in the same run (each cheap, all sharing one fit)

- **Regime split** (unknown 1/2): distribution of `|phi|` in grid cells, overall
  and restricted to near-interface pixels, using s2's *identical* interface
  rule (`tau = 0.1` on `|u|/max|u|` with top-decile `|grad u|` fallback and
  pooled-quartile distance strata) so the two cards' sidecars are directly
  comparable.
- **Keil & Craig 2009-style decomposition** (the published displacement /
  amplitude split, adopted by citation): partition copy-LF's squared error into
  DIS (removed by the warp), AMP (further removed by a post-warp per-sample
  optimal scalar rescale — same alpha construction as s2 M5a), RES (remainder =
  the thickness/topology term a warp provably cannot reach).
- **Thickness probe**: interface-band gradient-energy ratio
  `||grad HF|| / ||grad(warped LF)||` before and after warping. A warp is
  volume-preserving in value space, so a persistent ratio > 1 after warping is
  direct evidence of the un-warpable thickness regime.
- **Topology** (§12.3 requirement): connected-component counts of the phase
  indicator for LF vs HF per sample; report `mean |Delta N|` and the fraction
  of samples with `Delta N != 0`. This tells a future D1 card which datasets
  need the metamorphosis-style appearance term (MetaRegNet arXiv:2303.09088)
  and which are safely diffeomorphic.
- **s2 tie-ins**: warp benefit by interface-distance stratum (does the benefit
  live where copy-LF's error lives?) and by dyadic spectral band with s2's
  identical band edges (is s2's M3 low-band excess displacement-explainable, or
  is band-0 dominance just the 0.96-0.9998 HF energy share?).
- **Learnability bracket**: transfer the displacement fitted for a *train*
  sample to a *test* sample chosen by nearest neighbour (a) in LF-field space
  and (b) in condition space. Neither uses test-split HF, so both are honest
  predictors; they bound from below what a retrieval-grade predictor achieves.
  Stated confound: a learned field-conditioned head can exceed retrieval, so a
  low transfer number does **not** falsify D1 — it is reported, not a leg.

### Step 6 — the scored split

The contract requires `splits.test*.nRMSE`. s2's precedent (`ref_*` split keys
are ignored by `score_panel._extract_test_metric`) lets me choose what is
scored. I score the **NN-in-LF-field displacement transfer** — the strongest
predictor in this card that never touches test-split HF — and put copy-LF,
every oracle rung, and the NN-in-X transfer under `ref_*` keys plus sidecars.
The oracle rungs are HF-fitted upper bounds and must never be scored. I
pre-register `do_not_promote: true` in the card (s2 had to have this added by
the reviewer after the fact): the scored entry is a training-free nonparametric
transfer, not a model, and is ineligible for the leaderboard, anchors, and
top-3 confirmation.

### Step 7 — ADR compliance

ADR 0009 constrains *models* ("no candidate MODEL may require the governing
equations at test time") and explicitly permits "diagnostics / upper-bound
measurements". This card uses no governing equations at all — it is fields-only
— and the HF target it consults is used exclusively for the oracle upper bound,
never in a scored predictor. ADR 0007 propose-many is explicitly exempt for
diagnostics; one design, no candidate pool. ADR 0004: seeds `[0]`, and the
measurement is deterministic anyway (fixed init, fixed iteration count,
`CUBLAS_WORKSPACE_CONFIG` set by `score_panel`).

## Proposal

- **Category**: `diagnostic / warp-opportunity oracle (displacement-vs-thickness
  decomposition of the LF->HF discrepancy)`
- **Card type**: `diagnostic`
- **Motivation**: gates D1 per the websearcher's own verdict (quoted verbatim
  in the report); measures unknowns 1-5, 8 and confronts s2's M1/M3/M4.
- **Concrete config**: new contract family `models_r1/s3_warp_oracle/`
  (`manifest.json` with `"diagnostic": true`, `smoke_eval.py`, `INSPIRATION.md`,
  helper modules), run by `eval/score_panel.py` at `--epochs 0 --seed 0` over
  the five beyond-copy datasets. Measurements M0-M9 as in Steps 2/5/6.
  Warp = `torch.nn.functional.grid_sample(LF_up, grid + phi)`, `phi` a bilinear
  control-grid field at `C x C` control points, `C in {0, 4, 8, 16, 32, full}`
  (rung `0` = zero displacement = copy-LF, asserted equal to
  `eval/copylf_baselines.json` to <= 1e-9), coarse-to-fine, Adam, Laplacian
  smoothness penalty, `|phi|` clamped to 16 cells. Learnable rung = `C = 16`.
- **Recipe**: see the report (complete JSON).
- **Expected outcome**: see the report.
- **Expected falsification**: see the report (legs A-D).
- **Anchor reference**: `null` (lever stream, program.md §4.5; the card makes
  no anchor-referenced claim and never runs the champion).

## Status

- Slot covered: yes (1 proposal, `diagnostic`).
- Skipped: no.
- Reopen candidates resolved: none exist (all five extant cards carry
  `reopen_candidate: false`).
- Immutables self-check: **pass (10/10)** — recorded below.

## Immutables self-check (10 items, positive evidence)

1. **Data read-only.** The family only *reads* through
   `round1/eval/panel_data.py::load_split` / `copylf_prediction`, which wrap
   the factory adapter; it writes nothing under `factory_root/data/**` or
   `benchmark_42/**`; no regeneration, no extra HF, N_hf untouched (400 train /
   100 test as recorded in s2's part 5); LF is consumed exactly as the round's
   copy-LF definition produces it (real coarse solve, bilinearly interpolated),
   never a downsampled HF. The one synthetic field in the card (the self-test
   pseudo-LF) lives in memory, is never written to any dataset directory, and
   is never scored.
2. **Panel + guard set fixed.** Datasets are a strict subset of the frozen
   panel (5 of the 6 `project.yaml panel:` entries); nothing is added,
   substituted, or reordered; the `ifc_poisson` omission is a *coverage*
   choice justified by ADR 0002 (no LF in its test split) and recorded in the
   card, not a redefinition of the panel. No guard-set run is needed (the card
   claims no panel win).
3. **Eval layer / spec untouched.** Every number is produced by invoking
   `eval/score_panel.py` unmodified with `--family_dir` pointing into the
   worktree, and every nRMSE inside the family is computed by importing
   `eval/nrmse.py` (whose `NRMSE_DEF_HASH` is recorded in each sidecar). No
   file under `round1/eval/`, `project.yaml`, `program.md`, `docs/adr/`, or
   `subagents/` is edited; the `s2_copylf_forensics` family is the working
   precedent that this is achievable.
4. **One nRMSE definition.** The scored value is whatever
   `score_panel._extract_test_metric` reads from `splits.test_hf` (per-sample
   rel-L2 mean), and the sidecar nRMSEs are computed by calling `eval/nrmse.py`
   directly, so `nrmse_def_hash` is identical
   (`d3d0ade9191c13bacc40702f3eb26ad290e01641cacee22a1d2233b74c035850`, matching
   s2's recorded hash). The fitting objective (masked L2 + Laplacian penalty) is
   a *training* objective, which program.md §5 leaves free, and is never
   reported as a score.
5. **Contract CLI fixed.** `smoke_eval.py` takes exactly
   `--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed` and writes
   `{model, dataset, splits}`; all eleven knobs are passed as
   `score_panel --env KEY=VAL`, all eleven are listed in `recipe.env`, and they
   therefore enter `code_hash` (`score_panel.code_hash` folds sorted env pairs
   into the sha).
6. **Seeds / epochs fixed.** `seeds: [0]` per ADR 0004 strict-single-seed;
   `epochs: 0`, which SCHEMA.md declares legal for diagnostics ("`recipe.epochs
   = 0` is legal") and which s2-B1 already ran through `score_panel` on H100.
   No tier budget is altered; nothing trains, so no epoch budget is consumed.
7. **Guarded factory surfaces untouched.** All new code lives at
   `worktrees/s3_warp/B1/models_r1/s3_warp_oracle/`; the card touches
   `factory_root/{eval,baselines,references,scripts,data}/`, `factory.md`, and
   `mf_field/akash/**` only through read-only imports of
   `data_adapters/loaders.py` performed *by the eval layer*, and outputs are
   redirected to `${OUTPUTS_ROOT}/s3_warp/B1/eval` via `ROUND1_EVAL_RESULTS`
   (the S1 reviewer suggestion honoured on s2-B1).
8. **Checkpoint-resume implementable.** The family writes
   `<ckpt_dir>/last.pt` after each dataset's fit completes, containing the
   fitted displacement coefficient tensors and the finished measurement dict,
   and on start it loads `last.pt` and short-circuits any completed
   (dataset, rung) pair — the identical pattern `s2_copylf_forensics` uses
   ("Re-running after preemption is safe: `<ckpt_dir>/last.pt` stores the
   finished result and short-circuits a completed dataset"). Per-rung
   granularity means a preemption costs at most one rung.
9. **Falsification threshold vs the noise floor.** Leg A's effect is 0.56
   skill units (copy-LF skill 1.0 -> threshold 0.44). Certified
   `min_claimable_effect`: cahn_hilliard **0.553** (0.56 > 0.553, clears),
   fisher_kpp **0.418** (0.56 > 0.418, clears), allen_cahn **1.633** and pfc
   **1.151** (unclearable by *any* copy-LF-referenced effect since the range is
   1.0 — see Step 4; the applicable term there is the certified `spread`
   **0.0141** and **0.0826**, cleared by 40x and 6.8x). helmholtz
   (`min_claimable_effect` **9.695**) is report-only, no leg, no claim. Legs
   B/C are geometric counts with no seed dimension; leg B's threshold (0.5
   cells) is 2x the pre-registered self-test measurement floor (0.25 cells).
10. **Not a pre-falsified lever.** Nearest is **LF low-mode freezing**
    (`mf_fno_spectral`, "worst on sharp, catastrophic on lid-cavity"). The
    difference: that lever *froze LF's low Fourier modes in the value field*,
    forbidding the model from correcting them; this card applies a low-mode
    constraint to a **displacement field** (a coordinate map), leaves the value
    field entirely free, and trains nothing — no value-space mode is frozen,
    and no model is proposed at all. WNO backbone swap and the diffusion prior
    are unrelated (no backbone change, no generative prior).
