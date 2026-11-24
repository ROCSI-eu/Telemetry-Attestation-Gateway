"""Synthetic fixture-only QA, no SITL, ZKP, network, or real signing key."""
import copy
import hashlib
import json
import unittest

from temporal_gate import TemporalGate, BindingRejected, REFERENCE
from binding_reference import authorized_digest, parser

CASES = {c["name"]: c for c in json.loads(
    (REFERENCE.parent / "mavlink-normalization-v0/fixtures.json").read_text()
)["captures"]}
KEY = bytes(range(32))
POLICY = {"slot": "1:1:7", "alias": "qa-synthetic-source", "active": True,
          "key_fingerprint": hashlib.sha256(KEY).hexdigest()}
CONFIG = dict(verifier_key_hex=KEY.hex(), enrollment=POLICY,
              requested_alias=POLICY["alias"])


def sample(stamp=100000, boot=1000):
    """Derive a deterministic synthetic observation using existing test key."""
    capture = copy.deepcopy(CASES["signed-valid"])
    for i, event in enumerate(capture["events"]):
        frame = bytearray.fromhex(event["frame_hex"])
        n = frame[1]
        msg_id = int.from_bytes(frame[7:10], "little")
        if msg_id == 33:
            frame[10:14] = boot.to_bytes(4, "little")
            crc = parser.mavlink_crc(bytes(frame[1:10]), bytes(frame[10:10+n]), 104)
            frame[10+n:12+n] = crc.to_bytes(2, "little")
        frame[-12:-6] = (stamp+i).to_bytes(6, "little")
        frame[-6:] = hashlib.sha256(KEY + frame[:-6]).digest()[:6]
        event["frame_hex"] = frame.hex()
    return capture


class TemporalTests(unittest.TestCase):
    def setUp(self):
        self.gate = TemporalGate(**CONFIG)

    def test_first_and_next_preserve_authorized_digest(self):
        for c in (sample(), sample(100002, 1001)):
            self.assertEqual(self.gate.accept(c), authorized_digest(c, **CONFIG))

    def test_exact_replay_with_rewritten_receiver_metadata(self):
        c = sample()
        self.gate.accept(c)
        replay = copy.deepcopy(c)
        replay["decision_received_at_ms"] += 500
        for e in replay["events"]:
            e["received_at_ms"] += 500
        self.assertEqual(authorized_digest(c, **CONFIG),
                         authorized_digest(replay, **CONFIG))
        with self.assertRaisesRegex(BindingRejected, "CROSS_CAPTURE_REPLAY_OR_REGRESSION"):
            self.gate.accept(replay)

    def test_older_valid_capture_and_equal_last_signed_timestamp(self):
        self.gate.accept(sample())
        for t in (99998, 100001):
            c = sample(t, 1000)
            authorized_digest(c, **CONFIG)
            with self.assertRaisesRegex(BindingRejected, "CROSS_CAPTURE_REPLAY_OR_REGRESSION"):
                self.gate.accept(c)

    def test_new_signing_time_cannot_hide_boot_regression(self):
        self.gate.accept(sample())
        c = sample(100002, 999)
        authorized_digest(c, **CONFIG)
        with self.assertRaisesRegex(BindingRejected, "CROSS_CAPTURE_BOOT_REGRESSION"):
            self.gate.accept(c)
        # Failed boot check must not consume the signed timestamp.
        self.gate.accept(sample(100002, 1001))

    def test_invalid_high_timestamp_does_not_poison_watermark(self):
        self.gate.accept(sample())
        bad = sample(900000, 9000)
        f = bytearray.fromhex(bad["events"][-1]["frame_hex"])
        f[-1] ^= 1
        bad["events"][-1]["frame_hex"] = f.hex()
        with self.assertRaisesRegex(BindingRejected, "REJECTED_SIGNATURE_OR_CAPTURE"):
            self.gate.accept(bad)
        self.gate.accept(sample(100002, 1001))

    def test_revoked_policy_cannot_start_temporal_state(self):
        revoked = TemporalGate(**{**CONFIG, "enrollment": {**POLICY, "active": False}})
        with self.assertRaisesRegex(BindingRejected, "REJECTED_NOT_ENROLLED_OR_REVOKED"):
            revoked.accept(sample())
        self.assertIsNone(revoked._watermark)

    def test_capture_metadata_cannot_reset_session_state(self):
        c = sample()
        self.gate.accept(c)
        replay = copy.deepcopy(c)
        replay.update({"watermark": None, "session_id": "new", "test_trust_store": {}})
        with self.assertRaisesRegex(BindingRejected, "CROSS_CAPTURE_REPLAY_OR_REGRESSION"):
            self.gate.accept(replay)

    def test_restart_and_resigning_limitations_explicit(self):
        c = sample()
        self.gate.accept(c)
        # New instance has no persisted history; a fresh signature over the
        # same observation payload is not detectable as a semantic duplicate.
        self.assertEqual(TemporalGate(**CONFIG).accept(c), authorized_digest(c, **CONFIG))
        self.gate.accept(sample(100002, 1000))


if __name__ == "__main__":
    unittest.main(verbosity=2)
