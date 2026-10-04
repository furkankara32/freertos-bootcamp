"""Reproducible build from checked-in sources; no CubeIDE workspace required."""
from pathlib import Path
import argparse, concurrent.futures, hashlib, json, os, shutil, subprocess

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'firmware/Homework_001'

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', choices=['Debug', 'Release'], default='Release')
    ap.add_argument('--variant', choices=['Q','QW','QB','QWB'], default='QWB')
    ap.add_argument('--trace', choices=['systemview','none'], default='systemview')
    ap.add_argument('--toolchain', help='Directory containing arm-none-eabi-gcc.exe')
    args = ap.parse_args()
    gcc = shutil.which('arm-none-eabi-gcc')
    if args.toolchain:
        gcc = str(Path(args.toolchain)/'arm-none-eabi-gcc.exe')
    if not gcc:
        choices = sorted(Path('C:/ST').glob('**/arm-none-eabi-gcc.exe'))
        if not choices: ap.error('ARM GCC bulunamadı; --toolchain <bin> kullanın')
        gcc = str(choices[-1])
    out = ROOT/'firmware/build/v2'/args.variant/args.config/args.trace
    out.mkdir(parents=True, exist_ok=True)
    opt = '-Os' if args.config == 'Release' else '-O0'
    provenance = json.loads((ROOT.parents[1]/'provenance/v2-source.json').read_text(encoding='utf-8-sig'))
    sha = provenance['commit']
    manifest = {str(p.relative_to(PROJECT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(PROJECT.rglob('*')) if p.is_file() and p.suffix in {'.c','.h','.s','.ld'}}
    original = {f['path'].removeprefix('firmware/Homework_001/'):f['sha256'] for f in provenance['files']}
    dirty = any(original.get(p)!=h for p,h in manifest.items())
    includes = ['Inc','Drivers/STM32F4xx_HAL_Driver/Inc','Drivers/STM32F4xx_HAL_Driver/Inc/Legacy',
        'Drivers/CMSIS/Include','Drivers/CMSIS/Device/ST/STM32F4xx/Include',
        'Middlewares/Third_Party/FreeRTOS/Source/include','Middlewares/Third_Party/FreeRTOS/Source/CMSIS_RTOS_V2',
        'Middlewares/Third_Party/FreeRTOS/Source/portable/GCC/ARM_CM4F']
    includes += ['Middlewares/SEGGER/'+d for d in ['Config','SYSVIEW','SEGGER','RTT','FreeRTOS']]
    common = ['-mcpu=cortex-m4','-mthumb','-mfpu=fpv4-sp-d16','-mfloat-abi=hard',opt,'-g3',
        '-ffunction-sections','-fdata-sections','-Wall','-Wextra','--specs=nano.specs']
    sources = sorted(PROJECT.glob('Src/*.c')) + sorted(PROJECT.glob('Drivers/STM32F4xx_HAL_Driver/Src/*.c'))
    kernel = PROJECT/'Middlewares/Third_Party/FreeRTOS/Source'
    sources += sorted(kernel.glob('*.c')) + [kernel/'CMSIS_RTOS_V2/cmsis_os2.c',kernel/'portable/GCC/ARM_CM4F/port.c',kernel/'portable/MemMang/heap_4.c']
    sources += sorted(PROJECT.glob('Startup/*.s'))
    if args.trace == 'systemview':
        sources += sorted((PROJECT/'Middlewares/SEGGER').rglob('*.c'))
    objects = [out/(str(s.relative_to(PROJECT)).replace(os.sep,'_').replace('/','_')+'.o') for s in sources]
    def compile_one(pair):
        src,obj=pair
        cmd=[gcc,*common,'-c',str(src),'-o',str(obj)]
        if src.suffix=='.c':
            cmd+=['-std=gnu11','-fstack-usage','-DSTM32F407xx','-DUSE_HAL_DRIVER',
                f'-DAPP_TRACE={int(args.trace=="systemview")}',f'-DAPP_PROFILE={dict(Q=1,QW=2,QB=3,QWB=4)[args.variant]}',f'-DAPP_GIT_SHA="{sha}"',f'-DAPP_BUILD_CONFIG="{args.config}"',f'-DAPP_OPT_LEVEL="{opt[1:]}"']
            cmd += [f'-I{PROJECT/i}' for i in includes]
        r=subprocess.run(cmd,capture_output=True,text=True)
        return r.returncode, ' '.join(cmd)+'\n'+r.stdout+r.stderr
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        results=list(pool.map(compile_one,zip(sources,objects)))
    log='\n'.join(r[1] for r in results)
    if any(r[0] for r in results):
        (out/'build.log').write_text(log); print(log); raise SystemExit(1)
    elf=out/'Homework_001.elf'
    cmd=[gcc,*common,*map(str,objects),'-o',str(elf),f'-T{PROJECT / "STM32F407VGTX_FLASH.ld"}',
        '--specs=nosys.specs',f'-Wl,-Map={out / "Homework_001.map"}','-Wl,--gc-sections','-Wl,--start-group','-lc','-lm','-Wl,--end-group']
    r=subprocess.run(cmd,capture_output=True,text=True); log+='\n'+' '.join(cmd)+'\n'+r.stdout+r.stderr
    (out/'build.log').write_text(log)
    if r.returncode: print(r.stderr);raise SystemExit(r.returncode)
    bindir=Path(gcc).parent
    size=subprocess.check_output([str(bindir/'arm-none-eabi-size.exe'),str(elf)],text=True)
    subprocess.run([str(bindir/'arm-none-eabi-objcopy.exe'),'-O','binary',str(elf),str(out/'Homework_001.bin')],check=True)
    version=subprocess.check_output([gcc,'--version'],text=True).splitlines()[0]
    meta={'design_version':2,'variant':args.variant,'protocol':'PROTO3','baud':460800 if args.variant in {'QB','QWB'} else 115200,'source_sha':sha,'git_dirty':dirty,'config':args.config,'optimization':opt,'gcc':version,
          'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'size':size}
    (out/'build.json').write_text(json.dumps(meta,indent=2))
    meta.update(trace_backend=args.trace, source_manifest_sha256=hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest(),
                kernel='10.3.1', timestamp_hz=168000000, trace_buffer_bytes=65536 if args.trace=='systemview' else 0)
    (out/'build.json').write_text(json.dumps(meta,indent=2))
    (out/'source-manifest.json').write_text(json.dumps(manifest,indent=2))
    warnings=[line for line in log.splitlines() if 'warning:' in line]
    print(size);print('\n'.join(warnings)); print(f'Build OK: {elf}\nWarnings: {len(warnings)}')

if __name__=='__main__': main()
