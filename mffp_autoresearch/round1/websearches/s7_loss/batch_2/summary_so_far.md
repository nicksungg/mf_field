# Summary so far — `s7_loss`, batch 2 (pre-search state)

## Where the stream stands (B1 = FALSIFIED, mechanism fully resolved)

s7_loss (program.md §12.7, ADR 0012) asks whether a **training objective**
change — scoring never changes (§2.1 immutable) — fixes sharp-2D fusion.
B1 (`experiment_cards/s7_loss/batch_1/B1.json`) tested `amp` λ=4, a per-sample
relative + explicit-gain objective, on the champion substrate
(`mf_fno_transfer_film`, one-line loss delta at `smoke_eval.py:96`). Verdict:
**falsified + cratered**. Card part 6 / the mechanism handoff
(`worktrees/s7_loss/B1/notes/handoff_experiment_mechanism_analyzer.md`)
resolve the mechanism completely:

- `amp(λ)` reduces exactly to `L = (1−c²) + λ(r−c)²`, `r = ‖p‖/‖y‖`,
  `c = cos(p,y)` (residual 4.26e-14). Stationary points: the true field **and
  the origin**. For λ>1 the origin's escape drive is `2λ/(λ−1)·r → 0`, and
  29 % of `sharp__allen_cahn_2d` samples sit where descent *reduces* the
  target-aligned component. Both pathologies are **algebraically impossible at
  λ=1**. An untrained FNO starts at r≈0, c≈0 — on the bad stationary point.
- The pfc / cahn_hilliard "collapse" is **not** loss-induced: an MSE-trained
  model of the same family collapses on the same samples (overlap 1.00 / 0.92,
  Spearman 0.979 / 0.810). Separator = pfc's uniform/crystal bifurcation
  (62/38 test) and cahn_hilliard's *smooth* samples (sharpness AUC 0.099),
  visible from the LF field, invisible to the condition vector.
- Helmholtz gains are an artifact: 97.75 % of A1a's helmholtz gain over the
  champion is reproduced by predicting **zero** (zero-predictor skill 3.035
  beats the seed-0 champion's 18.826).

**Standing design rule (card part 6, M6)**: measure the target-norm spread
before adopting any per-sample-normalized objective — `hf_norm_spread ≥ ~10`
requires a **denominator floor** (the two collapsed datasets: 22.7 and 5017);
`≲ 3` makes the objective a no-op (the four healthy ones ≤ 2.55; on
cahn_hilliard the relative weighting differs from MSE's by 1 %); **λ ≤ 1
always**; never apply it unchecked to the LF-pretrain stage.

**PRE-FALSIFIED for B2** (card F5+F6+F8): re-proposing a per-sample-normalized
objective aimed at `sharp__phase_field_crystal_2d` or `sharp__cahn_hilliard`.

## Open question inherited (card part 7)

Normalization vs λ>1 disambiguation: one 200-epoch **A0 (λ=1)** run on
`sharp__allen_cahn_2d` alone, seed 0, same code_hash (~10 min GPU), with three
pre-registered outcomes (a) ≈0.26 nRMSE → λ>1 is the sole cause; (b) ≈1.0 →
per-sample normalization is fatal at high spread regardless of λ; (c) between
→ both contribute and the stream should stop. This arm needs **no novelty** —
it is a measurement of this project's own falsified lever — but any *new*
objective proposed alongside it does.

## Round-wide amplitude/normalization theme (5 data points)

s1_poisson-B1 (amplitude-channel capture), s2_beyond_copy-B1 M5a
(`amplitude_share_of_error` 0.865 helmholtz; `alpha_mean` 0.73 pfc / 0.76
cahn_hilliard — systematic **under-gain**), s3_warp-B1 (408× per-sample ‖u‖
spread against one global `scaler_hf` = 7.38), s5_tuning-B1 (cap-32 helmholtz
gain closed by a per-sample rescale), s7_loss-B1 (this card). The **amplitude
calibration** direction (predict-then-rescale, output-gain heads) is live and
architecturally distinct from the falsified relative-loss lever;
`experiment_cards/s1_poisson/batch_3/B3.json` is currently running a *post-hoc,
closed-form ridge* gain head (`mf_fno_ladder_gain`) whose prior-art verdict is
already `preempted-but-MF-composition-open` (ROMES 1405.5170, LR-MFS
1705.02956, IFC 2207.00678, APEX 2605.26732). A **jointly trained, loss-level**
gain term is the s7 analogue and must be vetted separately.

## Adjacent stream signal

s2_beyond_copy-B2's LF-residual mechanism (`lf_resid_fno`) posted geomean
0.380 on the beyond-copy set — that is *residual prediction* (architecture:
LF enters the model / the output parameterization), which belongs to s2.
The s7-shaped neighbour is **residual supervision in the loss** (weighting or
normalizing the objective by the LF-referenced residual while the prediction
target stays the field). Prior art must separate the two.

## Batch-1 websearch verdicts to build on

`websearches/s7_loss/batch_1/report.md`: C-REL **preempted**; C-STRUCT
(Sobolev/H1/SSIM/Charbonnier) **preempted** *and* empirically contraindicated
(s2-B1 M3: excess error in the LOWEST band 5/5; M4: pfc error not
interface-peaked); C-AMP and C-BAND **preempted-but-MF-composition-open**;
C-LFANCHOR degenerate while the champion is LF-blind at inference. Documented
failure modes of loss-only interventions to re-use:
https://arxiv.org/html/2511.08753 (over-constraint OOD; conflicting
time/frequency gradients; loss cannot repair architectural truncation).

## In-repo literature reports (do not re-derive)

`docs/reports/MF_Sharp_HighFreq_Report.md` proposes P2
`mf_fno_transfer_sharploss` (Charbonnier + |∇LF| weight map + focal-frequency
+ frequency continuation) and radially-binned spectral losses (LOGLO-FNO
arXiv:2504.04260); `docs/reports/MF_Leaderboard_Beaters_2026_Report.md` ranks
IRNO's **progressive spectral loss** (arXiv:2605.24041) #1 for high-frequency
and notes it is transferable to any residual family. Both are prior websearches
by another agent — cite, don't re-derive. Note B1 already made the
interface/spectral family the *lower*-ranked branch.

## Thresholds any falsification clause must clear (`state/noise_floor.json`)

geomean floor 0.884; per-dataset `min_claimable_effect` (skill units):
`sharp__phase_field_crystal_2d` 1.151, `sharp__allen_cahn_2d` 1.633,
`sharp__fisher_kpp_2d` 0.418, `sharp__cahn_hilliard` 0.553, `ifc_poisson`
0.240; `ext__helmholtz_2d` 9.695 → **report-only**, no numeric claim. There is
no `state/anchors/s7_loss.json`; B1 used the champion's certified panel
geomean (6.703 anchor at `state/anchors/s5_tuning.json`).

## Open questions this batch's search must answer

1. Is a **denominator-floored / clamped** relative loss (rel-MSE + ε) novel, or
   is it standard practice with a name and a citation?
2. Is a **continuously tempered** per-sample weight `w_i = ‖y_i‖^{−2β}`
   (β ∈ [0,1]) — an explicit interpolation between MSE and rel-MSE with an
   effective-sample-fraction control — published?
3. Is a **jointly trained loss-level gain/amplitude term** for neural PDE
   surrogates preempted (distinct from s1-B3's post-hoc head)?
4. Are there **published negative results** on relative-error training for
   operator learning that corroborate B1's origin-stationary-point mechanism?
5. Is **loss-level residual/LF-referenced supervision** distinguishable in the
   literature from residual *prediction* (s2's mechanism)?
