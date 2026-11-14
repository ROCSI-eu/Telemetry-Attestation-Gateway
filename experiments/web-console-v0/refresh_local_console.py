#!/usr/bin/env python3
"""Build or refresh one private, static, synthetic console session offline.

EXPERIMENTAL
SYNTHETIC_ONLY
A0_SYNTHETIC
NOT VALIDATION OR PRODUCTION AUTHORIZATION

No server or prover is started. Only minimized verified results reach the view.
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

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SOURCE_INDEX = HERE / "index.html"
SOURCE_MOCK = HERE.parent / "integrated-cli-v0" / "evidence-results.json"
REPLAY = "authentic-evidence.json"
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
        if {item.name for item in subdir.iterdir()} != allowed:
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


def _copy_private(source: Path, target: Path) -> None:
    target.write_bytes(source.read_bytes())
    target.chmod(0o600)


def refresh(package: Path, session: Path) -> None:
    """Run genuine verification first; never modify a session on verifier failure."""
    if not session.is_absolute() or not package.is_absolute():
        raise SessionRejected
    # Reject symlinks even in parent path components.
    if (Path(os.path.abspath(session)) != Path(os.path.realpath(session))
            or Path(os.path.abspath(package)) != Path(os.path.realpath(package))):
        raise SessionRejected
    session = session.resolve()
    package = package.resolve()
    parent = session.parent
    if (not parent.is_dir() or session == parent or session == Path("/")
            or _contained(session, REPO) or _contained(REPO, session)
            or _contained(session, package) or _contained(package, session)):
        raise SessionRejected
    if session.exists():
        _existing_session_safe(session)

    # All staged files are minimized or static; private temporary directory
    # stays on the same filesystem as the final atomic rename/replace.
    with tempfile.TemporaryDirectory(prefix=".tag-console-session-", dir=parent) as temporary:
        stage = Path(temporary)
        view = stage / "web-console-v0"
        mock = stage / "integrated-cli-v0"
        view.mkdir(mode=0o700)
        mock.mkdir(mode=0o700)
        exporter.export(package, view / REPLAY)
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
            # Create the complete viewer at once, without touching the Git tree.
            os.rename(stage, session)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-dir", type=Path, required=True,
                        help="absolute private path to an existing synthetic proof package")
    parser.add_argument("--session-dir", type=Path, required=True,
                        help="absolute private path outside repository and proof package")
    args = parser.parse_args()
    try:
        refresh(args.package_dir, args.session_dir)
    except (SessionRejected, exporter.ExportRejected, OSError, ValueError):
        print("EXPERIMENTAL SYNTHETIC_ONLY A0_SYNTHETIC NOT VALIDATION OR PRODUCTION AUTHORIZATION: local session not updated", file=sys.stderr)
        return 2
    print("EXPERIMENTAL SYNTHETIC_ONLY A0_SYNTHETIC NOT VALIDATION OR PRODUCTION AUTHORIZATION: private local session refreshed; reload browser page to view precomputed offline result")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
