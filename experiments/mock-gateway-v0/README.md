# Mock local gateway/operator boundary (`v0`)

> **EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION**

This experiment addresses issue #79. It wraps the existing synthetic end-to-end telemetry-to-proof path in a deliberately small local service boundary to test duplicate handling, idempotency, bounded retries, restart behavior, stage-failure isolation, minimized persistence, proof-package disposal, and restricted-field absence.

It is a disposable technical-feasibility experiment. It is **not** the formal `RP` package, a frozen claim contract, a selected service architecture, a production API, a supported MAVLink adapter, or a proof-system selection.

## Research question

Can the existing experimental path survive realistic local gateway/service behavior without collapsing typed verifier dimensions or leaking restricted data?

The tested logical flow is:

```text
synthetic fixture
  -> existing parser/normalizer
  -> existing proof worker path
  -> existing independent verifier
  -> minimized local lifecycle/result
```

The default genuine runner delegates to [`../end-to-end-v0/demo.py`](../end-to-end-v0/demo.py). It does not create a second proof implementation.

## Boundaries

The experiment remains:

- local-only and offline-default;
- synthetic-only and `A0_SYNTHETIC`;
- receive-only and observational;
- free of hardware, real telemetry, participant/customer data, production credentials, hosted verification, live ledgers, and publication authority;
- free of HTTP, authentication, multi-tenancy, external queues, and production service dependencies; and
- free of any MAVLink command-generation, approval, forwarding, relay, or flight-control path.

The persistent state is a disposable local JSON file used only to exercise restart and idempotency behavior. It stores a domain-separated hash of the opaque idempotency key, a request fingerprint, monotonic lifecycle state, bounded attempt metadata, and a minimized typed result. It does **not** store the raw idempotency key, capture name, raw MAVLink, normalized/private speed, coordinates, witness, proof bytes, stable source identity, salts/nonces, credentials, customer details, or mission details.

The hash is still correlation material and is therefore confined to this local disposable state. It is not emitted in the CLI result or checked-in evidence.

## Lifecycle and idempotency

The experiment uses the following narrow local states:

```text
RECEIVED -> PROVING -> PROVED -> VERIFIED
                  \-> REJECTED
                  \-> FAILED
           PROVED \-> REJECTED
```

Retries append attempt metadata and do not move lifecycle state backward. A process interruption can leave a request at `PROVING`; reopening the same state file and resubmitting the same request continues from that state rather than creating a second record.

For one opaque idempotency key:

- an identical retry returns the stored logical outcome without invoking the runner again;
- changed request content returns stable `IDEMPOTENCY_CONFLICT`; and
- the raw idempotency key is never persisted or emitted.

This is experimental local behavior, not a stable API contract.

## Failure separation

The mock boundary intentionally keeps service availability separate from proof validity.

- A retryable prover failure produces `cryptographic = UNVERIFIABLE` and can be retried within the configured bound.
- A verifier outage or unavailable verifier produces `cryptographic = UNVERIFIABLE`; it does **not** become `INVALID`.
- A proof that the verifier actually checks and rejects remains `cryptographic = INVALID`.
- Malformed telemetry is rejected before successful proof generation.
- `publication` remains `NOT_PERFORMED`.
- `relying_party_decision` remains `NOT_MADE`.

No `overall_valid`, compliance, or business-decision Boolean is introduced.

## Boundary tests

The standard-library suite does not require Noir or Barretenberg:

```text
python3 experiments/mock-gateway-v0/test_mock_gateway.py
```

It covers:

- identical duplicate convergence without rerunning the work;
- `IDEMPOTENCY_CONFLICT` for changed content under the same key;
- bounded retry and retry exhaustion;
- process interruption plus restart from persisted state;
- verifier-unavailable versus cryptographic-invalid separation;
- malformed-input rejection;
- monotonic lifecycle transitions;
- temporary proof/work-package disposal;
- recursive restricted-field/value absence from emitted and persisted material; and
- execution while Python network connection functions are denied.

The network guard covers this Python service-boundary path. It is not a substitute for OS/network-namespace isolation when genuine external proof binaries are measured.

## Checked-in service evidence

Regenerate the deterministic fault-injection evidence with:

```text
python3 experiments/mock-gateway-v0/evidence.py \
  > experiments/mock-gateway-v0/evidence-results.json
```

[`evidence-results.json`](evidence-results.json) records only minimized synthetic service-boundary results. Its controlled fault cases do **not** pretend to be new proof-system measurements.

The genuine proof-backed integration path is available through the default runner when the pinned proof tools used by `end-to-end-v0` are already installed. The previously measured genuine proof evidence remains [`../end-to-end-v0/evidence-results.json`](../end-to-end-v0/evidence-results.json).

## Genuine local integration

With the same pinned local proof tooling already required by `end-to-end-v0`, run:

```text
python3 experiments/mock-gateway-v0/mock_gateway.py \
  --state-file /tmp/tag-mock-gateway-state.json \
  --idempotency-key synthetic-request-1 \
  --capture-name unsigned-consistent \
  --maximum-speed-cm-s 600
```

The default runner calls the existing end-to-end experiment, uses a temporary proof package, minimizes the typed result, disposes of the package, and persists only the local service metadata described above.

The command itself performs no provisioning or network fetch. Genuine proof execution inherits the pinned experimental tool and CRS requirements documented by `end-to-end-v0`.

## Interpretation boundary

A successful experiment establishes only that one disposable local wrapper can exercise the tested service behaviors around the existing synthetic research path.

It does **not** establish telemetry truth, trustworthy sensors or time, source provenance, interval/continuous/whole-flight coverage, safety, contractual/payment/regulatory compliance, workflow value, demand, willingness to pay, pilot readiness, production capacity, a selected service architecture, a selected proof system, or production readiness.

Publication is not verification. Verification is not a relying party's business decision. One observation is not a whole-flight or compliance claim. `A0_SYNTHETIC` remains the only demonstrator assurance tier.
