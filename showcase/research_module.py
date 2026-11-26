"""EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION.

Public research page: static editorial evidence and native HTML disclosure only.
"""
from html import escape
from localization import LANGUAGE_DROPDOWN_CSS, language_dropdown

ORIGIN = "https://tag.rocsi.eu"
REPO = "https://github.com/ROCSI-eu/Telemetry-Attestation-Gateway"
CSS = """
.research-page{margin:0;background:#101a1d;color:#e9e8df;font:16px/1.65 system-ui,-apple-system,BlinkMacSystemFont,sans-serif}
.research-page *{box-sizing:border-box}
.research-page a{color:#eacb91;text-underline-offset:4px}
.research-page a:focus-visible,.research-page summary:focus-visible{outline:3px solid #eacb91;outline-offset:5px}
.r-wrap{width:min(1120px,100% - 64px);margin:auto}
.r-header{display:flex;align-items:center;justify-content:space-between;gap:18px;padding:22px 0;border-bottom:1px solid #405052;flex-wrap:wrap}
.r-brand{display:flex;align-items:center;gap:12px;text-decoration:none;color:#e9e8df!important;font-weight:700;letter-spacing:.04em}
.r-brand img{width:34px;height:34px;object-fit:contain}
.r-hero{padding:64px 0 42px;border-bottom:1px solid #405052}
.r-kicker{font-size:.73rem;text-transform:uppercase;letter-spacing:.16em;font-weight:750;color:#eacb91;margin:0 0 10px}
.r-hero h1{font-size:clamp(2.2rem,5vw,4.35rem);letter-spacing:-.045em;line-height:1.06;max-width:850px;margin:0 0 18px;color:#f5f1e6}
.r-lead{font-size:1.15rem;color:#c6d0cb;max-width:74ch;margin:0 0 24px}
.r-boundary{display:inline-block;padding:8px 12px;border:1px solid #68706a;font-size:.75rem;color:#eeddb9;line-height:1.5}
.r-nav{display:flex;gap:12px 26px;flex-wrap:wrap;margin-top:24px}
.r-section{padding:42px 0;border-bottom:1px solid #405052;scroll-margin-top:20px}
.r-section h2{font-size:clamp(1.6rem,3vw,2.25rem);line-height:1.17;letter-spacing:-.025em;margin:0 0 12px;color:#f3efe2}
.r-section-intro{color:#bbc7c3;max-width:78ch;margin:0 0 24px}
.r-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}
.r-entry{background:#162427;border:1px solid #415254;padding:24px;min-width:0;display:flex;flex-direction:column;align-items:flex-start}
.r-entry h4{font-size:1.2rem;line-height:1.3;color:#f1e4cb;margin:5px 0 12px}
.r-entry p{margin:0 0 12px;color:#d2dbd5}
.r-entry .r-limit{border-top:1px solid #405052;padding-top:12px;color:#c3cbc4;font-size:.92rem}
.r-entry a{margin-top:auto;font-size:.88rem}
.r-article{max-width:880px;margin:0 auto;padding:28px 0 60px}
.r-article h1{font-size:clamp(2rem,4.5vw,3.6rem);line-height:1.12;margin:0 0 15px;color:#f5f1e6}
.r-article h2{font-size:1.45rem;line-height:1.25;margin:28px 0 10px;color:#eacb91}
.r-article p{color:#d2dbd5;margin:0 0 16px}
.r-article .r-equation{border:1px solid #596567;background:#141f22;padding:19px;white-space:pre-wrap;overflow-wrap:anywhere;color:#f1e4cb;font-size:1rem}
/* Static visual atlas: text labels, not color alone, carry meaning. */
.r-diagram{border:1px dashed #7b8d92;border-radius:12px;background:#121e22;padding:clamp(12px,3vw,24px);margin:24px 0}
.r-diagram .r-atlas-boundary{font-size:.72rem;letter-spacing:.08em;text-transform:uppercase;color:#b8c5c6;text-align:center;margin:0 0 16px}
.r-diagram .r-atlas-mode{color:#eacb91;letter-spacing:0;text-transform:none;font-size:.85rem;font-weight:650}
.r-diagram ol,.r-visual-path{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:22px;margin:0;padding:0;list-style:none}
.r-diagram li,.r-visual-node{position:relative;min-width:0;overflow-wrap:anywhere;border:1px solid #6c8490;border-radius:8px;background:#202e35;padding:12px 10px;text-align:center;color:#eef3f3;display:flex;align-items:center;justify-content:center;min-height:74px;font-size:.95rem;line-height:1.45}
.r-diagram li:not(:last-child):after,.r-visual-node:not(:last-child):after{content:'→';position:absolute;right:-20px;top:50%;transform:translateY(-50%);font-size:1.2rem;color:#bac9ce}
.r-diagram ol li:nth-child(2){border-color:#3ba7a0;background:#173333}
.r-visual-heading{margin:22px 0 8px;font-size:.8rem;letter-spacing:.07em;text-transform:uppercase;color:#c3d1d1;font-weight:700}
.r-visual-case{margin:12px 0;padding:12px;border:1px solid #4a6267;border-radius:10px;background:#182529}
.r-visual-case h3{margin:0 0 10px;font-size:.83rem;letter-spacing:.06em;text-transform:uppercase;color:#c9d6d5}
.r-visual-case .r-visual-node:nth-child(2){border-color:#3ba7a0;background:#173333}
.r-visual-case-observed .r-visual-node:last-child{border-color:#79bfa0;background:#20382e;color:#c5f0d8}
.r-visual-case-control .r-visual-node:last-child{border-color:#df9292;background:#38292b;color:#ffdddd}
.r-visual-case-limit .r-visual-node:last-child{border-color:#c3a369;background:#352f25;color:#f3e4c5}
.r-visual-case-limit{border-style:dashed}
.r-diagram figcaption{color:#c5cecb;font-size:.85rem;margin-top:16px}
.r-atlas-map{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
.r-atlas-group{min-width:0;border:1px solid #4b6469;border-radius:10px;background:#162427;padding:18px}
.r-atlas-group{display:flex;flex-direction:column;justify-content:center;gap:6px;min-height:84px;text-decoration:none;overflow-wrap:anywhere}
.r-atlas-group strong{color:#a6e0d9;font-size:1.02rem;line-height:1.4;text-decoration:underline;text-underline-offset:4px}
.r-atlas-group span{color:#c3cbc4;font-size:.82rem}
.r-atlas-group:hover,.r-atlas-group:focus-visible{background:#203134}
.r-theme{margin:28px 0 0;scroll-margin-top:20px}
.r-theme>h3{font-size:1.25rem;color:#a6e0d9;margin:0 0 12px;line-height:1.3}
.r-theme-back{display:inline-block;margin-top:12px;font-size:.85rem}
.r-article a{overflow-wrap:anywhere}
@media(max-width:700px){.r-atlas-map{grid-template-columns:1fr}}
@media(max-width:640px){.r-diagram ol,.r-visual-path{grid-template-columns:1fr;gap:24px}.r-diagram li,.r-visual-node{min-height:0;padding:12px}.r-diagram li:not(:last-child):after,.r-visual-node:not(:last-child):after{content:'↓';right:50%;top:auto;bottom:-24px;transform:translateX(50%)}}
.r-feature{border-left:3px solid #bda36d;background:#1b282a;padding:22px 24px;margin:0 0 20px}
.r-feature h3{font-size:1.2rem;margin:0 0 8px;color:#f2e8d2}
.r-feature p{margin:6px 0;color:#d2dbd5}
.r-demo{border:1px solid #415254;background:#162427;margin-top:10px}
.r-demo summary{cursor:pointer;padding:17px 20px;font-weight:650;color:#f1e4cb}
.r-demo summary:hover{background:#203134}
.r-demo[open] summary{border-bottom:1px solid #415254}
.r-demo-body{padding:16px 20px;color:#d2dbd5}
.r-demo-body p{margin:0 0 8px}
.r-status{font-size:.76rem;letter-spacing:.04em;text-transform:uppercase;color:#eacb91;font-weight:700}
.r-questions{padding:24px;border:1px solid #596567;background:#141f22}
.r-questions h3{margin:0 0 10px;color:#f1e4cb}
.r-questions p{margin:0;color:#c6d0cb}
.r-footer{padding:24px 0 36px;font-size:.82rem;color:#aab8b2}
.r-footer p{margin:8px 0}
@media(max-width:700px){.r-wrap{width:calc(100% - 36px)}.r-hero{padding:38px 0 28px}.r-section{padding:30px 0}.r-grid{grid-template-columns:1fr}.r-entry{padding:19px}.r-lead{font-size:1rem}.r-brand{font-size:.9rem}.r-feature,.r-questions{padding:18px}}
@media(max-width:360px){.r-wrap{width:calc(100% - 28px)}.r-header{gap:10px}.r-nav{gap:8px 16px}.r-entry{padding:16px}.r-demo summary,.r-demo-body{padding:14px}}
""" + LANGUAGE_DROPDOWN_CSS
COPY = {
"ro": {
 "home":"Prezentare", "title":"Cercetare și rezultate experimentale", "label":"ROCSI / Telemetry Attestation Gateway",
 "lead":"Ce-am demonstrat în laborator, ce limite au rezultatele și ce întrebări rămân deschise. O evidență cumulativă a cercetării TAG, separată de prezentarea generală.",
 "boundary":"EXPERIMENTAL · DOAR DATE SINTETICE · A0_SYNTHETIC · FĂRĂ VALIDARE SAU AUTORIZARE OPERAȚIONALĂ",
 "findings":"Rezultate documentate", "demos":"Explorează demonstrațiile", "next":"Direcții deschise",
 "intro":"Rezultatele sunt grupate pe teme, de la cel mai recent la cel mai vechi în fiecare temă. Fiecare constatare are un singur rezumat, limita ei și legături către articol și dovezi.",
 "limit":"Ce înseamnă și ce nu demonstrează", "evidence":"Documentația experimentului",
 "demo_intro":"Scenarii deterministe care explică fluxul decizional. Explorează rezultatele preînregistrate.",
 "record":"Rezultat criptografic preînregistrat", "record_valid":"Verificatorul offline a acceptat o dovadă sintetică.", "record_invalid":"Verificatorul offline a respins o dovadă sintetică.",
 "record_limit":"Aceasta este o consemnare JSON minimizată, neautentificată de browser, nu o dovadă verificată aici. Nu confirmă sursa, prospețimea sau adevărul telemetriei.",
 "mock":"Simulare a fluxului", "claim":"Condiție", "crypto":"Rezultat criptografic simulat",
 "satisfied":"Îndeplinită", "not_satisfied":"Neîndeplinită", "valid":"Acceptat", "invalid":"Respins", "not_checked":"Neverificat",
 "cases":[("below_limit_local_publication","Condiție îndeplinită","Fluxul simulat continuă până la verificare."),("over_limit","Limită depășită","Condiția nu este îndeplinită; nu se verifică o dovadă."),("tampered_proof","Dovadă alterată","Chiar dacă rezultatul condiției este favorabil, verificarea simulată respinge dovada.")],
 "foot":"Cercetare ROCSI. Fără telemetrie reală, comenzi, calcule criptografice în browser sau autorizare operațională.",
 "github":"Repository și documentație", "cta":"Explorează cercetarea",
 "home_progress":"Cercetăm verificarea criptografică a condițiilor, legarea dovezilor de observații semnate sintetic, protecția împotriva reutilizării și prospețimea recepției cu o autoritate temporală simulată. Experimentele distincte investighează și completitudinea, continuitatea, integritatea stării, agregarea și consistența emisiilor și epocilor. Nu toate aceste rezultate implică dovezi criptografice noi; limitele și contraexemplele sunt documentate în catalog."
},
"en": {
 "home":"Overview", "title":"Research and experimental results", "label":"ROCSI / Telemetry Attestation Gateway",
 "lead":"What we have demonstrated in the lab, what the results cannot establish, and what remains open. A cumulative record of TAG research, separate from the general overview.",
 "boundary":"EXPERIMENTAL · SYNTHETIC ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION",
 "findings":"Documented findings", "demos":"Explore the demonstrations", "next":"Open research directions",
 "intro":"Findings are grouped by theme, newest first within each theme. Each has one summary, its limitation and links to the article and evidence.",
 "limit":"Meaning and limitations", "evidence":"Experiment documentation",
 "demo_intro":"Deterministic scenarios explain the decision flow. Explore the recorded outcomes.",
 "record":"Recorded cryptographic result", "record_valid":"An offline verifier accepted a synthetic proof.", "record_invalid":"An offline verifier rejected a synthetic proof.",
 "record_limit":"This is a minimized JSON record, not authenticated by the browser, not a proof verified here. It does not establish source identity, freshness or telemetry truth.",
 "mock":"Simulated flow", "claim":"Condition", "crypto":"Simulated cryptographic result",
 "satisfied":"Satisfied", "not_satisfied":"Not satisfied", "valid":"Accepted", "invalid":"Rejected", "not_checked":"Not checked",
 "cases":[("below_limit_local_publication","Condition satisfied","The simulated flow proceeds to verification."),("over_limit","Limit exceeded","The condition is not met; no proof is checked."),("tampered_proof","Tampered proof","Even with a favorable condition outcome, simulated verification rejects the proof.")],
 "foot":"ROCSI research. No real telemetry, commands, browser cryptography or operational authorization.",
 "github":"Repository and documentation", "cta":"Explore the research",
 "home_progress":"We investigate cryptographic verification of conditions, proof binding to synthetically signed observations, replay protection and reception freshness with a simulated time authority. Separate experiments also investigate completeness, continuity, state integrity, aggregation, and emission and epoch consistency. Not all these results involve new cryptographic proofs; limitations and counterexamples are documented in the catalog."
}}
ARTICLE_LABELS = {
    "ro": {"open": "Citește articolul", "back": "Înapoi la jurnal",
           "question": "Întrebarea de cercetare", "principle": "Principiul și modelul",
           "method": "Metodă experimentală", "observed": "Observația documentată",
           "formula": "Relație formală sau invariant", "interpretation": "Interpretare",
           "controls": "Controale și contraexemple", "limitations": "Limite",
           "figure": "Schemă conceptuală, nu dovadă experimentală",
           "source": "Proveniență: raportul experimental verificabil"},
    "en": {"open": "Read the article", "back": "Back to research journal",
           "question": "Research question", "principle": "Principle and model",
           "method": "Experimental method", "observed": "Documented observation",
           "formula": "Formal relation or invariant", "interpretation": "Interpretation",
           "controls": "Controls and counterexamples", "limitations": "Limitations",
           "figure": "Conceptual diagram, not experimental evidence",
           "source": "Provenance: inspectable experimental record"},
}

# Categories are thematic, not milestones, dependencies or assurance tiers.
ATLAS_THEMES = {
    "foundations": ("Fundamente criptografice și simulare", "Cryptographic foundations and simulation"),
    "source": ("Legarea de sursă și prospețime", "Source binding and freshness"),
    "coverage": ("Completitudine și continuitate", "Completeness and continuity"),
    "state": ("Integritatea stării", "State integrity"),
    "aggregate": ("Agregare criptografică", "Cryptographic aggregation"),
    "emission": ("Consistența emisiilor și epocilor", "Emission and epoch consistency"),
}
ATLAS_KINDS = ("observed", "control", "limit")
ATLAS_MODES = {
    "genuine": ("Dovadă criptografică reală în experimentul sintetic", "Genuine cryptographic proof in the synthetic experiment"),
    "passive": ("Recepție pasivă; fără dovadă în acest pas", "Passive reception; no proof at this step"),
    "mock": ("Verificator de dovezi simulat; fără ZKP nouă", "Mock proof verifier; no new ZKP"),
    "authenticated_no_zkp": ("Controale de autentificare și consistență; fără ZKP nouă", "Authentication and consistency checks; no new ZKP"),
}
ATLAS_COPY = {
    "ro": {"heading": "Atlasul vizual al cercetării", "intro": "Explorează constatările și mini-articolele grupate după teme de cercetare. Gruparea descrie relații conceptuale, nu maturitatea produsului.",
           "count_one": "constatare", "count_many": "constatări", "back": "Înapoi la atlas",
           "boundary": "Mediu experimental · exclusiv date sintetice",
           "flow": "Modelul investigat", "observed": "Scenariu documentat", "control": "Control / caz negativ", "limit": "Limită / contraexemplu",
           "caption": "Modelul investigat și relațiile conceptuale dintre cazurile documentate."},
    "en": {"heading": "Research visual atlas", "intro": "Explore findings and articles grouped by research theme. The grouping describes conceptual relationships, not product maturity.",
           "count_one": "finding", "count_many": "findings", "back": "Back to atlas",
           "boundary": "Experimental environment · synthetic data only",
           "flow": "Investigated model", "observed": "Documented scenario", "control": "Control / negative case", "limit": "Limitation / counterexample",
           "caption": "Investigated model and conceptual relationships between the documented cases."},
}


# Overview-only styles, appended to the existing inert stylesheet at build time.
OVERVIEW_CSS = """
.public-research-summary{margin:28px 0 24px}
.public-research-summary h3,.public-gcs h3{font-size:clamp(1.3rem,2.4vw,1.8rem);line-height:1.25;color:#f1e4cb;margin:0 0 14px}
.public-research-counts{display:flex;flex-wrap:wrap;gap:12px 30px;margin:0 0 20px}
.public-research-counts div{min-width:0;flex:0 1 190px}
.public-research-counts dt{color:#c8d4d0;font-size:.88rem}
.public-research-counts dd{margin:0;color:#e4c58e;font-size:2rem;font-weight:750;line-height:1.2}
.public-gcs{margin:32px 0 24px;padding:clamp(15px,3vw,26px);border:1px solid #466168;background:#102329}
.public-gcs p{color:#ccd7d0;line-height:1.6;margin:0 0 12px}
.public-gcs figure{margin:20px auto 0;max-width:680px}
.public-gcs-source,.public-gcs-node{min-width:0;overflow-wrap:anywhere;border:1px solid #6c8490;background:#17282c;padding:14px;text-align:center;color:#e5efeb}
.public-gcs-source{max-width:300px;margin:auto}
.public-gcs-source strong,.public-gcs-node strong{display:block;color:#ebd1a4;margin-bottom:5px}
.public-gcs-arrow{text-align:center;color:#a6e0d9;font-size:1.1rem;margin:5px 0}
.public-gcs-branches{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;align-items:start}
.public-gcs-branch{min-width:0}
.public-gcs-branch:last-child .public-gcs-node{border-color:#69aba3;border-style:dashed}
.public-gcs figcaption{font-size:.84rem;color:#c8d4d0;margin-top:14px}
@media(max-width:600px){.public-gcs-branches{grid-template-columns:1fr;gap:16px}.public-research-counts div{flex:1 1 120px}}
/* Overview only: preserve the research catalog's common CSS. */
.public-research-summary{border-top:1px solid #466168;padding-top:24px}
.public-research-counts{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;max-width:560px}
.public-research-counts div{border-top:2px solid #d5b67e;padding:12px 16px;background:#14272c}
.public-research-counts dd{font-size:clamp(2rem,4vw,3rem)}
.public-gcs figure{max-width:840px}
.public-gcs-icon{display:block;width:56px;height:46px;color:#9bd3cf;flex:none}
.public-gcs-source,.public-gcs-node{display:flex;align-items:center;gap:14px;text-align:left;padding:16px}
.public-gcs-source strong,.public-gcs-node strong{margin-bottom:4px}
.public-gcs-fork{width:100%;height:44px;display:block;color:#9bd3cf}
.public-gcs-branch>.public-gcs-arrow:first-child{display:none}
.public-gcs-arrow{height:28px;margin:3px 0}
.public-gcs-arrow svg{width:32px;height:28px}
.public-gcs-branch:last-child .public-gcs-node{background:#142c31}
@media(max-width:600px){.public-gcs-fork{display:none}.public-gcs-source{max-width:none}.public-gcs-branches{gap:12px;margin-left:12px;padding:14px 0 0 18px;border-left:1px solid #9bd3cf}.public-gcs-branch{position:relative}.public-gcs-branch::before{content:"";position:absolute;top:24px;left:-18px;width:17px;border-top:1px solid #9bd3cf}.public-gcs-branch::after{content:"";position:absolute;top:21px;left:-7px;width:6px;height:6px;border-top:1px solid #9bd3cf;border-right:1px solid #9bd3cf;transform:rotate(45deg)}.public-gcs-icon{width:42px;height:38px}.public-gcs-node,.public-gcs-source{gap:10px;padding:12px}.public-research-counts div{padding:10px}}
/* Balance the summary and illustrate proposed observation flow only. */
.public-research-balance{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:clamp(20px,4vw,48px);align-items:center}
.public-research-metrics{min-width:0}
.public-research-balance .public-research-counts{max-width:none;margin-bottom:16px}
.public-research-balance .public-documentation,.public-research-balance .public-progress{margin:0;max-width:none}
.public-gcs-flow{animation:public-gcs-flow 3s linear infinite}
@keyframes public-gcs-flow{to{stroke-dashoffset:-36}}
@keyframes public-gcs-branch-pulse{0%,100%{opacity:.55}50%{opacity:1}}
@media(max-width:750px){.public-research-balance{grid-template-columns:1fr;gap:18px}}
@media(max-width:600px){.public-gcs-branch::before,.public-gcs-branch::after{border-color:#e5c18a;animation:public-gcs-branch-pulse 3s ease-in-out infinite}}
@media(prefers-reduced-motion:reduce){.public-gcs-flow,.public-gcs-branch::before,.public-gcs-branch::after{animation:none!important}}
"""
OVERVIEW_COPY = {
    "ro": {"heading": "De la verificarea unei condiții la integritatea fluxului de telemetrie",
           "findings": "Constatări documentate", "themes": "Teme de cercetare",
           "direction": "Integrarea TAG cu sistemele GCS",
           "proposed": "Arhitectură propusă",
           "intro": "Următorul obiectiv este un companion TAG experimental, complementar software-ului existent de comandă și control (GCS), într-un mediu izolat, exclusiv sintetic.",
           "source": "ArduPilot SITL", "synthetic": "Observații sintetice",
           "gcs": "Software GCS", "gcs_note": "QGroundControl sau Mission Planner · control separat de TAG",
           "tag": "Companion TAG", "receive": "Doar recepție · fără comenzi sau retransmitere de control",
           "proof": "Dovezi exportabile", "verify": "Verificare independentă offline (obiectiv)",
           "caption": "Arhitectură propusă: observațiile sintetice ar urma să fie recepționate separat de GCS și companionul TAG."},
    "en": {"heading": "From checking a condition to telemetry stream integrity",
           "findings": "Documented findings", "themes": "Research themes",
           "direction": "TAG integration with GCS systems",
           "proposed": "Proposed architecture",
           "intro": "The next objective is an experimental TAG companion alongside existing ground control station (GCS) software, in an isolated, synthetic-only environment.",
           "source": "ArduPilot SITL", "synthetic": "Synthetic observations",
           "gcs": "GCS software", "gcs_note": "QGroundControl or Mission Planner · control separate from TAG",
           "tag": "TAG companion", "receive": "Receive-only · no commands or control relay",
           "proof": "Exportable evidence", "verify": "Independent offline verification (objective)",
           "caption": "Proposed architecture: the GCS and TAG companion would receive the synthetic observations separately."},
}


def render_overview_progress(journal: dict, lang: str) -> str:
    """Derived counts and proposed architecture, never a separate evidence registry."""
    c = OVERVIEW_COPY[lang]
    e = escape
    findings = len(journal["entries"])
    themes = len({item["article"]["visual"]["theme"] for item in journal["entries"]})
    icons = {
        "source": '<path d="M14 24h36M32 6v36M12 10l40 28M52 10L12 38"/><rect x="24" y="16" width="16" height="16" rx="4"/><circle cx="12" cy="10" r="5"/><circle cx="52" cy="10" r="5"/><circle cx="12" cy="38" r="5"/><circle cx="52" cy="38" r="5"/>',
        "gcs": '<rect x="5" y="5" width="54" height="34" rx="3"/><path d="M13 29l11-12 10 7 12-10M25 39v6m14-6v6M18 45h28"/>',
        "tag": '<path d="M32 4l23 12v23L32 51 9 39V16Z"/><path d="M20 24h24M20 31h24M20 38h14"/>',
        "proof": '<rect x="5" y="6" width="30" height="42" rx="3"/><path d="M12 17h16M12 25h16M12 33h12"/><circle cx="45" cy="32" r="15"/><path d="M39 32l5 5 8-10"/>',
    }
    def node(title, note, cls="public-gcs-node"):
        icon = ('<svg class="public-gcs-icon" viewBox="0 0 64 54" aria-hidden="true" focusable="false" '
                'fill="none" stroke="currentColor" stroke-width="1.8">' + icons[title] + '</svg>')
        return f'<div class="{cls}">{icon}<div><strong>{e(c[title])}</strong>{e(c[note])}</div></div>'
    arrow = ('<div class="public-gcs-arrow" aria-hidden="true"><svg viewBox="0 0 32 28" fill="none" stroke="currentColor" stroke-width="1.5">'
             '<path d="M16 1v23m-6-6 6 6 6-6"/></svg></div>')
    fork = ('<svg class="public-gcs-fork" viewBox="0 0 840 44" preserveAspectRatio="none" aria-hidden="true" '
            'fill="none" stroke="currentColor" stroke-width="1.5"><path d="M420 0v15H210v26m-6-6 6 6 6-6M420 15h210v26m-6-6 6 6 6-6"/><path class="public-gcs-flow" d="M420 0v15H210v26M420 0v15h210v26" stroke="#e5c18a" stroke-dasharray="3 15"/></svg>')
    return (
        f'<section class="public-research-summary" aria-labelledby="public-research-title">'
        f'<h3 id="public-research-title">{e(c["heading"])}</h3>'
        f'<div class="public-research-balance"><div class="public-research-metrics"><dl class="public-research-counts"><div><dt>{e(c["findings"])}</dt><dd id="public-finding-count">{findings}</dd></div>'
        f'<div><dt>{e(c["themes"])}</dt><dd id="public-theme-count">{themes}</dd></div></dl>'
        f'<p class="public-documentation"><a href="/{lang}/research/">{e(COPY[lang]["cta"])}</a></p></div>'
        f'<p class="public-progress">{e(COPY[lang]["home_progress"])}</p></div></section>'
        f'<section class="public-gcs" aria-labelledby="public-gcs-title">'
        f'<h3 id="public-gcs-title">{e(c["direction"])}</h3><p><strong>{e(c["proposed"])}</strong></p>'
        f'<p>{e(c["intro"])}</p><figure aria-label="{e(c["direction"], quote=True)}">'
        + node("source", "synthetic", "public-gcs-source") + fork
        + '<div class="public-gcs-branches"><div class="public-gcs-branch">'
        + arrow + node("gcs", "gcs_note")
        + '</div><div class="public-gcs-branch">'
        + arrow + node("tag", "receive") + arrow + node("proof", "verify")
        + f'</div></div><figcaption>{e(c["caption"])}</figcaption></figure></section>'
    )


def render_visual_diagram(item: dict, lang: str) -> str:
    """Static, semantic HTML; all node text is escaped and data comes from journal."""
    c = ATLAS_COPY[lang]
    article = item["article"]
    stages = "".join(f"<li>{escape(stage)}</li>" for stage in article[lang]["stages"])
    mode = ATLAS_MODES[article["visual"]["mode"]][lang == "en"]
    cases = []
    for path in article["visual"]["paths"]:
        kind = path["kind"]
        nodes = "".join(f'<div class="r-visual-node" role="listitem">{escape(node[lang])}</div>'
                        for node in path["nodes"])
        cases.append(f'<section class="r-visual-case r-visual-case-{kind}"><h3>{escape(c[kind])}</h3>'
                     f'<div class="r-visual-path" role="list" aria-label="{escape(c[kind], quote=True)}">{nodes}</div></section>')
    return (f'<figure class="r-diagram" aria-label="{escape(item[lang]["title"], quote=True)}">'
            f'<p class="r-atlas-boundary">{escape(c["boundary"])} · A0_SYNTHETIC</p>'
            f'<p class="r-atlas-boundary r-atlas-mode">{escape(mode)}</p>'
            f'<h3 class="r-visual-heading">{escape(c["flow"])}</h3><ol>{stages}</ol>'
            + "".join(cases) + f'<figcaption>{escape(c["caption"])}</figcaption></figure>')


def atlas_groups(journal: dict):
    """One grouping, newest finding first within each theme; no parallel registry."""
    groups = {}
    for number, item in reversed(list(enumerate(journal["entries"], 1))):
        groups.setdefault(item["article"]["visual"]["theme"], []).append((number, item))
    return groups


def render_atlas_map(groups: dict, lang: str) -> str:
    c = ATLAS_COPY[lang]
    links = []
    for theme, items in groups.items():
        label = ATLAS_THEMES[theme][lang == "en"]
        count = len(items)
        unit = c["count_one" if count == 1 else "count_many"]
        links.append(f'<a class="r-atlas-group" href="#theme-{theme}"><strong>{escape(label)}</strong>'
                     f'<span>{count} {escape(unit)} →</span></a>')
    return (f'<section class="r-section" id="visual-atlas"><h2>{escape(c["heading"])}</h2>'
            f'<p class="r-section-intro">{escape(c["intro"])}</p>'
            f'<nav class="r-atlas-map" aria-label="{escape(c["heading"], quote=True)}">{"".join(links)}</nav></section>')


def render_theme_findings(groups: dict, lang: str) -> str:
    c = COPY[lang]
    e = escape
    sections = []
    for theme, items in groups.items():
        entries = []
        for number, item in items:
            copy = item[lang]
            slug = e(item["id"], quote=True)
            entries.append(f'<article class="r-entry" id="{slug}"><p class="r-kicker">{number:02d} · {e(copy["field"])}</p>'
                           f'<h4>{e(copy["title"])}</h4><p>{e(copy["result"])}</p>'
                           f'<p class="r-limit"><strong>{e(c["limit"])}:</strong> {e(copy["insight"])}</p>'
                           f'<a href="/{lang}/research/{slug}/">{e(ARTICLE_LABELS[lang]["open"])}</a>'
                           f'<a href="{REPO}/blob/main/{e(item["evidence_path"], quote=True)}">{e(c["evidence"])}</a></article>')
        sections.append(f'<section class="r-theme" id="theme-{theme}"><h3>{e(ATLAS_THEMES[theme][lang == "en"])}</h3>'
                        f'<div class="r-grid">{"".join(entries)}</div>'
                        f'<a class="r-theme-back" href="#visual-atlas">{e(ATLAS_COPY[lang]["back"])}</a></section>')
    return "".join(sections)


def research_page(journal, scenarios, verifier, lang):
    c=COPY[lang]
    e=escape
    other="en" if lang=="ro" else "ro"
    url=f"{ORIGIN}/{lang}/research/"
    groups = atlas_groups(journal)
    demos=[]
    for case,title,note in c["cases"]:
        data=scenarios["cases"][case]
        claim=c[data["claim"].lower()]
        crypto=c[data["cryptographic"].lower()]
        demos.append(f'<details class="r-demo"><summary>{e(title)}</summary><div class="r-demo-body"><p class="r-status">{e(c["mock"])}</p><p>{e(note)}</p><p><strong>{e(c["claim"])}:</strong> {e(claim)}<br><strong>{e(c["crypto"])}:</strong> {e(crypto)}</p></div></details>')
    recorded=c["record_valid" if verifier["cryptographic"]=="VALID" else "record_invalid"]
    question=journal["next_question"][lang]
    return f'''<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(c["title"])} | TAG · ROCSI</title><meta name="robots" content="noindex,nofollow"><meta name="description" content="{e(c["lead"],quote=True)}">
<link rel="canonical" href="{url}"><link rel="alternate" hreflang="ro" href="{ORIGIN}/ro/research/"><link rel="alternate" hreflang="en" href="{ORIGIN}/en/research/"><link rel="alternate" hreflang="x-default" href="{ORIGIN}/ro/research/"><link rel="icon" href="/assets/favicon.svg">
<meta property="og:title" content="{e(c["title"],quote=True)} | TAG · ROCSI"><meta property="og:description" content="{e(c["lead"],quote=True)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{ORIGIN}/og/{lang}.png"><meta property="og:type" content="website">
<style>{CSS}</style></head><body class="research-page"><div class="r-wrap">
<header class="r-header"><a class="r-brand" href="/{lang}/"><img src="/assets/rocsi-mark.svg" alt="">TAG / ROCSI</a><a href="/{lang}/">{e(c["home"])}</a>{language_dropdown(lang, "/research/", "r-lang")}</header>
<main><section class="r-hero"><p class="r-kicker">{e(c["label"])}</p><h1>{e(c["title"])}</h1><p class="r-lead">{e(c["lead"])}</p><p class="r-boundary">{e(c["boundary"])}</p><nav class="r-nav" aria-label="{e(c["title"],quote=True)}"><a href="#visual-atlas">{e(ATLAS_COPY[lang]["heading"])}</a><a href="#findings">{e(c["findings"])}</a><a href="#demonstrations">{e(c["demos"])}</a><a href="#next">{e(c["next"])}</a></nav></section>
{render_atlas_map(groups, lang)}
<section class="r-section" id="findings"><p class="r-kicker">01 / TAG</p><h2>{e(c["findings"])}</h2><p class="r-section-intro">{e(c["intro"])}</p>{render_theme_findings(groups, lang)}</section>
<section class="r-section" id="demonstrations"><p class="r-kicker">02 / TAG</p><h2>{e(c["demos"])}</h2><p class="r-section-intro">{e(c["demo_intro"])}</p><aside class="r-feature"><h3>{e(c["record"])}</h3><p>{e(recorded)}</p><p>{e(c["record_limit"])}</p></aside>{"".join(demos)}</section>
<section class="r-section" id="next"><p class="r-kicker">03 / TAG</p><h2>{e(c["next"])}</h2><div class="r-questions"><h3>{e(question["title"])}</h3><p>{e(question["description"])}</p></div></section></main>
<footer class="r-footer"><a href="{REPO}">{e(c["github"])}</a><p>{e(c["foot"])}</p><p>EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION</p></footer></div></body></html>'''


def article_page(item: dict, lang: str) -> str:
    """Static bilingual article from the checked, public-safe journal record."""
    e = escape
    labels = ARTICLE_LABELS[lang]
    copy = item[lang]
    article = item["article"][lang]
    slug = item["id"]
    other = "en" if lang == "ro" else "ro"
    url = f"{ORIGIN}/{lang}/research/{slug}/"
    other_url = f"{ORIGIN}/{other}/research/{slug}/"
    return f"""<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(copy["title"])} | TAG · ROCSI</title><meta name="robots" content="noindex,nofollow"><meta name="description" content="{e(copy["result"],quote=True)}">
<link rel="canonical" href="{url}"><link rel="alternate" hreflang="ro" href="{ORIGIN}/ro/research/{slug}/"><link rel="alternate" hreflang="en" href="{ORIGIN}/en/research/{slug}/"><link rel="alternate" hreflang="x-default" href="{ORIGIN}/ro/research/{slug}/"><link rel="icon" href="/assets/favicon.svg">
<meta property="og:title" content="{e(copy["title"],quote=True)} | TAG · ROCSI"><meta property="og:description" content="{e(copy["result"],quote=True)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{ORIGIN}/og/{lang}.png"><meta property="og:type" content="article">
<style>{CSS}</style></head><body class="research-page"><div class="r-wrap">
<header class="r-header"><a class="r-brand" href="/{lang}/"><img src="/assets/rocsi-mark.svg" alt="">TAG / ROCSI</a><a href="/{lang}/research/">{e(labels["back"])}</a>{language_dropdown(lang, "/research/" + slug + "/", "r-lang")}</header>
<main><article class="r-article" id="{slug}"><p class="r-kicker">{e(copy["field"])}</p><h1>{e(copy["title"])}</h1><p class="r-boundary">{e(COPY[lang]["boundary"])}</p>
<h2>{e(labels["question"])}</h2><p>{e(article["question"])}</p>
<h2>{e(labels["principle"])}</h2><p>{e(article["principle"])}</p>
<h2>{e(labels["formula"])}</h2><pre class="r-equation"><code>{e(item["article"]["formula"])}</code></pre>
<p>{e(article["formula_note"])}</p>
{render_visual_diagram(item, lang)}
<h2>{e(labels["method"])}</h2><p>{e(article["method"])}</p>
<h2>{e(labels["observed"])}</h2><p>{e(copy["result"])}</p>
<h2>{e(labels["interpretation"])}</h2><p>{e(article["interpretation"])}</p>
<h2>{e(labels["controls"])}</h2><p>{e(article["controls"])}</p>
<h2>{e(labels["limitations"])}</h2><p>{e(copy["insight"])}</p>
<p><a href="{REPO}/blob/main/{e(item["evidence_path"],quote=True)}">{e(labels["source"])}</a></p>
<p><a href="/{lang}/research/">{e(labels["back"])}</a></p></article></main>
<footer class="r-footer"><a href="{REPO}">{e(COPY[lang]["github"])}</a><p>{e(COPY[lang]["foot"])}</p><p>EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION</p></footer></div></body></html>"""
