"""Explicitly synthetic protocol peer, NOT an RTOS scheduling simulator."""
import time,zlib
from .protocol import frame,SUM_KEYS

class Simulator:
    def __init__(self, clock=time.monotonic):
        self.clock=clock;self.state='IDLE';self.run=0;self.scenario='S0';self.rows=[];self.selected='S0'
        self.started=0;self.last_tel=0;self.tel=0;self.saved=None;self.cache={};self.last_press=None
    def command(self,text):
        fields=text.strip().split(',');cmd=fields[0];req=fields[1] if len(fields)>1 else '0'
        if req!='0' and req in self.cache:
            old,answer=self.cache[req]
            return [] if self.state in {'ARMED','WARMUP'} else ([frame(f'ERR,{req},BAD_ARG')] if old!=text else answer)
        result=[]
        if cmd=='HELLO':result=[frame('SYS,RTOSLAT,FW03,PROTO2'),frame(f'ACK,{req},HELLO,{self.run}'),frame(f'EXP,{self.run},{self.state},{self.scenario}')]
        elif cmd=='CFG' and self.state in {'IDLE','CONFIGURED','DONE'} and len(fields)==3 and fields[2] in {f'S{i}' for i in range(6)}:
            self.selected=fields[2];self.state='CONFIGURED';result=[frame(f'ACK,{req},CFG,{self.run}'),frame(f'EXP,{self.run},CONFIGURED,{self.selected}')]
        elif cmd=='START' and self.state=='CONFIGURED':
            self.scenario=self.selected;self.run+=1;self.rows=[];self.tel=0;self.last_press=None;self.state='WARMUP';self.started=self.clock()
            result=[frame(f'ACK,{req},START,{self.run}'),frame(f'EXP,{self.run},WARMUP,{self.scenario}')]
        elif cmd=='STOP' and self.state in {'WARMUP','ARMED'}:
            cancelled=self.state=='WARMUP';self.state='DONE'
            self.saved=self.dump('CANCELLED' if cancelled else 'COMPLETE')
            result=[frame(f'ACK,{req},STOP,{self.run}'),*self.saved]
        elif cmd=='DUMP' and self.saved and self.state in {'DONE','CONFIGURED'}:result=[frame(f'ACK,{req},DUMP,{self.run}'),*self.saved]
        else:result=[frame(f'ERR,{req},BAD_STATE')]
        if req!='0':self.cache={req:(text,result[:1])}
        return result
    def poll(self):
        now=self.clock();out=[]
        if self.state=='WARMUP' and now-self.started>=5:
            self.state='ARMED';self.started=now;self.last_tel=now;out.append(frame(f'EXP,{self.run},ARMED,{self.scenario}'))
        rates=[0,10,50,100,100,100];hz=rates[int(self.scenario[1])]
        if self.state=='ARMED' and hz:
            while now-self.last_tel>=1/hz:
                self.last_tel+=1/hz;self.tel+=1;out.append(frame(f'TEL,{self.run},{self.scenario},{self.tel},{self.tel*17}'))
        return out
    def press(self):
        if self.state!='ARMED':return []
        now=self.clock()
        if self.last_press is not None and now-self.last_press<.5:return []
        self.last_press=now;i=len(self.rows)+1;s=int(self.scenario[1]);t0=int((now-self.started)*1e6)+1000000
        d1=80+(i*137%(1+[0,200,500,1200,2600,5600][s]));d2=40;d3=60+(i*719%(1+[0,500,2200,5000,6500,8500][s]));d4=5600
        t=[t0,t0+d1,t0+d1+d2,t0+d1+d2+d3,t0+d1+d2+d3+d4];self.rows.append((i,t))
        return [frame(f'BTN,{self.run},{self.scenario},{i},PRESSED')]
    def dump(self,result='COMPLETE'):
        s=int(self.scenario[1]);period=[0,100,20,10,10,10][s];n=len(self.rows)
        meta=dict(sysclk_hz=168000000,timer_hz=1000000,tick_hz=1000,baud=115200,frame_bytes=64,prio_tel=3,prio_btn=2,prio_tx=1,buttonq_len=8,txq_len=16,record_capacity=128,
            telemetry_hz=1000//period if period else 0,period_ms=period,work_target_us=[0,0,0,0,2000,5000][s],work_iters=0,work_min_us=0,work_mean_us=0,work_max_us=0,
            run_start_us=1000000,run_stop_us=int((self.clock()-self.started)*1e6)+1000000,tel_first_us=1000000 if self.tel else '-',tel_last_us=1000000+(self.tel-1)*period*1000 if self.tel else '-',
            period_min_us=period*1000 if self.tel>=2 else '-',period_max_us=period*1000 if self.tel>=2 else '-',period_sum_us=max(0,self.tel-1)*period*1000,period_n=max(0,self.tel-1),
            fw_sha_a='synthetic',fw_sha_b='synthetic',build_config='SYNTHETIC',opt_level='none',kernel_version='V10.3.1',result=result)
        counters=dict.fromkeys(SUM_KEYS,0);counters.update(accepted=n,ok=n,late_completed=sum(t[4]-t[0]>20000 for _,t in self.rows),tel_generated=self.tel,tel_enqueued=self.tel,tel_completed=self.tel,txq_hwm=1 if n or self.tel else 0,buttonq_hwm=1 if n else 0)
        out=[frame(f'BEGIN,{self.run},{self.scenario},{n},{n}')]
        out += [frame(f'MET,{self.run},{k},{v}') for k,v in meta.items()]
        out += [frame(f'SUM,{self.run},{k},{v}') for k,v in sorted(counters.items())]
        crc=0
        for i,t in self.rows:
            for msg in [f'M1,{self.run},{i},{t[0]},{t[1]},{t[2]}',f'M2,{self.run},{i},{t[3]},{t[4]},ok']:
                raw=frame(msg);crc=zlib.crc32(raw,crc);out.append(raw)
        return out+[frame(f'END,{self.run},{n},{crc:08X}'),frame(f'EXP,{self.run},DONE,{self.scenario}')]
