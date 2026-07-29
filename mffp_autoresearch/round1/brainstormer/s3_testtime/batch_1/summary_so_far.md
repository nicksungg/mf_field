# Summary so far — `s3_testtime`, batch 1

Stream question (`project.yaml`): *"how far does test-time refinement go when the
governing residual is real?"* Class **lever**. Anchor
(`state/anchors/s3_testtime.json`): champion `mf_fno_transfer_film` panel geomean
skill **6.703**, CI [6.219, 7.102], per-seed [7.102, 6.219, 6.788], `provisional: false`.

## 1. Websearch findings + prior-art verdict

Source: `websearches/s3_testtime/batch_1/report.md` (5 iterations, cap hit; 12 usable
fetches). Its **prior-art verdict** table has four rows:

- **D1** (exact Helmholtz residual `Δu + k²u = f` descended on the output field with an
  anchor, from a frozen MF base): **"preempted-but-MF-composition-open (cite)"**, with the
  honesty caveat that the preempting source (PINO, arXiv:2111.03794) could not be fetched
  in 3 attempts. Open: *"**field-space** vs weight-space optimization; doing it **from an MF
  prediction at N_hf = 5**; and scoring against **copy-LF** rather than against the base
  model — nobody in this literature uses that bar."* **Standing threat (fetched)**:
  residual minimization *"can be an unreliable proxy for reconstruction accuracy in
  ill-conditioned systems"* (ENS, arXiv:2606.27354). **Mandatory mitigation**: PIC-Flow-style
  masking of source/stencil-error pixels (arXiv:2605.06929).
- **D2** (IRNO-style frozen-base fixed-point refinement conditioned on LF): **preempted
  (cite)** — MFFM (arXiv:2605.16118) claims exactly that cascade as its primary
  contribution; IRNO (2605.24041) and SINO (2606.18305) are two more instances. The report's
  §"For the brainstormer" item 2: *"Do not propose D2's plain form … this would be 0-for-5."*
- **D3** (MF prediction as Krylov warm start): **preempted (cite)** — NOWS (2511.02481),
  super-fidelity (2312.11842, LF→HF warm start with few solutions), FCG-NO (2402.05598).
  *"Not recommended for batch 1."*
- **D4** (free-energy / equilibrium projection at test time on the four phase-field panel
  sets): **novel** (by absence of evidence — weak); flagged as the natural batch-2 card.

Item 4 of the report's brainstormer notes asks specifically for a **residual-vs-error sweep**
so that *"a null outcome [is] informative rather than wasted"*.

## 2. §12.3 conventions (verbatim, program.md, post-ADR-0003)

> - **Anchor**: champion's certified panel geomean (batch 0).
> - Quantified priors — **CORRECTED, see ADR 0003** (the earlier −21% claim was
>   a FINDINGS.md misread; refuted in-repo by the batch-1 websearch):
>   `mf_fno_ptr`'s refinement is a registry NO-OP outside ifc_heat/ifc_poisson;
>   where it ran (`ifc_poisson`) it bought −1.5%, inside the CI, at 163×
>   inference latency. The lever has never been shown to help — this stream's
>   batch 1 is closer to a first real test than a scale-up.
> - A true governing residual is computable for only **one** panel dataset:
>   `ext__helmholtz_2d` (steady; `x = [k, source_x, source_y]` fully determines
>   `f`; `Δu + k²u = f` exact). The phase-field snapshots lack ∂ₜu; ifc_poisson's
>   source decode is not shipped. Cards must scope accordingly (Helmholtz-exact
>   refinement, or equilibrium/free-energy projection for the phase-field sets).
> - Known threat (fetched, arXiv:2606.27354): residual minimization can be an
>   unreliable proxy for reconstruction accuracy in ill-conditioned systems —
>   Helmholtz is the canonical indefinite case; designs should include a
>   residual-vs-error check so a null is informative.
> - Second lever: IRNO-style frozen-base iterative refinement
>   (`docs/reports/MF_Leaderboard_Beaters_2026_Report.md` proposal N1,
>   arXiv:2605.24041, ~50× high-frequency band-error reduction claimed) — unbuilt.
> - Test-time changes must still respect the contract CLI (refinement runs
>   inside `smoke_eval.py`) and report wall-clock in build notes.

ADR 0003 (`docs/adr/0003-s3-prior-correction.md`) records that this replaced the false
−21% `mf_fno_ptr` prior, and that the batch-1 seed direction is re-scoped to
Helmholtz-only exact-residual refinement or equilibrium-projection alternatives.

## 3. Within-stream prior cards

**None.** `experiment_cards/` contains only `SCHEMA.md`; no card exists in any stream
(verified by listing the tree). Batch 1 is this stream's first card.

## 4. Cross-stream prior cards

**None.** No cards exist anywhere yet, so there is no part-7 text to scan. The only
sibling artifacts are other streams' batch-1 websearches.

## 5. Reopen candidates

**None** — there are no prior cards, therefore no `reopen_candidate: true` entries.

## 6. What is UNKNOWN (and what I resolved before designing)

The batch-0 numbers make `ext__helmholtz_2d` the stream's whole problem:
`state/noise_floor.json` gives champion per-seed nRMSE **[6.202, 3.008, 4.446]** →
per-seed skill **[18.83, 9.13, 13.49]**, mean **13.817**, spread **9.695**
(`min_claimable_effect`). Two things follow. (i) The champion is **13.8× worse than
copy-LF** on the one dataset where the s3 lever is even applicable. (ii) Any numeric
per-dataset claim there must exceed **9.695 skill units** — a bar so high that only a
near-total fix clears it.

Unknowns going into design, and how I closed the cheap ones with **read-only, design-time
probes** (scripts kept in the session scratchpad; every number below is reproducible from
`benchmark_42/ext/helmholtz_2d` + `mf_field_extension_data/solvers.py`):

1. *Is the "true residual" actually reproducible?* **Resolved: yes, exactly.**
   `solvers.py::solve_helmholtz` + `assemble_elliptic` + `grid_xy` fix the discretisation:
   `n=96` interior nodes, `h=1/(n+1)`, homogeneous Dirichlet, 5-point Laplacian,
   `f = exp(-((x-sx)²+(y-sy)²)/(2·0.04²))`. Measured `‖Au_hf − f‖/‖f‖ ≤ 2.7e-11` on all 100
   shipped HF test fields.
2. *How hard is the operator to invert?* **Resolved: it is trivially invertible.** `Δ_h + k²I`
   with Dirichlet-0 on a uniform grid is **exactly diagonalised by the 2-D DST-I**
   (checked: 4.3e-14). The exact spectral solve reproduces the shipped HF test fields to
   **2.2e-13 median rel-L2**. So *unbounded* residual minimisation on this dataset is a
   two-FFT re-solve — model-independent, and faster than the network's forward pass.
   **This is the vacuity hazard nobody in the stream's context had named.**
3. *Does the residual track the error?* **Partly, and treacherously.** On noise-perturbed
   truth, Spearman(rel-residual, rel-error) = 0.85 — but the least-squares residual weights
   modes by λ² over six decades (|λ| ∈ [0.059, 7.5e4]), so it is dominated by prediction
   **roughness**, not prediction **error**. The 1-dof residual-optimal rescale
   α* = ⟨Au,f⟩/‖Au‖² gives α*≈1.0000 (rel-L2 0.0037) on a 12-mode low-pass of the truth,
   but α*≈0.003 on copy-LF (rel-L2 0.3295 → **0.9964**) and α*≈1e-4 on truth+10% noise
   (rel-L2 0.10 → **0.9999**). *A very good but slightly rough prediction is destroyed.*
4. *Where does the champion's actual output sit?* **Resolved, and it is the finding that
   reframes the card.** I reconstructed the three certified batch-0 checkpoints
   (`eval/results/mf_fno_transfer_film/ckpt_ext__helmholtz_2d_e200_s{0,1,2}/last.pt`) and
   reproduced the recorded rel-L2 to 7 digits (6.202275 vs 6.202266). Then: the **oracle**
   1-dof rescale — the best any scalar correction could ever do — only reaches rel-L2
   0.839/0.899/0.926 (skill 2.55/2.73/2.81), i.e. **the champion's Helmholtz output is barely
   more informative than the zero field** (cos ≈ 0.37–0.54); and the *achievable* residual
   α* drives all three seeds to rel-L2 **1.0000** — skill exactly **3.035**, the zero
   predictor. Cause is visible in the champion's own `smoke_eval.py`: a single global
   `scaler_hf = max|Y_hf_train|` = 7.38 against a **408×** per-sample ‖u‖ spread caused by
   near-resonance samples.
5. **Still genuinely unknown** (what the card must measure): the *budgeted* regime —
   K-step masked-residual descent for K ∈ {0…1000} from base / copy-LF / zero
   initialisations; whether the MF prediction is worth anything as a warm start at any
   finite budget; the per-|λ| bucket anatomy of base vs copy-LF error; whether the
   PIC-Flow source/stencil mask changes the α* collapse; wall-clock of every arm; and —
   decisive for batch 2 — whether the **free-energy surrogate** is a monotone error proxy on
   the three phase-field panel datasets (the D4 premise), which nobody has checked.
