#!/usr/bin/env python3
"""Offline-only tests of disposable A0_SYNTHETIC preview orchestration."""
from pathlib import Path
import stat
import shutil
import tempfile
import threading
import unittest
from unittest.mock import patch
import urllib.error
import urllib.request

import run_private_preview as runner


class PreviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="tag-preview-tests-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.private = self.root / "private"
        self.private.mkdir(mode=0o700)
        self.package = self.root / "synthetic-package"
        self.package.mkdir(mode=0o700)

    def _fake_refresh(self, package, session, temporary_root):
        self.assertEqual(package, self.package)
        self.assertEqual(temporary_root.parent, self.private)
        self.assertEqual(stat.S_IMODE(temporary_root.stat().st_mode), 0o700)
        session.mkdir(mode=0o700)
        view = session / "web-console-v0"
        mock = session / "integrated-cli-v0"
        view.mkdir(parents=True, mode=0o700)
        mock.mkdir(mode=0o700)
        for target, source in (
            (view / "index.html", runner.session_cli.SOURCE_INDEX),
            (view / "authentic-evidence.json", runner.HERE / "authentic-evidence.json"),
            (mock / "evidence-results.json", runner.session_cli.SOURCE_MOCK),
        ):
            shutil.copyfile(source, target)
            target.chmod(0o600)

    def test_cleanup_success(self):
        with patch.object(runner, "offline_refresh", side_effect=self._fake_refresh):
            runner.preview(self.package, self.private, 0, serve=False)
        self.assertEqual(list(self.private.iterdir()), [])

    def test_cleanup_on_verifier_failure(self):
        with patch.object(runner, "offline_refresh", side_effect=runner.Rejected):
            with self.assertRaises(runner.Rejected):
                runner.preview(self.package, self.private, 0, serve=False)
        self.assertEqual(list(self.private.iterdir()), [])

    def test_private_parent_and_package_containment(self):
        self.private.chmod(0o755)
        with self.assertRaises(runner.Rejected):
            runner.preview(self.package, self.private, 0, serve=False)
        self.private.chmod(0o700)
        nested = self.private / "synthetic-package"
        nested.mkdir(mode=0o700)
        with self.assertRaises(runner.Rejected):
            runner.preview(nested, self.private, 0, serve=False)
        linked = self.root / "private-link"
        linked.symlink_to(self.private, target_is_directory=True)
        with self.assertRaises(runner.Rejected):
            runner.preview(self.package, linked, 0, serve=False)

    def test_no_unbounded_lifetime(self):
        with self.assertRaises(runner.Rejected):
            runner.preview(self.package, self.private, 301, serve=False)
        self.assertEqual(list(self.private.iterdir()), [])

    def test_allowlist_routes_local_only_and_cleanup(self):
        outcomes = []

        def inspect(port, session):
            self.assertEqual(stat.S_IMODE(session.stat().st_mode), 0o700)
            base = f"http://127.0.0.1:{port}"
            for uri in ("/web-console-v0/", "/web-console-v0/authentic-evidence.json",
                        "/integrated-cli-v0/evidence-results.json"):
                with urllib.request.urlopen(base + uri, timeout=2) as result:
                    self.assertEqual(result.status, 200)
                    self.assertEqual(result.headers["Cache-Control"], "no-store")
                    data = result.read()
                    self.assertGreater(len(data), 0)
            with self.assertRaises(urllib.error.HTTPError) as failed_host:
                urllib.request.urlopen(urllib.request.Request(
                    base + "/web-console-v0/", headers={"Host": "example.invalid"}), timeout=2)
            self.assertEqual(failed_host.exception.code, 404)
            failed_host.exception.close()
            for uri in ("/", "/../../../etc/passwd", "/web-console-v0/../manifest.json",
                        "/proof", "/vk", "/web-console-v0/unknown.json"):
                try:
                    urllib.request.urlopen(base + uri, timeout=2)
                    self.fail("unexpected route authorized")
                except urllib.error.HTTPError as error:
                    with error:
                        self.assertEqual(error.code, 404)
            outcomes.append("PASS")

        # ready is called before serve_forever. Run the inspector on a helper
        # thread so requests execute only once the bounded listener starts.
        def ready(port, session):
            worker = threading.Thread(target=inspect, args=(port, session))
            worker.start()
            self.addCleanup(worker.join)

        with patch.object(runner, "offline_refresh", side_effect=self._fake_refresh):
            runner.preview(self.package, self.private, 1, ready=ready)
        self.assertEqual(outcomes, ["PASS"])
        self.assertEqual(list(self.private.iterdir()), [])

    def test_modified_file_after_snapshot_cannot_be_served(self):
        observed = []
        errors = []

        def ready(port, session):
            target = session / "web-console-v0/authentic-evidence.json"
            expected = target.read_bytes()
            target.write_text("TEST_ONLY_RESTRICTED_SENTINEL_NEVER_FOR_BROWSER")
            target.chmod(0o600)

            def inspect():
                try:
                    with urllib.request.urlopen(
                        f"http://127.0.0.1:{port}/web-console-v0/authentic-evidence.json",
                        timeout=2,
                    ) as response:
                        observed.append(response.read())
                    self.assertEqual(observed, [expected])
                except Exception as exc:
                    errors.append(exc)

            self.worker = threading.Thread(target=inspect)
            self.worker.start()

        with patch.object(runner, "offline_refresh", side_effect=self._fake_refresh):
            runner.preview(self.package, self.private, 1, ready=ready)
        self.worker.join()
        self.assertFalse(errors)
        self.assertEqual(len(observed), 1)
        self.assertEqual(list(self.private.iterdir()), [])

    def test_modified_file_before_snapshot_refuses_to_serve(self):
        def modified(package, session, temporary_root):
            self._fake_refresh(package, session, temporary_root)
            replay = session / "web-console-v0/authentic-evidence.json"
            replay.write_text("TEST_ONLY_RESTRICTED_SENTINEL_NEVER_FOR_BROWSER")
            replay.chmod(0o600)

        with patch.object(runner, "offline_refresh", side_effect=modified):
            with self.assertRaises(runner.session_cli.SessionRejected):
                runner.preview(self.package, self.private, 1)
        self.assertEqual(list(self.private.iterdir()), [])

    def test_system_isolation_tool_must_be_root_owned_and_nonwritable(self):
        import os

        actual_path = Path("/usr/bin/bwrap")
        with patch.dict(os.environ, {"PATH": str(self.root) + os.pathsep + "/usr/bin"}):
            with patch.object(Path, "lstat", autospec=True) as metadata:
                metadata.return_value = type("Meta", (), {
                    "st_mode": stat.S_IFREG | 0o755, "st_uid": 0
                })()
                self.assertEqual(runner.trusted_bwrap(), actual_path)
                metadata.assert_called_once_with(actual_path)
                metadata.return_value = type("Meta", (), {
                    "st_mode": stat.S_IFREG | 0o777, "st_uid": 1000
                })()
                with self.assertRaises(runner.Rejected):
                    runner.trusted_bwrap()

    def test_zero_exit_without_validated_session_is_rejected(self):
        with patch.object(runner, "trusted_bwrap", return_value=Path("/usr/bin/bwrap")):
            with patch.object(runner.subprocess, "run", return_value=type("Result", (), {"returncode": 0})()):
                with patch.object(runner, "approved_assets", side_effect=runner.session_cli.SessionRejected):
                    with self.assertRaises(runner.Rejected):
                        runner.offline_refresh(self.package, self.private / "console", self.private)

    def test_default_private_parent_uses_approved_runtime(self):
        import os

        with patch.dict(os.environ, {"XDG_RUNTIME_DIR": str(self.private)}):
            selected = runner.default_private_parent()
            self.assertEqual(selected, self.private)
            runner.private_parent(selected, self.package)

        with patch.dict(os.environ, {"XDG_RUNTIME_DIR": ""}):
            with self.assertRaises(runner.Rejected):
                runner.private_parent(runner.default_private_parent(), self.package)

        with patch.dict(os.environ, {"XDG_RUNTIME_DIR": str(self.root)}):
            with self.assertRaises(runner.Rejected):
                runner.private_parent(runner.default_private_parent(), self.package)

    def test_runtime_fallback_uses_existing_private_user_directory(self):
        import os
        env = dict(os.environ)
        env.pop("XDG_RUNTIME_DIR", None)
        with patch.dict(os.environ, env, clear=True):
            self.assertEqual(runner.default_private_parent(), Path(f"/run/user/{os.getuid()}"))

    def test_default_parent_is_passed_to_cli_and_explicit_override_wins(self):
        import os

        argv = ["run_private_preview.py", "--package-dir", str(self.package), "--no-serve"]
        with patch.dict(os.environ, {"XDG_RUNTIME_DIR": str(self.private)}):
            with patch.object(runner.sys, "argv", argv):
                with patch.object(runner, "preview") as invoke:
                    self.assertEqual(runner.main(), 0)
                    self.assertEqual(invoke.call_args.args[:3],
                                     (self.package, self.private, 30))
            with patch.object(runner.sys, "argv", argv + [
                "--private-parent", str(self.root)]):
                with patch.object(runner, "preview") as invoke:
                    self.assertEqual(runner.main(), 0)
                    self.assertEqual(invoke.call_args.args[1], self.root)

    def test_offline_invocation_has_network_and_file_isolation(self):
        recorded = []

        def fake_run(args, **kwargs):
            recorded.append((args, kwargs))
            return type("Completed", (), {"returncode": 0})()

        with patch.object(runner, "trusted_bwrap", return_value=Path("/usr/bin/bwrap")):
            with patch.object(runner.subprocess, "run", side_effect=fake_run):
                with patch.object(runner, "approved_assets", return_value={}):
                    runner.offline_refresh(self.package, self.private / "console", self.private)
        args, kwargs = recorded[0]
        self.assertIn("--unshare-net", args)
        self.assertIn("--ro-bind", args)
        self.assertEqual(args[args.index("--bind")+1], str(self.private))
        self.assertEqual(kwargs["timeout"], 90)
        self.assertNotIn("PYTHONPATH", kwargs["env"])
        self.assertNotIn("HOME", kwargs["env"])


if __name__ == "__main__":
    unittest.main()
