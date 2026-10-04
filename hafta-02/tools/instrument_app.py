from pathlib import Path
import re
W=Path(__file__).resolve().parents[1];P=W/'projects/v2/firmware/Homework_001'
def edit(p,a,b,count=1):
 s=p.read_text();assert s.count(a)==count,(p,a,s.count(a));p.write_text(s.replace(a,b))
f=P/'Src/app.c'
edit(f,'#include "queue.h"','#include "queue.h"\n#include "app_trace.h"')
edit(f,'static volatile uint16_t active_index = NO_RECORD;','static volatile uint16_t active_index = NO_RECORD;\n#if APP_TRACE\nstatic uint32_t trace_tel_id, trace_tel_run;\n#endif')
edit(f,'    if (!button_q || !tx_q || !btn_tx_q || !tel_tx_q || !control_q) Error_Handler();','''    if (!button_q || !tx_q || !btn_tx_q || !tel_tx_q || !control_q) Error_Handler();
    AppTrace_NameQueue(button_q,"button_q");
    AppTrace_NameQueue(btn_tx_q,"btn_tx_q");
    AppTrace_NameQueue(tel_tx_q,"tel_tx_q");
    AppTrace_NameQueue(tx_q,"control_tx_q");
    AppTrace_NameQueue(control_q,"command_q");''')
edit(f,'    records[index].status=PENDING;','    records[index].status=PENDING;\n    AppTrace_Event(TR_BTN_ACCEPT,run_id,id,now,0);')
edit(f,'records[index].status=BUTTON_DROP; ++counters[BQ_DROP];','records[index].status=BUTTON_DROP; ++counters[BQ_DROP];\n            AppTrace_Event(TR_BTN_DROP,run_id,id,now,BUTTON_DROP);')
edit(f,'        if(!pending) continue;','        if(!pending) continue;\n        AppTrace_Event(TR_BTN_TASK,run_id,records[i].id,t1,0);')
edit(f,'if(xQueueSend(btn_tx_q,&m,0)!=pdPASS) { records[i].status=TX_DROP; ++counters[BTX_DROP]; }','''AppTrace_Event(TR_BTN_READY,run_id,records[i].id,records[i].t[2],0);
        if(xQueueSend(btn_tx_q,&m,0)!=pdPASS) { records[i].status=TX_DROP; ++counters[BTX_DROP]; AppTrace_Event(TR_BTN_DROP,run_id,records[i].id,App_Now(),TX_DROP); }''')
edit(f,'if(n>counters[BTN_HWM])counters[BTN_HWM]=n;','if(n>counters[BTN_HWM])counters[BTN_HWM]=n;\n            AppTrace_Event(TR_BTN_ENQUEUE,run_id,records[i].id,App_Now(),n);')
edit(f,'records[i].t[4]=now;records[i].mask|=16;records[i].status=OK;','records[i].t[4]=now;records[i].mask|=16;records[i].status=OK;\n            AppTrace_Event(TR_BTN_TX_TC,run_id,records[i].id,now,0);')
edit(f,'    taskEXIT_CRITICAL_FROM_ISR(mask);','''#if APP_TRACE
    if(i==NO_RECORD && trace_tel_id) AppTrace_Event(TR_TEL_TX_TC,trace_tel_run,trace_tel_id,now,0);
#endif
    taskEXIT_CRITICAL_FROM_ISR(mask);''')
edit(f,'    HAL_StatusTypeDef rc=HAL_UART_Transmit_DMA(&huart2,dma_bytes,64);','''    if(index!=NO_RECORD) AppTrace_Event(TR_BTN_TX_START,run_id,records[index].id,records[index].t[3],0);
#if APP_TRACE
    else if(trace_tel_id) AppTrace_Event(TR_TEL_TX_START,trace_tel_run,trace_tel_id,App_Now(),0);
#endif
    HAL_StatusTypeDef rc=HAL_UART_Transmit_DMA(&huart2,dma_bytes,64);
    if(rc!=HAL_OK) AppTrace_Event(TR_TX_ERROR,run_id,index!=NO_RECORD?records[index].id:0,App_Now(),rc);''')
edit(f,'        int success=transmit(m.bytes,m.index,m.kind==TEL||m.kind==BTN);','''#if APP_TRACE
        trace_tel_id=trace_tel_run=0;
        /* Extract existing immutable wire IDs; do not change the queue element. */
        if(m.kind==TEL) {
            unsigned long tr,ts,ti;
            if(sscanf((const char *)m.bytes,"TEL,%lu,S%lu,%lu",&tr,&ts,&ti)==3) {trace_tel_run=(uint32_t)tr;trace_tel_id=(uint32_t)ti;}
        }
#endif
        int success=transmit(m.bytes,m.index,m.kind==TEL||m.kind==BTN);''')
# Avoid expensive sscanf/newlib: replace parser above with simple bounded digit scan.
s=f.read_text();s=s.replace('''            unsigned long tr,ts,ti;
            if(sscanf((const char *)m.bytes,"TEL,%lu,S%lu,%lu",&tr,&ts,&ti)==3) {trace_tel_run=(uint32_t)tr;trace_tel_id=(uint32_t)ti;}''','''            unsigned field=0;uint32_t value=0;
            for(unsigned j=4;j<FRAME;j++) {
                uint8_t c=m.bytes[j];
                if(c>='0' && c<='9')value=value*10U+(c-'0');
                else if(c==',') {if(field==0)trace_tel_run=value;if(field==2){trace_tel_id=value;break;}field++;value=0;}
            }''');f.write_text(s)
edit(f,'uint32_t start=App_Now();workload(n,&x,offset);uint32_t dt=App_Now()-start;','''AppTrace_Event(TR_WORK_BEGIN,run_id,sequence+1,App_Now(),k);
        uint32_t start=App_Now();workload(n,&x,offset);uint32_t dt=App_Now()-start;
        AppTrace_Event(TR_WORK_END,run_id,sequence+1,App_Now(),k);''')
edit(f,'if(xQueueSend(tel_tx_q,&m,0)!=pdPASS){if(state==RUNNING)++counters[TEL_DROP];}','if(xQueueSend(tel_tx_q,&m,0)!=pdPASS){if(state==RUNNING)++counters[TEL_DROP];AppTrace_Event(TR_TEL_DROP,run_id,sequence,App_Now(),TX_DROP);}')
edit(f,'if(n>counters[TX_HWM])counters[TX_HWM]=n;}','if(n>counters[TX_HWM])counters[TX_HWM]=n;AppTrace_Event(TR_TEL_ENQUEUE,run_id,sequence,App_Now(),n);}')
edit(f,'scenario=selected;++run_id;have_snapshot=0;','scenario=selected;++run_id;AppTrace_Event(TR_RUN_CONFIG,run_id,scenario,App_Now(),APP_BAUD);have_snapshot=0;')
edit(f,'run_start=App_Now();accepting=1;state=RUNNING;','run_start=App_Now();accepting=1;state=RUNNING;AppTrace_Event(TR_RUN_ARMED,run_id,scenario,run_start,0);')
edit(f,'static void finish(uint32_t req,int cancelled)\n{','static void finish(uint32_t req,int cancelled)\n{\n    AppTrace_Event(TR_RUN_STOP,run_id,scenario,App_Now(),cancelled);')
# Capture control is separate from ordinary experiment commands, task context only.
edit(f,'    if(hello) {','''#if APP_TRACE
    if(!strcmp(verb,"TRACE")) {
        uint32_t duration;
        if(!arg || !number(arg,&duration) || duration>2000U){reply("ERR,0,BAD_TRACE");return;}
        if(duration) {
            AppTrace_Start(duration);
            AppTrace_Event(TR_RUN_CONFIG,run_id,scenario,App_Now(),APP_BAUD);
        } else AppTrace_Stop();
        return; /* No extra UART traffic during the measured interval. */
    }
#endif
    if(hello) {''')
# TRACE must pass the verb validator; inspect exact validator below when running.
f=P/'Middlewares/Third_Party/FreeRTOS/Source/portable/GCC/ARM_CM4F/port.c'
edit(f,'#include "task.h"','#include "task.h"\n#include "app_trace.h"')
edit(f,'else { traceISR_EXIT(); }\n\tportENABLE_INTERRUPTS();','else { traceISR_EXIT(); }\n\tAppTrace_Tick();\n\tportENABLE_INTERRUPTS();')
print('Application trace events added; inspect TRACE command validation.')
