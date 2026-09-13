# Bounded-speed proof and offline verifier experiment (`v0`)

> **EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION**

This experiment addresses issue #68. It connects the provisional deterministic public artifact from [`../bounded-speed-v0/`](../bounded-speed-v0/) to one genuine Noir/Barretenberg proof path and a separately invokable verifier that has no access to the private speed witness.

It is a disposable research demonstrator. It is **not** the repository's promoted `RP` package, a frozen claim contract, an accepted proof-system selection, a security audit, or production code.

## Research question

Can a verifier independently reconstruct the public inputs for the synthetic predicate

`speed_cm_s <= maximum_speed_cm_s`

from the strict public CBOR artifact, then verify a genuine proof locally without receiving `speed_cm_s` or any witness material?

## Pinned experiment stack

- Noir / Nargo: `v1.0.0-beta.26`
- Barretenberg `bb`: `v5.2.0`
- public artifact semantics: `bounded-speed-v0`, schema version `0`
- demonstrator assurance: `A0_SYNTHETIC`

These versions are experiment inputs, not an accepted architecture. The Barretenberg release-binary provenance/licensing adoption question recorded by the proof benchmark remains **Open**; no tool binary, CRS, or third-party source is vendored here.

## Public/private boundary

Private witness:

- `speed_cm_s: u32`

Verifier-visible material:

- deterministic CBOR public artifact containing the version, domain, public `maximum_speed_cm_s`, statement, and `A0_SYNTHETIC`;
- proof bytes; and
- verification key.

The verifier does not accept a witness file, `Prover.toml`, generated witness, or private speed argument.

### Proof-system public inputs

The verifier first calls the strict `bounded-speed-v0` decoder and reconstructs its ordered proof-system-neutral inputs:

1. `version`;
2. `maximum_speed_cm_s`;
3. `context_sha256`.

For this experiment only, the 256-bit context digest is split into two unsigned 128-bit limbs so each value is safely representable as one Noir/Barretenberg field input. The concrete ordered proof inputs are therefore:

1. `version: u32`;
2. `maximum_speed_cm_s: u32`;
3. high 128 bits of `context_sha256`;
4. low 128 bits of `context_sha256`.

The circuit independently constrains the fixed version and context limbs as well as `speed_cm_s <= maximum_speed_cm_s`. This mapping is **Proposed experimental glue**, not a released encoding contract.

The verifier writes its own Barretenberg public-input file from the CBOR artifact. It never trusts a prover-supplied public-input file, ordering, context interpretation, or maximum value.

## Typed verifier result

The verifier returns separate dimensions rather than one overall validity Boolean:

- `input`: `ACCEPTED` or `REJECTED`;
- `cryptographic`: `VALID`, `INVALID`, `UNVERIFIABLE`, or `NOT_CHECKED`;
- `policy`: `NOT_EVALUATED`;
- `freshness`: `NOT_EVALUATED`;
- `revocation`: `NOT_EVALUATED`;
- `replay`: `NOT_EVALUATED`;
- `assurance`: explicit `A0_SYNTHETIC` demonstrator/effective state, with required assurance not evaluated;
- `publication`: `NOT_PERFORMED`;
- `relying_party_decision`: `NOT_MADE`.

`VALID` means only that the pinned cryptographic verifier accepted the proof for the public inputs reconstructed from the supplied artifact and verification key.

## Prover package minimization

`prove.py` uses a temporary working copy of the Noir circuit. `Prover.toml` and the generated witness remain inside the temporary directory and are destroyed after proving. A successful output package contains only:

- `public-artifact.cbor`;
- `proof`;
- `vk`; and
- `manifest.json` with public/test-only metadata and digests.

The manifest does not contain the private speed.

The prover rejects an over-limit synthetic witness before proof generation. It does not convert that policy/predicate failure into a cryptographic result.

## Run

The default scripts make no network requests. The pinned `nargo` and `bb` binaries must already be installed, and Barretenberg's public CRS material must already be provisioned in the local cache.

Generate one synthetic proof package:

```text
python3 experiments/bounded-speed-proof-v0/prove.py --speed-cm-s 1200 --maximum-speed-cm-s 1500 --output-dir /tmp/tag-proof
```

Verify without witness access:

```text
python3 experiments/bounded-speed-proof-v0/verify.py \
  --public-artifact /tmp/tag-proof/public-artifact.cbor \
  --proof /tmp/tag-proof/proof \
  --verification-key /tmp/tag-proof/vk
```

The CLI speed argument is for an explicitly synthetic local experiment only. The prover does not echo it or include it in the output package. The verifier has no corresponding argument.

Run standard-library structural/unit tests:

```text
python3 experiments/bounded-speed-proof-v0/test_verify.py
```

`evidence.py` exercises the genuine proof cases with the pinned toolchain and writes a minimized result record. The committed `evidence-results.json` is captured from the PR evidence run after tool/CRS provisioning, with the measured evidence phase executed without network egress.

## Evidence cases

The genuine evidence run covers:

- below-limit proof verifies;
- equality-boundary proof verifies;
- above-limit witness is rejected before proof generation;
- one-byte proof mutation is cryptographically rejected;
- a different but canonical public speed-limit artifact causes cryptographic rejection;
- malformed public artifact is rejected before cryptographic verification; and
- the verifier package contains no witness or private speed material.

## Interpretation boundary

Proof validity is not telemetry truth. Telemetry assurance is separate from proof strength. One observation is not interval, whole-flight, safety, contractual, payment, or regulatory compliance evidence. Verification is not a relying party's business decision. Publication is not verification.

This experiment does not establish trustworthy sensors or time, hardware integrity, continuous coverage, workflow value, demand, pilot intent, willingness to pay, compliance, safety, production capacity, or deployment readiness.
