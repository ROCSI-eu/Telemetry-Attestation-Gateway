#!/usr/bin/env python3
"""Privacy and strict schema checks for the precomputed genuine synthetic replay.

EXPERIMENTAL
SYNTHETIC_ONLY
A0_SYNTHETIC
NOT VALIDATION OR PRODUCTION AUTHORIZATION
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import export_authentic as exporter  # noqa: E402

FIXTURE = ROOT / "authentic-evidence.json"
HTML = ROOT / "index.html"


def checked(status: str = "VALID") -> dict:
    return {
        "labels": list(exporter.LABELS),
        "schema_version": exporter.authentic.RESULT_VERSION,
        "evidence_kind": "AUTHENTIC_SYNTHETIC_PACKAGE_CHECK",
        "mock": False,
        "package": {"status": "ACCEPTED", "reason": None},
        "verification_input": {"status": "ACCEPTED", "reason": None},
        "cryptographic": {"status": status, "reason": None if status == "VALID" else "PROOF_REJECTED"},
        "verification_performed": True,
        "proof_generation": "NOT_OBSERVED",
        "source_trust": "NOT_EVALUATED",
        "assurance": {
            "declared": "A0_SYNTHETIC",
            "effective": "A0_SYNTHETIC",
            "required": "NOT_EVALUATED",
            "demonstrator": "A0_SYNTHETIC",
        },
        "policy": "NOT_EVALUATED", "freshness": "NOT_EVALUATED",
        "revocation": "NOT_EVALUATED", "replay": "NOT_EVALUATED",
        "publication": "NOT_PERFORMED", "relying_party_decision": "NOT_MADE",
        "command_path": "NONE", "private_witness_disclosed": False,
        "proof_validity_is_telemetry_truth": False,
        # Must never reach output even if the upstream process has this material.
        "speed_cm_s": 1200, "proof": "DO_NOT_EXPORT", "vk": "DO_NOT_EXPORT",
        "witness": "DO_NOT_EXPORT", "identity": "DO_NOT_EXPORT",
        "raw_telemetry": "DO_NOT_EXPORT", "secret": "DO_NOT_EXPORT",
        "source_path": "/private/path/DO_NOT_EXPORT",
    }


class GenuineReplayTests(unittest.TestCase):
    def test_fixture_is_exact_minimized_shape_and_labeled(self) -> None:
        raw = FIXTURE.read_bytes()
        self.assertLessEqual(len(raw), 4096)
        result = json.loads(raw)
        self.assertEqual(set(result), exporter.FIELDS)
        self.assertEqual(result, exporter.minimize(checked()))
        self.assertEqual(result["evidence_kind"], exporter.KIND)
        self.assertFalse(result["browser_verified"])
        self.assertFalse(result["private_fields_disclosed"])
        self.assertEqual(result["proof_generation"], "NOT_OBSERVED")
        self.assertEqual(result["assurance"], "A0_SYNTHETIC")
        self.assertNotIn("DO_NOT_EXPORT", raw.decode())
        for restricted in ("speed_cm_s", "witness", "proof_bytes", "proof_hash", "source_path",
                           "vk", "raw_telemetry", "identity", "mission", "nonce", "salt"):
            self.assertNotIn('"' + restricted + '"', raw.decode())

    def test_minimization_drops_unknown_private_fields(self) -> None:
        minimized = exporter.minimize(checked())
        self.assertEqual(set(minimized), exporter.FIELDS)
        self.assertNotIn("DO_NOT_EXPORT", json.dumps(minimized))
        self.assertNotIn("1200", json.dumps(minimized))

    def test_no_mock_or_unverified_result_can_be_exported(self) -> None:
        for update in (
            {"mock": True},
            {"verification_performed": False},
            {"proof_generation": "GENERATED"},
            {"private_witness_disclosed": True},
            {"source_trust": "SIGNED"},
            {"publication": "MOCK_FINAL"},
            {"cryptographic": {"status": "UNVERIFIABLE", "reason": "NO_VERIFIER"}},
            {"cryptographic": {"status": "VALID", "reason": "PROOF_REJECTED"}},
        ):
            with self.subTest(update=update):
                data = checked()
                data.update(update)
                with self.assertRaises(exporter.ExportRejected):
                    exporter.minimize(data)

    def test_invalid_proof_remains_distinct(self) -> None:
        result = exporter.minimize(checked("INVALID"))
        self.assertEqual(result["cryptographic"], "INVALID")
        self.assertEqual(result["cryptographic_reason"], "PROOF_REJECTED")

    def test_export_never_serializes_upstream_or_overwrites(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            dest = Path(root) / "replay.json"
            with patch.object(exporter.authentic, "check_package", return_value=checked()) as verifier:
                exporter.export(Path(root) / "test-only", dest)
                self.assertEqual(set(json.loads(dest.read_text())), exporter.FIELDS)
                with self.assertRaises(exporter.ExportRejected):
                    exporter.export(Path(root) / "test-only", dest)
                self.assertEqual(verifier.call_count, 2)
            self.assertEqual(dest.stat().st_mode & 0o777, 0o600)

    def test_browser_is_static_separate_strict_and_fails_closed(self) -> None:
        html = HTML.read_text()
        self.assertIn('fetch("../integrated-cli-v0/evidence-results.json"', html)
        self.assertIn('fetch("authentic-evidence.json"', html)
        self.assertIn("Object.keys(e).length!==keys.length", html)
        self.assertIn("keys.every(k=>Object.hasOwn(e,k))", html)
        self.assertIn('$("authentic-data").hidden=true', html)
        self.assertIn(".layout[hidden]{display:none}", html)
        self.assertIn("Browser verification: NOT_PERFORMED", html)
        self.assertIn("NOT VALIDATION OR PRODUCTION AUTHORIZATION", html)
        for banned in ("WebSocket(", "localStorage", "sessionStorage", "navigator.sendBeacon",
                       "crypto.subtle", "http://", "https://"):
            self.assertNotIn(banned, html)


if __name__ == "__main__":
    unittest.main()
