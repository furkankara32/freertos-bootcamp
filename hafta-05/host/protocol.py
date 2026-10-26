"""100-byte little-endian frames, CRC-16/CCITT-FALSE over bytes 0..97."""
import struct
from dataclasses import dataclass
HELLO, START, STOP, LOAD, WORK, SEQUENCE, TRACE, STATUS, DIAG = range(1, 10)
MSG_HELLO, ACK, RUN_START, LED, DONE, STATS, ERROR, DIAGNOSTIC = range(128, 136)
NAMES = dict(zip(range(128,136), ['HELLO','ACK','RUN_START','LED','DONE','STATUS','ERROR','DIAG']))
COLORS = ['Yeşil','Turuncu','Kırmızı','Mavi','Kapalı']
def crc16(data):
    crc=0xffff
    for b in data:
        crc ^= b << 8
        for _ in range(8): crc=((crc<<1)^0x1021 if crc&0x8000 else crc<<1)&0xffff
    return crc
def encode(kind, seq, values=()):
    if len(values)>22: raise ValueError('At most 22 values')
    raw=struct.pack('<2sBBI22I2x',b'W5',1,kind,seq,*values,*([0]*(22-len(values))))
    return raw+struct.pack('<H',crc16(raw))
@dataclass
class Frame:
    kind: int
    seq: int
    values: tuple
    raw: bytes
    def as_dict(self):
        return {'type':NAMES.get(self.kind,str(self.kind)),'kind':self.kind,'seq':self.seq,'values':list(self.values)}
class Decoder:
    def __init__(self): self.buffer=bytearray();self.rejected_bytes=0
    def feed(self,data):
        self.buffer.extend(data);out=[]
        while len(self.buffer)>=100:
            raw=bytes(self.buffer[:100])
            if raw[:3]!=b'W5\x01' or crc16(raw[:98])!=struct.unpack_from('<H',raw,98)[0]:
                del self.buffer[0];self.rejected_bytes+=1;continue
            fields=struct.unpack('<2sBBI22I2xH',raw)
            out.append(Frame(fields[2],fields[3],fields[4:26],raw));del self.buffer[:100]
        return out
def bulk(seq=1):
    """Exactly 100 complete frames = 10,000 bytes; never interleaved mid-frame."""
    return b''.join(encode(LOAD,seq+i,[i]) for i in range(100))
