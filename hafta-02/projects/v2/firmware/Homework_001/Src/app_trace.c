/* Week 2 instrumentation only. No task, queue policy or workload changes. */
#include "FreeRTOS.h"
#include "app_trace.h"
#if APP_TRACE
#include "task.h"
#include "stm32f4xx.h"
#include "SEGGER_SYSVIEW.h"
#include "SEGGER_RTT.h"
#include "app_config.h"
extern const SEGGER_SYSVIEW_OS_API SYSVIEW_X_OS_TraceAPI;
static void send_description(void);
static SEGGER_SYSVIEW_MODULE module = {"M=Bootcamp_V2,T=BC",TR_EVENT_COUNT,0,send_description,0};
static const char *const descriptions[] = {
 "0 RUN_CONFIG run=%u scenario=%u tim5_us=%u baud=%u",
 "1 RUN_ARMED run=%u scenario=%u tim5_us=%u detail=%u",
 "2 RUN_STOP run=%u scenario=%u tim5_us=%u detail=%u",
 "3 BTN_ACCEPT run=%u id=%u tim5_us=%u detail=%u",
 "4 BTN_TASK run=%u id=%u tim5_us=%u detail=%u",
 "5 BTN_READY run=%u id=%u tim5_us=%u detail=%u",
 "6 BTN_ENQUEUE run=%u id=%u tim5_us=%u depth=%u",
 "7 BTN_DROP run=%u id=%u tim5_us=%u reason=%u",
 "8 BTN_TX_START run=%u id=%u tim5_us=%u detail=%u",
 "9 BTN_TX_TC run=%u id=%u tim5_us=%u detail=%u",
 "10 TEL_ENQUEUE run=%u id=%u tim5_us=%u depth=%u",
 "11 TEL_DROP run=%u id=%u tim5_us=%u reason=%u",
 "12 TEL_TX_START run=%u id=%u tim5_us=%u detail=%u",
 "13 TEL_TX_TC run=%u id=%u tim5_us=%u detail=%u",
 "14 WORK_BEGIN run=%u id=%u tim5_us=%u slice=%u",
 "15 WORK_END run=%u id=%u tim5_us=%u slice=%u",
 "16 TX_ERROR run=%u id=%u tim5_us=%u hal_status=%u"
};
static volatile uint32_t ticks_left;
volatile uint32_t app_trace_capture_complete;
volatile uint32_t app_trace_bytes;
volatile uint32_t app_trace_dropped;
static unsigned initialized;
static struct { void *handle; const char *name; } queues[5];
static unsigned queue_count;
static void send_description(void) {
    for(unsigned i=0;i<TR_EVENT_COUNT;i++) SEGGER_SYSVIEW_RecordModuleDescription(&module,descriptions[i]);
}
static void system_description(void) {
    SEGGER_SYSVIEW_SendSysDesc("N=Bootcamp V2 " APP_VARIANT ",D=STM32F407VG,O=FreeRTOS");
    SEGGER_SYSVIEW_SendSysDesc("I#15=SysTick,I#22=EXTI0,I#32=DMA1_Stream5,I#33=DMA1_Stream6,I#45=TIM3,I#54=USART2");
    for(unsigned i=0;i<queue_count;i++) SEGGER_SYSVIEW_NameResource((U32)queues[i].handle,queues[i].name);
}
void SEGGER_SYSVIEW_Conf(void) {
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CYCCNT=0; DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
    SEGGER_SYSVIEW_Init(SystemCoreClock,SystemCoreClock,&SYSVIEW_X_OS_TraceAPI,system_description);
    SEGGER_SYSVIEW_SetRAMBase(0x20000000U);
}
void AppTrace_Init(void) {
    SEGGER_SYSVIEW_Conf();
    SEGGER_SYSVIEW_RegisterModule(&module);
    initialized=1;
}
void AppTrace_NameQueue(void *q,const char *name) {
    if(queue_count<5){queues[queue_count].handle=q;queues[queue_count++].name=name;}
}
void AppTrace_Event(unsigned event,uint32_t run,uint32_t id,uint32_t stamp,uint32_t detail) {
    if(initialized) SEGGER_SYSVIEW_RecordU32x4(module.EventOffset+event,run,id,stamp,detail);
}
void AppTrace_IsrEnter(void) { if(initialized) SEGGER_SYSVIEW_RecordEnterISR(); }
void AppTrace_IsrExit(void) {
    if(!initialized)return;
    if(SCB->ICSR & SCB_ICSR_PENDSVSET_Msk) SEGGER_SYSVIEW_RecordExitISRToScheduler();
    else SEGGER_SYSVIEW_RecordExitISR();
}
void AppTrace_Stop(void) {
    /* Caller may be SysTick. RTT's BASEPRI lock covers all recording ISRs. */
    SEGGER_SYSVIEW_Stop(); ticks_left=0;
    app_trace_dropped=SEGGER_SYSVIEW_GetMainContext()->DropCount;
    app_trace_bytes=_SEGGER_RTT.aUp[1].WrOff;
    app_trace_capture_complete=1;
}
void AppTrace_Start(uint32_t duration_ms) {
    /* Task context only, after all tasks exist. Short atomic initialization. */
    taskENTER_CRITICAL();
    SEGGER_SYSVIEW_Stop();
    _SEGGER_RTT.aUp[1].WrOff=0; _SEGGER_RTT.aUp[1].RdOff=0;
    app_trace_capture_complete=0;app_trace_bytes=0;app_trace_dropped=0;
    SEGGER_SYSVIEW_Start();
    SEGGER_SYSVIEW_SendModule(0);
    SEGGER_SYSVIEW_OnTaskStartExec((U32)xTaskGetCurrentTaskHandle());
    ticks_left=duration_ms;
    taskEXIT_CRITICAL();
}
void AppTrace_Tick(void) { if(ticks_left && --ticks_left==0)AppTrace_Stop(); }
#endif
