"""EXPERIMENTAL / SYNTHETIC_ONLY / A0_SYNTHETIC / NOT VALIDATION OR PRODUCTION AUTHORIZATION.
Independent byte-level checker: no reference codec, shared encoder or verifier imports.
Same-author AI-assisted implementation, not independent review.
"""
import hashlib
import unicodedata

MARKS=["EXPERIMENTAL","SYNTHETIC_ONLY","A0_SYNTHETIC","NOT VALIDATION OR PRODUCTION AUTHORIZATION"]
FIELDS="envelope_version statement_id proof_suite assurance_tier policy_ref validity domain commitment nullifier verification_key_id public_inputs".split()
class Malformed(ValueError): pass
def check(condition):
    if not condition: raise Malformed()
class Cursor:
    def __init__(self, data): self.rest=data
    def take(self,n):
        check(0<=n<=len(self.rest))
        b,self.rest=self.rest[:n],self.rest[n:]
        return b
    def value(self,depth=0):
        check(depth<=8)
        start=self.rest
        tag=self.take(1)[0]; major,small=divmod(tag,32)
        if small>=24:
            check(small<=27)
            width=1<<(small-24)
            size=int.from_bytes(self.take(width),"big")
            check(size >= {1:24,2:256,4:65536,8:4294967296}[width])
        else: size=small
        if major==0: value=size
        elif major==2: value=self.take(size)
        elif major==3:
            value=self.take(size).decode("utf-8")
            check(unicodedata.is_normalized("NFC",value))
        elif major==4:
            check(size<=32)
            value=[self.value(depth+1)[0] for _ in range(size)]
        elif major==5:
            check(size<=32)
            value={};last=b""
            for _ in range(size):
                k,raw=self.value(depth+1)
                check(isinstance(k,str) and raw>last and k not in value)
                last=raw
                value[k]=self.value(depth+1)[0]
        else: raise Malformed()
        return value,start[:len(start)-len(self.rest)]
def fields(obj, names):
    check(isinstance(obj,dict) and sorted(obj)==sorted(names.split()))
def textid(s):
    check(isinstance(s,str) and 1<=len(s)<=255 and s.isascii() and all("!"<=c<="~" for c in s))
def number(n,top=2**64-1):check(type(n) is int and 0<=n<=top)
def blob(b,n):check(isinstance(b,bytes) and len(b)==n)
def payload(b):check(isinstance(b,bytes) and 1<=len(b)<=1024)
def ref(obj):
    fields(obj,"id version digest");textid(obj["id"]);number(obj["version"],2**32-1);blob(obj["digest"],32)
def assess(data,s):
    required="decision_time artifacts_available policy_allows revocation assurance already_seen store_available".split()
    if not isinstance(s,dict) or sorted(s) not in (sorted(required),sorted(required+["optional_publication_unavailable"])):
        raise ValueError("INVALID_SYNTHETIC_SCENARIO")
    if (not all(type(s[k]) is bool for k in ("artifacts_available","policy_allows","already_seen","store_available"))
        or type(s.get("optional_publication_unavailable",False)) is not bool
        or (s["decision_time"] is not None and (type(s["decision_time"]) is not int or not 0<=s["decision_time"]<2**64))
        or s["revocation"] not in ("revoked","temporarily_unverifiable","not_revoked")
        or s["assurance"] not in ("insufficient","temporarily_unverifiable","sufficient")):
        raise ValueError("INVALID_SYNTHETIC_SCENARIO")
    out={"labels":MARKS,"verification":"NOT_PERFORMED","actual_crypto":"NOT_CHECKED","mode":"NON_CRYPTOGRAPHIC_PLACEHOLDER","simulated_result":None}
    try:
        check(isinstance(data,bytes) and 0<len(data)<=8192)
        c=Cursor(data);x,_=c.value();check(not c.rest)
        check(isinstance(x,dict))
        names=FIELDS+["proof"]+(["ledger_receipt"] if "ledger_receipt" in x else [])
        fields(x," ".join(names))
        v=x["envelope_version"];check(isinstance(v,list) and len(v)==2)
        for n in v:number(n,2**32-1)
        for name in ("statement_id","proof_suite","domain"):textid(x[name])
        number(x["assurance_tier"],255)
        ref(x["policy_ref"]);ref(x["verification_key_id"])
        w=x["validity"];fields(w,"not_before not_after")
        number(w["not_before"]);number(w["not_after"]);check(w["not_before"]<w["not_after"])
        blob(x["commitment"],32);blob(x["nullifier"],32)
        fields(x["public_inputs"],"maximum_speed_cm_s");number(x["public_inputs"]["maximum_speed_cm_s"],2**32-1)
        p=x["proof"];check(isinstance(p,dict))
        if p.get("kind")=="attached":
            fields(p,"kind content_type bytes");payload(p["bytes"])
        elif p.get("kind")=="referenced":
            fields(p,"kind content_type uri digest size");textid(p["uri"]);blob(p["digest"],32);number(p["size"]);check(p["size"]>0)
        else:raise Malformed()
        textid(p["content_type"])
        if "ledger_receipt" in x:
            r=x["ledger_receipt"];fields(r,"ledger_id transaction_id recorded_at payload_digest finality proof")
            for k in ("ledger_id","transaction_id","finality"):textid(r[k])
            number(r["recorded_at"]);blob(r["payload_digest"],32);payload(r["proof"])
    except (Malformed,UnicodeError):
        out["admission"]="malformed";return out
    if (v,x["statement_id"],x["proof_suite"],x["assurance_tier"],p["kind"],p["content_type"],"ledger_receipt" in x)!=([1,0],"tag.experimental.scalar-speed.v1","tag.experimental.placeholder.v1",0,"attached","application/vnd.tag.placeholder",False):
        out["admission"]="unsupported";return out
    # Reconstruct array from canonical value slices, not from an encoder or
    # supplied public inputs. The map has a one-byte header (12 fields).
    c=Cursor(data);check(c.take(1)==b"\xac")
    raw={}
    for _ in range(12):
        k=c.value()[0];raw[k]=c.value()[1]
    seq=b"\x8b"+b"".join(raw[k] for k in FIELDS)
    out.update(admission="structurally_accepted",public_input_hex=seq.hex())
    sha=lambda b:hashlib.sha256(b).digest()
    good=(x["domain"]=="tag.synthetic.local" and x["policy_ref"]=={"id":"test-policy","version":1,"digest":sha(b"TAG-TEST-POLICY-V1")} and x["verification_key_id"]=={"id":"test-key","version":1,"digest":sha(b"TAG-TEST-KEY-V1")} and p["bytes"]==b"PLACEHOLDER:"+sha(b"TAG-SYNTHETIC-INPUTS-V1\x00"+seq))
    e="valid" if good and s["artifacts_available"] else "temporarily_unverifiable" if good else "invalid"
    t=s["decision_time"]
    f="temporarily_unverifiable"
    if t is not None:
        f=next(k for yes,k in [(t<w["not_before"],"not_yet_valid"),(t>=w["not_after"],"expired"),(True,"current")] if yes)
    pol={False:"rejected",True:("accepted" if s["artifacts_available"] else "temporarily_unverifiable")}[s["policy_allows"]]
    rev=s["revocation"];a=s["assurance"]
    states=(e,pol,f,rev,a)
    replay="temporarily_unverifiable"
    if s["already_seen"]:replay="replayed"
    elif s["store_available"] and states==("valid","accepted","current","not_revoked","sufficient"):replay="accepted"
    if e=="invalid":disp="cryptographically_invalid"
    elif e!="valid":disp="temporarily_unverifiable"
    elif set((pol,f,rev,a,replay)) & {"rejected","expired","not_yet_valid","revoked","insufficient","replayed"}:disp="rejected"
    elif (pol,f,rev,a,replay)==("accepted","current","not_revoked","sufficient","accepted"):disp="accepted"
    else:disp="temporarily_unverifiable"
    out["simulated_result"]={"envelope_evaluation":e,"policy_acceptance":pol,"freshness":f,"revocation":rev,"replay":replay,"assurance":{"declared_tier":0,"effective_tier":0 if a in ("sufficient","insufficient") else "unavailable","tier_sufficiency":a},"service_disposition":disp,"decision_time":t}
    simulated=out["simulated_result"]
    simulated["reason_codes"]=[f"{k}:{v.upper()}" for k,v in zip(("ENVELOPE","POLICY","FRESHNESS","REVOCATION","REPLAY","ASSURANCE"),(e,pol,f,rev,replay,a))]
    if s.get("optional_publication_unavailable",False):
        simulated["publication"]={"requirement":"optional","receipt_verification":"temporarily_unverifiable","finality":"temporarily_unverifiable"}
        simulated["reason_codes"]+=["PUBLICATION:OPTIONAL_UNAVAILABLE"]
    return out


def check_corpus(path):
    import json
    from pathlib import Path
    data=json.loads(Path(path).read_text())
    check(data["labels"]==MARKS and data["profile"]=="PROVISIONAL_V1_PLACEHOLDER")
    names=set()
    for case in data["cases"]:
        check(case["name"] not in names)
        names.add(case["name"])
        check(assess(bytes.fromhex(case["wire_hex"]),case["scenario"])==case["expected"])
        check(case["expected"]["actual_crypto"]=="NOT_CHECKED")
        check(case["expected"]["verification"]=="NOT_PERFORMED")
    check(bool(names))
    print("INDEPENDENT_CORPUS_PASS",len(names))
if __name__=="__main__":
    from pathlib import Path
    check_corpus(Path(__file__).with_name("vectors.json"))
