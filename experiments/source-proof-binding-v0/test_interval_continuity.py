"""EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION.
Synthetic continuity tests; proof verification mocked, no new proof.
"""
import copy
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

from interval_continuity import ContinuitySession, WIDTH
from interval_coverage import accept_interval, PERIOD, COUNT
from trusted_time import TrustedTimeUnified, receipt_mac, BindingRejected
from test_persistent_unified import ARTIFACTS, CONFIG, mock_pins, sample
from binding_reference import authorized_digest
from unified import public_inputs

ANCHOR = 19600
TIME_KEY = bytes(reversed(range(32)))


def options(clock, verify):
    return dict(decision_clock=clock, verify=verify, time_key=TIME_KEY,
                max_age_ms=1000, **ARTIFACTS, **CONFIG)


def batch(index, start, scope, offset=0):
    return [(c, {"ingress_ms": t, "mac": receipt_mac(TIME_KEY, scope, c, t)})
            for i in range(COUNT)
            for c in [sample(100000+index*6+i*2, 1000+index*WIDTH+i*PERIOD)]
            for t in [start+i*PERIOD+PERIOD//2+offset]]


class ContinuityTests(unittest.TestCase):
    def setUp(self):
        pins = mock_pins()
        pins.start()
        self.addCleanup(pins.stop)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.state = self.root / "state.json"
        self.clock = Mock(return_value=ANCHOR+400)
        self.verify = Mock(return_value=True)
        self.session = self.open(initialize=True)
        with self.session._stage() as stage:
            self.scope = stage._scope

    def open(self, anchor=ANCHOR, **extra):
        return ContinuitySession(state_dir=self.root, anchor=anchor,
                                 **options(self.clock, self.verify), **extra)

    def inputs(self, idx, start=None, offset=0):
        start = ANCHOR+idx*WIDTH if start is None else start
        self.clock.return_value = start+400
        return batch(idx, start, self.scope, offset)

    def accept(self, idx, offset=0, session=None):
        b = self.inputs(idx, offset=offset)
        result = (session or self.session).accept_next(b, ANCHOR+idx*WIDTH)
        self.assertEqual(result, tuple(authorized_digest(c, **CONFIG) for c,_ in b))
        self.assertEqual([a.args[0] for a in self.verify.call_args_list[-COUNT:]],
                         [public_inputs(d) for d in result])
        return result

    def reject(self, b, start, reason, *, no_callback=False, session=None):
        before = self.state.read_bytes()
        calls = self.verify.call_count
        with self.assertRaisesRegex(BindingRejected, reason):
            (session or self.session).accept_next(b, start)
        self.assertEqual(self.state.read_bytes(), before)
        if no_callback:
            self.assertEqual(self.verify.call_count, calls)

    def test_baseline_accepts_gap(self):
        with tempfile.TemporaryDirectory() as path:
            legacy = TrustedTimeUnified(state_dir=path, initialize=True,
                                        **options(self.clock, self.verify))
            accept_interval(legacy, self.inputs(0), ANCHOR)
            accept_interval(legacy, self.inputs(2), ANCHOR+2*WIDTH)
            self.assertEqual(self.verify.call_count, 6)

    def test_three_contiguous_and_public_inputs(self):
        for i, offset in enumerate((-10, 0, 10)):
            self.accept(i, offset=offset)
        self.assertEqual(self.open()._read(), ((100017, 1800), ANCHOR+3*WIDTH))
        self.assertEqual(self.verify.call_count, 9)
        self.assertEqual(self.state.stat().st_mode & 0o777, 0o600)

    def test_first_anchor(self):
        self.reject(self.inputs(1), ANCHOR+WIDTH, "INTERVAL_GAP", no_callback=True)
        self.reject(self.inputs(0, ANCHOR-1), ANCHOR-1,
                    "INTERVAL_OVERLAP_OR_REPLAY", no_callback=True)

    def test_missing_interval(self):
        self.accept(0)
        self.reject(self.inputs(2), ANCHOR+2*WIDTH, "INTERVAL_GAP", no_callback=True)

    def test_one_ms_gap(self):
        self.accept(0)
        self.reject(self.inputs(1, ANCHOR+WIDTH+1), ANCHOR+WIDTH+1,
                    "INTERVAL_GAP", no_callback=True)

    def test_one_ms_overlap(self):
        self.accept(0)
        self.reject(self.inputs(1, ANCHOR+WIDTH-1), ANCHOR+WIDTH-1,
                    "INTERVAL_OVERLAP_OR_REPLAY", no_callback=True)

    def test_retransmission(self):
        self.accept(0)
        self.reject(self.inputs(0), ANCHOR, "INTERVAL_OVERLAP_OR_REPLAY",
                    no_callback=True)

    def test_reverse_order(self):
        self.accept(0)
        self.accept(1)
        self.reject(self.inputs(0), ANCHOR, "INTERVAL_OVERLAP_OR_REPLAY",
                    no_callback=True)

    def test_invalid_authentication_last_slot(self):
        self.accept(0)
        b = self.inputs(1)
        b[-1][1]["mac"] = "0"*64
        self.reject(b, ANCHOR+WIDTH, "TIME_REFERENCE_NOT_AUTHENTIC")

    def test_source_signature_last_slot(self):
        self.accept(0)
        b = self.inputs(1)
        c, r = b[-1]
        frame = bytearray.fromhex(c["events"][-1]["frame_hex"])
        frame[-1] ^= 1
        c["events"][-1]["frame_hex"] = frame.hex()
        r["mac"] = receipt_mac(TIME_KEY, self.scope, c, r["ingress_ms"])
        self.reject(b, ANCHOR+WIDTH, "REJECTED_SIGNATURE_OR_CAPTURE")

    def test_negative_verifier_and_recovery(self):
        self.accept(0)
        b = self.inputs(1)
        self.verify.side_effect = [True, True, False]
        self.reject(b, ANCHOR+WIDTH, "PROOF_NOT_ACCEPTED")
        self.verify.side_effect = None
        self.accept(1, session=self.open())

    def test_real_process_restart(self):
        self.accept(0)
        code = """
from pathlib import Path
import sys
from unittest.mock import Mock
from test_interval_continuity import ANCHOR, WIDTH, options, batch, mock_pins
from interval_continuity import ContinuitySession
with mock_pins():
    v = Mock(return_value=True)
    s = ContinuitySession(state_dir=Path(sys.argv[1]), anchor=ANCHOR,
                          **options(Mock(return_value=ANCHOR+WIDTH+400), v))
    with s._stage() as stage:
        s.accept_next(batch(1, ANCHOR+WIDTH, stage._scope), ANCHOR+WIDTH)
    assert v.call_count == 3
"""
        subprocess.run([sys.executable, "-B", "-c", code, str(self.root)],
                       cwd=Path(__file__).resolve().parent, check=True, timeout=10)
        self.assertEqual(self.open()._read(), ((100011,1500), ANCHOR+2*WIDTH))

    def test_corruption_and_policy_change(self):
        self.accept(0)
        good = self.state.read_bytes()
        self.state.write_bytes(b"{")
        with self.assertRaisesRegex(BindingRejected, "STATE_MISSING_CORRUPT_OR_INCOMPATIBLE"):
            self.open()
        self.state.write_bytes(good)
        with self.assertRaisesRegex(BindingRejected, "STATE_MISSING_CORRUPT_OR_INCOMPATIBLE"):
            self.open(anchor=ANCHOR+1)

    def test_reject_missing_and_out_of_order_observations(self):
        self.accept(0)
        b = self.inputs(1)
        self.reject(b[:2], ANCHOR+WIDTH, "INCOMPLETE_INTERVAL")
        self.reject([b[1],b[0],b[2]], ANCHOR+WIDTH, "SLOT_MISMATCH")
        self.accept(1)

    def test_precommit_failure(self):
        self.accept(0)
        b = self.inputs(1)
        replace = os.replace
        def fail_outer(src, dest):
            if Path(dest) == self.state:
                raise OSError("synthetic commit failure")
            return replace(src, dest)
        with patch("persistent_unified.os.replace", side_effect=fail_outer):
            self.reject(b, ANCHOR+WIDTH, "STATE_COMMIT_FAILED")
        self.assertEqual(list(self.root.iterdir()), [self.state])
        self.accept(1, session=self.open())

    def test_ambiguous_commit_no_success(self):
        self.accept(0)
        b = self.inputs(1)
        fsync = os.fsync
        st = self.root.stat()
        def fail_outer_dir(fd):
            target = os.fstat(fd)
            if (target.st_dev,target.st_ino)==(st.st_dev,st.st_ino):
                raise OSError("synthetic directory fsync failure")
            fsync(fd)
        with patch("persistent_unified.os.fsync", side_effect=fail_outer_dir):
            with self.assertRaisesRegex(BindingRejected, "STATE_COMMIT_FAILED"):
                self.session.accept_next(b, ANCHOR+WIDTH)
        reopened = self.open()
        self.assertEqual(reopened._read(), ((100011,1500), ANCHOR+2*WIDTH))
        self.reject(b, ANCHOR+WIDTH, "INTERVAL_OVERLAP_OR_REPLAY",
                    session=reopened, no_callback=True)

if __name__ == "__main__":
    print(__doc__, flush=True)
    unittest.main(verbosity=2)
