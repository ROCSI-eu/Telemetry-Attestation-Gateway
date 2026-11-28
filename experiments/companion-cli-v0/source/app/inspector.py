"""EXPERIMENTAL / SYNTHETIC_ONLY / A0_SYNTHETIC / NOT VALIDATION OR PRODUCTION AUTHORIZATION."""
import hashlib,json,os,re,stat,sys,tempfile
from pathlib import Path
from dataclasses import dataclass,asdict
from types import MappingProxyType
HERE=Path(__file__).resolve().parent
ENGINE=HERE/"engine"
sys.path.insert(0,str(ENGINE/"integrated-cli-v0"))
import authentic_package_cli as canonical
MARKS=tuple(canonical.LABELS)
SUITE="bounded-speed-proof-v0"
NAMES=canonical.FILES
LIMITS=canonical.MAX_BYTES
class Rejected(ValueError): pass
def need(ok,reason="PACKAGE_REJECTED"):
    if not ok:raise Rejected(reason)
def unique(pairs):
    out={}
    for k,v in pairs:
        need(k not in out,"DUPLICATE_KEY");out[k]=v
    return out
def decode(raw):
    return json.loads(raw,object_pairs_hook=unique,parse_constant=lambda _:(_ for _ in ()).throw(Rejected("NONFINITE")))
def snapshot(path):
    """Owner-cooperative, bounded dirfd reads; no symlinks, no hardlinks, no special files."""
    try:
        fd=os.open(path,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
        try:
            s=os.fstat(fd);need(s.st_uid==os.getuid() and stat.S_IMODE(s.st_mode)==0o700,"PRIVATE_DIRECTORY_REQUIRED")
            # Bounded directory iteration, reject any surplus entry.
            with os.scandir(fd) as entries:
                names=[]
                for ent in entries:
                    names.append(ent.name);need(len(names)<=len(NAMES))
            need(set(names)==set(NAMES))
            raw={}
            for name in NAMES:
                f=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=fd)
                with os.fdopen(f,"rb") as h:
                    m=os.fstat(h.fileno())
                    need(stat.S_ISREG(m.st_mode) and m.st_uid==os.getuid() and m.st_nlink==1 and not stat.S_IMODE(m.st_mode)&0o077 and 0<m.st_size<=LIMITS[name],"PRIVATE_REGULAR_FILE_REQUIRED")
                    b=h.read(LIMITS[name]+1);after=os.fstat(h.fileno())
                    need(len(b)==m.st_size and (m.st_size,m.st_mtime_ns,m.st_ctime_ns)==(after.st_size,after.st_mtime_ns,after.st_ctime_ns),"FILE_CHANGED")
                    raw[name]=b
            return MappingProxyType(raw)
        finally:os.close(fd)
    except Rejected:raise
    except (OSError,ValueError,TypeError):raise Rejected("PACKAGE_UNAVAILABLE") from None
def validate(raw):
    try:
        m=decode(raw["manifest.json"])
        need(type(m) is dict)
        need(m.get("experiment")==SUITE,"UNSUPPORTED_SUITE")
        need(set(m)=={"labels","experiment","predicate","proof_mode","verifier_target","private_witness_disclosed","public","tool_versions","artifacts","dimensions_not_evaluated"})
        need(m["labels"]==list(MARKS) and m["predicate"]=="speed_cm_s <= maximum_speed_cm_s" and m["proof_mode"]=="zero_knowledge" and m["verifier_target"]=="noir-recursive" and m["private_witness_disclosed"] is False)
        p=m["public"];need(type(p) is dict and set(p)=={"schema_version","maximum_speed_cm_s","assurance_id"} and type(p["schema_version"]) is int and p["schema_version"]==0 and type(p["maximum_speed_cm_s"]) is int and 0<=p["maximum_speed_cm_s"]<=2**32-1 and p["assurance_id"]=="A0_SYNTHETIC")
        v=m["tool_versions"];need(type(v) is dict and set(v)=={"nargo","bb"} and type(v["nargo"]) is str and len(v["nargo"])<=256 and re.search(r"^nargo version = 1\.0\.0-beta\.26$",v["nargo"],re.M) is not None and v["bb"]=="5.2.0")
        need(m["dimensions_not_evaluated"]==["telemetry_truth","policy_lifecycle","freshness","revocation","replay","publication","relying_party_business_decision"])
        a=m["artifacts"];need(type(a) is dict and set(a)==set(NAMES)-{"manifest.json"})
        for n in a:
            x=a[n];need(type(x) is dict and set(x)==({"sha256"} if n=="public-artifact.cbor" else {"sha256","size_bytes"}))
            need(x["sha256"]==hashlib.sha256(raw[n]).hexdigest(),"DIGEST_MISMATCH")
            if n!="public-artifact.cbor":need(type(x["size_bytes"]) is int and x["size_bytes"]==len(raw[n]))
        decoded=canonical.independent_verifier.BOUNDED.decode_public_artifact(raw["public-artifact.cbor"])
        need(decoded["version"]==p["schema_version"] and decoded["maximum_speed_cm_s"]==p["maximum_speed_cm_s"],"PUBLIC_INPUT_MISMATCH")
        return raw
    except Rejected:raise
    except (ValueError,TypeError,KeyError,UnicodeError,AttributeError,RecursionError,canonical.independent_verifier.BOUNDED.EncodingError):raise Rejected("PACKAGE_REJECTED") from None
def stage(raw,folder):
    for n in NAMES:
        with (folder/n).open("xb") as h:h.write(raw[n])
        (folder/n).chmod(0o600)
@dataclass(frozen=True)
class Result:
    origin:str="NONE"
    suite:str="NOT_SELECTED"
    package:str="NOT_CHECKED"
    input:str="NOT_CHECKED"
    crypto:str="NOT_CHECKED"
    verification:str="NOT_PERFORMED"
    reason:str="NONE"
    source_trust:str="NOT_EVALUATED"
    observation_binding:str="NOT_EVALUATED"
    generation:str="NOT_OBSERVED"
    policy:str="NOT_EVALUATED"
    freshness:str="NOT_EVALUATED"
    revocation:str="NOT_EVALUATED"
    replay:str="NOT_EVALUATED"
    assurance:str="A0_SYNTHETIC"
    publication:str="NOT_PERFORMED"
    decision:str="NOT_MADE"
    command_path:str="NONE"
    def export(self):
        values=asdict(self)
        for k,v in values.items():
            need(type(v) is str and v in EXPORT_VALUES[k],"EXPORT_REJECTED")
        return json.dumps({"schema":"TAG_INSPECTOR_EXPERIMENTAL_01","labels":list(MARKS),**values},sort_keys=True,indent=2)+"\n"
REASONS={"UNTRUSTED_OR_INCOMPATIBLE_PACKAGE","PUBLIC_ARTIFACT_UNAVAILABLE","PUBLIC_ARTIFACT_MALFORMED_OR_INCOMPATIBLE","PROOF_OR_KEY_UNAVAILABLE","VERIFICATION_KEY_UNRECOGNIZED","INCOMPATIBLE_OR_MISSING_VERIFIER","VERIFIER_EXECUTION_FAILED","PROOF_REJECTED","VERIFIER_OPERATIONAL_FAILURE"}
EXPORT_VALUES={
    "origin":{"NONE","PACKAGE","CURRENT_VERIFIER","MOCK"},
    "suite":{"NOT_SELECTED",SUITE},
    "package":{"NOT_CHECKED","ACCEPTED","REJECTED"},
    "input":{"NOT_CHECKED","ACCEPTED","REJECTED"},
    "crypto":{"NOT_CHECKED","VALID","INVALID","UNVERIFIABLE"},
    "verification":{"NOT_PERFORMED","PERFORMED","SIMULATED"},
    "reason":REASONS|{"NONE","READY_NOT_VERIFIED","PACKAGE_REJECTED","UNSUPPORTED_SUITE","DUPLICATE_KEY","NONFINITE","PRIVATE_DIRECTORY_REQUIRED","PRIVATE_REGULAR_FILE_REQUIRED","FILE_CHANGED","PACKAGE_UNAVAILABLE","DIGEST_MISMATCH","PUBLIC_INPUT_MISMATCH","RESPONSE_INVALID","RECORDED_ONLY_PROOF_NOT_RETAINED","RECORDED_RESULT_REJECTED","VERIFICATION_IN_PROGRESS","ISOLATION_NOT_ESTABLISHED"},
    "source_trust":{"NOT_EVALUATED"},
    "observation_binding":{"NOT_EVALUATED"},
    "generation":{"NOT_OBSERVED"},
    **{k:{"NOT_EVALUATED"} for k in ("policy","freshness","revocation","replay")},
    "assurance":{"A0_SYNTHETIC"},"publication":{"NOT_PERFORMED"},"decision":{"NOT_MADE"},"command_path":{"NONE"}
}
def from_cli(raw,rc,*,simulated=False):
    """Strictly reconstruct safe fields; no manifest-only validity or free-form reason."""
    origin="MOCK" if simulated else "CURRENT_VERIFIER"
    try:
        need(type(raw) is bytes and 0<len(raw)<=16384,"RESPONSE_INVALID")
        d=decode(raw);base=canonical._result()
        need(type(d) is dict and set(d)==set(base),"RESPONSE_INVALID")
        for k in set(base)-{"package","verification_input","cryptographic","verification_performed"}:
            need(type(d[k]) is type(base[k]) and d[k]==base[k],"RESPONSE_INVALID")
        p,i,c=(d[k] for k in ("package","verification_input","cryptographic"))
        for item,allowed in ((p,{"REJECTED","ACCEPTED"}),(i,{"REJECTED","ACCEPTED","NOT_CHECKED"}),(c,{"VALID","INVALID","UNVERIFIABLE","NOT_CHECKED"})):
            need(type(item) is dict and set(item)=={"status","reason"} and item["status"] in allowed and (item["reason"] is None or item["reason"] in REASONS),"RESPONSE_INVALID")
        ps,ins,cs=p["status"],i["status"],c["status"]
        allowed={(2,"REJECTED","NOT_CHECKED","NOT_CHECKED"),(3,"ACCEPTED","REJECTED","NOT_CHECKED"),(0,"ACCEPTED","ACCEPTED","VALID"),(4,"ACCEPTED","ACCEPTED","INVALID"),(5,"ACCEPTED","ACCEPTED","UNVERIFIABLE"),(5,"ACCEPTED","NOT_CHECKED","UNVERIFIABLE")}
        need((rc,ps,ins,cs) in allowed,"RESPONSE_INVALID")
        need(d["verification_performed"] is (cs in {"VALID","INVALID"}),"RESPONSE_INVALID")
        need(all((x["reason"] is None)==(x["status"] in {"ACCEPTED","VALID","NOT_CHECKED"}) for x in (p,i,c)),"RESPONSE_INVALID")
        need(p["reason"] in (None,"UNTRUSTED_OR_INCOMPATIBLE_PACKAGE") and i["reason"] in (None,"PUBLIC_ARTIFACT_UNAVAILABLE","PUBLIC_ARTIFACT_MALFORMED_OR_INCOMPATIBLE"),"RESPONSE_INVALID")
        need((cs!="INVALID" or c["reason"]=="PROOF_REJECTED") and (cs!="UNVERIFIABLE" or c["reason"] in {"PROOF_OR_KEY_UNAVAILABLE","VERIFICATION_KEY_UNRECOGNIZED","INCOMPATIBLE_OR_MISSING_VERIFIER","VERIFIER_EXECUTION_FAILED","VERIFIER_OPERATIONAL_FAILURE"}),"RESPONSE_INVALID")
        return Result(origin,SUITE,ps,ins,cs,"SIMULATED" if simulated else ("PERFORMED" if d["verification_performed"] else "NOT_PERFORMED"),c["reason"] or i["reason"] or p["reason"] or "NONE")
    except (Rejected,ValueError,TypeError,KeyError,AttributeError,RecursionError):
        return Result(origin,SUITE,crypto="UNVERIFIABLE",reason="RESPONSE_INVALID",verification="SIMULATED" if simulated else "NOT_PERFORMED")
class Session:
    def __init__(self):self.clear()
    def clear(self):self.result=Result();self._raw=None
    def select(self,path):
        self.clear()
        try:
            self._raw=validate(snapshot(path))
            self.result=Result("PACKAGE",SUITE,package="ACCEPTED",reason="READY_NOT_VERIFIED")
        except Rejected as e:self.result=Result("PACKAGE",package="REJECTED",reason=str(e))
        return self.result
    def verify(self):
        from adapter import run_verified
        if self._raw is None:return self.result
        raw=self._raw;self._raw=None
        self.result=Result("CURRENT_VERIFIER",SUITE,package="ACCEPTED",crypto="UNVERIFIABLE",reason="VERIFIER_OPERATIONAL_FAILURE")
        try:
            with tempfile.TemporaryDirectory(prefix="tag-inspector-") as tmp:
                folder=Path(tmp);stage(raw,folder)
                rc,response=run_verified(folder)
                result=from_cli(response,rc)
            self.result=result
        except (OSError,ValueError,RuntimeError,TimeoutError):pass
        return self.result
    @property
    def can_verify(self):return self._raw is not None
