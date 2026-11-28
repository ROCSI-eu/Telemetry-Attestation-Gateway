"""EXPERIMENTAL / SYNTHETIC_ONLY / A0_SYNTHETIC / NOT VALIDATION OR PRODUCTION AUTHORIZATION."""
import gzip, hashlib, io, os, socket, stat, tarfile
from pathlib import Path
assert __debug__ and socket.if_nameindex()==[(1,"lo")]
root=Path("/release"); out=Path("/archive/TAG-Portable-Demonstrator-0.1.0-exp.1.tar.gz")
def make():
    raw=io.BytesIO()
    with gzip.GzipFile(filename="",mode="wb",fileobj=raw,mtime=0) as zipped:
        with tarfile.open(fileobj=zipped,mode="w",format=tarfile.USTAR_FORMAT) as tar:
            for p in [root,*sorted(root.rglob("*"))]:
                st=p.lstat()
                name="TAG-Portable-Demonstrator/"+p.relative_to(root).as_posix()
                info=tarfile.TarInfo(name.rstrip("/"));info.mode=stat.S_IMODE(st.st_mode)
                assert not p.is_symlink() and (stat.S_ISDIR(st.st_mode) or stat.S_ISREG(st.st_mode))
                if p.is_dir():
                    info.type=tarfile.DIRTYPE;tar.addfile(info)
                else:
                    data=p.read_bytes();info.size=len(data);tar.addfile(info,io.BytesIO(data))
    return raw.getvalue()
a=make();assert a==make()
with tarfile.open(fileobj=io.BytesIO(a),mode="r:gz") as t:
    expected={f.relative_to(root).as_posix():f for f in root.rglob("*") if f.is_file()}
    actual={}
    for m in t:
        assert m.isdir() or m.isfile()
        if m.isfile():
            n=m.name.removeprefix("TAG-Portable-Demonstrator/")
            assert n in expected and n not in actual and m.mode==stat.S_IMODE(expected[n].stat().st_mode)
            data=t.extractfile(m).read();assert data==expected[n].read_bytes();actual[n]=1
    assert set(actual)==set(expected)
with out.open("xb") as f:f.write(a)
print("ARCHIVE_REPRODUCIBILITY PASS; inventory",len(actual),"files;",len(a),"bytes;",hashlib.sha256(a).hexdigest())
