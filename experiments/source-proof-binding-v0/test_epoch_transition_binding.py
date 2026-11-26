"""EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION."""
import tempfile
from pathlib import Path
import unittest
from epoch_transition_binding import EpochTransitionBinding, transition_mac
from emission_gap import BindingRejected, index_mac
from test_emission_gap import KEY, SCOPE, CONFIG, record
from test_emission_end_anchor import anchor
from test_emission_end_freshness import A, B

NAMES = ("current", "reference", "closure-0", "closure-1")


def authorization(scope=SCOPE, previous=A, successor=B, key=KEY):
    return dict(scope=scope, previous=previous, successor=successor,
                mac=transition_mac(key, scope, previous, successor))


class TransitionTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        for name in NAMES:
            (self.root / name).mkdir(mode=0o700)
        self.gate = self.open(True)
        self.auth = authorization()

    def open(self, initialize=False):
        return EpochTransitionBinding(self.root, key=KEY, scope=SCOPE,
            first=1, config=CONFIG, epochs=(A, B), initialize=initialize)

    def path(self, name):
        return self.root / name / "state.json"

    def snapshot(self):
        return tuple(self.path(name).read_bytes() for name in NAMES)

    def reject(self, auth, reason, gate=None):
        before = self.snapshot()
        with self.assertRaisesRegex(BindingRejected, reason):
            (gate or self.gate).transition(auth)
        self.assertEqual(before, self.snapshot())

    def test_valid_transition_and_terminal_admission(self):
        self.assertEqual(self.gate.accept([record(1, epoch=A)], anchor(1, epoch=A)), "ACCEPT")
        self.assertEqual(self.gate.transition(self.auth), "ACCEPT")
        self.assertEqual(self.gate.accept([record(1, epoch=B)], anchor(1, epoch=B)), "ACCEPT")
        with self.assertRaisesRegex(BindingRejected, "TERMINAL_EPOCH_NOT_CURRENT"):
            self.gate.accept([record(1, epoch=A)], anchor(1, epoch=A))

    def test_mutated_scope(self):
        self.reject(dict(self.auth, scope="other"), "TRANSITION_NOT_AUTHENTIC")

    def test_mutated_previous(self):
        self.reject(dict(self.auth, previous="other"), "TRANSITION_NOT_AUTHENTIC")

    def test_mutated_successor(self):
        self.reject(dict(self.auth, successor="other"), "TRANSITION_NOT_AUTHENTIC")

    def test_invalid_mac_and_wrong_key(self):
        self.reject(dict(self.auth, mac="0"*64), "TRANSITION_NOT_AUTHENTIC")
        self.reject(authorization(key=b"X"*32), "TRANSITION_NOT_AUTHENTIC")

    def test_authentic_wrong_scope(self):
        self.reject(authorization(scope="other"), "TRANSITION_SCOPE_MISMATCH")

    def test_authentic_wrong_previous(self):
        self.reject(authorization(previous="other"), "EPOCH_TRANSITION_NOT_AUTHORIZED")

    def test_authentic_wrong_successor(self):
        self.reject(authorization(successor="other"), "EPOCH_TRANSITION_NOT_AUTHORIZED")

    def test_replay_and_stale_session(self):
        stale = self.open()
        self.gate.transition(self.auth)
        self.reject(self.auth, "EPOCH_TRANSITION_NOT_AUTHORIZED", stale)

    def test_authentic_reverse(self):
        self.gate.transition(self.auth)
        self.reject(authorization(previous=B, successor=A), "EPOCH_TRANSITION_NOT_AUTHORIZED")

    def test_restart_and_rejection_preserve_state(self):
        self.reject(authorization(key=b"X"*32), "TRANSITION_NOT_AUTHENTIC")
        self.assertEqual(self.open().transition(self.auth), "ACCEPT")
        self.reject(self.auth, "EPOCH_TRANSITION_NOT_AUTHORIZED", self.open())

    def test_missing_or_invalid_reference(self):
        reference = self.path("reference")
        reference.write_text("invalid\n")
        self.reject(self.auth, "REFERENCE_UNAVAILABLE_OR_INVALID")
        before = self.path("current").read_bytes()
        reference.unlink()
        with self.assertRaisesRegex(BindingRejected, "REFERENCE_UNAVAILABLE_OR_INVALID"):
            self.gate.transition(self.auth)
        self.assertEqual(before, self.path("current").read_bytes())
        self.assertFalse(reference.exists())

    def test_only_state_restored(self):
        old = self.path("current").read_bytes()
        self.gate.transition(self.auth)
        self.path("current").write_bytes(old)
        self.reject(self.auth, "STATE_REFERENCE_MISMATCH")

    def test_both_copies_restored_counterexample(self):
        old = self.snapshot()
        self.gate.transition(self.auth)
        for name, data in zip(NAMES[:2], old[:2]):
            self.path(name).write_bytes(data)
        self.assertEqual(self.open().transition(self.auth), "ACCEPT")

    def test_domain_separation_and_shape(self):
        other = index_mac(KEY, SCOPE, A, 1, bytes(32))
        self.reject(dict(self.auth, mac=other), "TRANSITION_NOT_AUTHENTIC")
        self.reject(dict(self.auth, extra=True), "INVALID_TRANSITION_EVIDENCE")


if __name__ == "__main__":
    unittest.main(verbosity=2)
