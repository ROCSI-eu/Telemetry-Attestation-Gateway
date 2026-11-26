# Commercial model

| Metadata | Value |
| --- | --- |
| Status | Proposed product and packaging policy |
| Audience | Product, community, engineering, security, partners, and customers |
| Accountable role | Product owner |
| Review trigger | Change to licensing, packaging, interoperability, hosted services, or edition compatibility |
| Authority | Normative for the boundary between independently usable community capabilities and optional commercial services |

## Purpose and commercial principle

The project uses an open-core model in which the complete standard proof path remains open, inspectable, and independently usable. Commercial value may be created by operating, integrating, governing, and supporting that path at organizational scale; it must not come from making a proprietary service necessary to understand, produce, or verify a standard proof.

“Open” in this document is a **project governance promise**: material is to be available under the repository's open-source licensing with sufficient source, schemas, documentation, keys, and tests to use it without an account, network call, commercial credential, or managed control plane. A downstream recipient's legal obligations come only from the license actually applicable to a file and applicable third-party terms; this policy is not a substitute copyright license.

**Current effective licensing:** all project-authored contents remain under the root MIT license. MIT permits closed redistribution of modified core files, so it does not itself enforce every openness promise below. **Proposed, not approved or effective:** [ADR-0003](adr/0003-layered-licensing-model-for-the-open-proof-path.md) would apply MPL-2.0 to standard proof-path machine artifacts (including verifier/prover and local tooling, circuits, schemas, adapters, scripts, workflows, build inputs, and conformance tooling), CC-BY-4.0 to documentation, specifications, diagrams, and governance, and CC0-1.0 only to explicitly designated synthetic fixtures and vectors. The root [`LICENSING.md`](../LICENSING.md) records path rules and unmet gates. Third-party terms still require review, and no future separately authored commercial component is pre-licensed.

## Capabilities that must remain open

The following form the portable interoperability floor and **MUST** remain open, versioned, documented, and independently usable:

- **Claim specifications:** the predicate, units, boundary behavior, public inputs, private witness, assurance semantics, time and replay fields, failure conditions, and version-identification rules for every standard claim.
- **Circuits and build inputs:** circuit source, constraints, reproducible build instructions, and the information required to associate circuit and proving-system versions with verification material. A standard claim must not depend on an undisclosed constraint or proprietary circuit variant.
- **Proof verification:** a local verifier and the verification keys or deterministic retrieval rules needed to validate supported standard proofs offline. Verification must expose the normative typed result dimensions and precedence, preserving cryptographic validity independently from policy, freshness, revocation, replay, assurance, publication, and external business decisions.
- **Canonical encodings:** normative schemas, field ordering, integer widths, endianness, domain separators, hashing rules, normalization rules, and versioning behavior for claims, policies, public inputs, proofs, and verification results.
- **Synthetic fixtures and vectors:** non-sensitive positive, boundary, malformed, and negative examples sufficient to reproduce proof generation and verification and to detect incompatible encodings or circuit behavior.
- **Local CLI or SDK:** at least one maintained, scriptable implementation that can normalize supported synthetic inputs, create a standard proof, and verify it locally without a hosted account. Its interfaces must be adequate for CI and third-party integration, not merely a demonstration UI.
- **Adapter contract tests:** a reusable conformance suite for telemetry, policy, verifier, and publication adapters, including deterministic mock implementations. Third parties must be able to implement an adapter and establish compatibility without access to proprietary infrastructure.

These artifacts must be usable together as a complete local path. Publishing isolated source files while withholding required schemas, keys, build steps, fixtures, or test harnesses does not satisfy this boundary.

## Optional commercial capabilities

MPL's proposed file boundary would permit proprietary larger works, enterprise control planes, integrations, operational tooling, and managed services around the independently usable open path. Hosted operation alone would not trigger AGPL-style source disclosure under this proposal. That permission must not weaken the governance floor: managed services cannot become proof authority; security fixes affecting proof soundness or canonical interpretation remain in open artifacts; and the open verifier, circuits, schemas, keys, fixtures, and local path remain sufficient without a vendor account.

Commercial-offering exploration follows the staged [commercial offering discovery decision](decisions.md#commercial-offering-discovery-decision). Its smallest initial offer is a workflow/assurance assessment plus an offline verification pilot using synthetic positive and negative packages. The assessment may occur during earlier discovery, but the pilot MUST NOT begin until a versioned offline package exists and every evidence item and required review for [commercial evidence and Gate E](product-scope.md#commercial-evidence-ce-for-pilot-promotion) has been satisfied; synthetic packages do not waive or satisfy those controls. Before then, discovery and synthetic reversible experiments may proceed only within their applicable exploration boundaries. Later differentiation proceeds through consulting/integration, supported customer-managed deployment, enterprise support and upgrade validation, and only then managed verification or policy operations after repeated evidence-backed demand. That sequence is for discovery, not evidence of demand, a selected price, a managed-service commitment, or a license decision.

Commercial community support, self-hosted enterprise packages, and managed services may add capabilities that reduce operational burden or meet organizational requirements, including:

- hosted policy authoring, approval workflows, distribution, version history, and revocation management;
- tenant isolation, organization and project boundaries, quotas, delegated administration, and billing controls;
- managed verifier APIs, autoscaling, caching, rate limiting, health reporting, and authenticated batch processing;
- durable replay protection and coordinated nonce or nullifier state across processes, regions, and recovery events;
- identity-provider integration, including SSO, federation, directory synchronization, role mapping, and lifecycle automation;
- configurable audit exports and connectors for customer-controlled object stores, SIEM systems, compliance workflows, or evidence archives;
- regional deployment, data-residency controls, private networking, customer-managed keys, and managed disaster recovery;
- operational support, implementation assistance, upgrade planning, incident coordination, and validated deployment guidance; and
- measured service objectives for availability, latency, support response, recovery, retention, and capacity, backed by commercial terms where offered.

These features may be proprietary because they operate or administer the open proof path rather than redefine it. Their security, privacy, retention, and assurance claims must remain explicit. Service objectives are commitments of a particular offering, not properties of the proof protocol or defaults for the proposed MVP.

## Repository boundary and GCS reference integration

Owner-endorsed direction, 2026-11-26 (planning only): retain the existing public repository as the canonical research and open proof-path repository. Continue the synthetic reference integrations with QGroundControl and Mission Planner, the shared standard TAG core, local CLI/SDK, verifier, schemas, fixtures, conformance tests and reproducible local demonstrator in that repository. Do not fork either GCS merely to integrate TAG. Publication of integration code does not imply supported interoperability or authorize real telemetry, hardware or external evaluation.

Defer a separate private commercial implementation repository until a concrete proprietary capability, customer need and ownership boundary justify it. Its name, license, interfaces and support scope remain unselected. Future private modules may consume versioned public interfaces and add organization-specific integrations, administration or managed operations; they must not make proprietary software or a hosted account necessary to produce or independently verify standard proofs, nor move existing open capabilities behind a paid boundary. Keep customer-specific confidential material, credentials, contracts and negotiations in separately approved private systems, never in the public repository. Private repository creation, licensing changes, commercial release and promotion are separately authorized decisions.

The existing MIT license remains effective; ADR-0003 is Proposed and its prerequisites remain unchanged. This direction confirms the existing open-core policy; it is not acceptance of an implementation technology, commercial demand, a pricing decision or an artifact promotion.

## Independence and anti-lock-in rules

Commercial packaging **MUST** preserve all of the following principles:

1. A relying party can verify any standard proof locally using open artifacts and public verification material; a managed API is a convenience, not an authority.
2. Standard proof validity cannot depend on a vendor account, license server, undisclosed allowlist, proprietary identity assertion, billing state, or successful connection to a hosted service.
3. Managed services may add authenticated envelopes, policy approvals, timestamps, replay decisions, audit records, or service attestations, but these must use the standard typed dimensions and remain separable from cryptographic evaluation. An aggregate service disposition is derived convenience data. The cryptographic verifier never returns the customer’s business decision.
4. Vendor-specific metadata must use namespaced, optional extensions. It must not change the meaning or canonical encoding of a standard field, and an implementation that does not understand it must still be able to verify the standard proof when safe to do so.
5. Verification keys, circuit identifiers, schemas, and compatibility data required for previously issued standard proofs must remain available under a documented lifecycle policy. Ending a hosted product must not make retained standard proofs unverifiable.
6. Customers can export standard proofs, public inputs, policies needed to interpret them, replay/audit state they are entitled to retain, and configuration in documented formats. Export must not require the destination verifier to use the managed edition.
7. No proprietary policy language may be the only way to express a standard claim. A managed policy may impose additional organizational acceptance rules, but the standard predicate and public inputs remain portable.
8. Security fixes that affect standard proof soundness, canonical interpretation, or conformance belong in the open artifacts. A paid tier must not be the only edition capable of correctly verifying a supported standard proof.

These are governance constraints on what the project will publish and support, not a claim that MIT currently imposes equivalent duties on every downstream recipient. If the layered proposal is adopted, MPL duties attach to covered files when distributed, not merely because a service is hosted. Publication remains separate from verification, and verification remains separate from a relying party's business decision.

## Community and managed edition compatibility

The community implementation defines the interoperability floor; the claim specification and canonical test vectors, rather than either edition's incidental behavior, define the wire contract.

| Expectation | Required behavior |
| --- | --- |
| Standard proof portability | A standard proof produced by either edition verifies in every conformant verifier that supports its declared claim, circuit, encoding, and proving-system versions. |
| Managed production | Managed services produce the same standard proof envelope and canonical public inputs, except for explicitly namespaced optional metadata. |
| Community production | Managed verification accepts conformant community-produced proofs without requiring that they were created through a vendor account or hosted policy service. Organizational policy may reject them only with a distinct, explainable policy result. |
| Version negotiation | Both editions publish supported versions and return explicit unsupported-version errors. Silent reinterpretation, coercion, or downgrade is prohibited. |
| Conformance | Both editions run the same open fixtures and adapter contract tests for shared behavior. Managed-only tests may cover operations, isolation, or integrations but cannot replace shared conformance tests. |
| Release compatibility | Additive optional fields require documented handling; breaking canonical, claim, circuit, or adapter changes require a new version and migration guidance. |
| Deprecation | Deprecation announces affected versions, timelines, replacement paths, and verification-material retention. Managed services must not withdraw support earlier than their published commitments. |
| Result semantics | Editions expose identical typed cryptographic, policy, freshness, revocation, replay, assurance, and optional publication dimensions and precedence. A derived service disposition is not a proof result; a relying-party business decision is external and never verifier-produced. |

Feature parity is not required: managed editions may provide better scale, availability, administration, integrations, and support. Interoperability parity is required for every capability described as a standard claim or standard proof. Proprietary claim types must be labeled as extensions and must not be represented as community-standard compatible until their specifications, verification path, encodings, and conformance material meet the open boundary above.

## Governance and validation

A change that moves an existing open capability behind a commercial boundary, alters standard proof portability, or creates a managed-only dependency requires product, architecture, cryptography, and community review plus an accepted ADR. The review must include an offline verification demonstration, cross-edition conformance results, export/exit analysis, and an inventory of proprietary extensions.

The existing MIT license MUST NOT be changed without a separately stated business objective, legal review, community-impact analysis, dependency review, and an accepted ADR recording the decision and its consequences. Commercial discovery or interest in proprietary future components is not, by itself, a license-change decision.

Release acceptance requires testing both directions: community-produced proof to managed verifier, and managed-produced proof to community verifier. It also requires proving that the documented local CLI or SDK completes the standard fixture path with hosted endpoints disabled.

This model inherits the product boundaries in [product scope](product-scope.md), the proof semantics in [data and proof model](data-and-proof-model.md), component boundaries in [architecture](architecture.md), security controls in [security and privacy](security-and-privacy.md), and evidence requirements in [testing and operations](testing-and-operations.md). Where a commercial feature changes a normative protocol decision, the [decision register](decisions.md) records the accountable decision and migration consequences.
