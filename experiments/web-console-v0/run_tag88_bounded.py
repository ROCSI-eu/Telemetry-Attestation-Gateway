#!/usr/bin/env python3
"""Opt-in, unprivileged TAG #88 local aggregate limits; synthetic short-circuit only.

EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC
NOT VALIDATION OR PRODUCTION AUTHORIZATION

No system service is installed or enabled; each invocation uses a collected
transient user unit in its own cgroup. No production or proof workloads.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import secrets
import socket
import stat
import subprocess
import sys

sys.dont_write_bytecode = True
import run_isolated_local as local  # noqa: E402

HERE = Path(__file__).resolve().parent
SLICE = "tag-qa88.slice"
UNIT_PREFIX = "tag-qa88-bounded-"
MEMORY_MAX = "134217728"
TASKS_MAX = "12"
CPU_MAX = "50000 100000"
RUNTIME_SECONDS = 15


class Unavailable(Exception):
    """Fail closed, without relaying user-bus or service implementation details."""


def user_cgroup_root() -> Path:
    uid = os.geteuid()
    return Path("/sys/fs/cgroup/user.slice") / f"user-{uid}.slice" / f"user@{uid}.service"


def verify_inside(unit: str, *, root: Path | None = None,
                  membership: str | None = None) -> None:
    """Reject missing/wrong service or ignored hard quotas before a listener."""
    if not re.fullmatch(r"tag-qa88-bounded-[0-9a-f]{12}\.service", unit):
        raise Unavailable
    uid = os.geteuid()
    expected = (f"/user.slice/user-{uid}.slice/user@{uid}.service/"
                f"tag.slice/{SLICE}/{unit}")
    try:
        actual = (membership if membership is not None
                  else Path("/proc/self/cgroup").read_text().strip().split("::", 1)[1])
        if actual != expected:
            raise Unavailable
        group = (root if root is not None else Path("/sys/fs/cgroup")) / actual.lstrip("/")
        if ((group / "memory.max").read_text().strip() != MEMORY_MAX
                or (group / "pids.max").read_text().strip() != TASKS_MAX
                or (group / "cpu.max").read_text().strip() != CPU_MAX):
            raise Unavailable
    except (OSError, IndexError, ValueError) as exc:
        raise Unavailable from exc


def safe_user_bus() -> dict[str, str]:
    uid = os.geteuid()
    if uid == 0:
        raise Unavailable
    base = Path(f"/run/user/{uid}")
    bus = base / "bus"
    try:
        info = bus.stat()
        binary = Path("/usr/bin/systemd-run").lstat()
        if (not stat.S_ISSOCK(info.st_mode) or info.st_uid != uid
                or not stat.S_ISREG(binary.st_mode) or binary.st_uid != 0
                or stat.S_IMODE(binary.st_mode) & 0o022):
            raise Unavailable
    except OSError as exc:
        raise Unavailable from exc
    return {
        "PATH": "/usr/bin:/bin",
        "LANG": "C.UTF-8",
        "XDG_RUNTIME_DIR": str(base),
        "DBUS_SESSION_BUS_ADDRESS": f"unix:path={bus}",
        "PYTHONDONTWRITEBYTECODE": "1",
    }


def systemctl(env: dict[str, str], *args: str) -> str:
    result = subprocess.run(
        ["/usr/bin/systemctl", "--user", *args],
        stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL, text=True, timeout=3, env=env,
        check=False,
    )
    if result.returncode:
        raise Unavailable
    return result.stdout.strip()


def own_slice_empty(root: Path) -> bool:
    """Only an empty, known TAG #88 slice may be stopped; never touch app.slice."""
    if not root.exists():
        return True
    try:
        events = dict(line.split() for line in (root / "cgroup.events").read_text().splitlines())
        return (events.get("populated") == "0"
                and (root / "cgroup.procs").read_text().strip() == ""
                and not any(child.is_dir() for child in root.iterdir()))
    except (OSError, ValueError):
        return False


def cleanup(env: dict[str, str], unit: str) -> None:
    """Stop only a verified own unit, then remove only the empty own slice."""
    state = systemctl(env, "show", "-P", "ActiveState", unit)
    if state not in ("inactive", "failed"):
        scope = systemctl(env, "show", "-P", "Slice", unit)
        cg = systemctl(env, "show", "-P", "ControlGroup", unit)
        if scope != SLICE or not cg.endswith("/" + SLICE + "/" + unit):
            raise Unavailable
        systemctl(env, "stop", unit)
    root = user_cgroup_root() / "tag.slice" / SLICE
    if not own_slice_empty(root):
        raise Unavailable
    if root.exists():
        systemctl(env, "stop", SLICE)
    if root.exists() or systemctl(env, "show", "-P", "ActiveState", SLICE) != "inactive":
        raise Unavailable


def build_command(unit: str, parent: Path, seconds: int, check_only: bool) -> list[str]:
    cmd = [
        "/usr/bin/systemd-run", "--user", "--wait", "--pipe", "--collect",
        f"--unit={unit}", f"--slice={SLICE}",
        "-p", f"MemoryMax={MEMORY_MAX}",
        "-p", "CPUQuota=50%",
        "-p", f"TasksMax={TASKS_MAX}",
        "-p", f"RuntimeMaxSec={RUNTIME_SECONDS}s",
        "-p", "KillMode=control-group",
        "/usr/bin/python3", "-B", str(HERE / "run_tag88_bounded.py"),
        "--inside", "--unit-name", unit, "--runtime-parent", str(parent),
        "--seconds", str(seconds),
    ]
    if check_only:
        cmd.append("--check-only")
    return cmd


def launch(parent: Path, seconds: int, check_only: bool) -> int:
    local.private_parent(parent)
    local.bridge.trusted_bwrap()
    env = safe_user_bus()
    root = user_cgroup_root() / "tag.slice" / SLICE
    if root.exists():  # stale or concurrent service: require separate owner inspection
        raise Unavailable
    unit = UNIT_PREFIX + secrets.token_hex(6) + ".service"
    if systemctl(env, "show", "-P", "ActiveState", unit) != "inactive":
        raise Unavailable
    cmd = build_command(unit, parent, seconds, check_only)
    result = 1
    try:
        result = subprocess.run(
            cmd, stdin=subprocess.DEVNULL, stdout=None, stderr=subprocess.DEVNULL,
            timeout=20, check=False, env=env,
        ).returncode
    except subprocess.TimeoutExpired:
        pass  # cleanup only the verified transient TAG-owned unit
    finally:
        cleanup(env, unit)
    return 0 if result == 0 else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-parent", type=Path, required=True)
    parser.add_argument("--seconds", type=int, default=8)
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--inside", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--unit-name", default="", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if not 1 <= args.seconds <= 10:
        parser.error("bounded synthetic session must be 1-10 seconds")
    try:
        if args.inside:
            verify_inside(args.unit_name)
            flags = ["--runtime-parent", str(args.runtime_parent),
                     "--seconds", str(args.seconds), "--tag88-tmpfs-8m"]
            if args.check_only:
                flags.append("--check-only")
            return local.main(flags)
        if args.unit_name:
            raise Unavailable
        return launch(args.runtime_parent, args.seconds, args.check_only)
    except (Unavailable, local.Unavailable, OSError, ValueError, subprocess.SubprocessError):
        print("UNAVAILABLE · TAG #88 cgroup or cleanup gate failed", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
