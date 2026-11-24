"""EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION.

Fixed synthetic reception-slot admission. Reuses authenticated receipts,
per-observation verification and the persistent watermark; no interval ZKP.
"""
import copy
import tempfile
from pathlib import Path
from trusted_time import valid_ms, BindingRejected

PERIOD, COUNT, TOLERANCE = 100, 3, 10

def accept_interval(session, pairs, start):
    """Accept one closed synthetic reception interval; start is verifier-owned.

    The caller must supply a trusted interval start and a TrustedTimeUnified
    session. This is an experimental composition, not an interval ZKP.
    """
    # Fixed verifier-owned policy: 3 slots, centers at +50,+150,+250ms.
    # Freeze decision clock once at batch admission; each receipt is authenticated
    # by the existing gate. No caller-provided coverage or time policy.
    if not valid_ms(start) or not valid_ms(start + COUNT*PERIOD):
        raise BindingRejected("INVALID_INTERVAL")
    if type(pairs) not in (list, tuple) or len(pairs) != COUNT:
        raise BindingRejected("INCOMPLETE_INTERVAL")
    pairs = copy.deepcopy(pairs)
    if any(type(pair) not in (tuple, list) or len(pair) != 2 for pair in pairs):
        raise BindingRejected("INVALID_INTERVAL_PAIR")
    try:
        now = session._clock()
    except Exception:
        raise BindingRejected("DECISION_CLOCK_UNAVAILABLE") from None
    if not valid_ms(now):
        raise BindingRejected("DECISION_CLOCK_UNAVAILABLE")
    if now < start + COUNT*PERIOD:
        raise BindingRejected("INTERVAL_NOT_CLOSED")
    with session._locked():
        previous = session._read()
        with tempfile.TemporaryDirectory(prefix="interval-stage-") as temp:
            stage = copy.copy(session)
            stage._gate = copy.copy(session._gate)
            stage._directory = Path(temp)
            stage._state = stage._directory / "state.json"
            stage._clock = lambda: now
            stage._write(previous)
            digests = []
            for i, (capture, receipt) in enumerate(pairs):
                center = start + i*PERIOD + PERIOD//2
                if (type(receipt) is not dict or not valid_ms(receipt.get("ingress_ms"))
                        or abs(receipt["ingress_ms"]-center) > TOLERANCE):
                    raise BindingRejected("SLOT_MISMATCH")
                old = stage._read()
                digest = stage.accept(capture, receipt=receipt)
                new = stage._read()
                # Exactly one primary observation per slot, with strictly
                # increasing signed source boot counters, including prior state.
                primary = sum(int.from_bytes(bytes.fromhex(e["frame_hex"])[7:10],"little")==33
                              for e in capture["events"])
                if primary != 1 or (old is not None and new[1] <= old[1]):
                    raise BindingRejected("PRIMARY_COUNT_OR_BOOT_ORDER")
                digests.append(digest)
            session._write(stage._read())
            session._gate = stage._gate
            return tuple(digests)
