# Summary so far — stream `r2s1_direct`, batch 1

## Stream question and bar

`r2s1_direct` (class: gap) asks how well a **from-scratch condition→HF
architecture** — no LF field at test — can predict the HF field
(`mffp_autoresearch/round2/project.yaml`, streams[0]; program.md §12.1).
The launch anchor for every stream is the **best training-free floor panel
geomean = 23.06** (`state/anchors/r2s1_direct.json`,
`anchor_type: best_floor_panel_geomean`, `provisional: false`). Per-dataset
best floors (`state/anchors/floors.json`): helmholtz 3.344 (zero),
pfc 59.81 (train_mean), allen_cahn 269.20 (NN), fisher_kpp 11.99 (train_mean),
cahn_hilliard 23.18 (NN), ifc_poisson 10.05 (NN). Copy-LF skill < 1 on any
panel dataset is the headline claim (program.md §2.2–§2.3); the table says the
regime is 10–270x away from it before training starts.

`state/noise_floor.json` is `_provisional: true`
(`_source: round1-batch0-rescaled`, from LF-consuming families) — it is NOT a
numeric threshold until r2s4-B1 certifies a condition→HF 3-seed spread
(program.md §4.3, §12.4). Claims inside a floor/anchor band are noise.

## Prior cards / prior websearches

None. `experiment_cards/r2s1_direct/` and `websearches/r2s1_direct/` are empty
(batch 1 is the stream's first). In-repo literature reports read instead:

- `docs/reports/MF_Leaderboard_Beaters_2026_Report.md` — §4.2 [LF-11]
  data-efficient **multi-fidelity DeepONet** with physics-guided subsampling
  (arXiv:2503.17941): freeze LF-pretrained branch/trunk, train a small
  nonlinear merge head on HF. §3.4 notes MLP vs SIREN vs KAN backbones have
  complementary spectral strengths under limited data.
- `docs/reports/MF_Sharp_HighFreq_Report.md` — line 180: Lanthaler et al.
  (ICLR 2023, arXiv:2210.01074) prove **linear-reconstruction operator
  architectures (DeepONet, PCA-Net) are provably inefficient for
  discontinuous solution operators**; shift-DeepONet is the fix. Line 134:
  SirenFNO (arXiv:2606.11518) parameterizes the spectral kernel with an
  implicit network. These bear directly on the §12.1 design priors
  (branch–trunk, spectral/implicit decoders) on a sharp-field panel.

## Load-bearing fact discovered while reading the data (read-only inspection)

Inspecting `mf_field/factory_mffp/data/*/meta.json` + `train_l*.npz`:
`sharp__phase_field_crystal_2d` (`param_names: [r, mean_density]`),
`sharp__fisher_kpp_2d` (`[D, r]`), `sharp__allen_cahn_2d`
(`[eps, mobility, mean_composition]`) carry **no initial-condition parameters**;
only `sharp__cahn_hilliard` does (16 `ic_c*` coefficients of its 19 dims) and
helmholtz's `[wavenumber_k, source_x, source_y]` is complete by construction.
Measured on the train split: the two closest-in-condition pfc samples
(standardized cond distance 0.0124) have **relative field difference 1.149**;
fisher_kpp's closest pair (0.0124) differs by **0.343**. The same index pair in
`train_l1.npz` (LF) differs by 1.148 / 0.412 — i.e. **the per-sample random IC
lives in the LF field, not in the condition vector**. So on pfc/fisher_kpp
(and partly allen_cahn) the condition→HF map is *stochastic*: the MSE-optimal
predictor is the conditional mean, which is why `train_mean` beats
`nn_condition` on exactly those two datasets in `floors.json`. This contradicts
the program.md §12.1 aside that "each sharp `meta.json` certifies the field is
a learnable function of them" — the metas make no such statement.

## Open questions this batch's search must serve

1. Which condition→field decoder class (FiLM-FNO decoder / branch–trunk /
   modulated INR) is best-supported at N=400 and N_hf=5, and what is already
   published so a proposal is not a rebadge (program.md §13.3, 0-for-4)?
2. Is "the parametric map is not identifiable, so report against the
   conditional-mean/aleatoric floor" an established methodology, or does this
   project have to build the floor argument itself?
3. Are NN-in-condition / train-mean / zero floors an established certification
   protocol for parametric neural-operator papers (program.md §2.2 floor arms)?
