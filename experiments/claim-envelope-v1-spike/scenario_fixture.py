"""EXPERIMENTAL / SYNTHETIC_ONLY / A0_SYNTHETIC / NOT VALIDATION OR PRODUCTION AUTHORIZATION.
Deterministic public test fixture only, no real telemetry or proof."""
import copy
import hashlib
import codec
import vectors
from binding_adapter import openings, status_mac, scope_for, status_bytes
from binding_reference import authorized_digest, parser
from trusted_time import receipt_mac
from test_temporal_gate import CONFIG, sample

TIME=bytes(reversed(range(32)))
STATUS=b"S"*32
SECRET=b"X"*32
NONCE=b"N"*32
NOW=21000
def status(revoked=False):
    return {"scope":scope_for(CONFIG),"policy_digest":codec.POLICY.hex(),"key_digest":codec.KEY.hex(),"issued_ms":20000,"expires_ms":30000,"revoked":revoked,"maximum_speed_cm_s":500}
def pin(s):return hashlib.sha256(status_bytes(s)).hexdigest()
def fixture(c=None,nonce=NONCE,ingress=20000):
    c=sample() if c is None else c
    x=vectors.envelope()
    x["validity"]={"not_before":ingress//1000,"not_after":ingress//1000+10}
    clean=copy.deepcopy(c);clean["test_trust_store"]={CONFIG["enrollment"]["slot"]:CONFIG["verifier_key_hex"]}
    speed=parser.evaluate_capture(clean)["speed_cm_s"]
    x["commitment"],x["nullifier"]=openings(x,authorized_digest(c,**CONFIG),speed,nonce,SECRET,CONFIG["requested_alias"])
    x["proof"]["bytes"]=codec.token(x)
    return codec.enc(x),c,{"ingress_ms":ingress,"mac":receipt_mac(TIME,scope_for(CONFIG),c,ingress)},nonce

def at_speed(speed,stamp,boot):
    c=sample(stamp,boot)
    for e in c["events"]:
        frame=bytearray.fromhex(e["frame_hex"])
        if int.from_bytes(frame[7:10],"little")==33:
            n=frame[1]
            frame[30:32]=speed.to_bytes(2,"little",signed=True)
            frame[32:34]=b"\x00\x00"
            frame[10+n:12+n]=parser.mavlink_crc(bytes(frame[1:10]),bytes(frame[10:10+n]),104).to_bytes(2,"little")
            frame[-6:]=hashlib.sha256(bytes(range(32))+frame[:-6]).digest()[:6]
            e["frame_hex"]=frame.hex()
    return c
