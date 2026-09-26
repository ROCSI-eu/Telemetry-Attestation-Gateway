#!/usr/bin/env python3
"""Generate minimized deterministic evidence for publication-mock-v0."""

from __future__ import annotations

import json
import os
from pathlib import Path
import socket
import tempfile

import publication_mock as publication
from test_publication_mock import valid_verifier_result


FORBIDDEN_TOKENS = (
    '"speed_cm_s":',
    '"private_speed":',
    '"raw_frame":',
    '"raw_telemetry":',
    '"proof":',
    '"witness":',
    '"stable_identity":',
    '"source_identity":',
    '"coordinates":',
    '"mission":',
    '"customer":',
    '"credential":',
    '"private_key":',
    '"idempotency_key":',
    '"request_fingerprint":',
    '"subject_digest":',
)


def _assert_no_restricted_output(value: object) -> None:
    encoded = json.dumps(value, sort_keys=True)
    for token in FORBIDDEN_TOKENS:
        if token in encoded:
            raise AssertionError(f"restricted token escaped publication evidence: {token}")


def main() -> int:
    original_connect = socket.socket.connect
    original_create_connection = socket.create_connection

    def denied(*args, **kwargs):
        raise AssertionError("external network access attempted")

    socket.socket.connect = denied
    socket.create_connection = denied
    try:
        subject_digest = publication.synthetic_subject_digest(
            "synthetic-publication-subject-v0"
        )
        verifier = valid_verifier_result()

        with tempfile.TemporaryDirectory() as temporary:
            original_cwd = Path.cwd()
            try:
                os.chdir(temporary)
                workspace_empty_before = list(Path(".").iterdir()) == []

                finalized = publication.publish(
                    subject_digest=subject_digest, verifier_result=verifier
                )
                duplicate = publication.publish(
                    subject_digest=subject_digest, verifier_result=verifier
                )
                not_performed = publication.publish(
                    subject_digest=subject_digest,
                    verifier_result=verifier,
                    behavior="not_performed",
                )
                outage = publication.publish(
                    subject_digest=subject_digest,
                    verifier_result=verifier,
                    behavior="outage",
                )
                workspace_empty_after = list(Path(".").iterdir()) == []
            finally:
                os.chdir(original_cwd)

        public_evidence = {
            "experiment": "publication-mock-v0",
            "labels": list(publication.LABELS),
            "marker": publication.MOCK_MARKER,
            "cases": {
                "finalized": {
                    "state": finalized["publication_adapter"]["state"],
                    "lifecycle": finalized["publication_adapter"]["lifecycle"],
                    "authentication": finalized["publication_adapter"]["authentication"],
                    "subject_binding": finalized["publication_adapter"]["subject_binding"],
                    "receipt_authentication": finalized["publication_adapter"]["receipt"]["authentication"],
                    "receipt_signature": finalized["publication_adapter"]["receipt"]["signature"],
                    "receipt_subject_binding": finalized["publication_adapter"]["receipt"]["subject_binding"],
                    "receipt_verification_authority": finalized["publication_adapter"]["receipt"]["verification_authority"],
                    "mock_record_digest": finalized["publication_adapter"]["receipt"]["mock_record_digest"],
                },
                "duplicate": {
                    "state": duplicate["publication_adapter"]["state"],
                    "same_result": duplicate == finalized,
                },
                "not_performed": {
                    "state": not_performed["publication_adapter"]["state"],
                    "cryptographic": not_performed["verifier_result"]["cryptographic"]["status"],
                    "receipt_present": not_performed["publication_adapter"]["receipt"] is not None,
                },
                "publisher_outage": {
                    "state": outage["publication_adapter"]["state"],
                    "reason": outage["publication_adapter"]["reason"],
                    "cryptographic": outage["verifier_result"]["cryptographic"]["status"],
                    "receipt_present": outage["publication_adapter"]["receipt"] is not None,
                },
            },
            "checks": {
                "verifier_result_unchanged_after_finalize": "PASS"
                if finalized["verifier_result"] == verifier
                else "FAIL",
                "verifier_result_unchanged_on_outage": "PASS"
                if outage["verifier_result"] == verifier
                else "FAIL",
                "publication_failure_does_not_change_cryptographic_validity": "PASS"
                if outage["verifier_result"]["cryptographic"]["status"] == "VALID"
                else "FAIL",
                "publication_omission_does_not_change_cryptographic_validity": "PASS"
                if not_performed["verifier_result"]["cryptographic"]["status"] == "VALID"
                else "FAIL",
                "non_cryptographic_mock_marking": "PASS"
                if finalized["publication_adapter"]["receipt"]["authentication"]
                == "NOT_PERFORMED"
                and finalized["publication_adapter"]["receipt"]["signature"]
                == "NOT_PERFORMED"
                and finalized["publication_adapter"]["receipt"]["subject_binding"]
                == "NOT_PERFORMED"
                else "FAIL",
                "deterministic_duplicate_convergence": "PASS"
                if duplicate == finalized
                else "FAIL",
                "subject_correlation_not_emitted": "PASS"
                if subject_digest not in json.dumps(finalized, sort_keys=True)
                else "FAIL",
                "python_network_denied": "PASS",
                "restricted_field_absence": "PASS",
                "no_persistent_state_created": "PASS"
                if workspace_empty_before and workspace_empty_after
                else "FAIL",
            },
            "limitations": [
                "Synthetic local evidence only.",
                "The receipt is a deterministic non-cryptographic control-flow mock; authentication, signatures, and claim binding are not performed.",
                "The synthetic subject digest is accepted only as ephemeral invocation input and is not emitted, persisted, or reflected in the mock receipt.",
                "No persistent publication state is created by this experiment.",
                "No live publication service, ledger, vendor dependency, production trust root, or production credential is used.",
                "Publication success, omission, or outage does not alter the pre-publication verifier result.",
                "No workflow, demand, assurance, safety, compliance, pilot, deployment, or production claim is established.",
            ],
        }
        _assert_no_restricted_output(public_evidence)
        if any(value != "PASS" for value in public_evidence["checks"].values()):
            raise AssertionError("one or more publication evidence checks failed")
        print(json.dumps(public_evidence, indent=2, sort_keys=True))
    finally:
        socket.socket.connect = original_connect
        socket.create_connection = original_create_connection
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
