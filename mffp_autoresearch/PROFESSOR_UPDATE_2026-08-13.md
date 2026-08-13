# MFFP Autoresearch — Mentor Update (2026-08-13)

Date: 2026-08-13. Author: Eloise (with the autoresearch orchestrator).
This is the concise current-state brief; the full round-3 narrative it condenses is archived at [`PROFESSOR_UPDATE_2026-08-12.md`](PROFESSOR_UPDATE_2026-08-12.md) / [`.html`](PROFESSOR_UPDATE_2026-08-12.html).
Canonical adjudicated records (both fact-check-converged): `round3/docs/round3_report.md` (round 3) and `mffp_autoresearch/benchmark30/docs/report.md`, branch `bench30-campaign` (benchmark_30 head-to-head).
Rendered page: [Claude artifact](https://claude.ai/code/artifact/a03c7fd2-cf39-42d6-8ec5-cf5ee44449cc) (private until shared from its share menu).

## The short version

1. **Round 3 closed on 2026-08-12**: all 10 experiment cards complete at 3 random seeds, both round questions answered.
   The model round 3 certified as its best on the era's 5-dataset panel is the initial-condition stack route (`r3s2_route`): 10.09 against the certified training-free floor, 0.72× the error of the strongest learned baseline (the film-transfer FNO) on that panel.
   (The round leaderboard is era-scoped — rankings compare only within a panel composition; one batch-3 arm separately posted the round's best single score in film units, 0.5780.)
2. **New (2026-08-13) — the round-3 winner was benchmarked at full breadth against that film baseline on the published `benchmark_30` release, and it is a specialist, not a generalist.**
   Film wins overall (the certified model's panel error is ~1.67× film's); the certified model wins 5 of 29 datasets, by up to 6.4×.
   Details and Fig. 1 in §2.
3. **The system caught two real benchmark defects and corrected its own headline.**
   It found the `pfc` task had essentially no fidelity gap (the reported reference error was ~100% our own interpolation artifact) and that mandatory checkpoint resumption had silently skipped retraining several baselines; 32 runs were quarantined and retrained, and a permanent checkpoint↔data binding gate (108/108 on a labelled-defect exam) now guards every baseline build.
   After the repair, the early "+10.1% from low-fidelity training data" headline was retracted: the true panel change is −0.81%, only 0.08× the certified minimum detectable effect.
4. **Both governance rulings were ratified by Eloise and executed on 2026-08-12** (panel-composition option C; ifc affine-floor option B).
   Under the corrected noise bars the batch-3 route headline survives at reduced magnitude (2.75× / 2.54× its own bar, direction unchanged).
5. **Round 4 was approved on 2026-08-13: the goal is now a model that beats the film baseline on benchmark_30.**
   It starts lean — diagnostics plus a training-budget check on the baseline itself — before any new model is built (§4).
   Nothing here requires mentor action; questions welcome.

## 1. What this system is

An autonomous research loop that invents and tests multi-fidelity PDE surrogate models on a SLURM cluster: each experiment is a pre-registered card (hypothesis, recipe, falsification bar), run at 3 random seeds and adjudicated in writing — model experiments against certified performance floors, diagnostic and audit cards against their own pre-registered criteria.
Two AIs cross-check every artifact (one authors, the other adversarially reviews, looping to convergence), and every number in this page traces to a fact-check-converged report.

## 2. New result: the benchmark_30 head-to-head

**Question.** Round 3 certified `r3s2_route` as its best model on a 5-dataset panel; does that advantage generalize?

**Setup.** We trained it and the film-transfer baseline from scratch across the newly published `benchmark_30` release — film on all 30 datasets, the certified model on the 29 its frozen implementation supports (`era5` exceeds its grid cap; predeclared) — at 3 seeds × 200 epochs, under round 3's evaluation protocol, comparing per-dataset relative-L2 error.

**Answer: film generalizes; the certified model specializes.**
Over the 29-dataset common set the film-relative skill geomean (error ratio film/certified; >1 means the certified model is better) is **0.6004** (per-seed 0.5934 / 0.6047 / 0.6032) — the certified model's panel error is ~1.67× film's.
It wins 5 of 29 — `sharp__fisher_kpp_2d` (6.4×), `ext__helmholtz_2d` (5.2×), `sharp__allen_cahn_2d` (2.6×), `sharp__cahn_hilliard` (1.35×), `sharp__phase_field_crystal_2d` (1.22×) — four phase-field / reaction-diffusion problems plus one Helmholtz variant.
Only three of those five sit in its round-3 certification panel, and the panel's other two members (`ifc_heat`, `ifc_poisson`) flip to film — consistent with round 3, which certified a panel-level advantage; benchmark_30 shows per-dataset where it comes from.
One win carries an asterisk: on `ext__helmholtz_2d` film is unstable (rel-L2 4.43, worse than predicting zero) and the certified model still sits at 0.86 — neither model solves that dataset.

![Fig. 1 — benchmark_30 per-dataset film-relative skill](figures/b30_skill_per_dataset.png)

*Fig. 1 — per-dataset film-relative skill of the certified model (log scale; bars right of 1.0 are its wins), colored by benchmark group, whiskers spanning the three per-seed ratios, with the panel geomean marked.*

**Integrity.** 177/177 eligible runs completed and scored, zero failures; the 30 published datasets were verified byte-identical (per-array sha256) to the local arrays and the corrected hub release, so the published benchmark needs no correction; and film's `ifc_heat` seed-0 error re-trained here matches the round-3 record to 0.03% (0.0268262 vs 0.0268172).

**Caveats** (full list in the campaign report): relative-L2 is level-dominated on near-uniform fields — on `sharp__fisher_kpp_2d` the manifest's copy-LF error is 35× larger mean-removed than raw, so the 6.4× win is protocol-true but metric-sensitive; one ext dataset's low-fidelity input is downsampled fine solution rather than a true coarse solve; and *why* each side wins where it does is left as labeled hypotheses until the round-3 diagnostic probes are run on these residuals.

## 3. Round 3 in brief

The round asked two questions and answered both: the synthetic-coarse-field detour is capped by a scalar identity (emulator ceiling **confirmed**, retiring that detour), and the training-free knee predictor does **not** transfer (**falsified**, with a mechanism for when such predictions can work).
Along the way the round refined the scored panel for cause (e.g. `ifc_poisson` demoted to report-only: its condition→answer map is exactly linear, and no learned model ever beat the copy-the-coarse-solve reference there).

![Fig. 2 — round-3 final leaderboard](round3/docs/figures/r3_performance_vs_baselines.png)

*Fig. 2 — the round-3 leaderboard: every certified experiment card against the certified floors and the film baseline. Bars span two different 5-dataset panel compositions (eras); rankings compare only within an era, not across the whole figure.*

![Fig. 3 — the four experiment lines](round3/docs/figures/r3_architectures_overview.png)

*Fig. 3 — the four round-3 experiment lines ("streams": parallel research directions, one model family each), what each model actually is, and the round's verdict on each (CONFIRMED / FALSIFIED / etc.; the verdict vocabulary is keyed at the bottom of the figure itself).*

## 4. What happens next (round 4, approved 2026-08-13)

The goal is a model that beats film on benchmark_30.
Approved lean start, in order: **Phase 0** — a headroom map of film's error against certified floors, a mean-removed companion metric panel, and spectral/interface residual diagnostics; then **S1** — a training-budget check on film itself (if longer training moves film, the bar moves before any challenger is scored).
Development will iterate on a pre-registered ~12–15-dataset dev subset, touching the full 30 only at certification points, to avoid overfitting the benchmark.
The backbone choice is deliberately open: a preliminary screen of the pre-existing family sweep (30 families × 15 datasets, single seed, non-campaign protocol) shows film is not uniformly dominant even on core datasets — one coregionalization family posts 8× lower error on `lid_driven_cavity` — so re-screening the existing registry under the campaign protocol is proposed for Phase 0 before any substrate is locked.
The only open hold from earlier rounds is the round-1 2500-epoch queue (unchanged since 2026-08-01).

---

Archive (full narrative & all round-3 figures): `PROFESSOR_UPDATE_2026-08-12.{md,html}` · canonical records: `round3/docs/round3_report.md` and `mffp_autoresearch/benchmark30/docs/report.md` + `state/leaderboard.json` (branch `bench30-campaign`) · Fig. 1 rendered by `tools/render_b30_update_figure.py`, Figs. 2–3 by `round3/tools/render_round3_update_figures.py` · this page is private until shared from its share menu.
