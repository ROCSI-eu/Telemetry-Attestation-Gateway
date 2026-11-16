# TAG Mission Control — static public showcase (#89)

> **EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION**

**Code-only static package:** this directory builds a separate, precomputed, static technology
showcase from the already existing Mission Control console (#87). It is not a
deployed website, validated product, live verifier, customer workflow, or permission
to activate tag.rocsi.eu. Issue #88 remains open and is not a dependency for
serving immutable static assets on separately authorized hosting.

## Build and scope

From the repository root:

\`\`\`sh
python3 showcase/build.py --out-dir /tmp/tag-showcase
python3 -m unittest discover -s showcase -p 'test_*.py' -v
\`\`\`

Use a local static HTTP server to inspect the generated *six-file directory*
in a separately permitted development environment (do not use Qube/Production
without authorization). The package is:

- \`index.html\`: transformed shared Mission Control HTML/CSS/SVG/JS; operator
  card, local capabilities discovery, authentication/token and execution JS removed.
- \`404.html\`: static inert not-found page with experimental labels and a return
  link; prevents Cloudflare Pages' implicit SPA fallback on unknown routes.
- \`evidence-results.json\`: **strictly reconstructed** deterministic orchestration
  mock outcomes, never actual proof-verification evidence.
- \`authentic-evidence.json\`: **strictly reconstructed** precomputed synthetic
  offline-verifier result; the browser does not verify it or authenticate the JSON.
- \`_headers\`: static-host security headers including exact inline-content CSP hashes,
  same-origin-only JSON fetches, denied frames/camera/geolocation, no tracking.
- \`robots.txt\`: explicit no-index preference for this initial experimental release.

Build fails closed if an input fixture schema, allowlisted typed value, privacy
boundary, HTML exclusion marker or expected public-script shape changes.
No proof, witness, private speed, coordinates, credentials, restricted source
identity, CLI runner, operator endpoint, POST route, analytics, or remote fetch
is shipped. The checked-in source console and its loopback operator are unchanged
and remain local-only.

## Hosting comparison and recommendation (not activation)

**Preferred:** Cloudflare Pages/static edge hosting with a new isolated project.
Build command: \`python3 showcase/build.py --out-dir dist\`.
Build output: \`dist\`; framework preset: none; no runtime functions,
environment secrets, analytics or SSR. Connect the Git repository under the
existing organization's authorized Cloudflare account, configure *only* the
approved custom hostname after a separate GO. Confirm that Pages applies
\`_headers\` on the final deployment, returns HTTP 404 for missing routes, and that its public route serves only
the six generated files. Keep previews restricted as appropriate: a public
preview URL is itself a public exposure and needs authorization.

**Alternative:** existing ROCSI Production VM served as pure static content.
This would add web-server/domain configuration, disk and operational coupling
to unrelated production sites for no technical gain. Do not use it for the
first showcase without a separate shared-host assessment and approval.

**Fallback:** a separate static-only host may be used if equivalent CSP and
no-index headers, isolation, DNS/TLS and rollback are confirmed. No public prover
is needed under any of these options.

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
approval for **public activation**. Default: **NO-GO** for hostname activation.

Rollback: disable the Pages custom domain/route or revert the static
deployment via the authorized hosting controls. Offline independent verification
and the original local console remain unaffected.
