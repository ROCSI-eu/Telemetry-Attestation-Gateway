#!/usr/bin/env python3
"""Tests for the synthetic-only receive/normalize MAVLink experiment."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("mavlink_normalize", HERE / "mavlink_normalize.py")
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)


class FixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = json.loads((HERE / "fixtures.json").read_text(encoding="utf-8"))

    def test_all_fixture_expectations(self) -> None:
        for capture in self.fixture["captures"]:
            with self.subTest(capture=capture["name"]):
                result = mod.evaluate_capture(capture)
                self.assertEqual(result["status"], capture["expected_status"])
                if result["status"] == "NORMALIZED":
                    self.assertEqual(result["speed_cm_s"], capture["expected_speed_cm_s"])
                    self.assertEqual(result["source"]["trust"], capture["expected_trust"])
                    self.assertEqual(result["claim_eligibility"], "NOT_EVALUATED")
                    self.assertFalse(result["observed_time"]["trustworthy_time"])
                    if "expected_vfr_speed_cm_s" in capture:
                        self.assertEqual(
                            result["vfr_hud_diagnostic_speed_cm_s"],
                            capture["expected_vfr_speed_cm_s"],
                        )
                else:
                    self.assertEqual(result["reason_code"], capture["expected_reason_code"])

    def test_capture_metadata_does_not_coerce_strings_or_booleans(self) -> None:
        import copy

        base = next(item for item in self.fixture["captures"] if item["name"] == "unsigned-consistent")

        string_time = copy.deepcopy(base)
        string_time["decision_received_at_ms"] = "2000"
        result = mod.evaluate_capture(string_time)
        self.assertEqual(result["reason_code"], "MALFORMED_CAPTURE")

        boolean_time = copy.deepcopy(base)
        boolean_time["events"][0]["received_at_ms"] = True
        result = mod.evaluate_capture(boolean_time)
        self.assertEqual(result["reason_code"], "MALFORMED_CAPTURE")

        non_string_hex = copy.deepcopy(base)
        non_string_hex["events"][0]["frame_hex"] = 123
        result = mod.evaluate_capture(non_string_hex)
        self.assertEqual(result["reason_code"], "MALFORMED_CAPTURE")

    def test_labels_are_conspicuous(self) -> None:
        for required in (
            "EXPERIMENTAL",
            "SYNTHETIC_ONLY",
            "A0_SYNTHETIC",
            "NOT VALIDATION OR PRODUCTION AUTHORIZATION",
        ):
            self.assertIn(required, mod.LABELS)

    def test_allowlist_is_observation_only(self) -> None:
        self.assertEqual(set(mod.MESSAGE_SPECS), {33, 74})
        source = (HERE / "mavlink_normalize.py").read_text(encoding="utf-8")
        self.assertNotIn("import socket", source)
        self.assertNotIn("sendto(", source)
        self.assertNotIn("COMMAND_LONG", source)
        self.assertNotIn("COMMAND_INT", source)
        self.assertNotIn("SET_MODE", source)


class NormalizationMathTests(unittest.TestCase):
    def test_ceil_sqrt_does_not_understate(self) -> None:
        for value in (0, 1, 2, 15, 16, 17, 25, 2_147_483_648):
            result = mod._ceil_sqrt(value)
            self.assertGreaterEqual(result * result, value)
            if result:
                self.assertLess((result - 1) * (result - 1), value)

    def test_binary32_exact_five_mps(self) -> None:
        self.assertEqual(mod._binary32_to_fraction(bytes.fromhex("0000a040")), Fraction(5, 1))

    def test_binary32_nan_is_rejected(self) -> None:
        with self.assertRaises(mod.NormalizationError) as caught:
            mod._binary32_to_fraction(bytes.fromhex("0000c07f"))
        self.assertEqual(caught.exception.code, "NON_FINITE_GROUNDSPEED")


class ProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        fixture = json.loads((HERE / "fixtures.json").read_text(encoding="utf-8"))
        cls.captures = {item["name"]: item for item in fixture["captures"]}

    def test_known_message_metadata(self) -> None:
        self.assertEqual(mod.MESSAGE_SPECS[33]["crc_extra"], 104)
        self.assertEqual(mod.MESSAGE_SPECS[74]["crc_extra"], 20)
        self.assertEqual(mod.MESSAGE_SPECS[33]["full_payload_len"], 28)
        self.assertEqual(mod.MESSAGE_SPECS[74]["full_payload_len"], 20)

    def test_unsigned_frame_crc_parses(self) -> None:
        event = self.captures["unsigned-consistent"]["events"][0]
        parsed = mod.parse_mavlink2_frame(bytes.fromhex(event["frame_hex"]))
        self.assertEqual(parsed.msg_id, 33)
        self.assertEqual(parsed.trust, mod.TRUST_UNSIGNED)

    def test_signed_frame_verifies(self) -> None:
        capture = self.captures["signed-valid"]
        event = capture["events"][0]
        parsed = mod.parse_mavlink2_frame(
            bytes.fromhex(event["frame_hex"]),
            capture["test_trust_store"],
            {},
        )
        self.assertEqual(parsed.trust, mod.TRUST_SIGNED_VALID)
        self.assertEqual(parsed.signature_link_id, 7)

    def test_mavlink2_zero_truncation_is_zero_padded(self) -> None:
        capture = self.captures["gpi-trailing-zero-truncated"]
        result = mod.normalize_capture(capture)
        self.assertEqual(result["speed_cm_s"], 0)

    def test_mixed_source_fails_closed(self) -> None:
        result = mod.evaluate_capture(self.captures["mixed-source"])
        self.assertEqual(result["reason_code"], "MIXED_SOURCE")

    def test_bad_crc_fails_closed(self) -> None:
        result = mod.evaluate_capture(self.captures["bad-crc"])
        self.assertEqual(result["reason_code"], "BAD_CRC")

    def test_signature_failure_is_not_trust(self) -> None:
        result = mod.evaluate_capture(self.captures["signed-invalid"])
        self.assertEqual(result["reason_code"], "SIGNATURE_INVALID")
        self.assertNotEqual(result.get("source", {}).get("trust"), mod.TRUST_SIGNED_VALID)


if __name__ == "__main__":
    unittest.main(verbosity=2)
