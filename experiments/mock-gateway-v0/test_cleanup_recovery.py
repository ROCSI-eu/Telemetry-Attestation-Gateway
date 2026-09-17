#!/usr/bin/env python3
"""Recovery tests for mock-gateway proof-package disposal."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

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


class SweepAwareRunner:
    def __init__(self, orphan: Path) -> None:
        self.orphan = orphan
        self.calls = 0

    def __call__(self, capture_name: str, maximum_speed_cm_s: int, package_dir: Path):
        self.calls += 1
        if self.orphan.exists():
            raise AssertionError("orphaned proof package was not swept before retry")
        (package_dir / "proof").write_text("synthetic-proof", encoding="utf-8")
        (package_dir / "witness").write_text("synthetic-witness", encoding="utf-8")
        return valid_result()


class CleanupRecoveryTests(unittest.TestCase):
    def test_restart_sweeps_orphaned_package_before_retry(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            state_path = root / "state.json"
            key = "restart-cleanup-key"
            capture = "unsigned-consistent"
            limit = 600
            key_digest = gateway._digest_idempotency_key(key)
            fingerprint = gateway._request_fingerprint(capture, limit)

            bootstrap = gateway.MockGateway(state_path, runner=lambda *_: valid_result())
            orphan = bootstrap._package_dir(key_digest, 1)
            self.assertEqual(
                orphan.parent.parent,
                state_path.with_name(state_path.name + ".proof-work"),
            )
            orphan.mkdir(parents=True)
            (orphan / "proof").write_text("orphaned-proof", encoding="utf-8")
            (orphan / "witness").write_text("orphaned-witness", encoding="utf-8")

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
                            }
                        ],
                        "reason": None,
                        "result": None,
                        "proof_package_disposed": False,
                    }
                },
            }
            state_path.write_text(json.dumps(state), encoding="utf-8")

            runner = SweepAwareRunner(orphan)
            restarted = gateway.MockGateway(state_path, runner=runner, max_attempts=3)
            result = restarted.submit(
                idempotency_key=key,
                capture_name=capture,
                maximum_speed_cm_s=limit,
            )

            self.assertEqual(result["state"], "VERIFIED")
            self.assertEqual(result["attempt_count"], 2)
            self.assertEqual(runner.calls, 1)
            self.assertTrue(result["proof_package_disposed"])
            self.assertFalse(orphan.exists())
            self.assertFalse(restarted._work_root().exists())
            self.assertEqual(
                [event["outcome"] for event in result["attempts"]],
                ["STARTED", "INTERRUPTED", "STARTED", "COMPLETED"],
            )


if __name__ == "__main__":
    unittest.main()
