#!/usr/bin/env python3
"""Startup-only fail-closed checks for opt-in, non-Production TAG #88 service.

No mounts or elevated operations are performed by this module.
"""
from __future__ import annotations

from contextlib import contextmanager
import os
import pwd
import grp
from pathlib import Path
import stat

RUNTIME = Path("/run/tag-qa88")
CONTROL = Path("/run/tag-qa88-control")
UNIT = "tag-qa88-persistent.service"
EXPECTED_CGROUP = "/tag.slice/tag-qa88.slice/" + UNIT
EXPECTED_LIMITS = {
    "memory.max": "134217728", "memory.swap.max": "0",
    "cpu.max": "50000 100000", "pids.max": "12",
}


class GateRejected(Exception):
    """No listener may start if any prerequisite cannot be attested."""


def expected_identity() -> tuple[int, int]:
    """Resolve the fixed, dedicated system account; never accept UID 0."""
    try:
        user = pwd.getpwnam("tag-qa88")
        group = grp.getgrnam("tag-qa88")
    except KeyError as exc:
        raise GateRejected from exc
    if user.pw_uid <= 0 or group.gr_gid <= 0 or user.pw_gid != group.gr_gid:
        raise GateRejected
    return user.pw_uid, group.gr_gid


def private_dir(path: Path) -> None:
    try:
        entry = path.lstat()
        uid, gid = expected_identity()
        if (not path.is_absolute() or str(path) != os.path.realpath(path)
                or not stat.S_ISDIR(entry.st_mode)
                or entry.st_uid != uid or entry.st_gid != gid
                or stat.S_IMODE(entry.st_mode) != 0o700):
            raise GateRejected
    except OSError as exc:
        raise GateRejected from exc


def verify_identity_and_cgroup(*, proc: Path = Path("/proc"),
                               cgroup_root: Path = Path("/sys/fs/cgroup")) -> None:
    uid, gid = expected_identity()
    if os.geteuid() != uid or os.getegid() != gid:
        raise GateRejected
    try:
        status = (proc / "self/status").read_text()
        attributes = dict(line.split(":", 1) for line in status.splitlines() if ":" in line)
        if (attributes["CapEff"].strip() != "0000000000000000"
                or attributes["NoNewPrivs"].strip() != "1"):
            raise GateRejected
        rows = (proc / "self/cgroup").read_text().strip().splitlines()
        if rows != ["0::" + EXPECTED_CGROUP]:
            raise GateRejected
        group = cgroup_root / EXPECTED_CGROUP.lstrip("/")
        for prop, value in EXPECTED_LIMITS.items():
            if (group / prop).read_text().strip() != value:
                raise GateRejected
    except (OSError, KeyError) as exc:
        raise GateRejected from exc


def verify_mount(path: Path) -> None:
    try:
        mounts = [line for line in Path("/proc/self/mountinfo").read_text().splitlines()
                  if line.split()[4] == str(path)]
        if len(mounts) != 1 or " - tmpfs " not in mounts[0]:
            raise GateRejected
        fs = os.statvfs(path)
        if (not 0 < fs.f_blocks * fs.f_frsize <= 8 * 1024 * 1024
                or not 0 < fs.f_files <= 128):
            raise GateRejected
        # /run is a separate host tmpfs; this runtime must be its own mount.
        if path.stat().st_dev == path.parent.stat().st_dev:
            raise GateRejected
    except (OSError, ValueError, IndexError) as exc:
        raise GateRejected from exc


def persistent_preflight(runtime: Path, token_file: Path) -> Path:
    """Only expected fixed paths and the dedicated quota-backed mount."""
    if runtime != RUNTIME or token_file != CONTROL / "operator.token":
        raise GateRejected
    verify_identity_and_cgroup()
    private_dir(runtime)
    verify_mount(runtime)
    private_dir(CONTROL)
    if CONTROL.stat().st_dev != Path("/run").stat().st_dev:
        raise GateRejected  # token control-plane must remain in volatile /run.
    if list(runtime.iterdir()) or list(CONTROL.iterdir()):
        raise GateRejected  # stale session/token: no implicit cleanup/reuse.
    work = runtime / "work"
    try:
        work.mkdir(mode=0o700)
        private_dir(work)
    except OSError as exc:
        raise GateRejected from exc
    return work


@contextmanager
def exclusive_token_file(path: Path, token: str):
    """Owner-only, boot-volatile control-plane token; not a result or proof file."""
    if path != CONTROL / "operator.token":
        raise GateRejected
    private_dir(path.parent)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC
    try:
        fd = os.open(path, flags, 0o600)
    except OSError as exc:
        raise GateRejected from exc
    entry = os.fstat(fd)
    try:
        uid, gid = expected_identity()
        if (entry.st_uid != uid or entry.st_gid != gid
                or stat.S_IMODE(entry.st_mode) != 0o600):
            raise GateRejected
        os.write(fd, (token + "\n").encode("ascii"))
    finally:
        os.close(fd)
    try:
        yield token
    finally:
        try:
            if path.lstat().st_ino == entry.st_ino and path.lstat().st_dev == entry.st_dev:
                path.unlink()
        except FileNotFoundError:
            pass
