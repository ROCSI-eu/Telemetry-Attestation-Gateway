#!/usr/bin/env python3
"""Generate minimized synthetic service-boundary evidence.

EXPERIMENTAL
SYNTHETIC_ONLY
A0_SYNTHETIC
NOT VALIDATION OR PRODUCTION AUTHORIZATION
"""

from __future__ import annotations

import json
from pathlib import Path
import socket
import tempfile
from typing import Any

import mock_gateway as gateway


def valid_result() -> dict[str, Any]:
    return {
        "invocation": {"status": "ACCEPTED", "reason": None},
        "telemetry": {
            "status": "NORMALIZED",
            "reason": None,
            "assurance_id": "A0_SYNTHETIC",
            "source_trust": "UNSIGNED",
            "speed_cm_s": 424242,
            "raw_frame": "restricted-frame",
        },
        "predicate": "SATISFIED",
        "proof_generation": "GENERATED",
        "verification_input": {"status": "ACCEPTED", "reason": None},
        "cryptographic": {"status": "VALID", "reason": None},
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
        "proof": "restricted-proof-bytes",
        "witness": {"private_speed": 424242},
    }


def malformed_result() -> dict[str, Any]:
    value = valid_result()
    value["telemetry"] = {
        "status": "REJECTED",
        "reason": "MALFORMED_FRAME",
        "assurance_id": "A0_SYNTHETIC",
        "source_trust": "NOT_EVALUATED",
    }
    value["predicate"] = "NOT_EVALUATED"
    value["proof_generation"] = "NOT_ATTEMPTED"
    value["verification_input"] = {"status": "NOT_CHECKED", "reason": None}
    value["cryptographic"] = {"status": "NOT_CHECKED", "reason": None}
    return value


def invalid_result() -> dict[str, Any]:
    value = valid_result()
    value["cryptographic"] = {"status": "INVALID", "reason": "PROOF_INVALID"}
    return value


class CountingRunner:
    def __init__(self, result: dict[str, Any] | None = None) -> None:
        self.calls = 0
        self.result = result if result is not None else valid_result()
        self.package_paths: list[Path] = []

    def __call__(self, capture_name: str, maximum_speed_cm_s: int, package_dir: Path):
        self.calls += 1
        self.package_paths.append(package_dir)
        (package_dir / "proof").write_text("restricted-proof-bytes", encoding="utf-8")
        (package_dir / "witness").write_text("restricted-witness", encoding="utf-8")
        return self.result


class FlakyRunner:
    def __init__(self, failures: int, stage: str) -> None:
        self.failures = failures
        self.stage = stage
        self.calls = 0
        self.package_paths: list[Path] = []

    def __call__(self, capture_name: str, maximum_speed_cm_s: int, package_dir: Path):
        self.calls += 1
        self.package_paths.append(package_dir)
        (package_dir / "transient-proof").write_text("restricted", encoding="utf-8")
        if self.calls <= self.failures:
            code = "PROVER_UNAVAILABLE" if self.stage == "PROVING" else "VERIFIER_UNAVAILABLE"
            raise gateway.RetryableStageError(self.stage, code)
        return valid_result()


class InterruptingRunner:
    def __init__(self) -> None:
        self.calls = 0
        self.package_paths: list[Path] = []

    def __call__(self, capture_name: str, maximum_speed_cm_s: int, package_dir: Path):
        self.calls += 1
        self.package_paths.append(package_dir)
        (package_dir / "partial-proof").write_text("restricted", encoding="utf-8")
        raise RuntimeError("simulated interruption")


def run_case(runner, key: str, *, max_attempts: int = 3, malformed: bool = False):
    temporary = tempfile.TemporaryDirectory()
    root = Path(temporary.name)
    service = gateway.MockGateway(
        root / "state.json", runner=runner, max_attempts=max_attempts
    )
    result = service.submit(
        idempotency_key=key,
        capture_name="malformed" if malformed else "unsigned-consistent",
        maximum_speed_cm_s=600,
    )
    return temporary, root, service, result


def assert_no_restricted_output(text: str) -> None:
    for token in (
        "restricted-proof-bytes",
        "restricted-witness",
        "restricted-frame",
        '"speed_cm_s": 424242',
        '"private_speed"',
        '"raw_frame"',
        '"proof":',
        '"witness":',
        '"capture_name":',
        '"idempotency_key":',
    ):
        if token in text:
            raise AssertionError(f"restricted token escaped minimization: {token}")


def main() -> int:
    package_paths: list[Path] = []
    persisted_texts: list[str] = []
    public_results: list[dict[str, Any]] = []

    original_connect = socket.socket.connect
    original_create_connection = socket.create_connection

    def denied(*args, **kwargs):
        raise AssertionError("external network access attempted")

    socket.socket.connect = denied
    socket.create_connection = denied
    temporaries: list[tempfile.TemporaryDirectory] = []
    try:
        duplicate_runner = CountingRunner()
        tmp1, root1, duplicate_service, duplicate_first = run_case(
            duplicate_runner, "duplicate-private-key"
        )
        temporaries.append(tmp1)
        duplicate_second = duplicate_service.submit(
            idempotency_key="duplicate-private-key",
            capture_name="unsigned-consistent",
            maximum_speed_cm_s=600,
        )
        package_paths += duplicate_runner.package_paths
        persisted_texts.append((root1 / "state.json").read_text(encoding="utf-8"))
        public_results += [duplicate_first, duplicate_second]

        conflict = duplicate_service.submit(
            idempotency_key="duplicate-private-key",
            capture_name="unsigned-consistent",
            maximum_speed_cm_s=601,
        )
        public_results.append(conflict)

        retry_runner = FlakyRunner(2, "PROVING")
        tmp2, root2, _, retry_result = run_case(
            retry_runner, "retry-private-key", max_attempts=3
        )
        temporaries.append(tmp2)
        package_paths += retry_runner.package_paths
        persisted_texts.append((root2 / "state.json").read_text(encoding="utf-8"))
        public_results.append(retry_result)

        verifier_runner = FlakyRunner(9, "VERIFYING")
        tmp3, root3, _, verifier_result = run_case(
            verifier_runner, "verifier-private-key", max_attempts=2
        )
        temporaries.append(tmp3)
        package_paths += verifier_runner.package_paths
        persisted_texts.append((root3 / "state.json").read_text(encoding="utf-8"))
        public_results.append(verifier_result)

        invalid_runner = CountingRunner(invalid_result())
        tmp4, root4, _, invalid = run_case(invalid_runner, "invalid-private-key")
        temporaries.append(tmp4)
        package_paths += invalid_runner.package_paths
        persisted_texts.append((root4 / "state.json").read_text(encoding="utf-8"))
        public_results.append(invalid)

        malformed_runner = CountingRunner(malformed_result())
        tmp5, root5, _, malformed = run_case(
            malformed_runner, "malformed-private-key", malformed=True
        )
        temporaries.append(tmp5)
        package_paths += malformed_runner.package_paths
        persisted_texts.append((root5 / "state.json").read_text(encoding="utf-8"))
        public_results.append(malformed)

        restart_tmp = tempfile.TemporaryDirectory()
        temporaries.append(restart_tmp)
        restart_root = Path(restart_tmp.name)
        first_restart_runner = InterruptingRunner()
        before = gateway.MockGateway(
            restart_root / "state.json", runner=first_restart_runner, max_attempts=3
        )
        try:
            before.submit(
                idempotency_key="restart-private-key",
                capture_name="unsigned-consistent",
                maximum_speed_cm_s=600,
            )
        except RuntimeError:
            pass
        else:
            raise AssertionError("restart interruption was not exercised")
        mid_state = json.loads((restart_root / "state.json").read_text(encoding="utf-8"))
        mid_record = next(iter(mid_state["records"].values()))
        second_restart_runner = CountingRunner()
        after = gateway.MockGateway(
            restart_root / "state.json", runner=second_restart_runner, max_attempts=3
        )
        restart_result = after.submit(
            idempotency_key="restart-private-key",
            capture_name="unsigned-consistent",
            maximum_speed_cm_s=600,
        )
        package_paths += first_restart_runner.package_paths
        package_paths += second_restart_runner.package_paths
        persisted_texts.append((restart_root / "state.json").read_text(encoding="utf-8"))
        public_results.append(restart_result)

        all_public_text = json.dumps(public_results, sort_keys=True)
        assert_no_restricted_output(all_public_text)
        for text in persisted_texts:
            assert_no_restricted_output(text)
        for private_key in (
            "duplicate-private-key",
            "retry-private-key",
            "verifier-private-key",
            "invalid-private-key",
            "malformed-private-key",
            "restart-private-key",
        ):
            if private_key in all_public_text or any(private_key in text for text in persisted_texts):
                raise AssertionError("raw idempotency key escaped minimization")

        if not all(not path.exists() for path in package_paths):
            raise AssertionError("temporary proof package was not disposed")

        evidence = {
            "labels": list(gateway.LABELS),
            "experiment": "mock-gateway-v0",
            "evidence_scope": "deterministic synthetic service-boundary behavior with controlled fault injection",
            "genuine_integration": {
                "runner": "experiments/end-to-end-v0/demo.py",
                "status": "AVAILABLE_WHEN_PINNED_PROOF_TOOLING_IS_PRESENT",
                "checked_in_service_evidence_reproved": False,
                "upstream_genuine_proof_evidence": "experiments/end-to-end-v0/evidence-results.json",
            },
            "cases": {
                "duplicate_submission": {
                    "state": duplicate_second["state"],
                    "runner_calls": duplicate_runner.calls,
                    "idempotent_replay": duplicate_second["idempotent_replay"],
                },
                "idempotency_conflict": {
                    "state": conflict["state"],
                    "reason": conflict["reason"],
                },
                "bounded_retry_recovery": {
                    "state": retry_result["state"],
                    "attempt_count": retry_result["attempt_count"],
                    "lifecycle": retry_result["lifecycle"],
                },
                "verifier_unavailable": {
                    "state": verifier_result["state"],
                    "attempt_count": verifier_result["attempt_count"],
                    "cryptographic": verifier_result["result"]["cryptographic"]["status"],
                    "reason": verifier_result["reason"],
                },
                "cryptographic_invalid": {
                    "state": invalid["state"],
                    "cryptographic": invalid["result"]["cryptographic"]["status"],
                    "reason": invalid["reason"],
                },
                "malformed_input": {
                    "state": malformed["state"],
                    "proof_generation": malformed["result"]["proof_generation"],
                    "reason": malformed["reason"],
                },
                "restart": {
                    "state_before_restart": mid_record["state"],
                    "lifecycle_before_restart": mid_record["lifecycle"],
                    "state_after_restart": restart_result["state"],
                    "lifecycle_after_restart": restart_result["lifecycle"],
                    "attempt_count_after_restart": restart_result["attempt_count"],
                    "attempt_outcomes_after_restart": [
                        event["outcome"] for event in restart_result["attempts"]
                    ],
                },
            },
            "checks": {
                "python_network_denied": "PASS",
                "restricted_field_absence": "PASS",
                "raw_idempotency_key_absence": "PASS",
                "proof_package_disposal": "PASS",
                "lifecycle_monotonicity": "PASS",
                "publication_not_performed": "PASS",
                "verifier_unavailable_distinct_from_invalid": "PASS",
            },
            "limitations": [
                "Synthetic local evidence only.",
                "Controlled service-failure cases do not re-run the genuine proof toolchain.",
                "The genuine integration runner delegates to the existing end-to-end-v0 experiment when pinned Noir/Barretenberg tooling is present.",
                "Python network calls are denied in this evidence runner; subprocess-level isolation remains a separate execution-environment control for genuine proof measurements.",
                "No workflow, market, safety, compliance, hardware, pilot, deployment, production, or higher-assurance claim is established.",
            ],
        }

        if verifier_result["result"]["cryptographic"]["status"] == invalid["result"]["cryptographic"]["status"]:
            raise AssertionError("unavailable verifier collapsed into cryptographic invalidity")
        if malformed["result"]["proof_generation"] != "NOT_ATTEMPTED":
            raise AssertionError("malformed input reached proof generation")
        if duplicate_runner.calls != 1:
            raise AssertionError("duplicate submission reran the work")
        if mid_record["state"] != "PROVING" or restart_result["state"] != "VERIFIED":
            raise AssertionError("restart lifecycle evidence did not match expectation")
        if restart_result["attempt_count"] != 2:
            raise AssertionError("interrupted attempt was not retained across restart")
        if [event["outcome"] for event in restart_result["attempts"]] != [
            "STARTED",
            "INTERRUPTED",
            "STARTED",
            "COMPLETED",
        ]:
            raise AssertionError("restart attempt history was not append-only/auditable")
        for result in public_results:
            typed = result.get("result")
            if isinstance(typed, dict) and typed.get("publication") not in {
                None,
                "NOT_PERFORMED",
            }:
                raise AssertionError("publication changed during local gateway evidence")

        print(json.dumps(evidence, indent=2, sort_keys=True))
    finally:
        socket.socket.connect = original_connect
        socket.create_connection = original_create_connection
        for temporary in temporaries:
            temporary.cleanup()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
