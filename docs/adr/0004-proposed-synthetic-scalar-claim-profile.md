# ADR-0004 (Proposed): bounded synthetic scalar claim profile

| Metadata | Value |
| --- | --- |
| Status | Proposed; local-only draft, not accepted or frozen |
| Accountable role | Product and architecture owners; cryptography lead for wire semantics |
| Review trigger | Scope, encoding, trust, disclosure, version or destination changes |
| Authority | Proposal under [delivery plan](../delivery-plan.md); [claim envelope](../claim-envelope.md) remains normative for draft v1 |
| Classification | Concept only / No execution evidence (reuses scoped experimental evidence) / Unreviewed / Public documentation / Documentation-only / No external assurance claim |
| Activity | Exploration permitted |

**EXPERIMENTAL / SYNTHETIC_ONLY / A0_SYNTHETIC / NOT VALIDATION OR PRODUCTION AUTHORIZATION**

## Context and proposed decision

The maintainer selected a provisional technical direction on 2026-11-28: one synthetic scalar observation, not commercial or continuous-coverage evidence. This does not select a product claim for industrial inspection, close Gate A, accept a proof system, or authorize release. [Product scope](../product-scope.md) retains its reopened workflow selection. A hypothetical technical relying party checks whether a synthetic evidence item demonstrates the selected mathematical predicate; no contract, payment, flight or safety decision follows.

Use the existing bounded-speed-v0 as the first experimental profile, not as the normative envelope v1. For a synthetic integer witness s and public integer M, both uint32 in cm/s, the proof asserts knowledge of a witness s satisfying s <= M under the reconstructed public inputs; equality passes. For the intended receive-only snapshot path, use GLOBAL_POSITION_INT.vx/vy (signed int16 cm/s, MAVLink2 pinned dialect) and ceiling of the Euclidean norm (integer arithmetic); VFR_HUD is diagnostic only. The scalar proof does NOT bind s to an observation/frame. A separate verified binding is necessary before claiming even synthetic observation attribution. Physical truth, trusted time, source identity, complete sampling, interval and mission coverage remain non-claims. Use only explicit test-fixture provenance and A0; UNSIGNED is eligible solely for explicitly selected synthetic fixture presentation; UNKNOWN, invalid signature, unavailable input and mixed sources do not become accepted observations. SIGNED_VALID with public test keys does not raise A0.

Alternatives: (1) adopt the full v1 draft immediately (more scope and unclosed registries); (2) widen to source-bound or aggregate claims (separate suites and materially different semantics); (3) retain v0 as a narrow experimental profile while reconciling a scoped v1 candidate (recommended). No v1 mandatory field or review is waived. No new stable identifier is registered by this draft.

## Wire, result and version contract

Current v0: deterministic CBOR integer keys 1 version=0, 2 domain=tag.bounded-speed.v0, 3 public maximum uint32, 4 statement=speed_cm_s<=maximum_speed_cm_s, 5 assurance=A0_SYNTHETIC. Reject noncanonical, unknown/missing, duplicate, wrong domain, trailing bytes, incompatible version and invalid range. Reconstruct version, maximum, SHA256 context (fixed domain/statement/assurance); proof input order is version u32, maximum u32, context high128 then low128. The existing pinned VK is an experimental integrity anchor, not authenticated production registry. Preserve the exact portable four-file package, release/profile/grant constraints and separate private evidence as in [Companion](../../experiments/companion-cli-v0/README.md).

Software 0.1.0-exp.4, bounded-speed-v0 and draft envelope [1,0] are separate versions. Do not silently convert numeric-key CBOR to the text-key envelope, reinterpret old proofs or accept unknown versions. Migration requires explicit mapping, newly reviewed binding and vectors; old v0 evidence remains historical in its own schema. No stable API or interoperability declaration.

Preserve [ADR-0001](0001-half-open-validity-windows.md) and [ADR-0002](0002-typed-verifier-result-model.md). Exp.4 VALID is scalar cryptographic acceptance, not canonical envelope_evaluation=valid. INVALID is cryptographic rejection, not an above-limit input or malformed package; UNVERIFIABLE means verification could not be established; NOT_CHECKED means no invocation. Package/input state, origin, verification mode and cryptographic result remain separate. Policy/freshness/revocation/replay/source trust/observation binding are NOT_EVALUATED; A0 is a demonstrator label, not sufficiency. Publication NOT_PERFORMED; decision NOT_MADE is experimental diagnostic only, never a business-decision field in v1. Do not infer service_disposition=accepted. Optional publication never rewrites crypto. Grant V2 single local consumption is not a claim nullifier.

For a future selected v1 profile preserve exact text-key canonical CBOR, statement/suite/version registry, numeric tier, policy/key digest authentication, explicit decision time and half-open validity, commitment and pseudorandom scoped nullifier, canonical ordered public inputs, proof attachment/reference and optional receipt semantics. No algorithm defaults, no caller-asserted trust and no conversion of retention expiry into claim freshness. Missing or stale required evidence fails closed. Freeze requires reviewed exact bound fields, encoding/field conversion, registry entries and migration; these remain Open. The proof-system benchmark/selection, licensing, setup and key lifecycle remain distinct decisions.

## Disclosure and GCS scenario

Proposed public allowlist (not yet reviewed or accepted): statement/version, public limit/unit, domain, A0, minimized typed result and non-sensitive reasons. Proof, VK and public artifact may be handled only as governed portable verification material, not public website/log by default. Keep exact speed, raw frames, coordinates, trajectory, exact private time, stable identities/pseudonyms or hashes, nonce/openings and source keys private. Future v1 policy/key references, validity, commitment, nullifier and proof fields need reviewed per-profile necessity and linkage analysis. Proof key identifier is not source identity.

Reuse [scalar fixtures](../../experiments/bounded-speed-v0/fixtures.json) below/equal/above 500 cm/s. For the proposed deterministic mapping, use vx=499, 500, 501 cm/s respectively and vy=0 in three fabricated primary frames, with test-only local observation ordinals; no assertion of timing or continuity. A common deterministic synthetic fixture manifest must identify matching observations for a derived offline GCS view and TAG normalization; exact values remain inside fixture boundary, view uses sample labels/public threshold and minimized outcomes. Below/equal SATISFIED, above NOT_SATISFIED (no invalid proof inferred); malformed/mixed/unknown/invalid signature rejected and missing verifier HOLD. Historical scalar VALID remains separate unless exact binding is independently established. The [SITL parity evidence](../../experiments/sitl-receive-v0/qube-parity-evidence-20261123.md) uses 600 cm/s, not this fixture; [GCS visual evidence](../../experiments/sitl-receive-v0/qa-gcs-companion-visual-20261126.md) is offline presentation, not shared live integration. Reuse common receive-only core, no native fork/plugin requirement, no TAG command path or real telemetry. QGC and GTK 02 HOLD; no launch in this mandate. Actual common-scenario acceptance and authentic application-specific media remain separate.

## Vector and implementation delta

The following is a source inventory, not newly executed QA. Reuse prior scope-matched PASS evidence only; no v0 or mock result counts as v1 conformance.

| Requirement | Existing source/evidence | Missing for selected v1 profile |
| --- | --- | --- |
| Integer predicate, bounds, equality | [scalar tests](../../experiments/bounded-speed-v0/test_bounded_speed.py), below/equal/above fixtures | Bind approved normalization and exact v1 statement to ordered inputs |
| Canonical encoding and mutations | Scalar tests: byte stability, unknown/duplicate keys, nonminimal integer, domain, trailing bytes, float; [verifier tests](../../experiments/bounded-speed-proof-v0/test_verify.py) reconstruct four inputs | Text-key v1 codec and golden bytes; required/unknown fields, UTF-8/NFC, tags/null/indefinite, version and cross-context mutations; independent lightweight checker |
| MAVLink normalization and source trust | [normalization tests](../../experiments/mavlink-normalization-v0/test_mavlink_normalize.py), prior SITL parity | Exact shared GCS fixture mapping; explicit source eligibility and no false proof attribution |
| Cryptographic integrity and unavailable dependencies | Scalar verifier tests (key pin, malformed artifact, missing proof, changed public limit); Companion exp.4 runtime acceptance (private, scoped) | v1 binding/commitment/nullifier and authenticated key/policy artifacts; proof reference digest/size cases; no new proof in this mandate |
| Freshness and authenticated inputs | [trusted-time tests](../../experiments/source-proof-binding-v0/test_trusted_time.py) and [binding evidence](../../experiments/source-proof-binding-v0/qa-evidence-20261124.md) | Explicit v1 decision time, both endpoints plus adjacent/skew/empty/inverted vectors; authenticated policy/status/revocation integration; stale or unavailable dependencies |
| Replay and lifecycle | [persistent tests](../../experiments/source-proof-binding-v0/test_persistent_unified.py), [Companion contracts](../../experiments/companion-cli-v0/test_contract.py) | Canonical nullifier construction and scope; nonce/domain/policy/statement/source changes; atomic concurrent replay; privacy/linkage review, not grant consumption |
| Result dimensions and precedence | [verifier tests](../../experiments/bounded-speed-proof-v0/test_verify.py), Companion artificial transport tests; [publication adapter tests](../../experiments/publication-adapter-v0/test_publication_adapter.py) | Exact v1 enums and every required precedence collision, optional/required receipt, assurance sufficiency and separately authored business rejection |
| Privacy and assurance | Scalar no-private-speed tests, minimized Companion output, source coverage [counterexample](../../experiments/source-proof-binding-v0/qa-physical-coverage-boundary-20261125.md) | Per-profile allowlist, reserved tiers/inconsistent mapping, committed-field binding, linkage and dictionary analysis; full tier privacy vectors as applicable to canonical release |

The [conformance plan](../testing-and-operations.md#claim-envelope-interoperability) requires a reference codec plus independently authored checker at spike stage. Two independent languages, released corpus, exchanged fresh proofs and compatibility matrix apply before stable public API/interoperability, not this draft. No tests are added or run by this proposal. Gate A requires reviewed positive, negative, boundary, mutation and incompatibility vectors for the exact selected profile; existing vectors are not blanket substitutes.

## Remaining decisions and implementation sequence

1. Review and approve the bounded statement, normalization, intended decision and disclosure; record exact scope without commercial promotion.
2. Specify the scoped v1 registry/binding/encoding and time, trust, replay and assurance model; decide how separate source-binding research is consumed, rather than relabeling scalar results. Review commitment/nullifier alternatives, unlinkability and migration. Existing ADRs remain authoritative.
3. Build only missing codec/vector/checker and result integration, with synthetic placeholder proofs where suitable; use exact existing suite evidence only where semantics match. No new proving or runtime authority inferred.
4. Obtain required named accountable reviews for implicated cryptography, security, privacy, telemetry, architecture, product and safety, accepted ADRs and synchronized owning docs/register. Solo planning/AI review is not promotion approval. Gate A remains OPEN; Gate B/D OPEN. Commercial WF and real assurance are not prerequisites for provisional exploration; they remain destination-gate requirements.

No promotion, public release, provisioning, CI, deployment or GitHub mutation authorized by this proposal.
