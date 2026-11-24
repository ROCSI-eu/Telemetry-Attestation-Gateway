#!/usr/bin/env python3
"""Offline synthetic reference for verifier-authorized proof input binding."""
from __future__ import annotations

import copy
import hashlib
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "mavlink-normalization-v0"))
import mavlink_normalize as parser


class BindingRejected(ValueError):
    """No authorized digest is available."""


def authorized_digest(capture: dict, *, verifier_key_hex: str,
                      enrollment: dict | None, requested_alias: str) -> bytes:
    """Return the signed primary frame digest only under verifier-owned policy.

    Both the enrollment and the symmetric MAVLink key must be supplied out of
    band by the verifier; neither may be selected from the capture. This
    deliberately supports only the existing synthetic slot, not real identity.
    """
    if not isinstance(enrollment, dict) or enrollment.get("active") is not True:
        raise BindingRejected("REJECTED_NOT_ENROLLED_OR_REVOKED")
    if (not isinstance(capture, dict) or not isinstance(verifier_key_hex, str)
            or not isinstance(requested_alias, str) or not requested_alias):
        raise BindingRejected("REJECTED_INVALID_POLICY")
    try:
        key = bytes.fromhex(verifier_key_hex)
    except ValueError:
        raise BindingRejected("REJECTED_INVALID_POLICY") from None
    if len(key) != 32 or hashlib.sha256(key).hexdigest() != enrollment.get("key_fingerprint"):
        raise BindingRejected("REJECTED_KEY_FINGERPRINT")
    if requested_alias != enrollment.get("alias"):
        raise BindingRejected("REJECTED_SOURCE_ALIAS")
    slot = enrollment.get("slot")
    if slot != "1:1:7":
        raise BindingRejected("REJECTED_SOURCE_SLOT")

    clean = copy.deepcopy(capture)
    clean["test_trust_store"] = {slot: verifier_key_hex}
    result = parser.evaluate_capture(clean)
    if result["status"] != "NORMALIZED" or result["source"]["trust"] != "SIGNED_VALID":
        raise BindingRejected("REJECTED_SIGNATURE_OR_CAPTURE")

    # Same primary selection and BLAKE2s preimage as the validated QA binding.
    frames = [bytes.fromhex(event["frame_hex"]) for event in clean["events"]]
    primary = [frame for frame in frames
               if int.from_bytes(frame[7:10], "little") == parser.GLOBAL_POSITION_INT]
    if not primary:
        raise BindingRejected("PRIMARY_OBSERVATION_MISSING")
    frame = primary[-1]
    if len(frame) != 53 or frame[1] != 28 or frame[2] != 1:
        raise BindingRejected("UNSUPPORTED_SIGNED_PRIMARY_PROFILE")
    return hashlib.blake2s(frame).digest()
