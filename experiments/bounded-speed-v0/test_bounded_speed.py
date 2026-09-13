#!/usr/bin/env python3
"""Tests for the bounded-speed deterministic encoding spike."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("bounded_speed.py")
SPEC = importlib.util.spec_from_file_location("bounded_speed", MODULE_PATH)
assert SPEC and SPEC.loader
bounded_speed = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bounded_speed)


class BoundedSpeedSpikeTests(unittest.TestCase):
    def test_predicate_below_equal_above(self) -> None:
        self.assertEqual(bounded_speed.evaluate_predicate(499, 500), "satisfied")
        self.assertEqual(bounded_speed.evaluate_predicate(500, 500), "satisfied")
        self.assertEqual(bounded_speed.evaluate_predicate(501, 500), "not_satisfied")

    def test_rejects_non_integer_and_out_of_range_values(self) -> None:
        for value in (-1, bounded_speed.UINT32_MAX + 1, 1.5, True):
            with self.subTest(value=value):
                with self.assertRaises(bounded_speed.EncodingError):
                    bounded_speed.evaluate_predicate(value, 500)

    def test_public_artifact_is_byte_stable(self) -> None:
        first = bounded_speed.encode_public_artifact(500)
        second = bounded_speed.encode_public_artifact(500)
        self.assertEqual(first, second)
        decoded = bounded_speed.decode_public_artifact(first)
        self.assertEqual(decoded["maximum_speed_cm_s"], 500)

    def test_public_input_order_is_reconstructed(self) -> None:
        encoded = bounded_speed.encode_public_artifact(500)
        public_inputs = bounded_speed.reconstruct_public_inputs(encoded)
        self.assertEqual(
            [name for name, _ in public_inputs],
            ["version", "maximum_speed_cm_s", "context_sha256"],
        )
        self.assertEqual(public_inputs[1], ("maximum_speed_cm_s", 500))
        self.assertEqual(len(public_inputs[2][1]), 64)

    def test_out_of_range_public_limit_is_rejected(self) -> None:
        public = {
            1: bounded_speed.SCHEMA_VERSION,
            2: bounded_speed.DOMAIN,
            3: bounded_speed.UINT32_MAX + 1,
            4: bounded_speed.STATEMENT,
            5: bounded_speed.ASSURANCE_ID,
        }
        encoded = bounded_speed._encode_value(public)
        with self.assertRaisesRegex(bounded_speed.EncodingError, "maximum_speed_cm_s"):
            bounded_speed.decode_public_artifact(encoded)

    def test_unknown_field_is_rejected(self) -> None:
        public = {
            1: bounded_speed.SCHEMA_VERSION,
            2: bounded_speed.DOMAIN,
            3: 500,
            4: bounded_speed.STATEMENT,
            5: bounded_speed.ASSURANCE_ID,
            6: "unexpected",
        }
        encoded = bounded_speed._encode_value(public)
        with self.assertRaisesRegex(bounded_speed.EncodingError, "unexpected public fields"):
            bounded_speed.decode_public_artifact(encoded)

    def test_mutated_domain_is_rejected(self) -> None:
        encoded = bytearray(bounded_speed.encode_public_artifact(500))
        needle = bounded_speed.DOMAIN.encode("utf-8")
        start = bytes(encoded).index(needle)
        encoded[start] ^= 0x01
        with self.assertRaisesRegex(bounded_speed.EncodingError, "unexpected domain"):
            bounded_speed.decode_public_artifact(bytes(encoded))

    def test_trailing_bytes_are_rejected(self) -> None:
        encoded = bounded_speed.encode_public_artifact(500) + b"\x00"
        with self.assertRaisesRegex(bounded_speed.EncodingError, "trailing bytes"):
            bounded_speed.decode_public_artifact(encoded)

    def test_noncanonical_integer_encoding_is_rejected(self) -> None:
        # Start from a canonical map and replace version 0 (0x00) with the
        # non-canonical uint8 representation 0x18 0x00.
        encoded = bounded_speed.encode_public_artifact(500)
        self.assertTrue(encoded.startswith(b"\xa5\x01\x00"))
        noncanonical = encoded[:2] + b"\x18\x00" + encoded[3:]
        with self.assertRaisesRegex(bounded_speed.EncodingError, "non-canonical"):
            bounded_speed.decode_public_artifact(noncanonical)

    def test_duplicate_or_noncanonical_key_order_is_rejected(self) -> None:
        # Canonical five-entry map, then declare six entries and append a second
        # key 5. The decoder rejects it because the key order is not strictly
        # increasing (and therefore cannot be deterministic CBOR).
        encoded = bounded_speed.encode_public_artifact(500)
        self.assertEqual(encoded[0], 0xA5)
        duplicate = bytes([0xA6]) + encoded[1:] + bounded_speed._encode_value(5) + bounded_speed._encode_value("A0_SYNTHETIC")
        with self.assertRaisesRegex(
            bounded_speed.EncodingError, "duplicated or not canonically ordered"
        ):
            bounded_speed.decode_public_artifact(duplicate)

    def test_float_cbor_is_not_supported(self) -> None:
        with self.assertRaisesRegex(bounded_speed.EncodingError, "unsupported CBOR major type 7"):
            bounded_speed._decode_value(b"\xfa\x3f\x80\x00\x00")

    def test_fixture_file_is_self_consistent(self) -> None:
        report = bounded_speed.fixture_report(Path(__file__).with_name("fixtures.json"))
        self.assertEqual([item["name"] for item in report], ["below_limit", "at_limit", "above_limit"])


if __name__ == "__main__":
    unittest.main()
