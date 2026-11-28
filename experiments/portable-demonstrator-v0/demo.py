"""EXPERIMENTAL / SYNTHETIC_ONLY / A0_SYNTHETIC / NOT VALIDATION OR PRODUCTION AUTHORIZATION.
Non-cryptographic UX prototype — no proof generated or verified."""
import argparse, hashlib, json, os, re, socket, stat, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
MARKS="EXPERIMENTAL / SYNTHETIC_ONLY / A0_SYNTHETIC / NOT VALIDATION OR PRODUCTION AUTHORIZATION"
def need(ok,reason):
    if not ok:raise ValueError(reason)
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def private(p):
    s=p.lstat();need(stat.S_ISDIR(s.st_mode) and s.st_uid==os.getuid() and stat.S_IMODE(s.st_mode)==0o700,"PRIVATE_DIRECTORY")
def regular(f):
    s=f.lstat();need(stat.S_ISREG(s.st_mode) and s.st_uid==os.getuid() and s.st_nlink==1 and not s.st_mode&0o077 and 0<s.st_size<=1024*1024,"RELEASE_FILE")
def check(pin):
    private(ROOT);m=ROOT/"SHA256SUMS";regular(m)
    need(re.fullmatch("[a-f0-9]{64}",pin) and sha(m)==pin,"RELEASE_PIN")
    rows={}
    for l in m.read_text().splitlines():
        h,sep,n=l.partition("  ");p=Path(n)
        need(sep and re.fullmatch("[a-f0-9]{64}",h) and n not in rows and not p.is_absolute() and p.as_posix()==n and all(x not in (".","..") for x in p.parts) and n!="SHA256SUMS","MANIFEST")
        rows[n]=h
    dirs={p.as_posix() for n in rows for p in Path(n).parents if p!=Path(".")}
    actual=set()
    for f in ROOT.rglob("*"):
        n=f.relative_to(ROOT).as_posix()
        need(not f.is_symlink(),"SYMLINK")
        if f.is_dir():private(f);need(n in dirs,"EXTRA_DIRECTORY")
        else:regular(f);actual.add(n)
    need(actual==set(rows)|{"SHA256SUMS"},"FILE_SET")
    for n,h in rows.items():need(sha(ROOT/n)==h,"RELEASE_CHANGED")
    return json.loads((ROOT/"release.json").read_text())
def main():
    a=argparse.ArgumentParser(description=MARKS+" — no proof generated or verified")
    a.add_argument("--release-sha256",required=True);a.add_argument("--output",required=True,type=Path)
    args=a.parse_args()
    try:
        need(__debug__ and sys.flags.dont_write_bytecode and sys.flags.isolated,"PYTHON_FLAGS")
        need(socket.if_nameindex()==[(1,"lo")],"ISOLATION_REQUIRED")
        meta=check(args.release_sha256)
        out=args.output;private(out);need(out.resolve()==out and not out.is_relative_to(ROOT) and not ROOT.is_relative_to(out) and not list(out.iterdir()),"OUTPUT_NOT_EMPTY_OR_SEPARATE")
        p=subprocess.run([sys.executable,"-I","-B",str(ROOT/"companion/tag_cli.py"),"--release-sha256",meta["companion_release_sha256"],"version"],check=True,capture_output=True,text=True,timeout=10)
        v=json.loads(p.stdout);need(v["version"]=="0.1.0-exp.4" and v["execution"]=="NOT_PERFORMED","COMPANION_VERSION")
        sys.path.insert(0,str(ROOT/"experiments/claim-envelope-v1-spike"))
        import common_scenario
        common_scenario.run(out)
        result=json.loads((out/"common-results.json").read_text())
        print(MARKS)
        print("Companion CLI:",v["version"],"SOURCE_ONLY; verification NOT_PERFORMED")
        for row in result["samples"]+result["unavailable_cases"]:
            print("Synthetic ordinal",row["ordinal"],row["admission"],row["reason"],"actual crypto NOT_CHECKED")
        print("Historical exp.4: VALID then; NOT_PERFORMED now; current association NONE")
        print("No proof generated or verified; no publication or relying-party decision.")
        return 0
    except (OSError,ValueError,RuntimeError,KeyError,subprocess.SubprocessError) as e:
        print(MARKS+"\nDEMO_REJECTED",file=sys.stderr);return 2
if __name__=="__main__":sys.exit(main())
