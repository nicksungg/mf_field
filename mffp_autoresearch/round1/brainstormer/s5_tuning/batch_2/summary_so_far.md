# Summary so far — Stream `s5_tuning`, Batch 2

## 1. Websearch findings + prior-art verdict

Source: `websearches/s5_tuning/batch_2/report.md` (5 iterations, cap hit; 15
WebSearch / 15 usable WebFetch).

Four verdict rows (the row this card uses is quoted verbatim in `iteration_1.md`):

- **(i) per-sample / condition-predicted output scaling** ->
  `preempted-but-MF-composition-open`. Nearest art: RevIN
  (https://arxiv.org/html/2603.11869 , https://seharanul17.github.io/RevIN/),
  MPP (https://arxiv.org/html/2310.02994v2 — RevIN inside a PDE surrogate,
  "statistics are saved and used to denormalize model outputs"), APEX
  (https://arxiv.org/abs/2605.26732 — per-sample amplitude anchor from a
  coarser-fidelity operator in a target-scarce MF regime, framed as
  architecture). Open: scaler-only normalize/denormalize **across the fidelity
  boundary**, network + MSE byte-identical.
- **(ii) robust-quantile target scaling** -> `preempted`, measurement only.
  "MaxAbsScaler therefore also suffers from the presence of large outliers"
  (https://scikit-learn.org/stable/auto_examples/preprocessing/plot_all_scaling.html);
  field standard is per-channel mean/std
  (https://raw.githubusercontent.com/neuraloperator/neuraloperator/main/neuralop/data/transforms/normalizers.py).
- **(iii) stage-consistent scaler** -> `novel` (narrow) with an **unfavourable
  prior**: AdaBN prescribes the opposite (re-estimate on the target,
  parameter-free, https://arxiv.org/abs/1603.04779); Walrus normalizes inputs
  and outputs separately by design.
- **(bonus) constant-field-oracle reference line** -> `preempted`, adopt free
  (The Well: "predicting the mean value of the target field results in a score
  of 1", https://arxiv.org/html/2412.00568).

**Binding territory ruling** (report section "For the brainstormer", para 1): a
per-sample scale is s5-legal **only** if computed from inference-available data
with zero new parameters **and** the prediction is denormalized with the same
scalar (RevIN's construction); a learned scale head = s6/s3; per-sample target
division without denormalization = s7's already-claimed `C-REL`/`C-AMP`.
Two RevIN failure modes to pre-register: no learnable affine ("not beneficial
in practice"), and conditional shift between input and output statistics =
for us the per-sample LF->HF scale ratio, testable on existing data.

## 2. Section 12 conventions verbatim (program.md 12.5)

> ### 12.5 `s5_tuning` (tuning)
>
> - **Anchor**: champion's certified panel geomean (batch 0); later batches
>   re-target the current champion card.
> - Audited knob findings to grind (from `docs/proposals/MODEL_TWEAKS*.md`):
>   **F22** `modes_cap = 12` never scales with resolution (12 of 128 modes at
>   256² — candidate M1 in MODELS_TO_TRY.md proposes 32); **F19** training loss
>   ≠ scored metric in 11 families; **F20** model-selection metric mismatch;
>   normalization choices.
> - Constraint: no new losses-as-mechanisms, no new paradigms, no architectural
>   changes — knobs on existing recipes only. Anything else belongs in another
>   stream.
> - G4's dry-run card (`s5_tuning-B1`, modes_cap 12->32 on the champion) is a
>   REAL batch-1 card for this stream.

Anchor (`state/anchors/s5_tuning.json`): `champion_panel_geomean` **6.703**,
family `mf_fno_transfer_film`, per_seed [7.1022, 6.2185, 6.7883], provisional
false. Geomean noise floor **0.884** = that per-seed spread (7.10224 - 6.21854
= 0.88370). Per-dataset `min_claimable_effect` (`state/noise_floor.json`):
helmholtz **9.695**, allen_cahn **1.633**, phase_field_crystal **1.151**,
cahn_hilliard **0.553**, fisher_kpp **0.418**, ifc_poisson **0.240**.

## 3. Within-stream prior cards

`experiment_cards/s5_tuning/batch_1/B1.json` — `complete`, category
`tuning_spectral_bandwidth`, recipe `{base_family: mf_fno_transfer_film,
base_commit: 967562e..., family_dir: models_r1/mf_fno_transfer_film_modes,
datasets: panel, epochs: 200, env: {MFFP_MODES_CAP: "32"}}`.

- Part 5: geomean 6.196 vs anchor 6.703, delta -0.507 < 0.884 floor;
  falsification `not_resolvable` (conjunct A decisively unmet; conjunct B flips
  with the anchor basis — 3-seed mean vs paired seed-0 vs H100 retrain). ADR
  0005 H100 carry-over PASS (retrain geomean 7.1171). Guard `heat_local`
  flagged at contract tier only.
- Part 6 (mechanism): 100% of the panel movement is `ext__helmholtz_2d`, and
  it is **amplitude/tail**, not shape (alpha 0.071/0.048, worst sample
  50.20->8.91). `ifc_poisson` is the one dataset where the map is learnable
  (per-sample corr 0.994) and modes_cap is a true bandwidth knob (-14.6%
  nRMSE). **DECISIVE CONTROL**: on allen_cahn / pfc / fisher_kpp / helmholtz
  the demeaned per-sample correlation with truth is 0.001-0.13, pattern-only
  nRMSE ~= 1.0 -> the champion is a DC (spatial-mean) predictor plus
  uncorrelated noise, and is **worse than the constant-field oracle** on
  allen_cahn, pfc, helmholtz. Cause (imported from s2-B1): the family is
  **LF-blind at inference** — only `[batch, cond_dim]` enters the network.
- Part 7 `next_direction`: the **normalization knob**, because (a) helmholtz
  error is 70-87% amplitude, alpha 0.05-0.07, (b) the family uses ONE global
  `scaler = max(|Y_stage|)` re-derived between LF and HF stages, (c) it is a
  pure hyperparameter. Secondary: report the constant-field oracle alongside
  every panel number. NOT recommended: modes+muP-LR.
- Reference build pattern (B1 worktree, reviewed PASS): copy family ->
  `models_r1/<name>/`, fix `REPO_ROOT = HERE.parents[1]/"mf_field"/"factory_mffp"`,
  env-knob default == anchor value (default-equivalence proof at contract
  tier), knob provenance in result-JSON `extra`, `preds_test.npz` dump,
  periodic `last.pt` with config-match gate on resume.

## 4. Cross-stream cards touching this stream

- `s2_beyond_copy/batch_1/B1.json` (complete): LF-blindness at inference +
  1-NN-in-X beats the champion on 4/5 sharp datasets; independently measured
  86.5% amplitude share on helmholtz.
- `s6_local/batch_1/B1.json` (`analyzing`, under scrutiny): geomean **0.2346**
  with skill < 1 on 4 of 5 beyond-copy datasets (allen_cahn 0.081, pfc 0.030,
  fisher_kpp 0.095, cahn_hilliard 0.469) and helmholtz exactly 1.0000 — an
  LF-consuming model now dominates the LF-blind champion. Consequence for this
  card: a scaler knob on `mf_fno_transfer_film` is a **mechanism probe with a
  transferable knob**, not a leaderboard play.
- `s7_loss/batch_1/B1.json` (`built`, `objective-reparameterization`): owns the
  per-sample *objective* forms `C-REL`/`C-AMP` — the boundary this card must
  not cross (we denormalize; s7 does not).

## 5. Reopen candidates

None. Every card in `experiment_cards/**` carries `reopen_candidate: false`
(checked all 10 cards); s5-B1 is `complete`, not skipped.

## 6. What is UNKNOWN

1. **Is the champion's target scaler a lever at all on the datasets that can
   carry a claim?** B1 localized the amplitude channel to helmholtz, whose
   floor (9.695 on a mean skill of 13.8) forbids any numeric claim. Unknown
   whether *any* scaler change moves the four sharp datasets or ifc_poisson
   beyond their floors. Design-time measurement (this run, train splits only)
   says the amplitude channel is nearly absent there: per-sample `max|Y_hf|`
   spread is 3929x on helmholtz but only 1.1-8.6x on the four sharp sets, and
   3.2x on ifc_poisson.
2. **Does the LF field predict the per-sample HF scale?** (RevIN
   conditional-shift caveat.) Measured now: HF/LF `max|.|` ratio median 1.002,
   p5-p95 0.76-1.32 (p95/p5 = 1.74, CV 0.69) on helmholtz — one LF scalar
   collapses a 3929x target-scale spread to a 1.7x residual. On the four sharp
   sets the ratio is ~= 1.000 with CV 0.0006-0.014, i.e. per-sample scaling is
   a **measured no-op** there. `ifc_poisson`'s test split ships only
   `fidelity_64` (verified: `data/ifc_poisson/test/` contains `fidelity_64`
   only), so an LF-statistic scale is **unavailable at inference** there.
3. **How large is the stage re-anchoring B1 part 7 blames?** Measured:
   `scaler_lf/scaler_hf` = 0.235 (helmholtz), **42.1** (ifc_poisson, N_hf = 5),
   0.985-1.000 (all four sharp). So the "re-anchored output scale" hypothesis
   is arithmetically incapable of explaining the sharp-panel collapse — it
   stays open only for ifc_poisson/helmholtz.
4. **Is the affine part of the scaler the real knob?** Unmeasured. Pooled
   `|mean|/std` of the HF train field: fisher_kpp **3.75**, ifc_poisson
   **1.43**, pfc **1.32**, helmholtz 0.042, allen_cahn 0.005, cahn_hilliard
   0.0002; `max/std` = 39.5 / 9.9 / 3.8 / 6.0 / 2.5 / 1.3. The family's
   `max|Y|` scaler never centres, so on three panel datasets the network must
   spend most of its output range on a constant the metric barely rewards. This
   is the one scaler axis with non-trivial leverage on claimable datasets.
5. **What does a global scaler change actually change?** `y -> y/s` is a linear
   reparameterization; with a bias in the output layer the function class is
   identical. Any effect therefore runs through optimization conditioning
   (init scale vs target scale, fixed `lr_pretrain 1e-3`/`lr_finetune 3e-4`,
   `weight_decay 1e-5`, `grad_clip 1.0`). Unknown how large that is at 200
   epochs — and it is exactly the F19/F20-adjacent question 12.5 owns.
6. **Does X predict per-sample scale?** (operator's TabPFN/kNN suggestion.)
   Measured (leave-one-out kNN in standardized X, log-space average):
   helmholtz k=3 pred/true p95/p5 = **14.2**, logRMSE 0.875 (~2.4x typical
   multiplicative error) — **8x looser than the LF-field statistic (1.74)**;
   ifc_poisson (N_hf=5) logRMSE 0.23-0.31 against a raw spread of only 3.2x;
   sharp sets logRMSE 0.007-0.09 where amplitude is not the failure mode.
7. **Unknowable within s5**: whether any of this transfers to the LF-consuming
   regime that now leads the round (s6-B1). A knob validated here is portable;
   that is the card's cross-stream value.
