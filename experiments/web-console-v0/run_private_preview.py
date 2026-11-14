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
import stat
import subprocess
import sys
import tempfile
import threading

import refresh_local_console as session_cli

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


def approved_assets(session: Path) -> dict[str, tuple[bytes, str]]:
    """Freeze verified public display bytes before exposing any HTTP endpoint.

    Session directories are private but another same-UID process could modify
    one while the viewer runs. Never re-open a mutable path during a request.
    """
    session_cli._existing_session_safe(session)
    result = {}
    for uri, (name, content_type) in ROUTES.items():
        if name in result:
            continue
        path = session / name
        meta = path.lstat()
        if (not stat.S_ISREG(meta.st_mode) or meta.st_uid != os.getuid()
                or stat.S_IMODE(meta.st_mode) != 0o600 or meta.st_size > 65536):
            raise Rejected
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
        try:
            current = os.fstat(fd)
            if ((current.st_dev, current.st_ino) != (meta.st_dev, meta.st_ino)
                    or current.st_uid != os.getuid()
                    or stat.S_IMODE(current.st_mode) != 0o600
                    or not stat.S_ISREG(current.st_mode)):
                raise Rejected
            with os.fdopen(fd, "rb", closefd=False) as handle:
                body = handle.read(65537)
        finally:
            os.close(fd)
        if len(body) > 65536:
            raise Rejected
        if name == "web-console-v0/index.html":
            if body != session_cli.SOURCE_INDEX.read_bytes():
                raise Rejected
        elif name == "integrated-cli-v0/evidence-results.json":
            if body != session_cli.SOURCE_MOCK.read_bytes():
                raise Rejected
        elif name == "web-console-v0/authentic-evidence.json":
            if not session_cli._prior_replay_safe(body):
                raise Rejected
        else:
            raise Rejected
        result[name] = (body, content_type)
    return {uri: result[name] for uri, (name, _) in ROUTES.items()}


class Preview(http.server.BaseHTTPRequestHandler):
    # Materialized immutable allowlisted response bytes, never source file paths.
    assets: dict[str, tuple[bytes, str]]

    def log_message(self, *args: object) -> None:
        pass

    def do_GET(self) -> None:
        if self.headers.get("Host") != f"127.0.0.1:{self.server.server_port}":
            self.send_error(404, "Not found")
            return
        route = self.path.split("?", 1)[0]
        asset = self.assets.get(route)
        if asset is None:
            self.send_error(404, "Not found")
            return
        body, content_type = asset
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


def trusted_bwrap() -> Path:
    # Explicit system path, never a potentially PATH-shadowed executable.
    bwrap = Path("/usr/bin/bwrap")
    try:
        info = bwrap.lstat()
        if (not stat.S_ISREG(info.st_mode) or info.st_uid != 0
                or stat.S_IMODE(info.st_mode) & 0o022):
            raise Rejected
    except OSError:
        raise Rejected from None
    return bwrap


def offline_refresh(package: Path, session: Path, temporary_root: Path) -> None:
    # The existing exporter/CLI performs independent genuine cryptographic
    # verification and strict allowlisting; never reimplement it here.
    # Qube-specific trust boundary: PATH may include untrusted executable names.
    # Do not silently accept a substituted bwrap that skips network isolation.
    bwrap = trusted_bwrap()
    isolated = [
        str(bwrap), "--unshare-net", "--ro-bind", "/", "/",
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
    # Success is not the subprocess exit code alone: verify the complete
    # minimized/allowlisted session exists even when --no-serve is selected.
    try:
        approved_assets(session)
    except session_cli.SessionRejected:
        raise Rejected from None


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
        assets = approved_assets(session)
        handler = type("AllowlistedSessionPreview", (Preview,), {"assets": assets})
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


def default_private_parent() -> Path:
    """Select an existing owner-private runtime directory, never generic /tmp.

    XDG_RUNTIME_DIR is accepted only after the same strict parent validation
    that applies to an explicit --private-parent. A supplied unsafe XDG value
    must fail closed; it must not silently fall back to another location.
    """
    configured = os.environ.get("XDG_RUNTIME_DIR")
    if configured is not None:
        return Path(configured)
    return Path(f"/run/user/{os.getuid()}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-dir", type=Path, required=True)
    parser.add_argument("--private-parent", type=Path,
                        help="existing private 0700 directory (default: validated XDG_RUNTIME_DIR or /run/user/UID)")
    parser.add_argument("--seconds", type=int, default=30,
                        help="bounded preview lifetime: 0-300 seconds, default 30")
    parser.add_argument("--no-serve", action="store_true",
                        help="offline verification + ephemeral export + cleanup only")
    args = parser.parse_args()
    try:
        parent = args.private_parent if args.private_parent is not None else default_private_parent()
        preview(args.package_dir, parent, args.seconds,
                serve=not args.no_serve)
    except (Rejected, session_cli.SessionRejected, OSError, ValueError):
        print(f"{LABEL}: preview not started; no persistent session", file=sys.stderr)
        return 2
    print(f"{LABEL}: local preview closed; temporary session disposed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
