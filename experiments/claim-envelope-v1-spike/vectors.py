"""EXPERIMENTAL / SYNTHETIC_ONLY / A0_SYNTHETIC / NOT VALIDATION OR PRODUCTION AUTHORIZATION."""
import copy
import json
from pathlib import Path
import codec as c
from independent_checker import assess
BASE={"decision_time":100,"artifacts_available":True,"policy_allows":True,"revocation":"not_revoked","assurance":"sufficient","already_seen":False,"store_available":True}
def envelope():
    x={"envelope_version":[1,0],"statement_id":c.STATEMENT,"proof_suite":c.SUITE,"assurance_tier":0,"policy_ref":{"id":"test-policy","version":1,"digest":c.POLICY},"validity":{"not_before":100,"not_after":110},"domain":c.DOMAIN,"commitment":b"C"*32,"nullifier":b"N"*32,"verification_key_id":{"id":"test-key","version":1,"digest":c.KEY},"public_inputs":{"maximum_speed_cm_s":500},"proof":{"kind":"attached","content_type":c.MEDIA,"bytes":b"x"}}
    x["proof"]["bytes"]=c.token(x)
    return x
def cases():
    x=envelope();wire=c.enc(x)
    def row(name,data,admission,e=None,disp=None,**change):
        return name,data,dict(BASE,**change),admission,e,disp
    yield row("positive_lower_endpoint",wire,"structurally_accepted","valid","accepted")
    yield row("just_after_lower",wire,"structurally_accepted","valid","accepted",decision_time=101)
    yield row("just_before_upper",wire,"structurally_accepted","valid","accepted",decision_time=109)
    yield row("upper_endpoint",wire,"structurally_accepted","valid","rejected",decision_time=110)
    yield row("after_upper",wire,"structurally_accepted","valid","rejected",decision_time=111)
    yield row("before_lower",wire,"structurally_accepted","valid","rejected",decision_time=99)
    yield row("clock_missing",wire,"structurally_accepted","valid","temporarily_unverifiable",decision_time=None)
    yield row("policy_rejected",wire,"structurally_accepted","valid","rejected",policy_allows=False)
    yield row("artifact_unavailable",wire,"structurally_accepted","temporarily_unverifiable","temporarily_unverifiable",artifacts_available=False)
    yield row("revoked",wire,"structurally_accepted","valid","rejected",revocation="revoked")
    yield row("revocation_unavailable",wire,"structurally_accepted","valid","temporarily_unverifiable",revocation="temporarily_unverifiable")
    yield row("replayed",wire,"structurally_accepted","valid","rejected",already_seen=True)
    yield row("store_unavailable",wire,"structurally_accepted","valid","temporarily_unverifiable",store_available=False)
    yield row("insufficient",wire,"structurally_accepted","valid","rejected",assurance="insufficient")
    yield row("assurance_unavailable",wire,"structurally_accepted","valid","temporarily_unverifiable",assurance="temporarily_unverifiable")
    yield row("optional_publication_unavailable",wire,"structurally_accepted","valid","accepted",optional_publication_unavailable=True)
    yield row("policy_negative_vs_unavailable",wire,"structurally_accepted","temporarily_unverifiable","temporarily_unverifiable",policy_allows=False,artifacts_available=False)
    yield row("context_collision",wire,"structurally_accepted","valid","rejected",decision_time=110,store_available=False)
    for name,value in [("domain","tag.wrong"),("commitment",b"D"*32),("nullifier",b"M"*32),("policy_ref",dict(x["policy_ref"],digest=b"P"*32)),("verification_key_id",dict(x["verification_key_id"],digest=b"K"*32)),("public_inputs",{"maximum_speed_cm_s":501}),("validity",{"not_before":99,"not_after":110}),("proof",dict(x["proof"],bytes=b"bad"))]:
        y=dict(x,**{name:value})
        yield row("mutate_"+name,c.enc(y),"structurally_accepted","invalid","cryptographically_invalid",artifacts_available=False)
    for name,value in [("envelope_version",[2,0]),("statement_id","tag.unknown"),("proof_suite","tag.unknown"),("assurance_tier",6),("proof",{"kind":"referenced","content_type":c.MEDIA,"uri":"fixture:unavailable","digest":b"R"*32,"size":12})]:
        yield row("unsupported_"+name,c.enc(dict(x,**{name:value})),"unsupported")
    for name,value in [("validity",{"not_before":100,"not_after":100}),("public_inputs",{"maximum_speed_cm_s":2**32}),("assurance_tier",256),("commitment",b"C"),("domain","bad domain"),("proof",dict(x["proof"],extra=1)),("private_speed",499)]:
        yield row("malformed_"+name,c.enc(dict(x,**{name:value})),"malformed")
    yield row("inverted_window",c.enc(dict(x,validity={"not_before":110,"not_after":100})),"malformed")
    yield row("unsupported_minor",c.enc(dict(x,envelope_version=[1,1])),"unsupported")
    yield row("unsupported_tier_1",c.enc(dict(x,assurance_tier=1)),"unsupported")
    yield row("unsupported_media",c.enc(dict(x,proof=dict(x["proof"],content_type="application/unknown"))),"unsupported")
    yield row("unsupported_receipt",c.enc(dict(x,ledger_receipt={"ledger_id":"mock","transaction_id":"test","recorded_at":100,"payload_digest":b"L"*32,"finality":"pending","proof":b"x"})),"unsupported")
    yield row("nonminimal_integer",wire.replace(c.enc("assurance_tier")+b"\x00",c.enc("assurance_tier")+b"\x18\x00",1),"malformed")
    # Replace the domain text with valid UTF-8 but non-NFC text using raw bytes.
    yield row("non_nfc_text",wire.replace(c.enc(c.DOMAIN),b"\x63e\xcc\x81",1),"malformed")
    yield row("oversize_wire",b"\x00"*8193,"malformed")
    y=dict(x);del y["proof"]
    yield row("missing_proof",c.enc(y),"malformed")
    yield row("trailing",wire+b"\x00","malformed")
    yield row("truncated",wire[:-1],"malformed")
    yield row("nonminimal_map",b"\xb8\x0c"+wire[1:],"malformed")
    yield row("indefinite",b"\xbf"+wire[1:]+b"\xff","malformed")
    yield row("duplicate_key",b"\xad"+wire[1:]+c.enc("domain")+c.enc(c.DOMAIN),"malformed")
    yield row("reordered_keys",b"\xac"+b"".join(c.enc(k)+c.enc(v) for k,v in x.items()),"malformed")
    yield row("invalid_utf8",wire.replace(b"tag.synthetic.local",b"\xff"+b"ag.synthetic.local",1),"malformed")
    for key in ("public_inputs",):
        marker=c.enc(key)+c.enc(x[key])
        for name,b in [("null",b"\xf6"),("float",b"\xf9\x00\x00"),("tag",b"\xc0\x00"),("bool",b"\xf5")]:
            yield row("forbidden_"+name,wire.replace(marker,c.enc(key)+b,1),"malformed")
    for n in (0,2**32-1):
        y=dict(x,public_inputs={"maximum_speed_cm_s":n},proof=dict(x["proof"]))
        y["proof"]["bytes"]=c.token(y)
        yield row("uint_boundary_"+str(n),c.enc(y),"structurally_accepted","valid","accepted")
def generate():
    result=[]
    for name,data,scenario,admission,e,disp in cases():
        a=c.evaluate(data,scenario)
        if a["admission"]!=admission:raise RuntimeError(name+" admission "+a["admission"])
        if e is not None:
            b=a["simulated_result"]
            if (b["envelope_evaluation"],b["service_disposition"])!=(e,disp):raise RuntimeError(name+" expected result")
        if a!=assess(data,scenario):raise RuntimeError(name+" independent mismatch")
        if a["actual_crypto"]!="NOT_CHECKED" or a["verification"]!="NOT_PERFORMED":raise RuntimeError(name+" actual status")
        result.append({"name":name,"wire_hex":data.hex(),"scenario":scenario,"expected":a})
    return {"labels":c.LABELS,"profile":"PROVISIONAL_V1_PLACEHOLDER","cases":result}
if __name__=="__main__":
    path=Path(__file__).with_name("vectors.json")
    data=json.dumps(generate(),indent=2,sort_keys=True)+"\n"
    if path.exists():
        if path.read_text()!=data:raise SystemExit("VECTOR_MISMATCH")
    else:
        with path.open("x") as f:f.write(data)
    print("VECTOR_AND_CHECKER_PASS",len(json.loads(data)["cases"]))
