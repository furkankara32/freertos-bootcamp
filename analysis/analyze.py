"""Rebuild statistics/plots from exported events.csv + metadata.json.

Usage: python analysis/analyze.py measurements/runs --output analysis/results
Synthetic inputs require --allow-synthetic and are visibly labelled.
"""
import argparse,csv,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from interface.src.protocol import stages,ProtocolError,CSV_FIELDS,elapsed

def summarize(rows,meta):
    valid=[];invalid=0
    for row in rows:
        try:
            value=stages(row)
            if value:valid.append(value)
        except ProtocolError:invalid+=1
    m=meta['MET'];c=meta['SUM'];n=c['tel_generated']
    summary={'protocol':meta.get('protocol','PROTO2'),'variant':m.get('variant','V1'),'deadline_us':m.get('deadline_us',20000),'scenario':meta['scenario'],'run_id':meta['run_id'],'accepted':c['accepted'],'ok':len(valid),
        'late_completed':sum(x['r_us']>m.get('deadline_us',20000) for x in valid),'late_10ms':sum(x['r_us']>10000 for x in valid),'late_20ms':sum(x['r_us']>20000 for x in valid),'invalid_records':invalid,
        'dump_complete':meta['dump_complete'],'source':meta['source']}
    for status in ['button_q_drop','tx_drop','tx_error','timeout','record_overflow']:summary[status]=sum(r['status']==status for r in rows)
    for key in ['unrecorded_events','tel_q_drop','uart_tx_error','tx_timeout','drain_timeout','txq_hwm','buttonq_hwm']:summary[key]=c.get(key,'')
    for key in ['btn_txq_hwm','tel_txq_hwm','period_overrun','rx_error','format_error']:summary[key]=c.get(key,'')
    summary['telemetry_hz_actual']=(n-1)*1e6/elapsed(m['tel_last_us'],m['tel_first_us']) if n>=2 and elapsed(m['tel_last_us'],m['tel_first_us']) else (0 if meta['scenario']=='S0' else '')
    summary.update(period_mean_us=m['period_sum_us']/m['period_n'] if m['period_n'] else '',period_min_us=m['period_min_us'],period_max_us=m['period_max_us'])
    values=[x['r_us'] for x in valid]
    summary.update(r_min_us=min(values) if values else '',r_mean_us=sum(values)/len(values) if values else '',r_max_us=max(values) if values else '')
    for i in range(1,5):summary[f'd{i}_mean_us']=sum(x[f'd{i}_us'] for x in valid)/len(valid) if valid else ''
    return summary

def load(folder):
    meta=json.loads((folder/'metadata.json').read_text(encoding='utf-8'))
    with (folder/'events.csv').open(newline='',encoding='utf-8') as f:
        reader=csv.DictReader(f)
        if reader.fieldnames!=CSV_FIELDS:raise ValueError(f'Ham CSV kolonları yanlış: {folder}')
        rows=list(reader)
    for row in rows:
        row['event_id']=int(row['event_id'])
        for i in range(5):row[f't{i}_us']=int(row[f't{i}_us']) if row[f't{i}_us'] else None
    return rows,meta

def analyze(folders,output,allow_synthetic=False):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    output=Path(output);output.mkdir(parents=True,exist_ok=True);summaries=[];seen=set();identity=None
    for folder in folders:
        rows,meta=load(Path(folder))
        current=(meta.get('protocol','PROTO2'),meta['MET'].get('variant','V1'))
        if identity is not None and identity!=current:raise ValueError('Farklı protokol/varyantları aynı analizde birleştirmeyin')
        identity=current
        if meta['source']=='synthetic' and not allow_synthetic:raise ValueError('Sentetik girdi: --allow-synthetic gerekli')
        if meta['scenario'] in seen:raise ValueError('Senaryo başına tek koşu seçin; eski denemeleri sessiz birleştirmeyin')
        seen.add(meta['scenario']);summary=summarize(rows,meta);summaries.append(summary)
        fig,ax=plt.subplots(figsize=(9,4))
        valid=[(r['event_id'],stages(r)['r_us']/1000) for r in rows if r['status']=='ok']
        if valid:ax.plot(*zip(*valid),marker='o',markersize=3,label=f'R (n={len(valid)})')
        failed=[r['event_id'] for r in rows if r['status']!='ok']
        if failed:ax.scatter(failed,[-1]*len(failed),marker='x',label=f'Failure / no R (n={len(failed)})')
        deadline=meta['MET'].get('deadline_us',20000)/1000
        ax.axhline(deadline,color='red',linestyle='--',label=f'Deadline {deadline:g} ms')
        if deadline==10:ax.axhline(20,color='gray',linestyle=':',label='V1 20 ms')
        ax.set(xlabel='Event ID',ylabel='Response [ms]',title=f'{meta["MET"].get("variant","V1")} {meta["scenario"]} | {meta["source"].upper()} | accepted={summary["accepted"]}')
        ax.legend();ax.grid(alpha=.2);fig.tight_layout();fig.savefig(output/f'{meta["scenario"]}_response.png',dpi=160);plt.close(fig)
    summaries.sort(key=lambda s:s['scenario'])
    if not summaries:raise ValueError('Tamamlanmış events.csv bulunamadı')
    with (output/'summary.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(summaries[0]));writer.writeheader();writer.writerows(summaries)
    fig,ax=plt.subplots(figsize=(9,5));bottom=[0.0]*len(summaries)
    for i in range(1,5):
        values=[s[f'd{i}_mean_us']/1000 if s[f'd{i}_mean_us']!='' else 0 for s in summaries]
        ax.bar([s['scenario'] for s in summaries],values,bottom=bottom,label=f'd{i}');bottom=[a+b for a,b in zip(bottom,values)]
    for i,s in enumerate(summaries):ax.text(i,bottom[i],f'n={s["ok"]}, excluded={s["accepted"]-s["ok"]}',ha='center',va='bottom',fontsize=8)
    ax.set(ylabel='Mean stage duration [ms]',title=' / '.join(sorted(set(s['source'].upper() for s in summaries)))+' — same valid event set per scenario');ax.legend();ax.margins(y=.2);fig.tight_layout();fig.savefig(output/'stage_means.png',dpi=160);plt.close(fig)
    return summaries

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('input',type=Path);ap.add_argument('--output',type=Path,default=Path('analysis/results'));ap.add_argument('--allow-synthetic',action='store_true');args=ap.parse_args()
    folders=[args.input] if (args.input/'events.csv').exists() else [p.parent for p in sorted(args.input.rglob('events.csv'))]
    analyze(folders,args.output,args.allow_synthetic)
