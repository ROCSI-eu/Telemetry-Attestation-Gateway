"""EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION."""
import unittest
from test_emission_gap import record, KEY, SCOPE, EPOCH, CONFIG, check
from emission_gap import index_mac, authorized_digest, BindingRejected
from emission_end_anchor import end_mac, check_closed

def anchor(final=4, epoch=EPOCH, scope=SCOPE, key=KEY, first=1):
    return {"epoch": epoch, "final": final,
            "mac": end_mac(key, scope, epoch, first, final)}

def closed(records, end):
    return check_closed(records, end, key=KEY, scope=SCOPE, epoch=EPOCH,
                        first=1, config=CONFIG)

class EndTests(unittest.TestCase):
    def setUp(self):
        self.records = [record(i) for i in (1, 2, 3, 4)]

    def test_complete(self):
        self.assertEqual(closed(self.records, anchor()), (1, 2, 3, 4))

    def test_missing_suffix(self):
        for n in (1, 2, 3):
            with self.subTest(n=n):
                self.assertEqual(check(self.records[:n]), tuple(range(1, n+1)))
                with self.assertRaisesRegex(BindingRejected, "TERMINAL_EMISSION_GAP"):
                    closed(self.records[:n], anchor())

    def test_absent(self):
        with self.assertRaisesRegex(BindingRejected, "END_ANCHOR_MISSING"):
            closed(self.records, None)

    def test_modified(self):
        changed = anchor()
        changed["final"] = 3
        with self.assertRaisesRegex(BindingRejected, "END_NOT_AUTHENTIC"):
            closed(self.records[:3], changed)

    def test_wrong_key(self):
        with self.assertRaisesRegex(BindingRejected, "END_NOT_AUTHENTIC"):
            closed(self.records, anchor(key=b"X"*32))

    def test_wrong_epoch(self):
        with self.assertRaisesRegex(BindingRejected, "END_EPOCH_MISMATCH"):
            closed(self.records, anchor(epoch="synthetic-epoch-2"))

    def test_wrong_scope_or_start(self):
        for end in (anchor(scope="other-synthetic-scope"), anchor(first=2)):
            with self.assertRaisesRegex(BindingRejected, "END_NOT_AUTHENTIC"):
                closed(self.records, end)

    def test_wrong_mac_domain(self):
        end = anchor()
        digest = authorized_digest(self.records[-1][0], **CONFIG)
        end["mac"] = index_mac(KEY, SCOPE, EPOCH, 4, digest)
        with self.assertRaisesRegex(BindingRejected, "END_NOT_AUTHENTIC"):
            closed(self.records, end)

    def test_conflicting_final(self):
        with self.assertRaisesRegex(BindingRejected, "END_INDEX_CONFLICT"):
            closed(self.records, anchor(3))

    def test_invalid_final(self):
        for final in (0, True, 2**64):
            with self.assertRaisesRegex(BindingRejected, "INVALID_END_ANCHOR"):
                closed(self.records, {"epoch": EPOCH, "final": final, "mac": "0"*64})

    def test_internal_gap_still_rejected(self):
        with self.assertRaisesRegex(BindingRejected, "EMISSION_GAP"):
            closed([self.records[0], *self.records[2:]], anchor())

    def test_unnumbered_event(self):
        a = self.records
        b = [*a[:2], "hypothetical unnumbered physical event", *a[2:]]
        visible = lambda h: [x for x in h if isinstance(x, tuple)]
        self.assertEqual(visible(a), visible(b))
        self.assertEqual(closed(visible(a), anchor()), closed(visible(b), anchor()))

    def test_authentic_false_end(self):
        # Honest stop after 3 vs authority falsely declaring 3 after emitting 4.
        honest_history = self.records[:3]
        false_history = self.records[:4]
        self.assertNotEqual(honest_history, false_history)
        visible_honest = (honest_history, anchor(3))
        visible_false = (false_history[:3], anchor(3))
        self.assertEqual(visible_honest, visible_false)
        self.assertEqual(closed(*visible_honest), (1, 2, 3))
        self.assertEqual(closed(*visible_false), (1, 2, 3))

if __name__ == "__main__":
    unittest.main(verbosity=2)
