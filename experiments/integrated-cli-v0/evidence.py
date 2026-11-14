#!/usr/bin/env python3
"""Generate deterministic orchestration evidence for integrated CLI prototype v0."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile
from typing import Any
from unittest.mock import patch

import cli


def _valid_demo_result() -> dict[str, Any]:
    result = cli.demo._base_result("synthetic-case")
    result["invocation"] = {"status": "ACCEPTED", "reason": None}
    result["telemetry"] = {
        "status": "NORMALIZED",
        "reason": None,
        "assurance_id": "A0_SYNTHETIC",
        "source_trust": "UNSIGNED",
    }
    result["predicate"] = "SATISFIED"
    result["proof_generation"] = "GENERATED"
    result["verification_input"] = {"status": "ACCEPTED", "reason": None}
    result["cryptographic"] = {"status": "VALID", "reason": None}
    return result


def _fake_run_fixture(
    capture_file: Path,
    capture_name: str,
    maximum_speed_cm_s: int,
    package_dir: Path,
) -> dict[str, Any]:
    if capture_name == "bad-crc":
        result = cli.demo._base_result(capture_name)
        result["telemetry"] = {
            "status": "REJECTED",
            "reason": "BAD_CRC",
            "assurance_id": "A0_SYNTHETIC",
            "source_trust": "NOT_EVALUATED",
        }
        return result

    result = _valid_demo_result()
    if maximum_speed_cm_s < 500:
        result["predicate"] = "NOT_SATISFIED"
        result["proof_generation"] = "NOT_ATTEMPTED"
        result["verification_input"] = {"status": "NOT_CHECKED", "reason": None}
        result["cryptographic"] = {"status": "NOT_CHECKED", "reason": None}
        return result

    package_dir.mkdir(parents=True, exist_ok=True)
    (package_dir / "public-artifact.cbor").write_bytes(
        f"public:{maximum_speed_cm_s}".encode()
    )
    (package_dir / "proof").write_bytes(b"synthetic-proof")
    (package_dir / "vk").write_bytes(b"synthetic-vk")
    return result


def _verification(status: str, *, rejected_input: bool = False) -> dict[str, Any]:
    return {
        "input": {
            "status": "REJECTED" if rejected_input else "ACCEPTED",
            "reason": (
                "PUBLIC_ARTIFACT_MALFORMED_OR_INCOMPATIBLE"
                if rejected_input
                else None
            ),
        },
        "cryptographic": {
            "status": "NOT_CHECKED" if rejected_input else status,
            "reason": None if rejected_input or status == "VALID" else "PROOF_REJECTED",
        },
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
    }


def _summary(result: dict[str, Any]) -> dict[str, Any]:
    error = result["publication"].get("error")
    return {
        "source": result["source"]["normalization"],
        "source_trust": result["source"]["source_trust"],
        "claim": result["claim"]["status"],
        "proof_generation": result["proof"]["generation"],
        "verification_input": result["proof"]["verification_input"]["status"],
        "cryptographic": result["proof"]["cryptographic"]["status"],
        "assurance": result["verification_dimensions"]["assurance"]["effective"],
        "publication": {
            "mode": result["publication"]["mode"],
            "state": result["publication"]["state"],
            "attempts": result["publication"]["attempts"],
            "reconciled": result["publication"]["reconciled"],
            "error_code": error.get("code") if isinstance(error, dict) else None,
        },
        "relying_party_decision": result["relying_party_decision"],
        "command_path": result["command_path"],
        "restricted_fields_disclosed": any(result["disclosure"].values()),
    }


def capture_evidence(output: Path) -> dict[str, Any]:
    fixture = Path("synthetic-fixtures.json")
    with tempfile.TemporaryDirectory(prefix="tag-integrated-cli-evidence-") as temporary:
        work = Path(temporary)
        with patch.object(cli.demo, "run_fixture", side_effect=_fake_run_fixture):
            below = cli.run_integrated(
                fixture,
                "unsigned-consistent",
                600,
                publication_mode="local",
                publication_state=work / "below-state.json",
                package_dir=work / "below-package",
            )
            equal_disabled = cli.run_integrated(
                fixture,
                "unsigned-consistent",
                500,
                package_dir=work / "equal-package",
            )
            above = cli.run_integrated(
                fixture,
                "unsigned-consistent",
                499,
                publication_mode="local",
                publication_state=work / "above-state.json",
                package_dir=work / "above-package",
            )
            malformed = cli.run_integrated(
                fixture,
                "bad-crc",
                600,
                publication_mode="local",
                publication_state=work / "bad-state.json",
                package_dir=work / "bad-package",
            )
            timeout_retry = cli.run_integrated(
                fixture,
                "unsigned-consistent",
                600,
                publication_mode="local",
                publication_state=work / "timeout-state.json",
                publication_fault="timeout",
                package_dir=work / "timeout-package",
            )
            definitive_failure = cli.run_integrated(
                fixture,
                "unsigned-consistent",
                600,
                publication_mode="local",
                publication_state=work / "failure-state.json",
                publication_fault="definitive_failure",
                package_dir=work / "failure-package",
            )
            unavailable = cli.run_integrated(
                fixture,
                "unsigned-consistent",
                600,
                publication_mode="local",
                publication_state=work / "unavailable-state.json",
                publication_fault="unavailable",
                package_dir=work / "unavailable-package",
            )
            with patch.object(
                cli.demo.proof_verifier,
                "verify_public_package",
                return_value=_verification("INVALID"),
            ):
                tampered = cli.run_integrated(
                    fixture,
                    "unsigned-consistent",
                    600,
                    verification_case="tampered-proof",
                    package_dir=work / "tampered-package",
                )
                altered = cli.run_integrated(
                    fixture,
                    "unsigned-consistent",
                    600,
                    verification_case="altered-public-input",
                    package_dir=work / "altered-package",
                )
            with patch.object(
                cli.demo.proof_verifier,
                "verify_public_package",
                return_value=_verification("NOT_CHECKED", rejected_input=True),
            ):
                unsupported = cli.run_integrated(
                    fixture,
                    "unsigned-consistent",
                    600,
                    verification_case="unsupported-version",
                    package_dir=work / "unsupported-package",
                )

    evidence = {
        "labels": list(cli.LABELS),
        "experiment": "integrated-cli-v0",
        "evidence_kind": "deterministic orchestration/control-flow evidence",
        "cases": {
            "below_limit_local_publication": _summary(below),
            "equality_publication_disabled": _summary(equal_disabled),
            "over_limit": _summary(above),
            "malformed_source": _summary(malformed),
            "publication_timeout_retry_reconciliation": _summary(timeout_retry),
            "publication_definitive_failure": _summary(definitive_failure),
            "publication_unavailable": _summary(unavailable),
            "tampered_proof": _summary(tampered),
            "altered_public_input": _summary(altered),
            "unsupported_public_version": _summary(unsupported),
        },
        "boundaries": {
            "network_required": False,
            "hardware_required": False,
            "mavlink_command_path": False,
            "raw_telemetry_disclosed": False,
            "exact_normalized_speed_disclosed": False,
            "private_witness_disclosed": False,
            "stable_identity_disclosed": False,
            "relying_party_business_decision": False,
        },
        "evidence_note": (
            "This file checks deterministic integration semantics only. Genuine proof "
            "generation/verification evidence remains owned by end-to-end-v0 with its "
            "separately pinned Noir/Barretenberg/CRS provisioning."
        ),
    }
    output.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return evidence


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
