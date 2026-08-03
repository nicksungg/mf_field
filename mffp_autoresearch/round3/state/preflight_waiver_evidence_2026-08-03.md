# Preflight waiver evidence — repaired-panel run, 2026-08-03

Companion to `preflight_repaired_panel_2026-08-03.json` (verdict PASS with 2 waivers).
Both waived hard-fails were adjudicated with a decisive artifact-level test before waiving; both belong in the round-3 launch ADR.

## `ext__helmholtz_2d:completeness` — witness false-positive (resonance sensitivity)

The witness flagged pair (113, 284): standardized condition distance 0.035, relative field difference 0.221.
The decisive test is reconstruction: re-solving from the stored `x` alone through the registered solver reproduces the on-disk fields to rel-L2 $1.4\times10^{-15}$–$2.8\times10^{-15}$, including both witness-flagged rows.
The condition vector is complete; the witness fired on legitimate resonance sensitivity (near a Dirichlet eigenvalue, small wavenumber changes produce large smooth field changes — a steep map, not a stochastic one).
Round 2 recorded the same property as "trivially re-solvable from `x`" (rel-L2 2.2e-13).

## `sharp__sod_1d:pairing` — best-match ambiguity among near-duplicate rows

The pairing check reported row-match accuracy 0.01.
The decisive test is cross-level condition identity: `x` arrays of `train_l1/l2/l3` are bit-identical (`np.array_equal` True), so the ladder is aligned by construction — LF row i and HF row i share one parameter vector.
The low best-match accuracy comes from sod's near-degenerate rows (1-NN baseline 0.007: Riemann solutions are close to self-similar across the sampled range), which makes cosine best-match arbitrary among look-alikes.
Guard dataset; not a panel member.

## Expected warnings (not waived, documented)

- `sharp__phase_field_crystal_2d`, `sharp__fisher_kpp_2d` (+ 1d variants) `fidelity_gap`: the known weak-gap/NO_GAP physics under a complete band-limited IC — a round-3 panel-composition ADR item, per `condition_completeness_proposal/PROPOSAL.md` and the sample.yaml recipe notes.
- `ifc_poisson` NO_DATA: ifc_raw layout is not preflight's npz layout; its pairing defect and the staged nested-condition repair are measured directly in `mffp_autoresearch/ifc_pairing_repair/` (shipped row-match 0.2, repaired 1.0).
- guards `fluid`, `heat_local` `nn_baseline`: triviality screen on guards; guards are not meant to be won.
