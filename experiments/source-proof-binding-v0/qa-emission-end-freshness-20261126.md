# TAG / SOURCE-EMISSION-END-FRESHNESS-01 — local synthetic research record

**EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION**

Observed 2026-11-26 on Qube. GitHub live main resolved at 3b57779a38ff979be6a81a2fe5be5340c3a11286, merge of PR #195. Previously verified, not rerun: CI #45814276716 SUCCESS 4/4; Cloudflare Pages Production 17 findings/34 RO/EN articles; Chromium 6/6 PASS; SOURCE-EMISSION-END-CONSISTENCY-01 10/10 PASS. Consulted AGENTS.md, docs/README.md, docs/current-work-authorization.md, docs/delivery-plan.md, experiments/README.md and CONTRIBUTING.md from main. Local synthetic mandate only.

Six independent dimensions: Experimental / Synthetic evidence / Maintainer-reviewed (owner accepted local result on 2026-11-26; not independent) / Synthetic data / Local-only / No external assurance claim. Activity: Exploration permitted. No independent review or promotion.

## Method and invariant

Fixed two-epoch verifier policy (A,B), opaque identifiers with reverse lexical order, explicit trusted verifier-only transition from A to B. The two closure directories are enrolled explicitly at bootstrap; each reuses unchanged EndConsistency and check_closed. Current local state and simulated reference store a digest D(e)=SHA256(canonical([domain,scope,first,SHA256(test key),[A,B],e])). Reuse Checkpoint and its atomic writer and locking; state read and matching reference required before every admission or transition. Reference advanced first; a mismatch fails closed, no implicit repair. No new proof or authority. Transition policy is fixed configuration, not general authenticated administration or multi-epoch registry. For retained e, admission requires anchor.epoch=e and existing per-context authenticated closure checks. A historical authentic declaration is rejected when e=B. A matching pair restored to A makes that declaration idempotent again. No trusted time, source truth, physical completeness, real origin, or independent rollback guarantee.

## Reproduction on existing Qube sources

QA_SOURCE=/path/to/pinned-QA-source-checkout
EXPERIMENT_DIR=/path/to/experiment-directory

Local QA checkout HEAD 25de1b62b671d8966705e7538816ca3dc47d089b with local integration overlay; relied-on eight module hashes matched accepted finding 17, not represented as a clean checkout of current main. Python 3.14.4, existing bwrap, standard library. Run only:
```sh
bwrap --unshare-all --die-with-parent --new-session --ro-bind /usr /usr --symlink usr/bin /bin --symlink usr/lib /lib --symlink usr/lib64 /lib64 --proc /proc --dev /dev --tmpfs /tmp --ro-bind "$QA_SOURCE" /qa --ro-bind "$EXPERIMENT_DIR" /experiment --clearenv --setenv PATH /usr/local/bin:/usr/bin --setenv HOME /tmp --setenv PYTHONPATH /experiment:/qa/experiments/source-proof-binding-v0 --chdir /experiment python3 -B -m unittest -v test_emission_end_freshness
```

## Observed focal results

10/10 PASS, 0.033 s, PID 161478, FOCUSED_EXIT=0. Active ACCEPT; same epoch IDEMPOTENT and unchanged bytes; future B rejected before explicit transition and accepted after; historical A independently passes existing check_closed in A but rejected TERMINAL_EPOCH_NOT_CURRENT in B, unchanged bytes; B-to-A rejected EPOCH_TRANSITION_NOT_AUTHORIZED; restart retains B and rejects A replay without changes; malformed/missing current reference fails closed; restoration of current state alone rejected STATE_REFERENCE_MISMATCH; restoration of current state and local reference accepts old A IDEMPOTENT (expected negative control, not a security guarantee); stale session re-reads current epoch and rejects A. All fixtures fabricated using existing test-only fixtures. No production data. No proving, GitHub write, CI, provisioning, deployment or TAG #88 changes.

## SHA-256

emission_end_freshness.py f13f6c128b0f80894f96a0f22e2a1bd5c5b3b15c1e7a925f3acc03a9c7787aed
test_emission_end_freshness.py fbadaa372f08746fda9cfef97ee0a38d4c4a473fb2452dc3347060a907b2cde3
emission_end_consistency.py e1eff540d447397004e73f93a1ae4b6a57076bb6ddf708ed658ea8205fb9d896
emission_end_anchor.py 0c563a41541aa98ee6851981eb0fc6cc0f93a3d87cb54871b1b0a64872db6645
emission_gap.py 0600618467b11db422e043b0da5f3633fac344a4ac14614d3d61588a75bb5f32
test_emission_end_anchor.py 53317e43e99f78b740a0dc8a1f7ae58f76585d7e9168053a21622d2cdd897a83
test_emission_gap.py 83e1cdbcb86ed2543988fbf540e55e33522f9010e156f41b50d3adc6c2f389f6
binding_reference.py 62f26929d9eede6ccaca20a279eec31a3e2f62ea5926ff264e9b344c87837f78
persistent_unified.py ab91b905f4733ad460c0cfdd520ef95824e4e51ced9a8c44107cb0b4f79fa894
state_rollback.py 0264112c89df16e1adc99ec477f93a2554499f71f8233824b00ae58c123124f9

## Cleanup and limits

Sandbox exited 0; temporary directories managed by unittest and disposable tmpfs. Post-run owned mode-0700 directory contained only the two source files; PID 161478 absent in ps. This sanitized evidence record retained alongside them. No runtime outputs or compiled bytecode. Existing QA inputs read-only. No concurrency stress, injected crash recovery, arbitrary epoch history, independent reference or real-time assurance tested. Pair rollback test restores both active-epoch copies, not the closure history; this suffices to admit A again. No automatic reconciliation implemented; only fail-closed comparison and reference-first ordering reused from the prior state model.

## Owner-accepted finding 18 — Draft integration only, not published

RO: Într-un experiment sintetic, păstrarea epocii active de către verificator și tranziția explicită către o epocă distinctă permit respingerea unei declarații terminale istorice, chiar dacă aceasta rămâne autentică și validă în contextul original. Restaurarea simultană a stării și a referinței locale permite însă readmiterea declarației; fără o referință independentă nu se poate garanta prospețimea contextuală împotriva unei asemenea restaurări.

EN: In a synthetic experiment, verifier-retained active epoch state and an explicit transition to a distinct epoch enable rejection of a historical terminal declaration even when it remains authentic and valid in its original context. Restoring both local state and the local reference can nevertheless admit the declaration again; without an independent reference, contextual freshness cannot be guaranteed against such restoration.

Owner accepted the scientific result and authorized focused Draft integration on 2026-11-26. Ready, merge and publication remain separate decisions.

Original local evidence SHA-256: 8f4918b1f52eafe121e629215ab8aa905ac144ceb1a7724a1f0d1ba82da5bef4.
Integration adds only the unittest.main entrypoint to the test file for the existing gate. Integrated test SHA-256: dee83b6a3f45de20226d54fcd8c406d76c66e738ded6ff709e67e9884a0ce396; direct script execution in the same isolated namespace model: 10/10 PASS, 0.035 s, PID 164592, ENTRYPOINT_EXIT=0. Implementation unchanged.
