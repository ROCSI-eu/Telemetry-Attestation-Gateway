"""EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION."""
import tempfile
from pathlib import Path
import subprocess
import sys
import unittest
from epoch_transition_consistency import TransitionConsistency, BindingRejected
from test_epoch_transition_binding import authorization, KEY, SCOPE, A, B

C = "synthetic-other-successor"


class ConsistencyTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.gate = self.slot(self.root)
        self.a = authorization()
        self.b = authorization(successor=C)

    def slot(self, root, scope=SCOPE, previous=A):
        for name in ("state", "reference"):
            (root / name).mkdir(mode=0o700, parents=True)
        return TransitionConsistency(root, key=KEY, scope=scope,
                                     previous=previous, initialize=True)

    def open(self):
        return TransitionConsistency(self.root, key=KEY, scope=SCOPE, previous=A)

    def path(self, name):
        return self.root / name / "state.json"

    def snapshot(self):
        return tuple(self.path(name).read_bytes() for name in ("state", "reference"))

    def reject(self, auth, reason, gate=None):
        before = self.snapshot()
        with self.assertRaisesRegex(BindingRejected, reason):
            (gate or self.gate).observe(auth)
        self.assertEqual(self.snapshot(), before)

    def test_first(self):
        self.assertEqual(self.gate.observe(self.a), "ACCEPT")

    def test_idempotence(self):
        self.gate.observe(self.a)
        before = self.snapshot()
        self.assertEqual(self.gate.observe(self.a), "IDEMPOTENT")
        self.assertEqual(before, self.snapshot())

    def test_conflict(self):
        self.gate.observe(self.a)
        self.reject(self.b, "TRANSITION_AUTHORIZATION_CONFLICT")

    def test_reverse_order(self):
        self.assertEqual(self.gate.observe(self.b), "ACCEPT")
        self.reject(self.a, "TRANSITION_AUTHORIZATION_CONFLICT")

    def test_invalid_mac_before_and_after(self):
        self.reject(dict(self.a, mac="0"*64), "TRANSITION_NOT_AUTHENTIC")
        self.gate.observe(self.a)
        self.reject(dict(self.b, mac=self.a["mac"]), "TRANSITION_NOT_AUTHENTIC")
        self.reject(authorization(key=b"X"*32), "TRANSITION_NOT_AUTHENTIC")

    def test_context_scope(self):
        self.gate.observe(self.a)
        other = authorization(scope="synthetic-other-scope", successor=C)
        self.reject(other, "CONSISTENCY_CONTEXT_MISMATCH")
        slot = self.slot(self.root / "other-scope", scope=other["scope"])
        self.assertEqual(slot.observe(other), "ACCEPT")

    def test_context_previous(self):
        self.gate.observe(self.a)
        other = authorization(previous=B, successor=C)
        self.reject(other, "CONSISTENCY_CONTEXT_MISMATCH")
        slot = self.slot(self.root / "other-previous", previous=B)
        self.assertEqual(slot.observe(other), "ACCEPT")

    def test_restart_process(self):
        self.gate.observe(self.a)
        before = self.snapshot()
        script = """
import sys
from pathlib import Path
from epoch_transition_consistency import TransitionConsistency, BindingRejected
from test_epoch_transition_binding import authorization, KEY, SCOPE, A
gate = TransitionConsistency(Path(sys.argv[1]), key=KEY, scope=SCOPE, previous=A)
assert gate.observe(authorization()) == "IDEMPOTENT"
try:
    gate.observe(authorization(successor="synthetic-other-successor"))
except BindingRejected as e:
    assert str(e) == "TRANSITION_AUTHORIZATION_CONFLICT"
else:
    raise AssertionError("missing conflict")
"""
        subprocess.run([sys.executable, "-B", "-c", script, str(self.root)], check=True)
        self.assertEqual(before, self.snapshot())

    def test_invalid_reference(self):
        self.gate.observe(self.a)
        self.path("reference").write_text("invalid\n")
        self.reject(self.b, "REFERENCE_UNAVAILABLE_OR_INVALID")
        with self.assertRaisesRegex(BindingRejected, "REFERENCE_UNAVAILABLE_OR_INVALID"):
            self.open()

    def test_missing_reference(self):
        self.gate.observe(self.a)
        before = self.path("state").read_bytes()
        self.path("reference").unlink()
        for action in (lambda: self.gate.observe(self.b), self.open):
            with self.assertRaisesRegex(BindingRejected, "REFERENCE_UNAVAILABLE_OR_INVALID"):
                action()
        self.assertEqual(before, self.path("state").read_bytes())
        self.assertFalse(self.path("reference").exists())

    def test_single_copy_restored(self):
        old = self.path("state").read_bytes()
        self.gate.observe(self.a)
        self.path("state").write_bytes(old)
        self.reject(self.b, "STATE_REFERENCE_MISMATCH")

    def test_both_copies_restored_counterexample(self):
        old = self.snapshot()
        self.gate.observe(self.a)
        for name, data in zip(("state", "reference"), old):
            self.path(name).write_bytes(data)
        self.assertEqual(self.open().observe(self.b), "ACCEPT")
        self.reject(self.a, "TRANSITION_AUTHORIZATION_CONFLICT")

    def test_shape(self):
        self.reject(dict(self.a, extra=True), "INVALID_TRANSITION_EVIDENCE")


if __name__ == "__main__":
    unittest.main(verbosity=2)
