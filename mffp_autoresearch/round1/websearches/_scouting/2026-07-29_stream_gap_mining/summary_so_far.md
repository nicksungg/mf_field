# Summary so far — scouting gap-mine for an 8th stream (2026-07-29)

Scope: NOT a stream websearch. Gap-mine mechanism classes for few-shot
multi-fidelity PDE field prediction that Round 1's **7 streams do not cover**,
so the operator can decide whether an 8th stream is warranted.

## What the 7 streams already own (program.md §4.1)

| Stream | Owned question | Mechanism territory it consumes |
|---|---|---|
| `s1_poisson` | why is `ifc_poisson` above the paper bar? | fidelity-ladder training (all-pairs), variance reduction at N_hf=5 |
| `s2_beyond_copy` | why does fusion lose to copy-LF on the 5 sharp-2D sets? | diagnostics; residual/normalization/spectral-wall forensics |
| `s3_warp` (ADR 0010) | does geometric alignment beat additive correction? | warping / registration / displacement fields |
| `s4_hybrid_routing` | MF composition of FNO<->Transolver hybrids | routing, MoE-over-operators, per-band/per-region gating |
| `s5_tuning` | how much of the gap is knobs? | modes_cap, loss/metric alignment, normalization, LR |
| `s6_local` (ADR 0011) | does a local (CNN/ConvNeXt) branch fix sharp-2D? | local-kernel + spectral composition |
| `s7_loss` (ADR 0012) | does an interface-aware objective fix sharp-2D? | training objectives, reweighting, physics-agnostic losses |

Pre-falsified levers, off the table (program.md §5): WNO backbone swap, LF
low-mode freezing, diffusion prior for point accuracy.

Hard constraints on any 8th-stream candidate: physics-agnostic **at test time**
(`docs/adr/0009-unknown-physics-constraint.md`); PINN family retired
(`docs/adr/0008-ignore-pinn.md`); the 6 panel datasets are fixed and read-only
(immutable 1-2); one nRMSE definition (immutable 4); contract CLI fixed
(immutable 5).

## In-round findings this scout must condition on

Source: `experiment_cards/s2_beyond_copy/batch_1/B1.json` part 5 (diagnostic,
SLURM 65991328, `falsification_verdict: falsified`).

1. **The certified champion never consumes LF at test time.** M1: for
   `mf_fno_transfer_film`, `lf_at_inference = false` on 5/5 datasets x 3/3
   batch-0 seeds; `n_field_shaped_inputs_at_eval = 0`; the only tensor entering
   the network is the `[batch, cond_dim]` condition vector. The whole panel is
   currently being attacked by an **X->HF map**, and copy-LF is the only
   LF-using entry in the ladder. "Fusion destroys LF information" is a category
   error - LF is never handed to the model.
2. **No predictor beats copy-LF anywhere.** Min skill over the entire M2 ladder
   = 3.98 (helmholtz knn1). Champion skills 4.2-16.3.
3. **Three regimes** (M2): information-bounded (`fisher_kpp`, cond_dim 2 -
   champion 4.179 ~= meanfield 4.107 ~= knn10 4.153, gap 6x below the 0.418
   floor); training-buys-nothing (`pfc` - champion 11.511 ~= knn1 11.299, and
   **training-free knn10 = 8.466 BEATS the champion by 3.045**, above the 1.151
   floor); training-wins (`allen_cahn` champion better by 4.74;
   `cahn_hilliard` better by 3.05).
4. **The excess is LOW-band, not high-k.** M3: `R_low > 1` on 5/5 datasets x
   3/3 seeds (11.2-209.6). Error energy share in band 0 is 0.39-0.9996. The
   band-split direction is NOT licensed. Secondarily, the champion *injects*
   spurious high-k energy that the lookups do not.
5. **Not interface-localized.** M4: champion error-mass/area ratios never
   exceed ~1.3x at the interface stratum; `pfc` excess is mid-distance and
   shape-identical to the lookups'.
6. **helmholtz is 86.5% amplitude/normalization** (M5a: champion nRMSE 6.202
   raw -> 0.839 under a per-sample optimal scalar rescale).
7. **No LF<->HF pairing defect** (M5b) - the datasets are not buggy.
8. `nn_over_random` (X-informativeness): fisher_kpp 0.937, cahn_hilliard 0.865,
   helmholtz 0.419, allen_cahn 0.201, pfc 0.023.

## Sample-count correction the operator brief should absorb

The brief says "feasible at N_hf = 5-25". Measured in the same card,
`n_train_hf = 400` on all five beyond-copy panel datasets (helmholtz 96^2,
allen_cahn / fisher_kpp / cahn_hilliard 256^2, pfc 128^2). **Only `ifc_poisson`
is N_hf = 5** (program.md §12.1). This materially widens what is feasible:
retrieval banks, in-context prompting, and fine-tuning recipes all have 400 HF
pairs to work with on 5/6 panel datasets. I assess each candidate under both
regimes.

## Prior in-repo literature (cite, don't re-derive)

- `docs/reports/MF_Leaderboard_Beaters_2026_Report.md` §4.2 already surveys
  data-efficient transfer: F-Adapter (arXiv:2509.23173), Poseidon
  (arXiv:2405.19101), DPOT (arXiv:2403.03542), **VICON in-context operator
  nets (arXiv:2411.16063)**, MOFS few-shot multi-operator (arXiv:2508.01211).
  §3.4 covers uncertainty-aware residual learning (FIRE-relevant).
- `docs/reports/MF_Sharp_HighFreq_Report.md` §3.6 proposes a **patch-dictionary
  / VQ-codebook** retrieval mechanism (CodeFormer transplant, arXiv:2206.11253)
  - the closest in-repo relative to angle (c).
- These are prior websearches by another agent. Their citations were not
  fetched in THIS loop, so per program.md §13.3 they do **not** count as this
  report's prior-art evidence; I re-fetch anything I lean on.

## Open questions this scout must answer

- (a) Is cross-dataset / foundation-style pretraining (the deferred `s8_data`)
  supported by literature at panel-relevant scale, and is it fair under
  immutable 1?
- (b) Uncertainty-weighted / trust-region fusion: when to trust LF vs model.
- (c) Retrieval-augmented / nonparametric hybrids - motivated by
  knn10-beats-champion on pfc.
- (d) Meta-learning / in-context operator learning for new-PDE adaptation.
- (e) Anything else recurring in 2024-2026 MF operator learning that none of
  (a)-(d) or the 7 streams cover.
