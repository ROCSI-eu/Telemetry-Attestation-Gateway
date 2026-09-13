#!/usr/bin/env python3
"""Independently verify a synthetic bounded-speed proof from public material only.

EXPERIMENTAL
SYNTHETIC_ONLY
A0_SYNTHETIC
NOT VALIDATION OR PRODUCTION AUTHORIZATION
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import tempfile
from typing import Any

from common import BOUNDED, ExperimentError, LABELS, public_inputs_json, reconstruct_bb_public_inputs, require_bb


def _base_result() -> dict[str, Any]:
    return {
        "labels": list(LABELS),
        "input": {"status": "NOT_CHECKED", "reason": None},
        "cryptographic": {"status": "NOT_CHECKED", "reason": None},
        "policy": "NOT_EVALUATED",
        "freshness": "NOT_EVALUATED",
        "revocation": "NOT_EVALUATED",
        "replay": "NOT_EVALUATED",
        "assurance": {"declared": "A0_SYNTHETIC", "effective": "A0_SYNTHETIC", "required": "NOT_EVALUATED", "demonstrator": "A0_SYNTHETIC"},
        "publication": "NOT_PERFORMED",
        "relying_party_decision": "NOT_MADE",
        "proof_validity_is_telemetry_truth": False,
    }


def verify_public_package(public_artifact_path: Path, proof_path: Path, verification_key_path: Path) -> dict[str, Any]:
    result = _base_result()
    try:
        public_artifact = public_artifact_path.read_bytes()
    except OSError:
        result["input"] = {"status": "REJECTED", "reason": "PUBLIC_ARTIFACT_UNAVAILABLE"}
        return result
    try:
        artifact = BOUNDED.decode_public_artifact(public_artifact)
        ordered = reconstruct_bb_public_inputs(public_artifact)
        expected_json = public_inputs_json(public_artifact)
    except (BOUNDED.EncodingError, ExperimentError):
        result["input"] = {"status": "REJECTED", "reason": "PUBLIC_ARTIFACT_MALFORMED_OR_INCOMPATIBLE"}
        return result
    result["input"] = {"status": "ACCEPTED", "reason": None, "schema_version": artifact["version"], "public_input_names": [name for name, _ in ordered]}
    if not proof_path.is_file() or not verification_key_path.is_file():
        result["cryptographic"] = {"status": "UNVERIFIABLE", "reason": "PROOF_OR_KEY_UNAVAILABLE"}
        return result
    try:
        bb_path, _ = require_bb()
    except ExperimentError:
        result["cryptographic"] = {"status": "UNVERIFIABLE", "reason": "INCOMPATIBLE_OR_MISSING_VERIFIER"}
        return result
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", prefix="tag-expected-public-inputs-", suffix=".json", delete=False) as handle:
        handle.write(expected_json)
        expected_path = Path(handle.name)
    try:
        completed = subprocess.run([bb_path, "verify", "-i", str(expected_path), "-p", str(proof_path), "-k", str(verification_key_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError:
        result["cryptographic"] = {"status": "UNVERIFIABLE", "reason": "VERIFIER_EXECUTION_FAILED"}
        return result
    finally:
        expected_path.unlink(missing_ok=True)
    if completed.returncode == 0:
        result["cryptographic"] = {"status": "VALID", "reason": None}
    else:
        result["cryptographic"] = {"status": "INVALID", "reason": "PROOF_REJECTED"}
    return result


def exit_code(result: dict[str, Any]) -> int:
    if result["input"]["status"] == "REJECTED":
        return 2
    status = result["cryptographic"]["status"]
    if status == "VALID":
        return 0
    if status == "INVALID":
        return 3
    return 4


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--public-artifact", type=Path, required=True)
    parser.add_argument("--proof", type=Path, required=True)
    parser.add_argument("--verification-key", type=Path, required=True)
    args = parser.parse_args()
    result = verify_public_package(args.public_artifact, args.proof, args.verification_key)
    print(json.dumps(result, indent=2, sort_keys=True))
    return exit_code(result)


if __name__ == "__main__":
    raise SystemExit(main())
