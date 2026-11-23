#!/usr/bin/env python3
"""Offline-only contract tests. No simulator, cryptographic tools or live runtime."""
from __future__ import annotations

import json
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch

import sitl_record as record
import refresh_local_console as session
import run_private_preview as viewer


def completed():
    return {
        "labels": record.LABELS.copy(),
        "source": "real_Copter_4.7.1_synthetic_SITL",
        "observations": 2, "normalization": "NORMALIZED", "source_trust": "UNSIGNED",
        "proof": "GENERATED", "integrated_crypto": "VALID",
        "separate_process_crypto": "VALID", "publication": "DISABLED",
        "relying_party_decision": "NOT_MADE", "command_path": "NONE",
        "status": "PASS", "cleanup": "PASS",
    }


class SITLRecordTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="tag-sitl-record-contract-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.origin = self.root / "owner-private-record"
        self.origin.mkdir(mode=0o700)
        self.destination = self.root / "private-preview"

    def _saved(self):
        record.write_completed(completed(), self.origin)
        return record.read_private(self.origin)

    def test_strict_completed_result_and_minimization(self):
        minimized = record.minimize_completed(completed())
        self.assertEqual(minimized["integrated_crypto"], "VALID")
        self.assertEqual(minimized["separate_process_crypto"], "VALID")
        self.assertFalse(minimized["record_authenticated"])
        self.assertFalse(minimized["browser_verified"])
        self.assertFalse(minimized["proof_validity_is_telemetry_truth"])
        self.assertEqual(minimized["source_trust"], "UNSIGNED")
        for sensitive in ("witness", "frame_hex", "private_speed", "public-artifact",
                          "verification_key", "proof_bytes", "coordinates"):
            self.assertNotIn(sensitive, json.dumps(minimized))
        for key, unexpected in (
            ("cleanup", "FAILED"), ("status", "FAIL"),
            ("integrated_crypto", "INVALID"), ("separate_process_crypto", "INVALID"),
            ("publication", "ENABLED"), ("source_trust", "SIGNED"),
            ("observations", True), ("command_path", "MAVLINK_COMMAND"),
        ):
            changed = completed()
            changed[key] = unexpected
            with self.subTest(key=key), self.assertRaises(record.RecordRejected):
                record.minimize_completed(changed)
        extra = completed()
        extra["proof_bytes"] = "secret"
        with self.assertRaises(record.RecordRejected):
            record.minimize_completed(extra)

    def test_private_exclusive_write_and_checked_read(self):
        raw = self._saved()
        self.assertLess(len(raw), 4096)
        self.assertEqual(stat.S_IMODE((self.origin / record.NAME).stat().st_mode), 0o600)
        self.assertEqual(record.parse_record(raw)["proof_generation"], "GENERATED")
        with self.assertRaises(record.RecordRejected):
            record.write_completed(completed(), self.origin)
        self.assertEqual(record.read_private(self.origin), raw)
        (self.origin / record.NAME).chmod(0o644)
        with self.assertRaises(record.RecordRejected):
            record.read_private(self.origin)

    def test_forged_expanded_or_tampered_json_fails_closed(self):
        raw = self._saved()
        e = json.loads(raw)
        for key, unexpected in (
            ("proof_generation", "NOT_ATTEMPTED"), ("source_trust", "SIGNED"),
            ("record_authenticated", True), ("public_maximum_cm_s", 601),
            ("integrated_crypto", "NOT_CHECKED"), ("browser_verified", True),
        ):
            forged = {**e, key: unexpected}
            with self.subTest(key=key), self.assertRaises(record.RecordRejected):
                record.parse_record(json.dumps(forged).encode())
        with self.assertRaises(record.RecordRejected):
            record.parse_record(b'{"labels":[], "labels":[]}')
        self.origin.chmod(0o755)
        with self.assertRaises(record.RecordRejected):
            record.read_private(self.origin)

    def test_offline_refresh_is_record_only_and_keeps_other_sources_separate(self):
        raw = self._saved()
        with patch.object(session.exporter, "export", side_effect=AssertionError("no verifier")):
            session.refresh(None, self.destination, sitl_record_dir=self.origin)
        self.assertEqual(
            (self.destination / "web-console-v0" / record.NAME).read_bytes(), raw)
        session._existing_session_safe(self.destination)
        self.assertEqual(
            (self.destination / "web-console-v0/authentic-evidence.json").read_bytes(),
            (session.HERE / "authentic-evidence.json").read_bytes())
        self.assertEqual(
            (self.destination / "integrated-cli-v0/evidence-results.json").read_bytes(),
            session.SOURCE_MOCK.read_bytes())
        with self.assertRaises(session.SessionRejected):
            session.refresh(None, self.destination, sitl_record_dir=self.origin)
        with self.assertRaises(session.SessionRejected):
            session.refresh(self.origin, self.destination)

    def test_loopback_assets_optional_and_frozen_before_serving(self):
        self._saved()
        session.refresh(None, self.destination, sitl_record_dir=self.origin)
        assets = viewer.approved_assets(self.destination)
        self.assertEqual(set(assets) - set(viewer.ROUTES),
                         {"/web-console-v0/sitl-record.json"})
        self.assertEqual(
            record.parse_record(assets["/web-console-v0/sitl-record.json"][0])
                ["separate_process_crypto"], "VALID")
        recorded = self.destination / "web-console-v0" / record.NAME
        recorded.write_text('{"raw_telemetry": "UNSAFE"}', encoding="utf-8")
        with self.assertRaises((session.SessionRejected, viewer.Rejected)):
            viewer.approved_assets(self.destination)

    def test_ui_is_hidden_and_does_not_upgrade_recorded_json(self):
        html = session.SOURCE_INDEX.read_text(encoding="utf-8")
        self.assertIn('id="sitl-record-panel"', html)
        self.assertIn('fetch("sitl-record.json",{cache:"no-store"})', html)
        self.assertIn('Object.keys(e).length!==keys.length', html)
        self.assertIn('record_authenticated:false,browser_verified:false', html)
        self.assertIn('A structurally valid record is NOT an authenticated attestation', html)
        self.assertIn('panel.hidden=true', html)
        self.assertIn('panel.hidden=false', html)
        self.assertNotIn("WebSocket(", html)
        # The existing active CLI backend truth is changed only by its own
        # authenticated one-shot path, never by the recorded self-report.
        segment = html.split("async function initializeSITLRecord()", 1)[1].split(
            "const OPERATOR_KEYS=", 1)[0]
        self.assertNotIn("mission-backend-", segment)
        source = (session.REPO / "experiments/sitl-receive-v0/sitl_ci_e2e.py").read_text()
        self.assertEqual(source.count(
            "        record = run_once()  # Includes separate verification and full cleanup."), 1)
        self.assertEqual(source.count("sitl_record.write_completed(completed, args.record_dir)"), 1)
        self.assertLess(source.index("record = run_once()  # Includes"),
                        source.index("sitl_record.write_completed(completed"))


if __name__ == "__main__":
    unittest.main()
