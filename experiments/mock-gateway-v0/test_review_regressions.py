#!/usr/bin/env python3
"""Regression tests for final mock-gateway review findings."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import mock_gateway as gateway


def valid_result() -> dict:
    return {
        "invocation": {"status": "ACCEPTED", "reason": None},
        "telemetry": {
            "status": "NORMALIZED",
            "reason": None,
            "assurance_id": "A0_SYNTHETIC",
            "source_trust": "UNSIGNED",
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
    }


class FixtureDemoError(ValueError):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


class FixtureModule:
    DemoError = FixtureDemoError

    def __init__(self) -> None:
        self.calls = 0

    def run_fixture(self, capture_file, capture_name, maximum_speed_cm_s, package_dir):
        self.calls += 1
        if self.calls == 1:
            raise self.DemoError("FIXTURE_UNAVAILABLE_OR_INVALID")
        return valid_result()


class CountingRunner:
    def __init__(self, result: dict | None = None) -> None:
        self.calls = 0
        self.result = result if result is not None else valid_result()

    def __call__(self, capture_name: str, maximum_speed_cm_s: int, package_dir: Path):
        self.calls += 1
        return self.result


class AssertSweptRunner(CountingRunner):
    def __init__(self, prior_package: Path) -> None:
        super().__init__()
        self.prior_package = prior_package

    def __call__(self, capture_name: str, maximum_speed_cm_s: int, package_dir: Path):
        if self.prior_package.exists():
            raise AssertionError("prior retry package was not swept before resumed work")
        return super().__call__(capture_name, maximum_speed_cm_s, package_dir)


class ReviewRegressionTests(unittest.TestCase):
    def test_fixture_availability_failure_is_retryable(self):
        with tempfile.TemporaryDirectory() as temporary:
            module = FixtureModule()
            with mock.patch.object(gateway, "_load_end_to_end_demo", return_value=module):
                service = gateway.MockGateway(
                    Path(temporary) / "state.json",
                    runner=gateway.existing_end_to_end_runner,
                    max_attempts=2,
                )
                result = service.submit(
                    idempotency_key="fixture-retry-key",
                    capture_name="unsigned-consistent",
                    maximum_speed_cm_s=600,
                )

            self.assertEqual(result["state"], "VERIFIED")
            self.assertEqual(result["attempt_count"], 2)
            self.assertEqual(module.calls, 2)
            failures = [
                event for event in result["attempts"]
                if event["outcome"] == "RETRYABLE_FAILURE"
            ]
            self.assertEqual(len(failures), 1)
            self.assertEqual(failures[0]["stage"], "TELEMETRY")
            self.assertEqual(failures[0]["reason"], "FIXTURE_UNAVAILABLE_OR_INVALID")

    def test_verifier_failure_preserves_generated_proof_dimension(self):
        with tempfile.TemporaryDirectory() as temporary:
            result_with_verifier_outage = valid_result()
            result_with_verifier_outage["cryptographic"] = {
                "status": "UNVERIFIABLE",
                "reason": "VERIFIER_UNAVAILABLE",
            }
            runner = CountingRunner(result_with_verifier_outage)
            service = gateway.MockGateway(
                Path(temporary) / "state.json",
                runner=runner,
                max_attempts=1,
            )
            result = service.submit(
                idempotency_key="verifier-preserve-key",
                capture_name="unsigned-consistent",
                maximum_speed_cm_s=600,
            )

            self.assertEqual(result["state"], "FAILED")
            self.assertEqual(result["result"]["proof_generation"], "GENERATED")
            self.assertEqual(
                result["result"]["cryptographic"]["status"], "UNVERIFIABLE"
            )
            self.assertEqual(
                result["result"]["cryptographic"]["reason"], "VERIFIER_UNAVAILABLE"
            )

    def test_terminal_cleanup_failure_retries_disposal_before_replay(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            state_path = root / "state.json"
            key = "cleanup-replay-key"
            capture = "unsigned-consistent"
            limit = 600
            key_digest = gateway._digest_idempotency_key(key)
            fingerprint = gateway._request_fingerprint(capture, limit)

            bootstrap = gateway.MockGateway(state_path, runner=CountingRunner())
            package_dir = bootstrap._package_dir(key_digest, 1)
            package_dir.mkdir(parents=True)
            (package_dir / "proof").write_text("restricted-proof", encoding="utf-8")
            (package_dir / "witness").write_text("restricted-witness", encoding="utf-8")

            state = {
                "schema_version": 1,
                "labels": list(gateway.LABELS),
                "records": {
                    key_digest: {
                        "request_fingerprint": fingerprint,
                        "state": "FAILED",
                        "lifecycle": ["RECEIVED", "PROVING", "FAILED"],
                        "attempts": [
                            {
                                "number": 1,
                                "stage": "END_TO_END",
                                "outcome": "STARTED",
                                "reason": None,
                            },
                            {
                                "number": 1,
                                "stage": "CLEANUP",
                                "outcome": "CLEANUP_FAILED",
                                "reason": "PROOF_PACKAGE_DISPOSAL_FAILED",
                            },
                        ],
                        "reason": "PROOF_PACKAGE_DISPOSAL_FAILED",
                        "result": gateway._failure_dimensions(
                            "PROVING", "PROOF_PACKAGE_DISPOSAL_FAILED"
                        ),
                        "proof_package_disposed": False,
                    }
                },
            }
            state_path.write_text(json.dumps(state), encoding="utf-8")

            runner = CountingRunner()
            service = gateway.MockGateway(state_path, runner=runner)
            result = service.submit(
                idempotency_key=key,
                capture_name=capture,
                maximum_speed_cm_s=limit,
            )

            self.assertEqual(result["state"], "FAILED")
            self.assertTrue(result["proof_package_disposed"])
            self.assertFalse(package_dir.exists())
            self.assertEqual(runner.calls, 0)
            self.assertEqual(result["attempts"][-1]["stage"], "CLEANUP")
            self.assertEqual(result["attempts"][-1]["outcome"], "CLEANUP_RECOVERED")

    def test_persisted_retry_failure_sweeps_package_before_next_attempt(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            state_path = root / "state.json"
            key = "retry-crash-window-key"
            capture = "unsigned-consistent"
            limit = 600
            key_digest = gateway._digest_idempotency_key(key)
            fingerprint = gateway._request_fingerprint(capture, limit)

            bootstrap = gateway.MockGateway(state_path, runner=CountingRunner())
            package_dir = bootstrap._package_dir(key_digest, 1)
            package_dir.mkdir(parents=True)
            (package_dir / "proof").write_text("orphaned-proof", encoding="utf-8")
            state = {
                "schema_version": 1,
                "labels": list(gateway.LABELS),
                "records": {
                    key_digest: {
                        "request_fingerprint": fingerprint,
                        "state": "PROVING",
                        "lifecycle": ["RECEIVED", "PROVING"],
                        "attempts": [
                            {
                                "number": 1,
                                "stage": "END_TO_END",
                                "outcome": "STARTED",
                                "reason": None,
                            },
                            {
                                "number": 1,
                                "stage": "VERIFYING",
                                "outcome": "RETRYABLE_FAILURE",
                                "reason": "VERIFIER_UNAVAILABLE",
                            },
                        ],
                        "reason": "VERIFIER_UNAVAILABLE",
                        "result": gateway._failure_dimensions(
                            "VERIFYING", "VERIFIER_UNAVAILABLE"
                        ),
                        "proof_package_disposed": False,
                    }
                },
            }
            state_path.write_text(json.dumps(state), encoding="utf-8")

            runner = AssertSweptRunner(package_dir)
            service = gateway.MockGateway(state_path, runner=runner, max_attempts=2)
            result = service.submit(
                idempotency_key=key,
                capture_name=capture,
                maximum_speed_cm_s=limit,
            )

            self.assertEqual(result["state"], "VERIFIED")
            self.assertEqual(result["attempt_count"], 2)
            self.assertEqual(runner.calls, 1)
            self.assertFalse(package_dir.exists())
            self.assertTrue(result["proof_package_disposed"])

    def test_persisted_completed_result_resumes_without_reproving(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            state_path = root / "state.json"
            key = "completed-crash-window-key"
            capture = "unsigned-consistent"
            limit = 600
            key_digest = gateway._digest_idempotency_key(key)
            fingerprint = gateway._request_fingerprint(capture, limit)
            completed_result = gateway._minimal_verifier_dimensions(valid_result())
            state = {
                "schema_version": 1,
                "labels": list(gateway.LABELS),
                "records": {
                    key_digest: {
                        "request_fingerprint": fingerprint,
                        "state": "PROVING",
                        "lifecycle": ["RECEIVED", "PROVING"],
                        "attempts": [
                            {
                                "number": 1,
                                "stage": "END_TO_END",
                                "outcome": "STARTED",
                                "reason": None,
                            },
                            {
                                "number": 1,
                                "stage": "END_TO_END",
                                "outcome": "COMPLETED",
                                "reason": None,
                            },
                        ],
                        "reason": None,
                        "result": completed_result,
                        "proof_package_disposed": True,
                    }
                },
            }
            state_path.write_text(json.dumps(state), encoding="utf-8")

            runner = CountingRunner()
            service = gateway.MockGateway(state_path, runner=runner, max_attempts=1)
            result = service.submit(
                idempotency_key=key,
                capture_name=capture,
                maximum_speed_cm_s=limit,
            )

            self.assertEqual(result["state"], "VERIFIED")
            self.assertEqual(runner.calls, 0)
            self.assertEqual(result["attempt_count"], 1)
            self.assertEqual(result["result"]["cryptographic"]["status"], "VALID")
            self.assertEqual(
                result["lifecycle"], ["RECEIVED", "PROVING", "PROVED", "VERIFIED"]
            )


if __name__ == "__main__":
    unittest.main()
