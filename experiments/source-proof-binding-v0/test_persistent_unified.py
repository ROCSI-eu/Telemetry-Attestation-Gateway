"""New persistence tests; verifier callback is a test double, not a new ZKP.

EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION
"""
import copy
import hashlib
import unified
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

from persistent_unified import PersistentUnified, BindingRejected
from test_temporal_gate import CONFIG, sample
from unified import public_inputs
from binding_reference import authorized_digest

ARTIFACTS = dict(proof=b"mock-proof-not-cryptographic", vk=b"mock-vk-not-cryptographic")


def mock_pins():
    return patch.multiple(unified,
                          PINNED_PROOF=hashlib.sha256(ARTIFACTS["proof"]).hexdigest(),
                          PINNED_VK=hashlib.sha256(ARTIFACTS["vk"]).hexdigest())


def open_session(directory, verify, **extra):
    return PersistentUnified(state_dir=directory, verify=verify, **ARTIFACTS, **CONFIG, **extra)


class PersistenceTests(unittest.TestCase):
    def setUp(self):
        pins = mock_pins()
        pins.start()
        self.addCleanup(pins.stop)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.file = self.directory / "state.json"
        self.verify = Mock(return_value=True)
        self.session = open_session(self.directory, self.verify, initialize=True)

    def test_actual_process_restart(self):
        writer = """
import sys
from test_persistent_unified import open_session, sample, Mock, mock_pins
mock_pins().start()
verify = Mock(return_value=True)
open_session(sys.argv[1], verify).accept(sample())
verify.assert_called_once()
"""
        subprocess.run([sys.executable, "-B", "-c", writer, str(self.directory)],
                       cwd=Path(__file__).resolve().parent, check=True, timeout=10)
        code = '''
import sys
from test_persistent_unified import open_session, sample, Mock, BindingRejected, mock_pins
mock_pins().start()
verify = Mock(return_value=True)
s = open_session(sys.argv[1], verify)
try:
    s.accept(sample())
except BindingRejected as e:
    assert "CROSS_CAPTURE_REPLAY" in str(e)
else:
    raise AssertionError("replay accepted")
verify.assert_not_called()
s.accept(sample(100002, 1001))
verify.assert_called_once()
'''
        subprocess.run([sys.executable, "-B", "-c", code, str(self.directory)],
                       cwd=Path(__file__).resolve().parent, check=True, timeout=10)
        with self.assertRaisesRegex(BindingRejected, "CROSS_CAPTURE_REPLAY"):
            self.session.accept(sample(100002, 1001))
        self.verify.assert_not_called()

    def test_proof_false_and_exception_leave_state_unchanged(self):
        self.session.accept(sample())
        prior = self.file.read_bytes()
        self.verify.side_effect = [False, RuntimeError("mock verifier failed"), True]
        c = sample(100002, 1001)
        with self.assertRaisesRegex(BindingRejected, "PROOF_NOT_ACCEPTED"):
            self.session.accept(c)
        with self.assertRaises(RuntimeError):
            self.session.accept(c)
        self.assertEqual(self.file.read_bytes(), prior)
        self.assertEqual(open_session(self.directory, self.verify).accept(c), authorized_digest(c, **CONFIG))
        self.assertEqual(self.verify.call_args.args[0], public_inputs(authorized_digest(c, **CONFIG)))

    def test_replace_failure_no_acceptance_or_partial_state(self):
        prior = self.file.read_bytes()
        with patch("persistent_unified.os.replace", side_effect=OSError):
            with self.assertRaisesRegex(BindingRejected, "STATE_COMMIT_FAILED"):
                self.session.accept(sample())
        self.assertEqual(self.file.read_bytes(), prior)
        self.assertEqual(list(self.directory.iterdir()), [self.file])
        open_session(self.directory, self.verify).accept(sample())

    def test_fsync_after_replace_failure_no_acceptance(self):
        real = os.fsync
        calls = []
        def fail_directory(fd):
            calls.append(fd)
            if len(calls) == 2:
                raise OSError
            real(fd)
        with patch("persistent_unified.os.fsync", side_effect=fail_directory):
            with self.assertRaisesRegex(BindingRejected, "STATE_COMMIT_FAILED"):
                self.session.accept(sample())
        with self.assertRaisesRegex(BindingRejected, "CROSS_CAPTURE_REPLAY"):
            open_session(self.directory, self.verify).accept(sample())

    def test_corruption_and_incompatibility(self):
        self.session.accept(sample())
        good = self.file.read_bytes()
        for data in [b"{", good.replace(b"100001", b"100000"),
                     good.replace(b'"version":1', b'"version":2'),
                     good.replace(b'"scope":"', b'"scope":"x'),
                     good+b" ", b"[]" , self.session._encode([True, 0]),
                     self.session._encode([2**48, 0])]:
            self.file.write_bytes(data)
            with self.assertRaisesRegex(BindingRejected, "STATE_MISSING_CORRUPT_OR_INCOMPATIBLE"):
                open_session(self.directory, self.verify)
        self.file.write_bytes(good)
        open_session(self.directory, self.verify)
        self.verify.assert_called_once()

    def test_missing_state_and_no_reinitialize(self):
        with self.assertRaisesRegex(BindingRejected, "STATE_ALREADY_EXISTS"):
            open_session(self.directory, self.verify, initialize=True)
        self.file.unlink()
        with self.assertRaisesRegex(BindingRejected, "STATE_MISSING_CORRUPT_OR_INCOMPATIBLE"):
            open_session(self.directory, self.verify)
        with self.assertRaisesRegex(BindingRejected, "STATE_MISSING_CORRUPT_OR_INCOMPATIBLE"):
            self.session.accept(sample())
        self.verify.assert_not_called()

    def test_other_enrollment_rejected(self):
        c = copy.deepcopy(CONFIG)
        c["enrollment"]["alias"] = c["requested_alias"] = "other-synthetic"
        with self.assertRaisesRegex(BindingRejected, "STATE_MISSING_CORRUPT_OR_INCOMPATIBLE"):
            PersistentUnified(state_dir=self.directory, verify=self.verify, **ARTIFACTS, **c)
        self.verify.assert_not_called()

    def test_private_state_and_serialization(self):
        self.assertEqual(self.file.stat().st_mode & 0o777, 0o600)
        with self.session._locked():
            with self.assertRaisesRegex(BindingRejected, "DIRECTORY_UNAVAILABLE_OR_BUSY"):
                open_session(self.directory, self.verify)
        self.session.accept(sample())
        payload = json.loads(self.file.read_bytes())["payload"]
        self.assertEqual(set(payload), {"scope", "version", "watermark"})

    def test_rollback_limitation_demonstrated(self):
        historical = self.file.read_bytes()
        self.session.accept(sample())
        self.file.write_bytes(historical)
        # Trusted local state is an assumption: a valid old state bypasses history.
        open_session(self.directory, self.verify).accept(sample())
        self.assertEqual(self.verify.call_count, 2)

    def test_regression_after_restart(self):
        self.session.accept(sample())
        restarted = open_session(self.directory, self.verify)
        with self.assertRaisesRegex(BindingRejected, "CROSS_CAPTURE_BOOT_REGRESSION"):
            restarted.accept(sample(100002, 999))
        self.verify.assert_called_once()
        restarted.accept(sample(100002, 1001))


if __name__ == "__main__":
    unittest.main(verbosity=2)
