#!/usr/bin/env python3
"""Loopback-only, one-shot, operator-triggered synthetic CLI short-circuit demo.

EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC
NOT VALIDATION OR PRODUCTION AUTHORIZATION

This adapter cannot run a prover: its two hard-coded scenarios stop beforehand.
No customer/source data, private witness, commands, publication or public network.
"""
from __future__ import annotations

import argparse
import http.server
import json
import os
from pathlib import Path
import resource
import secrets
import stat
import subprocess
import sys
import threading

HERE = Path(__file__).resolve().parent
CLI = HERE.parent / "integrated-cli-v0" / "cli.py"
LABELS = ["EXPERIMENTAL", "SYNTHETIC_ONLY", "A0_SYNTHETIC",
          "NOT VALIDATION OR PRODUCTION AUTHORIZATION"]
SCHEMA = "TAG_LOCAL_CLI_SHORT_CIRCUIT_V0_EXPERIMENTAL"
# The actual repository CLI executes, but these cases stop before proving.
PRESETS = {
    "over_limit": ("unsigned-consistent", "499", 3, "NOT_SATISFIED"),
    "malformed_source": ("bad-crc", "600", 2, "NOT_EVALUATED"),
}
MAX_INPUT = 64
MAX_OUTPUT = 16384
RUN_SECONDS = 20
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
<p>One authorized synthetic short-circuit CLI invocation per preview.
These scenarios stop <strong>before proof generation</strong>; they do not verify
a cryptographic proof. No live telemetry, source truth, policy acceptance,
publication, relying-party decision or browser proof verification is implied.</p>
<label>One-session operator token (from local terminal)
<input id="token" type="password" autocomplete="off" spellcheck="false"></label>
<label>Predefined synthetic scenario
<select id="scenario"><option value="over_limit">Over-limit observation</option>
<option value="malformed_source">Malformed synthetic source</option></select></label>
<button id="run" type="button">Execute one isolated CLI short-circuit</button>
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
  status.textContent="COMPLETED · synthetic CLI short-circuit (no proof)";
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
            or document["proof"]["generation"] != "NOT_ATTEMPTED"
            or document["proof"]["cryptographic"]["status"] != "NOT_CHECKED"
            or document["claim"]["status"] != expected_claim
            or any(document["disclosure"].values())):
            raise Rejected
        source = document["source"]["normalization"]
        if (scenario == "over_limit" and source != "NORMALIZED"
            or scenario == "malformed_source" and source != "REJECTED"):
            raise Rejected
    except (KeyError, ValueError, TypeError, AttributeError) as exc:
        raise Rejected from exc
    return {
        "schema_version": SCHEMA, "labels": LABELS, "state": "COMPLETED",
        "scenario": scenario, "source": source,
        "claim": expected_claim, "proof_generation": "NOT_ATTEMPTED",
        "cryptographic": "NOT_CHECKED", "assurance": "A0_SYNTHETIC",
        "publication": "NOT_PERFORMED", "relying_party_decision": "NOT_MADE",
        "command_path": "NONE", "restricted_fields_disclosed": False,
        "browser_verified": False,
    }


def execute(scenario: str) -> dict:
    if scenario not in PRESETS:
        raise Rejected
    capture, bound, _, _ = PRESETS[scenario]
    cmd = [trusted_bwrap(), "--unshare-net", "--ro-bind", "/", "/",
           "--tmpfs", "/tmp", "--dev-bind", "/dev", "/dev", "--proc", "/proc",
           "--setenv", "HOME", "/tmp", "--setenv", "TMPDIR", "/tmp",
           "--setenv", "PATH", "/usr/bin:/bin", "--",
           sys.executable, str(CLI), "--capture-name", capture,
           "--maximum-speed-cm-s", bound, "--format", "json",
           "--publication", "disabled"]
    try:
        proc = subprocess.run(cmd, cwd="/", stdin=subprocess.DEVNULL,
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                              timeout=RUN_SECONDS, check=False,
                              env={"PATH": "/usr/bin:/bin", "PYTHONDONTWRITEBYTECODE": "1",
                                   "LANG": "C.UTF-8"}, preexec_fn=_resource_limits)
        if len(proc.stdout) > MAX_OUTPUT:
            raise Rejected
        return minimize(json.loads(proc.stdout), scenario, proc.returncode)
    except (OSError, subprocess.TimeoutExpired, ValueError, TypeError) as exc:
        raise Rejected from exc


class Handler(http.server.BaseHTTPRequestHandler):
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
        if (self.path != "/" or
                self.headers.get("Host") != f"127.0.0.1:{self.server.server_port}"):
            self._send(404, b"Not found", "text/plain")
            return
        self._send(200, PAGE.encode(), "text/html; charset=utf-8")

    def do_POST(self) -> None:
        if (self.path != "/execute" or not self._origin_ok()
            or self.headers.get("Content-Type") != "application/json"
            or not secrets.compare_digest(
                self.headers.get("X-TAG-Local-Token", ""), self.server.token)
            or not self.headers.get("Content-Length", "").isdigit()
            or not 1 <= int(self.headers["Content-Length"]) <= MAX_INPUT):
            self._send(403, b'{"error":"REJECTED"}', "application/json")
            return
        try:
            body = self.rfile.read(int(self.headers["Content-Length"]))
            payload = json.loads(body)
            if (type(payload) is not dict or set(payload) != {"scenario"}
                or type(payload["scenario"]) is not str
                or payload["scenario"] not in PRESETS):
                raise Rejected
            with self.server.guard:
                if self.server.used:
                    raise Rejected
                self.server.used = True  # fail closed; no retries or queue
            result = execute(payload["scenario"])
            self._send(200, json.dumps(result, separators=(",", ":")).encode(),
                       "application/json")
        except (Rejected, ValueError, TypeError, OSError):
            self._send(503, b'{"error":"UNAVAILABLE"}', "application/json")


class Server(http.server.HTTPServer):
    def __init__(self, token: str):
        super().__init__(("127.0.0.1", 0), Handler)
        self.token = token
        self.guard = threading.Lock()
        self.used = False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seconds", type=int, default=120)
    args = parser.parse_args()
    if not 1 <= args.seconds <= 300:
        parser.error("preview lifetime must be 1-300 seconds")
    trusted_bwrap()  # missing isolation means no listener
    with Server(secrets.token_urlsafe(32)) as server:
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
