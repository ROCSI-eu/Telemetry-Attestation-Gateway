#!/usr/bin/env python3
"""Offline, non-cryptographic TAG #88 isolated cgroup launcher regression tests."""
from __future__ import annotations

import contextlib
import io
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import run_tag88_bounded as pkg


UNIT = "tag-qa88-bounded-a1b2c3d4e5f6.service"


class BoundedLocalTests(unittest.TestCase):
    def setUp(self) -> None:
        temp = tempfile.TemporaryDirectory(prefix="tag88-bounded-test-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def test_command_is_fully_bounded_and_not_mount_namespaced_by_systemd(self):
        cmd = pkg.build_command(UNIT, self.root, 8, False)
        self.assertEqual(cmd[0], "/usr/bin/systemd-run")
        for opt in ("--user", "--wait", "--pipe", "--collect",
                    "--slice=tag-qa88.slice", f"--unit={UNIT}",
                    "MemoryMax=134217728", "CPUQuota=50%", "TasksMax=12",
                    "RuntimeMaxSec=15s", "KillMode=control-group"):
            self.assertIn(opt, cmd)
        self.assertNotIn("TemporaryFileSystem", " ".join(cmd))
        self.assertIn("--inside", cmd)
        self.assertEqual(cmd[cmd.index("--unit-name")+1], UNIT)
        self.assertNotIn("--offline-toolchain-root", cmd)
        self.assertEqual(pkg.build_command(UNIT, self.root, 8, True)[-1],
                         "--check-only")

    def test_exact_cgroup_quota_attestation(self):
        uid = 1000
        membership = (f"/user.slice/user-{uid}.slice/user@{uid}.service/"
                      f"tag.slice/tag-qa88.slice/{UNIT}")
        cg = self.root / membership.lstrip("/")
        cg.mkdir(parents=True)
        for name, value in (("memory.max", "134217728"),
                            ("pids.max", "12"), ("cpu.max", "50000 100000")):
            (cg / name).write_text(value+"\n")
        with patch.object(pkg.os, "geteuid", return_value=uid):
            pkg.verify_inside(UNIT, root=self.root, membership=membership)
            for bad in (membership.replace("tag-qa88.slice", "app.slice"),
                        membership+"-wrong", "/"):
                with self.assertRaises(pkg.Unavailable):
                    pkg.verify_inside(UNIT, root=self.root, membership=bad)
            for name, bad in (("memory.max", "max"), ("pids.max", "13"),
                              ("cpu.max", "max 100000")):
                file = cg / name
                previous = file.read_text()
                try:
                    file.write_text(bad+"\n")
                    with self.assertRaises(pkg.Unavailable):
                        pkg.verify_inside(UNIT, root=self.root,
                                          membership=membership)
                finally:
                    file.write_text(previous)

    def test_no_launch_on_existing_slice(self):
        with patch.object(pkg, "user_cgroup_root", return_value=self.root), \
             patch.object(pkg, "safe_user_bus", return_value={}), \
             patch.object(pkg.local.bridge, "trusted_bwrap"), \
             patch.object(pkg.subprocess, "run") as spawn:
            (self.root / "tag.slice" / pkg.SLICE).mkdir(parents=True)
            with self.assertRaises(pkg.Unavailable):
                pkg.launch(self.root, 8, False)
            spawn.assert_not_called()

    def test_service_failure_never_falls_back_to_unbounded_runner(self):
        with patch.object(pkg, "user_cgroup_root", return_value=self.root), \
             patch.object(pkg, "safe_user_bus", return_value={}), \
             patch.object(pkg.local.bridge, "trusted_bwrap"), \
             patch.object(pkg, "systemctl", return_value="inactive"), \
             patch.object(pkg, "cleanup") as cleanup, \
             patch.object(pkg.subprocess, "run",
                          return_value=SimpleNamespace(returncode=1)) as run:
            self.assertEqual(pkg.launch(self.root, 8, False), 1)
            run.assert_called_once()
            cleanup.assert_called_once()
            self.assertIn("--user", run.call_args.args[0])

    def test_nonempty_slice_is_never_stopped(self):
        slice_dir = self.root / "tag.slice" / pkg.SLICE
        slice_dir.mkdir(parents=True)
        (slice_dir / "cgroup.events").write_text("populated 1\nfrozen 0\n")
        (slice_dir / "cgroup.procs").write_text("125\n")
        with patch.object(pkg, "user_cgroup_root", return_value=self.root), \
             patch.object(pkg, "systemctl", return_value="inactive") as ctl:
            with self.assertRaises(pkg.Unavailable):
                pkg.cleanup({}, UNIT)
            self.assertFalse(any(c.args[1] == "stop" for c in ctl.call_args_list))
        self.assertTrue(slice_dir.exists())

    def test_empty_owned_slice_is_stopped(self):
        slice_dir = self.root / "tag.slice" / pkg.SLICE
        slice_dir.mkdir(parents=True)
        (slice_dir / "cgroup.events").write_text("populated 0\nfrozen 0\n")
        (slice_dir / "cgroup.procs").write_text("")
        def ctl(env, *args):
            if args == ("stop", pkg.SLICE):
                for f in slice_dir.iterdir():
                    f.unlink()
                slice_dir.rmdir()
                return ""
            return "inactive"
        with patch.object(pkg, "user_cgroup_root", return_value=self.root), \
             patch.object(pkg, "systemctl", side_effect=ctl) as stub:
            pkg.cleanup({}, UNIT)
            self.assertIn(unittest.mock.call({}, "stop", pkg.SLICE),
                          stub.call_args_list)
        self.assertFalse(slice_dir.exists())

    def test_inside_never_starts_if_attestation_fails(self):
        with patch.object(pkg, "verify_inside", side_effect=pkg.Unavailable), \
             patch.object(pkg.local, "main") as runner, \
             contextlib.redirect_stderr(io.StringIO()) as error:
            self.assertEqual(pkg.main(["--inside", "--unit-name", UNIT,
                                       "--runtime-parent", str(self.root)]), 1)
            runner.assert_not_called()
        self.assertIn("UNAVAILABLE", error.getvalue())

    def test_inside_forwards_only_noncrypto_tmpfs_profile(self):
        with patch.object(pkg, "verify_inside") as gate, \
             patch.object(pkg.local, "main", return_value=0) as runner:
            result = pkg.main(["--inside", "--unit-name", UNIT,
                               "--runtime-parent", str(self.root), "--seconds", "8"])
        self.assertEqual(result, 0)
        gate.assert_called_once_with(UNIT)
        forwarded = runner.call_args.args[0]
        self.assertIn("--tag88-tmpfs-8m", forwarded)
        self.assertNotIn("--offline-toolchain-root", forwarded)

    def test_seconds_cannot_outlive_hard_unit_budget(self):
        for value in ("0", "11", "300"):
            with self.subTest(value=value), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    pkg.main(["--runtime-parent", str(self.root), "--seconds", value])


if __name__ == "__main__":
    unittest.main()
