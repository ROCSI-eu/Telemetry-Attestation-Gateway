#!/usr/bin/env python3
"""Synthetic-only MAVLink 2 observation normalization experiment.

EXPERIMENTAL
SYNTHETIC_ONLY
A0_SYNTHETIC
NOT VALIDATION OR PRODUCTION AUTHORIZATION

This module is receive/parse/normalize only. It contains no socket, send,
forward, command, or flight-control path.
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import math
import struct
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

LABELS = (
    "EXPERIMENTAL",
    "SYNTHETIC_ONLY",
    "A0_SYNTHETIC",
    "NOT VALIDATION OR PRODUCTION AUTHORIZATION",
)

MAVLINK2_MAGIC = 0xFD
MAVLINK_IFLAG_SIGNED = 0x01
SUPPORTED_INCOMPAT_FLAGS = MAVLINK_IFLAG_SIGNED

GLOBAL_POSITION_INT = 33
VFR_HUD = 74

MESSAGE_SPECS = {
    GLOBAL_POSITION_INT: {
        "name": "GLOBAL_POSITION_INT",
        "full_payload_len": 28,
        "crc_extra": 104,
    },
    VFR_HUD: {
        "name": "VFR_HUD",
        "full_payload_len": 20,
        "crc_extra": 20,
    },
}

TRUST_SIGNED_VALID = "SIGNED_VALID"
TRUST_UNSIGNED = "UNSIGNED"
TRUST_SIGNATURE_INVALID = "SIGNATURE_INVALID"
TRUST_UNKNOWN = "UNKNOWN"

UINT32_MAX = (1 << 32) - 1
INT16_MIN = -(1 << 15)
INT16_MAX = (1 << 15) - 1


class NormalizationError(ValueError):
    """Typed failure for the experimental receive-only normalization path."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True)
class ParsedFrame:
    msg_id: int
    message_name: str
    seq: int
    system_id: int
    component_id: int
    payload: bytes
    trust: str
    signature_link_id: int | None
    signature_timestamp: int | None


def _fail(code: str, message: str) -> None:
    raise NormalizationError(code, message)


def _x25_accumulate(crc: int, byte: int) -> int:
    tmp = byte ^ (crc & 0xFF)
    tmp ^= (tmp << 4) & 0xFF
    return (
        (crc >> 8)
        ^ (tmp << 8)
        ^ (tmp << 3)
        ^ (tmp >> 4)
    ) & 0xFFFF


def mavlink_crc(header_without_magic: bytes, payload: bytes, crc_extra: int) -> int:
    """CRC-16/MCRF4XX used by MAVLink, including CRC_EXTRA."""
    crc = 0xFFFF
    for byte in header_without_magic + payload:
        crc = _x25_accumulate(crc, byte)
    crc = _x25_accumulate(crc, crc_extra)
    return crc


def _trust_key(
    trust_store: dict[str, str],
    system_id: int,
    component_id: int,
    link_id: int,
) -> bytes | None:
    value = trust_store.get(f"{system_id}:{component_id}:{link_id}")
    if value is None:
        return None
    try:
        key = bytes.fromhex(value)
    except (TypeError, ValueError) as exc:
        _fail("INVALID_TEST_TRUST_STORE", "test trust-store key is not valid hex")
    if len(key) != 32:
        _fail("INVALID_TEST_TRUST_STORE", "test trust-store key must be exactly 32 bytes")
    return key


def parse_mavlink2_frame(
    frame: bytes,
    trust_store: dict[str, str] | None = None,
    signature_timestamps: dict[tuple[int, int, int], int] | None = None,
) -> ParsedFrame:
    """Parse one allowlisted observation frame and verify CRC/signature state.

    `signature_timestamps` is a capture-local anti-replay state keyed by
    (system_id, component_id, link_id). It does not establish trustworthy time.
    """
    trust_store = trust_store or {}
    signature_timestamps = signature_timestamps if signature_timestamps is not None else {}

    if len(frame) < 12:
        _fail("MALFORMED_FRAME", "frame is shorter than a MAVLink 2 packet")
    if frame[0] != MAVLINK2_MAGIC:
        _fail("UNSUPPORTED_PROTOCOL", "only MAVLink 2 frames are accepted in this experiment")

    payload_len = frame[1]
    incompat_flags = frame[2]
    if incompat_flags & ~SUPPORTED_INCOMPAT_FLAGS:
        _fail("UNSUPPORTED_INCOMPAT_FLAG", "frame contains an unsupported MAVLink 2 incompatibility flag")

    signed = bool(incompat_flags & MAVLINK_IFLAG_SIGNED)
    unsigned_len = 12 + payload_len
    expected_len = unsigned_len + (13 if signed else 0)
    if len(frame) != expected_len:
        _fail("MALFORMED_FRAME", f"frame length {len(frame)} does not match header-declared length {expected_len}")

    seq = frame[4]
    system_id = frame[5]
    component_id = frame[6]
    if system_id == 0 or component_id == 0:
        _fail("INVALID_SOURCE_ID", "MAVLink source system/component IDs must be non-zero")

    msg_id = int.from_bytes(frame[7:10], "little")
    spec = MESSAGE_SPECS.get(msg_id)
    if spec is None:
        _fail("UNSUPPORTED_MESSAGE", f"message id {msg_id} is outside the observation allowlist")

    if payload_len == 0 or payload_len > spec["full_payload_len"]:
        _fail(
            "INVALID_PAYLOAD_LENGTH",
            f"{spec['name']} payload length {payload_len} is invalid for the pinned dialect",
        )

    payload = frame[10 : 10 + payload_len]
    received_crc = int.from_bytes(frame[10 + payload_len : 12 + payload_len], "little")
    calculated_crc = mavlink_crc(frame[1:10], payload, spec["crc_extra"])
    if received_crc != calculated_crc:
        _fail("BAD_CRC", "MAVLink frame checksum does not match the pinned message definition")

    trust = TRUST_UNSIGNED
    link_id: int | None = None
    signature_timestamp: int | None = None

    if signed:
        sig = frame[unsigned_len:]
        link_id = sig[0]
        timestamp_bytes = sig[1:7]
        signature_timestamp = int.from_bytes(timestamp_bytes, "little")
        signature = sig[7:13]
        key = _trust_key(trust_store, system_id, component_id, link_id)

        if key is None:
            trust = TRUST_UNKNOWN
        else:
            expected_signature = hashlib.sha256(
                key + frame[:unsigned_len] + bytes([link_id]) + timestamp_bytes
            ).digest()[:6]
            if not hmac.compare_digest(signature, expected_signature):
                _fail("SIGNATURE_INVALID", "MAVLink frame signature does not validate under the supplied test trust store")
            trust = TRUST_SIGNED_VALID

            stream = (system_id, component_id, link_id)
            prior = signature_timestamps.get(stream)
            if prior is not None and signature_timestamp <= prior:
                _fail(
                    "SIGNATURE_TIMESTAMP_REPLAY_OR_REGRESSION",
                    "signed frame timestamp did not increase for the capture-local logical stream",
                )
            signature_timestamps[stream] = signature_timestamp

    padded = payload + b"\x00" * (spec["full_payload_len"] - payload_len)
    return ParsedFrame(
        msg_id=msg_id,
        message_name=spec["name"],
        seq=seq,
        system_id=system_id,
        component_id=component_id,
        payload=padded,
        trust=trust,
        signature_link_id=link_id,
        signature_timestamp=signature_timestamp,
    )


def _ceil_sqrt(value: int) -> int:
    if value < 0:
        _fail("INTERNAL_RANGE_ERROR", "cannot take square root of a negative integer")
    root = math.isqrt(value)
    return root if root * root == value else root + 1


def _binary32_to_fraction(raw: bytes) -> Fraction:
    """Decode one little-endian IEEE-754 binary32 value exactly as a Fraction."""
    if len(raw) != 4:
        _fail("MALFORMED_FLOAT", "binary32 field must be exactly four bytes")
    bits = int.from_bytes(raw, "little")
    sign = -1 if (bits >> 31) else 1
    exponent = (bits >> 23) & 0xFF
    fraction_bits = bits & 0x7FFFFF

    if exponent == 0xFF:
        _fail("NON_FINITE_GROUNDSPEED", "VFR_HUD groundspeed is NaN or infinity")

    if exponent == 0:
        if fraction_bits == 0:
            return Fraction(0, 1)
        significand = fraction_bits
        power = -149
    else:
        significand = (1 << 23) | fraction_bits
        power = exponent - 150

    value = Fraction(sign * significand, 1)
    if power >= 0:
        return value * (1 << power)
    return value / (1 << (-power))


def _ceil_fraction(value: Fraction) -> int:
    return -(-value.numerator // value.denominator)


def _capture_nonnegative_int(name: str, value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        _fail("MALFORMED_CAPTURE", f"{name} must be a non-negative integer")
    return value


def decode_global_position_int(frame: ParsedFrame) -> dict[str, Any]:
    if frame.msg_id != GLOBAL_POSITION_INT:
        _fail("WRONG_MESSAGE_TYPE", "expected GLOBAL_POSITION_INT")
    time_boot_ms, lat, lon, alt, relative_alt, vx, vy, vz, hdg = struct.unpack(
        "<IiiiihhhH", frame.payload
    )
    if not INT16_MIN <= vx <= INT16_MAX or not INT16_MIN <= vy <= INT16_MAX:
        _fail("FIELD_RANGE_ERROR", "GLOBAL_POSITION_INT velocity component is outside int16 range")

    squared = vx * vx + vy * vy
    speed_cm_s = _ceil_sqrt(squared)
    return {
        "time_boot_ms": time_boot_ms,
        "vx_cm_s": vx,
        "vy_cm_s": vy,
        "speed_cm_s": speed_cm_s,
        "rounding": "ceil_euclidean_norm",
    }


def decode_vfr_hud(frame: ParsedFrame) -> dict[str, Any]:
    if frame.msg_id != VFR_HUD:
        _fail("WRONG_MESSAGE_TYPE", "expected VFR_HUD")
    # Wire order after MAVLink field-size ordering:
    # airspeed, groundspeed, alt, climb, heading, throttle.
    groundspeed_m_s = _binary32_to_fraction(frame.payload[4:8])
    if groundspeed_m_s < 0:
        _fail("NEGATIVE_GROUNDSPEED", "VFR_HUD groundspeed must be non-negative for this experiment")
    speed_cm_s = _ceil_fraction(groundspeed_m_s * 100)
    if speed_cm_s > UINT32_MAX:
        _fail("NORMALIZED_SPEED_OVERFLOW", "normalized VFR_HUD groundspeed exceeds uint32")
    return {
        "speed_cm_s": speed_cm_s,
        "binary32_bits_hex": frame.payload[4:8].hex(),
        "rounding": "exact_binary32_times_100_then_ceil",
    }


def normalize_capture(capture: Any) -> dict[str, Any]:
    """Normalize a deterministic synthetic capture into one observation result."""
    if not isinstance(capture, dict):
        _fail("MALFORMED_CAPTURE", "capture must be an object")

    try:
        decision_received_at_ms = _capture_nonnegative_int(
            "decision_received_at_ms", capture["decision_received_at_ms"]
        )
        max_age_ms = _capture_nonnegative_int("max_age_ms", capture["max_age_ms"])
        events = capture["events"]
    except KeyError:
        _fail("MALFORMED_CAPTURE", "capture metadata is missing or invalid")

    if not isinstance(events, list) or not events:
        _fail("MALFORMED_CAPTURE", "capture requires at least one event")

    trust_store = capture.get("test_trust_store", {})
    if not isinstance(trust_store, dict):
        _fail("MALFORMED_CAPTURE", "test_trust_store must be a mapping")

    signature_timestamps: dict[tuple[int, int, int], int] = {}
    source: tuple[int, int] | None = None
    parsed_events: list[dict[str, Any]] = []
    prior_received_at: int | None = None
    prior_boot_ms: int | None = None

    for event in events:
        if not isinstance(event, dict):
            _fail("MALFORMED_CAPTURE", "event must be an object")
        try:
            received_at_ms = _capture_nonnegative_int("received_at_ms", event["received_at_ms"])
            frame_hex = event["frame_hex"]
            if not isinstance(frame_hex, str):
                _fail("MALFORMED_CAPTURE", "event frame_hex must be a hexadecimal string")
            frame_bytes = bytes.fromhex(frame_hex)
        except KeyError:
            _fail("MALFORMED_CAPTURE", "event timestamp/frame hex is invalid")
        except ValueError:
            _fail("MALFORMED_CAPTURE", "event frame_hex is not valid hexadecimal")
        if received_at_ms > decision_received_at_ms:
            _fail(
                "RECEIVER_TIME_IN_FUTURE",
                "event receiver timestamp is later than decision timestamp",
            )
        if decision_received_at_ms - received_at_ms > max_age_ms:
            _fail(
                "STALE_RECEIVER_OBSERVATION",
                "event is older than the capture receiver-age bound",
            )
        if prior_received_at is not None and received_at_ms < prior_received_at:
            _fail("RECEIVER_TIME_REGRESSION", "capture receiver timestamps must be monotonic")
        prior_received_at = received_at_ms

        frame = parse_mavlink2_frame(frame_bytes, trust_store, signature_timestamps)
        this_source = (frame.system_id, frame.component_id)
        if source is None:
            source = this_source
        elif this_source != source:
            _fail("MIXED_SOURCE", "capture contains observation frames from more than one system/component source")

        decoded: dict[str, Any]
        if frame.msg_id == GLOBAL_POSITION_INT:
            decoded = decode_global_position_int(frame)
            boot_ms = decoded["time_boot_ms"]
            if prior_boot_ms is not None and boot_ms < prior_boot_ms:
                _fail(
                    "SOURCE_TIME_REGRESSION_UNSUPPORTED",
                    "GLOBAL_POSITION_INT time_boot_ms regressed; reset/reordering handling is not defined in v0",
                )
            prior_boot_ms = boot_ms
        elif frame.msg_id == VFR_HUD:
            decoded = decode_vfr_hud(frame)
        else:  # defensive; parser already allowlists.
            _fail("UNSUPPORTED_MESSAGE", "message is outside the observation allowlist")

        parsed_events.append(
            {
                "received_at_ms": received_at_ms,
                "message_id": frame.msg_id,
                "message_name": frame.message_name,
                "trust": frame.trust,
                "signature_link_id": frame.signature_link_id,
                "signature_timestamp": frame.signature_timestamp,
                "decoded": decoded,
            }
        )

    gpi_events = [event for event in parsed_events if event["message_id"] == GLOBAL_POSITION_INT]
    if not gpi_events:
        _fail("MISSING_PRIMARY_SPEED_SOURCE", "GLOBAL_POSITION_INT is required as the v0 primary speed source")

    selected = gpi_events[-1]
    age_ms = decision_received_at_ms - selected["received_at_ms"]
    if age_ms < 0:
        _fail("RECEIVER_TIME_IN_FUTURE", "selected observation receiver timestamp is later than decision timestamp")
    if age_ms > max_age_ms:
        _fail("STALE_RECEIVER_OBSERVATION", "selected observation is older than the capture receiver-age bound")

    trusts = [event["trust"] for event in parsed_events]
    if TRUST_SIGNATURE_INVALID in trusts:
        # Unreachable: invalid signatures fail during parsing, kept defensive.
        aggregate_trust = TRUST_SIGNATURE_INVALID
    elif trusts and all(value == TRUST_SIGNED_VALID for value in trusts):
        aggregate_trust = TRUST_SIGNED_VALID
    elif any(value == TRUST_UNKNOWN for value in trusts):
        aggregate_trust = TRUST_UNKNOWN
    else:
        aggregate_trust = TRUST_UNSIGNED

    vfr_events = [event for event in parsed_events if event["message_id"] == VFR_HUD]
    diagnostic_vfr_speed = vfr_events[-1]["decoded"]["speed_cm_s"] if vfr_events else None

    return {
        "labels": list(LABELS),
        "status": "NORMALIZED",
        "assurance_id": "A0_SYNTHETIC",
        "source": {
            "system_id": source[0] if source else None,
            "component_id": source[1] if source else None,
            "trust": aggregate_trust,
        },
        "speed_cm_s": selected["decoded"]["speed_cm_s"],
        "primary_speed_source": "GLOBAL_POSITION_INT.vx/vy",
        "primary_rounding": selected["decoded"]["rounding"],
        "observed_time": {
            "value": selected["decoded"]["time_boot_ms"],
            "unit": "ms_since_autopilot_boot",
            "trustworthy_time": False,
        },
        "received_at_ms": selected["received_at_ms"],
        "receiver_age_ms": age_ms,
        "vfr_hud_diagnostic_speed_cm_s": diagnostic_vfr_speed,
        "claim_eligibility": "NOT_EVALUATED",
        "publication": "NOT_PERFORMED",
    }


def evaluate_capture(capture: Any) -> dict[str, Any]:
    try:
        return normalize_capture(capture)
    except NormalizationError as exc:
        return {
            "labels": list(LABELS),
            "status": "REJECTED",
            "reason_code": exc.code,
            "reason": exc.message,
            "assurance_id": "A0_SYNTHETIC",
            "claim_eligibility": "NOT_EVALUATED",
            "publication": "NOT_PERFORMED",
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "capture_file",
        nargs="?",
        default=str(Path(__file__).with_name("fixtures.json")),
        help="deterministic synthetic capture fixture JSON",
    )
    args = parser.parse_args()
    fixture_path = Path(args.capture_file)
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    if not isinstance(fixture, dict):
        raise SystemExit("fixtures must be an object containing a captures array")
    captures = fixture.get("captures")
    if not isinstance(captures, list):
        raise SystemExit("fixtures must contain a captures array")

    report = {
        "labels": list(LABELS),
        "fixture_file": fixture_path.name,
        "results": [
            {
                "name": (
                    item.get("name", "<unnamed>") if isinstance(item, dict) else "<unnamed>"
                ),
                "result": evaluate_capture(item),
            }
            for item in captures
        ],
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
