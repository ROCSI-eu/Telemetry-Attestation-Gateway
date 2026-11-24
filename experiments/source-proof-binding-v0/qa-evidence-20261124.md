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

## Verifier-owned source-key authorization (reference integration)

`binding_reference.authorized_digest` reuses the normalization parser and
returns the same BLAKE2s proof input only after checking a verifier-owned
enrollment (slot, alias, SHA-256 key fingerprint, active flag) and signature.
The verifier supplies the symmetric key and requested alias independently of
capture data. Capture-supplied trust is replaced. The synthetic slot is
restricted to `1:1:7`; absent/revoked enrollment and valid signatures under
unregistered keys cannot produce an authorized digest.

Run `python3 -B experiments/source-proof-binding-v0/test_binding.py` offline.
This is a reference integration, not a new ZKP run or a public proof package.
The public fixture keys establish neither real key custody nor identity; the
capture-local time checks do not provide independent freshness or replay
protection across captures. No persistent service or production policy changes.

## Sequential verifier-session temporal integrity (reference integration)

`TemporalGate.accept` reuses `authorized_digest` and returns its unchanged
digest only after checking the signed timestamps and source boot time against
the last accepted capture. The verifier retains two numeric watermarks in
memory for one fixed synthetic enrollment and sequential calls. Rejected
captures do not advance either watermark. Capture metadata cannot reset them.

Run `python3 -B experiments/source-proof-binding-v0/test_temporal_gate.py`.
The tests cover replay, cross-capture regression, rejected-state isolation
and preservation of the authorized digest. No raw observation is retained.
This is session-local ordering only: restart loses history, concurrent use
and key rotation are outside the model, a freshly signed duplicate payload
may pass, and neither timestamp establishes independently trusted time.
No new proof run, persistent service, or production policy change.
