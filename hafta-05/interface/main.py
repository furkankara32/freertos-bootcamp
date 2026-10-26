"""Windows Week 5 laboratory. Run with Python or packaged EXE."""
import sys, json, threading, subprocess, os
if '--smoke-test' in sys.argv:os.environ['QT_QPA_PLATFORM']='offscreen'
from pathlib import Path
if not getattr(sys,'frozen',False):sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtCore import Qt,QTimer,Signal,QObject,QUrl
from PySide6.QtGui import QDesktopServices,QPainter,QColor,QPen
from PySide6.QtWidgets import QApplication,QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QGridLayout,QLabel,QPushButton,QComboBox,QSpinBox,QPlainTextEdit,QFileDialog,QMessageBox,QGroupBox
from serial.tools import list_ports
from host.protocol import *
from host.session import Session
from host.record_store import complete_capture
from tools.hardware import extract_trace

def root_path():
    anchor=Path(sys.executable if getattr(sys,'frozen',False) else __file__).resolve()
    for p in anchor.parents:
        if (p/'SPEC.md').exists():return p
    raise RuntimeError('Uygulamayı hafta-05 klasörü içinde tutun')
ROOT=root_path()
class Signals(QObject):
    frame=Signal(object);error=Signal(str);trace=Signal(object);capture_failed=Signal(str)
class Plot(QWidget):
    def __init__(self):super().__init__();self.values=[];self.setMinimumHeight(170)
    def paintEvent(self,event):
        p=QPainter(self);p.fillRect(self.rect(),QColor('#0e1728'));p.setPen(QColor('#bac6dc'));p.drawText(14,22,'LED geçiş gecikmesi (ms) • son 100 geçiş')
        values=self.values[-100:];maximum=max([15]+values);w=self.width()-40;h=self.height()-50
        p.setPen(QPen(QColor('#f6b55f'),1,Qt.PenStyle.DashLine));y=int(35+h*(1-10/maximum));p.drawLine(20,y,20+w,y)
        p.setPen(QPen(QColor('#50d6c3'),2))
        for i in range(1,len(values)):
            p.drawLine(int(20+(i-1)*w/max(1,len(values)-1)),int(35+h*(1-values[i-1]/maximum)),int(20+i*w/max(1,len(values)-1)),int(35+h*(1-values[i]/maximum)))
class Window(QMainWindow):
    def __init__(self):
        super().__init__();self.setWindowTitle('Hafta 5 • UART / LED / SystemView Laboratuvarı');self.resize(1100,800)
        self.sig=Signals();self.sig.frame.connect(self.received);self.sig.error.connect(self.error);self.sig.trace.connect(self.trace_done)
        self.sig.capture_failed.connect(self.capture_failed)
        self.session=Session(self.sig.frame.emit,self.sig.error.emit);self.last_folder=None;self.recording=False;self.count=0;self.stopping=False;self.trace_busy=False
        base=QWidget();self.setCentralWidget(base);layout=QVBoxLayout(base)
        title=QLabel('HAFTA 05  /  GERÇEK KART LABORATUVARI');title.setStyleSheet('font-size:24px;font-weight:700;color:#50d6c3');layout.addWidget(title)
        layout.addWidget(QLabel('TTL TX → PB11 (USART3 RX)   |   TTL RX ← PA2 (USART2 TX)   |   115200 baud   |   ST-LINK: RAM trace'))
        row=QHBoxLayout();layout.addLayout(row);self.ports=QComboBox();row.addWidget(self.ports);self.refresh()
        for text,fn in [('Portları yenile',self.refresh),('Bağlan',self.connect_port),('Bağlantıyı kapat',self.disconnect)]:b=QPushButton(text);b.clicked.connect(fn);row.addWidget(b)
        self.state=QLabel('Bağlı değil');row.addWidget(self.state)
        group=QGroupBox('Senaryo ve kayıt');grid=QGridLayout(group);layout.addWidget(group)
        self.scenario=QComboBox();self.scenario.addItems(['S1 • Doğru çalışan referans','S2 • Polling / öncelik','S3 • Uzun parser işi','S4 • Event / Queue birikmesi']);self.scenario.currentIndexChanged.connect(self.variants)
        self.variant=QComboBox();self.variants();self.period=QSpinBox();self.period.setRange(50,5000);self.period.setValue(1000);self.period.setSuffix(' ms / LED')
        self.cycles=QSpinBox();self.cycles.setRange(1,100);self.cycles.setValue(3);self.cycles.setSuffix(' tur')
        grid.addWidget(self.scenario,0,0);grid.addWidget(self.variant,0,1);grid.addWidget(self.period,0,2);grid.addWidget(self.cycles,0,3)
        buttons=[('Kaydı başlat',self.start),('Durdur ve kaydet',self.stop),('10 KB yük gönder',self.bulk),('Senaryo hatasını tetikle',self.trigger),('Durum oku',lambda:self.send(STATUS)),('Trace penceresi (1,5 s)',lambda:self.send(TRACE,[1500])),('ST-LINK trace çıkar',self.capture),('SystemView ile aç',self.open_trace)]
        for i,(text,fn) in enumerate(buttons):b=QPushButton(text);b.clicked.connect(fn);grid.addWidget(b,1+i//4,i%4)
        self.leds=[];row=QHBoxLayout();layout.addLayout(row)
        for name in COLORS[:4]:label=QLabel(name+'\n—');label.setAlignment(Qt.AlignmentFlag.AlignCenter);label.setMinimumHeight(65);row.addWidget(label);self.leds.append(label)
        self.metrics=QLabel('Henüz gerçek kart ölçümü yok.');layout.addWidget(self.metrics)
        self.plot=Plot();layout.addWidget(self.plot)
        self.log=QPlainTextEdit();self.log.setReadOnly(True);self.log.setMaximumBlockCount(2000);layout.addWidget(self.log)
        self.record_label=QLabel('Kayıt klasörü: —');layout.addWidget(self.record_label)
        history=QHBoxLayout();layout.addLayout(history)
        for text,fn in [('Kayıt seç',self.select_record),('Kayıt klasörünü aç',self.open_folder),('Kaydı iptal et',self.abort_record),('Firmware yükle (ST-LINK)',self.flash_board)]:
            b=QPushButton(text);b.clicked.connect(fn);history.addWidget(b)
        self.timer=QTimer(self);self.timer.timeout.connect(self.periodic);self.timer.start(2000)
        self.setStyleSheet('QWidget{background:#162238;color:#e7edf7;font-size:13px} QPushButton{background:#253b58;padding:9px;border-radius:4px} QPushButton:hover{background:#365878} QComboBox,QSpinBox{padding:7px;background:#20334d} QGroupBox{border:1px solid #36506b;margin-top:12px;padding-top:12px} QPlainTextEdit{background:#0e1728}')
    def refresh(self):self.ports.clear();[self.ports.addItem(p.device+' — '+p.description,p.device) for p in list_ports.comports()]
    def variants(self):
        self.variant.clear();options=[['Referans'],['Hata: yüksek öncelik + polling','Düzeltme: düşük öncelik + polling','Düzeltme: yüksek öncelik + kesme'],['Hata: kesintisiz iş','Düzeltme: parçalı iş'],['Hata: event başına tek komut','Düzeltme: Queue tüketimi']]
        self.variant.addItems(options[self.scenario.currentIndex()])
    def connect_port(self):
        if self.recording or self.trace_busy:self.error('Önce kayıt işlemini tamamlayın');return
        try:self.session.close();self.session=Session(self.sig.frame.emit,self.sig.error.emit);self.session.connect(self.ports.currentData());self.state.setText('Kimlik doğrulanıyor…')
        except Exception as exc:self.error(str(exc))
    def disconnect(self):
        if self.recording:self.error('Önce kaydı durdurun');return
        if self.trace_busy:return
        self.session.close();self.state.setText('Bağlı değil / LED durumu eski')
    def abort_record(self):
        if not self.recording or self.trace_busy:return
        folder=self.session.finish();self.session.close();self.recording=False;self.stopping=False
        manifest=json.loads((folder/'manifest.json').read_text(encoding='utf-8'));manifest['capture_status']='ABORTED'
        (folder/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
        for field in (self.scenario,self.variant,self.period,self.cycles):field.setEnabled(True)
        self.state.setText('Bağlantı kapalı');self.error('Koşu iptal edildi; önceki geçerli kayıt korundu. Kartın durduğu doğrulanmadı; yeniden çalıştırmadan önce kartı resetleyin.')
    def send(self,kind,values=()):
        if not self.session.identity:self.error('Önce gerçek karta bağlanın');return
        self.session.send(kind,values)
    def start(self):
        if self.trace_busy:self.error('Trace aktarımı sürüyor');return
        if self.recording:self.error('Önce mevcut koşuyu tamamlayın');return
        try:
            self.last_folder=self.session.begin(ROOT/'records',self.scenario.currentIndex()+1,self.variant.currentIndex(),self.period.value(),self.cycles.value());self.recording=True
            self.plot.values=[];self.record_label.setText(str(self.last_folder));self.log.appendPlainText('Kayıt başladı; trace ilk 1,5 saniyeyi hedefler. Taşarsa PARTIAL olarak işaretlenir.')
            self.start_seen=False
            for field in (self.scenario,self.variant,self.period,self.cycles):field.setEnabled(False)
            QTimer.singleShot(5000,self.start_timeout)
        except Exception as exc:self.error(str(exc))
    def start_timeout(self):
        if self.recording and not self.start_seen:self.error('RUN_START alınamadı; Durdur ve kaydet ile koşuyu sonlandırın.')
    def stop(self):
        if not self.recording or self.stopping:return
        self.stopping=True;self.send(STOP);self.send(STATUS);QTimer.singleShot(5000,self.stop_timeout)
    def stop_timeout(self):
        if self.stopping:self.stopping=False;self.error('STOP tamamlanma cevabı alınamadı; kayıt açık kaldı. Bağlantıyı kontrol edin.')
    def finish(self):
        if not self.recording:return
        self.last_folder=self.session.finish();self.recording=False;self.stopping=False;self.log.appendPlainText('UART kaydı kaydedildi; ST-LINK üzerinden trace çıkarılıyor.');self.capture()
        for field in (self.scenario,self.variant,self.period,self.cycles):field.setEnabled(True)
    def bulk(self):
        if not self.recording or self.stopping or not self.start_seen:return
        if self.session.identity:self.session.send_bulk();self.log.appendPlainText('10.000 bayt TX kuyruğuna eklendi; fiziksel teslim ayrıca ölçülür.')
    def trigger(self):
        if not self.recording or self.stopping or not self.start_seen:return
        s=self.scenario.currentIndex()+1
        if s==2:self.send(DIAG)
        elif s==3:self.send(WORK,[200])
        elif s==4:
            for _ in range(4):self.send(SEQUENCE,[0,0,0,self.period.value(),1])
        else:self.bulk()
    def periodic(self):
        if self.session.identity and not self.trace_busy:self.session.send(STATUS)
    def received(self,f):
        v=f.values
        if f.kind==RUN_START and self.recording and v[0]==self.session.run_id and not self.start_seen:
            self.start_seen=True;token=self.last_folder
            def planned_action():
                if self.recording and self.last_folder==token:self.trigger()
            QTimer.singleShot(max(0,self.period.value()-100) if self.scenario.currentIndex() in (1,2) else 150,planned_action)
        if f.kind==DONE and v[1]==0 and self.stopping and (v[0]==self.session.run_id or not self.start_seen):QTimer.singleShot(250,self.finish)
        if f.kind==MSG_HELLO:self.state.setText('STM32F407 • doğrulandı');self.log.appendPlainText('Kart kimliği alındı; gerçek bağlantı.')
        elif f.kind==LED:
            for i,label in enumerate(self.leds):label.setStyleSheet('background:'+('#247e6c' if i==v[3] else '#20334d')+';border-radius:6px')
            if v[2]<4:
                self.leds[v[2]].setText(f'{COLORS[v[2]]}\n{v[7]/1000:.2f} ms');self.plot.values.append(v[8]/1000);self.plot.update()
                a=self.plot.values;self.metrics.setText(f'{len(a)} geçiş | ortalama gecikme {sum(a)/len(a):.2f} ms | maksimum {max(a):.2f} ms | >10 ms: {sum(x>10 for x in a)}')
                self.log.appendPlainText(f'{COLORS[v[2]]} söndü: {v[7]/1000:.2f} ms açık; geçiş gecikmesi {v[8]/1000:.2f} ms')
            else:self.log.appendPlainText('LED dizisi başladı: Yeşil')
        elif f.kind==STATS:self.state.setText(f'RX {v[3]} B | kayıp {v[4]} | Queue {v[11]} | trace {v[12]} B / neden {v[15]}')
        elif f.kind!=DIAGNOSTIC:self.log.appendPlainText(f'{NAMES.get(f.kind,f.kind)}: {list(v[:4])}')
    def error(self,text):self.log.appendPlainText('HATA: '+text)
    def capture(self):
        if self.trace_busy:return
        if self.recording:self.error('Önce Durdur ve kaydet kullanın; ölçüm sırasında halt yapılmaz.');return
        if not self.last_folder:self.error('Önce bir koşu kaydedin');return
        if self.last_folder.parent.name!='.pending':self.error('Kaydedilmiş koşu yeniden yazılmaz; yeni koşu başlatın.');return
        folder=self.last_folder;self.trace_busy=True
        def work():
            try:self.sig.trace.emit((folder,extract_trace(folder/'systemview')))
            except Exception as exc:self.sig.capture_failed.emit(str(exc))
        threading.Thread(target=work,daemon=True).start()
    def capture_failed(self,text):
        self.trace_busy=False;self.error(text+' | Önceki geçerli senaryo kaydı korundu.')
    def trace_done(self,result):
        self.trace_busy=False
        folder,(path,meta)=result
        try:
            self.last_folder=complete_capture(folder,meta);self.record_label.setText(str(self.last_folder))
            self.log.appendPlainText(f'COMPLETE: {self.last_folder} | Bu senaryonun önceki kaydı değiştirildi.')
        except Exception as exc:self.capture_failed(str(exc))
    def select_record(self):
        if self.recording or self.trace_busy:return
        selected=QFileDialog.getExistingDirectory(self,'Koşu klasörü seç',str(ROOT/'records'))
        if selected:
            folder=Path(selected)
            if not (folder/'manifest.json').exists() and not (folder/'summary.json').exists():self.error('Geçerli koşu klasörü değil');return
            self.last_folder=folder;self.record_label.setText(str(folder))
            if (folder/'summary.json').exists():self.log.appendPlainText((folder/'summary.json').read_text())
    def open_folder(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.last_folder or ROOT/'records')))
    def flash_board(self):
        if self.recording or self.trace_busy:self.error('Önce kaydı tamamlayın');return
        from tools.hardware import flash
        self.trace_busy=True
        def work():
            try:flash();self.sig.error.emit('BİLGİ: Firmware yüklendi ve doğrulandı; yeniden bağlanın.')
            except Exception as exc:self.sig.error.emit(str(exc))
            finally:self.trace_busy=False
        self.session.close();threading.Thread(target=work,daemon=True).start()
    def open_trace(self):
        if not self.last_folder:return
        path=self.last_folder/'systemview/trace.SVDat'
        if not path.exists():self.error('Bu koşuda .SVDat yok');return
        settings=ROOT/'interface/settings.json';cfg=json.loads(settings.read_text()) if settings.exists() else {}
        exe=cfg.get('systemview','')
        if not Path(exe).is_file():
            exe,_=QFileDialog.getOpenFileName(self,'SystemView.exe seçin','','SystemView (SystemView.exe)')
            if not exe:return
            settings.write_text(json.dumps({'systemview':exe}),encoding='utf-8')
        subprocess.Popen([exe,str(path)])
    def closeEvent(self,event):
        if self.recording or self.trace_busy:
            self.error('Kapatmadan önce Durdur ve kaydet işlemini tamamlayın.');event.ignore();return
        self.session.close();event.accept()
if __name__=='__main__':
    app=QApplication(sys.argv);window=Window()
    if '--smoke-test' in sys.argv:
        from interface.smoke import run_smoke
        run_smoke(app,window,ROOT,sys.argv[sys.argv.index('--smoke-test')+1])
    else:window.show()
    sys.exit(app.exec())
