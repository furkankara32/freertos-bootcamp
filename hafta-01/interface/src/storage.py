"""Atomic export: invalid/partial dumps never become events.csv."""
from pathlib import Path
from datetime import datetime, timezone
import csv, json, platform
from .protocol import CSV_FIELDS, stages

def save_dump(dump, root, raw, synthetic=False, extra=None):
    root=Path(root)
    if dump.protocol=='PROTO3':root=root/'v2'/dump.metadata['variant']
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')
    folder=root/('demo' if synthetic else 'runs')/f'{stamp}_{dump.scenario}_run{dump.run}'
    folder.mkdir(parents=True,exist_ok=False)
    (folder/'serial_raw.bin').write_bytes(raw)
    metadata={'protocol':dump.protocol,'run_id':dump.run,'scenario':dump.scenario,'source':'synthetic' if synthetic else 'hardware',
        'dump_complete':True,'MET':dump.metadata,'SUM':dump.counters,'host_python':platform.python_version(),
        'host_platform':platform.platform(),'captured_utc':stamp,**(extra or {})}
    (folder/'metadata.json').write_text(json.dumps(metadata,indent=2,ensure_ascii=False),encoding='utf-8')
    path=folder/'events.csv.partial'
    with path.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=CSV_FIELDS);writer.writeheader();writer.writerows(dump.rows)
    path.rename(folder/'events.csv')
    with (folder/'derived.csv').open('w',newline='',encoding='utf-8') as f:
        names=['event_id','status','d1_us','d2_us','d3_us','d4_us','r_us']
        writer=csv.DictWriter(f,fieldnames=names);writer.writeheader()
        for row in dump.rows:writer.writerow({'event_id':row['event_id'],'status':row['status'],**(stages(row) or {})})
    return folder
