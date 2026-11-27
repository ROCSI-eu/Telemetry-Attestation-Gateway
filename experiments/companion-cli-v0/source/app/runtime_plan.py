"""EXPERIMENTAL / SYNTHETIC_ONLY / A0_SYNTHETIC / NOT VALIDATION OR PRODUCTION AUTHORIZATION.
Fixed non-GUI outer sandbox plan; not an active launcher in CODE-ONLY scope.
"""
from pathlib import Path
import os,stat
from adapter import BB_SHA,CRS,sha,check_sources,need
from inspector import snapshot,validate,stage
HERE=Path(__file__).resolve().parent
from local_profile import check
def command(staged,profile):
    # Caller creates an owned private temporary snapshot, then mounts only it.
    need(staged.is_dir() and not staged.is_symlink() and staged.stat().st_uid==os.getuid() and stat.S_IMODE(staged.stat().st_mode)==0o700)
    validate(snapshot(staged));check_sources(HERE)
    TC=check(profile,HERE)
    need(sha(TC/"tools/bb")==BB_SHA)
    for name,digest in CRS.items():need(sha(TC/"cache/crs"/name)==digest)
    cmd=["/usr/bin/timeout","--kill-after=3s","40s","/usr/bin/prlimit","--as=2147483648","--cpu=30","--fsize=8388608","--nofile=64","--core=0","--",
         "/usr/bin/bwrap","--unshare-all","--die-with-parent","--new-session","--clearenv","--ro-bind","/usr","/usr","--symlink","usr/lib","/lib","--symlink","usr/lib64","/lib64","--symlink","usr/bin","/bin",
         "--proc","/proc","--dev","/dev","--size","268435456","--tmpfs","/tmp","--dir","/run","--dir","/home",
         "--ro-bind",str(HERE),"/app","--ro-bind",str(staged),"/input/package","--dir","/tool/crs","--ro-bind",str(TC/"tools/bb"),"/tool/bb"]
    for name in CRS:cmd+=["--ro-bind",str(TC/"cache/crs"/name),"/tool/crs/"+name]
    return cmd+["--setenv","PATH","/usr/bin:/bin","--setenv","HOME","/tmp","--setenv","TMPDIR","/tmp","--chdir","/tmp","/usr/bin/python3","-B","/app/verify_entry.py"]
