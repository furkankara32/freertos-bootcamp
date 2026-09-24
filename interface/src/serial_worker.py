from datetime import datetime,timezone
from pathlib import Path
from queue import SimpleQueue,Empty
from threading import Event
import time
import serial
from PySide6.QtCore import QThread,Signal
from .protocol import Decoder,Protocol,ProtocolError
from .simulator import Simulator
from .storage import save_dump

class SerialWorker(QThread):
    received=Signal(str,object)
    problem=Signal(str)
    connected=Signal(bool)
    def __init__(self, port, output, parent=None):
        super().__init__(parent);self.port=port;self.output=Path(output);self.commands=SimpleQueue();self.halt=Event()
    def send(self,text):self.commands.put(text)
    def stop(self):self.halt.set()
    def run(self):
        handle=None;raw_file=None;raw=bytearray();decoder=Decoder();protocol=Protocol()
        demo=self.port=='DEMO';sim=Simulator() if demo else None
        try:
            session=self.output/('demo' if demo else 'runs')/('connection_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ'))
            session.mkdir(parents=True,exist_ok=False);raw_file=(session/'serial_raw.partial.bin').open('wb')
            if not demo:handle=serial.Serial(self.port,115200,timeout=.02,write_timeout=1,dsrdtr=False,rtscts=False)
            self.connected.emit(True)
            while not self.halt.is_set():
                incoming=[]
                try:
                    while True:
                        cmd=self.commands.get_nowait()
                        if demo:incoming.extend(sim.press() if cmd=='!PRESS' else sim.command(cmd))
                        elif cmd!='!PRESS':handle.write((cmd+'\n').encode('ascii'))
                except Empty:pass
                if demo:incoming.extend(sim.poll());time.sleep(.01)
                else:
                    chunk=handle.read(min(max(handle.in_waiting,1),4096))
                    if chunk:incoming.append(chunk)
                for chunk in incoming:
                    raw.extend(chunk);raw_file.write(chunk)
                    frames=decoder.feed(chunk)
                    if decoder.errors:
                        protocol.invalidate()
                        for err in decoder.errors:self.problem.emit(err)
                        decoder.errors.clear()
                    for line in frames:
                        try:
                            kind,payload=protocol.accept(line)
                            if kind=='DUMP':
                                folder=save_dump(payload,self.output,raw,demo,{'port':self.port,'connection_path':str(session)})
                                raw_file.flush();self.received.emit('SAVED',(payload,str(folder)))
                            else:self.received.emit(kind,payload)
                        except ProtocolError as exc:self.problem.emit(str(exc))
                # Bound in-memory transport capture. Full connection bytes remain on disk.
                if len(raw)>4*1024*1024 and protocol.dump is None:raw.clear()
        except Exception as exc:self.problem.emit(f'Bağlantı/kayıt hatası: {exc}')
        finally:
            if handle:handle.close()
            if raw_file:raw_file.close()
            self.connected.emit(False)
