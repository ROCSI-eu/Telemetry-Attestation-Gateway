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
    def test_frozen_bundle_has_only_fourteen_allowlisted_files(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            self.assertEqual(set(build(target)), {
                "index.html", "en/index.html", "404.html", "en/404.html",
                "evidence-results.json", "authentic-evidence.json", "_headers", "_redirects",
                "robots.txt", "assets/favicon.svg", "assets/favicon.ico", "assets/apple-touch-icon.png",
                "og/ro.png", "og/en.png",
            })
            html = (target / "index.html").read_text(encoding="utf-8")
            self.assertIn('lang="ro"', html)
            self.assertIn("Centru de comandă și control", html)
            self.assertIn("DEMONSTRAȚIE PUBLICĂ · DOAR REZULTATE PRECALCULATE", html)
            self.assertIn("telemetrie sintetică → normalizare → dovadă → verificare independentă → publicare opțională", html)
            self.assertIn("TRASEU SINTETIC · FĂRĂ REFERINȚĂ GEOGRAFICĂ", html)
            self.assertIn("Fără comenzi MAVLink, controlul navigației", html)
            for label in LABELS:
                self.assertIn(label, html)
            self.assertNotIn("operator-", html)
            for secret_surface in (
                '"/execute"', '"/operator-capabilities"', "X-TAG-Local-Token",
                "type=\"password\"", "operatorResultAllowed", "initializeOperator",
                "one-shot", "http://", "WebSocket(", "EventSource(",
                "localStorage", "sessionStorage", "navigator.sendBeacon",
            ):
                self.assertNotIn(secret_surface, html)
            self.assertEqual(
                set(re.findall(r'fetch\("([^"]+)"', html)),
                {"/evidence-results.json", "/authentic-evidence.json"},
            )
            self.assertNotIn("../", html)
            self.assertNotIn('style="', html)
            self.assertIn("noindex", html)
            self.assertEqual((target / "robots.txt").read_text(), "User-agent: *\nAllow: /\n")
            self.assertIn('content="noindex,nofollow"', html)
            self.assertIn('<meta property="og:locale" content="ro_RO">', html)
            self.assertIn('<meta name="twitter:card" content="summary_large_image">', html)

    def test_romanian_alias_uses_single_permanent_pages_redirect(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            build(target)
            self.assertEqual(
                (target / "_redirects").read_text(encoding="utf-8"),
                "/ro/ / 301\n",
            )
            self.assertFalse((target / "ro").exists())
            html = (target / "index.html").read_text(encoding="utf-8")
            self.assertIn('<link rel="canonical" href="https://tag.rocsi.eu/">', html)
            self.assertIn('<link rel="alternate" hreflang="ro" href="https://tag.rocsi.eu/">', html)
            self.assertIn('<meta property="og:image" content="https://tag.rocsi.eu/og/ro.png">', html)

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
            self.assertIn('lang="ro"', page)
            self.assertIn("Pagina nu a fost găsită", page)
            self.assertEqual(re.findall(r'href="([^"]+)"', page), ["/", "/en/"])
            en_page = (target / "en/404.html").read_text()
            self.assertIn('lang="en"', en_page)
            self.assertIn("Page not found", en_page)
            self.assertEqual(re.findall(r'href="([^"]+)"', en_page), ["/en/", "/"])
            for forbidden in (
                "<script", "<style", "<form", "<iframe", "<img",
                "http://", "https://", "/execute", "operator-",
                "fetch(", "WebSocket(", "location.href",
            ):
                self.assertNotIn(forbidden, page)
            self.assertIn("/*", (target / "_headers").read_text(encoding="utf-8"))

    def test_ro_en_social_metadata_and_localized_static_content(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            build(target)
            ro = (target / "index.html").read_text(encoding="utf-8")
            en = (target / "en/index.html").read_text(encoding="utf-8")
            self.assertIn('<html lang="ro">', ro)
            self.assertIn('<html lang="en">', en)
            self.assertIn("<h1>Centru de comandă și control</h1>", ro)
            self.assertIn("<h1>Mission Control</h1>", en)
            self.assertIn("Continuă animația</button>", ro)
            self.assertIn("Resume illustration</button>", en)
            self.assertIn('href="/" hreflang="ro" lang="ro" aria-current="page"', ro)
            self.assertIn('href="/en/" hreflang="en" lang="en" aria-current="page"', en)
            for language, page, locale in (
                ("ro", ro, "ro_RO"), ("en", en, "en_US")
            ):
                from localization import SHARE, ORIGIN
                image = ORIGIN + "/og/" + language + ".png"
                self.assertIn(f'<meta property="og:locale" content="{locale}">', page)
                self.assertIn(f'<meta property="og:image" content="{image}">', page)
                self.assertIn(f'<meta name="twitter:image" content="{image}">', page)
                self.assertIn('href="/assets/favicon.svg"', page)
                self.assertIn('href="/assets/favicon.ico"', page)
                self.assertIn('href="/assets/apple-touch-icon.png"', page)
                self.assertIn(SHARE[language]["title"], page)
                self.assertIn(SHARE[language]["description"], page)
                self.assertIn(f'<link rel="canonical" href="{ORIGIN}{"/" if language=="ro" else "/en/"}">', page)
                self.assertNotIn("operator-panel", page)
                self.assertEqual(
                    set(re.findall(r'fetch\("([^"]+)"', page)),
                    {"/evidence-results.json", "/authentic-evidence.json"},
                )
                self.assertIn("A0_SYNTHETIC", page)
                self.assertIn("SYNTHETIC_ONLY", page)
                self.assertIn("NOT VALIDATION OR PRODUCTION AUTHORIZATION", page)
            self.assertNotEqual(ro, en)
            self.assertEqual(
                re.search(r'<script>(.*?)</script>', ro, flags=re.S).group(1),
                re.search(r'<script>(.*?)</script>', en, flags=re.S).group(1)
            )

    def test_social_graphics_dimensions_and_favicon(self) -> None:
        import struct
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            build(target)
            for language in ("ro", "en"):
                image = (target / "og" / f"{language}.png").read_bytes()
                self.assertTrue(image.startswith(b"\x89PNG\r\n\x1a\n"))
                self.assertEqual(struct.unpack(">II", image[16:24]), (1200, 630))
                self.assertLess(len(image), 450_000)
            self.assertNotEqual(
                (target / "og/ro.png").read_bytes(),
                (target / "og/en.png").read_bytes()
            )
            self.assertIn('viewBox="0 0 64 64"', (target / "assets/favicon.svg").read_text())
            self.assertTrue((target / "assets/favicon.ico").read_bytes().startswith(b"\x00\x00\x01\x00"))
            self.assertTrue((target / "assets/apple-touch-icon.png").read_bytes().startswith(b"\x89PNG"))
            self.assertIn("img-src 'self' data:", (target / "_headers").read_text())

    def test_reject_untranslated_public_text_drift(self) -> None:
        from localization import romanian_html
        html = public_html(CONSOLE.read_text(encoding="utf-8"))
        self.assertIn("<html lang=\"ro\">", romanian_html(html))
        with self.assertRaisesRegex(ValueError, "untranslated public HTML"):
            romanian_html(html.replace("<h1>Mission Control</h1>", "<h1>New untranslated text</h1>"))

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
        self.assertIn('id="mission-motion-toggle" type="button" aria-pressed="true"', html)
        self.assertIn("document.addEventListener(\"visibilitychange\",syncMissionMotion)", html)
        self.assertIn('motionPreference.addEventListener("change",()=>{', html)
        self.assertIn('@media(prefers-reduced-motion:reduce){.mission-craft{animation:none!important', html)
        self.assertIn('.mission-control[data-scene-started="true"][data-motion="paused"] .mission-craft', html)
        self.assertIn("toggle.disabled=reduce || !active;", html)
        motion = html.split("// Entirely predetermined illustrative geometry.", 1)[1].split("function render(e)", 1)[0]
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
            assets = {str(p.relative_to(target)): p.read_bytes() for p in target.rglob("*") if p.is_file()}
            build(target)
            self.assertEqual(assets, {str(p.relative_to(target)): p.read_bytes() for p in target.rglob("*") if p.is_file()})


if __name__ == "__main__":
    unittest.main()
