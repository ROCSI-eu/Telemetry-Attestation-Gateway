#!/usr/bin/env python3
"""Boundary tests for the synthetic mock gateway experiment."""

from __future__ import annotations

import json
from pathlib import Path
import socket
import tempfile
import unittest

import mock_gateway as gateway


def valid_result() -> dict:
    return {
        "invocation": {"status": "ACCEPTED", "reason": None, "secret": "drop-me"},
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
            "stable_identity": "restricted",
        },
        "publication": "NOT_PERFORMED",
        "relying_party_decision": "NOT_MADE",
        "proof": "restricted-proof-bytes",
        "witness": {"private_speed": 424242},
        "coordinates": [1, 2],
    }


def malformed_result() -> dict:
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


def invalid_result() -> dict:
    value = valid_result()
    value["cryptographic"] = {"status": "INVALID", "reason": "PROOF_INVALID"}
    return value


class CountingRunner:
    def __init__(self, result=None):
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
    def __init__(self, failures: int, stage: str):
        self.failures = failures
        self.stage = stage
        self.calls = 0

    def __call__(self, capture_name: str, maximum_speed_cm_s: int, package_dir: Path):
        self.calls += 1
        (package_dir / "transient-proof").write_text("restricted", encoding="utf-8")
        if self.calls <= self.failures:
            code = "PROVER_UNAVAILABLE" if self.stage == "PROVING" else "VERIFIER_UNAVAILABLE"
            raise gateway.RetryableStageError(self.stage, code)
        return valid_result()


class InterruptingRunner:
    def __init__(self):
        self.calls = 0

    def __call__(self, capture_name: str, maximum_speed_cm_s: int, package_dir: Path):
        self.calls += 1
        (package_dir / "partial-proof").write_text("restricted", encoding="utf-8")
        raise RuntimeError("simulated process interruption")


class MockGatewayTests(unittest.TestCase):
    def make_gateway(self, directory: Path, runner, max_attempts: int = 3):
        return gateway.MockGateway(
            directory / "state.json",
            runner=runner,
            max_attempts=max_attempts,
        )

    def test_duplicate_submission_is_idempotent_and_does_not_rerun(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            runner = CountingRunner()
            service = self.make_gateway(root, runner)

            first = service.submit(
                idempotency_key="duplicate-key",
                capture_name="unsigned-consistent",
                maximum_speed_cm_s=600,
            )
            second = service.submit(
                idempotency_key="duplicate-key",
                capture_name="unsigned-consistent",
                maximum_speed_cm_s=600,
            )

            self.assertEqual(first["state"], "VERIFIED")
            self.assertEqual(second["state"], "VERIFIED")
            self.assertFalse(first["idempotent_replay"])
            self.assertTrue(second["idempotent_replay"])
            self.assertEqual(runner.calls, 1)
            self.assertEqual(first["lifecycle"], ["RECEIVED", "PROVING", "PROVED", "VERIFIED"])
            self.assertTrue(first["proof_package_disposed"])
            self.assertTrue(all(not path.exists() for path in runner.package_paths))

    def test_changed_content_under_same_key_is_conflict(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            runner = CountingRunner()
            service = self.make_gateway(root, runner)
            service.submit(
                idempotency_key="conflict-key",
                capture_name="unsigned-consistent",
                maximum_speed_cm_s=600,
            )
            conflict = service.submit(
                idempotency_key="conflict-key",
                capture_name="unsigned-consistent",
                maximum_speed_cm_s=601,
            )
            self.assertEqual(conflict["state"], "ERROR")
            self.assertEqual(conflict["reason"], "IDEMPOTENCY_CONFLICT")
            self.assertEqual(runner.calls, 1)

    def test_retry_is_bounded_and_lifecycle_does_not_move_backwards(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            runner = FlakyRunner(failures=2, stage="PROVING")
            service = self.make_gateway(root, runner, max_attempts=3)
            result = service.submit(
                idempotency_key="retry-key",
                capture_name="unsigned-consistent",
                maximum_speed_cm_s=600,
            )
            self.assertEqual(result["state"], "VERIFIED")
            self.assertEqual(result["attempt_count"], 3)
            self.assertEqual(result["lifecycle"], ["RECEIVED", "PROVING", "PROVED", "VERIFIED"])
            self.assertEqual(
                [
                    event["outcome"]
                    for event in result["attempts"]
                    if event["outcome"] != "STARTED"
                ],
                ["RETRYABLE_FAILURE", "RETRYABLE_FAILURE", "COMPLETED"],
            )

    def test_retry_exhaustion_is_unverifiable_not_invalid(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            runner = FlakyRunner(failures=9, stage="VERIFYING")
            service = self.make_gateway(root, runner, max_attempts=2)
            result = service.submit(
                idempotency_key="verifier-down-key",
                capture_name="unsigned-consistent",
                maximum_speed_cm_s=600,
            )
            self.assertEqual(result["state"], "FAILED")
            self.assertEqual(result["reason"], "VERIFIER_UNAVAILABLE")
            self.assertEqual(result["result"]["cryptographic"]["status"], "UNVERIFIABLE")
            self.assertNotEqual(result["result"]["cryptographic"]["status"], "INVALID")

    def test_cryptographic_invalidity_is_distinct_from_verifier_unavailability(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            service = self.make_gateway(root, CountingRunner(invalid_result()))
            result = service.submit(
                idempotency_key="invalid-proof-key",
                capture_name="unsigned-consistent",
                maximum_speed_cm_s=600,
            )
            self.assertEqual(result["state"], "REJECTED")
            self.assertEqual(result["result"]["cryptographic"]["status"], "INVALID")
            self.assertEqual(result["reason"], "PROOF_INVALID")

    def test_malformed_input_is_rejected_before_proof_success(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            service = self.make_gateway(root, CountingRunner(malformed_result()))
            result = service.submit(
                idempotency_key="malformed-key",
                capture_name="malformed",
                maximum_speed_cm_s=600,
            )
            self.assertEqual(result["state"], "REJECTED")
            self.assertEqual(result["reason"], "MALFORMED_FRAME")
            self.assertEqual(result["result"]["proof_generation"], "NOT_ATTEMPTED")
            self.assertNotIn("PROVED", result["lifecycle"])

    def test_restart_resumes_without_backward_transition_or_duplicate_record(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first_runner = InterruptingRunner()
            service = self.make_gateway(root, first_runner)
            with self.assertRaisesRegex(RuntimeError, "simulated process interruption"):
                service.submit(
                    idempotency_key="restart-key",
                    capture_name="unsigned-consistent",
                    maximum_speed_cm_s=600,
                )

            persisted_before = json.loads((root / "state.json").read_text(encoding="utf-8"))
            only_record = next(iter(persisted_before["records"].values()))
            self.assertEqual(only_record["state"], "PROVING")
            self.assertEqual(only_record["lifecycle"], ["RECEIVED", "PROVING"])
            self.assertEqual(
                [event["outcome"] for event in only_record["attempts"]],
                ["STARTED"],
            )
            self.assertTrue(only_record["proof_package_disposed"])

            second_runner = CountingRunner()
            restarted = self.make_gateway(root, second_runner)
            result = restarted.submit(
                idempotency_key="restart-key",
                capture_name="unsigned-consistent",
                maximum_speed_cm_s=600,
            )
            self.assertEqual(result["state"], "VERIFIED")
            self.assertEqual(result["attempt_count"], 2)
            self.assertEqual(result["lifecycle"], ["RECEIVED", "PROVING", "PROVED", "VERIFIED"])
            self.assertEqual(
                [event["outcome"] for event in result["attempts"]],
                ["STARTED", "INTERRUPTED", "STARTED", "COMPLETED"],
            )
            self.assertEqual(first_runner.calls, 1)
            self.assertEqual(second_runner.calls, 1)
            persisted_after = json.loads((root / "state.json").read_text(encoding="utf-8"))
            self.assertEqual(len(persisted_after["records"]), 1)

    def test_outputs_and_persistence_exclude_restricted_values(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            raw_key = "do-not-leak-this-idempotency-key"
            service = self.make_gateway(root, CountingRunner())
            result = service.submit(
                idempotency_key=raw_key,
                capture_name="unsigned-consistent",
                maximum_speed_cm_s=600,
            )
            public_text = json.dumps(result, sort_keys=True)
            state_text = (root / "state.json").read_text(encoding="utf-8")

            for forbidden in (
                raw_key,
                "restricted-proof-bytes",
                "restricted-witness",
                "restricted-frame",
                '"speed_cm_s": 424242',
                '"private_speed"',
                '"raw_frame"',
                '"proof":',
                '"witness":',
                '"coordinates":',
                '"stable_identity":',
                '"capture_name":',
                '"idempotency_key":',
            ):
                self.assertNotIn(forbidden, public_text)
                self.assertNotIn(forbidden, state_text)

    def test_boundary_suite_succeeds_with_python_network_denied(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            runner = CountingRunner()
            service = self.make_gateway(root, runner)
            original_connect = socket.socket.connect
            original_create_connection = socket.create_connection

            def denied(*args, **kwargs):
                raise AssertionError("network access attempted")

            socket.socket.connect = denied
            socket.create_connection = denied
            try:
                result = service.submit(
                    idempotency_key="offline-key",
                    capture_name="unsigned-consistent",
                    maximum_speed_cm_s=600,
                )
            finally:
                socket.socket.connect = original_connect
                socket.create_connection = original_create_connection

            self.assertEqual(result["state"], "VERIFIED")
            self.assertEqual(runner.calls, 1)

    def test_default_runner_is_wired_to_existing_end_to_end_experiment(self):
        self.assertEqual(gateway.END_TO_END_DEMO.name, "demo.py")
        self.assertEqual(gateway.END_TO_END_DEMO.parent.name, "end-to-end-v0")


if __name__ == "__main__":
    unittest.main()
