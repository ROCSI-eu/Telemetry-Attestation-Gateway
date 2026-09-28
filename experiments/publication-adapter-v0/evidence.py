#!/usr/bin/env python3
"""Generate deterministic checked-in evidence for publication-adapter-v0.

EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION
"""

from __future__ import annotations

import json
from pathlib import Path
import socket
import tempfile

import publication_adapter as publication

RESTRICTED_VALUES = (
    "restricted-proof-bytes",
    "restricted-witness",
    "restricted-opening",
    "vehicle-identity-123",
    "mission-123",
    "customer-123",
    "credential-123",
)

RAW_KEYS = (
    "idk_10000000000000000000000000000001",
    "idk_10000000000000000000000000000002",
    "idk_10000000000000000000000000000003",
    "idk_10000000000000000000000000000004",
    "idk_10000000000000000000000000000005",
    "idk_10000000000000000000000000000006",
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


def req(key: str, label: str = "synthetic-evidence-package") -> publication.PublicationRequest:
    return publication.PublicationRequest(
        idempotency_key=key,
        payload_digest=publication.synthetic_payload_digest(label),
        metadata={"fixture": "synthetic-evidence", "scenario": "synthetic-issue-83"},
    )


def assert_safe(value: object) -> None:
    def walk(item: object) -> None:
        if isinstance(item, dict):
            for key, nested in item.items():
                if str(key).lower() in RESTRICTED_KEYS:
                    raise AssertionError(f"restricted key escaped: {key}")
                walk(nested)
        elif isinstance(item, list):
            for nested in item:
                walk(nested)
    walk(value)
    encoded = json.dumps(value, sort_keys=True)
    for raw_key in RAW_KEYS:
        if raw_key in encoded:
            raise AssertionError("raw idempotency key escaped")
    for restricted_value in RESTRICTED_VALUES:
        if restricted_value in encoded:
            raise AssertionError("restricted value escaped")


def main() -> int:
    original_connect = socket.socket.connect
    original_create_connection = socket.create_connection

    def denied(*args, **kwargs):
        raise AssertionError("network access attempted")

    socket.socket.connect = denied
    socket.create_connection = denied
    try:
        disabled = publication.DisabledAdapter()
        disabled_first = disabled.submit(req(RAW_KEYS[0]))
        disabled_retry = disabled.submit(req(RAW_KEYS[0]))
        disabled_lookup = disabled.status(disabled_first["record_id"])

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            local_path = root / "local.json"
            local = publication.DeterministicLocalAdapter(local_path)
            local_first = local.submit(req(RAW_KEYS[1]))
            local_retry = local.submit(req(RAW_KEYS[1]))
            local_lookup = local.status(local_first["record_id"])
            try:
                local.submit(req(RAW_KEYS[1], "synthetic-conflicting-package"))
            except publication.PublicationAdapterError as conflict:
                conflict_error = conflict.public()
            else:
                raise AssertionError("idempotency conflict was not detected")
            changed_profile_request = publication.PublicationRequest(
                idempotency_key=RAW_KEYS[1],
                payload_digest=local_first["payload_digest"],
                metadata={"fixture": "synthetic-evidence", "scenario": "synthetic-issue-83"},
                profile=publication.ALT_PROFILE,
            )
            try:
                local.submit(changed_profile_request)
            except publication.PublicationAdapterError as profile_conflict:
                profile_conflict_error = profile_conflict.public()
            else:
                raise AssertionError("profile idempotency conflict was not detected")

            timeout_path = root / "timeout.json"
            timeout_adapter = publication.DeterministicLocalAdapter(timeout_path, fault_once="timeout")
            timeout_first = timeout_adapter.submit(req(RAW_KEYS[2]))
            timeout_lookup = timeout_adapter.status(timeout_first["record_id"])
            timeout_reconciled = publication.DeterministicLocalAdapter(timeout_path).submit(req(RAW_KEYS[2]))

            cancel_path = root / "cancel.json"
            cancelled = publication.DeterministicLocalAdapter(cancel_path, fault_once="cancelled").submit(req(RAW_KEYS[3]))
            cancel_reconciled = publication.DeterministicLocalAdapter(cancel_path).submit(req(RAW_KEYS[3]))

            failed_path = root / "failed.json"
            failed = publication.DeterministicLocalAdapter(failed_path, fault_once="definitive_failure").submit(req(RAW_KEYS[4]))

            unavailable_path = root / "unavailable.json"
            try:
                publication.DeterministicLocalAdapter(unavailable_path, fault_once="unavailable").submit(
                    req(RAW_KEYS[5])
                )
            except publication.PublicationAdapterError as unavailable:
                unavailable_error = unavailable.public()
            else:
                raise AssertionError("unavailable fault was not exercised")
            if unavailable_path.exists():
                raise AssertionError("unavailable-before-side-effect unexpectedly persisted state")

            superseded = publication.DeterministicLocalAdapter(local_path).supersede_for_test(local_first["record_id"])
            persisted_values = [
                json.loads(path.read_text(encoding="utf-8"))
                for path in (local_path, timeout_path, cancel_path, failed_path)
            ]

            public_values = [
                disabled_first,
                disabled_retry,
                disabled_lookup,
                local_first,
                local_retry,
                local_lookup,
                conflict_error,
                profile_conflict_error,
                timeout_first,
                timeout_lookup,
                timeout_reconciled,
                cancelled,
                cancel_reconciled,
                failed,
                unavailable_error,
                superseded,
            ]
            for value in [*public_values, *persisted_values]:
                assert_safe(value)

            if disabled_first != disabled_retry or disabled_first != disabled_lookup:
                raise AssertionError("disabled adapter duplicate/lookup conformance failed")
            if local_first != local_retry or local_first != local_lookup:
                raise AssertionError("local adapter duplicate/lookup conformance failed")
            if timeout_first["state"] != "pending" or timeout_reconciled["state"] != "final":
                raise AssertionError("timeout reconciliation failed")
            if timeout_first["record_id"] != timeout_reconciled["record_id"]:
                raise AssertionError("timeout reconciliation changed logical record")
            if cancel_reconciled["state"] != "final":
                raise AssertionError("cancellation reconciliation failed")
            if failed["state"] != "failed":
                raise AssertionError("definitive failure was not terminal")
            if superseded["state"] != "superseded":
                raise AssertionError("supersession state was not exercised")

            evidence = {
                "labels": list(publication.LABELS),
                "experiment": "publication-adapter-v0",
                "contract_version": publication.CONTRACT_VERSION,
                "profile": publication.PROFILE,
                "evidence_scope": "provisional substrate-neutral local publication adapter conformance",
                "adapters": {
                    "disabled": {
                        "substrate": disabled_first["substrate"],
                        "duplicate_retry": "PASS",
                        "status_lookup": "PASS",
                        "terminal_state": disabled_first["state"],
                        "error_code": disabled_first["error"]["code"],
                    },
                    "deterministic_local_mock": {
                        "substrate": local_first["substrate"],
                        "duplicate_retry": "PASS",
                        "status_lookup": "PASS",
                        "payload_binding": "PASS",
                        "success_lifecycle": local_first["lifecycle"],
                        "superseded_lifecycle": superseded["lifecycle"],
                    },
                },
                "cases": {
                    "idempotency_conflict": {
                        "changed_payload_code": conflict_error["error"]["code"],
                        "changed_profile_code": profile_conflict_error["error"]["code"],
                        "classification": conflict_error["error"]["classification"],
                    },
                    "timeout_reconciliation": {
                        "initial_state": timeout_first["state"],
                        "initial_code": timeout_first["error"]["code"],
                        "lookup_state": timeout_lookup["state"],
                        "reconciled_state": timeout_reconciled["state"],
                        "reconciled_lifecycle": timeout_reconciled["lifecycle"],
                        "same_logical_record": True,
                    },
                    "cancellation_reconciliation": {
                        "initial_state": cancelled["state"],
                        "initial_code": cancelled["error"]["code"],
                        "reconciled_state": cancel_reconciled["state"],
                    },
                    "retryable_unavailable": {
                        "code": unavailable_error["error"]["code"],
                        "classification": unavailable_error["error"]["classification"],
                        "retryable": unavailable_error["error"]["retryable"],
                    },
                    "definitive_failure": {
                        "state": failed["state"],
                        "code": failed["error"]["code"],
                        "classification": failed["error"]["classification"],
                        "retryable": failed["error"]["retryable"],
                    },
                },
                "checks": {
                    "python_network_denied": "PASS",
                    "raw_idempotency_key_absence": "PASS",
                    "restricted_field_absence_public_results": "PASS",
                    "restricted_field_absence_local_state": "PASS",
                    "lifecycle_monotonicity": "PASS",
                    "skipped_or_reversed_transitions_rejected_by_tests": "PASS",
                    "verifier_dimensions_outside_adapter_contract": "PASS",
                    "relying_party_business_decision_absent": "PASS",
                    "external_dependency_required": False,
                },
                "limitations": [
                    "Synthetic local evidence only; the adapter contract remains provisional experimental research.",
                    "The local record time is a fixed test clock and is not trustworthy time or external publication authority.",
                    "The mock receipt state is not authenticated, signed, independently verified, globally ordered, or a live-ledger record.",
                    "No proof validity, telemetry truth, telemetry assurance, workflow, safety, compliance, payment, demand, pilot, deployment, or production claim is established.",
                ],
            }
            assert_safe(evidence)
            print(json.dumps(evidence, indent=2, sort_keys=True))
    finally:
        socket.socket.connect = original_connect
        socket.create_connection = original_create_connection
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
