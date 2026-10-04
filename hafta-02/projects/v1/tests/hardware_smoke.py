"""Real board smoke test; never fabricates button events.

Run one scenario, wait for physical button presses, stop and validate its dump.
This is a smoke run unless >=30 accepted physical presses were collected.
"""
import argparse,json,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import serial
from interface.src.protocol import Decoder,Protocol,ProtocolError
from interface.src.storage import save_dump

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--port',required=True);ap.add_argument('--scenario',choices=[f'S{i}' for i in range(6)],default='S0');ap.add_argument('--seconds',type=float,default=15);ap.add_argument('--target',type=int,default=0);ap.add_argument('--formal',action='store_true');ap.add_argument('--output',type=Path,default=Path('measurements'));args=ap.parse_args()
    decoder=Decoder();protocol=Protocol();raw=bytearray();events=[];result=None
    with serial.Serial(args.port,115200,timeout=.05,write_timeout=1) as port:
        req=int(time.time())%60000+100
        def read_until(predicate,seconds):
            nonlocal result
            end=time.monotonic()+seconds
            while time.monotonic()<end:
                chunk=port.read(min(max(port.in_waiting,1),4096));raw.extend(chunk)
                for line in decoder.feed(chunk):
                    kind,data=protocol.accept(line);events.append((kind,data))
                    if kind=='DUMP':result=data
                    if kind not in {'TEL','M1','M2','MET','SUM','BEGIN'}:print(kind,data if kind!='DUMP' else f'{len(data.rows)} records',flush=True)
                    if predicate(kind,data):return True
                if decoder.errors:raise ProtocolError('; '.join(decoder.errors))
            return False
        port.write(b'HELLO,0\n')
        if not read_until(lambda k,d:k=='EXP',3):raise RuntimeError('HELLO yanıtı yok; TX/RX/GND/port kontrol edin')
        for command,expected in [(f'CFG,{req},{args.scenario}','CONFIGURED'),(f'START,{req+1}','ARMED')]:
            port.write((command+'\n').encode())
            if not read_until(lambda k,d:k=='EXP' and d[2]==expected,10):raise RuntimeError(f'{command} tamamlanmadı')
        print(f'ARMED: {args.seconds:g} saniye fiziksel butona basabilirsiniz.',flush=True)
        received=0
        def target_reached(kind,data):
            nonlocal received
            if kind=='BTN':received+=1
            return bool(args.target and received>=args.target)
        read_until(target_reached,args.seconds)
        port.write(f'STOP,{req+2}\n'.encode())
        if not read_until(lambda k,d:k=='DUMP',15):raise RuntimeError('Tam dump alınamadı')
    intervals=[(b['t0_us']-a['t0_us'])&0xffffffff for a,b in zip(result.rows,result.rows[1:])]
    extra={'port':args.port,'purpose':'formal_candidate' if args.target or args.formal else 'hardware_smoke','formal_sample_count_met':result.counters['accepted']>=30,
        'press_spacing_met':all(x>=500000 for x in intervals),'press_min_interval_us':min(intervals) if intervals else None}
    build=Path('firmware/build/Release/build.json')
    if build.exists():extra['host_build']=json.loads(build.read_text())
    folder=save_dump(result,args.output,raw,False,extra)
    print(f'SAVED {folder}',flush=True)
    print(json.dumps({'accepted':result.counters['accepted'],'metadata':result.metadata,'counters':result.counters},indent=2),flush=True)

if __name__=='__main__':main()
