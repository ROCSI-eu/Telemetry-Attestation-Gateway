#!/usr/bin/env python3
"""Deterministic local publication mock for synthetic verifier results.

EXPERIMENTAL
SYNTHETIC_ONLY
A0_SYNTHETIC
NOT VALIDATION OR PRODUCTION AUTHORIZATION
NON_CRYPTOGRAPHIC_PUBLICATION_MOCK
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from typing import Any

LABELS = (
    "EXPERIMENTAL",
    "SYNTHETIC_ONLY",
    "A0_SYNTHETIC",
    "NOT VALIDATION OR PRODUCTION AUTHORIZATION",
)
MOCK_MARKER = "NON_CRYPTOGRAPHIC_PUBLICATION_MOCK"
PROFILE = "TAG_PUBLICATION_MOCK_V0"
SUBJECT_DOMAIN = b"TAG_PUBLICATION_MOCK_SUBJECT_V0\x00"
RECORD_DOMAIN = b"TAG_PUBLICATION_MOCK_RECORD_V0\x00"
HEX_256 = re.compile(r"^[0-9a-f]{64}$")

_ALLOWED_TOP_LEVEL = {
    "labels",
    "invocation",
    "telemetry",
    "predicate",
    "proof_generation",
    "verification_input",
    "cryptographic",
    "policy",
    "freshness",
    "revocation",
    "replay",
    "assurance",
    "publication",
    "relying_party_decision",
    "proof_validity_is_telemetry_truth",
    "private_witness_disclosed",
    "command_path",
}
_ALLOWED_OBJECT_FIELDS = {
    "invocation": {"status", "reason"},
    "telemetry": {"status", "reason", "assurance_id", "source_trust"},
    "verification_input": {"status", "reason"},
    "cryptographic": {"status", "reason"},
    "assurance": {"declared", "effective", "required", "demonstrator"},
}
_RESTRICTED_KEYS = {
    "raw_frame",
    "raw_telemetry",
    "speed_cm_s",
    "private_speed",
    "witness",
    "opening",
    "salt",
    "nonce",
    "proof",
    "proof_bytes",
    "stable_identity",
    "source_identity",
    "pseudonym",
    "coordinates",
    "position",
    "mission",
    "customer",
    "credential",
    "secret",
    "private_key",
    "idempotency_key",
    "request_fingerprint",
    "subject_digest",
}


class PublicationMockError(ValueError):
    """Stable error for the local publication experiment."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def synthetic_subject_digest(label: str) -> str:
    """Create a deterministic test-only input digest from a synthetic label."""
    if not isinstance(label, str) or not label or len(label) > 128:
        raise PublicationMockError("INVALID_SYNTHETIC_SUBJECT_LABEL")
    return hashlib.sha256(SUBJECT_DOMAIN + label.encode("utf-8")).hexdigest()


def _primitive(value: Any) -> bool:
    return isinstance(value, (str, int, bool, type(None))) and not isinstance(value, float)


def _reject_restricted_keys(value: Any) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if not isinstance(key, str):
                raise PublicationMockError("NON_MINIMIZED_VERIFIER_RESULT")
            if key.lower() in _RESTRICTED_KEYS:
                raise PublicationMockError("RESTRICTED_VERIFIER_RESULT")
            _reject_restricted_keys(nested)
    elif isinstance(value, list):
        for nested in value:
            _reject_restricted_keys(nested)


def validate_minimized_verifier_result(value: Any) -> dict[str, Any]:
    """Accept only the allowlisted minimized shape emitted by mock-gateway-v0."""
    if not isinstance(value, dict):
        raise PublicationMockError("NON_MINIMIZED_VERIFIER_RESULT")
    _reject_restricted_keys(value)
    if set(value) != _ALLOWED_TOP_LEVEL:
        raise PublicationMockError("NON_MINIMIZED_VERIFIER_RESULT")
    if value.get("labels") != list(LABELS):
        raise PublicationMockError("INVALID_EXPERIMENT_LABELS")

    for field, allowed in _ALLOWED_OBJECT_FIELDS.items():
        nested = value.get(field)
        if not isinstance(nested, dict) or not set(nested).issubset(allowed):
            raise PublicationMockError("NON_MINIMIZED_VERIFIER_RESULT")
        if any(not _primitive(item) for item in nested.values()):
            raise PublicationMockError("NON_MINIMIZED_VERIFIER_RESULT")

    for field in (
        "predicate",
        "proof_generation",
        "policy",
        "freshness",
        "revocation",
        "replay",
        "publication",
        "relying_party_decision",
        "proof_validity_is_telemetry_truth",
        "private_witness_disclosed",
        "command_path",
    ):
        if not _primitive(value.get(field)):
            raise PublicationMockError("NON_MINIMIZED_VERIFIER_RESULT")

    if value["publication"] != "NOT_PERFORMED":
        raise PublicationMockError("PUBLICATION_ALREADY_EVALUATED")
    if value["relying_party_decision"] != "NOT_MADE":
        raise PublicationMockError("BUSINESS_DECISION_NOT_ALLOWED")
    if value["proof_validity_is_telemetry_truth"] is not False:
        raise PublicationMockError("TELEMETRY_TRUTH_OVERCLAIM")
    if value["private_witness_disclosed"] is not False:
        raise PublicationMockError("PRIVATE_WITNESS_DISCLOSURE_NOT_ALLOWED")
    if value["command_path"] != "NONE":
        raise PublicationMockError("COMMAND_PATH_NOT_ALLOWED")

    assurance = value["assurance"]
    if assurance.get("demonstrator") != "A0_SYNTHETIC":
        raise PublicationMockError("UNSUPPORTED_DEMONSTRATOR_ASSURANCE")
    telemetry = value["telemetry"]
    if telemetry.get("assurance_id") != "A0_SYNTHETIC":
        raise PublicationMockError("UNSUPPORTED_TELEMETRY_ASSURANCE")

    return copy.deepcopy(value)


def _validate_subject_digest(subject_digest: str) -> None:
    if not isinstance(subject_digest, str) or HEX_256.fullmatch(subject_digest) is None:
        raise PublicationMockError("INVALID_SYNTHETIC_SUBJECT_DIGEST")


def _mock_receipt() -> dict[str, Any]:
    base = {
        "profile": PROFILE,
        "marker": MOCK_MARKER,
        "state": "FINALIZED",
        "authentication": "NOT_PERFORMED",
        "signature": "NOT_PERFORMED",
        "subject_binding": "NOT_PERFORMED",
        "verification_authority": "NONE",
    }
    record_digest = hashlib.sha256(RECORD_DOMAIN + _canonical_json(base)).hexdigest()
    return {**base, "mock_record_digest": record_digest}


def _public_result(
    verifier_result: dict[str, Any],
    *,
    state: str,
    lifecycle: list[str],
    reason: str | None,
    receipt: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "labels": list(LABELS),
        "marker": MOCK_MARKER,
        "verifier_result": copy.deepcopy(verifier_result),
        "publication_adapter": {
            "state": state,
            "lifecycle": list(lifecycle),
            "reason": reason,
            "receipt": copy.deepcopy(receipt),
            "authentication": "NOT_PERFORMED",
            "subject_binding": "NOT_PERFORMED",
        },
    }


def publish(
    *,
    subject_digest: str,
    verifier_result: dict[str, Any],
    behavior: str = "finalize",
) -> dict[str, Any]:
    """Exercise publication behavior without persisting or emitting subject correlation data."""
    _validate_subject_digest(subject_digest)
    minimized = validate_minimized_verifier_result(verifier_result)

    if behavior == "not_performed":
        return _public_result(
            minimized,
            state="NOT_PERFORMED",
            lifecycle=["NOT_PERFORMED"],
            reason=None,
            receipt=None,
        )

    if behavior == "outage":
        return _public_result(
            minimized,
            state="SUBMISSION_FAILED",
            lifecycle=["SUBMITTED", "SUBMISSION_FAILED"],
            reason="MOCK_PUBLISHER_UNAVAILABLE",
            receipt=None,
        )

    if behavior != "finalize":
        raise PublicationMockError("UNSUPPORTED_MOCK_BEHAVIOR")

    return _public_result(
        minimized,
        state="FINALIZED",
        lifecycle=["SUBMITTED", "FINALIZED"],
        reason=None,
        receipt=_mock_receipt(),
    )
