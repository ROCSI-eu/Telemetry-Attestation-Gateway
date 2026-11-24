"""Synthetic QA: sequential verifier-session replay and regression boundary."""
import copy
from pathlib import Path
import sys

REFERENCE = Path(__file__).resolve().parent
sys.path.insert(0, str(REFERENCE))
from binding_reference import authorized_digest, BindingRejected


class TemporalGate:
    """One verifier-owned enrollment per session; no trusted clock or persistence."""

    def __init__(self, *, verifier_key_hex, enrollment, requested_alias):
        self._key = verifier_key_hex
        self._enrollment = copy.deepcopy(enrollment)
        self._alias = requested_alias
        self._watermark = None  # (signed timestamp, source boot ms)

    def accept(self, capture):
        # Snapshot untrusted input; existing gate validates all frames and policy.
        snapshot = copy.deepcopy(capture)
        digest = authorized_digest(snapshot, verifier_key_hex=self._key,
                                   enrollment=self._enrollment,
                                   requested_alias=self._alias)
        frames = [bytes.fromhex(e["frame_hex"]) for e in snapshot["events"]]
        stamps = [int.from_bytes(f[-12:-6], "little") for f in frames]
        boots = [int.from_bytes(f[10:10+min(4, f[1])], "little")
                 for f in frames if int.from_bytes(f[7:10], "little") == 33]
        # The existing parser already checks ordering inside each capture and
        # the fixed enrolled slot; compare the first values to prior maxima.
        if self._watermark is not None:
            last_stamp, last_boot = self._watermark
            if stamps[0] <= last_stamp:
                raise BindingRejected("REJECTED_CROSS_CAPTURE_REPLAY_OR_REGRESSION")
            if boots[0] < last_boot:
                raise BindingRejected("REJECTED_CROSS_CAPTURE_BOOT_REGRESSION")
        # Commit both watermarks only after every check passes. Never return
        # a digest for rejected input. No raw observation is retained.
        self._watermark = (stamps[-1], boots[-1])
        return digest
