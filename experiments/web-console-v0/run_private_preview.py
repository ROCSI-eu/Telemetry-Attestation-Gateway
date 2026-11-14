#!/usr/bin/env python3
"""One disposable local synthetic offline-verifier-to-console preview.

EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC
NOT VALIDATION OR PRODUCTION AUTHORIZATION

Requires an existing demonstrably synthetic proof package and locally pinned
verifier; this orchestrator never creates witnesses, runs a prover, or downloads
security material. No public listener, long-lived job, or production surface.
"""
from __future__ import annotations

import argparse
import http.server
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import threading

HERE = Path(__file__).resolve().parent
REFRESH = HERE / "refresh_local_console.py"
LABEL = "EXPERIMENTAL SYNTHETIC_ONLY A0_SYNTHETIC NOT VALIDATION OR PRODUCTION AUTHORIZATION"
ROUTES = {
    "/web-console-v0/": ("web-console-v0/index.html", "text/html; charset=utf-8"),
    "/web-console-v0/index.html": ("web-console-v0/index.html", "text/html; charset=utf-8"),
    "/web-console-v0/authentic-evidence.json": ("web-console-v0/authentic-evidence.json", "application/json"),
    "/integrated-cli-v0/evidence-results.json": ("integrated-cli-v0/evidence-results.json", "application/json"),
}


class Rejected(Exception):
    """Public errors must not include file paths or proof contents."""


def private_parent(parent: Path, package: Path) -> None:
    if not parent.is_absolute() or not package.is_absolute():
        raise Rejected
    if (Path(os.path.abspath(parent)) != Path(os.path.realpath(parent))
            or Path(os.path.abspath(package)) != Path(os.path.realpath(package))):
        raise Rejected
    meta = parent.lstat()
    if (not stat.S_ISDIR(meta.st_mode) or meta.st_uid != os.getuid()
            or stat.S_IMODE(meta.st_mode) != 0o700):
        raise Rejected
    parent = parent.resolve()
    package = package.resolve()
    if parent == package or parent in package.parents or package in parent.parents:
        raise Rejected
    if HERE.parents[1] == parent or HERE.parents[1] in parent.parents:
        raise Rejected


class Preview(http.server.BaseHTTPRequestHandler):
    # Set from factory, never accept arbitrary URL paths as file names.
    session: Path

    def log_message(self, *args: object) -> None:
        pass

    def do_GET(self) -> None:
        if self.headers.get("Host") != f"127.0.0.1:{self.server.server_port}":
            self.send_error(404, "Not found")
            return
        route = self.path.split("?", 1)[0]
        if route not in ROUTES:
            self.send_error(404, "Not found")
            return
        name, content_type = ROUTES[route]
        try:
            target = self.session / name
            meta = target.lstat()
            if (not stat.S_ISREG(meta.st_mode) or meta.st_uid != os.getuid()
                    or stat.S_IMODE(meta.st_mode) != 0o600 or meta.st_size > 65536):
                raise Rejected
            fd = os.open(target, os.O_RDONLY | os.O_NOFOLLOW)
            try:
                actual = os.fstat(fd)
                if ((actual.st_dev, actual.st_ino) != (meta.st_dev, meta.st_ino)
                        or not stat.S_ISREG(actual.st_mode)):
                    raise Rejected
                with os.fdopen(fd, "rb", closefd=False) as handle:
                    body = handle.read(65537)
                if len(body) > 65536:
                    raise Rejected
            finally:
                os.close(fd)
        except (OSError, Rejected):
            self.send_error(404, "Not found")
            return
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy",
                         "default-src 'none'; connect-src 'self'; "
                         "style-src 'unsafe-inline'; script-src 'unsafe-inline'")
        self.end_headers()
        self.wfile.write(body)


def offline_refresh(package: Path, session: Path, temporary_root: Path) -> None:
    # The existing exporter/CLI performs independent genuine cryptographic
    # verification and strict allowlisting; never reimplement it here.
    bwrap = shutil.which("bwrap")
    if not bwrap:
        raise Rejected
    isolated = [
        bwrap, "--unshare-net", "--ro-bind", "/", "/",
        "--bind", str(temporary_root), str(temporary_root),
        "--dev-bind", "/dev", "/dev", "--proc", "/proc",
        "--setenv", "HOME", str(temporary_root),
        "--setenv", "TMPDIR", str(temporary_root),
        "--setenv", "PATH", os.environ.get("PATH", "/usr/bin:/bin"),
        "--", sys.executable, str(REFRESH),
        "--package-dir", str(package), "--session-dir", str(session),
    ]
    try:
        completed = subprocess.run(
            isolated, timeout=90, check=False, capture_output=True,
            env={"PATH": os.environ.get("PATH", "/usr/bin:/bin"),
                 "LANG": "C.UTF-8", "PYTHONDONTWRITEBYTECODE": "1"},
        )
    except (OSError, subprocess.TimeoutExpired):
        raise Rejected from None
    if completed.returncode:
        raise Rejected


def preview(package: Path, parent: Path, seconds: int, serve: bool = True,
            ready: object = None) -> None:
    private_parent(parent, package)
    if not 0 <= seconds <= 300 or (serve and seconds == 0):
        raise Rejected
    with tempfile.TemporaryDirectory(prefix="tag-local-preview-", dir=parent) as tmp:
        root = Path(tmp)
        session = root / "console"
        offline_refresh(package, session, root)
        if not serve:
            return
        handler = type("AllowlistedSessionPreview", (Preview,), {"session": session})
        # This port is allocated by the OS, never selected from user input.
        with http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler) as server:
            server.daemon_threads = True
            if ready is not None:
                ready(server.server_address[1], session)
            print(f"{LABEL}: temporary loopback preview at "
                  f"http://127.0.0.1:{server.server_address[1]}/web-console-v0/",
                  flush=True)
            if seconds:
                timer = threading.Timer(seconds, server.shutdown)
                timer.daemon = True
                timer.start()
                try:
                    server.serve_forever(poll_interval=0.1)
                finally:
                    timer.cancel()
            # seconds=0 creates no HTTP serving interval; useful for tests.
    # TemporaryDirectory closes after the loopback HTTP server closes.


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-dir", type=Path, required=True)
    parser.add_argument("--private-parent", type=Path, required=True,
                        help="existing 0700 owner-only directory outside Git and package")
    parser.add_argument("--seconds", type=int, default=30,
                        help="bounded preview lifetime: 0-300 seconds, default 30")
    parser.add_argument("--no-serve", action="store_true",
                        help="offline verification + ephemeral export + cleanup only")
    args = parser.parse_args()
    try:
        preview(args.package_dir, args.private_parent, args.seconds,
                serve=not args.no_serve)
    except (Rejected, OSError, ValueError):
        print(f"{LABEL}: preview not started; no persistent session", file=sys.stderr)
        return 2
    print(f"{LABEL}: local preview closed; temporary session disposed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
