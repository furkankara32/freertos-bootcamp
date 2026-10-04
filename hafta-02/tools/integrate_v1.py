"""One-time V1 integration; checks originals before copying shared trace hooks."""
from pathlib import Path
import shutil
W=Path(__file__).resolve().parents[1]; P=W/'projects/v1/firmware/Homework_001'; V=W/'projects/v2/firmware/Homework_001'
O=Path('D:/freertos-bootcamp/hafta-01/firmware/Homework_001')
for rel in ['Inc/FreeRTOSConfig.h','Middlewares/Third_Party/FreeRTOS/Source/include/FreeRTOS.h','Middlewares/Third_Party/FreeRTOS/Source/tasks.c','Middlewares/Third_Party/FreeRTOS/Source/portable/GCC/ARM_CM4F/port.c','Src/main.c','Src/stm32f4xx_it.c','.cproject']:
 assert (P/rel).read_text()==(O/rel).read_text(),rel
 shutil.copy2(V/rel,P/rel)
shutil.copytree(V/'Middlewares/SEGGER',P/'Middlewares/SEGGER')
shutil.copy2(V/'Inc/app_trace.h',P/'Inc/app_trace.h')
s=(V/'Src/app_trace.c').read_text().replace('#include "app_config.h"','').replace('Bootcamp_V2','Bootcamp_V1').replace('"N=Bootcamp V2 " APP_VARIANT ",D=STM32F407VG,O=FreeRTOS"','"N=Bootcamp V1,D=STM32F407VG,O=FreeRTOS"')
(P/'Src/app_trace.c').write_text(s)
f=P/'Src/app.c';s=f.read_text()
def edit(a,b,count=1):
 global s
 assert s.count(a)==count,(a,s.count(a));s=s.replace(a,b)
edit('#include "queue.h"','#include "queue.h"\n#include "app_trace.h"')
edit('static volatile uint16_t active_index = NO_RECORD;','static volatile uint16_t active_index = NO_RECORD;\n#if APP_TRACE\nstatic uint32_t trace_tel_id, trace_tel_run;\n#endif')
edit('    if (!button_q || !tx_q || !control_q) Error_Handler();','''    if (!button_q || !tx_q || !control_q) Error_Handler();
    AppTrace_NameQueue(button_q,"button_q");
    AppTrace_NameQueue(tx_q,"shared_tx_q");
    AppTrace_NameQueue(control_q,"command_q");''')
edit('    records[index].status=PENDING;','    records[index].status=PENDING;\n    AppTrace_Event(TR_BTN_ACCEPT,run_id,id,now,0);')
edit('records[index].status=BUTTON_DROP; ++counters[BQ_DROP];','records[index].status=BUTTON_DROP; ++counters[BQ_DROP]; AppTrace_Event(TR_BTN_DROP,run_id,id,now,BUTTON_DROP);')
edit('        if(!pending) continue;','        if(!pending) continue;\n        AppTrace_Event(TR_BTN_TASK,run_id,records[i].id,t1,0);')
edit('        if(xQueueSend(tx_q,&m,0)!=pdPASS) { records[i].status=TX_DROP; ++counters[BTX_DROP]; }','''        AppTrace_Event(TR_BTN_READY,run_id,records[i].id,records[i].t[2],0);
        if(xQueueSend(tx_q,&m,0)!=pdPASS) { records[i].status=TX_DROP; ++counters[BTX_DROP]; AppTrace_Event(TR_BTN_DROP,run_id,records[i].id,App_Now(),TX_DROP); }''')
edit('        else {UBaseType_t n=uxQueueMessagesWaiting(tx_q);if(n>counters[TX_HWM])counters[TX_HWM]=n;}','        else {UBaseType_t n=uxQueueMessagesWaiting(tx_q);if(n>counters[TX_HWM])counters[TX_HWM]=n;AppTrace_Event(TR_BTN_ENQUEUE,run_id,records[i].id,App_Now(),n);}')
edit('records[i].t[4]=now;records[i].mask|=16;records[i].status=OK;','records[i].t[4]=now;records[i].mask|=16;records[i].status=OK;\n            AppTrace_Event(TR_BTN_TX_TC,run_id,records[i].id,now,0);')
edit('    taskEXIT_CRITICAL_FROM_ISR(mask);','''#if APP_TRACE
    if(i==NO_RECORD && trace_tel_id) AppTrace_Event(TR_TEL_TX_TC,trace_tel_run,trace_tel_id,now,0);
#endif
    taskEXIT_CRITICAL_FROM_ISR(mask);''')
edit('    HAL_StatusTypeDef rc=HAL_UART_Transmit_DMA(&huart2,dma_bytes,64);','''    if(index!=NO_RECORD) AppTrace_Event(TR_BTN_TX_START,run_id,records[index].id,records[index].t[3],0);
#if APP_TRACE
    else if(trace_tel_id) AppTrace_Event(TR_TEL_TX_START,trace_tel_run,trace_tel_id,App_Now(),0);
#endif
    HAL_StatusTypeDef rc=HAL_UART_Transmit_DMA(&huart2,dma_bytes,64);
    if(rc!=HAL_OK) AppTrace_Event(TR_TX_ERROR,run_id,index!=NO_RECORD?records[index].id:0,App_Now(),rc);''')
edit('        int success=transmit(m.bytes,m.index,m.kind==TEL||m.kind==BTN);','''#if APP_TRACE
        trace_tel_id=trace_tel_run=0;
        if(m.kind==TEL) {
            unsigned field=0;uint32_t value=0;
            for(unsigned j=4;j<FRAME;j++) {
                uint8_t c=m.bytes[j];
                if(c>='0' && c<='9')value=value*10U+(c-'0');
                else if(c==',') {if(field==0)trace_tel_run=value;if(field==2){trace_tel_id=value;break;}field++;value=0;}
            }
        }
#endif
        int success=transmit(m.bytes,m.index,m.kind==TEL||m.kind==BTN);''')
edit('    workload(iterations);','    AppTrace_Event(TR_WORK_BEGIN,run_id,sequence+1,App_Now(),0);\n    workload(iterations);\n    AppTrace_Event(TR_WORK_END,run_id,sequence+1,App_Now(),0);')
edit('if(xQueueSend(tx_q,&m,0)!=pdPASS){if(state==RUNNING)++counters[TEL_DROP];}','if(xQueueSend(tx_q,&m,0)!=pdPASS){if(state==RUNNING)++counters[TEL_DROP];AppTrace_Event(TR_TEL_DROP,run_id,sequence,App_Now(),TX_DROP);}')
edit('else if(state==RUNNING){++counters[TEL_ENQUEUED];UBaseType_t n=uxQueueMessagesWaiting(tx_q);if(n>counters[TX_HWM])counters[TX_HWM]=n;}','else if(state==RUNNING){++counters[TEL_ENQUEUED];UBaseType_t n=uxQueueMessagesWaiting(tx_q);if(n>counters[TX_HWM])counters[TX_HWM]=n;AppTrace_Event(TR_TEL_ENQUEUE,run_id,sequence,App_Now(),n);}')
edit('static void finish(uint32_t req,int cancelled)\n{','static void finish(uint32_t req,int cancelled)\n{\n    AppTrace_Event(TR_RUN_STOP,run_id,scenario,App_Now(),cancelled);')
edit('    char error[64];snprintf(error,64,"ERR,%lu,BAD_ARG",(unsigned long)req);','''#if APP_TRACE
    if(!strcmp(cmd->bytes,"TRACE")) {
        uint32_t duration;
        if(!arg || !number(arg,&duration) || duration>2000U){reply("ERR,0,BAD_TRACE");return;}
        if(duration) { AppTrace_Start(duration);AppTrace_Event(TR_RUN_CONFIG,run_id,scenario,App_Now(),115200); }
        else AppTrace_Stop();
        return;
    }
#endif
    char error[64];snprintf(error,64,"ERR,%lu,BAD_ARG",(unsigned long)req);''')
f.write_text(s)
# Builder keeps V1 sources, baud and protocol; only adds instrumentation/tool metadata.
s=(W/'projects/v2/firmware/build.py').read_text()
s=s.replace("ap.add_argument('--variant', choices=['Q','QW','QB','QWB'], default='QWB')","ap.add_argument('--variant', choices=['V1'], default='V1')")
s=s.replace("ROOT/'firmware/build/v2'/args.variant/args.config/args.trace","ROOT/'firmware/build/v1'/args.config/args.trace").replace('provenance/v2-source.json','provenance/v1-source.json')
s=s.replace("f'-DAPP_PROFILE={dict(Q=1,QW=2,QB=3,QWB=4)[args.variant]}',",'')
s=s.replace("'design_version':2,'variant':args.variant,'protocol':'PROTO3','baud':460800 if args.variant in {'QB','QWB'} else 115200","'design_version':1,'variant':'V1','protocol':'PROTO2','baud':115200")
(W/'projects/v1/firmware/build.py').write_text(s)
print('V1 trace integration complete')
