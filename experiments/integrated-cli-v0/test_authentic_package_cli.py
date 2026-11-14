#!/usr/bin/env python3
"""Offline fixture tests; no cryptographic toolchain is installed or invoked by CI.

EXPERIMENTAL
SYNTHETIC_ONLY
A0_SYNTHETIC
NOT VALIDATION OR PRODUCTION AUTHORIZATION
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import authentic_package_cli as authentic  # noqa: E402


def synthetic_package(folder: Path) -> None:
    """Generate fake bytes for schema tests only, never a genuine proof."""
    folder.mkdir()
    public = authentic.independent_verifier.BOUNDED.encode_public_artifact(1500)
    artifacts = {
        "public-artifact.cbor": public,
        "proof": b"FAKE_NOT_A_PROOF",
        "vk": b"FAKE_NOT_A_KEY",
    }
    for name, data in artifacts.items():
        (folder / name).write_bytes(data)
    manifest = {
        "labels": list(authentic.LABELS),
        "experiment": "bounded-speed-proof-v0",
        "predicate": "speed_cm_s <= maximum_speed_cm_s",
        "proof_mode": "zero_knowledge",
        "verifier_target": "noir-recursive",
        "private_witness_disclosed": False,
        "public": {"schema_version": 0, "maximum_speed_cm_s": 1500, "assurance_id": "A0_SYNTHETIC"},
        "tool_versions": {"nargo": "nargo version = 1.0.0-beta.26", "bb": "5.2.0"},
        "artifacts": {
            name: {
                "sha256": hashlib.sha256(data).hexdigest(),
                **({"size_bytes": len(data)} if name != "public-artifact.cbor" else {}),
            }
            for name, data in artifacts.items()
        },
        "dimensions_not_evaluated": ["source_trust", "policy", "freshness", "revocation", "replay"],
    }
    (folder / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


def verifier_result(status: str, reason: str | None = None) -> dict:
    return {
        "input": {"status": "ACCEPTED", "reason": None},
        "cryptographic": {"status": status, "reason": reason},
    }


class AuthenticResultContractTests(unittest.TestCase):
    def test_validated_package_invokes_independent_verifier_not_mock(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            package = Path(root) / "package"
            synthetic_package(package)
            with patch.object(authentic.independent_verifier, "verify_public_package",
                              return_value=verifier_result("VALID")) as verify:
                result = authentic.check_package(package)
            verify.assert_called_once_with(
                package / "public-artifact.cbor", package / "proof", package / "vk"
            )
        self.assertEqual(result["cryptographic"]["status"], "VALID")
        self.assertTrue(result["verification_performed"])
        self.assertFalse(result["mock"])
        self.assertEqual(result["proof_generation"], "NOT_OBSERVED")
        self.assertEqual(result["source_trust"], "NOT_EVALUATED")
        self.assertEqual(result["publication"], "NOT_PERFORMED")
        self.assertEqual(result["relying_party_decision"], "NOT_MADE")
        self.assertEqual(result["command_path"], "NONE")
        self.assertFalse(result["private_witness_disclosed"])
        self.assertEqual(authentic.exit_code(result), 0)
        encoded = json.dumps(result)
        self.assertNotIn("FAKE_NOT_A_PROOF", encoded)
        self.assertNotIn("FAKE_NOT_A_KEY", encoded)
        self.assertNotIn("speed_cm_s\": 1200", encoded)

    def test_rejected_digest_does_not_invoke_verifier(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            package = Path(root) / "package"
            synthetic_package(package)
            (package / "proof").write_bytes(b"ALTERED")
            with patch.object(authentic.independent_verifier, "verify_public_package") as verify:
                result = authentic.check_package(package)
            verify.assert_not_called()
        self.assertEqual(result["package"]["status"], "REJECTED")
        self.assertEqual(result["cryptographic"]["status"], "NOT_CHECKED")
        self.assertEqual(authentic.exit_code(result), 2)

    def test_metadata_claims_cannot_override_verifier(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            package = Path(root) / "package"
            synthetic_package(package)
            manifest = json.loads((package / "manifest.json").read_text())
            manifest["cryptographic"] = {"status": "VALID"}
            (package / "manifest.json").write_text(json.dumps(manifest))
            with patch.object(authentic.independent_verifier, "verify_public_package") as verify:
                result = authentic.check_package(package)
            verify.assert_not_called()
        self.assertEqual(result["package"]["status"], "REJECTED")

    def test_unrecognized_key_or_invalid_proof_never_becomes_valid(self) -> None:
        for status, reason, code in (
            ("INVALID", "PROOF_REJECTED", 4),
            ("UNVERIFIABLE", "VERIFICATION_KEY_UNRECOGNIZED", 5),
        ):
            with self.subTest(status=status), tempfile.TemporaryDirectory() as root:
                package = Path(root) / "package"
                synthetic_package(package)
                with patch.object(authentic.independent_verifier, "verify_public_package",
                                  return_value=verifier_result(status, reason)):
                    result = authentic.check_package(package)
                self.assertEqual(result["cryptographic"]["status"], status)
                self.assertEqual(authentic.exit_code(result), code)
                self.assertEqual(result["verification_performed"], status == "INVALID")

    def test_symlinks_and_extra_material_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            package = Path(root) / "package"
            synthetic_package(package)
            (package / "Prover.toml").write_text("private material")
            self.assertEqual(authentic.check_package(package)["package"]["status"], "REJECTED")
            (package / "Prover.toml").unlink()
            (package / "vk").unlink()
            (package / "vk").symlink_to(package / "proof")
            self.assertEqual(authentic.check_package(package)["package"]["status"], "REJECTED")

    def test_missing_or_invalid_package_is_untrusted(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            for path in (Path(root) / "missing", Path(root)):
                self.assertEqual(authentic.check_package(path)["package"]["status"], "REJECTED")


if __name__ == "__main__":
    unittest.main()
