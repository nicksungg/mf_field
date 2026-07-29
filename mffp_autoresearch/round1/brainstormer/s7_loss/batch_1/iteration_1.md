# Iteration 1 — s7_loss batch 1 slot design

## Design context considered

- `summary_so_far.md` section 6 (the seven unknowns), especially #1 (unmeasured
  per-sample norm spread on the claimable datasets), #2 (oracle-conversion rate),
  #6 (pfc is the only dataset where mechanism and headroom coincide).
- The prior-art verdict table (`websearches/s7_loss/batch_1/report.md`), ranking
  C-AMP > C-BAND, with C-REL as control-only and C-STRUCT dead.
- program.md §12.7 verbatim (quoted in summary section 2), §5 immutables (below),
  §2.1 (metric immutable), §4.4 (strict single seed), §4.5 (anchor policy).
- ADR 0007 (propose-many / screen-cheap / promote-few), ADR 0009 (physics-agnostic),
  ADR 0012 (this stream's ground rules), ADR 0004 (single seed), ADR 0005 (H100).
- Anchor 6.703; `state/noise_floor.json` verbatim; the geomean floor 0.884.
- The base family's actual training loop, read first-hand
  (`models/mf_fno_transfer_film/smoke_eval.py:76-103`): `loss = F.mse_loss(pred, yb)`,
  `yb = Y/scaler`, `scaler = max|Y_train|` — one global scalar per stage.
- The s5-B1 worktree family as the mechanical substrate pattern
  (`worktrees/s5_tuning/B1/models_r1/mf_fno_transfer_film_modes/smoke_eval.py`,
  lines 63–66 REPO_ROOT fix, 130–178 RNG-neutral checkpointing).
- `state/timing_ledger.json`: H100 panel @200 epochs = 36.6 min/seed; guard set
  @2 epochs = 0.8 min — a 6-arm contract screen is ~10–15 min.

## Proposal reasoning

### The mechanism I am attacking

Three independently-recorded findings collapse onto ONE line of code:

- F19 (training loss != scored metric) — program.md §12.5, MODEL_TWEAKS backlog.
- s3-B1: per-sample ||u|| spans **408x** on helmholtz against a single global
  `scaler_hf = 7.38`.
- s2-B1 M5a: `amplitude_share_of_error` 0.865 (helmholtz), 0.19 (pfc), 0.14
  (cahn_hilliard); `alpha_mean` 0.73 (pfc) / 0.76–0.78 (cahn_hilliard) — a
  **systematic** amplitude under-prediction, not noise.

The line is `F.mse_loss(pred, Y/max|Y_train|)`. Under a global scaler, MSE's
gradient is dominated by the largest-norm samples; the scored metric weights
every sample by its own norm. So the champion is fitted to an objective that
does not ask for what it is graded on, and it responds by predicting an
average amplitude (`alpha_std` 0.59–0.88 on helmholtz: "the right pattern at
~10x the wrong, sample-dependent amplitude" — s2-B1 M5a verbatim).

### The key algebraic observation (verified numerically this iteration)

For a sample with prediction `p` and target `y`, write `g = ||p||/||y||`
(gain) and `cos = <p,y>/(||p|| ||y||)`. Then

```
rel_i^2 = ||p-y||^2/||y||^2 = (1 - cos^2) + (g - cos)^2
        = [shape term]     + [gain term]
```

I verified this to 4.4e-16 max abs error on random tensors. So the **scored
metric factorizes exactly into a shape term and a gain term**, and

```
L_amp(lambda) = mean_i [ (1 - cos_i^2) + lambda * (g_i - cos_i)^2 ]
```

is a one-parameter family whose `lambda = 1` member IS the (squared) scored
metric. This satisfies the websearcher's binding design constraint verbatim —
"do not propose a scale-*invariant* loss ... Propose a two-term objective
(normalized-shape term + explicit per-sample gain term)" — because the gain
term is explicit and never dropped. Setting `lambda > 1` is exactly the
"emphasize per-sample gain calibration" intervention M5a motivates, with no
free-floating design choices to defend.

Equally, by Parseval, the per-sample-normalized **flat-weight** spectral squared
error equals `rel_i^2` exactly; so

```
L_band(beta, k_c) = mean_i  sum_k w(k) |F(p_i - y_i)(k)|^2 / ||y_i||^2,
                    w(k) = beta for |k| < k_c, else 1
```

is a second one-parameter family whose `beta = 1` member is the same origin.
`k_c = k_nyq/8` reproduces s2-B1 M3's dyadic band 0 exactly
(`worktrees/s2_beyond_copy/B1/models_r1/s2_copylf_forensics/forensics.py:99-125`),
so the arm is aimed at the measured band, not a guessed one.

Therefore **all arms are one substrate**: one per-sample-normalized objective
with two orthogonal knobs (`lambda`, `(beta, k_c)`), sharing a common origin
that is itself the C-REL control arm. This is exactly the ADR 0007 shape
(one substrate, env-knob variant selector) without any arm being a bolt-on.

### Alternatives weighed and rejected

- **C-STRUCT (Sobolev / gradient / SSIM / interface-weighted)** — the literal
  ADR 0012 framing. REJECTED: verdict `preempted`
  (https://arxiv.org/abs/2402.09084, the SSIM survey), AND empirically
  contraindicated by our own M4 ("the champion's spatial error is nowhere
  interface-localized beyond ~1.3x area share"; pfc's interface prediction
  FALSIFIED). Proposing it would burn the stream's first card on a mechanism
  our own diagnostic already excluded. Recorded here so the deviation from the
  ADR's seed direction is auditable.
- **C-LFANCHOR** — REJECTED per verdict item 5: the champion is LF-blind at
  inference (M1), LF/HF low-band coherence is 0.9999 (allen_cahn), so it
  degenerates into C-BAND while transmitting no per-sample LF information.
- **A whole new architecture that consumes LF at test time** — that is the
  right fix for M1, but it is s3_warp / s6_local's territory, not a loss stream.
- **Per-sample output normalization (predict `y/||y||` and a separate scalar
  head)** — REJECTED: that is an *architecture* change (new head), not an
  objective change; §12.7 confines this stream to the training objective, and
  it would confound with s6_local. The gain term achieves the same pressure
  through the loss only.
- **`mean_i rel_i` (unsquared) as the control** — REJECTED in favour of
  `mean_i rel_i^2`: the unsquared form has a sqrt kink with unbounded gradient
  as `rel -> 0`, and the squared form is the exact origin of BOTH knob families,
  so every arm difference is attributable to its knob alone.
- **Applying the objective to the HF fine-tune stage only** — REJECTED for
  batch 1 (kept as a batch-2 ablation, exposed as `MFFP_S7_STAGES`): with
  N_hf = 5 on ifc_poisson the LF-pretrain stage carries essentially all of the
  amplitude prior, so an HF-only application would be a much weaker intervention
  and its null would be uninterpretable.

### Arm slate (ADR 0007: 5 arms, ranked)

Selector env `MFFP_S7_LOSS`; all arms per-sample normalized with the denominator
clamped as `transolver_residual/smoke_eval.py:68` already does
(`clamp(min=1e-4)` relative form; here `max(||y_i||, 1e-4 * mean_j ||y_j||)`),
addressing PDEBench's near-zero-magnitude nRMSE caveat.

| rank | arm id | env | objective | why this parameter value |
|---|---|---|---|---|
| 1 | **A1a** | `MFFP_S7_LOSS=amp`, `MFFP_S7_LAMBDA=4.0` | `mean[(1-cos^2) + 4*(g-cos)^2]` | C-AMP, top-ranked verdict row. lambda=4 = 4x gain emphasis, the direction M5a implies (`alpha_mean` 0.73/0.76 = systematic under-gain); chosen a priori, not tuned |
| 2 | **A1b** | `MFFP_S7_LOSS=amp`, `MFFP_S7_LAMBDA=auto` | same with `lambda_t = detach(shape)/detach(gain+1e-8)` clamped to [0.25, 64] | the fetched mitigation for failure mode (ii) conflicting gradients (https://arxiv.org/html/2502.02440v1 uses gradient-norm balancing); here loss-magnitude balancing, described as such, not overclaimed as gradient-norm balancing |
| 3 | **A2a** | `MFFP_S7_LOSS=band`, `MFFP_S7_BETA=4.0`, `MFFP_S7_KC=8` | low band `kr < k_nyq/8` weighted 4x | C-BAND at exactly M3's band 0, the band where `R_low > 1` on 5/5 x 3/3 |
| 4 | **A2b** | `MFFP_S7_LOSS=band`, `MFFP_S7_BETA=2.0`, `MFFP_S7_KC=4` | bands 0+1 (`kr < k_nyq/4`) weighted 2x | milder, wider variant — hedges the over-constraint failure mode (i) |
| 5 | **A0** | `MFFP_S7_LOSS=rel` | `mean_i rel_i^2` | C-REL **control** (verdict: preempted; measurement only). Isolates how much of the gap is pure loss/metric mismatch before any structured objective is credited |
| — | **A-def** | env unset | `F.mse_loss` | not an arm: the default-equivalence proof that licenses comparison against the batch-0 anchor |

### Screening plan (contract tier, ADR 0007 step 2)

One contract-tier pass, seed 0, `--epochs 2`, run before any SLURM submit:

1. **Default equivalence** (`A-def`, env unset) on `ext__helmholtz_2d,ifc_poisson`
   vs the untouched factory family `mf_fno_transfer_film` at the same 2 epochs /
   seed 0: per-sample nRMSE must agree to <= 1e-9. This is the proof that the
   loss code, when off, is byte-equivalent to the anchor path.
2. **All five arms** on `--datasets panel --epochs 2 --seed 0` (~1.5–2 min/arm on
   H100; panel @200 epochs = 36.6 min, guard @2 epochs = 0.8 min in the ledger).
   Records: finite loss, no NaN/inf predictions, per-dataset nRMSE, and the
   logged per-sample HF-norm spread `max||y||/min||y||` per dataset (unknown #1).
3. **Guard set** `--datasets guard --epochs 2 --seed 0` with the promoted arm's
   env (§2.3, required before any panel-win claim).

Per ADR 0007 the screen numbers are **plumbing + gross ordering only** and are
recorded in `build_notes`, never in parts 5–7.

### Promotion rule — FIXED BEFORE THE 200-EPOCH SUBMIT

1. **Gate 1 (validity)**: eliminate any arm that crashes, emits non-finite loss
   or predictions, or whose screen geomean over the five *claimable* datasets
   (panel minus `ext__helmholtz_2d`) exceeds **2x** the `A-def` arm's screen
   value on the same run. Threshold is 2x, not 1.5x, because ADR 0007 mandates
   discarding only "clearly-broken/cratered variants, not close calls".
2. **Gate 2 (pre-registered rank order)**: promote the first surviving arm in
   the fixed order **A1a -> A1b -> A2a -> A2b -> A0**. The order is the
   prior-art openness ranking (C-AMP > C-BAND > C-REL) with the more
   conservative member of each pair first. It does NOT depend on screen numbers.
3. **Gate 3 (gross-signal override)**: a lower-ranked survivor displaces the rank
   leader only if its screen 5-dataset geomean is <= **0.5x** the leader's — a
   2x gross difference, beyond coarse-filter tolerance.
4. **If every structured arm (A1a/A1b/A2a/A2b) is eliminated at Gate 1**, A0 is
   promoted and the card is reframed in `build_notes` as a *measurement of
   loss/metric mismatch* — never as a contribution (verdict: C-REL preempted).
5. The card's `recipe.env` names **A1a** as the pre-registered promotion. Any
   Gate-1/Gate-3 deviation is written into `build_notes` with the screen table
   and raised to the orchestrator as an explicit recipe amendment BEFORE submit.
   No post-hoc arm switching after the 200-epoch job starts.

### Expected-outcome arithmetic (all from certified numbers)

M5a's `amplitude_share_of_error` is `1 - rescaled/raw`, so an oracle per-sample
gain would multiply skill by `(1 - share)`:

| dataset | anchor skill | M5a share | oracle skill | oracle delta | floor | claimable? |
|---|---|---|---|---|---|---|
| `sharp__phase_field_crystal_2d` | 11.511 | 0.19 | 9.34 | **2.17** | 1.151 | YES (needs 53% of oracle) |
| `sharp__cahn_hilliard` | 5.533 | 0.139 | 4.76 | **0.77** | 0.553 | YES, tight (needs 72%) |
| `sharp__allen_cahn_2d` | 16.334 | 0.0085 | 16.20 | 0.14 | 1.633 | no |
| `sharp__fisher_kpp_2d` | 4.177 | 0.0015 | 4.17 | 0.006 | 0.418 | no (also info-bounded, M2) |
| `ifc_poisson` | 1.566 | n/a | — | — | 0.240 | N_hf=5; wide, no prior |
| `ext__helmholtz_2d` | 13.817 | 0.865 | 1.87 | 11.95 | **9.695** | **no numeric claim** |

Panel geomean under a pfc+cahn_hilliard-only oracle: multiplicative factor
`(9.34/11.511 * 4.76/5.533)^(1/6) = 0.942`, i.e. 6.703 -> **6.31, delta 0.39 <
the 0.884 floor**. Under the full oracle including helmholtz the factor is 0.674
(6.703 -> 4.52, delta 2.20 > 0.884) — but that geomean win would be ~100%
helmholtz, the s5-B1 trap. **Conclusion: the decidable basis is per-dataset on
pfc and cahn_hilliard; the geomean is a secondary, guarded conjunct.**

Second, unbounded channel: per-sample normalization also re-weights *which
samples* the gradient serves. M2 shows knn10 beats the champion on pfc by 3.045
(> the 1.151 floor) using the same X — i.e. >=3.0 skill of pfc headroom is
reachable by a better estimator of the same map, which is what a loss change is.
This channel is not bounded by the amplitude oracle, and is the reason pfc is
the primary target.

Pre-registered risk (ADR 0012 requires it): on `sharp__allen_cahn_2d`
(headroom 0.14) and `sharp__fisher_kpp_2d` (information-bounded), the objective
change has nothing to win and can lose bulk accuracy. A regression larger than
1.633 / 0.418 there, with pfc/cahn_hilliard gains, is a **trade, not a win**.

## Proposal

- **Category**: `objective-reparameterization` (per-sample shape/gain factorized
  training objective on the champion, architecture fixed)
- **Card type**: `model`
- **Motivation**: prior-art verdict for C-AMP, verbatim: *"Open:
  amplitude/shape-decomposed objective for **multi-fidelity PDE field regression
  scored on unchanged per-sample rel-L2**. No fetched source applies
  gain-invariant training to neural PDE surrogates. Design constraint: full
  scale-invariance is unscoreable under rel-L2 — use a two-term (shape +
  explicit gain) objective, not an invariant one."* Motivated in-repo by s2-B1
  M5a (`amplitude_share_of_error` 0.19 pfc / 0.14 cahn_hilliard, `alpha_mean`
  0.73 / 0.76 — systematic under-gain) against a base family whose training loss
  is `F.mse_loss(pred, Y/max|Y_train|)` under a per-sample norm spread measured
  at 408x on helmholtz.
- **Concrete config**: new family `models_r1/mf_fno_transfer_film_s7loss/`,
  a verbatim copy of `mf_fno_transfer_film` (substrate commit `967562e`) with
  the s5-B1 relocation fix (`REPO_ROOT = HERE.parents[1] / "mf_field" /
  "factory_mffp"`) and RNG-neutral periodic checkpointing. The ONLY behavioural
  delta: `smoke_eval.py:96`'s `loss = F.mse_loss(pred, yb)` becomes
  `loss = LOSS_FN(pred, yb)` where `LOSS_FN` is selected by `MFFP_S7_LOSS`
  (default `mse` -> `F.mse_loss`, byte-identical). Objective applied to both
  the LF-pretrain and HF-finetune stages (`MFFP_S7_STAGES=both`). Five arms
  A1a/A1b/A2a/A2b/A0 as tabulated; contract screen and promotion rule as
  pre-registered above; `recipe.env` names A1a. The family logs per-dataset
  `max||y||/min||y||` (train and test HF) to stdout and to result-JSON `extra`.
- **Recipe**:
```json
{
  "base_family": "mf_fno_transfer_film",
  "base_commit": "967562e2a4e3493515edab36b0fcb23655fce71f",
  "family_dir": "models_r1/mf_fno_transfer_film_s7loss",
  "datasets": "panel",
  "epochs": 200,
  "seeds": [0],
  "env": {
    "MFFP_S7_LOSS": "amp",
    "MFFP_S7_LAMBDA": "4.0",
    "MFFP_S7_STAGES": "both"
  }
}
```
- **Expected outcome**: metric = seed-0 200-epoch per-dataset skill + panel
  geomean vs the certified anchor **6.703** [6.219, 7.102]
  (`state/anchors/s5_tuning.json`), provisional-single-seed.
  pfc 11.511 -> **9.0–11.0** (target delta >= 1.151; oracle bound 2.17, lookup
  headroom 3.045); cahn_hilliard 5.533 -> **4.7–5.6** (target delta >= 0.553;
  oracle bound 0.77); allen_cahn 16.334 -> 15.5–17.0 (null expected, headroom
  0.14 << floor 1.633); fisher_kpp 4.177 -> 4.1–4.3 (null by construction, M2
  information floor); ifc_poisson 1.566 -> 1.4–1.9 (N_hf=5, no prior);
  helmholtz reported **qualitatively only** (floor 9.695). Panel geomean
  6.703 -> **4.5–6.4**, expected to be helmholtz-dominated; the
  leave-helmholtz-out geomean is a mandatory reported cross-check (s5-B1
  precedent) but carries no certified floor and is not a threshold.
- **Expected falsification**: If the promoted arm's seed-0 200-epoch panel run
  improves skill by less than its dataset's certified `min_claimable_effect` on
  BOTH `sharp__phase_field_crystal_2d` (< 1.151, i.e. not <= 10.360) AND
  `sharp__cahn_hilliard` (< 0.553, i.e. not <= 4.980) — the only two panel
  datasets where s2-B1 M5a measured amplitude headroom exceeding the floor
  (oracle deltas 2.17 and 0.77) — and the panel geomean does not improve by
  >= 0.884 with the leave-helmholtz-out geomean also improving (so the geomean
  win is not 100% helmholtz), then the champion's sharp-2D excess error is NOT
  attributable to its global-scaler MSE objective, and the s7_loss lever is
  falsified at the objective level; the trade-off case (pfc/cahn_hilliard gain
  while `sharp__allen_cahn_2d` regresses > 1.633 or `sharp__fisher_kpp_2d`
  regresses > 0.418) is pre-registered as a TRADE, not a win.
- **Anchor reference**: `null` (lever stream — own-stream anchor implicit,
  program.md §4.5).

## Status

- Slot covered: YES (one proposal, 5 ADR-0007 arms on one substrate).
- Skipped: no.
- Reopen candidates resolved: none exist (all six batch-1 cards
  `reopen_candidate: false`; verified by reading each card JSON).
- Immutables self-check: **pass (10/10)** — see below.

## Immutables self-check (positive evidence for each)

1. **Data read-only** — the family calls `load_mf_dataset(ds_dir, split)`
   unchanged from the base copy; the delta is confined to the loss expression
   inside `_train`. No generation script, no `benchmark_42/` or
   `factory_root/data/` write path exists in the proposal, and N_hf is whatever
   the loader returns (5 on ifc_poisson).
2. **Panel + guard set fixed** — recipe `datasets: "panel"` expands from
   `project.yaml panel:` (6 datasets); the screen additionally runs
   `--datasets guard` (`heat_local,fluid,sharp__sod_1d`) unchanged.
3. **Eval layer / spec untouched** — scoring runs through
   `eval/score_panel.py` -> `eval/nrmse.py` with no argument beyond
   `--family_dir/--datasets/--epochs/--seed/--out/--env`; the proposal edits
   only files under `<worktree>/models_r1/`, never `round1/eval/`,
   `project.yaml`, `program.md`, ADRs, or subagent prompts.
4. **One nRMSE definition** — the training objective changes; the scored value
   is still produced by `finalize_and_write(...)` from `pred`/`target` exactly
   as in the base family (`smoke_eval.py:196-205`), carrying the same
   `nrmse_def_hash`. The shape/gain factorization is applied ONLY inside
   `_train`, never to the reported metric.
5. **Contract CLI fixed** — `smoke_eval.py` keeps the six-argument signature
   (`--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed`); every knob
   (`MFFP_S7_LOSS`, `MFFP_S7_LAMBDA`, `MFFP_S7_STAGES`, and for the band arms
   `MFFP_S7_BETA`, `MFFP_S7_KC`) is an env var, and the promoted arm's knobs are
   listed in `recipe.env` so they enter the cache key.
6. **Seeds and tier epochs fixed** — `seeds: [0]` per ADR 0004 strict
   single-seed; screen at `--epochs 2` (contract), the reportable run at
   `--epochs 200` (smoke). No full-tier run is proposed.
7. **Guarded factory surfaces untouched** — the base family is *copied out* of
   `factory_root/models/` into the worktree's `models_r1/`; nothing under
   `factory_root/{eval,baselines,references,scripts,data}/`, `factory.md`, or
   `mf_field/akash/` is written. The s5-B1 worktree proves this pattern works
   (`worktrees/s5_tuning/B1/models_r1/mf_fno_transfer_film_modes/`).
8. **Checkpoint-resume from `<ckpt_dir>/last.pt`** — implemented by copying
   s5-B1's `_train` checkpointing (stage, epoch, model/opt/sched/generator
   state; `worktrees/s5_tuning/B1/models_r1/mf_fno_transfer_film_modes/smoke_eval.py:130-178`).
   All five objectives are stateless functions of the current batch — A1b's
   `lambda_t` is recomputed from detached batch statistics each step — so no
   extra state must be checkpointed and resume is exact.
9. **Falsification threshold vs the noise floor** — pfc threshold **1.151** =
   `state/noise_floor.json["sharp__phase_field_crystal_2d"].min_claimable_effect`
   (1.1511001428346894); cahn_hilliard **0.553** =
   `min_claimable_effect` 0.5533465853654416; geomean **0.884** = the derived
   panel-geomean floor used by s5-B1 and ADR 0011. Trade-off thresholds
   allen_cahn **1.633** (1.633407079448426) and fisher_kpp **0.418**
   (0.41773549950819566) are likewise verbatim floors. `ext__helmholtz_2d`
   (floor 9.695) carries **no numeric claim anywhere in the clause**, per the
   websearcher's item 7.
10. **Not a pre-falsified lever** — nearest is **LF low-mode freezing**
    (`mf_fno_spectral`, "worst on sharp", program.md §5). Difference: that lever
    removes the low modes from the model's degrees of freedom and *substitutes
    the LF field's* low-k content architecturally; arm A2 changes only the
    training-time weight on low-k **HF** error, leaves every mode trainable, and
    is scored identically. Arms A1a/A1b/A0 have no relation to it. The other two
    pre-falsified levers (WNO backbone swap, diffusion prior) are architectural
    and unrelated. This card is also not a re-run of s5-B1 (`modes_cap`), which
    changed spectral capacity, not the objective.
