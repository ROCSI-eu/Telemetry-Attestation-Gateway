#!/usr/bin/env python3
"""Loopback-only, one-shot, operator-triggered synthetic CLI short-circuit demo.

EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC
NOT VALIDATION OR PRODUCTION AUTHORIZATION

Two short-circuit cases remain; a third requires an explicitly provisioned offline
synthetic Noir/Barretenberg toolchain. All private material stays in the sandbox.
No customer/source data, commands, publication or public network.
"""
from __future__ import annotations

import argparse
import http.server
import json
import os
from pathlib import Path
import resource
import secrets
import selectors
import signal
import socket
import stat
import subprocess
import sys
import threading
import time

HERE = Path(__file__).resolve().parent
CLI = HERE.parent / "integrated-cli-v0" / "cli.py"
LABELS = ["EXPERIMENTAL", "SYNTHETIC_ONLY", "A0_SYNTHETIC",
          "NOT VALIDATION OR PRODUCTION AUTHORIZATION"]
SCHEMA = "TAG_LOCAL_CLI_SHORT_CIRCUIT_V0_EXPERIMENTAL"
# The actual repository CLI executes, but these cases stop before proving.
PRESETS = {
    "over_limit": ("unsigned-consistent", "499", 3, "NOT_SATISFIED"),
    "malformed_source": ("bad-crc", "600", 2, "NOT_EVALUATED"),
    "verified_synthetic": ("unsigned-consistent", "600", 0, "SATISFIED"),
}
MAX_INPUT = 64
MAX_OUTPUT = 16384
RUN_SECONDS = 20
HTTP_READ_SECONDS = 3
PROOF_RUN_SECONDS = 90
PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>TAG — local synthetic CLI control</title>
<style>body{font:16px/1.5 system-ui;background:#091524;color:#e9f4ff;
max-width:730px;margin:5vh auto;padding:20px}main{background:#14273b;
border:1px solid #486479;border-radius:18px;padding:24px}h1{font-size:1.55rem}
.notice{color:#b9f1e5;font-weight:700}button,input,select{font:inherit;
padding:10px;border-radius:8px}input,select{background:#071725;color:#fff;
border:1px solid #7a9bb1}button{background:#9ce5df;border:0;cursor:pointer}
button:disabled{opacity:.45}label{display:block;margin:14px 0}
pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#081623;padding:16px}
</style></head><body><main><p class="notice">EXPERIMENTAL · SYNTHETIC_ONLY ·
A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION</p>
<h1>Local CLI → browser experiment</h1>
<p>One allowlisted synthetic CLI invocation per preview. Short-circuit scenarios
never prove. The optional genuine synthetic case invokes the pinned Noir prover
and independent offline verifier module only when the operator has explicitly
provisioned an isolated local toolchain. Missing tools fail closed.</p>
<p>Proof validity is <strong>not</strong> telemetry truth, interval coverage, safety,
compliance, policy/freshness/revocation/replay acceptance or a business decision.
No source identity, private witness or observed speed is sent to the browser.</p>
<label>One-session operator token (from local terminal)
<input id="token" type="password" autocomplete="off" spellcheck="false"></label>
<label>Predefined synthetic scenario
<select id="scenario"><option value="over_limit">Over-limit observation</option>
<option value="malformed_source">Malformed synthetic source</option>
<option value="verified_synthetic">Genuine synthetic proof + offline verification (preprovisioned only)</option></select></label>
<button id="run" type="button">Execute one isolated synthetic CLI scenario</button>
<p id="status" role="status" aria-live="polite">IDLE · no CLI execution</p>
<pre id="result">No result yet.</pre>
<p>Only typed, allowlisted result fields can enter this page. The server
accepts no arbitrary commands, inputs, proof packages or uploads.
A failed isolated invocation is UNAVAILABLE, never VALID.</p></main>
<script>"use strict";
const run=document.getElementById("run"),status=document.getElementById("status");
run.addEventListener("click",async()=>{
 run.disabled=true;status.textContent="RUNNING · bounded isolated CLI invocation";
 document.getElementById("result").textContent="No accepted result yet.";
 try {
  const response=await fetch("execute",{method:"POST",cache:"no-store",
   headers:{"Content-Type":"application/json","X-TAG-Local-Token":
    document.getElementById("token").value},
   body:JSON.stringify({scenario:document.getElementById("scenario").value})});
  const data=await response.json();
  if(!response.ok)throw Error("Local invocation rejected or unavailable");
  if(data.schema_version!=="TAG_LOCAL_CLI_SHORT_CIRCUIT_V0_EXPERIMENTAL"
    ||data.state!=="COMPLETED")throw Error("Incompatible local result");
  status.textContent=data.scenario==="verified_synthetic"
   ?"COMPLETED · recorded synthetic proof verification (not browser verification)"
   :"COMPLETED · synthetic CLI short-circuit (no proof)";
  document.getElementById("result").textContent=JSON.stringify(data,null,2);
 }catch(_){status.textContent="UNAVAILABLE · no verified result";
  document.getElementById("result").textContent="Run failed closed.";}
 finally {document.getElementById("token").value="";}
});</script></body></html>"""


class Rejected(Exception):
    """Generic failure; private paths and CLI stderr must not reach HTTP."""


def trusted_bwrap() -> str:
    binary = Path("/usr/bin/bwrap")
    try:
        mode = binary.lstat()
        if (not stat.S_ISREG(mode.st_mode) or mode.st_uid != 0
                or stat.S_IMODE(mode.st_mode) & 0o022):
            raise Rejected
    except OSError as exc:
        raise Rejected from exc
    return str(binary)


def _resource_limits() -> None:
    resource.setrlimit(resource.RLIMIT_CPU, (12, 12))
    resource.setrlimit(resource.RLIMIT_AS, (1024 * 1024 * 1024,) * 2)
    resource.setrlimit(resource.RLIMIT_FSIZE, (1024 * 1024,) * 2)


def offline_toolchain(root: Path | None) -> Path:
    """Validate one explicit owner-private preprovisioned research toolchain.

    The browser cannot provide this path. No download, PATH lookup, or silent
    fallback is permitted for genuine proof generation.
    """
    if root is None or not root.is_absolute():
        raise Rejected
    try:
        if (Path(os.path.abspath(root)) != Path(os.path.realpath(root))
                or HERE.parent in root.parents or root == HERE.parent):
            raise Rejected
        meta = root.lstat()
        if (not stat.S_ISDIR(meta.st_mode) or meta.st_uid != os.getuid()
                or stat.S_IMODE(meta.st_mode) != 0o700):
            raise Rejected
        for name in ("bb", "nargo"):
            command = root / "bin" / name
            resolved = command.resolve(strict=True)
            if root not in resolved.parents:
                raise Rejected
            info = resolved.stat()
            if (not stat.S_ISREG(info.st_mode) or not info.st_mode & stat.S_IXUSR
                    or info.st_uid != os.getuid()
                    or stat.S_IMODE(info.st_mode) & 0o022):
                raise Rejected
        cache = root / "cache" / "crs"
        if (not cache.is_dir() or cache.is_symlink()
                or root not in cache.resolve().parents):
            raise Rejected
        return root
    except (OSError, RuntimeError) as exc:
        raise Rejected from exc


def minimize(document: dict, scenario: str, status: int) -> dict:
    """Reconstruct each permitted field, never relay upstream JSON wholesale."""
    capture, bound, expected_exit, expected_claim = PRESETS[scenario]
    try:
        if (status != expected_exit or type(document) is not dict
            or document["schema_version"] != "TAG_INTEGRATED_CLI_RESULT_V0_EXPERIMENTAL"
            or document["labels"] != LABELS
            or document["capture_case"] != capture
            or document["command_path"] != "NONE"
            or document["relying_party_decision"] != "NOT_MADE"
            or document["proof_validity_is_telemetry_truth"] is not False
            or document["claim"]["maximum_speed_cm_s"] != int(bound)
            or document["claim"]["private_observation_disclosed"] is not False
            or document["proof"]["generation"] != (
                "GENERATED" if scenario == "verified_synthetic" else "NOT_ATTEMPTED")
            or document["proof"]["cryptographic"]["status"] != (
                "VALID" if scenario == "verified_synthetic" else "NOT_CHECKED")
            or document["publication"]["mode"] != "disabled"
            or document["publication"]["state"] != "NOT_PERFORMED"
            or set(document["disclosure"]) != {"raw_telemetry", "exact_normalized_speed", "private_witness", "proof_secrets", "stable_identity"}
            or document["claim"]["status"] != expected_claim
            or any(document["disclosure"].values())):
            raise Rejected
        source = document["source"]["normalization"]
        if (scenario == "over_limit" and source != "NORMALIZED"
            or scenario == "malformed_source" and source != "REJECTED"
            or scenario == "verified_synthetic" and source != "NORMALIZED"):
            raise Rejected
        if scenario == "verified_synthetic":
            dims = document["verification_dimensions"]
            if (document["proof"]["verification_input"]["status"] != "ACCEPTED"
                    or document["proof"]["cryptographic"].get("reason") is not None
                    or document["source"]["assurance_id"] != "A0_SYNTHETIC"
                    or document["source"]["source_trust"] != "UNSIGNED"
                    or dims["policy"] != "NOT_EVALUATED"
                    or dims["freshness"] != "NOT_EVALUATED"
                    or dims["revocation"] != "NOT_EVALUATED"
                    or dims["replay"] != "NOT_EVALUATED"
                    or dims["assurance"] != {
                        "declared": "A0_SYNTHETIC", "effective": "A0_SYNTHETIC",
                        "required": "NOT_EVALUATED", "demonstrator": "A0_SYNTHETIC",
                    }):
                raise Rejected
    except (KeyError, ValueError, TypeError, AttributeError) as exc:
        raise Rejected from exc
    return {
        "schema_version": SCHEMA, "labels": LABELS, "state": "COMPLETED",
        "scenario": scenario, "source": source,
        "source_trust": "UNSIGNED" if scenario == "verified_synthetic" else "NOT_EVALUATED",
        "claim": expected_claim,
        "proof_generation": "GENERATED" if scenario == "verified_synthetic" else "NOT_ATTEMPTED",
        "verification_input": "ACCEPTED" if scenario == "verified_synthetic" else "NOT_CHECKED",
        "cryptographic": "VALID" if scenario == "verified_synthetic" else "NOT_CHECKED",
        "assurance": "A0_SYNTHETIC", "policy": "NOT_EVALUATED",
        "freshness": "NOT_EVALUATED", "revocation": "NOT_EVALUATED",
        "replay": "NOT_EVALUATED",
        "publication": "NOT_PERFORMED", "relying_party_decision": "NOT_MADE",
        "command_path": "NONE", "restricted_fields_disclosed": False,
        "browser_verified": False,
        "proof_validity_is_telemetry_truth": False,
    }


def _bounded_run(cmd: list[str], *, timeout: int = RUN_SECONDS,
                 extra_path: str = "/usr/bin:/bin") -> tuple[bytes, int]:
    """Read only MAX_OUTPUT bytes while running; kill the child process group on failure."""
    try:
        proc = subprocess.Popen(
            cmd, cwd="/", stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            env={"PATH": extra_path, "PYTHONDONTWRITEBYTECODE": "1",
                 "LANG": "C.UTF-8"},
            preexec_fn=_resource_limits, start_new_session=True,
        )
    except OSError as exc:
        raise Rejected from exc
    try:
        deadline = time.monotonic() + timeout
        output = bytearray()
        with selectors.DefaultSelector() as selector:
            selector.register(proc.stdout, selectors.EVENT_READ)
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0 or not selector.select(remaining):
                    raise Rejected
                chunk = os.read(proc.stdout.fileno(),
                                min(4096, MAX_OUTPUT + 1 - len(output)))
                if not chunk:
                    break
                output.extend(chunk)
                if len(output) > MAX_OUTPUT:
                    raise Rejected
        proc.wait(timeout=max(0.01, deadline - time.monotonic()))
        return bytes(output), proc.returncode
    except (OSError, subprocess.TimeoutExpired, Rejected) as exc:
        # Kill the whole bounded process group; a CLI-descendant cannot outlive it.
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        proc.wait()
        raise Rejected from exc
    finally:
        proc.stdout.close()


def execute(scenario: str, toolchain_root: Path | None = None) -> dict:
    if scenario not in PRESETS:
        raise Rejected
    capture, bound, _, _ = PRESETS[scenario]
    tools = offline_toolchain(toolchain_root) if scenario == "verified_synthetic" else None
    # Expose only system Python and the repository's synthetic experiment tree.
    # In particular: never bind host /, /home, /etc or the full /dev tree.
    experiments = HERE.parent
    cmd = [trusted_bwrap(), "--unshare-net", "--die-with-parent",
           "--ro-bind", "/usr", "/usr",
           "--symlink", "usr/lib", "/lib",
           "--symlink", "usr/lib64", "/lib64",
           "--ro-bind", str(experiments), str(experiments),
           "--tmpfs", "/tmp", "--dev", "/dev", "--proc", "/proc",
           "--setenv", "HOME", "/tmp", "--setenv", "TMPDIR", "/tmp"]
    if tools is not None:
        cmd.extend(["--ro-bind", str(tools), str(tools)])
    path = f"{tools}/bin:/usr/bin:/bin" if tools is not None else "/usr/bin:/bin"
    cmd.extend(["--setenv", "PATH", path, "--",
           sys.executable, str(CLI), "--capture-name", capture,
           "--maximum-speed-cm-s", bound, "--format", "json",
           "--publication", "disabled"])
    try:
        if tools is None:
            output, exit_status = _bounded_run(cmd)
        else:
            output, exit_status = _bounded_run(
                cmd, timeout=PROOF_RUN_SECONDS, extra_path=path)
        return minimize(json.loads(output), scenario, exit_status)
    except (ValueError, TypeError) as exc:
        raise Rejected from exc

class Handler(http.server.BaseHTTPRequestHandler):
    def setup(self) -> None:
        # One wall-clock deadline covers both request headers and body.
        # A per-recv socket timeout alone does not stop slow-drip clients.
        self._input_deadline = time.monotonic() + HTTP_READ_SECONDS
        self._input_expired = threading.Event()
        self.request.settimeout(HTTP_READ_SECONDS)
        self._input_timer = threading.Timer(HTTP_READ_SECONDS, self._expire_input)
        self._input_timer.daemon = True
        self._input_timer.start()
        try:
            super().setup()
        except BaseException:
            self._input_timer.cancel()
            raise

    def _expire_input(self) -> None:
        self._input_expired.set()
        try:
            # Interrupt a buffered readline or body read, even when a peer
            # has been sending bytes continuously.
            self.request.shutdown(socket.SHUT_RD)
        except OSError:
            pass

    def _finish_input(self) -> bool:
        self._input_timer.cancel()
        return (not self._input_expired.is_set()
                and time.monotonic() < self._input_deadline)

    def finish(self) -> None:
        try:
            super().finish()
        finally:
            self._input_timer.cancel()

    def log_message(self, *args) -> None:
        pass  # No access logs, tokens, request content or private paths.

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy",
                         "default-src 'none'; script-src 'unsafe-inline'; "
                         "style-src 'unsafe-inline'; connect-src 'self'; form-action 'none'")
        self.end_headers()
        self.wfile.write(body)

    def _origin_ok(self) -> bool:
        origin = f"http://127.0.0.1:{self.server.server_port}"
        return (self.headers.get("Host") == f"127.0.0.1:{self.server.server_port}"
                and self.headers.get("Origin") == origin
                and self.headers.get("Sec-Fetch-Site", "same-origin") == "same-origin")

    def do_GET(self) -> None:
        if not self._finish_input():
            return
        if (self.path != "/" or
                self.headers.get("Host") != f"127.0.0.1:{self.server.server_port}"):
            self._send(404, b"Not found", "text/plain")
            return
        self._send(200, PAGE.encode(), "text/html; charset=utf-8")

    def do_POST(self) -> None:
        if (self._input_expired.is_set() or time.monotonic() >= self._input_deadline
            or self.path != "/execute" or not self._origin_ok()
            or self.headers.get("Content-Type") != "application/json"
            or not secrets.compare_digest(
                self.headers.get("X-TAG-Local-Token", ""), self.server.token)
            or not self.headers.get("Content-Length", "").isdigit()
            or not 1 <= int(self.headers["Content-Length"]) <= MAX_INPUT):
            self._send(403, b'{"error":"REJECTED"}', "application/json")
            return
        try:
            expected_bytes = int(self.headers["Content-Length"])
            body = self.rfile.read(expected_bytes)
            if len(body) != expected_bytes or not self._finish_input():
                raise Rejected
            payload = json.loads(body)
            if (type(payload) is not dict or set(payload) != {"scenario"}
                or type(payload["scenario"]) is not str
                or payload["scenario"] not in PRESETS):
                raise Rejected
            with self.server.guard:
                if self.server.used:
                    raise Rejected
                self.server.used = True  # fail closed; no retries or queue
            result = execute(payload["scenario"], self.server.toolchain_root)
            self._send(200, json.dumps(result, separators=(",", ":")).encode(),
                       "application/json")
        except (Rejected, ValueError, TypeError, OSError):
            self._send(503, b'{"error":"UNAVAILABLE"}', "application/json")


class Server(http.server.HTTPServer):
    def __init__(self, token: str, toolchain_root: Path | None = None):
        super().__init__(("127.0.0.1", 0), Handler)
        self.token = token
        self.toolchain_root = toolchain_root
        self.guard = threading.Lock()
        self.used = False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seconds", type=int, default=120)
    parser.add_argument("--offline-toolchain-root", type=Path,
                        help="existing owner-private, preprovisioned pinned research toolchain")
    args = parser.parse_args()
    if not 1 <= args.seconds <= 300:
        parser.error("preview lifetime must be 1-300 seconds")
    trusted_bwrap()  # missing isolation means no listener
    if args.offline_toolchain_root is not None:
        offline_toolchain(args.offline_toolchain_root)
    with Server(secrets.token_urlsafe(32), args.offline_toolchain_root) as server:
        timer = threading.Timer(args.seconds, server.shutdown)
        timer.daemon = True
        timer.start()
        try:
            print(" · ".join(LABELS), flush=True)
            print(f"Local preview: http://127.0.0.1:{server.server_port}/", flush=True)
            print(f"One-session operator token: {server.token}", flush=True)
            server.serve_forever(poll_interval=0.1)
        finally:
            timer.cancel()
            server.token = ""  # no retained credentials
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
