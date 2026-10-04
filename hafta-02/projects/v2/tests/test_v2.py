import json
import pytest
from interface.src.protocol import Protocol, ProtocolError, frame, Dump, stages
from interface.src.simulator import Simulator
from interface.src.storage import save_dump
from analysis.analyze import summarize


def v2_frames(scenario=5, variant='QWB', count=30):
    clock=[0.0];sim=Simulator(lambda:clock[0],version='PROTO3',variant=variant)
    frames=sim.command('HELLO,0')
    frames+=sim.command(f'CFG,1,S{scenario}')+sim.command('START,2')
    clock[0]=5;frames+=sim.poll()
    for _ in range(count):
        clock[0]+=.51;frames+=sim.poll()+sim.press()
    return frames+sim.command('STOP,3')


def parse(frames):
    parser=Protocol();dump=None
    for raw in frames:
        kind,data=parser.accept(raw)
        if kind=='DUMP':dump=data
    return dump


@pytest.mark.parametrize('variant',['Q','QW','QB','QWB'])
@pytest.mark.parametrize('scenario',range(6))
def test_v2_profiles_and_storage(tmp_path,variant,scenario):
    frames=v2_frames(scenario,variant);dump=parse(frames)
    assert dump.protocol=='PROTO3' and len(dump.rows)==30
    folder=save_dump(dump,tmp_path,b''.join(frames),True)
    assert folder.parent==tmp_path/'v2'/variant/'demo'
    meta=json.loads((folder/'metadata.json').read_text(encoding='utf-8'))
    summary=summarize(dump.rows,meta)
    assert meta['protocol']=='PROTO3' and summary['deadline_us']==10000
    assert summary['variant']==variant and summary['source']=='synthetic'


@pytest.mark.parametrize('key',['variant','deadline_us','slice_count','btn_txq_len','activation_wall_max_us','baud_actual'])
def test_v2_missing_required_metadata(key):
    with pytest.raises(ProtocolError,match='eksik'):
        parse([r for r in v2_frames(count=1) if not r.startswith(f'MET,1,{key},'.encode())])


@pytest.mark.parametrize('key,value',[('baud',115200),('prio_tel',2),('slice_count',1),('uart_brr',0),('deadline_us',20000),('queue_policy','fifo')])
def test_v2_invalid_configuration(key,value):
    frames=[frame(f'MET,1,{key},{value}') if r.startswith(f'MET,1,{key},'.encode()) else r for r in v2_frames(count=1)]
    with pytest.raises(ProtocolError):parse(frames)


def test_deadline_boundaries_and_wrap():
    dump=parse(v2_frames(count=4))
    for row,r in zip(dump.rows,[10000,10001,20000,20001]):
        t0=0xffffff00
        for i,t in enumerate([t0,t0+20,t0+40,t0+r-1400,t0+r]):row[f't{i}_us']=t&0xffffffff
    dump.counters['late_10ms']=3;dump.counters['late_20ms']=1
    dump.validate(4,dump.crc)
    dump.counters['late_10ms']=2
    with pytest.raises(ProtocolError,match='Geç'):dump.validate(4,dump.crc)


def test_unknown_protocol_and_v2_crc():
    with pytest.raises(ProtocolError):Protocol().accept(frame('SYS,RTOSLAT,FW2-QWB,PROTO4'))
    with pytest.raises(ProtocolError,match='CRC'):
        parse([frame('END,1,1,00000000') if r.startswith(b'END,') else r for r in v2_frames(count=1)])


def test_v2_drop_remains_visible():
    dump=parse(v2_frames(count=1));row=dump.rows[0]
    row.update(status='tx_drop',t3_us=None,t4_us=None)
    dump.counters.update(ok=0,btn_tx_drop=1,late_10ms=0,late_20ms=0)
    dump.validate(1,dump.crc)
    assert stages(row) is None
    meta={'protocol':'PROTO3','scenario':'S5','run_id':1,'source':'hardware','dump_complete':True,'MET':dump.metadata,'SUM':dump.counters}
    summary=summarize(dump.rows,meta)
    assert summary['tx_drop']==1 and summary['r_max_us']==''


def test_audit_rejects_synthetic_and_tampered_export(tmp_path):
    from analysis.v2_report import verified_load,evaluate
    frames=v2_frames();dump=parse(frames);folder=save_dump(dump,tmp_path,b''.join(frames),True)
    rows,meta=verified_load(folder)
    result=evaluate(rows,meta)
    assert not result['acceptance_pass'] and 'not hardware' in result['failures']
    text=(folder/'events.csv').read_text(encoding='utf-8')
    (folder/'events.csv').write_text(text.replace('ok','timeout',1),encoding='utf-8')
    with pytest.raises(ValueError,match='CRC-validated'):verified_load(folder)


def test_audit_requires_load_and_zero_losses():
    from analysis.v2_report import evaluate
    dump=parse(v2_frames());meta={'protocol':'PROTO3','scenario':'S5','run_id':1,'source':'hardware','dump_complete':True,'MET':dump.metadata.copy(),'SUM':dump.counters.copy(),
        'host_build':{'variant':'QWB','baud':460800,'elf_sha256':'a'*64}}
    # Unit fixture only; no synthetic data is saved as hardware evidence.
    meta['MET']['work_iters']=5000
    assert evaluate(dump.rows,meta)['acceptance_pass']
    meta['MET']['work_mean_us']=1000
    assert 'CPU calibration' in evaluate(dump.rows,meta)['failures']
    meta['MET']['work_mean_us']=5000;meta['SUM']['tel_q_drop']=1
    assert 'tel_q_drop' in evaluate(dump.rows,meta)['failures']
