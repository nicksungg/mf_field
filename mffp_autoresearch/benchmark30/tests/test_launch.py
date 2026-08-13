"""A8: SLURM launcher + gate→tier matrix (spec D6, D10, D12).

Dry-run tests only — nothing is submitted.  The launcher must refuse each
tier until exactly its required gates are recorded (smoke: G0–G2; full
seed 0: +G3; full seeds 1–2: +G4), render every mutable path under the
D12 revision root, and isolate per-dataset failures (one score_panel
invocation per dataset).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

CAMPAIGN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CAMPAIGN))

from slurm.launch import TIER_GATES, GateError, render_jobs  # noqa: E402

HASH8 = "abcd1234"


def _mk_state(tmp_path, gates):
    state = tmp_path / "state"
    state.mkdir(parents=True)
    (state / "staging_manifest.json").write_text(json.dumps(
        {"sealed": True, "manifest_hash": HASH8 + "f" * 56,
         "registry_revision": "b30-0001", "datasets": {}}))
    (state / "gates.json").write_text(json.dumps(
        {g: {"utc": "2026-08-12T00:00:00Z", "evidence": "test",
             "manifest_hash": HASH8 + "f" * 56} for g in gates}))
    return state


@pytest.fixture()
def cfg():
    import yaml
    with open(CAMPAIGN / "config.yaml") as f:
        return yaml.safe_load(f)


def test_tier_gate_matrix_is_the_spec_matrix():
    assert TIER_GATES == {
        "smoke": ["G0", "G1", "G2"],
        "full-seed0": ["G0", "G1", "G2", "G3"],
        "full-seeds12": ["G0", "G1", "G2", "G3", "G4"],
    }


@pytest.mark.parametrize("tier", list(TIER_GATES))
def test_each_tier_refuses_every_insufficient_gate_combo(cfg, tmp_path, tier):
    need = TIER_GATES[tier]
    for missing in need:
        state = _mk_state(tmp_path / f"m_{tier}_{missing}", [g for g in need if g != missing])
        with pytest.raises(GateError, match=missing):
            render_jobs(cfg, tier=tier, state_dir=state)


def test_smoke_renders_both_families_all_30(cfg, tmp_path):
    state = _mk_state(tmp_path, ["G0", "G1", "G2"])
    jobs = render_jobs(cfg, tier="smoke", state_dir=state)
    assert {j["family"] for j in jobs} == {"r3s2_route_b30", "mf_fno_transfer_film"}
    assert all(j["seed"] == 0 and j["epochs"] == 2 for j in jobs)
    assert all(len(j["datasets"]) == 30 for j in jobs)


def test_full_seed0_renders_200_epochs_and_filters_ledger(cfg, tmp_path):
    state = _mk_state(tmp_path, ["G0", "G1", "G2", "G3"])
    (state / "exclusion_ledger.json").write_text(json.dumps(
        {"r3s2_route_b30": {"era5": "WORK_CAP raise (spec D11)"}}))
    jobs = render_jobs(cfg, tier="full-seed0", state_dir=state)
    r3s2 = next(j for j in jobs if j["family"] == "r3s2_route_b30")
    film = next(j for j in jobs if j["family"] == "mf_fno_transfer_film")
    assert "era5" not in r3s2["datasets"] and len(r3s2["datasets"]) == 29
    assert "era5" in film["datasets"]
    assert all(j["epochs"] == 200 and j["seed"] == 0 for j in jobs)


def test_full_seeds12_renders_four_jobs(cfg, tmp_path):
    state = _mk_state(tmp_path, ["G0", "G1", "G2", "G3", "G4"])
    jobs = render_jobs(cfg, tier="full-seeds12", state_dir=state)
    assert sorted((j["family"], j["seed"]) for j in jobs) == [
        ("mf_fno_transfer_film", 1), ("mf_fno_transfer_film", 2),
        ("r3s2_route_b30", 1), ("r3s2_route_b30", 2)]


def test_sbatch_script_contract(cfg, tmp_path):
    state = _mk_state(tmp_path, ["G0", "G1", "G2"])
    jobs = render_jobs(cfg, tier="smoke", state_dir=state)
    script = jobs[0]["script"]
    rev_root = f"{cfg['output_root']}/rev-{HASH8}"
    for required in (
        "#SBATCH --partition=gpu",
        "#SBATCH --gres=gpu:nvidia_h200:1",
        "#SBATCH --mail-user=ezeng@caltech.edu",
        "#SBATCH --mail-type=END,FAIL",
        f"#SBATCH --output={rev_root}/logs/%x_%j.out",
        f"#SBATCH --error={rev_root}/logs/%x_%j.err",
        f"export ROUND2_EVAL_RESULTS={rev_root}/results",
        f"export ROUND2_EVAL_CACHE={rev_root}/cache",
    ):
        assert required in script, f"sbatch missing: {required}"
    # per-dataset isolation: one scorer invocation per dataset, failure recorded
    assert script.count("score_panel.py") >= 30
    assert script.count("--out") >= 30 and "/results/scores/" in script
    assert "FAILED" in script and "exit 1" in script, \
        "residual non-ledgered failures must exit nonzero (r1-lifecycle-3)"


def test_r3s2_carries_recipe_env_film_does_not(cfg, tmp_path):
    state = _mk_state(tmp_path, ["G0", "G1", "G2"])
    jobs = render_jobs(cfg, tier="smoke", state_dir=state)
    r3s2 = next(j for j in jobs if j["family"] == "r3s2_route_b30")
    film = next(j for j in jobs if j["family"] == "mf_fno_transfer_film")
    assert "R3S2B2_ARM=A1_stack_ic_reg" in r3s2["script"]
    assert "R3S2_TARGET_SCALER_PREFLIGHT=not_applicable_no_helmholtz_no_pfc_in_datasets" \
        in r3s2["script"]
    assert "R3S2B2_ARM" not in film["script"]


def test_gates_must_be_bound_to_the_active_manifest(cfg, tmp_path):
    """r1 fix F4: a gate recorded under a DIFFERENT manifest must not authorize
    a launch into the current revision namespace."""
    state = _mk_state(tmp_path, [])
    stale = {g: {"utc": "x", "evidence": "y", "manifest_hash": "0" * 64}
             for g in ("G0", "G1", "G2")}
    (state / "gates.json").write_text(json.dumps(stale))
    with pytest.raises(GateError, match="manifest"):
        render_jobs(cfg, tier="smoke", state_dir=state)
    # matching hash -> allowed
    good = {g: {"utc": "x", "evidence": "y", "manifest_hash": HASH8 + "f" * 56}
            for g in ("G0", "G1", "G2")}
    (state / "gates.json").write_text(json.dumps(good))
    assert render_jobs(cfg, tier="smoke", state_dir=state)


def test_sbatch_retries_and_honest_exit(cfg, tmp_path):
    """r1 fix F5: per-dataset bounded retries (retry_cap) and a NONZERO exit
    when any non-ledgered dataset still failed — so FAIL mail actually fires
    and sacct COMPLETED means what G4 needs it to mean."""
    state = _mk_state(tmp_path, ["G0", "G1", "G2"])
    jobs = render_jobs(cfg, tier="smoke", state_dir=state)
    script = jobs[0]["script"]
    assert "for attempt in $(seq 1 3)" in script, "retry_cap=3 loop missing"
    assert "exit 1" in script, "residual failures must exit nonzero"
    assert not script.rstrip().endswith("exit 0"), \
        "unconditional exit 0 masks failures (r1-lifecycle-3)"


def test_submissions_persisted_incrementally(cfg, tmp_path, monkeypatch):
    """r1 fix F7: each accepted job id lands on disk immediately."""
    import slurm.launch as L
    state = _mk_state(tmp_path, ["G0", "G1", "G2"])
    calls = []

    def fake_run(cmd, **kw):
        calls.append(cmd)
        if len(calls) == 2:
            raise RuntimeError("sbatch down")
        class R: stdout = f"Submitted batch job 100{len(calls)}\n"
        return R()

    monkeypatch.setattr(L.subprocess, "run", fake_run)
    jobs = render_jobs(cfg, tier="smoke", state_dir=state)
    sub_file = tmp_path / "submissions.json"
    with pytest.raises(RuntimeError):
        L.submit(jobs, tmp_path / "rev", sub_file=sub_file, tier="smoke",
                 manifest_hash=HASH8 + "f" * 56)
    recorded = json.load(open(sub_file))
    assert len(recorded) == 1 and recorded[0]["job_id"] == "1001", \
        "the job accepted before the sbatch failure must already be on disk"
