#!/usr/bin/env python3
"""Private minimized SITL outcome: unsigned local self-report, never a proof."""
from __future__ import annotations

import json
import os
from pathlib import Path
import stat
import tempfile

LABELS = ["EXPERIMENTAL", "SYNTHETIC_ONLY", "A0_SYNTHETIC",
          "NOT VALIDATION OR PRODUCTION AUTHORIZATION"]
SCHEMA = "TAG_RECORDED_SYNTHETIC_SITL_V1_EXPERIMENTAL"
NAME = "sitl-record.json"
RUN_KEYS = {"labels", "source", "observations", "normalization", "source_trust",
            "proof", "integrated_crypto", "separate_process_crypto", "publication",
            "relying_party_decision", "command_path", "status", "cleanup"}


class RecordRejected(ValueError):
    """Private paths and detailed input never enter public errors."""


def require(ok: bool) -> None:
    if not ok:
        raise RecordRejected


def expected(trust: str) -> dict:
    return {
        "schema_version": SCHEMA, "labels": LABELS, "evidence_kind": "SITL_E2E_RECORDED_SELF_REPORT",
        "source": "Copter_4.7.1_synthetic_SITL", "observations": 2,
        "normalization": "NORMALIZED", "source_trust": trust,
        "claim": "SATISFIED", "public_maximum_cm_s": 600,
        "proof_generation": "GENERATED", "integrated_crypto": "VALID",
        "separate_process_crypto": "VALID", "assurance": "A0_SYNTHETIC",
        "policy": "NOT_EVALUATED", "freshness": "NOT_EVALUATED",
        "revocation": "NOT_EVALUATED", "replay": "NOT_EVALUATED",
        "publication": "DISABLED", "relying_party_decision": "NOT_MADE",
        "command_path": "NONE", "cleanup": "PASS",
        "record_authenticated": False, "browser_verified": False,
        "proof_validity_is_telemetry_truth": False,
    }


def minimize_completed(run: dict) -> dict:
    """Called only after separate-process verification AND complete cleanup."""
    require(type(run) is dict and set(run) == RUN_KEYS)
    require(run["labels"] == LABELS)
    require(run["source"] == "real_Copter_4.7.1_synthetic_SITL")
    require(type(run["observations"]) is int and run["observations"] == 2)
    trust = run["source_trust"]
    require(type(trust) is str and trust in ("UNSIGNED", "UNKNOWN"))
    for key, value in (
        ("normalization", "NORMALIZED"), ("proof", "GENERATED"),
        ("integrated_crypto", "VALID"), ("separate_process_crypto", "VALID"),
        ("publication", "DISABLED"), ("relying_party_decision", "NOT_MADE"),
        ("command_path", "NONE"), ("status", "PASS"), ("cleanup", "PASS"),
    ):
        require(type(run[key]) is str and run[key] == value)
    return expected(trust)


def parse_record(raw: bytes) -> dict:
    require(len(raw) <= 4096)
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result)
            result[key] = value
        return result
    try:
        record = json.loads(raw, object_pairs_hook=unique)
    except (ValueError, UnicodeDecodeError, TypeError) as exc:
        raise RecordRejected from exc
    require(type(record) is dict and type(record.get("source_trust")) is str
            and record["source_trust"] in ("UNSIGNED", "UNKNOWN"))
    require(record == expected(record["source_trust"]))
    return record


def private_directory(directory: Path) -> None:
    require(directory.is_absolute())
    require(Path(os.path.abspath(directory)) == Path(os.path.realpath(directory)))
    meta = directory.lstat()
    require(stat.S_ISDIR(meta.st_mode) and meta.st_uid == os.getuid()
            and stat.S_IMODE(meta.st_mode) == 0o700)


def read_private(directory: Path) -> bytes:
    private_directory(directory)
    require({p.name for p in directory.iterdir()} == {NAME})
    path = directory / NAME
    before = path.lstat()
    require(stat.S_ISREG(before.st_mode) and before.st_uid == os.getuid()
            and stat.S_IMODE(before.st_mode) == 0o600 and before.st_nlink == 1
            and before.st_size <= 4096)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        current = os.fstat(fd)
        require((current.st_dev, current.st_ino) == (before.st_dev, before.st_ino)
                and current.st_uid == os.getuid() and stat.S_ISREG(current.st_mode)
                and stat.S_IMODE(current.st_mode) == 0o600
                and current.st_nlink == 1 and current.st_size <= 4096)
        raw = os.read(fd, 4097)
        parse_record(raw)
        return raw
    finally:
        os.close(fd)


def write_completed(run: dict, directory: Path) -> None:
    """Exclusive, 0600 publication only after the script has returned PASS."""
    record = minimize_completed(run)
    private_directory(directory)
    require(not any(directory.iterdir()))
    raw = (json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n").encode()
    require(len(raw) <= 4096)
    directory_fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    temporary = None
    try:
        fd, temporary = tempfile.mkstemp(prefix=".tag-sitl-record-", dir=directory)
        with os.fdopen(fd, "wb") as output:
            output.write(raw)
            output.flush()
            os.fsync(output.fileno())
        os.chmod(temporary, 0o600)
        # Exclusive: no replacement or overwrite of an existing recording.
        os.link(temporary, NAME, dst_dir_fd=directory_fd, follow_symlinks=False)
    finally:
        if temporary is not None:
            os.unlink(temporary)
        os.close(directory_fd)
