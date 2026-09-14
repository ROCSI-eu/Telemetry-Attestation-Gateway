#!/usr/bin/env python3
"""Standard-library tests for the local telemetry-to-proof demonstrator."""

from __future__ import annotations

import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import demo


def normalized(speed: int = 500, trust: str = "UNSIGNED") -> dict[str, object]:
    return {
        "status": "NORMALIZED",
        "assurance_id": "A0_SYNTHETIC",
        "source": {"trust": trust},
        "speed_cm_s": speed,
    }


def verifier_result(status: str = "VALID") -> dict[str, object]:
    return {
        "input": {"status": "ACCEPTED", "reason": None},
        "cryptographic": {"status": status, "reason": None},
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
        "proof_validity_is_telemetry_truth": False,
    }


class DemoPipelineTests(unittest.TestCase):
    def _fake_prove(self, observed: list[int]):
        def fake(speed: int, maximum: int, output_dir: Path):
            observed.append(speed)
            output_dir.mkdir(parents=True, exist_ok=True)
            for name in ("public-artifact.cbor", "proof", "vk"):
                (output_dir / name).write_bytes(b"synthetic")
            return {
                "predicate": "SATISFIED",
                "cryptographic": "PROOF_GENERATED_NOT_YET_VERIFIED",
                "package_written": True,
            }

        return fake

    def test_normalized_speed_flows_to_prover_but_not_result(self) -> None:
        observed: list[int] = []
        with patch.object(demo.telemetry, "evaluate_capture", return_value=normalized()):
            with patch.object(
                demo.proof_prover, "prove_package", side_effect=self._fake_prove(observed)
            ):
                with patch.object(
                    demo.proof_verifier,
                    "verify_public_package",
                    return_value=verifier_result(),
                ):
                    result = demo.run_capture("synthetic-case", {}, 600)
        self.assertEqual(observed, [500])
        self.assertEqual(result["cryptographic"]["status"], "VALID")
        self.assertNotIn('"speed_cm_s"', json.dumps(result))
        self.assertFalse(result["private_witness_disclosed"])

    def test_verifier_receives_only_public_package_paths(self) -> None:
        observed: list[int] = []
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp) / "package"
            with patch.object(demo.telemetry, "evaluate_capture", return_value=normalized()):
                with patch.object(
                    demo.proof_prover,
                    "prove_package",
                    side_effect=self._fake_prove(observed),
                ):
                    with patch.object(
                        demo.proof_verifier,
                        "verify_public_package",
                        return_value=verifier_result(),
                    ) as verify_call:
                        demo.run_capture("synthetic-case", {}, 600, package)
        args = verify_call.call_args.args
        self.assertEqual(len(args), 3)
        self.assertTrue(all(isinstance(value, Path) for value in args))

    def test_telemetry_rejection_stops_before_proving(self) -> None:
        rejected = {"status": "REJECTED", "reason_code": "BAD_CRC"}
        with patch.object(demo.telemetry, "evaluate_capture", return_value=rejected):
            with patch.object(demo.proof_prover, "prove_package") as prove_call:
                result = demo.run_capture("bad-crc", {}, 600)
        prove_call.assert_not_called()
        self.assertEqual(result["telemetry"]["status"], "REJECTED")
        self.assertEqual(result["telemetry"]["reason"], "BAD_CRC")
        self.assertEqual(result["cryptographic"]["status"], "NOT_CHECKED")

    def test_over_limit_stops_before_verification(self) -> None:
        over_limit = {
            "predicate": "NOT_SATISFIED",
            "cryptographic": "NOT_ATTEMPTED",
            "package_written": False,
        }
        with patch.object(demo.telemetry, "evaluate_capture", return_value=normalized()):
            with patch.object(
                demo.proof_prover, "prove_package", return_value=over_limit
            ):
                with patch.object(
                    demo.proof_verifier, "verify_public_package"
                ) as verify_call:
                    result = demo.run_capture("synthetic-case", {}, 499)
        verify_call.assert_not_called()
        self.assertEqual(result["predicate"], "NOT_SATISFIED")
        self.assertEqual(result["proof_generation"], "NOT_ATTEMPTED")

    def test_prover_failure_is_unverifiable_not_invalid(self) -> None:
        with patch.object(demo.telemetry, "evaluate_capture", return_value=normalized()):
            with patch.object(
                demo.proof_prover,
                "prove_package",
                side_effect=demo.proof_prover.ExperimentError("test failure"),
            ):
                result = demo.run_capture("synthetic-case", {}, 600)
        self.assertEqual(result["cryptographic"]["status"], "UNVERIFIABLE")
        self.assertEqual(
            result["cryptographic"]["reason"], "PROVER_UNAVAILABLE_OR_FAILED"
        )

    def test_source_trust_remains_separate_from_proof_validity(self) -> None:
        observed: list[int] = []
        with patch.object(
            demo.telemetry,
            "evaluate_capture",
            return_value=normalized(trust="UNKNOWN"),
        ):
            with patch.object(
                demo.proof_prover, "prove_package", side_effect=self._fake_prove(observed)
            ):
                with patch.object(
                    demo.proof_verifier,
                    "verify_public_package",
                    return_value=verifier_result("VALID"),
                ):
                    result = demo.run_capture("synthetic-case", {}, 600)
        self.assertEqual(result["telemetry"]["source_trust"], "UNKNOWN")
        self.assertEqual(result["cryptographic"]["status"], "VALID")
        self.assertEqual(result["assurance"]["effective"], "A0_SYNTHETIC")

    def test_result_keeps_typed_dimensions_and_no_overall_boolean(self) -> None:
        result = demo._base_result("synthetic-case")
        for key in (
            "invocation",
            "telemetry",
            "predicate",
            "cryptographic",
            "policy",
            "freshness",
            "revocation",
            "replay",
            "assurance",
            "publication",
            "relying_party_decision",
        ):
            self.assertIn(key, result)
        self.assertNotIn("overall_valid", result)
        self.assertNotIn("business_disposition", result)
        self.assertEqual(result["command_path"], "NONE")

    def test_invalid_public_limit_is_an_invocation_rejection(self) -> None:
        output = io.StringIO()
        with patch.object(
            demo.sys,
            "argv",
            ["demo.py", "--maximum-speed-cm-s", str(1 << 32)],
        ):
            with patch.object(demo.telemetry, "evaluate_capture") as evaluate_call:
                with patch("sys.stdout", output):
                    status = demo.main()

        evaluate_call.assert_not_called()
        result = json.loads(output.getvalue())
        self.assertEqual(status, 6)
        self.assertEqual(
            result["invocation"],
            {"status": "REJECTED", "reason": "INVALID_PUBLIC_LIMIT"},
        )
        self.assertEqual(result["telemetry"]["status"], "NOT_CHECKED")
        self.assertEqual(result["verification_input"]["status"], "NOT_CHECKED")

    def test_invalid_fixture_root_is_typed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp) / "fixture.json"
            fixture.write_text("[]", encoding="utf-8")
            with self.assertRaises(demo.DemoError) as context:
                demo.load_capture(fixture, "anything")
        self.assertEqual(context.exception.code, "FIXTURE_UNAVAILABLE_OR_INVALID")

    def test_capture_not_found_is_typed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp) / "fixture.json"
            fixture.write_text('{"captures":[]}', encoding="utf-8")
            with self.assertRaises(demo.DemoError) as context:
                demo.load_capture(fixture, "missing")
        self.assertEqual(context.exception.code, "CAPTURE_NOT_FOUND")


if __name__ == "__main__":
    unittest.main(verbosity=2)
