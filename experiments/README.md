# Experimental research workspace

> **EXPERIMENTAL · SYNTHETIC_ONLY · NOT VALIDATION OR PRODUCTION AUTHORIZATION**

This directory is the lightweight workspace for disposable, reproducible technical research that is already permitted by the repository's Current parallel-exploration model.

Experiments here are intentionally easier to start than promoted project artifacts. They exist to answer bounded technical questions with synthetic inputs and reproducible evidence, not to create another governance layer.

## Minimum experiment record

Each experiment should state:

1. the hypothesis or research question;
2. the synthetic input provenance and any fixture assumptions;
3. the pinned tool/dependency versions needed to reproduce it;
4. the local/offline command used to run it;
5. the observed result; and
6. the limitations and non-claims.

Use [`TEMPLATE.md`](TEMPLATE.md) when useful. It is guidance, not a gate.

## Current experiments

- [`bounded-speed-v0/`](bounded-speed-v0/) — deterministic integer/CBOR encoding spike for the synthetic predicate `speed_cm_s <= maximum_speed_cm_s`.
- [`proof-system-benchmark-v0/`](proof-system-benchmark-v0/) — proof-system feasibility benchmark for the same synthetic bounded-speed predicate.
- [`mavlink-normalization-v0/`](mavlink-normalization-v0/) — receive-only MAVLink 2 parsing and deterministic synthetic horizontal-speed normalization spike.
- [`bounded-speed-proof-v0/`](bounded-speed-proof-v0/) — genuine bounded-speed proof plus independently invokable public-input-reconstructing offline verifier experiment.
- [`end-to-end-v0/`](end-to-end-v0/) — local synthetic MAVLink normalization → private witness → zero-knowledge proof → independent offline verification demonstrator.
- [`mock-gateway-v0/`](mock-gateway-v0/) — local synthetic gateway/operator-boundary experiment for idempotency, retry/restart, failure isolation, minimized state, and restricted-field absence around the existing end-to-end path.

## Workspace boundary

Experiments in this directory must remain synthetic, local/offline by default, reversible, and isolated from production infrastructure. Do not add real telemetry, participant/customer data, stable identities, exact mission/location data, production credentials or trust roots, live publication, hardware, or any MAVLink command-generation/forwarding path.

External SDKs should remain behind narrow adapters when introduced. A successful experiment is technical exploration evidence only. It does not freeze a claim contract, select an architecture, establish telemetry truth or assurance, validate a workflow or market, authorize hardware, or create an MVP/pilot/production claim.

The Current demonstrator assurance remains `A0_SYNTHETIC`.
