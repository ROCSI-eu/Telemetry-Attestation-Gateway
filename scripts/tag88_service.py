#!/usr/bin/env python3
"""TAG #88 non-Production systemd package and private mountpoint lifecycle.

No action is implicit. install/remove require an explicitly authorized local
root session; this script must never be invoked during Draft review.
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
TEMPLATE = Path("experiments/web-console-v0/tag-qa88-persistent.service")
MOUNT = Path("/run/tag-qa88")
MARKER = Path("/run/tag-qa88-mountpoint-owned")
CONTROL = Path("/run/tag-qa88-control")
LABEL = "TAG-88-MOUNTPOINT-V1\n"
ROOT_UID = 0
ROOT_GID = 0
SHA_RE = re.compile(r"[a-f0-9]{40}\Z")


class Refused(RuntimeError):
    pass


# Fixed public labels only: never print exception messages or local paths.
MOUNT_CODES = frozenset({
    "MOUNT_ROOT_REQUIRED", "MOUNT_MARKER_PRESENT", "MOUNT_CREATE_FAILED",
    "MOUNT_OPEN_FAILED", "MOUNT_NOT_DIRECTORY", "MOUNT_OWNER_MISMATCH",
    "MOUNT_MODE_MISMATCH", "MOUNT_MOUNTINFO_FAILED", "MOUNT_ALREADY_MOUNTED",
    "MOUNT_NOT_EMPTY", "MOUNT_PATH_REPLACED", "MOUNT_CHMOD_FAILED",
    "MOUNT_MARKER_CREATE_FAILED", "MOUNT_MARKER_WRITE_FAILED",
    "MOUNT_CLEAN_ROOT_REQUIRED", "MOUNT_CLEAN_UNOWNED",
    "MOUNT_CLEAN_CHANGED", "MOUNT_HOST_LOOKUP_FAILED",
    "MOUNT_HOST_MOUNTED", "MOUNT_PRIVATE_INVALID",
    "MOUNT_PRIVATE_QUOTA", "MOUNT_PRIVATE_FLAGS",
    "MOUNT_PRIVATE_IDENTITY", "MOUNT_CLEAN_HOST_INVALID",
})


class MountRefused(Refused):
    def __init__(self, code: str) -> None:
        if code not in MOUNT_CODES:
            raise ValueError("invalid diagnostic code")
        self.code = code
        super().__init__(code)


def require_root() -> None:
    if os.geteuid() != 0:
        raise Refused("local root authorization required")


def checked_identity() -> tuple[int, int]:
    try:
        user, group = pwd.getpwnam(ACCOUNT), grp.getgrnam(ACCOUNT)
    except KeyError as exc:
        raise Refused("dedicated account missing") from exc
    if user.pw_uid == 0 or group.gr_gid == 0 or user.pw_gid != group.gr_gid:
        raise Refused("unexpected account identity")
    return user.pw_uid, group.gr_gid


def checked_abs(path: Path) -> Path:
    if not path.is_absolute() or path != Path(os.path.realpath(path)):
        raise Refused("path must be absolute and free of symlinks")
    return path


def must_be_absent(*paths: Path) -> None:
    if any(os.path.lexists(p) for p in paths):
        raise Refused("TAG path already exists; no overwrite or stale reuse")


def is_mount(path: Path) -> bool:
    return any(row.split()[4] == str(path) for row in Path("/proc/self/mountinfo").read_text().splitlines())


def _host_view(path: Path) -> Path:
    """Resolve the host's view through PID 1, never through this hook's mount namespace."""
    return Path("/proc/1/root") / path.relative_to("/")


def _mount_row(path: Path, table: Path) -> tuple[str, set[str]] | None:
    """Return (fstype, mount flags) for exactly one mount, or None.

    Fail closed if mount metadata cannot be inspected. The target paths are
    fixed by the installed unit, without whitespace or mountinfo escapes.
    """
    try:
        lines = table.read_text().splitlines()
        matches = [line for line in lines if line.split()[4] == str(path)]
        if len(matches) > 1:
            raise MountRefused("MOUNT_MOUNTINFO_FAILED")
        if not matches:
            return None
        fields = matches[0].split()
        separator = fields.index("-")
        return fields[separator + 1], set(fields[5].split(","))
    except (OSError, IndexError, ValueError) as exc:
        raise MountRefused("MOUNT_MOUNTINFO_FAILED") from exc


def _open_checked(path: Path, uid: int, gid: int, mode: int,
                  *, code: str) -> tuple[int, os.stat_result]:
    try:
        fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    except OSError as exc:
        raise MountRefused(code) from exc
    try:
        entry = os.fstat(fd)
        if not stat.S_ISDIR(entry.st_mode):
            raise MountRefused(code)
        if (entry.st_uid != uid or entry.st_gid != gid
                or stat.S_IMODE(entry.st_mode) != mode):
            raise MountRefused(code)
        if os.listdir(fd):
            raise MountRefused("MOUNT_NOT_EMPTY")
        current = path.lstat()
        if ((current.st_dev, current.st_ino) != (entry.st_dev, entry.st_ino)
                or not stat.S_ISDIR(current.st_mode)):
            raise MountRefused(code)
        return fd, entry
    except BaseException:
        os.close(fd)
        raise


def _host_directory(mode: int) -> tuple[int, os.stat_result]:
    host = _host_view(MOUNT)
    # PID 1 sees the host mount namespace, not systemd's per-command tmpfs.
    if _mount_row(MOUNT, Path("/proc/1/mountinfo")) is not None:
        raise MountRefused("MOUNT_HOST_MOUNTED")
    fd, entry = _open_checked(host, ROOT_UID, ROOT_GID, mode,
                              code="MOUNT_HOST_LOOKUP_FAILED")
    try:
        if entry.st_dev != _host_view(MOUNT.parent).stat().st_dev:
            raise MountRefused("MOUNT_HOST_LOOKUP_FAILED")
    except BaseException:
        os.close(fd)
        raise
    return fd, entry


def _separate_device(path: Path, entry: os.stat_result) -> bool:
    return entry.st_dev != path.parent.stat().st_dev


def _private_directory() -> tuple[int, os.stat_result]:
    facts = _mount_row(MOUNT, Path("/proc/self/mountinfo"))
    if facts is None or facts[0] != "tmpfs":
        raise MountRefused("MOUNT_PRIVATE_INVALID")
    if not {"nodev", "nosuid", "noexec"}.issubset(facts[1]):
        raise MountRefused("MOUNT_PRIVATE_FLAGS")
    try:
        uid, gid = checked_identity()
    except Refused as exc:
        raise MountRefused("MOUNT_PRIVATE_IDENTITY") from exc
    fd, entry = _open_checked(MOUNT, uid, gid, 0o700, code="MOUNT_PRIVATE_IDENTITY")
    try:
        fs = os.fstatvfs(fd)
        if not (0 < fs.f_blocks * fs.f_frsize <= 8 * 1024 * 1024
                and 0 < fs.f_files <= 128):
            raise MountRefused("MOUNT_PRIVATE_QUOTA")
        if not _separate_device(MOUNT, entry):
            raise MountRefused("MOUNT_PRIVATE_INVALID")
    except BaseException:
        os.close(fd)
        raise
    return fd, entry


def mount_prepare() -> None:
    try:
        require_root()
    except Refused as exc:
        raise MountRefused("MOUNT_ROOT_REQUIRED") from exc
    if os.path.lexists(MARKER):
        raise MountRefused("MOUNT_MARKER_PRESENT")

    own_mount = _mount_row(MOUNT, Path("/proc/self/mountinfo"))
    if own_mount is not None:
        # systemd's private tmpfs is already mounted for the + hook. Never
        # chmod/remove that mount, and never mistake its uid/gid for host ownership.
        private_fd, _ = _private_directory()
        try:
            host_fd, _ = _host_directory(0o755)
            os.close(host_fd)
        finally:
            os.close(private_fd)
    else:
        # Host-only compatibility path. The [Unit] assertions forbid adopting
        # pre-existing residue before systemd prepares the unit.
        existed = os.path.lexists(MOUNT)
        if not existed:
            try:
                os.mkdir(MOUNT, 0o700)
            except OSError as exc:
                raise MountRefused("MOUNT_CREATE_FAILED") from exc
        try:
            fd, entry = _open_checked(MOUNT, ROOT_UID, ROOT_GID,
                                      0o755 if existed else 0o700,
                                      code="MOUNT_HOST_LOOKUP_FAILED")
            try:
                host_fd, host_entry = _host_directory(0o755 if existed else 0o700)
                try:
                    if (host_entry.st_dev, host_entry.st_ino) != (entry.st_dev, entry.st_ino):
                        raise MountRefused("MOUNT_HOST_LOOKUP_FAILED")
                finally:
                    os.close(host_fd)
                os.fchmod(fd, 0o700)
            finally:
                os.close(fd)
        except MountRefused:
            raise
        except OSError as exc:
            raise MountRefused("MOUNT_CHMOD_FAILED") from exc

    try:
        fd = os.open(MARKER, os.O_CREAT | os.O_EXCL | os.O_WRONLY
                     | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    except OSError as exc:
        raise MountRefused("MOUNT_MARKER_CREATE_FAILED") from exc
    try:
        try:
            marker_stat = os.fstat(fd)
            if (marker_stat.st_uid != ROOT_UID or marker_stat.st_gid != ROOT_GID
                    or stat.S_IMODE(marker_stat.st_mode) != 0o600):
                raise MountRefused("MOUNT_MARKER_CREATE_FAILED")
            if os.write(fd, LABEL.encode("ascii")) != len(LABEL.encode("ascii")):
                raise MountRefused("MOUNT_MARKER_WRITE_FAILED")
        except OSError as exc:
            raise MountRefused("MOUNT_MARKER_WRITE_FAILED") from exc
    finally:
        os.close(fd)


def mount_clean() -> None:
    try:
        require_root()
    except Refused as exc:
        raise MountRefused("MOUNT_CLEAN_ROOT_REQUIRED") from exc
    if not os.path.lexists(MARKER) and not os.path.lexists(MOUNT):
        return
    if (not MARKER.is_file() or MARKER.is_symlink()
            or MARKER.lstat().st_uid != ROOT_UID
            or MARKER.lstat().st_gid != ROOT_GID
            or stat.S_IMODE(MARKER.lstat().st_mode) != 0o600
            or MARKER.read_text() != LABEL):
        raise MountRefused("MOUNT_CLEAN_UNOWNED")

    own_mount = _mount_row(MOUNT, Path("/proc/self/mountinfo"))
    if own_mount is not None:
        # A fresh namespace may be created for ExecStopPost=+. Validate it,
        # then remove ONLY PID 1's host-side empty directory, not the tmpfs.
        private_fd, _ = _private_directory()
        try:
            host_fd, _ = _host_directory(0o755)
            os.close(host_fd)
        except BaseException:
            os.close(private_fd)
            raise
        os.close(private_fd)
    else:
        host_fd, _ = _host_directory(0o700)
        os.close(host_fd)

    # The parent fd anchors removal to the host's /run path. Refuse symlinks
    # and replacement rather than blindly rmdir a path in a private namespace.
    parent = _host_view(MOUNT.parent)
    try:
        parent_fd = os.open(parent, os.O_RDONLY | os.O_DIRECTORY
                            | os.O_NOFOLLOW | os.O_CLOEXEC)
    except OSError as exc:
        raise MountRefused("MOUNT_CLEAN_HOST_INVALID") from exc
    try:
        host_fd, entry = _open_checked(_host_view(MOUNT), ROOT_UID, ROOT_GID,
                                       0o755 if own_mount is not None else 0o700,
                                       code="MOUNT_CLEAN_HOST_INVALID")
        try:
            target = os.stat(MOUNT.name, dir_fd=parent_fd, follow_symlinks=False)
            if (target.st_dev, target.st_ino) != (entry.st_dev, entry.st_ino):
                raise MountRefused("MOUNT_CLEAN_HOST_INVALID")
            os.rmdir(MOUNT.name, dir_fd=parent_fd)
        finally:
            os.close(host_fd)
    except OSError as exc:
        raise MountRefused("MOUNT_CLEAN_HOST_INVALID") from exc
    finally:
        os.close(parent_fd)
    MARKER.unlink()

def git_checked_checkout(checkout: Path, sha: str) -> bytes:
    checked_abs(checkout)
    if not SHA_RE.fullmatch(sha) or not checkout.is_dir():
        raise Refused("invalid SHA or checkout")
    def git(*args: str) -> bytes:
        p = subprocess.run(["git", "-C", str(checkout), *args], check=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
        return p.stdout
    if git("rev-parse", "HEAD").decode().strip() != sha:
        raise Refused("checkout is not at the exact approved SHA")
    if git("status", "--porcelain", "--untracked-files=all").strip():
        raise Refused("checkout must be clean, including untracked files")
    return git("archive", "--format=tar", sha)


def unpack_archive(archive: bytes, release: Path) -> dict[str, str]:
    """Extract trusted, exact-SHA Git tree with no links or special entries."""
    files: dict[str, str] = {}
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as tar:
        members = tar.getmembers()
        for item in members:
            rel = PurePosixPath(item.name)
            if (not item.name or rel.is_absolute() or ".." in rel.parts
                    or not (item.isdir() or item.isfile())):
                raise Refused("unsafe archive entry")
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
        for directory in sorted((p for p in release.rglob("*") if p.is_dir()), key=lambda p: len(p.parts)):
            os.chmod(directory, 0o755)
    return files


def unit_render(template: str, release: Path, uid: int, gid: int) -> str:
    if not all(isinstance(v, int) and v > 0 for v in (uid, gid)):
        raise Refused("invalid identity")
    return (template.replace("@TAG_UID@", str(uid))
                    .replace("@TAG_GID@", str(gid))
                    .replace("@TAG_RELEASE@", str(release)))


def run_admin(*argv: str) -> None:
    subprocess.run(argv, check=True, stdin=subprocess.DEVNULL, timeout=30)


def install(checkout: Path, sha: str) -> None:
    require_root()
    checked_abs(PREFIX)
    must_be_absent(PREFIX, UNIT_PATH, MOUNT, MARKER, CONTROL)
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
    archive = git_checked_checkout(checkout, sha)  # before any write
    PREFIX.mkdir(mode=0o755)
    release = PREFIX / ("release-" + sha)
    files = unpack_archive(archive, release)
    useradd = shutil.which("useradd") or "/usr/sbin/useradd"
    run_admin(useradd, "--system", "--user-group", "--no-create-home",
              "--home-dir", "/nonexistent", "--shell", "/usr/sbin/nologin", ACCOUNT)
    uid, gid = checked_identity()
    unit = unit_render((release / TEMPLATE).read_text(), release, uid, gid)
    if any(marker in unit for marker in ("@TAG_UID@", "@TAG_GID@", "@TAG_RELEASE@")):
        raise Refused("unresolved unit placeholder")
    receipt = {"sha": sha, "uid": uid, "gid": gid, "files": files,
               "unit_sha256": hashlib.sha256(unit.encode()).hexdigest()}
    (PREFIX / "receipt.json").write_text(json.dumps(receipt, sort_keys=True) + "\n")
    os.chmod(PREFIX / "receipt.json", 0o644)
    fd = os.open(UNIT_PATH, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o644)
    with os.fdopen(fd, "w") as dest:
        dest.write(unit)
    run_admin("/usr/bin/systemctl", "daemon-reload")  # NOT enable/start
    print("INSTALLED_DISABLED", sha)


def remove() -> None:
    require_root()
    must_be_absent(MOUNT, MARKER, CONTROL)
    if not PREFIX.is_dir() or not (PREFIX / "receipt.json").is_file() or not UNIT_PATH.is_file():
        raise Refused("installation receipt/unit missing; no partial removal")
    receipt = json.loads((PREFIX / "receipt.json").read_text())
    sha = receipt.get("sha")
    if not isinstance(sha, str) or not SHA_RE.fullmatch(sha):
        raise Refused("receipt SHA invalid")
    release = PREFIX / ("release-" + sha)
    uid, gid = checked_identity()
    if (uid, gid) != (receipt.get("uid"), receipt.get("gid")):
        raise Refused("user identity changed")
    if hashlib.sha256(UNIT_PATH.read_bytes()).hexdigest() != receipt["unit_sha256"]:
        raise Refused("unit was modified")
    for name, digest in receipt["files"].items():
        rel = PurePosixPath(name)
        if not name or rel.is_absolute() or ".." in rel.parts or not isinstance(digest, str):
            raise Refused("unsafe receipt entry")
        path = release.joinpath(*rel.parts)
        if path.is_symlink() or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise Refused("release files modified")
    # Systemd activation is managed only in the separately approved lifecycle.
    state = subprocess.run(["/usr/bin/systemctl", "is-active", "--quiet",
                            "tag-qa88-persistent.service"], check=False, timeout=15)
    enabled = subprocess.run(["/usr/bin/systemctl", "is-enabled", "--quiet",
                              "tag-qa88-persistent.service"], check=False, timeout=15)
    if state.returncode == 0 or enabled.returncode == 0:
        raise Refused("service is active or enabled; stop/disable via separate authorization")
    # Verify exact installed scope before removal.
    expected = {release / name for name in receipt["files"]}
    actual = {p for p in release.rglob("*") if p.is_file() or p.is_symlink()}
    if actual != expected:
        raise Refused("unexpected files in release")
    UNIT_PATH.unlink()
    for path in sorted(expected, key=lambda p: len(p.parts), reverse=True):
        path.unlink()
    for path in sorted((p for p in release.rglob("*") if p.is_dir()),
                       key=lambda p: len(p.parts), reverse=True):
        path.rmdir()
    release.rmdir()
    (PREFIX / "receipt.json").unlink()
    PREFIX.rmdir()
    userdel = shutil.which("userdel") or "/usr/sbin/userdel"
    run_admin(userdel, ACCOUNT)
    run_admin("/usr/bin/systemctl", "daemon-reload")
    print("UNINSTALLED")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    choices = ap.add_subparsers(dest="command", required=True)
    ins = choices.add_parser("install")
    ins.add_argument("--checkout", type=Path, required=True)
    ins.add_argument("--sha", required=True)
    choices.add_parser("remove")
    choices.add_parser("mount-prepare")
    choices.add_parser("mount-clean")
    args = ap.parse_args()
    try:
        if args.command == "install":
            install(args.checkout, args.sha)
        elif args.command == "remove":
            remove()
        elif args.command == "mount-prepare":
            mount_prepare()
        elif args.command == "mount-clean":
            mount_clean()
    except (Refused, OSError, subprocess.SubprocessError, ValueError, KeyError, tarfile.TarError) as exc:
        # Mount diagnostics are enumerated, non-secret labels. Other errors
        # retain their original type-only output; no paths or tokens are shown.
        if isinstance(exc, MountRefused):
            print("TAG_INSTALL_FAIL_CLOSED: Refused", exc.code, file=sys.stderr)
        else:
            print("TAG_INSTALL_FAIL_CLOSED:", type(exc).__name__, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
