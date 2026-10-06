#!/usr/bin/env python3
"""Run the repository-owned lightweight experiment quality gate."""

from __future__ import annotations

import difflib
import os
from pathlib import Path
import subprocess
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
LABEL = "EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION"
COMMAND_TIMEOUT_SECONDS = 120

APPROVED_TESTS = (
    "experiments/bounded-speed-v0/test_bounded_speed.py",
    "experiments/mavlink-normalization-v0/test_mavlink_normalize.py",
    "experiments/bounded-speed-proof-v0/test_verify.py",
    "experiments/end-to-end-v0/test_demo.py",
    "experiments/mock-gateway-v0/test_mock_gateway.py",
    "experiments/mock-gateway-v0/test_cleanup_recovery.py",
    "experiments/mock-gateway-v0/test_review_regressions.py",
    "experiments/publication-mock-v0/test_publication_mock.py",
    "experiments/publication-adapter-v0/test_publication_adapter.py",
)

DETERMINISTIC_EVIDENCE = (
    (
        "experiments/mock-gateway-v0/evidence.py",
        "experiments/mock-gateway-v0/evidence-results.json",
    ),
    (
        "experiments/publication-mock-v0/evidence.py",
        "experiments/publication-mock-v0/evidence-results.json",
    ),
    (
        "experiments/publication-adapter-v0/evidence.py",
        "experiments/publication-adapter-v0/evidence-results.json",
    ),
)


class CheckFailure(RuntimeError):
    """Raised when a quality-gate check fails."""


def repository_python_files() -> list[Path]:
    roots = (REPO_ROOT / "experiments", REPO_ROOT / "scripts")
    return sorted(
        path
        for root in roots
        for path in root.rglob("*.py")
        if path.is_file()
    )


def compile_python_sources() -> None:
    files = repository_python_files()
    if not files:
        raise CheckFailure("no Python sources found under experiments/ or scripts/")

    print(f"[compile] checking {len(files)} Python source files")
    for path in files:
        try:
            source = path.read_text(encoding="utf-8")
            compile(source, str(path.relative_to(REPO_ROOT)), "exec", dont_inherit=True)
        except (OSError, SyntaxError, UnicodeError) as exc:
            raise CheckFailure(
                f"Python compile/integrity check failed for {path.relative_to(REPO_ROOT)}: {exc}"
            ) from exc


def checked_path(relative: str) -> Path:
    path = REPO_ROOT / relative
    if not path.is_file():
        raise CheckFailure(f"registered check path does not exist: {relative}")
    return path


def subprocess_environment() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def run_python(
    relative: str, *, capture_stdout: bool = False
) -> subprocess.CompletedProcess[bytes]:
    path = checked_path(relative)
    print(f"[run] {relative}")
    try:
        completed = subprocess.run(
            [sys.executable, str(path)],
            cwd=REPO_ROOT,
            env=subprocess_environment(),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE if capture_stdout else None,
            stderr=subprocess.PIPE if capture_stdout else None,
            check=False,
            timeout=COMMAND_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        raise CheckFailure(
            f"{relative} exceeded the {COMMAND_TIMEOUT_SECONDS}s quality-gate timeout"
        ) from exc

    if completed.returncode != 0:
        if capture_stdout:
            stdout = completed.stdout.decode("utf-8", errors="replace")
            stderr = completed.stderr.decode("utf-8", errors="replace")
            if stdout:
                print(stdout, file=sys.stderr, end="" if stdout.endswith("\n") else "\n")
            if stderr:
                print(stderr, file=sys.stderr, end="" if stderr.endswith("\n") else "\n")
        raise CheckFailure(f"{relative} exited with status {completed.returncode}")

    return completed


def run_approved_tests() -> None:
    for relative in APPROVED_TESTS:
        run_python(relative)


def check_evidence(generator: str, expected_relative: str) -> None:
    expected_path = checked_path(expected_relative)
    completed = run_python(generator, capture_stdout=True)
    actual = completed.stdout
    expected = expected_path.read_bytes()

    if actual == expected:
        print(f"[evidence] byte-for-byte match: {expected_relative}")
        return

    expected_text = expected.decode("utf-8", errors="replace").splitlines(keepends=True)
    actual_text = actual.decode("utf-8", errors="replace").splitlines(keepends=True)
    diff = "".join(
        difflib.unified_diff(
            expected_text,
            actual_text,
            fromfile=expected_relative,
            tofile=f"regenerated:{generator}",
        )
    )
    if diff:
        print(diff, file=sys.stderr, end="" if diff.endswith("\n") else "\n")
    raise CheckFailure(f"deterministic evidence mismatch: {expected_relative}")


def check_deterministic_evidence() -> None:
    for generator, expected in DETERMINISTIC_EVIDENCE:
        check_evidence(generator, expected)


def main() -> int:
    print(LABEL)
    print("[quality-gate] offline-default lightweight experiment checks")
    try:
        compile_python_sources()
        run_approved_tests()
        check_deterministic_evidence()
    except CheckFailure as exc:
        print(f"[quality-gate] FAIL: {exc}", file=sys.stderr)
        return 1

    print("[quality-gate] PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
