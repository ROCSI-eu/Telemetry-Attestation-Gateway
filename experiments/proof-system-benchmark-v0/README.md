# Proof-system benchmark (`v0`)

> **EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION**

This experiment evaluates practical zero-knowledge tooling for the synthetic predicate:

`speed_cm_s <= maximum_speed_cm_s`

The observed speed remains private/witness-side; the maximum is public. The experiment reuses the `u32` integer semantics from [`../bounded-speed-v0/`](../bounded-speed-v0/).

## Research question

Can an open, locally runnable proof stack generate and independently verify a genuine proof of the bounded-speed predicate without revealing the private synthetic speed, and what are the basic proof-size/runtime/tooling trade-offs?

## Candidate set

See [`candidates.md`](candidates.md). The implemented candidate is Noir `v1.0.0-beta.26` with Barretenberg `v5.2.0`. Halo2 `halo2_proofs 0.3.5` is the comparison candidate for setup, portability, licensing, and integration characteristics; it is not implemented in this PR because adding a second Rust dependency graph would not improve the first bounded feasibility result enough to justify making the repository's default experiment path heavier.

This is not a proof-system selection. Any later selection remains a separate reviewed decision.

## Implemented circuit

[`noir/src/main.nr`](noir/src/main.nr) is intentionally minimal:

- `speed_cm_s: u32` — private witness;
- `maximum_speed_cm_s: pub u32` — public input;
- one constrained assertion that the private speed is less than or equal to the public maximum.

No telemetry source, identity, timestamp, mission field, publication layer, or command path exists in this experiment.

## Toolchain and setup

The experiment runner never downloads tools or reaches a hosted verifier. It requires locally installed, pinned-compatible `nargo` and `bb` binaries. Barretenberg may require its public CRS to be provisioned once in the local cache before an offline run; that CRS is public setup material, not a secret key. The benchmark evidence workflow used during PR review warms the CRS once, then runs the measured phase with network egress unavailable.

Tool binaries and CRS material are not committed to this repository.

## Run

From this directory, with the pinned toolchain already installed and the CRS already cached:

```text
python3 benchmark.py --runs 3 --output benchmark-results.json
```

The runner:

1. compiles the circuit;
2. generates a circuit verification key;
3. proves and verifies synthetic below-limit and equality-boundary witnesses;
4. confirms an over-limit witness fails before proof generation;
5. mutates proof bytes and confirms verification fails; and
6. records proof size, proving/verification timings, peak child-process RSS where available, tool versions, and case outcomes.

The command itself performs no network fetches. Reproducibility depends on the documented toolchain and locally provisioned public CRS.

## Interpretation boundary

A successful proof establishes only that the chosen cryptographic stack accepted a witness satisfying this synthetic circuit and that the corresponding verifier accepted the proof for its public input. It does **not** establish telemetry truth, trustworthy sensors or time, continuous/whole-flight coverage, hardware integrity, safety, contractual/payment/regulatory compliance, product demand, pilot readiness, production readiness, or sufficiency of `A0_SYNTHETIC` for any external decision.
