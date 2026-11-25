"""Synthetic QA: restart-safe sequential watermark on a trusted local filesystem.

EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION
"""
import copy
import fcntl
import hashlib
import hmac
import json
import os
from pathlib import Path
import stat
import tempfile
from contextlib import contextmanager

from unified import Unified, BindingRejected, PINNED_VK


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


class PersistentUnified(Unified):
    """Dedicated private directory, cooperative writers, no rollback protection."""

    def __init__(self, *, state_dir, initialize=False, **kwargs):
        super().__init__(**kwargs)
        self._directory = Path(state_dir).absolute()
        self._state = self._directory / "state.json"
        enrollment = self._gate._enrollment
        try:
            key = bytes.fromhex(self._gate._key)
            if (len(key) != 32 or enrollment["active"] is not True
                    or enrollment["slot"] != "1:1:7"
                    or not self._gate._alias
                    or enrollment["alias"] != self._gate._alias
                    or enrollment["key_fingerprint"] != hashlib.sha256(key).hexdigest()):
                raise ValueError
            self._scope = hashlib.sha256(canonical([
                enrollment["slot"], enrollment["alias"],
                enrollment["key_fingerprint"], *self._state_context()
            ])).hexdigest()
        except (TypeError, KeyError, ValueError, AttributeError):
            raise BindingRejected("INVALID_STATE_POLICY") from None
        with self._locked():
            if initialize:
                if os.path.lexists(self._state):
                    raise BindingRejected("STATE_ALREADY_EXISTS")
                self._write(None)
            self._gate._watermark = self._read()

    def _state_context(self):
        return [PINNED_VK, 500, 1]

    @contextmanager
    def _locked(self):
        fd = None
        try:
            fd = os.open(self._directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            st = os.fstat(fd)
            if st.st_uid != os.getuid() or stat.S_IMODE(st.st_mode) != 0o700:
                raise BindingRejected("UNSAFE_STATE_DIRECTORY")
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            if fd is not None:
                os.close(fd)
            raise BindingRejected("STATE_DIRECTORY_UNAVAILABLE_OR_BUSY") from None
        except BaseException:
            if fd is not None:
                os.close(fd)
            raise
        try:
            yield fd
        finally:
            os.close(fd)

    def _encode(self, watermark):
        payload = {"version": 1, "scope": self._scope, "watermark": watermark}
        return canonical({"payload": payload, "checksum": hashlib.sha256(canonical(payload)).hexdigest()}) + b"\n"

    def _read(self):
        try:
            fd = os.open(self._state, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
            with os.fdopen(fd, "rb") as stream:
                st = os.fstat(stream.fileno())
                if (not stat.S_ISREG(st.st_mode) or st.st_uid != os.getuid()
                        or stat.S_IMODE(st.st_mode) != 0o600 or st.st_size > 1024):
                    raise ValueError
                raw = stream.read(1025)
            obj = json.loads(raw)
            payload = obj["payload"]
            w = payload["watermark"]
            if (type(payload["version"]) is not int or payload["version"] != 1
                    or payload["scope"] != self._scope
                    or (w is not None and (type(w) is not list or len(w) != 2
                        or any(type(x) is not int for x in w)
                        or not 0 <= w[0] < 2**48 or not 0 <= w[1] < 2**32))
                    or not hmac.compare_digest(raw, self._encode(w))):
                raise ValueError
            return None if w is None else tuple(w)
        except (OSError, ValueError, TypeError, KeyError, OverflowError, RecursionError):
            raise BindingRejected("STATE_MISSING_CORRUPT_OR_INCOMPATIBLE") from None

    def _write(self, watermark):
        tmp = None
        try:
            with tempfile.NamedTemporaryFile(dir=self._directory, prefix=".state-", delete=False) as stream:
                tmp = Path(stream.name)
                stream.write(self._encode(watermark))
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(tmp, self._state)
            fd = os.open(self._directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            try:
                os.fsync(fd)
            finally:
                os.close(fd)
        except OSError:
            raise BindingRejected("STATE_COMMIT_FAILED") from None
        finally:
            if tmp is not None:
                tmp.unlink(missing_ok=True)

    def accept(self, capture):
        with self._locked():
            self._gate._watermark = self._read()
            previous = copy.copy(self._gate)
            try:
                digest = super().accept(capture)
                self._write(self._gate._watermark)
            except BaseException:
                self._gate = previous
                raise
            return digest
