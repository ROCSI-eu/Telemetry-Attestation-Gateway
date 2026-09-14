#!/usr/bin/env python3
"""Shared helpers for the synthetic bounded-speed proof experiment."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
BOUNDED_SPEED_MODULE = ROOT.parent / "bounded-speed-v0" / "bounded_speed.py"

EXPECTED_NARGO_VERSION = "1.0.0-beta.26"
EXPECTED_BB_VERSION = "5.2.0"
EXPECTED_VK_SHA256 = "0e4eb3c0d0e64b43a67460d6e208f2f1070c805bd3c075413dee21a83e0c85b1"

LABELS = (
    "EXPERIMENTAL",
    "SYNTHETIC_ONLY",
    "A0_SYNTHETIC",
    "NOT VALIDATION OR PRODUCTION AUTHORIZATION",
)

CONTEXT_HI = 0xE835225E3470B8ECAE7748209D432AC2
CONTEXT_LO = 0x6DF591A1FEBB1176F0A96A0D439C94B5


class ExperimentError(RuntimeError):
    """Fail-closed error that is safe to surface without witness material."""


def load_bounded_speed_module():
    spec = importlib.util.spec_from_file_location("tag_bounded_speed_v0", BOUNDED_SPEED_MODULE)
    if spec is None or spec.loader is None:
        raise ExperimentError("bounded-speed-v0 module could not be loaded")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BOUNDED = load_bounded_speed_module()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def context_limbs(context_hex: str) -> tuple[int, int]:
    if not isinstance(context_hex, str) or len(context_hex) != 64:
        raise ExperimentError("experimental context digest must be 32-byte hex")
    try:
        value = int(context_hex, 16)
    except ValueError as exc:
        raise ExperimentError("experimental context digest is not hexadecimal") from exc
    hi, lo = value >> 128, value & ((1 << 128) - 1)
    if (hi, lo) != (CONTEXT_HI, CONTEXT_LO):
        raise ExperimentError("experimental context digest does not match the pinned circuit context")
    return hi, lo


def reconstruct_bb_public_inputs(public_artifact: bytes) -> tuple[tuple[str, int], ...]:
    """Strictly reconstruct the exact ordered public inputs expected by the circuit."""
    neutral = dict(BOUNDED.reconstruct_public_inputs(public_artifact))
    hi, lo = context_limbs(neutral["context_sha256"])
    return (
        ("version", int(neutral["version"])),
        ("maximum_speed_cm_s", int(neutral["maximum_speed_cm_s"])),
        ("context_hi", hi),
        ("context_lo", lo),
    )


def public_inputs_json(public_artifact: bytes) -> str:
    ordered = reconstruct_bb_public_inputs(public_artifact)
    values = [f"0x{value:064x}" for _, value in ordered]
    return json.dumps({"public_inputs": values}, sort_keys=True, separators=(",", ":")) + "\n"


def tool_version(command: str, expected_version: str) -> tuple[str, str]:
    path = shutil.which(command)
    if not path:
        raise ExperimentError(f"required local tool is unavailable: {command}")
    result = subprocess.run([path, "--version"], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if result.returncode != 0:
        raise ExperimentError(f"could not determine {command} version")
    output = result.stdout.strip()
    patterns = {
        "nargo": r"^nargo version = ([^\s]+)$",
        "bb": r"^([^\s]+)$",
    }
    pattern = patterns.get(command)
    match = re.search(pattern, output, flags=re.MULTILINE) if pattern else None
    if match is None or match.group(1) != expected_version:
        raise ExperimentError(f"incompatible {command} version; expected {expected_version}")
    return path, output


def require_bb() -> tuple[str, str]:
    return tool_version("bb", EXPECTED_BB_VERSION)


def require_prover_tools() -> dict[str, str]:
    nargo_path, nargo_version = tool_version("nargo", EXPECTED_NARGO_VERSION)
    bb_path, bb_version = require_bb()
    return {"nargo_path": nargo_path, "nargo_version": nargo_version, "bb_path": bb_path, "bb_version": bb_version}


def run_sanitized(command: list[str], cwd: Path, *, expect_success: bool = True) -> int:
    """Run a tool without surfacing stdout/stderr that could include witness details."""
    result = subprocess.run(command, cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if expect_success and result.returncode != 0:
        raise ExperimentError(f"local proof tool failed with exit code {result.returncode}")
    if not expect_success and result.returncode == 0:
        raise ExperimentError("local proof tool unexpectedly succeeded")
    return result.returncode
