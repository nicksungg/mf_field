"""Train, predict, evaluate, and reload AutoMF on newly generated scalar fields.

Run from the repository root after `python -m pip install -e .`.
Use --models all after installing the neural extra to train the full library.
The analytic fields illustrate the API. They are not simulated PDE solutions.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from automf import FieldDataset, FieldPredictor


def fields(parameters: np.ndarray, height: int, width: int, coarse: bool) -> np.ndarray:
    """Evaluate a smooth parameterized field on the requested rectangular grid."""
    y, x = np.meshgrid(
        np.linspace(0.0, 1.0, height),
        np.linspace(0.0, 1.0, width),
        indexing="ij",
    )
    a = parameters[:, 0, None, None]
    b = parameters[:, 1, None, None]
    c = parameters[:, 2, None, None]
    broad = 1.0 + a * np.sin(np.pi * x) * np.sin(np.pi * y)
    broad = broad + 0.25 * b * np.cos(np.pi * y)
    detail = 0.12 * c * np.sin(3.0 * np.pi * x) * np.sin(2.0 * np.pi * y)
    output = 0.96 * broad if coarse else broad + detail
    return np.asarray(output, dtype=np.float32)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--models", default="M7", help="Comma separated model IDs, or all for M1 to M9",
    )
    parser.add_argument("--presets", choices=("balanced", "smoke"), default="smoke")
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--rule", choices=("selected", "inverse", "fitted"), default="fitted")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--output", type=Path, help="New predictor directory")
    args = parser.parse_args()

    run_name = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    output = args.output or Path("outputs") / f"new_dataset_{run_name}"
    models = "all" if args.models.lower() == "all" else args.models.split(",")

    rng = np.random.default_rng(42)
    x_coarse = rng.uniform(0.1, 0.9, size=(48, 3)).astype(np.float32)
    x_fine = x_coarse[:28].copy()
    x_test = rng.uniform(0.1, 0.9, size=(8, 3)).astype(np.float32)
    data = FieldDataset(
        low_fidelity=(x_coarse, fields(x_coarse, 8, 8, coarse=True)),
        high_fidelity=(x_fine, fields(x_fine, 16, 16, coarse=False)),
    )

    predictor = FieldPredictor(
        path=str(output),
        models=models,
        rule=args.rule,
        device=args.device,
        random_state=42,
    ).fit(data, fitting_size=5, presets=args.presets, epochs=args.epochs)

    # Test answers are used only after model training and weight fitting finish.
    prediction = predictor.predict(x_test)
    y_test = fields(x_test, 16, 16, coarse=False)
    metrics = predictor.evaluate(x_test, y_test)
    restored = FieldPredictor.load(str(output))
    np.testing.assert_allclose(restored.predict(x_test), prediction, rtol=1e-5, atol=1e-6)

    np.savez_compressed(output / "example_predictions.npz", x=x_test, y=y_test, predictions=prediction)
    report = {
        "example": "synthetic scalar fields, not a PDE benchmark",
        "models": models,
        "prediction_shape": list(prediction.shape),
        "leaderboard": predictor.leaderboard(),
        "evaluation": metrics,
        "reload_predictions_match": True,
    }
    (output / "example_metrics.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    print(f"Saved predictor and example outputs to {output}")


if __name__ == "__main__":
    main()
