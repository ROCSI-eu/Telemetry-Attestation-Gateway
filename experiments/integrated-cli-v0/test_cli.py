#!/usr/bin/env python3
"""Standard-library tests for integrated CLI prototype v0."""

from __future__ import annotations

import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import cli


def valid_demo_result() -> dict[str, object]:
    result = cli.demo._base_result("synthetic-case")
    result["invocation"] = {"status": "ACCEPTED", "reason": None}
    result["telemetry"] = {
        "status": "NORMALIZED",
        "reason": None,
        "assurance_id": "A0_SYNTHETIC",
        "source_trust": "UNSIGNED",
    }
    result["predicate"] = "SATISFIED"
    result["proof_generation"] = "GENERATED"
    result["verification_input"] = {"status": "ACCEPTED", "reason": None}
    result["cryptographic"] = {"status": "VALID", "reason": None}
    return result


def fake_run_fixture(
    capture_file: Path,
    capture_name: str,
    maximum_speed_cm_s: int,
    package_dir: Path,
) -> dict[str, object]:
    package_dir.mkdir(parents=True, exist_ok=True)
    (package_dir / "public-artifact.cbor").write_bytes(
        f"public:{maximum_speed_cm_s}".encode()
    )
    (package_dir / "proof").write_bytes(b"synthetic-proof")
    (package_dir / "vk").write_bytes(b"synthetic-vk")
    result = valid_demo_result()
    result["capture_case"] = capture_name
    return result


class IntegratedCliTests(unittest.TestCase):
    def test_opt_in_loopback_reuses_same_demo_capture_boundary(self) -> None:
        capture = {"decision_received_at_ms": 100, "max_age_ms": 1500,
                   "events": [{"frame_hex": "synthetic-only-private", "received_at_ms": 50}]}
        with patch.object(cli.demo, "run_fixture", side_effect=AssertionError("fixture path")):
            with patch.object(cli.demo, "run_capture", return_value=valid_demo_result()) as run:
                result = cli.run_integrated(
                    cli.MAVLINK_DIR / "fixtures.json", "sitl-loopback", 600,
                    capture_data=capture,
                )
        self.assertEqual(run.call_args.args[:3], ("sitl-loopback", capture, 600))
        self.assertEqual(result["source"]["normalization"], "NORMALIZED")
        self.assertEqual(result["proof"]["cryptographic"]["status"], "VALID")
        self.assertEqual(result["relying_party_decision"], "NOT_MADE")
        self.assertEqual(result["command_path"], "NONE")
        self.assertNotIn("synthetic-only-private", json.dumps(result))

    def test_sitl_capture_cannot_select_publication_or_other_capture(self) -> None:
        for mode, name in (("local", "sitl-loopback"), ("disabled", "other")):
            with self.subTest(mode=mode, name=name):
                with self.assertRaises(ValueError):
                    cli.run_integrated(
                        cli.MAVLINK_DIR / "fixtures.json", name, 600,
                        publication_mode=mode, capture_data={"events": []},
                    )

    def test_sitl_receiver_failure_is_minimized_typed_without_proof(self) -> None:
        from contextlib import redirect_stdout
        from unittest.mock import patch
        with patch.object(cli.sitl_receive, "receive_capture",
                          side_effect=cli.sitl_receive.ReceiveError("SOURCE_LOSS")):
            with patch.object(cli, "run_integrated", side_effect=AssertionError("no proof")):
                with patch("sys.argv", ["cli.py", "--source", "sitl-loopback",
                                        "--maximum-speed-cm-s", "600",
                                        "--format", "json"]):
                    buffer = io.StringIO()
                    with redirect_stdout(buffer):
                        code = cli.main()
        doc = json.loads(buffer.getvalue())
        self.assertEqual(code, 2)
        self.assertEqual(doc["source"]["reason"], "SOURCE_LOSS")
        self.assertEqual(doc["source"]["source_trust"], "NOT_EVALUATED")
        self.assertEqual(doc["proof"]["cryptographic"]["status"], "NOT_CHECKED")
        self.assertEqual(doc["command_path"], "NONE")
        self.assertFalse(any(doc["disclosure"].values()))

    def test_machine_result_keeps_dimensions_and_redacts_private_material(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp) / "package"
            with patch.object(cli.demo, "run_fixture", side_effect=fake_run_fixture):
                result = cli.run_integrated(
                    Path("fixtures.json"),
                    "synthetic-case",
                    600,
                    package_dir=package,
                )

        self.assertEqual(result["source"]["normalization"], "NORMALIZED")
        self.assertEqual(result["claim"]["status"], "SATISFIED")
        self.assertEqual(result["proof"]["cryptographic"]["status"], "VALID")
        self.assertEqual(result["relying_party_decision"], "NOT_MADE")
        self.assertEqual(result["command_path"], "NONE")
        self.assertFalse(any(result["disclosure"].values()))
        encoded = json.dumps(result, sort_keys=True)
        self.assertNotIn("synthetic-proof", encoded)
        self.assertNotIn("frame_hex", encoded)
        self.assertNotIn("idk_", encoded)

    def test_over_limit_stops_before_publication(self) -> None:
        over = valid_demo_result()
        over["predicate"] = "NOT_SATISFIED"
        over["proof_generation"] = "NOT_ATTEMPTED"
        over["verification_input"] = {"status": "NOT_CHECKED", "reason": None}
        over["cryptographic"] = {"status": "NOT_CHECKED", "reason": None}
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp) / "package"
            with patch.object(cli.demo, "run_fixture", return_value=over):
                with patch.object(cli, "_publish") as publish_call:
                    result = cli.run_integrated(
                        Path("fixtures.json"),
                        "synthetic-case",
                        499,
                        publication_mode="local",
                        package_dir=package,
                        publication_state=Path(tmp) / "state.json",
                    )

        publish_call.assert_not_called()
        self.assertEqual(result["claim"]["status"], "NOT_SATISFIED")
        self.assertEqual(result["publication"]["status"], "NOT_ATTEMPTED")
        self.assertEqual(
            result["publication"]["error"]["code"], "CLAIM_NOT_ELIGIBLE"
        )

    def test_local_publication_reconciles_to_final(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp) / "package"
            state = Path(tmp) / "publication.json"
            with patch.object(cli.demo, "run_fixture", side_effect=fake_run_fixture):
                result = cli.run_integrated(
                    Path("fixtures.json"),
                    "synthetic-case",
                    600,
                    publication_mode="local",
                    publication_state=state,
                    package_dir=package,
                )

        publication_result = result["publication"]
        self.assertEqual(publication_result["state"], "final")
        self.assertEqual(publication_result["receipt_state"], "MOCK_FINAL")
        self.assertEqual(publication_result["attempts"], 1)
        self.assertTrue(publication_result["reconciled"])

    def test_retryable_publication_timeout_is_retried_and_reconciled(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp) / "package"
            state = Path(tmp) / "publication.json"
            with patch.object(cli.demo, "run_fixture", side_effect=fake_run_fixture):
                result = cli.run_integrated(
                    Path("fixtures.json"),
                    "synthetic-case",
                    600,
                    publication_mode="local",
                    publication_state=state,
                    publication_fault="timeout",
                    package_dir=package,
                )

        publication_result = result["publication"]
        self.assertEqual(publication_result["state"], "final")
        self.assertEqual(publication_result["attempts"], 2)
        self.assertTrue(publication_result["reconciled"])
        self.assertIsNone(publication_result["error"])

    def test_publication_failure_does_not_rewrite_valid_verification(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp) / "package"
            state = Path(tmp) / "publication.json"
            with patch.object(cli.demo, "run_fixture", side_effect=fake_run_fixture):
                result = cli.run_integrated(
                    Path("fixtures.json"),
                    "synthetic-case",
                    600,
                    publication_mode="local",
                    publication_state=state,
                    publication_fault="definitive_failure",
                    package_dir=package,
                )

        self.assertEqual(result["proof"]["cryptographic"]["status"], "VALID")
        self.assertEqual(result["publication"]["state"], "failed")
        self.assertEqual(
            result["publication"]["error"]["code"], "SUBSTRATE_REJECTED"
        )
        self.assertEqual(cli.exit_code(result), 7)

    def test_tampered_proof_case_uses_independent_verifier_result(self) -> None:
        invalid = {
            "input": {"status": "ACCEPTED", "reason": None},
            "cryptographic": {"status": "INVALID", "reason": "PROOF_REJECTED"},
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
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp) / "package"
            with patch.object(cli.demo, "run_fixture", side_effect=fake_run_fixture):
                with patch.object(
                    cli.demo.proof_verifier,
                    "verify_public_package",
                    return_value=invalid,
                ) as verify_call:
                    result = cli.run_integrated(
                        Path("fixtures.json"),
                        "synthetic-case",
                        600,
                        verification_case="tampered-proof",
                        package_dir=package,
                    )

        self.assertEqual(verify_call.call_count, 1)
        self.assertEqual(result["proof"]["cryptographic"]["status"], "INVALID")
        self.assertEqual(result["publication"]["status"], "NOT_ATTEMPTED")
        self.assertEqual(
            result["publication"]["error"]["code"], "VERIFICATION_NOT_VALID"
        )

    def test_unsupported_version_case_fails_closed_before_crypto(self) -> None:
        rejected = {
            "input": {
                "status": "REJECTED",
                "reason": "PUBLIC_ARTIFACT_MALFORMED_OR_INCOMPATIBLE",
            },
            "cryptographic": {"status": "NOT_CHECKED", "reason": None},
        }
        fake_bounded = type(
            "FakeBounded",
            (),
            {
                "SCHEMA_VERSION": 1,
                "DOMAIN": "domain",
                "STATEMENT": "statement",
                "ASSURANCE_ID": "A0_SYNTHETIC",
                "_encode_value": staticmethod(lambda value: b"unsupported"),
            },
        )
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp) / "package"
            with patch.object(cli.demo, "run_fixture", side_effect=fake_run_fixture):
                with patch.object(cli.demo.proof_prover, "BOUNDED", fake_bounded):
                    with patch.object(
                        cli.demo.proof_verifier,
                        "verify_public_package",
                        return_value=rejected,
                    ):
                        result = cli.run_integrated(
                            Path("fixtures.json"),
                            "synthetic-case",
                            600,
                            verification_case="unsupported-version",
                            package_dir=package,
                        )

        self.assertEqual(result["proof"]["verification_input"]["status"], "REJECTED")
        self.assertEqual(result["proof"]["cryptographic"]["status"], "NOT_CHECKED")
        self.assertEqual(cli.exit_code(result), 6)

    def test_human_output_explains_boundaries_without_private_speed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp) / "package"
            with patch.object(cli.demo, "run_fixture", side_effect=fake_run_fixture):
                result = cli.run_integrated(
                    Path("fixtures.json"),
                    "synthetic-case",
                    600,
                    package_dir=package,
                )

        rendered = cli.render_human(result)
        self.assertIn("private normalized speed <= 600 cm/s", rendered)
        self.assertIn("Relying-party business decision: NOT_MADE", rendered)
        self.assertIn("MAVLink command path: NONE", rendered)
        self.assertIn("Restricted fields disclosed: no", rendered)
        self.assertNotIn("500 cm/s", rendered)

    def test_cli_rejects_arbitrary_capture_file_before_execution(self) -> None:
        with patch.object(
            cli.sys,
            "argv",
            [
                "cli.py",
                "--maximum-speed-cm-s",
                "600",
                "--capture-file",
                "unreviewed-input.json",
            ],
        ):
            with patch.object(cli, "run_integrated") as run_call:
                with patch("sys.stderr", new_callable=io.StringIO) as stderr:
                    with self.assertRaises(SystemExit) as caught:
                        cli.main()

        self.assertEqual(caught.exception.code, 2)
        self.assertIn("unrecognized arguments: --capture-file", stderr.getvalue())
        run_call.assert_not_called()

    def test_cli_json_output_is_machine_readable(self) -> None:
        output = io.StringIO()
        with patch.object(cli.demo, "run_fixture", side_effect=fake_run_fixture):
            with patch.object(
                cli.sys,
                "argv",
                [
                    "cli.py",
                    "--maximum-speed-cm-s",
                    "600",
                    "--format",
                    "json",
                ],
            ):
                with patch("sys.stdout", output):
                    status = cli.main()

        document = json.loads(output.getvalue())
        self.assertEqual(status, 0)
        self.assertEqual(
            document["schema_version"], "TAG_INTEGRATED_CLI_RESULT_V0_EXPERIMENTAL"
        )
        self.assertEqual(document["proof"]["cryptographic"]["status"], "VALID")


if __name__ == "__main__":
    unittest.main()
