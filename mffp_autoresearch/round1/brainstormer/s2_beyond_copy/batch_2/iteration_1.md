# iteration_1 — s2_beyond_copy, batch 2

## Design context considered

- `summary_so_far.md` §6 unknowns 1–5 (can a trained operator beat the training-free floor;
  does it no-op on Class B; is the key the lever; does the ladder add anything; is the
  hybrid more than the sum).
- Prior-art verdicts (i) `preempted (cite)`, (ii)/(iii) `preempted-but-MF-composition-open`
  from `websearches/s2_beyond_copy/batch_2/report.md`, plus its mandatory batch-1 overclaim
  correction (MFFM's `Bilinear` baseline IS copy-LF).
- program.md §12.2 verbatim (quoted in `summary_so_far.md` §2); anchor `skill 1.0 = copy-LF`,
  `state/anchors/s2_beyond_copy.json`.
- `state/noise_floor.json`, in two framings: absolute `min_claimable_effect` (for the
  "improved on the certified champion" leg) and the seed spread rescaled to a predictor
  living at skill ~= 1.0, `spread / certified_skill` (for the fine "beat the floor" leg):
  pfc 0.007180, allen_cahn 0.000866, cahn_hilliard 0.034667, fisher_kpp 0.021973,
  helmholtz 0.701654 (=> helmholtz report-only). Precedent for the rescaling: s6_local-B1's
  `expected_falsification` uses exactly these four rescaled numbers.
- The 8 immutables (§4.5 block, quoted in the self-check below) and the §5 pre-falsified
  levers (WNO backbone swap; LF low-mode freezing `mf_fno_spectral`; diffusion prior).
- ADR 0004 (strict single seed, `provisional-single-seed` labels), ADR 0005 (H100),
  ADR 0007 (propose-many / screen-cheap / promote-few; applies — this is a model card with
  genuine design freedom, not a pre-directed slot), ADR 0009 (no known physics at test time).
- Cross-stream boundary: `experiment_cards/s6_local/batch_1/B1.json` owns "LOCAL corrector
  with a trust gate" over the same LF substrate.
- Substrate facts read this session:
  `mf_field/factory_mffp/models/mf_fno_transfer_film/model.py:138` — `self.lift =
  nn.Conv2d(2, hidden_channels, 1)`, i.e. the network input is coordinates only and X enters
  by FiLM; `smoke_eval.py` `SMOKE = dict(hidden_channels=64, n_blocks=4, modes_cap=12,
  batch_size=16, lr_pretrain=1e-3, lr_finetune=3e-4, weight_decay=1e-5, grad_clip=1.0)`,
  `WORK_CAP = 256`, LF chosen as `min(train["lf_fids"])`.
  Fidelity ladders probed through `eval/panel_data.py` (read-only): helmholtz `lf_fids [1]`
  24²->96²; pfc `[1,2]` 32²/64²->128²; allen_cahn / fisher_kpp / cahn_hilliard `[1,2]`
  64²/128²->256²; `cond_dim` 3 (helmholtz/allen_cahn per B1) to 19 (cahn_hilliard).
  Timing prior: `state/timing_ledger.json` — s5-B1 6-dataset 200-epoch H100 run 36.62 min;
  2-epoch 3-dataset guard run 0.77 min; B1's numpy forensics 0.77 min for 5 datasets.

## Proposal reasoning

**What the stream owes right now.** B1 part 7 states the open question and prescribes the
family. The websearcher then established that the prescribed family is the literature's
*baseline*, not a mechanism (LRC-FNO, MFFM's `FNO-residual`, Multifidelity DeepONet). So the
honest card is not "we invented an LF-input residual operator"; it is **"the zoo never ran
the literature-standard control, a zero-parameter retrieval rule already beats it, and here
is the measurement that says which of the two wins"**. The contribution is the discipline:
a pre-registered floor that the trained model must clear, in a benchmark where 0/27 families
even read the input the floor uses.

**Alternatives weighed and rejected.**

1. *Bare direction (i), single arm, no floor in-run.* Rejected: the falsification would then
   compare a 200-epoch number against B1's probe numbers computed by a different code path
   (`worktrees/.../reanalysis_turn_2.py`). Recomputing the floor inside the scored run,
   through `eval/nrmse.py` and `eval/panel_data.py`, makes the comparison seam-checkable
   (F6 reproduction to a declared tolerance) instead of cross-run folklore.
2. *Promote the retrieval rule itself as the card's scored family.* Rejected outright:
   B1 part 5 `do_not_promote` — "a training-free 1-NN-in-X LOOKUP TABLE, not a model
   (reviewer S3). It MUST NOT enter any leaderboard, anchor, or top-3 eligibility."
   Floors therefore live in `ref_*` splits + a sidecar, never in `splits.test`.
3. *Lead with direction (iii), the hybrid.* Rejected as the promoted arm: it is the only
   arguable mechanism claim, but it confounds the question. If a hybrid wins, the retrieval
   term alone may explain it, and a 2-epoch ADR-0007 screen actively *favours* arms whose
   strength is training-free. Hybrid stays in the pool under an anti-hijack promotion rule,
   and is additionally measured for free post-hoc as a convex blend `ref_*` split.
4. *A local/depthwise corrector or a spatial trust gate.* Rejected: that is `s6_local-B1`'s
   declared ownership (`y = LF_up + G (*) Delta`, ConvNeXt-lite). B2 stays global-spectral.
5. *Raise `modes_cap` to 32 while adding the LF input.* Rejected: confounds with
   `s5_tuning-B1`, whose provisional result already says spectral capacity alone is not the
   claimable lever. `modes_cap` pinned at the champion default 12.
6. *Chase Class B below copy-LF (allen_cahn / fisher_kpp).* Rejected on evidence: F13 shows
   the LF field does not predict their residual in any band (R_b >= 1.003). Pre-declared as a
   no-harm leg, per B1 part 7 design point (2).
7. *A band-split / low-mode treatment.* Explicitly forbidden by B1 part 7 ("Do NOT license
   the D3 band-split") and adjacent to the §5 pre-falsified `mf_fno_spectral` lever.
8. *Test-time physics residual refinement of the correction.* Excluded by ADR 0009; the
   websearcher confirms every published hybrid corrector of that shape needs the PDE at test
   time. Retrieval is the compliant substitute.

**Why these particular arms.** One substrate, env-selected, so all arms share data path,
normalization, checkpointing and the identity seam:

```
LF_up  = interp(field_by_fid[max(lf_fids)] -> 256-capped working grid)   # == copylf_prediction
y_hat  = LF_up + Delta_theta([coords, LF_up(, extra channels)], FiLM(X))
```
with a **zero-init final 1x1** so `Delta_theta == 0` at init and `y_hat == LF_up` exactly
(copy-LF exactly recoverable — the parameterization the verdict (iii) row calls open, and a
cheap auditable seam for every arm). Target on the HF train split is `R = Y_hf - LF_up`.

Trained arms (ADR 0007 pool, ranked):

| rank | `S2_ARM` | delta | why it is in the pool |
|---|---|---|---|
| 1 | `lf_resid_fno` | LF_up as the only extra input channel | the literature-standard control the verdict names; answers the falsification question with nothing else moving |
| 2 | `lf_resid_fno_ladderpre` | pretrain the same net on the coarse pair (fid1 -> fid2 residual, 400 samples) then fine-tune on (fid2 -> fid3); helmholtz has one LF rung so it falls back to rank 1 | the MF-composition question unknown 4; reuses the champion's own pretrain->finetune schedule instead of adding capacity |
| 3 | `lf_resid_fno_multichan` | all LF fidelities interpolated as separate input channels | cheapest test of whether the ladder carries information past `max(lf_fids)` |
| 4 | `hybrid_retr_resid` | retrieved residual `R_retr` (block-mean key) as an extra input channel AND an additive term with scalar `w` init 0 | direction (iii); still exactly copy-LF-recoverable at init |

Training-free floors (never promotable, emitted as `ref_*` splits + `floor_<ds>.json`):

| `S2_FLOOR_ARMS` | key | provenance |
|---|---|---|
| `retr_blockmean16_k5` (**required**) | 16x16 block-mean signature of the test LF field, k=5 | B1 F6/F9; must reproduce 0.562 / 0.625 / 0.785 / 1.042 / 1.062 within `S2_FLOOR_F6_TOL=0.02`, else the data path differs from `tools/lf_conditioned_headroom.py` and the build flags it |
| `retr_s1grad_k5` | Teweles-Wobus S1 gradient criterion | free steal (a), AtmoSwing <https://gmd.copernicus.org/articles/12/2915/2019/> |
| `retr_patch_k5` | 4x4 tiles, per-tile kNN, cosine-window reassembly | free steal (b), LOCA region-then-local |
| `copylf_identity` | none | seam: skill must equal 1.0 up to the interpolation-kernel delta vs `eval/copylf_baselines.json` |
| `blend_trained_retrieval` | post-hoc convex blend of the promoted arm and `retr_blockmean16_k5`, weight fit on a 20% held-out slice of the HF **train** split, candidate set contains 0 | direction (iii) evidence at zero extra training cost |

**Screen spec (ADR 0007).** ONE contract-tier job: `--epochs 2 --seed 0`, arms
`S2_SCREEN_ARMS` (4 trained) over the 5 beyond-copy datasets **and** the guard set
(§2.3 requires a guard contract run before any panel-win claim; `sharp__sod_1d` is 1-D and
takes the pre-registered `S2_FALLBACK_NO_TEST_LF=champion` path). Floors are deterministic
and epoch-independent, so they are computed once in the same job and reused. Expected cost
by the ledger: << 5 min GPU + ~5-15 min numpy.

**Promotion rule (`S2_PROMOTION_RULE`).** Promote the pinned rank-1 arm `lf_resid_fno`
unless the screen shows it CRATERED (crash/NaN, or screen skill > 1.5x the best surviving
arm's on >= 3 of the 5 beyond-copy datasets); then take the next non-cratered arm in rank
order. A hybrid arm may be promoted ONLY if additionally its screen skill is <= (screen skill
of `retr_blockmean16_k5`) - 0.05 on >= 2 Class-A datasets — otherwise its screen advantage is
attributable to its training-free term and says nothing about the learned one. Pinning rank 1
by default is deliberate: 2-epoch rankings are noise (ADR 0007 calls them "a coarse filter"),
and the card's question is about the control, so screen results may only *remove* it, never
silently replace it. Promoted identity is fixed in the card before the 200-epoch submit.

**Why the expected numbers.** pfc: 53% of samples have copy-LF exact to ~1e-8 and the
residual is a strong function of the LF field (F6 0.562 with zero parameters); a trained
global operator that sees LF_up should beat a 5-neighbour average -> ~0.40. cahn_hilliard:
floor 0.625, no bimodality, champion already the best-behaved -> ~0.55. helmholtz: floor
0.785 but 86.5% amplitude error and 3% of samples carrying half the error -> ~0.8, wide,
report-only. Class B: the zero-init residual head should shrink toward ~0 but MSE returns a
small conditional mean -> ~1.02 / ~1.03, i.e. better than the retrieval rule's 1.042 / 1.062
and within the 1.05 no-harm bound. Panel geomean of those five = **0.713** (computed), vs
the training-free floor 0.7886 and the certified champion 9.6362.

## Proposal

- **Category**: `mf_composition / literature-standard LF-residual control vs a training-free
  retrieval floor (benchmark-floor discipline)`
- **Card type**: `model`
- **Motivation**: the websearcher's verdict for direction (i) is **`preempted (cite)`** and
  its open column reads, verbatim: "**Nothing at the mechanism level.** Only setting: (a) our
  LF is a real coarse *consistent* solve (immutable 1) rather than a coarse-network output or
  a downsample; (b) no retrieved MF/coarse-correction work runs on sharp-interface 2-D
  phase-field data; (c) the Class-A/Class-B partition (fidelity residual unlearnable on 2/5
  datasets) is a data finding. **Propose it as the missing literature-standard control**,
  given batch-1 F14 (0/27 families read the test LF field), not as a new model." The card
  does exactly that, and pairs it with verdict (ii)'s open composition — "transferring the
  **fidelity residual** (`HF-LF`) of retrieved neighbours onto the query's **own** coarse
  field, keyed on the LF solution field, used as a **floor in an MF operator benchmark**" —
  as the pre-registered bar. It also carries the required correction: batch 1's prior-art
  cell overclaimed; MFFM's **Bilinear** no-learning baseline IS copy-LF.
- **Concrete config**: as the arm/floor/screen/promotion tables above; substrate copied from
  `mf_fno_transfer_film` (`hidden_channels=64, n_blocks=4, modes_cap=12, batch_size=16,
  lr 1e-3 pretrain / 3e-4 finetune, weight_decay 1e-5, grad_clip 1.0, WORK_CAP=256`), with
  `lift = Conv2d(2 + n_extra, 64, 1)` and a zero-init projection head; `max(lf_fids)` (NOT
  the champion's `min`); residual target; copy-LF added back; checkpoint-resume from
  `<ckpt_dir>/last.pt` keyed on (arm, epochs_target, grid, stage); leakage tripwires
  (no HF test field on the prediction path; LF native grid strictly coarser than HF;
  retrieval reads residuals from the TRAIN split only).
- **Recipe**: see `report.md` (complete JSON).
- **Expected outcome**: promoted-arm skills ~0.40 pfc / ~0.55 cahn_hilliard / ~0.8 helmholtz
  / ~1.02 allen_cahn / ~1.03 fisher_kpp; panel geomean ~0.713 vs the 0.7886 training-free
  floor and the 9.6362 certified champion; skill < 1 on >= 2 (target 3) beyond-copy datasets
  = the first movement on program.md §1 success criterion 2. Every per-dataset improvement
  over the certified champion exceeds that dataset's `min_claimable_effect` by >= 3.2x
  (pfc 11.1 vs 1.1511; allen_cahn 15.3 vs 1.6334; cahn_hilliard 4.98 vs 0.5533;
  fisher_kpp 3.15 vs 0.4177; helmholtz 13.0 vs 9.6950).
- **Expected falsification**: see `report.md` (single clause, four legs).
- **Anchor reference**: `null` — s2_beyond_copy is a gap stream and its own anchor
  (copy-LF, skill 1.0) is implicit (program.md §4.5).

## Status

- Slot covered (1 proposal, `model` card, ADR-0007 arm pool + screen + promotion rule).
- Skipped: no.
- Reopen candidates resolved: none exist (B1 `reopen_candidate: false`).
- Immutables self-check: **pass (10/10)** — recorded below, no revision needed.

## Immutables self-check (positive evidence, 10 items)

1. **Data read-only.** All access is `eval/panel_data.py::load_split` / the factory adapter
   in read mode; the LF tensor is `field_by_fid[max(lf_fids)]` from the shipped arrays,
   upsampled by the same transform as `copylf_prediction`; a builder tripwire
   (`S2_LEAKAGE_TRIPWIRE=1`) aborts if the LF fidelity's native grid is not strictly coarser
   than HF (i.e. if anything downsampled-HF-like were substituted). No file under
   `benchmark_42/**` or `factory_root/data/**` is opened for writing; N_hf stays 400/100.
2. **Panel + guard set fixed.** `datasets` is exactly the five beyond-copy panel members
   from `project.yaml panel:` minus `ifc_poisson` (whose test split ships no LF — verified:
   `lf_fids` present only for the other five; ADR 0002 makes it a paper-bar dataset anyway);
   the guard set appears only as `S2_SCREEN_DATASETS=beyond_copy5,guard` at contract tier,
   which is what §2.3 requires. No dataset is added, removed or redefined.
3. **Eval layer / spec untouched.** The whole proposal is a new directory
   `models_r1/s2_lf_residual_control/` inside the worktree plus `scripts/`; scoring is by
   `eval/score_panel.py --family_dir ...`; nothing in `round1/eval/`, `project.yaml`,
   `program.md`, ADRs or `subagents/` needs an edit for any arm, floor, screen or tripwire
   described here.
4. **One nRMSE definition.** Every reported number — the scored `test_hf` split, every
   `ref_*` floor split, the blend — is produced by the family's result JSON and scored
   through `eval/nrmse.py` with `nrmse_def_hash` recorded, exactly as B1 did
   (`nrmse_def_hash: d3d0ade9...`, `nrmse_def_hash_consistent: true`). The training loss is
   MSE on the residual in scaler space (free under §5); the scored metric is untouched.
5. **Contract CLI fixed.** `smoke_eval.py` keeps the six-argument signature
   (`--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed`); every behavioural knob
   is an `S2_*` environment variable and all of them are listed in the recipe `env` block, so
   they enter the cache key (§5.5). No new CLI flag is proposed.
6. **Seeds / epochs fixed.** `seeds: [0]` (ADR 0004 strict single seed); `epochs: 200`
   (smoke tier); the ADR-0007 screen is at `epochs: 2` (contract tier). No other budget
   appears; full tier is not requested. All results will be labelled
   `provisional-single-seed`.
7. **Guarded factory surfaces untouched.** The substrate is *copied* into `models_r1/` (the
   s5-B1 precedent, including the `REPO_ROOT = HERE.parents[1] / "mf_field" /
   "factory_mffp"` import fix); `factory_root/{eval,baselines,references,scripts,data}`,
   `factory.md` and `mf_field/akash/**` are never opened for writing — the card's only reads
   there are the frozen family source and the read-only data symlinks.
8. **Checkpoint-resume implementable.** Training is a plain AdamW loop over 400 HF samples
   (plus an optional coarse-pair pretrain stage for arm 2), so `last.pt` carries
   `{arm, stage, epoch, model, opt, sched, generator, epochs_target, grid, nrmse_def_hash}`
   and resume is a guarded load — the same shape the champion already implements at
   `mf_fno_transfer_film/smoke_eval.py` (resume "keyed on (epochs_target, grid)"). The
   retrieval floors are deterministic and recomputed in seconds on resume.
9. **Thresholds exceed the noise floor** (`state/noise_floor.json`; every number quoted):
   - pfc: margin 0.05 skill units vs rescaled floor `0.082643 / 11.511001 = 0.007180`
     -> **6.96x**; the champion-improvement leg 11.1 units vs `min_claimable_effect`
     **1.151100** -> 9.6x.
   - cahn_hilliard: margin 0.07 vs `0.191827 / 5.533466 = 0.034667` -> **2.02x**;
     improvement leg 4.98 vs **0.553347** -> 9.0x.
   - allen_cahn: no-harm margin 0.05 vs `0.014150 / 16.334071 = 0.000866` -> **57.7x**;
     improvement leg 15.3 vs **1.633407** -> 9.4x.
   - fisher_kpp: no-harm margin 0.05 vs `0.091789 / 4.177355 = 0.021973` -> **2.28x**;
     improvement leg 3.15 vs **0.417735** -> 7.5x.
   - ext__helmholtz_2d: rescaled floor `9.694961 / 13.817290 = 0.701654` admits no
     fine-grained claim -> **report-only**, and it carries no threshold in the falsification
     clause except the coarse improvement leg (13.0 vs `min_claimable_effect` 9.694961).
10. **Not a pre-falsified lever.** Nearest §5 entry is **LF low-mode freezing**
    (`mf_fno_spectral`, "worst on sharp"). Difference: that lever *fixes* the LF's low modes
    inside the output spectrum during training and never gives the network the per-sample LF
    field at inference; this card leaves the spectrum entirely free and instead changes the
    INPUT (the real coarse solve enters as a channel at both train and test time) with an
    additive residual output. B1 F14 shows the pre-falsified family, like all 27, was
    LF-blind at inference, so its falsification does not bear on this composition. The WNO
    backbone swap and the diffusion prior are untouched (backbone stays FNO; no generative
    head). The card also explicitly does NOT re-propose the D3 band-split that B1 part 7
    forbids.
