# Local web console preview v0

> **EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION**

**Status:** experimental local UI increment for #87, not public hosting or an accepted product/operator console.

This is a static, dependency-free, responsive **local** browser presentation of two separately labeled sources: (1) deterministic orchestration **mock** evidence from `../integrated-cli-v0/evidence-results.json` and (2) a precomputed genuine synthetic verifier replay in `authentic-evidence.json`, exported after an isolated, pinned Noir/Barretenberg verifier run. **The browser does not verify cryptographic proofs and cannot independently authenticate a JSON replay.** The mock source is never promoted into the authentic source. No background jobs, live MAVLink, browser-to-Qube/MCP connection, raw telemetry, witness material, keys, private speed or persistent browser storage.

## Run locally

From the repository root:

```sh
python3 -m http.server 8765 --bind 127.0.0.1 --directory experiments
```

In the **same machine's browser**, open:

`http://127.0.0.1:8765/web-console-v0/`

The browser fetches only the two fixed, separately versioned, minimized files `../integrated-cli-v0/evidence-results.json` (mock) and `authentic-evidence.json` (precomputed authentic local verification result) from the same loopback server. **Do not bind a public interface, expose the server through a tunnel/proxy or deploy this page to a public hostname.** Stop the temporary server when the inspection ends. There is no independent live backend or proof-generation endpoint in this increment.

## Visible evidence-scope explanation (experimental)

**EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION**

The existing static console now places a two-column (single-column on narrow screens), always-visible explanation before the result panels. It distinguishes the historical, precomputed genuine synthetic verifier outcome from mock orchestration and states explicitly that unauthenticated JSON replay is not browser proof verification. The adjacent non-claims cover telemetry/source truth, time, coverage, safety, compliance, independent policy/freshness/revocation/replay decisions, publication and relying-party acceptance. No evidence shape, verifier, runtime, network behavior, browser storage or dependency has changed. This is a presentation-only increment for local exploration under #87, with potential reuse for the **Proposed** #89 showcase; it does not authorize public activation. Structural tests check the explanation's static visibility, location and narrow-viewport CSS. Browser/assistive-technology acceptance remains separate and unverified for this increment.

## UI scope

- Choose and replay pre-recorded synthetic orchestration cases without executing them.
- See typed source, predicate, proof-generation, verification-input and cryptographic states.
- Keep publication state, source assurance and relying-party decision separate.
- Mark stages according to the recorded case and explicitly disclose when proof generation was only mocked.
- Avoid animation that implies a live run. Use responsive CSS, native keyboard/touch controls and reduced-motion-safe behavior.
- Fail closed with a visible error if the expected labeled evidence is missing or incompatible.

This UI deliberately does not expose exact normalized speed, raw telemetry, coordinates, identities, witness material, proof bytes, verification keys, proof hashes, credentials, hidden correlation data or a MAVLink command path. The precomputed replay contains no proof/verification key and thus is not independently verifiable from the browser. It was derived from a genuine synthetic test package on Qube, checked with a separately invoked pinned verifier offline (2026-11-14). It does **not** claim proof generation observation, source truth, time, interval coverage, safety, compliance, or commercial validation.

## Next increments (Proposed)

1. The separately versioned precomputed genuine synthetic verifier replay is now included locally. It is a presentation of an independently checked outcome, not a live run, signed attestation, browser-verifiable proof, or production service.
2. Design a narrow allowlisted local runner/status interface for authenticated, bounded operator-triggered synthetic jobs without shipping witnesses to the browser.
3. Chromium/Firefox local browser smoke tests have now been run (details below); WebKit, real mobile hardware, assistive technology and comprehensive accessibility/performance evaluation remain Open before broader platform claims.
4. Keep any public static showcase at `tag.rocsi.eu` governed by #89. Live proving, Production/shared-VM execution and public routing are not authorized by this file.

Proof validity is not telemetry truth. This project is observational only; no flight control or MAVLink command generation/forwarding is permitted.

## Reproduce the minimized authentic synthetic replay

> **EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION**

Use only the pinned local Noir/Barretenberg binaries and pre-provisioned public CRS described in the [Qube reproduction procedure](../bounded-speed-proof-v0/qube-offline-reproduction.md). Run the exporter in the same local network-disabled test environment as the independent verifier. This command takes an already-generated test-only package and writes only an allowlisted result (not the witness, proof, key or public claim limit). It never runs proof generation or makes network requests:

```text
python3 experiments/web-console-v0/export_authentic.py --package-dir /private/test-only/proof-package --output /private/empty-directory/authentic-evidence.json
```

The output fails closed unless the **independently executed** verifier reports cryptographic VALID or INVALID for an accepted test package; metadata or a manifest-only status cannot authorize the export. The local replay has `verification_basis: INDEPENDENT_OFFLINE_CHECK_AT_EXPORT` and `browser_verified: false`: these are truthful process labels, **not cryptographic authentication of the exported JSON**. This limitation remains Open before anyone may treat a public-facing replay as externally verifiable proof evidence.

The checked-in `authentic-evidence.json` is a single precomputed, strictly minimized A0_SYNTHETIC positive outcome from the isolated Qube proof/check. It is **not** a customer, hardware, market, compliance or production artifact, and is separate from the mock-only integrated CLI fixture. Never commit or serve the source proof package, witness, any private exact telemetry, public proof artifacts, verification key, raw CLI result, paths, identifiers, nonces, salts or correlated data. A new export should be reviewed against the exact privacy allowlist before use.

Offline checks: `python3 experiments/web-console-v0/test_authentic_console.py`, `python3 scripts/check_experiments.py`, `python3 scripts/check_docs.py`. Missing, extra-field, wrong-version, or unverifiable replay must close only the authentic panel, never masquerade as mock evidence. No public deployment, Qube-to-browser live API, or Production integration is authorized.

## Private offline CLI-to-console session refresh (experimental)

> **EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION**

The stand-alone `refresh_local_console.py` builds a private **copy** of the two static console inputs and the HTML into a destination **outside the Git repository and proof package**. No JSON editing is required. The tool must run on the same authorized, isolated machine that holds the **demonstrably synthetic, test-only** proof package, the locally pinned verifier, and already provisioned public CRS. Keep network egress disabled when invoking the verifier. Example using abstract, private absolute paths:

```text
python3 experiments/web-console-v0/refresh_local_console.py --package-dir /private/test-only/proof-package --session-dir /private/temporary/console-session
```

The session directory must initially **not exist**. Its parent must exist. The new session is created with mode `0700` and contains only `web-console-v0/index.html`, `web-console-v0/authentic-evidence.json`, and `integrated-cli-v0/evidence-results.json`, each mode `0600`. There are **no** private proof artifacts, witnesses, verification keys, command paths, identities or exact values in the session. The CLI neither downloads binaries nor runs a prover or local HTTP service.

For a **later** synthetic experiment, repeat the same command with the same `--session-dir` and the new allowed `--package-dir`. The independent verifier must return a typed `VALID` or `INVALID` result first. Only the minimized authentic JSON is then **atomically replaced**, with no manual editing, while the mock record and HTML stay unchanged. Verification failures, extra/altered session files, unsafe permissions or symlinks **fail closed** and preserve the previous session. This does not authenticate the JSON for external consumers.

To inspect it, start an **optional temporary loopback-only static server** from the session directory (not from the repository or proof directory):

```text
python3 -m http.server 8765 --bind 127.0.0.1 --directory /private/temporary/console-session
```

Open `http://127.0.0.1:8765/web-console-v0/` in a browser **on the same machine**. After another CLI refresh, reload the page to read the newly precomputed synthetic result. Stop the temporary server when finished. **Never** bind non-loopback interfaces, expose the session via a proxy/tunnel, or point the server at the proof/CRS/test-input directory. The CLI does not offer web-triggered verification, server-side jobs, scheduled execution, HTTP endpoints, or live streaming; those would require separate evidence and authorization.

The session is disposable; deletion of its private directory after inspection is a local cleanup action. The checked-in `authentic-evidence.json` is a historical research fixture and is **not rewritten** by this CLI. It cannot verify telemetry truth, real assurance, fresh source information, interval coverage, replay resistance, customer demand, safety, regulatory compliance or production readiness. `browser_verified` remains false; `A0_SYNTHETIC` remains the only demonstrator tier.

## Local browser QA checkpoint — 2026-11-14

> **EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION**

The local preview was tested using an **ephemeral loopback-only** HTTP server on Qube, Chrome/Chromium 157 and Firefox 157 headless, with test-only evidence and disposable browser profiles. No hosted site, participant data, real telemetry or production system was accessed. Findings:

- Chromium: viewport sizes **1366, 768, 390 and 320 CSS px**, all loaded the separately labeled precomputed `VALID` result with unchanged mock scenario controls. At 320 px before this change, the long unbroken authentic evidence-kind token caused **368–384 px** effective/scrollable layout width and mobile horizontal overflow. The narrow-viewport CSS wrapping/grid-minimum fix restored **320 px document and layout width** in both desktop-width simulation and mobile viewport emulation.
- Firefox headless: **1366 and 768 CSS px** passed without horizontal overflow, including precomputed `VALID`, mock controls, missing/extra-field fail-closed responses, `INVALID` outcome and keyboard Tab focus on the scenario selector. The Firefox WebDriver session did not permit a window narrower than **500 px**; its attempted 390/320 tests are **not evidence** of Firefox mobile compatibility.
- Chromium: `INVALID` remains a distinct authentic result, and extra-field/missing authentic JSON fails closed only the authentic panel; the mock selector remains usable. Basic keyboard Tab focus reaches the selector.
- Browser reload after a **test-only synthetic CLI refresh** was separately exercised on both Chromium and Firefox: after writing a minimized `VALID` record, the local CLI was invoked again with a **mocked verifier outcome** `INVALID`; a page reload displayed the new authentic-typed result while the independent mock selector remained functional. The real pinned offline cryptographic verifier was exercised separately in the preceding CLI increment; these browser checks do **not** count as new real-proof verification evidence.
- The browser **does not verify or authenticate** proof material. These smoke tests are not WCAG certification, real phone testing, screen-reader testing, accessibility audits, performance benchmarks or evidence of cross-platform production readiness. WebKit and real mobile hardware remain untested.

The actual CLI refresh, strict privacy allowlist, `A0_SYNTHETIC` and independent offline verifier boundaries are unchanged by this CSS-only fix.

## One-command disposable Qube preview (experimental)

> **EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION**

`run_private_preview.py` is a **small orchestrator**, not another prover, verifier, network service or persistent deployment. It consumes a **previously generated demonstrably synthetic proof package** (created only with the existing pinned offline Noir/Barretenberg workflow and synthetic private inputs). It invokes the **existing** `refresh_local_console.py` and its independent verifier inside `bwrap --unshare-net` with a read-only filesystem except for one private ephemeral directory. No additional dependencies beyond Python, `bwrap` and the already provisioned pinned verifier/CRS are introduced. On success it starts a temporary **loopback-only, allowlisted static** view of the minimized copy, with a bounded lifespan; at timeout it closes the listener and deletes its own private session. The source package, public CRS and repository are read-only and never served.

The session parent defaults to an already-existing Qube runtime directory: `XDG_RUNTIME_DIR` if set, otherwise `/run/user/<uid>`. It is **not created automatically**. The existing strict checks require an absolute owner-owned `0700` directory, no symlink components, and no overlap with Git or the proof package. An unsafe configured `XDG_RUNTIME_DIR` fails closed rather than silently falling back to `/tmp` or another path. To use a different existing private directory, pass `--private-parent`. No restricted customer material may be present. Example from the Qube checkout, with an abstract synthetic package path:

```text
python3 experiments/web-console-v0/run_private_preview.py --package-dir /private/test-only/proof-package --seconds 60
```

For a non-default private parent, add `--private-parent /private/disposable-tag-sessions`; the user must prepare that directory with `0700` permissions. Open the printed `http://127.0.0.1:<ephemeral-port>/web-console-v0/` **on the same Qube machine** before the preview expires. Before opening HTTP, the server checks the entire private session against the existing strict CLI contract and freezes only the three allowlisted, minimized/static assets into an immutable in-memory snapshot. Requests never re-open mutable session files, including after a same-user process modifies a file. The server only permits the HTML, mock JSON and minimized authentic JSON paths and rejects directory listings and any other path. No tunnel, external proxy, fixed public port, browser-triggered proof, command endpoint, remote API or hosted URL is authorized. The preview lifetime must be **1–300 seconds**; `--no-serve` verifies and constructs then immediately deletes a private session without opening a port. The Qube runner requires a root-owned, non-group/world-writable **`/usr/bin/bwrap`**, not an arbitrary executable found earlier in `PATH`. A successful child exit without an independently verified, structurally valid private session is rejected.

For an invalid-but-well-formed **synthetic** proof, the reused independent verifier may return `INVALID / PROOF_REJECTED`; the minimized browser replay preserves that dimension separately from mock. Invalid packages, unavailable verification material, path/permission errors and verifier failures fail closed. A failed run leaves no created preview directory, and never deletes the user-provided proof package or parent. After process termination the server is closed and only the temporary directory it created is removed; if interrupted forcefully (for example SIGKILL), a leftover directory may require explicit inspection and safe manual cleanup. Never automatically recursively delete an arbitrary user-provided path.

This wrapper makes **no claim to generate a new proof, observe telemetry, verify in the browser, prove source truth, provide a continuous interval, offer production-ready assurance, or validate a customer workflow**. Real witness generation stays within the existing separately documented private, offline proof workflow. `A0_SYNTHETIC` is the only demonstrator tier.

Run the offline-default checks through `python3 scripts/check_experiments.py`, plus `python3 scripts/check_docs.py`.
