#!/usr/bin/env python3
"""Provisional substrate-neutral publication adapter experiment.

EXPERIMENTAL
SYNTHETIC_ONLY
A0_SYNTHETIC
NOT VALIDATION OR PRODUCTION AUTHORIZATION
"""

from __future__ import annotations

from dataclasses import dataclass
import copy
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from typing import Any, Protocol

LABELS = (
    "EXPERIMENTAL",
    "SYNTHETIC_ONLY",
    "A0_SYNTHETIC",
    "NOT VALIDATION OR PRODUCTION AUTHORIZATION",
)
CONTRACT_VERSION = "TAG_PUBLICATION_ADAPTER_CONTRACT_V0_EXPERIMENTAL"
PROFILE = "TAG_PUBLICATION_PROFILE_TEST_V0"
ALT_PROFILE = "TAG_PUBLICATION_PROFILE_TEST_V0_ALT"
SUPPORTED_PROFILES = frozenset({PROFILE, ALT_PROFILE})
TEST_CLOCK_AUTHORITY = "TEST_FIXED_CLOCK_V0"
TEST_RECORDED_TIME = "2000-01-01T00:00:00Z"
HEX_256 = re.compile(r"^[0-9a-f]{64}$")
RECORD_ID = re.compile(r"^rec_[0-9a-f]{24}$")
IDEMPOTENCY_KEY = re.compile(r"^idk_[0-9a-f]{32}$")
ALLOWED_METADATA_KEYS = frozenset({"fixture", "scenario"})
RECORD_DOMAIN = b"TAG_PUBLICATION_ADAPTER_RECORD_V0\x00"

_ALLOWED_TRANSITIONS = {
    "pending": {"recorded", "failed"},
    "recorded": {"final", "superseded", "failed"},
    "final": {"superseded"},
    "superseded": set(),
    "failed": set(),
}


class PublicationAdapterError(ValueError):
    """Stable non-sensitive caller-visible adapter error."""

    def __init__(self, code: str, classification: str, retryable: bool) -> None:
        super().__init__(code)
        self.code = code
        self.classification = classification
        self.retryable = retryable

    def public(self) -> dict[str, Any]:
        return {
            "labels": list(LABELS),
            "contract_version": CONTRACT_VERSION,
            "error": {
                "code": self.code,
                "classification": self.classification,
                "retryable": self.retryable,
            },
        }


@dataclass(frozen=True)
class PublicationRequest:
    """Provisional request shape; raw idempotency keys are internal-only."""

    idempotency_key: str
    payload_digest: str
    metadata: dict[str, str]
    profile: str = PROFILE


class ProvisionalPublicationAdapter(Protocol):
    """Experimental port shared by local deterministic adapters only."""

    substrate: str

    def submit(self, request: PublicationRequest) -> dict[str, Any]: ...

    def status(self, record_id: str) -> dict[str, Any]: ...


def synthetic_payload_digest(label: str) -> str:
    if not isinstance(label, str) or not label or len(label) > 128:
        raise PublicationAdapterError("INVALID_SYNTHETIC_LABEL", "malformed", False)
    return hashlib.sha256(b"TAG_SYNTHETIC_PAYLOAD_V0\x00" + label.encode()).hexdigest()


def _validate_request(request: PublicationRequest) -> None:
    if not isinstance(request, PublicationRequest):
        raise PublicationAdapterError("INVALID_REQUEST", "malformed", False)
    # Keep the secret input namespace disjoint from every caller-visible value.
    # This is deliberately narrower than accepting arbitrary opaque strings: none
    # of the fixed labels, states, errors, profiles, substrates, or record handles
    # emitted by this experiment can satisfy this format.
    if (
        not isinstance(request.idempotency_key, str)
        or IDEMPOTENCY_KEY.fullmatch(request.idempotency_key) is None
    ):
        raise PublicationAdapterError("INVALID_IDEMPOTENCY_KEY", "malformed", False)
    if not isinstance(request.payload_digest, str) or HEX_256.fullmatch(request.payload_digest) is None:
        raise PublicationAdapterError("INVALID_PAYLOAD_DIGEST", "malformed", False)
    if not isinstance(request.profile, str) or request.profile not in SUPPORTED_PROFILES:
        raise PublicationAdapterError("UNSUPPORTED_PUBLICATION_PROFILE", "rejected", False)
    if not isinstance(request.metadata, dict) or not set(request.metadata).issubset(ALLOWED_METADATA_KEYS):
        raise PublicationAdapterError("INVALID_METADATA", "malformed", False)
    for key, value in request.metadata.items():
        if (
            not isinstance(key, str)
            or not isinstance(value, str)
            or len(value) > 64
            or not value.startswith("synthetic-")
            or request.idempotency_key in value
        ):
            raise PublicationAdapterError("INVALID_METADATA", "malformed", False)


def _record_id_for_key(raw_key: str) -> str:
    return "rec_" + hashlib.sha256(RECORD_DOMAIN + raw_key.encode()).hexdigest()[:24]


def _same_request(record: dict[str, Any], request: PublicationRequest) -> bool:
    return (
        record["payload_digest"] == request.payload_digest
        and record["metadata"] == request.metadata
        and record["profile"] == request.profile
    )


def _new_record(request: PublicationRequest, substrate: str) -> dict[str, Any]:
    return {
        "record_id": _record_id_for_key(request.idempotency_key),
        "payload_digest": request.payload_digest,
        "metadata": copy.deepcopy(request.metadata),
        "profile": request.profile,
        "substrate": substrate,
        "state": "pending",
        "lifecycle": ["pending"],
        "recorded_time": None,
        "time_authority": None,
        "receipt_state": "NOT_ISSUED",
        "error": None,
    }


def _transition(record: dict[str, Any], target: str) -> None:
    current = record["state"]
    if target not in _ALLOWED_TRANSITIONS[current]:
        raise PublicationAdapterError("INVALID_LIFECYCLE_TRANSITION", "rejected", False)
    record["state"] = target
    record["lifecycle"].append(target)
    if target in {"recorded", "final", "superseded"} and record["recorded_time"] is None:
        record["recorded_time"] = TEST_RECORDED_TIME
        record["time_authority"] = TEST_CLOCK_AUTHORITY
    if target == "final":
        record["receipt_state"] = "MOCK_FINAL"
    elif target == "superseded":
        record["receipt_state"] = "MOCK_SUPERSEDED"
    elif target == "failed":
        record["receipt_state"] = "NOT_ISSUED"


def _public_result(record: dict[str, Any]) -> dict[str, Any]:
    result = {
        "labels": list(LABELS),
        "contract_version": CONTRACT_VERSION,
        "substrate": record["substrate"],
        "profile": record["profile"],
        "record_id": record["record_id"],
        "payload_digest": record["payload_digest"],
        "metadata": copy.deepcopy(record["metadata"]),
        "state": record["state"],
        "lifecycle": list(record["lifecycle"]),
        "recorded_time": record["recorded_time"],
        "time_authority": record["time_authority"],
        "receipt_state": record["receipt_state"],
        "error": copy.deepcopy(record["error"]),
    }
    return result


def _error(code: str, classification: str, retryable: bool) -> dict[str, Any]:
    return {"code": code, "classification": classification, "retryable": retryable}


def _valid_error(value: Any) -> bool:
    return value is None or (
        isinstance(value, dict)
        and set(value) == {"code", "classification", "retryable"}
        and isinstance(value["code"], str)
        and isinstance(value["classification"], str)
        and isinstance(value["retryable"], bool)
    )


def _error_matches_state(state: str, value: Any) -> bool:
    """Accept only error combinations the deterministic local adapter emits."""
    if state == "pending":
        return value is None or value in (
            _error("SUBMISSION_TIMEOUT", "retryable", True),
            _error("SUBMISSION_CANCELLED", "retryable", True),
        )
    if state == "failed":
        return value == _error("SUBSTRATE_REJECTED", "definitive", False)
    return value is None


def _valid_record(record_id: str, record: Any) -> bool:
    expected_keys = {
        "record_id",
        "payload_digest",
        "metadata",
        "profile",
        "substrate",
        "state",
        "lifecycle",
        "recorded_time",
        "time_authority",
        "receipt_state",
        "error",
    }
    lifecycle_paths = {
        ("pending",),
        ("pending", "failed"),
        ("pending", "recorded"),
        ("pending", "recorded", "failed"),
        ("pending", "recorded", "final"),
        ("pending", "recorded", "superseded"),
        ("pending", "recorded", "final", "superseded"),
    }
    if not isinstance(record, dict) or set(record) != expected_keys:
        return False
    metadata = record["metadata"]
    lifecycle = record["lifecycle"]
    if (
        RECORD_ID.fullmatch(record_id) is None
        or record["record_id"] != record_id
        or not isinstance(record["payload_digest"], str)
        or HEX_256.fullmatch(record["payload_digest"]) is None
        or not isinstance(record["profile"], str)
        or record["profile"] not in SUPPORTED_PROFILES
        or record["substrate"] != DeterministicLocalAdapter.substrate
        or not isinstance(metadata, dict)
        or not set(metadata).issubset(ALLOWED_METADATA_KEYS)
        or any(
            not isinstance(value, str)
            or len(value) > 64
            or not value.startswith("synthetic-")
            for value in metadata.values()
        )
        or not isinstance(lifecycle, list)
        or not all(isinstance(state, str) for state in lifecycle)
        or tuple(lifecycle) not in lifecycle_paths
        or record["state"] != lifecycle[-1]
        or not _valid_error(record["error"])
        or not _error_matches_state(record["state"], record["error"])
    ):
        return False
    was_recorded = "recorded" in lifecycle
    if was_recorded and (
        record["recorded_time"] != TEST_RECORDED_TIME
        or record["time_authority"] != TEST_CLOCK_AUTHORITY
    ):
        return False
    if not was_recorded and (
        record["recorded_time"] is not None or record["time_authority"] is not None
    ):
        return False
    expected_receipt = {
        "final": "MOCK_FINAL",
        "superseded": "MOCK_SUPERSEDED",
    }.get(record["state"], "NOT_ISSUED")
    return record["receipt_state"] == expected_receipt


def _valid_local_state(state: Any) -> bool:
    expected_keys = {"labels", "contract_version", "state_profile", "records"}
    if (
        not isinstance(state, dict)
        or set(state) != expected_keys
        or state["labels"] != list(LABELS)
        or state["contract_version"] != CONTRACT_VERSION
        or state["state_profile"] != "DISPOSABLE_LOCAL_TEST_STATE_V0"
        or not isinstance(state["records"], dict)
    ):
        return False
    return all(_valid_record(record_id, record) for record_id, record in state["records"].items())


class DisabledAdapter:
    """No-publication adapter with in-memory test-only lookup/idempotency semantics."""

    substrate = "disabled-local-v0"

    def __init__(self) -> None:
        self._records: dict[str, dict[str, Any]] = {}

    def submit(self, request: PublicationRequest) -> dict[str, Any]:
        _validate_request(request)
        record_id = _record_id_for_key(request.idempotency_key)
        existing = self._records.get(record_id)
        if existing is not None:
            if not _same_request(existing, request):
                raise PublicationAdapterError("IDEMPOTENCY_CONFLICT", "rejected", False)
            return _public_result(existing)

        record = _new_record(request, self.substrate)
        _transition(record, "failed")
        record["error"] = _error("PUBLICATION_DISABLED", "definitive", False)
        self._records[record["record_id"]] = record
        return _public_result(record)

    def status(self, record_id: str) -> dict[str, Any]:
        _validate_record_id(record_id)
        try:
            return _public_result(self._records[record_id])
        except KeyError as exc:
            raise PublicationAdapterError("UNKNOWN_RECORD", "not_found", False) from exc


class DeterministicLocalAdapter:
    """Disposable JSON-state publication mock for deterministic conformance evidence."""

    substrate = "deterministic-local-mock-v0"

    def __init__(self, state_path: Path, *, fault_once: str | None = None) -> None:
        if fault_once not in {None, "timeout", "cancelled", "unavailable", "definitive_failure"}:
            raise PublicationAdapterError("UNSUPPORTED_TEST_FAULT", "malformed", False)
        self.state_path = Path(state_path)
        self.fault_once = fault_once
        self._state = self._load()

    def _empty_state(self) -> dict[str, Any]:
        return {
            "labels": list(LABELS),
            "contract_version": CONTRACT_VERSION,
            "state_profile": "DISPOSABLE_LOCAL_TEST_STATE_V0",
            "records": {},
        }

    def _load(self) -> dict[str, Any]:
        try:
            if not self.state_path.exists():
                return self._empty_state()
            loaded = json.loads(self.state_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise PublicationAdapterError("INVALID_LOCAL_STATE", "definitive", False) from exc
        except OSError as exc:
            raise PublicationAdapterError("LOCAL_STATE_IO_FAILURE", "retryable", True) from exc
        if not _valid_local_state(loaded):
            raise PublicationAdapterError("INVALID_LOCAL_STATE", "definitive", False)
        return loaded

    def _save(self) -> None:
        temporary_name: str | None = None
        try:
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.state_path.parent,
                prefix=self.state_path.name + ".",
                suffix=".tmp",
                delete=False,
            ) as temporary:
                temporary_name = temporary.name
                temporary.write(json.dumps(self._state, indent=2, sort_keys=True) + "\n")
                temporary.flush()
                os.fsync(temporary.fileno())
            os.replace(temporary_name, self.state_path)
        except OSError as exc:
            raise PublicationAdapterError("LOCAL_STATE_IO_FAILURE", "retryable", True) from exc
        finally:
            if temporary_name is not None:
                try:
                    Path(temporary_name).unlink(missing_ok=True)
                except OSError:
                    # Preserve the stable error from the failed persistence operation.
                    pass

    @contextmanager
    def _locked_state(self):
        """Serialize each read/modify/write transaction across adapter instances."""
        try:
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
            lock_path = self.state_path.with_suffix(self.state_path.suffix + ".lock")
            with lock_path.open("a+", encoding="utf-8") as lock_file:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
                try:
                    self._refresh()
                    yield
                finally:
                    fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
        except OSError as exc:
            raise PublicationAdapterError("LOCAL_STATE_IO_FAILURE", "retryable", True) from exc

    def _refresh(self) -> None:
        self._state = self._load()

    def submit(self, request: PublicationRequest) -> dict[str, Any]:
        _validate_request(request)
        with self._locked_state():
            record_id = _record_id_for_key(request.idempotency_key)
            record = self._state["records"].get(record_id)
            if record is not None:
                if not _same_request(record, request):
                    raise PublicationAdapterError("IDEMPOTENCY_CONFLICT", "rejected", False)
                if record["state"] == "pending":
                    _transition(record, "recorded")
                    _transition(record, "final")
                    record["error"] = None
                    self._save()
                return _public_result(record)

            if self.fault_once == "unavailable":
                self.fault_once = None
                raise PublicationAdapterError("SUBSTRATE_UNAVAILABLE", "retryable", True)

            record = _new_record(request, self.substrate)
            self._state["records"][record["record_id"]] = record
            self._save()

            fault = self.fault_once
            self.fault_once = None
            if fault in {"timeout", "cancelled"}:
                code = "SUBMISSION_TIMEOUT" if fault == "timeout" else "SUBMISSION_CANCELLED"
                record["error"] = _error(code, "retryable", True)
                self._save()
                return _public_result(record)
            if fault == "definitive_failure":
                _transition(record, "failed")
                record["error"] = _error("SUBSTRATE_REJECTED", "definitive", False)
                self._save()
                return _public_result(record)
            _transition(record, "recorded")
            _transition(record, "final")
            self._save()
            return _public_result(record)

    def status(self, record_id: str) -> dict[str, Any]:
        _validate_record_id(record_id)
        with self._locked_state():
            try:
                return _public_result(self._state["records"][record_id])
            except KeyError as exc:
                raise PublicationAdapterError("UNKNOWN_RECORD", "not_found", False) from exc

    def supersede_for_test(self, record_id: str) -> dict[str, Any]:
        """Exercise final -> superseded; not part of the provisional publication port."""
        _validate_record_id(record_id)
        with self._locked_state():
            try:
                record = self._state["records"][record_id]
            except KeyError as exc:
                raise PublicationAdapterError("UNKNOWN_RECORD", "not_found", False) from exc
            _transition(record, "superseded")
            self._save()
            return _public_result(record)

    def transition_for_test(self, record_id: str, target: str) -> dict[str, Any]:
        """Negative-test hook for skipped/reversed transition rejection only."""
        _validate_record_id(record_id)
        with self._locked_state():
            try:
                record = self._state["records"][record_id]
            except KeyError as exc:
                raise PublicationAdapterError("UNKNOWN_RECORD", "not_found", False) from exc
            _transition(record, target)
            self._save()
            return _public_result(record)


def _validate_record_id(record_id: str) -> None:
    if not isinstance(record_id, str) or RECORD_ID.fullmatch(record_id) is None:
        raise PublicationAdapterError("INVALID_RECORD_HANDLE", "malformed", False)
