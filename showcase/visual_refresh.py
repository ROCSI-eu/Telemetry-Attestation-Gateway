"""Presentation-only transformation of the isolated public TAG showcase.

The source console, synthetic animation logic, typed evidence, and trust boundaries
remain unchanged. No new scripts, requests, fonts, images or operator controls.
"""
from __future__ import annotations

import re


VISUAL_CSS = """
    /* TAG-VISUAL-REFRESH-01: original industrial editorial presentation. */
    :root{color:#f1f0eb;background:#0a0d0e;font-family:Arial,Helvetica,system-ui,sans-serif}
    body{background:radial-gradient(circle at 88% 4%,#243037 0,transparent 27%),#0a0d0e;color:#f1f0eb}
    a{color:#e7c58e}
    a:focus-visible,button:focus-visible,select:focus-visible{outline-color:#f1d4a2}
    .wrap{max-width:1560px;padding:0 clamp(18px,5vw,92px) 88px}
    .site-header{display:flex;align-items:center;gap:30px;flex-wrap:wrap;min-height:94px;border-bottom:1px solid #3d4548}
    .brand{display:flex;align-items:center;gap:15px;text-decoration:none;color:#f7f4eb;min-width:0}
    .brand-signal{font-size:1.72rem;font-weight:900;letter-spacing:-.09em}
    .brand-detail{font-size:.66rem;letter-spacing:.13em;text-transform:uppercase;color:#c2c7c8;max-width:160px;line-height:1.5}
    .section-nav{display:flex;gap:clamp(12px,2vw,34px);flex-wrap:wrap;align-items:center;margin-left:auto}
    .section-nav a{text-decoration:none;font-size:.73rem;letter-spacing:.06em;color:#cbd0cf}
    .section-nav a:hover{color:#fff}
    .header-status{display:flex;align-items:center;gap:12px;flex-wrap:wrap}
    .header-status .pill{font-size:.62rem;letter-spacing:.07em;border-color:#555c5d;color:#c7cdcc;background:transparent}
    .hero{display:grid;grid-template-columns:minmax(0,1.6fr) minmax(230px,.65fr);gap:5vw;align-items:stretch;min-height:clamp(520px,68vh,800px);padding:clamp(68px,9vw,155px) 0 clamp(58px,7vw,115px);border-bottom:1px solid #3d4548}
    .hero-content{display:flex;flex-direction:column;align-items:start;justify-content:center;min-width:0}
    .hero-overline,.section-overline,.hero-art-label,.hero-art-caption{font-size:.69rem;letter-spacing:.2em;text-transform:uppercase;font-weight:800;color:#e3be83}
    .hero h1{font-size:clamp(3.3rem,7.2vw,8.7rem);max-width:11ch;line-height:.99;letter-spacing:-.072em;font-weight:820;margin:22px 0 30px;text-wrap:balance}
    .hero .sub{font-size:clamp(.95rem,1.12vw,1.15rem);max-width:69ch;line-height:1.7;color:#c6ccca}
    .hero-actions{display:flex;gap:12px;flex-wrap:wrap;margin-top:35px}
    .hero-actions a{display:inline-block;text-decoration:none;font-size:.78rem;font-weight:750;letter-spacing:.06em;padding:14px 18px;border:1px solid #707b7d;color:#f0efea}
    .hero-actions a:first-child{background:#e5c18a;border-color:#e5c18a;color:#111617}
    .hero-actions a:hover{border-color:#eee6d5}
    .hero-art{position:relative;overflow:hidden;min-height:320px;background:radial-gradient(circle at 53% 47%,#25373b 0,transparent 55%),repeating-linear-gradient(0deg,transparent 0 47px,#31404455 48px),repeating-linear-gradient(90deg,transparent 0 47px,#31404455 48px);border:1px solid #394548}
    .hero-art:before,.hero-art:after{content:"";position:absolute;border:1px solid #7c9b96;border-radius:50%;width:75%;aspect-ratio:1;top:50%;left:50%;transform:translate(-50%,-50%);opacity:.6}
    .hero-art:after{width:47%;border-color:#d9b77f;opacity:.8}
    .hero-art .hero-axis{position:absolute;left:12%;right:12%;top:50%;border-top:1px solid #a8b7ae;transform:rotate(-28deg)}
    .hero-art .hero-axis:after{content:"";position:absolute;right:0;top:-5px;width:9px;height:9px;background:#e5c18a;border-radius:50%}
    .hero-art-label,.hero-art-caption{position:absolute;z-index:1;left:20px;color:#d4d7cf}
    .hero-art-label{top:20px}.hero-art-caption{bottom:20px;color:#e3be83}
    .notice{margin:25px 0 0;padding:14px 18px;background:transparent;border:1px solid #5b5c4e;border-left:3px solid #d9b77f;border-radius:0;color:#e7ded0;letter-spacing:.05em}
    .primer,.use-cases,.mission-control,.technical-evidence,.research-limits{scroll-margin-top:26px}
    .primer{background:transparent;border:0;border-bottom:1px solid #353f41;border-radius:0;margin:0;padding:clamp(75px,10vw,150px) 0;max-width:none;display:grid;grid-template-columns:minmax(0,.8fr) minmax(0,1.2fr);column-gap:5vw}
    .primer .primer-kicker{grid-column:1;grid-row:1/5;font-size:.72rem;color:#e2c08b;letter-spacing:.2em}
    .primer h2{font-size:clamp(2.25rem,4.2vw,5.25rem);line-height:1.07;letter-spacing:-.055em;color:#f7f4eb;margin:0 0 28px;text-wrap:balance}
    .primer p{grid-column:2;font-size:1rem;line-height:1.74;color:#c7cdcb}
    .primer .primer-example{border-left:2px solid #d8b67b;padding-left:20px;color:#eee7d9}
    .primer .primer-links{grid-column:2;display:flex;gap:12px 26px;font-size:.81rem;letter-spacing:.03em}
    .section-overline{margin:0 0 16px}
    .section-display{font-size:clamp(2.45rem,4.5vw,5.6rem);font-weight:780;line-height:1.07;letter-spacing:-.06em;margin:0 0 32px;max-width:14ch;text-wrap:balance}
    .mission-control{background:transparent;border:0;border-bottom:1px solid #374245;box-shadow:none;border-radius:0;padding:clamp(76px,8vw,132px) 0;margin:0}
    .mission-control .section-display{max-width:none}
    .mission-top{border-top:1px solid #536063;padding-top:24px;gap:30px;margin-bottom:24px}
    .mission-top h2{font-size:1.24rem;letter-spacing:-.025em;color:#efece4}
    .mission-top .small{max-width:64ch;line-height:1.7}
    .mission-label{color:#dbbc88}
    .mission-layout{grid-template-columns:minmax(0,1.85fr) minmax(245px,.65fr);gap:0}
    .mission-viewport{border-radius:0;border-color:#3f5558;background:radial-gradient(ellipse at 65% 45%,#193c45,#0b1318 72%)}
    .mission-readout{background:#10191b;border:0;border-left:1px solid #3f5558;border-radius:0;padding:25px}
    .mission-timeline{border-radius:0;margin-top:0;background:#1d2b30}
    .mission-timeline-fill{background:#d9bd8a}
    .mission-boundary{color:#b7c1c0;line-height:1.65}
    .mission-legend span{background:#0b1416e8;border-radius:0}
    .mission-actions{gap:8px}
    .mission-actions select,select{background:#151d20;border-color:#758384;border-radius:0;color:#f3f0e9}
    button{background:#dbbc88;color:#101617;border-radius:0}
    button:hover:not(:disabled){background:#efd6a7}
    .use-cases{padding:clamp(75px,8vw,130px) 0;margin:0;border-bottom:1px solid #374245}
    .use-cases h2{font-size:clamp(2.2rem,4vw,4.5rem);line-height:1.08;letter-spacing:-.055em;max-width:18ch;margin-bottom:44px}
    .use-cases-grid{gap:0;border-top:1px solid #465255}
    .use-cases article{background:transparent;border:0;border-bottom:1px solid #465255;border-right:1px solid #465255;border-radius:0;padding:33px 25px 34px 0}
    .use-cases article:not(:first-child){padding-left:25px}
    .use-cases article:last-child{border-right:0}
    .use-cases h3{color:#eee8da;font-size:1.3rem;letter-spacing:-.035em;margin-bottom:18px}
    .use-cases p{color:#bfc8c7;font-size:.95rem;line-height:1.75}
    .technical-evidence{padding:clamp(76px,9vw,140px) 0;border-bottom:1px solid #374245}
    .technical-evidence .section-display{max-width:none}
    .evidence-intro{color:#bfc7c6;max-width:68ch;line-height:1.7;margin:0 0 40px}
    .layout{gap:12px}
    .card{background:#121a1c;border:1px solid #435052;border-radius:0;box-shadow:none;padding:clamp(18px,2.4vw,35px)}
    .card h2{font-size:1.35rem;letter-spacing:-.03em}
    .step{border-radius:0;background:#192226;border-color:#495b5e}
    .metric{border-radius:0;background:#0f171a;border-color:#38494c}
    .metric b{color:#f5ebd8}
    .kicker{color:#becac7}
    .status{border-radius:0}
    .small,dt{color:#b6c3c2}
    #authentic-panel{margin-top:12px}
    .research-limits{padding:clamp(76px,9vw,140px) 0 10px}
    .research-limits .section-display{max-width:none}
    .scope-disclosure{background:transparent;border:1px solid #556063;border-radius:0;margin:32px 0 0;padding:25px}
    .scope-disclosure summary{font-size:1.08rem;color:#e6c58f}
    .scope article{border-radius:0;background:#141e21}
    .scope h2{color:#f2eee5}
    footer{border-top:1px solid #3d4548;padding-top:27px;line-height:1.7;color:#aeb7b6}
    .language-switch{border-color:#596567;border-radius:0}
    .language-switch a,.language-switch a[aria-current="page"]{border-radius:0}
    .language-switch a[aria-current="page"]{background:#d9bd8a;color:#151918}
    @media(max-width:1120px){.site-header{padding:16px 0}.section-nav{order:3;flex-basis:100%;margin-left:0}.hero{grid-template-columns:minmax(0,1.4fr) minmax(180px,.6fr)}.hero h1{font-size:clamp(3.2rem,7vw,6.5rem)}}
    @media(max-width:750px){
      .wrap{padding:0 16px 60px}
      .site-header{gap:12px;min-height:70px}
      .brand{gap:10px}.brand-detail{max-width:130px}
      .header-status{margin-left:auto}
      .header-status .pill{display:none}
      .section-nav{gap:16px;overflow-x:auto;flex-wrap:nowrap;padding-bottom:8px}
      .section-nav a{white-space:nowrap}
      .hero{grid-template-columns:1fr;gap:36px;padding:64px 0 70px;min-height:0}
      .hero h1{font-size:clamp(3.05rem,12vw,5.7rem);margin:16px 0 25px}
      .hero-art{min-height:230px}
      .primer{display:block;padding:72px 0}
      .primer .primer-kicker{margin-bottom:24px}
      .primer h2{font-size:clamp(2.2rem,8vw,4rem)}
      .primer p{font-size:.95rem}
      .mission-control{padding:75px 0}
      .mission-layout{grid-template-columns:1fr}
      .mission-readout{border:1px solid #3f5558;border-top:0}
      .use-cases{padding:75px 0}
      .use-cases-grid{grid-template-columns:1fr}
      .use-cases article,.use-cases article:not(:first-child){border-right:0;padding:24px 0}
      .technical-evidence{padding:75px 0}
      .research-limits{padding:75px 0}
    }
    @media(max-width:420px){.brand-detail{font-size:.58rem}.section-nav{flex-wrap:wrap;overflow-x:visible;gap:7px 16px;padding-bottom:0}.section-nav a{white-space:normal;font-size:.69rem}.hero h1{font-size:clamp(2.75rem,12.2vw,3.3rem)}.hero-actions a{width:100%;text-align:center}.mission-actions select{min-width:0;width:100%}.mission-actions label{width:100%}.mission-actions{width:100%}.mission-actions button{flex:1}.hero-art{min-height:205px}}
"""


def redesign_public_html(html: str) -> str:
    """Reorder known public-only sections, fail closed on source changes."""
    original_header = re.search(r"<header>.*?</header>", html, flags=re.S)
    if original_header is None or html.count("<header>") != 1:
        raise ValueError("unexpected public hero source")
    intro_text = re.search(r'<p class="sub">([^<]+)</p>', original_header.group())
    if intro_text is None:
        raise ValueError("public introduction changed")

    header = f"""<header class="site-header">
    <a class="brand" href="/" aria-label="TAG · ROCSI"><span class="brand-signal">TAG</span><span class="brand-detail">ROCSI / Telemetry Attestation Gateway</span></a>
    <nav class="section-nav" aria-label="Page sections">
      <a href="#principle">The Principle</a>
      <a href="#mission-control">Mission Observability</a>
      <a href="#technical-evidence">Technical Evidence</a>
    </nav>
    <div class="header-status"><div class="pill" id="console-mode">PUBLIC SHOWCASE · PRECOMPUTED ONLY</div></div>
  </header>
  <section class="hero" aria-labelledby="hero-title">
    <div class="hero-content">
      <p class="hero-overline">EXPERIMENTAL / SYNTHETIC-ONLY RESEARCH</p>
      <h1 id="hero-title">Verify the condition. Keep the rest private.</h1>
      <p class="sub">{intro_text.group(1)}</p>
      <div class="hero-actions"><a href="#mission-control">Explore the illustration</a><a href="#technical-evidence">Review technical evidence</a></div>
    </div>
    <div class="hero-art" aria-hidden="true"><span class="hero-art-label">TAG / EXPERIMENT</span><span class="hero-axis"></span><span class="hero-art-caption">A0 / SYNTHETIC</span></div>
  </section>"""
    html = html.replace(original_header.group(), header, 1)

    anchors = [
        '  <section class="primer"',
        '  <section class="use-cases"',
        '  <details class="scope-disclosure"',
        '  <section class="mission-control"',
        '  <div class="layout">',
        '  <footer id="console-footer">',
    ]
    if any(html.count(a) != 1 for a in anchors):
        raise ValueError("public section anchor mismatch")
    a, b, c, d, e, f = (html.index(anchor) for anchor in anchors)
    if not a < b < c < d < e < f:
        raise ValueError("public section ordering drift")
    intro, applications = html[a:b], html[b:c]
    scope, mission, evidence = html[c:d], html[d:e], html[e:f]

    intro = intro.replace('class="primer" aria', 'class="primer" id="principle" aria', 1)
    intro = intro.replace("THE CONCEPT IN BRIEF", "01 / THE PRINCIPLE", 1)
    applications = applications.replace(
        '<h2 id="use-cases-title">',
        '<p class="section-overline">03 / POTENTIAL APPLICATIONS</p>\n    <h2 id="use-cases-title">',
        1,
    )
    mission = mission.replace(
        'aria-labelledby="mission-title">\n',
        'aria-labelledby="mission-title">\n'
        '    <p class="section-overline">02 / OBSERVATIONAL RESEARCH</p>\n'
        '    <h2 class="section-display">Mission Observability</h2>\n',
        1,
    )
    technical = (
        '  <section class="technical-evidence" id="technical-evidence" aria-labelledby="technical-evidence-title">\n'
        '    <p class="section-overline">04 / EVIDENCE BOUNDARIES</p>\n'
        '    <h2 class="section-display" id="technical-evidence-title">Technical Evidence</h2>\n'
        '    <p class="evidence-intro">The orchestration is simulated. The separate verifier outcome was recorded offline; the browser displays both without independently checking proofs.</p>\n'
        + evidence + '  </section>\n'
    )
    research = (
        '  <section class="research-limits" id="research-limitations" aria-labelledby="research-limitations-title">\n'
        '    <p class="section-overline">05 / EXPERIMENTAL BOUNDARY</p>\n'
        '    <h2 class="section-display" id="research-limitations-title">Research &amp; Limitations</h2>\n'
        + scope + '  </section>\n'
    )
    html = html[:a] + intro + mission + applications + technical + research + html[f:]
    if html.count("</style>") != 1:
        raise ValueError("public style shape changed")
    return html.replace("</style>", VISUAL_CSS + "  </style>", 1)
