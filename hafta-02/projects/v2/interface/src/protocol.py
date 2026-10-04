"""PROTO2/PROTO3 framing, strict dump validation and MCU-only time arithmetic."""
from dataclasses import dataclass, field
import re
import zlib

FRAME_BYTES = 64
CSV_FIELDS = ['scenario','event_id','t0_us','t1_us','t2_us','t3_us','t4_us','status']
STATUSES = {'ok','button_q_drop','tx_drop','tx_error','timeout','record_overflow'}
SUM_KEYS = set('accepted ok late_completed debounce_reject button_q_drop btn_tx_drop tel_q_drop uart_tx_error tx_timeout drain_timeout record_overflow unrecorded_events txq_hwm buttonq_hwm tel_generated tel_enqueued tel_completed rx_error control_drop format_error period_overrun'.split())
MET_KEYS = set('sysclk_hz timer_hz tick_hz baud frame_bytes prio_tel prio_btn prio_tx buttonq_len txq_len record_capacity telemetry_hz period_ms work_target_us work_iters work_min_us work_mean_us work_max_us run_start_us run_stop_us tel_first_us tel_last_us period_min_us period_max_us period_sum_us period_n fw_sha_a fw_sha_b build_config opt_level kernel_version result'.split())
TEXT_MET = {'fw_sha_a','fw_sha_b','build_config','opt_level','kernel_version','result'}
OPTIONAL_NUM = {'work_min_us','work_mean_us','work_max_us','tel_first_us','tel_last_us','period_min_us','period_max_us'}

V3_MET_KEYS = (MET_KEYS-{'txq_len'}) | set(('design_version variant deadline_us baud_actual uart_brr uart_pclk_hz baud_error_ppm '
    'queue_policy btn_txq_len tel_txq_len work_mode slice_target_us slice_count slice_gap_ticks cal_slice_max_us '
    'cpu_work_mean_us cpu_work_max_us slice_max_us activation_wall_max_us').split())
V3_SUM_KEYS = (SUM_KEYS-{'txq_hwm','late_completed'}) | {'btn_txq_hwm','tel_txq_hwm','late_10ms','late_20ms'}
TEXT_MET |= {'variant','queue_policy','work_mode'}

class ProtocolError(ValueError): pass

def uint(text, maximum=0xffffffff):
    if not re.fullmatch(r'[0-9]+', text): raise ProtocolError(f'Geçersiz tamsayı: {text!r}')
    value = int(text)
    if value > maximum: raise ProtocolError('Tamsayı aralık dışında')
    return value

def frame(payload):
    raw = payload.encode('ascii')
    if len(raw)>63 or b'\n' in raw or b'\r' in raw: raise ProtocolError('Payload en fazla 63 ASCII bayt olmalı')
    return raw.ljust(63,b' ')+b'\n'

def elapsed(end, start): return (end-start) & 0xffffffff

def stages(row):
    if row['status'] != 'ok': return None
    t=[row[f't{i}_us'] for i in range(5)]
    if any(v is None for v in t): raise ProtocolError('ok kaydının timestamp alanı eksik')
    d=[elapsed(t[i+1],t[i]) for i in range(4)]
    r=elapsed(t[4],t[0])
    if sum(d)!=r or r>1000000: raise ProtocolError('Tutarsız zaman zinciri / 1 s bütçesi aşılmış')
    return dict(zip(['d1_us','d2_us','d3_us','d4_us','r_us'],[*d,r]))

class Decoder:
    def __init__(self): self.buffer=bytearray();self.discard=False;self.errors=[]
    def feed(self, data):
        result=[]
        for byte in data:
            if self.discard:
                if byte==10: self.discard=False
                continue
            self.buffer.append(byte)
            if byte==10:
                raw=bytes(self.buffer);self.buffer.clear()
                if len(raw)!=64 or any(b<32 or b>126 for b in raw[:-1]): self.errors.append('Bozuk ASCII/64 bayt çerçeve')
                else: result.append(raw)
            elif len(self.buffer)>=64:
                self.errors.append('LF/çerçeve sınırı kayıp');self.buffer.clear();self.discard=True
        return result

@dataclass
class Dump:
    run: int
    scenario: str
    expected: int
    last_id: int
    metadata: dict = field(default_factory=dict)
    counters: dict = field(default_factory=dict)
    rows: list = field(default_factory=list)
    crc: int = 0
    half: tuple | None = None
    invalid: bool = False
    protocol: str = "PROTO2"

    def validate(self, count, checksum):
        if self.invalid or self.half is not None or count!=self.expected or len(self.rows)!=count: raise ProtocolError('Eksik/bozuk dump')
        if checksum!=self.crc: raise ProtocolError('Dump CRC uyuşmuyor')
        if not (V3_MET_KEYS if self.protocol=='PROTO3' else MET_KEYS)<=self.metadata.keys() or not (V3_SUM_KEYS if self.protocol=='PROTO3' else SUM_KEYS)<=self.counters.keys(): raise ProtocolError('MET/SUM alanları eksik')
        c=self.counters;m=self.metadata
        counts={s:sum(r['status']==s for r in self.rows) for s in STATUSES}
        if c['accepted']!=len(self.rows)+c['unrecorded_events'] or c['accepted']!=self.last_id: raise ProtocolError('Kabul/kayıt sayısı tutarsız')
        if self.rows and self.rows[-1]['event_id']>self.last_id: raise ProtocolError('last_event_id tutarsız')
        if not c['unrecorded_events'] and [r['event_id'] for r in self.rows]!=list(range(1,self.last_id+1)): raise ProtocolError('Olay kimliği kayıp')
        for key,status in [('ok','ok'),('button_q_drop','button_q_drop'),('btn_tx_drop','tx_drop'),('record_overflow','record_overflow')]:
            if c[key]!=counts[status]: raise ProtocolError(f'Sayaç uyuşmuyor: {key}')
        for key,deadline in ([('late_10ms',10000),('late_20ms',20000)] if self.protocol=='PROTO3' else [('late_completed',20000)]):
            if c[key]!=sum(r['status']=='ok' and stages(r)['r_us']>deadline for r in self.rows): raise ProtocolError('Geç yanıt sayısı tutarsız')
        fixed={'timer_hz':1000000,'tick_hz':1000,'baud':115200,'frame_bytes':64,'prio_tel':3,'prio_btn':2,'prio_tx':1,'buttonq_len':8,'txq_len':16,'record_capacity':128}
        if self.protocol=='PROTO3':
            fixed.pop('txq_len');fixed.pop('baud')
            fixed.update(design_version=2,deadline_us=10000,btn_txq_len=8,tel_txq_len=16)
            if m['variant'] not in {'Q','QW','QB','QWB'} or m['queue_policy']!='btn_first':raise ProtocolError('V2 varyant/kuyruk politikası geçersiz')
            if m['baud']!=(460800 if m['variant'] in {'QB','QWB'} else 115200):raise ProtocolError('Varyant baud uyuşmuyor')
            sliced=m['variant'] in {'QW','QWB'}
            if m['work_mode']!=('sliced' if sliced else 'monolithic'):raise ProtocolError('İş profili uyuşmuyor')
            target=[0,0,0,0,2000,5000][int(self.scenario[1])]
            slices=(target//1000 if sliced else 1) if target else 0
            if m['work_target_us']!=target or m['slice_count']!=slices or m['slice_gap_ticks']!=int(sliced and slices>1):raise ProtocolError('Dilim yapılandırması uyuşmuyor')
            if m['slice_target_us']!=(target//slices if slices else 0):raise ProtocolError('Dilim hedefi uyuşmuyor')
            if not m['uart_brr'] or m['baud_actual']!=m['uart_pclk_hz']//m['uart_brr']:raise ProtocolError('Gerçek baud tutarsız')
            if m['baud_error_ppm']!=abs(m['baud_actual']-m['baud'])*1000000//m['baud']:raise ProtocolError('Baud hata hesabı tutarsız')
            if c['btn_txq_hwm']>8 or c['tel_txq_hwm']>16:raise ProtocolError('Kuyruk HWM aralık dışında')
        if any(m[k]!=v for k,v in fixed.items()): raise ProtocolError('Deney sabitleri specs ile uyuşmuyor')
        if (self.protocol=='PROTO2' and c['txq_hwm']>16) or c['buttonq_hwm']>8: raise ProtocolError('Kuyruk HWM aralık dışında')
        if m['result'] not in {'COMPLETE','INCOMPLETE','CANCELLED'}: raise ProtocolError('Koşu sonucu geçersiz')
        if c['tel_generated']!=c['tel_enqueued']+c['tel_q_drop'] or c['tel_completed']>c['tel_enqueued']: raise ProtocolError('TEL sayaçları tutarsız')
        n=c['tel_generated']
        if m['period_n']!=max(0,n-1): raise ProtocolError('Periyot sayısı tutarsız')
        if n>=2 and elapsed(m['tel_last_us'],m['tel_first_us'])!=m['period_sum_us']: raise ProtocolError('Periyot toplamı tutarsız')
        return self

class Protocol:
    def __init__(self): self.dump=None;self.version="PROTO2";self.firmware=None
    def invalidate(self):
        if self.dump: self.dump.invalid=True
    def accept(self, raw):
        try: return self._accept(raw)
        except (ValueError, IndexError, KeyError, TypeError) as exc:
            self.invalidate()
            if isinstance(exc,ProtocolError): raise
            raise ProtocolError(str(exc)) from exc
    def _accept(self, raw):
        if len(raw)!=64 or raw[-1:]!=b'\n' or any(b<32 or b>126 for b in raw[:-1]): raise ProtocolError('Geçersiz frame')
        fields=raw[:-1].rstrip(b' ').decode('ascii').split(',');kind=fields[0]
        lengths={'SYS':4,'ACK':4,'ERR':3,'EXP':4,'TEL':5,'BTN':5,'BEGIN':5,'MET':4,'SUM':4,'M1':6,'M2':6,'END':4}
        if kind not in lengths or len(fields)!=lengths[kind]: raise ProtocolError('Bilinmeyen mesaj / alan sayısı')
        if kind=='BEGIN':
            if fields[2] not in {f'S{i}' for i in range(6)}: raise ProtocolError('Geçersiz senaryo')
            self.dump=Dump(uint(fields[1]),fields[2],uint(fields[3],136),uint(fields[4]),protocol=self.version);return kind,self.dump
        if kind in {'MET','SUM','M1','M2','END'}:
            d=self.dump
            if d is None or uint(fields[1])!=d.run: raise ProtocolError('Dump/run eşleşmiyor')
            if kind in {'MET','SUM'}:
                key,value=fields[2:];dest=d.metadata if kind=='MET' else d.counters
                if not key or len(key)>24 or len(value)>24 or key in dest: raise ProtocolError('Yinelenen/uzun MET/SUM alanı')
                if kind=='SUM':value=uint(value)
                elif key in (MET_KEYS|V3_MET_KEYS)-TEXT_MET: value=None if value=='-' and key in OPTIONAL_NUM else uint(value)
                dest[key]=value
            elif kind=='M1':
                if d.half is not None: raise ProtocolError('M2 eksik')
                event=uint(fields[2]);times=[None if v=='-' else uint(v) for v in fields[3:]]
                if event==0 or (d.rows and event<=d.rows[-1]['event_id']): raise ProtocolError('Olay sırası/tekilliği hatalı')
                d.half=(event,times);d.crc=zlib.crc32(raw,d.crc)
            elif kind=='M2':
                if d.half is None or uint(fields[2])!=d.half[0]: raise ProtocolError('M1/M2 eşleşmiyor')
                times=d.half[1]+[None if v=='-' else uint(v) for v in fields[3:5]];status=fields[5]
                if status not in STATUSES or times[0] is None: raise ProtocolError('Status/t0 geçersiz')
                mask=sum((t is not None)<<i for i,t in enumerate(times))
                allowed={'ok':{31},'button_q_drop':{1},'record_overflow':{1},'tx_drop':{7},'tx_error':{1,3,7,15},'timeout':{1,3,7,15}}
                if mask not in allowed[status]: raise ProtocolError('Status/timestamp zinciri uyuşmuyor')
                row=dict(zip(CSV_FIELDS,[d.scenario,d.half[0],*times,status]));stages(row)
                d.rows.append(row);d.half=None;d.crc=zlib.crc32(raw,d.crc)
            else:
                if not re.fullmatch('[0-9A-Fa-f]{8}',fields[3]):raise ProtocolError('CRC biçimi geçersiz')
                result=d.validate(uint(fields[2]),int(fields[3],16));self.dump=None;return 'DUMP',result
            return kind,fields
        if kind=='SYS':
            if fields==['SYS','RTOSLAT','FW03','PROTO2']:self.version='PROTO2'
            elif fields[1]=='RTOSLAT' and fields[3]=='PROTO3' and fields[2] in {'FW2-Q','FW2-QW','FW2-QB','FW2-QWB'}:self.version='PROTO3'
            else:raise ProtocolError('Firmware/protokol sürümü uyumsuz')
            self.firmware=fields[2]
        if kind in {'EXP','TEL','BTN'}:
            uint(fields[1])
            scenario=fields[3] if kind=='EXP' else fields[2]
            if scenario not in {f'S{i}' for i in range(6)}: raise ProtocolError('Geçersiz canlı senaryo')
        if kind in {'TEL','BTN'}:uint(fields[3])
        if kind=='TEL':uint(fields[4])
        if kind=='BTN' and fields[4]!='PRESSED':raise ProtocolError('Geçersiz BTN')
        if kind in {'ACK','ERR'}:uint(fields[1],65535)
        return kind,fields
