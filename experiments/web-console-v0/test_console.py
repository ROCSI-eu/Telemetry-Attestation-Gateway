#!/usr/bin/env python3
"""Structural safety and fixture checks for local mock-only web console.

EXPERIMENTAL
SYNTHETIC_ONLY
A0_SYNTHETIC
NOT VALIDATION OR PRODUCTION AUTHORIZATION
"""

from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PAGE = Path(__file__).with_name("index.html")
EVIDENCE = ROOT / "integrated-cli-v0" / "evidence-results.json"
LABELS = (
    "EXPERIMENTAL",
    "SYNTHETIC_ONLY",
    "A0_SYNTHETIC",
    "NOT VALIDATION OR PRODUCTION AUTHORIZATION",
)


class ConsoleFixtureTests(unittest.TestCase):
    def test_all_required_labels_visible_in_page_and_evidence(self) -> None:
        html = PAGE.read_text(encoding="utf-8")
        evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        for label in LABELS:
            self.assertIn(label, html)
            self.assertIn(label, evidence["labels"])

    def test_only_local_mock_evidence_is_referenced(self) -> None:
        html = PAGE.read_text(encoding="utf-8")
        self.assertIn('fetch("../integrated-cli-v0/evidence-results.json"', html)
        self.assertIn('"deterministic orchestration/control-flow evidence"', html)
        self.assertIn("LOCAL PREVIEW", html)
        self.assertIn("NO LIVE PROOF", html)
        self.assertNotIn("http://", html)
        self.assertNotIn("https://", html)
        self.assertNotIn("WebSocket(", html)

    def test_recorded_states_are_minimized_and_typed(self) -> None:
        evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        self.assertTrue(evidence["cases"])
        for case in evidence["cases"].values():
            self.assertEqual(case["assurance"], "A0_SYNTHETIC")
            self.assertEqual(case["command_path"], "NONE")
            self.assertEqual(case["relying_party_decision"], "NOT_MADE")
            self.assertFalse(case["restricted_fields_disclosed"])
            self.assertIn("cryptographic", case)
            self.assertIn("publication", case)
            self.assertNotIn("frame_hex", case)
            self.assertNotIn("speed_cm_s", case)


if __name__ == "__main__":
    unittest.main()
