#!/usr/bin/env python3
"""Bounded, foreground-only local package for the synthetic web console.

EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC
NOT VALIDATION OR PRODUCTION AUTHORIZATION

No installation, service identity, global state, public listener, toolchain
provisioning, proof creation, or persistent job is performed by this launcher.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import resource
import signal
import stat
import subprocess
import sys
import tempfile

import local_cli_bridge as bridge

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
LABEL = "EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION"


class Unavailable(Exception):
    """Fail without disclosing private paths, process details, or credentials."""


class StopRequested(Exception):
    """Foreground termination requested; owned child still needs cleanup."""


def private_parent(parent: Path) -> None:
    """Only an existing owner-controlled directory outside the checkout."""
    if os.geteuid() == 0 or not parent.is_absolute():
        raise Unavailable
    if Path(os.path.abspath(parent)) != Path(os.path.realpath(parent)):
        raise Unavailable
    if parent == REPO or REPO in parent.parents:
        raise Unavailable
    try:
        info = parent.lstat()
    except OSError as exc:
        raise Unavailable from exc
    if (not stat.S_ISDIR(info.st_mode) or info.st_uid != os.geteuid()
            or stat.S_IMODE(info.st_mode) & 0o022):
        raise Unavailable


def isolated_env(runtime: Path) -> dict[str, str]:
    """Do not inherit user, provider, production or credential variables."""
    value = str(runtime)
    return {
        "PATH": "/usr/bin:/bin",
        "HOME": value,
        "TMPDIR": value,
        "XDG_CACHE_HOME": value,
        "LANG": "C.UTF-8",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONNOUSERSITE": "1",
    }


def limits() -> None:
    """A small inherited FD/core envelope; CLI imposes its own CPU/RAM caps."""
    hard = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
    soft = 64 if hard == resource.RLIM_INFINITY else min(64, hard)
    resource.setrlimit(resource.RLIMIT_NOFILE, (soft, hard))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def stop_owned(proc: subprocess.Popen[bytes]) -> None:
    """Terminate only this launcher's process group, never unrelated PIDs."""
    if proc.poll() is not None:
        return
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        proc.wait(timeout=3)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        proc.wait(timeout=3)


def run(seconds: int, parent: Path, check_only: bool) -> int:
    private_parent(parent)
    bridge.trusted_bwrap()  # fail before any listener or process
    old_umask = os.umask(0o077)
    try:
        with tempfile.TemporaryDirectory(prefix="tag-synthetic-", dir=parent) as private:
            runtime = Path(private)
            mode = runtime.lstat()
            if (mode.st_uid != os.geteuid()
                    or stat.S_IMODE(mode.st_mode) != 0o700):
                raise Unavailable
            print(LABEL, flush=True)
            if check_only:
                print("LOCAL PRECHECK PASS · no process, listener, proof or persistent state", flush=True)
                return 0
            print("LOCAL ONE-SHOT · loopback only · temporary runtime · no logs persisted", flush=True)
            cmd = [
                sys.executable, "-I", str(HERE / "local_cli_bridge.py"),
                "--seconds", str(seconds),
            ]
            # Never pass a toolchain path: genuine proof generation is unavailable
            # in this minimal package unless separately provisioned and authorized.
            previous = {}
            def on_stop(signum: int, frame: object) -> None:
                raise StopRequested
            for sig in (signal.SIGTERM, signal.SIGHUP):
                previous[sig] = signal.signal(sig, on_stop)
            try:
                proc = subprocess.Popen(
                    cmd, stdin=subprocess.DEVNULL,
                    stdout=None, stderr=subprocess.DEVNULL,
                    cwd=runtime, env=isolated_env(runtime),
                    start_new_session=True, preexec_fn=limits,
                )
                try:
                    returncode = proc.wait(timeout=seconds + 8)
                    if returncode != 0:
                        raise Unavailable
                    return 0
                finally:
                    stop_owned(proc)
            finally:
                for sig, handler in previous.items():
                    signal.signal(sig, handler)
    finally:
        os.umask(old_umask)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seconds", type=int, default=90,
                        help="opt-in foreground lifetime (1-300 seconds)")
    parser.add_argument("--runtime-parent", type=Path, default=Path.home(),
                        help="existing owner-controlled, non-writable-by-others parent")
    parser.add_argument("--check-only", action="store_true",
                        help="validate isolation prerequisites without starting the bridge")
    args = parser.parse_args(argv)
    if not 1 <= args.seconds <= 300:
        parser.error("preview lifetime must be 1-300 seconds")
    try:
        return run(args.seconds, args.runtime_parent, args.check_only)
    except (Unavailable, bridge.Rejected, OSError, ValueError,
            subprocess.TimeoutExpired, subprocess.SubprocessError):
        print("UNAVAILABLE · local isolation or lifecycle preflight failed", file=sys.stderr)
        return 1
    except (KeyboardInterrupt, StopRequested):
        print("LOCAL SESSION STOPPED · owned process cleanup requested", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
