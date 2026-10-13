"""Validate a complete hardware session and generate comparison reports."""
import argparse, csv, hashlib, json
from pathlib import Path
from protocol import MATRIX, require, validate, statistics
from record_files import csv_bytes, replace_files

def load_session(folder):
    folder=Path(folder).resolve();index=json.loads((folder/'session.json').read_text())
    require(index.get('source')=='hardware_serial' and index.get('complete') is True,'Not a completed hardware session')
    require(len(index['runs'])==7 and len(set(index['runs']))==7,'Seven distinct runs required')
    runs=[]
    for name,condition in zip(index['runs'],MATRIX):
        path=(folder/name).resolve();require(path.parent==folder,'Run path outside session')
        stored=json.loads(path.read_text());v,l,t=condition
        require(stored.get('source')=='hardware_serial' and stored.get('valid') is True,'Invalid or non-hardware record')
        raw=path.with_suffix('.txt');csvpath=path.with_suffix('.csv')
        require(hashlib.sha256(raw.read_bytes()).hexdigest()==stored['raw_sha256'],'Raw transcript hash mismatch')
        require(hashlib.sha256(csvpath.read_bytes()).hexdigest()==stored['csv_sha256'],'CSV hash mismatch')
        meta,rows,data=validate(raw.read_text().splitlines(),v,l,t,stored['build_id'])
        require(meta['valid'],'Dropped trace events')
        for key in meta:require(meta[key]==stored[key],f'Metadata mismatch: {key}')
        require(stored['local_build']['build_id']==meta['build_id'],'Build metadata mismatch')
        if t:require(path.with_suffix('.SVDat').read_bytes()==data,'Saved trace differs from UART data')
        stats=statistics(rows);require(stats==stored['statistics'],'Statistics mismatch')
        meta.update(statistics=stats,file=name);runs.append(meta)
    require(len({r['build_id'] for r in runs})==1,'Different firmware builds within matrix')
    require(len({r['run_id'] for r in runs})==7,'Duplicate/reset run IDs; repeat matrix without board reset')
    return runs

def fmt(n):return 'N/A' if n is None else f'{n:.2f}'

def write_report(runs,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    fields=['run_id','variant','load','trace_enabled','attempted','accepted','failed','consumed','failure_pct']
    for key in runs[0]['statistics']:
        fields.extend(f'{key}_{s}' for s in ['n','mean','max'])
    rows=[]
    for r in runs:
        row={k:r[k] for k in fields if k in r};row['failure_pct']=100*r['failed']/r['attempted']
        for key,s in r['statistics'].items():row.update({f'{key}_{n}':v for n,v in s.items()})
        rows.append([row.get(key) for key in fields])
    replace_files(out,{'comparison.csv':csv_bytes(fields,rows)})
    lines=['# Hafta 03 - Donanım ölçüm karşılaştırması','',f"Build kimliği: `{runs[0]['build_id']}`",'',
           'Süreler us cinsindedir. Send sütunu başarılı girişimleri, gecikme sütunu alınan mesajları kullanır. Başarısızlar gecikme ortalamasına sıfır olarak katılmaz.','',
           '| Koşu | Varyant/yük | Trace | Kabul / başarısız / tamamlanan | Send ort./maks. | Gecikme ort./maks. |',
           '|---|---|---|---|---|---|']
    for r in runs:
        s=r['statistics']['send_success_us'];g=r['statistics']['generation_to_receive_us']
        lines.append(f"| {r['run_id']} | {r['variant']}/{r['load']} | {int(r['trace_enabled'])} | {r['accepted']} / {r['failed']} / {r['consumed']} | {fmt(s['mean'])} / {fmt(s['max'])} | {fmt(g['mean'])} / {fmt(g['max'])} |")
    lines+=['','## Kontrollü farklar','', 'Farklar ikinci koşul eksi ilk koşuldur; tek örnek nedensellik için zaman çizgisiyle birlikte değerlendirilmelidir.','']
    for title,a,b in [('NORMAL A/B kapasite',runs[0],runs[1]),('NORMAL A/C bekleme',runs[0],runs[2]),('BURST A/B kapasite',runs[3],runs[4]),('BURST A/C bekleme',runs[3],runs[5]),('BURST A trace OFF/ON',runs[6],runs[3])]:
        sa=a['statistics'];sb=b['statistics']
        diff=lambda k,m: None if sa[k][m] is None or sb[k][m] is None else sb[k][m]-sa[k][m]
        lines.append(f"- {title}: kabul farkı {b['accepted']-a['accepted']:+d}; başarılı send ortalaması farkı {fmt(diff('send_success_us','mean'))} us; alınanların maksimum gecikme farkı {fmt(diff('generation_to_receive_us','max'))} us.")
    lines+=['','## Kayıt kapsamı','', 'CSV 44 girişimin tamamını, SystemView nominal 200 ms pencereyi kapsar. C’de enqueue öncesi bekleme gecikmeye dahildir. vTaskDelay dış servis beklemesi modelidir. Gözlenen maksimum kesin üst sınır değildir.','']
    for r in runs:
        tr=r['trace'];lines.append(f"- run {r['run_id']}: `{r['file']}`; "+(f"trace {tr['bytes']} bayt, drops={tr['drops']}, stop_reason={tr['stop_reason']}." if tr else 'trace kapalı.'))
    lines+=['','## İnsan incelemesi gereken kanıt','', 'CSV sonuç yorumu ve politika değerlendirmesi `analysis/yorum.md` içindedir; kayıtlar yenilenirse yorum da güncellenmelidir. Üç SystemView görseli ayrıca hazırlanmalıdır. Bu otomatik rapor scheduler olaylarını decode etmez; bloklanmayı kendiliğinden kanıtlamaz.','']
    (out/'comparison.md').write_text('\n'.join(lines),encoding='utf-8')
    (out/'validated-runs.json').write_text(json.dumps(runs,indent=2),encoding='utf-8')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('session',type=Path);p.add_argument('--output',type=Path)
    a=p.parse_args();runs=load_session(a.session);out=a.output or a.session/'analysis';write_report(runs,out);print(out)
