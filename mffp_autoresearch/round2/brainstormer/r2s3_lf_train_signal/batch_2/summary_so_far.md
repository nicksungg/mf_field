# Summary so far — Stream `r2s3_lf_train_signal`, Batch 2

All content below is read from files (paths cited); nothing is recalled.

## 1. Websearch findings + prior-art verdict (batch 2)

Source: `websearches/r2s3_lf_train_signal/batch_2/report.md` (5 iterations, cap
hit; 14 WebSearch / 12 WebFetch, 9 usable fetches).

The verdict table scores six candidate directions distilled from B1's part 7:

- **E1** — ship the linear/affine LF channel `c*A(cond) + R(cond)` as the B2
  family: **preempted**. "LR-MFS: LF prediction as basis + polynomial
  discrepancy, one least-squares fit, motivated by few affordable HF runs"
  (https://arxiv.org/abs/1705.02956, fetched) and, decisively,
  "projection-based MF **linear** regression for **data-scarce** apps,
  **POD-projected field outputs**, additive-KO / direct-augmentation /
  regression-mapping variants" (https://arxiv.org/pdf/2508.08517, fetched).
  Open: "Nothing at the mechanism level... Ship it as a **cited baseline**,
  never as a contribution."
- **E2** — LF rows at **disjoint** conditions supply the null direction of the
  5x6 HF design: **preempted-but-MF-composition-open**
  (https://arxiv.org/html/2510.15337 retain-plus-transfer, source information
  "only into the null space" of the target design;
  https://arxiv.org/pdf/2508.08517 "LF data can be evaluated at parameter
  values where no HF data exists"; https://arxiv.org/abs/2511.20183 non-nested
  MF-GP). Left open: "The **field-valued, neural, certified-floor** instance...
  priced in skill units against a 3-seed `min_claimable_effect`, on a panel
  where 5/6 datasets have **condition-aligned** rungs. **Supersedes batch 1's
  `novel` verdict for D3.**"
- **E3a** per-rung scaler — "novel but weak; against convention"; **E3b**
  Nyquist-pinned mode clipping — **preempted** by MG-TFNO's "the first alpha modes
  in each direction, where alpha is independent of the discretization"
  (https://arxiv.org/html/2310.00120, fetched): "Bug fix."
- **E3c** null-direction gain calibration — **preempted-but-MF-composition-open**
  (https://arxiv.org/html/2510.01608 NPN; deep null-space learning family);
  what is open is "The **measurement**, not the fix: a FiLM-FNO placing 27.7%
  of its implicit law energy in the unconstrained direction **anti-aligned**
  (cos -0.99) contradicts the min-norm implicit-bias prediction."
- **E4** training-free per-dataset gate — **preempted**
  (https://arxiv.org/abs/2403.08118): "Mandatory engineering; not a claim."
- **E5** — "the **measurement**: matched, budget-equal with/without-LF-training
  contrast for a **neural condition->field** surrogate at N_hf ~ 5 (and N = 400
  with condition-aligned rungs), per dataset, against a certified 3-seed noise
  floor": **novel** (nearest neighbours named). "three independent search
  framings ... failed to retrieve a matched-architecture with/without-LF
  accounting for neural field surrogates at this sample count. This is round-2
  success criterion 1 and the stream's remaining publishable content."

Binding instructions to me (report "## For the brainstormer"): card E1 as a
cited baseline only; do not repeat batch 1's D3 `novel` claim; per-dataset,
per-mechanism falsification clauses ("B1's part 7 warns that a single
panel-geomean threshold is what let B1's F3 flip"); helmholtz report-only; pfc
band-limited caveat; ifc_poisson criterion-2 claims are rank recovery.

## 2. §12.3 conventions verbatim (program.md)

> ### 12.3 `r2s3_lf_train_signal` (lever)
>
> - **Question**: LF as training-only signal. Candidate mechanisms (spec §6):
>   distillation from an LF-consuming teacher (round-1 families in role §5.10b
>   — teacher at train, absent at test), LF-pretrain → HF-finetune, auxiliary
>   multi-fidelity losses (predict LF and HF jointly from condition).
> - **The stream has a mandatory declared baseline**: `mf_fno_transfer_film`
>   (factory zoo champion) IS LF-pretrain→HF-finetune from the condition
>   vector (verified 2026-07-31: its test input is `cond_by_fid` only; it runs
>   on the stripped view unmodified). Any r2s3 pretrain/finetune proposal must
>   either score it as the baseline arm or cite how it differs — an
>   undifferentiated re-proposal is a rebadge (reviewer FAIL, §5.10).
> - **revin_lf two-scaler finding** (r1 s5): exact at LF-pretrain, 3.1% proxy
>   at HF — normalization transfer across fidelities is a solved sub-problem;
>   reuse it, don't rediscover it.
> - **Nested-ladder degeneracy** (r1 report §6) directly constrains this
>   stream: with aligned/nested ladders, "multi-fidelity" training pairs
>   degenerate toward top-rung replication — LF-as-signal designs must state
>   what information the LF rungs add that the HF rung does not already
>   contain (spectral truncation structure, more samples at low rungs on
>   ifc_poisson: 70 lower-fidelity vs 5 HF).
> - The **unified normalization eligibility rule** (r1 s2, checks 0–6) governs
>   any per-sample normalization proposal; spread is not the decider.
> - Uses the existing 400 aligned samples only (§5.11).

Common §12 preamble, verbatim: "quote the launch anchor (best-floor geomean
23.06) and the per-dataset floor table verbatim when designing; thresholds
must clear the noise floor for the dataset(s) — while `state/noise_floor.json`
is provisional, judge falsification clauses directly (§4.3); cite the
websearcher's prior-art verdict; every proposal carries a complete `recipe`
block; floor arms mandatory on model cards (§2.2)." (The provisional clause is
now moot: `state/noise_floor.json` carries `_provisional: false`.)

Stream anchor (`state/anchors/r2s3_lf_train_signal.json`): value **23.063617**,
`anchor_type: best_floor_panel_geomean`, per dataset — ifc_poisson 10.054891
(nn_condition), sharp__cahn_hilliard 23.180342 (nn_condition),
sharp__fisher_kpp_2d 11.993111 (train_mean), ext__helmholtz_2d 3.344110
(zero), pfc 59.811754 (train_mean), allen_cahn 269.195876 (nn_condition).

Certified noise floor (`state/noise_floor.json`, `_provisional: false`, source
r2s4_diag-B1 3 seeds of `r2s4_cert_min`): `min_claimable_effect` — panel
1.1418668, ifc_poisson **0.9377041**, sharp__cahn_hilliard **0.0912454**,
sharp__fisher_kpp_2d **0.0007137**, ext__helmholtz_2d 2.9529916, pfc
0.2130273, allen_cahn 0.8797047.

## 3. Within-stream prior cards

`experiment_cards/r2s3_lf_train_signal/batch_1/B1.json` (`complete`,
`cratered`, F1 falsified; `reopen_candidate: false`). Family
`r2s3_rung_supervised`; arms `hf_only` / `rung_native` (primary) /
`rung_upsampled`; single job 77.05 min on h200 (`state/timing_ledger.json`).

Part 5 (numbers quoted from the card): panel geomean `rung_native` 25.3919 vs
`hf_only` 26.8687 vs anchor 23.0636 — the primary arm is **resolvably worse
than the training-free anchor**. ifc_poisson: `rung_native` skill 16.7963 vs
`hf_only` 9.4466 → value-of-LF **-7.3497** (an inversion, 7.8x the certified
0.9377 floor). `rung_upsampled` diverged on ifc (647.51). Floor arms:
`rung_native` beats the best frozen floor on 2/6 (allen_cahn, cahn_hilliard);
`hf_only` on 3/6.

Part 6 (mechanism, 3 turns): ifc_poisson is **exactly affine** in its 5-dim
condition (exact-LOO 3.2e-08 at every rung and on the 128 test rows), unique
on the panel (others 0.25–2.56). The 5 HF rows' design `[X_hf,1]` (5x6) has
**one null direction carrying 18.83% of the law's coefficient energy**; the
min-norm HF-only fit scores **3.4744** — an information limit for *any*
capacity. LF rungs recover that direction (null-direction recovery 0.940 /
0.982 / 0.996 for rungs 8/16/32). Architecture-free value of LF: rung-32
affine + 5-row residual ridge → **0.2427** (below the paper bar). The shipped
network delivered -7.3497 instead; identified defects: the shared `max|y|`
scaler (42.1x rung amplitude spread → **1772x HF-loss deflation**), an
unsupervised `|k|>4` band (post-hoc low-pass with a train-selected cutoff
recovers +1.605), and a null-direction gain **2.653x too large** (cos +0.8497)
while the no-LF control puts **27.7% of its law energy anti-aligned**
(cos -0.9919) in that same direction. Architecture tax at matched information:
**2.72x** without LF (3.4744 → 9.4441) and **60x** with LF (0.2427 → 14.6254).

Part 7 next_direction: ship the linear channel (E1 — now preempted), or, if
the network route is taken, **all three repairs together** (per-rung scaler,
HF-Nyquist-pinned clipping, explicit null-direction gain calibration), scored
against 0.2427 rather than 16.7963; mandatory per-dataset gate because the
affine channel is ifc-specific; per-dataset, per-mechanism falsification
clauses; dump train-condition predictions; reuse `tools/affine_ladder_voi.py`
and `tools/posthoc_repair_ladder.py` (both promoted).

Two reviewer confounds recorded on B1's deciding measurement: **C1** shared
scaler not normalization-matched between arms, **C2** epoch-matched not
step-matched.

## 4. Cross-stream cards (light scan, part-7 references to this stream)

- `r2s4_diag/batch_2/B2.json` (`drafted`, in build, 3 seeds) — the **sibling
  measurement** and the turf boundary. Arms `T0_cond_only` / `T1_lf_aux`
  (aux LF head, separate LF scaler) / `I1_lf_teacher` / `I2_lf_ablated`;
  full-N panel contrast plus `N_FIT_LEVELS = 20,80` (+320 full) on the five
  N=400 datasets; LF is the finest train rung **paired to the fit rows**. It
  predicts ifc_poisson as "the one predicted claimable full-N effect, sign
  NEGATIVE, magnitude 0.5-5 vs floor 0.93770". It never reaches N_hf = 5 on
  the sharp datasets and never uses LF at conditions where HF is absent.
- `r2s4_diag/batch_1/B1.json` (`complete`) — certified `state/noise_floor.json`
  (family `r2s4_cert_min`, 3 seeds, smoke tier) and `state/anchors/floors.json`.
- `r2s1_direct/batch_2/B2.json` (`drafted`) — a ~10^2-parameter closed-form
  head vs a 10^7-parameter decoder; B1's part 7 cross-stream note attributes
  that capacity tie to the same null-direction geometry measured here.
- `r2s2_stacked/batch_1/B1.json` (`analyzing`) — independent confirmation that
  ifc_poisson's LF side is a closed-form affine map (ridge(cond) held-out
  nRMSE 0.0000; emulator output effective rank 1.02).

## 5. Reopen candidates

None. All six round-2 cards carry `reopen_candidate: false` (verified by
reading every `experiment_cards/*/*/B*.json`); no skipped slots exist in this
stream.

## 6. What is UNKNOWN

1. **Does the repaired network convert LF-at-uncovered-conditions into skill,
   or is the architecture tax irreducible?** B1 measured both endpoints —
   information +3.2317 skill units (linear estimator) vs delivery -7.3497
   (network) — and diagnosed three separately-priced defects, but *never ran
   the repaired network*. Post-hoc repairs recovered at most 1.605 of the
   7.3497 inversion; the remaining ~5.7 units are attributed to the shared
   scaler's damage to the **row-space** law (0.921 vs the control's 0.604),
   which post-hoc surgery cannot undo. Nobody knows whether retraining with
   per-rung scalers repairs the row space. This is the single question the
   stream can still answer with a training run.
2. **Is the value-of-LF sign at N_hf ~ 5 a property of ifc_poisson or of the
   regime?** ifc_poisson is the panel's only natively-N_hf=5 dataset and its
   only affine one. The five sharp/helmholtz datasets have 400 **aligned** HF
   and LF rows, so at full N the LF rungs add only spectral truncation
   (nested-ladder degeneracy) — which is why B1's F3 found no coherent effect
   there. **Nobody has constructed the intermediate regime**: HF restricted to
   5 rows while the LF rungs keep all 400 conditions, i.e. LF at 395
   conditions where no HF exists. That regime is constructible from the
   existing files (verified: `stripped_data/sharp__cahn_hilliard/train_l{1,2,3}.npz`
   each carry `x (400,19)`, `y` at 4096 / 16384 / 65536; fisher_kpp the same
   with `x (400,2)`), needs no new data, and is exactly E2's open surface.
3. **Coverage vs curriculum.** On aligned datasets one can supply LF *only at
   the same 5 conditions as the HF rows* (pure resolution curriculum, zero
   parameter coverage) or *at the other 395* (pure coverage). No card has ever
   separated these two channels; §12.3 demands exactly this statement ("what
   information the LF rungs add that the HF rung does not already contain").
   On ifc_poisson the paired version is not even constructible (rungs are at
   pairwise disjoint conditions — exact overlap 0, B1 part 5 instrumentation;
   re-verified here: train fidelity_8/16/32/64 carry 100/50/20/5 rows).
4. **Does the null-direction deficit predict where LF pays?** The deficit is
   computable training-free: `m = (d+1) - rank([X_hf,1])`. At N_hf = 5 it is
   1 on ifc_poisson (d = 5), **15 on cahn_hilliard (d = 19)** and **0 on
   fisher_kpp (d = 2)** — a pre-registerable structural ordering (cond_dims
   read from `state/anchors/floors.json`). Nothing in the round has tested
   whether it predicts the sign or size of a *neural* arm's LF effect.
5. **Are the certified thresholds regime-valid?** `state/noise_floor.json`'s
   ifc_poisson mce 0.9377 was certified by `r2s4_cert_min` trained on the same
   5 HF rows — regime-matched. The cahn_hilliard 0.0912 and fisher_kpp 0.0007
   constants were certified at N = 400; at N_hf = 5 the seed/subsample spread
   is unknown and probably larger, so any sharp-dataset claim needs an in-job
   paired spread (drift-class rule, §12.4).
6. **Are the frozen floors the right bar at N_hf = 5?** `state/anchors/floors.json`
   computes `nn_condition` and `train_mean` from the **full 400-row** train
   split (`n_train_hf: 400` recorded per dataset). A 5-row model losing to a
   400-row NN floor is not evidence it learned nothing; the honest in-regime
   floors (NN / mean over the same 5 rows, plus the standing zero column) have
   never been computed on this panel.
7. **Unresolved by design in this stream**: whether any of this transfers to
   the three stochastic-map datasets (pfc, fisher_kpp, allen_cahn — ADR
   r2-0003: the realized IC is absent from the condition), where a
   deterministic condition→HF model is bounded by the conditional mean and LF
   at *other* conditions cannot supply a test sample's IC.
