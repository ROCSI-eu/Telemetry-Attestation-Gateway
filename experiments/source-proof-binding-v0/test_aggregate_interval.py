"""EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION.
Mock-only integration tests; no cryptographic proof.
"""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from test_temporal_gate import sample, CONFIG
from test_interval_coverage import TIME_KEY, MAX_AGE
from trusted_time import receipt_mac, TrustedTimeUnified, BindingRejected
from binding_reference import authorized_digest
from aggregate_interval import AggregateInterval, MockResult, MOCK_VK
from test_persistent_unified import ARTIFACTS

class AggregateTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.file = self.root / "state.json"
        self.clock = Mock(return_value=20000)
        self.verify = Mock()
        self.session = self.open(initialize=True)
        self.start = 19600
        self.batch = self.make_batch()
        self.token = b"mock-token-not-proof"
        self.expected = self.inputs(self.batch)
        self.verify.side_effect = self.oracle

    def open(self, **extra):
        return AggregateInterval(state_dir=self.root, verify_mock=self.verify,
             time_key=TIME_KEY, decision_clock=self.clock, max_age_ms=MAX_AGE,
             **CONFIG, **extra)

    def receipt(self,c,t):
        return {"ingress_ms":t,"mac":receipt_mac(TIME_KEY,self.session._scope,c,t)}

    def make_batch(self, stamp=100000, boot=1000, start=19600):
        return [(c,self.receipt(c,start+50+i*100)) for i in range(3)
                for c in [sample(stamp+i*2,boot+i*100)]]

    def inputs(self,batch):
        return [v for c,_ in batch for v in authorized_digest(c,**CONFIG)]+[500,1]

    def oracle(self,encoded,token,vk):
        vals=[int(x,16) for x in json.loads(encoded)["public_inputs"]]
        return (MockResult.VALID if vals==self.expected and token==self.token and vk==MOCK_VK
                else MockResult.INVALID)

    def accept(self,batch=None,session=None,start=None,token=None):
        return (session or self.session).accept_aggregate(
            self.batch if batch is None else batch,self.start if start is None else start,
            mock_token=self.token if token is None else token)

    def reject(self,batch,reason):
        before=self.file.read_bytes()
        with self.assertRaisesRegex(BindingRejected,reason):
            self.accept(batch)
        self.assertEqual(before,self.file.read_bytes())
        self.verify.assert_not_called()

    def test_exact_inputs_and_one_commit(self):
        old=self.file.read_bytes()
        def verify(*args):
            self.assertEqual(self.file.read_bytes(),old)
            self.assertIsNone(self.session._gate._watermark)
            return self.oracle(*args)
        self.verify.side_effect=verify
        with patch.object(self.session,"_write",wraps=self.session._write) as write:
            self.assertIs(self.accept(),MockResult.VALID)
            write.assert_called_once()
        self.verify.assert_called_once()
        vals=json.loads(self.verify.call_args.args[0])["public_inputs"]
        self.assertEqual(len(vals),98)
        self.assertEqual([int(v,16) for v in vals],self.expected)
        self.assertTrue(all(len(v)==66 for v in vals))
        self.assertEqual(self.open()._read(),(100005,1200))

    def test_missing(self):
        self.reject(self.batch[:2],"INCOMPLETE_INTERVAL")

    def test_duplicate(self):
        c=self.batch[0][0]
        self.reject([self.batch[0],(c,self.receipt(c,self.start+150)),self.batch[2]],
                    "CROSS_CAPTURE_REPLAY")

    def test_reordered(self):
        self.reject([self.batch[1],self.batch[0],self.batch[2]],"SLOT_MISMATCH")

    def test_modified_receipt_and_source(self):
        c=copy.deepcopy(self.batch[1][0])
        frame=bytearray.fromhex(c["events"][-1]["frame_hex"])
        frame[-1]^=1
        c["events"][-1]["frame_hex"]=frame.hex()
        self.reject([self.batch[0],(c,self.batch[1][1]),self.batch[2]],"TIME_REFERENCE_NOT_AUTHENTIC")
        self.reject([self.batch[0],(c,self.receipt(c,self.start+150)),self.batch[2]],"SIGNATURE_OR_CAPTURE")

    def test_other_authenticated_sequence_same_token(self):
        before=self.file.read_bytes()
        other=self.make_batch(stamp=110000,boot=2000)
        self.assertIs(self.accept(other),MockResult.INVALID)
        self.assertEqual(before,self.file.read_bytes())
        self.verify.assert_called_once()
        self.assertIs(self.accept(),MockResult.VALID)

    def test_invalid_token_and_unavailable_verifier(self):
        before=self.file.read_bytes()
        self.assertIs(self.accept(token=b"wrong"),MockResult.INVALID)
        for outcome in (MockResult.UNVERIFIABLE, True, None):
            self.verify.side_effect=None
            self.verify.return_value=outcome
            self.assertIs(self.accept(),MockResult.UNVERIFIABLE)
            self.assertEqual(self.file.read_bytes(),before)
        self.verify.side_effect=RuntimeError("mock unavailable")
        self.assertIs(self.accept(),MockResult.UNVERIFIABLE)
        self.assertEqual(self.file.read_bytes(),before)
        self.assertIsNone(self.open()._read())

    def test_replay_after_reopen(self):
        self.assertIs(self.accept(),MockResult.VALID)
        before=self.file.read_bytes()
        self.verify.reset_mock()
        with self.assertRaisesRegex(BindingRejected,"CROSS_CAPTURE_REPLAY"):
            self.accept(session=self.open())
        self.assertEqual(self.file.read_bytes(),before)
        self.verify.assert_not_called()

    def test_distinct_state_context_no_implicit_reset(self):
        before=self.file.read_bytes()
        with self.assertRaisesRegex(BindingRejected,"STATE_MISSING_CORRUPT_OR_INCOMPATIBLE"):
            TrustedTimeUnified(state_dir=self.root,verify=Mock(),time_key=TIME_KEY,
                decision_clock=self.clock,max_age_ms=MAX_AGE,**CONFIG,**ARTIFACTS)
        with self.assertRaisesRegex(BindingRejected,"STATE_ALREADY_EXISTS"):
            self.open(initialize=True)
        with self.assertRaisesRegex(BindingRejected,"AGGREGATE_ONLY"):
            self.session.accept(self.batch[0][0])
        self.assertEqual(self.file.read_bytes(),before)

    def test_pre_replace_commit_failure(self):
        before=self.file.read_bytes()
        with patch("persistent_unified.os.replace",side_effect=OSError):
            with self.assertRaisesRegex(BindingRejected,"STATE_COMMIT_FAILED"):
                self.accept()
        self.assertEqual(self.file.read_bytes(),before)
        self.assertIsNone(self.session._gate._watermark)
        self.assertEqual(list(self.root.iterdir()),[self.file])
        self.assertIs(self.accept(session=self.open()),MockResult.VALID)

    def test_lock_busy(self):
        before=self.file.read_bytes()
        with self.session._locked():
            with self.assertRaisesRegex(BindingRejected,"DIRECTORY_UNAVAILABLE_OR_BUSY"):
                self.accept()
        self.assertEqual(self.file.read_bytes(),before)
        self.verify.assert_not_called()

if __name__=="__main__":
    unittest.main()
