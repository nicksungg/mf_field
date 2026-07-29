# summary_so_far — `s6_local`, batch 1

Written before searching. Sources: `program.md` §2.3/§5/§12.6/§13.2,
`docs/adr/0011-s6-local-stream.md`, `state/anchors/*.json`,
`state/noise_floor.json`, `mf_field/akash/results/bench_full_metrics.csv`,
`docs/reports/MF_FNO_CNN_Hybrid_Report.md`,
`docs/reports/MF_Sharp_HighFreq_Report.md` §0–§1.2, and the sibling batch-1
websearch reports (`websearches/s4_hybrid_routing/batch_1/report.md`,
`websearches/s2_beyond_copy/batch_1/report.md`).

## The stream's question

Does adding a **local representation** (CNN/ConvNeXt branch, local kernels) to
the FNO fix sharp-2D multi-fidelity fusion? This is the direct test of
hypothesis **H2 (missing local representation)**, live because s5-B1's H1 test
(`modes_cap` 12→32 on the champion) moved the panel geomean by only **0.507**,
below the **0.884** claimable floor (provisional-single-seed, orchestrator
brief) — i.e. spectral capacity alone is not the lever.

## Anchor and floors (quote verbatim when designing)

`state/anchors/s4_hybrid_routing.json` / `s3_testtime.json` (same certified
champion) — `mf_fno_transfer_film` panel geomean skill **6.703**
[6.219, 7.102], 3 seeds, `provisional: false`. `s6_local`'s own anchor file
does not exist yet; ADR 0011 says the anchor is "champion's certified panel
geomean", i.e. the same 6.703. Per-dataset `min_claimable_effect`
(`state/noise_floor.json`): helmholtz 9.695, allen_cahn 1.633, cahn_hilliard
0.553, fisher_kpp 0.418, phase_field_crystal 1.151, ifc_poisson 0.240.
**Helmholtz's floor (9.695) is most of its own anchor skill (13.82)** — no
numeric per-dataset claim on helmholtz is defensible.

## What the zoo already says about locality (measured, not searched)

From `mf_field/akash/results/bench_full_metrics.csv` (2500-epoch bench, 1 seed;
priors only, not round-1 claims), `convnext_unet_film` (pure ConvNeXt-U-Net)
vs the champion `mf_fno_transfer_film`, rel-L2:

| dataset | convnext_unet_film | mf_fno_transfer_film |
|---|---|---|
| `sharp__allen_cahn_2d` | **0.3314** | 0.3412 |
| `sharp__cahn_hilliard` | 0.4664 | **0.4406** |
| `sharp__phase_field_crystal_2d` | 0.4808 | **0.4468** |
| `ext__helmholtz_2d` | 3.5987 | **1.5257** |
| `ifc_poisson` | 0.0555 | **0.0488** |

So the pure-local model is *marginally* better on the one purely
interface-driven dataset and **2.4× worse on the oscillatory global one**
(helmholtz). This is the empirical statement of ADR 0011's "capacity is not
the question, composition is": replacing the spectral backbone with a local
one trades global structure for interface sharpness. It motivates
**complementary composition** (parallel branch / gate), not substitution.

## The mentor's FNO→CNN attempt — what actually happened

`program.md` §13.2 states plainly that the FNO→CNN two-stage hybrid **was
never built**; `MF_FNO_CNN_Hybrid_Report.md` is a *design + prior-art* report,
and the thing that "went poorly" is its **§6 verdict**, not a training run:
*"Every individual component of this design is published prior art, and one
paper combines three of the four."* Nearest matches it names: SINO
(arXiv:2606.18305), Park et al. (arXiv:2507.06133), CorrDiff
(arXiv:2309.15214), U-FNO, U-AFNO, LOGLO-FNO, HUFNO, WHNO. Its §5 lists three
predicted failure modes: (5.1) exposure bias at the stage boundary (stage 2
trained on true LF, fed predicted LF at test), (5.2) the additive-residual
dipole when LF *misplaces* rather than blurs a feature, (5.3) payoff
concentrated in a few sharp datasets while extra HF-fitted parameters overfit
at N_hf=5. Its §6.6 flags **NO-LIDK (Liu-Schiaffini et al., ICML 2024)** as
"plausibly tighter FNO+local-conv prior art than anything verified here" —
never fetched. That is my first retrieval target.

`MF_Sharp_HighFreq_Report.md` §1.2 already calls a local convolutional path
beside the spectral path "the single most consistently validated fix" and §0.4
notes the champion family **never looks at the LF field at inference** — so a
local branch that *consumes the LF field* is a different composition from
either the mentor's two-stage proposal or the incumbent.

## Sibling-stream prior art already on file (to re-verify, not re-derive)

`s4_hybrid_routing/batch_1/report.md` fetched **U-HNO** (arXiv:2605.12965) —
"per-location hard spectral-vs-local routing, zero-init gates, no MF" — the
single closest published threat to a spectral/local gating composition here.
`s2_beyond_copy/batch_1/report.md` fetched **Fixup** (arXiv:1901.09321) for
identity-at-init residual branches, relevant to a no-harm local branch.

## Open questions this batch's search must settle

1. Is a **parallel** local branch inside an FNO (U-FNO / NO-LIDK / DCNO) fully
   published for sharp fields — and with what measured evidence?
2. *Why* do local branches help or fail at sharp interfaces — aliasing/Gibbs
   or receptive field? (retrieval-grounded, not from memory)
3. Parallel branch vs sequential stages; shared vs separate losses.
4. Any evidence at **N_hf ~ 5–25** for hybrid operators — or is the tiny-HF
   regime genuinely unoccupied?
5. Does any published work put a local/hybrid operator inside a **genuine
   multi-fidelity** (real coarse solve → fine solve) pipeline?
