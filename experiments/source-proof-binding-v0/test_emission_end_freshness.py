"""EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION."""
import tempfile
from pathlib import Path
import unittest
from emission_end_freshness import EndFreshness
from emission_end_anchor import check_closed
from emission_gap import BindingRejected
from test_emission_end_anchor import anchor
from test_emission_gap import record, KEY, SCOPE, CONFIG

# Intentionally reverse lexical order; no temporal interpretation.
A, B = "synthetic-z", "synthetic-a"


class FreshnessTests(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.root = Path(t.name)
        for name in ("current", "reference", "closure-0", "closure-1"):
            (self.root / name).mkdir(mode=0o700)
        self.gate = self.open(True)
        self.ra = [record(i, epoch=A) for i in range(1, 5)]
        self.rb = [record(i, epoch=B) for i in range(1, 5)]
        self.aa, self.ab = anchor(4, epoch=A), anchor(4, epoch=B)

    def open(self, initialize=False):
        return EndFreshness(self.root, key=KEY, scope=SCOPE, first=1,
            config=CONFIG, epochs=(A, B), initialize=initialize)

    def snapshot(self):
        return tuple((self.root / n / "state.json").read_bytes()
                     for n in ("current", "reference", "closure-0", "closure-1"))

    def advance(self):
        self.gate.transition(expected=A, target=B)

    def test_active(self):
        self.assertEqual(self.gate.accept(self.ra, self.aa), "ACCEPT")

    def test_idempotent(self):
        self.gate.accept(self.ra, self.aa)
        before = self.snapshot()
        self.assertEqual(self.gate.accept(self.ra, self.aa), "IDEMPOTENT")
        self.assertEqual(before, self.snapshot())

    def test_explicit_transition(self):
        with self.assertRaisesRegex(BindingRejected, "TERMINAL_EPOCH_NOT_CURRENT"):
            self.gate.accept(self.rb, self.ab)
        self.advance()
        self.assertEqual(self.gate.accept(self.rb, self.ab), "ACCEPT")

    def test_authentic_historical_replay(self):
        self.gate.accept(self.ra, self.aa)
        self.advance()
        self.assertEqual(check_closed(self.ra, self.aa, key=KEY, scope=SCOPE,
            epoch=A, first=1, config=CONFIG), (1, 2, 3, 4))
        before = self.snapshot()
        with self.assertRaisesRegex(BindingRejected, "TERMINAL_EPOCH_NOT_CURRENT"):
            self.gate.accept(self.ra, self.aa)
        self.assertEqual(before, self.snapshot())

    def test_no_reverse_transition(self):
        self.advance()
        before = self.snapshot()
        with self.assertRaisesRegex(BindingRejected, "EPOCH_TRANSITION_NOT_AUTHORIZED"):
            self.gate.transition(expected=B, target=A)
        self.assertEqual(before, self.snapshot())

    def test_restart_and_replay_preserve_state(self):
        self.gate.accept(self.ra, self.aa)
        self.advance()
        self.gate.accept(self.rb, self.ab)
        before = self.snapshot()
        resumed = self.open()
        with self.assertRaisesRegex(BindingRejected, "TERMINAL_EPOCH_NOT_CURRENT"):
            resumed.accept(self.ra, self.aa)
        self.assertEqual(resumed.accept(self.rb, self.ab), "IDEMPOTENT")
        self.assertEqual(before, self.snapshot())

    def test_missing_or_invalid_reference(self):
        self.advance()
        path = self.root / "reference" / "state.json"
        path.write_text("invalid\n")
        with self.assertRaisesRegex(BindingRejected, "REFERENCE_UNAVAILABLE_OR_INVALID"):
            self.gate.accept(self.rb, self.ab)
        path.unlink()
        with self.assertRaisesRegex(BindingRejected, "REFERENCE_UNAVAILABLE_OR_INVALID"):
            self.open()

    def test_only_local_state_restored(self):
        path = self.root / "current" / "state.json"
        old = path.read_bytes()
        self.advance()
        path.write_bytes(old)
        with self.assertRaisesRegex(BindingRejected, "STATE_REFERENCE_MISMATCH"):
            self.open()

    def test_both_local_copies_restored_counterexample(self):
        self.gate.accept(self.ra, self.aa)
        old = self.snapshot()
        self.advance()
        self.gate.accept(self.rb, self.ab)
        for n, data in zip(("current", "reference"), old[:2]):
            (self.root / n / "state.json").write_bytes(data)
        # Both references now consistently identify A again, with no external witness.
        self.assertEqual(self.open().accept(self.ra, self.aa), "IDEMPOTENT")

    def test_stale_session_reads_current(self):
        stale = self.open()
        self.advance()
        with self.assertRaisesRegex(BindingRejected, "TERMINAL_EPOCH_NOT_CURRENT"):
            stale.accept(self.ra, self.aa)
        self.assertEqual(stale.accept(self.rb, self.ab), "ACCEPT")


if __name__ == "__main__":
    unittest.main(verbosity=2)
