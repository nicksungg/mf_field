# Summary so far — stream `r2s3_lf_train_signal`, batch 2

## Where the stream stands after B1

B1 (`experiment_cards/r2s3_lf_train_signal/batch_1/B1.json`, status complete,
`cratered_verdict: "cratered"` via the falsification branch) shipped
`r2s3_rung_supervised`: a FiLM-FNO condition→field decoder trained with
native-resolution supervision on all LF rungs (arm `rung_native`), against a
matched no-LF control (`hf_only`) and an upsampled-rung mechanism control.

Headline numbers (seed 0, smoke tier, `5_actual_result`):
panel geomean skill **25.3919** (`rung_native`) vs **26.8687** (`hf_only`) vs
the stream anchor **23.0636** (`state/anchors/r2s3_lf_train_signal.json`,
best-floor panel geomean) — *both arms worse than the training-free anchor*.
**F1 falsified with an inversion**: on `ifc_poisson` `rung_native` 16.7963 vs
`hf_only` 9.4466, i.e. the LF arm is 7.35 skill units WORSE, = 7.8x the
certified `min_claimable_effect` 0.93770 (`state/noise_floor.json`, certified
by r2s4-B1, 3 seeds). F2 survived only against a diverged comparator
(`rung_upsampled` 647.51, a 24x amplitude blow-up). Helmholtz stays
report-only (best floor = zero field, 3.3441); pfc claims carry the
band-limited-denominator caveat.

## What B1's mechanism analysis established (parts 6-7)

1. **`ifc_poisson` is exactly affine in its 5-dim condition** — affine LOO
   residual 3.2e-08 at every rung including the 128 test HF rows; the other
   five panel datasets sit at 0.2507-2.3141 (`tools/affine_ladder_voi.py
   --affinity_only`). Independently confirmed from the LF side by
   r2s2_stacked-B1 (ridge held-out nRMSE 0.0000, emulator output rank 1.02).
2. **The information premise of the stream is CORRECT on ifc_poisson**: the
   5 HF rows leave one null direction of the 5x6 design carrying 18.83% of
   the law's coefficient energy; the 170 disjoint LF conditions supply it
   (transferred at cos 0.9993 by rung 32). A ~60-line linear/affine probe
   (rung-32 affine law + 5-row residual ridge) reaches **skill 0.2427** —
   below the paper bar, 2.5x better than round-1's round-best 0.6087, 69x
   better than B1's shipped network. The HF-only information limit is 3.4744
   for a model of any capacity.
3. **The architecture is the failure**: at matched information the FiLM-FNO
   decoder costs 2.72x with no LF (3.4744 -> 9.4441) and 60x with LF (0.2427 ->
   14.6254). Named defects: the shared `max|y|` scaler collides with
   ifc_poisson's h^2 amplitude convention (42x spread -> 1772x HF-row loss
   deflation); mode bands above the coarse rungs' Nyquist are supervised by
   5 deflated rows only (worth 1.605 skill units to repair legitimately); and
   the decoder places 27.7% (no-LF control) of its implicit law energy in the
   unconstrained null direction **anti-aligned** (cos -0.99) with truth —
   an active wrong-signed extrapolation, not min-norm shrinkage. Train-row
   diagnostics are blind to all of it (`rung_upsampled` looked healthy on its
   5 fine-tune rows).

## What B2 is likely to propose (part 7 `next_direction`)

- **E1** — ship the **linear/affine LF channel** as a contract-compliant
  family: `c*A(cond) + R(cond)`, A fitted on the best LF rung (rung chosen by
  in-rung LOO), c and residual ridge fitted on the 5 HF rows, with a
  **training-free per-dataset affinity gate** falling back to a no-LF neural
  control wherever the task is not affine.
- **E2** — the **null-direction / rank-completion** framing itself: LF rows at
  *disjoint parameter values* identify the direction the HF design cannot,
  with a matched with/without-LF value-of-information ablation at N_hf = 5.
- **E3** — the **repaired-network trio**: per-rung output scaler + mode
  clipping pinned at the HF Nyquist for every rung + explicit null-direction
  gain calibration / min-norm penalty.

## Prior-art already on record (batch 1 — do not re-derive)

`websearches/r2s3_lf_train_signal/batch_1/report.md`: D1 (teacher
distillation) and D2 (auxiliary coarse heads) = **preempted-but-MF-
composition-open** (Meng & Karniadakis composite MFNN arXiv:1903.00104; EAAI
representation-level privileged distillation); D3 (LF-as-parameter-coverage)
= **novel**, nearest neighbours MLMC/multiscale operator training
(arXiv:2505.12940, arXiv:2501.12739) which are cost-oriented and keep the same
parameters at every level. LF-pretrain->HF-finetune is externally published
(arXiv:2304.06972) and is the mandatory declared baseline
(`mf_fno_transfer_film`).

In-repo literature reports (cited, not re-derived):
`docs/reports/MF_Sharp_HighFreq_Report.md` (line 162-165) records Kennedy &
O'Hagan `y_HF = rho*y_LF + delta` (Biometrika 2000) and NARGP (Perdikaris et
al., Proc. R. Soc. A 2017, DOI 10.1098/rspa.2016.0751) as the classical
linear/nonlinear MF regression canon — directly relevant to E1's novelty and
**already prior art in hand**. `docs/reports/MF_Leaderboard_Beaters_2026_Report.md`
is architecture-oriented (IRNO, F-Adapter) and only tangential here.
Cross-stream, `websearches/r2s1_direct/batch_2/report.md` already retrieved
**PCA-RaNN** (closed-form ridge onto PCA coefficients vs DeepONet/FNO,
arXiv:2606.29440) and McGreivy & Hakim's weak-baseline critique
(arXiv:2407.07218) — both bear on E1 and are re-verified here where used.

## Open questions this batch must answer

- Is a **linear/affine multi-fidelity channel with LF at disjoint parameter
  values** (E1/E2) preempted by co-kriging / transfer-learning-for-linear-
  regression / MLMC literature, and if so what composition remains open?
- Is **per-resolution normalization + Nyquist-pinned mode clipping** for
  mixed-resolution operator training (E3a/E3b) already published?
- Is **null-direction / unidentifiable-direction regularization** of a
  neural surrogate (E3c) already published, and under what name?
- Is a **training-free per-dataset gate choosing between a closed-form and a
  neural surrogate** published (E1's mandatory guard)?
