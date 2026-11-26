"""EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION."""
import copy
import os
from pathlib import Path
import stat
import tempfile
import unittest

from emission_end_consistency import EndConsistency
from emission_end_anchor import check_closed
from test_emission_end_anchor import anchor
from test_emission_gap import record, KEY, SCOPE, EPOCH, CONFIG
from emission_gap import index_mac, authorized_digest, BindingRejected


class ConsistencyTests(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory()
        self.addCleanup(self.workspace.cleanup)
        self.root = Path(self.workspace.name)
        self.records = [record(i) for i in range(1, 5)]

    def session(self, label="primary", *, scope=SCOPE, epoch=EPOCH,
                first=1, initialize=True):
        directory = self.root / label
        if initialize:
            directory.mkdir(mode=0o700)
        return EndConsistency(directory, key=KEY, scope=scope, epoch=epoch,
                              first=first, config=CONFIG, initialize=initialize)

    def test_first_valid_terminal_is_accepted(self):
        gate = self.session()
        self.assertEqual(gate.accept(self.records, anchor()), "ACCEPT")
        f = self.root / "primary" / "state.json"
        self.assertEqual(stat.S_IMODE(os.stat(f).st_mode), 0o600)
        self.assertEqual(len(f.read_bytes()), 65)

    def test_identical_repetition_is_idempotent(self):
        gate = self.session()
        self.assertEqual(gate.accept(self.records, anchor()), "ACCEPT")
        f = self.root / "primary" / "state.json"
        original = f.read_bytes()
        self.assertEqual(gate.accept(self.records, anchor()), "IDEMPOTENT")
        self.assertEqual(f.read_bytes(), original)

    def test_two_individually_authentic_ends_conflict(self):
        gate = self.session()
        first_records = self.records[:3]
        self.assertEqual(check_closed(first_records, anchor(3), key=KEY,
                         scope=SCOPE, epoch=EPOCH, first=1, config=CONFIG),
                         (1, 2, 3))
        self.assertEqual(check_closed(self.records, anchor(4), key=KEY,
                         scope=SCOPE, epoch=EPOCH, first=1, config=CONFIG),
                         (1, 2, 3, 4))
        self.assertEqual(gate.accept(first_records, anchor(3)), "ACCEPT")
        with self.assertRaisesRegex(BindingRejected, "TERMINAL_CLOSURE_CONFLICT"):
            gate.accept(self.records, anchor(4))

    def test_reverse_conflict_also_preserves_first(self):
        gate = self.session()
        self.assertEqual(gate.accept(self.records, anchor(4)), "ACCEPT")
        with self.assertRaisesRegex(BindingRejected, "TERMINAL_CLOSURE_CONFLICT"):
            gate.accept(self.records[:3], anchor(3))
        self.assertEqual(gate.accept(self.records, anchor(4)), "IDEMPOTENT")

    def test_unauthenticated_mutation_cannot_rewrite_reference(self):
        gate = self.session()
        self.assertEqual(gate.accept(self.records, anchor(4)), "ACCEPT")
        f = self.root / "primary" / "state.json"
        original = f.read_bytes()
        forged = copy.copy(anchor(4))
        forged["final"] = 3
        with self.assertRaisesRegex(BindingRejected, "END_NOT_AUTHENTIC"):
            gate.accept(self.records[:3], forged)
        with self.assertRaisesRegex(BindingRejected, "END_NOT_AUTHENTIC"):
            gate.accept(self.records, anchor(4, scope="other-scope"))
        self.assertEqual(f.read_bytes(), original)

    def test_contexts_are_separately_enrolled(self):
        other = "other-synthetic-scope"
        alternative = []
        for i, (capture, _) in enumerate(self.records, start=1):
            digest = authorized_digest(capture, **CONFIG)
            alternative.append((capture, {
                "epoch": EPOCH, "index": i,
                "mac": index_mac(KEY, other, EPOCH, i, digest)}))
        a = self.session()
        b = self.session("scope2", scope=other)
        c = self.session("epoch2", epoch="synthetic-epoch-2")
        e = self.session("start2", first=2)
        self.assertEqual(a.accept(self.records, anchor(4)), "ACCEPT")
        self.assertEqual(b.accept(alternative, anchor(4, scope=other)), "ACCEPT")
        self.assertEqual(c.accept([record(i, epoch="synthetic-epoch-2")
                         for i in range(1, 5)],
                         anchor(4, epoch="synthetic-epoch-2")), "ACCEPT")
        self.assertEqual(e.accept(self.records[1:3], anchor(3, first=2)), "ACCEPT")

    def test_restart_after_conflict_retains_original(self):
        gate = self.session()
        self.assertEqual(gate.accept(self.records[:3], anchor(3)), "ACCEPT")
        f = self.root / "primary" / "state.json"
        original = f.read_bytes()
        with self.assertRaisesRegex(BindingRejected, "TERMINAL_CLOSURE_CONFLICT"):
            gate.accept(self.records, anchor(4))
        self.assertEqual(f.read_bytes(), original)
        resumed = self.session(initialize=False)
        self.assertEqual(resumed.accept(self.records[:3], anchor(3)), "IDEMPOTENT")
        with self.assertRaisesRegex(BindingRejected, "TERMINAL_CLOSURE_CONFLICT"):
            resumed.accept(self.records, anchor(4))
        self.assertEqual(f.read_bytes(), original)

    def test_missing_or_malformed_persistent_reference_fails_closed(self):
        gate = self.session()
        self.assertEqual(gate.accept(self.records, anchor(4)), "ACCEPT")
        f = self.root / "primary" / "state.json"
        f.write_text("untrusted replacement\n")
        with self.assertRaisesRegex(BindingRejected, "REFERENCE_UNAVAILABLE_OR_INVALID"):
            self.session(initialize=False)
        f.unlink()
        with self.assertRaisesRegex(BindingRejected, "REFERENCE_UNAVAILABLE_OR_INVALID"):
            self.session(initialize=False)

    def test_missing_anchor_does_not_initialize_terminal(self):
        gate = self.session()
        f = self.root / "primary" / "state.json"
        original = f.read_bytes()
        with self.assertRaisesRegex(BindingRejected, "END_ANCHOR_MISSING"):
            gate.accept(self.records, None)
        self.assertEqual(f.read_bytes(), original)

    def test_false_but_consistent_terminal_remains_indistinguishable(self):
        # Hidden fourth emission is not available to either local verifier.
        honest_history = self.records[:3]
        false_history = self.records
        honest_visible = honest_history
        false_visible = false_history[:3]
        self.assertNotEqual(honest_history, false_history)
        self.assertEqual((honest_visible, anchor(3)), (false_visible, anchor(3)))
        honest = self.session("honest")
        false = self.session("false")
        self.assertEqual(honest.accept(honest_visible, anchor(3)), "ACCEPT")
        self.assertEqual(false.accept(false_visible, anchor(3)), "ACCEPT")
        self.assertEqual((self.root / "honest" / "state.json").read_bytes(),
                         (self.root / "false" / "state.json").read_bytes())


if __name__ == "__main__":
    unittest.main(verbosity=2)
