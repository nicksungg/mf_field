# Evaluator Agent Output

- **timestamp:** 2026-06-02T20:58:46Z
- **exit_code:** 0

---

## Eval Results — before (cycle-010 baseline)

### Scores
| Dimension       | Score                  | Status |
|-----------------|------------------------|--------|
| composite_nRMSE | 0.022161472746117312   | PASS   |

### Composite: 0.022161 [PASS — matches previous best exactly]

### Interpretation
Cycle-010 baseline reproduces cycle-009-h1h2 exactly (delta = 0.000000). All 14 (model × dataset) runs hit the cache; total wall time ≈ 0s. The geometric-mean composite is driven by the per-dataset best:
- **ifc_heat** best = 0.012884 (`fno_coregionalization`)
- **ifc_poisson** best = 0.038120 (`fno_mf_stack`)

`vs_paper`: beats Takamoto et al. on ifc_heat by 5.7× (ratio 0.174), still 1.06× the paper on ifc_poisson.

### Per-family × per-dataset breakdown (nRMSE, cache=hit on all 14)
| Model                          | ifc_heat   | ifc_poisson |
|--------------------------------|------------|-------------|
| **fno_coregionalization**      | **0.01288**| 0.59780     |
| fno_coreg_residual             | 0.02627    | 0.07200     |
| mf_fno_transfer_bar            | 0.03317    | 0.08333     |
| fno_mf_stack                   | 0.03827    | **0.03812** |
| transolver_residual            | 0.11456    | 2.59235     |
| transolver_attention_fusion    | 0.14923    | 0.38181     |
| v9_baseline                    | 0.14883    | 18.50344    |

### Trend
- cycle-007 H1 (fno_coregionalization repair): composite ≈ 0.0349
- cycle-008 H1 (paper-config capacity bump): composite ≈ 0.0249
- cycle-009 H1+H2 (fno_mf_stack capacity + recipe_hash): **0.022161**
- cycle-010 baseline: **0.022161** (identical — cache hit; commit 0b6e6eb unchanged)

Composite has dropped ~37% over the last 3 cycles. Headroom now sits with **ifc_poisson**: `fno_mf_stack` at 0.0381 is the only model under 0.07 and is 1.06× paper. The runner-up family on poisson is `fno_coreg_residual` at 0.0720. Cycle-010 hypotheses should target ifc_poisson — that's where composite reduction will come from, since ifc_heat already beats paper by 5.7×.

### Artifacts written
- `.factory/research/runs/cycle-010-baseline/summary.json`
- `.factory/research/runs/cycle-010-baseline/smoke_latest.json`
