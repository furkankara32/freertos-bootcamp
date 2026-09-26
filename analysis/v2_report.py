"""Audit V2 runs without filtering out slow/lost events.

Usage: python -m analysis.v2_report measurements/v2/QWB/runs --output analysis/v2/QWB
Every run is retained in the audit. No latest/best-run cherry-picking occurs.
"""
import argparse,csv,json,hashlib
from pathlib import Path
from .analyze import load,summarize,analyze
from interface.src.protocol import Protocol,Decoder,elapsed


def verified_load(folder):
    rows,meta=load(folder)
    if meta.get('protocol')!='PROTO3':raise ValueError('V2 audit requires PROTO3')
    decoder=Decoder();parser=Protocol();parser.version='PROTO3';matched=False
    # Raw capture may start after HELLO when a long connection was rotated.
    # The completed, CRC-validated dump must match the exported files exactly.
    for line in decoder.feed((folder/'serial_raw.bin').read_bytes()):
        try:kind,value=parser.accept(line)
        except ValueError:continue
        if kind=='DUMP' and value.rows==rows and value.metadata==meta['MET'] and value.counters==meta['SUM'] and value.run==meta['run_id'] and value.scenario==meta['scenario']:
            matched=True
    if not matched:raise ValueError('CSV/metadata does not match a complete CRC-validated raw dump')
    return rows,meta


def evaluate(rows,meta,minimum=30):
    s=summarize(rows,meta);m=meta['MET'];c=meta['SUM'];fail=[]
    if meta.get('source')!='hardware':fail.append('not hardware')
    if not meta.get('dump_complete') or m['result']!='COMPLETE':fail.append('incomplete run')
    if c['accepted']<minimum:fail.append(f'accepted < {minimum}')
    if any(elapsed(b['t0_us'],a['t0_us'])<500000 for a,b in zip(rows,rows[1:])):fail.append('press spacing < 0.5 s')
    if s['ok']!=c['accepted'] or s['invalid_records']:fail.append('lost/invalid button events')
    if s['r_max_us']=='' or s['r_max_us']>10000:fail.append('response exceeds 10 ms or no valid response')
    for key in ['button_q_drop','btn_tx_drop','tel_q_drop','uart_tx_error','tx_timeout','drain_timeout','record_overflow','unrecorded_events','rx_error','control_drop','format_error','period_overrun']:
        if c[key]:fail.append(f'{key}={c[key]}')
    if c['tel_completed']!=c['tel_enqueued']:fail.append('TEL drain incomplete')
    target=m['work_target_us']
    if target and not target*.95<=m['work_mean_us']<=target*1.05:fail.append('CPU calibration outside 5%')
    if target and (not m['work_iters'] or not m['cpu_work_mean_us']):fail.append('CPU workload evidence missing')
    if m['work_mode']=='sliced' and m['cal_slice_max_us']>1100:fail.append('calibrated slice exceeds 1100 us')
    hz=s['telemetry_hz_actual'];expected=m['telemetry_hz']
    if expected and (hz=='' or abs(hz-expected)>expected*.01):fail.append('telemetry frequency outside 1%')
    build=meta.get('host_build',{})
    if not isinstance(build.get('elf_sha256'),str) or len(build['elf_sha256'])!=64:fail.append('ELF identity missing')
    if build.get('variant')!=m['variant'] or build.get('baud')!=m['baud']:fail.append('build/profile mismatch')
    bins=[0]*10
    if m['period_ms']==10 and m['tel_first_us'] is not None:
        for row in rows:bins[(elapsed(row['t0_us'],m['tel_first_us'])%10000)//1000]+=1
    s.update(acceptance_pass=not fail,failures='; '.join(fail),phase_bins=bins,
        phase_coverage_complete=all(bins) if m['period_ms']==10 else None,
        elf_sha256=build.get('elf_sha256',''),cal_work_mean_us=m['work_mean_us'],
        runtime_cpu_mean_us=m['cpu_work_mean_us'],runtime_cpu_max_us=m['cpu_work_max_us'],
        cal_slice_max_us=m['cal_slice_max_us'],slice_max_us=m['slice_max_us'],activation_wall_max_us=m['activation_wall_max_us'])
    return s


def report(input_path,output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    root=Path(input_path);folders=[root] if (root/'events.csv').exists() else sorted(p.parent for p in root.rglob('events.csv'))
    if not folders:raise ValueError('No real V2 runs found; no passing report generated')
    results=[];errors=[]
    for folder in folders:
        try:
            rows,meta=verified_load(folder);s=evaluate(rows,meta)
            s['folder']=str(folder);s['events_sha256']=hashlib.sha256((folder/'events.csv').read_bytes()).hexdigest();results.append(s)
            if meta['source']=='hardware':analyze([folder],output/meta['MET']['variant']/folder.name)
        except (ValueError,KeyError,OSError) as exc:errors.append({'folder':str(folder),'error':str(exc)})
    # Passing experiments with different binaries never collectively certify a release.
    final_sets=[]
    for identity in sorted({r['elf_sha256'] for r in results if r['variant']=='QWB' and r['elf_sha256']}):
        candidates=[r for r in results if r['variant']=='QWB' and r['elf_sha256']==identity]
        passed={r['scenario'] for r in candidates if r['acceptance_pass']}
        endurance=any(r['scenario']=='S5' and r['accepted']>=100 and r['acceptance_pass'] and r['phase_coverage_complete'] for r in candidates)
        final_sets.append({'elf_sha256':identity,'all_runs_pass':all(r['acceptance_pass'] for r in candidates),
            'scenarios_complete':passed=={f'S{i}' for i in range(6)},'s5_endurance_and_phase_complete':endurance})
    final_pass=bool(final_sets) and not errors and any(all(v for k,v in item.items() if k!='elf_sha256') for item in final_sets)
    audit={'hardware_acceptance_pass':final_pass,'runs':results,'invalid_inputs':errors,'release_sets':final_sets,
        'phase_note':'Nominal phase relative to first TEL activation; not a hardware-captured release trace.',
        'limit':'Finite observations, not a proven WCRT bound. Failed runs remain visible.'}
    (output/'audit.json').write_text(json.dumps(audit,indent=2,ensure_ascii=False),encoding='utf-8')
    if results:
        with (output/'comparison.csv').open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=list(results[0]));w.writeheader();w.writerows(results)
    lines=['# V2 hardware acceptance', '',f'Overall: **{"PASS" if final_pass else "NOT PASSED"}**','',
        '| Variant | Scenario | Accepted / OK | R max ms | d3 mean ms | Result |','|---|---|---:|---:|---:|---|']
    for r in results:
        maximum=r['r_max_us']/1000 if r['r_max_us']!='' else 'N/A';d3=r['d3_mean_us']/1000 if r['d3_mean_us']!='' else 'N/A'
        lines.append(f"| {r['variant']} | {r['scenario']} | {r['accepted']} / {r['ok']} | {maximum} | {d3} | {'PASS' if r['acceptance_pass'] else r['failures']} |")
    lines+=['','See audit.json for every run, build identity, phase coverage and invalid inputs.','Finite measurements do not prove a WCRT bound.']
    (output/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    return audit


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('input',type=Path);ap.add_argument('--output',type=Path,default=Path('analysis/v2'));args=ap.parse_args()
    result=report(args.input,args.output);print(json.dumps({'hardware_acceptance_pass':result['hardware_acceptance_pass'],'runs':len(result['runs']),'invalid_inputs':len(result['invalid_inputs'])}))
