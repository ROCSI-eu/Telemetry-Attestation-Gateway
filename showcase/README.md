# TAG Mission Control — static public showcase (#89)

> **EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION**

**Static package:** this directory builds a separate, precomputed, static technology
showcase from the already existing Mission Control console (#87). The current
Romanian-first bilingual baseline is hosted on Cloudflare Pages at tag.rocsi.eu.
A Draft PR does not authorize publication. The owner confirmed on 23 November
2026 that GitHub `main` merges automatically deploy to Cloudflare Pages Production.
Treat that as the expected consequence of an explicitly approved merge, not a
reason to recheck Cloudflare dashboard settings. Verify the served SHA afterward;
It is not a validated product, live verifier or customer workflow. Issue #88
remains independent of serving immutable static assets.

## PUBLIC-RESEARCH-MODULE-01 — QA candidate

The main RO/EN overview remains a short static presentation. The dedicated
research routes /ro/research/ and /en/research/ render the validated cumulative
journal, newest first, with technical evidence references and limitations.
Three native HTML disclosure examples use allowlisted deterministic mock
outcomes. A separately labelled offline cryptographic result is pre-recorded
and not authenticated or verified by the browser. No JavaScript, live verifier,
JSON endpoint, upload, operator action or network API is published.

The build emits exactly 15 static assets (13 baseline + two research pages).
The CSP permits only the two known inline stylesheet hashes, no scripts or
connections; both language pairs share their respective stylesheet. Historical
evidence-results.json and authentic-evidence.json remain source-only and are
removed from reused output directories. The prior custom-domain stale-cache
incident requires separately authorized targeted URL purge and HTTP 404 checks;
this QA candidate does not perform that action. No deployment is authorized.

The historical notes below describe superseded presentation implementations.

## TAG-VISUAL-REFRESH-01 — public presentation layer

The visual refresh changes the **static public showcase only**, without changing
the shared local console, CLI, verifier, scenario fixtures or browser scripts.
The visitor-facing editorial sequence is **Hero → The Concept → How It Works →
Potential Applications → The Research**, in RO and EN. The proof-stage illustration
is kept alongside the synthetic mission scene; detailed tools, laboratory scenario
replays and limitations are contained in expandable technical panels under Research.
Mock orchestration, the separately recorded offline-verifier replay and the
now verified synthetic SITL→ZKP GitHub Actions experiment remain explicitly distinct.
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

**Code-only Draft PR**: neither opening a Draft nor passing QA authorizes
merging or the automatic Production effect. Require explicit merge approval
that covers the existing GitHub `main` → Cloudflare Pages deployment. Reuse
that accepted checkpoint rather than demanding another dashboard/Preview/
rollback inventory for ordinary content updates without contradictory evidence.

### Focused acceptance

Build the same 15 files using python3 showcase/build.py --out-dir LOCAL_QA_PATH.
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

## Research journal: accepted laboratory progress only

The public research section reads `showcase/research_journal.json` **at build time**.
It contains a limited, bilingual set of documented synthetic laboratory results,
their plain-language takeaway and a repository evidence path, plus a separate
unresolved research question. It does not ingest GitHub activity, execute experiments,
or publish live/runtime telemetry.

When a relevant laboratory finding has been verified and accepted for public
presentation, update this file in **the same PR** as the corresponding research
change. Write Romanian and English copy, report what was actually observed,
state the limitation, and point `evidence_path` to the existing source in
`experiments/`. Do not publish routine refactors, unfinished experiments,
unverified claims or real/sensitive data. No invented dates or percentage
progress. Review the wording and evidence before merge.

An explicitly approved merge to `main` triggers the owner-confirmed automatic
Cloudflare Pages Production build, embedding updated entries into dedicated RO/EN research HTML;
there is no CMS, external fetch, browser scripting or extra
deployment step. The strict schema/evidence-path check fails closed on invalid
input. A commit that does not update the journal cannot magically create
an entry, even when it deploys successfully.

## Build and scope

From the repository root:

\`\`\`sh
python3 showcase/build.py --out-dir /tmp/tag-showcase
python3 -m unittest discover -s showcase -p 'test_*.py' -v
\`\`\`

Use a local static HTTP server in an authorized isolated QA environment to
inspect the generated **15 files** (the existing 13 plus two research pages). The allowlisted package is:

- \`ro/index.html\`: Romanian-default public page (**Centru de comandă și control**);
  \`en/index.html\`: English page (**Mission Control**). Both use the same
  sanitized HTML/CSS/JS, without the operator card, authentication or execution.
- \`404.html\` and \`en/404.html\`: localized inert not-found pages with
  experimental markings and return links, preventing Pages' implicit SPA fallback.
- \`og/ro.png\`, \`og/en.png\`: pre-rendered 1200×630, same graphic composition
  (synthetic A–B–C route, illustrative quadcopter and data/rule/result stages), separately translated captions.
- \`favicon.svg\`, \`favicon.ico\`, \`apple-touch-icon.png\`: shared drone/radar
  site identity, without text or claims of live verification.
- ROCSI symbol asset (assets/rocsi-mark.svg): the unmodified current blue/tricolor
  mark from ROCSI-Website src/app/icon.svg at
  85c5f0eadaa15666817a27c940358146c8c479dd, rendered locally in the TAG
  header and ROCSI card. Distinct from TAG's browser favicon. It is ROCSI
  organization branding; its inclusion is not a grant of trademark rights.
- \`evidence-results.json\`: **strictly reconstructed** deterministic orchestration
  mock outcomes, never actual proof-verification evidence.
- \`authentic-evidence.json\`: **strictly reconstructed** precomputed synthetic
  offline-verifier result; the browser does not verify it or authenticate the JSON.
- \`_headers\`: static-host security headers including exact inline-content CSP hashes,
  no browser connections, denied frames/camera/geolocation, no tracking.
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
Reuse accepted hosting checkpoints until materially contradicted. On 23 November
2026 the owner confirmed GitHub `main` → Pages Production auto-deployment.
Preview controls, served deployment identity and rollback availability are
mutable, but a dashboard/API recheck is **not** a prerequisite for every
ordinary approved documentation merge. Reopen account-state checks only for
contradictory evidence, hosting/build/branch changes, a publication failure or
an actual separately authorized rollback. After merge verify the provider
check, served RO/EN revision, HTTP redirects and relevant `_headers`/assets.
Do not mistake provider SUCCESS for live publication or deploy manually again.

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
  \`https://tag.rocsi.eu/og/{ro,en}.png?v=20261121\` URLs, versioned to refresh social previews.
- Type enums (\`VALID\`, \`INVALID\`, \`A0_SYNTHETIC\`, experimental boundary
  markers) remain evidence-backed immutable values. Romanian translates UI
  labels and display statuses, but never changes underlying JSON, policy
  predicates or cryptographic results.
- The social graphics are original synthetic vector-style art rendered deterministically
  with \`node showcase/social_og_builder.mjs\` (Node used only for optional author-side re-rendering).
  The independent legacy favicon renderer remains \`showcase/render_social_assets.py\`
  (Pillow needed only when re-authoring icons). Cloudflare's
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


## TAG technical research presentation and release provenance (2026-11-20)

The public research chapter uses three concise, collapsed technical topics with
nested, optional raw diagnostics. The original scenario replay, offline-verifier
result and scope fields remain available inside those archives and in the
unchanged, precomputed JSON assets. No new live execution or network dependency
was added.

The **accepted research journal** remains `showcase/research_journal.json`,
validated at build time with checked-in evidence references. New public-safe,
owner-accepted results are added to that file **in the same reviewed PR** as
their source evidence, not inferred automatically from unrelated GitHub commits.
The compact scenario count and offline verification summary come from the
validated fixtures in the same build.

Cloudflare Pages injects `CF_PAGES_COMMIT_SHA` during an automatic build. The
static HTML shows that exact build revision as a GitHub commit link when set,
allowing comparisons with the newest GitHub source. Local offline builds without
this variable show a neutral explanation instead of inventing a SHA. A successful
GitHub merge or provider deployment check is **not** by itself proof that the
custom domain already serves the new HTML; confirm RO/EN acceptance separately.

## SITL-to-ZKP integrated synthetic evidence (22 November 2026)

GitHub Actions run #44995909866 at TAG PR #167 HEAD
`215d9ec5b6739f599f96d57ef311f64c0a97fa42` returned SUCCESS for a
single bounded synthetic ArduPilot Copter 4.7.1 SITL -> two receive-only
MAVLink2 observations -> TAG normalization -> real Noir/Barretenberg proof
-> separately invoked verifier VALID. The run reports `UNSIGNED` source,
`DISABLED` publication, `NONE` command path and successful cleanup.

This update records the accepted finding in the RO/EN research journal, the
technical evidence panel and limits. The public HTML remains a static
presentation: its mock replays and earlier offline-only evidence are not the
2026-11-22 integrated execution. See the historical execution evidence at
`https://github.com/ROCSI-eu/Telemetry-Attestation-Gateway/actions/runs/44995909866`.
A valid synthetic proof does not authenticate telemetry, establish trusted
timing or cover a whole flight. No production/operational use is authorized.
