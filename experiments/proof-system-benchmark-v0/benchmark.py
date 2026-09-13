#!/usr/bin/env python3
"""Run the synthetic bounded-speed proof benchmark with preinstalled tools.

EXPERIMENTAL
SYNTHETIC_ONLY
A0_SYNTHETIC
NOT VALIDATION OR PRODUCTION AUTHORIZATION
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import statistics
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parent
NOIR_DIR = ROOT / "noir"
TARGET = NOIR_DIR / "target"
PROVER_TOML = NOIR_DIR / "Prover.toml"
TIME_BIN = Path("/usr/bin/time")

EXPECTED_NARGO_FRAGMENT = "1.0.0-beta.26"
EXPECTED_BB_FRAGMENT = "5.2.0"

CASES = {
    "below": (1200, 1500),
    "equal": (1500, 1500),
    "above": (1501, 1500),
}


class BenchmarkError(RuntimeError):
    pass


def tool_version(command: str) -> str:
    path = shutil.which(command)
    if not path:
        raise BenchmarkError(f"required tool not found on PATH: {command}")
    result = subprocess.run(
        [path, "--version"],
        cwd=NOIR_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
    )
    return result.stdout.strip()


def require_pinned_versions() -> dict[str, str]:
    versions = {"nargo": tool_version("nargo"), "bb": tool_version("bb")}
    if EXPECTED_NARGO_FRAGMENT not in versions["nargo"]:
        raise BenchmarkError(
            f"expected nargo containing {EXPECTED_NARGO_FRAGMENT!r}, got {versions['nargo']!r}"
        )
    if EXPECTED_BB_FRAGMENT not in versions["bb"]:
        raise BenchmarkError(
            f"expected bb containing {EXPECTED_BB_FRAGMENT!r}, got {versions['bb']!r}"
        )
    return versions


def write_inputs(speed: int, maximum: int) -> None:
    PROVER_TOML.write_text(
        "# Demonstrably synthetic, test-only values.\n"
        f"speed_cm_s = {speed}\n"
        f"maximum_speed_cm_s = {maximum}\n",
        encoding="utf-8",
    )


def run(command: list[str], *, expect_success: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=NOIR_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if expect_success and result.returncode != 0:
        raise BenchmarkError(
            f"command failed ({result.returncode}): {' '.join(command)}\n{result.stdout}"
        )
    if not expect_success and result.returncode == 0:
        raise BenchmarkError(f"command unexpectedly succeeded: {' '.join(command)}")
    return result


def timed(command: list[str]) -> dict[str, float | int]:
    with tempfile.NamedTemporaryFile(prefix="tag-benchmark-rss-", delete=False) as handle:
        rss_path = Path(handle.name)
    try:
        wrapped = [str(TIME_BIN), "-f", "%M", "-o", str(rss_path), "--", *command]
        start = time.perf_counter_ns()
        run(wrapped)
        elapsed_ms = (time.perf_counter_ns() - start) / 1_000_000
        rss_text = rss_path.read_text(encoding="utf-8").strip()
        max_rss_kb = int(rss_text) if rss_text else 0
        return {"elapsed_ms": round(elapsed_ms, 3), "max_rss_kb": max_rss_kb}
    finally:
        rss_path.unlink(missing_ok=True)


def circuit_path() -> Path:
    path = TARGET / "bounded_speed_noir.json"
    if not path.is_file():
        raise BenchmarkError(f"compiled circuit missing: {path}")
    return path


def witness_path() -> Path:
    path = TARGET / "bounded_speed_noir.gz"
    if not path.is_file():
        raise BenchmarkError(f"witness missing: {path}")
    return path


def proof_path() -> Path:
    path = TARGET / "proof"
    if not path.is_file():
        raise BenchmarkError(f"proof missing: {path}")
    return path


def vk_path() -> Path:
    path = TARGET / "vk"
    if not path.is_file():
        raise BenchmarkError(f"verification key missing: {path}")
    return path


def execute_witness(speed: int, maximum: int, *, expect_success: bool = True) -> None:
    write_inputs(speed, maximum)
    run(["nargo", "execute"], expect_success=expect_success)


def summarize(samples: list[dict[str, float | int]]) -> dict[str, object]:
    elapsed = [float(sample["elapsed_ms"]) for sample in samples]
    rss = [int(sample["max_rss_kb"]) for sample in samples]
    return {
        "runs": len(samples),
        "elapsed_ms": {
            "samples": elapsed,
            "median": round(statistics.median(elapsed), 3),
            "min": round(min(elapsed), 3),
            "max": round(max(elapsed), 3),
        },
        "max_rss_kb": {
            "samples": rss,
            "max": max(rss),
        },
    }


def benchmark_valid_case(name: str, speed: int, maximum: int, runs: int) -> dict[str, object]:
    execute_witness(speed, maximum)
    circuit = circuit_path()
    witness = witness_path()

    prove_samples: list[dict[str, float | int]] = []
    verify_samples: list[dict[str, float | int]] = []
    proof_sizes: list[int] = []

    for _ in range(runs):
        prove_samples.append(
            timed(["bb", "prove", "-b", str(circuit), "-w", str(witness), "-o", str(TARGET)])
        )
        proof = proof_path()
        proof_sizes.append(proof.stat().st_size)
        verify_samples.append(
            timed(["bb", "verify", "-p", str(proof), "-k", str(vk_path())])
        )

    return {
        "case": name,
        "synthetic_relation": "<" if speed < maximum else "=",
        "proof_size_bytes": sorted(set(proof_sizes)),
        "prove": summarize(prove_samples),
        "verify": summarize(verify_samples),
    }


def verify_tampered_proof() -> dict[str, object]:
    source = proof_path()
    data = bytearray(source.read_bytes())
    if not data:
        raise BenchmarkError("cannot tamper an empty proof")
    index = len(data) // 2
    data[index] ^= 0x01
    tampered = TARGET / "proof.tampered"
    tampered.write_bytes(data)
    result = run(
        ["bb", "verify", "-p", str(tampered), "-k", str(vk_path())],
        expect_success=False,
    )
    return {"rejected": True, "return_code": result.returncode, "mutated_byte_index": index}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--output", type=Path, default=ROOT / "benchmark-results.json")
    args = parser.parse_args()
    if args.runs < 1:
        raise BenchmarkError("--runs must be at least 1")
    if not TIME_BIN.is_file():
        raise BenchmarkError("/usr/bin/time is required for the benchmark")

    versions = require_pinned_versions()
    TARGET.mkdir(parents=True, exist_ok=True)

    write_inputs(*CASES["below"])
    compile_measurement = timed(["nargo", "compile"])
    circuit = circuit_path()
    execute_witness(*CASES["below"])
    vk_measurement = timed(["bb", "write_vk", "-b", str(circuit), "-o", str(TARGET)])
    vk = vk_path()

    valid_results = [
        benchmark_valid_case("below", *CASES["below"], args.runs),
        benchmark_valid_case("equal", *CASES["equal"], args.runs),
    ]

    execute_witness(*CASES["above"], expect_success=False)
    over_limit = {"rejected_before_proof": True, "synthetic_relation": ">"}

    # Regenerate a known-good below-limit proof before tampering.
    execute_witness(*CASES["below"])
    run(["bb", "prove", "-b", str(circuit), "-w", str(witness_path()), "-o", str(TARGET)])
    run(["bb", "verify", "-p", str(proof_path()), "-k", str(vk)])
    tampered = verify_tampered_proof()

    output = {
        "labels": [
            "EXPERIMENTAL",
            "SYNTHETIC_ONLY",
            "A0_SYNTHETIC",
            "NOT VALIDATION OR PRODUCTION AUTHORIZATION",
        ],
        "predicate": "speed_cm_s <= maximum_speed_cm_s",
        "tool_versions": versions,
        "compile": compile_measurement,
        "verification_key_generation": vk_measurement,
        "valid_cases": valid_results,
        "over_limit_case": over_limit,
        "tampered_proof": tampered,
        "proof_validity_is_not_telemetry_truth": True,
        "environment": {
            "network_required_by_runner": False,
            "hardware": "none",
            "command_path": "none",
        },
    }
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
