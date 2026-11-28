"""EXPERIMENTAL / SYNTHETIC_ONLY / A0_SYNTHETIC / NOT VALIDATION OR PRODUCTION AUTHORIZATION.
All transport responses and grants are artificial, no genuine bb invocation.
"""
import contextlib,io,json,sys,tempfile,unittest,os,subprocess
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent
import assemble
import atexit
# Deterministic isolated source assembly from the checked-in canonical engine.
_ASSEMBLY=tempfile.TemporaryDirectory()
atexit.register(_ASSEMBLY.cleanup)
REPO=ROOT.parents[1]
# A local QA checkout may supply an explicitly isolated synthetic source tree;
# canonical CI uses only its own repository sources.
assemble.assemble(REPO,Path(_ASSEMBLY.name))
sys.path.insert(0,_ASSEMBLY.name)
import tag_cli as c
import verify_dispatch as v
p=c.engine()
import runtime_plan as rp
class QA(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        self.gd=self.root/"grant";self.gd.mkdir(mode=0o700)
        self.pkg=self.root/"package";self.pkg.mkdir(mode=0o700)
        self.prov=p.enc({"retention_not_after_utc":"2026-12-04T17:20:25Z"})
        self.review=p.enc({"issued_utc":"2026-11-27T17:30:00Z","expires_utc":"2026-12-04T17:20:25Z"})
        for n,b in (("review",self.review),("provenance",self.prov)):
            (self.root/n).write_bytes(b);(self.root/n).chmod(0o600)
        self.args=SimpleNamespace(release_sha256=c.sha(c.ROOT/"SHA256SUMS"),package_dir=str(self.pkg),package_sha256="a"*64,review=str(self.root/"review"),review_sha256=p.sha(self.review),provenance=str(self.root/"provenance"),grant_dir=str(self.gd),grant_sha256="",profile=str(self.root/"profile"),profile_sha256="c"*64)
        self.now=datetime(2026,11,27,18,tzinfo=timezone.utc)
        self.grant={"schema":"TAG_CLI_EXECUTION_GRANT_V2_EXPERIMENTAL","labels":c.MARKS,"release_sha256":self.args.release_sha256,"package_sha256":self.args.package_sha256,"review_sha256":self.args.review_sha256,"provenance_sha256":p.sha(self.prov),"profile_sha256":self.args.profile_sha256,"action":"REVERIFY","max_attempts":1,"issued_utc":"2026-11-27T17:40:00Z","expires_utc":"2026-12-04T17:20:25Z","scope":"LOCAL_ONLY_NO_PUBLICATION"}
        self.write_grant()
    def tearDown(self):self.tmp.cleanup()
    def write_grant(self):
        b=p.enc(self.grant);f=self.gd/"execution-grant.json";f.write_bytes(b);f.chmod(0o600);self.args.grant_sha256=p.sha(b);return b
    def grantcheck(self):
        b=self.write_grant();return v.grant_check(b,self.args,p,self.now,self.prov,self.review)
    def typed(self,crypto="VALID",**kw):
        fields=dict(origin="CURRENT_VERIFIER",suite=p.SUITE,package="ACCEPTED",input="ACCEPTED",crypto=crypto,verification="PERFORMED")
        fields.update(kw);return p.i.Result(**fields).export().encode()
    def invoke(self,rc=0,data=None,fail=None,eligible=True,deps=True,changed=False):
        if data is None:data=self.typed()
        def fake_plan(staged,profile):return ["fixed-test-only",str(c.ROOT/"app"),str(staged),"--unshare-all","--clearenv"]
        with contextlib.ExitStack() as s:
            s.enter_context(patch.object(v,"utcnow",return_value=self.now))
            s.enter_context(patch.object(p,"load_package",return_value={"artificial":b"not proof"}))
            s.enter_context(patch.object(p,"fingerprint",return_value="b"*64 if changed else self.args.package_sha256))
            s.enter_context(patch.object(p,"inspect_for_action",return_value={"status":"ELIGIBLE_FOR_SCOPED_ACTION_REVIEW" if eligible else "REJECTED"}))
            s.enter_context(patch.object(c,"doctor",return_value={"status":"DEPENDENCY_PINS_MATCH" if deps else "HOLD"}))
            stage=s.enter_context(patch.object(p,"_stage_snapshot",return_value=self.args.package_sha256))
            plan=s.enter_context(patch.object(rp,"command",side_effect=fake_plan))
            run=s.enter_context(patch.object(v,"run_transport",side_effect=fail,return_value=(rc,data)))
            s.enter_context(patch("subprocess.Popen",side_effect=AssertionError("NO REAL PROCESS")))
            result,code=v.dispatch(self.args,p,{})
            self.calls=run.call_count
            if run.called:self.assertFalse(run.call_args.args[1].exists())
            return result,code
    def test_release_exact(self):
        self.assertEqual(len(c.check_release(c.ROOT,self.args.release_sha256)),17)
    def test_cli_parse(self):
        a=c.parse(["--release-sha256",self.args.release_sha256,"verify","--package-dir",self.args.package_dir,"--package-sha256",self.args.package_sha256,"--review",self.args.review,"--review-sha256",self.args.review_sha256,"--provenance",self.args.provenance,"--grant-dir",self.args.grant_dir,"--grant-sha256",self.args.grant_sha256])
        self.assertEqual(a.command,"verify")
    def test_grant_binding(self):
        self.assertEqual(self.grantcheck()["action"],"REVERIFY")
        self.grant["release_sha256"]="b"*64
        with self.assertRaisesRegex(c.Rejected,"GRANT_BINDING"):self.grantcheck()
    def test_wrong_package(self):
        self.grant["package_sha256"]="b"*64
        with self.assertRaisesRegex(c.Rejected,"GRANT_BINDING"):self.grantcheck()
    def test_wrong_provenance(self):
        self.grant["provenance_sha256"]="b"*64
        with self.assertRaisesRegex(c.Rejected,"GRANT_BINDING"):self.grantcheck()
    def test_wrong_action(self):
        self.grant["action"]="RETAIN"
        with self.assertRaisesRegex(c.Rejected,"GRANT_SCOPE"):self.grantcheck()
    def test_bool_attempt_count(self):
        self.grant["max_attempts"]=True
        with self.assertRaisesRegex(c.Rejected,"GRANT_SCOPE"):self.grantcheck()
    def test_expired(self):
        self.grant["expires_utc"]="2026-11-27T18:00:00Z"
        with self.assertRaisesRegex(c.Rejected,"GRANT_TIME"):self.grantcheck()
    def test_retention_not_extended(self):
        self.grant["expires_utc"]="2026-12-05T00:00:00Z"
        with self.assertRaisesRegex(c.Rejected,"GRANT_TIME"):self.grantcheck()
    def test_grant_pin(self):
        b=self.write_grant();self.args.grant_sha256="b"*64
        with self.assertRaisesRegex(c.Rejected,"GRANT_PIN"):v.grant_check(b,self.args,p,self.now,self.prov,self.review)
    def test_mock_valid_response_contract(self):
        r,rc=self.invoke();self.assertEqual((r["crypto"],rc,self.calls),("VALID",0,1))
        self.assertEqual(r["cleanup"],"PASS");self.assertTrue((self.gd/"attempt.started").is_file())
        # This is artificial transport, no observed proof validity.
    def test_mock_invalid_response_contract(self):
        r,rc=self.invoke(4,self.typed("INVALID",reason="PROOF_REJECTED"));self.assertEqual((r["crypto"],rc,self.calls),("INVALID",4,1))
    def test_mock_false_origin(self):
        r,rc=self.invoke(data=self.typed(origin="MOCK"));self.assertEqual((r["crypto"],rc),("UNVERIFIABLE",5))
    def test_exit_mismatch(self):
        r,rc=self.invoke(4);self.assertEqual((r["crypto"],rc),("UNVERIFIABLE",5))
    def test_scope_mismatch(self):
        data=json.loads(self.typed());data["publication"]="PERFORMED"
        r,rc=self.invoke(data=p.enc(data));self.assertEqual((r["crypto"],rc),("UNVERIFIABLE",5))
    def test_malformed(self):
        r,rc=self.invoke(data=b"{");self.assertEqual((r["crypto"],rc),("UNVERIFIABLE",5))
    def test_oversize(self):
        r,rc=self.invoke(data=b"x"*16385);self.assertEqual((r["crypto"],rc),("UNVERIFIABLE",5))
    def test_timeout_consumed(self):
        r,rc=self.invoke(fail=subprocess.TimeoutExpired("synthetic",45));self.assertEqual((r["crypto"],rc,self.calls),("UNVERIFIABLE",5,1))
        r,rc=self.invoke();self.assertEqual((rc,self.calls,r["attempts"]),(5,0,0))
    def test_no_retry_after_success(self):
        self.invoke();r,rc=self.invoke();self.assertEqual((rc,self.calls,r["attempts"]),(5,0,0))
    def test_review_gate_before_execution(self):
        r,rc=self.invoke(eligible=False);self.assertEqual((rc,self.calls,r["attempts"]),(5,0,0));self.assertFalse((self.gd/"attempt.started").exists())
    def test_dependency_gate_before_execution(self):
        r,rc=self.invoke(deps=False);self.assertEqual((rc,self.calls,r["attempts"]),(5,0,0));self.assertFalse((self.gd/"attempt.started").exists())
    def test_changed_original_fails_closed(self):
        r,rc=self.invoke(changed=True);self.assertEqual((r["crypto"],rc,self.calls),("UNVERIFIABLE",5,1))
    def test_extra_grant_file(self):
        (self.gd/"extra").touch();r,rc=self.invoke();self.assertEqual((rc,self.calls),(5,0))
    def test_public_grant(self):
        self.gd.chmod(0o755);r,rc=self.invoke();self.assertEqual((rc,self.calls),(5,0))
    def test_grant_overlap(self):
        self.args.grant_dir=str(self.pkg);r,rc=self.invoke();self.assertEqual((rc,self.calls),(5,0))
    def test_lock_contention(self):
        gd,fd=v.open_grant(self.args)
        try:
            r,rc=self.invoke();self.assertEqual((rc,self.calls),(5,0))
        finally:os.close(fd)
    def test_existing_runtime_plan_contract(self):
        # Actual unchanged plan builder; synthetic input parser boundary only,
        # no child process. Real local binary/CRS digest checks remain enabled.
        with patch.object(rp,"snapshot",return_value={}),patch.object(rp,"validate",return_value=None),patch.object(rp,"check",return_value=Path("/synthetic-toolchain")),patch.object(rp,"sha",side_effect=lambda f:rp.BB_SHA if f.name=="bb" else rp.CRS[f.name]),patch("subprocess.Popen",side_effect=AssertionError("NO PROCESS")):
            cmd=rp.command(self.pkg,{})
        self.assertIn("--unshare-all",cmd);self.assertIn("--clearenv",cmd)
        self.assertNotIn("--bind",cmd);self.assertNotIn("--share-net",cmd)
        self.assertEqual(cmd[-1],"/app/verify_entry.py")
        self.assertIn(str(c.ROOT/"app"),cmd);self.assertIn(str(self.pkg),cmd)
        self.assertNotIn(str(c.ROOT),cmd)
        self.assertIn("--as=2147483648",cmd)
    def test_missing_grant(self):
        (self.gd/"execution-grant.json").unlink()
        r,rc=self.invoke();self.assertEqual((rc,self.calls,r["attempts"]),(5,0,0))
    def test_profile_binding(self):
        self.grant["profile_sha256"]="d"*64
        with self.assertRaisesRegex(c.Rejected,"GRANT_BINDING"):self.grantcheck()
    def test_profile_required(self):
        import io
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(c.main(["--release-sha256",self.args.release_sha256,"doctor"]),2)
    def test_profile_validation(self):
        import local_profile as lp
        record={"schema":"TAG_LOCAL_PROFILE_V1_EXPERIMENTAL","labels":c.MARKS,"platform":"Linux x86_64","python":"3.14.4","host":{n:"a"*64 for n in lp.HOST},"toolchain_root":"/synthetic-toolchain","bb":lp.BB_SHA,"crs":lp.CRS}
        f=Path(self.args.profile)
        def load():
            b=p.enc(record);f.write_bytes(b);f.chmod(0o600);return lp.load(f,p.sha(b))
        self.assertEqual(load(),record)
        record["toolchain_root"]="/usr"
        with self.assertRaises(ValueError):load()
    def test_assembly_repeat(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(assemble.assemble(REPO,Path(d)),self.args.release_sha256)
    def test_lifecycle_plan_preserves_records(self):
        import lifecycle as l
        old={"version":"0.1.0-exp.3","seal":"a"*64}
        new={"version":"0.1.0-exp.4","seal":"b"*64}
        state=l.plan({"current":old,"previous":None},"update",new)["desired_state"]
        self.assertEqual(l.plan(state,"rollback")["desired_state"],{"current":old,"previous":new})
        self.assertEqual(l.plan(state,"uninstall")["evidence"],"PRESERVE")
    def test_no_private_display_dependency(self):
        self.assertFalse((c.ROOT/"app/bound_result.py").exists())
        self.assertFalse(hasattr(p.i.Session,"show_recorded"))
        self.assertFalse(hasattr(p.i.Session,"show_mock"))
    def test_profile_pin_and_unknown_field(self):
        import local_profile as lp
        f=Path(self.args.profile);b=p.enc({"synthetic":True});f.write_bytes(b);f.chmod(0o600)
        for pin in ("0"*64,p.sha(b)):
            with self.assertRaises(ValueError):lp.load(f,pin)
    def test_actual_lifecycle_contract_no_process(self):
        from local_lifecycle import Local,EMPTY
        entry={"version":c.VERSION,"seal":self.args.release_sha256}
        root=self.root/"owned-lifecycle"
        with patch.object(Local,"info",return_value={}) as info,patch("subprocess.Popen",side_effect=AssertionError("NO PROCESS")):
            mgr=Local(root,{c.VERSION:(c.ROOT,self.args.release_sha256)},create=True,profile=(self.args.profile,self.args.profile_sha256))
            state=mgr.apply("install",EMPTY,entry)
            self.assertEqual(state,{"current":entry,"previous":None})
            self.assertEqual(info.call_count,2)
            self.assertEqual(mgr.apply("uninstall",state),EMPTY)
            self.assertEqual(mgr.recover(),"CLEAN")
            self.assertEqual(list(mgr.releases.iterdir()),[])
        self.assertTrue((self.gd/"execution-grant.json").is_file())
    def test_lifecycle_profile_forwarding(self):
        from local_lifecycle import Local,EMPTY
        e={"version":c.VERSION,"seal":self.args.release_sha256}
        mgr=Local(self.root/"info-lifecycle",{c.VERSION:(c.ROOT,e["seal"])},create=True,profile=(self.args.profile,self.args.profile_sha256))
        with mgr.locked():mgr.install_copy(e)
        response=SimpleNamespace(returncode=0,stdout=p.enc({"labels":c.MARKS,"status":"DEPENDENCY_PINS_MATCH","runtime_acceptance":"NOT_PERFORMED"}))
        with patch("local_lifecycle.subprocess.run",return_value=response) as run:
            mgr.info(e,"doctor")
            args=run.call_args.args[0]
            self.assertEqual(args[-5:],["--profile",self.args.profile,"--profile-sha256",self.args.profile_sha256,"doctor"])
    def test_assembly_reject_nonempty(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d)/"unrelated").write_text("keep")
            with self.assertRaises(ValueError):assemble.assemble(REPO,Path(d))
            self.assertEqual((Path(d)/"unrelated").read_text(),"keep")
    def test_explicit_permissions_and_no_repair_of_existing(self):
        import stat
        from local_lifecycle import Local,EMPTY
        entry={"version":c.VERSION,"seal":self.args.release_sha256}
        def assert_modes(root):
            for f in root.rglob("*"):
                expected=0o700 if f.is_dir() else 0o500 if f.name=="bb" else 0o400
                self.assertEqual(stat.S_IMODE(f.stat().st_mode),expected,str(f.relative_to(root)))
        for mask in (0o022,0o077):
            prior=os.umask(mask)
            try:
                with tempfile.TemporaryDirectory() as d:
                    base=Path(d);release=base/"release";release.mkdir(mode=0o700)
                    seal=assemble.assemble(REPO,release)
                    self.assertEqual(seal,entry["seal"]);assert_modes(release)
                    mgr=Local(base/"install",{c.VERSION:(release,seal)},create=True)
                    for n in ("lock","state.json"):
                        self.assertEqual(stat.S_IMODE((mgr.root/n).stat().st_mode),0o600)
                    with patch.object(Local,"info",return_value={}),patch("subprocess.Popen",side_effect=AssertionError("NO PROCESS")):
                        state=mgr.apply("install",EMPTY,entry)
                        installed=mgr.check_version(entry);assert_modes(installed)
                        (installed/"app").chmod(0o755)
                        with self.assertRaises(c.Rejected):mgr.check_version(entry)
                        self.assertEqual(stat.S_IMODE((installed/"app").stat().st_mode),0o755)
                        (installed/"app").chmod(0o700)
                        self.assertEqual(mgr.apply("uninstall",state),EMPTY)
            finally:os.umask(prior)
if __name__=="__main__":unittest.main(verbosity=2)
