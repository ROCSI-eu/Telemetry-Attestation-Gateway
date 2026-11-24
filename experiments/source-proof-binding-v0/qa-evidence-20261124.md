# SOURCE-AUTHENTICITY-02 — synthetic proof binding (24 November 2026)

**EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION**

## Verified Qube QA result

On 24 November 2026, one controlled local research experiment used the existing
`signed-valid` MAVLink 2 synthetic capture. Its test signature was checked
before an independent BLAKE2s digest was computed over the complete 53-byte
signed `GLOBAL_POSITION_INT` frame.

The corrected standalone Noir circuit (source SHA-256
`956699405bfd017d67358a3506def3f1c51a6ba4204536c4c379f2687bd98aa6`)
bound that private frame to the public digest and proved its horizontal speed
satisfied the public limit of **500 cm/s**. One real zero-knowledge proof was
generated using Nargo `1.0.0-beta.26` and Barretenberg `5.2.0` with the
`noir-recursive` verifier target.

A separate verification step recomputed the digest from the signature-checked
synthetic fixture, reconstructed all 34 public field inputs independently of the
prover, and returned **cryptographic VALID**. The verification key was copied
into the verifier's workspace before witness creation.

The proof measured 14,656 bytes and the verification key 3,680 bytes. The
one-shot experiment exited successfully, with no retry. Private proof and
verification artifacts remain in restricted Qube QA evidence; the witness,
raw frame, and temporary workspaces were not retained or published.

## What this does — and does not — establish

**Established:** For this synthetic observation, the generated proof was
cryptographically bound to the independently signature-checked signed frame
rather than to an arbitrary speed supplied by the prover.

**Not established:** Real vehicle identity, custody or authorization of a
hardware signing key, trustworthy timestamps, whole-mission coverage, sensor
truth, policy approval, operational suitability, or production readiness.
The signing key is a publicly known **test key**. This note is a sanitized
experimental result, not an independently reproducible public proof package.

Existing unrelated SITL end-to-end experiments and the persistent Qube TAG #88
service were not altered. No real telemetry, deployment, or public verifier was
involved.
