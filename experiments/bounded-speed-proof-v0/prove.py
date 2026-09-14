#!/usr/bin/env python3
"""Generate one minimized synthetic bounded-speed proof package.

EXPERIMENTAL
SYNTHETIC_ONLY
A0_SYNTHETIC
NOT VALIDATION OR PRODUCTION AUTHORIZATION
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import tempfile
from typing import Any

from common import BOUNDED, ExperimentError, LABELS, ROOT, reconstruct_bb_public_inputs, require_prover_tools, run_sanitized, sha256_file

NOIR_SOURCE = ROOT / "noir"
UINT32_MAX = (1 << 32) - 1


def _validate_u32(name: str, value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= UINT32_MAX:
        raise ExperimentError(f"{name} must be an unsigned 32-bit integer")
    return value


def _write_manifest(output_dir: Path, public_artifact: Path, proof: Path, vk: Path, maximum_speed_cm_s: int, versions: dict[str, str]) -> None:
    manifest = {
        "labels": list(LABELS),
        "experiment": "bounded-speed-proof-v0",
        "predicate": "speed_cm_s <= maximum_speed_cm_s",
        "proof_mode": "zero_knowledge",
        "private_witness_disclosed": False,
        "public": {"schema_version": BOUNDED.SCHEMA_VERSION, "maximum_speed_cm_s": maximum_speed_cm_s, "assurance_id": BOUNDED.ASSURANCE_ID},
        "tool_versions": {"nargo": versions["nargo_version"], "bb": versions["bb_version"]},
        "artifacts": {
            "public-artifact.cbor": {"sha256": sha256_file(public_artifact)},
            "proof": {"sha256": sha256_file(proof), "size_bytes": proof.stat().st_size},
            "vk": {"sha256": sha256_file(vk), "size_bytes": vk.stat().st_size},
        },
        "dimensions_not_evaluated": ["telemetry_truth", "policy_lifecycle", "freshness", "revocation", "replay", "publication", "relying_party_business_decision"],
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def prove_package(speed_cm_s: int, maximum_speed_cm_s: int, output_dir: Path) -> dict[str, Any]:
    speed_cm_s = _validate_u32("speed_cm_s", speed_cm_s)
    maximum_speed_cm_s = _validate_u32("maximum_speed_cm_s", maximum_speed_cm_s)
    if BOUNDED.evaluate_predicate(speed_cm_s, maximum_speed_cm_s) != "satisfied":
        return {"labels": list(LABELS), "input": "ACCEPTED", "predicate": "NOT_SATISFIED", "cryptographic": "NOT_ATTEMPTED", "package_written": False}

    versions = require_prover_tools()
    public_artifact_bytes = BOUNDED.encode_public_artifact(maximum_speed_cm_s)
    ordered = dict(reconstruct_bb_public_inputs(public_artifact_bytes))
    output_dir = output_dir.resolve()
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ExperimentError("output directory must not contain existing files")
    output_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="tag-proof-prover-") as tmp:
        work = Path(tmp)
        noir = work / "noir"
        shutil.copytree(NOIR_SOURCE, noir)
        (noir / "Prover.toml").write_text(
            "# EXPERIMENTAL SYNTHETIC_ONLY witness; destroyed after proving.\n"
            f"speed_cm_s = {speed_cm_s}\n"
            f"version = {ordered['version']}\n"
            f"maximum_speed_cm_s = {ordered['maximum_speed_cm_s']}\n"
            f"context_hi = \"{ordered['context_hi']}\"\n"
            f"context_lo = \"{ordered['context_lo']}\"\n",
            encoding="utf-8",
        )
        run_sanitized([versions["nargo_path"], "compile"], noir)
        run_sanitized([versions["nargo_path"], "execute"], noir)
        target = noir / "target"
        circuit = target / "bounded_speed_proof_v0.json"
        witness = target / "bounded_speed_proof_v0.gz"
        if not circuit.is_file() or not witness.is_file():
            raise ExperimentError("pinned Noir outputs were not generated")
        run_sanitized([versions["bb_path"], "write_vk", "-b", str(circuit), "-o", str(target)], noir)
        run_sanitized([versions["bb_path"], "prove", "--zk", "-b", str(circuit), "-w", str(witness), "-o", str(target)], noir)
        proof_source = target / "proof"
        vk_source = target / "vk"
        if not proof_source.is_file() or not vk_source.is_file():
            raise ExperimentError("pinned Barretenberg outputs were not generated")
        public_artifact = output_dir / "public-artifact.cbor"
        proof = output_dir / "proof"
        vk = output_dir / "vk"
        public_artifact.write_bytes(public_artifact_bytes)
        shutil.copyfile(proof_source, proof)
        shutil.copyfile(vk_source, vk)
        _write_manifest(output_dir, public_artifact, proof, vk, maximum_speed_cm_s, versions)

    forbidden = {"Prover.toml", "bounded_speed_proof_v0.gz"}
    if any(path.name in forbidden for path in output_dir.rglob("*")):
        raise ExperimentError("private witness material escaped the temporary prover workspace")
    return {"labels": list(LABELS), "input": "ACCEPTED", "predicate": "SATISFIED", "cryptographic": "PROOF_GENERATED_NOT_YET_VERIFIED", "package_written": True, "output_files": sorted(path.name for path in output_dir.iterdir())}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--speed-cm-s", type=int, required=True, help="synthetic private witness")
    parser.add_argument("--maximum-speed-cm-s", type=int, required=True, help="public synthetic limit")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = prove_package(args.speed_cm_s, args.maximum_speed_cm_s, args.output_dir)
    except ExperimentError as exc:
        result = {"labels": list(LABELS), "input": "REJECTED", "predicate": "NOT_EVALUATED", "cryptographic": "NOT_ATTEMPTED", "package_written": False, "reason": str(exc)}
        print(json.dumps(result, indent=2, sort_keys=True))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["package_written"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
