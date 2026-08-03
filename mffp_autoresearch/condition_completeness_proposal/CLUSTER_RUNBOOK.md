# Cluster runbook — completing the repair pipeline (2026-08-03)

## State at local handoff (2026-08-03, Mac session paused its generation)

Already FINAL on the Mac's `benchmark_42/sharp` (certified COMPLETE, metas committed on this branch): `phase_field_crystal_2d`, `fisher_kpp_1d`, `allen_cahn_1d`.
INTERIM (complete but gapless first-pass; replace these): `fisher_kpp_2d` (T=0.05) and `allen_cahn_2d` (T=0.5) — their FINAL recipes are already in `sample.yaml` (fk `output_time: 0.30`; ac `eps_range: [0.012, 0.02]` + `output_time: 10.0`).
**The cluster's first job is regenerating those two at the final recipes**; regenerating all five for single-provenance is also fine (cheap).
The Caltech cluster (`login.hpc.caltech.edu`) has NO checkout and no ORCD mount — clone `nicksungg/mf_field` branch `mffp-trunk-eloise` (needs your GitHub auth), create a venv (`python/3.11` module; `pip install numpy scipy pyyaml h5py matplotlib scikit-image pytest && pip install -e mf_field_eloise_data/SURF_2026-main/mffp_sharp`), and use partition `expansion` (CPU) / `gpu` (anchors).
Heavy arrays are NOT in git — the cluster regenerates its own (each meta self-certifies via the generation gate), and only small artifacts (metas, reports, figures) flow back through the branch.

Paste the **Claude prompt** below into a Claude Code session on the cluster login node (run it inside `tmux` so it survives disconnects; durable work goes through `sbatch`, never the login shell).
Or run the **quick-start shell block** first if you just want the regeneration jobs submitted immediately.

## Quick-start shell block (deterministic part)

```bash
cd /orcd/data/faez/001/nick/mf_field   # or wherever the monorepo checkout lives
git fetch origin && git checkout mffp-trunk-eloise && git pull
cd mf_field_eloise_data && source .venv/bin/activate 2>/dev/null || source ../SURF_2026-main/.venv/bin/activate
for v in phase_field_crystal_2d fisher_kpp_2d allen_cahn_2d fisher_kpp_1d allen_cahn_1d; do
  sbatch -J regen_$v -p pi_faez -N1 --cpus-per-task=4 --mem=16G --time=6:00:00 \
    --mail-user=ezeng@caltech.edu --mail-type=END,FAIL \
    --wrap "python generate_standardized.py $v --ntrain 400 --ntest 100"
done
squeue -u $USER
```

The completeness gate runs inside each job and hard-fails the job on INCOMPLETE, writing `condition_completeness` into each output `meta.json`.

## Claude prompt (full pipeline)

> Work in the MFFP monorepo checkout (branch `mffp-trunk-eloise`, `git pull` first — read root `CLAUDE.md` and `mf_field_eloise_data/SURF_2026-main/CLAUDE.md`).
> Context you need before acting: `mffp_autoresearch/condition_completeness_proposal/` (PROPOSAL.md with the recipe history, APPROVAL.md — Eloise's operator approval covers this whole pipeline, mentor gate waived), `mffp_autoresearch/round3/PROGRAM_NOTE.md` (round-3 prerequisites), and `mffp_autoresearch/preflight/README.md` (preflight + HOLD contract).
>
> Tasks, in order, each verified against the artifact it should produce (never a job's exit status):
>
> 1. Regenerate through the fixed package path, via sbatch with `--mail-user=ezeng@caltech.edu --mail-type=END,FAIL`: `phase_field_crystal_2d`, `fisher_kpp_2d`, `allen_cahn_2d`, `fisher_kpp_1d`, `allen_cahn_1d` (recipes are already in `SURF_2026-main/mffp_sharp/configs/sample.yaml`; the generation gate certifies completeness in-job). Then audit every other `sharp_generated`/benchmark variant on the cluster: any meta with a stochastic module (`allen_cahn, cahn_hilliard, fisher_kpp, gray_scott, kdv, kuramoto_sivashinsky, nls, phase_field_crystal, sine_gordon, swift_hohenberg`) and zero `ic_c*` params is still defective — regenerate those too.
> 2. After jobs land: verify each `meta.json` has `condition_completeness.verdict == COMPLETE` with `reconstruction.rel_L2_max <= 1e-9`; run `python mffp_autoresearch/preflight/preflight.py --root <benchmark root> --datasets ...` and archive the report. Known/accepted flags: pfc and fisher_kpp are NO_GAP/weak-gap by physics (documented in PROPOSAL.md) — they are warnings for the round-3 panel ADR, not failures.
> 3. Swap regenerated data into the benchmark tree with the old data moved to `_incomplete_backup_2026-08-03/` (never deleted — round-2 numbers were measured on it). The Mac-side benchmark_42 swap is already done and pushed; keep layouts consistent with it.
> 4. The ladder fix is already LANDED on this branch (commit c29c269). Re-run `mffp_autoresearch/ladder_fix_proposal/verify_ladder_fix.py` on the cluster and regenerate the ifc-derived arrays it prescribes (the ifc_poisson pairing defect from round 2).
> 5. Only after 1–4 all verify: submit the 3-seed anchor runs for round 2's claimable slate (r2s2-B1, r2s3-B3, r2s1-B2/B3) on the repaired panel per `round3/PROGRAM_NOTE.md` §7 — these are round 3's launch anchors. GPU jobs via the factory harness (`MFFP_PARTITION` knob, default `mit_preemptable`; checkpoint-resume is mandatory).
> 6. Do NOT launch round 3. Its remaining prerequisites (preflight PASS archived + panel-composition ADR for helmholtz/ifc/pfc/fisher_kpp + operator go) are listed in the PROGRAM_NOTE; stop after the anchors and report.
> 7. If you find any defect on a mentor-owned surface mid-run: `python mffp_autoresearch/preflight/hold.py set --state <round dir>/state --reason "..."` FIRST, then report. Stop-the-line is the standing rule.
>
> Commit and push artifacts (reports, metas, logs summaries — not heavy arrays) back to `mffp-trunk-eloise` as you go; the Mac session syncs from there.
