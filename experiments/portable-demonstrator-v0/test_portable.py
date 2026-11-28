"""EXPERIMENTAL / SYNTHETIC_ONLY / A0_SYNTHETIC / NOT VALIDATION OR PRODUCTION AUTHORIZATION."""
import hashlib, os, shutil, socket, subprocess, sys, tempfile
from pathlib import Path
assert __debug__ and socket.if_nameindex()==[(1,"lo")]
PIN="9c1cf5e48aac136ce3e625c9827b497252d5325d21f611deb852f487286489bc"
RELEASE=Path("/release")
OUT=Path("/output")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(root,output,pin=PIN,opts=("-I","-B")):
    return subprocess.run([sys.executable,*opts,str(root/"demo.py"),"--release-sha256",pin,"--output",str(output)],capture_output=True,text=True,timeout=12)
def accept(root,out):
    r=run(root,out)
    if r.returncode:print(r.stdout,r.stderr)
    assert r.returncode==0
    assert "Historical exp.4: VALID then; NOT_PERFORMED now; current association NONE" in r.stdout
    assert "Companion CLI: 0.1.0-exp.4 SOURCE_ONLY; verification NOT_PERFORMED" in r.stdout
    assert r.stdout.count("actual crypto NOT_CHECKED")==5
    return r.stdout
def reject(root,out,**kw):
    r=run(root,out,**kw)
    assert r.returncode==2 and "DEMO_REJECTED" in r.stderr
    assert not list(out.iterdir())
with tempfile.TemporaryDirectory(prefix="portable-qa-") as tmp:
    t=Path(tmp); second=t/"relocated";second.mkdir(mode=0o700)
    a=subprocess.run([sys.executable,"-I","-B","/design/assemble_demo.py","/source",str(second)],capture_output=True,text=True,timeout=10)
    assert a.returncode==0,a.stderr
    assert sha(second/"SHA256SUMS")==PIN==sha(RELEASE/"SHA256SUMS")
    def inventory(root):
        return {f.relative_to(root).as_posix():(sha(f),f.stat().st_mode&0o777) for f in root.rglob("*") if f.is_file()}
    assert inventory(second)==inventory(RELEASE)
    print("ASSEMBLY_REPRODUCIBILITY PASS (39 files, independent directory)",flush=True)
    b=t/"out-b";b.mkdir(mode=0o700)
    first=accept(RELEASE,OUT); assert first==accept(second,b)
    names={"common-results.json","EXPERIMENTAL_SYNTHETIC_ONLY_TAGD.bin"}
    assert {f.name for f in OUT.iterdir()}==names=={f.name for f in b.iterdir()}
    # Compare deterministic minimized synthetic outputs without a private evidence mount.
    expected={"common-results.json":"697171ff406e2c12fad06984acf413382b191a3857a85e098004dce0bccac745",
              "EXPERIMENTAL_SYNTHETIC_ONLY_TAGD.bin":"8134c1164bddb3a64186b401c4663f50604288681ac5e6f9b46bcf683e9bee24"}
    for n in names:
        assert (OUT/n).read_bytes()==(b/n).read_bytes()
        assert sha(OUT/n)==expected[n]
    print(first,end="")
    print("RELOCATED_EXECUTION_AND_PREVIOUS_OUTPUT_EQUIVALENCE PASS (2/2 outputs)",flush=True)
    test=subprocess.run([sys.executable,"-I","-B",str(RELEASE/"experiments/claim-envelope-v1-spike/test_common_scenario.py"),str(OUT)],capture_output=True,text=True,timeout=10)
    print(test.stderr,end="");assert test.returncode==0
    fail=t/"fail";fail.mkdir(mode=0o700)
    reject(second,fail,pin="0"*64); print("WRONG_PIN PASS",flush=True)
    extra=second/"extra";extra.write_text("synthetic negative control");reject(second,fail);extra.unlink();print("EXTRA_FILE PASS",flush=True)
    extra.symlink_to(second/"README.md");reject(second,fail);extra.unlink();print("SYMLINK PASS",flush=True)
    target=second/"README.md";orig=target.read_bytes();target.chmod(0o600);target.write_bytes(orig+b"\nmodified\n");reject(second,fail);target.write_bytes(orig);target.chmod(0o400);print("MODIFIED_FILE PASS",flush=True)
    reject(second,fail,opts=("-I","-B","-O"));print("OPTIMIZED_PYTHON PASS",flush=True)
    x=fail/"sentinel";x.write_text("preserve");r=run(second,fail);assert r.returncode==2 and x.read_text()=="preserve" and len(list(fail.iterdir()))==1; x.unlink();print("NONEMPTY_OUTPUT PASS",flush=True)
    assert inventory(second)==inventory(RELEASE)
    print("NEGATIVE_CONTROLS 6/6 PASS",flush=True)
assert not t.exists()
print("OWNED_TEMP_CLEANUP PASS",flush=True)
