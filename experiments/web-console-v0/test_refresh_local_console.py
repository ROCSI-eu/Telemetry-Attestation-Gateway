#!/usr/bin/env python3
"""Offline session-refresh safety tests; verifier outcomes here are mocked.

EXPERIMENTAL
SYNTHETIC_ONLY
A0_SYNTHETIC
NOT VALIDATION OR PRODUCTION AUTHORIZATION
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import refresh_local_console as session
from test_authentic_console import checked


class PrivateConsoleSessionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="tag-local-session-tests-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.package = self.root / "synthetic-package"
        self.package.mkdir(mode=0o700)
        self.destination = self.root / "console-session"

    def _refresh(self, status: str = "VALID") -> None:
        with patch.object(session.exporter.authentic, "check_package",
                          return_value=checked(status)) as verifier:
            session.refresh(self.package, self.destination)
            verifier.assert_called_once_with(self.package)

    def _record(self) -> dict:
        return json.loads((self.destination / "web-console-v0" / session.REPLAY).read_text())

    def test_initial_session_only_exposes_allowlisted_static_and_minimized_files(self) -> None:
        self._refresh()
        self.assertEqual({p.name for p in self.destination.iterdir()}, set(session.FILES))
        self.assertEqual({p.name for p in (self.destination / "web-console-v0").iterdir()},
                         {"index.html", "authentic-evidence.json"})
        self.assertEqual({p.name for p in (self.destination / "integrated-cli-v0").iterdir()},
                         {"evidence-results.json"})
        self.assertEqual((self.destination.stat().st_mode & 0o777), 0o700)
        for folder, files in session.FILES.items():
            child = self.destination / folder
            self.assertEqual(child.stat().st_mode & 0o777, 0o700)
            for name in files:
                self.assertEqual((child / name).stat().st_mode & 0o777, 0o600)
        self.assertEqual((self.destination / "web-console-v0" / "index.html").read_bytes(),
                         session.SOURCE_INDEX.read_bytes())
        self.assertEqual((self.destination / "integrated-cli-v0" / "evidence-results.json").read_bytes(),
                         session.SOURCE_MOCK.read_bytes())
        output = self._record()
        self.assertEqual(set(output), session.exporter.FIELDS)
        self.assertEqual(output["cryptographic"], "VALID")
        self.assertFalse(output["browser_verified"])

    def test_refresh_replaces_only_approved_precomputed_result(self) -> None:
        self._refresh()
        original_index = (self.destination / "web-console-v0/index.html").read_bytes()
        original_mock = (self.destination / "integrated-cli-v0/evidence-results.json").read_bytes()
        self._refresh("INVALID")
        self.assertEqual(self._record()["cryptographic"], "INVALID")
        self.assertEqual(self._record()["cryptographic_reason"], "PROOF_REJECTED")
        self.assertEqual((self.destination / "web-console-v0/index.html").read_bytes(), original_index)
        self.assertEqual((self.destination / "integrated-cli-v0/evidence-results.json").read_bytes(), original_mock)
        self.assertEqual({p.name for p in self.root.iterdir()},
                         {"synthetic-package", "console-session"})

    def test_verifier_failure_preserves_last_good_result(self) -> None:
        self._refresh()
        previous = (self.destination / "web-console-v0" / session.REPLAY).read_bytes()
        bad = checked()
        bad["verification_performed"] = False
        with patch.object(session.exporter.authentic, "check_package", return_value=bad):
            with self.assertRaises(session.exporter.ExportRejected):
                session.refresh(self.package, self.destination)
        self.assertEqual((self.destination / "web-console-v0" / session.REPLAY).read_bytes(), previous)
        self.assertEqual({p.name for p in self.root.iterdir()},
                         {"synthetic-package", "console-session"})

    def test_publish_failure_preserves_last_good_result_and_cleans_stage(self) -> None:
        self._refresh()
        target = self.destination / "web-console-v0" / session.REPLAY
        previous = target.read_bytes()
        with patch.object(session.exporter.authentic, "check_package", return_value=checked("INVALID")):
            with patch.object(session.os, "replace", side_effect=OSError("test only")):
                with self.assertRaises(OSError):
                    session.refresh(self.package, self.destination)
        self.assertEqual(target.read_bytes(), previous)
        self.assertEqual({p.name for p in self.root.iterdir()},
                         {"synthetic-package", "console-session"})

    def test_swapped_directory_symlink_cannot_redirect_atomic_replacement(self) -> None:
        """Regression: old path-based replace overwrote external output after parent swap."""
        self._refresh()
        external = self.root / "external"
        external.mkdir(mode=0o700)
        sentinel = external / session.REPLAY
        sentinel.write_text("DO_NOT_OVERWRITE_EXTERNAL_FILE")
        previous_dir = self.destination / "web-console-v0"
        original_replace = os.replace

        def swap_then_replace(src, dst, *args, **kwargs):
            previous_dir.rename(self.destination / "detached-previous-view")
            previous_dir.symlink_to(external, target_is_directory=True)
            return original_replace(src, dst, *args, **kwargs)

        with patch.object(session.exporter.authentic, "check_package",
                          return_value=checked("INVALID")):
            with patch.object(session.os, "replace", side_effect=swap_then_replace):
                session.refresh(self.package, self.destination)

        self.assertEqual(sentinel.read_text(), "DO_NOT_OVERWRITE_EXTERNAL_FILE")
        self.assertEqual(
            json.loads((self.destination / "detached-previous-view" / session.REPLAY).read_text())["cryptographic"],
            "INVALID",
        )
        self.assertTrue(previous_dir.is_symlink())

    def test_swap_before_open_is_rejected_without_external_write(self) -> None:
        self._refresh()
        external = self.root / "external"
        external.mkdir(mode=0o700)
        sentinel = external / session.REPLAY
        sentinel.write_text("UNCHANGED")
        original_check = session._existing_session_safe
        calls = 0

        def check_then_swap(path):
            nonlocal calls
            original_check(path)
            calls += 1
            if calls == 2:
                view = self.destination / "web-console-v0"
                view.rename(self.destination / "detached-previous-view")
                view.symlink_to(external, target_is_directory=True)

        with patch.object(session.exporter.authentic, "check_package",
                          return_value=checked("INVALID")):
            with patch.object(session, "_existing_session_safe", side_effect=check_then_swap):
                with self.assertRaises(OSError):
                    session.refresh(self.package, self.destination)
        self.assertEqual(sentinel.read_text(), "UNCHANGED")

    def test_reject_tampered_existing_replay_and_mock_without_overwriting(self) -> None:
        self._refresh()
        replay = self.destination / "web-console-v0" / session.REPLAY
        old = replay.read_bytes()
        replay.write_text('{"proof":"private"}')
        with patch.object(session.exporter.authentic, "check_package") as verifier:
            with self.assertRaises(session.SessionRejected):
                session.refresh(self.package, self.destination)
            verifier.assert_not_called()
        self.assertEqual(replay.read_text(), '{"proof":"private"}')
        replay.write_bytes(old)
        mock = self.destination / "integrated-cli-v0/evidence-results.json"
        mock.write_text("tampered")
        with self.assertRaises(session.SessionRejected):
            session.refresh(self.package, self.destination)

    def test_reject_symlinks_unexpected_files_and_unsafe_session_location(self) -> None:
        self._refresh()
        target = self.destination / "web-console-v0" / session.REPLAY
        target.unlink()
        target.symlink_to(self.package)
        with self.assertRaises(session.SessionRejected):
            session.refresh(self.package, self.destination)
        target.unlink()
        (self.destination / "web-console-v0" / "witness").write_text("restricted test-only")
        with self.assertRaises(session.SessionRejected):
            session.refresh(self.package, self.destination)
        with self.assertRaises(session.SessionRejected):
            session.refresh(self.package, session.HERE / "forbidden-session")
        with self.assertRaises(session.SessionRejected):
            session.refresh(self.package, self.package / "forbidden-session")

    def test_cli_failure_has_no_private_path_or_witness_in_stdout(self) -> None:
        with patch("sys.argv", ["refresh_local_console.py", "--package-dir", str(self.package),
                                "--session-dir", str(self.destination)]):
            with patch.object(session.exporter.authentic, "check_package",
                              return_value={"mock": True}):
                from io import StringIO
                with patch("sys.stderr", new_callable=StringIO) as stderr:
                    code = session.main()
        self.assertEqual(code, 2)
        self.assertNotIn(str(self.package), stderr.getvalue())
        self.assertIn("SYNTHETIC_ONLY", stderr.getvalue())
        self.assertFalse(self.destination.exists())


if __name__ == "__main__":
    unittest.main()
