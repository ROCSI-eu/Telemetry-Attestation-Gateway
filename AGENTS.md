# AGENTS.md — Telemetry Attestation Gateway

## Authority and autonomy
- Treat current `main` and owning documents as authoritative; check affected files, PRs, issues, authorizations and relevant gates before edits.
- Continue already-authorized synthetic, isolated, reversible local exploration autonomously; do not invent dependencies on external reviewers or repeatedly request the same approval.
- Use a focused branch/PR, existing checks, concise evidence and an explicit checkpoint. Report only tests actually run. Follow the contribution policy effective at the time; never forge a DCO sign-off.

## Safety and evidence
- Synthetic experiments only; no real telemetry, hardware, MAVLink command generation/forwarding, production systems, live ledgers, participant data, or external sensitive operations without their separately authorized gates.
- No secrets, raw telemetry, witnesses, exact private values, stable identifiers or participant/customer material in Git, logs, UI, exports or receipts.
- All experimental outputs remain `EXPERIMENTAL`, `SYNTHETIC_ONLY`, `NOT VALIDATION OR PRODUCTION AUTHORIZATION`; use `A0_SYNTHETIC` when assurance is shown.
- Proof validity is not telemetry truth; separate source assurance, independent typed verification, publication and the relying party's decision. Do not claim safety, compliance, interoperability, demand, MVP or production readiness without direct accepted evidence.
- Maintain offline independent verification, authenticated canonical security inputs, failure-closed version/trust behavior, and observational-only operation.

## Decisions and handoff
- Update owning documents for substantive decisions, not redundant registers or ADRs for each experiment; keep GitHub history/review evidence.
- Obtain explicit authorization for policy/license changes, external or irreversible actions, hardware, real data, merge, deployment, and any promotion of experimental evidence.
- AGENTIC-INTERACTION-01: at a stopping point report completed work, next action and named blocker; offer an actionable `Continuă` control when no new decision is needed or a precise approval control when it is. Never infer a separate gate approval from a generic continuation.
- Resume from the last verified current checkpoint and do not redo completed steps.
