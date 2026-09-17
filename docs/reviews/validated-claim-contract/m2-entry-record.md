# M2 paired-discovery entry readiness record

| Record field | Value |
| --- | --- |
| Implementation state | Concept only |
| Evidence source | No execution evidence |
| Review independence | Maintainer-reviewed |
| Data class | Public documentation |
| Permitted environment | Documentation-only |
| External claim level | No external assurance claim |
| Activity | Exploration permitted within the Current work authorization |
| Work item | Historical `M2` label — paired provider/relying-party discovery |
| Record date | 2026-08-30 |
| Status | **Current** as a scoped paired-discovery readiness record; repository-wide milestone hold is **Superseded** |
| Current disposition | Paired external discovery is **Deferred**; `Blocked — paired-discovery promotion` applies only to participant-facing discovery |
| Required accountable role | Discovery lead with product owner; accepted assignees absent |
| Primary tracker | [Issue #49](https://github.com/ROCSI-eu/Telemetry-Attestation-Gateway/issues/49) |
| Downstream tracker | [Issue #50](https://github.com/ROCSI-eu/Telemetry-Attestation-Gateway/issues/50), tracking the paired-discovery evidence and disposition after issue #49 |
| Authority | [`docs/delivery-plan.md`](../../delivery-plan.md), [`docs/current-work-authorization.md`](../../current-work-authorization.md), and [`docs/discovery-research-plan.md`](../../discovery-research-plan.md) |
| Historical routing context | [`authority-map.md`](authority-map.md) and [`solo-planning-readiness-record.md`](solo-planning-readiness-record.md) |

## Purpose and scoped non-authorization

This record now tracks only the prerequisites for participant-facing paired provider/relying-party discovery. It does not control work authorization outside that activity. Earlier wording that treated `M1`/`M2` as sequential repository-wide gates is **Superseded** by the Current parallel-track delivery model and risk-proportionate work authorization.

This record does not authorize participant-data collection, interviews, externally observed discovery findings, real or restricted telemetry, hardware, a vehicle or other command path, live publication, a pilot, deployment, production activity, or external assurance claims. It also does **not** prohibit or gate compliant solo synthetic work that is already **Current / Exploration permitted**, including provisional format spikes, toy circuits, proof-system benchmarks, synthetic or no-hardware/no-command-path SITL normalization, local proof generation and verification, and local demonstrations.

Commercial hypotheses may be explored under the delivery plan, but this record does not establish customer evidence, demand, pilot intent, willingness to pay, or a purchasing decision.

The industrial-site inspection workflow and its buyer, relying-party decision, coverage unit, disclosure need, assurance requirement, volume, purchasing path, pilot intent, and willingness to pay remain hypotheses or **Open** questions. Bounded horizontal speed remains a Proposed synthetic technical primitive, not an approved compliance product.

## Current paired-discovery entry assessment

| Entry condition | Required owner or reviewers | Current status | Evidence or blocker |
| --- | --- | --- | --- |
| Former `M1` completion prerequisite | Repository maintainer | **Superseded** | Numbered milestone completion no longer controls work authorization or paired-discovery entry; prerequisites attach to the activity and promotion being attempted |
| Risk-triggered accountability recorded | Discovery lead with product owner; reviewers identified by the role-by-risk matrix | **Open** — paired-discovery promotion remains blocked | The planned participant research triggers privacy and discovery-method review; additional roles are required only if the actual activity triggers their risk row |
| Provider-side and relying-party-side participants | Discovery lead, product owner, paired participants | **Deferred** — paired-discovery promotion remains blocked | Paired participation and research recruitment remain Deferred until funding or suitable organic relationships exist |
| Approved bounded paired-discovery protocol and evidence-sufficiency method | Product owner; discovery-method review | **Deferred** — paired-discovery promotion remains blocked | `docs/discovery-research-plan.md` remains a Proposed protocol; no independent discovery-method approval exists |
| Approved research and input-handling arrangement | Product owner and privacy reviewer; additional review only where the matrix is triggered | **Deferred** — paired-discovery promotion remains blocked | Google Drive is only Proposed and unconfigured; no approved handling record, system, access model, retention, deletion, or disclosure control exists |
| Synthetic-or-governed participant inputs | Product owner and privacy owner | **Current planning boundary only** | Any future participant-facing discovery must use synthetic inputs or inputs covered by its approved governance arrangement; this condition does not govern the separate synthetic technical sandbox |
| Hypothesis and non-claim boundary acknowledged | Product owner, discovery lead, paired participants, and risk-triggered reviewers | **Current maintainer acknowledgement only** | The workflow, claim materiality, coverage, need, decision, assurance, procurement, pilot intent, and willingness to pay remain Open; the required external acknowledgements are absent |
| Demonstrator assurance restricted to `A0_SYNTHETIC` | Product owner, relying-party participant, and any reviewer triggered by the proposed assurance claim | **Current maintainer acknowledgement only** | `A0_SYNTHETIC` is the only permitted demonstrator tier; required external review remains absent |
| Mandatory participant-facing output labels | Product owner and discovery lead | **Current maintainer acknowledgement only** | Every paper output states **“paper mockup — no proof generated”**; every non-cryptographic output states **“non-cryptographic UX prototype — no proof generated or verified”** on every surface and associated record |
| Complete paired-discovery disposition | Discovery lead with product owner after all applicable evidence and risk-triggered reviews | **Open** — paired-discovery promotion remains blocked | The maintainer explicitly acknowledges that no positive participant-facing discovery disposition can currently be issued |

These conditions apply to paired participant research only. They neither authorize real-data, hardware, command-path, pilot, deployment, or production work nor block the separate solo synthetic experiments explicitly permitted by the delivery plan, current-work-authorization document, and operational register.

## Required acceptance evidence for paired discovery

Before paired provider/relying-party discovery may become active participant research, the repository must contain only the minimum non-sensitive references needed to establish all of the following:

1. **Accountability:** the activity and intended claims are mapped to the role-by-risk matrix; approved stable references resolve to the accountable discovery and product owners, paired participants, privacy and discovery-method reviewers, and any additional role actually triggered. Each referenced person has acknowledged the applicable duties. Names, contact details, or private directory material need not and should not be copied into Git.
2. **Independent relying-party ownership and paired participation:** a genuine relying-party decision owner is not the producer, maintainer, project team, or an AI proxy; the required provider-side and relying-party-side participants are available for the same bounded decision workflow.
3. **Protocol approval:** the product owner has approved the bounded paired-discovery scope, and a qualified discovery-method reviewer has approved the method, sampling rationale, evidence-sufficiency rule, contradiction handling, and review trigger.
4. **Privacy and input approval:** the product and privacy owners have approved the purpose and lawful basis where applicable, notice and consent, minimization and prohibited data, approved systems, access and export controls, retention and deletion, disclosure review, incident handling, and the exact repository path and formats permitted for any minimized synthesis.
5. **Input eligibility:** the approved plan limits participant-facing work to synthetic inputs or inputs covered by the recorded governance arrangement. Raw or restricted participant, customer, mission, or telemetry data is not copied into Git, fixtures, logs, screenshots, exports, or mockups.
6. **Claim boundary:** the product owner, discovery lead, paired participants, and reviewers triggered by the actual claim acknowledge that proof validity is not telemetry truth; one observation is not interval, whole-flight, safety, contractual, payment, or regulatory compliance; verification is not the relying party's business decision; and publication is optional corroboration rather than verification authority.
7. **Assurance boundary:** `A0_SYNTHETIC` is the only demonstrator assurance tier. The relying-party participant and any reviewer triggered by a proposed assurance claim acknowledge that a higher future requirement neither upgrades evidence nor authorizes hardware or other work needed to attain it.
8. **Output labelling:** every permitted paper or non-cryptographic concept surface, export, screenshot, recording, result, and research record carries the applicable required label.
9. **Entry disposition:** the discovery lead and product owner record that the complete applicable entry set is satisfied, cite the accepted evidence references, and confirm that no excluded activity is thereby authorized.

Completion of a former numbered milestone is not an entry condition. The Current model attaches prerequisites to the paired-discovery activity and intended evidence claim itself.

## Privacy and repository boundary

Governed source evidence belongs only in an approved external research system. Google Drive is presently Proposed but unconfigured and unapproved. Do not place participant names, contact details, employer or site details where identifying, recruitment records, recordings, transcripts, raw notes, consent records, procurement documents, contract material, exact locations, flight paths, telemetry, customer or mission identifiers, credentials, restricted fields, or re-identifying combinations in Git or an unapproved Drive location.

Until a privacy-handling approval explicitly permits a repository evidence path, do not create `docs/discovery/` or commit completed participant research material. Blank templates may remain planning aids only. This restriction does not apply to the separate `experiments/` workspace when it remains within the Current demonstrably synthetic, minimized, test-only sandbox rules.

## Deferred conditions and revisit trigger

Paired-participant research recruitment, discovery-method approval, and research/input-handling approval are **Deferred**. They may be reconsidered when funding or suitable organic relationships make genuine paired participation realistic and when qualified reviewers and a controlled external evidence system can be established.

Deferred does not mean satisfied. Each deferred item remains blocking for paired participant research until accepted evidence changes its status. It is not a blocker to unrelated synthetic technical feasibility work.

## Transition procedure

Only when every paired-discovery entry condition is complete:

1. update this record with the non-sensitive evidence references, reviewer acknowledgements, expiry or review triggers, and discovery-lead/product-owner disposition;
2. update each affected artifact row in `docs/management/validated-claim-contract-register.csv` with its six labels, approved research environment, evidence references, and limitations;
3. record the accepted non-contact accountability and evidence references required by the approved research arrangement;
4. clear only the scoped paired-discovery blocker and add a dated status-change reference;
5. close issue #49 and leave issue #50 open for the governed discovery evidence and final paired-discovery disposition; and
6. run `python3 scripts/check_docs.py` and the applicable repository review checks.

Activating paired discovery would authorize only the bounded, approved participant research. It would not change the authorization of another exploration track, freeze the claim contract, establish implementation, demand, pilot readiness, willingness to pay, safety, compliance, or production readiness.
