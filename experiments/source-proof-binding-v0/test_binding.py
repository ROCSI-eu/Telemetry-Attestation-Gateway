#!/usr/bin/env python3
"""Offline regression tests; no prover, SITL, network or real keys."""
import copy
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import binding_reference as binding

CASES = {c["name"]: c for c in json.loads(
    (Path(__file__).resolve().parents[1] / "mavlink-normalization-v0/fixtures.json").read_text()
)["captures"]}
KEY_A = bytes(range(32)).hex()  # Public synthetic fixture key, not capture-provisioned.
KEY_B = bytes(reversed(range(32))).hex()
ALIAS = "qa-synthetic-source"
POLICY = {"slot": "1:1:7", "alias": ALIAS, "active": True,
          "key_fingerprint": "630dcd2966c4336691125448bbb25b4ff412a49c732db2c8abc1b8581bd710dd"}


class AuthorizedBindingTests(unittest.TestCase):
    def digest(self, capture=None, key=KEY_A, policy=POLICY, alias=ALIAS):
        return binding.authorized_digest(
            CASES["signed-valid"] if capture is None else capture,
            verifier_key_hex=key, enrollment=policy, requested_alias=alias)

    def assert_blocked(self, reason, **kwargs):
        with patch.object(binding.hashlib, "blake2s") as digest:
            with self.assertRaisesRegex(binding.BindingRejected, reason):
                self.digest(**kwargs)
            digest.assert_not_called()

    def test_registered_key_preserves_existing_binding(self):
        frames = [bytes.fromhex(e["frame_hex"]) for e in CASES["signed-valid"]["events"]]
        primary = [f for f in frames if int.from_bytes(f[7:10], "little") == 33][-1]
        self.assertEqual(len(primary), 53)
        self.assertEqual(self.digest(), hashlib.blake2s(primary).digest())

    def test_capture_cannot_provision_authority(self):
        self.assert_blocked("REJECTED_NOT_ENROLLED_OR_REVOKED", policy=None)

    def test_revoked_or_malformed_active_flag(self):
        for value in (False, "false", 1, None):
            with self.subTest(value=value):
                self.assert_blocked("REJECTED_NOT_ENROLLED_OR_REVOKED",
                                    policy={**POLICY, "active": value})

    def test_alias_must_match(self):
        self.assert_blocked("REJECTED_SOURCE_ALIAS", alias="other-source")

    def test_slot_must_match(self):
        self.assert_blocked("REJECTED_SOURCE_SLOT", policy={**POLICY, "slot": "1:1:8"})

    def test_unknown_key(self):
        self.assert_blocked("REJECTED_KEY_FINGERPRINT", key=KEY_B)

    def test_invalid_or_unsigned_capture(self):
        for name in ("signed-invalid", "unsigned-consistent", "signed-timestamp-regression"):
            with self.subTest(name=name):
                self.assert_blocked("REJECTED_SIGNATURE_OR_CAPTURE", capture=CASES[name])

    def test_valid_signature_under_unauthorized_key(self):
        capture = copy.deepcopy(CASES["signed-valid"])
        capture["test_trust_store"] = {POLICY["slot"]: KEY_A}
        result = binding.parser.evaluate_capture(capture)
        self.assertEqual(result["status"], "NORMALIZED")
        self.assertEqual(result["source"]["trust"], "SIGNED_VALID")
        policy_b = {**POLICY, "key_fingerprint": hashlib.sha256(bytes.fromhex(KEY_B)).hexdigest()}
        self.assert_blocked("REJECTED_SIGNATURE_OR_CAPTURE", capture=capture,
                            key=KEY_B, policy=policy_b)
        self.assert_blocked("REJECTED_KEY_FINGERPRINT", capture=capture,
                            key=KEY_A, policy=policy_b)

    def test_capture_cannot_override_verifier_key(self):
        capture = copy.deepcopy(CASES["signed-valid"])
        capture["test_trust_store"] = {POLICY["slot"]: KEY_B}
        self.assertEqual(self.digest(capture=capture), self.digest())
        self.assertEqual(capture["test_trust_store"], {POLICY["slot"]: KEY_B})


if __name__ == "__main__":
    unittest.main(verbosity=2)
