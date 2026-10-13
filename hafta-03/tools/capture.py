"""Capture one real board run. No simulation or automatic flashing."""
import argparse, hashlib, json, time
from pathlib import Path
from protocol import HELLO, COLUMNS, require, validate, statistics
from record_files import csv_bytes, replace_files

ROOT=Path(__file__).resolve().parents[1]

def verify_build(path):
    path=Path(path);meta=json.loads(path.read_text())
    require(meta['target']=='STM32F407VG','Wrong build target')
    elf=path.with_name('week3_f407.elf')
    require(hashlib.sha256(elf.read_bytes()).hexdigest()==meta['elf_sha256'],'ELF hash mismatch')
    manifest=json.loads(path.with_name('source-manifest.json').read_text())
    for name,digest in manifest.items():
        require(hashlib.sha256((ROOT/'firmware'/name).read_bytes()).hexdigest()==digest,f'Source changed: {name}; rebuild first')
    return meta

def capture(port,variant,load,out,trace=True,build=None,serial_factory=None,check_only=False):
    build=Path(build or ROOT/'firmware/build/Release/build.json')
    compiled=verify_build(build)
    if serial_factory is None:
        import serial
        serial_factory=serial.Serial
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    stem='connection' if check_only else f'{variant}_{load}_trace{int(trace)}'
    lines=[];startup_lines=[];pending=bytearray()
    try:
        with serial_factory(port,230400,timeout=.2,write_timeout=2) as ser:
            ser.reset_input_buffer()
            def send(s):ser.write((s+'\n').encode('ascii'));ser.flush()
            def until(prefix,seconds=20,startup=False):
                deadline=time.monotonic()+seconds
                while time.monotonic()<deadline:
                    if b'\n' not in pending:
                        pending.extend(ser.read(max(1,min(4096,ser.in_waiting))))
                        require(len(pending)<65536,'Serial frame too long')
                    while b'\n' in pending:
                        raw,_,rest=pending.partition(b'\n');pending[:]=rest
                        line=raw.decode('ascii').strip()
                        if not line:continue
                        if startup:
                            startup_lines.append(line)
                            if line in {'#ERROR,BAD_COMMAND','#ERROR,LINE_TOO_LONG'}:
                                require(sum(s.startswith('#ERROR') for s in startup_lines)<=2,'Repeated startup command errors; check serial link')
                                continue
                        else:
                            lines.append(line)
                        require(not line.startswith('#ERROR'),line)
                        if line.startswith(prefix):return line.split(',')[1:]
                raise TimeoutError(f'No {prefix}; check reset/resume, port and wiring')
            # reset_input_buffer clears the PC side only. Invalidate and end
            # a stale device-side line before HELLO. The extra non-whitespace
            # byte also prevents a pending RUN command from being executed.
            send('\x18\nHELLO')
            hello=until('#HELLO,',startup=True)
            require(hello==HELLO,'Wrong board firmware')
            lines.append('#HELLO,'+','.join(hello))
            send('BUILD');require(until('#BUILD,')==[compiled['build_id']],'Loaded firmware differs from local build')
            if check_only:
                path=out/(stem+'.json')
                path.write_text(json.dumps({'source':'hardware_connection','port':port,'build_id':compiled['build_id'],'valid':True,'scenario_started':False,'startup_lines':startup_lines,'lines':lines},indent=2),encoding='utf-8')
                return path
            send('TRACE ON' if trace else 'TRACE OFF');until('#ACK,')
            send(f'RUN {variant} {load}');until('#RUN,');until('#END,')
            if trace:send('TRACE');until('#TRACE_END,',30)
        meta,rows,data=validate(lines,variant,load,trace,compiled['build_id'])
        meta.update({'port':port,'local_build':compiled,'statistics':statistics(rows),'startup_lines':startup_lines,'captured_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())})
        require(meta['valid'],f'Trace drops detected: {stem}')
        raw=('\n'.join(lines)+'\n').encode('utf-8')
        csvdata=csv_bytes(COLUMNS,(r[:5]+[r[5] if r[2] else ''] for r in rows))
        meta['raw_sha256']=hashlib.sha256(raw).hexdigest()
        meta['csv_sha256']=hashlib.sha256(csvdata).hexdigest()
        files={stem+'.txt':raw,stem+'.csv':csvdata}
        if trace:files[stem+'.SVDat']=data
        files[stem+'.json']=json.dumps(meta,indent=2).encode('utf-8')
        replace_files(out,files)
        for suffix in ('.failed.txt','.failed.json'):
            (out/(stem+suffix)).unlink(missing_ok=True)
        return out/(stem+'.json')
    except Exception as exc:
        (out/(stem+'.failed.txt')).write_text('\n'.join(startup_lines+lines)+'\n',encoding='utf-8')
        (out/(stem+'.failed.json')).write_text(json.dumps({'valid':False,'error':str(exc),'partial_hex':pending.hex(),'variant':variant,'load':load,'trace':trace},indent=2))
        raise

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--port',required=True)
    p.add_argument('--variant',choices=list('ABC'),default='A');p.add_argument('--load',choices=['NORMAL','BURST'],default='NORMAL')
    p.add_argument('--check-only',action='store_true',help='Check HELLO/BUILD without starting a scenario')
    p.add_argument('--output',type=Path,default=ROOT/'measurements/hardware');p.add_argument('--build',type=Path,default=ROOT/'firmware/build/Release/build.json');p.add_argument('--no-trace',action='store_true')
    a=p.parse_args()
    try:
        print(capture(a.port,a.variant,a.load,a.output,not a.no_trace,a.build,check_only=a.check_only))
    except (ValueError,TimeoutError,OSError) as exc:
        p.exit(1,f'Kayit baslatilamadi veya tamamlanamadi: {exc}\nHata ayrintilari: {a.output}\n')
