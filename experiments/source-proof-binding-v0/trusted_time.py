"""EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION.

Offline simulated ingress-time attestation, not sensor capture time.
A separate test authority observes a capture at its own clock boundary.
The relying verifier trusts its configured test key and decision clock.
"""
import copy
import hashlib
import hmac

from persistent_unified import PersistentUnified, BindingRejected, canonical

DOMAIN = b"TAG/QA/INGRESS-TIME/v1\x00"


def valid_ms(value):
    return type(value) is int and 0 <= value < 2**63


def capture_hash(capture):
    # The existing binding replaces this untrusted trust store. Bind all
    # other capture fields, including ordered frames and receiver metadata.
    if type(capture) is not dict:
        raise BindingRejected("INVALID_TIME_CAPTURE")
    try:
        return hashlib.sha256(canonical({
            k: v for k, v in capture.items() if k != "test_trust_store"
        })).hexdigest()
    except (TypeError, ValueError, OverflowError, RecursionError):
        raise BindingRejected("INVALID_TIME_CAPTURE") from None


def receipt_mac(key, scope, capture, ingress_ms):
    return hmac.digest(key, DOMAIN + canonical([
        scope, capture_hash(capture), ingress_ms
    ]), "sha256").hex()


class TrustedTimeUnified(PersistentUnified):
    """Half-open decision window [ingress, ingress + max_age), zero skew."""

    def __init__(self, *, time_key, decision_clock, max_age_ms, **kwargs):
        if (type(time_key) is not bytes or len(time_key) != 32
                or not callable(decision_clock) or not valid_ms(max_age_ms)
                or max_age_ms == 0):
            raise BindingRejected("INVALID_TIME_POLICY")
        try:
            source_key = bytes.fromhex(kwargs["verifier_key_hex"])
        except (KeyError, TypeError, ValueError):
            raise BindingRejected("INVALID_TIME_POLICY") from None
        if hmac.compare_digest(time_key, source_key):
            raise BindingRejected("TIME_KEY_NOT_SEPARATE")
        self._time_key = time_key
        self._clock = decision_clock
        self._max_age = max_age_ms
        super().__init__(**kwargs)

    def _check_reference(self, capture, *, receipt=None):
        # Reference and decision clock never selected by the capture.
        snapshot = copy.deepcopy(capture)
        evidence = copy.deepcopy(receipt)
        if (type(evidence) is not dict
                or set(evidence) != {"ingress_ms", "mac"}
                or not valid_ms(evidence["ingress_ms"])
                or type(evidence["mac"]) is not str
                or len(evidence["mac"]) != 64
                or not evidence["mac"].isascii()):
            raise BindingRejected("INVALID_TIME_REFERENCE")
        ingress = evidence["ingress_ms"]
        expected = receipt_mac(self._time_key, self._scope, snapshot, ingress)
        if not hmac.compare_digest(expected, evidence["mac"]):
            raise BindingRejected("TIME_REFERENCE_NOT_AUTHENTIC")
        try:
            now = self._clock()
        except Exception:
            raise BindingRejected("DECISION_CLOCK_UNAVAILABLE") from None
        if not valid_ms(now):
            raise BindingRejected("DECISION_CLOCK_UNAVAILABLE")
        if ingress > now:
            raise BindingRejected("TIME_REFERENCE_IN_FUTURE")
        if now - ingress >= self._max_age:
            raise BindingRejected("TIME_REFERENCE_STALE")
        # Reuse original proof callback and persistent replay check. Time is
        # evaluated at admission, not again after proof verification.
        return snapshot

    def accept(self, capture, *, receipt=None):
        return super().accept(self._check_reference(capture, receipt=receipt))
