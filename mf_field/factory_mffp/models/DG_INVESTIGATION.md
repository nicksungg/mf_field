# Discrepancy-Gated Operators for Multi-Fidelity Field Prediction

An investigation into **conditioning mechanisms** for multi-fidelity (MF) neural
operators, conducted in the `factory_mffp` benchmark. Two new model families were
built and benchmarked head-to-head against the existing leaderboard: **`dg_fno`** and
**`dg_transfer`**. This document records the idea, the design, the results, and the
(partly negative) scientific conclusion.

**TL;DR.** We tried to beat the benchmark's #1 model (`mf_fno_transfer_film`) by feeding
it a richer conditioning signal — a per-pixel "where is the cheap model unreliable?"
field — delivered through learned gates. It *helped* a weak base (`dg_fno` beat its FIRE
parent) but was *redundant — even mildly harmful* — on the strong transfer base
(`dg_transfer` landed ~1.6× behind #1, winning only 2/15 datasets). The reason is clean and
reusable: **the hint only helps a corrector that cannot already see the low-fidelity model.
Transfer learning *is* the low-fidelity model, so the hint tells it nothing new.**

---

## 1. The motivating observation

On the fair benchmark (30 families × 15 datasets, per-sample rel-L2, 2500 epochs), the
two strongest fusion mechanisms each injected information in a *mismatched* way:

| model | injection mechanism | signal it injects | rank |
|---|---|---|---|
| `mf_fno_transfer_film` | **FiLM** — per-block feature modulation (the best) | global parameter vector `X` (weak) | **#1** |
| `fno_fire_distcond` (FIRE) | `torch.cat` at input (the worst) | per-pixel LF **uncertainty fields** μ/σ/quantiles (the best) | #3 |

FIRE had the **best signal through the worst delivery**; transfer-FiLM had the **best
delivery on a weak signal**. Nobody had crossed them. That cross is the whole idea.

---

## 2. `dg_fno` — the Discrepancy-Gated Operator (DGO)

Cross the two: take FIRE's per-pixel uncertainty field and inject it the FiLM way —
**modulate every spectral block with it** — plus two extensions only an operator allows.
Three gates, each answering a different design question:

- **Gate A — spatial FiLM.** Generalize the global per-channel FiLM affine `(γ,β)` to a
  **per-pixel** affine produced from the encoded uncertainty field, *added to* the proven
  global-`X` term.
- **Gate B — spectral mode-gate.** Scale each retained Fourier mode of the correction by a
  learned gain from the **uncertainty's own spectrum** — open the high-frequency bands
  where LF error is high-frequency (shocks, boundaries), keep them shut where LF is smooth.
  This is native to an FNO and impossible for a pixel-space network.
- **Gate C — heteroscedastic gain.** `HF = μ_LF + ρ(x)·δ`, with `ρ(x)` a learned spatial
  gain — the spatial generalization of the scalar `ρ` in Kennedy–O'Hagan (2000)
  autoregressive co-kriging. Doubles as a diagnostic: does `ρ(x)` light up where the true
  error is?

**Zero-init unification.** Every gate initializes to a no-op (`γ_U=0`, mode-gain `=1`,
`ρ=1`), so at step 0 DGO *is* an X-FiLM residual model and can only grow the gates if they
help. Consequently its ancestors are exact ablations — flip gates off (or swap to
input-concat) and you recover `mf_fno_transfer_film`, `fno_fire_distcond`, or `fno_additive`.

```
 uncertainty field U=[μ,σ,q10,q50,q90]
        │                  └── spectrum → U_modes
   encode → G                         │
        ▼                             ▼
  per FNO block:  spectral conv (gated by U_modes, B) + FiLM(γ,β from X ⊕ from G, A)
        ▼
       δ   →   HF = μ_LF + ρ(x)·δ      (ρ from G, C)
```

Files: [`dg_fno/model.py`](dg_fno/model.py), [`dg_fno/smoke_eval.py`](dg_fno/smoke_eval.py).

### `dg_fno` result — a real but partial win
- **geomean rel-L2 = 2.47e-2 → rank 9/31.**
- **Beats its FIRE parent** `fno_fire_distcond` (2.74e-2) on **9/15 datasets** and in geomean.
  The gates work.
- **Mechanism validated:** the gain field `ρ(x)` correlated with the true `|HF−μ_LF|` error
  (mean **+0.36**, and exactly **+1.0** on the three high-discrepancy Poisson datasets).
- **But 3× behind #1** (`mf_fno_transfer_film` 8.15e-3), dragged down by a catastrophic
  `ifc_poisson = 14.5` (the FIRE residual blows up on the Poisson value-scale collapse,
  which transfer sidesteps). Even Poisson-free it only *ties* its FIRE parent — meaning the
  gates were grafted onto the **wrong backbone**.

---

## 3. `dg_transfer` — grafting the gates onto the #1 backbone

Diagnosis from `dg_fno`: the gates are sound, but the FIRE-residual base is inferior to the
transfer base. So move the **same gates (A + B)** onto `mf_fno_transfer_film` itself.

- Keep the winning recipe **untouched**: one FNO, pretrained on abundant LF, fine-tuned on
  scarce HF, with a **separate output scaler per stage** (the re-scaling that dodges the
  Poisson collapse). The network predicts the HF field *directly*.
- Add uncertainty modulation from a **small** LF ensemble (E=3, ~8.3M params total vs FIRE's
  28M): Gate A (spatial FiLM) + Gate B (spectral mode-gate). **Gate C dropped** — there is no
  `μ_LF` residual to gate when the net predicts HF directly.
- **Zero-init ⇒ at init `dg_transfer` ≡ `mf_fno_transfer_film`** (verified: output is invariant
  to the uncertainty input at initialization). It cannot regress below #1 at the start.

Files: [`dg_transfer/model.py`](dg_transfer/model.py), [`dg_transfer/smoke_eval.py`](dg_transfer/smoke_eval.py).

### `dg_transfer` result — the Poisson fix worked, but it doesn't beat #1
- **The Poisson collapse is gone** (the primary diagnostic goal): `ifc_poisson` 0.047 (was
  14.5 in `dg_fno`), `poisson_local` 0.0037, `poisson_generated` 0.0007. Per-stage scalers did
  their job. `lid_driven_cavity` recovered (43.8 @2-epoch → 0.044 @full).
- **But it does not beat #1 — it regresses it.** Final geomean (15/15) = **1.30e-2** vs
  `mf_fno_transfer_film` **8.15e-3** (~1.6× worse), beating #1 on only **2 of 15** datasets.
  Tellingly, it falls **below even the ungated transfer baselines** (`mf_fno_transfer` 1.23e-2,
  `mf_fno_transfer_2m` 1.25e-2): the gates took a model that *starts* at #1 (zero-init) and, over
  2500 epochs on scarce HF data (5–160 samples), let the extra gate capacity **overfit** it well
  below its own backbone. The damage is worst on the climate fields (`era5`/`pm_test`: 0.098 vs
  #1's 0.072) — exactly the datasets where the *same gates helped* `dg_fno`, underscoring that the
  gates' value is conditional on the base, not the dataset.

---

## 4. The scientific conclusion

> **Uncertainty-gated modulation helps a corrector only when that corrector cannot already
> see the low-fidelity model. Transfer learning *is* the low-fidelity model (one network,
> pretrained on LF then fine-tuned on HF), so the "where is LF wrong?" hint is information it
> already carries in its own weights — redundant. FIRE freezes a *separate* corrector that
> never saw the LF model, so for it the same hint is the only window in — and it helps.**

This explains the whole arc:

| base | corrector sees the LF model? | does the hint help? | evidence |
|---|---|---|---|
| FIRE residual (`dg_fno`) | No — separate frozen corrector | **Yes** | beats FIRE parent 9/15, `ρ`–error corr +0.36 |
| Transfer (`dg_transfer`) | Yes — it *is* the LF model | **No (redundant/harmful)** | ~1.6× behind #1, wins 2/15 |

It also reframes *why transfer-FiLM is so hard to beat*: it already uses the cheap data in the
most complete way possible (the same weights become the HF model), so there is little residual
information a hint can add. The only hint that *could* help a transfer base is one it genuinely
**cannot self-derive** (e.g. the true PDE/physics residual, or a signal from a different source
than its own pretraining) — not a summary of what it already is.

---

## 5. Status & reproduction

- `dg_fno`: **complete**, 15/15 datasets, in `results/raw_bench/dg_fno__*__e2500__s42.json`.
- `dg_transfer`: **complete**, 15/15 datasets, in `results/raw_bench/dg_transfer__*__e2500__s42.json`.
- Both pass the contract (`eval/MODEL_CONTRACT.md`), an init-equivalence check, and a 2-epoch
  sanity smoke on all 15 datasets/all geometries (1-D, square, rectangular).

Run one cell (GPU node):
```bash
source scripts/env.sh
$MFFP_PY models/dg_fno/smoke_eval.py      --dataset_dir data/ifc_heat --dataset_name ifc_heat \
    --epochs 2 --out /tmp/x.json --ckpt_dir /tmp/c --seed 0
$MFFP_PY models/dg_transfer/smoke_eval.py --dataset_dir data/ifc_heat --dataset_name ifc_heat \
    --epochs 2 --out /tmp/x.json --ckpt_dir /tmp/c --seed 0
```
Gate ablations via `DG_GATES` env var (e.g. `DG_GATES=A,B`, default all). Aggregate the
leaderboard with `$MFFP_PY bench/summary_report.py` (both families are registered there).

## 6. Open thread
The DGO machinery (gates A/B/C) is validated and reusable; the question it leaves open is
**what signal deserves to flow through it on a strong base** — something the transfer network
cannot already self-derive. The PDE-residual gate is the most promising untried combination.
