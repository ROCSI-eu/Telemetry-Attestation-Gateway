#!/usr/bin/env python3
"""Build a strictly static, minimized public Mission Control showcase.

EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC
NOT VALIDATION OR PRODUCTION AUTHORIZATION

This builder never invokes a CLI, verifier, network service, or operator endpoint.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
from html import escape
import json
from pathlib import Path, PurePosixPath
import re

from localization import inject_locale_js, localize_404, romanian_html, social_metadata
from visual_refresh import redesign_public_html

ROOT = Path(__file__).resolve().parents[1]
JOURNAL = ROOT / "showcase/research_journal.json"
JOURNAL_MARKER = "<!-- TAG_RESEARCH_JOURNAL -->"
CONSOLE = ROOT / "experiments/web-console-v0/index.html"
SCENARIOS = ROOT / "experiments/integrated-cli-v0/evidence-results.json"
# Static navigation only. The public bundle still rejects every other external URL.
PUBLIC_REFERENCE_URLS = frozenset({
    "https://www.noir-lang.org/docs/",
    "https://barretenberg.aztec.network/docs/",
    "https://rocsi.eu/en",
    "https://rocsi.eu/en/contact",
    "https://github.com/ROCSI-eu/Telemetry-Attestation-Gateway/tree/main/experiments/bounded-speed-proof-v0",
})
VERIFIER = ROOT / "experiments/web-console-v0/authentic-evidence.json"
LABELS = [
    "EXPERIMENTAL", "SYNTHETIC_ONLY", "A0_SYNTHETIC",
    "NOT VALIDATION OR PRODUCTION AUTHORIZATION",
]
SCENARIO_NAMES = {
    "altered_public_input", "below_limit_local_publication",
    "equality_publication_disabled", "malformed_source", "over_limit",
    "publication_definitive_failure", "publication_timeout_retry_reconciliation",
    "publication_unavailable", "tampered_proof", "unsupported_public_version",
}
CASE_KEYS = {
    "assurance", "claim", "command_path", "cryptographic", "proof_generation",
    "publication", "relying_party_decision", "restricted_fields_disclosed",
    "source", "source_trust", "verification_input",
}
PUBLICATION_KEYS = {"attempts", "error_code", "mode", "reconciled", "state"}
CASE_ENUMS = {
    "assurance": {"A0_SYNTHETIC"},
    "claim": {"SATISFIED", "NOT_SATISFIED", "NOT_EVALUATED"},
    "command_path": {"NONE"},
    "cryptographic": {"VALID", "INVALID", "NOT_CHECKED"},
    "proof_generation": {"GENERATED", "NOT_ATTEMPTED"},
    "relying_party_decision": {"NOT_MADE"},
    "source": {"NORMALIZED", "REJECTED"},
    "source_trust": {"UNSIGNED", "NOT_EVALUATED"},
    "verification_input": {"ACCEPTED", "REJECTED", "NOT_CHECKED"},
}
PUBLICATION_ENUMS = {
    "error_code": {
        None, "CLAIM_NOT_ELIGIBLE", "SOURCE_NOT_ELIGIBLE",
        "VERIFICATION_NOT_VALID", "PUBLICATION_DISABLED",
        "SUBSTRATE_REJECTED", "SUBSTRATE_UNAVAILABLE",
    },
    "mode": {"local", "disabled"},
    "state": {"final", "failed", "NOT_PERFORMED", "NOT_RECORDED"},
}
AUTHENTIC_FIXED = {
    "schema_version": "TAG_PRECOMPUTED_SYNTHETIC_VERIFIER_REPLAY_V0_EXPERIMENTAL",
    "evidence_kind": "PRECOMPUTED_GENUINE_SYNTHETIC_VERIFICATION",
    "verification_basis": "INDEPENDENT_OFFLINE_CHECK_AT_EXPORT",
    "verification_input": "ACCEPTED",
    "proof_generation": "NOT_OBSERVED",
    "source_trust": "NOT_EVALUATED",
    "assurance": "A0_SYNTHETIC",
    "policy": "NOT_EVALUATED",
    "freshness": "NOT_EVALUATED",
    "revocation": "NOT_EVALUATED",
    "replay": "NOT_EVALUATED",
    "publication": "NOT_PERFORMED",
    "relying_party_decision": "NOT_MADE",
    "command_path": "NONE",
    "private_fields_disclosed": False,
    "browser_verified": False,
    "proof_validity_is_telemetry_truth": False,
}


def exact_fields(value: object, fields: set[str], context: str) -> dict:
    if type(value) is not dict or set(value) != fields:
        raise ValueError("incompatible public fields: " + context)
    return value


def minimized_scenarios(source: dict) -> dict:
    exact_fields(source, {
        "boundaries", "cases", "evidence_kind", "evidence_note",
        "experiment", "labels",
    }, "source")
    if (source["labels"] != LABELS
        or source["experiment"] != "integrated-cli-v0"
        or source["evidence_kind"] != "deterministic orchestration/control-flow evidence"):
        raise ValueError("unrecognized orchestration evidence provenance")
    boundaries = exact_fields(source["boundaries"], {
        "exact_normalized_speed_disclosed", "hardware_required",
        "mavlink_command_path", "network_required", "private_witness_disclosed",
        "raw_telemetry_disclosed", "relying_party_business_decision",
        "stable_identity_disclosed",
    }, "boundaries")
    if any(value is not False for value in boundaries.values()):
        raise ValueError("source evidence boundary is not false")
    cases = exact_fields(source["cases"], SCENARIO_NAMES, "scenario list")
    clean = {}
    for name, case in cases.items():
        exact_fields(case, CASE_KEYS, name)
        if any(case[key] not in options for key, options in CASE_ENUMS.items()):
            raise ValueError("incompatible typed case: " + name)
        if (case["restricted_fields_disclosed"] is not False
            or type(case["publication"]) is not dict):
            raise ValueError("restricted disclosure or publication shape")
        pub = exact_fields(case["publication"], PUBLICATION_KEYS, name + "/publication")
        if (any(pub[key] not in options for key, options in PUBLICATION_ENUMS.items())
            or type(pub["attempts"]) is not int or pub["attempts"] not in (0, 1, 2)
            or type(pub["reconciled"]) is not bool):
            raise ValueError("incompatible publication metadata")
        clean[name] = {
            **{key: case[key] for key in sorted(CASE_KEYS - {"publication"})},
            "publication": {key: pub[key] for key in sorted(PUBLICATION_KEYS)},
        }
    return {
        "labels": LABELS,
        "evidence_kind": "deterministic orchestration/control-flow evidence",
        "cases": clean,
    }


def minimized_verifier(source: dict) -> dict:
    keys = set(AUTHENTIC_FIXED) | {"labels", "cryptographic", "cryptographic_reason"}
    exact_fields(source, keys, "offline verifier")
    if (source["labels"] != LABELS
        or any(source[k] != v or type(source[k]) is not type(v)
               for k, v in AUTHENTIC_FIXED.items())
        or source["cryptographic"] not in ("VALID", "INVALID")
        or source["cryptographic_reason"] != (
            None if source["cryptographic"] == "VALID" else "PROOF_REJECTED"
        )):
        raise ValueError("incompatible offline-verifier result")
    return {key: source[key] for key in sorted(keys)}


def replace_once(html: str, old: str, new: str) -> str:
    if html.count(old) != 1:
        raise ValueError("shared-console source anchor changed")
    return html.replace(old, new, 1)


def remove_between(html: str, start: str, end: str) -> str:
    if html.count(start) != 1 or html.count(end) != 1:
        raise ValueError("shared-console exclusion anchor changed")
    a = html.index(start)
    b = html.index(end)
    if b <= a:
        raise ValueError("shared-console exclusion order changed")
    return html[:a] + html[b:]


PUBLIC_INTRO_AND_SCOPE_OPEN = """  <section class="primer" aria-labelledby="primer-title">
    <p class="primer-kicker">THE CONCEPT IN BRIEF</p>
    <h2 id="primer-title">Verify a condition without revealing all the telemetry</h2>
    <p>TAG investigates cryptographic verification of selected telemetry conditions with limited disclosure. Instead of providing a full mission record, a system could provide a proof about a specific condition, subject to trusted inputs and appropriate validation.</p>
    <p class="primer-example"><strong>Illustrative example:</strong> A speed value satisfies a predefined limit without revealing the exact private value. This page does not test a real measurement or attest an actual mission.</p>
    <p class="primer-links"><a href="#mission-control">Explore the synthetic route</a><a href="#scenario-title">Inspect recorded scenarios</a><a href="#authentic-title">See the separate offline verifier result</a></p>
  </section>
  <section class="use-cases" aria-labelledby="use-cases-title">
    <h2 id="use-cases-title">Potential applications, not validated deployments</h2>
    <div class="use-cases-grid">
      <article><h3>Telemetry audits</h3><p>An operator could present evidence about a predefined condition without exposing the complete underlying dataset. No audit acceptance is established by this showcase.</p></article>
      <article><h3>Autonomous platforms</h3><p>Future integrations could be investigated for aerial, ground or maritime vehicles. This page does not connect to or control any vehicle.</p></article>
      <article><h3>Existing workflows</h3><p>CLI tools and possible future connectors could support integration with other systems. The public site exposes no execution endpoint.</p></article>
    </div>
  </section>
  <details class="scope-disclosure" id="technical-scope">
    <summary>Full experimental scope and limitations</summary>
  <section class="scope" aria-label="Scope and limitations of synthetic evidence">"""


def public_html(source: str) -> str:
    html = remove_between(
        source, "    .operator[hidden],.operator-result[hidden]{display:none}",
        '    .status[data-tone="good"]',
    )
    html = remove_between(
        html, '  <section class="card operator" id="operator-panel"',
        '  <div class="layout">\n    <section class="card" aria-labelledby="scenario-title">',
    )
    html = remove_between(
        html, "// Progressive enhancement: the shared page remains a recorded-only console",
        '$("authentic-reload").addEventListener("click",initializeAuthentic);',
    )
    html = replace_once(html, "\ninitializeOperator();", "")
    html = replace_once(
        html, "<title>TAG — Mission Control · Synthetic Research</title>",
        '<title>TAG — Privacy-Preserving Telemetry Attestation | ROCSI</title>\n'
        '  <meta name="robots" content="noindex,nofollow">',
    )
    html = replace_once(
        html,
        '<p class="sub">Explore the orchestration states of privacy-preserving bounded-speed attestation. Recorded mock orchestration and offline verifier evidence remain separate. On the authenticated local CLI preview only, this same console also enables one bounded synthetic execution. No proof or verification runs in the browser.</p>',
        '<p class="sub">TAG explores how specific telemetry conditions could be verified without sharing all underlying data. This experimental public page only displays synthetic animations, mock scenarios and a recorded offline verification outcome; no live vehicle connection, control, proof generation or browser verification occurs.</p>',
    )
    html = replace_once(
        html, 'LOCAL PREVIEW · PRECOMPUTED ONLY</div>',
        'PUBLIC SHOWCASE · PRECOMPUTED ONLY</div>',
    )
    html = replace_once(
        html,
        '  <section class="scope" aria-label="Scope and limitations of synthetic evidence">',
        PUBLIC_INTRO_AND_SCOPE_OPEN,
    )
    html = replace_once(
        html, '  </section>\n  <section class="mission-control" id="mission-control"',
        '  </section>\n  </details>\n  <section class="mission-control" id="mission-control"',
    )
    html = replace_once(
        html, '#authentic-panel{overflow-wrap:anywhere}',
        '#authentic-panel{overflow-wrap:anywhere}\n'
        '.primer{margin:0 0 18px;padding:20px;border:1px solid #35647c;border-radius:16px;background:#112739;min-width:0}\n'
        '.primer h2{font-size:1.3rem;margin:0 0 10px;color:#e1f8fb}\n'
        '.primer p{color:#d2e4ee;font-size:.91rem;line-height:1.55;margin:9px 0}\n'
        '.primer .primer-kicker{font-size:.72rem;color:#81d9e7;font-weight:800;letter-spacing:.08em}\n'
        '.primer .primer-example{border-left:3px solid #81d9e7;padding:6px 0 6px 12px}\n'
        '.primer .primer-links{display:flex;flex-wrap:wrap;gap:8px 20px;margin:15px 0 0}\n'
        '.use-cases{margin:0 0 18px}.use-cases h2{margin:0 0 12px}\n'
        '.use-cases-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}\n'
        '.use-cases article{background:#102538;border:1px solid #38556a;border-radius:12px;padding:15px;min-width:0}\n'
        '.use-cases h3{margin:0 0 8px;font-size:.94rem;color:#d5f5fa}\n'
        '.use-cases p{margin:0;color:#c4d7e6;font-size:.85rem;line-height:1.48}\n'
        '.scope-disclosure{margin:0 0 18px;padding:13px 16px;border:1px solid #38556a;border-radius:12px;background:#0e2031}\n'
        '.scope-disclosure summary{color:#d5f5fa}.scope-disclosure .scope{margin:15px 0 0}\n'
        '@media(max-width:750px){.use-cases-grid{grid-template-columns:1fr}}',
    )
    html = replace_once(
        html, "Backend truth · separate from animation",
        "No live backend · independent of illustration",
    )
    html = replace_once(html, "<h3>Accepted final CLI result</h3>",
                        "<h3>Execution deliberately disabled</h3>")
    html = replace_once(
        html, "NOT_OBSERVED · no active CLI result</dd>",
        "DISABLED · static showcase only</dd>",
    )
    html = replace_once(
        html, "Only a validated final response from the existing one-shot CLI bridge updates these fields. Request in flight never means a pipeline stage completed. Recorded mocks and offline replay remain separate below.",
        "These fields never represent running computation on this public site. "
        "The mock scenario panel and independently recorded offline-verifier result "
        "below remain separate from the illustration.",
    )
    html = replace_once(
        html, '      <div class="flow" aria-label="Conceptual pipeline">',
        '      <p class="small">Conceptual flow only: synthetic telemetry → normalization → '
        'proof → independent verification → optional publication. The stages below replay mocks; '
        'they are not live progress.</p>\n'
        '      <div class="flow" aria-label="Conceptual pipeline">',
    )
    html = replace_once(
        html, 'fetch("../integrated-cli-v0/evidence-results.json"',
        'fetch("/evidence-results.json"',
    )
    html = replace_once(html, 'fetch("authentic-evidence.json"',
                        'fetch("/authentic-evidence.json"')
    html = replace_once(
        html, "Local evidence could not be loaded. Serve the experiments/ directory over loopback HTTP; no external service is required.",
        "Precomputed scenario file unavailable. Check the same-origin static assets; "
        "no live fallback exists.",
    )
    html = replace_once(
        html, ' id="authentic-panel" aria-labelledby="authentic-title" style="margin-top:18px"',
        ' id="authentic-panel" aria-labelledby="authentic-title"',
    )
    html = replace_once(
        html, '#authentic-panel{overflow-wrap:anywhere}',
        '#authentic-panel{overflow-wrap:anywhere;margin-top:18px}',
    )
    html = replace_once(
        html, "A local JSON replay is not an authenticated proof",
        "A static JSON replay is not an authenticated proof",
    )
    html = replace_once(
        html,
        "To update this panel, first run the separate private offline CLI refresh, then reload its recorded result below. This button never runs the CLI, proves a claim or starts verification.",
        "This frozen result was created before publication. Reloading this static file "
        "never runs a prover, verifies a proof or refreshes an offline computation.",
    )
    html = replace_once(
        html, "Local/offline demonstration preview only. No analytics, remote APIs, uploads, external fonts, or proof jobs. Sources are separately labeled: deterministic mock orchestration and an offline-verifier-generated, minimized synthetic replay. The browser does not verify proofs.",
        "Public static technology showcase. Experimental synthetic-only, precomputed results. "
        "No visitor execution, vehicle connection, telemetry upload, analytics, tracking, "
        "external fonts or proof jobs. The browser does not independently verify proofs.",
    )
    html = redesign_public_html(html)
    forbidden = (
        "operator-panel", "operator-token", "operator-run", "operator-capabilities",
        "initializeOperator", "OPERATOR_KEYS", "X-TAG-Local-Token",
        '"execute"', "/execute", "one-shot", "http://", "https://",
        "WebSocket(", "EventSource(", "localStorage", "sessionStorage",
        "navigator.sendBeacon", "setInterval(", "<form",
    )
    # Explicit reference and parent-site links are navigation only, never fetch targets.
    # Strip only exact allowlisted href values for the existing fail-closed
    # external URL guard; any other URL (including in scripts) remains rejected.
    external_urls = re.findall(r'https?://[^\s"<>]+', html)
    if (set(external_urls) != PUBLIC_REFERENCE_URLS
            or len(external_urls) != len(PUBLIC_REFERENCE_URLS)):
        raise ValueError("unapproved external reference in public HTML")
    guarded_html = html
    for url in PUBLIC_REFERENCE_URLS:
        href = f'href="{url}"'
        if guarded_html.count(href) != 1:
            raise ValueError("external reference is not a single navigation link")
        guarded_html = guarded_html.replace(href, 'href="#reference"', 1)
    if any(token in guarded_html for token in forbidden):
        raise ValueError("public HTML retains restricted local/external feature")
    if html.count('<script>') != 1 or html.count('<style>') != 1:
        raise ValueError("unexpected HTML script/style surface")
    if re.search(r'\sstyle="', html):
        raise ValueError("inline style attribute incompatible with strict CSP")
    if not all(label in html for label in LABELS):
        raise ValueError("missing experimental label in public HTML")
    return html


def sha256_source(text: str) -> str:
    return "'sha256-" + base64.b64encode(
        hashlib.sha256(text.encode("utf-8")).digest()
    ).decode("ascii") + "'"


def security_headers(html: str) -> str:
    style = re.search(r"<style>(.*?)</style>", html, flags=re.S)
    script = re.search(r"<script>(.*?)</script>", html, flags=re.S)
    if not style or not script:
        raise ValueError("inline content missing for CSP")
    csp = "; ".join((
        "default-src 'none'",
        "script-src " + sha256_source(script.group(1)),
        "style-src " + sha256_source(style.group(1)),
        "style-src-attr 'none'",
        "img-src 'self' data:",
        "connect-src 'self'",
        "base-uri 'none'",
        "form-action 'none'",
        "frame-ancestors 'none'",
        "object-src 'none'",
        "upgrade-insecure-requests",
    ))
    return (
        "/*\n"
        "  Content-Security-Policy: " + csp + "\n"
        "  X-Content-Type-Options: nosniff\n"
        "  Referrer-Policy: no-referrer\n"
        "  Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=()\n"
        "  X-Frame-Options: DENY\n"
        "  Cache-Control: no-store\n"
        "  X-Robots-Tag: noindex\n"
    )



def load_research_journal(path: Path = JOURNAL) -> dict:
    """Validate public-safe, bilingual accepted research summaries at build time."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    exact_fields(payload, {"schema_version", "entries", "next_question"}, "journal")
    if payload["schema_version"] != "TAG_RESEARCH_JOURNAL_V1":
        raise ValueError("unsupported journal schema")
    entries = payload["entries"]
    if type(entries) is not list or not 1 <= len(entries) <= 12:
        raise ValueError("journal entry count invalid")
    seen = set()

    def fields(value: object, required: set[str], where: str) -> dict:
        obj = exact_fields(value, required, where)
        for key, text in obj.items():
            if (type(text) is not str or not text or text != text.strip()
                or len(text) > 420 or re.search(r'https?://|[<>]|\x00', text)):
                raise ValueError("unsafe public journal text: " + where + "/" + key)
        return obj

    for item in entries:
        exact_fields(item, {"id", "status", "evidence_path", "ro", "en"}, "entry")
        if (type(item["id"]) is not str
            or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", item["id"])
            or item["id"] in seen or item["status"] != "documented_synthetic"):
            raise ValueError("invalid, duplicate or unapproved journal entry")
        seen.add(item["id"])
        ref = item["evidence_path"]
        if type(ref) is not str or not re.fullmatch(
            r"experiments/[a-z0-9-]+/(?:[a-z0-9-]+/)*[a-z0-9_.-]+\.(?:md|py)",
            ref,
        ) or any(part in (".", "..") for part in PurePosixPath(ref).parts):
            raise ValueError("invalid journal evidence reference")
        if not (ROOT / ref).is_file():
            raise ValueError("journal evidence reference not found: " + ref)
        for language in ("ro", "en"):
            fields(item[language], {"field", "title", "result", "insight"}, item["id"] + "/" + language)
    exact_fields(payload["next_question"], {"ro", "en"}, "next question")
    for language in ("ro", "en"):
        fields(payload["next_question"][language], {"label", "title", "description"}, "next/" + language)
    return payload


def render_research_journal(html: str, journal: dict, language: str) -> str:
    """Inline verified editorial copy into the already-static page, never browser JS."""
    if language not in ("ro", "en") or html.count(JOURNAL_MARKER) != 1:
        raise ValueError("journal insertion anchor or locale changed")
    en = language == "en"
    note = "LAB NOTE" if en else "NOTĂ DE LABORATOR"
    lesson = "What we learned" if en else "Ce am învățat"
    items = []
    for i, item in enumerate(journal["entries"], 1):
        copy = item[language]
        items.append(
            '<li class="research-entry"><div class="research-entry-meta">'
            f'<span class="research-entry-number">{i:02d} / {note}</span>'
            f'<span class="research-entry-field">{escape(copy["field"])}</span>'
            '</div><div class="research-entry-copy">'
            f'<h3>{escape(copy["title"])}</h3>'
            f'<p>{escape(copy["result"])}</p>'
            f'<p class="research-entry-insight"><strong>{lesson}:</strong> '
            f'{escape(copy["insight"])}</p></div></li>'
        )
    next_copy = journal["next_question"][language]
    markup = ('<ol class="research-journal" aria-label="' +
              ("Documented research notes" if en else "Note de cercetare documentate") + '">'
              + "\n".join(items) + '</ol>'
              '<aside class="research-next-question">'
              f'<span>{escape(next_copy["label"])}</span>'
              f'<h3>{escape(next_copy["title"])}</h3>'
              f'<p>{escape(next_copy["description"])}</p></aside>')
    return html.replace(JOURNAL_MARKER, markup, 1)


def build(out: Path) -> tuple[str, ...]:
    target = out.resolve()
    protected = (ROOT.resolve(), CONSOLE.parent.resolve(),
                 SCENARIOS.parent.resolve())
    if target in protected or any(target == folder for folder in protected):
        raise ValueError("cannot overwrite an experiment source directory")
    html = public_html(CONSOLE.read_text(encoding="utf-8"))
    # The original inline data-URI placeholder is replaced by the local drone icon.
    html = re.sub(r'  <link rel="icon" href="data:image/svg\+xml,[^"]+">\n',
                  "", html, count=1)
    if 'href="data:image/svg+xml,' in html:
        raise ValueError("placeholder favicon was not removed")
    html = inject_locale_js(html)
    journal = load_research_journal()
    html_en = social_metadata(render_research_journal(html, journal, "en"), "en")
    html_ro = social_metadata(render_research_journal(romanian_html(html), journal, "ro"), "ro")
    if security_headers(html_ro) != security_headers(html_en):
        raise ValueError("localized assets have mismatching CSP inline hashes")
    media = ROOT / "showcase/assets"
    png = ("og/ro.png", "og/en.png", "apple-touch-icon.png")
    for name in png:
        payload = (media / name).read_bytes()
        if (not payload.startswith(b"\x89PNG\r\n\x1a\n")
            or len(payload) > 450_000):
            raise ValueError("invalid or oversized PNG: " + name)
    scenarios = minimized_scenarios(json.loads(SCENARIOS.read_text(encoding="utf-8")))
    authentic = minimized_verifier(json.loads(VERIFIER.read_text(encoding="utf-8")))
    assets = {
        "ro/index.html": html_ro,
        "en/index.html": html_en,
        "404.html": localize_404("ro"),
        "en/404.html": localize_404("en"),
        "evidence-results.json": json.dumps(scenarios, indent=2, ensure_ascii=False) + "\n",
        "authentic-evidence.json": json.dumps(authentic, indent=2, ensure_ascii=False) + "\n",
        "_headers": security_headers(html_ro),
        "_redirects": '/ /ro/ 301\n',
        # Crawlers need access to static Open Graph metadata and PNGs. The
        # X-Robots-Tag and HTML robots=noindex remain set for search indexing.
        "robots.txt": "User-agent: *\nAllow: /\n",
        "assets/favicon.svg": (media / "favicon.svg").read_bytes(),
        "assets/favicon.ico": (media / "favicon.ico").read_bytes(),
        "assets/apple-touch-icon.png": (media / "apple-touch-icon.png").read_bytes(),
        "og/ro.png": (media / "og/ro.png").read_bytes(),
        "og/en.png": (media / "og/en.png").read_bytes(),
    }
    target.mkdir(parents=True, exist_ok=True)
    # Avoid shipping a stale root page if the output directory is reused.
    obsolete_root = target / "index.html"
    if obsolete_root.is_symlink() or (obsolete_root.exists() and not obsolete_root.is_file()):
        raise ValueError("refusing unsafe stale root entry")
    obsolete_root.unlink(missing_ok=True)
    for filename, content in assets.items():
        destination = target / filename
        if not destination.resolve().is_relative_to(target):
            raise ValueError("refusing output path escape")
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.is_symlink():
            raise ValueError("refusing output symlink")
        if isinstance(content, bytes):
            destination.write_bytes(content)
        else:
            destination.write_text(content, encoding="utf-8")
    return tuple(assets)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    names = build(args.out_dir)
    print("EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION")
    print("Static-only public assets:", ", ".join(names))
