# summary_so_far — s2_beyond_copy, batch 3

## Where the stream stands (from cards + handoffs, read 2026-07-30)

**B1 (diagnostic).** Established F14: 0 of 27 factory families read the test split's
LF field at inference, and a zero-parameter retrieval rule (copy-LF + mean of the 5
nearest train residuals, keyed on a 16x16 block-mean LF signature) reaches panel
geomean skill 0.7886 vs the certified champion's 9.6362
(`experiment_cards/s2_beyond_copy/batch_2/B2.json` part 2 quoting B1 F6).

**B2 (literature-standard LF-residual control + retrieval floor).** Scored arm
`lf_resid_fno`, 200 ep, seed 0, beyond-copy geomean **0.380264**. The mechanism
analysis (`worktrees/s2_beyond_copy/B2/notes/handoff_experiment_mechanism_analyzer.md`;
card parts 6-7) shows the win is **re-learned registration**, not physics:

- learned correction vs the analytic half-cell ramp: cos **0.987-0.999**, amplitude
  0.996-1.004 on allen_cahn / cahn_hilliard; registration share of the "win" pfc
  ~100 %, allen_cahn 97.5 %, cahn_hilliard 99.9 %, fisher_kpp 95.9 %;
  Spearman(registration share, model share) = 0.90.
- Against a node-aligned (variant C/D/E) reference the same run's geomean flips
  **0.380 -> 10.31**, while the **zero-parameter** node-aligned fix alone scores
  **0.0369** — 10.3x better than 200 epochs of training.
- **helmholtz root cause**: one global `max|HF-LF|` target scaler over a train split
  whose per-sample residual scale spans decades; **one of 400 samples carries 89.2 %
  of the MSE energy (effective N = 1.2)**; a single train-fitted scalar alpha = 0.0224
  turns skill 4.14 into 0.995. pfc mirror: the global scaler is 7.9e4x the median
  per-sample max, targets are numerically ~0, model emits a noise floor 8206x truth.
- **fisher_kpp** shortfall is `modes_cap = 12` band limitation (16.8 % of its residual
  is in-band; the sqrt(2(1-cos)) law predicts its skill to 0.014).
- **Trust-gate oracle** already measured: geomean 0.380 -> **0.259**, helmholtz
  4.136 -> 0.675, but a real gate needs a decision rule reading only (X, LF).

**Operator note** `docs/operator_notes/2026-07-30-benchmark-registration-note.md`
records the registration defect in closed form (scipy zoom `grid_mode=True`
cell-centred convention applied to node-sampled dyadic ladders => fixed (r-1)/2 HF-cell
shift), plus the helmholtz zero-predictor addendum. The **round-1 metric is frozen**
(program.md §5 immutables 2-4): corrected references may be reported ALONGSIDE, never
instead of, the frozen copy-LF skill.

## Anchors and floors this batch must respect

`state/anchors/s2_beyond_copy.json`: anchor = copy-LF skill 1.0; certified best skills
helmholtz 13.82, allen_cahn 16.33, pfc 11.51, fisher_kpp 4.18, cahn_hilliard 5.53.
Certified falsification floors handed to me: geomean 0.884; pfc 1.151, allen_cahn
1.633, fisher_kpp 0.418, cahn_hilliard 0.553, ifc_poisson 0.240; helmholtz
report-only (`state/noise_floor.json` + ADR 0002). ADR 0004 = seed 0 only; ADR 0007 =
propose-many/screen-cheap/promote-few; ADR 0009 = no known physics at test time.

## Prior websearch state (batch 2)

`websearches/s2_beyond_copy/batch_2/report.md` verdicts: (i) LF-as-input-channel
residual FNO = **preempted** (LRC-FNO arXiv:2606.17733; MFFM arXiv:2605.16118;
Multifidelity DeepONet arXiv:2204.06684); (ii) retrieval residual floor =
**preempted-but-MF-composition-open** (AtmoSwing GMD 12:2915; DeltaPhi arXiv:2406.09795);
(iii) learned+retrieved hybrid = **preempted-but-MF-composition-open** (NNTNNR
arXiv:2310.00664). None of those loops searched normalization, loss reweighting,
gating, or resampling-registration literature — batch 3's levers are unsearched.

In-repo literature reports: `docs/reports/MF_Sharp_HighFreq_Report.md` (line 78: all
zoo families train MSE in scaler-normalized space; loss menu at line 279) and
`MF_Leaderboard_Beaters_2026_Report.md` (line 252: EMA of normalized PDE residual as a
per-instance error estimator triggering corrective solver steps — the nearest in-repo
relative of the trust gate). Neither report covers per-sample target normalization or
resampling misregistration.

## Open questions batch 3's search must serve

1. Is **per-sample (instance-wise) target normalization** of the fidelity residual
   published prior art in operator learning / neural PDE surrogates? Is RevIN-style
   reversible instance normalization already applied to *residual targets*?
2. Is there published treatment of **heavy-tailed / effective-sample-size** collapse of
   an MSE objective under a single global scaler (one sample owning ~89 % of energy)?
3. Is a **no-harm / trust gate** (predict-then-verify, fall back to the input when the
   corrector would hurt) published for PDE-surrogate correctors?
4. Has anyone published **resampling misregistration (half-pixel / align_corners)
   contaminating a super-resolution or multi-fidelity benchmark** — i.e. is our
   closed-form half-cell result already in the literature (mentor-note citations)?
