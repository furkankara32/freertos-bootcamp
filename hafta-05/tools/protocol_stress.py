"""Device-side boundary checks. Run with no UI serial connection."""
import sys,time,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import serial
from host.protocol import *
from tools.regression_check import wait_for
from tools.hardware import ROOT

def run(port='COM5'):
    results={};seq=10000;decoder=Decoder();frames=[]
    with serial.Serial(port,115200,timeout=.02,write_timeout=3) as wire:
        def send(kind,values=()):
            nonlocal seq
            seq+=1;wire.write(encode(kind,seq,values));return seq
        def wait(kind,command=None):
            def match():
                frames.extend(decoder.feed(wire.read(wire.in_waiting or 1)))
                return next((f for f in frames if f.kind==kind and (command is None or f.values[1]==command)),None)
            wait_for(match);return match()
        send(STOP);wait(DONE,0);frames.clear()
        for values in ([1,0,0,1000,1,1500],[1,1,1,1000,1,1500],[1,1,0,0,1,1500],[1,1,0,5001,1,1500],[1,1,0,1000,0,1500],[1,1,0,1000,101,1500]):
            command=send(START,values);assert wait(ERROR,command).values[2]==3
        results['invalid_parameters_rejected']=6
        command=send(START,[777,1,0,1000,1,1500]);wait(RUN_START,command)
        command=send(START,[778,2,0,1000,1,1500]);assert wait(ERROR,command).values[2]==4
        results['busy_start_rejected']=True
        for _ in range(4):send(SEQUENCE,[0,0,0,1000,1])
        frames.clear();send(STOP);wait(DONE,0)
        command=send(STATUS);state=wait(STATS,command).values
        assert state[2]==0 and state[11]==0
        results['stop_clears_active_and_pending']=True
        initial=state[9]
        for _ in range(10):wire.write(bulk(seq+1));seq+=100
        command=send(STATUS);state2=wait(STATS,command).values
        assert state2[9]-initial==1000
        assert all(state2[i]==state[i] for i in (4,5,6,7,8))
        results['sustained_rx_bytes']=100000;results['sustained_rx_loss']=0
        send(STOP)
    (ROOT/'docs/protocol-stress.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    print(json.dumps(results))

if __name__=='__main__':run()
