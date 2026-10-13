"""Offline ARM build. Does not access or flash hardware."""
from pathlib import Path
import argparse, concurrent.futures, hashlib, json, os, shutil, subprocess
ROOT = Path(__file__).resolve().parent

def source_files():
    return sorted(p for p in ROOT.rglob('*') if p.is_file() and 'build' not in p.relative_to(ROOT).parts and p.suffix in {'.c','.h','.s','.ld','.py','.json'})

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--config',choices=['Debug','Release'],default='Release')
    ap.add_argument('--toolchain',type=Path)
    args=ap.parse_args()
    gcc=str(args.toolchain/'arm-none-eabi-gcc.exe') if args.toolchain else shutil.which('arm-none-eabi-gcc')
    if not gcc:
        found=sorted(Path('C:/ST').glob('**/arm-none-eabi-gcc.exe'))
        if not found: ap.error('ARM GCC not found; use --toolchain <bin directory>')
        gcc=str(found[-1])
    out=ROOT/'build'/args.config;out.mkdir(parents=True,exist_ok=True)
    version=subprocess.check_output([gcc,'--version'],text=True).splitlines()[0]
    manifest={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files()}
    identity=hashlib.sha256(json.dumps({'sources':manifest,'config':args.config,'gcc':version},sort_keys=True).encode()).hexdigest()
    (out/'build_identity.h').write_text(f'#define APP_BUILD_ID "{identity}"\n')
    v=ROOT/'vendor';hal=v/'Drivers/STM32F4xx_HAL_Driver';kernel=v/'freertos'
    sources=sorted((ROOT/'src').glob('*.c'))+sorted((ROOT/'startup').glob('*.s'))
    sources += [hal/'Src'/('stm32f4xx_hal'+s+'.c') for s in ['', '_cortex','_rcc','_rcc_ex','_gpio','_pwr','_pwr_ex','_flash','_flash_ex','_uart','_dma']]
    sources += [kernel/s for s in ['tasks.c','queue.c','list.c','portable/GCC/ARM_CM4F/port.c','portable/MemMang/heap_4.c']]
    sources += [v/s for s in ['systemview/SYSVIEW/SEGGER_SYSVIEW.c','systemview/Sample/FreeRTOSV11/SEGGER_SYSVIEW_FreeRTOS.c','rtt/RTT/SEGGER_RTT.c']]
    inc=[ROOT/'include',out,hal/'Inc',hal/'Inc/Legacy',v/'Drivers/CMSIS/Include',v/'Drivers/CMSIS/Device/ST/STM32F4xx/Include',kernel/'include',kernel/'portable/GCC/ARM_CM4F',v/'systemview/SYSVIEW',v/'systemview/SEGGER',v/'systemview/Sample/FreeRTOSV11',v/'rtt/RTT']
    cpu=['-mcpu=cortex-m4','-mthumb','-mfpu=fpv4-sp-d16','-mfloat-abi=hard']
    flags=[*cpu,'-Os' if args.config=='Release' else '-Og','-g3','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror','--specs=nano.specs']
    def compile_one(src):
        obj=out/(src.relative_to(ROOT).as_posix().replace('/','_')+'.o')
        cmd=[gcc,*flags,'-c',str(src),'-o',str(obj),'-DSTM32F407xx','-DUSE_HAL_DRIVER',*[f'-I{p}' for p in inc]]
        if src.suffix=='.c':cmd+=['-std=gnu11','-fstack-usage']
        # F407 HAL keeps bank arguments unused on this single-bank device.
        if src.is_relative_to(hal):cmd+=['-Wno-unused-parameter']
        r=subprocess.run(cmd,capture_output=True,text=True)
        return obj,r.returncode,' '.join(cmd)+'\n'+r.stdout+r.stderr
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(compile_one,sources))
    log='\n'.join(x[2] for x in results)
    if any(x[1] for x in results):
        (out/'build.log').write_text(log);print('\n'.join(line for line in log.splitlines() if 'error:' in line or 'warning:' in line));return 1
    elf=out/'week3_f407.elf'
    cmd=[gcc,*cpu,*[str(x[0]) for x in results],f'-T{ROOT/"STM32F407VG.ld"}','--specs=nano.specs','--specs=nosys.specs','-Wl,--gc-sections',f'-Wl,-Map={out/"week3_f407.map"}','-Wl,--print-memory-usage','-o',str(elf)]
    result=subprocess.run(cmd,capture_output=True,text=True);log+='\n'+' '.join(cmd)+'\n'+result.stdout+result.stderr
    (out/'build.log').write_text(log)
    if result.returncode:print(result.stderr);return result.returncode
    bindir=Path(gcc).parent;ext='.exe' if os.name=='nt' else ''
    for fmt,suffix in [('binary','bin'),('ihex','hex')]:subprocess.run([str(bindir/('arm-none-eabi-objcopy'+ext)),'-O',fmt,str(elf),str(elf.with_suffix('.'+suffix))],check=True)
    size=subprocess.check_output([str(bindir/('arm-none-eabi-size'+ext)),str(elf)],text=True)
    meta={'build_id':identity,'target':'STM32F407VG','board':'STM32F407G-DISC1','clock_hz':168000000,'tick_hz':1000,'timer_hz':1000000,'baud':230400,'freertos':'11.1.0','config':args.config,'gcc':version,'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'bin_sha256':hashlib.sha256(elf.with_suffix('.bin').read_bytes()).hexdigest(),'size':size,'hardware_tested':False}
    (out/'build.json').write_text(json.dumps(meta,indent=2));(out/'source-manifest.json').write_text(json.dumps(manifest,indent=2))
    print(result.stdout+size);print(f'BUILD OK: {elf}\nBuild ID: {identity}');return 0

if __name__=='__main__':raise SystemExit(main())
