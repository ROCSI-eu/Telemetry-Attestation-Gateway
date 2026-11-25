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


## Continuity between synthetic reception intervals — SOURCE-INTERVAL-CONTINUITY-01

Qube QA, 24 November 2026, main
`acd24951c02588484be14cb45f0315aa251993f8`: 16/16 focused tests
passed (0.283 s, exit 0). Ten reused source/fixture Git blob pins matched
the baseline. Maintainer accepted the finding on 24 November 2026.
The 13/13 interval-coverage checkpoint is reused, not rerun locally.
The tests use the existing deterministic signed synthetic fixture,
simulated ingress-time authority and mock per-observation proof verifier.
No new ZKP generated or verified.

A baseline counterexample accepted two individually valid intervals
with an entire interval missing between them. The separate continuity
reference adds a verifier-owned initial anchor and an exact next-start
requirement to the existing 300 ms, three-slot, 10 Hz, +/-10 ms model.
The original lock and atomic writer commit the source watermark and
next expected interval start in one version-2 record. Scope binds the
source policy, initial anchor, slot policy, age and time-key fingerprint.
Version-1 state is not migrated; a separate private state directory is
required. Gap, overlap and replay reject before the proof callback.

Three contiguous intervals (nine observations) accepted with matching
reconstructed per-observation inputs. Wrong initial anchor, missing
interval, 1 ms gap/overlap, replay, reverse order, invalid receipt/source
signature, missing/misordered slots and negative mock verification were
rejected. Restart in another process retained continuity. Corrupt state
and changed anchor were rejected. Injected pre-replace failure preserved
the prior record; post-replace directory fsync failure returned no
acceptance and reopening reconciled the record, refusing replay.
The tests use private temporary state; the isolated process completed,
and no captures, witnesses, proofs or test state were retained.

Reproduce offline with
`python3 -B experiments/source-proof-binding-v0/test_interval_continuity.py`.
Python 3.14.4; the recorded run used the existing network-isolated bwrap
sandbox, read-only host, clean environment and disposable writable /tmp.
Exact tested source SHA-256:
- interval_continuity.py: `5fe18baf2d3b326ba4c500f25916a241bed7f6816f21d66aeca6faadfe45b5a2`
- test_interval_continuity.py: `cdf65c1fadb1e5ede0201e3bf0e1edd1353723c2f35af6b27787633d1e4d204d`

Profile: Experimental / Synthetic evidence / Maintainer-reviewed /
Synthetic data / Local-only / No external assurance claim.
Continuity applies only to admitted synthetic reception intervals.
Physical acquisition continuity, real identity/time and rollback
resistance are not established. Trusted cooperative filesystem assumed;
no power-loss durability test, no automatic retry after ambiguous commit,
no policy for resuming after an unrecoverable gap. Aggregate ZKP remains
a separate open question. No hardware, real telemetry, deployment or
TAG #88 change. EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC ·
NOT VALIDATION OR PRODUCTION AUTHORIZATION.

Draft integration delta: first repository-root run was 15/16 with a
child-process import error (test working directory). Only the restart
test invocation was corrected to use its module directory. Reference
implementation SHA-256 unchanged. Corrected test SHA-256:
`e8d05ddc779354639f7f0f502130494d256ef2de872c8ff9cc9d26ead057e324`.
Repository-root isolated rerun: 16/16 PASS (0.304 s); static public bundle
13/13 PASS (0.233 s), including bilingual continuity finding. No proving.


## Recovery after synthetic reception discontinuity — SOURCE-INTERVAL-RECOVERY-01

Qube QA, 24 November 2026, main
`d1079d9548011ad784909ed4c04dd8789f93b091`: 13/13 focused tests
passed (0.336 s, exit 0). Twelve reused source/fixture Git blob pins
matched the baseline. Maintainer accepted the result on 24 November
2026. Prior continuity 16/16 and public bundle 13/13 PASS are reused.
The test uses deterministic signed synthetic fixtures, simulated ingress
time and a mock proof verifier; no new proof generated or verified.

A separate version-3 state uses the existing private-directory lock and
atomic writer, retaining the global signed/boot watermark, accepted
half-open segments and a pending gap in one record. The verifier explicitly
declares an irrecoverable forward gap; an untrusted capture cannot
implicitly trigger recovery. A separate synthetic HMAC authority binds
authorization to scope, watermark, accepted segments and exact gap.
Only a fully accepted interval opens the new segment. Coverage requires
containment within a single accepted segment, never across a gap.

Tests cover gap declaration, unauthorized/wrong-target recovery, late
fill denial, replay with fresh authenticated receipts, source boot
regression, negative mock verification, invalid final receipt, stale
recovery authorization, a genuine child-process restart, atomic
pre-replace failure and bounded history. The experimental cap is 16
segments, with fail-closed recovery rather than eviction. A declared
gap survives rejection and restart; adjacent segment boundaries retain
historical discontinuities. The existing post-replace uncertainty is
reused, not retested. No physical capture time, physical coverage,
source-reset or key-rotation support, actual access-control service,
anti-rollback protection against historical state restoration, hostile
filesystem or power-loss qualification is established. Irrecoverability
is a verifier-side assumption, not cryptographically established.
No recovery before the first accepted interval or automatic retargeting.

Reproduce offline with
`python3 -B experiments/source-proof-binding-v0/test_interval_recovery.py`.
Python 3.14.4; existing network-isolated bwrap, host read-only, disposable
writable /tmp, completed and cleaned. No new dependencies. Exact tested
source SHA-256:
- interval_recovery.py: `b18bb4ed925ca83d8d2f16db9568c283866d3255e54281da7c2e4ee77724f6f6`
- test_interval_recovery.py: `e82acfa1c5a41286457a1c6a2c9dbc31d8bc01a37333bd6c0842619a33231c92`

Profile: Experimental / Synthetic evidence / Maintainer-reviewed /
Synthetic data / Local-only / No external assurance claim.
EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC ·
NOT VALIDATION OR PRODUCTION AUTHORIZATION.
SOURCE-INTERVAL-ZKP-01 remains PENDING. No TAG #88 change.


## Valid historical state restoration — SOURCE-STATE-ROLLBACK-01

Qube QA, 24 November 2026, main
`61ac69400b8594ab16975f1e9b84972a6575b01a`: 12/12 focused tests
passed (0.452 s, exit 0). Fourteen reused source/fixture Git blob pins
matched the baseline. Maintainer accepted the result on 24 November
2026 and authorized Draft integration only. Recovery 13/13 and static
bundle 14/14 PASS are reused, not rerun for unchanged inputs.

Existing deterministic signed synthetic fixtures, simulated ingress
time and recovery authority, mock proof verifier. No new proof generated
or verified. The legacy counterexample restores a valid historical v3
record, fills the declared gap and admits an already accepted interval,
then reports contiguous synthetic coverage. A separate simulated trusted
reference stores the SHA-256 digest of the entire canonical record,
binding scope, recovery policy, global watermark, segments and pending
gap. Reuse the existing lock, atomic writer and v3 integrity checks.
Compare before admission, declaration, recovery, coverage and reopen.
Compare-and-advance the reference before local commit; no success on
partial commit and no automatic reseed or repair of mismatching pairs.

Tests cover intact recovery, historical local-state rollback, same-watermark
pending-gap rollback, preservation of the gap, corrupt state versus valid
reference mismatch, absent/malformed/inconsistent reference, reference
write failure, local write failure after reference advance, actual process
restart and the expected negative control: restoring both records coherently
permits replay and loss of interruption history. Mismatch establishes
divergence, not attribution or proof of rollback direction.

Reproduce offline with
`python3 -B experiments/source-proof-binding-v0/test_state_rollback.py`.
Python 3.14.4; existing network-isolated bubblewrap, read-only host,
disposable writable /tmp; sandbox exited and test state cleaned.
Exact tested new source SHA-256:
- state_rollback.py: `e5bcbd52726da5cedd62ccee6f30ccb880619331e2ac157d53adb3b1e61529de`
- test_state_rollback.py: `7525cec0214457a69d2c588f7cde9878dd5027ccd4f82fcaa4bc500549015d54`

Profile: Experimental / Synthetic evidence / Maintainer-reviewed /
Synthetic data / Local-only / No external assurance claim.
Separate directories on one host simulate, but do not provide, independent
rollback domains. Digest equality does not establish reference origin or
freshness; the reference must be trusted and independently retained.
Two writes are not a distributed atomic transaction; partial commit
sacrifices availability, with no automatic reconciliation. No hostile-host,
concurrent direct file mutation, power-loss, real independent service,
real source/time, physical coverage or operational anti-rollback claim.
No proving, no SOURCE-INTERVAL-ZKP-01 or TAG #88 changes.
EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC ·
NOT VALIDATION OR PRODUCTION AUTHORIZATION.

Draft integration: static bilingual bundle 15/15 PASS (0.247 s);
documentation check PASS (32 Markdown files). Staged whitespace check
identified one extra terminal blank line in each new source; removed
only those lines and ran the focused suite again, 12/12 PASS (0.446 s,
exit 0), same isolation. Final integrated source SHA-256:
- state_rollback.py: `0264112c89df16e1adc99ec477f93a2554499f71f8233824b00ae58c123124f9`
- test_state_rollback.py: `6177ab536ee5ea0d0f520620831ecc6b638a652c3a64f6c2d168786eff07d4e1`

## SOURCE-STATE-RECONCILIATION-01 — 25 November 2026

**EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION**

Non-cryptographic prototype: no proof generated or verified.
Activity: Exploration permitted. Maintainer accepted the local result on 25 November 2026 and authorized Draft integration only.
Profile: Experimental / Synthetic evidence / Maintainer-reviewed / Synthetic data / Local-only / No external assurance claim.

### Provenance and scope

Live GitHub main was confirmed as 7bc490547701af2a466a5acefa1cc46aa9e2d63c,
PR #186 merged. AGENTS.md, docs/README.md, docs/current-work-authorization.md,
docs/delivery-plan.md, experiments/README.md, CONTRIBUTING.md and the existing
rollback evidence were consulted. Prior rollback 12/12, static 15/15, CI
#45473257221 SUCCESS and Production FINAL/PASS (ten RO/EN findings) reused;
not rerun. Qube source archive created from the exact local Git commit object,
no network fetch or shared checkout mutation. Existing deterministic signed
synthetic fixtures, mock proof verifier and simulated reference only.

### Hypothesis and method

Retain one bounded canonical v3 candidate before reference advance, using the
existing atomic writer. Normal open still fails closed on a mismatch.
Explicit reconciliation requires a valid local record, a valid prepared
record in the same scope, a matching trusted current reference, and exactly
one admissible forward structural transition (first/next interval, declared
gap or recovery). Both watermarks must strictly increase for admission;
gap declaration retains the exact watermark and segments. Reuse the v3
parser, original local lock, reference lock and atomic writer. No reference
advance, proof callback, history rewrite, or automatic reseed on repair.
Candidate stays as one bounded file; superseded on the next prepared write.
Bootstrap reconciliation is excluded. No migration or production design.

### Execution

Python 3.14.4; existing bubblewrap with isolated user/network namespace,
read-only host, private /tmp tmpfs, cleared environment.
From experiments/source-proof-binding-v0:
    bwrap --unshare-user --unshare-net --die-with-parent --ro-bind / / --dev /dev --proc /proc --tmpfs /tmp --clearenv --setenv PATH /usr/bin:/bin --setenv HOME /tmp --chdir "$PWD" /usr/bin/python3 -B test_state_reconciliation.py

Observed 11/11 PASS, 0.306 s unittest duration, exit 0, process 42094
completed (reported runtime 0.63 s). First run. Focused cases:
1. Interrupted interval commit: normal reopen rejected; explicit repair succeeds, replay rejected.
2. Interrupted gap declaration: same watermark, pending gap preserved.
3. Interrupted recovery: both historical segments preserved, no bridging, replay and late fill rejected.
4. Historical candidate with current reference rejected.
5. Historical reference plus historical candidate rejected against newer local state.
6. Missing candidate rejected.
7. Malformed candidate rejected.
8. Missing reference rejected.
9. Matching pair: explicit repair refused, not proof of freshness.
10. Separate process after repair: history retained and replay rejected before mock proof call.
11. Negative control: restoring local, reference and candidate together allows replay and erases the gap; expected limitation, not evidence of rollback resistance.

Injected failure at local atomic replace after reference advancement;
no real crash or power-loss test. Rejections check local/reference bytes and
proof callback count; successful repair checks byte-identical candidate,
unchanged reference, no proof callback. Runtime state in private tmpfs;
sandbox exited. Source and sanitized evidence retained for reproducibility.

SHA-256:
- state_reconciliation.py: a0a562632a643b5b1d8afbf245c817cbbd7213786871619c646d20454ac86e56
- test_state_reconciliation.py: 1f2e2452bf0ad06fc70f267544424888fb183ffa353f64a4c869ee55195d06fb

### Limits and recommendation

Current trusted reference is an assumption; same-host simulated directories
are not independent rollback domains. A matching digest establishes
consistency, not origin, freshness or actual time. Prepared state is
not an authenticated transition log; structural forward checks and trusted
reference are necessary assumptions, not proof of historical execution.
A missing, corrupt, non-adjacent or mismatching candidate/local/reference
cannot be recovered by this method. No concurrent uncooperative writers,
hostile filesystem, fsync/power-loss durability, multi-transition recovery,
independent reference service or production recovery qualification.
Prior post-replace uncertainty remains; no guarantee of exactly-once external
acknowledgement. No raw observation stored by candidate, no fresh proving,
no real telemetry, no deployment, no GitHub write, no CI, no modification
of SOURCE-INTERVAL-ZKP-01 (PENDING) or TAG #88.

Draft integration authorized on 25 November 2026: retain these limits and
negative control, register in the existing gate and add one public-safe
bilingual journal finding. No Ready/merge/deployment authorization inferred.

Draft integration check: the two experimental source SHA-256 pins matched
the accepted local run. The staged base tree matched the exact main tree.
Static bilingual bundle 16/16 PASS (0.279 s); documentation check PASS
(32 Markdown files); staged diff check PASS. No rerun of unchanged
11/11 experiment locally; the existing mandatory PR gate covers it.

## SOURCE-STATE-CRASH-CONSISTENCY-01 — 25 November 2026

**EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION**

Profile: Experimental / Synthetic evidence / Maintainer-reviewed / Synthetic data / Local-only / No external assurance claim. Maintainer accepted the finding and authorized Draft integration on 25 November 2026. Non-cryptographic prototype; no proof generated or verified.

Baseline: main `2aea4f4a221634167b710ac273b0957ef4389d0f`, PR #187 merged; previously verified reconciliation 11/11, static bundle 16/16, CI #45555874588 SUCCESS and Production 11/11 bilingual findings. AGENTS.md, current authorization and experimental workspace rules consulted. Reused checkpoint evidence, not rerun.

Question: what happens when the process terminates at each update boundary? Existing deterministic signed synthetic fixtures, mock proof verifier, simulated independent reference and private v3 state. Qube Python 3.14.4, bubblewrap 0.11.1, isolated user/network namespaces, read-only host, private writable tmpfs, cleared environment. Child process exits abruptly with status 73 at the selected call boundary; surviving test process opens a new session.

Observed first run: 5/5 PASS, 0.125 s, exit 0. Local probe SHA-256 `7987099f0c56458bf1027322f2e038cf4b7cc2f82665bbbabcb4033887fdeaf1`; sanitized result SHA-256 `484038f740b1237b0f1d5e0ef37fad9e63570d44ce7601c7c939024359a9ab9c`. Reused reconciliation source SHA-256 `a0a562632a643b5b1d8afbf245c817cbbd7213786871619c646d20454ac86e56`, rollback source SHA-256 `0264112c89df16e1adc99ec477f93a2554499f71f8233824b00ae58c123124f9`.

- Before candidate replace: old local/reference/prepared files unchanged; normal reopen succeeds, reconciliation not required, subsequent replay rejected.
- After candidate preparation before reference advance: candidate alone is not authoritative; old matching pair remains usable.
- After reference advance before local replace: normal open rejects divergence; explicit forward reconciliation preserves both historical segments and the gap; replay and historical local regression rejected.
- After local replace before directory fsync: new record visibly matches reference on reopen; replay rejected. No claim of physical durability or acknowledgement semantics.
- Malformed candidate or missing reference: fail closed, no automatic reseed.

Reproduce offline: `python3 -B experiments/source-proof-binding-v0/test_state_crash_consistency.py` (Linux). The integration removes the local absolute import path and unused assignment only. Integrated test SHA-256: `58949519972ca7773a7532763098f8165042f7636319a081bc2e5eb629988261`.

Limitations: process termination in tmpfs is not power-loss, whole-host restart or persistent-media recovery testing. Same-host directories do not establish independent rollback domains. Two updates are not a distributed atomic transaction. The earlier joint-restoration counterexample remains: restoring all three historical copies can permit replay and erase gap history. Matching digest does not prove freshness, origin or source truth. No exactly-once external acknowledgement, hostile-host or multi-transition recovery qualification. Runtime tmpfs discarded on sandbox exit. SOURCE-INTERVAL-ZKP-01 remains PENDING; TAG #88 unchanged. No proving, hardware, real telemetry or deployment.

Draft integration delta: portable focused probe 5/5 PASS (0.126 s), static bilingual bundle 17/17 PASS (0.281 s), documentation check PASS (32 Markdown files), all exit 0 in the same isolated runtime. No unrelated suites rerun locally. The existing mandatory PR gate remains unchanged.
