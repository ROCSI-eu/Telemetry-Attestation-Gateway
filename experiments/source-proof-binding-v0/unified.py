"""QA-only composition; no proof generation, no persistent state."""
import copy
import hashlib
import json
from temporal_gate import TemporalGate, BindingRejected

PINNED_PROOF = "f02f00a061aa12daf46e5644db50a52d20c3759301626ec76c35127ac060337c"
PINNED_VK = "623d47a30e83bb889d0709d452f14e9ca6d02fe2d96de4cb2de486d6e367ccd8"


def public_inputs(digest):
    if not isinstance(digest, bytes) or len(digest) != 32:
        raise BindingRejected("INVALID_DIGEST")
    # Circuit declaration: digest[32], maximum_speed_cm_s, version.
    return json.dumps({"public_inputs": [f"0x{v:064x}" for v in (*digest, 500, 1)]},
                      separators=(",", ":")) + "\n"


class Unified:
    """Sequential fixed-enrollment session. Commit only on proof acceptance."""

    def __init__(self, *, verify, proof: bytes, vk: bytes, **config):
        self._gate = TemporalGate(**config)
        self._verify = verify
        self._proof, self._vk = bytes(proof), bytes(vk)

    def accept(self, capture):
        staged = copy.copy(self._gate)
        digest = staged.accept(capture)
        proof, vk = self._proof, self._vk
        if (hashlib.sha256(proof).hexdigest() != PINNED_PROOF or
                hashlib.sha256(vk).hexdigest() != PINNED_VK):
            raise BindingRejected("UNRECOGNIZED_QA_ARTIFACT")
        # The verifier callback must actually verify these exact bytes and
        # independently reconstructed inputs. A receipt is not a verifier.
        if self._verify(public_inputs(digest), proof, vk) is not True:
            raise BindingRejected("PROOF_NOT_ACCEPTED")
        self._gate = staged
        return digest


def local_bb_verifier(bb_path, crs_path):
    """Use the exact verified local toolchain; no provisioning or proving."""
    import os
    from pathlib import Path
    import subprocess
    import tempfile

    pins = {
        Path(bb_path): "fc9279e32471e036827c911ec9f8106ade987aec91d3e9a55cf4d33ebfb6f2cf",
        Path(crs_path) / "bn254_g1_compressed.dat": "fad8203ae1fd103658d4bb33b2b4cf126a28352b5de4684737cff23cc15fb94b",
        Path(crs_path) / "bn254_g2.dat": "01797bfc4de5a96f0e516a9ea4537d18786dc30cb991aca4274c95822b69c32f",
    }

    def verify(encoded, proof, vk):
        with tempfile.TemporaryDirectory(prefix="tag-unified-") as directory:
            tmp = Path(directory)
            crs = tmp / "crs"
            crs.mkdir()
            for i, (source, expected) in enumerate(pins.items()):
                data = source.read_bytes()
                if hashlib.sha256(data).hexdigest() != expected:
                    raise BindingRejected("UNRECOGNIZED_TOOLCHAIN")
                destination = tmp / "bb" if i == 0 else crs / source.name
                destination.write_bytes(data)
            bb = tmp / "bb"
            bb.chmod(0o700)
            home = tmp / "home"
            home.mkdir()
            env = dict(os.environ, HOME=str(home), XDG_CACHE_HOME=str(home), TMPDIR=str(tmp))
            (tmp / "inputs.json").write_text(encoded)
            (tmp / "proof").write_bytes(proof)
            (tmp / "vk").write_bytes(vk)
            completed = subprocess.run(
                [str(bb), "verify", "-t", "noir-recursive", "-i", str(tmp / "inputs.json"),
                 "-p", str(tmp / "proof"), "-k", str(tmp / "vk"), "-c", str(crs)],
                cwd=tmp, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                timeout=60)
            return completed.returncode == 0
    return verify
