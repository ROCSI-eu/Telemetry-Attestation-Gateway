#!/usr/bin/env python3
"""Bounded receive-only synthetic ArduPilot SITL observation intake.

EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC
NOT VALIDATION OR PRODUCTION AUTHORIZATION
No send, connect, request, forwarding, file persistence, or source authentication.
"""
from __future__ import annotations

import socket
import sys
import time
from pathlib import Path
from typing import Any, Callable

MAVLINK_DIR = Path(__file__).resolve().parents[1] / "mavlink-normalization-v0"
if str(MAVLINK_DIR) not in sys.path:
    sys.path.insert(0, str(MAVLINK_DIR))
from mavlink_normalize import (  # noqa: E402
    GLOBAL_POSITION_INT, MAVLINK2_MAGIC, MAVLINK_IFLAG_SIGNED,
    NormalizationError, parse_mavlink2_frame,
)

LISTEN_IP = "127.0.0.1"
LISTEN_PORT = 14550
MAX_DATAGRAM_BYTES = 1200
MAX_DATAGRAMS = 256
MAX_OBSERVATIONS = 2
DEADLINE_SECONDS = 3.0
RECEIVER_MAX_AGE_MS = 1500
PINNED_PROFILE = "ArduPilot Copter-4.7.1 / MAVLink2 common.xml / dialect 0"


class ReceiveError(ValueError):
    """Redacted typed failure without frame bytes, source IDs, or positions."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def observation_frames(datagram: bytes) -> list[bytes]:
    """Skip unrelated MAVLink2 messages; accept only complete GPI observations."""
    if not datagram or len(datagram) > MAX_DATAGRAM_BYTES:
        raise ReceiveError("DATAGRAM_LENGTH_REJECTED")
    offset = 0
    observations: list[bytes] = []
    while offset < len(datagram):
        remaining = datagram[offset:]
        if len(remaining) < 12:
            raise ReceiveError("TRUNCATED_MAVLINK_FRAME")
        if remaining[0] != MAVLINK2_MAGIC:
            raise ReceiveError("UNSUPPORTED_MAVLINK_PROTOCOL")
        payload_len = remaining[1]
        length = 12 + payload_len + (13 if remaining[2] & MAVLINK_IFLAG_SIGNED else 0)
        if len(remaining) < length:
            raise ReceiveError("TRUNCATED_MAVLINK_FRAME")
        frame = remaining[:length]
        offset += length
        if int.from_bytes(frame[7:10], "little") != GLOBAL_POSITION_INT:
            continue
        try:
            # Empty trust store means signed observations remain UNKNOWN, not trusted.
            parse_mavlink2_frame(frame, {})
        except NormalizationError as error:
            raise ReceiveError(error.code) from None
        observations.append(frame)
    return observations


def receive_capture(
    *,
    socket_factory: Callable[..., Any] = socket.socket,
    clock: Callable[[], float] = time.monotonic,
) -> dict[str, Any]:
    """Collect two synthetic observations privately, only on loopback UDP."""
    started = clock()
    events: list[dict[str, Any]] = []
    datagrams = 0
    try:
        with socket_factory(socket.AF_INET, socket.SOCK_DGRAM) as receiver:
            receiver.bind((LISTEN_IP, LISTEN_PORT))
            receiver.settimeout(0.2)
            while len(events) < MAX_OBSERVATIONS:
                if clock() - started >= DEADLINE_SECONDS:
                    raise ReceiveError("SOURCE_LOSS" if events else "RECEIVE_TIMEOUT")
                if datagrams >= MAX_DATAGRAMS:
                    raise ReceiveError("DATAGRAM_BUDGET_EXCEEDED")
                try:
                    packet, address = receiver.recvfrom(MAX_DATAGRAM_BYTES + 1)
                except socket.timeout:
                    continue
                datagrams += 1
                if not isinstance(address, tuple) or address[0] != LISTEN_IP:
                    raise ReceiveError("NON_LOOPBACK_SOURCE_REJECTED")
                for frame in observation_frames(packet):
                    events.append({
                        "received_at_ms": max(0, int((clock() - started) * 1000)),
                        "frame_hex": frame.hex(),
                    })
                    if len(events) == MAX_OBSERVATIONS:
                        break
    except OSError:
        raise ReceiveError("RECEIVER_SOCKET_UNAVAILABLE") from None
    finished_ms = max(events[-1]["received_at_ms"], int((clock() - started) * 1000))
    return {
        "decision_received_at_ms": finished_ms,
        "max_age_ms": RECEIVER_MAX_AGE_MS,
        "events": events,
    }
