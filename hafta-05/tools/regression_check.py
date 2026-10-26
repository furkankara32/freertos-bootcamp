"""Real board regression using the EXE's session and record store."""
import sys,time,json,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import serial
from host.protocol import *
from host.session import Session
from host.record_store import complete_capture
from tools.hardware import extract_trace,ROOT

def wait_for(predicate,seconds=5):
    end=time.monotonic()+seconds
    while time.monotonic()<end:
        if predicate():return
        time.sleep(.01)
    raise AssertionError('Timed out waiting for device response')

def protocol_faults(port):
    with serial.Serial(port,115200,timeout=.03) as wire:
        wire.write(encode(STOP,900));time.sleep(.25);wire.reset_input_buffer()
        bad=bytearray(encode(HELLO,901));bad[40]^=1
        wire.write(b'noise'+bad)
        good=encode(HELLO,902)
        for offset in range(0,100,7):wire.write(good[offset:offset+7]);time.sleep(.002)
        decoder=Decoder();frames=[]
        def received(kind):
            frames.extend(decoder.feed(wire.read(wire.in_waiting or 1)))
            return any(f.kind==kind for f in frames)
        wait_for(lambda:received(MSG_HELLO))
        frames.clear();wire.write(encode(START,903,[1,1,0,0xffffffff,1,1500]))
        wait_for(lambda:received(ERROR))
        assert any(f.kind==ERROR and f.values[1]==903 for f in frames)
    return {'corrupt_frame_recovery':True,'fragmented_frame':True,'invalid_start_rejected':True}

def run(port,scenario,variant,cycles=8):
    frames=[];errors=[];session=Session(frames.append,errors.append)
    try:
        session.connect(port);wait_for(lambda:session.identity is not None)
        session.send(STOP);wait_for(lambda:any(f.kind==DONE and f.values[1]==0 for f in frames))
        frames.clear();session.send(STATUS);wait_for(lambda:any(f.kind==STATS for f in frames))
        baseline=next(f.values for f in frames if f.kind==STATS);frames.clear()
        assert baseline[2]==0 and baseline[11]==0,'STOP did not clear execution/queue'
        period=100 if scenario==4 else 1000
        folder=session.begin(ROOT/'records',scenario,variant,period,cycles)
        wait_for(lambda:any(f.kind==RUN_START for f in frames));run_id=session.run_id
        begin=time.monotonic();triggered=False
        duration=period/1000*cycles*4+(2.2 if scenario==4 else .4)
        while time.monotonic()-begin<duration:
            elapsed=time.monotonic()-begin
            if not triggered and elapsed>(.90 if scenario in (2,3) else .15):
                if scenario==1:session.send_bulk()
                if scenario==2:session.send(DIAG)
                if scenario==3:session.send(WORK,[200])
                if scenario==4:
                    for _ in range(4):session.send(SEQUENCE,[0,0,0,100,1])
                triggered=True
            if errors:raise AssertionError(errors)
            time.sleep(.01)
        marker=len(frames);session.send(STATUS)
        wait_for(lambda:any(f.kind==STATS for f in frames[marker:]))
        stats=next(f.values for f in frames[marker:] if f.kind==STATS)
        marker=len(frames);session.send(STOP)
        wait_for(lambda:any(f.kind==DONE and f.values[0]==run_id and f.values[1]==0 for f in frames[marker:]))
        time.sleep(.15);folder=session.finish();session.close()
        _,meta=extract_trace(folder/'systemview');folder=complete_capture(folder,meta)
        led=[f for f in frames if f.kind==LED and f.values[0]==run_id and f.values[2]<4]
        maximum=max(f.values[8] for f in led)
        assert len(led)>=cycles*4,(scenario,variant,len(led))
        assert all(stats[i]==baseline[i] for i in (4,5,6,7,8)),('loss/error counters',stats,baseline)
        assert not errors and session.decoder.rejected_bytes==0
        if scenario==1:assert stats[9]-baseline[9]==100
        if scenario==4:assert stats[11]==(3 if variant==0 else 0),stats[11]
        elif scenario in (2,3) and variant==0:assert maximum>20000,maximum
        else:assert maximum<10000,maximum
        summary=json.loads((folder/'summary.json').read_text())
        summary.update(scenario=scenario,variant=variant,pending_commands=stats[11],load_frames=stats[9]-baseline[9],source='hardware',passed=True,trace_bytes=meta['size'])
        (folder/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
        print(json.dumps(summary),flush=True)
        return summary
    finally:session.close()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--port',default='COM5');ap.add_argument('--cycles',type=int,default=8);args=ap.parse_args()
    results={'protocol':protocol_faults(args.port),'firmware':json.loads((ROOT/'firmware/build/Release/build.json').read_text())['build_id'],'variants':[]}
    for scenario,variant in [(1,0),(2,0),(2,1),(2,2),(3,0),(3,1),(4,0),(4,1)]:
        results['variants'].append(run(args.port,scenario,variant,args.cycles))
        (ROOT/'docs/regression-results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')

if __name__=='__main__':main()
