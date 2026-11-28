# Claim envelope specification

| Metadata | Value |
| --- | --- |
| Status | Pre-standard executable draft; not a released compatibility contract |
| Audience | Prover, verifier, relying-party, policy, ledger, and interoperability implementers |
| Accountable role | Cryptography lead, with security and protocol-owner approval |
| Review trigger | Envelope, encoding, proof suite, policy, key, revocation, disclosure, replay, or receipt change |
| Authority | Normative wire contract and verifier result model |

Until the Phase 0 executable spike gate is passed and a release ADR is accepted, the field numbers and names, canonical profile, proof attachment rules, and outcome schema in this draft are subject to incompatible change. They are not released compatibility commitments. Passing requires the specified vectors and independent codecs to demonstrate strict decoding, deterministic re-encoding, public-input reconstruction, mutation rejection, and cross-language agreement. The `[1, 0]` value and `v=1` media-type parameter below identify the current draft for testing; they do not by themselves promote it to a released version.

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHOULD**, **SHOULD NOT**, and **MAY** are to be interpreted as normative requirements. An envelope conveys a privacy-preserving claim and the material needed to evaluate it; it is not evidence that the underlying sensor was truthful.

## Provisional scalar exploration profile

The [proposed bounded synthetic scalar profile](adr/0004-proposed-synthetic-scalar-claim-profile.md) reconciles existing experimental v0 evidence with this draft. Its integer-key CBOR and scalar cryptographic result are not version 1 conformance, a frozen contract, or an accepted registry entry. All normative v1 fields, checks and review requirements below remain unchanged.

## Version and canonical serialization

An envelope version is the two-element unsigned-integer array `[major, minor]`. This specification defines `[1, 0]`. A major version changes field meaning or canonical encoding. A minor version may only add optional fields whose absence preserves meaning. A verifier MUST reject an unknown major version as `unsupported`. It MAY process a newer minor version only when it recognizes every present field and the applicable policy explicitly permits that minor version; otherwise it returns `unsupported`. The version is independent of telemetry-schema, statement, proof-suite, policy, and key versions.

The normative wire representation is deterministic CBOR as specified by RFC 8949 section 4.2, with the following profile:

- the top-level value and every structured child are maps with the exact text-string keys defined below;
- map keys are compared and ordered by their deterministic CBOR encodings; duplicate or unknown keys are forbidden;
- integers use the shortest encoding; indefinite-length items, floating-point values, tags, and CBOR `null` are forbidden;
- text is valid UTF-8 and in Unicode NFC; identifiers use the restricted ASCII syntax stated below;
- byte strings have the exact lengths required by their registered algorithm; and
- an optional field is omitted, never encoded with a sentinel value.

The media type is `application/vnd.mavlink-zkp.claim-envelope+cbor;v=1`. A transport using base64url MUST use the unpadded RFC 4648 URL-safe alphabet and is only a transport wrapper; implementations MUST decode it to bytes before canonicality checks. JSON MAY be emitted as a diagnostic view with media type `application/vnd.mavlink-zkp.claim-envelope+json;v=1`, but it is non-canonical and MUST NOT be hashed, signed, committed, or accepted as the verification wire form.

Canonicality is verified by strict decode, schema validation, deterministic re-encoding, and byte-for-byte comparison with the received CBOR. Failure at any step is `malformed`.

## Envelope fields

All identifier strings (`statement_id`, `proof_suite`, `domain`, and URI-like identifiers) are case-sensitive ASCII, 1–255 bytes, and MUST NOT contain whitespace or control characters. Digest and identifier byte strings are raw bytes rather than hexadecimal or base64 text. Bounds below are inclusive.

| Field | Type | Required | Normative meaning |
| --- | --- | --- | --- |
| `envelope_version` | `[uint, uint]` | Yes | Envelope major and minor version; exactly `[1, 0]` here. |
| `statement_id` | text | Yes | Registered statement and statement-version identifier defining the proved predicate and ordered public-input mapping. For the first statement this identifies the speed-at-or-below-policy-bound predicate. |
| `proof_suite` | text | Yes | Registered proof system, transcript, curve/field, hash, commitment, nullifier, and public-input encoding profile. No algorithm defaults are permitted. |
| `assurance_tier` | uint `0..255` | Yes | Registered assurance tier. Version 1 permits only `0..5` with the canonical mapping below. It is a claim input, not a verifier-computed score; a verifier MUST confirm that policy permits it. |
| `policy_ref` | map | Yes | Exactly `{"id": text, "version": uint, "digest": bstr}`. `digest` is over the canonical policy artifact using the suite's registered digest algorithm. |
| `validity` | map | Yes | Exactly `{"not_before": uint, "not_after": uint}` in Unix epoch seconds. Version 1 uses the non-empty half-open interval `[not_before, not_after)`: `not_before < not_after`, `not_before` is inclusive, and `not_after` is exclusive. |
| `domain` | text | Yes | Relying-party/deployment context. It MUST be an input to the statement or a suite-defined domain-bound public-input digest. Exact string comparison is required; redirects, aliases, and case folding are forbidden. |
| `commitment` | bstr | Yes | Suite-sized commitment to the private record and all interpretation-critical fields required by the statement specification. |
| `nullifier` | bstr | Yes | Suite-sized, domain-separated replay identifier binding at least the domain, policy, source pseudonym, and record nonce. |
| `verification_key_id` | map | Yes | Exactly `{"id": text, "version": uint, "digest": bstr}`; identifies and integrity-binds one authenticated verification-key artifact. |
| `public_inputs` | map | Yes | The exact allowlisted, typed public values required by `statement_id`, excluding values already represented by canonical envelope fields. Unknown inputs are forbidden. |
| `proof` | map | Yes | Exactly one proof form defined below. |
| `ledger_receipt` | map | No | Optional receipt defined below; it does not change cryptographic proof validity. |

The version 1 numeric-to-string mapping is one-to-one and canonical: `0` = `A0_SYNTHETIC`, `1` = `A1_UNSIGNED_SOFTWARE`, `2` = `A2_PROTOCOL_SIGNED`, `3` = `A3_APPROVED_GATEWAY_ATTESTED`, `4` = `A4_HARDWARE_BACKED_DEVICE`, and `5` = `A5_INDEPENDENTLY_CORROBORATED`. Values `6..255` are reserved and `unsupported`; aliases, case folding, and policy-local renumbering are forbidden. The envelope carries only the numeric value. APIs, results, displays, exports, and audit records MUST derive and show the exact string ID from this mapping, MUST reject a supplied inconsistent pair, and MUST NOT treat numeric order alone as evidence that a tier was established. `A5` additionally binds its primary tier as a registered committed fact or selectively disclosed public input, as the statement profile specifies.

The canonical public-input sequence is the registered `statement_id` sequence. It MUST include, directly or through a registered suite-defined digest, the statement/schema and circuit identifiers, policy digest, validity window, domain, commitment, nullifier, verification-key identifier, assurance tier, and statement-specific public values. A verifier MUST reconstruct that sequence from the envelope and MUST NOT trust a separately supplied public-input byte array.

### Proof attachment and reference

`proof` is exactly one of:

- attached: `{"kind": "attached", "content_type": text, "bytes": bstr}`; or
- referenced: `{"kind": "referenced", "content_type": text, "uri": text, "digest": bstr, "size": uint}`.

`content_type` MUST be the registered, versioned media type for `proof_suite`. An attached proof's size is bounded by the suite registry and policy. For a referenced proof, `digest` covers the exact retrieved bytes, `size` is their exact byte length, and both MUST be checked before parsing. Fetching MUST follow verifier policy for scheme, host, redirects, size, timeout, and authentication. A reference MUST NOT embed credentials. Fetch failure, timeout, or an unavailable but otherwise permitted dependency produces `temporarily_unverifiable`; a forbidden reference, digest/size mismatch, or proof parse failure produces `invalid`. Verifiers MUST NOT silently change between attached and referenced material or treat the URI as proof identity.

### Optional ledger receipt

When present, `ledger_receipt` is exactly `{"ledger_id": text, "transaction_id": text, "recorded_at": uint, "payload_digest": bstr, "finality": text, "proof": bstr}`. The registered ledger profile defines canonical transaction identifiers, the digest algorithm, `finality` values, and receipt-proof verification. `payload_digest` MUST bind the canonical envelope with `ledger_receipt` omitted, preventing recursion. A receipt is corroborating submission/order evidence only: it neither repairs an invalid claim nor establishes sensor truth, freshness before submission, or proof validity. Receipt verification and finality are reported only in the publication dimension. A policy that requires publication evaluates that dimension when deriving `policy_acceptance`; it MUST NOT rewrite `envelope_evaluation`. In particular, an absent or unavailable optional publication service never changes a cryptographically `valid` envelope into `invalid` or any other cryptographic value.

## Public disclosure and binding rules

The canonical envelope is public-disclosure material. Producers MUST use an explicit, reviewed allowlist per `(envelope major, statement_id, proof_suite, assurance_tier)` and MUST disclose only fields in this specification and the selected statement's `public_inputs`. Private witnesses, commitment openings, source identifiers or stable pseudonyms, record nonces, salts, raw telemetry, exact position, signing keys, and linkable operational metadata MUST NOT appear anywhere in an envelope, URI, receipt, or extension. Hashing or encrypting a disallowed stable identifier does not make it permitted.

A source pseudonym is always a private commitment input; it is never a public value, even when domain-scoped or hashed. A key identifier is normally a verifier trust-store lookup or a committed fact. It MAY be a public value only when independent verification cannot select the authenticated artifact without it, the statement/policy allowlist requires it, and it is an opaque, domain-scoped identifier rotated at least at the policy-defined unlinkability epoch. It MUST NOT encode or deterministically derive from a device, owner, certificate subject, stable public key, or cross-domain account; rotation mappings remain restricted. `verification_key_id` identifies the proof verification key, not a telemetry source key, and does not authorize exposing a source identity.

The nullifier is a pseudorandom output, not a public identity: its registered construction MUST bind the private source-pseudonym commitment (not the pseudonym value), a fresh high-entropy private record nonce, `domain`, `policy_ref.digest`, `statement_id`, and a nullifier version/domain-separation tag. Only the output is public. Reuse of a record nonce with the same source commitment is forbidden. The nonce and source commitment opening remain private, and the construction MUST be computationally unlinkable across different nonces, domains, policies, and statements except for the intentional equality revealed by replaying the same scoped claim. A suite that produces a stable per-source output or permits dictionary testing of source identities is non-conformant. Durable replay storage is scoped by the same domain, policy, and statement and MUST NOT create a cross-scope identity index.

Policy artifacts MUST state the permitted statement and suite versions, assurance tiers, public-input names and bounds, validity duration and clock/skew rules, accepted domains, key status, revocation source/freshness, nullifier retention scope, proof-reference rules, and any ledger requirement. Clock/skew rules MUST NOT reinterpret version 1's endpoint inclusivity: any tolerance is an explicit, independently tested input to the currency calculation. A relying party that requires different endpoint semantics needs a reviewed, versioned contract that cannot be represented by reinterpreting a version 1 envelope. Envelope `policy_ref.digest` and `verification_key_id.digest` MUST be compared in constant time after length validation. A policy or key selected only by a mutable name is insufficient.

Before proof verification, the verifier MUST authenticate and integrity-check the referenced policy, verification key, suite parameters, and revocation state. It MUST evaluate at an explicit integer `decision_time` from its configured clock authority. Subject to the policy's explicit skew calculation, an envelope is current exactly when `not_before <= decision_time < not_after`: equality at `not_before` is current and equality at `not_after` is expired. Nullifier uniqueness MUST be checked and recorded atomically in a durable store scoped by domain, policy, and statement. A nullifier is recorded only after all required checks succeed; concurrent attempts MUST yield at most one `replay=accepted` result.

## Typed verifier result model

This section defines the public verifier-result contract. A verifier returns the following independent, typed dimensions, non-sensitive reason codes, and evaluated facts (including `decision_time`, authenticated artifact digests, and snapshot identifiers). It MUST NOT expose witnesses or secrets. Every dimension is deterministic for the same envelope and authenticated policy, keys, revocation snapshot, replay state, decision time, and dependency results.

A result MUST contain `envelope_evaluation`, `policy_acceptance`, `freshness`, `revocation`, `replay`, and `assurance`. It MUST contain `publication` when a receipt is present, publication is required by policy, or publication was attempted. `service_disposition` MAY be emitted only as the derived convenience value defined below. A verifier result MUST NOT contain a relying-party business decision.

### Envelope and cryptographic evaluation

`envelope_evaluation` has exactly one value:

| Value | Meaning |
| --- | --- |
| `malformed` | Bytes fail canonical decoding or the structural schema, types, lengths, ranges, required/exclusive-field, UTF-8/NFC, or unknown-field rules. No network lookup or proof verification SHOULD occur. |
| `unsupported` | The canonical envelope uses an unsupported envelope/statement/suite version, registered algorithm, content type, or optional cryptographic feature. |
| `invalid` | A supported, well-formed envelope fails proof parsing or verification, canonical public-input reconstruction, commitment/nullifier binding, domain separation, or policy/key identifier binding. |
| `temporarily_unverifiable` | A proof reference or authenticated cryptographic artifact required to finish this evaluation is transiently unavailable and no definitive negative is known. |
| `valid` | Canonical/schema, version, binding, authenticated cryptographic-artifact, and proof checks pass. This says nothing about current policy acceptance, freshness, revocation, replay, assurance sufficiency, publication, or a business decision. |

If more than one condition is observed, precedence is `malformed` > `unsupported` > `invalid` > `temporarily_unverifiable` > `valid`. Verifiers MUST perform safe local checks first and MUST NOT fetch attacker-selected resources before structural, version, domain, and policy-reference checks.

### Acceptance dimensions

Each acceptance dimension has its own closed value set and precedence. A lower-precedence positive value MUST NOT hide a higher-precedence failure or indeterminate value.

| Dimension | Values in highest-to-lowest precedence | Normative rule |
| --- | --- | --- |
| `policy_acceptance` | `rejected` > `temporarily_unverifiable` > `accepted` | `rejected` covers a locally decidable violation of the authenticated policy, including disclosure, domain, version combination, required-publication, or other eligibility rules. Missing/stale authenticated policy material is `temporarily_unverifiable`. Proof validity never overrides rejection. |
| `freshness` | `not_yet_valid` > `expired` > `temporarily_unverifiable` > `current` | Before `not_before` is `not_yet_valid`; at or after `not_after`, or outside an explicit maximum-age/skew rule, is `expired`; missing trustworthy clock state is `temporarily_unverifiable`; otherwise it is `current`. If inconsistent clock facts make both temporal negatives observable, `not_yet_valid` takes precedence and a diagnostic MUST record the inconsistency. |
| `revocation` | `revoked` > `temporarily_unverifiable` > `not_revoked` | Any applicable revoked policy, key, suite/parameters, issuer authorization, or required publication trust anchor is `revoked`. Missing or stale required revocation evidence is `temporarily_unverifiable`; otherwise it is `not_revoked`. |
| `replay` | `replayed` > `temporarily_unverifiable` > `accepted` | An already accepted nullifier, including the losing concurrent submission, is `replayed`. Unavailable durable replay state is `temporarily_unverifiable`; otherwise atomic insertion yields `accepted`. |

Replay insertion MUST occur only when `envelope_evaluation=valid`, policy/freshness/revocation are positive, and assurance is sufficient. Concurrent attempts MUST yield at most one `replay=accepted`. This ordering avoids consuming a nullifier for evidence that could not otherwise be accepted.

### Assurance dimension

`assurance` is exactly `{"declared_tier": uint, "effective_tier": uint / "unavailable", "tier_sufficiency": text}`. `declared_tier` repeats the bound envelope claim and is never described as verifier-computed. `effective_tier` is the highest tier justified by authenticated source, policy, key, and attestation evidence under the applicable assurance registry; it MUST be `unavailable` when that evidence cannot be authenticated or evaluated. It MUST NOT exceed `declared_tier`.

`tier_sufficiency` has precedence `insufficient` > `temporarily_unverifiable` > `sufficient`. It is `insufficient` when a known effective tier is below the policy-required tier or the declared tier is disallowed; `temporarily_unverifiable` when the effective tier or requirement cannot be determined; otherwise it is `sufficient`. A cryptographically valid proof can therefore carry insufficient assurance without becoming cryptographically invalid.

### Optional publication dimension

`publication` is exactly `{"requirement": text, "receipt_verification": text, "finality": text}`:

- `requirement` is `optional` or `required` according to authenticated policy;
- `receipt_verification` precedence is `invalid` > `temporarily_unverifiable` > `valid` > `not_present`; and
- `finality` precedence is `failed` > `temporarily_unverifiable` > `pending` > `final` > `not_applicable`.

A malformed, inconsistent, or cryptographically bad receipt is `receipt_verification=invalid`. A dependency outage is `temporarily_unverifiable`; a verified receipt is `valid`; absence is `not_present`. Finality is `not_applicable` without a verified receipt or when the ledger profile has no finality concept, `pending` before the required level, `final` at that level, `failed` for a definitive reorganization/rejection, and `temporarily_unverifiable` when finality cannot currently be established. Receipt validity and finality do not establish envelope validity. Most importantly, unavailable optional publication MUST leave `envelope_evaluation` unchanged and cannot by itself prevent acceptance; when publication is required, its negative or indeterminate state is reflected in `policy_acceptance` and the derived disposition.

### Derived service disposition

A service MAY expose `service_disposition` for routing or legacy clients, but it is not the proof result and MUST be recomputed solely from the typed dimensions. It has the following cross-dimension precedence:

1. `malformed`, `unsupported`, `cryptographically_invalid`, or `temporarily_unverifiable`, corresponding to the non-`valid` `envelope_evaluation` value;
2. `rejected` if policy is `rejected`, freshness is `not_yet_valid`/`expired`, revocation is `revoked`, replay is `replayed`, assurance is `insufficient`, or required publication is definitively unsatisfied;
3. `temporarily_unverifiable` if any required acceptance, assurance, replay, or publication check is `temporarily_unverifiable`;
4. `accepted` only when the envelope is valid, every required acceptance dimension is positive, assurance is sufficient, and required publication (if any) is verified at required finality.

Optional publication values, including `invalid`, `failed`, `pending`, `temporarily_unverifiable`, and `not_present`, are diagnostic only and MUST be ignored when deriving disposition. Reason codes identify every contributing dimension rather than collapsing them into the convenience value. No value, including `accepted`, authorizes an action.

### External relying-party business decision

Whether to accept a deliverable, make a payment, open a gate, initiate an investigation, or take any other business action is an explicitly external relying-party decision. It may consider the verifier result alongside contracts, identity, operational evidence, risk tolerance, and human review. The cryptographic verifier MUST NOT produce, infer, default, or serialize that decision. If an application records it, the record MUST use a separate schema, authority, timestamp, and audit trail and MUST preserve the complete verifier result it considered. Thus `envelope_evaluation=valid` and even `service_disposition=accepted` can coexist with an external `business_decision=rejected`.

## Registries and conformance

The project MUST maintain reviewed registries for statement identifiers, proof suites and media types, digest lengths, canonical public-input order and encoding, verification-key identifiers, assurance tiers, policy schemas, and ledger profiles. Registry entries are immutable; changes receive new identifiers or versions. Removing support requires an announced migration and revocation/retention plan. The assurance-tier mapping/semantics and nullifier construction registry MUST NOT be frozen or declared stable until an ADR records alternatives, linkage analysis, migration consequences, and validation evidence and receives explicit product/privacy and security approval.

An implementation is conformant only if it passes the golden-vector and independent cross-implementation requirements in [testing and operations](testing-and-operations.md#claim-envelope-interoperability).
