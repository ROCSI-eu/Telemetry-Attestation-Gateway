#!/usr/bin/env python3
"""Build or refresh one private, static, synthetic console session offline.

EXPERIMENTAL
SYNTHETIC_ONLY
A0_SYNTHETIC
NOT VALIDATION OR PRODUCTION AUTHORIZATION

No server or prover is started. Proof-package replay remains verified; an optional
SITL record is explicitly unauthenticated even when its schema is valid.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import stat
import sys
import tempfile

import export_authentic as exporter
import sitl_record

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SOURCE_INDEX = HERE / "index.html"
SOURCE_MOCK = HERE.parent / "integrated-cli-v0" / "evidence-results.json"
REPLAY = "authentic-evidence.json"
SITL = sitl_record.NAME
FILES = {
    "web-console-v0": {"index.html", REPLAY},
    "integrated-cli-v0": {"evidence-results.json"},
}


class SessionRejected(Exception):
    """No user-controlled paths or package data in public errors."""


def _contained(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def _private_directory(path: Path) -> None:
    meta = path.lstat()
    if (not stat.S_ISDIR(meta.st_mode) or meta.st_uid != os.getuid()
            or stat.S_IMODE(meta.st_mode) != 0o700):
        raise SessionRejected


def _private_file(path: Path) -> None:
    meta = path.lstat()
    if (not stat.S_ISREG(meta.st_mode) or meta.st_uid != os.getuid()
            or stat.S_IMODE(meta.st_mode) != 0o600):
        raise SessionRejected


def _prior_replay_safe(raw: bytes) -> bool:
    """Reject altered, expanded or unknown previous browser-visible records."""
    if len(raw) > 4096:
        return False
    try:
        observed = json.loads(raw)
        template = json.loads((HERE / REPLAY).read_bytes())
        if not isinstance(observed, dict) or set(observed) != exporter.FIELDS:
            return False
        if observed["cryptographic"] == "INVALID":
            template["cryptographic"] = "INVALID"
            template["cryptographic_reason"] = "PROOF_REJECTED"
        return observed == template
    except (ValueError, KeyError, TypeError, OSError):
        return False


def _existing_session_safe(session: Path) -> None:
    _private_directory(session)
    if {item.name for item in session.iterdir()} != set(FILES):
        raise SessionRejected
    for folder, allowed in FILES.items():
        subdir = session / folder
        _private_directory(subdir)
        found = {item.name for item in subdir.iterdir()}
        choices = (allowed, allowed | {SITL}) if folder == "web-console-v0" else (allowed,)
        if found not in choices:
            raise SessionRejected
    for rel, reference in (
        ("web-console-v0/index.html", SOURCE_INDEX),
        ("integrated-cli-v0/evidence-results.json", SOURCE_MOCK),
    ):
        target = session / rel
        _private_file(target)
        if target.read_bytes() != reference.read_bytes():
            raise SessionRejected
    replay = session / "web-console-v0" / REPLAY
    _private_file(replay)
    if not _prior_replay_safe(replay.read_bytes()):
        raise SessionRejected
    recorded = session / "web-console-v0" / SITL
    if recorded.exists() or recorded.is_symlink():
        _private_file(recorded)
        try:
            sitl_record.parse_record(recorded.read_bytes())
        except sitl_record.RecordRejected as exc:
            raise SessionRejected from exc


def _copy_private(source: Path, target: Path) -> None:
    target.write_bytes(source.read_bytes())
    target.chmod(0o600)


def refresh(package: Path | None, session: Path, *,
            sitl_record_dir: Path | None = None) -> None:
    """Two distinct sources: verified package OR recorded SITL self-report."""
    if (package is None) == (sitl_record_dir is None):
        raise SessionRejected
    source = package if package is not None else sitl_record_dir
    if not session.is_absolute() or not source.is_absolute():
        raise SessionRejected
    # Reject symlinks even in parent path components.
    if (Path(os.path.abspath(session)) != Path(os.path.realpath(session))
            or Path(os.path.abspath(source)) != Path(os.path.realpath(source))):
        raise SessionRejected
    session = session.resolve()
    source = source.resolve()
    if package is not None:
        package = source
    else:
        sitl_record_dir = source
    parent = session.parent
    if (not parent.is_dir() or session == parent or session == Path("/")
            or _contained(session, REPO) or _contained(REPO, session)
            or _contained(session, source) or _contained(source, session)
            or (sitl_record_dir is not None
                and (_contained(source, REPO) or _contained(REPO, source)))):
        raise SessionRejected
    if session.exists():
        if sitl_record_dir is not None:
            raise SessionRejected  # One SITL record per private session; no refresh/replay.
        _existing_session_safe(session)
        if (session / "web-console-v0" / SITL).exists():
            raise SessionRejected  # Never refresh an older SITL claim in place.

    # All staged files are minimized or static; private temporary directory
    # stays on the same filesystem as the final atomic rename/replace.
    with tempfile.TemporaryDirectory(prefix=".tag-console-session-", dir=parent) as temporary:
        stage = Path(temporary)
        view = stage / "web-console-v0"
        mock = stage / "integrated-cli-v0"
        view.mkdir(mode=0o700)
        mock.mkdir(mode=0o700)
        if package is not None:
            exporter.export(package, view / REPLAY)
        else:
            # Existing historical independent verifier replay stays a distinct panel.
            _copy_private(HERE / REPLAY, view / REPLAY)
            recorded = view / SITL
            recorded.write_bytes(sitl_record.read_private(sitl_record_dir))
            recorded.chmod(0o600)
        _copy_private(SOURCE_INDEX, view / "index.html")
        _copy_private(SOURCE_MOCK, mock / "evidence-results.json")
        if session.exists():
            # Validate again immediately before replacing the one managed record.
            _existing_session_safe(session)
            # Bind the commit to the verified directory inode. Reopening the
            # destination path inside os.replace would follow a swapped symlink.
            destination_dir = session / "web-console-v0"
            before = destination_dir.lstat()
            directory_fd = os.open(
                destination_dir, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
            )
            try:
                current = os.fstat(directory_fd)
                if ((current.st_dev, current.st_ino) != (before.st_dev, before.st_ino)
                        or current.st_uid != os.getuid()
                        or stat.S_IMODE(current.st_mode) != 0o700
                        or not stat.S_ISDIR(current.st_mode)):
                    raise SessionRejected
                os.replace(view / REPLAY, REPLAY, dst_dir_fd=directory_fd)
            finally:
                os.close(directory_fd)
        else:
            # mkdir is exclusive: never replace a concurrently created session
            # (plain rename silently overwrites an existing empty directory).
            # The directory descriptor prevents redirects after this point.
            try:
                session.mkdir(mode=0o700)
            except FileExistsError as exc:
                raise SessionRejected from exc
            directory_fd = os.open(
                session, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
            )
            try:
                current = os.fstat(directory_fd)
                if (current.st_uid != os.getuid()
                        or stat.S_IMODE(current.st_mode) != 0o700
                        or not stat.S_ISDIR(current.st_mode)):
                    raise SessionRejected
                os.rename(view, "web-console-v0", dst_dir_fd=directory_fd)
                os.rename(mock, "integrated-cli-v0", dst_dir_fd=directory_fd)
            finally:
                os.close(directory_fd)
            # Interrupted creation leaves a private, incomplete session that
            # fails strict validation on retry; no arbitrary directory is removed.


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    inputs = parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument("--package-dir", type=Path,
                        help="existing synthetic proof package (independently reverified)")
    inputs.add_argument("--sitl-record-dir", type=Path,
                        help="private locally recorded SITL outcome (unauthenticated replay)")
    parser.add_argument("--session-dir", type=Path, required=True,
                        help="absolute private path outside repository and proof package")
    args = parser.parse_args()
    try:
        refresh(args.package_dir, args.session_dir, sitl_record_dir=args.sitl_record_dir)
    except (SessionRejected, exporter.ExportRejected, sitl_record.RecordRejected, OSError, ValueError):
        print("EXPERIMENTAL SYNTHETIC_ONLY A0_SYNTHETIC NOT VALIDATION OR PRODUCTION AUTHORIZATION: local session not updated", file=sys.stderr)
        return 2
    if args.sitl_record_dir is None:
        print("EXPERIMENTAL SYNTHETIC_ONLY A0_SYNTHETIC NOT VALIDATION OR PRODUCTION AUTHORIZATION: private local session refreshed; reload browser page to view precomputed offline result")
    else:
        print("EXPERIMENTAL SYNTHETIC_ONLY A0_SYNTHETIC NOT VALIDATION OR PRODUCTION AUTHORIZATION: private SITL self-report recorded; JSON NOT authenticated or verified by browser")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
