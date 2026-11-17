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

## Build and scope

From the repository root:

\`\`\`sh
python3 showcase/build.py --out-dir /tmp/tag-showcase
python3 -m unittest discover -s showcase -p 'test_*.py' -v
\`\`\`

Use a local static HTTP server in an authorized isolated QA environment to
inspect the generated **14 files** (13 existing assets plus one Pages redirect configuration). The allowlisted package is:

- \`index.html\`: Romanian-default public page (**Centru de comandă și control**);
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
- \`_redirects\`: Cloudflare Pages rule \`/ro/ / 301\` permanently redirects
  the optional Romanian alias to canonical \`/\` without duplicating its HTML.
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

- \`/\` uses **Romanian** (\`<html lang="ro">\`); \`/en/\` uses English
  (\`lang="en"\`). Native RO/EN links allow an explicit change of language.
  No cookies, session storage, browser-language detection or redirect logic.
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

For Pause/Resume, first ensure **reduced motion is off** and the tab is visible.
Use the control to pause, then check \`aria-pressed=true\`,
\`data-motion=paused\`, CSS animation \`playState=paused\`, and frozen
SVG transform **after allowing animation and style sampling to settle**.
An early transform sample can advance after the click even when pause
is correct; do not interpret one unsynchronized 240 ms comparison as a defect.
Paste this non-production diagnostic in the browser DevTools console:

\`\`\`js
(async () => {
  const root = document.querySelector("#mission-control");
  const craft = root.querySelector(".mission-craft");
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) {
    return {mode: "reduced-motion", stationary: getComputedStyle(craft).animationName === "none"};
  }
  if (root.dataset.motion !== "paused") document.querySelector("#mission-motion-toggle").click();
  const settle = () => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
  await settle();
  const state = craft.getAnimations().map(a => a.playState);
  const first = getComputedStyle(craft).transform;
  await new Promise(resolve => setTimeout(resolve, 320));
  await settle();
  const second = getComputedStyle(craft).transform;
  return {pressed: document.querySelector("#mission-motion-toggle").getAttribute("aria-pressed"),
          visibility: root.dataset.visibility, state, frozen: first === second};
})()
\`\`\`

Expected: pressed \`"true"\`, visibility \`"visible"\`, animation
state \`["paused"]\` and frozen \`true\`. Then click Resume and confirm
\`aria-pressed=false\` and animation \`running\`. In reduced-motion mode,
the vehicle is stationary, and the toggle is disabled. On hidden tab, the
animation must pause. This is a **manual acceptance instruction**, not a
claim that any of those browser checks ran in this PR.

Pre-launch **GO** requires: focused CI PASS on exact PR HEAD; code review and
no new material findings; desktop/mobile + Pause/Resume/reduced-motion
acceptance; a manual inspection of emitted assets and public source/network
for absent operator execution; approved hosting, TLS, response headers and
DNS configuration; explicit owner approval for **merge** and a separate
approval for **public activation**. Default: **NO-GO** for merging or deploying this localization PR.

Rollback: disable the Pages custom domain/route or revert the static
deployment via the authorized hosting controls. Offline independent verification
and the original local console remain unaffected.
