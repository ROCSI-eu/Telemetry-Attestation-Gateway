"""EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION.

Public research page: static editorial evidence and native HTML disclosure only.
"""
from html import escape

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
.r-lang{display:flex;gap:5px}
.r-lang a{padding:5px 10px;border:1px solid #566263;text-decoration:none;font-size:.8rem}
.r-lang a[aria-current=page]{background:#eacb91;color:#151a1a}
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
.r-entry h3{font-size:1.2rem;line-height:1.3;color:#f1e4cb;margin:5px 0 12px}
.r-entry p{margin:0 0 12px;color:#d2dbd5}
.r-entry .r-limit{border-top:1px solid #405052;padding-top:12px;color:#c3cbc4;font-size:.92rem}
.r-entry a{margin-top:auto;font-size:.88rem}
.r-article{max-width:880px;margin:0 auto;padding:28px 0 60px}
.r-article h1{font-size:clamp(2rem,4.5vw,3.6rem);line-height:1.12;margin:0 0 15px;color:#f5f1e6}
.r-article h2{font-size:1.45rem;line-height:1.25;margin:28px 0 10px;color:#eacb91}
.r-article p{color:#d2dbd5;margin:0 0 16px}
.r-article .r-equation{border:1px solid #596567;background:#141f22;padding:19px;white-space:pre-wrap;overflow-wrap:anywhere;color:#f1e4cb;font-size:1rem}
.r-diagram{border:1px solid #506263;background:#162427;padding:22px;margin:22px 0}
.r-diagram ol{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:25px;margin:10px 0;padding:0;list-style:none;counter-reset:stage}
.r-diagram li{position:relative;border:1px solid #76807b;padding:14px 11px;text-align:center;min-height:74px;color:#f1e4cb;display:flex;align-items:center;justify-content:center;counter-increment:stage}
.r-diagram li:not(:last-child):after{content:'→';position:absolute;right:-22px;font-size:1.3rem;color:#eacb91}
.r-diagram figcaption{color:#aebdb6;font-size:.88rem;margin-top:12px}
.r-article a{overflow-wrap:anywhere}
@media(max-width:560px){.r-diagram ol{grid-template-columns:1fr;gap:26px}.r-diagram li:not(:last-child):after{content:'↓';right:50%;top:auto;bottom:-28px;transform:translateX(50%)}}
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
"""
COPY = {
"ro": {
 "home":"Prezentare", "title":"Cercetare și rezultate experimentale", "label":"ROCSI / Telemetry Attestation Gateway",
 "lead":"Ce-am demonstrat în laborator, ce limite au rezultatele și ce întrebări rămân deschise. O evidență cumulativă a cercetării TAG, separată de prezentarea generală.",
 "boundary":"EXPERIMENTAL · DOAR DATE SINTETICE · A0_SYNTHETIC · FĂRĂ VALIDARE SAU AUTORIZARE OPERAȚIONALĂ",
 "findings":"Rezultate documentate", "demos":"Explorează demonstrațiile", "next":"Direcții deschise",
 "intro":"Rezultatele confirmate sunt prezentate de la cel mai recent la cel mai vechi. Fiecare include observația, semnificația și limita ei, cu trimitere la documentația tehnică.",
 "limit":"Ce înseamnă și ce nu demonstrează", "evidence":"Documentația experimentului",
 "demo_intro":"Exemple selectate din scenarii deterministe, pentru înțelegerea deciziilor. Deschide un exemplu pentru a vedea rezultatul înregistrat; nu se execută un prover sau un verificator.",
 "record":"Rezultat criptografic preînregistrat", "record_valid":"Verificatorul offline a acceptat o dovadă sintetică.", "record_invalid":"Verificatorul offline a respins o dovadă sintetică.",
 "record_limit":"Aceasta este o consemnare JSON minimizată, neautentificată de browser, nu o dovadă verificată aici. Nu confirmă sursa, prospețimea sau adevărul telemetriei.",
 "mock":"Simulare a fluxului", "claim":"Condiție", "crypto":"Rezultat criptografic simulat",
 "satisfied":"Îndeplinită", "not_satisfied":"Neîndeplinită", "valid":"Acceptat", "invalid":"Respins", "not_checked":"Neverificat",
 "cases":[("below_limit_local_publication","Condiție îndeplinită","Fluxul simulat continuă până la verificare."),("over_limit","Limită depășită","Condiția nu este îndeplinită; nu se verifică o dovadă."),("tampered_proof","Dovadă alterată","Chiar dacă rezultatul condiției este favorabil, verificarea simulată respinge dovada.")],
 "foot":"Cercetare ROCSI. Fără telemetrie reală, comenzi, calcule criptografice în browser sau autorizare operațională.",
 "github":"Repository și documentație", "cta":"Explorează cercetarea", "home_progress":"Am demonstrat experimental legarea unei dovezi de o observație semnată, protecția împotriva reutilizării și verificarea prospețimii recepției cu o autoritate temporală simulată. Rezultatele detaliate și limitele sunt disponibile în secțiunea de cercetare."
},
"en": {
 "home":"Overview", "title":"Research and experimental results", "label":"ROCSI / Telemetry Attestation Gateway",
 "lead":"What we have demonstrated in the lab, what the results cannot establish, and what remains open. A cumulative record of TAG research, separate from the general overview.",
 "boundary":"EXPERIMENTAL · SYNTHETIC ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION",
 "findings":"Documented findings", "demos":"Explore the demonstrations", "next":"Open research directions",
 "intro":"Confirmed findings appear newest first. Each records what was observed, what it means and its limitation, with a reference to the technical evidence.",
 "limit":"Meaning and limitations", "evidence":"Experiment documentation",
 "demo_intro":"Selected deterministic scenarios help explain the decision flow. Expand an example to see the recorded outcome; no prover or verifier is executed.",
 "record":"Recorded cryptographic result", "record_valid":"An offline verifier accepted a synthetic proof.", "record_invalid":"An offline verifier rejected a synthetic proof.",
 "record_limit":"This is a minimized JSON record, not authenticated by the browser, not a proof verified here. It does not establish source identity, freshness or telemetry truth.",
 "mock":"Simulated flow", "claim":"Condition", "crypto":"Simulated cryptographic result",
 "satisfied":"Satisfied", "not_satisfied":"Not satisfied", "valid":"Accepted", "invalid":"Rejected", "not_checked":"Not checked",
 "cases":[("below_limit_local_publication","Condition satisfied","The simulated flow proceeds to verification."),("over_limit","Limit exceeded","The condition is not met; no proof is checked."),("tampered_proof","Tampered proof","Even with a favorable condition outcome, simulated verification rejects the proof.")],
 "foot":"ROCSI research. No real telemetry, commands, browser cryptography or operational authorization.",
 "github":"Repository and documentation", "cta":"Explore the research", "home_progress":"We experimentally demonstrated proof binding to a signed observation, replay protection and reception freshness checks with a simulated time authority. Detailed findings and limitations are available in the research section."
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

def research_page(journal, scenarios, verifier, lang):
    c=COPY[lang]
    e=escape
    other="en" if lang=="ro" else "ro"
    url=f"{ORIGIN}/{lang}/research/"
    entries=[]
    for item in reversed(journal["entries"]):
        copy=item[lang]
        entries.append(f'<article class="r-entry" id="{e(item["id"])}"><p class="r-kicker">{e(copy["field"])}</p><h3>{e(copy["title"])}</h3><p>{e(copy["result"])}</p><p class="r-limit"><strong>{e(c["limit"])}:</strong> {e(copy["insight"])}</p><a href="/{lang}/research/{e(item["id"])}/">{e(ARTICLE_LABELS[lang]["open"])}</a><a href="{REPO}/blob/main/{e(item["evidence_path"],quote=True)}">{e(c["evidence"])}</a></article>')
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
<header class="r-header"><a class="r-brand" href="/{lang}/"><img src="/assets/rocsi-mark.svg" alt="">TAG / ROCSI</a><a href="/{lang}/">{e(c["home"])}</a><nav class="r-lang" aria-label="Limbă / Language"><a href="/ro/research/" hreflang="ro" lang="ro" aria-current="{"page" if lang=="ro" else "false"}">RO</a><a href="/en/research/" hreflang="en" lang="en" aria-current="{"page" if lang=="en" else "false"}">EN</a></nav></header>
<main><section class="r-hero"><p class="r-kicker">{e(c["label"])}</p><h1>{e(c["title"])}</h1><p class="r-lead">{e(c["lead"])}</p><p class="r-boundary">{e(c["boundary"])}</p><nav class="r-nav" aria-label="{e(c["title"],quote=True)}"><a href="#findings">{e(c["findings"])}</a><a href="#demonstrations">{e(c["demos"])}</a><a href="#next">{e(c["next"])}</a></nav></section>
<section class="r-section" id="findings"><p class="r-kicker">01 / TAG</p><h2>{e(c["findings"])}</h2><p class="r-section-intro">{e(c["intro"])}</p><div class="r-grid">{"".join(entries)}</div></section>
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
    stages = "".join(f"<li>{e(stage)}</li>" for stage in article["stages"])
    return f"""<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(copy["title"])} | TAG · ROCSI</title><meta name="robots" content="noindex,nofollow"><meta name="description" content="{e(copy["result"],quote=True)}">
<link rel="canonical" href="{url}"><link rel="alternate" hreflang="ro" href="{ORIGIN}/ro/research/{slug}/"><link rel="alternate" hreflang="en" href="{ORIGIN}/en/research/{slug}/"><link rel="alternate" hreflang="x-default" href="{ORIGIN}/ro/research/{slug}/"><link rel="icon" href="/assets/favicon.svg">
<meta property="og:title" content="{e(copy["title"],quote=True)} | TAG · ROCSI"><meta property="og:description" content="{e(copy["result"],quote=True)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{ORIGIN}/og/{lang}.png"><meta property="og:type" content="article">
<style>{CSS}</style></head><body class="research-page"><div class="r-wrap">
<header class="r-header"><a class="r-brand" href="/{lang}/"><img src="/assets/rocsi-mark.svg" alt="">TAG / ROCSI</a><a href="/{lang}/research/">{e(labels["back"])}</a><nav class="r-lang" aria-label="Limbă / Language"><a href="/ro/research/{slug}/" hreflang="ro" lang="ro" aria-current="{"page" if lang=="ro" else "false"}">RO</a><a href="/en/research/{slug}/" hreflang="en" lang="en" aria-current="{"page" if lang=="en" else "false"}">EN</a></nav></header>
<main><article class="r-article" id="{slug}"><p class="r-kicker">{e(copy["field"])}</p><h1>{e(copy["title"])}</h1><p class="r-boundary">{e(COPY[lang]["boundary"])}</p>
<h2>{e(labels["question"])}</h2><p>{e(article["question"])}</p>
<h2>{e(labels["principle"])}</h2><p>{e(article["principle"])}</p>
<h2>{e(labels["formula"])}</h2><pre class="r-equation"><code>{e(item["article"]["formula"])}</code></pre>
<p>{e(article["formula_note"])}</p>
<figure class="r-diagram"><ol>{stages}</ol><figcaption>{e(labels["figure"])}</figcaption></figure>
<h2>{e(labels["method"])}</h2><p>{e(article["method"])}</p>
<h2>{e(labels["observed"])}</h2><p>{e(copy["result"])}</p>
<h2>{e(labels["interpretation"])}</h2><p>{e(article["interpretation"])}</p>
<h2>{e(labels["controls"])}</h2><p>{e(article["controls"])}</p>
<h2>{e(labels["limitations"])}</h2><p>{e(copy["insight"])}</p>
<p><a href="{REPO}/blob/main/{e(item["evidence_path"],quote=True)}">{e(labels["source"])}</a></p>
<p><a href="/{lang}/research/">{e(labels["back"])}</a></p></article></main>
<footer class="r-footer"><a href="{REPO}">{e(COPY[lang]["github"])}</a><p>{e(COPY[lang]["foot"])}</p><p>EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION</p></footer></div></body></html>"""
