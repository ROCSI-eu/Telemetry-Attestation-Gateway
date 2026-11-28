# Data and proof model

| Metadata | Value |
| --- | --- |
| Status | Proposed; encoding and proof system are Open |
| Audience | Cryptography, telemetry, security, and implementing engineers |
| Accountable role | Cryptography lead, with telemetry and security approval |
| Review trigger | Supported message, unit, schema, encoding, circuit, commitment, nullifier, or disclosure change |
| Authority | Normative requirements; JSON record is illustrative and non-canonical |

The public wire contract, disclosure boundary, artifact references, and verifier result semantics are defined by the normative [claim envelope specification](claim-envelope.md). If an illustrative representation in this document conflicts with that specification, the claim envelope specification governs.

## Provisional scalar profile

The [proposed scalar profile](adr/0004-proposed-synthetic-scalar-claim-profile.md) records the current technical direction and existing receive-only integer normalization. A scalar proof does not bind a received observation without additional verified evidence; source-binding experiments remain separate. No final commitment fields, proof system or product claim are selected by this proposal.

## Canonical telemetry model

The MVP snapshot draws only from the selected MAVLink dialect's `GLOBAL_POSITION_INT` and `VFR_HUD`. Compatibility with a pinned SITL and exact field selection MUST be demonstrated before schema approval. The internal record uses integers and rejects overflow or unavailable values rather than coercing them.

| Concept | Unit/encoding | Source direction |
| --- | --- | --- |
| Latitude/longitude | signed degrees × 10^7 | `GLOBAL_POSITION_INT` candidate fields |
| Relative altitude | signed millimetres | `GLOBAL_POSITION_INT` candidate field |
| Horizontal ground speed | non-negative centimetres/second | Normalize a validated groundspeed source |
| Observed/received time | integer milliseconds plus named clock provenance | Source and bridge clocks; not inherently trusted |
| Source trust | closed enum, not Boolean | Parser/signature evaluation |

Required initial trust values are `SIGNED_VALID`, `UNSIGNED`, `SIGNATURE_INVALID`, and `UNKNOWN`. `SIGNATURE_INVALID` records MUST NOT be claim-eligible. Eligibility for `UNSIGNED` or `UNKNOWN` is **Open** and must be explicit in policy; no state silently becomes `SIGNED_VALID`.

Illustrative edge/debug JSON:

```json
{
  "schema_version": 1,
  "record_id": "0191d7c8-632f-7f3d-a5ad-2dcbe4223d24",
  "source": {
    "system_id": 23,
    "component_id": 1,
    "trust": "SIGNED_VALID",
    "message_ids": [33, 74]
  },
  "observed_at_unix_ms": 1712345678000,
  "received_at_unix_ms": 1712345678120,
  "position": {
    "latitude_deg_e7": 513456789,
    "longitude_deg_e7": -113456789,
    "relative_altitude_mm": 54500
  },
  "ground_speed_cm_s": 125,
  "policy_digest": "sha256:illustrative-not-a-complete-digest",
  "nonce": "illustrative-base64url-value"
}
```

This JSON is not the proof encoding and its values do not define production identifiers or algorithms.

## Deterministic encoding requirements

Before circuit implementation, a versioned specification MUST define field order, widths, signedness, bounds, absence semantics, byte order, byte-to-field conversion, field-reduction rejection, hash/commitment parameters, and domain-separation tags. Floating-point proof inputs are prohibited. Golden vectors MUST cover minimum, maximum, negative where allowed, overflow, absent, malformed, and cross-language cases.

A record commitment binds every field needed to interpret the claim, including schema/circuit version, policy digest, trust state where eligibility depends on it, speed, source commitment, nonce, and the version 1 half-open time-window representation `[not_before, not_after)`. The final bound-field list remains **Open** pending privacy and circuit review.

Tier establishment follows the evidence classifications in [security and privacy](security-and-privacy.md#tier-evidence-disclosure-classification). Authenticated source and attestation details may be private witnesses, verifier trust-store artifacts, or committed facts without becoming envelope metadata. The public numeric tier uses the canonical mapping in the [claim envelope](claim-envelope.md#envelope-fields). Source pseudonyms remain private commitment inputs. A source key identifier is a trust-store lookup or committed fact by default and may be selectively disclosed only as an opaque, domain-scoped rotating value under the statement and policy allowlists; `verification_key_id` identifies the proof verifier artifact and is not a source-key identifier.

## First proof statement

Given a versioned committed record and policy, the prover knows a valid opening whose normalized horizontal speed `speed_cm_s` is within the supported integer range and satisfies `speed_cm_s <= maximum_speed_cm_s`. Successful verification represents the pass claim; it does not prove source truth or recency by itself.

### Private witness

- normalized horizontal speed;
- source pseudonym and source-commitment opening (the pseudonym is never public);
- fresh high-entropy record nonce and record-commitment opening; and
- only those additional fields approved by the threat model.

### Public inputs

- schema and circuit identifiers;
- policy digest and public `maximum_speed_cm_s`;
- approved coarse time-window identifier;
- record commitment;
- domain-separated, pseudorandom nullifier output; and
- deployment/domain identifier required to prevent cross-context replay.

### Circuit constraints

- `speed_cm_s` and `maximum_speed_cm_s` have explicit bit widths and range constraints.
- The circuit enforces the non-strict upper bound, including equality.
- Commitment and nullifier calculations use the versioned, domain-separated encoding.
- The nullifier binds the private source-commitment, fresh private record nonce, deployment domain, policy digest, statement ID, and nullifier version/tag; it MUST reveal neither the pseudonym nor a stable per-source value and MUST be unlinkable across nonces and scopes except when the identical scoped claim is replayed.
- Unsupported versions or non-canonical encodings cannot verify.

## Policy lifecycle and verifier trust

A policy is an immutable, canonically encoded, content-addressed document. Its digest binds its policy identifier and revision, issuer identity, approval authority and approval evidence, assurance-tier requirements, predicate parameters, effective window (`not_before` inclusive and `not_after` exclusive), compatible schema/statement/circuit/proof-suite and verification-key identifiers, deployment domains, and supersession/rollback metadata. Changing any bound field creates a new digest and revision; a mutable name or “latest” pointer is never a proof input. The issuer identity identifies the organization accountable for the policy's contents and MUST be authenticated through an approved trust chain. The approval authority is the separately authorized person or body permitted to approve, activate, deprecate, revoke, or authorize rollback; its signed decision MUST name the exact digest, action, reason, decision time, and effective time.

Policy status has the following closed state model:

| State | Meaning and verifier treatment |
| --- | --- |
| `draft` | Authored but not approved. It may be used only in explicitly isolated tests and MUST NOT authorize production proving or acceptance. |
| `approved` | Approval evidence is valid, but the policy is not yet effective or has not been activated. Production claims MUST NOT be accepted under it. |
| `active` | Approved, activated, inside its effective window, compatible with the selected circuit and artifacts, and not revoked. It is eligible for proving and verification. |
| `deprecated` | Still valid only through its declared `not_after` or an earlier signed sunset. New proving SHOULD migrate to its named successor; verification MAY accept it while it remains effective and policy status permits, and MUST report the deprecation. |
| `revoked` | Withdrawn by an authorized, signed revocation, normally for compromise, defect, or invalid approval. It MUST NOT authorize a verification decision at or after the revocation's effective time. Revocation has no implicit end. |
| `expired` | The decision time is at or after `not_after`. It MUST NOT authorize new proving or acceptance. Expiry follows from the signed effective window and does not require a separate status event. |

Transitions are normally `draft` → `approved` → `active` → `deprecated` → `expired`; `approved` or `active` may transition directly to `revoked`, and deprecated policy may also be revoked. States MUST NOT be moved backward in place. Activation cannot precede both approval and `not_before`, and no state event may extend the immutable effective window. Verifiers use an authenticated decision-time authority and require the version 1 rule `not_before <= decision_time < not_after`: equality at `not_before` is eligible, while equality at `not_after` is expired. Future-dated, empty (`not_before == not_after`), inverted, ambiguous, or missing windows fail closed. A proof also fails closed when the policy's compatibility tuple does not explicitly admit every schema, statement, circuit, proof suite, verification key, and domain used by the claim, even if the proof is cryptographically valid.

Rollback means publishing a new, signed status decision that selects a previously approved immutable policy digest as the active target; it never edits history, resurrects a revoked/expired digest, or makes claims under an incompatible circuit valid. The approval authority MUST authorize the rollback, state its scope and effective time, confirm current circuit/key compatibility, and identify the superseded digest. Emergency rollback uses the same controls and produces the same audit evidence. When no non-revoked compatible predecessor exists, proving and acceptance stop rather than fall back to an unsigned, draft, expired, or prover-selected policy.

Claims produced before revocation are not automatically grandfathered. Verification is evaluated against policy status at the verifier's decision time: a claim presented or rechecked at or after the revocation effective time returns `revoked`, including one whose observation, proof-generation, or ledger-recording time was earlier. A relying-party profile MAY preserve a historical decision already completed before revocation as an auditable fact, but MUST label it with its original decision time and status snapshot, MUST NOT represent it as currently valid, and MUST append the revocation linkage. Only an explicit, signed revocation directive may narrow retroactivity for non-compromise administrative revocations; such an exception MUST name a cutoff and relying-party scope, cannot override law or a compromised cryptographic root, and is itself retained in the audit record.

### Test-only offline policy profile

The repository MUST define a **test-only offline policy profile** for deterministic lifecycle tests. The profile consists only of reviewed, checked-in fixture material: the exact immutable canonical policy bytes addressed by their computed digests; a versioned fixture schema; pinned test issuer, approval, status, and publication trust anchors; deterministic signed approval and status-event fixtures with fixed sequence/checkpoint values; and an explicit decision time supplied by each test vector. Private signing keys, if retained to regenerate vectors, are test credentials and MUST be conspicuously named and marked as publicly known and unsafe. Tests MUST verify fixture signatures and recompute digests rather than trusting expected labels.

This profile has no network registry, discovery, mutable `latest` pointer, wall-clock fallback, or ambient production trust store. Resolution is limited to the checked-in fixture set, and an omitted decision time fails closed. Its profile identifier, deployment domain, policy identifiers, trust-anchor identifiers, and signature domain-separation context MUST be reserved for tests. The verifier MUST reject these artifacts outside an explicit test configuration and MUST emit a conspicuous `TEST_ONLY_NOT_PRODUCTION_AUTHORIZATION` classification in human- and machine-readable results. A successful fixture decision demonstrates conformance to the test vector only; it MUST NOT be represented, promoted, or consumed as production authorization.

The fixtures represent the production lifecycle's data and decision semantics: immutable digest binding; independent issuer, approval, status, and publication signature validation; ordered status history; approval and activation prerequisites; half-open effective-window boundaries at an explicit decision time; deprecation reporting; revocation without implicit grandfathering; expiry; compatible rollback to a previously approved digest; compatibility-tuple enforcement; and fail-closed handling of missing, malformed, tampered, unauthorized, out-of-order, revoked, expired, or incompatible evidence. Fixture coverage also records the audit fields and stable reason codes expected from those decisions.

The profile does **not** represent an authoritative registry service, online cache freshness or freeze/outage detection, operational approval quorum, break-glass custody or handling, production trust-root/key provisioning, rotation, revocation, hardware protection, or production key ceremonies. Those operational guarantees remain Deferred until a separately approved production deployment gate supplies their architecture, governance, runbooks, and exercised evidence. Deterministic fixture signatures model the validation inputs for those systems; they are not evidence that those systems or controls exist.

### Authoritative publication and status resolution

Verifiers MUST resolve the bound policy digest through a configured policy registry or an offline signed snapshot anchored in a relying-party trust store; they MUST NOT trust a prover-supplied policy description, state, URL, issuer key, compatibility assertion, or “latest” pointer. A prover may transport the exact policy bytes and signed evidence as untrusted convenience data, but the verifier recomputes the digest and validates it against independently configured issuer, approval, and status trust anchors.

The publisher MUST provide immutable policy bytes by digest plus an append-only, monotonically ordered signed status log containing approvals, activations, deprecations, revocations, expirations/sunsets, rollbacks, issuer/authority authorization changes, sequence numbers, and publication times. Manifests and snapshots MUST be canonically encoded, signed with an authorized publication key, protected against rollback/freeze by sequence or checkpoint continuity, and distributable through authenticated channels. Publication signatures authenticate artifacts; they do not substitute for approval-authority signatures. Key rotation and revocation evidence MUST remain available for historical validation.

A verifier cache MUST be keyed by digest and registry/trust domain, retain the signed status evidence and last verified sequence/checkpoint, enforce a configured maximum status age, and never replace newer status with older data. Cached immutable policy bytes may be used indefinitely for digest reconstruction, but cached status may authorize a decision only while its freshness bound is satisfied and no required log continuity is missing. During a registry outage, a fresh complete cache or approved offline snapshot MAY be used and the result records its checkpoint and age; absent, stale, conflicting, or unverifiable status yields `temporarily_unverifiable` and never `valid`. Revocation-sensitive profiles MAY require an online or shorter-lived status check.

Every decision MUST audit the policy digest/revision, resolved state, issuer and approval-authority identifiers, approval/status/publication signature and key identifiers, effective window, compatibility result, registry or snapshot identity, status sequence/checkpoint and fetch time/cache age, authenticated decision time, rollback/supersession chain, revocation check/result, verifier version, outcome, and non-sensitive reason code. Audit records are append-only, integrity protected, access controlled, and retained according to the approved retention schedule without witness, exact telemetry, or other restricted data.

## Recency, replay, and limitations

A timestamp alone does not prove recency. Until trustworthy time attestation exists, the verifier applies an external policy using a named clock authority, maximum skew, the half-open accepted window, sequence evidence, and durable nullifier uniqueness. Skew may affect the currency calculation but MUST NOT change which endpoint is inclusive. The tolerance values and handling of resets/reordering are **Open** and owned by security.

MAVLink signing, if validated and provisioned, authenticates protocol frames; it does not validate sensors. UDP provides neither confidentiality nor reliable delivery. A chain may timestamp and durably order submission metadata; it does not authenticate the original reading.

## Data classification and lifecycle

Classification and retention controls are authoritative in [security and privacy](security-and-privacy.md). Witness and opening material MUST be released after proving and never logged. Exact position is not required by the first speed statement and MUST NOT become a public input. Hashing stable identity is pseudonymization, not anonymization.

Schema, circuit, policy, proving/verifying key, commitment, nullifier, and domain versions require compatibility rules and migration/revocation procedures before persistence or live-chain work. The tier and nullifier registries remain Proposed until explicit product/privacy and security approval and an ADR cover their freeze. Key-generation/setup assumptions depend on the selected proof system and remain **Open**.

## Acceptance and related documents

Acceptance requires reviewed golden vectors; circuit boundary/overflow/altered-input tests; an independent verifier without witness access; replay, wrong-policy, wrong-domain, and unsupported-version rejection; and benchmark evidence identifying hardware and parameters. The [claim envelope specification](claim-envelope.md) owns the canonical public exchange format and verifier outcomes. [Architecture](architecture.md) owns component flow, [security and privacy](security-and-privacy.md) owns eligibility and handling controls, and [decisions](decisions.md) owns closure evidence.
