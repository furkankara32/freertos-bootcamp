import json,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from host.session import Session
from host.protocol import Frame,LED,encode,Decoder


class SessionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)/'records'
        self.s=Session(lambda f:None,lambda e:None)
        self.s.identity={'values':[0xF4070005,1,115200,0]+[0]*18}
        self.s.port=SimpleNamespace(port='test')
    def test_invalid_inputs_do_not_create_records(self):
        for args in ((1,1,1000,3),(4,2,1000,3),(1,0,0,3),(1,0,1000,0)):
            with self.assertRaises(ValueError):self.s.begin(self.root,*args)
        self.assertFalse(self.root.exists())
    def test_stale_run_leds_are_excluded(self):
        folder=self.s.begin(self.root,1,0);run=self.s.run_id
        for rid,late in ((run,800),(run^1,999999)):
            self.s.frames.extend(Decoder().feed(encode(LED,1,[rid,1,0,1,0,0,0,1000000,late])))
        self.s.finish();summary=json.loads((folder/'summary.json').read_text())
        self.assertEqual(summary['samples'],1);self.assertEqual(summary['max_us'],800)
    def test_busy_writer_prevents_new_run(self):
        self.s.send_bulk()
        with self.assertRaises(RuntimeError):self.s.begin(self.root,1,0)
    def test_firmware_mismatch_blocks_capture(self):
        p=self.root.parent/'firmware/build/Release';p.mkdir(parents=True)
        (p/'build.json').write_text(json.dumps({'build_id':'a'*64}))
        with self.assertRaises(RuntimeError):self.s.begin(self.root,1,0)
