# Summary so far — `s1_poisson`, batch 3 (pre-search state)

## Where the stream stands (from `experiment_cards/s1_poisson/batch_2/B2.json`)

B2 (5 arms, one seed-0 job, 200-epoch smoke) closed the headline gap:
`allpairs__per_level` = **0.034250 nRMSE = skill 0.9514** vs the paper bar 0.036
(`5_actual_result.per_arm`), i.e. round-1 success criterion 1 is
**provisionally met (single seed, no CI, ADR 0004)**. Both pre-registered clauses
confirmed: F1 (per-level vs shared target scaler) 20.3x the certified floor, F2
(all-ordered-pairs vs two-level) 5.13x the floor; the 2x2 interaction is +4.194
skill = 17.5x floor (`5_actual_result.contrasts`). Anchor for the stream is
`state/anchors/s1_poisson.json` = **1.5656 skill / 0.056363 nRMSE**
(3-seed certified); floor `state/noise_floor.json:ifc_poisson.min_claimable_effect`
= **0.23990756 skill units = 0.0086367 nRMSE**. Stretch bar 0.018 (IFC-GPODE) is
**1.90x away** (`6_analysis`, SCOPE item).

Mechanism, settled in part 6: the win is **resolution-axis supervision in tag
space** — 70 extra (X, y) points at 16^2/32^2 teach `X -> y(X; resolution)` where
there are 100/50/20 samples — **not** defect correction (the ifc_poisson test
split ships only fidelity 64, and train levels are not index-aligned, so a
per-sample defect is undefined; `7_gap_and_future.cross_stream_notes` item 1).
The `f_tgt` axis is a finite amplitude budget; per-level target standardization
stops the discretization gain law from spending it.

## The B3 card class prescribed by part 7 (`next_direction`)

A **model** card: freeze `per_level` + `allpairs`, add **one head predicting a
per-sample scalar gain g(X)** applied to the field output, **fitted on the 175
pooled ladder rows** (where each level's own scaler already puts targets at
comparable amplitude) rather than on the 5 HF rows. Quantified motivation, all
from part 6 measurements: **57.10 %** of the winning arm's remaining squared
error is a per-sample scalar gain; per-sample **oracle** gain gives 0.022917
(skill 0.6366, hard ceiling); the gain is **LOO-ridge linear in the 5-D
condition vector at R^2 0.9190 -> 0.02431 (skill 0.6752)**; gain distribution mean
0.99307, std 0.03046, range [0.90123, 1.03765]; **n_hf_train = 5 vs cond_dim+1 = 6**
is the whole design constraint. Available effect is only **0.0099-0.0113 nRMSE**
against a **0.0086367** floor — a demanding clause, so part 7 requires the
negative reading be pre-registered too ("the gain is a property of the HF solve
that the lower levels do not share").

Ruled out **by direct measurement** for this dataset (do not re-propose):
interface-aware losses, local/CNN branches, LF-consuming defect correctors,
spectral-mode capacity (part 6; `tools/interface_locality_profile.py` shows all
arms bulk-dominated, error falling monotonically with |grad HF|; 99.78 % of
target energy in radial band 0).

## What batches 1-2 already searched (do not re-cover)

- `websearches/s1_poisson/batch_1/report.md`: D1 all-ordered-pairs =
  `preempted-but-MF-composition-open`; D2 telescoping/MLMC-NO + MFRNP =
  `preempted`; D3 seed-ensembling = `preempted` + collides with sec 4.4.
  **Unresolved and material**: which method owns 0.036 vs 0.018 — the engine
  returned "IFC-ODE2 at m = 1 and m = 2.14 is 0.036 vs 0.018", both PDF fetches
  failed. Batch 3 task (d) reopens exactly this.
- `websearches/s1_poisson/batch_2/report.md`: per-level target normalization =
  `preempted-but-MF-composition-open`; h^p-hardcoded scaling = `preempted` (GRE);
  the 2x2 factorial = `novel` (weak, design-level); training-free matched-level
  lookup floor = `novel`, report-don't-claim. Framing asset already fetched:
  classical MF **models** the level ratio as rho (AR1 `y_high = rho(x)*y_low + delta`,
  https://smt.readthedocs.io/en/latest/_src_docs/applications/mfk.html;
  NARGP's input-dependent rho_t(.)). Dead-end rules: use `arxiv.org/abs` or
  `/html`, never `/pdf`; sciencedirect 403; springer 303; pmc needs the
  `pmc.ncbi.nlm.nih.gov` host.
- `websearches/s5_tuning/batch_2/report.md` (adjacent territory, must be
  respected): RevIN-style per-sample normalize/denormalize = the *knob* framing;
  **APEX** (https://arxiv.org/abs/2605.26732) extracts a per-sample **amplitude
  anchor from a lower-frequency neural operator's prediction** in an explicitly
  target-scarce MF regime — the strongest known preemption threat to a gain
  head; s5's territory ruling: *a learned scale head is architecture (s6/s3),
  not a knob*. B3 is a model card, so the head is legal here, but the ruling
  means s5 has already conceded the head to another stream and the novelty claim
  must be narrower than "per-sample output scaling".
- In-repo prior sweeps (`docs/reports/MF_Leaderboard_Beaters_2026_Report.md`):
  [U-1] **REEF-GP** post-hoc GP on a *frozen* operator's residuals
  (arXiv:2606.17513); [U-2] **MF quantile regression via a local quantile link**
  (arXiv:2605.10406) — "estimating a level function that is smoother — hence
  learnable from scarce HF data — when LF and HF conditional distributions share
  shape". Both are nearest-neighbour threats to (a) and (b) and must be fetched
  first-hand this loop before they can be cited.

## Open questions this loop must answer

1. Is a **post-hoc per-sample scalar-gain head on a frozen operator** published?
2. Is **fitting a calibration/scale parameter on lower-fidelity rows and
   transferring it to HF** published (hierarchical borrowing of strength for
   calibration parameters, as opposed to for GP means)?
3. Does the literature warn that rho / the discrepancy scale is **level-dependent**
   (recursive co-kriging fits a separate rho_t per level) — i.e. is there a cited
   reason the ladder-fitted gain law will *not* transfer? (Adversarial: this is
   the card's own pre-registered negative.)
4. Honest small-N: what does the calibration literature say about fitting ~6
   parameters with 5 points, and about LOO estimates as headroom?
5. **IFC-GPODE**: what is its actual mechanism, and does it hold anything the
   current base lacks? Also settle the 0.036/0.018 attribution if possible.
