# TAG / SOURCE-EPOCH-TRANSITION-CONSISTENCY-01 — local synthetic research record

**EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION**

Observed on Qube, 2026-11-26. GitHub main resolved to 7088124bd9df2a83a97bcffbde7f1fb39eb67196; PR #197 merged baseline supplied by owner. Previously verified, not rerun: CI #45826676774 SUCCESS 4/4; Cloudflare Pages Production FINAL/PASS; 19 findings and 38 RO/EN articles; Chromium Production 6/6 PASS; SOURCE-EPOCH-TRANSITION-BINDING-01 15/15 PASS. Consulted AGENTS.md, docs/README.md, docs/current-work-authorization.md, docs/delivery-plan.md, experiments/README.md, CONTRIBUTING.md and prior QA record from main. Local synthetic mandate only.

Six dimensions: Experimental / Synthetic evidence / Maintainer-reviewed (owner accepted the scientific result on 2026-11-26; not independent) / Synthetic data / Local-only / No external assurance claim. Activity: Exploration permitted. No independent review, promotion or publication.

## Question and method

Can a verifier detect two authentic authorizations for the same scope and previous opaque epoch with distinct successors, independently of active-epoch admission? Reuse transition_mac from epoch_transition_binding.py (domain-separated HMAC-SHA256 of canonical scope, previous, successor), and Checkpoint/canonical/BindingRejected used by emission_end_consistency.py. Reuse existing test-only key and synthetic fixture authorizations. One explicitly pre-enrolled slot per (scope, previous, test key), two private local directories, separate state/reference digests; context includes version and key digest. Verify exact shape, MAC and slot context before mutation. Under the existing state lock, compare retained state to mock reference; if empty, advance reference first and write state, if equal to candidate return IDEMPOTENT, otherwise raise TRANSITION_AUTHORIZATION_CONFLICT. No active epoch or allowed-successor policy is consulted; either authentic successor may be observed first. ACCEPT denotes observation only, never permission to execute a transition.

For correctly enrolled and retained context, two well-formed authentic authorizations:
AUTH_VALID(a1) AND AUTH_VALID(a2) AND SAME_SCOPE AND SAME_PREVIOUS AND DIFFERENT_SUCCESSOR => CONFLICT (assuming collision resistance and retained matching state/reference).
No global registry, order of epochs, clock, consensus or determination of legitimate successor. SHA-256 digests are commitments, not independent authority. Conflict does not itself persist the second authorization or identify a valid winner.

## Reproduction

Python 3.14.4; existing /usr/bin/bwrap; standard library only. Reused the retained PR197 integration source archive (not asserted to be a clean main checkout); 12 directly relevant source/test hashes matched the finding 19 record. No download, dependency provisioning or rerun of previous 15/15 suite.

QA_SOURCE=/path/to/pr197-integration-source-archive
EXPERIMENT_DIR=/path/to/experiment-directory

```sh
bwrap --unshare-all --die-with-parent --new-session --ro-bind /usr /usr --symlink usr/bin /bin --symlink usr/lib /lib --symlink usr/lib64 /lib64 --proc /proc --dev /dev --tmpfs /tmp --ro-bind "$QA_SOURCE" /qa --ro-bind "$EXPERIMENT_DIR" /experiment --clearenv --setenv PATH /usr/local/bin:/usr/bin --setenv HOME /tmp --setenv PYTHONPATH /experiment:/qa/experiments/source-proof-binding-v0 --chdir /experiment python3 -B -m unittest -v test_epoch_transition_consistency
```

## Observed results

13/13 PASS; 0.119 s; PID 190062; FOCUSED_EXIT=0; process completed exit 0. First authentic authorization accepted, identical repeat idempotent and both conflicting orders detected (each successor accepted independently when first). Invalid MAC before/after first observation, wrong fixture key and changed successor with original MAC rejected without state change; extra field rejected. Other scope and other previous epoch rejected by wrong slot and accepted in distinct enrolled slots. Fresh child Python process reopens slot, observes idempotent and conflict, both state copies unchanged. Malformed or absent reference fails closed on observation and reopening, without implicit re-enrollment. State-only restoration rejected STATE_REFERENCE_MISMATCH. Both copies restored to their empty snapshot: previously conflicting successor accepted, original authorization then rejected as conflict. This is the expected negative control, not rollback prevention.

## SHA-256

epoch_transition_consistency.py 87c857c9f7349034f32d9a5980244b7a234a79553f36a7f86ce53c2979665a1a
test_epoch_transition_consistency.py efa555fa467f5a1e9c4816795569364627128417c776c4178e51701b5cf74069 (corrected integration test; original local test bc6bb09234147252860b0ca0c094a5567ff02eb3cafd044546877394d4d291fd)
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

## Cleanup, self-review and limitations

Qube sandbox exited zero; unittest temporary directories and disposable tmpfs removed on exit; post-run directory owned by local operator mode 0700, contained exactly the two source files, no bytecode or runtime outputs. Existing QA inputs read-only. Retain the two sources and sanitized research record. One preliminary search of Dev1 encountered inaccessible lost+found; no changes there, resolved by locating retained source under home QA. No real telemetry, hardware, network, proving, provisioning, GitHub write, CI, deployment or TAG #88 changes. No concurrent stress, injected crash recovery, arbitrary context substitution, key lifecycle or independently retained reference tested. Two matching but substituted valid-looking digests are not evidence of genuine enrollment; the experiment assumes verifier-owned correctly enrolled slots and no direct state/API bypass. A partial write may cause a mismatch and fail closed; crash recovery not demonstrated. No trusted time, authority legitimacy, global equivocation prevention, telemetry truth, physical coverage or simultaneous rollback protection established.

## Owner-accepted finding 20 — Draft integration only, not published

RO: Într-un experiment sintetic, un verificator care păstrează o referință locală a primei autorizări autentificate pentru același domeniu și aceeași epocă precedentă poate detecta o autorizare autentificată cu un succesor diferit, independent de admisibilitatea efectivă a tranziției. Restaurarea simultană a stării și a referinței locale la starea inițială permite însă acceptarea autorizării contradictorii; detectarea locală nu stabilește care autorizare este legitimă și nu previne echivocul global.

EN: In a synthetic experiment, a verifier retaining a local reference to the first authenticated authorization for the same scope and previous epoch can detect an authenticated authorization naming a different successor, independently of actual transition admissibility. Restoring both local state and its reference to the initial snapshot nevertheless permits acceptance of the conflicting authorization; local detection neither establishes which authorization is legitimate nor prevents global equivocation.

Owner explicitly accepted finding 20 and authorized focused Draft integration on 2026-11-26. Ready, merge and publication remain separate decisions. Original local evidence SHA-256: f049b3375e333cee0dee0a9c81d29a7556a7ea6a2c2739415fccd8f599473aef. Implementation unchanged; focal test launch corrected as described below.

## Draft integration portability correction — 2026-11-26

PR #198 initial HEAD ff65d5464028bce4d84e99f6a4ee9f3b449b5f49, CI #45831262652: documentation PASS; experimental gate FAIL solely because the child interpreter in test_restart_process could not import epoch_transition_consistency when launched from the repository root without the sandbox's PYTHONPATH. Twelve of thirteen new tests passed; the showcase steps were skipped. Owner authorized the minimal correction. The subprocess now uses cwd=Path(__file__).resolve().parent; the test assertions, implementation and scientific finding remain unchanged. Original local observation and digest retained above. On Qube, Python 3.14.4, bwrap read-only candidate source, isolated namespaces, disposable tmpfs, cleared environment without PYTHONPATH, repository-root working directory, direct invocation `python3 -B experiments/source-proof-binding-v0/test_epoch_transition_consistency.py`: 13/13 PASS in 0.114 s, PID 193525, exit 0. This reproduces the CI invocation context, not the entire runner environment. No new proof or provisioning.
