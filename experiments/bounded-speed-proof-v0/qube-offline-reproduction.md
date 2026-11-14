# Qube isolated synthetic-proof reproduction (research checkpoint)

> **EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION**

**Status:** Current observation on Qube, 2026-11-14, from repository `main` at `43dd91c76c4d75b7382f914ed83dd97542fbe6dc`. Commands below are a **manual, opt-in experimental procedure**, not an installer, CI prerequisite, deployment, selected proof stack, supported service, or approved `RP` evaluation package. Issue #88 governs future packaging.

## Verified source, version, and trust limits

The historical synthetic benchmark [GitHub Actions run 34744374843](https://github.com/ROCSI-eu/Telemetry-Attestation-Gateway/actions/runs/34744374843) recorded these release assets and checksum pins. They were downloaded again from the official project GitHub release paths and matched SHA-256 on Qube:

| Artifact | SHA-256 |
| --- | --- |
| `https://github.com/noir-lang/noir/releases/download/v1.0.0-beta.26/nargo-x86_64-unknown-linux-gnu.tar.gz` | `64048040befd55a987158b11137d8f38f9688f696db4d84910dd1bcf0442fb80` |
| `https://github.com/AztecProtocol/barretenberg/releases/download/v5.2.0/barretenberg-amd64-linux.tar.gz` | `17ab8476961728cdc5c69b6c4ff427c9092cef11d1e0b0166929a0417dfa7cfb` |

The extracted executables reported `nargo 1.0.0-beta.26` and `bb 5.2.0`. No binary, third-party source, CRS, or test witness is committed to the repository. **Checksum equivalence to a previous experiment is not a vendor signature or an independent supply-chain audit.** The standalone Barretenberg release-binary provenance/licensing adoption question remains **Open**, so this is ephemeral research use only, not redistribution or architectural selection.

## Preflight and explicit network-only setup

Use a non-production Linux x86_64 research machine where `bwrap`, `wget`, `sha256sum`, `tar`, `python3`, `timeout`, `nice`, and `taskset` are available. Check current `main`/authorization first. Do not run on the shared Production VM. Reject an unavailable network isolation mechanism, mismatched archive digest, unexpected archive entry, incompatible version, unexpected resource pressure, or unresolved source provenance needed for the intended use.

The following **explicit provisioning step requires GitHub downloads** and allows the `bb write_vk` command to fetch public CRS material. It is **not** part of default/offline CI. Perform only when external provisioning is authorized. Run under an unprivileged user:

```sh
umask 077
R=$(mktemp -d /tmp/tag-crypto-synthetic.XXXXXXXX)
mkdir -p "$R/archives" "$R/tools" "$R/bin" "$R/cache/crs" "$R/work/tmp" "$R/work/verify-tmp" "$R/home"
wget -q --timeout=25 --tries=2 -O "$R/archives/nargo.tar.gz" \
  https://github.com/noir-lang/noir/releases/download/v1.0.0-beta.26/nargo-x86_64-unknown-linux-gnu.tar.gz
wget -q --timeout=25 --tries=2 -O "$R/archives/bb.tar.gz" \
  https://github.com/AztecProtocol/barretenberg/releases/download/v5.2.0/barretenberg-amd64-linux.tar.gz
printf '%s  %s\n' 64048040befd55a987158b11137d8f38f9688f696db4d84910dd1bcf0442fb80 "$R/archives/nargo.tar.gz" | sha256sum -c -
printf '%s  %s\n' 17ab8476961728cdc5c69b6c4ff427c9092cef11d1e0b0166929a0417dfa7cfb "$R/archives/bb.tar.gz" | sha256sum -c -
```

Before extracting, inspect both archives and reject any absolute/traversal path, link, device, or other non-regular entry; this gate is **mandatory** (the observed releases contain one regular file each):

```sh
export R
python3 - <<'PY'
import os, tarfile
from pathlib import PurePosixPath
for name in ("nargo", "bb"):
    with tarfile.open(f"{os.environ['R']}/archives/{name}.tar.gz") as archive:
        entries = archive.getmembers()
        assert len(entries) == 1 and entries[0].isfile()
        item = PurePosixPath(entries[0].name)
        assert item.parts == (name,), item
print("Archive entry checks: PASS")
PY
tar -xzf "$R/archives/nargo.tar.gz" -C "$R/tools"
tar -xzf "$R/archives/bb.tar.gz" -C "$R/tools"
chmod 700 "$R/tools/nargo" "$R/tools/bb"
"$R/tools/nargo" --version
"$R/tools/bb" --version
```

Compile the checked-in circuit using only source from the current repository checkout, then provision only the public CRS required by the tiny circuit. **Do not run a prover with private inputs during this network-enabled step.**

```sh
REPO=/path/to/Telemetry-Attestation-Gateway
mkdir -p "$R/work/provision-noir"
cp -a "$REPO/experiments/bounded-speed-proof-v0/noir/." "$R/work/provision-noir/"
(cd "$R/work/provision-noir" && timeout 60s nice -n 10 taskset -c 0-3 "$R/tools/nargo" compile >/dev/null)
timeout 100s nice -n 10 taskset -c 0-3 "$R/tools/bb" write_vk \
  -t noir-recursive \
  -b "$R/work/provision-noir/target/bounded_speed_proof_v0.json" \
  -o "$R/work/provision-noir/target" -c "$R/cache/crs"
sha256sum "$R/work/provision-noir/target/vk"
du -sh "$R/cache/crs" "$R/tools" "$R/archives"
```

The observed VK digest was `0e4eb3c0d0e64b43a67460d6e208f2f1070c805bd3c075413dee21a83e0c85b1`, matching the test-only anchor in `verify.py`. The cached public CRS files observed were `bn254_g1.dat` (262,144 B; SHA-256 `73b97f238c8fdc53dead1e1cc674c73cacab5aea5c2bb06b7ab6c9fa2b9517c7`) and `bn254_g1_compressed.dat` (4,194,304 B; SHA-256 `fad8203ae1fd103658d4bb33b2b4cf126a28352b5de4684737cff23cc15fb94b`). These are **observed local digests**, not a separately authenticated upstream CRS manifest. Reject a mismatched VK or incomplete CRS.

## Offline-only proof and independent verification

A small local `bb` wrapper forwards the **same** isolated `-c` CRS directory for `write_vk`, `prove` and `verify`. It is never added to the user's global PATH, only to the sandbox process environment.

```sh
cat > "$R/bin/bb" <<EOF
#!/bin/sh
set -eu
if [ "\${1:-}" = '--version' ]; then exec "$R/tools/bb" --version; fi
cmd=\$1; shift
exec "$R/tools/bb" "\$cmd" "\$@" -c "$R/cache/crs"
EOF
chmod 700 "$R/bin/bb"
ln -s ../tools/nargo "$R/bin/nargo"
bwrap --unshare-net --ro-bind / / -- /usr/bin/true
```

The `bwrap` network-namespace check must succeed; do **not** silently fall back to a networked prover. Set two **explicitly synthetic** integer test inputs locally (`SYNTHETIC_SPEED_CM_S` and `SYNTHETIC_MAXIMUM_CM_S`; the first must not exceed the second). They must not be sourced from real telemetry or written to Git, receipts, logs, UI, or browser data. The sandbox's `TMPDIR` and output directory are private:

```sh
: "${SYNTHETIC_SPEED_CM_S:?set a synthetic private witness}"
: "${SYNTHETIC_MAXIMUM_CM_S:?set a synthetic public limit}"
P="$REPO/experiments/bounded-speed-proof-v0"
timeout 90s nice -n 10 taskset -c 0-3 bwrap --unshare-net \
  --ro-bind / / --bind "$R" "$R" --dev-bind /dev /dev --proc /proc \
  --setenv HOME "$R/home" --setenv TMPDIR "$R/work/tmp" \
  --setenv PATH "$R/bin:/usr/bin:/bin" \
  -- /usr/bin/python3 "$P/prove.py" \
  --speed-cm-s "$SYNTHETIC_SPEED_CM_S" \
  --maximum-speed-cm-s "$SYNTHETIC_MAXIMUM_CM_S" \
  --output-dir "$R/work/proof-package"
```

Run the verifier in a **separate offline process**. The entire filesystem is read-only to the verifier except its private disposable scratch directory. The verifier reconstructs public inputs from canonical CBOR and checks the pinned VK without witness access:

```sh
timeout 45s nice -n 10 taskset -c 0-3 bwrap --unshare-net \
  --ro-bind / / --bind "$R/work/verify-tmp" "$R/work/verify-tmp" \
  --dev-bind /dev /dev --proc /proc \
  --setenv HOME "$R/home" --setenv TMPDIR "$R/work/verify-tmp" \
  --setenv PATH "$R/bin:/usr/bin:/bin" \
  -- /usr/bin/python3 "$P/verify.py" \
  --public-artifact "$R/work/proof-package/public-artifact.cbor" \
  --proof "$R/work/proof-package/proof" \
  --verification-key "$R/work/proof-package/vk"
```

Also test a separately copied and deliberately corrupted proof: `INVALID / PROOF_REJECTED` with exit code `3`, while a valid case returns `VALID` with exit code `0`. Never modify the preserved original. Test malformed public artifacts, version incompatibility, and missing trust material before claiming broader verifier coverage.

## Observed resource envelope and rollback

Single Qube observation, not a production benchmark, upper bound, or guarantee: with `nice -n 10`, CPU affinity `0-3`, and offline `bwrap`, a repeated synthetic proof took approximately **1.00 s / 76,712 KB peak RSS**, and a separate verification **0.10 s / 22,752 KB peak RSS** (GNU `time` measurements include process overhead). The complete disposable tree, including downloaded archives and executables, occupied about **117 MB**; public CRS about **4.3 MB**. Qube at the checkpoint had about **8.2 GiB free in /tmp**, **58 GiB free on /**, **19 GiB available RAM**, and **6.4/8 GiB swap in use**. Re-measure before each execution; stop on resource pressure or interference with other Qube work.

Expected minimized proof output: `manifest.json`, `public-artifact.cbor`, `proof`, `vk`; no `Prover.toml`, raw frame, or witness file. Verification does not imply telemetry truth, source assurance beyond `A0_SYNTHETIC`, time, interval coverage, safety, compliance, publication, or business acceptance. No change to public presentation at `tag.rocsi.eu` is authorized.

**Rollback:** stop any experiment process, then remove only the disposable sandbox directory (never use an unchecked empty or generic path):

```sh
case "$R" in
  /tmp/tag-crypto-synthetic.*) test -d "$R" && rm -rf -- "$R" ;;
  *) echo "Refusing unsafe cleanup target" >&2; exit 2 ;;
esac
```

Confirm no leftover private witness directory, process, socket, download, or scheduled task. The test must be repeatable from scratch without a vendor account or hosted verifier. The network-enabled CRS/tool provisioning is a separate prerequisite; proof and verification themselves must remain offline.
