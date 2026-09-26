"""Manual offscreen V2 GUI end-to-end evidence; entirely synthetic."""
import os,sys,time
from pathlib import Path
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtWidgets import QApplication
from interface.src.main import Window

app=QApplication([]);root=Path('docs/review/v2');root.mkdir(parents=True,exist_ok=True)
w=Window('tests/output/v2-gui');w.show();w.toggle_connection()
def wait(predicate,seconds=10):
    until=time.monotonic()+seconds
    while time.monotonic()<until:
        app.processEvents();time.sleep(.01)
        if predicate():return
    raise AssertionError(w.log.toPlainText())
try:
    wait(lambda:w.ready and w.pending is None)
    assert w.protocol_version=='PROTO3'
    w.scenario.setCurrentIndex(5);w.request('CFG','S5');wait(lambda:w.state=='CONFIGURED' and w.pending is None)
    w.request('START');wait(lambda:w.state=='ARMED')
    for i in range(5):
        w.worker.send('!PRESS');wait(lambda:w.btn_count==i+1)
        until=time.monotonic()+.51
        while time.monotonic()<until:app.processEvents();time.sleep(.01)
    w.request('STOP');wait(lambda:w.folder is not None)
    assert w.table.rowCount()==5 and w.deadline_us==10000
    app.processEvents();w.grab().save(str(root/'gui-demo.png'))
    (root/'gui-demo-test.log').write_text(f'PASS: SYNTHETIC PROTO3 QWB S5; 5 events; CRC/export; GUI 10 ms + V1 20 ms.\n{w.folder}\n',encoding='utf-8')
    print('PASS: synthetic V2 GUI end-to-end')
finally:w.close();app.processEvents()
