# Brainstormer Report — Stream `s5_tuning`, Batch 3

**Stream**: s5_tuning · **Batch**: 3 · **Total iterations**: 1 · **Slot filled**: 1/1 ·
**Reopen candidates resolved**: 0 (none exist)

## Slot

- **Category**: `tuning_persample_target_scaler` — per-sample output-target scaling on the
  LF-blind champion lineage (raw HF target), with gradient-clip attribution and
  realized-loss effective-N instrumentation. The RAW-target / LF-blind twin of
  `s2_beyond_copy-B3` (residual-target / LF-consuming).

- **Card type**: `model`

- **Motivation**: s5-B2 part 6 F1 falsified, arithmetically, the story the arm was designed
  around — helmholtz HF-stage effective N is **1.0145/400** under `maxabs` and **1.0179/400**
  under `zscore`, because *"a global scalar divides every sample's energy by the same
  constant"*. B2 part 7 names the only intervention that can move it (*"only a PER-SAMPLE
  scale can"*) and hands B3 the arm that was built, rank-ordered and screened but **never run
  at 200 epochs**: `revin_lf`. B2 part 6 also leaves H3 open in writing: *"whatever
  robustification the outlier-dominated loss received came from the CLIPPER, not from the
  scaler ... Testing this needs training-time instrumentation ... and is a B3 item."*
  The batch-3 prior-art verdict licenses exactly this construction and no more —
  **preempted-but-MF-composition-open** (E1), **oracle-only** (E2), **attribution-open**
  (E3), **application-open** (E4a), **predictor-under-test** (E4b). E1 verbatim, from
  `websearches/s5_tuning/batch_3/report.md`: *"**preempted-but-MF-composition-open** | WNE:
  'a parameter-free wrapper that normalizes the input, applies any backbone, and denormalizes
  the output. We prove every NE function admits this factorization' ... | (i) the statistic
  comes from a **different fidelity's field**, not the sample's own target — unretrieved
  anywhere; (ii) applied to a **raw** (non-residual) target, which is the complement of
  s2-B3's D1; (iii) as a **scaler-only knob**, zero new parameters, inside a few-HF-sample MF
  recipe ...; (iv) **WNE's guarantee does not transfer**: in denoising input and target share
  a space, across a fidelity boundary they do not, so `max|LF_i|`-as-HF-scale-proxy is an
  empirical question (B2 measured helmholtz 3929x -> 1.74x; sharp CV <= 0.0099 = no-op)"*.
  The full five-row verdict block is reproduced verbatim below under
  **Prior-art verdict quoted**.

- **Concrete config**:

  New worktree family `models_r1/mf_fno_transfer_film_scaler_ps`, vendored from
  `worktrees/s5_tuning/B2/models_r1/mf_fno_transfer_film_scaler` @ `a55c788e...` (itself
  `mf_fno_transfer_film` @ `967562e2...`). Network, `F.mse_loss`, optimizer, schedule, batch
  size, epochs and `modes_cap=12` untouched. **Seven env-gated deltas, all defaulting to
  B2's exact behaviour:**

  | # | knob | what it does | default |
  |---|---|---|---|
  | D1 | `MFFP_REVIN_FALLBACK` | scaler used where per-sample LF is unavailable (`smoke_eval.py::_lf_per_sample_scales` returns `None`) | `maxabs` (= B2); card sets `zscore` so A1 == A0 on ifc_poisson |
  | D2 | `MFFP_REVIN_FLOOR_Q` | optional train-quantile floor on the per-sample denominator (s7-B1 M6 rule 1) | `none` (B2's `scalers.py:186` `FLOOR=1e-8` only) |
  | D3 | `MFFP_GRAD_CLIP` | makes the hard-coded `p["grad_clip"]=1.0` (`smoke_eval.py:194`) settable; `off` skips `clip_grad_norm_` | `1.0` |
  | D4 | `MFFP_LOSS_INSTR` | per-batch log of pre-clip global grad-norm, clip-fired flag, and the realized per-sample loss energies -> `n_eff = 1/Sum_i alpha_i^2` (per-batch AND epoch-pooled over all train rows) | `0` |
  | D5 | `MFFP_ORACLE_PERSAMPLE` | arm A4: train with per-sample TRUE target scales; writes `splits.ref_oracle_persample` (true test scale, LEAKED) **and** `splits.test` (fallback global constant, legal, pre-registered to be worse) | `off` |
  | D6 | `MFFP_ARM_TAG` | explicit ckpt/arm isolation key, added to the resume config-match gate | derived (B2 behaviour) |
  | D7 | `MFFP_DUMP_PREDS`, `MFFP_DUMP_PER_SAMPLE` | `preds_test.npz` + per-sample rel-L2 columns for every arm (B1/B2 precedent) | `0` |

  **Datasets (4 of the 6 panel sets) — the eligibility 2x2 of B2 F7:**

  | dataset | G | pattern verdict | `revin_lf` real? | role |
  |---|---|---|---|---|
  | `ext__helmholtz_2d` | 39.47 | WEAK_PATTERN 0.402 | YES (cv 0.689, p95/p5 1.744) | diagnostics host; REPORT-ONLY |
  | `ifc_poisson` | 9.858 | REAL_PATTERN 0.994 | **NO** (`revin_lf_available=false`) | PRIMARY numeric leg, carried by A4 |
  | `sharp__cahn_hilliard` | 1.322 | REAL_PATTERN 0.735 | no-op (cv 0.0024) | control: pattern WITHOUT G |
  | `sharp__fisher_kpp_2d` | 5.997 = 1.55 x 3.88 | LEVEL_ONLY 0.0024 | no-op (cv 0.0100) | control: G WITHOUT pattern |

  pfc and allen_cahn (the redundant low-G/dead-pattern cell) are dropped: B2 closed sharp-2D
  for normalization at high confidence and they cost 680 s/arm. **Consequence stated up
  front: this card computes NO panel geomean and makes NO panel-level claim.**

  **Arms (ADR 0007; promotion rank pinned BEFORE submit):**

  | rank | arm (`MFFP_ARM_TAG`) | scaler | clip | datasets | role | promotable |
  |---|---|---|---|---|---|---|
  | — | **A0** `A0_zscore_ctrl` | `zscore` | 1.0 | all 4 | paired control in the SAME 200-ep job (same node/seed/code_hash) + B2-continuity gate | **never** |
  | **1** | **A1** `A1_revin_lf` | `revin_lf` (fallback `zscore`) | 1.0 | all 4 | **THE CANDIDATE — scored arm** | yes (pinned) |
  | 2 | **A5** `A5_revin_lf_floorq25` | `revin_lf` + `FLOOR_Q=0.25` | 1.0 | screen only unless A1 broken | s7-B1 M6 denominator-floor variant | yes |
  | — | **A2** `A2_zscore_noclip` | `zscore` | `off` | helm, poisson | H3 leg (global scaler, clip off) | **never** |
  | — | **A3** `A3_revin_lf_noclip` | `revin_lf` | `off` | helm, poisson | H3 leg (per-sample scaler, clip off) | **never** |
  | — | **A4** `A4_ref_oracle_persample` | `oracle_y` (`s_i = max\|Y_i\|`) | 1.0 | all 4 | **ORACLE** headroom bound; HF test enters ONLY `splits.ref_oracle_persample` | **never** (`ref_*`, leakage-fenced) |

  *Broken* := crash / non-finite metric / contract-tier 4-dataset geomean > 3.0x A0's on the
  same screen run. Close calls never reorder. Screen numbers live in `build_notes` only.

  **Mandatory instrumentation (all zero extra GPU):**
  1. `n_eff` of the realized per-batch loss (D4), per stage per dataset: per-batch value and
     epoch-pooled value over all train rows, epoch-1 and final-epoch median. *Cite the
     formula* `n_eff = 1/Sum_i alpha_i^2` (https://alex.smola.org/posts/40-effective-sample-size/),
     *claim only the application.*
  2. `clip_rate` = fraction of optimizer steps with pre-clip `||g||_2 > 1.0`, plus the
     grad-norm quantiles, per stage per dataset.
  3. `tools/dc_pattern_split.py` on every arm's `preds_test.npz` (level rel-err / pattern-only
     nRMSE / DC share), tabled next to the five existing ifc_poisson rows — this is the
     double-count attribution instrument.
  4. `tools/paired_arm_displacement.py` A1-vs-A0 and A4-vs-A0 (score movement and function
     movement are nearly uncorrelated on this panel — B2 F8).
  5. `tools/target_range_placement_audit.py` before the run (G, tail x pedestal, per-sample
     denominator spread) with a **tripwire**: abort and report if
     `min_i s_i / median_i s_i < 0.01` on any dataset.
  6. Per-sample rel-L2 columns for all arms (mean / median / top-decile share / test-side
     effective N) — the train-space/score-space separation instrument.

- **Recipe**:

```json
{
  "base_family": "mf_fno_transfer_film_scaler",
  "base_commit": "a55c788eec97683061b8a049610de59377cfd332",
  "family_dir": "models_r1/mf_fno_transfer_film_scaler_ps",
  "datasets": "ext__helmholtz_2d,ifc_poisson,sharp__cahn_hilliard,sharp__fisher_kpp_2d",
  "epochs": 200,
  "seeds": [0],
  "env": {
    "MFFP_TARGET_SCALER": "revin_lf",
    "MFFP_MODES_CAP": "12",
    "MFFP_REVIN_FALLBACK": "zscore",
    "MFFP_REVIN_FLOOR_Q": "none",
    "MFFP_GRAD_CLIP": "1.0",
    "MFFP_ARM_TAG": "A1_revin_lf",
    "MFFP_ORACLE_PERSAMPLE": "off",
    "MFFP_REF_SPLITS_ARE_REF_ONLY": "1",
    "MFFP_LOSS_INSTR": "1",
    "MFFP_INSTR_OUT": "/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch_outputs/round1/s5_tuning/B3/instr",
    "MFFP_DUMP_PREDS": "1",
    "MFFP_DUMP_PER_SAMPLE": "1",

    "_note": "keys prefixed _ are card directives, NOT passed to --env. The --env set for the scored arm is exactly the 12 unprefixed keys above. score_panel.py:238 uses --env nargs='*' with NO append, so a second --env REPLACES the first: pass every knob in ONE invocation (s5-B2 builder note, verified).",

    "_arms": [
      {"tag": "A0_zscore_ctrl",          "MFFP_TARGET_SCALER": "zscore",   "MFFP_GRAD_CLIP": "1.0", "MFFP_ORACLE_PERSAMPLE": "off",      "datasets": "ext__helmholtz_2d,ifc_poisson,sharp__cahn_hilliard,sharp__fisher_kpp_2d", "promotable": false},
      {"tag": "A1_revin_lf",             "MFFP_TARGET_SCALER": "revin_lf", "MFFP_GRAD_CLIP": "1.0", "MFFP_REVIN_FALLBACK": "zscore",      "datasets": "ext__helmholtz_2d,ifc_poisson,sharp__cahn_hilliard,sharp__fisher_kpp_2d", "promotable": true},
      {"tag": "A2_zscore_noclip",        "MFFP_TARGET_SCALER": "zscore",   "MFFP_GRAD_CLIP": "off", "MFFP_ORACLE_PERSAMPLE": "off",      "datasets": "ext__helmholtz_2d,ifc_poisson", "promotable": false},
      {"tag": "A3_revin_lf_noclip",      "MFFP_TARGET_SCALER": "revin_lf", "MFFP_GRAD_CLIP": "off", "MFFP_REVIN_FALLBACK": "zscore",      "datasets": "ext__helmholtz_2d,ifc_poisson", "promotable": false},
      {"tag": "A4_ref_oracle_persample", "MFFP_TARGET_SCALER": "oracle_y", "MFFP_GRAD_CLIP": "1.0", "MFFP_ORACLE_PERSAMPLE": "ref_only", "datasets": "ext__helmholtz_2d,ifc_poisson,sharp__cahn_hilliard,sharp__fisher_kpp_2d", "promotable": false},
      {"tag": "A5_revin_lf_floorq25",    "MFFP_TARGET_SCALER": "revin_lf", "MFFP_GRAD_CLIP": "1.0", "MFFP_REVIN_FLOOR_Q": "0.25",         "datasets": "screen_only", "promotable": true}
    ],
    "_promotion_rank": "A1_revin_lf,A5_revin_lf_floorq25",
    "_promotion_rule": "pinned_rank1_unless_broken__broken=crash|nonfinite|screen_4dataset_geomean_gt_3x_A0; close calls never reorder; promoted identity written into the card BEFORE submit (ADR 0007)",
    "_screen": "contract tier, 2 epochs, seed 0, ONE job: all six arms x the 4 card datasets; PLUS (a) A0 default-equivalence vs s5-B2's contract-tier zscore on ext__helmholtz_2d,ifc_poisson; (b) --datasets guard (heat_local,fluid,sharp__sod_1d) with the promoted env; (c) A1-vs-A0 bit-identity assertion on ifc_poisson (fallback == control); (d) a checkpoint-resume demonstration (kill + resubmit) on ifc_poisson. Screen numbers are NEVER reportable (ADR 0007) and live in build_notes only.",
    "_scored_arms_200ep": "A0_zscore_ctrl,A1_revin_lf,A2_zscore_noclip,A3_revin_lf_noclip,A4_ref_oracle_persample",
    "_ref_splits": "ref_oracle_persample (A4 only) — leakage-fenced, never leaderboard-eligible, labelled ORACLE in every table",
    "_design": "ONE SLURM job, seed 0; five score_panel.py calls in arm order, each with its own --env and its own ROUND1_EVAL_RESULTS=<outputs>/eval/results_<tag>; ckpt root shared, per-arm subdir keyed by MFFP_ARM_TAG so arms never cross-load. Idempotent + resumable (slurm_rules §5).",
    "_source": "vendor from worktree round1/exp-s5_tuning-B2 @ a55c788eec97683061b8a049610de59377cfd332, path models_r1/mf_fno_transfer_film_scaler (files: INSPIRATION.md, manifest.json, model.py, scalers.py, smoke_eval.py), renamed to models_r1/mf_fno_transfer_film_scaler_ps. factory_root/{eval,baselines,references,scripts,data}, factory.md and akash/** are never touched.",
    "_cost": "B2 train_seconds @200ep/H100: helmholtz 180.85, ifc_poisson 35.61, cahn_hilliard 491.63, fisher_kpp 496.32 => 1204.4 s per 4-dataset arm. 3 full arms (A0,A1,A4) + 2 two-dataset arms (A2,A3 @216.5 s) = 4046 s = 67.4 min train; +2% wall overhead (B2 precedent 1922 s wall / 1885 s train) => ~69 min."
  },
  "sbatch": {
    "main": {
      "script": "scripts/01_train_eval.sh",
      "submitted_by": "scripts/submit.sh (ORCHESTRATOR invokes; the builder never submits)",
      "job_name": "r1-s5_tuning-B3-s0",
      "partition": "gpu",
      "gres": "gpu:h100:1",
      "nodes": 1,
      "ntasks": 1,
      "cpus_per_task": 4,
      "mem": "32G",
      "time": "03:00:00",
      "requeue": true,
      "exclude": "hpc-93-36",
      "output": "/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch_outputs/round1/s5_tuning/B3/slurm/%x_%j.out",
      "error": "/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch_outputs/round1/s5_tuning/B3/slurm/%x_%j.err",
      "directives_verbatim": "#SBATCH --job-name=r1-s5_tuning-B3\n#SBATCH --partition=gpu\n#SBATCH --nodes=1\n#SBATCH --ntasks=1\n#SBATCH --cpus-per-task=4\n#SBATCH --gres=gpu:h100:1\n#SBATCH --mem=32G\n#SBATCH --time=03:00:00\n#SBATCH --requeue\n#SBATCH --exclude=hpc-93-36\n#SBATCH --output=/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch_outputs/round1/s5_tuning/B3/slurm/%x_%j.out\n#SBATCH --error=/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch_outputs/round1/s5_tuning/B3/slurm/%x_%j.err",
      "time_basis": "67.4 min measured-train + 2% overhead (s5-B2 job 66056499: 32.03 min wall for 1885 s train on hpc-33-13 H100 80GB); 03:00:00 gives 2.6x headroom for a preemption + resume cycle"
    },
    "screen": {
      "script": "scripts/00_screen.sh",
      "submitted_by": "scripts/submit_screen.sh",
      "job_name": "r1-s5_tuning-B3-screen",
      "partition": "gpu",
      "gres": "gpu:h100:1",
      "cpus_per_task": 4,
      "mem": "32G",
      "time": "00:40:00",
      "requeue": true,
      "exclude": "hpc-93-36",
      "output": "/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch_outputs/round1/s5_tuning/B3/slurm/%x_%j.out",
      "error": "/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch_outputs/round1/s5_tuning/B3/slurm/%x_%j.err",
      "time_basis": "2-epoch contract tier; s5-B2's 5-arm 6-dataset screen (job 66024808) plus guard fitted well inside 40 min"
    },
    "seeds_2_3": {
      "script": "scripts/submit_seeds_2_3.sh",
      "note": "written for the end-of-round top-3 confirmation ONLY; NOT invoked in-round (ADR 0004 strict single seed)"
    }
  }
}
```

- **Expected outcome** (seed 0, 200 ep, `provisional-single-seed`, PRIMARY basis = the paired
  in-job A0; SECONDARY = s5-B2 part-5 and s5-B1's H100 same-hardware maxabs control):

  | leg | metric | prediction | vs floor |
  |---|---|---|---|
  | **A4 oracle, ifc_poisson** (PRIMARY numeric) | `ref_oracle_persample` skill | **NULL**: 1.097–1.194 (nRMSE 0.0395–0.0430) — the amplitude channel here is measured at 0.0027 nRMSE = **0.31x floor** (s1-B3 pt 7 note 2). Bar to declare the branch alive: **<= 0.945** | bar implies 0.240106 > floor **0.239908** (1.0008x) |
  | **A1, ifc_poisson** | skill | **bit-identical to A0** (fallback = `zscore`; `revin_lf_available=false`) — a plumbing proof, not a result | n/a |
  | **A1, cahn_hilliard** | skill | NEUTRAL inside **[4.903873, 6.011873]** around A0's 5.457873 | band 0.554 > floor **0.553347**; 2.888x the seed spread 0.191827 |
  | **A1, fisher_kpp** | skill | NEUTRAL inside **[3.800984, 4.636984]** around A0's 4.218984 | band 0.418 > floor **0.417735**; 4.554x the spread 0.091789 |
  | **A1, helmholtz** | rel. nRMSE vs A0 | −40% to +25% (central: modest improvement; B2 F3 showed 91.6% of the zscore gain was amplitude calibration, which the LF proxy supplies at 1.74x residual spread) | **NO threshold**: 5.766462 − 9.694961 = **−3.928500 < 0**, so no attainable value clears the floor. REPORT-ONLY, descriptive |
  | **headline diagnostic** | helmholtz HF-stage epoch-pooled `n_eff` | A0 **~1** (B2: 1.0145/400 maxabs, 1.0179/400 zscore); A1 and A4 **>= 50** of 400 | 49x margin against a quantity B2 measured to 4 dp under both scalers |
  | **H3** | helmholtz HF-stage `clip_rate` | unmeasured anywhere; both signs pre-registered (see falsification (d)) | counted over >= 5000 steps |
  | panel geomean | — | **not computed** (4-dataset subset); no panel-level claim | — |

  Wall clock: ~69 min for the main job, ~10 min for the screen.

- **Expected falsification** (one sentence, then the legs): *H-s5B3 — "on the LF-blind
  champion lineage a per-sample output-target scale taken from the sample's own LF field
  repairs the effective N of the realized per-batch loss where the dataset is eligible
  (`G >= 8` AND a live pattern channel), and that repair, not `grad_clip=1.0`, is what
  produces target-scaler score movement" — is FALSIFIED at 200 epochs / seed 0 if ANY of:*

  **(a) PRIMARY / ifc_poisson bar.** A4's `ref_oracle_persample` skill fails to reach
  **<= 0.945** (nRMSE **<= 0.034020**; equivalently **<= A0_in-job − 0.240**; against the
  certified batch-0 anchor 1.565633 the bar is **<= 1.325527**). Implied improvement 0.240106
  **> floor 0.239908 (1.0008x)**. A failure here retires the per-sample target-scaler branch
  on `ifc_poisson` round-wide for this substrate; a pass says the headroom exists and the
  blocker is *scale prediction*, which s5 may not build (E2) — hand to `s2_beyond_copy-B3` /
  `s1_poisson`.

  **(b) ASYMMETRY / eligibility rule (E4b, predictor under test).** Either ineligible control
  moves beyond its band **in EITHER direction** — `sharp__cahn_hilliard` outside
  **[4.903873, 6.011873]** (band 0.554 > floor 0.553347) or `sharp__fisher_kpp_2d` outside
  **[3.800984, 4.636984]** (band 0.418 > floor 0.417735). A favourable move counts as
  falsification: a gain where `G` is 1.32 (pattern without G) or where the pattern channel is
  dead (G without pattern) means the lever is not what the rule says it is.
  *Implementation-validity sub-prediction (directional, not a claim):* because
  `hf_lf_ratio_cv` is 0.0024 / 0.0100 there, A1's per-sample scale is constant to <1% and A1
  should sit nearer s5-B1's same-hardware **maxabs** control (5.562725 / 4.116518) than A0's
  zscore values (5.457873 / 4.218984); both gaps are inside the floors.

  **(c) MECHANISM / effective N (E4a).** A1's helmholtz HF-stage epoch-pooled `n_eff` stays
  **< 10** of 400 — i.e. `max|LF_i|` does not track per-sample HF energy across the fidelity
  boundary, exactly the transfer WNE's proof does **not** cover. Two-sided and both
  informative: `n_eff >= 50` **with** helmholtz relative nRMSE change **< 10%** vs A0 is the
  decisive negative — the loss-concentration repair is real and buys nothing, which retires
  "de-concentrate the MSE" as an explanation round-wide for this substrate and tells
  `s7_loss` what its `rel` arm is worth before it lands.

  **(d) H3 / clip attribution (E3, both signs pre-registered).**
  *H3-TRUE* if helmholtz HF-stage `clip_rate(A0) >= 0.50` AND the clip-off control A2's
  helmholtz nRMSE regresses to **>= 4.183881** (= 1.899761 + 0.5 x (6.4680 − 1.899761), i.e.
  it gives back >= 50% of A0's gain over s5-B1's same-hardware maxabs control) — then s5-B2's
  headline is re-attributed to the clipper as a Huberised loss
  (https://arxiv.org/html/2412.08941v4), not to the scaler.
  *H3-FALSE* if `clip_rate < 0.05` in both A0 and A1, or A2 reproduces A0 within 10%
  relative — the fetched precedent where clipping *"does not improve the performance"* while
  normalization *"improves significantly"* (https://ar5iv.labs.arxiv.org/html/1707.06799).
  Caveat carried verbatim into the card: 2206.07136's threshold-redundancy result
  (*"eta_effective = eta·R"*, R *"cancels out"*) is for **per-sample** DP clipping; ours is a
  **whole-batch** norm clip, so it is an argument, not a theorem about our recipe.

  **(e) REPORT-ONLY arithmetic.** `ext__helmholtz_2d` carries no numeric threshold anywhere in
  this card because `5.766462 − 9.694961 = −3.928500 < 0`: no attainable skill clears its
  floor. Every helmholtz number is descriptive (relative reduction vs the paired A0).

  **(f) TRAIN-SPACE / SCORE-SPACE CONFOUND — mandatory part-4 statement.** From the E-verdict
  retrieval: *"training via backpropagation in the normalized space yields better models ...
  even when evaluating with the non-normalized MSE"* and *"normalizing by instance on certain
  stationary datasets might be detrimental"* (https://arxiv.org/html/2603.11869). Our scored
  metric is the frozen per-sample rel-L2 on the RAW field, so a per-sample scaler shifts
  **which samples the optimizer serves relative to the metric**; any A1 gain may be
  metric-realignment rather than a representational change. Separation instruments: per-sample
  rel-L2 distributions (mean / median / top-decile share / test-side effective N) for A0 vs
  A1, `tools/paired_arm_displacement.py`, and the cross-stream comparator — `s7_loss-B2` is
  running `MFFP_S7_LOSS=rel` on this SAME champion family, i.e. the per-sample **weighting**
  half with the output space unchanged, so **A1 minus s7-B2's `rel` isolates the PLACEMENT
  half**. A4's legal `splits.test` readout (per-sample-trained, globally denormalized) is
  pre-registered to be WORSE than A0 — that is the controlled statement of E2's point that
  the arm is unusable without a per-sample test statistic.

  **(g) ifc_poisson DOUBLE-COUNT ATTRIBUTION — pre-stated for the round report.**
  On `ifc_poisson` (HF DC energy share **0.6928**, constant-field oracle 0.51327),
  `s1_poisson-B3`'s gain head and this card's scaler act on the SAME level channel, and s1's
  head strictly dominates it: level rel-err **0.008792** (s1 head) vs **0.011486** (s5-B2
  zscore), pattern-only **0.052198** vs **0.090934**. s1-B3 part 7 note (1) already rules
  *"The round report must NOT count them as two stackable ifc_poisson levers"*.
  Therefore: **(1)** part 5 MUST table `nRMSE / level rel-err / pattern-only nRMSE / DC share`
  for every arm via `tools/dc_pattern_split.py`, alongside the five existing rows — s1 base
  0.034264/0.024023/0.058118, s1 head 0.024970/0.008792/0.052198, s1 self_only
  0.021913/0.008809/0.044650, s5-B1 maxabs 0.047483/0.024773/0.090870, s5-B2 zscore
  0.042664/0.011486/0.090934. **(2)** If an s5-B3 ifc_poisson move is LEVEL-dominated
  (>= 50% of removed squared-error energy in the DC term, or `Delta level rel-err` >= 50%
  relative), it is the SAME axis; the round report credits the axis **once, to
  `s1_poisson-B3`**, and records s5-B3 as a substrate-independent replication on an LF-blind
  family — never as an additive gain. **(3)** Only if the move is PATTERN-dominated (level
  rel-err flat within ±10% relative while pattern-only nRMSE falls) may s5-B3 be credited
  separately; this is the discriminator precisely because s5-B2's zscore left pattern-only
  flat (0.090870 -> 0.090934). **(4)** No summing: the round report quotes the single best
  ifc_poisson number (currently s1-B3 `self_only__none` **0.021913**, skill 0.608694, already
  below the ADR-0002 paper bar) with axis attributions beneath it; s5-B3 never claims progress
  toward success criterion 1. **(5)** A4's oracle readout is labelled LEAKED in every table.

- **Prior-art verdict quoted** (verbatim, `websearches/s5_tuning/batch_3/report.md`):

  > **E1** — arm A3 `revin_lf` at 200 epochs: per-sample de-normalization of the **raw HF
  > target** by a scalar statistic of the **LF input field** (`s_i = max|LF_i|`), scaler-only,
  > zero new parameters, across an LF-pretrain -> HF-finetune boundary | **preempted-but-MF-
  > composition-open** | WNE: *"a parameter-free wrapper that normalizes the input, applies
  > any backbone, and denormalizes the output. We prove every NE function admits this
  > factorization"*, NE = `f(ay+b1)=af(y)+b1` — https://arxiv.org/abs/2605.08193
  > (`iteration_1.md`). MORPH: *"normalize the data and cache the corresponding means and
  > standard deviations, then use these statistics to exactly denormalize model outputs"* —
  > https://arxiv.org/html/2509.21670v3 (`iteration_1.md`). RevIN construction +
  > inference-available statistics — https://arxiv.org/html/2603.11869 (`iteration_5.md`).
  > APEX = learned coarse operator + flow-matching enhancer, **not** a scaler —
  > https://arxiv.org/abs/2605.26732 (`iteration_2.md`). MF survey silent on per-sample
  > functional-output scaling — https://ar5iv.labs.arxiv.org/html/2408.17075
  > (`iteration_5.md`) | (i) the statistic comes from a **different fidelity's field**, not
  > the sample's own target — unretrieved anywhere; (ii) applied to a **raw** (non-residual)
  > target, which is the complement of s2-B3's D1; (iii) as a **scaler-only knob**, zero new
  > parameters, inside a few-HF-sample MF recipe whose own survey leaves field magnitude *"to
  > each surrogate's implicit assumptions"*; (iv) **WNE's guarantee does not transfer**: in
  > denoising input and target share a space, across a fidelity boundary they do not, so
  > `max|LF_i|`-as-HF-scale-proxy is an empirical question (B2 measured helmholtz 3929x ->
  > 1.74x; sharp CV <= 0.0099 = no-op)

  > **E2** — LF-free per-sample-scale arm on the raw target (`s_i = max|Y_i|`) | **preempted
  > (cite)** — and retrieval says the only honest s5-legal form is an **oracle** arm | DAIN:
  > *"per instance normalization is applied using learned scale and offset factors ... but no
  > denormalization module is proposed"*; RevIN's statistics are the observed window's,
  > *"available at inference"* — https://arxiv.org/html/2603.11869 (`iteration_5.md`) ... |
  > Only the framing. `max|Y_i|` is unobservable at test time, so the arm is either an
  > **oracle upper bound** (a measurement — legal, cheap, must be labelled) or needs a scale
  > predictor, which s5-B2's territory ruling and program.md §12.5 both place **outside s5**.
  > Nothing about the *mechanism* is open

  > **E3** — H3: per-batch gradient-norm / clip-rate logging to test whether `grad_clip=1.0`,
  > not the scaler, robustified the dominant helmholtz sample | **preempted (cite)** for the
  > mechanism; **open** for the attribution measurement | ... | Nobody uses **clip rate as the
  > explanatory variable for a target-normalization result** — i.e. nobody asks "was the
  > normalization gain actually the clipper?". Also note the transfer caveat: 2206.07136's
  > redundancy result is for **per-sample** (DP-SGD) clipping, ours is a **whole-batch** norm
  > clip, so it is an argument, not a theorem about our recipe

  > **E4a** — headline metric: **effective N of the realized per-batch loss** | **preempted**
  > as a formula; **open** as this diagnostic | *"n_eff = 1/||alpha||_2^2 = 1/Sum_i alpha_i^2"*,
  > *"a diagnostic control signal"*, and explicitly *"does not discuss loss or gradient
  > concentration during training"* — https://alex.smola.org/posts/40-effective-sample-size/
  > (`iteration_3.md`) ... | Every retrieved use computes ESS from **chosen
  > sampling/importance weights**. Computing it from the **realized per-sample loss energies
  > of an unweighted MSE batch**, as a dataset-pathology diagnostic that a *global* scaler
  > provably cannot move (B2: 1.0145/400 vs 1.0179/400), is unretrieved. **Cite the formula,
  > claim only the application**

  > **E4b** — eligibility rule `G = max|Y_train|/sd(Y_train) >= 8` gated on a live pattern
  > channel | **novel** (narrow), nearest neighbour is the qualitative version of the same
  > claim | *"normalizing by instance on certain stationary datasets might be detrimental"* ...
  > https://arxiv.org/html/2603.11869 (`iteration_5.md`) ... | Everything quantitative: no
  > retrieved source offers a **target dynamic-range statistic as a pre-registered eligibility
  > predictor** for whether a normalization change will act. Given §13.3 (0-for-4) and s5's
  > no-novelty charter, present G as **a predictor under test**, not a contribution

- **Immutables self-check**: **pass (10/10)** — all ten items with positive evidence in
  [iteration_1.md](iteration_1.md) §"Immutables self-check". Nothing flagged; no revision pass
  was required.

- **Anchor reference**: `"s5_tuning-B2"` (program.md §4.5: s5 batches >= 2 re-target the
  current champion card; B2's promoted `zscore` arm IS the champion recipe and is reproduced
  as the paired in-job control A0).

- **Source iteration**: [iteration_1.md](iteration_1.md)

## Reopen candidates

| Candidate | Verdict | Eased conditions | Source iteration |
|---|---|---|---|
| *(none)* — `s5_tuning-B1` and `s5_tuning-B2` are both `status: complete` with `reopen_candidate: false`; this stream has never skipped a slot | n/a | n/a | [iteration_1.md](iteration_1.md) §Status |

## Skipped slot

None.

## Summary table

| Slot | Category | One-liner | Status |
|---|---|---|---|
| s5_tuning-B3 | `tuning_persample_target_scaler` (model) | Run B2's built-but-never-trained `revin_lf` arm at 200 ep with a paired `zscore` control, two clip-off arms and a labelled per-sample ORACLE, on the eligibility 2x2 (helmholtz / ifc_poisson / cahn_hilliard / fisher_kpp) — settling H3 (clip vs scaler), measuring whether a per-sample scale repairs the realized loss's effective N (1.0145/400) and whether the repair buys anything, and bounding the ifc_poisson per-sample branch against a bar of skill <= 0.945 | filled |
