"""EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION.
Fixed two-epoch local model; no independent authority or trusted time.
"""
import hmac
from emission_end_freshness import EndFreshness
from emission_gap import BindingRejected
from persistent_unified import canonical

DOMAIN = b"TAG/QA/EPOCH-TRANSITION/v1\x00"


def transition_mac(key, scope, previous, successor):
    return hmac.digest(key, DOMAIN + canonical(
        [scope, previous, successor]), "sha256").hex()


class EpochTransitionBinding(EndFreshness):
    """Reuse fixed policy and locked reference-first transition; fixture key only."""
    def __init__(self, root, *, key, scope, **options):
        super().__init__(root, key=key, scope=scope, **options)
        self._transition_key = key
        self._transition_scope = scope

    def transition(self, authorization):
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
            expected_mac = transition_mac(self._transition_key, scope, previous, successor)
        except (ValueError, UnicodeError):
            raise BindingRejected("INVALID_TRANSITION_EVIDENCE") from None
        if not hmac.compare_digest(expected_mac, mac):
            raise BindingRejected("TRANSITION_NOT_AUTHENTIC")
        if scope != self._transition_scope:
            raise BindingRejected("TRANSITION_SCOPE_MISMATCH")
        # The unchanged base method re-reads current state under lock, requires
        # a matching reference and the exact fixed directed pair, then advances.
        super().transition(expected=previous, target=successor)
        return "ACCEPT"
