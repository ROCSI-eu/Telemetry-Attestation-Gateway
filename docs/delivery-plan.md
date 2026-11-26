# Delivery plan

| Metadata | Value |
| --- | --- |
| Status | Parallel exploration tracks with artifact-promotion gates |
| Audience | Delivery, product, discovery, engineering, cryptography, security, privacy, safety, commercial, platform, and operations |
| Accountable role | Delivery lead; each artifact owner and named discipline reviewer approves only the evidence in their scope |
| Review trigger | Artifact status, dependency, evidence, risk, ownership, or intended-use change |
| Authority | Normative delivery tracks, artifact dependencies, promotion gates, and MVP declaration |

## Operating model

Delivery proceeds through five parallel tracks rather than a milestone sequence:

1. [Problem and workflow discovery](#track-problem-and-workflow-discovery)
2. [Claim and contract exploration](#track-claim-and-contract-exploration)
3. [Technical feasibility](#track-technical-feasibility)
4. [Safety, privacy, and trust analysis](#track-safety-privacy-and-trust-analysis)
5. [Commercial discovery](#track-commercial-discovery)

Each track MAY begin immediately with solo, synthetic, reversible exploration. A track does not wait for another track merely because the other track's evidence is incomplete. Dependencies attach to a named artifact and intended promotion, not to a phase, milestone number, role roster, or the general completion of another track.

Technical feasibility does not validate a workflow or market. External workflow evidence does not establish technical feasibility, safety, privacy, security, purchasing intent, or deployment readiness. Commercial interest does not freeze a claim or authorize implementation. Evidence may inform another track, but it changes that track's status only through the applicable promotion gate.

### Status dimensions

Every governed artifact record MUST carry the six independent labels defined by the [documentation status model](README.md#orthogonal-artifact-labels): implementation state, evidence source, review independence, data class, permitted environment, and external claim level. Records additionally state activity as `Exploration permitted`, `Exploration restricted`, or `Exploration not permitted`, and may state whether a contract is provisional or frozen. `Open` is reserved for unresolved hypotheses or decisions. `Blocked` is reserved for a specific named promotion or deployment decision that cannot proceed; a failed gate MUST NOT stop unrelated exploration.

Statuses are scoped assertions, not a maturity ladder. Each value MUST name the artifact version or digest, intended use, evidence links, owner, decision date, limitations, and any approving authority. For example, a contract can remain provisional while a synthetic codec spike is `Exploration permitted`; a workflow can have participant evidence while deployment remains unauthorized; and `Blocked — Gate B participant evaluation` can coexist with continued local exploration.

### Exploration boundary

Solo exploration MUST be disposable or readily reversible and use demonstrably synthetic data with recorded provenance. It MAY include paper workflows, provisional schemas, canonical-encoding spikes, synthetic fixtures, local-only mock adapters, toy circuits, proof-system benchmarks, SITL experiments without hardware or a command path, threat-model drafts, pricing hypotheses, and local UI or CLI demonstrations.

Experimental artifacts and outputs MUST conspicuously carry **`EXPERIMENTAL`**, **`SYNTHETIC_ONLY`**, and **`NOT VALIDATION OR PRODUCTION AUTHORIZATION`**. If a format cannot embed those markings, an adjacent manifest MUST identify it by path and digest, and every human-visible rendering MUST show the markings. Experiments MUST remain isolated from participant or customer data, real telemetry, hardware, vehicle or other command paths, live ledgers or networks, production credentials or trust roots, and production infrastructure. Test-only loopback endpoints and disposable test keys are allowed when identified as such.

Experiment output is not external discovery evidence, independent verification, a performance commitment, a security finding closure, or a product capability. It MUST NOT be relabelled in place. Promotion requires a reviewed copy or reimplementation under the destination controls, retaining provenance while excluding sandbox data and keys.

## Product-readiness focus and GCS demonstrator

Planning direction, 2026-11-26: pause automatic continuation of individual fundamental experiments; retain the research track and resume narrowly scoped investigations only for material demonstrator or product limitations. Reuse accepted synthetic evidence and the existing pinned tools. This is a prioritization within the parallel-track model, not an additional promotion gate.

The first proposed increment is GCS-COMPANION-01: an isolated, synthetic, receive-only reference companion for one existing GCS, preferably QGroundControl, or Mission Planner first if the existing test environment makes that simpler. Both integrations should ultimately reuse the same experimental TAG core and minimal ingestion contract, without native plugins, GCS forks or a TAG command/relay path. Keep GCS command capabilities outside the TAG trust boundary and enforce the isolated synthetic test boundary. Reuse the demonstrated bounded-speed SITL-to-ZKP path and independent offline verifier; keep mock, replay and newly observed cryptographic results distinguishable. An historical proof is not evidence for a new observation unless the actual bound inputs and provenance match.

Acceptance for the first integration: reproducible shared synthetic scenario in the GCS and TAG; bounded intake and policy evaluation; correctly attributed genuine proof or explicitly separate replay; independently invokable offline verification; minimized typed output; positive, negative and unavailable-input/verifier fail-closed cases; no raw telemetry, witness or restricted identifiers in UI/export/logs; verified absence of a TAG command path; scoped cleanup. Any new execution, proving, provisioning or installation must remain within its applicable authorization. Reuse the same core for the second GCS.

Proposed test-tool retention: preserve version-pinned GCS applications in the appropriate non-production QA environments alongside existing toolchains after separately approved installation and dependency/provenance checks. Retain synthetic scenario definitions and manual reproduction instructions beside automated tests. Keep experiment processes and private runtime data disposable and isolated. Do not alter the existing TAG #88 service or use a production host for this increment.

Finite follow-on objectives: consolidate the shared experimental core; demonstrate both GCS integrations; package portable offline evidence; freeze the applicable contract and select the proof system through Gate A and required review; prepare a reproducible supported distribution through applicable promotion controls; complete scoped security/privacy/recovery evidence; conduct separately authorized external workflow and technical/commercial evaluation under Gate B; and consider an offline MVP declaration only when Gate D is satisfied. Gate C and Gate E remain separate for real sources/hardware and pilot/deployment. External discovery and security preparation may run in parallel within their authorization. Keep the six independent artifact dimensions and existing register unchanged until evidence and authority justify promotion.

The public reference implementation and eventual private commercial boundary follow the [commercial model](commercial-model.md#repository-boundary-and-gcs-reference-integration). No private repository, new deployment, proof-system adoption or release is authorized by this planning section.

## Artifact map and dependencies

The identifiers below name artifacts, not sequential work packages.

| ID | Artifact | Producing track | May be explored with | Required only when promoted or consumed for |
| --- | --- | --- | --- | --- |
| `WF` | Workflow evidence record | Problem/workflow | A hypothesis, paper workflow, and synthetic examples | Selecting a workflow for an MVP claim or making an external workflow-value claim |
| `CC` | Claim contract | Claim/contract | A candidate decision, provisional schema, and synthetic examples | Freezing public inputs, result/time semantics, assurance language, or a stable API |
| `FV` | Format vectors and codec spike | Technical feasibility | **Provisional schema plus synthetic fixtures only** | Releasing an interoperable envelope or stable codec/API |
| `TF` | Telemetry/SITL feasibility record | Technical feasibility | Candidate fields and synthetic or SITL records | Selecting supported telemetry inputs or preparing hardware evaluation |
| `PB` | Proof-system benchmark | Technical feasibility | Provisional claim shape and synthetic representative workload | Selecting a proof system or beginning real proof implementation |
| `RP` | Real-proof evaluation package | Technical feasibility | Frozen relevant contract, real proofs, authenticated policy/revocation material, and independent verifier | Participant-facing technical evaluation of proof behavior |
| `ST` | Safety, privacy, and trust record | Safety/privacy/trust | Draft data flow, threats, harms, and synthetic fixtures | Participant research, real-proof evaluation, hardware connection, pilot, or deployment as scoped below |
| `CE` | Commercial evidence record | Commercial discovery | Pricing, buyer, procurement, and integration hypotheses | Claiming pilot intent, willingness to pay, or commercial MVP evidence |
| `MP` | MVP evidence index and declaration | Cross-track gate | Links to candidate artifacts | Declaring the bounded MVP |

An artifact depends only on the inputs named in its row or promotion gate. In particular:

- `FV` does **not** depend on `WF`, `CE`, validated market evidence, a selected proof system, or real telemetry.
- `WF` external validation depends on participant governance in `ST`; it does **not** depend on `FV`, `TF`, `PB`, `RP`, or any technical-feasibility result.
- `PB` may benchmark provisional claim shapes; selecting a proof system depends on the relevant accepted claim semantics and cryptography/security review, not commercial validation.
- `RP` depends on the relevant frozen cryptographic contract, accepted proof-system decision, security/cryptography review, authenticated test materials, and an independent verifier. It does **not** require chain, SRE, hardware, sales, procurement, or other unrelated production roles.
- `CE` may test pricing and procurement hypotheses before technical feasibility is known, provided limitations are explicit and no capability is represented as implemented.

## Synchronization gates

Synchronization occurs only when an artifact is promoted to a higher-consequence use. Gate failure blocks that promotion, not the originating track's safe exploration or unrelated work.

### Gate A — freeze a claim contract

**Purpose:** promote `CC` from provisional exploration to the frozen contract used by real proof work or a stable public interface.

**Required artifacts:**

- bounded claim and relying-party decision, including snapshot-versus-coverage semantics and non-claims;
- typed outcomes and precedence, explicit decision time, freshness, replay, policy lifecycle, canonical encoding, ordered public inputs, versioning, and migration rules;
- field-by-field public/private disclosure and assurance presentation;
- positive, negative, boundary, mutation, and incompatibility fixtures; and
- accepted contract ADRs and review of security, privacy, cryptography, telemetry, architecture, product, and safety issues actually implicated by the contract.

Workflow and commercial evidence SHOULD inform the freeze, but their absence does not prevent continued contract exploration or a format spike. If the contract is frozen for an MVP declaration, Gate D additionally requires the workflow evidence specified there.

### Gate B — begin participant-facing technical evaluation

There are two distinct paths; neither is allowed to masquerade as the other.

**Workflow research without real proofs** requires an approved research protocol; participant roles and sampling rationale; consent or other lawful basis; minimization, access, retention, deletion, and approved storage; participant-safe wording; and paper or prototype surfaces labelled **“paper mockup — no proof generated”** or **“non-cryptographic UX prototype — no proof generated or verified.”** Passing this path may externally validate `WF`, but does not validate technical feasibility.

**Real-proof evaluation** requires the relevant parts of `CC` frozen; an accepted proof-system decision; real positive, negative, and boundary proofs; canonical public inputs; authenticated verification, policy, and revocation artifacts; an independent verifier; cryptography and security approval of the evaluation design; privacy governance for participant inputs and outputs; and a fail-closed plan. Reviewers are selected by the risks present. Unrelated production roles are not prerequisites.

### Gate C — connect hardware or a real telemetry source

**Required artifacts:** accepted `TF` for the pinned source/profile; a source-specific hazard analysis; safety-owner approval of an isolated, no-command test plan; security review of the trust boundary and credentials; privacy approval for the data handled; stop conditions; observability; rollback and incident procedures; and named test operators. A command path, live ledger publication, or production use requires a separate explicit authorization and is not implied.

### Gate D — declare the MVP

**Required artifacts:**

- externally validated `WF` evidence for the bounded provider/relying-party workflow;
- frozen `CC` with reviewed vectors and accepted ADRs;
- technical evidence for the bounded synthetic telemetry-to-proof-to-independent-verification path, including `FV`, `TF`, `PB`, and the required `RP` cases;
- accepted `ST` analysis for the MVP boundary, with critical issues closed or explicitly accepted by accountable owners;
- `CE` evidence for the MVP's stated commercial claim, clearly distinguishing integration fit, pilot intent, and completed purchasing evidence; and
- an immutable or content-addressed `MP` index recording scope, approvers, dissent, unresolved risks, accepted residual risk, known limitations, and stop conditions.

Gate D is an MVP declaration only. It does not authorize a pilot, hardware, a live chain, multi-tenancy, production operation, safety or regulatory claims, or deployment. If commercial validation is intentionally excluded from the MVP claim, `MP` MUST say so and MUST NOT claim buyer validation, pilot intent, or willingness to pay.

### Gate E — pilot or deployment promotion

Promotion beyond the offline MVP requires controls specific to the proposed environment: named accountable service, security, privacy, safety, and operational owners; separation of duties; governed real-data basis; independent security/privacy/safety review; supported versions and dependencies; SLO/capacity evidence; recovery, rollback, incident, credential and key lifecycle controls; authoritative registry and freshness behavior; deployment scope; and explicit pilot or production authorization. Only roles and controls implicated by the deployment are required, but none may be inferred from MVP completion.

## Track: Problem and workflow discovery

**Question:** Is there a bounded evidence handoff and relying-party decision worth supporting?

**Exploration allowed:** interviews planning, desk research, paper workflows, synthetic scenarios, alternative mapping, and labelled non-cryptographic comprehension prototypes may proceed independently.

**Provisional artifacts:** actor/decision hypothesis; current evidence handoff; disclosure map; snapshot-versus-coverage statement; provider and relying-party recruitment/sampling plan; research protocol; contradictory evidence log; workflow acceptance thresholds.

**External validation:** use genuinely paired provider and relying-party perspectives for the same handoff. Record participant role, decision, representative inputs, method, pre-agreed threshold, observed result, objections, contradictory cases, limitations, and product-owner disposition. Participant-level notes, recordings, contact details, consent records, procurement material, and re-identifying combinations remain outside Git unless an approved privacy record explicitly permits a minimized form and exact location.

**Does not establish:** parser compatibility, proof validity, security, assurance sufficiency, performance, willingness to pay, or deployment readiness.

**Owner:** discovery lead with product owner; privacy and method review apply when participant research begins.

## Track: Claim and contract exploration

**Question:** What exactly is asserted, disclosed, verified, timed, and rejected?

**Exploration allowed:** candidate bounded-speed claims, result taxonomies, assurance wording, schemas, encodings, and synthetic fixtures may be revised incompatibly without workflow or market validation.

**Provisional artifacts:** claim statement and non-claims; relying-party decision hypothesis; public/private field map; result and error precedence; decision-time and replay semantics; policy lifecycle; assurance vocabulary; envelope/schema draft; versioning and migration options; contract ADR drafts.

**Promotion:** Gate A freezes only the accepted version and scope. Later workflow, security, privacy, telemetry, or cryptographic evidence that changes meaning reopens the gate and invalidates affected downstream evidence.

**Does not establish:** user value, implementation feasibility, proof-system security, interoperability, or deployment approval.

**Owner:** product and architecture owners; specialist reviewers are triggered by the contract content.

## Track: Technical feasibility

**Question:** Can the bounded contract be implemented and independently checked within declared constraints?

This track contains separable experiments:

- **Format spike (`FV`):** using only a provisional schema and synthetic fixtures, test strict canonical decoding, deterministic byte-identical re-encoding, ordered public-input reconstruction, and rejection of duplicate, unknown, invalid, unsupported, out-of-bound, and mutated fields. Opaque placeholder proof bytes are sufficient. A disposable independent checker may use the same language. Releasing an interoperable format later requires the frozen contract, accepted release ADR, and two genuinely independent implementations in different languages passing the released corpus.
- **Telemetry/SITL feasibility (`TF`):** pin simulator/autopilot, dialect, messages, units, ranges, clocks, signing/trust states, and synthetic record/replay digests. Reject malformed, mixed-source, stale, invalid-signature, and unsupported inputs. SITL evidence is not hardware or real-flight evidence.
- **Proof benchmark (`PB`):** compare viable candidates on synthetic representative workloads, documenting versions, assumptions, setup/key lifecycle, licensing, portability, proof size, generation and verification distributions, memory, and throughput. Results are feasibility evidence, not an SLO.
- **Real-proof package (`RP`):** after Gate A and acceptance of the proof-system decision, construct the bounded positive, negative, and boundary proofs, authenticated offline policy/revocation fixtures, independent verifier, lifecycle vectors, altered-input cases, and explicit test-only trust roots needed for review. This construction remains non-participant, test-only technical work. Gate B reviews the completed package and authorizes only its participant-facing evaluation; it is not a prerequisite for constructing that package. Every result using fixture authority is labelled `TEST_ONLY_NOT_PRODUCTION_AUTHORIZATION`.
- **Mock operator boundary:** after local proof semantics exist, a deterministic mock adapter and offline package may explore idempotency, retry/restart/outage behavior, stable machine-readable errors, restricted-field absence, and verification without a vendor service or network dependency.

**Does not establish:** workflow value, safety, commercial demand, real-source provenance, sensor truth, production capacity, or deployment readiness.

**Owner:** the artifact's engineering, telemetry, architecture, or cryptography owner; cryptography/security approval is mandatory only where cryptographic selection or real-proof work is promoted.

## Track: Safety, privacy, and trust analysis

**Question:** What harms, disclosures, trust assumptions, and operating boundaries accompany each proposed use?

**Exploration allowed:** draft threat models, misuse/abuse cases, data-flow maps, disclosure comparisons, linkage analysis, assurance tiers, trust-boundary alternatives, safety hazards, and synthetic policy lifecycle fixtures may proceed independently.

**Provisional artifacts:** harm and threat register; data classification and flow; minimization/retention/deletion proposal; restricted-field tests; provenance and assurance model; trust-root/key lifecycle proposal; safety boundary and no-command rule; risk-triggered role matrix; residual-risk register.

**Promotion:** approve only the intended use reviewed. Participant governance, real-proof evaluation, hardware connection, MVP declaration, pilot, and deployment each consume the relevant version of `ST` at Gates B–E. Approval at one scope does not carry forward automatically.

**Does not establish:** workflow value, cryptographic correctness, participant comprehension, regulatory compliance, commercial demand, or deployment approval outside the named scope.

**Owner:** security, privacy, or safety owner according to the risk; independence and separation of duties are required for pilot/production, not for solo synthetic analysis.

## Track: Commercial discovery

**Question:** Who buys, through what route, for which bounded outcome and evidence threshold?

**Exploration allowed:** stakeholder maps, buyer/budget hypotheses, pricing tests, procurement-path research, integration assumptions, and synthetic package walkthroughs may proceed before technical feasibility or workflow validation. Materials MUST state which capabilities are hypothetical or unavailable.

**Provisional artifacts:** economic buyer and budget-holder hypothesis; purchasing route; alternatives and switching costs; integration-effort threshold; price hypothesis; pilot success/stop criteria; objections and counterevidence.

**External validation:** record the organization and decision-owning roles, evaluated package/version, actual integration effort, dependencies, support burden, performance threshold, budget/procurement next step, objections, and disposition. Pilot intent requires a written commitment naming provider and relying-party owners, scope, timing, resources, and success/stop criteria. Willingness to pay requires purchasing evidence such as an executed paid-pilot agreement or completed purchase; interest or an unsigned expression does not qualify.

**Does not establish:** technical feasibility, proof/security assurance, workflow validity, or deployment approval.

**Owner:** commercial or product owner; participant privacy governance still applies.

## Shared evidence rubric

| Question | Minimum evidence for the claim |
| --- | --- |
| **Privacy improvement** | Field-by-field comparison of current disclosure and the evaluated package, confirming restricted-field absence; preference alone is insufficient. |
| **Verifier comprehension** | An unaided representative relying-party reviewer explains accepted/rejected results, public claim, assurance, freshness/replay limits, and non-claims; errors and revisions are recorded. |
| **Acceptable integration effort** | A reference integrator records elapsed time, changes, dependencies, deployment/support steps, and blockers against a pre-agreed threshold. |
| **Assurance sufficiency** | The relying party states minimum provenance, policy, freshness, replay, and verification controls and accepts or rejects the explicit tier for its decision. This does not imply sensor truth or safety. |
| **Performance fit** | Measurements on declared representative hardware cover applicable generation, transfer/import, verification, reviewer time, memory, and throughput against pre-agreed discovery thresholds; these are not SLOs. |
| **Pilot intent** | A written commitment records owners, decision, scope, governed inputs, timing, resources, success/stop criteria, and procurement/budget next step. |
| **Willingness to pay** | Executed purchasing evidence; proposed pricing, positive feedback, or intent alone is insufficient. |

Failed or inconclusive results remain useful learning. They set the applicable validation status to `no` or `pending` and keep only the dependent promotion closed.

## MVP boundary and later progression

The proposed MVP remains an offline, synthetic, bounded telemetry-to-proof-to-independent-verification path with a deterministic mock adapter and no vehicle command path. The mock is the only required chain dependency. One pinned synthetic scenario MUST reproduce in default offline CI; positive, negative, boundary, fuzz, security, privacy, resilience, lifecycle, and benchmark evidence MUST be linked; restricted fields MUST remain outside proof, verifier, logs, mock, and export surfaces; and failures, drops, duplicates, retries, and lifecycle transitions MUST be observable and bounded.

After Gate D, optional post-MVP work may explore a pinned chain test environment and then a controlled hardware pilot. A chain promotion requires an ADR covering the supported SDK/network/contract language, verification route, disclosure behavior, cost model, finality, retries, reorganization, reconciliation, and key handling. Hardware remains behind Gate C. Neither is required to declare the offline MVP.

No phase, track completion, fixture profile, MVP declaration, or controlled pilot authorizes production. Gate E MUST separately approve authoritative registries, cache freshness and outage/freeze controls, operational approval quorum, break-glass handling, production trust-root and key ceremonies, tenant/identity boundaries, SLOs, capacity, recovery, rollback, incident response, and the exact deployment scope.

## Related documents and validation

[Product scope](product-scope.md) owns outcomes, [architecture](architecture.md) owns boundaries, [data and proof model](data-and-proof-model.md) owns proof semantics, [security and privacy](security-and-privacy.md) owns trust and disclosure controls, [discovery research plan](discovery-research-plan.md) owns research methods, [testing and operations](testing-and-operations.md) owns evidence methods, and [decisions](decisions.md) owns decision closure. Supporting artifacts MUST link to this plan without recreating a sequential milestone dependency graph.
