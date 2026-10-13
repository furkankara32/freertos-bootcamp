"""Strict Week 3 F407 transcript validation; no serial access in this module."""
import hashlib
import re

HELLO = ['WEEK3', '1', 'STM32F407VG', '230400', '168000000']
COLUMNS = ['id','accepted','received','generated_us','send_call_us','generation_to_receive_us']
MATRIX = [('A','NORMAL',True),('B','NORMAL',True),('C','NORMAL',True),
          ('A','BURST',True),('B','BURST',True),('C','BURST',True),('A','BURST',False)]

def require(condition, message):
    if not condition: raise ValueError(message)

def fnv(data):
    value=2166136261
    for b in data:value=((value ^ b)*16777619)&0xffffffff
    return value

def validate(lines, variant, load, trace, build_id):
    require(variant in 'ABC' and len(variant)==1 and load in {'NORMAL','BURST'},'Invalid condition')
    records=[s.strip().split(',') for s in lines if s.strip()]
    require(not any(r[0]=='#ERROR' for r in records),'Device reported an error')
    def one(tag, fields=None):
        found=[r[1:] for r in records if r[0]==tag]
        require(len(found)==1,f'Expected exactly one {tag}')
        if fields is not None:require(len(found[0])==fields,f'Invalid {tag} field count')
        return found[0]
    # Serial open may race with the boot banner: allow duplicate identical HELLOs.
    hellos=[r[1:] for r in records if r[0]=='#HELLO']
    require(bool(hellos) and all(h==HELLO for h in hellos),'Wrong MCU/protocol/clock/baud')
    require(re.fullmatch(r'[0-9a-f]{64}',build_id) is not None,'Invalid expected build ID')
    require(one('#BUILD',1)==[build_id],'Loaded firmware does not match local build')
    require(one('#ACK',1)==['TRACE_ON' if trace else 'TRACE_OFF'],'Trace ACK mismatch')
    run=one('#RUN',3);rid=int(run[0]);require(rid>0 and run[1:]==[variant,load],'Run identity mismatch')
    require(one('#END',1)==[str(rid)],'END identity mismatch')
    result=one('#RESULT',10)
    require(result[:3]==run,'RESULT identity mismatch')
    attempted,accepted,failed,consumed,enabled,nbytes,drops=map(int,result[3:])
    require(attempted==44 and 0<=accepted<=44 and failed>=0 and accepted+failed==44,'Counter mismatch')
    require(consumed==accepted and enabled==int(trace),'Drain or trace flag mismatch')
    require(one('#COLUMNS',6)==['id','ok','received','generated_us','send_us','latency_us'],'Raw schema mismatch')
    raw=[r[1:] for r in records if r[0]=='#ROW']
    require(len(raw)==44 and all(len(r)==6 for r in raw),'Missing/malformed rows')
    rows=[list(map(int,r)) for r in raw]
    require([r[0] for r in rows]==list(range(1,45)),'Duplicate/out-of-order/missing IDs')
    require(all(r[1] in {0,1} and r[2]==r[1] for r in rows),'Invalid accepted/received flags')
    require(all(0<=x<=0xffffffff for r in rows for x in r),'Unsigned value out of range')
    require(sum(r[1] for r in rows)==accepted,'Rows and accepted counter disagree')
    stack=list(map(int,one('#STACK',3)));rx=list(map(int,one('#RX',2)))
    require(all(x>0 for x in stack),'Stack high water mark exhausted')
    require(rx==[0,0],'UART errors or dropped RX bytes')
    rx_diagnostics={}
    if any(r[0] in {'#RX_BASE','#RX_TOTAL'} for r in records):
        base=list(map(int,one('#RX_BASE',2)));total=list(map(int,one('#RX_TOTAL',2)))
        require(all(0<=n<=0xffffffff for n in base+total),'RX diagnostic out of range')
        require([(b-a)&0xffffffff for a,b in zip(base,total)]==rx,'RX baseline/delta mismatch')
        rx_diagnostics={'rx_before_run':base,'rx_lifetime_total':total,'rx_scope':'run_start_to_report'}
    data=bytearray();trace_meta=None
    if trace:
        hdr=one('#TRACE',5)
        require(int(hdr[0])==rid and one('#TRACE_END',1)==[str(rid)],'TRACE identity mismatch')
        for r in records:
            if r[0]=='#HEX':
                require(len(r)==3 and int(r[1])==len(data),'Trace chunk offset mismatch')
                require(bool(r[2]) and len(r[2])%2==0 and re.fullmatch('[0-9A-Fa-f]+',r[2]) is not None,'Invalid hex')
                data.extend(bytes.fromhex(r[2]))
        require(0<len(data)<=32768 and len(data)==int(hdr[1])==nbytes,'Trace byte count mismatch')
        require(fnv(data)==int(hdr[2],16),'Trace checksum mismatch')
        require(int(hdr[3])==drops and drops>=0,'Trace drop counter mismatch')
        require(int(hdr[4]) in {0,1,2},'Unknown stop reason')
        trace_meta={'bytes':len(data),'fnv1a':hdr[2],'drops':drops,'stop_reason':int(hdr[4]),'sha256':hashlib.sha256(data).hexdigest(),'clean':drops==0}
    else:
        require(nbytes==0 and drops==0,'Trace OFF has trace bytes/drops')
        require(not any(r[0] in {'#TRACE','#HEX','#TRACE_END'} for r in records),'Unexpected trace while OFF')
    meta={'source':'hardware_serial','board':'STM32F407G-DISC1','mcu':'STM32F407VG',
          'build_id':build_id,'run_id':rid,'variant':variant,'load':load,'trace_enabled':trace,
          'attempted':attempted,'accepted':accepted,'failed':failed,'consumed':consumed,
          'stack_words':stack,'rx_errors_drops':rx,'trace':trace_meta,
          'valid':not trace or drops==0}
    meta.update(rx_diagnostics)
    return meta,rows,bytes(data)

def statistics(rows):
    def stats(values):
        return {'n':len(values),'mean':sum(values)/len(values) if values else None,'max':max(values) if values else None}
    return {'send_all_us':stats([r[4] for r in rows]),
            'send_success_us':stats([r[4] for r in rows if r[1]]),
            'send_failed_us':stats([r[4] for r in rows if not r[1]]),
            'generation_to_receive_us':stats([r[5] for r in rows if r[2]])}
