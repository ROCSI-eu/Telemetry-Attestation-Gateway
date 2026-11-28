"""EXPERIMENTAL / SYNTHETIC_ONLY / A0_SYNTHETIC / NOT VALIDATION OR PRODUCTION AUTHORIZATION.
Separate owner-reviewed execution grant; single attempt per private grant directory.
No proof generation or arbitrary command dispatch. Code-only candidate.
"""
import os,json,stat,sys,fcntl,subprocess,tempfile,hashlib
from pathlib import Path
from datetime import datetime,timezone
import tag_cli as c
def need(ok,reason):
    if not ok:raise c.Rejected(reason)
def utcnow():return datetime.now(timezone.utc)
def overlaps(a,b):return a==b or a.is_relative_to(b) or b.is_relative_to(a)
def grant_check(b,args,p,now,provenance,review):
    need(p.sha(b)==args.grant_sha256,"GRANT_PIN")
    g=p.i.decode(b)
    need(type(g) is dict and set(g)=={"schema","labels","release_sha256","package_sha256","review_sha256","provenance_sha256","profile_sha256","action","max_attempts","issued_utc","expires_utc","scope"},"GRANT_SCHEMA")
    need(g["schema"]=="TAG_CLI_EXECUTION_GRANT_V2_EXPERIMENTAL" and g["labels"]==c.MARKS and g["scope"]=="LOCAL_ONLY_NO_PUBLICATION" and g["action"]=="REVERIFY" and type(g["max_attempts"]) is int and g["max_attempts"]==1,"GRANT_SCOPE")
    need(g["release_sha256"]==args.release_sha256 and g["package_sha256"]==args.package_sha256 and g["review_sha256"]==args.review_sha256 and g["provenance_sha256"]==p.sha(provenance) and g["profile_sha256"]==args.profile_sha256,"GRANT_BINDING")
    need(p.sha(review)==args.review_sha256,"REVIEW_PIN")
    r=p.i.decode(review);pr=p.i.decode(provenance)
    issued,expires=p.time_value(g["issued_utc"]),p.time_value(g["expires_utc"])
    need(p.time_value(r["issued_utc"])<=issued<=now<expires<=p.time_value(r["expires_utc"])<=p.time_value(pr["retention_not_after_utc"]),"GRANT_TIME")
    return g
def check_result(data,rc,p):
    need(type(data) is bytes and 0<len(data)<=16384,"RESULT_SIZE")
    d=p.i.decode(data)
    need(type(d) is dict and d.get("labels")==c.MARKS and d.get("schema")=="TAG_INSPECTOR_EXPERIMENTAL_01","RESULT_SCHEMA")
    fields={k:v for k,v in d.items() if k not in ("labels","schema")}
    need(set(fields)==set(p.i.Result.__dataclass_fields__),"RESULT_FIELDS")
    reconstructed=p.i.Result(**fields)
    need(p.i.decode(reconstructed.export())==d,"RESULT_ENUMS")
    need(d["publication"]=="NOT_PERFORMED" and d["decision"]=="NOT_MADE" and d["command_path"]=="NONE" and d["generation"]=="NOT_OBSERVED","RESULT_SCOPE")
    need(all(d[k]=="NOT_EVALUATED" for k in ("source_trust","observation_binding","policy","freshness","revocation","replay")),"RESULT_SCOPE")
    if d["crypto"] in ("VALID","INVALID"):
        need(d["origin"]=="CURRENT_VERIFIER" and d["suite"]==p.SUITE and d["package"]=="ACCEPTED" and d["input"]=="ACCEPTED" and d["verification"]=="PERFORMED" and rc==(0 if d["crypto"]=="VALID" else 4),"RESULT_CONSISTENCY")
    else:
        need(d["verification"]=="NOT_PERFORMED" and d["crypto"] in ("NOT_CHECKED","UNVERIFIABLE") and rc in (2,5),"RESULT_CONSISTENCY")
    return d
def open_grant(args):
    gd=Path(args.grant_dir)
    c.private_dir(gd);gd=gd.resolve()
    for path in (c.ROOT,Path(args.package_dir),Path(args.review),Path(args.provenance),Path(args.profile)):
        need(not overlaps(gd,path.resolve()),"GRANT_DIRECTORY_SCOPE")
    fd=os.open(gd,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:
        fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
        need({x.name for x in gd.iterdir()}=={"execution-grant.json"},"GRANT_ALREADY_USED_OR_EXTRA")
        return gd,fd
    except BaseException:os.close(fd);raise
def consume(gd,fd,args,p):
    s=os.fstat(fd);d=gd.lstat()
    need((s.st_dev,s.st_ino)==(d.st_dev,d.st_ino),"GRANT_DIRECTORY_CHANGED")
    f=os.open("attempt.started",os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=fd)
    with os.fdopen(f,"wb") as h:
        h.write(p.enc({"labels":c.MARKS,"grant_sha256":args.grant_sha256,"attempt":1,"state":"CONSUMED_NO_RETRY"}));h.flush();os.fsync(h.fileno())
    os.fsync(fd)
def run_transport(cmd,work):
    # Fixed existing runtime plan only; capped child output via owned file,
    # no stdout/stderr passthrough. Inner adapter already caps stdout to 16 KiB.
    with (work/"stdout").open("xb") as f:
        proc=subprocess.run(cmd,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.DEVNULL,env={"PATH":"/usr/bin:/bin","LANG":"C.UTF-8"},timeout=45)
    f=work/"stdout";need(f.stat().st_size<=16384,"RESULT_SIZE")
    return proc.returncode,f.read_bytes()
def dispatch(args,p,profile):
    # No authority inferred from hashes. Caller must hold a separately approved
    # exact grant; this is a local consistency check, not signature or trusted time.
    result={"labels":c.MARKS,"status":"HOLD","crypto":"NOT_CHECKED","verification":"NOT_PERFORMED","publication":"NOT_PERFORMED","decision":"NOT_MADE","attempts":0}
    fd=None
    try:
        raw=p.load_package(Path(args.package_dir))
        review=c.read_record(Path(args.review));prov=c.read_record(Path(args.provenance))
        now=utcnow()
        e=p.inspect_for_action(raw,review,args.review_sha256,args.package_sha256,"REVERIFY",now,prov)
        need(e["status"]=="ELIGIBLE_FOR_SCOPED_ACTION_REVIEW","REVIEW_GATE")
        gd,fd=open_grant(args)
        grant=c.read_record(gd/"execution-grant.json")
        grant_check(grant,args,p,now,prov,review)
        need(c.doctor(profile)["status"]=="DEPENDENCY_PINS_MATCH","DEPENDENCY_GATE")
        import runtime_plan as rp
        # Only app/ is mounted, not release root or its sibling checkpoints.
        need(rp.HERE==c.ROOT/"app","APP_SCOPE")
        with tempfile.TemporaryDirectory(prefix="tag-cli-verify-",dir="/tmp") as t:
            work=Path(t);c.private_dir(work)
            staged=work/"package";staged.mkdir(mode=0o700)
            need(p._stage_snapshot(raw,staged)==args.package_sha256,"STAGE_PIN")
            cmd=rp.command(staged,profile)
            need(str(c.ROOT/"app") in cmd and str(staged) in cmd and "--unshare-all" in cmd and "--clearenv" in cmd and "--bind" not in cmd and "--share-net" not in cmd,"PLAN_SCOPE")
            grant_check(grant,args,p,utcnow(),prov,review)
            consume(gd,fd,args,p);result["attempts"]=1
            rc,data=run_transport(cmd,work)
            typed=check_result(data,rc,p)
        # Recheck original package, never replace it. A changed original or
        # failed cleanup must not produce an externally reported VALID.
        need(p.fingerprint(p.load_package(Path(args.package_dir)))==args.package_sha256,"ORIGINAL_CHANGED")
        result={"labels":c.MARKS,"status":typed["crypto"],"crypto":typed["crypto"],"verification":typed["verification"],"publication":"NOT_PERFORMED","decision":"NOT_MADE","attempts":1,"cleanup":"PASS","result":typed}
        return result,rc
    except (OSError,ValueError,TypeError,RuntimeError,KeyError,subprocess.SubprocessError):
        # Never expose untrusted paths or raw output. Consumed marker remains.
        result["status"]="HOLD";result["crypto"]="UNVERIFIABLE" if result["attempts"] else "NOT_CHECKED"
        result["reason"]="EXECUTION_OR_GATE_NOT_ACCEPTED"
        return result,5
    finally:
        if fd is not None:os.close(fd)
