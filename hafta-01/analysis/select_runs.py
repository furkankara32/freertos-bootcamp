"""Choose the latest procedurally valid hardware run for each scenario.

Selection depends on sample count/spacing/integrity, never response time or loss
rate. All failed and earlier runs remain in the archive. Existing selected files
are not silently overwritten with different content.
"""
from pathlib import Path
import hashlib,json,shutil
from .analyze import load,analyze

def select(root=Path('.')):
    root=Path(root);chosen={};rejected=[]
    for path in sorted((root/'measurements/runs').glob('*/events.csv')):
        rows,meta=load(path.parent)
        intervals=[(b['t0_us']-a['t0_us'])&0xffffffff for a,b in zip(rows,rows[1:])]
        reasons=[]
        if meta['source']!='hardware':reasons.append('not hardware')
        if not meta.get('dump_complete'):reasons.append('incomplete dump')
        if meta['SUM']['accepted']<30:reasons.append('accepted < 30')
        if any(t<500000 for t in intervals):reasons.append('accepted edge interval < 0.5 s')
        if meta['MET']['result']!='COMPLETE':reasons.append('run result not COMPLETE')
        if not meta.get('host_build',{}).get('elf_sha256'):reasons.append('ELF hash missing')
        if reasons:rejected.append({'folder':str(path.parent.relative_to(root)),'reasons':reasons})
        else:chosen[meta['scenario']]=(path.parent,meta)
    missing=set(f'S{i}' for i in range(6))-chosen.keys()
    if missing:raise ValueError(f'Qualified runs missing: {sorted(missing)}')
    if len({m['host_build']['elf_sha256'] for _,m in chosen.values()})!=1:raise ValueError('Different ELF hashes in comparison set')
    def copy(source,dest):
        dest.parent.mkdir(parents=True,exist_ok=True)
        if dest.exists() and dest.read_bytes()!=source.read_bytes():raise FileExistsError(f'Refusing to overwrite: {dest}')
        shutil.copy2(source,dest)
    manifest={'rule':'latest hardware COMPLETE dump; accepted >=30; every accepted edge interval >=500000 us; one ELF; losses retained','runs':{},'excluded':rejected}
    folders=[]
    for scenario,(folder,meta) in sorted(chosen.items()):
        selected=root/'measurements/selected'/scenario
        for name in ['events.csv','metadata.json','derived.csv','serial_raw.bin']:copy(folder/name,selected/name)
        copy(folder/'events.csv',root/'measurements'/f'{scenario}.csv');copy(folder/'metadata.json',root/'measurements'/f'{scenario}_meta.json')
        manifest['runs'][scenario]={'folder':str(folder.relative_to(root)),'events_sha256':hashlib.sha256((folder/'events.csv').read_bytes()).hexdigest(),'accepted':meta['SUM']['accepted'],'elf_sha256':meta['host_build']['elf_sha256']}
        folders.append(selected)
    (root/'measurements/selection.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    summaries=analyze(folders,root/'analysis/plots')
    shutil.copy2(root/'analysis/plots/summary.csv',root/'measurements/summary.csv')
    print(json.dumps(summaries,indent=2))
    return summaries

if __name__=='__main__':select()
