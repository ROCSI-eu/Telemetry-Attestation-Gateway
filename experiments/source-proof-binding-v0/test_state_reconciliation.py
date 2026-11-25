"""EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION."""
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch
import test_state_rollback as fixtures
from state_rollback import Checkpoint
from state_reconciliation import ReconciliationSession
from test_interval_recovery import RECOVERY_KEY, authorize
from test_interval_continuity import ANCHOR, WIDTH, options
from trusted_time import BindingRejected


class Tests(fixtures.RollbackTests):
    def open(self, **extra):
        return ReconciliationSession(state_dir=self.local, anchor=ANCHOR,
            recovery_key=RECOVERY_KEY, reference=Checkpoint(self.refdir),
            **options(self.clock,self.verify), **extra)

    @property
    def prepared(self):
        return self.local / "prepared.json"

    def fail_local(self, fn):
        old = self.file.read_bytes()
        ref = self.ref.read_bytes()
        replace = os.replace
        def fail(src,dest):
            if Path(dest) == self.file:
                raise OSError("synthetic local commit interruption")
            return replace(src,dest)
        with patch("persistent_unified.os.replace", side_effect=fail):
            with self.assertRaisesRegex(BindingRejected, "STATE_COMMIT_FAILED"):
                fn()
        self.assertEqual(self.file.read_bytes(),old)
        self.assertNotEqual(self.ref.read_bytes(),ref)
        self.assertNotEqual(self.prepared.read_bytes(),old)

    def repair(self):
        ref = self.ref.read_bytes()
        calls = self.verify.call_count
        s = self.open(reconcile=True)
        self.assertEqual(self.file.read_bytes(),self.prepared.read_bytes())
        self.assertEqual(self.ref.read_bytes(),ref)
        self.assertEqual(self.verify.call_count,calls)
        return s

    def interrupted_recovery(self):
        self.admit(0)
        self.gap()
        self.fail_local(lambda:self.recover())

    def test_repair_interval(self):
        self.admit(0)
        self.fail_local(lambda:self.admit(1))
        self.reject("STATE_REFERENCE_MISMATCH",self.open)
        s = self.repair()
        self.assertTrue(s.covers(ANCHOR,self.start(2)))
        self.reject("INTERVAL_OVERLAP_OR_REPLAY",lambda:self.admit(1,s))

    def test_repair_gap_same_watermark(self):
        self.admit(0)
        self.fail_local(self.gap)
        s = self.repair()
        self.reject("RECOVERY_REQUIRED",lambda:self.admit(1,s))
        self.recover(s)
        self.assertFalse(s.covers(ANCHOR,self.start(3)))

    def test_repair_recovery_history(self):
        self.interrupted_recovery()
        s = self.repair()
        self.assertTrue(s.covers(ANCHOR,self.start(1)))
        self.assertTrue(s.covers(self.start(2),self.start(3)))
        self.assertFalse(s.covers(ANCHOR,self.start(3)))
        self.reject("INTERVAL_OVERLAP_OR_REPLAY",lambda:self.admit(1,s))
        self.reject("INTERVAL_OVERLAP_OR_REPLAY",lambda:self.admit(2,s))

    def test_historical_candidate(self):
        self.admit(0)
        old = self.prepared.read_bytes()
        self.gap()
        self.fail_local(lambda:self.recover())
        self.prepared.write_bytes(old)
        self.reject("RECONCILIATION_REFERENCE_MISMATCH",lambda:self.open(reconcile=True))

    def test_reference_and_candidate_historical(self):
        self.admit(0)
        old = self.prepared.read_bytes(),self.ref.read_bytes()
        self.gap()
        self.recover()
        self.prepared.write_bytes(old[0])
        self.ref.write_bytes(old[1])
        self.reject("RECONCILIATION_NOT_FORWARD",lambda:self.open(reconcile=True))

    def test_missing_candidate(self):
        self.interrupted_recovery()
        self.prepared.unlink()
        self.reject("RECONCILIATION_EVIDENCE_UNAVAILABLE",lambda:self.open(reconcile=True))

    def test_invalid_candidate(self):
        self.interrupted_recovery()
        self.prepared.write_bytes(b"{")
        self.reject("RECONCILIATION_EVIDENCE_UNAVAILABLE",lambda:self.open(reconcile=True))

    def test_missing_reference(self):
        self.interrupted_recovery()
        self.ref.unlink()
        self.reject("REFERENCE_UNAVAILABLE_OR_INVALID",lambda:self.open(reconcile=True))

    def test_no_repair_on_matching_pair(self):
        self.admit(0)
        self.reject("RECONCILIATION_NOT_REQUIRED",lambda:self.open(reconcile=True))

    def test_restart_after_repair(self):
        self.interrupted_recovery()
        self.repair()
        code = """import sys
from unittest.mock import Mock
from state_reconciliation import ReconciliationSession
from state_rollback import Checkpoint
from test_interval_recovery import RECOVERY_KEY
from test_interval_continuity import ANCHOR, WIDTH, options, batch, mock_pins
from trusted_time import BindingRejected
with mock_pins():
    verify=Mock(return_value=True)
    s=ReconciliationSession(state_dir=sys.argv[1],reference=Checkpoint(sys.argv[2]),
        anchor=ANCHOR,recovery_key=RECOVERY_KEY,
        **options(Mock(return_value=ANCHOR+2*WIDTH+400),verify))
    assert not s.covers(ANCHOR,ANCHOR+3*WIDTH)
    assert s.covers(ANCHOR+2*WIDTH,ANCHOR+3*WIDTH)
    with s._stage() as stage:
        scope=stage._scope
    try:
        s.accept_next(batch(2,ANCHOR+2*WIDTH,scope),ANCHOR+2*WIDTH)
    except BindingRejected as e:
        assert str(e)=="INTERVAL_OVERLAP_OR_REPLAY"
    else:
        raise AssertionError("replay accepted")
    assert verify.call_count==0
"""
        subprocess.run([sys.executable,"-B","-c",code,str(self.local),str(self.refdir)],
            cwd=Path(__file__).resolve().parent,check=True,timeout=10)

    def test_joint_rollback_counterexample(self):
        self.admit(0)
        old = self.file.read_bytes(),self.ref.read_bytes(),self.prepared.read_bytes()
        self.gap()
        self.recover()
        for path,data in zip((self.file,self.ref,self.prepared),old):
            path.write_bytes(data)
        s=self.open()
        self.reject("RECONCILIATION_NOT_REQUIRED",lambda:self.open(reconcile=True))
        self.admit(1,s)
        self.admit(2,s)
        self.assertTrue(s.covers(ANCHOR,self.start(3)))


if __name__ == "__main__":
    print(__doc__,flush=True)
    names=[n for n in Tests.__dict__ if n.startswith("test_")]
    result=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(Tests(n) for n in names))
    sys.exit(not result.wasSuccessful())
