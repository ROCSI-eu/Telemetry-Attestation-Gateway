# Deterministic local publication mock (`v0`)

> **EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION**
>
> **NON_CRYPTOGRAPHIC_PUBLICATION_MOCK — NO AUTHENTICATION, SIGNATURE, SUBJECT BINDING, OR PUBLICATION AUTHORITY**

This experiment addresses issue #81. It exercises the optional publication boundary around an already-minimized synthetic verifier result without creating a live publication service, ledger dependency, production receipt format, or new proof path.

It is deliberately narrower than the Proposed product-level local signed receipt. The generated record is a deterministic control-flow mock only. Its `authentication`, `signature`, and `subject_binding` fields are all `NOT_PERFORMED`, and `verification_authority` is `NONE`.

## Research question

Can publication be exercised as an optional local adapter outcome while preserving the pre-publication verifier result, remaining offline, and preventing restricted or correlating material from entering a receipt or persistent record?

## Boundaries

The experiment remains:

- local and offline;
- synthetic-only and `A0_SYNTHETIC`;
- stateless: it creates no publication database, receipt store, queue, or durable correlation record;
- free of real telemetry, hardware, command paths, participant/customer data, production credentials, production trust roots, vendor services, DNS, and live ledgers; and
- independent of proof generation: it consumes only the allowlisted minimized result shape already used by `mock-gateway-v0`.

A caller supplies a demonstrably synthetic 256-bit subject digest only as an invocation input. The mock validates that input and then deliberately discards it. It is not emitted, persisted, or deterministically reflected in the receipt because doing so would create correlation material. Consequently, the mock receipt **does not bind to a claim** and cannot count as cryptographic publication evidence.

## Tested publication outcomes

The local adapter exercises these experimental control-flow outcomes:

```text
NOT_PERFORMED
SUBMITTED -> FINALIZED
SUBMITTED -> SUBMISSION_FAILED
```

These names are used only to exercise the local adapter lifecycle. They do not freeze a public API or replace the normative typed publication dimension in `docs/claim-envelope.md`.

For every outcome, the input verifier result is copied unchanged. Publication success does not upgrade cryptographic validity, and publication omission or outage does not rewrite a `VALID` cryptographic result. The mock never creates or serializes a relying-party business decision.

## Receipt shape

A successful mock call returns a deterministic record containing only:

- the experiment profile;
- the non-cryptographic mock marker;
- local adapter state;
- explicit `NOT_PERFORMED` authentication, signature, and subject-binding markers;
- `verification_authority = NONE`; and
- a deterministic digest of that fixed mock record shape.

The digest is only a reproducibility checksum for the mock record. It is **not** a signature, receipt proof, claim binding, timestamp, ordering proof, publication authority, or security evidence.

No raw telemetry, exact/private speed, proof bytes, witness/opening, salt/nonce, source identity or pseudonym, mission/customer data, credential/key, idempotency secret, request fingerprint, or subject/correlation digest is permitted in the receipt or evidence output.

## Run locally

```text
python3 experiments/publication-mock-v0/test_publication_mock.py
python3 experiments/publication-mock-v0/evidence.py > experiments/publication-mock-v0/evidence-results.json
```

Both commands use only the Python standard library. The tests/evidence runner deny Python network connection functions while exercising the mock.

## Evidence interpretation

`evidence-results.json` records deterministic synthetic evidence for:

- finalized mock publication;
- repeated-call convergence;
- publication omission;
- injected publisher outage;
- unchanged verifier results across publication outcomes;
- absence of emitted subject correlation material;
- absence of publication-created persistent state in a clean temporary workspace;
- non-cryptographic marking;
- restricted-field absence; and
- offline execution.

Success establishes only that this stateless synthetic adapter preserves the tested control-flow and privacy separation.

It does **not** establish a cryptographically authenticated or claim-bound receipt, publication authority, independent receipt verification, telemetry truth, trustworthy provenance/time, interval or whole-flight coverage, safety, contractual/payment/regulatory compliance, workflow value, demand, pilot intent, a selected publication substrate, production capacity, or production readiness.

Publication remains optional corroboration. Independent proof verification remains usable without publication. `A0_SYNTHETIC` remains the only demonstrator assurance tier.
