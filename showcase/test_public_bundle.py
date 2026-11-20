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
    CASE_KEYS, CONSOLE, LABELS, SCENARIOS, VERIFIER, JOURNAL, build, load_research_journal,
    minimized_scenarios, minimized_verifier, public_html, sha256_source,
)


class StaticShowcaseTests(unittest.TestCase):
    def test_editorial_four_chapters_are_bilingual_and_technical_panels_secondary(self) -> None:
        from localization import SHARE
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            build(target)
            ro = (target / "ro/index.html").read_text(encoding="utf-8")
            en = (target / "en/index.html").read_text(encoding="utf-8")
            for page, concept, how, applications, research, title in (
                (ro, "Mai puține date expuse. O condiție verificabilă.",
                 "De la măsurarea UAS la un rezultat verificabil.",
                 "Unde ar putea conta această capacitate?",
                 "Din jurnalul de cercetare TAG", SHARE["ro"]["title"]),
                (en, "Less data exposed. A condition that can be verified.",
                 "From a UAS measurement to a verifiable result.",
                 "Where could this capability matter?",
                 "From the TAG research journal", SHARE["en"]["title"]),
            ):
                for value in (concept, how, applications, research):
                    self.assertIn(value, page)
                self.assertIn("<title>" + title + "</title>", page)
                ordered = ('id="hero-title"', 'id="primer-title"', 'id="mission-control"',
                           'id="editorial-process-title"', 'id="tech-animation"',
                           'id="use-cases-title"', 'id="research-title"',
                           'id="technical-evidence"', 'id="proof-tooling-title"',
                           'id="laboratory-scenarios"', 'id="scenario-title"',
                           'id="authentic-title"', 'id="research-limitations"',
                           'id="technical-scope"')
                self.assertEqual([page.index(marker) for marker in ordered],
                                 sorted(page.index(marker) for marker in ordered))
                self.assertEqual(page.count('class="research-detail"'), 3)
                self.assertNotIn('class="editorial-steps"', page)
                self.assertIn('class="editorial-proof-intro"', page)
                self.assertIn('id="scope-proves"', page)
                self.assertIn('id="scope-limits"', page)
                self.assertIn('class="architecture-flow"', page)
                self.assertIn("PRECOMPUTED_GENUINE_SYNTHETIC_VERIFICATION", page)
                self.assertNotIn('class="notice" role="note"', page)
                self.assertIn('id="concept-cinema" data-visibility="visible"', page)
                self.assertIn('class="concept-stage"', page)
                self.assertIn('class="concept-private-wave"', page)
                self.assertIn('class="concept-proof-ring"', page)
                self.assertIn('@keyframes concept-packet', page)
                self.assertIn('conceptObserver.observe(conceptScene)', page)
                self.assertIn('.concept-cinema[data-visibility="hidden"]', page)
                self.assertIn('.concept-cinema .concept-private-wave', page)
                self.assertIn('@media(prefers-reduced-motion:reduce)', page)
            self.assertIn('class="primer-visual"', ro)
            self.assertIn('class="primer-copy"', ro)
            self.assertIn('class="primer-visual"', en)
            self.assertNotIn('DOAR ILUSTRAȚIE', ro)
            self.assertNotIn('Conceptual animation only. No private measurement', en)
            self.assertIn('VERIFICARE SELECTIVĂ', ro)
            self.assertIn('SELECTIVE VERIFICATION', en)
            self.assertIn('CERCETARE · CONFIDENȚIALITATEA DATELOR', ro)
            self.assertIn('RESEARCH · DATA PRIVACY', en)
            self.assertIn('A0_SYNTHETIC', ro)  # Technical research, not hero status.
            self.assertIn('VALOARE PRIVATĂ', ro)
            self.assertIn('NEDEZVĂLUITĂ', ro)
            self.assertIn('INFORMAȚII PRIVATE', ro)
            self.assertIn('PUBLIC CLAIM', en)
            self.assertIn('CHECKABLE', en)
            self.assertIn('PRIVATE VALUE', en)
            self.assertIn("nu a fost încă demonstrat", ro)
            self.assertIn("has not yet been demonstrated", en)
            self.assertEqual(
                re.search(r'<script>(.*?)</script>', ro, flags=re.S).group(1),
                re.search(r'<script>(.*?)</script>', en, flags=re.S).group(1),
            )

    def test_six_potential_application_cards_are_bilingual_and_accessible(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            build(target)
            for lang, headings in (
                ("ro", (
                    "Audit și verificare", "Sisteme autonome", "Schimb de informații",
                    "Logistică și transport", "Monitorizare industrială",
                    "Cercetare colaborativă",
                )),
                ("en", (
                    "Audit and verification", "Autonomous systems",
                    "Information exchange", "Logistics and transport",
                    "Industrial monitoring", "Collaborative research",
                )),
            ):
                page = (target / lang / "index.html").read_text(encoding="utf-8")
                block = page.split('<section class="use-cases"', 1)[1].split('</section>', 1)[0]
                self.assertEqual(block.count('<article class="use-case-card">'), 6)
                self.assertEqual(block.count('class="use-case-icon-wrap"'), 6)
                self.assertEqual(block.count('class="use-case-icon"'), 6)
                self.assertEqual(block.count('viewBox="0 0 24 24"'), 6)
                self.assertEqual(block.count('aria-hidden="true" focusable="false"'), 6)
                self.assertEqual(block.count("<h3>"), 6)
                self.assertEqual(block.count("<p>"), 7)  # section intro plus six explanations
                for heading in headings:
                    self.assertEqual(block.count("<h3>" + heading + "</h3>"), 1)
                self.assertNotIn("<button", block)
                self.assertNotIn("<script", block)
                self.assertNotIn('href="', block)
                self.assertIn("grid-template-columns:repeat(3,minmax(0,1fr))", page)
                self.assertIn("grid-template-columns:repeat(2,minmax(0,1fr))", page)
                self.assertIn(".use-cases-grid{grid-template-columns:1fr;gap:12px}", page)
                self.assertIn('id="research-title"', page)

    def test_public_vertical_rhythm_and_single_separator_rules(self) -> None:
        # Presentation-only: keep one divider per chapter/accordion boundary.
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            build(target)
            for language in ("ro", "en"):
                page = (target / language / "index.html").read_text(encoding="utf-8")
                self.assertIn(
                    ".mission-control{background:transparent;border:0;border-bottom:1px solid #374245;"
                    "box-shadow:none;border-radius:0;padding:clamp(48px,5.2vw,76px) 0",
                    page,
                )
                self.assertIn(
                    ".use-cases{padding:clamp(48px,5vw,76px) 0;margin:0;border-bottom:0}",
                    page,
                )
                # A later legacy rule must not override the compact mission padding.
                self.assertNotIn(".mission-control{padding-top:clamp(75px,8vw,125px)", page)
                self.assertIn(".research-limits{padding:clamp(50px,5.5vw,82px) 0 0}", page)
                self.assertIn(
                    ".research-detail{border-top:0;border-bottom:1px solid #526165;"
                    "margin:0;padding:0",
                    page,
                )
                self.assertIn(".research-details{border-top:1px solid #526165;margin-top:0}", page)
                self.assertIn(
                    "footer{border-top:1px solid #344446;margin-top:28px;padding:22px 0 8px;line-height:1.75",
                    page,
                )
                self.assertEqual(page.count('class="research-detail"'), 3)
                self.assertEqual(page.count('class="research-entry"'), 2)
                self.assertIn('class="rocsi-affiliation"', page)

    def test_research_journal_is_bilingual_static_and_separates_open_question(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            build(target)
            for language, journal_heading, lesson, pending in (
                ("ro", "Din jurnalul de cercetare TAG", "Ce am învățat",
                 "Fluxul complet nu a fost încă demonstrat."),
                ("en", "From the TAG research journal", "What we learned",
                 "The complete end-to-end path has not yet been demonstrated."),
            ):
                page = (target / language / "index.html").read_text(encoding="utf-8")
                self.assertIn(journal_heading, page)
                self.assertEqual(page.count('class="research-entry"'), 2)
                self.assertEqual(page.count('class="research-entry-insight"'), 2)
                self.assertIn(lesson, page)
                self.assertIn(pending, page)
                self.assertIn('class="research-next-question"', page)
                self.assertLess(page.index('class="research-journal"'),
                                page.index('class="research-next-question"'))
                self.assertLess(page.index('class="research-next-question"'),
                                page.index('id="technical-evidence"'))
                self.assertEqual(page.count('class="research-detail"'), 3)
                self.assertNotIn("TAG_RESEARCH_JOURNAL", page)
                self.assertEqual(set(re.findall(r'fetch\("([^"]+)"', page)),
                                 {"/evidence-results.json", "/authentic-evidence.json"})
            self.assertEqual(
                re.search(r'<script>(.*?)</script>', (target / "ro/index.html").read_text(), flags=re.S).group(1),
                re.search(r'<script>(.*?)</script>', (target / "en/index.html").read_text(), flags=re.S).group(1),
            )

    def test_journal_rejects_unapproved_claims_and_unsafe_evidence(self) -> None:
        original = json.loads(JOURNAL.read_text(encoding="utf-8"))
        altered = copy.deepcopy(original)
        altered["entries"][0]["status"] = "production_validated"
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "journal.json"
            path.write_text(json.dumps(altered), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unapproved journal entry"):
                load_research_journal(path)
            altered = copy.deepcopy(original)
            altered["entries"][0]["evidence_path"] = "../private.txt"
            path.write_text(json.dumps(altered), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "invalid journal evidence reference"):
                load_research_journal(path)
            altered = copy.deepcopy(original)
            altered["entries"][0]["ro"]["title"] = "<script>alert(1)</script>"
            path.write_text(json.dumps(altered), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unsafe public journal text"):
                load_research_journal(path)

    def test_architecture_replaces_route_selector_with_one_research_flow(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            build(target)
            for lang, title, warning in (
                ("ro", "De la măsurarea UAS la un rezultat verificabil.",
                 "Integrarea UAS–TAG–C2 rămâne un obiectiv de cercetare."),
                ("en", "From a UAS measurement to a verifiable result.",
                 "The combined UAS–TAG–C2 flow remains a research objective."),
            ):
                page = (target / lang / "index.html").read_text(encoding="utf-8")
                self.assertIn(title, page)
                self.assertIn(warning, page)
                self.assertIn('class="architecture-flow"', page)
                self.assertEqual(page.count('class="architecture-node"'), 2)
                self.assertEqual(page.count('class="architecture-node architecture-node-tag"'), 1)
                self.assertEqual(page.count('class="architecture-link'), 2)
                for obsolete in ('id="mission-pattern"', 'id="mission-scene-status"',
                                 'class="mission-speed-example"', 'const routeDescriptions=',
                                 'startMissionScene()', 'mission.dataset.scene='):
                    self.assertNotIn(obsolete, page)
                self.assertIn('id="editorial-process-title"', page)
                self.assertIn('id="tech-animation"', page)
                self.assertIn('id="laboratory-scenarios"', page)
                self.assertIn('PRECOMPUTED_GENUINE_SYNTHETIC_VERIFICATION', page)
                self.assertIn('NO-GO', page)

    def test_visual_final_remains_synthetic_bilingual_and_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            build(target)
            ro = (target / "ro/index.html").read_text(encoding="utf-8")
            en = (target / "en/index.html").read_text(encoding="utf-8")
            for page, words in (
                (ro, ("TRASEU SINTETIC", "01 / CONDIȚIE", "03 / VERIFICARE")),
                (en, ("SYNTHETIC ROUTE", "01 / CONDITION", "03 / CHECK")),
            ):
                self.assertIn('class="hero-scene"', page)
                self.assertIn('class="hero-vehicle"', page)
                self.assertIn('<svg class="hero-scene" viewBox="0 0 760 700" preserveAspectRatio="xMidYMid meet" focusable="false" aria-hidden="true">', page)
                self.assertIn('class="hero-art"', page)
                self.assertNotIn('class="hero-visual"', page)
                self.assertNotIn('hero-art-caption', page)
                self.assertNotIn('Reperele A–B–C ilustrează', page)
                self.assertNotIn('The A–B–C markers illustrate', page)
                self.assertNotIn('not a cryptographic proof', page)
                self.assertNotIn('class="hero-art-index"', page)
                self.assertNotIn('OBS / 02', page)
                self.assertNotIn('ROUTE / SYN', page)
                self.assertNotIn('TRASEU / SINT', page)
                self.assertNotIn('PRIVATE DATA · VERIFIABLE CONDITIONS', page)
                self.assertNotIn('DATE PRIVATE · CONDIȚII VERIFICABILE', page)
                self.assertNotIn('class="editorial-steps"', page)
                self.assertIn('aria-hidden="true"', page)
                self.assertIn('class="research-journal"', page)
                self.assertIn('prefers-reduced-motion:reduce', page)
                for item in words:
                    self.assertIn(item, page)
                self.assertNotIn('class="hero-axis"', page)
            self.assertIn('class="concept-cinema"', ro)
            self.assertEqual(
                re.search(r'<script>(.*?)</script>', ro, flags=re.S).group(1),
                re.search(r'<script>(.*?)</script>', en, flags=re.S).group(1),
            )

    def test_cinematic_hero_is_decorative_bilingual_and_reduced_motion_safe(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            build(target)
            scenes = []
            for language in ("ro", "en"):
                page = (target / language / "index.html").read_text(encoding="utf-8")
                match = re.search(r'<svg class="hero-scene".*?</svg>', page, flags=re.S)
                self.assertIsNotNone(match)
                scene = match.group()
                scenes.append(scene)
                self.assertIn('class="hero-vehicle"', scene)
                self.assertIn('class="hero-route-flow"', scene)
                self.assertIn('class="hero-sweep"', scene)
                self.assertEqual(scene.count('class="hero-rotor-disc"'), 4)
                self.assertEqual(scene.count('class="hero-beacon-pulse"'), 2)
                self.assertNotIn("<image", scene)
                self.assertNotIn("<foreignObject", scene)
                self.assertNotIn("http://", scene)
                self.assertNotIn("https://", scene)
                self.assertIn("@keyframes hero-hover", page)
                self.assertIn("@keyframes hero-propeller", page)
                self.assertIn("@keyframes hero-radar-sweep", page)
                self.assertIn("@media(prefers-reduced-motion:reduce)", page)
                self.assertIn(".hero-vehicle,.hero-floor-shadow,.hero-sweep,.hero-route-flow,.hero-rotor-disc,.hero-beacon-pulse{animation:none!important;will-change:auto}", page)
                self.assertIn("A0_SYNTHETIC", page)
                self.assertIn("SYNTHETIC_ONLY", page)
            # The illustration SVG now has no locale-specific callouts. Its
            # geometric animation remains identical in both languages.
            self.assertEqual(scenes[0].casefold(), scenes[1].casefold())

    def test_proof_tooling_is_bilingual_static_and_in_evidence_section(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            build(target)
            ro = (target / "ro/index.html").read_text(encoding="utf-8")
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
                self.assertTrue(page.index('id="technical-evidence"')
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

    def test_evidence_checkpoint_separates_sitl_and_offline_zk_in_both_locales(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            build(target)
            ro = (target / "ro/index.html").read_text(encoding="utf-8")
            en = (target / "en/index.html").read_text(encoding="utf-8")
            for page, heading, sitl, proof, incomplete in (
                (ro, "SITL și dovada offline: rezultate distincte", "normalizarea TAG", "rezultatul VALID",
                 "nedemonstrat integral"),
                (en, "SITL and offline proof: distinct evidence", "TAG normalization", "offline verifier VALID",
                 "not demonstrated end to end"),
            ):
                section = re.search(
                    r'<aside class="proof-evidence-checkpoint".*?</aside>', page,
                    flags=re.S,
                )
                self.assertIsNotNone(section)
                checkpoint = section.group()
                self.assertIn(heading, checkpoint)
                self.assertIn(sitl, checkpoint)
                self.assertIn(proof, checkpoint)
                self.assertIn(incomplete, checkpoint)
                self.assertEqual(checkpoint.count("<p>"), 3)
                self.assertIn("PASS", checkpoint)
                self.assertIn("NO-GO", checkpoint)
                self.assertIn("600 cm/s", checkpoint)
                self.assertIn("SITL", checkpoint)
                self.assertLess(page.index('id="technical-evidence"'),
                                page.index('id="proof-evidence-checkpoint-title"'))
                self.assertLess(page.index('id="proof-evidence-checkpoint-title"'),
                                page.index('id="scenario-title"'))
                self.assertNotIn("<script", checkpoint)
            self.assertIn("A0_SYNTHETIC", ro)
            self.assertIn("A0_SYNTHETIC", en)

    def test_rocsi_affiliation_and_contact_links_are_bilingual_and_navigation_only(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            build(target)
            for lang, brand, contact, home, heading, cta in (
                ("ro", "O inițiativă de cercetare ROCSI",
                 "https://rocsi.eu/ro/contact", "https://rocsi.eu/ro",
                 "TAG este o inițiativă de cercetare ROCSI.", "Programează o conversație"),
                ("en", "A ROCSI research initiative",
                 "https://rocsi.eu/en/contact", "https://rocsi.eu/en",
                 "TAG is a research initiative of ROCSI.", "Start a conversation"),
            ):
                page = (target / lang / "index.html").read_text(encoding="utf-8")
                self.assertIn(brand, page)
                self.assertIn(heading, page)
                self.assertEqual(page.count(f'href="{contact}"'), 1)
                self.assertEqual(page.count(f'href="{home}"'), 1)
                self.assertIn(f'class="header-cta" href="{contact}">{cta}</a>', page)
                self.assertIn('class="rocsi-affiliation"', page)
                self.assertIn('class="language-switch"', page)
                self.assertEqual(page.count('src="/assets/rocsi-mark.svg"'), 2)
                self.assertIn('<img class="brand-rocsi-mark" src="/assets/rocsi-mark.svg" alt="" width="34" height="34"', page)
                self.assertIn('<img class="rocsi-affiliation-mark" src="/assets/rocsi-mark.svg" alt="" width="60" height="60"', page)
                self.assertIn('class="rocsi-affiliation-actions"', page)
                self.assertIn('.brand-rocsi-mark{display:block;width:34px;height:34px;', page)
                self.assertIn('.rocsi-affiliation-mark{display:block;width:60px;height:60px;', page)
                self.assertIn('.rocsi-affiliation-mark{width:48px;height:48px}', page)
                self.assertEqual(page.count('class="rocsi-affiliation"'), 1)
                self.assertIn('<aside class="rocsi-affiliation" aria-labelledby="rocsi-affiliation-title">', page)
                self.assertIn('<h3 id="rocsi-affiliation-title">', page)
                card_position = page.index('<aside class="rocsi-affiliation"')
                footer_position = page.index('<footer id="console-footer">')
                self.assertLess(page.index('id="research-limitations"'), card_position)
                self.assertLess(card_position, footer_position)
                self.assertNotIn('rocsi-affiliation', page[footer_position:page.index('</footer>', footer_position)])
                self.assertIn('grid-template-columns:minmax(0,1fr) auto', page)
                self.assertIn('background:linear-gradient(120deg,#17292c,#101c1f)', page)
                self.assertIn('footer{border-top:1px solid #344446;margin-top:28px;', page)
                self.assertNotIn("<iframe", page)
                self.assertNotIn("cal.com", page)
                self.assertEqual(
                    set(re.findall(r'fetch\("([^"]+)"', page)),
                    {"/evidence-results.json", "/authentic-evidence.json"},
                )
            self.assertEqual(
                re.search(r'<script>(.*?)</script>', (target / "ro/index.html").read_text(), flags=re.S).group(1),
                re.search(r'<script>(.*?)</script>', (target / "en/index.html").read_text(), flags=re.S).group(1),
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
            ro = (target / "ro/index.html").read_text(encoding="utf-8")
            en = (target / "en/index.html").read_text(encoding="utf-8")
            for page, headline, labels in (
                (ro, "De la informație privată la rezultat verificabil", ("01 / CONDIȚIE", "02 / DOVADĂ", "03 / VERIFICARE")),
                (en, "From private data to a verifiable result", ("01 / CONDITION", "02 / PROOF", "03 / CHECK")),
            ):
                self.assertEqual(page.count('id="tech-animation"'), 1)
                self.assertIn('id="tech-animation-svg"', page)
                self.assertIn('class="tech-scene-scroll" tabindex="0"', page)
                self.assertIn('aria-hidden="true"', page)
                self.assertIn('data-started="true" data-visibility="visible"', page)
                for removed in ('id="tech-animation-pause"', 'id="tech-animation-replay"',
                                'id="mission-replay"', 'id="mission-motion-toggle"'):
                    self.assertNotIn(removed, page)
                self.assertIn('class="tech-panel-depth"', page)
                self.assertIn('class="tech-highlight tech-highlight-one"', page)
                self.assertIn('class="tech-highlight tech-highlight-two"', page)
                self.assertIn('class="tech-highlight tech-highlight-three"', page)
                self.assertIn('class="tech-transfer tech-transfer-one"', page)
                self.assertIn('class="tech-transfer tech-transfer-two"', page)
                self.assertIn('animation:tech-cycle-one 15s', page)
                self.assertIn('animation:tech-cycle-two 15s', page)
                self.assertIn('animation:tech-cycle-three 15s', page)
                self.assertIn('animation:none!important', page)
                self.assertIn(headline, page)
                for label in labels:
                    self.assertIn(label, page)
                for duplicate in ('class="tech-animation-top"', 'class="tech-animation-caption"',
                                  'id="tech-animation-status"', 'PROOF WORKFLOW', 'PROCESUL DOVEZII',
                                  '01 / NOIR', '02 / BARRETENBERG', '03 / OFFLINE'):
                    self.assertNotIn(duplicate, page)
                self.assertTrue(page.index('id="mission-control"')
                                < page.index('id="tech-animation"')
                                < page.index('id="use-cases-title"'))
                self.assertEqual(
                    set(re.findall(r'fetch\("([^"]+)"', page)),
                    {"/evidence-results.json", "/authentic-evidence.json"},
                )
                self.assertNotIn('type="module"', page)
            self.assertIn('TAG cercetează cum poate fi verificată o condiție', ro)
            self.assertIn('TAG studies how a defined condition can be checked', en)
            script = re.search(r'<script>(.*?)</script>', en, flags=re.S).group(1)
            self.assertIn('const techObserver=new IntersectionObserver', script)
            self.assertIn('document.addEventListener("visibilitychange",syncTechAnimation)', script)
            self.assertNotIn('const techStatus=$("tech-animation-status")', script)
            self.assertIn('techAnimation.dataset.started="true"', script)
            self.assertNotIn('techReplay', script)
            self.assertNotIn('techPause', script)
            self.assertNotIn('setInterval(', script)
            self.assertNotIn('setTimeout(', script)
            self.assertEqual(script,
                             re.search(r'<script>(.*?)</script>', ro, flags=re.S).group(1))

    def test_scenario_explanation_reuses_ten_typed_mocks_in_both_locales(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            build(target)
            ro = (target / "ro/index.html").read_text(encoding="utf-8")
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
            ro = (target / "ro/index.html").read_text(encoding="utf-8")
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
                self.assertIn('positive.includes(value)?"good":caution.includes(value)?"warn":"neutral"', script)
                for token in ('"NOT_SATISFIED"', '"NOT_RECORDED"', '"final"'):
                    self.assertIn(token, script)
                self.assertNotIn('operator-panel', page)
                self.assertEqual(
                    set(re.findall(r'fetch\("([^"]+)"', page)),
                    {"/evidence-results.json", "/authentic-evidence.json"},
                )
            self.assertEqual(
                re.search(r'<script>(.*?)</script>', ro, flags=re.S).group(1),
                re.search(r'<script>(.*?)</script>', en, flags=re.S).group(1),
            )

    def test_frozen_bundle_has_only_fifteen_allowlisted_files(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            self.assertEqual(set(build(target)), {
                "ro/index.html", "en/index.html", "404.html", "en/404.html",
                "evidence-results.json", "authentic-evidence.json", "_headers", "_redirects",
                "robots.txt", "assets/favicon.svg", "assets/rocsi-mark.svg", "assets/favicon.ico", "assets/apple-touch-icon.png",
                "og/ro.png", "og/en.png",
            })
            html = (target / "ro/index.html").read_text(encoding="utf-8")
            self.assertIn('lang="ro"', html)
            self.assertIn("Centru de comandă și control", html)
            self.assertIn("TELEMETRIE CU PROTECȚIA DATELOR", html)
            self.assertIn("telemetrie sintetică → normalizare → dovadă → verificare independentă → publicare opțională", html)
            self.assertIn("ARHITECTURĂ ÎN CERCETARE", html)
            self.assertIn("Fără comenzi MAVLink, controlul navigației", html)
            # The banner is localized for visitors; immutable protocol labels
            # remain exact in the exported evidence contracts.
            scenario_labels = json.loads((target / "evidence-results.json").read_text())["labels"]
            proof_labels = json.loads((target / "authentic-evidence.json").read_text())["labels"]
            for label in LABELS:
                self.assertIn(label, scenario_labels)
                self.assertIn(label, proof_labels)
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

    def test_root_redirects_to_romanian_canonical_page(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            build(target)
            self.assertEqual(
                (target / "_redirects").read_text(encoding="utf-8"),
                "/ /ro/ 301\n",
            )
            self.assertTrue((target / "ro/index.html").is_file())
            self.assertFalse((target / "index.html").exists())
            html = (target / "ro/index.html").read_text(encoding="utf-8")
            self.assertIn('<link rel="canonical" href="https://tag.rocsi.eu/ro/">', html)
            self.assertIn('<link rel="alternate" hreflang="ro" href="https://tag.rocsi.eu/ro/">', html)
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
            self.assertEqual(re.findall(r'href="([^"]+)"', page), ["/ro/", "/en/"])
            en_page = (target / "en/404.html").read_text()
            self.assertIn('lang="en"', en_page)
            self.assertIn("Page not found", en_page)
            self.assertEqual(re.findall(r'href="([^"]+)"', en_page), ["/en/", "/ro/"])
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
            ro = (target / "ro/index.html").read_text(encoding="utf-8")
            en = (target / "en/index.html").read_text(encoding="utf-8")
            self.assertIn('<html lang="ro">', ro)
            self.assertIn('<html lang="en">', en)
            self.assertIn('<h1 id="hero-title">Verifică o condiție. Păstrează restul privat.</h1>', ro)
            self.assertIn('<h1 id="hero-title">Verify the condition. Keep the rest private.</h1>', en)
            self.assertIn('class="architecture-flow"', ro)
            self.assertIn('class="architecture-flow"', en)
            self.assertNotIn('id="mission-motion-toggle"', ro)
            self.assertNotIn('id="mission-replay"', en)
            self.assertIn('href="/ro/" hreflang="ro" lang="ro" aria-current="page"', ro)
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
                self.assertIn(f'<link rel="canonical" href="{ORIGIN}{"/ro/" if language=="ro" else "/en/"}">', page)
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
            rocsi_mark = (target / "assets/rocsi-mark.svg").read_text(encoding="utf-8")
            self.assertIn('viewBox="0 0 64 64"', rocsi_mark)
            self.assertIn('stroke="#ffd126"', rocsi_mark)
            self.assertIn('stroke="#ef3340"', rocsi_mark)
            self.assertIn('role="img" aria-label="ROCSI"', rocsi_mark)
            self.assertNotIn("<script", rocsi_mark)
            self.assertNotIn("href=", rocsi_mark)
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
        source = CONSOLE.read_text(encoding="utf-8")
        self.assertIn('id="mission-motion-toggle"', source)
        self.assertIn('id="mission-replay"', source)
        for obsolete in ('id="mission-pattern"', 'id="mission-replay"',
                         'id="mission-motion-toggle"', 'id="mission-scene-status"',
                         'const routeDescriptions=', 'startMissionScene();'):
            self.assertNotIn(obsolete, html)
        self.assertIn('class="architecture-panel"', html)
        self.assertIn('architecture-packet', html)
        self.assertIn('@keyframes architecture-packet-down', html)
        self.assertIn('@media(prefers-reduced-motion:reduce){.architecture-link:after{animation:none!important', html)
        script = re.search(r'<script>(.*?)</script>', html, flags=re.S).group(1)
        self.assertNotIn("mission-pattern", script)
        self.assertNotIn("mission-craft", script)
        self.assertNotIn("setInterval(", script)
        self.assertIn('SYNTHETIC_ONLY', html)

    def test_strict_csp_hashes_match_inline_code(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            build(Path(folder))
            target = Path(folder)
            html = (target / "ro/index.html").read_text(encoding="utf-8")
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
