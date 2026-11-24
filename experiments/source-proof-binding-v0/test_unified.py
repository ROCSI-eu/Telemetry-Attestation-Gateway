"""Composition tests with a test double, NOT cryptographic verification."""
import copy
import hashlib
import json
import unittest
from unittest.mock import Mock, patch

import unified
from unified import Unified, BindingRejected
from test_temporal_gate import CONFIG, sample
from binding_reference import authorized_digest


class CompositionTests(unittest.TestCase):
    def setUp(self):
        self.verify = Mock(return_value=True)
        self.proof, self.vk = b"mock-proof-not-cryptographic", b"mock-vk-not-cryptographic"
        pins = patch.multiple(unified, PINNED_PROOF=hashlib.sha256(self.proof).hexdigest(),
                              PINNED_VK=hashlib.sha256(self.vk).hexdigest())
        pins.start()
        self.addCleanup(pins.stop)
        self.session = Unified(verify=self.verify, proof=self.proof, vk=self.vk, **CONFIG)

    def test_authorized_capture_supplies_exact_public_inputs_and_artifacts(self):
        c = sample()
        digest = authorized_digest(c, **CONFIG)
        self.assertEqual(self.session.accept(c), digest)
        encoded, proof, vk = self.verify.call_args.args
        values = [int(x, 16) for x in json.loads(encoded)["public_inputs"]]
        self.assertEqual(values, list(digest) + [500, 1])
        self.assertEqual(hashlib.sha256(proof).hexdigest(), unified.PINNED_PROOF)
        self.assertEqual(hashlib.sha256(vk).hexdigest(), unified.PINNED_VK)

    def test_replay_rejected_before_verifier(self):
        self.session.accept(sample())
        with self.assertRaisesRegex(BindingRejected, "CROSS_CAPTURE_REPLAY"):
            self.session.accept(sample())
        self.verify.assert_called_once()

    def test_revoked_key_rejected_before_verifier(self):
        session = Unified(verify=self.verify, proof=self.proof, vk=self.vk, **{**CONFIG,
            "enrollment": {**CONFIG["enrollment"], "active": False}})
        with self.assertRaisesRegex(BindingRejected, "NOT_ENROLLED_OR_REVOKED"):
            session.accept(sample())
        self.verify.assert_not_called()

    def test_invalid_signature_rejected_before_verifier(self):
        c = sample()
        f = bytearray.fromhex(c["events"][0]["frame_hex"])
        f[-1] ^= 1
        c["events"][0]["frame_hex"] = f.hex()
        with self.assertRaisesRegex(BindingRejected, "SIGNATURE_OR_CAPTURE"):
            self.session.accept(c)
        self.verify.assert_not_called()

    def test_proof_failure_does_not_commit_temporal_state(self):
        self.verify.side_effect = [False, True]
        with self.assertRaisesRegex(BindingRejected, "PROOF_NOT_ACCEPTED"):
            self.session.accept(sample())
        self.session.accept(sample())
        self.assertEqual(self.verify.call_count, 2)

    def test_unrecognized_proof_never_reaches_verifier(self):
        session = Unified(verify=self.verify, proof=b"wrong", vk=self.vk, **CONFIG)
        with self.assertRaisesRegex(BindingRejected, "UNRECOGNIZED_QA_ARTIFACT"):
            session.accept(sample())
        self.verify.assert_not_called()

    def test_changed_observation_changes_inputs_without_new_proof(self):
        c, later = sample(), sample(100002, 1001)
        self.verify.return_value = False
        for item in (c, later):
            with self.assertRaisesRegex(BindingRejected, "PROOF_NOT_ACCEPTED"):
                self.session.accept(item)
        a, b = [call.args for call in self.verify.call_args_list]
        self.assertNotEqual(a[0], b[0])
        self.assertEqual(a[1:], b[1:])


if __name__ == "__main__":
    unittest.main(verbosity=2)
