import sys, unittest, random
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from host.protocol import *
class ProtocolTests(unittest.TestCase):
    def test_crc_reference(self):self.assertEqual(crc16(b'123456789'),0x29b1)
    def test_fragmented_and_combined(self):
        stream=b''.join(encode(LED,i,[i,0x3557]) for i in range(20));d=Decoder();frames=[];r=random.Random(5)
        while stream:
            n=r.randrange(1,153);frames+=d.feed(stream[:n]);stream=stream[n:]
        self.assertEqual([f.seq for f in frames],list(range(20)))
    def test_corruption_resync(self):
        bad=bytearray(encode(LOAD,1));bad[20]^=1;d=Decoder()
        frames=d.feed(b'garbage'+bad+encode(LED,2));self.assertEqual([f.seq for f in frames],[2]);self.assertEqual(d.rejected_bytes,107)
    def test_bulk(self):
        data=bulk();self.assertEqual(len(data),10000);self.assertEqual(len(Decoder().feed(data)),100)
if __name__=='__main__':unittest.main()
