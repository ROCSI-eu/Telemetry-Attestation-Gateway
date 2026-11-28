"""EXPERIMENTAL / SYNTHETIC_ONLY / A0_SYNTHETIC / NOT VALIDATION OR PRODUCTION AUTHORIZATION.
Non-cryptographic UX prototype — no proof generated or verified."""
import hashlib
import json
import struct
import tempfile
from pathlib import Path
import codec
from binding_adapter import BindingSession, parser, status_mac
from scenario_fixture import CONFIG, TIME, STATUS, SECRET, NOW, status, pin, fixture, at_speed

LABELS=codec.LABELS
CLASSIFICATION="Experimental / Synthetic evidence / Unreviewed / Synthetic data / Local-only / No external assurance claim"
MODE="SYNTHETIC_BINDING_PLACEHOLDER"
if not __debug__:raise RuntimeError("QA_ASSERTIONS_REQUIRED")
THRESHOLD=500

def encode(obj):
    return (json.dumps(obj, sort_keys=True, indent=2)+"\n").encode()

def manifest():
    rows=[]
    for ordinal,speed in enumerate((499,500,501),1):
        wire,capture,receipt,nonce=fixture(at_speed(speed,100000+2*(ordinal-1),999+ordinal),bytes([64+ordinal])*32)
        rows.append(dict(ordinal=ordinal,wire=wire.hex(),capture=capture,receipt=receipt,nonce=nonce.hex()))
    return dict(labels=LABELS,threshold_cm_s=THRESHOLD,observations=rows)

def session(state, s, now=NOW):
    return BindingSession(state_dir=state,config=CONFIG,time_key=TIME,status_key=STATUS,
        source_secret=SECRET,status_pin=pin(s),clock=lambda:now,initialize=True)

def submit(verifier,row,s):
    return verifier.accept(bytes.fromhex(row["wire"]),row["capture"],row["receipt"],
        bytes.fromhex(row["nonce"]),s,status_mac(STATUS,s))

def presentation(ordinal, outcome, reason, replay_commit="NOT_PERFORMED"):
    return dict(ordinal=ordinal,admission=outcome,reason=reason,mode=MODE,
        actual_crypto="NOT_CHECKED",verification="NOT_PERFORMED",replay_commit=replay_commit,
        publication="NOT_PERFORMED",relying_party_decision="NOT_MADE",command_path="NONE")

def present(row,verifier,s):
    if row is None:return presentation(None,"HOLD","INPUT_UNAVAILABLE")
    if verifier is None:return presentation(row["ordinal"],"HOLD","VERIFIER_UNAVAILABLE")
    result=submit(verifier,row,s)
    if any(result.get(k)!=v for k,v in {
        "mode":MODE,"actual_crypto":"NOT_CHECKED","verification":"NOT_PERFORMED",
        "publication":"NOT_PERFORMED","relying_party_decision":"NOT_MADE","command_path":"NONE"}.items()):
        raise RuntimeError("OUTPUT_CONTRACT")
    return presentation(row["ordinal"],result["admission"],result.get("reason","NONE"),result["replay_commit"])

def record(t,payload):return b"\xa3\x95"+bytes([t])+payload
def fmt(t,n,name,f,cols):return record(128,struct.pack("<BB4s16s64s",t,n,name,f,cols))
def dataflash(rows, outcomes):
    # Reuse the previously imported offline TAGD/MSG DataFlash layout.
    data=fmt(150,19,b"TAGD",b"QII",b"TimeUS,Sample,Synthetic")+fmt(151,75,b"MSG",b"QZ",b"TimeUS,Message")
    messages=["EXPERIMENTAL / SYNTHETIC_ONLY / A0_SYNTHETIC",
        "NOT VALIDATION OR PRODUCTION AUTHORIZATION",
        "DERIVED DISPLAY ONLY - NOT A VEHICLE LOG OR PROOF",
        "Threshold 500 cm/s; placeholder; no proof verified",
        "Non-cryptographic UX prototype: no proof generated or verified"]
    for msg in messages:data+=record(151,struct.pack("<Q64s",0,msg.encode("ascii")))
    for row,out in zip(rows,outcomes[:len(rows)],strict=True):
        ordinal=row["ordinal"]
        if ordinal!=out["ordinal"]:raise RuntimeError("ORDINAL_MISMATCH")
        t=(ordinal-1)*1000000
        data+=record(150,struct.pack("<QII",t,ordinal,1))
        msg=f"Sample {ordinal}: {out['admission']} {out['reason']}"
        if len(msg)>64:raise RuntimeError("MSG_SIZE")
        data+=record(151,struct.pack("<Q64s",t,msg.encode("ascii")))
    for out in outcomes[len(rows):]:
        msg=f"Case {out['ordinal'] or 'none'}: HOLD {out['reason']}"
        data+=record(151,struct.pack("<Q64s",len(rows)*1000000,msg.encode("ascii")))
    return data

def run(out):
    # Private manifest/capture and replay state exist only in owned temporary runtime.
    with tempfile.TemporaryDirectory(prefix="tag-common-") as tmp:
        root=Path(tmp); private=root/"manifest.json"
        m=manifest()
        private.write_bytes(encode(m)); private.chmod(0o600)
        assert private.read_bytes()==encode(manifest())
        rows=json.loads(private.read_bytes())["observations"]
        s=status()
        state=root/"state";state.mkdir(mode=0o700)
        v=session(state,s)
        outcomes=[]
        normalized=[]
        for row in rows:
            c=dict(row["capture"],test_trust_store={CONFIG["enrollment"]["slot"]:CONFIG["verifier_key_hex"]})
            n=parser.evaluate_capture(c)
            assert n["status"]=="NORMALIZED"
            normalized.append(n["speed_cm_s"])
            before=(state/"state.json").read_bytes()
            result=present(row,v,s); outcomes.append(result)
            if result["admission"]=="HOLD":assert (state/"state.json").read_bytes()==before
        assert normalized==[499,500,501]
        assert [x["admission"] for x in outcomes]==["SYNTHETIC_CONTRACT_ACCEPTED","SYNTHETIC_CONTRACT_ACCEPTED","HOLD"]
        assert outcomes[2]["reason"]=="PREDICATE_NOT_SATISFIED"
        assert len(v._read()["nullifiers"])==2
        before=(state/"state.json").read_bytes()
        outcomes.extend([present(None,v,s),present(rows[0],None,s)])
        assert (state/"state.json").read_bytes()==before
        assert [x["reason"] for x in outcomes[3:]]==["INPUT_UNAVAILABLE","VERIFIER_UNAVAILABLE"]
        # Additional fail-closed control: replay exact previously accepted observation.
        replay=present(rows[0],v,s)
        assert replay["admission"]=="HOLD" and "REPLAY" in replay["reason"]
        assert (state/"state.json").read_bytes()==before
        # Revoked status: fresh isolated state, no commit.
        rs=status(True); rev=root/"revoked";rev.mkdir(mode=0o700)
        rv=session(rev,rs); old=(rev/"state.json").read_bytes()
        rejected=present(rows[0],rv,rs)
        assert rejected["reason"]=="REVOKED" and rejected["admission"]=="HOLD"
        assert (rev/"state.json").read_bytes()==old
        blob=dataflash(rows,outcomes)
        report=dict(labels=LABELS,classification=CLASSIFICATION,
            notice="Non-cryptographic UX prototype — no proof generated or verified",
            threshold_cm_s=THRESHOLD,association="SCOPED_SYNTHETIC_ORDINAL_NOT_CRYPTOGRAPHIC",
            samples=outcomes[:3],unavailable_cases=outcomes[3:],
            historical=dict(origin="COMPANION_EXP4_HISTORICAL_ONLY",suite="bounded-speed-proof-v0",
                actual_crypto_then="VALID",verification_then="PERFORMED",
                verification_now="NOT_PERFORMED",observation_binding="NOT_EVALUATED",
                current_sample_association="NONE"),
            control_results={"replay":"PASS","revocation":"PASS","deterministic_manifest":"PASS"})
    assert not root.exists()
    report["cleanup"]="PASS"
    out.mkdir(exist_ok=True)
    (out/"common-results.json").write_bytes(encode(report))
    (out/"EXPERIMENTAL_SYNTHETIC_ONLY_TAGD.bin").write_bytes(blob)
    print("COMMON_SCENARIO_PASS: 3 observations, 2 unavailable cases, replay/revocation controls; cleanup PASS")

if __name__=="__main__":
    import sys
    if len(sys.argv)!=2:raise SystemExit("usage: common_scenario.py OUTPUT_DIR")
    run(Path(sys.argv[1]))
