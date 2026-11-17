#!/usr/bin/env python3
"""Offline/fake-socket tests; no UDP transmission or SITL invocation."""
from __future__ import annotations

import json
from pathlib import Path
import socket
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "mavlink-normalization-v0"))
import mavlink_normalize as normalizer  # noqa: E402
import sitl_receive as intake  # noqa: E402

DOC = json.loads((ROOT / "mavlink-normalization-v0/fixtures.json").read_text())
CAPTURES = {x["name"]: x for x in DOC["captures"]}
GPI = bytes.fromhex(CAPTURES["unsigned-consistent"]["events"][0]["frame_hex"])
VFR = bytes.fromhex(CAPTURES["unsigned-consistent"]["events"][1]["frame_hex"])
SIGNED = bytes.fromhex(CAPTURES["signed-valid"]["events"][0]["frame_hex"])


class Clock:
    def __init__(self, step=0.02):
        self.now = 0.0
        self.step = step

    def __call__(self):
        self.now += self.step
        return self.now


class FakeReceiver:
    def __init__(self, packets, *, bind_error=False):
        self.packets = iter(packets)
        self.bind_error = bind_error
        self.bound = None
        self.timeout = None
        self.recv_lengths = []
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.closed = True

    def bind(self, address):
        if self.bind_error:
            raise OSError("simulated bind failure")
        self.bound = address

    def settimeout(self, value):
        self.timeout = value

    def recvfrom(self, length):
        self.recv_lengths.append(length)
        try:
            item = next(self.packets)
        except StopIteration:
            raise socket.timeout()
        if item is None:
            raise socket.timeout()
        if isinstance(item, tuple):
            return item
        return item, ("127.0.0.1", 44001)


def capture_with(packets, *, step=0.02, bind_error=False):
    receiver = FakeReceiver(packets, bind_error=bind_error)
    def factory(family, kind):
        assert family == socket.AF_INET and kind == socket.SOCK_DGRAM
        return receiver
    return receiver, lambda: intake.receive_capture(socket_factory=factory, clock=Clock(step))


def adjust_gpi(*, sys_id=None, boot_ms=None):
    frame = bytearray(GPI)
    if sys_id is not None:
        frame[5] = sys_id
    if boot_ms is not None:
        frame[10:14] = boot_ms.to_bytes(4, "little")
    crc = normalizer.mavlink_crc(bytes(frame[1:10]), bytes(frame[10:-2]), 104)
    frame[-2:] = crc.to_bytes(2, "little")
    return bytes(frame)


class ReceiveOnlyTests(unittest.TestCase):
    def test_two_observations_pinned_loopback_no_send(self):
        receiver, collect = capture_with([VFR + GPI, GPI])
        capture = collect()
        self.assertEqual(receiver.bound, ("127.0.0.1", 14550))
        self.assertEqual(receiver.timeout, 0.2)
        self.assertTrue(receiver.closed)
        self.assertTrue(all(n == 1201 for n in receiver.recv_lengths))
        self.assertEqual(len(capture["events"]), 2)
        self.assertEqual(normalizer.evaluate_capture(capture)["status"], "NORMALIZED")
        self.assertEqual(normalizer.evaluate_capture(capture)["source"]["trust"], "UNSIGNED")

    def test_unsigned_never_promoted(self):
        _, collect = capture_with([GPI, GPI])
        self.assertEqual(normalizer.evaluate_capture(collect())["source"]["trust"], "UNSIGNED")

    def test_signed_without_key_remains_unknown(self):
        _, collect = capture_with([SIGNED, SIGNED])
        self.assertEqual(normalizer.evaluate_capture(collect())["source"]["trust"], "UNKNOWN")

    def test_no_primary_source_times_out(self):
        _, collect = capture_with([VFR], step=0.5)
        with self.assertRaisesRegex(intake.ReceiveError, "RECEIVE_TIMEOUT"):
            collect()

    def test_partial_capture_source_loss(self):
        _, collect = capture_with([GPI], step=0.5)
        with self.assertRaisesRegex(intake.ReceiveError, "SOURCE_LOSS"):
            collect()

    def test_mixed_sources_fail_normalizer(self):
        _, collect = capture_with([GPI, adjust_gpi(sys_id=2)])
        self.assertEqual(normalizer.evaluate_capture(collect())["reason_code"], "MIXED_SOURCE")

    def test_boot_time_reset_fail_normalizer(self):
        _, collect = capture_with([GPI, adjust_gpi(boot_ms=3)])
        self.assertEqual(normalizer.evaluate_capture(collect())["reason_code"], "SOURCE_TIME_REGRESSION_UNSUPPORTED")

    def test_invalid_crc_and_unsupported_wire(self):
        broken = bytearray(GPI)
        broken[-1] ^= 1
        for packet, code in [(bytes(broken), "BAD_CRC"), (b"\\xfe" + GPI[1:], "UNSUPPORTED_MAVLINK_PROTOCOL"), (GPI[:-1], "TRUNCATED_MAVLINK_FRAME"), (b"x"*1201, "DATAGRAM_LENGTH_REJECTED")]:
            with self.subTest(code=code):
                with self.assertRaises(intake.ReceiveError) as ctx:
                    intake.observation_frames(packet)
                self.assertEqual(ctx.exception.code, code)

    def test_nonlocal_sender_and_bind_failure_fail_closed(self):
        _, collect = capture_with([(GPI, ("192.0.2.1", 40000))])
        with self.assertRaisesRegex(intake.ReceiveError, "NON_LOOPBACK_SOURCE_REJECTED"):
            collect()
        _, collect = capture_with([], bind_error=True)
        with self.assertRaisesRegex(intake.ReceiveError, "RECEIVER_SOCKET_UNAVAILABLE"):
            collect()

    def test_no_outgoing_socket_interface(self):
        import inspect
        source = inspect.getsource(intake)
        for forbidden in ("sendto(", ".send(", ".connect(", "subprocess", "Popen(", "socketserver"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
