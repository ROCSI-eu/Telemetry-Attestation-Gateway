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

    def mount_case(self, root, *, private=False):
        """Private mount and PID1 host views are separate fake filesystems."""
        base = Path(root)
        self_host = base / "host"
        self_private = base / "private"
        self_host.mkdir()
        self_private.mkdir()
        mount = self_private / "mnt"
        host = self_host / "mnt"
        marker = self_private / "marker"
        host.mkdir(mode=0o755)
        os.chmod(host, 0o755)
        if private:
            mount.mkdir(mode=0o700)
            os.chmod(mount, 0o700)
        else:
            mount = host
            marker = base / "marker"

        from types import SimpleNamespace
        flags = {"nodev", "nosuid", "noexec"}
        def mount_row(path, table):
            if str(table) == "/proc/1/mountinfo":
                return None
            return ("tmpfs", flags) if private else None
        def host_view(path):
            if path == mount:
                return host
            if path == mount.parent:
                return host.parent
            raise AssertionError("unexpected host path")
        def fake_statvfs(fd):
            return SimpleNamespace(f_blocks=2048, f_frsize=4096, f_files=128)
        return mount, host, marker, mount_row, host_view, fake_statvfs

    def test_host_only_mount_prepare_and_clean(self):
        with tempfile.TemporaryDirectory() as root:
            mount, host, marker, rows, view, vfs = self.mount_case(root)
            with patch.object(service, "MOUNT", mount), patch.object(service, "MARKER", marker), \
                 patch.object(service, "ROOT_UID", os.getuid()), \
                 patch.object(service, "ROOT_GID", os.getgid()), \
                 patch.object(service, "require_root"), \
                 patch.object(service, "_mount_row", side_effect=rows), \
                 patch.object(service, "_host_view", side_effect=view):
                service.mount_prepare()
                self.assertEqual(mount.stat().st_mode & 0o777, 0o700)
                self.assertEqual(marker.stat().st_mode & 0o777, 0o600)
                with self.assertRaises(service.MountRefused) as cm:
                    service.mount_prepare()
                self.assertEqual(cm.exception.code, "MOUNT_MARKER_PRESENT")
                service.mount_clean()
                self.assertFalse(mount.exists())
                self.assertFalse(marker.exists())
                service.mount_clean()

    def test_host_absent_is_created_exclusively_and_removed(self):
        with tempfile.TemporaryDirectory() as root:
            base = Path(root)
            mount = base / "mnt"
            marker = base / "marker"
            with patch.object(service, "MOUNT", mount), patch.object(service, "MARKER", marker), \
                 patch.object(service, "ROOT_UID", os.getuid()), \
                 patch.object(service, "ROOT_GID", os.getgid()), \
                 patch.object(service, "require_root"), \
                 patch.object(service, "_mount_row", return_value=None), \
                 patch.object(service, "_host_view", side_effect=lambda p: p):
                service.mount_prepare()
                self.assertEqual(mount.stat().st_mode & 0o777, 0o700)
                self.assertEqual(marker.stat().st_mode & 0o777, 0o600)
                service.mount_clean()
                self.assertFalse(mount.exists())
                self.assertFalse(marker.exists())

    def test_mountinfo_real_parser(self):
        with tempfile.TemporaryDirectory() as root:
            table = Path(root) / "mountinfo"
            fake_path = Path(root) / "mnt"
            table.write_text(
                f"100 9 0:99 / {fake_path} rw,nosuid,nodev,noexec,relatime - tmpfs tmpfs rw,size=8192k,nr_inodes=128\n"
            )
            kind, flags = service._mount_row(fake_path, table)
            self.assertEqual(kind, "tmpfs")
            self.assertTrue({"nosuid", "nodev", "noexec"}.issubset(flags))
            self.assertIsNone(service._mount_row(fake_path / "other", table))
            with self.assertRaises(service.MountRefused):
                service._mount_row(fake_path, Path(root) / "nonexistent")

    def test_private_mount_prepare_and_clean_separate_host(self):
        with tempfile.TemporaryDirectory() as root:
            mount, host, marker, rows, view, vfs = self.mount_case(root, private=True)
            with patch.object(service, "MOUNT", mount), patch.object(service, "MARKER", marker), \
                 patch.object(service, "ROOT_UID", os.getuid()), \
                 patch.object(service, "ROOT_GID", os.getgid()), \
                 patch.object(service, "checked_identity", return_value=(os.getuid(), os.getgid())), \
                 patch.object(service, "require_root"), \
                 patch.object(service, "_mount_row", side_effect=rows), \
                 patch.object(service, "_host_view", side_effect=view), \
                 patch.object(service, "_separate_device", return_value=True), \
                 patch.object(service.os, "fstatvfs", side_effect=vfs):
                service.mount_prepare()
                self.assertEqual(mount.stat().st_mode & 0o777, 0o700)
                self.assertEqual(host.stat().st_mode & 0o777, 0o755)
                self.assertEqual(marker.stat().st_mode & 0o777, 0o600)
                service.mount_clean()
                self.assertFalse(host.exists())
                self.assertFalse(marker.exists())
                self.assertTrue(mount.exists())  # private mount is NEVER removed by hook

    def test_private_mount_rejects_untrusted_evidence(self):
        from types import SimpleNamespace
        cases = {
            "bad_fs": "MOUNT_PRIVATE_INVALID",
            "missing_flag": "MOUNT_PRIVATE_FLAGS",
            "wrong_uid": "MOUNT_PRIVATE_IDENTITY",
            "wrong_mode": "MOUNT_PRIVATE_IDENTITY",
            "too_large": "MOUNT_PRIVATE_QUOTA",
            "too_many_inodes": "MOUNT_PRIVATE_QUOTA",
            "same_device": "MOUNT_PRIVATE_INVALID",
            "mounted_host": "MOUNT_HOST_MOUNTED",
            "nonempty_private": "MOUNT_NOT_EMPTY",
            "nonempty_host": "MOUNT_NOT_EMPTY",
            "host_wrong_owner": "MOUNT_HOST_LOOKUP_FAILED",
            "host_wrong_mode": "MOUNT_HOST_LOOKUP_FAILED",
        }
        for case, reason in cases.items():
            with self.subTest(case=case), tempfile.TemporaryDirectory() as root:
                mount, host, marker, rows, view, vfs = self.mount_case(root, private=True)
                if case == "wrong_mode":
                    os.chmod(mount, 0o755)
                if case == "nonempty_private":
                    (mount / "foreign").write_text("unchanged")
                if case == "nonempty_host":
                    (host / "foreign").write_text("unchanged")
                if case == "host_wrong_mode":
                    os.chmod(host, 0o700)
                def fake_rows(path, table):
                    if case == "mounted_host" and str(table) == "/proc/1/mountinfo":
                        return ("ext4", set())
                    result = rows(path, table)
                    if result is not None and case == "bad_fs":
                        return ("ext4", result[1])
                    if result is not None and case == "missing_flag":
                        return ("tmpfs", {"nodev", "nosuid"})
                    return result
                def fake_vfs(fd):
                    if case == "too_large":
                        return SimpleNamespace(f_blocks=4096, f_frsize=4096, f_files=128)
                    if case == "too_many_inodes":
                        return SimpleNamespace(f_blocks=2048, f_frsize=4096, f_files=1024)
                    return vfs(fd)
                with patch.object(service, "MOUNT", mount), patch.object(service, "MARKER", marker), \
                     patch.object(service, "ROOT_UID", os.getuid() + (1 if case == "host_wrong_owner" else 0)), \
                     patch.object(service, "ROOT_GID", os.getgid()), \
                     patch.object(service, "checked_identity",
                                  return_value=(os.getuid() + (1 if case == "wrong_uid" else 0),
                                                os.getgid())), \
                     patch.object(service, "require_root"), \
                     patch.object(service, "_mount_row", side_effect=fake_rows), \
                     patch.object(service, "_host_view", side_effect=view), \
                     patch.object(service, "_separate_device", return_value=case != "same_device"), \
                     patch.object(service.os, "fstatvfs", side_effect=fake_vfs):
                    with self.assertRaises(service.MountRefused) as cm:
                        service.mount_prepare()
                    self.assertEqual(cm.exception.code, reason)
                self.assertFalse(marker.exists())
                self.assertTrue(host.is_dir())
                if case == "nonempty_host":
                    self.assertEqual((host / "foreign").read_text(), "unchanged")
                if case == "nonempty_private":
                    self.assertEqual((mount / "foreign").read_text(), "unchanged")

    def test_private_cleanup_refuses_changed_host_and_preserves_marker(self):
        with tempfile.TemporaryDirectory() as root:
            mount, host, marker, rows, view, vfs = self.mount_case(root, private=True)
            with patch.object(service, "MOUNT", mount), patch.object(service, "MARKER", marker), \
                 patch.object(service, "ROOT_UID", os.getuid()), \
                 patch.object(service, "ROOT_GID", os.getgid()), \
                 patch.object(service, "checked_identity", return_value=(os.getuid(), os.getgid())), \
                 patch.object(service, "require_root"), \
                 patch.object(service, "_mount_row", side_effect=rows), \
                 patch.object(service, "_host_view", side_effect=view), \
                 patch.object(service, "_separate_device", return_value=True), \
                 patch.object(service.os, "fstatvfs", side_effect=vfs):
                service.mount_prepare()
                os.chmod(host, 0o700)
                with self.assertRaises(service.MountRefused):
                    service.mount_clean()
                self.assertTrue(host.exists())
                self.assertTrue(marker.exists())
                self.assertEqual(marker.read_text(), service.LABEL)

    def test_host_prepare_refuses_stale_or_ambiguous_paths(self):
        for case in ("wrong_mode", "marker", "nonempty", "symlink", "regular_file"):
            with self.subTest(case=case), tempfile.TemporaryDirectory() as root:
                mount, host, marker, rows, view, vfs = self.mount_case(root)
                if case == "wrong_mode":
                    os.chmod(mount, 0o700)
                if case == "marker":
                    marker.write_text("stale")
                if case == "nonempty":
                    (mount / "foreign").write_text("unchanged")
                if case in ("symlink", "regular_file"):
                    mount.rmdir()
                    if case == "symlink":
                        target = Path(root) / "target"
                        target.mkdir()
                        mount.symlink_to(target)
                    else:
                        mount.write_text("unchanged")
                with patch.object(service, "MOUNT", mount), patch.object(service, "MARKER", marker), \
                     patch.object(service, "ROOT_UID", os.getuid()), \
                     patch.object(service, "ROOT_GID", os.getgid()), \
                     patch.object(service, "require_root"), \
                     patch.object(service, "_mount_row", side_effect=rows), \
                     patch.object(service, "_host_view", side_effect=view):
                    with self.assertRaises(service.MountRefused):
                        service.mount_prepare()
                if case == "marker":
                    self.assertEqual(marker.read_text(), "stale")
                else:
                    self.assertFalse(marker.exists())

    def test_clean_unowned_host_residue_and_bad_marker(self):
        with tempfile.TemporaryDirectory() as root:
            mount, host, marker, rows, view, vfs = self.mount_case(root)
            with patch.object(service, "MOUNT", mount), patch.object(service, "MARKER", marker), \
                 patch.object(service, "ROOT_UID", os.getuid()), \
                 patch.object(service, "ROOT_GID", os.getgid()), \
                 patch.object(service, "require_root"), \
                 patch.object(service, "_mount_row", side_effect=rows), \
                 patch.object(service, "_host_view", side_effect=view):
                with self.assertRaises(service.MountRefused) as cm:
                    service.mount_clean()
                self.assertEqual(cm.exception.code, "MOUNT_CLEAN_UNOWNED")
                marker.write_text("not-the-tag-label")
                os.chmod(marker, 0o600)
                with self.assertRaises(service.MountRefused):
                    service.mount_clean()
                self.assertTrue(host.exists())
                self.assertTrue(marker.exists())

    def test_mount_diagnostics_are_enumerated_and_nonsecret(self):
        err = io.StringIO()
        with patch.object(service, "mount_prepare",
                          side_effect=service.MountRefused("MOUNT_PRIVATE_IDENTITY")), \
             patch.object(sys, "argv", ["tag88_service.py", "mount-prepare"]), \
             patch.object(sys, "stderr", err):
            self.assertEqual(service.main(), 1)
        self.assertEqual(err.getvalue(),
                         "TAG_INSTALL_FAIL_CLOSED: Refused MOUNT_PRIVATE_IDENTITY\n")
        with self.assertRaises(ValueError):
            service.MountRefused("secret=/run/tag-qa88-control/operator.token")

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
