#!/usr/bin/env python3
"""Offline-default tests for local CLI to browser short-circuit operator control.

EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC
NOT VALIDATION OR PRODUCTION AUTHORIZATION
"""
from __future__ import annotations

import http.client
import json
from pathlib import Path
import sys
import threading
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
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
        "source": {"normalization": "NORMALIZED" if scenario == "over_limit" else "REJECTED"},
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
        self.assertEqual(set(bridge.PRESETS), {"over_limit", "malformed_source"})
        self.assertIn("--unshare-net", bridge.execute.__code__.co_consts)
        self.assertIn("127.0.0.1", bridge.Server.__init__.__code__.co_consts)
        self.assertNotIn("WebSocket", bridge.PAGE)
        self.assertNotIn("localStorage", bridge.PAGE)
        self.assertNotIn("sessionStorage", bridge.PAGE)
        self.assertNotIn("navigator.sendBeacon", bridge.PAGE)
        self.assertIn("NOT VALIDATION OR PRODUCTION AUTHORIZATION", bridge.PAGE)

    def test_minimization_never_relays_raw_cli_fields(self):
        for scenario in bridge.PRESETS:
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

    def test_runtime_invokes_only_pinned_args_inside_bwrap(self):
        scenario = "over_limit"
        fake = cli_result(scenario)
        completed = type("P", (), {
            "stdout": json.dumps(fake).encode(), "returncode": 3})()
        with patch.object(bridge, "trusted_bwrap", return_value="/usr/bin/bwrap"):
            with patch.object(bridge.subprocess, "run", return_value=completed) as run:
                result = bridge.execute(scenario)
        args = run.call_args.args[0]
        self.assertEqual(args[0], "/usr/bin/bwrap")
        self.assertIn("--unshare-net", args)
        self.assertEqual(args[-8:], ["--capture-name", "unsigned-consistent",
                                     "--maximum-speed-cm-s", "499", "--format",
                                     "json", "--publication", "disabled"])
        self.assertEqual(run.call_args.kwargs["timeout"], bridge.RUN_SECONDS)
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

    def test_single_operator_run_and_no_raw_fields(self):
        with patch.object(bridge, "execute", return_value=bridge.minimize(
                cli_result(), "over_limit", 3)) as execute:
            code, raw = self.request()
            self.assertEqual(code, 200)
            obj = json.loads(raw)
            self.assertEqual(obj["state"], "COMPLETED")
            self.assertNotIn("DO_NOT_EXPORT", raw)
            self.assertEqual(self.request()[0], 503)
            execute.assert_called_once_with("over_limit")

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
