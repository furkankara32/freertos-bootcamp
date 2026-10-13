import hashlib
import json
import os
import sys
import time
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import pytest
from PySide6.QtCore import QProcess
from PySide6.QtWidgets import QApplication
from interface.src.main import Window
from interface.src import systemview as sv


@pytest.fixture
def gui(tmp_path, monkeypatch):
    app = QApplication.instance() or QApplication([])
    w = Window(tmp_path / 'measurements')
    sent = []
    w.worker = SimpleNamespace(send=sent.append, isRunning=lambda: False)
    w.connection_id = 'test-connection'
    w.ports.addItem('TEST COM', 'TEST_COM')
    w.ports.setCurrentIndex(w.ports.count()-1)
    w.is_connected = w.ready = True
    w.demo = False
    w.baud.setCurrentIndex(w.baud.findData(115200))
    w.receive('SYS', ['SYS', 'RTOSLAT', 'FW03', 'PROTO2'])
    w.receive('EXP', ['EXP', '8', 'ARMED', 'S5'])
    elf = tmp_path / 'firmware' / 'test.elf'
    elf.parent.mkdir()
    elf.write_bytes(b'test-only ELF fixture')
    build = {'variant': 'V1', 'design_version': 1, 'protocol': 'PROTO2', 'baud': 115200,
             'trace_backend': 'systemview', 'elf_sha256': hashlib.sha256(elf.read_bytes()).hexdigest()}
    elf.with_name('build.json').write_text(json.dumps(build))
    w.systemview.elf = elf
    w.systemview.countdown_seconds = 0
    week = tmp_path / 'week'
    helper = week / 'tools/export_systemview.py'
    helper.parent.mkdir(parents=True)
    helper.write_text('''import argparse,hashlib,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--elf');p.add_argument('--output');a=p.parse_args()
f=Path(a.output);d=b'TEST FIXTURE ONLY - not a hardware recording'
(f/'recording.SVDat').write_bytes(d)
(f/'trace.json').write_text(json.dumps(dict(clean=True,capture_complete=True,dropped_events=0,bytes=len(d),capacity=65536,trace_sha256=hashlib.sha256(d).hexdigest())))
''')
    runtime = week / 'projects/v2/interface/.venv/Scripts/python.exe'
    runtime.parent.mkdir(parents=True)
    runtime.touch()
    monkeypatch.setattr(sv, 'WEEK', week)
    class TestProcess(QProcess):
        def setProgram(self, program):
            super().setProgram(sys.executable)
    monkeypatch.setattr(sv, 'QProcess', TestProcess)
    yield app, w, sent, helper
    w.systemview.timer.stop()
    if w.systemview.process and w.systemview.process.state() != QProcess.ProcessState.NotRunning:
        w.systemview.process.kill(); w.systemview.process.waitForFinished(2000)
    w.systemview.finish(); w.close(); app.processEvents()


def wait(app, predicate):
    end = time.monotonic() + 8
    while time.monotonic() < end and not predicate():
        app.processEvents(); time.sleep(.01)
    assert predicate()


def test_record_uses_existing_uart_and_actual_scenario(gui, tmp_path):
    app,w,sent,_ = gui
    panel = w.systemview
    w.scenario.setCurrentIndex(0)  # Should never relabel the running S5 as S0.
    panel.start()
    assert panel.busy and len(sent) == 1 and sent[0].startswith('TRACE,')
    assert not w.stop_btn.isEnabled() and not w.connect_btn.isEnabled()
    assert not panel.timer.isActive()  # Wait until SerialWorker confirms the write.
    panel.command_sent(sent[0])
    assert panel.timer.isActive()
    wait(app, lambda: not panel.busy)
    trace = Path(panel.files.currentData())
    assert trace.exists() and 'S5' in trace.parts
    record = json.loads((trace.parent/'session.json').read_text(encoding='utf-8'))
    assert record['run'] == 8 and record['status'] == 'complete'
    assert w.state == 'ARMED' and w.stop_btn.isEnabled()
    assert panel.open.isEnabled() and panel.record.isEnabled()
    panel.on_receive('SAVED', (SimpleNamespace(run=8), str(tmp_path/'measurement')))
    record = json.loads((trace.parent/'session.json').read_text(encoding='utf-8'))
    assert record['measurement_folder'] == str(tmp_path/'measurement')
    w.resize(1440,1050);w.show();app.processEvents()
    w.grab().save(str(tmp_path/'systemview-gui.png'))


def test_no_fake_hardware_recording_in_demo_or_before_armed(gui):
    _,w,sent,_=gui
    w.demo=True;w.systemview.start()
    assert not sent
    w.demo=False;w.state='CONFIGURED';w.systemview.start()
    assert not sent


def test_wrong_elf_rejected_before_trace_command(gui):
    _,w,sent,_=gui
    w.systemview.elf.write_bytes(b'changed ELF')
    w.systemview.start()
    assert not sent and not w.systemview.busy
    assert 'SHA256' in w.systemview.status.text()


def test_uart_rejection_and_disconnect_release_lock(gui):
    _,w,sent,_=gui
    w.systemview.start()
    w.receive('ERR',['ERR','0','BAD_TRACE'])
    assert not w.systemview.busy and w.systemview.files.count()==0
    w.systemview.start();w.connection_changed(False)
    assert not w.systemview.busy and not w.systemview.record.isEnabled()


def test_export_failure_not_offered_as_valid_record(gui):
    app,w,sent,helper=gui
    helper.write_text('raise SystemExit(2)')
    w.systemview.start();w.systemview.command_sent(sent[-1])
    wait(app,lambda:not w.systemview.busy)
    assert w.systemview.files.count()==0 and not w.systemview.open.isEnabled()
    assert json.loads((w.systemview.folder/'session.json').read_text(encoding='utf-8'))['status']=='failed'


def test_overflow_or_corrupt_file_is_rejected(tmp_path):
    data=b'test trace';(tmp_path/'recording.SVDat').write_bytes(data)
    info=dict(clean=False,capture_complete=True,dropped_events=1,bytes=len(data),capacity=65536,trace_sha256=hashlib.sha256(data).hexdigest())
    p=tmp_path/'trace.json';p.write_text(json.dumps(info))
    with pytest.raises(ValueError,match='kaybı'):sv.validate_recording(tmp_path)
    info.update(clean=True,dropped_events=0,trace_sha256='0'*64);p.write_text(json.dumps(info))
    with pytest.raises(ValueError,match='SHA256'):sv.validate_recording(tmp_path)


def test_close_while_recording_waits_for_file(gui):
    app,w,sent,_=gui
    w.show();w.systemview.start();app.processEvents()
    assert not w.close() and w.systemview.busy
    w.systemview.fail('test cleanup')


def test_countdown_precedes_uart_command(gui):
    _,w,sent,_=gui
    w.systemview.countdown_seconds=3
    w.systemview.start()
    assert not sent and w.systemview.busy
    w.systemview.countdown_tick();w.systemview.countdown_tick()
    assert not sent
    w.systemview.countdown_tick()
    assert len(sent)==1 and sent[0].startswith('TRACE,')


def test_cubeide_elf_without_metadata_checks_symbols(tmp_path,monkeypatch):
    elf=tmp_path/'Homework_001.elf';elf.write_bytes(b'ELF test fixture')
    symbols={'_SEGGER_RTT','app_trace_capture_complete','app_trace_bytes','app_trace_dropped','AppTrace_Start'}
    monkeypatch.setattr(sv,'elf_symbols',lambda path:symbols)
    build=sv.validate_build(elf,'PROTO2',115200)
    assert build['build_metadata_available'] is False and build['variant']=='V1'
    assert build['elf_sha256']==hashlib.sha256(elf.read_bytes()).hexdigest()
    symbols.remove('AppTrace_Start')
    with pytest.raises(ValueError,match='APP_TRACE=1'):sv.validate_build(elf,'PROTO2',115200)


def test_explicit_elf_survives_handshake(gui):
    _,w,_,_=gui
    selected=w.systemview.elf
    w.systemview.explicit_elf=True;w.systemview.protocol=None
    w.receive('SYS',['SYS','RTOSLAT','FW03','PROTO2'])
    assert w.systemview.elf==selected


def test_warmup_cannot_record_and_defaults_follow_actual_scenario(gui):
    _,w,sent,_=gui
    w.receive('EXP',['EXP','8','WARMUP','S0'])
    assert w.systemview.duration.value()==1000
    w.systemview.start();assert not sent
    w.receive('EXP',['EXP','8','ARMED','S5'])
    assert w.systemview.duration.value()==500
    assert w.systemview.duration.minimum()==50 and w.systemview.duration.maximum()==2000


def test_recording_display_ends_before_export_settle(gui):
    _,w,sent,_=gui
    w.systemview.start();w.systemview.command_sent(sent[-1])
    assert w.systemview.timer.interval()==500
    w.systemview.recording_ended()
    assert 'KAYIT AÇIK' not in w.systemview.status.text()
    assert w.systemview.settle_timer.interval()==350


def test_capture_preserves_elf_if_cubeide_rebuilds(gui):
    _,w,_,_=gui
    original=w.systemview.elf.read_bytes()
    w.systemview.start()
    w.systemview.elf.write_bytes(b'rebuilt')
    assert w.systemview.capture_elf.read_bytes()==original
    assert hashlib.sha256(original).hexdigest()==w.systemview.manifest['build']['elf_sha256']


def test_bad_metadata_is_readable_error(gui):
    _,w,sent,_=gui
    w.systemview.elf.with_name('build.json').write_text('[]')
    w.systemview.start()
    assert not sent and 'JSON' in w.systemview.status.text()


def test_measurement_manifest_write_error_does_not_crash(gui,monkeypatch):
    _,w,_,_=gui
    w.systemview.records=[{'run':8,'connection':w.connection_id}]
    def denied(record):raise OSError('disk read-only')
    monkeypatch.setattr(w.systemview,'write_manifest',denied)
    w.systemview.on_receive('SAVED',(SimpleNamespace(run=8),'measurement'))
    assert 'yazılamadı' in w.systemview.status.text()
