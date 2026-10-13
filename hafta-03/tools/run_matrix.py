"""Run seven conditions sequentially on a connected board; save each trace before the next run."""
import argparse, json
from pathlib import Path
from capture import capture, ROOT
from protocol import MATRIX

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--port',required=True)
    p.add_argument('--output',type=Path,default=ROOT/'measurements/hardware')
    p.add_argument('--build',type=Path,default=ROOT/'firmware/build/Release/build.json')
    a=p.parse_args();session=a.output
    session.mkdir(parents=True,exist_ok=True)
    index={'complete':False,'runs':[],'source':'hardware_serial'}
    index_path=session/'session.json'
    index_path.write_text(json.dumps(index,indent=2))
    try:
        for i,(v,l,t) in enumerate(MATRIX,1):
            print(f'{i}/7: {v} {l} trace={t}',flush=True)
            f=capture(a.port,v,l,session,t,a.build);index['runs'].append(f.name)
            index_path.write_text(json.dumps(index,indent=2))
        index['complete']=True
    finally:index_path.write_text(json.dumps(index,indent=2))
    print(f'Complete: {session}\nNext: python tools/analyze.py "{session}"')

if __name__=='__main__':main()
