# Summary so far — `s4_hybrid_routing`, batch 2

## Where the stream stands (from B1's completed card)

`experiment_cards/s4_hybrid_routing/batch_1/B1.json` measured the built family
`fno_transolver_seq` (FNO-FiLM base + zero-init, alpha-gated Transolver
corrector on out-of-fold LF->HF residuals) on the panel at seed 0 (ADR 0004
single-seed). Anchor: `state/anchors/s4_hybrid_routing.json`, champion panel
geomean **6.703 [6.219, 7.102]**. Floors: `state/noise_floor.json`
(`min_claimable_effect` = allen_cahn 1.633, pfc 1.151, fisher_kpp 0.418,
cahn_hilliard 0.553, helmholtz 9.695, ifc_poisson 0.240).

Four B1 mechanism results define what batch 2 may propose (card part 7):

1. **The Transolver corrector's win was a lossy re-derivation of copy-LF, not
   fidelity-gap modelling.** The correction is collinear with `copylf - base`
   (cosine 0.54-0.83) and orthogonal to `hf - copylf` (cosine <= 0.02) => the
   implemented mechanism's ceiling is skill 1.0; attained 3.10-4.20. A single
   scalar `base + a*(copylf - base)` matches the whole corrector on pfc and
   beats it on fisher_kpp.
2. **The alpha gate's "validation" split was inside the memorised training
   set.** `smoke_eval.py:354` fine-tunes stage 1 on ALL of `X_hf`, then splits
   `val_idx` (`:391-392`); on `sharp__cahn_hilliard` the base is 0.008648
   in-sample vs 0.500684 on test (57.9x). The gate's veto there was WRONG --
   the vetoed `alpha_ls = 1.1027` is the test optimum to 0.9% (-43%, skill
   5.56 -> 3.16), and no test data entered `alpha_ls`.
3. **The shrinkage line search must be KEPT.** On pfc `alpha_ls = 0.9944`
   scores 1.066448 vs the shipped 0.125893 -- an 8.47x regression. So the
   licensed repair is *split repair with shrinkage retained*, not
   "use the least-squares weight".
4. **Spatially-resolved routing is REFUSED by measurement** (card F11,
   `tools/routing_headroom.py`): honest per-pixel alpha field = -1.31% on
   fisher_kpp and LOSES 6.18% / 3.54% on pfc / cahn_hilliard; per-sample oracle
   <= 5.33%; in-sample per-pixel upper bound <= 4.40%. All inside every sharp
   dataset's 10%-relative floor. s6's `trust_gate_headroom.py` reaches the same
   verdict from base = copy-LF (<= 4.1%, negative on cahn_hilliard).

Part 7 licenses exactly two directions: **LICENSED-1** repair the gate's
scoring split (hold `val_idx` out of the stage-1 HF finetune; keep shrinkage);
**LICENSED-2** dense LF input instead of the 1024-point cloud (`n_ctx = 1024`
= 6.25-25% of the LF grid, and the recovered LF-direction fraction tracks that
coverage: pfc 25% -> cosine 0.834 / R^2 0.906; cahn_hilliard and fisher_kpp
6.25% -> 0.642/0.538 and R^2 0.43/0.30).

## Prior search coverage (do not re-cover)

`websearches/s4_hybrid_routing/batch_1/report.md` (4 iterations) already
settled: MoE-over-operator-experts routing is mainstream (MoE-POT
arXiv:2510.25803); per-band spectral routing published (SPAMoE
arXiv:2604.07421); per-location hard spectral-vs-local routing published
(U-HNO arXiv:2605.12965); spatially-variant gating by localized expert
performance published (arXiv:2508.21249); FNO+ViT / FNO+conv+attention
frequency-complementary sequential hybrids published (arXiv:2602.11197,
arXiv:2311.12902); LGFNet (arXiv:2603.29303) does LF-as-low-frequency-carrier
+ fidelity-gap delta learning with local window + global self-attention and NO
router; MF operator learning explicitly disclaims routing (arXiv:2507.07292).
Batch 1's D2/D3 (LF-conditioned spatial routing; per-band fidelity routing) are
now moot -- D2 is refused by measurement, D3 is the pre-falsified low-mode
freezing lever (program.md section 5).

`websearches/s6_local/batch_2/report.md` (verdict iv) established that
out-of-fold gate/combiner fitting is **Wolpert 1992's founding requirement**,
citable through a fetched paper (arXiv:1106.1684). This batch must extend that
to (a) *shrinkage/line-search* gates and (b) the MF-corrector setting, and must
not re-derive the plain stacking rule.

In-repo lit: `docs/reports/MF_Sharp_HighFreq_Report.md:102` already flags the
attention families' bottleneck -- "all cross-fidelity information squeezes
through 16-32 slice tokens" -- which is exactly LICENSED-2's premise;
`:141`/`:395` cite Transolver (arXiv:2402.02366) as the source paper.

## Cross-stream boundaries

s6 owns local dense-LF defect correction (B1 geomean 0.2346); s2 owns the
LF-residual FNO control + retrieval floors. What s4 still uniquely owns: the
**Transolver/attention corrector class**, **cross-attention context
mechanisms**, and the question of whether **attention (nonlocal,
content-adaptive) adds anything over local convolution** for the fidelity-gap
residual. B1's one datapoint on that: fisher_kpp's band-1 nonlinearity was the
single place the NN beat the LSI filter.

## Open questions this search must answer

- Is *properly-split, shrunk* ensemble/gate-weight fitting (James-Stein /
  ridge / non-negativity-constrained stacking) published for operator learning
  or MF surrogates?
- Is there published evidence on **context density** for attention-based
  operators consuming a coarse field (full field vs subsampled points)?
- Is there any **head-to-head attention-vs-convolution** result for
  residual/defect correction on regular grids?
