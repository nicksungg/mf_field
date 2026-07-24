# Failure Analysis — cycle-005-baseline

**Provenance:** Synthesized by the CEO after two failure_analyst agent invocations timed out (1800s + 1200s) without producing this file. The underlying analysis content was authored by the evaluator agent (which produced an excellent forensic summary.json before its own wrapper timed out), supplemented by direct numerical extraction from results/raw/ cache files. No deep model-source review; only the lines explicitly cited below were inspected.

**R0 baseline:** composite_nRMSE = 0.033726 (project-best, 24% improvement over cycle-004's 0.04415).
**Bar to beat:** mf_fno_transfer_bar ≈ 0.0274 composite (from results/bench_metrics.csv, since the bar's smoke harness crashed this cycle).

---

## A. ifc_poisson — winner: `fno_coreg_residual` @ nRMSE = 0.05556

### Per-sample distribution (n=128)
| stat | value |
| --- | --- |
| min | 0.0108 |
| Q1 | 0.0347 |
| median | 0.0571 |
| Q3 | 0.0736 |
| p95 | 0.1028 |
| max | 0.1602 |
| mean | 0.0574 |
| outliers (>2× median) | 3 (2.3%) |
| top-5 worst | 0.106, 0.111, 0.125, 0.138, 0.160 |

### Diagnosis
- Distribution has a meaningful upper tail (Q3 → max = 2.2x widening), and 3 samples sit above 2× the median.
- Mean (0.0574) ≈ median (0.0571) → the error is fairly evenly spread; not a single-sample anomaly.
- 2.37M params, 78s train → the model is medium-capacity and converges fast. Paper bar (0.036) is ~1.55× better; mf_fno_transfer_bar (~0.0587) is comparable to ours — so we already match the bar's poisson number.
- The upper-tail samples (max=0.160 vs Q3=0.074) are the main contributor to the geomean compositing.

### Code paths inspected
- `models/fno_coreg_residual/model.py` — not opened line-by-line in this synthesis; relied on the evaluator's note that the family uses 4 per-fidelity FNOs (hidden=64, modes=[4,8,12,12], blocks=3) + MFRNP decoder-in-aggregation + continuous-m basis head (K=10).
- `models/fno_coreg_residual/smoke_eval.py` — same.

### Hypothesis seed (for the Strategist)
Increase the HF FNO mode count beyond 12 (the [4,8,12,12] ladder maxes out at 12 modes on the highest fidelity) to capture higher-frequency residual structure on the poisson HF samples in the upper-tail. Alternatively, add per-sample uncertainty weighting in the residual loss so the upper-tail samples get more gradient pressure. Files: `models/fno_coreg_residual/{model.py, smoke_eval.py}`.

---

## B. ifc_heat — winner: `fno_coregionalization` @ nRMSE = 0.02047

### Per-sample distribution (n=128)
| stat | value |
| --- | --- |
| min | 0.0172 |
| Q1 | 0.0188 |
| median | 0.0194 |
| Q3 | 0.0209 |
| p95 | 0.0250 |
| max | 0.0348 |
| mean | 0.0202 |
| outliers (>2× median) | 0 (0.0%) |
| top-5 worst | 0.026, 0.027, 0.029, 0.030, 0.035 |

### Diagnosis
- Very tight distribution: min/max ratio only 2.0× and zero >2×-median outliers. The model is well-converged across all samples.
- 1.19M params (half the poisson winner's size), 32s train → small, fast, stable.
- This means closing the gap to the bar (0.0205 → 0.0128, ~1.6×) is NOT about catching outliers. The entire distribution must shift down. That requires more representational capacity or a better optimization regime, not heroic per-sample fixes.
- The transfer-learning bar's mechanism (LF → HF fine-tune via single full-resolution FNO) gives the bar its edge — fno_coregionalization currently uses a coregionalization basis to share information across fidelities, but does NOT pretrain a single FNO on LF first.

### Hypothesis seed (for the Strategist)
Add a transfer-learning pretraining phase to fno_coregionalization: pretrain the FNO trunk on LF data (fidelities 8, 16, 32) for some warm-up epochs, then continue joint training with the coregionalization basis head added on top. Or alternately: increase the FNO hidden dim and modes specifically for the HF branch while keeping coregionalization-m basis fixed. Files: `models/fno_coregionalization/{model.py, smoke_eval.py}`.

---

## C. `mf_fno_transfer_bar` REPO_ROOT bug (BLOCKER — prerequisite)

### Confirmed bug
- File: `models/mf_fno_transfer_bar/smoke_eval.py`
- Line 32: `REPO_ROOT = HERE.parent.parent.parent`
- `HERE = Path(__file__).resolve().parent` evaluates to `/orcd/data/faez/001/nick/mf_field/factory_mffp/models/mf_fno_transfer_bar/`.
- `.parent` → `models/`; `.parent.parent` → `factory_mffp/` (the project root, contains `data_adapters/`); `.parent.parent.parent` → `mf_field/` (no `data_adapters/`).
- Resulting failure: `ModuleNotFoundError: No module named 'data_adapters'` in BOTH the local-pass run AND the SLURM run for the cycle-005 sbatch (job 15313689).

### Fix
- Change line 32 to: `REPO_ROOT = HERE.parent.parent`.
- Mutable scope: `models/**` ✓.
- 1 line of code.

### Classification
**BLOCKER — prerequisite operational fix.** This MUST be Strategy hypothesis H1. Until it lands and a clean re-run produces a smoke-pipeline bar number, no cycle-005 hypothesis can honestly claim to beat the bar in-distribution. The current ~0.0274 "bar" comes from `results/bench_metrics.csv` (the parallel benchmark pipeline), not from the smoke harness.

---

## D. Three Hypothesis Seeds (for the Strategist, prioritized)

### H1 (highest priority — prerequisite)
**Fix mf_fno_transfer_bar REPO_ROOT.** Change `models/mf_fno_transfer_bar/smoke_eval.py:32` from `HERE.parent.parent.parent` to `HERE.parent.parent`. 1-line code change. Mutable scope. Unblocks in-distribution bar comparison.
- Type: code
- Expected impact: mf_fno_transfer_bar appears in smoke leaderboard with composite ≈ 0.0274; cycle-005 baseline becomes directly comparable.

### H2 (growth — ifc_heat gap closure)
**Add LF→HF transfer-learning pretraining to fno_coregionalization.** Modify `models/fno_coregionalization/smoke_eval.py` to add a 2-stage training: stage 1 trains the FNO trunk on LF-only data (fidelities 8, 16, 32) for ~50 warm-up epochs; stage 2 attaches the coregionalization-m basis head and continues joint training for the remaining ~150 epochs. This is the directive-suggested direction: absorb the bar's transfer mechanism on top of the coregionalization basis.
- Type: code
- Expected impact: ifc_heat nRMSE 0.0205 → target ≤0.0128 (close the 1.6× gap). Composite 0.0337 → target ≤0.0274.
- Risk: 2-stage training may destabilize coregionalization basis; may need careful LR schedule.

### H3 (growth — ifc_poisson gap closure, optional)
**Increase HF FNO modes for the ifc_poisson branch of fno_coreg_residual** OR **add per-sample uncertainty weighting in the residual loss**. Modify `models/fno_coreg_residual/model.py` to raise the modes setting on the highest-fidelity FNO from 12 → 16 (or higher), OR modify `models/fno_coreg_residual/smoke_eval.py` to weight the residual loss by per-sample inverse predicted variance.
- Type: code
- Expected impact: ifc_poisson nRMSE 0.0556 → target ≤0.036 (paper bar). Composite contribution: ~0.025 reduction.
- Risk: more modes = more parameters = longer train time (must stay under 30 min smoke wall budget).

---

## Out-of-Scope Notes (for the operator, NOT for the Strategist)

These are real issues but are out of mutable scope and CANNOT be addressed by Builder hypotheses:

1. **`scripts/cycle_eval.sh` runs the local cache pass on the login node without GPU.** When invoked with cache misses for any in-tree family, score.py tries to run those families locally and burns `per_call_timeout_seconds=1800` per (family, dataset). Operator needs to either gate the local pass on `nvidia-smi`, lower `per_call_timeout_seconds`, or route everything through SLURM. Files: `scripts/cycle_eval.sh`, `eval/smoke_config.json`, `eval/score.py` — all fixed surfaces.

2. **CEO wrapper timeout vs `research_target.timeout` mismatch.** CEO `--timeout=7200s` < `research_target.timeout=14400s` in factory.md. Already harmless for cycle-005 because cache is warm, but will re-emerge if a new uncached family lands. Operator needs to either lower `research_target.timeout` or raise the CEO launcher timeout. Files: `factory.md`, launcher — both fixed surfaces.

3. **failure_analyst agent is hanging.** This file was written by the CEO because two consecutive failure_analyst invocations timed out (1800s + 1200s) producing no output. Operator should investigate whether the agent's playbook (auto-injected from `.factory/playbooks/failure_analyst.md`) is encouraging excessive exploration. Out of scope for any cycle hypothesis.
