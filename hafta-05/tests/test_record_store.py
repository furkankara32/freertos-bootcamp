import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from host.record_store import new_record, complete_capture


class RecordStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)/'records'

    def draft(self,scenario=1,run=10,variant=0):
        p=new_record(self.root,scenario)
        (p/'manifest.json').write_text(json.dumps(dict(scenario=scenario,run_id=run,variant=variant)))
        (p/'summary.json').write_text('{}')
        (p/'systemview').mkdir();(p/'systemview/trace.SVDat').write_bytes(bytes([run])*20)
        return p,dict(run_id=run,scenario=scenario,variant=variant,complete_window=True,size=20)

    def test_replaces_same_scenario_across_variants(self):
        p,m=self.draft();complete_capture(p,m)
        p,m=self.draft(run=11,variant=1);out=complete_capture(p,m)
        self.assertEqual(out,self.root/'S1')
        self.assertEqual((out/'systemview/trace.SVDat').read_bytes(),bytes([11])*20)
        self.assertEqual([p.name for p in self.root.iterdir() if not p.name.startswith('.')],['S1'])

    def test_four_scenarios_independent(self):
        for s in range(1,5):
            p,m=self.draft(s);complete_capture(p,m)
        self.assertEqual(sorted(p.name for p in self.root.glob('S*')),['S1','S2','S3','S4'])

    def test_partial_mismatch_or_truncated_preserves_old(self):
        p,m=self.draft();complete_capture(p,m)
        for change in ({'complete_window':False},{'run_id':90},{'size':21}):
            with self.subTest(change=change):
                p,m=self.draft(run=11);m.update(change)
                with self.assertRaises((RuntimeError,ValueError)):complete_capture(p,m)
                self.assertEqual((self.root/'S1/systemview/trace.SVDat').read_bytes(),bytes([10])*20)

    def test_promotion_failure_rolls_back(self):
        p,m=self.draft();complete_capture(p,m)
        p,m=self.draft(run=11);original=Path.rename
        def fail(source,target):
            if source==p:raise OSError('simulated filesystem failure')
            return original(source,target)
        with patch.object(Path,'rename',fail),self.assertRaises(OSError):complete_capture(p,m)
        self.assertTrue((self.root/'S1/systemview/trace.SVDat').exists())
        self.assertFalse((self.root/'.S1.previous').exists())

