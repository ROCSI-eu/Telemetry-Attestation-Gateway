#!/usr/bin/env python3
"""Synthetic local mock gateway/operator-boundary experiment.

EXPERIMENTAL
SYNTHETIC_ONLY
A0_SYNTHETIC
NOT VALIDATION OR PRODUCTION AUTHORIZATION
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import tempfile
import threading
from typing import Any, Callable

HERE = Path(__file__).resolve().parent
EXPERIMENTS_ROOT = HERE.parent
END_TO_END_DEMO = EXPERIMENTS_ROOT / "end-to-end-v0" / "demo.py"
DEFAULT_CAPTURE_FILE = EXPERIMENTS_ROOT / "mavlink-normalization-v0" / "fixtures.json"

LABELS = (
    "EXPERIMENTAL",
    "SYNTHETIC_ONLY",
    "A0_SYNTHETIC",
    "NOT VALIDATION OR PRODUCTION AUTHORIZATION",
)

UINT32_MAX = (1 << 32) - 1
FINAL_STATES = {"VERIFIED", "REJECTED", "FAILED"}
ALLOWED_TRANSITIONS = {
    "RECEIVED": {"PROVING", "REJECTED", "FAILED"},
    "PROVING": {"PROVED", "REJECTED", "FAILED"},
    "PROVED": {"VERIFIED", "REJECTED", "FAILED"},
    "VERIFIED": set(),
    "REJECTED": set(),
    "FAILED": set(),
}


class GatewayError(ValueError):
    """Stable input/state error for the local mock gateway."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


class RetryableStageError(RuntimeError):
    """Injected or observed retryable service-stage failure."""

    def __init__(self, stage: str, code: str) -> None:
        super().__init__(code)
        self.stage = stage
        self.code = code


Runner = Callable[[str, int, Path], dict[str, Any]]


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def _digest_idempotency_key(key: str) -> str:
    if not isinstance(key, str) or not key or len(key) > 256:
        raise GatewayError("INVALID_IDEMPOTENCY_KEY")
    material = b"TAG_MOCK_GATEWAY_IDEMPOTENCY_V0\x00" + key.encode("utf-8")
    return hashlib.sha256(material).hexdigest()


def _request_fingerprint(capture_name: str, maximum_speed_cm_s: int) -> str:
    if not isinstance(capture_name, str) or not capture_name or len(capture_name) > 128:
        raise GatewayError("INVALID_CAPTURE_REFERENCE")
    if (
        isinstance(maximum_speed_cm_s, bool)
        or not isinstance(maximum_speed_cm_s, int)
        or not 0 <= maximum_speed_cm_s <= UINT32_MAX
    ):
        raise GatewayError("INVALID_PUBLIC_LIMIT")
    return hashlib.sha256(
        b"TAG_MOCK_GATEWAY_REQUEST_V0\x00"
        + _canonical_json(
            {
                "capture_reference": capture_name,
                "maximum_speed_cm_s": maximum_speed_cm_s,
            }
        )
    ).hexdigest()


def _load_end_to_end_demo():
    spec = importlib.util.spec_from_file_location("tag_end_to_end_v0_demo", END_TO_END_DEMO)
    if spec is None or spec.loader is None:
        raise RetryableStageError("PROVING", "END_TO_END_RUNNER_UNAVAILABLE")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except (ImportError, OSError) as exc:
        raise RetryableStageError(
            "PROVING", "END_TO_END_RUNNER_UNAVAILABLE"
        ) from exc
    return module


def existing_end_to_end_runner(
    capture_name: str, maximum_speed_cm_s: int, package_dir: Path
) -> dict[str, Any]:
    """Use the existing synthetic end-to-end proof/verifier path unchanged."""
    module = _load_end_to_end_demo()
    try:
        return module.run_fixture(
            DEFAULT_CAPTURE_FILE,
            capture_name,
            maximum_speed_cm_s,
            package_dir=package_dir,
        )
    except Exception as exc:
        # The underlying experiment already returns typed failures for expected cases.
        # Unexpected failures remain retryable and do not become INVALID.
        raise RetryableStageError("END_TO_END", "END_TO_END_EXECUTION_FAILED") from exc


def _copy_fields(value: Any, fields: tuple[str, ...]) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    return {key: copy.deepcopy(value[key]) for key in fields if key in value}


def _minimal_verifier_dimensions(raw: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {
        "labels": list(LABELS),
        "invocation": _copy_fields(raw.get("invocation"), ("status", "reason")),
        "telemetry": _copy_fields(
            raw.get("telemetry"),
            ("status", "reason", "assurance_id", "source_trust"),
        ),
        "verification_input": _copy_fields(
            raw.get("verification_input"), ("status", "reason")
        ),
        "cryptographic": _copy_fields(
            raw.get("cryptographic"), ("status", "reason")
        ),
        "assurance": _copy_fields(
            raw.get("assurance"),
            ("declared", "effective", "required", "demonstrator"),
        ),
    }
    for key in (
        "predicate",
        "proof_generation",
        "policy",
        "freshness",
        "revocation",
        "replay",
    ):
        if key in raw and isinstance(raw[key], (str, int, bool, type(None))):
            result[key] = copy.deepcopy(raw[key])
    publication = raw.get("publication")
    result["publication"] = (
        publication if isinstance(publication, str) else "NOT_PERFORMED"
    )
    relying_party_decision = raw.get("relying_party_decision")
    result["relying_party_decision"] = (
        relying_party_decision
        if isinstance(relying_party_decision, str)
        else "NOT_MADE"
    )
    result["proof_validity_is_telemetry_truth"] = False
    result["private_witness_disclosed"] = False
    result["command_path"] = "NONE"
    return result


def _failure_dimensions(stage: str, reason: str) -> dict[str, Any]:
    return {
        "labels": list(LABELS),
        "invocation": {"status": "ACCEPTED", "reason": None},
        "telemetry": {
            "status": "NOT_CHECKED",
            "reason": None,
            "assurance_id": "A0_SYNTHETIC",
            "source_trust": "NOT_EVALUATED",
        },
        "predicate": "NOT_EVALUATED",
        "proof_generation": "UNAVAILABLE" if stage == "PROVING" else "NOT_REPEATED",
        "verification_input": {
            "status": "UNAVAILABLE" if stage == "VERIFYING" else "NOT_CHECKED",
            "reason": reason if stage == "VERIFYING" else None,
        },
        "cryptographic": {"status": "UNVERIFIABLE", "reason": reason},
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


def _classify_result(result: dict[str, Any]) -> tuple[str, str | None]:
    invocation = result.get("invocation")
    if isinstance(invocation, dict) and invocation.get("status") == "REJECTED":
        return "REJECTED", str(invocation.get("reason") or "INVOCATION_REJECTED")

    telemetry = result.get("telemetry")
    if isinstance(telemetry, dict) and telemetry.get("status") == "REJECTED":
        return "REJECTED", str(telemetry.get("reason") or "TELEMETRY_REJECTED")

    if result.get("predicate") == "NOT_SATISFIED":
        return "REJECTED", "PREDICATE_NOT_SATISFIED"

    proof_generation = result.get("proof_generation")
    if proof_generation in {"UNAVAILABLE", "FAILED"}:
        raise RetryableStageError("PROVING", "PROVER_UNAVAILABLE_OR_FAILED")

    verification_input = result.get("verification_input")
    if isinstance(verification_input, dict):
        input_status = verification_input.get("status")
        if input_status in {"REJECTED", "INCOMPATIBLE"}:
            return "REJECTED", str(
                verification_input.get("reason") or "VERIFICATION_INPUT_REJECTED"
            )
        if input_status == "UNAVAILABLE":
            raise RetryableStageError(
                "VERIFYING",
                str(verification_input.get("reason") or "VERIFIER_UNAVAILABLE"),
            )

    cryptographic = result.get("cryptographic")
    crypto_status = cryptographic.get("status") if isinstance(cryptographic, dict) else None
    crypto_reason = (
        cryptographic.get("reason") if isinstance(cryptographic, dict) else None
    )
    if crypto_status == "VALID":
        return "VERIFIED", None
    if crypto_status == "INVALID":
        return "REJECTED", str(crypto_reason or "PROOF_INVALID")
    if crypto_status == "UNVERIFIABLE":
        raise RetryableStageError(
            "VERIFYING", str(crypto_reason or "VERIFIER_UNAVAILABLE_OR_FAILED")
        )
    raise RetryableStageError("VERIFYING", "VERIFIER_RESULT_UNAVAILABLE")


class MockGateway:
    """Minimal local persistence and retry boundary around the existing experiment."""

    def __init__(
        self,
        state_path: Path,
        *,
        max_attempts: int = 3,
        runner: Runner = existing_end_to_end_runner,
    ) -> None:
        if not isinstance(max_attempts, int) or not 1 <= max_attempts <= 16:
            raise GatewayError("INVALID_RETRY_BUDGET")
        self.state_path = Path(state_path)
        self.max_attempts = max_attempts
        self.runner = runner
        self._lock = threading.RLock()
        self._state = self._load_state()

    def _empty_state(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "labels": list(LABELS),
            "records": {},
        }

    def _load_state(self) -> dict[str, Any]:
        if not self.state_path.exists():
            return self._empty_state()
        try:
            value = json.loads(self.state_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise GatewayError("STATE_UNAVAILABLE_OR_INVALID") from exc
        if (
            not isinstance(value, dict)
            or value.get("schema_version") != 1
            or not isinstance(value.get("records"), dict)
        ):
            raise GatewayError("STATE_UNAVAILABLE_OR_INVALID")
        return value

    def _persist(self) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(self._state, indent=2, sort_keys=True) + "\n"
        fd, temp_name = tempfile.mkstemp(
            prefix=".mock-gateway-state-", dir=str(self.state_path.parent)
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, self.state_path)
        finally:
            try:
                os.unlink(temp_name)
            except FileNotFoundError:
                pass

    def _transition(self, record: dict[str, Any], new_state: str) -> None:
        current = record["state"]
        if new_state == current:
            return
        if new_state not in ALLOWED_TRANSITIONS.get(current, set()):
            raise GatewayError("INVALID_LIFECYCLE_TRANSITION")
        record["state"] = new_state
        record["lifecycle"].append(new_state)
        self._persist()

    @staticmethod
    def _attempt_count(record: dict[str, Any]) -> int:
        return sum(
            1
            for event in record["attempts"]
            if event.get("outcome") == "STARTED"
        )

    @staticmethod
    def _attempt_finished(record: dict[str, Any], number: int) -> bool:
        return any(
            event.get("number") == number
            and event.get("outcome") in {"COMPLETED", "RETRYABLE_FAILURE", "INTERRUPTED"}
            for event in record["attempts"]
        )

    def _reconcile_interrupted_attempt(self, record: dict[str, Any]) -> None:
        count = self._attempt_count(record)
        if count and not self._attempt_finished(record, count):
            record["attempts"].append(
                {
                    "number": count,
                    "stage": "END_TO_END",
                    "outcome": "INTERRUPTED",
                    "reason": "PROCESS_INTERRUPTED",
                }
            )
            record["reason"] = "PROCESS_INTERRUPTED"
            self._persist()

    def _public_view(
        self,
        record: dict[str, Any],
        *,
        replayed: bool = False,
        override_reason: str | None = None,
    ) -> dict[str, Any]:
        return {
            "labels": list(LABELS),
            "state": record["state"],
            "lifecycle": list(record["lifecycle"]),
            "attempt_count": self._attempt_count(record),
            "attempts": copy.deepcopy(record["attempts"]),
            "result": copy.deepcopy(record.get("result")),
            "reason": override_reason if override_reason is not None else record.get("reason"),
            "idempotent_replay": replayed,
            "proof_package_disposed": bool(record.get("proof_package_disposed", False)),
        }

    def get_status(self, idempotency_key: str) -> dict[str, Any]:
        with self._lock:
            key_digest = _digest_idempotency_key(idempotency_key)
            record = self._state["records"].get(key_digest)
            if record is None:
                return {
                    "labels": list(LABELS),
                    "state": "NOT_FOUND",
                    "reason": "NOT_FOUND",
                }
            return self._public_view(record, replayed=True)

    def submit(
        self,
        *,
        idempotency_key: str,
        capture_name: str,
        maximum_speed_cm_s: int,
    ) -> dict[str, Any]:
        with self._lock:
            key_digest = _digest_idempotency_key(idempotency_key)
            fingerprint = _request_fingerprint(capture_name, maximum_speed_cm_s)
            record = self._state["records"].get(key_digest)

            if record is not None:
                if record["request_fingerprint"] != fingerprint:
                    return {
                        "labels": list(LABELS),
                        "state": "ERROR",
                        "reason": "IDEMPOTENCY_CONFLICT",
                        "idempotent_replay": False,
                    }
                if record["state"] in FINAL_STATES:
                    return self._public_view(record, replayed=True)
            else:
                record = {
                    "request_fingerprint": fingerprint,
                    "state": "RECEIVED",
                    "lifecycle": ["RECEIVED"],
                    "attempts": [],
                    "reason": None,
                    "result": None,
                    "proof_package_disposed": False,
                }
                self._state["records"][key_digest] = record
                self._persist()

            if record["state"] == "RECEIVED":
                self._transition(record, "PROVING")
            else:
                self._reconcile_interrupted_attempt(record)

            while self._attempt_count(record) < self.max_attempts:
                attempt_number = self._attempt_count(record) + 1
                record["attempts"].append(
                    {
                        "number": attempt_number,
                        "stage": "END_TO_END",
                        "outcome": "STARTED",
                        "reason": None,
                    }
                )
                self._persist()
                package_dir = Path(
                    tempfile.mkdtemp(prefix="tag-mock-gateway-proof-")
                )
                try:
                    raw = self.runner(
                        capture_name,
                        maximum_speed_cm_s,
                        package_dir,
                    )
                    if not isinstance(raw, dict):
                        raise RetryableStageError(
                            "VERIFYING", "RUNNER_RESULT_UNAVAILABLE"
                        )
                    result = _minimal_verifier_dimensions(raw)
                    terminal_state, reason = _classify_result(result)
                except RetryableStageError as exc:
                    record["attempts"].append(
                        {
                            "number": attempt_number,
                            "stage": exc.stage,
                            "outcome": "RETRYABLE_FAILURE",
                            "reason": exc.code,
                        }
                    )
                    record["result"] = _failure_dimensions(exc.stage, exc.code)
                    record["reason"] = exc.code
                    self._persist()
                    if self._attempt_count(record) >= self.max_attempts:
                        self._transition(record, "FAILED")
                        return self._public_view(record)
                    continue
                finally:
                    shutil.rmtree(package_dir, ignore_errors=True)
                    record["proof_package_disposed"] = not package_dir.exists()
                    self._persist()

                record["attempts"].append(
                    {
                        "number": attempt_number,
                        "stage": "END_TO_END",
                        "outcome": "COMPLETED",
                        "reason": reason,
                    }
                )
                record["result"] = result
                record["reason"] = reason
                self._persist()

                if result.get("proof_generation") == "GENERATED":
                    self._transition(record, "PROVED")

                if terminal_state == "VERIFIED":
                    if record["state"] == "PROVING":
                        self._transition(record, "PROVED")
                    self._transition(record, "VERIFIED")
                else:
                    self._transition(record, "REJECTED")
                return self._public_view(record)

            record["reason"] = "RETRY_BUDGET_EXHAUSTED"
            record["result"] = _failure_dimensions("VERIFYING", record["reason"])
            self._transition(record, "FAILED")
            return self._public_view(record)


def _cli() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-file", type=Path, required=True)
    parser.add_argument("--idempotency-key", required=True)
    parser.add_argument("--capture-name", default="unsigned-consistent")
    parser.add_argument("--maximum-speed-cm-s", type=int, required=True)
    parser.add_argument("--max-attempts", type=int, default=3)
    args = parser.parse_args()

    try:
        gateway = MockGateway(
            args.state_file,
            max_attempts=args.max_attempts,
        )
        result = gateway.submit(
            idempotency_key=args.idempotency_key,
            capture_name=args.capture_name,
            maximum_speed_cm_s=args.maximum_speed_cm_s,
        )
    except GatewayError as exc:
        result = {
            "labels": list(LABELS),
            "state": "ERROR",
            "reason": exc.code,
        }

    print(json.dumps(result, indent=2, sort_keys=True))
    state = result.get("state")
    if state == "VERIFIED":
        return 0
    if state == "REJECTED":
        return 3
    if state == "FAILED":
        return 5
    return 6


if __name__ == "__main__":
    raise SystemExit(_cli())
