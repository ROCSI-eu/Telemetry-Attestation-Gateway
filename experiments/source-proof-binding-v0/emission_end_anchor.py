"""EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION."""
import hmac
from emission_gap import check_sequence, BindingRejected
from persistent_unified import canonical

DOMAIN = b"TAG/QA/EMISSION-END/v1\x00"

def end_mac(key, scope, epoch, first, final):
    return hmac.digest(key, DOMAIN + canonical(
        [scope, epoch, first, final]), "sha256").hex()

def check_closed(records, anchor, *, key, scope, epoch, first, config):
    indices = check_sequence(records, key=key, scope=scope, epoch=epoch,
                             first=first, config=config)
    if anchor is None:
        raise BindingRejected("END_ANCHOR_MISSING")
    if (type(anchor) is not dict
            or set(anchor) != {"epoch", "final", "mac"}
            or type(anchor["epoch"]) is not str
            or type(anchor["final"]) is not int
            or not first <= anchor["final"] < 2**64
            or type(anchor["mac"]) is not str
            or len(anchor["mac"]) != 64
            or not anchor["mac"].isascii()):
        raise BindingRejected("INVALID_END_ANCHOR")
    expected = end_mac(key, scope, anchor["epoch"], first, anchor["final"])
    if not hmac.compare_digest(expected, anchor["mac"]):
        raise BindingRejected("END_NOT_AUTHENTIC")
    if anchor["epoch"] != epoch:
        raise BindingRejected("END_EPOCH_MISMATCH")
    if indices[-1] < anchor["final"]:
        raise BindingRejected("TERMINAL_EMISSION_GAP")
    if indices[-1] > anchor["final"]:
        raise BindingRejected("END_INDEX_CONFLICT")
    return indices
