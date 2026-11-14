#!/usr/bin/env python3
"""Offline regression tests for the bounded synthetic local console session.

EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC
NOT VALIDATION OR PRODUCTION AUTHORIZATION
"""
from __future__ import annotations

import contextlib
import fcntl
import io
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, patch

import run_isolated_local as pkg


class LocalSessionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="tag-synthetic-test-")
        self.addCleanup(self.temp.cleanup)
        self.parent = Path(self.temp.name)

    def test_parent_rejects_root_and_unsafe_paths(self) -> None:
        pkg.private_parent(self.parent)
        with patch.object(pkg.os, "geteuid", return_value=0):
            with self.assertRaises(pkg.Unavailable):
                pkg.private_parent(self.parent)
        with self.assertRaises(pkg.Unavailable):
            pkg.private_parent(Path("relative"))
        with self.assertRaises(pkg.Unavailable):
            pkg.private_parent(pkg.REPO)
        with self.assertRaises(pkg.Unavailable):
            pkg.private_parent(pkg.HERE)
        link = self.parent / "link"
        link.symlink_to(self.parent, target_is_directory=True)
        with self.assertRaises(pkg.Unavailable):
            pkg.private_parent(link)
        outside = self.parent / "permissive"
        outside.mkdir(mode=0o777)
        outside.chmod(0o777)
        with self.assertRaises(pkg.Unavailable):
            pkg.private_parent(outside)

    def test_no_server_or_files_after_check_only(self) -> None:
        with patch.object(pkg.bridge, "trusted_bwrap", return_value="/usr/bin/bwrap"), \
             patch.object(pkg.subprocess, "Popen") as spawn:
            self.assertEqual(pkg.run(30, self.parent, True), 0)
            spawn.assert_not_called()
        self.assertEqual(list(self.parent.iterdir()), [])

    def test_missing_bwrap_fails_before_spawning(self) -> None:
        with patch.object(pkg.bridge, "trusted_bwrap", side_effect=pkg.bridge.Rejected), \
             patch.object(pkg.subprocess, "Popen") as spawn:
            with self.assertRaises(pkg.bridge.Rejected):
                pkg.run(30, self.parent, False)
            spawn.assert_not_called()
        self.assertEqual(list(self.parent.iterdir()), [])

    def test_foreground_session_sanitizes_environment_and_cleans(self) -> None:
        child = Mock()
        child.pid = 32456
        child.wait.return_value = 0
        child.poll.return_value = 0
        with patch.dict(os.environ, {"AWS_SECRET_ACCESS_KEY": "test-unsafe",
                                     "OPENAI_API_KEY": "test-unsafe"}), \
             patch.object(pkg.bridge, "trusted_bwrap", return_value="/usr/bin/bwrap"), \
             patch.object(pkg.subprocess, "Popen", return_value=child) as spawn:
            self.assertEqual(pkg.run(20, self.parent, False), 0)
        cmd, kwargs = spawn.call_args
        self.assertEqual(cmd[0][1:3], ["-I", str(pkg.HERE / "local_cli_bridge.py")])
        self.assertEqual(cmd[0][-2:], ["--seconds", "20"])
        self.assertNotIn("--offline-toolchain-root", cmd[0])
        self.assertTrue(kwargs["start_new_session"])
        self.assertEqual(kwargs["stdin"], subprocess.DEVNULL)
        self.assertEqual(kwargs["stderr"], subprocess.DEVNULL)
        self.assertEqual(kwargs["env"]["PATH"], "/usr/bin:/bin")
        self.assertNotIn("AWS_SECRET_ACCESS_KEY", kwargs["env"])
        self.assertNotIn("OPENAI_API_KEY", kwargs["env"])
        self.assertEqual(kwargs["env"]["HOME"], str(kwargs["cwd"]))
        self.assertEqual(kwargs["env"]["TMPDIR"], str(kwargs["cwd"]))
        self.assertFalse(Path(kwargs["cwd"]).exists())
        self.assertEqual(list(self.parent.iterdir()), [])

    def test_bounded_wait_force_stops_only_owned_group(self) -> None:
        child = Mock()
        child.pid = 32457
        child.poll.return_value = None
        child.wait.side_effect = [
            subprocess.TimeoutExpired("bridge", 16),
            subprocess.TimeoutExpired("bridge", 3),
            0,
        ]
        with patch.object(pkg.bridge, "trusted_bwrap", return_value="/usr/bin/bwrap"), \
             patch.object(pkg.subprocess, "Popen", return_value=child), \
             patch.object(pkg.os, "killpg") as kill:
            with self.assertRaises(subprocess.TimeoutExpired):
                pkg.run(8, self.parent, False)
        self.assertEqual(
            kill.call_args_list,
            [unittest.mock.call(32457, signal.SIGTERM),
             unittest.mock.call(32457, signal.SIGKILL)],
        )
        self.assertEqual(list(self.parent.iterdir()), [])

    def test_fd_limit_stays_bounded_even_with_infinite_hard_limit(self) -> None:
        with patch.object(pkg.resource, "getrlimit",
                          return_value=(1024, pkg.resource.RLIM_INFINITY)), \
             patch.object(pkg.resource, "setrlimit") as set_limit:
            pkg.limits()
        self.assertEqual(
            set_limit.call_args_list[0],
            unittest.mock.call(pkg.resource.RLIMIT_NOFILE,
                               (64, pkg.resource.RLIM_INFINITY)),
        )
        self.assertEqual(
            set_limit.call_args_list[1],
            unittest.mock.call(pkg.resource.RLIMIT_CORE, (0, 0)),
        )

    def test_stale_owned_directory_blocks_preflight_and_launch(self) -> None:
        stale = self.parent / "tag-synthetic-interrupted"
        stale.mkdir(mode=0o700)
        with patch.object(pkg.bridge, "trusted_bwrap", return_value="/usr/bin/bwrap"), \
             patch.object(pkg.subprocess, "Popen") as spawn:
            for check_only in (True, False):
                with self.subTest(check_only=check_only):
                    with self.assertRaises(pkg.Unavailable):
                        pkg.run(20, self.parent, check_only)
            spawn.assert_not_called()
        self.assertEqual(list(self.parent.iterdir()), [stale])
        self.assertTrue(stale.is_dir())  # no automatic deletion

    def test_stale_symlink_blocks_without_following_or_deleting(self) -> None:
        target = self.parent / "owner-data"
        target.mkdir(mode=0o700)
        marker = self.parent / "tag-synthetic-ambiguous"
        marker.symlink_to(target, target_is_directory=True)
        with patch.object(pkg.bridge, "trusted_bwrap", return_value="/usr/bin/bwrap"), \
             patch.object(pkg.subprocess, "Popen") as spawn:
            with self.assertRaises(pkg.Unavailable):
                pkg.run(20, self.parent, False)
            spawn.assert_not_called()
        self.assertTrue(marker.is_symlink())
        self.assertTrue(target.is_dir())

    def test_parent_lease_rejects_second_session_then_releases(self) -> None:
        fd = os.open(self.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            with patch.object(pkg.bridge, "trusted_bwrap", return_value="/usr/bin/bwrap"), \
                 patch.object(pkg.subprocess, "Popen") as spawn:
                with self.assertRaises(pkg.Unavailable):
                    pkg.run(20, self.parent, False)
                spawn.assert_not_called()
        finally:
            os.close(fd)
        with patch.object(pkg.bridge, "trusted_bwrap", return_value="/usr/bin/bwrap"):
            self.assertEqual(pkg.run(20, self.parent, True), 0)
        self.assertEqual(list(self.parent.iterdir()), [])

    def test_inspect_clear_is_read_only_without_bwrap_or_listener(self) -> None:
        output = io.StringIO()
        with patch.object(pkg.bridge, "trusted_bwrap",
                          side_effect=AssertionError("must not require bwrap")), \
             patch.object(pkg.subprocess, "Popen",
                          side_effect=AssertionError("must not spawn")), \
             contextlib.redirect_stdout(output):
            code = pkg.main(["--inspect-only", "--runtime-parent", str(self.parent)])
        self.assertEqual(code, 0)
        self.assertIn("LOCAL INSPECTION · CLEAR", output.getvalue())
        self.assertIn("SYNTHETIC_ONLY", output.getvalue())
        self.assertIn("NO PROCESS STARTED · NO CLEANUP", output.getvalue())
        self.assertNotIn(str(self.parent), output.getvalue())
        self.assertEqual(list(self.parent.iterdir()), [])

    def test_inspect_busy_lease_reports_no_owner_or_path(self) -> None:
        fd = os.open(self.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            output = io.StringIO()
            with patch.object(pkg.subprocess, "Popen",
                              side_effect=AssertionError("must not spawn")), \
                 contextlib.redirect_stdout(output):
                code = pkg.main(["--inspect-only", "--runtime-parent", str(self.parent)])
            self.assertEqual(code, 2)
            self.assertIn("LEASE_BUSY_OR_UNCERTAIN", output.getvalue())
            self.assertNotIn(str(self.parent), output.getvalue())
            self.assertEqual(list(self.parent.iterdir()), [])
        finally:
            os.close(fd)

    def test_inspect_reserved_entries_never_opens_or_deletes_them(self) -> None:
        private_target = self.parent / "unrelated"
        private_target.mkdir(mode=0o700)
        marker = self.parent / "tag-synthetic-residual"
        marker.symlink_to(private_target, target_is_directory=True)
        output = io.StringIO()
        with patch.object(pkg.subprocess, "Popen",
                          side_effect=AssertionError("must not spawn")), \
             contextlib.redirect_stdout(output):
            code = pkg.main(["--inspect-only", "--runtime-parent", str(self.parent)])
        self.assertEqual(code, 2)
        self.assertIn("RESERVED_ENTRIES_PRESENT", output.getvalue())
        self.assertNotIn(str(marker), output.getvalue())
        self.assertNotIn("residual", output.getvalue())
        self.assertTrue(marker.is_symlink())
        self.assertTrue(private_target.is_dir())

    def test_inspect_unsafe_parent_fails_closed(self) -> None:
        link = self.parent / "private-parent-link"
        link.symlink_to(self.parent, target_is_directory=True)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = pkg.main(["--inspect-only", "--runtime-parent", str(link)])
        self.assertEqual(code, 2)
        self.assertIn("LOCAL INSPECTION · UNAVAILABLE", output.getvalue())
        self.assertNotIn(str(link), output.getvalue())
        self.assertTrue(link.is_symlink())

    def test_inspect_and_check_only_are_mutually_exclusive(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                pkg.main(["--inspect-only", "--check-only"])
        self.assertEqual(list(self.parent.iterdir()), [])

    def test_invalid_lifetime_fails_before_any_session(self) -> None:
        for seconds in (0, 301):
            with self.subTest(seconds=seconds), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    pkg.main(["--seconds", str(seconds), "--check-only"])
        self.assertEqual(list(self.parent.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
