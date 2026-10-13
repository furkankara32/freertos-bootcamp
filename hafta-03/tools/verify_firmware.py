"""Check linked vector table and reproducibility metadata without a board."""
import argparse, hashlib, json, shutil, struct, subprocess
from pathlib import Path
from capture import verify_build
from protocol import require

def verify(path):
    path=Path(path);meta=verify_build(path)
    binary=path.with_name('week3_f407.bin').read_bytes()
    require(hashlib.sha256(binary).hexdigest()==meta['bin_sha256'],'BIN hash mismatch')
    require(len(binary)<=1024*1024,'Flash overflow')
    words=struct.unpack_from('<55I',binary)
    require(words[0]==0x20020000,'Wrong F407 main stack address')
    nm=shutil.which('arm-none-eabi-nm')
    if not nm:
        matches=sorted(Path('C:/ST').glob('**/arm-none-eabi-nm.exe'))
        require(bool(matches),'ARM nm not found');nm=str(matches[-1])
    symbols={}
    for line in subprocess.check_output([nm,str(path.with_name('week3_f407.elf'))],text=True).splitlines():
        fields=line.split()
        if len(fields)==3:symbols[fields[2]]=int(fields[0],16)
    expected={1:'Reset_Handler',3:'HardFault_Handler',11:'SVC_Handler',14:'PendSV_Handler',15:'SysTick_Handler',54:'USART2_IRQHandler'}
    for index,name in expected.items():
        require(words[index]&1==1,f'Non-Thumb vector {name}')
        require(words[index]&~1==symbols[name]&~1,f'Wrong vector binding: {name}')
        require(symbols[name]!=symbols['Default_Handler'],f'Default handler bound: {name}')
    return {'build_id':meta['build_id'],'config':meta['config'],'vectors_verified':list(expected.values()),'binary_bytes':len(binary),'status':'passed','hardware_tested':False}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('build',type=Path);a=p.parse_args();print(json.dumps(verify(a.build),indent=2))
