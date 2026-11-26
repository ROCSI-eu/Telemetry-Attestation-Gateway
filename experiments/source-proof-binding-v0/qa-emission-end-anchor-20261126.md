# SOURCE-EMISSION-END-ANCHOR-01 — local synthetic evidence

**EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION**

Observed 2026-11-26 on Qube. Main resolved via GitHub: 4bb5174854c7f1de674c7a2f94a2440274c44456. Rules consulted: AGENTS.md, docs/README.md, docs/current-work-authorization.md, docs/delivery-plan.md, experiments/README.md, CONTRIBUTING.md. Owner mandate: isolated local research only. PR #193 merged, CI #45756534600 SUCCESS, Production 15 findings / 30 RO/EN articles, and SOURCE-EMISSION-GAP-01 9/9 PASS are reused checkpoints, not rerun. Prior record: experiments/source-proof-binding-v0/qa-emission-gap-20261126.md.

Artifact profile: Experimental / Synthetic evidence / Maintainer-reviewed (owner accepted the local result and Draft integration on 2026-11-26; not independent) / Synthetic data / Local-only / No external assurance claim. Activity: Exploration permitted.

## Hypothesis and method
Reuse check_sequence with verifier-owned scope, epoch, first index, separate synthetic index test key and existing authenticated observation fixtures. Add a closed-sequence wrapper requiring a terminal HMAC-SHA256 on canonical([scope, epoch, first, final]) with distinct domain TAG/QA/EMISSION-END/v1 plus NUL. Same test-only index key, distinct domain; not a new independent authority. Validate the existing sequence before validating the exact terminal fields, range, MAC, expected epoch, then endpoint equality. No persistent state or proof. For nonempty records, accept iff existing check_sequence succeeds, the terminal declaration authenticates in context, and last index equals final. With an honest terminal authority, this establishes supplied index continuity from first through declared final, not physical coverage.

## Reproduction
Python 3.14.4, bubblewrap 0.11.1, standard library. Set QA_SOURCE to the pinned existing aggregate QA source checkout, GAP to the prior experiment directory (both prior Python files), EXPERIMENT_DIR to the two new files. In an integrated copy the GAP directory can be the source-proof-binding-v0 directory of the exact main checkout. The seven dependency hashes and two gap hashes below matched the previously accepted record; no downloads, provisioning or proving.

```sh
bwrap --unshare-all --die-with-parent --new-session \
  --ro-bind /usr /usr --symlink usr/bin /bin --symlink usr/lib /lib \
  --symlink usr/lib64 /lib64 --proc /proc --dev /dev --tmpfs /tmp \
  --ro-bind "$QA_SOURCE" /qa --ro-bind "$GAP" /gap \
  --ro-bind "$EXPERIMENT_DIR" /experiment --clearenv \
  --setenv PATH /usr/local/bin:/usr/bin --setenv HOME /tmp \
  --setenv PYTHONPATH /gap:/qa/experiments/source-proof-binding-v0 \
  --chdir /experiment python3 -B -m unittest -v test_emission_end_anchor
```

SHA-256:
- emission_end_anchor.py: 0c563a41541aa98ee6851981eb0fc6cc0f93a3d87cb54871b1b0a64872db6645
- test_emission_end_anchor.py: 53317e43e99f78b740a0dc8a1f7ae58f76585d7e9168053a21622d2cdd897a83
- emission_gap.py: 0600618467b11db422e043b0da5f3633fac344a4ac14614d3d61588a75bb5f32
- test_emission_gap.py: 83e1cdbcb86ed2543988fbf540e55e33522f9010e156f41b50d3adc6c2f389f6

Reused QA sources (relative to experiments/):
- source-proof-binding-v0/binding_reference.py: 62f26929d9eede6ccaca20a279eec31a3e2f62ea5926ff264e9b344c87837f78
- source-proof-binding-v0/persistent_unified.py: ab91b905f4733ad460c0cfdd520ef95824e4e51ced9a8c44107cb0b4f79fa894
- source-proof-binding-v0/test_temporal_gate.py: a84f519e7a7da5767c511d5ba5f96ed64b9582b62378a78a64d7960a8b393cd1
- source-proof-binding-v0/temporal_gate.py: 29dac8a413704a1fbc19b30e2444ff8052a4207aec08227b93dc5f3f404b5683
- source-proof-binding-v0/unified.py: d758d2d04566717d009e52588e461e43317d6fd0bbace616917161dc9b30762c
- mavlink-normalization-v0/fixtures.json: 6ecd5049e49a2cd661eb132db4248ebb35bb2d5fc8ef4afd94150f8bbaf659bf
- mavlink-normalization-v0/mavlink_normalize.py: b3c16ed8cc93d234eb9f4e91b42a1ca4bdb786793e8d8666aacb17b2c774cc91

## Observed execution
13/13 test methods PASS, 0.013 s; shell PID 74492 completed exit 0 (runtime 0.26 s). Actual outcomes:
- complete: ACCEPT (1,2,3,4)
- missing_suffix: prefixes of lengths 1,2,3 accepted by old check but rejected by closed check with TERMINAL_EMISSION_GAP against final=4.
- absent: END_ANCHOR_MISSING
- modified, wrong_key, wrong_scope_or_start, wrong_mac_domain: END_NOT_AUTHENTIC
- wrong_epoch: END_EPOCH_MISMATCH
- conflicting_final: END_INDEX_CONFLICT
- invalid_final (zero, bool, overflow): INVALID_END_ANCHOR
- internal_gap_still_rejected: EMISSION_GAP
- unnumbered_event: different hypothetical histories project to identical visible inputs and equal ACCEPT.
- authentic_false_end: honest three-emission history vs four-emission history with withheld fourth and false authenticated final=3 project to identical visible inputs and equal ACCEPT.

## Interpretation and limitations
The terminal suffix is detectable relative to an authentic, truthful declared endpoint, not an independently established physical endpoint. A missing anchor rejects closed-sequence acceptance but does not itself prove omission. HMAC binds the test credential, scope, epoch and endpoints; no real source identity, independent authority, clock trust, truthful numbering, physical completeness or source-loss attribution. Same-epoch stale/contradictory anchors not globally reconciled: no freshness, unique closure enforcement, epoch lifecycle, persistent state, or ZKP binding tested. Empty sequences remain rejected by the reused checker; no empty-interval closure protocol claimed. These are analytic synthetic counterexamples, not physical measurements. No changes to prior experiment or #88.

## Cleanup and disposition
Sandbox exited 0; private tmpfs released with namespace exit; read-only host mounts and no bytecode writes. Post-run inspection showed exactly two new source files in owned mode-0700 directory, no runtime artifacts. Preserve sources and this sanitized record only for reproducibility. Existing QA tooling and sources preserved. No GitHub write, CI, proving, provisioning, deployment or journal update. Local execution complete; owner accepted the result and Draft integration on 2026-11-26. Ready, merge and actual publication remain distinct decisions. Original local evidence SHA-256: fcaee7ef7179a60b3e95b35e642bc359f7e8cd20b6dcd024fd5a8766ee163fd5.

Owner-accepted finding 16 (Draft integration only; not published):
RO: O referință terminală autentificată permite detectarea observațiilor numerotate lipsă la sfârșitul unei secvențe, în raport cu limita declarată. În modelul sintetic, o declarație autentică, dar falsă, poate ascunde o omisiune. Acoperirea fizică, originea reală și timpul de încredere rămân nedemonstrate.
EN: An authenticated end reference enables detection of missing numbered observations at the end of a sequence relative to the declared endpoint. In the synthetic model, an authentic but false declaration can conceal an omission. Physical coverage, real origin and trusted time remain unestablished.
