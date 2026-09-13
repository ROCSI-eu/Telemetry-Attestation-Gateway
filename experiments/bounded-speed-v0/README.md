# Bounded-speed deterministic encoding spike (`v0`)

> **EXPERIMENTAL · SYNTHETIC_ONLY · NOT VALIDATION OR PRODUCTION AUTHORIZATION**

This experiment implements the first executable format/claim spike for:

`speed_cm_s <= maximum_speed_cm_s`

It is a provisional research artifact for issues #65 and #66. It is **not** the frozen claim envelope, an interoperable API, a cryptographic proof, telemetry-assurance evidence, or production code.

## Research question

Can we represent the bounded-speed predicate with explicit integer semantics, a byte-stable deterministic CBOR public artifact, strict decoding, and verifier-side reconstruction of an ordered proof-system-neutral public-input vector?

## Integer semantics

- `speed_cm_s`: private/witness-side synthetic integer, unsigned 32-bit, unit `cm/s`.
- `maximum_speed_cm_s`: public synthetic policy limit, unsigned 32-bit, unit `cm/s`.
- valid range for both: `0..4294967295`.
- floating-point values, booleans, negative values, and overflow are rejected.
- predicate equality is accepted: `speed_cm_s == maximum_speed_cm_s` is `satisfied`.

The broad `uint32` range is an encoding bound only. It is not a claim that every value is physically meaningful.

## Provisional public artifact

The experiment encodes this deterministic CBOR map using unsigned integer field identifiers:

| Key | Field | Type/value |
| --- | --- | --- |
| `1` | `version` | unsigned integer, fixed `0` |
| `2` | `domain` | UTF-8 text, fixed `tag.bounded-speed.v0` |
| `3` | `maximum_speed_cm_s` | unsigned 32-bit integer |
| `4` | `statement` | UTF-8 text, fixed `speed_cm_s<=maximum_speed_cm_s` |
| `5` | `assurance_id` | UTF-8 text, fixed `A0_SYNTHETIC` |

The private `speed_cm_s` value is deliberately absent from the public artifact.

The decoder accepts only the narrow CBOR subset needed by this spike, enforces shortest-form integer/length encodings and canonical map-key ordering, rejects unknown/missing fields and trailing bytes, and re-encodes the accepted object to confirm byte identity.

## Ordered public inputs

The checker reconstructs, in this exact order:

1. `version`;
2. `maximum_speed_cm_s`; and
3. `context_sha256`.

`context_sha256` domain-separates the fixed experiment domain, statement, and assurance identifier. It deliberately remains a 32-byte digest/hex value at this layer. Mapping that digest into a proof-system field is deferred to the proof benchmark rather than hidden inside the format spike.

## Synthetic fixtures

[`fixtures.json`](fixtures.json) contains three fabricated test-only observations: below the limit, exactly at the limit, and above the limit. These values have no relationship to a real vehicle, flight, operator, mission, site, customer, or participant.

## Run locally

No third-party package, account, network service, hosted verifier, ledger, DNS lookup, credential, or hardware is required.

```text
python3 experiments/bounded-speed-v0/test_bounded_speed.py
python3 experiments/bounded-speed-v0/bounded_speed.py
```

The first command runs strict encoding/decoding and boundary tests. The second emits diagnostic JSON containing public artifact bytes and reconstructed public inputs for the synthetic fixtures.

## What this experiment establishes

If the tests pass, this experiment establishes only that the pinned Python implementation can reproducibly encode/decode this provisional synthetic representation, enforce the declared integer predicate semantics, and reconstruct the same ordered public-input values.

It does **not** generate or verify a zero-knowledge proof. It does not establish telemetry truth, trustworthy sensors/time, continuous or whole-flight coverage, hardware integrity, safety, contractual/payment/regulatory compliance, interoperability, customer demand, willingness to pay, pilot readiness, or production readiness.
