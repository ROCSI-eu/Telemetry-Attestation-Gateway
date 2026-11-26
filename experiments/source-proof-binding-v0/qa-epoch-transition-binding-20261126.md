# TAG / SOURCE-EPOCH-TRANSITION-BINDING-01 — local synthetic research record

**EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION**

Observed on Qube, 2026-11-26. Live GitHub main resolved to 4f8584fd341ad07f9b328cfe1ea638af54fce1a7 (PR #196 merged). Previously verified, not rerun: CI #45820664622 SUCCESS; Cloudflare Pages Production FINAL/PASS, 18 findings and 36 RO/EN articles; Chromium Production 6/6 PASS; SOURCE-EMISSION-END-FRESHNESS-01 10/10 PASS. Consulted AGENTS.md, docs/README.md, docs/current-work-authorization.md, docs/delivery-plan.md, experiments/README.md, CONTRIBUTING.md and prior QA record from main. Local synthetic mandate only.

Six independent dimensions: Experimental / Synthetic evidence / Maintainer-reviewed (owner accepted the scientific result on 2026-11-26; not independent) / Synthetic data / Local-only / No external assurance claim. Activity: Exploration permitted. No independent review, promotion or publication.

## Method and invariant

Reuse EndFreshness, EndConsistency and Checkpoint unchanged. Extend only the transition entrypoint, preserving the fixed verifier-owned pair (A,B) and the existing locked state/reference comparison and reference-first update. Epochs are opaque (reverse lexical order). HMAC-SHA256 with the existing synthetic fixture key and distinct prefix TAG/QA/EPOCH-TRANSITION/v1 followed by NUL authenticates canonical([scope, previous, successor]). The fixture key is reused deliberately; domain separation is not independent key ownership or a new trust root. The key is pinned in the inherited state context. Verify the exact four-field shape, MAC and scope before invoking the unchanged base transition, which re-reads current state under lock and checks the exact directed pair. No new persistence format. For well-formed authorization and consistent available state/reference:
ADMIT iff AUTH_VALID and SCOPE_MATCH and PREVIOUS_ACTIVE and SUCCESSOR_AUTHORIZED.
Invalid or missing reference fails closed. This is a fixed-policy laboratory model, not an epoch management protocol or a public API security boundary; no claim about arbitrary in-process callers or authority legitimacy.

## Reproduction

Python 3.14.4; existing bwrap; standard library. Reused the prior integration source archive (no .git metadata; not represented as a clean main checkout). Ten directly relevant existing module/test hashes below matched the previously recorded finding 18 hashes, including its integrated test entrypoint. No download or provisioning. The prior 10/10 suite was not rerun.

QA_SOURCE=/path/to/pr196-integration-source-archive
EXPERIMENT_DIR=/path/to/experiment-directory

```sh
bwrap --unshare-all --die-with-parent --new-session --ro-bind /usr /usr --symlink usr/bin /bin --symlink usr/lib /lib --symlink usr/lib64 /lib64 --proc /proc --dev /dev --tmpfs /tmp --ro-bind "$QA_SOURCE" /qa --ro-bind "$EXPERIMENT_DIR" /experiment --clearenv --setenv PATH /usr/local/bin:/usr/bin --setenv HOME /tmp --setenv PYTHONPATH /experiment:/qa/experiments/source-proof-binding-v0 --chdir /experiment python3 -B -m unittest -v test_epoch_transition_binding
```

## Observed results

15/15 PASS, 0.027 s, PID 174798, FOCUSED_EXIT=0. Valid A-to-B accepted; existing terminal gate accepts B and rejects historical A. Mutation of scope, previous, successor without remac rejected TRANSITION_NOT_AUTHENTIC; wrong MAC/key likewise. Authenticated wrong scope rejected TRANSITION_SCOPE_MISMATCH; authenticated wrong previous or successor, replay through stale session, and authentic reverse rejected EPOCH_TRANSITION_NOT_AUTHORIZED. Restart preserves state; reject helper compares all four state files byte-for-byte. Missing/malformed reference fails closed; restoration of current state alone rejected STATE_REFERENCE_MISMATCH. Both current copies restored to A: authentic A-to-B authorization accepted again (expected counterexample, not prevention). Index MAC substituted as transition MAC rejected; extra field rejected. Only fabricated fixtures, no real telemetry, hardware, network, proving, GitHub write, CI, provisioning, deployment or TAG #88 changes.

## SHA-256

epoch_transition_binding.py 2d6d58955706c28083fcb6265a73241f7d2d7e2e599d667f402d9c29b4741bc7
test_epoch_transition_binding.py 4a8783195363274229b7ee2218a7d32d7a0485af4b1f4c4854fcf28f6a2a6eb9
emission_end_freshness.py f13f6c128b0f80894f96a0f22e2a1bd5c5b3b15c1e7a925f3acc03a9c7787aed
emission_end_consistency.py e1eff540d447397004e73f93a1ae4b6a57076bb6ddf708ed658ea8205fb9d896
emission_end_anchor.py 0c563a41541aa98ee6851981eb0fc6cc0f93a3d87cb54871b1b0a64872db6645
emission_gap.py 0600618467b11db422e043b0da5f3633fac344a4ac14614d3d61588a75bb5f32
binding_reference.py 62f26929d9eede6ccaca20a279eec31a3e2f62ea5926ff264e9b344c87837f78
persistent_unified.py ab91b905f4733ad460c0cfdd520ef95824e4e51ced9a8c44107cb0b4f79fa894
state_rollback.py 0264112c89df16e1adc99ec477f93a2554499f71f8233824b00ae58c123124f9
test_emission_end_freshness.py dee83b6a3f45de20226d54fcd8c406d76c66e738ded6ff709e67e9884a0ce396
test_emission_gap.py 83e1cdbcb86ed2543988fbf540e55e33522f9010e156f41b50d3adc6c2f389f6
test_emission_end_anchor.py 53317e43e99f78b740a0dc8a1f7ae58f76585d7e9168053a21622d2cdd897a83

## Cleanup and limits

Sandbox exited zero. Temporary directories managed by unittest and disposable tmpfs. Post-run owned mode-0700 directory contained only the two source files, no bytecode or runtime outputs. Existing QA inputs read-only. Retain only source and sanitized research record. No concurrency stress, injected crash recovery, arbitrary epoch history, key lifecycle or independent reference tested. Pair rollback restores current state and its mock reference, not closure history. No trusted time, authority legitimacy, source truth, real provenance, physical completeness or protection against simultaneous rollback established.

## Owner-accepted finding 19 — Draft integration only, not published

RO: Într-un experiment sintetic, autentificarea domeniului și a perechii direcționale de epoci, combinată cu starea curentă reținută de verificator și politica sa fixă, permite respingerea autorizărilor modificate, emise pentru alt context sau reutilizate după tranziție. Restaurarea simultană a stării și a referinței locale permite însă reutilizarea autorizării autentice; autentificarea nu garantează singură prospețimea tranziției.

EN: In a synthetic experiment, authenticating the scope and directed epoch pair, combined with verifier-retained current state and its fixed policy, enables rejection of altered authorizations, authorizations issued for another context, and replay after transition. Restoring both local state and its local reference nevertheless permits reuse of the authentic authorization; authentication alone does not guarantee transition freshness.

Owner explicitly accepted finding 19 and authorized focused Draft integration on 2026-11-26. Ready, merge and publication remain separate decisions. Original local evidence SHA-256: b596f3a0bdc1f9d5e9d64c468f4807a85216d4fe87f8182dfa39e559d719260b. Implementation and focal tests unchanged.
