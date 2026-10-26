"""ST-LINK/OpenOCD operations. No J-Link; trace extraction is after the run."""

import argparse, json, subprocess, tempfile, re, sys

from pathlib import Path

ROOT=next(p for p in Path(sys.executable if getattr(sys,'frozen',False) else __file__).resolve().parents if (p/'SPEC.md').exists())

def find_tool(name):

    paths=sorted(Path('C:/ST').glob('**/'+name))

    if not paths: raise RuntimeError(f'{name} bulunamadı (STM32CubeIDE araçları gerekli)')

    return paths[-1]

def openocd(commands, timeout=40):

    exe=find_tool('openocd.exe');scripts=sorted(Path('C:/ST').glob('**/st_scripts/interface/stlink.cfg'))[-1].parent.parent

    result=subprocess.run([str(exe),'-s',str(scripts),'-f','interface/stlink-dap.cfg','-f','target/stm32f4x.cfg','-c',commands],capture_output=True,text=True,timeout=timeout,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))

    if result.returncode: raise RuntimeError(result.stdout+'\n'+result.stderr)

    return result.stdout+'\n'+result.stderr

def symbols():

    elf=ROOT/'firmware/build/Release/week5_f407.elf'

    text=subprocess.check_output([str(find_tool('arm-none-eabi-nm.exe')),'-n',str(elf)],text=True)

    return {p[2]:int(p[0],16) for line in text.splitlines() if len(p:=line.split())==3 and re.fullmatch('[0-9a-fA-F]+',p[0])}

def flash():

    elf=(ROOT/'firmware/build/Release/week5_f407.elf').as_posix()

    return openocd(f'program {{{elf}}} verify reset exit',timeout=90)

def extract_trace(folder):
    """Read a stopped capture and always attempt to resume after SWD access."""
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True);sym=symbols()
    keys=['app_trace_data','app_trace_bytes','app_trace_dropped','app_trace_complete',
          'app_trace_reason','run_id','scenario','variant']
    with tempfile.TemporaryDirectory() as td:
        paths={key:Path(td)/(key+'.bin') for key in keys}
        data=folder/'trace.SVDat'
        try:
            commands=['init','halt']+[f'dump_image {{{path.as_posix()}}} 0x{sym[key]:x} 4' for key,path in paths.items()]+['shutdown']
            openocd('; '.join(commands))
            values={key:int.from_bytes(path.read_bytes(),'little') for key,path in paths.items()}
            size=values['app_trace_bytes'];addr=values['app_trace_data']
            if not values['app_trace_complete'] or not 0<size<=65536 or not 0x20000000<=addr or addr+size>0x20020000:
                raise RuntimeError('Invalid or incomplete RAM trace: '+str(values))
            openocd(f'init; halt; dump_image {{{data.as_posix()}}} 0x{addr:x} {size}; shutdown')
        finally:
            openocd('init; halt; resume; shutdown')
        if data.stat().st_size!=size:raise RuntimeError('Incomplete trace file')
        values.update(mode='ST-LINK RAM single-shot',size=size,
                      complete_window=values['app_trace_reason']==1 and values['app_trace_dropped']==0)
        (folder/'capture_metadata.json').write_text(json.dumps(values,indent=2),encoding='utf-8')
        return data,values

if __name__=='__main__':

    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['flash','trace']);ap.add_argument('--out',default=str(ROOT/'records/manual/systemview'));args=ap.parse_args()

    print(flash() if args.action=='flash' else extract_trace(args.out))


