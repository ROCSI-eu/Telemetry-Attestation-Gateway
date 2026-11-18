# TAG Mission Control — static public showcase (#89)

> **EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION**

**Static package:** this directory builds a separate, precomputed, static technology
showcase from the already existing Mission Control console (#87). The current
Romanian-first bilingual baseline is hosted on Cloudflare Pages at tag.rocsi.eu.
A Draft PR does not itself authorize publication; a merge **may trigger an
automatic Cloudflare deployment when enabled**. Assess that side effect before
merging, and do not infer the publicly served SHA from a GitHub check alone.
It is not a validated product, live verifier or customer workflow. Issue #88
remains independent of serving immutable static assets.

## TAG-VISUAL-REFRESH-01 — public presentation layer

The visual refresh changes the **static public showcase only**, without changing
the shared local console, CLI, verifier, scenario fixtures or browser scripts.
The visitor-facing editorial sequence is **Hero → The Concept → How It Works →
Potential Applications → The Research**, in RO and EN. The proof-stage illustration
is kept alongside the synthetic mission scene; detailed tools, laboratory scenario
replays and limitations are contained in expandable technical panels under Research.
Mock orchestration, offline-verifier evidence and unproven integrated SITL→ZK remain
explicitly distinct.
The visitor-facing chapters are a concise research presentation, not a
development status dashboard. The public GitHub-style experimental banner is
removed; the original boundary labels remain in the immutable evidence JSON
and the dedicated technical research detail. The cinematic concept scene is
aligned alongside the introduction on desktop (two explicit columns) and stacked
above the copy on mobile. Presentation-only labels replace repetitive defensive
captions. The animations remain illustrations of the concept; their motion,
offscreen suspension, accessibility preferences, precomputed results and
independent evidence boundaries remain unaffected.
Headlines are "Verifică o condiție. Păstrează restul privat." (RO) and
"Verify the condition. Keep the rest private." (EN).

The original TAG visual language uses system fonts, large type, dark industrial
surfaces, original CSS geometry and restrained warm signal accents. It adopts
general high-impact editorial design principles rather than reusing Anduril
branding, photography, fonts, code, layouts or other third-party assets.
The How It Works chapter now grounds the route visualization in the actual
research question: whether a **private speed measurement** meets a **public
speed limit** and how a future ZKP could confirm that proposition without
disclosing the exact value. The right panel uses three readable, unnumbered
value/limit/claim pairs instead of abstract numbered process labels; route
selection changes only the route description and illustration. No route state,
measured speed or proof verification is inferred or executed by the browser.
The explicit integration limitations and evidence markers remain in technical
research panels and immutable synthetic JSON outputs.

The public-only transformation lives in showcase/visual_refresh.py and is
applied after strict operator-surface removal in showcase/build.py; its
source anchors deliberately fail closed if the console structure changes.
The static site remains noindex, bilingual, CSP-hash protected and free
of analytics, external resources, real vehicle controls or browser cryptography.
The public-only presentation now adds deterministic SVG/CSS motion: both
mission and Noir/Barretenberg illustrations play automatically when visible,
without manual Start/Stop/Replay controls. The existing three synthetic mission
patterns remain selectable and restart automatically on change. Offscreen or
hidden-tab motion pauses; prefers-reduced-motion freezes both illustrations.
The local experimental console retains its original controls and logic.
Recorded mocks and offline verifier evidence remain independent of animation.

**Code-only Draft PR**: neither creating the PR nor passing QA authorizes
merging, an automatic hosting side effect or deploying the live site. Accept
the visual design in a browser and separately authorize integration. At that
point assess the currently effective Pages automatic deployment settings
before any merge, because merging may publish automatically.

### Focused acceptance

Build the same 14 files using python3 showcase/build.py --out-dir LOCAL_QA_PATH.
Run python3 -m unittest discover -s showcase -p 'test_*.py' -v and
python3 scripts/check_docs.py. In an isolated Chromium/Chrome session served
over loopback, inspect RO and EN at 1440px, 375px and 320px. Confirm the exact
hero headlines, four-chapter visitor order, expandable technical panels and
mobile navigation without overflow; verify scenario mock data and the distinct
recorded offline verifier outcome. Only
retest the changed public browser presentation: default auto-motion for both
illustrations, automatic changes among pass/hold/return, offscreen suspension,
reduced-motion fallback, and absence of animation playback buttons. The
Noir/Barretenberg graphic scrolls horizontally on narrow screens. Reuse
unaffected evidence. Localhost QA is not Production acceptance.

## Build and scope

From the repository root:

\`\`\`sh
python3 showcase/build.py --out-dir /tmp/tag-showcase
python3 -m unittest discover -s showcase -p 'test_*.py' -v
\`\`\`

Use a local static HTTP server in an authorized isolated QA environment to
inspect the generated **14 files** (13 existing assets plus one Pages redirect configuration). The allowlisted package is:

- \`ro/index.html\`: Romanian-default public page (**Centru de comandă și control**);
  \`en/index.html\`: English page (**Mission Control**). Both use the same
  sanitized HTML/CSS/JS, without the operator card, authentication or execution.
- \`404.html\` and \`en/404.html\`: localized inert not-found pages with
  experimental markings and return links, preventing Pages' implicit SPA fallback.
- \`og/ro.png\`, \`og/en.png\`: pre-rendered 1200×630, same graphic composition
  (synthetic A–B–C route and illustrative drone), separately translated captions.
- \`favicon.svg\`, \`favicon.ico\`, \`apple-touch-icon.png\`: shared drone/radar
  site identity, without text or claims of live verification.
- \`evidence-results.json\`: **strictly reconstructed** deterministic orchestration
  mock outcomes, never actual proof-verification evidence.
- \`authentic-evidence.json\`: **strictly reconstructed** precomputed synthetic
  offline-verifier result; the browser does not verify it or authenticate the JSON.
- \`_headers\`: static-host security headers including exact inline-content CSP hashes,
  same-origin-only JSON fetches, denied frames/camera/geolocation, no tracking.
- \`_redirects\`: Cloudflare Pages rule \`/ /ro/ 301\` permanently redirects
  the bare domain to canonical \`/ro/\` without duplicating Romanian HTML.
- \`robots.txt\`: allows social crawlers to retrieve the page's **static**
  Open Graph/Twitter metadata and share image. **No indexing** remains enforced by
  HTML \`robots=noindex,nofollow\` and \`X-Robots-Tag: noindex\` response header.

Build fails closed if an input fixture schema, allowlisted typed value, privacy
boundary, HTML exclusion marker or expected public-script shape changes.
No proof, witness, private speed, coordinates, credentials, restricted source
identity, CLI runner, operator endpoint, POST route, analytics, or remote fetch
is shipped. The checked-in source console and its loopback operator are unchanged
and remain local-only.

## Hosting comparison and recommendation (not activation)

**Current hosting:** Cloudflare Pages Free, project \`tag-mission-control\`.
Do not change DNS, trigger Pages builds or deploy this PR without authorization.
Build command: \`python3 showcase/build.py --out-dir dist\`.
Build output: \`dist\`; framework preset: none; no runtime functions,
environment secrets, analytics or SSR. The Pages project and custom hostname are
existing accepted setup, not provisioning tasks to repeat at each handoff.
Reuse the last verified checkpoint for unchanged work. Production/Preview
auto-deploy, current deployment identity and available rollback are **mutable
account state**, not repo invariants: do not assume they are OFF or demand fresh
dashboard screenshots for read-only/code-only tasks. Before an authorized
merge or release, check only the relevant mutable facts that could affect
publication. At a separately authorized public-activation gate, confirm
the target version's \`_headers\`, HTTP behavior and static assets. Do not
mistake GitHub SUCCESS for a live deployment or redeploy an already-live SHA.

**Alternative:** existing ROCSI Production VM served as pure static content.
This would add web-server/domain configuration, disk and operational coupling
to unrelated production sites for no technical gain. Do not use it for the
first showcase without a separate shared-host assessment and approval.

**Fallback:** a separate static-only host may be used if equivalent CSP and
no-index headers, isolation, DNS/TLS and rollback are confirmed. No public prover
is needed under any of these options.

## Localization and social preview

- \`/\` permanently redirects to \`/ro/\`; \`/ro/\` serves Romanian
  (\`<html lang="ro">\`), and \`/en/\` serves English (\`lang="en"\`).
  Native RO/EN links switch languages without cookies, session storage,
  browser-language detection or client-side redirects.
- Each path has its own fully rendered HTML title, meta description, Open Graph
  locale/title/description/image, Twitter card and image-alt text, plus
  \`canonical\` and \`hreflang\` alternates. WhatsApp and other crawlers can
  read these without JavaScript. The images use absolute
  \`https://tag.rocsi.eu/og/{ro,en}.png\` URLs.
- Type enums (\`VALID\`, \`INVALID\`, \`A0_SYNTHETIC\`, experimental boundary
  markers) remain evidence-backed immutable values. Romanian translates UI
  labels and display statuses, but never changes underlying JSON, policy
  predicates or cryptographic results.
- The social graphics and drone/radar site icon are **original synthetic art**
  authored for this project with \`showcase/render_social_assets.py\` (Pillow
  needed only for optional artist-side re-rendering). Cloudflare's
  \`python3 showcase/build.py --out-dir dist\` has no Pillow or external build
  dependency. No stock, vendor, participant or operational imagery is used.
- Social platforms may cache previews. A changed picture becomes visible only
  after a separately approved deployment and may need platform cache refresh.
  \`noindex\` is kept deliberately; link-sharing metadata is not SEO approval.

## Minimal acceptance and release gate

Desktop and mobile (320px, 375px, and standard desktop width): no
horizontal overflow/overlap; visible experimental markings; scenario selector
and recorded typed outcomes usable by mouse, keyboard and touch; the distinct
precomputed genuine verifier panel visible; no mislabeled live progress.
Test representative browsers without claiming untested engine compatibility.

For the public showcase, both SVG/CSS animations start automatically. Check
the mission scene with the default pass scenario selected: the mission-craft
element should use mission-cinema-pass, with four animated rotor groups.
Changing the selector to hold or return restarts the corresponding synthetic
animation without clicking another control. No mission or technical-animation
playback buttons should be rendered. The technical diagram continuously cycles
through the three conceptual stages while visible; it is never evidence.

For accessibility, both SVG animations pause outside the viewport or
when the tab is hidden. With prefers-reduced-motion: reduce, their CSS
animation names must be none, while labels and evidence remain readable.
On narrow screens verify that the technical diagram scrolls horizontally
inside its own container, without page-level horizontal overflow. Chromium
QA must also check absence of console exceptions and independent JSON evidence
loading. These are acceptance procedures, not Production attestations.

Pre-launch **GO** requires: focused CI PASS on exact PR HEAD; code review and
no new material findings; desktop/mobile + automatic scenario-switch/reduced-motion
acceptance; a manual inspection of emitted assets and public source/network
for absent operator execution; approved hosting, TLS, response headers and
DNS configuration; explicit owner approval for **merge** and a separate
approval for **public activation**. Default: **NO-GO** for merging or deploying this localization PR.

Rollback: disable the Pages custom domain/route or revert the static
deployment via the authorized hosting controls. Offline independent verification
and the original local console remain unaffected.
