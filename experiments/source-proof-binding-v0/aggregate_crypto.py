"""EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION.

Crypto-verifier adapter for one authenticated synthetic three-slot interval.
Proof bytes must be supplied; a previous PASS record is never substituted.
The local unit-test verifier is simulated; no cryptographic verification in tests.
"""
import copy
from enum import Enum
import hashlib
import json
from interval_coverage import _validate_interval, _admit_slots, PERIOD, COUNT, TOLERANCE
from trusted_time import TrustedTimeUnified, BindingRejected

LIMIT = 500
VERSION = 2
EXPECTED_VK_SHA256 = "942b463decd9b1f6ab58369b0ab16f8412cf769d0e8cf137e4ea5862ef644fba"
EXPECTED_VK_BYTES = 3680

class CryptoResult(Enum):
    VALID = "VALID"
    INVALID = "INVALID"
    UNVERIFIABLE = "UNVERIFIABLE"

def public_inputs(digests):
    """Verifier reconstructs all 98 public field values from admitted frames."""
    if type(digests) is not tuple or len(digests) != COUNT or any(type(d) is not bytes or len(d) != 32 for d in digests):
        raise BindingRejected("INVALID_AGGREGATE_DIGESTS")
    values = [v for digest in digests for v in digest] + [LIMIT, VERSION]
    assert len(values) == 98
    return json.dumps({"public_inputs": [f"0x{v:064x}" for v in values]}, separators=(",", ":")) + "\n"

def local_bb_verify_only(bb_path, crs_path):
    """Reuse existing local offline independent verifier; no proving path.
    Exit code not recognized as positive becomes UNVERIFIABLE, never VALID.
    Run only inside an authorized offline isolated QA sandbox.
    """
    from unified import local_bb_verifier
    check = local_bb_verifier(bb_path, crs_path)
    def verify(encoded, proof, vk):
        result = check(encoded, proof, vk)
        return CryptoResult.VALID if result is True else CryptoResult.UNVERIFIABLE
    return verify

class AggregateCrypto(TrustedTimeUnified):
    """Separate real-VK state context; lock, verify, then one atomic write."""
    def __init__(self, *, verify_crypto, **kwargs):
        if not callable(verify_crypto):
            raise BindingRejected("INVALID_CRYPTO_VERIFIER")
        self._verify_crypto = verify_crypto
        super().__init__(verify=None, proof=b"", vk=b"", **kwargs)

    def _state_context(self):
        return ["TAG-interval-crypto-v2", EXPECTED_VK_SHA256, LIMIT,
                VERSION, COUNT, PERIOD, TOLERANCE]

    def accept(self, *args, **kwargs):
        raise BindingRejected("AGGREGATE_ONLY")

    def accept_aggregate(self, pairs, start, *, proof, vk):
        # A provenance record, hash, token or a missing proof cannot commit.
        if type(proof) is not bytes or not 0 < len(proof) <= 65536:
            return CryptoResult.UNVERIFIABLE
        if (type(vk) is not bytes or len(vk) != EXPECTED_VK_BYTES
                or hashlib.sha256(vk).hexdigest() != EXPECTED_VK_SHA256):
            return CryptoResult.UNVERIFIABLE
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
                result = self._verify_crypto(public_inputs(digests), proof, vk)
            except Exception:
                return CryptoResult.UNVERIFIABLE
            if result is not CryptoResult.VALID:
                return CryptoResult.INVALID if result is CryptoResult.INVALID else CryptoResult.UNVERIFIABLE
            self._write(staged._gate._watermark)
            self._gate = staged._gate
            return CryptoResult.VALID
