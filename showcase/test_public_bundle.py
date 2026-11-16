#!/usr/bin/env python3
"""Focused static-showcase isolation, minimization and reproducibility tests."""
from __future__ import annotations

import base64
import copy
import hashlib
import json
from pathlib import Path
import re
import tempfile
import unittest

from build import (
    CASE_KEYS, CONSOLE, LABELS, SCENARIOS, VERIFIER, build,
    minimized_scenarios, minimized_verifier, public_html, sha256_source,
)


class StaticShowcaseTests(unittest.TestCase):
    def test_frozen_bundle_only_has_six_public_assets(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            self.assertEqual(set(build(target)), {
                "index.html", "404.html", "evidence-results.json",
                "authentic-evidence.json", "_headers", "robots.txt",
            })
            html = (target / "index.html").read_text(encoding="utf-8")
            self.assertIn("Mission Control", html)
            self.assertIn("PUBLIC SHOWCASE · PRECOMPUTED ONLY", html)
            self.assertIn("synthetic telemetry → normalization → proof → independent verification → optional publication", html)
            self.assertIn("SYNTHETIC ROUTE · NOT GEOGRAPHIC", html)
            self.assertIn("No MAVLink commands, navigation control", html)
            for label in LABELS:
                self.assertIn(label, html)
            self.assertNotIn("operator-", html)
            for secret_surface in (
                '"/execute"', '"/operator-capabilities"', "X-TAG-Local-Token",
                "type=\"password\"", "operatorResultAllowed", "initializeOperator",
                "one-shot", "http://", "https://", "WebSocket(", "EventSource(",
                "localStorage", "sessionStorage", "navigator.sendBeacon",
            ):
                self.assertNotIn(secret_surface, html)
            self.assertEqual(
                set(re.findall(r'fetch\("([^"]+)"', html)),
                {"evidence-results.json", "authentic-evidence.json"},
            )
            self.assertNotIn("../", html)
            self.assertNotIn('style="', html)
            self.assertIn("noindex", html)
            self.assertIn("Disallow: /", (target / "robots.txt").read_text())

    def test_cloudflare_pages_404_is_static_and_has_no_execution_surface(self) -> None:
        # A root 404.html prevents Cloudflare Pages' implicit SPA fallback.
        # Actual HTTP 404 behavior is verified only at authorized deployment.
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            build(target)
            page = (target / "404.html").read_text(encoding="utf-8")
            self.assertTrue(page.startswith("<!doctype html>"))
            self.assertIn('<meta name="robots" content="noindex,nofollow">', page)
            self.assertIn("<h1>404", page)
            for label in LABELS:
                self.assertIn(label, page)
            self.assertEqual(re.findall(r'href="([^"]+)"', page), ["/"])
            for forbidden in (
                "<script", "<style", "<form", "<iframe", "<img",
                "http://", "https://", "/execute", "operator-",
                "fetch(", "WebSocket(", "location.href",
            ):
                self.assertNotIn(forbidden, page)
            self.assertIn("/*", (target / "_headers").read_text(encoding="utf-8"))

    def test_public_scenarios_are_strictly_reconstructed(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            build(Path(folder))
            source = json.loads(SCENARIOS.read_text(encoding="utf-8"))
            output = json.loads((Path(folder) / "evidence-results.json").read_text())
            self.assertEqual(set(output), {"labels", "evidence_kind", "cases"})
            self.assertEqual(set(output["cases"]), set(source["cases"]))
            for item in output["cases"].values():
                self.assertEqual(set(item), CASE_KEYS)
                self.assertEqual(item["command_path"], "NONE")
                self.assertIs(item["restricted_fields_disclosed"], False)
                self.assertEqual(item["assurance"], "A0_SYNTHETIC")
                self.assertEqual(item["relying_party_decision"], "NOT_MADE")
                self.assertNotIn("speed_cm_s", json.dumps(item))

    def test_new_fields_and_boundary_drift_fail_closed(self) -> None:
        original = json.loads(SCENARIOS.read_text(encoding="utf-8"))
        injected = copy.deepcopy(original)
        injected["cases"]["over_limit"]["private_speed_cm_s"] = 415
        with self.assertRaises(ValueError):
            minimized_scenarios(injected)
        injected = copy.deepcopy(original)
        injected["boundaries"]["raw_telemetry_disclosed"] = True
        with self.assertRaises(ValueError):
            minimized_scenarios(injected)
        injected = copy.deepcopy(original)
        injected["cases"]["over_limit"]["source"] = "/tmp/private"
        with self.assertRaises(ValueError):
            minimized_scenarios(injected)
        genuine = json.loads(VERIFIER.read_text(encoding="utf-8"))
        genuine["operator_token"] = "must-not-copy"
        with self.assertRaises(ValueError):
            minimized_verifier(genuine)

    def test_precomputed_verifier_remains_independent(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            build(Path(folder))
            output = json.loads((Path(folder) / "authentic-evidence.json").read_text())
            self.assertEqual(output["evidence_kind"], "PRECOMPUTED_GENUINE_SYNTHETIC_VERIFICATION")
            self.assertEqual(output["verification_basis"], "INDEPENDENT_OFFLINE_CHECK_AT_EXPORT")
            self.assertEqual(output["browser_verified"], False)
            self.assertEqual(output["private_fields_disclosed"], False)
            self.assertEqual(output["proof_generation"], "NOT_OBSERVED")
            self.assertEqual(output["publication"], "NOT_PERFORMED")
            self.assertEqual(output["relying_party_decision"], "NOT_MADE")

    def test_motion_accessibility_and_no_backend_animation_coupling(self) -> None:
        html = public_html(CONSOLE.read_text(encoding="utf-8"))
        self.assertIn('id="mission-motion-toggle" type="button" aria-pressed="false"', html)
        self.assertIn("document.addEventListener(\"visibilitychange\",syncMissionMotion)", html)
        self.assertIn('motionPreference.addEventListener("change",syncMissionMotion)', html)
        self.assertIn('@media(prefers-reduced-motion:reduce){.mission-craft{animation:none', html)
        self.assertIn('.mission-control[data-motion="paused"] .mission-craft', html)
        self.assertIn("toggle.disabled=reduce;", html)
        motion = html.split("// Purely illustrative, fixed SVG geometry.", 1)[1].split("function render(e)", 1)[0]
        for forbidden in ("fetch(", "execute(", "setInterval(", "WebSocket(", "renderOperator("):
            self.assertNotIn(forbidden, motion)

    def test_strict_csp_hashes_match_inline_code(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            build(Path(folder))
            target = Path(folder)
            html = (target / "index.html").read_text(encoding="utf-8")
            headers = (target / "_headers").read_text(encoding="utf-8")
            css = re.search(r"<style>(.*?)</style>", html, flags=re.S).group(1)
            js = re.search(r"<script>(.*?)</script>", html, flags=re.S).group(1)
            for block in (css, js):
                self.assertIn(sha256_source(block), headers)
            for required in (
                "default-src 'none'", "connect-src 'self'", "frame-ancestors 'none'",
                "style-src-attr 'none'", "Permissions-Policy: camera=()",
                "Cache-Control: no-store",
            ):
                self.assertIn(required, headers)
            assets = {p.name: p.read_bytes() for p in target.iterdir()}
            build(target)
            self.assertEqual(assets, {p.name: p.read_bytes() for p in target.iterdir()})


if __name__ == "__main__":
    unittest.main()
