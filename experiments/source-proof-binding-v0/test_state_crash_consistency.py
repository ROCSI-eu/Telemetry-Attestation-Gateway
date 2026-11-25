"""EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION.
Non-cryptographic synthetic process-interruption probe; no real crash/power-loss qualification.
"""
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

from state_rollback import Checkpoint
from state_reconciliation import ReconciliationSession
from test_state_rollback import RollbackTests
from test_interval_recovery import RECOVERY_KEY
from test_interval_continuity import ANCHOR, options

EXIT_CRASH = 73


class CrashCases(RollbackTests):
    def open(self, **extra):
        return ReconciliationSession(
            state_dir=self.local, anchor=ANCHOR, recovery_key=RECOVERY_KEY,
            reference=Checkpoint(self.refdir), **options(self.clock, self.verify), **extra)

    @property
    def prepared(self):
        return self.local / "prepared.json"

    def triplet(self):
        return (self.file.read_bytes(), self.ref.read_bytes(),
                self.prepared.read_bytes())

    def interrupt(self, phase, operation):
        pid = os.fork()
        if pid == 0:
            try:
                real_replace = os.replace
                real_fsync = os.fsync
                if phase in ("pre_candidate_replace", "pre_local_replace"):
                    target = self.prepared if phase == "pre_candidate_replace" else self.file

                    def replaced(src, dst):
                        if Path(dst) == target:
                            os._exit(EXIT_CRASH)
                        return real_replace(src, dst)

                    with patch("persistent_unified.os.replace", side_effect=replaced):
                        operation()
                elif phase == "post_candidate_pre_reference":
                    self.s._reference.advance = lambda *args: os._exit(EXIT_CRASH)
                    operation()
                elif phase == "post_local_replace_pre_directory_fsync":
                    local_replaced = False

                    def replaced(src, dst):
                        nonlocal local_replaced
                        result = real_replace(src, dst)
                        if Path(dst) == self.file:
                            local_replaced = True
                        return result

                    def synced(fd):
                        path = os.readlink(f"/proc/self/fd/{fd}")
                        if local_replaced and path == str(self.local):
                            os._exit(EXIT_CRASH)
                        return real_fsync(fd)

                    with patch("persistent_unified.os.replace", side_effect=replaced), \
                         patch("persistent_unified.os.fsync", side_effect=synced):
                        operation()
                else:
                    os._exit(74)
            except BaseException:
                os._exit(75)
            os._exit(76)
        _, status = os.waitpid(pid, 0)
        self.assertTrue(os.WIFEXITED(status), status)
        self.assertEqual(os.WEXITSTATUS(status), EXIT_CRASH, (phase, status))

    def test_01_interrupt_before_candidate_persistence(self):
        self.admit(0)
        original = self.triplet()
        self.interrupt("pre_candidate_replace", lambda: self.admit(1))
        self.assertEqual(self.triplet(), original)
        self.open()  # Fresh object, no repair required.
        self.reject("RECONCILIATION_NOT_REQUIRED", lambda: self.open(reconcile=True))
        restarted = self.open()
        self.admit(1, restarted)
        self.reject("INTERVAL_OVERLAP_OR_REPLAY", lambda: self.admit(1, restarted))

    def test_02_prepared_candidate_not_yet_referenced(self):
        self.admit(0)
        original = self.triplet()
        self.interrupt("post_candidate_pre_reference", lambda: self.admit(1))
        after = self.triplet()
        self.assertEqual(after[:2], original[:2])
        self.assertNotEqual(after[2], original[2])
        self.open()  # Old matching pair is usable; candidate alone is not authoritative.
        self.reject("RECONCILIATION_NOT_REQUIRED", lambda: self.open(reconcile=True))
        restarted = self.open()
        self.admit(1, restarted)
        self.reject("INTERVAL_OVERLAP_OR_REPLAY", lambda: self.admit(1, restarted))

    def test_03_reference_advanced_local_not_replaced(self):
        self.admit(0)
        self.gap()
        original = self.triplet()
        self.interrupt("pre_local_replace", self.recover)
        after = self.triplet()
        self.assertEqual(after[0], original[0])
        self.assertNotEqual(after[1], original[1])
        self.assertNotEqual(after[2], original[2])
        self.reject("STATE_REFERENCE_MISMATCH", self.open)
        self.open(reconcile=True)
        self.assertEqual(self.file.read_bytes(), self.prepared.read_bytes())
        restarted = self.open()
        self.assertTrue(restarted.covers(ANCHOR, self.start(1)))
        self.assertTrue(restarted.covers(self.start(2), self.start(3)))
        self.assertFalse(restarted.covers(ANCHOR, self.start(3)))
        self.reject("INTERVAL_OVERLAP_OR_REPLAY", lambda: self.admit(2, restarted))
        latest = self.file.read_bytes()
        self.file.write_bytes(original[0])  # Synthetic historical-state regression.
        self.reject("STATE_REFERENCE_MISMATCH", self.open)
        self.file.write_bytes(latest)
        self.assertFalse(self.open().covers(ANCHOR, self.start(3)))

    def test_04_local_replaced_before_durability_acknowledgement(self):
        self.admit(0)
        original = self.triplet()
        self.interrupt("post_local_replace_pre_directory_fsync", lambda: self.admit(1))
        after = self.triplet()
        self.assertNotEqual(after[0], original[0])
        self.assertNotEqual(after[1], original[1])
        self.assertEqual(after[0], after[2])
        restarted = self.open()  # Visibility after process death, NOT power-loss durability.
        self.reject("RECONCILIATION_NOT_REQUIRED", lambda: self.open(reconcile=True))
        self.assertTrue(restarted.covers(ANCHOR, self.start(2)))
        self.reject("INTERVAL_OVERLAP_OR_REPLAY", lambda: self.admit(1, restarted))

    def test_05_ambiguous_interrupted_pair_fails_closed(self):
        self.admit(0)
        self.gap()
        self.interrupt("pre_local_replace", self.recover)
        self.prepared.write_bytes(b"{")  # Candidate lacks parseable evidence.
        self.reject("STATE_REFERENCE_MISMATCH", self.open)
        self.reject("RECONCILIATION_EVIDENCE_UNAVAILABLE", lambda: self.open(reconcile=True))
        self.ref.unlink()  # Trusted reference unavailable: no automatic reseed.
        self.reject("REFERENCE_UNAVAILABLE_OR_INVALID", lambda: self.open(reconcile=True))


if __name__ == "__main__":
    print(__doc__, flush=True)
    suite = unittest.TestSuite(CrashCases(name) for name in CrashCases.__dict__
                               if name.startswith("test_"))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
