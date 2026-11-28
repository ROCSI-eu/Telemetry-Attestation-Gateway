# Testing and operations

| Metadata | Value |
| --- | --- |
| Status | Proposed quality and readiness baseline; SLOs are Open |
| Audience | Engineering, cryptography, security, platform, QA, and operations |
| Accountable role | Service owner/SRE, with discipline leads for specialized evidence |
| Review trigger | Interface, threat, circuit, deployment, SLO, retention, or failure-mode change |
| Authority | Normative evidence categories and readiness gates; tooling/topology examples are illustrative |

## Test layers

- **Unit/property:** conversions, ranges, freshness, trust eligibility, lifecycle invariants, canonical encoding, circuit boundaries.
- **Negative:** invalid/unsigned signatures as policy dictates, stale/mixed snapshots, malformed lengths, overflow, duplicate nullifiers, wrong policy/version/domain, altered public inputs.
- **Golden/cryptographic:** deterministic cross-implementation schema, commitment, nullifier, proof, and verification vectors, including equality at the speed bound and both half-open validity boundaries.
- **Contract:** clients and mock/live adapters against identical version and state-transition suites.
- **Integration:** pinned SITL or synthetic replay with no external-network requirement in default CI.
- **Fuzz:** MAVLink parser, canonical decoder, public API decoder, and proof/public-input decoder; corpus and regressions retained.
- **Security/privacy:** dependencies, secrets, authorization matrix, log/trace/UI redaction, tier-evidence classification and public-metadata review, pseudonym/key-ID rotation, nullifier unlinkability, key rotation, and rollback.
- **Resilience:** restart, persistence unavailable, chain timeout/reorganization, corrupt artifact, clock skew, queue overload, and cancellation.

Fixtures MUST be synthetic or approved for redistribution. Randomized failures print reproducible seeds. Test output must not contain restricted or secret data.

## Solo experimental sandbox testing

Disposable schema/encoding spikes, fixture-driven parsers, local-only mock adapters, non-cryptographic prototypes, proof feasibility benchmarks, toy circuits/local verification, no-hardware/no-command SITL, and local UI/CLI demonstrations MAY run before milestone gates. Their harnesses MUST verify demonstrably synthetic provenance, deny external network access by default, use only loopback mocks and disposable test keys, and assert that no hardware or command interface is reachable. Tests and scans MUST fail when real telemetry, live-ledger endpoints, production hosts, credentials/non-test keys, participant identifiers, or production infrastructure references are present.

Every source artifact or adjacent digest manifest and every console, log, report, export, screen, screenshot, recording, benchmark table, or test result MUST include **`EXPERIMENTAL`**, **`SYNTHETIC_ONLY`**, and **`NOT VALIDATION OR PRODUCTION AUTHORIZATION`**. Sandbox performance is feasibility data only: it is not an SLO, representative benchmark, validation result, or release evidence. Tests may inform redesign, but only the [destination-specific promotion gate](delivery-plan.md#synchronization-gates) can admit a reviewed copy or reimplementation into supported, discovery, MVP, pilot, or production evidence.

## Policy lifecycle, publication, and rollback cases

Lifecycle tests MUST exercise every permitted transition and reject skipped, reversed, unsigned, unauthorized, wrong-digest, out-of-order, and in-place mutation attempts. With an authenticated integer boundary clock, cases MUST cover just before, exactly at, and just after each of `not_before` and `not_after`; equality at `not_before` MUST be accepted as current, while equality at and just after `not_after` MUST be expired. Cases MUST also cover activation before approval or before `not_before`, deprecated acceptance before the exclusive sunset with a warning, and rejection at and after expiry. Matrix cases MUST pair each policy with supported and unsupported schema, statement, circuit, proof-suite, verification-key, tier, and domain identifiers, proving that cryptographic validity cannot override incompatibility.

Publication and resolver tests MUST demonstrate digest-addressed retrieval from a configured registry and offline snapshot without using a prover-supplied description, URL, status, key, or compatibility claim. They MUST reject altered policy bytes, forged/expired/revoked issuer, approval, or publication keys, missing signatures, signatures for a different digest/action, stale or equivocated checkpoints, status-log gaps, sequence rollback, conflicting registries, and a “latest” pointer substituted for the bound digest. Tests MUST show that approval and publication signatures are independently validated and that historical key/authorization evidence remains verifiable after rotation.

Cache and outage cases MUST cover cold cache, fresh cache, freshness-bound edge, stale cache, corrupt cache, missing log continuity, registry timeout, partial response, and recovery with a newer checkpoint. A fresh and complete signed cache or approved offline snapshot may produce the specified result with checkpoint and age recorded; stale, incomplete, conflicting, or unauthenticated status MUST return `temporarily_unverifiable`, never `valid`. Recovery MUST not downgrade a stored sequence or erase a learned revocation. Restart and concurrent-verifier tests MUST preserve those invariants.

Revocation cases MUST cover approved, active, and deprecated policies; immediate and future-effective events; claims produced and/or recorded before revocation but first verified afterward; and rechecking a formerly valid historical decision. At or after the effective revocation time, the expected current result is `revoked`. Historical decisions remain immutable but gain a revocation linkage and cannot be displayed as currently valid. Any permitted non-compromise cutoff exception MUST be signed, exact in scope/time, and rejected for a compromised root or outside its scope.

Rollback drills MUST activate a previously approved immutable digest through a new authorized event, verify its current effective window and complete circuit/key compatibility tuple, preserve the superseded policy and full audit chain, and route new proving to the selected digest. Negative cases MUST attempt rollback to draft, expired, revoked, incompatible, tampered, and unauthorized policies and confirm fail-closed suspension when no eligible predecessor exists. Emergency rollback MUST exercise break-glass expiry and independent review without bypassing signature, digest, or audit requirements.

For every case, assertions MUST cover the externally visible outcome/reason and the append-only audit fields required by the [policy lifecycle model](data-and-proof-model.md#policy-lifecycle-and-verifier-trust), including issuer/authority/key IDs, effective window, state, compatibility, checkpoint/source, cache age, decision time, rollback chain, and revocation result. Privacy tests MUST confirm that these records contain no witness, exact telemetry, or restricted identity. A release gate requires a tabletop and executable rollback/revocation exercise with artifacts sufficient for an independent auditor to reconstruct the decision.

## Scalar profile vector reconciliation

The [proposed scalar profile and vector inventory](adr/0004-proposed-synthetic-scalar-claim-profile.md#vector-and-implementation-delta) identifies scope-matched existing experimental cases and missing v1 cases. It is not a new suite, release gate, or evidence of v1 conformance. The conformance requirements below remain unchanged.

## Claim-envelope interoperability

Interoperability evidence is staged so that early discovery does not imply a stable contract:

1. **Phase 0 discovery/spike:** one reference codec plus an independently authored lightweight decoder or vector checker MUST consume the format-spike fixtures and detect the specified canonical-encoding, field, public-input-ordering, mutation, and typed-outcome failures. The checker MAY be throwaway and MAY use the same language as the reference codec. The released-corpus requirements below do not block synthetic discovery fixtures, paper/non-cryptographic prototypes, or an intentionally disposable schema spike.
2. **Released interoperable envelope/public API:** before an envelope is described as released or interoperable, or its public API as stable, at least two genuinely independent implementations in different languages MUST pass the released vector corpus. They MUST share neither an envelope codec nor verification business-logic library. This two-language requirement remains a release gate, not a Phase 0 entry requirement.
3. **Proof-system/edition compatibility:** before claiming cross-proof-system or cross-edition verification, independent implementations MUST exchange and verify the corresponding proofs and public inputs in every claimed direction and pass the applicable version, suite, key, and negative vectors. Evidence for one proof system or edition MUST NOT be generalized into a compatibility claim for another.

Every supported envelope major/minor, statement, proof suite, assurance tier, policy schema, and ledger profile MUST have a version-controlled golden-vector set. Each vector bundle MUST contain:

- a human-readable case manifest and the exact canonical CBOR envelope bytes;
- decoded field values, canonical public-input sequence/bytes, commitment, nullifier, policy and verification-key artifact bytes and digests, proof bytes (or referenced bytes, digest, and size), and receipt bytes when applicable;
- the authenticated clock, policy, key, revocation, replay-store, reference-fetch, and ledger inputs needed to make evaluation deterministic;
- every expected typed result dimension and non-sensitive reason code, plus the recomputed `service_disposition` when emitted; and
- provenance: specification/registry versions, generator source revision, reproducible command, and artifact digests.

Privacy vectors MUST cover every `A0`–`A5` evidence row and assert that private witnesses and trust-store artifacts are absent from envelope bytes, public inputs, results, receipts, URLs, logs, traces, metrics, crash artifacts, and ledger payloads. They MUST demonstrate the canonical numeric/string tier mapping, reject reserved tiers and inconsistent numeric/string presentations, and prove that committed facts remain bound when undisclosed. For every selectively disclosed field, tests MUST show allowlist/policy necessity, bounded encoding, and rejection when injected into a profile that does not permit it. Source pseudonyms and their hashes MUST never appear publicly. Key-ID cases MUST distinguish the proof `verification_key_id` from source keys, reject stable/cross-domain/identity-derived source-key identifiers, exercise epoch rotation, and verify that rotation mappings remain restricted. Nullifier vectors MUST show equality for replay of the identical scoped claim, inequality after changing the nonce, domain, policy, statement, or source commitment, resistance to a representative source-identity dictionary test, and no cross-scope replay-store identity index. Privacy review MUST assess linkage across a representative multi-claim dataset, not only single-record redaction.

Positive vectors MUST cover attached and referenced proofs and optional receipt absence/presence. Boundary vectors MUST include distinct equality-at-`not_before`, equality-at-`not_after`, just-before, and just-after cases for each endpoint, with expected results demonstrating `not_before <= decision_time < not_after`; they MUST also cover permitted skew without changing endpoint inclusivity, assurance tiers, integer and length bounds, and equality in the proved predicate. Empty and inverted window vectors MUST be rejected as `malformed`. Vectors MUST independently cover every value and precedence collision in the [typed verifier result model](claim-envelope.md#typed-verifier-result-model). Required cross-dimension vectors are: valid proof with policy rejection; valid proof with replay; valid proof with an invalid optional receipt while cryptographic evaluation remains valid; valid proof with insufficient effective assurance; and verifier-valid/service-accepted evidence followed by a separately authored relying-party business rejection. They MUST also show that absent or unavailable optional publication does not change cryptographic validity or derived acceptance, while an unavailable policy-required publication makes policy acceptance/disposition indeterminate without rewriting cryptographic evaluation. They MUST also cover non-minimal CBOR, reordered/non-canonical maps, duplicate/unknown/missing fields, invalid UTF-8/NFC, forbidden null/float/tag/indefinite values, altered domain/policy/key/public input/commitment/nullifier/proof, proof-reference size and digest mismatch, disclosure-policy violations, concurrent replay, revoked or stale artifacts, and unavailable dependencies. Mutation cases MUST change one property at a time where possible.

For the released-envelope/public-API gate, the two independent, different-language implementations MUST consume the same checked-in vectors. Each implementation MUST:

1. decode accepted bytes and re-encode byte-for-byte identically;
2. reconstruct identical public-input bytes without prover-supplied ordering;
3. produce identical commitment and nullifier bytes from approved opening fixtures;
4. verify proofs produced by the other implementation and return every specified dimension/reason and, when present, the correctly derived service disposition for every vector;
5. reject non-canonical encodings rather than normalize and accept them; and
6. demonstrate atomic replay behavior under concurrent submission.

CI MUST run both implementations against the immutable released vector corpus and publish a compatibility matrix keyed by envelope, statement, suite, policy, and key versions. A vector may change only to correct a documented defect; the original remains as a regression fixture when its bytes were released. Adding or changing a registry entry blocks release until vectors, both implementations, and the matrix agree. Freezing the assurance-tier or nullifier registry additionally blocks release until its ADR and explicit product/privacy and security approvals are recorded. Implementations MUST additionally exchange at least one freshly generated, non-golden proof in each direction so that hard-coded vector acceptance cannot satisfy the gate.

## Benchmark methodology

Measure ingestion, queue wait, proving, verification, submission, and end-to-end stages separately. Reports state commit, schema/circuit/policy version, proof parameters, machine CPU/memory, operating system, concurrency, queue settings, fixture, warm-up, sample count, and p50/p95/p99 where meaningful. Record proofs/second, peak memory per worker, dropped-frame rate, proof size, and failure rate.

No “real-time,” scalable, fault-tolerant, or capacity claim is permitted without an explicit workload, deadline/criterion, repeatable method, and result. Thresholds and regression budgets are **TBD by the service owner** after Phase 1/2 baselines.

## Observability and privacy

Required signals are counters for received/rejected/dropped frames and proof outcomes; histograms for queue/proving/verification/submission/end-to-end duration; bounded-queue/backlog gauges; and lifecycle/finality health. Opaque correlation IDs join signals. Stable vehicle IDs, exact telemetry, witnesses, keys, salts, and unreviewed public inputs MUST NOT appear in logs, traces, metrics labels, crash artifacts, or alerts.

Alerts must correspond to user-visible symptoms or safety/security controls and link to an owned runbook once operations begin. Alert thresholds remain Open until baselines exist; high-cardinality attributes require review.

## Deployment progression and resilience

1. Offline deterministic fixture and in-process/mock dependencies.
2. Local SITL integration in a controlled network.
3. Midnight test environment only after the Phase 4 entry ADR.
4. Controlled hardware pilot only after privacy, security, operational, and safety evidence.
5. Production is a separate approval, not an automatic phase outcome.

A minimal local Compose profile may be added when dependencies exist. PostgreSQL, separate services, containers, OpenTelemetry tooling, and UI infrastructure remain proposed. Kubernetes, Redis, NATS, object storage, high availability, and multi-region recovery require demonstrated needs.

Backups/restores apply only when durable state is introduced. Retry, reconciliation, restart, overload, dependency outage, and corrupt-state behavior must be exercised before their corresponding environment gate.

## Deployment-mode acceptance checks

Every supported mode MUST have reproducible evidence for its applicable checks. Packet captures, logs, traces, crash artifacts, queues, and persisted records used as evidence MUST be inspected to confirm that raw telemetry, exact position, stable identity, salts/openings, and witnesses remain inside the approved proving boundary.

| Mode | Required acceptance evidence |
| --- | --- |
| Local developer | Run the pinned synthetic fixture, proof generation, independent verification, lifecycle query, and mock submission with external network access denied. Confirm only reviewed public inputs and redacted metadata cross the logical prover/verifier and mock boundaries; confirm disposable keys are used and restart/failure states do not expose restricted values. |
| Edge agent plus managed control plane | Capture both directions at the customer/vendor boundary and confirm the permitted proof envelope, redacted signals, signed policy/update material, and no restricted fields. Disconnect vendor networking while continuing bounded ingestion and proving, exercise outbox overflow, then reconnect and prove idempotent drain. Reject invalid server identity, unsigned/revoked updates, expired policy state, altered proofs, and incompatible versions. |
| Fully customer-managed | Install and operate from an exportable, integrity-checked artifact bundle with vendor DNS, APIs, credentials, and networks blocked. Exercise proof, verification, policy lookup, audit, backup/restore where applicable, and mock submission; confirm vendor outage has no runtime effect. Test customer-controlled key rotation/revocation, segmented-network partition, bounded queues, rollback, and optional chain outage independently. |
| Independent relying-party verifier | On a machine with no vendor or general network route, import a self-contained proof package and authenticated verification/policy/revocation artifacts, reconstruct canonical public inputs, and obtain the expected result without witness or prover access. Repeat for altered inputs, missing/revoked/expired/incompatible artifacts, and confirm each fails closed. Demonstrate that optional chain/receipt lookup failure is reported separately from proof validity. |

The offline tests MUST block traffic rather than merely omit configuration, assert that no DNS or connection attempt targets a vendor endpoint, and retain the verifier command, artifact digests, trust-store/policy snapshot, decision time, and result. A cached vendor verdict is not independent verification. Acceptance also requires update and rollback ownership to match the selected topology, documented key custody, stated connectivity assumptions, and observed failure behavior consistent with [architecture](architecture.md#deployment-modes).

## SLOs, retention, and readiness

Availability, latency, recovery objectives, data-loss tolerance, capacity, retention durations, and alert thresholds are **Open/TBD**, not zero or unlimited. The service owner proposes values from workload and benchmark evidence; product/privacy approves retention and security reviews exposure.

Production readiness requires:

- accepted workload, SLOs, capacity limits, and overload behavior;
- supported version matrix and upgrade/rollback procedure;
- data inventory, purpose, retention/deletion, access, and backup treatment;
- key rotation/revocation and incident runbooks;
- restore/reconciliation evidence and dependency-failure exercises;
- resolved or explicitly owned residual security/privacy findings;
- external review appropriate to the risk; and
- an approved hardware safety case while preserving no-command architecture.

## Acceptance and related documents

Each [delivery phase](delivery-plan.md) links reproducible commands and artifacts satisfying the relevant categories above. [Architecture](architecture.md) defines failures and signals, [data and proof model](data-and-proof-model.md) defines vectors, and [security and privacy](security-and-privacy.md) defines restricted data and controls.
