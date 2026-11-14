#!/usr/bin/env python3
"""Offline-default tests for local CLI to browser short-circuit operator control.

EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC
NOT VALIDATION OR PRODUCTION AUTHORIZATION
"""
from __future__ import annotations

import http.client
import json
import socket
import subprocess
import time
from pathlib import Path
import sys
import threading
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "integrated-cli-v0"))
import local_cli_bridge as bridge  # noqa: E402


def cli_result(scenario="over_limit"):
    capture, bound, _, claim = bridge.PRESETS[scenario]
    return {
        "schema_version": "TAG_INTEGRATED_CLI_RESULT_V0_EXPERIMENTAL",
        "labels": list(bridge.LABELS),
        "capture_case": capture, "command_path": "NONE",
        "relying_party_decision": "NOT_MADE",
        "proof_validity_is_telemetry_truth": False,
        "claim": {"maximum_speed_cm_s": int(bound), "status": claim,
                  "private_observation_disclosed": False},
        "source": {"normalization": "REJECTED" if scenario == "malformed_source" else "NORMALIZED"},
        "proof": {"generation": "NOT_ATTEMPTED",
                  "cryptographic": {"status": "NOT_CHECKED"}},
        "publication": {"mode": "disabled", "state": "NOT_PERFORMED"},
        "disclosure": dict.fromkeys(
            ("raw_telemetry", "exact_normalized_speed", "private_witness",
             "proof_secrets", "stable_identity"), False),
        # Adversarial upstream fields must never reach HTTP:
        "proof_bytes": "DO_NOT_EXPORT",
        "witness": "DO_NOT_EXPORT",
        "private_speed": 500,
    }


class BridgeUnitTests(unittest.TestCase):
    def test_only_pre_proof_short_circuit_cases_are_pinned(self):
        self.assertEqual(set(bridge.PRESETS), {"over_limit", "malformed_source", "verified_synthetic"})
        self.assertIn("--unshare-net", bridge.execute.__code__.co_consts)
        self.assertIn("127.0.0.1", bridge.Server.__init__.__code__.co_consts)
        self.assertNotIn("WebSocket", bridge.PAGE)
        self.assertNotIn("localStorage", bridge.PAGE)
        self.assertNotIn("sessionStorage", bridge.PAGE)
        self.assertNotIn("navigator.sendBeacon", bridge.PAGE)
        self.assertIn("NOT VALIDATION OR PRODUCTION AUTHORIZATION", bridge.PAGE)

    def test_minimization_never_relays_raw_cli_fields(self):
        for scenario in ("over_limit", "malformed_source"):
            _, _, exit_code, claim = bridge.PRESETS[scenario]
            minimized = bridge.minimize(cli_result(scenario), scenario, exit_code)
            serialized = json.dumps(minimized)
            self.assertEqual(minimized["claim"], claim)
            self.assertEqual(minimized["cryptographic"], "NOT_CHECKED")
            self.assertEqual(minimized["proof_generation"], "NOT_ATTEMPTED")
            self.assertFalse(minimized["restricted_fields_disclosed"])
            self.assertFalse(minimized["browser_verified"])
            for restricted in ("DO_NOT_EXPORT", "private_speed", "witness",
                               "proof_bytes", "500", "capture_case"):
                self.assertNotIn(restricted, serialized)

    def test_fail_closed_on_wrong_exit_proof_publication_and_disclosure(self):
        base = cli_result()
        for mutation in ("exit", "proof", "crypto", "source", "publication",
                         "disclosure", "label", "limit", "decision", "extra_disclosure"):
            with self.subTest(mutation=mutation):
                item = json.loads(json.dumps(base))
                exit_code = 3
                if mutation == "exit": exit_code = 0
                elif mutation == "proof": item["proof"]["generation"] = "GENERATED"
                elif mutation == "crypto": item["proof"]["cryptographic"]["status"] = "VALID"
                elif mutation == "source": item["source"]["normalization"] = "REJECTED"
                elif mutation == "publication": item["publication"]["mode"] = "local"
                elif mutation == "disclosure": item["disclosure"]["private_witness"] = True
                elif mutation == "label": item["labels"] = []
                elif mutation == "limit": item["claim"]["maximum_speed_cm_s"] = 600
                elif mutation == "decision": item["relying_party_decision"] = "APPROVED"
                elif mutation == "extra_disclosure": item["disclosure"]["identity"] = False
                with self.assertRaises(bridge.Rejected):
                    bridge.minimize(item, "over_limit", exit_code)

    def test_genuine_synthetic_result_is_allowlisted_and_distinct(self):
        doc = cli_result("verified_synthetic")
        doc["proof"]["generation"] = "GENERATED"
        doc["proof"]["cryptographic"] = {"status": "VALID", "reason": None}
        doc["proof"]["verification_input"] = {"status": "ACCEPTED", "reason": None}
        doc["source"]["assurance_id"] = "A0_SYNTHETIC"
        doc["source"]["source_trust"] = "UNSIGNED"
        doc["publication"] = {
            "mode": "disabled", "state": "failed", "status": "FAILED",
            "attempts": 1, "reconciled": True, "receipt_state": "NOT_ISSUED",
            "record_id": "rec_internal_synthetic_only",
            "error": {"code": "PUBLICATION_DISABLED",
                      "classification": "definitive", "retryable": False},
        }
        doc["verification_dimensions"] = {
            "policy": "NOT_EVALUATED", "freshness": "NOT_EVALUATED",
            "revocation": "NOT_EVALUATED", "replay": "NOT_EVALUATED",
            "assurance": {
                "declared": "A0_SYNTHETIC", "effective": "A0_SYNTHETIC",
                "required": "NOT_EVALUATED", "demonstrator": "A0_SYNTHETIC",
            },
        }
        output = bridge.minimize(doc, "verified_synthetic", 0)
        self.assertEqual(output["proof_generation"], "GENERATED")
        self.assertEqual(output["cryptographic"], "VALID")
        self.assertEqual(output["verification_input"], "ACCEPTED")
        self.assertFalse(output["browser_verified"])
        self.assertFalse(output["proof_validity_is_telemetry_truth"])
        self.assertEqual(output["publication"], "NOT_PERFORMED")
        self.assertNotIn("rec_internal_synthetic_only", json.dumps(output))
        for name in ("witness", "proof_bytes", "private_speed", "capture_case"):
            self.assertNotIn(name, output)
        for mutation in ("wrong_exit", "missing_verification", "fake_crypto",
                         "bad_trust", "bad_assurance", "bad_policy",
                         "publication_mode", "publication_state", "publication_code",
                         "publication_class", "publication_retry", "publication_attempts",
                         "publication_receipt", "publication_reconciliation"):
            candidate = json.loads(json.dumps(doc))
            code = 0
            if mutation == "wrong_exit": code = 5
            elif mutation == "missing_verification":
                candidate["proof"]["verification_input"]["status"] = "NOT_CHECKED"
            elif mutation == "fake_crypto":
                candidate["proof"]["cryptographic"]["status"] = "NOT_CHECKED"
            elif mutation == "bad_trust":
                candidate["source"]["source_trust"] = "SIGNED"
            elif mutation == "bad_assurance":
                candidate["verification_dimensions"]["assurance"]["effective"] = "A1"
            elif mutation == "bad_policy":
                candidate["verification_dimensions"]["policy"] = "ACCEPTED"
            elif mutation == "publication_mode":
                candidate["publication"]["mode"] = "local"
            elif mutation == "publication_state":
                candidate["publication"]["state"] = "final"
            elif mutation == "publication_code":
                candidate["publication"]["error"]["code"] = "SUBSTRATE_REJECTED"
            elif mutation == "publication_class":
                candidate["publication"]["error"]["classification"] = "retryable"
            elif mutation == "publication_retry":
                candidate["publication"]["error"]["retryable"] = True
            elif mutation == "publication_attempts":
                candidate["publication"]["attempts"] = 2
            elif mutation == "publication_receipt":
                candidate["publication"]["receipt_state"] = "MOCK_FINAL"
            elif mutation == "publication_reconciliation":
                candidate["publication"]["reconciled"] = False
            with self.subTest(mutation=mutation):
                with self.assertRaises(bridge.Rejected):
                    bridge.minimize(candidate, "verified_synthetic", code)

    def test_disabled_adapter_real_contract_is_accepted_without_exposing_record_id(self):
        """Use the actual repository DisabledAdapter, not an invented publication status."""
        import cli as integrated
        pub = integrated.publication
        request = pub.PublicationRequest(
            idempotency_key="idk_" + "a" * 32,
            payload_digest=pub.synthetic_payload_digest("proof-contract-regression"),
            metadata={"scenario": "synthetic-proof-contract"},
        )
        adapter = pub.DisabledAdapter()
        submitted = adapter.submit(request)
        checked = adapter.status(submitted["record_id"])
        actual = integrated._summarize_publication(
            "disabled", checked, attempts=1, reconciled=True)
        self.assertEqual(actual["state"], "failed")
        self.assertEqual(actual["error"]["code"], "PUBLICATION_DISABLED")
        doc = cli_result("verified_synthetic")
        doc["proof"]["generation"] = "GENERATED"
        doc["proof"]["cryptographic"] = {"status": "VALID", "reason": None}
        doc["proof"]["verification_input"] = {"status": "ACCEPTED", "reason": None}
        doc["source"].update({"assurance_id": "A0_SYNTHETIC", "source_trust": "UNSIGNED"})
        doc["verification_dimensions"] = {
            "policy": "NOT_EVALUATED", "freshness": "NOT_EVALUATED",
            "revocation": "NOT_EVALUATED", "replay": "NOT_EVALUATED",
            "assurance": {
                "declared": "A0_SYNTHETIC", "effective": "A0_SYNTHETIC",
                "required": "NOT_EVALUATED", "demonstrator": "A0_SYNTHETIC",
            },
        }
        doc["publication"] = actual
        minimized = bridge.minimize(doc, "verified_synthetic", 0)
        self.assertEqual(minimized["cryptographic"], "VALID")
        self.assertEqual(minimized["publication"], "NOT_PERFORMED")
        self.assertNotIn(checked["record_id"], json.dumps(minimized))
        self.assertNotIn("record_id", minimized)

    def test_proof_cannot_start_without_explicit_private_toolchain(self):
        with patch.object(bridge, "_bounded_run") as worker:
            with self.assertRaises(bridge.Rejected):
                bridge.execute("verified_synthetic")
            worker.assert_not_called()

    def test_preprovisioned_toolchain_is_only_used_by_real_proof_case(self):
        with patch.object(bridge, "trusted_bwrap", return_value="/usr/bin/bwrap"):
            with patch.object(bridge, "offline_toolchain", return_value=Path("/private/offline")):
                with patch.object(bridge, "_bounded_run",
                                  return_value=(b"{}", 5)) as worker:
                    with self.assertRaises(bridge.Rejected):
                        bridge.execute("verified_synthetic", Path("/private/offline"))
        args = worker.call_args.args[0]
        self.assertEqual(args[0], "/usr/bin/bwrap")
        self.assertIn("--unshare-net", args)
        self.assertIn("--die-with-parent", args)
        self.assertEqual(args[args.index("--ro-bind", args.index("--die-with-parent"))+1], "/usr")
        self.assertIn("/private/offline/bin:/usr/bin:/bin", args)
        self.assertEqual(worker.call_args.kwargs["timeout"], bridge.PROOF_RUN_SECONDS)
        self.assertEqual(worker.call_args.kwargs["extra_path"],
                         "/private/offline/bin:/usr/bin:/bin")

    def test_bounded_stdout_rejects_oversize_and_kills_process_group(self):
        oversized = ("import sys; sys.stdout.write('X'*"
                     + str(bridge.MAX_OUTPUT + 8192) + "); sys.stdout.flush()")
        with self.assertRaises(bridge.Rejected):
            bridge._bounded_run([sys.executable, "-c", oversized])

    def test_bounded_stdout_timeout_rejects_with_no_leaking_child(self):
        with patch.object(bridge, "RUN_SECONDS", 0.15):
            started = time.monotonic()
            with self.assertRaises(bridge.Rejected):
                bridge._bounded_run([sys.executable, "-c",
                                     "import time; time.sleep(5)"])
            self.assertLess(time.monotonic() - started, 2.0)

    def test_runtime_invokes_only_pinned_args_inside_bwrap(self):
        scenario = "over_limit"
        fake = cli_result(scenario)
        with patch.object(bridge, "trusted_bwrap", return_value="/usr/bin/bwrap"):
            with patch.object(bridge, "_bounded_run",
                              return_value=(json.dumps(fake).encode(), 3)) as run:
                result = bridge.execute(scenario)
        args = run.call_args.args[0]
        self.assertEqual(args[0], "/usr/bin/bwrap")
        self.assertIn("--unshare-net", args)
        self.assertIn("--die-with-parent", args)
        self.assertNotIn("--ro-bind", args[:1])
        self.assertNotIn("--dev-bind", args)
        self.assertNotIn("/", [args[i + 1] for i, arg in enumerate(args[:-2])
                                if arg == "--ro-bind"])
        self.assertEqual([args[i + 1] for i, arg in enumerate(args[:-2])
                          if arg == "--ro-bind"],
                         ["/usr", str(bridge.HERE.parent)])
        self.assertEqual(args[-8:], ["--capture-name", "unsigned-consistent",
                                     "--maximum-speed-cm-s", "499", "--format",
                                     "json", "--publication", "disabled"])
        self.assertEqual(run.call_count, 1)
        self.assertEqual(result["state"], "COMPLETED")
        with self.assertRaises(bridge.Rejected):
            bridge.execute("arbitrary-command")


class BridgeHttpTests(unittest.TestCase):
    def setUp(self):
        self.server = bridge.Server("synthetic-test-only-token")
        self.worker = threading.Thread(target=self.server.serve_forever,
                                       kwargs={"poll_interval": 0.02}, daemon=True)
        self.worker.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.worker.join(timeout=2)

    def request(self, path="/execute", scenario="over_limit", token="synthetic-test-only-token",
                origin=True, host=True, body=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        doc = json.dumps({"scenario": scenario}) if body is None else body
        headers = {"Host": f"127.0.0.1:{self.server.server_port}" if host else "attacker.test",
                   "Content-Type": "application/json",
                   "X-TAG-Local-Token": token}
        if origin:
            headers["Origin"] = f"http://127.0.0.1:{self.server.server_port}"
        conn.request("POST", path, body=doc, headers=headers)
        response = conn.getresponse()
        data = response.read().decode()
        status = response.status
        conn.close()
        return status, data

    def test_preflight_rejects_cross_origin_and_bad_token_without_execution(self):
        with patch.object(bridge, "execute") as execute:
            for kw in ({"token": "wrong"}, {"origin": False},
                       {"host": False}, {"path": "/anything"}):
                with self.subTest(kwargs=kw):
                    code, _ = self.request(**kw)
                    self.assertEqual(code, 403)
            execute.assert_not_called()
            self.assertFalse(self.server.used)

    def test_incomplete_http_body_times_out_and_does_not_consume_run(self):
        with patch.object(bridge, "HTTP_READ_SECONDS", 0.2):
            # The socket timeout is set when the handler is initialized.
            # Rebind setup for this one request only through the class constant.
            conn = socket.create_connection(("127.0.0.1", self.server.server_port), 2)
            try:
                headers = (
                    f"POST /execute HTTP/1.1\r\n"
                    f"Host: 127.0.0.1:{self.server.server_port}\r\n"
                    f"Origin: http://127.0.0.1:{self.server.server_port}\r\n"
                    "Sec-Fetch-Site: same-origin\r\n"
                    "Content-Type: application/json\r\n"
                    "X-TAG-Local-Token: synthetic-test-only-token\r\n"
                    "Content-Length: 64\r\n\r\n"
                    '{"scenario":"over_limit"}'
                )
                conn.sendall(headers.encode())
                conn.settimeout(2)
                reply = conn.recv(4096)
                self.assertIn(b"503", reply)
                self.assertFalse(self.server.used)
            finally:
                conn.close()

    def _assert_drip_does_not_hold_server(self, prefix: bytes):
        """A peer keeps sending data, yet the next request must be accepted."""
        with patch.object(bridge, "HTTP_READ_SECONDS", 0.18):
            conn = socket.create_connection(
                ("127.0.0.1", self.server.server_port), 2
            )
            stop = threading.Event()
            started = threading.Event()
            def drip():
                try:
                    conn.sendall(prefix)
                    started.set()
                    while not stop.wait(0.04):
                        conn.sendall(b"X")
                except OSError:
                    started.set()

            worker = threading.Thread(target=drip, daemon=True)
            worker.start()
            try:
                self.assertTrue(started.wait(timeout=1))
                # Original per-read socket timeout did not help: a slow peer
                # could indefinitely occupy the single-threaded HTTPServer.
                time.sleep(0.32)
                began = time.monotonic()
                self.assertEqual(self.request(token="wrong")[0], 403)
                self.assertLess(time.monotonic() - began, 0.7)
                self.assertFalse(self.server.used)
            finally:
                stop.set()
                try:
                    conn.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                conn.close()
                worker.join(timeout=1)
                self.assertFalse(worker.is_alive())

    def test_slow_drip_headers_have_absolute_deadline(self):
        self._assert_drip_does_not_hold_server(
            b"POST /execute HTTP/1.1\r\nX-Partial: "
        )

    def test_slow_drip_body_cannot_consume_operator_run(self):
        prefix = (
            f"POST /execute HTTP/1.1\r\n"
            f"Host: 127.0.0.1:{self.server.server_port}\r\n"
            f"Origin: http://127.0.0.1:{self.server.server_port}\r\n"
            "Sec-Fetch-Site: same-origin\r\n"
            "Content-Type: application/json\r\n"
            "X-TAG-Local-Token: synthetic-test-only-token\r\n"
            "Content-Length: 64\r\n\r\n"
            '{"scenario":'
        ).encode()
        self._assert_drip_does_not_hold_server(prefix)

    def test_genuine_proof_http_fails_closed_without_offline_toolchain(self):
        with patch.object(bridge, "_bounded_run") as worker:
            code, response = self.request(scenario="verified_synthetic")
        self.assertEqual(code, 503)
        self.assertEqual(json.loads(response), {"error": "UNAVAILABLE"})
        self.assertTrue(self.server.used)
        worker.assert_not_called()
        self.assertEqual(self.request(scenario="over_limit")[0], 503)

    def test_single_operator_run_and_no_raw_fields(self):
        with patch.object(bridge, "execute", return_value=bridge.minimize(
                cli_result(), "over_limit", 3)) as execute:
            code, raw = self.request()
            self.assertEqual(code, 200)
            obj = json.loads(raw)
            self.assertEqual(obj["state"], "COMPLETED")
            self.assertNotIn("DO_NOT_EXPORT", raw)
            self.assertEqual(self.request()[0], 503)
            execute.assert_called_once_with("over_limit", None)

    def test_invalid_payload_does_not_consume_run_and_failure_cannot_retry(self):
        with patch.object(bridge, "execute", side_effect=bridge.Rejected):
            self.assertEqual(self.request(body='{"scenario":"over_limit","x":1}')[0], 503)
            self.assertFalse(self.server.used)
            self.assertEqual(self.request()[0], 503)
            self.assertTrue(self.server.used)
            self.assertEqual(self.request()[0], 503)

    def test_get_is_only_static_html_and_no_store(self):
        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_port)
        conn.request("GET", "/", headers={"Host": f"127.0.0.1:{self.server.server_port}"})
        res = conn.getresponse()
        body = res.read()
        self.assertEqual(res.status, 200)
        self.assertEqual(res.getheader("Cache-Control"), "no-store")
        self.assertIn(b"One-session operator token", body)
        conn.close()


if __name__ == "__main__":
    unittest.main()
