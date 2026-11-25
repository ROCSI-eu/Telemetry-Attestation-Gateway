"""EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION.
SOURCE-STATE-COMMIT-UNCERTAINTY-01: isolated synthetic acknowledgement/commit ambiguity.
Non-cryptographic test harness; no real power-loss, independent reference or proving.
"""
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

# Reuse locally pinned source, no source mutation or new dependency.

from state_reconciliation import ReconciliationSession
from state_rollback import Checkpoint
from test_state_rollback import RollbackTests
from test_interval_continuity import ANCHOR, options
from test_interval_recovery import RECOVERY_KEY
from trusted_time import BindingRejected


class CommitUncertaintyCases(RollbackTests):
    def open(self, **kwargs):
        return ReconciliationSession(
            state_dir=self.local, anchor=ANCHOR, recovery_key=RECOVERY_KEY,
            reference=Checkpoint(self.refdir), **options(self.clock, self.verify),
            **kwargs,
        )

    @property
    def prepared(self):
        return self.local / "prepared.json"

    def snapshot(self):
        return tuple(p.read_bytes() if p.exists() else None for p in (self.file, self.ref, self.prepared))

    def denied(self, reason, action):
        before = self.snapshot()
        checks = self.verify.call_count
        with self.assertRaises(BindingRejected) as error:
            action()
        self.assertEqual(str(error.exception), reason)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.verify.call_count, checks)

    def fail_reference_replace(self, action):
        original = os.replace

        def injected(src, dst):
            if Path(dst) == self.ref:
                raise OSError("synthetic reference write failed before atomic replace")
            return original(src, dst)

        with patch("persistent_unified.os.replace", side_effect=injected):
            with self.assertRaisesRegex(BindingRejected, "STATE_COMMIT_FAILED"):
                action()

    def fail_local_replace(self, action):
        original = os.replace

        def injected(src, dst):
            if Path(dst) == self.file:
                raise OSError("synthetic local write failed before atomic replace")
            return original(src, dst)

        with patch("persistent_unified.os.replace", side_effect=injected):
            with self.assertRaisesRegex(BindingRejected, "STATE_COMMIT_FAILED"):
                action()

    def test_01_not_applied_retry_once_then_replay_denied(self):
        self.admit(0)
        before = self.snapshot()
        self.fail_reference_replace(lambda: self.admit(1))
        local, reference, candidate = self.snapshot()
        self.assertEqual((local, reference), before[:2])
        self.assertNotEqual(candidate, before[2])  # Prepared, not committed.
        reopened = self.open()
        self.denied("RECONCILIATION_NOT_REQUIRED", lambda: self.open(reconcile=True))
        self.admit(1, reopened)  # One safe retry in this explicitly known state.
        self.assertTrue(self.open().covers(ANCHOR, self.start(2)))
        self.denied("INTERVAL_OVERLAP_OR_REPLAY", lambda: self.admit(1, reopened))

    def test_02_commit_succeeded_but_caller_acknowledgement_lost(self):
        self.admit(0)

        def commit_then_lose_reply():
            self.admit(1)  # The state update really returned success internally.
            raise ConnectionError("synthetic acknowledgement lost to caller")

        with self.assertRaisesRegex(ConnectionError, "acknowledgement lost"):
            commit_then_lose_reply()
        committed = self.snapshot()
        reopened = self.open()
        self.assertTrue(reopened.covers(ANCHOR, self.start(2)))
        self.assertEqual(self.snapshot(), committed)
        # A duplicate request is rejected before another proof callback.
        self.denied("INTERVAL_OVERLAP_OR_REPLAY", lambda: self.admit(1, reopened))

    def test_03_local_replace_succeeded_but_fsync_reports_failure(self):
        self.admit(0)
        original_replace = os.replace
        original_fsync = os.fsync
        local_swapped = False
        rejected_directory_fsync = False

        def replaced(src, dst):
            nonlocal local_swapped
            result = original_replace(src, dst)
            if Path(dst) == self.file:
                local_swapped = True
            return result

        def synced(fd):
            nonlocal rejected_directory_fsync
            if local_swapped and os.readlink(f"/proc/self/fd/{fd}") == str(self.local):
                rejected_directory_fsync = True
                raise OSError("synthetic directory fsync acknowledgement failure")
            return original_fsync(fd)

        with patch("persistent_unified.os.replace", side_effect=replaced), \
             patch("persistent_unified.os.fsync", side_effect=synced):
            with self.assertRaisesRegex(BindingRejected, "STATE_COMMIT_FAILED"):
                self.admit(1)
        self.assertTrue(rejected_directory_fsync)
        self.assertEqual(self.file.read_bytes(), self.prepared.read_bytes())
        reopened = self.open()  # Visible after failure; not power-loss durability.
        self.assertTrue(reopened.covers(ANCHOR, self.start(2)))
        self.denied("INTERVAL_OVERLAP_OR_REPLAY", lambda: self.admit(1, reopened))

    def test_04_reference_advanced_local_failed_retry_must_not_replay(self):
        self.admit(0)
        self.gap()
        previous = self.snapshot()
        self.fail_local_replace(self.recover)
        old_local, new_ref, new_candidate = self.snapshot()
        self.assertEqual(old_local, previous[0])
        self.assertNotEqual(new_ref, previous[1])
        self.assertNotEqual(new_candidate, previous[2])
        self.denied("STATE_REFERENCE_MISMATCH", self.open)
        self.denied("STATE_REFERENCE_MISMATCH", lambda: self.admit(2))
        # Only explicit bounded reconciliation, not blind resend.
        self.open(reconcile=True)
        reopened = self.open()
        self.assertTrue(reopened.covers(ANCHOR, self.start(1)))
        self.assertTrue(reopened.covers(self.start(2), self.start(3)))
        self.assertFalse(reopened.covers(ANCHOR, self.start(3)))
        self.denied("INTERVAL_OVERLAP_OR_REPLAY", lambda: self.admit(2, reopened))
        self.denied("RECOVERY_TARGET_MISMATCH", lambda: self.recover(reopened))
        saved = self.file.read_bytes()
        self.file.write_bytes(previous[0])  # Synthetic local regression.
        self.denied("STATE_REFERENCE_MISMATCH", self.open)
        self.file.write_bytes(saved)
        self.assertFalse(self.open().covers(ANCHOR, self.start(3)))

    def test_05_ambiguous_evidence_fails_closed_no_automatic_reseed(self):
        self.admit(0)
        self.gap()
        previous = self.snapshot()
        self.fail_local_replace(self.recover)
        self.prepared.write_bytes(previous[2])  # Valid but stale candidate.
        self.denied("STATE_REFERENCE_MISMATCH", self.open)
        self.denied("RECONCILIATION_REFERENCE_MISMATCH",
                    lambda: self.open(reconcile=True))
        self.denied("STATE_REFERENCE_MISMATCH", lambda: self.admit(2))
        self.ref.unlink()  # Missing simulated independent reference.
        self.denied("REFERENCE_UNAVAILABLE_OR_INVALID", self.open)
        self.denied("REFERENCE_UNAVAILABLE_OR_INVALID",
                    lambda: self.open(reconcile=True))


if __name__ == "__main__":
    print(__doc__, flush=True)
    suite = unittest.TestSuite(
        CommitUncertaintyCases(case) for case in CommitUncertaintyCases.__dict__
        if case.startswith("test_")
    )
    outcome = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if outcome.wasSuccessful() else 1)
