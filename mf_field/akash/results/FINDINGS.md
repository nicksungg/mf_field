# Subset benchmark — findings (10 models × 12 hard datasets, full 2500 epochs, pi_faez)

118/120 cells (allpairs × era5/pm_test timed out at 12h — its O(L²)=36-pair cost at L=9).
Metric = per-sample rel-L2 mean (lower better). Anchors: `transfer_film` (FiLM winner),
`transfer_bar` (concat).

## Data-quality flag (act on this)
- **`kuramoto_sivashinsky_generated` and `cahn_hilliard_generated` are unlearnable here** — *every*
  model scores rel-L2 **> 1.0** (worse than predicting zero) ⇒ LF and HF are effectively decorrelated
  (same failure that got `gray_scott` dropped). They add only noise; excluded from the clean ranking
  below. Recommend auditing/regenerating or dropping them.
- The **learnable sharp** sets (`euler`, `burgers_2d`, `shallow_water`) are actually well-modeled
  (~0.003–0.06) — sharp isn't the wall it looked like once the 2 degenerate sets are removed.

## Clean leaderboard (geomean over 10 learnable datasets; 7 smooth + 3 sharp)
| Rank | Model | gm_learn | smooth | sharp | ELO(12) | note |
|---|---|---|---|---|---|---|
| 1 | **mf_fno_allpairs** | **0.0094** | 0.0090 | 0.0102 | 1624 | wins 5/12; **missing era5/pm_test** (flattered) |
| 2 | mf_fno_hyperfilm | 0.0114 | 0.0116 | 0.0112 | 1549 | edges anchor on smooth |
| 3 | mf_fno_ptr | 0.0121 | 0.0128 | 0.0106 | 1589 | ≈anchor geomean, higher ELO (consistent refine) |
| 4 | mf_fno_transfer_film *(anchor)* | 0.0121 | 0.0129 | 0.0105 | 1552 | the bar |
| 5 | mf_fno_foundation | 0.0142 | 0.0158 | 0.0110 | 1563 | self-pretrain only |
| 6 | mf_fno_richardson | 0.0160 | 0.0191 | 0.0107 | 1536 | — |
| 7 | mf_fno_transfer_bar *(anchor)* | 0.0167 | 0.0199 | 0.0110 | 1455 | concat baseline |
| 8 | mf_fno_spectral | 0.0173 | 0.0184 | 0.0149 | 1465 | worst on sharp (as predicted) |
| 9 | mf_fno_lora | 0.0311 | 0.0343 | 0.0249 | 1421 | underfits |
| 10 | mf_fno_diffprior | 0.95 | 1.34 | 0.42 | 1246 | broken for point accuracy |

(Note: the historical **0.0082** is the easier 15-set benchmark — not comparable. On this hard subset
the FiLM anchor is **0.0121**.)

## Hypothesis read-out
- **allpairs (POSEIDON all-pairs) — SUPPORTED, the win.** Best geomean + ELO; wins lid-cavity, heat_local,
  euler, burgers_2d, shallow_water. Data amplification across the fidelity ladder helps. **Caveat:** #1
  partly because it skipped the 2 hardest cells (era5/pm_test timed out); its cost is the bottleneck.
  → Re-run those two with longer walltime or pair-subsampling to settle it.
- **ptr (test-time PDE residual) — SUPPORTED beyond expectation.** Beats FiLM on ELO with only a
  *placeholder* smoothness residual; biggest gains on era5/pm_test (0.0585 vs 0.0737, **−21%**) and
  ifc_poisson. → Implement the **true** governing residuals (heat/poisson/burgers/euler) — likely more.
- **hyperfilm (meta/fidelity FiLM) — NEUTRAL/slight+.** Ties the anchor, small smooth edge (wins darcy,
  poisson_local); never regresses (the safe-generalization design held). Its core "widens under HF
  scarcity" claim is **untested** → run the few-shot-HF sweep.
- **foundation (BPOM, self-pretrain) — INCONCLUSIVE.** #3 ELO is inflated by "winning" the 2 unlearnable
  sets; mid on real data. Cross-dataset hypothesis **untested** (no corpus pretrain) → corpus-pretrain next.
- **spectral (freeze low modes) — FALSIFIED, as predicted.** Worst learnable-sharp geomean; catastrophic
  on lid-cavity (0.060 vs allpairs 0.0077). Freezing LF low modes hurts where high-freq structure matters
  (shocks, vortices). Clean confirmation of the smooth↔sharp prediction.
- **richardson (continuous-fidelity + super-fidelity) — mostly FALSIFIED on full data** (0.0160).
- **lora (low-rank adapter) — FALSIFIED for accuracy** (0.0311; LF→HF gap isn't low-rank) — but truly
  0.15%-param.
- **diffprior (latent-diffusion prior) — FALSIFIED for point accuracy** (gm 0.95; ifc_poisson 76.9,
  poisson_local 122). Generative path unusable at this scale/data — keep only as a UQ tool.

## Recommended next steps
1. Settle **allpairs** on era5/pm_test (longer walltime or cap pairs to ~12).
2. **True PDE residuals for ptr/residfid** (it already helps with a placeholder).
3. **Few-shot-HF sweep** for hyperfilm (its untested core claim).
4. **Corpus-pretrain foundation** (its untested core claim).
5. Audit/drop **KS-2D & cahn_hilliard** (decorrelated LF/HF).
6. Retire diffprior/lora as accuracy contenders.
