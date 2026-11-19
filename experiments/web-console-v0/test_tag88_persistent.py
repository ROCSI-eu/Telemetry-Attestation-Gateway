#!/usr/bin/env python3
"""Focused unit tests only; no systemd, root, real CLI, SITL or cryptography."""
import http.client
import io
import json
import os
from pathlib import Path
import sys
import tarfile
import tempfile
import threading
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import tag88_service as service
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
                 patch.object(gate.os, "getegid", return_value=1000), \
                 patch.object(gate, "expected_identity", return_value=(1000, 1000)):
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


class PersistentInstallPackageTest(unittest.TestCase):
    def test_install_template_is_rendered_and_disabled(self):
        template = (Path(__file__).with_name("tag-qa88-persistent.service")).read_text()
        rendered = service.unit_render(template, Path("/opt/tag-qa88/release-" + "a" * 40), 991, 992)
        self.assertIn("User=tag-qa88", rendered)
        self.assertIn("Group=tag-qa88", rendered)
        self.assertIn("uid=991,gid=992", rendered)
        self.assertIn("WantedBy=multi-user.target", rendered)
        self.assertIn("Restart=no", rendered)
        self.assertIn("AssertPathExists=!/run/tag-qa88\n", rendered)
        self.assertIn("AssertPathExists=!/run/tag-qa88-mountpoint-owned\n", rendered)
        self.assertIn("ExecStartPre=+/usr/bin/python3", rendered)
        self.assertIn("ExecStopPost=+/usr/bin/python3", rendered)
        self.assertIn("RuntimeDirectory=tag-qa88-control", rendered)
        self.assertNotIn("ReadWritePaths=/run/tag-qa88", rendered)
        self.assertNotIn("RuntimeDirectory=tag-qa88\n", rendered)
        self.assertNotIn("@TAG_", rendered)
        with self.assertRaises(service.Refused):
            service.unit_render(template, Path("/opt/tag-qa88/release"), 0, 992)

    def test_mountpoint_lifecycle_is_exclusive_and_nonprivileged_test(self):
        with tempfile.TemporaryDirectory() as root:
            mount, marker = Path(root) / "mount", Path(root) / "marker"
            with patch.object(service, "MOUNT", mount), patch.object(service, "MARKER", marker), \
                 patch.object(service, "ROOT_UID", os.getuid()), \
                 patch.object(service, "ROOT_GID", os.getgid()), \
                 patch.object(service, "require_root"), \
                 patch.object(service, "is_mount", return_value=False):
                mount.mkdir(mode=0o755)  # systemd host-side mountpoint
                os.chmod(mount, 0o755)
                service.mount_prepare()
                self.assertEqual(mount.stat().st_mode & 0o777, 0o700)
                self.assertEqual(marker.stat().st_mode & 0o777, 0o600)
                with self.assertRaises(service.Refused):
                    service.mount_prepare()  # never overwrite an existing mountpoint
                service.mount_clean()
                self.assertFalse(mount.exists())
                self.assertFalse(marker.exists())
                service.mount_clean()  # no-op after clean stop
                mount.mkdir(mode=0o700)
                with self.assertRaises(service.Refused):
                    service.mount_clean()  # no deletion without an ownership marker
                self.assertTrue(mount.exists())

    def test_mount_prepare_accepts_exclusively_created_absent_path(self):
        with tempfile.TemporaryDirectory() as root:
            mount, marker = Path(root) / "mount", Path(root) / "marker"
            with patch.object(service, "MOUNT", mount), patch.object(service, "MARKER", marker), \
                 patch.object(service, "ROOT_UID", os.getuid()), \
                 patch.object(service, "ROOT_GID", os.getgid()), \
                 patch.object(service, "require_root"), \
                 patch.object(service, "is_mount", return_value=False):
                service.mount_prepare()
                self.assertEqual(mount.stat().st_mode & 0o777, 0o700)
                self.assertEqual(marker.stat().st_mode & 0o777, 0o600)
                service.mount_clean()
                self.assertFalse(mount.exists())
                self.assertFalse(marker.exists())

    def test_mount_prepare_refuses_ambiguous_systemd_path(self):
        codes = {
            "wrong_mode": "MOUNT_MODE_MISMATCH",
            "nonempty": "MOUNT_NOT_EMPTY",
            "marker_present": "MOUNT_MARKER_PRESENT",
            "mounted": "MOUNT_ALREADY_MOUNTED",
            "symlink": "MOUNT_OPEN_FAILED",
            "wrong_owner": "MOUNT_OWNER_MISMATCH",
            "regular_file": "MOUNT_OPEN_FAILED",
        }
        cases = tuple(codes)
        for case in cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as root:
                base = Path(root)
                mount, marker = base / "mount", base / "marker"
                if case == "symlink":
                    target = base / "target"
                    target.mkdir()
                    mount.symlink_to(target)
                elif case == "regular_file":
                    mount.write_text("foreign")
                else:
                    mount.mkdir(mode=0o755)
                    os.chmod(mount, 0o700 if case == "wrong_mode" else 0o755)
                if case == "nonempty":
                    (mount / "foreign").write_text("keep")
                if case == "marker_present":
                    marker.write_text("foreign")
                with patch.object(service, "MOUNT", mount), patch.object(service, "MARKER", marker), \
                     patch.object(service, "ROOT_UID", os.getuid() + (1 if case == "wrong_owner" else 0)), \
                     patch.object(service, "ROOT_GID", os.getgid()), \
                     patch.object(service, "require_root"), \
                     patch.object(service, "is_mount", return_value=case == "mounted"):
                    with self.assertRaises(service.MountRefused) as cm:
                        service.mount_prepare()
                    self.assertEqual(cm.exception.code, codes[case])
                if case == "nonempty":
                    self.assertEqual((mount / "foreign").read_text(), "keep")
                if case == "marker_present":
                    self.assertEqual(marker.read_text(), "foreign")
                else:
                    self.assertFalse(marker.exists())

    def test_mount_diagnostics_are_enumerated_and_nonsecret(self):
        err = io.StringIO()
        with patch.object(service, "mount_prepare",
                          side_effect=service.MountRefused("MOUNT_MODE_MISMATCH")), \
             patch.object(sys, "argv", ["tag88_service.py", "mount-prepare"]), \
             patch.object(sys, "stderr", err):
            self.assertEqual(service.main(), 1)
        self.assertEqual(err.getvalue(),
                         "TAG_INSTALL_FAIL_CLOSED: Refused MOUNT_MODE_MISMATCH\n")
        with self.assertRaises(ValueError):
            service.MountRefused("secret=/run/tag-qa88-control/operator.token")

    def test_mount_prepare_rejects_root_and_marker_creation_error(self):
        with tempfile.TemporaryDirectory() as root:
            mount, marker = Path(root) / "mount", Path(root) / "marker"
            mount.mkdir(mode=0o755)
            os.chmod(mount, 0o755)
            with patch.object(service, "MOUNT", mount), patch.object(service, "MARKER", marker), \
                 patch.object(service, "ROOT_UID", os.getuid()), \
                 patch.object(service, "ROOT_GID", os.getgid()), \
                 patch.object(service, "is_mount", return_value=False):
                with patch.object(service, "require_root",
                                  side_effect=service.Refused("local root authorization required")):
                    with self.assertRaises(service.MountRefused) as cm:
                        service.mount_prepare()
                    self.assertEqual(cm.exception.code, "MOUNT_ROOT_REQUIRED")
                original = os.open
                with patch.object(service, "require_root"), \
                     patch.object(service.os, "open") as opener:
                    def deny_marker(path, flags, *args, **kwargs):
                        if path == marker:
                            raise PermissionError("denied")
                        return original(path, flags, *args, **kwargs)
                    opener.side_effect = deny_marker
                    with self.assertRaises(service.MountRefused) as cm:
                        service.mount_prepare()
                    self.assertEqual(cm.exception.code, "MOUNT_MARKER_CREATE_FAILED")
                self.assertFalse(marker.exists())
                self.assertEqual(mount.stat().st_mode & 0o777, 0o700)

    def test_mount_clean_rejects_unowned_residue(self):
        with tempfile.TemporaryDirectory() as root:
            mount, marker = Path(root) / "mount", Path(root) / "marker"
            mount.mkdir(mode=0o755)
            with patch.object(service, "MOUNT", mount), patch.object(service, "MARKER", marker), \
                 patch.object(service, "ROOT_UID", os.getuid()), \
                 patch.object(service, "ROOT_GID", os.getgid()), \
                 patch.object(service, "require_root"):
                with self.assertRaises(service.MountRefused) as cm:
                    service.mount_clean()
                self.assertEqual(cm.exception.code, "MOUNT_CLEAN_UNOWNED")
                self.assertTrue(mount.exists())

    def test_exact_tree_archive_only_allows_regular_files(self):
        with tempfile.TemporaryDirectory() as root:
            def make_archive(kind):
                data = io.BytesIO()
                with tarfile.open(fileobj=data, mode="w") as tf:
                    item = tarfile.TarInfo("sample.py")
                    if kind == "link":
                        item.type = tarfile.SYMTYPE
                        item.linkname = "/etc/passwd"
                        tf.addfile(item)
                    else:
                        payload = b"print('synthetic')\n"
                        item.size = len(payload)
                        tf.addfile(item, io.BytesIO(payload))
                return data.getvalue()
            with self.assertRaises(service.Refused):
                service.unpack_archive(make_archive("link"), Path(root) / "bad")
            self.assertFalse((Path(root) / "bad").exists())
            result = service.unpack_archive(make_archive("regular"), Path(root) / "ok")
            self.assertIn("sample.py", result)
            self.assertEqual((Path(root) / "ok" / "sample.py").read_text(), "print('synthetic')\n")

    def test_fail_closed_install_without_root_or_sha(self):
        with patch.object(service.os, "geteuid", return_value=1000):
            with self.assertRaises(service.Refused):
                service.install(Path("/tmp"), "a" * 40)
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaises(service.Refused):
                service.git_checked_checkout(Path(root), "bad-sha")


if __name__ == "__main__":
    unittest.main()
