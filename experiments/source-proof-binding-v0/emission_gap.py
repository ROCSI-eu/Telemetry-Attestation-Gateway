"""EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION.
Local test-only emission-index hypothesis; not a ZKP or persistent gate.
"""
import hashlib
import hmac
from binding_reference import authorized_digest, BindingRejected
from persistent_unified import canonical

DOMAIN = b"TAG/QA/EMISSION-INDEX/v1\x00"

def index_mac(key, scope, epoch, index, digest):
    return hmac.digest(key, DOMAIN + canonical(
        [scope, epoch, index, digest.hex()]), "sha256").hex()

def check_sequence(records, *, key, scope, epoch, first, config):
    """Verify supplied records against a verifier-owned epoch and start index."""
    if (type(key) is not bytes or len(key) != 32
            or type(scope) is not str or not scope
            or type(epoch) is not str or not epoch
            or type(first) is not int or not 1 <= first < 2**64
            or hmac.compare_digest(key, bytes.fromhex(config["verifier_key_hex"]))):
        raise BindingRejected("INVALID_INDEX_POLICY")
    if type(records) is not list or not records:
        raise BindingRejected("EMPTY_SEQUENCE")
    indices = []
    for capture, evidence in records:
        if (type(evidence) is not dict
                or set(evidence) != {"epoch", "index", "mac"}
                or type(evidence["epoch"]) is not str
                or type(evidence["index"]) is not int
                or not 1 <= evidence["index"] < 2**64
                or type(evidence["mac"]) is not str
                or len(evidence["mac"]) != 64
                or not evidence["mac"].isascii()):
            raise BindingRejected("INVALID_INDEX_EVIDENCE")
        digest = authorized_digest(capture, **config)
        claimed = evidence["index"]
        expected = index_mac(key, scope, evidence["epoch"], claimed, digest)
        if not hmac.compare_digest(expected, evidence["mac"]):
            raise BindingRejected("INDEX_NOT_AUTHENTIC")
        if evidence["epoch"] != epoch:
            raise BindingRejected("EPOCH_MISMATCH")
        indices.append(claimed)
    for offset, actual in enumerate(indices):
        expected = first + offset
        if actual > expected:
            raise BindingRejected("EMISSION_GAP")
        if actual < expected:
            raise BindingRejected("INDEX_REPLAY_OR_REGRESSION")
    return tuple(indices)
