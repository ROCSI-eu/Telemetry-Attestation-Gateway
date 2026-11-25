"""EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION.
Non-cryptographic mock integration; no proof generated or verified.
"""
import copy
import hashlib
import json
from enum import Enum
from interval_coverage import _validate_interval, _admit_slots, PERIOD, COUNT, TOLERANCE
from trusted_time import TrustedTimeUnified, BindingRejected

class MockResult(Enum):
    VALID = "VALID"
    INVALID = "INVALID"
    UNVERIFIABLE = "UNVERIFIABLE"

LIMIT, VERSION = 500, 1
# Distinct, intentionally synthetic mock context. Not the actual aggregate VK.
MOCK_VK = b"TAG-interval-mock-vk-not-cryptographic"

def public_inputs(digests):
    if type(digests) is not tuple or len(digests) != COUNT or any(
        type(d) is not bytes or len(d) != 32 for d in digests):
        raise BindingRejected("INVALID_AGGREGATE_DIGESTS")
    values = [v for d in digests for v in d] + [LIMIT, VERSION]
    return json.dumps({"public_inputs":[f"0x{v:064x}" for v in values]}, separators=(",",":")) + "\n"

class AggregateInterval(TrustedTimeUnified):
    """Mock-only isolated state; does not migrate or reset prior state."""
    def __init__(self, *, verify_mock, **kwargs):
        if not callable(verify_mock):
            raise BindingRejected("INVALID_MOCK_VERIFIER")
        self._verify_mock = verify_mock
        super().__init__(verify=None, proof=b"", vk=MOCK_VK, **kwargs)

    def _state_context(self):
        return ["TAG-interval-mock-v1", hashlib.sha256(MOCK_VK).hexdigest(),
                LIMIT, VERSION, COUNT, PERIOD, TOLERANCE]

    def accept(self, *args, **kwargs):
        raise BindingRejected("AGGREGATE_ONLY")

    def accept_aggregate(self, pairs, start, *, mock_token):
        if type(mock_token) is not bytes or not 0 < len(mock_token) <= 65536:
            return MockResult.UNVERIFIABLE
        pairs, now = _validate_interval(self, pairs, start)
        with self._locked():
            staged = copy.copy(self)
            staged._gate = copy.copy(self._gate)
            staged._gate._watermark = self._read()
            staged._clock = lambda: now
            def admit(capture, *, receipt):
                return staged._gate.accept(staged._check_reference(capture, receipt=receipt))
            digests = _admit_slots(pairs, start, admit, lambda: staged._gate._watermark)
            try:
                result = self._verify_mock(public_inputs(digests), mock_token, MOCK_VK)
            except Exception:
                return MockResult.UNVERIFIABLE
            if result is not MockResult.VALID:
                return MockResult.INVALID if result is MockResult.INVALID else MockResult.UNVERIFIABLE
            self._write(staged._gate._watermark)
            self._gate = staged._gate
            return MockResult.VALID
