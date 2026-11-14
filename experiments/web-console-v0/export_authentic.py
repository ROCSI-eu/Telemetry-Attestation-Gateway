#!/usr/bin/env python3
"""Export a tiny browser-safe replay ONLY after genuine offline verification.

EXPERIMENTAL
SYNTHETIC_ONLY
A0_SYNTHETIC
NOT VALIDATION OR PRODUCTION AUTHORIZATION
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Any

CLI_DIR = Path(__file__).resolve().parents[1] / "integrated-cli-v0"
if str(CLI_DIR) not in sys.path:
    sys.path.insert(0, str(CLI_DIR))

import authentic_package_cli as authentic  # noqa: E402

LABELS = list(authentic.LABELS)
VERSION = "TAG_PRECOMPUTED_SYNTHETIC_VERIFIER_REPLAY_V0_EXPERIMENTAL"
KIND = "PRECOMPUTED_GENUINE_SYNTHETIC_VERIFICATION"
DISPOSITION = "INDEPENDENT_OFFLINE_CHECK_AT_EXPORT"
ALLOWED_CRYPTO = ("VALID", "INVALID")
ALLOWED_REASONS = (None, "PROOF_REJECTED")

# Precisely defined output; do not serialize the CLI result or proof manifest.
FIELDS = frozenset({
    "labels", "schema_version", "evidence_kind", "verification_basis",
    "verification_input", "cryptographic", "cryptographic_reason",
    "proof_generation", "source_trust", "assurance", "policy", "freshness",
    "revocation", "replay", "publication", "relying_party_decision",
    "command_path", "private_fields_disclosed", "browser_verified",
    "proof_validity_is_telemetry_truth",
})


class ExportRejected(Exception):
    """Fail closed without leaking package paths or restricted content."""


def minimize(checked: dict[str, Any]) -> dict[str, Any]:
    """Take only known typed values from the actual verifier result."""
    try:
        if (checked["package"]["status"] != "ACCEPTED"
                or checked["verification_input"]["status"] != "ACCEPTED"
                or checked["verification_performed"] is not True
                or checked["cryptographic"]["status"] not in ALLOWED_CRYPTO
                or checked["cryptographic"]["reason"] not in ALLOWED_REASONS):
            raise ExportRejected
        if (checked["cryptographic"]["status"] == "VALID"
                and checked["cryptographic"]["reason"] is not None):
            raise ExportRejected
        if (checked["cryptographic"]["status"] == "INVALID"
                and checked["cryptographic"]["reason"] != "PROOF_REJECTED"):
            raise ExportRejected
        if (checked["schema_version"] != authentic.RESULT_VERSION
                or checked["evidence_kind"] != "AUTHENTIC_SYNTHETIC_PACKAGE_CHECK"
                or checked["mock"] is not False
                or checked["labels"] != LABELS
                or checked["proof_generation"] != "NOT_OBSERVED"
                or checked["source_trust"] != "NOT_EVALUATED"
                or checked["private_witness_disclosed"] is not False
                or checked["proof_validity_is_telemetry_truth"] is not False
                or checked["command_path"] != "NONE"
                or checked["publication"] != "NOT_PERFORMED"
                or checked["relying_party_decision"] != "NOT_MADE"):
            raise ExportRejected
        for name in ("policy", "freshness", "revocation", "replay"):
            if checked[name] != "NOT_EVALUATED":
                raise ExportRejected
        assurance = checked["assurance"]
        if assurance != {
            "declared": "A0_SYNTHETIC",
            "effective": "A0_SYNTHETIC",
            "required": "NOT_EVALUATED",
            "demonstrator": "A0_SYNTHETIC",
        }:
            raise ExportRejected
        output = {
            "labels": LABELS,
            "schema_version": VERSION,
            "evidence_kind": KIND,
            "verification_basis": DISPOSITION,
            "verification_input": "ACCEPTED",
            "cryptographic": checked["cryptographic"]["status"],
            "cryptographic_reason": checked["cryptographic"]["reason"],
            "proof_generation": "NOT_OBSERVED",
            "source_trust": "NOT_EVALUATED",
            "assurance": "A0_SYNTHETIC",
            "policy": "NOT_EVALUATED",
            "freshness": "NOT_EVALUATED",
            "revocation": "NOT_EVALUATED",
            "replay": "NOT_EVALUATED",
            "publication": "NOT_PERFORMED",
            "relying_party_decision": "NOT_MADE",
            "command_path": "NONE",
            "private_fields_disclosed": False,
            "browser_verified": False,
            "proof_validity_is_telemetry_truth": False,
        }
        if set(output) != FIELDS:
            raise ExportRejected
        return output
    except (KeyError, ValueError, TypeError, AttributeError) as exc:
        raise ExportRejected from exc


def export(package: Path, destination: Path) -> None:
    """This must run in an isolated offline environment with a pinned verifier."""
    result = authentic.check_package(package)
    minimized = minimize(result)
    # Never overwrite existing evidence; no partial file, restrictive permissions.
    destination_parent = destination.parent
    if not destination_parent.is_dir() or destination.is_symlink() or destination.exists():
        raise ExportRejected
    encoded = (json.dumps(minimized, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("ascii")
    if len(encoded) > 4096:
        raise ExportRejected
    fd = None
    try:
        fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "wb") as stream:
            fd = None
            stream.write(encoded)
    except OSError as exc:
        raise ExportRejected from exc
    finally:
        if fd is not None:
            os.close(fd)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        export(args.package_dir, args.output)
    except ExportRejected:
        print("EXPERIMENTAL SYNTHETIC_ONLY A0_SYNTHETIC NOT VALIDATION OR PRODUCTION AUTHORIZATION: export refused", file=sys.stderr)
        return 2
    print("EXPERIMENTAL SYNTHETIC_ONLY A0_SYNTHETIC NOT VALIDATION OR PRODUCTION AUTHORIZATION: minimized offline verifier replay exported")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
