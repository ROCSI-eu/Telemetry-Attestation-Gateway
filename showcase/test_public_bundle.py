#!/usr/bin/env python3
"""Public-UX-Simplification: focused static and synthetic-evidence boundaries.

The former interactive scenario/technical-panel assertions were superseded by
an explicit owner decision. Source-fixture validation is retained and tested.
"""
from __future__ import annotations

import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import tempfile
import unittest

from build import (
    CONSOLE, SCENARIOS, VERIFIER, build, minimized_scenarios,
    minimized_verifier, public_html, security_headers, sha256_source,
)


class PageLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        props = dict(attrs)
        if "id" in props:
            self.ids.add(props["id"])
        if tag == "a":
            self.hrefs.append(props.get("href"))


class PublicUXTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.files = build(self.folder)
        self.ro = (self.folder / "ro/index.html").read_text(encoding="utf-8")
        self.en = (self.folder / "en/index.html").read_text(encoding="utf-8")
        self.research_ro = (self.folder / "ro/research/index.html").read_text(encoding="utf-8")
        self.research_en = (self.folder / "en/research/index.html").read_text(encoding="utf-8")

    def test_bilingual_three_stage_sequence_and_confirmed_results(self):
        for page, stage, title, proof, verification, progress in (
            (self.ro, "Telemetrie → dovadă criptografică → verificare",
             "Trei etape confirmate prin teste sintetice de laborator",
             "Dovadă ZKP generată", "Verificare independentă reușită", "Explorează cercetarea"),
            (self.en, "Telemetry → cryptographic proof → verification",
             "Three steps confirmed in synthetic laboratory tests",
             "ZKP generated", "Independent verification passed", "Explore the research"),
        ):
            for required in (stage, title, proof, verification, progress, 'id="demonstration"',
                             'id="results"', 'id="principle"', 'id="hero-title"',
                             'id="concept-cinema"', 'class="hero-scene"',
                             '20s linear infinite'):
                self.assertIn(required, page)
            self.assertNotIn('GitHub Actions', page)
            self.assertNotIn('Qube', page)
            self.assertNotIn('class="research-journal"', page)
            self.assertEqual(page.count('class="public-progress"'), 1)
            self.assertEqual(page.count('class="public-step"'), 3)
            self.assertEqual(page.count('class="public-result"'), 3)
            self.assertLess(page.index('id="hero-title"'), page.index('id="demonstration"'))
            self.assertLess(page.index('id="demonstration"'), page.index('id="results"'))
        self.assertIn("Verificăm respectarea unei condiții fără să dezvăluim datele din spatele ei", self.ro)
        self.assertIn("We check whether a condition is met without revealing the data behind it", self.en)

    def test_no_technical_controls_panel_or_executable_replay(self):
        for page in (self.ro, self.en):
            for forbidden in ('<script', '<details', '<select', '<button', '<form',
                              'id="scenario"', 'scenario-explanation', 'authentic-panel',
                              'mission-pattern', 'A0_SYNTHETIC', '>VALID<', '>INVALID<',
                              'evidence-results.json', 'authentic-evidence.json',
                              'fetch(', 'operator-panel', 'private speed:', 'data-token'):
                self.assertNotIn(forbidden, page)
            self.assertEqual(page.count('https://github.com/'), 1)
            self.assertIn('prefers-reduced-motion:reduce', page)
            self.assertIn('EXPERIMENTAL', page)
            self.assertIn('SYNTHETIC ONLY' if page == self.en else 'DOAR DATE SINTETICE', page)

    def test_navigation_all_anchors_resolve_and_one_github_link(self):
        for page in (self.ro, self.en):
            parsed = PageLinks()
            parsed.feed(page)
            for href in parsed.hrefs:
                self.assertTrue(href)
                if href.startswith('#'):
                    self.assertIn(href[1:], parsed.ids)
            self.assertEqual(len([v for v in parsed.hrefs if v.startswith('https://github.com/')]), 1)
            self.assertEqual(page.count('href="#demonstration"'), 2)
            self.assertNotIn('href="#mission-control"', page)
            self.assertNotIn('href="#research"', page)

    def test_synthetic_truth_limits_are_plain_and_bilingual(self):
        self.assertIn('nu autenticitatea telemetriei de zbor', self.ro)
        self.assertIn('not authentic flight telemetry', self.en)
        self.assertIn('href="/ro/research/"', self.ro)
        self.assertIn('href="/en/research/"', self.en)
        self.assertIn('autoritate temporală simulată', self.ro)
        self.assertIn('simulated time authority', self.en)
        self.assertIn('Restoring valid historical state defeats this protection', self.research_en)
        self.assertIn('Restaurarea unei stări istorice valide anulează protecția', self.research_ro)
        self.assertIn('not physical capture time', self.research_en)
        self.assertIn('nu momentul fizic al observației', self.research_ro)
        self.assertIn('mock proof verifier', self.research_en)
        self.assertIn('verificator de dovezi simulat', self.research_ro)
        self.assertIn('not authenticated by the browser', self.research_en)
        self.assertIn('neautentificată de browser', self.research_ro)
        self.assertIn('JSON', self.ro)
        self.assertIn('JSON', self.en)
        self.assertIn('does not authenticate its source, timestamp or the full mission', self.en)
        self.assertIn('nu autentifică sursa, marcajul temporal sau întreaga misiune', self.ro)

    def test_bundle_is_static_no_replay_artifacts_and_safe_rebuild(self):
        expected = {
            'ro/index.html', 'en/index.html', 'ro/research/index.html',
            'en/research/index.html', '404.html', 'en/404.html',
            'assets/favicon.svg', 'assets/rocsi-mark.svg', 'assets/favicon.ico',
            'assets/apple-touch-icon.png', 'og/ro.png', 'og/en.png',
            '_headers', '_redirects', 'robots.txt',
        }
        self.assertEqual(set(self.files), expected)
        self.assertEqual({p.relative_to(self.folder).as_posix() for p in self.folder.rglob('*') if p.is_file()}, expected)
        for old in ('evidence-results.json','authentic-evidence.json'):
            (self.folder / old).write_text('old unused replay', encoding='utf-8')
        self.assertEqual(set(build(self.folder)), expected)
        for old in ('evidence-results.json','authentic-evidence.json'):
            self.assertFalse((self.folder / old).exists())

    def test_csp_no_script_tracking_or_remote_connections(self):
        headers = (self.folder / '_headers').read_text(encoding='utf-8')
        for label in ("script-src 'none'", "connect-src 'none'", "default-src 'none'",
                      "style-src-attr 'none'", 'X-Robots-Tag: noindex',
                      'geolocation=()','frame-ancestors \'none\''):
            self.assertIn(label, headers)
        style = re.search(r'<style>(.*?)</style>', self.en, re.S).group(1)
        self.assertIn(sha256_source(style), headers)
        self.assertEqual(headers, security_headers(self.ro, self.research_ro))
        self.assertEqual(headers, security_headers(self.en, self.research_en))
        for page in (self.en, self.ro):
            self.assertIn('name="robots" content="noindex,nofollow"', page)
            self.assertNotIn('analytics', page.lower())
            self.assertNotIn('localStorage', page)

    def test_root_routing_social_assets_and_brand(self):
        self.assertEqual((self.folder / '_redirects').read_text(), '/ /ro/ 301\n')
        for page,lang in ((self.ro,'ro'),(self.en,'en')):
            self.assertIn('<html lang="'+lang+'">', page)
            self.assertIn('<meta property="og:', page)
            self.assertIn('rocsi-mark.svg', page)
            self.assertIn('TAG', page)
        for filename in ('og/ro.png','og/en.png'):
            self.assertTrue((self.folder / filename).read_bytes().startswith(b'\x89PNG\r\n\x1a\n'))
        for name in ('404.html','en/404.html'):
            self.assertIn('noindex', (self.folder / name).read_text().lower())

    def test_original_console_and_evidence_remain_source_only(self):
        original = CONSOLE.read_text(encoding='utf-8')
        self.assertIn('id="scenario"', original)
        self.assertIn('id="operator-panel"', original)
        cases = minimized_scenarios(json.loads(SCENARIOS.read_text(encoding='utf-8')))
        proof = minimized_verifier(json.loads(VERIFIER.read_text(encoding='utf-8')))
        self.assertEqual(len(cases['cases']), 10)
        self.assertIn(proof['cryptographic'], ('VALID','INVALID','NOT_CHECKED'))
        self.assertFalse((self.folder / 'evidence-results.json').exists())
        self.assertFalse((self.folder / 'authentic-evidence.json').exists())

    def test_fixture_fail_closed_against_injected_data(self):
        source = json.loads(SCENARIOS.read_text(encoding='utf-8'))
        source['unexpected_private_field'] = 'secret'
        with self.assertRaises(ValueError):
            minimized_scenarios(source)
        verifier = json.loads(VERIFIER.read_text(encoding='utf-8'))
        verifier['unexpected_private_field'] = 'secret'
        with self.assertRaises(ValueError):
            minimized_verifier(verifier)

    def test_research_module_static_bilingual_and_linked(self):
        from build import load_research_journal
        journal = load_research_journal()
        headers = (self.folder / '_headers').read_text()
        for page, lang in ((self.research_ro, 'ro'), (self.research_en, 'en')):
            self.assertIn('<html lang="'+lang+'">', page)
            self.assertEqual(page.count('class="r-entry"'), len(journal["entries"]))
            self.assertEqual(page.count('<details class="r-demo">'), 3)
            self.assertIn('href="/'+lang+'/"', page)
            self.assertIn('href="/ro/research/"', page)
            self.assertIn('href="/en/research/"', page)
            self.assertIn('name="robots" content="noindex,nofollow"', page)
            self.assertIn(sha256_source(re.search(r'<style>(.*?)</style>', page, re.S).group(1)), headers)
            for entry in journal["entries"]:
                self.assertIn('id="'+entry["id"]+'"', page)
                self.assertIn(entry["evidence_path"], page)
            for forbidden in ('<script', '<form', '<button', 'fetch(', 'localStorage',
                              'operator-panel', 'evidence-results.json', 'authentic-evidence.json'):
                self.assertNotIn(forbidden, page)
            parsed = PageLinks()
            parsed.feed(page)
            for href in parsed.hrefs:
                if href.startswith('#'):
                    self.assertIn(href[1:], parsed.ids)
        self.assertIn('Simulated cryptographic result', self.research_en)
        self.assertIn('Rezultat criptografic simulat', self.research_ro)

    def test_interval_coverage_finding_is_research_only(self):
        for page, overview, title, limit, proof_limit in (
            (self.research_ro, self.ro, "Completitudinea unei secvențe sintetice",
             "nu la intervalul fizic", "Nu am generat o dovadă ZKP pentru întreaga secvență"),
            (self.research_en, self.en, "Completeness of a synthetic observation sequence",
             "not the physical interval", "No ZKP was generated for the entire sequence"),
        ):
            self.assertIn('id="synthetic-interval-coverage"', page)
            self.assertIn(title, page)
            self.assertIn(limit, page)
            self.assertIn(proof_limit, page)
            self.assertNotIn(title, overview)
            self.assertNotIn('synthetic-interval-coverage', overview)

    def test_interval_continuity_research_finding(self):
        from build import load_research_journal
        journal = load_research_journal()
        self.assertEqual(journal["entries"][7]["id"], "synthetic-interval-continuity")
        for page, overview, title, mock, limitation, proof_limit in (
            (self.research_ro, self.ro, "Continuitatea între intervale sintetice",
             "verificator de dovezi simulat", "nu observația fizică",
             "Nu am generat o dovadă ZKP agregată"),
            (self.research_en, self.en, "Continuity between synthetic intervals",
             "mock proof verifier", "not physical observation",
             "No aggregate ZKP was generated"),
        ):
            self.assertIn('id="synthetic-interval-continuity"', page)
            self.assertIn(title, page)
            self.assertIn(mock, page)
            self.assertIn(limitation, page)
            self.assertIn(proof_limit, page)
            self.assertNotIn(title, overview)
            self.assertNotIn("synthetic-interval-continuity", overview)

    def test_interval_recovery_research_finding(self):
        from build import load_research_journal
        journal = load_research_journal()
        self.assertEqual(journal["entries"][8]["id"], "synthetic-interval-recovery")
        for page, overview, title, mock, gap, physical, proof in (
            (self.research_ro, self.ro, "Reluarea după o întrerupere a secvenței",
             "verificator de dovezi simulat", "Reluarea nu șterge intervalul lipsă",
             "nu demonstrează acoperirea fizică", "Nu am generat o dovadă ZKP agregată"),
            (self.research_en, self.en, "Resuming after a sequence interruption",
             "mock proof verifier", "Recovery does not erase the missing interval",
             "does not establish physical coverage", "No aggregate ZKP was generated"),
        ):
            for required in ('id="synthetic-interval-recovery"', title, mock, gap, physical, proof):
                self.assertIn(required, page)
            self.assertNotIn(title, overview)
            self.assertNotIn("synthetic-interval-recovery", overview)
            self.assertNotIn("Qube", page)
            self.assertNotIn("GitHub Actions", page)

    def test_state_rollback_research_finding(self):
        from build import load_research_journal
        journal = load_research_journal()
        self.assertEqual(journal["entries"][9]["id"], "synthetic-state-rollback")
        for page, overview, title, mock, limit, partial, proof in (
            (self.research_ro, self.ro, "Detectarea restaurării unei stări istorice",
             "verificator de dovezi simulat", "ambele stări sunt restaurate simultan",
             "fără recuperare automată", "Nu am generat o dovadă ZKP agregată"),
            (self.research_en, self.en, "Detecting restoration of historical state",
             "mock proof verifier", "both states are restored together",
             "without automatic recovery", "No aggregate ZKP was generated"),
        ):
            for required in ('id="synthetic-state-rollback"', title, mock, limit, partial, proof):
                self.assertIn(required, page)
            self.assertNotIn(title, overview)
            self.assertNotIn("synthetic-state-rollback", overview)
            self.assertNotIn("Qube", page)
            self.assertNotIn("GitHub Actions", page)

    def test_state_reconciliation_research_finding(self):
        from build import load_research_journal
        journal = load_research_journal()
        self.assertEqual(len(journal["entries"]), 11)
        self.assertEqual(journal["entries"][10]["id"], "synthetic-state-reconciliation")
        for page, overview, title, mock, step, limit, freshness, proof in (
            (self.research_ro, self.ro, "Reconcilierea după actualizarea parțială a stării",
             "verificator de dovezi simulat", "o singură tranziție înainte",
             "Restaurarea simultană a tuturor copiilor rămâne nedetectabilă",
             "coincidența stărilor nu dovedește actualitatea", "nu am generat o dovadă ZKP agregată"),
            (self.research_en, self.en, "Reconciliation after a partial state update",
             "mock proof verifier", "a single forward transition",
             "Restoring all copies together remains undetectable",
             "matching states do not prove freshness", "no aggregate ZKP was generated"),
        ):
            for required in ('id="synthetic-state-reconciliation"', title, mock, step, limit, freshness, proof):
                self.assertIn(required, page)
            self.assertNotIn(title, overview)
            self.assertNotIn("synthetic-state-reconciliation", overview)
            self.assertNotIn("Qube", page)
            self.assertNotIn("GitHub Actions", page)

    def test_public_source_drift_is_rejected(self):
        source = CONSOLE.read_text(encoding='utf-8')
        with self.assertRaises(ValueError):
            public_html(source.replace('<header>', '<header class="changed">', 1))


if __name__ == '__main__':
    unittest.main()
