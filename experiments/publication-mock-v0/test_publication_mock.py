#!/usr/bin/env python3
"""Boundary tests for the deterministic local publication mock."""

from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import socket
import tempfile
import unittest

import publication_mock as publication


def valid_verifier_result() -> dict:
    return {
        "labels": list(publication.LABELS),
        "invocation": {"status": "ACCEPTED", "reason": None},
        "telemetry": {
            "status": "NORMALIZED",
            "reason": None,
            "assurance_id": "A0_SYNTHETIC",
            "source_trust": "UNSIGNED",
        },
        "predicate": "SATISFIED",
        "proof_generation": "GENERATED",
        "verification_input": {"status": "ACCEPTED", "reason": None},
        "cryptographic": {"status": "VALID", "reason": None},
        "policy": "NOT_EVALUATED",
        "freshness": "NOT_EVALUATED",
        "revocation": "NOT_EVALUATED",
        "replay": "NOT_EVALUATED",
        "assurance": {
            "declared": "A0_SYNTHETIC",
            "effective": "A0_SYNTHETIC",
            "required": "NOT_EVALUATED",
            "demonstrator": "A0_SYNTHETIC",
        },
        "publication": "NOT_PERFORMED",
        "relying_party_decision": "NOT_MADE",
        "proof_validity_is_telemetry_truth": False,
        "private_witness_disclosed": False,
        "command_path": "NONE",
    }


class PublicationMockTests(unittest.TestCase):
    def subject(self) -> str:
        return publication.synthetic_subject_digest("synthetic-publication-subject-v0")

    def test_finalize_is_deterministic_minimized_and_non_cryptographic(self):
        verifier = valid_verifier_result()
        result = publication.publish(subject_digest=self.subject(), verifier_result=verifier)
        receipt = result["publication_adapter"]["receipt"]

        self.assertEqual(result["verifier_result"], verifier)
        self.assertEqual(result["publication_adapter"]["state"], "FINALIZED")
        self.assertEqual(
            result["publication_adapter"]["lifecycle"], ["SUBMITTED", "FINALIZED"]
        )
        self.assertEqual(receipt["marker"], publication.MOCK_MARKER)
        self.assertEqual(receipt["authentication"], "NOT_PERFORMED")
        self.assertEqual(receipt["signature"], "NOT_PERFORMED")
        self.assertEqual(receipt["subject_binding"], "NOT_PERFORMED")
        self.assertEqual(receipt["verification_authority"], "NONE")
        self.assertNotIn("subject_digest", json.dumps(receipt, sort_keys=True))
        self.assertEqual(receipt, publication._mock_receipt())

    def test_repeated_finalization_converges_without_state(self):
        first = publication.publish(
            subject_digest=self.subject(), verifier_result=valid_verifier_result()
        )
        second = publication.publish(
            subject_digest=self.subject(), verifier_result=valid_verifier_result()
        )
        self.assertEqual(first, second)
        self.assertEqual(
            first["publication_adapter"]["receipt"],
            second["publication_adapter"]["receipt"],
        )

    def test_subject_digest_is_not_reflected_in_output(self):
        first_subject = publication.synthetic_subject_digest("synthetic-subject-one")
        second_subject = publication.synthetic_subject_digest("synthetic-subject-two")
        first = publication.publish(
            subject_digest=first_subject, verifier_result=valid_verifier_result()
        )
        second = publication.publish(
            subject_digest=second_subject, verifier_result=valid_verifier_result()
        )
        first_json = json.dumps(first, sort_keys=True)
        second_json = json.dumps(second, sort_keys=True)
        self.assertNotIn(first_subject, first_json)
        self.assertNotIn(second_subject, second_json)
        self.assertEqual(first, second)

    def test_outage_does_not_rewrite_verifier_result(self):
        verifier = valid_verifier_result()
        result = publication.publish(
            subject_digest=self.subject(), verifier_result=verifier, behavior="outage"
        )
        self.assertEqual(result["verifier_result"], verifier)
        self.assertEqual(result["verifier_result"]["cryptographic"]["status"], "VALID")
        self.assertEqual(result["publication_adapter"]["state"], "SUBMISSION_FAILED")
        self.assertEqual(
            result["publication_adapter"]["reason"], "MOCK_PUBLISHER_UNAVAILABLE"
        )
        self.assertIsNone(result["publication_adapter"]["receipt"])

    def test_not_performed_leaves_verifier_result_usable(self):
        verifier = valid_verifier_result()
        result = publication.publish(
            subject_digest=self.subject(),
            verifier_result=verifier,
            behavior="not_performed",
        )
        self.assertEqual(result["verifier_result"], verifier)
        self.assertEqual(result["publication_adapter"]["state"], "NOT_PERFORMED")
        self.assertIsNone(result["publication_adapter"]["receipt"])

    def test_rejects_non_minimized_restricted_result(self):
        verifier = valid_verifier_result()
        verifier["telemetry"]["speed_cm_s"] = 424242
        with self.assertRaisesRegex(
            publication.PublicationMockError, "RESTRICTED_VERIFIER_RESULT"
        ):
            publication.publish(subject_digest=self.subject(), verifier_result=verifier)

    def test_rejects_business_decision_and_command_path(self):
        verifier = valid_verifier_result()
        verifier["relying_party_decision"] = "ACCEPT"
        with self.assertRaisesRegex(
            publication.PublicationMockError, "BUSINESS_DECISION_NOT_ALLOWED"
        ):
            publication.publish(subject_digest=self.subject(), verifier_result=verifier)

        verifier = valid_verifier_result()
        verifier["command_path"] = "MAVLINK_COMMAND"
        with self.assertRaisesRegex(
            publication.PublicationMockError, "COMMAND_PATH_NOT_ALLOWED"
        ):
            publication.publish(subject_digest=self.subject(), verifier_result=verifier)

    def test_python_network_is_not_needed(self):
        original_connect = socket.socket.connect
        original_create_connection = socket.create_connection

        def denied(*args, **kwargs):
            raise AssertionError("network access attempted")

        socket.socket.connect = denied
        socket.create_connection = denied
        try:
            result = publication.publish(
                subject_digest=self.subject(), verifier_result=valid_verifier_result()
            )
        finally:
            socket.socket.connect = original_connect
            socket.create_connection = original_create_connection

        self.assertEqual(result["publication_adapter"]["state"], "FINALIZED")

    def test_publish_creates_no_files_in_clean_workspace(self):
        with tempfile.TemporaryDirectory() as temporary:
            original_cwd = Path.cwd()
            try:
                os.chdir(temporary)
                self.assertEqual(list(Path(".").iterdir()), [])
                publication.publish(
                    subject_digest=self.subject(),
                    verifier_result=valid_verifier_result(),
                )
                self.assertEqual(list(Path(".").iterdir()), [])
            finally:
                os.chdir(original_cwd)

    def test_input_object_is_not_mutated(self):
        verifier = valid_verifier_result()
        before = copy.deepcopy(verifier)
        publication.publish(subject_digest=self.subject(), verifier_result=verifier)
        self.assertEqual(verifier, before)


if __name__ == "__main__":
    unittest.main()
