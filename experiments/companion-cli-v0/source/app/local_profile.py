"""EXPERIMENTAL / SYNTHETIC_ONLY / A0_SYNTHETIC / NOT VALIDATION OR PRODUCTION AUTHORIZATION.
Explicit owner-pinned local profile, no default host path or arbitrary executable.
"""
import hashlib,json,os,stat,platform,re
from pathlib import Path
from adapter import BB_SHA,CRS,check_sources,sha
MARKS=["EXPERIMENTAL","SYNTHETIC_ONLY","A0_SYNTHETIC","NOT VALIDATION OR PRODUCTION AUTHORIZATION"]
HOST=("python3","bwrap","prlimit","timeout")
def need(ok):
    if not ok:raise ValueError("LOCAL_PROFILE_REJECTED")
def unique(pairs):
    d={}
    for k,v in pairs:
        need(k not in d);d[k]=v
    return d
def digest(b):return hashlib.sha256(b).hexdigest()
def load(path,pin):
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
    with os.fdopen(fd,"rb") as h:
        s=os.fstat(h.fileno());need(stat.S_ISREG(s.st_mode) and s.st_uid==os.getuid() and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o600 and 0<s.st_size<=4096)
        b=h.read(4097);need(len(b)==s.st_size and digest(b)==pin)
    try:d=json.loads(b,object_pairs_hook=unique,parse_constant=lambda _:(_ for _ in ()).throw(ValueError("LOCAL_PROFILE_REJECTED")))
    except (RecursionError,UnicodeError):raise ValueError("LOCAL_PROFILE_REJECTED") from None
    need(type(d) is dict and set(d)=={"schema","labels","platform","python","host","toolchain_root","bb","crs"})
    need(d["schema"]=="TAG_LOCAL_PROFILE_V1_EXPERIMENTAL" and d["labels"]==MARKS and d["platform"]=="Linux x86_64")
    need(type(d["python"]) is str and re.fullmatch(r"3\.[0-9]+\.[0-9]+",d["python"]))
    need(type(d["host"]) is dict and set(d["host"])==set(HOST) and all(type(x) is str and re.fullmatch("[0-9a-f]{64}",x) for x in d["host"].values()))
    need(d["bb"]==BB_SHA and d["crs"]==CRS)
    need(type(d["toolchain_root"]) is str)
    root=Path(d["toolchain_root"])
    need(root.is_absolute() and root!=Path("/") and root.resolve()==root)
    need(not any(root==Path(n) or root.is_relative_to(n) for n in ("/proc","/sys","/dev","/run","/etc","/usr","/bin","/lib","/lib64")))
    return d
def check(profile,app):
    need(platform.system()+" "+platform.machine()==profile["platform"] and platform.python_version()==profile["python"])
    for n,h in profile["host"].items():
        f=Path("/usr/bin")/n;need(f.is_file() and os.access(f,os.X_OK) and sha(f)==h)
    check_sources(app)
    root=Path(profile["toolchain_root"]);need(root.is_dir() and root.resolve()==root)
    for n,h in {"tools/bb":BB_SHA,**{"cache/crs/"+n:h for n,h in CRS.items()}}.items():
        f=root/n;need(f.is_file() and f.resolve()==f and sha(f)==h)
    return root
