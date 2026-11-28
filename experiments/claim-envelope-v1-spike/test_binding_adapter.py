"""EXPERIMENTAL / SYNTHETIC_ONLY / A0_SYNTHETIC / NOT VALIDATION OR PRODUCTION AUTHORIZATION."""
import copy
import hashlib
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch
import codec
import vectors
from binding_adapter import BindingSession, openings, status_mac, scope_for, status_bytes
from binding_reference import authorized_digest, parser
from trusted_time import receipt_mac
from test_temporal_gate import CONFIG, sample

from scenario_fixture import TIME, STATUS, SECRET, NONCE, NOW, status, pin, fixture, at_speed
class Integration(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)
        self.status=status()
        self.session=self.open(initialize=True)
    def open(self,*,initialize=False,s=None,now=NOW):
        return BindingSession(state_dir=self.path,config=CONFIG,time_key=TIME,status_key=STATUS,source_secret=SECRET,status_pin=pin(self.status if s is None else s),clock=lambda:now,initialize=initialize)
    def submit(self,args=None,session=None,s=None,signature=None):
        s=self.status if s is None else s
        return (session or self.session).accept(*(fixture() if args is None else args),s,status_mac(STATUS,s) if signature is None else signature)
    def blocked(self,reason,**kwargs):
        old=(self.path/"state.json").read_bytes()
        out=self.submit(**kwargs)
        self.assertEqual(out["admission"],"HOLD");self.assertIn(reason,out["reason"])
        self.assertEqual(out["actual_crypto"],"NOT_CHECKED");self.assertEqual(out["verification"],"NOT_PERFORMED")
        self.assertEqual((self.path/"state.json").read_bytes(),old)
    def test_positive_and_restart(self):
        self.assertEqual(self.submit()["admission"],"SYNTHETIC_CONTRACT_ACCEPTED")
        self.blocked("CROSS_CAPTURE_REPLAY",session=self.open())
        self.assertEqual(self.submit(fixture(sample(100002,1001),b"M"*32),session=self.open())["replay_commit"],"LOCAL_ATOMIC_COMMIT")
    def test_opening_mutation_and_placeholder(self):
        w,c,r,n=fixture()
        self.blocked("OPENING_BINDING",args=(w,c,r,b"Q"*32))
        x=codec.decode(w);x["proof"]["bytes"]=b"fake"
        self.blocked("PLACEHOLDER_MISMATCH",args=(codec.enc(x),c,r,n))
        x=codec.decode(w);x["commitment"]=b"Z"*32;x["proof"]["bytes"]=codec.token(x)
        self.blocked("OPENING_BINDING",args=(codec.enc(x),c,r,n))
    def test_fresh_signature_not_binding(self):
        w,c,r,n=fixture(); changed=sample(100002,1001)
        fresh={"ingress_ms":20000,"mac":receipt_mac(TIME,scope_for(CONFIG),changed,20000)}
        self.blocked("OPENING_BINDING",args=(w,changed,fresh,n))
    def test_ingress_authentication_and_boundary(self):
        w,c,r,n=fixture()
        self.blocked("TIME_REFERENCE_NOT_AUTHENTIC",args=(w,c,{**r,"mac":"0"*64},n))
        self.blocked("STATUS_STALE_OR_FUTURE",session=self.open(now=30000))
        self.blocked("TIME_REFERENCE_STALE",args=fixture(ingress=10000))
        self.blocked("TIME_REFERENCE_IN_FUTURE",args=fixture(ingress=22000))
    def test_status_pin_mac_and_revocation(self):
        self.blocked("STATUS_AUTH",signature="0"*64)
        altered={**self.status,"expires_ms":31000}
        self.blocked("STATUS_PIN",s=altered)
        rev=status(True)
        self.blocked("REVOKED",session=self.open(s=rev),s=rev)
    def test_nullifier_reuse_new_frame(self):
        self.assertEqual(self.submit()["admission"],"SYNTHETIC_CONTRACT_ACCEPTED")
        self.blocked("NULLIFIER_REPLAY",args=fixture(sample(100002,1001)))
        self.assertEqual(self.submit(fixture(sample(100002,1001),b"M"*32))["admission"],"SYNTHETIC_CONTRACT_ACCEPTED")
    def test_invalid_signature_no_commit(self):
        w,c,r,n=fixture(); bad=copy.deepcopy(c)
        f=bytearray.fromhex(bad["events"][-1]["frame_hex"]);f[-1]^=1;bad["events"][-1]["frame_hex"]=f.hex()
        r={"ingress_ms":20000,"mac":receipt_mac(TIME,scope_for(CONFIG),bad,20000)}
        self.blocked("SIGNATURE_OR_CAPTURE",args=(w,bad,r,n))
    def test_concurrent_single_commit(self):
        sessions=[self.open(),self.open()]
        args=fixture()
        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes=list(pool.map(lambda s:self.submit(args,session=s),sessions))
        self.assertEqual(sum(r["admission"]=="SYNTHETIC_CONTRACT_ACCEPTED" for r in outcomes),1)
        self.assertEqual(len(self.session._read()["nullifiers"]),1)
    def test_private_minimized_state_and_output(self):
        out=self.submit()
        self.assertEqual(set(self.session._read()),{"watermark","nullifiers"})
        self.assertEqual((self.path/"state.json").stat().st_mode&0o777,0o600)
        self.assertNotIn("speed_cm_s",out);self.assertNotIn("nullifier",out)
        self.assertEqual(out["actual_crypto"],"NOT_CHECKED")
    def test_atomic_failure(self):
        with patch("persistent_unified.os.replace",side_effect=OSError):
            self.blocked("STATE_COMMIT_FAILED")
        self.assertEqual(self.submit()["admission"],"SYNTHETIC_CONTRACT_ACCEPTED")
    def test_corrupt_state(self):
        (self.path/"state.json").write_bytes(b"{}")
        self.blocked("STATE_MISSING_CORRUPT")
    def test_predicate_boundary(self):
        self.assertEqual(self.submit(fixture(at_speed(500,100000,1000)))["admission"],"SYNTHETIC_CONTRACT_ACCEPTED")
        self.blocked("PREDICATE_NOT_SATISFIED",args=fixture(at_speed(501,100002,1001),b"M"*32))
        self.assertEqual(self.submit(fixture(at_speed(499,100002,1001),b"M"*32))["admission"],"SYNTHETIC_CONTRACT_ACCEPTED")
    def test_authority_rotation_not_implicit(self):
        from binding_adapter import BindingRejected
        with self.assertRaisesRegex(BindingRejected,"STATE_MISSING_CORRUPT"):
            BindingSession(state_dir=self.path,config=CONFIG,time_key=TIME,status_key=STATUS,source_secret=b"Y"*32,status_pin=pin(self.status),clock=lambda:NOW)
    def test_commit_uncertainty_no_accept(self):
        import os
        real=os.fsync
        calls=[]
        def fail_second(fd):
            calls.append(fd)
            if len(calls)==2:raise OSError()
            real(fd)
        with patch("persistent_unified.os.fsync",side_effect=fail_second):
            result=self.submit()
        self.assertEqual(result["admission"],"HOLD")
        self.assertEqual(result["reason"],"STATE_COMMIT_FAILED")
        self.assertEqual(result["replay_commit"],"UNKNOWN")
        self.blocked("CROSS_CAPTURE_REPLAY",session=self.open())
    def test_bounded_capture_and_no_caller_trust(self):
        w,c,r,n=fixture()
        for bad in (dict(c,extra="not allowed"),dict(c,events=[{"received_at_ms":1,"frame_hex":"00"*281}]),dict(c,events=[{"received_at_ms":True,"frame_hex":"00"}])):
            self.blocked("CAPTURE_",args=(w,bad,r,n))
        # Untrusted trust store is excluded by the existing receipt MAC and
        # must not be copied, interpreted or used to select the source key.
        c["test_trust_store"]={"ignored":object()}
        self.assertEqual(self.submit((w,c,r,n))["admission"],"SYNTHETIC_CONTRACT_ACCEPTED")
    def test_fixed_public_source_profile(self):
        from binding_adapter import BindingRejected
        cfg=copy.deepcopy(CONFIG)
        key=b"Z"*32
        cfg["verifier_key_hex"]=key.hex()
        cfg["enrollment"]["key_fingerprint"]=hashlib.sha256(key).hexdigest()
        with self.assertRaisesRegex(BindingRejected,"SOURCE_CONFIG_INVALID"):
            BindingSession(state_dir=self.path,config=cfg,time_key=TIME,status_key=STATUS,source_secret=SECRET,status_pin=pin(self.status),clock=lambda:NOW)
    def test_output_scope(self):
        out=self.submit()
        self.assertEqual((out["publication"],out["relying_party_decision"],out["command_path"]),("NOT_PERFORMED","NOT_MADE","NONE"))
        self.assertEqual(out["actual_crypto"],"NOT_CHECKED")
    def test_unclassified_write_io_is_hold_unknown(self):
        before=(self.path/"state.json").read_bytes()
        with patch.object(self.session,"_write",side_effect=OSError):
            out=self.submit()
        self.assertEqual((out["admission"],out["reason"],out["replay_commit"]),("HOLD","STATE_IO_UNAVAILABLE","UNKNOWN"))
        self.assertEqual((self.path/"state.json").read_bytes(),before)
    def test_policy_limit_mismatch(self):
        w,c,r,n=fixture();x=codec.decode(w);x["public_inputs"]["maximum_speed_cm_s"]=501;x["proof"]["bytes"]=codec.token(x)
        self.blocked("POLICY_BINDING",args=(codec.enc(x),c,r,n))
if __name__=="__main__":unittest.main(verbosity=2)
