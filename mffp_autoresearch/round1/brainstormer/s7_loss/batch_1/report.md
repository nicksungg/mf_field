# Brainstormer Report — Stream `s7_loss`, Batch 1

**Stream**: s7_loss (lever, ADR 0012) · **Batch**: 1 · **Total iterations**: 1 ·
**Slot filled**: 1/1 · **Reopen candidates resolved**: 0 (none exist)

## Slot

- **Category**: `objective-reparameterization` — per-sample shape/gain factorized
  training objective on the frozen champion architecture (ADR 0007: 5 ranked
  arms, one substrate, contract-tier screen, one promoted 200-epoch run).
- **Card type**: `model`
- **Motivation**: the prior-art verdict row for **C-AMP**
  (`preempted-but-MF-composition-open`), verbatim: *"Open: amplitude/shape-decomposed
  objective for **multi-fidelity PDE field regression scored on unchanged
  per-sample rel-L2**. No fetched source applies gain-invariant training to
  neural PDE surrogates. Design constraint: full scale-invariance is unscoreable
  under rel-L2 — use a two-term (shape + explicit gain) objective, not an
  invariant one."* In-repo, three independent findings collapse onto one line of
  code — F19 (loss != metric), s3-B1's **408x** per-sample ||u|| spread against a
  single global `scaler_hf = 7.38`, and s2-B1 M5a's systematic under-gain
  (`amplitude_share_of_error` 0.19 pfc / 0.14 cahn_hilliard, `alpha_mean` 0.73 /
  0.76) — and that line is
  `mf_fno_transfer_film/smoke_eval.py:96  loss = F.mse_loss(pred, Y/max|Y_train|)`.
  Under a global scaler, MSE's gradient is dominated by large-norm samples while
  the scored metric weights every sample by its own norm.

- **Concrete config**: new family `models_r1/mf_fno_transfer_film_s7loss/`, a
  verbatim copy of `mf_fno_transfer_film` (substrate `967562e`) with (a) the
  s5-B1 relocation fix `REPO_ROOT = HERE.parents[1] / "mf_field" / "factory_mffp"`,
  (b) s5-B1's RNG-neutral periodic checkpointing, and (c) the **only**
  behavioural delta: line 96 becomes `loss = LOSS_FN(pred, yb)` with `LOSS_FN`
  selected by `MFFP_S7_LOSS` (default `mse` -> `F.mse_loss`, byte-identical).
  Applied to both the LF-pretrain and HF-finetune stages (`MFFP_S7_STAGES=both`).
  The family logs per-dataset HF norm spread `max||y||/min||y||` (train + test)
  to stdout and result-JSON `extra` — the unmeasured quantity behind the whole
  mechanism.

  **The algebraic basis** (verified numerically to 4.4e-16 in iteration_1):
  with `g = ||p||/||y||` and `cos = <p,y>/(||p|| ||y||)`,
  `rel_i^2 = (1 - cos_i^2) + (g_i - cos_i)^2` — the **scored metric factorizes
  exactly into a shape term and a gain term**. Both knob families below have the
  control arm as their origin, so every arm difference is attributable to its
  knob alone; and the gain term is always explicit, so no arm is
  scale-invariant (the verdict's binding constraint).

  | rank | arm | env | objective |
  |---|---|---|---|
  | 1 | **A1a** (C-AMP) | `MFFP_S7_LOSS=amp`, `MFFP_S7_LAMBDA=4.0` | `mean[(1-cos^2) + 4(g-cos)^2]` — 4x gain emphasis, the direction M5a's `alpha_mean` 0.73/0.76 implies |
  | 2 | **A1b** (C-AMP, balanced) | `MFFP_S7_LOSS=amp`, `MFFP_S7_LAMBDA=auto` | same, `lambda_t = detach(shape)/detach(gain+1e-8)` clamped [0.25, 64] — loss-magnitude balancing against failure mode (ii) |
  | 3 | **A2a** (C-BAND) | `MFFP_S7_LOSS=band`, `MFFP_S7_BETA=4.0`, `MFFP_S7_KC=8` | per-sample-normalized spectral SE, `kr < k_nyq/8` weighted 4x — exactly M3's dyadic band 0 |
  | 4 | **A2b** (C-BAND, mild) | `MFFP_S7_LOSS=band`, `MFFP_S7_BETA=2.0`, `MFFP_S7_KC=4` | bands 0+1 weighted 2x — hedges over-constraint |
  | 5 | **A0** (C-REL) | `MFFP_S7_LOSS=rel` | `mean_i rel_i^2` — **control**, measurement only |
  | — | **A-def** | env unset | `F.mse_loss` — default-equivalence proof, not an arm |

  Denominators clamped as `transolver_residual/smoke_eval.py:68` already does
  (PDEBench near-zero caveat). By Parseval, A2 at `beta=1` equals A0 exactly.

  **Contract-tier screen** (seed 0, `--epochs 2`, before any submit):
  (1) A-def on `ext__helmholtz_2d,ifc_poisson` must match the untouched factory
  family to <= 1e-9; (2) all five arms on `--datasets panel`
  (~1.5–2 min/arm on H100 — ledger: panel@200 = 36.6 min, guard@2 = 0.8 min);
  (3) `--datasets guard` with the promoted arm's env. Screen numbers go in
  `build_notes` only, never parts 5–7 (ADR 0007).

  **Promotion rule, fixed BEFORE the 200-epoch submit**:
  (1) *Validity gate* — eliminate arms that crash, emit non-finite loss/preds, or
  whose screen geomean over the five claimable datasets (panel minus helmholtz)
  exceeds **2x** A-def's (2x, not 1.5x: ADR 0007 discards only clearly-broken
  variants). (2) *Rank order* — promote the first survivor in the fixed order
  **A1a -> A1b -> A2a -> A2b -> A0**, independent of screen numbers.
  (3) *Gross-signal override* — a lower-ranked survivor displaces the leader only
  at <= 0.5x its screen geomean. (4) If all structured arms die, A0 is promoted
  and the card is reframed as a *measurement of loss/metric mismatch*, never a
  contribution. (5) `recipe.env` names A1a; any deviation is a logged recipe
  amendment before submit — no post-hoc arm switching.

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

- **Expected outcome**: seed-0 200-epoch per-dataset skill + panel geomean vs the
  certified anchor **6.703** [6.219, 7.102] (`state/anchors/s5_tuning.json`),
  labelled `provisional-single-seed`. M5a's `amplitude_share_of_error` is
  `1 - rescaled/raw`, so an oracle per-sample gain multiplies skill by
  `(1 - share)`:

  | dataset | anchor | M5a share | oracle skill | oracle delta | floor | verdict basis |
  |---|---|---|---|---|---|---|
  | `sharp__phase_field_crystal_2d` | 11.511 | 0.19 | 9.34 | **2.17** | **1.151** | PRIMARY (needs 53% of oracle) |
  | `sharp__cahn_hilliard` | 5.533 | 0.139 | 4.76 | **0.77** | **0.553** | PRIMARY, tight (needs 72%) |
  | `sharp__allen_cahn_2d` | 16.334 | 0.0085 | 16.20 | 0.14 | 1.633 | null expected / trade-off watch |
  | `sharp__fisher_kpp_2d` | 4.177 | 0.0015 | 4.17 | 0.006 | 0.418 | null by construction (M2 info floor) |
  | `ifc_poisson` | 1.566 | n/a | — | — | 0.240 | N_hf=5, no prior; predicted 1.4–1.9 |
  | `ext__helmholtz_2d` | 13.817 | 0.865 | 1.87 | 11.95 | **9.695** | **qualitative only, no numeric claim** |
  | **panel geomean** | **6.703** | — | 4.52 (full oracle) | 2.20 | **0.884** | secondary, guarded |

  Predicted: pfc **9.0–11.0**, cahn_hilliard **4.7–5.6**, allen_cahn 15.5–17.0,
  fisher_kpp 4.1–4.3, geomean **4.5–6.4**. A pfc+cahn_hilliard-only oracle moves
  the geomean by just 0.39 (< the 0.884 floor), so a geomean win would be
  helmholtz-dominated — the s5-B1 trap; the leave-helmholtz-out geomean is a
  mandatory reported cross-check (no certified floor, therefore not a threshold).
  A second, oracle-unbounded channel supports pfc as the primary target: s2-B1 M2
  shows knn10 beats the champion there by **3.045** (> the 1.151 floor) using the
  same X — i.e. >= 3.0 skill of headroom is reachable by a better estimator of the
  same map, which is exactly what an objective change is.

- **Expected falsification**: *If the promoted arm's seed-0 200-epoch panel run
  improves skill by less than its dataset's certified `min_claimable_effect` on
  BOTH `sharp__phase_field_crystal_2d` (< 1.151, i.e. not <= 10.360) AND
  `sharp__cahn_hilliard` (< 0.553, i.e. not <= 4.980) — the only two panel
  datasets where s2-B1 M5a measured amplitude headroom above the floor (oracle
  deltas 2.17 and 0.77) — and the panel geomean does not improve by >= 0.884 with
  the leave-helmholtz-out geomean also improving (so the geomean win is not 100%
  helmholtz), then the champion's sharp-2D excess error is NOT attributable to
  its global-scaler MSE objective and the s7_loss lever is falsified at the
  objective level.* Pre-registered trade-off (ADR 0012): pfc/cahn_hilliard gains
  accompanied by an `sharp__allen_cahn_2d` regression > 1.633 or a
  `sharp__fisher_kpp_2d` regression > 0.418 is a **TRADE, not a win**.
  Pre-registered loss-only failure modes to check in parts 5–7
  (https://arxiv.org/html/2511.08753): (i) over-constraint / guard-set collapse,
  (ii) conflicting gradients between the two terms, (iii) a loss cannot repair an
  architectural truncation limit.

- **Prior-art verdict quoted**: from
  `websearches/s7_loss/batch_1/report.md` "## Prior-art verdict", verbatim:
  > **C-AMP** — gain/shape-decomposed (per-sample amplitude-calibrating) objective |
  > **preempted-but-MF-composition-open** | https://ar5iv.labs.arxiv.org/html/1406.2283
  > (Eigen 2014 scale-invariant log loss + oracle-rescale evidence) ;
  > https://arxiv.org/abs/2507.18813 (PDE "scale-consistent" = spatial rescaling,
  > NOT amplitude) | Open: amplitude/shape-decomposed objective for
  > **multi-fidelity PDE field regression scored on unchanged per-sample rel-L2**.
  > No fetched source applies gain-invariant training to neural PDE surrogates.
  > Design constraint: full scale-invariance is unscoreable under rel-L2 — use a
  > two-term (shape + explicit gain) objective, not an invariant one.
  >
  > **C-BAND** — band-weighted objective emphasizing the LOW-k band (fixed or
  > error-adaptive) | **preempted-but-MF-composition-open** |
  > https://arxiv.org/html/2607.19387 (BSP relative per-band energy ratio,
  > loss-only) ; https://ar5iv.labs.arxiv.org/html/2012.12821 (FFL error-adaptive
  > bin weights) ; https://arxiv.org/html/2511.08753 (loss-only FNO spectrogram
  > loss + its failure modes) ; https://arxiv.org/html/2602.19265v1 (survey never
  > treats low-band-dominant error) | Mechanism fully preempted — claim no new
  > loss. Open: the **regime inversion** (all published band losses target high-k
  > under-weighting; our M3 measures low-band-dominant excess with spurious high-k
  > injection) and the **MF composition** (HF stage of an LF->HF fusion model,
  > small N_hf).
  >
  > **C-REL** — per-sample relative-L2 training loss + matching model-selection
  > metric (F19/F20) | **preempted** | https://ar5iv.labs.arxiv.org/html/2010.08895 ;
  > https://arxiv.org/abs/2210.07182 ; https://www.emergentmind.com/topics/pdebench |
  > Nothing novel; in-repo precedent already exists
  > (`transolver_residual/smoke_eval.py:65-69`). Defensible ONLY as a controlled
  > measurement of how much panel gap is loss/metric mismatch. Must never be
  > written up as a contribution.

  Card `prior_art.verdict` should read `preempted-pivoted`; citations = the six
  URLs above (all fetched by the websearcher). **The seven quarantined leads in
  the websearch report's "Unverified leads" section must not appear anywhere.**

- **Immutables self-check**: **pass (10/10)** — full positive evidence in
  `iteration_1.md` section "Immutables self-check". Highlights: (3) only
  `<worktree>/models_r1/` is edited; (4) the factorization lives strictly inside
  `_train`, the reported metric still flows through `finalize_and_write` ->
  `eval/nrmse.py` with the same `nrmse_def_hash`; (8) all five objectives are
  stateless functions of the current batch (A1b's `lambda_t` recomputed from
  detached statistics), so s5-B1's checkpoint/resume transfers exactly;
  (9) every threshold is a verbatim `min_claimable_effect` and helmholtz
  (floor 9.695) carries no numeric claim; (10) nearest pre-falsified lever is
  **LF low-mode freezing** (`mf_fno_spectral`) — that lever removes low modes
  from the model's degrees of freedom and substitutes the LF field's low-k
  content architecturally, whereas A2 only re-weights training-time low-k **HF**
  error with every mode still trainable.

- **Anchor reference**: `null` (lever stream; own-stream anchor implicit,
  program.md §4.5). The numeric anchor used throughout is the certified champion
  panel geomean 6.703 from `state/anchors/s5_tuning.json` (no `s7_loss.json`
  anchor file exists; the s3/s4/s5 anchors are the same certified object).

- **Source iteration**: [iteration_1.md](iteration_1.md)

## Reopen candidates

| Candidate | Verdict (retry/drop) | Eased conditions | Source iteration |
|---|---|---|---|
| _none_ | — | all six existing batch-1 cards carry `reopen_candidate: false` (verified by reading each `experiment_cards/*/batch_1/B1.json`) | [iteration_1.md](iteration_1.md) |

## Skipped slot

Not applicable — the slot is filled.

## Summary table

| Slot | Category | One-liner | Status |
|---|---|---|---|
| s7_loss-B1 | `objective-reparameterization` | Factorize the scored rel-L2 into its exact shape and gain terms and re-weight them (plus an inverted low-k band variant and a rel-L2 control) on the frozen champion; 5 arms screened at contract tier, A1a pre-registered for promotion | filled |
