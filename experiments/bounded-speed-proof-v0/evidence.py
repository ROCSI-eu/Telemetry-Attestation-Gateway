#!/usr/bin/env python3
"""Capture genuine cryptographic evidence for bounded-speed-proof-v0.

EXPERIMENTAL
SYNTHETIC_ONLY
A0_SYNTHETIC
NOT VALIDATION OR PRODUCTION AUTHORIZATION
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile
from typing import Any

from common import BOUNDED, EXPECTED_VK_SHA256, LABELS, require_prover_tools, sha256_file
from prove import prove_package
from verify import verify_public_package


def _dimension_summary(result: dict[str, Any]) -> dict[str, Any]:
    return {"input": result["input"]["status"], "cryptographic": result["cryptographic"]["status"], "policy": result["policy"], "freshness": result["freshness"], "revocation": result["revocation"], "replay": result["replay"], "assurance_effective": result["assurance"]["effective"], "publication": result["publication"], "relying_party_decision": result["relying_party_decision"]}


def _verify_package(package: Path) -> dict[str, Any]:
    return verify_public_package(package / "public-artifact.cbor", package / "proof", package / "vk")


def capture_evidence(output: Path) -> dict[str, Any]:
    versions = require_prover_tools()
    with tempfile.TemporaryDirectory(prefix="tag-proof-evidence-") as tmp:
        work = Path(tmp)
        below, equal, over = work / "below", work / "equal", work / "over"
        below_prove = prove_package(1200, 1500, below)
        equal_prove = prove_package(1500, 1500, equal)
        if not below_prove["package_written"] or not equal_prove["package_written"]:
            raise RuntimeError("valid synthetic cases did not produce proof packages")
        below_vk_sha256 = sha256_file(below / "vk")
        equal_vk_sha256 = sha256_file(equal / "vk")
        if below_vk_sha256 != EXPECTED_VK_SHA256 or equal_vk_sha256 != EXPECTED_VK_SHA256:
            raise RuntimeError("generated verification key does not match the pinned experimental trust anchor")
        below_verify, equal_verify = _verify_package(below), _verify_package(equal)
        if below_verify["cryptographic"]["status"] != "VALID": raise RuntimeError("below-limit synthetic proof did not verify")
        if equal_verify["cryptographic"]["status"] != "VALID": raise RuntimeError("equality-boundary synthetic proof did not verify")
        over_result = prove_package(1501, 1500, over)
        if over_result["predicate"] != "NOT_SATISFIED" or over_result["package_written"]: raise RuntimeError("over-limit synthetic witness was not rejected before proving")
        if over.exists() and any(over.iterdir()): raise RuntimeError("over-limit rejection left an output package")
        tampered_proof = work / "proof.tampered"
        proof_bytes = bytearray((below / "proof").read_bytes())
        if not proof_bytes: raise RuntimeError("proof output is empty")
        proof_bytes[len(proof_bytes) // 2] ^= 0x01
        tampered_proof.write_bytes(proof_bytes)
        tampered_verify = verify_public_package(below / "public-artifact.cbor", tampered_proof, below / "vk")
        if tampered_verify["cryptographic"]["status"] != "INVALID": raise RuntimeError("mutated proof was not rejected")
        altered_public = work / "public-artifact.altered.cbor"
        altered_public.write_bytes(BOUNDED.encode_public_artifact(1501))
        altered_public_verify = verify_public_package(altered_public, below / "proof", below / "vk")
        if altered_public_verify["cryptographic"]["status"] != "INVALID": raise RuntimeError("altered canonical public material was not rejected cryptographically")
        malformed_public = work / "public-artifact.malformed.cbor"
        malformed_public.write_bytes(b"\xa0")
        malformed_verify = verify_public_package(malformed_public, below / "proof", below / "vk")
        if malformed_verify["input"]["status"] != "REJECTED" or malformed_verify["cryptographic"]["status"] != "NOT_CHECKED": raise RuntimeError("malformed public material did not fail before cryptographic verification")
        forbidden_names = {"Prover.toml", "bounded_speed_proof_v0.gz"}
        package_files = {path.name for package in (below, equal) for path in package.rglob("*") if path.is_file()}
        escaped = sorted(package_files & forbidden_names)
        if escaped: raise RuntimeError(f"private witness artifacts escaped prover workspace: {escaped}")
        def collect_keys(value: Any) -> set[str]:
            if isinstance(value, dict):
                keys = set(value)
                for item in value.values(): keys.update(collect_keys(item))
                return keys
            if isinstance(value, list):
                keys: set[str] = set()
                for item in value: keys.update(collect_keys(item))
                return keys
            return set()
        for package in (below, equal):
            manifest = json.loads((package / "manifest.json").read_text(encoding="utf-8"))
            if manifest.get("private_witness_disclosed") is not False: raise RuntimeError("proof package does not record the witness-disclosure boundary")
            if "speed_cm_s" in collect_keys(manifest): raise RuntimeError("manifest contains an unexpected private speed field")
        result = {
            "labels": list(LABELS), "experiment": "bounded-speed-proof-v0", "predicate": "speed_cm_s <= maximum_speed_cm_s",
            "tool_versions": {"nargo": versions["nargo_version"], "bb": versions["bb_version"]},
            "cases": {
                "below_limit": _dimension_summary(below_verify), "equality_boundary": _dimension_summary(equal_verify),
                "over_limit": {"input": "ACCEPTED", "predicate": "NOT_SATISFIED", "cryptographic": "NOT_ATTEMPTED", "package_written": False},
                "tampered_proof": _dimension_summary(tampered_verify), "altered_public_input": _dimension_summary(altered_public_verify), "malformed_public_artifact": _dimension_summary(malformed_verify)},
            "package_evidence": {"proof_size_bytes": (below / "proof").stat().st_size, "proof_sha256": sha256_file(below / "proof"), "verification_key_sha256": below_vk_sha256, "public_artifact_sha256": sha256_file(below / "public-artifact.cbor"), "private_witness_disclosed": False, "verifier_accepts_witness_input": False},
            "environment": {"network_required_by_experiment_scripts": False, "vendor_account": False, "hosted_verifier": False, "live_ledger": False, "production_trust_root": False, "hardware": "none", "command_path": "none"},
            "non_claims": {"proof_validity_is_telemetry_truth": False, "telemetry_assurance_equals_proof_strength": False, "verification_is_relying_party_decision": False, "publication_is_verification": False, "one_observation_is_interval_or_whole_flight": False}}
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("evidence-results.json"))
    args = parser.parse_args(); capture_evidence(args.output); return 0


if __name__ == "__main__": raise SystemExit(main())
