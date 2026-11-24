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

## Unified synthetic source assurance — cryptographic VALID

On 24 November 2026 the unified sequential flow checked verifier-owned
key authorization, the synthetic signature and session-local temporal gate,
then reconstructed the 34 public inputs (32 digest bytes, limit 500 cm/s,
version 1) independently and verified the retained proof once with pinned
Barretenberg 5.2.0 and compatible checked CRS. Verification exited 0 (VALID).
The staged temporal state was committed only after verification succeeded.
Proof and verification-key SHA-256 values are pinned in `unified.py`.
No new proof, circuit compilation or SITL run was needed.

The reference accepts the retained proof and VK as caller-provided bytes;
`local_bb_verifier` requires the pinned local executable and CRS. Those
private QA proof artifacts are not published. Run the offline composition
tests with `python3 -B experiments/source-proof-binding-v0/test_unified.py`;
they use a mock verifier and dummy artifacts, not a fresh cryptographic run.
The real result is recorded evidence, not a publicly reproducible proof
package. The real run accepted one synthetic capture; replay/regression
rejections and state rollback were tested separately with a mock verifier.
The experiment establishes neither real source identity, independent trusted
time, restart-safe replay protection, sensor truth nor interval coverage.

## Restart-persistent temporal integrity — SOURCE-TEMPORAL-PERSISTENCE-01

Separate Qube QA on 24 November 2026: 10/10 focused tests passed, including
a strengthened restart check with two successive child processes. Tests
used the existing synthetic signed fixture and a mock proof verifier.
The preceding real cryptographic VALID result is reused, not rerun; no
new cryptographic execution is claimed for the persistence extension.

`PersistentUnified` wraps the unchanged sequential verifier. It requires
an explicitly initialized, verifier-owned private directory (0700), a
trusted local Linux filesystem and cooperating writers. Directory locking
serializes read/check/proof/commit; each call reloads the state. The single
0600 canonical JSON file contains version, hashed enrollment/verifier
context, two numeric watermarks and an unkeyed corruption checksum. No raw
observations, signing keys, proofs or witnesses are stored there. Missing,
malformed or incompatible state fails closed in normal reopen mode.

A successful proof callback precedes file fsync, atomic replacement and
directory fsync. Failure before replacement leaves the old state intact;
failure after replacement but before directory fsync returns no acceptance,
yet may consume the observation. No power-loss durability experiment was
run. The directory and its ancestors must be trusted and must not be moved,
replaced or edited by uncooperative actors. Explicit initialization is a
trusted provisioning action, not an automatic recovery/reset operation.

The checksum detects accidental corruption, not deliberate modification.
Restoring a valid historical file was tested and allows replay; deletion
followed by privileged reinitialization also resets history. No rollback
resistance, independent trusted time, semantic duplicate detection after
resigning, key rotation, real identity or interval coverage is claimed.

Reproduce offline with `python3 -B experiments/source-proof-binding-v0/test_persistent_unified.py`.
The repository tests use dummy proof/VK bytes and patched test pins instead
of private QA artifacts. The underlying proof binding and verifier interface
are unchanged. No persistent service, real telemetry or TAG #88 change.


## Authenticated reception freshness — SOURCE-TRUSTED-TIME-01

Qube QA, 24 November 2026, baseline main
`ab7eae18caed6aa1b19436b6e1202b205b76a96c`: 12/12 focused tests
passed (0.015 s, exit 0) after correcting the test-only key length in
the fixture. The first run rejected the invalid fixture at initialization;
no implementation security check was weakened. Eight reused files matched
their main Git blob IDs. The previous real cryptographic VALID result
is reused, not rerun. The tests use dummy proof/VK bytes and a mock
proof verifier; the proof input interface remains unchanged.

`TrustedTimeUnified` wraps the existing persistent verifier. A simulated
ingress authority uses a separate public synthetic HMAC-SHA256 test key.
The domain-separated MAC binds verifier scope, the canonical capture hash
(excluding the replaced untrusted trust store), and attested ingress time.
The verifier uses its separately configured decision clock and a half-open
admission window [ingress, ingress + max_age), with zero future tolerance
and a 1000 ms example bound. The authority must actually observe the
capture at ingress; the source cannot select the verifier clock or key.

Tests reject stale/future, missing/invalid and tampered references, modified
capture metadata or frames, wrong authority/scope and unavailable clocks.
They check replay rejection after reopening (even with a new receipt),
unchanged persistent state for tested rejections and proof failure, and
unchanged reconstructed proof inputs. The test also explicitly accepts
fresh ingress of potentially old sensor data. Time is checked at admission,
not proof completion. No real time service, physical capture time, clock
synchronization or clock rollback resistance is established. The existing
historical-state rollback limit still applies; neither real source identity
nor interval coverage is established.

Reproduce offline: `python3 -B experiments/source-proof-binding-v0/test_trusted_time.py`.
No new proof generation/verification, real telemetry or TAG #88 changes.
Exact tested source SHA-256:
- trusted_time.py: `6a60224d207a710a6b5d7262a61102f886f6f7036b2bc103ff3e206cc6cbf0ac`
- test_trusted_time.py: `679b9d26cd980263217fa33c79cbb20ace37a66fb982dc184bf44ad91f27643a`


## Finite synthetic reception coverage — SOURCE-INTERVAL-COVERAGE-01

Qube QA, 24 November 2026, main
`80e1101c8a932ba6e1b6ef26ab6b07b28a5c8f5e`: 12/12 focused tests
passed (0.042 s, exit 0) on the first isolated execution; nine reused
source/fixture files matched their main Git blobs. Disposable runtime
cleanup passed. Original experiment SHA-256:
`a6a934ed5e0da243451edef85ef402346bd50861e93b4c2c0c652e2912493971`.
The original one-file experiment was split into a reference module and
regression tests; integration also handles malformed pair shapes and
unavailable decision clocks explicitly. The preceding single-observation
cryptographic VALID evidence is reused, not rerun. All interval tests
use public synthetic keys, deterministic signed fixture observations,
dummy proof/VK bytes and a mock proof verifier.

The verifier owns the start of a half-open 300 ms reception interval.
Exactly three ordered captures are required at nominal 10 Hz, centered
at start + 50, 150 and 250 ms (inclusive ±10 ms tolerance), with exactly
one primary observation per capture. The separate simulated ingress
authority authenticates each receipt; the trusted decision clock is
sampled once at admission after the interval closes. The example
freshness policy is 1000 ms, with zero future tolerance. Signed source
timestamps and primary boot counters must strictly increase across
captures; equal boot values are rejected even with a fresh signature.
This is a fixed synthetic sampling model, not a general mission profile.

While holding the original persistent-state lock, the existing verifier
checks each capture against private temporary staged state. Only after
all three accept does it replace the original watermark once. Missing
or extra observations, slot gaps, duplicates/replay, regressions,
tampered/unauthenticated inputs, stale receipts, and proof callback
rejection do not advance the original state in the tested cases. A
subsequent valid interval can be accepted after reopening. The existing
filesystem assumptions and post-replace fsync uncertainty still apply;
no crash, power-loss or hostile-filesystem resistance was measured.

Completeness means one authenticated reception per expected slot in
this model, not continuous physical observation, physical capture time,
or sensor truth. Re-signing with new counters can still disguise semantic
duplicates. Interval identities and overlap history are not persisted;
the caller must choose the trusted interval, and global interval
uniqueness/coverage is not established. No aggregate proof or fresh ZKP
verification, real time service, real telemetry, or TAG #88 changes.

Reproduce offline:
`python3 -B experiments/source-proof-binding-v0/test_interval_coverage.py`.
