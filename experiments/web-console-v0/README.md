# Local web console preview v0

> **EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION**

**Status:** experimental local UI increment for #87, not public hosting or an accepted product/operator console.

This is a dependency-free, responsive **local** browser presentation of two separately labeled recorded sources: (1) deterministic orchestration **mock** evidence from `../integrated-cli-v0/evidence-results.json` and (2) a precomputed genuine synthetic verifier replay in `authentic-evidence.json`, exported after an isolated, pinned Noir/Barretenberg verifier run. **The browser does not verify cryptographic proofs and cannot independently authenticate a JSON replay.** The mock source is never promoted into the authentic source. No background jobs, live MAVLink, browser-to-Qube/MCP connection, raw telemetry, witness material, keys, private speed or persistent browser storage.

## Mission Control visual scene (#87, Proposed, code-only)

> **EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION**

The existing shared HTML console starts with an observational **Mission Control** scene: a lightweight inline SVG, an abstract predefined route (waypoints A/B/C) and a stylized 2.5D vehicle. **All motion is illustrative**. The route has screen-space geometry only, no location, speed, real-world vehicle identity, live telemetry, flight coverage or validated movement. Animation does not correspond to a backend stage, proof, source truth or mission status. The scene has a manual Pause/Resume illustration control, pauses automatically when its document is hidden and becomes stationary under the reduced-motion browser preference. No WebGL, external library, font, map, network source, client storage, timer, new API or command channel is introduced.

The neighboring **Backend truth** panel begins at NOT_OBSERVED. Static mock case selection and the separate offline-verifier replay **never** update it. While the already-existing authenticated one-shot CLI request is in flight, it explicitly states that no stage progress is confirmed. Only the existing strict operatorResultAllowed check of a **complete, minimized, final typed CLI response** can populate observed proof-generation and cryptographic fields; incompatible/unavailable responses reset them to NOT_OBSERVED. This is **not live streaming** or continuous mission observation. Independent evidence panels remain unchanged; cryptographic validity is not telemetry truth, policy approval, publication, source assurance or a relying-party decision.

This increment is source-only; focused offline structural checks in test_console.py cover the illustration/evidence boundary, reduced motion, visibility pausing, no new command path or storage, and final-result validation ordering. The existing bridge serves the same HTML with no extra allowlisted route. Browser-engine compatibility, runtime frame rate, and cross-device performance are **not yet measured** and must not be claimed. The local/Qube runtime readiness work stays separately Open in issue #88. No Ready, merge, deployment, public host or hardware authorization is implied.

## Unified active local console (experimental one-shot operator mode)

> **EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION**

`local_cli_bridge.py` now serves the **same** existing `index.html` as the static console, not a parallel miniature page. A strictly allowlisted, same-origin `/operator-capabilities` GET activates an extra operator section only when the loopback bridge is present. Static/disposable previews retain their two independent recorded panels and hide the operator control. The bridge serves only the shared HTML, the two existing minimized synthetic fixtures, and the capability response, plus its authenticated one-shot POST; it never serves a proof package or private workspace. The available synthetic CLI presets are `over_limit` and `malformed_source` (both stop before proof) and conditional `verified_synthetic` (real synthetic proof and independent offline verification only with the preprovisioned pinned toolchain). No browser proof, client-side verifier, SSE, WebSocket, progress stream, live telemetry, public publication, background job or persisted operator run exists. During the HTTP call the UI reports only **request in flight**, not fabricated pipeline stages. After a final typed and allowlisted response, it shows source, proof, cryptography and publication with independent policy, freshness, revocation, replay, assurance and relying-party decision dimensions. An incompatible/unavailable response hides the prior result and fails closed; the one-shot button never permits retry within the same preview.

Run on the **same isolated local machine** that hosts the browser, after confirming the root-owned `/usr/bin/bwrap` is available. From the repository root:

```text
python3 experiments/web-console-v0/local_cli_bridge.py --seconds 120
```

Open the loopback URL printed in the local terminal and paste the one-session operator token from that same terminal into the password input in the **Local operator** card. Select a pinned scenario and click the one-shot execution button. The token is never placed in the URL or persistent browser storage. The UI sends it only as a same-origin request header. **Do not copy this token into Git, screenshots, logs, chat transcripts or other shared material.** There is no background service, remote tunnel, VM proxy, scheduled task or browser command-line argument. The preview ends within 1–300 seconds; restart it for another demonstration.

The server rejects non-loopback binding (it always binds `127.0.0.1` on an ephemeral port), unexpected routes, foreign/missing Origin, unexpected Host, missing/wrong token, malformed input, arbitrary scenario names, oversized JSON and retries. Only one syntactically valid request is consumed; there is no queue or replay history. The server keeps no CLI stdout/stderr or proof material and suppresses access logs. It launches only the hardcoded `cli.py` command inside trusted `bwrap --unshare-net`, with a minimal sandbox root: read-only `/usr`, the experimental source tree, the two required system loader symlinks, isolated `/tmp`, minimal `/dev` and `/proc`. Host `/`, `/home`, `/etc`, the complete `/dev` tree, and unrelated private data directories are not mounted. The CLI subprocess has a 20-second wall timeout, CPU/memory/file-size limits, a bounded 16 KiB stdout pipe reader that kills the process group on overflow or timeout, and no forwarded stderr. HTTP input has a 3-second **absolute wall-clock deadline covering both request headers and body**, in addition to per-socket read timeouts; a watchdog interrupts reading even if a peer continues to drip bytes. Incomplete or late input is rejected without consuming the one-shot allowance. Tests verify that continuous slow-drip headers or body cannot hold the single-threaded server or prevent subsequent requests. An unavailable sandbox or unexpected CLI result fails closed. The response is **reconstructed** from a fixed set of typed, minimized fields, never copied wholesale from the CLI. Restricted telemetry, normalized speed, witnesses, proof bytes, verification keys, identities, command paths and correlation identifiers are never returned.

This is a **local, one-shot active operator demonstration**, **not** a streaming monitor: the conditional genuine synthetic preset can invoke the already-supported local prover and independent offline verifier; short-circuit presets do not. It does not stream intermediate progress, persist runs, authenticate a remote user, or attach to Qube/MCP from another machine. It does not validate telemetry truth, source assurance, time, interval coverage, compliance, publication or relying-party decisions. The existing precomputed genuine verification panel is distinct and unchanged; it must not be confused with the active CLI result. Any later expansion to prover-triggering, longer-lived status tracking, cross-machine access or public `tag.rocsi.eu` requires a separate reviewed gate and threat analysis.

Run regression checks with `python3 experiments/web-console-v0/test_local_cli_bridge.py` and the standard offline `python3 scripts/check_experiments.py`, `python3 scripts/check_docs.py`.

## Conditional genuine synthetic proof through the local CLI (Proposed, offline-only)

> **EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION**

The same one-shot local operator bridge now offers a third **predefined** option, `verified_synthetic`. Unlike the two earlier short-circuit scenarios, this option invokes the existing integrated CLI with the checked-in, demonstrably synthetic `unsigned-consistent` capture, public maximum `600 cm/s`, publication **disabled** and normal verification case. The existing Noir/Barretenberg prover generates a real **synthetic** proof; the separately implemented verifier module reconstructs canonical public inputs from the public CBOR artifact, then checks the proof offline without accepting a witness argument. This is not separate-process verifier isolation; that is a later reviewable boundary. The CLI's disposable workspace holds the synthetic witness and proof and is removed when the subprocess finishes; neither enters the browser response.

The operator must **explicitly** provide `--offline-toolchain-root /ABSOLUTE/PRIVATE/TOOLCHAIN` when starting `local_cli_bridge.py`. The root must exist, be owned by the invoking user, have mode `0700`, and contain `bin/nargo`, `bin/bb` and `cache/crs` under that root. Symlinked executables must resolve **inside** that private root. The integrated CLI checks pinned Nargo `1.0.0-beta.26` and Barretenberg `5.2.0` versions; its `bb` wrapper must use the **already provisioned** public CRS cache, never fetch anything. See [the Qube offline reproduction record](../bounded-speed-proof-v0/qube-offline-reproduction.md) for prior research-only provisioning evidence and explicit external-network prerequisites. **No installation, network download, CRS provisioning, fallback verifier or external connection is performed by this bridge.** An absent, untrusted or incompatible toolchain returns an `UNAVAILABLE` outcome and never `VALID`.

The sandbox remains loopback-only, one authenticated operator request per session, with `bwrap --unshare-net`, private `/tmp`, read-only experiment sources and read-only bind of only the explicitly supplied toolchain root. The real-proof execution has an explicit 90-second wall bound and retains the 12-second CPU, 1 MiB FSIZE, and 16 KiB bounded stdout caps. Its **finite RLIMIT_AS cap alone** is 2,560 MiB (2.5 GiB), selected as the lowest passing value among 1,280 / 1,536 / 1,792 / 2,048 / 2,560 MiB tested on Qube. Short-circuit scenarios remain at their original 1 GiB RLIMIT_AS and 20-second wall bound. This measured threshold is experimental, not a general upper bound or production sizing guarantee. Operator input never selects witness values, arbitrary fixture paths, commands, publication mode, network destination, or private data; the browser selects only the fixed scenario identifier.

The bridge **reconstructs** an allowlisted outcome and accepts `GENERATED / ACCEPTED / VALID` only when the real integrated CLI exits successfully with exact expected labels, schema, capture, claim, proof, assurance, unsigned source, non-evaluated independent dimensions, no disclosures, `publication=NOT_PERFORMED`, `command_path=NONE` and `relying_party_decision=NOT_MADE`. Failure, absence of the offline toolchain or any incompatible data **fails closed**. The browser never verifies or authenticates the recorded JSON response; it is not a portable independently authenticated receipt.

**Qube experimental observation (2026-11-14):** in an explicitly authorized temporary, checksum-verified research sandbox, the `verified_synthetic` loopback HTTP path completed real pinned Noir proving and the independently implemented offline verifier with typed `GENERATED / ACCEPTED / VALID`; the bridge returned only allowlisted metadata, denied a second invocation and performed cleanup. With the original 1 GiB `RLIMIT_AS`, `nargo compile` aborted (SIGABRT); the bounded proof-only profile at 2,560 MiB succeeded. The preprovisioned toolchain and public CRS were removed after testing and are **not** globally installed or provided by the default offline CI. This single observation does not constitute a security audit, telemetry truth, proof-system selection, continuous coverage, customer validation, or permission for deployment or public presentation.

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

## Explicit recorded-result reload (experimental)

> **EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION**

The authentic-evidence panel now includes **Reload recorded result**. After an authorized operator separately invokes `refresh_local_console.py` against an isolated synthetic package and the independent offline verifier, this button fetches the same allowlisted `authentic-evidence.json` again from the local session server without a full page reload. It disables during the request and hides previously displayed evidence before loading; malformed or unavailable input stays hidden with an error. No browser execution, remote proof job, authentication, polling, history, witness access or server-side API has been introduced. The mock scenario selection is unaffected.

**Important distinction:** `run_private_preview.py` intentionally freezes HTTP assets at startup. Its replay cannot change while that preview instance runs, so pressing reload there returns the same snapshot. To see a newly refreshed offline CLI record, use the separate static session server described above or restart a new authorized disposable preview. A live interactive CLI-controlled monitor still remains **Proposed** and requires a separately reviewed local operator boundary.

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

## Bounded local test package (#88, Proposed)

> **EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION**

**Question:** can the already integrated local CLI + web console be started, checked and stopped reproducibly as one disposable Linux test session without any shared-VM deployment, cryptographic reprovisioning, persistent operator state or public exposure?

**Proposed scope:** a standard-library, foreground-only wrapper `run_isolated_local.py` around the unchanged, previously tested `local_cli_bridge.py`. This is a **local/Qube research package only**, not an installable service or a readiness decision for a shared production VM. Startup is opt-in. The existing bridge still serves the allowlisted page and synthetic fixtures only on an OS-assigned `127.0.0.1` port; exactly one bearer-token-authenticated, pinned scenario can run. Both default short-circuit presets require no Noir/Barretenberg/CRS. Without an explicit toolchain root, `verified_synthetic` still fails closed. The optional `--offline-toolchain-root` selects **only an already provisioned, owner-private** Noir/Barretenberg/CRS research toolchain; the launcher validates it using the existing bridge check **before creating any session or listener**, then forwards it to the unchanged loopback bridge. This opt-in path neither installs dependencies nor runs a proof by itself. The prior genuinely verified synthetic replay remains **precomputed evidence**, not a fresh proof.

From a **clean, SHA-pinned checkout on the same non-production machine as the browser**, after confirming no conflicting browser/QA ownership and a non-root Linux account:

```sh
python3 experiments/web-console-v0/run_isolated_local.py --check-only
python3 experiments/web-console-v0/run_isolated_local.py --seconds 90

# Only when a separately provisioned, pinned private toolchain already exists:
python3 experiments/web-console-v0/run_isolated_local.py --check-only --offline-toolchain-root /PRIVATE/TOOLCHAIN
python3 experiments/web-console-v0/run_isolated_local.py --seconds 90 --offline-toolchain-root /PRIVATE/TOOLCHAIN
```

Use the printed local loopback URL and token only within that machine and short session. Do **not** copy the token to Git, screenshots, logs, chat or a public site. Do not use a tunnel, reverse proxy, shared VM or DNS. A Ctrl-C or TERM/HUP ends the owned bridge process group; a hard deadline also bounds a stuck session. The bridge itself enforces its 1–300 second listener lifetime, its no-retry token, `bwrap --unshare-net`, bounded CLI execution and output minimization. The wrapper does not execute a shell, download material, install software, launch browsers, start background services or log request content.

**Isolation and cleanup:** refuses root, symlinked/non-owner/group-or-world-writable runtime parent, runtime inside repository, or missing/untrusted root-owned `/usr/bin/bwrap` **before any listener exists**. Creates one owner-private `0700` temporary session directory under the invoking account's home (or an explicitly provided eligible `--runtime-parent`), supplies a minimal child environment without inherited credentials, uses private HOME/TMPDIR/cache, limits child open file descriptors and disables core dumps. The parent owns and waits for the foreground bridge process; exit, interrupt, or timeout removes this directory and sends TERM, then bounded KILL only to its own process group if necessary. Child proof workers, when used through the separately authorized bridge path, retain `bwrap --die-with-parent` and their own CPU/memory/time bounds. Abnormal power loss/SIGKILL cannot guarantee cleanup; check for stale owner-private directories and processes before any restart, **never remove another session without ownership evidence**.

**Local restart guard (Proposed):** before creating a session, the wrapper takes a nonblocking Linux advisory lock on the existing, owner-controlled runtime parent directory (no lockfile) and checks for any `tag-synthetic-*` entry there. Another launch using the same parent, or any potentially orphaned directory/file/symlink with that prefix, **fails closed before spawning the bridge**. Normal exit releases the lock and removes only the current temporary directory. After a crash/SIGKILL, inspect process ownership and the exact leftover privately before manually disposing of it; **no automatic stale-session deletion or takeover** occurs. This is a same-parent research-session guard, not a security boundary against malicious processes of the same user or a cross-host lease. It does not make the shared VM eligible.

**Read-only restart diagnosis (Proposed):** after PR #112's restart guard refuses a launch, run `python3 experiments/web-console-v0/run_isolated_local.py --inspect-only` (add `--runtime-parent /ABSOLUTE/OWNER-CONTROLLED/PARENT` only if the same parent was explicitly configured). This command does **not** require `bwrap`, launch a process, open a listener, inspect a private session's contents or remove anything. It prints only the experimental labels and one fixed status: `CLEAR` (exit 0), `LEASE_BUSY_OR_UNCERTAIN`, `RESERVED_ENTRIES_PRESENT`, or `UNAVAILABLE` (all exit 2). No paths, file names, PIDs, owners or tokens enter its output. A `CLEAR` result is a momentary lease/entry observation, **not** operational readiness; `LEASE_BUSY_OR_UNCERTAIN` does not establish that a session is healthy, and `RESERVED_ENTRIES_PRESENT` does not prove entries are safe to delete. Investigate exact ownership and active processes separately before any manual recovery; this command grants no cleanup authority.

**Optional local resource observation (Proposed):** For a later authorized **synthetic, local-only** foreground session, add `--report-resources` to the normal launch command. After the owned bridge process has exited or been stopped, the wrapper prints only the kernel-accounted **reaped-child user/system CPU time in milliseconds** and **maximum RSS in KiB of a single reaped child**. It is disabled by default, cannot be combined with `--check-only` or `--inspect-only`, and creates no output file, log, remote call or new process. If the OS accounting cannot be read, the output is only `UNAVAILABLE`; if an earlier reaped child already established a nonzero RSS watermark, RSS is `NOT_COMPARABLE`. These are opt-in diagnostic observations, **not aggregate peak concurrent memory, an entire process-tree resource peak, a disk-capacity threshold, a performance guarantee, production sizing, proof validity or deployment readiness**. No new resource observations have been collected as part of the source-only increment. Compare controlled positive/negative synthetic sessions on a separately authorized local test host before considering limits.

**Stop conditions / evidence boundary:** unexpected listening interface, failed guard, disk/memory pressure, interference with other processes, residual proof material, or any non-synthetic input ⇒ STOP, inspect read-only and clean only owned test resources. No background journal or persistence is configured. The wrapper does not enforce cgroups, dedicated service UID, global host disk thresholds, public binary/CRS provenance or hardware sizing. Those remain **Open** for issue #88 before any separate environment/deployment decision. Existing Qube proof/resource observations are not production capacity evidence, and the wrapper does not need or repeat proof provision. `python3 experiments/web-console-v0/test_run_isolated_local.py`, `python3 scripts/check_experiments.py` and `python3 scripts/check_docs.py` run offline without fetching proof tools.

**Status:** Proposed portable packaging increment; no shared-VM GO. MIT remains the Current project license; no license model change. No production configuration, systemd service, Docker, port routing, remote operator connection, customer data, external independent validation, safety/compliance claim or publication authority.

## #88 isolated Linux package — reproducibility and Qube acceptance (Proposed)

> **EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION**

**Artifact:** the already existing source checkout, `run_isolated_local.py`, `local_cli_bridge.py`, and the existing HTML/minimized synthetic fixtures; **not** another launcher, installer, proof package, Docker image, system service, or preconfigured host. Pin the checkout to an exact commit for each QA session (`git rev-parse HEAD`), require a clean working tree, and record that SHA in the private receipt. The observed Qube package below used `6fc48a66643bbbb8ad09082c736d169774ef77d6` (2026-11-18). A newer commit needs its own focused acceptance only if it changes this package.

**Offline dependencies:** an unprivileged Linux account, `python3` with standard-library modules, a trusted root-owned `/usr/bin/bwrap` supporting `--unshare-net`, and a private owner-controlled runtime parent **outside** the source checkout. On the observed x86_64 Qube: Python `3.14.4` and bubblewrap `0.11.1`. Do not silently install or change these tools. The default `over_limit` / `malformed_source` scenarios use **no** Noir, Barretenberg, CRS or ArduPilot. The optional unexecuted `verified_synthetic` scenario requires separately authorized and already checksum-pinned `nargo 1.0.0-beta.26`, `bb 5.2.0` and the pre-provisioned public CRS per the [offline reproduction checkpoint](../bounded-speed-proof-v0/qube-offline-reproduction.md); no proof tooling is bundled or downloaded.

**Same-machine, opt-in procedure:** using an existing owner-only `0700` parent outside the repository (never the shared VM, generic writable `/tmp`, or a production tree), run:

```sh
REPO=/absolute/path/to/pinned/Telemetry-Attestation-Gateway
PARENT=/absolute/path/to/owner-private-qa-runtime
git -C "$REPO" rev-parse HEAD
test -z "$(git -C "$REPO" status --porcelain)"
python3 "$REPO/experiments/web-console-v0/run_isolated_local.py" --runtime-parent "$PARENT" --inspect-only
python3 "$REPO/experiments/web-console-v0/run_isolated_local.py" --runtime-parent "$PARENT" --check-only
python3 "$REPO/experiments/web-console-v0/run_isolated_local.py" --runtime-parent "$PARENT" --seconds 30 --report-resources
```

Use the one-session URL and token only in that machine's local browser; never include the token in logs, screenshots, GitHub, receipts or remote diagnostics. The **existing** bridge offers the unchanged allowlisted `/`, `/operator-capabilities` and `/execute` endpoints: `GET /` and `GET /operator-capabilities` return 200, an unrecognized path returns 404, unauthenticated execution is refused, and only one permitted synthetic CLI execution is accepted. For the non-cryptographic package smoke test choose `over_limit`, which exits before proving; a second execution must be refused. Do not select `verified_synthetic` for this packaging QA. The HTTP bridge binds only an OS-assigned `127.0.0.1` port; the CLI child uses `bwrap --unshare-net` with a minimized read-only filesystem and disposable private `/tmp`. The HTTP bridge itself is **not** claimed to run in a network namespace. Do not expose or forward its loopback listener.

**Already enforced bounds:** the opt-in foreground preview accepts 1–300 seconds; the CLI short-circuit has a 20-second wall bound, 12-second CPU limit, 1 GiB address-space limit, 1 MiB file-size limit and 16 KiB stdout ceiling. The optional proof path (not exercised here) has a 90-second wall bound and 2,560 MiB address-space limit. The launcher sets an inherited 64-file-descriptor soft limit and zero core dumps. Child process groups are reaped and TERM then bounded KILL applies only to owned children. No persistent logs, service, timer, port allocation, credential store, proof, witness or capture is installed. Resource accounting is opt-in and reports **reaped-child** CPU and maximum single-child RSS only; it is not peak aggregate memory or sizing assurance.

**Qube Dev1 baseline, 2026-11-18 (non-Production):** at the exact source SHA above, the clean checkout occupied 2,880 KiB; before execution the dedicated QA volume had 107,880,120 KiB available and `MemAvailable` was 24,529,752 KiB. Focused existing unit tests: `test_run_isolated_local.py` 23/23 PASS, `test_local_cli_bridge.py` 20/20 PASS. A disposable real local session passed inspect/check-only, loopback HTML and CLI capabilities, route allowlist, token denial, single `over_limit` non-crypto execution, retry denial, explicit TERM stop, release of its listener and empty runtime-parent postflight. Observed reaped-child user/system CPU: 137/40 ms; maximum **single** reaped-child RSS: 26,448 KiB. These are one QA observation, **not** a guaranteed resource budget, full-tree peak or proof performance measurement. Neither SITL nor a prover was started. Token and private files were not retained as evidence.

**Focused whole-session resource QA, Qube Dev1, 2026-11-18:** at the merged #136 `main` SHA `5bb05f1e6eb6c99efbfb7aebb006f6806cda9645`, one disposable foreground session (`--seconds 25 --report-resources`) used only the existing `over_limit` synthetic short-circuit (no SITL, prover or verifier). An additional private, non-committed observer sampled the launcher **and its process descendants** through Linux `/proc` at a 10 ms target interval (143 samples). The observed peak was **4 concurrent processes**, **79,076 KiB summed RSS** (shared pages can be counted more than once), **43,823 KiB summed PSS**, and approximately **0.23 s of sampled cumulative process CPU**. There were 4 distinct observed PIDs; the owner-private runtime had a maximum of **0 regular files / 0 file bytes** and 2 directory entries including its parent. The bridge advertised/listened on an ephemeral `127.0.0.1` port; a `bwrap` child was observed in a network namespace different from the host. The HTML and capabilities GETs passed, exactly one authenticated `over_limit` CLI request succeeded and a replay was denied. Explicit TERM stopped the owned session; every observed owned PID exited, the port was released, no runtime entries remained, and `--inspect-only` returned `CLEAR`. These are finite, sampled **observations rather than hard limits**: short-lived peaks may be missed, and this zero-byte disk observation covers **only** the no-proof scenario. The original launcher's child-only resource observation (129 ms user, 55 ms system, maximum single reaped-child RSS 26,368 KiB) is **not** a substitute for whole-tree accounting.

**Operational readiness boundary:** the existing runtime enforces duration, a one-shot HTTP/token interface, a strict child stdout cap, child `RLIMIT_CPU`/`RLIMIT_AS`/`RLIMIT_FSIZE`, and process-group teardown. It **does not** hard-cap whole-tree RSS/PSS, cumulative CPU, process count, or total disk bytes via an isolated cgroup/quota. Qube exposes cgroup v2, but the tested process is under the Desktop Commander service's cgroup: **do not modify or adopt that shared service cgroup as a TAG quota**. No guaranteed minimum free-space requirement follows from this no-proof measurement, and no automatic process-tree capacity controller was introduced. For the current Qube-only short session, STOP if the preflight resource headroom is insufficient, any unexpected process or network listener appears, the network namespace guard fails, cleanup leaves residuals, or the sampled behavior materially exceeds this tested scope; investigate before rerun, not via automatic retries. Dedicated, independently scoped cgroup identity/quotas and non-cryptographic **plus** proof-workload storage and peak-resource tests are separate readiness gates before any shared-host or persistent experiment. No Production deployment claim follows.

**Disk and rollback gate:** before launch, observe available space and memory on the dedicated runtime filesystem; refuse launch under disk/memory pressure or interference with another workload. The launcher currently has **no independently measured full-session peak disk bound, cgroup disk quota, or dedicated Linux service identity**. Do not fabricate a minimum-free-space threshold from checkout size or from unrelated historical proof measurements: these are **open host-readiness gates in #88**. Normal exit/CTRL-C/TERM must leave no `tag-synthetic-*` entry in the selected runtime parent and no listener/process for that session; rerun `--inspect-only` to confirm the local lease/entry state. After abnormal termination, STOP and investigate exact process and path ownership before *manual* cleanup; never auto-delete an uncertain leftover or remove pinned sources, binaries or CRS. Rolling back this local package means stopping the session and deleting only confirmed disposable session files; no installation or Production configuration was changed.

**Disposition:** **GO** for the demonstrated short-lived, same-machine, pre-provisioned, synthetic non-cryptographic local package, conditioned on the same preflight and scope. **NO-GO** for shared-VM/Production deployment, persistent service, newly provisioned cryptography or SITL integration. Whole-session **sampled measurements** now exist for one synthetic non-crypto scenario; **hard-enforced aggregate CPU/RAM/process/disk budgets**, dedicated service identity, proof-path capacity evidence and any colocation authorization remain separately Open under [#88](https://github.com/ROCSI-eu/Telemetry-Attestation-Gateway/issues/88). This local package does not promote cryptographic evidence or change the 600 cm/s predicate.


### TAG #88: opt-in aggregate bounds on Qube Dev1 (non-Production)

The *separate* `run_tag88_bounded.py` entrypoint runs the existing local,
synthetic short-circuit console inside a **collected transient systemd user
service** in the dedicated `tag-qa88.slice`. No service is installed/enabled,
and the existing `run_isolated_local.py` default remains unchanged. The
bounded path requires an existing owner-private runtime parent and a working
unprivileged user bus. It fails closed if another/stale TAG #88 slice exists,
the service cannot start, or the inner process cannot attest the exact
dedicated cgroup membership and hard values:

- `MemoryMax=134217728` (128 MiB) across the service process tree;
- `MemorySwapMax=0` (swap disabled for this unit, fail closed unless
  `memory.swap.max` is exactly `0` before any listener);
- `CPUQuota=50%`, `TasksMax=12`, `RuntimeMaxSec=15s`,
  `KillMode=control-group`;
- `bwrap --size 8388608 --tmpfs /tmp` **only** on this opt-in path, with
  separate loopback-only network namespace and existing read-only source
  binds. `TemporaryFileSystem` is intentionally not used by systemd.

Use only an approved disposable Qube parent, outside the source checkout:

```sh
python3 experiments/web-console-v0/run_tag88_bounded.py \
  --runtime-parent /path/to/existing/private/qa-parent --check-only
python3 experiments/web-console-v0/run_tag88_bounded.py \
  --runtime-parent /path/to/existing/private/qa-parent --seconds 8
```

The child lifetime is restricted to 1–10 seconds, leaving room for startup
and teardown under the 15-second unit ceiling; a shorter measured run is
**not** evidence that expiration at 15 seconds has been exercised. The
operator token is printed only to the invoking terminal through
`systemd-run --pipe`; do not persist it in QA logs. A fully verified, empty
own slice is stopped after execution, while a nonempty or foreign slice is
**never** stopped or deleted. After abnormal process death or an uncertain
lease, halt and inspect before manual owner-only cleanup; do not retry
blindly or touch any shared Desktop Commander or app.slice cgroup.

The 8 MiB limit applies to the **inner sandbox /tmp only**. The outer
owner-private session runtime is not covered by a disk quota, so this is
**not** a whole-session disk cap. The outer ext4 runtime has **no per-session
quota**, remains a separate NO-GO storage gate, and was not filled for QA.
The research proof path is explicitly
excluded from this low-memory profile and the bounded launcher accepts no
offline toolchain selector. Qube's one-off synthetic preflight on
2026-11-18 showed exact cgroup memory/CPU/task values, CPU throttling,
private /tmp ENOSPC at 8 MiB, distinct loopback namespace and clean slice
rollback. Those observations are non-Production research only, not proof
capacity, dedicated service identity, production-readiness or authorization
for shared-VM colocation. Separate synthetic negative QA on 2026-11-18
confirmed: systemd runtime timeout after ~17.3 s with a 2 s stop grace;
128 MiB RAM pressure and an `oom-kill` with `MemorySwapMax=0` and no
observed swap; and a gradual `TasksMax=12` denial (`pids.events:max=1`,
peak `pids.current=12`). All dedicated units/slices were removed and
Desktop Commander remained untouched. These are reused experimental QA
checkpoints, not new runtime tests or Production-readiness evidence.
