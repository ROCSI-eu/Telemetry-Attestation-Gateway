"""EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION.
Synthetic signed fixtures, independent simulated time/reference, mock proof verifier.
"""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

from state_rollback import Checkpoint, RollbackSession
from test_interval_recovery import open_session, authorize, RECOVERY_KEY
from test_interval_continuity import ANCHOR, WIDTH, options, batch, mock_pins
from trusted_time import BindingRejected


class RollbackTests(unittest.TestCase):
    def setUp(self):
        pins = mock_pins()
        pins.start()
        self.addCleanup(pins.stop)
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        self.local = root / "local"
        self.refdir = root / "reference"
        self.local.mkdir(mode=0o700)
        self.refdir.mkdir(mode=0o700)
        self.file = self.local / "state.json"
        self.ref = self.refdir / "state.json"
        self.clock = Mock(return_value=ANCHOR+400)
        self.verify = Mock(return_value=True)
        self.s = self.open(initialize=True)
        with self.s._stage() as stage:
            self.scope = stage._scope

    def open(self, **extra):
        return RollbackSession(state_dir=self.local, anchor=ANCHOR,
                               recovery_key=RECOVERY_KEY, reference=Checkpoint(self.refdir),
                               **options(self.clock,self.verify), **extra)

    def start(self, i):
        return ANCHOR+i*WIDTH

    def inputs(self, i):
        self.clock.return_value = max(self.clock.return_value,self.start(i)+400)
        return batch(i,self.start(i),self.scope)

    def admit(self, i, s=None):
        return (s or self.s).accept_next(self.inputs(i),self.start(i))

    def gap(self, s=None):
        s = s or self.s
        self.inputs(2)
        s.declare_gap(self.start(2))

    def recover(self, s=None):
        s = s or self.s
        s.recover(self.inputs(2),self.start(2),authorize(s))

    def reject(self, reason, fn):
        before = self.file.read_bytes() if self.file.exists() else None
        ref = self.ref.read_bytes() if self.ref.exists() else None
        calls = self.verify.call_count
        with self.assertRaisesRegex(BindingRejected,reason):
            fn()
        self.assertEqual(self.file.read_bytes() if self.file.exists() else None,before)
        self.assertEqual(self.ref.read_bytes() if self.ref.exists() else None,ref)
        self.assertEqual(self.verify.call_count,calls)

    def test_legacy_counterexample_replay_and_history_erasure(self):
        # Separate legacy directory; protected session is not touched.
        with tempfile.TemporaryDirectory() as path:
            s = open_session(path,self.clock,self.verify,initialize=True)
            f = Path(path)/"state.json"
            self.admit(0,s)
            old = f.read_bytes()
            self.gap(s)
            self.recover(s)
            self.assertFalse(s.covers(ANCHOR,self.start(3)))
            f.write_bytes(old)
            s = open_session(path,self.clock,self.verify)
            calls = self.verify.call_count
            self.admit(1,s)
            self.admit(2,s)
            self.assertEqual(self.verify.call_count,calls+6)
            self.assertTrue(s.covers(ANCHOR,self.start(3)))

    def test_normal_recovery_and_reopen_preserves_history(self):
        self.admit(0)
        self.gap()
        self.recover()
        s = self.open()
        self.assertTrue(s.covers(ANCHOR,self.start(1)))
        self.assertTrue(s.covers(self.start(2),self.start(3)))
        self.assertFalse(s.covers(ANCHOR,self.start(3)))
        self.reject("INTERVAL_OVERLAP_OR_REPLAY",lambda:self.admit(2,s))

    def test_historical_valid_record_rejected_before_replay(self):
        self.admit(0)
        old = self.file.read_bytes()
        self.admit(1)
        self.file.write_bytes(old)
        self.reject("STATE_REFERENCE_MISMATCH",self.open)
        self.reject("STATE_REFERENCE_MISMATCH",lambda:self.admit(1))
        self.reject("STATE_REFERENCE_MISMATCH",lambda:self.s.covers(ANCHOR,self.start(1)))

    def test_pending_gap_rollback_same_watermark(self):
        self.admit(0)
        old = self.file.read_bytes()
        self.gap()
        self.file.write_bytes(old)
        self.reject("STATE_REFERENCE_MISMATCH",lambda:self.admit(1))
        self.reject("STATE_REFERENCE_MISMATCH",self.open)

    def test_recovered_history_rollback_cannot_bridge_gap(self):
        self.admit(0)
        old = self.file.read_bytes()
        self.gap()
        self.recover()
        latest = self.file.read_bytes()
        self.file.write_bytes(old)
        self.reject("STATE_REFERENCE_MISMATCH",lambda:self.admit(1))
        self.reject("STATE_REFERENCE_MISMATCH",lambda:self.s.covers(ANCHOR,self.start(3)))
        self.file.write_bytes(latest)
        self.assertFalse(self.open().covers(ANCHOR,self.start(3)))

    def test_corrupt_state_distinct_from_valid_rollback(self):
        self.admit(0)
        self.file.write_bytes(b"{")
        self.reject("STATE_MISSING_CORRUPT_OR_INCOMPATIBLE",self.open)

    def test_missing_reference_no_reseed(self):
        self.admit(0)
        self.ref.unlink()
        self.reject("REFERENCE_UNAVAILABLE_OR_INVALID",self.open)
        self.reject("REFERENCE_UNAVAILABLE_OR_INVALID",lambda:self.admit(1))
        self.reject("STATE_ALREADY_EXISTS",lambda:self.open(initialize=True))

    def test_invalid_and_inconsistent_reference(self):
        self.admit(0)
        self.ref.write_bytes(b"invalid")
        self.reject("REFERENCE_UNAVAILABLE_OR_INVALID",self.open)
        self.ref.write_bytes(b"0"*64+b"\n")
        self.reject("STATE_REFERENCE_MISMATCH",lambda:self.admit(1))

    def test_reference_write_failure_never_commits_local(self):
        self.admit(0)
        old = self.file.read_bytes(),self.ref.read_bytes()
        replace = os.replace
        def fail(src,dest):
            if Path(dest)==self.ref:
                raise OSError("synthetic reference failure")
            return replace(src,dest)
        with patch("persistent_unified.os.replace",side_effect=fail):
            with self.assertRaisesRegex(BindingRejected,"STATE_COMMIT_FAILED"):
                self.admit(1)
        self.assertEqual((self.file.read_bytes(),self.ref.read_bytes()),old)
        self.assertEqual(list(self.refdir.iterdir()),[self.ref])
        self.open()

    def test_partial_commit_fail_closed_no_automatic_repair(self):
        self.admit(0)
        old = self.file.read_bytes(),self.ref.read_bytes()
        replace = os.replace
        def fail(src,dest):
            if Path(dest)==self.file:
                raise OSError("synthetic local failure")
            return replace(src,dest)
        with patch("persistent_unified.os.replace",side_effect=fail):
            with self.assertRaisesRegex(BindingRejected,"STATE_COMMIT_FAILED"):
                self.admit(1)
        self.assertEqual(self.file.read_bytes(),old[0])
        self.assertNotEqual(self.ref.read_bytes(),old[1])
        self.assertEqual(list(self.local.iterdir()),[self.file])
        self.reject("STATE_REFERENCE_MISMATCH",self.open)
        self.reject("STATE_REFERENCE_MISMATCH",lambda:self.admit(1))

    def test_both_restored_counterexample(self):
        self.admit(0)
        old = self.file.read_bytes(),self.ref.read_bytes()
        self.gap()
        self.recover()
        self.file.write_bytes(old[0])
        self.ref.write_bytes(old[1])
        s = self.open()
        self.admit(1,s)
        self.admit(2,s)
        self.assertTrue(s.covers(ANCHOR,self.start(3)))

    def test_restart_checks_reference(self):
        self.admit(0)
        old = self.file.read_bytes()
        self.gap()
        self.recover()
        code = """import sys
from unittest.mock import Mock
from state_rollback import RollbackSession,Checkpoint
from test_interval_recovery import RECOVERY_KEY
from test_interval_continuity import ANCHOR,WIDTH,options,mock_pins
from trusted_time import BindingRejected
with mock_pins():
    try:
        s=RollbackSession(state_dir=sys.argv[1],reference=Checkpoint(sys.argv[2]),anchor=ANCHOR,
           recovery_key=RECOVERY_KEY,**options(Mock(return_value=ANCHOR+2*WIDTH+400),Mock(return_value=True)))
    except BindingRejected as e:
        assert sys.argv[3]=="reject" and str(e)=="STATE_REFERENCE_MISMATCH"
    else:
        assert sys.argv[3]=="accept" and not s.covers(ANCHOR,ANCHOR+3*WIDTH)
"""
        def child(mode):
            subprocess.run([sys.executable,"-B","-c",code,str(self.local),str(self.refdir),mode],
                           cwd=Path(__file__).resolve().parent,check=True,timeout=10)
        child("accept")
        self.file.write_bytes(old)
        child("reject")

if __name__ == "__main__":
    print(__doc__,flush=True)
    unittest.main(verbosity=2)
