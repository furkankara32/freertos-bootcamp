"""Short SystemView snapshots while the existing serial session keeps running."""
import hashlib
import json
import sys
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from PySide6.QtCore import QProcess, QTimer, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (QComboBox, QFileDialog, QGroupBox, QHBoxLayout,
                              QLabel, QPushButton, QSpinBox, QVBoxLayout)

def week_root():
    anchor = Path(sys.executable).resolve() if getattr(sys, 'frozen', False) else Path(__file__).resolve()
    for parent in anchor.parents:
        if (parent / 'tools/export_systemview.py').is_file() and (parent / 'projects/v2').is_dir():
            return parent
    raise RuntimeError('Arayüz hafta-02 klasörü içinde çalıştırılmalı.')


WEEK = week_root()


def elf_symbols(elf):
    choices = sorted(Path('C:/ST').glob('**/arm-none-eabi-nm.exe'))
    if not choices:
        raise ValueError('ELF kontrolü için STM32 toolchain bulunamadı (C:/ST).')
    try:
        output = subprocess.check_output([str(choices[-1]), '--defined-only', str(elf)],
                                         text=True, stderr=subprocess.STDOUT, timeout=15,
                                         creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    except (OSError, subprocess.SubprocessError) as exc:
        raise ValueError('ELF sembolleri okunamadı: ' + str(exc)) from exc
    return {line.split()[-1] for line in output.splitlines() if line.split()}



def validate_build(elf, protocol, baud):
    elf = Path(elf)
    metadata = elf.with_name('build.json')
    if not metadata.exists():
        if protocol not in {'PROTO2','PROTO3'} or baud != (115200 if protocol == 'PROTO2' else 460800):
            raise ValueError('Önce V1 veya V2-QWB karta doğru baud ile bağlanın.')
        required = {'_SEGGER_RTT','app_trace_capture_complete','app_trace_bytes','app_trace_dropped','AppTrace_Start'}
        if not required <= elf_symbols(elf):
            raise ValueError('ELF SystemView desteği içermiyor. CubeIDE içinde APP_TRACE=1 ile derleyin.')
        return {'variant': 'V1' if protocol == 'PROTO2' else 'QWB',
                'protocol': protocol, 'baud': baud, 'trace_backend': 'systemview',
                'elf_sha256': hashlib.sha256(elf.read_bytes()).hexdigest(),
                'identity_source': 'CubeIDE ELF symbols checked; profile from connected board; operator matches ELF',
                'build_metadata_available': False}
    build = json.loads(metadata.read_text(encoding='utf-8'))
    if not isinstance(build, dict):
        raise ValueError('build.json bir JSON nesnesi olmalı.')
    expected = ('V1', 1, 115200) if protocol == 'PROTO2' else ('QWB', 2, 460800)
    if protocol not in {'PROTO2', 'PROTO3'}:
        raise ValueError('Önce gerçek karta bağlanın.')
    if (build.get('variant'), build.get('design_version'), baud) != expected:
        raise ValueError('Seçilen ELF, bağlı V1 / V2-QWB profiliyle eşleşmiyor.')
    if build.get('protocol') != protocol or build.get('baud') != baud:
        raise ValueError('Build protokolü / baud bilgisi kartla eşleşmiyor.')
    if build.get('trace_backend') != 'systemview':
        raise ValueError('SystemView destekli ELF seçin (--trace systemview).')
    if hashlib.sha256(elf.read_bytes()).hexdigest() != build.get('elf_sha256'):
        raise ValueError('ELF ile build.json SHA256 eşleşmiyor. Doğru derlemeyi seçin.')
    return build


def validate_recording(folder):
    info = json.loads((folder / 'trace.json').read_text(encoding='utf-8'))
    if not isinstance(info, dict):
        raise ValueError('trace.json bir JSON nesnesi olmalı.')
    trace = folder / 'recording.SVDat'
    if not info.get('capture_complete') or not info.get('clean') or info.get('dropped_events') != 0:
        raise ValueError('İzleme kaybı veya eksik kayıt var. Süreyi kısaltıp yeniden kaydedin.')
    data = trace.read_bytes()
    if not 0 < len(data) == info.get('bytes', 0) < info.get('capacity', 0):
        raise ValueError('Kayıt boyutu doğrulanamadı.')
    if hashlib.sha256(data).hexdigest() != info.get('trace_sha256'):
        raise ValueError('Kayıt dosyasının SHA256 değeri eşleşmiyor.')
    return trace


class SystemViewPanel(QGroupBox):
    def __init__(self, window):
        super().__init__('SystemView kaydı • V1 / V2-QWB', window)
        self.window = window
        self.busy = False
        self.elf = None
        self.explicit_elf = False
        self.protocol = None
        self.req = None
        self.folder = None
        self.manifest = None
        self.invalid = None
        self.process = None
        self.records = []
        self.countdown_seconds = 3
        self.countdown_timer = QTimer(self)
        self.countdown_timer.timeout.connect(self.countdown_tick)
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.recording_ended)
        self.settle_timer = QTimer(self)
        self.settle_timer.setSingleShot(True)
        self.settle_timer.timeout.connect(self.export)
        self.recommended_scenario = None
        self.sent_timer = QTimer(self)
        self.sent_timer.setSingleShot(True)
        self.sent_timer.timeout.connect(lambda: self.fail('TRACE komutu seri porta yazılamadı.'))
        self.watchdog = QTimer(self)
        self.watchdog.setSingleShot(True)
        self.watchdog.timeout.connect(self.export_timeout)
        layout = QVBoxLayout(self)
        row = QHBoxLayout()
        layout.addLayout(row)
        self.duration = QSpinBox()
        self.duration.setRange(50, 2000)
        self.duration.setSingleStep(100)
        self.duration.setValue(500)
        self.duration.setSuffix(' ms')
        self.duration.setToolTip('Isınma dahil değil. S0: 1000 ms; S5: 500 ms. Sınır: 50–2000 ms; tampon dolarsa süreyi azaltın.')
        self.record = QPushButton('SystemView için kaydet')
        self.select_elf = QPushButton('Yüklü ELF seç')
        self.files = QComboBox()
        self.files.setMinimumWidth(180)
        self.open = QPushButton('SystemView’da aç')
        self.reveal = QPushButton('Klasörü aç')
        for item in [QLabel('Kayıt süresi:'), self.duration, self.record, self.select_elf,
                     self.files, self.open, self.reveal]:
            row.addWidget(item)
        self.status = QLabel('Senaryoyu uygula → Başlat → ARMED → SystemView için kaydet. İki USB bağlantısı da gerekli.')
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        self.timing_help = QLabel('Önce ≥5 s ısınma ve ARMED. Kayıt: S0 için 1000 ms, S5 için 500 ms. 3 s geri sayım kayda dahil değil.')
        self.timing_help.setWordWrap(True)
        layout.addWidget(self.timing_help)
        self.identity = QLabel('ELF, karta yüklediğiniz derlemeyle aynı olmalı. Firmware bu düğmeyle değiştirilmez.')
        self.identity.setWordWrap(True)
        layout.addWidget(self.identity)
        self.record.clicked.connect(self.start)
        self.select_elf.clicked.connect(self.choose_elf)
        self.open.clicked.connect(self.open_recording)
        self.reveal.clicked.connect(self.open_folder)
        self.files.currentIndexChanged.connect(self.update_controls)
        self.update_controls()

    def choose_elf(self):
        path, _ = QFileDialog.getOpenFileName(self, 'CubeIDE ile karta yüklediğiniz ELF dosyası',
                                               str(self.elf or WEEK / 'projects'), 'ELF (*.elf)')
        if path:
            self.elf = Path(path)
            self.explicit_elf = True
            self.identity.setText('Seçili ELF: ' + path)

    def on_receive(self, kind, data):
        if kind == 'SYS':
            if self.protocol != data[3]:
                self.protocol = data[3]
                rel = ('v1/firmware/build/v1/Release/systemview/Homework_001.elf'
                       if self.protocol == 'PROTO2' else
                       'v2/firmware/build/v2/QWB/Release/systemview/Homework_001.elf')
                if not self.explicit_elf:
                    self.elf = WEEK / 'projects' / rel
                self.identity.setText('ELF: ' + str(self.elf) + ' • Karttaki derlemeyle aynı olmalı.')
        elif kind == 'ERR' and self.busy:
            self.invalidate('Kart TRACE komutunu reddetti: ' + ','.join(data[1:]))
        elif kind == 'EXP':
            if self.busy and (data[2] != 'ARMED' or int(data[1]) != self.manifest['run']):
                self.invalidate('Kayıt sırasında deney durumu değişti; pencere geçersiz.')
            elif not self.busy and data[3] != self.recommended_scenario:
                self.recommended_scenario = data[3]
                self.duration.setValue(1000 if data[3] == 'S0' else 500)
        elif kind == 'SAVED':
            dump, folder = data
            for record in self.records:
                if record['run'] == dump.run and record['connection'] == self.window.connection_id:
                    record['measurement_folder'] = str(folder)
                    try:
                        self.write_manifest(record)
                    except OSError as exc:
                        self.status.setText('Ölçüm kaydedildi; izleme bağlantı bilgisi yazılamadı: ' + str(exc))
        self.update_controls()

    def update_controls(self, *_):
        w = self.window
        eligible = (w.is_connected and w.ready and not w.demo and w.state == 'ARMED'
                    and w.pending is None and not self.busy)
        self.record.setEnabled(eligible)
        self.select_elf.setEnabled(not self.busy)
        self.duration.setEnabled(not self.busy)
        available = self.files.currentData() is not None
        self.open.setEnabled(available and not self.busy)
        self.reveal.setEnabled(available)

    def start(self):
        self.update_controls()
        if not self.record.isEnabled():
            return
        w = self.window
        try:
            build = validate_build(self.elf, w.protocol_version, w.baud.currentData())
            helper = WEEK / 'tools/export_systemview.py'
            python = WEEK / 'projects/v2/interface/.venv/Scripts/python.exe'
            if not helper.is_file() or not python.is_file():
                raise ValueError('Hafta-02 araçları veya ortak Python ortamı bulunamadı.')
            self.folder = w.output / 'systemview' / build['variant'] / w.active_scenario / datetime.now().strftime('%Y%m%d-%H%M%S-%f')
            self.folder.mkdir(parents=True, exist_ok=False)
            # Preserve the exact symbol file even if CubeIDE rebuilds it during export.
            elf_bytes = self.elf.read_bytes()
            if hashlib.sha256(elf_bytes).hexdigest() != build['elf_sha256']:
                raise ValueError('ELF doğrulama sırasında değişti. Derlemenin bitmesini bekleyin.')
            self.capture_elf = self.folder / 'firmware.elf'
            self.capture_elf.write_bytes(elf_bytes)
            self.req = w.next_request_id()
            self.manifest = {'status': 'recording', 'folder': str(self.folder),
                             'run': w.current_run, 'scenario': w.active_scenario,
                             'connection': w.connection_id, 'port': w.ports.currentData(),
                             'window_ms': self.duration.value(), 'build': build,
                             'elf': str(self.elf), 'archived_elf': str(self.capture_elf), 'started_utc': datetime.now(timezone.utc).isoformat(),
                             'build_identity_source': 'host ELF; operator must match flashed build',
                             'method': 'frozen RTT via ST-LINK; existing UART session remains open'}
            self.write_manifest(self.manifest)
            self.busy = True
            self.invalid = None
            self.remaining = self.countdown_seconds
            if self.remaining:
                self.status.setText(f'{self.remaining} saniye sonra kayıt açılacak. USER butonuna basmaya hazırlanın.')
                self.countdown_timer.start(1000)
            else:
                self.begin_capture()
            w.update_controls()
        except (OSError, ValueError, TypeError) as exc:
            self.status.setText('Kayıt başlatılamadı: ' + str(exc))

    def countdown_tick(self):
        self.remaining -= 1
        if self.remaining <= 0:
            self.countdown_timer.stop()
            self.begin_capture()
        else:
            self.status.setText(f'{self.remaining} saniye sonra kayıt açılacak. USER butonuna basmaya hazırlanın.')

    def begin_capture(self):
        if not self.busy:
            return
        self.status.setText('İzleme komutu gönderiliyor…')
        self.window.worker.send(f'TRACE,{self.req},{self.manifest["window_ms"]}')
        self.sent_timer.start(3000)

    def command_sent(self, command):
        if not self.busy or command != f'TRACE,{self.req},{self.manifest["window_ms"]}':
            return
        # Firmware intentionally sends no TRACE ACK. Start after actual UART write.
        self.sent_timer.stop()
        self.status.setText(f'KAYIT AÇIK • Şimdi mavi USER butonuna basın ({self.manifest["window_ms"]} ms).')
        self.timer.start(self.manifest['window_ms'])

    def recording_ended(self):
        self.status.setText('Kayıt süresi doldu. Artık bu pencere için butona basmayın; aktarım hazırlanıyor…')
        self.settle_timer.start(350)

    def export(self):
        if not self.busy or self.invalid:
            return
        self.status.setText('Kayıt süresi doldu • ST-LINK ile dosyaya aktarılıyor… Deney devam ediyor.')
        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.finished.connect(self.export_finished)
        self.process.errorOccurred.connect(self.process_error)
        self.process.setProgram(str(WEEK / 'projects/v2/interface/.venv/Scripts/python.exe'))
        self.process.setArguments([str(WEEK / 'tools/export_systemview.py'), '--elf', str(self.capture_elf),
                                   '--output', str(self.folder)])
        self.process.setWorkingDirectory(str(WEEK))
        self.watchdog.start(45000)
        self.process.start()

    def process_error(self, error):
        if error == QProcess.ProcessError.FailedToStart:
            self.fail('Dışa aktarma aracı başlatılamadı: ' + self.process.errorString())

    def export_timeout(self):
        self.invalid = 'Dışa aktarma zaman aşımı. openocd.log dosyasını inceleyin.'
        if self.process and self.process.state() != QProcess.ProcessState.NotRunning:
            self.process.kill()
        else:
            self.fail(self.invalid)

    def export_finished(self, code, status):
        self.watchdog.stop()
        output = bytes(self.process.readAllStandardOutput()).decode('utf-8', errors='replace')
        try:
            (self.folder / 'export.log').write_text(output, encoding='utf-8')
            if self.invalid:
                raise ValueError(self.invalid)
            if code or status != QProcess.ExitStatus.NormalExit:
                raise ValueError(('Tampon doldu / izleme kaybı var. Kayıt süresini kısaltıp tekrar deneyin.' if code == 2 else 'Aktarım başarısız. Süreyi/ELF’i/bağlantıyı ve export.log dosyasını kontrol edin.'))
            trace = validate_recording(self.folder)
            self.manifest['status'] = 'complete'
            self.manifest['trace'] = str(trace)
            self.write_manifest(self.manifest)
            self.records.append(self.manifest)
            self.files.addItem(f'{self.manifest["scenario"]} / run {self.manifest["run"]} / {self.folder.name}', str(trace))
            self.files.setCurrentIndex(self.files.count() - 1)
            self.status.setText('Kayıt hazır: ' + str(trace) + '\nYeni pencere alabilir veya Durdur ve aktar ile ölçümü tamamlayabilirsiniz.')
            self.finish()
        except (OSError, ValueError, TypeError) as exc:
            self.fail(str(exc))

    def write_manifest(self, record):
        (Path(record['folder']) / 'session.json').write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding='utf-8')

    def invalidate(self, message):
        if not self.busy:
            return
        self.invalid = message
        if self.process and self.process.state() != QProcess.ProcessState.NotRunning:
            self.status.setText(message + ' Aktarımın kapanması bekleniyor.')
        else:
            self.fail(message)

    def fail(self, message):
        if self.manifest and self.busy:
            self.manifest.update(status='failed', error=message)
            try:
                self.write_manifest(self.manifest)
            except OSError:
                pass
        self.status.setText('Kayıt başarısız: ' + message)
        self.finish()

    def finish(self):
        self.countdown_timer.stop()
        self.timer.stop()
        self.settle_timer.stop()
        self.sent_timer.stop()
        self.watchdog.stop()
        self.busy = False
        self.window.update_controls()

    def open_recording(self):
        trace = self.files.currentData()
        exe = WEEK / 'tools/SystemView-4.10a/SystemView.exe'
        if not exe.is_file():
            selected, _ = QFileDialog.getOpenFileName(self, 'SystemView.exe seçin', '', 'SystemView (SystemView.exe)')
            if not selected:
                return
            exe = Path(selected)
        if trace and not QProcess.startDetached(str(exe), ['-load', trace])[0]:
            self.status.setText('SystemView açılamadı. Klasörü açıp recording.SVDat dosyasını elle yükleyin.')

    def open_folder(self):
        trace = self.files.currentData()
        if trace:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(Path(trace).parent)))
