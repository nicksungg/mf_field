# Brainstormer Report — Stream `s2_beyond_copy`, Batch 2

**Stream**: s2_beyond_copy · **Batch**: 2 · **Total iterations**: 1 ·
**Slot filled**: 1 (`model` card) · **Reopen candidates resolved**: 0 (none exist)

## Slot

- **Category**: `mf_composition / literature-standard LF-residual control vs a training-free
  retrieval floor (benchmark-floor discipline)`

- **Card type**: `model`

- **Motivation**: batch 1 established (F14, and the runtime M1 audit) that **0 of 27 factory
  families read the test split's LF field at inference**, and that a ZERO-PARAMETER rule
  (`copy-LF + mean of the 5 nearest train residuals`, keyed on a 16x16 block-mean signature
  of the test LF field) reaches panel geomean skill **0.7886** against the certified
  champion's **9.6362** (B1 part 6, F6). The batch-2 websearcher's verdict for the obvious
  fix is **`preempted (cite)`**, and its instruction is explicit: "**Propose it as the
  missing literature-standard control**, given batch-1 F14 (0/27 families read the test LF
  field), not as a new model." This card does that, and makes the *discipline* the
  contribution: the trained control is pre-registered against the training-free retrieval
  floor recomputed inside the same scored run (verdict (ii)'s open composition —
  "transferring the **fidelity residual** (`HF-LF`) of retrieved neighbours onto the query's
  **own** coarse field, keyed on the LF solution field, used as a **floor in an MF operator
  benchmark**"), with the hybrid of verdict (iii) as a cheap non-promotable arm. The card
  also carries the mandated correction of batch 1's overclaim: MFFM's **Bilinear**
  no-learning baseline IS copy-LF, so the surviving gap is only that "no fetched source
  *requires* the trained model to beat that baseline, and none reports a dataset class where
  it cannot (our Class B)".

- **Concrete config**: new family `models_r1/s2_lf_residual_control/` (manifest.json +
  smoke_eval.py + model.py + retrieval.py + INSPIRATION.md), substrate copied from
  `mf_fno_transfer_film` (`hidden_channels=64, n_blocks=4, modes_cap=12, batch_size=16,
  lr_pretrain=1e-3, lr_finetune=3e-4, weight_decay=1e-5, grad_clip=1.0, WORK_CAP=256`;
  s5-B1's relocated-import fix `REPO_ROOT = HERE.parents[1] / "mf_field" / "factory_mffp"`).
  One substrate, env-selected arms:

  ```
  LF_up  = interp(field_by_fid[max(lf_fids)] -> 256-capped working grid)   # == eval/panel_data.copylf_prediction
  y_hat  = LF_up + Delta_theta([coords, LF_up (, extra channels)], FiLM(X))
  target = Y_hf - LF_up          (HF train split)
  ```
  `model.py` changes exactly one line of the champion's network — `lift = nn.Conv2d(2 +
  n_extra, hidden, 1)` instead of `nn.Conv2d(2, hidden, 1)` (`mf_fno_transfer_film/model.py:138`)
  — plus a **zero-init final 1x1**, so `Delta_theta == 0` at init and `y_hat == LF_up`
  exactly (copy-LF exactly recoverable; the parameterization verdict (iii) calls open).
  `max(lf_fids)` is mandatory: the champion pretrains on `min(lf_fids)` while copy-LF uses
  `max` (F14).

  **Trained arms (ADR 0007 pool, ranked)**

  | rank | `S2_ARM` | delta |
  |---|---|---|
  | 1 (pinned default) | `lf_resid_fno` | LF_up as the only extra input channel — the literature-standard control |
  | 2 | `lf_resid_fno_ladderpre` | pretrain on the coarse pair (fid1 -> fid2 residual), fine-tune on (fid2 -> fid3); helmholtz has one LF rung and falls back to arm 1 |
  | 3 | `lf_resid_fno_multichan` | all LF fidelities as separate input channels |
  | 4 | `hybrid_retr_resid` | retrieved residual `R_retr` as extra input channel + additive term with scalar `w` init 0 (direction (iii)) |

  **Training-free floors** — emitted as `ref_*` splits + `floor_<dataset>.json`, NEVER as the
  scored `test_hf` split (B1 part 5 `do_not_promote`: a training-free lookup "MUST NOT enter
  any leaderboard, anchor, or top-3 eligibility"):
  `retr_blockmean16_k5` (**required**; must reproduce F6's 0.562 / 0.625 / 0.785 / 1.042 /
  1.062 within `S2_FLOOR_F6_TOL=0.02` or the build flags a data-path divergence),
  `retr_s1grad_k5` (Teweles-Wobus S1 gradient key — AtmoSwing steal),
  `retr_patch_k5` (4x4 tiles, per-tile kNN, cosine-window reassembly — LOCA steal),
  `copylf_identity` (seam: skill 1.0 up to the interpolation-kernel delta vs
  `eval/copylf_baselines.json`), and `blend_trained_retrieval` (post-hoc convex blend of the
  promoted arm with `retr_blockmean16_k5`, weight fit on a 20% held-out slice of the HF
  **train** split, candidate set contains 0).

  **Screen (ADR 0007)**: ONE contract-tier job, `--epochs 2 --seed 0`, the four trained arms
  over the five beyond-copy datasets **and** the guard set (§2.3 requires a guard contract run
  before any panel-win claim; `sharp__sod_1d` is 1-D and takes the pre-registered
  `S2_FALLBACK_NO_TEST_LF=champion` path). Floors are deterministic and computed once in the
  same job. Ledger-based cost: << 5 min GPU (s5-B1 2-epoch 3-dataset guard run = 0.77 min) +
  ~5-15 min numpy (B1's 5-dataset forensics = 0.77 min).

  **Promotion rule** (`S2_PROMOTION_RULE`): promote the pinned rank-1 arm `lf_resid_fno`
  unless the screen shows it CRATERED (crash/NaN, or screen skill > 1.5x the best surviving
  arm's on >= 3 of the 5 beyond-copy datasets); then take the next non-cratered arm in rank
  order. A hybrid arm is promotable ONLY if additionally its screen skill is <= (screen skill
  of `retr_blockmean16_k5`) - 0.05 on >= 2 Class-A datasets, otherwise its screen advantage is
  attributable to its training-free term. Screen numbers are never reportable (ADR 0007); the
  promoted identity is fixed in the card before the 200-epoch submit.

  **Tripwires**: no HF *test* field may enter the prediction path; the LF fidelity's native
  grid must be strictly coarser than HF (immutable 1); retrieval reads residuals from the
  TRAIN split only; identity-path nRMSE must match `eval/copylf_baselines.json` up to the
  declared interpolation-kernel delta. Checkpoint-resume from `<ckpt_dir>/last.pt` keyed on
  (arm, stage, epochs_target, grid).

- **Recipe**:
```json
{
  "base_family": "mf_fno_transfer_film",
  "base_commit": "967562e2a4e3493515edab36b0fcb23655fce71f",
  "family_dir": "models_r1/s2_lf_residual_control",
  "datasets": "ext__helmholtz_2d,sharp__phase_field_crystal_2d,sharp__allen_cahn_2d,sharp__fisher_kpp_2d,sharp__cahn_hilliard",
  "epochs": 200,
  "seeds": [0],
  "env": {
    "S2_ARM": "lf_resid_fno",
    "S2_SCREEN_ARMS": "lf_resid_fno,lf_resid_fno_ladderpre,lf_resid_fno_multichan,hybrid_retr_resid",
    "S2_SCREEN_EPOCHS": "2",
    "S2_SCREEN_DATASETS": "beyond_copy5,guard",
    "S2_SCREEN_CRATER_FACTOR": "1.5",
    "S2_PROMOTION_RULE": "pinned_rank1_unless_cratered__hybrid_requires_learned_margin_0.05_on_2_classA",
    "S2_LF_SOURCE": "dataset_lf_fidelity",
    "S2_LF_FID": "max",
    "S2_LF_CHANNELS": "max_only",
    "S2_TARGET": "residual_hf_minus_lfup",
    "S2_HEAD_INIT": "zero",
    "S2_HIDDEN": "64",
    "S2_BLOCKS": "4",
    "S2_MODES_CAP": "12",
    "S2_FLOOR_ARMS": "retr_blockmean16_k5,retr_s1grad_k5,retr_patch_k5",
    "S2_FLOOR_REQUIRED": "retr_blockmean16_k5",
    "S2_FLOOR_SIG": "16",
    "S2_FLOOR_K": "5",
    "S2_FLOOR_PATCH_TILES": "4",
    "S2_FLOOR_F6_TOL": "0.02",
    "S2_FLOOR_SPLITS_ARE_REF_ONLY": "1",
    "S2_BLEND_HOLDOUT_FRAC": "0.2",
    "S2_BLEND_INCLUDES_ZERO": "1",
    "S2_LEAKAGE_TRIPWIRE": "1",
    "S2_FALLBACK_NO_TEST_LF": "champion",
    "S2_DIAG_OUT": "mffp_autoresearch_outputs/round1/s2_beyond_copy/B2/eval"
  }
}
```

- **Expected outcome**: promoted-arm skill ~**0.40** pfc, ~**0.55** cahn_hilliard, ~**0.8**
  helmholtz (report-only), ~**1.02** allen_cahn, ~**1.03** fisher_kpp -> panel geomean
  **~0.713** (computed from those five), vs the training-free floor **0.7886** (B1 F6) and
  the certified champion **9.6362**; skill < 1 on >= 2 (target 3) beyond-copy datasets, the
  first movement on program.md §1 success criterion 2. Anchor is `skill 1.0 = copy-LF`
  (`state/anchors/s2_beyond_copy.json`), so Δ vs anchor is −0.60 (pfc) / −0.45
  (cahn_hilliard) / +0.02–0.03 (Class B, i.e. no-harm). **Vs the noise floor**: every
  per-dataset improvement over the certified champion clears that dataset's
  `min_claimable_effect` by >= 3.2x (pfc 11.1 vs 1.151100; allen_cahn 15.3 vs 1.633407;
  cahn_hilliard 4.98 vs 0.553347; fisher_kpp 3.15 vs 0.417735; helmholtz 13.0 vs 9.694961),
  and the fine "beat the floor" margins clear the seed spread rescaled to skill ~1.0 by
  6.96x (pfc), 2.02x (cahn_hilliard), 57.7x (allen_cahn), 2.28x (fisher_kpp).

- **Expected falsification**: H-B2 ("a trained operator that receives the real coarse solve
  as an input and predicts the fidelity residual exploits the LF field at least as well as
  the training-free LF-keyed retrieval rule, and correctly no-ops where the residual is
  unlearnable") is FALSIFIED if, at 200 epochs / seed 0, the promoted arm's scored skill is
  not `<= 0.512` on `sharp__phase_field_crystal_2d` (B1-F6 floor 0.562 minus a 0.05 margin =
  6.96x the champion seed spread rescaled to skill 1.0, `0.082643 / 11.511001 = 0.007180`) or
  not `<= 0.555` on `sharp__cahn_hilliard` (floor 0.625 minus 0.07 = 2.02x
  `0.191827 / 5.533466 = 0.034667`) — in which case a trained LF-input residual operator has a
  representation/optimization defect, not an information deficit (B1 part 7: "a trained
  operator that cannot match a 5-NN lookup has a representation or optimization defect, not an
  information one") — OR if it degrades on Class B, i.e. skill `> 1.05` on
  `sharp__allen_cahn_2d` (0.05 = 57.7x its rescaled floor `0.014150 / 16.334071 = 0.000866`)
  or `> 1.05` on `sharp__fisher_kpp_2d` (0.05 = 2.28x `0.091789 / 4.177355 = 0.021973`),
  meaning the LF-input path cannot recover copy-LF where the residual is unlearnable (F13);
  the substrate-sanity leg additionally requires improvement over the certified batch-0
  champion skills by more than each dataset's `min_claimable_effect` (pfc 11.511001 needs
  >= 1.151100, allen_cahn 16.334071 >= 1.633407, cahn_hilliard 5.533466 >= 0.553347,
  fisher_kpp 4.177355 >= 0.417735, ext__helmholtz_2d 13.817290 >= 9.694961); with
  `ext__helmholtz_2d` otherwise REPORT-ONLY (rescaled floor `9.694961 / 13.817290 = 0.701654`
  admits no fine-grained claim), every number labelled `provisional-single-seed` (ADR 0004),
  and the retrieval floors plus the trained+retrieved blend reported as `ref_*` splits that
  are explicitly not leaderboard-eligible (B1 part 5 `do_not_promote`).

- **Prior-art verdict quoted** (verbatim from
  `websearches/s2_beyond_copy/batch_2/report.md`, `## Prior-art verdict` rows (i)–(iii) and
  "For the brainstormer" item 2):

  > **(i)** LF field (max fidelity, interpolated per `panel_data.copylf_prediction`) as an
  > **input channel** to the FiLM-FNO backbone, predicting `hf - lf`, copy-LF added back at
  > output; MF few/moderate-shot | **preempted (cite)** | LRC-FNO
  > https://arxiv.org/html/2606.17733 ("upsampled coarse solution ... concatenated as the
  > input of the Residual-Closure FNO"; "adding the coarse solution and the residual
  > correction"); MFFM https://arxiv.org/html/2605.16118 (residual `u_HF-u_LF` "conditioned
  > on u_LF"; **`FNO-residual` is one of its baselines**; bilinear no-learning baseline
  > reported); Multifidelity DeepONet https://arxiv.org/abs/2204.06684 ("residual learning
  > and input augmentation") | **Nothing at the mechanism level.** Only setting: (a) our LF is
  > a real coarse *consistent* solve (immutable 1) rather than a coarse-network output or a
  > downsample; (b) no retrieved MF/coarse-correction work runs on sharp-interface 2-D
  > phase-field data; (c) the Class-A/Class-B partition (fidelity residual unlearnable on 2/5
  > datasets) is a data finding. **Propose it as the missing literature-standard control**,
  > given batch-1 F14 (0/27 families read the test LF field), not as a new model.
  >
  > **(ii)** The zero-parameter LF-keyed residual transfer (`copy-LF + mean_k[HF_j - LF_j]`,
  > `j` retrieved by LF-field signature) reported as a **training-free floor** a trained model
  > must clear | **preempted-but-MF-composition-open** | AtmoSwing analog method
  > https://gmd.copernicus.org/articles/12/2915/2019/ ...; DeltaPhi
  > https://arxiv.org/pdf/2406.09795 ...; Hybrid-MF overview
  > https://www.emergentmind.com/topics/hybrid-multi-fidelity-models ...; baseline discipline
  > https://arxiv.org/html/2508.05831 ... | Open: transferring the **fidelity residual**
  > (`HF-LF`) of retrieved neighbours onto the query's **own** coarse field, keyed on the LF
  > solution field, used as a **floor in an MF operator benchmark**. Analog methods
  > substitute/average the retrieved fine fields instead; the MF additive-correction corrector
  > is parametric. Reportable **with the analog family cited as its ancestor** — not a novelty
  > claim.
  >
  > **(iii)** Hybrid: trained LF-input residual operator **+** a retrieved-residual term under
  > a confidence/blend weight | **preempted-but-MF-composition-open** | NNTNNR
  > https://arxiv.org/abs/2310.00664 ...; DeltaPhi https://arxiv.org/pdf/2406.09795; image-domain
  > KRF ... | Open: the **multi-fidelity binding** — correction = learned term + retrieved
  > fidelity-residual term over a **real coarse solve**, parameterized so copy-LF is exactly
  > recoverable ... Thin, but the only arguable *mechanism* claim of the three.
  >
  > **Correct an overclaim inherited from batch 1.** Batch 1's prior-art cell said no MF paper
  > baselines against the interpolated LF field. MFFM does: its **Bilinear** no-learning
  > baseline error is "the relative L2 norm of the residual ||delta||/||u_HF||" — copy-LF
  > under another name. The surviving gap is narrower: no fetched source *requires* the
  > trained model to beat that baseline, and none reports a dataset class where it cannot
  > (our Class B).

  The card's `prior_art` cell must carry row (i) as the verdict for the promoted arm, rows
  (ii)/(iii) for the floor and blend arms, and the overclaim correction verbatim.

- **Immutables self-check**: **pass (10/10)** — full positive evidence in
  [iteration_1.md](iteration_1.md) §"Immutables self-check". Nothing flagged; no revision
  pass was needed. Items 9 and 10 in brief: every threshold clears its dataset's floor
  (6.96x / 2.02x / 57.7x / 2.28x on the rescaled floors, >= 7.5x on the absolute
  `min_claimable_effect` legs; helmholtz report-only at rescaled floor 0.701654), and the
  nearest pre-falsified lever is **LF low-mode freezing** (`mf_fno_spectral`), which
  constrains the output spectrum during training while remaining LF-blind at inference (F14)
  — this card leaves the spectrum free and changes the INPUT instead.

- **Anchor reference**: `null` (gap stream; the stream's own anchor `skill 1.0 = copy-LF`
  is implicit — program.md §4.5).

- **Source iteration**: [iteration_1.md](iteration_1.md)

## Reopen candidates

| Candidate | Verdict (retry/drop) | Eased conditions | Source iteration |
|---|---|---|---|
| _none_ — `s2_beyond_copy-B1` is `status: complete`, `reopen_candidate: false`, and is the only prior card in this stream | n/a | n/a | [iteration_1.md](iteration_1.md) |

## Skipped slot

Not applicable — the slot is filled.

## Summary table

| Slot | Category | One-liner | Status |
|---|---|---|---|
| s2_beyond_copy-B2 | mf_composition / literature-standard LF-residual control vs training-free retrieval floor | build the LF-input residual FNO the zoo never had (preempted, cited as the missing control), pre-registered against the zero-parameter LF-keyed retrieval floor (0.7886 panel geomean) recomputed in-run as `ref_*` splits, with an S1-gradient key, a LOCA per-patch key and a copy-LF-recoverable trained+retrieved blend as non-promotable arms | filled |
