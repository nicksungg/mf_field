"""Contract-shaped fake family for score_panel tests. Trains nothing.

Env knobs:
  FAKE_NRMSE  — reported test nRMSE (default 0.5); part of the recipe/cache-key tests.
  FAKE_BREAK  — missing_key | wrong_dataset | nan : produce one contract violation.
"""
import argparse
import json
import os


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dataset_dir", required=True)
    p.add_argument("--dataset_name", required=True)
    p.add_argument("--epochs", type=int, required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--ckpt_dir", required=True)
    p.add_argument("--seed", type=int, required=True)
    args = p.parse_args()

    os.makedirs(args.ckpt_dir, exist_ok=True)
    value = float(os.environ.get("FAKE_NRMSE", "0.5"))
    mode = os.environ.get("FAKE_BREAK", "")
    shape = os.environ.get("FAKE_MODE", "")

    if shape == "factory_style":
        # mimic data_adapters.metrics.finalize_and_write output
        splits = {"test_hf": {"nRMSE": 0.9, "rel_l2_mean": 0.3,
                              "rel_l2_per_sample": [0.2, 0.4], "n_samples": 2}}
    elif shape == "ood_only":
        splits = {"ood_l4": {"nRMSE": value}}
    else:
        splits = {"test": {"nRMSE": value}}

    result = {
        "model": "fake_family",
        "dataset": args.dataset_name,
        "splits": splits,
    }
    if mode == "missing_key":
        del result["splits"]["test"]["nRMSE"]
    elif mode == "wrong_dataset":
        result["dataset"] = "some_other_dataset"
    elif mode == "nan":
        result["splits"]["test"]["nRMSE"] = float("nan")

    with open(args.out, "w") as f:
        json.dump(result, f)


if __name__ == "__main__":
    main()
