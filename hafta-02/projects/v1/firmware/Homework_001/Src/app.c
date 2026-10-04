/* FreeRTOS Bootcamp: all timestamps are TIM5 microseconds, never host time. */
#include "app.h"
#include "main.h"
#include "tim.h"
#include "usart.h"
#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"
#include "app_trace.h"
#include <stdio.h>
#include <stdarg.h>
#include <string.h>
#include <stdlib.h>
#include <limits.h>

#ifndef APP_GIT_SHA
#define APP_GIT_SHA "unknown"
#endif
#ifndef APP_BUILD_CONFIG
#define APP_BUILD_CONFIG "CubeIDE"
#endif
#ifndef APP_OPT_LEVEL
#define APP_OPT_LEVEL "unknown"
#endif
#define FRAME 64U
#define CAPACITY 128U
#define RECORDS 136U
#define NO_RECORD 0xffffU
#define BUDGET 1000000U
#define CTRL_RX 1U
#define CTRL_DONE 2U
#define AUTO_STOP 4U
#define TX_DONE 1U
#define TX_FAILED 2U
#define TX_STOP 4U

enum Status { PENDING, OK, BUTTON_DROP, TX_DROP, TX_ERROR, TIMEOUT, OVERFLOW };
static const char *const statuses[] = {"pending", "ok", "button_q_drop", "tx_drop", "tx_error", "timeout", "record_overflow"};
enum State { IDLE, CONFIGURED, WARMUP, RUNNING, DRAINING, COMPLETE, FAULT };
enum Kind { TEL, BTN, CONTROL, BARRIER, DUMP };
enum Counter { ACCEPTED, DEBOUNCE, BQ_DROP, BTX_DROP, TEL_DROP, UART_ERROR, TX_TIMEOUT,
    DRAIN_TIMEOUT, RECORD_OVERFLOW, UNRECORDED, TX_HWM, BQ_HWM, TEL_GENERATED,
    TEL_ENQUEUED, TEL_COMPLETED, RX_ERROR, CONTROL_DROP, FORMAT_ERROR, PERIOD_OVERRUN, COUNTERS };
static const char *const counter_names[] = {
    "accepted", "debounce_reject", "button_q_drop", "btn_tx_drop", "tel_q_drop",
    "uart_tx_error", "tx_timeout", "drain_timeout", "record_overflow", "unrecorded_events",
    "txq_hwm", "buttonq_hwm", "tel_generated", "tel_enqueued", "tel_completed",
    "rx_error", "control_drop", "format_error", "period_overrun"};
typedef struct { uint32_t id, t[5]; uint8_t mask, status; } Record;
typedef struct { uint16_t index; uint8_t barrier; } ButtonEvent;
typedef struct { uint8_t kind; uint16_t index; uint8_t bytes[FRAME]; } TxMsg;
typedef struct { char bytes[64]; } Command;
static Record records[RECORDS];
static uint32_t counters[COUNTERS], snapshot[COUNTERS];
static QueueHandle_t button_q, tx_q, control_q;
static TaskHandle_t control_task, uart_task;
static volatile enum State state = IDLE;
static volatile uint8_t accepting, stopping, tx_active;
static volatile uint16_t active_index = NO_RECORD;
#if APP_TRACE
static uint32_t trace_tel_id, trace_tel_run;
#endif
static uint32_t run_id, selected, scenario, record_count, last_press;
static uint8_t first_press = 1, have_snapshot, sync_failed;
static uint32_t run_start, run_stop, stop_start, sequence;
static uint32_t tel_first, tel_last, period_min, period_max, period_sum, period_n;
static uint32_t iterations, work_min, work_mean, work_max;
static volatile uint32_t work_sink;
static const uint32_t periods[] = {0,100,20,10,10,10};
static const uint32_t targets[] = {0,0,0,0,2000,5000};
static const char *result = "COMPLETE";
static uint8_t rx_byte;
static Command rx_line;
static uint32_t rx_length;
static uint8_t rx_discard;
static char deferred[4][64];
static unsigned deferred_count;
static uint32_t last_req;
static char last_command[64], last_ack[64];

uint32_t App_Now(void) { return TIM5->CNT; }
static TickType_t ticks_up(uint32_t us) { return (TickType_t)((us + 999U) / 1000U); }
static void count(enum Counter c) { taskENTER_CRITICAL(); ++counters[c]; taskEXIT_CRITICAL(); }
static void terminal(uint16_t i, enum Status status)
{
    taskENTER_CRITICAL();
    if (i < record_count && records[i].status == PENDING) records[i].status = status;
    taskEXIT_CRITICAL();
}
static int format(uint8_t *dst, const char *fmt, ...)
{
    char tmp[64]; va_list ap; va_start(ap, fmt);
    int n = vsnprintf(tmp, sizeof(tmp), fmt, ap); va_end(ap);
    if (n < 0 || n > 63) { count(FORMAT_ERROR); return 0; }
    memset(dst, ' ', 63); memcpy(dst, tmp, (size_t)n); dst[63] = '\n'; return 1;
}
static uint32_t remaining_stop(void)
{
    uint32_t age = App_Now() - stop_start;
    return age < BUDGET ? BUDGET - age : 0;
}
static int wait_control(uint32_t ms)
{
    TickType_t start = xTaskGetTickCount(), limit = pdMS_TO_TICKS(ms);
    for (;;) {
        uint32_t bits = 0; TickType_t elapsed = xTaskGetTickCount() - start;
        if (elapsed >= limit) return 0;
        xTaskNotifyWait(0, UINT32_MAX, &bits, limit - elapsed);
        if (bits & CTRL_DONE) return !sync_failed;
    }
}
static void clear_done(void) { (void)ulTaskNotifyValueClear(NULL, CTRL_DONE); sync_failed = 0; }
static int control_frame(const char *text)
{
    TxMsg m = {.kind=CONTROL, .index=NO_RECORD};
    if (!format(m.bytes, "%s", text)) return 0;
    clear_done();
    if (xQueueSend(tx_q, &m, pdMS_TO_TICKS(1000)) != pdPASS) return 0;
    return wait_control(1500);
}
static void reply(const char *text)
{
    if (state == RUNNING || state == WARMUP) {
        if (deferred_count < 4) snprintf(deferred[deferred_count++],64,"%s",text);
        else count(CONTROL_DROP);
    } else if (!control_frame(text)) { state = FAULT; accepting = 0; }
}
static void exp_state(const char *name)
{
    char text[64]; snprintf(text,64,"EXP,%lu,%s,S%lu",(unsigned long)run_id,name,(unsigned long)scenario);
    if (!control_frame(text)) state = FAULT;
}
static void reset_measurement(void)
{
    taskENTER_CRITICAL();
    memset(records,0,sizeof(records)); memset(counters,0,sizeof(counters));
    record_count=0; first_press=1; sequence=0;
    tel_first=tel_last=period_sum=period_n=period_max=0; period_min=UINT32_MAX;
    taskEXIT_CRITICAL();
}
void App_Init(void)
{
    if (HAL_TIM_Base_Start(&htim5) != HAL_OK) Error_Handler();
    button_q=xQueueCreate(8,sizeof(ButtonEvent)); tx_q=xQueueCreate(16,sizeof(TxMsg));
    control_q=xQueueCreate(4,sizeof(Command));
    if (!button_q || !tx_q || !control_q) Error_Handler();
    AppTrace_NameQueue(button_q,"button_q");
    AppTrace_NameQueue(tx_q,"shared_tx_q");
    AppTrace_NameQueue(control_q,"command_q");
}

/* Called at EXTI0 entry after the hardware pending flag is cleared. */
void App_ButtonIRQ(uint32_t now)
{
    if (!accepting) return;
    if (!first_press && (uint32_t)(now-last_press)<30000U) { ++counters[DEBOUNCE]; return; }
    first_press=0; last_press=now;
    uint32_t id=++counters[ACCEPTED];
    if (record_count>=RECORDS) { ++counters[UNRECORDED]; accepting=0; return; }
    uint16_t index=(uint16_t)record_count++;
    records[index].id=id; records[index].t[0]=now; records[index].mask=1;
    records[index].status=PENDING;
    AppTrace_Event(TR_BTN_ACCEPT,run_id,id,now,0);
    BaseType_t wake=pdFALSE;
    if (index>=CAPACITY) {
        records[index].status=OVERFLOW; ++counters[RECORD_OVERFLOW]; accepting=0;
        xTaskNotifyFromISR(control_task,AUTO_STOP,eSetBits,&wake);
    } else {
        ButtonEvent e={.index=index,.barrier=0};
        if (xQueueSendFromISR(button_q,&e,&wake)!=pdPASS) {
            records[index].status=BUTTON_DROP; ++counters[BQ_DROP]; AppTrace_Event(TR_BTN_DROP,run_id,id,now,BUTTON_DROP);
        } else {
            UBaseType_t n=uxQueueMessagesWaitingFromISR(button_q);
            if(n>counters[BQ_HWM]) counters[BQ_HWM]=n;
        }
    }
    portYIELD_FROM_ISR(wake);
}
void App_ButtonTask(void)
{
    for (;;) {
        ButtonEvent e;
        if(xQueueReceive(button_q,&e,portMAX_DELAY)!=pdPASS) continue;
        uint32_t t1=App_Now();
        if(e.barrier) {
            TxMsg m={.kind=BARRIER,.index=NO_RECORD};
            /* Even after expiry the marker must reach the TX owner; expired data
             * is discarded there. It alone declares the hardware quiescent. */
            if(xQueueSend(tx_q,&m,pdMS_TO_TICKS(1100))!=pdPASS) {
                sync_failed=1; xTaskNotify(control_task,CTRL_DONE,eSetBits);
            }
            continue;
        }
        uint16_t i=e.index;
        taskENTER_CRITICAL();
        int pending=records[i].status==PENDING;
        if(pending) { records[i].t[1]=t1; records[i].mask|=2; }
        taskEXIT_CRITICAL();
        if(!pending) continue;
        AppTrace_Event(TR_BTN_TASK,run_id,records[i].id,t1,0);
        if((uint32_t)(t1-records[i].t[0])>=BUDGET) {terminal(i,TIMEOUT);continue;}
        TxMsg m={.kind=BTN,.index=i};
        if(!format(m.bytes,"BTN,%lu,S%lu,%lu,PRESSED",(unsigned long)run_id,(unsigned long)scenario,(unsigned long)records[i].id)) {terminal(i,TX_ERROR);continue;}
        taskENTER_CRITICAL();
        if(records[i].status==PENDING) { records[i].t[2]=App_Now(); records[i].mask|=4; }
        else {taskEXIT_CRITICAL();continue;}
        AppTrace_Event(TR_BTN_READY,run_id,records[i].id,records[i].t[2],0);
        if(xQueueSend(tx_q,&m,0)!=pdPASS) { records[i].status=TX_DROP; ++counters[BTX_DROP]; AppTrace_Event(TR_BTN_DROP,run_id,records[i].id,App_Now(),TX_DROP); }
        else {UBaseType_t n=uxQueueMessagesWaiting(tx_q);if(n>counters[TX_HWM])counters[TX_HWM]=n;AppTrace_Event(TR_BTN_ENQUEUE,run_id,records[i].id,App_Now(),n);}
        taskEXIT_CRITICAL();
    }
}

void HAL_UART_TxCpltCallback(UART_HandleTypeDef *huart)
{
    uint32_t now=App_Now();
    if(huart!=&huart2 || !tx_active) return;
    UBaseType_t mask=taskENTER_CRITICAL_FROM_ISR();
    uint16_t i=active_index;
    if(i!=NO_RECORD && records[i].status==PENDING) {
        if((uint32_t)(now-records[i].t[0])<=BUDGET) {
            records[i].t[4]=now;records[i].mask|=16;records[i].status=OK;
            AppTrace_Event(TR_BTN_TX_TC,run_id,records[i].id,now,0);
        } else records[i].status=TIMEOUT;
    }
#if APP_TRACE
    if(i==NO_RECORD && trace_tel_id) AppTrace_Event(TR_TEL_TX_TC,trace_tel_run,trace_tel_id,now,0);
#endif
    taskEXIT_CRITICAL_FROM_ISR(mask);
    BaseType_t wake=pdFALSE; xTaskNotifyFromISR(uart_task,TX_DONE,eSetBits,&wake);portYIELD_FROM_ISR(wake);
}
void HAL_UART_ErrorCallback(UART_HandleTypeDef *huart)
{
    if(huart!=&huart2) return;
    BaseType_t wake=pdFALSE;
    if(tx_active && huart->hdmatx && huart->hdmatx->ErrorCode!=HAL_DMA_ERROR_NONE)
        xTaskNotifyFromISR(uart_task,TX_FAILED,eSetBits,&wake);
    else {
        ++counters[RX_ERROR]; rx_length=0;rx_discard=1;
        /* A DMA TX error must not be confused with RX ORE/FE/NE. */
        if(huart->RxState==HAL_UART_STATE_READY) (void)HAL_UART_Receive_IT(&huart2,&rx_byte,1);
    }
    portYIELD_FROM_ISR(wake);
}
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
    if(huart!=&huart2) return;
    BaseType_t wake=pdFALSE;
    if(rx_byte=='\n') {
        if(!rx_discard) {
            if(rx_length && rx_line.bytes[rx_length-1]=='\r') --rx_length;
            rx_line.bytes[rx_length]='\0';
            if(xQueueSendFromISR(control_q,&rx_line,&wake)!=pdPASS) ++counters[CONTROL_DROP];
            else xTaskNotifyFromISR(control_task,CTRL_RX,eSetBits,&wake);
        }
        rx_length=0;rx_discard=0;
    } else if(!rx_discard) {
        if(rx_length>=63 || rx_byte<32 || rx_byte>126) {
            if(rx_byte=='\r' && rx_length<63) rx_line.bytes[rx_length++]=(char)rx_byte;
            else {rx_discard=1;++counters[FORMAT_ERROR];}
        } else rx_line.bytes[rx_length++]=(char)rx_byte;
    }
    if(HAL_UART_Receive_IT(&huart2,&rx_byte,1)!=HAL_OK) ++counters[RX_ERROR];
    portYIELD_FROM_ISR(wake);
}

/* Only UartTxTask enters this function. The persistent buffer is DMA-accessible SRAM. */
static int transmit(const uint8_t bytes[64],uint16_t index,int measurement)
{
    static uint8_t dma_bytes[64];
    if(index!=NO_RECORD && records[index].status!=PENDING) return 0;
    if(measurement && stopping && !remaining_stop()) {if(index!=NO_RECORD)terminal(index,TIMEOUT);return 0;}
    memcpy(dma_bytes,bytes,64);
    uint32_t ignore; xTaskNotifyWait(0,UINT32_MAX,&ignore,0);
    uint32_t started=App_Now();
    if(index!=NO_RECORD && (uint32_t)(started-records[index].t[0])>=BUDGET) {terminal(index,TIMEOUT);return 0;}
    taskENTER_CRITICAL();
    if(index!=NO_RECORD && records[index].status!=PENDING) {taskEXIT_CRITICAL();return 0;}
    active_index=index;tx_active=1;
    if(index!=NO_RECORD) {records[index].t[3]=App_Now();records[index].mask|=8;}
    taskEXIT_CRITICAL();
    if(index!=NO_RECORD) AppTrace_Event(TR_BTN_TX_START,run_id,records[index].id,records[index].t[3],0);
#if APP_TRACE
    else if(trace_tel_id) AppTrace_Event(TR_TEL_TX_START,trace_tel_run,trace_tel_id,App_Now(),0);
#endif
    HAL_StatusTypeDef rc=HAL_UART_Transmit_DMA(&huart2,dma_bytes,64);
    if(rc!=HAL_OK) AppTrace_Event(TR_TX_ERROR,run_id,index!=NO_RECORD?records[index].id:0,App_Now(),rc);
    int success=0, timedout=0;
    if(rc==HAL_OK) {
        for(;;) {
            uint32_t now=App_Now(),base=index==NO_RECORD?started:records[index].t[0];
            uint32_t age=now-base, left=age<BUDGET?BUDGET-age:0;
            if(measurement && stopping && remaining_stop()<left)left=remaining_stop();
            uint32_t bits=0;
            xTaskNotifyWait(0,UINT32_MAX,&bits,ticks_up(left));
            if(bits&TX_DONE) {success=1;break;}
            if(bits&TX_FAILED) break;
            now=App_Now();
            if((uint32_t)(now-base)>=BUDGET || (measurement && stopping && !remaining_stop())) {timedout=1;break;}
        }
    }
    if(!success) {
        if(measurement)count(timedout?TX_TIMEOUT:UART_ERROR);
        if(index!=NO_RECORD)terminal(index,timedout?TIMEOUT:TX_ERROR);
        /* Stop hardware BEFORE publishing idle or reusing its buffer. UART TCIE
         * and DMA stream are disabled by the blocking HAL abort. RX stays live. */
        HAL_StatusTypeDef aborted=HAL_UART_AbortTransmit(&huart2);
        __HAL_UART_CLEAR_FLAG(&huart2,UART_FLAG_TC);
        HAL_NVIC_ClearPendingIRQ(DMA1_Stream6_IRQn);
        taskENTER_CRITICAL();tx_active=0;active_index=NO_RECORD;taskEXIT_CRITICAL();
        xTaskNotifyWait(0,UINT32_MAX,&ignore,0);
        if(aborted!=HAL_OK || (DMA1_Stream6->CR&DMA_SxCR_EN)) {state=FAULT;accepting=0;}
    } else {taskENTER_CRITICAL();tx_active=0;active_index=NO_RECORD;taskEXIT_CRITICAL();}
    return success;
}
static uint32_t crc_add(uint32_t crc,const uint8_t *p)
{
    for(unsigned n=0;n<64;n++) {crc^=p[n];for(unsigned b=0;b<8;b++)crc=(crc>>1)^((0U-(crc&1U))&0xedb88320U);}
    return crc;
}
static int dump_line(uint32_t *crc,const char *fmt,...)
{
    char text[64];uint8_t bytes[64];va_list ap;va_start(ap,fmt);int n=vsnprintf(text,64,fmt,ap);va_end(ap);
    if(n<0||n>63||!format(bytes,"%s",text))return 0;
    if(crc)*crc=crc_add(*crc,bytes);
    return transmit(bytes,NO_RECORD,0);
}
static int met(const char *key,uint32_t n)
{return dump_line(NULL,"MET,%lu,%s,%lu",(unsigned long)run_id,key,(unsigned long)n);}
static int met_text(const char *key,const char *value)
{return dump_line(NULL,"MET,%lu,%s,%s",(unsigned long)run_id,key,value);}
static int dump_records(void)
{
    uint32_t ok=0,late=0,crc=UINT32_MAX;
    for(unsigned i=0;i<record_count;i++)if(records[i].status==OK){++ok;if((uint32_t)(records[i].t[4]-records[i].t[0])>20000)++late;}
    if(!dump_line(NULL,"EXP,%lu,DUMPING,S%lu",(unsigned long)run_id,(unsigned long)scenario))return 0;
    if(!dump_line(NULL,"BEGIN,%lu,S%lu,%lu,%lu",(unsigned long)run_id,(unsigned long)scenario,(unsigned long)record_count,(unsigned long)snapshot[ACCEPTED]))return 0;
#define MET(k,v) do {if(!met(k,v))return 0;}while(0)
    MET("sysclk_hz",SystemCoreClock);MET("timer_hz",1000000);MET("tick_hz",configTICK_RATE_HZ);
    MET("baud",115200);MET("frame_bytes",64);MET("prio_tel",3);MET("prio_btn",2);MET("prio_tx",1);
    MET("buttonq_len",8);MET("txq_len",16);MET("record_capacity",CAPACITY);
    MET("telemetry_hz",periods[scenario]?1000/periods[scenario]:0);MET("period_ms",periods[scenario]);
    MET("work_target_us",targets[scenario]);MET("work_iters",iterations);
    MET("work_min_us",work_min);MET("work_mean_us",work_mean);MET("work_max_us",work_max);
    MET("run_start_us",run_start);MET("run_stop_us",run_stop);
    if(snapshot[TEL_GENERATED]) {MET("tel_first_us",tel_first);MET("tel_last_us",tel_last);}
    else if(!met_text("tel_first_us","-")||!met_text("tel_last_us","-"))return 0;
    if(period_n){MET("period_min_us",period_min);MET("period_max_us",period_max);}
    else if(!met_text("period_min_us","-")||!met_text("period_max_us","-"))return 0;
    MET("period_sum_us",period_sum);MET("period_n",period_n);
    MET("heap_min_bytes",xPortGetMinimumEverFreeHeapSize());
    MET("stack_tx_words",uxTaskGetStackHighWaterMark(NULL));
    MET("stack_tel_words",uxTaskGetStackHighWaterMark(control_task));
    char sha_a[21]={0},sha_b[21]={0};const char *sha=APP_GIT_SHA;
    if(strlen(sha)==40){memcpy(sha_a,sha,20);memcpy(sha_b,sha+20,20);}else{strcpy(sha_a,"unknown");strcpy(sha_b,"unknown");}
    if(!met_text("fw_sha_a",sha_a)||!met_text("fw_sha_b",sha_b)||!met_text("build_config",APP_BUILD_CONFIG)||!met_text("opt_level",APP_OPT_LEVEL)||!met_text("kernel_version",tskKERNEL_VERSION_NUMBER)||!met_text("result",result))return 0;
    for(unsigned n=0;n<COUNTERS;n++)if(!dump_line(NULL,"SUM,%lu,%s,%lu",(unsigned long)run_id,counter_names[n],(unsigned long)snapshot[n]))return 0;
    if(!dump_line(NULL,"SUM,%lu,ok,%lu",(unsigned long)run_id,(unsigned long)ok)||!dump_line(NULL,"SUM,%lu,late_completed,%lu",(unsigned long)run_id,(unsigned long)late))return 0;
    for(unsigned i=0;i<record_count;i++) {
        Record *r=&records[i];char ts[5][11];
        for(unsigned j=0;j<5;j++) {if(r->mask&(1U<<j))snprintf(ts[j],11,"%lu",(unsigned long)r->t[j]);else strcpy(ts[j],"-");}
        if(!dump_line(&crc,"M1,%lu,%lu,%s,%s,%s",(unsigned long)run_id,(unsigned long)r->id,ts[0],ts[1],ts[2]))return 0;
        if(!dump_line(&crc,"M2,%lu,%lu,%s,%s,%s",(unsigned long)run_id,(unsigned long)r->id,ts[3],ts[4],statuses[r->status]))return 0;
    }
    if(!dump_line(NULL,"END,%lu,%lu,%08lX",(unsigned long)run_id,(unsigned long)record_count,(unsigned long)(crc^UINT32_MAX)))return 0;
    return dump_line(NULL,"EXP,%lu,%s,S%lu",(unsigned long)run_id,strcmp(result,"COMPLETE")==0?"DONE":result,(unsigned long)scenario);
}
void App_UartTask(void)
{
    uart_task=xTaskGetCurrentTaskHandle();
    for(;;) {
        TxMsg m;if(xQueueReceive(tx_q,&m,portMAX_DELAY)!=pdPASS)continue;
        if(m.kind==BARRIER) {xTaskNotify(control_task,CTRL_DONE,eSetBits);continue;}
        if(m.kind==DUMP) {sync_failed=!dump_records();xTaskNotify(control_task,CTRL_DONE,eSetBits);continue;}
#if APP_TRACE
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
        int success=transmit(m.bytes,m.index,m.kind==TEL||m.kind==BTN);
        if(m.kind==TEL&&success&&state!=WARMUP)count(TEL_COMPLETED);
        if(m.kind==CONTROL){sync_failed=!success;xTaskNotify(control_task,CTRL_DONE,eSetBits);}
    }
}

__attribute__((noinline)) static void workload(uint32_t n)
{
    uint32_t x=work_sink+0x9e3779b9U;
    for(uint32_t i=0;i<n;i++){x^=x<<13;x^=x>>17;x^=x<<5;x+=i;}
    work_sink=x;
}
static void calibrate(uint32_t target)
{
    iterations=work_min=work_mean=work_max=0;if(!target)return;
    iterations=1000;
    for(unsigned k=0;k<4;k++) {
        uint32_t start=App_Now();workload(iterations);uint32_t dt=App_Now()-start;if(!dt)dt=1;
        uint64_t next=(uint64_t)iterations*target/dt;
        iterations=(uint32_t)(next>10000000?10000000:next);if(!iterations)iterations=1;
    }
    uint64_t total=0;work_min=UINT32_MAX;
    for(unsigned k=0;k<100;k++){uint32_t start=App_Now();workload(iterations);uint32_t dt=App_Now()-start;total+=dt;if(dt<work_min)work_min=dt;if(dt>work_max)work_max=dt;}
    work_mean=(uint32_t)((total+50)/100);
}
static void telemetry(void)
{
    uint32_t now=App_Now();
    if(state==RUNNING) {
        if(counters[TEL_GENERATED]){uint32_t d=now-tel_last;period_sum+=d;++period_n;if(d<period_min)period_min=d;if(d>period_max)period_max=d;}
        else tel_first=now;
        tel_last=now;count(TEL_GENERATED);
    }
    AppTrace_Event(TR_WORK_BEGIN,run_id,sequence+1,App_Now(),0);
    workload(iterations);
    AppTrace_Event(TR_WORK_END,run_id,sequence+1,App_Now(),0);
    TxMsg m={.kind=TEL,.index=NO_RECORD};
    if(!format(m.bytes,"TEL,%lu,S%lu,%lu,%lu",(unsigned long)run_id,(unsigned long)scenario,(unsigned long)++sequence,(unsigned long)work_sink))return;
    taskENTER_CRITICAL();
    if(xQueueSend(tx_q,&m,0)!=pdPASS){if(state==RUNNING)++counters[TEL_DROP];AppTrace_Event(TR_TEL_DROP,run_id,sequence,App_Now(),TX_DROP);}
    else if(state==RUNNING){++counters[TEL_ENQUEUED];UBaseType_t n=uxQueueMessagesWaiting(tx_q);if(n>counters[TX_HWM])counters[TX_HWM]=n;AppTrace_Event(TR_TEL_ENQUEUE,run_id,sequence,App_Now(),n);}
    taskEXIT_CRITICAL();
}
static int drain(void)
{
    taskENTER_CRITICAL();accepting=0;run_stop=App_Now();stop_start=run_stop;stopping=1;taskEXIT_CRITICAL();
    state=DRAINING;clear_done();
    if(uart_task)xTaskNotify(uart_task,TX_STOP,eSetBits);
    ButtonEvent barrier={.index=NO_RECORD,.barrier=1};
    if(xQueueSend(button_q,&barrier,pdMS_TO_TICKS(1000))!=pdPASS || !wait_control(1500)) {
        count(DRAIN_TIMEOUT);result="INCOMPLETE";state=FAULT;return 0;
    }
    if(!remaining_stop()){count(DRAIN_TIMEOUT);result="INCOMPLETE";}
    for(unsigned i=0;i<record_count;i++)if(records[i].status==PENDING){terminal(i,TIMEOUT);result="INCOMPLETE";}
    stopping=0;return 1;
}
static int start_dump(void)
{
    TxMsg m={.kind=DUMP,.index=NO_RECORD};clear_done();
    if(xQueueSend(tx_q,&m,pdMS_TO_TICKS(1000))!=pdPASS)return 0;
    return wait_control(15000);
}
static void finish(uint32_t req,int cancelled)
{
    AppTrace_Event(TR_RUN_STOP,run_id,scenario,App_Now(),cancelled);
    if(cancelled)result="CANCELLED";
    if(!drain())return;
    if(counters[RECORD_OVERFLOW]||counters[UNRECORDED])result="INCOMPLETE";
    memcpy(snapshot,counters,sizeof(snapshot));have_snapshot=1;state=COMPLETE;
    if(req){char ack[64];snprintf(ack,64,"ACK,%lu,STOP,%lu",(unsigned long)req,(unsigned long)run_id);strcpy(last_ack,ack);reply(ack);}
    for(unsigned i=0;i<deferred_count;i++) {reply(deferred[i]);}
    deferred_count=0;
    if(!start_dump())state=FAULT;
}
static int number(const char *p,uint32_t *n)
{
    if(!p||!*p)return 0;
    uint32_t value=0;
    for(;*p;p++){if(*p<'0'||*p>'9'||value>6553||(value==6553&&*p>'5'))return 0;value=value*10+(uint32_t)(*p-'0');}
    *n=value;return 1;
}
static void command(Command *cmd)
{
    char original[64];strcpy(original,cmd->bytes);
    char *comma=strchr(cmd->bytes,',');uint32_t req=0;
    if(!comma){reply("ERR,0,BAD_CMD");return;}*comma++=0;
    char *arg=strchr(comma,',');if(arg)*arg++=0;
    if(!number(comma,&req)||(!req&&strcmp(cmd->bytes,"HELLO"))){reply("ERR,0,BAD_ARG");return;}
#if APP_TRACE
    if(!strcmp(cmd->bytes,"TRACE")) {
        uint32_t duration;
        if(!arg || !number(arg,&duration) || duration>2000U){reply("ERR,0,BAD_TRACE");return;}
        if(duration) { AppTrace_Start(duration);AppTrace_Event(TR_RUN_CONFIG,run_id,scenario,App_Now(),115200); }
        else AppTrace_Stop();
        return;
    }
#endif
    char error[64];snprintf(error,64,"ERR,%lu,BAD_ARG",(unsigned long)req);
    if(req&&req==last_req){if(strcmp(original,last_command))reply(error);else reply(last_ack);return;}
    int cfg=!strcmp(cmd->bytes,"CFG"), hello=!strcmp(cmd->bytes,"HELLO"), start=!strcmp(cmd->bytes,"START"), stop=!strcmp(cmd->bytes,"STOP"), dump=!strcmp(cmd->bytes,"DUMP");
    if(!cfg&&!hello&&!start&&!stop&&!dump){snprintf(error,64,"ERR,%lu,BAD_CMD",(unsigned long)req);reply(error);return;}
    if((cfg&&(!arg||strlen(arg)!=2||arg[0]!='S'||arg[1]<'0'||arg[1]>'5'))||(!cfg&&arg)){reply(error);return;}
    int calm=state==IDLE||state==CONFIGURED||state==COMPLETE;
    if((cfg&&!calm)||(start&&state!=CONFIGURED)||(stop&&state!=RUNNING&&state!=WARMUP)||(dump&&(!have_snapshot||!calm))){snprintf(error,64,"ERR,%lu,BAD_STATE",(unsigned long)req);reply(error);return;}
    const char *verb=cfg?"CFG":hello?"HELLO":start?"START":stop?"STOP":"DUMP";
    char ack[64];snprintf(ack,64,"ACK,%lu,%s,%lu",(unsigned long)req,verb,(unsigned long)(start?run_id+1:run_id));
    if(req){last_req=req;strcpy(last_command,original);strcpy(last_ack,ack);}
    if(hello) {
        reply("SYS,RTOSLAT,FW03,PROTO2");reply(ack);
        const char *name=state==RUNNING?"ARMED":state==WARMUP?"WARMUP":state==CONFIGURED?"CONFIGURED":state==COMPLETE?"DONE":"IDLE";
        char text[64];snprintf(text,64,"EXP,%lu,%s,S%lu",(unsigned long)run_id,name,(unsigned long)(state==CONFIGURED?selected:scenario));reply(text);return;
    }
    if(cfg){selected=(uint32_t)(arg[1]-'0');state=CONFIGURED;reply(ack);char text[64];snprintf(text,64,"EXP,%lu,CONFIGURED,S%lu",(unsigned long)run_id,(unsigned long)selected);reply(text);return;}
    if(start){
        if(run_id==UINT32_MAX){reply("ERR,0,INTERNAL");return;}
        scenario=selected;++run_id;have_snapshot=0;result="COMPLETE";reset_measurement();run_start=run_stop=0;
        reply(ack);if(state==FAULT)return;
        exp_state("WARMUP");if(state==FAULT)return;
        calibrate(targets[scenario]);state=WARMUP;return;
    }
    if(stop){finish(req,state==WARMUP);return;}
    if(dump){reply(ack);if(!start_dump())state=FAULT;return;}
}
void App_TelemetryTask(void)
{
    control_task=xTaskGetCurrentTaskHandle();
    if(HAL_UART_Receive_IT(&huart2,&rx_byte,1)!=HAL_OK)Error_Handler();
    __HAL_GPIO_EXTI_CLEAR_IT(GPIO_PIN_0);HAL_NVIC_ClearPendingIRQ(EXTI0_IRQn);
    HAL_NVIC_SetPriority(EXTI0_IRQn,5,0);HAL_NVIC_EnableIRQ(EXTI0_IRQn);
    TickType_t last=xTaskGetTickCount();uint32_t warm_start=0;enum State previous=IDLE;
    for(;;) {
        Command cmd;while(xQueueReceive(control_q,&cmd,0)==pdPASS)command(&cmd);
        if(state==WARMUP&&previous!=WARMUP){warm_start=App_Now();last=xTaskGetTickCount();}
        if(state==WARMUP&&(uint32_t)(App_Now()-warm_start)>=5000000U){
            if(drain()){
                reset_measurement();state=CONFIGURED;exp_state("ARMED");
                if(state!=FAULT){taskENTER_CRITICAL();run_start=App_Now();accepting=1;state=RUNNING;taskEXIT_CRITICAL();last=xTaskGetTickCount();}
            }
        }
        if(state==RUNNING){
            uint32_t now=App_Now();
            taskENTER_CRITICAL();
            for(unsigned i=0;i<record_count;i++)if(records[i].status==PENDING && i!=active_index && (uint32_t)(now-records[i].t[0])>=BUDGET)records[i].status=TIMEOUT;
            taskEXIT_CRITICAL();
            if(!accepting||(uint32_t)(now-run_start)>=600000000U)finish(0,0);
        }
        previous=state;
        if((state==RUNNING||state==WARMUP)&&periods[scenario]){
            telemetry();TickType_t period=pdMS_TO_TICKS(periods[scenario]);
            if((TickType_t)(xTaskGetTickCount()-last)>=period&&state==RUNNING)count(PERIOD_OVERRUN);
            vTaskDelayUntil(&last,period);
        }else{
            uint32_t bits;TickType_t wait=portMAX_DELAY;
            if(state==WARMUP)wait=pdMS_TO_TICKS(10);
            if(state==RUNNING){
                uint32_t now=App_Now(),remaining=600000000U-(uint32_t)(now-run_start);
                for(unsigned i=0;i<record_count;i++)if(records[i].status==PENDING){uint32_t age=now-records[i].t[0];uint32_t left=age<BUDGET?BUDGET-age:1;if(left<remaining)remaining=left;}
                wait=ticks_up(remaining);
            }
            xTaskNotifyWait(0,UINT32_MAX,&bits,wait);
        }
    }
}
void vApplicationStackOverflowHook(TaskHandle_t task,char *name){(void)task;(void)name;taskDISABLE_INTERRUPTS();for(;;){}}
void vApplicationMallocFailedHook(void){taskDISABLE_INTERRUPTS();for(;;){}}
