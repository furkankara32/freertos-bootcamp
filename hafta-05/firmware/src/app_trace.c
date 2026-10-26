/* RAM single-shot capture. USART2 only exports AFTER capture has stopped. */
#include "FreeRTOS.h"
#include "task.h"
#include "board.h"
#include "app_trace.h"
#include "SEGGER_SYSVIEW.h"
#include "SEGGER_RTT.h"
extern const SEGGER_SYSVIEW_OS_API SYSVIEW_X_OS_TraceAPI;
static void descriptions(void);
static SEGGER_SYSVIEW_MODULE module = {"M=Week5_LED,T=W5", TR_COUNT, 0, descriptions, 0};
static void *named_queue;
static volatile uint32_t ticks_left;
volatile const uint8_t *app_trace_data;
volatile uint32_t app_trace_bytes, app_trace_dropped, app_trace_complete, app_trace_reason;
static const char *const labels[] = {
 "0 RUN run=%u scenario=%u variant=%u", "1 FRAME run=%u id=%u type=%u",
 "2 EVENT run=%u id=%u detail=%u", "3 EXECUTE run=%u id=%u period=%u",
 "4 LED run=%u color=%u late_us=%u", "5 WORK_BEGIN run=%u id=%u units=%u",
 "6 WORK_END run=%u id=%u elapsed_us=%u", "7 TX_BEGIN run=%u id=%u detail=%u",
 "8 TX_END run=%u id=%u detail=%u", "9 DONE run=%u id=%u detail=%u"
};
static void descriptions(void) {
    for (unsigned i=0;i<TR_COUNT;i++) SEGGER_SYSVIEW_RecordModuleDescription(&module, labels[i]);
}
static void system_description(void) {
    SEGGER_SYSVIEW_SendSysDesc("N=Bootcamp Week5 UART LED Lab (FreeRTOS 11.1.0),D=STM32F407VG,O=FreeRTOS");
    SEGGER_SYSVIEW_SendSysDesc("I#15=SysTick,I#54=USART2,I#55=USART3");
    if (named_queue) SEGGER_SYSVIEW_NameResource((U32)named_queue, "CommandQueue");
}
void SEGGER_SYSVIEW_Conf(void) {
    SEGGER_SYSVIEW_Init(SystemCoreClock, SystemCoreClock, &SYSVIEW_X_OS_TraceAPI, system_description);
    SEGGER_SYSVIEW_SetRAMBase(0x20000000U);
}
void AppTrace_Init(void) { SEGGER_SYSVIEW_Conf(); SEGGER_SYSVIEW_RegisterModule(&module); }
void AppTrace_NameQueue(void *queue) { named_queue=queue; }
void AppTrace_Event(unsigned e,uint32_t run,uint32_t id,uint32_t detail) {
    SEGGER_SYSVIEW_RecordU32x3(module.EventOffset+e,run,id,detail);
}
void AppTrace_Start(uint32_t ms) {
    taskENTER_CRITICAL();
    SEGGER_SYSVIEW_Stop();
    _SEGGER_RTT.aUp[1].WrOff=0; _SEGGER_RTT.aUp[1].RdOff=0;
    SEGGER_SYSVIEW_GetMainContext()->DropCount=0;
    app_trace_complete=0; app_trace_bytes=0; app_trace_dropped=0; app_trace_reason=0;
    SEGGER_SYSVIEW_Start();
    app_trace_data=(const uint8_t *)_SEGGER_RTT.aUp[1].pBuffer;
    system_description(); SEGGER_SYSVIEW_SendTaskList();
    SEGGER_SYSVIEW_SendModule(0); descriptions();
    SEGGER_SYSVIEW_OnTaskStartExec((U32)xTaskGetCurrentTaskHandle());
    ticks_left=pdMS_TO_TICKS(ms);
    taskEXIT_CRITICAL();
}
void AppTrace_Stop(void) {
    UBaseType_t mask=portSET_INTERRUPT_MASK_FROM_ISR();
    SEGGER_SYSVIEW_Stop(); ticks_left=0;
    app_trace_bytes=_SEGGER_RTT.aUp[1].WrOff;
    app_trace_dropped=SEGGER_SYSVIEW_GetMainContext()->DropCount;
    app_trace_complete=1;
    portCLEAR_INTERRUPT_MASK_FROM_ISR(mask);
}
void AppTrace_Tick(void) {
    /* Called after the port's balanced SysTick trace exits. All tracing IRQs
       have priority >= 5; protect snapshot bookkeeping from priority-6 IRQs. */
    UBaseType_t mask=portSET_INTERRUPT_MASK_FROM_ISR();
    if(ticks_left) {
        if (_SEGGER_RTT.aUp[1].WrOff > SEGGER_SYSVIEW_RTT_BUFFER_SIZE-2048U) {
            app_trace_reason=2; AppTrace_Stop();
        } else if (--ticks_left==0) { app_trace_reason=1; AppTrace_Stop(); }
    }
    portCLEAR_INTERRUPT_MASK_FROM_ISR(mask);
}
const uint8_t *AppTrace_Data(void) { return (const uint8_t *)_SEGGER_RTT.aUp[1].pBuffer; }
