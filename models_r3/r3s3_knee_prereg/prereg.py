"""The SEALED pre-registration: the ladder source, and the digest that pins it.

Card `r3s3_lf_value-B3` CARDED CHANGE 1. The base family
(`models_r3/r3s3_row_efficiency` @ `eedcc655`) carried a HARDCODED
`LF_COND_CAP_LADDER` dict. On this card the ladder is not a constant of the
code: it is READ from the phase-P seal
(`R3S3B3_PREREG_JSON` = `state/r3s3_lf_value/prereg_knees_B3.json`), which was
written by `scripts/phase_p_prereg.py` BEFORE any leg ran.

WHY THE DIGEST IS BLOCKING (card part 3, phase P item 4, verbatim: "No GPU job
may be submitted before the seal exists"). The card's whole claim is the
DIRECTION of inference — the prediction precedes the measurement. Two things
could destroy it silently:

  * the seal being edited after a leg landed (a prediction retro-fitted to a
    result), and
  * a leg running against a seal that is not the one the card registered.

`R3S3B3_PREREG_SHA256` closes both: it is the sha256 of the CANONICAL payload
(`json.dumps(payload, sort_keys=True, separators=(',',':'), default=float)`),
carried in the card's `recipe.env`, and every leg recomputes it from the file it
actually read. Any byte of any prediction changing moves the digest and the leg
refuses to run. `_sealed_utc` is checked against the leg's own start time for
the same reason: a seal dated after the leg started is not a pre-registration.

NOTHING HERE WRITES. The seal is read-only to the family.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

LADDER_KEYS = ("r1", "r2", "r3", "r4")


def canonical(obj) -> bytes:
    """The digest convention, identical to `scripts/phase_p_prereg.py::canonical`."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      default=float).encode()


def payload_sha256(seal: dict) -> str:
    return hashlib.sha256(canonical(seal["payload"])).hexdigest()


def load(path, expected_sha256: str, enforce: bool, dataset: str = None) -> dict:
    """Read + verify the seal. Returns the record written into every result JSON."""
    p = Path(path)
    if not p.exists():
        raise SystemExit(
            f"PRE-REGISTRATION MISSING: {p} does not exist (R3S3B3_PREREG_JSON). "
            "Phase P (CPU only, scripts/phase_p_prereg.py) MUST run and seal the "
            "predicted knee caps BEFORE any training leg; that ordering IS this "
            "card's experiment. Refusing to run.")
    seal = json.loads(p.read_text())
    for key in ("_sealed_utc", "_payload_sha256", "payload"):
        if key not in seal:
            raise SystemExit(f"{p}: malformed seal, missing {key!r}")
    got = payload_sha256(seal)
    if got != seal["_payload_sha256"]:
        raise SystemExit(
            f"PRE-REGISTRATION CORRUPT: {p} carries _payload_sha256 "
            f"{seal['_payload_sha256']!r} but its payload hashes to {got!r} — the "
            "sealed predictions were edited after sealing. Refusing to run.")
    if enforce:
        if not expected_sha256 or expected_sha256.startswith("<"):
            raise SystemExit(
                "R3S3B3_PREREG_SHA256 is unset or still the card's transcription "
                f"placeholder ({expected_sha256!r}). The seal at {p} hashes to "
                f"{got}; put that value in the card recipe and in the leg's --env. "
                "R3S3B3_PREREG_ASSERT=1 refuses to run without it.")
        if expected_sha256 != got:
            raise SystemExit(
                f"PRE-REGISTRATION MISMATCH: R3S3B3_PREREG_SHA256={expected_sha256!r} "
                f"but {p} hashes to {got!r}. This leg would be measured against a "
                "different pre-registration than the card registered. Refusing to run.")
    cells = seal["payload"].get("cells", {})
    if dataset is not None and dataset not in cells:
        raise SystemExit(
            f"PRE-REGISTRATION has no entry for {dataset!r} (sealed cells: "
            f"{sorted(cells)}). Every ladder leg of this card runs on a sealed cell; "
            "an unsealed cell has no registered prediction and must not be scored "
            "as if it had one.")
    return seal


def sealed_utc(seal: dict) -> datetime:
    return datetime.strptime(seal["_sealed_utc"], "%Y-%m-%dT%H:%M:%SZ").replace(
        tzinfo=timezone.utc)


def assert_sealed_before(seal: dict, leg_start: datetime) -> dict:
    """Card `_blocking_preflights` (1): `_sealed_utc` precedes every leg start."""
    ts = sealed_utc(seal)
    if ts > leg_start:
        raise SystemExit(
            f"PRE-REGISTRATION ORDERING VIOLATED: the seal is dated {seal['_sealed_utc']} "
            f"but this leg started at {leg_start.strftime('%Y-%m-%dT%H:%M:%SZ')}. A "
            "prediction written after the measurement is not a pre-registration.")
    return {"sealed_utc": seal["_sealed_utc"],
            "leg_start_utc": leg_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "seal_precedes_leg": True,
            "lead_seconds": int((leg_start - ts).total_seconds())}


def ladder_for(seal: dict, dataset: str) -> tuple:
    """The sealed `{r1, r2, r3, r4}` for one cell — this card's ONLY cap ladder."""
    cell = seal["payload"]["cells"][dataset]
    lad = cell["ladder"]
    rungs = tuple(int(lad[k]) for k in LADDER_KEYS)
    if not (1 <= rungs[0] < rungs[1] < rungs[2] < rungs[3]):
        raise SystemExit(f"{dataset}: sealed ladder {rungs} violates 1 <= r1 < r2 < r3 "
                         "< r4; the seal is not usable")
    return rungs


def cell_record(seal: dict, dataset: str, path) -> dict:
    """The block every result JSON of this card carries."""
    cell = seal["payload"]["cells"][dataset]
    return {
        "prereg_json": str(path),
        "payload_sha256": seal["_payload_sha256"],
        "sealed_utc": seal["_sealed_utc"],
        "instrument": seal.get("_instrument"),
        "driver": seal.get("_driver"),
        "view": seal["payload"].get("_view"),
        "dataset": dataset,
        "cell_role": cell.get("cell_role"),
        "ladder": [int(cell["ladder"][k]) for k in LADDER_KEYS],
        "ladder_branch": cell["ladder"].get("branch"),
        "c_hat_dense": cell.get("c_hat"),
        "c_pred_REGISTERED": cell.get("c_pred"),
        "c_pred_linear_specificity_control":
            cell.get("c_pred_linear_specificity_control"),
        "c_pred_diverges_from_c_hat": cell.get("c_pred_diverges_from_c_hat"),
        "margin_R_surrogate": cell.get("margin_R_surrogate"),
        "R_surr_curve_on_ladder": cell.get("R_surr_curve_on_ladder"),
        "structural_nulls": cell.get("structural_nulls"),
        "fold_population_histogram_summary": {
            k: cell.get("fold_population_histogram", {}).get(k)
            for k in ("applicable", "n_draws", "counts", "modal_knee",
                      "modal_frequency", "c_pred_frequency", "reason")},
        "reproduction_control": cell.get("reproduction_control"),
        "film_units": cell.get("film_units"),
        "lf_rungs_trained_at_seal_time": cell.get("lf_rungs_trained"),
        "role": "PRE-REGISTERED PREDICTION. The trained step-max knee K is computed "
                "ANALYSIS-SIDE from the five legs of this cell; this family emits no "
                "cross-arm quantity and never compares K to c_pred in-process.",
    }
