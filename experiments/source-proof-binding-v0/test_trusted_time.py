"""EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION.

Only synthetic test keys, fixture capture and mock proof verification.
"""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from trusted_time import TrustedTimeUnified, receipt_mac, BindingRejected
from test_persistent_unified import ARTIFACTS, CONFIG, mock_pins, sample
from binding_reference import authorized_digest
from unified import public_inputs

TIME_KEY = bytes(reversed(range(32)))  # Public synthetic authority key
NOW = 20000
AGE = 1000


class TrustedTimeTests(unittest.TestCase):
    def setUp(self):
        pins = mock_pins()
        pins.start()
        self.addCleanup(pins.stop)
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.directory = Path(tmp.name)
        self.file = self.directory / "state.json"
        self.verify = Mock(return_value=True)
        self.clock = Mock(return_value=NOW)
        self.session = self.open_session(initialize=True)

    def open_session(self, **extra):
        return TrustedTimeUnified(state_dir=self.directory, verify=self.verify,
                                  time_key=TIME_KEY, decision_clock=self.clock,
                                  max_age_ms=AGE, **ARTIFACTS, **CONFIG, **extra)

    def witness(self, capture, ingress=NOW-100, key=TIME_KEY, scope=None):
        # Simulated separate ingress authority; no verifier auto-stamping.
        return {"ingress_ms": ingress,
                "mac": receipt_mac(key, self.session._scope if scope is None else scope,
                                   capture, ingress)}

    def blocked(self, reason, capture, receipt=None, session=None):
        before = self.file.read_bytes()
        calls = self.verify.call_count
        with self.assertRaisesRegex(BindingRejected, reason):
            (session or self.session).accept(capture, receipt=receipt)
        self.assertEqual(self.file.read_bytes(), before)
        self.assertEqual(self.verify.call_count, calls)

    def test_recent_preserves_proof_inputs(self):
        c = sample()
        self.assertEqual(self.session.accept(c, receipt=self.witness(c)),
                         authorized_digest(c, **CONFIG))
        self.verify.assert_called_once_with(public_inputs(authorized_digest(c, **CONFIG)),
                                           ARTIFACTS["proof"], ARTIFACTS["vk"])

    def test_half_open_window_and_future(self):
        c = sample()
        for stamp, reason in ((NOW-AGE, "STALE"), (NOW-AGE-1, "STALE"),
                              (NOW+1, "IN_FUTURE")):
            self.blocked(reason, c, self.witness(c, stamp))
        self.session.accept(c, receipt=self.witness(c, NOW-AGE+1))
        nxt = sample(100002, 1001)
        self.session.accept(nxt, receipt=self.witness(nxt, NOW))
        self.assertEqual(self.verify.call_count, 2)

    def test_rewritten_capture_receiver_metadata_and_age(self):
        c = sample()
        receipt = self.witness(c)
        for edit in ("receiver", "age", "source_time"):
            altered = copy.deepcopy(c)
            if edit == "receiver":
                altered["decision_received_at_ms"] += 500
                for e in altered["events"]:
                    e["received_at_ms"] += 500
            elif edit == "age":
                altered["max_age_ms"] += 1000
            else:
                altered["claimed_observation_ms"] = NOW
            self.blocked("NOT_AUTHENTIC", altered, receipt)
        self.session.accept(c, receipt=receipt)

    def test_resigned_frame_cannot_reuse_reference(self):
        c = sample()
        changed = sample(100002, 1001)
        self.blocked("NOT_AUTHENTIC", changed, self.witness(c))
        self.session.accept(c, receipt=self.witness(c))

    def test_tampered_reference_and_wrong_authority_scope(self):
        c = sample()
        r = self.witness(c)
        self.blocked("NOT_AUTHENTIC", c, {**r, "ingress_ms": NOW})
        self.blocked("NOT_AUTHENTIC", c, self.witness(c, key=bytes(range(32))))
        self.blocked("NOT_AUTHENTIC", c, self.witness(c, scope="wrong-scope"))

    def test_missing_invalid_reference(self):
        c = sample()
        r = self.witness(c)
        for invalid in (None, {}, {**r, "ingress_ms": True}, {**r, "ingress_ms": -1},
                        {**r, "ingress_ms": 2**63}, {**r, "mac": "é"*64},
                        {**r, "extra": 1}):
            self.blocked("INVALID_TIME_REFERENCE", c, invalid)

    def test_decision_clock_failure(self):
        c = sample()
        r = self.witness(c)
        for value in (None, True, -1, 2**63, float("nan")):
            self.clock.return_value = value
            self.blocked("CLOCK_UNAVAILABLE", c, r)
        self.clock.side_effect = RuntimeError("test unavailable")
        self.blocked("CLOCK_UNAVAILABLE", c, r)

    def test_persisted_replay_even_with_new_ingress_receipt(self):
        c = sample()
        self.session.accept(c, receipt=self.witness(c))
        reopened = self.open_session()
        self.blocked("CROSS_CAPTURE_REPLAY", c, self.witness(c, NOW), reopened)
        nxt = sample(100002, 1001)
        reopened.accept(nxt, receipt=self.witness(nxt))
        self.assertEqual(self.verify.call_count, 2)

    def test_rejected_high_stamp_does_not_poison_state(self):
        c = sample()
        self.session.accept(c, receipt=self.witness(c))
        high = sample(900000, 9000)
        self.blocked("STALE", high, self.witness(high, NOW-AGE))
        nxt = sample(100002, 1001)
        self.session.accept(nxt, receipt=self.witness(nxt))

    def test_proof_failure_still_does_not_commit(self):
        c = sample()
        before = self.file.read_bytes()
        self.verify.return_value = False
        with self.assertRaisesRegex(BindingRejected, "PROOF_NOT_ACCEPTED"):
            self.session.accept(c, receipt=self.witness(c))
        self.assertEqual(self.file.read_bytes(), before)
        self.verify.return_value = True
        self.session.accept(c, receipt=self.witness(c))

    def test_ingress_not_sensor_capture_time_limitation(self):
        # An old physical observation could arrive now for the first time;
        # the fixture's signed ticks are not a trustworthy wall-clock.
        c = sample(1, 1)
        self.session.accept(c, receipt=self.witness(c, NOW))
        self.verify.assert_called_once()

    def test_same_key_rejected(self):
        with self.assertRaisesRegex(BindingRejected, "TIME_KEY_NOT_SEPARATE"):
            TrustedTimeUnified(state_dir=self.directory, verify=self.verify,
                               time_key=bytes(range(32)), decision_clock=self.clock,
                               max_age_ms=AGE, **ARTIFACTS, **CONFIG)


if __name__ == "__main__":
    print("EXPERIMENTAL | SYNTHETIC_ONLY | A0_SYNTHETIC | NOT VALIDATION OR PRODUCTION AUTHORIZATION", flush=True)
    unittest.main(verbosity=2)
