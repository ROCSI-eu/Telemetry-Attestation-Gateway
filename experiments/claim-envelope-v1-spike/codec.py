"""EXPERIMENTAL / SYNTHETIC_ONLY / A0_SYNTHETIC / NOT VALIDATION OR PRODUCTION AUTHORIZATION."""
import hashlib
import hmac
import sys
import unicodedata
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bounded-speed-v0"))
from bounded_speed import _encode_head as head, _read_argument, EncodingError

LABELS = ["EXPERIMENTAL", "SYNTHETIC_ONLY", "A0_SYNTHETIC", "NOT VALIDATION OR PRODUCTION AUTHORIZATION"]
STATEMENT = "tag.experimental.scalar-speed.v1"
SUITE = "tag.experimental.placeholder.v1"
DOMAIN = "tag.synthetic.local"
MEDIA = "application/vnd.tag.placeholder"
MAX_WIRE = 8192
MAX_U32 = 2**32-1
ORDER = ("envelope_version","statement_id","proof_suite","assurance_tier","policy_ref","validity","domain","commitment","nullifier","verification_key_id","public_inputs")
def need(ok):
    if not ok:
        raise EncodingError("MALFORMED")
def uint(x, max_value=2**64-1):
    return type(x) is int and 0 <= x <= max_value
def ascii_id(x):
    return type(x) is str and 0 < len(x) <= 255 and all(33 <= ord(c) <= 126 for c in x)
def enc(x):
    if uint(x): return head(0,x)
    if type(x) is bytes: return head(2,len(x))+x
    if type(x) is str:
        need(unicodedata.normalize("NFC",x)==x)
        b=x.encode("utf-8"); return head(3,len(b))+b
    if type(x) is list: return head(4,len(x))+b"".join(enc(y) for y in x)
    if type(x) is dict:
        need(all(type(k) is str for k in x))
        return head(5,len(x))+b"".join(k+v for k,v in sorted((enc(k),enc(v)) for k,v in x.items()))
    raise EncodingError("MALFORMED")
def read(data, pos=0, depth=0):
    need(depth <= 8 and pos < len(data))
    initial=data[pos]; major=initial>>5
    n,pos=_read_argument(data,pos+1,initial&31)
    if major==0:return n,pos
    if major in (2,3):
        need(n<=MAX_WIRE and pos+n<=len(data))
        b=data[pos:pos+n]
        return (b if major==2 else b.decode("utf-8")),pos+n
    need(major in (4,5) and n<=32)
    if major==4:
        a=[]
        for _ in range(n):
            x,pos=read(data,pos,depth+1); a.append(x)
        return a,pos
    m={}; previous=None
    for _ in range(n):
        start=pos;k,pos=read(data,pos,depth+1); raw=data[start:pos]
        need(type(k) is str and k not in m and (previous is None or previous<raw))
        previous=raw
        m[k],pos=read(data,pos,depth+1)
    return m,pos
def shape(x, keys):
    need(type(x) is dict and set(x)==set(keys))
def b32(x):return type(x) is bytes and len(x)==32
def reference(x):
    shape(x,("id","version","digest"))
    need(ascii_id(x["id"]) and uint(x["version"],MAX_U32) and b32(x["digest"]))
def decode(data):
    need(type(data) is bytes and 0<len(data)<=MAX_WIRE)
    x,p=read(data)
    need(p==len(data) and enc(x)==data)
    need(type(x) is dict)
    required=set(ORDER)|{"proof"}
    need(set(x) in (required,required|{"ledger_receipt"}))
    v=x["envelope_version"]
    need(type(v) is list and len(v)==2 and all(uint(i,MAX_U32) for i in v))
    need(all(ascii_id(x[k]) for k in ("statement_id","proof_suite","domain")))
    need(uint(x["assurance_tier"],255))
    reference(x["policy_ref"]); reference(x["verification_key_id"])
    shape(x["validity"],("not_before","not_after"))
    lo,hi=x["validity"]["not_before"],x["validity"]["not_after"]
    need(uint(lo) and uint(hi) and lo<hi)
    need(b32(x["commitment"]) and b32(x["nullifier"]))
    shape(x["public_inputs"],("maximum_speed_cm_s",))
    need(uint(x["public_inputs"]["maximum_speed_cm_s"],MAX_U32))
    p=x["proof"]
    need(type(p) is dict and p.get("kind") in ("attached","referenced"))
    if p["kind"]=="attached":
        shape(p,("kind","content_type","bytes"));need(ascii_id(p["content_type"]) and type(p["bytes"]) is bytes and 0<len(p["bytes"])<=1024)
    else:
        shape(p,("kind","content_type","uri","digest","size"));need(ascii_id(p["content_type"]) and ascii_id(p["uri"]) and b32(p["digest"]) and uint(p["size"]) and p["size"]>0)
    if "ledger_receipt" in x:
        r=x["ledger_receipt"];shape(r,("ledger_id","transaction_id","recorded_at","payload_digest","finality","proof"))
        need(all(ascii_id(r[k]) for k in ("ledger_id","transaction_id","finality")) and uint(r["recorded_at"]) and b32(r["payload_digest"]) and type(r["proof"]) is bytes and 0<len(r["proof"])<=1024)
    return x
def supported(x):
    return (x["envelope_version"]==[1,0] and x["statement_id"]==STATEMENT and x["proof_suite"]==SUITE and x["assurance_tier"]==0 and x["proof"]["kind"]=="attached" and x["proof"]["content_type"]==MEDIA and "ledger_receipt" not in x)
def inputs(x):
    return enc([x[k] for k in ORDER])
def token(x):
    return b"PLACEHOLDER:"+hashlib.sha256(b"TAG-SYNTHETIC-INPUTS-V1\x00"+inputs(x)).digest()
def digest(s):return hashlib.sha256(s).digest()
POLICY=digest(b"TAG-TEST-POLICY-V1")
KEY=digest(b"TAG-TEST-KEY-V1")
def evaluate(data, scenario):
    required={"decision_time","artifacts_available","policy_allows","revocation","assurance","already_seen","store_available"}
    if (type(scenario) is not dict or set(scenario) not in (required,required|{"optional_publication_unavailable"})
        or any(type(scenario[k]) is not bool for k in ("artifacts_available","policy_allows","already_seen","store_available"))
        or type(scenario.get("optional_publication_unavailable",False)) is not bool
        or (scenario["decision_time"] is not None and not uint(scenario["decision_time"]))
        or scenario["revocation"] not in ("revoked","temporarily_unverifiable","not_revoked")
        or scenario["assurance"] not in ("insufficient","temporarily_unverifiable","sufficient")):
        raise ValueError("INVALID_SYNTHETIC_SCENARIO")
    result={"labels":LABELS,"verification":"NOT_PERFORMED","actual_crypto":"NOT_CHECKED","mode":"NON_CRYPTOGRAPHIC_PLACEHOLDER","simulated_result":None}
    try:x=decode(data)
    except (EncodingError,UnicodeError,TypeError,ValueError):
        result["admission"]="malformed";return result
    if not supported(x):
        result["admission"]="unsupported";return result
    result.update(admission="structurally_accepted",public_input_hex=inputs(x).hex())
    # Scenario is trusted only as an artificial test harness input. No external
    # artifacts, clock authority, proof, key registry or replay store are evaluated.
    pol=x["policy_ref"];key=x["verification_key_id"]
    binding=(x["domain"]==DOMAIN and pol["id"]=="test-policy" and pol["version"]==1 and hmac.compare_digest(pol["digest"],POLICY) and key["id"]=="test-key" and key["version"]==1 and hmac.compare_digest(key["digest"],KEY) and hmac.compare_digest(x["proof"]["bytes"],token(x)))
    e="invalid" if not binding else ("temporarily_unverifiable" if not scenario["artifacts_available"] else "valid")
    t=scenario["decision_time"];w=x["validity"]
    f="temporarily_unverifiable" if t is None else ("not_yet_valid" if t<w["not_before"] else ("expired" if t>=w["not_after"] else "current"))
    p="rejected" if not scenario["policy_allows"] else ("accepted" if scenario["artifacts_available"] else "temporarily_unverifiable")
    r=scenario["revocation"]
    a=scenario["assurance"]
    replay="replayed" if scenario["already_seen"] else ("accepted" if scenario["store_available"] and e=="valid" and p=="accepted" and f=="current" and r=="not_revoked" and a=="sufficient" else "temporarily_unverifiable")
    negative=p=="rejected" or f in ("not_yet_valid","expired") or r=="revoked" or replay=="replayed" or a=="insufficient"
    positive=p=="accepted" and f=="current" and r=="not_revoked" and replay=="accepted" and a=="sufficient"
    disposition=({"invalid":"cryptographically_invalid","temporarily_unverifiable":"temporarily_unverifiable"}[e] if e!="valid" else ("rejected" if negative else ("accepted" if positive else "temporarily_unverifiable")))
    result["simulated_result"]={"envelope_evaluation":e,"policy_acceptance":p,"freshness":f,"revocation":r,"replay":replay,"assurance":{"declared_tier":0,"effective_tier":0 if a in ("sufficient","insufficient") else "unavailable","tier_sufficiency":a},"service_disposition":disposition,"decision_time":t}
    sim=result["simulated_result"]
    sim["reason_codes"]=[name.upper()+":"+value.upper() for name,value in (("envelope",e),("policy",p),("freshness",f),("revocation",r),("replay",replay),("assurance",a))]
    if scenario.get("optional_publication_unavailable",False):
        sim["publication"]={"requirement":"optional","receipt_verification":"temporarily_unverifiable","finality":"temporarily_unverifiable"}
        sim["reason_codes"].append("PUBLICATION:OPTIONAL_UNAVAILABLE")
    return result
