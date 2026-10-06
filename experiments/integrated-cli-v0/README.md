# Integrated local CLI prototype v0

> **EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION**

This experiment addresses issue #85 by composing the existing synthetic research boundaries into one local command. It reuses the current MAVLink normalization, genuine bounded-speed proof generation, independent offline verification, and provisional publication-adapter implementations rather than forking their semantics.

The integrated result schema is \`TAG_INTEGRATED_CLI_RESULT_V0_EXPERIMENTAL\`. It is an experimental transport for the later demonstrator console, not a frozen public API or product contract.

## What the command does

The default path is:

\`checked-in synthetic fixture -> receive-only normalization -> private bounded-speed witness -> genuine proof -> independent verification -> publication disabled -> redacted typed result\`

The CLI keeps these dimensions separate:

- source normalization and source trust;
- the bounded claim against the public maximum;
- proof-generation state;
- verification-input and cryptographic state;
- policy, freshness, revocation, replay, and assurance;
- optional publication state; and
- the relying-party decision, which remains \`NOT_MADE\`.

It does not print the exact normalized private speed, raw MAVLink bytes, witness material, proof secrets, stable identity, coordinates, mission/customer data, credentials, or unrelated correlation material. There is no MAVLink command-generation, approval, forwarding, or relay path.

## Prerequisite for genuine proof runs

The CLI intentionally does not provision proof tooling or fetch setup material. Before a genuine proof run, provision the exact Noir, Barretenberg, and CRS/setup material required by [\`../bounded-speed-proof-v0/\`](../bounded-speed-proof-v0/) according to that experiment's pinned instructions.

After those public proof dependencies are provisioned, the default integrated flow requires no network access.

If the proof tooling is unavailable or incompatible, the CLI reports the cryptographic dimension as \`UNVERIFIABLE\`; it does not silently replace genuine proving with a mock.

## Run the default human-readable flow

From the repository root:

\`\`\`text
python3 experiments/integrated-cli-v0/cli.py --maximum-speed-cm-s 600
\`\`\`

The default synthetic capture is \`unsigned-consistent\`. Its private normalized speed is used by the prover but is deliberately absent from human-visible and machine-readable output.

For the experimental machine-readable transport:

\`\`\`text
python3 experiments/integrated-cli-v0/cli.py --maximum-speed-cm-s 600 --format json
\`\`\`

## Optional deterministic local publication

Publication is disabled by default. To exercise the disposable local adapter after a valid proof verifies:

\`\`\`text
python3 experiments/integrated-cli-v0/cli.py \
  --maximum-speed-cm-s 600 \
  --publication local
\`\`\`

A temporary publication state file is used unless \`--publication-state\` is supplied. A supplied state path is still disposable test state, not a production database or stable publication service.

Synthetic one-shot publication faults can exercise timeout, cancellation, substrate-unavailable, and definitive-failure behavior. Retryable pending timeout/cancellation results are retried once and reconciled through the adapter's status lookup. Publication failure never rewrites the already computed verifier dimensions.

## Boundary and failure scenarios

The CLI can exercise the existing boundaries without exposing the private observation:

\`\`\`text
# Equality boundary
python3 experiments/integrated-cli-v0/cli.py --maximum-speed-cm-s 500

# Over-limit: stops before proof generation
python3 experiments/integrated-cli-v0/cli.py --maximum-speed-cm-s 499

# Malformed source: stops before proving
python3 experiments/integrated-cli-v0/cli.py --maximum-speed-cm-s 600 --capture-name bad-crc

# Verify a deliberately tampered proof
python3 experiments/integrated-cli-v0/cli.py --maximum-speed-cm-s 600 --verification-case tampered-proof

# Verify altered public input
python3 experiments/integrated-cli-v0/cli.py --maximum-speed-cm-s 600 --verification-case altered-public-input

# Fail closed on an unsupported public-artifact version
python3 experiments/integrated-cli-v0/cli.py --maximum-speed-cm-s 600 --verification-case unsupported-version

# Exercise retry/reconciliation in the local publication adapter
python3 experiments/integrated-cli-v0/cli.py \
  --maximum-speed-cm-s 600 \
  --publication local \
  --publication-fault timeout
\`\`\`

A tampered proof or altered public input is expected to become cryptographically invalid. An incompatible public-artifact version is expected to be rejected before cryptographic verification. An over-limit observation is expected to stop before proof generation rather than being mislabeled as a cryptographic failure.

## Deterministic repository-owned checks

The lightweight standard-library test and orchestration evidence run without Noir/Barretenberg provisioning:

\`\`\`text
python3 experiments/integrated-cli-v0/test_cli.py
python3 experiments/integrated-cli-v0/evidence.py --output /tmp/integrated-cli-evidence.json
diff -u experiments/integrated-cli-v0/evidence-results.json /tmp/integrated-cli-evidence.json
\`\`\`

They are also registered in:

\`\`\`text
python3 scripts/check_experiments.py
\`\`\`

The checked-in \`evidence-results.json\` covers deterministic orchestration/control-flow semantics, including disabled/local publication, retry/reconciliation behavior, malformed and over-limit short-circuiting, tampered proof, altered public input, and unsupported version handling.

It deliberately does **not** pretend to be fresh cryptographic benchmark evidence. Genuine proof-generation and verification evidence remains owned by [\`../end-to-end-v0/\`](../end-to-end-v0/) and its separately pinned proof environment.

## Non-claims

Success here means the existing synthetic research pieces can be invoked coherently through one redacted local experimental program.

It does not establish telemetry truth, trustworthy time, source assurance beyond \`A0_SYNTHETIC\`, interval or whole-flight compliance, safety, contractual or regulatory compliance, customer demand, willingness to pay, pilot readiness, deployment authorization, production capacity, or a relying-party business decision.

No real telemetry, hardware, live ledger/vendor service, production credential, production trust root, participant/customer data, stable production API, browser UI, or MAVLink command path is introduced by this experiment.
