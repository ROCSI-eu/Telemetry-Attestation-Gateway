"""EXPERIMENTAL / SYNTHETIC_ONLY / A0_SYNTHETIC / NOT VALIDATION OR PRODUCTION AUTHORIZATION.
Separate verifier process in a registered private sandbox. No proving, no host fallback.
"""
import hashlib,os,selectors,signal,socket,stat,subprocess,time,shutil
from pathlib import Path
APP=Path("/app")
TOOL=Path("/tool")
CRS={"bn254_g1_compressed.dat":"fad8203ae1fd103658d4bb33b2b4cf126a28352b5de4684737cff23cc15fb94b","bn254_g2.dat":"01797bfc4de5a96f0e516a9ea4537d18786dc30cb991aca4274c95822b69c32f"}
BB_SHA="fc9279e32471e036827c911ec9f8106ade987aec91d3e9a55cf4d33ebfb6f2cf"
PINS={"engine/integrated-cli-v0/authentic_package_cli.py":"8e0551347013207d6f4ee19ddde89d57245d0d68","engine/bounded-speed-proof-v0/verify.py":"ad7a3d4e3a5f463206bfaae8a31dfe4d77001b7e","engine/bounded-speed-proof-v0/common.py":"c76abf1c335c61d0a20fa7f6defab756479aa7b3","engine/bounded-speed-v0/bounded_speed.py":"094b0b68c3792aceb907d7735934ca08ca02aaf5"}
class Unavailable(RuntimeError):pass
def need(ok):
    if not ok:raise Unavailable("VERIFIER_OPERATIONAL_FAILURE")
def sha(p):
    with p.open("rb") as f:return hashlib.file_digest(f,"sha256").hexdigest()
def blob(p):
    b=p.read_bytes();return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def check_sources(root):
    for n,h in PINS.items():
        p=root/n;need(p.is_file() and not p.is_symlink() and blob(p)==h)
def gate():
    # Defense in depth: not a replacement for independently reviewed outer launch isolation.
    need(Path(__file__).resolve().parent==APP and socket.if_nameindex()==[(1,"lo")])
    need(not Path("/mnt").exists() and not Path("/media").exists() and not list(Path("/home").iterdir()) and not list(Path("/run").iterdir()))
    need(not Path("/dev/dri").exists() and not list(Path("/dev").glob("ttyUSB*")) and not list(Path("/dev").glob("ttyACM*")))
    fs=os.statvfs("/tmp");need(fs.f_blocks*fs.f_frsize<=256*1024**2)
    need(bool(os.statvfs(APP).f_flag & os.ST_RDONLY) and bool(os.statvfs("/input/package").f_flag & os.ST_RDONLY) and bool(os.statvfs(TOOL/"bb").f_flag & os.ST_RDONLY) and all(bool(os.statvfs(TOOL/"crs"/n).f_flag & os.ST_RDONLY) for n in CRS))
    check_sources(APP)
def prepare_crs():
    need((TOOL/"bb").is_file() and not (TOOL/"bb").is_symlink() and sha(TOOL/"bb")==BB_SHA)
    target=Path("/tmp/crs")
    target.mkdir(mode=0o700,exist_ok=False)
    for n,h in CRS.items():
        p=TOOL/"crs"/n
        need(p.is_file() and not p.is_symlink() and p.stat().st_size<=8*1024**2 and sha(p)==h)
        dest=target/n
        with dest.open("xb") as f:f.write(p.read_bytes())
        dest.chmod(0o600)
        need(sha(dest)==h)
def collect(argv,seconds=25,maximum=16384):
    """Bound wall and stdout while child runs; no stderr exposure; reap own process group."""
    p=subprocess.Popen(argv,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,
        env={"PATH":"/app/bin:/usr/bin:/bin","HOME":"/tmp","TMPDIR":"/tmp","LANG":"C.UTF-8","RAYON_NUM_THREADS":"2","OMP_NUM_THREADS":"2"},
        cwd="/tmp",start_new_session=True)
    data=bytearray();deadline=time.monotonic()+seconds
    try:
        with selectors.DefaultSelector() as s:
            s.register(p.stdout,selectors.EVENT_READ)
            while True:
                left=deadline-time.monotonic();need(left>0)
                if not s.select(left):raise Unavailable("TIMEOUT")
                b=os.read(p.stdout.fileno(),min(4096,maximum+1-len(data)))
                if not b:break
                data.extend(b);need(len(data)<=maximum)
        return p.wait(timeout=max(.001,deadline-time.monotonic())),bytes(data)
    finally:
        try:os.killpg(p.pid,signal.SIGKILL)
        except ProcessLookupError:pass
        p.wait(timeout=3);p.stdout.close()
def run_verified(folder):
    gate()
    need(folder.resolve().parent==Path("/tmp") and folder.name.startswith("tag-inspector-"))
    # One invocation per isolated runtime; no reuse or mutable key cache.
    need(not Path("/tmp/crs").exists())
    try:
        prepare_crs()
        return collect(["/usr/bin/python3","-B","/app/engine/integrated-cli-v0/authentic_package_cli.py","--package-dir",str(folder)])
    except (subprocess.SubprocessError,OSError) as exc:
        raise Unavailable("VERIFIER_OPERATIONAL_FAILURE") from None
    finally:
        target=Path("/tmp/crs")
        if target.is_dir() and not target.is_symlink() and target.stat().st_uid==os.getuid():shutil.rmtree(target)
