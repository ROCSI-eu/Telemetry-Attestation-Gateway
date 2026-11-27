"""EXPERIMENTAL / SYNTHETIC_ONLY / A0_SYNTHETIC / NOT VALIDATION OR PRODUCTION AUTHORIZATION.
Local experimental lifecycle; fixed registered releases, private root, no global install.
Caller must hold separate scoped owner authorization. No crypto dispatcher.
"""
import contextlib,fcntl,json,os,shutil,stat,subprocess,sys
from pathlib import Path
import tag_cli as c
import lifecycle as planner
MARKS=c.MARKS
EMPTY={"current":None,"previous":None}
class Interrupted(RuntimeError):pass
def need(ok,reason):
    if not ok:raise RuntimeError(reason)
def encode(obj):return (json.dumps(obj,sort_keys=True,separators=(",",":"))+"\n").encode()
def sync_dir(p):
    fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:os.fsync(fd)
    finally:os.close(fd)
def read_private(p):
    fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
    with os.fdopen(fd,"rb") as h:
        s=os.fstat(h.fileno());need(stat.S_ISREG(s.st_mode) and s.st_uid==os.getuid() and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o600 and 0<s.st_size<=8192,"STATE_FILE")
        data=h.read(8193);need(len(data)==s.st_size,"STATE_SIZE")
    def unique(pairs):
        obj={}
        for k,v in pairs:
            need(k not in obj,"DUPLICATE_STATE_KEY");obj[k]=v
        return obj
    return json.loads(data,object_pairs_hook=unique)
def atomic(p,obj):
    tmp=p.with_name(p.name+".next")
    with tmp.open("xb") as h:h.write(encode(obj));h.flush();os.fsync(h.fileno())
    os.replace(tmp,p);sync_dir(p.parent)
class Local:
    def __init__(self,root,registry,create=False,profile=None):
        self.root=Path(root);self.registry=dict(registry);self.profile=profile
        for version,(path,seal) in self.registry.items():planner.validate_entry({"version":version,"seal":seal})
        self.releases=self.root/"releases"
        self.statefile=self.root/"state.json";self.journal=self.root/"transaction.json"
        if create:
            self.root.mkdir(mode=0o700)
            self.releases.mkdir(mode=0o700)
            with (self.root/"lock").open("xb"):pass
            atomic(self.statefile,EMPTY)
        self.identity=c.private_dir(self.root);c.private_dir(self.releases)
    def guard(self):
        s=c.private_dir(self.root);need((s.st_dev,s.st_ino)==(self.identity.st_dev,self.identity.st_ino),"ROOT_IDENTITY")
        c.private_dir(self.releases)
        need({p.name for p in self.root.iterdir()}<={"releases","lock","state.json","transaction.json","state.json.next","transaction.json.next"},"ROOT_EXTRA")
        need(not any((self.root/n).exists() or (self.root/n).is_symlink() for n in ("state.json.next","transaction.json.next")),"INCOMPLETE_ATOMIC_WRITE")
    @contextlib.contextmanager
    def locked(self):
        self.guard()
        fd=os.open(self.root/"lock",os.O_RDWR|os.O_NOFOLLOW|os.O_NONBLOCK)
        try:
            s=os.fstat(fd);need(stat.S_ISREG(s.st_mode) and s.st_uid==os.getuid() and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o600,"LOCK_FILE")
            fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB);self.guard();yield
        finally:os.close(fd)
    def entry(self,e):
        e=planner.validate_entry(e);need(e["version"] in self.registry and self.registry[e["version"]][1]==e["seal"],"UNREGISTERED_RELEASE");return e
    def state(self):
        s=read_private(self.statefile)
        need(type(s) is dict and set(s)=={"current","previous"},"STATE_SCHEMA")
        for e in s.values():
            if e is not None:self.entry(e)
        need(not s["previous"] or (s["current"] and s["previous"]!=s["current"]),"STATE_SCHEMA")
        return s
    def check_version(self,e):
        e=self.entry(e);d=self.releases/e["version"];c.check_release(d,e["seal"]);return d
    def check_tree(self,state):
        names={e["version"] for e in state.values() if e}
        need({p.name for p in self.releases.iterdir()}==names,"RELEASE_SET")
        for e in state.values():
            if e:self.check_version(e)
    def info(self,e,command):
        need(command in ("version","doctor"),"INFO_ONLY")
        d=self.check_version(e)
        argv=["/usr/bin/python3","-B",str(d/"tag_cli.py"),"--release-sha256",e["seal"]]
        if command=="doctor":
            need(self.profile is not None,"PROFILE_REQUIRED");argv+=["--profile",str(self.profile[0]),"--profile-sha256",self.profile[1]]
        result=subprocess.run(argv+[command],cwd=d,env={"PATH":"/usr/bin:/bin","LANG":"C.UTF-8","HOME":"/tmp"},stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,timeout=10)
        need(result.returncode==0 and len(result.stdout)<=16384,"INFO_FAILED")
        data=json.loads(result.stdout);need(data["labels"]==MARKS,"INFO_LABELS")
        if command=="version":need(data["version"]==e["version"] and data["execution"]=="NOT_PERFORMED","INFO_VERSION")
        else:need(data["status"]=="DEPENDENCY_PINS_MATCH" and data["runtime_acceptance"]=="NOT_PERFORMED","INFO_DEPS")
        return data
    def install_copy(self,e):
        source,seal=self.registry[e["version"]];c.check_release(source,seal)
        target=self.releases/e["version"];stage=self.releases/(".stage-"+e["version"])
        need(not target.exists() and not target.is_symlink() and not stage.exists() and not stage.is_symlink(),"TARGET_EXISTS")
        stage.mkdir(mode=0o700)
        for n in (*c.RELEASE_FILES,"SHA256SUMS"):
            dst=stage/n;dst.parent.mkdir(parents=True,mode=0o700,exist_ok=True)
            with (source/n).open("rb") as src,dst.open("xb") as out:
                shutil.copyfileobj(src,out);out.flush();os.fsync(out.fileno())
            dst.chmod(0o500 if n=="app/bin/bb" else 0o400)
        for d in sorted((p for p in stage.rglob("*") if p.is_dir()),key=lambda d:len(d.parts),reverse=True):sync_dir(d)
        sync_dir(stage);c.check_release(stage,seal)
        stage.rename(target);sync_dir(self.releases)
    def retire(self,e):
        target=self.check_version(e)
        # Exact sealed, registered private directory only. No generic path deletion.
        need(target.parent==self.releases and shutil.rmtree.avoids_symlink_attacks,"RETIRE_SCOPE")
        shutil.rmtree(target);sync_dir(self.releases)
    def recover_locked(self):
        need(not self.journal.is_symlink(),"JOURNAL_SYMLINK")
        if not self.journal.exists():
            self.check_tree(self.state());return "CLEAN"
        j=read_private(self.journal)
        need(set(j)=={"action","before","after","candidate"},"JOURNAL_SCHEMA")
        a=j["action"];before=j["before"];after=j["after"];candidate=j["candidate"]
        expected=planner.plan(before,a,candidate)
        need(expected["desired_state"]==after,"JOURNAL_PLAN")
        for e in (*before.values(),*after.values()):
            if e:self.entry(e)
        current=self.state()
        need(current in (before,after),"STATE_DIVERGED")
        if current==before and before!=after:
            # Aborted precommit: only remove a complete exact sealed candidate.
            # Incomplete/ambiguous stage fails closed and needs scoped reconciliation.
            if candidate:
                stage=self.releases/(".stage-"+candidate["version"])
                need(not stage.exists() and not stage.is_symlink(),"PARTIAL_STAGE_HOLD")
                target=self.releases/candidate["version"]
                if target.exists() or target.is_symlink():self.retire(candidate)
            self.check_tree(before);outcome="ABORTED_BEFORE_COMMIT"
        else:
            keep={e["version"] for e in after.values() if e}
            for e in before.values():
                if e and e["version"] not in keep:
                    t=self.releases/e["version"]
                    if t.exists() or t.is_symlink():self.retire(e)
            self.check_tree(after);outcome="COMMITTED_RECOVERED"
        self.journal.unlink();sync_dir(self.root);return outcome
    def recover(self):
        with self.locked():return self.recover_locked()
    def apply(self,action,expected,candidate=None,interrupt=None):
        with self.locked():
            need(not self.journal.exists() and not self.journal.is_symlink(),"RECOVERY_REQUIRED")
            before=self.state();need(before==expected,"CAS_STATE");self.check_tree(before)
            if candidate:self.entry(candidate)
            after=planner.plan(before,action,candidate)["desired_state"]
            atomic(self.journal,{"action":action,"before":before,"after":after,"candidate":candidate})
            if candidate:
                self.install_copy(candidate)
                self.info(candidate,"version");self.info(candidate,"doctor")
            if interrupt=="before":raise Interrupted("BEFORE_COMMIT")
            need(self.state()==before,"CAS_STATE")
            atomic(self.statefile,after)
            if interrupt=="after":raise Interrupted("AFTER_COMMIT")
            need(self.recover_locked()=="COMMITTED_RECOVERED","COMMIT")
            return after
