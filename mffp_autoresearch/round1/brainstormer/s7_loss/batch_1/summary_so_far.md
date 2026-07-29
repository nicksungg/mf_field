# Summary so far — Stream `s7_loss`, Batch 1

First batch of a stream created 2026-07-29 by ADR 0012. No within-stream prior
cards exist; everything numeric below comes from cross-stream cards, batch-0
certification, and this batch's websearch.

## 1. Websearch findings + prior-art verdict

Source: `websearches/s7_loss/batch_1/report.md` (5 iterations, cap hit; 15
WebSearch + 13 usable WebFetch).

The verdict table ranks five candidate directions. Verbatim rows that matter:

- **C-AMP** — gain/shape-decomposed objective — **`preempted-but-MF-composition-open`**:
  "Open: amplitude/shape-decomposed objective for **multi-fidelity PDE field
  regression scored on unchanged per-sample rel-L2**. No fetched source applies
  gain-invariant training to neural PDE surrogates. Design constraint: full
  scale-invariance is unscoreable under rel-L2 — use a two-term (shape +
  explicit gain) objective, not an invariant one."
  (cites `https://ar5iv.labs.arxiv.org/html/1406.2283`, `https://arxiv.org/abs/2507.18813`)
- **C-BAND** — low-k band-weighted objective — **`preempted-but-MF-composition-open`**:
  "Mechanism fully preempted — claim no new loss. Open: the **regime inversion**
  (all published band losses target high-k under-weighting; our M3 measures
  low-band-dominant excess with spurious high-k injection) and the **MF
  composition** (HF stage of an LF→HF fusion model, small N_hf)."
  (cites `https://arxiv.org/html/2607.19387`, `https://ar5iv.labs.arxiv.org/html/2012.12821`,
  `https://arxiv.org/html/2511.08753`, `https://arxiv.org/html/2602.19265v1`)
- **C-REL** — per-sample rel-L2 training loss — **`preempted`**: "Nothing novel;
  in-repo precedent already exists (`transolver_residual/smoke_eval.py:65-69`).
  Defensible ONLY as a controlled measurement of how much panel gap is
  loss/metric mismatch. Must never be written up as a contribution."
  (Verified first-hand: that file's `hybrid_loss` is `mse + mean(per-sample
  rel-L2)` with `clamp(min=1e-4)` on the denominator.)
- **C-STRUCT** — Sobolev/H1/gradient/SSIM — **`preempted`** and "additionally
  contraindicated by our own diagnostics (M3 low-band excess; M4 pfc error not
  interface-peaked)". This kills ADR 0012's *literal* "interface-aware" framing.
- **C-LFANCHOR** — likely degenerate: the champion is LF-blind at inference, so
  anchoring the low band to LF ≈ upweighting the low band against HF.

Three fetched failure modes of loss-only interventions (report item 4, from
`https://arxiv.org/html/2511.08753`, the closest methodological analogue —
loss-only, FNO, architecture fixed): (i) over-constraint / OOD collapse;
(ii) conflicting gradients between terms; (iii) a loss cannot repair an
architectural truncation limit. Mitigation precedent: gradient-norm balancing
(`https://arxiv.org/html/2502.02440v1`). Seven quarantined leads must not be
cited (report section "Unverified leads").

Threshold instruction (report item 7): helmholtz `min_claimable_effect` is
**9.695 skill** — the dataset that motivates C-AMP supports **no numeric claim**.

## 2. §12 conventions verbatim

`program.md §12.7 s7_loss (lever) — ADDED STREAM, see ADR 0012`:

> - **Question**: does an interface-aware training objective (scored on the
>   unchanged rel-L2 metric) fix sharp-2D fusion where architecture does not?
> - **Anchor**: champion's certified panel geomean (batch 0).
> - **Backlog ingested**: F14-F18 (docs/proposals/MODEL_TWEAKS*.md) —
>   loss/metric mismatch; rel-L2's blindness to thin sharp regions is the
>   repo's own documented metric caveat.
> - **Hard rule**: §2.1 is immutable — scoring never changes; only the training
>   objective does. Physics-agnostic losses only (ADR 0009): weights from the
>   field's own gradients/level sets.
> - **Pre-registered risk**: interface upweighting can lose on rel-L2 by
>   trading bulk accuracy; cards must state this trade-off in
>   expected_falsification.
> - ADR 0007 applies (propose 3-5 loss designs, screen at contract tier).

Anchor (`state/anchors/s5_tuning.json`, the same certified object the s3/s4/s5
streams anchor on; no `s7_loss.json` file exists): champion
`mf_fno_transfer_film`, panel geomean skill **6.703** [6.219, 7.102], per-seed
[7.102, 6.219, 6.788], `provisional: false`, `source: batch0`.

Noise floor (`state/noise_floor.json`, `min_claimable_effect`): allen_cahn
**1.633**, pfc **1.151**, cahn_hilliard **0.553**, fisher_kpp **0.418**,
ifc_poisson **0.240**, helmholtz **9.695 (no claim)**. Panel-geomean floor
**0.884** (derived; used by s5-B1 card part 5 and ADR 0011).

## 3. Within-stream prior cards

None — this is `s7_loss` batch 1 (`experiment_cards/` contains no `s7_loss/`
directory).

## 4. Cross-stream prior cards (the evidence this design stands on)

**`s2_beyond_copy-B1`** (`experiment_cards/s2_beyond_copy/batch_1/B1.json`,
part 5 `measurement_summary`, status `analyzing`) — the whole quantitative basis:

- **M1**: `lf_at_inference = FALSE` for `mf_fno_transfer_film` on 5/5 datasets x
  3/3 seeds; the only tensor entering the net at eval is the `[16, cond_dim]`
  condition vector. **The champion is an X-only predictor.**
- **M5a**: `amplitude_share_of_error` (= 1 − rescaled/raw nRMSE under one
  per-sample optimal scalar): helmholtz **0.865** (6.202 → 0.839), pfc
  **0.184–0.193** (`alpha_mean 0.73` — systematic under-prediction),
  cahn_hilliard **0.127–0.151** (`alpha_mean 0.76–0.78`), allen_cahn
  0.008–0.009, fisher_kpp 0.001–0.002.
- **M3**: `R_low > 1` on 5/5 datasets x 3/3 seeds; error energy concentrated in
  dyadic band 0 (`kr < k_nyq/8`, share 0.39–0.9996); the champion also **injects
  spurious high-k** that a k-NN lookup does not.
- **M4**: error nowhere interface-localized beyond ~1.3x area share; the
  pfc "interface-concentrated" prediction is FALSIFIED.
- **M2**: fisher_kpp is **information-bounded** (champion 4.179 sits AT the X-only
  floor; gap to best lookup 0.070 < the 0.418 floor) — no objective can fix it.
  pfc is **training-buys-nothing** (knn10 8.466 BEATS the champion 11.511 by
  3.045 > the 1.151 floor) — there is >=3.0 skill of headroom on pfc reachable
  without any new architecture. allen_cahn/cahn_hilliard are training-wins.
- **M5b**: LF<->HF pairing is sound; the data-defect branch is CLOSED.

**`s5_tuning-B1`** (`experiment_cards/s5_tuning/batch_1/B1.json`, `analyzing`) —
two things. (a) Result: modes_cap 12→32 moved the geomean by 0.507 < the 0.884
floor (provisional-single-seed) and its apparent win was 100% helmholtz — the
exact reporting trap this card must avoid. (b) The **substrate pattern** to copy:
a verbatim copy of `mf_fno_transfer_film` into `models_r1/<family>/`, the
`REPO_ROOT = HERE.parents[1] / "mf_field" / "factory_mffp"` relocation fix
(verified at `worktrees/s5_tuning/B1/models_r1/mf_fno_transfer_film_modes/smoke_eval.py:63`),
an env-gated single-line behavioural delta with default-equivalence proved at
contract tier, and RNG-neutral periodic checkpointing (same file, `_train`,
lines 130–178).

**`s3_testtime-B1`** (`retired_by_operator`) — its brainstormer measured the
champion's per-sample ||u|| spread on helmholtz at **408x** (0.070 → 28.46)
against a single global `scaler_hf = max|Y_hf_train| = 7.38`
(`brainstormer/s3_testtime/batch_1/summary_so_far.md:118`).

**Base-family fact verified first-hand**
(`mf_field/factory_mffp/models/mf_fno_transfer_film/smoke_eval.py`):
line 96 is `loss = F.mse_loss(pred, yb)` where `yb = Y / scaler` and
`scaler = max(|Y_train|)` (lines 83, 136–137) — **one global scalar per stage**.
That single line is simultaneously F19 (training loss != scored metric), the
408x-norm-span pathology, and the M5a amplitude mechanism.

## 5. Reopen candidates

None. All six existing batch-1 cards carry `reopen_candidate: false`
(`s1_poisson`, `s2_beyond_copy`, `s5_tuning` = `analyzing`; `s3_testtime` =
`retired_by_operator`; `s3_warp`, `s4_hybrid_routing` = `drafted`).

## 6. What is UNKNOWN

1. **Does the per-sample-normalization channel exist at all on the four
   claimable datasets?** The 408x ||u|| spread is measured on helmholtz ONLY.
   Under `mse(pred, y/scaler)` with a global scaler, samples with large ||y||
   dominate the gradient while rel-L2 weights every sample equally. If pfc /
   cahn_hilliard / allen_cahn / fisher_kpp have narrow norm spreads, this
   channel is inert there and the card nulls out for a boring reason. **Nobody
   has measured the per-sample HF-norm spread on those four datasets.** Cheap to
   log inside the family; must be logged.
2. **How much of the amplitude oracle a loss can actually capture.** M5a is an
   oracle (a per-sample scalar chosen with knowledge of the truth). Its headroom
   on the claimable datasets is pfc delta ~2.17 skill and cahn_hilliard ~0.77 — vs
   floors 1.151 and 0.553. A loss must capture >53% (pfc) / >72% (cahn_hilliard)
   of the oracle to be claimable on that channel alone. Unknown whether a
   training-time gain term converts at that rate — the model must *predict* the
   right per-sample gain from X, and M2 says X is 87–94% degenerate on
   cahn_hilliard/fisher_kpp.
3. **Whether the two channels interact or cancel.** Per-sample normalization
   (channel 1) and explicit gain calibration (channel 2) both change how
   amplitude is learned; the fetched failure mode (ii) is conflicting gradients
   between multi-term objectives. Unknown sign of the interaction.
4. **Whether inverting the published band-weight direction helps.** M3 shows
   low-band-dominant excess *and* spurious high-k injection. Down-weighting
   high-k could either suppress the spurious injection (good) or be the exact
   "over-constraint" failure mode (i). No fetched source tests the inverted
   regime.
5. **What the LF-pretrain stage contributes.** The objective could be applied to
   both stages or to the HF fine-tune only. With N_hf = 5 on ifc_poisson the LF
   stage carries almost all the amplitude prior. Unmeasured; a batch-2 ablation.
6. **Whether an objective change can move an X-only predictor at all.** M1 makes
   this stream's whole intervention a change to how a `cond_vec -> field`
   regressor is fitted. On fisher_kpp M2 proves it cannot (information floor).
   On pfc M2 proves >=3.045 of headroom is reachable by a *better estimator* of
   the same X->field map — a loss change is exactly such a change, so pfc is the
   one dataset where the mechanism and the headroom coincide.
7. **Guard-set behaviour.** No guard-set measurement exists for any objective
   change; `sharp__sod_1d` is 1-D and shock-dominated, where per-sample
   normalization could plausibly crater.
