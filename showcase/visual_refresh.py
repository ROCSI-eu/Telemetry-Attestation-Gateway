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

    /* TAG-VISUAL-FINAL-01: presentation only, no change to simulation or evidence. */
    .hero{grid-template-columns:minmax(0,1.04fr) minmax(0,.96fr);gap:clamp(22px,4.2vw,66px);min-height:clamp(620px,79vh,830px);padding:clamp(50px,6vw,82px) 0 clamp(55px,7vw,99px)}
    .hero h1{font-size:clamp(3.6rem,6.35vw,7.1rem);max-width:11ch;line-height:.97;margin:22px 0 25px}
    .hero .sub{max-width:57ch;color:#d4d8d6;font-size:clamp(.97rem,1.1vw,1.08rem);line-height:1.64}
    .hero-actions{margin-top:25px}
    .hero-actions a{transition:border-color .18s ease,background-color .18s ease}
    .hero-art{min-height:clamp(490px,48vw,715px);border:1px solid #355056;background:radial-gradient(ellipse at 58% 53%,#203e47 0,#0d1a20 53%,#0b1216 88%);isolation:isolate}
    .hero-art:before{content:"";position:absolute;inset:0;border:0;border-radius:0;width:auto;aspect-ratio:auto;top:0;left:0;transform:none;opacity:.75;background:repeating-linear-gradient(0deg,transparent 0 65px,#3b5a6040 66px),repeating-linear-gradient(90deg,transparent 0 65px,#3b5a6040 66px)}
    .hero-art:after{content:"";position:absolute;inset:0;border:0;border-radius:0;width:auto;aspect-ratio:auto;top:0;left:0;transform:none;opacity:1;background:linear-gradient(180deg,#0c1418ae,transparent 17%,transparent 81%,#0b151bdc)}
    .hero-scene{display:block;position:absolute;inset:0;width:100%;height:100%;z-index:1}
    .hero-art-label,.hero-art-caption,.hero-art-index{position:absolute;z-index:2;font-size:.65rem;letter-spacing:.16em;font-weight:800;text-transform:uppercase}
    .hero-art-label{top:22px;left:22px}
    .hero-art-index{top:22px;right:22px;color:#95b8b9}
    .hero-art-caption{bottom:21px;left:22px;color:#e8c58b}
    .section-overline{display:flex;align-items:center;gap:13px;line-height:1.4}
    .section-overline:before{content:"";display:inline-block;width:20px;height:2px;background:#e3be83;flex:none}
    .section-display{letter-spacing:-.065em;max-width:18ch}
    .mission-control{padding-top:clamp(75px,8vw,125px);padding-bottom:clamp(82px,9vw,140px)}
    .mission-control .section-display{margin-bottom:42px}
    .mission-layout{grid-template-columns:minmax(0,2.15fr) minmax(245px,.65fr)}
    .mission-viewport{background:radial-gradient(ellipse at 53% 52%,#16404a,#0a1419 73%);box-shadow:inset 0 0 90px #0810128a}
    .mission-readout{padding:clamp(22px,2.5vw,38px);background:linear-gradient(160deg,#102125,#0e171a)}
    .mission-readout h3{font-size:1.2rem;line-height:1.15;max-width:22ch}
    .mission-readout dt{margin-top:17px;font-size:.66rem;letter-spacing:.09em;text-transform:uppercase;color:#9cb4b5}
    .mission-readout dd{font-size:.86rem;font-weight:700;color:#d6f0ee}
    .mission-legend span{background:#0a171bcf;border:1px solid #365159}
    .mission-boundary{max-width:100ch;font-size:.75rem}
    .evidence-intro{margin-bottom:24px}
    .evidence-path{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));margin:0 0 34px;border-top:1px solid #5a6f71;border-bottom:1px solid #465759}
    .evidence-path>div{padding:22px 20px 25px;border-right:1px solid #405153;min-width:0}
    .evidence-path>div:first-child{padding-left:0}
    .evidence-path>div:last-child{border-right:0}
    .evidence-path span{display:block;color:#dfbf89;font-size:.65rem;font-weight:800;letter-spacing:.12em;margin-bottom:12px}
    .evidence-path strong{display:block;font-weight:650;color:#e9f0eb;font-size:clamp(.88rem,1.12vw,1.05rem);line-height:1.35}
    .proof-tooling{border:1px solid #405357;background:#10191c;padding:clamp(20px,3vw,36px);margin:0 0 38px;min-width:0}
    .proof-tooling-kicker,.toolchain-diagram span{color:#dfbf89;font-size:.67rem;letter-spacing:.13em;font-weight:800}
    .proof-tooling h3{font-size:clamp(1.45rem,2.2vw,2.2rem);line-height:1.18;letter-spacing:-.04em;margin:12px 0}
    .proof-tooling-intro,.proof-tooling-boundary{color:#bdcbca;font-size:.93rem;line-height:1.7;max-width:94ch}
    .toolchain-diagram{list-style:none;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px;padding:0;margin:26px 0}
    .toolchain-diagram li{position:relative;min-width:0;padding:20px 18px;background:#16252a;border-top:2px solid #bda072}
    .toolchain-diagram li:not(:last-child):after{content:"→";position:absolute;right:-17px;top:38%;z-index:1;color:#dfbf89;font-size:1.3rem}
    .toolchain-diagram strong{display:block;color:#edf0e8;font-size:1.1rem;margin:9px 0}
    .toolchain-diagram p{color:#c2d0ce;font-size:.85rem;line-height:1.62;margin:0}
    .proof-tooling-links{display:flex;gap:10px 22px;flex-wrap:wrap;font-size:.83rem;margin:0 0 22px}
    .proof-tooling-links a{color:#e7c58e;text-underline-offset:3px}
    .proof-tooling-boundary{border-left:2px solid #bda072;padding-left:15px;margin:0}
    .technical-evidence .layout{align-items:stretch}
    .technical-evidence .card{background:#10191c;border-color:#3b5052}
    .technical-evidence .card h2{color:#f4f0e6}
    .technical-evidence .step{border-top:2px solid #bda072}
    .technical-evidence .metric{border-left:2px solid #47767d}
    @media(max-width:1120px){
      .hero{grid-template-columns:minmax(0,1.1fr) minmax(0,.9fr)}
      .hero h1{font-size:clamp(3.4rem,6.6vw,6rem)}
    }
    @media(max-width:750px){
      .hero{grid-template-columns:1fr;min-height:0;gap:19px;padding:35px 0 47px}
      .hero h1{font-size:clamp(2.7rem,10.5vw,4.3rem);margin:12px 0 17px;line-height:1.01;letter-spacing:-.055em}
      .hero .sub{font-size:.92rem;line-height:1.52}
      .hero-actions{margin-top:21px;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));width:100%;gap:8px}
      .hero-actions a{display:flex;align-items:center;justify-content:center;text-align:center;font-size:.72rem;letter-spacing:.01em;padding:12px 9px;line-height:1.35;min-height:47px}
      .hero-art{min-height:315px}
      .hero-art-label,.hero-art-caption,.hero-art-index{font-size:.54rem}
      .hero-art-label{top:16px;left:15px}.hero-art-index{top:16px;right:15px}.hero-art-caption{bottom:15px;left:15px}
      .section-display{font-size:clamp(2.45rem,8vw,3.9rem)}
      .mission-control .section-display{margin-bottom:27px}
      .mission-layout{grid-template-columns:minmax(0,1fr)}
      .mission-viewport{min-width:0}
      .mission-viewport svg{width:125%;max-width:none;transform:translateX(-10%)}
      .mission-legend{position:relative;inset:auto;justify-content:space-between;padding:0 10px 10px;font-size:.58rem}
      .mission-readout{padding:20px 22px}
      .evidence-path{grid-template-columns:repeat(2,minmax(0,1fr))}
      .evidence-path>div{padding:20px 12px;border-bottom:1px solid #405153}
      .evidence-path>div:nth-child(odd){padding-left:0}
      .evidence-path>div:nth-child(even){border-right:0;padding-right:0}
      .evidence-path>div:nth-last-child(-n+2){border-bottom:0}
      .toolchain-diagram{grid-template-columns:1fr;gap:9px}
      .toolchain-diagram li:not(:last-child):after{display:none}
    }
    @media(max-width:420px){
      .hero h1{font-size:clamp(2.65rem,10.6vw,3.3rem)}
      .hero-actions a{width:auto;font-size:.68rem}
      .hero-art{min-height:260px}
      .hero .sub{font-size:.91rem}
    }
    @media(prefers-reduced-motion:reduce){
      .hero-actions a{transition:none}
    }
"""


TECH_TOOLING = """  <section class="proof-tooling" aria-labelledby="proof-tooling-title">
    <p class="proof-tooling-kicker">EXPERIMENTAL PROOF TOOLCHAIN</p>
    <h3 id="proof-tooling-title">How Noir and Barretenberg are used in TAG</h3>
    <p class="proof-tooling-intro">The synthetic bounded-speed experiment uses a pinned research toolchain: Noir/Nargo 1.0.0-beta.26 and Barretenberg bb 5.2.0. This is not a production technology selection.</p>
    <ol class="toolchain-diagram" aria-label="Experimental proof flow, executed offline">
      <li><span>01 / DEFINE</span><strong>Noir</strong><p>Noir expresses a constraint comparing a private speed value with a public limit; Nargo compiles the circuit.</p></li>
      <li><span>02 / PROVE</span><strong>Barretenberg</strong><p>With the private witness, the pinned bb backend generates a zero-knowledge proof of the constrained statement.</p></li>
      <li><span>03 / VERIFY</span><strong>Offline verifier</strong><p>A separately invoked verifier reconstructs public inputs from canonical CBOR and checks the proof with the expected verification key, without the private speed.</p></li>
    </ol>
    <nav class="proof-tooling-links" aria-label="Tool documentation and TAG implementation">
      <a href="https://www.noir-lang.org/docs/">Noir documentation</a>
      <a href="https://barretenberg.aztec.network/docs/">Barretenberg documentation</a>
      <a href="https://github.com/ROCSI-eu/Telemetry-Attestation-Gateway/tree/main/experiments/bounded-speed-proof-v0">TAG experimental implementation</a>
    </nav>
    <p class="proof-tooling-boundary">A cryptographically valid proof does not establish telemetry truth, trusted sensors or time, whole-flight coverage, safety or legal compliance. This public page shows recorded synthetic outcomes: the browser neither generates nor verifies a proof.</p>
  </section>
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
      <p class="sub">TAG explores verification without disclosing all telemetry. This public scene is synthetic and its separate verifier result was recorded offline; the browser neither connects to vehicles nor verifies proofs.</p>
      <div class="hero-actions"><a href="#mission-control">Explore the scene</a><a href="#technical-evidence">Review the evidence</a></div>
    </div>
    <div class="hero-art" aria-hidden="true">
      <span class="hero-art-label">TAG / SYNTHETIC OBSERVATION</span>
      <span class="hero-art-index">A–B–C / 01</span>
      <svg class="hero-scene" viewBox="0 0 760 700" preserveAspectRatio="xMidYMid meet" focusable="false">
        <defs>
          <linearGradient id="hero-craft-shell" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stop-color="#f4eddb"/><stop offset=".44" stop-color="#91c8cf"/><stop offset="1" stop-color="#27536a"/>
          </linearGradient>
          <linearGradient id="hero-craft-wing" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stop-color="#78c8d6"/><stop offset="1" stop-color="#1d4f60"/>
          </linearGradient>
          <radialGradient id="hero-craft-halo">
            <stop offset="0" stop-color="#328e9b" stop-opacity=".24"/><stop offset="1" stop-color="#328e9b" stop-opacity="0"/>
          </radialGradient>
        </defs>
        <circle cx="382" cy="346" r="286" fill="url(#hero-craft-halo)"/>
        <g class="hero-reticle" fill="none" stroke="#70969b" stroke-width="1">
          <circle cx="385" cy="346" r="225" opacity=".22"/>
          <circle cx="385" cy="346" r="145" opacity=".26"/>
          <path d="M385 74V618 M118 346H650" opacity=".15"/>
          <path d="M116 536L202 506M594 203L662 161" opacity=".58"/>
        </g>
        <path d="M98 548 C235 514 298 446 389 350 S559 228 681 136" fill="none" stroke="#172c35" stroke-width="30" opacity=".5"/>
        <path d="M98 548 C235 514 298 446 389 350 S559 228 681 136" fill="none" stroke="#78d4db" stroke-width="3" stroke-dasharray="13 12" opacity=".92"/>
        <g fill="#e6c28a" stroke="#1a3338" stroke-width="5">
          <circle cx="98" cy="548" r="10"/><circle cx="389" cy="350" r="10"/><circle cx="681" cy="136" r="10"/>
        </g>
        <g fill="#d8e3df" font-size="19" font-family="Arial,Helvetica,sans-serif" font-weight="700" letter-spacing="3">
          <text x="75" y="584">A</text><text x="414" y="341">B</text><text x="684" y="118">C</text>
        </g>
        <g class="hero-vehicle" transform="translate(389 350) rotate(-24)">
          <ellipse cx="2" cy="66" rx="122" ry="26" fill="#020b12" opacity=".5"/>
          <path d="M-120 -35L-58 -13 M58 -13L120 -35 M-62 21L-102 70 M62 21L102 70" stroke="#447d8d" stroke-width="17" stroke-linecap="round"/>
          <g fill="#5bb8be" opacity=".72">
            <ellipse cx="-120" cy="-35" rx="48" ry="12"/><ellipse cx="120" cy="-35" rx="48" ry="12"/>
            <ellipse cx="-102" cy="70" rx="39" ry="10"/><ellipse cx="102" cy="70" rx="39" ry="10"/>
          </g>
          <path d="M-67 -16L0 -60L67 -16L0 38Z" fill="url(#hero-craft-shell)" stroke="#e3f5ef" stroke-width="3"/>
          <path d="M-67 -16L0 38L0 62L-67 2Z" fill="url(#hero-craft-wing)"/>
          <path d="M67 -16L0 38L0 62L67 2Z" fill="#143f54"/>
          <path d="M0 -60L0 38" fill="none" stroke="#f5e9cb" stroke-width="2" opacity=".7"/>
          <path d="M-39 -11L0 -36L39 -11" fill="none" stroke="#d7e9e7" stroke-width="2"/>
          <circle cx="0" cy="-16" r="8" fill="#e8c58b"/>
        </g>
        <g fill="none" stroke="#c5d2cc" opacity=".45" stroke-width="1">
          <path d="M443 354H586V390"/><path d="M236 502H124V463"/>
        </g>
        <g font-family="Arial,Helvetica,sans-serif" fill="#c2dbdc" font-size="13" letter-spacing="2">
          <text x="593" y="409">OBS / 02</text><text x="90" y="453">ROUTE / SYN</text>
        </g>
      </svg>
      <span class="hero-art-caption">A0 / SYNTHETIC · OBSERVATION ONLY</span>
    </div>
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
        '    <p class="evidence-intro">The orchestration is simulated. The separate verifier outcome was recorded offline; the browser displays both without independently checking proofs.</p>\n    <div class="evidence-path" role="group" aria-label="Conceptual evidence path, not executed in the browser">\n      <div><span>01 / CLAIM</span><strong>Predefined condition</strong></div>\n      <div><span>02 / PROOF</span><strong>Synthetic research artifact</strong></div>\n      <div><span>03 / CHECK</span><strong>Recorded offline result</strong></div>\n      <div><span>04 / DECISION</span><strong>Not made on this page</strong></div>\n    </div>\n'
        + TECH_TOOLING + evidence + '  </section>\n'
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
