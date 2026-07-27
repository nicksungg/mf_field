- **One SOTA field-prediction backbone** — e.g. Transolver, FNO/UNO/F-FNO, OFormer, MeshGraphNet, GNO, Geometric Latent Diffusion, SIREN/FilmNet, DeepONet, transformer-PDE solvers, etc.
- **One (or more) multi-fidelity ML concept** — e.g. residual learning between fidelities, coregionalization, in-context regression over fidelity context, transfer learning across fidelities, hierarchical priors, gated/attention fusion, neural-process-style stacking, score-matching diffusion priors over the residual, autoencoder fusion, distribution-conditioned in-context (FIRE-style).
- Researcher: fetch the per-fidelity nRMSE tables from li2022ifc (Infinite-Fidelity Coregionalization, NeurIPS 2022, arXiv:2207.00678) for `ifc_heat` and `ifc_poisson`, append to `baselines/paper_baselines.json` under each dataset's `splits` key. Without these the smoke loop's `vs_paper` view stays null and we have no SOTA-comparison signal.
- Researcher: add a row for **FIRE — Multi-fidelity Regression with Distribution-conditioned In-context Learning using Tabular Foundation Models** (Sung et al.) to `papers_summary.csv`. This is one of the methods the Strategist should adapt to field prediction.
- Researcher: WebSearch for additional 2024-2026 multi-fidelity field-prediction papers not yet in `papers_summary.csv`. Append rows.
- `transolver_residual` — Transolver backbone, additive residual learning between fidelities (predict HF − LF instead of HF directly). Different from v9 because it's a hard residual, not a soft gated prior.
- `mfgnn_residual` — Graph operator backbone + residual learning across mesh fidelities (taghizadeh2024mfgnn, gladstone2024mfgunet).
- `oformer_attention_fusion` — OFormer / attention-based PDE solver + cross-fidelity attention fusion.
- `transolver_diffusion_prior` — Transolver + score-matching diffusion prior over the HF residual.
- `siren_film_fidelity` — SIREN / FilmNet conditioned on fidelity index, residual ladder LF→HF.
- `fire_field` — Adapt FIRE in-context regression to field prediction by tokenizing patches/coords; foundation-model-style prior with distribution conditioning. Inspiration: Sung et al. FIRE.
- `deeponet_branch_fidelity` — MF-DeepONet branch network with fidelity-conditioned trunk (yang2025mfdeeponet).
- `transolver_pinn_residual` — Transolver + multi-fidelity PINN residual loss (penwarden2022mfpinns / imanov2026mfbpinn).
- `transolver_autoencoder_fusion` — Transolver decoder + MF-AE fusion of latent fidelity embeddings (nietocentenero2025mfae).
- Once 2–3 families exist that beat v9 on ifc_heat or ifc_poisson, expand `eval/smoke_config.json` to include a third smoke dataset (e.g. `poisson_local` once an `npz_l5` loader is wired up).
- Builder: when adding a new family that needs the npz datasets, write a generic `models/<family>/data.py` that handles both `ifc_raw` and `npz_l*` layouts (`references/v9_baseline/mfrnp_npz_data.py` is a starting reference, but reimplement cleanly).
- Re-verify cycle-002 H3 baseline (0.04420 on experiment/4-fno_coreg_residual @ 0c46f43) under a clean from-scratch run. The cycle-002 H3 verdict's reported fno_coreg_residual_train_seconds: {ifc_heat: 139.7, ifc_poisson: 25.0} indicates the baseline was almost certainly trained under the same checkpoint-resume contamination pattern observed (and resolved) in cycle-003 H1 — poisson trained for only 25 seconds is not 200-epoch-from-scratch. Required: checkout experiment/4-fno_coreg_residual, clear checkpoints/fno_coreg_residual/{ifc_heat,ifc_poisson}/ entirely, clear results/raw/fno_coreg_residual__*_e200_s42_*.json, run sbatch --wait eval/run_smoke.sbatch, and record the clean numbers as the verified project-best baseline. The clean baseline may be worse than 0.04420 — if so, that's the real bar cycle-004 must beat. Cycle-004 prerequisite. Mutable surface: none (this is an operational task; runs scripts/eval as fixed surface, which is read-only — the work is checkpoint hygiene plus an eval run, not code changes). Type: operational. Execution step: 'git checkout experiment/4-fno_coreg_residual && rm -f checkpoints/fno_coreg_residual/ifc_heat/{best,last}.pt checkpoints/fno_coreg_residual/ifc_poisson/{best,last}.pt results/raw/fno_coreg_residual__ifc_heat__e200__s42__*.json results/raw/fno_coreg_residual__ifc_poisson__e200__s42__*.json && bash scripts/cycle_eval.sh'. Expected output: results/smoke_latest.json with composite_nRMSE recorded as the clean cycle-002 H3 baseline; both fno_coreg_residual_train_seconds entries should be in the 400-600s range.
## NEW DIRECTIVE (human-injected 2026-05-31): beat the transfer-learning MF-FNO
A new FROZEN competitor `models/mf_fno_transfer_bar/` has been added: the published
transfer-learning MF-FNO (pretrain a single FNO on low-fidelity, fine-tune on
high-fidelity; Lyu 2023 / GCS 2023). In the FULL 15-dataset benchmark it is the
strongest model (geomean rel-L2 0.0113), beating every in-tree family even at
matched parameters (~2.7M variant: 0.0236). On the 2 smoke datasets it scores
~0.0098 (ifc_heat) and ~0.067 (ifc_poisson) -> composite bar ~0.026.
GOAL: invent a NEW family in models/ whose composite_nRMSE beats mf_fno_transfer_bar.
HYPOTHESIS SEEDS worth trying (Researcher to expand): (a) add transfer-learning
pretraining (LF->HF fine-tune) ON TOP OF the coregionalization/residual heads —
the current families train all fidelities jointly and may underuse the LF->HF
transfer signal; (b) a single full-resolution HF FNO (not per-fidelity coarse
FNOs) but conditioned on a coregionalization-m basis; (c) curriculum: pretrain the
whole stack on LF, then fine-tune the HF head. The transfer mechanism is the thing
to absorb/surpass, not just match.

## NEW DIRECTIVE (human-injected 2026-06-12): distribution-conditioned residual (FIRE for fields)
A new family `models/fno_fire_distcond/` has been added: the FIELD analog of FIRE
(Yu, Sung & Ahmed 2026, arXiv:2601.22371). A deep ENSEMBLE of LF-FNOs supplies
per-pixel posterior-predictive summary FIELDS (mean mu_LF, std sigma_LF, quantiles
q10/q50/q90); the HF correction FNO_delta is conditioned on those distributional
fields (extra input channels) and predicts the residual HF - mu_LF. Final HF =
mu_LF + delta. This is `fno_additive` (mean-only, uncertainty-blind) UPGRADED with
LF uncertainty so it can handle spatially heteroscedastic cross-fidelity error
(LF error concentrates at shocks/boundaries/vortex cores).

GOAL: invent a NEW family that beats both mf_fno_transfer_bar (composite ~0.026)
AND fno_fire_distcond by exploring SMARTER distribution-conditioning. HYPOTHESIS
SEEDS worth trying (Researcher/Strategist to expand, Builder to implement; keep the
shared geometry-general backbone so the comparison isolates the MECHANISM):
  (a) Heteroscedastic single LF-FNO: one network with 2 output heads (mu, log-var)
      trained with Gaussian NLL — gives a SMOOTH per-pixel sigma at 1/5 the cost of
      the 5-member ensemble. Condition delta on [mu, sigma].
  (b) Quantile-regression LF: LF-FNO with multiple quantile output channels trained
      with pinball loss -> captures NON-Gaussian residual shape (FIRE's quantiles),
      no ensemble. Condition delta on the quantile fields.
  (c) MC-dropout LF: single FNO with dropout, T stochastic passes for mu/sigma -
      epistemic uncertainty, cheap.
  (d) Heteroscedastic delta: give FNO_delta its own (mu, log-var) head so the
      reported predictive variance is sigma^2_LF + sigma^2_delta (proper two-stage
      UQ as in FIRE Algorithm 1), and train delta with NLL.
  (e) FiLM the conditioning: instead of concatenating sigma as an input channel,
      use sigma to FiLM-modulate delta's norm layers (gamma(sigma),beta(sigma)) -
      a softer, multiplicative form of uncertainty gating.
  (f) COMPOSE with the transfer winner: the LF-pretrained FNO inside mf_fno_transfer
      is already a free LF surrogate. Ensemble/dropout it for a sigma field, then
      FiLM-condition the HF fine-tuning on that sigma -> "distribution-conditioned
      transfer", uniting the two strongest ideas in the project.
Expected payoff regime: the NON-SMOOTH / heteroscedastic datasets (burgers,
burgers_param, high-Re cavity) where mean-only coupling loses most. Report whether
distribution-conditioning closes the output-coupling-vs-transfer gap there.
