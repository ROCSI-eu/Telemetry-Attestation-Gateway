"""EXPERIMENTAL / SYNTHETIC_ONLY / A0_SYNTHETIC / NOT VALIDATION OR PRODUCTION AUTHORIZATION."""
from pathlib import Path
from inspector import Session,Result
from adapter import gate,run_verified,Unavailable
def main():
    try:gate()
    except (Unavailable,OSError,ValueError):
        print(Result(crypto="UNVERIFIABLE",reason="ISOLATION_NOT_ESTABLISHED").export(),end="");return 5
    s=Session();s.select(Path("/input/package"))
    if s.can_verify:s.verify()
    print(s.result.export(),end="")
    return {"VALID":0,"INVALID":4}.get(s.result.crypto,5 if s.result.package!="REJECTED" else 2)
if __name__=="__main__":raise SystemExit(main())
