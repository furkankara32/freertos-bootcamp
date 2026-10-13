"""Synthetic protocol fixtures only; these are not hardware results."""
import csv, hashlib, json, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from protocol import validate, statistics, fnv, MATRIX, COLUMNS
from capture import capture
from analyze import write_report, load_session
from record_files import replace_files, csv_bytes
ID='a'*64

def fixture(v='A',load='BURST',trace=True,rid=1,drops=0):
    data=b'fixture-only-not-a-real-svdat'
    accepted=24
    lines=['#HELLO,WEEK3,1,STM32F407VG,230400,168000000',f'#BUILD,{ID}',
           '#ACK,TRACE_ON' if trace else '#ACK,TRACE_OFF',f'#RUN,{rid},{v},{load}',
           f'#RESULT,{rid},{v},{load},44,{accepted},20,{accepted},{int(trace)},{len(data) if trace else 0},{drops if trace else 0}',
           '#COLUMNS,id,ok,received,generated_us,send_us,latency_us']
    for i in range(1,45):
        ok=int(i<=accepted);lines.append(f'#ROW,{i},{ok},{ok},{i*1000},{i},{i*10 if ok else 0}')
    lines+=['#STACK,100,100,200','#RX,0,0',f'#END,{rid}']
    if trace:lines += [f'#TRACE,{rid},{len(data)},{fnv(data):08X},{drops},1',f'#HEX,0,{data.hex()}',f'#TRACE_END,{rid}']
    return lines

class ProtocolTests(unittest.TestCase):
    def check(self,lines):return validate(lines,'A','BURST',True,ID)
    def test_valid(self):
        m,r,d=self.check(fixture());self.assertEqual(m['accepted'],24);self.assertTrue(m['valid'])
    def test_all_conditions(self):
        for v,l,t in MATRIX:self.assertTrue(validate(fixture(v,l,t),v,l,t,ID)[0]['valid'])
    def bad(self,old,new):
        lines=[s.replace(old,new) for s in fixture()]
        with self.assertRaises(ValueError):self.check(lines)
    def test_wrong_mcu(self):self.bad('STM32F407VG','STM32L476RG')
    def test_wrong_clock(self):self.bad('168000000','80000000')
    def test_wrong_build(self):self.bad(ID,'b'*64)
    def test_bad_ack(self):self.bad('#ACK,TRACE_ON','#ACK,TRACE_OFF')
    def test_counter_mismatch(self):self.bad(',44,24,20,24,',',44,24,19,24,')
    def test_not_drained(self):self.bad(',44,24,20,24,',',44,24,20,23,')
    def test_missing_row(self):
        with self.assertRaises(ValueError):self.check([s for s in fixture() if not s.startswith('#ROW,44,')])
    def test_duplicate_id(self):self.bad('#ROW,44,','#ROW,43,')
    def test_invalid_flag(self):self.bad('#ROW,1,1,1,','#ROW,1,2,1,')
    def test_negative_time(self):self.bad('#ROW,1,1,1,1000,1,10','#ROW,1,1,1,1000,-1,10')
    def test_uart_error(self):self.bad('#RX,0,0','#RX,1,0')
    def test_preexisting_uart_error_separate_from_run(self):
        lines=fixture();lines.extend(['#RX_BASE,1,0','#RX_TOTAL,1,0'])
        m,_,_=self.check(lines)
        self.assertTrue(m['valid']);self.assertEqual(m['rx_before_run'],[1,0])
    def test_run_uart_error_still_rejected(self):
        lines=[s.replace('#RX,0,0','#RX,1,0') for s in fixture()]
        lines.extend(['#RX_BASE,1,0','#RX_TOTAL,2,0'])
        with self.assertRaises(ValueError):self.check(lines)
    def test_rx_delta_mismatch_rejected(self):
        lines=fixture();lines.extend(['#RX_BASE,1,0','#RX_TOTAL,2,0'])
        with self.assertRaises(ValueError):self.check(lines)
    def test_missing_rx_total_rejected(self):
        lines=fixture();lines.append('#RX_BASE,1,0')
        with self.assertRaises(ValueError):self.check(lines)
    def test_stack_exhausted(self):self.bad('#STACK,100,100,200','#STACK,0,100,200')
    def test_end_wrong_run(self):self.bad('#END,1','#END,2')
    def test_trace_end_wrong_run(self):self.bad('#TRACE_END,1','#TRACE_END,2')
    def test_offset(self):self.bad('#HEX,0,','#HEX,1,')
    def test_checksum(self):
        lines=fixture();i=next(i for i,s in enumerate(lines) if s.startswith('#HEX'))
        lines[i]=lines[i][:-2]+'00'
        with self.assertRaises(ValueError):self.check(lines)
    def test_truncated_trace(self):
        with self.assertRaises(ValueError):self.check(fixture()[:-1])
    def test_drops_marked_invalid(self):self.assertFalse(self.check(fixture(drops=1))[0]['valid'])
    def test_duplicate_result(self):
        lines=fixture();lines.append(next(s for s in lines if s.startswith('#RESULT')))
        with self.assertRaises(ValueError):self.check(lines)
    def test_zero_failure_latency_excluded(self):
        _,rows,_=self.check(fixture());s=statistics(rows)
        self.assertEqual(s['generation_to_receive_us'],{'n':24,'mean':125.0,'max':240})
        self.assertEqual(s['send_failed_us']['n'],20)
    def test_empty_group(self):
        s=statistics([[1,0,0,1000,20,0]])
        self.assertIsNone(s['generation_to_receive_us']['mean'])
    def test_fnv_known(self):self.assertEqual(fnv(b'hello'),0x4f9f2cab)
    def serial_capture_fixture(self,startup_error='#ERROR,BAD_COMMAND',later_error=False,check_only=False):
        transcript=fixture()
        groups={'HELLO':transcript[:1],'BUILD':transcript[1:2],'TRACE ON':transcript[2:3],
                'RUN A BURST':transcript[3:-3],'TRACE':transcript[-3:]}
        class FakeSerial:
            def __init__(self,*a,**k):self.buf=bytearray()
            def __enter__(self):return self
            def __exit__(self,*a):pass
            def reset_input_buffer(self):pass
            def write(self,b):
                command=b.decode().strip()
                if command=='\x18\nHELLO':response=[startup_error]+groups['HELLO']
                elif command=='TRACE ON' and later_error:response=['#ERROR,BAD_COMMAND']
                else:response=groups[command]
                self.buf.extend(('\n'.join(response)+'\n').encode())
            def flush(self):pass
            @property
            def in_waiting(self):return min(len(self.buf),7)
            def read(self,n):result=self.buf[:n];del self.buf[:n];return result
        with tempfile.TemporaryDirectory() as tmp,patch('capture.verify_build',return_value={'build_id':ID}):
            path=capture('FAKE','A','BURST',tmp,serial_factory=FakeSerial,check_only=check_only)
            if check_only:
                self.assertFalse(json.loads(path.read_text())['scenario_started'])
                self.assertFalse(list(Path(tmp).glob('*.csv')))
                return
            with path.with_suffix('.csv').open(encoding='utf-8-sig') as f:rows=list(csv.DictReader(f,delimiter=';'))
            self.assertEqual(rows[-1]['generation_to_receive_us'],'')
            self.assertTrue(json.loads(path.read_text())['valid'])
            self.assertIn(startup_error,json.loads(path.read_text())['startup_lines'])
            self.assertNotIn('#ERROR',path.with_suffix('.txt').read_text())
            self.assertEqual(path.name,'A_BURST_trace1.json')
            self.assertTrue(path.with_suffix('.csv').read_bytes().startswith(b'\xef\xbb\xbf'))
            self.assertEqual(len(rows),44)
            self.assertEqual(list(rows[0]),COLUMNS)
            second=capture('FAKE','A','BURST',tmp,serial_factory=FakeSerial)
            self.assertEqual(second,path)
            self.assertEqual(len(list(Path(tmp).iterdir())),4)
            previous={p.name:p.read_bytes() for p in Path(tmp).iterdir()}
            with patch('capture.validate',side_effect=ValueError('Bad next run')):
                with self.assertRaises(ValueError):capture('FAKE','A','BURST',tmp,serial_factory=FakeSerial)
            for name,data in previous.items():self.assertEqual((Path(tmp)/name).read_bytes(),data)
            capture('FAKE','A','BURST',tmp,serial_factory=FakeSerial)
            self.assertEqual(len(list(Path(tmp).iterdir())),4)
    def test_fragmented_serial_capture(self):self.serial_capture_fixture()
    def test_stale_overlong_line_recovered(self):self.serial_capture_fixture('#ERROR,LINE_TOO_LONG')
    def test_unknown_startup_error_rejected(self):
        with self.assertRaises(ValueError):self.serial_capture_fixture('#ERROR,UNEXPECTED')
    def test_error_after_handshake_not_ignored(self):
        with self.assertRaises(ValueError):self.serial_capture_fixture(later_error=True)
    def test_check_only_does_not_start_run(self):self.serial_capture_fixture(check_only=True)
    def test_report_no_hardware(self):
        runs=[]
        for i,(v,l,t) in enumerate(MATRIX,1):
            m,r,_=validate(fixture(v,l,t,i),v,l,t,ID);m.update(statistics=statistics(r),file='TEST_FIXTURE');runs.append(m)
        with tempfile.TemporaryDirectory() as tmp:
            write_report(runs,tmp)
            with (Path(tmp)/'comparison.csv').open(encoding='utf-8-sig') as f:self.assertEqual(len(list(csv.DictReader(f,delimiter=';'))),7)
    def test_locked_file_restores_previous_bundle(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp);files={'run.txt':b'old raw','run.csv':b'old csv','run.json':b'old metadata'}
            replace_files(folder,files)
            original=Path.replace
            def locked(path,target):
                if path==folder/'run.csv':raise PermissionError('Excel lock')
                return original(path,target)
            with patch.object(Path,'replace',locked):
                with self.assertRaises(PermissionError):replace_files(folder,{k:b'new' for k in files})
            self.assertEqual({p.name:p.read_bytes() for p in folder.iterdir()},files)
    def test_excel_decimal_separator(self):
        self.assertEqual(csv_bytes(['mean','max'],[[12.5,19]]).decode('utf-8-sig'),'mean;max\r\n12,5;19\r\n')
    def test_incomplete_session_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp)/'session.json').write_text(json.dumps({'complete':False,'source':'hardware_serial'}))
            with self.assertRaises(ValueError):load_session(tmp)

    def session_fixture(self,folder):
        names=[]
        for i,(v,l,t) in enumerate(MATRIX,1):
            lines=fixture(v,l,t,i);m,rows,data=validate(lines,v,l,t,ID)
            path=Path(folder)/f'fixture-{i}.json';names.append(path.name)
            raw=path.with_suffix('.txt');raw.write_text('\n'.join(lines)+'\n')
            csvpath=path.with_suffix('.csv')
            with csvpath.open('w',newline='') as f:
                w=csv.writer(f);w.writerow(COLUMNS)
                for r in rows:w.writerow(r[:5]+[r[5] if r[2] else ''])
            if t:path.with_suffix('.SVDat').write_bytes(data)
            m.update(statistics=statistics(rows),local_build={'build_id':ID},
                     raw_sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),
                     csv_sha256=hashlib.sha256(csvpath.read_bytes()).hexdigest())
            path.write_text(json.dumps(m))
        (Path(folder)/'session.json').write_text(json.dumps({'complete':True,'source':'hardware_serial','runs':names}))
    def test_complete_session_pipeline(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.session_fixture(tmp);runs=load_session(tmp);self.assertEqual(len(runs),7)
            write_report(runs,Path(tmp)/'analysis')
    def test_changed_csv_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.session_fixture(tmp);(Path(tmp)/'fixture-1.csv').write_text('bad')
            with self.assertRaises(ValueError):load_session(tmp)
    def test_changed_trace_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.session_fixture(tmp);(Path(tmp)/'fixture-1.SVDat').write_bytes(b'bad')
            with self.assertRaises(ValueError):load_session(tmp)
    def test_changed_metadata_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.session_fixture(tmp);p=Path(tmp)/'fixture-1.json';m=json.loads(p.read_text());m['accepted']=30;p.write_text(json.dumps(m))
            with self.assertRaises(ValueError):load_session(tmp)

if __name__=='__main__':unittest.main()
