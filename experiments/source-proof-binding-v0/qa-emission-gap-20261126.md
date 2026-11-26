# SOURCE-EMISSION-GAP-01 — local synthetic evidence

**EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION**

Observed 2026-11-26 on Qube. Scope: local-only experiment authorized by owner; no integration or publication. Main baseline observed in preceding turn: 7985b3fd5a3605fc45b0740482323c4a86cd9890. Rules consulted: AGENTS.md, docs/README.md, docs/current-work-authorization.md, docs/delivery-plan.md, experiments/README.md. Existing QA source copy from aggregate research reused read-only. During Draft integration all seven listed dependency hashes matched the exact main checkout. Original local evidence SHA-256: 1cb62f3ff428614b5a8ac91c42bc79758542cd0ec41daa2ec5f8e0ece2b87430; this copy redacts host paths and records owner acceptance.

Artifact profile: Experimental / Synthetic evidence / Maintainer-reviewed (owner accepted local result on 2026-11-26; not independent review) / Synthetic data / Local-only / No external assurance claim.

## Hypothesis and method
Under an assumed honest test index authority, independently authenticated observation indices within one verifier-selected scope and epoch reveal a gap before a later received index, starting at a verifier-owned first index. Reuse test_temporal_gate.sample and binding_reference.authorized_digest (existing synthetic fixture authentication); no new simulator, proving or verifier callback. Separate deterministic test-only HMAC key, domain TAG/QA/EMISSION-INDEX/v1 and canonical encoding bind scope, epoch, index and authorized observation digest. Check each MAC and expected epoch before continuity; reject the complete batch on failure. No persistent state changes.

Invariant: for all supplied authenticated records j in [0,n), index_j = first + j, under fixed trusted scope and epoch. A larger index signals a gap relative to that anchor; a smaller index signals replay/regression relative to the expected index. This does not imply physical coverage or prove honest index assignment.

## Reproduction
Set QA_SOURCE to an absolute checkout of the baseline, and EXPERIMENT_DIR to the absolute directory containing the two new Python files (experiments/source-proof-binding-v0 in this integration).
Python 3.14.4; bubblewrap 0.11.1; standard library and existing synthetic QA sources, no network. The experiment directory and QA source are read-only in the isolated runtime. Private tmpfs, new namespaces, clean environment; no bytecode writes.

```sh
bwrap --unshare-all --die-with-parent --new-session \
  --ro-bind /usr /usr --symlink usr/bin /bin --symlink usr/lib /lib \
  --symlink usr/lib64 /lib64 --proc /proc --dev /dev --tmpfs /tmp \
  --ro-bind "$QA_SOURCE" /qa \
  --ro-bind "$EXPERIMENT_DIR" /experiment \
  --clearenv --setenv PATH /usr/local/bin:/usr/bin --setenv HOME /tmp \
  --setenv PYTHONPATH /qa/experiments/source-proof-binding-v0 \
  --chdir /experiment python3 -B -m unittest -v test_emission_gap
```

SHA-256 of local implementation and tests:
- emission_gap.py: 0600618467b11db422e043b0da5f3633fac344a4ac14614d3d61588a75bb5f32
- test_emission_gap.py: 83e1cdbcb86ed2543988fbf540e55e33522f9010e156f41b50d3adc6c2f389f6

Reused QA source hashes (relative to experiments/):
- source-proof-binding-v0/binding_reference.py: 62f26929d9eede6ccaca20a279eec31a3e2f62ea5926ff264e9b344c87837f78
- source-proof-binding-v0/persistent_unified.py: ab91b905f4733ad460c0cfdd520ef95824e4e51ced9a8c44107cb0b4f79fa894
- source-proof-binding-v0/test_temporal_gate.py: a84f519e7a7da5767c511d5ba5f96ed64b9582b62378a78a64d7960a8b393cd1
- source-proof-binding-v0/temporal_gate.py: 29dac8a413704a1fbc19b30e2444ff8052a4207aec08227b93dc5f3f404b5683
- source-proof-binding-v0/unified.py: d758d2d04566717d009e52588e461e43317d6fd0bbace616917161dc9b30762c
- mavlink-normalization-v0/fixtures.json: 6ecd5049e49a2cd661eb132db4248ebb35bb2d5fc8ef4afd94150f8bbaf659bf
- mavlink-normalization-v0/mavlink_normalize.py: b3c16ed8cc93d234eb9f4e91b42a1ca4bdb786793e8d8666aacb17b2c774cc91

## Observed execution
9/9 PASS, 0.008 s, exit 0, process 67169 exited. All nine test methods reported ok:
- authenticated_wrong_epoch: reject EPOCH_MISMATCH
- consecutive: accept consecutive supplied records
- duplicate: reject INDEX_REPLAY_OR_REGRESSION
- index_bound_to_observation: reject INDEX_NOT_AUTHENTIC
- missing_prefix_with_anchor: reject EMISSION_GAP
- numbered_message_omitted: reject EMISSION_GAP
- unanchored_tail_indistinguishable: accepted prefix, no authenticated end
- unnumbered_physical_event_indistinguishable: two hypothetical histories project to identical visible records and equal result
- wrong_index_authentication: reject INDEX_NOT_AUTHENTIC for altered index and wrong test key

## Interpretation and limitations
A missing numbered observation is detectable when the verifier has an anchor and a later authenticated index, conditional on honest source-side issuance. A hypothetical unnumbered physical event produces no extra evidence. Without an authenticated end index, a missing suffix and a stopped source remain indistinguishable. HMAC establishes the test credential's binding, not real origin, truthful capture, independent physical time or an honest source. No source-loss attribution, epoch transition protocol, persistent state, receiver-time receipt check, aggregate proof binding, real data, general wire-format hardening or external assurance tested. The counterexample is an analytic synthetic projection tested for equality, not a physical measurement. Existing aggregate ZKP and atomic watermark PASS checkpoints reused as background only, not rerun or claimed to cover the new index.

## Cleanup and disposition
Sandbox process exited; private tmpfs released on namespace exit, no persistent runtime, proof, capture, socket, or bytecode artifact created by this experiment. Post-run directory inspection showed only the two source files; preserve these and this sanitized evidence in the owned private QA directory (mode 0700). Existing QA sources and toolchain preserved. No GitHub write, CI, provisioning, proving, deployment, journal publication, or TAG #88 change. Local execution complete and owner accepted for Draft integration on 2026-11-26. Ready, merge and actual publication remain distinct decisions.
