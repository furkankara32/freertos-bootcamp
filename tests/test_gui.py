import os,time
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from PySide6.QtWidgets import QApplication
from interface.src.main import Window
from interface.src.simulator import Simulator
from interface.src.protocol import Protocol

def test_gui_demo_roundtrip_and_screenshot(tmp_path):
    app=QApplication.instance() or QApplication([]);w=Window(tmp_path);w.show();w.toggle_connection()
    def wait_for(predicate,timeout=3):
        end=time.monotonic()+timeout
        while time.monotonic()<end:
            app.processEvents();time.sleep(.01)
            if predicate():return
        assert predicate()
    try:
        wait_for(lambda:w.ready and w.pending is None)
        assert w.protocol_version=='PROTO3' and w.deadline_us==10000
        w.request('CFG','S0');wait_for(lambda:w.state=='CONFIGURED' and w.pending is None)
        w.request('START');wait_for(lambda:w.state=='ARMED',8)
        w.worker.send('!PRESS');wait_for(lambda:w.btn_count==1)
        w.request('STOP');wait_for(lambda:w.folder is not None,5)
        assert (w.folder/'events.csv').exists() and w.table.rowCount()==1
        assert 'v2' in w.folder.parts and 'QWB' in w.folder.parts
        assert 'SENTETİK' in w.source.text()
        app.processEvents();w.grab().save(str(tmp_path/'gui.png'))
    finally:w.close();app.processEvents()

def test_unsaved_run_blocks_new_start(tmp_path):
    app=QApplication.instance() or QApplication([]);w=Window(tmp_path)
    try:
        w.is_connected=True;w.ready=True
        w.receive('EXP',['EXP','9','DONE','S3'])
        w.receive('EXP',['EXP','9','CONFIGURED','S0'])
        assert w.unsaved_run and not w.start.isEnabled() and w.dump_btn.isEnabled()
        assert 'Önceki kaydı al' in w.message.text()
        assert w.dump_btn.text()=='Önceki kaydı al'
    finally:w.close();app.processEvents()

def test_configured_and_armed_explain_capture_flow(tmp_path):
    app=QApplication.instance() or QApplication([]);w=Window(tmp_path)
    try:
        w.is_connected=True;w.ready=True
        w.receive('EXP',['EXP','0','CONFIGURED','S0'])
        assert w.start.isEnabled() and 'Başlat' in w.message.text()
        w.receive('EXP',['EXP','1','ARMED','S0'])
        assert 'BTN sayacı canlı' in w.message.text()
        assert 'Durdur ve aktar' in w.message.text()
    finally:w.close();app.processEvents()

def test_reconnect_configured_preserves_previous_record(tmp_path):
    app=QApplication.instance() or QApplication([]);w=Window(tmp_path)
    try:
        w.is_connected=True;w.ready=True
        w.receive('EXP',['EXP','15','CONFIGURED','S3'])
        assert w.unsaved_run and not w.start.isEnabled()
        assert w.dump_btn.isEnabled() and 'Önceki kaydı al' in w.message.text()
    finally:w.close();app.processEvents()

def test_reconnect_can_stop_unknown_active_run(tmp_path):
    app=QApplication.instance() or QApplication([]);w=Window(tmp_path)
    try:
        w.is_connected=True;w.state='CONNECTED';w.pending=None;w.update_controls()
        assert w.stop_btn.isEnabled() and not w.start.isEnabled()
    finally:w.close();app.processEvents()


def test_gui_v1_handshake_keeps_old_deadline(tmp_path):
    app=QApplication.instance() or QApplication([]);w=Window(tmp_path)
    try:
        w.baud.setCurrentIndex(w.baud.findData(115200))
        w.receive('SYS',['SYS','RTOSLAT','FW03','PROTO2'])
        assert w.deadline_us==20000 and '115200' in w.source.text()
        assert '20 ms' in w.result_label.text()
        w.receive('SYS',['SYS','RTOSLAT','FW2-QWB','PROTO3'])
        assert w.deadline_us==10000
    finally:w.close();app.processEvents()
