"""EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION.
Fixed synthetic reception-interval continuity. Mock verifier only; no ZKP.
"""
import copy
import hashlib
import hmac
import json
import os
import stat
import tempfile
from contextlib import contextmanager
from pathlib import Path

from interval_coverage import accept_interval, PERIOD, COUNT, TOLERANCE
from persistent_unified import PersistentUnified, canonical
from trusted_time import TrustedTimeUnified, BindingRejected, valid_ms

WIDTH = PERIOD * COUNT


class ContinuitySession:
    """Private dedicated state; verifier-owned anchor; no rollback protection."""
    _locked = PersistentUnified._locked
    _write = PersistentUnified._write

    def __init__(self, *, state_dir, anchor, initialize=False, **options):
        if not valid_ms(anchor) or not valid_ms(anchor + WIDTH):
            raise BindingRejected("INVALID_INTERVAL_ANCHOR")
        self._directory = Path(state_dir).absolute()
        self._state = self._directory / "state.json"
        self._anchor = anchor
        self._options = dict(options)
        self._options["enrollment"] = copy.deepcopy(options["enrollment"])
        with self._stage() as stage:
            self._scope = hashlib.sha256(canonical([
                "TAG/QA/CONTINUITY/v1", stage._scope, anchor,
                PERIOD, COUNT, TOLERANCE, stage._max_age,
                hashlib.sha256(stage._time_key).hexdigest()
            ])).hexdigest()
        with self._locked():
            if initialize:
                if os.path.lexists(self._state):
                    raise BindingRejected("STATE_ALREADY_EXISTS")
                self._write((None, anchor))
            self._read()

    @contextmanager
    def _stage(self):
        with tempfile.TemporaryDirectory(prefix="continuity-stage-") as path:
            yield TrustedTimeUnified(state_dir=path, initialize=True, **self._options)

    def _encode(self, record):
        watermark, next_start = record
        payload = {"version": 2, "scope": self._scope,
                   "watermark": watermark, "next_start": next_start}
        return canonical({"payload": payload,
                          "checksum": hashlib.sha256(canonical(payload)).hexdigest()}) + b"\n"

    def _read(self):
        try:
            fd = os.open(self._state, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
            with os.fdopen(fd, "rb") as stream:
                st = os.fstat(stream.fileno())
                if (not stat.S_ISREG(st.st_mode) or st.st_uid != os.getuid()
                        or stat.S_IMODE(st.st_mode) != 0o600 or st.st_size > 1024):
                    raise ValueError
                raw = stream.read(1025)
            p = json.loads(raw)["payload"]
            w, n = p["watermark"], p["next_start"]
            if (type(p["version"]) is not int or p["version"] != 2
                    or p["scope"] != self._scope
                    or not valid_ms(n) or n < self._anchor
                    or (n-self._anchor) % WIDTH != 0
                    or ((w is None) != (n == self._anchor))
                    or (w is not None and (type(w) is not list or len(w) != 2
                        or any(type(x) is not int for x in w)
                        or not 0 <= w[0] < 2**48 or not 0 <= w[1] < 2**32))
                    or not hmac.compare_digest(raw, self._encode((w, n)))):
                raise ValueError
            return (None if w is None else tuple(w), n)
        except (OSError, ValueError, TypeError, KeyError, OverflowError, RecursionError):
            raise BindingRejected("STATE_MISSING_CORRUPT_OR_INCOMPATIBLE") from None

    def accept_next(self, pairs, start):
        if not valid_ms(start) or not valid_ms(start + WIDTH):
            raise BindingRejected("INVALID_INTERVAL")
        with self._locked():
            watermark, expected = self._read()
            if start > expected:
                raise BindingRejected("INTERVAL_GAP")
            if start < expected:
                raise BindingRejected("INTERVAL_OVERLAP_OR_REPLAY")
            with self._stage() as stage:
                stage._write(watermark)
                digests = accept_interval(stage, pairs, start)
                self._write((stage._read(), start + WIDTH))
                return digests
