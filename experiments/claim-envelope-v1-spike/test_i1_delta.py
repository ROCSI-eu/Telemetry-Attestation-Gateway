"""EXPERIMENTAL / SYNTHETIC_ONLY / A0_SYNTHETIC / NOT VALIDATION OR PRODUCTION AUTHORIZATION.
Supplement to the immutable placeholder corpus. No actual proof or independent authorship.
"""
import copy
import unittest
import codec as c
import independent_checker as checker
import vectors as v
from bounded_speed import encode_public_artifact

MARKS = ["EXPERIMENTAL", "SYNTHETIC_ONLY", "A0_SYNTHETIC",
         "NOT VALIDATION OR PRODUCTION AUTHORIZATION"]
CASES = 0


class Delta(unittest.TestCase):
    def check_case(self, name, wire, admission, envelope=None, disposition=None,
                   scenario=None, dimensions=None, expected_inputs=None):
        global CASES
        with self.subTest(case=name):
            context = dict(v.BASE if scenario is None else scenario)
            a = c.evaluate(wire, context)
            b = checker.assess(wire, context)
            self.assertEqual(a, b)
            self.assertEqual(a["labels"], MARKS)
            self.assertEqual(a["mode"], "NON_CRYPTOGRAPHIC_PLACEHOLDER")
            self.assertEqual(a["actual_crypto"], "NOT_CHECKED")
            self.assertEqual(a["verification"], "NOT_PERFORMED")
            self.assertNotIn("business_decision", a)
            self.assertEqual(a["admission"], admission)
            sim = a["simulated_result"]
            if admission != "structurally_accepted":
                self.assertIsNone(sim)
                self.assertNotIn("public_input_hex", a)
            else:
                self.assertIsNotNone(sim)
                self.assertNotIn("business_decision", sim)
                self.assertEqual(sim["envelope_evaluation"], envelope)
                self.assertEqual(sim["service_disposition"], disposition)
                for k, expected in (dimensions or {}).items():
                    self.assertEqual(sim[k], expected)
                if expected_inputs is not None:
                    self.assertEqual(a["public_input_hex"], expected_inputs.hex())
            CASES += 1

    def mutate(self, name, field, value, admission="malformed", **kwargs):
        x = v.envelope()
        x[field] = value
        self.check_case(name, c.enc(x), admission, **kwargs)

    def test_identifier_edges(self):
        for length in (1, 255):
            self.mutate("id_shape_" + str(length), "domain", "a" * length,
                        "structurally_accepted", envelope="invalid",
                        disposition="cryptographically_invalid")
        for value in ("", "a" * 256, "a\x01", "a\x7f"):
            self.mutate("bad_domain_" + repr(value), "domain", value)

    def test_missing_and_nested_shape(self):
        original = v.envelope()
        for key in original:
            if key == "proof":  # frozen corpus already covers this
                continue
            x = dict(original)
            del x[key]
            self.check_case("missing_" + key, c.enc(x), "malformed")
        for field in ("policy_ref", "verification_key_id", "validity", "public_inputs"):
            nested = original[field]
            for key in nested:
                replacement = dict(nested)
                del replacement[key]
                self.mutate("missing_" + field + "." + key, field, replacement)
            self.mutate("extra_" + field, field, dict(nested, extra=0))
        for key in ("source_pseudonym", "record_nonce", "speed_cm_s"):
            self.mutate("private_nested_" + key, "public_inputs",
                        dict(original["public_inputs"], **{key: 1}))
        self.mutate("caller_inputs", "public_input_sequence", [0, 500])

    def test_uint_and_lengths(self):
        x = v.envelope()
        wire = c.enc(x)
        marker = c.enc("maximum_speed_cm_s") + c.enc(500)
        self.assertEqual(wire.count(marker), 1)
        self.check_case("negative_m", wire.replace(marker, c.enc("maximum_speed_cm_s")+b"\x20",1), "malformed")
        self.mutate("m_wrong_type", "public_inputs", {"maximum_speed_cm_s": "500"})
        for field in ("commitment", "nullifier"):
            for length in (31, 33):
                self.mutate(field + "_len_" + str(length), field, b"z"*length)
        for field in ("policy_ref", "verification_key_id"):
            for length in (31, 33):
                self.mutate(field + "_digest_len_" + str(length), field,
                            dict(x[field], digest=b"z"*length))
        for length in (0, 1025):
            self.mutate("bad_attached_size_" + str(length), "proof",
                        dict(x["proof"], bytes=b"x"*length))
        for length in (1, 1024):
            self.mutate("valid_shape_bad_token_" + str(length), "proof",
                        dict(x["proof"], bytes=b"x"*length),
                        "structurally_accepted", envelope="invalid",
                        disposition="cryptographically_invalid")

    def test_v0_and_bound_context(self):
        self.check_case("v0_incompatible", encode_public_artifact(500), "malformed")
        x = v.envelope()
        for field in ("policy_ref", "verification_key_id"):
            for key, value in (("id", "other"), ("version", 2)):
                self.mutate("stale_token_" + field + "." + key, field,
                            dict(x[field], **{key: value}), "structurally_accepted",
                            envelope="invalid", disposition="cryptographically_invalid")
        self.mutate("stale_token_upper", "validity", {"not_before":100,"not_after":111},
                    "structurally_accepted", envelope="invalid", disposition="cryptographically_invalid")
        # Explicit test-only eleven-item CBOR array. Independent fixed ordering,
        # not codec.ORDER or final normative field-element sequence.
        seq = [x["envelope_version"], x["statement_id"], x["proof_suite"],
               x["assurance_tier"], x["policy_ref"], x["validity"], x["domain"],
               x["commitment"], x["nullifier"], x["verification_key_id"], x["public_inputs"]]
        self.check_case("placeholder_order", c.enc(x), "structurally_accepted",
                        "valid", "accepted", expected_inputs=c.enc(seq))

    def test_time_and_tier_edges(self):
        for tier in (5, 255):
            self.mutate("unsupported_tier_" + str(tier), "assurance_tier", tier, "unsupported")
        self.mutate("injected_tier_label", "assurance_label", "A0_SYNTHETIC")
        for lo, hi in ((0,1), (2**64-2,2**64-1)):
            x = v.envelope()
            x["validity"] = {"not_before": lo, "not_after": hi}
            x["proof"]["bytes"] = c.token(x)
            for t, freshness, disposition in ((lo,"current","accepted"),(hi,"expired","rejected")):
                self.check_case("one_second_"+str(t), c.enc(x), "structurally_accepted",
                                "valid", disposition, dict(v.BASE, decision_time=t),
                                {"freshness":freshness})
        global CASES
        for t in (-1, 2**64):
            with self.subTest(bad_harness_time=t):
                for fn in (c.evaluate, checker.assess):
                    with self.assertRaises(ValueError):
                        fn(c.enc(v.envelope()), dict(v.BASE, decision_time=t))
                CASES += 1

    def test_policy_reject_with_missing_store(self):
        self.check_case("policy_reject_store_missing", c.enc(v.envelope()),
                        "structurally_accepted", "valid", "rejected",
                        dict(v.BASE, policy_allows=False, store_available=False),
                        {"policy_acceptance":"rejected","replay":"temporarily_unverifiable"})


if __name__ == "__main__":
    print(" / ".join(MARKS), flush=True)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Delta)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("I1_DELTA", "PASS" if result.wasSuccessful() else "FAIL",
          "groups", result.testsRun, "cases_passed", CASES, flush=True)
    raise SystemExit(0 if result.wasSuccessful() else 1)
