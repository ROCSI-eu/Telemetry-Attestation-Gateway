# SOURCE-INTERVAL-AGGREGATE-CRYPTO-E2E-01 — local synthetic experiment, 25 November 2026

**EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION**

**Status/scope:** local research experiment FINAL/PASS, 25 November 2026. Not independent external validation, product or proof-design promotion, pilot or production authority. Draft-only repository integration is not Ready, merge or deployment authorization.

## Question and method

Can a genuine ZKP for exactly three ordered, test-key-signed synthetic frames be verified using public inputs independently reconstructed by the verifier, with exactly one atomic source-watermark commit after cryptographic acceptance, and no commit for rejected proof material?

Verifier-owned synthetic interval policy: three authenticated simulated reception slots 100 ms apart; existing source-signature, boot-counter, replay, ingress-receipt, state and lock checks. Three distinct signed synthetic GLOBAL_POSITION_INT fixture captures were admitted. The prover used exactly those private primary frame bytes. The verifier independently reconstructed 98 public field inputs (3 × 32 BLAKE2s digest bytes, fixed speed limit 500 cm/s and version 2). The exact Noir circuit binds each private frame to its authenticated digest and checks the fixed per-frame speed limit. This does not certify physical samples between the supplied frames.

The 25 November local Qube QA run used bubblewrap with network/user isolation, unprivileged execution, read-only host/toolchain, private writable temporary runtime, bounded time and memory; no downloaded tools or services. Pinned Nargo 1.0.0-beta.26 and Barretenberg 5.2.0, noir-recursive target and previously verified public BN254 CRS were reused. Noir source: experiments/source-proof-binding-v0/interval-zkp-v0/src/main.nr, SHA-256 098c49802636cd3b2407868e091144b25dbaa3e79baa26eeb5e0688104a4f814; recovered from the original CRS-DIAGNOSTIC-01 procedure, byte-identical. Exactly one proof was created in this E2E run.

## Reused prior verified checkpoints — not rerun

- 24 November: 34/34 original non-cryptographic mock integration tests PASS; mock context/verification key and public version 1 are distinct from cryptographic version 2.
- 25 November: source-recovery SHA-256 PASS; standalone aggregate ZKP proving and independent verification PASS, 98 public fields, 14,656-byte proof, six negative controls. The original proof was cleaned up and was not used as a substitute for the E2E proof.
- 25 November: adapter checks 43/43 local PASS (9 new + 34 affected existing); these tested the commit barrier with a simulated callback, not real cryptography.

## New end-to-end evidence

One new genuine ZKP proof was generated for the exact three captures admitted by the aggregate adapter. The independent bb verifier accepted it using 98 public field inputs reconstructed from the authenticated captures, followed by **one** atomic persistent-watermark update; reopened state matched the expected watermark [100005,1200]. The same interval was rejected on replay after commit.

- Proof: 14,656 bytes, SHA-256 9316a04c673d3940c0373986251d615a0e7b677d78863a2118b12d0a55e99526. Witness and proof were **not retained**.
- VK: 3,680 bytes, SHA-256 942b463decd9b1f6ab58369b0ab16f8412cf769d0e8cf137e4ea5862ef644fba. Pinned verifier context; local generation is **not independent governance**.
- Digest of ordered three synthetic authenticated-frame digests, SHA-256 6a1b6c365983b3582d202f485b07f0e823da8e653f73dc7626ae6c4f224b36a8.
- One locally observed execution (seconds): compile 0.297; write_vk 0.167; nargo witness 0.285; bb prove 0.318; real verifier **plus atomic commit** 0.117. These are not general benchmarks.
- Before commit, missing proof, wrong VK, mutated proof and a different fully authenticated synthetic sequence each returned UNVERIFIABLE without changing the watermark; the same interval replay was rejected without another write. UNVERIFIABLE is intentionally fail-closed and does not distinguish invalid from operationally unavailable cryptography.
- Reopened persistent QA state recovered the expected watermark; private runtime cleanup PASS. Temporary witness, private data, proof, VK, CRS copy and state were removed. No private/test signing key, witness, proof or test frame is published in this record.

## Reproducibility and integration limits

The local candidate adapter and tests were preserved with SHA-256 manifest in the TAG development workspace. Integrate only the minimal main-compatible changes: separate mock and cryptographic aggregate adapters, 98 public fields with version 2, strict VK pin, explicit atomic commit barrier, source/receipt/interval checks and focused standard-library tests. Three shared helpers require carefully bounded refactoring; unchanged main behavior must remain compatible. Routine CI does not run cryptographic proving or download CRS. No production code, operational gateway, TAG #88, live endpoint or public browser proving path is authorized.

**Limitations:** Cryptographic validity covers only these three supplied synthetic captures, not physical continuous reception, sensor truth, real source provenance or independent time, physical power-loss durability, adversarial host security, independent VK lifecycle, exactly-once external acknowledgment, real-world safety/compliance, or MVP/product readiness. No real vehicle, hardware, participant, customer, or restricted data were used. This is A0_SYNTHETIC laboratory evidence only.

Checkpoint: local E2E FINAL/PASS, repository contribution Draft-only. Public journal addition requires maintainer acceptance and separate approval for merge/automatic Cloudflare Production publication.
