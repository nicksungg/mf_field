# Approval record

**2026-08-05 — Mentor ratification.**
The mentor reviewed `CONDITION_COMPLETENESS_BRIEFING_2026-08-03.md` and endorsed option A (band-limited parametric ICs) as the fix, relayed by Eloise ("option A is good").
This retroactively ratifies the 2026-08-03 operator-authority waiver below; the executed repair and the mentor's chosen design coincide.
Recorded in the round-3 launch ADR (`round3/docs/adr/0001-launch-panel-composition.md`, D1).

**2026-08-03 — Operator approval: Eloise.**
Eloise directed that mentor sign-off is not required for this work; her approval is sufficient and is given for the full pipeline: the IC-encoding package changes, the completeness generation gate, regeneration of `phase_field_crystal_2d` / `fisher_kpp_2d` / `allen_cahn_2d` through the fixed path, the ladder-fix patch, and the gated sequence toward the 3-seed anchors and round 3.

Notes:

- The SURF `CLAUDE.md` sample-round mentor gate is waived by operator authority for this regeneration; the sample round was nevertheless produced and certified (`sample_round/`), so the de-risking evidence exists regardless of who approves.
- The fisher_kpp recipe decision (band-limited IC weakening the front regime) is resolved by the operator's delegation of domain judgment: `output_time` is retuned by a measured sweep (`fk_t_sweep`) to recover the LF-vs-HF gap, with the chosen value and its evidence recorded in the regeneration metadata and PROPOSAL.md.
- `DRAFT_MESSAGE_TO_NICHOLAS.md` is now optional/informational, not a gate.
