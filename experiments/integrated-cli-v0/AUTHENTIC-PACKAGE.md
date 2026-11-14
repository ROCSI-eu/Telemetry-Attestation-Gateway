# Authentic synthetic package check — isolated CLI increment

> **EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION**

This independent local command is a **separate experimental contract**, not a replacement for the existing integrated CLI, and **not** an implementation of an accepted public envelope or `RP` package.

The current `integrated-cli-v0/evidence-results.json` is deterministic orchestration **mock** evidence. It is not relabeled or modified by this increment. The browser console continues to consume **mock-only** evidence and never accepts raw proof packages.

## Genuine versus mock discriminator

`authentic_package_cli.py` accepts a **locally generated, explicitly synthetic** bounded-speed proof package and invokes the existing independently callable `bounded-speed-proof-v0/verify.py` API. It **reconstructs** public inputs using the strict checked-in CBOR decoder, checks the pinned verification-key digest through the verifier, and does not accept a manifest's declaration of cryptographic validity.

The machine-readable output is structurally distinct from the mock orchestration transport:

- `schema_version: TAG_AUTHENTIC_SYNTHETIC_CHECK_V0_EXPERIMENTAL`
- `evidence_kind: AUTHENTIC_SYNTHETIC_PACKAGE_CHECK` and `mock: false`
- `package`, `verification_input`, and `cryptographic` are separate typed outcomes
- `verification_performed` becomes true only for independently obtained `VALID` or `INVALID`
- `proof_generation: NOT_OBSERVED` — the verifier did not witness the proving process
- `source_trust: NOT_EVALUATED`, `policy`, `freshness`, `revocation`, `replay` all `NOT_EVALUATED`
- `publication: NOT_PERFORMED`, `relying_party_decision: NOT_MADE`, `command_path: NONE`
- `A0_SYNTHETIC` is demonstrator assurance only; no inference about real telemetry truth, sensor trust, time or coverage

A `VALID` result only means the locally pinned verifier accepted the submitted proof with public inputs independently reconstructed from deterministic CBOR and the expected verification key. The command does **not** generate a proof, execute a MAVLink pipeline, assert an observation's truth, or make a relying-party decision.

## Minimal local contract

The package directory must be private, generated only by the existing test-only `bounded-speed-proof-v0/prove.py` and contain exactly four regular files:

- `manifest.json` — recognized experimental labels, expected schema/target/tool versions, digests and minimized public metadata
- `public-artifact.cbor` — strict public canonical CBOR
- `proof` — cryptographic bytes, not serialized into the result
- `vk` — verification material, checked against the experiment's pinned digest by the verifier

The CLI rejects extra files, symlinks, missing files, incompatible manifest fields, inappropriate labels, unexpected tool versions, and digest mismatches before invoking the verifier. It bounds each file's size and does not print package paths, private speed, witness material, proof contents or secret correlation data. Manifest digests are **integrity checks, not a signature or source-of-truth attestation**. A locally forged manifest can pass those hashes; only the pinned verifier establishes cryptographic validity.

Invalid or incompatible package material fails closed as `REJECTED`; operational inability to verify is `UNVERIFIABLE`, never `VALID`. An independently rejected proof may report `INVALID` if its manifest accurately binds those proof bytes.

## Invocation (local, no provisioning in this command)

With an already provisioned, checksum-pinned research toolchain and locally cached CRS, invoke from an **isolated, network-disabled environment** as described in `../bounded-speed-proof-v0/qube-offline-reproduction.md` (currently proposed in PR #98). The path below must name a privately held synthetic test package:

```text
python3 experiments/integrated-cli-v0/authentic_package_cli.py \
  --package-dir /path/to/private/synthetic-proof-package
```

The program never fetches a vendor verifier, hosted service, license server, remote policy service or CRS material. If `bb` or CRS is unavailable, verification fails closed. No new default dependency is introduced: the standard offline CI tests mock the invocation boundary and inspect the contract only.

**Exit codes:** 0 independently valid; 2 rejected package; 3 invalid canonical input; 4 independently invalid proof; 5 unverified or operational failure.

Default repository tests:

```text
python3 scripts/check_experiments.py
python3 scripts/check_docs.py
```

## Remaining Open work

A reviewed authentic result may eventually be mapped into a **separate, minimized browser-safe evidence artifact**; a proof package itself must never be served to the web console. Adding that adapter requires an explicit provenance discriminator, an authenticated producer or locally verifiable evidence binding, strict allowlisting and checks that neither a mock `VALID` nor a manifest-only `VALID` can be promoted.

No architecture selection, official proof suite contract, upgraded assurance, consumer guarantee, legal/license decision, deployment, production host, real telemetry, customer workflow or compliance claim follows from this experiment.
