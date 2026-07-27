"""fno_fire_quantile: quantile-regression distribution-conditioned residual. FIRE-family ablation — the LF predictive distribution is
obtained via quantile regression (pinball, q10/q50/q90 heads); the rest of the pipeline (condition a residual FNO on
[mu,sigma,q10,q50,q90], HF = mu_LF + delta) is shared via models/_common/fire_core."""
import argparse, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))   # factory_mffp (data_adapters)
sys.path.insert(0, str(HERE.parent))        # models/  -> _common package
from _common.fire_core import fire_run            # noqa: E402
from _common.fire_methods import QuantileLF            # noqa: E402

SMOKE = dict(hidden_channels=64, n_blocks=4, modes_cap=12, batch_size=16, lr=1e-3, weight_decay=1e-5, grad_clip=1.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset_dir", required=True)
    ap.add_argument("--dataset_name", required=True)
    ap.add_argument("--epochs", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--ckpt_dir", required=True)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    make_lf = lambda cd, grid, mh, mw, dev: QuantileLF(cd, grid, mh, mw, dev, SMOKE)
    fire_run(args, out, "fno_fire_quantile", make_lf,
             {"mf_mechanism": "quantile-regression distribution-conditioned residual", "uncertainty_source": "quantile regression (pinball, q10/q50/q90 heads)"}, SMOKE)
    print("[wrote]", out, flush=True)


if __name__ == "__main__":
    main()
