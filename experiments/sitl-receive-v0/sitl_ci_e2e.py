#!/usr/bin/env python3
"""Single bounded real-SITL -> synthetic proof -> separate verifier CI check.

EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC
NOT VALIDATION OR PRODUCTION AUTHORIZATION
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments" / "integrated-cli-v0"))
import cli  # noqa: E402

LABELS = ["EXPERIMENTAL", "SYNTHETIC_ONLY", "A0_SYNTHETIC",
          "NOT VALIDATION OR PRODUCTION AUTHORIZATION"]
LIMIT_CM_S = 600
STARTUP_SECONDS = 15
VERIFY_SECONDS = 45


class GateFailure(RuntimeError):
    pass


def require(condition: bool, code: str) -> None:
    if not condition:
        raise GateFailure(code)


def stop_simulator(proc: subprocess.Popen[bytes]) -> None:
    if proc.poll() is None:
        os.killpg(proc.pid, signal.SIGTERM)
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait(timeout=5)
    require(proc.poll() is not None, "SIMULATOR_CLEANUP_FAILED")


def run_once() -> dict[str, object]:
    os.umask(0o077)
    sim = Path(os.environ["TAG_SITL_BIN"]).resolve(strict=True)
    source = Path(os.environ["TAG_ARDUPILOT_ROOT"]).resolve(strict=True)
    require(sim == source / "build/sitl/bin/arducopter" and sim.is_file(),
            "SIMULATOR_BINARY_UNEXPECTED")
    defaults = source / "Tools/autotest/default_params/copter.parm"
    require(defaults.is_file(), "SIMULATOR_DEFAULTS_UNAVAILABLE")

    with tempfile.TemporaryDirectory(prefix="tag-sitl-e2e-", dir=os.environ["RUNNER_TEMP"]) as td:
        session = Path(td)
        state = session / "sitl-state"
        state.mkdir(mode=0o700)
        params = state / "synthetic.parm"
        params.write_text("SERIAL0_PROTOCOL 2\nSR0_POSITION 5\n", encoding="utf-8")
        command = [str(sim), "--model", "+", "--speedup", "1",
                   "--home", "-35.362938,149.165085,584,353",
                   "--defaults", f"{defaults},{params}",
                   "--serial0", "udpclient:127.0.0.1:14550"]
        proc = subprocess.Popen(command, cwd=state, stdin=subprocess.DEVNULL,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                start_new_session=True)
        try:
            time.sleep(STARTUP_SECONDS)
            require(proc.poll() is None, "SIMULATOR_EXITED_BEFORE_RECEIVE")
            try:
                capture = cli.sitl_receive.receive_capture()
            except cli.sitl_receive.ReceiveError as error:
                raise GateFailure("RECEIVER_" + error.code) from None
            require(len(capture["events"]) == 2, "RECEIVER_COUNT_MISMATCH")
            package = session / "proof-package"
            result = cli.run_integrated(cli.MAVLINK_DIR / "fixtures.json",
                                        "sitl-loopback", LIMIT_CM_S,
                                        capture_data=capture, package_dir=package)
            require(result["source"]["normalization"] == "NORMALIZED", "NORMALIZATION_FAILED")
            require(result["source"]["source_trust"] in {"UNSIGNED", "UNKNOWN"},
                    "SOURCE_TRUST_UNEXPECTED")
            require(result["claim"]["status"] == "SATISFIED", "PREDICATE_NOT_SATISFIED")
            require(result["proof"]["generation"] == "GENERATED", "PROOF_NOT_GENERATED")
            require(result["proof"]["cryptographic"]["status"] == "VALID", "INTEGRATED_VERIFICATION_FAILED")
            require(result["publication"]["mode"] == "disabled", "PUBLICATION_NOT_DISABLED")
            require(result["relying_party_decision"] == "NOT_MADE", "BUSINESS_DECISION_UNEXPECTED")
            require(result["command_path"] == "NONE", "COMMAND_PATH_UNEXPECTED")
            require(not any(result["disclosure"].values()), "RESTRICTED_DISCLOSURE")
            encoded = json.dumps(result, sort_keys=True)
            for forbidden in ("frame_hex", "Prover.toml"):
                require(forbidden not in encoded, "RESTRICTED_RESULT_FIELD")
            verifier = ROOT / "experiments/bounded-speed-proof-v0/verify.py"
            args = [sys.executable, str(verifier),
                    "--public-artifact", str(package / "public-artifact.cbor"),
                    "--proof", str(package / "proof"),
                    "--verification-key", str(package / "vk")]
            try:
                checked = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                         text=True, timeout=VERIFY_SECONDS, check=False)
            except subprocess.TimeoutExpired:
                raise GateFailure("SEPARATE_VERIFIER_TIMEOUT") from None
            require(checked.returncode == 0, "SEPARATE_VERIFIER_FAILED")
            try:
                independently = json.loads(checked.stdout)
            except json.JSONDecodeError:
                raise GateFailure("SEPARATE_VERIFIER_OUTPUT_INVALID") from None
            require(independently["cryptographic"]["status"] == "VALID", "SEPARATE_VERIFIER_NOT_VALID")
            require(proc.poll() is None, "SIMULATOR_EXITED_DURING_PROOF")
            return {"labels": LABELS, "source": "real_Copter_4.7.1_synthetic_SITL",
                    "observations": 2, "normalization": "NORMALIZED",
                    "source_trust": result["source"]["source_trust"],
                    "proof": "GENERATED", "integrated_crypto": "VALID",
                    "separate_process_crypto": "VALID", "publication": "DISABLED",
                    "relying_party_decision": "NOT_MADE", "command_path": "NONE"}
        finally:
            stop_simulator(proc)


def main() -> int:
    def terminate(_signal, _frame) -> None:
        raise GateFailure("EXECUTION_TIMEOUT")
    signal.signal(signal.SIGTERM, terminate)
    try:
        record = run_once()
    except (GateFailure, OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        code = str(exc) if isinstance(exc, GateFailure) else "INTEGRATION_EXECUTION_FAILED"
        print(json.dumps({"labels": LABELS, "status": "FAIL", "reason": code}, sort_keys=True))
        return 1
    print(json.dumps({**record, "status": "PASS", "cleanup": "PASS"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
