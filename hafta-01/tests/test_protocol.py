import csv,json,zlib
import pytest
from interface.src.protocol import Decoder,Protocol,ProtocolError,frame,elapsed,stages
from interface.src.simulator import Simulator
from interface.src.storage import save_dump
from analysis.analyze import summarize

def run_frames(scenario=0,n=30):
    clock=[0.0];sim=Simulator(lambda:clock[0]);sim.command(f'CFG,1,S{scenario}');sim.command('START,2');clock[0]=5;sim.poll()
    for _ in range(n):clock[0]+=.51;sim.poll();sim.press()
    return sim.command('STOP,3')

def parse(frames):
    p=Protocol();result=None
    for raw in frames:
        kind,data=p.accept(raw)
        if kind=='DUMP':result=data
    return result

@pytest.mark.parametrize('scenario',range(6))
def test_scenarios_crc_counts_export(tmp_path,scenario):
    frames=run_frames(scenario);dump=parse(frames)
    assert len(dump.rows)==30 and dump.counters['accepted']==30
    folder=save_dump(dump,tmp_path,b''.join(frames),True)
    metadata=json.loads((folder/'metadata.json').read_text());summary=summarize(dump.rows,metadata)
    assert summary['ok']==30 and summary['source']=='synthetic'
    assert 'demo' in folder.parts
    assert len(list(csv.DictReader((folder/'events.csv').open())))==30
    assert abs(sum(summary[f'd{i}_mean_us'] for i in range(1,5))-summary['r_mean_us'])<1e-8

def test_all_serial_split_boundaries():
    wire=b''.join(run_frames())
    for split in range(65):
        d=Decoder();frames=d.feed(wire[:split])+d.feed(wire[split:]);assert not d.errors;assert parse(frames).expected==30
    d=Decoder();frames=[]
    for byte in wire:frames+=d.feed(bytes([byte]))
    assert parse(frames).expected==30

def test_corrupt_crc_and_missing_half():
    frames=run_frames();bad=[frame('END,1,30,00000000') if r.startswith(b'END,') else r for r in frames]
    with pytest.raises(ProtocolError,match='CRC'):parse(bad)
    bad=[r for r in frames if not r.startswith(b'M2,1,1,')]
    with pytest.raises(ProtocolError):parse(bad)

def test_missing_metadata_and_duplicate():
    frames=run_frames()
    with pytest.raises(ProtocolError,match='eksik'):parse([r for r in frames if not r.startswith(b'MET,1,baud,')])
    at=next(i for i,r in enumerate(frames) if r.startswith(b'MET,'))
    with pytest.raises(ProtocolError,match='Yinelenen'):parse(frames[:at]+[frames[at]]+frames[at:])

def test_framing_resynchronization():
    decoder=Decoder();valid=frame('SYS,RTOSLAT,FW03,PROTO2')
    assert decoder.feed(b'x'*90+b'\n'+valid)==[valid] and decoder.errors
    assert decoder.feed(b'bad\n'+valid)==[valid]

def test_uint_wrap_and_deadline():
    assert elapsed(0x10,0xfffffff0)==32
    row=dict(status='ok',t0_us=0xfffffff0,t1_us=0,t2_us=10,t3_us=20,t4_us=(0xfffffff0+20000)&0xffffffff)
    assert stages(row)['r_us']==20000
    row['t4_us']+=1;assert stages(row)['r_us']==20001
    row['status']='timeout';row['t4_us']=None;assert stages(row) is None

def test_full_width_and_oversize():
    n='4294967295'
    for text in [f'M1,{n},{n},{n},{n},{n}',f'M2,{n},{n},{n},{n},record_overflow']:
        assert len(frame(text))==64
    with pytest.raises(ProtocolError):frame('x'*64)

def test_redump_after_bad_crc():
    p=Protocol();frames=run_frames()
    for raw in frames:
        if raw.startswith(b'END,'):
            with pytest.raises(ProtocolError):p.accept(frame('END,1,30,00000000'))
            break
        p.accept(raw)
    for raw in frames:
        kind,data=p.accept(raw)
        if kind=='DUMP':assert len(data.rows)==30

def test_failed_event_not_zero_and_zero_success(tmp_path):
    frames=run_frames(n=0);d=parse(frames);meta={'MET':d.metadata,'SUM':d.counters,'source':'synthetic','dump_complete':True,'run_id':d.run,'scenario':d.scenario}
    summary=summarize(d.rows,meta);assert summary['r_mean_us']=='' and summary['ok']==0

def test_strict_numeric():
    p=Protocol()
    with pytest.raises(ProtocolError):p.accept(frame('TEL,1,S0,2,3x'))
    with pytest.raises(ProtocolError):p.accept(frame('TEL,1,S8,2,3'))

def test_simulator_cfg_preserves_old_snapshot():
    clock=[0.0];sim=Simulator(lambda:clock[0]);sim.command('CFG,1,S0');sim.command('START,2');clock[0]=5;sim.poll();clock[0]=6;sim.press();sim.command('STOP,3');sim.command('CFG,4,S5')
    assert parse(sim.command('DUMP,5')).scenario=='S0'
