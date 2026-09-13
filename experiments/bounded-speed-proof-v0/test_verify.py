#!/usr/bin/env python3
"""Standard-library tests for the synthetic proof/verifier boundary."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch

import common
import prove
import verify


class PublicInputTests(unittest.TestCase):
    def test_context_limbs_are_pinned(self) -> None:
        artifact = common.BOUNDED.encode_public_artifact(1500)
        ordered = common.reconstruct_bb_public_inputs(artifact)
        self.assertEqual([name for name, _ in ordered], ["version", "maximum_speed_cm_s", "context_hi", "context_lo"])
        values = dict(ordered)
        self.assertEqual(values["version"], 0)
        self.assertEqual(values["maximum_speed_cm_s"], 1500)
        self.assertEqual(values["context_hi"], common.CONTEXT_HI)
        self.assertEqual(values["context_lo"], common.CONTEXT_LO)

    def test_public_input_json_has_four_field_elements(self) -> None:
        artifact = common.BOUNDED.encode_public_artifact(1500)
        document = json.loads(common.public_inputs_json(artifact))
        self.assertEqual(len(document["public_inputs"]), 4)
        for value in document["public_inputs"]:
            self.assertRegex(value, r"^0x[0-9a-f]{64}$")

    def test_public_artifact_contains_no_private_speed(self) -> None:
        artifact = common.BOUNDED.encode_public_artifact(1500)
        decoded = common.BOUNDED.decode_public_artifact(artifact)
        self.assertNotIn("speed_cm_s", decoded)
        self.assertEqual(decoded["maximum_speed_cm_s"], 1500)


class FakeVerifierTests(unittest.TestCase):
    def _fake_bb(self, directory: Path, expected_maximum: int = 1500) -> Path:
        script = directory / "bb"
        expected = common.reconstruct_bb_public_inputs(common.BOUNDED.encode_public_artifact(expected_maximum))
        expected_hex = [f"0x{value:064x}" for _, value in expected]
        script.write_text(
            "#!/usr/bin/env python3\nimport json, pathlib, sys\n"
            "if '--version' in sys.argv:\n    print('5.2.0')\n    raise SystemExit(0)\n"
            "if len(sys.argv) < 2 or sys.argv[1] != 'verify':\n    raise SystemExit(9)\n"
            "def arg(flag): return sys.argv[sys.argv.index(flag) + 1]\n"
            "doc = json.loads(pathlib.Path(arg('-i')).read_text())\n"
            f"expected = {expected_hex!r}\n"
            "raise SystemExit(0 if doc.get('public_inputs') == expected else 1)\n",
            encoding="utf-8",
        )
        script.chmod(script.stat().st_mode | stat.S_IXUSR)
        return script

    def test_verifier_reconstructs_expected_inputs_without_witness(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            self._fake_bb(d, 1500)
            artifact = d / "public.cbor"
            proof_path = d / "proof"
            vk = d / "vk"
            artifact.write_bytes(common.BOUNDED.encode_public_artifact(1500))
            proof_path.write_bytes(b"synthetic proof")
            vk.write_bytes(b"synthetic vk")
            expected_vk = hashlib.sha256(b"synthetic vk").hexdigest()
            with patch.object(verify, "EXPECTED_VK_SHA256", expected_vk):
                with patch.dict(os.environ, {"PATH": f"{d}:{os.environ.get('PATH', '')}"}):
                    result = verify.verify_public_package(artifact, proof_path, vk)
            self.assertEqual(result["input"]["status"], "ACCEPTED")
            self.assertEqual(result["cryptographic"]["status"], "VALID")
            self.assertNotIn("valid", result)
            self.assertEqual(result["relying_party_decision"], "NOT_MADE")

    def test_altered_public_limit_changes_verifier_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            self._fake_bb(d, 1500)
            artifact = d / "public.cbor"
            proof_path = d / "proof"
            vk = d / "vk"
            artifact.write_bytes(common.BOUNDED.encode_public_artifact(1501))
            proof_path.write_bytes(b"synthetic proof")
            vk.write_bytes(b"synthetic vk")
            expected_vk = hashlib.sha256(b"synthetic vk").hexdigest()
            with patch.object(verify, "EXPECTED_VK_SHA256", expected_vk):
                with patch.dict(os.environ, {"PATH": f"{d}:{os.environ.get('PATH', '')}"}):
                    result = verify.verify_public_package(artifact, proof_path, vk)
            self.assertEqual(result["cryptographic"]["status"], "INVALID")

    def test_unrecognized_verification_key_is_unverifiable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            self._fake_bb(d, 1500)
            artifact = d / "public.cbor"
            proof_path = d / "proof"
            vk = d / "vk"
            artifact.write_bytes(common.BOUNDED.encode_public_artifact(1500))
            proof_path.write_bytes(b"synthetic proof")
            vk.write_bytes(b"wrong vk")
            with patch.dict(os.environ, {"PATH": f"{d}:{os.environ.get('PATH', '')}"}):
                result = verify.verify_public_package(artifact, proof_path, vk)
            self.assertEqual(result["cryptographic"]["status"], "UNVERIFIABLE")
            self.assertEqual(result["cryptographic"]["reason"], "VERIFICATION_KEY_UNRECOGNIZED")

    def test_malformed_public_artifact_stops_before_tool_lookup(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            artifact = d / "public.cbor"
            proof_path = d / "proof"
            vk = d / "vk"
            artifact.write_bytes(b"\xa0")
            proof_path.write_bytes(b"proof")
            vk.write_bytes(b"vk")
            with patch.dict(os.environ, {"PATH": ""}):
                result = verify.verify_public_package(artifact, proof_path, vk)
            self.assertEqual(result["input"]["status"], "REJECTED")
            self.assertEqual(result["cryptographic"]["status"], "NOT_CHECKED")

    def test_missing_proof_is_unverifiable_not_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            artifact = d / "public.cbor"
            artifact.write_bytes(common.BOUNDED.encode_public_artifact(1500))
            result = verify.verify_public_package(artifact, d / "missing-proof", d / "missing-vk")
            self.assertEqual(result["input"]["status"], "ACCEPTED")
            self.assertEqual(result["cryptographic"]["status"], "UNVERIFIABLE")


class BoundaryTests(unittest.TestCase):
    def test_verifier_has_no_speed_argument(self) -> None:
        source = Path(__file__).with_name("verify.py").read_text(encoding="utf-8")
        self.assertNotIn("--speed-cm-s", source)
        self.assertNotIn("Prover.toml", source)

    def test_typed_dimensions_remain_separate(self) -> None:
        result = verify._base_result()
        for dimension in ("cryptographic", "policy", "freshness", "revocation", "replay", "assurance", "publication", "relying_party_decision"):
            self.assertIn(dimension, result)
        self.assertNotIn("overall_valid", result)
        self.assertNotIn("business_disposition", result)

    def test_over_limit_is_rejected_before_tooling(self) -> None:
        with patch.object(prove, "require_prover_tools") as tools:
            result = prove.prove_package(1501, 1500, Path("/tmp/should-not-be-written-tag-test"))
        tools.assert_not_called()
        self.assertEqual(result["predicate"], "NOT_SATISFIED")
        self.assertEqual(result["cryptographic"], "NOT_ATTEMPTED")
        self.assertFalse(result["package_written"])

    def test_manifest_writer_does_not_take_private_speed(self) -> None:
        self.assertNotIn("speed_cm_s", prove._write_manifest.__annotations__)


if __name__ == "__main__":
    unittest.main(verbosity=2)
