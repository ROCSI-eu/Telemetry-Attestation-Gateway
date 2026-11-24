"""EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION.
Deterministic signed fixtures, simulated time and recovery authority, mock proof verifier.
"""
import hmac
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

from interval_recovery import RecoverySession, MAX_SEGMENTS
from test_interval_continuity import ANCHOR, WIDTH, PERIOD, options, batch, mock_pins, TIME_KEY
from test_persistent_unified import sample
from trusted_time import BindingRejected, receipt_mac

RECOVERY_KEY = b"R"*32


def open_session(root, clock, verify, **extra):
    return RecoverySession(state_dir=root, anchor=ANCHOR, recovery_key=RECOVERY_KEY,
                           **options(clock, verify), **extra)


def authorize(s):
    with s._locked():
        return hmac.digest(RECOVERY_KEY, s._authorization_message(s._read()), "sha256").hex()


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        pins = mock_pins()
        pins.start()
        self.addCleanup(pins.stop)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.clock = Mock()
        self.verify = Mock(return_value=True)
        self.s = open_session(self.root, self.clock, self.verify, initialize=True)
        with self.s._stage() as stage:
            self.scope = stage._scope
        self.file = self.root / "state.json"

    def start(self, i):
        return ANCHOR+i*WIDTH

    def inputs(self, i, start=None):
        t = self.start(i) if start is None else start
        self.clock.return_value = t+400
        return batch(i, t, self.scope)

    def admit(self, i):
        return self.s.accept_next(self.inputs(i), self.start(i))

    def gap(self):
        self.admit(0)
        self.inputs(2)
        self.s.declare_gap(self.start(2))
        return authorize(self.s)

    def resume(self):
        token = self.gap()
        self.s.recover(self.inputs(2), self.start(2), token)
        return token

    def reject(self, reason, fn, *, no_callback=False):
        before = self.file.read_bytes()
        count = self.verify.call_count
        with self.assertRaisesRegex(BindingRejected, reason):
            fn()
        self.assertEqual(self.file.read_bytes(), before)
        if no_callback:
            self.assertEqual(self.verify.call_count, count)

    def test_contiguous_baseline_and_gap_detection(self):
        self.admit(0)
        self.admit(1)
        b = self.inputs(3)
        self.reject("INTERVAL_GAP", lambda: self.s.accept_next(b, self.start(3)), no_callback=True)
        self.s.declare_gap(self.start(3))
        r = self.s._read()
        self.assertEqual(r["pending"], [self.start(2), self.start(3)])
        self.assertEqual(r["segments"], [[ANCHOR,self.start(2)]])
        self.assertTrue(self.s.covers(ANCHOR,self.start(2)))
        self.assertFalse(self.s.covers(ANCHOR,self.start(3)))

    def test_no_implicit_gap_or_recovery_without_declaration(self):
        self.admit(0)
        b = self.inputs(2)
        self.reject("RECOVERY_TARGET_MISMATCH",
                    lambda: self.s.recover(b,self.start(2),"0"*64), no_callback=True)
        self.reject("NOT_A_FORWARD_GAP", lambda: self.s.declare_gap(self.start(1)))

    def test_pending_blocks_late_fill_and_redeclaration(self):
        self.gap()
        b = self.inputs(1)
        self.reject("RECOVERY_REQUIRED", lambda: self.s.accept_next(b,self.start(1)), no_callback=True)
        self.reject("GAP_DECLARATION_NOT_ALLOWED", lambda: self.s.declare_gap(self.start(3)))

    def test_recovery_authorization_and_target_binding(self):
        token = self.gap()
        b = self.inputs(2)
        self.reject("RECOVERY_NOT_AUTHORIZED", lambda: self.s.recover(b,self.start(2),"0"*64), no_callback=True)
        self.reject("RECOVERY_TARGET_MISMATCH", lambda: self.s.recover(b,self.start(3),token), no_callback=True)
        self.s.recover(b,self.start(2),token)
        self.assertEqual(self.s._read()["segments"], [[ANCHOR,self.start(1)],[self.start(2),self.start(3)]])
        self.assertEqual(self.verify.call_count,6)

    def test_coverage_never_bridges_gap(self):
        self.resume()
        self.admit(3)
        self.assertTrue(self.s.covers(ANCHOR,self.start(1)))
        self.assertTrue(self.s.covers(self.start(2),self.start(4)))
        for a,b in [(ANCHOR,self.start(4)),(self.start(1),self.start(2)),
                    (self.start(1)-1,self.start(2)+1),(self.start(2),self.start(2))]:
            self.assertFalse(self.s.covers(a,b))

    def test_replayed_source_with_fresh_receipts(self):
        token = self.gap()
        b = self.inputs(0,start=self.start(2))
        self.reject("CROSS_CAPTURE_REPLAY_OR_REGRESSION",
                    lambda: self.s.recover(b,self.start(2),token), no_callback=True)
        self.s.recover(self.inputs(2),self.start(2),token)

    def test_boot_regression_with_new_signing_time(self):
        token = self.gap()
        b = self.inputs(2)
        c = sample(200000,999)
        t = self.start(2)+PERIOD//2
        b[0] = (c,{"ingress_ms":t,"mac":receipt_mac(TIME_KEY,self.scope,c,t)})
        self.reject("CROSS_CAPTURE_BOOT_REGRESSION",
                    lambda: self.s.recover(b,self.start(2),token), no_callback=True)

    def test_failed_last_slot_retains_gap_and_watermark(self):
        token = self.gap()
        b = self.inputs(2)
        b[-1][1]["mac"] = "0"*64
        self.reject("TIME_REFERENCE_NOT_AUTHENTIC",lambda: self.s.recover(b,self.start(2),token))
        self.verify.side_effect = [True,True,False]
        self.reject("PROOF_NOT_ACCEPTED",lambda: self.s.recover(self.inputs(2),self.start(2),token))
        self.verify.side_effect = None
        self.s.recover(self.inputs(2),self.start(2),token)

    def test_old_authorization_and_history_across_second_gap(self):
        old = self.resume()
        self.inputs(4)
        self.s.declare_gap(self.start(4))
        b = self.inputs(4)
        self.reject("RECOVERY_NOT_AUTHORIZED",lambda: self.s.recover(b,self.start(4),old),no_callback=True)
        self.s.recover(b,self.start(4),authorize(self.s))
        self.assertEqual(len(self.s._read()["segments"]),3)
        self.assertFalse(self.s.covers(ANCHOR,self.start(5)))

    def test_actual_process_restart_pending_and_resumed(self):
        self.gap()
        code = """
import sys
from unittest.mock import Mock
from test_interval_recovery import open_session,authorize,ANCHOR,WIDTH,batch,mock_pins
with mock_pins():
    s = open_session(sys.argv[1],Mock(return_value=ANCHOR+2*WIDTH+400),Mock(return_value=True))
    assert s._read()["pending"] == [ANCHOR+WIDTH,ANCHOR+2*WIDTH]
    with s._stage() as stage:
        b = batch(2,ANCHOR+2*WIDTH,stage._scope)
    s.recover(b,ANCHOR+2*WIDTH,authorize(s))
"""
        subprocess.run([sys.executable,"-B","-c",code,str(self.root)],
                       cwd=Path(__file__).resolve().parent,check=True,timeout=10)
        s = open_session(self.root,self.clock,self.verify)
        self.assertIsNone(s._read()["pending"])
        self.assertFalse(s.covers(ANCHOR,self.start(3)))
        self.assertTrue(s.covers(self.start(2),self.start(3)))
        self.reject("INTERVAL_OVERLAP_OR_REPLAY",
                    lambda: s.accept_next(self.inputs(0),ANCHOR),no_callback=True)

    def test_atomic_recovery_commit_failure(self):
        token = self.gap()
        replace = os.replace
        def fail_outer(src,dest):
            if Path(dest)==self.file:
                raise OSError("synthetic commit failure")
            return replace(src,dest)
        with patch("persistent_unified.os.replace",side_effect=fail_outer):
            self.reject("STATE_COMMIT_FAILED",lambda: self.s.recover(self.inputs(2),self.start(2),token))
        self.assertEqual(list(self.root.iterdir()),[self.file])
        self.s.recover(self.inputs(2),self.start(2),token)

    def test_gap_declaration_future_time_denied(self):
        self.admit(0)
        self.reject("INTERVAL_NOT_CLOSED",lambda: self.s.declare_gap(self.start(2)))

    def test_bounded_history_fails_closed_without_eviction(self):
        self.admit(0)
        for i in range(2,2*MAX_SEGMENTS,2):
            b = self.inputs(i)
            self.s.declare_gap(self.start(i))
            self.s.recover(b,self.start(i),authorize(self.s))
        b = self.inputs(2*MAX_SEGMENTS)
        self.s.declare_gap(self.start(2*MAX_SEGMENTS))
        self.reject("SEGMENT_LIMIT",lambda: self.s.recover(b,self.start(2*MAX_SEGMENTS),authorize(self.s)),no_callback=True)
        self.assertEqual(len(self.s._read()["segments"]),MAX_SEGMENTS)
        self.assertTrue(self.s.covers(ANCHOR,self.start(1)))

if __name__ == "__main__":
    print(__doc__,flush=True)
    unittest.main(verbosity=2)
