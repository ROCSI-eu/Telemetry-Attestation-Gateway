# Provisional publication adapter conformance experiment

> **EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION**

This experiment addresses issue #83. It tests whether a small **provisional, substrate-neutral publication port** can express deterministic local publication behavior without changing proof/verifier semantics, exposing restricted material, depending on a network, or selecting a production publication substrate.

The contract version is `TAG_PUBLICATION_ADAPTER_CONTRACT_V0_EXPERIMENTAL`. It is independently versioned from the test-only publication profiles `TAG_PUBLICATION_PROFILE_TEST_V0` and `TAG_PUBLICATION_PROFILE_TEST_V0_ALT`, the latter existing only to exercise profile-scoped idempotency conflicts. None of these identifiers is a frozen product contract.

## Experimental boundary

The experiment uses only Python's standard library and synthetic digests/metadata. It has two local adapters:

- `DisabledAdapter` — an in-memory no-publication adapter with deterministic idempotency and status semantics; and
- `DeterministicLocalAdapter` — a narrowly refactored equivalent of the existing deterministic local publication mock, using disposable JSON state only where #83 requires idempotency/status/reconciliation evidence. It exercises successful publication, timeout/cancellation reconciliation, typed failures, restart/reload, payload binding, lifecycle monotonicity, and test-only supersession.

There is no HTTP service, live ledger, hosted verifier, vendor SDK, DNS dependency, production credential/trust root, hardware, MAVLink command path, real telemetry, participant/customer data, or production persistence.

## Provisional port

The shared experimental interface exposes only:

- `submit(PublicationRequest) -> minimized result`; and
- `status(record_id) -> minimized result`.

A request contains only an internal opaque idempotency key, a synthetic 256-bit payload digest, an allowlisted synthetic metadata map, and the explicit test-only profile identifier. In this experiment the key is constrained to `idk_` plus 32 lowercase hexadecimal characters, a private-input namespace disjoint from every fixed value the adapter can emit; request validation also rejects metadata values that contain the submitted key. The raw idempotency key and derived request/scope fingerprints are never emitted or persisted in public results, local state, errors, or checked-in evidence. The only permitted correlation handle is the opaque test-local record identifier required for status lookup.

A public result contains only experimental labels, contract/substrate/profile identifiers, an opaque local record handle, the supplied payload digest, allowlisted synthetic metadata, lifecycle state/history, fixed test-recorded time and its explicit test clock authority when applicable, mock receipt state, and a stable typed error where applicable. SDK-, database-, filesystem-, log-, and ledger-native objects do not cross the port.

The adapter receives no proof bytes, witness, raw telemetry, exact protected value, verifier result, policy result, assurance result, stable identity, mission/customer data, credential, or relying-party business decision. Publication therefore cannot rewrite cryptographic validity or another verifier dimension through this contract.

## Lifecycle and error model

The local mock permits only these test transitions:

- `pending -> recorded | failed`
- `recorded -> final | superseded | failed`
- `final -> superseded`

`superseded` and `failed` are terminal. Skipped and reversed transitions are rejected with `INVALID_LIFECYCLE_TRANSITION`.

Failure classes remain distinct:

- retryable/unavailable: `SUBSTRATE_UNAVAILABLE`, `SUBMISSION_TIMEOUT`, `SUBMISSION_CANCELLED`;
- definitive: `PUBLICATION_DISABLED`, `SUBSTRATE_REJECTED`;
- caller rejection/conflict: `UNSUPPORTED_PUBLICATION_PROFILE`, `IDEMPOTENCY_CONFLICT`; and
- malformed/not-found: stable input/handle errors such as `INVALID_PAYLOAD_DIGEST` and `UNKNOWN_RECORD`.

A timeout or cancellation persists only a `pending` disposable test record. A retry after reload reconciles that same logical record monotonically to `recorded -> final`; it does not create a second record or report ambiguous success.

## Run locally

```text
python3 experiments/publication-adapter-v0/test_publication_adapter.py
python3 experiments/publication-adapter-v0/evidence.py > experiments/publication-adapter-v0/evidence-results.json
```

The tests and evidence runner deny Python socket connection attempts while exercising the port. The checked-in evidence must reproduce byte-for-byte under CI.

## Evidence and limitations

`evidence-results.json` records only minimized synthetic conformance outcomes. Recursive checks cover public results, public errors, disposable local state, and the evidence object itself for restricted keys and raw idempotency-key values.

Success establishes only that the tested **provisional synthetic adapter contract** expresses the listed deterministic local behaviors. It does not establish interoperability, a frozen API, a selected substrate, receipt authenticity, publication authority, global ordering, trustworthy time, independent receipt verification, telemetry truth, higher assurance, safety, contractual/payment/regulatory compliance, workflow value, demand, pilot intent, deployment approval, or production readiness.

Publication remains optional corroboration. Proof validity is not telemetry truth, telemetry assurance remains separate from proof strength, one observation is not interval/whole-flight compliance, and verification remains separate from any relying-party business decision.
