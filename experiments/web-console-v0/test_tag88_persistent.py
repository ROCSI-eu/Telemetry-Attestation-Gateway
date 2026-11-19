#!/usr/bin/env python3
"""Focused unit tests only; no systemd, root, real CLI, SITL or cryptography."""
import errno
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
    def test_single_service_policy_and_rendering(self):
        template = Path(__file__).with_name("tag-qa88-persistent.service").read_text()
        rendered = service.unit_render(template, Path("/opt/tag-qa88/release-" + "a"*40), 991, 992)
        self.assertIn("Type=exec", rendered)
        self.assertIn("User=tag-qa88", rendered)
        self.assertIn("Group=tag-qa88", rendered)
        self.assertIn("uid=991,gid=992", rendered)
        self.assertIn("AssertPathIsDirectory=/var/lib/tag-qa88/runtime", rendered)
        self.assertIn("AssertPathIsMountPoint=!/var/lib/tag-qa88/runtime", rendered)
        self.assertIn("TemporaryFileSystem=/var/lib/tag-qa88/runtime:", rendered)
        self.assertIn("ExecStartPre=+/usr/bin/python3", rendered)
        self.assertIn("mount-verify", rendered)
        self.assertIn("Restart=no", rendered)
        self.assertIn("MemorySwapMax=0", rendered)
        self.assertIn("MemoryMax=134217728", rendered)
        self.assertIn("CPUQuota=50%", rendered)
        self.assertIn("TasksMax=12", rendered)
        self.assertIn("RuntimeDirectory=tag-qa88-control", rendered)
        self.assertIn("nodev,nosuid,noexec", rendered)
        self.assertIn("WantedBy=multi-user.target", rendered)
        for unsupported in ("OnSuccess=", "OnFailure=", "mount-prepare",
                            "mount-clean", "postcleanup", "ReadWritePaths=",
                            "ExecStopPost=", "RuntimeDirectory=tag-qa88\n"):
            self.assertNotIn(unsupported, rendered)
        self.assertFalse(Path(__file__).with_name("tag-qa88-postcleanup.service").exists())
        self.assertNotIn("@TAG_", rendered)
        with self.assertRaises(service.Refused):
            service.unit_render(template, Path("/opt/tag-qa88/release-x"), 0, 991)

    def _host(self, base: Path) -> tuple[Path, Path, Path]:
        parent = base / "tag-qa88"
        parent.mkdir(mode=0o755)
        parent.chmod(0o755)
        child = parent / "runtime"
        child.mkdir(mode=0o755)
        child.chmod(0o755)
        table = base / "mountinfo"
        table.write_text("")
        return parent, child, table

    def _host_patches(self):
        from contextlib import ExitStack
        stack = ExitStack()
        stack.enter_context(patch.object(service, "HOST_PARENT", Path("/tag-qa88")))
        stack.enter_context(patch.object(service, "MOUNT", Path("/tag-qa88/runtime")))
        stack.enter_context(patch.object(service, "ROOT_UID", os.getuid()))
        stack.enter_context(patch.object(service, "ROOT_GID", os.getgid()))
        return stack

    def test_verified_host_is_readonly_and_binds_to_recorded_identity(self):
        with tempfile.TemporaryDirectory() as root, self._host_patches():
            base = Path(root)
            parent, child, table = self._host(base)
            before = (parent.stat().st_ino, child.stat().st_ino)
            receipt = service.verified_host(root=base, table=table)
            self.assertEqual(receipt["parent_ino"], before[0])
            self.assertEqual(receipt["mount_ino"], before[1])
            self.assertEqual(receipt, service.verified_host(root=base, table=table,
                                                           expected=receipt))
            self.assertEqual(list(child.iterdir()), [])
            self.assertEqual((parent.stat().st_ino, child.stat().st_ino), before)

    def test_verified_host_rejects_untrusted_directory_without_deleting(self):
        cases = ("parent_mode", "child_mode", "wrong_owner", "child_symlink",
                 "child_file", "child_nonempty", "parent_extra", "missing",
                 "record_changed", "mounted", "parent_mounted", "bad_table")
        for case in cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as root, self._host_patches():
                base = Path(root)
                parent, child, table = self._host(base)
                expected = service.verified_host(root=base, table=table)
                if case == "parent_mode":
                    parent.chmod(0o700)
                elif case == "child_mode":
                    child.chmod(0o700)
                elif case == "child_symlink":
                    child.rmdir()
                    child.symlink_to(parent)
                elif case == "child_file":
                    child.rmdir()
                    child.write_text("untouched")
                elif case == "child_nonempty":
                    (child / "foreign").write_text("untouched")
                elif case == "parent_extra":
                    (parent / "foreign").write_text("untouched")
                elif case == "missing":
                    child.rmdir()
                elif case == "record_changed":
                    expected["mount_ino"] += 1
                elif case == "mounted":
                    table.write_text("10 9 0:99 / /tag-qa88/runtime rw - tmpfs tmpfs rw\n")
                elif case == "parent_mounted":
                    table.write_text("10 9 0:99 / /tag-qa88 rw - tmpfs tmpfs rw\n")
                elif case == "bad_table":
                    table.unlink()
                if case == "wrong_owner":
                    with patch.object(service, "ROOT_UID", os.getuid()+1):
                        with self.assertRaises(service.MountRefused):
                            service.verified_host(root=base, table=table, expected=expected)
                else:
                    with self.assertRaises(service.MountRefused):
                        service.verified_host(root=base, table=table, expected=expected)
                if (parent / "foreign").exists():
                    self.assertEqual((parent / "foreign").read_text(), "untouched")
                if child.is_file():
                    self.assertEqual(child.read_text(), "untouched")
                if (child / "foreign").is_file():
                    self.assertEqual((child / "foreign").read_text(), "untouched")

    def test_private_mount_limits_and_flags_enforced(self):
        from types import SimpleNamespace
        cases = ("ok", "missing", "other_fs", "missing_flag",
                 "same_device", "too_many_blocks", "too_many_inodes", "nonempty", "bad_owner")
        for case in cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as root:
                base = Path(root)
                child = base / "runtime"
                child.mkdir(mode=0o700)
                child.chmod(0o700)
                uid, gid = os.getuid(), os.getgid()
                mount_row = ("tmpfs", {"nodev", "nosuid", "noexec"})
                if case == "missing":
                    mount_row = None
                elif case == "other_fs":
                    mount_row = ("ext4", {"nodev", "nosuid", "noexec"})
                elif case == "missing_flag":
                    mount_row = ("tmpfs", {"nodev", "nosuid"})
                elif case == "nonempty":
                    (child / "foreign").write_text("preserved")
                def checked(path, identity, mode):
                    if case == "bad_owner":
                        raise service.MountRefused("VERIFY_HOST_INVALID")
                    self.assertEqual(identity, (uid, gid))
                    fd = os.open(child, os.O_RDONLY | os.O_DIRECTORY)
                    dev = base.stat().st_dev
                    return fd, SimpleNamespace(st_dev=dev if case == "same_device" else dev+1)
                blocks = 4096 if case == "too_many_blocks" else 2048
                inodes = 512 if case == "too_many_inodes" else 128
                with patch.object(service, "MOUNT", child), \
                     patch.object(service, "_mount_row", return_value=mount_row), \
                     patch.object(service, "_checked_directory", side_effect=checked), \
                     patch.object(service, "checked_identity", return_value=(uid, gid)), \
                     patch.object(service.os, "fstatvfs",
                                  return_value=SimpleNamespace(f_blocks=blocks, f_frsize=4096,
                                                               f_files=inodes)):
                    if case == "ok":
                        service.verified_private()
                    else:
                        with self.assertRaises(service.MountRefused):
                            service.verified_private()
                if case == "nonempty":
                    self.assertEqual((child / "foreign").read_text(), "preserved")

    def test_mountinfo_parser_rejects_ambiguous_records(self):
        with tempfile.TemporaryDirectory() as root:
            table = Path(root) / "mountinfo"
            path = Path("/tag-qa88/runtime")
            row = "10 9 0:99 / /tag-qa88/runtime rw,nosuid,nodev,noexec - tmpfs tmpfs rw\n"
            table.write_text(row)
            self.assertEqual(service._mount_row(path, table)[0], "tmpfs")
            self.assertIsNone(service._mount_row(Path("/unrelated"), table))
            table.write_text(row * 2)
            with self.assertRaises(service.MountRefused):
                service._mount_row(path, table)
            table.unlink()
            with self.assertRaises(service.MountRefused):
                service._mount_row(path, table)

    def test_start_verifier_is_root_only_and_no_lifecycle_mutations(self):
        with patch.object(service.os, "geteuid", return_value=1000):
            with self.assertRaises(service.MountRefused) as err:
                service.mount_verify()
            self.assertEqual(err.exception.code, "VERIFY_ROOT_REQUIRED")
        source = __import__("inspect").getsource(service.mount_verify)
        for forbidden in ("mkdir(", "chmod(", "rmdir(", "unlink(", "mount(", "subprocess.run("):
            self.assertNotIn(forbidden, source)
        with patch.object(service, "require_root"), \
             patch.object(service, "trusted_receipt", side_effect=service.MountRefused(
                 "VERIFY_RECEIPT_INVALID")):
            with self.assertRaises(service.MountRefused):
                service.mount_verify()

    def test_mount_verifier_checks_receipt_identity_before_private(self):
        sha = "a"*40
        receipt = {"sha":sha, "uid":900, "gid":900,
                   "host":{"parent_dev":1, "parent_ino":2, "mount_dev":1, "mount_ino":3}}
        pretend_file = "/opt/tag-qa88/release-" + sha + "/scripts/tag88_service.py"
        with patch.object(service, "__file__", pretend_file), \
             patch.object(service, "require_root"), \
             patch.object(service, "trusted_receipt", return_value=receipt), \
             patch.object(service, "checked_identity", return_value=(900,900)), \
             patch.object(service, "verified_host") as host, \
             patch.object(service, "verified_private") as private:
            service.mount_verify()
            host.assert_called_once()
            private.assert_called_once()
        with patch.object(service, "__file__", pretend_file), \
             patch.object(service, "require_root"), \
             patch.object(service, "trusted_receipt", return_value=receipt), \
             patch.object(service, "checked_identity", return_value=(901,900)), \
             patch.object(service, "verified_host") as host:
            with self.assertRaises(service.MountRefused):
                service.mount_verify()
            host.assert_not_called()

    def test_receipt_rejects_foreign_symlink_or_bad_shape(self):
        sha = "a"*40
        body = {"sha":sha, "uid":900, "gid":900,
                "host":{"parent_dev":1, "parent_ino":2, "mount_dev":1, "mount_ino":3}}
        with tempfile.TemporaryDirectory() as root:
            prefix = Path(root)
            receipt = prefix / "receipt.json"
            receipt.write_text(json.dumps(body))
            receipt.chmod(0o644)
            with patch.object(service, "PREFIX", prefix), \
                 patch.object(service, "ROOT_UID", os.getuid()), \
                 patch.object(service, "ROOT_GID", os.getgid()):
                self.assertEqual(service.trusted_receipt()["sha"], sha)
                receipt.write_text(json.dumps(dict(body, host={"parent_ino":1})))
                with self.assertRaises(service.MountRefused):
                    service.trusted_receipt()
                receipt.unlink()
                foreign = prefix / "foreign"
                foreign.write_text(json.dumps(body))
                receipt.symlink_to(foreign)
                with self.assertRaises(service.MountRefused):
                    service.trusted_receipt()
                self.assertEqual(json.loads(foreign.read_text())["sha"], sha)

    def test_install_refuses_existing_anchor_before_archive_or_mutations(self):
        with tempfile.TemporaryDirectory() as root:
            base = Path(root)
            existing = base / "tag"
            existing.mkdir()
            with patch.object(service, "require_root"), \
                 patch.object(service, "PREFIX", base / "opt"), \
                 patch.object(service, "UNIT_PATH", base / "unit"), \
                 patch.object(service, "LEGACY_CLEAN_UNIT_PATH", base / "other-unit"), \
                 patch.object(service, "HOST_PARENT", existing), \
                 patch.object(service, "CONTROL", base / "control"), \
                 patch.object(service, "git_checked_checkout") as archive:
                with self.assertRaises(service.Refused):
                    service.install(base, "a"*40)
                archive.assert_not_called()
            self.assertTrue(existing.is_dir())

    def test_diagnostics_never_expose_secrets(self):
        err = io.StringIO()
        with patch.object(service, "mount_verify",
                          side_effect=service.MountRefused("VERIFY_PRIVATE_IDENTITY")), \
             patch.object(sys, "argv", ["tag88_service.py", "mount-verify"]), \
             patch.object(sys, "stderr", err):
            self.assertEqual(service.main(), 1)
        self.assertEqual(err.getvalue(), "TAG_INSTALL_FAIL_CLOSED: Refused VERIFY_PRIVATE_IDENTITY\n")
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

    def test_remove_rejects_unknown_or_unavailable_systemd_state(self):
        """One mocked query: only the exact known-safe state permits removal."""
        from types import SimpleNamespace
        baseline = {
            "LoadState": "loaded", "ActiveState": "inactive",
            "MainPID": "0", "ControlPID": "0", "UnitFileState": "disabled",
        }
        def payload(fields):
            return "".join(f"{key}={value}\n" for key, value in fields.items())

        with patch.object(service.subprocess, "run",
                          return_value=SimpleNamespace(stdout=payload(baseline))) as command:
            service._require_primary_inactive_disabled()
            command.assert_called_once()
            self.assertEqual(command.call_args.args[0][:3],
                             ["/usr/bin/systemctl", "show", service.UNIT_NAME])
            self.assertTrue(command.call_args.kwargs["check"])
            self.assertEqual(command.call_args.kwargs["timeout"], 15)

        invalid = {
            "active": dict(baseline, ActiveState="active"),
            "failed": dict(baseline, ActiveState="failed"),
            "activating": dict(baseline, ActiveState="activating"),
            "unknown_active": dict(baseline, ActiveState="mystery"),
            "loaded_unknown": dict(baseline, LoadState="unknown"),
            "not_found": dict(baseline, LoadState="not-found"),
            "enabled": dict(baseline, UnitFileState="enabled"),
            "static": dict(baseline, UnitFileState="static"),
            "masked": dict(baseline, UnitFileState="masked"),
            "unknown_unit": dict(baseline, UnitFileState="unknown"),
            "main_running": dict(baseline, MainPID="991"),
            "control_running": dict(baseline, ControlPID="991"),
            "empty_active": dict(baseline, ActiveState=""),
        }
        for name, fields in invalid.items():
            with self.subTest(case=name), patch.object(
                service.subprocess, "run",
                return_value=SimpleNamespace(stdout=payload(fields))
            ):
                with self.assertRaises(service.Refused):
                    service._require_primary_inactive_disabled()

        lines = payload(baseline).splitlines()
        malformed = {
            "missing_key": "\n".join(lines[1:]) + "\n",
            "duplicate_key": payload(baseline) + "LoadState=loaded\n",
            "extra_key": payload(baseline) + "Other=value\n",
            "bad_separator": payload(baseline).replace("MainPID=0", "MainPID:0"),
            "empty_output": "",
            "empty_value": payload(baseline).replace("ControlPID=0", "ControlPID="),
            "unknown_property": payload(baseline).replace("MainPID=0", "AnotherPID=0"),
        }
        for name, output in malformed.items():
            with self.subTest(case=name), patch.object(
                service.subprocess, "run",
                return_value=SimpleNamespace(stdout=output)
            ):
                with self.assertRaises(service.Refused):
                    service._require_primary_inactive_disabled()
        with patch.object(service.subprocess, "run",
                          return_value=SimpleNamespace(stdout=None)):
            with self.assertRaises(service.Refused):
                service._require_primary_inactive_disabled()
        for error in (OSError("offline"),
                      service.subprocess.CalledProcessError(1, "systemctl"),
                      service.subprocess.TimeoutExpired("systemctl", 15)):
            with self.subTest(error=type(error).__name__), patch.object(
                service.subprocess, "run", side_effect=error
            ):
                with self.assertRaises(service.Refused):
                    service._require_primary_inactive_disabled()
        source = __import__("inspect").getsource(service.remove)
        self.assertIn("_require_primary_inactive_disabled()", source)
        self.assertNotIn("is-active", source)
        self.assertNotIn("is-enabled", source)

    def test_fail_closed_install_without_root_or_sha(self):
        with patch.object(service.os, "geteuid", return_value=1000):
            with self.assertRaises(service.Refused):
                service.install(Path("/tmp"), "a"*40)
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaises(service.Refused):
                service.git_checked_checkout(Path(root), "bad-sha")


if __name__ == "__main__":
    unittest.main()
