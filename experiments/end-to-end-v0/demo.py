#!/usr/bin/env python3
"""Run the synthetic local telemetry-to-proof demonstrator.

EXPERIMENTAL
SYNTHETIC_ONLY
A0_SYNTHETIC
NOT VALIDATION OR PRODUCTION AUTHORIZATION
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MAVLINK_DIR = ROOT / "mavlink-normalization-v0"
PROOF_DIR = ROOT / "bounded-speed-proof-v0"

for module_dir in (PROOF_DIR, MAVLINK_DIR):
    path = str(module_dir)
    if path not in sys.path:
        sys.path.insert(0, path)

import mavlink_normalize as telemetry  # noqa: E402
import prove as proof_prover  # noqa: E402
import verify as proof_verifier  # noqa: E402

LABELS = (
    "EXPERIMENTAL",
    "SYNTHETIC_ONLY",
    "A0_SYNTHETIC",
    "NOT VALIDATION OR PRODUCTION AUTHORIZATION",
)

UINT32_MAX = (1 << 32) - 1


class DemoError(ValueError):
    """Typed local-demonstrator input failure."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def _validate_public_limit(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= UINT32_MAX:
        raise DemoError("INVALID_PUBLIC_LIMIT")
    return value


def load_capture(path: Path, capture_name: str) -> dict[str, Any]:
    """Load one named synthetic capture without returning unrelated fixtures."""
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        raise DemoError("FIXTURE_UNAVAILABLE_OR_INVALID") from None
    if not isinstance(document, dict):
        raise DemoError("FIXTURE_UNAVAILABLE_OR_INVALID")
    captures = document.get("captures")
    if not isinstance(captures, list):
        raise DemoError("FIXTURE_UNAVAILABLE_OR_INVALID")
    for capture in captures:
        if isinstance(capture, dict) and capture.get("name") == capture_name:
            return capture
    raise DemoError("CAPTURE_NOT_FOUND")


def _base_result(capture_name: str) -> dict[str, Any]:
    return {
        "labels": list(LABELS),
        "experiment": "end-to-end-v0",
        "capture_case": capture_name,
        "invocation": {"status": "NOT_CHECKED", "reason": None},
        "telemetry": {
            "status": "NOT_CHECKED",
            "reason": None,
            "assurance_id": "A0_SYNTHETIC",
            "source_trust": "NOT_EVALUATED",
        },
        "predicate": "NOT_EVALUATED",
        "proof_generation": "NOT_ATTEMPTED",
        "verification_input": {"status": "NOT_CHECKED", "reason": None},
        "cryptographic": {"status": "NOT_CHECKED", "reason": None},
        "policy": "NOT_EVALUATED",
        "freshness": "NOT_EVALUATED",
        "revocation": "NOT_EVALUATED",
        "replay": "NOT_EVALUATED",
        "assurance": {
            "declared": "A0_SYNTHETIC",
            "effective": "A0_SYNTHETIC",
            "required": "NOT_EVALUATED",
            "demonstrator": "A0_SYNTHETIC",
        },
        "publication": "NOT_PERFORMED",
        "relying_party_decision": "NOT_MADE",
        "proof_validity_is_telemetry_truth": False,
        "private_witness_disclosed": False,
        "command_path": "NONE",
    }


def _run_with_package(
    capture_name: str,
    capture: dict[str, Any],
    maximum_speed_cm_s: int,
    package_dir: Path,
) -> dict[str, Any]:
    result = _base_result(capture_name)
    maximum_speed_cm_s = _validate_public_limit(maximum_speed_cm_s)
    result["invocation"] = {"status": "ACCEPTED", "reason": None}

    normalized = telemetry.evaluate_capture(capture)
    if normalized.get("status") != "NORMALIZED":
        result["telemetry"] = {
            "status": "REJECTED",
            "reason": normalized.get("reason_code", "TELEMETRY_REJECTED"),
            "assurance_id": "A0_SYNTHETIC",
            "source_trust": "NOT_EVALUATED",
        }
        return result

    source = normalized.get("source") if isinstance(normalized.get("source"), dict) else {}
    result["telemetry"] = {
        "status": "NORMALIZED",
        "reason": None,
        "assurance_id": normalized.get("assurance_id", "A0_SYNTHETIC"),
        "source_trust": source.get("trust", "UNKNOWN"),
    }

    private_speed = normalized.get("speed_cm_s")
    try:
        prove_result = proof_prover.prove_package(
            private_speed,
            maximum_speed_cm_s,
            package_dir,
        )
    except (proof_prover.ExperimentError, OSError):
        result["predicate"] = "SATISFIED_OR_NOT_EVALUATED"
        result["proof_generation"] = "UNAVAILABLE"
        result["cryptographic"] = {
            "status": "UNVERIFIABLE",
            "reason": "PROVER_UNAVAILABLE_OR_FAILED",
        }
        return result

    result["predicate"] = prove_result.get("predicate", "NOT_EVALUATED")
    if result["predicate"] == "NOT_SATISFIED":
        result["proof_generation"] = "NOT_ATTEMPTED"
        return result

    if not prove_result.get("package_written"):
        result["proof_generation"] = "FAILED"
        result["cryptographic"] = {
            "status": "UNVERIFIABLE",
            "reason": "PROOF_PACKAGE_NOT_WRITTEN",
        }
        return result

    result["proof_generation"] = "GENERATED"
    verification = proof_verifier.verify_public_package(
        package_dir / "public-artifact.cbor",
        package_dir / "proof",
        package_dir / "vk",
    )
    result["verification_input"] = verification.get(
        "input", {"status": "NOT_CHECKED", "reason": None}
    )
    result["cryptographic"] = verification.get(
        "cryptographic", {"status": "NOT_CHECKED", "reason": None}
    )
    for dimension in (
        "policy",
        "freshness",
        "revocation",
        "replay",
        "assurance",
        "publication",
        "relying_party_decision",
        "proof_validity_is_telemetry_truth",
    ):
        if dimension in verification:
            result[dimension] = verification[dimension]
    return result


def run_capture(
    capture_name: str,
    capture: dict[str, Any],
    maximum_speed_cm_s: int,
    package_dir: Path | None = None,
) -> dict[str, Any]:
    """Normalize, prove, and independently verify one synthetic capture."""
    if package_dir is not None:
        return _run_with_package(
            capture_name, capture, maximum_speed_cm_s, package_dir
        )
    with tempfile.TemporaryDirectory(prefix="tag-end-to-end-") as temporary:
        return _run_with_package(
            capture_name, capture, maximum_speed_cm_s, Path(temporary)
        )


def run_fixture(
    capture_file: Path,
    capture_name: str,
    maximum_speed_cm_s: int,
    package_dir: Path | None = None,
) -> dict[str, Any]:
    capture = load_capture(capture_file, capture_name)
    return run_capture(
        capture_name, capture, maximum_speed_cm_s, package_dir=package_dir
    )


def exit_code(result: dict[str, Any]) -> int:
    if result["invocation"]["status"] == "REJECTED":
        return 6
    if result["telemetry"]["status"] == "REJECTED":
        return 2
    if result["predicate"] == "NOT_SATISFIED":
        return 3
    cryptographic = result["cryptographic"]["status"]
    if cryptographic == "VALID":
        return 0
    if cryptographic == "INVALID":
        return 4
    if cryptographic == "UNVERIFIABLE":
        return 5
    return 6


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--capture-file",
        type=Path,
        default=MAVLINK_DIR / "fixtures.json",
        help="synthetic capture fixture file",
    )
    parser.add_argument(
        "--capture-name",
        default="unsigned-consistent",
        help="named synthetic capture",
    )
    parser.add_argument(
        "--maximum-speed-cm-s",
        type=int,
        required=True,
        help="public synthetic policy limit",
    )
    args = parser.parse_args()

    try:
        result = run_fixture(
            args.capture_file,
            args.capture_name,
            args.maximum_speed_cm_s,
        )
    except DemoError as exc:
        result = _base_result(args.capture_name)
        if exc.code == "INVALID_PUBLIC_LIMIT":
            result["invocation"] = {"status": "REJECTED", "reason": exc.code}
        else:
            result["telemetry"] = {
                "status": "REJECTED",
                "reason": exc.code,
                "assurance_id": "A0_SYNTHETIC",
                "source_trust": "NOT_EVALUATED",
            }
    print(json.dumps(result, indent=2, sort_keys=True))
    return exit_code(result)


if __name__ == "__main__":
    raise SystemExit(main())
