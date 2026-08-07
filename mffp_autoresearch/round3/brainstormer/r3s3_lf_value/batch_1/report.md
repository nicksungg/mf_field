# Brainstormer Report — Stream `r3s3_lf_value`, Batch 1

**Stream**: `r3s3_lf_value` (lever) · **Batch**: 1 · **Total iterations**: 1 · **Slot filled**: 1/1 · **Reopen candidates resolved**: 0 (none exist)

## Slot

- **Category**: `lf_value / coverage-vs-optimisation channel decomposition of the matched +/-LF-at-train effect on the completeness-certified panel, with the HF-row-equivalent price`
- **Card type**: `model`
- **Motivation**: The round-3 stream question asks "what is LF-at-train worth on the honest panel (coverage/amplitude, ch identifiability-vs-trainability), matched with/without arms at matched procedure?" and criterion 2 wants a certified matched-arm measurement on >= 3 scored datasets. The websearcher's verdict says the ablation *genre* is preempted and that only a four-clause composition is open — "**The finding must be the measured number, never the ablation genre.**" This card delivers the number and, in the same run, the mechanism split that round 2 handed forward: `r2s3-B4` closed with "whether 5 HF rows plus a 19-dimensional condition vector fail to DETERMINE that phase (an identifiability limit ...) or merely fail to let this optimiser FIND it in 200 epochs (a trainability limit, closable without LF)". The design insight is that information about the condition -> field map at unseen conditions can only come from rows *at* those conditions, so partitioning the LF rows by **condition coverage** (covered vs uncovered by the HF draw) splits the +/-LF effect into an optimisation channel and a supervision/coverage channel with a matched procedure. On the honest panel this is newly informative: I measured the affine coverage deficit at N_hf = 5 as m = 14 (pfc) / 15 (ac) / 46 (fk) / 15 (ch) / 1 (ifc_poisson) / **0 (ifc_heat)** — five of six datasets now carry a live coverage channel where 4 of 6 had none in round 2, and `ifc_heat` becomes the panel's natural negative control. The section-12.3 declared baseline `mf_fno_transfer_film` (LF-pretrain -> HF-finetune on the *full* LF pool) is cited and differentiated, not re-run: it blends the two channels this card separates.
- **Concrete config**: New family `models_r3/r3s3_lf_channels`, condition-only at test, stripped view only. Backbone/optimizer/scaler/step-budget/RNG-order vendored byte-for-byte from `models_r2/r2s3_coverage_panel` (B3, commit dfcd46c6) so the `A0`/`A1` legs form an exact reproduction seam against the certified anchor. Six arms, driven by two orthogonal knobs (`LF_COND_SET`, `N_HF`): `A0_nolf` (HF only); **`A1_lf_all`** (PRIMARY scored: HF + all rungs at all conditions); `A2_lf_covered` (LF only at the 5 conditions that already carry an HF row -> optimisation channel); `A3_lf_uncovered` (LF only at conditions with no HF row -> coverage channel; 395 sharp, 95/45/15 ifc); `A3s_lf_uncov_n5` (5 uncovered conditions, row-count-matched twin of A2; ch + both ifc); `A4_hf20_nolf` (N_hf = 20, no LF, sharp only — labelled budget-varied reference arm outside the scored contrast, pricing LF in HF-row units). Grid = 48 + 8 + 5 + 12 + 1 guard = **74 legs, one SLURM job, seed 0** (~2.1 h at B3's measured 1.7 min/leg; 06:00:00 with END,FAIL mail). Mandatory floor arms + `affine_on_hf_train` on both ifc datasets on every leg; blocking pre-flights = `target_scale_spread_audit.py` on pfc (ADR r2-0004), `condition_identifiable_rank.py` + `affine_ladder_voi.py` on ch's 19-D design (B4's named probes), and a data-binding assertion tying `copylf_baselines.json` to `floors.json` references.
- **Recipe**:
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
- **Expected outcome**: The PRIMARY arm `A1_lf_all` is expected at panel geomean **13-18** against the own-stream anchor `r2s3_lf_train_signal-B3` = **15.5893** (CI [15.2071, 15.9714]) — deliberately *no claimed improvement*; it clears the cratered gate (1.5 x 36.3912 = 54.5868) by ~3x. The metric that moves is the per-dataset **+/-LF effect** `E_total = skill(A0_nolf) - skill(A1_lf_all)` and its channels `E_opt` (via `A2_lf_covered`) and `E_cov` (via `A3_lf_uncovered`). Predictions vs the operative threshold `tau_d = max(r3-provisional mce, r2-certified mce)`: ch +9 to +16 vs tau 1.1604 (**~8-14x the floor**; B4's LF-vs-no-LF cosine 0.962-0.964 vs 0.0003-0.0385); ac -20 to +120 vs tau 16.4223 (uncertain — cond_dim 3 -> 19 should lift `A0`); fk +1 to +40 vs tau 158.3322 (predicted fail); pfc -6 to +4 vs tau 8.8595 (predicted sign fail, B3's shrinkage-reward mechanism); ifc_poisson -3 to +3 vs tau 0.9377041 (uncertain — the ladder is nested now, so B3's disjoint-condition supply is gone); ifc_heat large positive but **reported only** (no certified mce; placeholder 0.1394). Channel prediction on ch: `E_cov >= 0.5 x E_total` and `E_opt < 0.25 x E_total`. A claimability **floor gate** applies: an effect counts only where `A1_lf_all` beats the dataset's best training-free floor (48.0773 / 475.8568 / 390.7015 / 23.1803 / 8.0409 / 1.3941) — on B3's certified cells that gate would exclude pfc and ifc_poisson, leaving {ac, fk, ch, ifc_heat} eligible, which is what makes "at least 3" tight.
- **Expected falsification**: FALSIFIED if, at seed 0 on the worst HF-subset draw, `E_total` fails to exceed `tau_d` (pfc 8.8595, ac 16.4223, fk 158.3322, ch 1.1604, ifc_poisson 0.9377041) on at least 3 of the 5 threshold-carrying datasets *restricted to those where `A1_lf_all` also beats that dataset's best training-free floor*, or if on `sharp__cahn_hilliard` `A2_lf_covered` recovers >= 50 % of `E_total` while the row-count-matched `A3s_lf_uncov_n5` recovers < 50 % — which would show the ch effect is an optimisation artefact of multi-resolution supervision rather than the coverage-supply mechanism this card predicts.
- **Prior-art verdict quoted** (verbatim, `websearches/r3s3_lf_value/batch_1/report.md`, "## Prior-art verdict"):

  > **D1** — matched, budget-matched **+/-LF-at-train** contrast for a condition-only field surrogate on the **completeness-certified** round-3 panel; the deliverable is the certified per-dataset effect in copy-LF skill units (success criterion 2, >= 3 datasets) | **preempted-but-MF-composition-open** | Ablation genre: https://arxiv.org/abs/2512.02868 (fetched — "equivalent single-fidelity tests for each case, quantifying the performance gains achieved through fusing multiple sources"). Mechanism theory: https://leon.bottou.org/publications/pdf/iclr-2016.pdf (fetched — privileged information accelerates the rate O(n^-1/2) -> O(n^-1)); http://arxiv.org/abs/1511.03643v3 (fetched via arXiv API). Negative side: https://arxiv.org/abs/2410.12690 (fetched — LF data can worsen HF predictions; transfer must be local). | The composition, all four clauses simultaneously: (a) LF **absent from the test path by construction** (stripped view), so the contrast prices LF as *training data*, not as an input; (b) a panel carrying an explicit **completeness certificate** (HF exactly reconstructible from the stored condition) — turn 4 term 2 returned **nothing** in this slot, every retrieved MF-PDE work either keeps LF at inference or never certifies sufficiency; (c) the **copy-LF denominator** ("is the model worth more than running the coarse solve?") plus the ifc `affine_on_hf_train` floor; (d) N_hf = 5 on the ifc ladder with a certified `min_claimable_effect`. **The finding must be the measured number, never the ablation genre.**

  > **D2** — decide **identifiability vs trainability** on `sharp__cahn_hilliard` (19-D complete condition): arms where LF can only act as an optimisation aid (LF-pretrain -> HF-finetune, warm start, curriculum) vs arms where LF supplies supervision at conditions with no HF row | **preempted-but-MF-composition-open** | Dichotomy + vocabulary: https://arxiv.org/pdf/2502.04282 (fetched — information-theoretic recoverability "as soon as the number of measurements equals the dimensionality" vs "an algorithmically hard phase where all known polynomial-time algorithms struggle"). Optimisation channel formalised: https://proceedings.neurips.cc/paper_files/paper/2023/file/ee1f0da706829d7f198eac0edaacc338-Paper-Conference.pdf (fetched — KD = **partial variance reduction** of the stochastic gradient). Trainability-limit language: https://arxiv.org/abs/2602.16177 (fetched — "data determines the fundamental limit of trainability"). | The **discrimination has a name** (statistical-to-computational gap), so the card must not claim the concept. What is open: nobody has run it for *low-fidelity coarse solves as the auxiliary signal on a certified-complete PDE condition vector*, and turn 2 term 2 + turn 3 term 2 both returned **no usable result** for a matched experiment separating warm-start/optimisation help from supervision help. Note the sharpened stake: B4 measured the no-LF ch arm at median per-sample cosine 0.0003-0.0385 vs the LF arm's 0.962-0.964 — that signature is *local-minimum-like*, which is a prediction the trainability arm can falsify.

  > **D3** — distil an **LF-consuming teacher** into a condition-only student (LF as a pure training-time privileged signal, teacher absent at test) | **preempted (cite)** | ... | Ship only as a **cited baseline arm**, never as the contribution. ... Round-2 batch 1 already returned the same verdict class for this mechanism (`round2/websearches/r2s3_lf_train_signal/batch_1/report.md`), so a re-proposal without this framing is a rebadge.

- **Immutables self-check**: **pass (11/11)** — see `iteration_1.md` "Immutables self-check". No item was flagged and no revision pass was needed. Highlights: (1) the ifc HF budget stays at the shipped 5 rows and `A4_hf20_nolf` uses only already-shipped sharp HF rows on the axis round-2 12.4 sanctions; (9) `tau_d = max(r3-provisional, r2-certified)` per dataset with both inputs quoted, so an r3s4 re-certification can only loosen the clause; (10) the nearest pre-falsified item is `r2s4_diag-B2`'s auxiliary-LF-target null, which this card uses as its **control arm** rather than its lever; (11) the floor arms are not merely reported but **gate the claim**.
- **Anchor reference**: `null` (round-3 policy for all four streams: gap/lever/diag, own-stream anchor implicit)
- **Source iteration**: [iteration_1.md](iteration_1.md)

## Reopen candidates

| Candidate | Verdict (retry/drop) | Eased conditions | Source iteration |
|---|---|---|---|
| _none_ — all 14 round-2 cards carry `reopen_candidate: false` and round 3 has no prior cards for this stream | n/a | n/a | [iteration_1.md](iteration_1.md) |

## Skipped slot

Not applicable — the slot is filled.

## Summary table

| Slot | Category | One-liner | Status |
|---|---|---|---|
| 1 | `lf_value / coverage-vs-optimisation channel decomposition` | Partition the LF training rows by *condition coverage* to split the matched +/-LF effect into an optimisation channel and a supervision/coverage channel on the completeness-certified panel, with a row-count-matched twin and an N_hf = 20 reference rung that prices LF in HF-row units | filled (`model`) |
