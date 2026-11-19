#!/usr/bin/env python3
"""Focused unit tests only; no systemd, root, real CLI, SITL or cryptography."""
import http.client
import json
import os
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

import local_cli_bridge as bridge
import tag88_persistent_gate as gate


class PersistentBridgeTest(unittest.TestCase):
    def test_single_service_two_sequential_synthetic_requests(self):
        token = "synthetic-only-unit-token"
        with tempfile.TemporaryDirectory() as root:
            with bridge.Server(token, persistent=True, work_root=Path(root)) as server:
                worker = threading.Thread(target=server.serve_forever,
                                          kwargs={"poll_interval": 0.01}, daemon=True)
                worker.start()
                try:
                    port = server.server_port
                    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=3)
                    conn.request("GET", "/operator-capabilities", headers={"Host": f"127.0.0.1:{port}"})
                    response = conn.getresponse()
                    self.assertEqual(response.status, 200)
                    info = json.loads(response.read())
                    self.assertEqual(info["mode"], "PERSISTENT_LOCAL_CLI")
                    self.assertEqual(info["scenarios"], ["over_limit", "malformed_source"])
                    self.assertNotIn(token, json.dumps(info))
                    conn.close()
                    with patch.object(bridge, "execute", return_value={"state": "COMPLETED"}) as execute:
                        for scenario in ("over_limit", "malformed_source"):
                            conn = http.client.HTTPConnection("127.0.0.1", port, timeout=3)
                            conn.request("POST", "/execute", body=json.dumps({"scenario": scenario}),
                                headers={"Host": f"127.0.0.1:{port}",
                                         "Origin": f"http://127.0.0.1:{port}",
                                         "Sec-Fetch-Site": "same-origin",
                                         "Content-Type": "application/json",
                                         "X-TAG-Local-Token": token})
                            response = conn.getresponse()
                            self.assertEqual(response.status, 200)
                            self.assertEqual(json.loads(response.read()), {"state": "COMPLETED"})
                            conn.close()
                            self.assertFalse(server.used)
                            self.assertEqual(list(Path(root).iterdir()), [])
                        self.assertEqual(execute.call_count, 2)
                        for args in execute.call_args_list:
                            self.assertTrue(Path(args.kwargs["shared_work"]).is_absolute())
                    # A proof scenario is denied in persistent mode, before CLI.
                    with patch.object(bridge, "execute") as execute:
                        conn = http.client.HTTPConnection("127.0.0.1", port, timeout=3)
                        conn.request("POST", "/execute", body='{"scenario":"verified_synthetic"}',
                            headers={"Host": f"127.0.0.1:{port}",
                                     "Origin": f"http://127.0.0.1:{port}",
                                     "Sec-Fetch-Site": "same-origin",
                                     "Content-Type": "application/json",
                                     "X-TAG-Local-Token": token})
                        response = conn.getresponse()
                        self.assertEqual(response.status, 503)
                        response.read()
                        conn.close()
                        execute.assert_not_called()
                finally:
                    server.shutdown()
                    worker.join(timeout=3)
                    self.assertFalse(worker.is_alive())

    def test_persistent_failure_releases_lease_and_cleans_workspace(self):
        with tempfile.TemporaryDirectory() as root:
            with bridge.Server("token", persistent=True, work_root=Path(root)) as server:
                thread = threading.Thread(target=server.serve_forever,
                                          kwargs={"poll_interval": 0.01}, daemon=True)
                thread.start()
                try:
                    with patch.object(bridge, "execute", side_effect=bridge.Rejected):
                        for _ in range(2):
                            conn = http.client.HTTPConnection("127.0.0.1", server.server_port)
                            conn.request("POST", "/execute", '{"scenario":"over_limit"}',
                                headers={"Host": f"127.0.0.1:{server.server_port}",
                                    "Origin": f"http://127.0.0.1:{server.server_port}",
                                    "Sec-Fetch-Site": "same-origin",
                                    "Content-Type": "application/json",
                                    "X-TAG-Local-Token": "token"})
                            response = conn.getresponse()
                            self.assertEqual(response.status, 503)
                            response.read()
                            conn.close()
                            self.assertFalse(server.used)
                            self.assertFalse(list(Path(root).iterdir()))
                finally:
                    server.shutdown()
                    thread.join(timeout=3)

    def test_bwrap_cli_tmp_reuses_exact_outer_workdir(self):
        with tempfile.TemporaryDirectory() as root:
            with patch.object(bridge, "_bounded_run", return_value=(b"{}", 3)) as runner, \
                 patch.object(bridge, "minimize", return_value={}):
                bridge.execute("over_limit", shared_work=Path(root))
                argv = runner.call_args.args[0]
                self.assertIn("--unshare-net", argv)
                self.assertIn("--bind", argv)
                idx = argv.index("--bind")
                self.assertEqual(argv[idx + 1:idx + 3], [root, "/tmp"])
                self.assertNotIn("--tmpfs", argv)
                self.assertNotIn("--size", argv)
                self.assertNotIn("verified_synthetic", argv)
        with self.assertRaises(bridge.Rejected):
            bridge.execute("over_limit", shared_work=Path("/tmp"), toolchain_root=Path("/foo"))

    def test_one_shot_default_is_unchanged(self):
        with bridge.Server("one-shot") as server:
            self.assertFalse(server.persistent)
            self.assertEqual(tuple(server.scenarios), tuple(bridge.PRESETS))
            self.assertIsNone(server.work_root)


class PersistentGateTest(unittest.TestCase):
    def test_cgroup_fail_closed_on_limits_or_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            proc = base / "proc"
            group = base / "sys" / gate.EXPECTED_CGROUP.lstrip("/")
            (proc / "self").mkdir(parents=True)
            group.mkdir(parents=True)
            (proc / "self/status").write_text("CapEff:\t0000000000000000\nNoNewPrivs:\t1\n")
            (proc / "self/cgroup").write_text("0::" + gate.EXPECTED_CGROUP + "\n")
            for key, value in gate.EXPECTED_LIMITS.items():
                (group / key).write_text(value + "\n")
            with patch.object(gate.os, "geteuid", return_value=1000), \
                 patch.object(gate.os, "getegid", return_value=1000):
                gate.verify_identity_and_cgroup(proc=proc, cgroup_root=base / "sys")
                (group / "memory.swap.max").write_text("max")
                with self.assertRaises(gate.GateRejected):
                    gate.verify_identity_and_cgroup(proc=proc, cgroup_root=base / "sys")
                (group / "memory.swap.max").write_text("0")
                (proc / "self/status").write_text("CapEff:\t0000000000000000\nNoNewPrivs:\t0\n")
                with self.assertRaises(gate.GateRejected):
                    gate.verify_identity_and_cgroup(proc=proc, cgroup_root=base / "sys")
                (proc / "self/status").write_text("CapEff:\t0000000000000001\nNoNewPrivs:\t1\n")
                with self.assertRaises(gate.GateRejected):
                    gate.verify_identity_and_cgroup(proc=proc, cgroup_root=base / "sys")

    def test_persistent_gate_rejects_unexpected_paths_without_mutation(self):
        with self.assertRaises(gate.GateRejected):
            gate.persistent_preflight(Path("/tmp"), Path("/tmp/token"))

    def test_credential_file_never_in_program_output(self):
        # Static assertion: the persistent path has no token print, only URL.
        from inspect import getsource
        source = getsource(bridge.main)
        clause = source.split("if args.persistent:", 1)[1].split("if args.runtime_root is not None", 1)[0]
        self.assertNotIn('print(token)', clause)
        self.assertNotIn('print(server.token)', clause)
        self.assertIn("exclusive_token_file", clause)


if __name__ == "__main__":
    unittest.main()
