#!/usr/bin/env python3
"""Inspect one local genuine synthetic proof package with the independent verifier.

EXPERIMENTAL
SYNTHETIC_ONLY
A0_SYNTHETIC
NOT VALIDATION OR PRODUCTION AUTHORIZATION
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import stat
import sys
from typing import Any

PROOF_DIR = Path(__file__).resolve().parents[1] / "bounded-speed-proof-v0"
if str(PROOF_DIR) not in sys.path:
    sys.path.insert(0, str(PROOF_DIR))

import verify as independent_verifier  # noqa: E402

LABELS = (
    "EXPERIMENTAL",
    "SYNTHETIC_ONLY",
    "A0_SYNTHETIC",
    "NOT VALIDATION OR PRODUCTION AUTHORIZATION",
)
RESULT_VERSION = "TAG_AUTHENTIC_SYNTHETIC_CHECK_V0_EXPERIMENTAL"
FILES = ("manifest.json", "public-artifact.cbor", "proof", "vk")
MAX_BYTES = {"manifest.json": 65536, "public-artifact.cbor": 4096, "proof": 1048576, "vk": 65536}


def _result() -> dict[str, Any]:
    return {
        "labels": list(LABELS),
        "schema_version": RESULT_VERSION,
        "evidence_kind": "AUTHENTIC_SYNTHETIC_PACKAGE_CHECK",
        "mock": False,
        "package": {"status": "NOT_CHECKED", "reason": None},
        "proof_generation": "NOT_OBSERVED",
        "verification_input": {"status": "NOT_CHECKED", "reason": None},
        "cryptographic": {"status": "NOT_CHECKED", "reason": None},
        "verification_performed": False,
        "policy": "NOT_EVALUATED",
        "freshness": "NOT_EVALUATED",
        "revocation": "NOT_EVALUATED",
        "replay": "NOT_EVALUATED",
        "assurance": {
            "declared": "A0_SYNTHETIC",
            "effective": "A0_SYNTHETIC",
            "required": "NOT_EVALUATED",
            "demonstrator": "A0_SYNTHETIC",
        },
        "publication": "NOT_PERFORMED",
        "relying_party_decision": "NOT_MADE",
        "source_trust": "NOT_EVALUATED",
        "command_path": "NONE",
        "private_witness_disclosed": False,
        "proof_validity_is_telemetry_truth": False,
    }


class PackageRejected(Exception):
    """Do not expose potentially sensitive package values in error output."""


def _file_bytes(path: Path, maximum: int) -> bytes:
    try:
        meta = path.lstat()
        if not stat.S_ISREG(meta.st_mode) or meta.st_size > maximum:
            raise PackageRejected
        with path.open("rb") as handle:
            data = handle.read(maximum + 1)
        if len(data) > maximum:
            raise PackageRejected
        return data
    except (OSError, ValueError) as exc:
        raise PackageRejected from exc


def _preflight(package: Path) -> None:
    try:
        if package.is_symlink() or not package.is_dir():
            raise PackageRejected
        if {p.name for p in package.iterdir()} != set(FILES):
            raise PackageRejected
        raw = {name: _file_bytes(package / name, MAX_BYTES[name]) for name in FILES}
        manifest = json.loads(raw["manifest.json"])
        if not isinstance(manifest, dict):
            raise PackageRejected
        if set(manifest) != {
            "labels", "experiment", "predicate", "proof_mode", "verifier_target",
            "private_witness_disclosed", "public", "tool_versions", "artifacts",
            "dimensions_not_evaluated",
        }:
            raise PackageRejected
        if (manifest["labels"] != list(LABELS)
                or manifest["experiment"] != "bounded-speed-proof-v0"
                or manifest["predicate"] != "speed_cm_s <= maximum_speed_cm_s"
                or manifest["proof_mode"] != "zero_knowledge"
                or manifest["verifier_target"] != "noir-recursive"
                or manifest["private_witness_disclosed"] is not False):
            raise PackageRejected
        versions = manifest["tool_versions"]
        if (not isinstance(versions, dict)
                or "1.0.0-beta.26" not in versions.get("nargo", "")
                or versions.get("bb") != "5.2.0"):
            raise PackageRejected
        public = manifest["public"]
        if (not isinstance(public, dict) or public.get("schema_version") != 0
                or public.get("assurance_id") != "A0_SYNTHETIC"):
            raise PackageRejected
        decoded = independent_verifier.BOUNDED.decode_public_artifact(raw["public-artifact.cbor"])
        if (decoded["version"] != public["schema_version"]
                or decoded["maximum_speed_cm_s"] != public["maximum_speed_cm_s"]):
            raise PackageRejected
        artifacts = manifest["artifacts"]
        if not isinstance(artifacts, dict) or set(artifacts) != set(FILES) - {"manifest.json"}:
            raise PackageRejected
        for name in ("public-artifact.cbor", "proof", "vk"):
            item = artifacts[name]
            if not isinstance(item, dict) or item.get("sha256") != hashlib.sha256(raw[name]).hexdigest():
                raise PackageRejected
            if name in ("proof", "vk") and item.get("size_bytes") != len(raw[name]):
                raise PackageRejected
    except (OSError, ValueError, TypeError, KeyError, UnicodeError, PackageRejected,
            independent_verifier.BOUNDED.EncodingError) as exc:
        raise PackageRejected from exc


def check_package(package: Path) -> dict[str, Any]:
    """Never accept a cryptographic status or public ordering from the manifest."""
    result = _result()
    try:
        _preflight(package)
    except PackageRejected:
        result["package"] = {"status": "REJECTED", "reason": "UNTRUSTED_OR_INCOMPATIBLE_PACKAGE"}
        return result

    result["package"] = {"status": "ACCEPTED", "reason": None}
    try:
        verified = independent_verifier.verify_public_package(
            package / "public-artifact.cbor", package / "proof", package / "vk"
        )
        result["verification_input"] = {
            "status": verified["input"]["status"],
            "reason": verified["input"].get("reason"),
        }
        result["cryptographic"] = {
            "status": verified["cryptographic"]["status"],
            "reason": verified["cryptographic"].get("reason"),
        }
        result["verification_performed"] = result["cryptographic"]["status"] in {"VALID", "INVALID"}
    except (OSError, ValueError, KeyError, TypeError):
        result["cryptographic"] = {
            "status": "UNVERIFIABLE",
            "reason": "VERIFIER_OPERATIONAL_FAILURE",
        }
    return result


def exit_code(result: dict[str, Any]) -> int:
    if result["package"]["status"] == "REJECTED":
        return 2
    if result["verification_input"]["status"] == "REJECTED":
        return 3
    return {"VALID": 0, "INVALID": 4}.get(result["cryptographic"]["status"], 5)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-dir", type=Path, required=True, help="isolated synthetic proof package only")
    args = parser.parse_args()
    result = check_package(args.package_dir)
    print(json.dumps(result, sort_keys=True, indent=2))
    return exit_code(result)


if __name__ == "__main__":
    raise SystemExit(main())
