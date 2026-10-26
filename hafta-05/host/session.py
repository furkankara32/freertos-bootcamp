"""Single writer serial session; raw recordings remain separate from analysis."""
import csv, json, queue, threading, time
from datetime import datetime
from pathlib import Path
import serial
from .protocol import *
from .record_store import new_record
import secrets

class Session:
    def __init__(self, on_frame, on_error):
        self.on_frame=on_frame;self.on_error=on_error;self.port=None;self.thread=None
        self.tx=queue.Queue();self.seq=0;self.stop_event=threading.Event();self.folder=None
        self.decoder=Decoder();self.frames=[];self.lock=threading.Lock();self.identity=None
    def connect(self,port):
        self.port=serial.Serial(port,115200,timeout=.02,write_timeout=2)
        self.stop_event.clear();self.thread=threading.Thread(target=self._loop,daemon=True);self.thread.start();self.send(HELLO)
    def send(self,kind,values=()):
        if kind==STOP:
            # Cancel host-queued bulk/commands; bytes already on the wire cannot be recalled.
            while True:
                try:self.tx.get_nowait()
                except queue.Empty:break
        self.seq+=1;self.tx.put(encode(kind,self.seq,values));return self.seq
    def send_bulk(self):
        for _ in range(100): self.send(LOAD,[self.seq])
    def begin(self,root,scenario,variant,period=1000,cycles=3):
        if not self.identity: raise RuntimeError('Kart kimliği doğrulanmadı')
        if self.folder: raise RuntimeError('Önce mevcut kaydı bitirin')
        build=Path(root).parent/'firmware/build/Release/build.json'
        if build.exists():
            expected=json.loads(build.read_text())['build_id'][:32]
            actual=struct.pack('<8I',*self.identity['values'][4:12]).decode('ascii',errors='replace')
            if expected!=actual:raise RuntimeError('Kart firmware sürümü yerel ELF ile eşleşmiyor; önce firmware yükleyin')
        if variant not in {1:range(1),2:range(3),3:range(2),4:range(2)}.get(scenario,()):
            raise ValueError('Geçersiz senaryo/varyant')
        if not 50<=period<=5000 or not 1<=cycles<=100:raise ValueError('Geçersiz LED süresi/tur sayısı')
        if not self.tx.empty():raise RuntimeError('Önce gönderim kuyruğunun boşalmasını bekleyin')
        run=secrets.randbits(32) or 1
        folder=new_record(root,scenario)
        manifest={'run_id':run,'scenario':scenario,'variant':variant,'period_ms':period,'cycles':cycles,'baud':115200,'port':self.port.port,'pins':{'rx':'PB11 USART3','tx':'PA2 USART2'},'identity':self.identity,'capture_status':'RECORDING','trace_mode':'ST-LINK single-shot','source':'hardware','trace_window_ms':1500}
        (folder/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
        manifest['created_at']=datetime.now().astimezone().isoformat()
        manifest.update(task_priorities={'Parser':4,'Execute':3,'Report':5 if scenario==2 and variant!=1 else 2},
                        buffers={'rx_stream':4096,'tx_stream':512,'command_queue':8,'result_queue':64},
                        cpu_hz=168000000,tick_hz=1000,timer_hz=1000000,
                        diag_frames=20,parser_work_units=200,bulk_bytes=10000,
                        firmware=json.loads(build.read_text()) if build.exists() else None)
        (folder/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
        with self.lock:self.frames=[];self.folder=folder;self.run_id=run;self.rejected_start=self.decoder.rejected_bytes
        self.send(START,[run,scenario,variant,period,cycles,1500]);return folder
    def finish(self):
        with self.lock:
            folder=self.folder
            if not folder:return None
            rows=[{'seq':f.seq,'command_id':f.values[1],'old_led':f.values[2],'new_led':f.values[3],'planned_us':f.values[4],'actual_us':f.values[5],'on_duration_us':f.values[7],'late_us':f.values[8]} for f in self.frames if f.kind==LED and f.values[2]<4 and f.values[0]==self.run_id]
            with (folder/'led_timing.csv').open('w',newline='',encoding='utf-8') as fp:
                writer=csv.DictWriter(fp,fieldnames=['seq','command_id','old_led','new_led','planned_us','actual_us','on_duration_us','late_us']);writer.writeheader();writer.writerows(rows)
            late=[r['late_us'] for r in rows]
            summary={'samples':len(late),'min_us':min(late,default=0),'mean_us':sum(late)/len(late) if late else None,'max_us':max(late,default=0),'over_10ms':sum(v>10000 for v in late),'decoder_rejected_bytes':self.decoder.rejected_bytes-self.rejected_start,'trace_status':'MISSING'}
            (folder/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
            manifest=json.loads((folder/'manifest.json').read_text());manifest['capture_status']='UART_SAVED_TRACE_PENDING'
            (folder/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8');self.folder=None
            return folder
    def _append(self,name,data):
        if self.folder:
            with (self.folder/name).open('ab') as fp:fp.write(data)
    def _loop(self):
        try:
            while not self.stop_event.is_set():
                try: data=self.tx.get_nowait()
                except queue.Empty:data=None
                if data:
                    written=self.port.write(data)
                    if written!=len(data):raise IOError('Kısmi host seri yazma')
                    with self.lock:
                        self._append('host_tx.bin',data)
                        self._append('host_tx_events.jsonl',(json.dumps({'host_ns':time.time_ns(),'bytes':written})+'\n').encode())
                waiting=self.port.in_waiting
                data=self.port.read(waiting) if waiting else (self.port.read(1) if self.tx.empty() else b'')
                if data:
                    with self.lock:self._append('raw_rx_uart.bin',data)
                    for frame in self.decoder.feed(data):
                        if frame.kind==MSG_HELLO:
                            if frame.values[:3]!=(0xF4070005,1,115200):raise RuntimeError('Yanlış kart/firmware/protokol')
                            self.identity=frame.as_dict()
                        with self.lock:
                            if self.folder:self.frames.append(frame)
                            self._append('events.jsonl',(json.dumps(frame.as_dict())+'\n').encode())
                        self.on_frame(frame)
        except Exception as exc:self.identity=None;self.on_error(str(exc))
    def close(self):
        self.stop_event.set()
        if self.thread:self.thread.join(3)
        if self.port:self.port.close()
        self.identity=None
