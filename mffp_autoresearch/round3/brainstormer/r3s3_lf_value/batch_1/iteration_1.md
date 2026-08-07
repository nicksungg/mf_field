# Iteration 1 — Stream `r3s3_lf_value`, Batch 1

## Design context considered

1. **The stream question (authoritative, `project.yaml` streams + `program.md` section 4)**: "what is LF-at-train worth on the honest panel (coverage/amplitude, ch identifiability-vs-trainability), matched with/without arms at matched procedure?" — note it names *both* the coverage/amplitude accounting and the ch identifiability-vs-trainability discrimination.
2. **Success criterion 2 (`program.md` section 3)**: "A certified matched-arm measurement of LF-at-train value on >= 3 scored datasets under the repaired denominators."
3. **Section 12.3 conventions** (round-2 program, applying verbatim per round-3 section 5) — quoted in `summary_so_far.md` section 2. Candidate mechanisms are LF-consuming-teacher distillation, LF-pretrain -> HF-finetune, and auxiliary MF losses; the nested-ladder degeneracy clause requires the card to state what the LF rungs add that the HF rung does not already contain; existing 400 aligned samples only.
4. **The prior-art verdict**: D1 preempted-but-composition-open (the number, never the genre); D2 preempted-but-composition-open (may not claim the statistical-to-computational-gap concept); D3 preempted (cited baseline only).
5. **The immutables block (section 4.5 of my prompt), held verbatim** — reproduced and answered in the self-check below.
6. **Anchors**: stream anchor / best card on the round-3 panel is `r2s3_lf_train_signal-B3`, per-seed geomeans [15.2085, 15.8527, 15.7065], mean **15.5893**, CI [15.2071, 15.9714], per-dataset mean skill pfc 50.3973 / ac 186.7596 / fk 172.2459 / ch 12.8723 / ifc_poisson 9.5116 / ifc_heat 0.0725 (`state/anchors/launch_anchors.json`, CERTIFIED 2026-08-07). Launch best-floor geomean **36.3912**; cratered threshold 1.5x = 54.5868.
7. **Noise floors**: `state/anchors_repaired/noise_floor.json` is PROVISIONAL (ifc_poisson 0.2399, ac 16.4223, ch 1.1604, fk 158.3322, pfc 8.8595; **no ifc_heat key**). `round2/state/noise_floor.json` is the round-2 certified file (ifc 0.9377041, ac 0.8797047, ch 0.0912454, fk 0.0007137, pfc 0.2130273) but was certified pre-repair. r3s4-B1 re-certifies in parallel with this card.
8. **Per-dataset floors** (`state/anchors_repaired/floors.json`, certified on the repaired panel): best training-free floor per dataset — pfc `train_mean` 48.0773, ac `nn_condition` 475.8568, fk `train_mean` 390.7015, ch `nn_condition` 23.1803, ifc_poisson `nn_condition` 8.0409 (+ mandatory `affine_on_hf_train` 1.5938), ifc_heat `nn_condition` 1.3941 (+ `affine_on_hf_train` 0.9584).
9. **My own pre-flight measurements** (summary section 6a/6b): the affine coverage deficit at N_hf = 5 is now m = 14 (pfc) / 15 (ac) / 46 (fk) / 15 (ch) / 1 (ifc_poisson) / **0 (ifc_heat)**; the ifc ladders are nested (overlap 5 with the HF rung at every rung), leaving 95/45/15 uncovered conditions.
10. **Cost calibration**: B3 ran 33 legs in 55 min wall on one H200 (~1.7 min/leg), so a ~75-leg card is a ~2.5 h job.

## Proposal reasoning

### What the round actually needs from this stream at batch 1

Criterion 2 wants a *certified matched-arm measurement* on >= 3 datasets. The stream question additionally names the ch identifiability-vs-trainability split. B4 closed round 2 by handing forward exactly that question and specifying what it needs: "a rank/identifiability probe on cahn_hilliard's condition design plus at least one HF-budget rung above 5". The rank probe I have already run (summary 6a). The rest is one training card.

The decisive design insight is that **all three questions are answered by the same experiment if the LF row set is partitioned by *condition coverage* rather than by rung**. Information about the condition -> field map at unseen conditions can only come from rows *at* those conditions. So:

- LF rows at conditions that already carry an HF row supply **no new conditions**; on a nested ladder they are a coarsening of a target the arm already has exactly. Any gain from them is an optimisation / multi-resolution-regularisation channel. This is the **trainability** arm.
- LF rows at conditions with **no** HF row supply the null direction of the design. Any gain from them is a supervision/coverage channel. This is the **identifiability/coverage** arm.
- The union is the total +/-LF effect, which is criterion 2's number.

That partition is exactly implementable on this data (nested ladders verified; 395 uncovered conditions on every sharp dataset, 95/45/15 on ifc), costs one extra arm, and is a *matched-procedure* contrast because every arm shares the backbone, optimizer, scaler, step count and RNG order.

### Alternatives weighed and rejected

- **D3, distillation from an LF-consuming teacher.** Rejected as the *contribution*. The verdict is `preempted (cite)` and the websearcher warns "Round-2 batch 1 already returned the same verdict class for this mechanism, so a re-proposal without this framing is a rebadge". Worse, B3's cross-stream note 1 (SCALE-NOT-MAP) prices single-teacher distillation as inheriting one arbitrary member of a set of models that sit 100.5 skill units apart in function space at inter-draw cosine 0.9485. It also needs a teacher family built from scratch — a whole card's build budget for a mechanism the literature already characterises as non-monotone. Deferred to a later batch, where it can ride as a cited arm on top of a measured channel decomposition.
- **Auxiliary MF loss (predict LF and HF jointly from the condition).** Rejected as a *mechanism proposal*: `r2s4_diag-B2` closed this channel — "|T1-T0| below its operative threshold in 15/15 dataset x N cells ... the aux target is a duplicate of the main task, cos >= 0.997". Re-proposing it as a lever would be a self-check-11 failure. It survives in this card only as the **A2 control arm whose predicted value is ~0**, which is the honest use of a closed channel: as the null leg of a decomposition.
- **LF-pretrain -> HF-finetune as the headline.** Rejected: 12.3 makes `mf_fno_transfer_film` the mandatory declared baseline for exactly this shape, and an undifferentiated re-proposal is a reviewer FAIL. It is also confounded — pretraining on the *full* LF pool mixes the coverage channel into the "warm start", so it cannot answer D2. The coverage-partitioned joint-training design isolates the channels that a pretrain/finetune arm blends together; I record the baseline as a *cited* comparator in the card's motivation rather than re-running it.
- **Bigger/deeper decoder, more modes.** Pre-priced as the wrong lever by B3 cross-stream note 3: a zero-parameter 12-mode truncation of the true HF field scores skill 0.09 on pfc and 0.64 on ch while trained arms sit at ~60 and ~12.6 — capacity is not the binding constraint on this panel.
- **Five or more HF-subset draws** (B3's own recommendation, since n = 3 cannot reach p < 0.05 by a sign test on the draw axis). Rejected on cost/robustness grounds *for the draw axis* and replaced by the stronger instrument B4 actually used: a **paired per-test-sample** sign test and bootstrap CI, which has n = 78-128 per leg and does not need extra legs. Draws stay at 3 so that the reproduction seam against B3's certified anchor legs is exact (B3 used seeds 0/1/2 with the same draw rule).
- **Making this a diagnostic card.** Rejected: the channel partition requires *training* arms that do not exist in any shipped dump; a training-free audit cannot produce A2/A3. Turf is also clean — r3s4-B1 is pre-directed to mce/floor certification (`index.md`), so there is no batch-1 collision, and this card claims the +/-LF *optimisation*, per the round-2 division "r2s4 measures, r2s3 optimizes".

### Why the honest panel makes this newly informative

Round 2's version of this contrast ran on a panel where 4 of 6 datasets had **no** affine coverage deficit at N_hf = 5, and B3's structural clause F2 was falsified there. On the honest panel the deficit is m = 14/15/46/15/1/**0** — five of six datasets now have a live coverage channel and `ifc_heat` is the single m = 0 negative control. The card therefore re-runs a *falsified* structural hypothesis on the panel that was built to make it testable, with the added control that its predicted-null dataset is now identifiable in advance.

## Proposal

- **Category**: `lf_value / coverage-vs-optimisation channel decomposition of the matched +/-LF-at-train effect on the completeness-certified panel, with the HF-row-equivalent price`
- **Card type**: `model`
- **Anchor reference**: `null` (round-3 policy: gap/lever/diag streams carry `null`; own-stream anchor `r2s3_lf_train_signal-B3` at geomean 15.5893 is implicit)

### Motivation (quoting the prior-art verdict)

Verbatim from `websearches/r3s3_lf_value/batch_1/report.md`, "## Prior-art verdict", row D1:

> **D1** — matched, budget-matched **+/-LF-at-train** contrast for a condition-only field surrogate on the **completeness-certified** round-3 panel; the deliverable is the certified per-dataset effect in copy-LF skill units (success criterion 2, >= 3 datasets) | **preempted-but-MF-composition-open** | ... | The composition, all four clauses simultaneously: (a) LF **absent from the test path by construction** (stripped view), so the contrast prices LF as *training data*, not as an input; (b) a panel carrying an explicit **completeness certificate** (HF exactly reconstructible from the stored condition) — turn 4 term 2 returned **nothing** in this slot, every retrieved MF-PDE work either keeps LF at inference or never certifies sufficiency; (c) the **copy-LF denominator** ("is the model worth more than running the coarse solve?") plus the ifc `affine_on_hf_train` floor; (d) N_hf = 5 on the ifc ladder with a certified `min_claimable_effect`. **The finding must be the measured number, never the ablation genre.**

and row D2:

> **D2** — decide **identifiability vs trainability** on `sharp__cahn_hilliard` (19-D complete condition): arms where LF can only act as an optimisation aid (LF-pretrain -> HF-finetune, warm start, curriculum) vs arms where LF supplies supervision at conditions with no HF row | **preempted-but-MF-composition-open** | ... | The **discrimination has a name** (statistical-to-computational gap), so the card must not claim the concept. What is open: nobody has run it for *low-fidelity coarse solves as the auxiliary signal on a certified-complete PDE condition vector* ... Note the sharpened stake: B4 measured the no-LF ch arm at median per-sample cosine 0.0003-0.0385 vs the LF arm's 0.962-0.964 — that signature is *local-minimum-like*, which is a prediction the trainability arm can falsify.

Pre-registered expectation, written as inherited theory and **not** as a discovery (websearcher instruction 2): privileged information accelerates the learning rate from O(n^-1/2) to O(n^-1) (Lopez-Paz, Bottou, Scholkopf & Vapnik 2016, `https://leon.bottou.org/publications/pdf/iclr-2016.pdf`, fetched); on a completeness-certified panel LF cannot add information about a target the condition already determines, so any surviving effect must be sample-efficiency/optimisation *or* the finite-sample coverage of the condition space. A certified null or negative is a literature-anchored result (negative transfer: `https://arxiv.org/abs/2410.12690`, fetched; `program.md` section 3 "a certified null is a result").

### Concrete config

New from-scratch-for-round-3 family `models_r3/r3s3_lf_channels`, condition-only at test, stripped view only, no LF tensor constructed on any test path.
Code is a **declared within-stream continuation** vendored with provenance comments from `models_r2/r2s3_coverage_panel` (branch `round2/exp-r2s3_lf_train_signal-B3`, commit dfcd46c6b51b5fe0bd533b9c670a7cdbf9d13830), preserving byte-for-byte: the `CoverageDecoder` backbone (width 64, 4 blocks, coord channels built at forward time, `SpectralConv2d` + 1x1 conv + FiLM(cond) after GroupNorm + GELU, FFT `norm="forward"`), the `pinned_min_rung_nyquist` mode policy, the per-rung `max|y|` scaler, the step-matched budget `steps = epochs x 25`, AdamW(1e-3, wd 1e-5) + cosine + clip 1.0, and the `_step_rng(seed, step)` resume contract (HF batch drawn first, then LF). This preserves an exact **reproduction seam** against B3's certified anchor legs.
**New** (the experiment): the LF row selector is partitioned by *condition coverage*, plus an HF-budget reference rung.

Arms (`R3S3B1_ARM`; each arm is its own `ROUND3_EVAL_RESULTS` dir and `ckpt_dir`):

| arm | HF rows | LF rows | role |
|---|---|---|---|
| `A0_nolf` | N_hf = 5 | none | matched no-LF control |
| `A1_lf_all` | N_hf = 5 | all rungs, all train conditions | **PRIMARY scored arm**; total +/-LF effect (criterion 2); reproduction seam vs B3 |
| `A2_lf_covered` | N_hf = 5 | all rungs, restricted to the 5 conditions that already carry an HF row (15 LF rows) | **optimisation/trainability channel** (no new conditions) |
| `A3_lf_uncovered` | N_hf = 5 | all rungs, restricted to conditions with **no** HF row (sharp 395x3; ifc 95/45/15) | **coverage/identifiability channel** |
| `A3s_lf_uncov_n5` | N_hf = 5 | all rungs, 5 **uncovered** conditions only (15 LF rows) | row-count-matched twin of A2; isolates *where* the LF rows sit from *how many* there are. ch (3 draws) + ifc_poisson + ifc_heat only |
| `A4_hf20_nolf` | N_hf = 20 | none | **budget-varied reference arm** (labelled, never part of the +/-LF contrast): prices LF in HF-row units. Sharp datasets only (the ifc ladders ship exactly 5 HF rows and are untouched) |

Leg grid: 4 sharp x 3 draws x {A0, A1, A2, A3} = 48; 2 ifc x native x {A0, A1, A2, A3} = 8; A3s = 5; A4 = 4 sharp x 3 draws = 12; guard leg (`--datasets guard`, contract tier 2 epochs, arm A1) = 1. **74 legs, one SLURM job, training seed 0** (~2.1 h at B3's measured 1.7 min/leg; request 06:00:00 with `--mail-user=ezeng@caltech.edu --mail-type=END,FAIL`).

Mandatory reported arms on every leg (`program.md` section 2 + section 4.5 item 11): `nn_condition`, `train_mean`, `zero` from `state/anchors_repaired/floors.json` with a `floors_seam_check` at tol 1e-9, plus `affine_on_hf_train` on both ifc datasets and `linear_hfonly`.
Pre-flight, card-level and blocking: (i) `tools/target_scale_spread_audit.py` on `sharp__phase_field_crystal_2d` (ADR r2-0004); (ii) `tools/condition_identifiable_rank.py` and `tools/affine_ladder_voi.py` on `sharp__cahn_hilliard`'s 19-D design (B4's named handoff probes); (iii) a data-binding assertion that `copylf_baselines.json` reference values equal `floors.json` `reference.test_nrmse` (ac 0.0020593576160366327, pfc 0.018257409062703473, ch 0.041802962686225575, fk 0.00016524586579046429, ifc 0.036 / 0.074) — this is the guard against the stale-substrate hazard in summary section 6g.
Score-neutral instrumentation: per-arm LF row/condition manifest with exact overlap counts against the HF draw; per-leg test-prediction dumps (needed for the per-sample cosine/gain split that carried B4's mechanism reading); train/test gap per arm; per-arm loss curves.
Registration: LF lifts use the ADR r2-0001 conventions vendored from `eval/panel_data.py` (inherited unchanged from B3's `R3S3B1_LF_LIFT=match_copylf_convention`); no bare `F.interpolate`.

### Recipe

```json
{
  "base_family": "declared within-stream continuation of models_r2/r2s3_coverage_panel (branch round2/exp-r2s3_lf_train_signal-B3, commit dfcd46c6b51b5fe0bd533b9c670a7cdbf9d13830); vendored with provenance comments. NEW in this card: the coverage-partitioned LF row selector (R3S3B1_LF_COND_SET / _LF_COND_CAP) and the N_hf reference rung. NOT a round-1 family and not a rebadge of mf_fno_transfer_film (which is LF-pretrain->HF-finetune on the full pool; cited as the section-12.3 declared baseline in part 2, not re-run).",
  "base_commit": "9ad78b47dbcc9373b1270bb18deba43ab7adb4ad",
  "family_dir": "models_r3/r3s3_lf_channels",
  "datasets": "sharp__phase_field_crystal_2d,sharp__allen_cahn_2d,sharp__fisher_kpp_2d,sharp__cahn_hilliard,ifc_poisson,ifc_heat",
  "epochs": 200,
  "seeds": [0],
  "env": {
    "R3S3B1_ARM": "A1_lf_all",
    "R3S3B1_SPLIT_SEED": "0",
    "R3S3B1_N_HF": "5",
    "R3S3B1_LF_COND_SET": "all",
    "R3S3B1_LF_COND_CAP": "0",
    "R3S3B1_WIDTH": "64",
    "R3S3B1_BLOCKS": "4",
    "R3S3B1_MODES_CAP": "12",
    "R3S3B1_MODE_POLICY": "pinned_min_rung_nyquist",
    "R3S3B1_SCALER": "per_rung_max",
    "R3S3B1_STEPS_PER_EPOCH": "25",
    "R3S3B1_HF_BATCH": "5",
    "R3S3B1_LF_BATCH": "16",
    "R3S3B1_LR": "1e-3",
    "R3S3B1_WD": "1e-5",
    "R3S3B1_SCHED": "cosine",
    "R3S3B1_CLIP": "1.0",
    "R3S3B1_LAMBDA_LF": "1.0",
    "R3S3B1_LF_LIFT": "match_copylf_convention",
    "R3S3B1_REF_ARMS": "nn_condition_n5,train_mean_n5,zero,linear_hfonly,affine_on_hf_train,nn_condition_full,train_mean_full",
    "R3S3B1_FLOORS_JSON": "/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch/round3/state/anchors_repaired/floors.json",
    "R3S3B1_FLOOR_TOL": "1e-9",
    "R3S3B1_NOISE_FLOOR_JSON": "/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch/round3/state/anchors_repaired/noise_floor.json",
    "R3S3B1_NOISE_FLOOR_R2_JSON": "/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch/round2/state/noise_floor.json",
    "R3S3B1_MCE_MODE": "max_r3provisional_r2certified",
    "R3S3B1_ANCHORS_JSON": "/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch/round3/state/anchors/launch_anchors.json",
    "R3S3B1_DATA_BINDING_ASSERT": "1",
    "R3S3B1_TARGET_SCALE_AUDIT": "1",
    "R3S3B1_LF_ROW_MANIFEST": "1",
    "R3S3B1_DUMP_TRAIN_PREDS": "1",
    "R3S3B1_DUMP_TEST_PREDS": "1",
    "R3S3B1_CKPT_EVERY_STEPS": "250",
    "R3S3B1_GUARD_NSUB": "off",
    "_note": "keys prefixed _ are card directives, NOT passed to --env. The --env set is exactly the 33 R3S3B1_* keys above; each leg overrides only R3S3B1_ARM, R3S3B1_SPLIT_SEED, R3S3B1_LF_COND_SET, R3S3B1_LF_COND_CAP and R3S3B1_N_HF (the guard leg also sets epochs=2). ARM<->selector binding, asserted in smoke_eval: A0_nolf=(N_HF 5, COND_SET none, CAP 0); A1_lf_all=(5, all, 0); A2_lf_covered=(5, covered, 0); A3_lf_uncovered=(5, uncovered, 0); A3s_lf_uncov_n5=(5, uncovered, 5); A4_hf20_nolf=(20, none, 0). smoke_eval MUST raise on any other combination.",
    "_primary_arm": "A1_lf_all is the PRIMARY scored arm for cratered screening (cratered = panel geomean > 1.5 x 36.3912 = 54.5868). A0_nolf, A2, A3, A3s, A4 are matched controls and may legitimately sit above that.",
    "_hf_subset_draws": "SPLIT_SEED in {0,1,2} draws 5 of the 400 HF train rows via np.sort(np.random.default_rng(s).permutation(400)[:5]) -> d0 = 55,88,133,202,293; d1 = 39,45,51,198,379; d2 = 11,157,162,211,355 (identical to r2s3-B3, so the A0/A1 legs form an exact reproduction seam against the certified anchor). ifc_poisson and ifc_heat are native N_hf = 5 -> SPLIT_SEED=native, one leg per arm. A4_hf20_nolf draws 20 rows with the same rule and the same HF batch size 5.",
    "_lf_cond_set": "Computed from exact condition-row matching against the drawn HF conditions. Verified live 2026-08-07 on mffp_autoresearch/round2/stripped_data: sharp datasets are condition-aligned across rungs (400/400), so covered = the 5 drawn conditions and uncovered = the other 395, at every rung; ifc_poisson and ifc_heat ladders are NESTED with overlap 5 of 100 / 5 of 50 / 5 of 20 at rungs 8/16/32, so uncovered = 95/45/15. The manifest must re-derive and record these counts per leg.",
    "_base_commit_rationale": "round3-substrate (8aae33a) is STALE for this card: its round2/eval/copylf_baselines.json predates the ac trim, the pfc crystalline-box swap and the ifc_heat promotion, and it has no ifc_heat entry at all (score_panel.py would raise ScoreContractError). 9ad78b4 is the mffp-trunk-eloise head carrying ADR r3-0002/r3-0003. If the orchestrator prefers to fast-forward round3-substrate, that is equivalent; R3S3B1_DATA_BINDING_ASSERT is the check that decides it either way.",
    "_datasets_note": "NEVER pass --datasets panel: round2/eval/panel_data.py::load_config reads round2/project.yaml, whose panel is the ROUND-2 panel (helmholtz in, ifc_heat out). Always pass the explicit 6-name list. --datasets guard is safe (identical guard set in both configs).",
    "_slurm": "one job, 74 legs, partition gpu, gres gpu:nvidia_h200:1, time 06:00:00, --mail-user=ezeng@caltech.edu --mail-type=END,FAIL (>= 1 h). Per-leg `done` marker keyed on (arm, dataset, split_seed, epochs_target); resume from <ckpt_dir>/last.pt."
  }
}
```

### Expected outcome

Primary scored arm `A1_lf_all` is a coverage-partitioned re-run of B3's primary arm on the repaired panel and is expected to land at panel geomean **13-18** against the own-stream anchor **15.5893** (CI [15.2071, 15.9714]) — i.e. *no claimed improvement*; the card's deliverable is the decomposition, not a new best. It clears the cratered gate (54.5868) by ~3x. It is far below the launch best-floor anchor 36.3912.

The metric that moves is the **per-dataset +/-LF effect** `E_total = skill(A0_nolf) - skill(A1_lf_all)` and its two channels `E_opt = skill(A0) - skill(A2_lf_covered)` and `E_cov = skill(A0) - skill(A3_lf_uncovered)`. Pre-registered per-dataset predictions, in copy-LF skill units, against the operative threshold `tau_d = max(r3-provisional mce, r2-certified mce)`:

| dataset | tau_d | predicted E_total | vs tau_d | reasoning |
|---|---|---|---|---|
| `sharp__cahn_hilliard` | **1.1604** | +9 to +16 | ~8-14x | ch data and its 19-D condition are unchanged by the ADRs; B4 measured the LF arm aligned (cos 0.962-0.964) and the no-LF arm orthogonal (0.0003-0.0385), E_struct 99-125x its round-2 mce |
| `sharp__allen_cahn_2d` | **16.4223** | -20 to +120 | uncertain | cond_dim 3 -> 19: A0 should improve substantially now that the IC is in the vector, so B3's +299 should shrink; genuinely 50/50 |
| `sharp__fisher_kpp_2d` | **158.3322** | +1 to +40 | predicted FAIL | B3 measured +1.31; even with the 50-D condition the provisional mce is enormous |
| `sharp__phase_field_crystal_2d` | **8.8595** | -6 to +4 | predicted FAIL (sign) | B3 measured -2.56; the shrinkage-reward mechanism (B3 M2) predicts the negative sign |
| `ifc_poisson` | **0.9377** | -3 to +3 | uncertain sign | the ladder is now nested, so the disjoint-condition supply that carried B3's ifc win is gone; B3's re-scored arm (9.5116) is already worse than the nn floor |
| `ifc_heat` | 0.1394 (**placeholder**, 10 % of its nn floor 1.3941; not claimable until r3s4 certifies) | large positive | reported only | the anchor's 0.0725 vs the affine floor 0.9584 implies a very large LF effect on the panel's only m = 0 dataset |

Channel prediction (the D2 leg): on `sharp__cahn_hilliard`, `E_cov >= 0.5 x E_total` and `E_opt < 0.25 x E_total` — i.e. the ch failure is a **coverage/identifiability** limit at N_hf = 5, not a trainability limit. Two independent reasons: `r2s4_diag-B2` already closed the same-condition auxiliary-LF channel (15/15 cells null, aux target cos >= 0.997 with the main task), and ch's design deficit is m = 15 at N_hf = 5 against d = 19. The row-count-matched twin `A3s_lf_uncov_n5` guards the converse reading (A2 small merely because its pool is 15 rows).
Every predicted effect above tau_d is >= 8x the relevant noise floor except allen_cahn and ifc_poisson, which are explicitly recorded as uncertain rather than predicted claims.

**Floor-arm gate (mandatory, `program.md` section 2 + spec 3).** An effect is claimable only on datasets where `A1_lf_all` also beats the dataset's best training-free floor (pfc `train_mean` 48.0773, ac `nn_condition` 475.8568, fk `train_mean` 390.7015, ch `nn_condition` 23.1803, ifc_poisson `nn_condition` 8.0409 and `affine_on_hf_train` 1.5938, ifc_heat `nn_condition` 1.3941 and `affine_on_hf_train` 0.9584). Applying the gate to B3's certified anchor cells, pfc (50.3973 > 48.0773) and ifc_poisson (9.5116 > 8.0409) would **fail** it, leaving {ac, fk, ch, ifc_heat} eligible — this is what makes "at least 3" a genuinely tight bar and stops the card from reporting a contest between two failed predictors (B4 cross-stream note 3).

### Expected falsification

FALSIFIED if, at seed 0 on the worst HF-subset draw, `E_total = skill(A0_nolf) - skill(A1_lf_all)` fails to exceed its operative threshold `tau_d = max(r3-provisional mce, r2-certified mce)` — pfc 8.8595, allen_cahn 16.4223, fisher_kpp 158.3322, cahn_hilliard 1.1604, ifc_poisson 0.9377041 — on at least **3** of the 5 threshold-carrying panel datasets *restricted to those where `A1_lf_all` also beats that dataset's best training-free floor* (pfc 48.0773, ac 475.8568, fk 390.7015, ch 23.1803, ifc_poisson 8.0409 / affine 1.5938), **or** if on `sharp__cahn_hilliard` the covered-conditions-only arm `A2_lf_covered` recovers >= 50 % of `E_total` while the row-count-matched uncovered arm `A3s_lf_uncov_n5` recovers < 50 % — which would show the ch +/-LF effect is an optimisation artefact of multi-resolution supervision rather than the coverage-supply mechanism this card predicts.

## Immutables self-check (positive evidence, 11/11)

1. **Data read-only.** Every leg reads `paths.stripped_data_root` (`round2/stripped_data`, symlinks into `benchmark_42`) through the frozen `round2/eval/score_panel.py`; the card writes only to `mffp_autoresearch_outputs/round3/r3s3_lf_value/B1/**` and its worktree. No generator is invoked, no `.npz`/`.npy` is written under any dataset dir, LF is never a downsampled HF (all rungs are the shipped coarse consistent solves), and the ifc HF budget stays at the shipped 5 rows (`train/fidelity_64/Xs.npy` shape (5, d), verified). `A4_hf20_nolf` selects 20 rows from the **already-shipped** 400 sharp HF train rows — the same axis round-2 12.4 sanctions ("overfitting anatomy at N_hf in {5, 20, 50} ... and N=400 (sharp)") — and is declared a labelled reference arm outside the scored +/-LF contrast.
2. **Panel + guard set fixed.** `datasets` is the exact 6-name ADR-A1 panel from `round3/project.yaml`, in order, with helmholtz absent (report-only, ADR D2) and the guard leg run via `--datasets guard` = `heat_local, fluid, sharp__sod_1d`. No dataset is added or dropped.
3. **Eval layer / spec untouched.** The card runs `round2/eval/score_panel.py` through its published CLI (`--family_dir --datasets --epochs --seed --out --env --no_cache`, read at lines 254-263) and edits nothing under `round2/eval/`, `project.yaml`, `program.md` or `subagents/`. The one eval-layer *hazard* I found is handled by choosing a `base_commit` that already carries the repaired `copylf_baselines.json` plus a runtime assertion — not by editing the eval layer.
4. **One nRMSE definition.** Scoring is whatever `score_panel.py` computes (`_nrmse_def_hash` d3d0ade9..., `_copylf_def_hash` 9753ff24...), asserted by `R3S3B1_DATA_BINDING_ASSERT`; the training loss is MSE in per-rung-scaled units, which is free.
5. **Contract CLI fixed.** All 33 knobs are `R3S3B1_*` env keys passed via `--env KEY=VAL`; `smoke_eval.py` keeps the mandated signature `--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed`; no new CLI flag is introduced.
6. **Seeds / tier epochs fixed.** `seeds: [0]` and `epochs: 200` (smoke tier from `project.yaml tiers`), guard leg at the contract tier 2. Seeds 1-2 are an in-round close precondition (PROGRAM_NOTE MUST 4) for the orchestrator to schedule if the card becomes claimable, not part of this recipe. No 2500-epoch full tier.
7. **Guarded factory surfaces untouched.** The family lives at `models_r3/r3s3_lf_channels` inside the experiment worktree; nothing under `mf_field/factory_mffp/{data,baselines,eval,references,scripts}`, `factory.md`, `akash/`, `mf_field_eloise_data` or `benchmark_42` generation code is read-write. `factory_mffp/models/_common/lf_registration.py` is *imported* read-only for the ADR r2-0001 lift convention.
8. **Checkpoint resume.** Inherited byte-for-byte from B3's proven contract: `<ckpt_dir>/last.pt` written every 250 steps with `{step, epoch, model, opt, sched, rng, epochs_target, arm, split_seed, n_hf, lf_cond_set}`, `_step_rng(seed, step)` making the step stream position-addressable, and a per-leg `done` marker keyed on `(arm, dataset, split_seed, epochs_target)`. B3's build notes record an executed resume verification on the same code path.
9. **Falsification threshold exceeds the noise floor for every cited dataset.** `tau_d = max(r3-provisional, r2-certified)` per dataset, quoted with both inputs: pfc max(8.8595, 0.2130) = **8.8595**; allen_cahn max(16.4223, 0.8797) = **16.4223**; fisher_kpp max(158.3322, 0.0007) = **158.3322**; cahn_hilliard max(1.1604, 0.0912) = **1.1604**; ifc_poisson max(0.2399, 0.9377) = **0.9377041**. Every threshold is >= the larger of the two available floors by construction, so if r3s4-B1 certifies smaller repaired-panel values the clause only gets easier and no verdict flips direction. `ifc_heat` has **no** mce in either file, so it is reported with an explicit placeholder (0.1394 = 10 % of its `nn_condition` floor skill 1.3941) and is **excluded** from the claimable count until r3s4 certifies it. The clause is also read on the **worst draw** against a constant, never `max(mce, in-job range)` — B3 cross-stream note 2 showed the range term prices the control's heteroscedasticity and penalises variance-reducing treatments.
10. **Not a pre-falsified lever re-proposed as-is.** Nearest pre-falsified item is `r2s4_diag-B2`'s auxiliary-LF-target channel ("|T1-T0| below its operative threshold in 15/15 dataset x N cells"; mechanism: the aux target duplicates the main task at cos >= 0.997). The difference: that channel is **not proposed as this card's lever** — `A2_lf_covered` is its arm, and its predicted value is ~0; the card's claim rides on `A3_lf_uncovered` / `A1_lf_all`, and B2's null is precisely what makes A2 a trustworthy null leg of the decomposition. Second nearest is B3's own falsified F2 (LF value confined to affine-deficit datasets): re-tested here deliberately, because the honest panel inverted the deficit structure (m = 0 on 4/6 in round 2 vs m >= 14 on 5/6 now, measured in summary 6a) — the card states the falsification and the difference rather than re-proposing the hypothesis blind. Round-1 pre-falsified levers (WNO backbone swap, LF low-mode freezing, diffusion prior) are untouched.
11. **Floor arms in the falsification reasoning.** `R3S3B1_REF_ARMS` puts `nn_condition`, `train_mean` and `zero` (plus `linear_hfonly` and, on both ifc datasets, `affine_on_hf_train`) on every leg with a `floors_seam_check` at tol 1e-9 against `state/anchors_repaired/floors.json`; and the falsification clause **gates on them**: an effect counts only on datasets where `A1_lf_all` beats the dataset's best training-free floor, with the numbers quoted inline (48.0773 / 475.8568 / 390.7015 / 23.1803 / 8.0409 + 1.5938 / 1.3941 + 0.9584).

## Status

- Slot covered: yes, one `model` card proposal.
- Skipped: no.
- Reopen candidates resolved: none exist for this stream (all 14 round-2 cards `reopen_candidate: false`; round 3 has no prior cards) — nothing to retry or drop.
- Immutables self-check: **pass (11/11)** on this iteration; no revision pass required, so no `iteration_2.md`.
