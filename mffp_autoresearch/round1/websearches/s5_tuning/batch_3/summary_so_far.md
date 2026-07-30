# Summary so far — `s5_tuning`, batch 3

Written before searching. Sources are files I read in this invocation; paths are
relative to `${ROUND_ROOT}` = `/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch/round1`.

## Where the stream stands

`s5_tuning` is the **tuning** stream (program.md §12.5): knobs on existing recipes
only — no new losses-as-mechanisms, no architectural changes, no new paradigms.
Anchor (`state/anchors/s5_tuning.json`): champion `mf_fno_transfer_film`, certified
panel geomean skill **6.703**, CI95 [6.2185, 7.1022], 3 seeds, batch 0.

**s5-B1** raised `modes_cap` 12→32 and closed `not_resolvable`; its part 7 named the
normalization knob as the leading candidate.

**s5-B2** (`experiment_cards/s5_tuning/batch_2/B2.json`) ran the target-scaler knob:
five arms (A0 `maxabs` control, A1 `p995`, A2 `zscore` promoted, A3 `revin_lf`
per-sample `s_i = max|LF_i|`, A4 `shared`), ADR-0007 screen + one 200-epoch panel of
the promoted arm A2. Result (part 5, seed 0, single-seed provisional): panel geomean
skill **5.5547** vs anchor 6.703; `ext__helmholtz_2d` skill 18.83 → 5.77 (report-only,
floor 9.695), `ifc_poisson` 1.545 → 1.185 (the only numerically claimable dataset move,
floor 0.2399), four sharp sets inside their floors (allen_cahn 1.633, cahn_hilliard
0.553, fisher_kpp 0.418, pfc 1.151). **A3 `revin_lf` was implemented and rank-ordered
but never run at 200 epochs** — it is the pre-scoped B3 arm.

## What the mechanism analyzer settled (B2 part 6/7 + `worktrees/s5_tuning/B2/notes/handoff_experiment_mechanism_analyzer.md`)

1. The zscore gain is **dynamic-range placement + per-sample amplitude calibration**:
   on helmholtz **91.6 %** of the log gain is amplitude an oracle rescale gives for free;
   after an oracle rescale the arms differ by only 1.108x.
2. **A global scalar cannot repair effective N.** Effective N of the helmholtz training
   MSE is 1.0145/400 under `maxabs` and 1.0179/400 under `zscore`; top-1 energy share
   0.9928 vs 0.9912. Only a per-sample scale (or an objective-side fix) can move it.
   This *corrects* the s2-B2 "effective-N repair" story as applied to global scalers.
3. **Eligibility predictor is `G = max|Y_train| / sd(Y_train)`**, reported as
   tail (max/rms) x pedestal (rms/sd) — never `|mu|/sd`, which measures the pedestal the
   output bias absorbs for free. Panel break: G 6.0 = nothing, G 9.9 = effect; B3
   pre-registers **G >= 8 gated on a live pattern channel** (`tools/dc_pattern_split.py`;
   LEVEL_ONLY sets are inert by construction).
4. **Sharp-2D normalization is closed negatively** — the three LEVEL_ONLY sharp sets sit
   at 1.04–1.44x their own constant-field oracle under both scalers.
5. **Untested H3**: `grad_clip = 1.0` interacts directly with the loss scale (helmholtz's
   `maxabs` loss is ~1/1558 of the `zscore` loss). If the clipper, not the scaler, is what
   robustified the dominant sample, a per-batch grad-norm/clip-rate log settles it.
6. Tools promoted: `tools/target_range_placement_audit.py`, `tools/paired_arm_displacement.py`.

## The B3 scope and the s2-B3 division of labour

B2 part 7 declares a **MERGE CANDIDATE**: "*this is the same experiment
s2_beyond_copy-B3 is heading for from the residual-target side; ... s5 owning the
raw-target/LF-blind substrate and s2 owning the residual-target/LF-consuming one.*"
So B3's arms are: A3 `revin_lf` at 200 epochs, an **LF-free** per-sample-scale arm, a
`SCALER_INERT` control, pre-registered G>=8 + live-pattern eligibility, per-batch
gradient-norm/clip-rate logging (H3), headline metric = **effective N of the realized
per-batch loss**.

## Prior searches I must build on, not redo

- `websearches/s2_beyond_copy/batch_3/report.md` — its **D1** verdict is
  `preempted-but-MF-composition-open` for per-sample normalization of the
  **fidelity-residual** target: DiSOL magnitude decoupling (per-sample amplitude `u_lim`,
  `u_h := U_h/u_lim`, optional amplitude regressor, https://arxiv.org/html/2601.09143v1);
  QuadNorm per-sample stats in operator *feature* layers "not inputs or targets"
  (https://arxiv.org/html/2605.07375); RevIN critique scoped "exclusively time series"
  (https://arxiv.org/html/2603.11869); RMFNN does not normalize the MF residual at all
  (https://arxiv.org/html/2310.03572). Its **D4** carries a fetched NEGATIVE result for
  tail reweighting (https://arxiv.org/html/2605.16078). I do **not** re-search that ground.
- `websearches/s5_tuning/batch_2/report.md` rows (i)–(iii): row (i) already fetched MPP
  (RevIN inside a PDE surrogate, https://arxiv.org/html/2310.02994v2) and APEX
  (per-sample amplitude anchor from a *coarser-fidelity operator*, target-scarce MF,
  framed as architecture, https://arxiv.org/abs/2605.26732), and issued the standing
  **territory ruling**: scaler-only is s5-legal (K) *only* if the scale comes from an
  inference-available statistic with zero new parameters; a learned scale head is
  architecture (s6/s3).
- In-repo reports `docs/reports/MF_Leaderboard_Beaters_2026_Report.md`,
  `docs/reports/MF_Sharp_HighFreq_Report.md` — batch-2 already mined these for the
  normalization question; not re-derived here.

## Open questions this batch's search must serve

- Q1 Is **LF-statistic-based target de-normalization** (RevIN whose statistics come from
  the *input* low-fidelity field, applied to a **raw** target) published anywhere outside
  time-series forecasting? APEX is the nearest known neighbour — is it the same thing?
- Q2 Is there prior art for **gradient clipping as the implicit robustifier** of a
  heavy-tailed per-sample energy distribution, and for clipping vs per-sample
  normalization being **redundant/competing**? (H3)
- Q3 Is "**effective N of the realized per-batch loss**" a published training diagnostic?
- Q4 Is there any **systematic maxabs-vs-zscore-vs-per-sample target-scaling comparison**
  in operator learning (dynamic-range placement)?

## Constraints that bound anything the brainstormer proposes

ADR 0009 (no PDE-residual information at test time); metric frozen (program.md §5
immutables 2–4); ADR 0004 seed 0 single-seed in-round; ADR 0007 screen machinery
available; certified floors geomean 0.884, helmholtz report-only 9.695, pfc 1.151,
allen_cahn 1.633, fisher_kpp 0.418, cahn_hilliard 0.553, ifc_poisson 0.240.
Prior-art discipline: program.md §13.3 — the project is 0-for-4 on novelty; recall is
not citation.
