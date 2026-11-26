"""EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION."""
import copy
import hashlib
import unittest
from test_temporal_gate import sample, CONFIG
from emission_gap import check_sequence, index_mac, authorized_digest, BindingRejected

KEY = hashlib.sha256(b"TAG synthetic index authority fixture").digest()
SCOPE, EPOCH = "synthetic-observation-scope", "synthetic-epoch-1"

def record(index, epoch=EPOCH, key=KEY):
    capture = sample(100000 + index*2, 1000 + index*100)
    digest = authorized_digest(capture, **CONFIG)
    return capture, {"epoch": epoch, "index": index,
        "mac": index_mac(key, SCOPE, epoch, index, digest)}

def check(records):
    return check_sequence(records, key=KEY, scope=SCOPE, epoch=EPOCH,
                          first=1, config=CONFIG)

class EmissionTests(unittest.TestCase):
    def setUp(self):
        self.records = [record(i) for i in (1, 2, 3, 4)]

    def test_consecutive(self):
        self.assertEqual(check(self.records), (1, 2, 3, 4))

    def test_numbered_message_omitted(self):
        with self.assertRaisesRegex(BindingRejected, "EMISSION_GAP"):
            check([self.records[i] for i in (0, 2, 3)])

    def test_wrong_index_authentication(self):
        changed = copy.deepcopy(self.records)
        changed[1][1]["index"] = 5
        with self.assertRaisesRegex(BindingRejected, "INDEX_NOT_AUTHENTIC"):
            check(changed)
        with self.assertRaisesRegex(BindingRejected, "INDEX_NOT_AUTHENTIC"):
            check([record(1, key=b"X"*32)])

    def test_authenticated_wrong_epoch(self):
        with self.assertRaisesRegex(BindingRejected, "EPOCH_MISMATCH"):
            check([record(1, epoch="synthetic-epoch-2")])

    def test_index_bound_to_observation(self):
        with self.assertRaisesRegex(BindingRejected, "INDEX_NOT_AUTHENTIC"):
            check([(self.records[1][0], self.records[0][1])])

    def test_duplicate(self):
        with self.assertRaisesRegex(BindingRejected, "INDEX_REPLAY_OR_REGRESSION"):
            check([self.records[0], self.records[0]])

    def test_missing_prefix_with_anchor(self):
        with self.assertRaisesRegex(BindingRejected, "EMISSION_GAP"):
            check(self.records[1:])

    def test_unnumbered_physical_event_indistinguishable(self):
        history_a = list(self.records)
        history_b = [*self.records[:2], "hypothetical physical event with no record",
                     *self.records[2:]]
        visible = lambda history: [x for x in history if isinstance(x, tuple)]
        self.assertEqual(visible(history_a), visible(history_b))
        self.assertEqual(check(visible(history_a)), check(visible(history_b)))

    def test_unanchored_tail_indistinguishable(self):
        self.assertEqual(check(self.records[:3]), (1, 2, 3))
        # No authenticated expected final index: absence of a fourth record
        # does not distinguish a stopped source from a missing terminal record.

if __name__ == "__main__":
    unittest.main(verbosity=2)
