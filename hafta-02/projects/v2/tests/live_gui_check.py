"""Read the retained hardware snapshot through the real Qt worker and UI.
Does not start/reset the MCU or discard its previous run.
"""
import os,sys,time
from pathlib import Path
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtWidgets import QApplication
from interface.src.main import Window

app=QApplication([]);window=Window('docs/review/live-gui');window.show()
index=window.ports.findData('COM5')
assert index>=0,'COM5 missing'
window.ports.setCurrentIndex(index);window.toggle_connection()
def wait(predicate,seconds=10):
    end=time.monotonic()+seconds
    while time.monotonic()<end:
        app.processEvents();time.sleep(.01)
        if predicate():return
    raise AssertionError(window.log.toPlainText())
try:
    wait(lambda:window.ready and window.pending is None)
    assert window.unsaved_run,'Retained hardware data must be recovered before a new run'
    window.request('DUMP');wait(lambda:window.folder is not None)
    assert window.table.rowCount()>=30
    assert not window.unsaved_run
    app.processEvents();window.grab().save('docs/review/ui-hardware.png')
    Path('docs/review/gui-hardware-test.log').write_text(f'PASS: COM5 HELLO + DUMP -> {window.table.rowCount()} rows, CRC validation, CSV saved, UI rendered.\n{window.folder}\n',encoding='utf-8')
    print('PASS: hardware GUI recovery, CSV export and screenshot')
finally:window.close();app.processEvents()
