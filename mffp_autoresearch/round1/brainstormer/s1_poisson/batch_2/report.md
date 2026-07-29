# Brainstormer Report — Stream `s1_poisson`, Batch 2

**Stream**: s1_poisson (gap) · **Batch**: 2 · **Total iterations**: 1 · **Slot filled**: 1/1 ·
**Reopen candidates resolved**: 0 (none existed)

## Slot

- **Category**: `normalization × composition factorial / ladder-data-fusion`
- **Card type**: `model`

- **Motivation**:
  B1 measured a level-set effect *through* a normalization defect. The `mf_fno_ladder` family
  divides every pooled stage-1 target by ONE scalar taken from the coarsest, largest-amplitude
  level (`max|Y_all|` = 0.077146) while `ifc_poisson`'s four fidelity levels differ by a clean ~h²
  amplitude law spanning **75.7× in RMS** (consecutive ratios 4.3788 / 4.1957 / 4.1198). B1 part 6
  measured that **74.73 %** of the primary arm's squared test error is removable by a per-sample
  scalar gain, that retained conditional variance ranks exactly as the arms do (0.8574 / 0.4408 /
  0.4206 / 0.2652), and — at reduced capacity — that per-level target scaling **reverses the sign
  of B1's central contrast** (allpairs 0.214313 → 0.087352, becoming 1.69× better than
  two_level/per_level 0.147214). Classical MF *models* this level ratio as ρ (AR1
  `y_high = ρ·y_low + δ`; NARGP's input-dependent ρ_t(·)); the shared scaler neither models nor
  removes it, so per-level scaling implicitly restores the ρ the pooled formulation deleted. The
  websearcher scores this as **`preempted-but-MF-composition-open`** and directs that it be framed
  as a hygiene fix whose effect size is being measured, never as an invention; the same run gives
  the open composition (all ordered pairs, one shared net, N_hf = 5) its first *fair* test, motivated
  by verdict (v): recursive NARGP-style cascades train each level independently so "no information
  flows backward from higher to lower fidelities" — exactly what one shared pooled-row operator
  avoids. B1's clause conflated normalization with composition; this card pre-registers **two
  separate clauses** so that conflation cannot recur (B1 part 7 requirement).

- **Concrete config**:
  Family `models_r1/mf_fno_ladder_norm`, vendored deterministically from B1's build commit (B2 gets a
  fresh worktree off `round1-substrate`, so B1's family must be re-materialized). Inside the B2
  worktree:
  `git checkout d070f86f18028893c59618c291e5bf4ab5c37dba -- models_r1/mf_fno_ladder` then
  `git mv models_r1/mf_fno_ladder models_r1/mf_fno_ladder_norm`. Provenance pins to verify before any
  edit and record in `build_notes` (sha256-16): `backbone.py f56fa8029fad2ffb` (= guarded
  `akash/common/backbone.py`, read-only), `model.py 740ed992efcda53e`,
  `smoke_eval.py a693d77909c14ccc`, `manifest.json 849c8c390517ca9c`,
  `INSPIRATION.md 94e9ec5724215e81`. All hyperparameters (hidden 64 / blocks 4 / modes_cap 12 /
  batch 16 / lr 1e-3 & 3e-4 / wd 1e-5 / clip 1.0), the `cond_from=target` correspondence fix, the
  self pairs, the 200 + 200 two-stage schedule and the eval query `(X_test, f_src=0, f_tgt=1)` are
  inherited **unchanged**.

  **The only code change** — one new env knob `MFFP_LADDER_SCALER ∈ {shared, per_level,
  shared_reweight}`, default `shared` (bit-preserving):
  1. Replace the scalar at `smoke_eval.py:359` with a per-row vector `scal` of shape `(M,1,1)` and
     let `_train` divide by it, so shared and per-level go through one code path (already prototyped
     at `scratchpad/reanalysis_turn_3.py:68-69,114-127` on B1's branch).
     `level_scaler[f] = max(|Y^{(f)}|.max(), 1e-8)` from the arm's stage-1 rows grouped by each row's
     **target** fidelity. `shared`: `scal[i] = max_f level_scaler[f]` (must equal `max|Y_all|` =
     0.077146 bit-for-bit). `per_level`: `scal[i] = level_scaler[f_tgt(i)]`. `shared_reweight`:
     shared `scal` **plus** a per-row loss weight `w[i] ∝ (S/level_scaler[f_tgt(i)])²` normalized to
     `mean(w) = 1`, loss `mean(w_b·(pred − y/S)²)`; `w ≡ 1` in the other two modes.
  2. Stage 2 untouched (`scaler_hf` = 0.0018357) — it is already single-level.
  3. **Carry B1's two build traps**: checkpoint key must include *both* factors
     (`<ckpt_dir>/mode_{MODE}__scal_{SCALER}/last.pt`, meta-guard extended to the scaler), and the
     job script must export a per-arm `ROUND1_EVAL_RESULTS` (`score_panel._run_one` derives paths
     from `(family_dir.name, dataset, epochs, seed)` only, so the arm is invisible to it).
  4. **Score-neutral instrumentation** into the result JSON `extra`: per-level scaler values +
     per-target-level row counts; the measured consecutive per-level RMS ratios (expect
     4.379 / 4.196 / 4.120 ≈ 2², the empirical h^p measurement demanded by verdict (ii)); an f_tgt
     output-RMS sweep over `{0, 1/3, 2/3, 1}` from the final checkpoint (B1 T2 measured 3.4× against
     the data's 75.7×; under `per_level` it should collapse toward ~1×); and B1's `preds_test.npz`
     dump (B1 part 7 `cross_stream_notes` item 3).

  **Five arms**, one SLURM job, seed 0, serial, ~6 min total:

  | arm tag | `MFFP_LADDER_MODE` | `MFFP_LADDER_SCALER` | role |
  |---|---|---|---|
  | `two_level__shared` | two_level | shared | cell (−,−); **B1 reproduction gate** |
  | `allpairs__shared` | allpairs | shared | cell (+,−); **B1 reproduction gate**; F1 control |
  | `two_level__per_level` | two_level | per_level | cell (−,+); F2 control |
  | `allpairs__per_level` | allpairs | per_level | cell (+,+); **PRIMARY**; F1 + F2 treatment |
  | `allpairs__shared_reweight` | allpairs | shared_reweight | mechanism disentangler; **in no clause** |

  The 5th arm separates per_level's two simultaneous effects — (a) equalizing each level's loss
  contribution vs (b) removing the 75.7× gain law from the represented function. `shared_reweight`
  does (a) without (b). If it ≈ `per_level`, the effect is loss weighting and B1 part 6's
  amplitude-channel-capture claim is wrong; if it ≈ `shared`, B1 part 6 is confirmed at production
  capacity. Numerics (verifiable): `(S/s_f)² = 1 / 10.6 / 125 / 1766` at fid 8/16/32/64, target-level
  row counts 100/100/60/20 in the 280-row allpairs set → mean raw weight 157.1, normalized weights
  0.0064 / 0.0675 / 0.796 / 11.24; dynamic range ~1766, safe in float32.

  **Validity gate (not a clause)**: the two `shared` cells must reproduce B1 seed-0 within 10 %
  (`two_level` 0.0925–0.1130, `allpairs` 0.1884–0.2302). A miss means the vendoring or knob default
  changed inherited behaviour and every contrast is suspect (ALGO, fix before reading results).

- **Recipe**:
```json
{
  "base_family": "mf_fno_ladder",
  "base_commit": "d070f86f18028893c59618c291e5bf4ab5c37dba",
  "family_dir": "models_r1/mf_fno_ladder_norm",
  "datasets": "ifc_poisson",
  "epochs": 200,
  "seeds": [0],
  "env": {
    "MFFP_LADDER_MODE": "allpairs",
    "MFFP_LADDER_SCALER": "per_level",
    "_arms": [
      {"tag": "two_level__shared",         "MFFP_LADDER_MODE": "two_level", "MFFP_LADDER_SCALER": "shared"},
      {"tag": "allpairs__shared",          "MFFP_LADDER_MODE": "allpairs",  "MFFP_LADDER_SCALER": "shared"},
      {"tag": "two_level__per_level",      "MFFP_LADDER_MODE": "two_level", "MFFP_LADDER_SCALER": "per_level"},
      {"tag": "allpairs__per_level",       "MFFP_LADDER_MODE": "allpairs",  "MFFP_LADDER_SCALER": "per_level"},
      {"tag": "allpairs__shared_reweight", "MFFP_LADDER_MODE": "allpairs",  "MFFP_LADDER_SCALER": "shared_reweight"}
    ],
    "_primary_arm": "allpairs__per_level",
    "_design": "2x2 factorial {two_level,allpairs} x {shared,per_level}, all four cells reported, plus one non-clause mechanism arm allpairs__shared_reweight. No screen-and-promote (ADR 0007 reconciliation in iteration_1.md): the arms ARE the factor levels, all five are reported, the primary arm is fixed before submit.",
    "_sweep": "one SLURM job, seed 0, runs 5 score_panel.py calls serially, each with --env MFFP_LADDER_MODE=<m> --env MFFP_LADDER_SCALER=<s> and its own --out result_ifc_poisson_<tag>_s0.json; export ROUND1_EVAL_RESULTS=<outputs>/eval/results_<tag> per arm so per-arm result JSONs and ckpt dirs cannot collide (B1 build trap 1). Checkpoint path <ckpt_dir>/mode_<m>__scal_<s>/last.pt with the meta-guard extended to the scaler.",
    "_source": "vendored from branch round1/exp-s1_poisson-B1 @ d070f86 path models_r1/mf_fno_ladder (sha256-16: backbone.py f56fa8029fad2ffb, model.py 740ed992efcda53e, smoke_eval.py a693d77909c14ccc, manifest.json 849c8c390517ca9c, INSPIRATION.md 94e9ec5724215e81), renamed to models_r1/mf_fno_ladder_norm; the ONLY edit is the MFFP_LADDER_SCALER knob + the ckpt key + score-neutral extra{} instrumentation. akash/** and factory_root/{eval,baselines,references,scripts,data} are never touched.",
    "_sbatch": "partition gpu, --gres=gpu:h100:1 (ADR 0005), --time=02:00:00; B1 ran 4 arms in 4.45 min, so 5 arms is ~6 min (5% of the request)."
  }
}
```

- **Expected outcome**:
  Metric: `ifc_poisson` test nRMSE → skill vs paper bar 0.036 (ADR 0002), **seed 0 only**, labelled
  `provisional-single-seed` (ADR 0004). **Noise floor: 0.23990756 skill units = 0.0086367 nRMSE.**

  Four reference lines to carry in card part 4 (reason to carry them: McGreivy & Hakim 2024,
  https://arxiv.org/abs/2407.07218 — 79 % (60/76) of ML-beats-solver claims use a weak baseline):
  **anchor 1.5656334 skill / 0.056363 nRMSE**; **noise floor 0.23991 skill units**; **training-free
  nearest-condition matched-8² lookup with one calibration gain 0.24828 nRMSE / 6.8967 skill**;
  **HF-train-mean predictor 0.40343 nRMSE / 11.2064 skill**. *Unit warning for the card*: 0.23991 is
  in skill units, 0.24828 is in nRMSE units — they look alike and are not comparable.

  **Honest extrapolation label**: every `per_level` prediction is extrapolated from a
  **reduced-capacity, scratchpad-only proxy** (hidden 16 / 2 blocks / modes 8, joint 30 ep, ft 200
  ep, 1 CPU core, seed 0, seed-1 replication incomplete — both allpairs seed-1 runs killed at the
  1200 s cap). The proxy's own validity gate shows it *attenuates* the shared-scaler gap (1.17× vs
  production 2.04×), and it does so mostly by degrading `two_level` — the arm F2 compares against.
  Ranges, not points, are the claim.

  | arm | predicted nRMSE (range) | predicted skill | basis |
  |---|---|---|---|
  | `two_level__shared` | 0.1027 (0.0925–0.1130) | 2.85 | B1 seed-0 reproduction |
  | `allpairs__shared` | 0.2093 (0.1884–0.2302) | 5.81 | B1 seed-0 reproduction |
  | `allpairs__per_level` | **0.085 (0.060–0.130)** | 2.36 (1.67–3.61) | proxy ratio 0.408 × 0.2093 |
  | `two_level__per_level` | 0.083 (0.065–0.115) | 2.30 (1.81–3.19) | proxy ratio 0.804 × 0.1027 |
  | `allpairs__shared_reweight` | 0.15–0.35 | 4.2–9.7 | nearer `shared` if B1 part 6 is right |

  - **Δ vs anchor**: the primary arm is predicted at skill 2.36 vs anchor 1.5656, i.e. **+0.79 skill
    units WORSE than the anchor** (3.3× the floor). This card does not claim a champion; it claims
    two internal contrasts.
  - **F1 vs the floor**: predicted Δ = 0.2093 − 0.085 = **0.124 nRMSE = 3.45 skill = 14.4× the
    0.23991 floor**; pessimistic end 0.079 nRMSE = 2.20 skill = **9.2× the floor**. Confident clause.
  - **F2 vs the floor**: predicted Δ = 0.083 − 0.085 = **−0.002 nRMSE = −0.06 skill = 0.23× the
    floor**, i.e. under the primary extrapolation **F2 is predicted to fire**. The alternative
    extrapolation (transfer the proxy's per_level *gap* instead of each arm's ratio) puts allpairs at
    0.049 and F2 at +0.95 skill = 4.0× the floor. The two extrapolations disagree qualitatively —
    which is why the contrast is worth running, and either outcome is decisive for the stream
    (B1 part 7: "If batch 2 confirms the fix and still loses to the anchor, s1 should stop
    optimizing this family").
  - **Cratered-verdict forewarning**: threshold = 1.5 × 1.5656334 = 2.34845 skill = **0.084544
    nRMSE**, and the primary arm's point prediction (0.085) sits essentially on it. The card may be
    labelled `cratered` even if F1 succeeds by 14× the floor. `cratered` is an anchor-relative
    bookkeeping label; B1 was cratered and still produced the stream's best mechanism finding.
  - **Guard set**: owed only if an arm claims a panel win over the anchor (i.e. nRMSE < 0.056363).
  - **Wall clock**: ~6 min/seed on one H100 (B1: 4 arms in 4.45 min); `--time=02:00:00` (ADR 0005).

- **Expected falsification** (TWO separate clauses — B1 part 7 requirement):
  - **F1 — normalization contrast.** Falsified if `allpairs__per_level` fails to beat
    `allpairs__shared` on `ifc_poisson` test nRMSE by more than the certified noise floor — seed-0
    skill improving by ≤ **0.23991 skill units (≤ 0.0086367 nRMSE)** — which would mean the shared
    target scaler was not the cause of B1's ~2× degradation of the pooled ladder and B1 part 6's
    amplitude-channel-capture mechanism does not survive production capacity.
  - **F2 — composition contrast.** Falsified if `allpairs__per_level` fails to beat
    `two_level__per_level` by more than the certified noise floor — seed-0 skill improving by ≤
    **0.23991 skill units (≤ 0.0086367 nRMSE)** — which would mean that even with the amplitude
    nuisance removed, the intermediate fidelities and the extra ordered pairs add nothing measurable
    over the 8²→64² transfer at N_hf = 5, and the websearcher's open composition is empirically empty
    on this ladder.

  Neither clause references `allpairs__shared_reweight`; that arm is exploratory mechanism
  instrumentation and cannot falsify anything.

- **Prior-art verdict quoted** (verbatim from `websearches/s1_poisson/batch_2/report.md`,
  "## Prior-art verdict"):

  > **(i)** Per-level / per-fidelity **target** normalization (`MFFP_LADDER_SCALER=per_level`) in a
  > pooled multi-level ladder | **preempted-but-MF-composition-open** | per-level error normalization
  > required in multi-level residual NNs:
  > https://www.sciencedirect.com/science/article/abs/pii/S0045782523007892 (**snippet-grade, fetch
  > 403**) · internal-normalization discretization-dependence: https://arxiv.org/html/2605.07375
  > (fetched) · classical MF models ρ instead of normalizing:
  > https://smt.readthedocs.io/en/latest/_src_docs/applications/mfk.html (fetched) · four MF sources
  > that do not state their cross-fidelity normalization at all: https://arxiv.org/html/2602.01176v1,
  > https://www.frontiersin.org/articles/10.3389/fmats.2019.00061/full,
  > https://arxiv.org/abs/2507.07292 (all fetched) | Per-level standardization of **targets pooled
  > into ONE shared fidelity-conditioned operator**; no published effect size for the choice; nothing
  > at N_hf = 5 on an elliptic ladder. Frame as a **hygiene fix measured as an ablation**, never as
  > an invention.

  > **(ii)** h^p-aware residual/target scaling as an explicit inductive bias (hard-coded h² divisor)
  > | **preempted (cite)** | https://pmc.ncbi.nlm.nih.gov/articles/PMC11985099/ (fetched — GRE:
  > b(x)=x^r in the kernel; "the normalized error (f(x)−f(0))/b(x) behaves regularly"; r estimated
  > when unknown) · https://arxiv.org/pdf/2504.05493 (search-return — NN replaces Richardson for
  > truncation error) | … **Do not hard-code h²**; use the empirical per-level scaler and report the
  > measured 4.379/4.196/4.120 ≈ 2² agreement as a result.

  > **(iii)** The **factorial** `{shared, per_level} × {two_level, allpairs}` design itself |
  > **novel** (design-level, weak claim) | explicit engine negatives, iteration_5 term 3 and
  > iteration_3 term 2; nearest neighbors: routine hyperparameter ablations
  > https://arxiv.org/html/2405.17260v2 (search-return), MFRNP aggregation ablation
  > https://arxiv.org/html/2402.18846v1 (batch-1 fetched) | Nothing close found. Value is **internal
  > validity** (separating the two contrasts B1 conflated), not novelty. Claim "not previously
  > ablated", never "novel method".

  > **(iv)** Training-free level-matched nearest-condition lookup as a reported floor (0.24828) |
  > **novel** for elliptic MF; report, do not claim | https://arxiv.org/abs/2407.07218 (fetched —
  > 79 % weak baselines; abstract does **not** cover NN/interpolation baselines) …

  > **(v)** All-ordered-pairs composition (carried over from batch 1) |
  > **preempted-but-MF-composition-open** (batch 1, unchanged) | … Batch 2 adds: NARGP-style
  > recursive MF trains each level independently so "no information flows backward from higher to
  > lower fidelities" (iteration_5) — the deficiency the pooled shared network is supposed to avoid,
  > and a sharper motivation than batch 1 had.

  Card `prior_art.verdict` to record: **`preempted-pivoted`** (the schema's nearest enum to
  `preempted-but-MF-composition-open`, following the B1 precedent). The card must say "not previously
  ablated", never "novel method", and must present `per_level` as a hygiene fix whose effect size is
  being measured.

- **Immutables self-check**: **pass (10/10)** — one positive-evidence sentence per item recorded in
  [iteration_1.md](iteration_1.md) § "Immutables self-check". Headlines: (3) the entire diff lives in
  the B2 worktree under `models_r1/`, `scripts/`, `notes/`, `scratchpad/` and the only eval-layer
  interface is existing `score_panel.py` CLI flags; (4) the knob changes the **training** target
  normalization only (training loss is explicitly free under §5) — the output is multiplied back by
  `scaler_hf` before scoring, so the scored quantity is the raw HF field in every arm; (5) the knob is
  an env var declared in `recipe.env`, so it enters the cache key exactly as `MFFP_LADDER_MODE` did
  (B1 proved this with four distinct `code_hash` values); (7) vendoring is from B1's own round-1
  branch commit, not from `akash/**`, and `backbone.py` carries the same sha256 the B1 reviewer
  verified against the guarded copy; (9) both clauses are written as strict exceedance of
  `ifc_poisson`'s certified floor 0.23990756 skill = 0.0086367 nRMSE, with F1 predicted at 14.4×
  (pessimistic 9.2×) that floor; (10) nearest pre-falsified lever is **LF low-mode freezing
  (`mf_fno_spectral`)** — nothing is frozen, copied or masked here, `modes_cap` stays 12 in every arm,
  and the intervention is a target-normalization statistic before the loss, not a spectral inductive
  bias. No revision pass was needed.

- **Anchor reference**: `null` — `s1_poisson` is a **gap** stream, so per program.md §4.5 the
  own-stream anchor (`state/anchors/s1_poisson.json`, 1.5656334) is implicit; the `card_id` form is
  reserved for `s5_tuning` batches ≥ 2.

- **Source iteration**: [iteration_1.md](iteration_1.md)

## Reopen candidates

| Candidate | Verdict (retry/drop) | Eased conditions | Source iteration |
|---|---|---|---|
| _(none — no card in any stream carries `reopen_candidate: true`; s1_poisson-B1 is `status: complete, reopen_candidate: false`)_ | n/a | n/a | [iteration_1.md](iteration_1.md) |

## Skipped slot

Not applicable — the slot is filled.

## Summary table

| Slot | Category | One-liner | Status |
|---|---|---|---|
| s1_poisson-B2 | `normalization × composition factorial / ladder-data-fusion` | 2×2 `MFFP_LADDER_SCALER {shared, per_level}` × `MFFP_LADDER_MODE {two_level, allpairs}` on `ifc_poisson` (+ one non-clause `shared_reweight` mechanism arm), 200 ep, seed 0, ~6 min on H100; two separate pre-registered clauses so B1's normalization/composition conflation cannot recur | filled |
