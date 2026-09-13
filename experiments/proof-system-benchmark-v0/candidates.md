# Candidate assessment

> **EXPERIMENTAL · SYNTHETIC_ONLY · NOT VALIDATION OR PRODUCTION AUTHORIZATION**

This is a bounded feasibility comparison, not an architecture decision, dependency approval, or security review.

| Dimension | Noir + Barretenberg | Halo2 (`halo2_proofs`) |
| --- | --- | --- |
| Evaluated version | Noir `v1.0.0-beta.26`; Barretenberg `v5.2.0` | `halo2_proofs 0.3.5` |
| Model | Noir DSL -> ACIR -> Barretenberg proof backend | Rust library implementing a PLONK-family proving system |
| Private/public inputs | Native private inputs; `pub` marks public inputs | Explicit circuit advice/instance columns in Rust |
| Integer support | Native range-constrained `u32` and comparison | Requires circuit/gadget design for range/comparison constraints |
| Setup | Barretenberg uses public CRS/SRS material; cache must be provisioned for offline use | Library documentation describes no trusted setup; parameters are generated/handled locally for the circuit configuration |
| Key lifecycle in this experiment | Circuit-specific verification key generated locally from the compiled synthetic circuit; proof, witness, and key outputs are disposable test artifacts and are not committed | Would require an explicit local parameter/key lifecycle in a future implementation |
| Default verification dependency | Local `bb` binary; no hosted verifier required | Local Rust binary/library; no hosted verifier required |
| Licensing / provenance | Noir source declares MIT OR Apache-2.0. The Barretenberg `bb` CLI package metadata in the upstream `aztec-packages` tree declares MIT, but the standalone `v5.2.0` release repository used for the benchmark binary does not expose a root license file. The binary was checksum-pinned, used ephemerally, and is not redistributed here; exact release-binary provenance/license mapping remains an **Open adoption blocker** before vendoring, redistribution, or architectural selection. | `halo2_proofs 0.3.5` declares MIT OR Apache-2.0; exact transitive dependency review would still be required before adoption |
| Repository integration | Small circuit source and thin subprocess adapter | Would add a Rust crate plus transitive dependency graph and more custom circuit code |
| Current disposition | **Implemented for benchmark evidence only** | **Evaluated; full implementation Deferred in v0** |

## Why Noir + Barretenberg is implemented first

For this first predicate, Noir directly represents a private `u32`, a public `u32`, and the `<=` constraint with minimal custom cryptographic code. That makes it useful for answering the immediate question: can the repository generate and independently verify a genuine private bounded-integer proof locally?

This convenience does not make the stack selected architecture. Barretenberg's CRS handling, exact binary provenance/license mapping, toolchain compatibility, proof characteristics, dependency lifecycle, and security posture remain subjects for later review.

## Why Halo2 implementation is Deferred in v0

Halo2 remains a credible comparison candidate because it is an open Rust library, exposes circuit-level control, supports local verification, and its current crate documentation describes it as a PLONK-family system without a trusted setup.

A comparable bounded-speed implementation would require a second non-trivial range/comparison circuit or gadget design plus a new Rust/transitive dependency graph. Doing that in the same first benchmark would mix the question “can we generate a genuine private bounded-integer proof?” with a larger custom-circuit and dependency-integration exercise. The additional dependency set would also need its own provenance review before repository adoption.

Accordingly, v0 evaluates Halo2's setup, integration, licensing, portability, and verification model but does not invent runtime or proof-size numbers for it. A later benchmark may implement it if comparison depth becomes decision-relevant. **Deferred here means outside this first benchmark, not rejected as a technology and not selected as architecture.**

## Setup and trust observations

For the implemented candidate, the Barretenberg CRS used by the benchmark is public setup material. It is not treated as a secret key or evidence of telemetry provenance. The benchmark generates its circuit-specific verification key locally and keeps all witness, proof, and key files disposable. No production trust root, credential, hosted verifier, vendor account, live ledger, or policy service is involved.

These setup properties concern proof execution only. They do not upgrade `A0_SYNTHETIC`, establish sensor truth, trustworthy time, hardware integrity, continuous coverage, or any external compliance claim.

## Sources checked for this experiment

- Noir documentation/release: <https://noir-lang.org/docs/>
- Noir source/license: <https://github.com/noir-lang/noir>
- Barretenberg release binaries: <https://github.com/AztecProtocol/barretenberg/releases>
- Barretenberg source/package metadata: <https://github.com/AztecProtocol/aztec-packages/tree/master/barretenberg>
- Halo2 crate documentation: <https://docs.rs/halo2_proofs/0.3.5/halo2_proofs/>

Version and licensing observations are research inputs as of 2026-09-13; they are not legal approval, dependency-update policy, or authorization to vendor/distribute third-party material.
