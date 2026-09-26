import argparse,json,sys,time
from pathlib import Path
from PySide6.QtCore import QSettings,QTimer,Qt,QUrl
from PySide6.QtGui import QDesktopServices,QFontDatabase
from PySide6.QtWidgets import (QApplication,QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,QComboBox,QGroupBox,QTableWidget,QTableWidgetItem,QHeaderView,QPlainTextEdit,QFileDialog,QSplitter)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib
from serial.tools import list_ports
from .serial_worker import SerialWorker
from .protocol import stages

ROOT=Path(__file__).resolve().parents[2] if not getattr(sys,'frozen',False) else Path(sys.executable).resolve().parent
PROJECT=ROOT

class Window(QMainWindow):
    def __init__(self,output=None):
        super().__init__();self.setWindowTitle('FreeRTOS Bootcamp • Hafta 01');self.resize(1240,850)
        # Bundle a known Unicode font; the offscreen Windows Qt platform otherwise
        # renders boxes when it cannot discover the native system font directory.
        QFontDatabase.addApplicationFont(str(Path(matplotlib.get_data_path())/'fonts/ttf/DejaVuSans.ttf'))
        self.settings=QSettings('FreeRTOSBootcamp','Hafta01');self.worker=None;self.state='DISCONNECTED';self.pending=None
        self.folder=None;self.btn_count=0;self.tel_count=0;self.current_run=None;self.demo=False;self.is_connected=False;self.ready=False
        self.unsaved_run=False;self.saved_run_id=None;self.deadline_us=10000;self.protocol_version=None;self.build_metadata=None
        self.output=Path(output or PROJECT/'measurements');self.last_traffic=time.monotonic();self.started_at=0
        root=QWidget();self.setCentralWidget(root);layout=QVBoxLayout(root);layout.setContentsMargins(24,20,24,20);layout.setSpacing(12)
        title=QLabel('FreeRTOS  /  Yanıt süresi laboratuvarı');title.setObjectName('title');layout.addWidget(title)
        self.source=QLabel('Kart bağlantısı bekleniyor • STM32F407 • Baud seçip bağlanın');layout.addWidget(self.source)
        row=QHBoxLayout();layout.addLayout(row)
        self.ports=QComboBox();self.baud=QComboBox();self.baud.addItem('460800 · V2',460800);self.baud.addItem('115200 · V1 / Q / QW',115200);self.refresh=QPushButton('Portları yenile');self.connect_btn=QPushButton('Bağlan');self.path_btn=QPushButton('Kayıt konumu');self.open_btn=QPushButton('Son kaydı aç')
        for w in [self.ports,self.baud,self.refresh,self.connect_btn,self.path_btn,self.open_btn]:row.addWidget(w)
        self.refresh.clicked.connect(self.refresh_ports);self.connect_btn.clicked.connect(self.toggle_connection);self.path_btn.clicked.connect(self.choose_path);self.open_btn.clicked.connect(self.open_folder)
        row=QHBoxLayout();layout.addLayout(row);box=QGroupBox('Deney kontrolü');controls=QHBoxLayout(box);row.addWidget(box)
        self.scenario=QComboBox();self.scenario.addItems(['S0 · Telemetri kapalı','S1 · 10 Hz','S2 · 50 Hz','S3 · 100 Hz','S4 · 100 Hz + 2 ms','S5 · 100 Hz + 5 ms'])
        self.cfg=QPushButton('Senaryoyu uygula');self.start=QPushButton('Başlat');self.stop_btn=QPushButton('Durdur ve aktar');self.dump_btn=QPushButton('Kaydı tekrar al');self.press=QPushButton('Demo: butona bas')
        for w in [self.scenario,self.cfg,self.start,self.stop_btn,self.dump_btn,self.press]:controls.addWidget(w)
        self.cfg.clicked.connect(lambda:self.request('CFG',f'S{self.scenario.currentIndex()}'));self.start.clicked.connect(lambda:self.request('START'));self.stop_btn.clicked.connect(lambda:self.request('STOP'));self.dump_btn.clicked.connect(lambda:self.request('DUMP'));self.press.clicked.connect(lambda:self.worker.send('!PRESS') if self.worker else None)
        cards=QHBoxLayout();layout.addLayout(cards)
        self.status_label=QLabel('BAĞLI DEĞİL');self.count_label=QLabel('Alınan BTN: 0');self.tel_label=QLabel('Alınan TEL: 0');self.result_label=QLabel('Hedef: 10 ms')
        for w in [self.status_label,self.count_label,self.tel_label,self.result_label]:w.setObjectName('card');cards.addWidget(w)
        self.message=QLabel('Port seçip bağlanın. Donanım yoksa SENTETİK DEMO seçeneğini kullanabilirsiniz.');self.message.setWordWrap(True);layout.addWidget(self.message)
        splitter=QSplitter(Qt.Orientation.Horizontal);layout.addWidget(splitter,1)
        self.figure=Figure(figsize=(7,4),facecolor='#101d2d');self.canvas=FigureCanvasQTAgg(self.figure);self.axes=self.figure.add_subplot(111);splitter.addWidget(self.canvas)
        self.table=QTableWidget(0,7);self.table.setHorizontalHeaderLabels(['Olay','Durum','d1 ms','d2 ms','d3 ms','d4 ms','R ms']);self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch);splitter.addWidget(self.table);splitter.setSizes([650,500])
        self.draw([])
        self.log=QPlainTextEdit();self.log.setReadOnly(True);self.log.setMaximumBlockCount(200);self.log.setMaximumHeight(125);layout.addWidget(self.log)
        self.build_btn=QPushButton('Yüklenen firmware build.json seç');self.build_btn.clicked.connect(self.choose_build);layout.addWidget(self.build_btn)
        self.location=QLabel(f'Kayıt: {self.output}');self.location.setWordWrap(True);layout.addWidget(self.location)
        self.refresh_ports();self.update_controls();self.timer=QTimer(self);self.timer.timeout.connect(self.tick);self.timer.start(100)
        self.setStyleSheet('''QMainWindow,QWidget{background:#0a1422;color:#e5edf7;font-family:"DejaVu Sans";font-size:13px} QLabel#title{font-size:26px;font-weight:600} QLabel#card{background:#172a3f;border:1px solid #29435e;border-radius:8px;padding:16px;font-size:17px} QPushButton{background:#1b3951;border:1px solid #34536a;border-radius:5px;padding:9px 14px} QPushButton:hover{background:#25506b} QPushButton:disabled{color:#65788b;background:#152334} QComboBox{background:#172a3f;padding:8px;border:1px solid #34536a} QGroupBox{border:1px solid #29435e;border-radius:6px;margin-top:12px;padding-top:12px} QGroupBox::title{subcontrol-origin:margin;left:12px} QTableWidget,QPlainTextEdit{background:#101d2d;gridline-color:#29435e;border:1px solid #29435e} QHeaderView::section{background:#172a3f;padding:6px;border:0}''')
    def refresh_ports(self):
        self.ports.clear();self.ports.addItem('SENTETİK DEMO — donanım gerekmez','DEMO')
        for port in list_ports.comports():self.ports.addItem(f'{port.device} · {port.description}',port.device)
    def choose_path(self):
        path=QFileDialog.getExistingDirectory(self,'Ölçüm kayıt konumu',str(self.output))
        if path:self.output=Path(path);self.location.setText(f'Kayıt: {path}')
    def choose_build(self):
        path,_=QFileDialog.getOpenFileName(self,'Karta yüklediğiniz build.json dosyası',str(PROJECT/'firmware/build'),'JSON (*.json)')
        if path:self.load_build(path)
    def load_build(self,path):
        try:
            data=json.loads(Path(path).read_text(encoding='utf-8'))
            if not isinstance(data.get('elf_sha256'),str) or len(data['elf_sha256'])!=64:raise ValueError('ELF SHA256 eksik')
            self.build_metadata=data;self.build_btn.setText(f"Firmware kimliği: {data.get('variant','V1')} / {data['elf_sha256'][:12]} (seçilen build)")
        except (OSError,ValueError,TypeError) as exc:self.problem(str(exc))
    def open_folder(self):
        if self.folder:QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.folder)))
    def toggle_connection(self):
        if self.worker and self.worker.isRunning():self.worker.stop();return
        self.pending=None;self.ready=False;self.saved_run_id=None;self.demo=self.ports.currentData()=='DEMO';self.btn_count=self.tel_count=0;self.current_run=None
        self.worker=SerialWorker(self.ports.currentData(),self.output,self,baud=self.baud.currentData(),build_metadata=self.build_metadata);self.worker.received.connect(self.receive);self.worker.problem.connect(self.problem);self.worker.connected.connect(self.connection_changed);self.worker.start()
    def connection_changed(self,yes):
        self.is_connected=yes;self.connect_btn.setText('Bağlantıyı kes' if yes else 'Bağlan')
        self.state='CONNECTED' if yes else 'DISCONNECTED'
        self.source.setText('SENTETİK DEMO • Bu veriler gerçek kart ölçümü değildir' if self.demo else 'GERÇEK DONANIM • STM32F407 • Baud seçip bağlanın')
        if yes:self.worker.send('HELLO,0');self.pending=(0,'HELLO',time.monotonic(),False)
        else:self.pending=None;self.ready=False
        self.update_controls()
    def request(self,cmd,arg=None):
        if not self.worker or self.pending:return
        key='request/'+str(self.ports.currentData());req=int(self.settings.value(key,0))+1
        if req>65535:self.problem('İstek kimliği sınırı: RAM kaydını kurtarıp cihaz oturumunu yenileyin.');return
        self.settings.setValue(key,req);self.settings.sync()
        text=f'{cmd},{req}'+(f',{arg}' if arg is not None else '')
        self.pending=(req,cmd,time.monotonic(),False);self.worker.send(text);self.log.appendPlainText('→ '+text);self.update_controls()
    def problem(self,text):self.log.appendPlainText('HATA: '+text);self.message.setText(text)
    def receive(self,kind,data):
        self.last_traffic=time.monotonic()
        if kind=='SYS':
            self.ready=True;self.protocol_version=data[3];self.deadline_us=10000 if data[3]=='PROTO3' else 20000
            label='SENTETİK DEMO' if self.demo else 'GERÇEK DONANIM'
            self.source.setText(f'{label} • STM32F407 • {self.baud.currentData()} baud • {data[2]} • {data[3]}')
            self.result_label.setText(f'Deadline: {self.deadline_us/1000:g} ms');self.draw([])
        if kind=='TEL':
            if self.current_run is None or str(self.current_run)==data[1]:self.tel_count+=1
            return
        if kind=='BTN':
            if self.current_run is None or str(self.current_run)==data[1]:
                self.btn_count+=1;self.message.setText(f'Butona basıldı — Olay {data[3]} — {data[2]}')
            return
        if kind not in {'M1','M2','MET','SUM'}:self.log.appendPlainText(kind+' '+(str(data) if kind not in {'BEGIN','SAVED'} else ''))
        if kind=='ACK' and self.pending and int(data[1])==self.pending[0]:
            self.pending=(*self.pending[:3],True)
            if data[2] in {'STOP','DUMP'}:self.state='DUMPING';self.pending=(self.pending[0],self.pending[1],time.monotonic(),True)
        elif kind=='ERR':
            self.problem('MCU komut hatası: '+','.join(data[1:]));self.pending=None
        elif kind=='EXP':
            self.state=data[2]
            if self.state=='IDLE':self.unsaved_run=False
            if self.state in {'WARMUP','ARMED'}:
                if self.current_run!=int(data[1]):self.btn_count=self.tel_count=0
                self.current_run=int(data[1])
                self.unsaved_run=True
            elif self.state in {'DONE','INCOMPLETE','CANCELLED','CONFIGURED'} and int(data[1])>0 and int(data[1])!=self.saved_run_id:
                self.unsaved_run=True
            if self.state=='WARMUP':self.started_at=time.monotonic();self.message.setText('5 saniye ısınma ve TX boşaltma bekleniyor…')
            elif self.state=='ARMED':self.message.setText('Ölçüm hazır: kartın USER butonuna basın. BTN sayacı canlı artar; grafik ve tablo Durdur ve aktar sonrası oluşur. En az 30 basış, aralık ≥0,5 s.');self.started_at=0
            if self.pending and self.pending[3] and self.pending[1] in {'HELLO','CFG','START'}:self.pending=None
        elif kind=='SAVED':
            dump,folder=data;self.deadline_us=dump.metadata.get('deadline_us',20000);self.folder=Path(folder);self.pending=None;self.state='DONE';self.unsaved_run=False;self.saved_run_id=dump.run
            self.table.setRowCount(len(dump.rows))
            for i,row in enumerate(dump.rows):
                calc=stages(row);values=[row['event_id'],row['status']]+([f'{calc[k]/1000:.3f}' for k in ['d1_us','d2_us','d3_us','d4_us','r_us']] if calc else ['—']*5)
                for j,v in enumerate(values):self.table.setItem(i,j,QTableWidgetItem(str(v)))
            self.draw(dump.rows)
            values=[stages(r)['r_us'] for r in dump.rows if r['status']=='ok']
            text=f'Kabul: {dump.counters["accepted"]} • başarılı: {len(values)} • geç: {dump.counters.get("late_10ms",dump.counters.get("late_completed",0))}'
            if values:text+=f' • ort: {sum(values)/len(values)/1000:.3f} ms • maks: {max(values)/1000:.3f} ms'
            self.message.setText(text+'\nCSV + metadata + ham akış kaydedildi: '+folder)
            self.result_label.setText(f'Kabul / başarı: {dump.counters["accepted"]} / {len(values)}')
        self.update_controls()
    def draw(self,rows):
        ax=self.axes;ax.clear();ax.set_facecolor('#101d2d');ax.tick_params(colors='#bbcbdc');ax.spines[['top','right']].set_visible(False)
        for spine in ax.spines.values():spine.set_color('#34536a')
        ok=[(r['event_id'],stages(r)['r_us']/1000) for r in rows if r['status']=='ok']
        if ok:ax.plot(*zip(*ok),marker='o',markersize=4,color='#52e0bd',label='R = t4 − t0')
        failed=[r['event_id'] for r in rows if r['status']!='ok']
        if failed:ax.scatter(failed,[-1]*len(failed),marker='x',color='#ffbb66',label='Başarısız (R yok)')
        ax.axhline(self.deadline_us/1000,color='#ff8e99',linestyle='--',label=f'Deadline: {self.deadline_us/1000:g} ms')
        if self.deadline_us==10000:ax.axhline(20,color='#a5aab5',linestyle=':',label='V1 sınırı: 20 ms')
        ax.set_ylim(bottom=-2 if failed else 0,top=max(24,max((v for _,v in ok),default=0)*1.2))
        ax.set_xlabel('Olay kimliği',color='#bbcbdc');ax.set_ylabel('MCU yanıt süresi [ms]',color='#bbcbdc');ax.grid(alpha=.12);ax.legend(facecolor='#172a3f',labelcolor='#e5edf7',fontsize=9)
        self.figure.tight_layout();self.canvas.draw_idle()
    def update_controls(self):
        busy=self.pending is not None;calm=self.state in {'IDLE','CONFIGURED','DONE','INCOMPLETE','CANCELLED'}
        self.cfg.setEnabled(self.is_connected and self.ready and calm and not busy);self.start.setEnabled(self.is_connected and self.state=='CONFIGURED' and not busy and not self.unsaved_run)
        # HELLO is deliberately deferred during RUN, so a reconnected host may
        # not know the state. A user-requested STOP must remain available then.
        self.stop_btn.setEnabled(self.is_connected and self.state in {'CONNECTED','WARMUP','ARMED'} and not busy)
        self.dump_btn.setEnabled(self.is_connected and calm and not busy);self.press.setEnabled(self.demo and self.state=='ARMED')
        self.dump_btn.setText('Önceki kaydı al' if self.unsaved_run and calm else 'Kaydı tekrar al')
        if self.is_connected and calm and not busy:
            if self.unsaved_run:
                self.message.setText('Kartta önceki deneyin kaydı var. Başlat kilidini açmak için Önceki kaydı al düğmesine basın; kayıt bilgisayara aktarılır. Ardından senaryoyu uygulayıp Başlat seçin. Henüz yeni ölçüm başlamadı.')
            elif self.state=='CONFIGURED':
                self.message.setText('Senaryo hazır. Başlat düğmesine basın ve 5 saniye sonra ARMED durumunu bekleyin. Basışlar BTN sayacında canlı görünür; grafik ve tablo Durdur ve aktar sonrası oluşur.')
            elif self.state=='IDLE':
                self.message.setText('Bağlantı hazır. Senaryo seçin → Senaryoyu uygula → Başlat → 5 saniye bekleyin → kartın USER butonuna basın → Durdur ve aktar.')
        self.build_btn.setEnabled(not self.is_connected);self.baud.setEnabled(not self.is_connected);self.ports.setEnabled(not self.is_connected);self.refresh.setEnabled(not self.is_connected);self.path_btn.setEnabled(not self.is_connected);self.open_btn.setEnabled(self.folder is not None)
        self.status_label.setText(self.state)
    def tick(self):
        self.count_label.setText(f'Alınan BTN: {self.btn_count}');self.tel_label.setText(f'Alınan TEL: {self.tel_count}')
        if self.pending:
            _,cmd,start,ack=self.pending;limit=15 if cmd in {'STOP','DUMP'} and ack else 3 if cmd=='STOP' else 2
            if time.monotonic()-start>limit:
                self.pending=None;self.problem(f'{cmd} yanıt zaman aşımı. COM, TX/RX/GND ve baud seçimini kontrol edin (V1: 115200, V2 QWB: 460800). Yeni START gönderilmedi.');self.update_controls()
    def closeEvent(self,event):
        if self.worker and self.worker.isRunning():self.worker.stop();self.worker.wait(2500)
        event.accept()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output');ap.add_argument('--build');ap.add_argument('--demo',action='store_true');ap.add_argument('--port');ap.add_argument('--baud',type=int,choices=[115200,460800],default=460800);ap.add_argument('--smoke-test',action='store_true');args=ap.parse_args()
    app=QApplication(sys.argv);window=Window(args.output);window.baud.setCurrentIndex(window.baud.findData(args.baud));window.show()
    if args.build:window.load_build(args.build)
    if args.port:
        index=window.ports.findData(args.port)
        if index<0:raise SystemExit(f'Port bulunamadı: {args.port}')
        window.ports.setCurrentIndex(index)
    if args.demo or args.port:QTimer.singleShot(100,window.toggle_connection)
    if args.smoke_test:
        def finish_smoke():
            if args.output:
                folder=Path(args.output);folder.mkdir(parents=True,exist_ok=True);window.grab().save(str(folder/'packaged-gui.png'))
            window.close();app.quit()
        QTimer.singleShot(2500,finish_smoke)
    return app.exec()

if __name__=='__main__':raise SystemExit(main())
