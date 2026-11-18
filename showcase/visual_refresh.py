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
    .proof-evidence-checkpoint{border:1px solid #405357;background:#142125;padding:18px 20px;margin:8px 0 24px}
    .proof-evidence-checkpoint h4{color:#e7c58e;font-size:.8rem;letter-spacing:.08em;text-transform:uppercase;margin:0 0 10px}
    .proof-evidence-checkpoint p{color:#c2d0ce;font-size:.87rem;line-height:1.62;margin:8px 0}
    .proof-tooling-links{display:flex;gap:10px 22px;flex-wrap:wrap;font-size:.83rem;margin:0 0 22px}
    .proof-tooling-links a{color:#e7c58e;text-underline-offset:3px}
    .proof-tooling-boundary{border-left:2px solid #bda072;padding-left:15px;margin:0}

    /* TAG-TECH-ANIMATION-01: browser-only conceptual illustration; not evidence. */
    .tech-animation{margin:22px 0 28px;padding:clamp(14px,2.4vw,24px);border:1px solid #456066;background:radial-gradient(ellipse at 50% 15%,#1a343d,#0b161b 78%);min-width:0}
    .tech-animation svg{display:block;width:100%;height:auto;overflow:visible}
    .tech-animation .tech-panel{fill:#12272d;stroke:#42626b;stroke-width:2}
    .tech-animation .tech-guide{fill:none;stroke:#809da2;stroke-width:3;stroke-dasharray:8 9;opacity:.68}
    .tech-animation .tech-glyph{fill:none;stroke:#9cc8ca;stroke-width:4;stroke-linecap:round;stroke-linejoin:round}
    .tech-animation .tech-public{fill:#dfc48b}
    .tech-animation .tech-secret{fill:#19292c;stroke:#d5bd85;stroke-width:2}
    .tech-animation .tech-highlight{opacity:0;stroke:#77b8c5;stroke-width:2}
    .tech-animation .tech-end-signal{opacity:0}
    .tech-animation[data-started="true"] .tech-highlight-one{animation:tech-define 12s ease-in-out both}
    .tech-animation[data-started="true"] .tech-highlight-two{animation:tech-prove 12s ease-in-out both}
    .tech-animation[data-started="true"] .tech-highlight-three{animation:tech-verify 12s ease-in-out both}
    .tech-animation[data-started="true"] .tech-end-signal{animation:tech-end 12s linear both}
    .tech-animation[data-started="true"] .tech-transfer-one{animation:tech-transfer-one 12s ease-in-out both}
    .tech-animation[data-started="true"] .tech-transfer-two{animation:tech-transfer-two 12s ease-in-out both}
    .tech-animation[data-motion="paused"] .tech-highlight,
    .tech-animation[data-motion="paused"] .tech-end-signal,
    .tech-animation[data-visibility="hidden"] .tech-highlight,
    .tech-animation[data-visibility="hidden"] .tech-end-signal,
    .tech-animation[data-motion="paused"] .tech-transfer,
    .tech-animation[data-visibility="hidden"] .tech-transfer{animation-play-state:paused}
    .tech-animation .tech-transfer{fill:#dfc48b;opacity:0}
    @keyframes tech-transfer-one{0%,24%{opacity:0;transform:translateX(-10px)}30%{opacity:1}37%{opacity:0;transform:translateX(25px)}100%{opacity:0;transform:translateX(25px)}}
    @keyframes tech-transfer-two{0%,59%{opacity:0;transform:translateX(-10px)}65%{opacity:1}72%{opacity:0;transform:translateX(25px)}100%{opacity:0;transform:translateX(25px)}}
    @keyframes tech-define{0%,2%{opacity:0}9%,25%{opacity:.85}33%,100%{opacity:0}}
    @keyframes tech-prove{0%,32%{opacity:0}40%,57%{opacity:.85}65%,100%{opacity:0}}
    @keyframes tech-verify{0%,65%{opacity:0}73%,94%{opacity:.85}100%{opacity:.35}}
    @keyframes tech-end{0%,99%{opacity:0}100%{opacity:.01}}
    .tech-animation-top{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap}
    .tech-animation-label{font-size:.68rem;font-weight:800;letter-spacing:.12em;color:#e2c58e;text-transform:uppercase}
    .tech-animation-caption{margin:8px 0 14px;color:#b8c9ca;font-size:.82rem;line-height:1.5}
    .tech-animation-actions{display:flex;gap:8px;flex-wrap:wrap}
    .tech-animation-actions button{padding:10px 14px;font-size:.76rem;font-weight:700;min-height:42px}
    .tech-animation-actions button:disabled{opacity:.55;cursor:not-allowed}
    .tech-animation-status{font-size:.78rem;color:#c4d0cd;line-height:1.6;min-height:1.3em;margin:14px 0 0}
    @media(max-width:750px){
      .tech-animation{padding:13px;margin:20px 0 26px}
      .tech-animation-actions{width:100%}
      .tech-animation-actions button{flex:1;min-width:0}
    }
    @media(prefers-reduced-motion:reduce){
      .tech-animation .tech-highlight,.tech-animation .tech-end-signal,.tech-animation .tech-transfer{animation:none!important}
      .tech-animation .tech-highlight{opacity:.27}
      .tech-animation .tech-transfer,.tech-animation .tech-end-signal{opacity:0}
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

    /* TAG-HERO-CINEMATIC-01: deterministic, decorative synthetic SVG; no real footage or telemetry. */
    .hero-art{background:#071116;box-shadow:inset 0 0 75px #01090ab8,0 14px 52px #01070938}
    .hero-art:before{opacity:.24;background:repeating-linear-gradient(0deg,transparent 0 72px,#6e9b9e35 73px),repeating-linear-gradient(90deg,transparent 0 72px,#6e9b9e35 73px)}
    .hero-art:after{background:linear-gradient(180deg,#071216cf 0,transparent 20%,transparent 79%,#061117ea 100%),linear-gradient(90deg,#0711168e,transparent 20%,transparent 82%,#0711168e);pointer-events:none}
    .hero-scene{overflow:hidden}
    .hero-flight{transform-box:view-box;transform-origin:0 0;animation:hero-hover 10s ease-in-out infinite;will-change:transform}
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
      .hero-flight,.hero-floor-shadow,.hero-sweep,.hero-route-flow,.hero-rotor-disc,.hero-beacon-pulse{animation:none!important;will-change:auto}
    }

    @media(prefers-reduced-motion:reduce){
      .hero-actions a{transition:none}
    }
"""


HERO_SCENE_SVG = r'''<svg class="hero-scene" viewBox="0 0 760 700" preserveAspectRatio="xMidYMid meet" focusable="false">
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
        <g class="hero-flight" transform="translate(389 350)">
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
        <g fill="none" stroke="#bfd6d5" stroke-width="1" opacity=".43">
          <path d="M465 374h105v35m-335 97H143v-34"/>
        </g>
        <g fill="#bed9da" font-family="Arial,Helvetica,sans-serif" font-size="12" letter-spacing="2.1">
          <text x="578" y="425">OBS / 02</text><text x="116" y="461">ROUTE / SYN</text>
        </g>
      </svg>'''


TECH_TOOLING = """  <section class="proof-tooling" aria-labelledby="proof-tooling-title">
    <p class="proof-tooling-kicker">EXPERIMENTAL PROOF TOOLCHAIN</p>
    <h3 id="proof-tooling-title">How Noir and Barretenberg are used in TAG</h3>
    <p class="proof-tooling-intro">The synthetic bounded-speed experiment uses a pinned research toolchain: Noir/Nargo 1.0.0-beta.26 and Barretenberg bb 5.2.0. This is not a production technology selection.</p>
    <figure class="tech-animation" id="tech-animation" data-started="false" data-complete="false" data-motion="paused" data-visibility="hidden">
      <div class="tech-animation-top">
        <span class="tech-animation-label">CONCEPTUAL ANIMATION / NOT A PROOF RUN</span>
        <div class="tech-animation-actions">
          <button type="button" id="tech-animation-replay" aria-controls="tech-animation-svg">Replay explanation</button>
          <button type="button" id="tech-animation-pause" aria-controls="tech-animation-svg" aria-pressed="false" disabled>Pause illustration</button>
        </div>
      </div>
      <p class="tech-animation-caption">Three illustrative stages, not measured computation or a live verifier.</p>
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
          <text x="140" y="199">01 / NOIR</text>
          <text x="450" y="199">02 / BARRETENBERG</text>
          <text x="760" y="199">03 / OFFLINE</text>
        </g>
        <rect x="0" y="0" width="1" height="1" class="tech-end-signal"/>
      </svg>
      <figcaption class="tech-animation-status" id="tech-animation-status" role="status" aria-live="polite">Conceptual illustration · no proving or verification in this browser</figcaption>
    </figure>
    <ol class="toolchain-diagram" aria-label="Experimental proof flow, executed offline">
      <li><span>01 / DEFINE</span><strong>Noir</strong><p>Noir expresses a constraint comparing a private speed value with a public limit; Nargo compiles the circuit.</p></li>
      <li><span>02 / PROVE</span><strong>Barretenberg</strong><p>With the private witness, the pinned bb backend generates a zero-knowledge proof of the constrained statement.</p></li>
      <li><span>03 / VERIFY</span><strong>Offline verifier</strong><p>A separately invoked verifier reconstructs public inputs from canonical CBOR and checks the proof with the expected verification key, without the private speed.</p></li>
    </ol>
    <aside class="proof-evidence-checkpoint" aria-labelledby="proof-evidence-checkpoint-title">
      <h4 id="proof-evidence-checkpoint-title">SITL and offline proof: distinct evidence</h4>
      <p>Local ArduPilot Copter 4.7.1 SITL (TAG #86): PASS for isolated, receive-only MAVLink2 intake of two GLOBAL_POSITION_INT observations and TAG normalization. This does not establish telemetry truth.</p>
      <p>Independent synthetic ZK checkpoint (14 November 2026): historical Qube evidence records proof generation and offline verifier VALID with the pinned verification key. This proof was separate from the SITL observations.</p>
      <p>Combined SITL → 600 cm/s predicate → ZK: NO-GO / not demonstrated end to end. The speed predicate produced different outcomes across isolated SITL sessions; no SITL-derived ZK proof was generated or verified.</p>
    </aside>
    <nav class="proof-tooling-links" aria-label="Tool documentation and TAG implementation">
      <a href="https://www.noir-lang.org/docs/">Noir documentation</a>
      <a href="https://barretenberg.aztec.network/docs/">Barretenberg documentation</a>
      <a href="https://github.com/ROCSI-eu/Telemetry-Attestation-Gateway/tree/main/experiments/bounded-speed-proof-v0">TAG experimental implementation</a>
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
// TAG-TECH-ANIMATION-01: finite, illustrative-only SVG/CSS. Never touches evidence.
const techAnimation=$("tech-animation");
const techPause=$("tech-animation-pause");
const techReplay=$("tech-animation-replay");
const techStatus=$("tech-animation-status");
const techEnd=techAnimation.querySelector(".tech-end-signal");
const techCopy=document.documentElement.lang==="ro"?{
  pause:"Oprește animația",resume:"Continuă animația",replay:"Reia explicația",
  ready:"Ilustrație conceptuală · fără generare sau verificare în browser",
  playing:"Ilustrație conceptuală în redare · nu este progres backend",
  paused:"Ilustrație conceptuală în pauză · fără execuție backend",
  complete:"Ilustrație conceptuală încheiată · fără dovadă verificată aici",
  reduced:"Ilustrație statică · mișcare redusă; fără execuție backend"
}:{
  pause:"Pause illustration",resume:"Resume illustration",replay:"Replay explanation",
  ready:"Conceptual illustration · no proving or verification in this browser",
  playing:"Playing conceptual illustration · not backend progress",
  paused:"Conceptual illustration paused · no backend execution",
  complete:"Conceptual illustration complete · no proof verified here",
  reduced:"Static illustration · reduced motion; no backend execution"
};
function syncTechAnimation(){
  const reduce=motionPreference.matches;
  techAnimation.dataset.visibility=document.hidden||techAnimation.dataset.inview!=="true"?"hidden":"visible";
  const started=techAnimation.dataset.started==="true";
  const completed=techAnimation.dataset.complete==="true";
  const paused=techAnimation.dataset.motion==="paused";
  techReplay.disabled=reduce;
  techPause.disabled=reduce||!started||completed;
  techReplay.textContent=techCopy.replay;
  techPause.textContent=paused?techCopy.resume:techCopy.pause;
  techPause.setAttribute("aria-pressed",String(paused&&started&&!completed));
  techStatus.textContent=reduce?techCopy.reduced:
    completed?techCopy.complete:!started?techCopy.ready:paused?techCopy.paused:techCopy.playing;
}
function startTechAnimation(){
  if(motionPreference.matches)return;
  techAnimation.dataset.started="false";
  techAnimation.dataset.complete="false";
  void techAnimation.offsetWidth; // Finite CSS keyframes restart without timers.
  techAnimation.dataset.motion="playing";
  techAnimation.dataset.started="true";
  syncTechAnimation();
}
techReplay.addEventListener("click",startTechAnimation);
techPause.addEventListener("click",()=>{
  if(motionPreference.matches||techAnimation.dataset.started!=="true"||techAnimation.dataset.complete==="true")return;
  techAnimation.dataset.motion=techAnimation.dataset.motion==="paused"?"playing":"paused";
  syncTechAnimation();
});
techEnd.addEventListener("animationend",event=>{
  if(event.target!==techEnd||event.animationName!=="tech-end")return;
  techAnimation.dataset.complete="true";
  syncTechAnimation();
});
const techObserver=new IntersectionObserver(entries=>{
  const visible=entries[0].isIntersecting;
  techAnimation.dataset.inview=String(visible);
  if(visible&&techAnimation.dataset.started==="false"&&!motionPreference.matches){
    startTechAnimation();
  }else{
    syncTechAnimation();
  }
},{threshold:.2});
techObserver.observe(techAnimation);
document.addEventListener("visibilitychange",syncTechAnimation);
motionPreference.addEventListener("change",()=>{
  if(motionPreference.matches){
    techAnimation.dataset.started="false";
    techAnimation.dataset.complete="false";
    techAnimation.dataset.motion="paused";
  }else if(techAnimation.dataset.inview==="true"){
    startTechAnimation();
  }
  syncTechAnimation();
});
syncTechAnimation();
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
{HERO_SCENE_SVG}
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
    html = html.replace("</script>", TECH_ANIMATION_JS + SCENARIO_INTERPRETATION_JS + "\n</script>", 1)
    return html.replace("</style>", VISUAL_CSS + "  </style>", 1)
