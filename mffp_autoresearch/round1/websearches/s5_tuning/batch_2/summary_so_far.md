# Summary so far — `s5_tuning`, batch 2 (pre-search state)

## What the stream owns, and where the boundary is

`s5_tuning` asks "how much of the gap is knobs, not architecture?" (program.md
§4.1, §12.5). Hard scope: **knobs on existing recipes only — no new
losses-as-mechanisms, no new paradigms, no architectural changes**. Two
neighbouring streams now claim adjacent ground and this batch must not
trespass: `s7_loss` (ADR 0012) owns the *training objective* — its batch-1
verdict table already claims `C-AMP` (gain/shape-decomposed objective) and
`C-REL` (per-sample relative-L2 training loss) as ITS candidates
(`websearches/s7_loss/batch_1/report.md`, Prior-art verdict rows) — and
`s6_local` (ADR 0011) owns adding field-shaped input paths. So s5-B2's legal
territory is: **the target/output scaler and other pure preprocessing knobs on
an unchanged MSE objective and an unchanged network.**

## Where batch 1 left us

`experiment_cards/s5_tuning/batch_1/B1.json` (modes_cap 12->32 on the champion
`mf_fno_transfer_film`) is complete. Its parts 5-7 establish:

- **The knob answered, and mostly negatively.** Panel geomean 6.196 vs anchor
  6.703 (`state/anchors/s5_tuning.json`), delta -0.507 < the 0.884 geomean
  noise floor => not claimable. 100% of the movement is `ext__helmholtz_2d`,
  the one dataset whose `min_claimable_effect` is 9.695
  (`state/noise_floor.json`) — i.e. unclaimable by construction. All four
  sharp-2D datasets got slightly *worse* at cap 32.
- **A regime split**: modes_cap is a real bandwidth knob only on `ifc_poisson`
  (per-sample corr with HF 0.994, band error falls only above k=12, -14.6%
  test nRMSE); on the other five the model is a **DC (spatial-mean) predictor
  plus an uncorrelated pattern** (demeaned corr 0.001-0.13), so extra modes
  only host spurious high-k energy (1.7-18.9x more top-band energy).
- **The champion is worse than a constant-field oracle** (each test sample's
  own spatial mean) on `allen_cahn`, `phase_field_crystal`, `helmholtz`
  (part 6, `tools/dc_pattern_split.py`).
- **Part 7 `next_direction` names the batch-2 candidate explicitly**: the
  NORMALIZATION knob. Grounds recorded there: helmholtz error is 70-87% pure
  amplitude with fitted alpha 0.05-0.07 (predictions 14-21x too large in
  scale); s2-B1 independently measured an 86.5% amplitude share; per-sample HF
  norms span 408x under the single global scaler. Part 7 explicitly marks the
  modes+muP-LR branch **NOT RECOMMENDED** (measured negative sign on 5/6).

## What the recipe actually does (read from source, not memory)

`mf_field/factory_mffp/models/mf_fno_transfer_film/smoke_eval.py:136-137`:

```
scaler_lf = max(float(np.abs(Y_lf).max()), 1e-8)
scaler_hf = max(float(np.abs(Y_hf).max()), 1e-8)
```

One **global max-abs scalar per stage**, set by the single most extreme
training field; `_train` (line 82) supervises `Y/scaler` under plain
`F.mse_loss`; the LF-pretrain stage uses `scaler_lf` and the HF-finetune stage
re-derives `scaler_hf`, so the network's output scale is re-anchored between
stages. No demeaning, no per-sample or per-channel statistics, no robust
quantile. The network input is `[batch, cond_dim]` only (LF-blind at
inference, s2-B1 M1) — which is why a *per-sample* scale cannot simply be read
off an input field at test time.

## Open questions this search must answer

1. What do the reference PDE-surrogate codebases/benchmarks (PDEBench,
   PDEArena, the Well, `neuraloperator`) actually normalize, and how — global
   vs per-sample vs per-channel, max-abs vs Gaussian vs quantile?
2. Is **per-sample / condition-predicted output scale** published as a
   *normalization trick* (knob) or only as an architecture change (a scalar
   head)? The boundary decides whether s5 may propose it at all.
3. Are **robust (quantile/median) scalers** used in scientific ML in
   preference to max-abs, with evidence?
4. Is **pretrain/finetune scaler mismatch** a documented failure mode
   (normalization-statistics transfer; AdaBN-style literature is adjacent)?
5. Is "beat the constant/mean predictor" a published sanity bar for operator
   learning (so B1's constant-field-oracle finding has a citable frame)?

## Prior searches not to re-cover

`websearches/s5_tuning/batch_1/report.md` covers mode counts, spectral bias,
iFNO/AFNO/TFNO, muP-LR-vs-K, aliasing, E-UNO. `websearches/s7_loss/batch_1/`
covers loss-side amplitude handling (Eigen scale-invariant loss, band losses,
Sobolev, SSIM) — **its territory, not ours**; I will cite it for the boundary
call, not re-run its terms. The two in-repo literature reports
(`docs/reports/MF_Sharp_HighFreq_Report.md`,
`docs/reports/MF_Leaderboard_Beaters_2026_Report.md`) touch normalization only
in passing — `MF_Sharp_HighFreq_Report.md:78` records that all zoo families
train "with MSE in scaler-normalized space", and its displacement/amplitude
material is s3_warp's, not a normalization source. Nothing there answers Q1-Q5.
