#!/usr/bin/env python3
"""TAG #88 non-Production installer and read-only persistent-mount verifier.

No runtime mount, chmod, unlink or rmdir occurs on service start/stop.
Install/remove are separate, root-only, explicitly authorized operations.
"""
from __future__ import annotations

import argparse
import grp
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import pwd
import re
import shutil
import stat
import subprocess
import sys
import tarfile

ACCOUNT = "tag-qa88"
PREFIX = Path("/opt/tag-qa88")
UNIT_PATH = Path("/etc/systemd/system/tag-qa88-persistent.service")
LEGACY_CLEAN_UNIT_PATH = Path("/etc/systemd/system/tag-qa88-postcleanup.service")
UNIT_NAME = "tag-qa88-persistent.service"
TEMPLATE = Path("experiments/web-console-v0/tag-qa88-persistent.service")
HOST_PARENT = Path("/var/lib/tag-qa88")
MOUNT = HOST_PARENT / "runtime"
CONTROL = Path("/run/tag-qa88-control")
ROOT_UID = 0
ROOT_GID = 0
SHA_RE = re.compile(r"[a-f0-9]{40}\Z")
DIAGNOSTICS = frozenset({
    "VERIFY_ROOT_REQUIRED", "VERIFY_RECEIPT_INVALID", "VERIFY_IDENTITY",
    "VERIFY_HOST_INVALID", "VERIFY_HOST_CHANGED", "VERIFY_HOST_MOUNTED",
    "VERIFY_PRIVATE_INVALID", "VERIFY_PRIVATE_FLAGS", "VERIFY_PRIVATE_IDENTITY",
    "VERIFY_PRIVATE_QUOTA", "VERIFY_MOUNTINFO_INVALID",
})


class Refused(RuntimeError):
    pass


class MountRefused(Refused):
    """Fixed non-secret failure codes for the start-time gate."""
    def __init__(self, code: str):
        if code not in DIAGNOSTICS:
            raise ValueError("unknown diagnostic code")
        self.code = code
        super().__init__(code)


def require_root() -> None:
    if os.geteuid() != 0:
        raise Refused("local root authorization required")


def checked_identity() -> tuple[int, int]:
    try:
        user, group = pwd.getpwnam(ACCOUNT), grp.getgrnam(ACCOUNT)
    except KeyError as exc:
        raise Refused("dedicated identity missing") from exc
    if user.pw_uid <= 0 or group.gr_gid <= 0 or user.pw_gid != group.gr_gid:
        raise Refused("unexpected identity")
    return user.pw_uid, group.gr_gid


def checked_abs(path: Path) -> Path:
    if not path.is_absolute() or path != Path(os.path.realpath(path)):
        raise Refused("path is not absolute or contains a symlink")
    return path


def must_be_absent(*paths: Path) -> None:
    if any(os.path.lexists(p) for p in paths):
        raise Refused("existing installation path; no implicit adoption")


def _mount_row(path: Path, table: Path) -> tuple[str, set[str]] | None:
    """Match an exact, fixed mountpoint; ambiguous/unreadable tables reject."""
    try:
        matches = [line.split() for line in table.read_text().splitlines()
                   if len(line.split()) > 4 and line.split()[4] == str(path)]
        if len(matches) > 1:
            raise MountRefused("VERIFY_MOUNTINFO_INVALID")
        if not matches:
            return None
        fields = matches[0]
        separator = fields.index("-")
        return fields[separator + 1], set(fields[5].split(","))
    except (OSError, IndexError, ValueError) as exc:
        raise MountRefused("VERIFY_MOUNTINFO_INVALID") from exc


def _checked_directory(path: Path, owner: tuple[int, int], mode: int) -> tuple[int, os.stat_result]:
    try:
        fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
        entry = os.fstat(fd)
        current = path.lstat()
        if (not stat.S_ISDIR(entry.st_mode)
                or (entry.st_dev, entry.st_ino) != (current.st_dev, current.st_ino)
                or (entry.st_uid, entry.st_gid) != owner
                or stat.S_IMODE(entry.st_mode) != mode):
            raise MountRefused("VERIFY_HOST_INVALID")
        return fd, entry
    except OSError as exc:
        if "fd" in locals():
            os.close(fd)
        raise MountRefused("VERIFY_HOST_INVALID") from exc
    except BaseException:
        if "fd" in locals():
            os.close(fd)
        raise


def verified_host(*, root: Path, table: Path, expected: dict | None = None) -> dict[str, int]:
    """Inspect stable host anchor, never adopt or modify an existing directory.

    For the service hook, root=/proc/1/root and table=/proc/1/mountinfo.
    The host-side directory is root-owned and inaccessible for modification
    by the unprivileged service; private tmpfs never changes the host inode.
    """
    parent = root / HOST_PARENT.relative_to("/")
    child = root / MOUNT.relative_to("/")
    if _mount_row(HOST_PARENT, table) is not None or _mount_row(MOUNT, table) is not None:
        raise MountRefused("VERIFY_HOST_MOUNTED")
    parent_fd, parent_st = _checked_directory(parent, (ROOT_UID, ROOT_GID), 0o755)
    try:
        child_fd, child_st = _checked_directory(child, (ROOT_UID, ROOT_GID), 0o755)
        try:
            if (parent_st.st_dev != child_st.st_dev
                    or os.listdir(parent_fd) != [MOUNT.name]
                    or os.listdir(child_fd)):
                raise MountRefused("VERIFY_HOST_INVALID")
            observed = {
                "parent_dev": parent_st.st_dev, "parent_ino": parent_st.st_ino,
                "mount_dev": child_st.st_dev, "mount_ino": child_st.st_ino,
            }
            if expected is not None and observed != expected:
                raise MountRefused("VERIFY_HOST_CHANGED")
            return observed
        finally:
            os.close(child_fd)
    finally:
        os.close(parent_fd)


def verified_private(*, table: Path = Path("/proc/self/mountinfo")) -> None:
    """Validate the service's independent, bounded tmpfs before the CLI."""
    row = _mount_row(MOUNT, table)
    if row is None or row[0] != "tmpfs":
        raise MountRefused("VERIFY_PRIVATE_INVALID")
    if not {"nodev", "nosuid", "noexec"}.issubset(row[1]):
        raise MountRefused("VERIFY_PRIVATE_FLAGS")
    try:
        uid, gid = checked_identity()
    except Refused as exc:
        raise MountRefused("VERIFY_PRIVATE_IDENTITY") from exc
    try:
        fd, entry = _checked_directory(MOUNT, (uid, gid), 0o700)
    except MountRefused as exc:
        raise MountRefused("VERIFY_PRIVATE_IDENTITY") from exc
    try:
        quota = os.fstatvfs(fd)
        if os.listdir(fd):
            raise MountRefused("VERIFY_PRIVATE_INVALID")
        if (entry.st_dev == MOUNT.parent.stat().st_dev
                or not 0 < quota.f_blocks * quota.f_frsize <= 8388608
                or not 0 < quota.f_files <= 128):
            raise MountRefused("VERIFY_PRIVATE_QUOTA")
    except OSError as exc:
        raise MountRefused("VERIFY_PRIVATE_INVALID") from exc
    finally:
        os.close(fd)


def trusted_receipt() -> dict:
    try:
        fd = os.open(PREFIX / "receipt.json", os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
        try:
            st = os.fstat(fd)
            if (not stat.S_ISREG(st.st_mode) or st.st_nlink != 1
                    or (st.st_uid, st.st_gid) != (ROOT_UID, ROOT_GID)
                    or stat.S_IMODE(st.st_mode) != 0o644 or st.st_size > 131072):
                raise MountRefused("VERIFY_RECEIPT_INVALID")
            with os.fdopen(fd, "r", closefd=False) as f:
                receipt = json.load(f)
        finally:
            os.close(fd)
        sha = receipt["sha"]
        if (not isinstance(sha, str) or not SHA_RE.fullmatch(sha)
                or not isinstance(receipt["host"], dict)
                or set(receipt["host"]) != {"parent_dev", "parent_ino", "mount_dev", "mount_ino"}
                or any(type(n) is not int or n <= 0 for n in receipt["host"].values())):
            raise MountRefused("VERIFY_RECEIPT_INVALID")
        return receipt
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise MountRefused("VERIFY_RECEIPT_INVALID") from exc


def mount_verify() -> None:
    """Only reads state; does not prepare, create, chmod or clean anything."""
    try:
        require_root()
    except Refused as exc:
        raise MountRefused("VERIFY_ROOT_REQUIRED") from exc
    receipt = trusted_receipt()
    try:
        uid, gid = checked_identity()
    except Refused as exc:
        raise MountRefused("VERIFY_IDENTITY") from exc
    if (uid, gid) != (receipt.get("uid"), receipt.get("gid")):
        raise MountRefused("VERIFY_IDENTITY")
    expected_release = PREFIX / ("release-" + receipt["sha"])
    if Path(__file__).resolve() != expected_release / "scripts/tag88_service.py":
        raise MountRefused("VERIFY_RECEIPT_INVALID")
    verified_host(root=Path("/proc/1/root"), table=Path("/proc/1/mountinfo"),
                  expected=receipt["host"])
    verified_private()


def git_checked_checkout(checkout: Path, sha: str) -> bytes:
    checked_abs(checkout)
    if not SHA_RE.fullmatch(sha) or not checkout.is_dir():
        raise Refused("invalid SHA or checkout")
    def git(*args: str) -> bytes:
        return subprocess.run(["git", "-C", str(checkout), *args], check=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30).stdout
    if git("rev-parse", "HEAD").decode().strip() != sha:
        raise Refused("checkout is not at the approved SHA")
    if git("status", "--porcelain", "--untracked-files=all").strip():
        raise Refused("checkout not clean")
    return git("archive", "--format=tar", sha)


def unpack_archive(archive: bytes, release: Path) -> dict[str, str]:
    files: dict[str, str] = {}
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as tar:
        members = tar.getmembers()
        for item in members:
            rel = PurePosixPath(item.name)
            if (not item.name or rel.is_absolute() or ".." in rel.parts
                    or not (item.isdir() or item.isfile())):
                raise Refused("unsafe archive member")
        release.mkdir(mode=0o755)
        for item in members:
            target = release.joinpath(*PurePosixPath(item.name).parts)
            if item.isdir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                payload = tar.extractfile(item).read()
                with target.open("xb") as fp:
                    fp.write(payload)
                os.chmod(target, 0o644)
                files[item.name] = hashlib.sha256(payload).hexdigest()
        for folder in sorted((p for p in release.rglob("*") if p.is_dir()),
                             key=lambda p: len(p.parts)):
            os.chmod(folder, 0o755)
    return files


def unit_render(template: str, release: Path, uid: int, gid: int) -> str:
    if not all(isinstance(v, int) and v > 0 for v in (uid, gid)):
        raise Refused("invalid uid/gid")
    return (template.replace("@TAG_UID@", str(uid))
                    .replace("@TAG_GID@", str(gid))
                    .replace("@TAG_RELEASE@", str(release)))


def run_admin(*argv: str) -> None:
    subprocess.run(argv, check=True, stdin=subprocess.DEVNULL, timeout=30)


def install(checkout: Path, sha: str) -> None:
    require_root()
    checked_abs(PREFIX)
    must_be_absent(PREFIX, UNIT_PATH, LEGACY_CLEAN_UNIT_PATH, HOST_PARENT, CONTROL)
    try:
        pwd.getpwnam(ACCOUNT)
    except KeyError:
        pass
    else:
        raise Refused("dedicated user already exists")
    try:
        grp.getgrnam(ACCOUNT)
    except KeyError:
        pass
    else:
        raise Refused("dedicated group already exists")
    archive = git_checked_checkout(checkout, sha)
    PREFIX.mkdir(mode=0o755)
    release = PREFIX / ("release-" + sha)
    files = unpack_archive(archive, release)
    useradd = shutil.which("useradd") or "/usr/sbin/useradd"
    run_admin(useradd, "--system", "--user-group", "--no-create-home",
              "--home-dir", "/nonexistent", "--shell", "/usr/sbin/nologin", ACCOUNT)
    uid, gid = checked_identity()
    HOST_PARENT.mkdir(mode=0o755)
    os.chmod(HOST_PARENT, 0o755)
    MOUNT.mkdir(mode=0o755)
    os.chmod(MOUNT, 0o755)
    host = verified_host(root=Path("/"), table=Path("/proc/self/mountinfo"))
    unit = unit_render((release / TEMPLATE).read_text(), release, uid, gid)
    if (any(marker in unit for marker in ("@TAG_UID@", "@TAG_GID@", "@TAG_RELEASE@"))
            or unit.count("TemporaryFileSystem=") != 1
            or unit.count("ExecStartPre=") != 1
            or "mount-verify" not in unit
            or "OnSuccess=" in unit or "OnFailure=" in unit or "postcleanup" in unit
            or "RuntimeDirectory=tag-qa88\n" in unit
            or "ReadWritePaths=" in unit):
        raise Refused("unit policy invalid")
    receipt = {
        "sha": sha, "uid": uid, "gid": gid, "files": files, "host": host,
        "unit_sha256": hashlib.sha256(unit.encode()).hexdigest(),
    }
    (PREFIX / "receipt.json").write_text(json.dumps(receipt, sort_keys=True) + "\n")
    os.chmod(PREFIX / "receipt.json", 0o644)
    fd = os.open(UNIT_PATH, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o644)
    with os.fdopen(fd, "w") as dest:
        dest.write(unit)
    run_admin("/usr/bin/systemctl", "daemon-reload")  # no enable/start
    print("INSTALLED_DISABLED", sha)


def _require_primary_inactive_disabled() -> None:
    """Reject any unavailable, ambiguous or non-terminal systemd state."""
    required = ("LoadState", "ActiveState", "MainPID", "ControlPID", "UnitFileState")
    try:
        result = subprocess.run(
            ["/usr/bin/systemctl", "show", UNIT_NAME,
             *(arg for prop in required for arg in ("-p", prop)), "--no-pager"],
            check=True, stdin=subprocess.DEVNULL, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=15,
        )
        rows = result.stdout.splitlines()
        if len(rows) != len(required):
            raise Refused("ambiguous systemd state")
        fields = {}
        for row in rows:
            if row.count("=") != 1:
                raise Refused("malformed systemd state")
            key, value = row.split("=", 1)
            if key not in required or key in fields or not value:
                raise Refused("unexpected systemd state")
            fields[key] = value
    except (OSError, ValueError, subprocess.SubprocessError, AttributeError) as exc:
        raise Refused("unable to attest systemd state") from exc
    if fields != {
        "LoadState": "loaded", "ActiveState": "inactive",
        "MainPID": "0", "ControlPID": "0", "UnitFileState": "disabled",
    }:
        raise Refused("service is not definitively inactive and disabled")


def remove() -> None:
    require_root()
    must_be_absent(CONTROL)
    if (not PREFIX.is_dir() or not UNIT_PATH.is_file()
            or not (PREFIX / "receipt.json").is_file()):
        raise Refused("receipt or primary unit missing")
    receipt = trusted_receipt()
    sha = receipt["sha"]
    release = PREFIX / ("release-" + sha)
    uid, gid = checked_identity()
    if (uid, gid) != (receipt.get("uid"), receipt.get("gid")):
        raise Refused("dedicated account mismatch")
    if hashlib.sha256(UNIT_PATH.read_bytes()).hexdigest() != receipt["unit_sha256"]:
        raise Refused("unit modified")
    expected = set()
    for name, digest in receipt["files"].items():
        rel = PurePosixPath(name)
        if (not name or rel.is_absolute() or ".." in rel.parts
                or not isinstance(digest, str)):
            raise Refused("unsafe release file entry")
        path = release.joinpath(*rel.parts)
        if (path.is_symlink() or not path.is_file()
                or hashlib.sha256(path.read_bytes()).hexdigest() != digest):
            raise Refused("release modified")
        expected.add(path)
    actual = {p for p in release.rglob("*") if p.is_file() or p.is_symlink()}
    if actual != expected:
        raise Refused("unexpected release content")
    _require_primary_inactive_disabled()
    jobs = subprocess.run(["/usr/bin/systemctl", "list-jobs", "--no-legend", "--no-pager"],
                          check=True, text=True, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, timeout=15)
    if UNIT_NAME in jobs.stdout:
        raise Refused("pending systemd job")
    verified_host(root=Path("/"), table=Path("/proc/self/mountinfo"),
                  expected=receipt["host"])
    # A different-namespace mount is out of scope; this operation is separately
    # authorized and must be performed only after a reviewed host preflight.
    UNIT_PATH.unlink()
    for path in sorted(expected, key=lambda p: len(p.parts), reverse=True):
        path.unlink()
    for folder in sorted((p for p in release.rglob("*") if p.is_dir()),
                         key=lambda p: len(p.parts), reverse=True):
        folder.rmdir()
    release.rmdir()
    (PREFIX / "receipt.json").unlink()
    PREFIX.rmdir()
    MOUNT.rmdir()
    HOST_PARENT.rmdir()
    userdel = shutil.which("userdel") or "/usr/sbin/userdel"
    run_admin(userdel, ACCOUNT)
    run_admin("/usr/bin/systemctl", "daemon-reload")
    print("UNINSTALLED")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    choices = parser.add_subparsers(dest="command", required=True)
    add = choices.add_parser("install")
    add.add_argument("--checkout", type=Path, required=True)
    add.add_argument("--sha", required=True)
    choices.add_parser("remove")
    choices.add_parser("mount-verify")
    args = parser.parse_args()
    try:
        if args.command == "install":
            install(args.checkout, args.sha)
        elif args.command == "remove":
            remove()
        else:
            mount_verify()
    except (Refused, OSError, subprocess.SubprocessError, ValueError,
            KeyError, TypeError, tarfile.TarError) as exc:
        if isinstance(exc, MountRefused):
            print("TAG_INSTALL_FAIL_CLOSED: Refused", exc.code, file=sys.stderr)
        else:
            print("TAG_INSTALL_FAIL_CLOSED:", type(exc).__name__, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
