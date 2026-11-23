# TAG SITL-to-ZKP: Qube Dev1 reproduction (23 November 2026)

**EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION**

## Provenance and scope

This is a minimized, owner-observed record of one local, isolated synthetic experiment on Qube Dev1 on 23 November 2026. The experiment reused the source script `experiments/sitl-receive-v0/sitl_ci_e2e.py` at exact TAG commit `215d9ec5b6739f599f96d57ef311f64c0a97fa42` (merged in PR #167), without source modifications. ArduPilot Copter 4.7.1 was pinned to `dbe792162d06cab66c3475fd5556bf7a120f119e`, MAVLink submodule to `288b907c384a892c8519bfe271682424b1e1a3a0`; Noir was `1.0.0-beta.26`, Barretenberg `5.2.0`. Pinned binaries and public CRS were verified against recorded checksums.

The baseline integrated GitHub Actions experiment succeeded on 22 November 2026: [run #44995909866](https://github.com/ROCSI-eu/Telemetry-Attestation-Gateway/actions/runs/44995909866), job `137126775699`. The Qube reproduction reused the same bounded synthetic SITL configuration: `MAV3_POSITION=10`, MAVLink2 through `serial2` to loopback UDP `127.0.0.1:14550`, `serial0=none`, 15-second simulator startup and a 3-second receive window for up to two observations. The local experiment used an isolated network namespace and a pre-provisioned, verified offline cryptographic toolchain.

## Observed, minimized result

| Gate | Qube Dev1, 23 November 2026 |
| --- | --- |
| Final preflight and single authorized execution | PASS, process exit 0 |
| `GLOBAL_POSITION_INT` observations | 2 |
| Normalization | `NORMALIZED` |
| Bounded-speed predicate (public maximum 600 cm/s) | `SATISFIED` |
| Noir/Barretenberg proof generation | `GENERATED` |
| Integrated cryptographic verification | `VALID` |
| Independent, separate-process cryptographic verification | `VALID` |
| Source trust | `UNSIGNED` |
| Publication | `DISABLED` |
| Relying-party decision | `NOT_MADE` |
| Vehicle command path | `NONE` |
| Experiment cleanup | `PASS` |

The owner supplied the local terminal output confirming this result. A separate read-only postflight confirmed no experiment processes or loopback UDP listener remaining. A one-time, scoped cleanup removed only nine untracked Python bytecode files and an empty Nargo cache file and their empty directories; the final checkout was clean, pinned sources/toolchain were preserved and the separate TAG #88 persistent synthetic service remained running. No private observation values, raw frames, witness, proof, key material, screenshot or host-specific paths are reproduced in this record.

## What this establishes and does not establish

The same synthetic SITL → MAVLink2 → normalization → bounded-speed ZKP → independent verification sequence completed successfully in both GitHub Actions and the local Qube environment. The GitHub run has a publicly inspectable workflow record; the Qube result is an owner-observed local QA record, **not** a separately signed or externally audited attestation.

These two bounded runs do **not** authenticate the MAVLink source, establish trusted timing, prove interval or whole-flight coverage, demonstrate real sensor correctness, physical vehicle compatibility, safety, regulatory or contractual compliance, or authorize live telemetry, hardware, public proving, a vehicle command path, deployment or production use. The public Mission Control showcase remains a static illustration; it does not execute SITL or cryptographic proofs in the visitor's browser.
