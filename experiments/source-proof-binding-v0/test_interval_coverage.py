"""EXPERIMENTAL | SYNTHETIC_ONLY | A0_SYNTHETIC | NOT VALIDATION OR PRODUCTION AUTHORIZATION.
Synthetic interval admission only; existing cryptographic verification is mocked.
"""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock
from trusted_time import TrustedTimeUnified, receipt_mac, BindingRejected
from interval_coverage import accept_interval, PERIOD, COUNT, TOLERANCE
from test_persistent_unified import ARTIFACTS, CONFIG, mock_pins, sample
from binding_reference import authorized_digest
from unified import public_inputs

TIME_KEY = bytes(reversed(range(32)))
MAX_AGE = 1000

class IntervalTests(unittest.TestCase):
    def setUp(self):
        pins=mock_pins(); pins.start(); self.addCleanup(pins.stop)
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name); self.file=self.root/"state.json"
        self.verify=Mock(return_value=True); self.clock=Mock(return_value=20000)
        self.session=self.open(initialize=True)
        self.start=19600
    def open(self, **extra):
        return TrustedTimeUnified(state_dir=self.root, verify=self.verify, time_key=TIME_KEY,
                    decision_clock=self.clock, max_age_ms=MAX_AGE, **ARTIFACTS, **CONFIG, **extra)
    def receipt(self,c,t):
        return {"ingress_ms":t,"mac":receipt_mac(TIME_KEY,self.session._scope,c,t)}
    def batch(self,start=None,stamp=100000,boot=1000,offset=0):
        start=self.start if start is None else start
        return [(c,self.receipt(c,start+i*PERIOD+PERIOD//2+offset))
                for i in range(COUNT) for c in [sample(stamp+i*2,boot+i*PERIOD)]]
    def reject(self,b,reason,start=None,session=None):
        before=self.file.read_bytes()
        with self.assertRaisesRegex(BindingRejected,reason):
            accept_interval(session or self.session,b,self.start if start is None else start)
        self.assertEqual(self.file.read_bytes(),before)
    def test_complete_and_bound_inputs(self):
        b=self.batch()
        result=accept_interval(self.session,b,self.start)
        self.assertEqual(result,tuple(authorized_digest(c,**CONFIG) for c,_ in b))
        self.assertEqual([x.args[0] for x in self.verify.call_args_list],
                         [public_inputs(d) for d in result])
        self.assertEqual(self.open()._read(),(100005,1200))
    def test_missing_middle_empty_and_extra(self):
        b=self.batch()
        for v in ([b[0],b[2]],[],b+[b[2]]):
            self.reject(v,"INCOMPLETE_INTERVAL")
    def test_gap_even_with_expected_count(self):
        b=self.batch(); c=b[1][0]; b[1]=(c,self.receipt(c,self.start+180))
        self.reject(b,"SLOT_MISMATCH")
    def test_duplicate_and_reused_with_new_receipt(self):
        b=self.batch()
        self.reject([b[0],b[0],b[2]],"SLOT_MISMATCH")
        c=b[0][0]; b[1]=(c,self.receipt(c,self.start+150))
        self.reject(b,"CROSS_CAPTURE_REPLAY")
    def test_out_of_order_ingress(self):
        b=self.batch(); self.reject([b[1],b[0],b[2]],"SLOT_MISMATCH")
    def test_signed_time_regression(self):
        b=self.batch(); c=sample(99998,1100); b[1]=(c,self.receipt(c,self.start+150))
        self.reject(b,"CROSS_CAPTURE_REPLAY")
    def test_equal_boot_with_fresh_signature(self):
        b=self.batch(); c=sample(100002,1000); b[1]=(c,self.receipt(c,self.start+150))
        self.reject(b,"PRIMARY_COUNT_OR_BOOT_ORDER")
    def test_modified_capture_and_invalid_source_signature(self):
        b=self.batch(); c=copy.deepcopy(b[1][0])
        frame=bytearray.fromhex(c["events"][-1]["frame_hex"]); frame[-1]^=1
        c["events"][-1]["frame_hex"]=frame.hex()
        self.reject([b[0],(c,b[1][1]),b[2]],"TIME_REFERENCE_NOT_AUTHENTIC")
        self.reject([b[0],(c,self.receipt(c,self.start+150)),b[2]],"REJECTED_SIGNATURE_OR_CAPTURE")
    def test_invalid_authority(self):
        b=self.batch(); r=dict(b[1][1],mac="0"*64)
        self.reject([b[0],(b[1][0],r),b[2]],"TIME_REFERENCE_NOT_AUTHENTIC")
    def test_expired_and_not_closed(self):
        b=self.batch(); self.clock.return_value=20650
        self.reject(b,"TIME_REFERENCE_STALE")
        self.clock.return_value=self.start+299
        self.reject(b,"INTERVAL_NOT_CLOSED")
    def test_tolerance_edges(self):
        self.reject(self.batch(offset=11),"SLOT_MISMATCH")
        self.reject(self.batch(offset=-11),"SLOT_MISMATCH")
        accept_interval(self.session,self.batch(offset=-10),self.start)
        nxt=self.start+300; self.clock.return_value=20200
        accept_interval(self.session,self.batch(nxt,100006,1300,10),nxt)
    def test_malformed_pair_and_unavailable_decision_clock(self):
        b=self.batch()
        self.reject([b[0], None, b[2]],"INVALID_INTERVAL_PAIR")
        self.reject([b[0], (b[1][0],), b[2]],"INVALID_INTERVAL_PAIR")
        self.clock.return_value=True
        self.reject(b,"DECISION_CLOCK_UNAVAILABLE")
        self.clock.side_effect=RuntimeError("test unavailable")
        self.reject(b,"DECISION_CLOCK_UNAVAILABLE")
        self.verify.assert_not_called()

    def test_atomic_rejection_then_reopen_and_recover(self):
        accept_interval(self.session,self.batch(),self.start)
        nxt=self.start+300; self.clock.return_value=20200
        b=self.batch(nxt,100006,1300)
        bad=copy.deepcopy(b); bad[2][1]["mac"]="0"*64
        opened=self.open()
        self.reject(bad,"TIME_REFERENCE_NOT_AUTHENTIC",nxt,opened)
        self.verify.side_effect=[True,True,False]
        self.reject(b,"PROOF_NOT_ACCEPTED",nxt,self.open())
        self.verify.side_effect=None
        accept_interval(self.open(),b,nxt)
        self.reject(b,"CROSS_CAPTURE_REPLAY",nxt,self.open())

if __name__ == "__main__":
    print(__doc__,flush=True)
    unittest.main(verbosity=2)

