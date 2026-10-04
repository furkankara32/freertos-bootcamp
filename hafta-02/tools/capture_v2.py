"""Real UART + frozen RTT-buffer capture via existing ST-LINK. No probe conversion.
Never halts the core. No synthetic button events.
"""
from pathlib import Path
import argparse, concurrent.futures, datetime, hashlib, json, re, struct, subprocess, time, sys
W=Path(__file__).resolve().parents[1];ROOT=W/'projects/v2'
sys.path.insert(0,str(ROOT))
from interface.src.protocol import Protocol, Decoder
from interface.src.storage import save_dump
import serial

def find_tool(pattern):
    found=sorted(Path('C:/ST').glob(pattern))
    if not found:raise RuntimeError(f'Tool not found: {pattern}')
    return found[-1]

def export_trace(elf,folder):
    nm=find_tool('**/arm-none-eabi-nm.exe')
    symbols={m[2]:int(m[1],16) for line in subprocess.check_output([str(nm),'-n',str(elf)],text=True).splitlines()
             if (m:=re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)',line))}
    oc=find_tool('**/openocd.exe');cfg=find_tool('**/st_scripts/target/stm32f4x.cfg').parents[1]
    ram=folder/'ram.bin'
    commands=('init; poll; targets; '
              'if {[stm32f4x.cpu curstate] ne "running"} {error "Target is not running"}; '
              f'dump_image {{{ram.as_posix()}}} 0x20000000 0x20000; '
              'poll; targets; if {[stm32f4x.cpu curstate] ne "running"} {error "Target stopped"}; shutdown')
    result=subprocess.run([str(oc),'-s',str(cfg),'-f','interface/stlink-dap.cfg','-c','transport select dapdirect_swd',
       '-f','target/stm32f4x.cfg','-c','adapter speed 1800','-c',commands],capture_output=True,text=True,timeout=25)
    (folder/'openocd.log').write_text(result.stdout+result.stderr)
    if result.returncode:raise RuntimeError('OpenOCD failed; see '+str(folder/'openocd.log'))
    data=ram.read_bytes()
    def u32(addr):return struct.unpack_from('<I',data,addr-0x20000000)[0]
    complete=u32(symbols['app_trace_capture_complete']); size=u32(symbols['app_trace_bytes'])
    dropped=u32(symbols['app_trace_dropped'])
    cb=symbols['_SEGGER_RTT'];header=data[cb-0x20000000:cb-0x20000000+16]
    if not header.startswith(b'SEGGER RTT'):raise RuntimeError('Invalid RTT control block')
    # Cortex-M32 RTT: ID[16], MaxUp/MaxDown[4 each], six-word up descriptor.
    desc=cb+24+24
    ptr,capacity,wr,rd=[u32(desc+off) for off in (4,8,12,16)]
    if not complete or size!=wr or rd!=0 or not 0<size<capacity:
        raise RuntimeError(f'Capture not frozen or invalid: complete={complete}, size={size}, wr={wr}, rd={rd}')
    if not 0x20000000<=ptr<ptr+size<=0x20020000:raise RuntimeError('RTT buffer outside SRAM')
    trace=folder/'recording.SVDat';trace.write_bytes(data[ptr-0x20000000:ptr-0x20000000+size])
    info={'rtt_control_block':hex(cb),'buffer':hex(ptr),'capacity':capacity,'bytes':size,
          'capture_complete':bool(complete),'dropped_events':dropped,'clean':dropped==0,'read_offset':rd,'trace_sha256':hashlib.sha256(trace.read_bytes()).hexdigest(),
          'method':'ST-LINK: read frozen trace from SRAM with CPU running; no halt/reset/resume command'}
    (folder/'trace.json').write_text(json.dumps(info,indent=2))
    return trace,info

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--port',default='COM5');ap.add_argument('--scenario',default='S0',choices=[f'S{i}' for i in range(6)])
    ap.add_argument('--windows',type=int,default=1);ap.add_argument('--window-ms',type=int,default=500)
    ap.add_argument('--label',default='pilot');args=ap.parse_args()
    if not 50<=args.window_ms<=2000:ap.error('window-ms: 50..2000')
    out=W/'traces/v2'/args.scenario/(datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'-'+args.label);out.mkdir(parents=True)
    elf=ROOT/'firmware/build/v2/QWB/Release/systemview/Homework_001.elf'
    build=json.loads(elf.with_name('build.json').read_text());raw=bytearray();decoder=Decoder();parser=Protocol();dump=None
    with serial.Serial(args.port,460800,timeout=.05) as ser:
        def read(seconds):
            nonlocal dump
            until=time.monotonic()+seconds
            while time.monotonic()<until:
                block=ser.read(4096);raw.extend(block)
                for frame in decoder.feed(block):
                    kind,value=parser.accept(frame)
                    if kind=='DUMP':dump=value
        req=int(time.time())%50000+100
        def send(text):ser.write((text+'\n').encode());ser.flush()
        send('HELLO,0');read(.3)
        if b'FW2-QWB,PROTO3' not in raw:raise RuntimeError('Expected V2-QWB firmware missing')
        send(f'CFG,{req},{args.scenario}');read(.3)
        send(f'START,{req+1}');read(6)
        if b',ARMED,' not in raw:
            (out/"serial_raw.bin").write_bytes(raw)
            raise RuntimeError("Experiment did not arm; inspect serial_raw.bin")
        traces=[]
        for n in range(args.windows):
            print(f'CAPTURE {n+1}/{args.windows}: press USER now (window {args.window_ms} ms)',flush=True)
            send(f'TRACE,{req+10+n},{args.window_ms}');read(args.window_ms/1000+.25)
            folder=out/f'window-{n+1:02d}';folder.mkdir()
            # Keep draining the UART while the independent SWD export runs.
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future=pool.submit(export_trace,elf,folder)
                while not future.done():read(.1)
                trace,info=future.result()
            traces.append(str(trace))
            print(f'Saved {info["bytes"]} bytes: {trace}',flush=True)
            read(.3)
        send(f'STOP,{req+2}');read(4)
        if dump is None:raise RuntimeError('No CRC-valid experiment dump received')
        measurement=save_dump(dump,W/'measurements/pilots',bytes(raw),False,
             extra={'purpose':'setup pilot; not formal acceptance','build':build,'cpu_halted':False})
    (out/'serial_raw.bin').write_bytes(raw)
    (out/'dump.json').write_text(json.dumps({'rows':dump.rows,'metadata':dump.metadata,'counters':dump.counters},indent=2))
    meta={'purpose':'setup pilot, NOT formal timing acceptance','scenario':args.scenario,'build':build,
          'trace_files':traces,'decoder_errors':decoder.errors,'accepted':dump.counters.get('accepted'),
          'measurement_folder':str(measurement),'cpu_halted':False,
          'warning':'Setup pilot; trace-window preparation and SWD readout overhead must be considered in formal experiments.'}
    (out/'session.json').write_text(json.dumps(meta,indent=2));print(json.dumps(meta,indent=2))
    print('OUTPUT='+str(out))
if __name__=='__main__':main()
