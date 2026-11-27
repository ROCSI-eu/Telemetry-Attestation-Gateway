"""EXPERIMENTAL / SYNTHETIC_ONLY / A0_SYNTHETIC / NOT VALIDATION OR PRODUCTION AUTHORIZATION.
Source-only distribution candidate. No automatic installation or provisioning.
"""
import argparse,hashlib,json,os,platform,stat,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent
MARKS=["EXPERIMENTAL","SYNTHETIC_ONLY","A0_SYNTHETIC","NOT VALIDATION OR PRODUCTION AUTHORIZATION"]
VERSION="0.1.0-exp.4"
APP_FILES=("inspector.py","adapter.py","runtime_plan.py","verify_entry.py","local_profile.py","bin/bb","portable/portable.py","engine/integrated-cli-v0/authentic_package_cli.py","engine/bounded-speed-proof-v0/verify.py","engine/bounded-speed-proof-v0/common.py","engine/bounded-speed-v0/bounded_speed.py")
RELEASE_FILES=tuple("app/"+n for n in APP_FILES)+("tag_cli.py","verify_dispatch.py","lifecycle.py","local_lifecycle.py","LICENSE","README.md")
class Rejected(ValueError):pass
def need(ok,reason):
    if not ok:raise Rejected(reason)
def sha(f):
    with f.open("rb") as h:return hashlib.file_digest(h,"sha256").hexdigest()
def regular(f):
    s=f.lstat();need(stat.S_ISREG(s.st_mode) and s.st_nlink==1 and s.st_uid==os.getuid() and not s.st_mode&0o022,"RELEASE_FILE")
def private_dir(d):
    s=d.lstat();need(stat.S_ISDIR(s.st_mode) and s.st_uid==os.getuid() and stat.S_IMODE(s.st_mode)==0o700,"PRIVATE_DIRECTORY")
    return s
def check_release(root,expected):
    private_dir(root);m=root/"SHA256SUMS";regular(m)
    need(m.stat().st_size<=8192 and type(expected) is str and len(expected)==64 and sha(m)==expected,"RELEASE_PIN")
    rows={}
    for line in m.read_text().splitlines():
        h,sep,n=line.partition("  ")
        need(sep and n in RELEASE_FILES and n not in rows and len(h)==64,"RELEASE_MANIFEST")
        rows[n]=h
    need(set(rows)==set(RELEASE_FILES),"RELEASE_MANIFEST")
    paths=list(root.rglob("*"))
    allowed_dirs={str(Path(n).parent) for n in RELEASE_FILES}
    allowed_dirs|={str(parent) for n in RELEASE_FILES for parent in Path(n).parents}
    for path in paths:
        rel=str(path.relative_to(root))
        need(not path.is_symlink(),"RELEASE_SYMLINK")
        if path.is_dir():
            need(rel in allowed_dirs,"RELEASE_EXTRA");private_dir(path)
        else:need(rel in set(RELEASE_FILES)|{"SHA256SUMS"},"RELEASE_EXTRA")
    for n,h in rows.items():
        f=root/n;regular(f);need(sha(f)==h,"RELEASE_CHANGED")
    return rows
def engine():
    sys.path.insert(0,str(ROOT/"app"/"portable"))
    import portable as p
    return p
def doctor(profile):
    from local_profile import check
    try:
        check(profile,ROOT/"app")
        return {"labels":MARKS,"status":"DEPENDENCY_PINS_MATCH","runtime_acceptance":"NOT_PERFORMED"}
    except (OSError,ValueError,RuntimeError,KeyError,TypeError):
        return {"labels":MARKS,"status":"HOLD","runtime_acceptance":"NOT_PERFORMED"}
def read_record(path,limit=4096):
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
    with os.fdopen(fd,"rb") as h:
        s=os.fstat(h.fileno());need(stat.S_ISREG(s.st_mode) and s.st_uid==os.getuid() and s.st_nlink==1 and not s.st_mode&0o077 and 0<s.st_size<=limit,"RECORD_PRIVATE")
        b=h.read(limit+1);need(len(b)==s.st_size,"RECORD_SIZE");return b
def inspect_action(args,p):
    raw=p.load_package(Path(args.package_dir))
    review=read_record(Path(args.review));prov=read_record(Path(args.provenance))
    now=datetime.now(timezone.utc)
    result=p.inspect_for_action(raw,review,args.review_sha256,args.package_sha256,"REVERIFY",now,prov)
    return raw,result
def verification_plan(args,p,profile):
    # This release is DESIGN-AND-READINESS only: no execution dispatcher.
    # A separate accepted lifecycle/runtime increment may activate the existing
    # adapter, using the exact same gates and no new proof suite.
    _,eligibility=inspect_action(args,p)
    deps=doctor(profile)
    ready=eligibility["status"]=="ELIGIBLE_FOR_SCOPED_ACTION_REVIEW" and deps["status"]=="DEPENDENCY_PINS_MATCH"
    return {"labels":MARKS,"version":VERSION,"status":"PREPARED_NOT_EXECUTED" if ready else "HOLD","eligibility":eligibility["status"],"dependencies":deps["status"],"crypto":"NOT_CHECKED","verification":"NOT_PERFORMED","publication":"NOT_PERFORMED","decision":"NOT_MADE","execution_gate":"SEPARATE_AUTHORIZATION_AND_RUNTIME_ACCEPTANCE_REQUIRED"}
class Parser(argparse.ArgumentParser):
    def error(self,message):raise Rejected("ARGUMENTS")
def parse(argv):
    a=Parser(description=" / ".join(MARKS)+" — source-only distribution candidate")
    a.add_argument("--release-sha256",required=True)
    a.add_argument("--profile");a.add_argument("--profile-sha256")
    s=a.add_subparsers(dest="command",required=True,parser_class=Parser)
    s.add_parser("version");s.add_parser("doctor")
    for name in ("inspect","verify-plan","verify"):
        c=s.add_parser(name);c.add_argument("--package-dir",required=True);c.add_argument("--package-sha256",required=True);c.add_argument("--review",required=True);c.add_argument("--review-sha256",required=True);c.add_argument("--provenance",required=True)
        if name=="verify":
            c.add_argument("--grant-dir",required=True);c.add_argument("--grant-sha256",required=True)
    return a.parse_args(argv)
def main(argv=None):
    try:
        args=parse(argv);check_release(ROOT,args.release_sha256)
        if args.command=="version":result={"labels":MARKS,"version":VERSION,"status":"SOURCE_ONLY","execution":"NOT_PERFORMED"}
        else:
            p=engine()
            profile=None
            if args.command in ("doctor","verify-plan","verify"):
                from local_profile import load
                need(args.profile and args.profile_sha256,"PROFILE_REQUIRED")
                profile=load(Path(args.profile),args.profile_sha256)
            if args.command=="doctor":result=doctor(profile)
            elif args.command=="inspect":_,result=inspect_action(args,p)
            elif args.command=="verify-plan":result=verification_plan(args,p,profile)
            else:
                from verify_dispatch import dispatch
                result,rc=dispatch(args,p,profile);print(json.dumps(result,sort_keys=True));return rc
        print(json.dumps(result,sort_keys=True));return 2 if result["status"]=="REJECTED" else 5 if result["status"]=="HOLD" else 0
    except (Rejected,OSError,ValueError,TypeError,RuntimeError,KeyError):
        print(json.dumps({"labels":MARKS,"status":"REJECTED","reason":"PREFLIGHT_OR_INPUT_REJECTED","verification":"NOT_PERFORMED"},sort_keys=True));return 2
if __name__=="__main__":sys.exit(main())
