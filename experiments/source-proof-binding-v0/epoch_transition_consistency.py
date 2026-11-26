"""EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION.
One pre-enrolled consistency slot; no transition execution or independent authority.
"""
import hashlib
import hmac
from pathlib import Path
from epoch_transition_binding import transition_mac
from emission_end_consistency import Checkpoint, canonical, BindingRejected

VERSION = "TAG/QA/EPOCH-TRANSITION-CONSISTENCY/v1"


class TransitionConsistency:
    def __init__(self, root, *, key, scope, previous, initialize=False):
        if (type(key) is not bytes or len(key) != 32
                or any(type(v) is not str or not v for v in (scope, previous))):
            raise BindingRejected("INVALID_CONSISTENCY_CONTEXT")
        self.key, self.scope, self.previous = key, scope, previous
        self.context = [VERSION, scope, previous, hashlib.sha256(key).hexdigest()]
        self.empty = self.digest(["UNSET"])
        self.state = Checkpoint(Path(root) / "state")
        self.reference = Checkpoint(Path(root) / "reference")
        if initialize:
            self.reference.advance(None, self.empty)
            self.state.advance(None, self.empty)
        with self.state._locked():
            self.retained()

    def digest(self, fields):
        return hashlib.sha256(canonical([self.context, fields])).hexdigest()

    def retained(self):
        digest = self.state._read()
        self.reference.check(digest)
        return digest

    def observe(self, authorization):
        if type(authorization) is not dict:
            raise BindingRejected("INVALID_TRANSITION_EVIDENCE")
        fields = authorization.copy()
        if set(fields) != {"scope", "previous", "successor", "mac"}:
            raise BindingRejected("INVALID_TRANSITION_EVIDENCE")
        scope, previous, successor, mac = (
            fields[k] for k in ("scope", "previous", "successor", "mac"))
        if (any(type(v) is not str or not v for v in (scope, previous, successor))
                or type(mac) is not str or len(mac) != 64 or not mac.isascii()):
            raise BindingRejected("INVALID_TRANSITION_EVIDENCE")
        try:
            expected = transition_mac(self.key, scope, previous, successor)
        except (ValueError, UnicodeError):
            raise BindingRejected("INVALID_TRANSITION_EVIDENCE") from None
        if not hmac.compare_digest(expected, mac):
            raise BindingRejected("TRANSITION_NOT_AUTHENTIC")
        if (scope, previous) != (self.scope, self.previous):
            raise BindingRejected("CONSISTENCY_CONTEXT_MISMATCH")
        candidate = self.digest(["AUTHORIZATION", successor, mac])
        with self.state._locked():
            retained = self.retained()
            if hmac.compare_digest(retained, self.empty):
                self.reference.advance(retained, candidate)
                self.state._write(candidate)
                return "ACCEPT"
            if hmac.compare_digest(retained, candidate):
                return "IDEMPOTENT"
            raise BindingRejected("TRANSITION_AUTHORIZATION_CONFLICT")
