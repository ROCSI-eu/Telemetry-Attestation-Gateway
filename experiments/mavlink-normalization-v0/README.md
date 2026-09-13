# MAVLink normalization feasibility spike (`v0`)

> **EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION**

This experiment addresses issue #69. It tests whether a narrow, receive-only MAVLink 2 adapter can parse deterministic synthetic observation frames and normalize horizontal speed into the integer `speed_cm_s` input used by the bounded-speed experiments.

It is not a flight interface, telemetry-truth mechanism, supported adapter, claim-eligibility decision, or production parser. No live vehicle, hardware, network socket, customer/participant data, mission data, or command path is used.

## Pinned source context

The synthetic fixtures are pinned against:

- **Autopilot/SITL target:** ArduPilot Copter `4.7.1` (stable release published 2026-09-03);
- **MAVLink source used by that release:** ArduPilot's `modules/mavlink` submodule commit `288b907c384a892c8519bfe271682424b1e1a3a0`;
- **dialect:** `common.xml`, dialect `0`;
- **wire protocol:** MAVLink 2 only.

The current evidence uses fabricated wire frames rather than launching a SITL process. Pinning the Copter/SITL target prevents the experiment from silently drifting across message-definition versions and leaves a concrete target for a later deterministic SITL capture.

Source references:

- ArduPilot release: <https://github.com/ArduPilot/ardupilot/releases/tag/Copter-4.7.1>
- pinned MAVLink submodule: <https://github.com/ArduPilot/mavlink/tree/288b907c384a892c8519bfe271682424b1e1a3a0>
- pinned common dialect: <https://github.com/ArduPilot/mavlink/blob/288b907c384a892c8519bfe271682424b1e1a3a0/message_definitions/v1.0/common.xml>
- MAVLink 2 serialization: <https://mavlink.io/en/guide/serialization.html>
- MAVLink 2 signing: <https://mavlink.io/en/guide/message_signing.html>

## Observation allowlist and mapping

Only two message IDs are understood:

| Message | ID | Fields used | v0 role |
| --- | ---: | --- | --- |
| `GLOBAL_POSITION_INT` | `33` | `time_boot_ms`, `vx`, `vy` | **Primary** horizontal-speed source |
| `VFR_HUD` | `74` | `groundspeed` | Diagnostic comparison source only |

The parser uses the pinned `CRC_EXTRA` values `104` and `20` respectively and rejects every other message ID before normalization.

### Primary normalization

`GLOBAL_POSITION_INT.vx` and `.vy` are signed `int16` values already expressed in `cm/s`. v0 therefore avoids a floating-point proof input and computes:

`speed_cm_s = ceil(sqrt(vx_cm_s^2 + vy_cm_s^2))`

The ceiling is deliberate. If the Euclidean norm is non-integral, v0 rounds upward so normalization cannot make the horizontal vector magnitude appear smaller than it is. The largest representable pair (`-32768`, `-32768`) normalizes to `46341 cm/s`, which still fits the downstream experimental `uint32` speed domain.

This is a provisional normalization rule, not an approved claim-contract decision.

### `VFR_HUD` diagnostic normalization

`VFR_HUD.groundspeed` is an IEEE-754 binary32 value in `m/s`. The experiment decodes the binary32 bits **exactly** into a rational value, multiplies by `100`, then applies ceiling to produce diagnostic `cm/s`. NaN, infinity, negative values, and values that overflow `uint32` after normalization are rejected.

This path is intentionally diagnostic in v0. It provides evidence about the cost/ambiguity of a float-originated source without making it the primary proof witness.

## Source and trust handling

The capture is single-source. Any change in `(system_id, component_id)` across allowlisted observation frames causes `MIXED_SOURCE`.

Trust is preserved as a closed experimental state:

- `SIGNED_VALID` — the frame signature validates under an explicitly supplied **public synthetic test key** and its signing timestamp increases within the capture-local `(system_id, component_id, link_id)` stream;
- `UNSIGNED` — the frame carries no MAVLink 2 signature;
- `UNKNOWN` — the frame is signed but no matching test verification key is supplied;
- `SIGNATURE_INVALID` — the signature does not validate; the frame is rejected.

The checked-in key material in [`fixtures.json`](fixtures.json) is deliberately public, synthetic, test-only, and unsafe for any real system.

MAVLink signing authenticates frame/key possession only. Even `SIGNED_VALID` does **not** establish sensor truth, hardware integrity, trustworthy time, continuous coverage, safety, compliance, or claim eligibility. `claim_eligibility` is therefore always `NOT_EVALUATED` in this experiment.

## Time and staleness

`GLOBAL_POSITION_INT.time_boot_ms` is preserved as `ms_since_autopilot_boot` and explicitly marked `trustworthy_time: false`.

A deterministic synthetic bridge-receive timestamp accompanies every fixture event. v0 applies only a receiver-age bound:

`decision_received_at_ms - received_at_ms <= max_age_ms`

This demonstrates typed stale-input handling but does not turn the bridge clock into proof of observation recency. Source-time regression is rejected as `SOURCE_TIME_REGRESSION_UNSUPPORTED` because reset/reordering semantics are not defined in v0.

For signed frames, capture-local signing timestamps are checked only for monotonic anti-replay behavior. They are not promoted to trusted observation time.

## MAVLink 2 parsing behavior

The receive-only parser:

- requires MAVLink 2 magic `0xFD`;
- rejects unsupported incompatibility flags;
- validates packet length and the pinned message CRC;
- supports legal MAVLink 2 trailing-zero payload truncation by zero-padding only after CRC validation;
- verifies optional MAVLink 2 signatures when a test verification key exists;
- preserves unknown/unsigned trust instead of silently upgrading it; and
- has no socket, transmit, forwarding, command-generation, command-approval, or flight-control code.

## Synthetic record/replay coverage

[`fixtures.json`](fixtures.json) contains only fabricated test bytes. Coverage includes:

- unsigned and signed-valid observations;
- signed input with no known key;
- invalid signature and signing-timestamp regression;
- bad CRC;
- unsupported message type;
- mixed source IDs;
- stale receiver observation;
- receiver-time and source-time regression;
- non-finite, negative, and overflowing `VFR_HUD` speed;
- missing primary speed source;
- maximum `GLOBAL_POSITION_INT` velocity components;
- conservative non-perfect-square rounding; and
- legal MAVLink 2 trailing-zero truncation.

No fixture is derived from a real vehicle, flight, operator, mission, location, site, customer, or participant.

## Run locally

The experiment uses only the Python standard library and performs no network access:

```text
python3 experiments/mavlink-normalization-v0/test_mavlink_normalize.py
python3 experiments/mavlink-normalization-v0/mavlink_normalize.py
```

The first command runs the test suite. The second replays every checked-in synthetic capture and prints typed normalization/rejection results.

## Current research finding

For the narrow bounded-speed experiment, `GLOBAL_POSITION_INT.vx/vy` is the cleaner **Proposed experimental primary source** because it supplies integer centimetres-per-second components directly. `VFR_HUD.groundspeed` is useful as a diagnostic comparison but introduces binary32 conversion and rounding semantics.

That finding does not freeze the telemetry schema, establish compatibility beyond the pinned experiment, or prove that either field reflects physical truth.

## Non-claims

A successful replay establishes only that this pinned parser can recognize selected synthetic MAVLink 2 observation frames, preserve their declared trust state, and deterministically normalize a bounded horizontal-speed candidate offline.

It does **not** establish:

- telemetry truth or sensor integrity;
- trustworthy time or real-world recency;
- continuous, interval, or whole-flight coverage;
- hardware provenance;
- safety, contractual, payment, or regulatory compliance;
- demand, pilot readiness, or production readiness; or
- authorization for live telemetry, hardware, or MAVLink commands.
