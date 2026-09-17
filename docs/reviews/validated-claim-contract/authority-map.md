# Validated claim contract authority map

| Record field | Value |
| --- | --- |
| Implementation state | Concept only |
| Evidence source | No execution evidence |
| Review independence | Maintainer-reviewed |
| Data class | Public documentation |
| Permitted environment | Documentation-only |
| External claim level | No external assurance claim |
| Activity | Exploration permitted within the Current work authorization |
| Work item | Documentation authority routing; historically created during `M1` reconciliation |
| Review date | 2026-08-30 |
| Status | **Current** routing map; prior M1 approval record and milestone-wide work holds **Superseded** |
| Accountable role | Repository maintainer at solo concept level; promoted uses require only their risk-triggered accountable roles |
| Applies to | Proposed downstream contracts, fixtures, tests, reviews, and decisions |
| Current work rule | [`docs/current-work-authorization.md`](../../current-work-authorization.md) and [`docs/delivery-plan.md`](../../delivery-plan.md) |

## Precedence rule

Authority is **area-specific**, not a single total ordering of whole files:

1. An accepted/Current ADR controls the decision it expressly makes and supersedes every conflicting Proposed or Open statement in its affected scope.
2. Within an area not decided by an accepted ADR, the owning document in the table below controls semantics.
3. `docs/delivery-plan.md` controls parallel delivery tracks, artifact dependencies, promotion gates, required evidence, and MVP declaration. Historical numbered-milestone records cannot create a repository-wide hold that conflicts with the Current exploration boundary.
4. `docs/testing-and-operations.md` controls how evidence is executed and assessed, but expected values come from the owning contract/accepted ADR.
5. `docs/decisions.md` controls whether a choice is Current, Proposed, Open, Deferred, or Superseded; descriptive repetition there does not replace the owning contract.
6. `docs/README.md` controls documentation governance and routing. `docs/system-plan.md` is Superseded and has no normative precedence.
7. Examples, diagrams, diagnostic JSON, candidates, plans, and proposed artifact paths cannot override normative prose. An unresolved Open value fails closed or waits for its closure gate; readers must not resolve it by document order.

This routing rule remains useful as Current documentation governance. It is not an approval record and does not itself promote any artifact or activity.

## Downstream contract-area map

| Contract area | Normative owner | Supporting/evidence documents | Accepted ADR precedence and conflict handling |
| --- | --- | --- | --- |
| Product problem, actors, relying-party decision, claim/coverage, MVP/non-goals, success measures | `docs/product-scope.md` | Discovery evidence from `docs/discovery-research-plan.md`; state in `docs/decisions.md`; gates in `docs/delivery-plan.md` | A scope-affecting ADR cannot silently change scope: product approval and synchronized scope update are also required. |
| Discovery protocol, privacy gate, sampling, collection, synthesis, evidence promotion | `docs/discovery-research-plan.md` | Product gate outcome in `docs/product-scope.md`; promotion timing and gates in `docs/delivery-plan.md` | An ADR may decide architecture, never manufacture findings or waive discovery evidence. |
| Delivery tracks, artifact dependencies, promotion gates, required reviewers/evidence, MVP declaration | `docs/delivery-plan.md` | Current work rule in `docs/current-work-authorization.md`; coordination state in `docs/management/validated-claim-contract-register.csv` | No topic ADR or historical milestone record can reorder or waive a delivery gate unless the delivery plan is amended through its owner. |
| Components, ports, dependency direction, trust/deployment boundaries, lifecycle flow | `docs/architecture.md` | Security controls and contract documents | Accepted architecture ADR controls its exact decision; affected architecture prose must be updated atomically. |
| Telemetry normalization, units, bounds, source trust states, witness/public inputs, commitment/nullifier/circuit semantics, policy lifecycle | `docs/data-and-proof-model.md` | Envelope exchange fields; security eligibility; tests | ADR-0001 controls v1 window endpoints. Future accepted circuit/nullifier/policy ADRs supersede proposals only within their stated/versioned scope. |
| Public envelope bytes, canonical CBOR, field map, proof/receipt shape, disclosure allowlist, public-input reconstruction, typed verifier result and precedence | `docs/claim-envelope.md` | Data/proof semantics; tests | ADR-0001 controls half-open windows; ADR-0002 controls independent typed results, derived disposition, and external business decision. |
| Assurance-tier evidence, disclosure classification, source eligibility controls, threats, privacy/retention, safety boundary | `docs/security-and-privacy.md` | Encoded tier fields/results in `docs/claim-envelope.md`; claim non-goals in `docs/product-scope.md` | Accepted security/privacy ADR controls its decision but cannot upgrade evidence: effective assurance remains bounded by demonstrated evidence. |
| Expected test layers, vectors, interoperability method, benchmarks, observability, deployment/readiness evidence | `docs/testing-and-operations.md` | Expected semantics from each owning contract; gate timing from delivery | Tests implement accepted ADR semantics. They cannot treat an expected fixture label as authority over signed bytes, digests, or the owning contract. |
| Decision state, accountable decider, required review/evidence, ADR lifecycle | `docs/decisions.md` | ADR files and owning topic document | Only accepted/Current ADRs supersede proposals. Proposed ADR-0003 has no effect on this contract. |
| Documentation status vocabulary, navigation, maintenance and validation command | `docs/README.md` | All topic documents | Accepted ADR wins on its decision; README remains authority for how that decision is reflected and validated. |
| Former combined plan | None; `docs/system-plan.md` is trace-only | `docs/README.md` routes to replacements | It can never defeat an active document or ADR. |

## Accepted ADR supersession procedure

An accepted ADR is not merely “another document.” Its decision wins over a conflicting proposal from its decision date, but acceptance also creates a synchronization obligation:

1. Confirm the ADR status is accepted/Current, its owner and required reviewers approved it, and its scope/version includes the conflict.
2. Apply the decision to every affected owning document and expected vector in the same change or mark the stale proposal explicitly superseded and gate execution until synchronization completes.
3. Update `docs/decisions.md` with status and evidence. If scope or delivery changes, obtain those owners' approval and update `docs/product-scope.md` or `docs/delivery-plan.md`; an ADR alone cannot waive them.
4. For an incompatible later choice, write a new ADR that explicitly supersedes the earlier one and defines version/migration/rollback. Never reinterpret already versioned bytes.

Under this procedure ADR-0001 supersedes inclusive `not_after` prose for envelope v1, and ADR-0002 supersedes the single-primary-outcome proposal. Their current rules are already synchronized in the claim, data/proof, architecture, testing, and decision documents. ADR-0003 is Proposed and therefore supersedes nothing.

## Review and approval record

The historical review and approval record is **Superseded**. The listed identifiers did not resolve to assigned participants, and the approval references were not evidence of real reviews.

| Required reviewer | Historical placeholder | Historical approval reference | Current disposition |
| --- | --- | --- | --- |
| Product | `team-directory:TAG-PRODUCT-01` | `TAG-M1-BASELINE-PRODUCT-2026-08-30` | **Superseded** — no real approval evidenced |
| Architecture | `team-directory:TAG-ARCHITECTURE-01` | `TAG-M1-BASELINE-ARCHITECTURE-2026-08-30` | **Superseded** — no real approval evidenced |
| Cryptography | `team-directory:TAG-CRYPTOGRAPHY-01` | `TAG-M1-BASELINE-CRYPTOGRAPHY-2026-08-30` | **Superseded** — no real approval evidenced |
| Security | `team-directory:TAG-SECURITY-01` | `TAG-M1-BASELINE-SECURITY-2026-08-30` | **Superseded** — no real approval evidenced |
| Privacy | `team-directory:TAG-PRIVACY-01` | `TAG-M1-BASELINE-PRIVACY-2026-08-30` | **Superseded** — no real approval evidenced |
| Safety | `team-directory:TAG-SAFETY-01` | `TAG-M1-BASELINE-SAFETY-2026-08-30` | **Superseded** — no real approval evidenced |
| Telemetry | `team-directory:TAG-TELEMETRY-01` | `TAG-M1-BASELINE-TELEMETRY-2026-08-30` | **Superseded** — no real approval evidenced |
| Discovery | `team-directory:TAG-DISCOVERY-01` | `TAG-M1-BASELINE-DISCOVERY-2026-08-30` | **Superseded** — no real approval evidenced |
| Relying party | `external-tool:TAG-RP-DECISION-OWNER-01` | `TAG-M1-BASELINE-RELYING-PARTY-2026-08-30` | **Superseded** — no independent decision owner evidenced |

The sole maintainer may use the routing map for planning, but maintainer review cannot be counted as independent discipline or relying-party approval.

## Historical M1 disposition and Current scoped blockers

The historical status-change reference `TAG-M1-ACCEPTED-DOC-BASELINE-2026-08-30` remains **Superseded** because it falsely implied external approval. The former numbered-milestone sequence is retained only for traceability; it does not control Current work authorization.

- Former `M1` reconciliation records may still support a **solo-maintainer provisional baseline**, but completion of `M1` is not a prerequisite for another exploration track.
- The Current delivery plan and work-authorization document permit compliant solo, synthetic, reversible exploration where the operational register says **Exploration permitted**.
- Missing external discipline or relying-party roles block only the promotion or external claim that triggers those roles; they do not block documentation reconciliation or synthetic technical experiments.
- Paired provider/relying-party discovery remains **Deferred** until suitable participants, discovery-method review, and privacy/input governance exist. `Blocked — paired-discovery promotion` applies only to that participant-facing activity.
- Real or restricted telemetry, hardware, command paths, participant/customer data, live publication, pilots, deployment, production, and higher-assurance claims remain outside the solo synthetic sandbox and require their applicable promotion gates.
