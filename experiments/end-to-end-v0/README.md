# End-to-end local demonstrator (`v0`)

> **EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION**

This experiment connects the repository's existing synthetic MAVLink normalization and bounded-speed proof experiments into one narrow local path:

`synthetic MAVLink observation -> allowlisted normalization -> private speed witness -> bounded-speed zero-knowledge proof -> independent offline verification -> typed experimental result`

It addresses issue #70. It is a disposable technical-feasibility demonstrator, not the formal `RP` package, not a frozen claim contract, not a supported MAVLink adapter, and not a proof-system or architecture selection.

## Research question

Can the existing synthetic observation parser/normalizer feed the private integer witness used by the bounded-speed proof experiment and reach independent offline cryptographic verification without exposing the normalized speed in the demonstrator result?

## Inputs and boundaries

The default fixture source is the demonstrably synthetic record/replay corpus in [`../mavlink-normalization-v0/fixtures.json`](../mavlink-normalization-v0/fixtures.json). The demonstrator does not open a socket or connect to SITL, hardware, a vehicle, a participant, a customer, a hosted verifier, a ledger, or a publication service.

The observation path remains receive-only. No MAVLink command-generation, approval, forwarding, relay, or flight-control path exists.

The normalized `speed_cm_s` value is handed directly to the prover in process and is not placed in the demonstrator result. The verifier still receives only the public CBOR artifact, proof, and pinned experimental verification key. Proof validity therefore remains separate from telemetry truth and source trust.

## One-command local run

Prerequisites are the same pinned local research tools used by [`../bounded-speed-proof-v0/`](../bounded-speed-proof-v0/):

- Noir/Nargo `1.0.0-beta.26`;
- Barretenberg `5.2.0`;
- the required public Barretenberg CRS already present in the local cache.

Once those public tools/materials are provisioned, the command itself performs no network fetch:

```text
python3 experiments/end-to-end-v0/demo.py \
  --capture-name unsigned-consistent \
  --maximum-speed-cm-s 600
```

The default proof package is temporary and is deleted after verification. Human-visible output is minimized and does not print the private normalized speed or raw MAVLink frame bytes.

For the checked-in synthetic `unsigned-consistent` fixture, the following public limits exercise the three predicate relationships used by the evidence runner:

```text
# below limit
python3 experiments/end-to-end-v0/demo.py --capture-name unsigned-consistent --maximum-speed-cm-s 600

# equality boundary
python3 experiments/end-to-end-v0/demo.py --capture-name unsigned-consistent --maximum-speed-cm-s 500

# over limit: normalization succeeds, proof generation does not begin
python3 experiments/end-to-end-v0/demo.py --capture-name unsigned-consistent --maximum-speed-cm-s 499
```

These numbers are fabricated test-only values. They do not represent a real vehicle, mission, customer, site, or policy.

## Typed result

The CLI keeps these dimensions separate:

- telemetry normalization and source trust;
- predicate outcome;
- proof-generation state;
- verifier input status;
- cryptographic validity;
- policy;
- freshness;
- revocation;
- replay;
- assurance;
- publication; and
- relying-party decision.

There is no single `overall_valid` or business-disposition Boolean.

`A0_SYNTHETIC` remains the only demonstrator assurance tier. A cryptographically valid proof does not upgrade source trust, prove sensor truth, establish trustworthy time, or make a relying-party decision.

## Test and evidence coverage

The standard-library boundary tests run without proof tooling:

```text
python3 experiments/end-to-end-v0/test_demo.py
```

The genuine evidence runner additionally exercises:

- below-limit end-to-end proof and offline verification;
- equality at the public maximum;
- over-limit rejection before proving;
- malformed MAVLink telemetry rejected before proving;
- one-byte proof mutation;
- altered but canonical public input;
- incompatible public-artifact version;
- zero-knowledge proof mode; and
- absence of generated witness material from proof packages.

During PR evidence collection, proof tools and public CRS material may be provisioned first. The measured evidence phase is then run inside an isolated network namespace. The temporary network-enabled evidence workflow is removed before merge so the repository's default CI remains offline-oriented.

## Interpretation boundary

A successful run establishes only that, under the pinned synthetic experiment conditions, the project can connect one observation-shaped MAVLink input to deterministic normalization, use the normalized integer as a private bounded-speed witness, generate a genuine zero-knowledge proof, and independently verify it offline.

It does **not** establish telemetry truth, trustworthy sensors or time, interval/continuous/whole-flight coverage, hardware provenance, safety, contractual/payment/regulatory compliance, workflow validity, demand, willingness to pay, pilot readiness, production readiness, or authorization for live telemetry/hardware.

Publication is not verification. Verification is not a relying party's business decision. One observation is not a whole-flight or compliance claim.
