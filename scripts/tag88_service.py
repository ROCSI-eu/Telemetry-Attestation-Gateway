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


def mount_prepare() -> None:
    require_root()
    must_be_absent(MARKER)
    # systemd 259 creates the host destination for TemporaryFileSystem before
    # ExecStartPre. Unit assertions reject any pre-existing/stale host path
    # before that setup. Accept ONLY its fresh, empty root-owned 0755 directory.
    try:
        directory_fd = os.open(MOUNT, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    except OSError as exc:
        raise Refused("systemd mountpoint missing or unsafe") from exc
    try:
        entry = os.fstat(directory_fd)
        if (not stat.S_ISDIR(entry.st_mode)
                or entry.st_uid != ROOT_UID or entry.st_gid != ROOT_GID
                or stat.S_IMODE(entry.st_mode) != 0o755
                or is_mount(MOUNT) or list(MOUNT.iterdir())):
            raise Refused("systemd mountpoint is not fresh and empty")
        os.fchmod(directory_fd, 0o700)
    finally:
        os.close(directory_fd)
    fd = os.open(MARKER, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
    try:
        os.write(fd, LABEL.encode("ascii"))
    finally:
        os.close(fd)


def mount_clean() -> None:
    require_root()
    if not os.path.lexists(MARKER) and not os.path.lexists(MOUNT):
        return  # failed start before creation
    if not MARKER.is_file() or MARKER.is_symlink() or not MOUNT.is_dir() or MOUNT.is_symlink():
        raise Refused("mountpoint ownership is ambiguous")
    token = MARKER.lstat()
    directory = MOUNT.lstat()
    if (token.st_uid != ROOT_UID or token.st_gid != ROOT_GID
            or stat.S_IMODE(token.st_mode) != 0o600
            or directory.st_uid != ROOT_UID or directory.st_gid != ROOT_GID
            or stat.S_IMODE(directory.st_mode) != 0o700
            or MARKER.read_text() != LABEL or is_mount(MOUNT) or list(MOUNT.iterdir())):
        raise Refused("mountpoint is busy, altered, or not empty")
    os.rmdir(MOUNT)
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
        print("TAG_INSTALL_FAIL_CLOSED:", type(exc).__name__, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
