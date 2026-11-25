"""EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION.
Synthetic rollback detection; independent reference simulated by a separate private directory.
Non-cryptographic prototype: no proof generated or verified.
"""
import hashlib
import hmac
import os
from pathlib import Path
import stat

from interval_recovery import RecoverySession
from persistent_unified import PersistentUnified
from trusted_time import BindingRejected


class Checkpoint:
    """Simulated independently retained, trusted reference; not a real trust service."""
    _locked = PersistentUnified._locked
    _write = PersistentUnified._write

    def __init__(self, directory):
        self._directory = Path(directory).absolute()
        self._state = self._directory / "state.json"

    def _encode(self, digest):
        return (digest + "\n").encode("ascii")

    def _read(self):
        try:
            fd = os.open(self._state, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
            with os.fdopen(fd, "rb") as stream:
                st = os.fstat(stream.fileno())
                if (not stat.S_ISREG(st.st_mode) or st.st_uid != os.getuid()
                        or stat.S_IMODE(st.st_mode) != 0o600 or st.st_size != 65):
                    raise ValueError
                raw = stream.read(66)
            digest = raw[:-1].decode("ascii")
            if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest) or raw != self._encode(digest):
                raise ValueError
            return digest
        except (OSError, ValueError):
            raise BindingRejected("REFERENCE_UNAVAILABLE_OR_INVALID") from None

    def check(self, digest):
        with self._locked():
            if not hmac.compare_digest(self._read(), digest):
                raise BindingRejected("STATE_REFERENCE_MISMATCH")

    def advance(self, previous, digest):
        with self._locked():
            if previous is None:
                if os.path.lexists(self._state):
                    raise BindingRejected("REFERENCE_ALREADY_EXISTS")
            elif not hmac.compare_digest(self._read(), previous):
                raise BindingRejected("STATE_REFERENCE_MISMATCH")
            self._write(digest)


class RollbackSession(RecoverySession):
    """Check the complete canonical v3 record before every admission or coverage query."""
    def __init__(self, *, reference, initialize=False, **options):
        self._reference = reference
        if Path(options["state_dir"]).resolve() == reference._directory.resolve():
            raise BindingRejected("REFERENCE_NOT_SEPARATE")
        self._bootstrap = initialize
        super().__init__(initialize=initialize, **options)
        self._bootstrap = False

    def _digest(self, record):
        return hashlib.sha256(self._encode(record)).hexdigest()

    def _read(self):
        record = super()._read()
        self._reference.check(self._digest(record))
        return record

    def _write(self, record):
        # Called under the existing local lock. Advance reference first; no success
        # on a partial commit and no automatic repair of a mismatching pair.
        previous = None if self._bootstrap else self._digest(super()._read())
        self._reference.advance(previous, self._digest(record))
        super()._write(record)
