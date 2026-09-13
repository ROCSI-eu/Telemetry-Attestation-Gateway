# Candidate assessment

> **EXPERIMENTAL · SYNTHETIC_ONLY · NOT VALIDATION OR PRODUCTION AUTHORIZATION**

This is a bounded feasibility comparison, not an architecture decision or security review.

| Dimension | Noir + Barretenberg | Halo2 (`halo2_proofs`) |
| --- | --- | --- |
| Evaluated version | Noir `v1.0.0-beta.26`; Barretenberg `v5.2.0` | `halo2_proofs 0.3.5` |
| Model | Noir DSL -> ACIR -> Barretenberg proof backend | Rust library implementing a PLONK-family proving system |
| Private/public inputs | Native private inputs; `pub` marks public inputs | Explicit circuit advice/instance columns in Rust |
| Integer support | Native range-constrained `u32` and comparison | Requires circuit/gadget design for range/comparison constraints |
| Setup | Barretenberg uses public CRS/SRS material; cache must be provisioned for offline use | Library describes no trusted setup; parameters are generated/handled locally for the circuit configuration |
| Default verification dependency | Local `bb` binary; no hosted verifier required | Local Rust binary/library; no hosted verifier required |
| Licensing | Noir: MIT OR Apache-2.0; Barretenberg/Aztec tooling reviewed as external experimental dependency and not vendored here | MIT OR Apache-2.0 |
| Repository integration | Small circuit source and thin subprocess adapter | Would add a Rust crate plus transitive dependency graph and more custom circuit code |
| Current disposition | **Implemented for benchmark evidence only** | **Evaluated, not implemented in v0** |

## Why Noir + Barretenberg is implemented first

For this first predicate, Noir directly represents a private `u32`, a public `u32`, and the `<=` constraint with minimal custom cryptographic code. That makes it useful for answering the immediate question: can the repository generate and independently verify a genuine private bounded-integer proof locally?

This convenience does not make the stack selected architecture. Barretenberg's CRS handling, toolchain compatibility, proof characteristics, dependency lifecycle, and security posture remain subjects for later review.

## Why Halo2 remains a comparison candidate

Halo2 is credible for a future deeper comparison because it is an open Rust library, exposes circuit-level control, supports local verification, and its current crate documentation describes it as a PLONK-family system without a trusted setup. For this v0 experiment, implementing it would require a second non-trivial circuit/gadget implementation plus a new Rust dependency graph. That adds substantial integration work before the project has even established the first proof feasibility result.

Accordingly, v0 records Halo2's setup/integration/licensing characteristics but does not manufacture benchmark numbers for it. A later benchmark may implement it if the first proof result shows that proof-system comparison is worth deepening.

## Sources checked for this experiment

- Noir documentation/release: <https://noir-lang.org/docs/>
- Noir source/license: <https://github.com/noir-lang/noir>
- Barretenberg releases: <https://github.com/AztecProtocol/barretenberg/releases>
- Halo2 crate documentation: <https://docs.rs/halo2_proofs/0.3.5/halo2_proofs/>

Version observations are research inputs as of 2026-09-13; they are not dependency-update policy.
