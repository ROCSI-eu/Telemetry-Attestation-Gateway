"""EXPERIMENTAL / SYNTHETIC_ONLY / A0_SYNTHETIC / NOT VALIDATION OR PRODUCTION AUTHORIZATION."""
import hashlib, importlib.util, json, os, stat, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
MARKS="EXPERIMENTAL / SYNTHETIC_ONLY / A0_SYNTHETIC / NOT VALIDATION OR PRODUCTION AUTHORIZATION"
def need(ok):
    if not ok: raise ValueError("ASSEMBLY_REJECTED")
def digest(b):return hashlib.sha256(b).hexdigest()
def blob(b):return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def private(p):
    s=p.lstat()
    need(stat.S_ISDIR(s.st_mode) and s.st_uid==os.getuid() and stat.S_IMODE(s.st_mode)==0o700)
def main(repo,out):
    need(socket_ok())
    private(out);need(not list(out.iterdir()))
    pins=json.loads((HERE/"source-pins.json").read_text())
    for name,pin in pins.items():
        f=repo/name
        need(f.is_file() and not f.is_symlink() and f.resolve()==f and blob(f.read_bytes())==pin)
    f=repo/"experiments/companion-cli-v0/assemble.py"
    spec=importlib.util.spec_from_file_location("companion_assembly",f);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    comp=out/"companion";comp.mkdir(mode=0o700)
    cp=module.assemble(repo,comp)
    for n in pins:
        if n.startswith(("experiments/claim-envelope-v1-spike/","experiments/source-proof-binding-v0/","experiments/mavlink-normalization-v0/","experiments/bounded-speed-v0/")):
            target=out/n;target.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
            target.write_bytes((repo/n).read_bytes());target.chmod(0o400)
    for n in ("demo.py","README.md","source-pins.json"):
        target=out/n;target.write_bytes((HERE/n).read_bytes());target.chmod(0o400)
    meta={"version":"0.1.0-exp.1","source_main":"4f9c2f2b746f938bd589062b0bf947d98e7166fc","companion_release_sha256":cp,"markings":MARKS,"historical_evidence":"COMPANION_EXP4_HISTORICAL_ONLY","classification":"Experimental / Synthetic evidence / Unreviewed / Synthetic data / Local-only / No external assurance claim"}
    (out/"release.json").write_text(json.dumps(meta,sort_keys=True,indent=2)+"\n");(out/"release.json").chmod(0o400)
    inventory="".join(digest(f.read_bytes())+"  "+f.relative_to(out).as_posix()+"\n" for f in sorted(out.rglob("*")) if f.is_file())
    (out/"SHA256SUMS").write_text(inventory);(out/"SHA256SUMS").chmod(0o400)
    print("SOURCE_PINS",len(pins),"COMPANION",cp,"RELEASE",digest(inventory.encode()))
def socket_ok():
    import socket
    return socket.if_nameindex()==[(1,"lo")]
if __name__=="__main__":
    main(Path(sys.argv[1]).resolve(),Path(sys.argv[2]).resolve())
