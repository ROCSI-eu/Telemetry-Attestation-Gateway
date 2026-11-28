"""EXPERIMENTAL / SYNTHETIC_ONLY / A0_SYNTHETIC / NOT VALIDATION OR PRODUCTION AUTHORIZATION."""
import json
import unittest
from pathlib import Path
import codec
import independent_checker as independent
import vectors
class Contract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus=json.loads(Path(__file__).with_name("vectors.json").read_text())
        cls.cases={x["name"]:x for x in cls.corpus["cases"]}
    def result(self,name):return self.cases[name]["expected"]["simulated_result"]
    def test_exact_corpus_regeneration(self):
        self.assertEqual(vectors.generate(),self.corpus)
    def test_independent_wire_checker(self):
        for v in self.cases.values():
            with self.subTest(case=v["name"]):
                self.assertEqual(independent.assess(bytes.fromhex(v["wire_hex"]),v["scenario"]),v["expected"])
    def test_half_open(self):
        for name,expected in [("before_lower","not_yet_valid"),("positive_lower_endpoint","current"),("just_after_lower","current"),("just_before_upper","current"),("upper_endpoint","expired"),("after_upper","expired"),("clock_missing","temporarily_unverifiable")]:
            self.assertEqual(self.result(name)["freshness"],expected)
    def test_cross_dimension_precedence(self):
        for name,key,value in [("policy_rejected","policy_acceptance","rejected"),("revoked","revocation","revoked"),("replayed","replay","replayed"),("store_unavailable","replay","temporarily_unverifiable")]:
            r=self.result(name);self.assertEqual(r["envelope_evaluation"],"valid");self.assertEqual(r[key],value)
        self.assertEqual(self.result("insufficient")["assurance"]["tier_sufficiency"],"insufficient")
        self.assertEqual(self.result("mutate_proof")["envelope_evaluation"],"invalid")
    def test_optional_publication_independent(self):
        a=self.result("positive_lower_endpoint");b=self.result("optional_publication_unavailable")
        for key in ("envelope_evaluation","policy_acceptance","service_disposition","replay"):
            self.assertEqual(a[key],b[key])
    def test_actual_status_never_valid(self):
        for v in self.cases.values():
            out=v["expected"];self.assertEqual(out["actual_crypto"],"NOT_CHECKED");self.assertEqual(out["verification"],"NOT_PERFORMED")
            self.assertNotIn("business_decision",out)
    def test_privacy_allowlist(self):
        wire=bytes.fromhex(self.cases["positive_lower_endpoint"]["wire_hex"])
        x=codec.decode(wire)
        self.assertEqual(set(x["public_inputs"]),{"maximum_speed_cm_s"})
        self.assertEqual(set(x),set(codec.ORDER)|{"proof"})
        for name in ("speed_cm_s","source_pseudonym","record_nonce","latitude","longitude","witness"):
            self.assertNotIn(name,x);self.assertNotIn(name,x["public_inputs"])
        self.assertEqual(self.cases["malformed_private_speed"]["expected"]["admission"],"malformed")
    def test_bad_harness_context(self):
        wire=codec.enc(vectors.envelope())
        for s in ({},dict(vectors.BASE,already_seen="false"),dict(vectors.BASE,decision_time=True),dict(vectors.BASE,revocation="unknown"),dict(vectors.BASE,assurance="accepted")):
            for fn in (codec.evaluate,independent.assess):
                with self.assertRaises(ValueError):fn(wire,s)
if __name__=="__main__":unittest.main()
