# Local web console preview v0

> **EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION**

**Status:** experimental local UI increment for #87, not public hosting or an accepted product/operator console.

This is a static, dependency-free, responsive browser presentation of the **deterministic orchestration/control-flow mock** already recorded in `../integrated-cli-v0/evidence-results.json`. The result source uses mocks for proof generation and verification. **Neither this page nor that source proves that a genuine cryptographic proof was freshly generated or verified.** No background jobs, live MAVLink, browser-to-Qube/MCP connection, raw telemetry, witness material, keys, private speed or persistent browser storage.

## Run locally

From the repository root:

```sh
python3 -m http.server 8765 --bind 127.0.0.1 --directory experiments
```

In the **same machine's browser**, open:

`http://127.0.0.1:8765/web-console-v0/`

The browser fetches only `../integrated-cli-v0/evidence-results.json` from the same loopback server. **Do not bind a public interface, expose the server through a tunnel/proxy or deploy this page to a public hostname.** Stop the temporary server when the inspection ends. There is no independent live backend or proof-generation endpoint in this increment.

## UI scope

- Choose and replay pre-recorded synthetic orchestration cases without executing them.
- See typed source, predicate, proof-generation, verification-input and cryptographic states.
- Keep publication state, source assurance and relying-party decision separate.
- Mark stages according to the recorded case and explicitly disclose when proof generation was only mocked.
- Avoid animation that implies a live run. Use responsive CSS, native keyboard/touch controls and reduced-motion-safe behavior.
- Fail closed with a visible error if the expected labeled evidence is missing or incompatible.

This UI deliberately does not expose exact normalized speed, raw telemetry, coordinates, identities, witnesses, credentials, hidden correlation data or a MAVLink command path.

## Next increments (Proposed)

1. Use genuine synthetic proof/independent-verifier evidence generated with the pinned experimental Noir and Barretenberg toolchain **only after a verified isolated run**, with a provenance and kind discriminator. Never blend mock and genuine results.
2. Design a narrow allowlisted local runner/status interface for authenticated, bounded operator-triggered synthetic jobs without shipping witnesses to the browser.
3. Verify browser behavior on Chromium, Firefox and WebKit-family engines; assess performance and accessibility before making platform support claims.
4. Keep any public static showcase at `tag.rocsi.eu` governed by #89. Live proving, Production/shared-VM execution and public routing are not authorized by this file.

Proof validity is not telemetry truth. This project is observational only; no flight control or MAVLink command generation/forwarding is permitted.
