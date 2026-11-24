"""EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION.
Synthetic recovery after verifier-declared irrecoverable reception gap; mock proof verifier.
"""
import hashlib
import hmac
import json
import os
import stat

from interval_continuity import ContinuitySession, WIDTH
from interval_coverage import accept_interval
from persistent_unified import canonical
from trusted_time import BindingRejected, valid_ms

MAX_SEGMENTS = 16
MAX_STATE = 4096
DOMAIN = b"TAG/QA/INTERVAL-RECOVERY/v1\x00"


class RecoverySession(ContinuitySession):
    """Separate v3 state; same enrollment and global watermark across segments."""

    def __init__(self, *, recovery_key, **options):
        if (type(recovery_key) is not bytes or len(recovery_key) != 32
                or recovery_key == options["time_key"]
                or recovery_key == bytes.fromhex(options["verifier_key_hex"])):
            raise BindingRejected("INVALID_RECOVERY_POLICY")
        self._recovery_key = recovery_key
        self._recovery_fingerprint = hashlib.sha256(recovery_key).hexdigest()
        super().__init__(**options)

    def _encode(self, record):
        # Base initializer invokes _write with the v2 empty record only.
        if record == (None, self._anchor):
            record = {"watermark": None, "segments": [], "pending": None}
        payload = {"version": 3, "scope": self._scope,
                   "recovery_policy": self._recovery_fingerprint, **record}
        return canonical({"payload": payload,
                          "checksum": hashlib.sha256(canonical(payload)).hexdigest()}) + b"\n"

    def _read(self):
        try:
            fd = os.open(self._state, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
            with os.fdopen(fd, "rb") as stream:
                st = os.fstat(stream.fileno())
                if (not stat.S_ISREG(st.st_mode) or st.st_uid != os.getuid()
                        or stat.S_IMODE(st.st_mode) != 0o600 or st.st_size > MAX_STATE):
                    raise ValueError
                raw = stream.read(MAX_STATE + 1)
            p = json.loads(raw)["payload"]
            w, segments, pending = p["watermark"], p["segments"], p["pending"]
            if (type(p["version"]) is not int or p["version"] != 3
                    or p["scope"] != self._scope
                    or p["recovery_policy"] != self._recovery_fingerprint
                    or type(segments) is not list or len(segments) > MAX_SEGMENTS
                    or ((w is None) != (not segments))
                    or (w is not None and (type(w) is not list or len(w) != 2
                        or any(type(x) is not int for x in w)
                        or not 0 <= w[0] < 2**48 or not 0 <= w[1] < 2**32))):
                raise ValueError
            previous = None
            for s in segments:
                if (type(s) is not list or len(s) != 2
                        or not all(valid_ms(x) for x in s)
                        or s[0] >= s[1] or (s[1]-s[0]) % WIDTH
                        or (previous is None and s[0] != self._anchor)
                        or (previous is not None and s[0] <= previous)):
                    raise ValueError
                previous = s[1]
            if pending is not None and (not segments or type(pending) is not list
                    or len(pending) != 2 or not all(valid_ms(x) for x in pending)
                    or pending[0] != previous or pending[1] <= previous
                    or not valid_ms(pending[1]+WIDTH)):
                raise ValueError
            record = {"watermark": w, "segments": segments, "pending": pending}
            if not hmac.compare_digest(raw, self._encode(record)):
                raise ValueError
            return record
        except (OSError, ValueError, TypeError, KeyError, OverflowError, RecursionError):
            raise BindingRejected("STATE_MISSING_CORRUPT_OR_INCOMPATIBLE") from None

    def _validate_start(self, start):
        if not valid_ms(start) or not valid_ms(start+WIDTH):
            raise BindingRejected("INVALID_INTERVAL")

    def _check_closed(self, start):
        try:
            now = self._options["decision_clock"]()
        except Exception:
            raise BindingRejected("DECISION_CLOCK_UNAVAILABLE") from None
        if not valid_ms(now):
            raise BindingRejected("DECISION_CLOCK_UNAVAILABLE")
        if now < start+WIDTH:
            raise BindingRejected("INTERVAL_NOT_CLOSED")

    def _admit(self, record, pairs, start, *, recovery=False):
        with self._stage() as stage:
            stage._write(record["watermark"])
            digests = accept_interval(stage, pairs, start)
            record["watermark"] = stage._read()
            if recovery or not record["segments"]:
                record["segments"].append([start, start+WIDTH])
            else:
                record["segments"][-1][1] = start+WIDTH
            record["pending"] = None
            self._write(record)
            return digests

    def accept_next(self, pairs, start):
        """Ordinary future intervals are rejected, not implicitly declared lost."""
        self._validate_start(start)
        with self._locked():
            r = self._read()
            if r["pending"] is not None:
                raise BindingRejected("RECOVERY_REQUIRED")
            expected = r["segments"][-1][1] if r["segments"] else self._anchor
            if start > expected:
                raise BindingRejected("INTERVAL_GAP")
            if start < expected:
                raise BindingRejected("INTERVAL_OVERLAP_OR_REPLAY")
            return self._admit(r, pairs, start)

    def declare_gap(self, start):
        """Verifier-owned declaration of irrecoverable gap, not a capture field."""
        self._validate_start(start)
        with self._locked():
            r = self._read()
            if not r["segments"] or r["pending"] is not None:
                raise BindingRejected("GAP_DECLARATION_NOT_ALLOWED")
            expected = r["segments"][-1][1]
            if start <= expected:
                raise BindingRejected("NOT_A_FORWARD_GAP")
            self._check_closed(start)
            r["pending"] = [expected, start]
            self._write(r)

    def _authorization_message(self, record):
        return DOMAIN + canonical([self._scope, self._recovery_fingerprint,
                                   record["watermark"], record["segments"], record["pending"]])

    def recover(self, pairs, start, authorization):
        self._validate_start(start)
        with self._locked():
            r = self._read()
            if r["pending"] is None or start != r["pending"][1]:
                raise BindingRejected("RECOVERY_TARGET_MISMATCH")
            if len(r["segments"]) >= MAX_SEGMENTS:
                raise BindingRejected("SEGMENT_LIMIT")
            expected = hmac.digest(self._recovery_key, self._authorization_message(r),
                                   "sha256").hex()
            if (type(authorization) is not str or len(authorization) != 64
                    or not authorization.isascii()
                    or not hmac.compare_digest(expected, authorization)):
                raise BindingRejected("RECOVERY_NOT_AUTHORIZED")
            return self._admit(r, pairs, start, recovery=True)

    def covers(self, start, end):
        """Only one accepted contiguous segment may cover a half-open range."""
        if not valid_ms(start) or not valid_ms(end) or start >= end:
            return False
        with self._locked():
            return any(a <= start and end <= b for a, b in self._read()["segments"])
