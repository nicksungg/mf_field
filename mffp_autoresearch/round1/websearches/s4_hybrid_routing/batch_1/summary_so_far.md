# summary_so_far — `s4_hybrid_routing`, batch 1

## What this stream owns

`project.yaml streams[3]`: *"can MF compositions of hybrid operators capture the
+30.6% FNO<->Transolver oracle?"* — class `lever`. program.md §12.4 fixes the
conventions:

- **Anchor**: the batch-0 certified champion's panel geomean skill.
  `mffp_autoresearch/round1/state/anchors/` is **empty** and
  `state/noise_floor.json` **does not exist** (verified by `ls`); `state/gates.md`
  records *"G3 — batch 0 (anchors + noise floor): PENDING"*. Batch 0 is queued on
  SLURM. Consequence: **no numeric anchor and no noise floor exist yet**, so any
  falsification threshold must be expressed relative to the anchor once certified,
  or clear a stated-and-justified provisional margin. Per §4.5 a missing/
  provisional anchor is not a numeric threshold — judge against the falsification
  clause instead.
- **Quantified prior**: FNO<->Transolver pairwise oracle **+30.6%** over FNO alone
  (Transolver wins 16/38 datasets despite being ~2x worse on average). In-repo
  source of the number: `mf_field/akash/models/fno_transolver_seq/model.py`
  docstring (FNO-FiLM geomean rel-L2 0.01577, `transolver_residual` 0.02998,
  per-dataset oracle 0.01095 = -30.6%), echoed in
  `docs/superpowers/specs/2026-07-28-mffp-autoresearch-design.md:69`.
- **§12.4 batch-1 direction**: *"`mf_field/akash/models/fno_transolver_seq`
  (sequential FNO->Transolver residual hybrid) is BUILT but unbenchmarked — batch 1
  should start by scoring it on the panel (cheap, mostly evaluation)."*
- **§12.4 novelty boundary**: *"The surviving novelty is the **MF composition**
  (routing, per-band/per-region gating, which fidelity feeds which expert) — the
  base hybrids themselves are published (WLNO, Park 2507.06133, SINO)."*
- **§12.4 caveat**: `transolver_residual` is best-in-zoo on 4 of the 5
  beyond-copy datasets; learned routing must **preserve** that behaviour there.

## Existing assets (verified on disk)

- `mf_field/akash/models/fno_transolver_seq/` — `manifest.json`, `model.py`,
  `smoke_eval.py`. The manifest confirms three safety properties relevant to any
  routing card: zero-init correction head; scalar gate `alpha` initialised at 0
  and set by least-squares + line search containing 0 (a useless correction
  collapses the hybrid EXACTLY to the FNO); out-of-fold residual targets from a
  K-fold rerun of the HF fine-tune. **Strongest in-repo precedent for
  identity-safe composition.**
- `mf_field/factory_mffp/models/transolver_residual/` — hard MF residual
  `HF = LF_interp + transolver_delta`.
- `mf_field/factory_mffp/models/transolver_attention_fusion/` — iterated
  cross-fidelity attention ("attention IS the fusion").
- Akash zoo also holds `mf_fno_allpairs`, `mf_fno_ptr`, `mf_fno_spectral`
  (pre-falsified, §5), `convnext_unet_film`.

## Prior websearch reports to reuse, not re-derive

- `docs/reports/MF_Leaderboard_Beaters_2026_Report.md` — §3.1 IRNO
  (arXiv:2605.24041) frozen-base iterative refinement; §4.4 line 270 describes a
  *"frozen-host, three-stage correction: global corrector -> blockwise local
  refiner -> deployment-time label-free risk score routing refinement compute to
  high-risk blocks under a budget"* — the closest already-surveyed published thing
  to per-region routing.
- `docs/reports/MF_Sharp_HighFreq_Report.md` — P4 band-splitting (lines 293-298:
  hard-constrain output Fourier coefficients below a per-dataset cutoff `k_c` to
  the LF spectrum, predict only `k > k_c`, with `k_c` from LF/HF cross-spectral
  coherence < 0.7); P6 patch dictionary blended through a **learned confidence
  gate** (lines 248, 322). Both are band/region routing ideas already surveyed
  but NOT prior-art-checked as routing mechanisms.

## Open questions this batch's search must answer

1. Is **per-band (spectral) routing between a spectral operator and an attention
   operator** published? (P4 + §12.4 "per-band gating".)
2. Is **per-region / spatial gating (MoE) over neural-operator experts**
   published, and if so is the *multi-fidelity* composition still open?
3. Is a **sequential residual FNO->Transolver hybrid** itself published (i.e. does
   even the cheap benchmark-the-built-thing card stand on prior art)?
4. Do any published routing schemes carry an **identity / no-harm guarantee** (the
   `alpha`-init-0 property) that would let routing preserve `transolver_residual`
   on the 4 beyond-copy datasets it wins?
