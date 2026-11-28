"""EXPERIMENTAL / SYNTHETIC_ONLY / A0_SYNTHETIC / NOT VALIDATION OR PRODUCTION AUTHORIZATION.
Deterministic source-only assembly; no installation or dependency acquisition.
"""
import argparse,hashlib,os,stat,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
MARKS="EXPERIMENTAL / SYNTHETIC_ONLY / A0_SYNTHETIC / NOT VALIDATION OR PRODUCTION AUTHORIZATION"
CANONICAL={"experiments/integrated-cli-v0/authentic_package_cli.py":"8e0551347013207d6f4ee19ddde89d57245d0d68","experiments/bounded-speed-proof-v0/verify.py":"ad7a3d4e3a5f463206bfaae8a31dfe4d77001b7e","experiments/bounded-speed-proof-v0/common.py":"c76abf1c335c61d0a20fa7f6defab756479aa7b3","experiments/bounded-speed-v0/bounded_speed.py":"094b0b68c3792aceb907d7735934ca08ca02aaf5","LICENSE":"2cd3e21e87cf075b309a4e9c0edcc6ae0b329752"}
LOCAL=("tag_cli.py","verify_dispatch.py","lifecycle.py","local_lifecycle.py","app/adapter.py","app/inspector.py","app/runtime_plan.py","app/verify_entry.py","app/local_profile.py","app/bin/bb","app/portable/portable.py")
def need(ok):
    if not ok:raise ValueError("ASSEMBLY_REJECTED")
def read(f):
    need(f.is_file() and not f.is_symlink() and f.stat().st_size<=262144)
    return f.read_bytes()
def blob(b):return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def assemble(repo,out):
    repo=Path(repo).resolve();out=Path(out)
    need(out.is_dir() and not out.is_symlink() and out.stat().st_uid==os.getuid() and stat.S_IMODE(out.stat().st_mode)==0o700 and not list(out.iterdir()))
    need(not out.resolve().is_relative_to(HERE))
    # Validate all inputs before any write. Only approved canonical engine blobs.
    data={}
    for n,h in CANONICAL.items():
        b=read(repo/n);need(blob(b)==h)
        data["LICENSE" if n=="LICENSE" else "app/engine/"+n.removeprefix("experiments/")]=b
    for n in LOCAL:data[n]=read(HERE/"source"/n)
    data["README.md"]=read(HERE/"README.md")
    inventory="".join(hashlib.sha256(b).hexdigest()+"  "+n+"\n" for n,b in sorted(data.items())).encode()
    for n,b in sorted({**data,"SHA256SUMS":inventory}.items()):
        f=out/n
        parent=out
        for part in Path(n).parts[:-1]:
            parent=parent/part
            try:parent.mkdir(mode=0o700)
            except FileExistsError:pass
            st=parent.lstat()
            need(stat.S_ISDIR(st.st_mode) and st.st_uid==os.getuid() and stat.S_IMODE(st.st_mode)==0o700)
        fd=os.open(f,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        with os.fdopen(fd,"wb") as h:
            h.write(b);h.flush();os.fchmod(h.fileno(),0o500 if n=="app/bin/bb" else 0o400)
    return hashlib.sha256(inventory).hexdigest()
def main():
    a=argparse.ArgumentParser(description=MARKS)
    a.add_argument("--out",required=True);args=a.parse_args()
    try:print(MARKS+"\nSOURCE_ONLY "+assemble(HERE.parents[1],Path(args.out)));return 0
    except (OSError,ValueError):print(MARKS+"\nASSEMBLY_REJECTED");return 2
if __name__=="__main__":sys.exit(main())
