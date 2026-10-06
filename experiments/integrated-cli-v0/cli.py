#!/usr/bin/env python3
"""Run the integrated synthetic Telemetry Attestation Gateway CLI prototype.

EXPERIMENTAL
SYNTHETIC_ONLY
A0_SYNTHETIC
NOT VALIDATION OR PRODUCTION AUTHORIZATION
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile
from typing import Any

EXPERIMENTS_ROOT = Path(__file__).resolve().parents[1]
MAVLINK_DIR = EXPERIMENTS_ROOT / "mavlink-normalization-v0"
E2E_DIR = EXPERIMENTS_ROOT / "end-to-end-v0"
PUBLICATION_DIR = EXPERIMENTS_ROOT / "publication-adapter-v0"

for module_dir in (PUBLICATION_DIR, E2E_DIR, MAVLINK_DIR):
    module_path = str(module_dir)
    if module_path not in sys.path:
        sys.path.insert(0, module_path)

import demo  # noqa: E402
import publication_adapter as publication  # noqa: E402

LABELS = demo.LABELS
SCHEMA_VERSION = "TAG_INTEGRATED_CLI_RESULT_V0_EXPERIMENTAL"
PUBLICATION_DIGEST_DOMAIN = b"TAG_INTEGRATED_CLI_PUBLICATION_V0\x00"
IDEMPOTENCY_DOMAIN = b"TAG_INTEGRATED_CLI_IDEMPOTENCY_V0\x00"
UINT32_MAX = (1 << 32) - 1
VERIFICATION_CASES = (
    "normal",
    "tampered-proof",
    "altered-public-input",
    "unsupported-version",
)
PUBLICATION_FAULTS = (
    "timeout",
    "cancelled",
    "unavailable",
    "definitive_failure",
)


def _not_attempted_publication(mode: str, reason: str) -> dict[str, Any]:
    return {
        "mode": mode,
        "status": "NOT_ATTEMPTED",
        "state": "NOT_PERFORMED",
        "attempts": 0,
        "reconciled": False,
        "record_id": None,
        "receipt_state": "NOT_ISSUED",
        "error": {"code": reason, "classification": "not_attempted", "retryable": False},
    }


def _publication_digest(package_dir: Path) -> str:
    digest = hashlib.sha256(PUBLICATION_DIGEST_DOMAIN)
    for name in ("public-artifact.cbor", "proof", "vk"):
        data = (package_dir / name).read_bytes()
        digest.update(name.encode("utf-8"))
        digest.update(b"\x00")
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
    return digest.hexdigest()


def _idempotency_key(payload_digest: str) -> str:
    digest = hashlib.sha256(
        IDEMPOTENCY_DOMAIN + payload_digest.encode("ascii")
    ).hexdigest()
    return "idk_" + digest[:32]


def _publication_request(
    payload_digest: str, capture_name: str
) -> publication.PublicationRequest:
    fixture_tag = hashlib.sha256(capture_name.encode("utf-8")).hexdigest()[:16]
    return publication.PublicationRequest(
        idempotency_key=_idempotency_key(payload_digest),
        payload_digest=payload_digest,
        metadata={
            "fixture": f"synthetic-fixture-{fixture_tag}",
            "scenario": "synthetic-integrated-cli-v0",
        },
    )


def _summarize_publication(
    mode: str,
    record: dict[str, Any],
    *,
    attempts: int,
    reconciled: bool,
) -> dict[str, Any]:
    state = record.get("state", "unknown")
    return {
        "mode": mode,
        "status": str(state).upper(),
        "state": state,
        "attempts": attempts,
        "reconciled": reconciled,
        "record_id": record.get("record_id"),
        "receipt_state": record.get("receipt_state", "NOT_ISSUED"),
        "error": record.get("error"),
    }


def _publish(
    package_dir: Path,
    capture_name: str,
    mode: str,
    state_path: Path | None,
    fault_once: str | None,
) -> dict[str, Any]:
    payload_digest = _publication_digest(package_dir)
    request = _publication_request(payload_digest, capture_name)

    if mode == "disabled":
        adapter: publication.ProvisionalPublicationAdapter = publication.DisabledAdapter()
    elif mode == "local":
        if state_path is None:
            raise ValueError("local publication requires a state path")
        adapter = publication.DeterministicLocalAdapter(state_path, fault_once=fault_once)
    else:
        raise ValueError("unsupported publication mode")

    attempts = 0
    reconciled = False
    try:
        record = adapter.submit(request)
        attempts += 1
        error = record.get("error")
        if (
            mode == "local"
            and record.get("state") == "pending"
            and isinstance(error, dict)
            and error.get("retryable") is True
        ):
            record = adapter.submit(request)
            attempts += 1

        record_id = record.get("record_id")
        if isinstance(record_id, str):
            record = adapter.status(record_id)
            reconciled = True
        return _summarize_publication(
            mode, record, attempts=attempts, reconciled=reconciled
        )
    except publication.PublicationAdapterError as exc:
        public_error = exc.public()["error"]
        return {
            "mode": mode,
            "status": "ERROR",
            "state": "NOT_RECORDED",
            "attempts": attempts + 1,
            "reconciled": False,
            "record_id": None,
            "receipt_state": "NOT_ISSUED",
            "error": public_error,
        }


def _apply_verification_case(
    package_dir: Path,
    maximum_speed_cm_s: int,
    verification_case: str,
) -> dict[str, Any] | None:
    if verification_case == "normal":
        return None

    public_artifact = package_dir / "public-artifact.cbor"
    proof = package_dir / "proof"
    verification_key = package_dir / "vk"

    if verification_case == "tampered-proof":
        tampered_proof = package_dir / "proof.tampered"
        proof_bytes = bytearray(proof.read_bytes())
        if not proof_bytes:
            raise OSError("proof output is empty")
        proof_bytes[len(proof_bytes) // 2] ^= 0x01
        tampered_proof.write_bytes(proof_bytes)
        return demo.proof_verifier.verify_public_package(
            public_artifact, tampered_proof, verification_key
        )

    bounded = demo.proof_prover.BOUNDED
    altered_public = package_dir / "public-artifact.scenario.cbor"
    if verification_case == "altered-public-input":
        altered_limit = (
            0 if maximum_speed_cm_s == UINT32_MAX else maximum_speed_cm_s + 1
        )
        altered_public.write_bytes(bounded.encode_public_artifact(altered_limit))
    elif verification_case == "unsupported-version":
        altered_public.write_bytes(
            bounded._encode_value(
                {
                    1: bounded.SCHEMA_VERSION + 1,
                    2: bounded.DOMAIN,
                    3: maximum_speed_cm_s,
                    4: bounded.STATEMENT,
                    5: bounded.ASSURANCE_ID,
                }
            )
        )
    else:
        raise ValueError("unsupported verification case")
    return demo.proof_verifier.verify_public_package(
        altered_public, proof, verification_key
    )


def _apply_verification_result(
    demo_result: dict[str, Any], verification: dict[str, Any]
) -> None:
    demo_result["verification_input"] = verification.get(
        "input", {"status": "NOT_CHECKED", "reason": None}
    )
    demo_result["cryptographic"] = verification.get(
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
            demo_result[dimension] = verification[dimension]


def _result_from_demo(
    capture_name: str,
    maximum_speed_cm_s: int,
    verification_case: str,
    demo_result: dict[str, Any],
    publication_result: dict[str, Any],
) -> dict[str, Any]:
    telemetry = demo_result["telemetry"]
    assurance = demo_result["assurance"]
    return {
        "labels": list(LABELS),
        "schema_version": SCHEMA_VERSION,
        "experiment": "integrated-cli-v0",
        "capture_case": capture_name,
        "source": {
            "normalization": telemetry["status"],
            "reason": telemetry.get("reason"),
            "assurance_id": telemetry.get("assurance_id", "A0_SYNTHETIC"),
            "source_trust": telemetry.get("source_trust", "NOT_EVALUATED"),
        },
        "claim": {
            "predicate": "speed_cm_s <= maximum_speed_cm_s",
            "maximum_speed_cm_s": maximum_speed_cm_s,
            "status": demo_result["predicate"],
            "private_observation_disclosed": False,
        },
        "proof": {
            "generation": demo_result["proof_generation"],
            "verification_case": verification_case,
            "verification_input": demo_result["verification_input"],
            "cryptographic": demo_result["cryptographic"],
        },
        "verification_dimensions": {
            "policy": demo_result["policy"],
            "freshness": demo_result["freshness"],
            "revocation": demo_result["revocation"],
            "replay": demo_result["replay"],
            "assurance": assurance,
        },
        "publication": publication_result,
        "disclosure": {
            "raw_telemetry": False,
            "exact_normalized_speed": False,
            "private_witness": False,
            "proof_secrets": False,
            "stable_identity": False,
        },
        "relying_party_decision": demo_result["relying_party_decision"],
        "proof_validity_is_telemetry_truth": demo_result[
            "proof_validity_is_telemetry_truth"
        ],
        "command_path": "NONE",
    }


def _demo_error_result(capture_name: str, error: demo.DemoError) -> dict[str, Any]:
    result = demo._base_result(capture_name)
    if error.code == "INVALID_PUBLIC_LIMIT":
        result["invocation"] = {"status": "REJECTED", "reason": error.code}
    else:
        result["telemetry"] = {
            "status": "REJECTED",
            "reason": error.code,
            "assurance_id": "A0_SYNTHETIC",
            "source_trust": "NOT_EVALUATED",
        }
    return result


def _run_in_workspace(
    capture_file: Path,
    capture_name: str,
    maximum_speed_cm_s: int,
    publication_mode: str,
    publication_state: Path | None,
    publication_fault: str | None,
    verification_case: str,
    package_dir: Path,
) -> dict[str, Any]:
    try:
        demo_result = demo.run_fixture(
            capture_file,
            capture_name,
            maximum_speed_cm_s,
            package_dir=package_dir,
        )
    except demo.DemoError as exc:
        demo_result = _demo_error_result(capture_name, exc)

    if (
        demo_result["proof_generation"] == "GENERATED"
        and demo_result["cryptographic"]["status"] == "VALID"
        and verification_case != "normal"
    ):
        try:
            verification = _apply_verification_case(
                package_dir, maximum_speed_cm_s, verification_case
            )
        except OSError:
            verification = {
                "input": {"status": "NOT_CHECKED", "reason": None},
                "cryptographic": {
                    "status": "UNVERIFIABLE",
                    "reason": "SCENARIO_WORKSPACE_FAILURE",
                },
            }
        if verification is not None:
            _apply_verification_result(demo_result, verification)

    cryptographic = demo_result["cryptographic"]["status"]
    if demo_result["telemetry"]["status"] != "NORMALIZED":
        publication_result = _not_attempted_publication(
            publication_mode, "SOURCE_NOT_ELIGIBLE"
        )
    elif demo_result["predicate"] != "SATISFIED":
        publication_result = _not_attempted_publication(
            publication_mode, "CLAIM_NOT_ELIGIBLE"
        )
    elif cryptographic != "VALID":
        publication_result = _not_attempted_publication(
            publication_mode, "VERIFICATION_NOT_VALID"
        )
    else:
        if publication_mode == "local" and publication_state is None:
            publication_state = package_dir.parent / "publication-state.json"
        try:
            publication_result = _publish(
                package_dir,
                capture_name,
                publication_mode,
                publication_state,
                publication_fault,
            )
        except (OSError, ValueError):
            publication_result = {
                "mode": publication_mode,
                "status": "ERROR",
                "state": "NOT_RECORDED",
                "attempts": 0,
                "reconciled": False,
                "record_id": None,
                "receipt_state": "NOT_ISSUED",
                "error": {
                    "code": "PUBLICATION_WORKSPACE_FAILURE",
                    "classification": "retryable",
                    "retryable": True,
                },
            }

    return _result_from_demo(
        capture_name,
        maximum_speed_cm_s,
        verification_case,
        demo_result,
        publication_result,
    )


def run_integrated(
    capture_file: Path,
    capture_name: str,
    maximum_speed_cm_s: int,
    *,
    publication_mode: str = "disabled",
    publication_state: Path | None = None,
    publication_fault: str | None = None,
    verification_case: str = "normal",
    package_dir: Path | None = None,
) -> dict[str, Any]:
    """Run one minimized integrated synthetic flow and return redacted typed state."""
    if publication_mode not in {"disabled", "local"}:
        raise ValueError("unsupported publication mode")
    if publication_fault is not None and publication_mode != "local":
        raise ValueError("publication faults require local publication mode")
    if publication_fault not in {None, *PUBLICATION_FAULTS}:
        raise ValueError("unsupported publication fault")
    if verification_case not in VERIFICATION_CASES:
        raise ValueError("unsupported verification case")

    if package_dir is not None:
        return _run_in_workspace(
            capture_file,
            capture_name,
            maximum_speed_cm_s,
            publication_mode,
            publication_state,
            publication_fault,
            verification_case,
            package_dir,
        )

    with tempfile.TemporaryDirectory(prefix="tag-integrated-cli-") as temporary:
        workspace = Path(temporary)
        return _run_in_workspace(
            capture_file,
            capture_name,
            maximum_speed_cm_s,
            publication_mode,
            publication_state or (workspace / "publication-state.json"),
            publication_fault,
            verification_case,
            workspace / "proof-package",
        )


def render_human(result: dict[str, Any]) -> str:
    source = result["source"]
    claim = result["claim"]
    proof = result["proof"]
    dims = result["verification_dimensions"]
    publication_result = result["publication"]
    disclosure = result["disclosure"]

    source_reason = f" ({source['reason']})" if source.get("reason") else ""
    crypto_reason = (
        f" ({proof['cryptographic'].get('reason')})"
        if proof["cryptographic"].get("reason")
        else ""
    )
    publication_error = publication_result.get("error")
    publication_suffix = ""
    if isinstance(publication_error, dict) and publication_error.get("code"):
        publication_suffix = f" ({publication_error['code']})"

    return "\n".join(
        [
            " · ".join(result["labels"]),
            f"Synthetic capture: {result['capture_case']}",
            f"Source normalization: {source['normalization']}{source_reason}",
            f"Source trust: {source['source_trust']} / assurance {source['assurance_id']}",
            (
                "Bounded claim: private normalized speed <= "
                f"{claim['maximum_speed_cm_s']} cm/s -> {claim['status']}"
            ),
            f"Proof generation: {proof['generation']}",
            f"Verification input: {proof['verification_input']['status']}",
            (
                "Cryptographic verification: "
                f"{proof['cryptographic']['status']}{crypto_reason}"
            ),
            (
                "Other verifier dimensions: "
                f"policy={dims['policy']}, freshness={dims['freshness']}, "
                f"revocation={dims['revocation']}, replay={dims['replay']}, "
                f"assurance={dims['assurance']['effective']}"
            ),
            (
                "Publication: "
                f"{publication_result['status']}{publication_suffix}; "
                f"reconciled={str(publication_result['reconciled']).lower()}"
            ),
            (
                "Restricted fields disclosed: "
                + (
                    "yes"
                    if any(disclosure.values())
                    else "no (raw telemetry, exact normalized speed, witness/proof secrets, stable identity)"
                )
            ),
            f"Relying-party business decision: {result['relying_party_decision']}",
            f"MAVLink command path: {result['command_path']}",
            (
                "Proof validity is telemetry truth: "
                + ("yes" if result["proof_validity_is_telemetry_truth"] else "no")
            ),
        ]
    )


def exit_code(result: dict[str, Any]) -> int:
    if result["source"]["normalization"] != "NORMALIZED":
        return 2
    if result["claim"]["status"] == "NOT_SATISFIED":
        return 3
    verification_input = result["proof"]["verification_input"]["status"]
    cryptographic = result["proof"]["cryptographic"]["status"]
    if verification_input == "REJECTED":
        return 6
    if cryptographic == "INVALID":
        return 4
    if cryptographic != "VALID":
        return 5
    publication_result = result["publication"]
    if (
        publication_result["mode"] == "local"
        and publication_result["state"] != "final"
    ):
        return 7
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--capture-file",
        type=Path,
        default=MAVLINK_DIR / "fixtures.json",
        help="checked-in deterministic synthetic capture fixture file",
    )
    parser.add_argument(
        "--capture-name",
        default="unsigned-consistent",
        help="named synthetic capture from the fixture file",
    )
    parser.add_argument(
        "--maximum-speed-cm-s",
        type=int,
        required=True,
        help="public synthetic bounded-speed maximum",
    )
    parser.add_argument(
        "--format",
        choices=("human", "json"),
        default="human",
        help="human explanation or stable machine-readable experimental JSON",
    )
    parser.add_argument(
        "--publication",
        choices=("disabled", "local"),
        default="disabled",
        help="disabled adapter or disposable deterministic local adapter",
    )
    parser.add_argument(
        "--publication-state",
        type=Path,
        help="optional disposable local adapter state path for cross-run reconciliation",
    )
    parser.add_argument(
        "--publication-fault",
        choices=PUBLICATION_FAULTS,
        help="synthetic one-shot local publication fault",
    )
    parser.add_argument(
        "--verification-case",
        choices=VERIFICATION_CASES,
        default="normal",
        help="synthetic verification scenario applied after a valid proof is generated",
    )
    args = parser.parse_args()

    if args.publication_state is not None and args.publication != "local":
        parser.error("--publication-state requires --publication local")
    if args.publication_fault is not None and args.publication != "local":
        parser.error("--publication-fault requires --publication local")

    result = run_integrated(
        args.capture_file,
        args.capture_name,
        args.maximum_speed_cm_s,
        publication_mode=args.publication,
        publication_state=args.publication_state,
        publication_fault=args.publication_fault,
        verification_case=args.verification_case,
    )
    if args.format == "json":
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(render_human(result))
    return exit_code(result)


if __name__ == "__main__":
    raise SystemExit(main())
