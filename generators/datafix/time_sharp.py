"""Time the sharp (SURF) solvers per resolution for the roster PDEs that do not need PyClaw.
Uses the package's own sample_configs/generate_sample with the shipped configs/sample.yaml resolutions."""
import sys, time, json, importlib, traceback
import numpy as np, yaml
S = "/archive/mf_field_solver_data/SURF_2026-main/mffp_sharp"; sys.path.insert(0, S + "/src")
cfg = yaml.safe_load(open(S + "/configs/sample.yaml"))
print("top-level keys:", list(cfg.keys())[:12])
pdes = cfg.get("pdes") or cfg.get("datasets") or {}
out = {}
for name, block in pdes.items():
    mod_name = block.get("module", name); ndim = block.get("ndim", 2)
    try:
        mod = importlib.import_module(f"mffp_sharp.pdes.{mod_name}")
    except Exception as e:
        print(f"[{name}] import failed: {e}"); continue
    if "clawpack" in (open(f"{S}/src/mffp_sharp/pdes/{mod_name}.py").read()):
        print(f"[{name}] needs PyClaw (clawpack not installed) -> skipped"); out[name] = "needs_pyclaw"; continue
    ladder = block.get("ladder") or cfg.get("ladder") or {}; res = ladder.get("resolutions") or block.get("resolutions"); hf = res[ladder.get("hf_index", -1)] if res else None
    T = block.get("T", block.get("output_time", cfg.get("T", 1.0)))
    try:
        specs = mod.sample_configs(2, block.get("sampling", {}), ndim, 0)
    except Exception as e:
        print(f"[{name}] sample_configs failed: {e}"); traceback.print_exc(limit=1); continue
    rows = {}
    for r in res:
        ts = []
        for spec in specs:
            t = time.perf_counter()
            try:
                mod.generate_sample(spec, [r], r, T)
            except Exception as e:
                print(f"[{name}] res {r} failed: {e}"); ts = None; break
            ts.append(time.perf_counter() - t)
        if ts: rows[r] = float(np.median(ts))
    out[name] = rows; print(f"[{name}] ndim={ndim} T={T} seconds/solve by resolution: { {r: round(v, 3) for r, v in rows.items()} }", flush=True)
json.dump(out, open("/archive/mf_field/experiments/datafix/sharp_costs.json", "w"), indent=1); print("SHARP_TIMING_DONE")
