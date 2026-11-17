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
from unittest.mock import patch

from build import (
    CASE_KEYS, CONSOLE, LABELS, SCENARIOS, VERIFIER, build,
    minimized_scenarios, minimized_verifier, public_html, sha256_source,
)


class StaticShowcaseTests(unittest.TestCase):
    def test_introductory_layer_is_bilingual_and_technical_limits_remain_accessible(self) -> None:
        from localization import SHARE
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            build(target)
            ro = (target / "index.html").read_text(encoding="utf-8")
            en = (target / "en/index.html").read_text(encoding="utf-8")
            for page, heading, application, scope, title in (
                (ro, "Verifică o condiție fără să divulgi toată telemetria",
                 "Aplicații potențiale, nu implementări validate",
                 "Domeniul complet și limitele experimentale", SHARE["ro"]["title"]),
                (en, "Verify a condition without revealing all the telemetry",
                 "Potential applications, not validated deployments",
                 "Full experimental scope and limitations", SHARE["en"]["title"]),
            ):
                self.assertIn(heading, page)
                self.assertIn(application, page)
                self.assertIn(scope, page)
                self.assertIn("<title>"+title+"</title>", page)
                ordered = ('id="hero-title"', 'id="primer-title"', 'id="mission-control"',
                           'id="use-cases-title"', 'id="technical-evidence-title"',
                           'id="scenario-title"', 'id="authentic-title"',
                           'id="research-limitations-title"', 'id="technical-scope"')
                self.assertEqual([page.index(marker) for marker in ordered],
                                 sorted(page.index(marker) for marker in ordered))
                self.assertIn('<summary>'+scope+'</summary>', page)
                self.assertIn('id="scope-proves"', page)
                self.assertIn('id="scope-limits"', page)
                self.assertIn('href="#authentic-title"', page)
                self.assertIn('href="#scenario-title"', page)
                self.assertIn('EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC', page)
                self.assertIn('NOT VALIDATION OR PRODUCTION AUTHORIZATION', page)
                self.assertIn('id="mission-pattern"', page)
                self.assertIn("PRECOMPUTED_GENUINE_SYNTHETIC_VERIFICATION", page)
            self.assertIn("nu atestă o misiune efectivă", ro)
            self.assertIn("does not test a real measurement", en)
            self.assertIn("nu se conectează la vehicule", ro)
            self.assertIn("does not connect to or control any vehicle", en)

    def test_visual_final_remains_synthetic_bilingual_and_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            build(target)
            ro = (target / "index.html").read_text(encoding="utf-8")
            en = (target / "en/index.html").read_text(encoding="utf-8")
            for page, words in (
                (ro, ("TAG / OBSERVAȚIE SINTETICĂ", "DOAR OBSERVAȚIE",
                      "Condiție prestabilită", "Nu este luată aici")),
                (en, ("TAG / SYNTHETIC OBSERVATION", "OBSERVATION ONLY",
                      "Predefined condition", "Not made on this page")),
            ):
                self.assertIn('class="hero-scene"', page)
                self.assertIn('class="hero-vehicle"', page)
                self.assertIn('class="evidence-path"', page)
                self.assertIn('aria-hidden="true"', page)
                self.assertIn('role="group"', page)
                self.assertIn('prefers-reduced-motion:reduce', page)
                for item in words:
                    self.assertIn(item, page)
                self.assertNotIn('class="hero-axis"', page)
            self.assertIn('evidence-path', ro)
            self.assertEqual(
                re.search(r'<script>(.*?)</script>', ro, flags=re.S).group(1),
                re.search(r'<script>(.*?)</script>', en, flags=re.S).group(1),
            )

    def test_proof_tooling_is_bilingual_static_and_in_evidence_section(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            build(target)
            ro = (target / "index.html").read_text(encoding="utf-8")
            en = (target / "en/index.html").read_text(encoding="utf-8")
            expected = (
                'https://www.noir-lang.org/docs/',
                'https://barretenberg.aztec.network/docs/',
                'https://github.com/ROCSI-eu/Telemetry-Attestation-Gateway/tree/main/experiments/bounded-speed-proof-v0',
            )
            for page, title, define, verify, boundary in (
                (ro, "Cum sunt folosite Noir și Barretenberg în TAG",
                 "Noir exprimă o constrângere", "reconstruiește intrările publice",
                 "browserul nu generează și nu verifică dovezi"),
                (en, "How Noir and Barretenberg are used in TAG",
                 "Noir expresses a constraint", "reconstructs public inputs",
                 "the browser neither generates nor verifies a proof"),
            ):
                self.assertEqual(page.count('class="proof-tooling"'), 1)
                section = re.search(
                    r'<section class="proof-tooling".*?</section>', page, flags=re.S
                ).group()
                self.assertIn(title, section)
                self.assertIn(define, section)
                self.assertIn(verify, section)
                self.assertIn(boundary, section)
                self.assertIn("1.0.0-beta.26", section)
                self.assertIn("5.2.0", section)
                self.assertEqual(section.count("<li>"), 3)
                self.assertIn("canonical CBOR" if page is en else "CBOR canonic", section)
                self.assertTrue(page.index('id="technical-evidence-title"')
                                < page.index('id="proof-tooling-title"')
                                < page.index('id="scenario-title"'))
                for url in expected:
                    self.assertEqual(section.count(f'href="{url}"'), 1)
                self.assertNotIn("<script", section)
                self.assertNotIn("fetch(", section)
                self.assertIn(".toolchain-diagram{grid-template-columns:1fr", page)
            self.assertIn('aria-label="Flux experimental al dovezii, executat offline"', ro)
            self.assertIn('aria-label="Experimental proof flow, executed offline"', en)
            self.assertEqual(
                re.search(r"<script>(.*?)</script>", ro, flags=re.S).group(1),
                re.search(r"<script>(.*?)</script>", en, flags=re.S).group(1),
            )

    def test_unapproved_external_links_fail_closed(self) -> None:
        import visual_refresh
        source = CONSOLE.read_text(encoding="utf-8")
        official = "https://www.noir-lang.org/docs/"
        with patch.object(
            visual_refresh, "TECH_TOOLING",
            visual_refresh.TECH_TOOLING.replace(official, "https://tracker.invalid/docs/"),
        ):
            with self.assertRaisesRegex(ValueError, "unapproved external reference"):
                public_html(source)
        with patch.object(
            visual_refresh, "TECH_TOOLING",
            visual_refresh.TECH_TOOLING.replace(
                f'href="{official}"', f'data-url="{official}"'
            ),
        ):
            with self.assertRaisesRegex(ValueError, "single navigation link"):
                public_html(source)

    def test_educational_animation_is_bilingual_static_only_and_isolated(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            build(target)
            ro = (target / "index.html").read_text(encoding="utf-8")
            en = (target / "en/index.html").read_text(encoding="utf-8")
            for page, headline, action in (
                (ro, "ANIMAȚIE CONCEPTUALĂ", "Reia explicația"),
                (en, "CONCEPTUAL ANIMATION", "Replay explanation"),
            ):
                self.assertEqual(page.count('id="tech-animation"'), 1)
                self.assertIn('id="tech-animation-svg"', page)
                self.assertIn('aria-hidden="true"', page)
                self.assertIn('id="tech-animation-pause"', page)
                self.assertIn('id="tech-animation-replay"', page)
                self.assertIn('data-motion="paused"', page)
                self.assertIn('data-started="false"', page)
                self.assertIn('class="tech-end-signal"', page)
                self.assertIn('class="tech-transfer tech-transfer-one"', page)
                self.assertIn('class="tech-transfer tech-transfer-two"', page)
                self.assertIn('animation:tech-define 12s', page)
                self.assertIn('animation:tech-prove 12s', page)
                self.assertIn('animation:tech-verify 12s', page)
                self.assertIn('tech-animation .tech-transfer{animation:none!important}', page)
                self.assertIn(headline, page)
                self.assertIn(action, page)
                self.assertTrue(page.index('id="technical-evidence-title"')
                                < page.index('id="tech-animation"')
                                < page.index('id="scenario-title"'))
                self.assertEqual(
                    set(re.findall(r'fetch\("([^"]+)"', page)),
                    {"/evidence-results.json", "/authentic-evidence.json"},
                )
                self.assertNotIn('type="module"', page)
            self.assertIn('fără generare sau verificare în browser', ro)
            self.assertIn('no proving or verification in this browser', en)
            script = re.search(r'<script>(.*?)</script>', en, flags=re.S).group(1)
            self.assertIn('const techObserver=new IntersectionObserver', script)
            self.assertIn('document.addEventListener("visibilitychange",syncTechAnimation)', script)
            self.assertIn('motionPreference.addEventListener("change",()=>{', script)
            self.assertIn('techEnd.addEventListener("animationend",event=>{', script)
            self.assertNotIn('setInterval(', script)
            self.assertNotIn('setTimeout(', script)
            self.assertEqual(script,
                             re.search(r'<script>(.*?)</script>', ro, flags=re.S).group(1))

    def test_scenario_explanation_reuses_ten_typed_mocks_in_both_locales(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            build(target)
            ro = (target / "index.html").read_text(encoding="utf-8")
            en = (target / "en/index.html").read_text(encoding="utf-8")
            cases = set(json.loads(SCENARIOS.read_text(encoding="utf-8"))["cases"])
            for page in (ro, en):
                self.assertEqual(page.count('id="scenario"'), 1)
                self.assertEqual(page.count('id="scenario-explanation"'), 1)
                self.assertTrue(page.index('id="scenario"') < page.index('id="scenario-explanation"'))
                self.assertIn('renderScenarioInterpretation($("scenario").value,e);', page)
                script = re.search(r'<script>(.*?)</script>', page, flags=re.S).group(1)
                mappings = script.split("const scenarioInterpretations={", 1)[1].split("};", 1)[0]
                self.assertEqual(
                    set(re.findall(r'^  ([a-z_]+):\[', mappings, flags=re.M)),
                    cases,
                )
                self.assertIn("e.publication.error_code", script)
                self.assertEqual(
                    set(re.findall(r'fetch\("([^"]+)"', page)),
                    {"/evidence-results.json", "/authentic-evidence.json"},
                )
                self.assertNotIn("setInterval(", script)
                self.assertNotIn("WebSocket(", script)
                self.assertNotIn("operator-run", page)
            self.assertIn("Orchestrare simulată", ro)
            self.assertIn("Recorded orchestration mock", en)
            self.assertEqual(
                re.search(r'<script>(.*?)</script>', ro, flags=re.S).group(1),
                re.search(r'<script>(.*?)</script>', en, flags=re.S).group(1),
            )

    def test_scenario_ux_pairs_existing_selector_and_typed_results(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            build(target)
            ro = (target / "index.html").read_text(encoding="utf-8")
            en = (target / "en/index.html").read_text(encoding="utf-8")
            for page in (ro, en):
                self.assertEqual(page.count('id="scenario"'), 1)
                self.assertEqual(page.count('id="scenario-results"'), 1)
                self.assertEqual(page.count('id="scenario-active"'), 1)
                self.assertIn('aria-controls="scenario-explanation scenario-results"', page)
                self.assertIn('class="card scenario-controller"', page)
                self.assertIn('class="card scenario-results"', page)
                self.assertIn('id="scenario-active" aria-live="off"', page)
                self.assertIn('id="scenario-explanation" role="status" aria-live="polite"', page)
                self.assertIn('.scenario-results dd[data-tone="good"]', page)
                self.assertIn('.scenario-results dd[data-tone="warn"]', page)
                self.assertIn('.scenario-results dd[data-tone="neutral"]', page)
                script = re.search(r'<script>(.*?)</script>', page, flags=re.S).group(1)
                self.assertIn('$("scenario-active").textContent=', script)
                self.assertIn('$(field).dataset.tone=', script)
                for token in ('"NOT_SATISFIED"', '"NOT_RECORDED"', '"final"', '"NOT_CHECKED"'):
                    self.assertIn(token, script)
                self.assertNotIn('operator-panel', page)
                self.assertEqual(
                    set(re.findall(r'fetch\\("([^"]+)"', page)),
                    {"/evidence-results.json", "/authentic-evidence.json"},
                )
            self.assertEqual(
                re.search(r'<script>(.*?)</script>', ro, flags=re.S).group(1),
                re.search(r'<script>(.*?)</script>', en, flags=re.S).group(1),
            )

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
            self.assertIn('<h1 id="hero-title">Verifică o condiție. Păstrează restul privat.</h1>', ro)
            self.assertIn('<h1 id="hero-title">Verify the condition. Keep the rest private.</h1>', en)
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
            romanian_html(html.replace("Verify the condition. Keep the rest private.", "New untranslated text"))

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
