# TAG / SOURCE-EMISSION-END-CONSISTENCY-01 — local synthetic research record

**EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION**

Observed 2026-11-26 on Qube. Repository main resolved in GitHub at `25de1b62b671d8966705e7538816ca3dc47d089b`, PR #194 MERGED. Previously verified, not rerun: CI #45762484311 SUCCESS, Cloudflare Pages Production 16 findings and 32 RO/EN mini-articles, Chromium 6/6 PASS, SOURCE-EMISSION-END-ANCHOR-01 local 13/13 PASS. Rules read from main: AGENTS.md, docs/README.md, docs/current-work-authorization.md, docs/delivery-plan.md, experiments/README.md, CONTRIBUTING.md. Local work only: no GitHub write, CI, deployment, provisioning, proving, TAG #88 change, hardware, real telemetry or network.

**Six independent artifact dimensions (owner accepted local result, 2026-11-26):** implementation `Experimental`; evidence `Synthetic evidence`; review `Maintainer-reviewed — owner accepted local result; not independent`; data `Synthetic data`; permitted environment `Local-only`; external claims `No external assurance claim`. Activity `Exploration permitted`. No promotion is implied. The owner separately accepted the finding and authorized Draft integration; not independent review or publication. Original test fixtures are fabricated local values, not physical measurements or source data.

## Question, method and scope

Can a verifier detect two *individually authentic* terminal declarations with different final indices for the same verifier-owned `(scope, epoch, first)`, retaining the first closure after a conflict, without claiming the declared terminal index is truthful?

Reused unchanged `emission_end_anchor.check_closed` for authenticated observation indices and terminal HMAC; reused `state_rollback.Checkpoint` and its existing `PersistentUnified._locked` / `_write` for an owned mode-0700 local directory, one mode-0600 atomic digest file and fail-closed read. Added only a small, local glue class `EndConsistency`; no new proof, protocol, trust root, key, registry or infrastructure. Initial enrollment is explicit; restart cannot silently enroll a missing reference. The model requires one stable, verifier-owned checkpoint directory **per context**; it makes no global uniqueness claim if different checkpoints are used.

`C = [TAG/QA/EMISSION-END-CONSISTENCY/v1, scope, epoch, first, SHA256(test_index_key)]`. The initial local checkpoint is `SHA256(canonical([C, UNSET]))`. For a checked terminal declaration `A=(epoch,final,mac)`, define `D(A)=SHA256(canonical([C,final,mac]))`. First admissible `A` replaces UNSET with D(A); a later identical D(A) is idempotent; a different D(A) that first passes `check_closed` yields `TERMINAL_CLOSURE_CONFLICT` without changing D(A). The pre-existing test-only terminal MAC authenticates `(scope,epoch,first,final)`; a matching local digest does not authenticate any physical event. Mock checkpoint retention is an assumption, not an independent service.

## Local reproduction

Source files used: existing Qube checkout `<pinned-QA-source-checkout>` (checkout commit `7985b3fd5a3605fc45b0740482323c4a86cd9890`; relied-on modules compared by SHA-256 to the accepted source, not claimed to be a full checkout of later main). Work in owned mode-0700 directory `<experiment-directory>`. Python 3.14.4, bubblewrap present, standard library; no installs or downloads.

```sh
QA_SOURCE=/path/to/pinned-qa-source-checkout
EXPERIMENT_DIR=/path/to/experiment-directory
bwrap --unshare-all --die-with-parent --new-session \
  --ro-bind /usr /usr --symlink usr/bin /bin --symlink usr/lib /lib \
  --symlink usr/lib64 /lib64 --proc /proc --dev /dev --tmpfs /tmp \
  --ro-bind "$QA_SOURCE" /qa --ro-bind "$EXPERIMENT_DIR" /experiment \
  --clearenv --setenv PATH /usr/local/bin:/usr/bin --setenv HOME /tmp \
  --setenv PYTHONPATH /experiment:/qa/experiments/source-proof-binding-v0 \
  --chdir /experiment python3 -B -m unittest -v test_emission_end_consistency
```

## Observed execution (one focal run)

Ten test methods PASS in 0.022 s, process PID 136884 exit 0; explicit shell marker `FOCUSED_EXIT=0`. Cases:
1. First authenticated valid declaration: `ACCEPT`; persisted checkpoint file mode 0600.
2. Byte-identical repeated closure: `IDEMPOTENT`, no state change.
3. Two independent valid sequence+end checks (final 3, final 4; same scope/epoch/first): second rejected `TERMINAL_CLOSURE_CONFLICT`.
4. Reverse conflict order (4 then 3): rejection; original 4 remains idempotent.
5. Modified final with original MAC and wrong-scope MAC: `END_NOT_AUTHENTIC`; retained bytes unchanged.
6. Separated verifier-owned checkpoints for alternative scope, epoch and initial index: independent `ACCEPT`.
7. After conflict, reopening the original persistent checkpoint: original declaration `IDEMPOTENT`, conflicting declaration still rejected, bytes unchanged.
8. Malformed or missing persistent reference on restart: fail closed `REFERENCE_UNAVAILABLE_OR_INVALID`.
9. Missing terminal anchor: `END_ANCHOR_MISSING`, original initial checkpoint unchanged.
10. Honest stop at 3 versus authentic but falsely declared stop at 3 after a hidden fourth emission: identical verifier-visible inputs and accepted checkpoint digest; false declaration remains undetectable.

Test code covers controlled restart; it does not claim verified crash recovery midway through filesystem commit, adversarial concurrency, rollback resistance, or authentic reference ownership beyond the test filesystem. In particular, a validly formatted malicious replacement of the mock checkpoint cannot be distinguished without a genuinely independently trusted reference.

## SHA-256 source manifest

- `emission_end_consistency.py`: `e1eff540d447397004e73f93a1ae4b6a57076bb6ddf708ed658ea8205fb9d896`
- `test_emission_end_consistency.py`: `a96c65d9ca10aa819d010449d7a6fc93a1d66548ba7497534da5774355665f8a`
- Reused `emission_end_anchor.py`: `0c563a41541aa98ee6851981eb0fc6cc0f93a3d87cb54871b1b0a64872db6645`
- Reused `test_emission_end_anchor.py`: `53317e43e99f78b740a0dc8a1f7ae58f76585d7e9168053a21622d2cdd897a83`
- Reused `emission_gap.py`: `0600618467b11db422e043b0da5f3633fac344a4ac14614d3d61588a75bb5f32`
- Reused `test_emission_gap.py`: `83e1cdbcb86ed2543988fbf540e55e33522f9010e156f41b50d3adc6c2f389f6`
- Reused `binding_reference.py`: `62f26929d9eede6ccaca20a279eec31a3e2f62ea5926ff264e9b344c87837f78`
- Reused `persistent_unified.py`: `ab91b905f4733ad460c0cfdd520ef95824e4e51ced9a8c44107cb0b4f79fa894`
- Reused `state_rollback.py`: `0264112c89df16e1adc99ec477f93a2554499f71f8233824b00ae58c123124f9`

## Scientific interpretation / limitation

The minimal synthetic closure uniqueness invariant is `ACCEPT(C,A_1) => ACCEPT(C,A_1)=IDEMPOTENT and ACCEPT(C,A_2)=CONFLICT` for any later individually valid `A_2` with the same retained context and different terminal index. This describes a conditional local state machine, **not** physical completeness. Local closure conflicts are evaluated after the reused complete sequence check; distinct verifier-owned checkpoint directories are explicitly enrolled for separate contexts. A single authentic, false but consistent endpoint passes exactly as an honest endpoint when no independent expected endpoint is available. HMAC authentication does not establish truthful source behavior, trusted time, physical coverage, real hardware identity, or an independent authority. A missing endpoint is not proof of source omission. No ZKP or promotion decision was performed.

## Cleanup and disposition

Focal sandbox exited 0; bwrap namespace and `tmpfs /tmp` discarded. Test `TemporaryDirectory` contexts were disposed. Post-run owned directory enumeration showed precisely two retained Python source files, no runtime output, state databases, logs, private keys or compiled bytecode. PID 136884 had no active bwrap/unittest runner. QA sources, pinned tooling and existing public Production assets were not rewritten. Retain this sanitized local evidence record and two source files only. Owner accepted finding 17 and authorized Draft integration on 2026-11-26; Ready, merge and publication are separate decisions. Original local evidence SHA-256: 1f561d3ee67676feb1c2c36b480f76f514763e08902815d5f80e0b4ad941b83d.

**Owner-accepted finding 17 — Draft integration only; not published.**
RO: Într-un experiment sintetic, păstrarea unei referințe terminale autentificate într-o stare locală stabilă permite acceptarea idempotentă a repetării și detectarea unei închideri autentificate contradictorii pentru același domeniu, aceeași epocă și același indice inițial. Prima declarație poate totuși fi falsă și consecventă; fără referință independentă nu se poate stabili acoperirea reală.
EN: In a synthetic experiment, retaining an authenticated terminal reference in stable local state enables idempotent repetition and detection of a conflicting authenticated closure for the same scope, epoch and initial index. The first declaration may nevertheless be false yet consistent; without an independent reference, real coverage cannot be established.
