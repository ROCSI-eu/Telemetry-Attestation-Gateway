#!/usr/bin/env python3
"""Offline regression tests for the bounded synthetic local console session.

EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC
NOT VALIDATION OR PRODUCTION AUTHORIZATION
"""
from __future__ import annotations

import contextlib
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

    def test_invalid_lifetime_fails_before_any_session(self) -> None:
        for seconds in (0, 301):
            with self.subTest(seconds=seconds), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    pkg.main(["--seconds", str(seconds), "--check-only"])
        self.assertEqual(list(self.parent.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
