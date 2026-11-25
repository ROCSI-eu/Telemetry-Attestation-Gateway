"""EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION.
Non-cryptographic prototype: no proof generated or verified.
"""
import copy
import hmac
from interval_continuity import WIDTH
from interval_recovery import RecoverySession
from persistent_unified import PersistentUnified
from state_rollback import RollbackSession
from trusted_time import BindingRejected


def forward_one(old, new, anchor):
    """Only one existing v3 transition; never delete or bridge history."""
    a, b = old["segments"], new["segments"]
    x, y = old["watermark"], new["watermark"]
    p, q = old["pending"], new["pending"]
    if p is None and q is not None:
        return bool(a) and a == b and x == y and q[0] == a[-1][1]
    if q is not None or y is None:
        return False
    if x is not None and not all(n > o for o, n in zip(x, y)):
        return False
    if p is not None:
        return b == a + [[p[1], p[1]+WIDTH]]
    if not a:
        return b == [[anchor, anchor+WIDTH]]
    return b == a[:-1] + [[a[-1][0], a[-1][1]+WIDTH]]


class ReconciliationSession(RollbackSession):
    """One bounded candidate, explicit repair, trusted current reference."""
    def __init__(self, *, reconcile=False, initialize=False, **options):
        if reconcile and initialize:
            raise BindingRejected("RECONCILIATION_MODE_CONFLICT")
        self._repair = reconcile
        super().__init__(initialize=initialize, **options)
        self._repair = False

    def _candidate(self):
        # Reuse the exact canonical v3 parser and atomic writer with a
        # separate file in the same locked local directory.
        target = copy.copy(self)
        target._state = self._directory / "prepared.json"
        return target

    def _write(self, record):
        if not self._bootstrap:
            PersistentUnified._write(self._candidate(), record)
        super()._write(record)

    def _read(self):
        if not self._repair:
            return super()._read()
        old = RecoverySession._read(self)
        with self._reference._locked():
            current = self._reference._read()
            if hmac.compare_digest(current, self._digest(old)):
                raise BindingRejected("RECONCILIATION_NOT_REQUIRED")
            try:
                new = RecoverySession._read(self._candidate())
            except BindingRejected:
                raise BindingRejected("RECONCILIATION_EVIDENCE_UNAVAILABLE") from None
            if not hmac.compare_digest(current, self._digest(new)):
                raise BindingRejected("RECONCILIATION_REFERENCE_MISMATCH")
            if not forward_one(old, new, self._anchor):
                raise BindingRejected("RECONCILIATION_NOT_FORWARD")
            # Reference remains unchanged and locked throughout repair.
            PersistentUnified._write(self, new)
            return new
