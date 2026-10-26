"""Exercise the packaged Qt event loop, serial callbacks and replacement flow."""
import json,time
from PySide6.QtCore import QTimer

def run_smoke(app,window,root,port):
    state={'stage':'connect','started':time.monotonic(),'runs':[]}
    timer=QTimer(window);timer.setInterval(100)
    def fail(exc):
        timer.stop();window.session.close()
        (root/'docs/interface-smoke.json').write_text(json.dumps({'passed':False,'error':str(exc),'log':window.log.toPlainText()},indent=2),encoding='utf-8')
        app.exit(1)
    def tick():
        try:
            if time.monotonic()-state['started']>90:raise TimeoutError(state['stage']+' | '+window.log.toPlainText())
            if state['stage']=='connect':
                index=window.ports.findData(port)
                if index<0:raise RuntimeError('Port missing: '+port)
                window.ports.setCurrentIndex(index);window.connect_port();state['stage']='identity'
            elif state['stage']=='identity' and window.session.identity:
                window.cycles.setValue(1);window.period.setValue(1000);window.start()
                assert window.recording
                assert not window.scenario.isEnabled()
                state['run_started']=time.monotonic();state['stage']='running'
            elif state['stage']=='running' and time.monotonic()-state['run_started']>4.5:
                assert window.start_seen,'No RUN_START acknowledgement'
                window.stop();state['stage']='saving'
            elif state['stage']=='saving' and not window.recording and not window.trace_busy:
                folder=window.last_folder
                assert folder==root/'records/S1',str(folder)
                manifest=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
                summary=json.loads((folder/'summary.json').read_text(encoding='utf-8'))
                assert manifest['capture_status']=='COMPLETE'
                assert summary['samples']==4 and summary['max_us']<10000,summary
                state['runs'].append(manifest['run_id'])
                if len(state['runs'])==1:
                    state['stage']='identity'
                else:
                    assert state['runs'][0]!=state['runs'][1]
                    assert len(list((root/'records').glob('S1')))==1
                    result={'passed':True,'runs':state['runs'],'replaced_previous':True,'summary':summary,'packaged_exe':True}
                    (root/'docs/interface-smoke.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
                    timer.stop();window.session.close();app.exit(0)
        except Exception as exc:fail(exc)
    timer.timeout.connect(tick);timer.start()
