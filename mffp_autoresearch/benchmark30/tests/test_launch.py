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


def _mk_tier_env(tmp_path, cfg_small, tier, epochs, seeds, scores, states, ledger=None):
    """Fixture env for validate_tier: submissions + score files + fake sacct."""
    state = tmp_path / "state"
    state.mkdir(parents=True, exist_ok=True)
    mh = HASH8 + "f" * 56
    (state / "staging_manifest.json").write_text(json.dumps(
        {"sealed": True, "manifest_hash": mh, "registry_revision": "b30-0001",
         "datasets": {}}))
    subs = [{"job_name": f"j{i}", "job_id": str(1000 + i), "tier": tier,
             "family": f, "seed": s, "epochs": epochs, "manifest_hash": mh,
             "utc": "x"}
            for i, (f, s) in enumerate((f, s) for f in cfg_small["families"] for s in seeds)]
    (state / "submissions.json").write_text(json.dumps(subs))
    if ledger:
        (state / "exclusion_ledger.json").write_text(json.dumps(ledger))
    rev = Path(cfg_small["output_root"]) / f"rev-{HASH8}"
    d = rev / "results/scores"
    d.mkdir(parents=True, exist_ok=True)
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "b30_pd_fixture", Path(__file__).resolve().parents[1] / "eval/panel_data.py")
    pd_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pd_mod)
    for fam, seed, ds in scores:
        (d / f"{fam}_s{seed}_e{epochs}_{ds}.json").write_text(json.dumps(
            {"family": fam, "seed": seed, "epochs": epochs,
             "copylf_def_hash": pd_mod.COPYLF_DEF_HASH,
             "per_dataset": {ds: {"nRMSE": 0.1}}}))
    return state, (lambda ids: {j: states.get(j, "COMPLETED") for j in ids})


def test_validate_tier_records_g3_when_all_cells_accounted(tmp_path):
    from staging.validate_tier import validate_tier
    cfg_small = {"output_root": str(tmp_path / "out"),
                 "families": {"famA": "x", "famB": "y"},
                 "epochs": {"smoke": 2, "full": 200},
                 "datasets": {"core": [{"id": "d1", "dataset_dir": "d1"},
                                       {"id": "d2", "dataset_dir": "d2"}]}}
    scores = [(f, 0, ds) for f in ("famA", "famB") for ds in ("d1",)]
    ledger = {"famA": {"d2": "raise"}, "famB": {"d2": "raise"}}
    state, sacct = _mk_tier_env(tmp_path, cfg_small, "smoke", 2, [0], scores,
                                {"1000": "COMPLETED", "1001": "FAILED"}, ledger)
    entry = validate_tier(cfg_small, "smoke", state_dir=state, sacct_fn=sacct)
    g = json.load(open(state / "gates.json"))
    assert "G3" in g and g["G3"]["manifest_hash"] == HASH8 + "f" * 56


def test_validate_tier_refuses_unaccounted_cell_and_nonterminal(tmp_path):
    from staging.validate_tier import validate_tier
    cfg_small = {"output_root": str(tmp_path / "out"),
                 "families": {"famA": "x"},
                 "epochs": {"smoke": 2, "full": 200},
                 "datasets": {"core": [{"id": "d1", "dataset_dir": "d1"},
                                       {"id": "d2", "dataset_dir": "d2"}]}}
    scores = [("famA", 0, "d1")]  # d2 unscored and NOT ledgered
    state, sacct = _mk_tier_env(tmp_path, cfg_small, "smoke", 2, [0], scores, {})
    with pytest.raises(RuntimeError, match="no score JSON and no ledger"):
        validate_tier(cfg_small, "smoke", state_dir=state, sacct_fn=sacct)
    # running job -> refuse regardless of files
    state2, _ = _mk_tier_env(tmp_path / "b", cfg_small, "smoke", 2, [0],
                             scores + [("famA", 0, "d2")], {})
    with pytest.raises(RuntimeError, match="not terminal"):
        validate_tier(cfg_small, "smoke", state_dir=state2,
                      sacct_fn=lambda ids: {j: "RUNNING" for j in ids})


def test_validate_tier_latest_attempt_supersedes_failed(tmp_path):
    """micro-fix M2: a retry (new submission) must clear an earlier FAILED
    attempt; and (M1) a job invisible to sacct must refuse the gate."""
    from staging.validate_tier import validate_tier
    cfg_small = {"output_root": str(tmp_path / "out"),
                 "families": {"famA": "x"},
                 "epochs": {"smoke": 2, "full": 200},
                 "datasets": {"core": [{"id": "d1", "dataset_dir": "d1"}]}}
    state, _ = _mk_tier_env(tmp_path, cfg_small, "full-seed0", 200, [0],
                            [("famA", 0, "d1")], {})
    mh = HASH8 + "f" * 56
    subs = json.load(open(state / "submissions.json"))
    subs.append({**subs[0], "job_id": "2000"})  # retry of the same cell
    (state / "submissions.json").write_text(json.dumps(subs))
    entry = validate_tier(cfg_small, "full-seed0", state_dir=state,
                          sacct_fn=lambda ids: {j: "COMPLETED" for j in ids}
                          if ids == ["2000"] else {j: "FAILED" for j in ids})
    assert list(entry["jobs"]) == ["2000"], "only the latest attempt is validated"
    with pytest.raises(RuntimeError, match="no state for submitted"):
        validate_tier(cfg_small, "full-seed0", state_dir=state,
                      sacct_fn=lambda ids: {})
    # missing expected cell refuses
    (state / "submissions.json").write_text("[]")
    with pytest.raises(RuntimeError, match="no full-seed0 submission recorded"):
        validate_tier(cfg_small, "full-seed0", state_dir=state,
                      sacct_fn=lambda ids: {})


def test_validate_tier_rejects_truncated_score_artifact(tmp_path):
    """round-2 test-quality fix: an EMPTY score file must not certify a tier
    (mutation: `run_ds ... && : > out_json` truncates after write)."""
    from staging.validate_tier import validate_tier
    cfg_small = {"output_root": str(tmp_path / "out"),
                 "families": {"famA": "x"},
                 "epochs": {"smoke": 2, "full": 200},
                 "datasets": {"core": [{"id": "d1", "dataset_dir": "d1"}]}}
    state, sacct = _mk_tier_env(tmp_path, cfg_small, "smoke", 2, [0],
                                [("famA", 0, "d1")], {})
    art = Path(cfg_small["output_root"]) / f"rev-{HASH8}/results/scores/famA_s0_e2_d1.json"
    art.write_text("")  # truncated
    with pytest.raises(RuntimeError, match="score artifact invalid"):
        validate_tier(cfg_small, "smoke", state_dir=state, sacct_fn=sacct)
