"""Generate six labelled synthetic runs and reproduce plots without hardware."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from interface.src.simulator import Simulator
from interface.src.protocol import Protocol
from interface.src.storage import save_dump
from analysis.analyze import analyze

folders=[]
for scenario in range(6):
    clock=[0.0];sim=Simulator(lambda:clock[0]);sim.command(f'CFG,1,S{scenario}');sim.command('START,2');clock[0]=5;sim.poll()
    for i in range(30):clock[0]+=.51+(i%7)*.037;sim.poll();sim.press()
    frames=sim.command('STOP,3');p=Protocol()
    for raw in frames:
        kind,data=p.accept(raw)
        if kind=='DUMP':folders.append(save_dump(data,Path('measurements'),b''.join(frames),True))
analyze(folders,Path('analysis/demo_results'),True)
print('Six SYNTHETIC runs, 180 events: analysis/demo_results')
