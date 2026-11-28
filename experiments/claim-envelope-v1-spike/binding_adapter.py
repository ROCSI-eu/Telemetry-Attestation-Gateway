"""EXPERIMENTAL / SYNTHETIC_ONLY / A0_SYNTHETIC / NOT VALIDATION OR PRODUCTION AUTHORIZATION.
Synthetic local composition. No proof verification callback or runtime dispatch.
"""
import copy
import hashlib
import hmac
import json
import os
import stat
import sys
from pathlib import Path
import codec
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"source-proof-binding-v0"))
from temporal_gate import TemporalGate, BindingRejected
from binding_reference import authorized_digest, parser
from trusted_time import TrustedTimeUnified, valid_ms
from persistent_unified import PersistentUnified, canonical

MAX_RECORDS=64
MAX_STATE=16384
# This adapter is for the canonical public fixture source only, not a
# generic MAVLink receiver. Other test authorities remain verifier-owned.
FIXTURE_SOURCE_KEY=bytes(range(32))
FIXTURE_ALIAS="qa-synthetic-source"
def bounded_capture(capture):
    required={"events","decision_received_at_ms","max_age_ms"}
    optional={"name","test_trust_store","expected_status","expected_speed_cm_s","expected_trust"}
    require(type(capture) is dict and required<=set(capture)<=required|optional,"CAPTURE_SHAPE")
    require(valid_ms(capture["decision_received_at_ms"]) and valid_ms(capture["max_age_ms"]),"CAPTURE_SHAPE")
    events=capture["events"]
    require(type(events) is list and 1<=len(events)<=8,"CAPTURE_BOUND")
    for event in events:
        require(type(event) is dict and set(event)=={"received_at_ms","frame_hex"} and valid_ms(event["received_at_ms"]),"CAPTURE_SHAPE")
        frame=event["frame_hex"]
        require(type(frame) is str and 0<len(frame)<=560 and len(frame)%2==0 and all(c in "0123456789abcdefABCDEF" for c in frame),"CAPTURE_BOUND")
    for k in ("name","expected_status","expected_trust"):
        if k in capture:require(type(capture[k]) is str and len(capture[k])<=128 and capture[k].isascii(),"CAPTURE_SHAPE")
    if "expected_speed_cm_s" in capture:require(codec.uint(capture["expected_speed_cm_s"],codec.MAX_U32),"CAPTURE_SHAPE")
    # Ingress MAC already excludes the caller-owned trust store. Do not copy
    # or consult that potentially unbounded, untrusted object.
    return copy.deepcopy({k:v for k,v in capture.items() if k!="test_trust_store"})

def reject(reason):raise BindingRejected(reason)
def require(ok,reason):
    if not ok:reject(reason)
def mac(key,tag,parts):
    return hmac.digest(key,tag+b"\x00"+codec.enc(parts),"sha256")
def scope_for(config):
    e=config["enrollment"]
    return hashlib.sha256(canonical(["TAG-SYNTHETIC-BINDING-V1",codec.DOMAIN,codec.STATEMENT,codec.POLICY.hex(),e["slot"],e["alias"],e["key_fingerprint"]])).hexdigest()
def status_bytes(status):
    return canonical(status)
def status_mac(key,status):
    return hmac.digest(key,b"TAG-SYNTHETIC-STATUS-V1\x00"+status_bytes(status),"sha256").hex()
def openings(x, digest, speed, nonce, source_secret, alias):
    require(type(nonce) is bytes and len(nonce)==32 and type(source_secret) is bytes and len(source_secret)==32,"OPENING_INVALID")
    source=mac(source_secret,b"TAG-SYNTHETIC-SOURCE",[alias])
    # Explicit non-circuit candidate: domain-separated HMAC, nonce kept private.
    binding=[x["envelope_version"],x["statement_id"],x["proof_suite"],x["assurance_tier"],x["policy_ref"],x["validity"],x["domain"],x["verification_key_id"],x["public_inputs"],digest,speed,source]
    commitment=mac(nonce,b"TAG-SYNTHETIC-COMMITMENT-V1",binding)
    nullifier=mac(nonce,b"TAG-SYNTHETIC-NULLIFIER-V1",[source,x["domain"],x["policy_ref"]["digest"],x["statement_id"]])
    return commitment,nullifier

class BindingSession:
    # Reuse tested lock/atomic writer and authenticated ingress-time check;
    # deliberately do not subclass Unified or expose its verifier callback.
    _locked=PersistentUnified._locked
    _write=PersistentUnified._write
    _check_reference=TrustedTimeUnified._check_reference
    def __init__(self, *, state_dir, config, time_key, status_key, source_secret, status_pin, clock, initialize=False):
        self._directory=Path(state_dir).absolute()
        self._state=self._directory/"state.json"
        require(type(config) is dict and set(config)=={"verifier_key_hex","enrollment","requested_alias"},"SOURCE_CONFIG_INVALID")
        e=config["enrollment"]
        require(type(e) is dict and set(e)=={"slot","alias","active","key_fingerprint"} and config["verifier_key_hex"]==FIXTURE_SOURCE_KEY.hex() and config["requested_alias"]==FIXTURE_ALIAS,"SOURCE_CONFIG_INVALID")
        self._config=copy.deepcopy(config)
        source_key=FIXTURE_SOURCE_KEY
        require(type(e) is dict and e.get("active") is True and e.get("slot")=="1:1:7" and e.get("alias")==config["requested_alias"] and e.get("key_fingerprint")==hashlib.sha256(source_key).hexdigest(),"SOURCE_CONFIG_INVALID")
        keys=(source_key,time_key,status_key,source_secret)
        require(all(type(k) is bytes and len(k)==32 for k in keys) and len(set(keys))==4,"KEY_SEPARATION")
        require(type(status_pin) is str and len(status_pin)==64 and all(c in "0123456789abcdef" for c in status_pin) and callable(clock),"STATUS_CONFIG_INVALID")
        self._scope=scope_for(config)
        self._authority_pin=hashlib.sha256(canonical([hashlib.sha256(k).hexdigest() for k in keys])).hexdigest()
        self._time_key=time_key;self._status_key=status_key;self._source_secret=source_secret
        self._status_pin=status_pin;self._decision_clock=clock;self._max_age=10000
        # The exact decision clock is frozen for each call; avoid shared mutable clock.
        self._clock=clock
        with self._locked():
            if initialize:
                require(not os.path.lexists(self._state),"STATE_ALREADY_EXISTS")
                self._write({"watermark":None,"nullifiers":[]})
            self._read()
    def _encode(self,record):
        payload={"version":1,"scope":self._scope,"authority_pin":self._authority_pin,"record":record}
        return canonical({"payload":payload,"checksum":hashlib.sha256(canonical(payload)).hexdigest()})+b"\n"
    def _read(self):
        try:
            fd=os.open(self._state,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
            with os.fdopen(fd,"rb") as f:
                st=os.fstat(f.fileno())
                require(stat.S_ISREG(st.st_mode) and st.st_uid==os.getuid() and stat.S_IMODE(st.st_mode)==0o600 and st.st_nlink==1 and st.st_size<=MAX_STATE,"STATE_UNSAFE")
                raw=f.read(MAX_STATE+1)
            obj=json.loads(raw);rec=obj["payload"]["record"]
            require(type(rec) is dict and set(rec)=={"watermark","nullifiers"},"STATE_INVALID")
            w=rec["watermark"];n=rec["nullifiers"]
            require(w is None or (type(w) is list and len(w)==2 and type(w[0]) is int and type(w[1]) is int and 0<=w[0]<2**48 and 0<=w[1]<2**32),"STATE_INVALID")
            require(type(n) is list and len(n)<=MAX_RECORDS and all(type(i) is str and len(i)==64 and all(c in "0123456789abcdef" for c in i) for i in n) and n==sorted(set(n)) and ((w is None)==(not n)),"STATE_INVALID")
            require(hmac.compare_digest(raw,self._encode(rec)),"STATE_INVALID")
            return rec
        except (OSError,ValueError,TypeError,KeyError,OverflowError,RecursionError):
            reject("STATE_MISSING_CORRUPT_OR_INCOMPATIBLE")
    def _status(self,status,signature,now):
        require(type(status) is dict and set(status)=={"scope","policy_digest","key_digest","issued_ms","expires_ms","revoked","maximum_speed_cm_s"},"STATUS_INVALID")
        require(status["scope"]==self._scope and status["policy_digest"]==codec.POLICY.hex() and status["key_digest"]==codec.KEY.hex() and type(status["revoked"]) is bool and type(status["maximum_speed_cm_s"]) is int and status["maximum_speed_cm_s"]==500,"STATUS_SCOPE")
        require(valid_ms(status["issued_ms"]) and valid_ms(status["expires_ms"]) and status["issued_ms"]<=now<status["expires_ms"],"STATUS_STALE_OR_FUTURE")
        require(type(signature) is str and len(signature)==64 and signature.isascii() and hmac.compare_digest(signature,status_mac(self._status_key,status)),"STATUS_AUTH")
        require(hmac.compare_digest(hashlib.sha256(status_bytes(status)).hexdigest(),self._status_pin),"STATUS_PIN")
        require(not status["revoked"],"REVOKED")
    def accept(self,wire,capture,receipt,nonce,status,signature):
        # No raw/private fields returned. The accepted label is explicitly local
        # mock contract admission, never canonical service acceptance.
        out={"labels":codec.LABELS,"mode":"SYNTHETIC_BINDING_PLACEHOLDER","actual_crypto":"NOT_CHECKED","verification":"NOT_PERFORMED","admission":"HOLD","replay_commit":"NOT_PERFORMED","publication":"NOT_PERFORMED","relying_party_decision":"NOT_MADE","command_path":"NONE"}
        try:
            require(type(wire) is bytes and 0<len(wire)<=codec.MAX_WIRE,"ENVELOPE_MALFORMED")
            capture=bounded_capture(capture)
            require(type(receipt) is dict and set(receipt)=={"ingress_ms","mac"} and valid_ms(receipt["ingress_ms"]) and type(receipt["mac"]) is str and len(receipt["mac"])==64,"INVALID_TIME_REFERENCE")
            require(type(status) is dict and set(status)=={"scope","policy_digest","key_digest","issued_ms","expires_ms","revoked","maximum_speed_cm_s"} and all(type(status[k]) is str and len(status[k])==64 for k in ("scope","policy_digest","key_digest")) and all(valid_ms(status[k]) for k in ("issued_ms","expires_ms")) and type(status["revoked"]) is bool and codec.uint(status["maximum_speed_cm_s"],codec.MAX_U32),"STATUS_INVALID")
            receipt,status=dict(receipt),dict(status)
            with self._locked():
                rec=self._read()
                try:now=self._decision_clock()
                except Exception:reject("DECISION_CLOCK_UNAVAILABLE")
                require(valid_ms(now),"DECISION_CLOCK_UNAVAILABLE")
                self._status(status,signature,now)
                try:x=codec.decode(wire)
                except (ValueError,TypeError,UnicodeError):reject("ENVELOPE_MALFORMED")
                require(codec.supported(x),"ENVELOPE_UNSUPPORTED")
                require(x["domain"]==codec.DOMAIN and x["policy_ref"]=={"id":"test-policy","version":1,"digest":codec.POLICY} and x["verification_key_id"]=={"id":"test-key","version":1,"digest":codec.KEY} and x["public_inputs"]["maximum_speed_cm_s"]==status["maximum_speed_cm_s"],"POLICY_BINDING")
                # Reuse prior authenticated ingress-time gate without a proof path.
                stage=copy.copy(self);stage._clock=lambda:now
                capture=stage._check_reference(capture,receipt=receipt)
                ingress=receipt["ingress_ms"]
                require(ingress%1000==0 and x["validity"]=={"not_before":ingress//1000,"not_after":ingress//1000+10},"VALIDITY_BINDING")
                gate=TemporalGate(**self._config);gate._watermark=None if rec["watermark"] is None else tuple(rec["watermark"])
                digest=gate.accept(capture)
                require(sum(int.from_bytes(bytes.fromhex(e["frame_hex"])[7:10],"little")==33 for e in capture["events"])==1,"PRIMARY_COUNT")
                cleaned=copy.deepcopy(capture)
                cleaned["test_trust_store"]={self._config["enrollment"]["slot"]:self._config["verifier_key_hex"]}
                normalized=parser.evaluate_capture(cleaned)
                require(normalized["status"]=="NORMALIZED","NORMALIZATION")
                speed=normalized["speed_cm_s"]
                require(speed<=status["maximum_speed_cm_s"],"PREDICATE_NOT_SATISFIED")
                c,n=openings(x,digest,speed,nonce,self._source_secret,self._config["requested_alias"])
                require(hmac.compare_digest(c,x["commitment"]) and hmac.compare_digest(n,x["nullifier"]),"OPENING_BINDING")
                require(hmac.compare_digest(codec.token(x),x["proof"]["bytes"]),"PLACEHOLDER_MISMATCH")
                require(n.hex() not in rec["nullifiers"],"NULLIFIER_REPLAY")
                require(len(rec["nullifiers"])<MAX_RECORDS,"STATE_CAPACITY")
                # Failure after atomic replacement can leave committed state.
                # Never report NOT_PERFORMED once write has begun.
                out["replay_commit"]="UNKNOWN"
                self._write({"watermark":list(gate._watermark),"nullifiers":sorted(rec["nullifiers"]+[n.hex()])})
                out.update(admission="SYNTHETIC_CONTRACT_ACCEPTED",replay_commit="LOCAL_ATOMIC_COMMIT",source_binding="TEST_SIGNATURE_AND_PRIVATE_OPENING_MATCH",freshness="TEST_INGRESS_CURRENT",policy="TEST_STATUS_MATCH")
        except BindingRejected as exc:
            out["reason"]=str(exc)
        except OSError:
            out["reason"]="STATE_IO_UNAVAILABLE"
        except (ValueError,TypeError,KeyError,OverflowError,RecursionError):
            out["reason"]="MALFORMED_SYNTHETIC_INPUT"
        return out
