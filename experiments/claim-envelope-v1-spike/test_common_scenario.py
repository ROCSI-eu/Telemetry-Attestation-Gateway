"""EXPERIMENTAL / SYNTHETIC_ONLY / A0_SYNTHETIC / NOT VALIDATION OR PRODUCTION AUTHORIZATION."""
import json
import struct
import unittest
from pathlib import Path
import sys

class SavedOutput(unittest.TestCase):
    def setUp(self):
        self.report=json.loads((ROOT/"common-results.json").read_bytes())
        self.raw=(ROOT/"EXPERIMENTAL_SYNTHETIC_ONLY_TAGD.bin").read_bytes()

    def test_minimized_contract(self):
        r=self.report
        self.assertEqual(set(r),{"labels","classification","notice","threshold_cm_s","association","samples","unavailable_cases","historical","control_results","cleanup"})
        self.assertEqual(r["threshold_cm_s"],500)
        rows=r["samples"]+r["unavailable_cases"]
        self.assertEqual([x["ordinal"] for x in rows],[1,2,3,None,1])
        for x in rows:
            self.assertEqual(set(x),{"ordinal","admission","reason","mode","actual_crypto","verification","replay_commit","publication","relying_party_decision","command_path"})
            self.assertEqual((x["actual_crypto"],x["verification"],x["publication"],x["relying_party_decision"],x["command_path"]),("NOT_CHECKED","NOT_PERFORMED","NOT_PERFORMED","NOT_MADE","NONE"))
        self.assertEqual([x["admission"] for x in rows],["SYNTHETIC_CONTRACT_ACCEPTED"]*2+["HOLD"]*3)
        self.assertEqual([x["reason"] for x in rows],["NONE","NONE","PREDICATE_NOT_SATISFIED","INPUT_UNAVAILABLE","VERIFIER_UNAVAILABLE"])
        self.assertEqual([x["replay_commit"] for x in rows],["LOCAL_ATOMIC_COMMIT"]*2+["NOT_PERFORMED"]*3)
        self.assertEqual(r["cleanup"],"PASS")

    def test_independent_dataflash_parse(self):
        data=self.raw; i=0; formats={}; samples=[]; messages=[]
        while i<len(data):
            self.assertEqual(data[i:i+2],b"\xa3\x95")
            kind=data[i+2]
            if kind==128:
                n,length,name,fmt,cols=struct.unpack_from("<BB4s16s64s",data,i+3)
                self.assertNotIn(n,formats)
                formats[n]=(length,name.rstrip(b"\0"),fmt.rstrip(b"\0"),cols.rstrip(b"\0"))
                i+=89
            else:
                length,name,fmt,cols=formats[kind]
                payload=data[i+3:i+length];self.assertEqual(len(payload),length-3)
                if name==b"TAGD":
                    samples.append(struct.unpack("<QII",payload))
                elif name==b"MSG":
                    t,msg=struct.unpack("<Q64s",payload)
                    messages.append(msg.rstrip(b"\0").decode("ascii"))
                else:self.fail("unexpected record")
                i+=length
        self.assertEqual(i,len(data))
        self.assertEqual(formats,{150:(19,b"TAGD",b"QII",b"TimeUS,Sample,Synthetic"),151:(75,b"MSG",b"QZ",b"TimeUS,Message")})
        self.assertEqual(samples,[(0,1,1),(1000000,2,1),(2000000,3,1)])
        self.assertEqual(len(messages),10)
        self.assertEqual(messages[:5],["EXPERIMENTAL / SYNTHETIC_ONLY / A0_SYNTHETIC","NOT VALIDATION OR PRODUCTION AUTHORIZATION","DERIVED DISPLAY ONLY - NOT A VEHICLE LOG OR PROOF","Threshold 500 cm/s; placeholder; no proof verified","Non-cryptographic UX prototype: no proof generated or verified"])
        for x,msg in zip(self.report["samples"],messages[5:8],strict=True):
            self.assertEqual(msg,f"Sample {x['ordinal']}: {x['admission']} {x['reason']}")
        self.assertEqual(messages[8:],["Case none: HOLD INPUT_UNAVAILABLE","Case 1: HOLD VERIFIER_UNAVAILABLE"])

    def test_historical_separation(self):
        h=self.report["historical"]
        self.assertEqual(h,{"origin":"COMPANION_EXP4_HISTORICAL_ONLY","suite":"bounded-speed-proof-v0","actual_crypto_then":"VALID","verification_then":"PERFORMED","verification_now":"NOT_PERFORMED","observation_binding":"NOT_EVALUATED","current_sample_association":"NONE"})
        self.assertNotIn(b"VALID",self.raw.replace(b"VALIDATION",b""))

if __name__=="__main__":
    ROOT=Path(sys.argv.pop(1))
    unittest.main(verbosity=2)
