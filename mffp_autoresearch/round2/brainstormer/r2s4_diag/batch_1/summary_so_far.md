# Summary so far — Stream `r2s4_diag`, Batch 1

Sources read (paths relative to `mffp_autoresearch/round2/` unless absolute):
`websearches/r2s4_diag/batch_1/report.md`, `websearches/r2s1_direct/batch_1/report.md`
(cross-stream, prior-art only), `program.md` §1–§5, §12.4, §13,
`project.yaml`, `state/anchors/{r2s4_diag,floors}.json`, `state/noise_floor.json`,
`state/gates.md`, `state/timing_ledger.json`, `docs/adr/0003-condition-vector-incompleteness.md`,
`experiment_cards/SCHEMA.md`, `eval/score_panel.py`,
`../round1/experiment_cards/s2_beyond_copy/batch_1/B1.json` (diagnostic-card precedent),
`mf_field/factory_mffp/data_adapters/{loaders,metrics,geometry}.py`.

## 1. Websearch findings + prior-art verdict

`websearches/r2s4_diag/batch_1/report.md` ran 5 iterations (cap), 15 searches,
14 successful fetches. Verdict rows verbatim:

- **D1a** — certify a minimum-claimable-effect from a 3-seed condition→HF spread
  (replaces provisional `noise_floor.json`) — verdict **`preempted (cite)`**;
  citations Agarwal et al. *Deep RL at the Edge of the Statistical Precipice*
  (https://ar5iv.labs.arxiv.org/html/2108.13264), Du *When +1% Is Not Enough*
  (https://arxiv.org/abs/2511.19794). "Nothing methodological. Open item is the
  **empirical constant** for this panel/regime. Adopt IQM + stratified/paired BCa
  bootstrap CIs + per-seed deltas instead of a bare max−min spread; expect 3 seeds
  to license only LARGE effects."
- **D1b** — training-free floor panel (NN-in-condition / train-mean / zero) as
  mandatory reported arms — **`preempted-but-MF-composition-open (cite)`**;
  McGreivy & Hakim (https://arxiv.org/abs/2407.07218, 79% weak baselines),
  *Predictivity and Utility…* (https://arxiv.org/html/2604.20061v1),
  Westermann et al. (https://arxiv.org/abs/2604.00689), Operator Boosting
  (https://arxiv.org/abs/2606.17460). "All published floors are **fitted** (ROM,
  polynomial, GP, kriging)… no *training-free* trivial-predictor panel reported as
  mandatory columns, and none expressed in **copy-LF skill units** for a
  no-solver-at-test regime. That composition is open."
- **D2** — value-of-LF accounting (matched ± LF arms) — **`preempted-but-MF-composition-open (cite)`**;
  Yang et al. (https://arxiv.org/abs/2209.08754) supplies the matched no-distillation
  arm and the **non-monotone law** (student worsens as the privileged feature becomes
  more predictive, via teacher variance).
- **D3** — overfitting anatomy / n_eff — **`preempted-but-MF-composition-open`, LOW
  confidence**; the report explicitly says "Re-search before a B2/B3 card leans on this."

Instructions to the brainstormer (report §"For the brainstormer"): reframe the spread
half as *adopting* Agarwal + Du rather than inventing a protocol; budget for "three
seeds never declaring significance" for sub-2-point effects; lead the floor half with
"training-free floors expressed in copy-LF skill units for a no-solver-at-test regime";
note that `floors.json` already shows **ifc_poisson's NN floor is a 5-atom dictionary**
(all 128 test points map onto 5 train fields) and report that as a caveat; write Yang
et al.'s non-monotone law into `expected_falsification`; do not quote the do-not-cite
list (FNO r = 0.28, 60.1K samples, SPDEBench factor-of-two, the 20-sample anecdote).

Cross-stream (prior art only, `websearches/r2s1_direct/batch_1/report.md`): D1
(FiLM-conditioned spectral decoder) is **`preempted`** — "Admissible only as a
*measurement/baseline arm* on this panel against the mandatory floor arms"; D3
(conditional-mean/aleatoric floor certification, arXiv:2605.28076) is
**`preempted-but-MF-composition-open`**, open because "the barrier diagnostic has
never been instantiated where the unobserved driver is a *stored coarse solve*".

## 2. §12 conventions verbatim

program.md §12 preamble: "Common to all streams: quote the launch anchor (best-floor
geomean 23.06) and the per-dataset floor table verbatim when designing; thresholds must
clear the noise floor for the dataset(s) — while `state/noise_floor.json` is
provisional, judge falsification clauses directly (§4.3); cite the websearcher's
prior-art verdict; every proposal carries a complete `recipe` block; floor arms
mandatory on model cards (§2.2)."

program.md §12.4 `r2s4_diag` (diagnostics), verbatim:

> - **B1 is pre-directed**: floor + spread certification. (a) Verify the frozen
>   floors reproduce (standing zero-predictor column included); (b) train ONE
>   minimal condition→HF baseline (smallest reasonable FiLM-FNO decoder or
>   MLP→field) at smoke tier, seeds {0,1,2}, on the panel — its per-dataset
>   seed spread replaces the provisional `state/noise_floor.json` (§4.3).
>   Diagnostic card, but WITH training (3 seeds) — the exception is the point;
>   cheap by design (small model).
> - Later batches: **value-of-LF accounting** — matched architecture ± LF
>   training signal (coordinates with r2s3: r2s4 measures, r2s3 optimizes);
>   **overfitting anatomy** at N_hf ∈ {5, 20, 50} (ifc ladder) and N=400
>   (sharp): train/test gap decomposition, effective sample counts (the
>   **drift-class rule**: when n_eff/N < 1%, only in-job paired controls are
>   controls).
> - The round-1 probe library is seeded in `tools/` (37 files; index header
>   notes they were written against round-1 eval paths — adapt on use, promote
>   adapted versions via the register turn).

Anchor (`state/anchors/r2s4_diag.json`): `best_floor_panel_geomean` = **23.0636**,
`provisional: false`; per-dataset best-floor skills helmholtz 3.3441 (zero),
pfc 59.8118 (mean), allen_cahn 269.1959 (NN), fisher_kpp 11.9931 (mean),
cahn_hilliard 23.1803 (NN), ifc_poisson 10.0549 (NN).

Provisional noise floor (`state/noise_floor.json`, `_source: round1-batch0-rescaled`,
`_provisional: true`) `min_claimable_effect` in skill units: helmholtz **10.6811**,
pfc **6.9839**, allen_cahn **14.8152**, fisher_kpp **1.2198**, cahn_hilliard **1.1604**,
ifc_poisson **0.2399**.

## 3. Within-stream prior cards

**None.** `experiment_cards/r2s4_diag/` contains no batch directories
(`ls -R experiment_cards` shows all four stream dirs empty); this is the stream's
first card and the round's certification card (§8: "r2s4-B1 is the certification card").

## 4. Cross-stream prior cards

**None** — no cards exist in any stream (all of `experiment_cards/{r2s1_direct,
r2s2_stacked,r2s3_lf_train_signal,r2s4_diag}/` are empty). The only cross-stream
artifacts are the four batch-1 websearch reports; the r2s1 one bears directly on this
design (§1 above) and on the scope boundary discussed in §6.

## 5. Reopen candidates

**None** — no prior cards, therefore no `reopen_candidate: true` entries anywhere
(verified: `experiment_cards/*/` empty).

## 6. What is UNKNOWN

1. **The empirical seed-noise constant for condition→HF at smoke tier.** The one
   number that gates every later falsification clause in this round. `noise_floor.json`
   is round-1 **LF-consuming** families rescaled: those models read a real coarse solve
   at test, so most of their output was determined by the input field, and their seed
   spread is plausibly an *under*estimate for condition-only models (nothing pins the
   output but the weights) — or an overestimate on helmholtz, where the rescaled
   min-claimable-effect (10.68 skill) exceeds the entire best-floor value there (3.34).
   Direction of the bias is unknown; that is exactly what must be measured.
2. **Whether 3 seeds license anything at all.** Du reports a conservative paired
   protocol declaring nothing significant for 0.6–2.0-point effects. Unknown: on this
   panel, with n_test = 100–128 per-sample rel-L2 values per run, whether the
   *per-sample* bootstrap axis restores enough power to license effects materially
   below the provisional constants. The card must produce a usable number either way.
3. **Whether the frozen floors reproduce from the stripped view.** `floors.json` was
   computed by `eval/make_floor_anchors.py` from the ORIGINAL datasets. The stripped
   view removes only test LF files; every input the floors need (train HF fields, test
   conditions, test HF targets) should still be present. Nobody has checked. If they
   reproduce to ≤1e-9, that is an independent certificate that stripping damaged
   nothing but LF; if they don't, every round-2 number is suspect. G1-r2 checked
   `lf_fids == []` and train-fid identity, not floor values.
4. **The conditional-mean (aleatoric) barrier per dataset.** ADR r2-0003 establishes
   condition→HF is a *stochastic* map on pfc / fisher_kpp / allen_cahn (measured: two
   nearest-in-condition pfc train samples, standardized distance 0.0124, differ by
   relative field 1.149). It does NOT quantify the resulting barrier. Unknown: how far
   below the frozen floors any deterministic condition-only model can possibly go
   there — i.e. whether `train_mean` (59.81 pfc / 11.99 fisher_kpp) is already
   essentially the barrier, or whether a large gap remains. Without this, a B1 spread
   number certifies noise but not headroom, and later cards cannot tell "model failed"
   from "map is stochastic".
5. **Scope boundary with r2s1.** r2s1's websearcher recommends its D3 (conditional-mean
   barrier certification) as "the only open composition found" — but §12.1 directs r2s1
   to build a from-scratch condition→HF *architecture* (model card), and §12.4 gives
   floor certification to r2s4. Unknown/undecided until this card fixes it: who owns
   which half. The training-free half (estimate the barrier from train HF fields) is
   floor work and belongs here; the *validation* half (show the missing driver lives in
   the withheld LF field, which ADR r2-0003 already probed for pfc/fisher_kpp) is
   LF-side work and belongs to r2s1/r2s2/r2s3 or a later r2s4 batch.
6. **Whether a minimal condition-only decoder even beats the training-free floors.**
   The launch anchor says the regime is hard (best floor 10–270× worse than copy-LF),
   but no trained condition-only model has been scored on this panel under the
   corrected denominators. Round-1's `mf_fno_transfer_film` — condition→field all along
   — lost to copy-LF everywhere (program §3), and its rescaled helmholtz skills
   (10.06–20.74) are *worse than the zero floor* (3.34). Unknown: does the without-LF
   arm clear the floor panel at all? That answer sets whether success criterion 2 is
   reachable and whether B2's value-of-LF contrast has a meaningful base.
7. **What the without-LF arm should be, so B2's contrast is matched.** §12.4's B2 needs
   a matched ± LF pair. Unknown until fixed by fiat here: the architecture, budget,
   val-split discipline and normalization that B2 will hold constant. If B1 does not
   pre-register them, B2's "matched" claim is unfalsifiable.
8. **ifc_poisson at N_hf = 5.** `floors.json` shows the NN floor is a 5-atom dictionary
   (`nn_index_hist_top5` = {0:41, 1:17, 2:20, 3:38, 4:12} covering all 128 test points).
   Unknown: whether a val split is even definable there (10% of 5 = 0), and what seed
   spread means with 5 training fields. Every ifc claim is anecdote-grade (§12.1).
9. **D3 (overfitting anatomy) evidence base is thin** — one dedicated search, LOW
   confidence, "no train/test gap decomposition protocol found", "no PDE-domain
   effective-sample-size diagnostic". Unknown whether a defensible n_eff estimator
   exists at all; the websearcher asks for a fresh search before B2/B3 leans on it.
   This is a reason NOT to put overfitting anatomy in B1.
