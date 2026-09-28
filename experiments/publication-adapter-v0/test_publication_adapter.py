#!/usr/bin/env python3
"""Conformance tests for publication-adapter-v0.

EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import socket
import tempfile
import unittest
from unittest import mock

import publication_adapter as publication


RAW_KEY = "idk_00000000000000000000000000000001"
CHANGED_KEY = "idk_00000000000000000000000000000002"
RESTRICTED_VALUES = (
    RAW_KEY,
    CHANGED_KEY,
    "restricted-proof-bytes",
    "restricted-witness",
    "vehicle-identity-123",
    "mission-123",
    "customer-123",
    "credential-123",
)
RESTRICTED_KEYS = {
    "idempotency_key",
    "raw_telemetry",
    "speed_cm_s",
    "private_speed",
    "proof",
    "proof_bytes",
    "witness",
    "opening",
    "salt",
    "nonce",
    "stable_identity",
    "source_identity",
    "pseudonym",
    "mission",
    "customer",
    "credential",
    "secret",
    "private_key",
    "relying_party_decision",
    "scope_digest",
    "request_binding",
}


def request(*, key: str = RAW_KEY, payload_label: str = "synthetic-package-a", profile: str = publication.PROFILE):
    return publication.PublicationRequest(
        idempotency_key=key,
        payload_digest=publication.synthetic_payload_digest(payload_label),
        metadata={"fixture": "synthetic-a", "scenario": "synthetic-conformance"},
        profile=profile,
    )


def assert_no_restricted(test: unittest.TestCase, value: object) -> None:
    def walk(item: object) -> None:
        if isinstance(item, dict):
            for key, nested in item.items():
                test.assertNotIn(str(key).lower(), RESTRICTED_KEYS)
                walk(nested)
        elif isinstance(item, list):
            for nested in item:
                walk(nested)
    walk(value)
    encoded = json.dumps(value, sort_keys=True)
    for restricted in RESTRICTED_VALUES:
        test.assertNotIn(restricted, encoded)


class SharedConformanceMixin:
    def make_adapter(self):
        raise NotImplementedError

    def test_duplicate_retry_converges_and_status_lookup_matches(self):
        adapter = self.make_adapter()
        first = adapter.submit(request())
        second = adapter.submit(request())
        self.assertEqual(first, second)
        self.assertEqual(adapter.status(first["record_id"]), first)
        self.assertEqual(first["payload_digest"], request().payload_digest)
        assert_no_restricted(self, first)

    def test_changed_payload_same_key_is_stable_conflict(self):
        adapter = self.make_adapter()
        adapter.submit(request())
        with self.assertRaises(publication.PublicationAdapterError) as caught:
            adapter.submit(request(payload_label="synthetic-package-b"))
        self.assertEqual(caught.exception.code, "IDEMPOTENCY_CONFLICT")
        self.assertEqual(caught.exception.classification, "rejected")
        self.assertFalse(caught.exception.retryable)
        assert_no_restricted(self, caught.exception.public())

    def test_changed_profile_same_key_is_stable_conflict(self):
        adapter = self.make_adapter()
        adapter.submit(request())
        with self.assertRaises(publication.PublicationAdapterError) as caught:
            adapter.submit(request(profile=publication.ALT_PROFILE))
        self.assertEqual(caught.exception.code, "IDEMPOTENCY_CONFLICT")
        self.assertEqual(caught.exception.classification, "rejected")
        self.assertFalse(caught.exception.retryable)

    def test_unknown_lookup_is_deterministic_and_safe(self):
        adapter = self.make_adapter()
        with self.assertRaises(publication.PublicationAdapterError) as caught:
            adapter.status("rec_" + "0" * 24)
        self.assertEqual(caught.exception.code, "UNKNOWN_RECORD")
        self.assertEqual(caught.exception.classification, "not_found")
        assert_no_restricted(self, caught.exception.public())

    def test_profile_conflict_and_malformed_input_are_distinct(self):
        adapter = self.make_adapter()
        with self.assertRaises(publication.PublicationAdapterError) as unsupported:
            adapter.submit(request(profile="TAG_PUBLICATION_PROFILE_UNKNOWN"))
        self.assertEqual(unsupported.exception.code, "UNSUPPORTED_PUBLICATION_PROFILE")
        self.assertEqual(unsupported.exception.classification, "rejected")

        malformed = publication.PublicationRequest(
            idempotency_key=RAW_KEY,
            payload_digest="not-a-digest",
            metadata={"fixture": "synthetic-a"},
        )
        with self.assertRaises(publication.PublicationAdapterError) as invalid:
            adapter.submit(malformed)
        self.assertEqual(invalid.exception.code, "INVALID_PAYLOAD_DIGEST")
        self.assertEqual(invalid.exception.classification, "malformed")

    def test_unhashable_profile_has_stable_adapter_error(self):
        adapter = self.make_adapter()
        malformed = request()
        object.__setattr__(malformed, "profile", [])
        with self.assertRaises(publication.PublicationAdapterError) as caught:
            adapter.submit(malformed)
        self.assertEqual(caught.exception.code, "UNSUPPORTED_PUBLICATION_PROFILE")
        self.assertEqual(caught.exception.classification, "rejected")
        self.assertFalse(caught.exception.retryable)

    def test_raw_key_format_cannot_overlap_any_public_value(self):
        candidates = (
            "synthetic-a",
            "fixture",
            publication.PROFILE,
            request().payload_digest,
            "EXPERIMENTAL",
            "failed",
            "PUBLICATION_DISABLED",
            "deterministic-local-mock-v0",
            "rec_000000000000000000000000",
        )
        for raw_key in candidates:
            with self.subTest(raw_key=raw_key):
                with self.assertRaises(publication.PublicationAdapterError) as caught:
                    adapter = self.make_adapter()
                    adapter.submit(request(key=raw_key))
                self.assertEqual(caught.exception.code, "INVALID_IDEMPOTENCY_KEY")
                self.assertEqual(caught.exception.classification, "malformed")
                assert_no_restricted(self, caught.exception.public())

    def test_metadata_cannot_embed_raw_idempotency_key(self):
        adapter = self.make_adapter()
        embedded = publication.PublicationRequest(
            idempotency_key=RAW_KEY,
            payload_digest=request().payload_digest,
            metadata={"fixture": f"synthetic-{RAW_KEY}"},
        )
        with self.assertRaises(publication.PublicationAdapterError) as caught:
            adapter.submit(embedded)
        self.assertEqual(caught.exception.code, "INVALID_METADATA")
        self.assertEqual(caught.exception.classification, "malformed")
        self.assertFalse(caught.exception.retryable)
        assert_no_restricted(self, caught.exception.public())

    def test_network_is_not_needed(self):
        adapter = self.make_adapter()
        original_connect = socket.socket.connect
        original_create_connection = socket.create_connection

        def denied(*args, **kwargs):
            raise AssertionError("network access attempted")

        socket.socket.connect = denied
        socket.create_connection = denied
        try:
            result = adapter.submit(request())
            lookup = adapter.status(result["record_id"])
        finally:
            socket.socket.connect = original_connect
            socket.create_connection = original_create_connection
        self.assertEqual(lookup, result)


class DisabledAdapterConformance(SharedConformanceMixin, unittest.TestCase):
    def make_adapter(self):
        return publication.DisabledAdapter()

    def test_disabled_adapter_has_definitive_non_retryable_failure(self):
        result = self.make_adapter().submit(request())
        self.assertEqual(result["state"], "failed")
        self.assertEqual(result["lifecycle"], ["pending", "failed"])
        self.assertEqual(result["error"]["code"], "PUBLICATION_DISABLED")
        self.assertEqual(result["error"]["classification"], "definitive")
        self.assertFalse(result["error"]["retryable"])


class LocalAdapterConformance(SharedConformanceMixin, unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.state_path = Path(self.temporary.name) / "publication-state.json"

    def tearDown(self):
        self.temporary.cleanup()

    def make_adapter(self, **kwargs):
        return publication.DeterministicLocalAdapter(self.state_path, **kwargs)

    def test_success_exercises_pending_recorded_final_and_payload_binding(self):
        result = self.make_adapter().submit(request())
        self.assertEqual(result["state"], "final")
        self.assertEqual(result["lifecycle"], ["pending", "recorded", "final"])
        self.assertEqual(result["payload_digest"], request().payload_digest)
        self.assertEqual(result["recorded_time"], publication.TEST_RECORDED_TIME)
        self.assertEqual(result["time_authority"], publication.TEST_CLOCK_AUTHORITY)
        self.assertEqual(result["receipt_state"], "MOCK_FINAL")

    def test_timeout_reconciles_after_restart_without_duplicate_record(self):
        first_adapter = self.make_adapter(fault_once="timeout")
        timed_out = first_adapter.submit(request())
        self.assertEqual(timed_out["state"], "pending")
        self.assertEqual(timed_out["error"]["code"], "SUBMISSION_TIMEOUT")
        self.assertEqual(timed_out["error"]["classification"], "retryable")
        self.assertTrue(timed_out["error"]["retryable"])
        self.assertEqual(first_adapter.status(timed_out["record_id"]), timed_out)

        restarted = self.make_adapter()
        reconciled = restarted.submit(request())
        self.assertEqual(reconciled["record_id"], timed_out["record_id"])
        self.assertEqual(reconciled["state"], "final")
        self.assertEqual(reconciled["lifecycle"], ["pending", "recorded", "final"])
        self.assertIsNone(reconciled["error"])
        state = json.loads(self.state_path.read_text(encoding="utf-8"))
        self.assertEqual(len(state["records"]), 1)
        assert_no_restricted(self, state)

    def test_cancellation_is_bounded_retryable_and_reconcilable(self):
        cancelled = self.make_adapter(fault_once="cancelled").submit(request())
        self.assertEqual(cancelled["state"], "pending")
        self.assertEqual(cancelled["error"]["code"], "SUBMISSION_CANCELLED")
        self.assertTrue(cancelled["error"]["retryable"])
        final = self.make_adapter().submit(request())
        self.assertEqual(final["state"], "final")

    def test_retryable_unavailable_is_distinct_from_definitive_failure(self):
        unavailable_adapter = self.make_adapter(fault_once="unavailable")
        with self.assertRaises(publication.PublicationAdapterError) as unavailable:
            unavailable_adapter.submit(request())
        self.assertEqual(unavailable.exception.code, "SUBSTRATE_UNAVAILABLE")
        self.assertEqual(unavailable.exception.classification, "retryable")
        self.assertTrue(unavailable.exception.retryable)
        self.assertFalse(self.state_path.exists())

        failed = self.make_adapter(fault_once="definitive_failure").submit(request())
        self.assertEqual(failed["state"], "failed")
        self.assertEqual(failed["lifecycle"], ["pending", "failed"])
        self.assertEqual(failed["error"]["code"], "SUBSTRATE_REJECTED")
        self.assertEqual(failed["error"]["classification"], "definitive")
        self.assertFalse(failed["error"]["retryable"])

    def test_superseded_state_and_invalid_transitions_are_exercised(self):
        final = self.make_adapter().submit(request())
        superseded = self.make_adapter().supersede_for_test(final["record_id"])
        self.assertEqual(superseded["state"], "superseded")
        self.assertEqual(superseded["lifecycle"], ["pending", "recorded", "final", "superseded"])
        with self.assertRaises(publication.PublicationAdapterError) as reversed_transition:
            self.make_adapter().transition_for_test(final["record_id"], "recorded")
        self.assertEqual(reversed_transition.exception.code, "INVALID_LIFECYCLE_TRANSITION")

        separate_path = Path(self.temporary.name) / "pending-state.json"
        pending = publication.DeterministicLocalAdapter(separate_path, fault_once="timeout").submit(
            request(key=CHANGED_KEY)
        )
        with self.assertRaises(publication.PublicationAdapterError) as skipped:
            publication.DeterministicLocalAdapter(separate_path).transition_for_test(
                pending["record_id"], "final"
            )
        self.assertEqual(skipped.exception.code, "INVALID_LIFECYCLE_TRANSITION")

    def test_public_and_persisted_shapes_exclude_business_and_verifier_dimensions(self):
        result = self.make_adapter().submit(request())
        state = json.loads(self.state_path.read_text(encoding="utf-8"))
        for value in (result, state):
            encoded = json.dumps(value, sort_keys=True)
            for forbidden in (
                "cryptographic",
                "policy",
                "freshness",
                "revocation",
                "replay",
                "relying_party_decision",
                "proof_validity",
            ):
                self.assertNotIn(forbidden, encoded)
            assert_no_restricted(self, value)

    def test_state_reload_preserves_idempotency_conflict_detection(self):
        self.make_adapter().submit(request())
        restarted = self.make_adapter()
        with self.assertRaises(publication.PublicationAdapterError) as caught:
            restarted.submit(request(payload_label="synthetic-package-b"))
        self.assertEqual(caught.exception.code, "IDEMPOTENCY_CONFLICT")

    def test_concurrent_instances_preserve_every_submission(self):
        requests = [request(key=f"idk_{index + 16:032x}") for index in range(16)]

        def submit(item):
            return self.make_adapter().submit(item)

        with ThreadPoolExecutor(max_workers=8) as executor:
            results = list(executor.map(submit, requests))

        state = json.loads(self.state_path.read_text(encoding="utf-8"))
        self.assertEqual(len(state["records"]), len(requests))
        self.assertEqual(
            set(state["records"]),
            {result["record_id"] for result in results},
        )
        self.assertTrue(all(result["state"] == "final" for result in results))
        assert_no_restricted(self, state)

    def test_malformed_or_incomplete_local_state_has_stable_error(self):
        malformed_states = (
            "{truncated",
            json.dumps({"labels": list(publication.LABELS), "contract_version": publication.CONTRACT_VERSION}),
            json.dumps(
                {
                    "labels": list(publication.LABELS),
                    "contract_version": publication.CONTRACT_VERSION,
                    "state_profile": "DISPOSABLE_LOCAL_TEST_STATE_V0",
                    "records": [],
                }
            ),
            json.dumps(
                {
                    "labels": list(publication.LABELS),
                    "contract_version": publication.CONTRACT_VERSION,
                    "state_profile": "DISPOSABLE_LOCAL_TEST_STATE_V0",
                    "records": {"rec_" + "0" * 24: {}},
                }
            ),
        )
        for serialized in malformed_states:
            with self.subTest(serialized=serialized):
                self.state_path.write_text(serialized, encoding="utf-8")
                with self.assertRaises(publication.PublicationAdapterError) as caught:
                    self.make_adapter()
                self.assertEqual(caught.exception.code, "INVALID_LOCAL_STATE")
                self.assertEqual(caught.exception.classification, "definitive")
                self.assertFalse(caught.exception.retryable)

    def test_pre_recording_state_rejects_any_timestamp_data(self):
        pending = self.make_adapter(fault_once="timeout").submit(request())
        state = json.loads(self.state_path.read_text(encoding="utf-8"))
        record = state["records"][pending["record_id"]]

        for recorded_time, time_authority in (
            ("secret-or-malformed", 123),
            (publication.TEST_RECORDED_TIME, None),
            (None, publication.TEST_CLOCK_AUTHORITY),
        ):
            with self.subTest(
                recorded_time=recorded_time,
                time_authority=time_authority,
            ):
                record["recorded_time"] = recorded_time
                record["time_authority"] = time_authority
                self.state_path.write_text(json.dumps(state), encoding="utf-8")
                with self.assertRaises(publication.PublicationAdapterError) as caught:
                    self.make_adapter()
                self.assertEqual(caught.exception.code, "INVALID_LOCAL_STATE")
                self.assertEqual(caught.exception.classification, "definitive")
                self.assertFalse(caught.exception.retryable)

    def test_lifecycle_inconsistent_errors_are_invalid_local_state(self):
        final = self.make_adapter().submit(request())
        valid_state = json.loads(self.state_path.read_text(encoding="utf-8"))
        corruptions = (
            (
                "final",
                {
                    "code": "SUBMISSION_TIMEOUT",
                    "classification": "retryable",
                    "retryable": True,
                },
            ),
            ("failed", None),
        )
        for state_name, error in corruptions:
            with self.subTest(state=state_name, error=error):
                state = json.loads(json.dumps(valid_state))
                candidate = state["records"][final["record_id"]]
                candidate["state"] = state_name
                candidate["error"] = error
                if state_name == "failed":
                    candidate["lifecycle"] = ["pending", "recorded", "failed"]
                    candidate["receipt_state"] = "NOT_ISSUED"
                self.state_path.write_text(json.dumps(state), encoding="utf-8")
                with self.assertRaises(publication.PublicationAdapterError) as caught:
                    self.make_adapter()
                self.assertEqual(caught.exception.code, "INVALID_LOCAL_STATE")

    def test_filesystem_failures_have_stable_adapter_error(self):
        adapter = self.make_adapter()
        with mock.patch.object(Path, "read_text", side_effect=OSError("unreadable")):
            self.state_path.touch()
            with self.assertRaises(publication.PublicationAdapterError) as read_failure:
                adapter.status("rec_" + "0" * 24)
        self.assertEqual(read_failure.exception.code, "LOCAL_STATE_IO_FAILURE")
        self.assertEqual(read_failure.exception.classification, "retryable")
        self.assertTrue(read_failure.exception.retryable)

        self.state_path.unlink()
        adapter = self.make_adapter()
        with mock.patch.object(publication.os, "replace", side_effect=OSError("read-only")):
            with self.assertRaises(publication.PublicationAdapterError) as write_failure:
                adapter.submit(request())
        self.assertEqual(write_failure.exception.code, "LOCAL_STATE_IO_FAILURE")
        self.assertEqual(write_failure.exception.classification, "retryable")
        self.assertTrue(write_failure.exception.retryable)


if __name__ == "__main__":
    unittest.main()
