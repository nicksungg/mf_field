# Brainstormer Report — Stream `s5_tuning`, Batch 2

**Stream**: s5_tuning (tuning class, program.md 12.5 — knobs only)
**Batch**: 2
**Total iterations**: 1
**Slot filled**: yes (1 `model` card; ADR 0007 propose-many: 5 arms, 1 promoted)
**Reopen candidates resolved**: 0 of 0 (none exist round-wide)

## Slot

- **Category**: `tuning_target_scaler`
- **Card type**: `model`
- **Motivation**: measure the champion's OUTPUT-TARGET SCALER — the knob
  s5-B1 part 7 named ("*the leading candidate is the NORMALIZATION knob, not
  another capacity knob*") — claiming no novelty, with the verdict placed on the
  datasets whose noise floor permits one. The batch-2 prior-art verdict licenses
  exactly this: row (ii) `preempted` — "*Nothing novel — defensible ONLY as a
  measurement. Open as measurement: no fetched source quantifies
  robust-vs-max-abs **target** scaling in a **multi-fidelity few-shot**
  operator-learning regime; the nearest MF paper does not state its
  normalization at all (https://arxiv.org/html/2511.01830). Territory: **K**,
  unambiguously (two scalars, `smoke_eval.py:136-137`).*" Row (i)
  `preempted-but-MF-composition-open` supplies the per-sample arm's legality
  ruling; row (iii) supplies the stage-consistency control arm. Value framing
  (given s6-B1's LF-consuming geomean 0.2346): clean attribution of the
  amplitude/level channel on the LF-blind champion, plus one env-switchable
  scaler block that transfers to any later family.

- **Concrete config**: worktree family `models_r1/mf_fno_transfer_film_scaler`
  = a copy of `mf_field/factory_mffp/models/mf_fno_transfer_film` at
  `967562e`, with s5-B1's three plumbing deltas (REPO_ROOT fix, knob provenance
  in result-JSON `extra`, periodic `last.pt` + config-match resume gate) and ONE
  behavioural change: the target-scaler block (base `smoke_eval.py:210-211`, and
  the denormalization at `:293`) becomes env-switchable via
  `MFFP_TARGET_SCALER`, default `maxabs` == the anchor path. Network, `F.mse_loss`,
  optimizer, schedule, batch size, epochs and `modes_cap` (held at 12) untouched;
  no learnable affine anywhere; the HF **test** field never enters any scaler.

  | arm | knob value | definition (both stages, denormalized with the same constants) | design-time measured leverage | rank |
  |---|---|---|---|---|
  | A0 | `maxabs` | `s_stage = max(|Y_stage_train|)` (base family) | control + default-equivalence proof | never promoted |
  | A1 | `p995` | `s_stage = pct(|Y_stage_train|, 99.5)`, **no clipping** | `max/p99.5` = 46.5 helm, 1.63 poisson, 1.05-1.26 sharp | 2 |
  | A2 | `zscore` | `mu, sd = mean/std(Y_stage_train)` (= `UnitGaussianNormalizer` at C=1); `pred = f(x)*sd_hf + mu_hf` | `|mean|/sd` = 3.75 fisher_kpp, 1.43 poisson, 1.32 pfc | **1 — default promotion** |
  | A3 | `revin_lf` | per-sample `s_i = max(|LF_i|)`, both stages, `pred_i = f(x_i)*s_i`; `maxabs` fallback + `scaler_fallback: true` where the split ships no LF (ifc_poisson) | 3929x -> 1.74x residual on helm; CV <= 0.0099 on sharp (no-op); unavailable on poisson | 3 |
  | A4 | `shared` | `s = max(|Y_lf_train|)` for BOTH stages (stage-consistency control) | 42.1x poisson, 4.3x helm, <= 1.5% sharp | 4 |

  **Screen (ADR 0007)**: one contract-tier job — 2 epochs, seed 0, all five arms
  x the full panel on H100 (minutes; B1's 200-epoch panel was 36.6 min). Screen
  numbers live in `build_notes` only, never in parts 5-7.
  **Fixed promotion rule (pre-registered; order from the design-time
  measurements, NOT from screen scores)**: promote the highest-ranked arm that is
  not *broken*, broken := crash / non-finite metric / contract-tier panel geomean
  > 3x arm A0's on the same run. Order A2 -> A1 -> A3 -> A4; A0 never promoted;
  close calls never reorder. Promoted identity written into the card before submit.
  **Also at contract tier**: (a) `maxabs` default-equivalence vs the untouched
  factory family on `ext__helmholtz_2d,ifc_poisson`; (b) `--datasets guard` with
  the promoted env; (c) `scripts/precheck_scale_ratio.py` reproducing the
  RevIN conditional-shift pre-check into `notes/precheck_scale_ratio.json`.
  **Free reporting adds**: every panel number alongside
  `tools/dc_pattern_split.py`'s constant-field oracle, citing The Well
  (https://arxiv.org/html/2412.00568); `preds_test.npz` dumped as in B1.
  **Pre-registered dual basis** (B1's `not_resolvable` came from an unfixed
  basis): PRIMARY = certified anchor 6.703 + per-dataset 3-seed means; SECONDARY
  cross-check that cannot flip the verdict = s5-B1's H100 same-hardware cap-12
  seed-0 control (geomean 7.1171).
  **Builder note (verified)**: `score_panel.py:238` uses `--env nargs="*"` with
  no `append`, so a second `--env` REPLACES the first — both knobs in ONE
  invocation: `--env MFFP_TARGET_SCALER=<arm> MFFP_MODES_CAP=12`.

- **Recipe**:

```json
{
  "base_family": "mf_fno_transfer_film",
  "base_commit": "967562e2a4e3493515edab36b0fcb23655fce71f",
  "family_dir": "models_r1/mf_fno_transfer_film_scaler",
  "datasets": "panel",
  "epochs": 200,
  "seeds": [0],
  "env": {"MFFP_TARGET_SCALER": "zscore", "MFFP_MODES_CAP": "12"}
}
```

- **Expected outcome** (arm A2, seed 0, provisional-single-seed, PRIMARY basis):
  `sharp__fisher_kpp_2d` improves by **>= 0.418** skill (4.177 -> <= 3.759;
  pooled `|mean|/sd` = 3.75, `max/sd` = 6.00 — the largest affine change on the
  panel); `ifc_poisson` improves by **>= 0.240** (1.566 -> <= 1.326;
  `|mean|/sd` = 1.43 and `max|Y|` over N_hf = 5 is the noisiest available
  scaler); `sharp__phase_field_crystal_2d` a plausible but unpredicted mover
  (floor 1.151); `sharp__allen_cahn_2d` and `sharp__cahn_hilliard`
  **pre-registered NULL** (`|mean|/sd` = 0.005 / 0.0002 -> scale-only change);
  `ext__helmholtz_2d` likely moves a lot (`max/sd` = 39.5) but is **reported
  qualitatively only** (floor 9.695). Panel geomean expected -0.3 to -0.9,
  probably helmholtz-dominated; a geomean gain that vanishes in the
  leave-helmholtz-out decomposition (anchor LHO 5.842) is recorded as a tail
  artefact, not a win (s5-B1 precedent). **vs the noise floor**: both predicted
  movers are stated AT their certified floors (0.418, 0.240) and every other
  dataset is a null against its own floor; honest prior ~40% that a claimable
  per-dataset improvement lands, with the pre-registered null the single most
  likely outcome — which retires the normalization branch of B1 part 7
  round-wide. Pre-registered RevIN items: no learnable affine ("not beneficial
  in practice"), and the conditional-shift caveat already measured (HF/LF ratio
  CV 0.0017-0.0099 on the four sharp sets, so arm A3 cannot work there).

- **Expected falsification**: if the promoted arm's seed-0 200-epoch panel run
  moves NO non-helmholtz panel dataset beyond its own `min_claimable_effect` in
  either direction (`ifc_poisson` 0.240, `sharp__fisher_kpp_2d` 0.418,
  `sharp__cahn_hilliard` 0.553, `sharp__phase_field_crystal_2d` 1.151,
  `sharp__allen_cahn_2d` 1.633) AND the leave-helmholtz-out panel geomean moves
  by less than 0.884 vs the anchor's 5.842, then the champion's output-target
  scaler is NOT a lever on the panel gap — the amplitude/level channel found in
  s5-B1 is confined to `ext__helmholtz_2d` where the round permits no numeric
  claim, and normalization is retired round-wide as an explanation for the
  sharp-2D DC-predictor collapse.

- **Prior-art verdict quoted**: see Motivation above — row (ii) `preempted`
  ("*Nothing novel — defensible ONLY as a measurement ... Territory: **K**,
  unambiguously (two scalars, `smoke_eval.py:136-137`)*",
  https://scikit-learn.org/stable/auto_examples/preprocessing/plot_all_scaling.html ,
  https://raw.githubusercontent.com/neuraloperator/neuraloperator/main/neuralop/data/transforms/normalizers.py ,
  https://arxiv.org/html/2511.01830); row (i)
  `preempted-but-MF-composition-open` ("*K only if the scale comes from an
  inference-available statistic with zero new parameters*",
  https://arxiv.org/html/2603.11869 , https://seharanul17.github.io/RevIN/ ,
  https://arxiv.org/html/2310.02994v2 , https://arxiv.org/abs/2605.26732);
  row (iii) `novel`-narrow-with-unfavourable-prior ("*expect a null-or-negative
  sign ... Value is as a **control arm***", https://arxiv.org/abs/1603.04779);
  bonus row `preempted` for the constant-field-oracle line
  (https://arxiv.org/html/2412.00568). No novelty is claimed by this card.

- **Immutables self-check**: **pass (10/10)** — each item evidenced in
  `iteration_1.md` (data read-only incl. the LF-statistic scalar and the
  read-only pre-check; panel/guard unchanged with LHO as an additional
  decomposition precedented by B1 part 5; eval layer untouched because the knob
  rides the existing `--env` path at `score_panel.py:238-255`/`:94`; metric via
  `finalize_and_write` with `nrmse_def_hash d3d0ade9...`; six-flag CLI plus two
  recipe-recorded env knobs that enter `code_hash`; contract 2 / smoke 200 /
  seed 0 per ADR 0004; family copied into the worktree, factory surfaces read at
  a pinned commit; `last.pt` resume gate extended with `scaler_mode`;
  thresholds equal to the certified floors with helmholtz excluded; no
  pre-falsified lever re-proposed, `modes_cap` held at 12).

- **Anchor reference**: `"s5_tuning-B1"`

- **Source iteration**: [iteration_1.md](iteration_1.md)

## Reopen candidates

| Candidate | Verdict (retry/drop) | Eased conditions | Source iteration |
|---|---|---|---|
| (none) | n/a — all 10 cards in `experiment_cards/**` carry `reopen_candidate: false`; s5-B1 is `complete` | n/a | [iteration_1.md](iteration_1.md) |

## Operator suggestion — ruled EXCLUDED (recorded, not silently dropped)

The training-free per-sample scale predictor from X (TabPFN in-context
regression, or the kNN degraded form) is excluded from the s5 knob pool for
three reasons, all in `iteration_1.md`:
(1) **Territory** — an auxiliary regressor fitted on the train split and
inserted into the forward path is a second predictor composed with the network
(APEX's construction, which the websearcher found the literature frames as
architecture); the verdict's zero-parameter clause covers statistics of the
sample's own inference-available data, not the fitting algorithm of an auxiliary
model, and TabPFN would import a pretrained transformer's learned weights.
s6/s4 territory, and 12.5's "no new paradigms" independently excludes it.
(2) **Dominated where it matters** — measured leave-one-out kNN-in-X on
`ext__helmholtz_2d`: logRMSE 0.875, pred/true p95/p5 = 14.2 (~2.4x typical
multiplicative error) vs **1.74** for the free LF-field statistic (8x looser),
on the one dataset with amplitude headroom.
(3) **No headroom where it is uniquely usable** — `ifc_poisson` is the only
panel dataset where X reaches and LF does not (test ships `fidelity_64` only),
and there the raw per-sample scale spread is 3.2x with B1 turn 2 measuring
alpha ~ 0.996.
**Handed to s6/s4** with those numbers: any APEX-like amplitude-anchor
composition should read the **LF field**, not X; the kNN form needs no new
dependency and can be screened for free.

## Skipped slot

n/a — slot filled.

## Summary table

| Slot | Category | One-liner | Status |
|---|---|---|---|
| s5_tuning-B2 | `tuning_target_scaler` | Env-switchable output-target scaler on the certified champion: 5 arms {maxabs control, p99.5 no-clip, dataset z-score, per-sample LF RevIN, shared LF/HF} screened at contract tier, z-score promoted to 200 epochs seed 0; verdict on fisher_kpp (0.418) and ifc_poisson (0.240), helmholtz report-only | filled |
