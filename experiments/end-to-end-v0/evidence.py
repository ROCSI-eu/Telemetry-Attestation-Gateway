#!/usr/bin/env python3
"""Capture minimized genuine end-to-end synthetic evidence.

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

import demo

FIXTURES = demo.MAVLINK_DIR / "fixtures.json"
BOUNDED = demo.proof_prover.BOUNDED


def _verification_summary(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "telemetry": result["telemetry"]["status"],
        "source_trust": result["telemetry"]["source_trust"],
        "predicate": result["predicate"],
        "proof_generation": result["proof_generation"],
        "verification_input": result["verification_input"]["status"],
        "cryptographic": result["cryptographic"]["status"],
        "assurance": result["assurance"]["effective"],
        "publication": result["publication"],
        "relying_party_decision": result["relying_party_decision"],
    }


def _safe_failure_details(result: dict[str, Any]) -> str:
    return json.dumps(
        {
            "summary": _verification_summary(result),
            "verification_input_reason": result["verification_input"].get("reason"),
            "cryptographic_reason": result["cryptographic"].get("reason"),
        },
        sort_keys=True,
    )


def capture_evidence(output: Path) -> dict[str, Any]:
    accepted_capture = demo.load_capture(FIXTURES, "unsigned-consistent")
    bad_crc_capture = demo.load_capture(FIXTURES, "bad-crc")

    with tempfile.TemporaryDirectory(prefix="tag-e2e-evidence-") as temporary:
        work = Path(temporary)
        below_package = work / "below"
        equal_package = work / "equal"
        above_package = work / "above"
        bad_package = work / "bad"

        below = demo.run_capture(
            "unsigned-consistent", accepted_capture, 600, below_package
        )
        equal = demo.run_capture(
            "unsigned-consistent", accepted_capture, 500, equal_package
        )
        above = demo.run_capture(
            "unsigned-consistent", accepted_capture, 499, above_package
        )
        malformed_telemetry = demo.run_capture(
            "bad-crc", bad_crc_capture, 600, bad_package
        )

        if below["cryptographic"]["status"] != "VALID":
            raise RuntimeError(
                "below-limit end-to-end case did not verify: "
                + _safe_failure_details(below)
            )
        if equal["cryptographic"]["status"] != "VALID":
            raise RuntimeError(
                "equality-boundary end-to-end case did not verify: "
                + _safe_failure_details(equal)
            )
        if above["predicate"] != "NOT_SATISFIED":
            raise RuntimeError("over-limit observation did not stop before proving")
        if malformed_telemetry["telemetry"]["status"] != "REJECTED":
            raise RuntimeError("malformed telemetry did not fail before proving")

        tampered_proof = work / "proof.tampered"
        proof_bytes = bytearray((below_package / "proof").read_bytes())
        if not proof_bytes:
            raise RuntimeError("proof output is empty")
        proof_bytes[len(proof_bytes) // 2] ^= 0x01
        tampered_proof.write_bytes(proof_bytes)
        tampered = demo.proof_verifier.verify_public_package(
            below_package / "public-artifact.cbor",
            tampered_proof,
            below_package / "vk",
        )
        if tampered["cryptographic"]["status"] != "INVALID":
            raise RuntimeError("tampered proof was not cryptographically rejected")

        altered_public = work / "public-artifact.altered.cbor"
        altered_public.write_bytes(BOUNDED.encode_public_artifact(601))
        altered = demo.proof_verifier.verify_public_package(
            altered_public,
            below_package / "proof",
            below_package / "vk",
        )
        if altered["cryptographic"]["status"] != "INVALID":
            raise RuntimeError("altered canonical public input was not rejected")

        incompatible_public = work / "public-artifact.incompatible.cbor"
        incompatible_public.write_bytes(
            BOUNDED._encode_value(
                {
                    1: BOUNDED.SCHEMA_VERSION + 1,
                    2: BOUNDED.DOMAIN,
                    3: 600,
                    4: BOUNDED.STATEMENT,
                    5: BOUNDED.ASSURANCE_ID,
                }
            )
        )
        incompatible = demo.proof_verifier.verify_public_package(
            incompatible_public,
            below_package / "proof",
            below_package / "vk",
        )
        if (
            incompatible["input"]["status"] != "REJECTED"
            or incompatible["cryptographic"]["status"] != "NOT_CHECKED"
        ):
            raise RuntimeError("incompatible public version did not fail closed")

        forbidden = {"Prover.toml", "bounded_speed_proof_v0.gz"}
        for package in (below_package, equal_package):
            package_files = {
                path.name for path in package.rglob("*") if path.is_file()
            }
            if package_files & forbidden:
                raise RuntimeError("private witness material escaped prover workspace")
            manifest = json.loads(
                (package / "manifest.json").read_text(encoding="utf-8")
            )
            if manifest.get("private_witness_disclosed") is not False:
                raise RuntimeError("proof package does not preserve witness privacy")
            if manifest.get("proof_mode") != "zero_knowledge":
                raise RuntimeError("proof package is not marked zero-knowledge")
            if manifest.get("verifier_target") != demo.proof_prover.VERIFIER_TARGET:
                raise RuntimeError("proof package does not pin the expected verifier target")

        minimized = {
            "labels": list(demo.LABELS),
            "experiment": "end-to-end-v0",
            "path": (
                "synthetic MAVLink observation -> allowlisted normalization -> "
                "private bounded-speed witness -> zero-knowledge proof -> "
                "independent offline verification"
            ),
            "cases": {
                "below_limit": _verification_summary(below),
                "equality_boundary": _verification_summary(equal),
                "over_limit": _verification_summary(above),
                "malformed_telemetry": _verification_summary(malformed_telemetry),
                "tampered_proof": {
                    "verification_input": tampered["input"]["status"],
                    "cryptographic": tampered["cryptographic"]["status"],
                },
                "altered_public_input": {
                    "verification_input": altered["input"]["status"],
                    "cryptographic": altered["cryptographic"]["status"],
                },
                "incompatible_public_version": {
                    "verification_input": incompatible["input"]["status"],
                    "cryptographic": incompatible["cryptographic"]["status"],
                },
            },
            "proof_evidence": {
                "proof_mode": "zero_knowledge",
                "verifier_target": demo.proof_prover.VERIFIER_TARGET,
                "proof_size_bytes": (below_package / "proof").stat().st_size,
                "private_witness_disclosed": False,
                "verifier_accepts_witness_input": False,
            },
            "environment": {
                "network_required_by_measured_run": False,
                "hardware": "none",
                "command_path": "none",
                "publication": "not_performed",
            },
            "non_claims": {
                "telemetry_truth": False,
                "trustworthy_time": False,
                "continuous_or_whole_flight_coverage": False,
                "safety_or_compliance": False,
                "customer_demand_or_pilot_readiness": False,
                "production_readiness": False,
            },
        }

    output.write_text(
        json.dumps(minimized, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(minimized, indent=2, sort_keys=True))
    return minimized


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("evidence-results.json"),
    )
    args = parser.parse_args()
    capture_evidence(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())