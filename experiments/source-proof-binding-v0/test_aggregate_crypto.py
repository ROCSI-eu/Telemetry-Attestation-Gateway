"""EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION.
Adapter logic tested with a simulated verifier. NO ZKP PROOF VERIFIED.
"""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from aggregate_crypto import AggregateCrypto, CryptoResult, public_inputs
from aggregate_crypto import EXPECTED_VK_SHA256, local_bb_verify_only
import test_aggregate_interval as aggregate_reference
from test_temporal_gate import CONFIG
from test_interval_coverage import TIME_KEY, MAX_AGE
from trusted_time import receipt_mac, BindingRejected

class CryptoAdapterTests(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root=Path(tmp.name)
        self.file=self.root/"state.json"
        self.clock=Mock(return_value=20000)
        self.verify=Mock(return_value=CryptoResult.VALID)
        self.session=self.open(initialize=True)
        self.start=19600
        self.batch=aggregate_reference.AggregateTests.make_batch(self,stamp=100000,boot=1000,start=self.start)
        self.synthetic_vk=b"X"*3680
        self.synthetic_proof=b"THIS_IS_NOT_A_REAL_PROOF"
    def open(self,**extra):
        return AggregateCrypto(state_dir=self.root,verify_crypto=self.verify,
           time_key=TIME_KEY,decision_clock=self.clock,max_age_ms=MAX_AGE,
           **CONFIG,**extra)
    def receipt(self,c,t):
        return {"ingress_ms":t,"mac":receipt_mac(TIME_KEY,self.session._scope,c,t)}
    def accept(self,batch=None,proof=None,vk=None,session=None):
        return (session or self.session).accept_aggregate(
          self.batch if batch is None else batch,self.start,
          proof=self.synthetic_proof if proof is None else proof,
          vk=self.synthetic_vk if vk is None else vk)
    def assert_unchanged(self,original):
        self.assertEqual(self.file.read_bytes(),original)
        self.assertIsNone(self.session._gate._watermark)
    def test_public_inputs_have_version_two_and_exact_98_elements(self):
        di=tuple(bytes([i])*32 for i in range(3))
        vals=[int(v,16) for v in json.loads(public_inputs(di))["public_inputs"]]
        self.assertEqual(len(vals),98)
        self.assertEqual(vals[-2:],[500,2])
        self.assertNotEqual(EXPECTED_VK_SHA256,hashlib.sha256(b"TAG-interval-mock-vk-not-cryptographic").hexdigest())
    def test_missing_proof_or_record_is_not_proof(self):
        original=self.file.read_bytes()
        for proof in (b"",{"cryptographic_proving":"PASS"},"f93de584",None):
            with self.subTest(proof_type=type(proof).__name__):
                self.assertIs(self.accept(proof=proof),CryptoResult.UNVERIFIABLE)
        self.assert_unchanged(original)
        self.verify.assert_not_called()
    def test_untrusted_vk_is_rejected_without_verifier(self):
        original=self.file.read_bytes()
        self.assertIs(self.accept(),CryptoResult.UNVERIFIABLE)
        self.assert_unchanged(original)
        self.verify.assert_not_called()
    def test_simulated_verifier_callback_controls_atomic_commit(self):
        # A testing-only patched VK digest exercises the commit barrier, NOT crypto.
        original=self.file.read_bytes()
        expected=hashlib.sha256(self.synthetic_vk).hexdigest()
        def oracle(encoded,proof,vk):
            self.assertEqual(original,self.file.read_bytes())
            vals=[int(x,16) for x in json.loads(encoded)["public_inputs"]]
            self.assertEqual(len(vals),98)
            self.assertEqual(vals[-2:],[500,2])
            self.assertEqual(proof,self.synthetic_proof)
            self.assertEqual(vk,self.synthetic_vk)
            return CryptoResult.VALID
        self.verify.side_effect=oracle
        with patch("aggregate_crypto.EXPECTED_VK_SHA256",expected), patch.object(self.session,"_write",wraps=self.session._write) as commit:
            self.assertIs(self.accept(),CryptoResult.VALID)
            commit.assert_called_once()
        self.assertEqual(self.open()._read(),(100005,1200))
    def test_invalid_unavailable_and_boolean_true_do_not_commit(self):
        expected=hashlib.sha256(self.synthetic_vk).hexdigest()
        original=self.file.read_bytes()
        with patch("aggregate_crypto.EXPECTED_VK_SHA256",expected):
            for result in (CryptoResult.INVALID,CryptoResult.UNVERIFIABLE,True,None):
                self.verify.reset_mock(side_effect=True,return_value=True)
                self.verify.return_value=result
                actual=self.accept()
                self.assertIs(actual,CryptoResult.INVALID if result is CryptoResult.INVALID else CryptoResult.UNVERIFIABLE)
                self.assert_unchanged(original)
            self.verify.side_effect=RuntimeError("offline verifier unavailable")
            self.assertIs(self.accept(),CryptoResult.UNVERIFIABLE)
            self.assert_unchanged(original)
    def test_invalid_interval_rejected_before_crypto_and_no_commit(self):
        expected=hashlib.sha256(self.synthetic_vk).hexdigest()
        original=self.file.read_bytes()
        with patch("aggregate_crypto.EXPECTED_VK_SHA256",expected):
            with self.assertRaisesRegex(BindingRejected,"INCOMPLETE_INTERVAL"):
                self.accept(batch=self.batch[:2])
        self.assert_unchanged(original)
        self.verify.assert_not_called()
    def test_lock_and_pre_replace_write_failure_do_not_advance(self):
        expected=hashlib.sha256(self.synthetic_vk).hexdigest()
        original=self.file.read_bytes()
        with patch("aggregate_crypto.EXPECTED_VK_SHA256",expected):
            with self.session._locked():
                with self.assertRaisesRegex(BindingRejected,"DIRECTORY_UNAVAILABLE_OR_BUSY"):
                    self.accept()
            self.assert_unchanged(original)
            with patch("persistent_unified.os.replace",side_effect=OSError):
                with self.assertRaisesRegex(BindingRejected,"STATE_COMMIT_FAILED"):
                    self.accept()
            self.assert_unchanged(original)
    def test_separate_context_rejects_mock_state(self):
        expected=hashlib.sha256(self.synthetic_vk).hexdigest()
        with patch("aggregate_crypto.EXPECTED_VK_SHA256",expected):
            self.verify.return_value=CryptoResult.VALID
            self.assertIs(self.accept(),CryptoResult.VALID)
        # Mock variant cannot consume the crypto-specific state context.
        from aggregate_interval import AggregateInterval
        with self.assertRaisesRegex(BindingRejected,"STATE_MISSING_CORRUPT_OR_INCOMPATIBLE"):
            AggregateInterval(state_dir=self.root,verify_mock=Mock(),
                time_key=TIME_KEY,decision_clock=self.clock,max_age_ms=MAX_AGE,**CONFIG)
    def test_real_verifier_adapter_is_fail_closed_type(self):
        # Interface only; no bb invocation and no proof.
        self.assertTrue(callable(local_bb_verify_only("/not-executed/bb","/not-executed/crs")))
if __name__=="__main__":
    unittest.main()
