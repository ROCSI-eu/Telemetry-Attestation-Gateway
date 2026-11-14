#!/usr/bin/env python3
"""Structural safety and privacy checks for separate local console evidence types.

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

    def test_only_separate_local_mock_and_precomputed_evidence_are_referenced(self) -> None:
        html = PAGE.read_text(encoding="utf-8")
        self.assertIn('fetch("../integrated-cli-v0/evidence-results.json"', html)
        self.assertIn('fetch("authentic-evidence.json"', html)
        self.assertIn('"PRECOMPUTED_GENUINE_SYNTHETIC_VERIFICATION"', html)
        self.assertIn('"browser_verified"', (PAGE.parent / "authentic-evidence.json").read_text())
        self.assertIn(".layout[hidden]{display:none}", html)
        self.assertIn('"deterministic orchestration/control-flow evidence"', html)
        self.assertIn("LOCAL PREVIEW", html)
        self.assertIn("PRECOMPUTED ONLY", html)
        self.assertNotIn("http://", html)
        self.assertNotIn("https://", html)
        self.assertNotIn("WebSocket(", html)

    def test_narrow_viewport_evidence_labels_wrap_without_hiding_outcomes(self) -> None:
        html = PAGE.read_text(encoding="utf-8")
        # The very long synthetic evidence-kind token has no natural spaces.
        # Grid min-content sizing previously expanded a 320px viewport.
        self.assertIn("#authentic-panel{overflow-wrap:anywhere}", html)
        self.assertIn("#authentic-data > div{min-width:0}", html)
        self.assertIn("#authentic-data dl{grid-template-columns:minmax(0,1fr) auto}", html)
        self.assertIn("#authentic-data dt{overflow-wrap:anywhere}", html)
        self.assertIn('@media(max-width:750px)', html)
        self.assertIn('id="authentic-data" hidden', html)

    def test_browser_facing_fixture_has_exact_allowlisted_shape(self) -> None:
        """Reject new fields before they can reach the browser over local HTTP."""
        evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        self.assertEqual(
            set(evidence),
            {"boundaries", "cases", "evidence_kind", "evidence_note", "experiment", "labels"},
        )
        allowed_case = {
            "assurance", "claim", "command_path", "cryptographic",
            "proof_generation", "publication", "relying_party_decision",
            "restricted_fields_disclosed", "source", "source_trust",
            "verification_input",
        }
        allowed_publication = {"attempts", "error_code", "mode", "reconciled", "state"}
        for name, case in evidence["cases"].items():
            with self.subTest(case=name):
                self.assertEqual(set(case), allowed_case)
                self.assertEqual(set(case["publication"]), allowed_publication)
                self.assertIs(type(case["restricted_fields_disclosed"]), bool)
                self.assertIs(type(case["publication"]["reconciled"]), bool)
                self.assertIs(type(case["publication"]["attempts"]), int)

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
