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

    def test_mode_copy_changes_only_after_validated_local_capability(self) -> None:
        html = PAGE.read_text(encoding="utf-8")
        self.assertIn('id="console-mode">LOCAL PREVIEW · PRECOMPUTED ONLY</div>', html)
        self.assertIn('<footer id="console-footer">Local/offline demonstration preview only.', html)
        self.assertIn("or proof jobs. Sources are separately labeled", html)
        operator = html.split("async function initializeOperator() {", 1)[1].split(
            '$("operator-run").addEventListener', 1)[0]
        gate = operator.index('e.mode!=="ONE_SHOT_LOCAL_CLI"')
        active_label = operator.index(
            'setText("console-mode","LOCAL PREVIEW · ACTIVE ONE-SHOT CLI")')
        active_footer = operator.index('setText("console-footer","Local/offline experimental operator mode:')
        visible = operator.index('$("operator-panel").hidden=false')
        self.assertLess(gate, active_label)
        self.assertLess(active_label, active_footer)
        self.assertLess(active_footer, visible)
        self.assertIn('requires the explicitly provisioned private toolchain', operator)
        self.assertIn('only the final minimized CLI result', operator)
        self.assertIn('does not prove or verify', operator)
        self.assertIn('Recorded mock orchestration and precomputed offline-verifier replay remain separate', operator)
        self.assertIn('if(!response.ok) return;', operator)
        self.assertIn('}catch(_) { /* Static replay remains usable with no operator bridge. */ }', operator)

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

    def test_proof_scope_and_non_claims_are_visible_without_interaction(self) -> None:
        html = PAGE.read_text(encoding="utf-8")
        # The explanation precedes both result panels and is not behind details/JS.
        scope = html.index('<section class="scope"')
        mock = html.index('id="scenario-title"')
        authentic = html.index('id="authentic-panel"')
        self.assertLess(scope, mock)
        self.assertLess(scope, authentic)
        self.assertIn('aria-label="Scope and limitations of synthetic evidence"', html)
        self.assertIn("What the recorded result can show", html)
        self.assertIn("What it does not establish", html)
        for boundary in (
            "unauthenticated JSON replay", "does not verify or authenticate",
            "orchestration scenarios below are mocks", "Telemetry truth",
            "interval or flight coverage", "a relying-party decision",
            "A0_SYNTHETIC",
        ):
            self.assertIn(boundary, html)
        self.assertIn("@media(max-width:620px){.scope{grid-template-columns:1fr}}", html)

    def test_shared_operator_panel_is_one_shot_progressive_enhancement(self) -> None:
        html = PAGE.read_text(encoding="utf-8")
        self.assertIn('id="operator-panel" aria-labelledby="operator-title" hidden', html)
        self.assertIn('fetch("operator-capabilities",{cache:"no-store"})', html)
        self.assertIn('fetch("execute",{method:"POST",cache:"no-store"', html)
        self.assertIn("OPERATOR_KEYS.every(k=>Object.hasOwn(e,k))", html)
        self.assertIn("operatorResultAllowed(outcome,selected)", html)
        self.assertIn("waiting for complete isolated CLI result", html)
        self.assertIn("no stage progress reported", html)
        self.assertIn("one-shot may have been consumed", html)
        self.assertIn('"NOT_ATTEMPTED","NOT_CHECKED","NOT_PERFORMED"', html)
        for forbidden in ("localStorage", "sessionStorage", "WebSocket(", "EventSource(",
                          "setInterval(", "navigator.sendBeacon"):
            self.assertNotIn(forbidden, html)

    def test_mission_control_is_synthetic_and_separate_from_backend(self) -> None:
        html = PAGE.read_text(encoding="utf-8")
        start = html.index('<section class="mission-control"')
        end = html.index('<section class="card operator"', start)
        scene = html[start:end]
        self.assertIn('id="mission-control" data-motion="paused"', scene)
        self.assertIn('data-scene="pass" data-scene-started="false"', scene)
        self.assertIn('id="mission-pattern" aria-controls="mission-scene"', scene)
        self.assertIn('id="mission-replay" type="button"', scene)
        self.assertIn('id="mission-scene-status" role="status" aria-live="polite"', scene)
        self.assertIn('aria-labelledby="mission-scene-title mission-scene-description"', scene)
        self.assertIn('SYNTHETIC ROUTE · NOT GEOGRAPHIC', scene)
        self.assertIn('ILLUSTRATION ONLY · NO LIVE STREAM', scene)
        self.assertIn('id="mission-backend-state" role="status" aria-live="polite">NOT_OBSERVED', scene)
        self.assertIn('id="mission-backend-proof">NOT_OBSERVED', scene)
        self.assertIn('id="mission-backend-crypto">NOT_OBSERVED', scene)
        self.assertIn('No MAVLink commands, navigation control, mission edits', scene)
        self.assertIn('NOT VALIDATION OR PRODUCTION AUTHORIZATION', scene)
        for forbidden in ('fetch(', '<form', 'type="password"', 'http://', 'https://'):
            self.assertNotIn(forbidden, scene)
        self.assertEqual(scene.count('class="mission-craft"'), 1)
        route = 'M120 290 L275 249 L430 194 L585 142 L714 87'
        self.assertEqual(scene.count(route), 2)

    def test_mission_motion_pauses_and_respects_reduced_motion(self) -> None:
        html = PAGE.read_text(encoding="utf-8")
        self.assertIn('id="mission-motion-toggle" type="button" aria-pressed="true"', html)
        self.assertIn('document.addEventListener("visibilitychange",syncMissionMotion)', html)
        self.assertIn('motionPreference.addEventListener("change",()=>{', html)
        self.assertIn('window.matchMedia("(prefers-reduced-motion: reduce)")', html)
        self.assertIn('.mission-control[data-scene-started="true"][data-motion="paused"] .mission-craft', html)
        self.assertIn('.mission-control[data-scene-started="true"][data-visibility="hidden"] .mission-craft{animation-play-state:paused}', html)
        self.assertIn('@media(prefers-reduced-motion:reduce){.mission-craft{animation:none!important', html)
        self.assertIn('data-scene-started="true"][data-scene="pass"', html)
        self.assertIn('data-scene-started="true"][data-scene="hold"', html)
        self.assertIn('data-scene-started="true"][data-scene="return"', html)
        self.assertIn('craft.addEventListener("animationend"', html)
        self.assertIn('void mission.offsetWidth', html)
        self.assertIn('toggle.disabled=reduce || !active;', html)
        self.assertIn('toggle.setAttribute("aria-pressed",String(paused))', html)
        self.assertIn('mission.dataset.visibility=document.hidden?"hidden":"visible"', html)
        motion = html.split('// Entirely predetermined illustrative geometry.', 1)[1].split('function render(e)', 1)[0]
        for forbidden in ('fetch(', 'renderOperator(', 'execute(', 'setInterval(', 'WebSocket('):
            self.assertNotIn(forbidden, motion)

    def test_mission_backend_status_only_uses_validated_final_cli_outcome(self) -> None:
        html = PAGE.read_text(encoding="utf-8")
        recorded = html.split('function render(e)', 1)[1].split('async function initialize()', 1)[0]
        self.assertNotIn('setText("mission-backend-', recorded)
        operator = html.split('function renderOperator(e)', 1)[1].split('async function initializeOperator()', 1)[0]
        self.assertIn('setText("mission-backend-state","FINAL TYPED CLI RESULT · not live progress")', operator)
        self.assertIn('setText("mission-backend-proof",e.proof_generation)', operator)
        self.assertIn('setText("mission-backend-crypto",e.cryptographic)', operator)
        request = html.split('$("operator-run").addEventListener("click",async()=>{', 1)[1]
        self.assertLess(request.index('operatorResultAllowed(outcome,selected)'),
                        request.index('renderOperator(outcome)'))
        self.assertIn('setText("mission-backend-state","REQUEST IN FLIGHT · no confirmed stage progress")', request)
        self.assertIn('setText("mission-backend-proof","NOT_OBSERVED")', request)
        self.assertIn('setText("mission-backend-state","UNAVAILABLE · no accepted final CLI result")', request)
        self.assertIn('setText("mission-backend-crypto","NOT_OBSERVED")', request)
        for forbidden in ('localStorage', 'sessionStorage'):
            self.assertNotIn(forbidden, html)

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
