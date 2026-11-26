"""Presentation-only transformation of the isolated public TAG showcase.

The source console, synthetic animation logic, typed evidence, and trust boundaries
remain unchanged. The decorative hero SVG has CSS-only animation; no new scripts,
requests, fonts, external assets or operator controls.
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
    .brand{display:flex;align-items:center;gap:11px;text-decoration:none;color:#f7f4eb;min-width:0}
    .brand-rocsi-mark{display:block;width:34px;height:34px;flex:none;object-fit:contain}
    .brand-signal{font-size:1.72rem;font-weight:900;letter-spacing:-.09em}
    .brand-detail{font-size:.66rem;letter-spacing:.13em;text-transform:uppercase;color:#c2c7c8;max-width:160px;line-height:1.5}
    .section-nav{display:flex;gap:clamp(12px,2vw,34px);flex-wrap:wrap;align-items:center;margin-left:auto}
    .section-nav a{text-decoration:none;font-size:.73rem;letter-spacing:.06em;color:#cbd0cf}
    .section-nav a:hover{color:#fff}
    .header-status{display:flex;align-items:center;gap:12px;flex-wrap:wrap}
    .header-cta{display:inline-flex;align-items:center;justify-content:center;min-height:42px;padding:9px 13px;border:1px solid #dfbb83;color:#f6e5c9;text-decoration:none;font-size:.74rem;font-weight:750;letter-spacing:.02em;line-height:1.3;text-align:center}
    .header-cta:hover{background:#dfbb83;color:#121717}
    .header-cta:focus-visible{outline:2px solid #f1d4a2;outline-offset:3px}
    .header-status .pill{font-size:.62rem;letter-spacing:.07em;border-color:#555c5d;color:#c7cdcc;background:transparent}
    .hero{display:grid;grid-template-columns:minmax(0,1.6fr) minmax(230px,.65fr);gap:5vw;align-items:stretch;min-height:clamp(520px,68vh,800px);padding:clamp(68px,9vw,155px) 0 clamp(58px,7vw,115px);border-bottom:1px solid #3d4548}
    .hero-content{display:flex;flex-direction:column;align-items:start;justify-content:center;min-width:0}
    .hero-overline,.section-overline,.hero-art-label{font-size:.69rem;letter-spacing:.2em;text-transform:uppercase;font-weight:800;color:#e3be83}
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
    .hero-art-label{position:absolute;z-index:1;left:20px;color:#d4d7cf}
    .hero-art-label{top:20px}
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
    .mission-control{background:transparent;border:0;border-bottom:1px solid #374245;box-shadow:none;border-radius:0;padding:clamp(48px,5.2vw,76px) 0;margin:0}
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
    .use-cases{padding:clamp(48px,5vw,76px) 0;margin:0;border-bottom:0}
    .use-cases h2{font-size:clamp(2.2rem,4vw,4.5rem);line-height:1.08;letter-spacing:-.055em;max-width:18ch;margin-bottom:29px}
    .use-cases>.editorial-chapter-intro{max-width:74ch;margin-bottom:30px}
    .use-cases-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:13px;align-items:stretch}
    .use-cases .use-case-card{display:flex;flex-direction:column;align-items:flex-start;min-width:0;margin:0;padding:clamp(20px,2.15vw,29px);border:1px solid #41575a;background:linear-gradient(155deg,#142326,#0d181b);border-radius:0}
    .use-case-icon-wrap{width:46px;height:46px;display:grid;place-items:center;flex:none;border:1px solid #4d7273;background:#192f32;margin-bottom:21px}
    .use-case-icon{display:block;width:27px;height:27px;fill:none;stroke:#d9c18f;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
    .use-cases .use-case-card h3{color:#eee8da;font-size:clamp(1.13rem,1.65vw,1.33rem);line-height:1.25;letter-spacing:-.025em;margin:0 0 12px}
    .use-cases .use-case-card p{color:#c4cecb;font-size:.92rem;line-height:1.7;margin:0;max-width:43ch}
    @media(max-width:1100px) and (min-width:751px){.use-cases-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
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
    .research-limits{padding:clamp(50px,5.5vw,82px) 0 0}
    .research-limits .section-display{max-width:none}
    .scope-disclosure{background:transparent;border:1px solid #556063;border-radius:0;margin:32px 0 0;padding:25px}
    .scope-disclosure summary{font-size:1.08rem;color:#e6c58f}
    .scope article{border-radius:0;background:#141e21}
    .scope h2{color:#f2eee5}
    .rocsi-affiliation{display:grid;grid-template-columns:60px minmax(0,1fr) auto;align-items:center;column-gap:clamp(18px,2.5vw,30px);row-gap:18px;margin:30px 0 0;padding:clamp(22px,2.8vw,36px);border:1px solid #4b6366;background:linear-gradient(120deg,#17292c,#101c1f)}
    .rocsi-affiliation-copy{min-width:0}
    .rocsi-affiliation h3{color:#f2e9d8;font-size:clamp(1.2rem,1.65vw,1.5rem);line-height:1.35;letter-spacing:-.02em;margin:0}
    .rocsi-affiliation p{margin:9px 0 0;color:#c1ccca;font-size:.94rem;line-height:1.65;max-width:66ch}
    .rocsi-affiliation-actions{display:flex;align-items:center;justify-content:flex-end;min-width:0}
    .rocsi-affiliation-mark{display:block;width:60px;height:60px;flex:none;object-fit:contain}
    .rocsi-affiliation-actions>a{display:inline-flex;align-items:center;justify-content:center;min-height:46px;padding:11px 18px;border:1px solid #d7b77f;color:#efd5a7;font-size:.86rem;font-weight:750;text-decoration:none;text-align:center}
    .rocsi-affiliation-actions>a:hover{background:#d7b77f;color:#11191b}
    .rocsi-affiliation-actions>a:focus-visible{outline:2px solid #f1d4a2;outline-offset:3px}
    @media(max-width:750px){.rocsi-affiliation{grid-template-columns:48px minmax(0,1fr);column-gap:16px;row-gap:14px}.rocsi-affiliation-actions{grid-column:2;justify-content:flex-start}.rocsi-affiliation-mark{width:48px;height:48px}.header-status{max-width:100%;justify-content:flex-end}}
    footer{border-top:1px solid #344446;margin-top:28px;padding:22px 0 8px;line-height:1.75;color:#c6cfcb;font-size:.87rem}
    .language-switch{border-color:#596567;border-radius:0}
    .language-switch a,.language-switch a[aria-current="page"]{border-radius:0}
    .language-switch a[aria-current="page"]{background:#d9bd8a;color:#151918}
    @media(max-width:1120px){.site-header{padding:16px 0}.section-nav{order:3;flex-basis:100%;margin-left:0}.hero{grid-template-columns:minmax(0,1.4fr) minmax(180px,.6fr)}.hero h1{font-size:clamp(3.2rem,7vw,6.5rem)}}
    @media(max-width:750px){
      .wrap{padding:0 16px 60px}
      .site-header{gap:12px;min-height:70px}
      .brand{gap:9px}.brand-detail{max-width:130px}.brand-rocsi-mark{width:29px;height:29px}
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
      .mission-control{padding:52px 0}
      .mission-layout{grid-template-columns:1fr}
      .mission-readout{border:1px solid #3f5558;border-top:0}
      .use-cases{padding:52px 0}
      .use-cases-grid{grid-template-columns:1fr;gap:12px}
      .use-cases .use-case-card{padding:22px}
      .use-case-icon-wrap{margin-bottom:17px}
      .technical-evidence{padding:75px 0}
      .research-limits{padding:58px 0 0}
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
    .hero-art-label{position:absolute;z-index:2;top:22px;left:22px;font-size:.69rem;letter-spacing:.13em}
    .section-overline{display:flex;align-items:center;gap:13px;line-height:1.4}
    .section-overline:before{content:"";display:inline-block;width:20px;height:2px;background:#e3be83;flex:none}
    .section-display{letter-spacing:-.065em;max-width:18ch}
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
    .proof-evidence-checkpoint{border:1px solid #405357;background:#142125;padding:18px 20px;margin:8px 0 24px}
    .proof-evidence-checkpoint h4{color:#e7c58e;font-size:.8rem;letter-spacing:.08em;text-transform:uppercase;margin:0 0 10px}
    .proof-evidence-checkpoint p{color:#c2d0ce;font-size:.87rem;line-height:1.62;margin:8px 0}
    .proof-tooling-links{display:flex;gap:10px 22px;flex-wrap:wrap;font-size:.83rem;margin:0 0 22px}
    .proof-tooling-links a{color:#e7c58e;text-underline-offset:3px}
    .proof-tooling-boundary{border-left:2px solid #bda072;padding-left:15px;margin:0}


    /* TAG-AUTO-CINEMATIC-01: synthetic education, never a live proof status. */
    .tech-animation{margin:0;padding:clamp(12px,1.6vw,18px);border:1px solid #45656b;background:radial-gradient(ellipse at 49% 15%,#183743,#0b171d 78%);min-width:0;overflow:hidden;isolation:isolate}
    .tech-scene-scroll{max-width:100%;min-width:0;overflow:hidden}
    .tech-scene-scroll:focus-visible{outline:2px solid #e3c58e;outline-offset:3px}
    .tech-animation svg{display:block;width:100%;height:auto;max-width:1060px;margin:0 auto;overflow:visible}
    .tech-animation-top{display:flex;align-items:center;gap:12px;justify-content:space-between}
    .tech-animation-label{font-size:.68rem;font-weight:800;letter-spacing:.12em;color:#e2c58e;text-transform:uppercase}
    .tech-animation-caption{margin:8px 0 15px;color:#b8c9ca;font-size:.82rem;line-height:1.5}
    .tech-animation-status{font-size:.78rem;color:#c4d0cd;line-height:1.6;min-height:1.3em;margin:13px 0 0}
    .tech-panel{fill:url(#tech-chassis);stroke:#60848b;stroke-width:1.8}
    .tech-panel-depth{fill:#07151d;stroke:#416872;stroke-width:1.1}
    .tech-panel-sheen{fill:url(#tech-reflection);opacity:.65}
    .tech-highlight{fill:url(#tech-panel-glow);stroke:#9ee5db;stroke-width:2;opacity:.10}
    .tech-workspace{fill:url(#tech-workspace-glass);stroke:#8cc6c9;stroke-width:2}
    .tech-glyph{fill:none;stroke:#b1e4df;stroke-width:3.6;stroke-linecap:round;stroke-linejoin:round}
    .tech-guide{fill:none;stroke:#699ea4;stroke-width:2;stroke-dasharray:5 9;opacity:.6}
    .tech-transfer{fill:#c4fff3;opacity:0;filter:url(#tech-soft-glow)}
    .tech-status-led{fill:#e1c38a;opacity:.86}
    .tech-scan{fill:url(#tech-scan-gradient);opacity:.23}
    .tech-mini-text{fill:#a9d1cf;opacity:.65}
    .tech-secret{fill:#203a40;stroke:#dfc58a;stroke-width:2}
    .tech-public{fill:#dfc48b}
    .tech-animation[data-started="true"] .tech-highlight-one{animation:tech-cycle-one 15s ease-in-out infinite}
    .tech-animation[data-started="true"] .tech-highlight-two{animation:tech-cycle-two 15s ease-in-out infinite}
    .tech-animation[data-started="true"] .tech-highlight-three{animation:tech-cycle-three 15s ease-in-out infinite}
    .tech-animation[data-started="true"] .tech-transfer-one{animation:tech-packet-one 15s ease-in-out infinite}
    .tech-animation[data-started="true"] .tech-transfer-two{animation:tech-packet-two 15s ease-in-out infinite}
    .tech-animation[data-started="true"] .tech-scan{animation:tech-scan 15s linear infinite}
    .tech-animation[data-started="true"] .tech-status-led{animation:tech-led 3.8s ease-in-out infinite}
    .tech-animation[data-visibility="hidden"] .tech-highlight,
    .tech-animation[data-visibility="hidden"] .tech-transfer,
    .tech-animation[data-visibility="hidden"] .tech-scan,
    .tech-animation[data-visibility="hidden"] .tech-status-led{animation-play-state:paused}
    @keyframes tech-cycle-one{0%,10%{opacity:.09}14%,28%{opacity:.8}33%,100%{opacity:.09}}
    @keyframes tech-cycle-two{0%,36%{opacity:.09}42%,57%{opacity:.8}62%,100%{opacity:.09}}
    @keyframes tech-cycle-three{0%,65%{opacity:.09}70%,89%{opacity:.8}95%,100%{opacity:.09}}
    @keyframes tech-packet-one{0%,26%{opacity:0;transform:translateX(-18px)}30%{opacity:1}39%{opacity:0;transform:translateX(34px)}100%{opacity:0}}
    @keyframes tech-packet-two{0%,59%{opacity:0;transform:translateX(-16px)}65%{opacity:1}72%{opacity:0;transform:translateX(34px)}100%{opacity:0}}
    @keyframes tech-scan{0%{transform:translateX(-250px);opacity:0}5%{opacity:.35}25%{opacity:0;transform:translateX(55px)}100%{opacity:0;transform:translateX(55px)}}
    @keyframes tech-led{0%,100%{opacity:.52}50%{opacity:1}}
    @media(max-width:750px){
      .tech-animation{padding:10px;margin:0}
      .tech-scene-scroll{overflow-x:auto;overscroll-behavior-inline:contain;scrollbar-width:thin;scrollbar-color:#719fa4 #112930}
      .tech-scene-scroll svg{width:820px;max-width:none}
    }
    @media(prefers-reduced-motion:reduce){
      .tech-animation .tech-highlight,.tech-animation .tech-transfer,.tech-animation .tech-scan,.tech-animation .tech-status-led{animation:none!important}
      .tech-animation .tech-highlight{opacity:.3}
      .tech-animation .tech-transfer,.tech-animation .tech-scan{opacity:0}
    }
    /* TAG-MISSION-SCENARIOS-01: explanation of a recorded mock, not proof execution. */
    /* TAG-SCENARIOS-UX-01: public-only hierarchy; never changes typed evidence. */
    .scenario-controller,.scenario-results{border-top:2px solid #d3b783}
    .scenario-controller .controls{margin-bottom:13px}
    .scenario-explanation{margin:12px 0 20px;padding:17px 19px;border-left:3px solid #dfc08c;background:#1b2b30;color:#eef1e9;font-size:clamp(.87rem,1vw,.96rem);line-height:1.65;overflow-wrap:anywhere}
    .scenario-active{margin:-6px 0 17px;padding:0 0 13px;border-bottom:1px solid #384d4e;color:#e0c392;font-size:.75rem;font-weight:750;letter-spacing:.045em;line-height:1.5;overflow-wrap:anywhere}
    .scenario-results dd[data-tone]{justify-self:end;padding:2px 7px;border-left:2px solid #657477;line-height:1.4;max-width:100%}
    .scenario-results dd[data-tone="good"]{color:#a7e1cc;background:#183730;border-left-color:#74c7ae}
    .scenario-results dd[data-tone="warn"]{color:#f0d0a4;background:#392a22;border-left-color:#e2b779}
    .scenario-results dd[data-tone="neutral"]{color:#c5cecb;background:#202a2c;border-left-color:#657477}
    @media(max-width:750px){.scenario-explanation{padding:15px 16px;font-size:.89rem}.scenario-active{font-size:.71rem}}

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
      .hero-art-label{top:16px;left:15px;font-size:.62rem}
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

    /* TAG-HERO-CINEMATIC-01: deterministic, decorative synthetic SVG; no real footage or telemetry. */
    .hero-art{background:#071116;box-shadow:inset 0 0 75px #01090ab8,0 14px 52px #01070938}
    .hero-art:before{opacity:.24;background:repeating-linear-gradient(0deg,transparent 0 72px,#6e9b9e35 73px),repeating-linear-gradient(90deg,transparent 0 72px,#6e9b9e35 73px)}
    .hero-art:after{background:linear-gradient(180deg,#071216cf 0,transparent 20%,transparent 79%,#061117ea 100%),linear-gradient(90deg,#0711168e,transparent 20%,transparent 82%,#0711168e);pointer-events:none}
    .hero-scene{overflow:hidden}
    .hero-vehicle{transform-box:view-box;transform-origin:0 0;animation:hero-hover 10s ease-in-out infinite;will-change:transform}
    .hero-floor-shadow{animation:hero-shadow-drift 10s ease-in-out infinite;transform-origin:402px 416px}
    .hero-sweep{transform-origin:385px 350px;animation:hero-radar-sweep 22s linear infinite}
    .hero-route-flow{animation:hero-route-drift 11s linear infinite}
    .hero-rotor-disc{transform-box:fill-box;transform-origin:center;animation:hero-propeller .24s linear infinite;will-change:transform}
    .hero-rotor:nth-of-type(even) .hero-rotor-disc{animation-direction:reverse}
    .hero-beacon-pulse{transform-box:fill-box;transform-origin:center;animation:hero-beacon 4.5s ease-out infinite}
    .hero-waypoints>g:last-child .hero-beacon-pulse{animation-delay:-2.3s}
    .hero-spotlight,.hero-landscape{pointer-events:none}
    @keyframes hero-hover{
      0%,100%{transform:translate(389px,350px) rotate(-1.8deg)}
      26%{transform:translate(399px,339px) rotate(.7deg)}
      54%{transform:translate(379px,347px) rotate(1.4deg)}
      78%{transform:translate(394px,356px) rotate(-.6deg)}
    }
    @keyframes hero-shadow-drift{0%,100%{transform:translate(0,0) scale(1)}50%{transform:translate(-5px,7px) scale(.93)}}
    @keyframes hero-radar-sweep{to{transform:rotate(360deg)}}
    @keyframes hero-route-drift{to{stroke-dashoffset:-390}}
    @keyframes hero-propeller{to{transform:rotate(360deg)}}
    @keyframes hero-beacon{0%,100%{opacity:.15;transform:scale(.8)}45%{opacity:.65;transform:scale(1.2)}80%{opacity:.12;transform:scale(1.42)}}
    @media(prefers-reduced-motion:reduce){
      .hero-vehicle,.hero-floor-shadow,.hero-sweep,.hero-route-flow,.hero-rotor-disc,.hero-beacon-pulse{animation:none!important;will-change:auto}
    }


    /* TAG-MISSION-AUTO-VISUAL-01: predetermined paths, no telemetry. */
    .mission-viewport{background:radial-gradient(ellipse at 54% 44%,#16434d,#081319 75%);box-shadow:inset 0 0 75px #01080c9e;isolation:isolate}
    .mission-viewport:after{content:"";position:absolute;inset:0;pointer-events:none;background:linear-gradient(180deg,#06121786,transparent 21%,transparent 78%,#0612176e);z-index:1}
    .mission-viewport .mission-grid{stroke:#6e98a0;opacity:.19}
    .mission-path-underlay{stroke:#0b2936;stroke-width:15}
    .mission-path{stroke:#80d4dc;stroke-width:2.3;opacity:.64}
    .mission-route-energy{fill:none;stroke:#baffec;stroke-width:2.7;stroke-dasharray:8 24;stroke-linecap:round;opacity:.77;animation:mission-flow 12s linear infinite}
    .mission-range-ring{fill:none;stroke:#77b5ba;stroke-width:1;opacity:.20}
    .mission-radar-sector{fill:url(#mission-radar-wash);opacity:.43;transform-origin:430px 190px;animation:mission-radar-cinema 22s linear infinite}
    .mission-waypoint-halo{fill:none;stroke:#a5f0dc;stroke-width:1.2;opacity:.45;transform-box:fill-box;transform-origin:center;animation:mission-waypoint-breathe 5s ease-in-out infinite}
    .mission-waypoint-b{animation-delay:-1.8s}
    .mission-craft{transform:translate(120px,290px);will-change:transform}
    .mission-control[data-scene-started="true"][data-scene="pass"] .mission-craft{animation:mission-cinema-pass 18s ease-in-out infinite}
    .mission-control[data-scene-started="true"][data-scene="hold"] .mission-craft{animation:mission-cinema-hold 14s ease-in-out infinite}
    .mission-control[data-scene-started="true"][data-scene="return"] .mission-craft{animation:mission-cinema-return 20s ease-in-out infinite}
    .mission-control[data-scene="return"] .mission-route-energy{animation-direction:reverse}
    .mission-control[data-scene-started="true"] .mission-timeline-fill{animation:mission-progress 18s linear infinite}
    .mission-control[data-scene="hold"] .mission-timeline-fill{animation-duration:14s}
    .mission-control[data-scene="return"] .mission-timeline-fill{animation-duration:20s}
    .mission-control[data-visibility="hidden"] .mission-route-energy,
    .mission-control[data-visibility="hidden"] .mission-radar-sector,
    .mission-control[data-visibility="hidden"] .mission-waypoint-halo,
    .mission-control[data-visibility="hidden"] .mission-rotor-blades{animation-play-state:paused}
    .mission-rotor-blades{transform-box:fill-box;transform-origin:center;animation:mission-rotor-spin .35s linear infinite;will-change:transform}
    .mission-rotor:nth-of-type(2n) .mission-rotor-blades{animation-direction:reverse}
    .mission-craft-hull{fill:url(#mission-hull-glass);stroke:#d8f3eb;stroke-width:1.3}
    .mission-craft-arm{stroke:url(#mission-arm-metal);stroke-width:7;stroke-linecap:round}
    .mission-craft-light{fill:#f0d39b}
    .mission-craft-shadow{fill:#020b10;opacity:.42}
    @keyframes mission-flow{to{stroke-dashoffset:-384}}
    @keyframes mission-radar-cinema{to{transform:rotate(360deg)}}
    @keyframes mission-rotor-spin{to{transform:rotate(360deg)}}
    @keyframes mission-waypoint-breathe{0%,100%{opacity:.18;transform:scale(.9)}50%{opacity:.73;transform:scale(1.32)}}
    @keyframes mission-cinema-pass{
      0%,100%{transform:translate(120px,290px) rotate(-4deg)}
      24%{transform:translate(272px,247px) rotate(1deg)}
      48%{transform:translate(426px,192px) rotate(-2deg)}
      74%{transform:translate(590px,139px) rotate(2deg)}
      92%{transform:translate(714px,87px) rotate(-2deg)}
    }
    @keyframes mission-cinema-hold{
      0%,100%{transform:translate(120px,290px) rotate(-3deg)}
      43%{transform:translate(424px,194px) rotate(1deg)}
      54%,77%{transform:translate(430px,188px) rotate(-1deg)}
      66%,88%{transform:translate(430px,198px) rotate(1deg)}
    }
    @keyframes mission-cinema-return{
      0%,100%{transform:translate(120px,290px) rotate(-3deg)}
      45%{transform:translate(430px,194px) rotate(2deg)}
      52%{transform:translate(430px,188px) rotate(-5deg)}
      82%{transform:translate(252px,255px) rotate(-6deg)}
    }
    @media(max-width:750px){.mission-viewport svg{width:100%;max-width:100%;transform:none}}
    @media(prefers-reduced-motion:reduce){
      .mission-control .mission-craft{animation:none!important;transform:translate(430px,194px);will-change:auto}
      .mission-control .mission-route-energy,.mission-control .mission-radar-sector,.mission-control .mission-waypoint-halo,.mission-control .mission-rotor-blades,.mission-control .mission-timeline-fill{animation:none!important;will-change:auto}
      .mission-control .mission-route-energy{opacity:.25}
    }

    @media(prefers-reduced-motion:reduce){
      .hero-actions a{transition:none}
    }
"""


HERO_SCENE_SVG = r'''<svg class="hero-scene" viewBox="0 0 760 700" preserveAspectRatio="xMidYMid meet" focusable="false" aria-hidden="true">
        <defs>
          <radialGradient id="hero-ambient" cx="51%" cy="47%" r="67%">
            <stop stop-color="#224b54"/><stop offset=".44" stop-color="#102a33"/><stop offset="1" stop-color="#060d13"/>
          </radialGradient>
          <radialGradient id="hero-bloom">
            <stop stop-color="#8adce0" stop-opacity=".36"/><stop offset=".45" stop-color="#2a7883" stop-opacity=".14"/><stop offset="1" stop-color="#1c485b" stop-opacity="0"/>
          </radialGradient>
          <radialGradient id="hero-spotlight">
            <stop stop-color="#d8eacc" stop-opacity=".24"/><stop offset=".28" stop-color="#6bb0b2" stop-opacity=".10"/><stop offset="1" stop-color="#62b1c2" stop-opacity="0"/>
          </radialGradient>
          <linearGradient id="hero-route-light" x1="0" y1="1" x2="1" y2="0">
            <stop stop-color="#297b89"/><stop offset=".52" stop-color="#b4f2e6"/><stop offset="1" stop-color="#56bdd0"/>
          </linearGradient>
          <linearGradient id="hero-shell" x1="0" y1="0" x2=".86" y2="1">
            <stop stop-color="#f2f3e6"/><stop offset=".13" stop-color="#98b9b9"/><stop offset=".42" stop-color="#304c54"/><stop offset=".68" stop-color="#152e37"/><stop offset="1" stop-color="#091c29"/>
          </linearGradient>
          <linearGradient id="hero-shell-side" x1="0" y1="0" x2=".94" y2="1">
            <stop stop-color="#86bcc4"/><stop offset=".32" stop-color="#345c69"/><stop offset="1" stop-color="#071923"/>
          </linearGradient>
          <linearGradient id="hero-carbon" x1="0" y1="0" x2="0" y2="1">
            <stop stop-color="#708c94"/><stop offset=".12" stop-color="#253f49"/><stop offset=".51" stop-color="#101f2b"/><stop offset=".83" stop-color="#304c54"/><stop offset="1" stop-color="#07151d"/>
          </linearGradient>
          <linearGradient id="hero-canopy" x1="0" y1="0" x2=".9" y2=".9">
            <stop stop-color="#d6f5ed"/><stop offset=".16" stop-color="#81d2db"/><stop offset=".42" stop-color="#285b6f"/><stop offset=".75" stop-color="#142f42"/><stop offset="1" stop-color="#071b2e"/>
          </linearGradient>
          <radialGradient id="hero-engine">
            <stop stop-color="#e2f3ea"/><stop offset=".22" stop-color="#82bec7"/><stop offset=".55" stop-color="#345865"/><stop offset="1" stop-color="#0b222c"/>
          </radialGradient>
          <linearGradient id="hero-rotor-blade" x1="0" y1="0" x2="1" y2="1">
            <stop stop-color="#c3eaec" stop-opacity=".78"/><stop offset=".5" stop-color="#5399a3" stop-opacity=".6"/><stop offset="1" stop-color="#173f4a" stop-opacity=".7"/>
          </linearGradient>
          <linearGradient id="hero-radar" x1="0" y1="0" x2="1" y2=".85">
            <stop stop-color="#8cf4e0" stop-opacity=".24"/><stop offset=".75" stop-color="#66b8c7" stop-opacity=".06"/><stop offset="1" stop-color="#66b8c7" stop-opacity="0"/>
          </linearGradient>
          <pattern id="hero-panel-texture" width="11" height="11" patternUnits="userSpaceOnUse">
            <path d="M0 11L11 0" fill="none" stroke="#bbd8dc" stroke-opacity=".06" stroke-width=".7"/>
          </pattern>
          <filter id="hero-soft-shadow" x="-65%" y="-200%" width="230%" height="500%">
            <feGaussianBlur stdDeviation="14"/>
          </filter>
          <filter id="hero-soft-beacon" x="-300%" y="-300%" width="700%" height="700%">
            <feGaussianBlur stdDeviation="6"/>
          </filter>
        </defs>
        <rect width="760" height="700" fill="url(#hero-ambient)"/>
        <ellipse cx="407" cy="345" rx="350" ry="300" fill="url(#hero-bloom)"/>
        <ellipse cx="566" cy="206" rx="248" ry="245" fill="url(#hero-spotlight)"/>
        <g class="hero-landscape" fill="none" stroke="#688b8e" stroke-width="1" opacity=".15">
          <path d="M-32 518C137 439 229 519 380 451S639 350 809 374"/>
          <path d="M-40 545C147 465 222 549 393 470S639 368 811 395"/>
          <path d="M-34 573C151 499 236 577 405 486S646 398 805 417"/>
          <path d="M-45 599C137 535 264 597 436 512S639 429 813 453"/>
          <path d="M-33 625C155 561 268 616 446 543S664 470 817 481"/>
          <path d="M-24 647C158 597 268 652 452 578S655 500 813 515"/>
        </g>
        <g class="hero-grid-perspective" fill="none" stroke="#4b7480" stroke-width="1" opacity=".2">
          <path d="M381 70V677M105 345H652M25 483H735M62 555H702"/>
          <path d="M380 70L-130 700M380 70L105 700M380 70L650 700M380 70L891 700"/>
        </g>
        <g class="hero-radar" fill="none" stroke="#a2d0cb" stroke-width="1">
          <circle cx="385" cy="350" r="228" opacity=".15"/>
          <circle cx="385" cy="350" r="163" opacity=".2"/>
          <circle cx="385" cy="350" r="88" opacity=".18"/>
          <circle cx="385" cy="350" r="290" stroke-dasharray="3 16" opacity=".18"/>
          <path d="M385 90V609M124 350H647" opacity=".14"/>
          <path d="M154 307h19m-9-9v19M602 389h19m-9-9v19" opacity=".46"/>
        </g>
        <g class="hero-sweep">
          <path d="M385 350L385 121A229 229 0 0 1 590 248Z" fill="url(#hero-radar)"/>
          <path d="M385 350L590 248" stroke="#baf6e6" stroke-opacity=".2" stroke-width="1.4"/>
        </g>
        <path d="M98 548C225 522 305 439 389 350S569 203 681 136" fill="none" stroke="#031016" stroke-width="22" opacity=".65"/>
        <path d="M98 548C225 522 305 439 389 350S569 203 681 136" fill="none" stroke="url(#hero-route-light)" stroke-width="8" opacity=".09"/>
        <path class="hero-route-static" d="M98 548C225 522 305 439 389 350S569 203 681 136" fill="none" stroke="#86d5dc" stroke-width="2.1" stroke-dasharray="9 13" opacity=".72"/>
        <path class="hero-route-flow" d="M98 548C225 522 305 439 389 350S569 203 681 136" fill="none" stroke="#d8fbef" stroke-width="2.7" stroke-dasharray="2 37" stroke-linecap="round"/>
        <g class="hero-waypoints">
          <g transform="translate(98 548)">
            <circle r="27" fill="#93e8da" opacity=".19" filter="url(#hero-soft-beacon)"/>
            <circle class="hero-beacon-pulse" r="18" fill="none" stroke="#9de9d7" stroke-width="1.4" opacity=".55"/>
            <circle r="8.5" fill="#dfbf8a" stroke="#d6ebd7" stroke-width="2"/>
          </g>
          <g transform="translate(389 350)">
            <circle r="24" fill="#96dfdd" opacity=".16" filter="url(#hero-soft-beacon)"/>
            <circle r="8" fill="#e0c18e" stroke="#d8f1e7" stroke-width="2"/>
          </g>
          <g transform="translate(681 136)">
            <circle r="27" fill="#9fe7df" opacity=".18" filter="url(#hero-soft-beacon)"/>
            <circle class="hero-beacon-pulse" r="18" fill="none" stroke="#9de9d7" stroke-width="1.4" opacity=".55"/>
            <circle r="8.5" fill="#dfbf8a" stroke="#d6ebd7" stroke-width="2"/>
          </g>
        </g>
        <g fill="#e1ebe6" font-family="Arial,Helvetica,sans-serif" font-size="17" letter-spacing="3" font-weight="750">
          <text x="78" y="582">A</text><text x="409" y="340" opacity=".68">B</text><text x="683" y="117">C</text>
        </g>
        <g class="hero-floor-shadow">
          <ellipse cx="402" cy="416" rx="147" ry="30" transform="rotate(-22 402 416)" fill="#02080e" opacity=".82" filter="url(#hero-soft-shadow)"/>
          <ellipse cx="399" cy="419" rx="99" ry="11" transform="rotate(-22 399 419)" fill="#020b10" opacity=".7"/>
        </g>
        <g class="hero-vehicle" transform="translate(389 350)">
          <g transform="rotate(-20)">
            <ellipse cx="0" cy="8" rx="187" ry="127" fill="url(#hero-bloom)" opacity=".24"/>
            <!-- Forged, shaded rear arms and lift-motor pods: conceptual vehicle only. -->
            <path d="M-46 -20L-148 -84L-160 -64L-61 5M51 -19L154 -83L166 -63L63 6" fill="url(#hero-carbon)" stroke="#6d9ca2" stroke-width="2.1" stroke-linejoin="round"/>
            <path d="M-48 28L-145 106L-131 122L-20 52M54 28L155 103L142 120L23 52" fill="url(#hero-carbon)" stroke="#548592" stroke-width="2.1" stroke-linejoin="round"/>
            <g class="hero-rotor hero-rotor-rear" transform="translate(-150 -76)">
              <ellipse rx="55" ry="18" fill="#76bfbe" opacity=".13"/>
              <ellipse rx="48" ry="14" fill="none" stroke="#93d2d0" stroke-width="1.3" opacity=".4"/>
              <g class="hero-rotor-disc">
                <ellipse rx="52" ry="8" fill="url(#hero-rotor-blade)" opacity=".84"/>
                <ellipse rx="53" ry="6.5" fill="url(#hero-rotor-blade)" transform="rotate(77)" opacity=".49"/>
              </g>
              <ellipse ry="10" rx="13" fill="url(#hero-engine)" stroke="#a1bec1" stroke-width="2"/>
              <ellipse ry="3" rx="5" cy="-3" fill="#d7e9e0" opacity=".8"/>
            </g>
            <g class="hero-rotor hero-rotor-rear" transform="translate(158 -76)">
              <ellipse rx="55" ry="18" fill="#76bfbe" opacity=".13"/>
              <ellipse rx="48" ry="14" fill="none" stroke="#93d2d0" stroke-width="1.3" opacity=".4"/>
              <g class="hero-rotor-disc">
                <ellipse rx="52" ry="8" fill="url(#hero-rotor-blade)" opacity=".84"/>
                <ellipse rx="53" ry="6.5" fill="url(#hero-rotor-blade)" transform="rotate(77)" opacity=".49"/>
              </g>
              <ellipse ry="10" rx="13" fill="url(#hero-engine)" stroke="#a1bec1" stroke-width="2"/>
              <ellipse ry="3" rx="5" cy="-3" fill="#d7e9e0" opacity=".8"/>
            </g>
            <path d="M-57 -37L-23 -75L36 -71L71 -33L70 32L35 70L-32 68L-68 29Z" fill="#081822" stroke="#5a8d9a" stroke-width="4"/>
            <path d="M-58 -34L-25 -72L36 -67L71 -32L62 29L30 61L-33 60L-64 26Z" fill="url(#hero-shell)" stroke="#b4d4d2" stroke-width="2.3"/>
            <path d="M-58 -34L-25 -72L-6 -40L-24 56L-64 26Z" fill="#7aa4ad" opacity=".45"/>
            <path d="M71 -32L62 29L30 61L39 -34Z" fill="url(#hero-shell-side)" opacity=".88"/>
            <path d="M-21 -61L30 -59L43 -19L23 34L-27 31L-37 -12Z" fill="url(#hero-canopy)" stroke="#cde3df" stroke-width="2"/>
            <path d="M-29 -13L-17 -47L26 -46" fill="none" stroke="#edfbef" stroke-opacity=".86" stroke-width="3.2" stroke-linecap="round"/>
            <path d="M-31 20L24 26L37 -13" fill="none" stroke="#99c7cc" stroke-opacity=".37" stroke-width="1.1"/>
            <path d="M-55 30L-28 52L29 54L56 27" fill="none" stroke="#051925" stroke-width="5" opacity=".85"/>
            <path d="M-51 32L-27 54L28 56" fill="none" stroke="#d3e9df" stroke-width="1.1" opacity=".62"/>
            <path d="M-58 -33L-20 -65L36 -66" fill="none" stroke="#fcfff3" stroke-width="1.8" opacity=".8"/>
            <path d="M-62 -17L-62 22M68 -24L64 17" stroke="#d7efea" opacity=".46" stroke-width="1.5"/>
            <path d="M-40 40l14 8m7-4l14 4m7-2l13 -1" stroke="#081722" stroke-width="4" stroke-linecap="round"/>
            <path d="M-44 40l11 6m7 0l12 4" stroke="#a4bec0" stroke-width=".8" opacity=".8"/>
            <path d="M-55 -34L-24 -67L36 -66L70 -32L61 29L29 62L-32 60L-63 25Z" fill="url(#hero-panel-texture)" opacity=".5"/>
            <g class="hero-optics" transform="translate(0 44)">
              <path d="M-23 10L-19 26L18 26L22 10" fill="#172e38" stroke="#7097a1" stroke-width="1.5"/>
              <rect x="-13" y="16" width="26" height="16" rx="4" fill="#0c1a24" stroke="#a4bfc0" stroke-width="1.7"/>
              <circle cx="0" cy="24" r="7.5" fill="#070e18" stroke="#6fabb9" stroke-width="2"/>
              <circle cx="0" cy="24" r="3.5" fill="#266777"/>
              <circle cx="-2" cy="21" r="1.2" fill="#d3f6ed"/>
            </g>
            <circle cx="-42" cy="-26" r="3.5" fill="#e9c790"/>
            <circle cx="46" cy="-25" r="3.2" fill="#8df3e0"/>
            <circle cx="-42" cy="-26" r="12" fill="#d6af75" opacity=".33" filter="url(#hero-soft-beacon)"/>
            <circle cx="46" cy="-25" r="12" fill="#7bdece" opacity=".4" filter="url(#hero-soft-beacon)"/>
            <g class="hero-rotor hero-rotor-front" transform="translate(-141 108)">
              <ellipse rx="50" ry="16" fill="#76bfbe" opacity=".15"/>
              <ellipse rx="46" ry="13" fill="none" stroke="#90cdd0" stroke-width="1.3" opacity=".37"/>
              <g class="hero-rotor-disc">
                <ellipse rx="50" ry="7.3" fill="url(#hero-rotor-blade)" opacity=".87"/>
                <ellipse rx="50" ry="6.5" fill="url(#hero-rotor-blade)" transform="rotate(78)" opacity=".46"/>
              </g>
              <ellipse ry="10" rx="12" fill="url(#hero-engine)" stroke="#b2d1cd" stroke-width="2"/>
            </g>
            <g class="hero-rotor hero-rotor-front" transform="translate(150 109)">
              <ellipse rx="50" ry="16" fill="#76bfbe" opacity=".15"/>
              <ellipse rx="46" ry="13" fill="none" stroke="#90cdd0" stroke-width="1.3" opacity=".37"/>
              <g class="hero-rotor-disc">
                <ellipse rx="50" ry="7.3" fill="url(#hero-rotor-blade)" opacity=".87"/>
                <ellipse rx="50" ry="6.5" fill="url(#hero-rotor-blade)" transform="rotate(78)" opacity=".46"/>
              </g>
              <ellipse ry="10" rx="12" fill="url(#hero-engine)" stroke="#b2d1cd" stroke-width="2"/>
            </g>
          </g>
        </g>
        <!-- The route and A/B/C landmarks are intentionally self-explanatory; no internal instrument labels. -->
      </svg>'''


TECH_TOOLING = """  <section class="proof-tooling" aria-labelledby="proof-tooling-title">
    <p class="proof-tooling-kicker">EXPERIMENTAL PROOF TOOLCHAIN</p>
    <h3 id="proof-tooling-title">How Noir and Barretenberg are used in TAG</h3>
    <p class="proof-tooling-intro">The synthetic bounded-speed experiment uses a pinned research toolchain: Noir/Nargo 1.0.0-beta.26 and Barretenberg bb 5.2.0. This is not a production technology selection.</p>
    <figure class="tech-animation" id="tech-animation" data-started="false" data-complete="false" data-motion="paused" data-visibility="hidden">
      <div class="tech-animation-top">
        <span class="tech-animation-label">PROOF WORKFLOW</span>
        <div class="tech-animation-actions">
          <button type="button" id="tech-animation-replay" aria-controls="tech-animation-svg">Replay explanation</button>
          <button type="button" id="tech-animation-pause" aria-controls="tech-animation-svg" aria-pressed="false" disabled>Pause illustration</button>
        </div>
      </div>
      <p class="tech-animation-caption">From a private condition to an independently verifiable result.</p>
      <svg id="tech-animation-svg" viewBox="0 0 900 240" focusable="false" aria-hidden="true">
        <defs>
          <linearGradient id="tech-panel-glow" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stop-color="#84dfe2" stop-opacity=".32"/>
            <stop offset="1" stop-color="#236475" stop-opacity=".12"/>
          </linearGradient>
        </defs>
        <rect x="9" y="18" width="264" height="198" rx="5" class="tech-panel"/>
        <rect x="318" y="18" width="264" height="198" rx="5" class="tech-panel"/>
        <rect x="627" y="18" width="264" height="198" rx="5" class="tech-panel"/>
        <rect x="12" y="21" width="258" height="192" rx="4" class="tech-highlight tech-highlight-one" fill="url(#tech-panel-glow)"/>
        <rect x="321" y="21" width="258" height="192" rx="4" class="tech-highlight tech-highlight-two" fill="url(#tech-panel-glow)"/>
        <rect x="630" y="21" width="258" height="192" rx="4" class="tech-highlight tech-highlight-three" fill="url(#tech-panel-glow)"/>
        <path d="M277 118H310m-10-8 10 8-10 8M586 118h33m-10-8 10 8-10 8" class="tech-guide"/>
        <circle cx="287" cy="118" r="6" class="tech-transfer tech-transfer-one"/>
        <circle cx="595" cy="118" r="6" class="tech-transfer tech-transfer-two"/>
        <g class="tech-glyph">
          <path d="M80 82h125v75H80zM118 82V61h48v21M119 111l15 15-15 15M165 111l-15 15 15 15"/>
          <path d="M391 79h116v82H391zM416 96l21 19-21 19m30 0h30M460 82v-19M460 161v18"/>
          <path d="M758 66l47 18v43c0 30-24 48-47 55-23-7-47-25-47-55V84z"/>
          <path d="m735 124 17 17 32-34"/>
        </g>
        <circle cx="217" cy="64" r="13" class="tech-secret"/>
        <path d="M211 62v-4a6 6 0 0 1 12 0v4m-13 0h14v11h-14z" fill="none" stroke="#e6c891" stroke-width="2"/>
        <circle cx="522" cy="64" r="10" class="tech-public"/>
        <path d="M517 64h10m-5-5v10" stroke="#16303a" stroke-width="2.5"/>
        <circle cx="805" cy="62" r="11" class="tech-public"/>
        <path d="m800 62 4 4 7-8" fill="none" stroke="#16303a" stroke-width="2.5"/>
        <g fill="#d0d8d6" font-family="Arial,Helvetica,sans-serif" font-weight="700" text-anchor="middle" font-size="17">
          <text x="140" y="199">01 / CONDITION</text>
          <text x="450" y="199">02 / PROOF</text>
          <text x="760" y="199">03 / CHECK</text>
        </g>
        <rect x="0" y="0" width="1" height="1" class="tech-end-signal"/>
      </svg>
      <figcaption class="tech-animation-status" id="tech-animation-status" role="status" aria-live="polite">Rule defined · proof prepared · result checked</figcaption>
    </figure>
    <ol class="toolchain-diagram" aria-label="Experimental proof flow, executed offline">
      <li><span>01 / DEFINE</span><strong>Noir</strong><p>Noir expresses a constraint comparing a private speed value with a public limit; Nargo compiles the circuit.</p></li>
      <li><span>02 / PROVE</span><strong>Barretenberg</strong><p>With the private witness, the pinned bb backend generates a zero-knowledge proof of the constrained statement.</p></li>
      <li><span>03 / VERIFY</span><strong>Offline verifier</strong><p>A separately invoked verifier reconstructs public inputs from canonical CBOR and checks the proof with the expected verification key, without the private speed.</p></li>
    </ol>
    <aside class="proof-evidence-checkpoint" aria-labelledby="proof-evidence-checkpoint-title">
      <h4 id="proof-evidence-checkpoint-title">SITL to ZKP: an integrated synthetic result</h4>
      <p>Local ArduPilot Copter 4.7.1 SITL (TAG #86): PASS for isolated, receive-only MAVLink2 intake of two GLOBAL_POSITION_INT observations and TAG normalization. This does not establish telemetry truth.</p>
      <p>Independent synthetic ZK checkpoint (14 November 2026): historical Qube evidence records proof generation and offline verifier VALID with the pinned verification key. This proof was separate from the SITL observations.</p>
      <p>Integrated ArduPilot Copter 4.7.1 SITL → MAVLink2 → TAG normalization → 600 cm/s predicate → Noir/Barretenberg proof → separate verifier: PASS on 22 November 2026 (GitHub Actions #44995909866). Two synthetic observations; proof GENERATED; both checks VALID. Source UNSIGNED; no commands, publication or operational validation.</p>
    </aside>
    <nav class="proof-tooling-links" aria-label="Tool documentation and TAG implementation">
      <a href="https://www.noir-lang.org/docs/">Noir documentation</a>
      <a href="https://barretenberg.aztec.network/docs/">Barretenberg documentation</a>
      <a href="https://github.com/ROCSI-eu/Telemetry-Attestation-Gateway/tree/main/experiments/bounded-speed-proof-v0">TAG experimental implementation</a>
      <a href="https://github.com/ROCSI-eu/Telemetry-Attestation-Gateway/actions/runs/44995909866">Integrated SITL-to-ZKP CI evidence</a>
    </nav>
    <p class="proof-tooling-boundary">A cryptographically valid proof does not establish telemetry truth, trusted sensors or time, whole-flight coverage, safety or legal compliance. This public page shows recorded synthetic outcomes: the browser neither generates nor verifies a proof.</p>
  </section>
"""


SCENARIO_INTERPRETATION_JS = r"""
// TAG-MISSION-SCENARIOS-01: explanatory text for the existing typed mock replay.
// The independent offline verifier result and conceptual animations are untouched.
const scenarioInterpretations={
  altered_public_input:["Intrările publice modificate duc la INVALID în simulare; nu există publicare.","Altered public inputs produce INVALID in the mock; no publication occurs."],
  below_limit_local_publication:["Condiția este îndeplinită; simularea înregistrează VALID și publicarea locală finalizată.","The claim is satisfied; the mock records VALID and finalized local publication."],
  equality_publication_disabled:["La egalitate, condiția rămâne îndeplinită și rezultatul simulat este VALID; publicarea dezactivată nu schimbă starea criptografică.","At the limit, the claim remains satisfied and the mock records VALID; disabled publication does not change cryptographic status."],
  malformed_source:["Sursa sintetică este respinsă înainte de evaluarea condiției sau generarea dovezii; NOT_CHECKED nu înseamnă INVALID.","The synthetic source is rejected before evaluating the claim or generating a proof; NOT_CHECKED is not INVALID."],
  over_limit:["Condiția nu este îndeplinită; generarea dovezii nu este încercată și verificarea nu este efectuată. NOT_CHECKED nu înseamnă INVALID.","The claim is not satisfied; proof generation is not attempted and verification is not performed. NOT_CHECKED is not INVALID."],
  publication_definitive_failure:["Rezultatul criptografic simulat rămâne VALID, însă substratul respinge definitiv publicarea.","The mock cryptographic status remains VALID, but the substrate definitively rejects publication."],
  publication_timeout_retry_reconciliation:["Simularea înregistrează două încercări și reconcilierea finală a publicării locale; nu există registru public live.","The mock records two attempts and final reconciliation of local publication; no live public ledger is involved."],
  publication_unavailable:["Rezultatul criptografic simulat este VALID, dar publicarea nu este înregistrată deoarece substratul este indisponibil.","The mock cryptographic status is VALID, but publication is not recorded because the substrate is unavailable."],
  tampered_proof:["O dovadă modificată produce INVALID în simulare; publicarea nu este efectuată.","A tampered proof produces INVALID in the mock; publication is not performed."],
  unsupported_public_version:["Versiunea intrărilor publice este respinsă înaintea verificării criptografice: NOT_CHECKED, nu INVALID.","The public-input version is rejected before cryptographic verification: NOT_CHECKED, not INVALID."]
};
function renderScenarioInterpretation(id,e){
  const localized=Object.hasOwn(scenarioInterpretations,id)?scenarioInterpretations[id]:null;
  const explanation=localized?localized[isRomanian?0:1]:(isRomanian?"Scenariu nerecunoscut.":"Unrecognized scenario.");
  // Reflect only the already-selected mock; never infer truth, assurance, or verification.
  $("scenario-active").textContent=(isRomanian?"SCENARIUL SELECTAT · ":"SELECTED SCENARIO · ")+label(id);
  const tones=[
    ["source",e.source,["NORMALIZED"],["REJECTED"]],
    ["claim",e.claim,["SATISFIED"],["NOT_SATISFIED"]],
    ["proof",e.proof_generation,["GENERATED"],[]],
    ["verify-input",e.verification_input,["ACCEPTED"],["REJECTED"]],
    ["publication",e.publication.state,["final"],["failed","NOT_RECORDED"]]
  ];
  for(const [field,value,positive,caution] of tones){
    $(field).dataset.tone=positive.includes(value)?"good":caution.includes(value)?"warn":"neutral";
  }
  const reason=e.publication.error_code;
  $("scenario-explanation").textContent=
    (isRomanian?"Orchestrare simulată: ":"Recorded orchestration mock: ")+explanation+
    (reason===null?"":(isRomanian?" Cod tipizat de publicare: ":" Typed publication code: ")+reason+".");
}
"""

TECH_ANIMATION_JS = r"""
// TAG-TECH-AUTO-01: continuous conceptual motion; never proof execution.
const techAnimation=$("tech-animation");
function syncTechAnimation(){
  techAnimation.dataset.visibility=document.hidden||techAnimation.dataset.inview!=="true"?"hidden":"visible";
}
const techObserver=new IntersectionObserver(entries=>{
  techAnimation.dataset.inview=String(entries[0].isIntersecting);
  syncTechAnimation();
},{threshold:.12});
techObserver.observe(techAnimation);
document.addEventListener("visibilitychange",syncTechAnimation);
techAnimation.dataset.started="true";
techAnimation.dataset.inview="true";
syncTechAnimation();
"""



MISSION_AUTO_CRAFT = r'''<g class="mission-craft" aria-hidden="true">
            <ellipse class="mission-craft-shadow" cx="3" cy="23" rx="60" ry="14"/>
            <g class="mission-airframe" transform="rotate(-18)">
              <path class="mission-craft-arm" d="M-20 -7L-50 -26M20 -7L50 -26M-18 9L-46 31M18 9L46 31"/>
              <path d="M-52 -29L-16 -8M51 -29L16 -8M-46 33L-14 12M46 33L14 12" fill="none" stroke="#b7e1dc" stroke-width=".8" opacity=".65"/>
              <g class="mission-rotor" transform="translate(-51 -27)">
                <ellipse rx="23" ry="7.5" fill="#64b8c1" opacity=".19"/>
                <g class="mission-rotor-blades"><ellipse rx="22" ry="3.2" fill="#a6e3df" opacity=".7"/><ellipse rx="23" ry="2.8" fill="#52939f" opacity=".54" transform="rotate(72)"/></g>
                <circle r="5" fill="url(#mission-motor)" stroke="#c0e2de" stroke-width="1.2"/>
              </g>
              <g class="mission-rotor" transform="translate(51 -27)">
                <ellipse rx="23" ry="7.5" fill="#64b8c1" opacity=".19"/>
                <g class="mission-rotor-blades"><ellipse rx="22" ry="3.2" fill="#a6e3df" opacity=".7"/><ellipse rx="23" ry="2.8" fill="#52939f" opacity=".54" transform="rotate(72)"/></g>
                <circle r="5" fill="url(#mission-motor)" stroke="#c0e2de" stroke-width="1.2"/>
              </g>
              <path d="M-24 -13L-5 -26L24 -13L29 7L8 24L-18 19L-29 5Z" fill="#081b26" stroke="#689ca8" stroke-width="2"/>
              <path class="mission-craft-hull" d="M-23 -13L-5 -25L24 -13L28 6L7 22L-18 18L-28 4Z"/>
              <path d="M-17 -8L-3 -20L16 -13L19 5L7 15L-14 12L-22 3Z" fill="url(#mission-canopy)" stroke="#cae7e4" stroke-width="1.3"/>
              <path d="M-17 -8L-3 -20L15 -14" fill="none" stroke="#f4fbef" stroke-width="1.8" opacity=".8"/>
              <path d="M-21 6L-15 15L6 19" stroke="#0d2a3a" stroke-width="2.6" fill="none"/>
              <circle cx="-18" cy="-9" r="2.3" class="mission-craft-light"/>
              <circle cx="20" cy="-10" r="2.2" fill="#97f4df"/>
              <g transform="translate(1 18)"><rect x="-7" y="-1" rx="2" width="14" height="8" fill="#122d3a" stroke="#88b4bb"/><circle cy="4" r="3" fill="#041522" stroke="#8dbbc1"/><circle cx="-1" cy="3" r=".8" fill="#a8f2e8"/></g>
              <g class="mission-rotor" transform="translate(-45 32)">
                <ellipse rx="22" ry="7" fill="#64b8c1" opacity=".17"/>
                <g class="mission-rotor-blades"><ellipse rx="21" ry="3.1" fill="#a6e3df" opacity=".73"/><ellipse rx="22" ry="2.6" fill="#52939f" opacity=".56" transform="rotate(72)"/></g>
                <circle r="4.7" fill="url(#mission-motor)" stroke="#c0e2de" stroke-width="1.2"/>
              </g>
              <g class="mission-rotor" transform="translate(45 32)">
                <ellipse rx="22" ry="7" fill="#64b8c1" opacity=".17"/>
                <g class="mission-rotor-blades"><ellipse rx="21" ry="3.1" fill="#a6e3df" opacity=".73"/><ellipse rx="22" ry="2.6" fill="#52939f" opacity=".56" transform="rotate(72)"/></g>
                <circle r="4.7" fill="url(#mission-motor)" stroke="#c0e2de" stroke-width="1.2"/>
              </g>
            </g>
          </g>'''
MISSION_AUTO_DEFS = r'''<linearGradient id="mission-arm-metal" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#a3d6d4"/><stop offset=".48" stop-color="#2b6070"/><stop offset="1" stop-color="#092536"/></linearGradient>
            <linearGradient id="mission-hull-glass" x1="0" y1="0" x2=".9" y2="1"><stop stop-color="#f3f1de"/><stop offset=".23" stop-color="#8ebcbd"/><stop offset=".56" stop-color="#396978"/><stop offset="1" stop-color="#092737"/></linearGradient>
            <linearGradient id="mission-canopy" x1="0" y1="0" x2=".8" y2="1"><stop stop-color="#dbf3e6"/><stop offset=".24" stop-color="#7bcbd0"/><stop offset=".6" stop-color="#245467"/><stop offset="1" stop-color="#091c2b"/></linearGradient>
            <radialGradient id="mission-motor"><stop stop-color="#e7f6ef"/><stop offset=".4" stop-color="#7ebbc1"/><stop offset="1" stop-color="#133541"/></radialGradient>
            <linearGradient id="mission-radar-wash" x1="0" y1="0" x2="1" y2=".8"><stop stop-color="#b9fff1" stop-opacity=".42"/><stop offset="1" stop-color="#64b9ca" stop-opacity="0"/></linearGradient>
            '''
MISSION_AUTO_BACKGROUND = r'''<g fill="none" stroke="#89aeb1" stroke-width=".8" opacity=".13">
            <path d="M-20 314C180 251 245 348 435 267S679 227 880 264"/>
            <path d="M-20 337C180 275 255 370 455 293S683 249 880 283"/>
            <path d="M-20 354C185 300 257 390 455 318S688 273 890 314"/>
          </g>
          <g class="mission-radar-sector"><path d="M430 190L430 40A150 150 0 0 1 571 139Z" fill="url(#mission-radar-wash)"/></g>
          <g class="mission-range-ring"><circle cx="430" cy="190" r="181"/><circle cx="430" cy="190" r="116"/></g>
          '''
MISSION_AUTO_WAYPOINTS = r'''<path class="mission-route-energy" d="M120 290 L275 249 L430 194 L585 142 L714 87"/>
          <g class="mission-waypoint-halo"><circle cx="120" cy="290" r="15"/><circle cx="714" cy="87" r="15"/></g>
          <circle class="mission-waypoint-halo mission-waypoint-b" cx="430" cy="194" r="15"/>
          '''
TECH_AUTO_SVG = r'''<svg id="tech-animation-svg" viewBox="0 0 900 240" focusable="false" aria-hidden="true">
        <defs>
          <linearGradient id="tech-chassis" x1="0" y1="0" x2="1" y2="1">
            <stop stop-color="#23434d"/><stop offset=".3" stop-color="#142b35"/><stop offset="1" stop-color="#0a1a22"/>
          </linearGradient>
          <linearGradient id="tech-reflection" x1="0" y1="0" x2=".85" y2="1">
            <stop stop-color="#e4ffef" stop-opacity=".2"/><stop offset=".36" stop-color="#8cdddf" stop-opacity=".07"/><stop offset="1" stop-color="#79ceda" stop-opacity="0"/>
          </linearGradient>
          <linearGradient id="tech-panel-glow" x1="0" y1="0" x2="1" y2="1">
            <stop stop-color="#b6f6e8" stop-opacity=".38"/><stop offset=".5" stop-color="#71b7c4" stop-opacity=".07"/><stop offset="1" stop-color="#266573" stop-opacity=".15"/>
          </linearGradient>
          <linearGradient id="tech-workspace-glass" x1="0" y1="0" x2="1" y2="1">
            <stop stop-color="#30616b"/><stop offset=".4" stop-color="#132f3b"/><stop offset="1" stop-color="#0b1b24"/>
          </linearGradient>
          <linearGradient id="tech-scan-gradient" x1="0" y1="0" x2="1" y2="0">
            <stop stop-color="#8fffee" stop-opacity="0"/><stop offset=".5" stop-color="#dffff5" stop-opacity=".67"/><stop offset="1" stop-color="#8fffee" stop-opacity="0"/>
          </linearGradient>
          <filter id="tech-soft-glow" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="2"/></filter>
        </defs>
        <g>
          <rect x="12" y="23" width="264" height="198" rx="5" class="tech-panel-depth"/>
          <rect x="8" y="17" width="264" height="198" rx="5" class="tech-panel"/>
          <rect x="12" y="21" width="256" height="190" rx="4" class="tech-panel-sheen"/>
          <rect x="16" y="25" width="248" height="182" rx="4" class="tech-highlight tech-highlight-one"/>
          <path d="M22 32h236" stroke="#bdfff1" opacity=".18"/>
          <path d="M34 54h78m-78 6h41" stroke="#8db6b5" stroke-width="2" opacity=".42"/>
          <g class="tech-glyph">
            <path d="M75 88h121v66H75zM106 88V67h60v21"/>
            <path d="M109 107l18 16-18 16M162 107l-18 16 18 16"/>
          </g>
          <path d="M75 154h121M75 88h121" stroke="#ecfff4" opacity=".3"/>
          <circle cx="225" cy="72" r="15" class="tech-secret"/>
          <path d="M220 70v-4a5 5 0 0 1 10 0v4m-12 0h14v10h-14z" stroke="#eacb97" stroke-width="2" fill="none"/>
          <circle cx="40" cy="187" r="3" class="tech-status-led"/>
        </g>
        <g>
          <rect x="321" y="23" width="264" height="198" rx="5" class="tech-panel-depth"/>
          <rect x="317" y="17" width="264" height="198" rx="5" class="tech-panel"/>
          <rect x="321" y="21" width="256" height="190" rx="4" class="tech-panel-sheen"/>
          <rect x="325" y="25" width="248" height="182" rx="4" class="tech-highlight tech-highlight-two"/>
          <path d="M331 32h236" stroke="#bdfff1" opacity=".18"/>
          <path d="M344 54h72m-72 6h49" stroke="#8db6b5" stroke-width="2" opacity=".42"/>
          <rect x="385" y="83" width="130" height="71" rx="3" class="tech-workspace"/>
          <g class="tech-glyph"><path d="M413 105l21 17-21 17m32 0h29"/></g>
          <path d="M392 92h114" stroke="#ecfff4" opacity=".3"/>
          <path d="M450 154v14m-28 0h56" stroke="#7db9c1" stroke-width="5" stroke-linecap="round"/>
          <circle cx="535" cy="72" r="13" class="tech-public"/>
          <path d="M529 72h12m-6-6v12" stroke="#16303a" stroke-width="2.7"/>
          <circle cx="348" cy="187" r="3" class="tech-status-led"/>
        </g>
        <g>
          <rect x="630" y="23" width="264" height="198" rx="5" class="tech-panel-depth"/>
          <rect x="626" y="17" width="264" height="198" rx="5" class="tech-panel"/>
          <rect x="630" y="21" width="256" height="190" rx="4" class="tech-panel-sheen"/>
          <rect x="634" y="25" width="248" height="182" rx="4" class="tech-highlight tech-highlight-three"/>
          <path d="M640 32h236" stroke="#bdfff1" opacity=".18"/>
          <path d="M654 54h77m-77 6h45" stroke="#8db6b5" stroke-width="2" opacity=".42"/>
          <g class="tech-glyph">
            <path d="M760 73l47 19v41c0 30-24 48-47 55-23-7-47-25-47-55V92z"/>
            <path d="M737 128l16 16 33-33"/>
          </g>
          <circle cx="823" cy="72" r="13" class="tech-public"/>
          <path d="m818 72 4 4 7-8" stroke="#16303a" stroke-width="2.5" fill="none"/>
          <circle cx="659" cy="187" r="3" class="tech-status-led"/>
        </g>
        <path d="M277 118h34m-11-8 11 8-11 8M587 118h33m-11-8 11 8-11 8" class="tech-guide"/>
        <circle cx="282" cy="118" r="8" class="tech-transfer tech-transfer-one"/>
        <circle cx="591" cy="118" r="8" class="tech-transfer tech-transfer-two"/>
        <rect class="tech-scan" x="16" y="32" width="160" height="169" rx="3"/>
        <g fill="#d4e0dc" font-family="Arial,Helvetica,sans-serif" font-weight="700" text-anchor="middle" font-size="15">
          <text x="140" y="199">01 / CONDITION</text>
          <text x="450" y="199">02 / PROOF</text>
          <text x="760" y="199">03 / CHECK</text>
        </g>
      </svg>'''
MISSION_AUTO_JS = r'''// Architecture has CSS-only motion and no route controls.
 // The separate technical illustration still needs the motion preference.
 const motionPreference=window.matchMedia("(prefers-reduced-motion: reduce)");
'''


def public_cinematic_motion(html: str) -> str:
    # Only the static public showcase is modified, never the source console.
    replay = '<button id="mission-replay" type="button" aria-controls="mission-scene">Replay illustration</button>'
    toggle = '<button id="mission-motion-toggle" type="button" aria-pressed="true" aria-controls="mission-scene" disabled>Resume illustration</button>'
    tech_actions = '''<div class="tech-animation-actions">
          <button type="button" id="tech-animation-replay" aria-controls="tech-animation-svg">Replay explanation</button>
          <button type="button" id="tech-animation-pause" aria-controls="tech-animation-svg" aria-pressed="false" disabled>Pause illustration</button>
        </div>'''
    for marker in (replay, toggle, tech_actions):
        if html.count(marker) != 1:
            raise ValueError("unexpected public-only animation control")
        html = html.replace(marker, "", 1)
    old_mission_state = 'data-motion="paused" data-visibility="visible" data-scene="pass"'
    if html.count(old_mission_state) != 1:
        raise ValueError("mission playback state changed")
    html = html.replace(old_mission_state, 'data-motion="playing" data-visibility="visible" data-scene="pass"', 1)
    old_tech_state = 'data-started="false" data-complete="false" data-motion="paused" data-visibility="hidden"'
    if html.count(old_tech_state) != 1:
        raise ValueError("technical animation state changed")
    html = html.replace(old_tech_state, 'data-started="true" data-visibility="visible"', 1)
    match = re.search(r'<svg id="tech-animation-svg".*?</svg>', html, re.S)
    if match is None or html.count('id="tech-animation-svg"') != 1:
        raise ValueError("technical animation SVG changed")
    html = html[:match.start()] + '<div class="tech-scene-scroll" tabindex="0">' + TECH_AUTO_SVG + '</div>' + html[match.end():]
    mission_start = html.index('<svg viewBox="0 0 860 370"')
    mission_end = html.index('</svg>', mission_start) + len('</svg>')
    svg = html[mission_start:mission_end]
    if svg.count("</defs>") != 1:
        raise ValueError("mission illustration defs changed")
    svg = svg.replace("</defs>", MISSION_AUTO_DEFS + "</defs>", 1)
    old_background = '<rect width="860" height="370" fill="url(#mission-glow)"/>'
    if svg.count(old_background) != 1:
        raise ValueError("mission illustration background changed")
    svg = svg.replace(old_background,old_background + MISSION_AUTO_BACKGROUND,1)
    original_path = '<path class="mission-path" d="M120 290 L275 249 L430 194 L585 142 L714 87"/>'
    if svg.count(original_path) != 1:
        raise ValueError("mission path changed")
    svg = svg.replace(original_path,original_path + MISSION_AUTO_WAYPOINTS,1)
    svg, count = re.subn(r'<g class="mission-craft" aria-hidden="true">.*?</g>', MISSION_AUTO_CRAFT, svg, count=1, flags=re.S)
    if count != 1:
        raise ValueError("mission craft shape changed")
    html = html[:mission_start] + svg + html[mission_end:]
    start = html.index("// Entirely predetermined illustrative geometry.")
    end = html.index("function render(e) {", start)
    if end <= start or "mission-replay" not in html[start:end]:
        raise ValueError("mission motion script changed")
    html = html[:start] + MISSION_AUTO_JS + "\n" + html[end:]
    return html


CONCEPT_VISUAL = """    <figure class="concept-cinema" id="concept-cinema" data-visibility="visible" aria-labelledby="concept-illustration-title">
      <figcaption class="concept-cinema-heading" id="concept-illustration-title">
        <span>VEHICLE SPEED · HYPOTHETICAL EXAMPLE</span>
        <strong>THE IDEA, AT A GLANCE</strong>
      </figcaption>
      <div class="concept-stage">
        <div class="concept-step concept-step-private">
          <span class="concept-step-icon" aria-hidden="true">
            <svg viewBox="0 0 48 48" focusable="false"><rect x="8" y="18" width="32" height="24" rx="5"/><path d="M15 18v-5a9 9 0 0 1 18 0v5"/><circle cx="24" cy="30" r="2"/><path d="M24 32v4"/></svg>
          </span>
          <div class="concept-step-copy">
            <span class="concept-step-label">01 / PRIVATE VALUE</span>
            <strong>Speed: hidden</strong>
            <p>The exact reading stays private.</p>
          </div>
        </div>
        <div class="concept-flow" aria-hidden="true"><span class="concept-flow-track"><span class="concept-flow-dot"></span></span></div>
        <div class="concept-step concept-step-rule">
          <span class="concept-step-icon" aria-hidden="true">
            <svg viewBox="0 0 48 48" focusable="false"><rect x="7" y="8" width="34" height="32" rx="4"/><path d="M15 19h18M16 28l6 5 11-12"/></svg>
          </span>
          <div class="concept-step-copy">
            <span class="concept-step-label">02 / PUBLIC RULE</span>
            <strong>Speed ≤ speed limit</strong>
            <p>The condition is known to everyone.</p>
          </div>
        </div>
        <div class="concept-flow concept-flow-second" aria-hidden="true"><span class="concept-flow-track"><span class="concept-flow-dot"></span></span></div>
        <div class="concept-step concept-step-result">
          <span class="concept-step-icon" aria-hidden="true">
            <svg viewBox="0 0 48 48" focusable="false"><path d="M24 4 40 11v13c0 10-7 16-16 20C15 40 8 34 8 24V11Z"/><path d="m15 24 7 7 12-14"/></svg>
          </span>
          <div class="concept-step-copy">
            <span class="concept-step-label">03 / VERIFIABLE ANSWER</span>
            <strong>Within the limit: YES</strong>
            <p>A proof could confirm this without revealing the speed.</p>
          </div>
        </div>
      </div>
    </figure>
"""

CONCEPT_CSS = """
    /* Visitor-first concept: three readable, static states; only link dots animate. */
    .primer{display:grid;grid-template-columns:minmax(0,.98fr) minmax(0,1.02fr);column-gap:clamp(32px,4.1vw,72px);align-items:start}
    .primer .primer-visual,.primer .primer-copy{display:flex;flex-direction:column;align-items:stretch;min-width:0;gap:0}
    .primer .primer-visual{grid-column:1;grid-row:1}
    .primer .primer-copy{grid-column:2;grid-row:1}
    .primer .primer-visual .primer-kicker{grid-column:auto;grid-row:auto;margin:0 0 24px;padding:4px 0 0;line-height:1.4}
    .primer .primer-visual .concept-cinema{grid-column:auto;grid-row:auto;align-self:stretch;width:100%;min-width:0}
    .primer .primer-copy h2{grid-column:auto;grid-row:auto;margin:0 0 30px}
    .primer .primer-copy p{grid-column:auto;grid-row:auto;margin:8px 0 12px}
    .concept-cinema{position:relative;isolation:isolate;overflow:hidden;margin:0;padding:clamp(17px,2.2vw,30px);border:1px solid #3b5a60;background:radial-gradient(ellipse at 50% 42%,#1b3940 0%,#0c1b21 59%,#081217 100%);box-shadow:inset 0 0 55px #02090b9c;min-width:0}
    .concept-cinema:before{content:"";position:absolute;inset:0;background:repeating-linear-gradient(0deg,transparent 0 47px,#76adae0b 48px),repeating-linear-gradient(90deg,transparent 0 47px,#76adae0b 48px);pointer-events:none}
    .concept-cinema-heading{position:relative;z-index:1;display:flex;flex-direction:column;gap:8px;margin:0 0 24px}
    .concept-cinema-heading>span{font-size:.67rem;font-weight:800;letter-spacing:.115em;line-height:1.45;color:#e2bd83}
    .concept-cinema-heading>strong{font-size:clamp(1.13rem,1.7vw,1.45rem);letter-spacing:-.025em;line-height:1.3;color:#f1eee4}
    .concept-stage{position:relative;z-index:1;display:flex;flex-direction:column;min-width:0;gap:0}
    .concept-step{display:grid;grid-template-columns:58px minmax(0,1fr);gap:clamp(13px,1.4vw,20px);align-items:center;min-width:0;min-height:126px;padding:17px clamp(16px,2.3vw,26px);background:#10252ac9;border:1px solid #476770}
    .concept-step-private{border-left:3px solid #7ed2d1}
    .concept-step-rule{border-left:3px solid #ddc18a;background:#192c31d9}
    .concept-step-result{border-left:3px solid #9ccfb5}
    .concept-step-icon{display:grid;place-items:center;width:55px;height:55px;border:1px solid #65878b;background:#193841;color:#b8e0dc}
    .concept-step-rule .concept-step-icon{border-color:#bba578;background:#32382f;color:#f1d49a}
    .concept-step-result .concept-step-icon{border-color:#78a997;background:#17352f;color:#addbc4}
    .concept-step-icon svg{display:block;width:35px;height:35px;fill:none;stroke:currentColor;stroke-width:2.3;stroke-linecap:round;stroke-linejoin:round}
    .concept-step-copy{display:flex;flex-direction:column;align-items:flex-start;min-width:0;gap:6px}
    .concept-step-label{color:#ddc291;font-weight:800;letter-spacing:.1em;font-size:.68rem;line-height:1.4}
    .concept-step-copy strong{color:#f3efe5;font-size:clamp(1.05rem,1.8vw,1.3rem);line-height:1.3;letter-spacing:-.02em;overflow-wrap:anywhere}
    .concept-step-copy p{color:#c8d5d1;line-height:1.55;font-size:.84rem;margin:0}
    .concept-flow{display:flex;justify-content:center;height:43px;flex:none}
    .concept-flow-track{position:relative;display:block;width:2px;height:100%;background:repeating-linear-gradient(to bottom,#7ca5a3 0 5px,transparent 5px 10px)}
    .concept-flow-track:after{content:"";position:absolute;bottom:-1px;left:-4px;border-left:5px solid transparent;border-right:5px solid transparent;border-top:7px solid #ddc18a}
    .concept-flow-dot{position:absolute;top:0;left:-3px;width:8px;height:8px;border-radius:50%;background:#e8dbb4;box-shadow:0 0 12px #b7e1cf;animation:concept-flow 4.5s ease-in-out infinite}
    .concept-flow-second .concept-flow-dot{animation-delay:-2.25s}
    @keyframes concept-flow{0%,8%{top:0;opacity:0}20%{opacity:1}80%{opacity:1}100%{top:calc(100% - 9px);opacity:0}}
    .concept-cinema[data-visibility="hidden"] .concept-flow-dot{animation-play-state:paused!important}
    @media(prefers-reduced-motion:reduce){.concept-cinema .concept-flow-dot{animation:none!important;top:calc(50% - 4px);opacity:.8}}
    @media(max-width:750px){.primer{display:flex;flex-direction:column;gap:0}.primer .primer-visual{width:100%;order:0}.primer .primer-copy{width:100%;order:1}.primer .primer-visual .primer-kicker{margin-bottom:22px}.primer .primer-visual .concept-cinema{margin:0 0 34px}}
    @media(max-width:420px){.concept-cinema{padding:16px}.concept-cinema-heading{margin-bottom:20px}.concept-step{grid-template-columns:43px minmax(0,1fr);min-height:115px;gap:11px;padding:14px 12px}.concept-step-icon{width:42px;height:42px}.concept-step-icon svg{width:27px;height:27px}.concept-step-label{font-size:.61rem;letter-spacing:.06em}.concept-step-copy strong{font-size:1rem}.concept-step-copy p{font-size:.78rem}.concept-flow{height:34px}}
"""

CONCEPT_VISIBILITY_JS = r"""
// Pause the conceptual animation outside the viewport or when the tab is hidden.
const conceptScene=document.getElementById("concept-cinema");
const conceptObserver=new IntersectionObserver(entries=>{
  conceptScene.dataset.inview=String(entries[0].isIntersecting);
  syncConceptScene();
},{threshold:.08});
function syncConceptScene(){
  conceptScene.dataset.visibility=document.hidden||conceptScene.dataset.inview!=="true"?"hidden":"visible";
}
conceptScene.dataset.inview="true";
conceptObserver.observe(conceptScene);
document.addEventListener("visibilitychange",syncConceptScene);
syncConceptScene();
"""

MISSION_EXPLAIN_CSS = """
    .mission-speed-example{display:flex;flex-direction:column;gap:0;min-width:0}
    .mission-speed-example .mission-label{display:block;margin:0 0 13px;color:#e8bf84;font-weight:800;letter-spacing:.115em;font-size:.69rem}
    .mission-speed-example h3{font-size:clamp(1.25rem,1.65vw,1.7rem);line-height:1.2;letter-spacing:-.025em;margin:0 0 17px;max-width:none}
    .mission-speed-example>p:not(.mission-label){margin:0 0 18px;font-size:.88rem;line-height:1.65;color:#d2ddd9}
    .mission-speed-facts{display:block;margin:5px 0 19px;padding:0;border-top:1px solid #486064}
    .mission-speed-facts .mission-speed-fact{display:block;margin:0;padding:16px 0 14px;border-bottom:1px solid #43585b}
    .mission-speed-facts .mission-speed-fact dt{display:block;margin:0 0 7px;font-size:.66rem;letter-spacing:.12em;color:#e6c08b;font-weight:800;text-transform:uppercase}
    .mission-speed-facts .mission-speed-fact dd{display:block;margin:0;color:#f0e9da;font-size:.95rem;font-weight:640;line-height:1.4;text-align:left;max-width:none;overflow-wrap:normal}
    .mission-speed-example>p.mission-speed-conclusion{color:#d7e2dd;margin:0;line-height:1.6;font-size:.87rem}
    .mission-scene-status{font-size:.8rem;line-height:1.5;color:#c4d4cf;margin-top:12px}
    @media(max-width:750px){.mission-speed-example{padding:22px}.mission-speed-facts .mission-speed-fact{padding:14px 0 12px}}
"""


ARCHITECTURE_PUBLIC_HTML = """  <section class="mission-control architecture-section" id="mission-control" aria-labelledby="architecture-title">
    <p class="section-overline">02 / THE ARCHITECTURE</p>
    <h2 class="section-display" id="architecture-title">From a UAS measurement to a verifiable result.</h2>
    <p class="editorial-chapter-intro">A proposed architecture linking an uncrewed aircraft, a TAG cryptographic gateway and command-and-control.</p>
    <div class="architecture-panel" aria-label="Proposed UAS to TAG to command-and-control information flow">
      <p class="architecture-eyebrow">ARCHITECTURE UNDER RESEARCH</p>
      <div class="architecture-flow">
        <div class="architecture-node">
          <svg viewBox="0 0 88 80" aria-hidden="true" focusable="false">
            <g fill="none" stroke="#a7dfd9" stroke-width="2.6" stroke-linecap="round">
              <path d="M23 27L38 39M65 27L50 39M23 59L38 45M65 59L50 45"/>
              <circle cx="19" cy="23" r="10"/><circle cx="69" cy="23" r="10"/>
              <circle cx="19" cy="63" r="10"/><circle cx="69" cy="63" r="10"/>
              <path d="M35 35L44 29L53 35L55 46L44 53L33 46Z" fill="#183c48" stroke="#efcf94"/>
              <circle cx="44" cy="42" r="3" fill="#e2c088"/>
            </g>
          </svg>
          <strong>UAS</strong><span>Collects a private measurement</span>
        </div>
        <div class="architecture-link" aria-hidden="true"><span>Protected channel</span></div>
        <div class="architecture-node architecture-node-tag">
          <svg viewBox="0 0 88 80" aria-hidden="true" focusable="false">
            <path d="M44 8L72 24V56L44 72L16 56V24Z" fill="#153641" stroke="#e5c58f" stroke-width="2.7"/>
            <circle cx="44" cy="40" r="18" fill="none" stroke="#98d9d6" stroke-width="2"/>
            <path d="M37 38V33a7 7 0 0 1 14 0v5M35 38h18v15H35Z" fill="#184857" stroke="#e6d4a8" stroke-width="2.2" stroke-linejoin="round"/>
            <circle cx="44" cy="45" r="2.2" fill="#eed49b"/>
          </svg>
          <strong>TAG / ZKP</strong><span>Would prepare a verifiable proof</span>
        </div>
        <div class="architecture-link architecture-link-second" aria-hidden="true"><span>Verifiable result</span></div>
        <div class="architecture-node">
          <svg viewBox="0 0 88 80" aria-hidden="true" focusable="false">
            <rect x="10" y="17" width="68" height="43" rx="3" fill="#123440" stroke="#a1d8d7" stroke-width="2.4"/>
            <path d="M17 29H71M27 38l9 8 18-17" fill="none" stroke="#e4c790" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M44 61v9M28 70h32" fill="none" stroke="#a1d8d7" stroke-width="2.8" stroke-linecap="round"/>
          </svg>
          <strong>C2</strong><span>Would check the defined condition</span>
        </div>
      </div>
    </div>
    <p class="architecture-note">Secure communication protects the channel; a ZKP supports verification. The combined UAS–TAG–C2 flow remains a research objective.</p>
"""


ARCHITECTURE_CSS = """
    /* Single concept animation: no route controls, network, crypto execution, or external assets. */
    .architecture-section .section-display{max-width:20ch;font-size:clamp(2.1rem,4vw,4.2rem);line-height:1.08}
    .architecture-section>.editorial-chapter-intro{max-width:74ch;margin-bottom:28px}
    .architecture-panel{padding:clamp(18px,2.4vw,32px);border:1px solid #466168;background:radial-gradient(ellipse at 50% 35%,#183943 0,#0b1c22 62%,#081318 100%);overflow:hidden;position:relative;min-width:0}
    .architecture-panel:before{content:"";position:absolute;inset:0;pointer-events:none;background:repeating-linear-gradient(0deg,transparent 0 61px,#80b3b50d 62px),repeating-linear-gradient(90deg,transparent 0 61px,#80b3b50d 62px)}
    .architecture-eyebrow{position:relative;color:#e9c78e;font-size:.69rem;letter-spacing:.14em;font-weight:800;margin:0 0 30px}
    .architecture-flow{position:relative;display:grid;grid-template-columns:minmax(0,1fr) minmax(50px,.38fr) minmax(0,1fr) minmax(50px,.38fr) minmax(0,1fr);gap:7px;align-items:center}
    .architecture-node{display:flex;align-items:center;flex-direction:column;justify-content:center;text-align:center;min-width:0;min-height:215px;padding:17px 11px;border:1px solid #44636b;background:#0e252bcf}
    .architecture-node svg{height:70px;width:79px;max-width:100%;margin-bottom:15px;flex:none;filter:drop-shadow(0 0 14px #57bdb433)}
    .architecture-node strong{font-size:clamp(1.15rem,1.8vw,1.6rem);font-weight:800;color:#f4ecd9;line-height:1.15}
    .architecture-node span{font-size:.83rem;line-height:1.5;color:#c5d4d0;margin-top:10px;max-width:23ch}
    .architecture-node-tag{border-color:#be9a68;background:#203236}
    .architecture-node-tag strong{color:#f1d19a}
    .architecture-link{position:relative;height:2px;border-top:2px dashed #72acb1;align-self:center;min-width:0}
    .architecture-link:before{content:"";position:absolute;right:-2px;top:-6px;border-top:5px solid transparent;border-bottom:5px solid transparent;border-left:7px solid #e4c590}
    .architecture-link:after{content:"";position:absolute;left:0;top:-5px;width:7px;height:7px;border-radius:50%;background:#d9f6e8;box-shadow:0 0 11px #a7ede5;animation:architecture-packet 4.8s ease-in-out infinite}
    .architecture-link-second:after{animation-delay:-2.4s}
    .architecture-link span{position:absolute;left:50%;bottom:18px;transform:translateX(-50%);color:#c4d9d6;font-size:.69rem;font-weight:650;line-height:1.4;text-align:center;width:120px;max-width:125%;pointer-events:none}
    .architecture-note{margin:17px 0 0;color:#c2ccca;font-size:.86rem;line-height:1.65;max-width:92ch}
    @keyframes architecture-packet{0%{left:0;opacity:0}12%{opacity:1}84%{opacity:1}100%{left:calc(100% - 7px);opacity:0}}
    @media(max-width:750px){
      .architecture-panel{padding:18px 16px 22px}
      .architecture-eyebrow{margin-bottom:16px}
      .architecture-flow{grid-template-columns:minmax(0,1fr);gap:0;max-width:410px;margin:0 auto}
      .architecture-node{min-height:150px;padding:12px 17px}
      .architecture-node svg{width:61px;height:55px;margin-bottom:8px}
      .architecture-node strong{font-size:1.2rem}
      .architecture-node span{margin-top:6px;font-size:.82rem}
      .architecture-link{justify-self:center;width:2px;height:63px;min-height:63px;border-top:0;border-left:2px dashed #72acb1}
      .architecture-link:before{right:auto;left:-5px;top:auto;bottom:-2px;border-top:7px solid #e4c590;border-left:5px solid transparent;border-right:5px solid transparent;border-bottom:0}
      .architecture-link:after{left:-5px;top:0;animation:architecture-packet-down 4.8s ease-in-out infinite}
      .architecture-link-second:after{animation-delay:-2.4s}
      .architecture-link span{left:16px;bottom:auto;top:16px;transform:none;width:140px;max-width:none;text-align:left}
      .architecture-note{font-size:.82rem}
    }
    @keyframes architecture-packet-down{0%{top:0;opacity:0}12%{opacity:1}84%{opacity:1}100%{top:calc(100% - 7px);opacity:0}}
    @media(prefers-reduced-motion:reduce){.architecture-link:after{animation:none!important;opacity:.75;left:calc(50% - 3px)}}
"""

EDITORIAL_CSS = """
    /* Editorial regrouping only: original visual system and motion remain intact. */
    .editorial-chapter-intro{max-width:74ch;color:#ccd3d0;line-height:1.74;margin:0 0 32px;font-size:1rem}
    .editorial-caveat{max-width:90ch;color:#c0c7c3;font-size:.86rem;line-height:1.75;margin:22px 0}
    .editorial-process{padding:37px 0 0;border-top:1px solid #425054;margin-top:40px}
    .editorial-process h3,.research-secondary-title{font-size:clamp(1.8rem,3vw,3.1rem);line-height:1.15;letter-spacing:-.05em;margin:12px 0 20px}
    .editorial-proof-intro{color:#c0c9c6;font-size:.98rem;line-height:1.7;max-width:73ch;margin:0}
    .editorial-proof-animation{margin:22px 0 0}
    .editorial-proof-animation .tech-animation{margin:0}
    .research-journal{list-style:none;padding:0;margin:24px 0 0;border-top:1px solid #536063}
    .research-entry{display:grid;grid-template-columns:minmax(145px,.31fr) minmax(0,1fr);gap:clamp(18px,4vw,64px);border-bottom:1px solid #445155;padding:30px 0 34px;min-width:0}
    .research-entry-meta{display:flex;flex-direction:column;gap:12px}
    .research-entry-number{color:#e2bf85;font-size:.73rem;font-weight:800;letter-spacing:.16em}
    .research-entry-field{color:#bdc8c5;font-size:.77rem;line-height:1.45}
    .research-entry-copy{min-width:0;max-width:78ch}
    .research-entry-copy h3{font-size:clamp(1.45rem,2.4vw,2.25rem);line-height:1.19;letter-spacing:-.035em;color:#f2eddf;margin:0 0 16px}
    .research-entry-copy p{color:#c4ceca;line-height:1.7;font-size:.97rem;margin:0 0 13px}
    .research-entry-copy .research-entry-insight{padding-left:16px;margin:18px 0 0;border-left:2px solid #d7b77e;color:#e3e2da}
    .research-entry-insight strong{color:#eed7ae}
    .research-next-question{margin:30px 0 46px;padding:26px clamp(18px,3vw,32px);border:1px solid #586165;background:#142023}
    .research-next-question span{font-size:.72rem;letter-spacing:.14em;font-weight:800;color:#e2bd83}
    .research-next-question h3{font-size:clamp(1.3rem,2.4vw,2rem);margin:12px 0;letter-spacing:-.03em}
    .research-next-question p{max-width:76ch;font-size:.95rem;line-height:1.7;color:#c7cfcb;margin:0}
    .research-details{border-top:1px solid #526165;margin-top:0}
    .research-detail{border-top:0;border-bottom:1px solid #526165;margin:0;padding:0;scroll-margin-top:25px}
    .research-detail>summary{cursor:pointer;list-style:none;position:relative;font-size:1.16rem;font-weight:720;padding:23px 45px 23px 0;color:#f1e7d5}
    .research-detail>summary::-webkit-details-marker{display:none}
    .research-detail>summary:after{content:'+';position:absolute;right:12px;top:20px;font-size:1.4rem;color:#e5bd7b}
    .research-detail[open]>summary:after{content:'−'}
    .research-detail>summary:focus-visible{outline:2px solid #e5bd7b;outline-offset:3px}
    .research-detail-body{padding:12px 0 35px;min-width:0}
    .research-detail .proof-tooling{margin:0}
    .research-detail .scope-disclosure{margin:0}
    .research-technical-intro{font-size:.96rem;line-height:1.7;max-width:78ch;color:#c7d0cc;margin:0 0 20px}
    .research-release{display:flex;align-items:center;justify-content:space-between;gap:10px 24px;flex-wrap:wrap;border:1px solid #3b5255;background:#0d1b1e;padding:15px 20px;margin:0 0 28px;font-size:.8rem;line-height:1.5;color:#c3cdc9}
    .research-release a{color:#ead1a3;text-underline-offset:4px;font-weight:750;white-space:nowrap}
    .research-release .research-revision-neutral{color:#aebcb8}
    .research-detail>summary{display:flex;flex-direction:column;gap:6px}
    .research-detail-heading{font-size:1.1rem;line-height:1.35;color:#f0e9d9}
    .research-detail-teaser{font-size:.86rem;font-weight:400;line-height:1.55;color:#becac6}
    .research-detail-body{padding:12px 0 26px}
    .research-simple-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
    .research-outcomes{grid-template-columns:repeat(2,minmax(0,1fr))}
    .research-simple-grid article{min-width:0;background:#121f22;border:1px solid #395156;padding:clamp(16px,2vw,24px)}
    .research-simple-grid article>span{display:block;font-size:.71rem;font-weight:800;letter-spacing:.1em;color:#e2c08a;margin:0 0 13px}
    .research-simple-grid h4{font-size:1.1rem;line-height:1.35;letter-spacing:-.02em;color:#f3ebdd;margin:0 0 9px}
    .research-simple-grid p{color:#c6d0cc;font-size:.87rem;line-height:1.65;margin:0}
    .research-method-boundary{color:#ccd5d1;font-size:.9rem;line-height:1.65;max-width:87ch;margin:19px 0 0}
    .research-archive{border-top:1px solid #395257;margin-top:22px;padding:0}
    .research-archive>summary{cursor:pointer;list-style:none;color:#e5c592;font-size:.86rem;font-weight:720;padding:18px 32px 18px 0;position:relative;line-height:1.5}
    .research-archive>summary::-webkit-details-marker{display:none}
    .research-archive>summary:after{content:'+';position:absolute;right:7px;top:15px;font-size:1.15rem}
    .research-archive[open]>summary:after{content:'−'}
    .research-archive>summary:focus-visible{outline:2px solid #e5bd7b;outline-offset:3px}
    .research-archive-body{padding:4px 0 16px}
    .research-archive-body .proof-tooling,.research-archive-body .scope-disclosure{margin:0}
    .research-archive-body>.editorial-caveat{margin:0 0 20px}
    @media(max-width:1050px) and (min-width:751px){.research-simple-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.research-methods article:last-child,.research-boundaries article:last-child{grid-column:1/-1}}
    @media(max-width:750px){.research-simple-grid,.research-outcomes{grid-template-columns:1fr}.research-release{align-items:flex-start}.research-simple-grid article{padding:19px}.research-detail>summary{padding-right:35px}.research-detail-teaser{font-size:.82rem}}
    @media(max-width:750px){.editorial-process{padding-top:27px}.research-entry{grid-template-columns:1fr;gap:11px;padding:25px 0}.research-entry-meta{flex-direction:row;flex-wrap:wrap;align-items:baseline;gap:8px 15px}.research-next-question{margin:27px 0 55px}}
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
    <a class="brand" href="/" aria-label="TAG · ROCSI"><span class="brand-signal">TAG</span><img class="brand-rocsi-mark" src="/assets/rocsi-mark.svg" alt="" width="34" height="34" decoding="async"><span class="brand-detail">Romanian Cyber Space Initiative</span></a>
    <nav class="section-nav" aria-label="Page sections">
      <a href="#principle">The Concept</a>
      <a href="#mission-control">How It Works</a>
      <a href="#use-cases">Applications</a>
      <a href="#research">The Research</a>
    </nav>
    <div class="header-status"><a class="header-cta" href="https://rocsi.eu/en/contact">Start a conversation</a><div class="pill" id="console-mode">PRIVACY-PRESERVING TELEMETRY</div></div>
  </header>
  <section class="hero" aria-labelledby="hero-title">
    <div class="hero-content">
      <p class="hero-overline">RESEARCH · DATA PRIVACY</p>
      <h1 id="hero-title">Verify the condition. Keep the rest private.</h1>
      <p class="sub">What if systems could demonstrate a condition without revealing the data behind it? TAG investigates this direction for telemetry through cryptographic research.</p>
      <div class="hero-actions"><a href="#principle">Explore the concept</a><a href="#mission-control">See the demonstration</a></div>
    </div>
    <div class="hero-art">
      <span class="hero-art-label">SYNTHETIC ROUTE</span>
{HERO_SCENE_SVG}
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

    # Four visitor chapters; technical details stay present in secondary panels.
    if 'id="primer-title"' not in intro or 'id="use-cases-title"' not in applications:
        raise ValueError("unexpected editorial source text")
    intro = '''  <section class="primer" id="principle" aria-labelledby="primer-title">
    <div class="primer-visual">
      <p class="primer-kicker">01 / THE CONCEPT</p>
    </div>
    <div class="primer-copy">
    <h2 id="primer-title">Less data exposed. A condition that can be verified.</h2>
    <p>Verifying a rule can require sharing detailed information. TAG investigates a different approach: proving that one defined condition is satisfied while keeping the underlying value private.</p>
    <p class="primer-example"><strong>A simple example:</strong> A vehicle must stay within a speed limit. A cryptographic proof could establish that a private speed value meets the public limit without disclosing the exact speed.</p>
    </div>
  </section>
'''
    opener = '      <p class="primer-kicker">01 / THE CONCEPT</p>\n    </div>'
    if intro.count(opener) != 1:
        raise ValueError("concept illustration insertion anchor changed")
    intro = intro.replace(opener, '      <p class="primer-kicker">01 / THE CONCEPT</p>\n' + CONCEPT_VISUAL + '    </div>', 1)
    applications = '''  <section class="use-cases" id="use-cases" aria-labelledby="use-cases-title">
    <p class="section-overline">03 / POTENTIAL APPLICATIONS</p>
    <h2 id="use-cases-title">Where could this capability matter?</h2>
    <p class="editorial-chapter-intro">Selective verification may help when a result needs to be demonstrated but sharing the entire dataset is undesirable.</p>
    <div class="use-cases-grid">
      <article class="use-case-card">
        <span class="use-case-icon-wrap"><svg class="use-case-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M12 2 20 6v6c0 5-3 8-8 10-5-2-8-5-8-10V6z"/><path d="m8.5 12 2.4 2.4 4.7-4.9"/></svg></span>
        <h3>Audit and verification</h3>
        <p>An organization could demonstrate that an agreed condition was met without handing over its complete underlying dataset.</p>
      </article>
      <article class="use-case-card">
        <span class="use-case-icon-wrap"><svg class="use-case-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="5" cy="5" r="3"/><circle cx="19" cy="5" r="3"/><circle cx="5" cy="19" r="3"/><circle cx="19" cy="19" r="3"/><path d="m7 7 3 3m7-3-3 3M7 17l3-3m7 3-3-3M9 10h6v4H9z"/></svg></span>
        <h3>Autonomous systems</h3>
        <p>A UAS or autonomous vehicle could report that a defined operational threshold was met without sharing its full telemetry record.</p>
      </article>
      <article class="use-case-card">
        <span class="use-case-icon-wrap"><svg class="use-case-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M7 7h13m-4-4 4 4-4 4M17 17H4m4-4-4 4 4 4"/></svg></span>
        <h3>Information exchange</h3>
        <p>Two organizations could exchange the verifiable outcome of an agreed check while keeping private inputs at their source.</p>
      </article>
      <article class="use-case-card">
        <span class="use-case-icon-wrap"><svg class="use-case-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M3 7 12 2l9 5v10l-9 5-9-5V7Z"/><path d="m3 7 9 5 9-5M12 12v10M8 4l9 5"/></svg></span>
        <h3>Logistics and transport</h3>
        <p>A temperature-sensitive shipment could support a check against an agreed limit without disclosing its entire sensor history.</p>
      </article>
      <article class="use-case-card">
        <span class="use-case-icon-wrap"><svg class="use-case-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M4 18a8 8 0 1 1 16 0M12 14l4-4M8 19h8"/><circle cx="12" cy="14" r="1"/></svg></span>
        <h3>Industrial monitoring</h3>
        <p>An operator could demonstrate that a technical threshold was respected without exposing all measurements from its equipment.</p>
      </article>
      <article class="use-case-card">
        <span class="use-case-icon-wrap"><svg class="use-case-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="8" cy="7" r="3"/><circle cx="17" cy="8" r="2.5"/><path d="M2 21v-3a6 6 0 0 1 12 0v3M14 15a5 5 0 0 1 8 4v2"/></svg></span>
        <h3>Collaborative research</h3>
        <p>Research teams could verify agreed properties of sensitive datasets without exchanging the raw records between them.</p>
      </article>
    </div>
  </section>
'''
    figure_match = re.search(r'<figure class="tech-animation".*?</figure>', TECH_TOOLING, flags=re.S)
    if figure_match is None or TECH_TOOLING.count('<figure class="tech-animation"') != 1:
        raise ValueError("technical animation source changed")
    figure = figure_match.group()
    tooling_details = TECH_TOOLING.replace(figure, '', 1)
    mission = mission.replace(
        'aria-labelledby="mission-title">\n',
        'aria-labelledby="mission-title">\n'
        '    <p class="section-overline">02 / HOW IT WORKS</p>\n'
        '    <h2 class="section-display">Can a vehicle prove it respects a speed limit without revealing its speed?</h2>\n'
        '    <p class="editorial-chapter-intro">TAG researches how a cryptographic proof could confirm that a private speed value meets a public limit, while keeping the exact value confidential.</p>\n',
        1,
    )
    if 'Can a vehicle prove it respects a speed limit without revealing its speed?' not in mission:
        raise ValueError("mission heading replacement failed")
    # Simplify the visitor-facing readout without touching source or animation JS.
    mission_copy = {
        "No live backend · independent of illustration": "Illustrative mission",
        "Execution deliberately disabled": "Three synthetic routes",
        "<dt>Execution</dt>": "<dt>Source</dt>",
        "DISABLED · static showcase only": "Synthetic only",
        "<dt>Proof generation</dt>": "<dt>Proof on this page</dt>",
        "<dt>Cryptographic verification</dt>": "<dt>Verification on this page</dt>",
        "These fields never represent running computation on this public site. The mock scenario panel and independently recorded offline-verifier result below remain separate from the illustration.":
            "Choose a route to explore a predefined animation. Neither the route nor the vehicle represents measured telemetry.",
        "EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION. No MAVLink commands, navigation control, mission edits, or source assurance. Animation never changes evidence status.":
            "Route selection shows three patterns for the same verification concept.",
    }
    for old, new in mission_copy.items():
        if mission.count(old) != 1:
            raise ValueError("public mission copy drift: " + old[:30])
        mission = mission.replace(old, new, 1)
    for ident, val in (("mission-backend-proof", "Not generated"),
                       ("mission-backend-crypto", "Not performed")):
        old = f'id="{ident}">NOT_OBSERVED</dd>'
        if mission.count(old) != 1:
            raise ValueError("public mission state drift: " + ident)
        mission = mission.replace(old, f'id="{ident}">{val}</dd>', 1)
    side_match = re.search(r'<aside class="mission-side".*?</aside>', mission, flags=re.S)
    if side_match is None or mission.count('<aside class="mission-side"') != 1:
        raise ValueError("public mission sidebar drift")
    mission = mission.replace(side_match.group(), '''<aside class="mission-side" aria-label="Speed-limit verification example">
        <div class="mission-readout mission-speed-example">
          <p class="mission-label">THE SPEED-LIMIT EXAMPLE</p>
          <h3>What could a proof confirm?</h3>
          <p>Imagine the vehicle has measured its speed. The aim is to check a rule without making the exact reading public.</p>
          <dl class="mission-speed-facts">
            <div class="mission-speed-fact">
              <dt>Private information</dt>
              <dd>The exact speed value</dd>
            </div>
            <div class="mission-speed-fact">
              <dt>Public rule</dt>
              <dd>The maximum permitted speed</dd>
            </div>
            <div class="mission-speed-fact">
              <dt>Verifiable claim</dt>
              <dd>The private value is within the public limit</dd>
            </div>
          </dl>
          <p class="mission-speed-conclusion">A zero-knowledge proof could support that claim without revealing the exact speed.</p>
        </div>
      </aside>''', 1)
    mission = re.sub(r'\n    <p class="mission-boundary">.*?</p>', "", mission, count=1, flags=re.S)
    # Explain what the route visualizes; it is not itself the cryptographic result.
    mission_top_copy = {
        "Mission Control · synthetic visualization": "A VEHICLE IN MOTION",
        "Observation only, never vehicle control": "Three routes, one question about speed",
        "A predefined 2.5D vehicle and route illustrate the concept. Motion is not telemetry, a measured trajectory, a live mission, proof generation, or verification progress.":
            "Explore how the vehicle moves between A, B and C. The research question is whether a speed measurement meets a defined limit while its precise value stays private.",
        "Illustrative scene": "Choose a route",
        "Observation pass · A–B–C": "Travel from A to C · A–B–C",
        "Hold at waypoint · A–B": "Stop at B · A–B",
        "Return route · A–B–A": "Return to A · A–B–A",
        "Ready · prerecorded illustration only": "Explore the routes",
    }
    for old, new in mission_top_copy.items():
        if mission.count(old) != 1:
            raise ValueError("mission public copy drift: " + old[:32])
        mission = mission.replace(old, new, 1)
    # Reframe route labels as concept presentation, not a runtime disclaimer.
    mission_labels = {
        "ILLUSTRATION ONLY · NO LIVE STREAM": "MISSION PATTERNS · SELECT A ROUTE",
        "SYNTHETIC ROUTE · NOT GEOGRAPHIC": "MISSION ROUTE · THREE PATTERNS",
    }
    for old, new in mission_labels.items():
        if mission.count(old) != 1:
            raise ValueError("mission route label drift: "+old)
        mission = mission.replace(old, new, 1)
    proof_explainer = '''    <div class="editorial-process" aria-labelledby="editorial-process-title">
      <p class="section-overline">THE PROOF IN THREE STEPS</p>
      <h3 id="editorial-process-title">From private data to a verifiable result</h3>
      <p class="editorial-proof-intro">TAG studies how a defined condition can be checked without disclosing the underlying private value.</p>
    </div>
'''
    last = mission.rfind('  </section>')
    if last < 0:
        raise ValueError("mission section end missing")
    mission = mission[:last] + proof_explainer + '    <div class="editorial-proof-animation">\n' + figure + '\n    </div>\n' + mission[last:]
    if scope.count('  </details>') != 1:
        raise ValueError("technical scope structure changed")
    scope = scope.replace('  </details>',
        '    <p class="editorial-caveat">No MAVLink commands, navigation control, mission edits, or source assurance are provided by this static site.</p>\n  </details>', 1)
    research = '''  <section class="research-limits" id="research" aria-labelledby="research-title">
    <p class="section-overline">04 / THE RESEARCH</p>
    <h2 class="section-display" id="research-title">From the TAG research journal</h2>
    <p class="editorial-chapter-intro">What we tested in the lab, what we learned and what still needs to be demonstrated.</p>
    <!-- TAG_RESEARCH_JOURNAL -->
    <h3 class="research-secondary-title">Inside the experiments</h3>
    <p class="research-technical-intro">The journal above records accepted findings. Open a topic below for the method, the recorded evidence or what still needs testing.</p>
    <div class="research-release" aria-label="Published research version">
      <span>Research notes and evidence are published together from the TAG repository.</span>
      <!-- TAG_RESEARCH_RELEASE -->
    </div>
    <div class="research-details" aria-label="Technical research panels">
      <details class="research-detail" id="technical-evidence">
        <summary><span class="research-detail-heading">How the proof works</span><span class="research-detail-teaser">The rule, the proof and independent verification</span></summary>
        <div class="research-detail-body">
          <div class="research-simple-grid research-methods" aria-label="Three stages of the offline proof experiment">
            <article><span>01</span><h4>Define the condition</h4><p>Noir describes a comparison between a private speed value and a public limit.</p></article>
            <article><span>02</span><h4>Create the proof</h4><p>Barretenberg uses the private witness to generate a proof of that condition.</p></article>
            <article><span>03</span><h4>Verify independently</h4><p>An offline verifier checks the proof with the expected verification key, without receiving the private speed.</p></article>
          </div>
          <details class="research-archive">
            <summary>Tool versions, full method and source documentation</summary>
            <div class="research-archive-body">''' + tooling_details + '''</div>
          </details>
        </div>
      </details>
      <details class="research-detail" id="laboratory-scenarios">
        <summary><span class="research-detail-heading">Recorded laboratory evidence</span><span class="research-detail-teaser">Separate offline verification from simulated orchestration</span></summary>
        <div class="research-detail-body">
          <div class="research-simple-grid research-outcomes">
            <article><span>INDEPENDENT OFFLINE EXPERIMENT</span><h4><!-- TAG_OFFLINE_OUTCOME --></h4><p>The recorded verifier result is from a separate experiment with synthetic data. No cryptographic verification happens on this page.</p></article>
            <article><span>DETERMINISTIC SCENARIOS</span><h4><!-- TAG_SCENARIO_COUNT --> recorded cases</h4><p>These cases exercise orchestration, input changes and publication states. They do not constitute independently verified cryptographic proofs.</p></article>
          </div>
          <p class="research-method-boundary">A separate isolated GitHub Actions run has now generated and independently verified a synthetic SITL-derived ZKP. The cases below remain static mock replays, not live proof execution in the browser.</p>
          <details class="research-archive">
            <summary>Explore recorded scenarios and the full offline result</summary>
            <div class="research-archive-body"><p class="editorial-caveat">The scenario controls replay static fixtures; their progress and publication indicators are not live operations.</p>
''' + evidence + '''</div>
          </details>
        </div>
      </details>
      <details class="research-detail" id="research-limitations">
        <summary><span class="research-detail-heading">Limits and next validation steps</span><span class="research-detail-teaser">What a successful cryptographic check cannot establish</span></summary>
        <div class="research-detail-body">
          <div class="research-simple-grid research-boundaries">
            <article><h4>Source and time</h4><p>A valid proof alone does not establish who produced a measurement or whether its time is trustworthy.</p></article>
            <article><h4>Coverage and integration</h4><p>One bounded two-observation SITL-to-ZKP run passed; whole-mission coverage, source authentication and trusted time remain unproven.</p></article>
            <article><h4>Operational use</h4><p>Safety, policy acceptance, customer decisions and production readiness require separate validation.</p></article>
          </div>
          <details class="research-archive">
            <summary>Full experimental boundaries and assurance fields</summary>
            <div class="research-archive-body">''' + scope + '''</div>
          </details>
        </div>
      </details>
    </div>
  </section>
'''
    html = html[:a] + intro + mission + applications + research + html[f:]
    footer_old = "Public static technology showcase. Experimental synthetic-only, precomputed results. No visitor execution, vehicle connection, telemetry upload, analytics, tracking, external fonts or proof jobs. The browser does not independently verify proofs."
    footer_new = "TAG · Telemetry Attestation Gateway. Exploring verifiable conditions, selective disclosure and privacy-preserving telemetry."
    if html.count(footer_old) != 1:
        raise ValueError("public footer source changed")
    html = html.replace(footer_old, footer_new, 1)
    footer_anchor = '<footer id="console-footer">'
    if html.count(footer_anchor) != 1:
        raise ValueError("public ROCSI affiliation footer anchor changed")
    html = html.replace(
        footer_anchor,
        '<aside class="rocsi-affiliation" aria-labelledby="rocsi-affiliation-title">'
        '<img class="rocsi-affiliation-mark" src="/assets/rocsi-mark.svg" alt="" width="60" height="60" loading="lazy" decoding="async">'
        '<div class="rocsi-affiliation-copy"><h3 id="rocsi-affiliation-title">TAG is a research initiative of the Romanian Cyber Space Initiative.</h3>'
        '<p>Discover more of ROCSI\'s open research and explore collaboration opportunities.</p></div>'
        '<div class="rocsi-affiliation-actions"><a href="https://rocsi.eu/en">Explore ROCSI</a></div>'
        '</aside>\n' + footer_anchor,
        1,
    )
    public_notice = '<div class="notice" role="note">EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION</div>\n'
    if html.count(public_notice) != 1:
        raise ValueError("public notice source changed")
    html = html.replace(public_notice, "", 1)
    if html.count("</style>") != 1:
        raise ValueError("public style shape changed")
    if html.count("</script>") != 1:
        raise ValueError("public script shape changed")
    # Only the public replay gets paired panels and screen-reader control linkage.
    selector_tag = '<select id="scenario" disabled>'
    results_tag = '<aside class="card" aria-labelledby="outcomes-title">'
    results_title = '<h2 id="outcomes-title">Recorded typed outcomes</h2>'
    controller_tag = '<section class="card" aria-labelledby="scenario-title">'
    for marker in (selector_tag, results_tag, results_title, controller_tag):
        if html.count(marker) != 1:
            raise ValueError("scenario presentation anchor changed")
    html = html.replace(
        selector_tag,
        '<select id="scenario" aria-controls="scenario-explanation scenario-results" disabled>',
        1,
    )
    html = html.replace(
        controller_tag,
        '<section class="card scenario-controller" aria-labelledby="scenario-title">',
        1,
    )
    html = html.replace(
        results_tag,
        '<aside class="card scenario-results" id="scenario-results" aria-labelledby="outcomes-title">',
        1,
    )
    html = html.replace(
        results_title,
        results_title + '\n      <p class="scenario-active" id="scenario-active" aria-live="off"></p>',
        1,
    )
    # Public-only context for the already existing selector; no new data source.
    selector_anchor = '<p id="error" role="status" aria-live="polite"></p>'
    if html.count(selector_anchor) != 1:
        raise ValueError("scenario replay anchor changed")
    html = html.replace(
        selector_anchor,
        selector_anchor + '\n      <p class="scenario-explanation" id="scenario-explanation" role="status" aria-live="polite"></p>',
        1,
    )
    render_anchor = "function render(e) {"
    if html.count(render_anchor) != 1:
        raise ValueError("scenario render anchor changed")
    html = html.replace(
        render_anchor,
        render_anchor + '\n  renderScenarioInterpretation($("scenario").value,e);',
        1,
    )
    html = public_cinematic_motion(html)
    # The local console retains its scenarios. Public showcase presents one
    # proposed UAS–TAG–C2 flow, preserving the separate proof explainer below.
    mission_start = html.index('  <section class="mission-control"')
    mission_end = html.index('  <section class="use-cases"', mission_start)
    previous = html[mission_start:mission_end]
    proof_start = previous.index('    <div class="editorial-process"')
    proof_end = previous.rfind('  </section>')
    if proof_end <= proof_start or previous.count('id="mission-pattern"') != 1:
        raise ValueError("public mission source unexpectedly changed")
    proof_explanation = previous[proof_start:proof_end]
    # One public explanation: remove the duplicate heading, caption and status
    # from the already-processed figure. Retain its animated three-stage SVG.
    for obsolete in (
        r'\s*<div class="tech-animation-top">.*?</div>\s*<p class="tech-animation-caption">.*?</p>',
        r'\s*<figcaption class="tech-animation-status".*?</figcaption>',
    ):
        proof_explanation, removed = re.subn(obsolete, '', proof_explanation, count=1, flags=re.S)
        if removed != 1:
            raise ValueError("public proof figure duplicate copy changed")
    html = (html[:mission_start] + ARCHITECTURE_PUBLIC_HTML + proof_explanation
            + '  </section>\n' + html[mission_end:])
    html = html.replace("</script>", TECH_ANIMATION_JS + SCENARIO_INTERPRETATION_JS + CONCEPT_VISIBILITY_JS + "\n</script>", 1)
    return html.replace("</style>", VISUAL_CSS + EDITORIAL_CSS + CONCEPT_CSS + MISSION_EXPLAIN_CSS + ARCHITECTURE_CSS + "  </style>", 1)

PUBLIC_THEME_CSS = """
    :root{font:16px/1.5 Arial,Helvetica,system-ui,sans-serif;color:#f1f0eb;background:#0a0d0e}
    *{box-sizing:border-box}html{scroll-behavior:smooth}
    body{margin:0;min-height:100vh;background:radial-gradient(circle at 88% 4%,#243037 0,transparent 27%),#0a0d0e;color:#f1f0eb}
    a{color:#e7c58e}a:focus-visible{outline:3px solid #f1d4a2;outline-offset:4px}
    .wrap{max-width:1560px;margin:auto;padding:0 clamp(18px,5vw,92px) 68px}
    .site-header{display:flex;align-items:center;gap:20px;flex-wrap:wrap;min-height:94px;border-bottom:1px solid #3d4548;padding:16px 0}
    .brand{display:flex;align-items:center;gap:11px;text-decoration:none;color:#f7f4eb;min-width:0}
    .brand-rocsi-mark{display:block;width:34px;height:34px;flex:none;object-fit:contain}
    .brand-signal{font-size:1.72rem;font-weight:900;letter-spacing:-.09em}
    .brand-detail{font-size:.66rem;letter-spacing:.11em;text-transform:uppercase;color:#c2c7c8;max-width:200px;line-height:1.45}
    .section-nav{display:flex;align-items:center;flex-wrap:wrap;gap:22px;margin-left:auto}
    .section-nav a{text-decoration:none;font-size:.75rem;letter-spacing:.04em;color:#cbd0cf}
    .section-nav a:hover{color:#fff}
    .header-status{display:flex;align-items:center;gap:12px;flex-wrap:wrap}
    .header-cta{display:inline-flex;align-items:center;justify-content:center;min-height:42px;padding:9px 13px;border:1px solid #dfbb83;color:#f6e5c9;text-decoration:none;font-size:.74rem;font-weight:750;text-align:center}
    .header-cta:hover{background:#dfbb83;color:#121717}
    .pill{font-size:.62rem;letter-spacing:.07em;border:1px solid #555c5d;border-radius:99px;padding:6px 12px;color:#c7cdcc}
    .hero{display:grid;grid-template-columns:minmax(0,1.04fr) minmax(0,.96fr);gap:clamp(22px,4vw,66px);align-items:stretch;min-height:clamp(560px,75vh,780px);padding:clamp(48px,6vw,82px) 0 clamp(48px,7vw,96px);border-bottom:1px solid #3d4548}
    .hero-content{display:flex;flex-direction:column;align-items:flex-start;justify-content:center;min-width:0}
    .hero-overline,.section-overline,.hero-art-label{font-size:.7rem;letter-spacing:.16em;text-transform:uppercase;font-weight:800;color:#e3be83}
    .hero h1{font-size:clamp(3.3rem,6.3vw,7.1rem);max-width:11ch;line-height:.98;letter-spacing:-.065em;font-weight:820;margin:22px 0 26px;text-wrap:balance}
    .hero .sub{max-width:57ch;color:#d4d8d6;font-size:clamp(.97rem,1.1vw,1.1rem);line-height:1.68}
    .hero-actions{margin-top:25px;display:flex;gap:12px;flex-wrap:wrap}
    .hero-actions a{display:inline-flex;align-items:center;justify-content:center;padding:14px 18px;background:#e5c18a;border:1px solid #e5c18a;color:#111617;text-decoration:none;font-size:.81rem;font-weight:750}
    .hero-actions a:hover{background:#f0d9ad}
    .hero-art{position:relative;overflow:hidden;isolation:isolate;min-height:0;aspect-ratio:760/700;align-self:center;border:1px solid #355056;background:radial-gradient(ellipse at 58% 53%,#203e47 0,#0d1a20 53%,#0b1216 88%)}
    .hero-art-label{position:absolute;z-index:2;top:22px;left:22px;color:#d4d7cf}
    .hero-scene{display:block;position:absolute;inset:0;width:100%;height:100%;overflow:hidden}
    .hero-flight{transform-box:view-box;transform-origin:0 0;animation:public-flight 3s linear infinite}
    .hero-sweep{transform-origin:385px 350px;animation:public-radar 6s linear infinite}
    .hero-route-flow{animation:public-route 3s linear infinite}
    .hero-rotor-disc{transform-box:fill-box;transform-origin:center;animation:public-rotor .375s linear infinite}
    .hero-beacon-pulse{transform-box:fill-box;transform-origin:center;animation:public-beacon 3s ease-out infinite}
    @keyframes public-flight{
      0%,100%{transform:translate(195px,510px) scale(.676) translate(-389px,-350px)}
      16%{transform:translate(210px,325px) scale(.676) translate(-389px,-350px)}
      33%{transform:translate(385px,180px) scale(.676) translate(-389px,-350px)}
      48%{transform:translate(510px,245px) scale(.676) translate(-389px,-350px)}
      65%{transform:translate(550px,450px) scale(.676) translate(-389px,-350px)}
      83%{transform:translate(370px,515px) scale(.676) translate(-389px,-350px)}
    }
    @keyframes public-radar{to{transform:rotate(360deg)}}
    @keyframes public-route{to{stroke-dashoffset:-390}}
    @keyframes public-rotor{to{transform:rotate(360deg)}}
    @keyframes public-beacon{0%,100%{opacity:.2;transform:scale(.9)}50%{opacity:.7;transform:scale(1.2)}}
    .primer{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:clamp(25px,4vw,68px);padding:clamp(54px,7vw,110px) 0;border-bottom:1px solid #3d4548;scroll-margin-top:25px}
    .primer h2{font-size:clamp(2.05rem,3.75vw,4.65rem);line-height:1.08;letter-spacing:-.055em;color:#f7f4eb;text-wrap:balance}
    .primer .primer-copy p{color:#c7cdcb;line-height:1.73;font-size:.98rem}
    .primer .primer-example{padding-left:17px;border-left:2px solid #d8b67b;color:#eee7d9}
    .section-display{font-size:clamp(2.15rem,4.2vw,4.9rem);font-weight:780;line-height:1.09;letter-spacing:-.055em;margin:0 0 27px;text-wrap:balance}
    .rocsi-affiliation{display:flex;align-items:center;flex-wrap:wrap;gap:18px 28px;margin:clamp(40px,6vw,72px) 0;padding:27px 0;border-top:1px solid #3d4548;border-bottom:1px solid #3d4548}
    .rocsi-affiliation-mark{display:block;width:60px;height:60px;flex:none}
    .rocsi-affiliation-copy{flex:1;min-width:210px}.rocsi-affiliation h3{font-size:1.18rem;margin:0 0 7px}
    .rocsi-affiliation p{margin:0;color:#c6d0cd;font-size:.9rem;line-height:1.6}
    .rocsi-affiliation-actions a{color:#e4c58e;text-decoration:underline;text-underline-offset:5px;font-weight:700;font-size:.87rem}
    footer{font-size:.76rem;color:#aebdb7;line-height:1.6}
    @media(max-width:1100px){.section-nav{order:3;flex-basis:100%;margin-left:0}.hero{min-height:0}}
    @media(max-width:750px){html{scroll-behavior:auto}.wrap{padding:0 18px 44px}.site-header{min-height:0;gap:12px 18px}.section-nav{gap:12px 18px}.header-status .pill{display:none}.hero{grid-template-columns:1fr;gap:24px;padding:18px 0 55px}.hero h1{font-size:clamp(2.8rem,10.8vw,4.6rem);margin:13px 0 18px}.hero .sub{font-size:.94rem}.hero-art{min-height:0;order:-1}.primer{padding:54px 0}.rocsi-affiliation{align-items:flex-start}}
    @media(max-width:420px){.brand-detail{font-size:.58rem}.section-nav{gap:9px 16px}.section-nav a{font-size:.7rem}.header-cta{font-size:.7rem}.hero h1{font-size:clamp(2.6rem,12vw,3.3rem)}.hero-art{min-height:0}.hero-art-label{top:14px;left:13px;font-size:.61rem}.hero-actions a{width:100%}}
    /* Compact initial mobile viewport; keep the illustration before readable copy. */
    @media(max-width:750px){
      .site-header{padding:9px 0;gap:8px 12px}
      .header-status{gap:8px}
      .header-cta{min-height:36px;padding:6px 12px}
      .section-nav{gap:8px 14px}
      .hero{gap:12px;padding:12px 0 42px}
      .hero-art{width:min(100%,clamp(150px,34svh,340px));justify-self:center}
      .hero-art-label{top:9px;left:10px;font-size:.57rem;letter-spacing:.1em}
      .hero-content{width:100%}
      .hero-overline{font-size:.64rem;letter-spacing:.08em;margin:0}
      .hero h1{font-size:clamp(1.7rem,7.1vw,2.8rem);max-width:none;line-height:1.09;letter-spacing:-.04em;margin:7px 0 8px;text-wrap:balance}
      .hero .sub{font-size:.91rem;line-height:1.42;margin:0}
      .hero-actions{margin-top:11px;width:100%}
      .hero-actions a{width:auto;min-height:44px;padding:9px 15px}
    }
    @media(max-width:750px) and (max-height:590px){
      .hero-art{width:min(100%,clamp(128px,25svh,200px))}
      .hero{gap:9px;padding-top:9px}
    }
    @media(prefers-reduced-motion:reduce){.hero-scene *{animation:none!important}}
"""

# TAG / PUBLIC-UX-SIMPLIFICATION-01: public-only static editorial surface.
# Reuse the already-drawn hero and concept, but do not ship the replay UI,
# technical archives, precomputed JSON clients, controls, or browser scripts.
PUBLIC_SIMPLE_CSS = """
    .section-nav{gap:clamp(12px,2vw,28px)}
    .hero-actions a{min-width:185px;text-align:center}
    .public-demo{padding:clamp(48px,7vw,92px) 0;border-top:1px solid #415256;scroll-margin-top:30px}
    .public-demo .section-display{max-width:23ch}
    .public-demo-lead{max-width:70ch;font-size:clamp(1rem,1.35vw,1.15rem);line-height:1.7;color:#d5dcd7;margin:16px 0 33px}
    .public-steps{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;list-style:none;padding:0;margin:0}
    .public-step{min-width:0;min-height:224px;padding:clamp(20px,2.7vw,32px);border:1px solid #466168;background:#102329;animation:public-phase 20s linear infinite}
    .public-step:nth-child(2){animation-delay:-13.33s}
    .public-step:nth-child(3){animation-delay:-6.67s}
    .public-step small{color:#e4c58e;font-size:.7rem;font-weight:800;letter-spacing:.15em}
    .public-step h3{font-size:clamp(1.3rem,2.15vw,2.1rem);line-height:1.16;letter-spacing:-.03em;margin:23px 0 13px;color:#f7f0e2}
    .public-step p{font-size:.94rem;line-height:1.63;color:#c8d4d0;margin:0}
    @keyframes public-phase{0%,30%{border-color:#e5c18a;background:#1e3335;box-shadow:inset 0 3px 0 #e5c18a}33%,100%{border-color:#466168;background:#102329;box-shadow:none}}
    .public-outcomes{padding:clamp(35px,5vw,65px) 0 30px;border-top:1px solid #415256;scroll-margin-top:30px}
    .public-outcomes h2{font-size:clamp(1.8rem,3vw,3rem);max-width:24ch}
    .public-results{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin:30px 0}
    .public-result{padding:24px;border-left:3px solid #b5d8cd;background:#17282c}
    .public-result strong{display:block;color:#ebd1a4;font-size:1.12rem;margin-bottom:10px}
    .public-result p{margin:0;color:#ccd7d0;line-height:1.6;font-size:.9rem}
    .public-progress{margin:0 0 24px;max-width:85ch;color:#d5dcd7;line-height:1.7}
    .public-progress strong{color:#efcc97}
    .public-limits{max-width:83ch;padding:20px 24px;border:1px solid #586165;background:#111e21;line-height:1.7;color:#c7d2cc}
    .public-limits strong{color:#f1dfbd}
    .public-documentation{margin:24px 0 0}
    .public-documentation a{color:#eed09a;text-underline-offset:5px;font-weight:700}
    @media(max-width:750px){.public-steps,.public-results{grid-template-columns:1fr}.public-step{min-height:0}.public-step h3{margin:12px 0}.public-demo{padding-top:48px}.public-result{padding:19px}}
    @media(prefers-reduced-motion:reduce){.public-step{animation:none!important}.hero-scene *,.concept-cinema *{animation:none!important}}
"""


def public_hero_flight(hero: str) -> str:
    """Adapt only the public hero: closed synthetic route, continuous CSS motion."""
    old_route = "M98 548C225 522 305 439 389 350S569 203 681 136"
    route = "M195 510L210 325L385 180L510 245L550 450L370 515Z"
    if hero.count(old_route) != 4 or hero.count('<g class="hero-floor-shadow">') != 1:
        raise ValueError("public hero route anchor changed")
    hero = hero.replace(old_route, route)
    for old, new in (("translate(98 548)", "translate(195 510)"),
                     ("translate(389 350)", "translate(385 180)"),
                     ("translate(681 136)", "translate(550 450)")):
        # Only the waypoint groups: keep the original vehicle's local transform.
        anchor = '<g transform="' + old + '">'
        if hero.count(anchor) != 1:
            raise ValueError("public hero waypoint anchor changed")
        hero = hero.replace(anchor, '<g transform="' + new + '">', 1)
    old_labels = '<text x="78" y="582">A</text><text x="409" y="340" opacity=".68">B</text><text x="683" y="117">C</text>'
    new_labels = '<text x="75" y="565">A</text><text x="382" y="87">B</text><text x="680" y="452">C</text>'
    if hero.count(old_labels) != 1 or hero.count('</svg>') < 1:
        raise ValueError("public hero label anchor changed")
    hero = hero.replace(old_labels, new_labels, 1)
    # The shadow and original artwork move together. The SVG attribute is the
    # exact resting pose, including when reduced motion disables all animation.
    hero = hero.replace('<g class="hero-floor-shadow">',
                        '<g class="hero-flight" transform="translate(195 510) scale(.676) translate(-389 -350)"><g class="hero-floor-shadow">', 1)
    end = '<!-- The route and A/B/C landmarks are intentionally self-explanatory; no internal instrument labels. -->'
    if hero.count(end) != 1:
        raise ValueError("public hero flight end anchor changed")
    return hero.replace(end, '</g>' + end, 1)


def simplify_public_html(html: str) -> str:
    """Replace the visitor body at known static landmarks; fail closed on drift."""
    def unique(pattern: str, label: str) -> str:
        matches = re.findall(pattern, html, flags=re.S)
        if len(matches) != 1:
            raise ValueError("public simplification anchor changed: " + label)
        return matches[0]

    if html.count('<body>') != 1 or html.count('</body>') != 1:
        raise ValueError("unexpected public document shape")
    header = unique(r'<header class="site-header">.*?</header>', "header")
    hero = unique(r'<section class="hero".*?</section>', "hero")
    intro = unique(r'<section class="primer".*?</section>', "concept")
    affiliation = unique(r'<aside class="rocsi-affiliation".*?</aside>', "ROCSI affiliation")
    if header.count('<nav class="section-nav"') != 1 or hero.count('class="hero-actions"') != 1:
        raise ValueError("unexpected public navigation")
    header = re.sub(r'<nav class="section-nav".*?</nav>',
        '<nav class="section-nav" aria-label="Page sections">'
        '<a href="#principle">The Concept</a><a href="#demonstration">The Demonstration</a>'
        '<a href="#results">Results</a></nav>', header, count=1, flags=re.S)
    hero = re.sub(r'<div class="hero-actions">.*?</div>',
        '<div class="hero-actions"><a href="#demonstration">See the demonstration</a></div>',
        hero, count=1, flags=re.S)
    hero = public_hero_flight(hero)
    # Retain the original artwork and the original explanation of the private value.
    demo = '''<section class="public-demo" id="demonstration" aria-labelledby="demo-title">
      <p class="section-overline">THE DEMONSTRATION</p>
      <h2 class="section-display" id="demo-title">Telemetry → cryptographic proof → verification</h2>
      <p class="public-demo-lead">We check whether a condition is met without revealing the data behind it. This twenty-second visual sequence illustrates the idea automatically; it is not a live computation.</p>
      <ol class="public-steps" aria-label="Three stages of the conceptual verification flow">
        <li class="public-step"><small>01 / TELEMETRY</small><h3>Receive observations</h3><p>A simulator produces synthetic observations. The exact value need not be shown to the verifier.</p></li>
        <li class="public-step"><small>02 / CRYPTOGRAPHIC PROOF</small><h3>Generate a proof</h3><p>A zero-knowledge proof supports a defined condition using the private input.</p></li>
        <li class="public-step"><small>03 / VERIFICATION</small><h3>Check independently</h3><p>A verifier checks the proof without needing the private measurement.</p></li>
      </ol>
    </section>
    <section class="public-outcomes" id="results" aria-labelledby="results-title">
      <p class="section-overline">DOCUMENTED EXPERIMENTAL RESULTS</p>
      <h2 id="results-title">Three steps confirmed in synthetic laboratory tests</h2>
      <div class="public-results">
        <article class="public-result"><strong>Synthetic telemetry received</strong><p>Simulator observations reached the experimental processing flow.</p></article>
        <article class="public-result"><strong>ZKP generated</strong><p>A cryptographic proof was generated for the bounded synthetic test.</p></article>
        <article class="public-result"><strong>Independent verification passed</strong><p>A separate verifier successfully checked the synthetic proof offline.</p></article>
      </div>
      <p class="public-progress"><strong>Research progress.</strong> In a synthetic experiment, we checked the signing key and signature, applied session-local replay protection and independently verified a zero-knowledge proof bound to the observation. Separate tests with a mock proof verifier rejected replay after restart using retained local state. Restoring old state defeats this protection. Separate synthetic tests with a mock proof verifier checked reception freshness using an authenticated time reference from a simulated authority separate from the telemetry source. This does not establish physical capture time or a real trusted-time service. The signing key is a publicly known test key; real vehicle identity remains unproven.</p>
      <p class="public-limits"><strong>Experimental and synthetic only.</strong> The tests confirm an isolated end-to-end research path, not authentic flight telemetry. A valid proof does not authenticate its source, timestamp or the full mission. The published illustration and JSON recordings are not independently authenticated by this website. No live vehicle, proving, verification or operational authorization is provided.</p>
      <p class="public-documentation"><a href="https://github.com/ROCSI-eu/Telemetry-Attestation-Gateway">Technical documentation and research evidence on GitHub</a></p>
    </section>'''
    prefix = html.split('<body>', 1)[0]
    if prefix.count('</style>') != 1 or prefix.count('<style>') != 1:
        raise ValueError("public stylesheet structure changed")
    # Discard the superseded console stylesheet too: dead selectors and
    # technical panel styles must not be published merely because their DOM is gone.
    prefix = re.sub(r'<style>.*?</style>',
                    '<style>' + PUBLIC_THEME_CSS + CONCEPT_CSS + PUBLIC_SIMPLE_CSS + '</style>',
                    prefix, count=1, flags=re.S)
    footer = '<footer id="console-footer">EXPERIMENTAL · SYNTHETIC ONLY · NOT VALIDATION OR PRODUCTION AUTHORIZATION. TAG is a ROCSI research project.</footer>'
    result = (prefix + '<body>\n<main class="wrap">\n' + header + '\n' + hero + '\n'
              + intro + '\n' + demo + '\n' + affiliation + '\n' + footer
              + '\n</main>\n</body>\n</html>')
    if any(token in result for token in ('<script', '<details', '<select', '<button',
                                         'id="scenario"', 'id="authentic-panel"',
                                         'A0_SYNTHETIC')):
        raise ValueError("technical replay leaked into simplified public page")
    return result
