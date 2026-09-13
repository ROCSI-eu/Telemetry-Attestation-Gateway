#!/usr/bin/env python3
"""Experimental deterministic encoding spike for a bounded-speed claim.

EXPERIMENTAL
SYNTHETIC_ONLY
NOT VALIDATION OR PRODUCTION AUTHORIZATION
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

LABELS = (
    "EXPERIMENTAL",
    "SYNTHETIC_ONLY",
    "NOT VALIDATION OR PRODUCTION AUTHORIZATION",
)

SCHEMA_VERSION = 0
DOMAIN = "tag.bounded-speed.v0"
STATEMENT = "speed_cm_s<=maximum_speed_cm_s"
ASSURANCE_ID = "A0_SYNTHETIC"

UINT8_MAX = (1 << 8) - 1
UINT32_MAX = (1 << 32) - 1

PUBLIC_KEYS = {
    1: "version",
    2: "domain",
    3: "maximum_speed_cm_s",
    4: "statement",
    5: "assurance_id",
}
EXPECTED_PUBLIC_KEY_SET = frozenset(PUBLIC_KEYS)

CONTEXT_PREFIX = b"TAG-PUBLIC-INPUT-CONTEXT\x00"


class EncodingError(ValueError):
    """Raised when an experimental artifact is malformed or non-canonical."""


def _validate_uint(name: str, value: Any, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise EncodingError(f"{name} must be an integer")
    if not 0 <= value <= maximum:
        raise EncodingError(f"{name} must be in [0, {maximum}]")
    return value


def _encode_head(major: int, value: int) -> bytes:
    if value < 0:
        raise EncodingError("negative CBOR values are not supported by this spike")
    if value < 24:
        return bytes([(major << 5) | value])
    if value <= 0xFF:
        return bytes([(major << 5) | 24, value])
    if value <= 0xFFFF:
        return bytes([(major << 5) | 25]) + value.to_bytes(2, "big")
    if value <= 0xFFFFFFFF:
        return bytes([(major << 5) | 26]) + value.to_bytes(4, "big")
    if value <= 0xFFFFFFFFFFFFFFFF:
        return bytes([(major << 5) | 27]) + value.to_bytes(8, "big")
    raise EncodingError("CBOR integer exceeds uint64")


def _encode_value(value: Any) -> bytes:
    if isinstance(value, bool):
        raise EncodingError("boolean values are not supported by this spike")
    if isinstance(value, int):
        return _encode_head(0, value)
    if isinstance(value, str):
        encoded = value.encode("utf-8")
        return _encode_head(3, len(encoded)) + encoded
    if isinstance(value, dict):
        encoded_items: list[tuple[bytes, bytes]] = []
        for key, item in value.items():
            if isinstance(key, bool) or not isinstance(key, int) or key < 0:
                raise EncodingError("map keys must be non-negative integers")
            encoded_items.append((_encode_value(key), _encode_value(item)))
        encoded_items.sort(key=lambda item: (len(item[0]), item[0]))
        return _encode_head(5, len(encoded_items)) + b"".join(
            key + item for key, item in encoded_items
        )
    raise EncodingError(f"unsupported value type: {type(value).__name__}")


def _read_argument(data: bytes, offset: int, additional: int) -> tuple[int, int]:
    if additional < 24:
        return additional, offset
    widths = {24: 1, 25: 2, 26: 4, 27: 8}
    if additional not in widths:
        raise EncodingError("indefinite or reserved CBOR lengths are not supported")
    width = widths[additional]
    end = offset + width
    if end > len(data):
        raise EncodingError("truncated CBOR argument")
    value = int.from_bytes(data[offset:end], "big")
    minimums = {24: 24, 25: 0x100, 26: 0x10000, 27: 0x100000000}
    if value < minimums[additional]:
        raise EncodingError("non-canonical CBOR integer/length encoding")
    return value, end


def _decode_value(data: bytes, offset: int = 0) -> tuple[Any, int]:
    if offset >= len(data):
        raise EncodingError("truncated CBOR value")
    initial = data[offset]
    offset += 1
    major, additional = initial >> 5, initial & 0x1F
    argument, offset = _read_argument(data, offset, additional)

    if major == 0:
        return argument, offset

    if major == 3:
        end = offset + argument
        if end > len(data):
            raise EncodingError("truncated CBOR text string")
        try:
            return data[offset:end].decode("utf-8"), end
        except UnicodeDecodeError as exc:
            raise EncodingError("invalid UTF-8 text string") from exc

    if major == 5:
        result: dict[int, Any] = {}
        previous_order_key: tuple[int, bytes] | None = None
        for _ in range(argument):
            key_start = offset
            key, offset = _decode_value(data, offset)
            key_bytes = data[key_start:offset]
            if isinstance(key, bool) or not isinstance(key, int):
                raise EncodingError("map keys must be non-negative integers")
            order_key = (len(key_bytes), key_bytes)
            if previous_order_key is not None and order_key <= previous_order_key:
                raise EncodingError("map keys are duplicated or not canonically ordered")
            previous_order_key = order_key
            if key in result:
                raise EncodingError("duplicate map key")
            value, offset = _decode_value(data, offset)
            result[key] = value
        return result, offset

    raise EncodingError(f"unsupported CBOR major type {major}")


def encode_public_artifact(maximum_speed_cm_s: int) -> bytes:
    """Encode the provisional public artifact using deterministic CBOR."""
    maximum_speed_cm_s = _validate_uint(
        "maximum_speed_cm_s", maximum_speed_cm_s, UINT32_MAX
    )
    artifact = {
        1: SCHEMA_VERSION,
        2: DOMAIN,
        3: maximum_speed_cm_s,
        4: STATEMENT,
        5: ASSURANCE_ID,
    }
    return _encode_value(artifact)


def decode_public_artifact(data: bytes) -> dict[str, Any]:
    """Strictly decode and validate the provisional public artifact."""
    decoded, offset = _decode_value(data)
    if offset != len(data):
        raise EncodingError("trailing bytes after public artifact")
    if not isinstance(decoded, dict):
        raise EncodingError("public artifact must be a CBOR map")
    if frozenset(decoded) != EXPECTED_PUBLIC_KEY_SET:
        unknown = sorted(set(decoded) - EXPECTED_PUBLIC_KEY_SET)
        missing = sorted(EXPECTED_PUBLIC_KEY_SET - set(decoded))
        raise EncodingError(f"unexpected public fields; unknown={unknown}, missing={missing}")

    version = _validate_uint("version", decoded[1], UINT8_MAX)
    maximum_speed_cm_s = _validate_uint(
        "maximum_speed_cm_s", decoded[3], UINT32_MAX
    )
    if version != SCHEMA_VERSION:
        raise EncodingError(f"unsupported schema version {version}")
    if decoded[2] != DOMAIN:
        raise EncodingError("unexpected domain")
    if decoded[4] != STATEMENT:
        raise EncodingError("unexpected statement")
    if decoded[5] != ASSURANCE_ID:
        raise EncodingError("unexpected assurance_id")

    canonical = encode_public_artifact(maximum_speed_cm_s)
    if canonical != data:
        raise EncodingError("public artifact is not byte-canonical")

    return {
        "version": version,
        "domain": decoded[2],
        "maximum_speed_cm_s": maximum_speed_cm_s,
        "statement": decoded[4],
        "assurance_id": decoded[5],
    }


def reconstruct_public_inputs(data: bytes) -> tuple[tuple[str, Any], ...]:
    """Reconstruct a proof-system-neutral ordered public-input vector.

    The digest is deliberately kept as bytes/hex at this layer. Mapping it into a
    proof-system field is deferred to the proof benchmark instead of being hidden
    in this format spike.
    """
    artifact = decode_public_artifact(data)
    context_preimage = (
        CONTEXT_PREFIX
        + artifact["domain"].encode("utf-8")
        + b"\x00"
        + artifact["statement"].encode("utf-8")
        + b"\x00"
        + artifact["assurance_id"].encode("utf-8")
    )
    context_digest = hashlib.sha256(context_preimage).hexdigest()
    return (
        ("version", artifact["version"]),
        ("maximum_speed_cm_s", artifact["maximum_speed_cm_s"]),
        ("context_sha256", context_digest),
    )


def evaluate_predicate(speed_cm_s: int, maximum_speed_cm_s: int) -> str:
    """Evaluate only the experimental integer predicate.

    This is not a proof and is not evidence of telemetry truth.
    """
    speed_cm_s = _validate_uint("speed_cm_s", speed_cm_s, UINT32_MAX)
    maximum_speed_cm_s = _validate_uint(
        "maximum_speed_cm_s", maximum_speed_cm_s, UINT32_MAX
    )
    return "satisfied" if speed_cm_s <= maximum_speed_cm_s else "not_satisfied"


def load_fixture_cases(path: Path) -> list[dict[str, Any]]:
    document = json.loads(path.read_text(encoding="utf-8"))
    if document.get("labels") != list(LABELS):
        raise EncodingError("fixture labels do not match the required experiment labels")
    cases = document.get("cases")
    if not isinstance(cases, list) or not cases:
        raise EncodingError("fixture document must contain non-empty cases")
    return cases


def fixture_report(path: Path) -> list[dict[str, Any]]:
    report: list[dict[str, Any]] = []
    for case in load_fixture_cases(path):
        speed = _validate_uint("speed_cm_s", case["speed_cm_s"], UINT32_MAX)
        maximum = _validate_uint(
            "maximum_speed_cm_s", case["maximum_speed_cm_s"], UINT32_MAX
        )
        expected = case["expected"]
        actual = evaluate_predicate(speed, maximum)
        if actual != expected:
            raise EncodingError(
                f"fixture {case.get('name', '<unnamed>')} expected {expected}, got {actual}"
            )
        encoded = encode_public_artifact(maximum)
        report.append(
            {
                "name": case["name"],
                "expected": expected,
                "public_artifact_cbor_hex": encoded.hex(),
                "public_inputs": dict(reconstruct_public_inputs(encoded)),
            }
        )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "fixtures",
        nargs="?",
        type=Path,
        default=Path(__file__).with_name("fixtures.json"),
        help="synthetic fixture JSON (default: fixtures.json next to this script)",
    )
    args = parser.parse_args()

    print(" | ".join(LABELS))
    print("A0_SYNTHETIC — predicate evaluation only; no proof generated or verified")
    print(json.dumps(fixture_report(args.fixtures), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
